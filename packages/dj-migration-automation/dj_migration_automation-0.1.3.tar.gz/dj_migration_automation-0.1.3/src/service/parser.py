import json
import os
from collections import defaultdict
import datetime
from typing import Optional, List, Dict, Any

import pandas as pd
from peewee import IntegrityError, InternalError, DataError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import get_current_date_time, get_current_date, convert_quantity, get_current_time, \
    convert_time, get_current_time_zone, log_args_and_response
from src import constants
from src.cloud_storage import rx_file_blob_dir, create_blob
from src.dao.company_setting_dao import db_get_template_split_settings_dao
from src.dao.drug_dao import db_get_drug_data_by_ndc_parser_dao
from src.dao.ext_change_rx_couchdb_dao import update_customize_template_couch_db_status
from src.dao.ext_change_rx_dao import process_change_rx_insert_data, update_ext_change_rx_new_template_dao, \
    db_delete_template_rx_info, db_get_ext_change_rx_record, \
    db_get_template_admin_duration_by_template, db_get_packs_count_by_template, db_get_pack_slot_count_by_template, \
    db_get_pack_slot_hoa_split, db_get_old_template_by_new_template_dao
from src.dao.file_dao import db_get_file_by_filename_status_company_dao, db_file_header_get_or_create_dao, \
    db_file_header_update_task_id_dao, db_update_file_status_message_path_dao, db_get_file_info_not_ungenerated_dao, \
    db_file_header_create_record_dao
from src.dao.parser_dao import PARSING_ERRORS, db_doctor_master_update_or_create, \
    db_partial_update_create_facility_master_dao, db_patient_rx_update_or_create_dao, \
    db_update_modification_status_by_change_rx
from src.dao.patient_dao import db_patient_master_update_or_create_dao, \
    db_get_patient_name_patient_no_from_patient_id_dao
from src.dao.template_dao import db_get_template_file_id_by_pharmacy_fill_dao, db_temp_slot_info_create_record, \
    db_temp_slot_info_create_multi_record, template_is_modified_map, db_template_master_create_record, \
    db_get_template_master_info_by_template_id_dao, db_get_template_master_by_patient_and_file_dao
from src.exc_thread import ExcThread
from src.exceptions import FileParsingException, DuplicateFileException, DrugFetchFailedException, \
    RedisConnectionException, RealTimeDBException, AutoProcessTemplateException
from src.service.file_validation import file_validation
from src.service.generate_packs import generate, db_check_old_packs_status_for_new_template_process
from src.service.generate_templates import is_template_modified, save_template_details, get_template_data_v2, \
    get_pack_requirement_by_template_column_number

from src.redis_controller import update_pending_template_data_in_redisdb
from src.service.misc import real_time_db_timestamp_trigger, update_notifications_couch_db_status
from src.service.notifications import Notifications
from sync_drug_data.update_drug_data import get_missing_drug_data, get_missing_drug_images
from tasks.celery import celery_app

logger = settings.logger

FILE_HEADER = settings.FILE_HEADER

FILE_CONVERTERS = settings.FILE_CONVERTERS

CHANGE_RX_HEADER = settings.CHANGE_RX_HEADER
CHANGE_RX_CONVERTERS = settings.CHANGE_RX_CONVERTERS

# Get the corresponding file headers from the settings
file_converters = settings.FILE_CONVERTERS


