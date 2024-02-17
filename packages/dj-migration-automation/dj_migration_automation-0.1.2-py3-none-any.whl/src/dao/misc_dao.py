import os
import sys
from typing import Optional, Dict, Any

import settings
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response, get_current_date

from src import constants

from src.model.model_overloaded_pack_timings import OverLoadedPackTiming
from src.model.model_pack_details import PackDetails
from peewee import InternalError, IntegrityError, DataError, JOIN_LEFT_OUTER, DoesNotExist, fn

from src.model.model_batch_master import BatchMaster
from src.model.model_celery_task_meta import CeleryTaskmeta
from src.model.model_company_setting import CompanySetting
from src.model.model_consumable_tracker import ConsumableTracker
from src.model.model_consumable_used import ConsumableUsed
from src.model.model_pack_queue import PackQueue
from src.model.model_system_setting import SystemSetting
from src.model.model_template_master import TemplateMaster

logger = settings.logger


def get_batch_id_for_pre_processing_wizard():
    """
    return batch id for Preprocessing wizard
    @return:
    """

    try:
        # get batch_id from batch_master in which batch_status in[34,35,58,130,36]
        query = BatchMaster.select(BatchMaster.id, BatchMaster.status, BatchMaster.sequence_no,
                                   BatchMaster.name, BatchMaster.system_id).dicts() \
            .join(PackDetails, on=PackDetails.batch_id == BatchMaster.id) \
            .where(BatchMaster.status.in_(constants.PRE_PROCESSING_MODULE_BATCH_STATUS) & (PackDetails.pack_status == settings.PENDING_PACK_STATUS))\
            .order_by(BatchMaster.id).limit(1)

        logger.info(f"Inside get_batch_id_for_pre_processing_wizard, query : {query}")

        for record in query:
            return record

    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_batch_id_for_pre_processing_wizard {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(f"Error in get_batch_id_for_pre_processing_wizard: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("Exception in get_batch_id_for_pre_processing_wizard {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(f"Exception in get_batch_id_for_pre_processing_wizard: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_sequence_no_for_pre_processing_wizard(sequence_no: int, batch_id: int) -> bool:
    """
    returns update requested canister status in Generate canister table
    :return:
    """
    try:
        status = BatchMaster.db_set_sequence(sequence_no=sequence_no, batch_id=batch_id)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("error in update_sequence_no_for_pre_processing_wizard {}".format(e))
        raise e


@log_args_and_response
def get_packs_count_for_latest_batch(batch_id: Optional[int] = None):
    """
    @return:get pack_count of the latest batch
    """
    try:
        if batch_id is None:
            count_of_packs = {"pack_count": 0, "batch_id": batch_id}
        else:
            total_packs = PackDetails.db_get_total_packs_count_for_batch(batch_id)
            # query = PackDetails.select(fn.COUNT(PackDetails.id)).where(PackDetails.batch_id == latest_batch_id)
            count_of_packs = {"pack_count": total_packs, "batch_id": batch_id}

        logger.info("In get_packs_count_for_latest_batch: count of packs {}".format(count_of_packs))
        return create_response(count_of_packs)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_packs_count_for_system(system_id: Optional[int] = None):
    """
    @return:get pack_count of the latest batch
    """
    try:

        query = PackDetails.select(fn.COUNT(PackDetails.id)).join(PackQueue, on=PackQueue.pack_id == PackDetails.id)\
                 .where(PackDetails.system_id == system_id)

        return query.scalar()

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def track_consumed_labels(quantity, company_id):
    """ Reduces consumed label quantity from consumable tracker and updates consumable used
    """
    consumed_data = dict()
    consumed_data[settings.CONSUMABLE_TYPE_LABEL] = quantity
    ConsumableTracker.db_remove_consumed_items(consumed_data, company_id)
    current_date = get_current_date()
    used_data = dict()
    used_data["used_quantity"] = quantity
    ConsumableUsed.db_update_or_create(company_id, settings.CONSUMABLE_TYPE_LABEL, current_date, used_data)


def get_queue_count(company_id):
    try:
        logger.info('count_query_start')
        count = TemplateMaster.select().dicts() \
            .join(CeleryTaskmeta, JOIN_LEFT_OUTER, on=CeleryTaskmeta.task_id == TemplateMaster.task_id) \
            .where(TemplateMaster.status == settings.PROGRESS_TEMPLATE_STATUS,
                   TemplateMaster.company_id == company_id,
                   CeleryTaskmeta.id.is_null(True)).count()
        logger.info('count_query_end')
        return count
    except (InternalError, IntegrityError) as e:
        logger.info(e)
        return None
    except DoesNotExist as e:
        logger.info(e)
        return 0


@log_args_and_response
def get_system_setting_by_system_id(system_id: int):
    """
    This function get system setting value by system id
    @param system_id:
    @return:
    """
    try:
        data_dict = SystemSetting.db_get_by_system_id(system_id)
        return data_dict

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in validate_canister_id_with_company_id {}".format(e))
        raise e


@log_args_and_response
def get_system_setting_info():
    """
    This function get system setting information
    @return:
    """
    try:
        return SystemSetting.db_get_system_setting_info()

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_system_setting_info {}".format(e))
        raise e


@log_args_and_response
def get_company_setting_data_by_company_id(company_id: int):
    """
    Fetches the data from the CompanySetting for the given company_id.
    """
    try:
        return CompanySetting.db_get_company_setting_data_by_company_id(company_id=company_id)

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_company_setting_data_by_company_id {}".format(e))
        raise e


@log_args_and_response
def system_setting_update_or_create_record(create_dict: dict, update_dict: dict) -> bool:
    """
    This function update or create record in system settings
    @param update_dict:
    @param create_dict:
    @return:
    """
    try:
        return SystemSetting.db_update_or_create_record(create_dict=create_dict, update_dict=update_dict)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in system_setting_update_or_create_record {}".format(e))
        raise e


@log_args_and_response
def update_company_setting_by_company_id(update_company_dict, company_id, name) -> bool:
    """
    This function update company settings by company id
    @param name:
    @param update_company_dict:
    @param company_id:
    @return:
    """
    try:
        return CompanySetting.db_update_company_setting_by_company_id(update_dict=update_company_dict, company_id=company_id, name=name)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_company_setting_by_company_id {}".format(e))
        raise e


@log_args_and_response
def company_setting_create_multiple_record(insert_dict):
    try:
        return CompanySetting.db_create_multi_record(insert_dict, CompanySetting)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in company_setting_create_multiple_record:  {}".format(e))
        raise e


@log_args_and_response
def get_company_setting_by_company_id(company_id: int) -> Dict[str, Any]:
    """
    Fetches the data from the CompanySetting for the given company_id.
    """
    try:
        return CompanySetting.db_get_by_company_id(company_id=company_id)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_add_overloaded_pack_timing_data_dao(insert_dict: list):
    """
    adds overloaded pack timing data in overloaded pack table
    """
    try:

        status = OverLoadedPackTiming.db_add_overloaded_pack_timing_data(insert_dict=insert_dict)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_add_overloaded_pack_timing_data_dao {}".format(e))
        raise e


