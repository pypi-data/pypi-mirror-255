"""
Service file for canister transfers
"""
import json

import math
import os
import sys
import threading
from collections import OrderedDict
from copy import deepcopy
from itertools import chain
import couchdb
from peewee import IntegrityError, InternalError, DataError, DoesNotExist
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, log_args, retry_exception
from dosepack.validation.validate import validate
from realtime_db.dp_realtimedb_interface import Database
from src.exceptions import RealTimeDBException
from src import constants

from src.dao.batch_dao import get_system_id_from_batch_id, get_progress_batch_id, db_is_imported
from src.dao.canister_dao import check_canisters_present_in_cart, update_canister_location, delete_canister_dao, \
    get_available_trolley_data, get_canister_history_latest_record_can_id_dao, update_canister_history_by_id_dao, \
    assign_cart_location_to_canister, update_canister_dao, update_replenish_based_on_device, \
    delete_reserved_canister_for_skipped_canister, insert_records_in_reserved_canister

from src.dao.canister_transfers_dao import get_trolley_to_transfer_canisters_to_trolley, \
    get_pending_devices_to_trolleys, get_trolley_drawers_data_for_to_trolley_tx, \
    get_canisters_to_be_transferred_to_trolley, transfer_cycle_status_for_update, check_couch_db_status, \
    get_trolley_drawers_from_trolley_tx, get_canister_transfers_for_robot_destination, \
    get_canisters_transfers_from_trolley_to_csr, get_trolley_to_transfer_canisters_from_trolley, \
    get_trolley_to_transfer_canisters_from_trolley_to_csr, get_pending_trolleys_for_from_trolley_flow_csr, \
    get_pending_trolleys_for_from_trolley_flow, get_empty_locations_for_canister, \
    get_pending_canister_transfer_batch_id, \
    get_pending_canister_transfers_for_batch, update_cycle_done_for_pending_cycles, \
    update_canister_loc_in_canister_transfers, get_to_trolley_pending_canister_transfers_for_batch, \
    db_update_canister_transfers, add_record_in_canister_tx_meta, \
    check_transfer_recommendation_status, get_trolley_drawers_from_trolley_tx_csr, \
    check_transfers_for_trolley, get_meta_id_from_batch_and_cycle, get_canister_tx_transfer_device_ids_by_status, \
    check_transfers_for_device, add_alt_canister_in_canister_transfers, \
    add_data_in_canister_transfer_history_tables, check_to_robot_required_for_meta_id, \
    check_to_csr_required_for_meta_id, get_pending_canister_transfers_by_device, \
    get_csr_canister_tx_meta_id_for_batch, db_update_canister_tx_meta, \
    get_pending_canisters_to_be_transferred_to_trolley, db_get_quad_drawer_type_wise_empty_unreserved_locations, \
    get_location_data_from_device_ids, insert_canister_transfer_cycle_history_data_dao, add_canister_history_data_dao, \
    get_canister_transfer_data, db_get_pending_transfers, \
    db_get_latest_canister_transfer_data_for_a_canister_from_robot_csr, \
    db_get_latest_canister_transfer_data_to_robot_from_trolley, \
    db_get_latest_canister_transfer_data_to_csr_from_trolley, db_get_remove_canister_list, \
    db_update_canister_tx_status_dao, update_canister_transfers, get_total_canister_transfer_data_dao, \
    update_canister_tx_meta_by_batch_id, check_to_csr_required_for_csr_meta_id, check_pending_canister_transfers, \
    db_get_quad_drawer_type_wise_non_delicate_reserved_locations, sorted_csr_canister_list_by_big_canisters, \
    get_delicate_drawers, get_csr_tx_status, db_update_canister_tx_meta_status_dao, get_csr_canister_tx_meta_id

from src.dao.device_manager_dao import get_device_data_by_device_id_dao, \
    get_zone_wise_system_list, get_zone_wise_device_list, get_drawer_data_based_on_serial_number, \
    get_available_canisters_in_device, get_location_info_from_location_id
from src.dao.guided_replenish_dao import update_guided_tracker_status, check_pending_guided_canister_transfer, \
    fetch_guided_tracker_ids_based_on_meta_id, fetch_guided_tracker_ids_by_canister_ids
from src.dao.mfd_canister_dao import get_device_id_from_serial_number, \
    get_device_id_from_drawer_serial_number
from src.dao.couch_db_dao import get_couch_db_database_name, reset_couch_db_document

from src.service.misc import update_canister_transfer_wizard_data_in_couch_db, update_cycle_module_in_canister_tx_wizard_couch_db
from src.dao.pack_analysis_dao import update_pack_analysis_canisters_data
from src.service.csr import recommend_csr_location
from src.service.guided_replenish import update_guided_cycle_status, \
    update_guided_cycle_for_batch_done
from utils.drug_inventory_webservices import get_current_inventory_data

logger = settings.logger
update_can_tras_lock = threading.Lock()


@log_args_and_response
def update_transfer_status(args: dict) -> dict:
    """
    This function updates the status in CanisterTransferMeta table for the provided transfer_cycle_id
    @param args:dict
    @return dict
    """
    try:
        logger.debug("In update_transfer_status")
        company_id = args.get("company_id", None)
        transfer_cycle_id = args.get("transfer_cycle_id", None)
        batch_id = args.get("batch_id", None)
        status = args.get("status", None)
        device_id = args.get("device_id", None)
        system_id = args.get("system_id", None)
        call_from_portal = args.get("call_from_portal", False)
        from_app = args.get("from_app", False)
        device_system_dict = dict()
        status_to_update = deepcopy(status)
        device_count = 0
        couch_db_flow = None
        # update the status for the given transfer_cycle_id
        if transfer_cycle_id and status and batch_id:
            # get transfer meta id from batch, device and cycle uniquely
            transfer_meta_id = get_meta_id_from_batch_and_cycle(batch_id=batch_id,
                                                                cycle_id=transfer_cycle_id,
                                                                device_id=device_id)
            # check if all the transfers to trolley are completed for the given device
            if status == constants.CANISTER_TRANSFER_TO_TROLLEY_DONE:
                if not check_transfers_for_trolley(batch_id=batch_id,
                                                   device_id=device_id,
                                                   to_meta_id=transfer_meta_id):
                    return error(1000, "Kindly place all the canisters in the trolley")

                # check if there transfer to trolley is already done for any other device,
                # if yes than update couch db timestamp
                device_system_dict, device_count = get_canister_tx_transfer_device_ids_by_status(batch_id=batch_id,
                                                                                   transfer_cycle_id=transfer_cycle_id,
                                                                                   status=[
                                                                                       constants.CANISTER_TRANSFER_TO_TROLLEY_DONE,
                                                                                   constants.CANISTER_TRANSFER_TO_ROBOT_DONE],
                                                                                   device_id=device_id)
                logger.info("update_transfer_status device_system_dict {}".format(device_system_dict))
                couch_db_flow = constants.KEY_TRANSFER_TO_TROLLEY

                # check to robot require for this meta id
                if not check_to_robot_required_for_meta_id(batch_id=batch_id,
                                                           from_meta_id=transfer_meta_id):
                    status_to_update = constants.CANISTER_TRANSFER_TO_ROBOT_DONE

                    # check if to CSR is required for this meta id
                    if call_from_portal:
                        if not check_to_csr_required_for_csr_meta_id(batch_id=batch_id,
                                                                     from_meta_id=transfer_meta_id):
                            status_to_update = constants.CANISTER_TRANSFER_TO_CSR_DONE

                    else:
                        if not check_to_csr_required_for_meta_id(batch_id=batch_id,
                                                                 from_meta_id=transfer_meta_id):
                            status_to_update = constants.CANISTER_TRANSFER_TO_CSR_DONE

            # check if all the transfers to robot are completed for the given device
            elif status == constants.CANISTER_TRANSFER_TO_ROBOT_DONE:
                if not check_transfers_for_device(batch_id=batch_id,
                                                  device_id=device_id,
                                                  from_meta_id=transfer_meta_id):
                    return error(1000, "Kindly place all the canisters in the device")

                # check if there transfer to robot is already done for any other device,
                # if yes than update couch db timestamp
                device_system_dict, device_count = get_canister_tx_transfer_device_ids_by_status(batch_id=batch_id,
                                                                                   transfer_cycle_id=transfer_cycle_id,
                                                                                   status=[constants.CANISTER_TRANSFER_TO_ROBOT_DONE,
                                                                                           constants.CANISTER_TRANSFER_TO_CSR_DONE],
                                                                                   device_id=device_id)
                logger.info("update_transfer_status device_system_dict {}".format(device_system_dict))
                couch_db_flow = constants.KEY_TRANSFER_FROM_TROLLEY

                if not check_to_csr_required_for_meta_id(batch_id=batch_id,
                                                         from_meta_id=transfer_meta_id):
                    status_to_update = constants.CANISTER_TRANSFER_TO_CSR_DONE

            # check if transfer to CSR is completed for given device
            elif status == constants.CANISTER_TRANSFER_TO_CSR_DONE:
                if not check_transfers_for_device(batch_id=batch_id,
                                                  device_id=device_id,
                                                  from_meta_id=transfer_meta_id):
                    return error(1000, "Kindly place all the canisters in the device")

                # check if there transfer to robot is already done for any other device,
                # if yes than update couch db timestamp
                device_system_dict, device_count = get_canister_tx_transfer_device_ids_by_status(batch_id=batch_id,
                                                                                   transfer_cycle_id=transfer_cycle_id,
                                                                                   status=[constants.CANISTER_TRANSFER_TO_CSR_DONE],
                                                                                   device_id=device_id)
                logger.info("update_transfer_status device_system_dict {}".format(device_system_dict))
                couch_db_flow = constants.KEY_TRANSFER_FROM_TROLLEY

            transfer_status_update, message = transfer_cycle_status_for_update(update_status=status_to_update,
                                                                               device_id=device_id,
                                                                               batch_id=batch_id,
                                                                               cycle_id=transfer_cycle_id)

            logger.info("transfer_status_update and message {}, {}".format(transfer_status_update, message))

            # update couch db timestamp if not updated previously
            if message == "success" and len(device_system_dict) and device_count > len(device_system_dict) + 1:
                for device, system in device_system_dict.items():
                    couch_db_update_status = canister_transfer_couch_db_update(device_id=int(device),
                                                                               flow=couch_db_flow,
                                                                               system_id=system,
                                                                               drawer_id=None,
                                                                               pending_transfer=None,
                                                                               drawer_serial_number=None)
                    logger.info("Couch db updated for device and system {}, {}, {}".format(couch_db_update_status,
                                                                                           device,
                                                                                           system))
            # update couch db after updating status in db
            if transfer_status_update:
                couch_db_update_status, cycle_id_to_update = check_couch_db_status(status=status,
                                                                                   cycle_id=transfer_cycle_id,
                                                                                   batch_id=batch_id)
                if status == constants.CANISTER_TRANSFER_TO_TROLLEY_DONE and couch_db_update_status:
                    couch_db_update = update_couch_db_trolley(company_id=company_id,
                                                              status=status,
                                                              transfer_cycle_id=cycle_id_to_update)

                if status == constants.CANISTER_TRANSFER_TO_ROBOT_DONE and couch_db_update_status:
                    couch_db_update = update_couch_db_trolley(company_id=company_id,
                                                              status=status,
                                                              transfer_cycle_id=cycle_id_to_update)

                if status in [constants.CANISTER_TRANSFER_TO_CSR_DONE]:
                    # resetting the couch db for device
                    reset_couch_db_dict_for_reset = {"system_id": system_id,
                                                     "document_name": str(
                                                         constants.CANISTER_TRANSFER_DEVICE_DOCUMENT_NAME) + '_{}'.format(
                                                         device_id),
                                                     "couchdb_level": constants.STRING_SYSTEM,
                                                     "key_name": "data"}
                    reset_couch_db_document(reset_couch_db_dict_for_reset)

                    # updating the couchdb for wizard level changes
                    if cycle_id_to_update != transfer_cycle_id:
                        if cycle_id_to_update:
                            couch_db_update = update_couch_db_trolley(company_id=company_id,
                                                                      status=status,
                                                                      transfer_cycle_id=cycle_id_to_update)
                        else:
                            batch_system_id = get_system_id_from_batch_id(batch_id)
                            batch_update = check_transfer_pending_for_coming_batch(company_id=company_id,
                                                                                   system_id=batch_system_id)
                            logger.info("update_transfer_status batch_update {}".format(batch_update))
                            if not batch_update:
                                couch_db_reset = update_couch_db_trolley(company_id=company_id,
                                                                         status=status,
                                                                         transfer_cycle_id=None)
                                logger.info("update_transfer_status couch_db_reset {}".format(couch_db_reset))
                return create_response(settings.SUCCESS_RESPONSE)

            else:
                return error(1000, str(message))

        else:
            return error(1000, "Invalid args value for transfer_cycle_id or batch_id or status")

    except Exception as e:
        logger.error(e)
        return error(1000, "Error in updating cycle status")


@log_args
def check_transfer_pending_for_coming_batch(company_id: int, system_id: int) -> bool:
    """
    Function to check if canister transfer is pending for coming batch than update batch in couch db
    @return:
    """
    try:
        logger.debug("In check_transfer_pending_for_coming_batch")
        batch_id = get_pending_canister_transfer_batch_id(system_id)
        if batch_id:
            logger.info("check_transfer_pending_for_coming_batch batch_id {}".format(batch_id))
            update_couch_db_status, couch_db_response = update_canister_transfer_wizard_data_in_couch_db(
                {"company_id": company_id, "batch_id": batch_id,
                 "timestamp": get_current_date_time()})
            logger.info("check_transfer_pending_for_coming_batch couch db update {}, {}".format(update_couch_db_status, couch_db_response))
            return True

        return False

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@validate(required_fields=["company_id", "system_id", "batch_id", "device_id", "transfer_cycle_id"])
def get_cart_data_from_device_transfer(args: dict):
    """
    Function to get cart data for transfer to trolley from device(robot)
    @param args: dict
    @return: json
    """
    logger.info("Input get_cart_data_from_device_transfer: " + str(args))
    company_id = int(args["company_id"])
    system_id = int(args["system_id"])
    batch_id = int(args["batch_id"])
    device_id = int(args["device_id"])
    transfer_cycle_id = int(args["transfer_cycle_id"])
    from_app = args.get("from_app", False)

    try:
        # check pending transfer key in couch db
        couch_db_data = get_canister_transfer_data_from_couch_db_(device_id=int(device_id),
                                                                  system_id=system_id)

        logger.info("get_canister_transfer_data_from_couch_db_ couch db status: " + str(couch_db_data))

        if couch_db_data and 'pending_transfer' in couch_db_data and couch_db_data['pending_transfer'] == True:
            trolley_list = list()

        else:
            # To return trolley list
            logger.debug("fetching trolley list for device: " + str(device_id))
            trolley_list = get_trolley_to_transfer_canisters_to_trolley(batch_id=batch_id,
                                                                        transfer_cycle_id=transfer_cycle_id,
                                                                        source_device_id=device_id,
                                                                        from_app=from_app)

            logger.debug("trolley list fetched now fetching pending devices list")
        pending_devices = get_pending_devices_to_trolleys(batch_id=batch_id,
                                                          transfer_cycle_id=transfer_cycle_id,
                                                          current_device=device_id)
        logger.debug("fetched pending devices data, now updating trolley data in couch db doc")

        response = {"trolley_list": trolley_list, "pending_devices": pending_devices}
        logger.info("response get_cart_data_from_device_transfer {}".format(response))

        return create_response(response)

    except RealTimeDBException as e:
        return error(2005, " - " + str(e))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting cart data to device transfer")


@validate(
    required_fields=["company_id", "system_id", "batch_id", "device_id", "transfer_cycle_id", "trolley_serial_number"])
def get_drawer_data_from_device_transfer(args: dict):
    """
    Function to get drawer data for transfer to trolley from device (robot)
    @param args: dict
    @return: json
    """
    logger.info("Input get_drawer_data_from_device_transfer: " + str(args))
    company_id = int(args["company_id"])
    system_id = int(args["system_id"])
    batch_id = int(args["batch_id"])
    device_id = int(args["device_id"])
    transfer_cycle_id = int(args["transfer_cycle_id"])
    trolley_serial_number = args["trolley_serial_number"]

    try:
        # when trolley scanned, return drawer data
        logger.info("get_drawer_data_from_device_transfer for trolley serial_number- " + str(trolley_serial_number))
        trolley_id = get_device_id_from_serial_number(serial_number=trolley_serial_number,
                                                      company_id=company_id)
        if not trolley_id:
            return error(1020, "Trolley_serial_number or company_id")
        logger.info("get_drawer_data_from_device_transfer trolley - " + str(trolley_id))
        drawer_list = get_trolley_drawers_data_for_to_trolley_tx(batch_id=batch_id,
                                                                 transfer_cycle_id=transfer_cycle_id,
                                                                 source_device_id=device_id,
                                                                 dest_trolley_id=trolley_id)
        logger.info("Response get_drawer_data_from_device_transfer {}".format(drawer_list))

        if len(drawer_list):
            drawer_serial_number = drawer_list[0]['serial_number']
        else:
            drawer_serial_number = 0
        # update couch db with scanned drawer
        couch_db_update_status = canister_transfer_couch_db_update(device_id=int(device_id),
                                                                   flow=constants.KEY_TRANSFER_FROM_TROLLEY,
                                                                   system_id=system_id,
                                                                   pending_transfer=None,
                                                                   drawer_id=None,
                                                                   drawer_serial_number=drawer_serial_number
                                                                   )
        logger.info("get_canister_data_to_device_transfer couch db status: " + str(couch_db_update_status))


        return create_response(drawer_list)

    except RealTimeDBException as e:
        return error(2005, " - " + str(e))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting drawer data to device transfer")


@validate(
    required_fields=["company_id", "system_id", "batch_id", "device_id", "transfer_cycle_id", "trolley_serial_number",
                     "drawer_serial_number"])
def get_canister_data_from_device_transfer(args: dict):
    """
    Method to fetch canister data to transfer from robot,csr to trolley
    @param args:
    @return:
    """
    logger.info("Input get_canister_data_from_device_transfer: " + str(args))
    company_id = int(args["company_id"])
    system_id = int(args["system_id"])
    batch_id = int(args["batch_id"])
    device_id = int(args["device_id"])
    transfer_cycle_id = int(args["transfer_cycle_id"])
    trolley_serial_number = args.get("trolley_serial_number", None)
    drawer_serial_number = args["drawer_serial_number"]
    sort_fields = args.get('sort_fields', None)
    from_app = args.get("from_app", False)

    try:
        # when drawer scanned
        logger.info("Input get_canister_data_from_device_transfer {}".format(args))
        # todo replace multiple functions with single function
        if from_app:
            trolley_id = get_device_id_from_drawer_serial_number(drawer_serial_number=drawer_serial_number,
                                                                 company_id=company_id)
        else:
            trolley_id = get_device_id_from_serial_number(serial_number=trolley_serial_number, company_id=company_id)
            logger.info("get_canister_data_from_device_transfer trolley_id {}".format(trolley_id))

        try:
            logger.debug("fetching drawer data based on drawer_serial_number")
            drawer_data = get_drawer_data_based_on_serial_number(drawer_serial_number=drawer_serial_number,
                                                                 company_id=company_id)
            trolley_drawer_id = drawer_data["id"]
            trolley_drawer_name = drawer_data["drawer_name"]
            logger.debug("fetched drawer data: "+str(drawer_data))

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return error(3007, " or company_id")

        logger.debug("get_canister_data_from_device_transfer drawer_id {}".format(trolley_drawer_id))

        if not trolley_id or not trolley_drawer_id:
            return error(1020, "trolley_serial_number or drawer_serial_number or company_id")

        transfer_data, source_drawer_list, delicate_drawers, ndc_list = get_canisters_to_be_transferred_to_trolley(
            batch_id=batch_id, source_device_id=device_id, dest_trolley_drawer_id=trolley_drawer_id,
            sort_fields=sort_fields, transfer_cycle_id=transfer_cycle_id)
        inventory_quantity = get_current_inventory_data(ndc_list=ndc_list, qty_greater_than_zero=False)
        inventory_qty_ndc_dict = dict()
        for item in inventory_quantity:
            inventory_qty_ndc_dict[item['ndc']] = item['quantity']

        for record in transfer_data:
            record['inventory_qty'] = inventory_qty_ndc_dict.get(record['ndc'], 0)
            record['is_in_stock'] = 0 if record['inventory_qty'] <= 0 else 1

        couch_db_update_status = canister_transfer_couch_db_update(device_id=int(device_id),
                                                                   flow=constants.KEY_TRANSFER_TO_TROLLEY,
                                                                   system_id=system_id,
                                                                   drawer_id=trolley_drawer_id,
                                                                   pending_transfer=None,
                                                                   drawer_serial_number=drawer_serial_number
                                                                   )
        logger.debug("couch db updated with status: " + str(couch_db_update_status))

        response = {"trolley_drawer_name": trolley_drawer_name,
                    "transfer_data": transfer_data,
                    "regular_drawers_to_unlock": list(source_drawer_list.values()),
                    "delicate_drawers_to_unlock": list(delicate_drawers.values())}
        logger.info("Output get_canister_data_from_device_transfer {}".format(response))

        return create_response(response)

    except RealTimeDBException as e:
        return error(2005, " - " + str(e))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting canister data to device transfer")


@validate(
    required_fields=["company_id", "system_id", "batch_id", "device_id", "transfer_cycle_id", "drawer_serial_number"])
def get_canister_data_to_device_transfer(args: dict):
    """
    Function to fetch canister list for transfer from trolley to robot and csr
    @param args:
    @return:
    """
    logger.info("Input for get_canister_data_to_device_transfer: " + str(args))
    company_id = int(args["company_id"])
    system_id = int(args["system_id"])
    batch_id = int(args["batch_id"])
    device_id = int(args["device_id"])
    transfer_cycle_id = int(args["transfer_cycle_id"])
    trolley_serial_number = args.get("trolley_serial_number")
    drawer_serial_number = args["drawer_serial_number"]
    sort_fields = args.get('sort_fields', None)
    from_app = args.get("from_app", False)

    try:
        # when drawer scanned
        if from_app:
            trolley_id = get_device_id_from_drawer_serial_number(drawer_serial_number=drawer_serial_number,
                                                                 company_id=company_id)
        else:
            trolley_id = get_device_id_from_serial_number(serial_number=trolley_serial_number,
                                                          company_id=company_id)

        try:
            logger.debug("fetching drawer data based on drawer_serial_number")
            drawer_data = get_drawer_data_based_on_serial_number(drawer_serial_number=drawer_serial_number,
                                                                 company_id=company_id)
            trolley_drawer_id = drawer_data["id"]
            trolley_drawer_name = drawer_data["drawer_name"]
            logger.debug("fetched drawer data: "+str(drawer_data))

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return error(3007, " or company_id")

        if not trolley_id or not trolley_drawer_id:
            return error(1020, "trolley_serial_number or drawer_serial_number or company_id")

        logger.info(
            "get_canister_data_to_device_transfer trolley and drawer {}, {}".format(trolley_id, trolley_drawer_id))

        # fetch device_type based on id to differentiate between robot and csr to suggest destination drawers
        device_data = get_device_data_by_device_id_dao(device_id=device_id)
        if not device_data:
            return error(1020, "device_id")
        device_type_id = device_data.device_type_id_id
        logger.info("device_type_id: " + str(device_type_id))
        delicate_drawers_to_unlock = {}
        delicate_transfer_data = []
        delicate_locations = False
        if device_type_id == settings.DEVICE_TYPES["ROBOT"]:
            delicate_transfer_data, transfer_data, source_drawer_list, dest_quadrant, canister_type_dict, delicate_locations, ndc_list = \
                get_canister_transfers_for_robot_destination(batch_id=batch_id, dest_device_id=device_id,
                                                             source_trolley_drawer_id=trolley_drawer_id,
                                                             transfer_cycle_id=transfer_cycle_id,
                                                             sort_fields=sort_fields)

            # drawer_list_to_unlock = get_empty_locations_for_canister(device_id,
            #                                                          dest_quadrant,
            #                                                          canister_type_dict)
            drawer_list_to_unlock, delicate_drawers_to_unlock = get_delicate_drawers(device_id, dest_quadrant,
                                                                                     canister_type_dict)

            # update couch db with scanned drawer
            couch_db_update_status = canister_transfer_couch_db_update(device_id=int(device_id),
                                                                       flow=constants.KEY_TRANSFER_FROM_TROLLEY,
                                                                       system_id=system_id,
                                                                       drawer_id=trolley_drawer_id,
                                                                       pending_transfer=None,
                                                                       drawer_serial_number=drawer_serial_number
                                                                       )
            logger.info("get_canister_data_to_device_transfer couch db status: " + str(couch_db_update_status))

        elif device_type_id == settings.DEVICE_TYPES["CSR"]:
            transfer_data, canister_id_list, ndc_list = \
                get_canisters_transfers_from_trolley_to_csr(batch_id=batch_id, dest_device_id=device_id,
                                                            source_trolley_drawer_id=trolley_drawer_id,
                                                            transfer_cycle_id=transfer_cycle_id,
                                                            sort_fields=sort_fields)

            drawer_list_to_unlock, delicate_drawers_to_unlock, transfer_data = recommend_csr_drawers_to_unlock(batch_id=batch_id,
                                                                    company_id=company_id,
                                                                    canister_id_list=canister_id_list,
                                                                    device_id=device_id,
                                                                    transfer_data=transfer_data)

            # update couch db with scanned drawer
            couch_db_update_status = canister_transfer_couch_db_update(device_id=int(device_id),
                                                                       flow=constants.KEY_TRANSFER_FROM_TROLLEY,
                                                                       system_id=system_id,
                                                                       drawer_id=trolley_drawer_id,
                                                                       pending_transfer=None,
                                                                       drawer_serial_number=drawer_serial_number
                                                                       )
            logger.info("get_canister_data_to_device_transfer couch db status: " + str(couch_db_update_status))

        else:
            return error(1020, " device_id")
        inventory_quantity = get_current_inventory_data(ndc_list=ndc_list, qty_greater_than_zero=False)
        inventory_qty_ndc_dict = dict()
        for item in inventory_quantity:
            inventory_qty_ndc_dict[item['ndc']] = item['quantity']

        for record in transfer_data:
            record['inventory_qty'] = inventory_qty_ndc_dict.get(record['ndc'], 0)
            record['is_in_stock'] = 0 if record['inventory_qty'] <= 0 else 1
        for record in delicate_transfer_data:
            record['inventory_qty'] = inventory_qty_ndc_dict.get(record['ndc'], 0)
            record['is_in_stock'] = 0 if record['inventory_qty'] <= 0 else 1

        response = {"delicate_transfer_data": delicate_transfer_data,
                    "transfer_data": transfer_data,
                    "regular_drawers_to_unlock": list(drawer_list_to_unlock.values()),
                    "delicate_drawers_to_unlock": list(delicate_drawers_to_unlock.values()),
                    "delicate_locations":delicate_locations}

        logger.info("Output get_canister_data_to_device_transfer {}".format(response))

        return create_response(response)

    except RealTimeDBException as e:
        return error(2005, " - " + str(e))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("error in get_canister_data_from_device_transfer {}".format(e))
        return error(1000, "Error in getting canister data from device transfer")


@log_args_and_response
def recommend_csr_drawers_to_unlock(company_id: int, batch_id: int, device_id: int, canister_id_list: list,
                                    transfer_data) -> tuple:
    """
    Function to get empty locations of CSR to place canisters
    @param company_id:
    @param batch_id:
    @param device_id:
    @param canister_id_list:
    @return:
    """
    try:
        drawer_to_unlock = dict()
        delicate_drawer_to_unlock = dict()
        reserve_location_list = list()
        input_args = {'device_id': device_id,
                      'company_id': company_id}

        for index, canister_id in enumerate(canister_id_list):
            input_args['canister_id'] = canister_id
            input_args['reserved_location_list'] = reserve_location_list
            response = recommend_csr_location(input_args)
            loaded_response = json.loads(response)
            logger.info("recommend_csr_drawers_to_unlock loaded response {}".format(loaded_response))
            location_id = loaded_response['data']['location_id']
            reserve_location_list.append(location_id)
            if transfer_data[index]['is_delicate']:
                if loaded_response['data']["drawer_name"] not in delicate_drawer_to_unlock.keys():
                    delicate_drawer_to_unlock[loaded_response['data']["drawer_name"]] = {
                        "drawer_name": loaded_response['data']["drawer_name"],
                        "secondary_mac_address": None,
                        "mac_address": None,
                        "device_ip_address": None,
                        "serial_number": loaded_response['data']["serial_number"],
                        "ip_address": loaded_response['data']["ip_address"],
                        "secondary_ip_address": loaded_response['data']["secondary_ip_address"],
                        "from_device": list(),
                        "to_device": list(),
                        "shelf": loaded_response['data']["shelf"],
                        "device_type_id": settings.DEVICE_TYPES['CSR']
                        }
            else:
                if loaded_response['data']["drawer_name"] not in drawer_to_unlock.keys():
                    drawer_to_unlock[loaded_response['data']["drawer_name"]] = {
                        "drawer_name": loaded_response['data']["drawer_name"],
                        "secondary_mac_address": None,
                        "mac_address": None,
                        "device_ip_address": None,
                        "serial_number": loaded_response['data']["serial_number"],
                        "ip_address": loaded_response['data']["ip_address"],
                        "secondary_ip_address": loaded_response['data']["secondary_ip_address"],
                        "from_device": list(),
                        "to_device": list(),
                        "shelf": loaded_response['data']["shelf"],
                        "device_type_id": settings.DEVICE_TYPES['CSR']
                    }

            if loaded_response['data']["drawer_name"]:
                transfer_data[index]['dest_drawer_number'] = str(loaded_response['data']["drawer_name"]).replace('-','')
            if transfer_data[index]['is_delicate']:
                delicate_drawer_to_unlock[loaded_response['data']["drawer_name"]]["to_device"].append(
                    loaded_response['data']["display_location"])
            else:
                drawer_to_unlock[loaded_response['data']["drawer_name"]]["to_device"].append(
                    loaded_response['data']["display_location"])

        return drawer_to_unlock,delicate_drawer_to_unlock, transfer_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in recommend_csr_drawers_to_unlock {}".format(e))
        raise error(2001)

    except Exception as e:
        logger.error("Error in recommend_csr_drawers_to_unlock {}".format(e))
        raise error(1000, "Error in recommend_csr_drawers_to_unlock")


@validate(
    required_fields=["company_id", "system_id", "batch_id", "device_id", "transfer_cycle_id", "trolley_serial_number"])
def get_drawer_data_to_device_transfer(args: dict):
    """
    Function to fetch drawer data for transfer from trolley to robot and csr
    @param args: dict
    @return: json
    """
    logger.debug("args for transfer_from_trolley: " + str(args))
    company_id = int(args["company_id"])
    system_id = int(args["system_id"])
    batch_id = int(args["batch_id"])
    device_id = int(args["device_id"])
    transfer_cycle_id = int(args["transfer_cycle_id"])
    trolley_serial_number = args["trolley_serial_number"]

    try:
        # when trolley scanned, return drawer data
        logger.info("Input get_drawer_data_to_device_transfer {}".format(args))
        trolley_id = get_device_id_from_serial_number(serial_number=trolley_serial_number,
                                                      company_id=company_id)
        if not trolley_id:
            return error(1020, "Trolley_serial_number or company_id")

        logger.info("trolley get_drawer_data_to_device_transfer  " + str(trolley_id))

        # fetch device_type based on id to differentiate between robot and csr to suggest destination drawers
        device_data = get_device_data_by_device_id_dao(device_id=device_id)
        if not device_data:
            return error(1020, "device_id")
        device_type_id = device_data.device_type_id_id
        logger.info("get_drawer_data_to_device_transfer device_type_id: " + str(device_type_id))

        if device_type_id == settings.DEVICE_TYPES["ROBOT"]:
            drawer_list = get_trolley_drawers_from_trolley_tx(batch_id=batch_id,
                                                              destination_device_id=device_id,
                                                              source_trolley_id=trolley_id,
                                                              transfer_cycle_id=transfer_cycle_id)
            logger.info("Output get_drawer_data_to_device_transfer {}".format(drawer_list))

        elif device_type_id == settings.DEVICE_TYPES["CSR"]:
            drawer_list = get_trolley_drawers_from_trolley_tx_csr(batch_id=batch_id,
                                                                  destination_device_id=device_id,
                                                                  source_trolley_id=trolley_id,
                                                                  transfer_cycle_id=transfer_cycle_id)
            logger.info("Output get_drawer_data_to_device_transfer {}".format(drawer_list))

        else:
            return error(1020, " device_id")
        if len(drawer_list):
            drawer_serial_number = drawer_list[0]['serial_number']
        else:
            drawer_serial_number = 0
        # update couch db with scanned drawer
        couch_db_update_status = canister_transfer_couch_db_update(device_id=int(device_id),
                                                                   flow=constants.KEY_TRANSFER_FROM_TROLLEY,
                                                                   system_id=system_id,
                                                                   drawer_id=None,
                                                                   pending_transfer=None,
                                                                   drawer_serial_number=drawer_serial_number
                                                                   )
        logger.info("get_canister_data_to_device_transfer couch db status: " + str(couch_db_update_status))

        return create_response(drawer_list)

    except RealTimeDBException as e:
        return error(2005, " - " + str(e))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting drawer data from device transfer")


@validate(required_fields=["company_id", "system_id", "batch_id", "device_id", "transfer_cycle_id"])
def get_cart_data_to_device_transfer(args: dict):
    """
    Method to fetch data for cart for transfer from trolley to robot and csr
    @param args: dict
    @return: json
    """
    logger.info("Input get_cart_data_from_device_transfer: " + str(args))
    company_id = int(args["company_id"])
    system_id = int(args["system_id"])
    batch_id = int(args["batch_id"])
    device_id = int(args["device_id"])
    transfer_cycle_id = int(args["transfer_cycle_id"])
    from_app = args.get("from_app", False)

    try:
        # fetch device_type based on id to differentiate between robot and csr to suggest destination drawers
        device_data = get_device_data_by_device_id_dao(device_id=device_id)
        if not device_data:
            return error(1020, "device_id")
        device_type_id = device_data.device_type_id_id
        logger.info("device_type_id: " + str(device_type_id))

        if device_type_id == settings.DEVICE_TYPES["ROBOT"]:
            # To return trolley list
            trolley_list = get_trolley_to_transfer_canisters_from_trolley(batch_id=batch_id,
                                                                          transfer_cycle_id=transfer_cycle_id,
                                                                          dest_device_id=device_id,
                                                                          from_app=from_app)
            logger.info("trolley get_cart_data_from_device_transfer: " + str(trolley_list))

            pending_devices = get_pending_trolleys_for_from_trolley_flow(batch_id=batch_id,
                                                                         transfer_cycle_id=transfer_cycle_id,
                                                                         current_device=device_id)

        elif device_type_id == settings.DEVICE_TYPES["CSR"]:
            # check pending transfer key in couch db
            couch_db_data = get_canister_transfer_data_from_couch_db_(device_id=int(device_id),
                                                                      system_id=system_id)

            logger.info("get_canister_transfer_data_from_couch_db_ couch db status: " + str(couch_db_data))

            if couch_db_data and 'pending_transfer' in couch_db_data and couch_db_data['pending_transfer'] == True:
                trolley_list = list()
            else:
                # To return trolley list
                trolley_list = get_trolley_to_transfer_canisters_from_trolley_to_csr(batch_id=batch_id,
                                                                                     transfer_cycle_id=transfer_cycle_id,
                                                                                     dest_device_id=device_id,
                                                                                     from_app=from_app)
                logger.info("trolley get_cart_data_from_device_transfer: " + str(trolley_list))

            pending_devices = get_pending_trolleys_for_from_trolley_flow_csr(batch_id=batch_id,
                                                                             transfer_cycle_id=transfer_cycle_id,
                                                                             current_device=device_id)

        else:
            return error(9059)

        response = {"trolley_list": trolley_list, "pending_devices": pending_devices}
        logger.info("Output get_cart_data_from_device_transfer {}".format(response))

        return create_response(response)

    except RealTimeDBException as e:
        return error(2005, " - " + str(e))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting canister data from device transfer")


@log_args_and_response
def get_canister_transfer_data_from_couch_db_(device_id: int, system_id: int):
    try:
        logger.info("canister_transfer_couch_db_update {}, {}".format(device_id, system_id))
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = 'canister_transfer_{}'.format(device_id)
        table = cdb.get(_id=id)
        logger.info("previous table canister_transfer_couch_db_update {}".format(table))

        if table is None:  # when no document available for given device_id
            table = {"_id": id, "type": 'canister_transfer', "data": {"scanned_drawer": None, "timestamp": None}}

        if not "data" in table:
            table["data"] = dict()

        return table["data"]

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        raise RealTimeDBException("Couch db Document update conflict.")

    except Exception as e:
        logger.error(e)
        raise RealTimeDBException('Couch db update failed while transferring canisters')


@log_args_and_response
@retry_exception(times = 3, exceptions=(couchdb.http.ResourceConflict, couchdb.http.HTTPError))
def canister_transfer_couch_db_update(device_id: int, flow: str, system_id: int,
                                      drawer_id: [int, None], pending_transfer: [bool, None],
                                      drawer_serial_number: [int, None]):
    try:
        logger.info("canister_transfer_couch_db_update {}, {}, {}".format(device_id, flow, system_id))
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = 'canister_transfer_{}'.format(device_id)
        table = cdb.get(_id=id)
        logger.info("canister_transfer_couch_db_update {}".format(drawer_id))
        logger.info("previous table canister_transfer_couch_db_update {}".format(table))

        if table is None:  # when no document available for given device_id
            table = {"_id": id, "type": 'canister_transfer', "data": {"scanned_drawer": None, "timestamp": None}}

        if not len(table["data"]):
            table["data"] = {
                            "scanned_drawer": None,
                            "currently_scanned_drawer_sr_no": None,
                            "previously_scanned_drawer_sr_no": None,
                            "timestamp": get_current_date_time()
                          }

        # when document is cleared
        if not "timestamp" in table["data"]:
            table["data"]["timestamp"] = get_current_date_time()

        if not "scanned_drawer" in table["data"]:
            table["data"]["scanned_drawer"] = None

        if "currently_scanned_drawer_sr_no" not in table['data'] or drawer_serial_number == 0:
            table["data"]["currently_scanned_drawer_sr_no"] = None
            table["data"]["previously_scanned_drawer_sr_no"] = None

        if drawer_serial_number and table["data"]["currently_scanned_drawer_sr_no"] != drawer_serial_number:
            table["data"]["previously_scanned_drawer_sr_no"] = table["data"]["currently_scanned_drawer_sr_no"]
            table["data"]["currently_scanned_drawer_sr_no"] = drawer_serial_number

        if drawer_id and table["data"]["scanned_drawer"] != drawer_id:
            table["data"]["scanned_drawer"] = drawer_id
        elif not drawer_id:
            if pending_transfer is not None:
                table["data"]["pending_transfer"] = pending_transfer
            else:
                table["data"]["timestamp"] = get_current_date_time()
        else:
            return True

        logger.info("updated table canister_transfer_couch_db_update {}".format(table))
        cdb.save(table)
        return True

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        raise RealTimeDBException("Couch db Document update conflict.")

    except Exception as e:
        logger.error(e)
        raise RealTimeDBException('Couch db update failed while transferring canisters')


@log_args_and_response
def get_pending_cycle_data_based_on_status(pending_guided_cycles: list, company_id: int, system_id: int) -> tuple:
    """
    Method to get pending device name and id based on status
    @param company_id:
    @param pending_guided_cycles:
    @param system_id:
    @return:
    """
    try:
        logger.debug("In get_pending_cycle_data_based_on_status")
        # At this point batch of pending cycle is already done or deleted.
        # get first cycle of pending cycles
        pending_cycle = None
        for cycle in pending_guided_cycles:
            pending_cycle = cycle
            break

        pending_cycle_status = pending_cycle["status"]
        cart_id = pending_cycle["cart_id"]
        # pending_batch_id = pending_cycle["batch_id"]
        args = {"guided_tx_cycle_id": pending_cycle["id"], "company_id": company_id,
                "batch_id": pending_cycle["batch_id"]}

        if pending_cycle_status == constants.GUIDED_META_RECOMMENDATION_DONE:
            # In Fetch the Drugs Screen, internally mark pending cycles as Done and
            # return batch id and device name as None as no user action needed in this case
            logger.debug("get_pending_cycle_data_based_on_status: "
                         "In guided module 0 so ineternally updating guided meta")
            return update_guided_cycle_for_batch_done(args)

        elif pending_cycle_status == constants.GUIDED_META_DRUG_BOTTLE_FETCHED:
            # In Transfer to Cart Screen, Check if canisters in trolley if so return it to csr else no user action
            # needed
            canisters_in_trolley = get_available_canisters_in_device(device_id=cart_id)
            if canisters_in_trolley:
                logger.debug("get_pending_cycle_data_based_on_status: Canisters- {} in available in cart - {}."
                             " So now updating its transfer status in guided tracker".format(canisters_in_trolley,
                                                                                             cart_id))

                all_gt_ids = fetch_guided_tracker_ids_based_on_meta_id(guided_tx_cycle_id=pending_cycle["id"],
                                                                       transfer_status_list=
                                                                       [constants.GUIDED_TRACKER_PENDING])
                cart_canisters_gt_ids = fetch_guided_tracker_ids_by_canister_ids(canister_ids=canisters_in_trolley,
                                                                                 guided_tx_cycle_id=pending_cycle["id"],
                                                                                 transfer_status_list=
                                                                                 [constants.GUIDED_TRACKER_PENDING])

                if cart_canisters_gt_ids:
                    non_cart_canisters_gt_ids = list(set(all_gt_ids) - set(cart_canisters_gt_ids))
                else:
                    non_cart_canisters_gt_ids = all_gt_ids
                logger.info("get_pending_cycle_data_based_on_status: cart_canisters_gt_ids - {}, "
                            "non_cart_canisters_gt_ids - {}".format(cart_canisters_gt_ids, non_cart_canisters_gt_ids))

                if cart_canisters_gt_ids:
                    update1 = update_guided_tracker_status(guided_tracker_ids=cart_canisters_gt_ids,
                                                           status=constants.GUIDED_TRACKER_TRANSFER_SKIPPED)
                if non_cart_canisters_gt_ids:
                    update2 = update_guided_tracker_status(guided_tracker_ids=non_cart_canisters_gt_ids,
                                                           status=
                                                           constants.GUIDED_TRACKER_TRANSFER_AND_REPLENISH_SKIPPED)
                logger.debug("get_pending_cycle_data_based_on_status: status updated in guided tracker, "
                             "now updating guided meta and couch db doc")
                args.update(
                    {"status": constants.GUIDED_META_TO_ROBOT_DONE, "module_id": constants.GUIDED_TO_CSR_MODULE,
                     "transfer_done_from_portal": False})
                logger.debug(
                    "get_pending_cycle_data_based_on_status: In guided module 0 so internally updating guided meta")
                update_response = update_guided_cycle_status(args)
                logger.debug("get_pending_cycle_data_based_on_status: update done")
                parsed_response = json.loads(update_response)

                if parsed_response["status"] == settings.SUCCESS_RESPONSE:
                    logger.debug("get_pending_cycle_data_based_on_status: Fetching CSR data")
                    csr_system_id = get_csr_system_id_in_zone(company_id, system_id)
                    return True, update_response, pending_cycle["batch_id"], csr_system_id
                else:
                    return False, update_response, None, None
            else:
                logger.debug(
                    "get_pending_cycle_data_based_on_status: No canisters in cart so update "
                    "guided meta status as 119 and and reset couch docs internally")
                return update_guided_cycle_for_batch_done(args)

        elif pending_cycle_status == constants.GUIDED_META_TO_TROLLEY_DONE:
            # In replenish screen, call updateguidedtx API with module 3 and status - 117: It will handle status changes
            args.update({"status": constants.GUIDED_META_REPLENISH_DONE,
                         "module_id": constants.GUIDED_TO_DRUG_DISPENSER_MODULE,
                         "transfer_done_from_portal": False})
            logger.debug(
                "get_pending_cycle_data_based_on_status: In guided module 2 (replenish) "
                "so change status and move to csr")
            update_response = update_guided_cycle_status(args)
            logger.debug("get_pending_cycle_data_based_on_status: update done")
            parsed_response = json.loads(update_response)

            if parsed_response["status"] == settings.SUCCESS_RESPONSE:
                logger.debug("get_pending_cycle_data_based_on_status: Fetching CSR data")
                csr_system_id = get_csr_system_id_in_zone(company_id, system_id)

                return True, update_response, pending_cycle["batch_id"], csr_system_id
            else:
                return False, update_response, None, None
        elif pending_cycle_status == constants.GUIDED_META_REPLENISH_DONE:
            # in transfer to robot screen, return batch id and csr name if canisters in trolley else return none
            # If canisters in trolley and its status is in (120,121,123) then change its status as 140
            logger.debug("get_pending_cycle_data_based_on_status: In transfer to robot screen. "
                         "Fetching canisters in trolley")
            canisters_in_trolley = get_available_canisters_in_device(device_id=cart_id)
            if canisters_in_trolley:
                cart_canisters_gt_ids = fetch_guided_tracker_ids_by_canister_ids(canister_ids=canisters_in_trolley,
                                                                                 guided_tx_cycle_id=pending_cycle["id"],
                                                                                 transfer_status_list=[
                                                                                     constants.GUIDED_TRACKER_PENDING,
                                                                                     constants.GUIDED_TRACKER_REPLENISH,
                                                                                     constants.GUIDED_TRACKER_SKIPPED])
                if cart_canisters_gt_ids:
                    update1 = update_guided_tracker_status(guided_tracker_ids=cart_canisters_gt_ids,
                                                               status=constants.GUIDED_TRACKER_TRANSFER_SKIPPED)
                logger.debug("get_pending_cycle_data_based_on_status: status updated in guided tracker, "
                             "now updating guided meta and couch db doc")
                args.update(
                    {"status": constants.GUIDED_META_TO_ROBOT_DONE, "module_id": constants.GUIDED_TO_CSR_MODULE,
                     "transfer_done_from_portal": False})
                logger.debug(
                    "get_pending_cycle_data_based_on_status: In guided module 0 so ineternally updating guided meta")
                update_response = update_guided_cycle_status(args)
                logger.debug("get_pending_cycle_data_based_on_status: update done")
                parsed_response = json.loads(update_response)

                if parsed_response["status"] == settings.SUCCESS_RESPONSE:
                    logger.debug("get_pending_cycle_data_based_on_status: Fetching CSR data")
                    csr_system_id = get_csr_system_id_in_zone(company_id, system_id)
                    return True, update_response, pending_cycle["batch_id"], csr_system_id
                else:
                    return False, update_response, None, None
            else:
                logger.debug(
                    "get_pending_cycle_data_based_on_status: No canisters in cart so update "
                    "guided meta status and and reset couch docs internally")
                return update_guided_cycle_for_batch_done(args)

        else:
            # status-118, in transfer to csr screen, return batch id and csr name if canisters are there to
            # transfer to csr else return none
            logger.debug("get_pending_cycle_data_based_on_status: in transfer to csr screen, so now checking for if "
                         "canisters are in cart")
            canisters_in_trolley = get_available_canisters_in_device(device_id=cart_id)
            if canisters_in_trolley:
                logger.debug("get_pending_cycle_data_based_on_status: There are canisters in cart")
                csr_system_id = get_csr_system_id_in_zone(company_id, system_id)
                return True, create_response(True), pending_cycle["batch_id"], csr_system_id
            else:
                logger.debug(
                    "get_pending_cycle_data_based_on_status: No canisters to be transferred in CSR so update "
                    "guided meta status and couch docs internally")
                return update_guided_cycle_for_batch_done(args)

    except (InternalError, IntegrityError, DataError, KeyError) as e:
        logger.info(e)
        return e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_csr_system_id_in_zone(company_id: int, system_id: int) -> int:
    """
    Function to get system id of CSR by given robot's system_id
    @param company_id:
    @param system_id:
    @return:
    """
    try:
        csr_system_id_list = get_zone_wise_system_list(company_id=company_id,
                                                       device_type=[settings.DEVICE_TYPES['CSR']],
                                                       system_id=system_id)
        csr_system_id = None
        for each_id in csr_system_id_list:
            csr_system_id = each_id
            break
        return csr_system_id

    except (IntegrityError, InternalError, KeyError, Exception) as e:
        logger.error(e)
        raise


@log_args_and_response
@validate(required_fields=["batch_id", "company_id", "system_id"])
def get_update_trolley_canister_transfers(args: dict) -> dict:
    """
    @param args: dict
    @return : status
    """
    logger.info("In get_update_trolley_canister_transfers {}".format(args))
    company_id = int(args['company_id'])
    batch_id = int(args['batch_id'])
    pending_batch_id = None
    pending_system_id = None
    try:
        with db.transaction():

            update_can_tras_lock.acquire()

            # check if batch is already imported
            is_imported = db_is_imported(batch_id=batch_id)
            if is_imported is None or is_imported:
                return error(1020, "Batch already imported")

            # check if recommendation is already executed for given batch
            existing_cycle_list = check_transfer_recommendation_status(batch_id=batch_id)
            if len(existing_cycle_list):
                return error(9066)

            # Fetch system id based on batch id to get robot system id everytime
            logger.debug("Fetching robot system_id based on batch id")
            robot_system_id = get_system_id_from_batch_id(batch_id=batch_id)
            args['system_id'] = robot_system_id

            # check for any batch in progress, if any batch is in progress in current system then return error
            # progress_batch_id = get_progress_batch_id(system_id=robot_system_id)
            # if progress_batch_id:
            #     return error(14006)

            # check if guided flow is pending or not
            logger.debug("get_update_trolley_canister_transfers: checking for pending guided canister cycle")
            pending_guided_cycles = check_pending_guided_canister_transfer(system_id=robot_system_id)
            logger.error(
                "get_update_trolley_canister_transfers: Pending guided canister cycles - " + str(pending_guided_cycles))

            if pending_guided_cycles:
                #guided flow is running so can not start transfer flow.
                return error(14005)
                # status, response, pending_batch_id, pending_system_id = get_pending_cycle_data_based_on_status(
                #     pending_guided_cycles=pending_guided_cycles, company_id=company_id, system_id=robot_system_id)
                # if status:
                #     logger.debug("get_update_trolley_canister_transfers: Successfully updated pending guided cycle data")
                #     if pending_batch_id and pending_system_id:
                #         logger.debug("get_update_trolley_canister_transfers: Need to complete pending guided flow")
                #         return error(14005, "{},{}".format(pending_batch_id, pending_system_id))
                # else:
                #     logger.debug("get_update_trolley_canister_transfers: Error in updating guided cycle status")
                #     return response

            # check if any canisters are already present in trolley before starting transfers
            cart_canisters = check_canisters_present_in_cart(system_id=robot_system_id)
            if len(cart_canisters):
                canister_tx_meta_list = check_pending_canister_transfers(robot_system_id)
                if canister_tx_meta_list:
                    for data in canister_tx_meta_list:
                        couchdb_batch_id = data['batch_id']
                        couchdb_cycle_id = data['cycle_id']
                    update_couch_db_status, couch_db_response = update_canister_transfer_wizard_data_in_couch_db(
                        {"company_id": company_id, "batch_id": couchdb_batch_id,
                         "timestamp": get_current_date_time(), "robot_system_id": robot_system_id, "module_id": 2,
                         "transfer_cycle_id": couchdb_cycle_id})
                    logger.info(f"In get_update_trolley_canister_transfers, Found canister transfer of previous batch {couchdb_batch_id} pending.")
                    logger.info(
                        f"In get_update_trolley_canister_transfers, update_couch_db_status {update_couch_db_status}")
                    return create_response(True)
                return error(9067)

            # to populate the data corresponding to the trolley location id in the canister_transfers.
            status, response_dict = trolley_canister_transfers(args)
            if not status:
                return error(1000, str(response_dict))
            cycle_id_list = list(response_dict['cycle_device_dict'].keys())
            logger.info("get_update_trolley_canister_transfers cycle id list {}".format(cycle_id_list))

            if len(cycle_id_list):
                update_couch_db_status, couch_db_response = update_cycle_module_in_canister_tx_wizard_couch_db(
                    {"company_id": company_id, "module_id": 0, "batch_id": batch_id,
                     "transfer_cycle_id": min(cycle_id_list)})

                logger.debug("canister transfer: couch db updated with status: " + str(update_couch_db_status))

                if not update_couch_db_status:
                    return create_response(update_couch_db_status)
                logger.info("data added in canister transfer {}, {}".format(status, cycle_id_list))
                response = {"transfer_cycle_id": min(cycle_id_list),
                            "batch_id": batch_id}
            else:
                logger.info("get_update_trolley_canister_transfers reset couch db")
                couch_db_reset = update_couch_db_trolley(company_id=company_id,
                                                         status=constants.CANISTER_TRANSFER_TO_CSR_DONE,
                                                         transfer_cycle_id=None)

                response = {"transfer_cycle_id": 0,
                            "batch_id": batch_id,
                            "message": "No transfers available for this batch"}

            logger.info("Response of get_update_trolley_canister_transfers {}".format(response))
        return create_response(response)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        return error(2001)

    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Error in recommend canister transfer: "+str(e))

    finally:
        update_can_tras_lock.release()
        if int(os.environ["IS_RUNNING_RECOMMENDCANISTERTRANSFER_API"]) > 1:
            os.environ["IS_RUNNING_RECOMMENDCANISTERTRANSFER_API"] = str(int(os.environ["IS_RUNNING_RECOMMENDCANISTERTRANSFER_API"])-1)
        else:
            os.environ["IS_RUNNING_RECOMMENDCANISTERTRANSFER_API"] = "0"


@log_args_and_response
def trolley_canister_transfers(args: dict) -> tuple:
    """
    Function for assigning trolley to canisters that are needed to be transfered for particular batch
    and return list of trolleys
    @param args:
    @return:
    """
    company_id = int(args['company_id'])
    batch_id = int(args['batch_id'])
    system_id = int(args['system_id'])
    response_dict = {'cycle_device_dict': dict()}

    try:
        # to get the list of pending canister to be transferred for a particular batch
        get_transfer_status, response_data_dict = get_canister_transfers_by_batch(company_id, system_id, batch_id)

        if not len(response_data_dict['canister_transfer_dest_loc_dict']):
            return True, response_dict

        # to get location data of required devices(trolley) for transfers
        status, trolley_data_dict = get_required_trolley_for_transfers(
            company_id, response_data_dict['canister_transfer_dest_loc_dict'])
        logger.info(
            "Response {}, {}, {}, {}".format(get_transfer_status, response_data_dict, status, trolley_data_dict))

        if status:
            trolley_data_dict.update(response_data_dict)
            canister_csr_destination_location = response_data_dict['canister_csr_destination_location']

            # get sorted canister list by quantity
            # trolley_data_dict['sorted_canister_qty'] = get_batch_canister_list_sorted_by_quantity(batch_id=batch_id,
            #                                                                                       company_id=company_id)

            transfer_data_status, response_dict = get_canister_transfer_data_to_update(trolley_data_dict)

            if transfer_data_status:
                if len(response_dict['canister_transfer_data_dict']):
                    status = db_update_canister_transfers(
                        batch_id=batch_id,
                        canister_transfers=response_dict['canister_transfer_data_dict'],
                        canister_csr_destination_location=canister_csr_destination_location,
                        canister_cycle_id_dict=response_dict['canister_cycle_id_dict'],
                        cycle_device_dict=response_dict['cycle_device_dict'],
                        cycle_device_info_dict=response_dict['cycle_device_info_dict'])

                    logger.info("status and update_transfers {}".format(status))

                else:
                    return True, response_dict

                return True, response_dict
            else:
                return False, response_dict

        else:
            return False, trolley_data_dict

    except (InternalError, IntegrityError) as e:
        logger.info(e)
        return False, e

    except Exception as e:
        logger.error(e)
        return False, "Error in updating canister transfers"


@log_args_and_response
def get_canister_transfers_by_batch(company_id: int, system_id: int, batch_id: int) -> tuple:
    """
   Returns list of canisters which are needed to transfer from robot or shelf
   @param company_id:int
   @param system_id:int
   @param batch_id:int
   @return response : dict
   """
    try:

        pending_transfers = list()
        csr_canister_list = list()
        unreserved_canister_transfers_list = list()  # robot to robot reserved canister list for lower to upper level
        device_quad_csr_canister = dict()
        canister_transfer_source_loc_dict = dict()
        canister_transfer_dest_loc_dict = dict()
        canister_dest_temp_location = dict()
        canister_destination_dict = dict()
        destination_device_canister_dict = dict()
        canister_csr_destination_location = dict()
        unassigned_location_to_canister = list()
        delicate_transfers_device_dict = dict()  # all the delicate transfers for robot to robot from upper to lower
        robot_to_robot_canister_transfer_dest_loc_dict = dict()  # robot to robot transfer for swapping  canisters
        robot_transfers = list()
        reserved_canister_transfers_list = list()  # robot to robot reserved canister list for lower to upper level
        device_quad_drawer_empty_locations_copy = dict()
        robot_to_robot_count_dict = dict()

        device_quad_drawer_empty_locations, device_quad_drawer_unreserved_locations, device_quad_drawer_non_delicate_unreserved_locations = \
            db_get_quad_drawer_type_wise_empty_unreserved_locations(
                company_id=company_id,
                batch_id=batch_id,
                system_id=system_id,
                device_type=settings.DEVICE_TYPES['ROBOT'])

        slow_movers,non_slow_movers = db_get_quad_drawer_type_wise_non_delicate_reserved_locations(company_id=company_id,
                                                                                                   batch_id=batch_id,
                                                                                                   system_id=system_id)

        logger.info(
            "device_quad_drawer_empty_locations in robot wise :{} device_quad_drawer_unreserved_locations: {} ".format(
                device_quad_drawer_empty_locations, device_quad_drawer_unreserved_locations))

        logger.info(" slow_movers: {},non_slow_movers: {} ".format(
                slow_movers,
                non_slow_movers))

        # device_ll_capacity = CanisterMaster.db_get_empty_locations_quad_wise_lower_level(system_id=system_id)
        slow_mover_canisters = []
        non_slow_mover_canisters = []
        delicate_transfers = []
        for record in chain(db_get_pending_transfers(batch_id),
                            db_get_remove_canister_list(batch_id, system_id)
                            ):

            if (record['source_device_id'] == record['dest_device_id']) and \
                    (record['source_quadrant'] == record['dest_quadrant']):

                # if canister is on same device and quandrant and it is non-delicate
                # then it will not considered to be transferred
                if not record["is_delicate"]:
                    continue

                # if canister is delicate and it is already on lower drawer level
                # then it will not consider to be transferred
                if (record["is_delicate"] and record['source_drawer_level'] <= constants.MAX_DELICATE_DRAWER_LEVEL) or (record["is_delicate"] and
                                                                                                                        record['canister_type'] == settings.SIZE_OR_TYPE['BIG'] ):
                    continue
                if record['source_device_id'] not in robot_to_robot_count_dict.keys():
                    robot_to_robot_count_dict[record['source_device_id']] = 0
                robot_to_robot_count_dict[record['source_device_id']] += 1

                if robot_to_robot_count_dict[record['source_device_id']] > settings.LIMIT_FOR_EXTRA_TRANSFERS_FOR_ROBOT:
                    continue

            if record['source_device_id'] is None:
                print("onshelf canisters {}".format(record['id']))

            if record['id'] not in canister_transfer_source_loc_dict.keys():
                canister_transfer_source_loc_dict[record['id']] = (record['source_device_id'],
                                                                   record['source_container_id'],
                                                                   record['source_quadrant'])
            drawer_level = None
            location = None

            if record['source_device_type_id'] == settings.DEVICE_TYPES['CSR']:
                LIFT_DRAWER_LEVEL = settings.DRAWER_LEVEL_CSR['lift_trolley']

            else:
                LIFT_DRAWER_LEVEL = settings.DRAWER_LEVEL["lift_trolley"]

            if record['dest_device_id'] and record['dest_quadrant']:
                if record["is_delicate"] and record['canister_type'] == settings.SIZE_OR_TYPE['SMALL']:
                    try:
                        # first check for empty location at drawer level at lower for delicate canisters

                        if device_quad_drawer_empty_locations[record['dest_device_id']][record['dest_quadrant']
                        ][record['canister_type']][0]["drawer_level"] <= constants.MAX_DELICATE_DRAWER_LEVEL:
                            location = \
                            device_quad_drawer_empty_locations[record['dest_device_id']][record['dest_quadrant']][
                                record['canister_type']].pop(0)
                            if (record['source_device_id'] == record['dest_device_id']) and \
                                    (record['source_quadrant'] == record['dest_quadrant']):
                                if record['dest_device_id'] not in device_quad_drawer_empty_locations_copy.keys():
                                    device_quad_drawer_empty_locations_copy[record['dest_device_id']] = dict()
                                if record['dest_quadrant'] not in device_quad_drawer_empty_locations_copy[record['dest_device_id']].keys():
                                    device_quad_drawer_empty_locations_copy[record['dest_device_id']][record['dest_quadrant']] = dict()
                                if record['canister_type'] not in device_quad_drawer_empty_locations_copy[record['dest_device_id']][record['dest_quadrant']].keys():
                                    device_quad_drawer_empty_locations_copy[record['dest_device_id']][
                                        record['dest_quadrant']][record['canister_type']] = list()
                                device_quad_drawer_empty_locations_copy[record['dest_device_id']][
                                    record['dest_quadrant']][record['canister_type']].append(location)

                                delicate_transfers.append(record['id'])
                        else:
                            raise KeyError
                    except (KeyError, IndexError):
                        logger.debug(
                            "Can't find empty location for delicate canister in lower level. Trying to find unreserved location {}".format(
                                record))
                        # when empty canister is not available at lower level for delicate canister then check for unreserved non delicate canister at lower level
                        if not location:
                            try:
                                if \
                                        device_quad_drawer_non_delicate_unreserved_locations[record['dest_device_id']][
                                            record['dest_quadrant']][
                                            record['canister_type']][0][
                                            "drawer_level"] <= constants.MAX_DELICATE_DRAWER_LEVEL:
                                    location = \
                                        device_quad_drawer_non_delicate_unreserved_locations[record['dest_device_id']][
                                            record['dest_quadrant']][
                                            record['canister_type']].pop(0)
                                    unreserved_canister_transfers_list.append(
                                        {"canister_id": location['existing_canister_id'],
                                         "device_id": record['dest_device_id'],
                                         "quadrant": record['dest_quadrant'],
                                         "canister_type": record['canister_type'],
                                         "drawer_level": location['drawer_level'],
                                         "drug_usage": location['drug_usage'],
                                         "is_delicate": location['is_delicate'],
                                         'container_id': location['container_id']})

                                    if (record['source_device_id'] == record['dest_device_id']) and \
                                            (record['source_quadrant'] == record['dest_quadrant']):
                                        if record['source_device_id'] not in delicate_transfers_device_dict.keys():
                                            delicate_transfers_device_dict[record['source_device_id']] = dict()
                                        if record['source_quadrant'] not in delicate_transfers_device_dict[record['source_device_id']].keys():
                                            delicate_transfers_device_dict[record['source_device_id']][record['source_quadrant']] = dict()
                                        if record['canister_type'] not in delicate_transfers_device_dict[record['source_device_id']][record['source_quadrant']].keys():
                                            delicate_transfers_device_dict[record['source_device_id']][
                                                record['source_quadrant']][record['canister_type']] = list()
                                        delicate_record = {"canister_id": record['id'],
                                                           "device_id": record['dest_device_id'],
                                                           "quadrant": record['dest_quadrant'],
                                                           "canister_type": record['canister_type'],
                                                           "drawer_level": record['drawer_level'],
                                                           "drug_usage": record['drug_usage'],
                                                           "container_id": record['source_container_id']}
                                        delicate_transfers_device_dict[record['source_device_id']][
                                            record['source_quadrant']][record['canister_type']].append(delicate_record)

                                else:
                                    raise KeyError
                            except (KeyError, IndexError):
                                logger.error(
                                    "Can't get type wise empty/unreserved location for delicate canister at low level"
                                    "try to find slow movers for delicate canisters {}".format(record))
                                # when unreserved non delicate canister is not there then check
                                # for reserverd slow moving canister
                                try:

                                    location = slow_movers[record['dest_device_id']][
                                        record['dest_quadrant']][
                                        record['canister_type']].pop(0)
                                    slow_mover_canisters.append(
                                        (location["id"], record['dest_device_id'], record['dest_quadrant']))
                                    reserved_canister_transfers_list.append(
                                        {"canister_id": location['existing_canister_id'],
                                         "device_id": record['dest_device_id'],
                                         "quadrant": record['dest_quadrant'],
                                         "canister_type": location['canister_type'],
                                         "drawer_level": location['drawer_level'],
                                         "drug_usage": location['drug_usage'],
                                         "is_delicate": location['is_delicate'],
                                         "container_id": location['container_id']})
                                    if (record['source_device_id'] == record['dest_device_id']) and \
                                            (record['source_quadrant'] == record['dest_quadrant']):
                                        if record['source_device_id'] not in delicate_transfers_device_dict.keys():
                                            delicate_transfers_device_dict[record['source_device_id']] = dict()
                                        if record['source_quadrant'] not in delicate_transfers_device_dict[record['source_device_id']].keys():
                                            delicate_transfers_device_dict[record['source_device_id']][record['source_quadrant']] = dict()
                                        if record['canister_type'] not in delicate_transfers_device_dict[record['source_device_id']][record['source_quadrant']].keys():
                                            delicate_transfers_device_dict[record['source_device_id']][
                                                record['source_quadrant']][record['canister_type']] = list()
                                        delicate_record = {"canister_id": record['id'],
                                                           "device_id": record['dest_device_id'],
                                                           "quadrant": record['dest_quadrant'],
                                                           "canister_type": record['canister_type'],
                                                           "drawer_level": record['drawer_level'],
                                                           "drug_usage": record['drug_usage'],
                                                           "container_id": record['source_container_id']}
                                        delicate_transfers_device_dict[record['source_device_id']][
                                            record['source_quadrant']][record['canister_type']].append(delicate_record)
                                        # delicate_transfers.append(record['id'])

                                except (KeyError, IndexError):
                                    logger.error("Can't get  slow movers for delicate canisters "
                                                 "try to find other canisters for delicate canisters {}".format(record))
                                    # when reserverd slow moving canister is not there then check
                                    # for reserverd non slow moving canister
                                    try:
                                        location = non_slow_movers[record['dest_device_id']][
                                            record['dest_quadrant']][
                                            record['canister_type']].pop(0)
                                        non_slow_mover_canisters.append(location["id"])
                                        reserved_canister_transfers_list.append(
                                            {"canister_id": location['existing_canister_id'],
                                             "device_id": record['dest_device_id'],
                                             "quadrant": record['dest_quadrant'],
                                             "canister_type": location['canister_type'],
                                             "drawer_level": location['drawer_level'],
                                             "drug_usage": location['drug_usage'],
                                             "is_delicate": location['is_delicate'],
                                             'container_id': location['container_id']})
                                        if (record['source_device_id'] == record['dest_device_id']) and \
                                                (record['source_quadrant'] == record['dest_quadrant']):
                                            if record['source_device_id'] not in delicate_transfers_device_dict.keys():
                                                delicate_transfers_device_dict[record['source_device_id']] = dict()
                                            if record['source_quadrant'] not in delicate_transfers_device_dict[
                                                record['source_device_id']].keys():
                                                delicate_transfers_device_dict[record['source_device_id']][
                                                    record['source_quadrant']] = dict()
                                            if record['canister_type'] not in \
                                                    delicate_transfers_device_dict[record['source_device_id']][
                                                        record['source_quadrant']].keys():
                                                delicate_transfers_device_dict[record['source_device_id']][
                                                    record['source_quadrant']][record['canister_type']] = list()
                                            delicate_record = {"canister_id": record['id'],
                                                               "device_id": record['dest_device_id'],
                                                               "quadrant": record['dest_quadrant'],
                                                               "canister_type": record['canister_type'],
                                                               "drawer_level": record['drawer_level'],
                                                               "drug_usage": record['drug_usage'],
                                                               "container_id": record['source_container_id']}
                                            delicate_transfers_device_dict[record['source_device_id']][
                                                record['source_quadrant']][record['canister_type']].append(
                                                delicate_record)
                                            # delicate_transfers.append(record['id'])
                                    except (KeyError, IndexError):
                                        logger.error(
                                            "Can't get type wise unreserved non delicate and reserved non delicate location for delicate canister at low level"
                                            "try to find delicate unreserved delicate canisters {}".format(record))
                                        # when reserverd non slow moving canister is not there then check
                                        # for unreserverd delicate canister
                                        try:
                                            if device_quad_drawer_unreserved_locations[record['dest_device_id']][
                                                record['dest_quadrant']
                                            ][record['canister_type']][0]["drawer_level"] <= constants.MAX_DELICATE_DRAWER_LEVEL:
                                                location = \
                                                device_quad_drawer_unreserved_locations[record['dest_device_id']][
                                                    record['dest_quadrant']][
                                                    record['canister_type']].pop(0)
                                                unreserved_canister_transfers_list.append(
                                                    {"canister_id": location['existing_canister_id'],
                                                     "device_id": record['dest_device_id'],
                                                     "quadrant": record['dest_quadrant'],
                                                     "canister_type": record['canister_type'],
                                                     "drawer_level": location['drawer_level'],
                                                     "drug_usage": location['drug_usage'],
                                                     "is_delicate": location['is_delicate'],
                                                     'container_id': location['container_id']})

                                                if (record['source_device_id'] == record['dest_device_id']) and \
                                                        (record['source_quadrant'] == record['dest_quadrant']):
                                                    if record[
                                                        'source_device_id'] not in delicate_transfers_device_dict.keys():
                                                        delicate_transfers_device_dict[
                                                            record['source_device_id']] = dict()
                                                    if record['source_quadrant'] not in delicate_transfers_device_dict[
                                                        record['source_device_id']].keys():
                                                        delicate_transfers_device_dict[record['source_device_id']][
                                                            record['source_quadrant']] = dict()
                                                    if record['canister_type'] not in \
                                                            delicate_transfers_device_dict[record['source_device_id']][
                                                                record['source_quadrant']].keys():
                                                        delicate_transfers_device_dict[record['source_device_id']][
                                                            record['source_quadrant']][record['canister_type']] = list()
                                                    delicate_record = {"canister_id": record['id'],
                                                                       "device_id": record['dest_device_id'],
                                                                       "quadrant": record['dest_quadrant'],
                                                                       "canister_type": record['canister_type'],
                                                                       "drawer_level": record['drawer_level'],
                                                                       "drug_usage": record['drug_usage'],
                                                                       "container_id": record['source_container_id']}
                                                    delicate_transfers_device_dict[record['source_device_id']][
                                                        record['source_quadrant']][record['canister_type']].append(
                                                        delicate_record)
                                            else:
                                                raise KeyError
                                        except (KeyError, IndexError):
                                            logger.error(
                                                "Can't get type wise empty/unreserved location for delicate canister at low level"
                                                "try to find slow movers for delicate canisters {}".format(record))
                                            # after that check for upper level empty and unreserved
                                            try:
                                                if (record['source_device_id'] == record['dest_device_id']) and \
                                                        (record['source_quadrant'] == record['dest_quadrant']):
                                                    del canister_transfer_source_loc_dict[record['id']]
                                                    continue
                                                location = \
                                                    device_quad_drawer_empty_locations[record['dest_device_id']][
                                                        record['dest_quadrant']][
                                                        record['canister_type']].pop(0)
                                            except (KeyError, IndexError):
                                                logger.error(
                                                    "Can't get type wise empty location for canister {}".format(record))
                                                try:

                                                    location = device_quad_drawer_unreserved_locations[record['dest_device_id']][
                                                            record['dest_quadrant']][
                                                            record['canister_type']].pop(0)
                                                    csr_canister_list.append(record["id"])
                                                    logger.error(
                                                        "Can't get any type empty/unreserved location for canister {}".format(record))

                                                except (KeyError, IndexError):
                                                    unassigned_location_to_canister.append(record["id"])
                                                    logger.error(
                                                        "Can't get any type empty/unreserved location for canister {}".format(
                                                            record))

                                                    continue

                    if not location:
                        unassigned_location_to_canister.append(record["id"])
                        logger.error("Can't get any type empty location for big canister {}".format(record))
                        continue

                    canister_dest_temp_location[record['id']] = location
                    if location['drawer_level'] in LIFT_DRAWER_LEVEL or record['source_drawer_level'] in LIFT_DRAWER_LEVEL:
                        drawer_level = settings.LIFT_TROLLEY
                    else:
                        drawer_level = settings.NORMAL_TROLLEY
                else:
                    try:
                        location = \
                        device_quad_drawer_empty_locations[record['dest_device_id']][record['dest_quadrant']][
                            record['canister_type']].pop()

                    except (KeyError, IndexError):
                        logger.debug(
                            "Can't find empty location for small canister. Trying to find Big canister location location {}".format(
                                record))
                        if record['canister_type'] == settings.SIZE_OR_TYPE['SMALL']:
                            try:
                                location = \
                                    device_quad_drawer_empty_locations[record['dest_device_id']][
                                        record['dest_quadrant']][
                                        settings.SIZE_OR_TYPE['BIG']].pop()
                            except (KeyError, IndexError):
                                logger.debug(
                                    "Can't find empty location for small canister. Trying to find unreserved location {}".format(
                                        record))
                                pass
                        if not location:
                            try:
                                location = \
                                    device_quad_drawer_unreserved_locations[record['dest_device_id']][
                                        record['dest_quadrant']][
                                        record['canister_type']].pop()
                                csr_canister_list.append(location['existing_canister_id'])
                            except (KeyError, IndexError):
                                logger.error(
                                    "Can't get type wise empty/unreserved location for canister {}".format(record))
                                try:
                                    location = \
                                        device_quad_drawer_unreserved_locations[record['dest_device_id']][
                                            record['dest_quadrant']][
                                            settings.SIZE_OR_TYPE['BIG']].pop()
                                    csr_canister_list.append(location['existing_canister_id'])
                                except (KeyError, IndexError):
                                    unassigned_location_to_canister.append(record["id"])
                                    logger.error(
                                        "Can't get any type empty/unreserved location for canister {}".format(record))

                                    continue

                    if not location:
                        unassigned_location_to_canister.append(record["id"])
                        logger.error("Can't get any type empty location for big canister {}".format(record))
                        continue

                    canister_dest_temp_location[record['id']] = location
                    if location['drawer_level'] in LIFT_DRAWER_LEVEL or record[
                        'source_drawer_level'] in LIFT_DRAWER_LEVEL:
                        drawer_level = settings.LIFT_TROLLEY
                    else:
                        drawer_level = settings.NORMAL_TROLLEY

            elif record['source_quadrant'] and record['source_device_id']:
                if record['source_device_id'] not in device_quad_csr_canister.keys():
                    device_quad_csr_canister[record['source_device_id']] = dict()
                if record['source_quadrant'] not in device_quad_csr_canister[record['source_device_id']].keys() and \
                        record['id'] not in csr_canister_list:
                    device_quad_csr_canister[record['source_device_id']][record['source_quadrant']] = list()
                if record['id'] in csr_canister_list:
                    continue
                device_quad_csr_canister[record['source_device_id']][record['source_quadrant']].append(record['id'])
                continue

            if not drawer_level:
                drawer_level = settings.LIFT_TROLLEY

            if record['dest_device_id'] not in destination_device_canister_dict.keys():
                destination_device_canister_dict[record['dest_device_id']] = dict()
                canister_transfer_dest_loc_dict[record['dest_device_id']] = dict()

            if drawer_level not in canister_transfer_dest_loc_dict[record['dest_device_id']].keys():
                canister_transfer_dest_loc_dict[record['dest_device_id']][drawer_level] = dict()

            if record['dest_quadrant'] not in canister_transfer_dest_loc_dict[record['dest_device_id']][
                drawer_level].keys():
                canister_transfer_dest_loc_dict[record['dest_device_id']][drawer_level][
                    record['dest_quadrant']] = dict()
            if constants.REGULAR_CANISTER not in canister_transfer_dest_loc_dict[record['dest_device_id']][drawer_level][
                    record['dest_quadrant']].keys():
                canister_transfer_dest_loc_dict[record['dest_device_id']][drawer_level][
                    record['dest_quadrant']][constants.REGULAR_CANISTER] = list()
            if constants.DELICATE_CANISTER not in canister_transfer_dest_loc_dict[record['dest_device_id']][drawer_level][
                record['dest_quadrant']].keys():
                canister_transfer_dest_loc_dict[record['dest_device_id']][drawer_level][
                    record['dest_quadrant']][constants.DELICATE_CANISTER] = list()
            if record['is_delicate'] and location['drawer_level'] <= constants.MAX_DELICATE_DRAWER_LEVEL and location[
                'drawer_level'] >= constants.MIN_DELICATE_DRAWER_LEVEL:
                canister_transfer_dest_loc_dict[record['dest_device_id']][drawer_level][record['dest_quadrant']][
                    constants.DELICATE_CANISTER].append(
                    record['id'])
            else:
                canister_transfer_dest_loc_dict[record['dest_device_id']][drawer_level][record['dest_quadrant']][
                    constants.REGULAR_CANISTER].append(
                    record['id'])
            canister_destination_dict[record['id']] = (record['dest_device_id'], drawer_level, record['dest_quadrant'])

            if record['dest_quadrant'] not in destination_device_canister_dict[record['dest_device_id']].keys():
                destination_device_canister_dict[record['dest_device_id']][record['dest_quadrant']] = list()

            destination_device_canister_dict[record['dest_device_id']][record['dest_quadrant']].append(record['id'])

            pending_transfers.append(record)
        swapping_list = list()
        if reserved_canister_transfers_list:
            reserved_canister_transfers_list = sorted(reserved_canister_transfers_list, key=lambda x: (x['drug_usage']))
            swapping_list.extend(reserved_canister_transfers_list)

        if unreserved_canister_transfers_list:
            unreserved_canister_transfers_list = sorted(unreserved_canister_transfers_list,
                                                        key=lambda x: (x['is_delicate'], x['drug_usage']))
            swapping_list.extend(unreserved_canister_transfers_list)

        if swapping_list:
            swapping_list_copy = swapping_list.copy()
            for index, item in enumerate(swapping_list_copy):
                # this list is for all the canisters which will be transfer to lower level to upper level
                device_id = item["device_id"]
                quadrant = item["quadrant"]
                can_type = item["canister_type"]
                drawer_level = item["drawer_level"]

                location = None
                if item['canister_id'] not in canister_transfer_source_loc_dict.keys():
                    canister_transfer_source_loc_dict[item['canister_id']] = (item['device_id'],
                                                                              item['container_id'],
                                                                              item['quadrant'])
                try:

                    if drawer_level and drawer_level in settings.DRAWER_LEVEL_CSR['lift_trolley']:
                        drawer_level = settings.LIFT_TROLLEY
                    else:
                        drawer_level = settings.NORMAL_TROLLEY
                    # if device_quad_drawer_empty_locations[device_id][quadrant][can_type]:
                    #     location = device_quad_drawer_empty_locations[device_id][quadrant][can_type].pop(0)
                    if device_id in device_quad_drawer_empty_locations.keys():
                        if quadrant in device_quad_drawer_empty_locations[device_id].keys():
                            if can_type in device_quad_drawer_empty_locations[device_id][quadrant].keys():
                                if device_quad_drawer_empty_locations[device_id][quadrant][can_type]:
                                    location = device_quad_drawer_empty_locations[device_id][quadrant][can_type].pop(0)

                    if device_id in device_quad_drawer_empty_locations_copy.keys() and location is None:
                        if quadrant in device_quad_drawer_empty_locations_copy[device_id].keys():
                            if can_type in device_quad_drawer_empty_locations_copy[device_id][quadrant].keys():
                                if device_quad_drawer_empty_locations_copy[device_id][quadrant][can_type]:
                                    location = device_quad_drawer_empty_locations_copy[device_id][quadrant][
                                        can_type].pop(0)

                    can_type_temp = can_type
                    if can_type == constants.SMALL_CANISTER_CODE and location is None:
                        can_type = constants.BIG_CANISTER_CODE
                        location = device_quad_drawer_empty_locations[device_id][quadrant][can_type].pop(0)
                    if location['id'] not in canister_transfer_source_loc_dict.keys():
                        canister_transfer_source_loc_dict[location['id']] = (location['device_id'],
                                                                             location['container_id'],
                                                                             location['quadrant'])

                    if device_id not in destination_device_canister_dict.keys():
                        destination_device_canister_dict[device_id] = dict()
                        canister_transfer_dest_loc_dict[device_id] = dict()

                    if drawer_level not in canister_transfer_dest_loc_dict[device_id].keys():
                        canister_transfer_dest_loc_dict[device_id][drawer_level] = dict()

                    if quadrant not in canister_transfer_dest_loc_dict[device_id][drawer_level].keys():
                        canister_transfer_dest_loc_dict[device_id][drawer_level][quadrant] = dict()
                    if constants.REGULAR_CANISTER not in \
                            canister_transfer_dest_loc_dict[device_id][drawer_level][
                                quadrant].keys():
                        canister_transfer_dest_loc_dict[device_id][drawer_level][
                            quadrant][constants.REGULAR_CANISTER] = list()
                    if constants.DELICATE_CANISTER not in \
                            canister_transfer_dest_loc_dict[device_id][drawer_level][
                                quadrant].keys():
                        canister_transfer_dest_loc_dict[device_id][drawer_level][
                            quadrant][constants.DELICATE_CANISTER] = list()
                    if location['is_delicate']:
                        canister_transfer_dest_loc_dict[device_id][drawer_level][quadrant][
                            constants.DELICATE_CANISTER].append(item["canister_id"])
                    else:
                        canister_transfer_dest_loc_dict[device_id][drawer_level][
                            quadrant][
                            constants.REGULAR_CANISTER].append(
                            item["canister_id"])
                    canister_destination_dict[item["canister_id"]] = (device_id, drawer_level, quadrant)

                    if quadrant not in destination_device_canister_dict[
                        device_id].keys():
                        destination_device_canister_dict[device_id][quadrant] = list()

                    destination_device_canister_dict[device_id][quadrant].append(item["canister_id"])
                    swapping_list.pop(0)

                except (KeyError, IndexError):
                    logger.error("Can't get type wise empty/unreserved location for unreserved/non delicate canister {}".format(item['canister_id']))
                    try:
                        can_type = can_type_temp
                        location = delicate_transfers_device_dict[device_id][quadrant][can_type].pop(0)
                        if location['canister_id'] not in canister_transfer_source_loc_dict.keys():
                            canister_transfer_source_loc_dict[location['canister_id']] = (location['source_device_id'],
                                                                                          location['source_container_id'],
                                                                                          location['source_quadrant'])
                        if device_id not in robot_to_robot_canister_transfer_dest_loc_dict.keys():
                            destination_device_canister_dict[device_id] = dict()
                            robot_to_robot_canister_transfer_dest_loc_dict[device_id] = dict()
                        lift_trolley = settings.LIFT_TROLLEY
                        normal_trolley = settings.NORMAL_TROLLEY
                        drawer_levels = [lift_trolley,normal_trolley]

                        for drawer_level in drawer_levels:
                            if drawer_level not in robot_to_robot_canister_transfer_dest_loc_dict[device_id].keys():
                                robot_to_robot_canister_transfer_dest_loc_dict[device_id][drawer_level] = dict()

                            if quadrant not in robot_to_robot_canister_transfer_dest_loc_dict[device_id][
                                drawer_level].keys():
                                robot_to_robot_canister_transfer_dest_loc_dict[device_id][drawer_level][
                                    quadrant] = dict()
                            if constants.REGULAR_CANISTER not in \
                                    robot_to_robot_canister_transfer_dest_loc_dict[device_id][drawer_level][
                                        quadrant].keys():
                                robot_to_robot_canister_transfer_dest_loc_dict[device_id][drawer_level][
                                    quadrant][constants.REGULAR_CANISTER] = list()
                            if constants.DELICATE_CANISTER not in \
                                    robot_to_robot_canister_transfer_dest_loc_dict[device_id][drawer_level][
                                        quadrant].keys():
                                robot_to_robot_canister_transfer_dest_loc_dict[device_id][drawer_level][
                                    quadrant][constants.DELICATE_CANISTER] = list()
                        canister_destination_dict[item["canister_id"]] = (device_id, normal_trolley, quadrant)
                        canister_destination_dict[location['canister_id']] = (device_id, lift_trolley, quadrant)

                        robot_to_robot_canister_transfer_dest_loc_dict[device_id][lift_trolley][
                                quadrant][constants.DELICATE_CANISTER].append(location['canister_id'])
                        robot_to_robot_canister_transfer_dest_loc_dict[device_id][normal_trolley][
                            quadrant][constants.REGULAR_CANISTER].append(item["canister_id"])
                        robot_transfers.append((item["canister_id"], location['canister_id']))
                        if location['canister_id'] in \
                                canister_transfer_dest_loc_dict[device_id][lift_trolley][quadrant][
                                    constants.DELICATE_CANISTER]:
                            canister_transfer_dest_loc_dict[device_id][lift_trolley][quadrant][
                                constants.DELICATE_CANISTER].remove(location['canister_id'])
                        else:
                            for device, drawer_data in canister_transfer_dest_loc_dict.items():
                                for drawer, quad_data in drawer_data.items():
                                    for quad, can_types in quad_data.items():
                                        for can_type, canisters in can_types.items():
                                            if location['canister_id'] in canisters:
                                                canisters.remove(location['canister_id'])

                        if quadrant not in destination_device_canister_dict[device_id].keys():
                            destination_device_canister_dict[device_id][quadrant] = list()
                        destination_device_canister_dict[device_id][quadrant].append(item["canister_id"])
                        destination_device_canister_dict[device_id][quadrant].append(location["canister_id"])
                        swapping_list.pop(0)

                    except (KeyError, IndexError):
                        csr_canister_list.append(item["canister_id"])
                        swapping_list.pop(0)
        #
        # if unreserved_canister_transfers_list:
        #     unreserved_canister_transfers_list = [item["canister_id"] for item in unreserved_canister_transfers_list]
        #     csr_canister_list.extend(unreserved_canister_transfers_list)


        logger.info(f'transfers for same device and quadrant for delicate canisters: {delicate_transfers} ')
        # todo remove 5 empty buffer locations only if tere are no empty loc left for that quad
        logger.info("device_quad_csr_canister ")
        for device, quad_can_list in device_quad_csr_canister.items():
            for quad, can_list in quad_can_list.items():
                big_loc_count = 0
                small_loc_count = 0
                if device in device_quad_drawer_empty_locations.keys() and quad in \
                    device_quad_drawer_empty_locations[device].keys():
                    if settings.SIZE_OR_TYPE['BIG'] in device_quad_drawer_empty_locations[device][quad].keys():
                        big_loc_count = len(device_quad_drawer_empty_locations[device][quad][
                            settings.SIZE_OR_TYPE['BIG']])
                    if settings.SIZE_OR_TYPE['SMALL'] in device_quad_drawer_empty_locations[device][quad].keys():
                        small_loc_count = len(device_quad_drawer_empty_locations[device][quad][
                    settings.SIZE_OR_TYPE['SMALL']])
                if device in device_quad_drawer_empty_locations_copy.keys() and quad in \
                    device_quad_drawer_empty_locations_copy[device].keys():
                    if settings.SIZE_OR_TYPE['BIG'] in device_quad_drawer_empty_locations_copy[device][quad].keys():
                        big_loc_count = len(device_quad_drawer_empty_locations_copy[device][quad][
                            settings.SIZE_OR_TYPE['BIG']])
                    if settings.SIZE_OR_TYPE['SMALL'] in device_quad_drawer_empty_locations_copy[device][quad].keys():
                        small_loc_count = len(device_quad_drawer_empty_locations_copy[device][quad][
                    settings.SIZE_OR_TYPE['SMALL']])

                if device in delicate_transfers_device_dict.keys() and quad in delicate_transfers_device_dict[device].keys():
                    if settings.SIZE_OR_TYPE['BIG'] in delicate_transfers_device_dict[device][quad].keys():
                        big_loc_count = len(delicate_transfers_device_dict[device][quad][
                            settings.SIZE_OR_TYPE['BIG']])
                    if settings.SIZE_OR_TYPE['SMALL'] in delicate_transfers_device_dict[device][quad].keys():
                        small_loc_count = len(delicate_transfers_device_dict[device][quad][
                    settings.SIZE_OR_TYPE['SMALL']])

                if big_loc_count + small_loc_count >= constants.PER_QUAD_CANISTER_BUFFER:
                    continue

                else:
                    logger.info(
                        f'In get_canister_transfers_by_batch, {small_loc_count + big_loc_count} empty location available for device: {device} quadrant: {quad}')
                    require_buffer = constants.PER_QUAD_CANISTER_BUFFER - (big_loc_count + small_loc_count)
                    csr_canister_list.extend(can_list[-require_buffer:])

        if len(csr_canister_list):
            csr_canister_list = sorted_csr_canister_list_by_big_canisters(csr_canister_list)
            canister_csr_destination_location = get_csr_lcoation_for_canister(company_id, csr_canister_list, system_id)

            for canister, location_tuple in canister_csr_destination_location.items():
                if location_tuple:
                    location_id, device_id, drawer_level = location_tuple
                    device_id = int(device_id)
                    if drawer_level and drawer_level in settings.DRAWER_LEVEL_CSR['lift_trolley']:
                        drawer_level = settings.LIFT_TROLLEY
                    else:
                        drawer_level = settings.NORMAL_TROLLEY
                    if device_id not in canister_transfer_dest_loc_dict.keys():
                        canister_transfer_dest_loc_dict[device_id] = dict()
                    if drawer_level not in canister_transfer_dest_loc_dict[device_id].keys():
                        canister_transfer_dest_loc_dict[device_id][drawer_level] = dict()
                    if None not in canister_transfer_dest_loc_dict[device_id][drawer_level].keys():
                        canister_transfer_dest_loc_dict[device_id][drawer_level][None] = dict()
                    if constants.REGULAR_CANISTER not in canister_transfer_dest_loc_dict[device_id][drawer_level][None].keys():
                        canister_transfer_dest_loc_dict[device_id][drawer_level][None][constants.REGULAR_CANISTER] = list()
                    if constants.DELICATE_CANISTER not in canister_transfer_dest_loc_dict[device_id][drawer_level][None].keys():
                        canister_transfer_dest_loc_dict[device_id][drawer_level][None][constants.DELICATE_CANISTER] = list()
                    source_device = canister_transfer_source_loc_dict[canister][0]
                    for device, drawer_data in canister_transfer_dest_loc_dict.items():
                        for drawer,quad_data in drawer_data.items():
                            for quad, can_types in quad_data.items():
                                for can_type , canisters in can_types.items():
                                    if canister in canisters:
                                        canisters.remove(canister)
                    for device, drawer_data in robot_to_robot_canister_transfer_dest_loc_dict.items():
                        for drawer,quad_data in drawer_data.items():
                            for quad, can_types in quad_data.items():
                                for can_type , canisters in can_types.items():
                                    if canister in canisters:
                                        canisters.remove(canister)
                    canister_transfer_dest_loc_dict[device_id][drawer_level][None][constants.REGULAR_CANISTER].append(
                        canister)

                else:
                    if None not in canister_transfer_dest_loc_dict.keys():
                        canister_transfer_dest_loc_dict[None] = {None: {None: {None : list()}}}
                    canister_transfer_dest_loc_dict[None][None][None][None].append(canister)
        canister_transfer_dest_loc_dict_copy = dict()
        canister_transfer_dest_loc_dict_copy[constants.ROBOT_TO_ROBOT_TRANSFERS] = robot_to_robot_canister_transfer_dest_loc_dict
        canister_transfer_dest_loc_dict_copy[constants.REGULAR_TRANSFERS] = canister_transfer_dest_loc_dict

        logger.info(
            f'In get_canister_transfers_by_batch, robot to robot transfers for unreserved canister to delicate canisters are {robot_transfers}')

        logger.info(
            f'In robot to robot transfers count are {robot_to_robot_count_dict}')

        response_dict = {"canister_transfer_source_loc_dict": canister_transfer_source_loc_dict,
                         "canister_transfer_dest_loc_dict": canister_transfer_dest_loc_dict_copy,
                         "canister_destination_dict": canister_destination_dict,
                         "pending_transfers": pending_transfers,
                         "destination_device_canister_dict": destination_device_canister_dict,
                         "canister_csr_destination_location": canister_csr_destination_location,
                         "unassigned_location_to_canister": unassigned_location_to_canister
                         }

        logger.debug('Data for Pending Transfer: {}'.format(response_dict))
        return True, response_dict

    except (InternalError, IntegrityError) as e:
        logger.info(e)
        return False, "Error in getting pending transfers {}".format(e)

    except Exception as e:
        logger.error(f"Error in get_canister_transfers_by_batch, e: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_canister_transfers_by_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return False, "Error in getting pending transfers"


@log_args_and_response
def get_csr_lcoation_for_canister(company_id: int, csr_canister_list: list, system_id: int) -> dict:
    """
    Function to recommend csr locations for given canister list
    @return: dict
    """
    canister_csr_destination_location = dict()
    reserve_location_list = list()

    try:
        csr_device_ids = get_zone_wise_device_list(company_id, [settings.DEVICE_TYPES['CSR']], system_id)
        input_args = {'device_id': csr_device_ids[0],
                      'company_id': company_id}
        for canister in csr_canister_list:
            input_args['canister_id'] = canister
            input_args['reserved_location_list'] = reserve_location_list
            response = recommend_csr_location(input_args)
            loaded_response = json.loads(response)
            location_id = loaded_response['data']['location_id']
            logger.info(loaded_response)
            reserve_location_list.append(location_id)
            location_info = get_location_info_from_location_id(location_id=location_id)

            if location_id:
                canister_csr_destination_location[canister] = [str(location_info['location_number']),
                                                               str(location_info['device_id']),
                                                               location_info['drawer_level']]
            else:
                canister_csr_destination_location[canister] = None

        return canister_csr_destination_location

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return e

    except ValueError as e:
        logger.error(e)
        raise


@log_args_and_response
def get_required_trolley_for_transfers(company_id: int, canister_transfer_dest_loc_dict: dict) -> tuple:
    """
    Calculate number of trolley required for transfer
    @param company_id: company_id
    @param canister_transfer_dest_loc_dict: dict
    @return tuple
    """

    try:
        trolley_list = list()
        device_type_ids = [settings.DEVICE_TYPES['Canister Transfer Cart'],
                           settings.DEVICE_TYPES['Canister Cart w/ Elevator']]

        # to get list of devices(trolley) which are not in use
        device_trolley_data_dict = get_available_trolley_data(device_type_ids, company_id)

        # to get count of devices(trolley) required by device_type
        trolley_required_by_type, device_quad_drawer_dict = get_required_trolley_count(canister_transfer_dest_loc_dict)

        for trolley_type, count in trolley_required_by_type.items():
            if trolley_type not in device_trolley_data_dict.keys():
                return False, "Trolley not available"
            if count > 0:
                for trolley in device_trolley_data_dict[trolley_type]:
                    trolley_list.append(trolley['id'])

        if not len(trolley_list):
            return False, "No trolley available for transfer"

        # to get location data of required devices(trolley)
        trolley_locations, drawer_location_info, location_device_dict = get_location_data_from_device_ids(trolley_list)

        response = {"trolley_list": trolley_list,
                    "device_quad_drawer_dict": device_quad_drawer_dict,
                    "trolley_locations": trolley_locations,
                    "location_device_dict": location_device_dict
                    }
        return True, response

    except (InternalError, IntegrityError) as e:
        return False, e

    except Exception as e:
        logger.error(e)
        return False, "Error in getting required CART for transfer"


def get_canister_transfer_data_to_update(trolley_data_dict: dict) -> tuple:
    """
    Function will assign device(trolley) location to each canister.
    @param trolley_data_dict: dict
    @return tuple
    """

    logger.info("Input args for get_canister_transfer_data_to_update {}".format(trolley_data_dict))
    cycle_id = trolley_data_dict.get('cycle_id', 1)
    cycle_device_dict = trolley_data_dict.get('cycle_device_dict', dict())
    cycle_device_info_dict = trolley_data_dict.get('cycle_device_info_dict', dict())
    canister_cycle_id_dict = trolley_data_dict.get('canister_cycle_id_dict', dict())
    trolley_locations = deepcopy(trolley_data_dict['trolley_locations'])
    location_device_dict = trolley_data_dict['location_device_dict']
    canister_transfer_dest_loc_dict = trolley_data_dict['canister_transfer_dest_loc_dict']
    canister_transfer_source_loc_dict = trolley_data_dict['canister_transfer_source_loc_dict']
    canister_transfer_data_dict = trolley_data_dict.get('canister_transfer_data_dict', dict())

    pending_canister_transfer_dest_loc_dict = dict()
    on_shelf_canisters = list()
    lift_trolley_drawers = list()
    regular_trolley_drawers = list()

    default_tx_info_dict = {"to_cart_transfer_count": 0,
                            "from_cart_transfer_count": 0,
                            "normal_cart_count": set(),
                            "elevator_cart_count": set()}

    if settings.DEVICE_TYPES['Canister Cart w/ Elevator'] in trolley_locations.keys():
        lift_trolley_drawers = [drawer_id for drawer_id in
                                trolley_locations[settings.DEVICE_TYPES['Canister Cart w/ Elevator']].keys()]

    if settings.DEVICE_TYPES['Canister Transfer Cart'] in trolley_locations.keys():
        regular_trolley_drawers = [drawer_id for drawer_id in
                                   trolley_locations[settings.DEVICE_TYPES['Canister Transfer Cart']].keys()]

    try:
        if cycle_id not in cycle_device_dict.keys():
            cycle_device_dict[cycle_id] = list()
            cycle_device_info_dict[cycle_id] = dict()
        canister_transfer_dest_loc_dict = OrderedDict(sorted(canister_transfer_dest_loc_dict.items(), reverse=True))
        for transfer_type, transfers in canister_transfer_dest_loc_dict.items():
            for device, drawer_quad in transfers.items():
                for drawer_level, quad_canister in drawer_quad.items():
                    if drawer_level == 2 or len(regular_trolley_drawers) == 0:
                        device_type_id = settings.DEVICE_TYPES['Canister Cart w/ Elevator']
                        can_per_drawer = settings.ELEVATOR_TROLLEY_CANISTER_PER_DRAWER
                        for quad, can_types in quad_canister.items():
                            can_types = OrderedDict(sorted(can_types.items(), reverse=True))
                            for can_type, can_list in can_types.items():
                                can_list = get_canister_sorted_on_source_location(can_list, canister_transfer_source_loc_dict)
                                drawer_required = math.ceil(len(can_list) / can_per_drawer)
                                trolley_loc_list = list()
                                if len(lift_trolley_drawers) > 0:
                                    for i in range(0, drawer_required):
                                        if len(lift_trolley_drawers):
                                            drawer = lift_trolley_drawers.pop(0)
                                            trolley_loc_list.extend(trolley_locations[device_type_id][drawer])

                                    for canister in can_list:
                                        if device and quad is None:
                                            on_shelf_canisters.append(canister)

                                        if len(trolley_loc_list):
                                            source_device, level, quadrant = canister_transfer_source_loc_dict[canister]
                                            if not source_device:
                                                source_device = device
                                            if source_device not in cycle_device_dict[cycle_id]:
                                                cycle_device_info_dict[cycle_id][source_device] = deepcopy(default_tx_info_dict)
                                                cycle_device_dict[cycle_id].append(source_device)
                                            trolley_loc_id = trolley_loc_list.pop(0)
                                            canister_cycle_id_dict[canister] = cycle_id
                                            canister_transfer_data_dict[canister] = (
                                            trolley_loc_id, device, quad, drawer_level, source_device)
                                            if device not in cycle_device_dict[cycle_id]:
                                                cycle_device_dict[cycle_id].append(device)
                                                cycle_device_info_dict[cycle_id][device] = deepcopy(default_tx_info_dict)

                                            # add info for tx tables
                                            cycle_device_info_dict[cycle_id][device]["from_cart_transfer_count"] += 1
                                            cycle_device_info_dict[cycle_id][source_device]["to_cart_transfer_count"] += 1
                                            cycle_device_info_dict[cycle_id][device]["elevator_cart_count"].add(
                                                location_device_dict[trolley_loc_id[0]])
                                            cycle_device_info_dict[cycle_id][source_device]["elevator_cart_count"].add(
                                                location_device_dict[trolley_loc_id[0]])

                                        else:
                                            if transfer_type not in pending_canister_transfer_dest_loc_dict.keys():
                                                pending_canister_transfer_dest_loc_dict[transfer_type] = dict()
                                            if device not in pending_canister_transfer_dest_loc_dict[transfer_type].keys():
                                                pending_canister_transfer_dest_loc_dict[transfer_type][device] = dict()
                                            if drawer_level not in pending_canister_transfer_dest_loc_dict[transfer_type][device].keys():
                                                pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level] = dict()
                                            if quad not in pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level].keys():
                                                pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][quad] = dict()
                                            if can_type not in pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][quad].keys():
                                                pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][quad][can_type] = list()
                                            pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][quad][can_type].append(canister)

                                else:
                                    if transfer_type not in pending_canister_transfer_dest_loc_dict.keys():
                                        pending_canister_transfer_dest_loc_dict[transfer_type] = dict()
                                    if device not in pending_canister_transfer_dest_loc_dict[transfer_type].keys():
                                        pending_canister_transfer_dest_loc_dict[transfer_type][device] = dict()
                                    if drawer_level not in pending_canister_transfer_dest_loc_dict[transfer_type][device].keys():
                                        pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level] = dict()
                                    if quad not in pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level].keys():
                                        pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][quad] = dict()
                                    if can_type not in pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][quad].keys():
                                        pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][quad][can_type] = list()
                                    pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][quad][can_type].extend(can_list)

                    else:
                        device_type_id = settings.DEVICE_TYPES['Canister Transfer Cart']
                        can_per_drawer = settings.TROLLEY_CANISTER_PER_DRAWER
                        for quad, can_types in quad_canister.items():
                            for can_type, can_list in can_types.items():

                                can_list = get_canister_sorted_on_source_location(can_list, canister_transfer_source_loc_dict)
                                drawer_required = math.ceil(len(can_list) / can_per_drawer)
                                trolley_loc_list = list()
                                if len(regular_trolley_drawers) > 0:
                                    for i in range(0, drawer_required):
                                        if len(regular_trolley_drawers):
                                            drawer = regular_trolley_drawers.pop(0)
                                            trolley_loc_list.extend(trolley_locations[device_type_id][drawer])

                                    for canister in can_list:
                                        if device and quad is None:
                                            on_shelf_canisters.append(canister)

                                        if len(trolley_loc_list):
                                            source_device, level, quadrant = canister_transfer_source_loc_dict[canister]
                                            if not source_device:
                                                source_device = device
                                            if source_device not in cycle_device_dict[cycle_id]:
                                                cycle_device_info_dict[cycle_id][source_device] = deepcopy(default_tx_info_dict)
                                                cycle_device_dict[cycle_id].append(source_device)
                                            trolley_loc_id = trolley_loc_list.pop(0)
                                            canister_cycle_id_dict[canister] = cycle_id
                                            canister_transfer_data_dict[canister] = (
                                            trolley_loc_id, device, quad, drawer_level, source_device)
                                            if device not in cycle_device_dict[cycle_id]:
                                                cycle_device_dict[cycle_id].append(device)
                                                cycle_device_info_dict[cycle_id][device] = deepcopy(default_tx_info_dict)

                                            # add info for tx tables
                                            cycle_device_info_dict[cycle_id][device]["from_cart_transfer_count"] += 1
                                            cycle_device_info_dict[cycle_id][source_device]["to_cart_transfer_count"] += 1
                                            cycle_device_info_dict[cycle_id][device]["normal_cart_count"].add(
                                                location_device_dict[trolley_loc_id[0]])
                                            cycle_device_info_dict[cycle_id][source_device]["normal_cart_count"].add(
                                                location_device_dict[trolley_loc_id[0]])

                                        else:
                                            if transfer_type not in pending_canister_transfer_dest_loc_dict.keys():
                                                pending_canister_transfer_dest_loc_dict[transfer_type] = dict()
                                            if device not in pending_canister_transfer_dest_loc_dict[
                                                transfer_type].keys():
                                                pending_canister_transfer_dest_loc_dict[transfer_type][device] = dict()
                                            if drawer_level not in \
                                                    pending_canister_transfer_dest_loc_dict[transfer_type][
                                                        device].keys():
                                                pending_canister_transfer_dest_loc_dict[transfer_type][device][
                                                    drawer_level] = dict()
                                            if quad not in \
                                                    pending_canister_transfer_dest_loc_dict[transfer_type][device][
                                                        drawer_level].keys():
                                                pending_canister_transfer_dest_loc_dict[transfer_type][device][
                                                    drawer_level][quad] = dict()
                                            if can_type not in \
                                                    pending_canister_transfer_dest_loc_dict[transfer_type][device][
                                                        drawer_level][quad].keys():
                                                pending_canister_transfer_dest_loc_dict[transfer_type][device][
                                                    drawer_level][quad][can_type] = list()
                                            pending_canister_transfer_dest_loc_dict[transfer_type][device][
                                                drawer_level][quad][can_type].append(canister)

                                else:
                                    if transfer_type not in pending_canister_transfer_dest_loc_dict.keys():
                                        pending_canister_transfer_dest_loc_dict[transfer_type] = dict()
                                    if device not in pending_canister_transfer_dest_loc_dict[transfer_type].keys():
                                        pending_canister_transfer_dest_loc_dict[transfer_type][device] = dict()
                                    if drawer_level not in pending_canister_transfer_dest_loc_dict[transfer_type][
                                        device].keys():
                                        pending_canister_transfer_dest_loc_dict[transfer_type][device][
                                            drawer_level] = dict()
                                    if quad not in pending_canister_transfer_dest_loc_dict[transfer_type][device][
                                        drawer_level].keys():
                                        pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][
                                            quad] = dict()
                                    if can_type not in pending_canister_transfer_dest_loc_dict[transfer_type][device][
                                        drawer_level][quad].keys():
                                        pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][
                                            quad][can_type] = list()
                                    pending_canister_transfer_dest_loc_dict[transfer_type][device][drawer_level][quad][
                                        can_type].extend(can_list)

        if len(pending_canister_transfer_dest_loc_dict):
            # recursive call of same function
            cycle_id += 1
            trolley_data_dict['cycle_id'] = cycle_id
            trolley_data_dict['cycle_device_dict'] = cycle_device_dict
            trolley_data_dict['location_device_dict'] = location_device_dict
            trolley_data_dict['canister_transfer_dest_loc_dict'] = pending_canister_transfer_dest_loc_dict
            trolley_data_dict['canister_transfer_data_dict'] = canister_transfer_data_dict
            trolley_data_dict['canister_cycle_id_dict'] = canister_cycle_id_dict
            trolley_data_dict['cycle_device_info_dict'] = cycle_device_info_dict
            get_canister_transfer_data_to_update(trolley_data_dict)

        response = {"canister_transfer_data_dict": canister_transfer_data_dict,
                    "remaining_trolley_locations": trolley_locations,
                    "transfer_count": len(canister_transfer_data_dict),
                    "canister_cycle_id_dict": canister_cycle_id_dict,
                    "cycle_device_dict": cycle_device_dict,
                    "cycle_device_info_dict": cycle_device_info_dict
                    }

        return True, response

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return False, e

    except Exception as e:
        logger.error(e)
        return False, "Error in getting transfer data for update"


@log_args_and_response
def get_required_trolley_count(canister_transfer_dest_loc_dict: dict) -> tuple:
    """
    Finds number of devices(trolley) required for transfer recommendation
    @param canister_transfer_dest_loc_dict: dict
    @return tuple
    """
    # todo change trolley can capacity dynamic
    try:
        trolley_required_by_type = {settings.DEVICE_TYPES['Canister Transfer Cart']: 0,
                                    settings.DEVICE_TYPES['Canister Cart w/ Elevator']: 0}

        device_quad_drawer_dict = dict()
        device_drawer_required_dict = dict()
        trolley_drawer_count = 0
        lift_trolley_drawer_count = 0
        canister_transfer_dest_loc_dict = OrderedDict(sorted(canister_transfer_dest_loc_dict.items(), reverse=True))
        for transfer_type, transfers in canister_transfer_dest_loc_dict.items():
            for device, drawer_quad_data in transfers.items():
                # if device is not None:
                device_quad_drawer_dict[device] = dict()
                device_drawer_required_dict[device] = dict()
                for drawer_level, quad_can in drawer_quad_data.items():
                    if drawer_level == settings.TRANSFER_DL_LIFT:
                        canister_per_drawer = settings.ELEVATOR_TROLLEY_CANISTER_PER_DRAWER
                    else:
                        canister_per_drawer = settings.TROLLEY_CANISTER_PER_DRAWER

                    device_quad_drawer_dict[device][drawer_level] = dict()
                    device_drawer_required_dict[device][drawer_level] = 0
                    for quad, can_types in quad_can.items():
                        device_quad_drawer_dict[device][drawer_level][quad] = dict()
                        can_types = OrderedDict(sorted(can_types.items(), reverse=True))
                        for can_type, can_list in can_types.items():
                            if not len(can_list):
                                continue
                            drawer_req = math.ceil(len(can_list) / canister_per_drawer)
                            device_quad_drawer_dict[device][drawer_level][quad][can_type] = drawer_req
                            device_drawer_required_dict[device][drawer_level] += drawer_req

                            if drawer_level == settings.TRANSFER_DL_LIFT:
                                lift_trolley_drawer_count += drawer_req
                            else:
                                trolley_drawer_count += drawer_req

        required_lift_trolley = math.ceil(
            lift_trolley_drawer_count / settings.TROLLEY_DRAWERS['Canister Cart w/ Elevator'])
        required_reg_trolley = math.ceil(
            trolley_drawer_count / settings.TROLLEY_DRAWERS['Canister Transfer Cart'])

        if lift_trolley_drawer_count > 0 and trolley_drawer_count > 0:

            free_space = (required_lift_trolley * settings.TROLLEY_DRAWERS['Canister Cart w/ Elevator'])\
                         - lift_trolley_drawer_count
            if free_space > 0:
                total_drawer = (trolley_drawer_count * 2)

                if 0 < total_drawer <= free_space:
                    lift_trolley_drawer_count += total_drawer
                    trolley_drawer_count -= trolley_drawer_count
                    required_lift_trolley = math.ceil(
                        lift_trolley_drawer_count / settings.TROLLEY_DRAWERS['Canister Cart w/ Elevator'])
                    required_reg_trolley = math.ceil(
                        trolley_drawer_count / settings.TROLLEY_DRAWERS['Canister Transfer Cart'])

        trolley_required_by_type[settings.DEVICE_TYPES['Canister Transfer Cart']] = required_reg_trolley
        trolley_required_by_type[settings.DEVICE_TYPES['Canister Cart w/ Elevator']] = required_lift_trolley

        return trolley_required_by_type, device_quad_drawer_dict

    except Exception as e:
        logger.error(e)
        return False, "Error in getting required CART count"