class Parser(object):
    """ A ParseFile object will be created whenever a file is received for
    parsing. The object has several utilities defined to perform operations
    on the parsed file.
    """

    def __init__(self, user_id, filename, company_id, upload_manual=False, data=None,
                 from_dict=False, system_id=None, fill_manual=0, upload_file_to_gcs=True, **kwargs):
        """ Initialization of the Parser object

        Args:
            system_id (int): The system ID
            filename (str): The name of prescription file.
            user_id (int): The logged user id who requests for the parser.
            filename (str): The name of the file received for processing.
            data (str | None): Data in case file already parsed on client side
            from_dict (bool): Whether data frame should be created from dict, True when data is present
            system_id (int): system id to assign for template
            fill_manual (int): 0,1. 1 if uploaded for Manual Filling system_type, 0 otherwise

        """
        # initialize a empty data frame to hold the parsed file
        self.df = None
        self.user_id = user_id
        self.company_id = company_id
        # get the current date time in %Y-%m-%d HH:MM:SS format
        self.current_date_time = get_current_date_time()
        # get the current date in %Y-%m-%d format
        self.current_date = get_current_date()
        self.file = filename
        self.filename = os.path.join(settings.PENDING_FILE_PATH, str(self.company_id), filename)
        # create a default data dict with the initialization arguments. This default dict is used
        # to insert records in table and avoid repeated initialization of this arguments
        self.default_data_dict = {"created_by": self.user_id, "modified_by": self.user_id}
        # initialize the file_id
        self.file_id = None
        self.pending_file_status = settings.PENDING_FILE_STATUS
        self.pending_template_status = settings.PENDING_TEMPLATE_STATUS

        # get the fields required for inserting record into facility_master table from parsed file
        self.facility_master_fields = settings.FACILITY_MASTER_FIELDS

        # get the fields required for inserting record into patient_master table from parsed file
        self.patient_master_fields = settings.PATIENT_MASTER_FIELDS

        # get the fields required for inserting record into doctor_master table from parsed file
        self.doctor_master_fields = settings.DOCTOR_MASTER_FIELDS

        # get the fields required for inserting record into patient_rx table from parsed file
        self.patient_rx_fields = settings.PATIENT_RX_FIELDS

        # get the fields required for inserting record into drug_master table from parsed file
        self.drug_master_fields = settings.DRUG_MASTER_FIELDS

        # get the fields required for inserting record into template_master table from parsed file
        self.template_master_fields = settings.TEMPLATE_MASTER_FIELDS

        # get the fields required for inserting record into temp_slot_info table from parsed file
        self.temp_slot_info_fields = settings.TEMP_SLOT_INFO_FIELDS

        # whether the file is manual or not
        self.manual_upload = upload_manual

        self.facility_ids = {}
        self.doctor_ids = {}
        self.patient_rx_ids = {}
        self.drug_ids = {}
        self.patient_master_ids = {}
        self.rx_drug_records = {}
        self.template_master_ids = defaultdict(set)
        self.template_master_rx_dict = defaultdict(list)
        self.data = data
        self.from_dict = from_dict
        self.system_id = system_id  # None or int
        self.fill_manual = bool(int(fill_manual))
        self.old_pharmacy_fill_id: List[int] = []

        self.upload_file_to_gcs = upload_file_to_gcs
        self.autoprocess_template = 0
        self.token = ""
        self.ips_user_name = ""

    def create_data_frame(self, change_rx: Optional[bool] = False):
        # parse the file with the inputs file headers and file converters
        # from settings and store the result in the data frame

        if not change_rx:
            self.parse_file(FILE_HEADER, FILE_CONVERTERS)
        else:
            self.parse_file(CHANGE_RX_HEADER, CHANGE_RX_CONVERTERS)

    def handle_file_processing_error(self, err):
        """
        Handles the error whenever the file processing fails
        """
        self.update_file(settings.ERROR_FILE_STATUS, err, settings.ERROR_FILE_PATH)

    def parse_file(self, field_names, _file_converters, file_encoding='utf-8', _file_separator='\t'):
        """ Takes a file and creates a data frame from it form the input arguments

            Args:
                field_names (list): The names of the fields present in the file.
                _file_converters (dict): Contains type conversion parameters if to be applied to certain field in file
                file_encoding (optional argument) (str): The encoding of the input file. The default value is utf-8
                _file_separator (optional argument) (str): The field separator in file. The default is tab.

            Returns:
                pandas data frame: The matrix of the values in the file with file headers as names for each field.

            Examples:
                >>> Parser().parse_file([], [])
                [0, 1, 2, 3]

        """
        try:
            # Using pandas library in python to parse the contents of the
            # file.The file is delimited by fixed width format
            filename = self.filename

            if not self.from_dict:
                self.df = pd.read_csv(filename, sep=_file_separator, header=
                None, names=field_names, converters=file_converters, encoding=file_encoding)
                # Fill all the NA values with 0
                # self.df = self.df.fillna(0)  # removed to correctly record file validation errors
            else:
                if type(self.data) == str:
                    data = json.loads(self.data)
                else:
                    data = self.data
                self.df = pd.DataFrame.from_dict(data)
        except IOError as e:
            logger.error(e, exc_info=True)
            raise IOError("Could Not Parse the File.")
        except pd.parser.CParserError as e:
            logger.error(e, exc_info=True)
            raise IOError("Input File is not in proper format.")
        except UnicodeDecodeError as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])
        except Exception as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    def query_record(self, field_names):
        """ Takes a file and creates a data frame from it form the input arguments

            Args:
                field_names (list): The names of the fields to be queried from data frame.

            Returns:
                pandas data frame: The data frame consisting of filtered values with no duplicates

            Examples:
                >>> Parser().query_record([])
        """
        return self.df[field_names].drop_duplicates()

    def validate_fill_id_count(self):
        """ Returns True if every patient has only one pharmacy_fill_id, False otherwise """

        required_fields = ['patient_no', 'pharmacy_fill_id']
        # drop duplicate values for combination of fields
        # group by patient_no to get count of pharmacy_fill_id
        # then convert to dict
        fill_id_count = self.df[required_fields].drop_duplicates() \
            .groupby('patient_no') \
            .apply(lambda x: len(x['pharmacy_fill_id'])) \
            .to_dict()
        invalid_patient_set = {patient_no for patient_no, fill_id_count in fill_id_count.items() if fill_id_count != 1}
        if invalid_patient_set:
            logger.error('Multiple pharmacy_fill_id found for patient_no(s): {}'.format(invalid_patient_set))
            return False

        return True

    def iterate_over_data_frame(self, fields):
        """ Receives a data frame and returns a generator object over the data frame."""
        # Query the unique facility data from data frame
        data = self.query_record(fields)
        return data.iterrows()

    def process_data(self, fields, generated_ids_dict, generated_ids_key, func_create_record):
        """ Receives the data frame iterator object to iterate over. Creates the iterated record
        in the table name provided as argument. Stores the id of the created record in the dictionary"""
        data = self.iterate_over_data_frame(fields)
        try:
            for index, item in data:
                record = dict(item)
                record = {k: (v.strip() if type(v) is str else v) for k, v in record.items()}
                pharmacy_facility_id = int(record['pharmacy_facility_id'])
                _record_generated = func_create_record(record, pharmacy_facility_id, self.company_id)
                # store the created id in generated_ids dict
                generated_ids_dict[str(record[generated_ids_key])] = _record_generated.id
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    def process_data_for_patient_master(self, fields):
        """ Receives the fields for patient_master to be fetched form logical data frame created above.It then inserts the
        facility_id for the respective patient_id. It then creates a record in the patient_master table if it does not
        exists"""
        data = self.iterate_over_data_frame(fields)
        try:
            for index, item in data:
                dict_patient_master_data = dict(item)
                dict_patient_master_data["allergy"] = dict_patient_master_data.pop("patient_allergy")
                pharmacy_patient_id = str(dict_patient_master_data["pharmacy_patient_id"])
                dict_patient_master_data["patient_picture"] = dict_patient_master_data["patient_picture"].split('\\')[
                    -1]
                # dict_patient_master_data["patient_name"] = dict_patient_master_data["patient_name"]
                dict_patient_master_data["dob"] = datetime.datetime.strptime(dict_patient_master_data["dob"],
                                                                             "%Y%m%d").date()
                name = dict_patient_master_data["patient_name"].split(",", 1)
                dict_patient_master_data["last_name"] = name[0]
                dict_patient_master_data["first_name"] = name[1] if len(name) > 1 else ""
                dict_patient_master_data = {k: (v.strip() if type(v) is str else v) for k, v in
                                            dict_patient_master_data.items()}
                pharmacy_patient_id = int(dict_patient_master_data['pharmacy_patient_id'])
                # _record_generated = PatientMaster.db_update_or_create(
                #     dict_patient_master_data, pharmacy_patient_id,
                #     company_id=self.company_id,
                #     default_data_dict=self.default_data_dict,
                #     add_fields={
                #         'facility_id': self.facility_ids[str(dict_patient_master_data['pharmacy_facility_id'])]
                #     },
                #     remove_fields=['pharmacy_facility_id', 'patient_name']
                # )
                _record_generated = \
                    db_patient_master_update_or_create_dao(dict_patient_master_data=dict_patient_master_data,
                                                           pharmacy_patient_id=pharmacy_patient_id,
                                                           company_id=self.company_id,
                                                           default_data_dict=self.default_data_dict,
                                                           facility_id=
                                                           self.facility_ids[str(
                                                               dict_patient_master_data['pharmacy_facility_id'])],
                                                           remove_fields_list=['pharmacy_facility_id', 'patient_name'])

                self.patient_master_ids[str(dict_patient_master_data['pharmacy_patient_id'])] = _record_generated.id
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    def process_data_for_doctor_master(self, fields):
        """ Receives the fields for doctor master to be fetched form logical data frame created above.It then inserts the
        facility_id for the respective doctor_id. It then creates a record in the doctormaster table if it does not
        exists"""
        data = self.iterate_over_data_frame(fields)
        try:
            for index, item in data:
                dict_doctor_master_data = dict(item)
                dict_doctor_master_data["workphone"] = dict_doctor_master_data["doctor_phone"]
                name = dict_doctor_master_data["doctor_name"].split(",", 1)
                dict_doctor_master_data["last_name"] = name[0]
                dict_doctor_master_data["first_name"] = name[1] if len(name) > 1 else ""
                dict_doctor_master_data = {k: (v.strip() if type(v) is str else v) for k, v in
                                           dict_doctor_master_data.items()}
                pharmacy_doctor_id = int(dict_doctor_master_data['pharmacy_doctor_id'])
                # _record_generated = DoctorMaster.db_update_or_create(
                #     dict_doctor_master_data,
                #     pharmacy_doctor_id,
                #     company_id=self.company_id,
                #     default_data_dict=self.default_data_dict,
                #     remove_fields=['doctor_phone', 'doctor_name']
                # )
                _record_generated = db_doctor_master_update_or_create(dict_doctor_master_data=dict_doctor_master_data,
                                                                      pharmacy_doctor_id=pharmacy_doctor_id,
                                                                      company_id=self.company_id,
                                                                      default_data_dict=self.default_data_dict,
                                                                      remove_fields=['doctor_phone', 'doctor_name'])

                self.doctor_ids[str(dict_doctor_master_data['pharmacy_doctor_id'])] = _record_generated.id
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    def process_data_for_patient_rx(self, fields, stop_data):
        """ Receives the fields for the patient_rx to be fetched from logical data frame. It then associates doctor_id
        with each patient_rx record. It then inserts the record in patient_rx table if it is not present already"""
        data = self.iterate_over_data_frame(fields)
        total_quantity = False  # as it will be used for morning, noon, eve, bed thus, False
        try:
            for index, item in data:
                dict_patient_rx_info = dict(item)
                dict_patient_rx_info["patient_id"] = self.patient_master_ids[
                    str(dict_patient_rx_info["pharmacy_patient_id"])]
                dict_patient_rx_info["sig"] = str(dict_patient_rx_info["sig"]).strip()
                dict_patient_rx_info["morning"] = convert_quantity(dict_patient_rx_info["morning"], total_quantity)
                dict_patient_rx_info["noon"] = convert_quantity(dict_patient_rx_info["noon"], total_quantity)
                dict_patient_rx_info["evening"] = convert_quantity(dict_patient_rx_info["evening"], total_quantity)
                dict_patient_rx_info["bed"] = convert_quantity(dict_patient_rx_info["bed"], total_quantity)
                dict_patient_rx_info["remaining_refill"] = convert_quantity(dict_patient_rx_info["remaining_refill"],
                                                                            total_quantity)
                if dict_patient_rx_info["is_tapered"].strip() == 'Y':
                    dict_patient_rx_info["is_tapered"] = 1
                else:
                    dict_patient_rx_info["is_tapered"] = 0
                if dict_patient_rx_info["is_bubble"]:
                    dict_patient_rx_info["packaging_type"] = constants.PACKAGING_TYPE_BUBBLE_PACK
                else:
                    dict_patient_rx_info["packaging_type"] = constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4


                try:
                    drug_id = self.drug_ids[dict_patient_rx_info["ndc"]]
                except KeyError as e:
                    logger.error(e, exc_info=True)
                    raise FileParsingException(
                        PARSING_ERRORS["missing_drug"] + dict_patient_rx_info["ndc"])

                dict_patient_rx_info = {k: (v.strip() if type(v) is str else v) for k, v in
                                        dict_patient_rx_info.items()}
                # _record_generated = PatientRx.db_update_or_create_rx(
                #     dict_patient_rx_info["patient_id"],
                #     dict_patient_rx_info["pharmacy_rx_no"],
                #     dict_patient_rx_info,
                #     add_fields={
                #         'drug_id': drug_id,
                #         'doctor_id': self.doctor_ids[str(dict_patient_rx_info["pharmacy_doctor_id"])]
                #     },
                #     remove_fields=['pharmacy_doctor_id', 'ndc', 'pharmacy_id', 'pharmacy_patient_id'],
                #     default_data_dict=self.default_data_dict
                # )
                _record_generated = db_patient_rx_update_or_create_dao(dict_patient_rx_info=dict_patient_rx_info,
                                                                       drug_id=drug_id,
                                                                       doctor_id=self.doctor_ids[str(
                                                                           dict_patient_rx_info["pharmacy_doctor_id"])],
                                                                       remove_fields_list=['pharmacy_doctor_id', 'ndc',
                                                                                           'pharmacy_id',
                                                                                           'pharmacy_patient_id',
                                                                                           'is_bubble'],
                                                                       default_data_dict=self.default_data_dict,
                                                                       stop_data=stop_data)
                _id = _record_generated.id
                self.patient_rx_ids[str(dict_patient_rx_info['pharmacy_rx_no'])] = _id
                self.rx_drug_records[_id] = drug_id
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    def duplicate_file_check(self):
        """
        This is second level check which raises `DuplicateFileException`
        if any other process made entry to FileHeader with same file name and pending/process status.
        This will set file to error state if current process was not first to make entry to db.
        This should make sure only first file stays valid.
        :return:
        """
        status_list = [settings.PENDING_FILE_STATUS,
                       settings.PROCESSED_FILE_STATUS]
        # first_pending_file = FileHeader.select(FileHeader.id) \
        #     .where(FileHeader.filename == self.file,
        #            FileHeader.status << status_list,
        #            FileHeader.company_id == self.company_id) \
        #     .order_by(FileHeader.id).dicts()
        #
        # # print(list(first_pending_file)[0], self.file_id)
        # first_pending_file = first_pending_file.get()
        first_pending_file = db_get_file_by_filename_status_company_dao(filename=self.file, status=status_list,
                                                                        company_id=self.company_id)
        if first_pending_file['id'] != self.file_id:
            self.handle_file_processing_error(PARSING_ERRORS["duplicate_file"])
            logger.info('Multiple Request for File Upload Detected. '
                        'Setting error state for file_id: {}, '
                        'Considering file_id {} valid.'
                        .format(self.file_id, first_pending_file['id']))
            raise DuplicateFileException(PARSING_ERRORS["duplicate_file"])

    def record_file(self):
        """ Creates a record in the file header for the received file. Stores the id of the inserted record
        in the file_id variable"""

        try:
            file_dict = {
                'filepath': settings.PENDING_FILE_PATH,
                "manual_upload": self.manual_upload,
                "created_date": get_current_date(),
                "created_time": get_current_time(),
                "modified_date": get_current_date_time(),
                "company_id": self.company_id,
                "created_by": self.user_id,
                "modified_by": self.user_id
            }
            # _record = FileHeader.get_or_create(
            #     filename=self.file, status=settings.PENDING_FILE_STATUS,
            #     defaults={
            #         'filepath': settings.PENDING_FILE_PATH,
            #         "manual_upload": self.manual_upload,
            #         "created_date": get_current_date(),
            #         "created_time": get_current_time(),
            #         "modified_date": get_current_date_time(),
            #         "company_id": self.company_id,
            #         "created_by": self.user_id,
            #         "modified_by": self.user_id
            #     }
            # )
            _record = db_file_header_get_or_create_dao(filename=self.file, status=settings.PENDING_FILE_STATUS,
                                                       file_dict=file_dict)

            if not _record[1]:  # if record already present
                raise DuplicateFileException(PARSING_ERRORS["duplicate_file"])
            self.file_id = _record[0].id
            self.duplicate_file_check()  # check duplicate file # can happen due to concurrency issue
        except IntegrityError as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])
        except DataError as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    @staticmethod
    def make_success_response():
        return create_response(settings.SUCCESS)

    def add_task(self):
        try:
            logger.info(celery_app.conf.broker_url)
            logger.debug('Adding Task to parse file_id {} '.format(self.file_id))
            task_id = celery_app.send_task(
                'tasks.dpws_single_worker_tasks.fetch_and_parse_rx_file',
                (self.file_id, self.fill_manual, self.system_id, self.company_id,),
                retry=True
            )
            # FileHeader.db_update_task_id(self.file_id, task_id)
            db_file_header_update_task_id_dao(file_id=self.file_id, task_id=task_id)
            logger.debug('Task to parse file_id {} is queued with task_id {}'.format(self.file_id, task_id))
        except Exception as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS['add_task_failed'])
        finally:
            real_time_db_timestamp_trigger(settings.CONST_PRESCRIPTION_FILE_DOC_ID, company_id=self.company_id)

    def update_file(self, status, message, filepath):
        try:
            logger.debug('updating file: {} with status {}'.format(self.file_id, status))
            # return FileHeader.update(status=status, message=message, filepath=filepath).where(
            #     FileHeader.id == self.file_id).execute()
            return db_update_file_status_message_path_dao(status=status, message=message, filepath=filepath,
                                                          file_id=self.file_id)
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    def fetch_drug_id(self):
        """ Queries the data frame for all the unique ndc and gets the drug_id for them
        for the drug_master table."""
        ndc_data = self.df.ndc.unique()

        missing_ndc_list = ndc_data.tolist()  # copy list of ndc then remove which are already present
        if len(ndc_data) > 0:
            # for record in DrugMaster.select().dicts().where(DrugMaster.ndc << ndc_data.tolist()):
            for record in db_get_drug_data_by_ndc_parser_dao(ndc_list=ndc_data.tolist()):
                self.drug_ids[str(record['ndc'])] = record['id']
                missing_ndc_list.remove(record["ndc"])

        if missing_ndc_list:
            logger.info("Missing NDCs: " + str(missing_ndc_list))
            try:
                get_missing_drug_data(missing_ndc_list, self.company_id, self.user_id, self.file_id)
            except DrugFetchFailedException:
                raise FileParsingException(PARSING_ERRORS['drug_fetch'])

        try:  # get missing images
            get_missing_drug_images(ndc_data.tolist(), self.company_id, self.file_id, self.user_id)
        except Exception as e:
            logger.error(e, exc_info=True)

        try:
            if missing_ndc_list:
                # create a list of the unique ndcs
                ndc_list = ndc_data.tolist()
                # logger.debug("formatted ndc and txr data for file ID: {} - {}".format(self.file_id, ndc_txr))
                # Get actual drug_id from drug_master
                # for record in DrugMaster.select(DrugMaster.id,
                #                                 DrugMaster.ndc).dicts(). \
                #         where(DrugMaster.ndc << missing_ndc_list):
                for record in db_get_drug_data_by_ndc_parser_dao(ndc_list=missing_ndc_list):
                    self.drug_ids[str(record["ndc"])] = record["id"]
        except KeyError as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    def update_couch_db_documents(self, fields, template_id: int, autoprocess_template_flag: bool=False,
                                  change_rx: Optional[bool] = False, data_dict: Optional[Dict[str, Any]] = None):
        """
        This method is utilized to update Couch DB documents during ChangeRx flow. It will work for ChangeRx template
        as well as New Template with/without Old Pharmacy Fill ID
        """
        pharmacy_patient_id: str
        patient_id: int
        old_template_id: int = 0
        try:
            data = self.iterate_over_data_frame(fields)
            for index, item in data:
                pharmacy_patient_id = str(int(item["pharmacy_patient_id"]))
                patient_id = self.patient_master_ids[pharmacy_patient_id]

                logger.debug("Update CouchDB document along with uuid for New or Change Rx Template...")
                update_customize_template_couch_db_status(company_id=self.company_id, file_id=self.file_id,
                                                          patient_id=patient_id, add_flag=True)

                # TODO: Code commented because we do not need notifications on Template screen.
                # if change_rx:
                #     logger.debug("Update CouchDB Notifications for Change Rx Template...")
                #     patient_data = db_get_patient_name_patient_no_from_patient_id_dao(patient_id=patient_id)
                #     message = constants.NOTIFICATION_EXT_CHANGE_RX_GENERAL
                #
                #     more_info = {"pack_ids": [data_dict["pharmacy_fill_id"]], "ips_username": "",
                #                  "change_rx": True, "file_id": self.file_id, "patient_id": patient_id,
                #                  "patient_no": data_dict["patient_no"], "only_template": True}
                #
                #     Notifications(user_id=self.user_id, call_from_client=True).send_with_username(user_id=0,
                #                                                                                   message=message,
                #                                                                                   flow='general',
                #                                                                                   more_info=more_info,
                #                                                                                   add_current_user=
                #                                                                                   False)

                logger.debug("Old Pharmacy Fill ID List: {}".format(self.old_pharmacy_fill_id))
                if self.old_pharmacy_fill_id:
                    old_template_id = db_get_old_template_by_new_template_dao(template_id=template_id)

                    logger.debug("Old Template ID: {}, New Template ID: {}".format(old_template_id, template_id))
                    if old_template_id:
                        logger.debug("Find the CouchDB Notifications to update the new Template Details...")
                        update_notifications_couch_db_status(old_pharmacy_fill_id=self.old_pharmacy_fill_id,
                                                             company_id=self.company_id, file_id=self.file_id,
                                                             old_template_id=old_template_id,
                                                             new_template_id=template_id,
                                                             autoprocess_template_flag=autoprocess_template_flag,
                                                             new_pack_ids=[],
                                                             remove_action=False)

        except (IntegrityError, InternalError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    def create_templates(self, fields, change_rx: Optional[bool] = False, old_pharmacy_fill_id: List[int] = None):
        """Queries the data frame for all the unique patient_ids. Checks the template_details table
        if all the rx_no required for the given patient_id is present in the table. If all rx
        are present template_modified flag is set to 0 else 1. A record is created in template_master
        table for all the patient_id received"""
        data = self.iterate_over_data_frame(fields)
        templates_id = []
        ext_change_rx_data: Dict[str, Any] = dict()
        ext_change_rx_new_template_dict: Dict[str, Any] = dict()
        ext_change_rx_id: int = 0
        try:
            for index, item in data:
                item = dict(item)
                pharmacy_patient_id = str(int(item["pharmacy_patient_id"]))
                # combining date and time to datetime string
                item['delivery_datetime'] = '{}{}00'.format(item['delivery_date'], item['delivery_time']) \
                    if item['delivery_date'] and item['delivery_time'] else None

                if not change_rx:
                    is_modified = is_template_modified(
                        self.patient_master_ids[pharmacy_patient_id],
                        self.template_master_ids[pharmacy_patient_id],
                        self.company_id
                    )
                    system_id = self.system_id
                    # set system id if system is of type Manual Fill
                    # when we set system_id of template_master
                    # it will also be set in pack_details, which we don't want for
                    # dosepacker system type

                    # Update the Modification status to Yellow if template is modified as True will be returned and this
                    # will indicate a value of 1 i.e. Red
                    if is_modified:
                        # is_modified = TemplateMaster.IS_MODIFIED_MAP['YELLOW']
                        is_modified = template_is_modified_map['YELLOW']

                    # key = BaseModel.db_create_record(
                    #     item,
                    #     TemplateMaster,
                    #     add_fields={
                    #         'is_modified': is_modified,
                    #         'file_id': self.file_id,
                    #         'status': self.pending_template_status,
                    #         'created_date': get_current_date_time(),
                    #         'created_time': get_current_time(),
                    #         'company_id': self.company_id,
                    #         'patient_id': self.patient_master_ids[pharmacy_patient_id],
                    #         'delivery_datetime': item['delivery_datetime'] or None,
                    #         'system_id': system_id,
                    #         'fill_manual': self.fill_manual
                    #     },
                    #     remove_fields=['pharmacy_patient_id', 'quantity', 'hoa_time',
                    #                    'pharmacy_id', 'client_id', 'pharmacy_rx_no'],
                    #     get_or_create=False,
                    #     default_data_dict=self.default_data_dict
                    # )

                    if old_pharmacy_fill_id:
                        logger.debug("Fetch the last Change Rx record from ext_change_rx table..")
                        ext_change_rx_data = db_get_ext_change_rx_record(old_pharmacy_fill_id=old_pharmacy_fill_id,
                                                                         template_id=0,
                                                                         company_id=self.company_id)
                        if ext_change_rx_data:
                            ext_change_rx_id = ext_change_rx_data.get("ext_change_rx_id", [])
                            self.pending_template_status = ext_change_rx_data.get("ext_action", 0)
                    logger.debug("Auto-Process Template @ create_templates: {}".format(self.autoprocess_template))
                    key = db_template_master_create_record(item=item,
                                                           add_fields={
                                                               'is_modified': is_modified,
                                                               'file_id': self.file_id,
                                                               'status': self.pending_template_status,
                                                               'created_date': get_current_date_time(),
                                                               'created_time': get_current_time(),
                                                               'company_id': self.company_id,
                                                               'patient_id': self.patient_master_ids[pharmacy_patient_id],
                                                               'delivery_datetime': item['delivery_datetime'] or None,
                                                               'system_id': system_id,
                                                               'fill_manual': self.fill_manual,
                                                               'fill_start_date': item["fill_start_date"],
                                                               'fill_end_date': item["fill_end_date"],
                                                               'pharmacy_fill_id': item["pharmacy_fill_id"],
                                                               'pack_type_id': constants.MULTI_DOSE_PER_PACK if item['pack_type'] == 'Multi' else (constants.UNIT_DOSE_PER_PACK if item['pack_type'] == 'Unit' else None),
                                                               'customized': item['customization'],
                                                               'seperate_pack_per_dose': 1 if item.get("is_bubble", False) else (item['seperate_pack_per_dose'] if not isinstance(item['seperate_pack_per_dose'], str) else (1 if item['seperate_pack_per_dose'] == "Y" else 0)),
                                                               'true_unit': item['true_unit'],
                                                               "is_bubble": item.get("is_bubble", False)
                                                           },
                                                           remove_fields_list=['pharmacy_patient_id', 'quantity',
                                                                               'hoa_time',
                                                                               'pharmacy_id', 'client_id',
                                                                               'pharmacy_rx_no'],
                                                           default_data_dict=self.default_data_dict)
                    templates_id.append(key.id)

                    if old_pharmacy_fill_id:
                        ext_change_rx_new_template_dict = {"new_template": key.id}
                        update_ext_change_rx_new_template_dao(ext_change_rx_new_template_dict, ext_change_rx_id)

                else:
                    # Update the Modification Status as Yellow and then continue to get template data
                    is_modified = template_is_modified_map['YELLOW']
                    db_update_modification_status_by_change_rx(patient_id=self.patient_master_ids[pharmacy_patient_id],
                                                               file_id=self.file_id)

                    template_data = \
                        db_get_template_master_by_patient_and_file_dao(patient_id=
                                                                       self.patient_master_ids[pharmacy_patient_id],
                                                                       file_id=self.file_id)
                    if template_data:
                        templates_id.append(template_data["id"])

                # split_config = CompanySetting.db_get_template_split_settings(self.company_id)
                split_config = db_get_template_split_settings_dao(company_id=self.company_id)

                TEMPLATE_AUTO_SAVE = int(split_config.get('TEMPLATE_AUTO_SAVE', 0))
                VOLUME_BASED_TEMPLATE_SPLIT = int(split_config.get('VOLUME_BASED_TEMPLATE_SPLIT', 0))
                # IS_YELLOW_TEMPLATE = bool(int(os.environ.get("IS_YELLOW_TEMPLATE", "0")))
                if TEMPLATE_AUTO_SAVE:
                    logger.info('template_auto_save_on')
                    # if is_modified:
                    logger.info('Yellow_template_entering data for template details')
                    save_template_details(self.patient_master_ids[pharmacy_patient_id], self.file_id, self.company_id,
                                          self.user_id, is_modified=is_modified, file_upload=True)
            return templates_id
        except (IntegrityError, InternalError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    def check_pfill_id(self, fields):
        """ Checks if the pfill ids in the file are already available or not for a given system."""
        try:
            logger.debug("Inside check_pfill_id...")
            logger.debug("TempSlotInfo Fields List - {}...".format(fields))
            logger.debug("Data Frame: {}".format(self.df))
            data = self.iterate_over_data_frame(fields)
            logger.debug("Data Frame Generated...")
            pharmacy_fill_id_set = set()
            existing_pharmacy_fill_id_set = set()
            for index, item in data:
                item = dict(item)
                pharmacy_fill_id = int(item["pharmacy_fill_id"])
                pharmacy_fill_id_set.add(pharmacy_fill_id)

            # get file ids for which pharmacy fill id is already present
            # file_id_query = TempSlotInfo.select(
            #     TempSlotInfo.pharmacy_fill_id,
            #     TempSlotInfo.file_id) \
            #     .where(TempSlotInfo.pharmacy_fill_id << list(pharmacy_fill_id_set))
            file_id_query = db_get_template_file_id_by_pharmacy_fill_dao(pharmacy_fill_id_set=pharmacy_fill_id_set)

            file_ids = list()
            for record in file_id_query.dicts():
                file_ids.append(record['file_id'])

            logger.debug("files_found" + str(file_ids))

            # check if records with this pharmacy fill id exists or not
            if file_ids:
                # for record in FileHeader.select(FileHeader.id).distinct()\
                #             .where(FileHeader.company_id == self.company_id,
                #                     FileHeader.id << file_ids,
                #                    FileHeader.status != settings.UNGENERATE_FILE_STATUS).dicts():
                for record in db_get_file_info_not_ungenerated_dao(company_id=self.company_id, file_ids=file_ids,
                                                                   status=settings.UNGENERATE_FILE_STATUS):
                    # adds file id of existing pharmacy fill id to optimize the performance
                    existing_pharmacy_fill_id_set.add(record['id'])

            if not existing_pharmacy_fill_id_set:
                # allow processing of uploaded file
                return True

            return False

        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])
        except KeyError as e:
            logger.error(e, exc_info=True)
            raise FileParsingException("Key Error while fetching record from SlotTempInfo")

    def create_temp_table(self, fields, change_rx: bool = False):
        """ Creates a entry in the temp_slot_info table for all the records in the data frame. This table will
        be later used in generation of packs"""
        total_quantity = True  # as used for total quantity in file
        temp_slot_list = list()
        change_rx_status: int = 0

        try:
            data = self.iterate_over_data_frame(fields)
            for index, item in data:
                item = dict(item)
                change_rx_status = item.get("status", 0)

                item["quantity"] = convert_quantity(item["quantity"], total_quantity)
                item["hoa_time"] = convert_time(item["hoa_time"])
                item["hoa_date"] = datetime.datetime.strptime(item["hoa_date"], "%Y%m%d").date()
                item["fill_start_date"] = datetime.datetime.strptime(item["fill_start_date"], "%Y%m%d").date()
                item["fill_end_date"] = datetime.datetime.strptime(item["fill_end_date"], "%Y%m%d").date()
                item = {k: (v.strip() if type(v) is str else v) for k, v in
                        item.items()}
                patient_rx_id = self.patient_rx_ids[str(item["pharmacy_rx_no"])]
                drug_id = self.rx_drug_records[patient_rx_id]

                if (not change_rx) or (change_rx and change_rx_status == constants.EXTCHANGERXACTIONS_ADD):
                    self.template_master_ids[str(item["pharmacy_patient_id"])].add(str(item["pharmacy_rx_no"]).strip() +
                                                                                   settings.SEPARATOR + str(
                        item["quantity"]).strip() +
                                                                                   settings.SEPARATOR + str(
                        item["hoa_time"]).strip() + \
                                                                                   settings.SEPARATOR + str(drug_id))
                    if int(os.environ.get('TEMP_SLOT_INSERT_MANY', '1')):
                        temp_slot_list.append({
                            'file_id': self.file_id,
                            'patient_rx_id': patient_rx_id,
                            'patient_id': self.patient_master_ids[str(item["pharmacy_patient_id"])],
                            'quantity': item['quantity'],
                            'hoa_date': item['hoa_date'],
                            'hoa_time': item['hoa_time'],
                            'filled_by': item['filled_by'],
                            'fill_start_date': item['fill_start_date'],
                            'fill_end_date': item['fill_end_date'],
                            'delivery_schedule': item['delivery_schedule'],
                            'pharmacy_fill_id': item['pharmacy_fill_id'],
                        })
                    else:
                        # TODO keeping below code for reference
                        # BaseModel.db_create_record(
                        #     item,
                        #     TempSlotInfo,
                        #     default_data_dict=False,
                        #     add_fields={
                        #         'patient_id': self.patient_master_ids[str(item["pharmacy_patient_id"])],
                        #         'patient_rx_id': patient_rx_id,
                        #         'file_id': self.file_id
                        #     },
                        #     remove_fields=['pharmacy_patient_id', 'pharmacy_rx_no', 'pharmacy_facility_id'],
                        #     get_or_create=False
                        # )
                        db_temp_slot_info_create_record(item=item,
                                                        add_fields={
                                                            'patient_id':
                                                                self.patient_master_ids[str(item["pharmacy_patient_id"])],
                                                            'patient_rx_id': patient_rx_id,
                                                            'file_id': self.file_id
                                                        },
                                                        remove_fields_list=['pharmacy_patient_id', 'pharmacy_rx_no',
                                                                            'pharmacy_facility_id'])

                if change_rx and (change_rx_status == constants.EXTCHANGERXACTIONS_DELETE):
                    logger.info("Delete the entries from TempSlotInfo for the Rx that needs to be removed from Pack.")
                    db_delete_template_rx_info(patient_id=self.patient_master_ids[str(item["pharmacy_patient_id"])],
                                               file_ids=[self.file_id],
                                               patient_rx_id=patient_rx_id,
                                               start_date=item['fill_start_date'], end_date=item['fill_end_date'])

            if ((not change_rx) and int(os.environ.get('TEMP_SLOT_INSERT_MANY', '1'))) or (
                    change_rx and temp_slot_list):
                # BaseModel.db_create_multi_record(temp_slot_list, TempSlotInfo)
                db_temp_slot_info_create_multi_record(temp_slot_list=temp_slot_list)
        except (IntegrityError, InternalError, DataError, KeyError) as e:
            logger.error(e, exc_info=True)
            raise FileParsingException(PARSING_ERRORS["default"])

    def enqueue_task(self):
        try:
            self.record_file()
            logger.debug("Records inserted in file header with id: " + str(self.file_id))
            if settings.USE_FILE_TASK_QUEUE:
                self.upload_and_delete_file(self.filename)
                self.add_task()
                logger.debug('Task to add file {} done'.format(self.filename))
                return self.make_success_response()
            logger.info('Before processing')
            response = self.start_processing()
            logger.info('Response_of_file ' + str(response))
            return response
        except FileParsingException as e:
            self.handle_file_processing_error(e)
            return error(3001)
        except DuplicateFileException as e:
            return error(3002)

    def start_processing(self, update_prescription_v1=False, change_rx: Optional[bool] = False, stop_data: Optional[bool] = False,
                         template_master_data: Optional[List[Dict[str, Any]]] = None,
                         data_dict: Optional[Dict[str, Any]] = None):
        """ The main block for parsing the file. It calls all the helper functions and inserts the file data in
        proper tables.
        """
        patient_id: int = 0
        pharmacy_patient_id: int = 0
        keys_added: List[int] = []
        validation_errors = set()
        try:
            if change_rx:
                logger.debug("Change Rx -- Start Processing Method...")
                for template in template_master_data:
                    self.file_id = template["file_id"]
                    patient_id = template["patient_id"]
                    pharmacy_patient_id = data_dict["pharmacy_patient_id"]

            logger.debug("starting data frame")
            self.create_data_frame(change_rx)
            logger.debug("data frame created")
            df_copy = self.df.copy()

            logger.debug("fetching file validation error")
            validation_errors = file_validation(df_copy, self.file_id, change_rx)
            logger.debug("fetched validation error")
            # Fill all the NA values with 0
            self.df.fillna(0)

            if not change_rx:
                logger.debug("initiating fill id validation")
                if not self.validate_fill_id_count():
                    raise FileParsingException(PARSING_ERRORS['multiple_fill_id'])
                logger.debug("fill id validation done")

                logger.debug("temp_slot_info_fields validation initiated")
                status = self.check_pfill_id(self.temp_slot_info_fields)
                logger.debug("temp_slot_info_fields validation done")
                if not status:
                    raise FileParsingException(PARSING_ERRORS['duplicate_fill_id'])

            self.fetch_drug_id()  # keeping it outside as creates issue in thread.

            logger.debug("Begin File Processing with ID")

            if not change_rx:
                logger.debug("Inserting records in facility master")
                # func_partial_facility_master = partial(FacilityMaster.db_update_or_create,
                #                                        default_data_dict=self.default_data_dict)
                func_partial_facility_master = db_partial_update_create_facility_master_dao(default_data_dict=
                                                                                            self.default_data_dict)
                self.process_data(self.facility_master_fields, self.facility_ids, 'pharmacy_facility_id',
                                  func_partial_facility_master)

                logger.debug("Records inserted in facility master with ids: " + str(self.facility_ids))

            logger.debug("Inserting records in doctor master")
            self.process_data_for_doctor_master(self.doctor_master_fields)
            logger.debug("Records inserted in doctor master with ids: " + str(self.doctor_ids))

            with db.transaction():
                if not change_rx:
                    logger.debug("Inserting records in patient master")
                    self.process_data_for_patient_master(self.patient_master_fields)
                    logger.debug("Records inserted in patient master with ids: " + str(self.patient_master_ids))
                else:
                    self.patient_master_ids[str(pharmacy_patient_id)] = patient_id
                logger.debug("Records inserted in drug master with ids: " + str(self.drug_ids))

                logger.debug("Inserting records in patient rx")
                logger.info("In Parser.start_processing(): stop_date: {}".format(stop_data))
                self.process_data_for_patient_rx(self.patient_rx_fields, stop_data)
                logger.debug("Records inserted in patient rx with ids: " + str(self.patient_rx_ids))

                logger.debug("Inserting records in temp slot info")
                if change_rx:
                    logger.debug("Manipulation of temp slot info Fields...")
                    if "pharmacy_facility_id" in self.temp_slot_info_fields:
                        logger.debug("Remove pharmacy_facility_id field from temp slot info Fields List...")
                        self.temp_slot_info_fields.remove("pharmacy_facility_id")

                    logger.debug("Add status field in temp slot info Fields List...")
                    self.temp_slot_info_fields.append("status")

                self.create_temp_table(self.temp_slot_info_fields, change_rx)
                logger.debug("Records inserted in temp slot info")

                if change_rx:
                    logger.debug("Reset temp slot info Fields...")
                    logger.debug("Remove status field from temp slot info Fields List...")
                    self.temp_slot_info_fields.remove("status")
                    if "pharmacy_facility_id" not in self.temp_slot_info_fields:
                        logger.debug("Add pharmacy_facility_id field in temp slot info Fields List...")
                        self.temp_slot_info_fields.append("pharmacy_facility_id")

                logger.debug("Inserting records in template master")
                keys_added = self.create_templates(self.template_master_fields, change_rx=change_rx,
                                                   old_pharmacy_fill_id=self.old_pharmacy_fill_id)
                logger.debug("Records inserted in template master")
                logger.debug("End File Processing with ID: " + str(self.file_id))

                if not change_rx:
                    self.update_file(settings.PROCESSED_FILE_STATUS, "Success", settings.PROCESSED_FILE_PATH)
                else:
                    process_change_rx_insert_data(template_master_data=template_master_data, company_id=self.company_id,
                                                  data_dict=data_dict)
            try:
                update_pending_template_data_in_redisdb(self.company_id)
            except (RedisConnectionException, Exception) as e:
                logger.info(e)
                pass

            # Update Couch DB for incoming New Template or Change Rx Template document
            logger.debug("Auto-Process Template @ start_processing: {}".format(self.autoprocess_template))
            if keys_added:
                logger.debug("Update CouchDB documents related to New or Change Rx Template...")
                auto_process = False if self.autoprocess_template == 0 else True
                self.update_couch_db_documents(fields=self.template_master_fields, change_rx=change_rx,
                                               data_dict=data_dict, template_id=keys_added[0],
                                               autoprocess_template_flag=auto_process)

            # notify with newly generated templates and the file uploaded.
            if not settings.USE_FILE_TASK_QUEUE or update_prescription_v1:
                real_time_db_timestamp_trigger(settings.CONST_TEMPLATE_MASTER_DOC_ID, company_id=self.company_id)


            # if self.autoprocess_template:
                # time_zone_value: str = get_current_time_zone()
                # manual_fill_system: bool = False
                #
                # if self.old_pharmacy_fill_id:
                #     logger.debug("Auto-Process Templates based on New JSON for Change Rx...")
                #     ext_change_rx_data = db_get_ext_change_rx_record(old_pharmacy_fill_id=self.old_pharmacy_fill_id,
                #                                                      company_id=self.company_id)
                #     if ext_change_rx_data:
                #         current_template_id = ext_change_rx_data["current_template"]
                #         new_template_id = ext_change_rx_data["new_template"]
                #
                #         new_template_dict = db_get_template_master_info_by_template_id_dao(template_id=new_template_id)
                #         if change_rx:
                #             logger.debug("Auto-Process Templates into DosePacker system...")
                #         else:
                #             logger.debug("Decision making for Auto-Processing Templates into DosePacker or "
                #                          "Manual Fill system...")
                #
                #             logger.debug("Identify if the Old Packs are In Progress/Done/Manual or if they are pending "
                #                          "then verify the batch status and recommendation..")
                #             old_packs_dict = db_check_old_packs_status_for_new_template_process(
                #                 old_template_id=current_template_id)
                #
                #             if old_packs_dict["process_old_packs"]:
                #                 manual_fill_system = True
                #     else:
                #         logger.debug("ExtChangeRx Data not found for Pharmacy Fill ID: {} and Company ID: {}"
                #                      .format(self.old_pharmacy_fill_id, self.company_id))
                #         raise AutoProcessTemplateException
                # else:
                #     logger.debug("Independent Auto-Process Templates based on New JSON into DosePacker system...")
                #     if keys_added:
                #         new_template_dict = db_get_template_master_info_by_template_id_dao(template_id=keys_added[0])
                #     else:
                #         logger.debug("No Template found for Auto-Process...")
                #         raise AutoProcessTemplateException
                #
                # # {"data": {"33128": [1018]}, "user_id": 13, "company_id": 3, "time_zone": "+05:30",
                # #  "transfer_to_manual_fill_system": false, "system_id": 14}
                # generate_packs_dict: Dict[str, Any] = {"data": {str(new_template_dict["file_id"]):
                #                                                     [new_template_dict["patient_id"]]},
                #                                        "user_id": self.user_id,
                #                                        "company_id": self.company_id,
                #                                        "time_zone": time_zone_value,
                #                                        "transfer_to_manual_fill_system": manual_fill_system,
                #                                        "system_id": self.system_id,
                #                                        "version": constants.GENERATE_PACK_VERSION,
                #                                        "autoprocess_template": self.autoprocess_template,
                #                                        "access_token": self.token,
                #                                        "old_packs_dict": old_packs_dict,
                #                                        "ext_change_rx_data": ext_change_rx_data,
                #                                        "ips_user_name": self.ips_user_name
                #                                        }
                #
                # response = generate(generate_packs_dict)
                # parsed_response = json.loads(response)
                # if parsed_response["status"] == settings.FAILURE_RESPONSE:
                #     logger.debug("Error in Auto-processing of packs. Response: {}".format(response))

                # with db.transaction():
                #     if not manual_fill_system and not old_packs_dict["process_old_packs"]:
                #         if old_packs_dict["facility_dis_id"]:
                #             logger.debug("Update Facility Distribution ID: {} for packs generated with "
                #                          "New Template ID: {}".format(old_packs_dict["facility_dis_id"], keys_added[0]))
                #             update_pack_dict = {"facility_dis_id": old_packs_dict["facility_dis_id"]}
                #
                #             if old_packs_dict["batch_id"]:
                #                 logger.debug("Associate Batch ID: {} for packs generated with New Template ID: {}"
                #                              .format(old_packs_dict["batch_id"], keys_added[0]))
                #                 update_pack_dict.update({"batch_id": old_packs_dict["batch_id"]})
                #                 update_status = db_update_pack_details_by_template_dao(update_pack_dict=
                #                                                                        update_pack_dict,
                #                                                                        template_id=keys_added[0])
                #
                #                 if old_packs_dict["cr_recommendation_check"]:
                #                     logger.debug("Perform Canister Recommendation again for packs with New Template..")
                #                     # TODO: Pending to code Canister Recommendation code for new packs
                #
                #                 if old_packs_dict["mfd_recommendation_check"] and ext_change_rx_data:
                #                     logger.debug("Map the MFD recommendation of Old Packs with New Packs...")
                #                     delete_old_packs_after_mfd_map = \
                #                         db_check_and_update_mfd_recommendation_mapping(
                #                             batch_id=old_packs_dict["batch_id"],
                #                             old_template_id=ext_change_rx_data["current_template_id"],
                #                             new_template_id=keys_added[0])
                #
                #                     if delete_old_packs_after_mfd_map:
                #                         logger.debug("Delete the old packs for Old template ID if not already deleted.")
                #
                #                         ext_pharmacy_fill_ids = \
                #                             db_get_pharmacy_fill_id_by_ext_id_dao(ext_change_rx_id=
                #                                                                   ext_change_rx_data["ext_change_rx_id"]
                #                                                                   )
                #
                #                         ext_pack_details_dict = {"pack_display_ids": ext_pharmacy_fill_ids,
                #                                                  "technician_fill_status":
                #                                                      constants.EXT_PACK_STATUS_CODE_DELETED,
                #                                                  "technician_user_name": self.ips_user_name,
                #                                                  "technician_fill_comment":
                #                                                      constants.DELETE_REASON_EXT_CHANGE_RX,
                #                                                  "user_id": self.user_id,
                #                                                  "company_id": self.company_id,
                #                                                  "change_rx": True,
                #                                                  "ext_change_rx_id":
                #                                                      ext_change_rx_data["ext_change_rx_id"]}
                #                         response_dict = json.loads(update_ext_pack_status(ext_pack_details_dict))
                #                         status_code = response_dict.get("code",
                #                                                         constants.ERROR_CODE_CONNECTION_ISSUE_WHILE_FILE_SAVING)
                #                         if status_code != constants.IPS_STATUS_CODE_OK:
                #                             logger.debug(
                #                                 "Issue with processing delete operation for Pack Display ID: {}. "
                #                                 "Received Status = {}".format(ext_pharmacy_fill_ids, status_code))
                #                             raise AutoProcessTemplateException
                #             else:
                #                 update_status = db_update_pack_details_by_template_dao(update_pack_dict=
                #                                                                        update_pack_dict,
                #                                                                        template_id=keys_added[0])

            return self.make_success_response()
        except FileParsingException as e:
            self.handle_file_processing_error(e)
            return error(3001, e, validation_errors)
        except IOError as e:
            logger.error(e, exc_info=True)
            self.handle_file_processing_error(PARSING_ERRORS["default"])
            return error(3011, self.filename)
        except RealTimeDBException as e:
            logger.error(e, exc_info=True)
            return error(3001, self.filename)
        except AutoProcessTemplateException as e:
            logger.error(e, exc_info=True)
            pass
        except Exception as e:
            logger.error(e, exc_info=True)
            self.handle_file_processing_error(PARSING_ERRORS["default"])
            return error(3001, self.filename)
        finally:
            if not settings.USE_FILE_TASK_QUEUE:
                if self.upload_file_to_gcs:  # if need to upload to cloud storage
                    try:
                        t = ExcThread([], target=self.upload_and_delete_file, args=[self.filename])
                        t.start()
                    except Exception as e:
                        logger.error(e, exc_info=True)
                    real_time_db_timestamp_trigger(settings.CONST_PRESCRIPTION_FILE_DOC_ID, company_id=self.company_id)
            logger.debug("Auto-Process Template @ start_processing -> finally: {}".format(self.autoprocess_template))
            if self.autoprocess_template:
                try:
                    t2 = ExcThread([], target=self.autoprocess_templates_execution, args=[keys_added[0]])
                    t2.start()
                except Exception as e:
                    logger.error(e, exc_info=True)

    def autoprocess_templates_execution(self, new_template_id):
        old_packs_dict: Dict[str, Any] = {}
        ext_change_rx_data: Dict[str, Any] = {}

        try:
            logger.debug("Inside autoprocess_templates_execution function..")
            time_zone_value: str = get_current_time_zone()
            manual_fill_system: bool = False

            if new_template_id:
                ext_change_rx_data = db_get_ext_change_rx_record(old_pharmacy_fill_id=[],
                                                                 template_id=new_template_id,
                                                                 company_id=self.company_id)
            else:
                logger.debug("No Template found for Auto-Process...")
                raise AutoProcessTemplateException

            if ext_change_rx_data:
                current_template_ids = ext_change_rx_data["current_template"]
                new_template_id = ext_change_rx_data["new_template"]

                new_template_dict = db_get_template_master_info_by_template_id_dao(template_id=new_template_id)
                # if change_rx:
                #     logger.debug("Auto-Process Templates into DosePacker system...")
                # else:
                #     logger.debug("Decision making for Auto-Processing Templates into DosePacker or "
                #                  "Manual Fill system...")

                logger.debug("Identify if the Old Packs are In Progress/Done/Manual or if they are pending "
                             "then verify the batch status and recommendation..")
                old_packs_dict = db_check_old_packs_status_for_new_template_process(
                    old_template_id=current_template_ids, new_template_id=new_template_id)

                if old_packs_dict["process_old_packs"] or settings.TRANSFER_TO_MANUAL:
                    manual_fill_system = True
            else:
                logger.debug("Independent Auto-Process Templates based on New JSON into DosePacker system...")
                if settings.TRANSFER_TO_MANUAL:
                    manual_fill_system = True

                new_template_dict = db_get_template_master_info_by_template_id_dao(template_id=new_template_id)

                if self.old_pharmacy_fill_id:
                    logger.debug("ExtChangeRx Data not found for Pharmacy Fill ID: {} and Company ID: {}"
                                 .format(self.old_pharmacy_fill_id, self.company_id))
                    raise AutoProcessTemplateException

            # commented below part to comment [ if self.old_pharmacy_fill_id: ] condition for below case:--
            # If template t1 processed with 4 packs >> change rx with auto process off  : template t2 >> change rx with auto process on : at that time processchangerx API will called and [ if self.old_pharmacy_fill_id: ] = []
            # for this case >> we were not checked packs of template t1. and we directly send packs of template t2 to BD.

            # if self.old_pharmacy_fill_id:
            #     logger.debug("Auto-Process Templates based on New JSON for Change Rx...")
            #     if new_template_id:
            #         ext_change_rx_data = db_get_ext_change_rx_record(old_pharmacy_fill_id=[],
            #                                                          template_id=new_template_id,
            #                                                          company_id=self.company_id)
            #     else:
            #         logger.debug("No Template found for Auto-Process...")
            #         raise AutoProcessTemplateException
            #
            #     if ext_change_rx_data:
            #         current_template_id = ext_change_rx_data["current_template"]
            #         new_template_id = ext_change_rx_data["new_template"]
            #
            #         new_template_dict = db_get_template_master_info_by_template_id_dao(template_id=new_template_id)
            #         # if change_rx:
            #         #     logger.debug("Auto-Process Templates into DosePacker system...")
            #         # else:
            #         #     logger.debug("Decision making for Auto-Processing Templates into DosePacker or "
            #         #                  "Manual Fill system...")
            #
            #         logger.debug("Identify if the Old Packs are In Progress/Done/Manual or if they are pending "
            #                      "then verify the batch status and recommendation..")
            #         old_packs_dict = db_check_old_packs_status_for_new_template_process(
            #             old_template_id=current_template_id, new_template_id=new_template_id)
            #
            #         if old_packs_dict["process_old_packs"]:
            #             manual_fill_system = True
            #     else:
            #         logger.debug("ExtChangeRx Data not found for Pharmacy Fill ID: {} and Company ID: {}"
            #                      .format(self.old_pharmacy_fill_id, self.company_id))
            #         raise AutoProcessTemplateException
            # else:
            #     logger.debug("Independent Auto-Process Templates based on New JSON into DosePacker system...")
            #     if new_template_id:
            #         new_template_dict = db_get_template_master_info_by_template_id_dao(template_id=new_template_id)
            #     else:
            #         logger.debug("No Template found for Auto-Process...")
            #         raise AutoProcessTemplateException

            # {"data": {"33128": [1018]}, "user_id": 13, "company_id": 3, "time_zone": "+05:30",
            #  "transfer_to_manual_fill_system": false, "system_id": 14}
            generate_packs_dict: Dict[str, Any] = {"data": {str(new_template_dict["file_id"]):
                                                                [new_template_dict["patient_id"]]},
                                                   "user_id": self.user_id,
                                                   "company_id": self.company_id,
                                                   "time_zone": time_zone_value,
                                                   "transfer_to_manual_fill_system": manual_fill_system,
                                                   "system_id": self.system_id,
                                                   "version": constants.GENERATE_PACK_VERSION,
                                                   "autoprocess_template": self.autoprocess_template,
                                                   "access_token": self.token,
                                                   "old_packs_dict": old_packs_dict,
                                                   "ext_change_rx_data": ext_change_rx_data,
                                                   "ips_user_name": self.ips_user_name
                                                   }

            response = generate(generate_packs_dict)
            parsed_response = json.loads(response)
            if parsed_response["status"] == settings.FAILURE_RESPONSE:
                logger.debug("Error in Auto-processing of packs. Response: {}".format(response))
        except AutoProcessTemplateException as e:
            logger.error(e, exc_info=True)
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise

    def notify_templates(self, keys_added, manual_upload):
        """ when templates are gnerated from file, this routine will notify the templates
       """
        # response = {}
        # data = TemplateMaster.db_get_by_id(settings.PENDING_TEMPLATE_STATUS, keys_added)
        # for item in data:
        #     admin_date_list = TempSlotInfo.db_get_unique_dates(item["patient_id"], item["file_id"])
        #     if admin_date_list:
        #         from_date = admin_date_list[0].strftime('%m-%d-%y')
        #         to_date = admin_date_list[len(admin_date_list) - 1].strftime('%m-%d-%y')
        #         item["admin_period"] = from_date + " to " + to_date
        #     else:
        #         item["admin_period"] = "" # to keep data consistent
        # response["data"] = data
        # response["manual"] = manual_upload
        # response["system_id"] = self.system_id
        # publish(settings.TEST_PUB_BASE_URL, settings.TEST_PUB_ENDPOINT, 'template', json.dumps(response))

    def upload_and_delete_file(self, file_path, blob_dir=rx_file_blob_dir):
        """Uploads file into bucket and deletes local file"""
        try:
            logger.info('Uploading file {} on cloud'.format(self.filename))
            start_time = datetime.datetime.now()
            create_blob(file_path, self.file,
                        '{}/{}'.format(blob_dir, self.company_id))
            logger.info('done creating blob for file: {}'.format(self.filename))
            os.remove(file_path)
            end_time = datetime.datetime.now()
            logger.info('Time for uploading file: {} on cloud is {}s'.format(self.file,
                                                                             (end_time - start_time).total_seconds()))
        except Exception as e:
            logger.info('Error while downloading file from cloud: {}'.format(e))
            logger.error(e, exc_info=True)
            raise


