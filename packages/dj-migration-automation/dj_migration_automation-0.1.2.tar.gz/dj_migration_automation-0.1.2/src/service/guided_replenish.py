import json
import math
import os
import sys
from collections import OrderedDict
from copy import deepcopy

import couchdb
from peewee import InternalError, DoesNotExist, IntegrityError, DataError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, get_current_modified_datetime, \
    log_args, get_canister_volume, get_max_possible_drug_quantities_in_canister
from dosepack.validation.validate import validate
from realtime_db.dp_realtimedb_interface import Database
from src import constants
from src.api_utility import calculate_max_possible_drug_quantity_in_refill_device
from src.dao.batch_dao import get_system_id_from_batch_id, get_batch_status, get_progress_batch_id, \
    validate_batch_id_dao
from src.dao.canister_dao import assign_cart_location_to_canister, update_canister_location \
    , check_canisters_present_in_cart, delete_canister_dao, get_available_trolley_data, \
    get_alternate_canister_for_batch_data, update_replenish_based_on_system, get_empty_locations_of_quadrant
from src.dao.couch_db_dao import get_couch_db_database_name, reset_couch_db_document
from src.dao.device_manager_dao import get_drawer_data_based_on_serial_number, get_max_locations_of_a_container, \
    get_max_drawers_per_device_based_on_device_id, get_max_locations_per_drawer_based_on_device_id, \
    get_robots_by_system_id_dao, get_location_data_from_device_ids, get_empty_locations_of_drawer, \
    get_location_info_from_location_id, validate_device_ids_with_company, verify_device_id_dao, \
    verify_device_id_list_dao
from src.dao.canister_transfers_dao import db_replace_canister_in_canister_transfers, \
    db_reserved_canister_replace_canister, get_slow_movers_for_device
from src.dao.drug_dao import get_fndc_txr_wise_inventory_qty
from src.dao.guided_replenish_dao import get_canister_transfer_to_trolley_guided, \
    get_canister_transfer_from_trolley_guided, get_canister_transfer_from_trolley_guided_csr, \
    get_guided_trolley_from_mini_batch, update_guided_tracker_location, update_guided_tracker_status, \
    update_guided_tracker, db_get_latest_guided_canister_transfer_data, \
    get_trolley_and_pending_devices_for_guided_transfer_to_trolley, \
    get_replaced_and_to_robot_skipped_canister_list, get_trolley_for_guided_transfer_from_trolley_csr, \
    get_trolley_for_guided_transfer_from_trolley, get_drawer_for_guided_transfer_to_trolley, \
    get_drawer_for_guided_transfer_from_trolley_csr, get_drawer_for_guided_transfer_from_trolley, \
    get_canister_to_be_replenished_next_dao, guided_cycle_status_for_update, \
    trolley_data_for_guided_tx, add_record_in_guided_meta, add_records_in_guided_tracker, \
    replace_canister_in_pack_analysis_details, fetch_guided_tracker_ids_based_on_destination_device, \
    fetch_guided_tracker_ids_by_destination_device_and_batch, \
    update_guided_meta_status_by_batch, get_serial_number_and_name_from_device, \
    get_pending_transfer_from_trolley_to_robot, get_transfer_cycle_drug_data, \
    get_next_cycle_id, get_system_device_for_batch, get_empty_drawer_data_with_locations, \
    fetch_empty_locations_count_quadrant_wise_based_on_device_ids, get_canisters_to_be_removed_from_robot, \
    get_transferred_canisters_of_robot_to_trolley, db_get_existing_guided_canister_transfer_data, \
    add_data_in_guided_transfer_history_tables, get_out_of_stock_tx_ids, add_data_in_guided_transfer_cycle_history, \
    get_pending_canister_transfer_from_trolley_guided, get_pending_canister_transfer_to_trolley_guided, \
    get_guided_tracker_based_on_status, get_pending_transfer_from_trolley_to_csr, \
    check_if_guided_replenish_exist_for_batch, add_data_in_guided_misplaced_canister, \
    get_guided_misplaced_canister_data, get_container_data_from_display_location, \
    guided_transfer_couch_db_timestamp_update, get_location_details_by_canister_id, check_if_canister_data_exit_dao, \
    db_delete_canister_data_dao, validate_guided_tx_cycle_id_dao, get_system_id_from_guided_tx_cycle_id
from src.dao.mfd_canister_dao import get_mfd_trolley_drawer_data, get_device_id_from_drawer_serial_number, \
    get_device_id_from_serial_number, get_drawer_id_from_serial_number
from src.dao.pack_analysis_dao import get_canister_drug_quantity_required_in_batch, db_get_drop_time
from src.dao.pack_dao import get_filling_pending_pack_ids, check_pending_canister_transfers, \
    check_packs_in_pack_queue_for_system, get_system_id_from_pack_queue
from src.dao.reserve_canister_dao import reserve_canister, remove_reserved_canisters
from src.exceptions import RealTimeDBException
from src.service.csr import recommend_csr_location, guided_recommend_csr_drawers_to_unlock
from src.service.misc import update_guided_tx_meta_data_in_couch_db, get_replenish_list_of_device
from utils.drug_inventory_webservices import get_current_inventory_data

logger = settings.logger


@log_args_and_response
def update_couch_db_of_to_trolley_done_devices(device_id: int, system_id: int) -> bool:
    """
    Function to CSR device for which guided transfer_to_trolley is done and update couch db timestamp for them
    @param system_id:
    @param batch_id:
    @param device_id:
    @return:
    """
    logger.info("Inside update_couch_db_of_to_trolley_done_devices")
    try:
        # get system_device_dict from given batch_id to update their couch db
        system_device_dict = get_system_device_for_batch()
        for system, device_list in system_device_dict.items():
            # not update couch db of input system i.e transfer ongoing on that system
            if system == system_id:
                continue
            for device in device_list:
                # update timestamp in couch db to get updated pending device list
                couch_db_update = guided_transfer_couch_db_timestamp_update(system_id=system,
                                                                            device_id=device)
                logger.info("update_couch_db_of_to_trolley_done_devices status {}".format(couch_db_update))

        return True

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("error in update_couch_db_of_to_trolley_done_devices {}".format(e))
        return False


@log_args_and_response
@validate(required_fields=["device_id", "company_id", "guided_tx_cycle_id", "system_id"])
def guided_cart_data_from_device_transfer(args: dict) -> dict:
    """
    Function to get canister transfers from given device in guided transfer flow
    @param args: dict
    @return: json
    """
    try:

        device_id = int(args["device_id"])
        company_id = int(args["company_id"])
        guided_tx_cycle_id = int(args["guided_tx_cycle_id"])
        system_id = int(args["system_id"])
        from_app = args.get("from_app", False)

        # first validate company id ,system id , batch id , device id then convert it to int otherwise it gives 500 error
        valid_device_with_company_id = validate_device_ids_with_company(device_ids=[args["device_id"]],
                                                                        company_id=args["company_id"])
        if not valid_device_with_company_id:
            return error(9059)

        valid_device_with_system_id = verify_device_id_list_dao(device_id=[args["device_id"]], system_id=args["system_id"])
        if not valid_device_with_system_id:
            return error(1015)

        validate_guided_tx_cycle_id = validate_guided_tx_cycle_id_dao(guided_tx_cycle_id=guided_tx_cycle_id)
        if not validate_guided_tx_cycle_id:
            return error(14016)

        response = dict()

        mini_batch_trolley = get_guided_trolley_from_mini_batch(guided_tx_cycle_id)

        #  to get trolley id in which canister are to be transferred from given device
        response['trolley_id'], pending_devices = get_trolley_and_pending_devices_for_guided_transfer_to_trolley(
            device_id=device_id,
            guided_tx_cycle_id=guided_tx_cycle_id,
            trolley_id=mini_batch_trolley)

        if response['trolley_id']:
            response['trolley_serial_number'], response['trolley_name'], response[
                'device_type_name'], response['device_type_id'] = get_serial_number_and_name_from_device(
                response['trolley_id'])

            if from_app:
                response['drawer_data'] = get_drawer_for_guided_transfer_to_trolley(device_id=device_id,
                                                                                    guided_tx_cycle_id=guided_tx_cycle_id,
                                                                                    trolley_id=response['trolley_id'])
            else:
                response['drawer_data'] = get_mfd_trolley_drawer_data(response['trolley_id'])

        pending_devices_copy = deepcopy(pending_devices)
        # check if trolley id is null and pending device is not null then check for replenish queue
        if not response["trolley_id"] and pending_devices_copy:
            logger.info(
                "In guided_cart_data_from_device_transfer: Transfer from device {} is completed and pending from another device"
                " so now checking whether replenish required in pending device or not".format(device_id))

            for i, pending_device in enumerate(pending_devices_copy):
                if pending_device["pending_device_type_id"] != settings.DEVICE_TYPES["ROBOT"]:
                    # if pending device is other than robot then no need to check replenish queue
                    continue
                pending_device_id = pending_device["pending_device_id"]
                pending_device_system_id = pending_device["pending_device_system_id"]
                if not pending_device_system_id:
                    return error(1000, "Invalid system_id for device {}".format(pending_device_id))

                replenish_list = get_replenish_list_of_device(device_id=pending_device_id,
                                                              system_id=pending_device_system_id)

                if not replenish_list:
                    # No transfer in pending device so change the status of all pending canisters to return to CSR.
                    all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids = \
                        fetch_guided_tracker_ids_based_on_destination_device(
                            dest_device_id=pending_device_id,
                            guided_tx_cycle_id=guided_tx_cycle_id,
                            transfer_status_list=constants.guided_tracker_to_trolley_status_list)
                    if source_guided_tracker_ids:
                        update_status = update_guided_tracker_status(guided_tracker_ids=source_guided_tracker_ids,
                                                                     status=constants.GUIDED_TRACKER_TRANSFER_AND_REPLENISH_SKIPPED)
                        logger.info("In guided_cart_data_from_device_transfer: guided status updated for source guided_tracker_id: {} "
                            "to GUIDED_TRACKER_TRANSFER_AND_REPLENISH_SKIPPED: {}".format(source_guided_tracker_ids,
                                                                                          update_status))

                    if alt_guided_tracker_ids:
                        update_status = update_guided_tracker_status(guided_tracker_ids=alt_guided_tracker_ids,
                                                                     status=constants.GUIDED_TRACKER_TRANSFER_SKIPPED)
                        logger.info("In guided_cart_data_from_device_transfer: guided status updated for alt guided_tracker_id: {} "
                            "to GUIDED_TRACKER_TRANSFER_SKIPPED: {}".format(source_guided_tracker_ids,
                                                                            update_status))

                    # remove pending device for which no more replenish required
                    pending_devices.pop(i)

            done_device_couch_db_update = update_couch_db_of_to_trolley_done_devices(device_id=device_id,
                                                                                     system_id=system_id)
            logger.info("guided_cart_data_from_device_transfer done_device_couch_db_update {}".format(
                done_device_couch_db_update))

        response["pending_devices"] = pending_devices

        return create_response(response)

    except InternalError as e:
        logger.error(e)
        return error(2001)

    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting canister transfer to trolley: " + str(e))


@log_args_and_response
@validate(
    required_fields=["device_id", "company_id", "guided_tx_cycle_id", "system_id", "trolley_serial_number"])
def guided_drawer_data_from_device_transfer(args: dict) -> dict:
    """
    Function to get canister transfers from given device in guided transfer flow
    @param args: dict
    @return: json
    """
    logger.info("In guided_transfer_to_trolley")

    try:

        device_id = int(args["device_id"])
        company_id = int(args["company_id"])
        guided_tx_cycle_id = int(args["guided_tx_cycle_id"])
        system_id = int(args["system_id"])
        # batch_id = int(args["batch_id"])
        trolley_serial_number = args.get("trolley_serial_number", None)

        # first validate company id ,system id , batch id , device id then convert it to int otherwise it gives 500 error
        valid_device_with_company_id = validate_device_ids_with_company(device_ids=[args["device_id"]],
                                                                        company_id=args["company_id"])
        if not valid_device_with_company_id:
            return error(9059)

        valid_device_with_system_id = verify_device_id_list_dao(device_id=[args["device_id"]], system_id=args["system_id"])
        if not valid_device_with_system_id:
            return error(1015)

        validate_guided_tx_cycle_id = validate_guided_tx_cycle_id_dao(guided_tx_cycle_id=guided_tx_cycle_id)
        if not validate_guided_tx_cycle_id:
            return error(14016)

        # transfer_data = list()
        # drawers_to_unlock = None
        response = dict()

        # Function to get trolley id and drawer id from their serial numbers
        trolley_id, drawer_id = get_trolley_drawer_from_serial_number(trolley_serial_number=trolley_serial_number,
                                                                      drawer_serial_number=None,
                                                                      company_id=company_id)

        drawer_list = get_drawer_for_guided_transfer_to_trolley(device_id=device_id,
                                                                guided_tx_cycle_id=guided_tx_cycle_id,
                                                                trolley_id=trolley_id)
        response['drawer_list'] = drawer_list

        if len(drawer_list):
            drawer_serial_number = drawer_list[0]['serial_number']
            drawer_id_db = drawer_list[0]['container_id']
        else:
            drawer_serial_number = 0
            drawer_id_db = 0
        couch_db_update_args = {
            "device_id": device_id,
            "system_id": system_id,
            "drawer_id": drawer_id_db,
            "drawer_serial_number": drawer_serial_number
        }

        couch_db_update_status = update_scanned_drawer_in_guided_tx_couch_db_doc(couch_db_update_args)
        response["couch_db_update"] = couch_db_update_status
        logger.info("In guided_drawer_data_from_device_transfer: response guided_drawer_data_from_device_transfer {}".format(
                response))
        return create_response(response)

    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting canister transfer to trolley")


@log_args_and_response
@validate(required_fields=["device_id", "company_id", "guided_tx_cycle_id", "system_id",
                           "drawer_serial_number"])
def guided_canister_data_from_device_transfer(args: dict) -> dict:
    """
    Function to get canister transfers from given device in guided transfer flow
    @param args: dict
    @return: json
    """

    trolley_serial_number = args.get("trolley_serial_number", None)
    drawer_serial_number = args["drawer_serial_number"]
    from_app = args.get("from_app", False)
    # transfer_data = list()
    # drawers_to_unlock = dict()
    response = dict()

    try:

        # first validate company id ,system id , batch id , device id then convert it to int otherwise it gives 500 error
        valid_device_with_company_id = validate_device_ids_with_company(device_ids=[args["device_id"]],
                                                                        company_id=args["company_id"])
        if not valid_device_with_company_id:
            return error(9059)

        valid_device_with_system_id = verify_device_id_list_dao(device_id=[args["device_id"]], system_id=args["system_id"])
        if not valid_device_with_system_id:
            return error(1015)

        validate_guided_tx_cycle_id = validate_guided_tx_cycle_id_dao(guided_tx_cycle_id=args["guided_tx_cycle_id"])
        if not validate_guided_tx_cycle_id:
            return error(14016)

        device_id = int(args["device_id"])
        company_id = int(args["company_id"])
        mini_batch = int(args["guided_tx_cycle_id"])
        system_id = int(args["system_id"])

        # Function to get trolley id and drawer id from their serial numbers
        if from_app:
            trolley_id = get_device_id_from_drawer_serial_number(drawer_serial_number=drawer_serial_number,
                                                                 company_id=company_id)
        else:
            trolley_id = get_device_id_from_serial_number(serial_number=trolley_serial_number, company_id=company_id)

        try:
            logger.info("In guided_canister_data_from_device_transfer: fetching drawer data based on drawer_serial_number")

            drawer_data = get_drawer_data_based_on_serial_number(drawer_serial_number=drawer_serial_number,
                                                                 company_id=company_id)
            drawer_id = drawer_data["id"]
            trolley_drawer_name = drawer_data["drawer_name"]
            logger.info("IN guided_canister_data_from_device_transfer: fetched drawer data: " + str(drawer_data))

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return error(3007, " or company_id")
        # to get canister list of given trolley and drawer that are to be transferred from given device
        transfer_data, drawers_to_unlock, delicate_drawers_to_unlock, couch_db_canister = get_canister_transfer_to_trolley_guided(
            company_id=company_id,
            device_id=device_id,
            mini_batch=mini_batch,
            trolley_id=trolley_id,
            drawer_id=drawer_id)

        response["trolley_drawer_name"] = trolley_drawer_name
        response['transfer_data'] = transfer_data
        response['regular_drawers_to_unlock'] = list(drawers_to_unlock.values())
        response['couch_db_canister'] = couch_db_canister
        if delicate_drawers_to_unlock:
            response['delicate_drawers_to_unlock'] = list(delicate_drawers_to_unlock.values())

        couch_db_update_args = {
            "device_id": device_id,
            "system_id": system_id,
            "drawer_id": drawer_id,
            "drawer_serial_number": drawer_serial_number
        }
        couch_db_update_status = update_scanned_drawer_in_guided_tx_couch_db_doc(couch_db_update_args)
        response["couch_db_update"] = couch_db_update_status
        return create_response(response)

    except RealTimeDBException as e:
        return error(2005, " - " + str(e))
    except(InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting canister transfer to trolley: " + str(e))


@log_args_and_response
@validate(required_fields=["device_id", "company_id", "guided_tx_cycle_id", "system_id"])
def guided_cart_data_to_device_transfer(args):
    """
    Function to get canister transfers from trolley in guided trasnfer flow
    @param args: dict
    @return: json
    """
    try:
        # first validate company id ,system id , batch id , device id then convert it to int otherwise it gives 500 error
        valid_device_with_company_id = validate_device_ids_with_company(device_ids=[args["device_id"]],
                                                                        company_id=args["company_id"])
        if not valid_device_with_company_id:
            return error(9059)

        valid_device_with_system_id = verify_device_id_list_dao(device_id=[args["device_id"]], system_id=args["system_id"])
        if not valid_device_with_system_id:
            return error(1015)

        validate_guided_tx_cycle_id = validate_guided_tx_cycle_id_dao(guided_tx_cycle_id=args["guided_tx_cycle_id"])
        if not validate_guided_tx_cycle_id:
            return error(14016)

        device_id = int(args["device_id"])
        company_id = int(args["company_id"])
        system_id = args["system_id"]
        mini_batch = int(args["guided_tx_cycle_id"])
        device_type = args.get("device_type", None)
        from_app = args.get("from_app", False)
        response = dict()

        #  to get trolley id in which canister are to be transferred in given device
        mini_batch_trolley = get_guided_trolley_from_mini_batch(mini_batch)

        if device_type and device_type == settings.DEVICE_TYPES_NAMES['CSR']:
            canister_list_csr = get_replaced_canister_list_and_assign_csr_location(device_id,
                                                                                   company_id,
                                                                                   system_id,
                                                                                   mini_batch)

            logger.info(canister_list_csr)
            guided_canister_status = constants.guided_tracker_to_csr_status_list
            response['trolley_id'] = get_trolley_for_guided_transfer_from_trolley_csr(device_id=device_id,
                                                                                      mini_batch=mini_batch,
                                                                                      mini_batch_trolley=mini_batch_trolley,
                                                                                      guided_canister_status=guided_canister_status,
                                                                                      canister_list_csr=canister_list_csr)
            pending_devices = get_pending_transfer_from_trolley_to_csr(mini_batch=mini_batch,
                                                                       trolley_id=mini_batch_trolley,
                                                                       guided_canister_status=guided_canister_status,
                                                                       system_id=system_id)

        else:
            guided_canister_status = constants.guided_tracker_to_robot_status_list
            response['trolley_id'] = get_trolley_for_guided_transfer_from_trolley(device_id=device_id,
                                                                                  mini_batch=mini_batch,
                                                                                  mini_batch_trolley=mini_batch_trolley,
                                                                                  guided_canister_status=guided_canister_status)
            pending_devices = get_pending_transfer_from_trolley_to_robot(mini_batch=mini_batch,
                                                                         trolley_id=mini_batch_trolley,
                                                                         guided_canister_status=guided_canister_status,
                                                                         system_id=system_id)

        if response['trolley_id']:
            response['trolley_serial_number'], response['trolley_name'], response[
                'device_type_name'], response['device_type_id'] = get_serial_number_and_name_from_device(
                response['trolley_id'])

            if from_app:
                if device_type and device_type == settings.DEVICE_TYPES_NAMES['CSR']:
                    response['drawer_data'] = get_drawer_for_guided_transfer_from_trolley_csr(device_id=device_id,
                                                                                              mini_batch=mini_batch,
                                                                                              trolley_id=response[
                                                                                                  'trolley_id'],
                                                                                              guided_canister_status=guided_canister_status)
                else:
                    response['drawer_data'] = get_drawer_for_guided_transfer_from_trolley(device_id=device_id,
                                                                                          mini_batch=mini_batch,
                                                                                          trolley_id=response[
                                                                                              'trolley_id'],
                                                                                          guided_canister_status=guided_canister_status)
            else:
                response['drawer_data'] = get_mfd_trolley_drawer_data(response['trolley_id'])

        # Commenting below code to resolve production issue(replenish not required in a robot but
        # already replenished canister is required to be transferred in Robot)

        # logger.info("guided_cart_data_to_device_transfer: checking whether tx to current device is completed or not")
        # pending_devices_copy = deepcopy(pending_devices)
        # # check for device type other than csr i.e., robot if trolley id is null and something in pending device
        # if (not device_type or (device_type and device_type != settings.DEVICE_TYPES_NAMES['CSR'])) \
        #         and not response["trolley_id"] and pending_devices_copy:
        #     logger.info("Transfer from current device completed and pending from another device"
        #                  " so now checking whether replenish required in pending device or not")
        #
        #     for i, pending_device_data in enumerate(pending_devices_copy):
        #         pending_device_id = pending_device_data["pending_device_id"]
        #         pending_device_system_id = pending_device_data["pending_device_system_id"]
        #         replenish_list = get_replenish_list_of_device(device_id=pending_device_id,
        #                                                       system_id=pending_device_system_id)
        #
        #         if not replenish_list:
        #             # No transfer in pending device so change the status of all pending canisters to return back to CSR.
        #             all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids = \
        #                 fetch_guided_tracker_ids_based_on_destination_device(dest_device_id=pending_device_id,
        #                                                                      guided_tx_cycle_id=mini_batch,
        #                                                                      transfer_status_list=constants.guided_tracker_to_robot_status_list)
        #             if all_guided_tracker_ids:
        #                 update_status = update_guided_tracker_status(guided_tracker_ids=all_guided_tracker_ids,
        #                                                              status=constants.GUIDED_TRACKER_TRANSFER_SKIPPED)
        #
        #             # remove pending device for which no more replenish required
        #             pending_devices.pop(i)
        response['pending_devices'] = pending_devices
        logger.info("In guided_cart_data_to_device_transfer: Response of guided_cart_data_to_device_transfer {}".format(
            response))
        return create_response(response)

    except InternalError as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting canister transfers form trolley")


@log_args_and_response
@validate(
    required_fields=["device_id", "company_id", "guided_tx_cycle_id", "system_id", "trolley_serial_number"])
def guided_drawer_data_to_device_transfer(args):
    """
    Function to get canister transfers from trolley in guided trasnfer flow
    @param args: dict
    @return: json
    """
    logger.info("In guided_transfer_from_trolley")
    mini_batch = int(args["guided_tx_cycle_id"])
    trolley_serial_number = args.get("trolley_serial_number", None)
    device_type = args.get("device_type", None)
    response = dict()

    try:
        # first validate company id ,system id , batch id , device id then convert it to int otherwise it gives 500 error
        valid_device_with_company_id = validate_device_ids_with_company(device_ids=[args["device_id"]],
                                                                        company_id=args["company_id"])
        if not valid_device_with_company_id:
            return error(9059)

        valid_device_with_system_id = verify_device_id_list_dao(device_id=[args["device_id"]], system_id=args["system_id"])
        if not valid_device_with_system_id:
            return error(1015)

        validate_guided_tx_cycle_id = validate_guided_tx_cycle_id_dao(guided_tx_cycle_id=mini_batch)
        if not validate_guided_tx_cycle_id:
            return error(14016)

        device_id = int(args["device_id"])
        company_id = int(args["company_id"])
        system_id = args["system_id"]

        trolley_id, drawer_id = get_trolley_drawer_from_serial_number(trolley_serial_number=trolley_serial_number,
                                                                      drawer_serial_number=None,
                                                                      company_id=company_id)

        #  to get containers of given trolley in which canisters are to be transferred in given device
        if device_type and device_type == settings.DEVICE_TYPES_NAMES['CSR']:
            guided_canister_status = constants.guided_tracker_to_csr_status_list

            drawer_list = get_drawer_for_guided_transfer_from_trolley_csr(device_id=device_id,
                                                                          mini_batch=mini_batch,
                                                                          trolley_id=trolley_id,
                                                                          guided_canister_status=guided_canister_status)
            response['drawer_list'] = drawer_list

        else:
            guided_canister_status = constants.guided_tracker_to_robot_status_list
            drawer_list = get_drawer_for_guided_transfer_from_trolley(device_id=device_id,
                                                                      mini_batch=mini_batch,
                                                                      trolley_id=trolley_id,
                                                                      guided_canister_status=guided_canister_status)
            response['drawer_list'] = drawer_list

        if len(drawer_list):
            drawer_serial_number = drawer_list[0]['serial_number']
            drawer_id_db = drawer_list[0]['container_id']
        else:
            drawer_serial_number = 0
            drawer_id_db = 0
        couch_db_update_args = {
            "device_id": device_id,
            "system_id": system_id,
            "drawer_id": drawer_id_db,
            "drawer_serial_number": drawer_serial_number
        }

        couch_db_update_status = update_scanned_drawer_in_guided_tx_couch_db_doc(couch_db_update_args)
        response["couch_db_update"] = couch_db_update_status
        logger.info("guided_drawer_data_to_device_transfer: Response of guided_drawer_data_to_device_transfer {}".format(
                response))
        return create_response(response)

    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting canister transfers form trolley")


@log_args_and_response
@validate(required_fields=["device_id", "company_id", "guided_tx_cycle_id", "system_id",
                           "drawer_serial_number"])
def guided_canister_data_to_device_transfer(args):
    """
    Function to get canister transfers from trolley in guided trasnfer flow
    @param args: dict
    @return: json
    """
    logger.info("In guided_transfer_from_trolley")
    mini_batch = int(args["guided_tx_cycle_id"])
    trolley_serial_number = args.get("trolley_serial_number", None)
    drawer_serial_number = args["drawer_serial_number"]
    device_type = args.get("device_type", None)
    from_app = args.get("from_app", False)
    # transfer_data = list()
    drawer_to_unlock = dict()
    response = dict()
    # dest_quad = None
    delicate_drawers_to_unlock = {}
    try:
        # first validate company id ,system id , batch id , device id then convert it to int otherwise it gives 500 error
        valid_device_with_company_id = validate_device_ids_with_company(device_ids=[args["device_id"]],
                                                                        company_id=args["company_id"])
        if not valid_device_with_company_id:
            return error(9059)

        valid_device_with_system_id = verify_device_id_list_dao(device_id=[args["device_id"]], system_id=args["system_id"])
        if not valid_device_with_system_id:
            return error(1015)

        validate_guided_tx_cycle_id = validate_guided_tx_cycle_id_dao(guided_tx_cycle_id=mini_batch)
        if not validate_guided_tx_cycle_id:
            return error(14016)

        device_id = int(args["device_id"])
        company_id = int(args["company_id"])
        system_id = args["system_id"]

        if from_app:
            trolley_id = get_device_id_from_drawer_serial_number(drawer_serial_number=drawer_serial_number,
                                                                 company_id=company_id)

        else:
            trolley_id = get_device_id_from_serial_number(serial_number=trolley_serial_number, company_id=company_id)

        try:
            logger.info(
                "In guided_canister_data_to_device_transfer: fetching drawer data based on drawer_serial_number")
            drawer_data = get_drawer_data_based_on_serial_number(drawer_serial_number=drawer_serial_number,
                                                                 company_id=company_id)
            drawer_id = drawer_data["id"]
            trolley_drawer_name = drawer_data["drawer_name"]
            logger.info("In guided_canister_data_to_device_transfer: fetched drawer data: " + str(drawer_data))

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return error(3007, " or company_id")

        # to get canister list of given trolley and drawer that are to be transferred in given device
        if device_type and device_type == settings.DEVICE_TYPES_NAMES['CSR']:

            guided_canister_status = constants.guided_tracker_to_csr_status_list

            transfer_data, canister_ids = get_canister_transfer_from_trolley_guided_csr(company_id=company_id,
                                                                                        device_id=device_id,
                                                                                        mini_batch=mini_batch,
                                                                                        trolley_id=trolley_id,
                                                                                        drawer_id=drawer_id,
                                                                                        guided_canister_status=
                                                                                        guided_canister_status)

            if transfer_data and canister_ids:
                logger.info("guided_canister_data_to_device_transfer: finding transfer data and canister ids")

                drawer_to_unlock, transfer_data = guided_recommend_csr_drawers_to_unlock(company_id=company_id,
                                                                                         canister_id_list=canister_ids,
                                                                                         device_id=device_id,
                                                                                         transfer_data=transfer_data)


        else:
            guided_canister_status = constants.guided_tracker_to_robot_status_list
            transfer_data, dest_quad, canister_type_dict = get_canister_transfer_from_trolley_guided(
                company_id=company_id,
                device_id=device_id,
                mini_batch=mini_batch,
                trolley_id=trolley_id,
                drawer_id=drawer_id,
                guided_canister_status=guided_canister_status)
            if transfer_data:
                drawer_to_unlock,delicate_drawers_to_unlock, locations_for_small_canisters, locations_for_big_canisters,locations_for_delicate_canisters = \
                    get_empty_drawer_data_with_locations(device_id=device_id, quadrant=dest_quad,
                                                         canister_type_dict=canister_type_dict)
                for container_name, data in drawer_to_unlock.items():
                    if "empty_locations" in data:
                        drawer_to_unlock[container_name]["from_device"] = list()
                        drawer_to_unlock[container_name]["to_device"] = data.pop("empty_locations")
                    else:
                        drawer_to_unlock[container_name]["from_device"] = list()
                        drawer_to_unlock[container_name]["to_device"] = list()
                for container_name, data in delicate_drawers_to_unlock.items():
                    if "empty_locations" in data:
                        delicate_drawers_to_unlock[container_name]["from_device"] = list()
                        delicate_drawers_to_unlock[container_name]["to_device"] = data.pop("empty_locations")
                    else:
                        delicate_drawers_to_unlock[container_name]["from_device"] = list()
                        delicate_drawers_to_unlock[container_name]["to_device"] = list()

                # map recommended empty loc to each canister data based on canister type
                for canister in transfer_data:
                    if canister["canister_type"] == settings.SIZE_OR_TYPE["SMALL"] and\
                            (locations_for_small_canisters or locations_for_delicate_canisters):
                        if canister['is_delicate'] and locations_for_delicate_canisters:
                            canister["dest_display_location"] = locations_for_delicate_canisters.pop(0)
                        else:
                            canister["dest_display_location"] = locations_for_small_canisters.pop(0)
                    elif canister["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and locations_for_big_canisters:
                        canister["dest_display_location"] = locations_for_big_canisters.pop(0)
                    else:
                        canister["dest_display_location"] = None

            logger.info(
                "In guided_canister_data_to_device_transfer: Fetching to be removed canister list data from robot")
            total_locations_per_drawer = int(get_max_locations_of_a_container(container_id=drawer_id))
            transferred_canisters_count = len(get_transferred_canisters_of_robot_to_trolley(container_id=drawer_id,
                                                                                            guided_cycle_id=mini_batch))
            to_be_removed_canister_count = int(total_locations_per_drawer - transferred_canisters_count)
            canisters_to_be_removed, drawer_to_unlock = get_canisters_to_be_removed_from_robot(device_id=device_id,
                                                                                               container_id=drawer_id,
                                                                                               guided_tx_cycle_id=mini_batch,
                                                                                               no_of_canisters=to_be_removed_canister_count,
                                                                                               drawers_to_unlock=drawer_to_unlock,
                                                                                               delicate_drawers_to_unlock=delicate_drawers_to_unlock,
                                                                                               quadrant=dest_quad)
            if canisters_to_be_removed:
                transfer_data.extend(canisters_to_be_removed)

        response["trolley_drawer_name"] = trolley_drawer_name
        response['transfer_data'] = transfer_data
        response['regular_drawers_to_unlock'] = list(drawer_to_unlock.values())
        response['delicate_drawers_to_unlock'] = list(delicate_drawers_to_unlock.values())

        couch_db_update_args = {"device_id": device_id,
                                "system_id": system_id,
                                "drawer_id": drawer_id,
                                "drawer_serial_number": drawer_serial_number
                                }
        couch_db_update_status = update_scanned_drawer_in_guided_tx_couch_db_doc(couch_db_update_args)
        response["couch_db_update"] = couch_db_update_status
        logger.info(
            "In guided_canister_data_to_device_transfer: Response of guided_canister_data_to_device_transfer {}".format(
                response))
        return create_response(response)

    except RealTimeDBException as e:
        return error(2005, " - " + str(e))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting canister transfers form trolley")


@log_args_and_response
def get_replaced_canister_list_and_assign_csr_location(device_id, company_id, system_id, cycle_id):
    """
    Function to get list of canisters that are replaced with their alternate canisters
    and assign CSR location to them.
    @param device_id: int
    @param company_id: int
    @param system_id: int
    @param batch_id: int
    @param cycle_id: int
    @return: dict
    """
    try:
        canister_location_dict = dict()
        reserve_location_list = list()
        canister_list = get_replaced_and_to_robot_skipped_canister_list(cycle_id=cycle_id)
        # remove canisters in canister_list from reserved_canister table
        if len(canister_list):
            status = remove_reserved_canisters(canister_list=canister_list)
            logger.info(
                "In get_replaced_canister_list_and_assign_csr_location: reserved canister: {} removed: {}".format(
                    canister_list, status))

            input_args = {'device_id': device_id,
                          'company_id': company_id,
                          'system_id': system_id}

            for canister in canister_list:
                input_args['canister_id'] = canister
                input_args['reserved_location_list'] = reserve_location_list
                logger.info(
                    "In get_replaced_canister_list_and_assign_csr_location: guided csr location reserved location list - {}".format(
                        reserve_location_list))
                response = recommend_csr_location(input_args)
                loaded_response = json.loads(response)
                location_id = loaded_response['data']['location_id']
                logger.info("In get_replaced_canister_list_and_assign_csr_location: loaded_response: {}".format(
                    loaded_response))
                reserve_location_list.append(location_id)
                canister_location_dict[canister] = location_id
                logger.info(
                    "In get_replaced_canister_list_and_assign_csr_location: guided- assign csr location: - {}".format(
                        canister_location_dict))

            if canister_location_dict:
                response = update_guided_tracker_location(cycle_id, canister_location_dict)
                logger.info(response)

        return canister_list

    except Exception as e:
        logger.error(e)
        return False


@log_args_and_response
def add_alternate_canister_id_and_replenish_reqd_data(company_id: int, replenish_list: list,
                                                      first_guided_replenish: bool) -> tuple:
    """
    Method to add alternate canister id in replenish list
    @param first_guided_replenish:
    @param company_id:
    @param batch_id:
    @param replenish_list:
    @return:
    """
    try:
        chosen_alternate_canister_list = list()
        slow_movers_with_destinations = {}
        alternate_location_list = []
        # fetch alternate canisters for canister_id, chose one alternate canister and reserve that alternate canister
        for replenish in replenish_list:

            if replenish['id'] in slow_movers_with_destinations.keys():
                replenish['can_location_id'] = slow_movers_with_destinations[replenish['id']]

            replenish["alternate_canister_id"] = None
            replenish["alt_can_drawer_level"] = 0
            replenish["alt_canister_type"] = None

            # Fetch drug quantity required in whole batch for particular canister
            # canister_qty_data = get_req_drug_qty_of_canister(filling_pending_pack_ids=filling_pending_pack_ids,
            # canister_ids=[replenish["canister_id"]])
            # for rec in canister_qty_data:
            #     replenish["required_qty"] = rec["required_qty"]
            #     break

            # if source canister having 0 qty then don't go for alternate canister
            if replenish["available_quantity"] <= 0:
                continue
            # check for alternate canisters for source canister having qty > 0
            alternate_canister_list = get_alternate_canister_for_batch_data(company_id=company_id,
                                                                            alt_in_robot=False,
                                                                            canister_ids=[replenish["canister_id"]],
                                                                            current_not_in_robot=False,
                                                                            alt_available=True,
                                                                            alt_canister_for_guided=True)
            if alternate_canister_list:
                # choose alternate_canister with the highest quantity
                chosen_alt_can = None
                alternate_delicates = []
                for alt_can in alternate_canister_list:
                    if replenish["canister_type"] == constants.SIZE_OR_TYPE_SMALL and \
                            alt_can["alt_canister_type"] == constants.SIZE_OR_TYPE_BIG:
                        # Do not recommend big alternate canister in case of small source canister,
                        # continue to check for other small canisters if available in alternate_canister_list
                        continue
                    if alt_can['alt_is_delicate'] and not replenish['is_delicate']:
                        alternate_delicates.append(alt_can)
                        continue

                    chosen_alt_can = alt_can
                    break
                if alternate_delicates and chosen_alt_can is None:
                    chosen_alt_can = alternate_delicates[0]
                    empty_locations = get_empty_locations_of_quadrant(replenish['device_id'],
                                                                      [replenish['quadrant']])

                    if empty_locations:
                        for item in empty_locations:
                            if item[1] < 5:
                                replenish['can_location_id'] = item[0]
                                break
                    else:
                        slow_movers,canister_id = get_slow_movers_for_device(replenish['device_id'],
                                                                 replenish['quadrant'])
                        for can_id, location in slow_movers:
                            if can_id in slow_movers_with_destinations.keys():
                                continue
                            temp_location_id = replenish['can_location_id']
                            replenish['can_location_id'] = location[1]
                            slow_movers_with_destinations[can_id] = temp_location_id

                if chosen_alt_can:
                    source_can_quantity = replenish["available_quantity"]
                    alt_can_quantity = chosen_alt_can["alt_available_quantity"]
                    req_quantity = int(replenish["required_qty"])
                    status = check_validation_of_alternate_canister_selection(req_quantity, source_can_quantity,
                                                                              alt_can_quantity,
                                                                              first_guided_replenish)
                    if status:
                        # reserve chosen alt canister
                        record, created = reserve_canister(batch_id=None,
                                                           canister_id=chosen_alt_can["alt_canister_id"])
                        if created:
                            replenish["alternate_canister_id"] = chosen_alt_can["alt_canister_id"]
                            replenish['alt_can_drawer_level'] = chosen_alt_can["alt_can_drawer_level"]
                            replenish["alt_canister_type"] = chosen_alt_can["alt_canister_type"]
                            chosen_alternate_canister_list.append(chosen_alt_can["alt_canister_id"])

                        if replenish["alternate_canister_id"]:
                            # fetch total required quantity for whole batch and compare with available qty of
                            # alt canister

                            if replenish["required_qty"] > chosen_alt_can["alt_available_quantity"]:
                                replenish["alt_can_replenish_required"] = True
                            else:
                                replenish["alt_can_replenish_required"] = False

        return replenish_list, chosen_alternate_canister_list
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_canister_replenish_list(system_id: int, device_ids: list, company_id: int,
                                first_guided_replenish: bool) -> tuple:
    """
    Method to get canister replenish list for one guided tx cycle
    @param first_guided_replenish:
    @param company_id:
    @param device_ids:
    @param batch_id:
    @param system_id:
    @return:
    """
    logger.info("recommendguidedtx: In get_canister_replenish_list")
    # replenish_meta_dict = dict()
    replenish_list_with_trolley_id = list()  # format: {"trolley_id":
    # {"robot_id":{"1":[list of dict], "2":[list of dict],  "3":[list of dict],"4":[list of dict]}}}
    # extra_locations_count = 0
    logger.info("In get_canister_replenish_list: fetching replenish list using method "
                "get_canister_to_be_replenished_next_dao")
    no_of_drawers = 0
    locations_per_drawer = 0
    chosen_alternate_canister_list = list()
    try:
        status, message, current_mini_batch_id, mini_batch_packs, replenish_list, pending_packs_for_timer = \
            get_canister_to_be_replenished_next_dao(system_id=system_id,
                                                    device_ids=device_ids)
        if not status or not replenish_list or not current_mini_batch_id:
            logger.error("In get_canister_replenish_list: False status with message - " + str(message))
            return False, message, current_mini_batch_id, mini_batch_packs, replenish_list_with_trolley_id, pending_packs_for_timer, \
                   chosen_alternate_canister_list

        logger.info("In get_canister_replenish_list: fetching alternate canister if available")
        # add key in replenish data for alternate canister available or not and
        # if available then replenish required or not - ( field -alternate_canister_id, alt_can_replenish_required)
        replenish_list, chosen_alternate_canister_list = \
            add_alternate_canister_id_and_replenish_reqd_data(company_id, replenish_list,
                                                              first_guided_replenish)

        logger.info("In get_canister_replenish_list: added alternate canister data, now dividing "
                    "replenish list in robot and quadrant wise")
        replenish_meta_dict = fetch_replenish_meta_dict(replenish_list)
        logger.info("In get_canister_replenish_list: prepared replenish_meta_dict")
        logger.info("In get_canister_replenish_list: fetching empty locations of robot quadrant wise")
        all_empty_locations_dict = fetch_empty_locations_count_quadrant_wise_based_on_device_ids(device_ids,
                                                                                                 consider_higher_drawers
                                                                                                 =True)
        empty_locations_dict = dict()
        # original_replenish_meta_dict = replenish_meta_dict
        # original_replenish_list = replenish_list
        pending_replenish = list()  # to keep track of replenish data which are unable to fit in one trolley
        on_initial = True  # flag for to execute below loop least once

        while (on_initial and replenish_list and replenish_meta_dict) or pending_replenish:
            on_initial = False
            if pending_replenish:
                # case when looking for next replenish cycle for current mini batch only
                logger.info("In get_canister_replenish_list: fetching replenish list from")
                # reverse pending replenish to maintain pack sequence and then repeat until we get list of
                # required trolley
                pending_replenish.reverse()
                replenish_list = [r for r_list in pending_replenish for r in r_list]
                replenish_meta_dict = fetch_replenish_meta_dict(replenish_list)
                pending_replenish = list()
            while True:
                # recommend drawers of trolley to transfers canisters to trolley based on dest device and dest quad.
                # find trolley type lift or normal, lift in case of big canister or can drawer level greater than 4
                trolley_type_id = None
                for record in replenish_list:
                    if record["canister_type"] == constants.SIZE_OR_TYPE_BIG \
                            or record["drawer_level"] in settings.DRAWER_LEVEL["lift_trolley"] \
                            or (
                            record["alt_canister_type"] and record["alt_canister_type"] == constants.SIZE_OR_TYPE_BIG) \
                            or record["alt_can_drawer_level"] in constants.CSR_LIFT_TROLLEY_LEVELS:
                        trolley_type_id = settings.DEVICE_TYPES["Canister Cart w/ Elevator"]
                        logger.info("In get_canister_replenish_list: assigned lift trolley- drawers_count: {}, "
                                    "locations_per_drawer: {}".format(no_of_drawers, locations_per_drawer))

                        # fetch empty locations dict based on trolley type
                        empty_locations_dict = fetch_empty_locations_count_quadrant_wise_based_on_device_ids(
                            device_ids, consider_higher_drawers=True)

                        break
                if not trolley_type_id:
                    trolley_type_id = settings.DEVICE_TYPES["Canister Transfer Cart"]
                    logger.info("In get_canister_replenish_list: assigned normal trolley- "
                                "drawers_count: {}, locations_per_drawer: {}".format(no_of_drawers,
                                                                                     locations_per_drawer))

                    # fetch empty locations dict based on trolley type
                    empty_locations_dict = fetch_empty_locations_count_quadrant_wise_based_on_device_ids(
                        device_ids, consider_higher_drawers=False)
                logger.info("In get_canister_replenish_list: fetching empty trolley based on trolley "
                            "type")
                empty_trolley_dict = get_available_trolley_data(device_type_ids=[trolley_type_id], company_id=company_id)
                logger.info("In get_canister_replenish_list: fetched empty_trolley_dict: " + str(
                    empty_trolley_dict))

                trolley_id = None
                if trolley_type_id in empty_trolley_dict:
                    for record in empty_trolley_dict[trolley_type_id]:
                        trolley_id = record["id"]
                        no_of_drawers = get_max_drawers_per_device_based_on_device_id(device_id=trolley_id)
                        locations_per_drawer = get_max_locations_per_drawer_based_on_device_id(device_id=trolley_id)
                        break
                if not trolley_id or not locations_per_drawer or not no_of_drawers:
                    return False, "Required trolley is not available", current_mini_batch_id, mini_batch_packs, \
                           replenish_list_with_trolley_id, pending_packs_for_timer, chosen_alternate_canister_list

                logger.info("In get_canister_replenish_list: dividing canisters in trolley drawers "
                            "according to trolley and drawer capacity")
                partition_list = list()
                for device_id, quadrant_dict in replenish_meta_dict.items():
                    for quadrant, canister_dict in quadrant_dict.items():
                        # check if alternate canisters are there in this quadrant
                        if "alternate_canisters" in canister_dict.keys():
                            # if alterenate canisters are there then identify whether we can combine source and
                            # alternate in same drawer of trolley or not based on empty locations in the quadrant
                            # of drawer and trolley type
                            # check for empty locations in robot
                            logger.info(
                                "In get_canister_replenish_list: identifying drawers should be merged or not for alt can")
                            empty_loc_count_based_on_trolley_type = 0
                            all_empty_loc_count = 0
                            if int(device_id) in empty_locations_dict and int(device_id) in all_empty_locations_dict \
                                    and int(quadrant) in empty_locations_dict[int(device_id)] and int(quadrant) in \
                                    all_empty_locations_dict[int(device_id)]:
                                empty_loc_count_based_on_trolley_type = empty_locations_dict[int(device_id)][
                                    int(quadrant)]
                                all_empty_loc_count = all_empty_locations_dict[int(device_id)][int(quadrant)]
                            alt_canisters_count = int(len(canister_dict["alternate_canisters"][constants.REGULAR_CANISTER])) + int(len(canister_dict["alternate_canisters"][constants.DELICATE_CANISTER]))
                            logger.info(
                                "In get_canister_replenish_list: device_id: {}, quadrant: {}, alt_canisters_count: {}, empty_loc_count_based_on_trolley_type: {},"
                                " all_empty_loc_count:{}"
                                    .format(device_id, quadrant, alt_canisters_count,
                                            empty_loc_count_based_on_trolley_type, all_empty_loc_count))

                            if alt_canisters_count <= empty_loc_count_based_on_trolley_type \
                                    and alt_canisters_count <= all_empty_loc_count:
                                logger.info("In get_canister_replenish_list: combining alt and source canisters")
                                # combine alt canisters and source in same drawer
                                if not "cluster_1" in replenish_meta_dict[device_id][quadrant].keys():
                                    replenish_meta_dict[device_id][quadrant]["cluster_1"] = dict()
                                    replenish_meta_dict[device_id][quadrant]["cluster_1"][constants.DELICATE_CANISTER] = list()
                                    replenish_meta_dict[device_id][quadrant]["cluster_1"][constants.REGULAR_CANISTER] = list()
                                replenish_meta_dict[device_id][quadrant]["cluster_1"][constants.DELICATE_CANISTER].extend(
                                    canister_dict["alternate_canisters"][constants.DELICATE_CANISTER])
                                replenish_meta_dict[device_id][quadrant]["cluster_1"][
                                    constants.REGULAR_CANISTER].extend(
                                    canister_dict["alternate_canisters"][constants.REGULAR_CANISTER])

                                source_canisters_count = 0
                                if "source_canisters" in canister_dict.keys():
                                    source_canisters_count = len(canister_dict["source_canisters"][constants.DELICATE_CANISTER]) + len(canister_dict["source_canisters"][constants.REGULAR_CANISTER])
                                    replenish_meta_dict[device_id][quadrant]["cluster_1"][constants.DELICATE_CANISTER].extend(
                                        canister_dict["source_canisters"][constants.DELICATE_CANISTER])
                                    replenish_meta_dict[device_id][quadrant]["cluster_1"][
                                        constants.REGULAR_CANISTER].extend(canister_dict["source_canisters"][constants.REGULAR_CANISTER])

                                partition_list.append(alt_canisters_count + source_canisters_count)

                                # subtract used locations
                                all_empty_locations_dict[int(device_id)][int(quadrant)] -= alt_canisters_count
                            else:
                                logger.info("In get_canister_replenish_list: keeping source and alternate canisters"
                                            " in different drawers")
                                if "source_canisters" in canister_dict.keys():
                                    partition_list.append(int(len(canister_dict["source_canisters"][constants.REGULAR_CANISTER])) + int(len(canister_dict["source_canisters"][constants.DELICATE_CANISTER])))
                                    if "cluster_1" not in replenish_meta_dict[device_id][quadrant].keys():
                                        replenish_meta_dict[device_id][quadrant]["cluster_1"] = dict()
                                        replenish_meta_dict[device_id][quadrant]["cluster_1"][constants.DELICATE_CANISTER] = list()
                                        replenish_meta_dict[device_id][quadrant]["cluster_1"][
                                            constants.REGULAR_CANISTER] = list
                                    replenish_meta_dict[device_id][quadrant]["cluster_1"][constants.DELICATE_CANISTER].extend(
                                        canister_dict["source_canisters"][constants.DELICATE_CANISTER])
                                    replenish_meta_dict[device_id][quadrant]["cluster_1"][
                                        constants.REGULAR_CANISTER].extend(
                                        canister_dict["source_canisters"][constants.REGULAR_CANISTER])

                                partition_list.append(int(len(canister_dict["alternate_canisters"][constants.REGULAR_CANISTER])) + int(len(canister_dict["alternate_canisters"][constants.DELICATE_CANISTER])))
                                if "cluster_2" not in replenish_meta_dict[device_id][quadrant].keys():
                                    replenish_meta_dict[device_id][quadrant]["cluster_2"] = dict()
                                    replenish_meta_dict[device_id][quadrant]["cluster_2"][constants.DELICATE_CANISTER] =list()
                                    replenish_meta_dict[device_id][quadrant]["cluster_2"][constants.REGULAR_CANISTER] =list()
                                replenish_meta_dict[device_id][quadrant]["cluster_2"][constants.DELICATE_CANISTER].extend(
                                    canister_dict["alternate_canisters"][constants.DELICATE_CANISTER])
                                replenish_meta_dict[device_id][quadrant]["cluster_2"][
                                    constants.REGULAR_CANISTER].extend(
                                    canister_dict["alternate_canisters"][constants.REGULAR_CANISTER])

                        else:
                            logger.info(
                                "In get_canister_replenish_list: alternate canisters not available so adding source canisters only")
                            partition_list.append(int(len(canister_dict["source_canisters"][constants.REGULAR_CANISTER])) + int(len(canister_dict["source_canisters"][constants.DELICATE_CANISTER])))
                            if "cluster_1" not in replenish_meta_dict[device_id][quadrant].keys():
                                replenish_meta_dict[device_id][quadrant]["cluster_1"] = dict()
                                replenish_meta_dict[device_id][quadrant]["cluster_1"][constants.DELICATE_CANISTER] = list()
                                replenish_meta_dict[device_id][quadrant]["cluster_1"][
                                    constants.REGULAR_CANISTER] = list()
                            replenish_meta_dict[device_id][quadrant]["cluster_1"][constants.DELICATE_CANISTER].extend(
                                canister_dict["source_canisters"][constants.DELICATE_CANISTER])
                            replenish_meta_dict[device_id][quadrant]["cluster_1"][constants.REGULAR_CANISTER].extend(
                                canister_dict["source_canisters"][constants.REGULAR_CANISTER])

                logger.info("In get_canister_replenish_list: get_canister_replenish_list: partition_list- " + str(
                    partition_list))
                extra_locations_count = get_extra_locations_count(no_of_drawers=no_of_drawers,
                                                                  partition_list=partition_list,
                                                                  no_of_locations_in_each_container=locations_per_drawer)
                logger.info("In get_canister_replenish_list: get_canister_replenish_list: extra_locations_count- " + str(
                        extra_locations_count))
                if extra_locations_count:
                    # prepare data for next cycle
                    intermediate_replenish_list = replenish_list
                    replenish_list = replenish_list[
                                     :-int(extra_locations_count)]  # get all except last extra_locations_count
                    pending_replenish.append(
                        intermediate_replenish_list[-int(extra_locations_count):])  # get last extra_locations_count
                    logger.info("In get_canister_replenish_list: pending replenish list {}".format(pending_replenish))
                    replenish_meta_dict = fetch_replenish_meta_dict(replenish_list)
                    logger.info("In get_canister_replenish_list: get_canister_replenish_list: modified replenish_list"
                                " as all canisters are unable to fit in one drawer")
                else:
                    # remove alternate and source canisters bcz now we have to use only data from cluster key
                    for device_id, quadrant_dict in replenish_meta_dict.items():
                        for quadrant, canister_dict in quadrant_dict.items():
                            # check if alternate canisters are there in this quadrant
                            if "alternate_canisters" in canister_dict.keys():
                                alt_canisters = canister_dict.pop("alternate_canisters")
                            if "source_canisters" in canister_dict.keys():
                                source_canisters = canister_dict.pop("source_canisters")
                    replenish_list_with_trolley_id.append({trolley_id: {"replenish_meta_dict": replenish_meta_dict,
                                                                        "locations_per_drawer": locations_per_drawer}})
                    # converted to list to handle case when there are two mini batch with same trolley in
                    # one replenish cycle
                    # replenish_dict_with_trolley_id[trolley_id] = {"replenish_meta_dict": replenish_meta_dict,
                    #                                               "locations_per_drawer": locations_per_drawer
                    #                                               }
                logger.info(
                    "In get_canister_replenish_list: get_canister_replenish_list: added replenish list for trolley- " + str(
                        trolley_id))
                break

        return True, message, current_mini_batch_id, mini_batch_packs, replenish_list_with_trolley_id, pending_packs_for_timer, \
               chosen_alternate_canister_list
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def fetch_replenish_meta_dict(replenish_list):
    replenish_meta_dict = dict()
    for record in replenish_list:
        if str(record["device_id"]) not in replenish_meta_dict:
            replenish_meta_dict[str(record["device_id"])] = dict()
        if str(record["quadrant"]) not in replenish_meta_dict[str(record["device_id"])]:
            replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])] = dict()

        if record["alternate_canister_id"] is not None:
            if "alternate_canisters" not in replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]:
                replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["alternate_canisters"] = dict()
            if constants.DELICATE_CANISTER not in replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["alternate_canisters"]:
                replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["alternate_canisters"][constants.DELICATE_CANISTER] = list()
            if constants.REGULAR_CANISTER not in replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["alternate_canisters"]:
                replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["alternate_canisters"][constants.REGULAR_CANISTER] = list()
            if record['is_delicate']:
                replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["alternate_canisters"][
                    constants.DELICATE_CANISTER].append(record)
            else:
                replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["alternate_canisters"][
                    constants.REGULAR_CANISTER].append(record)
        else:
            if "source_canisters" not in replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]:
                replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["source_canisters"] = dict()
            if constants.DELICATE_CANISTER not in \
                    replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["source_canisters"]:
                replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["source_canisters"][
                    constants.DELICATE_CANISTER] = list()
            if constants.REGULAR_CANISTER not in \
                    replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["source_canisters"]:
                replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["source_canisters"][
                    constants.REGULAR_CANISTER] = list()
            if record['is_delicate']:
                replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["source_canisters"][
                    constants.DELICATE_CANISTER].append(record)
            else:
                replenish_meta_dict[str(record["device_id"])][str(record["quadrant"])]["source_canisters"][
                    constants.REGULAR_CANISTER].append(record)
    return replenish_meta_dict


@log_args_and_response
def check_validation_of_alternate_canister_selection(req_quantity, source_can_quantity, alt_can_quantity,
                                                     first_guided_replenish):

    upper_threshold_quantity = req_quantity * settings.REPLENISH_CAN_QUANTITY_UPPER_THRESHOLD
    lower_threshold_quantity = req_quantity * settings.REPLENISH_CAN_QUANTITY_LOWER_THRESHOLD

    alt_canister_selection = False

    # In the first guided replenish cycle, priority of selection will be the source one. From second onwards priority
    # will be alternate canister.

    if first_guided_replenish:
        # If alt_can_quantity is in upper range than of source one, then and then only we consider alt canister.
        if source_can_quantity < upper_threshold_quantity <= alt_can_quantity:
            alt_canister_selection = True
        if source_can_quantity < lower_threshold_quantity <= alt_can_quantity:
            alt_canister_selection = True
        if source_can_quantity < req_quantity < alt_can_quantity:
            alt_canister_selection = True
    else:
        # If source_can_quantity is in upper range than of alt one, then and then only we consider source canister.
        alt_canister_selection = True
        if alt_can_quantity < upper_threshold_quantity <= source_can_quantity:
            alt_canister_selection = False
        if alt_can_quantity < lower_threshold_quantity <= source_can_quantity:
            alt_canister_selection = False

    return alt_canister_selection


@log_args_and_response
def update_scanned_drawer_in_guided_tx_couch_db_doc(args):
    """
    Function to update transfer data for guided transfer flow in couch db
    @param args: dict
    @return: status
    """
    logger.info("In update_guided_canister_transfer_couch_db")
    device_id = args["device_id"]
    system_id = args["system_id"]
    drawer_id = args["drawer_id"]
    drawer_serial_number = args["drawer_serial_number"]

    logger.info("update_guided_canister_transfer_couch_db Input {}".format(args))

    try:
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = '{}_{}'.format(constants.GUIDED_TRANSFER_DOCUMENT_NAME, device_id)
        table = cdb.get(_id=id)

        logger.info(
            "In update_scanned_drawer_in_guided_tx_couch_db_doc: previous table in guided transfer {}".format(table))

        if table is None:  # when no document available for given device_id
            table = {"_id": id, "type": 'guided_canister_transfer',
                     "data": dict()}

        if "scanned_drawer" in table['data'] and table['data']['scanned_drawer'] == drawer_id:
            logger.info("In update_scanned_drawer_in_guided_tx_couch_db_doc: updated table in guided transfer no change {}".format(
                    table))
            return True

        elif "currently_scanned_drawer_sr_no" not in table['data'] or drawer_serial_number == 0:
            table["data"]["currently_scanned_drawer_sr_no"] = None
            table["data"]["previously_scanned_drawer_sr_no"] = None
            table['data']['scanned_drawer'] = None
            table['data']['timestamp'] = get_current_date_time()

        else:
            # different drawer scanned so update it
            table["data"]["previously_scanned_drawer_sr_no"] = table["data"]["currently_scanned_drawer_sr_no"]
            table["data"]["currently_scanned_drawer_sr_no"] = drawer_serial_number
            table['data']['scanned_drawer'] = drawer_id
            table['data']['timestamp'] = get_current_date_time()
            logger.info("In update_scanned_drawer_in_guided_tx_couch_db_doc: updated table in guided transfer {}".format(table))

        logger.info("In update_scanned_drawer_in_guided_tx_couch_db_doc: updated table in guided transfer  {}".format(
                    table))
        cdb.save(table)
        return True

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return error(1000, "Document update conflict.")

    except RealTimeDBException as e:
        return error(1000, str(e))

    except Exception as e:
        logger.error(e)
        raise Exception('Couch db update failed while transferring canisters')


@log_args_and_response
def fetch_scanned_drawer_in_guided_tx_flow(args: dict) -> int:
    """
    Function to fetch scanned drawer id in guided transfer flow in couch db
    @param args: dict
    @return: status
    """
    logger.info("In fetch_scanned_drawer_in_guided_tx_flow")
    device_id = args["device_id"]
    system_id = args["system_id"]

    logger.info("update_guided_canister_transfer_couch_db Input {}".format(args))

    try:
        drawer_id = None
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = '{}_{}'.format(constants.GUIDED_TRANSFER_DOCUMENT_NAME, device_id)
        table = cdb.get(_id=id)

        logger.info("In fetch_scanned_drawer_in_guided_tx_flow: previous table in guided transfer {}".format(table))
        if table is not None:
            if "data" in table.keys() and "scanned_drawer" in table['data'] and table['data']['scanned_drawer']:
                drawer_id = table['data']['scanned_drawer']

        return drawer_id

    except RealTimeDBException as e:
        return error(1000, str(e))
    except Exception as e:
        logger.error(e)
        raise Exception(
            'In fetch_scanned_drawer_in_guided_tx_flow: Couch db access failed while transferring canisters')


@log_args_and_response
def update_guided_canister_transfer_couch_db(args):
    """
    Function to update transfer data for guided transfer flow in couch db
    @param args: dict
    @return: status
    """
    logger.info("In update_guided_canister_transfer_couch_db")
    device_id = args["device_id"]
    system_id = args["system_id"]
    batch_id = args["batch_id"]
    guided_tx_cycle_id = args["guided_tx_cycle_id"]
    flow = args["flow"]
    trolley_id = args["trolley_id"]
    drawer_list = args["drawer_list"]
    drawer_id = args.get("drawer_id", None)
    canister_to_transfer = args.get("canister_to_transfer", None)
    device_type = args.get("device_type", None)
    drawer_to_unlock = args.get("drawer_to_unlock", None)
    couch_db_canister = args.get('couch_db_canister', None)

    if device_type and device_type == settings.DEVICE_TYPES_NAMES['CSR']:
        flow = 'guided_transfer_to_csr'

    logger.info("update_guided_canister_transfer_couch_db Input {}".format(args))

    try:
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = '{}_{}'.format(constants.GUIDED_TRANSFER_DOCUMENT_NAME, device_id)
        table = cdb.get(_id=id)

        logger.info("In update_guided_canister_transfer_couch_db: previous table in guided transfer {}".format(table))
        if table is None:  # when no document available for given device_id
            table = {"_id": id, "type": 'guided_canister_transfer',
                     "data": dict()}

        if batch_id is not None:
            if 'guided_tx_cycle_id' in table['data'] and table['data']['guided_tx_cycle_id'] is not None and int(
                    table['data']['guided_tx_cycle_id']) != int(guided_tx_cycle_id):
                table['data'] = {"device_id": device_id,
                                 "batch_id": batch_id,
                                 "guided_tx_cycle_id": guided_tx_cycle_id,
                                 "guided_transfer_to_trolley": dict(),
                                 "guided_transfer_to_robot": dict(),
                                 "guided_transfer_to_csr": dict()}

        if not len(table['data']):
            table['data'] = {"device_id": device_id,
                             "batch_id": batch_id,
                             "guided_tx_cycle_id": guided_tx_cycle_id,
                             "guided_transfer_to_trolley": dict(),
                             "guided_transfer_to_robot": dict(),
                             "guided_transfer_to_csr": dict()}

            cdb.save(table)

        logger.info("In update_guided_canister_transfer_couch_db: Before adding trolley data {}".format(table))

        if trolley_id and str(trolley_id) not in table['data'][flow].keys():
            table['data'][flow][str(trolley_id)] = {"trolley_scanned": True, "drawer_data": dict()}

        if drawer_list:
            for drawer_data in drawer_list:
                each_drawer = drawer_data['container_id']
                serial_number = drawer_data['serial_number']
                if each_drawer and str(each_drawer) not in table['data'][flow][str(trolley_id)]['drawer_data'].keys():
                    table['data'][flow][str(trolley_id)]["drawer_data"][str(each_drawer)] = {"drawer_scanned": False,
                                                                                             "canister_to_transfer": None,
                                                                                             "serial_number": serial_number,
                                                                                             "drawer_to_unlock": None}

        if drawer_id and str(drawer_id) in table['data'][flow][str(trolley_id)]['drawer_data'].keys():
            table['data'][flow][str(trolley_id)]["drawer_data"][str(drawer_id)]["drawer_scanned"] = True
            table['data'][flow][str(trolley_id)]["drawer_data"][str(drawer_id)][
                "canister_to_transfer"] = canister_to_transfer
            table['data'][flow][str(trolley_id)]["drawer_data"][str(drawer_id)]["drawer_to_unlock"] = drawer_to_unlock

            if couch_db_canister:
                table['data'][flow][str(trolley_id)]["drawer_data"][str(drawer_id)][
                    "couch_db_canister"] = couch_db_canister

        logger.info("In update_guided_canister_transfer_couch_db: updated table in guided transfer {}".format(table))
        cdb.save(table)
        return True

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return error(1000, "Document update conflict.")

    except RealTimeDBException as e:
        return error(1000, str(e))

    except Exception as e:
        logger.error(e)
        raise Exception('Couch db update failed while transferring canisters')


@log_args_and_response
@validate(required_fields=["company_id", "system_id"])
def recommendguidedtx(args: dict) -> dict:
    """
    Method to run guided transfer algorithm
    @param args:
    @return:
    """

    robot_ids = list()
    status = 0
    current_mini_batch_processing_time = 0  # time in seconds
    recommended_alternate_canister_list = list()
    company_id = args["company_id"]
    system_id = args["system_id"]
    # batch_id = args.get("batch_id", None)
    try:

        # # fetch progress batch id if batch_id is None
        # if not batch_id:
        #     batch_id = get_progress_batch_id(system_id=system_id)
        #     if not batch_id:
        #         return error(14002)
        # else:
        #     # validate batch id
        #     validate_batch_id = validate_batch_id_dao(batch_id=batch_id)
        #     if not validate_batch_id:
        #         return error(14008)

        # check packs are available in pack queue or not.
        pack_queue_available = check_packs_in_pack_queue_for_system(system_id=system_id)

        if not pack_queue_available:
            return error(14003)

        # check for pending normal canister transfer flow
        logger.info("In recommendguidedtx: Checking for pending canister transfers")
        pending_can_transfers = check_pending_canister_transfers(system_id=system_id)

        if pending_can_transfers:
            logger.info("In recommendguidedtx: Incomplete canister transfer flow")
            pending_batch_id, pending_device_system_id = None, None
            for record in pending_can_transfers:
                if not pending_batch_id or not pending_device_system_id:
                    pending_batch_id = record["batch_id"]
                    pending_device_system_id = record["pending_device_system_id"]
            return error(14004, "{},{}".format(pending_batch_id, pending_device_system_id))

        logger.info("In recommendguidedtx: No pending cycle of canister transfer flow")


        # fetch robot_ids based on system_id
        robot_data = get_robots_by_system_id_dao(system_id=system_id)
        for robot in robot_data:
            robot_ids.append(robot["id"])

        # check if any canisters are already present in trolley before starting transfers
        cart_canisters = check_canisters_present_in_cart(system_id=system_id)
        if len(cart_canisters):
            return error(9067)

        # TODO: need to check this one
        # status = check_if_guided_replenish_exist_for_batch(batch_id=batch_id)
        status = True
        if status:
            first_guided_replenish = False
        else:
            first_guided_replenish = True

        # fetch list of canisters to be replenished
        logger.info("In recommendguidedtx: fetching replenish_dict_with_trolley_id using method "
                    "get_canister_replenish_list")
        status, message, current_mini_batch_id, mini_batch_packs, replenish_list_with_trolley_id, pending_packs_for_timer,\
            recommended_alternate_canister_list = get_canister_replenish_list(system_id=system_id,
                                                                                device_ids=robot_ids,
                                                                                company_id=company_id,
                                                                              first_guided_replenish=first_guided_replenish)

        logger.info("In recommendguidedtx: response of function: get_canister_replenish_list - status: {}, message:{}, "
                    "current_mini_batch_id:{}, timer:{}".format(status, message, current_mini_batch_id,
                                                                pending_packs_for_timer))
        if not status:
            logger.error(str(message))
            if recommended_alternate_canister_list:
                # remove reserved alternate canisters as recommendation is not successful
                try:
                    status = remove_reserved_canisters(canister_list=recommended_alternate_canister_list)
                except (InternalError, IntegrityError, DataError) as e:
                    logger.error("In recommendguidedtx: Error in removing reserved canisters - " + str(e))
            if message.isdigit():
                return error(int(message))
            else:
                return error(1000, message)

        if status and not len(replenish_list_with_trolley_id):
            # no more replenish for current batch
            if recommended_alternate_canister_list:
                # remove reserved alternate canisters as recommendation is not successful
                try:
                    status = remove_reserved_canisters(canister_list=recommended_alternate_canister_list)
                except (InternalError, IntegrityError, DataError) as e:
                    logger.error("In recommendguidedtx: Error in removing reserved canisters - " + str(e))
            logger.error("recommendguidedtx: empty replenish_list_with_trolley_id")
            return error(14001)

        logger.info("In recommendguidedtx: dividing replenish list in guided meta cycle")
        first_cycle_id = None
        for trolley_replenish_dict in replenish_list_with_trolley_id:
            for trolley_id, trolley_replenish_dict in trolley_replenish_dict.items():
                logger.info("In recommendguidedtx: fetching location info of trolley {}".format(trolley_id))

                total_transfers, alt_canister_count, alt_can_replenish_count = 0, 0, 0  # required for guided meta
                cycle_replenish_list = list()  # required for guided tracker

                logger.info("recommendguidedtx: fetching location info of trolley {}".format(trolley_id))
                trolley_locations, drawer_location_info = get_location_data_from_device_ids(device_id_list=[trolley_id])
                current_trolley_drawers_locations = drawer_location_info[trolley_id]
                logger.info(
                    "In recommendguidedtx: current_trolley_drawers_locations- " + str(
                        current_trolley_drawers_locations))

                locations_per_drawer = trolley_replenish_dict["locations_per_drawer"]

                replenish_meta_dict = trolley_replenish_dict["replenish_meta_dict"]

                for robot_id, robot_replenish_dict in replenish_meta_dict.items():
                    logger.info("In recommendguidedtx: robot_id- " + str(robot_id))
                    for quadrant, quad_replenish_dict in robot_replenish_dict.items():
                        logger.info("In recommendguidedtx: quadrant- " + str(quadrant))

                        # by forget quad_replenish_dict based on source_canister and alt_canisters
                        for item, can_data in quad_replenish_dict.items():
                            # for delicate and regular canisters
                            can_data = OrderedDict(sorted(can_data.items()))
                            for can_type, replenish_list in can_data.items():
                                # fetch drawers required for replenish_list
                                if replenish_list:
                                    no_of_drawers_required = int(math.ceil(len(replenish_list) / int(locations_per_drawer)))
                                    logger.info(
                                        "In recommendguidedtx: no_of_drawers_required - {} for quadrant- {}, for robot- {}, "
                                        "for item - {} ".format(no_of_drawers_required, quadrant, robot_id, item))
                                    locations_list = list()

                                    # remove "no_of_drawers_required" drawer location pair from
                                    # current_trolley_drawers_locations
                                    for i in range(no_of_drawers_required):
                                        # fetch locations of drawers assigned to current quadrant
                                        locations = current_trolley_drawers_locations.popitem()[1]
                                        locations_list.extend(locations)

                                    for replenish in replenish_list:
                                        # for guided tracker
                                        replenish_record = {"source_canister_id": replenish["canister_id"],
                                                            "alternate_canister_id": replenish.get("alternate_canister_id",
                                                                                                   None),
                                                            "alt_can_replenish_required": replenish.get(
                                                                "alt_can_replenish_required"),
                                                            "cart_location_id": locations_list.pop(0),
                                                            "destination_location_id": replenish.get("can_location_id"),
                                                            "required_qty": replenish.get("required_qty")}
                                        logger.info("In recommendguidedtx: replenish_record- " + str(replenish_record))
                                        cycle_replenish_list.append(replenish_record)

                                        # for guided meta
                                        total_transfers += 1
                                        if replenish.get("alternate_canister_id"):
                                            alt_canister_count += 1
                                        if replenish.get("alt_can_replenish_required"):
                                            alt_can_replenish_count += 1
                created_date, modified_date = get_current_modified_datetime()
                mini_batch_packs = str(mini_batch_packs)[1:-1]
                guided_meta_record = {"batch_id": None, "cart_id": trolley_id, "mini_batch_id": current_mini_batch_id,
                                      "total_transfers": total_transfers, "alt_canister_count": alt_canister_count,
                                      "alt_can_replenish_count": alt_can_replenish_count, "created_date": created_date,
                                      "modified_date": modified_date, "pack_ids": mini_batch_packs}
                logger.info("In recommendguidedtx: guided_meta_record - " + str(guided_meta_record))
                with db.transaction():
                    logger.info("In recommendguidedtx: adding record in guided_meta")
                    # add record in guided meta data
                    guided_meta_id = add_record_in_guided_meta(guided_meta_record)
                    logger.info(
                        "In recommendguidedtx: added record in guided_meta with guided_meta_id- " + str(guided_meta_id))

                    if not first_cycle_id:
                        first_cycle_id = guided_meta_id
                    # add guided meta id in cycle_replenish_list
                    for cycle_replenish in cycle_replenish_list:
                        cycle_replenish.update({"guided_meta_id": guided_meta_id})

                    logger.info("In recommendguidedtx: adding records in guided_tracker")
                    # insert replenish list in guided tracker
                    status = add_records_in_guided_tracker(cycle_replenish_list)
                    logger.info("In recommendguidedtx: added records in guided_tacker with status- " + str(status))

        if status and pending_packs_for_timer:
            logger.info("In recommendguidedtx: Calculating time for running mini batch")
            # calculate and add timer in couch to show at refill station screen
            pending_packs_for_timer = list(set(pending_packs_for_timer))
            current_mini_batch_processing_time, pending_packs, timer_update, blink_timer = db_get_drop_time(
                robot_ids, system_id, pending_packs_for_timer)
            logger.info("In recommendguidedtx: updating couch db for current_mini_batch_processing_time-"
                        + str(current_mini_batch_processing_time))
        logger.info("In recommendguidedtx: first_cycle_id- " + str(first_cycle_id))

        # update couch db doc guided-transfer-wizard
        update_couch_db_status, couch_db_response = update_guided_tx_meta_data_in_couch_db(
            {"company_id": company_id, "module_id": 0, "mini_batch_id": current_mini_batch_id,
             "guided_tx_cycle_id": first_cycle_id,
             "current_mini_batch_processing_time": current_mini_batch_processing_time,
             "transfer_done_from_portal": False, "timestamp": get_current_date_time()})
        logger.info("In recommendguidedtx: couch db updated with status: " + str(update_couch_db_status))

        if not update_couch_db_status:
            return couch_db_response
        response = {"guided_tx_cycle_id": first_cycle_id}
        return create_response(response)
    except (InternalError, IntegrityError, DataError) as e:
        if recommended_alternate_canister_list:
            # remove reserved alternate canisters as recommendation is not successful
            try:
                status = remove_reserved_canisters(canister_list=recommended_alternate_canister_list)
            except (InternalError, IntegrityError, DataError) as e:
                logger.error("recommendguidedtx: Error in removing reserved canisters - " + str(e))
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        if recommended_alternate_canister_list:
            # remove reserved alternate canisters as recommendation is not successful
            try:
                status = remove_reserved_canisters(canister_list=recommended_alternate_canister_list)
            except (InternalError, IntegrityError, DataError) as e:
                logger.error("recommendguidedtx: Error in removing reserved canisters - " + str(e))
        logger.error(e, exc_info=True)
        return error(1000, "Error while running guided tx algorithm - " + str(e))


@log_args_and_response
@validate(required_fields=["guided_tx_cycle_id", "system_id", "company_id"])
def get_batch_guided_tx_drugs(dict_batch_info: dict) -> dict:
    """
    This function is to obtain drug and canister data for Guided Transfer.
    @param dict_batch_info: dict
    @return dict
    """

    try:
        response: dict = dict()
        canister_data: list = list()
        inventory_data_list = []
        drug_data: dict = dict()
        ndc_list = []
        logger.info("In get_batch_guided_tx_drugs")
        guided_tx_cycle_id = dict_batch_info.get("guided_tx_cycle_id")
        system_id = dict_batch_info.get("system_id")
        company_id = dict_batch_info.get("company_id")
        filter_fields = dict_batch_info.get("filter_fields", None)
        sort_fields = dict_batch_info.get("sort_fields", None)
        inventory_data = dict()

        # validate batch id
        validate_guided_tx_cycle_id = validate_guided_tx_cycle_id_dao(guided_tx_cycle_id=guided_tx_cycle_id)
        if not validate_guided_tx_cycle_id:
            return error(14008)

        results, count, unique_drugs, alt_can_dic = get_transfer_cycle_drug_data(guided_tx_cycle_id=guided_tx_cycle_id,
                                                                                 company_id=company_id,
                                                                                 filter_fields=filter_fields,
                                                                                 sort_fields=sort_fields)
        for data in results:
            ndc_list.append(int(data['ndc']))
        if ndc_list:
            inventory_data_list = get_current_inventory_data(ndc_list=ndc_list, qty_greater_than_zero=False)
        if inventory_data_list:
            for record in inventory_data_list:
                inventory_data[record['ndc']] = record['quantity']

        for data in results:
            # to calculate max capacity of a canister
            if data['unit_weight'] is None:
                unit_weight = 0
                drug_calibration_status = "pending"
                max_refill_device_capacity = None
            else:
                unit_weight = data['unit_weight']
                drug_calibration_status = "done"
                max_refill_device_capacity = calculate_max_possible_drug_quantity_in_refill_device(
                    drug_unit_weight=unit_weight)

            # fetch canister capacity based on approx_volume of drug
            if data['approx_volume'] is None:
                max_canister_capacity = None
            else:
                type = data['canister_type']
                canister_volume = get_canister_volume(canister_type=type)
                max_canister_capacity = get_max_possible_drug_quantities_in_canister(
                    canister_volume=canister_volume,
                    unit_drug_volume=data['approx_volume'])
            record: dict = dict()
            record['drug_id'] = data['drug_id']
            record['id'] = data['canister_id']
            record['drug_name'] = data['drug_name_for_canister']
            record['image_name'] = data['image_name']
            record['ndc'] = data['ndc']
            record['formatted_ndc'] = data['formatted_ndc']
            record['txr'] = data['txr']
            record['is_powder_pill'] = data['is_powder_pill']
            record['display_location'] = data['display_location']
            record['location_number'] = data['location_number']
            record['available_quantity'] = data['available_quantity']
            record['canister_capacity'] = max_canister_capacity
            required_qty = int(unique_drugs[(data['canister_id'])])
            record['required_qty'] = required_qty
            record['expiry_status'] = data["expiry_status"]
            # replenish_quantity = required_qty - int(record['available_quantity'])
            # if replenish_quantity < 0:
            #     replenish_quantity = 0
            # record['replenish_required_quantity'] = replenish_quantity

            # adding packs which are in progress but yet not processed by robot.
            filling_pending_pack_ids = get_filling_pending_pack_ids(company_id=company_id)
            batch_required_quantity = get_canister_drug_quantity_required_in_batch(
                canister_id_list=[data['canister_id']],
                filling_pending_pack_ids=filling_pending_pack_ids)

            # Fetch drug quantity required in current batch and upcoming batch for particular canister
            if data['canister_id'] in alt_can_dic.keys():
                record['batch_required_quantity'] = batch_required_quantity.get(int(data['canister_id']),
                                                                                0) + required_qty
            else:
                record['batch_required_quantity'] = batch_required_quantity.get(int(data['canister_id']), 0)

            # to check if extra filling required for drug canister
            if data["drug_usage"] == constants.USAGE_FAST_MOVING:
                fill_extra = True
            else:
                fill_extra = False
            logger.info("In get_batch_guided_tx_drugs: record {}".format(record))
            canister_data.append(record.copy())

            drug_data_dict = {}
            if data['ndc'] not in list(drug_data.keys()):
                drug_data_dict['drug_id'] = data['drug_id']
                batch_required_quantity = get_canister_drug_quantity_required_in_batch(
                    canister_id_list=[data['canister_id']],
                    filling_pending_pack_ids=filling_pending_pack_ids)

                # Fetch drug quantity required in current batch and upcoming batch for particular canister
                if data['canister_id'] in alt_can_dic.keys():
                    drug_data_dict['batch_required_quantity'] = batch_required_quantity.get(int(data['canister_id']),
                                                                                            0) + required_qty
                else:
                    drug_data_dict['batch_required_quantity'] = batch_required_quantity.get(int(data['canister_id']), 0)

                drug_data_dict['required_qty'] = required_qty
                drug_data_dict['available_quantity'] = data['available_quantity']
                drug_data_dict['drug_name'] = data['drug_name_for_drug']
                drug_data_dict['strength'] = data['strength']
                drug_data_dict['strength_value'] = data['strength_value']
                drug_data_dict['ndc'] = data["ndc"]
                drug_data_dict['formatted_ndc'] = data["formatted_ndc"]
                drug_data_dict['txr'] = data["txr"]
                drug_data_dict["imprint"] = data["imprint"]
                drug_data_dict["image_name"] = data["image_name"]
                drug_data_dict["color"] = data["color"]
                drug_data_dict["shape"] = data["shape"]
                drug_data_dict["last_seen_by"] = data["last_seen_by"]
                drug_data_dict["last_seen_date"] = data["last_seen_date"]
                drug_data_dict["stock_updated_by"] = data["stock_updated_by"]
                drug_data_dict["stock_updated_on"] = data["stock_updated_on"]
                drug_data[data["ndc"]] = drug_data_dict
                drug_data_dict["unit_weight"] = unit_weight
                drug_data_dict['max_refill_device_capacity'] = max_refill_device_capacity
                drug_data_dict["drug_calibration_status"] = drug_calibration_status
                drug_data_dict["fill_extra"] = fill_extra
                drug_data_dict["inventory_qty"] = inventory_data.get(data['ndc'], 0)
                drug_data_dict['is_in_stock'] = 0 if drug_data_dict['inventory_qty'] <= 0 else 1
                drug_data_dict["unique_drug_id"] = data["unique_drug_id"]
                logger.info("drug_data_dict {}".format(drug_data_dict))
                drug_data[data['ndc']] = drug_data_dict
            else:
                # Fetch drug quantity required in current batch and upcoming batch for particular canister
                drug_data[data["ndc"]]['batch_required_quantity'] += record['batch_required_quantity']
                drug_data[data["ndc"]]['required_qty'] += required_qty
                drug_data[data["ndc"]]['available_quantity'] += data['available_quantity']
        response['canister_data'] = canister_data
        response['total_canister_count'] = count
        response['drug_data'] = drug_data
        response['total_drug_count'] = len(drug_data)

        return create_response(response)

    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting transfer replenish data")


@log_args_and_response
@validate(required_fields=["company_id", "system_id", "guided_tx_cycle_id", "canister_id", "guided_tx_flag"])
def skip_guided_tx_canister(args: dict) -> dict:
    """
    This method is used to skip a canister during guided transfer
    @param args:
    @return:
    """
    try:
        logger.info("In skip_guided_tx_canister")
        # company_id = args["company_id"]
        # system_id = args["system_id"]
        # guided_tx_flag = args.get("guided_tx_flag", False)
        guided_tx_cycle_id = args.get("guided_tx_cycle_id", None)
        canister_id = args.get("canister_id", None)

        status, response = trolley_data_for_guided_tx(canister_id=canister_id, guided_tx_cycle_id=guided_tx_cycle_id,
                                                      guided_tx_canister_status=constants.GUIDED_TRACKER_SKIPPED)
        if status:
            return create_response(response)
        else:
            return error(1020, str(response))

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("error in skip_guided_tx_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in skip_guided_tx_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in skip_guided_tx_canister: " + str(e))


@log_args_and_response
def update_guided_cycle_status(args: dict) -> dict:
    """
    This function updates the status in GuidedMeta table for the provided guided_tx_cycle_id
    @param args:dict
    @return dict
    """
    try:
        logger.info("In update_guided_cycle_status - args: " + str(args))
        company_id = args.get("company_id", None)
        guided_tx_cycle_id = args.get("guided_tx_cycle_id", None)
        # batch_id = args.get("batch_id", None)
        status = args.get("status", None)
        module_id = args.get("module_id", None)
        # from_app = args.get("from_app", False)
        transfer_done_from_portal = args.get("transfer_done_from_portal", None)
        # response = None

        # validate batch id
        validate_guided_tx_cycle_id = validate_guided_tx_cycle_id_dao(guided_tx_cycle_id=guided_tx_cycle_id)
        if not validate_guided_tx_cycle_id:
            return error(14016)

        # update the status for the given guided_tx_cycle_id
        if guided_tx_cycle_id and status:

            if status == constants.GUIDED_META_TO_CSR_DONE or (status == constants.GUIDED_META_DRUG_BOTTLE_FETCHED and
                                                               transfer_done_from_portal == False):
                logger.info("In update_guided_cycle_status: drug bottle fetched or to csr done")
                if status != constants.GUIDED_META_TO_CSR_DONE:
                    guided_tx_drug_skip_ids, guided_tracker_history_list, recommended_alternate_canisters \
                        = get_out_of_stock_tx_ids(guided_tx_cycle_id, 1, company_id)
                    logger.info(
                        'In update_guided_cycle_status: out of stock data: guided_tx_drug_skip_ids {} and guided_tracker_history_list {} '
                        'for guided_tx_cycle_id {}'.format(guided_tx_drug_skip_ids, guided_tracker_history_list,
                                                           guided_tx_cycle_id))
                    if guided_tx_drug_skip_ids:
                        update_status = update_guided_tracker_status(guided_tx_drug_skip_ids,
                                                                     constants.GUIDED_TRACKER_DRUG_SKIPPED)
                        history_status = add_data_in_guided_transfer_cycle_history(guided_tracker_history_list)

                        if recommended_alternate_canisters:
                            logger.info("In update_guided_cycle_status: "
                                        "removing reserved recommended_alternate_canisters: {}"
                                        .format(recommended_alternate_canisters))
                            remove_reserve_canister_status = \
                                remove_reserved_canisters(canister_list=recommended_alternate_canisters)
                            # ReservedCanister.db_remove_reserved_canister(canister_ids=
                            # recommended_alternate_canisters, batch_id=batch_id)

                            logger.info("update_guided_cycle_status: Removed reserved canister with status - {}"
                                         .format(remove_reserve_canister_status))

                    # check for any pending canisters in guided tracker if not then complete this cycle
                    pending_guided_tracker_data = get_guided_tracker_based_on_status(guided_cycle_id=guided_tx_cycle_id,
                                                                                     transfer_status_list=
                                                                                     [constants.GUIDED_TRACKER_PENDING])
                    if not pending_guided_tracker_data:
                        logger.info("update_guided_cycle_status: no pending guided tracker data so completing "
                                     "the current cycle")
                        status = constants.GUIDED_META_TO_CSR_DONE
                        module_id = constants.GUIDED_FETCH_DRUGS_MODULE

                logger.info("In update_guided_cycle_status: batch is in progress so check for replenish list")
                update_status = check_for_replenish_list_and_update_status(company_id=company_id,
                                                                           guided_tx_cycle_id=guided_tx_cycle_id,
                                                                           module_id=module_id,
                                                                           status=status,
                                                                           transfer_done_from_portal=transfer_done_from_portal)
                logger.info("In update_guided_cycle_status: replenish list check done")
            elif status == constants.GUIDED_META_DRUG_BOTTLE_FETCHED and transfer_done_from_portal == True:
                logger.info("Transfer from csr to cart is done and from robot to cart is pending")
                # case when updateguidedtxstatus api called when transfer from csr to trolley and
                # transfer from robot to trolley is yet to be done, Not checking for batch status and
                # replenish list here because API with this data get call only when there is some canisters to be
                # replenish in either of the robots
                # as per handling in GuidedCartDataFromDeviceTransfer API
                couchdb_update = update_guided_transfer_wizard_couch_db(company_id=company_id,
                                                                        module_id=module_id,
                                                                        transfer_done_from_portal=transfer_done_from_portal,
                                                                        update_status=status,
                                                                        next_cycle_id=None)
            elif status == constants.GUIDED_META_TO_ROBOT_DONE:
                logger.info("In update_guided_cycle_status: Transfer to robot done")
                # if batch_status not in settings.BATCH_PROCESSING_DONE_LIST:
                #     system_id = get_system_id_from_batch_id(batch_id=batch_id)
                #     update_replenish_based_on_system(system_id)
                #     logger.info("In update_guided_cycle_status: replenish queue updated")
                system_ids = get_system_id_from_pack_queue(company_id=company_id)
                if system_ids:
                    system_id=system_ids[0]
                    logger.info("In update_guided_cycle_status: updating replenish queue")
                    update_replenish_based_on_system(system_id)
                    logger.info("In update_guided_cycle_status: replenish queue updated")
                else:
                    logger.error("In update_guided_cycle_status, no packs in pack-queue.")
                # update guided meta as per normal flow
                guided_cycle_status_update, current_mini_batch = guided_cycle_status_for_update(
                    update_status=status,
                    guided_tx_cycle_id=guided_tx_cycle_id)
                logger.info("In update_guided_cycle_status: updating couch db")
                # update the couch db accordingly with the args provided
                update_status = update_guided_transfer_wizard_couch_db(company_id=company_id,
                                                                       module_id=module_id,
                                                                       transfer_done_from_portal=transfer_done_from_portal,
                                                                       update_status=status, next_cycle_id=None)
                logger.info("In update_guided_cycle_status: couch db updated")
            elif status == constants.GUIDED_META_TO_TROLLEY_DONE:
                logger.info("In update_guided_cycle_status: status to trolley done")
                batch_processing_done = False
                system_ids = get_system_id_from_pack_queue(company_id=company_id)
                if system_ids:
                    system_id = system_ids[0]
                    # fetch robot_data based on system_id
                    robot_data = get_robots_by_system_id_dao(system_id=system_id)
                else:
                    batch_processing_done = True

                # case when API called from wizard to_trolley_done, replenish_done
                if batch_processing_done:
                    logger.info("In update_guided_cycle_status: batch done")
                    status = constants.GUIDED_META_TO_ROBOT_DONE
                    module_id = constants.GUIDED_TO_CSR_MODULE
                    system_id = get_system_id_from_guided_tx_cycle_id(guided_tx_cycle_id=guided_tx_cycle_id)
                    # fetch robot_data based on system_id
                    robot_data = get_robots_by_system_id_dao(system_id=system_id)
                    for robot in robot_data:
                        all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids = \
                            fetch_guided_tracker_ids_based_on_destination_device(dest_device_id=robot["id"],
                                                                                 guided_tx_cycle_id=guided_tx_cycle_id,
                                                                                 transfer_status_list=
                                                                                 constants.guided_tracker_to_robot_status_list)
                        if all_guided_tracker_ids:
                            update_status = update_guided_tracker_status(
                                guided_tracker_ids=all_guided_tracker_ids,
                                status=constants.GUIDED_TRACKER_TRANSFER_SKIPPED)
                    logger.info("In update_guided_cycle_status: updating guided meta")
                    # update guided meta
                    guided_cycle_status_update, current_mini_batch = guided_cycle_status_for_update(
                        update_status=status,
                        guided_tx_cycle_id=guided_tx_cycle_id)

                    logger.info("In update_guided_cycle_status: updating couch db")
                    # update the wizard couch db document
                    update_status = update_guided_transfer_wizard_couch_db(company_id=company_id,
                                                                           module_id=module_id,
                                                                           transfer_done_from_portal=transfer_done_from_portal,
                                                                           update_status=status,
                                                                           next_cycle_id=None)
                else:
                    logger.info("In update_guided_cycle_status: Batch is in progress")
                    replenish_dict = dict()
                    replenish_required = False
                    for robot in robot_data:
                        replenish_dict[robot["id"]] = get_replenish_list_of_device(device_id=robot["id"],
                                                                                   system_id=system_id)
                        if replenish_dict[robot["id"]]:
                            replenish_required = True
                        else:
                            logger.info(
                                "In update_guided_cycle_status: replenish not required for device " + str(robot["id"]))
                            all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids = \
                                fetch_guided_tracker_ids_based_on_destination_device(dest_device_id=robot["id"],
                                                                                     guided_tx_cycle_id=guided_tx_cycle_id,
                                                                                     transfer_status_list=
                                                                                     constants.guided_tracker_to_robot_status_list)
                            if all_guided_tracker_ids:
                                update_status = update_guided_tracker_status(guided_tracker_ids=all_guided_tracker_ids,
                                                                             status=constants.GUIDED_TRACKER_TRANSFER_SKIPPED)
                    if not replenish_required:
                        logger.info("In update_guided_cycle_status: No more replenish required for both the robots")
                        status = constants.GUIDED_META_TO_ROBOT_DONE
                        module_id = constants.GUIDED_TO_CSR_MODULE

                    # update couch db and guided meta according to normal flow
                    guided_cycle_status_update, current_mini_batch = guided_cycle_status_for_update(
                        update_status=status,
                        guided_tx_cycle_id=guided_tx_cycle_id)
                    couchdb_update = update_guided_transfer_wizard_couch_db(company_id=company_id,
                                                                            module_id=module_id,
                                                                            transfer_done_from_portal=transfer_done_from_portal,
                                                                            update_status=status,
                                                                            next_cycle_id=None)
            elif status == constants.GUIDED_META_REPLENISH_DONE:
                logger.info("In update_guided_cycle_status: status for replenish done")

                batch_processing_done = False
                system_ids = get_system_id_from_pack_queue(company_id=company_id)
                if system_ids:
                    system_id = system_ids[0]
                    # fetch robot_data based on system_id
                    robot_data = get_robots_by_system_id_dao(system_id=system_id)
                else:
                    batch_processing_done = True
                # case when API called from wizard to_trolley_done, replenish_done
                if batch_processing_done:
                    logger.info("In update_guided_cycle_status: batch done")
                    status = constants.GUIDED_META_TO_ROBOT_DONE
                    module_id = constants.GUIDED_TO_CSR_MODULE
                    system_id = get_system_id_from_guided_tx_cycle_id(guided_tx_cycle_id=guided_tx_cycle_id)
                    # fetch robot_data based on system_id
                    robot_data = get_robots_by_system_id_dao(system_id=system_id)
                    for robot in robot_data:
                        all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids = \
                            fetch_guided_tracker_ids_based_on_destination_device(dest_device_id=robot["id"],
                                                                                 guided_tx_cycle_id=guided_tx_cycle_id,
                                                                                 transfer_status_list=
                                                                                 constants.guided_tracker_to_robot_status_list)
                        if all_guided_tracker_ids:
                            update_status = update_guided_tracker_status(
                                guided_tracker_ids=all_guided_tracker_ids,
                                status=constants.GUIDED_TRACKER_TRANSFER_SKIPPED)
                    logger.info("In update_guided_cycle_status: updating guided meta")
                    # update guided meta
                    guided_cycle_status_update, current_mini_batch = guided_cycle_status_for_update(
                        update_status=status,
                        guided_tx_cycle_id=guided_tx_cycle_id)

                    logger.info("In update_guided_cycle_status: updating couch db")
                    # update the wizard couch db document
                    update_status = update_guided_transfer_wizard_couch_db(company_id=company_id,
                                                                           module_id=module_id,
                                                                           transfer_done_from_portal=transfer_done_from_portal,
                                                                           update_status=status,
                                                                           next_cycle_id=None)
                else:
                    logger.info("In update_guided_cycle_status: Batch is in progress")
                    # replenish_dict = dict()
                    # replenish_required = False
                    # for robot in robot_data:
                    #     replenish_dict[robot["id"]] = get_replenish_list_of_device(device_id=robot["id"],
                    #                                                                system_id=system_id)
                    #     if replenish_dict[robot["id"]]:
                    #         replenish_required = True
                    #     else:
                    #         logger.info(
                    #             "update_guided_cycle_status: replenish not required for device " + str(robot["id"]))
                    #         all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids = \
                    #             fetch_guided_tracker_ids_based_on_destination_device(dest_device_id=robot["id"],
                    #                                                                  guided_tx_cycle_id=guided_tx_cycle_id,
                    #                                                                  transfer_status_list=
                    #                                                                  constants.guided_tracker_to_robot_status_list)
                    #         if all_guided_tracker_ids:
                    #             update_status = update_guided_tracker_status(guided_tracker_ids=all_guided_tracker_ids,
                    #                                                          status=constants.GUIDED_TRACKER_TRANSFER_SKIPPED)
                    # if not replenish_required:
                    #     logger.info("update_guided_cycle_status: No more replenish required for both the robots")
                    #     status = constants.GUIDED_META_TO_ROBOT_DONE
                    #     module_id = constants.GUIDED_TO_CSR_MODULE

                    # update couch db and guided meta according to normal flow
                    guided_cycle_status_update, current_mini_batch = guided_cycle_status_for_update(
                        update_status=status,
                        guided_tx_cycle_id=guided_tx_cycle_id)
                    couchdb_update = update_guided_transfer_wizard_couch_db(company_id=company_id,
                                                                            module_id=module_id,
                                                                            transfer_done_from_portal=transfer_done_from_portal,
                                                                            update_status=status,
                                                                            next_cycle_id=None)
            else:
                return error(1020, "Invalid status")
            return create_response(settings.SUCCESS_RESPONSE)
        else:
            return error(1000, "Invalid value of guided_tx_cycle_id or batch_id or status")

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except RealTimeDBException as e:
        logger.error(e)
        return error(1013)

    except Exception as e:
        logger.error(e)
        return error(1000, "Error in updating cycle status: " + str(e))


@log_args_and_response
def update_on_batch_done(batch_id: int, company_id: int, transfer_done_from_portal: bool, status: int):
    """
    Method to update replenish flow status when current batch is done
    @param batch_id:
    @param company_id:
    @param transfer_done_from_portal:
    @param status:
    @return:
    """
    try:
        logger.info("In update_on_batch_done")
        # update guided meta
        gm_update_status = update_guided_meta_status_by_batch(status=status)
        logger.info("update_on_batch_done: guided meta status updated now flush guided tracker data")
        # flush guided tracker when batch and guided flow completed
        # todo-uncomment below when we change structure of guided_transfer_cycle_history
        # gt_update_status = delete_from_guided_tracker(batch_id=batch_id)
        logger.info("update_on_batch_done: guided tracker data deleted, now update couch db")
        couch_db_response = reset_couch_db_on_cycle_completion(batch_id=batch_id, company_id=company_id,
                                                               transfer_done_from_portal=transfer_done_from_portal,
                                                               module_id=constants.GUIDED_FETCH_DRUGS_MODULE,
                                                               update_status=constants.GUIDED_META_TO_CSR_DONE,
                                                               next_cycle_id=None)
        logger.info("update_on_batch_done: Couch db reset done")
        return couch_db_response
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e

    except Exception as e:
        logger.error(e)
        raise e


@log_args_and_response
def check_for_replenish_list_and_update_status(company_id: int, guided_tx_cycle_id: int, module_id: int,
                                               status: int, transfer_done_from_portal: bool):
    try:
        logger.info("In check_for_replenish_list_and_update_status")
        response = None
        system_ids = get_system_id_from_pack_queue(company_id=company_id)
        if system_ids:
            system_id = system_ids[0]
        else:
            logger.error("Error in check_for_replenish_list_and_update_status, no packs in pack-queue.")
            return
        # fetch robot_data based on system_id
        robot_data = get_robots_by_system_id_dao(system_id=system_id)
        replenish_required = False
        replenish_dict = dict()
        for robot in robot_data:
            replenish_dict[robot["id"]] = get_replenish_list_of_device(device_id=robot["id"], system_id=system_id)
            if replenish_dict[robot["id"]]:
                replenish_required = True
        if replenish_required:
            logger.info("check_for_replenish_list_and_update_status: replenish required so updating status")
            # if replenish is required in any of the device then update guided meta as per normal and
            # guided tracker according to replenish list
            for device_id, replenish_list in replenish_dict.items():
                if not replenish_list:
                    # Replenish not required in a device so change the status of all pending canisters as skipped
                    all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids = \
                        fetch_guided_tracker_ids_by_destination_device_and_batch(dest_device_id=device_id,
                                                                                 batch_id=guided_tx_cycle_id,
                                                                                 transfer_status_list=
                                                                                 [constants.GUIDED_TRACKER_PENDING,
                                                                                  constants.GUIDED_TRACKER_REPLENISH,
                                                                                  constants.GUIDED_TRACKER_SKIPPED])
                    if all_guided_tracker_ids:
                        update_status = update_guided_tracker_status(guided_tracker_ids=all_guided_tracker_ids,
                                                                     status=constants.GUIDED_TRACKER_TRANSFER_AND_REPLENISH_SKIPPED)

            logger.info("check_for_replenish_list_and_update_status: updating couch db")
            # update couch db and guided meta as per normal flow
            guided_cycle_status_update, current_mini_batch = guided_cycle_status_for_update(update_status=status,
                                                                                            guided_tx_cycle_id=guided_tx_cycle_id)
            if status == constants.GUIDED_META_TO_CSR_DONE:
                # obtain the next cycle id for the current mini_batch of the batch_id
                next_cycle_id = get_next_cycle_id(current_mini_batch=current_mini_batch)
                response = reset_couch_db_on_cycle_completion(company_id=company_id,
                                                              transfer_done_from_portal=transfer_done_from_portal,
                                                              update_status=status,
                                                              module_id=module_id,
                                                              next_cycle_id=next_cycle_id)
            else:
                coucdb_update = update_guided_transfer_wizard_couch_db(company_id=company_id,
                                                                       module_id=module_id,
                                                                       transfer_done_from_portal=transfer_done_from_portal,
                                                                       update_status=status,
                                                                       next_cycle_id=None)
        else:
            # if replenish is not required in any robot then mark complete
            # here we can remove batch because if replenish not required than we can update status in guided meta to csr done.
            gm_update_status = update_guided_meta_status_by_batch(status=constants.GUIDED_META_TO_CSR_DONE)

            logger.info("update_guided_cycle_status: updating couch db")
            response = reset_couch_db_on_cycle_completion(company_id=company_id,
                                                          transfer_done_from_portal=transfer_done_from_portal,
                                                          update_status=constants.GUIDED_META_TO_CSR_DONE,
                                                          module_id=constants.GUIDED_FETCH_DRUGS_MODULE,
                                                          next_cycle_id=None)
            logger.info("update_guided_cycle_status: Couch db reset done")
        return True
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e

    except RealTimeDBException as e:
        raise e

    except Exception as e:
        logger.error(e)
        raise e


@log_args_and_response
def update_guided_cycle_for_batch_done(args):
    args.update({"status": constants.GUIDED_META_TO_CSR_DONE,
                 "module_id": constants.GUIDED_FETCH_DRUGS_MODULE,
                 "transfer_done_from_portal": False})
    update_response = update_guided_cycle_status(args)
    logger.info("get_pending_cycle_data_based_on_status: update done")
    parsed_response = json.loads(update_response)
    if parsed_response["status"] == settings.SUCCESS_RESPONSE:
        return True, update_response, None, None
    else:
        return False, update_response, None, None


@log_args_and_response
def get_trolley_drawer_from_serial_number(trolley_serial_number, drawer_serial_number, company_id):
    """
    Function to get trolley id and container (drawer) id from serial number
    @param trolley_serial_number: str
    @param drawer_serial_number: str
    @param company_id: int
    @return: int, int
    """
    logger.info("In get_trolley_drawer_from_serial_number")
    try:
        trolley_id = None
        trolley_drawer_id = None

        if trolley_serial_number:
            trolley_id = get_device_id_from_serial_number(trolley_serial_number, company_id)
            logger.info("trolley_id {}".format(trolley_id))

        if drawer_serial_number:
            trolley_drawer_id = get_drawer_id_from_serial_number(drawer_serial_number, company_id=company_id)
            logger.info("drawer_id {}".format(trolley_drawer_id))
        return trolley_id, trolley_drawer_id

    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting device from serial number")


@log_args_and_response
def get_extra_locations_count(no_of_drawers: int, partition_list: list,
                              no_of_locations_in_each_container: int) -> int:
    """

    @param no_of_drawers:
    @param partition_list:
    @param no_of_locations_in_each_container:
    @return:
    """
    try:
        exact_required_drawer_count = 0
        pending_locations_list = list()
        for item in partition_list:
            exact_required_drawer_count = exact_required_drawer_count + (
                    int(item) // int(no_of_locations_in_each_container))
            pending_locations_list.append(int(item) % int(no_of_locations_in_each_container))

        pending_sorted_list = sorted(pending_locations_list, reverse=True)

        if exact_required_drawer_count == no_of_drawers:
            # return direct sum of pending_sorted_list which are unable to fit in given no_of_drawers
            return sum(pending_sorted_list)
        elif exact_required_drawer_count < no_of_drawers:
            # in this case, use empty drawers to pending_sorted_list
            # first find diff of exact_required_drawer_count and no_of_drawers to get empty drawers
            empty_drawers_count = no_of_drawers - exact_required_drawer_count

            # so reserve first "empty_drawers_count" drawers of pending_sorted_list
            return sum(pending_sorted_list[empty_drawers_count:])
        else:
            # case when exact_required_drawer_count > no_of_drawers
            extra_drawers_count = exact_required_drawer_count - no_of_drawers

            # add locations used in extra drawers
            return (sum(pending_sorted_list)) + (extra_drawers_count * no_of_locations_in_each_container)

    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def reset_couch_db_on_cycle_completion(company_id: int, transfer_done_from_portal: bool,
                                       module_id: int, update_status: int, next_cycle_id: int = None) -> bool:
    """
    Method to reset couch db transfer doc and wozard doc
    @param batch_id:
    @param company_id:
    @param transfer_done_from_portal:
    @param module_id:
    @param update_status:
    @param next_cycle_id:
    @return:
    """
    try:
        logger.info("In reset_couch_db_on_cycle_completion")
        # update the wizard couch db document
        update_guided_transfer_wizard_couch_db(company_id=company_id,
                                               module_id=module_id,
                                               transfer_done_from_portal=transfer_done_from_portal,
                                               update_status=update_status,
                                               next_cycle_id=next_cycle_id)
        # obtain the system_device dict in order to reset the couch db
        system_device_dict = get_system_device_for_batch()
        response = reset_couch_db_for_done_cycle(reset_couch_db_dict=system_device_dict)
        logger.info("In reset_couch_db_on_cycle_completion: Done")
        return response

    except RealTimeDBException as e:
        raise e

    except Exception as e:
        raise e


@log_args_and_response
def verify_canister_location_and_update_couch_db(canister_info, system_id, device_id, user_id, status_to_update=None):
    """
    Function to update guided canister transfer count in couch db
    @param canister_info: dict
    @param system_id: int
    @param device_id: int
    @param user_id: int
    @param status_to_update
    @return: status
    """
    try:
        guided_history_list = list()
        system_device_dict = dict()

        for canister, canister_location_info in canister_info.items():
            canister_removed = canister_location_info['canister_removed']
            location_id = canister_location_info['id']
            current_device_id = canister_location_info['device_id']
            current_device_drawer = canister_location_info['container_id']
            canister_data = db_get_latest_guided_canister_transfer_data(canister)
            new_loc_id = None
            flow = None

            if canister_data:
                if not canister_removed and canister_data["guided_meta_status"] >= constants.GUIDED_META_REPLENISH_DONE:
                    # case when canister is placed in robot
                    # change transfer status and update location only if replenish is done to prevent
                    # status change when transfer to cart flow is going on
                    if canister == canister_data['source_canister_id']:
                        if canister_location_info['device_to_update'] == canister_data['dest_device'] and \
                                canister_location_info['quadrant_to_update'] == canister_data['dest_quadrant'] and \
                                not (canister_location_info["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and
                                     canister_location_info["drawer_type"] == settings.SIZE_OR_TYPE["SMALL"]):
                            if canister_data["transfer_status"] == constants.GUIDED_TRACKER_SKIPPED:
                                new_transfer_status = constants.GUIDED_TRACKER_SKIPPED_AND_DONE
                            else:
                                new_transfer_status = constants.GUIDED_TRACKER_DONE
                            update_status = update_guided_tracker_status([canister_data['guided_tracker_id']],
                                                                         new_transfer_status)
                            logger.info(update_status)

                            # add data in guided transfer cycle history tables
                            insert_data = {'guided_tracker_id': canister_data['guided_tracker_id'],
                                           'canister_id': canister,
                                           'action_id': constants.GUIDED_TRACKER_TRANSFER_ACTION,
                                           'current_status_id': new_transfer_status,
                                           'previous_status_id': canister_data['transfer_status'],
                                           'action_taken_by': user_id,
                                           'action_datetime': get_current_date_time()
                                           }

                            guided_history_list.append(insert_data)

                    if canister == canister_data['alternate_canister_id']:
                        source_canister = canister_data["source_canister_id"]
                        source_location_info = get_location_details_by_canister_id(
                            canister_id=source_canister)

                        # check if canister placed at proper loc
                        if canister_location_info['device_to_update'] == canister_data['dest_device'] and \
                                canister_location_info['quadrant_to_update'] == canister_data['dest_quadrant'] and \
                                not (canister_location_info["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and
                                     canister_location_info["drawer_type"] == settings.SIZE_OR_TYPE["SMALL"]):

                            # check if source canister is placed back to trolley or on-shelf
                            if not source_location_info or (source_location_info
                                                            and source_location_info['device_id'] == canister_data[
                                                                'trolley_id']):
                                # change status as source is placed in trolley and alternate in robot
                                if canister_data["transfer_status"] == constants.GUIDED_TRACKER_SKIPPED:
                                    replaced_transfer_status = constants.GUIDED_TRACKER_SKIPPED_AND_REPLACED
                                else:
                                    replaced_transfer_status = constants.GUIDED_TRACKER_REPLACED

                                update_status = update_guided_tracker_status([canister_data['guided_tracker_id']],
                                                                             replaced_transfer_status)
                                logger.info(update_status)
                                # update cart location in guided tracker only when transfer of both
                                # source and alternate canister done to respective destination

                                if source_location_info:
                                    cart_location_update_status = update_guided_tracker(
                                        update_dict={"cart_location_id": source_location_info["id"]},
                                        guided_tracker_id=canister_data['guided_tracker_id'])

                                # add data in guided transfer cycle history tables
                                insert_data = {'guided_tracker_id': canister_data['guided_tracker_id'],
                                               'canister_id': canister,
                                               'action_id': constants.GUIDED_TRACKER_TRANSFER_ACTION,
                                               'current_status_id': replaced_transfer_status,
                                               'previous_status_id': canister_data['transfer_status'],
                                               'action_taken_by': user_id,
                                               'action_datetime': get_current_date_time()
                                               }

                                guided_history_list.append(insert_data)

                            status = replace_canister_in_pack_analysis_details(system_id=system_id,
                                                                               original_canister=canister_data[
                                                                                   'source_canister_id'],
                                                                               new_canister=canister_data[
                                                                                   "alternate_canister_id"])
                            # changing canister in canister transfers
                            batch_id = get_progress_batch_id(system_id)
                            # canister_transfer_status = CanisterTransfers.db_replace_canister(
                            #     batch_id=batch_id, canister_id=canister_data['source_canister_id'],
                            #     alt_canister_id=canister_data["alternate_canister_id"])
                            canister_transfer_status = \
                                db_replace_canister_in_canister_transfers(batch_id, canister_data['source_canister_id'],
                                                                          canister_data["alternate_canister_id"])
                            logger.info(status)

                elif canister_removed:
                    # case when canister is removed from robot

                    if canister == canister_data['source_canister_id'] and canister_data["alternate_canister_id"] and \
                            canister_data["guided_meta_status"] >= constants.GUIDED_META_REPLENISH_DONE:
                        logger.info("guided_replenish - removed source canister for replacement")
                        # fetch scanned drawer location only when source canister
                        args = {"device_id": device_id, "system_id": system_id}
                        currently_scanned_drawer_id = fetch_scanned_drawer_in_guided_tx_flow(args=args)
                        logger.info("guided_replenish - removed source canister for replacement- "
                                     "currently_scanned_drawer_id - {}".format(currently_scanned_drawer_id))
                        if currently_scanned_drawer_id:
                            empty_locations_of_scanned_drawer = get_empty_locations_of_drawer(
                                drawer_id=currently_scanned_drawer_id)
                            if empty_locations_of_scanned_drawer:
                                new_loc_id = empty_locations_of_scanned_drawer.pop(0)
                        logger.info("guided_replenish - removed source canister for replacement- "
                                     "empty_locations_of_scanned_drawer - {}".format(empty_locations_of_scanned_drawer))
                    else:
                        logger.info("guided_replenish - removed source or alternate canister - {}".format(canister))
                        new_loc_id = canister_data["cart_location_id"]

                    if new_loc_id:
                        logger.info("assigning cart location to canister - {}, location_id - {}".format(canister,
                                                                                                         new_loc_id))
                        status = assign_cart_location_to_canister(canister, new_loc_id)
                        logger.info("assign_cart_location_to_canister - status {} for canister - {}, location_id - {}"
                                    .format(status, canister, new_loc_id))
                        update_status = update_guided_tracker_status([canister_data['guided_tracker_id']],
                                                                     constants.GUIDED_TRACKER_TO_TROLLEY_DONE)
                        logger.info("transfer status updated in guided {}".format(update_status))

                    # to check if the canister is removed for replacing or replenish, if removed for replacing
                    # then change its status accordingly
                    if canister_data["alternate_canister_id"] and \
                            canister_data["guided_meta_status"] >= constants.GUIDED_META_REPLENISH_DONE:
                        # change transfer status and update location only if replenish is done to prevent
                        # status change when transfer to cart flow is going on
                        alternate_location_info = get_location_details_by_canister_id(
                            canister_id=canister_data["alternate_canister_id"])

                        # check if alternate is placed in robot and source is removed
                        if alternate_location_info['device_id'] == canister_data['dest_device'] and \
                                alternate_location_info['quadrant'] == canister_data['dest_quadrant']:

                            if canister_data["transfer_status"] == constants.GUIDED_TRACKER_SKIPPED:
                                replaced_transfer_status = constants.GUIDED_TRACKER_SKIPPED_AND_REPLACED
                            else:
                                replaced_transfer_status = constants.GUIDED_TRACKER_REPLACED

                            update_status = update_guided_tracker_status([canister_data['guided_tracker_id']],
                                                                         replaced_transfer_status)
                            logger.info(update_status)

                            # add data in guided transfer cycle history tables
                            insert_data = {'guided_tracker_id': canister_data['guided_tracker_id'],
                                           'canister_id': canister,
                                           'action_id': constants.GUIDED_TRACKER_TRANSFER_ACTION,
                                           'current_status_id': replaced_transfer_status,
                                           'previous_status_id': canister_data['transfer_status'],
                                           'action_taken_by': user_id,
                                           'action_datetime': get_current_date_time()
                                           }

                            guided_history_list.append(insert_data)

                            # update cart location in guided tracker only when transfer of both
                            # source and alternate canister done to respective destination
                            if new_loc_id:
                                cart_location_update_status = update_guided_tracker(
                                    update_dict={"cart_location_id": new_loc_id},
                                    guided_tracker_id=canister_data['guided_tracker_id'])

                    # no need to handle below case now as now we are assigning cart location of guided tracker only
                    # else:
                    #     # source canister removed for replenish
                    #     if new_loc_id:
                    #         cart_location_update_status = update_guided_tracker(
                    #             update_dict={"cart_location_id": new_loc_id},
                    #             guided_tracker_id=canister_data['guided_tracker_id'])

                # update couch db according to current wizard
                system_device_dict[system_id] = device_id
                if canister_data['dest_device'] != device_id:
                    system_device_dict[canister_data["dest_system_id"]] = canister_data['dest_device']
                logger.info("verify_canister_location_and_update_couch_db system_device_dict {}"
                            .format(system_device_dict))

                for cdb_system_id, cdb_device_id in system_device_dict.items():
                    couch_db_update = guided_transfer_couch_db_timestamp_update(cdb_system_id, cdb_device_id)
                    logger.info("couch_db_update {}".format(couch_db_update))

            else:
                # if canister is not use in guided but reserved for batch then add canister data in
                # guided misplaced canister table
                response = add_data_in_guided_misplaced_canister(canister, canister_location_info, system_id,
                                                                 device_id, canister_removed)
                logger.info("In verify_canister_location_and_update_couch_db: guided misplaced canister data "
                            "added in table: {}".format(response))
        #  add guided transfer history data in transfer history tables
        if len(guided_history_list):
            response = add_data_in_guided_transfer_cycle_history(insert_data=guided_history_list)
            logger.info("add_data_in_guided_transfer_cycle_history response {}".format(response))

        return True

    except Exception as e:
        logger.error(1000, "Error in updating couch db for guided transfer")
        return e

# commenting below method as we are not using it now
# @log_args_and_response
# def verify_csr_canister_location_and_update_couch_db_in_guided(canister_info, system_id, device_id):
#     """
#     Function to verify if canister update is during guided transfer flow and update couch db
#     accordingly
#     @param canister_info: dict
#     @param system_id: int
#     @param device_id: int
#     @return: status
#     """
#     try:
#         for canister, canister_location_info in canister_info.items():
#             canister_removed = canister_location_info['canister_removed']
#             canister_data = db_get_latest_guided_canister_transfer_data(canister)
#             if canister_data:
#                 if not canister_removed:
#                     # case when canister is placed in csr
#                     if canister_location_info['csr_container_id'] == canister_data['dest_container_id']:
#                         if canister_data["transfer_status"] == constants.GUIDED_TRACKER_SKIPPED_AND_REPLACED:
#                             done_transfer_status = constants.GUIDED_TRACKER_SKIPPED_AND_DONE
#                         else:
#                             done_transfer_status = constants.GUIDED_TRACKER_DONE
#                         update_status = update_guided_tracker_status([canister_data['guided_tracker_id']],
#                                                                      done_transfer_status)
#                 elif canister_removed:
#                     args = {"device_id": device_id, "system_id": system_id}
#                     currently_scanned_drawer_id = fetch_scanned_drawer_in_guided_tx_flow(args=args)
#                     if currently_scanned_drawer_id:
#                         empty_locations_of_scanned_drawer = get_empty_locations_of_drawer(
#                             drawer_id=currently_scanned_drawer_id)
#                         if empty_locations_of_scanned_drawer:
#                             new_loc_id = empty_locations_of_scanned_drawer.pop(0)
#                             status = assign_cart_location_to_canister(canister, new_loc_id)
#                             logger.info("assign_cart_location_to_canister {}".format(status))
#
#                 # update couch db according to current wizard
#                 if canister_data["guided_meta_status"] == constants.GUIDED_META_DRUG_BOTTLE_FETCHED:
#                     # Drug bottle fetched means that we are in transfer to cart wizard
#                     cdb_system_id = system_id
#                     cdb_device_id = device_id
#                 elif canister_data["guided_meta_status"] == constants.GUIDED_META_TO_ROBOT_DONE:
#                     # Replenish done means that we are in wizard transfer to robot
#                     cdb_system_id = canister_data["dest_system_id"]
#                     cdb_device_id = canister_data['dest_device']
#                 else:
#                     cdb_system_id = None
#                     cdb_device_id = None
#
#                 if cdb_system_id and cdb_device_id:
#                     couch_db_update = guided_transfer_couch_db_timestamp_update(cdb_system_id, cdb_device_id)
#                     logger.info("couch_db_update {}".format(couch_db_update))
#                 else:
#                     logger.info("No need to update couch_db")
#
#         return True
#
#     except Exception as e:
#         logger.error("Error in verify_csr_canister_location_and_update_couch_db_in_guided {}".format(e))
#         return False


@log_args_and_response
def reset_couch_db_for_done_cycle(reset_couch_db_dict: dict) -> bool:
    """
    This function resets the couch db for the given system and device_id when transfer to CSR for guided_tx_cycle is done
    @param reset_couch_db_dict: dict
    @return bool
    """

    for system_id, device_ids in reset_couch_db_dict.items():
        for device_id in device_ids:
            document_name = str(constants.GUIDED_TRANSFER_DOCUMENT_NAME) + '_{}'.format(device_id)
            reset_couch_db_dict_for_reset = {"system_id": system_id,
                                             "document_name": document_name,
                                             "couchdb_level": constants.STRING_SYSTEM,
                                             "key_name": "data"}
            reset_couch_db_document(reset_couch_db_dict_for_reset)

    return True


@log_args_and_response
@validate(required_fields=["device_id", "module_id", "user_id", "company_id", "system_id", "comments",
                           "canisters_to_skip"])
def guided_transfer_skip(args: dict) -> str:
    """
    Function to skip canister to transfer to robot or CSR
    @param args:
    @return:
    """
    try:
        # batch_id = args['batch_id']
        company_id = args['company_id']
        system_id = args['system_id']
        module_id = args['module_id']
        device_id = args['device_id']
        user_id = args['user_id']
        comments = args['comments']
        call_from_portal = args.get('call_from_portal', False)
        canisters_to_skip = args['canisters_to_skip']
        alt_canister = args.get('alt_canister', None)
        deactive_canister = args.get('deactive_canister', False)
        deactive_comments = args.get('deactive_comments', '')
        pending_transfer_list = args.get('pending_transfer_list', False)
        misplaced_canister = args.get('misplaced_canister', False)  # true when call for misplaced canister in guided
        guided_tx_cycle_id = args.get("guided_tx_cycle_id", False)

        # first validate company id ,system id , batch id , device id then convert it to int otherwise it gives 500 error
        valid_device_with_company_id = validate_device_ids_with_company(device_ids=[args["device_id"]],
                                                                        company_id=args["company_id"])
        if not valid_device_with_company_id:
            return error(9059)

        valid_device_with_system_id = verify_device_id_list_dao(device_id=[args["device_id"]], system_id=args["system_id"])
        if not valid_device_with_system_id:
            return error(1015)

        if guided_tx_cycle_id:
            validate_guided_tx_cycle_id = validate_guided_tx_cycle_id_dao(guided_tx_cycle_id=guided_tx_cycle_id)
            if not validate_guided_tx_cycle_id:
                return error(14016)

        if misplaced_canister:
            for canister_id in canisters_to_skip:
                # function to check canister is present in guided misplaced canister table or not  if it is then
                # remove canister from table
                status = check_if_canister_data_exit_dao(canister_id=canister_id,
                                                         device_id=device_id,
                                                         guided_meta_id=guided_tx_cycle_id)

                logger.info("In guided_transfer_skip: canister_id: {} is already present in guided_misplaced_canister "
                            "table:{}".format(canister_id, status))

                # if canister is available in table then delete record from table
                if status:
                    status = db_delete_canister_data_dao(canister_id=canister_id, device_id=device_id,
                                                         guided_meta_id=guided_tx_cycle_id)

                    logger.info("In guided_transfer_skip: canister_id: {} is deleted from guided_misplaced_canister "
                                "table:{}".format(canister_id, status))

                if deactive_canister:
                    status = delete_canister_dao({"canister_id": canister_id,
                                                  "company_id": company_id,
                                                  "user_id": user_id,
                                                  "comment": deactive_comments})
                    logger.info("In guided_transfer_skip: misplaced canister: {} is deactivated: {}"
                                .format(canister_id, status))

            return create_response(True)

        existing_canisters_data, guided_tracker_ids = db_get_existing_guided_canister_transfer_data(
            canister_list=canisters_to_skip,
            filter_status=None)

        if not len(existing_canisters_data):
            return error(0)

        if module_id == constants.GUIDED_TO_TROLLEY_MODULE:
            logger.info("canister_transfer_skip when transfer to trolley was ongoing for {}".format(module_id))
            if alt_canister:
                if pending_transfer_list:
                    skip_status = constants.GUIDED_TRACKER_TO_TROLLEY_TRANSFER_LATER_SKIP
                    # mark the canister location as null if user skip while transferring to csr
                    for canister_id in canisters_to_skip:
                        args_dict = {"canister_id": int(canister_id), "location_id": None,
                                     "company_id": int(company_id), "user_id": user_id}

                        response = update_canister_location(args_dict)
                        logger.info("guided_transfer_skip: canister - {} , updated location as null with response- {}"
                                     .format(canister_id, response))

                else:
                    skip_status = constants.GUIDED_TRACKER_TO_TROLLEY_SKIPPED_AND_ALTERNATE

                for index, canister in enumerate(canisters_to_skip):
                    # if pending_transfer_list:
                    #     transfer_status = constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE_TRANSFER_LATER
                    # else:
                    transfer_status = constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE
                    # update status in current flow and add new entry for new alternate canister
                    alt_added_status = update_guided_tracker(
                        update_dict={"transfer_status": skip_status},
                        guided_tracker_id=existing_canisters_data[canister]['guided_tracker_id'])

                    # add new record for new alternate canister
                    replenish_record = {"guided_meta_id": existing_canisters_data[canister]['guided_meta_id'],
                                        "source_canister_id": existing_canisters_data[canister]['source_canister_id'],
                                        "alternate_canister_id": alt_canister[index],
                                        "alt_can_replenish_required": True,
                                        "cart_location_id": existing_canisters_data[canister]['cart_location_id'],
                                        "destination_location_id": existing_canisters_data[canister]['destination_location_id'],
                                        "transfer_status": transfer_status,
                                        "required_qty": existing_canisters_data[canister]['required_qty']}
                    status = add_records_in_guided_tracker([replenish_record])
                    logger.info("recommendguidedtx: added records in guided_tacker with status- " + str(status))

                    # ReservedCanister.db_replace_canister(batch_id, canister, alt_canister[index])
                    db_reserved_canister_replace_canister(canister_id=canister,
                                                          alt_canister_id=alt_canister[index])
                    logger.info("Alternate canister replaced in reserved canister")

            else:
                if pending_transfer_list:
                    skip_status = constants.GUIDED_TRACKER_TO_TROLLEY_TRANSFER_LATER_SKIP
                else:
                    skip_status = constants.GUIDED_TRACKER_TO_TROLLEY_SKIPPED
                guided_tx_status = update_guided_tracker_status(guided_tracker_ids=guided_tracker_ids,
                                                                status=skip_status)

        elif module_id == constants.GUIDED_TO_DRUG_DISPENSER_MODULE:
            logger.info("canister_transfer_skip when transfer from trolley to robot was ongoing")

            if alt_canister:
                if pending_transfer_list:
                    skip_status = constants.GUIDED_TRACKER_TO_ROBOT_TRANSFER_LATER_SKIP
                else:
                    skip_status = constants.GUIDED_TRACKER_TO_ROBOT_SKIPPED_AND_ALTERNATE

                # mark the canister location as null if user skip while transferring to robot
                for canister_id in canisters_to_skip:
                    args_dict = {"canister_id": int(canister_id), "location_id": None,
                                 "company_id": int(company_id), "user_id": user_id}

                    response = update_canister_location(args_dict)
                    logger.info("guided_transfer_skip: canister - {} , updated location as null with response- {}"
                                 .format(canister_id, response))

                for index, canister in enumerate(canisters_to_skip):
                    update_dict = {"transfer_status": skip_status}

                    # if pending_transfer_list:
                    #     transfer_status = constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE_TRANSFER_LATER
                    # else:
                    transfer_status = constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE
                    alt_added_status = update_guided_tracker(
                        update_dict={"transfer_status": skip_status},
                        guided_tracker_id=existing_canisters_data[canister]['guided_tracker_id'])
                    # add new record for new alternate canister
                    replenish_record = {"guided_meta_id": existing_canisters_data[canister]['guided_meta_id'],
                                        "source_canister_id": existing_canisters_data[canister]['source_canister_id'],
                                        "alternate_canister_id": alt_canister[index],
                                        "cart_location_id": existing_canisters_data[canister]['cart_location_id'],
                                        "destination_location_id": existing_canisters_data[canister][
                                            'destination_location_id'],
                                        "transfer_status": transfer_status}
                    status = add_records_in_guided_tracker([replenish_record])
                    logger.info("recommendguidedtx: added records in guided_tacker with status- " + str(status))

                    # ReservedCanister.db_replace_canister(batch_id, canister, alt_canister[index])
                    db_reserved_canister_replace_canister(canister_id=canister,
                                                          alt_canister_id=alt_canister[index])
                    logger.info("Alternate canister replaced in reserved canister")

            else:
                if pending_transfer_list:
                    skip_status = constants.GUIDED_TRACKER_TO_ROBOT_TRANSFER_LATER_SKIP
                else:
                    skip_status = constants.GUIDED_TRACKER_TO_ROBOT_SKIPPED
                guided_tx_status = update_guided_tracker_status(guided_tracker_ids=guided_tracker_ids,
                                                                status=skip_status)

        elif module_id == constants.GUIDED_TO_CSR_MODULE:
            logger.info("canister_transfer_skip when transfer from trolley to CSR was ongoing")
            skip_status = constants.GUIDED_TRACKER_TO_CSR_SKIPPED
            guided_tx_status = update_guided_tracker_status(guided_tracker_ids=guided_tracker_ids,
                                                            status=skip_status)
            # mark the canister location as null if user skip while transferring to csr
            for canister_id in canisters_to_skip:
                args_dict = {"canister_id": int(canister_id), "location_id": None,
                             "company_id": int(company_id), "user_id": user_id}

                response = update_canister_location(args_dict)
                logger.info("guided_transfer_skip: canister - {} , updated location as null with response- {}"
                             .format(canister_id, response))
        else:
            logger.info("Error in canister_transfer_skip invalid module")
            return error(1020, "module_id")

        if deactive_canister:
            action = constants.GUIDED_TRACKER_SKIPPED_AND_DEACTIVATE_ACTION
            for canister_id in canisters_to_skip:
                status = delete_canister_dao({"canister_id": canister_id,
                                              "company_id": company_id,
                                              "user_id": user_id,
                                              "comment": deactive_comments})
                logger.info(
                    "canister_transfer_skip deactivate canister for canister {}, {}".format(status, canister_id))
        else:
            action = constants.GUIDED_TRACKER_SKIPPED_ACTION

        # add data in canister transfer cycle history table
        status = add_data_in_guided_transfer_history_tables(existing_canisters_data=existing_canisters_data,
                                                            original_canister=canisters_to_skip,
                                                            skip_status=skip_status,
                                                            action=action,
                                                            comment=comments,
                                                            user_id=user_id)

        logger.info("update_canister canister_tx_status {}".format(status))

        return create_response(True)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in canister_transfer_skip {}".format(e))
        return error(2001, "{}".format(e))

    except (ValueError, Exception) as e:
        logger.error("Error in canister_transfer_skip {}".format(e))
        return error(1000, "Error in canister_transfer_skip")


@log_args_and_response
def get_guided_transfer_pending_canisters(args: dict) -> str:
    """
    Function to get canister list for which transfer is pending i.e transfer later selected
    for alternate canisters
    @param args:
    @return:
    """
    logger.info("Inside get_guided_transfer_pending_canisters")

    try:
        # first validate company id ,system id , batch id , device id then convert it to int otherwise it gives 500 error
        valid_device_with_company_id = validate_device_ids_with_company(device_ids=[args["device_id"]],
                                                                        company_id=args["company_id"])
        if not valid_device_with_company_id:
            return error(9059)

        valid_device_with_system_id = verify_device_id_list_dao(device_id=[args["device_id"]], system_id=args["system_id"])
        if not valid_device_with_system_id:
            return error(1015)

        validate_guided_tx_cycle_id = validate_guided_tx_cycle_id_dao(guided_tx_cycle_id=args['guided_meta_id'])
        if not validate_guided_tx_cycle_id:
            return error(14016)

        company_id = int(args['company_id'])
        system_id = int(args['system_id'])
        # user_id = int(args['user_id'])
        module_id = int(args['module_id'])
        device_id = int(args['device_id'])
        # sort_fields = args.get('sort_fields', None)
        guided_meta_id = int(args['guided_meta_id'])
        mini_batch_trolley = get_guided_trolley_from_mini_batch(guided_meta_id)
        quad_location_dict: dict = dict()
        final_canister_drawers_to_unlock: dict = dict()
        final_delicate_drawers_to_unlock: dict = dict()

        if module_id == constants.GUIDED_TO_TROLLEY_MODULE:

            transfer_data, final_canister_drawers_to_unlock,delicate_drawers_to_unlock, couch_db_canisters = \
                get_pending_canister_transfer_to_trolley_guided(company_id=company_id, device_id=device_id,
                                                                guided_meta_id=guided_meta_id,
                                                                trolley_id=mini_batch_trolley)

            # get misplaced canister data during guided flow when transfer to cart is done
            misplaced_canister_data, final_misplace_canister_drawers_to_unlock = \
                get_misplaced_canister_and_drawer_to_unlock_data(company_id=company_id, device_id=device_id,
                                                                 guided_meta_id=guided_meta_id)

            #  to get trolley id in which canister are to be transferred from given device
            trolley_id, pending_devices = get_trolley_and_pending_devices_for_guided_transfer_to_trolley(
                device_id=device_id,
                guided_tx_cycle_id=guided_meta_id,
                trolley_id=mini_batch_trolley)

            pending_devices_copy = deepcopy(pending_devices)
            # check if trolley id is null and pending device is not null then check for replenish queue
            if not trolley_id and pending_devices_copy:
                logger.info("Transfer from device {} is completed and pending from another device"
                             " so now checking whether replenish required in pending device or not".format(device_id))

                for i, pending_device in enumerate(pending_devices_copy):
                    if pending_device["pending_device_type_id"] != settings.DEVICE_TYPES["ROBOT"]:
                        # if pending device is other than robot then no need to check replenish queue
                        continue
                    pending_device_id = pending_device["pending_device_id"]
                    pending_device_system_id = pending_device["pending_device_system_id"]
                    if not pending_device_system_id:
                        return error(1000, "Invalid system_id for device {}".format(pending_device_id))

                    replenish_list = get_replenish_list_of_device(device_id=pending_device_id,
                                                                  system_id=pending_device_system_id)

                    if not replenish_list:
                        # No transfer in pending device so change the status of all pending canisters to return back to CSR.
                        all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids = \
                            fetch_guided_tracker_ids_based_on_destination_device(
                                dest_device_id=pending_device_id,
                                guided_tx_cycle_id=guided_meta_id,
                                transfer_status_list=constants.guided_tracker_to_trolley_status_list)
                        if source_guided_tracker_ids:
                            update_status = update_guided_tracker_status(guided_tracker_ids=source_guided_tracker_ids,
                                                                         status=constants.GUIDED_TRACKER_TRANSFER_AND_REPLENISH_SKIPPED)
                        if alt_guided_tracker_ids:
                            update_status = update_guided_tracker_status(guided_tracker_ids=alt_guided_tracker_ids,
                                                                         status=constants.GUIDED_TRACKER_TRANSFER_SKIPPED)
                        # remove pending device for which no more replenish required
                        pending_devices.pop(i)

                # done_device_couch_db_update = update_couch_db_of_to_trolley_done_devices(batch_id=batch_id,
                #                                                                          device_id=device_id,
                #                                                                          system_id=system_id)
                # logger.info("guided_cart_data_from_device_transfer done_device_couch_db_update {}".format(
                #     done_device_couch_db_update))

        elif module_id == constants.GUIDED_TO_DRUG_DISPENSER_MODULE:
            transfer_data, quad_canister_type_dict = get_pending_canister_transfer_from_trolley_guided(
                company_id=company_id,
                device_id=device_id,
                guided_meta_id=guided_meta_id,
                trolley_id=mini_batch_trolley)

            # get empty location for device and quadrant and location for small canister and location for big canister
            for dest_quadrant, canister_type_dict in quad_canister_type_dict.items():
                drawers_to_unlock,delicate_drawers_to_unlock ,locations_for_small_canisters, locations_for_big_canisters,locations_for_delicate_canisters = \
                    get_empty_drawer_data_with_locations(device_id=device_id, quadrant=dest_quadrant,
                                                         canister_type_dict=canister_type_dict)
                logger.info("In get_guided_transfer_pending_canisters:empty location for small canister: {},empty location for big canister: {}".format(locations_for_small_canisters, locations_for_big_canisters))

                # if destination_quad not in quad_location_dict then create dict for quadrant wise drawer to unlock, big_canister_location and small canister location
                if dest_quadrant not in quad_location_dict.keys():
                    quad_location_dict[dest_quadrant] = dict()
                quad_location_dict[dest_quadrant]["locations_for_big_canisters"] = locations_for_big_canisters
                quad_location_dict[dest_quadrant]["locations_for_small_canisters"] = locations_for_small_canisters
                quad_location_dict[dest_quadrant]["drawers_to_unlock"] = drawers_to_unlock

                # add to_device key in drawers_to_unlock
                for container_name, data in drawers_to_unlock.items():
                    if "empty_locations" in data:
                        drawers_to_unlock[container_name]["from_device"] = list()
                        drawers_to_unlock[container_name]["to_device"] = data.pop("empty_locations")
                    if data["to_device"]:
                        if container_name in final_canister_drawers_to_unlock.keys():
                            final_canister_drawers_to_unlock[container_name]["to_device"].extend(data["to_device"])
                        else:
                            final_canister_drawers_to_unlock[container_name] = data
                    else:
                        drawers_to_unlock[container_name]["from_device"] = list()
                        drawers_to_unlock[container_name]["to_device"] = list()

                for container_name, data in delicate_drawers_to_unlock.items():
                    if "empty_locations" in data:
                        delicate_drawers_to_unlock[container_name]["from_device"] = list()
                        delicate_drawers_to_unlock[container_name]["to_device"] = data.pop("empty_locations")
                    if data["to_device"]:
                        if container_name in final_delicate_drawers_to_unlock.keys():
                            final_delicate_drawers_to_unlock[container_name]["to_device"].extend(data["to_device"])
                        else:
                            final_delicate_drawers_to_unlock[container_name] = data
                    else:
                        delicate_drawers_to_unlock[container_name]["from_device"] = list()
                        delicate_drawers_to_unlock[container_name]["to_device"] = list()

                logger.info("In get_guided_transfer_pending_canisters: misplaced canister drawer unlock data: {}".format(drawers_to_unlock))

            # add destination location key in transfer_data
            for data in transfer_data:
                destination_quadrant = data["dest_quadrant"]
                if data["canister_type"] == settings.SIZE_OR_TYPE["SMALL"] and quad_location_dict[destination_quadrant]["locations_for_small_canisters"]:
                    unlock_display_location = quad_location_dict[destination_quadrant]["locations_for_small_canisters"].pop(0)
                elif data["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and quad_location_dict[destination_quadrant]["locations_for_big_canisters"]:
                    unlock_display_location = quad_location_dict[destination_quadrant]["locations_for_big_canisters"].pop(0)
                else:
                    unlock_display_location = None
                logger.info("In get_guided_transfer_pending_canisters: destination quadrant: {} for canister: {} and destination empty location: {}".format(
                        destination_quadrant, data["canister_id"], unlock_display_location))

                # if any empty location available for destination quadrant and destination device then pass key to unlock drawer data else NOne
                if unlock_display_location is not None:
                    drawer_data = get_container_data_from_display_location(unlock_display_location=unlock_display_location)
                    drawer_name = drawer_data["drawer_name"]
                    data["unlock_container_id"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["id"]
                    data["unlock_drawer_name"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["drawer_name"]
                    data["unlock_serial_number"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["serial_number"]
                    data["unlock_ip_address"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["ip_address"]
                    data["unlock_device_ip_address"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["device_ip_address"]
                    data["unlock_secondary_ip_address"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["secondary_ip_address"]
                    data["unlock_shelf"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["shelf"]
                    data["unlock_display_location"] = unlock_display_location
                    data["unlock_device_type_id"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["device_type_id"]
                else:
                    data["unlock_container_id"] = None
                    data["unlock_drawer_name"] = None
                    data["unlock_serial_number"] = None
                    data["unlock_ip_address"] = None
                    data["unlock_device_ip_address"] = None
                    data["unlock_secondary_ip_address"] = None
                    data["unlock_shelf"] = None
                    data["unlock_display_location"] = None
                    data["unlock_device_type_id"] = None

            # get misplaced canister data during guided flow when transfer to robot is done
            misplaced_canister_data, final_misplace_canister_drawers_to_unlock = get_misplaced_canister_and_drawer_to_unlock_data(
                company_id=company_id,
                device_id=device_id,
                guided_meta_id=guided_meta_id)

            pending_devices = get_pending_transfer_from_trolley_to_robot(mini_batch=guided_meta_id,
                                                                         trolley_id=mini_batch_trolley,
                                                                         guided_canister_status=constants.guided_tracker_to_robot_status_list,
                                                                         system_id=system_id)

            logger.info(
                "guided_cart_data_to_device_transfer: checking whether tx to current device is completed or not")
            pending_devices_copy = deepcopy(pending_devices)

            # check for device type other than csr i.e., robot if trolley id is null and something in pending device
            if not mini_batch_trolley and pending_devices_copy:
                logger.info("Transfer from current device completed and pending from another device"
                             " so now checking whether replenish required in pending device or not")

                for i, pending_device_data in enumerate(pending_devices_copy):
                    pending_device_id = pending_device_data["pending_device_id"]
                    pending_device_system_id = pending_device_data["pending_device_system_id"]
                    replenish_list = get_replenish_list_of_device(device_id=pending_device_id,
                                                                  system_id=pending_device_system_id)

                    if not replenish_list:
                        # No transfer in pending device so change the status of all pending canisters to return back to CSR.
                        all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids = \
                            fetch_guided_tracker_ids_based_on_destination_device(dest_device_id=pending_device_id,
                                                                                 guided_tx_cycle_id=guided_meta_id,
                                                                                 transfer_status_list=constants.guided_tracker_to_robot_status_list)
                        if all_guided_tracker_ids:
                            update_status = update_guided_tracker_status(guided_tracker_ids=all_guided_tracker_ids,
                                                                         status=constants.GUIDED_TRACKER_TRANSFER_SKIPPED)

                        # remove pending device for which no more replenish required
                        pending_devices.pop(i)

        else:
            return error(1020, "Module")

        # update couch db with pending transfer flag
        couch_db_update_args = {
            "device_id": device_id,
            "system_id": system_id,
            "pending_transfer": True if (len(transfer_data) or len(misplaced_canister_data)) else False,
        }
        couch_db_update_status = update_pending_transfer_in_guided_tx_couch_db_doc(couch_db_update_args)
        logger.info("get_guided_transfer_pending_canisters couch_db_update_status {}".format(couch_db_update_status))

        response = {"transfer_data": transfer_data,
                    "regular_drawers_to_unlock": list(final_canister_drawers_to_unlock.values()),
                    "delicate_drawers_to_unlock": list(final_delicate_drawers_to_unlock.values()),
                    "misplaced_canister_data": misplaced_canister_data,
                    "misplace_canister_drawers_to_unlock": list(final_misplace_canister_drawers_to_unlock.values()),
                    "pending_devices": pending_devices}
        logger.info("Output get_guided_transfer_pending_canisters {}".format(response))

        return create_response(response)

    except (DataError, ValueError) as e:
        logger.error("Error in get_guided_transfer_pending_canisters {}".format(e))
        return error(0)
    except Exception as e:
        logger.error("error in get_guided_transfer_pending_canisters {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_guided_transfer_pending_canisters: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_guided_transfer_pending_canisters: " + str(e))


@log_args_and_response
def update_pending_transfer_in_guided_tx_couch_db_doc(args):
    """
    Function to update transfer data for guided transfer flow in couch db
    @param args: dict
    @return: status
    """
    logger.info("In update_pending_transfer_in_guided_tx_couch_db_doc")
    device_id = args["device_id"]
    system_id = args["system_id"]
    pending_transfer = args["pending_transfer"]

    logger.info("update_pending_transfer_in_guided_tx_couch_db_doc Input {}".format(args))

    try:
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = '{}_{}'.format(constants.GUIDED_TRANSFER_DOCUMENT_NAME, device_id)
        table = cdb.get(_id=id)

        logger.info("previous table in guided transfer {}".format(table))
        if table is not None:  # when no document available for given device_id
            # different drawer scanned so update it
            table['data']['pending_transfer'] = pending_transfer
            table['data']['timestamp'] = get_current_date_time()
            logger.info("updated table in guided transfer {}".format(table))
            cdb.save(table)
        return True

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return error(1000, "Document update conflict.")

    except RealTimeDBException as e:
        return error(1000, str(e))

    except Exception as e:
        logger.error(e)
        raise Exception('Couch db update failed while transferring canisters')


@log_args_and_response
@validate(required_fields=["device_id", "module_id", "user_id", "company_id", "system_id", "canister_list"])
def guided_transfer_later(args: dict) -> str:
    """
    Function to assign transfer later status to canister
    @param args:
    @return:
    """
    logger.info("Inside guided_transfer_later")

    try:
        # company_id = args['company_id']
        # system_id = args['system_id']
        # batch_id = args['batch_id']
        user_id = args['user_id']
        module_id = args['module_id']
        # device_id = args['device_id']
        canister_list = args['canister_list']
        # call_from_portal = args.get("call_from_portal", False)

        # first validate company id ,system id , batch id , device id then convert it to int otherwise it gives 500 error
        valid_device_with_company_id = validate_device_ids_with_company(device_ids=[args["device_id"]],
                                                                        company_id=args["company_id"])
        if not valid_device_with_company_id:
            return error(9059)

        valid_device_with_system_id = verify_device_id_list_dao(device_id=[args["device_id"]], system_id=args["system_id"])
        if not valid_device_with_system_id:
            return error(1015)

        # validate_batch_id = validate_batch_id_dao(batch_id=args["batch_id"])
        # if not validate_batch_id:
        #     return error(14008)

        if module_id == constants.GUIDED_TO_TROLLEY_MODULE:
            transfer_status = constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE_TRANSFER_LATER
            filter_status = constants.guided_tracker_to_trolley_status_list

        elif module_id == constants.GUIDED_TO_DRUG_DISPENSER_MODULE:
            transfer_status = constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE_TRANSFER_LATER
            filter_status = constants.guided_tracker_to_robot_status_list
        else:
            return error(1020, "Invalid module")

        existing_canisters_data, guided_tracker_ids = db_get_existing_guided_canister_transfer_data(
            canister_list=canister_list,
            filter_status=filter_status)

        logger.info("guided_transfer_later existing_canisters_data {}".format(existing_canisters_data))

        if not len(existing_canisters_data):
            logger.error("Error in guided_transfer_later empty existing canister data")
            return error(1020, "Invalid canister list")

        guided_tx_status = update_guided_tracker_status(guided_tracker_ids=guided_tracker_ids,
                                                        status=transfer_status)

        logger.info("guided_transfer_later canister_tx_status {}".format(guided_tx_status))

        # add data in canister transfer cycle history table
        status = add_data_in_guided_transfer_history_tables(existing_canisters_data=existing_canisters_data,
                                                            original_canister=canister_list,
                                                            skip_status=transfer_status,
                                                            action=constants.GUIDED_TRACKER_TRANSFER_ACTION,
                                                            comment=None,
                                                            user_id=user_id)

        logger.info("guided_transfer_later canister history status {}".format(status))

        return create_response(True)

    except (DataError, ValueError) as e:
        logger.error("Error in guided_transfer_later {}".format(e))
        return error(0)
    except Exception as e:
        logger.error("error in guided_transfer_later {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in guided_transfer_later: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in guided_transfer_later: " + str(e))
    
    


def get_csr_destination_location_for_guided_canisters(input_args: dict):
    """

    @param input_args:
    @return:
    """
    logger.info("In assign_csr_location_to_pending_trolley_canisters")
    try:
        response = recommend_csr_location(input_args)
        loaded_response = json.loads(response)
        location_id = loaded_response['data']['location_id']
        logger.info(loaded_response)
        location_info = get_location_info_from_location_id(location_id=location_id)
        logger.info("location info in assign_csr_location_to_pending_trolley_canisters {}".format(location_info))

        return location_info['id']

    except ValueError as e:
        logger.error(e)
        raise ValueError
    except Exception as e:
        logger.error(e)
        return None


@log_args_and_response
def get_misplaced_canister_and_drawer_to_unlock_data(company_id: int, device_id: int, guided_meta_id: int) -> tuple:
    """
    function to get guided misplaced canister data and misplaced canister empty destination location with drawer to
    unlock data
    @param company_id:
    @param device_id:
    @param guided_meta_id:
    @param batch_id:
    @return:
    """
    quad_location_dict: dict = dict()
    misplaced_canister_data: list = list()
    final_misplace_canister_drawers_to_unlock: dict = dict()
    try:
        # get misplaced canister data after transfer to cart is done
        misplaced_canister_data, quad_type_dict = get_guided_misplaced_canister_data(company_id=company_id,
                                                                                     device_id=device_id,
                                                                                     guided_meta_id=guided_meta_id)
        logger.info("In get_guided_misplaced_canister_and_drawer_to_unlock_data: quadrant with number of canister "
                    "for type: {}".format(quad_type_dict))

        # get empty location for device and quadrant
        for dest_quadrant, canister_type_dict in quad_type_dict.items():
            misplace_canister_drawers_to_unlock, locations_for_small_canisters, locations_for_big_canisters = \
                get_empty_drawer_data_with_locations(device_id=device_id, quadrant=dest_quadrant,
                                                     canister_type_dict=canister_type_dict)
            logger.info("In get_guided_misplaced_canister_and_drawer_to_unlock_data:empty location for "
                        "small canister: {},empty location for big canister: {}".
                        format(locations_for_small_canisters, locations_for_big_canisters))

            # if destination_quad not in quad_location_dict then create dict for quadrant
            if dest_quadrant not in quad_location_dict.keys():
                quad_location_dict[dest_quadrant] = dict()
            quad_location_dict[dest_quadrant]["locations_for_big_canisters"] = locations_for_big_canisters
            quad_location_dict[dest_quadrant]["locations_for_small_canisters"] = locations_for_small_canisters
            quad_location_dict[dest_quadrant]["drawers_to_unlock"] = misplace_canister_drawers_to_unlock

            # add to_device key in canister data
            for container_name, data in misplace_canister_drawers_to_unlock.items():
                if "empty_locations" in data:
                    misplace_canister_drawers_to_unlock[container_name]["from_device"] = list()
                    misplace_canister_drawers_to_unlock[container_name]["to_device"] = data.pop("empty_locations")
                if data["to_device"]:
                    if container_name in final_misplace_canister_drawers_to_unlock.keys():
                        final_misplace_canister_drawers_to_unlock[container_name]["to_device"].extend(data["to_device"])
                    else:
                        final_misplace_canister_drawers_to_unlock[container_name] = data
                else:
                    misplace_canister_drawers_to_unlock[container_name]["from_device"] = list()
                    misplace_canister_drawers_to_unlock[container_name]["to_device"] = list()

            logger.info("In get_guided_misplaced_canister_and_drawer_to_unlock_data: misplaced canister drawer "
                        "unlock data: {}".format(misplace_canister_drawers_to_unlock))

        # add destination location key in misplaced canister data
        for data in misplaced_canister_data:
            destination_quadrant = data["destination_quadrant"]
            if data["canister_type"] == settings.SIZE_OR_TYPE["SMALL"] and \
                    quad_location_dict[destination_quadrant]["locations_for_small_canisters"]:
                unlock_display_location = \
                    quad_location_dict[destination_quadrant]["locations_for_small_canisters"].pop(0)

            elif data["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and \
                    quad_location_dict[destination_quadrant]["locations_for_big_canisters"]:
                unlock_display_location = quad_location_dict[destination_quadrant]["locations_for_big_canisters"].pop(0)
            else:
                unlock_display_location = None
            logger.info("In get_guided_misplaced_canister_and_drawer_to_unlock_data: destination quadrant: {} for "
                        "canister: {} and destination empty location: {}".format(destination_quadrant,
                                                                                 data["canister_id"],
                                                                                 unlock_display_location))

            # if any empty location available for quadrant and device then pass key to unlock drawer else NOne
            if unlock_display_location is not None:
                drawer_data = get_container_data_from_display_location(unlock_display_location=unlock_display_location)
                drawer_name = drawer_data["drawer_name"]
                data["unlock_container_id"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["id"]
                data["unlock_drawer_name"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["drawer_name"]
                data["unlock_serial_number"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["serial_number"]
                data["unlock_ip_address"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["ip_address"]
                data["unlock_device_ip_address"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["device_ip_address"]
                data["unlock_secondary_ip_address"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["secondary_ip_address"]
                data["unlock_shelf"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["shelf"]
                data["unlock_display_location"] = unlock_display_location
                data["unlock_device_type_id"] = quad_location_dict[destination_quadrant]["drawers_to_unlock"][drawer_name]["device_type_id"]
            else:
                data["unlock_container_id"] = None
                data["unlock_drawer_name"] = None
                data["unlock_serial_number"] = None
                data["unlock_ip_address"] = None
                data["unlock_device_ip_address"] = None
                data["unlock_secondary_ip_address"] = None
                data["unlock_shelf"] = None
                data["unlock_display_location"] = None
                data["unlock_device_type_id"] = None

        return misplaced_canister_data, final_misplace_canister_drawers_to_unlock

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_misplaced_canister_and_drawer_to_unlock_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_destination_location_for_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_misplaced_canister_and_drawer_to_unlock_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_guided_transfer_wizard_couch_db(company_id: int, module_id: int,
                                           transfer_done_from_portal: bool,
                                           update_status: int,
                                           next_cycle_id: int = None,
                                           batch_id = None
                                           ) -> bool:
    """
    This function updates the couch db with the given status
    @param company_id: int
    @param batch_id: int
    @param module_id: int
    @param transfer_done_from_portal: bool
    """
    try:
        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        doc_id = constants.GUIDED_TRANSFER_WIZARD
        table = cdb.get(_id=doc_id)
        logger.info("guided-transfer-wizard: before couch db doc: {}, data: {} ".format(doc_id, table))
        if table is not None:
            if update_status != constants.GUIDED_META_TO_CSR_DONE:
                if table["data"]:
                    table["data"]["module_id"] = module_id
                    table["data"]["transfer_done_from_portal"] = transfer_done_from_portal
            else:
                if next_cycle_id:
                    if table["data"]:
                        table["data"]["transfer_done_from_portal"] = False
                        table["data"]["guided_tx_cycle_id"] = next_cycle_id
                        table["data"]["module_id"] = 0
                else:
                    table["data"] = {}
            logger.info("guided-transfer-wizard: after couch db doc: {}, data: {} ".format(doc_id, table))
            cdb.save(table)
        return True

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        raise RealTimeDBException("Couch db Document update conflict.")

    except Exception as e:
        print("Key error came in updating couch db: ", e)
        raise e