def get_canister_sorted_on_source_location(canister_list, source_location_dict):
    """

    @param canister_list:
    @param source_location_dict:
    @return:
    """
    sorted_can_dict = OrderedDict()

    for can in canister_list:
        if source_location_dict[can] not in sorted_can_dict.keys():
            sorted_can_dict[source_location_dict[can]] = list()
        sorted_can_dict[source_location_dict[can]].append(can)
    ordered_can_dict = sorted(sorted_can_dict, key=lambda key: len(sorted_can_dict[key]), reverse=True)
    sorted_can_list = [item for sublist in ordered_can_dict for item in sorted_can_dict[sublist]]
    return sorted_can_list


@log_args
def skip_canister_transfers(args: dict):
    """
    Function to skip pending canister transfers and assign destination location of CSR
    @param args: dict
    @return:
    """
    logger.debug("In skip_canister_transfers")
    company_id = args['company_id']
    system_id = args['system_id']
    batch_id = args['batch_id']
    cycle_id = None
    tx_meta_id = None
    total_canister_list = []
    canister_tx_status = None
    updated_cycle_ids = 0

    try:
        # get pending canister list that needs to assign CSR location when transfer is skipped
        canister_list, cycle_id_list, device_list, cart_type_dict = get_pending_canister_transfers_for_batch(
            batch_id=batch_id)

        # get canister list for which to trolley is pending and mark them to trolley skipped
        pending_canister_list, pending_canister_list_cycle_wise = get_to_trolley_pending_canister_transfers_for_batch(
            batch_id=batch_id)

        if pending_canister_list:
            transfer_status_ = db_update_canister_tx_status_dao(batch_id=batch_id,
                                                                canister_id_list=pending_canister_list,
                                                                status=constants.CANISTER_TX_TO_TROLLEY_SKIPPED)
            logger.info("update_canister canister_tx_status {}".format(transfer_status_))

        for cycle_id, canisters in pending_canister_list_cycle_wise.items():

            # get total canister transfer from canister_transfers table
            total_canister_list_cycle_wise = get_total_canister_transfer_data_dao(batch_id=batch_id,
                                                                                  cycle_id=cycle_id,
                                                                                  skip_canister=False)

            # get total skip canister from canister_transfer table
            total_skip_canister_list_cycle_wise = get_total_canister_transfer_data_dao(batch_id=batch_id,
                                                                                       cycle_id=cycle_id,
                                                                                       skip_canister=True)

            total_canister_list.extend(total_canister_list_cycle_wise)

            # if all canister are skip from PPP(when import batch) - update canister_tx_meta status to CANISTER_TRANSFER_TO_CSR_DONE
            if total_canister_list_cycle_wise == total_skip_canister_list_cycle_wise:
                updated_cycle_ids += 1
                update_dict = {"status_id": constants.CANISTER_TRANSFER_TO_CSR_DONE,
                               "modified_date": get_current_date_time()}
                canister_tx_status = update_canister_tx_meta_by_batch_id(update_dict=update_dict,
                                                                         batch_id=batch_id,
                                                                         cycle_id=cycle_id)
                logger.info("In skip_canister_transfers: resting couchdb as skipped canisters")
                couch_db_update_company = update_couch_db_trolley(company_id=company_id,
                                                                  status=constants.CANISTER_TRANSFER_TO_CSR_DONE)
                logger.info("In skip_canister_transfers: canister_tx_status:{},batch_id: {}".format(canister_tx_status, batch_id))
                # return create_response(True)
        if updated_cycle_ids == len(pending_canister_list_cycle_wise):
            return create_response(True)

        # get tx meta id for CSR
        cycle_status_dict = get_csr_canister_tx_meta_id_for_batch(batch_id=batch_id)
        csr_device_ids = get_zone_wise_device_list(company_id, [settings.DEVICE_TYPES['CSR']], system_id)
        if not len(csr_device_ids):
            return error(1000, "No CSR available for given parameters")

        if not len(cycle_status_dict) and total_canister_list:
            cycle_id = 1
            create_dict = {'cycle_id': cycle_id,
                           'device_id': int(csr_device_ids[0]),
                           'batch_id': batch_id,
                           'status_id': constants.CANISTER_TRANSFER_TO_TROLLEY_DONE,
                           'to_cart_transfer_count': len(canister_list),
                           'from_cart_transfer_count': len(canister_list),
                           'normal_cart_count': len(cart_type_dict[settings.DEVICE_TYPES['Canister Transfer Cart']]),
                           'elevator_cart_count': len(cart_type_dict[settings.DEVICE_TYPES['Canister Cart w/ Elevator']]),
                           }

            update_dict = {'created_date': get_current_date_time(),
                           'modified_date': get_current_date_time()
                           }

            tx_meta_id = add_record_in_canister_tx_meta(create_dict=create_dict,
                                                        update_dict=update_dict)

        else:
            for cycle, tx_status in cycle_status_dict.items():
                tx_id, status = tx_status
                if status in [constants.CANISTER_TRANSFER_RECOMMENDATION_DONE, constants.CANISTER_TRANSFER_TO_TROLLEY_DONE]:
                    cycle_id = cycle
                    tx_meta_id = tx_id
                    break

            if not cycle_id:
                for cycle, tx_status in cycle_status_dict.items():
                    cycle_id = cycle
                    tx_meta_id, status = tx_status
                    break

        if canister_list:
            # assign destination location of CSR in canister_transfers to canisters for which transfer is skipped
            csr_device_id = assign_csr_location_to_pending_trolley_canisters(canister_list=list(canister_list.keys()),
                                                                             batch_id=batch_id,
                                                                             system_id=system_id,
                                                                             company_id=company_id)
            if not csr_device_id:
                return error(1000, "Error in assigning csr location to canisters")
            update_dict = {"from_ct_meta_id": tx_meta_id,
                          "transfer_status": constants.CANISTER_TX_TO_ROBOT_SKIPPED}
            canister_tx_status = update_canister_transfers(update_dict=update_dict,
                                                           canister_id_list=list(canister_list.keys()),
                                                           batch_id=batch_id)
            logger.info("updated data in canister transfers {}, {}".format(cycle_id, tx_meta_id, canister_tx_status))


            if cycle_id:
                # update transfer status to transfer done for robot and transfer to device pending for CSR
                status = update_cycle_done_for_pending_cycles(batch_id=batch_id,
                                                              tx_meta_id=tx_meta_id)

                if not status:
                    return error(1000, "Error in updating cycle for pending cycles")

            # reset couch db for devices (robot) as transfer for their canisters is skipped
            for device_id in device_list:
                reset_couch_db_dict_for_reset = {"system_id": system_id,
                                                 "document_name": str(
                                                     constants.CANISTER_TRANSFER_DEVICE_DOCUMENT_NAME) + '_{}'.format(
                                                     device_id),
                                                 "couchdb_level": constants.STRING_SYSTEM,
                                                 "key_name": "data"}
                reset_couch_db_document(reset_couch_db_dict_for_reset)

            # update csr couch db system level document
            couch_db_update_status = canister_transfer_couch_db_update(device_id=int(csr_device_ids[0]),
                                                                       flow=constants.KEY_TRANSFER_FROM_TROLLEY,
                                                                       system_id=system_id,
                                                                       drawer_id=None,
                                                                       pending_transfer=None,
                                                                       drawer_serial_number=None
                                                                       )
            logger.info("couch db update status {}".format(couch_db_update_status))

            if canister_list:
                # update company level transfer doc module if required
                couch_db_update_company = update_couch_db_trolley(company_id=company_id,
                                                                  status=constants.CANISTER_TRANSFER_TO_TROLLEY_DONE,
                                                                  transfer_cycle_id=cycle_id)
                logger.info("couch_db_update_company {}".format(couch_db_update_company))
            else:
                couch_db_update_company = update_couch_db_trolley(company_id=company_id,
                                                                  status=constants.CANISTER_TRANSFER_TO_CSR_DONE)

                logger.info("couch_db_update_company {}".format(couch_db_update_company))

        return create_response(True)

    except ValueError as e:
        logger.error(e)
        raise ValueError
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in skip_canister_transfers")


@log_args_and_response
def assign_csr_location_to_pending_trolley_canisters(canister_list: list,
                                                     batch_id: int,
                                                     system_id: int,
                                                     company_id: int):
    """
    Function that assign destination location of CSR to canisters that are in trolley and now not required for transfer
    @param canister_list: list
    @param batch_id: int
    @param system_id: int
    @param company_id: int
    @return:
    """
    logger.debug("In assign_csr_location_to_pending_trolley_canisters")
    try:
        reserve_location_list = list()
        csr_device_ids = get_zone_wise_device_list(company_id, [settings.DEVICE_TYPES['CSR']], system_id)
        csr_device = int(csr_device_ids[0])
        input_args = {'device_id': csr_device,
                      'company_id': company_id}
        for canister in canister_list:
            input_args['canister_id'] = canister
            input_args['reserved_location_list'] = reserve_location_list
            response = recommend_csr_location(input_args)
            loaded_response = json.loads(response)
            location_id = loaded_response['data']['location_id']
            logger.info(loaded_response)
            reserve_location_list.append(location_id)
            location_info = get_location_info_from_location_id(location_id=location_id)
            logger.info("location info in assign_csr_location_to_pending_trolley_canisters {}".format(location_info))

            if location_id:
                status = update_canister_loc_in_canister_transfers(batch_id=batch_id,
                                                                   canister_id=canister,
                                                                   dest_device_id=csr_device,
                                                                   dest_location_number=location_info['location_number'],
                                                                   dest_quadrant=None)
                logger.info("assign_csr_location_to_pending_trolley_canisters {}".format(status))
            else:
                return None

        return csr_device

    except ValueError as e:
        logger.error("Error in assign_csr_location_to_pending_trolley_canisters {}".format(e))
        raise ValueError
    except Exception as e:
        logger.error("Error in assign_csr_location_to_pending_trolley_canisters {}".format(e))
        return None


@log_args
@validate(required_fields=["device_id", "module_id", "batch_id", "user_id", "company_id", "system_id", "comments",
                           "canisters_to_skip"])
def canister_transfer_skip(args: dict) -> str:
    """
    Function to skip canister to transfer to robot or CSR
    @param args:
    @return:
    """
    logger.debug("Inside canister_transfer_skip")
    try:
        batch_id = args['batch_id']
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
        deactive_comments = args.get('deactive_comments', None)
        ppp_screen = args.get('ppp_screen', False)
        pending_transfer = args.get("pending_transfer", False)
        replace_confirmation = args.get('replace_confirmation', False)

        existing_canisters_data = get_canister_transfer_data(canister_id_list=canisters_to_skip,
                                                                                  batch_id=batch_id,
                                                                                  transfer_status=None)

        if module_id == constants.CANISTER_TRANSFER_TO_TROLLEY_MODULE:
            logger.info("canister_transfer_skip when transfer to trolley was ongoing for {}".format(module_id))
            if alt_canister:
                alt_canister_dict = dict()
                for index, canister in enumerate(canisters_to_skip):
                    alt_canister_dict[canister] = alt_canister[index]
                    # todo to check is canister is already removed and placed in trolley
                    if existing_canisters_data[canister]['trolley_loc_id'] == existing_canisters_data[canister]['location_id']:
                        if not replace_confirmation:
                            return error(1041)
                        else:
                            args_dict = {"canister_id": canister, "location_id": None,
                                         "company_id": int(company_id), "user_id": user_id}

                            response = update_canister_location(args_dict)
                            logger.debug(
                                "canister_transfer_skip: canister - {} , updated location as null with response- {}"
                                .format(canister, response))

                skip_status = constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE
                alt_added_status = add_alt_canister_in_canister_transfers(alt_canister=alt_canister_dict,
                                                                          batch_id=batch_id,
                                                                          existing_canister_data=existing_canisters_data,
                                                                          transfer_status=constants.CANISTER_TX_TO_TROLLEY_ALTERNATE)

                # update alternate canister in pack analysis tables
                response = update_pack_analysis_canisters_data(replace_canisters=alt_canister_dict,
                                                               batch_id=batch_id,
                                                               user_id=user_id,
                                                               transfer_replace=False)

                update_replenish_based_on_device(device_id)

            else:
                skip_status = constants.CANISTER_TX_TO_TROLLEY_SKIPPED

            # canister_tx_status = db_update_canister_tx_status_dao(batch_id=batch_id,
            #                                                                     canister_id_list=canisters_to_skip,
            #                                                                     status=skip_status)
            canister_tx_status = db_update_canister_tx_status_dao(batch_id=batch_id, canister_id_list=canisters_to_skip,
                                                                  status=skip_status)

        elif module_id == constants.CANISTER_TRANSFER_TO_ROBOT_MODULE:
            logger.info("canister_transfer_skip when transfer from trolley to robot was ongoing")

            if alt_canister:
                alt_canister_dict = dict()
                for index, canister in enumerate(canisters_to_skip):
                    alt_canister_dict[canister] = alt_canister[index]
                skip_status = constants.CANISTER_TX_TO_ROBOT_SKIPPED_AND_ALTERNATE
                alt_added_status = add_alt_canister_in_canister_transfers(alt_canister=alt_canister_dict,
                                                                          batch_id=batch_id,
                                                                          existing_canister_data=existing_canisters_data,
                                                                          transfer_status=constants.CANISTER_TX_TO_ROBOT_ALTERNATE)

                # update alternate canister in pack analysis tables
                response = update_pack_analysis_canisters_data(replace_canisters=alt_canister_dict,
                                                               batch_id=batch_id,
                                                               user_id=user_id,
                                                               device_id=device_id,
                                                               transfer_replace=False)

                update_replenish_based_on_device(device_id)

            else:
                skip_status = constants.CANISTER_TX_TO_ROBOT_SKIPPED

            tx_info = get_canister_tx_meta_id_for_canister_to_skip(
                existing_canisters_data=existing_canisters_data,
                company_id=company_id,
                batch_id=batch_id,
                system_id=system_id)
            if len(tx_info["in_trolley"]):
                update_dict = {"from_ct_meta_id": tx_info["tx_id"]}
                canister_tx_status = update_canister_transfers(update_dict=update_dict,
                                                               canister_id_list=tx_info["in_trolley"],
                                                               batch_id=batch_id)


                logger.info("canister_transfer_skip get_canister_tx_meta_id_for_canister_to_skip {}, status : {}".format(tx_info, canister_tx_status))

                # assign destination location of CSR to skipped canisters
                csr_device_id = assign_csr_location_to_pending_trolley_canisters(canister_list=tx_info["in_trolley"],
                                                                                 batch_id=batch_id,
                                                                                 system_id=system_id,
                                                                                 company_id=company_id)
                logger.info("Assigned csr destination location to canisters {}".format(csr_device_id))

            # todo get meta id of csr from canister tx meta
            # update skip status in canister transfer table
            # canister_tx_status = db_update_canister_tx_status_dao(batch_id=batch_id,
            #                                                                     canister_id_list=canisters_to_skip,
            #                                                                     status=skip_status)
            canister_tx_status = db_update_canister_tx_status_dao(batch_id=batch_id, canister_id_list=canisters_to_skip,
                                                                  status=skip_status)
            csr_status = get_csr_tx_status(tx_info["tx_id"])
            if csr_status == constants.CANISTER_TRANSFER_TO_CSR_DONE:
                db_update_canister_tx_meta_status_dao(tx_info["tx_id"])

        elif module_id == constants.CANISTER_TRANSFER_TO_CSR_MODULE:
            logger.info("canister_transfer_skip when transfer from trolley to CSR was ongoing")
            skip_status = constants.CANISTER_TX_TO_CSR_SKIPPED
            # canister_tx_status = db_update_canister_tx_status_dao(batch_id=batch_id,
            #                                                                     canister_id_list=canisters_to_skip,
            #                                                                     status=skip_status)
            canister_tx_status = db_update_canister_tx_status_dao(batch_id=batch_id, canister_id_list=canisters_to_skip,
                                                                  status=skip_status)

            # mark the canister location as null if user skip while transferring to csr
            for canister_id in canisters_to_skip:
                if existing_canisters_data[canister_id]['device_type_id'] in [
                    settings.DEVICE_TYPES['Canister Transfer Cart'],
                    settings.DEVICE_TYPES['Canister Cart w/ Elevator']]:
                    args_dict = {"canister_id": int(canister_id), "location_id": None,
                                 "company_id": int(company_id), "user_id": user_id}

                    response = update_canister_location(args_dict)
                    logger.debug("canister_transfer_skip: canister - {} , updated location as null with response- {}"
                                 .format(canister_id, response))

        elif not module_id and ppp_screen:
            logger.info("canister_transfer_skip when canister is skipped from PPP screen")
            if alt_canister:
                skip_status = constants.CANISTER_TX_TO_ROBOT_SKIPPED_AND_ALTERNATE
                alt_canister_dict = dict()
                for index, canister in enumerate(canisters_to_skip):
                    alt_canister_dict[canister] = alt_canister[index]
                alt_added_status = add_alt_canister_in_canister_transfers(alt_canister=alt_canister_dict,
                                                                          batch_id=batch_id,
                                                                          existing_canister_data=existing_canisters_data,
                                                                          transfer_status=constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_LATER)

                # update alternate canister in pack analysis tables
                response = update_pack_analysis_canisters_data(replace_canisters=alt_canister_dict,
                                                               batch_id=batch_id,
                                                               user_id=user_id,
                                                               device_id=device_id,
                                                               transfer_replace=False)

                update_replenish_based_on_device(device_id)
            else:
                skip_status = constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_AT_PPP

            # canister_tx_status = db_update_canister_tx_status_dao(batch_id=batch_id,
            #                                                                     canister_id_list=canisters_to_skip,
            #                                                                     status=skip_status)
            canister_tx_status = db_update_canister_tx_status_dao(batch_id=batch_id, canister_id_list=canisters_to_skip,
                                                                  status=skip_status)

            # mark the canister location as null if user skip while transferring to csr
            for canister_id in canisters_to_skip:
                if existing_canisters_data[canister_id]['device_type_id'] in [
                    settings.DEVICE_TYPES['Canister Transfer Cart'],
                    settings.DEVICE_TYPES['Canister Cart w/ Elevator']]:
                    args_dict = {"canister_id": int(canister_id), "location_id": None,
                                 "company_id": int(company_id), "user_id": user_id}

                    response = update_canister_location(args_dict)
                    logger.debug("canister_transfer_skip: canister - {} , updated location as null with response- {}"
                                 .format(canister_id, response))

        else:
            logger.info("Error in canister_transfer_skip invalid module")
            return error(1020)

        if deactive_canister:
            action = constants.CANISTER_TX_SKIPPED_AND_DEACTIVATE_ACTION
            for canister_id in canisters_to_skip:
                status = delete_canister_dao({"canister_id": canister_id,
                                          "company_id": company_id,
                                          "user_id": user_id,
                                          "comment": deactive_comments})
                logger.info(
                    "canister_transfer_skip deactivate canister for canister {}, {}".format(status, canister_id))

        else:
            action = constants.CANISTER_TX_SKIPPED_ACTION

        # add data in canister transfer cycle history table
        status = add_data_in_canister_transfer_history_tables(existing_canisters_data=existing_canisters_data,
                                                              original_canister=canisters_to_skip,
                                                              skip_status=skip_status,
                                                              action=action,
                                                              comment=comments,
                                                              user_id=user_id)

        logger.info("update_canister canister_tx_status {}".format(canister_tx_status))

        return create_response(True)

    except ValueError as e:
        logger.error("Error in canister_transfer_skip {}".format(e))
        raise ValueError
    except Exception as e:
        logger.error("Error in canister_transfer_skip {}".format(e))
        return error(1000, "Error in canister_transfer_skip")


@log_args_and_response
def get_canister_tx_meta_id_for_canister_to_skip(existing_canisters_data: dict, company_id: int, batch_id: int, system_id: int) -> dict:
    """

    @param existing_canisters_data:
    @param company_id:
    @param batch_id:
    @param system_id:
    @return:
    """
    trolley_type = None
    in_device = list()
    in_trolley = list()
    cycle_id = None
    tx_id = None

    try:
        for can, can_info in existing_canisters_data.items():
            if can_info['device_type_id'] in [settings.DEVICE_TYPES['ROBOT'], settings.DEVICE_TYPES['CSR']]:
                in_device.append(can)
            else:
                in_trolley.append(can)
                trolley_type = can_info['device_type_id']

        if in_trolley and trolley_type:
            # get tx meta id for CSR
            # cycle_status_dict = get_csr_canister_tx_meta_id_for_batch(batch_id=batch_id)
            cycle_status_dict = get_csr_canister_tx_meta_id(list(existing_canisters_data.keys())[0],batch_id)
            csr_device_ids = get_zone_wise_device_list(company_id, [settings.DEVICE_TYPES['CSR']], system_id)
            if not len(csr_device_ids):
                return error(1000, "No CSR available for given parameters")

            if not len(cycle_status_dict):
                cycle_id = 1
                create_dict = {'cycle_id': cycle_id,
                               'device_id': int(csr_device_ids[0]),
                               'batch_id': batch_id,
                               'status_id': constants.CANISTER_TRANSFER_TO_TROLLEY_DONE,
                               'to_cart_transfer_count': len(in_trolley),
                               'from_cart_transfer_count': len(in_trolley),
                               'normal_cart_count': 1 if trolley_type == settings.DEVICE_TYPES[
                                   'Canister Transfer Cart'] else 0,
                               'elevator_cart_count': 1 if trolley_type == settings.DEVICE_TYPES[
                                   'Canister Cart w/ Elevator'] else 0,
                               }

                update_dict = {'created_date': get_current_date_time(),
                               'modified_date': get_current_date_time()
                               }

                tx_id = add_record_in_canister_tx_meta(create_dict=create_dict,
                                                            update_dict=update_dict)

            else:
                for cycle, tx_status in cycle_status_dict.items():
                    tx_id, status = tx_status
                    if status in [constants.CANISTER_TRANSFER_RECOMMENDATION_DONE,
                                  constants.CANISTER_TRANSFER_TO_TROLLEY_DONE,
                                  constants.CANISTER_TRANSFER_TO_ROBOT_DONE]:
                        cycle_id = cycle
                        break

                if not cycle_id:
                    for cycle, tx_status in cycle_status_dict.items():
                        tx_id, status = tx_status
                        logger.info("No pending csr tx meta id so changing status as to robot done")
                        update_dict = {"status_id": constants.CANISTER_TRANSFER_TO_ROBOT_DONE,
                                       "modified_date": get_current_date_time()}
                        update_canister_meta_status = db_update_canister_tx_meta(update_dict=update_dict, meta_id=tx_id)
                        logger.info("update_canister_meta_status {}".format(update_canister_meta_status))
                        break

        return {"tx_id": tx_id, "in_trolley": in_trolley}

    except Exception as e:
        logger.error("Error in get_canister_tx_meta_id_for_canister_to_skip {}".format(e))
        raise


@log_args
@validate(required_fields=["device_id", "module_id", "batch_id", "user_id", "company_id", "system_id", "canister_list"])
def canister_transfer_later(args: dict) -> str:
    """
    Function to assign transfer later status to canister
    @param args:
    @return:
    """
    logger.debug("Inside canister_transfer_later")

    try:
        company_id = args['company_id']
        system_id = args['system_id']
        batch_id = args['batch_id']
        user_id = args['user_id']
        module_id = args['module_id']
        device_id = args['device_id']
        alt_canister_list = args['canister_list']
        call_from_portal = args.get("call_from_portal", False)
        pending_transfer = args.get("pending_transfer", False)

        if module_id == constants.CANISTER_TRANSFER_TO_TROLLEY_MODULE:
            transfer_status = constants.CANISTER_TX_TO_TROLLEY_ALTERNATE_TRANSFER_LATER
            filter_status = [constants.CANISTER_TX_TO_TROLLEY_ALTERNATE,
                             constants.CANISTER_TX_PENDING,
                             constants.CANISTER_TX_TO_TROLLEY_DONE,
                             constants.CANISTER_TX_TO_TROLLEY_ALTERNATE_TRANSFER_LATER]

        elif module_id == constants.CANISTER_TRANSFER_TO_ROBOT_MODULE:
            if pending_transfer:
                transfer_status = constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_AT_PPP
            else:
                transfer_status = constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_LATER
            filter_status = [constants.CANISTER_TX_TO_ROBOT_ALTERNATE,
                             constants.CANISTER_TX_TO_ROBOT_DONE,
                             constants.CANISTER_TX_TO_TROLLEY_DONE,
                             constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_LATER]
        else:
            return error(1020, "Invalid module")

        existing_canisters_data = get_canister_transfer_data(canister_id_list=alt_canister_list,
                                                                                  batch_id=batch_id,
                                                                                  transfer_status=filter_status)
        logger.info("canister_transfer_later existing_canisters_data {}".format(existing_canisters_data))

        if not len(existing_canisters_data):
            logger.error("Error in canister_transfer_later empty existing canister data")
            return error(1020, "Invalid canister list")

        # canister_tx_status = db_update_canister_tx_status_dao(batch_id=batch_id,
        #                                                                     canister_id_list=alt_canister_list,
        #                                                                     status=transfer_status)
        canister_tx_status = db_update_canister_tx_status_dao(batch_id=batch_id, canister_id_list=alt_canister_list,
                                                              status=transfer_status)
        logger.info("canister_transfer_later canister_tx_status {}".format(canister_tx_status))

        # add data in canister transfer cycle history table
        status = add_data_in_canister_transfer_history_tables(existing_canisters_data=existing_canisters_data,
                                                              original_canister=alt_canister_list,
                                                              skip_status=transfer_status,
                                                              action=constants.CANISTER_TX_TRANSFER_ACTION,
                                                              comment=None,
                                                              user_id=user_id)

        logger.info("canister_transfer_later canister history status {}".format(status))

        return create_response(True)

    except (DataError, ValueError) as e:
        logger.error("Error in canister_transfer_later {}".format(e))
        return error(0)


@log_args
def get_pending_canister_transfer_list(args: dict) -> str:
    """
    Function to get canister list for which transfer is pending i.e transfer later selected
    or canisters were onshelf
    @param args:
    @return:
    """
    logger.debug("Inside get_pending_canister_transfer_list")

    try:
        company_id = int(args['company_id'])
        system_id = int(args['system_id'])
        batch_id = int(args['batch_id'])
        user_id = int(args['user_id'])
        module_id = int(args['module_id'])
        device_id = int(args['device_id'])
        sort_fields = args.get('sort_fields', None)
        transfer_cycle_id = args['transfer_cycle_id']
        source_drawer_dict = dict()
        delicate_drawers_to_unlock = dict()

        if module_id == constants.CANISTER_TRANSFER_TO_TROLLEY_MODULE:
            transfer_data, source_drawer_dict,delicate_drawers_to_unlock = get_pending_canisters_to_be_transferred_to_trolley(
                batch_id=batch_id, source_device_id=device_id,
                sort_fields=sort_fields, transfer_cycle_id=transfer_cycle_id)

            pending_devices = get_pending_devices_to_trolleys(batch_id=batch_id,
                                                              transfer_cycle_id=transfer_cycle_id,
                                                              current_device=device_id)
            logger.debug("fetched pending devices data, now updating trolley data in couch db doc")

        else:
            transfer_data, drawer_list_to_unlock, quad_canister_type_dict = \
                get_pending_canister_transfers_by_device(batch_id=batch_id, dest_device_id=device_id,
                                                         transfer_cycle_id=transfer_cycle_id,
                                                         sort_fields=sort_fields)

            # get drawers to unlock in case of multiple quadrants
            if len(drawer_list_to_unlock):
                drawer_name = list()
                for dest_quadrant, canister_type_dict in quad_canister_type_dict.items():
                    source_drawer_dict, delicate_drawers_to_unlock = get_delicate_drawers(device_id,
                                                                                          dest_quadrant,
                                                                                          canister_type_dict)

                    # for drawer, location in quad_drawer_loc.items():
                    #     if drawer not in source_drawer_dict.keys():
                    #         source_drawer_dict[drawer] = location
                    #     else:
                    #         source_drawer_dict[drawer]['to_device'].extend(location['to_device'])

            pending_devices = get_pending_trolleys_for_from_trolley_flow(batch_id=batch_id,
                                                                         transfer_cycle_id=transfer_cycle_id,
                                                                         current_device=device_id)
            logger.debug("fetched pending devices data, now updating trolley data in couch db doc")

        # update couch db with scanned drawer
        if len(transfer_data):
            pending_transfer = True
        else:
            pending_transfer = False
        couch_db_update_status = canister_transfer_couch_db_update(device_id=int(device_id),
                                                                   flow=constants.KEY_TRANSFER_FROM_TROLLEY,
                                                                   system_id=system_id,
                                                                   drawer_id=None,
                                                                   pending_transfer=pending_transfer,
                                                                   drawer_serial_number=None
                                                                   )
        logger.info("get_canister_data_to_device_transfer couch db status: " + str(couch_db_update_status))

        response = {"transfer_data": transfer_data,
                    "regular_drawers_to_unlock": list(source_drawer_dict.values()),
                    "delicate_drawers_to_unlock": list(delicate_drawers_to_unlock.values()),
                    "pending_devices": pending_devices,
                    }
        logger.info("Output get_canister_data_to_device_transfer {}".format(response))

        return create_response(response)

    except (DataError, ValueError) as e:
        logger.error("Error in canister_transfer_later {}".format(e))
        return error(0)


@log_args_and_response
def update_canister_count_in_canister_transfer_couch_db(system_id, canister_id, source_device=None, dest_loc_id=None,
                                                        user_id=None, previous_location=None, dest_device_type_id=None,
                                                        status_to_update=None):
    logger.info("update_canister couch db input  {}, {}, {}, {}, {}"
                .format(system_id, canister_id, source_device, dest_loc_id, user_id))
    try:
        canister_history_list = list()
        system_device_dict = dict()
        if dest_loc_id is None:
            # when user remove canister from csr or robot
            canister_transfer_data = db_get_latest_canister_transfer_data_for_a_canister_from_robot_csr(
                canister_id)
            logger.info("cansiter transfer data {}".format(canister_transfer_data))
            if canister_transfer_data and canister_transfer_data['source_device_id'] is None\
                    or canister_transfer_data['source_device_type_id'] in [settings.DEVICE_TYPES['Canister Transfer Cart'],
                                                                           settings.DEVICE_TYPES['Canister Cart w/ Elevator']]:
                if canister_transfer_data["batch_status_id"] == settings.BATCH_IMPORTED:
                    trolley_loc_id = None
                    logger.info(
                        "Batch is imported so not giving trolley location to canister {}: Else trolley location was {}".format(
                            canister_id, canister_transfer_data['trolley_loc_id']))
                else:
                    trolley_loc_id = canister_transfer_data['trolley_loc_id']

                trolley_id = canister_transfer_data['trolley_id']
                trolley_drawer_id = canister_transfer_data['trolley_drawer_id']

                latest_record = get_canister_history_latest_record_can_id_dao(canister_id)
                logger.info("canister_tx_flow: latest record {}".format(latest_record))
                if latest_record and latest_record.id:
                    if latest_record.current_location_id_id is None:
                        logger.debug("canister_tx_flow: updating canister history - updating current loc")
                        update_history_dict = {"current_location_id": trolley_loc_id,
                                               "modified_by": user_id,
                                               "modified_date": get_current_date_time()}
                        status = update_canister_history_by_id_dao(update_history_dict, latest_record.id)
                    else:
                        logger.debug("canister_tx_flow: adding record in canister history in cart to cart tx case")
                        canister_history_dict = {
                            "canister_id": canister_id,
                            "current_location_id": trolley_loc_id,
                            "previous_location_id": latest_record.current_location_id_id,
                            "created_by": user_id,
                            "modified_by": user_id,
                        }
                        record = add_canister_history_data_dao(canister_history_dict=canister_history_dict)

                # update trolley location in canister master
                # status = CanisterMaster.update(location_id=trolley_loc_id) \
                #     .where(CanisterMaster.id == canister_id).execute()
                # status = assign_cart_location_to_canister(canister=canister_id, trolley_location_id=trolley_loc_id)

                update_type = update_canister_dao(update_dict={"location_id": trolley_loc_id},
                                                      id=canister_id)
                logger.info("In update_canister: canister master table updated: {}".format(update_type))


                # update status in canister transfer table
                if canister_transfer_data["status_id"] in [constants.CANISTER_TRANSFER_RECOMMENDATION_DONE,
                                                            constants.CANISTER_TRANSFER_TO_CSR_DONE,
                                                           constants.CANISTER_TRANSFER_TO_TROLLEY_DONE]:
                    if not status_to_update:
                        status_to_update = constants.CANISTER_TX_TO_TROLLEY_DONE
                    # canister_tx_status = db_update_canister_tx_status_dao(
                    #   batch_id=canister_transfer_data['batch_id'],
                    #   canister_id_list= [canister_id],
                    #   status=status_to_update)
                    canister_tx_status = db_update_canister_tx_status_dao(batch_id=canister_transfer_data['batch_id'],
                                                                          canister_id_list=[canister_id],
                                                                          status=status_to_update)

                    logger.info("update_canister canister_tx_status {}".format(canister_tx_status))

                insert_data = {'canister_transfer_id': canister_transfer_data['transfer_id'],
                               'action_id': constants.CANISTER_TX_TRANSFER_ACTION,
                               'current_status_id': status_to_update,
                               'previous_status_id': canister_transfer_data['transfer_status'],
                               'action_taken_by': constants.ROBOT_USER,
                               'action_datetime': get_current_date_time()
                               }

                # add data in CanisterTransferCycleHistory
                record = insert_canister_transfer_cycle_history_data_dao(data_dict=insert_data)
                transfer_cycle_history = record.id
                logger.info("Data added in canister transfer cycle history {}".format(insert_data))

            if canister_transfer_data:
                system_device_dict[canister_transfer_data['dest_system_id']] = canister_transfer_data['dest_device_id']
            system_device_dict[system_id] = source_device

            for system_id, device_id in system_device_dict.items():
                couch_db_update_status = canister_transfer_couch_db_update(device_id=device_id,
                                                                           flow=constants.KEY_TRANSFER_TO_TROLLEY,
                                                                           system_id=system_id,
                                                                           drawer_id=None,
                                                                           pending_transfer=None,
                                                                           drawer_serial_number=None)
                logger.info("update_canister couch db update status {}".format(couch_db_update_status))

        elif dest_loc_id is not None:
            # when placed canister to csr
            if dest_device_type_id and dest_device_type_id == settings.DEVICE_TYPES["CSR"]:
                canister_transfer_data = db_get_latest_canister_transfer_data_to_csr_from_trolley(
                    canister_id)

                if canister_transfer_data and canister_transfer_data['updated_dest_device_id'] == \
                        canister_transfer_data['dest_device_id'] and \
                        (canister_transfer_data['updated_dest_container_id'] ==
                         canister_transfer_data['recommended_container_id']):
                    logger.info("update_canister Correct location")

                    # update status in canister transfer
                    # canister_tx_status = CanisterTransfers.db_update_canister_tx_status(
                    #     batch_id=canister_transfer_data['batch_id'],
                    #     canister_id_list=[canister_id],
                    #     status=constants.CANISTER_TX_TO_CSR_DONE)
                    canister_tx_status = db_update_canister_tx_status_dao(batch_id=canister_transfer_data['batch_id'],
                                                                          canister_id_list=[canister_id],
                                                                          status=constants.CANISTER_TX_TO_CSR_DONE)
                    logger.info("update_canister canister_tx_status {}".format(canister_tx_status))

                    # add data in canister transfer history tables
                    insert_data = {'canister_transfer_id': canister_transfer_data['transfer_id'],
                                   'action_id': constants.CANISTER_TX_TRANSFER_ACTION,
                                   'current_status_id': constants.CANISTER_TX_TO_CSR_DONE,
                                   'previous_status_id': canister_transfer_data['transfer_status'],
                                   'action_taken_by': constants.ROBOT_USER,
                                   'action_datetime': get_current_date_time()
                                   }

                    # add data in CanisterTransferCycleHistory
                    record = insert_canister_transfer_cycle_history_data_dao(
                        data_dict=insert_data)
                    transfer_cycle_history = record.id
                    logger.info("Data added in canister transfer cycle history {}".format(insert_data))

                else:
                    logger.info("update_canister Incorrect location")

                if canister_transfer_data:
                    system_device_dict[canister_transfer_data['dest_system_id']] = canister_transfer_data['dest_device_id']

                system_device_dict[system_id] = source_device

                for system_id, device_id in system_device_dict.items():
                    couch_db_update_status = canister_transfer_couch_db_update(
                        device_id=device_id,
                        flow=constants.KEY_TRANSFER_FROM_TROLLEY,
                        system_id=system_id,
                        drawer_id=None,
                        pending_transfer=None,
                        drawer_serial_number=None)
                    logger.info("update_canister couch db update status {}".format(couch_db_update_status))

            else:
                # consider default device as robot
                canister_transfer_data = db_get_latest_canister_transfer_data_to_robot_from_trolley(
                    canister_id)

                if canister_transfer_data and canister_transfer_data['updated_dest_device_id'] == \
                        canister_transfer_data[
                            'dest_device_id'] and canister_transfer_data['updated_dest_quadrant'] == \
                        canister_transfer_data['dest_quadrant'] and not (canister_transfer_data["canister_type"] ==
                                                                         settings.SIZE_OR_TYPE["BIG"] and
                                                                         canister_transfer_data["drawer_type"] ==
                                                                         settings.SIZE_OR_TYPE["SMALL"]):
                    logger.info("update_canister correct location")
                    canister_tx_status = db_update_canister_tx_status_dao(batch_id=canister_transfer_data['batch_id'],
                                                                      canister_id_list=[canister_id],
                                                                      status=constants.CANISTER_TX_TO_ROBOT_DONE)
                    logger.info("update_canister canister_tx_status {}".format(canister_tx_status))

                    # add data in canister transfer history tables
                    insert_data = {'canister_transfer_id': canister_transfer_data['transfer_id'],
                                   'action_id': constants.CANISTER_TX_TRANSFER_ACTION,
                                   'current_status_id': constants.CANISTER_TX_TO_ROBOT_DONE,
                                   'previous_status_id': canister_transfer_data['transfer_status'],
                                   'action_taken_by': constants.ROBOT_USER,
                                   'action_datetime': get_current_date_time()
                                   }

                    # add data in CanisterTransferCycleHistory
                    record = insert_canister_transfer_cycle_history_data_dao(
                        data_dict=insert_data)
                    transfer_cycle_history = record.id
                    logger.info("Data added in canister transfer cycle history {}".format(insert_data))

                else:
                    logger.info("update_canister Incorrect location")

                if canister_transfer_data:
                    system_device_dict[canister_transfer_data['dest_system_id']] = canister_transfer_data[
                        'dest_device_id']

                system_device_dict[system_id] = source_device
                for system_id, device_id in system_device_dict.items():
                    couch_db_update_status = canister_transfer_couch_db_update(device_id=device_id,
                                                                               flow=constants.KEY_TRANSFER_FROM_TROLLEY,
                                                                               system_id=system_id,
                                                                               drawer_id=None,
                                                                               pending_transfer=None,
                                                                               drawer_serial_number=None)
                    logger.info("update_canister couch db update status {}".format(couch_db_update_status))

        return True

    except Exception as e:
        logger.error("update_canister_count_in_canister_transfer_couch_db {}".format(e))


@log_args_and_response
def update_couch_db_trolley(status: int, company_id: int, transfer_cycle_id: int = None) -> bool:
    """
    This function updates the canister-transfer-wizard couch db document for the given parameters
    """
    logger.debug("In update_couch_db_trolley")
    if status == constants.CANISTER_TRANSFER_TO_CSR_DONE and transfer_cycle_id is None:
        document_name = constants.CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME
        reset_couch_db_dict_for_reset = {"company_id": company_id,
                                         "document_name": document_name,
                                         "couchdb_level": constants.STRING_COMPANY,
                                         "key_name": "data"}
        reset_couch_db_document(reset_couch_db_dict_for_reset)
        return True
    else:
        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        doc_id = constants.CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME
        table = cdb.get(_id=doc_id)
        logger.debug("couch db doc: {}, data: ".format(doc_id, table))
        if table is not None:
            if status == constants.CANISTER_TRANSFER_TO_ROBOT_DONE:
                table["data"]["module_id"] = 2
            if status == constants.CANISTER_TRANSFER_TO_TROLLEY_DONE:
                table["data"]["module_id"] = 1
            if status == constants.CANISTER_TRANSFER_TO_CSR_DONE:
                if transfer_cycle_id:
                    table["data"]["module_id"] = 0
                    table["data"]["transfer_cycle_id"] = transfer_cycle_id

            cdb.save(table)
            return True