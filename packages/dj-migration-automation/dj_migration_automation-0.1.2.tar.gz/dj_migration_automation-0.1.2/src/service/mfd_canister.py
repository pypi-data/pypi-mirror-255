import json
import os
import sys
from collections import defaultdict
from uuid import uuid1

import couchdb
from peewee import *
from peewee import InternalError, IntegrityError, DataError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import (create_response, error)
from dosepack.utilities.utils import (log_args_and_response, get_current_date_time, validate_rfid_checksum,
                                      get_current_modified_datetime, log_args, retry_exception)
from dosepack.validation.validate import validate
from src.label_printing.canister_label import generate_mfd_canister_label, mfd_canister_dir
from src.label_printing.generate_label import remove_files
from realtime_db.dp_realtimedb_interface import Database
from src import constants
from src.cloud_storage import blob_exists, create_blob, mfd_canister_label_dir
from src.dao.couch_db_dao import get_couch_db_database_name, get_document_from_couch_db
from src.dao.device_manager_dao import get_active_mfd_trolley, get_container_data_based_on_serial_numbers_dao, \
    get_device_data_by_device_id_dao
from src.dao.mfd_canister_dao import (add_data_in_mfd_canister_master, get_device_mfd_trolley_data,
                                      get_trolley_drawer_query,
                                      get_drawer_canister_data_query, get_mfd_canister_data_query,
                                      get_mfd_trolley_drawer_data, duplicate_rfid_check,
                                      get_device_id_from_serial_number, get_drawer_id_from_serial_number,
                                      get_mfd_canister_data_by_id, update_mfd_canister,
                                      get_mfd_canister_home_cart_count,
                                      db_get_mfd_analysis_details_ids,
                                      get_unique_rts_filters,
                                      get_mfd_rts_canisters, get_mfd_non_rts_canisters,
                                      fetch_empty_trolley_locations_for_rts_canisters,
                                      fetch_empty_locations_of_mfd_container,
                                      get_canister_data_by_rfid, get_canister_data_by_location_id,
                                      update_mfd_canister_location, get_empty_drawers_for_locations_dao,
                                      get_home_cart_data_for_mfd_canister_in_robot, get_mfd_canister_master_filters,
                                      db_get_rts_drugs, check_drop_pending, mfd_misplaced_canister_dao,
                                      get_latest_record_by_canister_id, update_mfd_canister_transfer_data,
                                      add_mfd_canister_history, update_mfd_canister_location_with_fork,
                                      mfd_misplaced_canister_transfer_to_robot, db_mark_mfd_canister_activate,
                                      get_mfd_canister_data_by_ids,
                                      db_update_canister_active_status, mark_mfd_canister_misplaced,
                                      get_latest_mfd_status_history_data, get_unique_rts_actions,
                                      db_get_canister_transfer_info,
                                      db_get_rts_required_canisters, check_trolley_seq_for_batch)
from src.dao.mfd_dao import (get_empty_location_by_drawer,
                             get_empty_location_by_trolley, get_empty_drawer_device, get_empty_locations,
                             db_get_rts_required_canister_count, db_update_drug_status, db_update_canister_status,
                             associate_canister_with_analysis, get_current_mfs_batch_data,
                             update_mfd_rts_count_in_couch_db, update_mfd_transfer_couch_db)
from src.exceptions import (InvalidResponseFromInventory, InventoryBadRequestException, InventoryDataNotFoundException,
                            InventoryBadStatusCode, InventoryConnectionException, RealTimeDBException)
from src.service.misc import update_document_with_revision, get_mfd_transfer_couch_db
from utils.inventory_webservices import inventory_api_call

logger = settings.logger


@log_args_and_response
def get_trolley_drawer_from_serial_number_mfd(trolley_serial_number, drawer_serial_number, company_id):
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

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return None, None
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in getting device from serial number")


@log_args_and_response
def get_mfd_trolley_data(args):
    """
    Function for mfd transfer to robot flow
    @param args: dict
    @return: json
    """
    device_id = args['device_id']
    batch_id = args['batch_id']
    system_id = args['system_id']
    company_id = args['company_id']
    # default value is true to remove dependency from FE
    drawer_scanned = args.get('drawer_scanned', True)
    trolley_serial_number = args.get('trolley_serial_number', None)
    user_id = args.get('user_id', None)
    drawer_serial_number = args.get('drawer_serial_number', None)
    scanned_drawer_serial_number = args.get('scanned_drawer_serial_number', None)
    recommended_empty_drawers = dict()
    on_start = bool(int(args.get("on_start", 0)))

    try:
        if on_start:
            logger.info("updating transfer action_taken_by in couch db doc mfd_notifications.")
            couchdb_update_status = update_mfd_transfer_sent_notification(system_id=system_id, device_id=device_id,
                                                                          user_id=user_id)
            logger.info("couch db notification action taken by update status: " + str(couchdb_update_status))

        # case when transfer to robot trolley are required for device
        if not trolley_serial_number:
            logger.info("get_mfd_trolley_data: device_id: {} no trolley_serial_no from FE".format(device_id))
            trolley_list = get_trolley_associated_with_device(device_id=device_id, batch_id=batch_id)
            logger.info("get_mfd_trolley_data: device_id: {} trolley_list: {}".format(device_id, trolley_list))

            return create_response(trolley_list)

        trolley_id, drawer_id = get_trolley_drawer_from_serial_number_mfd(trolley_serial_number=trolley_serial_number,
                                                                          drawer_serial_number=drawer_serial_number,
                                                                          company_id=company_id)
        logger.info("In get_mfd_trolley_data, trolley_id {}, drawer_id {}".format(trolley_id, drawer_id))

        # case when transfer to robot drawer of specific trolley are required
        if trolley_serial_number and not drawer_serial_number:
            if not trolley_id:
                return error(1000, "Missing Parameter(s): trolley_id or Invalid trolley.")

            trolley_drawer_list, serial_number_list, drawer_highlight_serial_number = get_trolley_drawer_data(
                device_id=device_id, batch_id=batch_id, trolley_id=trolley_id,
                scanned_drawer_serial_number=scanned_drawer_serial_number)

            if drawer_highlight_serial_number:
                update_couch_db = update_canister_transfer_couch_db(
                    system_id, batch_id=batch_id, device_id=device_id, trolley_id=trolley_id,
                    drawer_serial_number=drawer_serial_number, transfer_flow=True,
                    drawer_highlight_serial_number=drawer_highlight_serial_number)
                logger.info("In get_mfd_trolley_data, Couch db status {}".format(update_couch_db))

                if not update_couch_db:
                    return error(9065)
            return create_response(trolley_drawer_list)

        # returns list of mfd canisters which are to be transferred for given trolley and drawer id's.
        if trolley_serial_number and drawer_serial_number:
            if not drawer_id:
                return error(1001, "Missing Parameter(s): drawer_id or Invalid drawer.")

            mfd_canister_list, transfer_count = get_drawer_canister_data(batch_id=batch_id, device_id=device_id,
                                                                         trolley_id=trolley_id, drawer_id=drawer_id)

            if mfd_canister_list:
                # count no. of canister transfers from trolley drawer to robot and recommend robot drawers
                # based on destination quadrant
                if "dest_quadrant" in mfd_canister_list[0]:
                    quadrant = mfd_canister_list[0]["dest_quadrant"]
                    recommended_empty_drawers = get_empty_drawers_for_locations_dao(
                        device_id=device_id, quadrant=quadrant, no_of_locations_required=transfer_count)

            # update transfer count in couch db when drawer is scanned
            if drawer_scanned:
                update_couch_db = update_canister_transfer_couch_db(system_id, batch_id=batch_id,
                                                                    device_id=device_id,
                                                                    trolley_id=trolley_id,
                                                                    drawer_id=drawer_id,
                                                                    drawer_serial_number=drawer_serial_number,
                                                                    transfer_flow=True)
                logger.info("In get_mfd_trolley_data, Couch db status {}".format(update_couch_db))

                if not update_couch_db:
                    return error(9065)

            if recommended_empty_drawers:
                recommended_empty_drawers = list(recommended_empty_drawers.values())

            response = {"transfer_data": mfd_canister_list,
                        "drawers_to_unlock": recommended_empty_drawers}

            logger.info("Output for get_mfd_trolley_data {}".format(response))
            return create_response(response)

    except InternalError as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except RealTimeDBException as e:
        logger.error(e)
        return error(11002, str(e))
    except Exception as e:
        logger.error(e)
        return error(1001, "Error in getting mfd trolley data.")


@log_args_and_response
def update_canister_transfer_couch_db(system_id, batch_id, device_id, trolley_id, drawer_id=None,
                                      drawer_serial_number=None, transfer_flow=True,
                                      drawer_highlight_serial_number=None):
    """
    Function to update canister transfer to robot data in couch db
    @param drawer_highlight_serial_number:
    @param transfer_flow:
    @param system_id: int
    @param batch_id: int
    @param device_id: int
    @param trolley_id: int
    @param drawer_id: int
    @param drawer_serial_number: int
    @return: Status
    """

    try:
        logger.info(
            "update_canister_transfer_couch_db {}, {}, {}, {}".format(device_id, batch_id, device_id, trolley_id))
        logger.info(drawer_id)
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = 'mfd_transfer_{}'.format(device_id)
        table = cdb.get(_id=id)

        logger.info("update_canister_transfer_couch_db previous table {}".format(table))
        if transfer_flow:
            if table is None:
                table = {"_id": id, "type": 'mfd_canister_transfer',
                         "data": {"scanned_drawer": drawer_id,
                                  "scanned_trolley": trolley_id,
                                  "currently_scanned_drawer_sr_no": drawer_serial_number,
                                  "previously_scanned_drawer_sr_no": None,
                                  "timestamp": get_current_date_time()}
                         }
                if drawer_highlight_serial_number:
                    table["data"]["previously_scanned_drawer_sr_no"] = None
                cdb.save(table)

            elif not len(table["data"]):
                table["data"] = {"scanned_drawer": drawer_id, "scanned_trolley": trolley_id,
                                 "currently_scanned_drawer_sr_no": drawer_serial_number,
                                 "previously_scanned_drawer_sr_no": None}
                cdb.save(table)

            else:
                scanned_drawer = table["data"].get("scanned_drawer", None)
                scanned_trolley = table["data"].get("scanned_trolley", None)
                currently_scanned_drawer_sr_no = table["data"].get("currently_scanned_drawer_sr_no", None)
                if drawer_highlight_serial_number and currently_scanned_drawer_sr_no and currently_scanned_drawer_sr_no != drawer_highlight_serial_number:
                    table["data"]["previously_scanned_drawer_sr_no"] = currently_scanned_drawer_sr_no
                if scanned_drawer != drawer_id or scanned_trolley != trolley_id:
                    if drawer_id:
                        table["data"]["scanned_drawer"] = drawer_id
                    table["data"]["scanned_trolley"] = trolley_id
                    if drawer_serial_number:
                        table["data"]["currently_scanned_drawer_sr_no"] = drawer_serial_number

                cdb.save(table)

            logger.info("update_canister_transfer_couch_db updated table {}".format(table))
            return True

        logger.info("update_canister_transfer_couch_db updated table {}".format(table))
        return False

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        raise RealTimeDBException("conflict_while_saving_document")
    except Exception as e:
        logger.error(e)
        raise RealTimeDBException('Couch db update failed while transferring canisters')


@log_args_and_response
def get_drawer_canister_data(batch_id, device_id, trolley_id, drawer_id):
    """
    Function to get canister data of given device drawer.
    @param batch_id: int
    @param device_id: int
    @param trolley_id: int
    @param drawer_id: int
    @return: list
    """
    try:
        transfer_count = 0
        canister_data = list()
        drawer_canister_query = get_drawer_canister_data_query(batch_id, device_id, trolley_id, drawer_id)
        for record in drawer_canister_query:
            canister_status = record['status_id']
            if canister_status not in [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                       constants.MFD_CANISTER_MVS_FILLING_REQUIRED]:
                record['rts_required'] = False
                record['mvs_filling_required'] = False
                if record['dest_device_id'] == record['current_device'] and \
                        record['dest_quadrant'] == record['current_quadrant'] and record['fork_detected']:
                    continue
                if record['trolley_location_id'] == record['current_location_id']:
                    transfer_count += 1
                    record['wrong_location'] = False
                    record['fork_detection_error'] = False
                else:
                    if record['dest_device_id'] == record['current_device'] and \
                            record['dest_quadrant'] == record['current_quadrant']:
                        record['wrong_location'] = False
                        record['fork_detection_error'] = True
                    else:
                        transfer_count += 1
                        record['fork_detection_error'] = not (record['fork_detected'])
                        record['wrong_location'] = True

            else:
                if record['device_type_id'] == settings.DEVICE_TYPES['Manual Canister Cart']:
                    continue
                if canister_status == constants.MFD_CANISTER_RTS_REQUIRED_STATUS:
                    record['rts_required'] = True
                    record['mvs_filling_required'] = False
                else:
                    record['rts_required'] = False
                    record['mvs_filling_required'] = True
                record['dest_trolley_drawer_name'] = record['trolley_drawer_name']

            canister_data.append(record)

        return canister_data, transfer_count

    except InternalError as e:
        logger.error(e)
        raise


@log_args_and_response
def get_trolley_drawer_data(device_id, batch_id, trolley_id, scanned_drawer_serial_number=None):
    """
    Function to get list of drawers of given trolley_id from which canisters
        are to be transferred to given device.
    @param device_id: int
    @param batch_id: int
    @param trolley_id: serial_number on scanning trolley
    @param scanned_drawer_serial_number: scanned drawer
    @return: list
    """
    trolley_drawer_list = list()
    highlight_drawer_added = False
    serial_number_list = list()
    drawer_highlight_serial_number = None
    trolley_drawer_query = get_trolley_drawer_query(device_id, batch_id, [trolley_id])
    for record in trolley_drawer_query:
        if record['serial_number'] not in serial_number_list:
            serial_number_list.append(record['serial_number'])
        if not highlight_drawer_added and scanned_drawer_serial_number and \
                record['serial_number'] == scanned_drawer_serial_number:
            highlight_drawer_added = True
            record["drawer_to_highlight"] = True
            drawer_highlight_serial_number = record['serial_number']
        else:
            record["drawer_to_highlight"] = False
        trolley_drawer_list.append(record)
    if not highlight_drawer_added and trolley_drawer_list:
        trolley_drawer_list[0]['drawer_to_highlight'] = True
        drawer_highlight_serial_number = trolley_drawer_list[0]['serial_number']

    return trolley_drawer_list, serial_number_list, drawer_highlight_serial_number


@log_args_and_response
def get_trolley_associated_with_device(device_id, batch_id):
    """
    Function to get trolley list from which canisters are to be transferred to given device
    @param device_id: int
    @param batch_id: int
    @return: dict
    """
    try:
        trolley_list = list()

        trolley_query, next_trolley_name, next_trolley = get_device_mfd_trolley_data(device_id, batch_id)
        for record in trolley_query:
            trolley_list.append(record)
        logger.info("trolley list {}".format(trolley_list))

        if len(trolley_list) or not next_trolley:
            return {"trolley_id": list(),
                    "drawer_data": list(),
                    "filling_pending": next_trolley_name}
        else:
            trolley_data = get_mfd_trolley_drawer_data(next_trolley)
            return {"trolley_id": next_trolley,
                    "serial_number": trolley_data[0]['device_serial_number'],
                    "trolley_name": next_trolley_name,
                    "drawer_data": trolley_data}

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["company_id", "mfd_canister_serial_number", "user_id"])
def add_mfd_canister(data_dict: dict) -> dict:
    """
    This Method adds the mfd canister data in the mfd_canister_master table and generate canister label.
    @param data_dict: data dict with required keys "company_id", "mfd_canister_serial_number", "user_id"
    @return: dict - generated label name and canister data
    """
    logger.info("Inside add_mfd_canister.")
    company_id = data_dict["company_id"]
    mfd_canister_serial_number = data_dict["mfd_canister_serial_number"]
    user_id = data_dict["user_id"]
    response = {"is_label_generated": False,
                "label_name": None,
                }
    try:
        # fetch rfid, product id from odoo based on mfd_canister_serial_number
        logger.info("fetching canister details from odoo based on mfd_canister_serial_number- "
                     + str(mfd_canister_serial_number))
        data = {"mfd_canister_serial_number": mfd_canister_serial_number,
                "customer_id": company_id}
        canister_data = inventory_api_call(api_name=settings.GET_MFD_CANISTER_DATA_FROM_INVENTORY, data=data)
        if not "mfd_canister_rfid" in canister_data or not "odoo_product_id" in canister_data:
            raise InvalidResponseFromInventory(canister_data)
        rfid = canister_data["mfd_canister_rfid"]
        product_id = canister_data["odoo_product_id"]
        logger.info("fetched canister data from odoo - " + str(canister_data))

        # validate rfid
        if not validate_rfid_checksum(rfid):
            return error(1022)

        # check for duplicate rfid if duplicate then return canister data
        duplicate_rfid_status, can_data = duplicate_rfid_check(rfid, input_args={
            "mfd_canister_serial_number": mfd_canister_serial_number})
        if duplicate_rfid_status:
            response["rfid"] = rfid
            response["mfd_canister_id"] = can_data["id"]
            response["product_id"] = product_id
            response["already_registered"] = True
            return create_response(response)

        with db.transaction():

            mfd_device_canister_count = dict()
            mfd_trolley_data = dict()
            home_found = False

            # get mfd home cart canister count
            mfd_can_device_query = get_mfd_canister_home_cart_count(company_id)
            for record in mfd_can_device_query:
                if record['home_cart_id'] and record['home_cart_id'] not in mfd_device_canister_count.keys():
                    mfd_device_canister_count[record['home_cart_id']] = record['mfd_canister_count']

            # get mfd trolley device data
            mfd_trolley_data_query = get_active_mfd_trolley(company_id)
            for record in mfd_trolley_data_query:
                if record['id'] not in mfd_trolley_data.keys():
                    mfd_trolley_data[record['id']] = record['name']
                if record['id'] not in mfd_device_canister_count.keys():
                    mfd_device_canister_count[record['id']] = 0

            # get home_cart for canister
            for home_device, canister_count in mfd_device_canister_count.items():
                if canister_count < constants.MFD_TROLLEY_CANISTER_CAPACITY:
                    home_cart_device = home_device
                    home_found = True
                    break

            if not home_found:
                return error(1000, "No MFD Trolley available.")

            # Add canister data in mfd_canister_master
            logger.info("adding canister data in mfd_canister_master")
            mfd_canister_data_dict = {
                "erp_product_id": int(product_id),
                "rfid": rfid,
                "user_id": user_id,
                "company_id": company_id,
                "home_cart": home_cart_device
            }
            mfd_canister_id = populate_mfd_canister_master(mfd_canister_data_dict)
            logger.info("Added canister data in mfd_canister_master with id: " + str(mfd_canister_id))

            db_update_canister_active_status({home_cart_device: [mfd_canister_id]}, constants.MFD_CANISTER_ADDED,
                                             user_id)

            # update mfd canister id in odoo
            logger.info("Updating mfd canister id in odoo")
            data = {"mfd_canister_id": mfd_canister_id,
                    "customer_id": company_id,
                    "product_id": product_id,
                    }
            odoo_response = inventory_api_call(api_name=settings.UPDATE_MFD_CANISTER_DATA_IN_INVENTORY, data=data)
            logger.info("updated mfd canister data in odoo with response: " + str(odoo_response))

        # generate mfd canister label
        label_response = json.loads(mfd_canister_label(data))
        if label_response["status"] == settings.SUCCESS_RESPONSE:
            response["is_label_generated"] = True
            response["label_name"] = label_response["data"]["label_name"]

        response["rfid"] = rfid
        response["mfd_canister_id"] = mfd_canister_id
        response["product_id"] = product_id
        response["already_registered"] = False
        response['home_cart_device'] = home_cart_device
        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

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


@validate(required_fields=["rfid", "user_id", "erp_product_id", "company_id"])
@log_args_and_response
def populate_mfd_canister_master(args: dict) -> object:
    """
        Function to populate data in mfd_canister_master
        @param args: should contain "rfid", "user_id", "erp_product_id", "company_id"
        @return: added record
    """
    company_id = int(args['company_id'])
    user_id = int(args['user_id'])
    erp_product_id = args['erp_product_id']
    rfid = args['rfid']
    home_cart = args['home_cart']

    try:
        logger.info("Fetching manual canister cart empty location")
        # TODO- mfd canister label
        logger.info("Adding record in mfd canister master")
        created_date, modified_date = get_current_modified_datetime()
        canister_data_dict = {
            "rfid": rfid,
            "canister_type": settings.SIZE_OR_TYPE["MFD"],
            "state_status": 1,
            "erp_product_id": erp_product_id,
            "home_cart_id": home_cart,
            "company_id": company_id,
            "created_by": user_id,
            "modified_by": user_id,
            "created_date": created_date,
            "modified_date": modified_date
        }
        mfd_id = add_data_in_mfd_canister_master(data_dict=canister_data_dict)
        # logger.info("Added record {} in mfd canister master".format(record))
        return mfd_id
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def get_mfd_canister_details(args):
    """
    Get location and drug data of active mfd canisters
    @param args: dict
    @return: json
    """
    try:
        company_id = args['company_id']
        mfd_canister_id = args['mfd_canister_id']
        pack_id = args['pack_id']
        mfd_canister_status = args.get('mfd_canister_status', None)
        mvs_filling = args.get('mvs_filling', False)
        mfd_canister_info, pack_slot_data = get_mfd_canister_data_query(company_id=company_id,
                                                                        mfd_canister_id=mfd_canister_id,
                                                                        mfd_canister_status=mfd_canister_status,
                                                                        pack_id=pack_id,
                                                                        mvs_filling=mvs_filling)

        return create_response(mfd_canister_info)

    except Exception as e:
        logger.error(e)
        return error(2001, "Error in getting mfd canister details.")


def get_canister_transfer(search_filters):
    """
    @param search_filters:  dict
    @return: json
    """
    clauses = list()

    filter_fields = search_filters['filter_fields']
    sort_fields = search_filters['sort_fields']
    paginate = search_filters['paginate']
    company_id = search_filters['company_id']
    # drop_down_data = dict()

    try:
        results, count = db_get_canister_transfer_info(company_id,
                                                       filter_fields=filter_fields,
                                                       sort_fields=sort_fields,
                                                       paginate=paginate,
                                                       clauses=clauses)

        response = {"mfd_canister_data": results,
                    "total_canisters": count}

        return create_response(response)


    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_canister_transfer: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_canister_transfer {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_canister_transfer: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_canister_transfer: " + str(e))


@log_args_and_response
def update_mfd_canister_history(canister_history_data):
    """
    updates canister history
    :param canister_history_data: dict
    :return:
    """
    canister_history_list = list()
    try:
        for canister_data in canister_history_data:
            last_history_record = get_latest_record_by_canister_id(canister_data['mfd_canister_id'])
            if last_history_record and last_history_record.current_location_id_id is None:
                update_history_dict = {"current_location_id": canister_data['current_location_id'],
                                       'is_transaction_manual': canister_data.get('is_transaction_manual', False),
                                       'modified_by': canister_data['user_id'],
                                       'modified_date': get_current_date_time()}
                logger.info("update_history_dict {}".format(update_history_dict))
                update_mfd_canister_transfer_data(update_history_dict, mfd_canister_id=last_history_record.id)
            else:
                canister_history_update_data = {
                    'mfd_canister_id': canister_data['mfd_canister_id'],
                    'current_location_id': canister_data['current_location_id'],
                    'created_by': canister_data['user_id'],
                    'modified_by': canister_data['user_id'],
                    'previous_location_id': last_history_record.current_location_id_id if last_history_record else None,
                    'is_transaction_manual': canister_data.get('is_transaction_manual', False)
                }
                canister_history_list.append(canister_history_update_data)
        if canister_history_list:
            logger.info("canister_history_list {}".format(canister_history_list))
            status = add_mfd_canister_history(canister_history_list)
            logger.info("In update_mfd_canister_history: canister_history_list updated: {}".format(status))
        return True

    except(InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
@validate(required_fields=["mfd_canister_id"])
def mfd_canister_label(canister_info: dict) -> dict:
    """
       Generates mfd canister label if not present, returns file name
       :param canister_info: dict with key canister_id
       :return: json
       """
    # product_id = canister_info.get("product_id")
    canister_id = canister_info["mfd_canister_id"]
    canister_id_with_mfd_prefix = constants.MFD_CANISTER_LABEL_PREFIX + str(canister_id)
    label_name = str(canister_id_with_mfd_prefix) + '.pdf'

    if 'regenerate' not in canister_info:  # flag to regenerate label forcefully
        logger.info("checking if label already exists in cloud")
        # If file already exists return
        try:
            if blob_exists(label_name, mfd_canister_label_dir):
                logger.info("mfd_canister_label: blob_exists now updating in print time")
                mfd_canister_update_dict = {"label_print_time": get_current_date_time()}
                update_status = update_mfd_canister(update_dict=mfd_canister_update_dict, id=canister_id)
                logger.info("In mfd_canister_label: updated mfd label print time: {}".format(update_status))
                response = {'label_name': label_name}
                return create_response(response)
        except InternalError as e:
            logger.info("mfd_canister_label: Caught Exception - " + str(e))
            logger.error(e)
            return error(2001)

        except Exception as e:
            logger.info("mfd_canister_label: Caught Exception - " + str(e))
            logger.error(e, exc_info=True)
            return error(1000, "Error in mfd_canister_label")

    logger.info("generating mfd canister label for canister " + str(canister_id_with_mfd_prefix))
    if not os.path.exists(mfd_canister_dir):
        os.makedirs(mfd_canister_dir)
    label_path = os.path.join(mfd_canister_dir, label_name)

    try:
        logger.info("fetching canister info of mfd canister: " + str(canister_id_with_mfd_prefix))
        canister = get_mfd_canister_data_by_id(canister_id)
        logger.info("fetched canister info of mfd canister: " + str(canister_id_with_mfd_prefix))
        product_id = canister.erp_product_id
        device_id = canister.home_cart_id
    except InternalError as e:
        logger.error(e)
        return error(2001)
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return error(1038)

    try:
        device_name = get_device_data_by_device_id_dao(device_id=device_id)
        home_cart_name = device_name.name
        canister_data_dict = {"canister_id": canister_id, "canister_id_with_mfd_prefix": canister_id_with_mfd_prefix,
                              "product_id": product_id, "home_cart": home_cart_name}
        logger.info("mfd canister info for label {}".format(canister_data_dict))
        logger.info('Starting MFD Canister Label Generation. Canister ID: {}, product ID: {}'
                     .format(canister_id_with_mfd_prefix, product_id))
        generate_mfd_canister_label(file_name=label_path, canister_data_list=[canister_data_dict])
        logger.info('Canister Label Generated. Canister ID: {}'.format(canister_id_with_mfd_prefix))
        logger.info("Uploading label to central storage for canister ID: {}".format(canister_id_with_mfd_prefix))
        create_blob(label_path, label_name, mfd_canister_dir)  # Upload label to central storage
        logger.info("Label of canister ID: {} uploaded to central storage ".format(canister_id_with_mfd_prefix))
        logger.info(
            "updating label print time in mfd canister master. canister ID: {}".format(canister_id_with_mfd_prefix))
        mfd_canister_update_dict = {"label_print_time": get_current_date_time()}
        update_status = update_mfd_canister(update_dict=mfd_canister_update_dict, id=canister_id)
        logger.info(
            "label_print_time updated in mfd canister master: {} for canister ID: {}".format(update_status, canister_id_with_mfd_prefix))
        response = {'label_name': label_name}
        return create_response(response)
    except Exception as e:
        logger.error('Canister Label Generation Failed: ' + str(e), exc_info=True)
        return error(2006)
    finally:
        remove_files([label_path])


@log_args_and_response
def update_mfd_canister_master(mfd_canister_locations: dict, user_id: int,
                               transfer_doc, transfer_wizard_doc, is_removed_manually=False) -> tuple:
    """
    To update mfd_canister, mfd_canister_transfer_history and couchdb for given locations.
    """
    updated_mfd_canister = dict()
    unknown_mfd_rfid = list()
    # get dest_device list to update couch db document
    couch_db_device_to_update = set()
    couch_db_update_required = False
    try:
        with db.transaction():
            logger.info("In update_mfd_canister_master with mfd_canister_locations: {}".format(mfd_canister_locations))

            mfd_canister_master_dict = dict()
            mfd_canister_activate_dict = defaultdict(list)
            canister_history_update_list = list()
            exclude_location = list()
            for location, rfid_fork_tuple in mfd_canister_locations.items():
                # addition of mfd_canister to robot
                rfid, fork_detection, is_disable = rfid_fork_tuple
                if rfid:
                    if is_disable:
                        logger.info('canister placed on disable location')
                        continue
                    canister_data = get_canister_data_by_rfid(rfid)
                    if not canister_data:
                        unknown_mfd_rfid.append(rfid)
                        continue
                    canister_id = canister_data['id']
                    home_cart_id = canister_data['home_cart_id']
                    canister_state_status = canister_data['state_status']
                    if canister_state_status == constants.MFD_CANISTER_MISPLACED:
                        mfd_canister_activate_dict[home_cart_id].append(canister_id)
                    updated_mfd_canister[rfid] = canister_id
                    mfd_canister_master_dict[canister_id] = {'location_id': location,
                                                             'fork_detection': fork_detection}
                    if canister_data['location_id'] != location:
                        history_dict = {
                            'mfd_canister_id': canister_id,
                            'current_location_id': location,
                            'user_id': user_id,
                            'is_transaction_manual': is_removed_manually
                        }
                        canister_history_update_list.append(history_dict)
                    if canister_data['dest_device_id'] and \
                            canister_data['dest_device_id'] not in couch_db_device_to_update:
                        couch_db_device_to_update.add(canister_data['dest_device_id'])

                # removal of mfd_canister from robot
                else:
                    # to obtain mfd_canister data based on its present location
                    canister_data = get_canister_data_by_location_id(location)
                    logger.info("mfd_canister_data: {}".format(canister_data))
                    if canister_data:
                        canister_id = canister_data['id']
                        canister_state_status = canister_data['state_status']
                        if canister_state_status == constants.MFD_CANISTER_INACTIVE:
                            transfer_location_id = None
                        else:
                            trolley_id = canister_data['home_cart_id']
                            # to obtain location as per the drawer data and location data in couchdb
                            logger.info('exclude_location: {}'.format(exclude_location))
                            transfer_location_id, scanned_drawer = get_transfer_location_from_couch_db(
                                trolley_id=trolley_id, canister_data=canister_data, exclude_location=exclude_location,
                                transfer_doc_cdb=transfer_doc, transfer_wizard_cdb=transfer_wizard_doc
                            )
                            if canister_data['dest_device_id'] and \
                                    canister_data['dest_device_id'] not in couch_db_device_to_update:
                                couch_db_device_to_update.add(canister_data['dest_device_id'])
                            exclude_location.append(transfer_location_id)

                        mfd_canister_master_dict[canister_id] = {'location_id': transfer_location_id,
                                                                 'fork_detection': 0}

                        history_dict = {
                            'mfd_canister_id': canister_id,
                            'current_location_id': transfer_location_id,
                            'user_id': user_id,
                            'is_transaction_manual': is_removed_manually
                        }
                        canister_history_update_list.append(history_dict)
                        if canister_data['dest_device_id'] and \
                                canister_data['dest_device_id'] not in couch_db_device_to_update:
                            couch_db_device_to_update.add(canister_data['dest_device_id'])

            # updating mfd canister location
            if mfd_canister_master_dict:
                logger.info('mfd_canister_master_dict: {}'.format(mfd_canister_master_dict))
                mfd_canister_location_update = update_mfd_canister_location_with_fork(mfd_canister_master_dict)
                logger.info('update_mfd_canister_master: mfd canister location updated with fork: {}'
                            .format(mfd_canister_location_update))

            # updating mfd canister history
            if canister_history_update_list:
                mfd_canister_history_update = update_mfd_canister_history(canister_history_update_list)
                logger.info('update_mfd_canister_master: mfd canister location updated with fork: {}'.format(
                    mfd_canister_history_update))

            # activating misplaced canister
            if mfd_canister_activate_dict:
                update_status = mfd_canister_found_update_status(mfd_canister_activate_dict, user_id)
                logger.info('update_mfd_canister_master: mfd canister found update status: {}'.format(
                    update_status))
            if mfd_canister_master_dict or canister_history_update_list:
                couch_db_update_required = True

            if transfer_wizard_doc and 'data' in transfer_wizard_doc:
                batch_id = transfer_wizard_doc['data'].get('batch_id', None)
                module_id = transfer_wizard_doc['data'].get('module_id', None)
            else:
                batch_id = None
                module_id = None
            return True, updated_mfd_canister, unknown_mfd_rfid, couch_db_update_required, list(
                couch_db_device_to_update), batch_id, module_id

    except(InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e)
        raise


@log_args_and_response
def update_mfd_canister_transfer_couch_db(device_id, system_id, batch_id, current_module_id):
    try:
        logger.info("update_canister_transfer_couch_db {}, {}, {}, {}".format(device_id, system_id, batch_id,
                                                                              current_module_id))
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = 'mfd_transfer_{}'.format(device_id)
        table = cdb.get(_id=id)

        misplaced_canisters = list()
        if 'data' in table:
            trolley_id = table['data'].get('scanned_trolley', None)
            scanned_drawer = table['data'].get('scanned_drawer', None)
            if trolley_id and batch_id and scanned_drawer and current_module_id is not None and \
                    current_module_id == constants.MFD_TRANSFER_WIZARD_MODULES['TRANSFER_TO_ROBOT_WIZARD']:
                misplaced_canisters, quadrant_wise_count = mfd_misplaced_canister_transfer_to_robot(batch_id=batch_id,
                                                                                                    device_id=device_id,
                                                                                                    trolley_id=trolley_id,
                                                                                                    drawer_id=scanned_drawer)

            if trolley_id and batch_id and current_module_id is not None and \
                    current_module_id in [constants.MFD_TRANSFER_WIZARD_MODULES['RTS_SCREEN_WIZARD'],
                                          constants.MFD_TRANSFER_WIZARD_MODULES['EMPTY_CANISTER_WIZARD']]:
                misplaced_canisters, rts_misplaced_count = mfd_misplaced_canister_dao(batch_id=batch_id,
                                                                                      device_id=device_id,
                                                                                      trolley_id=trolley_id)
            logger.info("misplaced_canisters: " + str(misplaced_canisters))
        # if table is None:  # when no document available for given device_id
        #     table = {"_id": id, "type": 'canister_transfer', "device_id": device_id, "batch": None}

        if table and table.get('data', {}):
            table['data']['timestamp'] = get_current_date_time()
            table['data']['uuid'] = uuid1().int
            table['data']['misplaced_count'] = len(misplaced_canisters)

            # save only if time stamp updated
            cdb.save(table)
            return True
        logger.info("updated table {}".format(table))
        return False

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return error(1000, "Document update conflict.")

    except RealTimeDBException as e:
        return error(1000, str(e))

    except Exception as e:
        logger.error(e)
        raise Exception("Couch db update failed while transferring canisters")


def recommend_drawers_based_on_transfers(empty_locations_info_drawer_wise: list, transfer_count: int) -> list:
    """
    Recommend trolley drawers to transfer mfd canister to list
    @param empty_locations_info_drawer_wise: drawer_wise info having empty_locations_count
    @param transfer_count: total canisters to be transferred
    @return: recommended_drawers
    """
    recommended_drawers = list()

    # sort list based on locations_count in descending order
    empty_locations_info_drawer_wise = sorted(empty_locations_info_drawer_wise,
                                              key=lambda item: item["empty_locations_count"],
                                              reverse=True)
    while transfer_count != 0:
        drawer_info = empty_locations_info_drawer_wise[0]
        if transfer_count == drawer_info["empty_locations_count"]:
            # when there are exact empty locations in a drawer
            recommended_drawers.append(drawer_info)
            empty_locations_info_drawer_wise.pop(0)
            # transfer_count = 0
            break
        elif transfer_count > drawer_info["empty_locations_count"]:
            # when needs more empty locations than empty locations in drawer
            recommended_drawers.append(drawer_info)
            transfer_count = int(transfer_count) - int(drawer_info["empty_locations_count"])
            empty_locations_info_drawer_wise.pop(0)
        else:
            # out of available drawers find optimum drawer which is best fit(
            # min. diff between empty locations count and remaining no.of transfer) and
            # for same diff choose first out of all equal distance data
            optimum_drawer = None
            for i, drawer in enumerate(empty_locations_info_drawer_wise):
                if transfer_count < empty_locations_info_drawer_wise[i]["empty_locations_count"]:
                    if i == 0:
                        optimum_drawer = drawer
                    elif empty_locations_info_drawer_wise[i]["empty_locations_count"] < \
                            empty_locations_info_drawer_wise[i - 1]["empty_locations_count"]:
                        optimum_drawer = drawer
                else:
                    break
            recommended_drawers.append(optimum_drawer)
            transfer_count = 0
    return recommended_drawers


@validate(required_fields=["company_id"])
def get_rts_canister_data(search_filters):
    """
    @param search_filters:  dict
    @return: json
    """
    clauses = list()

    filter_fields = search_filters['filter_fields']
    sort_fields = search_filters['sort_fields']
    paginate = search_filters['paginate']
    company_id = search_filters['company_id']

    try:
        results, count = db_get_rts_required_canisters(company_id=company_id,
                                                       filter_fields=filter_fields,
                                                       sort_fields=sort_fields,
                                                       paginate=paginate,
                                                       clauses=clauses)

        response = {"mfd_canister_data": results,
                    "total_canisters": count}

        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_rts_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_rts_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_rts_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_rts_canister_data: " + str(e))


@log_args_and_response
@validate(required_fields=["mfd_analysis_id", "company_id", "user_id"])
def mark_canister_rts_done(mfd_data):
    """
    updates drug and canister status and marks them to rts done.
    @param mfd_data:
    :return:
    """
    company_id = mfd_data['company_id']
    user_id = mfd_data['user_id']
    activate_canister = mfd_data.get('activate_canister', False)
    activate_response = None
    try:
        with db.transaction():
            # getting drugs for whom rts was required.
            mfd_analysis_details_ids, home_cart_id, mfd_canister_id, pack_mfd_analysis_details_ids, canister_done, \
             mfd_canistser_state_status, container_name, pack_status_list, home_cart_device_name = db_get_mfd_analysis_details_ids(
                mfd_data['mfd_analysis_id'], company_id,
                constants.MFD_DRUG_RTS_REQUIRED_STATUS)
            if not mfd_analysis_details_ids:
                return error(1020, 'No rts required for given canister.')

            if mfd_canistser_state_status != constants.MFD_CANISTER_INACTIVE:
                empty_location = get_empty_locations(constants.MFD_TROLLEY_EMPTY_DRAWER_TYPE, 1, home_cart_id)

                if not empty_location:
                    return error(1020, 'No empty location found')

                canister_location_dict = {mfd_canister_id: empty_location[0]}
                canister_location_update = update_mfd_canister_location(canister_location_dict)
                logger.info('mark_canister_rts_done: mfd canister location updated: {}'.format(
                    canister_location_update))

            # marking rts done on drug level.
            drug_update_status = db_update_drug_status(mfd_analysis_details_ids, constants.MFD_DRUG_RTS_DONE)

            # marking rts done on canister level.
            canister_status = db_update_canister_status([mfd_data['mfd_analysis_id']],
                                                        constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                        user_id)

            if mfd_canistser_state_status == constants.MFD_CANISTER_MISPLACED:
                mfd_canister_home_cart_dict = {home_cart_id: [mfd_canister_id]}
                update_status = mfd_canister_found_update_status(mfd_canister_home_cart_dict, user_id)
                logger.info('mark_canister_rts_done: mfd canister found update status: {}'.format(
                    update_status))

            elif mfd_canistser_state_status == constants.MFD_CANISTER_INACTIVE and activate_canister:
                activate_json_response = activate_mfd_canister({"company_id": company_id,
                                                                "mfd_canister_id": mfd_canister_id,
                                                                "user_id": user_id})
                activate_response = json.loads(activate_json_response)

            # updating couch db with pending rts canister count
            count = db_get_rts_required_canister_count(company_id)
            logger.info('pending_rts_count: {} for company_id: {}'.format(count, company_id))
            couch_db_data = {'count': count, 'update_timestamp': get_current_date_time()}
            update_mfd_rts_count_in_couch_db(constants.CONST_MFD_RTS_DOC_ID, company_id, couch_db_data)

            response = {'canister_status': canister_status,
                        'drug_status': drug_update_status,
                        'home_cart_device_name': home_cart_device_name}
            if activate_response:
                response.update(activate_response['data'])

            return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in mark_canister_rts_done: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in mark_canister_rts_done {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in mark_canister_rts_done: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in mark_canister_rts_done: " + str(e))


def get_unique_mfd_rts_canister_filters(args):
    """
    Returns all the filter data required for rts canisters
    :param args:
    :return:
    """
    company_id = args['company_id']
    state_status_filters = list()
    try:
        # getting all the device names where rts canisters are currently placed
        source_device_data, state_status = get_unique_rts_filters(company_id)

        # reason to return are only two either pack marked manually or deleted
        reason_to_return = get_unique_rts_actions(company_id)

        for status in state_status:
            status = int(status)
            state_status_filters.append({constants.MFD_STATE_STATUS[status]: status})

        return create_response({'source_device_id': source_device_data,
                                'state_status': state_status_filters,
                                'reason_to_return': reason_to_return})

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_unique_mfd_rts_canister_filters: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_unique_mfd_rts_canister_filters {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_unique_mfd_rts_canister_filters: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_unique_mfd_rts_canister_filters: " + str(e))


def get_unique_mfd_canister_master_filters(args):
    """
    Returns all the filter data required for MFD canister master screen
    @param args: dict
    @return: json
    """
    logger.info("In get_unique_mfd_canister_master_filters")
    # filters_dict = dict()
    company_id = args['company_id']
    dest_device_data_set = set()
    try:
        # getting all the filter data query for mfd canister master screen
        filter_data_query, source_device_name_records, home_cart_name_records, dest_device_name_records, \
            state_status_query = get_mfd_canister_master_filters(company_id)
        filters_dict = {"source_device_name": list(),
                        "home_cart_name": list(),
                        "dest_device_name": list(),
                        "status": list(),
                        "last_used_by": list()}
        # get the set of name in source_device_name_records and add to list
        source_device_name_list = sorted(
            list(set(record["source_device_name"] for record in source_device_name_records)))
        filters_dict['source_device_name'] = source_device_name_list
        # get the set of name in home_cart_name_records and add to list
        home_cart_name_list = sorted(list(set(record["home_cart_name"] for record in home_cart_name_records)))
        filters_dict['home_cart_name'] = home_cart_name_list
        # iterate through dest_device_name_records and obtain set of dest_device_names
        for record in dest_device_name_records:
            if record["status_id"] in [constants.MFD_CANISTER_FILLED_STATUS,
                                       constants.MFD_CANISTER_VERIFIED_STATUS]:
                # if the canister is filled or verified and is present in robot or MFS, destination assigned as trolley
                if record["device_type_id"] in [settings.DEVICE_TYPES['Manual Filling Device'],
                                                settings.DEVICE_TYPES['ROBOT']]:
                    dest_device_data_set.add(record["trolley_name"])
                # else if canister in trolley, then assign the destination device as per MfdAnalysis
                else:
                    dest_device_data_set.add(record["analysis_device_name"])
            elif record["status_id"] in [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                         constants.MFD_CANISTER_RTS_DONE_STATUS,
                                         constants.MFD_CANISTER_SKIPPED_STATUS,
                                         constants.MFD_CANISTER_DROPPED_STATUS]:
                # check if for the mentioned status is the canister in MFS or Robot, destination assigned as trolley
                if record["device_type_id"] in [settings.DEVICE_TYPES['Manual Filling Device'],
                                                settings.DEVICE_TYPES['ROBOT']]:
                    dest_device_data_set.add(record["trolley_name"])
            elif record["status_id"] in [constants.MFD_CANISTER_IN_PROGRESS_STATUS]:
                dest_device_data_set.add(record["trolley_name"])

        dest_device_name_list = sorted(list(dest_device_data_set))
        filters_dict['dest_device_name'] = dest_device_name_list

        # iterate the filter_data_query and obtain the status and last_used_by
        for record in filter_data_query:
            if record['status']:
                status_codes = list(record['status'].split(','))
                status_values = list()
                for status in status_codes:
                    status_values.append(constants.USER_MFD_CANISTER_STATUS[int(status)])
                filters_dict['status'] = status_values
            if record['last_used_by']:
                filters_dict['last_used_by'] = list(record['last_used_by'].split(','))

        state_status_filters = list()
        for record in state_status_query:
            state_status_filters.append({constants.MFD_STATE_STATUS[record['state_status']]: record['state_status']})
        filters_dict['state_status'] = state_status_filters

        return create_response(filters_dict)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_unique_mfd_canister_master_filters: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_unique_mfd_canister_master_filters {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_unique_mfd_canister_master_filters: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_unique_mfd_canister_master_filters: " + str(e))



@validate(required_fields=["company_id", "system_id", "device_id", "batch_id", "user_id", "current_module"])
def get_mfd_empty_canister_data(args):
    """
    Method to transfer mfd canisters from robot to trolley flow
    @param args: dict
    @return: json
    """
    logger.info("Input get_mfd_empty_canister_data {}".format(args))
    device_id = args['device_id']
    batch_id = args['batch_id']
    system_id = args['system_id']
    company_id = args['company_id']
    drawer_scanned = args.get('drawer_scanned', True)
    current_module = int(args['current_module'])
    # user_id = int(args["user_id"])
    # on_start = bool(int(args.get("on_start", 0)))
    trolley_serial_number = args.get('trolley_serial_number', None)
    drawer_serial_number = args.get('drawer_serial_number', None)
    # empty_locations_list_for_rts_canisters = list()
    # empty_locations_list_for_non_rts_canisters = list()
    drawers_to_unlock = dict()
    mfd_canister_list = list()
    try:
        logger.info("get_mfd_empty_canister_data: scanned trolley- {}, drawer- {}".format(trolley_serial_number,
                                                                                           drawer_serial_number))
        trolley_id = get_device_id_from_serial_number(serial_number=trolley_serial_number, company_id=company_id)
        logger.info("trolley_id {}".format(trolley_id))
        if not trolley_id:
            return error(1001, "Missing Parameter(s): trolley_id or Invalid trolley.")
        if current_module == constants.MFD_TRANSFER_WIZARD_MODULES['RTS_SCREEN_WIZARD']:
            drawer_data = get_container_data_based_on_serial_numbers_dao(serial_numbers=[drawer_serial_number])
            logger.info("drawer_data {}".format(drawer_data))
            if not drawer_data:
                return error(1001, "Missing Parameter(s): drawer_data or Invalid drawer.")

            drawer_id = drawer_data[0]["id"]

            drawer_empty_locations = fetch_empty_locations_of_mfd_container(device_id=trolley_id,
                                                                            container_id=drawer_id)
            logger.info("empty locations count-{} in drawer {}".format(len(drawer_empty_locations), drawer_id))

            if not drawer_empty_locations:
                return create_response({'drawers_to_unlock': list(drawers_to_unlock.values()),
                                        'canister_data': mfd_canister_list
                                        })

            # check scanned drawer is for rts canisters or empty canisters
            drawer_level = drawer_data[0]["drawer_level"]
            if drawer_level > constants.MFD_TROLLEY_MIDDLE_LEVEL:
                logger.info("drawer scanned for rts canisters")
                rts_drawer = True
            else:
                logger.info("drawer scanned for empty canisters")
                rts_drawer = False

            if rts_drawer:
                mfd_canister_list = get_mfd_rts_canisters(device_id=device_id, trolley_id=trolley_id, batch_id=batch_id,
                                                          required_canisters=len(drawer_empty_locations))
                if drawer_scanned:
                    transfer_data = {"scanned_drawer": drawer_id}
                    update_mfd_transfer_couch_db(device_id, system_id, transfer_data)
                logger.info("mfd_canister_list_returning: " + str(mfd_canister_list))
            else:
                mfd_canister_list = get_mfd_non_rts_canisters(device_id=device_id, trolley_id=trolley_id,
                                                              batch_id=batch_id)
                logger.info("mfd_canister_list_returning: " + str(mfd_canister_list))

            for canister in mfd_canister_list:
                if canister["drawer_name"] not in drawers_to_unlock.keys():
                    drawer_data = {"drawer_name": canister["drawer_name"],
                                   "serial_number": canister["serial_number"],
                                   "ip_address": canister["ip_address"],
                                   "secondary_ip_address": canister["secondary_ip_address"],
                                   "id": canister["drawer_id"],
                                   "mac_address": canister["mac_address"],
                                   "secondary_mac_address": canister["secondary_mac_address"],
                                   "from_device": list(),
                                   "to_device": list()
                                   }
                    drawers_to_unlock[canister["drawer_name"]] = drawer_data

                drawers_to_unlock[canister["drawer_name"]]["from_device"].append(canister["display_location"])

            return create_response({'drawers_to_unlock': list(drawers_to_unlock.values()),
                                    'canister_data': mfd_canister_list
                                    })
        elif current_module == constants.MFD_TRANSFER_WIZARD_MODULES['EMPTY_CANISTER_WIZARD']:
            mfd_canister_list = get_mfd_non_rts_canisters(device_id=device_id, trolley_id=trolley_id,
                                                          batch_id=batch_id)
            logger.info("fetched mfd canister list" + str(mfd_canister_list))
            # unique_robot_drawers = set()
            for canister in mfd_canister_list:
                if canister["drawer_name"] not in drawers_to_unlock.keys():
                    drawer_data = {"drawer_name": canister["drawer_name"],
                                   "serial_number": canister["serial_number"],
                                   "ip_address": canister["ip_address"],
                                   "secondary_ip_address": canister["secondary_ip_address"],
                                   "id": canister["drawer_id"],
                                   "mac_address": canister["mac_address"],
                                   "secondary_mac_address": canister["secondary_mac_address"],
                                   "from_device": list(),
                                   "to_device": list()
                                   }
                    drawers_to_unlock[canister["drawer_name"]] = drawer_data

                drawers_to_unlock[canister["drawer_name"]]["from_device"].append(canister["display_location"])

            return create_response({'drawers_to_unlock': list(drawers_to_unlock.values()),
                                    'canister_data': mfd_canister_list
                                    })
        else:
            return error(1020, 'Invalid module')

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_mfd_empty_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except RealTimeDBException as e:
        logger.error(e)
        return error(11002, str(e))
    except Exception as e:
        logger.error("Error in get_mfd_empty_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_mfd_empty_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_mfd_empty_canister_data: " + str(e))


@log_args_and_response
def check_mfd_trolley_drawer_scanned_or_not(system_id: int, batch_id: int, device_id: int, trolley_id: int,
                                            drawer_id: int):
    """
    Function to check whether drawer is scanned or not
    @param system_id: int
    @param batch_id: int
    @param device_id: int
    @param trolley_id: int
    @param drawer_id: int
    @return: bool
    """

    try:
        logger.info(
            "check_mfd_trolley_drawer_scanned_or_not {}, {}, {}, {}".format(device_id, batch_id, device_id, trolley_id))
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = 'mfd_transfer_{}'.format(device_id)
        table = cdb.get(_id=id)
        is_drawer_scanned = False
        if table is not None:
            if str(trolley_id) in table["data"]['mfd_transfer_to_robot'] and \
                    str(drawer_id) in table["data"]['mfd_transfer_to_robot'][str(trolley_id)]["drawer_data"].keys():
                is_drawer_scanned = \
                    table["data"]['mfd_transfer_to_robot'][str(trolley_id)]["drawer_data"][str(drawer_id)][
                        "drawer_scanned"]
        return is_drawer_scanned
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        raise RealTimeDBException("conflict_while_saving_document")
    except Exception as e:
        logger.error(e)
        raise RealTimeDBException('Couch db access failed while transferring canisters')


@log_args_and_response
def get_transfer_location_from_couch_db(trolley_id: int, canister_data: dict, exclude_location: list, transfer_doc_cdb,
                                        transfer_wizard_cdb, ext_scanned_drawer=None, ext_trolley_id=None,
                                        manual_update=False) -> tuple:
    """
    to obtain destination location_id for the selected device from couch-db
    :param: system_id: int
    :param: device_id: int
    :param: flow: str
    :param: trolley_id: int
    """
    try:
        dest_location_id: int or None = None
        scanned_drawer: int or None = None
        if transfer_doc_cdb is None:  # when no document available for given device_id
            logger.info("No document available for given data")
            return dest_location_id, None
        # to check if trolley is scanned
        if 'data' in transfer_doc_cdb:
            if trolley_id == transfer_doc_cdb['data'].get('scanned_trolley', None) or ext_trolley_id:
                if ext_trolley_id:
                    trolley_id = ext_trolley_id
                scanned_drawer = transfer_doc_cdb['data'].get('scanned_drawer', None)
                module = transfer_wizard_cdb['data'].get('module_id', None)
                if canister_data['status_id'] == constants.MFD_CANISTER_DROPPED_STATUS and \
                        canister_data['home_cart_id'] == trolley_id and module is not None and (module ==
                                                                                                constants.MFD_TRANSFER_WIZARD_MODULES[
                                                                                                    'EMPTY_CANISTER_WIZARD'] or
                                                                                                (module ==
                                                                                                 constants.MFD_TRANSFER_WIZARD_MODULES[
                                                                                                     'RTS_SCREEN_WIZARD'] and manual_update)):
                    dest_location_id = get_empty_location_by_trolley(trolley_id, exclude_location)
                elif canister_data['status_id'] in [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                    constants.MFD_CANISTER_MVS_FILLING_REQUIRED] and \
                        canister_data['home_cart_id'] == trolley_id:

                    if transfer_wizard_cdb is None:  # when no document available for given device_id
                        logger.info("No document available for given data")
                        return dest_location_id, scanned_drawer
                    if 'data' in transfer_wizard_cdb:
                        module = transfer_wizard_cdb['data'].get('module_id', None)
                        logger.info('module for mvs and rts canister: {}'.format(module))
                        if module is not None and module in [constants.MFD_TRANSFER_WIZARD_MODULES['RTS_SCREEN_WIZARD'],
                                                             constants.MFD_TRANSFER_WIZARD_MODULES[
                                                                 'EMPTY_CANISTER_WIZARD']]:
                            if ext_scanned_drawer:
                                scanned_drawer = ext_scanned_drawer
                            dest_location_id = get_empty_location_by_drawer(scanned_drawer, exclude_location)
                            logger.info('dest_loc for can: {}'.format(dest_location_id))
                        elif module is not None and module == constants.MFD_TRANSFER_WIZARD_MODULES['TRANSFER_TO_ROBOT_WIZARD']:
                            if ext_scanned_drawer:
                                scanned_drawer = ext_scanned_drawer
                            if scanned_drawer == canister_data['source_drawer_id']:
                                dest_location_id = canister_data['trolley_location_id']

        logger.info('dest_location {}'.format(dest_location_id))
        return dest_location_id, scanned_drawer

    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        raise RealTimeDBException("conflict_while_saving_document")
    except Exception as e:
        logger.error(e)
        raise Exception("Couch db update failed while transferring canisters")


@retry_exception(times = 3, exceptions=(couchdb.http.ResourceConflict, couchdb.http.HTTPError))
def update_mfd_transfer_sent_notification(system_id: int, device_id: int, user_id: int) -> bool:
    """
    Function to update action_taken_by field in sent notification
    @param user_id: int
    @param system_id: int
    @param device_id: int
    @return: bool
    """

    try:
        logger.info(
            "update_mfd_transfer_sent_notification {}, {}, {}.".format(system_id, device_id, user_id))
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        logger.error(f"In update_mfd_transfer_sent_notification, doc connected")
        id = 'mfd_notifications_{}'.format(device_id)
        table = cdb.get(_id=id)
        if table is not None:
            if table.get("data", {}) and table["data"].get("notification_data"):
                for i, item in enumerate(table["data"]["notification_data"]):
                    if not item["action_taken_by"]:
                        table["data"]["notification_data"][i]["action_taken_by"] = user_id
                cdb.save(table)
                return True
        return False
    except couchdb.http.ResourceConflict:
        settings.logger.info("In update_mfd_transfer_sent_notification, EXCEPTION: Document update conflict.")
        raise RealTimeDBException("conflict_while_saving_document")
    except Exception as e:
        logger.error(f"In update_mfd_transfer_sent_notification: e: {e}")
        raise RealTimeDBException('Couch db access failed while transferring canisters')


@validate(required_fields=["company_id"])
def get_rts_drug_data(rts_data: dict) -> dict:
    """
    returns drug data for rts canisters
    :param rts_data: dict
    :return: json
    """
    company_id = rts_data['company_id']

    try:
        results = db_get_rts_drugs(company_id)

        response = {"rts_data": results}

        return create_response(response)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_rts_drug_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_rts_drug_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_rts_drug_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_rts_drug_data: " + str(e))


@log_args
@validate(required_fields=["company_id", "system_id", "device_id", "batch_id", "module_id"])
def get_mfd_misplaced_canisters(args: dict) -> dict:
    """
    This function obtains the misplaced Empty, skipped and RTS MFD canisters for the given batch and device
    @param args: dict
    @return dict
    """
    logger.info("In get_mfd_misplaced_canisters")
    try:
        device_id = args.get("device_id", None)
        batch_id = args.get("batch_id", None)
        # misplaced_canister_count = args.get("misplaced_canister_count", 0)
        module_id = int(args["module_id"])
        system_id = int(args["system_id"])
        company_id = args["company_id"]
        misplaced_canisters = list()
        drawers_to_unlock_list = list()

        if device_id and batch_id:
            if module_id in [constants.MFD_TRANSFER_WIZARD_MODULES['RTS_SCREEN_WIZARD'],
                             constants.MFD_TRANSFER_WIZARD_MODULES['EMPTY_CANISTER_WIZARD']]:
                trolley_serial_number = args.get('trolley_serial_number', None)
                if not trolley_serial_number:
                    return error(1001)
                trolley_id, drawer_id = get_trolley_drawer_from_serial_number_mfd(
                    trolley_serial_number=trolley_serial_number,
                    drawer_serial_number=None,
                    company_id=company_id)
                logger.info("trolley_id {}, drawer_id {}".format(trolley_id, drawer_id))
                misplaced_canisters, rts_misplaced_canister_count = mfd_misplaced_canister_dao(batch_id=batch_id,
                                                                                               device_id=device_id,
                                                                                               trolley_id=trolley_id)
                logger.info("misplaced_canisters_for_module: " + str(misplaced_canisters))

                if misplaced_canisters:
                    if rts_misplaced_canister_count:
                        empty_locations_list_for_rts_canisters = fetch_empty_trolley_locations_for_rts_canisters(
                            trolley_id=trolley_id)

                        logger.info("recommending empty trolley drawers for rts canisters")
                        recommended_drawers = recommend_drawers_based_on_transfers(
                            empty_locations_info_drawer_wise=empty_locations_list_for_rts_canisters,
                            transfer_count=rts_misplaced_canister_count
                        )
                        logger.info("Recommended drawers: " + str(recommended_drawers))
                        if recommended_drawers:
                            # recommend loc for each canister
                            for canister in misplaced_canisters:
                                if canister['current_status'] == constants.MFD_CANISTER_RTS_REQUIRED_STATUS:
                                    for index, drawer in enumerate(recommended_drawers):
                                        if drawer['empty_locations_count'] > 0:
                                            canister["recommended_drawer_name"] = drawer['drawer_name']
                                            canister["recommended_drawer_id"] = drawer['container_id']
                                            canister["recommended_drawer_serial_number"] = drawer['serial_number']
                                            recommended_drawers[index]['empty_locations_count'] -= 1
                                        else:
                                            continue
                else:
                    update_mfd_misplaced_count(device_id=device_id, system_id=system_id,
                                               batch_id=batch_id, module_id=module_id, company_id=company_id,
                                               trolley_serial_number=trolley_serial_number,
                                               count=0)

                    # drawers_to_unlock_dict = get_empty_drawers_for_locations_dao(device_id=device_id,
                    #                                                              no_of_locations_required=len(
                    #                                                                  misplaced_canisters),
                    #                                                              quadrant=None)
                    # logger.info("fetched drawers_to_unlock_dict")
                    # if drawers_to_unlock_dict:
                    #     drawers_to_unlock_list = deepcopy(list(drawers_to_unlock_dict.values()))
                    #     logger.info("appending recommend loc in canister data")
                    #     # recommend loc for each canister
                    #     for canister in misplaced_canisters:
                    #         for robot_drawer, robot_drawer_data in drawers_to_unlock_dict.items():
                    #             if robot_drawer_data["to_device"]:
                    #                 canister["recommended_drawer_name"] = robot_drawer
                    #                 canister["recommended_display_loc"] = robot_drawer_data["to_device"].pop(0)
                    #                 break


            elif module_id == constants.MFD_TRANSFER_WIZARD_MODULES['TRANSFER_TO_ROBOT_WIZARD']:
                trolley_serial_number = args.get('trolley_serial_number', None)
                drawer_serial_number = args.get('drawer_serial_number', None)
                drawers_to_unlock_list = dict()
                if not trolley_serial_number or not drawer_serial_number:
                    return error(1001)
                trolley_id, drawer_id = get_trolley_drawer_from_serial_number_mfd(
                    trolley_serial_number=trolley_serial_number,
                    drawer_serial_number=drawer_serial_number,
                    company_id=company_id)
                logger.info("trolley_id {}, drawer_id {}".format(trolley_id, drawer_id))

                misplaced_canisters, quadrant_wise_count = mfd_misplaced_canister_transfer_to_robot(batch_id=batch_id,
                                                                                                    device_id=device_id,
                                                                                                    trolley_id=trolley_id,
                                                                                                    drawer_id=drawer_id)
                logger.info("misplaced_canisters: " + str(misplaced_canisters))

                # if misplaced_canisters:
                #     drawers_to_unlock_dict = get_empty_drawers_for_locations_dao(device_id=device_id,
                #                                                                  no_of_locations_required=len(
                #                                                                      misplaced_canisters),
                #                                                                  quadrant=None)
                #     logger.info("fetched drawers_to_unlock_dict")
                #     if drawers_to_unlock_dict:
                #         drawers_to_unlock_list = deepcopy(list(drawers_to_unlock_dict.values()))
                #         logger.info("appending recommend loc in canister data")
                #         # recommend loc for each canister
                #         for canister in misplaced_canisters:
                #             for robot_drawer, robot_drawer_data in drawers_to_unlock_dict.items():
                #                 if robot_drawer_data["to_device"]:
                #                     canister["recommended_drawer_name"] = robot_drawer
                #                     canister["recommended_display_loc"] = robot_drawer_data["to_device"].pop(0)
                #                     break

                if misplaced_canisters:
                    # count no. of canister transfers from trolley drawer to robot and recommend robot drawers
                    # based on destination quadrant
                    for quadrant, canisters in quadrant_wise_count.items():
                        # quadrant = mfd_canister_list[0]["dest_quadrant"]
                        transfer_count = len(canisters)
                        drawer_data = get_empty_drawers_for_locations_dao(device_id=device_id,
                                                                          quadrant=quadrant,
                                                                          no_of_locations_required=transfer_count)
                        display_location_list = list()
                        for drawer in drawer_data.values():
                            display_location_list.extend(drawer['to_device'])
                        index = 0
                        for mfd_can in misplaced_canisters:
                            if mfd_can['dest_quadrant'] == quadrant and mfd_can['to_be_placed_in_robot']:
                                mfd_can['dest_display_loc'] = display_location_list[index]
                                index += 1
                        for drawer_name, drawer_location_info in drawer_data.items():
                            if drawer_name in drawers_to_unlock_list:
                                drawers_to_unlock_list[drawer_name]['to_device'].extend(
                                    drawer_location_info['to_device'])
                            else:
                                drawers_to_unlock_list[drawer_name] = drawer_location_info
                    drawers_to_unlock_list = list(drawers_to_unlock_list.values())
                else:
                    update_mfd_misplaced_count(device_id=device_id, system_id=system_id,
                                               batch_id=batch_id, module_id=module_id, company_id=company_id,
                                               trolley_serial_number=trolley_serial_number,
                                               count=0)
        else:
            return error(1000, "Missing device_id or batch_id")

        response = {"misplaced_canisters": misplaced_canisters,
                    "drawers_to_unlock": drawers_to_unlock_list}

        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_mfd_misplaced_canisters: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_mfd_misplaced_canisters {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_mfd_misplaced_canisters: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_mfd_misplaced_canisters: " + str(e))


@log_args_and_response
@validate(required_fields=["company_id", "system_id", "device_id", "user_id", "batch_id"])
def get_mfd_empty_canister_cart(args):
    """
    Method to transfer mfd canisters from robot to trolley flow
    @param args: dict
    @return: json
    """
    logger.info('in get_mfd_empty_canister_cart:')
    device_id = args['device_id']
    logger.info('get_mfd_empty_canister_cart: for device_id: {} '.format(device_id))
    system_id = args['system_id']
    # company_id = args['company_id']
    user_id = int(args["user_id"])
    on_start = bool(int(args.get("on_start", 0)))
    try:
        drop_pending_canister_count = check_drop_pending(device_ids=[device_id])
        logger.info('get_mfd_empty_canister_cart: for device_id: {} drop_pending_canister {}'.format(
            device_id, drop_pending_canister_count))
        if drop_pending_canister_count:
            logger.info('get_mfd_empty_canister_cart: for device_id: {} returning  13003'.format(device_id))
            return error(13003)
        if on_start:
            logger.info("get_mfd_empty_canister_cart: for device_id: {} updating transfer action_taken_by in couch db "
                         "doc mfd_notifications.".format(device_id))
            couchdb_update_status = update_mfd_transfer_sent_notification(system_id=system_id, device_id=device_id,
                                                                          user_id=user_id)
            logger.info("couch db notification action taken by update status: " + str(couchdb_update_status))

        logger.info("get_mfd_empty_canister_cart: for device_id: {} fetching "
                     "get_home_cart_data_for_mfd_canister_in_robot.".format(device_id))
        trolley_list = get_home_cart_data_for_mfd_canister_in_robot(device_id=device_id)
        logger.info("get_mfd_empty_canister_cart: for device_id: {} trolley_list {}.".format(device_id, trolley_list))
        if not trolley_list:
            logger.error("get_mfd_empty_canister_cart: for device_id: {} No mfd canisters available. "
                         "returning 13001".format(device_id))
            return error(13001)
        for trolley in trolley_list:
            trolley["drawer_data"] = get_mfd_trolley_drawer_data(trolley['trolley_id'])
        logger.error("get_mfd_empty_canister_cart: for device_id: {} returning data {}".format(device_id, trolley_list))
        return create_response(trolley_list)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except RealTimeDBException as e:
        logger.error(e)
        return error(11002, str(e))
    except Exception as e:
        logger.error(e)
        return error(1001, "Error in getting mfd empty canister data.")


@log_args_and_response
@validate(required_fields=["company_id", "system_id", "device_id", "batch_id", "user_id", "current_module",
                           "trolley_serial_number"])
def get_mfd_empty_canister_drawer(args):
    """
    Method to transfer mfd canisters from robot to trolley flow
    @param args: dict
    @return: json
    """
    device_id = args['device_id']
    batch_id = args['batch_id']
    system_id = args['system_id']
    company_id = args['company_id']
    current_module = int(args['current_module'])
    # user_id = int(args["user_id"])
    trolley_serial_number = args['trolley_serial_number']
    try:
        drop_pending_canister_count = check_drop_pending(device_ids=[device_id])
        if drop_pending_canister_count:
            return error(13003)
        logger.info("get_mfd_empty_canister_drawer: Fetching cart details.")
        trolley_list = get_home_cart_data_for_mfd_canister_in_robot(device_id=device_id)
        if not trolley_list:
            logger.error("No mfd canisters available in device: " + str(device_id))
            return create_response([])

        logger.info("get_mfd_empty_canister_drawer: trolley scanned- fetching trolley id based on serial number")
        trolley_id = get_device_id_from_serial_number(serial_number=trolley_serial_number, company_id=company_id)
        logger.info("scanned trolley_id {}".format(trolley_id))
        if not trolley_id or trolley_id != trolley_list[0]['trolley_id']:
            return error(1001, "Invalid trolley.")

        logger.info("fetching mfd transfers")
        # fetch no. of transfers of rts and non-rts mfd canister from robot to trolley
        if current_module == constants.MFD_TRANSFER_WIZARD_MODULES['RTS_SCREEN_WIZARD']:
            mfd_rts_canisters = get_mfd_rts_canisters(device_id=device_id, trolley_id=trolley_id, batch_id=batch_id)
            if mfd_rts_canisters:
                logger.info("rts canisters are there in robot so fetching empty trolley locations for rts canisters")
                empty_locations_list_for_rts_canisters = fetch_empty_trolley_locations_for_rts_canisters(
                    trolley_id=trolley_id)

                logger.info("recommending empty trolley drawers for rts canisters")
                recommended_drawers = recommend_drawers_based_on_transfers(
                    empty_locations_info_drawer_wise=empty_locations_list_for_rts_canisters,
                    transfer_count=len(mfd_rts_canisters)
                )
                logger.info("Recommended drawers: " + str(recommended_drawers))
                drawer_highlighted = False
                highlighted_drawer_sr_no = None
                for drawer in recommended_drawers:
                    if not drawer_highlighted:
                        drawer['drawer_to_highlight'] = True
                        drawer_highlighted = True
                        highlighted_drawer_sr_no = drawer['serial_number']
                    else:
                        drawer['drawer_to_highlight'] = False
                    drawer.pop('empty_locations', None)
                    drawer.pop('empty_locations_count', None)
                transfer_data = {"scanned_trolley": trolley_id}
                status, couch_db_doc = get_mfd_transfer_couch_db(device_id, system_id)
                couch_db_data = couch_db_doc.get("data", {})
                # trolley_id = couch_db_data.get("scanned_trolley", None)
                currently_scanned_drawer_sr_no = couch_db_data.get("currently_scanned_drawer_sr_no", None)
                # previously_scanned_drawer_sr_no = couch_db_data.get("previously_scanned_drawer_sr_no", None)
                if highlighted_drawer_sr_no and currently_scanned_drawer_sr_no != highlighted_drawer_sr_no:
                    transfer_data["previously_scanned_drawer_sr_no"] = currently_scanned_drawer_sr_no
                    transfer_data["currently_scanned_drawer_sr_no"] = highlighted_drawer_sr_no

                update_mfd_transfer_couch_db(device_id, system_id, transfer_data)
                return create_response(recommended_drawers)
            else:
                misplaced_canister_list, rts_canister_misplaced_count = mfd_misplaced_canister_dao(batch_id=batch_id,
                                                                                                   device_id=device_id,
                                                                                                   trolley_id=trolley_id)
                if misplaced_canister_list:
                    update_mfd_misplaced_count(device_id=device_id, system_id=system_id,
                                               batch_id=batch_id, module_id=current_module, company_id=company_id,
                                               trolley_serial_number=trolley_serial_number,
                                               count=len(misplaced_canister_list))
                return create_response([])

        elif current_module == constants.MFD_TRANSFER_WIZARD_MODULES['EMPTY_CANISTER_WIZARD']:
            query = get_empty_drawer_device(trolley_id)
            recommended_drawers = list()
            for drawer in query:
                drawer['drawer_to_highlight'] = True
                recommended_drawers.append(drawer)
            transfer_data = {"scanned_trolley": trolley_id}
            update_mfd_transfer_couch_db(device_id, system_id, transfer_data)
            return create_response(recommended_drawers)
        else:
            return error(1020, 'Invalid module')

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except RealTimeDBException as e:
        logger.error(e)
        return error(11002, str(e))
    except Exception as e:
        logger.error(e)
        return error(1001, "Error in getting mfd empty canister data.")


@log_args_and_response
@validate(required_fields=["company_id", "system_id"])
def get_cart_rts_canister_data(search_filters):
    """
    @param search_filters:  dict
    @return: json
    """
    clauses = list()

    filter_fields = search_filters['filter_fields']
    sort_fields = search_filters['sort_fields']
    paginate = search_filters['paginate']
    company_id = search_filters['company_id']
    system_id = search_filters['system_id']
    cart_serial_number = search_filters['cart_serial_number']
    batch_id = int(search_filters['batch_id'])

    status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                  system_id=system_id)
    couch_db_doc = document.get_document()

    logger.info("couch_db_data_mfs: " + str(couch_db_doc))
    if not couch_db_doc:
        return error(1020, 'Trolley not scanned')
    couch_db_data = couch_db_doc.get("data", {})
    if not couch_db_data:
        return error(1020, 'Trolley not scanned')
    trolley_seq = couch_db_data.get("trolley_seq", None)
    skip_misplaced_rts = couch_db_data.get("skip_misplaced_rts", False)
    required_cart_serial_number = couch_db_data.get("trolley_serial_number", None)
    cart_id = couch_db_data.get("trolley_id", None)
    if not trolley_seq or not required_cart_serial_number:
        return error(1020, 'Trolley not scanned')
    if cart_serial_number != required_cart_serial_number:
        return error(1020, 'Invalid cart for given system')

    filter_fields['home_cart_id'] = cart_id
    results = []
    count = 0

    try:
        available_trolley_seq = check_trolley_seq_for_batch(trolley_seq=trolley_seq,
                                                            batch_id=batch_id)
        if available_trolley_seq:
            results, count = db_get_rts_required_canisters(company_id=company_id,
                                                           filter_fields=filter_fields,
                                                           sort_fields=sort_fields,
                                                           paginate=paginate,
                                                           clauses=clauses,
                                                           trolley_seq=trolley_seq,
                                                           batch_id=batch_id,
                                                           skip_misplaced_rts=skip_misplaced_rts)

        response = {"mfd_canister_data": results,
                    "total_canisters": count}

        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_cart_rts_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except ValueError as e:
        logger.error(e, exc_info=True)
        return error(1020)
    except Exception as e:
        logger.error("Error in get_cart_rts_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_cart_rts_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_cart_rts_canister_data: " + str(e))


@log_args_and_response
@validate(required_fields=["company_id", "system_id", "cart_serial_number", "batch_id"])
def get_cart_rts_drug_data(search_filters: dict) -> dict:
    """
    returns rts drug data of a particular cart
    @param search_filters:  dict
    @return: json
    """
    # clauses = list()

    company_id = search_filters['company_id']
    system_id = search_filters['system_id']
    cart_serial_number = search_filters['cart_serial_number']
    batch_id = int(search_filters['batch_id'])

    # gets trolley seq required for current scan
    status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                  system_id=system_id)
    couch_db_doc = document.get_document()
    logger.info("couch_db_data_mfs: " + str(couch_db_doc))
    if not couch_db_doc:
        return error(1020, 'Trolley not scanned')
    couch_db_data = couch_db_doc.get("data", {})
    if not couch_db_data:
        return error(1020, 'Trolley not scanned')
    trolley_seq = couch_db_data.get("trolley_seq", None)
    required_cart_serial_number = couch_db_data.get("trolley_serial_number", None)
    cart_id = couch_db_data.get("trolley_id", None)
    if not trolley_seq or not required_cart_serial_number:
        return error(1020, 'Trolley not scanned')
    if cart_serial_number != required_cart_serial_number:
        return error(1020, 'Invalid cart for given system')

    try:
        results = db_get_rts_drugs(company_id, cart_id, trolley_seq, batch_id)

        response = {"rts_data": results, 'count': len(results)}

        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_cart_rts_drug_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except ValueError as e:
        logger.error(e, exc_info=True)
        return error(1020)
    except Exception as e:
        logger.error("Error in get_cart_rts_drug_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_cart_rts_drug_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_cart_rts_drug_data: " + str(e))


def get_mfd_mvs_canister_details(args):
    """
    Get location and drug data of active mfd canisters
    @param args: dict
    @return: json
    """
    try:
        company_id = args['company_id']
        mfd_canister_id = args['mfd_canister_id']
        pack_id = args['pack_id']
        mfd_canister_status = args.get('mfd_canister_status', None)
        mvs_filling = args.get('mvs_filling', False)
        mfd_canister_info, pack_slot_data = get_mfd_canister_data_query(company_id=company_id,
                                                                        mfd_canister_id=mfd_canister_id,
                                                                        mfd_canister_status=mfd_canister_status,
                                                                        pack_id=pack_id,
                                                                        mvs_filling=mvs_filling)
        if not pack_slot_data:
            return error(1000, 'Invalid canister scanned.')

        response = {'mfd_canister_info': mfd_canister_info, 'pack_slot_data': pack_slot_data}

        return create_response(response)

    except Exception as e:
        logger.error(e)
        return error(2001, "Error in getting mfd canister details.")


@log_args_and_response
@validate(required_fields=["company_id", "mfd_canister_id", "user_id"])
def activate_mfd_canister(data_dict: dict) -> dict:
    """
    This Method will mark canister activate and add it is trolley association and regenerates label
    @param data_dict: data dict with required keys "company_id", "mfd_canister_id", "user_id"
    @return: dict - generated label name and canister data
    """
    logger.info("Inside activate_mfd_canister.")
    company_id = data_dict["company_id"]
    mfd_canister_id = data_dict["mfd_canister_id"]
    user_id = data_dict["user_id"]
    response = {"is_label_generated": False,
                "label_name": None,
                }
    update_mfs_data = False
    try:
        print_required = False
        # fetch rfid, product id from odoo based on mfd_canister_id
        logger.info("fetching canister details from on mfd_canister_id- " + str(mfd_canister_id))

        with db.transaction():
            canister_data = dict()
            mfd_device_canister_count = dict()
            # mfd_trolley_data = dict()
            home_found = False
            rts_done_required = list()

            # fetch rfid, product id from odoo based on mfd_canister_serial_number
            logger.info("fetching canister details based on mfd_canister_id- " + str(mfd_canister_id))
            data = {"mfd_canister_id": mfd_canister_id}
            canister_query = get_mfd_canister_data_by_ids([mfd_canister_id], company_id)
            for record in canister_query:
                if record['device_type_id'] == settings.DEVICE_TYPES['Manual Filling Device']:
                    update_mfs_data = True
                    mfs_id = record['current_device_id']
                    system_id = record['system_id']
                    location = record['current_location_number']
                if record['mfd_canister_status_id'] in [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                        constants.MFD_CANISTER_MVS_FILLING_REQUIRED]:
                    rts_done_required.append(record['mfd_canister_id'])
                canister_data = record
            if rts_done_required:
                return error(1000, 'RTS/Manual filling is pending')
            if not canister_data:
                return error(1001, 'Invalid mfd_canister_id or company_id')
            rfid = canister_data["rfid"]
            product_id = canister_data["erp_product_id"]
            logger.info("fetched canister data - " + str(canister_data))

            # get mfd home cart canister count
            mfd_can_device_query = get_mfd_canister_home_cart_count(company_id)
            for record in mfd_can_device_query:
                if record['home_cart_id'] and record['home_cart_id'] not in mfd_device_canister_count.keys():
                    mfd_device_canister_count[record['home_cart_id']] = {
                        'mfd_canister_count': record['mfd_canister_count'],
                        'home_cart_name': record['home_cart_name']}

            # get mfd trolley device data
            mfd_trolley_data_query = get_active_mfd_trolley(company_id)
            for record in mfd_trolley_data_query:
                if record['id'] not in mfd_device_canister_count.keys():
                    mfd_device_canister_count[record['id']] = {'mfd_canister_count': 0,
                                                               'home_cart_name': record['name']}

            # get home_cart for canister
            for home_device, home_device_info in mfd_device_canister_count.items():
                canister_count = home_device_info['mfd_canister_count']
                if canister_count < constants.MFD_TROLLEY_CANISTER_CAPACITY:
                    home_cart_device = home_device
                    home_found = True
                    break

            if not home_found:
                return error(1000, "No MFD Trolley available.")

            # Activate canister data in mfd_canister_master
            latest_status_history_data, canister_home_cart_dict = get_latest_mfd_status_history_data([mfd_canister_id],
                                                                                                     None)
            logger.info(
                "updating canister data in mfd_canister_master for mfd_canister_id: {}".format(mfd_canister_id))
            update_status = db_mark_mfd_canister_activate({home_cart_device: [mfd_canister_id]})

            if update_status:
                # checking if print is required getting last history data to find last trolley
                if canister_home_cart_dict.get(mfd_canister_id, None):
                    previous_home_cart = canister_home_cart_dict[mfd_canister_id]['home_cart_device']
                    if home_cart_device != previous_home_cart:
                        print_required = True
                        data["regenerate"] = True
                # adding latest history data
                db_update_canister_active_status({home_cart_device: [mfd_canister_id]},
                                                 constants.MFD_CANISTER_ACTIVATED, user_id)

                # generate mfd canister label
                label_response = json.loads(mfd_canister_label(data))
                if label_response["status"] == settings.SUCCESS_RESPONSE:
                    response["is_label_generated"] = True
                    response["label_name"] = label_response["data"]["label_name"]

                if update_mfs_data:
                    mfs_update_active_canister({'system_id': system_id,
                                                'location': location,
                                                'rfid': rfid,
                                                'mfs_id': mfs_id})

                response["rfid"] = rfid
                response["mfd_canister_id"] = mfd_canister_id
                response["product_id"] = product_id
                response["already_registered"] = True
                response['home_cart_device'] = home_cart_device
                response['print_required'] = print_required
                response['home_cart_device_name'] = mfd_device_canister_count[home_cart_device]['home_cart_name']

        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["company_id", "mfd_canister_ids", "user_id"])
def mark_canister_found(data_dict: dict) -> dict:
    """
    This Method will mark canister deactivates and remove it is trolley association
    @param data_dict: data dict with required keys "company_id", "mfd_canister_id", "user_id"
    @return: dict - generated label name and canister data
    """
    logger.info("Inside deactivate_mfd_canister: {}".format(data_dict))
    company_id = data_dict["company_id"]
    mfd_canister_ids = data_dict["mfd_canister_ids"]
    user_id = data_dict["user_id"]
    mfd_canister_home_cart_dict = defaultdict(list)
    mfd_empty_drawer_dict = defaultdict(list)
    mfd_filled_drawer_dict = defaultdict(list)
    valid_canister_set = set()
    canister_location_dict = dict()
    mfd_canister_drawer_dict = dict()
    rts_done_required = list()
    try:
        with db.transaction():

            # validate mfd canister
            logger.info('Validating_mfd_canister_for: {} and company_id: {}'.format(mfd_canister_ids, company_id))
            canister_query = get_mfd_canister_data_by_ids(mfd_canister_ids, company_id)
            for record in canister_query:
                if record['state_status'] == constants.MFD_CANISTER_MISPLACED:
                    mfd_canister_home_cart_dict[record['home_cart_id']].append(record['mfd_canister_id'])
                    valid_canister_set.add(record['mfd_canister_id'])
                    if record['mfd_canister_status_id'] in [constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                            constants.MFD_CANISTER_RTS_REQUIRED_STATUS]:
                        mfd_filled_drawer_dict[record['home_cart_id']].append(record['mfd_canister_id'])
                    else:
                        mfd_empty_drawer_dict[record['home_cart_id']].append(record['mfd_canister_id'])
            if rts_done_required:
                return error(1000, 'RTS is pending')
            if set(mfd_canister_ids) != valid_canister_set:
                return error(1020, 'Invalid mfd_canister_id or company_id')

            # update mfd canister data
            logger.info('activating_mfd_canister_ids as found: {}'.format(mfd_canister_ids))

            if mfd_canister_home_cart_dict:
                update_status = mfd_canister_found_update_status(mfd_canister_home_cart_dict, user_id)
            exclude_locations = list()
            for home_cart_id, mfd_can_ids in mfd_empty_drawer_dict.items():
                empty_location = get_empty_locations(constants.MFD_TROLLEY_EMPTY_DRAWER_TYPE, len(mfd_can_ids),
                                                     home_cart_id,
                                                     exclude_locations)
                exclude_locations.extend(empty_location)
                if len(mfd_can_ids) != len(empty_location):
                    raise ValueError(1020, 'No empty location available')
                for index, mfd_can in enumerate(mfd_can_ids):
                    canister_location_dict[mfd_can] = empty_location[index]

            for home_cart_id, mfd_can_ids in mfd_filled_drawer_dict.items():

                empty_locations_list_for_rts_canisters = fetch_empty_trolley_locations_for_rts_canisters(
                    trolley_id=home_cart_id)
                if not empty_locations_list_for_rts_canisters:
                    raise ValueError(1020, 'No empty location available')
                # todo: currently we receive one canister so not checking number for number of location in advance
                logger.info("recommending empty trolley drawers for rts canisters")
                recommended_drawers = recommend_drawers_based_on_transfers(
                    empty_locations_info_drawer_wise=empty_locations_list_for_rts_canisters,
                    transfer_count=len(mfd_can_ids)
                )
                logger.info("Recommended drawers: " + str(recommended_drawers))
                if recommended_drawers:
                    # recommend loc for each canister
                    for mfd_can_id in mfd_can_ids:
                        for index, drawer in enumerate(recommended_drawers):
                            if drawer['empty_locations_count'] > 0:
                                mfd_canister_drawer_dict[mfd_can_id] = drawer['drawer_name']
                                canister_location_dict[mfd_can_id] = drawer['empty_locations'][0]
                                recommended_drawers[index]['empty_locations'] = recommended_drawers[index][
                                                                                    'empty_locations'][1:]
                                recommended_drawers[index]['empty_locations_count'] -= 1
                            else:
                                continue

            if canister_location_dict:
                update_mfd_canister_location(canister_location_dict)

        return create_response({'canister_update_status': update_status,
                                'canister_drawer_suggestion': mfd_canister_drawer_dict})
    except ValueError as e:
        logger.info("In mark_canister_found: {}".format(e))
        return error(1000, 'No empty location available')
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in mark_canister_found: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in mark_canister_found {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in mark_canister_found: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in mark_canister_found: " + str(e))


@log_args_and_response
@validate(required_fields=["company_id", "mfd_canister_ids", "user_id"])
def update_mfd_canister_to_misplaced(data_dict: dict) -> dict:
    """
    This Method will mark canister deactivates and remove it is trolley association
    @param data_dict: data dict with required keys "company_id", "mfd_canister_id", "user_id"
    @return: dict - generated label name and canister data
    """
    logger.info("Inside deactivate_mfd_canister: {}".format(data_dict))
    company_id = data_dict["company_id"]
    mfd_canister_ids = data_dict["mfd_canister_ids"]
    user_id = data_dict["user_id"]
    mfd_canister_home_cart_dict = defaultdict(list)
    valid_canister_set = set()
    canister_history_update_list = list()
    try:
        with db.transaction():

            # validate mfd canister
            logger.info('In update_mfd_canister_to_misplaced: Validating_mfd_canister_for: {} and company_id: {}'.format(mfd_canister_ids, company_id))
            canister_query = get_mfd_canister_data_by_ids(mfd_canister_ids, company_id)
            for record in canister_query:
                mfd_canister_home_cart_dict[record['home_cart_id']].append(record['mfd_canister_id'])
                if record['location_id'] is not None:
                    history_dict = {
                        'mfd_canister_id': record['mfd_canister_id'],
                        'current_location_id': None,
                        'user_id': user_id,
                        'is_transaction_manual': True
                    }
                    canister_history_update_list.append(history_dict)
                valid_canister_set.add(record['mfd_canister_id'])
            if set(mfd_canister_ids) != valid_canister_set:
                return error(1020, 'Invalid mfd_canister_id or company_id')

            # update mfd canister data
            logger.info('In update_mfd_canister_to_misplaced: deactivating_mfd_canister_ids: {}'.format(mfd_canister_ids))
            update_status = mark_mfd_canister_misplaced(mfd_canister_home_cart_dict)

            if update_status:
                # update in canister status history
                db_update_canister_active_status(mfd_canister_home_cart_dict, constants.MFD_CANISTER_MARKED_MISPLACED,
                                                 user_id)
                # update in transfer history
                if canister_history_update_list:
                    mfd_canister_history_update = update_mfd_canister_history(canister_history_update_list)
                    logger.info('In update_mfd_canister_to_misplaced: mfd canister history updated: {}'.format(mfd_canister_history_update))
        return create_response(update_status)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_mfd_canister_to_misplaced: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_mfd_canister_to_misplaced {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_mfd_canister_to_misplaced: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_mfd_canister_to_misplaced: " + str(e))


def update_mfd_misplaced_count(device_id, system_id, batch_id, module_id, company_id, trolley_serial_number, count=0):
    try:
        logger.info("update_canister_transfer_couch_db {}, {}".format(device_id, system_id))
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = 'mfd_transfer_{}'.format(device_id)
        table = cdb.get(_id=id)

        if table and table.get('data', {}):
            table['data']['timestamp'] = get_current_date_time()
            table['data']['uuid'] = uuid1().int
            table['data']['misplaced_count'] = count

            # save only if time stamp updated
            cdb.save(table)

            # Removed update of wizard on count 0 as it should be handled from FE only
            # if count == 0:
            #     args = {'batch_id': batch_id,
            #             'system_id': system_id,
            #             'device_id': device_id,
            #             'module_id': module_id,
            #             'company_id': company_id,
            #             'trolley_serial_number': trolley_serial_number}
            #     update_mfd_transfer_status(args)
            return True
    except Exception as e:
        logger.error("Error in update_mfd_misplaced_count {}".format(e))
        return True


@log_args_and_response
def mfd_canister_found_update_status(mfd_canister_home_cart_dict: dict, user_id) -> bool:
    """
    Method to validate mfd canister against company
    @mfd_canister_home_cart_dict = list of canisters to be validated
    @return: bool
    """

    try:
        update_status = db_mark_mfd_canister_activate(mfd_canister_home_cart_dict)

        if update_status:
            db_update_canister_active_status(mfd_canister_home_cart_dict, constants.MFD_CANISTER_FOUND, user_id)
        return update_status
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


def mfd_mvs_filling_req_canister_found(mfd_canister_home_cart_dict: dict, user_id) -> bool:
    """
    Method to validate mfd canister against company
    @mfd_canister_home_cart_dict = list of canisters to be validated
    @return: bool
    """

    try:
        update_status = db_mark_mfd_canister_activate(mfd_canister_home_cart_dict)

        if update_status:
            db_update_canister_active_status(mfd_canister_home_cart_dict, constants.MFD_CANISTER_FOUND, user_id)
        return update_status
    except (IntegrityError, InternalError) as e:
        raise e


@validate(required_fields=["system_id", "location"])
def mfs_update_active_canister(data_dict: dict) -> bool:
    """
    This Method will update it is association with mfd-analysis and update couch db doc
    """
    system_id = data_dict['system_id']
    mfs_id = data_dict['mfs_id']
    loc = str(data_dict['location'])
    rfid = data_dict['rfid']
    canister_mfs_association_dict = dict()
    activate_mfd_can_dict = dict()
    try:
        status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                      system_id=system_id)
        couch_db_doc = document.get_document()
        logger.info('current_couch_db_data' + str(couch_db_doc))

        batch_id, current_mfs_batch, canister_location_mapping = get_current_mfs_batch_data(mfs_id)

        couch_db_canister_data = couch_db_doc["data"].get('canister_data', {})
        trolley_id = couch_db_doc["data"].get('trolley_id', None)
        trolley_name = couch_db_doc["data"].get('name', None)
        current_canister_data = get_canister_data_by_rfid(rfid)
        if not current_canister_data:
            return False
        current_canister_id = current_canister_data['id']
        home_cart = current_canister_data['home_cart_id']
        current_can_state_status = current_canister_data['state_status']
        analysis_id = current_mfs_batch[loc]['analysis_id']
        associated_canister_id = current_mfs_batch[loc]['canister_id']
        canister_status = current_mfs_batch[loc]['status']
        if current_mfs_batch.get(loc, None):
            # check if canister is bound with particular location or not. If bounded then give error messages
            # for invalid canister at that location. If not then check validity of currently
            if associated_canister_id:
                if associated_canister_id != current_canister_id:
                    # message_location = None
                    if current_canister_data['status_id'] in [constants.MFD_CANISTER_SKIPPED_STATUS,
                                                              constants.MFD_CANISTER_DROPPED_STATUS,
                                                              constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                              constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                              constants.MFD_CANISTER_PENDING_STATUS]:
                        error_message = constants.MFD_ERROR_MESSAGES['WRONG_CAN_DETECTED'] \
                            .format(associated_canister_id)
                        message_location = current_mfs_batch[loc]['mfs_location']
                    else:
                        if current_canister_data['status_id'] != constants.MFD_CANISTER_IN_PROGRESS_STATUS:
                            if current_canister_data['transfer_done'] or \
                                    current_canister_id not in canister_location_mapping:
                                error_message = constants.MFD_ERROR_MESSAGES['TROLLEY_PLACEMENT_REQUIRED'] \
                                    .format(current_canister_data['id'],
                                            current_canister_data['trolley_drawer_name'],
                                            current_canister_data['trolley_name'])
                                message_location = current_canister_data['trolley_drawer_name']
                            else:
                                error_message = constants.MFD_ERROR_MESSAGES['WRONG_PLACEMENT'] \
                                    .format(current_canister_id,
                                            canister_location_mapping[current_canister_id]['display_location'])
                                message_location = canister_location_mapping[current_canister_id][
                                    'display_location']

                        else:
                            error_message = constants.MFD_ERROR_MESSAGES['WRONG_CAN_DETECTED'] \
                                .format(associated_canister_id)
                            message_location = current_mfs_batch[loc]['mfs_location']
                    couch_db_canister_data[loc].update({
                        'current_canister_id': current_canister_id,
                        'dest_quadrant': current_mfs_batch[loc]['dest_quadrant'],
                        'error_message': error_message,
                        'is_in_error': True,
                        'message_location': message_location,
                        'required_canister_id': associated_canister_id})
                else:
                    if current_canister_data['transfer_done']:
                        error_message = constants.MFD_ERROR_MESSAGES['TROLLEY_PLACEMENT_REQUIRED'] \
                            .format(current_canister_data['id'],
                                    current_canister_data['trolley_drawer_name'],
                                    current_canister_data['trolley_name'])
                        couch_db_canister_data[loc].update({
                            'current_canister_id': current_canister_id,
                            'dest_quadrant': current_mfs_batch[loc]['dest_quadrant'],
                            'error_message': error_message,
                            'is_in_error': True,
                            'transfer_done': True,
                            'message_location': current_canister_data['trolley_drawer_name'],
                            'required_canister_id': current_canister_id})
                    else:
                        couch_db_canister_data[loc].update({
                            'current_canister_id': current_canister_id,
                            'dest_quadrant': current_mfs_batch[loc]['dest_quadrant'],
                            'error_message': None,
                            'is_in_error': False,
                            'transfer_done': False,
                            'message_location': None,
                            'required_canister_id': current_canister_id})
            else:
                # check if canister is required on a particular location or not. If required then validate else
                # return no can required error message
                if canister_status != constants.MFD_CANISTER_SKIPPED_STATUS:
                    # checking validity of canister
                    error_message = None
                    is_in_error = False
                    message_location = None
                    if current_can_state_status == constants.MFD_CANISTER_INACTIVE:
                        error_message = constants.MFD_ERROR_MESSAGES['DEACTIVATE_CANISTER']
                        is_in_error = True
                    elif home_cart != trolley_id:
                        error_message = constants.MFD_ERROR_MESSAGES['WRONG_HOME_CART'].format(trolley_name)
                        is_in_error = True
                    elif home_cart == trolley_id and not current_canister_data['status_id'] or \
                            current_canister_data['status_id'] in [constants.MFD_CANISTER_SKIPPED_STATUS,
                                                                   constants.MFD_CANISTER_DROPPED_STATUS,
                                                                   constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                                   constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                                   constants.MFD_CANISTER_PENDING_STATUS]:
                        canister_mfs_association_dict[analysis_id] = current_canister_id
                        if current_can_state_status == constants.MFD_CANISTER_MISPLACED:
                            activate_mfd_can_dict[home_cart].append(current_canister_id)
                    else:
                        if canister_location_mapping.get(current_canister_id, None):
                            error_message = constants.MFD_ERROR_MESSAGES['WRONG_PLACEMENT'] \
                                .format(current_canister_id,
                                        canister_location_mapping[current_canister_id]['display_location'])
                            is_in_error = True
                            message_location = canister_location_mapping[current_canister_id][
                                'display_location']
                        else:
                            if home_cart != trolley_id:
                                error_message = constants.MFD_ERROR_MESSAGES['WRONG_HOME_CART'].format(
                                    trolley_name)
                                is_in_error = True
                            else:
                                error_message = constants.MFD_ERROR_MESSAGES['TROLLEY_PLACEMENT_REQUIRED'] \
                                    .format(current_canister_data['id'],
                                            current_canister_data['trolley_drawer_name'],
                                            current_canister_data['trolley_name'])
                                is_in_error = True
                                message_location = current_canister_data['trolley_drawer_name']
                    couch_db_canister_data[loc].update({
                        'current_canister_id': current_canister_id,
                        'transfer_done': False,
                        'error_message': error_message,
                        'is_in_error': is_in_error,
                        'message_location': message_location,
                        'dest_quadrant': current_mfs_batch[loc]['dest_quadrant'],
                        'required_canister_id': current_canister_id})
                else:
                    couch_db_canister_data[loc].update({
                        'current_canister_id': current_canister_id,
                        'error_message': constants.MFD_ERROR_MESSAGES['NO_CAN_REQ'],
                        'message_location': None,
                        'is_in_error': True,
                        'required_canister_id': None})
        else:
            # The data will not be available if no placement was required at that location
            couch_db_canister_data[loc] = {
                'canister_required': False,
                'is_in_error': True,
                'current_canister_id': current_canister_id,
                'required_canister_id': None,
                'message_location': None,
                'error_message': constants.MFD_ERROR_MESSAGES['NO_CAN_REQ']
            }
        if canister_mfs_association_dict:
            status = associate_canister_with_analysis(canister_mfs_association_dict)
            logger.info(status)

        status, doc = update_document_with_revision(document, couch_db_doc, False)
        logger.info('In mfs_update_active_canister: update document status: {}, document:{}'.format(status, doc))
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
