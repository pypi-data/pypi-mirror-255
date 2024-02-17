from typing import List, Any

from peewee import InternalError, IntegrityError, DataError, DoesNotExist, JOIN_LEFT_OUTER
import settings
from dosepack.utilities.utils import log_args_and_response
from src.model.model_canister_master import CanisterMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_pack_details import PackDetails
from src.model.model_pack_queue import PackQueue

logger = settings.logger


@log_args_and_response
def reserve_canister(batch_id, canister_id: int) -> tuple:
    """
    Add canisters in reserve_canister table
    @param canister_id:
    @param batch_id:
    @return:
    """
    try:
        return ReservedCanister.get_or_create(canister_id=canister_id, defaults=dict(batch_id=batch_id))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


def remove_reserved_canisters(canister_list: list, batch_id = None) -> int:
    """
    Method to remove canisters form reserved canisters model
    @param batch_id:
    @param canister_list:
    @return:
    """

    try:
        return ReservedCanister.db_remove_reserved_canister(canister_ids=canister_list, batch_id=batch_id)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_delete_reserved_canister(batch_id, device_ids=None):
    """
    Deletes canisters for given batch id and given robot ids
    This makes canister available for other systems and canister recommendation will consider this canister.

    @param batch_id:
    @param device_ids:
    :return:
    """
    try:
        if device_ids:
            query = PackAnalysis.select(PackAnalysisDetails.canister_id).distinct() \
                .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)
            canisters = query.where(PackAnalysis.batch_id == batch_id,
                                    PackAnalysisDetails.device_id << device_ids)

            logger.info(
                " In db_delete_reserved_canister, removing canisters {} for batch {} from devices {}".format(canisters,
                                                                                                             batch_id,
                                                                                                             device_ids))
            return ReservedCanister.delete() \
                .where(ReservedCanister.canister_id << canisters,
                       ReservedCanister.batch_id == batch_id) \
                .execute()
        else:
            return ReservedCanister.delete() \
                .where(ReservedCanister.batch_id == batch_id).execute()

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def db_update_available_canister(batch_id):
    """
    Finds canister not available in robot for batch id and marks it available for other system
    :param batch_id: int
    :return:
    """
    try:
        # sub query to find canister whose position was outside robot
        sub_q = PackAnalysis.select(PackAnalysisDetails.canister_id).distinct() \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(PackAnalysisDetails.device_id.is_null(True),
                   PackAnalysis.batch_id == batch_id,
                   PackAnalysisDetails.canister_id.is_null(False))

        # deleting entry from reserved_canister to mark it available for other systems
        ReservedCanister.delete() \
            .where(ReservedCanister.canister_id << sub_q,
                   ReservedCanister.batch_id == batch_id) \
            .execute()
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_reserved_canister_query(device_id: int, company_id: int) -> List[Any]:
    """
    Function to get reserved canister query
    @param company_id:
    @param device_id:
    """
    try:
        # get alternate drug canisters
        skip_canister_query = CanisterMaster.select(CanisterMaster.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(LocationMaster.device_id == device_id |
                   CanisterMaster.location_id.is_null(True) |
                   LocationMaster.is_disabled == True |
                   (DeviceMaster.device_type_id == settings.DEVICE_TYPES['CSR']))

        skip_canisters = [item.id for item in skip_canister_query]
        logger.info('In get_reserved_canister_query: skip_canister: {}'.format(skip_canisters))

        reserved_canisters = ReservedCanister.db_get_reserved_canister_query(company_id=company_id,
                                                                             skip_canisters=skip_canisters)
        return reserved_canisters

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_reserved_canister_query {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_reserved_canister_query {}".format(e))
        raise e


def db_update_available_canister_pack_queue(batch_id_list):
    """
    Finds canister not available in robot for batch id and marks it available for other system
    :param batch_id_list: list
    :return:
    """
    try:
        # sub query to find canister whose position was outside robot
        sub_q = PackAnalysis.select(PackAnalysisDetails.canister_id).distinct() \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackDetails, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(PackAnalysisDetails.device_id.is_null(True),
                   PackAnalysisDetails.canister_id.is_null(False))

        # deleting entry from reserved_canister to mark it available for other systems
        ReservedCanister.delete() \
            .where(ReservedCanister.canister_id << sub_q) \
            .execute()
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        raise e