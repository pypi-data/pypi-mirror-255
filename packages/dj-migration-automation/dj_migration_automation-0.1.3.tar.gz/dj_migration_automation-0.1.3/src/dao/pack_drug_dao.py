from typing import Any

from peewee import InternalError, IntegrityError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate
from src.dao.pack_dao import verify_pack_id_by_system_id_dao
from src.model.model_error_details import ErrorDetails
from src.model.model_pack_canister_usage import PackCanisterUsage
from src.model.model_pack_drug_tracker import PackDrugTracker
from src.model.model_pack_error import PackError
from src.model.model_pack_fill_error_v2 import PackFillErrorV2
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_slot_transaction import SlotTransaction


logger = settings.logger


@log_args_and_response
def create_records_in_pack_drug_tracker(pack_drug_tracker_details: list) -> Any:
    """
    Method to create records in PackDrugTracker table
    @param pack_drug_tracker_details:
    @return:
    """
    try:

        resp = PackDrugTracker.db_insert_pack_drug_tracker_data(pack_drug_tracker_details)
        return resp
    except Exception as e:
        logger.error("Error in create_records_in_pack_drug_tracker {}".format(e))
        raise e


@log_args_and_response
def update_pack_rx_link_dao(update_dict: dict, pack_rx_link_id: list) -> bool:
    """
    This function to update pack rx link record
    @param update_dict:
    @param pack_rx_link_id:
    @return:

    """
    try:
        status = PackRxLink.db_update_pack_rx_link(update_dict=update_dict, pack_rx_link_id=pack_rx_link_id)
        return status

    except (InternalError, IntegrityError) as e:
        logger.error("Error in update_pack_rx_link_dao {}".format(e))
        raise e


@log_args_and_response
def populate_pack_drug_tracker(pack_drug_tracker_details: list) -> str:
    """
    This function here to create record of drug update in PackDrugTracker table
    @param pack_drug_tracker_details:
    @return:
    """

    try:

        response = create_records_in_pack_drug_tracker(pack_drug_tracker_details)
        create_response(response)

    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Error occurred while populate PackDrugTracker - " + str(e))


@validate(required_fields=["pack_id", "system_id"])
def delete_slot_transaction(pack_info):
    """
    Deletes slot transaction for pack id and related reported errors

    :param pack_info:
    :return: json
    """
    pack_id = pack_info["pack_id"]
    system_id = pack_info["system_id"]
    logger.debug("Received Pack ID {} and System ID {} to delete slot transaction"
                 .format(pack_id, system_id))

    valid_pack = verify_pack_id_by_system_id_dao(pack_id=pack_id, system_id=system_id)
    if not valid_pack:
        return error(1014)

    try:
        with db.transaction():
            status1 = SlotTransaction.db_delete_slot_transaction(pack_id)
            logger.debug("{} slot transaction rows deleted for pack id {}"
                         .format(status1, pack_id))
            pack_rx_ids = [item['id'] for item in PackRxLink.db_get(pack_id)]

            if pack_rx_ids:
                # Delete Error reported for pack as all slot transaction are deleted
                # for item in PackFillError.select() \
                #         .where(PackFillError.pack_rx_id << pack_rx_ids):
                #     logger.debug('Deleting reported fill error ID {}'
                #                  .format(item.id))
                #     status2 = item.delete_instance(recursive=True)
                #     logger.debug('Deleted {} records for fill error ID {}'
                #                  .format(status2, item.id))

                logger.debug('Deleting reported error for pack id {}'
                             .format(pack_id))
                # Below code is commented as deleting old PackError table and creating new
                # status3 = PackError.delete().where(PackError.pack_id == pack_id).execute()
                # logger.debug('Deleted {} reported error for pack id {}'
                #              .format(status3, pack_id))
            for item in PackFillErrorV2.select().where(PackFillErrorV2.pack_id == pack_id):
                status4 = item.delete_instance(recursive=True)
            logger.debug('Deleted errors reported for pack_id {}'.format(pack_id))
            status5 = PackCanisterUsage.delete().where(PackCanisterUsage.pack_id == pack_id).execute()
            logger.debug('Deleted {} canister usage data for pack_id {}'.format(status5, pack_id))
            status6 = ErrorDetails.delete().where(ErrorDetails.pack_id == pack_id).execute()
            logger.debug('Deleted {} errors summary for pack_id {}'.format(status6, pack_id))
        return create_response(status1)
    except (IntegrityError, InternalError):
        return error(2001)