class ParseError(object):
    """
    An parse-error object will be created whenever there is an error in file scheduler while parsing the file.
    """

    def __init__(self, status, filename, message, created_by=1, modified_by=1, manual_upload=False):
        """
        constructor to initialize the object.
        :param status: status of the file
        :param filename: name of the file
        :param message: error information
        :param created_by: id of the user who created
        :param modified_by: id of the user who modified
        """
        self.status = status
        self.file = filename
        self.message = message
        self.created_by = created_by
        self.modified_by = modified_by
        self.manual_upload = manual_upload
        self.file_id = None

    def record_parse_error(self):
        """
        records the parse error in fileheader table
        :return: None
        """

        try:
            file_dict = {'filename': self.file,
                         'status': self.status,
                         'message': self.message,
                         "created_date": get_current_date(),
                         "created_time": get_current_time(),
                         "modified_date": get_current_date_time(),
                         "created_by": self.created_by,
                         "modified_by": self.modified_by,
                         "manual_upload": self.manual_upload}
            _record = db_file_header_create_record_dao(file_dict=file_dict)
            self.file_id = _record[0].id
            return create_response(settings.SUCCESS)
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise FileParsingException("FileHeader record creation failed")
        except DataError as e:
            logger.error(e, exc_info=True)
            self.handle_file_processing_error(e)
            raise FileParsingException("FileHeader record creation failed")


@log_args_and_response
def db_check_split_old_and_new_template(old_template_id, new_template_id) -> bool:
    """
    returns whether Split exists between Old and New Template
    True --> Split exists
    False --> No Split
    """

    old_template: Dict[str, Any] = {}
    new_template: Dict[str, Any] = {}

    try:
        logger.debug("Check the admin duration between old and new packs...")
        old_template = db_get_template_admin_duration_by_template(old_template_id)
        new_template = db_get_template_admin_duration_by_template(new_template_id)

        if old_template and new_template:
            logger.debug("Old and New Template with TempSlotInfo exists...")

            if old_template["fill_start_date"] == new_template["fill_start_date"] and \
                    old_template["fill_end_date"] == new_template["fill_end_date"]:
                logger.debug("Old and New Template --> Admin duration matches...")

                old_template_args = {
                    "patient_id": old_template["patient_id"],
                    "file_id": old_template["file_id"],
                    "company_id": old_template["company_id"],
                }
                old_template_response = get_template_data_v2(old_template_args)

                new_template_args = {
                    "patient_id": new_template["patient_id"],
                    "file_id": new_template["file_id"],
                    "company_id": new_template["company_id"],
                }
                new_template_response = get_template_data_v2(new_template_args)

                old_packs_count = db_get_packs_count_by_template(old_template_id)
                new_packs_count = db_get_packs_count_by_template(new_template_id)

                if old_packs_count == new_packs_count:
                    logger.debug("Old and New Template --> Pack Count matches...")

                    old_pack_slot_data = db_get_pack_slot_count_by_template(old_template_id)
                    new_pack_slot_data = db_get_pack_slot_count_by_template(new_template_id)

                    if old_pack_slot_data.count() == new_pack_slot_data.count():
                        logger.debug("Old and New Template --> Pack and Slot count matches...")

                        check_pack_slot_hoa_split = db_get_pack_slot_hoa_split(old_pack_slot_data, new_pack_slot_data)
                        if not check_pack_slot_hoa_split:
                            logger.debug("Old and New Template --> Pack Count with Slot and HOA data matches...")
                            return False

        return True

    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_check_old_and_new_template_split(old_template_id, new_template_id):
    try:
        logger.debug("Fetch the Template Data for Old Template")
        old_template_dict = db_get_template_master_info_by_template_id_dao(template_id=old_template_id)
        template_args = {
            "patient_id": old_template_dict["patient_id"],
            "file_id": old_template_dict["file_id"],
            "company_id": old_template_dict["company_id"]
        }
        old_template_response = get_template_data_v2(template_args)

        logger.debug("Fetch the Template Data for New Template..")
        new_template_dict = db_get_template_master_info_by_template_id_dao(template_id=new_template_id)
        template_args = {
            "patient_id": new_template_dict["patient_id"],
            "file_id": new_template_dict["file_id"],
            "company_id": new_template_dict["company_id"]
        }
        new_template_response = get_template_data_v2(template_args)

        base_pack_count_by_old_template = \
            get_pack_requirement_by_template_column_number(template=old_template_response['template_data'],
                                                           base_pack_count_by_admin_duration=1)
        base_pack_count_by_new_template = \
            get_pack_requirement_by_template_column_number(template=new_template_response['template_data'],
                                                           base_pack_count_by_admin_duration=1)

        if base_pack_count_by_old_template != base_pack_count_by_new_template:
            return True

        return False

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException
