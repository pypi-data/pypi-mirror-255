from typing import List
from peewee import InternalError, IntegrityError, DoesNotExist, JOIN_LEFT_OUTER
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import log_args_and_response, get_current_date_time
from src import constants
from src.dao.canister_dao import get_replenish_info_by_drug_usage_status, update_drug_usage_status_in_canister_tracker, \
    update_canister_expiry_date, get_canister_last_replenished_drug_dao, \
    db_get_last_canister_replenish_id_dao
from src.dao.drug_tracker_dao import get_drug_tracker_info_by_canister_ids, drug_tracker_create_multiple_record
from src.dao.pack_drug_dao import populate_pack_drug_tracker
from src.model.model_slot_details import SlotDetails
from src.dao.generate_canister_dao import get_canister_info_by_canister_id
from src.dao.canister_dao import update_canister_dao
from src.dao.drug_dao import db_update_drug_id_by_slot_id
from src.dao.canister_dao import get_replenish_info_by_drug_usage_status_in_reverse
from decimal import Decimal
logger = settings.logger


@log_args_and_response
def populate_drug_tracker(slot_transaction_info: List[dict]) -> bool:
    """
    Method used to populate drug tracker, as
    1.get replenish info from canister tracker table for required canisters.
    2.get details from drug tracker for tracking drug_quantity usage per replenish id.
    3.update drug tracker table from usage_consideration status of replenish id.
    @param slot_transaction_info:
    @return:
    """

    try:

        logger.debug(" In populate_drug_tracker..")

        canister_id_list: list = []
        drug_tracker_data: list = []
        drug_tracker_info: dict = dict()
        replenish_ids_done: list = []
        replenish_ids_pending: list = []

        for slot_data in slot_transaction_info:
            canister_id = slot_data["canister_id"]
            if canister_id not in canister_id_list:
                canister_id_list.append(canister_id)

        """
        Get replenish details for required canister_ids and filter out replenish id to use for drug_tracker table

        """
        canister_replenishment_to_use: dict = dict()
        replenish_ids_to_compensate_details: dict = dict()
        replenish_ids_used_for_compensation_details: dict = dict()
        replenish_ids_in_progress: list = []

        canister_tracker_info: dict = get_replenish_info_by_drug_usage_status(canister_ids=canister_id_list, status=[
            constants.USAGE_CONSIDERATION_PENDING,
            constants.USAGE_CONSIDERATION_IN_PROGRESS])

        logger.debug(" find_appropriate_replenish_id_from_canister_tracker_info..")

        for canister_id in canister_tracker_info:
            replenish_info = canister_tracker_info[canister_id]

            canister_replenishment_to_use, drug_tracker_info, replenish_ids_to_compensate_details, \
            replenish_ids_used_for_compensation_details, replenish_ids_in_progress, replenish_ids_done, replenish_ids_pending = \
                find_appropriate_replenish_id_from_canister_tracker_info(
                    canister_id=canister_id, replenish_info=replenish_info,
                    replenish_ids_to_compensate_details=replenish_ids_to_compensate_details,
                    replenish_ids_used_for_compensation_details=replenish_ids_used_for_compensation_details,
                    canister_replenishment_to_use=canister_replenishment_to_use,
                    replenish_ids_in_progress=replenish_ids_in_progress,
                    replenish_ids_pending=replenish_ids_pending,
                    replenish_ids_done=replenish_ids_done,
                    drug_tracker_info=drug_tracker_info)

        logger.debug(" canister_replenishment_to_use: {} ".format(str(canister_replenishment_to_use)))
        logger.debug(" replenish_ids_pending: {} ".format(str(replenish_ids_pending)))
        logger.debug(" replenish_ids_to_compensate_details: {} ".format(str(replenish_ids_to_compensate_details)))
        logger.debug(" replenish_ids_used_for_compensation_details: {} ".format(
            str(replenish_ids_used_for_compensation_details)))

        """
        Get info of drug tacker devices to track quantity usage by replenish id
        """
        if replenish_ids_in_progress:
            logger.debug(
                " find drug tracker info for replenish_ids_in_progress: {}".format(str(replenish_ids_in_progress)))

            response = get_drug_tracker_info_by_canister_ids(replenish_ids_in_progress)
            drug_tracker_info.update(response)

        logger.debug(" drug_tracker_info: {} ".format(str(drug_tracker_info)))

        created_date = get_current_date_time()

        for index, record in enumerate(slot_transaction_info):
            canister_id = record["canister_id"]
            dropped_qty = record["dropped_qty"]
            slot_id = record["slot_id"]

            if canister_id not in canister_replenishment_to_use:
                logger.error(" not found any fresh replenish record for canister id: {} ".format(str(canister_id)))
                # return False
                drug_tracker_record = dict()
                drug_tracker_record["canister_id"] = canister_id
                drug_tracker_record["slot_id"] = slot_id

                # get drug_id from last replenished canister tracker id if not found then
                # update canister_master's drug id
                drug_id = get_canister_last_replenished_drug_dao(canister_id)
                if not drug_id:
                    canister_data = get_canister_info_by_canister_id(canister_id)
                    drug_id = canister_data["drug_id"]

                drug_tracker_record["drug_id"] = drug_id
                drug_tracker_record["created_date"] = created_date
                drug_tracker_record["comp_canister_tracker_id"] = None
                drug_tracker_record["pack_id"] = record["pack_id"]
                drug_tracker_record["created_by"] = record["created_by"]
                drug_tracker_record["drug_quantity"] = dropped_qty
                drug_tracker_record["filled_at"] = settings.FILLED_AT_DOSE_PACKER

                replenish_data = db_get_last_canister_replenish_id_dao(canister_id=canister_id)
                drug_tracker_record["canister_tracker_id"] = replenish_data["canister_tracker_id"]
                drug_tracker_record["lot_number"] = replenish_data["lot_number"]
                drug_tracker_record["expiry_date"] = replenish_data["expiration_date"]
                drug_tracker_record['case_id'] = replenish_data["case_id"]

                drug_tracker_data.append(drug_tracker_record)
                continue

            if canister_id not in drug_tracker_info:
                logger.error(" Replenish records not enough for canister id: {} ".format(str(canister_id)))
                # return False

            drug_id = canister_replenishment_to_use[canister_id]["drug_id"]

            drug_tracker_record = dict()
            drug_tracker_record["canister_id"] = canister_id
            drug_tracker_record["slot_id"] = slot_id
            drug_tracker_record["drug_id"] = drug_id
            drug_tracker_record["created_date"] = created_date
            drug_tracker_record["comp_canister_tracker_id"] = None
            drug_tracker_record["pack_id"] = record["pack_id"]
            drug_tracker_record["created_by"] = record["created_by"]
            drug_tracker_record["filled_at"] = settings.FILLED_AT_DOSE_PACKER

            if "comp_canister_tracker_id" in canister_replenishment_to_use[canister_id]:
                compensated_replenish_id = canister_replenishment_to_use[canister_id]["comp_canister_tracker_id"]
                replenish_quantity = canister_replenishment_to_use[canister_id]["actual_quantity"]
                drug_tracker_record["comp_canister_tracker_id"] = compensated_replenish_id
            else:
                replenish_quantity = canister_replenishment_to_use[canister_id]["quantity"]

            quantity_used = drug_tracker_info[canister_id]["quantity_used"]
            replenish_id = drug_tracker_info[canister_id]["canister_tracker_id"]
            case_id = drug_tracker_info[canister_id]["case_id"]
            lot_number = drug_tracker_info[canister_id]["lot_number"]
            expiry_date = drug_tracker_info[canister_id]["expiry_date"]
            drug_tracker_record["canister_tracker_id"] = replenish_id
            drug_tracker_record["case_id"] = case_id
            drug_tracker_record["lot_number"] = lot_number
            drug_tracker_record["expiry_date"] = expiry_date

            if quantity_used + dropped_qty > replenish_quantity:

                logger.debug(" additional record required as dropped quantity exceeded replenish quantity, "
                             "canister_id: {}, slot_id: {}, quantity_used: {}, dropped_qty: {}, replenish_id: {} "
                             .format(str(canister_id), str(slot_id), str(quantity_used), str(dropped_qty),
                                     str(replenish_id))
                             )

                # used for creation record of additional entry in drug_tracker for same drug id and slot id
                additional_quantity = quantity_used + dropped_qty - replenish_quantity

                drug_tracker_record["drug_quantity"] = dropped_qty - additional_quantity
                drug_tracker_info[canister_id]["quantity_used"] += dropped_qty - additional_quantity

                # add new record with addition dropped pills
                duplicate_record = record
                duplicate_record["dropped_qty"] = additional_quantity
                slot_transaction_info.insert(index + 1, duplicate_record)

            else:
                drug_tracker_record["drug_quantity"] = dropped_qty
                drug_tracker_info[canister_id]["quantity_used"] += dropped_qty

            drug_tracker_data.append(drug_tracker_record)

            """
            Update usage_consideration status in CanisterTracker table if required (quantity_used=replenish_quantity),
            find fresh replenish id from canister_tracker_info and update it in canister_replenishment_to_use and drug_tracker_info
            """

            quantity_used = drug_tracker_info[canister_id]["quantity_used"]
            if quantity_used == replenish_quantity:

                logger.debug(" need to fetch fresh replenish for canister id: {} , current replenish id: {},"
                             " current_slot_id: {} ".format(str(canister_id), str(replenish_id), str(slot_id)))

                replenish_ids_done.append(replenish_id)

                if replenish_id in replenish_ids_pending:
                    replenish_ids_pending.remove(replenish_id)

                # To update usage_consideration status for compensated replenish id and also for replenish ids used for compensate it
                if "comp_canister_tracker_id" in canister_replenishment_to_use[canister_id]:
                    if canister_id in replenish_ids_used_for_compensation_details:
                        if drug_id in replenish_ids_used_for_compensation_details[canister_id]:
                            used_replenish_ids_for_compensation = \
                            replenish_ids_used_for_compensation_details[canister_id][drug_id]
                            replenish_ids_done += used_replenish_ids_for_compensation

                        del replenish_ids_used_for_compensation_details[canister_id]

                    compensated_replenish_id = canister_replenishment_to_use[canister_id]["comp_canister_tracker_id"]
                    replenish_ids_done.append(compensated_replenish_id)
                    del replenish_ids_to_compensate_details[canister_id]

                # remove from canister_replenishment_to_use, drug_tracker_info and replenish_ids_to_compensate_details
                del canister_replenishment_to_use[canister_id]
                del drug_tracker_info[canister_id]

                replenish_info = canister_tracker_info[canister_id]

                canister_replenishment_to_use, drug_tracker_info, replenish_ids_to_compensate_details, \
                replenish_ids_used_for_compensation_details, replenish_ids_in_progress, replenish_ids_done, replenish_ids_pending = \
                    find_appropriate_replenish_id_from_canister_tracker_info(
                        canister_id=canister_id, replenish_info=replenish_info,
                        replenish_ids_to_compensate_details=replenish_ids_to_compensate_details,
                        replenish_ids_used_for_compensation_details=replenish_ids_used_for_compensation_details,
                        canister_replenishment_to_use=canister_replenishment_to_use,
                        replenish_ids_in_progress=replenish_ids_in_progress,
                        replenish_ids_pending=replenish_ids_pending,
                        replenish_ids_done=replenish_ids_done,
                        drug_tracker_info=drug_tracker_info)

                logger.debug(" canister_replenishment_to_use: {} ".format(str(canister_replenishment_to_use)))
                logger.debug(" replenish_ids_pending: {} ".format(str(replenish_ids_pending)))
                logger.debug(
                    " replenish_ids_to_compensate_details: {} ".format(str(replenish_ids_to_compensate_details)))
                logger.debug(" replenish_ids_used_for_compensation_details: {} ".format(
                    str(replenish_ids_used_for_compensation_details)))
                logger.debug(" drug_tracker_info: {} ".format(str(drug_tracker_info)))

        with db.transaction():
            slot_details_data = list()
            for record in drug_tracker_data:
                slot_id = record["slot_id"]
                drug_id = record["drug_id"]
                slot_details_data.append({"slot_id": slot_id, "drug_id": drug_id})
            logger.info("In populate_drug_tracker: slot_details_data: {}".format(slot_details_data))

            pack_drug_tracker_details = db_update_drug_id_by_slot_id(slot_details_data)
            logger.info("In populate_drug_tracker: pack_drug_tracker_details: {}".format(pack_drug_tracker_details))

            if pack_drug_tracker_details:
                pack_drug_tracker_status = populate_pack_drug_tracker(pack_drug_tracker_details)

            status = drug_tracker_create_multiple_record(insert_dict=drug_tracker_data)
            logger.info("In populate_drug_tracker: record created in drug tracker: {}".format(status))
            if replenish_ids_pending:
                for canister_id, tracker_info in drug_tracker_info.items():
                    if tracker_info["quantity_used"] == 0:
                        canister_tracker_id = tracker_info['canister_tracker_id']
                        if canister_tracker_id in replenish_ids_pending:
                            replenish_ids_pending.remove(canister_tracker_id)

                logger.info("In populate_drug_tracker: remove_canister_tracker_ids: {}".format(replenish_ids_pending))
                if replenish_ids_pending:
                    # update canister tracker to change usage_consideration status from pending to progress
                    update_drug_usage_status_in_canister_tracker(replenish_ids=replenish_ids_pending,
                                                                 status=constants.USAGE_CONSIDERATION_IN_PROGRESS)
                    update_canister_expiry_date(tracker_ids=replenish_ids_pending)
            if replenish_ids_done:
                # update canister tracker to change usage_consideration status from progress to done
                update_drug_usage_status_in_canister_tracker(replenish_ids=replenish_ids_done,
                                                             status=constants.USAGE_CONSIDERATION_DONE)


    except StopIteration:
        return error(2001)
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)
    except ValueError as e:
        return error(2005, str(e))
    except Exception as e:
        raise e
    return True


