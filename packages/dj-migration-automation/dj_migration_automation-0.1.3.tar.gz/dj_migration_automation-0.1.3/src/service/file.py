from peewee import InternalError, IntegrityError

import settings
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response, convert_date_to_sql_date, get_current_date_time
from dosepack.validation.validate import validate
from src.dao.file_dao import get_files_dao, db_verify_file_id_dao
from src.dao.template_dao import db_ungenerate_file, get_ungenerate_files
from src.exceptions import RedisConnectionException, TemplateAlreadyProcessed

from src.redis_controller import update_pending_template_data_in_redisdb
from src.service.misc import real_time_db_timestamp_trigger


logger = settings.logger


@log_args_and_response
@validate(required_fields=["date_from", "date_to", "company_id", "time_zone"],
          validate_dates=['date_from', 'date_to'])
def get_files(dict_info):
    """
    Takes the input argument for file search and retrieves
    the files which falls in the search criteria.

    Args:
        dict_info (dict): A dict containing date_from and date_to
    Returns:
        list: List of all the files which falls in the search criteria

    Examples:
        >>> get_files({})

    """
    # get the values from the input dict keys
    logger.debug("files: dict_info- {}".format(dict_info))
    start_date = dict_info["date_from"]
    end_date = dict_info["date_to"]
    time_zone = dict_info["time_zone"]
    status = int(dict_info["status"])
    company_id = int(dict_info["company_id"])

    start_date, end_date = convert_date_to_sql_date(start_date, end_date)

    all_status_list = settings.DEFAULT_FILE_STATUS

    if status == settings.NULL:
        status = all_status_list
    else:
        status = [status]
    template_status_list = [settings.DONE_TEMPLATE_STATUS]

    file_records = []

    # if CeleryTaskmeta.table_exists():
    #     if settings.USE_FILE_TASK_QUEUE:
    #         # roll_backfile = fn.IF(FileHeader.task_id.is_null(True),
    #         #                       fn.IF(FileHeader.status << [settings.PENDING_FILE_STATUS,
    #         #                                                   settings.ERROR_FILE_STATUS,
    #         #                                                   settings.PROCESSED_FILE_STATUS],
    #         #                             fn.IF(TemplateMaster.id.is_null(True), True, False),
    #         #                             False),
    #         #                       fn.IF(CeleryTaskmeta.status << [settings.SUCCESS_TEMPLATE_TASK_IN_TASK_QUEUE,
    #         #                                                       settings.FAILURE_TEMPLATE_TASK_IN_TASK_QUEUE],
    #         #                             fn.IF(FileHeader.status << [settings.PENDING_FILE_STATUS,
    #         #                                                         settings.ERROR_FILE_STATUS,
    #         #                                                         settings.PROCESSED_FILE_STATUS],
    #         #                                   fn.IF(TemplateMaster.id.is_null(True), True, False),
    #         #                                   False),
    #         #                             False)
    #         #                       )
    #         roll_backfile = fn.IF(FileHeader.status << [settings.ERROR_FILE_STATUS, settings.PROCESSED_FILE_STATUS],
    #                                 fn.IF(TemplateMaster.status.in_(template_status_list), False, True),
    #                                   fn.IF(FileHeader.status == settings.PENDING_FILE_STATUS,
    #                                         fn.IF(CeleryTaskmeta.status.is_null(True),
    #                                               False,
    #                                               fn.IF(TemplateMaster.status.in_(template_status_list), False, True),
    #                                               ),
    #                                         False)
    #                                   )
    #         file_status = fn.IF(FileHeader.status == settings.PENDING_FILE_STATUS,
    #                             fn.IF(CeleryTaskmeta.status.is_null(False), settings.ERROR_FILE_STATUS,
    #                                   settings.PENDING_FILE_STATUS)
    #                             , FileHeader.status)
    #         message = fn.IF(FileHeader.status == settings.PENDING_FILE_STATUS,
    #                         fn.IF(CeleryTaskmeta.status.is_null(False), "Unable to access the database."
    #                                                                     " Kindly rollback the file and upload it again.",
    #                               FileHeader.message)
    #                         , FileHeader.message)
    #     else:
    #         roll_backfile = fn.IF(FileHeader.status << [settings.PENDING_FILE_STATUS,
    #                                                               settings.ERROR_FILE_STATUS,
    #                                                               settings.PROCESSED_FILE_STATUS],
    #                                         fn.IF(TemplateMaster.status.in_(template_status_list), False, True),
    #                                         False)
    #         file_status = FileHeader.status
    #         message = FileHeader.message
    # else:
    #     roll_backfile = fn.IF(FileHeader.status << [settings.PENDING_FILE_STATUS,
    #                                                 settings.ERROR_FILE_STATUS,
    #                                                 settings.PROCESSED_FILE_STATUS],
    #                           fn.IF(TemplateMaster.in_(template_status_list), False, True),
    #                           False)
    #     file_status = FileHeader.status
    #     message = FileHeader.message
    # try:
    #     if CeleryTaskmeta.table_exists():
    #         query = FileHeader.select(FileHeader.filename,
    #                                   FileHeader.created_date,
    #                                   FileHeader.created_time,
    #                                   FileHeader.created_by,
    #                                   FileHeader.manual_upload,
    #                                   FileHeader.filepath,
    #                                   message.alias('message'),
    #                                   file_status.alias('file_status'),
    #                                   FileHeader.id,
    #                                   CodeMaster.value,
    #                                   roll_backfile.alias('can_rollback'),
    #                                   FileValidationError.file_id.alias('file_validation_error'),
    #                                   ) \
    #             .join(CodeMaster, on=FileHeader.status == CodeMaster.id) \
    #             .join(CeleryTaskmeta, JOIN_LEFT_OUTER, on=FileHeader.task_id == CeleryTaskmeta.task_id) \
    #             .join(TemplateMaster, JOIN_LEFT_OUTER, on=TemplateMaster.file_id == FileHeader.id) \
    #             .join(FileValidationError, JOIN_LEFT_OUTER, on=FileHeader.id == FileValidationError.file_id).dicts() \
    #             .order_by(SQL('FIELD(file_status, {}, {}, {}, {})'.format(settings.ERROR_FILE_STATUS,
    #                                                                       settings.PROCESSED_FILE_STATUS,
    #                                                                       settings.PENDING_FILE_STATUS,
    #                                                                       settings.UNGENERATE_FILE_STATUS)),
    #                       FileHeader.modified_date.desc()) \
    #             .group_by(FileHeader.id) \
    #             .where(FileHeader.company_id == company_id,
    #                    FileHeader.status << status,
    #                    fn.DATE(fn.CONVERT_TZ(cast(fn.CONCAT(FileHeader.created_date, ' ',
    #                                                         FileHeader.created_time), 'DATETIME'), settings.TZ_UTC,
    #                                          time_zone)).between(start_date, end_date)
    #                    )
    #     else:
    #         query = FileHeader.select(FileHeader.filename,
    #                                   FileHeader.created_date,
    #                                   FileHeader.created_time,
    #                                   FileHeader.created_by,
    #                                   FileHeader.manual_upload,
    #                                   FileHeader.filepath,
    #                                   message.alias('message'),
    #                                   file_status.alias('file_status'),
    #                                   FileHeader.id,
    #                                   CodeMaster.value,
    #                                   roll_backfile.alias('can_rollback'),
    #                                   FileValidationError.file_id.alias('file_validation_error'),
    #                                   ) \
    #             .join(CodeMaster, on=FileHeader.status == CodeMaster.id) \
    #             .join(TemplateMaster, JOIN_LEFT_OUTER, on=TemplateMaster.file_id == FileHeader.id) \
    #             .join(FileValidationError, JOIN_LEFT_OUTER, on=FileHeader.id == FileValidationError.file_id).dicts() \
    #             .order_by(SQL('FIELD(file_status, {}, {}, {}, {})'.format(settings.ERROR_FILE_STATUS,
    #                                                                       settings.PROCESSED_FILE_STATUS,
    #                                                                       settings.PENDING_FILE_STATUS,
    #                                                                       settings.UNGENERATE_FILE_STATUS)),
    #                       FileHeader.modified_date.desc()) \
    #             .group_by(FileHeader.id) \
    #             .where(FileHeader.company_id == company_id,
    #                    FileHeader.status << status,
    #                    fn.DATE(fn.CONVERT_TZ(cast(fn.CONCAT(FileHeader.created_date, ' ',
    #                                                         FileHeader.created_time), 'DATETIME'), settings.TZ_UTC,
    #                                          time_zone)).between(start_date, end_date)
    #                    )
    #     for record in query:
    #         record["status"] = settings.FILE_CODES[record["file_status"]]
    #         record["value"] = settings.FILE_CODES[record["file_status"]]
    #         record['created_date'] = datetime.combine(record["created_date"], record["created_time"])
    #         file_records.append(record)
    #
    #     logger.debug("files: fetched file data.")
    #
    #     # add patient data based on pharmacy_patient_id in filename -
    #     # e.g., filename- FID_2_01355328_27536.txt, extracted pharmacy_patient_id - 27536
    #     for file in file_records:
    #         if file["filename"]:
    #             logger.debug("files: file-"+str(file["filename"]))
    #             pharmacy_patient_ids.add(('.').join(file["filename"].split('.')[:-1]).split('_')[-1])
    #
    #     logger.debug("files: pharmacy_patient_ids- {}".format(pharmacy_patient_ids))
    #
    #     if pharmacy_patient_ids:
    #         for patient_record in PatientMaster.select(PatientMaster.id,
    #                                              PatientMaster.pharmacy_patient_id,
    #                                              PatientMaster.concated_patient_name_field().alias('patient_name')) \
    #             .dicts().where(PatientMaster.pharmacy_patient_id << list(pharmacy_patient_ids),
    #                            PatientMaster.company_id == company_id):
    #             patient_dict[patient_record["pharmacy_patient_id"]] = (patient_record["id"], patient_record["patient_name"])
    #
    #         logger.debug("files: patient_dict- {}".format(patient_dict))
    #
    #     for file in file_records:
    #         pharmacy_patient_id = int(('.').join(file["filename"].split('.')[:-1]).split('_')[-1])
    #         if pharmacy_patient_id in patient_dict.keys():
    #             file["patient_id"] = patient_dict[pharmacy_patient_id][0]
    #             file["patient_name"] = patient_dict[pharmacy_patient_id][1]
    #         else:
    #             file["patient_id"] = None
    #             file["patient_name"] = None
    #     logger.debug("files: Patient data added.")

    try:
        file_records = get_files_dao(template_status_list=template_status_list, company_id=company_id, status=status,
                                     time_zone=time_zone, start_date=start_date, end_date=end_date)
    except InternalError as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except StopIteration as e:
        logger.error(e, exc_info=True)
        return error(1004)

    return create_response(file_records)


@log_args_and_response
@validate(required_fields=["file_id", "user_id", "message", "company_id"])
def ungenerate_files(dict_file_info):
    """
    @function: ungenerate_files
    @createdBy: Manish Agarwal
    @createdDate: 02/18/2016
    @lastModifiedBy: Dushyant Parmar
    @lastModifiedDate: 10/31/2017
    @type: function
    @param: dict
    @purpose - to ungenerate file and change status for templates and packs
    @input -
        type: (dict)
        dict_date_range =
        {
             "file_id": "123",
             "user_id": 2,
             "message": "No Proper Dates",
             "company_id": 2
         }
    @output -
    {
        "status":"success", "error":"none"
    }

    """
    # get the values from the input dict keys
    file_id = dict_file_info["file_id"]
    user_id = int(dict_file_info["user_id"])  # get user_id from client
    message = dict_file_info["message"]
    company_id = dict_file_info["company_id"]
    modified_date = get_current_date_time()
    status = settings.UNGENERATE_FILE_STATUS

    # valid_file = FileHeader.db_verify_file_id(file_id, company_id)
    valid_file = db_verify_file_id_dao(file_id, company_id)

    if not valid_file:  # check whether file id is valid for system
        return error(1016)
    try:
        response = db_ungenerate_file(
            file_id, status, message,
            user_id, modified_date, company_id
        )
        if response:
            try:
                update_pending_template_data_in_redisdb(company_id)
            except (RedisConnectionException, Exception):
                pass
    except TemplateAlreadyProcessed as e:
        logger.error(e, exc_info=True)
        return error(5004)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Unknown error - " + str(e))
    finally:
        real_time_db_timestamp_trigger(
            settings.CONST_PRESCRIPTION_FILE_DOC_ID,
            company_id=company_id
        )
        real_time_db_timestamp_trigger(
            settings.CONST_TEMPLATE_MASTER_DOC_ID,
            company_id=company_id
        )

    return create_response(response)


def sample_function(a):
    return a


@log_args_and_response
@validate(required_fields=["date_from", "date_to", "company_id"],
          validate_dates=['date_from', 'date_to'])
def show_ungenerate_files(dict_file_info):
    try:
        dateTo = dict_file_info["date_to"]
        dateFrom = dict_file_info["date_from"]
        company_id = int(dict_file_info["company_id"])
        status = settings.UNGENERATE_FILE_STATUS

        fileList = []
        for record in get_ungenerate_files(status, dateFrom,
                                           dateTo, company_id):
            fileList.append(record)
        return fileList
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Unknown error - " + str(e))