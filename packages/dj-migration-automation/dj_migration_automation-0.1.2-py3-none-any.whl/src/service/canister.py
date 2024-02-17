import json
import os
import sys
from collections import defaultdict, OrderedDict
from copy import deepcopy
from typing import Dict, Any

import datetime

import openpyxl
from peewee import InternalError, IntegrityError, DataError, DoesNotExist
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args, log_args_and_response, get_current_date_time, validate_rfid_checksum, \
    get_current_modified_datetime, get_current_date, get_canister_volume, \
    get_max_possible_drug_quantities_in_canister, call_webservice, last_day_of_month
from dosepack.validation.validate import validate
from src.dao.drug_inventory_dao import get_drug_info_based_on_ndc_dao, drug_inventory_adjustment
from src.exc_thread import ExcThread
from src.label_printing.canister_label import canister_dir, generate_canister_label
from src.label_printing.generate_label import remove_files
from src.cloud_storage import blob_exists, canister_label_dir, create_blob
from src.dao.alternate_drug_dao import get_canister_by_id_dao, update_alternate_drug_canister_for_batch_data
from src.dao.analysis_dao import get_replenish_drugs_dao
from src.dao.batch_dao import get_progress_batch_id
from src.dao.drug_canister_stick_dao import add_canister_stick_mapping
from src.dao.drug_dao import get_unique_drugs_by_formatted_ndc_txr, db_get_by_id, db_get_canisters_v2, \
    db_get_drug_from_unique_drug_dao, db_create_new_fill_drug_dao, db_get_unique_drug_lower_level_by_drug, \
    db_get_unique_drug_by_drug_id, db_get_drug_txr_fndc_id_dao, db_create_unique_drug_dao, \
    db_get_custom_drug_shape_name, db_get_drug_dimension_id_by_unique_drug, db_get_expired_drug_history, \
    get_same_or_alternate_canister_by_pack
from src.dao.generate_canister_dao import get_canister_info_by_canister_id
from src.dao.inventory_dao import get_drug_image_and_id_from_ndc_dao
from src.dao.location_dao import db_get_empty_locations_dao, get_location_number_from_display_location_dao, \
    get_all_location_info, get_disabled_location_info_by_canister_ids, get_disabled_location_info_by_display_location, \
    get_quad_wise_location_info, get_empty_locations_by_device
from src.dao.mfd_dao import get_drug_status_by_drug_id
from src.dao.pack_analysis_dao import get_canister_drug_quantity_required_in_batch, \
    update_status_in_pack_analysis_details, update_batch_change_tracker_after_replenish_skipped_canister
from src.dao.pack_dao import get_filling_pending_pack_ids, get_drug_wise_pack_count, \
    db_get_progress_filling_left_pack_ids
from src.dao.zone_dao import db_canister_zone_mapping_insert_bulk_data_dao, db_create_canister_zone_mapping_dao
from src.exceptions import APIFailureException, InventoryBadRequestException, InventoryDataNotFoundException, \
    InventoryBadStatusCode, InventoryConnectionException, InvalidResponseFromInventory, \
    CanisterQuantityAdjustmentException, PharmacySoftwareCommunicationException, PharmacySoftwareResponseException, \
    CanisterStickException, DBUpdateFailedException
from realtime_db.dp_realtimedb_interface import Database
from src import constants
from src.dao.canister_dao import update_replenish_based_on_system, update_canister_movement, get_canister_info_data, \
    get_canister_data_by_serial_number_v3_dao, get_quad_drug_req_qty_for_packs, get_pack_list_by_robot, \
    db_get_canister_data_by_location_id_dao, get_skipped_replenish_query, \
    get_import_batch_id_from_system_id_or_device_id, \
    get_skipped_replenish_canister, update_replenish_based_on_device, get_drug_active_canister_dao, \
    get_canister_expiry_status, discard_canister_tracker, get_replenish_mini_batch_wise, \
    check_canister_uses_in_pack_queue, insert_records_in_reserved_canister, get_canister_history_dao, \
    db_validate_testing_status, db_create_change_ndc_history_dao, get_canister_data_by_canister_ids, \
    db_create_canister_orders, get_canister_order_history_dao, remove_pack_canister_from_replenish_skipped_canister, \
    get_data_for_order_canister, db_update_canister_quantity, db_update_canister_tracker
from src.migrations.migration_to_add_expiry_date_in_canister_master import add_expiry_date_column_in_canister_master
from src.service.canister_recommendation import revert_canister_usage_by_recom
from src.service.drug_inventory import inventory_adjust_quantity
from src.service.inventory import insert_drug_bottle_pill_drop_data
from src.service.volumetric_analysis import update_drug_dimension, add_drug_dimension, get_canister_stick_details
from src.dao.pack_dao import db_get_current_location_details_by_canisters
from src.dao.device_manager_dao import get_device_type_from_device_dao, get_device_id_from_serial_number, \
    get_system_id_by_device_id_dao
from utils.drug_inventory_webservices import get_current_inventory_data
from utils.inventory_webservices import inventory_api_call
from src.dao.guided_replenish_dao import get_reserved_canister_list_for_ongoing_batch, get_guided_reserved_location
from src.dao.canister_dao import get_canister_info_by_drawer_id, get_canister_history_latest_record_can_id_dao, \
    update_canister_history_by_id_dao, create_canister_history_record, update_canister_dao, \
    db_canister_master_remove_dao, db_is_canister_present, \
    db_update_canister_master_history_zone_mapping, get_canister_details_by_id_dao, db_canister_tracker_insert_data, \
    db_get_reserved_canister_data, db_get_canisters_by_rfid_list, get_canister_by_rfid, \
    db_get_canister_by_canister_code, db_get_canister_remove_list, db_get_location_ids_by_device_and_location_number, \
    db_update_canister_location_shelf_dao, update_canister_by_rfid_dao, update_canister_zone_mapping_by_rfid_dao, \
    db_canister_history_create_multi_record_dao, get_canister_parameter_by_rfids, db_get_canister_details_by_rfid, \
    db_get_canister_by_location_updates_dao, db_get_canister_location_by_rfid, get_canister_details_by_device_dao, \
    get_canister_replenish_info_by_canister, get_canister_replenish_info_by_lot_number, db_add_canister_drawer_dao, \
    get_drug_data_by_company_id_dao, find_canister_location_in_csr,  \
    db_get_canister_data_by_rfid_company_dao, add_canister_status_history, db_create_canister_master_dao, \
    db_create_canister_tracker_dao, get_all_canisters_of_a_csr, get_canisters_per_drawer_dao, \
    update_canister_category_dao, db_get_available_locations_dao, db_get_robot_canister_with_locations, \
    db_get_robot_canister_with_ids, update_canister_status_by_location_dao, db_check_canister_available_dao, \
    db_create_canister_record_dao, get_canister_details_by_rfid_dao, get_canister_details, \
    get_latest_adjusted_canister_record_by_canister_id, get_recently_replenished_drug_info, db_get_last_canister_id_dao, \
    get_serial_number_from_canister_id, db_update_canister_master_label_print_time, get_canister_details_by_canister_id, \
    update_canister_testing_status, get_canister_threshold_value_by_rfids
from src.dao.canister_testing_dao import validate_canister_id_with_company_id, validate_active_canister_id, \
    get_location_id_from_display_location_dao, db_get_product_details, db_get_product_id
from src.dao.device_manager_dao import get_drawer_data, get_station_type_by_device_container_code, \
    get_location_of_canister_based_on_rfid, get_device_data_by_device_id_dao, get_location_data_by_display_location, \
    get_zone_wise_device_list, verify_device_id_dao, get_location_id_by_location_number_dao, \
    db_location_disabled_details, db_get_disabled_locations, get_system_id_based_on_device_type, \
    get_csr_drawer_data_dao, db_update_drawer_ip_by_drawer_name_dao, db_delete_canister_drawer_by_drawer_name_dao, \
    find_empty_location, db_get_device_drawers_quantity, validate_device_id_dao, \
    get_location_canister_data_by_display_location, get_zone_by_system, \
    get_device_location_category
from src.dao.mfd_canister_dao import get_mfd_canister_data_by_ids, get_canister_data_by_id
from src.dao.refill_device_dao import db_get_canister_info, get_available_quantity_in_canister
from src.dao.couch_db_dao import get_couch_db_database_name

from src.service.canister_transfers import update_canister_count_in_canister_transfer_couch_db
from src.service.guided_replenish import verify_canister_location_and_update_couch_db
from src.service.misc import get_csr_station_id_loc_by_serial_number, update_rfid_in_couchdb, get_token, \
    get_current_user
from src.service.csr import recommend_csr_location
from src.service.device_manager import update_csr_canister, mfs_rfid_callback, \
    verify_csr_canister_location_and_update_couch_db, csr_location_canister_rfid_update, \
    get_canister_location_from_display_location
from src.service.mfd_canister import get_transfer_location_from_couch_db, update_mfd_canister_history, \
    update_mfd_canister_location_with_fork, mfd_canister_found_update_status, update_mfd_canister_master, \
    update_mfd_canister_transfer_couch_db

logger = settings.logger


@log_args_and_response
def get_canister_data_by_drawer_id(drawer_id: int, company_id: int, device_id: int) -> dict:
    """
    @param drawer_id: integer
    @param device_id: integer
    @param company_id: integer
    @desc: To obtain canister data using drawer_id, company_id and device_id
    @return: dictionary
    """
    try:
        drawer_type_id_data = get_drawer_data(drawer_id)

        if drawer_type_id_data:
            drawer_type_id = drawer_type_id_data["drawer_type"]
        else:
            return error(1000, "Invalid drawer_id.")

        response = get_canister_info_by_drawer_id(drawer_type_id, drawer_id, company_id, device_id)
        return create_response(response)

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("error in get_canister_data_by_drawer_id {}".format(e))
        raise e


@log_args_and_response
@validate(required_fields=["user_id", "transfer_type", "source_canister_rfid"])
def canister_transfer(args: dict) -> str:
    """
    Method to transfer canister from one location to another
    @param args:
    """
    user_id = args.get("user_id")
    transfer_type = args.get("transfer_type")

    source_system_id = args.get("source_system_id")
    source_device_type_id = args.get("source_device_type_id")
    source_device_id = args.get("source_device_id")
    source_drawer_id = args.get("source_drawer_id")
    source_display_location = args.get("source_display_location")
    source_canister_rfid = args.get("source_canister_rfid")

    dest_system_id = args.get("dest_system_id")
    dest_device_type_id = args.get("dest_device_type_id")
    dest_device_id = args.get("dest_device_id")
    dest_quadrant = args.get("dest_quadrant")
    dest_drawer_id = args.get("dest_drawer_id")
    dest_display_location = args.get("dest_display_location")
    dest_canister_rfid = args.get("dest_canister_rfid")
    dest_fork_status = args.get("dest_fork_status", True)

    try:
        # response = dict()

        # in case of transfer canister
        if transfer_type == constants.TRANSFER_TYPE_DEVICE_TO_SHELF:
            logger.info("Transfer_type: device to shelf")
            if not source_system_id or not source_device_type_id or not source_device_id or not source_drawer_id \
                    or not source_canister_rfid:
                return error(1002, "missing source_system_id or source_device_type_id or source_device_id or "
                                   "source_drawer_id or source_canister_rfid")

            if source_canister_rfid and not source_display_location:
                try:
                    # check for drawer type first(to differentiate mfd and normal canister)
                    # then find location of that canister
                    drawer_type_id_data = get_drawer_data(drawer_id=source_drawer_id)

                    if not drawer_type_id_data:
                        return error(1000, "Invalid drawer_id.")
                    drawer_type_id = drawer_type_id_data["drawer_type"]
                    canister_location_data = get_location_of_canister_based_on_rfid(rfid=source_canister_rfid,
                                                                                    drawer_type_id=drawer_type_id)
                    source_display_location = canister_location_data.get("display_location")

                    if not source_display_location:
                        return error(1000, "No display location available for given rfid")
                except DoesNotExist:
                    return error(1022, "or canister not canister available in any device")

            # In this case, we have to only remove canister from specified source device
            response = transfer_canister_based_on_device_type(user_id=user_id, system_id=source_system_id,
                                                              device_type_id=source_device_type_id,
                                                              device_id=source_device_id,
                                                              drawer_id=source_drawer_id,
                                                              display_location=source_display_location,
                                                              canister_rfid=None, quadrant=None,
                                                              fork_status=dest_fork_status)
            logger.info("Transfer from device to shelf is done with response: " + str(response))
        elif transfer_type == constants.TRANSFER_TYPE_SHELF_TO_DEVICE:
            logger.info("Transfer_type: shelf to device")
            # In this case, directly place canister to the specified destination location
            response = transfer_canister_based_on_device_type(user_id=user_id, system_id=dest_system_id,
                                                              device_type_id=dest_device_type_id,
                                                              device_id=dest_device_id,
                                                              drawer_id=dest_drawer_id,
                                                              display_location=dest_display_location,
                                                              canister_rfid=source_canister_rfid,
                                                              quadrant=dest_quadrant,
                                                              fork_status=dest_fork_status)
            logger.info("Transfer from shelf to device is done with response: " + str(response))

        elif transfer_type == constants.TRANSFER_TYPE_DEVICE_TO_DEVICE:
            logger.info("Transfer_type: device to device")
            if source_canister_rfid and not source_display_location:
                try:
                    drawer_type_id_data = get_drawer_data(drawer_id=source_drawer_id)

                    if not drawer_type_id_data:
                        return error(1000, "Invalid drawer_id.")
                    drawer_type_id = drawer_type_id_data["drawer_type"]
                    canister_location_data = get_location_of_canister_based_on_rfid(rfid=source_canister_rfid,
                                                                                    drawer_type_id=drawer_type_id)
                    source_display_location = canister_location_data.get("display_location")
                    if not source_display_location:
                        return error(1000, "No display location available for given rfid")
                except DoesNotExist:
                    return error(1022, "or canister not canister available in any device")

            # In this case, we have to first remove canister from specified source location and transfer to dest loc.
            # 1. remove canister from source
            response = transfer_canister_based_on_device_type(user_id=user_id, system_id=source_system_id,
                                                              device_type_id=source_device_type_id,
                                                              device_id=source_device_id,
                                                              drawer_id=source_drawer_id,
                                                              display_location=source_display_location,
                                                              canister_rfid=None, quadrant=None,
                                                              fork_status=dest_fork_status)
            logger.info("Canister removed from source device with response: " + str(response))
            response = json.loads(response)
            if response and response["status"] == settings.FAILURE_RESPONSE:
                logger.info("Error while removing canister from device - " + str(response["description"]))
                raise APIFailureException(response)
            # 2. place canister to destination
            response = transfer_canister_based_on_device_type(user_id=user_id, system_id=dest_system_id,
                                                              device_type_id=dest_device_type_id,
                                                              device_id=dest_device_id,
                                                              drawer_id=dest_drawer_id,
                                                              display_location=dest_display_location,
                                                              canister_rfid=source_canister_rfid,
                                                              quadrant=dest_quadrant,
                                                              fork_status=dest_fork_status)
            logger.info("Placing canister to destination dest is done with response - " + str(response))
        elif transfer_type == constants.TRANSFER_TYPE_SWAP:
            logger.info("Transfer_type: swap")
            # In this case, we have to first remove canisters from both the locations source and destination
            # and then swap locations of canister

            logger.info("fetching display location based on rfid ")
            if source_canister_rfid and not source_display_location:
                try:
                    drawer_type_id_data = get_drawer_data(drawer_id=source_drawer_id)

                    if not drawer_type_id_data:
                        return error(1000, "Invalid drawer_id.")
                    drawer_type_id = drawer_type_id_data["drawer_type"]
                    canister_location_data = get_location_of_canister_based_on_rfid(rfid=source_canister_rfid,
                                                                                    drawer_type_id=drawer_type_id)

                    source_display_location = canister_location_data.get("display_location")
                    if not source_display_location:
                        return error(1000, "No display location available for given rfid")
                except DoesNotExist:
                    return error(1022, "or canister not canister available in any device")

            if dest_canister_rfid and not dest_display_location:
                try:
                    drawer_type_id_data = get_drawer_data(drawer_id=dest_drawer_id)

                    if not drawer_type_id_data:
                        return error(1000, "Invalid drawer_id.")
                    drawer_type_id = drawer_type_id_data["drawer_type"]
                    canister_location_data = get_location_of_canister_based_on_rfid(rfid=dest_canister_rfid,
                                                                                    drawer_type_id=drawer_type_id)
                    dest_display_location = canister_location_data.get("display_location")
                    if not source_display_location:
                        return error(1000, "No display location available for given rfid")
                except DoesNotExist:
                    return error(1022, "or canister not canister available in any device")

            with db.transaction():

                logger.info("Removing canister from source location")
                # 1. remove canister from source
                response = transfer_canister_based_on_device_type(user_id=user_id, system_id=source_system_id,
                                                                  device_type_id=source_device_type_id,
                                                                  device_id=source_device_id,
                                                                  drawer_id=source_drawer_id,
                                                                  display_location=source_display_location,
                                                                  canister_rfid=None, quadrant=None,
                                                                  fork_status=dest_fork_status)
                logger.info("Removal of canister from source is done with response - " + str(response))
                response = json.loads(response)
                if response and response["status"] == settings.FAILURE_RESPONSE:
                    logger.info("Error while removing canister from source- " + str(response["description"]))
                    raise APIFailureException(response)

                logger.info("Removing canister from destination location")
                # 2. remove canister from destination
                response = transfer_canister_based_on_device_type(user_id=user_id, system_id=dest_system_id,
                                                                  device_type_id=dest_device_type_id,
                                                                  device_id=dest_device_id,
                                                                  drawer_id=dest_drawer_id,
                                                                  display_location=dest_display_location,
                                                                  canister_rfid=None,
                                                                  quadrant=None,
                                                                  fork_status=dest_fork_status)

                logger.info("Removal of canister from destination loc is done with response - " + str(response))
                response = json.loads(response)
                if response and response["status"] == settings.FAILURE_RESPONSE:
                    logger.info("Error while removing canister from destination- " + str(response["description"]))
                    raise APIFailureException(response)

                logger.info("Place source canister to destination loc")
                # 3. place canister 1 to location of canister 2
                response = transfer_canister_based_on_device_type(user_id=user_id, system_id=dest_system_id,
                                                                  device_type_id=dest_device_type_id,
                                                                  device_id=dest_device_id,
                                                                  drawer_id=dest_drawer_id,
                                                                  display_location=dest_display_location,
                                                                  canister_rfid=source_canister_rfid,
                                                                  quadrant=dest_quadrant,
                                                                  fork_status=dest_fork_status)
                logger.info("Placing of source canister to dest loc is done with response - " + str(response))
                response = json.loads(response)
                if response and response["status"] == settings.FAILURE_RESPONSE:
                    logger.info("Error while placing canister to dest loc- " + str(response["description"]))
                    raise APIFailureException(response)

                logger.info("Placing dest can to source location")
                # 4. place canister 2 to location of canister 1
                response = transfer_canister_based_on_device_type(user_id=user_id, system_id=source_system_id,
                                                                  device_type_id=source_device_type_id,
                                                                  device_id=source_device_id,
                                                                  drawer_id=source_drawer_id,
                                                                  display_location=source_display_location,
                                                                  canister_rfid=dest_canister_rfid,
                                                                  quadrant=dest_quadrant,
                                                                  fork_status=dest_fork_status)
                logger.info("Placing of dest canister to source loc is done with response: " + str(response))
        else:
            return error(1020, "transfer_type")

        if not response:
            response = create_response(True)
        return response
    except APIFailureException as e:
        return json.dumps(eval(str(e)), indent=4)
    except DoesNotExist as e:
        logger.error("error in canister_transfer {}".format(e))
        return error(1004, "DoesNotExist Exception - " + str(e))
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in canister_transfer {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("error in canister_transfer {}".format(e))
        return error(1000, "Error occurred while transferring canister - " + str(e))


@log_args_and_response
def transfer_canister_based_on_device_type(user_id: int, system_id: int, device_type_id: int, device_id: int,
                                           drawer_id: [int, None], display_location: [str, None], quadrant: [int, None],
                                           canister_rfid: [str, None], fork_status: bool = True) -> str:
    """
    Method to transfer canister based on device type
    @param fork_status:
    @param quadrant:
    @param drawer_id:
    @param user_id:
    @param system_id:
    @param device_type_id:
    @param device_id:
    @param display_location:
    @param canister_rfid:
    @return:
    """
    # if source is robot(type-2) then call update canister,
    # for type 1(csr) and 3(mfd) call callback api else no need to call api
    response = dict()
    if not canister_rfid:
        logger.info("To remove canister from device")
        canister_rfid = constants.NULL_RFID_CSR
        robot_canister_rfid = None
    else:
        logger.info("To place canister in device")
        canister_rfid = canister_rfid
        robot_canister_rfid = canister_rfid
    try:
        if device_type_id == settings.DEVICE_TYPES["ROBOT"]:
            # removing/placing canister from/to robot
            logger.info("removing/placing canister from/to robot")

            logger.info("Find an empty location in given quadrant of the robot")
            # todo- first canister type is mfd or normal and based on that find empty location in that quadrant

            dict_canister_info = {"rfid_locations": {str(display_location): robot_canister_rfid},
                                  "device_id": device_id, "system_id": system_id, "user_id": user_id,
                                  "fork_locations": {str(display_location): int(bool(fork_status))}}
            logger.info("args for update_canisters_by_rfid: " + str(dict_canister_info))
            response = update_canisters_by_rfid(dict_canister_info)
            logger.info("response of update_canisters_by_rfid: " + str(response))

        elif device_type_id == settings.DEVICE_TYPES["CSR"]:
            # removing/placing canister from/to csr
            logger.info("removing/placing canister from/to csr")

            logger.info("fetching container serial number based on drawer_id")
            drawer_data = get_drawer_data(drawer_id=drawer_id)
            if not drawer_data:
                return error(9065)
            drawer_serial_number = drawer_data.get("serial_number")
            if not drawer_serial_number:
                return error(9001, "for given drawer_id")

            code = drawer_serial_number[:3]

            try:
                station_type = get_station_type_by_device_container_code(code=code)
            except (IntegrityError, InternalError, DataError) as e:
                raise e
            except DoesNotExist:
                logger.info("No station type available based on device/container code")
                raise DoesNotExist("station type not available in database")

            station_id, location_number = get_csr_station_id_loc_by_serial_number(serial_number=drawer_serial_number,
                                                                                  display_location=display_location)
            csr_args = {"station_type": station_type, "station_id": station_id,
                        "eeprom_dict": {str(location_number): canister_rfid}}

            logger.info("args for update_csr_canister - " + str(csr_args))
            response = update_csr_canister(csr_args)
            logger.info("response of update_csr_canister - " + str(response))

        elif device_type_id == settings.DEVICE_TYPES["Manual Filling Device"]:
            # removing/placing canister from/to mfd
            logger.info("Removing/placing canister from/to mfd")

            logger.info("fetching device serial number based on device_id")
            # drawer_data = get_drawer_data(drawer_id=drawer_id)

            device_data = get_device_data_by_device_id_dao(device_id=device_id)
            if not device_data:
                return error(1000, "Invalid device_id")
            device_serial_number = device_data.serial_number
            # if not device_data:
            #     return error(9065)
            # drawer_serial_number = device_data.get("serial_number")
            if not device_serial_number:
                return error(9001, "for given device_id")

            try:
                station_type = get_station_type_by_device_container_code(code=device_serial_number[:3])
            except (IntegrityError, InternalError, DataError) as e:
                raise e
            except DoesNotExist:
                logger.info("No station type available based on device/container code")
                raise DoesNotExist("station type not available in database")

            station_id = int(device_serial_number[3:].lstrip("0"))

            try:
                location_data = get_location_data_by_display_location(device_id=device_id,
                                                                      display_location=display_location)
            except (IntegrityError, InternalError, DataError) as e:
                raise e
            except DoesNotExist:
                logger.info("No station type available based on device/container code")
                raise DoesNotExist("No location_data for given device_id and display_location")
            if not location_data:
                return error(1000, "Invalid display_location")
            location_number = int(location_data.location_number) - 1
            mfd_args = {"station_type": station_type, "station_id": station_id, "eeprom_dict": {
                str(location_number): canister_rfid}}
            logger.info("args for mfs_rfid_callback: " + str(mfd_args))
            response = mfs_rfid_callback(mfd_args)
            logger.info("response for mfs_rfid_callback: " + str(response))
        else:
            # No changes in db in case of device types other than robot, csr, mfd
            logger.info("No db changes required in case of dumb device")
            response = json.dumps(response)
            pass

        return response
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in transfer_canister_based_on_device_type {}".format(e))
        raise e
    except DoesNotExist as e:
        logger.error("error in transfer_canister_based_on_device_type {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in transfer_canister_based_on_device_type {}".format(e))
        raise e


@log_args_and_response
@validate(required_fields=["user_id", "company_id", "canister_id", "canister_type", "system_id"])
def update_canister_type(args: dict) -> str:
    """
    Function to update canister type in canister master table
    @param args:
    @return:
    """
    company_id = args["company_id"]
    system_id = args["system_id"]
    user_id = args["user_id"]
    canister_id = args["canister_id"]
    canister_type = args["canister_type"]

    try:
        # validate canister type
        if canister_type not in list(settings.CANISTER_TYPE.values()):
            return error(3018)

        # validate canister_id against company_id
        if not validate_canister_id_with_company_id(canister_id=canister_id, company_id=company_id):
            return error(3016)

        # verify if active canister_id.
        if not validate_active_canister_id(canister_id=canister_id):
            return error(3012)

        # check if canister is reserved
        reserved_canister = get_reserved_canister_list_for_ongoing_batch(canister_list=[canister_id])
        if canister_id in reserved_canister:
            return error(3019)

        update_dict = {"canister_type": canister_type,
                       "modified_date": get_current_date_time(),
                       "modified_by": user_id}

        # update canister type in canister master table
        update_type = update_canister_dao(update_dict=update_dict,
                                          id=canister_id)
        logger.info("update_canister_type update status {}".format(update_type))

        # get canister product_id from canister_id
        product_id = db_get_canister_info(canister_id=canister_id, company_id=company_id)["product_id"]

        # update canister details in the ODOO Inventory
        data_dict = {"canister_product_id": product_id,
                     "canister_id": canister_id,
                     "new_type": canister_type,
                     "is_activated": False,
                     "is_drug_ndc_txr_change": False,
                     "is_canister_type_change": True,
                     "customer_id": company_id}

        odoo_response = inventory_api_call(api_name=settings.UPDATE_CANISTER_DATA_IN_INVENTORY, data=data_dict)
        logger.info(odoo_response)

        # get recommended CSR location
        csr_device_ids = get_zone_wise_device_list(company_id, [settings.DEVICE_TYPES['CSR']], system_id)
        csr_device = int(csr_device_ids[0])
        input_args = {'device_id': csr_device,
                      'company_id': company_id,
                      'canister_id': canister_id}

        response = recommend_csr_location(input_args)
        loaded_response = json.loads(response)
        if loaded_response['status'] != settings.SUCCESS_RESPONSE:
            no_location_dict = {
                                "display_location": None,
                                "location_id": None,
                                "container_id": None,
                                "drawer_name": None,
                                "ip_address": None,
                                "secondary_ip_address": None,
                                "shelf": None,
                                "serial_number": None,
                                "device_name": None,
                                "canister_id": None
                            }
            return create_response(no_location_dict)

        return response

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in update_canister_type {}".format(e))
        raise

    # Handle the Inventory Webservice Call Exceptions to send appropriate message to FrontEnd
    except InventoryBadRequestException as e:
        return error(4001, "- Error: {}.".format(e))

    except InventoryDataNotFoundException as e:
        return error(4002, "- Error: {}.".format(e))

    except InventoryBadStatusCode as e:
        return error(4004, "- Error: {}.".format(e))

    except InventoryConnectionException as e:
        return error(4003, "- Error: {}.".format(e))

    except InvalidResponseFromInventory as e:
        return error(4005, "- Error: {}.".format(e))

    except Exception as e:
        logger.error("Error in update_canister_type {}".format(e))
        return error(1020)


@log_args
@validate(required_fields=["user_id", "company_id", "canisters_to_transfer", "system_id", "device_id",
                           "current_device_id"])
def canister_transferred_manually(args: dict) -> str:
    """
    Function to skip canister to transfer to robot or CSR
    @param args:
    @return:
    """
    try:
        # batch_id = args['batch_id']
        company_id = args['company_id']
        system_id = args['system_id']
        canisters_to_transfer = args['canisters_to_transfer']
        device_id = args['device_id']
        user_id = args['user_id']
        current_device_id = args["current_device_id"]
        canister_transfer = args.get('canister_transfer', False)
        guided_transfer = args.get('guided_transfer', False)
        mfd_canister = args.get('mfd_canister', False)
        scanned_drawer_id = args.get('scanned_drawer_id', None)
        trolley_serial_number = args.get('scanned_trolley', None)

        rfid_locations_dict = dict()
        existing_canisters_data = dict()
        # existing_mfd_canisters_data = dict()
        mfd_canister_transfer_manual_list = list()
        if trolley_serial_number:
            trolley_id = get_device_id_from_serial_number(trolley_serial_number, company_id)
            logger.info("trolley_id {}".format(trolley_id))

        if not (canister_transfer or guided_transfer or mfd_canister):
            return error(1002, "Either of canister_transfer, guided_transfer or mfd_canister must be true")

        if mfd_canister:
            existing_mfd_canisters_data = get_mfd_canister_data_by_ids(canisters_to_transfer)
            for existing_mfd_canister in existing_mfd_canisters_data:
                if existing_mfd_canister['display_location'] and existing_mfd_canister['device_type_id'] == settings.DEVICE_TYPES['ROBOT']:
                    rfid_locations_dict[existing_mfd_canister['display_location']] = None
                else:
                    mfd_canister_transfer_manual_list.append(existing_mfd_canister['mfd_canister_id'])

        else:
            existing_canisters_data = db_get_current_location_details_by_canisters(
                canister_ids=canisters_to_transfer)

        if mfd_canister and mfd_canister_transfer_manual_list:
            database_name = get_couch_db_database_name(system_id=system_id)
            cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
            cdb.connect()
            id = '{}_{}'.format(constants.MFD_TRANSFER_COUCH_DB, device_id)
            transfer_doc = cdb.get(_id=id)

            company_database_name = get_couch_db_database_name(company_id=company_id)
            cdb_company = Database(settings.CONST_COUCHDB_SERVER_URL, company_database_name)
            cdb_company.connect()
            transfer_wizard_id = '{}-{}'.format(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME, device_id)
            transfer_wizard_doc = cdb_company.get(_id=transfer_wizard_id)
            exclude_location = list()
            mfd_canister_master_dict = dict()
            canister_history_update_list = list()
            mfd_canister_activate_dict = defaultdict(list)
            couch_db_device_to_update = set()

            for mfd_canister_id in mfd_canister_transfer_manual_list:
                canister_data = get_canister_data_by_id(mfd_canister_id)
                trolley_id = canister_data['home_cart_id']
                mfd_canister_state_status = canister_data['state_status']
                if mfd_canister_state_status == constants.MFD_CANISTER_MISPLACED:
                    mfd_canister_activate_dict[trolley_id].append(mfd_canister_id)
                transfer_location_id, scanned_drawer = get_transfer_location_from_couch_db(
                    trolley_id=trolley_id, canister_data=canister_data, exclude_location=exclude_location,
                    transfer_doc_cdb=transfer_doc, transfer_wizard_cdb=transfer_wizard_doc,
                    ext_scanned_drawer=scanned_drawer_id, ext_trolley_id=trolley_id, manual_update=True
                )
                exclude_location.append(transfer_location_id)
                mfd_canister_master_dict[mfd_canister_id] = {'location_id': transfer_location_id,
                                                             'fork_detection': 0}

                history_dict = {
                    'mfd_canister_id': mfd_canister_id,
                    'current_location_id': transfer_location_id,
                    'user_id': user_id,
                    'is_transaction_manual': True
                }
                canister_history_update_list.append(history_dict)
                if canister_data['dest_device_id'] and \
                        canister_data['dest_device_id'] not in couch_db_device_to_update:
                    couch_db_device_to_update.add(canister_data['dest_device_id'])

                # updating mfd canister location
            if mfd_canister_master_dict:
                logger.info('mfd_canister_master_dict: {}'.format(mfd_canister_master_dict))
                mfd_canister_location_update = update_mfd_canister_location_with_fork(mfd_canister_master_dict)
                logger.info('In canister_transferred_manually: mfd_canister_location_update: {}'.format(mfd_canister_location_update))

                # updating mfd canister history
            if canister_history_update_list:
                mfd_canister_history_update = update_mfd_canister_history(canister_history_update_list)
                logger.info('In canister_transferred_manually: mfd_canister_history_update: {}'.format(mfd_canister_history_update))

                # activating misplaced canister
            if mfd_canister_activate_dict:
                update_status = mfd_canister_found_update_status(mfd_canister_activate_dict, user_id)
                logger.info('In canister_transferred_manually: update_status: {}'.format(update_status))

        if not device_id:
            # handle transfer canister from on shelf case here
            # normal canister transfer flow
            if canister_transfer:
                for canister_id in canisters_to_transfer:
                    update_canister_count_in_canister_transfer_couch_db(system_id=system_id,
                                                                        canister_id=canister_id,
                                                                        user_id=user_id,
                                                                        status_to_update=constants.CANISTER_TX_TO_TROLLEY_TRANSFERRED_MANUALLY,
                                                                        )

            elif guided_transfer:
                for canister_id in canisters_to_transfer:
                    # update location id in canister master
                    canister_info = {canister_id: {"canister_removed": True}}
                    couch_db_update_status, new_loc_id = verify_csr_canister_location_and_update_couch_db(canister_info=canister_info,
                                                                     system_id=system_id,
                                                                     device_id=current_device_id,
                                                                     user_id=user_id,
                                                                     manual_transfer=True)

                    # add record in canister history if we get empty location in scanned drawer
                    if new_loc_id:
                        latest_canister_history_record = get_canister_history_latest_record_can_id_dao(canister_id=canister_id)
                        if latest_canister_history_record is not None:
                            # record available in canister history
                            if latest_canister_history_record.current_location_id is None \
                                    and latest_canister_history_record.previous_location_id is not None:
                                # update current location id in the latest record
                                update_history_dict = {"current_location_id": new_loc_id,
                                                       "modified_by": user_id,
                                                       "modified_date": get_current_date_time()
                                                       }
                                can_history_update_status = update_canister_history_by_id_dao(update_history_dict,
                                                                                              latest_canister_history_record.id)
                                logger.info('In canister_transferred_manually: can_history_update_status: {}'
                                            .format(can_history_update_status))


            return create_response(True)

        # fetch device_type based on id to differentiate between cart or robot or csr to suggest destination drawers
        device_data = get_device_data_by_device_id_dao(device_id=device_id)
        if not device_data:
            return error(1020, "device_id")
        device_type_id = device_data.device_type_id_id
        logger.info("device_type_id: " + str(device_type_id))

        if device_type_id == settings.DEVICE_TYPES["ROBOT"]:
            if canister_transfer:
                for canister in canisters_to_transfer:
                    rfid_locations_dict[existing_canisters_data[canister]['display_location']] = None

                if not rfid_locations_dict:
                    return error(1020)

                update_canister_ = {"device_id": device_id,
                                    "system_id": system_id,
                                    "rfid_locations": rfid_locations_dict,
                                    "user_id": user_id,
                                    "company_id": company_id,
                                    "is_removed_manually": True,
                                    "status_to_update": constants.CANISTER_TX_TO_TROLLEY_TRANSFERRED_MANUALLY}

                response = update_canisters_by_rfid(update_canister_)
                logger.info(
                    "update_canisters_by_rfid canister_transfer_remove response {}".format(json.loads(response)))

            elif guided_transfer:
                for canister in canisters_to_transfer:
                    rfid_locations_dict[existing_canisters_data[canister]['display_location']] = None

                canister_location_dict = get_canister_location_from_display_location(
                    rfid_locations_dict, device_id)
                guided_update_status = verify_canister_location_and_update_couch_db(canister_location_dict, system_id,
                                                                                    device_id, user_id)
                logger.info("Guided status update when transferred manually {}".format(guided_update_status))

            elif mfd_canister:
                if rfid_locations_dict:
                    update_canister_ = {"device_id": device_id,
                                        "system_id": system_id,
                                        "rfid_locations": rfid_locations_dict,
                                        "user_id": user_id,
                                        "company_id": company_id,
                                        "is_removed_manually": True}

                    response = update_canisters_by_rfid(update_canister_)
                    return response

        elif device_type_id == settings.DEVICE_TYPES["CSR"]:

            if not guided_transfer:
                # update location in canister master
                for canister in canisters_to_transfer:
                    canister_location_update_status = csr_location_canister_rfid_update(
                        rfid_location_dict={constants.NULL_RFID_CSR: existing_canisters_data[canister]['location_id']},
                        user_id=user_id,
                        device_id=device_id,
                        system_id=system_id,
                        status_to_update=constants.CANISTER_TX_TO_TROLLEY_TRANSFERRED_MANUALLY)
                    logger.info(canister_location_update_status)
                    logger.info(
                        "call back api response in canister_transfer_remove: {}".format(canister_location_update_status))

            else:
                for canister in canisters_to_transfer:
                    rfid_locations_dict[existing_canisters_data[canister]['display_location']] = None

                canister_location_dict = get_canister_location_from_display_location(
                    rfid_locations_dict, device_id)
                guided_update_status = verify_canister_location_and_update_couch_db(canister_location_dict, system_id,
                                                                                    device_id, user_id)
                logger.info("Guided status update when transferred manually {}".format(guided_update_status))

        elif device_type_id in [settings.DEVICE_TYPES['Manual Canister Cart'],
                                settings.DEVICE_TYPES['Canister Transfer Cart'],
                                settings.DEVICE_TYPES['Canister Cart w/ Elevator']]:
            if canister_transfer:
                for canister_id in canisters_to_transfer:
                    update_canister_count_in_canister_transfer_couch_db(system_id=system_id,
                                                                        canister_id=canister_id,
                                                                        status_to_update=constants.CANISTER_TX_TO_TROLLEY_TRANSFERRED_MANUALLY,
                                                                        user_id=user_id)
            elif guided_transfer:
                for canister_id in canisters_to_transfer:
                    canister_info = {canister_id: {"canister_removed": True}}
                    couch_db_update_status, new_loc_id = verify_csr_canister_location_and_update_couch_db(canister_info=canister_info,
                                                                     system_id=system_id,
                                                                     device_id=current_device_id,
                                                                     user_id=user_id,
                                                                     manual_transfer=True)
                    if new_loc_id:
                        latest_canister_history_record = get_canister_history_latest_record_can_id_dao(
                            canister_id=canister_id)
                        if latest_canister_history_record is not None:
                            # record available in canister history
                            if latest_canister_history_record.current_location_id is not None:
                                # insert new history record
                                canister_history_dict = {
                                    "canister_id": canister_id,
                                    "current_location_id": new_loc_id,
                                    "previous_location_id": latest_canister_history_record.current_location_id,
                                    "created_by": user_id,
                                    "modified_by": user_id,
                                    "modified_date": get_current_date_time()
                                }
                                create_canister_history_record(data=canister_history_dict, get_or_create=False)
            elif mfd_canister:
                # todo - handle mfd flow on shelf to cart tx here
                pass
        else:
            return error(1033)

        return create_response(True)

    except ValueError as e:
        logger.error("Error in canister_transferred_manually {}".format(e))
        raise ValueError
    except Exception as e:
        logger.error("Error in canister_transferred_manually {}".format(e))
        return error(1000, "Error in canister_transferred_manually")


@log_args_and_response
@validate(required_fields=['batch_id', 'system_id', "pack_orders"])
def get_replenish_drugs(replenish_info):
    """
    Returns canisters list which needs replenish with replenish order
    :param replenish_info: dict
    :return: json
    """
    batch_id = replenish_info['batch_id']
    system_id = replenish_info['system_id']
    pack_orders = replenish_info['pack_orders']
    device_id = replenish_info.get('device_id', None)
    return_data = replenish_info.get('return_data', 0)
    logger.info('pack_order for replenish drug: {}'.format(pack_orders))
    try:
        # response_list = get_replenish_drugs_dao(batch_id, system_id, pack_orders, device_id)
        #
        # response = create_response(response_list)
        #
        # if return_data:
        #     return create_response(response)
        # else:  # If no data required for response, just return status
        return create_response(True)
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_replenish_drugs {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=["fndc", "txr", "rfid", "company_id"])
def adhoc_register_canister(dict_canister_info):
    """
    Function to register canister initially
    @param dict_canister_info:
    @return:
    """
    rfid = dict_canister_info["rfid"]
    fndc = dict_canister_info["fndc"]
    txr = dict_canister_info["txr"]
    big_stick = dict_canister_info["big_stick"]
    small_stick = dict_canister_info["small_stick"]
    company_id = dict_canister_info["company_id"]

    try:
        drug_data = get_unique_drugs_by_formatted_ndc_txr(fndc, txr)
        logger.info(drug_data)
        if len(drug_data) == 0:
            return error(1001, "Error in fetching drug_id, incorrect fndc txr.")

    except Exception as e:
        logger.info(e)
        return error(1001, "Error in fetching drug_id, incorrect fndc txr.")

    try:
        data_dict = {'rfid': rfid, 'fndc': fndc, 'txr': txr, 'big_stick': big_stick, 'small_stick': small_stick,
                     'customer_id': company_id}
        status, canister_data = get_external_canister_data(data_dict)
        logger.info("get_external_canister_data response {}".format(canister_data))
        if not status or not 'product_id' in canister_data:
            return canister_data

    except Exception as e:
        logger.info(e)
        return error(1001, "Error in fetching data for product id.")

    drug_id = drug_data[0]['drug_id']
    res = add_canister({'drug_id': drug_id,
                        'device_id': None,
                        'rfid': rfid,
                        'available_quantity': 0,
                        'location_number': None,
                        'user_id': 1,
                        'reorder_quantity': 5,
                        'barcode': 'dummy',
                        'canister_type': 'REGULAR',
                        'company_id': company_id,
                        'lot_number': None,
                        'expiration_date': None,
                        'product_id': canister_data['product_id'],
                        'drug_data': canister_data['drug_data'],
                        'skip_product_id': True,
                        'big_stick': big_stick,
                        'small_stick': small_stick
                        })
    response_data = json.loads(res)
    logger.info(response_data)

    if 'data' not in response_data:
        return res
    data_dict = {"canister_id": response_data['data']['canister_id'],
                 "customer_id": company_id,
                 "product_id": canister_data['product_id'],
                 "strength_value": drug_data[0]['strength_value'],
                 "strength": drug_data[0]['strength'],
                 "drug_name": drug_data[0]['drug_name'],
                 "big_stick": big_stick,
                 "small_stick": small_stick}

    try:
        # status, odoo_response = add_drug_canister_info_in_odoo(data_dict)
        odoo_response = inventory_api_call(api_name=settings.CREATE_CANISTER_PACKAGES, data=data_dict)
        logger.info(odoo_response)

    except InventoryBadRequestException as e:
        return error(4001, "- Error: {}.".format(e))

    except InventoryDataNotFoundException as e:
        return error(4002, "- Error: {}.".format(e))

    except InventoryBadStatusCode as e:
        return error(4004, "- Error: {}.".format(e))

    except InventoryConnectionException as e:
        return error(4003, "- Error: {}.".format(e))

    except InvalidResponseFromInventory as e:
        return error(4005, "- Error: {}.".format(e))

    if type(response_data) == dict and "data" in response_data:
        if 'label_name' in response_data["data"]:
            response = {"label_name": response_data["data"]['label_name']}
        else:
            return error(1001, "Error in generating label.")
    else:
        response = response_data

    return create_response(response)


@log_args_and_response
@validate(required_fields=["drug_id", "company_id", "system_id"])
def _add_canister_info(dict_canister_info: dict):
    """
    Function to add canister and post canister data in odoo
    @param dict_canister_info: dict
    @return:
    """
    try:
        auto_register = dict_canister_info.get("auto_register", None)
        with db.transaction():
            # get drug info from given ndc_txr
            drug_data = db_get_by_id(dict_canister_info['drug_id'], dicts=True)
            logger.info("drug data in _add_canister_info {}".format(drug_data))
            if not auto_register:
                untested = db_validate_testing_status(dict_canister_info.get('rfid', None))
                untested = False
                if untested:
                    return error(21008)

            if not len(drug_data):
                return error(1001, "Error in fetching drug data, invalid drug_id.")

            # adding dummy required filled data
            dict_canister_info["barcode"] = "dummy"

            response_data = add_canister(dict_canister_info)

            if '"status": "success"' not in response_data:
                print("Error", response_data)
                return response_data

            updated_response_data = json.loads(response_data)
            logger.info(updated_response_data)

            if "canister_id" in updated_response_data["data"] and updated_response_data["data"]["canister_id"] is not None:
                canister_id = updated_response_data["data"]["canister_id"]
            else:
                print("Error", updated_response_data)
                return updated_response_data

            data_dict = {"canister_product_id": dict_canister_info['product_id'],
                        "canister_id": canister_id,
                        "customer_id": dict_canister_info['company_id'],
                        "is_activated": True,
                        "is_drug_ndc_txr_change": False,
                        "is_canister_type_change": False}

            # create_canister_packages of oddo to create package for added canister
            odoo_response = inventory_api_call(api_name=settings.UPDATE_CANISTER_DATA_IN_INVENTORY, data=data_dict)
            # logger.info(odoo_response)
        if auto_register:
            return updated_response_data
        return response_data

    except InventoryBadRequestException as e:
        return error(4001, "- Error: {}.".format(e))

    except InventoryDataNotFoundException as e:
        return error(4002, "- Error: {}.".format(e))

    except InventoryBadStatusCode as e:
        return error(4004, "- Error: {}.".format(e))

    except InventoryConnectionException as e:
        return error(4003, "- Error: {}.".format(e))

    except InvalidResponseFromInventory as e:
        return error(4005, "- Error: {}.".format(e))

    except Exception as e:
        logger.error("error in _add_canister_info {}".format(e))
        return error(1001, e)


@log_args_and_response
@validate(required_fields=["canister_id", "company_id", "user_id"])
def remove_canister(canister_info):
    """
    Sets canister number 0 and robot id NULL for given canister id

    @param canister_info:
    :return: json
    """
    canister_id = canister_info["canister_id"]
    company_id = canister_info["company_id"]
    modified_by = canister_info["user_id"]
    modified_date = get_current_date_time()
    try:
        with db.transaction():
            status = db_canister_master_remove_dao(modified_by, modified_date, canister_id, company_id)

        return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error("error in remove_canister {}".format(e))
        return error(2001)
    except DoesNotExist as e:
        logger.error("error in remove_canister {}".format(e))
        return create_response(0)


@log_args_and_response
@validate(required_fields=["canister_id", "device_id", "user_id"])
def update_canister(dict_canister_info):
    """ Updates the canister for the given fields for the given canister id.

        Args:
            dict_canister_info (dict): The keys in dict are the canister id,
                                       robot id, system id, user_id

        Returns:
           json: success or the failure response along with the id of the canister deleted.

        Examples:
            >>> update_canister({"canister_id": 1, "device_id": 2, \
                                 "system_id": 3, "user_id": 2})
                {"status": "success", "data": 1}
    """
    canister_id = dict_canister_info.pop("canister_id")
    user_id = int(dict_canister_info.pop("user_id"))
    system_id = dict_canister_info.pop("system_id", None)
    device_id = dict_canister_info["device_id"]
    location_number = int(dict_canister_info["location_number"])
    current_date_time = get_current_date_time()
    dict_canister_info["modified_by"] = user_id
    dict_canister_info["modified_date"] = current_date_time
    canister_history = dict()
    zone_ids = list(map(lambda x: int(x), dict_canister_info["zone_id"].split(','))) if (
            "zone_id" in dict_canister_info.keys()) else None
    if dict_canister_info["rfid"]:
        try:
            if not validate_rfid_checksum(dict_canister_info["rfid"]):
                return error(1022)
        except Exception as e:
            logger.error("Error in validating RFID: {}".format(e))
            logger.error(e, exc_info=True)
            return error(1023)

    if device_id is not None:  # if robot id is present check for validations
        try:
            valid_device = verify_device_id_dao(device_id=device_id, system_id=system_id)
            if not valid_device:
                return error(1015)

            device_data = get_device_data_by_device_id_dao(device_id=device_id)

            if location_number < settings.MIN_LOCATION or \
                    location_number > device_data.max_canisters:
                # check if location_number is within the valid range [1 - max_location]
                return error(1020, "location_number")

            query_status, canister_present = db_is_canister_present(
                device_id, location_number
            )
            #  checking if canister already present for given robot
            if not query_status:
                return error(1003)
            if canister_present:
                return error(1013)
            location_id = get_location_id_by_location_number_dao(device_id=device_id, location_number=location_number)
            dict_canister_info['location_id'] = location_id
            if db_location_disabled_details(location_id=location_id):
                return error(3003)

        except (IntegrityError, InternalError) as e:
            logger.info("error in update_canister: {} ".format(e))
            return error(2001)
    else:  # if robot id is none, forcing canister number to 0
        dict_canister_info["location_id"] = None

    dict_canister_info.pop("location_number", None)
    try:  # change in canister location # create canister history record
        # canister = CanisterMaster.get(id=canister_id)
        canister = get_canister_info_by_canister_id(canister_id=canister_id)

        if dict_canister_info["location_id"] != canister.location_id:
            canister_history = {"canister_id": canister.id,
                                "current_location_id": dict_canister_info["location_id"],
                                "previous_location_id": canister.location_id,
                                "created_by": user_id,
                                "modified_by": user_id
                                }
    except DoesNotExist:
        pass
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    if "drug_id" in dict_canister_info:
        dict_canister_info["canister_code"] = get_canister_code(
            dict_canister_info["drug_id"], canister_id
        )

    try:
        with db.transaction():

            status = db_update_canister_master_history_zone_mapping(dict_canister_info=dict_canister_info,
                                                                    canister_id=canister_id,
                                                                    canister_history=canister_history,
                                                                    zone_ids=zone_ids, user_id=user_id)
    except (IntegrityError, InternalError) as e:
        logger.error("error in update_canister {}".format(e))
        return error(2001)
    except DataError as e:
        logger.error("error in update_canister {}".format(e))
        return error(1020)

    return create_response(status)


@validate(required_fields=["canister_id", "actual_quantity", "company_id", "user_id"],
          non_negative_integer_validation=["actual_quantity", "canister_id", "company_id", "user_id"])
@log_args_and_response
def adjust_canister_quantity_v3(dict_canister_info: dict) -> dict:
    """
    Updates the canister quantity for the given canister id
    @param dict_canister_info: The dict containing the canister adjustment info

    """

    # get the user_id from dict_canister_info
    user_id = int(dict_canister_info["user_id"])
    company_id = int(dict_canister_info["company_id"])
    canister_id = int(dict_canister_info["canister_id"])
    actual_quantity = int(dict_canister_info["actual_quantity"])
    qty_adjustment_list = list()
    expiry_date_list = list()
    case_id = dict_canister_info.get("case_id", None)
    try:
        # get canister details from given canister_id
        logger.info("adjust_canister_quantity_v3: Fetching canister details based on canister_id")
        try:
            canister_details = get_canister_details_by_id_dao(canister_id=canister_id, company_id=company_id)
        except DoesNotExist:
            return error(1038, "or company_id")

        # Adjusted qty is difference of actual qty and available quantity
        adjusted_qty = actual_quantity - canister_details["available_quantity"]
        logger.info("adjust_canister_quantity_v3: adjusted_qty: " + str(adjusted_qty))
        if not abs(adjusted_qty):
            logger.error("adjusted_qty is 0 i.e., actual_quantity is same as available_quantity for canister: " + str(
                canister_id))
            return error(3013)

        # Logic to get drug_id based on last replenish history
        logger.info("adjust_canister_quantity_v3: Adjusting drug quantity with past replenish data")
        recently_replenished_drug_info = get_appropriate_drug_info_for_adjusted_quantity(canister_id=canister_id,
                                                                                         adjusted_qty=adjusted_qty,
                                                                                         available_qty=canister_details[
                                                                                             "available_quantity"])
        if not recently_replenished_drug_info:
            return error(16001)

        current_date, modified_date = get_current_modified_datetime()
        case_quantity_dict = {}
        for adjustment_data in recently_replenished_drug_info:

            case_id = adjustment_data['case_id']
            case_quantity_dict[case_id] = adjustment_data["adjusted_qty"] if adjustment_data["adjusted_qty"] > 0 else adjustment_data["adjusted_qty"] * (-1)
            record = {
                "canister_id": canister_id,
                "drug_id": adjustment_data["drug_id"],
                "qty_update_type_id": constants.CANISTER_QUANTITY_UPDATE_TYPE_ADJUSTMENT,
                "original_quantity": adjustment_data["available_qty"],
                "quantity_adjusted": adjustment_data["adjusted_qty"],
                "lot_number": adjustment_data["lot_no"],
                "expiration_date": adjustment_data["expiration_date"],
                "note": dict_canister_info.get("note", None),
                "created_by": user_id,
                "created_date": current_date,
                "case_id": adjustment_data['case_id']
            }
            if canister_details["available_quantity"] == 0 and canister_details["expiry_date"] is None:
                expiry = adjustment_data["expiration_date"].split("-")
                expiry_month = int(expiry[0])
                expiry_year = int(expiry[1])
                expiry_date = last_day_of_month(datetime.date(expiry_year, expiry_month, 1))
                expiry_date_list.append(expiry_date)

            qty_adjustment_list.append(record)

        logger.info("adjust_canister_quantity_v3: updating canister qty in canister master and tracker.")
        with db.transaction():
            update_dict = {
                "available_quantity": actual_quantity,
                "modified_by": user_id,
                "modified_date": modified_date
            }
            if actual_quantity == 0:
                update_dict["expiry_date"] = None
            if expiry_date_list:
                update_dict["expiry_date"] = min(expiry_date_list)

            status = update_canister_dao(update_dict=update_dict, id=canister_id)

            # canister_tracker_status = CanisterTracker.insert_many(qty_adjustment_list).execute()
            canister_tracker_status = db_canister_tracker_insert_data(insert_dict_list=qty_adjustment_list)

        logger.info("adjust_canister_quantity_v3: updated qty in canister master and tracker with status- {} "
                     "Now checking if canister is currently reserved or not".format(canister_tracker_status))

        # if canister is currently reserved for any batch then updating replenish queue for v3 system type
        canister_data = db_get_reserved_canister_data(canister_id=dict_canister_info["canister_id"])
        logger.info('reserved_canister_data_while_replenish: ' + str(canister_data))
        if canister_data:
            logger.info("adjust_canister_quantity_v3: updating_replenish_data_while_adjust_qty")
            update_replenish_based_on_system(canister_data['system_id'])
        args = {
            "user_id": user_id,
            "ndc": canister_details['ndc'],
            "adjusted_quantity": adjusted_qty if adjusted_qty > 0 else adjusted_qty * (-1),
            "company_id": company_id,
            "case_id": case_id,
            "is_replenish": True,
            "transaction_type": settings.EPBM_DRUG_ADJUSTMENT_DECREMENT,
            "case_quantity_dict": case_quantity_dict
        }
        response = inventory_adjust_quantity(args)

        return create_response(status)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in adjust_canister_quantity_v3 {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("error in adjust_canister_quantity_v3 {}".format(e))
        return error(1000, "An error occurred while adjusting the canister quantity- " + str(e))


@log_args_and_response
@validate(required_fields=["adjusted_quantity_list", "user_id", "lot_number_list",
                           "expiration_date_list",
                           "device_list", "error_qty_list", "company_id"],
          validate_length=["adjusted_quantity_list", "lot_number_list",
                           "expiration_date_list", "error_qty_list"])
def adjust_canister_quantity_in_bulk(dict_canister_info):
    """ Updates the canister quantity for the given canister id

        Args:
            dict_canister_info (dict): The key containing the canister id, quantity to be adjusted

        Returns:
           json: success or the failure response along with the id of the canister deleted.

        Examples:
            >>> adjust_canister_quantity_in_bulk({})
                {"status": "success", "data": 1}
    """
    adjusted_quantity_list = dict_canister_info["adjusted_quantity_list"].split(',')
    lot_number_list = dict_canister_info["lot_number_list"].split(',')
    expiration_date_list = dict_canister_info["expiration_date_list"].split(',')
    qty_adjusted_list = dict_canister_info["error_qty_list"].split(',')
    replace_qty = dict_canister_info.get('replace_qty', False)
    voice_notification_uuid = dict_canister_info.get('voice_notification_uuid', None)

    if "canister_id_list" in dict_canister_info:
        canister_id_list = dict_canister_info["canister_id_list"].split(',')
        _type = 1
    else:
        rfid_list = dict_canister_info["rfid_list"].split(',')
        # canister_id_list = CanisterMaster.get_canister_ids(rfid_list)
        canister_id_list = db_get_canisters_by_rfid_list(rfid_list=rfid_list)

        _type = 2

    # get the length
    length = len(canister_id_list)
    try:
        # initialize an empty list to store output
        result_list = []
        # iterate over the list
        for i in range(0, length):
            dict_adjust_in_bulk: dict = dict()
            dict_adjust_in_bulk["canister_id"] = int(canister_id_list[i])
            dict_adjust_in_bulk["adjusted_quantity"] = int(adjusted_quantity_list[i])
            dict_adjust_in_bulk["lot_number"] = lot_number_list[i]
            dict_adjust_in_bulk["expiration_date"] = expiration_date_list[i]
            dict_adjust_in_bulk["note"] = 'default'
            dict_adjust_in_bulk["user_id"] = dict_canister_info["user_id"]
            dict_adjust_in_bulk["qty_update_type_id"] = constants.CANISTER_QUANTITY_UPDATE_TYPE_ADJUSTMENT
            dict_adjust_in_bulk["device_id"] = 1
            dict_adjust_in_bulk["qty_adjusted"] = int(qty_adjusted_list[i])
            dict_adjust_in_bulk["company_id"] = int(dict_canister_info["company_id"])
            dict_adjust_in_bulk['replace_qty'] = replace_qty
            dict_adjust_in_bulk['voice_notification_uuid'] = voice_notification_uuid
            dict_adjust_in_bulk['raise_exception'] = True
            dict_adjust_in_bulk['replenish_device'] = dict_canister_info.get('replenish_device', None)

            if dict_adjust_in_bulk["lot_number"].strip() == '':
                dict_adjust_in_bulk["lot_number"] = None
            # construct the input dict and pass it to adjust_canister_quantity function
            output = adjust_canister_quantity(dict_adjust_in_bulk)
            # append the output to the result_list
            result_list.append(json.loads(output))

    # on error or exception output the error msg in json
    except (CanisterQuantityAdjustmentException, Exception) as ex:
        logger.error("error in adjust_canister_quantity_in_bulk {}".format(ex))
        return error(2001, ex)

    return create_response(result_list)


@log_args_and_response
@validate(required_fields=['rfid_based', 'data', 'user_id', 'company_id'])
def adjust_quantity_v2(dict_canister_info):
    """ Updates the canister quantity for the given canister id

        Args:
            dict_canister_info (dict): The key containing the canister id, quantity to be adjusted

        Returns:
           json: success or the failure response along with the id of the canister deleted.

        Examples:
            >>> adjust_quantity_v2({})
                {"status": "success", "data": 1}
    """
    data = dict_canister_info["data"]
    rfid_based = dict_canister_info["rfid_based"]
    company_id = int(dict_canister_info["company_id"])
    user_id = int(dict_canister_info["user_id"])
    if not data:
        return error(1001, "Empty list of objects for adjusting canister quantity.")

    if not rfid_based:
        _type = 1
    else:
        _type = 2

    # get the current date, current time and current date time from settings
    current_date = get_current_date()
    # current_time = get_current_time()

    # get the user_id from username
    # user_id = get_user_id_from_user(dict_canister_info["username"])

    note = "default"
    with db.transaction():
        # begin transaction
        try:
            result_list = []
            for item in data:
                # construct the input dict and pass it to adjust_canister_quantity function
                if not "lot_number" in item or item['lot_number'].strip() == '':
                    item['lot_number'] = None
                output = adjust(item, _type, note, user_id, current_date, company_id)
                # append the output to the result_list
                result_list.append(output)

        # on error or exception output the error msg in json
        except CanisterQuantityAdjustmentException as ex:
            logger.error("error in adjust_quantity_v2 {}".format(ex))
            return error(2001, ex)

    return create_response(result_list)


@log_args_and_response
def get_canister(company_id, canister_id=None, rfid=None, system_id=None):
    """
    Gets canister data given canister id or rfid

    @param system_id:
    @param company_id:
    @param canister_id:
    @param rfid: RFID of canister
    @return: json
    """
    try:
        if not canister_id and not rfid:
            return error(1001, "Missing Parameter(s): canister_id or rfid.")
        canister = dict()
        if canister_id:
            canister = get_canister_by_id_dao(canister_id)
        if rfid:
            canister = get_canister_by_rfid(rfid)
            if not canister:
                canister = db_get_product_details(rfid, company_id, system_id)
        return create_response(canister)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_canister {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=["canister_code"])
def get_canister_by_canister_code(dict_canister_info):
    """
    Takes canister_code and system_id and returns canister info
    :param dict_canister_info:
    :return:
    """
    canister_code = dict_canister_info["canister_code"]
    # system_id = dict_canister_info["system_id"]
    try:
        response = db_get_canister_by_canister_code(canister_code)
        return create_response(response)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_canister_by_canister_code: {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=["rfid_locations", "device_id", "system_id", "user_id"])
def update_canisters_by_rfid(dict_canister_info):
    """
    Updates location and robot based on rfid

    @param dict_canister_info:
    :return: json
    """
    logger.info("update_canisters_by_rfid input {}".format(dict_canister_info))
    logger.info("Data to update_canisters_by_rfid using rfids for robot {} and rfid_locations{} "
                 "with fork_info {}".format(dict_canister_info["device_id"], dict_canister_info["rfid_locations"],
                                            dict_canister_info.get('fork_locations', {})))

    user_id = int(dict_canister_info["user_id"])
    system_id = int(dict_canister_info["system_id"])
    company_id = dict_canister_info.get("company_id", 3)
    # current_date_time = get_current_date_time()
    device_id = dict_canister_info["device_id"]
    status_to_update = dict_canister_info.get("status_to_update", None)
    mfd_canister_dict = dict()
    unknown_mfd_rfid = list()
    parameters = dict()

    device_type_dict = get_device_type_from_device_dao(device_id_list=[device_id])
    mfd_fork_dict = dict_canister_info.get("fork_locations", {})

    rfid_location_new, mfd_canister_locations = get_location_no_from_display_location(
        dict_canister_info["rfid_locations"], device_id, mfd_fork_dict)

    canister_location_dict = get_canister_location_from_display_location(
        dict_canister_info["rfid_locations"], device_id)

    # if the canister is of mfd_canister type
    if mfd_canister_locations:
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = '{}_{}'.format(constants.MFD_TRANSFER_COUCH_DB, device_id)
        transfer_doc = cdb.get(_id=id)

        company_database_name = get_couch_db_database_name(company_id=company_id)
        cdb_company = Database(settings.CONST_COUCHDB_SERVER_URL, company_database_name)
        cdb_company.connect()
        transfer_wizard_id = '{}-{}'.format(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME, device_id)
        transfer_wizard_doc = cdb_company.get(_id=transfer_wizard_id)

        status, mfd_canister_dict, unknown_mfd_rfid, couch_db_update_required, couch_db_device_to_update, batch_id, \
            current_module = update_mfd_canister_master(mfd_canister_locations=mfd_canister_locations, user_id=user_id,
                                                    transfer_doc=transfer_doc, transfer_wizard_doc=transfer_wizard_doc,
                                                    is_removed_manually=dict_canister_info.get('is_removed_manually',
                                                                                               False))

        logger.info(status)
        if couch_db_update_required:
            if len(couch_db_device_to_update):
                # if dest_device_id and all device_ids are same as input device (from where callback received)
                if couch_db_device_to_update.count(couch_db_device_to_update[0]) == len(couch_db_device_to_update) \
                        and couch_db_device_to_update[0] == device_id:
                    device_to_update = [device_id]
                else:
                    if device_id not in couch_db_device_to_update:
                        couch_db_device_to_update.append(device_id)
                    device_to_update = couch_db_device_to_update
            else:
                # update only device from where callback received
                device_to_update = [device_id]

            for each_device in device_to_update:
                current_batch_id = None
                current_module_id = None
                if each_device != device_id:
                    transfer_wizard_id = '{}-{}'.format(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME, each_device)
                    current_transfer_wizard_doc = cdb_company.get(_id=transfer_wizard_id)
                    if current_transfer_wizard_doc and 'data' in current_transfer_wizard_doc:
                        current_batch_id = current_transfer_wizard_doc['data'].get('batch_id', None)
                        current_module_id = current_transfer_wizard_doc['data'].get('module_id', None)
                else:
                    current_batch_id = batch_id
                    current_module_id = current_module
                couch_db_status = update_mfd_canister_transfer_couch_db(
                    device_id=each_device,
                    system_id=system_id,
                    batch_id=current_batch_id, current_module_id=current_module_id)
                logger.info("Couch db update status {}".format(couch_db_status))
        # if status:
        #     return create_response(status)
        # else:
        #     return error(1000,"Error in updating mfd_canister data.")

    zone_ids = list(map(lambda x: int(x), dict_canister_info["zone_id"].split(','))) if (
            "zone_id" in dict_canister_info.keys()) else None
    # location_rfid = dict()
    new_rfids = set(v for k, v in rfid_location_new.items() if v)
    # rfid_canisters = dict()
    # update_dict = dict()
    # remove_list = list()
    status = None
    # disabled_locations_overlap = list()
    # location_canister = dict()
    canister_history_list = list()
    # rfid_list = list()
    unknown_rfid_list = list()
    log_enabled = int(os.environ.get('CANISTER_UPDATE_LOG_ENABLE', 0))

    # valid_device = DeviceMaster.db_verify_device_id(device_id, system_id)
    valid_device = verify_device_id_dao(device_id=device_id, system_id=system_id)
    if not valid_device:
        return error(1015)

    # added validation for csr devices
    if device_type_dict[device_id] == settings.DEVICE_TYPES['CSR']:
        validate_status = validate_csr_location_for_canister(rfid_location_new)
        if not validate_status:
            return error(1001, "Incorrect category for {}.".format(rfid_location_new))

    disabled_locations = [record["location_number"] for record in
                          db_get_disabled_locations([device_id])]

    location_rfid, location_canister, rfid_canisters, canister_dict, update_dict, disabled_locations_overlap, \
        remove_list = db_get_canister_remove_list(new_rfids, device_id, log_enabled, disabled_locations, user_id,
                                              rfid_location_new)

    for item in remove_list:
        try:
            if item:
                location_id = get_location_id_by_location_number_dao(device_id=device_id, location_number=item)
            else:
                location_id = None
            canister_data = location_canister[item]
            canister_history_list.append({
                "canister_id": canister_data["canister_id"],
                "current_location_id": None,
                "previous_location_id": location_id,
                "created_by": user_id,
                "modified_by": user_id,
            })
        except KeyError as e:
            # If canister was not present where rfid was not detected, will throw KeyError
            logger.error(e, exc_info=True)
            pass  # no canister present

    try:
        if log_enabled:
            logger.info("Update Canister RFID Dict {} for robot id {}".
                         format(update_dict, device_id))
            logger.info('Overlap found for robot id {} - disabled locations {}'
                         .format(device_id, disabled_locations_overlap))

        with db.transaction():

            if remove_list:  # remove canister before updating new location
                if log_enabled:
                    logger.info("Remove Canister RFID Dict for robot id {}: {}".format(device_id, remove_list))
                # location_id_list = LocationMaster.get_location_ids(device_id, remove_list)
                location_id_list = db_get_location_ids_by_device_and_location_number(device_id=device_id,
                                                                                     location_number_list=remove_list)
                canister_update = db_update_canister_location_shelf_dao(user_id=user_id,
                                                                        location_id_list=location_id_list)

                logger.info(("canister_update {}".format(canister_update)))
                for loc_num_id in remove_list:
                    if canister_update and loc_num_id in location_canister:
                        update_canister_count_in_canister_transfer_couch_db(system_id=system_id,
                                                                            canister_id=location_canister[loc_num_id][
                                                                                'canister_id'], source_device=device_id,
                                                                            dest_device_type_id=settings.DEVICE_TYPES[
                                                                                "ROBOT"],
                                                                            user_id=user_id,
                                                                            status_to_update=status_to_update)

            for rfid in update_dict:  # update canister data based on rfid
                if rfid:
                    try:
                        if rfid_canisters[rfid]["device_id"]:
                            previous_location_id = get_location_id_by_location_number_dao(
                                device_id=rfid_canisters[rfid]["device_id"],
                                location_number=rfid_canisters[rfid]["location_number"])
                        else:
                            previous_location_id = None
                        if update_dict[rfid]["device_id"]:
                            current_location_id = get_location_id_by_location_number_dao(
                                device_id=update_dict[rfid].pop("device_id"),
                                location_number=update_dict[rfid].pop("location_number"))
                        else:
                            current_location_id = None
                        update_dict[rfid]['location_id'] = current_location_id

                        # To update current location in canister history
                        latest_record = get_canister_history_latest_record_can_id_dao(
                            rfid_canisters[rfid]["canister_id"])

                        if latest_record and \
                                current_location_id and previous_location_id is None:
                            #     update current_location_id in canister_history where
                            #     current_location_id is null but previous_location_id is not null in db: this will be
                            #     the case only when we transfer canister to robot from shelf
                            update_history_dict = {"current_location_id": current_location_id,
                                                   "modified_by": user_id,
                                                   "modified_date": get_current_date_time()
                                                   }
                            status = update_canister_history_by_id_dao(update_history_dict, latest_record.id)
                        else:
                            canister_history_list.append({
                                "canister_id": rfid_canisters[rfid]["canister_id"],
                                "previous_location_id": previous_location_id,
                                "current_location_id": current_location_id,
                                "created_by": user_id,
                                "modified_by": user_id,
                                "modified_date": get_current_date_time()
                            })

                        status = update_canister_by_rfid_dao(dict_canister_info=update_dict[rfid], rfid=rfid)

                        if zone_ids is not None:
                            # CanisterZoneMapping.update_canister_zone_mapping_by_rfid(zone_ids, user_id, rfid)
                            update_canister_zone_mapping_by_rfid_dao(zone_ids, user_id, rfid)

                    except KeyError as e:
                        logger.warning('Unknown RFID found {}'.format(e.args[0]))
                        unknown_rfid_list.append(e.args[0])
            if log_enabled:
                logger.info('Canister history list for updating locations using RFID: {}'
                             .format(canister_history_list))

            if canister_history_list:

                db_canister_history_create_multi_record_dao(canister_history_list)

        parameters = get_canister_threshold_value_by_rfids(list(update_dict.keys()))

        if status:
            update_canister_count_in_canister_transfer_couch_db(system_id, rfid_canisters[rfid]['canister_id'],
                                                                source_device=device_id,
                                                                dest_loc_id=update_dict[rfid]["location_id"],
                                                                user_id=user_id,
                                                                dest_device_type_id=settings.DEVICE_TYPES["ROBOT"],
                                                                status_to_update=status_to_update)

        guided_update_status = verify_canister_location_and_update_couch_db(canister_location_dict, system_id,
                                                                            device_id, user_id, status_to_update)
        logger.info("update_canisters_by_rfid guided_update_status {}".format(guided_update_status))

    except ValueError as e:
        logger.error("error in update_canisters_by_rfid {}".format(e))
        return error(1020)
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in update_canisters_by_rfid {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("error in update_canisters_by_rfid {}".format(e))
    mfd_canister_dict.update(canister_dict)
    response = {
        'status': status, 'unknown_rfids': unknown_rfid_list,
        'canister_parameters': parameters,
        'rfid_canister_dict': mfd_canister_dict,
        'unknown_mfd_rfids': unknown_mfd_rfid
    }
    logger.info(("update_canisters_by_rfid output {}".format(response)))
    return create_response(response)


@log_args_and_response
@validate(required_fields=["rfid", "company_id"])
def get_canister_details_by_rfid(dict_canister_info):
    """ Gets the canister info with the given rfids.

        Args:
            dict_canister_info (dict): The key containing the canister rfid

        Returns:
           json: success or the failure response along with information for the given canister rfid

        Examples:
            >>> get_canister_details_by_rfid({"rfid": 1, "company_id": 2)
                {"status": "success", "data":{} }
    """
    # get the value canister_id from input dict
    rfid = dict_canister_info["rfid"]
    company_id = dict_canister_info["company_id"]
    v2_width = int(dict_canister_info.get('v2_width', settings.SHORT_DRUG_V2_WIDTH))
    v2_min = int(dict_canister_info.get('v2_min', settings.SHORT_DRUG_V2_MIN))
    v2_include_strength = bool(int(dict_canister_info.get('v2_strength_flag', settings.SHORT_DRUG_V2_STRENGTH_FLAG)))
    if len(rfid) <= 1 and len(rfid[0]) < 1:
        return create_response([])
    try:
        status = db_get_canister_details_by_rfid(
            rfid,
            company_id,
            ai_width=v2_width,
            ai_min=v2_min,
            include_strength=v2_include_strength
        )
        return create_response(status)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("error in get_canister_details_by_rfid {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=['device_id', 'system_id'])
def get_canister_by_location_updates(filters):
    """
    Returns canister data.
    - if timestamp is provided, only this canister will be returned
    which have their location changed after given timestamp
    - otherwise all canisters' data will be provided for given robot id
    :param filters: dict {"device_id": 1, "system_id": 10, "timestamp": "2018-12-28 08:33:08 UTC+0000"}
    :return: str
    """
    # results = list()
    # removed_canisters = list()  # maintain list of canister number where canister was removed
    device_id = int(filters['device_id'])
    system_id = filters['system_id']
    timestamp = filters.get('timestamp', None)  # sample: 2018-12-28 08:33:08 UTC+0000
    v2_width = int(filters.get('v2_width', settings.SHORT_DRUG_V2_WIDTH))
    v2_min = int(filters.get('v2_min', settings.SHORT_DRUG_V2_MIN))
    v2_include_strength = bool(int(filters.get('v2_strength_flag', settings.SHORT_DRUG_V2_STRENGTH_FLAG)))
    get_current_date_time()


    try:
        results = db_get_canister_by_location_updates_dao(timestamp, device_id, v2_width, v2_min, v2_include_strength,
                                                          system_id)
        return create_response(results)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("error in get_canister_by_location_updates {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=["rfid"])
def get_canister_location_by_rfid(dict_canister_info):
    """ Gets the canister location for the given rfid

        Args:
            dict_canister_info (dict): The key containing the rfid, system_id

        Returns:
           json: success or the failure response

        Examples:
            >>> get_canister_location_by_rfid({"rfid": "rfid")
                {"status": "success", "data": 1}
    """
    # get the value canister_id from input dict
    rfid = dict_canister_info["rfid"]
    try:
        status = db_get_canister_location_by_rfid(rfid)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("error in get_canister_location_by_rfid {}".format(e))
        return error(1001)
    return create_response(status)


@log_args_and_response
def get_empty_locations(dict_robot_info):
    """ Get all the empty canister locations for the given robot

        Args:
            dict_robot_info (dict): The key containing the robot id, system_id

        Returns:
            json: success or the failure response along with the list of empty locations.

        Examples:
    """
    device_id = dict_robot_info.get("device_id", None)
    company_id = dict_robot_info.get("company_id", None)
    device_type_id: int = dict_robot_info.get("device_type_id", None)
    system_id: int = dict_robot_info.get("system_id", None)
    drawer_number: str = dict_robot_info.get("drawer_number", None)
    quadrant: int = dict_robot_info.get("quadrant", None)
    is_mfd: int = dict_robot_info.get("is_mfd", None)
    # response_dict: Dict[str, Any] = dict()
    try:

        response_dict = db_get_empty_locations_dao(company_id, is_mfd, device_id, quadrant, device_type_id, system_id,
                                                   drawer_number)
        return create_response(response_dict)

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_empty_locations {}".format(e))
        return error(3016)


@log_args_and_response
def get_canister_details_by_device_id(device_id, system_id):
    valid_device = verify_device_id_dao(device_id=device_id, system_id=system_id)
    if not valid_device:
        return error(1015)

    is_active = True

    canister_data = get_canister_details_by_device_dao(device_id=device_id, is_active=is_active, system_id=system_id)
    return create_response(canister_data)


@log_args_and_response
def get_canister_replenish_info(company_id, replenish_info):
    """
    returns replenish data
    :param company_id:
    :param replenish_info:
    :return: json
    """
    canister_id = replenish_info.get("canister_id", None)
    number_of_records = int(replenish_info.get("number_of_records", 5))
    lot_number = replenish_info.get("lot_number", None)
    # replenish_data = list()

    filling_pending_pack_ids: list = list()

    try:
        # get the robot system_id from the given company_id as of now.
        system_id = get_system_id_based_on_device_type(company_id=company_id,
                                                       device_type_id=settings.DEVICE_TYPES["ROBOT"])
        # adding packs which are in progress but yet not processed by robot.
        batch_id = get_progress_batch_id(system_id)
        if batch_id:
            filling_pending_pack_ids = get_filling_pending_pack_ids(company_id=company_id)

        if canister_id:
            replenish_data = get_canister_replenish_info_by_canister(canister_id=canister_id, company_id=company_id,
                                                                     number_of_records=number_of_records,
                                                                     filling_pending_pack_ids=filling_pending_pack_ids)
            return create_response(replenish_data)

        if lot_number:
            replenish_data = get_canister_replenish_info_by_lot_number(lot_number=lot_number, company_id=company_id,
                                                                       filling_pending_pack_ids=filling_pending_pack_ids)
            return create_response(replenish_data)
        return error(1001, "Missing Parameter(s): canister_id or lot_number.")
    except InternalError as e:
        logger.error("error in get_canister_replenish_info {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=["device_id", "drawer_id", "drawer_number", "ip_address", "user_id"])
def add_canister_drawer(canister_drawer_data):
    """
    adds information about drawer
    :param canister_drawer_data: dict
    :return: json
    """
    try:
        default_dict = {
            "ip_address": canister_drawer_data["ip_address"],
            "drawer_size": canister_drawer_data.get("drawer_size", "REGULAR"),
            "created_by": canister_drawer_data["user_id"],
            "modified_by": canister_drawer_data["user_id"]
        }
        canister_tracker_id = db_add_canister_drawer_dao(canister_drawer_data, default_dict)
        return create_response(canister_tracker_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in add_canister_drawer {}".format(e))
        return error(2001)


@log_args_and_response
def get_canister_drawers(device_id):
    """
    retrieves drawers information of a robot
    :param device_id: dict
    :return: json
    """
    canister_drawer_list = list()
    try:
        query = get_csr_drawer_data_dao(device_id=device_id)
        for record in query:
            record['drawer_number'] = record.pop('drawer_name')
            canister_drawer_list.append(record)
        return create_response(canister_drawer_list)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_canister_drawers {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=["device_id", "drawer_number", "drawer_id"])
def update_canister_drawer(canister_drawer_data):
    """
    updates drawer information of a robot
    :param canister_drawer_data: dict
    :return: json
    """
    ip_address = canister_drawer_data["ip_address"]
    drawer_size = canister_drawer_data["drawer_size"]
    try:
        status = db_update_drawer_ip_by_drawer_name_dao(canister_drawer_data=canister_drawer_data, ip_address=ip_address,
                                                        drawer_size=drawer_size)
        return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error("error in update_canister_drawer {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=["device_id", "drawer_number", "drawer_id"])
def delete_canister_drawer(canister_drawer_data):
    """
    deletes drawer of a robot
    :param canister_drawer_data: dict
    :return: json
    """
    try:
        status = db_delete_canister_drawer_by_drawer_name_dao(canister_drawer_data=canister_drawer_data)
        return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error("error in delete_canister_drawer {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=["company_id"])
def get_canister_info_v2(dict_canister_info):
    """ Get all the canisters for the given robot id and system_id

        Args:
            dict_canister_info (dict): The key containing the device_id and system_id

        Returns:
           json: success or the failure response along details of the canister for the given device_id

    """
    company_id = dict_canister_info["company_id"]
    filter_fields = dict_canister_info.get('filter_fields', None)
    sort_fields = dict_canister_info.get('sort_fields', None)
    paginate = dict_canister_info.get('paginate', None)
    records_from_date = dict_canister_info.get('records_from_date', None)
    # in change ndc flow when replenish pop up at that time same api is called nd return same canister
    replenish_canister_flag = dict_canister_info.get("replenish_canister_flag")
    canister_type_count = dict()
    filling_pending_pack_ids: list = list()
    manual_search = dict_canister_info.get('manual_search', False)

    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, ' Missing key(s) in paginate.')

    try:

        canister_list, count, non_paginate_records, ndc_list = db_get_canisters_v2(
            company_id=company_id,
            filter_fields=filter_fields,
            sort_fields=sort_fields,
            paginate=paginate, replenish_canister_flag=replenish_canister_flag
        )
        inventory_data = get_current_inventory_data(ndc_list=ndc_list,
                                                    qty_greater_than_zero=False)
        inventory_data_dict = {}
        for item in inventory_data:
            inventory_data_dict[item['ndc']] = item['quantity']
        # get the robot system_id from the given company_id as of now.
        system_id = get_system_id_based_on_device_type(company_id=company_id,
                                                       device_type_id=settings.DEVICE_TYPES["ROBOT"])

        # adding packs which are in progress but yet not processed by robot.
        batch_id = get_progress_batch_id(system_id)
        if batch_id:
            filling_pending_pack_ids = get_filling_pending_pack_ids(company_id=company_id)

        for record in canister_list:
            canister_id = int(record["canister_id"])
            record['inventory_qty'] = inventory_data_dict.get(record['ndc'], 0)
            record['is_in_stock'] = 0 if record["inventory_qty"] == 0 else 1
            record["batch_required_quantity"] = 0
            record["canister_capacity"] = None

            if not manual_search:
                # get total required drug quantity in canister for batch
                canister_required_quantity = get_canister_drug_quantity_required_in_batch(canister_id_list=[canister_id],
                                                                                          filling_pending_pack_ids=filling_pending_pack_ids)
                record["batch_required_quantity"] = canister_required_quantity.get(int(canister_id), 0)
                canister_drug_info = db_get_canister_info(canister_id=canister_id, company_id=company_id)
                unit_drug_volume = canister_drug_info["approx_volume"]
                if unit_drug_volume is not None:
                    logger.info("unit_drug_volume is not None so fetching canister_usable_volume")
                    # find canister volume
                    canister_usable_volume = get_canister_volume(canister_type=canister_drug_info["canister_type"])
                    logger.info("canister_usable_volume: {} for canister {}".format(canister_usable_volume, canister_id))

                    record["canister_capacity"] = get_max_possible_drug_quantities_in_canister(
                        canister_volume=canister_usable_volume, unit_drug_volume=unit_drug_volume)
                    logger.info("canister_capacity in canister {} : {}".format(canister_id, record["canister_capacity"]))

            # show status history and inventory history if searched for only one canister.
            if filter_fields and filter_fields.get('canister_id', None) and records_from_date:
                record['canister_inventory_history'] = get_canister_replenish_info_by_canister(canister_id=canister_id,
                                                                                               company_id=company_id,
                                                                                               records_from_date=records_from_date,
                                                                                               filling_pending_pack_ids=filling_pending_pack_ids)

                record['canister_status_history'] = get_canister_history_dao(canister_id=canister_id,
                                                                             records_from_date=records_from_date)
            else:
                record['canister_inventory_history'] = dict()
                record['canister_status_history'] = dict()

        if "canister_type" in non_paginate_records:
            canister_type_count[settings.CANISTER_TYPE["BIG"]] = non_paginate_records["canister_type"].count(
                settings.CANISTER_TYPE["BIG"])
            canister_type_count[settings.CANISTER_TYPE["SMALL"]] = non_paginate_records["canister_type"].count(
                settings.CANISTER_TYPE["SMALL"])

        return create_response({"canister_list": canister_list,
                                "number_of_records": count,
                                "canister_type_count": canister_type_count})

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_canister_info_v2 {}".format(e))
        return error(2001)


@log_args_and_response
def get_expired_drug_history(dict_canister_info):
    try:
        logger.info("In get_expired_drug_history")
        company_id = dict_canister_info["company_id"]
        filter_fields = dict_canister_info.get('filter_fields', None)
        sort_fields = dict_canister_info.get('sort_fields', None)
        paginate = dict_canister_info.get('paginate', None)

        results, count = db_get_expired_drug_history(company_id=company_id,
                                                           filter_fields=filter_fields,
                                                           sort_fields=sort_fields,
                                                           paginate=paginate)

        response_data = {"expired_drug_data": results,
                         "number_of_records": count}
        return create_response(response_data)
    except Exception as e:
        logger.info(f"Error in get_expired_drug_history, e: {e}")
        raise e


@log_args_and_response
@validate(required_fields=["company_id"])
def get_drug_data_by_company_id(canister_data_dict):
    """
    This function will be used to get data about the drugs whose canister is present for given system id/company id
    :param canister_data_dict: Canister data dict which has system id
    :return: Data for drugs
    """

    try:
        resp_dict = get_drug_data_by_company_id_dao(canister_data_dict=canister_data_dict)
        return create_response(resp_dict)

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("error in get_drug_data_by_company_id {}".format(e))
        raise e


@log_args_and_response
@validate(required_fields=["drug_ndc", "rfid_list", "user_id"])
def update_canister_drug_id_based_on_rfid(canister_drug_dict):
    """

    :param canister_drug_dict:
    :return:
    """
    drug_ndc = str(canister_drug_dict["drug_ndc"])
    rfid_list = canister_drug_dict["rfid_list"].split(',')
    user_id = int(canister_drug_dict["user_id"])

    response_dict = dict()

    try:
        drug_image, drug_id = get_drug_image_and_id_from_ndc_dao(ndc=drug_ndc)

        for rfid in rfid_list:
            try:
                if not validate_rfid_checksum(rfid):
                    response_dict[rfid] = False
            except Exception as e:
                logger.error("Error in validating RFID: {}".format(e))
                logger.error(e, exc_info=True)
                response_dict[rfid] = False

            # Get canister info by rfid
            canister_data = get_canister_by_rfid(rfid=rfid)

            if canister_data:
                # Delete canister
                # required_dict = {"canister_id": canister_data["canister_id"],
                #                  "company_id": canister_data["company_id"],
                #                  "user_id": user_id,
                #                  "drug_id": canister_data["drug_id"],
                #                  "location_number": canister_data["location_number"],
                #                  "device_id": canister_data["device_id"],
                #                  "display_location": canister_data["display_location"]
                #                  }

                # function not in use currently
                # resp = delete_canister(required_dict)

                resp_dict = json.loads(resp)

                if resp_dict["status"] == "success":
                    # Add canister
                    required_dict = {"drug_id": drug_id, "device_id": None, "system_id": canister_data["system_id"],
                                     "rfid": rfid, "available_quantity": 1,
                                     "location_number": 0, "user_id": user_id, "reorder_quantity": 10,
                                     "barcode": "dummyinventory", "canister_type": settings.SIZE_OR_TYPE["SMALL"],
                                     "company_id": canister_data["company_id"], "lot_number": None, "expiration_date": None,
                                     "zone_id": None}

                    resp = add_canister(required_dict)

                    resp_dict = json.loads(resp)

                    if resp_dict["status"]:
                        response_dict[rfid] = resp_dict["data"]["canister_id"]
                    else:
                        response_dict[rfid] = False
                else:
                    response_dict[rfid] = False
            else:
                response_dict[rfid] = False

        return create_response(response_dict)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in update_canister_drug_id_based_on_rfid {}".format(e))
        return error(2001)


@log_args_and_response
def get_empty_location_in_inventory(company_data):
    """
    Gets empty location to put canister from the inventory.
    @param company_data: company_id
    :return:
    """
    company_id = company_data['company_id']
    required_locations_count = company_data['required_locations_count']
    ndc = company_data["ndc"]
    try:
        canister_location_data = find_empty_location(company_id=company_id,
                                                     required_locations_count=required_locations_count,
                                                     ndc=ndc)

        return create_response(canister_location_data)
    except (IntegrityError, InternalError) as e:
        logger.error("error in get_empty_location_in_inventory {}".format(e))
        return error(2001)
    except DataError as e:
        logger.error("error in get_empty_location_in_inventory {}".format(e))
        return error(1020)
    except DoesNotExist as e:
        logger.error("error in get_empty_location_in_inventory {}".format(e))
        return create_response(None)
    except Exception as e:
        logger.error("error in get_empty_location_in_inventory {}".format(e))

        return error(1020)


@log_args_and_response
def get_canister_location_in_inventory(canister_data):
    """
    Gets the location of a canister which is placed in the inventory.
    @param canister_data: canister_id and company_id
    :return:
    """
    canister_id_list = canister_data['canister_id_list']
    company_id = canister_data['company_id']
    drug_id_list = canister_data['drug_id_list']
    try:
        canister_location_data = find_canister_location_in_csr(canister_id_list=canister_id_list,
                                                               company_id=company_id,
                                                               drug_id_list=drug_id_list)

        return create_response(canister_location_data)
    except (IntegrityError, InternalError) as e:
        logger.error("error in get_canister_location_in_inventory {}".format(e))
        return error(2001)
    except DataError as e:
        logger.error("error in get_canister_location_in_inventory {}".format(e))
        return error(1020)
    except DoesNotExist as e:
        logger.error("error in get_canister_location_in_inventory {}".format(e))
        return create_response(None)
    except Exception as e:
        logger.error("error in get_canister_location_in_inventory {}".format(e))
        return error(1020)


@log_args_and_response
def replace_canister(canister_data):
    try:
        with db.transaction():
            company_id = int(canister_data['company_id'])
            rfid = canister_data['rfid']
            user_id = int(canister_data['user_id'])
            drug_id = int(canister_data['drug_id'])
            device_id = canister_data['device_id']
            batch_id = canister_data['batch_id']
            zone_id = canister_data.get("zone_id", None)
            ignore_location = canister_data.get("ignore_location", False)

            if zone_id and type(zone_id) == str:
                zone_id = list(map(lambda x: int(x), canister_data["zone_id"].split(',')))

            try:
                canister_code = get_canister_code(drug_id)
            except DoesNotExist:
                return error(1017)

            try:
                existing_canister_data = db_get_canister_data_by_rfid_company_dao(rfid=rfid, company_id=company_id)
            except DoesNotExist:
                return error(1032)

            if existing_canister_data['location_id'] is not None and not ignore_location:
                return error(1031)

            # add data in canister status history for existing canister
            status_data_dict = {
                "canister_id": existing_canister_data['id'],
                "action": constants.CODE_MASTER_CANISTER_NDC_CHANGE,
                "created_by": user_id,
                "created_date": get_current_date_time()
            }
            canister_status_history_existing_id = add_canister_status_history(data_dict=status_data_dict)
            logger.info("Record added in canister status history {}".format(canister_status_history_existing_id.id))

            # update rfid null in canister master

            update_canister_by_rfid = update_canister_by_rfid_dao(dict_canister_info={"rfid": None, "active": False,
                                                                              "location_id": None, "product_id": None},
                                                                  rfid=rfid)

            logger.info("Canister master table updated {}".format(update_canister_by_rfid))

            # add data in canister master
            insert_canister_data = {
                'rfid': rfid,
                'location_id': existing_canister_data['location_id'],
                'drug_id': drug_id,
                'canister_type': existing_canister_data['canister_type'],
                'active': settings.is_canister_active,
                'barcode': existing_canister_data['barcode'],
                'created_by': user_id,
                'modified_by': user_id,
                'created_date': get_current_date_time(),
                'modified_date': get_current_date_time(),
                'available_quantity': int(canister_data['quantity']),
                'reorder_quantity': 10,
                'canister_code': canister_code,
                'company_id': company_id,
                'product_id': existing_canister_data['product_id'],
                'canister_stick_id': existing_canister_data['canister_stick_id']
            }

            record_id = db_create_canister_master_dao(insert_canister_data)

            change_ndc_history_data = {"old_drug_id": existing_canister_data['drug_id'],
                                       "old_canister_id": existing_canister_data['id'],
                                       "new_drug_id": drug_id,
                                       "new_canister_id": record_id}
            change_ndc_id = db_create_change_ndc_history_dao(change_ndc_history_data)

            #  add new canister data in zone master
            if zone_id is not None:
                insert_zone_data = []
                for zid in zone_id:
                    insert_zone_data.append({
                        'canister_id': record_id,
                        'zone_id': zid,
                        'created_date': get_current_date_time(),
                        'created_by': user_id
                    })
                db_canister_zone_mapping_insert_bulk_data_dao(insert_zone_data)

            # add data in canister status history for new added canister
            status_data_dict = {
                "canister_id": record_id,
                "action": constants.CODE_MASTER_CANISTER_NEW_FROM_OLD,
                "created_by": user_id,
                "created_date": get_current_date_time(),
                "associated_canister_id": canister_status_history_existing_id.id
            }
            canister_status_history = add_canister_status_history(data_dict=status_data_dict)
            logger.info(
                "Record for new canister added in canister status history {}".format(canister_status_history.id))

            canister_tracker_data = {
                'device_id': None,
                'drug_id': drug_id,
                'quantity_adjusted': int(canister_data['quantity']),
                'original_quantity': 0,
                "lot_number": canister_data["lot_number"],
                "expiration_date": canister_data["expiration_date"],
                "note": "default",
                'created_by': user_id,
                'created_date': get_current_date_time(),
                'canister_id': record_id,
                'qty_update_type_id': constants.CANISTER_QUANTITY_UPDATE_TYPE_REPLENISHMENT,
                "drug_scan_type_id": constants.USER_ENTERED,
                "replenish_mode_id": constants.MANUAL_CODE
            }

            canister_tracker_id = db_create_canister_tracker_dao(canister_tracker_data)
            logger.info("Data added in canister tracker: {}".format(canister_tracker_id))

            if device_id:
                update_alternate_canister = update_alternate_drug_canister_for_batch_data(batch_id,
                                                                                          existing_canister_data['id'],
                                                                                          record_id,
                                                                                          device_id,
                                                                                          user_id,
                                                                                          company_id,
                                                                                          current_pack_id=canister_data.get('current_pack_id', None))
                logger.info("replace_canister update_alternate_canister {}".format(update_alternate_canister))

            return create_response({'canister_id': record_id,
                                    'existing_canister_id': existing_canister_data['id'],
                                    'product_id': existing_canister_data['product_id']})

    except (InternalError, IntegrityError, ValueError) as e:
        logger.error("Error in replace_canister {}".format(e))
        return error(2001, e)
    except PharmacySoftwareCommunicationException as e:
        logger.error("Error in replace_canister {}".format(e))
        return error(7001)
    except PharmacySoftwareResponseException as e:
        logger.error("Error in replace_canister {}".format(e))
        return error(7001)
    except Exception as e:
        logger.error("Error in replace_canister {}".format(e))
        return error(2001, e)


@log_args_and_response
def get_csr_drawer_rfids(csr_data):
    try:
        location_number_dict = dict()
        for device_id in csr_data['csr_id_list']:
            # drawers_data = DeviceMaster.get_drawers_quantity(device_id=device_id)
            drawers_data = db_get_device_drawers_quantity(device_id=device_id)
            total_drawers = drawers_data['small_drawers']
            if total_drawers is None:
                total_drawers = drawers_data['big_drawers']

            max_canister_in_one_drawer = drawers_data['max_canisters'] // total_drawers
            for drawer in csr_data['drawer_number_list']:
                for location in csr_data['location_number_list']:
                    db_location = ((drawer - 1) * max_canister_in_one_drawer) + location
                    location_number_dict[db_location] = location
        response = get_all_canisters_of_a_csr(device_id_list=csr_data['csr_id_list'],
                                              drawer_number_list=csr_data['drawer_numbers'],
                                              location_number_dict=location_number_dict,
                                              company_id=csr_data['company_id'])

        return create_response(response)

    except (InternalError, InternalError) as e:
        logger.error("error in get_csr_drawer_rfids {}".format(e))
        return error(2001)
    except DoesNotExist as e:
        logger.error("error in get_csr_drawer_rfids {}".format(e))
        return error(9054)
    except Exception as e:
        logger.error("error in get_csr_drawer_rfids {}".format(e))
        return error(2001)


@log_args_and_response
def get_canisters_per_drawer(company_id, device_id, drawer_numbers):
    """
      Function to get canister per drawer
      @param company_id:
      @param device_id:
      @param drawer_numbers:
      @return:
    """
    try:
        valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
        if not valid_device:
            return error(1033)

        drawer_number_list = drawer_numbers.split(',')

        canister_data, mfd_canister_data_list = get_canisters_per_drawer_dao(company_id=company_id,
                                                                             device_id=device_id,
                                                                             drawer_number_list=drawer_number_list)
        return create_response({'canister_data': list(canister_data),
                                'mfd_canister_data': list(mfd_canister_data_list)})

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_canisters_per_drawer {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_canisters_per_drawer: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)
    except Exception as e:
        logger.error("error in get_canisters_per_drawer {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_canisters_per_drawer: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_canisters_per_drawer: " + str(e))


@log_args_and_response
def get_canister_data_by_serial_number(canister_serial_number, company_id, skip_testing=None, auto_register=None):
    """
    Method to fetch canister data from inventory
    @param auto_register:
    @param skip_testing:
    @param canister_serial_number: string
    @return: canister data - dict
    """
    logger.info(canister_serial_number)
    canister_data = {
        "canister_serial_number": canister_serial_number,
        "customer_id": company_id
    }
    try:
        canister_data = inventory_api_call(api_name=settings.GET_CANISTER_DATA, data=canister_data)
        if not canister_data.get('ndc##txr'):
            raise InvalidResponseFromInventory(canister_data)

        try:
            query = db_get_drug_from_unique_drug_dao(canister_data)
        except DoesNotExist as e:
            logger.error("error in get_canister_data_by_serial_number {}".format(e))
            return error(1014)

        response = {
            "drug_data": {
                "fillet": canister_data['fillet'],
                "shape": canister_data['shape'],
                "length": float(canister_data['length']),
                "width": float(canister_data['width']),
                "depth": float(canister_data['depth'])
            },
            "small_stick_length": canister_data["small_stick_length"] and float(
                canister_data["small_stick_length"]) or None,
            "big_stick_width": canister_data["big_stick_width"] and float(canister_data["big_stick_width"]) or None,
            "big_stick_serial_number": canister_data["big_stick_serial_number"],
            "big_stick_depth": canister_data["big_stick_depth"] and float(canister_data["big_stick_depth"]) or None,
            "product_id": canister_data["odoo_product_id"] and int(canister_data["odoo_product_id"]) or None,
            "rfid": canister_data["canister_rfid"],
            "ndc": query["ndc"],
            "drug_id": query["id"],
            "drug_name": query["drug_name"],
            "canister_type": canister_data.get("canister_type", settings.CANISTER_TYPE["SMALL"]),
            "drum_serial_number": canister_data.get("drum_serial_number", None),
            "drum_width": canister_data.get("drum_width", None),
            "drum_depth": canister_data.get("drum_depth", None),
            "drum_length": canister_data.get("drum_length", None)
        }
        product_id = db_get_product_id(canister_serial_number)
        if not skip_testing:
            untested = db_validate_testing_status(response['rfid'])
            if untested:
                logger.error(21008)
                if not product_id:
                    product_id = "N.A."
                response["error"] = f"Testing of scanned canister is pending for product_id:  {product_id}"
                return create_response({"canister_data": response})
            else:
                if auto_register:
                    response["auto_register"] = True
                    return response
                else:
                    return create_response({"canister_data": response})
        else:
            if auto_register:
                response["auto_register"] = True
                return response
            return create_response({"canister_data": response})

    except InventoryBadRequestException as e:
        return error(4001, "- Error: {}.".format(e))

    except InventoryDataNotFoundException as e:
        return error(4002, "- Error: {}.".format(e))

    except InventoryBadStatusCode as e:
        return error(4004, "- Error: {}.".format(e))

    except InventoryConnectionException as e:
        return error(4003, "- Error: {}.".format(e))

    except InvalidResponseFromInventory as e:
        return error(4005, "- Error: {}.".format(e))

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_canister_data_by_serial_number {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("error in get_canister_data_by_serial_number {}".format(e))
        return error(1000, "Error in get_canister_data_by_serial_number: " + str(e))


@log_args_and_response
def update_canister_category(args):
    """
    Function to update canister category (canister_type) according to csr
        location recommendation
    @param args: company_id, system_id
    @return: status: "success"
    """
    try:
        company_id = args['company_id']
        # system_id = args['system_id']
        fast_moving_big_canister_count = 400
        fast_moving_small_canister_count = 800
        medium_moving_big_canister_count = 640
        slow_moving_big_canister_count = 520
        medium_fast_moving_small_canister_count = 960
        medium_slow_moving_small_canister_count = 840
        update_canister_dict = {"canister_type": {70: list(), 71: list()},
                                "canister_size": {72: list(), 73: list(), 74: list(), 75: list()}}

        # category_canister_dict = {settings.CANISTER_DRUG_USAGE["Fast Moving"]: list(),
        #                           settings.CANISTER_DRUG_USAGE["Medium Fast Moving"]: list(),
        #                           settings.CANISTER_DRUG_USAGE["Medium Slow Moving"]: list(),
        #                           settings.CANISTER_DRUG_USAGE["Slow Moving"]: list()
        #                           }

        # will get drug wise pack count (within given time period)
        drug_canister_pack_count_dict = get_drug_wise_pack_count(time_period=settings.TIME_PERIOD_CC,
                                                                  company_id=company_id)
        logger.info(drug_canister_pack_count_dict)

        # logic to assign category to canisters based on pack count
        for drug, pack_canister_data in drug_canister_pack_count_dict.items():

            pack_count, canister_list = pack_canister_data
            if pack_count >= settings.FAST_MOVING_PACK_COUNT \
                    and fast_moving_big_canister_count >= len(canister_list):
                update_canister_dict["canister_type"][70].extend(canister_list)
                update_canister_dict["canister_size"][72].extend(canister_list)
                fast_moving_big_canister_count -= len(canister_list)
            else:
                if fast_moving_small_canister_count >= len(canister_list):
                    update_canister_dict["canister_type"][71].extend(canister_list)
                    update_canister_dict["canister_size"][72].extend(canister_list)
                    fast_moving_small_canister_count -= len(canister_list)
                elif medium_moving_big_canister_count >= len(canister_list):
                    update_canister_dict["canister_type"][70].extend(canister_list)
                    update_canister_dict["canister_size"][73].extend(canister_list)
                    medium_moving_big_canister_count -= len(canister_list)
                elif medium_fast_moving_small_canister_count >= len(canister_list):
                    update_canister_dict["canister_type"][71].extend(canister_list)
                    update_canister_dict["canister_size"][73].extend(canister_list)
                    medium_fast_moving_small_canister_count -= len(canister_list)
                elif medium_slow_moving_small_canister_count >= len(canister_list):
                    update_canister_dict["canister_type"][71].extend(canister_list)
                    update_canister_dict["canister_size"][74].extend(canister_list)
                    medium_slow_moving_small_canister_count -= len(canister_list)
                elif slow_moving_big_canister_count >= len(canister_list):
                    update_canister_dict["canister_type"][70].extend(canister_list)
                    update_canister_dict["canister_size"][75].extend(canister_list)
                    slow_moving_big_canister_count -= len(canister_list)
                else:
                    update_canister_dict["canister_type"][71].extend(canister_list)
                    update_canister_dict["canister_size"][75].extend(canister_list)

        # update canister category in canister master table
        update_canister_master = update_canister_category_dao(update_canister_dict)

        if update_canister_master:
            return create_response("canister category data updated")

        else:
            return error(1000, "Unable to update canister category, {}.".format(update_canister_master))

    except Exception as e:
        logger.error("error in update_canister_category {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=["company_id", "system_id"])
def get_available_locations(dict_robot_info):
    """
    Function to get empty and unreserved locations.
    unreserved locations: locations where canister is placed but that canister is not required in particular batch
    @param dict_robot_info:
    @return:
    """
    try:
        response_dict = db_get_available_locations_dao(dict_robot_info=dict_robot_info)
        return create_response(response_dict)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_available_locations {}".format(e))
        return error(3016)


@log_args_and_response
@validate(required_fields=["device_id"])
def get_disabled_location_canister_transfers(dict_location_info):
    try:
        device_id = dict_location_info['device_id']
        # drawer_flag = dict_location_info.get('drawer_flag', 0)
        canister_ids = dict_location_info.get('canister_ids', [])
        display_locations = dict_location_info.get('display_locations', None)
        exclude_locations = dict_location_info.get('exclude_locations', None)
        if not display_locations and not canister_ids:
            return error(1000, "Missing argument: canister_ids and display_locations can not be null")
        # location_info = {}
        # disabled_location_ids = []
        canister_destination_location_dict = {}
        # dis_quad_drug_canister_dict_updated = OrderedDict()

        system_id = get_system_id_by_device_id_dao(device_id=device_id)

        # obtain the current batch_id for the given system
        batch_id = get_progress_batch_id(system_id=system_id)
        dis_quad_drug_canister_dict = dict()
        dis_quad_canisters = set()

        # fetch the location_ids of the display_location
        # for display_location in display_locations:
        #     loc_id, is_disabled = LocationMaster.get_location_id_from_display_location(device_id=device_id,
        #                                                              display_location=display_location)
        #     disabled_location_ids.append(loc_id)

        # fetch info for the disabled locations
        if canister_ids:
            canister_ids = canister_ids.split(",")
            dis_quad_drug_canister_dict, dis_quad_canisters = get_disabled_location_info_by_canister_ids(
                canister_ids=canister_ids, batch_id=batch_id)

        # get the canisters present in the particular device
        canister_location_info_dict, reserved_location_ids = db_get_robot_canister_with_locations(device_id=[device_id])

        if canister_ids:
            canister_location_info_dict, reserved_location_ids = db_get_robot_canister_with_ids(
                canister_ids, canister_location_info_dict, reserved_location_ids)

        if display_locations:
            display_locations = display_locations.split(",")
            dis_quad_drug_canister_dict, dis_quad_canisters = get_disabled_location_info_by_display_location(
                display_locations=display_locations, batch_id=batch_id, device_id=device_id,
                quad_drug_canister_dict=dis_quad_drug_canister_dict, quad_canisters=dis_quad_canisters)
            exclude_locs = get_location_canister_data_by_display_location(device_id, display_locations)
            for loc in exclude_locs:
                reserved_location_ids.add(loc['loc_id'])

        if exclude_locations:
            exclude_locations = exclude_locations.split(",")
            exclude_loc_info = get_location_canister_data_by_display_location(device_id, exclude_locations)
            for loc in exclude_loc_info:
                reserved_location_ids.add(loc['loc_id'])

        quad_drug_canister_dict, quad_canisters, canister_drug_info_dict = get_all_location_info(device_id)

        if canister_ids:
            quad_drug_canister_dict, quad_canisters, canister_drug_info_dict = get_canister_info_data(canister_ids, batch_id, quad_drug_canister_dict, quad_canisters, canister_drug_info_dict)

        for quad, canisters in dis_quad_canisters.items():
            for canister in canisters:
                canister_info_data = canister_location_info_dict.get('canister', None)
                canister_destination_location_dict[canister] = {
                    'fndc_txr': canister_drug_info_dict[canister]['fndc_txr'],
                    'drug_name': canister_drug_info_dict[canister]['drug_name'],
                    'drug_ndc': canister_drug_info_dict[canister]['ndc'],
                    'required_qty': 0,
                    'source_device_name': canister_info_data[5] if canister_info_data else None,
                    'source_device_id': canister_info_data[0] if canister_info_data else None,
                    'source_display_location': canister_info_data[2] if canister_info_data else None,
                    'rfid': canister_info_data[3] if canister_info_data else None,
                    'dest_quadrant': None,
                    'dest_device_name': None,
                    'dest_device_id': None, 'dest_display_location': None, 'dest_location_number': None}

        if batch_id is None:
            response_data = make_response_data(canister_destination_location_dict=canister_destination_location_dict)
            return create_response(response_data)

        # obtain the pack list id
        pack_list = get_pack_list_by_robot(batch_id, device_id)

        if len(pack_list) == 0:
            response_data = make_response_data(canister_destination_location_dict)
            return create_response(response_data)

        # obtain the empty locations and robot disabled locations for the given device id
        empty_locations, robot_disabled_locations = get_empty_locations_by_device(device_id, reserved_location_ids)

        # to obtain the locations reserved for the guided_transfer flow
        guided_reserved_locations = get_guided_reserved_location(device_id=device_id, batch_id=batch_id)
        # to remove the guided_reserved_locations from the empty locations list.
        empty_locations = set(empty_locations) - set(guided_reserved_locations)
        # empty_locations = []

        # obtain the quadrant location info for the empty locations
        empty_quad_location_info_dict, location_data = get_quad_wise_location_info(empty_locations)

        # obtain the required drug qty quadrant wise
        quad_drug_req_qty_dict, quad_drug_req_qty_ordered_dict, total_required_unique_drug = get_quad_drug_req_qty_for_packs(
            pack_list)

        dis_quad_drug_canister_dict_updated = sort_dict(dis_quad_drug_canister_dict, quad_drug_req_qty_dict)

        canister_destination_location_dict = get_transfers(dis_quad_drug_canister_dict_updated, quad_drug_req_qty_dict,
                                                           quad_drug_req_qty_ordered_dict,
                                                           canister_destination_location_dict,
                                                           empty_quad_location_info_dict, canister_location_info_dict,
                                                           quad_drug_canister_dict, dis_quad_canisters,
                                                           canister_drug_info_dict)

        response_data = make_response_data(canister_destination_location_dict)

        return create_response(response_data)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_disabled_location_canister_transfers {}".format(e))
        raise


@log_args_and_response
def sort_dict(dis_quad_drug_canister_dict, quad_drug_req_qty_dict):
    dis_quad_drug_canister_dict_updated = deepcopy(dis_quad_drug_canister_dict)
    for quad, drug_canister in dis_quad_drug_canister_dict.items():
        # if quad not in quad_drug_req_qty_dict:
        #     continue
        for drug, req_qty in quad_drug_req_qty_dict[quad].items():
            if drug not in drug_canister:
                continue
            if quad not in dis_quad_drug_canister_dict_updated:
                dis_quad_drug_canister_dict_updated[quad] = OrderedDict()
            dis_quad_drug_canister_dict_updated[quad] = drug_canister
    return dis_quad_drug_canister_dict_updated


@log_args_and_response
def get_transfers(dis_quad_drug_canister_dict_updated, quad_drug_req_qty_dict, quad_drug_req_qty_ordered_dict,
                  canister_destination_location_dict, empty_quad_location_info_dict, canister_location_info_dict,
                  quad_drug_canister_dict, dis_quad_canisters, canister_drug_info_dict):
    try:
        canister_to_remove = 0
        # alloted = False
        index = 0
        # empty_quad_location_info_dict[4]['display_location'] = []
        for quad, drug_canister in dis_quad_drug_canister_dict_updated.items():
            alloted = False
            for drug, canister in drug_canister.items():
                canister_info = canister_location_info_dict.get(canister, None)
                if drug not in quad_drug_req_qty_dict[quad]:
                    canister_destination_location_dict[canister] = {
                        'fndc_txr': canister_drug_info_dict[canister]['fndc_txr'],
                        'drug_name': canister_drug_info_dict[canister]['drug_name'],
                        'drug_ndc': canister_drug_info_dict[canister]['ndc'],
                        'required_qty': 0,
                        'source_device_name': canister_info[5] if canister_info else None,
                        'source_device_id': canister_info[0] if canister_info else None,
                        'source_display_location': canister_info[2] if canister_info else None,
                        'rfid': canister_info[3] if canister_info else None,
                        'dest_quadrant': None,
                        'dest_device_name': None,
                        'dest_device_id': None, 'dest_display_location': None, 'dest_location_number': None}
                elif quad_drug_req_qty_dict[quad][drug] == 0:
                    canister_info = canister_location_info_dict.get(canister, None)
                    canister_destination_location_dict[canister] = {
                        'fndc_txr': canister_drug_info_dict[canister]['fndc_txr'],
                        'drug_name': canister_drug_info_dict[canister]['drug_name'],
                        'drug_ndc': canister_drug_info_dict[canister]['ndc'],
                        'required_qty': 0,
                        'source_device_name': canister_info[5] if canister_info else None,
                        'source_device_id': canister_info[0] if canister_info else None,
                        'source_display_location': canister_info[2] if canister_info else None,
                        'rfid': canister_info[3] if canister_info else None,
                        'dest_quadrant': None,
                        'dest_device_id': None, 'dest_device_name': None, 'dest_display_location': None,
                        'dest_location_number': None}
                    for drug_qty in quad_drug_req_qty_ordered_dict[quad]:
                        if drug_qty[0] == drug:
                            quad_drug_req_qty_ordered_dict[quad].remove(drug_qty)
                            del quad_drug_req_qty_dict[quad][drug]
                            break
                elif len(empty_quad_location_info_dict[quad]['display_location']) > 0:
                    canister_info = canister_location_info_dict.get(canister, None)
                    canister_destination_location_dict[canister] = {
                        'fndc_txr': canister_drug_info_dict[canister]['fndc_txr'],
                        'drug_name': canister_drug_info_dict[canister]['drug_name'],
                        'drug_ndc': canister_drug_info_dict[canister]['ndc'],
                        'required_qty': quad_drug_req_qty_dict[quad][drug],
                        'source_device_name': canister_info[5] if canister_info else None,
                        'source_device_id': canister_info[0] if canister_info else None,
                        'source_display_location': canister_info[2] if canister_info else None,
                        'rfid': canister_info[3] if canister_info else None,
                        'dest_device_id': canister_info[0] if canister_info else None,
                        'dest_device_name': canister_info[5] if canister_info else None,
                        'dest_quadrant': quad,
                        'dest_display_location': empty_quad_location_info_dict[quad]['display_location'].pop(),
                        'dest_location_number': empty_quad_location_info_dict[quad]['location_number'].pop()}
                else:
                    for i, drug_1 in enumerate(quad_drug_req_qty_dict[quad]):
                        if drug_1 not in quad_drug_canister_dict[quad]:
                            continue
                        canister_to_remove = next(
                            iter(quad_drug_canister_dict[quad][quad_drug_req_qty_ordered_dict[quad][i][0]]))
                        if canister == canister_to_remove or int(quad_drug_req_qty_dict[quad][drug_1]) == int(
                                quad_drug_req_qty_dict[quad][drug]):
                            canister_info = canister_location_info_dict.get(canister, None)
                            canister_destination_location_dict[canister] = {
                                'fndc_txr': canister_drug_info_dict[canister]['fndc_txr'],
                                'drug_name': canister_drug_info_dict[canister]['drug_name'],
                                'drug_ndc': canister_drug_info_dict[canister]['ndc'],
                                'required_qty': 0,
                                'source_device_name': canister_info[5] if canister_info else None,
                                'source_device_id': canister_info[0] if canister_info else None,
                                'source_display_location': canister_info[2] if canister_info else None,
                                'rfid': canister_info[3] if canister_info else None,
                                'dest_device_id': None,
                                'dest_device_name': None,
                                'dest_quadrant': None, 'dest_display_location': None, 'dest_location_number': None}
                            quad_drug_req_qty_ordered_dict[quad].remove(quad_drug_req_qty_ordered_dict[quad][i])
                            del quad_drug_req_qty_dict[quad][drug]
                            alloted = True
                            break
                        if canister_to_remove in dis_quad_canisters[quad]:
                            continue
                        else:
                            index = i
                            break
                    if not alloted:
                        required_qty = quad_drug_req_qty_dict[quad][drug]
                        del quad_drug_req_qty_dict[quad][quad_drug_req_qty_ordered_dict[quad][index][0]]
                        quad_drug_req_qty_ordered_dict[quad].remove(quad_drug_req_qty_ordered_dict[quad][index])
                        del quad_drug_req_qty_dict[quad][drug]
                        for drug_qty in quad_drug_req_qty_ordered_dict[quad]:
                            if drug_qty[0] == drug:
                                quad_drug_req_qty_ordered_dict[quad].remove(drug_qty)
                                break
                        canister_info = canister_location_info_dict.get(canister_to_remove, None)
                        canister_destination_location_dict[canister_to_remove] = {
                            'fndc_txr': canister_drug_info_dict[canister_to_remove]['fndc_txr'],
                            'drug_name': canister_drug_info_dict[canister_to_remove]['drug_name'],
                            'drug_ndc': canister_drug_info_dict[canister_to_remove]['ndc'],
                            'required_qty': 0,
                            'source_device_name': canister_info[5] if canister_info else None,
                            'source_device_id': canister_info[0] if canister_info else None,
                            'source_display_location': canister_info[2] if canister_info else None,
                            'rfid': canister_info[3] if canister_info else None,
                            'dest_device_id': None,
                            'dest_device_name': None,
                            'dest_quadrant': None, 'dest_display_location': None, 'dest_location_number': None}
                        canister_info = canister_location_info_dict.get(canister, None)
                        canister_destination_location_dict[canister] = {
                            'fndc_txr': canister_drug_info_dict[canister]['fndc_txr'],
                            'drug_name': canister_drug_info_dict[canister]['drug_name'],
                            'drug_ndc': canister_drug_info_dict[canister]['ndc'],
                            'required_qty': required_qty,
                            'source_device_name': canister_info[5] if canister_info else None,
                            'source_device_id': canister_info[0] if canister_info else None,
                            'source_display_location': canister_info[2] if canister_info else None,
                            'rfid': canister_info[3] if canister_info else None,
                            'dest_device_id': canister_info[0] if canister_info else None,
                            'dest_device_name': canister_info[5] if canister_info else None,
                            'dest_quadrant': canister_info[1] if canister_info else None,
                            'dest_display_location': canister_info[2] if canister_info else None,
                            'dest_location_number': canister_info[4] if canister_info else None}
                        # del quad_drug_req_qty_dict[quad][drug]
                        # for drug_qty in quad_drug_req_qty_ordered_dict[quad]:
                        #     if drug_qty[0] == drug:
                        #         quad_drug_req_qty_ordered_dict[quad].remove(drug_qty)
                        #         break

        return canister_destination_location_dict
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_transfers {}".format(e))
        raise


@log_args_and_response
def make_response_data(canister_destination_location_dict: dict):
    """
    To create response for the given parameters
    """
    # final_dict = {}
    # transfer_dict = {}
    response_data = []
    transfer_data = []

    try:
        for canister, dest_loc in canister_destination_location_dict.items():
            transfer_dict: dict = dict()
            transfer_dict['canister_id'] = canister
            transfer_dict.update(dest_loc)
            transfer_data.append(deepcopy(transfer_dict))
            # if not drawer_flag:
            #     break
        final_dict = {'transfers': transfer_data}
        response_data.append(final_dict)
        return response_data
    except Exception as e:
        logger.error("error in make_response_data {}".format(e))
        raise


@log_args_and_response
@validate(required_fields=["drug_id", "rfid", "product_id", "user_id", "system_id", "barcode", "company_id"],
          validate_location=['location_number'])
def add_canister(dict_canister_info):
    """ Take the canister info and creates a new canister.

        Args:
            dict_canister_info (dict): The key value pairs required to add a new canister

        Returns:
           json: success or the failure response along with the id of the canister added.

        Examples:
            >>> add_canister({"system_id":14,"big_stick_depth":None,"product_id":11858,"drug_id":4918,
            "rfid":"22904320641008415C0DA000A000008F","big_stick_width":null,"big_stick_serial_number":null,
            "small_stick_length":null,"drug_name":"CARVEDILOL","canister_type":71,"drug_data":{"fillet":"2.634",
            "shape":"Round Flat","length":2.634,"width":4.471,"depth":4.471},"ndc":"68382009205","company_id":3,
            "user_id":13,"device_id":null,"location_number":0,"available_quantity":0,"reorder_quantity":10,
            "barcode":"dummy","drum_serial_number":"S39","drum_depth":"3.1","drum_width":"5.5","drum_length":"4.4"}
)
                {"status": "success", "data": 1}
    """
    logger.info("add canister dict {}".format(dict_canister_info))

    company_id = int(dict_canister_info["company_id"])
    system_id = dict_canister_info.get("system_id", None)
    manual_flag = dict_canister_info.get("manualflag", 'N')
    user_id = int(dict_canister_info["user_id"])

    # get zone_id from system id
    zone_id = get_zone_by_system(system_id)

    #  if device_id in input validate device and location
    if dict_canister_info.get("device_id", None):
        # If robot id present check for validations

        valid_device = verify_device_id_dao(device_id=dict_canister_info["device_id"], system_id=system_id)

        if not valid_device:
            return error(1015)

        query_status, canister_present = db_is_canister_present(
            dict_canister_info["device_id"],
            dict_canister_info["location_number"]
        )
        #  checking if canister already present for given robot
        if query_status and canister_present:
            return error(1013)
        elif not query_status:
            return error(1003)

        location_id = get_location_id_by_location_number_dao(device_id=dict_canister_info["device_id"],
                                                     location_number=dict_canister_info["location_number"])

        disabled_location = db_location_disabled_details(location_id=location_id)
        if disabled_location:
            return error(3003)

    else:
        dict_canister_info["device_id"] = None
        dict_canister_info["location_number"] = None
        location_id = None  # set canister outside
    logger.info("In add_canister. validating rfid")
    if dict_canister_info["rfid"]:
        try:
            if not validate_rfid_checksum(dict_canister_info["rfid"]):
                return error(1022)
        except Exception as e:
            logger.error("Error in validating RFID: {}".format(e))
            logger.error(e, exc_info=True)
            return error(1023)

    logger.info("In add_canister. Updating canister status")
    try:
        with db.transaction():
            if manual_flag == "Y":
                update_status = update_canister_status_by_location_dao(status=False, location_id=location_id)
                logger.info("Update Status For Manual List: " + str(update_status))

            try:
                canister_code = get_canister_code(dict_canister_info["drug_id"])
            except DoesNotExist:
                return error(1017)

            try:  # check for duplicate rfid
                canister_exists = db_check_canister_available_dao(rfid=dict_canister_info["rfid"])

                if canister_exists:
                    logger.error('Duplicate rfid {} found while adding canister for canister data {}'
                                 .format(dict_canister_info["rfid"], dict_canister_info))
                    return error(1024)

            except DoesNotExist:
                pass  # No duplicate rfid

            logger.info("In add_canister. creating canister record")

            canister_master_id = db_create_canister_record_dao(dict_canister_info, company_id, canister_code, user_id,
                                                               location_id)

            if zone_id is not None:
                for id in zone_id:
                    db_create_canister_zone_mapping_dao(canister_master_id, id, user_id)

            # add data in canister status history
            status_data_dict = {
                "canister_id": canister_master_id,
                "action": constants.CODE_MASTER_CANISTER_ACTIVATE,
                "created_by": user_id,
                "created_date": get_current_date_time()
            }
            canister_status_history = add_canister_status_history(data_dict=status_data_dict)
            logger.info("Record added in canister history and canister status history : {}".format(canister_status_history))

            if not dict_canister_info.get('product_id', None):
                canister_tracker_info: Dict[str, Any] = {
                    "canister_id": canister_master_id,
                    "device_id": None,
                    "drug_id": dict_canister_info["drug_id"],
                    "qty_update_type_id": constants.CANISTER_QUANTITY_UPDATE_TYPE_REPLENISHMENT,
                    "original_quantity": dict_canister_info.get("available_quantity", 0),
                    "quantity_adjusted": 0,
                    "lot_number": dict_canister_info.get("lot_number", None),
                    "expiration_date": dict_canister_info.get("expiration_date", None),
                    "note": "default",
                    "created_by": user_id,
                    "drug_scan_type_id": constants.USER_ENTERED,
                    "replenish_mode_id": constants.MANUAL_CODE
                }
                db_create_canister_tracker_dao(canister_tracker_info)

        try:
            drug = db_get_by_id(dict_canister_info["drug_id"])
            drug_image = drug.image_name
            drug_ndc = drug.ndc
            # insert drug, marks it new, if already present don't change status
            db_create_new_fill_drug_dao(drug, company_id)
        except (DoesNotExist, IntegrityError, InternalError, Exception):
            drug_image = None
            drug_ndc = None

        try:

            lower_level = db_get_unique_drug_lower_level_by_drug(drug_id=dict_canister_info["drug_id"])
        except (DoesNotExist, IntegrityError, InternalError, Exception):
            lower_level = None

        if dict_canister_info.get('product_id', None):
            try:

                unique_drug_id = db_get_unique_drug_by_drug_id(drug_id=dict_canister_info["drug_id"])
                print(unique_drug_id)
                unique_drug_id = unique_drug_id.get()
            except Exception as e:
                logger.info(e)
                logger.info("In add_canister, Exception in db_get_unique_drug_by_drug_id : {}".format(e))

                drug_master_data = db_get_drug_txr_fndc_id_dao(drug_id=dict_canister_info["drug_id"])

                try:

                    unique_drug_id = db_create_unique_drug_dao(drug_master_data)
                except Exception as e:
                    logger.info("In add_canister, Exception in unique_drug_id : {}".format(e))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(
                        f"Error in add_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")

            logger.info("In add_canister. Fetching shape id")

            shape_id = db_get_custom_drug_shape_name(dict_canister_info['drug_data']['shape'])

            # create dimension data dict
            dimension_data = {"fillet": dict_canister_info['drug_data']['fillet'],
                              "shape": shape_id,
                              "length": dict_canister_info['drug_data']['length'],
                              "width": dict_canister_info['drug_data']['width'],
                              "depth": dict_canister_info['drug_data']['depth'],
                              "delete_mappings": False,
                              "add_canister": True}
            logger.info("In add_canister: Dimension Data {}".format(dimension_data))
            try:

                drug_dimension = db_get_drug_dimension_id_by_unique_drug(unique_drug_id['id'])

                dimension_data.update({"id": drug_dimension['id'], "user_id": user_id})
                response = json.loads(update_drug_dimension(dimension_data))
                print(response)
                if response["status"] == settings.FAILURE_RESPONSE:
                    raise CanisterStickException(response['code'])
            except DoesNotExist as e:
                logger.info(e)
                dimension_data.pop('delete_mappings', None)
                dimension_data.update({'unique_drug_id': unique_drug_id['id'],
                                       'user_id': dict_canister_info['user_id'],
                                       "add_canister": True})
                add_drug_dimension(dimension_data)
            except CanisterStickException as e:
                print(e)
                logger.info("In add_canister: Exception at CanisterStickException. {}".format(e))
                return error(e.error_code)


            dimension_id = db_get_drug_dimension_id_by_unique_drug(unique_drug_id['id'])

            dict_canister_info.update({'drug_dimension_id': dimension_id['id']})
            dict_canister_info['width'] = dict_canister_info.pop('big_stick_width', None)
            dict_canister_info['depth'] = dict_canister_info.pop('big_stick_depth', None)
            dict_canister_info['length'] = dict_canister_info.pop('small_stick_length', None)
            dict_canister_info['serial_number'] = dict_canister_info.pop('big_stick_serial_number', None)
            response = add_canister_stick_mapping(dict_canister_info, canister_master_id)
            response = json.loads(response)
            if response["status"] == settings.FAILURE_RESPONSE:
                raise CanisterStickException(response['code'])

    except CanisterStickException as e:
        return error(e.error_code)

    except (DataError, IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(1001)
    except Exception as e:
        logger.error(e)
        logger.info("In add_canister, Exception  : {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in add_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
    try:
        response = {'canister_id': canister_master_id, 'image_name': drug_image}

        if "product_id" in dict_canister_info.keys():
            product_id = dict_canister_info["product_id"]
        else:
            product_id = None

        big_stick_serial_number = dict_canister_info["serial_number"]
        small_stick_serial_number = dict_canister_info["length"]
        if small_stick_serial_number is not None:
            small_stick_serial_number = int(small_stick_serial_number)
        drum_serial_number = dict_canister_info["drum_serial_number"]

        if dict_canister_info["rfid"] is not None and drug_ndc is not None:
            data_dict = {"ndc": drug_ndc,
                         "canister_id": canister_master_id,
                         "rfid": dict_canister_info["rfid"],
                         "product_id": product_id,
                         "big_stick_serial_number": big_stick_serial_number,
                         "small_stick_serial_number": small_stick_serial_number,
                         "drum_serial_number": drum_serial_number,
                         "lower_level": lower_level}

            response_data = get_canister_label(data_dict)
            logger.info(response_data)
            canister_label = json.loads(response_data)
            if "data" in canister_label:
                response.update(canister_label["data"])
            else:
                response.update(canister_label)
        logger.info(response)
        return create_response(response)

    except Exception as e:
        logger.info("In add_canister:  Error at end: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in add_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")


@log_args_and_response
def get_location_no_from_display_location(location_rfid_dict, device_id, location_fork_dict):
    """
    @param location_rfid_dict:
    @return:
    @param device_id:
    @param location_fork_dict:
    @return:
    """
    # todo reduce the loop
    try:
        logger.info("get_location_no_from_display_location {}".format(location_rfid_dict))
        updated_location_rfid_dict = dict()
        mfd_canister_locations = dict()

        for display_location, rfid in location_rfid_dict.items():
            # location_number = LocationMaster.get_location_number_from_display_location(device_id=device_id,
            #                                                                        display_location=display_location)
            location_number = get_location_number_from_display_location_dao(device_id=device_id,
                                                                            display_location=display_location)

            temp = list(display_location.split("-"))

            if len(temp) and "M" in temp[0]:
                # location_id, is_disable = LocationMaster.get_location_id_from_display_location(device_id,
                #                                                                               display_location)
                location_id, is_disable = get_location_id_from_display_location_dao(device_id=device_id,
                                                                                    display_location=display_location)
                mfd_canister_locations[int(location_id)] = rfid, location_fork_dict.get(display_location, False), \
                                                           is_disable

            else:
                logger.info("Location number {}".format(location_number))
                updated_location_rfid_dict[int(location_number)] = rfid

        logger.info("updated_location_rfid_dict {}".format(updated_location_rfid_dict))
        return updated_location_rfid_dict, mfd_canister_locations

    except Exception as e:
        logger.error("error in get_location_no_from_display_location {}".format(e))
        return {}


@log_args_and_response
def validate_csr_location_for_canister(locations_rfid_dict):
    """

    @param locations_rfid_dict:
    @return:
    """
    try:
        for location, rfid in locations_rfid_dict.items():
            drawer_size, drawer_usage = get_device_location_category(location)
            canister_type, canister_usage = get_canister_details_by_rfid_dao(rfid)

            if drawer_size != canister_type or drawer_usage != canister_usage:
                return False

        return True

    except Exception as e:
        logger.error("error in validate_csr_location_for_canister {}".format(e))
        return False


@log_args_and_response
def adjust(dict_canister_info, _type, note, user_id, current_date, company_id):
    """ Updates the canister quantity for the given canister id

        Args:
            dict_canister_info (dict): The key containing the canister id, quantity to be adjusted
            _type(boolean) - rfid based or canister_id based
            note(str) - note for replenishing the canister quantity
            user_id(int) - the id of the user
            current_date(date) - the current date when replenish is taking place.
            current_time(time) - the current time when replenish is taking place.

        Returns:
           json: success or the failure response along with the id of the canister deleted.

        Examples:
            >>> adjust({"canister_id": 1)
                {"status": "success", "data": 1}
                @param dict_canister_info:
                @param _type:
                @param note:
                @param user_id:
                @param current_date:
                @return:
                @param company_id:
    """
    try:
        if _type == 1:
            _field = dict_canister_info["canister_id"]
        elif _type == 2:
            _field = dict_canister_info["rfid"]
        else:
            raise CanisterQuantityAdjustmentException("Invalid value for type.")

        # get drug_name, ndc, device_id from given canister_id
        drug_id, device_id, _id, current_qty = get_canister_details(
            _field, company_id, _type
        )

        if current_qty < 0:
            current_qty = 0

        if _type == 1:
            # begin transaction
            updated_quantity = current_qty + dict_canister_info["quantity"]
        elif _type == 2:
            updated_quantity = dict_canister_info["quantity"]
        else:
            raise CanisterQuantityAdjustmentException("Invalid value for type.")


        status = update_canister_dao(update_dict={
            "available_quantity": updated_quantity,
            "modified_by": user_id,
            "modified_date": current_date
        }, id=_id)

        if status:
            response = insert_drug_bottle_pill_drop_data(quantity_adjusted=dict_canister_info["quantity"],
                                                         lot_number=dict_canister_info["lot_number"],
                                                         created_by=user_id)
            print("Response from insert_drug_bottle_pill_drop_data: " + str(response))

        canister_tracker_info: Dict[str, Any] = {
            "canister_id": _id,
            "drug_id": drug_id,
            "device_id": dict_canister_info["device_id"],
            "qty_update_type_id": constants.CANISTER_QUANTITY_UPDATE_TYPE_ADJUSTMENT,
            "original_quantity": dict_canister_info["quantity"],
            "quantity_adjusted": 0,
            "lot_number": dict_canister_info["lot_number"],
            "expiration_date": dict_canister_info["expiration_date"],
            "note": note,
            # "created_time": current_time,     -- There is no column as created_time
            "created_by": user_id
        }

        db_create_canister_tracker_dao(canister_tracker_info)

    except (IntegrityError, InternalError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in adjust {}".format(e))
        raise CanisterQuantityAdjustmentException(e)

    return {"data": status}


@log_args_and_response
@validate(required_fields=["canister_id", "adjusted_quantity", "company_id", "user_id", "device_id"],
          validate_canister_id=['canister_id'],
          validate_canister_quantity=['adjusted_quantity'])
def adjust_canister_quantity(dict_canister_info):
    """ Updates the canister quantity for the given canister id

        Args:
            dict_canister_info (dict): The key containing the canister id, quantity to be adjusted

        Returns:
           json: success or the failure response along with the id of the canister deleted.

        Examples:
            >>> adjust_canister_quantity({"canister_id": 1)
                {"status": "success", "data": 1}
    """
    # get the current date, current time and current date time from settings
    current_date = get_current_date()
    # current_time = get_current_time()

    # get the user_id from dict_canister_info
    user_id = int(dict_canister_info["user_id"])
    company_id = int(dict_canister_info["company_id"])
    raise_exception = dict_canister_info.get('raise_exception', False)

    try:
        with db.transaction():
            # get drug_name, ndc, device_id from given canister_id
            drug_id, device_id, _id, current_qty = get_canister_details(
                dict_canister_info["canister_id"], company_id
            )
            if dict_canister_info['replace_qty']:
                updated_quantity = dict_canister_info['adjusted_quantity']
                dict_canister_info['adjusted_quantity'] = updated_quantity - current_qty
            elif not dict_canister_info["qty_adjusted"]:
                updated_quantity = dict_canister_info["adjusted_quantity"]
            # elif dict_canister_info["qty_adjusted"] > 0:
            #     updated_quantity = current_qty - dict_canister_info["qty_adjusted"] + dict_canister_info[
            #         "adjusted_quantity"]
            else:
                updated_quantity = current_qty + dict_canister_info["adjusted_quantity"]


            status = update_canister_dao(update_dict={
                "available_quantity": updated_quantity,
                "modified_by": user_id,
                "modified_date": current_date
            }, id=dict_canister_info["canister_id"])

            if status:
                response = insert_drug_bottle_pill_drop_data(quantity_adjusted=dict_canister_info["adjusted_quantity"],
                                                             lot_number=dict_canister_info["lot_number"],
                                                             created_by=user_id)
                print("Response from insert_drug_bottle_pill_drop_data: " + str(response))

            canister_tracker_info: Dict[str, Any] = {
                "canister_id": dict_canister_info["canister_id"],
                "device_id": device_id,
                "drug_id": drug_id,
                "qty_update_type_id": constants.CANISTER_QUANTITY_UPDATE_TYPE_ADJUSTMENT,
                "original_quantity": current_qty,
                "quantity_adjusted": dict_canister_info["adjusted_quantity"] if dict_canister_info['qty_adjusted']
                else dict_canister_info["adjusted_quantity"] - current_qty,
                "lot_number": dict_canister_info["lot_number"],
                "expiration_date": dict_canister_info["expiration_date"],
                "note": dict_canister_info["note"],
                "created_by": user_id,
                "voice_notification_uuid": dict_canister_info.get("voice_notification_uuid", None)
            }
            db_create_canister_tracker_dao(canister_tracker_info)



            # if canister is currently reserved for any batch then updating replenish queue for v3 system type
            canister_data = db_get_reserved_canister_data(canister_id=dict_canister_info["canister_id"])
            logger.info('reserved_canister_data_while_replenish: ' + str(canister_data))
            if canister_data:
                logger.info("updating_replenish_data_while_adjust_qty")
                update_replenish_based_on_system(canister_data['system_id'])

    except (IntegrityError, InternalError, DataError, DoesNotExist) as e:
        if raise_exception:
            raise CanisterQuantityAdjustmentException(e)
        else:
            return error(2001)
    except ValueError as e:
        if raise_exception:
            raise ValueError(str(e))
        else:
            return error(2005)

    except Exception as e:
        if raise_exception:
            raise CanisterQuantityAdjustmentException(e)
        else:
            return error(2001)

    return create_response(status, additional_info={"canister_id": dict_canister_info["canister_id"]})


@log_args_and_response
def get_appropriate_drug_info_for_adjusted_quantity(canister_id: int, adjusted_qty: int, available_qty: int) -> list:
    """
    Method to get appropriate drug info to save adjusted quantity data in canister tracker.
    Logic: Fetch latest replenish info based on replenish mode - manual > Replenished with entire drug bottle > refill device
    Consider replenish records only between two adjustment i.e., one cluster
    @param available_qty:
    @param adjusted_qty:
    @param canister_id:
    @return:
    """
    try:

        if adjusted_qty == 0:
            raise ValueError("adjusted_qty shouldn't be 0")
        adjust_history_ids = list()
        adjust_canister_dict = OrderedDict()
        replenish_history_ids = list()

        logger.info("adjust_canister_quantity_v3: 1. Fetching latest canister adjustment data")
        latest_adjusted_qty_info = get_latest_adjusted_canister_record_by_canister_id(canister_id=canister_id)

        if not latest_adjusted_qty_info:
            logger.info("adjust_canister_quantity_v3: No records of canister adjusted qty so fetching latest "
                         "replenish records directly")
            recent_replenish_list = get_recently_replenished_drug_info(canister_id=canister_id)

            if not recent_replenish_list:
                logger.info("adjust_canister_quantity_v3: No adjustment and replenish records available for "
                             "canister_id - {}".format(canister_id))
                return list(adjust_canister_dict.values())

            logger.info("adjust_canister_quantity_v3: Replenish records available so adjust canister")
            further_adjustment_required, adjust_canister_dict, replenish_history_ids, adjusted_qty, available_qty = \
                find_adjustment_list(adjusted_qty, available_qty, recent_replenish_list, adjust_canister_dict,
                                     replenish_history_ids)
            logger.info("adjust_canister_quantity_v3: adjust_canister_dict: " + str(adjust_canister_dict))
            # Here No need to check if further_adjustment_required or not as no more replenish data available
            return list(adjust_canister_dict.values())

        # Adjusted quantity record found so now fetch recent drug data based on last canister quantity adjusted and
        # latest replenish info
        logger.info("adjust_canister_quantity_v3: 2.Adjusted quantity record found so now fetch recent replenish info")
        adjust_history_ids.append(latest_adjusted_qty_info["id"])
        further_adjustment_required = True

        while further_adjustment_required:
            if len(adjust_history_ids) == 1:
                logger.info("adjust_canister_quantity_v3: Fetching replenish info for the immediate cluster")
                recent_replenish_list = get_recently_replenished_drug_info(canister_id=canister_id,
                                                                           record_after_id=latest_adjusted_qty_info[
                                                                               "id"],
                                                                           exception_ids=replenish_history_ids)
            else:
                logger.info("adjust_canister_quantity_v3: Fetching replenish info for the cluster between - "
                             "canister tracker record ids: {} and {}".format(adjust_history_ids[-2],
                                                                             latest_adjusted_qty_info["id"]))
                recent_replenish_list = get_recently_replenished_drug_info(canister_id=canister_id,
                                                                           record_after_id=latest_adjusted_qty_info["id"],
                                                                           record_before_id=adjust_history_ids[-2],
                                                                           exception_ids=replenish_history_ids)

            if not recent_replenish_list:
                logger.info("adjust_canister_quantity_v3: No recent replenish found after adjusted qty record id: "
                             + str(latest_adjusted_qty_info["id"]) + " So fetching next adjustment record")
                latest_adjusted_qty_info = get_latest_adjusted_canister_record_by_canister_id(canister_id=canister_id,
                                                                                              exception_ids=adjust_history_ids)
                if not latest_adjusted_qty_info:
                    logger.info("adjust_canister_quantity_v3: No records of next canister adjusted qty so"
                                 " fetching latest replenish records directly")
                    recent_replenish_list = get_recently_replenished_drug_info(canister_id=canister_id,
                                                                               record_before_id=adjust_history_ids[-1])

                    if not recent_replenish_list:
                        logger.info("adjust_canister_quantity_v3: No replenish records available for canister_id "
                                     "- {}".format(canister_id))
                        break  # No more adjustment or replenish info available

                    logger.info("adjust_canister_quantity_v3: Replenish records available so adjust canister")
                    further_adjustment_required, adjust_canister_dict, replenish_history_ids, adjusted_qty, \
                        available_qty = find_adjustment_list(adjusted_qty, available_qty, recent_replenish_list,
                                                         adjust_canister_dict, replenish_history_ids)
                    logger.info("adjust_canister_quantity_v3: adjust_canister_dict: " + str(adjust_canister_dict))
                    break  # No more adjustment or replenish info available

                adjust_history_ids.append(latest_adjusted_qty_info["id"])
                # as no recent replenish in current cluster but adjusted record available so check in previous cluster
                # after found adjustment record
                continue
            logger.info(
                "adjust_canister_quantity_v3: Found replenishment list after last adjustment so find adjustment"
                " list based on that")
            further_adjustment_required, adjust_canister_dict, replenish_history_ids, adjusted_qty, available_qty = \
                find_adjustment_list(adjusted_qty, available_qty, recent_replenish_list,
                                     adjust_canister_dict, replenish_history_ids)

        logger.info("adjust_canister_quantity_v3: Final adjust_canister_dict: " + str(adjust_canister_dict))
        return list(adjust_canister_dict.values())

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_appropriate_drug_info_for_adjusted_quantity {}".format(e))
        raise e


@log_args_and_response
def find_adjustment_list(adjusted_qty: int, available_qty: int, recent_replenish_list: list,
                         adjust_canister_dict: dict, replenish_history_ids: list) -> tuple:
    try:
        if adjusted_qty > 0:
            logger.info("adjust_canister_quantity_v3: Adjusted quantity is positive,"
                         " so directly preparing adjust canister dict")

            latest_replenishment_details_by_replenish_mode = dict()

            for record in recent_replenish_list:
                latest_replenishment_details_by_replenish_mode[record["replenish_mode_id"]] = record

            for mode in constants.ADJUST_REPLENISH_MODE_PRIORITY:
                if mode in latest_replenishment_details_by_replenish_mode:
                    replenish_to_use = latest_replenishment_details_by_replenish_mode[mode]
                    break

            adjust_canister_dict[replenish_to_use["drug_id"], replenish_to_use["case_id"]] = \
                {"drug_id": replenish_to_use["drug_id"],
                 "adjusted_qty": adjusted_qty,
                 "available_qty": available_qty,
                 "lot_no": replenish_to_use["lot_number"],
                 "expiration_date": replenish_to_use["expiration_date"],
                 "case_id": replenish_to_use['case_id']
                 }
            return False, adjust_canister_dict, [replenish_to_use["id"]], adjusted_qty, available_qty
        else:
            logger.info("adjust_canister_quantity_v3: Adjusted quantity is negative,"
                         " so prepare adjust canister data based on replenished drug quantity")

            for replenish_info in recent_replenish_list:
                replenish_history_ids.append(replenish_info["id"])
                replenished_qty = replenish_info["quantity_adjusted"]

                # Compare replenished_qty with adjusted qty to adjust max possible replenished drug quantity
                # as in real we can't remove quantity more than added for particular drug, e.g.,
                # if canister replenished with drug d1(50 drugs) and then if he adjusts 60 drugs then
                # we can't consider drug d1 only for adjustment as max drug qty possible for d1 is , so we have to
                # check for another possible drug d2 if replenished and adjust 10 qty with d2.
                if abs(adjusted_qty) <= replenished_qty:
                    # Directly consider adjusted_qty as adjusted_qty is less than replenished_qty
                    temp_adjust_qty = adjusted_qty
                else:
                    # Can adjust max up to replenished_qty with the selected drug
                    temp_adjust_qty = int(-replenished_qty)

                if (replenish_info["drug_id"], replenish_info["case_id"]) not in adjust_canister_dict.keys():
                    # Add new record in dict
                    adjust_canister_dict[(replenish_info["drug_id"], replenish_info["case_id"])] = \
                        {"drug_id": replenish_info["drug_id"],
                         "adjusted_qty": temp_adjust_qty,
                         "available_qty": available_qty,
                         "lot_no": replenish_info["lot_number"],
                         "expiration_date": replenish_info["expiration_date"],
                         "case_id": replenish_info['case_id']}

                else:
                    # modifies existing record based on drug id
                    # we are adding to quantity_adjusted because both quantity_adjusted and temp_adjust_qty are negative
                    adjust_canister_dict[(replenish_info["drug_id"], replenish_info["case_id"])]["adjusted_qty"] += int(temp_adjust_qty)

                    # find index of replenish_info["drug_id"] in ordered dict adjust_canister_dict to
                    # update available_qty in records after current record
                    i = tuple(adjust_canister_dict).index((replenish_info["drug_id"], replenish_info["case_id"]))
                    for drug, data in list(adjust_canister_dict.items())[i + 1:]:
                        data["available_qty"] += int(temp_adjust_qty)

                available_qty += temp_adjust_qty  # as available_qty is +ve and temp_adjust_qty so adding
                adjusted_qty -= temp_adjust_qty  # both adjusted and temp_adjust_qty so taking difference

                if not abs(adjusted_qty):
                    # when adjusted_qty is 0 i.e., no further adjustment needed.
                    return False, adjust_canister_dict, replenish_history_ids, adjusted_qty, available_qty

            return True, adjust_canister_dict, replenish_history_ids, adjusted_qty, available_qty
    except Exception as e:
        logger.error("error in find_adjustment_list {}".format(e))
        raise


@log_args_and_response
def get_canister_code(drug_id, canister_id=None):
    """
    "Takes drug_id, fetches ndc and creates canister code using ndc and unique_code.\
    Format of Canister Code: ndc#unique_code (separator: #)"
    :param drug_id:
    :param canister_id: to update existing canister (optional)
    :return:
    """

    try:
        ndc = get_drug_status_by_drug_id(drug_id).ndc
    except (InternalError, IntegrityError, DoesNotExist, Exception) as e:
        logger.error(e, exc_info=True)
        raise

    if canister_id is None:
        try:
            # last_id = CanisterMaster.select(CanisterMaster.id) \
            #     .order_by(CanisterMaster.id.desc()) \
            #     .get().id
            last_id = db_get_last_canister_id_dao()
            last_id = last_id + 1
        except DoesNotExist:
            last_id = 1
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e
    else:
        last_id = canister_id

    unique_code = str(last_id).zfill(10)
    canister_code = ndc + "#" + unique_code  # generating unique canister code
    return canister_code


@log_args_and_response
@validate(required_fields=["data", "user_id"])
def transfer_canisters(dict_canister_info):
    """
    Transfers location_number and device_id of source and destination (if available) canister

    @param dict_canister_info: contains system id and data of canisters to update
    :return:
    """
    user_id = dict_canister_info["user_id"]
    data = dict_canister_info["data"]
    source_device_id = data["source_device_id"]
    source_canister_location = data["source_canister_location"]
    dest_device_id = data["dest_device_id"]
    dest_canister_location = data["dest_canister_location"]
    source_zone_id = list(map(lambda x: int(x), data["source_zone_id"].split(','))) if (
            "source_zone_id" in data.keys() and data["source_zone_id"] is not None) else None
    dest_zone_id = list(map(lambda x: int(x), data["dest_zone_id"].split(','))) if (
            "dest_zone_id" in data.keys() and data["dest_zone_id"] is not None) else None
    if source_canister_location == 0 or dest_canister_location == 0:
        return error(1020)

    try:
        with db.transaction():
            # get canister records
            source_location_id = get_location_id_by_location_number_dao(device_id=source_device_id,
                                                                        location_number=source_canister_location)
            source_canister = db_get_canister_data_by_location_id_dao(location_id=source_location_id)
            try:
                dest_location_id = get_location_id_by_location_number_dao(device_id=dest_device_id,
                                                                          location_number=dest_canister_location)
                dest_canister = db_get_canister_data_by_location_id_dao(location_id=dest_location_id)

            except DoesNotExist as e:
                logger.info("No canister present for destination: {}".format(e))
                dest_canister = None

            # update records and create canister history record
            status1, _ = update_canister_movement(
                source_canister['id'], source_canister['drug_id'],
                dest_canister_location, dest_device_id, user_id, dest_zone_id
            )
            if dest_canister is not None:
                # If destination has canister update destination canister
                status2, _ = update_canister_movement(
                    dest_canister['id'], dest_canister['drug_id'],
                    source_canister_location, source_device_id,
                    user_id, source_zone_id
                )

                if status1 and status2:
                    return create_response(1)
            if dest_canister is None and status1:
                return create_response(1)
            raise DBUpdateFailedException
    except DoesNotExist as e:
        logger.error("error in transfer_canisters {}".format(e))
        return error(1020)
    except InternalError as e:
        logger.error("error in transfer_canisters {}".format(e))
        return error(2001)
    except DBUpdateFailedException:
        return create_response(0)  # one of the record didn't update so rollback and return 0


@validate(required_fields=["canister_id"])
@log_args_and_response
def get_canister_label(canister_info):
    """
    Generates canister label if not present, returns file name

    @param canister_info:
    :return: json
    """
    canister_id = canister_info["canister_id"]
    label_name = str(canister_id) + '.pdf'

    if 'regenerate' not in canister_info:  # flag to regenerate label forcefully
        # If file already exists return
        if blob_exists(label_name, canister_label_dir):
            logger.info("canister_label: label already exist on cloud")
            response = {'label_name': label_name}
            return create_response(response)

    if not os.path.exists(canister_dir):
        os.makedirs(canister_dir)
    label_path = os.path.join(canister_dir, label_name)

    try:
        canister = get_canister_by_id_dao(canister_id)
    except (IntegrityError, InternalError) as e:
        logger.error(e)
        return error(2001)

    try:
        logger.info('Starting Canister Label Generation. Canister ID: {}'.format(canister_id))

        if len(str(canister["rfid"])) <= 12:
            canister_version = "v2"
        else:
            canister_version = "v3"

        if not ('big_stick_serial_number' in canister_info or 'small_stick_serial_number' in canister_info or
                'drum_serial_number' in canister_info):
            big_stick_serial_number, small_stick_serial_number, drum_serial_number = \
                get_serial_number_from_canister_id(canister_id)
            canister_info['big_stick_serial_number'] = big_stick_serial_number
            canister_info['small_stick_serial_number'] = small_stick_serial_number
            canister_info['drum_serial_number'] = drum_serial_number

        generate_canister_label(file_name=label_path,
                                drug_name=canister["drug_name"],
                                ndc=str(canister["ndc"]),
                                strength=canister["strength"],
                                strength_value=canister["strength_value"],
                                canister_id=str(canister["canister_id"]),
                                manufacturer=canister['manufacturer'],
                                imprint=canister['imprint'],
                                color=canister['color'],
                                shape=canister['shape'],
                                form=canister['drug_form'],
                                canister_version=canister_version,
                                drug_shape_name=canister['drug_shape_name'],
                                big_canister_stick_id=canister['big_canister_stick_id'],
                                small_canister_stick_id=canister['small_canister_stick_id'],
                                product_id=canister['product_id'],
                                big_stick_serial_number=canister_info['big_stick_serial_number'],
                                small_stick_serial_number=canister_info['small_stick_serial_number'],
                                lower_level=canister['lower_level'],
                                drum_serial_number=canister_info['drum_serial_number'],
                                company_id=canister["company_id"])
        create_blob(label_path, label_name, canister_label_dir)  # Upload label to central storage
        logger.info('Canister Label Generated. Canister ID: {}'.format(canister_id))
        response = {'label_name': label_name, 'canister_version': canister_version}
        # CanisterMaster.update(label_print_time=get_current_date_time()).where(
        #     CanisterMaster.id == canister_id).execute()
        db_update_canister_master_label_print_time(canister_id)

        logger.info("get_canister_label response {}".format(response))
        return create_response(response)
    except Exception as e:
        logger.error('Canister Label Generation Failed: ' + str(e), exc_info=True)
        return error(2006)
    finally:
        remove_files([label_path])


@log_args_and_response
def get_canister_data_from_oddo_product_id(product_id, company_id, flag=False):
    token_request_data = {
        'username': settings.INVENTORY_USERNAME,
        'password': settings.INVENTORY_PASSWORD,
        'db': settings.INVENTORY_DATABASE_NAME
    }
    ACCESS_TOKEN = call_webservice(settings.BASE_URL_INVENTORY, settings.GET_ACCESS_TOKEN,
                                   token_request_data,
                                   request_type="POST", odoo_api=True, use_ssl=settings.ODOO_SSL)
    if not ACCESS_TOKEN \
            or not ACCESS_TOKEN[0] or 'error' in ACCESS_TOKEN[1]:
        return error(4003)
    ACCESS_TOKEN = ACCESS_TOKEN[1]['access_token']
    logger.info(ACCESS_TOKEN)
    data_dict = {"odoo_product_id": product_id,
                 "customer_id": company_id}
    data = call_webservice(settings.BASE_URL_INVENTORY, settings.GET_CANISTER_DATA_FROM_ODOO_PRODUCT_ID,
                           data_dict, request_type="POST", use_ssl=settings.ODOO_SSL,
                           headers={"Authorization": ACCESS_TOKEN}, odoo_api=True)
    logger.info("data {}".format(data))
    big_stick_serial_number = data[1]['big_stick_serial_number']
    small_stick_serial_number = data[1]['small_stick_serial_number']
    drum_serial_number = data[1]['drum_serial_number']
    logger.info("bs_Serial_number {}, ss_serial_number {}, drum_serial_number is {}.".format(
        big_stick_serial_number, small_stick_serial_number, drum_serial_number))
    if flag:
        canister_detail: Dict[str, int] = dict()
        canister_detail['big_stick_width'] = data[1]['big_stick_width']
        canister_detail['big_stick_depth'] = data[1]['big_stick_depth']
        canister_detail['small_stick_length'] = data[1]['small_stick_length']
        canister_detail['drum_width'] = data[1]['drum_width']
        canister_detail['drum_depth'] = data[1]['drum_depth']
        canister_detail['drum_length'] = data[1]['drum_length']
        return big_stick_serial_number, small_stick_serial_number, drum_serial_number, canister_detail
    else:
        return big_stick_serial_number, small_stick_serial_number, drum_serial_number


@log_args_and_response
def get_external_canister_data(data_dict):
    try:
        response = inventory_api_call(api_name=settings.GET_EXTERNAL_CANISTER_DATA, data=data_dict)
        logger.info("response {}".format(response))
        # if not status:
        #     return False, response
        canister_serial_number = response['canister_serial_number']
        company_id = data_dict["customer_id"]
        status, json_response_data = get_canister_data_by_serial_number_v3(canister_serial_number, company_id)
        response_data = json.loads(json_response_data)
        if not status:
            return False, response_data
        return True, response_data["data"]["canister_data"]

    except (InventoryBadRequestException, InventoryDataNotFoundException, InventoryBadStatusCode,
            InventoryConnectionException, InvalidResponseFromInventory) as e:
        raise e


@log_args_and_response
def get_canister_data_by_serial_number_v3(canister_serial_number, company_id):
    canister_data = {
        "canister_serial_number": canister_serial_number,
        "customer_id": company_id
    }
    try:
        canister_data = inventory_api_call(api_name=settings.GET_CANISTER_DATA, data=canister_data)

        if not canister_data.get('ndc##txr'):
            raise InvalidResponseFromInventory(canister_data)

    except (InventoryBadRequestException, InventoryDataNotFoundException, InventoryBadStatusCode,
            InventoryConnectionException, InvalidResponseFromInventory) as e:
        raise e

    try:
        query = get_canister_data_by_serial_number_v3_dao(canister_data=canister_data)
    except DoesNotExist as e:
        logger.error("error in get_canister_data_by_serial_number_v3: {}".format(e))
        return False, error(1014)

    response = {
        "drug_data": {
            "fillet": canister_data['fillet'],
            "shape": canister_data['shape'],
            "length": float(canister_data['length']) if len(canister_data['length']) > 0 else canister_data['length'],
            "width": float(canister_data['width']) if len(canister_data['width']) > 0 else canister_data['width'],
            "depth": float(canister_data['depth']) if len(canister_data['depth']) > 0 else canister_data['depth']
        },
        "small_stick_length": float(canister_data["small_stick_length"]) if len(canister_data['small_stick_length']) > 0
        else canister_data['small_stick_length'],
        "big_stick_width": float(canister_data["big_stick_width"]) if len(canister_data['big_stick_width']) > 0
        else canister_data['big_stick_width'],
        "big_stick_serial_number": canister_data["big_stick_serial_number"],
        "big_stick_depth": float(canister_data["big_stick_depth"]) if len(canister_data['big_stick_depth']) > 0
        else canister_data['big_stick_width'],
        "product_id": int(canister_data["odoo_product_id"]),
        "rfid": canister_data["canister_rfid"],
        "ndc": query["ndc"],
        "drug_id": query["id"],
        "drug_name": query["drug_name"],
        "canister_type": canister_data.get("canister_type", "REGULAR")
    }

    logger.info("get_canister_data_by_serial_number_v3 response {}".format(response))
    return True, create_response({"canister_data": response})


@log_args_and_response
def api_callback(args):
    try:
        # args = '{\"status\":\"success\",\"station_type\":\"56000\",\"station_id\":\"56001\",\"msg_id\":\"0\",\"resp_code\":\"11101\",\"data\":{\"5\":\"123654\"}}'
        callback_data = json.loads(args)
    except:
        try:
            callback_data = eval(args)
        except:
            logger.error(1001, "api_callback - Exception: ")
            return create_response(False)

    response = update_rfid_in_couchdb(callback_data)
    if response:
        return create_response(response)
    else:
        return error(1000, "Unable to update data in couch db.")


@log_args_and_response
def update_canister_ndc_multiple(args: dict):
    """

    @param args:
    @return:
    """
    system_id = args['system_id']
    company_id = args['company_id']
    user_id = args['user_id']
    # canister_id_list = ['canister_id_list']
    ndc_canister_list = (args['ndc_canister_list'])
    tested_canister = args.get('tested_canister', None)
    response_list = list()

    try:
        for ndc, canister_list in ndc_canister_list.items():
            for canister_id in canister_list:
                logger.info("update_canister_ndc_multiple canister {}".format(canister_id))
                canister_data = get_canister_details_by_canister_id(canister_id=canister_id)
                rfid = canister_data['rfid']
                response = update_canister_ndc({"system_id": system_id,
                                                "company_id": company_id,
                                                "user_id": user_id,
                                                "ndc": ndc,
                                                "rfid": rfid,
                                                "multiple_ndc_call": True,
                                                "ignore_location": True,
                                                "canister_id": canister_id,
                                                "tested_canister": tested_canister})
                logger.info("response of update_canister_ndc_multiple {} for ndc {} and canister {}".format(response,
                                                                                                            ndc,
                                                                                                            canister_id))
                response_list.append(response)

        return create_response(response_list)

    except InventoryDataNotFoundException as e:
        logger.error("Error in update_canister_ndc_multiple {}".format(e))
        return error(1000, "Error in update_canister_ndc_multiple: " + str(e))

    except Exception as e:
        logger.info("Error in update_canister_ndc_multiple {}".format(e))
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_canister_ndc_multiple: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(9017)


@validate(required_fields=["ndc", "rfid", "user_id"])
@log_args_and_response
def update_canister_ndc(args: dict) -> str:
    """
    Function to add new canister in canister master for given drug and
    delete (rfid = null) for  given canister id
    @param args:
    @return:
    """
    system_id = args['system_id']
    company_id = args['company_id']
    ndc = str(args['ndc'])
    rfid = args['rfid']
    user_id = args['user_id']
    multiple_ndc_call = args.get('multiple_ndc_call', False)
    ignore_location = args.get("ignore_location", False)
    print_label = args.get('print_label', True)
    # tested_canister = args.get("tested_canister")
    # old_canister_id = args.get("canister_id")
    try:
        # get drug info from given NDC
        drug_info_for_ndc = get_drug_info_based_on_ndc_dao(ndc_list=[ndc])[ndc]
        logger.info("update_canister_ndc drug info {}".format(drug_info_for_ndc))
        drug_id = drug_info_for_ndc['id']

    except Exception as e:
        logger.info("Error in update_canister_ndc {}".format(e))
        return error(9017)

    try:
        # get zone from given system id
        zone_id = get_zone_by_system(system_id)
        logger.info("update_canister_ndc zone_id {}".format(zone_id))

        with db.transaction():
            canister_data = {"drug_id": drug_id,
                             "expiration_date": args.get("expiration_date", None),
                             "lot_number": args.get("lot_number", None),
                             "quantity": args.get('quantity', 0),
                             "system_id": system_id,
                             "company_id": company_id,
                             "user_id": user_id,
                             "rfid": rfid,
                             "batch_id": None,
                             "device_id": None,
                             "zone_id": zone_id,
                             "ignore_location": ignore_location}

            # mark rfid null in existing canister and add new record in canister related tables
            canister_add_response = replace_canister(canister_data=canister_data)
            loaded_response = json.loads(canister_add_response)
            logger.info("update_canister_ndc replace_canister response {}".format(loaded_response))

            if loaded_response['status'] == settings.SUCCESS_RESPONSE:
                # update canister details in the ODOO Inventory
                data_dict = {"canister_product_id": loaded_response["data"]["product_id"],
                             "old_canister_id": loaded_response["data"]["existing_canister_id"],
                             "new_canister_id": loaded_response["data"]["canister_id"],
                             "new_drug_name": drug_info_for_ndc["drug_name"],
                             "new_fndc": drug_info_for_ndc["formatted_ndc"],
                             "new_txr": drug_info_for_ndc["txr"],
                             "is_activated": False,
                             "is_drug_ndc_txr_change": True,
                             "is_canister_type_change": False,
                             "customer_id": company_id}

                odoo_response = inventory_api_call(api_name=settings.UPDATE_CANISTER_DATA_IN_INVENTORY, data=data_dict)
                logger.info(odoo_response)

                # update new canister id in canister_testing_status table (where canister id is same as old canister id)
                status = update_canister_testing_status(new_canister_id=loaded_response["data"]["canister_id"],
                                                        old_canister_id=loaded_response["data"]["existing_canister_id"])
                logger.info("In update_canister_ndc: update_canister_testing_status status: {}".format(status))
                # generate canister label for new canister_id(only for tested canister)
                args['canister_id'] = loaded_response['data']['canister_id']
                # if old_canister_id == tested_canister:
                if print_label:
                    response = get_canister_label(args)
                if multiple_ndc_call:
                    return data_dict
                return response
            else:
                return canister_add_response

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in update_canister_ndc {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_canister_ndc: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise error(2001)

    except InventoryDataNotFoundException as e:
        logger.error("Error in update_canister_ndc {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_canister_ndc: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in update_canister_ndc {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_canister_ndc: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise error(1000, "Error in update_canister_ndc: " + str(e))


@validate(required_fields=["system_id", "device_id", "company_id"])
@log_args_and_response
def get_skipped_canister_during_replenish(args: dict):
    """
    This function returns canister with replenish qty, required qty, drug details with current and destination location details
    :param args:
    :return:
    """
    try:
        logger.info(f"Inside get_skipped_canister_during_replenish, args: {args}")

        # batch_id = args.get("batch_id", None)
        device_id: int = args["device_id"]
        system_id: int = args["system_id"]

        response_canister_dict: dict = dict()
        response_canister_list = list()
        progress_pack_ids = None


        # progress_pack_ids = db_get_progress_filling_left_pack_ids(batch_id=batch_id)
        #
        # logger.info(f"In get_skipped_canister_during_replenish, progress_pack_ids: {progress_pack_ids}")

        skipped_canister = get_skipped_replenish_canister(system_id=system_id,
                                                           device_id=device_id)

        logger.info(f"In get_skipped_canister_during_replenish, skipped_canister: {skipped_canister}")

        if not skipped_canister:
            # if there are not any skipped canister for this batch and given device id >> no need for further process
            return create_response(skipped_canister)

        skipped_replenish_canister_query = get_skipped_replenish_query(system_id=system_id,
                                                                       device_id=device_id,
                                                                       progress_pack_ids=progress_pack_ids,
                                                                       skipped_canister=skipped_canister)

        for record in skipped_replenish_canister_query:

            logger.info(
                f"In get_skipped_canister_during_replenish, record from skipped_replenish_canister_query: {record}")

            if record['location_number'] == None:
                record['location_number'] = 0

            if not response_canister_dict.get(record['canister_id'], None):
                # record['current_batch_replenish_required_quantity'] = float(abs(record['replenish_qty']))
                record['current_batch_required_quantity'] = float(abs(record['required_qty']))
                response_canister_dict[record['canister_id']] = record

            else:
                response_canister_dict[record['canister_id']]['current_batch_required_quantity'] += float(
                    abs(record['required_qty']))

            # fetch canister capacity based on approx_volume of drug
            if record['approx_volume'] is None:
                response_canister_dict[record['canister_id']]['canister_capacity'] = None
            else:
                canister_volume = get_canister_volume(canister_type=record['canister_type'])
                response_canister_dict[record['canister_id']][
                    'canister_capacity'] = get_max_possible_drug_quantities_in_canister(
                    canister_volume=canister_volume,
                    unit_drug_volume=record['approx_volume'])

            logger.info(
                f"In get_skipped_canister_during_replenish,canister:{response_canister_dict[record['canister_id']]}, approx_volume: {record['approx_volume']}")

            response_canister_dict[record['canister_id']].setdefault("batch_required_quantity", float(abs(record['required_qty'])))
            response_canister_dict[record['canister_id']].setdefault("replenish_required_quantity", float(abs(record['replenish_qty'])))

            del record['approx_volume']
            del record['replenish_qty']
            del record['required_qty']

        skipped_replenish_canister_query = get_skipped_replenish_query(system_id=system_id,
                                                                       device_id=device_id,
                                                                       progress_pack_ids=progress_pack_ids,
                                                                       skipped_canister=skipped_canister,
                                                                       all_packs=True)

        for data in skipped_replenish_canister_query:
            response_canister_dict[data['canister_id']]['batch_required_quantity'] = float(abs(data['required_qty']))
            response_canister_dict[data['canister_id']]['replenish_required_quantity'] = float(
                    abs(data['replenish_qty']))

        # sort data using pack order no
        if response_canister_dict:
            response_canister_list = sorted(list(response_canister_dict.values()), key=lambda index: index['pack_order_no'])

        return create_response(response_canister_list)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_skipped_canister_during_replenish {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_skipped_canister_during_replenish: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)
    except Exception as e:
        logger.error("error in get_skipped_canister_during_replenish {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_canister_ndc: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_skipped_canister_during_replenish: " + str(e))


@log_args_and_response
def revert_replenish_skipped_canister(args: dict):
    try:
        logger.info("Inside revert_replenish_skipped_canister")

        canister_id = args["canister_id"]
        system_id = args["system_id"]
        device_id = args["device_id"]
        company_id = args["company_id"]
        user_id = args["user_id"]
        batch_id = None
        status = None
        progress_batch_id = None

        if not batch_id:
            # get progress batch_id
            progress_batch_id = get_progress_batch_id(system_id)

        pack_analysis_details_update_status, reverted_packs, system_device = update_status_in_pack_analysis_details(
            canister_id=[canister_id], company_id=company_id, device_id=device_id)
        logger.info(
            f"In revert_replenish_skipped_canister, pack_analysis_details_update_status:{pack_analysis_details_update_status}")

        if reverted_packs:

            logger.info(f"In revert_replenish_skipped_canister, remove reverted pack-canister")
            remove_status = remove_pack_canister_from_replenish_skipped_canister(pack_ids=list(reverted_packs),
                                                                                 canister_id=canister_id)
            # current_batch_id = get_import_batch_id_from_system_id_or_device_id(system_id=system_id)
            # logger.info(f"In revert_replenish_skipped_canister, current_batch_id: {current_batch_id}")

            status = update_batch_change_tracker_after_replenish_skipped_canister(canister_id=canister_id,
                                                                                  user_id=user_id,
                                                                                  device_id=device_id,
                                                                                  reverted_packs=reverted_packs)
            logger.info(f"In revert_replenish_skipped_canister, batch_change_tracker update status:{status}")

        if progress_batch_id:
            reverted_packs = revert_canister_usage_by_recom(company_id=company_id, device_id=device_id,
                                                            canister_id=canister_id,
                                                            affected_pack_list=reverted_packs,
                                                            batch_id=progress_batch_id)

        """
        commented the below code as now we don't remove the canister from the reserved_canister table when we skip
        so to prevent the multiple data entry there is no need to add the data entry of skipped_canister
        """
        # if canister_id:
        #     canister_data = {progress_batch_id: [canister_id]}
        #     insert_records_in_reserved_canister(canister_data=canister_data)
        #     logger.info("Inserted data into reserved_canister, canister data {}".format(canister_data))

        logger.info("In revert_replenish_skipped_canister, updating replenish-mini-batch couchdb")
        update_replenish_based_on_system(system_id)

        if status:
            return create_response(True)
        else:
            return create_response(False)

    except (IntegrityError, InternalError, DataError) as e:

        logger.error("Error in revert_replenish_skipped_canister {}".format(e))

        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in revert_replenish_skipped_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:

        logger.error("error in revert_replenish_skipped_canister {}".format(e))

        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in revert_replenish_skipped_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in revert_replenish_skipped_canister: " + str(e))


@log_args_and_response
def initiate_replenish_update(args):
    try:
        pack_id = args.get('pack_id')
        device_id = args.get('device_id')
        if pack_id is None or device_id is None:
            return error(1001, "Missing Parameter(s): pack_id or device_id.")

        logger.info("Replenish Update after Slot Transaction for pack id {} initiated.".format(pack_id))
        update_replenish_based_on_device(device_id)
    except Exception as e:
        logger.error("In initiate_replenish_update. Error: {}".format(e))

    return create_response(1)


@validate(required_fields=["company_id"])
@log_args_and_response
def get_drug_active_canister(dict_info):

    ''' This function returns list of active canisters for each drug '''

    try:
        company_id = int(dict_info['company_id'])
        drug_canister_dict = {
            'fndc_cfi_list': list()
        }
        logger.info("Getting active canisters for drugs")
        for drug in get_drug_active_canister_dao(company_id):
            drug_canister_dict['fndc_cfi_list'].append({
                'fndc': drug['formatted_ndc'],
                'cfi': drug['txr']
            })

        return create_response(drug_canister_dict)
    except Exception as e:
        logger.error("In get_drug_active_canister. Error: {}".format(e))
        return error(1000, "Error in get_drug_active_canister: " + str(e))


@log_args_and_response
def discard_expired_canister_drug(dict_info):
    try:
        logger.info("In discard_expired_canister_drug")
        token = get_token()
        logger.debug("fetching_user_details")
        user_details = get_current_user(token=token)
        company_id = dict_info["company_id"]
        canister_id = dict_info["canister_id"]
        quantity = dict_info.get("quantity")
        user_id = dict_info["user_id"]
        robot_utility_call = dict_info.get("robot_utility_call")
        device_id = dict_info.get("device_id")
        system_id = dict_info.get("system_id")

        # ________________ validation : given canister must be expired.
        canister_expiry_status, expiry_date = get_canister_expiry_status(canister_id=canister_id,company_id=company_id)
        if quantity is None:
            quantity = get_available_quantity_in_canister(canister_id=canister_id)
        if canister_expiry_status is None or canister_expiry_status != constants.EXPIRED_CANISTER:

            if not quantity:
                logger.error(f"Error in discard_expired_canister_drug: given canister is already discarded.")
                return error(3021)
            else:
                logger.error(f"Error in discard_expired_canister_drug: given canister is not expired.")
                return error(3022)

        with db.transaction():
            # _____________1: update canister quantity to Zero and expiry date to null___________
            update_dict = {"expiry_date": None,
                           "available_quantity": 0}
            logger.info(f"In discard_expired_canister_drug, updating canister master")
            status = update_canister_dao(update_dict=update_dict, id=canister_id)

            # ____________canister tracker changes
            # --> need to update canister_tracker usage_consideration_status : if it is pending or progress >> trash

            epbm_data = discard_canister_tracker(canister_id=canister_id, quantity=quantity, user_id=user_id)

            # ___________________elite pbm call_____________________
            if settings.SEND_EXPIRED_DRUG_TO_INVENTORY:
                epbm_list = []
                if epbm_data:
                    for ndc, lot_number_info in epbm_data.items():
                        for lot, info in lot_number_info.items():
                            epbm_list.append({"ndc": ndc,
                                              "trash_qty": info['trash_qty'],
                                              "lot_number": lot,
                                              "expiry_date": info['expiry_date'],
                                              "note": info['note'],
                                              "case_id": info["case_id"]})

                    args = {"transaction_type": settings.EPBM_EXPIRY,
                            "expiry_list": epbm_list,
                            "user_details": user_details,
                            "is_replenish": True}
                    # drug_inventory_adjustment(args)
                    logger.info(f"In discard_expired_canister_drug, connect to epbm")
                    exception_list = list()
                    threads = list()
                    t = ExcThread(exception_list, target=drug_inventory_adjustment,
                                  args=[args])
                    threads.append(t)
                    t.start()

        if robot_utility_call:
            if device_id and system_id:
                data_dict = {
                    'system_id': system_id,
                    'device_id': device_id,
                }
                response = get_replenish_mini_batch_wise(data_dict)
                logger.info(f"1 In discard_expired_canister_drug, replenish mini batch doc updated response: {response}")
        if not robot_utility_call:
            update_req, device_id, system_id = check_canister_uses_in_pack_queue(canister_id=canister_id)
            if update_req:
                data_dict = {
                    'system_id': system_id,
                    'device_id': device_id,
                }
                response = get_replenish_mini_batch_wise(data_dict)
                logger.info(f"2 In discard_expired_canister_drug, replenish mini batch doc updated response: {response}")
        response = {"status": status, "expiry_date": expiry_date.strftime("%m-%Y") if expiry_date else expiry_date}
        return create_response(response)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in discard_expired_canister_drug {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in discard_expired_canister_drug: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("error in discard_expired_canister_drug {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in discard_expired_canister_drug: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in discard_expired_canister_drug: " + str(e))

#
# @log_args_and_response
# def get_expired_canister(args):
#     try:
#         logger.info("In get_expired_canister")
#
#         company_id = args["company_id"]
#         device_id = args.get("device_id")
#
#         response = []
#
#         canister_query = get_expired_canister_data_dao(company_id, device_id)
#
#         for data in canister_query:
#             pass
#
#     except Exception as e:
#         pass


@log_args_and_response
def get_canisters_by_pack_ndc(company_id, ndc, pack_id=None, mfd_analysis_ids=None):
    try:

        canister_list = get_same_or_alternate_canister_by_pack(company_id, ndc, pack_id, mfd_analysis_ids)

        return create_response(canister_list)

    except Exception as e:
        logger.error("error in get_canisters_by_pack_ndc {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error in get_canisters_by_pack_ndc: exc_type - {exc_type}, filename - {filename}, line - "
            f"{exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def check_valid_canister(ndc_list, canister_id):
    """
    This function is used to check given canister is valid or not with given recommended canisters list for that ndc.
    """
    try:
        canister_data = get_recommended_canisters(ndc_list)
        canister_data = json.loads(canister_data)
        canister_data = canister_data['data']['canister_data']
        canister_list = [item['canister_id'] for item in canister_data]
        if int(canister_id) in canister_list:
            return create_response(settings.SUCCESS_RESPONSE)
        else:
            return error(21013)

    except Exception as e:
        logger.error("In check_valid_canister. Error: {}".format(e))
        return error(1000, "Error in check_valid_canister: " + str(e))


@log_args_and_response
def get_recommended_canisters(ndc_list=None, filters=None, paginate=None, sort_fields=None):
    """
    In this api user can see the recommended canisters list for given ndc which is decided by dimensions of drugs
    and available canisters.
    """
    try:
        canister_list = []
        ndc_list = json.loads(ndc_list)
        canisters_df = get_canister_stick_details(ndc_list)
        if type(canisters_df) == str:
            return canisters_df
        canister_ids = canisters_df['Recommended_Canister_Id']
        for id in canister_ids:
            canister_list.extend(json.loads(id))
        # this canister list which is compatible with given ndc
        canister_list = list(set(canister_list))

        canisters_data_list, drug_list, total_count = get_canister_data_by_canister_ids(canister_list, filters, paginate, sort_fields)

        if not ndc_list:
            canisters_data_list = []
        response_data = {
            "canister_data": canisters_data_list,
            "drug_list": drug_list,
            "canister_list": canister_list,
            "total_count": total_count
        }
        return create_response(response_data)

    except Exception as e:
        logger.error(f"error occured in get_recommended_canisters {e}")
        return e


@log_args_and_response
def order_canisters(args):
    """
    This api is used to order new canisters and creates entry in canister_orders table
    """
    try:
        drug_list = args.get('drug_list')
        user_id = args.get('user_id')
        canister_order_list = []
        for item in drug_list:
            canister_order_dict = {
                "drug_id": item,
                "created_by": user_id
            }
            canister_order_list.append(canister_order_dict)
        status = db_create_canister_orders(canister_order_list)
        return create_response(constants.SUCCESS_RESPONSE)

    except Exception as e:
        logger.error(f"error occured in order_canisters {e}")
        return e


@log_args_and_response
def get_canister_order_history(filter_fields, paginate, sort_fields):
    """
    Function to get canister order history from filter fields .
    """
    try:
        response_data, drug_list, count = get_canister_order_history_dao(filter_fields, sort_fields, paginate)
        response_dict = {"canister_order_history": response_data,
                         "drug_list": drug_list,
                         "total_count": count,
                         "status_list": constants.ORDER_STATUS_LIST}
        return create_response(response_dict)
    except Exception as e:
        logger.error(f"error occured in get_canister_order_history {e}")
        return e


@log_args_and_response
def send_email_for_ordering_canisters(company_id):
    try:
        response_list = get_data_for_order_canister()
        response_dict = {}
        ndc_list = []
        for record in response_list:
            ndc_list.append(record['ndc'])
            response_dict[record["order_id"]] = {
                "ndc": record['ndc'],
                "drug_name": record['drug_name'],
                "fndc": str(record['formatted_ndc']),
                "txr": record['txr'],
                "strength": record['strength'],
                "strength_value": record['strength_value'],
                "width": float(record['width']),
                "depth" : float(record['depth']),
                "length": float(record['length']),
                "fillet": float(record['fillet']),
                "shape": record["shape"]
            }
        canister_data = get_canister_stick_details(ndc_list, file_needed=True)

        file_list = ["Molding.xlsx", "Printed_3d.xlsx"]
        valid_file_set = set()
        files = {}
        for file in file_list:
            # Load the workbook
            workbook = openpyxl.load_workbook(file)

            # Select the worksheet
            worksheet = workbook['Sheet1']  # Replace 'Sheet1' with the name of your desired sheet

            # Iterate through the rows and columns
            for row in worksheet.iter_rows(values_only=True):
                for cell in row:
                    valid_file_set.add(file)
                    break
        count = 1
        for file in valid_file_set:
            files["file_"+str(count)] = (file, open(settings.FILE_PATH_MAPPING[file], "rb"))
            count += 1

        status, data = call_webservice(settings.BASE_URL_AUTH, settings.CANISTER_ORDER_MAIL,
                                       parameters=json.dumps({"response_dict": response_dict, "company_id": company_id}),
                                       use_ssl=settings.AUTH_SSL,
                                       request_type="POST",
                                       files=files
                                       )
        return create_response(status)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in send_email_for_ordering_canisters {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in z: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1040)
    except Exception as e:
        logger.error("error in send_email_for_ordering_canisters {}".format(e))


@log_args_and_response
def update_canister_master(dict_canister_info):
    try:
        canister_id = dict_canister_info.get("canister_id")
        available_quantity = int(dict_canister_info.get("quantity"))
        company_id = dict_canister_info.get("company_id")

        canister_info = db_get_canister_info(canister_id, company_id)

        current_quantity = canister_info['available_quantity']

        diff = available_quantity - current_quantity

        with db.transaction():
            status = db_update_canister_quantity(canister_id, available_quantity)

            status, case_quantity_dict = db_update_canister_tracker(canister_id, diff)

            if case_quantity_dict:

                args = {
                    "ndc": canister_info['canister_ndc'],
                    "adjusted_quantity": diff if diff > 0 else diff * (-1),
                    "company_id": company_id,
                    "is_replenish": True,
                    "transaction_type": settings.EPBM_QTY_ADJUSTMENT_KEY,
                    "case_quantity_dict": case_quantity_dict
                }
                response = inventory_adjust_quantity(args)

        return create_response(constants.SUCCESS_RESPONSE)

    except Exception as e:
        return e