def find_appropriate_replenish_id_from_canister_tracker_info(canister_id: int, replenish_info: list, replenish_ids_to_compensate_details: dict,
                                                             replenish_ids_used_for_compensation_details: dict, canister_replenishment_to_use: dict,
                                                             replenish_ids_in_progress: list, replenish_ids_pending: list, replenish_ids_done,
                                                             drug_tracker_info: dict) -> tuple:
    """
    This Func used for filter out replenish info by its usage_consideration status, maintain replenish_ids for compensation if required and
    also manage replenish ids for which we have to update usage_consideration status in canister tracker table

    @param canister_id: canister_id
    @param replenish_info: replenish details from canister tracker
    @param replenish_ids_to_compensate_details: maintain details of replenish_ids_to_compensate
    @param replenish_ids_used_for_compensation_details: maintain details of replenish_ids_used_for_compensation
    @param canister_replenishment_to_use: maintain details of replenish_id currently in use
    @param replenish_ids_in_progress: replenish_ids currently in progress
    @param replenish_ids_pending:  replenish_ids currently in pending
    @param replenish_ids_done:  replenish_ids in done state
    @param drug_tracker_info: drug_tracker info about drug_quantity used till now
    @return:
    """

    for record in replenish_info:
        quantity = record["quantity_adjusted"]
        replenish_id = record["id"]
        usage_status = record["usage_consideration"]
        drug_id = record["drug_id"]
        case_id = record["case_id"]
        lot_number = record["lot_number"]
        expiry_date = record["expiration_date"]

        if replenish_id in replenish_ids_done:
            continue

        if quantity < 0:
            if canister_id not in replenish_ids_to_compensate_details:
                replenish_ids_to_compensate_details[canister_id] = dict()

            logger.debug(" find correction replenish record with replenish id: {}".format(str(replenish_id)))
            replenish_ids_to_compensate_details[canister_id][drug_id] = {"quantity": -quantity, "replenish_id": replenish_id}

        else:
            canister_replenishment_to_use[canister_id] = {"quantity": quantity, "drug_id": drug_id, "replenish_id": replenish_id}

            if canister_id in replenish_ids_to_compensate_details:
                if drug_id in replenish_ids_to_compensate_details[canister_id]:

                    logger.debug(" replenish id {} with drug_id {} used for compensation ".format(str(replenish_id), str(drug_id)))

                    compensate_replenish_id = replenish_ids_to_compensate_details[canister_id][drug_id]["replenish_id"]
                    compensate_quantity = replenish_ids_to_compensate_details[canister_id][drug_id]["quantity"]

                    if quantity > compensate_quantity:
                        canister_replenishment_to_use[canister_id]["comp_canister_tracker_id"] = compensate_replenish_id
                        canister_replenishment_to_use[canister_id]["actual_quantity"] = quantity - compensate_quantity

                    elif quantity == compensate_quantity:

                        replenish_ids_done.append(replenish_id)

                        drug_id = canister_replenishment_to_use[canister_id]["drug_id"]
                        if canister_id in replenish_ids_used_for_compensation_details:
                            if drug_id in replenish_ids_used_for_compensation_details[canister_id]:
                                used_replenish_ids_for_compensation = replenish_ids_used_for_compensation_details[canister_id][drug_id]
                                replenish_ids_done += used_replenish_ids_for_compensation

                                del replenish_ids_used_for_compensation_details[canister_id][drug_id]

                        replenish_ids_done.append(compensate_replenish_id)

                        # remove from canister_replenishment_to_use and replenish_ids_to_compensate_details
                        del canister_replenishment_to_use[canister_id]
                        del replenish_ids_to_compensate_details[canister_id][drug_id]
                        logger.debug(" continue as compensate quantity = replenish quantity  ".format(str(replenish_id), str(drug_id)))

                        continue

                    else:
                        del canister_replenishment_to_use[canister_id]

                        if not canister_id in replenish_ids_used_for_compensation_details:
                            replenish_ids_used_for_compensation_details[canister_id] = dict()
                        if not drug_id in replenish_ids_used_for_compensation_details[canister_id]:
                            replenish_ids_used_for_compensation_details[canister_id][drug_id] = []

                        replenish_ids_used_for_compensation_details[canister_id][drug_id].append(replenish_id)

                        logger.debug(" added in replenish_ids_used_for_compensation_details ")

                        # update compensate quantity with quantity of current replenish quantity
                        compensate_quantity -= quantity
                        replenish_ids_to_compensate_details[canister_id][drug_id]["quantity"] = compensate_quantity

                        continue

            if usage_status == constants.USAGE_CONSIDERATION_IN_PROGRESS:
                replenish_ids_in_progress.append(replenish_id)
            else:
                replenish_ids_pending.append(replenish_id)
                drug_tracker_info[canister_id] = {"canister_id": canister_id, "quantity_used": 0,
                                                  "canister_tracker_id": replenish_id,
                                                  "case_id": case_id, "lot_number": lot_number,
                                                  "expiry_date": expiry_date}

            break

    return canister_replenishment_to_use, drug_tracker_info, replenish_ids_to_compensate_details, \
           replenish_ids_used_for_compensation_details, replenish_ids_in_progress, replenish_ids_done, replenish_ids_pending

@log_args_and_response
def get_appropriate_replenish_id_from_canister_tracker_info(canister_tracker_info,
                                                            canister_id,
                                                            required_quantity
                                                            ):

    try:
        logger.info("Inside get_appropriate_replenish_id_from_canister_tracker_info")
        replenish_id: list = list()
        remaining_required_quantity = required_quantity

        for canister_tracker_id, canister_tracker_data in canister_tracker_info.items():

            status = 0
            drug_tracker_data = get_drug_tracker_info_by_canister_ids([canister_tracker_id])

            if drug_tracker_data:
                quantity_used = drug_tracker_data[canister_id]["quantity_used"]
            else:
                quantity_used = 0

            logger.info(
                "In get_appropriate_replenish_id_from_canister_tracker_info: remaining_required_quantity: {}".format(
                    remaining_required_quantity
                ))

            logger.info("In get_appropriate_replenish_id_from_canister_tracker_info: quantity_used: {}".format(
                quantity_used
            ))

            for data in canister_tracker_data:

                quantity_adjusted = data["quantity_adjusted"]

                available_quantity_in_canister_tracker = quantity_adjusted - quantity_used
                logger.info("In get_appropriate_replenish_id_from_canister_tracker_info: "
                            "available_quantity_in_canister_tracker: {}".format(available_quantity_in_canister_tracker))

                if available_quantity_in_canister_tracker >= remaining_required_quantity:
                    if available_quantity_in_canister_tracker == remaining_required_quantity:
                        logger.info("In get_appropriate_replenish_id_from_canister_tracker_info:same_quantity")
                        canister_data = get_canister_info_by_canister_id(canister_id=canister_id)

                        available_quantity_in_canister_master = canister_data["available_quantity"]
                        available_quantity_in_canister_master -= remaining_required_quantity

                        logger.info(
                            "In get_appropriate_replenish_id_from_canister_tracker_info: "
                            "available_quantity_in_canister_master: {}".format(available_quantity_in_canister_master))

                        if available_quantity_in_canister_master < 0:
                            update_dict = {"available_quantity": 0}
                        else:
                            update_dict = {"available_quantity": available_quantity_in_canister_master}

                        update_status = update_canister_dao(update_dict, canister_id)

                        update_drug_usage_status_in_canister_tracker(replenish_ids=[canister_tracker_id],
                                                                     status=constants.USAGE_CONSIDERATION_DONE)

                        replenish_id.append({"replenish_id": canister_tracker_id, "count": remaining_required_quantity})
                        status = 1
                    else:
                        logger.info("In get_appropriate_replenish_id_from_canister_tracker_info: high_quantity")
                        canister_data = get_canister_info_by_canister_id(canister_id=canister_id)

                        available_quantity_in_canister_master = canister_data["available_quantity"]
                        available_quantity_in_canister_master -= remaining_required_quantity

                        test_quantity = float(available_quantity_in_canister_master)

                        if not test_quantity.is_integer():
                            available_quantity_in_canister_master = int(available_quantity_in_canister_master)

                        logger.info(
                            "In get_appropriate_replenish_id_from_canister_tracker_info: "
                            "available_quantity_in_canister_master: {}".format(available_quantity_in_canister_master))

                        if available_quantity_in_canister_master < 0:
                            update_dict = {"available_quantity": 0}
                        else:
                            update_dict = {"available_quantity": available_quantity_in_canister_master}

                        update_status = update_canister_dao(update_dict, canister_id)

                        replenish_id.append({"replenish_id": canister_tracker_id, "count": remaining_required_quantity})
                        status = 1
                    break

                elif available_quantity_in_canister_tracker < remaining_required_quantity and \
                        available_quantity_in_canister_tracker != 0:
                    logger.info(
                        "In get_appropriate_replenish_id_from_canister_tracker_info: low_quantity but no zero")
                    quantity = float(remaining_required_quantity) - float(available_quantity_in_canister_tracker)

                    canister_data = get_canister_info_by_canister_id(canister_id=canister_id)

                    available_quantity_in_canister_master = canister_data["available_quantity"]
                    available_quantity_in_canister_master -= available_quantity_in_canister_tracker
                    remaining_required_quantity = quantity

                    test_quantity = float(available_quantity_in_canister_master)

                    if not test_quantity.is_integer():
                        available_quantity_in_canister_master = int(available_quantity_in_canister_master)

                    logger.info(
                        "In get_appropriate_replenish_id_from_canister_tracker_info: "
                        "available_quantity_in_canister_master: {}".format(available_quantity_in_canister_master))

                    if available_quantity_in_canister_master < 0:
                        update_dict = {"available_quantity": 0}
                    else:
                        update_dict = {"available_quantity": available_quantity_in_canister_master}

                    update_status = update_canister_dao(update_dict, canister_id)

                    update_drug_usage_status_in_canister_tracker(replenish_ids=[canister_tracker_id],
                                                                 status=constants.USAGE_CONSIDERATION_DONE)
                    replenish_id.append({"replenish_id": canister_tracker_id,
                                         "count": available_quantity_in_canister_tracker
                                         }
                                        )
                    continue

                elif available_quantity_in_canister_tracker <= 0:
                    logger.info(
                        "In get_appropriate_replenish_id_from_canister_tracker_info: low_quantity")
                    update_drug_usage_status_in_canister_tracker(replenish_ids=[canister_tracker_id],
                                                                 status=constants.USAGE_CONSIDERATION_DONE)
                    continue

            if status:
                break

        if remaining_required_quantity > 0:
            logger.info(
                "In get_appropriate_replenish_id_from_canister_tracker_info: "
                "All the canister_tracker_ids are replenish_done")

            replenish_data = db_get_last_canister_replenish_id_dao(canister_id=canister_id)
            canister_tracker_id = replenish_data["canister_tracker_id"]

            canister_data = get_canister_info_by_canister_id(canister_id=canister_id)

            available_quantity_in_canister_master = canister_data["available_quantity"]
            available_quantity_in_canister_master -= remaining_required_quantity

            test_quantity = float(available_quantity_in_canister_master)

            if not test_quantity.is_integer():
                available_quantity_in_canister_master = int(available_quantity_in_canister_master)

            logger.info(
                "In get_appropriate_replenish_id_from_canister_tracker_info: "
                "available_quantity_in_canister_master: {}".format(available_quantity_in_canister_master))

            if available_quantity_in_canister_master < 0:
                update_dict = {"available_quantity": 0}
            else:
                update_dict = {"available_quantity": available_quantity_in_canister_master}

            update_status = update_canister_dao(update_dict, canister_id)
            replenish_id.append({"replenish_id": canister_tracker_id, "count": remaining_required_quantity})


        logger.info(
            "In get_appropriate_replenish_id_from_canister_tracker_info replenish_ids: {}".format(replenish_id))
        return replenish_id
    except Exception as e:
        logger.error("Error in get_appropriate_replenish_id_from_canister_tracker_info: {}".format(e))
        raise e


@log_args_and_response
def get_and_insert_canister_replenish_id_in_drug_tracker_data(args):
    """
    this function get and then set the canister_tracker_id in the drug_tracker_data for 11_digit_ndc_slot_wise flow
    """
    logger.info("In get_and_insert_canister_replenish_id_in_drug_tracker_data")
    try:
        canister_id = args["canister_id"]
        required_quantity = args["required_quantity"]
        drug_tracker_info_list = args["drug_tracker_info_list"]

        canister_id_list = [canister_id]
        canister_tracker_info = get_replenish_info_by_drug_usage_status_in_reverse\
            (canister_ids=canister_id_list,
             status=[constants.USAGE_CONSIDERATION_PENDING,
                     constants.USAGE_CONSIDERATION_IN_PROGRESS
                     ])

        logger.info("In get_and_insert_canister_replenish_id_in_drug_tracker_data: canister_tracker_info {}"
                    .format(canister_tracker_info))

        canister_data = get_canister_info_by_canister_id(canister_id=canister_id)
        available_quantity_in_canister_master = canister_data["available_quantity"]

        if available_quantity_in_canister_master < required_quantity:
            logger.error(
                "In drug_filled available_canister_quantity {} is less than required_quantity {}".format(
                    available_quantity_in_canister_master, required_quantity
                ))

        replenish_ids = get_appropriate_replenish_id_from_canister_tracker_info(
            canister_tracker_info=canister_tracker_info,
            canister_id=canister_id,
            required_quantity=required_quantity
        )
        logger.info("In get_and_insert_canister_replenish_id_in_drug_tracker_data: replenish_ids {}"
                    .format(replenish_ids))

        # code for add the canister_tracker_id in drug_tracker records
        record_count = 0
        for item in replenish_ids:

            count = 0
            used_count = 0
            canister_tracker_id = item["replenish_id"]
            used_count += item["count"]

            for i in range(record_count, len(drug_tracker_info_list)):
                record = drug_tracker_info_list[i]
                record["canister_tracker_id"] = canister_tracker_id
                quantity = record["drug_quantity"]
                count += quantity
                record_count += 1
                if count >= used_count:
                    logger.info("loop for replenish id break with count {} and used_count {}"
                                .format(count, used_count))
                    break

        return drug_tracker_info_list
    except Exception as e:
        logger.error("error in get_and_insert_canister_replenish_id_in_drug_tracker_data: {}".format(e))
        raise e

