"""
    src.generate_packs
    ~~~~~~~~~~~~~~~~

    This module contains the core logic for generating packs from the temporary
    table. It has helper functions for fetching data from temporary table,
    creating packs from it, splitting the packs , persisting the split
    pack info back into the database, creating csv files for pharmacy_rx_no
    and slot details and sending this files to the pharmacy software.

    A general pack has seven rows and four columns. Every row represents a unique data
    and every column represents a time. A sample pack will look like this:
                  12:00:00 13:00:00 16:00:00   22:00:00
    2012-02-10      [0]      NaN      NaN           NaN
    2012-02-11      NaN      NaN      [1]           NaN
    2012-02-12      NaN      NaN      NaN           [2]
    2012-02-13      NaN      [3]      NaN           NaN
    2012-02-19      NaN      NaN      NaN  [4, 5, 6, 8]
    2012-02-29      NaN      NaN      NaN           [7]
    2012-02-29      NaN      NaN      NaN           [7]

    Example:
            $ obj_pack_gen = GeneratePacks(params)
              obj_pack_gen.start_generating_packs()

    Todo:
        Implement retry decorator if communication with the ips webservice fails.
        Proper Testing and performance measure with multi threading.

    :copyright: (c) 2015 by Dosepack LLC.

"""
import ast
import base64
import copy
import csv
import json
import math
import os
import threading
from collections import defaultdict
from datetime import timedelta, datetime
from io import StringIO
from itertools import cycle
from random import randint
from typing import Dict, Any, List

import cherrypy
import numpy as np
import pandas as pd
from kombu.exceptions import OperationalError
from peewee import InternalError, IntegrityError, DoesNotExist, fn, DataError

import settings
from com.pharmacy_software import send_data, is_response_valid
from dosepack.base_model.base_model import BaseModel, db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import get_current_date_time, log_args_and_response, batch, get_current_date
from dosepack.validation.validate import validate
from src import constants
from src.dao.batch_dao import get_batch_status
from src.dao.canister_dao import db_get_canister_drug_ids
from src.dao.company_setting_dao import db_get_template_split_settings_dao
from src.dao.device_manager_dao import get_system_id_based_on_device_type
from src.dao.ext_change_rx_couchdb_dao import update_notifications_couch_db_green_status, \
    update_couch_db_batch_distribution_status
from src.dao.ext_change_rx_dao import db_check_and_update_mfd_recommendation_mapping, \
    db_get_pharmacy_fill_id_by_ext_id_dao, db_check_linked_change_rx_details_by_patient_and_file, \
    db_get_ext_change_rx_record, db_get_ext_and_pack_details_for_template, db_get_new_pack_details_for_template
from src.dao.ext_file_dao import update_couch_db_pending_template_count
from src.dao.file_dao import db_verify_filelist_dao, get_file_upload_data_dao
from src.dao.mfd_dao import db_get_mfd_drugs_template_combination, \
    db_prepare_mfd_drug_template_column_unique_data, db_check_mfd_exists_for_batch_and_template, db_get_mfd_pack_status
from src.dao.misc_dao import get_company_setting_by_company_id
from src.dao.pack_analysis_dao import get_device_id_from_pack_list
from src.dao.pack_dao import get_pack_grid_id_dao, update_unit_dosage_flag, db_max_assign_order_no_manual_packs, \
    get_slot_details_data, insert_slot_data_dao, db_max_order_no_dao, get_ordered_pack_list, \
    db_get_pack_list_by_order_number, db_get_pack_user_map_old_template, insert_unassigned_pack_user_map_data_dao, \
    update_pack_details_and_insert_in_pack_user_map, update_unit_pack_for_multi_dosage_flag
from src.dao.pack_dao import insert_pack_user_map_data_dao, create_record_pack_rx_link_dao, create_record_slot_dao, \
    db_update_pack_details_by_template_dao, db_get_drug_info_old_template_packs, db_get_drug_info_new_template, \
    db_update_slot_details_drug_with_old_packs
from src.dao.pack_ext_dao import db_check_pack_user_map_data_dao
from src.dao.pack_queue_dao import insert_packs_to_pack_queue, remove_pack_from_pack_queue, \
    check_packs_in_pack_queue_or_not
from src.dao.patient_dao import db_get_patient_info_by_patient_id_dao
from src.dao.patient_schedule_dao import create_patient_schedule_dao, get_patient_schedule_data_dao, \
    update_patient_schedule_data_dao
from src.dao.template_dao import db_get_template, db_template_detail_columns, db_get_rx_records, \
    db_get_template_master_by_patient_and_file_dao, template_get_status_dao, get_template_file_id_dao, \
    update_template_status_with_template_id, get_template_id_dao, db_get_template_master_info_by_template_id_dao, \
    db_get_template_admin_duration_dao, get_template_flags, db_compare_min_admin_date_with_current_date, \
    db_setting_previous_facility_schedule_for_new_patient
from src.exc_thread import ExcThread
from src.exceptions import PackGenerationException, PharmacySoftwareCommunicationException, \
    PharmacySoftwareResponseException, PharmacyRxFileGenerationException, PharmacySlotFileGenerationException, \
    TemplateException, RedisConnectionException, RealTimeDBException, AutoProcessTemplateException
from src.model.model_celery_task_meta import CeleryTaskmeta
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_takeaway_template import TakeawayTemplate
from src.model.model_temp_slot_info import TempSlotInfo
from src.model.model_template_master import TemplateMaster
from src.pack_utilities import create_base_pack, create_child_pack
from src.redis_controller import update_pending_template_data_in_redisdb
from src.service.canister_recommendation import execute_recommendation_for_new_pack_after_change_rx, \
    update_drop_number_for_new_packs
from src.service.facility_schedule import update_delivery_date
from src.service.generate_templates import save_template_details, get_template_data_v2
from src.service.misc import remove_dir, update_queue_count, real_time_db_timestamp_trigger, \
    update_timestamp_couch_db_pre_processing_wizard, update_notifications_couch_db_status, fetch_systems_by_company
from src.service.notifications import Notifications
from src.service.pack import set_status, db_update_rx_changed_packs_manual_count
from src.service.pack_ext import update_ext_pack_status
from tasks.celery import celery_app

logger = settings.logger
lock = threading.Lock()


class GeneratePack(object):

    _TIMEOUT = (10, 25)

    def __init__(self, file_id, patient_id, user_id, order_no, pack_plate_location, canister_drug_ids_set,
                 company_id, company_settings, _type=1, version=1, time_zone=None,
                 transfer_to_manual_fill_system=False, assigned_to=None, system_id=None, template_id=None, token=None,
                 autoprocess_template=False):
        """
        Takes the constructor arguments to initialize the GeneratePack object.

        Args:
            file_id (int): The file_id for the data to be received.
            patient_id (int): The id of the patient for which the pack is to be created
            user_id (int): The id of the user who requests for pack generation
            order_no (boolean): The order no indicates whether to use order no feature
            pack_plate_location (boolean): This field indicates whether to use pack_plate_location feature
            canister_drug_ids_set (set): The set of drug ids for which we have canister
            company_id (int): Company ID
            company_settings (dict): settings which contains IPS communication
            _type(int): The type indicates if we were to disable IPS Communication or not
            version (int): version to use for pack generation method


        Examples:
            >>> GeneratePack(1, 1, 1, 100, False, {1,2,3}, 2, 2)
        """
        self.fill_strategy = 'STRICT_WEEKLY_FILL'
        self.template_data = None
        self.dummy_template = None
        self.time_zone = time_zone
        self.patient_id = patient_id
        self.file_id = file_id
        self.template_id = template_id
        self.user_id = user_id
        self.company_id = company_id
        self.system_id = None
        self.fill_manual = None
        self.company_settings = company_settings
        # fetches the data from temporary table and stores it here.
        self.data = []
        self.data_to_fill = []
        # keeps track of all the unique dates for the given patient_id
        self.unique_dates = set()
        # keeps track of all the unique columns for the given patient_id
        self.unique_template_columns = set()
        # stores the base id of the base pack generated
        self.base_pack_id = None
        # logical table to store the pack data
        self.pack_df = None
        self.takeaway_df = None
        self.generated_packs = []
        self.is_generated_packs_takeaway = list()
        # ids assigned by pharmacy for the given packs
        self.pharmacy_pack_id = []
        self.batch_ids = []
        self.pharmacy_fill_id = None
        self.dict_columns = defaultdict(lambda: defaultdict(dict))
        self.manual_drug_ids = {}
        self.canister_drug_ids_set = canister_drug_ids_set
        self.patient_no = None
        self.quantity_tracker = {}
        self.column_split_list = set()
        self.is_customized = False
        if _type == 0:
            self.DISABLE_IPS_COMMUNICATION = True
        elif _type == 1:
            self.DISABLE_IPS_COMMUNICATION = False
        elif _type == 2:
            self.DISABLE_IPS_COMMUNICATION = False

        self.pack_plate_location = pack_plate_location
        self.order_no = order_no
        self.version = version
        self.pack_details_ids = []
        self.max_column_number = None
        self.rx_file_counter = 0
        self.rx_file_data = list()
        self.slot_files = []
        self.combined_api = []
        self.delivery_datetime = None
        self.takeaway_template = dict()
        self.takeaway_weekdays = set()
        self.takeaway_ref_column_numbers = set()
        self.takeaway_columns = set()
        self.filled_at = None
        self.filled_date = None
        self.prepare_data_done = False  # status for `prepare_data` function was properly executed
        self.transfer_to_manual_fill_system = transfer_to_manual_fill_system
        self.assigned_to = assigned_to
        self.system_id = system_id
        self.token = token
        self.autoprocess_template = autoprocess_template
        self.old_packs_dict = {}
        self.ext_change_rx_data = {}
        self.ips_user_name = ""
        self.is_bubble = False
        self.pack_type = constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4

    def add_task(self):
        try:
            # self.validate_template_status()
            logger.debug("validating template status: "+str(get_current_date_time()))
            template_id = self.validate_task_queue()
            logger.info(celery_app.conf.broker_url)
            logger.info(settings.CONST_CELERY_SERVER_URL)
            logger.info(type(celery_app.conf.broker_url))
            logger.info(len(celery_app.conf.broker_url))
            task_id = celery_app.send_task(
                'tasks.dpws_multi_worker_tasks.generate_pack',
                (self.file_id, self.patient_id, self.user_id, self.company_id, self.version, self.time_zone,
                 self.transfer_to_manual_fill_system, self.assigned_to, self.system_id, self.template_id, self.token,
                 self.autoprocess_template, self.old_packs_dict, self.ext_change_rx_data, self.ips_user_name),
                retry=True
            )
            update_dict = {"task_id": task_id, "status":settings.PROGRESS_TEMPLATE_STATUS}
            update_template_status_with_template_id(template_id=template_id, update_dict=update_dict)
            logger.info('Task to generate template for file_id {} , patient_id {} is queued'.format(self.file_id, self.patient_id))
        except OperationalError as e:
            logger.error(e, exc_info=True)
            raise OperationalError("Server Error: Unable to process the selected template(s). Kindly contact support.")
        except PackGenerationException as e:
            raise PackGenerationException(e)
        except Exception as e:
            logger.error(e, exc_info=True)
            raise Exception(e)

    def initialize_auto_process_template_parameters(self, old_packs_dict, ext_change_rx_data, ips_user_name):
        self.old_packs_dict = old_packs_dict
        self.ext_change_rx_data = ext_change_rx_data
        self.ips_user_name = ips_user_name

    def validate_task_queue(self):
        try:
            template = db_get_template(self.file_id, self.patient_id)
            logger.info("Template to be processed - info: {}: ".format(str(template.id),str(template.status_id)))
            template_status = template.status_id
            logger.info("template status: "+str(template_status))
            self.fill_manual = template.fill_manual
            if CeleryTaskmeta.table_exists():
                queue_status = template.task_id.celery_task_status
            else:
                queue_status = None
            if self.fill_manual:
                self.system_id = template.system_id
            self.delivery_datetime = template.delivery_datetime
            if not template_status in settings.PENDING_TEMPLATE_LIST:
                if template_status != settings.PROGRESS_TEMPLATE_STATUS:
                    raise PackGenerationException("Some of the selected templates are already in the queue or rolled back. "
                                                  "Please reload the page to get the updated data.")
                elif template_status == settings.PROGRESS_TEMPLATE_STATUS and \
                        queue_status not in [settings.CELERY_TASK_SUCCESS_STATUS, settings.CELERY_TASK_FAILURE_STATUS]:
                    raise PackGenerationException(
                        "Some of the selected templates are already in the queue or rolled back. "
                        "Please reload the page to get the updated data.")
            return template.id
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException('Internal SQL Error.')
        except DoesNotExist:
            logger.debug('Pack generation request without template detected. file_id: {} and patient_id: {}'
                         .format(self.file_id, self.patient_id))
            raise PackGenerationException('No Template Found.')

    def get_pack_status(self):
        """ Returns status to set for pack """
        if self.fill_manual:
            # as marking manual automatic,
            # filled at should be 0 and filled_date should be current datetime
            if self.transfer_to_manual_fill_system:
                # self.filled_at = 1
                # self.filled_date = get_current_date_time()
                return settings.MANUAL_PACK_STATUS
            else:
                # self.filled_at = 0
                return settings.PENDING_PACK_STATUS
        elif self.transfer_to_manual_fill_system:
            # self.filled_at = 1
            # self.filled_date = get_current_date_time()
            return settings.MANUAL_PACK_STATUS
        return settings.PENDING_PACK_STATUS

    def validate_template_status(self):
        try:
            template = db_get_template(self.file_id, self.patient_id)
            template_status = template.status
            self.fill_manual = template.fill_manual
            if self.fill_manual:
                self.system_id = template.system_id
            self.delivery_datetime = template.delivery_datetime
            if settings.USE_TASK_QUEUE:
                if template_status.id != settings.PROGRESS_TEMPLATE_STATUS:
                    raise PackGenerationException("Template Already Processed or Rolled Back.")
            else:
                if template_status.id not in settings.PENDING_TEMPLATE_LIST:
                    raise PackGenerationException("Some of the selected templates are already in the queue or"
                                                  " rolled back. Please reload the page to get the updated data.")
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException('Internal SQL Error.')
        except DoesNotExist:
            logger.debug('Pack generation request without template detected. file_id: {} and patient_id: {}'
                         .format(self.file_id, self.patient_id))
            raise PackGenerationException('No Template Found.')

    def get_data(self):
        """ Gets the record from the temporary table and template details for the pack generation for given patient_id
        """
        try:
            temp_slot_data = {}
            for record in db_template_detail_columns(self.patient_id):
                self.unique_template_columns.add(record["column_number"])
                _key = str(record["patient_rx_id"]) + settings.SEPARATOR + str(record["hoa_time"])
                if "columns" not in self.dict_columns[_key]:
                    self.dict_columns[_key]["columns"] = []

                self.dict_columns[_key]["drug_id"] = record["drug_id"]
                self.dict_columns[_key]["columns"].append(record["column_number"])

                # self.dict_columns[_key].append(record["column_number"])
                _key += settings.SEPARATOR + str(record["column_number"])
                self.quantity_tracker[_key] = record["quantity"]
                if record["patient_rx_id"] in self.canister_drug_ids_set:
                    self.manual_drug_ids[record["patient_rx_id"]] = False
                else:
                    self.manual_drug_ids[record["patient_rx_id"]] = True
            logger.debug(threading.currentThread().getName() + "Template for the packs: " + str(self.quantity_tracker))

            for record in TempSlotInfo.db_get(self.patient_id, self.file_id):
                key_index_tuple = (record['patient_rx_id'], record['hoa_time'])
                if not key_index_tuple in temp_slot_data:
                    temp_slot_data[key_index_tuple] = [record]
                else:
                    temp_slot_data[key_index_tuple].append(record)

            updated_template_data = []
            for key, value in temp_slot_data.items():
                grouped_temp_slot_data = value
                first_record = grouped_temp_slot_data[0]
                admin_date_list = []
                # Find the minimum hoa_date value
                fill_start_date = min(list(TempSlotInfo.db_get(self.patient_id, self.file_id)), key=lambda x: x['hoa_date'])['hoa_date']
                while fill_start_date <= first_record['fill_end_date']:
                    admin_date_list.append(fill_start_date)
                    fill_start_date += timedelta(days=1)
                for temp_date in admin_date_list:
                    first_record_copy = first_record.copy()
                    first_record_copy['hoa_date'] = temp_date
                    updated_template_data.append(first_record_copy)

            if self.is_customized:
                for record in updated_template_data:
                    # only hoa_date, hoa_date and patient_rx_id will be used from all record of updated_template_data
                    # getting records for each slots from temp slot info which
                    # record['hoa_date'] = datetime.strptime("2023-12-01", "%Y-%m-%d")
                    _key = str(record["patient_rx_id"]) + settings.SEPARATOR + str(record["hoa_time"])

                    column_list = self.dict_columns[_key]["columns"]
                    # handling split columns
                    # creating data to fill which we will use to create df
                    for temp_record in self.dummy_template:
                        if temp_record['patient_rx_id'] == record['patient_rx_id'] and record['hoa_date'].strftime(
                                '%Y-%m-%d') in temp_record['admin_date_list'] and record['hoa_time'].strftime('%H:%M:%S') == \
                                temp_record['hoa_time']:
                            record['column_number'] = temp_record['column_number']
                            record['drug_id'] = temp_record['drug_id']
                            record['quantity'] = temp_record['quantity']
                            copy_record = copy.deepcopy(record)

                            self.data_to_fill.append(copy_record)
                    # to handle taper drug, if not split then use quantity from prescription as it is
                    if len(column_list) > 1:
                        record["quantity"] = self.quantity_tracker[_key + settings.SEPARATOR + str(column_list[0])]

                    for temp_record in self.template_data:
                        if temp_record['patient_rx_id'] == record['patient_rx_id'] and record['hoa_date'].strftime(
                                '%Y-%m-%d') in temp_record['admin_date_list'] and record['hoa_time'].strftime('%H:%M:%S') == \
                                temp_record['hoa_time']:
                            record['column_number'] = temp_record['column_number']
                            record['drug_id'] = temp_record['drug_id']
                            copy_record = copy.deepcopy(record)
                            # data is the list of dict we will use to persist slots
                            self.data.append(copy_record)

                    logger.info(f"PDT: prepare pack data: {self.data}")

                    self.unique_dates.add(record["hoa_date"])
                    self.pharmacy_fill_id = record["pharmacy_fill_id"]
            else:
                for record in TempSlotInfo.db_get(self.patient_id, self.file_id):
                    # getting records for each slots from temp slot info which
                    # record['hoa_date'] = datetime.strptime("2023-12-01", "%Y-%m-%d")
                    _key = str(record["patient_rx_id"]) + settings.SEPARATOR + str(record["hoa_time"])

                    column_list = self.dict_columns[_key]["columns"]
                    # handling split columns
                    # creating data to fill which we will use to create df
                    for column in column_list:
                        record["column_number"] = column

                        # to handle taper drug, if not split then use quantity from prescription as it is
                        if len(column_list) > 1:
                            record["quantity"] = self.quantity_tracker[_key + settings.SEPARATOR + str(column)]
                        record["drug_id"] = self.dict_columns[_key]["drug_id"]
                        temp_record = copy.deepcopy(record)
                        self.data.append(temp_record)

                    logger.info(f"PDT: prepare pack data: {self.data}")

                    self.unique_dates.add(record["hoa_date"])
                    self.pharmacy_fill_id = record["pharmacy_fill_id"]

            for record in TakeawayTemplate.db_get(self.patient_id):
                self.takeaway_template[record["template_column_number"], record["week_day"]] = record["column_number"]
                self.takeaway_weekdays.add(record["week_day"])
                self.takeaway_ref_column_numbers.add(record["template_column_number"])
                self.takeaway_columns.add(record["column_number"])

            if self.is_customized:
                # reordering data to fill to make it suitable for persisting slots
                self.data_to_fill = sorted(self.data_to_fill, key=lambda x: x['column_number'])

            logger.debug(threading.currentThread().getName() + "Data for the packs: " + str(self.data))
            self.max_column_number = max(self.unique_template_columns)
            self.unique_dates = sorted(self.unique_dates)
            self.unique_template_columns = sorted(self.unique_template_columns)
            self.takeaway_dates = [i for i in self.unique_dates if i.weekday() in self.takeaway_weekdays]
            # self.takeaway_times = sorted(self.takeaway_dates)
            self.takeaway_ref_column_numbers = sorted(self.takeaway_ref_column_numbers)
            self.takeaway_max_column_number = max(self.takeaway_columns, default=None)
        except (IntegrityError, InternalError, KeyError) as e:
            logger.error(f"in get_data error is {e}")
        except Exception as e:
            logger.error(f"in get_data error is {e}")

    def date_handling_for_fill_strategy(self, is_bubble=False):
        """
        This function will change date in dates for packs according to fill strategy
        - Below are the strategies can be used
        1) STRICT_WEEKLY_FILL
            Using this strategy will create pack for only continuous seven days, even when it can accommodate more days.
            It will skip those dates in pack.
            e.g. consider prescription dates [1 Jan, 4 Jan, 7 Jan, 8 Jan, 11 Jan, 14 Jan] with only one column
                 This will result in two packs with dates
                    1. [1 Jan, 4 Jan, 7 Jan]
                    2. [8 Jan, 11 Jan, 14 Jan]
        2) EFFICIENT_FILL
            Using this strategy will create pack in a way that there will be no empty row in a pack in between two days
            e.g. consider prescription dates [1 Jan, 4 Jan, 7 Jan, 8 Jan, 11 Jan, 14 Jan, 15 Jan] with only one column
                 This will result in one pack with dates
                    1. [1 Jan, 4 Jan, 7 Jan, 8 Jan, 11 Jan, 14 Jan, 15 Jan]
        :return:
        """
        self.fill_strategy = os.environ.get('PACK_FILL_STRATEGY', 'STRICT_WEEKLY_FILL')
        if self.fill_strategy == 'EFFICIENT_FILL':
            self.fill_dates = sorted(self.unique_dates)
            if self.takeaway_max_column_number:
                self.takeaway_fill_dates = sorted(self.takeaway_dates)
        else:
            # As a default we will use STRICT_WEEKLY_FILL

            hoa_date_range = (min(self.unique_dates), max(self.unique_dates))
            delta = hoa_date_range[1] - hoa_date_range[0]
            self.fill_dates = [hoa_date_range[0] + timedelta(i) for i in range(delta.days + 1)]
            # update unique dates for pack
            if self.takeaway_max_column_number:
                self.takeaway_fill_dates = list(self.fill_dates)
            self.fill_dates_df = self.fill_dates[:settings.PACK_ROW if not is_bubble else settings.BUBBLE_PACK_ROW]

    def create_empty_pack(self, row_names, col_names):
        """
        Takes the row_names and col_names and creates a matrix of size of length of row_names * length of col_names

        Args:
            row_names (list): The set of unique dates
            col_names (list): The set of unique columns which ranges from 1 to 16
            given patient_id

        Returns:
            pandas.DataFrame : A data frame indexed by row_names on x axis and col_names on y axis

        Examples:
            >>> GeneratePack().create_empty_pack(['2016-05-06', '2016-05-07'], [1,2])
                                    1      2
                    2016-05-06              NaN      NaN
                    2016-05-07              NaN      NaN
        """
        self.pack_df = pd.DataFrame(index=row_names, columns=col_names)
        logger.debug(str(self.pack_df))

    def create_empty_takeaway_pack(self, row_names, col_names):
        if row_names and col_names:
            self.takeaway_df = pd.DataFrame(index=row_names, columns=col_names)
            logger.debug("Takeaway DataFrame {}".format(self.takeaway_df))

    def get_patient_no(self, patient_id):
        """ returns patient_no given patient_id """
        try:
            self.patient_no = db_get_patient_info_by_patient_id_dao(patient_id=patient_id).patient_no
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException("Error in fetching patient data")
        except IntegrityError as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException("Error in fetching patient data")
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException("Internal SQL Error in fetching patient data")

    def populate_pack(self):
        """
            Takes  a list of records and extracts the date and column number from it.
            For every record it indexes the record to the empty data frame based
            on the extracted data and column number.

            Returns:
                pandas.DataFrame : A data frame containing inserted records from the the record list received.
                                    The data frame just contains the index to the inserted record

            Examples:
                >>> GeneratePack().populate_pack([{'hoa_date': '2016-05-06', 'hoa_time': '00:08:00', 'patient_id': 121}])
                                                    1           2
                        2016-05-06                [1,2,3]   [5, 6, 7]
                        2016-05-07                [8,9]      [4]
        """
        if self.is_customized:
            self.data = sorted(self.data, key=lambda x: x['column_number'])
        for index, item in enumerate(self.data):
            hoa_date = item["hoa_date"]
            column_number = item["column_number"]
            if (column_number, hoa_date.weekday()) not in self.takeaway_template:
                if not isinstance(self.pack_df.loc[hoa_date][column_number], list):
                    self.pack_df.loc[hoa_date][column_number] = []
                    self.pack_df.loc[hoa_date][column_number].append(index)
                else:
                    self.pack_df.loc[hoa_date][column_number].append(index)
            else:
                # using column number from takeaway template
                column_number = self.takeaway_template[column_number, hoa_date.weekday()]
                if not isinstance(self.takeaway_df.loc[hoa_date][column_number], list):
                    self.takeaway_df.loc[hoa_date][column_number] = []
                    self.takeaway_df.loc[hoa_date][column_number].append(index)
                else:
                    self.takeaway_df.loc[hoa_date][column_number].append(index)
                print("takeaway slot", item)
        logger.debug(threading.currentThread().getName() + "DataFrame for packs: " + str(self.pack_df))

    def split_pack(self, pack_df, is_takeaway=False, is_bubble=False):
        """
            Takes a big data frame containing every record for the patient and splits it into
            pack of size 7 * 4.

            Returns:
                list[pandas.DataFrames] : A list of data frame where every record represent the


            Examples:
                >>> GeneratePack().populate_pack([{'hoa_date': '2016-05-06', 'hoa_time': '00:08:00', 'patient_id': 121...}])
                                                    1          2
                        2016-05-06                [1,2,3]   [5, 6, 7]
                        2016-05-07                [8,9]      [4]
        """
        rows = pack_df.shape[0]
        cols = pack_df.shape[1]

        # Divide the pack matrix in blocks of 7 * 4

        no_of_cols_pack = math.ceil(cols / settings.PACK_COL)

        extra_cols = settings.PACK_COL - (cols % settings.PACK_COL)

        if extra_cols == settings.PACK_COL:
            extra_cols = settings.NULL

        for i in range(cols, extra_cols + cols):
            pack_df["extra_cols" + str(i)] = np.NaN

        split_x_axis = []

        for j in range(0, rows, settings.PACK_ROW if not is_bubble else settings.BUBBLE_PACK_ROW):
            split_x_axis.append(pack_df[j:j + (settings.PACK_ROW if not is_bubble else settings.BUBBLE_PACK_ROW)])

        # Split the matrix
        for packs in split_x_axis:
            split_y_axis = np.split(packs, no_of_cols_pack, axis=1)
            for sub_packs in split_y_axis:
                if self.fill_strategy == 'EFFICIENT_FILL':
                    sub_packs = sub_packs.dropna(how='all')  # drop all dates with all empty slot
                else:
                    # we have to keep empty rows in middle
                    while True:
                        first_row = sub_packs.iloc[0]  # Get the first row
                        if first_row.notna().any():
                            break  # Break the loop if a non-NaN row is found at either end
                        else:
                            sub_packs = sub_packs.iloc[1:]  # remove first row
                    while True:
                        last_row = sub_packs.iloc[-1]  # Get the last row
                        if last_row.notna().any():
                            break  # Break the loop if a non-NaN row is found at either end
                        else:
                            sub_packs = sub_packs.iloc[:-1]  # remove last row
                sub_packs = sub_packs.dropna(axis=1, how='all')  # drop all column with all empty slot
                if not sub_packs.empty:
                    self.is_generated_packs_takeaway.append(is_takeaway)
                    self.generated_packs.append(sub_packs)

        logger.debug(threading.currentThread().getName() + "Generated Packs: ")
        logger.debug(threading.currentThread().getName() + str(self.generated_packs))

    def persist_base_pack(self, total_packs):
        """
        Takes the total_no_of_packs and creates a base pack in the pack_header table. It returns the id
        of the created base pack.

        Args:
            total_packs (int): The total number of packs generated for the given patient_id

        Returns:
            id (int) : The id of the created base pack

        Examples:
            >>> GeneratePack().persist_base_pack(2)
                1001
        """
        linked_change_rx_exists: bool = False
        change_rx_flag: bool = False
        try:
            logger.info('t' + str(total_packs))

            logger.debug("Determine if the New Pack generation is linked with any previous Template through "
                         "Change Rx...")
            linked_change_rx_exists = db_check_linked_change_rx_details_by_patient_and_file(patient_id=self.patient_id,
                                                                                           file_id=self.file_id)
            if linked_change_rx_exists:
                change_rx_flag = True

            base_pack = BaseModel.db_create_record(create_base_pack(self.patient_id, self.file_id,
                                                                    self.data[0]["pharmacy_fill_id"], total_packs,
                                                                    self.delivery_datetime, self.user_id,
                                                                    change_rx_flag),
                                                   PackHeader, get_or_create=False)
            patient_data = db_get_patient_info_by_patient_id_dao(patient_id=self.patient_id)
            record, created = create_patient_schedule_dao(patient_id=self.patient_id,
                                                          facility_id=patient_data.facility_id,
                                                          total_packs=total_packs)
            logger.info(str(record)+ str(created))
            if created or record.active == False:
                try:
                    patient_schedule_data = get_patient_schedule_data_dao(facility_id=patient_data.facility_id, patient_id=self.patient_id)
                    schedule_id = patient_schedule_data['schedule_id']
                    delivery_date_offset = patient_schedule_data['delivery_date_offset']
                    logger.info('patient_schedule updated with patient_id {} and facility_id {}'
                                .format(self.patient_id, patient_data.facility_id))
                except DoesNotExist as e:
                    logger.info("No schedule exist for given facility.")
                    schedule_id = None
                    delivery_date_offset = None
                logger.info('__________________patient_id {}, faciliety_id {},'
                            ' scheduel_id {} and offset {}_______________'
                            .format(self.patient_id, patient_data.facility_id, schedule_id, delivery_date_offset))
                update_dict = {"modified_date": get_current_date_time(),
                               "last_import_date": fn.CONVERT_TZ(get_current_date_time(), '+00:00', self.time_zone),
                               "total_packs": total_packs,
                               "schedule_id": schedule_id,
                               "delivery_date_offset": delivery_date_offset,
                               "active": True}
                update_patient_schedule_data_dao(patient_schedule_id =record.id, update_dict=update_dict)
            else:
                update_dict = {"modified_date": get_current_date_time(),
                               "last_import_date": fn.CONVERT_TZ(get_current_date_time(), '+00:00', self.time_zone),
                               "total_packs": total_packs}
                update_patient_schedule_data_dao(patient_schedule_id=record.id, update_dict=update_dict)
            self.base_pack_id = base_pack.id
        except (IntegrityError, DataError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException("Error for the data to be inserted in the table PackHeader")

        logger.debug(threading.currentThread().getName() + "Base PackID Generated: " + str(base_pack))

    def persist_child_pack(self, base_pack_id, pharmacy_pack_id, pack_no, status, filled_by, filled_days, fill_start_date,
                           delivery_schedule, consumption_start_date, consumption_end_date, is_takeaway):
        """
        Stores the total packs generated for the given patient for a fill. The details are stored in the pack_details
        table. It returns the id of the pack after it is stored in the pack_details table.

        Args:
            base_pack_id (int): The base id of the pack generated for the patient.
            pharmacy_pack_id (int): The id assigned to the pack by the pharmacy software.
            pack_no (int): The order no of the generated pack.
            status (int): The status of the pack generated. The default status will be pending.
            filled_by (str): The user who created the file for the pack.
            fill_start_date (datetime): The start date for the pack filling.
            filled_days (int): The number of days for which the pack will be filled.
            delivery_schedule (datetime): The date at which the pack is supposed to be delivered to the patient.
            consumption_start_date (date): Start date of the pack
            consumption_end_date (date): Last date of the pack
            is_takeaway (date): True if pack is takeaway
        Returns:
            id (int) : The id of the created base pack

        Examples:
            >>> GeneratePack().persist_child_pack(1, 998016, 1, 1, 'Barry Geuiza', '2016-06-01', '2016-05-30')
                2000
        """
        pack_plate = None
        if self.order_no:
            self.order_no += 1
        try:
            child_pack = BaseModel.db_create_record(
                create_child_pack(
                    base_pack_id, pharmacy_pack_id,
                    pack_no, status,
                    filled_by, filled_days, fill_start_date,
                    delivery_schedule, self.user_id, pack_plate,
                    self.order_no, consumption_start_date, consumption_end_date,
                    self.company_id, self.system_id, is_takeaway,
                    self.filled_date, self.filled_at, is_bubble=self.is_bubble, pack_type=self.pack_type
                ), PackDetails, get_or_create=False)

            logger.debug(threading.currentThread().getName() + "Child PackID: " + str(child_pack))
            if self.transfer_to_manual_fill_system:
                old_pack_are_assigned = False
                logger.info("Identify if there used to be any pack from the Old Template and assigned to any "
                             "technician in Manual Flow. ")
                # --> Autoprocess flag is checked mainly to handle the scenario where template is not marked for
                # Autoprocess, but it is Change Rx template which needs to be processed manually.
                # --> In this case, when template is processed, we should have the logged-in user assigned in
                # Pack Fill Workflow.
                logger.info("Ext Change Rx Data: {}, Auto process Template: {}"
                             .format(self.ext_change_rx_data, self.autoprocess_template))

                if self.ext_change_rx_data:
                    user_id = db_get_pack_user_map_old_template(self.ext_change_rx_data)
                    if user_id:
                        old_pack_are_assigned = True
                        logger.info("User found from Old Packs: {}".format(user_id))
                    else:
                        logger.info("No user assigned to old packs, sending new pack unassigned ")
                        response = fetch_systems_by_company(company_id=self.company_id,
                                                            system_type=constants.AUTH_MF_SYSTEM_TYPE)
                        users = []
                        for record in list(response.values()):
                            users += record["users"]
                        if len(users) > 1:
                            user_id = None
                        else:
                            user_id = users[0]["user_id"]
                        # if there are multiple users assigned for system or multiple systems for same system type, we are not assigning user to the pack
                else:
                    logger.info("Assigning manual packs to {}".format(self.user_id))
                    response = fetch_systems_by_company(company_id=self.company_id,
                                                        system_type=constants.AUTH_MF_SYSTEM_TYPE)
                    users = []
                    for record in list(response.values()):
                        users += record["users"]
                    if len(users) > 1:
                        user_id = None
                    else:
                        user_id = users[0]["user_id"]
                    # if there are multiple users assigned for system or multiple systems for same system type, we are not assigning user to the pack

                if old_pack_are_assigned or not self.ext_change_rx_data:
                    pack_user_map = insert_pack_user_map_data_dao(pack_id=child_pack.id, user_id=user_id,
                                                                  date=get_current_date_time(), created_by=self.user_id)
                else:
                    pack_user_map = insert_unassigned_pack_user_map_data_dao(pack_id=child_pack.id, user_id=user_id,
                                                                             date=get_current_date_time(),
                                                                             created_by=self.user_id)

                logger.debug(threading.currentThread().getName() + "PackUserMap PackID: " + str(pack_user_map))
        except (IntegrityError, DataError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException("Error for the data to be inserted in the table PackDetails")
        return child_pack.id

    def persist_slot(self, pack_id, slot_row, slot_col, hoa_date, hoa_time):
        """
        Stores the slot info in the slot_header table. The slot info consists of
        pack_id , the row and column number for the given slot and the hoa_date
        and hoa_time associated with the slot. It creates a slot object and stores it
        in the slot_header table.

        Args:
            pack_id  (int):  The pack_id for which the slot will be created.
            slot_row (int): The row number for the slot. It is usually from 0 to 6.
            slot_col (int): The column_number for the slot. It is usually from 0 to 3.
            hoa_date (date): The house of administration date associated with the slot..
            hoa_time (time): The house of administration time associated with the slot.

        Returns:
            id (int) : The id of the created slot.

        Examples:
            >>> GeneratePack().persist_child_pack(1, 0, 0, '2016-06-01', '00:08:00')
                1100
        """
        try:
            pack_grid_id = get_pack_grid_id_dao(slot_row=slot_row, slot_column=slot_col)
            slot = create_record_slot_dao(data={
                "pack_id": pack_id, "pack_grid_id": pack_grid_id,
                "hoa_date": hoa_date, "hoa_time": hoa_time
            })

            return slot.id
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException("Error for the data to be inserted in the table SlotHeader")

    def persist_pack_rx_link(self, pack_id, patient_rx_id):
        """
        Stores the pack_id and all the rx nos associated with it.

        Args:
            pack_id  (int):  The pack_id for which the slot will be created.
            patient_rx_id (int): The patient_rx_id from the patient_rx table.

        Returns:
            id (int) : The id of the created pack_rx_link.

        Examples:
            >>> GeneratePack().persist_child_pack(1, 231)
                1100
        """
        try:
            pack_rx_link_record = create_record_pack_rx_link_dao(data={
                "pack_id": pack_id,
                "patient_rx_id": patient_rx_id
            })

        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException("Error for the data to be inserted in the table PackRxLink")

        return pack_rx_link_record.id

    def get_pharmacy_pack_id(self, pharmacy_fill_id):
        """
        Makes a webservice call to the pharmacy software and gets the
        pharmacy_pack_ids for the generated packs.

        Args:
            pharmacy_fill_id  (int):  The fill_id created for the patient during file generation

        Returns:
            (list) : The pharmacy_fill_ids for the given number of packs

        Examples:
            >>> GeneratePack().get_pharmacy_pack_id(882017, 3)
                [882017, 882018
        """
        try:
            no_of_packs = len(self.generated_packs)
            if no_of_packs == 1:
                self.pharmacy_pack_id = [self.pharmacy_fill_id]
                self.batch_ids = [self.pharmacy_fill_id]
                logger.info("getpackids skipped: single pack")
                return
            if self.DISABLE_IPS_COMMUNICATION:
                self.pharmacy_pack_id = [randint(1, 1000) for i in range(no_of_packs)]
                self.batch_ids = [randint(1, 1000) for i in range(no_of_packs)]
            else:
                data = send_data(
                    self.company_settings["BASE_URL_IPS"],
                    settings.PHARMACY_PACK_IDS_URL, {
                        "batchid": pharmacy_fill_id, "qty": no_of_packs,
                        'token': self.company_settings["IPS_COMM_TOKEN"]
                    },
                    0, _async=False, token=self.company_settings["IPS_COMM_TOKEN"],
                    timeout=self._TIMEOUT
                )
                self.pharmacy_pack_id = data["response"]["data"].split(',')
                self.batch_ids = data["response"]["data"].split(',')
        except PharmacySoftwareCommunicationException as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException("Not able to communicate with pharmacy software to get fill ids.")
        except PharmacySoftwareResponseException as e:
            logger.error(e, exc_info=True)
            raise PackGenerationException("Invalid response from pharmacy software for fill ids")

        logger.debug(threading.currentThread().getName() + "Pharmacy pack ids received from IPS: " + str(self.pharmacy_pack_id))


    def persist_data(self, df_pack, pack_ids_dict):
        """
        Takes a pack data frame and persists the data of the entire pack in the database. It inserts the
        data in the pack_header, pack_details, pack_rx_link, slot_header, slot_details.

        Args:
            df_pack (list): The list containing the series of generated data frames for packs

        Returns:
            (boolean) : True if pack_creation is successful or else False

        Examples:
            >>> GeneratePack().persist_data([])
                True
        """
        logger.info("Inside persist_data {}, {}".format(df_pack, pack_ids_dict))
        pack_no = 0
        notification_data=list()
        file_upload_date = get_file_upload_data_dao(file_id=self.file_id)
        prev_hoa_time = None
        prev_hoa_date = None

        for index, packs in enumerate(df_pack):
            pack_no += 1
            slot_details_list = []
            # Get the corresponding row and col count for pack
            rows = packs.shape[0]
            cols = packs.shape[1]
            if self.is_customized:
                prev_hoa_time = None
                prev_hoa_date = None
                for i in range(cols):
                    try:
                        consumption_start_date = self.data_to_fill[packs.iloc[0, i][0]]['hoa_date']
                    except TypeError as e:
                        for k in range(rows - 1):
                            try:
                                prev_hoa_time = self.data_to_fill[packs.iloc[(k + 1), i][0]]['hoa_time']
                                prev_hoa_date = self.data_to_fill[packs.iloc[(k + 1), i][0]]['hoa_date']
                            except TypeError as e:
                                continue
                            if prev_hoa_date:
                                break
                        continue
                    if consumption_start_date:
                        hoa_time = self.data_to_fill[packs.iloc[0, i][0]]['hoa_time']
                        if hoa_time == prev_hoa_time:
                            consumption_start_date = prev_hoa_date
                        break
                prev_hoa_time = None
                prev_hoa_date = None
                for i in range(cols):
                    try:
                        consumption_end_date = self.data_to_fill[packs.iloc[(rows - 1), (cols - i - 1)][0]]['hoa_date']
                    except TypeError as e:
                        for k in range(rows - 1):
                            try:
                                prev_hoa_time = self.data_to_fill[packs.iloc[(rows - 2 - k), (cols - i - 1)][0]][
                                    'hoa_time']
                                prev_hoa_date = self.data_to_fill[packs.iloc[(rows - 2 - k), (cols - i - 1)][0]][
                                    'hoa_date']
                            except TypeError as e:
                                continue
                            if prev_hoa_date:
                                break
                        continue
                    if consumption_end_date:
                        hoa_time = self.data_to_fill[packs.iloc[(rows - 1), (cols - i - 1)][0]]['hoa_time']
                        if hoa_time == prev_hoa_time:
                            consumption_end_date = prev_hoa_date
                        break
            else:
                consumption_start_date = packs.axes[0][0]  # getting first date of pack
                consumption_end_date = packs.axes[0][len(packs.axes[0]) - 1]
            names = packs.columns.tolist()
            # Fill all the na with 0
            packs = packs.fillna(0)
            # convert list to matrix
            mat = packs.as_matrix(columns=names)
            if isinstance(mat[0][0], list) and mat[0][0]:
                pack_details_record = self.data[mat[0][0][0]]
            elif isinstance(mat[0][1], list) and mat[0][1]:
                pack_details_record = self.data[mat[0][1][0]]
            elif isinstance(mat[0][2], list) and mat[0][2]:
                pack_details_record = self.data[mat[0][2][0]]
            elif isinstance(mat[0][3], list) and mat[0][3]:
                pack_details_record = self.data[mat[0][3][0]]
            elif isinstance(mat[3][0], list) and mat[3][0]:
                pack_details_record = self.data[mat[3][0][0]]
            elif isinstance(mat[6][0], list) and mat[6][0]:
                pack_details_record = self.data[mat[6][0][0]]
            pack_display_id = self.pharmacy_pack_id.pop(0)
            status = self.get_pack_status()
            rx_no_total_quantity_dict = defaultdict(int)
            rx_no_distinct_date_set = set()
            pack_rx_id_dict = {}
            pharmacy_fill_id = pack_details_record["pharmacy_fill_id"]
            filled_days = (consumption_end_date - consumption_start_date).days + 1
            pack_details_id = self.persist_child_pack(
                self.base_pack_id, pack_display_id, pack_no, status,
                pack_details_record["filled_by"], filled_days,
                pack_details_record["fill_start_date"],
                pack_details_record["delivery_schedule"],
                consumption_start_date,
                consumption_end_date,
                self.is_generated_packs_takeaway[index]
            )
            if self.transfer_to_manual_fill_system:
                notification_data.append({"pack_id": pack_details_id, "assigned_to": self.user_id, "assigned_from":None})
            else:
                notification_data.append({ "pack_id": pack_details_id})

            if self.patient_id not in pack_ids_dict:
                pack_ids_dict[self.patient_id] = list()
            pack_ids_dict[self.patient_id].append(pack_details_id)
            # Iterate over the pack
            for i in range(0, rows):
                for j in range(0, cols):
                    # check if data is of type list and the list is not empty
                    if isinstance(mat[i][j], list) and mat[i][j]:
                        record = mat[i][j]
                        if self.is_customized:
                            data = self.data_to_fill
                        else:
                            data = self.data
                        slot_header_id = self.persist_slot(
                            pack_details_id, i, j,
                            data[record[0]]["hoa_date"], data[record[0]]["hoa_time"]
                        )
                        logger.info("record in persist_data {}".format(record))
                        for item in record:
                            patient_rx_id = data[item]["patient_rx_id"]
                            quantity = data[item]["quantity"]
                            original_drug_id = data[item]["drug_id"]
                            drug_id = data[item]["drug_id"]

                            try:
                                pack_rx_id = pack_rx_id_dict[patient_rx_id]
                            except KeyError:
                                pack_rx_id = self.persist_pack_rx_link(pack_details_id, patient_rx_id)
                                pack_rx_id_dict[patient_rx_id] = pack_rx_id

                            is_manual = self.manual_drug_ids[patient_rx_id]
                            rx_no_total_quantity_dict[
                                (patient_rx_id, data[item]["hoa_time"].strftime('%H:%M:%S'),
                                 data[item]["column_number"])] += quantity
                            rx_no_distinct_date_set.add(data[item]["hoa_date"].strftime('%Y-%m-%d'))

                            slot_details_dict = {"slot_id": slot_header_id, "pack_rx_id": pack_rx_id,
                                                 "quantity": quantity, "is_manual": is_manual,
                                                 "original_drug_id": original_drug_id, "drug_id": drug_id}
                            slot_details_list.append(slot_details_dict)
            try:
                logger.info(f"PDT: persist_data insert data in slot details: {slot_details_list}")
                with db.atomic():
                    status = insert_slot_data_dao(slot_details_list)
                    logger.debug(threading.currentThread().getName() + "Inserting Record for SlotDetails Status: " + str(status))
            except (IntegrityError, DataError, InternalError) as e:
                logger.error(f"error in persist_data {slot_details_list}")
                logger.error(e, exc_info=True)
                raise PackGenerationException("Error for the data to be inserted in the table SlotDetails")

            self.pack_details_ids.append(pack_details_id)

            if not self.DISABLE_IPS_COMMUNICATION:
                self.create_files(pack_details_id, pack_display_id, pharmacy_fill_id, rx_no_total_quantity_dict, rx_no_distinct_date_set)

        print("notification data in packgeneration: ", notification_data)
        Notifications(self.token).generate_and_upload(file_upload_date, notification_data)

    def create_files(self, pack_details_id, pack_display_id, pharmacy_fill_id, rx_no_total_quantity_dict, rx_no_distinct_date_set):
        """
        Takes the functions for getting file data and creates csv files from the data received and
        then send the file to the pharmacy software for update.

        Args:
            pack_details_id (int): The id of the pack.
            pack_display_id (int): The pharmacy id of the pack.
            pharmacy_fill_id (int): The fill id generated by the pharmacy.
            rx_no_total_quantity_dict (dict): The total quantity for every distinct rx present dict
            rx_no_distinct_date_set (set): The date set for every distinct rx

        Returns:
            (boolean) : True if pack_creation is successful or else False

        Examples:
            >>> GeneratePack().create_files([])
                True
        """
        logger.debug(threading.currentThread().getName()
                     + threading.currentThread().getName()
                     + 'Starting File Generation for IPS')
        rx_data = self.create_pharmacy_rx_file(
            pack_details_id, pack_display_id, pharmacy_fill_id, rx_no_total_quantity_dict,
            rx_no_distinct_date_set, self.patient_no
        )
        slot_data = self.create_pharmacy_slot_file(pack_details_id)

        # rx_file_path = os.path.join(settings.PHARMACY_RX_FILE_PATH, str(self.system_id))
        slot_file_path = os.path.join(settings.PHARMACY_SLOT_FILE_PATH, str(self.system_id))
        slot_file = os.path.join(slot_file_path, str(pack_details_id) + ".csv")
        # rx_file = os.path.join(rx_file_path, str(self.pharmacy_fill_id) + ".csv")
        # if self.rx_file_counter == 0:
        #     remove_present_file(rx_file)

        # self.rx_file_counter += 1

        remove_present_file(slot_file)
        # self.create_csv_file(rx_data, rx_file_path, str(self.pharmacy_fill_id) + ".csv", ",")

        self.rx_file_data.extend(rx_data)
        self.create_csv_file(slot_data, slot_file_path, str(pack_details_id) + ".csv", ",")
        self.slot_files.append(str(pack_details_id) + ".csv")  # maintain list of all slot files

        logger.debug(threading.currentThread().getName() + "csv files created for pack id: " + str(pack_details_id))

        slot_file_data = self.get_file_data_b64encoded(slot_file)
        if not slot_file_data:
            logger.error("Couldn't get slot file data")
            slot_file_data = ""
        args = {
            "file": str(pack_details_id) + ".csv", "note": slot_file_data,
            'token': self.company_settings["IPS_COMM_TOKEN"]
        }
        self.combined_api.append({
            'api_name': settings.PHARMACY_SLOT_FILE_STORE_URL.split('/')[2],
            'api_args': args
        })

    @staticmethod
    def create_pharmacy_rx_file(pack_id, pharmacy_pack_id, pharmacy_fill_id,
                                dict_total_quantity, distinct_date_set, patient_no):
        """
        Takes a pack data frame and persists the data of the entire pack in the database. It inserts the
        data in the pack_header, pack_details, pack_rx_link, slot_header, slot_details.

        Args:
            pack_id (int): The pack_id for the given pack
            pharmacy_pack_id (int): The pharmacy_pack_id for the given pack_id
            pharmacy_fill_id (int): The pharmacy_fill_id associated with the given pack
            dict_total_quantity (dict): A dict containing all the distinct rx_no along with the total
            quantity associated with them for the given pack_id
            distinct_date_set (set): The set of distinct dates associated with the given pack_id

        Returns:
            pharmacy_rx_list(list) : A list containing distinct pharmacy_rx no for the given pack_id

        Examples:
            >>> GeneratePack().create_pharmacy_rx_file(1, 882019, 882019, {"34563": 24, "34567": 14}, set('2016-06-05', '2016-06-06'))
                True
        """
        # pharmacy file creation
        column_number_list = [0]
        pharmacy_rx_list = []
        distinct_date_set = list(sorted(distinct_date_set))
        for record in db_get_rx_records(pack_id, dict_total_quantity, distinct_date_set):
            if record["column_number"] not in column_number_list:
                column_number_list.append(record["column_number"])
            column_number = column_number_list.index(record["column_number"])  # setting pack column number instead of template column number
            pharmacy_rx_list.append([pack_id, patient_no, record["pharmacy_rx_no"], pharmacy_pack_id, pharmacy_fill_id,
                                     record["quantity"], record["total_quantity"], column_number,
                                     record["hoa_time"], record["date_list"]])

        if not pharmacy_rx_list:
            raise PharmacyRxFileGenerationException("PharmacyRxFile could not be generated for pack id: " + str(pack_id))

        return pharmacy_rx_list

    @staticmethod
    def create_pharmacy_slot_file(pack_id):
        """
        Takes a pack_id and creates a slot file containing all the slot_details to be sent to pharmacy software.

        Args:
            pack_id (int): The pack_id for the given pack
        Returns:
            pharmacy_slot_list(list) : List containing the slot details for the given pack_id

        Examples:
            >>> GeneratePack().create_pharmacy_slot_file(1)
                True
        """
        pharmacy_slot_list = []
        # slot details file creation
        for record in get_slot_details_data(pack_id):
            pharmacy_slot_list.append([record["pack_display_id"], 1, record["hoa_date"], record["hoa_time"],
                                       record["slot_row"], record["slot_column"], record["pharmacy_rx_no"], record["quantity"]])
        # todo check for value 1 in pharmacy slot list after pack_display_list

        if not pharmacy_slot_list:
            raise PharmacySlotFileGenerationException("PharmacySlotFile could not be generated for pack id: " + str(pack_id))

        return pharmacy_slot_list

    @staticmethod
    def get_file_data_b64encoded(file_path=None, file_content=None, bin_decoder="utf-8"):
        """
        Reads data in binary mode and encodes it using base64.
        At last returns string from binary data.

        :param file_path: Path to the file
        :param file_content: content of the file
        :param bin_decoder: (str | None) Decoder for binary data
        :return: str
        """
        data = None
        try:
            if file_path:
                with open(file_path, "rb") as f:
                    data = base64.b64encode(f.read())
            if file_content:
                data = base64.b64encode(file_content)
            if bin_decoder:
                data = data.decode(bin_decoder)
            return data
        except TypeError as e:
            logger.error(e, exc_info=True)
            return None
        except OSError as e:
            logger.error(e, exc_info=True)
            return None

    def update_status(self, status):
        """
        Updates the status of the template and file after packs are generated from it.

        Args:
            status (int): The status to be updated after packs are generated
        Returns:
            json : success or failure

        Examples:
            >>> GeneratePack().update_status(1)
                True
        """
        update_dict = {"status": settings.DONE_TEMPLATE_STATUS}
        if self.autoprocess_template:
            update_dict.update({"with_autoprocess": self.autoprocess_template})

        status = update_template_status_with_template_id(template_id=self.template_id, update_dict=update_dict)
        if not status:
            logger.error("Couldn't update template status for file_id {} and patient_id {}".format(self.file_id,
                                                                                                   self.patient_id))
            raise PackGenerationException('Template Already Processed.')

    def create_rx_file_csv(self, delimiter=','):
        """
        Writes to temporary csv file and returns data of that file.

        :param delimiter: delimiter for csv file
        :return: bytes
        """
        rx_file = StringIO()
        writer = csv.writer(rx_file, delimiter=delimiter, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line in self.rx_file_data:
            line = flatten(line)
            writer.writerow(line)
        data = rx_file.getvalue()
        return bytes(data, encoding="utf-8")

    def prepare_data(self):
        try:
            logger.info("In GeneratePacks prepare_data")
            self.get_patient_no(self.patient_id)
            is_modified_value = template_get_status_dao(self.file_id, self.patient_id)
            pack_type, customization_flag, is_sppd, is_true_unit, is_bubble = get_template_flags(file_id=self.file_id,
                                                                                      patient_id=self.patient_id)
            self.pack_type = pack_type
            self.is_bubble = is_bubble
            if is_modified_value in [1, 2] or ((is_modified_value == 0) and (
                    pack_type == constants.UNIT_DOSE_PER_PACK or customization_flag or is_true_unit or is_sppd)):
                saveable_template_file_id = get_template_file_id_dao(self.patient_id,
                                                                     settings.PENDING_PROGRESS_TEMPLATE_LIST)
                if not saveable_template_file_id == int(self.file_id):
                    raise ValueError(error(5001))
                # save data if no pending template is present other then the current one
                logger.info('in saving')
                self.template_data, self.is_customized, self.dummy_template = save_template_details(self.patient_id, self.file_id, self.company_id, self.user_id,
                                                           is_modified_value, False)
                logger.info('out saving')
            self.validate_template_status()
            logger.info('before get_data')
            self.get_data()
            logger.info('after save data')
            self.date_handling_for_fill_strategy(is_bubble=is_bubble)
            logger.info('2')
            # pack generation logic is different for multiple version
            # version = 1 --> unique column numbers will be considered from template
            # i.e. column_number 1,5,9,13 results into one pack for 7 day prescription
            # version = 2 --> all column numbers will be considered from template
            # i.e. column_number 1,5,9,13 results into four pack for 7 day prescription
            # as we will consider 1-4 for 1st pack, 5-8 for 2nd pack and so on.
            if self.is_customized:
                fill_dates = self.fill_dates_df
            else:
                fill_dates = self.fill_dates
            if self.version == 1:
                self.create_empty_pack(fill_dates, list(self.unique_template_columns))
                if self.takeaway_max_column_number:
                    self.create_empty_takeaway_pack(self.takeaway_fill_dates, list(self.takeaway_ref_column_numbers))
            else:
                self.create_empty_pack(fill_dates, list(range(1, self.max_column_number + 1)))
                if self.takeaway_max_column_number:
                    self.create_empty_takeaway_pack(self.takeaway_fill_dates, list(range(1, self.takeaway_max_column_number + 1)))
            logger.info('3')
            self.populate_pack()
            self.split_pack(self.pack_df, is_bubble=is_bubble)  # split regular packs
            if self.takeaway_df is not None and not self.takeaway_df.dropna(how='all').empty:
                self.split_pack(self.takeaway_df, is_takeaway=True)  # split takeaway packs
            logger.info('4')
            self.prepare_data_done = True
        except PackGenerationException as e:
            logger.debug("Error while preparing data of pack")
            logger.error(e)
            raise PackGenerationException(e)
        except TemplateException as e:
            logger.error(e)
            raise TemplateException(e)
        except Exception as e:
            raise

    # def update_unit_dosage_packs(self):
    #     try:
    #         volume_config = CompanySetting.db_get_template_split_settings(self.company_id)
    #         slot_volume_threshold = int(volume_config.get(CompanySetting.SLOT_VOLUME_THRESHOLD_MARK))
    #
    #         sub_q = PackDetails.select(PackDetails.id.alias('pack_id'),
    #                                    SlotHeader.id.alias('slot_header_id'),
    #                                    fn.SUM(SlotDetails.quantity),
    #                                    fn.IF(fn.SUM(SlotDetails.quantity)==1,1,fn.IF(fn.COUNT(fn.DISTINCT(fn.CONCAT(DrugMaster.formatted_ndc,'##',DrugMaster.txr)))==1,fn.IF(fn.ROUND(DrugDimension.width,DrugDimension.depth,DrugDimension.length).is_null(False),fn.IF(fn.ROUND(DrugDimension.width,DrugDimension.depth,DrugDimension.length)*fn.SUM(SlotDetails.quantity) <= settings.UNIT_DOSAGE_SLOT_VOLUME*slot_volume_threshold,1,0),fn.IF(settings.DEFAULT_PILL_VOLUME*fn.SUM(SlotDetails.quantity)<=settings.UNIT_DOSAGE_SLOT_VOLUME,1,0)),0)).alias('unit_dosage_slot'))\
    #             .join(SlotHeader, on=SlotHeader.pack_id == PackDetails.id)\
    #             .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id)\
    #             .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)\
    #             .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id)\
    #             .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id)\
    #             .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)&(UniqueDrug.txr == DrugMaster.txr)))\
    #             .join(DrugDimension,JOIN_LEFT_OUTER,on=DrugDimension.unique_drug_id == UniqueDrug.id)\
    #             .where(PackDetails.id << self.pack_details_ids)\
    #             .group_by(SlotHeader.id)\
    #             .order_by(PackDetails.id).alias('sub_q')
    #
    #         query = PackDetails.select(sub_q.c.pack_id,
    #                                    fn.IF(fn.COUNT(sub_q.c.slot_header_id)==fn.SUM(sub_q.c.unit_dosage_slot)),1,0).alias('is_unit_dosage')\
    #             .join(sub_q, on=sub_q.c.pack_id == PackDetails.id)\
    #             .group_by(sub_q.c.pack_id)
    #
    #         pack_ids = []
    #         seq_tuples = []
    #         for record in query.dicts():
    #             pack_ids.append(record['pack_id'])
    #             seq_tuples.append((record['pack_id'],record['is_unit_dosage']))
    #
    #         status = PackDetails.update().where(PackDetails.id << pack_ids).execute()
    #
    #
    #
    #     except (InternalError,IntegrityError) as e:
    #         logger.error(e)
    #         return e

    def start_pack_generation(self, pack_ids_dict):
        """ Start the pack generation process and keep track of all the stages during the pack generation cycle.
        """
        logger.info(threading.currentThread().getName() + ' persist_data Starting Pack Generation')
        try:
            with db.transaction():
                # self.get_pharmacy_pack_id(self.pharmacy_fill_id)  # commenting for bulk pack ids
                logger.info('5')
                self.persist_base_pack(len(self.generated_packs))
                logger.info('6')

                self.persist_data(self.generated_packs, pack_ids_dict)
                # self.update_unit_dosage_packs()

                logger.info('7')

                self.update_status(settings.SUCCESS)
                logger.info('8')

                self.combined_api.append({
                    'api_name': settings.PHARMACY_SLOT_STORE_URL.split('/')[2],
                    'api_args': {"file": ",".join(self.slot_files), 'token': self.company_settings["IPS_COMM_TOKEN"]}
                })
                rx_file_content = self.create_rx_file_csv()

                logger.info('rx_file_content' + str(rx_file_content))

                rx_file_data = self.get_file_data_b64encoded(file_content=rx_file_content)
                self.combined_api.append({
                    'api_name': settings.PHARMACY_STORE_RX_FILE_URL.split('/')[2],
                    'api_args': {"batchid": str(self.pharmacy_fill_id), "file": str(self.pharmacy_fill_id) + ".csv",
                                 "note": rx_file_data, 'token': self.company_settings["IPS_COMM_TOKEN"]}
                })

                logger.debug(threading.currentThread().getName() + " Beginning IPS Communication")
                self.call_combined_apis()
                logger.info('9')
            with db.transaction():
                logger.info(f"set pack type: multi or unit dose")
                set_unit_dosage_flag(self.company_id, self.pack_details_ids)

        except IOError as e:
            raise IOError(e)
        except PackGenerationException as e:
            raise PackGenerationException(e)
        except PharmacyRxFileGenerationException as e:
            raise PharmacyRxFileGenerationException(e)
        except PharmacySlotFileGenerationException as e:
            raise PharmacySlotFileGenerationException(e)
        except PharmacySoftwareResponseException as e:
            raise PharmacySoftwareResponseException(e)
        except PharmacySoftwareCommunicationException as e:
            raise PharmacySoftwareCommunicationException(e)
        except Exception as e:  # Default Error
            logger.info(e)
            raise PackGenerationException('Pack generation failed.')

        logger.debug(threading.currentThread().getName() + 'Exiting Pack Generation')

    @staticmethod
    def create_csv_file(data, filepath, filename, delimiter, headers=None):
        """
        Takes a file data and creates a csv file from it.

        Args:
            data (list): The data to be converted to the csv file
            filepath (str): The path at which the csv file is to be created
            filename (str): The name of the csv file to be created
            delimiter (str): The delimiter to be introduced while creating csv files.
        Returns:
            None

        Examples:
            >>> GeneratePack().create_csv_file([], '/storage', 'file', ',')
                True
        """
        try:
            os.makedirs(filepath)
        except FileExistsError:
            # directory already exist
            pass

        filename = os.path.join(filepath, filename)
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter,
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

            if headers:
                writer.writerow(headers)
            for record in data:
                output = flatten(record)
                writer.writerow(output)

    def send(self, pharmacy_fill_id, slot_files, rx_file_handler, slot_file_handler, batchlist=None,
             finalize_template_handler=None, data=None):
        """
        Makes the call to the IPS web services asynchronously
        """
        if not self.DISABLE_IPS_COMMUNICATION:
            if rx_file_handler:
                send_data(self.company_settings["BASE_URL_IPS"], settings.PHARMACY_STORE_RX_FILE_URL,
                          {"batchid": pharmacy_fill_id, "file": str(pharmacy_fill_id) + ".csv",
                           "note": data, 'token': self.company_settings["IPS_COMM_TOKEN"]}, 0,
                          response_handler=rx_file_handler, token=self.company_settings["IPS_COMM_TOKEN"])
            if slot_file_handler:
                send_data(self.company_settings["BASE_URL_IPS"], settings.PHARMACY_SLOT_STORE_URL,
                          {"file": ",".join(slot_files), 'token': self.company_settings["IPS_COMM_TOKEN"]}, 0,
                          response_handler=slot_file_handler, token=self.company_settings["IPS_COMM_TOKEN"],
                          timeout=self._TIMEOUT)
            if finalize_template_handler and batchlist:
                send_data(self.company_settings["BASE_URL_IPS"], settings.PHARMACY_FINALIZE_PACK_URL,
                          {"batchlist": ",".join(batchlist), 'token': self.company_settings["IPS_COMM_TOKEN"]}, 0,
                          response_handler=finalize_template_handler, token=self.company_settings["IPS_COMM_TOKEN"])

    def call_combined_apis(self):
        """Calls combined api webservice call"""
        try:
            send_data(self.company_settings['BASE_URL_IPS'], settings.PHARMACY_COMBINED_APIS,
                      json.dumps(self.combined_api), 0, response_handler=self.combined_api_handler,
                      token=self.company_settings['IPS_COMM_TOKEN'], timeout=None, request_type="POST")
        except PharmacySoftwareCommunicationException as e:
            logger.info(e)
            raise PharmacySoftwareCommunicationException("Couldn't store pack(s) data in Pharmacy Software."
                                                         " Kindly contact support.")

    @staticmethod
    def combined_api_handler(data):
        """Checks if all response are valid"""
        data = data['data']
        for item in data:
            if not is_response_valid(item['api_response']):
                if item['api_response']['response']['errormessage'] == settings.IPS_DELETED_BASE_PACK_MESSAGE:
                    raise PharmacySoftwareResponseException('The file/patient details associated with the template has '
                                                            'been deleted in the pharmacy software. Kindly rollback '
                                                            'and proceed further.')
                raise PharmacySoftwareResponseException('Error in storing pack(s) data in Pharmacy Software.'
                                                        ' Kindly contact support.')


def flatten(x):
    """
        Takes a list which has int and iterables and returns one flattened list.
    """
    output = []
    for item in x:
        if isinstance(item, list):
            [output.append(y) for y in item]
        else:
            output.append(item)

    return output


def remove_dirs(system_id):
    rx_file_path = os.path.join(settings.PHARMACY_RX_FILE_PATH, str(system_id))
    slot_file_path = os.path.join(settings.PHARMACY_SLOT_FILE_PATH, str(system_id))
    for directory in [rx_file_path, slot_file_path]:
        remove_dir(directory)


@log_args_and_response
def set_unit_dosage_flag(company_id, pack_list):
    """
    This function sets flag for unit dosage packs by slot_volume_threshold and logic binded in
    update_unit_dosage_flag function.
    """
    try:
        volume_config = db_get_template_split_settings_dao(company_id=company_id)
        slot_volume_threshold = int(volume_config.get(constants.SLOT_VOLUME_THRESHOLD_MARK))
        status = update_unit_dosage_flag(slot_volume_threshold=slot_volume_threshold, pack_list=pack_list)
        return status
    except (InternalError, IntegrityError) as e:
        logger.info(e)
        return e


@log_args_and_response
def set_unit_pack_for_multi_dosage(company_id, pack_list):
    """
    This function sets flag for multi dosage in unit packs if unit packs are available
    """
    try:
        volume_config = db_get_template_split_settings_dao(company_id=company_id)
        slot_volume_threshold = float(volume_config.get(constants.SLOT_VOLUME_THRESHOLD_MARK))
        status = update_unit_pack_for_multi_dosage_flag(slot_volume_threshold=slot_volume_threshold, pack_list=pack_list)
        return status
    except (InternalError, IntegrityError) as e:
        logger.info(e)
        return e

def remove_present_file(_file):
    """ Removes file if already present Ignores Otherwise

    :param _file:
    :return:
    """
    try:
        os.remove(_file)
    except OSError:
        pass  # No file present, So proceed


def make_success_response():
    return create_response(settings.SUCCESS)


@log_args_and_response
def db_process_new_packs_change_rx(old_packs_dict, ext_change_rx_data, company_id, user_id,
                                   transfer_to_manual_fill_system, token):
    update_pack_dict: Dict[str, Any] = {}
    update_pack_order_dict: Dict[str, Any] = {}
    ext_pharmacy_fill_ids: List[int] = []
    pack_orders: List[int] = []
    update_other_packs_order_no: bool = False
    pack_difference: int = 0
    update_pack_list: list = list()
    old_pack_length: int = 0
    new_pack_length: int = 0
    batch_imported: bool = False
    current_template: list = ext_change_rx_data['current_template']
    skip_template_dict: list = []
    try:
        with db.transaction():
            if len(current_template) > 1:
                logger.info("In db_process_new_packs_change_rx: multiple_template_found")
                current_template,  skip_template_dict = process_multiple_old_template_change_rx(current_template)

            if old_packs_dict["delete_old_packs"]:
                old_packs_dict["process_old_packs"] = False

            if not old_packs_dict["process_old_packs"]:
                logger.debug("Fetch the Details of Old and New Packs based on their Template Info...")
                new_pack_query = db_get_new_pack_details_for_template(template_id=ext_change_rx_data["new_template"])
                new_pack_list = [pack["id"] for pack in new_pack_query]

                old_pack_query = db_get_ext_and_pack_details_for_template(template_ids=
                                                                          current_template)
                old_pack_list = [pack["id"] for pack in old_pack_query]
                delivered_packs_set = set(record["packs_delivered"] for record in old_pack_query if record["packs_delivered"])
                delivered_packs = ast.literal_eval(delivered_packs_set.pop()) if delivered_packs_set else []

                logger.debug("Old Packs List: {}".format(old_pack_list))
                logger.debug("New Packs List: {}".format(new_pack_list))
                if delivered_packs:
                    logger.debug("Old Delivered Packs List: {}".format(delivered_packs))
                    # removing delivered packs to not to change its status
                    old_pack_list = [pack for pack in old_pack_list if pack not in delivered_packs]

                # Handling of association of Batch ID or Facility Distribution ID or canister Recommendation, for
                # new packs needs to be done only when processing happens through DosePacker system.
                if not transfer_to_manual_fill_system:
                    if old_packs_dict["facility_dis_id"]:
                        logger.debug("Update Facility Distribution ID: {} for packs generated with "
                                     "New Template ID: {}".format(old_packs_dict["facility_dis_id"],
                                                                  ext_change_rx_data["new_template"]))
                        update_pack_dict = {"facility_dis_id": old_packs_dict["facility_dis_id"]}
                    else:
                        logger.debug("Facility Distribution ID is not associated with Old Packs...")

                    if old_packs_dict["batch_id"]:
                        logger.debug("Associate Batch ID: {} for packs generated with New Template ID: {}"
                                     .format(old_packs_dict["batch_id"], ext_change_rx_data["new_template"]))
                        update_pack_dict.update({"batch_id": old_packs_dict["batch_id"]})

                        if old_packs_dict["system_id"]:
                            update_pack_dict.update({"system_id": old_packs_dict["system_id"]})

                        new_pack_list = get_ordered_pack_list(new_pack_list)

                        batch_status = get_batch_status(batch_id=old_packs_dict["batch_id"])
                        if batch_status == settings.BATCH_IMPORTED or old_packs_dict["pack_queue"]:
                            logger.debug("Check the Pack count among Old and New Templates")

                            old_pack_order_no_map = {pack["id"]: pack["order_no"] for pack in old_pack_query}
                            logger.debug("Old Pack-Order No mapping: {}".format(old_pack_order_no_map))

                            old_pack_length = len(old_pack_list)
                            new_pack_length = len(new_pack_list)
                            logger.debug("Old Packs Length: {}, New Packs Length: {}"
                                         .format(old_pack_length, new_pack_length))

                            batch_imported = True
                            if old_pack_length >= new_pack_length:
                                for index, pack in enumerate(old_pack_list):
                                    if index > new_pack_length - 1:
                                        break
                                    else:
                                        pack_orders.append(old_pack_order_no_map[pack])
                            else:
                                pack_difference = new_pack_length - old_pack_length
                                for index, pack in enumerate(old_pack_list):
                                    pack_orders.append(old_pack_order_no_map[pack])

                                if pack_orders:
                                    last_order_number = pack_orders[-1]

                                update_pack_list = db_get_pack_list_by_order_number(order_no=last_order_number,
                                                                                    batch_id=old_packs_dict["batch_id"])
                                update_pack_list = list(set(update_pack_list) - set(new_pack_list))
                                if update_pack_list:
                                    update_pack_list = get_ordered_pack_list(update_pack_list)

                                for remaining_value in range(pack_difference):
                                    if pack_orders:
                                        pack_orders.append(pack_orders[-1] + 1)
                                        update_other_packs_order_no = True
                        else:
                            _max_order_no = db_max_order_no_dao(old_packs_dict["system_id"])
                            pack_orders = [_max_order_no + index + 1 for index, item in enumerate(new_pack_list)]

                        update_pack_order_dict = {"pack_orders": pack_orders,
                                                  "system_id": old_packs_dict["system_id"],
                                                  "update_other_packs_order_no": update_other_packs_order_no,
                                                  "update_pack_list": update_pack_list,
                                                  "pack_difference": pack_difference
                                                  }

                    logger.debug("Update Pack Dictionary: {}".format(update_pack_dict))
                    if update_pack_dict:
                        update_status = \
                            db_update_pack_details_by_template_dao(update_pack_dict=update_pack_dict,
                                                                   pack_list=new_pack_list,
                                                                   update_pack_order_dict=update_pack_order_dict)

                        if old_packs_dict["cr_recommendation_check"]:
                            logger.debug("Perform Canister Recommendation again for packs with New Template..")
                            pack_max_drop_number = execute_recommendation_for_new_pack_after_change_rx(
                                new_pack_list=new_pack_list,
                                old_pack_list=old_pack_list,
                                company_id=company_id,
                                batch_id=old_packs_dict["batch_id"])

                            if list(pack_max_drop_number.keys()) != new_pack_list:
                                # some/all new packs have not canister drug or canister not available >> send all new packs to manual.
                                status = update_pack_details_and_insert_in_pack_user_map(pack_list = new_pack_list)
                                logger.info(f"In db_process_new_packs_change_rx, status: {status}")
                            else:
                                # if old packs are in pack queue >> insert new packs in pack queue
                                in_pack_queue = check_packs_in_pack_queue_or_not(old_pack_list)
                                if in_pack_queue:
                                    pack_queue_insert = insert_packs_to_pack_queue(new_pack_list)

                            # remove old packs from pack queue
                            remove_pack_queue_pack = remove_pack_from_pack_queue(old_pack_list)
                            # todo need to handle mfd of old packs >> right now mfd of all packs will skipped

                        #      todo need to update drop number for MFD

                        if old_packs_dict["mfd_recommendation_check"] and ext_change_rx_data:
                            logger.debug("Map the MFD recommendation of Old Packs with New Packs...")
                            delete_old_packs_after_mfd_map = \
                                db_check_and_update_mfd_recommendation_mapping(
                                    batch_id=old_packs_dict["batch_id"],
                                    old_template_id=current_template[0],
                                    new_template_id=ext_change_rx_data["new_template"])

                            mfd_drop_no_status = update_drop_number_for_new_packs(new_pack_list=new_pack_list,
                                                                                  pack_max_drop_number=pack_max_drop_number)

                            # TODO: No need to delete at this stage the old packs, because we are anyways calling
                            #  set_status at a later stage in this function.
                            # if delete_old_packs_after_mfd_map:
                            #     logger.debug("Delete the old packs for Old template ID if not already deleted.")
                            #
                            #     ext_pharmacy_fill_ids = \
                            #         db_get_pharmacy_fill_id_by_ext_id_dao(ext_change_rx_id=
                            #                                               ext_change_rx_data["ext_change_rx_id"]
                            #                                               )
                            #
                            #     ext_pack_details_dict = {"pack_display_ids": ext_pharmacy_fill_ids,
                            #                              "technician_fill_status":
                            #                                  constants.EXT_PACK_STATUS_CODE_DELETED,
                            #                              "technician_user_name": ips_user_name,
                            #                              "technician_fill_comment":
                            #                                  constants.DELETE_REASON_EXT_CHANGE_RX,
                            #                              "user_id": user_id,
                            #                              "company_id": company_id,
                            #                              "change_rx": True,
                            #                              "ext_change_rx_id":
                            #                                  ext_change_rx_data["ext_change_rx_id"]}
                            #     response_dict = json.loads(update_ext_pack_status(ext_pack_details_dict))
                            #     status_code = response_dict.get("code",
                            #                                     constants.ERROR_CODE_CONNECTION_ISSUE_WHILE_FILE_SAVING)
                            #     if status_code != constants.IPS_STATUS_CODE_OK:
                            #         logger.debug(
                            #             "Issue with processing delete operation for Pack Display ID: {}. "
                            #             "Received Status = {}".format(ext_pharmacy_fill_ids, status_code))
                            #         raise AutoProcessTemplateException
                        else:
                            update_status = \
                                db_update_pack_details_by_template_dao(update_pack_dict=update_pack_dict,
                                                                       pack_list=new_pack_list,
                                                                       update_pack_order_dict=update_pack_order_dict)
                    # pack_query = db_get_ext_and_pack_details_for_template(template_id=
                    #                                                   ext_change_rx_data["current_template"])
                    # pack_ids = [pack["id"] for pack in pack_query]

                # Prepare dictionary to perform old packs deletion when new packs have arrived for processing
                args = {"company_id": company_id, "user_id": user_id, "status": settings.DELETED_PACK_STATUS,
                        "pack_id": old_pack_list, "status_changed_from_ips": True,
                        "reason": constants.DELETE_PACK_DESC_FOR_OLD_PACKS_CHANGE_RX, "change_rx": True,
                        "change_rx_token": token, "delete_all_packs": True}
                response = json.loads(set_status(args))
                logger.debug("set_status response: {}".format(response))

                if old_packs_dict["batch_id"]:
                    if batch_imported:
                        logger.debug("Update the Pack Queue uuid for Auto-refresh...")
                        update_couch_db_batch_distribution_status(company_id=company_id,
                                                                  refresh_screen=constants.REFRESH_PACK_QUEUE)
                    else:
                        logger.debug("Update the Pack Pre-Processing wizard timestamp...")
                        system_id = get_system_id_based_on_device_type(company_id=company_id,
                                                                       device_type_id=settings.DEVICE_TYPES["ROBOT"])
                        args = {"system_id": system_id, "change_rx": True}
                        update_timestamp_couch_db_pre_processing_wizard(args)
                else:
                    logger.debug("Update the Batch Distribution uuid for Auto-refresh...")
                    update_couch_db_batch_distribution_status(company_id=company_id,
                                                              refresh_screen=constants.REFRESH_BATCH_DISTRIBUTION)
            else:
                logger.debug("Continue processing Old Packs and Transfer New Packs to Manual Fill Flow...")

            # This block was written as we were assuming that mid cycle and next cycle pack will come together
            # as one template. But now this has to be removed as ips is sending 2 template in this case

            # if skip_template_dict:
            #     direct_delete_template = skip_template_dict['direct_delete_template']
            #     for template in direct_delete_template:
            #         pack_data = db_get_ext_and_pack_details_for_template(template_ids=
            #                                                               [template])
            #         old_pack_list = [pack["id"] for pack in pack_data]
            #         delivered_packs_set = set(
            #             record["packs_delivered"] for record in pack_data if record["packs_delivered"])
            #         delivered_packs = ast.literal_eval(delivered_packs_set.pop()) if delivered_packs_set else []
            #
            #         logger.debug("skip_template_dict: Old Packs List: {}".format(old_pack_list))
            #         if delivered_packs:
            #             logger.debug("skip_template_dict: Old Delivered Packs List: {}".format(delivered_packs))
            #             # removing delivered packs to not to change its status
            #             old_pack_list = [pack for pack in old_pack_list if pack not in delivered_packs]
            #         args = {"company_id": company_id, "user_id": user_id, "status": settings.DELETED_PACK_STATUS,
            #                 "pack_id": old_pack_list, "status_changed_from_ips": True,
            #                 "reason": constants.DELETE_PACK_DESC_FOR_OLD_PACKS_CHANGE_RX, "change_rx": True,
            #                 "change_rx_token": token, "delete_all_packs": True}
            #         response = json.loads(set_status(args))
            #         logger.debug("set_status response: {}".format(response))

            if transfer_to_manual_fill_system:
                update_notifications_couch_db_status(old_pharmacy_fill_id=[],
                                                     company_id=company_id, file_id=0,
                                                     old_template_id=current_template[0],
                                                     new_template_id=ext_change_rx_data["new_template"],
                                                     autoprocess_template_flag=True,
                                                     new_pack_ids=[], remove_action=False)

    except (IntegrityError, InternalError, DataError, AutoProcessTemplateException, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException


@log_args_and_response
def db_manual_template_process_change_rx(file_id: int, patient_id: int, company_id: int):
    ext_change_rx_data: Dict[str, Any] = {}
    old_packs_dict: Dict[str, Any] = {}
    transfer_to_manual_fill_system: bool = False
    new_template_dict: Dict[str, Any] = {}

    try:
        new_template_dict = get_template_id_dao(file_id=file_id, patient_id=patient_id)
        if new_template_dict:
            ext_change_rx_data = db_get_ext_change_rx_record(old_pharmacy_fill_id=[],
                                                             template_id=new_template_dict["id"],
                                                             company_id=company_id)
            if ext_change_rx_data:
                current_template_id = ext_change_rx_data["current_template"]
                logger.debug("Identify if the Old Packs are In Progress/Done/Manual or if they are "
                             "pending then verify the batch status and recommendation..")
                old_packs_dict = db_check_old_packs_status_for_new_template_process(
                    old_template_id=current_template_id, new_template_id=new_template_dict["id"])

                if old_packs_dict["process_old_packs"]:
                    transfer_to_manual_fill_system = True

        return ext_change_rx_data, old_packs_dict, transfer_to_manual_fill_system
    except (IntegrityError, InternalError, DataError, AutoProcessTemplateException, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException


@log_args_and_response
@validate(required_fields=["data", "company_id", "user_id", "time_zone"])
def generate(dict_info):
    """
    Takes the input argument of file ids and patient ids and generates pack from it.

    Args:
        dict_info (dict): A dict containing file ids and patient ids associated with it in data key, system_id and user_id.
    Returns:
        json: If the pack generation process is successful or not.

    Examples:
        >>> generate({})

    """
    logger.info("Input args of pack generation {}".format(dict_info))
    global current_user_id
    # settings.ACCESS_TOKEN = cherrypy.request.headers.get("Authorization")
    time_zone = dict_info['time_zone']
    user_id = int(dict_info["user_id"])

    # to stop continue processing, if the min admin start date of the template to be processed is lesser that current date
    # we will stop the template to process and hold it at DDT until it is scheduled
    if settings.ALLOW_UNSCHEDULED_TEMPLATE_PROCESS:
        status = db_compare_min_admin_date_with_current_date(patient_id=list(dict_info["data"].values())[0][0],
                                                             file_id=list(dict_info["data"].keys())[0], current_date=get_current_date())
        if status == settings.FAILURE_RESPONSE:
            return error(21017)
        if status != settings.SUCCESS_RESPONSE:
            status_prev_schedule = db_setting_previous_facility_schedule_for_new_patient(
                patient_id=list(dict_info["data"].values())[0][0], user_id=user_id, start_date=status)
            if not status_prev_schedule:
                return error(21017)

    logger.debug(threading.currentThread().getName() + "Data Received For Pack Generation: " + str(dict_info))
    order_no, pack_plate_location = None, None
    company_id = int(dict_info["company_id"])
    # canister_drug_id_set = CanisterMaster.db_get_drug_ids(company_id)
    canister_drug_id_set = db_get_canister_drug_ids(company_id=company_id)
    try:
        company_settings = get_company_setting_by_company_id(company_id=company_id)
        required_settings = settings.PACK_GENERATION_REQUIRED_SETTINGS
        settings_present = all([key in company_settings for key in required_settings])
        if not settings_present:
            return error(6001)
    except InternalError:
        return error(2001)

    # if "system_id" in dict_info:
    #     system_id = dict_info['system_id']
    # else:
    #     system_id = None

    autoprocess_template = dict_info.get("autoprocess_template", 0)
    access_token = dict_info.get("access_token", "")

    current_user_id = user_id
    transfer_to_manual_fill_system = dict_info.get('transfer_to_manual_fill_system', False)
    if not transfer_to_manual_fill_system:
        # over writing transfer to manual flag with env variable
        transfer_to_manual_fill_system = settings.TRANSFER_TO_MANUAL
    assigned_to = None

    old_packs_dict = dict_info.get("old_packs_dict", {})
    ext_change_rx_data = dict_info.get("ext_change_rx_data", {})
    ips_user_name = dict_info.get("ext_change_rx_data", "")

    # Store the original value of transfer_to_manual_fill_system flag
    # This will help to handle processing of multiple templates together from DDT
    transfer_to_manual_fill_system_main = transfer_to_manual_fill_system

    if transfer_to_manual_fill_system:
        assigned_to = user_id
        system_id = dict_info.get('system_id', None)
        dict_info.get('system_id', None)
    else:
        system_id = None
    if not settings.USE_CONVEYOR:
        # order_no = PackDetails.db_max_order_no(company_id)
        # commenting as it is not returning correct value.
        order_no = 0
        pack_plate_location = cycle(settings.PACK_PLATE_LOCATION)
    gen_pack_list = dict_info["data"]
    if "version" in dict_info:
        version = int(dict_info["version"])
    else:
        version = 1

    if not autoprocess_template:
        token = cherrypy.request.headers.get("Authorization", None)
        token = token.split()[1]
    else:
        token = access_token

    if settings.USE_TASK_QUEUE:
        logger.info("USE_TASK_QUEUE of pack generation {}".format(settings.USE_TASK_QUEUE))

        exceptions_list = list()
        th_list = list()
        success_patient_ids = list()
        failure_patient_ids = list()
        try:
            for item in gen_pack_list:
                file_id = item
                patient_ids = list(set(gen_pack_list[item]))
                for patient_id in patient_ids:

                    logger.debug("Auto-Process Template: {}".format(autoprocess_template))
                    if not autoprocess_template:
                        ext_change_rx_data, old_packs_dict, transfer_to_manual_fill_system = \
                            db_manual_template_process_change_rx(file_id=file_id, patient_id=patient_id,
                                                                 company_id=company_id)
                        if transfer_to_manual_fill_system_main:
                            transfer_to_manual_fill_system = transfer_to_manual_fill_system_main

                    success_patient_ids.append(patient_id)
                    # template_data = TemplateMaster.select().dicts()\
                    #     .where(TemplateMaster.file_id == file_id, TemplateMaster.patient_id == patient_id).get()
                    template_data = db_get_template_master_by_patient_and_file_dao(patient_id=patient_id,
                                                                                   file_id=file_id)
                    template_id = template_data['id']
                    gen_pack = GeneratePack(
                        file_id, patient_id, user_id, order_no, pack_plate_location,
                        canister_drug_id_set, company_id, company_settings,
                        2, version, time_zone=time_zone,
                        transfer_to_manual_fill_system=transfer_to_manual_fill_system, assigned_to=assigned_to,
                        system_id=system_id, template_id=template_id, token=token,
                        autoprocess_template=autoprocess_template
                    )
                    gen_pack.initialize_auto_process_template_parameters(old_packs_dict=old_packs_dict,
                                                                         ext_change_rx_data=ext_change_rx_data,
                                                                         ips_user_name=ips_user_name)

                    t = ExcThread(
                        exceptions_list,
                        name='Thread-FileID-{}PatientID#{}'.format(file_id, patient_id),
                        target=gen_pack.add_task,
                    )
                    th_list.append(t)
                    t.start()
            [th.join() for th in th_list]
            if not exceptions_list:
                try:
                    update_pending_template_data_in_redisdb(company_id)
                except (RedisConnectionException, Exception):
                    pass
                logger.info('Add_count_couch_db: {}'.format(len(success_patient_ids)))
                status, _ = update_queue_count(settings.CONST_TEMPLATE_MASTER_DOC_ID, len(success_patient_ids), None,
                                               company_id,
                                               operation=settings.TASK_OPERATION['Add'], update_timestamp=True,
                                               raise_exc=True)
                if not status:
                    logger.error('Error in updating couch-db doc')
                    raise RealTimeDBException

                data = {"data": [], "more_info": [],
                        "patient_ids": list(set(success_patient_ids)), "pack_ids": []}
                return create_response(data)
            else:
                display_list = []
                error_message_patient_dict = set()
                for item in exceptions_list:
                    try:
                        patient_id = (str(item)[1:-1].split(':')[0])[1:-1].split('#')[1]
                        patient_id = int(patient_id)
                    except (ValueError, AttributeError, SyntaxError, TypeError):
                        patient_id = None
                    try:
                        patient = db_get_patient_info_by_patient_id_dao(patient_id=patient_id)
                        patient_name = patient.last_name + ", " + patient.first_name
                    except (InternalError, DoesNotExist):
                        patient_name = None
                    try:
                        msg = str(item)[1:-1].split("'")[3]
                    except ValueError:
                        msg = ''
                    print("msg: ", msg)

                    error_message_patient_dict.add(msg)
                    display_list.append(patient_name + ': ' + msg)
                    failure_patient_ids.append(patient_id)
                try:
                    update_pending_template_data_in_redisdb(company_id)
                except (RedisConnectionException, Exception) as e:
                    logger.info(e)
                    pass
                queue_count = len(success_patient_ids) - len(failure_patient_ids)
                logger.info('Add_count_couch_db: {}'.format(queue_count))
                status, _ = update_queue_count(settings.CONST_TEMPLATE_MASTER_DOC_ID,
                                               queue_count, None,
                                               company_id,
                                               operation=settings.TASK_OPERATION['Add'], update_timestamp=True,
                                               raise_exc=True)

                data = {"data": error_message_patient_dict, "more_info": error_message_patient_dict,
                        "patient_ids": list(set(success_patient_ids).difference(set(failure_patient_ids))),
                        "pack_ids": []}
                return create_response(data)
        except RealTimeDBException as e:
            return error(1001, 'Real time db not updated in template processing. DOCUMENT: " + document_name')
        except Exception as e:
            return error(1001)

    else:
        template_list = list()
        exceptions_list = []
        success_patient_ids = set()
        failure_patient_ids = set()
        pack_gen_instances = list()
        extra_pack_ids = dict()
        file_ids = list(gen_pack_list.keys())

        # valid_files = FileHeader.db_verify_filelist(file_ids, company_id)
        valid_files = db_verify_filelist_dao(file_ids=file_ids, company_id=company_id)
        if not valid_files:
            return error(1016)
        th_list = list()
        for item in gen_pack_list:
            file_id = item
            patient_ids = gen_pack_list[item]
            for patient_id in patient_ids:

                logger.debug("Auto-Process Template: {}".format(autoprocess_template))
                if not autoprocess_template:
                    ext_change_rx_data, old_packs_dict, transfer_to_manual_fill_system = \
                        db_manual_template_process_change_rx(file_id=file_id, patient_id=patient_id,
                                                             company_id=company_id)
                    if transfer_to_manual_fill_system_main:
                        transfer_to_manual_fill_system = transfer_to_manual_fill_system_main

                success_patient_ids.add(patient_id)
                template_id = TemplateMaster.get(file_id=file_id, patient_id=patient_id).id
                template_list.append((file_id, patient_id))
                try:
                    gen_pack = GeneratePack(
                        file_id, patient_id, user_id, order_no, pack_plate_location,
                        canister_drug_id_set, company_id, company_settings,
                        2, version, time_zone = time_zone,
                        transfer_to_manual_fill_system=transfer_to_manual_fill_system, assigned_to=assigned_to,
                        system_id=system_id, template_id=template_id, autoprocess_template=autoprocess_template
                    )
                    logger.info("Initializing Auto Process Template Paramaters")
                    gen_pack.initialize_auto_process_template_parameters(old_packs_dict=old_packs_dict,
                                                                         ext_change_rx_data=ext_change_rx_data,
                                                                         ips_user_name=ips_user_name)
                    t = ExcThread(
                        exceptions_list,
                        name='Thread-FileID-{}PatientID#{}'.format(file_id, patient_id),
                        target=gen_pack.prepare_data
                    )
                    th_list.append(t)
                    t.start()
                    pack_gen_instances.append(gen_pack)
                except Exception as e:
                    logger.error(e, exc_info=True)

        # wait for all the threads to join
        [th.join() for th in th_list]
        pack_ids_dict = defaultdict(list)
        try:
            bulk_pack_ids(pack_gen_instances, company_settings)
        except Exception as e:
            logger.error(e, exc_info=True)
            try:
                update_pending_template_data_in_redisdb(company_id)
            except (RedisConnectionException, Exception):
                pass
            display_list = ["All Patients: Couldn't get extra pack IDs from Pharmacy Software."]
            data = {"data": display_list, "more_info": display_list, "patient_ids": []}
            update_couch_db_pending_template_count(company_id=company_id)
            return create_response(data)

        # Limits processing of patients using batch.
        # It is to limit no. of web service requests to Pharmacy server, which will decrease load on Pharmacy server
        for items in batch(pack_gen_instances,
                           n=int(os.environ.get("PACK_GEN_BATCH_LIMIT", 4))):
            threads = list()
            for gen_pack in items:
                if not gen_pack.prepare_data_done:
                    continue  # if prepare data had error do not execute start_pack_generation
                try:
                    t = ExcThread(
                        exceptions_list,
                        name='Thread-FileID-{}PatientID#{}'.format(gen_pack.file_id,
                                                                   gen_pack.patient_id),
                        target=gen_pack.start_pack_generation, args=[pack_ids_dict]
                    )
                    threads.append(t)
                    t.start()
                except (PackGenerationException,
                        PharmacyRxFileGenerationException,
                        IOError,
                        PharmacySlotFileGenerationException) as e:
                    logger.error(e)
                    update_couch_db_pending_template_count(company_id=company_id)
                    return error(1001, e)

            # wait for all the threads to join
            [th.join() for th in threads]

            print(pack_ids_dict)
            pack_ids_list = [pack_id for pack_ids in list(pack_ids_dict.values()) for pack_id in pack_ids]

            # updating template screen in thread
            rtdb_th = ExcThread(
                [], target=real_time_db_timestamp_trigger,
                args=[settings.CONST_TEMPLATE_MASTER_DOC_ID, None, company_id]
            )
            rtdb_th.start()

        logger.debug("Exception List from thread: " + str(exceptions_list))
        success_patient_ids = success_patient_ids

        try:
            delivery_date_set = update_delivery_date({'update_existing': False,
                                                      'patient_ids': list(success_patient_ids),
                                                      'current_date': get_current_date()})
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            logger.info('Could not set delivery date')

        try:
            update_couch_db_pending_template_count(company_id=company_id)
        except Exception as e:
            logger.error(e, exc_info=True)
            pass

        if not exceptions_list:
            pack_ids_list = [pack_id for pack_ids in list(pack_ids_dict.values()) for pack_id in pack_ids]

            status = set_unit_dosage_flag(company_id, pack_ids_list)
            print(pack_ids_list)
            # if settings.CONSIDER_UNIT_DOSAGE:
            #     status = set_unit_pack_for_multi_dosage(company_id, pack_ids_list)
            if transfer_to_manual_fill_system and pack_ids_list:
                db_max_assign_order_no_manual_packs(company_id, pack_ids_list)
                db_update_rx_changed_packs_manual_count(company_id)

            try:
                if old_packs_dict and ext_change_rx_data:
                    logger.debug("Check if there is any change in drug information as compared to old packs..")
                    update_slot_drug_status = \
                        db_update_slot_details_drug_with_old_packs(update_drug_dict=old_packs_dict["slot_drug_update"],
                                                                   ext_change_rx_data=ext_change_rx_data,
                                                                   user_id=user_id)
            except (IntegrityError, InternalError, Exception) as e:
                logger.error(e, exc_info=True)
                logger.info('Could not process the check and update for Slot Drugs.')

            try:
                if old_packs_dict and ext_change_rx_data:
                    db_process_new_packs_change_rx(old_packs_dict=old_packs_dict, ext_change_rx_data=ext_change_rx_data,
                                                   company_id=company_id, user_id=user_id,
                                                   transfer_to_manual_fill_system=transfer_to_manual_fill_system,
                                                   token=token)
            except (IntegrityError, InternalError, Exception) as e:
                logger.error(e, exc_info=True)
                logger.info('Could not process the new packs linked due to Change Rx.')

            for item in gen_pack_list:
                file_id = item
                patient_ids = list(set(gen_pack_list[item]))
                for patient_id in patient_ids:
                    update_notifications_couch_db_green_status(file_id=file_id, patient_id=patient_id,
                                                               company_id=company_id)

            try:
                update_pending_template_data_in_redisdb(company_id)
            except (RedisConnectionException, Exception):
                pass
            data = {"data": [], "more_info": [],
                    "patient_ids": list(success_patient_ids), "pack_ids": pack_ids_list}
            return create_response(data)
        else:
            logger.error("Exception During PackProcessing" + str(exceptions_list))
            display_list = []
            for item in exceptions_list:
                try:
                    patient_id = (str(item)[1:-1].split(':')[0])[1:-1].split('#')[1]
                    patient_id = int(patient_id)
                except (ValueError, AttributeError, SyntaxError, TypeError):
                    patient_id = None
                try:
                    patient = db_get_patient_info_by_patient_id_dao(patient_id=patient_id)
                    patient_name = patient.last_name + ", " + patient.first_name
                except (InternalError, DoesNotExist):
                    patient_name = None
                try:
                    msg = str(item)[1:-1].split("'")[3]
                except ValueError:
                    msg = ''
                print("msg: ", msg)

                display_list.append(patient_name + ': ' + msg)
                failure_patient_ids.add(patient_id)
                pack_ids_dict.pop(patient_id, None)

            pack_ids_list = [pack_id for pack_ids in list(pack_ids_dict.values()) for pack_id in pack_ids]

            status = set_unit_dosage_flag(company_id=company_id, pack_list=pack_ids_list)
            # if settings.CONSIDER_UNIT_DOSAGE:
            #     status = set_unit_pack_for_multi_dosage(company_id, pack_ids_list)

            print(pack_ids_list)
            if transfer_to_manual_fill_system and pack_ids_list:
                db_max_assign_order_no_manual_packs(company_id, pack_ids_list)
            try:
                update_pending_template_data_in_redisdb(company_id)
            except (RedisConnectionException, Exception):
                pass
            data = {"data": display_list, "more_info": display_list,
                    "patient_ids": list(success_patient_ids.difference(failure_patient_ids)), "pack_ids": pack_ids_list}
            return create_response(data)


@log_args_and_response
def bulk_pack_ids(gen_pack_instances, company_settings):
    """
    Sets pack ids in given instances
    system_settings will be used to communicate

    :param gen_pack_instances: list
    :param company_settings: dict
    :return:
    """
    count_list = [len(i.generated_packs)-1 for i in gen_pack_instances if len(i.generated_packs)-1 > 0]
    qty = sum(count_list)
    if qty:
        try:
            data = send_data(
                company_settings["BASE_URL_IPS"],
                settings.BULK_PACK_IDS_URL, {
                    "qty": qty,
                    'token': company_settings["IPS_COMM_TOKEN"]
                },
                0, _async=False, token=company_settings["IPS_COMM_TOKEN"], timeout=(5, 25)
            )

            data = data["response"]["data"]
            if not data:
                raise PharmacySoftwareResponseException("Couldn't get extra pack IDs from Pharmacy Software. "
                                                        "Kindly contact support.")
        except (PharmacySoftwareResponseException, PharmacySoftwareCommunicationException) as e:
            logger.error(e, exc_info=True)
            raise PharmacySoftwareResponseException("Couldn't get extra pack IDs from Pharmacy Software. "
                                                    "Kindly contact support.")
    else:
        data = list()
    for pack_gen in gen_pack_instances:
        count = len(pack_gen.generated_packs)-1
        pack_gen.pharmacy_pack_id = [pack_gen.pharmacy_fill_id] + data[:count]
        pack_gen.batch_ids = [pack_gen.pharmacy_fill_id] + data[:count]
        data = data[count:]


# @log_args_and_response
# def get_pack_status_from_ips(pack_list, company_settings):
#     """
#     :param pack_list: list
#     :param company_settings: dict
#     :return:
#     """
#     try:
#         data = send_data(
#             company_settings["BASE_URL_IPS"],
#             settings.IPS_STATUS, {
#                 "pack_list": pack_list,
#                 'token': company_settings["IPS_COMM_TOKEN"]
#             },
#             0, _async=False, token=company_settings["IPS_COMM_TOKEN"], timeout=(5, 25)
#         )
#
#         data = data["response"]["data"]
#         if not data:
#             raise PharmacySoftwareResponseException("Couldn't get ips status from Pharmacy Software. "
#                                                     "Kindly contact support.")
#         return data
#
#     except (PharmacySoftwareResponseException, PharmacySoftwareCommunicationException) as e:
#         logger.error(e, exc_info=True)
#         raise PharmacySoftwareResponseException("Couldn't get ips status from Pharmacy Software. "
#                                                 "Kindly contact support.")


@log_args_and_response
def db_check_old_packs_status_for_new_template_process(old_template_id: list, new_template_id: int) -> Dict[str, Any]:
    process_old_packs: bool = False
    delete_old_packs: bool = False
    all_manual: bool = False
    batch_id: int = 0
    facility_dis_id: int = 0
    pack_queue: int = 0
    cr_recommendation_check: bool = False
    mfd_recommendation_check: bool = False
    old_template_admin_list: List[Dict[str, Any]] = []
    new_template_admin_list: List[Dict[str, Any]] = []
    # new_template_drugs_dict: Dict[Any, Any] = defaultdict(set)
    new_template_drugs_dict: Dict[Any, Any] = {}
    slot_fndc_old_drug_dict: Dict[str, int] = {}
    slot_fndc_new_drug_dict: Dict[str, int] = {}
    system_id: int = 0
    update_drug_dict: Dict[int, Dict[str, Any]] = {}
    pack_ids: List[int] = []
    data_set = set()
    final_data_set = set()
    skip_template_dict: dict = {}
    old_template_id = list(set(old_template_id))
    try:
        logger.debug("Check the Pack status for Old Packs...")
        if len(old_template_id) > 1:
            logger.info("In db_check_old_packs_status_for_new_template_process: Multiple Old Template Found")
            # overwriting variable old_template_id
            old_template_id, skip_template_dict = process_multiple_old_template_change_rx(old_template_id)

        # old_template_id is a list
        pack_query = db_get_ext_and_pack_details_for_template(template_ids=[old_template_id])

        done_pack_status: List[int] = list(set(settings.PACK_PROGRESS_DONE_STATUS_LIST) -
                                           {settings.PROGRESS_PACK_STATUS})

        pack_ids = [pack["id"] for pack in pack_query]
        delivered_packs_set = set(record["packs_delivered"] for record in pack_query if record["packs_delivered"])
        delivered_packs = ast.literal_eval(delivered_packs_set.pop()) if delivered_packs_set else []
        logger.debug("Old Pack IDs: {}".format(pack_ids))
        if delivered_packs:
            logger.debug("Old Delivered Packs List: {}".format(delivered_packs))
            # removing delivered packs to not to change its status
            pack_ids = [pack for pack in pack_ids if pack not in delivered_packs]

        for pack in pack_query:
            # pack_ids.append(pack["id"])
            logger.debug("PackID: {}, Pack Status: {}, Ext Pack Status: {}".format(pack["id"], pack["pack_status"],
                                                                                   pack["ext_status_id"]))
            if pack["pack_status"] in settings.PACK_PROGRESS_DONE_STATUS_LIST + [settings.MANUAL_PACK_STATUS,
                                                                                 settings.DELETED_PACK_STATUS]:
                logger.debug("Process Old Packs...")
                process_old_packs = True

                pack_user_map_data_exists = db_check_pack_user_map_data_dao(pack_id=pack["id"])
                if pack["pack_status"] in done_pack_status or \
                        (pack["pack_status"] in [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS,
                                                settings.PARTIALLY_FILLED_BY_ROBOT] and pack_user_map_data_exists):
                    all_manual = True
                else:
                    all_manual = False
                    break
            else:
                if pack["batch_id"]:
                    batch_id = pack["batch_id"]

                if pack["facility_dis_id"]:
                    facility_dis_id = pack["facility_dis_id"]

                if pack["system_id"]:
                    system_id = pack["system_id"]

                if pack["pack_queue"]:
                    pack_queue = pack["pack_queue"]

        if process_old_packs and all_manual:
            delete_old_packs = True

        logger.debug("Fetch the Drugs used in packs from Old Template...")
        slot_fndc_old_drug_dict = db_get_drug_info_old_template_packs(pack_ids=pack_ids)

        new_template_dict = db_get_template_master_info_by_template_id_dao(template_id=new_template_id)
        slot_fndc_new_drug_dict = db_get_drug_info_new_template(patient_id=new_template_dict["patient_id"],
                                                                file_id=new_template_dict["file_id"])

        logger.debug("Old FNDC Dict: {}, New FNDC Dict: {}".format(slot_fndc_old_drug_dict, slot_fndc_new_drug_dict))

        fndc_txr_new_template_list = list(slot_fndc_new_drug_dict.keys())
        for fndc_txr, drug_id in slot_fndc_old_drug_dict.items():
            if fndc_txr in fndc_txr_new_template_list:
                if slot_fndc_old_drug_dict[fndc_txr] != slot_fndc_new_drug_dict[fndc_txr]:
                    logger.debug("Drug change(SAME FNDC -- TXR) found between Old Packs and New Template. "
                                 "Old Packs Drug: {} and New Template Drug: {}"
                                 .format(slot_fndc_old_drug_dict[fndc_txr], slot_fndc_new_drug_dict[fndc_txr]))
                    drug_daw_check_dict = {constants.DRUG_ID_KEY: slot_fndc_old_drug_dict[fndc_txr],
                                           constants.CHECK_DAW_KEY: False}
                    update_drug_dict[slot_fndc_new_drug_dict[fndc_txr]] = drug_daw_check_dict
            else:
                old_fndc_txr_split = fndc_txr.split(settings.SEPARATOR)
                for record in fndc_txr_new_template_list:
                    new_fndc_txr_split = record.split(settings.SEPARATOR)
                    if old_fndc_txr_split[1] == new_fndc_txr_split[1] and \
                            slot_fndc_old_drug_dict[fndc_txr] != slot_fndc_new_drug_dict[record]:
                        logger.debug("Drug change(DIFF FNDC -- SAME TXR) found between Old Packs and New Template. "
                                     "Old Packs Drug: {} and New Template Drug: {}"
                                     .format(slot_fndc_old_drug_dict[fndc_txr], slot_fndc_new_drug_dict[record]))
                        drug_daw_check_dict = {constants.DRUG_ID_KEY: slot_fndc_old_drug_dict[fndc_txr],
                                               constants.CHECK_DAW_KEY: True}
                        update_drug_dict[slot_fndc_new_drug_dict[record]] = drug_daw_check_dict
                        break

        if not process_old_packs:
            logger.debug("Check the Batch - {} and its status...".format(batch_id))
            # assuming that all packs in queue will have a batch ID
            if batch_id:
                batch_status = get_batch_status(batch_id)
                if batch_status not in [settings.BATCH_DELETED, settings.BATCH_PENDING]:

                    # This check is applied mainly to identify if the old packs have all drugs marked for Manual
                    # Then, during Batch Import they get sent to Manual flow.
                    # For Change Rx, if new template is received then it should be processed directly as Manual
                    old_packs_devices = get_device_id_from_pack_list(pack_list=pack_ids)
                    if batch_status != settings.BATCH_IMPORTED and not old_packs_devices:
                        process_old_packs = True
                        delete_old_packs = True
                    else:
                        logger.debug("Recommendation has been executed for Batch ID: {}".format(batch_id))
                        cr_recommendation_check = True

                        mfd_exists_for_batch = db_check_mfd_exists_for_batch_and_template(batch_id=batch_id,
                                                                                          template_id=old_template_id[0])
                        if mfd_exists_for_batch:
                            logger.debug("Verify if admin duration is same among Old and New Template...")
                            mfd_recommendation_check = True

                            old_template_dict = \
                                db_get_template_master_info_by_template_id_dao(template_id=old_template_id[0])
                            old_template_admin_list = \
                                db_get_template_admin_duration_dao(patient_id=old_template_dict["patient_id"],
                                                                   file_id=old_template_dict["file_id"])
                            new_template_admin_list = \
                                db_get_template_admin_duration_dao(patient_id=new_template_dict["patient_id"],
                                                                   file_id=new_template_dict["file_id"])

                            if old_template_admin_list and new_template_admin_list:
                                if old_template_admin_list[0]["fill_start_date"] == \
                                        new_template_admin_list[0]["fill_start_date"] and \
                                        old_template_admin_list[0]["fill_end_date"] == \
                                        new_template_admin_list[0]["fill_end_date"]:

                                    logger.debug("Verify the MFD unique drugs among Old and New Template...")

                                    old_template_args = {
                                        "patient_id": old_template_dict["patient_id"],
                                        "file_id": old_template_dict["file_id"],
                                        "company_id": old_template_dict["company_id"]
                                    }
                                    mfd_drugs_dict = \
                                        db_get_mfd_drugs_template_combination(patient_id=
                                                                              old_template_dict["patient_id"],
                                                                              file_id=old_template_dict["file_id"])

                                    if mfd_drugs_dict:
                                        new_template_args = {
                                            "patient_id": new_template_dict["patient_id"],
                                            "file_id": new_template_dict["file_id"],
                                            "company_id": new_template_dict["company_id"]
                                        }
                                        new_template_response = get_template_data_v2(new_template_args)
                                        new_template_data = new_template_response.get("template_data", [])
                                        for template_column in new_template_data:
                                            data_set.clear()
                                            if template_column["formatted_ndc"] and template_column["txr"]:
                                                if template_column["drug_id"] in new_template_drugs_dict.keys():
                                                    data_set = \
                                                        new_template_drugs_dict[template_column["drug_id"]]["data"]
                                                    data_set.add(db_prepare_mfd_drug_template_column_unique_data(
                                                            template_column["column_number"],
                                                            template_column["hoa_time"], template_column["quantity"],
                                                            template_column["formatted_ndc"], template_column["txr"]))
                                                    final_data_set = copy.deepcopy(data_set)
                                                    new_template_drugs_dict[template_column["drug_id"]]["data"] = \
                                                        final_data_set
                                                else:
                                                    data_set.add(db_prepare_mfd_drug_template_column_unique_data(
                                                            template_column["column_number"],
                                                            template_column["hoa_time"], template_column["quantity"],
                                                            template_column["formatted_ndc"], template_column["txr"]))
                                                    final_data_set = copy.deepcopy(data_set)
                                                    fndc_dict = {
                                                        "fndc_txr": template_column["formatted_ndc"] +
                                                                    settings.SEPARATOR + template_column["txr"],
                                                        "data": final_data_set
                                                    }
                                                    new_template_drugs_dict[template_column["drug_id"]] = fndc_dict

                                        logger.debug("Old Template MFD Drug Dictionary: {}".format(mfd_drugs_dict))
                                        logger.debug("New Template Drug Dictionary: {}".format(new_template_drugs_dict))

                                        for old_drug_id, old_mfd_data in mfd_drugs_dict.items():
                                            match_drug_found = False
                                            for new_drug_id, new_mfd_data in new_template_drugs_dict.items():
                                                if old_mfd_data["fndc_txr"] == new_mfd_data["fndc_txr"]:
                                                    logger.debug("Matching MFD Drug found in new template")

                                                    match_drug_found = True
                                                    if old_mfd_data["data"] == new_mfd_data["data"]:
                                                        logger.debug("Same split found between Old and New Template..")
                                                        # todo this is done temporary until we don't fix the code for mfd mapping
                                                        if old_mfd_data["mfd_fill_status"] > 0:
                                                            process_old_packs = True
                                                        # if old_drug_id != new_drug_id:
                                                        #     slot_fndc_drug_update_dict[new_drug_id] = old_drug_id
                                                    else:
                                                        logger.debug("Different split found between Old and "
                                                                     "New Template..")
                                                        if old_mfd_data["mfd_fill_status"] > 0:
                                                            process_old_packs = True
                                                    break
                                            if process_old_packs:
                                                break

                                            logger.debug("Match Drug Status: {}, MFD Fill Status: {}"
                                                         .format(match_drug_found, old_mfd_data["mfd_fill_status"]))
                                            if not match_drug_found and old_mfd_data["mfd_fill_status"] > 0:
                                                process_old_packs = True
                                                break
                                    else:
                                        logger.debug("Old Template does not contain MFD Drugs...")
                                else:
                                    logger.debug("Admin Duration Mismatch among Old and New Templates...")
                            else:
                                logger.debug("Error in fetching Admin Duration -- Old Template Duration: {}, "
                                             "New Template Duration: {}".format(old_template_admin_list,
                                                                                new_template_admin_list))

        old_packs_dict: Dict[str, Any] = {
            "process_old_packs": process_old_packs,
            "delete_old_packs": delete_old_packs,
            "batch_id": batch_id,
            "cr_recommendation_check": cr_recommendation_check,
            "mfd_recommendation_check": mfd_recommendation_check,
            "facility_dis_id": facility_dis_id,
            "slot_drug_update": update_drug_dict,
            "system_id": system_id,
            "pack_queue": pack_queue,
            "skip_template_dict": skip_template_dict
        }

        return old_packs_dict
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException


@log_args_and_response
def process_multiple_old_template_change_rx(old_template_ids):
    delete_current_template_packs: bool = False
    template_to_select: int = 0
    manual_template = []
    pack_queue_in_progress_template = []
    pack_queue_pending_template = []
    pack_pre_recommended_template = []
    batch_allocated_template = []
    facility_dist_allocated_template = []
    pack_generated_template = []


    try:
        # assuming that nearest admin template will be at first
        for template in old_template_ids:

            pack_query = db_get_ext_and_pack_details_for_template(template_ids=[template])

            done_pack_status: List[int] = list(set(settings.PACK_PROGRESS_DONE_STATUS_LIST) -
                                               {settings.PROGRESS_PACK_STATUS})

            pack_ids = [pack["id"] for pack in pack_query]
            delivered_packs_set = set(record["packs_delivered"] for record in pack_query if record["packs_delivered"])
            delivered_packs = ast.literal_eval(delivered_packs_set.pop()) if delivered_packs_set else []
            logger.debug("Old Pack IDs: {}".format(pack_ids))
            if delivered_packs:
                logger.debug("Old Delivered Packs List: {}".format(delivered_packs))
                # removing delivered packs to not to change its status
                pack_ids = [pack for pack in pack_ids if pack not in delivered_packs]
                if not len(pack_ids):
                    logger.debug("In process_multiple_old_template_change_rx: All packs are delivered for template {}".format(template) )
                    continue
            for pack in pack_query:
                # will run loop once
                pack_status = pack["pack_status"]
                if pack_status in settings.PACK_PROGRESS_DONE_STATUS_LIST:
                    if template not in pack_queue_in_progress_template:
                        pack_queue_in_progress_template.append(template)
                elif pack_status == settings.MANUAL_PACK_STATUS:
                    if template not in manual_template:
                        manual_template.append(template)
                elif pack['pack_queue']:
                    # get pack mfd status
                    mfd_status_list = db_get_mfd_pack_status(template)
                    if set(mfd_status_list).intersection(
                            {constants.MFD_CANISTER_FILLED_STATUS, constants.MFD_CANISTER_VERIFIED_STATUS,
                             constants.MFD_CANISTER_RTS_REQUIRED_STATUS}):
                        if template not in pack_queue_in_progress_template:
                            pack_queue_in_progress_template.append(template)
                    elif template not in pack_queue_pending_template:
                        pack_queue_pending_template.append(template)
                elif pack['batch_id']:
                    batch_id = pack['batch_id']
                    batch_status = get_batch_status(batch_id)
                    if batch_status not in [settings.BATCH_DELETED, settings.BATCH_PENDING]:
                        old_packs_devices = get_device_id_from_pack_list(pack_list=[pack['id']])
                        if batch_status != settings.BATCH_IMPORTED and old_packs_devices:
                            if template not in pack_pre_recommended_template:
                                pack_pre_recommended_template.append(template)
                    else:
                        batch_allocated_template.append(template)
                elif pack['facility_dis_id']:
                    facility_dist_allocated_template.append(template)
                else:
                    pack_generated_template.append(template)

                break

        if pack_queue_pending_template:
            template_to_select = pack_queue_pending_template[0]
        elif pack_pre_recommended_template:
            template_to_select = pack_queue_pending_template[0]
        elif batch_allocated_template:
            template_to_select = batch_allocated_template[0]
        elif facility_dist_allocated_template:
            template_to_select = facility_dist_allocated_template[0]
        elif manual_template:
            template_to_select = manual_template[0]
        elif pack_generated_template:
                    template_to_select = pack_generated_template[0]

        else:
            # worst case all fails:
            template_to_select = old_template_ids[0]

        skip_template_dict = {
            "process_pack_template": [template for template in pack_queue_in_progress_template if template != template_to_select],
            "direct_delete_template": [template for template in
                                       pack_queue_pending_template + batch_allocated_template + facility_dist_allocated_template + manual_template + pack_generated_template
                                       if template != template_to_select]
        }
        return [template_to_select], skip_template_dict

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException


