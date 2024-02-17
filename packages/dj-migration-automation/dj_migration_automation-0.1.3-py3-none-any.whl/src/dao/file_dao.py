from playhouse.shortcuts import cast

from peewee import fn, JOIN_LEFT_OUTER, SQL, InternalError, IntegrityError, DataError
from datetime import datetime

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import log_args_and_response
from src.model.model_celery_task_meta import CeleryTaskmeta
from src.model.model_code_master import CodeMaster
from src.model.model_file_header import FileHeader
from src.model.model_file_validation_error import FileValidationError
from src.model.model_patient_master import PatientMaster
from src.model.model_template_master import TemplateMaster

logger = settings.logger


@log_args_and_response
def get_files_dao(template_status_list, company_id, status, time_zone, start_date, end_date):
    """

    @param template_status_list: 
    @param company_id: 
    @param status: 
    @param time_zone: 
    @param start_date: 
    @param end_date: 
    @return: 
    """
    file_records = []
    pharmacy_patient_ids = set()
    patient_dict = dict()

    try:
        if CeleryTaskmeta.table_exists():
            if settings.USE_FILE_TASK_QUEUE:
                # roll_backfile = fn.IF(FileHeader.task_id.is_null(True),
                #                       fn.IF(FileHeader.status << [settings.PENDING_FILE_STATUS,
                #                                                   settings.ERROR_FILE_STATUS,
                #                                                   settings.PROCESSED_FILE_STATUS],
                #                             fn.IF(TemplateMaster.id.is_null(True), True, False),
                #                             False),
                #                       fn.IF(CeleryTaskmeta.status << [settings.SUCCESS_TEMPLATE_TASK_IN_TASK_QUEUE,
                #                                                       settings.FAILURE_TEMPLATE_TASK_IN_TASK_QUEUE],
                #                             fn.IF(FileHeader.status << [settings.PENDING_FILE_STATUS,
                #                                                         settings.ERROR_FILE_STATUS,
                #                                                         settings.PROCESSED_FILE_STATUS],
                #                                   fn.IF(TemplateMaster.id.is_null(True), True, False),
                #                                   False),
                #                             False)
                #                       )
                roll_back_file = fn.IF(
                    FileHeader.status << [settings.ERROR_FILE_STATUS, settings.PROCESSED_FILE_STATUS],
                    fn.IF(TemplateMaster.status.in_(template_status_list), False, True),
                    fn.IF(FileHeader.status == settings.PENDING_FILE_STATUS,
                          fn.IF(CeleryTaskmeta.status.is_null(True),
                                False,
                                fn.IF(TemplateMaster.status.in_(template_status_list), False, True),
                                ),
                          False)
                    )
                file_status = fn.IF(FileHeader.status == settings.PENDING_FILE_STATUS,
                                    fn.IF(CeleryTaskmeta.status.is_null(False), settings.ERROR_FILE_STATUS,
                                          settings.PENDING_FILE_STATUS), FileHeader.status)
                message = fn.IF(FileHeader.status == settings.PENDING_FILE_STATUS,
                                fn.IF(CeleryTaskmeta.status.is_null(False), "Unable to access the database."
                                                                            " Kindly rollback the file and upload it "
                                                                            "again.",
                                      FileHeader.message), FileHeader.message)
            else:
                roll_back_file = fn.IF(FileHeader.status << [settings.PENDING_FILE_STATUS,
                                                             settings.ERROR_FILE_STATUS,
                                                             settings.PROCESSED_FILE_STATUS],
                                       fn.IF(TemplateMaster.status.in_(template_status_list), False, True),
                                       False)
                file_status = FileHeader.status
                message = FileHeader.message
        else:
            roll_back_file = fn.IF(FileHeader.status << [settings.PENDING_FILE_STATUS,
                                                         settings.ERROR_FILE_STATUS,
                                                         settings.PROCESSED_FILE_STATUS],
                                   fn.IF(TemplateMaster.in_(template_status_list), False, True),
                                   False)
            file_status = FileHeader.status
            message = FileHeader.message

        if CeleryTaskmeta.table_exists():
            query = FileHeader.select(FileHeader.filename,
                                      FileHeader.created_date,
                                      FileHeader.created_time,
                                      FileHeader.created_by,
                                      FileHeader.manual_upload,
                                      FileHeader.filepath,
                                      message.alias('message'),
                                      file_status.alias('file_status'),
                                      FileHeader.id,
                                      CodeMaster.value,
                                      roll_back_file.alias('can_rollback'),
                                      FileValidationError.file_id.alias('file_validation_error'),
                                      ) \
                .join(CodeMaster, on=FileHeader.status == CodeMaster.id) \
                .join(CeleryTaskmeta, JOIN_LEFT_OUTER, on=FileHeader.task_id == CeleryTaskmeta.task_id) \
                .join(TemplateMaster, JOIN_LEFT_OUTER, on=TemplateMaster.file_id == FileHeader.id) \
                .join(FileValidationError, JOIN_LEFT_OUTER, on=FileHeader.id == FileValidationError.file_id).dicts() \
                .order_by(SQL('FIELD(file_status, {}, {}, {}, {})'.format(settings.ERROR_FILE_STATUS,
                                                                          settings.PROCESSED_FILE_STATUS,
                                                                          settings.PENDING_FILE_STATUS,
                                                                          settings.UNGENERATE_FILE_STATUS)),
                          FileHeader.modified_date.desc()) \
                .group_by(FileHeader.id) \
                .where(FileHeader.company_id == company_id,
                       FileHeader.status << status,
                       fn.DATE(fn.CONVERT_TZ(cast(fn.CONCAT(FileHeader.created_date, ' ',
                                                            FileHeader.created_time), 'DATETIME'), settings.TZ_UTC,
                                             time_zone)).between(start_date, end_date)
                       )
        else:
            query = FileHeader.select(FileHeader.filename,
                                      FileHeader.created_date,
                                      FileHeader.created_time,
                                      FileHeader.created_by,
                                      FileHeader.manual_upload,
                                      FileHeader.filepath,
                                      message.alias('message'),
                                      file_status.alias('file_status'),
                                      FileHeader.id,
                                      CodeMaster.value,
                                      roll_back_file.alias('can_rollback'),
                                      FileValidationError.file_id.alias('file_validation_error'),
                                      ) \
                .join(CodeMaster, on=FileHeader.status == CodeMaster.id) \
                .join(TemplateMaster, JOIN_LEFT_OUTER, on=TemplateMaster.file_id == FileHeader.id) \
                .join(FileValidationError, JOIN_LEFT_OUTER, on=FileHeader.id == FileValidationError.file_id).dicts() \
                .order_by(SQL('FIELD(file_status, {}, {}, {}, {})'.format(settings.ERROR_FILE_STATUS,
                                                                          settings.PROCESSED_FILE_STATUS,
                                                                          settings.PENDING_FILE_STATUS,
                                                                          settings.UNGENERATE_FILE_STATUS)),
                          FileHeader.modified_date.desc()) \
                .group_by(FileHeader.id) \
                .where(FileHeader.company_id == company_id,
                       FileHeader.status << status,
                       fn.DATE(fn.CONVERT_TZ(cast(fn.CONCAT(FileHeader.created_date, ' ',
                                                            FileHeader.created_time), 'DATETIME'), settings.TZ_UTC,
                                             time_zone)).between(start_date, end_date)
                       )

        for record in query:
            record["status"] = settings.FILE_CODES[record["file_status"]]
            record["value"] = settings.FILE_CODES[record["file_status"]]
            record['created_date'] = datetime.combine(record["created_date"], record["created_time"])
            file_records.append(record)

        logger.info("files: fetched file data.")

        # add patient data based on pharmacy_patient_id in filename -
        # e.g., filename- FID_2_01355328_27536.txt, extracted pharmacy_patient_id - 27536
        for file in file_records:
            if file["filename"]:
                logger.info("files: file-" + str(file["filename"]))
                pharmacy_patient_ids.add(('.').join(file["filename"].split('.')[:-1]).split('_')[-1])

        logger.info("files: pharmacy_patient_ids- {}".format(pharmacy_patient_ids))

        if pharmacy_patient_ids:
            for patient_record in PatientMaster.select(PatientMaster.id,
                                                       PatientMaster.pharmacy_patient_id,
                                                       PatientMaster.concated_patient_name_field().alias(
                                                           'patient_name')) \
                    .dicts().where(PatientMaster.pharmacy_patient_id << list(pharmacy_patient_ids),
                                   PatientMaster.company_id == company_id):
                patient_dict[patient_record["pharmacy_patient_id"]] = (
                    patient_record["id"], patient_record["patient_name"])

            logger.info("files: patient_dict- {}".format(patient_dict))

        for file in file_records:
            pharmacy_patient_id = int(('.').join(file["filename"].split('.')[:-1]).split('_')[-1])
            if pharmacy_patient_id in patient_dict.keys():
                file["patient_id"] = patient_dict[pharmacy_patient_id][0]
                file["patient_name"] = patient_dict[pharmacy_patient_id][1]
            else:
                file["patient_id"] = None
                file["patient_name"] = None
        logger.info("files: Patient data added.")

        return file_records

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_files_dao:  {}".format(e))
        raise
    except StopIteration as e:
        logger.error("error in get_files_dao:  {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_files_dao:  {}".format(e))
        raise


@log_args_and_response
def db_verify_file_id_dao(file_id, company_id):
    try:
        return FileHeader.db_verify_file_id(file_id=file_id, company_id=company_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_verify_file_id_dao:  {}".format(e))
        raise


@log_args_and_response
def db_get_file_info_not_ungenerated_dao(company_id, file_ids, status):
    try:
        return FileHeader.db_get_file_info_not_ungenerated(company_id=company_id, file_ids=file_ids, status=status)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_file_header_create_record_dao(file_dict):
    try:
        return BaseModel.db_create_record(file_dict, FileHeader)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_update_file_status_message_path_dao(status, message, filepath, file_id):
    try:
        return FileHeader.db_update_file_status_message_path(status=status, message=message, filepath=filepath,
                                                             file_id=file_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_file_header_get_or_create_dao(filename, status, file_dict):
    try:
        return FileHeader.db_get_or_create(filename=filename, status=status, file_dict=file_dict)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_file_header_update_task_id_dao(file_id, task_id):
    try:
        return FileHeader.db_update_task_id(file_id=file_id, task_id=task_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_file_by_filename_status_company_dao(filename, status, company_id):
    try:
        return FileHeader.db_get_file_by_filename_status_company(filename=filename, status=status,
                                                                 company_id=company_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_file_validation_error_dao(file_id):
    file_validation_error_list = list()
    try:
        query = FileValidationError.select(FileValidationError.file_id,
                                           FileValidationError.patient_name,
                                           FileValidationError.patient_no,
                                           FileValidationError.column,
                                           FileValidationError.value,
                                           fn.trim(fn.GROUP_CONCAT(' ', FileValidationError.message))
                                           .alias('message')).dicts() \
            .group_by(FileValidationError.file_id,
                      FileValidationError.patient_no,
                      FileValidationError.column,
                      FileValidationError.value).where(FileValidationError.file_id == file_id)
        for record in query:
            file_validation_error_list.append(record)

        return file_validation_error_list
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_file_validation_error_dao:  {}".format(e))
        raise


@log_args_and_response
def db_verify_filelist_dao(file_ids, company_id):
    try:
        return FileHeader.db_verify_filelist(filelist=file_ids, company_id=company_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_verify_filelist_dao:  {}".format(e))
        raise
    
    
def db_get_files_by_filename_dao(filename_without_extension, company_id):
    try:
        return FileHeader.db_get_files_by_filename(filename_without_extension, company_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_files_by_filename_dao:  {}".format(e))
        raise e


def get_file_upload_data_dao(file_id):
    try:
        return FileHeader.db_get_file_upload_data(file_id=file_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_file_upload_data_dao:  {}".format(e))
        raise e
