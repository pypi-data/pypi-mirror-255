from typing import Dict, Any

import settings
from dosepack.utilities.utils import get_current_date, get_current_date_time, get_current_time, log_args_and_response
from src.model.model_ext_change_rx import ExtChangeRx
from src.model.model_ext_hold_rx import ExtHoldRx
from src.model.model_file_header import FileHeader
from peewee import *
from src.exceptions import DuplicateFileException
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_template_master import TemplateMaster
from src.service.misc import real_time_db_timestamp_trigger

logger = settings.logger


@log_args_and_response
def get_files_by_name(filename: str, company_id: int) -> list:
    """
    Method to fetch files based on name
    @param filename:
    @param company_id:
    @return:
    """
    try:
        return FileHeader.db_get_files_by_filename(filename, company_id)
    except InternalError as e:
        logger.error("error in get_files_by_name:  {}".format(e))
        raise e


@log_args_and_response
def add_file(filename: str, company_id: int, user_id: int, manual_upload: bool = False, file_status=None,
             file_path=None, message=None) -> object:
    """ Creates a record in the file header for the received file. Stores the id of the inserted record
    in the file_id variable"""

    try:
        file_status = file_status if file_status else settings.PENDING_FILE_STATUS
        file_path = file_path if file_path else settings.PENDING_FILE_PATH
        _record = FileHeader.get_or_create(
            filename=filename, status=file_status,
            defaults={
                'filepath': file_path,
                "manual_upload": manual_upload,
                "created_date": get_current_date(),
                "created_time": get_current_time(),
                "modified_date": get_current_date_time(),
                "company_id": company_id,
                "created_by": user_id,
                "modified_by": user_id,
                "message": message
            }
        )
        if not _record[1]:  # if record already present
            raise DuplicateFileException
        return _record[0]
    except (IntegrityError, InternalError, DataError, OperationalError, DuplicateFileException) as e:
        logger.error("error in add_file:  {}".format(e))
        raise e


@log_args_and_response
def update_couch_db_pending_template_count(company_id: int):
    pending_template_count: int = 0
    try:
        logger.debug("Update the Pending Templates Count in CouchDB...")
        pending_template_status = settings.PENDING_PROGRESS_TEMPLATE_LIST

        template_data = TemplateMaster.select(TemplateMaster.patient_id,
                                              TemplateMaster.file_id).dicts() \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMaster.status << pending_template_status)

        pending_template_count = template_data.count()
        real_time_db_timestamp_trigger(settings.CONST_TEMPLATE_MASTER_DOC_ID, company_id=company_id,
                                       update_count_flag=True, update_count=pending_template_count)

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        logger.error("Issue with update of CouchDB for Pending Template Count..")


@log_args_and_response
def get_template_ext_data(template_id: int):
    template_dict: Dict[str, Any] = {}
    try:
        template_query = TemplateMaster.select(TemplateMaster.id, ExtChangeRx.ext_action).dicts()\
            .join(ExtChangeRx, on=TemplateMaster.id == ExtChangeRx.new_template)\
            .where(TemplateMaster.id == template_id)

        for template in template_query:
            template_dict["template_id"] = template["id"]
            template_dict["status"] = template["ext_action"]

        return template_dict
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return {}
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def insert_ext_hold_rx_data_dao(hold_rx_dict: dict, file_id: int):
    """
    Function to add data in ext_hold_rx table,
    hold_rx: rx that are not required to fill in packs
    @param hold_rx_dict:
    @param file_id:
    @return:
    """
    try:
        ext_hold_rx_list = list()
        for rx, note in hold_rx_dict.items():
            ext_hold_rx_list.append({"file_id": file_id, "ext_pharmacy_rx_no": rx, "ext_note": note})

        return ExtHoldRx.insert_multiple_ext_hold_rx_data(data_list=ext_hold_rx_list)
    except (IntegrityError, DataError, InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise

@log_args_and_response
def db_check_rx_on_hold_for_pack(pack_id: int):
    """

    @param pack_id:
    @return:
    """
    try:
        ext_hold_rx_dict = dict()
        query = PackDetails.select(PackDetails.id.alias("pack_id"),
                                   ExtHoldRx.ext_pharmacy_rx_no,
                                   ExtHoldRx.ext_note,
                                   ExtHoldRx.file_id).dicts()\
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(ExtHoldRx, on=ExtHoldRx.file_id == PackHeader.file_id)\
                .where(PackDetails.id == pack_id)

        for record in query:
            ext_hold_rx_dict[record['ext_pharmacy_rx_no']] = record['ext_note']

        return ext_hold_rx_dict
    except (IntegrityError, DataError, InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise