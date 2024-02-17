import math
from collections import defaultdict
from decimal import Decimal
from typing import List, Dict, Any, Tuple, Set, Optional
from uuid import uuid4
import re

import couchdb
from peewee import InternalError, IntegrityError, DoesNotExist, DataError
from pytz import UnknownTimeZoneError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.local.lang_us_en import err
from dosepack.utilities.utils import (get_current_date_time, log_args_and_response,
                                      get_current_day_date_end_date_by_timezone, log_args,
                                      get_current_datetime_by_timezone)
from dosepack.validation.validate import validate
from realtime_db.dp_realtimedb_interface import Database
from settings import (SUCCESS_RESPONSE, GENERIC_FLAG, CONST_COUCHDB_SERVER_URL, FACILITY_DISTRIBUTION_PENDING_STATUS,
                      WEEKDAYS, SATURDAY, SUNDAY, AUTOMATIC_PER_HOUR, AUTOMATIC_PER_DAY_HOURS, AUTOMATIC_SATURDAY_HOURS,
                      AUTOMATIC_SUNDAY_HOURS, BRAND_FLAG, NON_DRUG_FLAG, MANUAL, ROBOT)
from src.dao.alternate_drug_dao import get_alternate_drug_dao
from src.dao.drug_dao import update_drug_status_dao, get_drug_and_bottle_information_by_drug_id_dao, \
    get_drug_data_from_ndc
from src.dao.pack_analysis_dao import update_batch_change_tracker_after_replenish_skipped_canister, \
    update_status_in_pack_analysis_details_for_out_of_stock
from src.exceptions import (DrugInventoryInternalException, DrugInventoryValidationException, TokenFetchException,
                            RealTimeDBException, APIFailureException, DataDoesNotExistException, TokenMissingException,
                            MissingParameterException)
from src.constants import (NUMBER_OF_DAYS_TO_ORDER, DRUG_INVENTORY_MANAGEMENT_DELETED_ID, EPBM_DOSEPACK_DEPARTMENT,
                           DRUG_INVENTORY_MANAGEMENT_ADDED_ID, DRUG_INVENTORY_MANAGEMENT_UPDATED_ID,
                           DRUG_INVENTORY_MANAGEMENT_ADDED_TO_CART_ID, FILTER_PRE_ORDER_EPBM_BATCH_ORDER_DATA,
                           FILTER_AVAILABLE_EPBM_BATCH_ORDER_DATA, DRUG_INVENTORY_MANAGEMENT_ORDER_PENDING_ID,
                           EPBM_INVENTORY_COUCH_DB, MANUAL_USER_COUNT, MANUAL_PER_HOUR, MANUAL_PER_DAY_HOURS,
                           MANUAL_SUNDAY_HOURS, MANUAL_SATURDAY_HOURS, MANUAL_CAPACITY, NUMBER_OF_DAYS_TO_FETCH_PO,
                           EPBM_VIBRANT_DEPARTMENT, USAGE_TO_BUFFER, DRUG_INVENTORY_MANAGEMENT_BYPASSED)

from src.dao.canister_dao import epbm_get_available_alternate_canister, get_canister_data_by_txr, \
     update_replenish_based_on_system, \
    get_canister_data_by_ndc_and_company_id_dao
from src.dao.drug_inventory_dao import (get_drug_info_based_on_ndc_dao, get_batch_drug_data, delete_batch_drug_data,
                                        get_records_by_facility_dist_id_and_dept, update_adhoc_drug_request_by_ndc,
                                        update_alternate_drug_option_by_order_data, delete_adhoc_drug_request_data,
                                        populate_batch_drug_data, get_inventory_order_data_by_facility_dist_id,
                                        populate_batch_order_data, update_batch_drug_data_by_fndc_txr_daw_and_dept,
                                        get_drug_data_from_ndc_list, update_batch_drug_order_data_by_batch_drug_data_id,
                                        validate_facility_dist_id_by_company_id,
                                        update_batch_drug_data_by_ndc, populate_batch_drug_request_mapping_data,
                                        get_mapping_data_by_facility_dist_id, update_txr_in_drug_master_and_unique_drug,
                                        populate_alternate_drug_option_by_order_data, get_batch_drug_data_id_from_ndc,
                                        populate_pre_order_missing_ndc, get_drug_data_by_ndc_list,
                                        get_canister_data_by_unique_drug_id_list, get_cur_inventory_mapping_data,
                                        insert_current_inventory_mapping_data, delete_current_inventory_mapping,
                                        update_current_inventory_mapping_by_id, populate_batch_pack_data,
                                        get_batch_drug_data_by_facility_dist_id_and_dept, get_fndc_txr_with_canister,
                                        get_facility_dist_id_status, get_reserve_ndc_by_facility_dist_id,
                                        get_data_for_modified_drug_list, get_system_setting_by_system_ids,
                                        get_manual_pack_ids_for_upcoming_days,
                                        get_auto_pack_ids_for_upcoming_days, get_records_by_unique_id_and_dept,
                                        populate_adhoc_drug_request, update_adhoc_drug_request_by_fndc_txr_daw,
                                        get_facility_dist_data_by_id, update_facility_dist_data_by_id,
                                        get_last_order_data_ny_ndc, populate_batch_drug_and_order_data,
                                        update_adhoc_drug_request_by_fndc_txr_daw_case, drug_inventory_adjustment)
from src.dao.inventory_dao import get_or_create_unique_drug
from src.dao.misc_dao import get_company_setting_by_company_id
from src.dao.couch_db_dao import get_couch_db_database_name

from src.service.local_drug_inventory import update_local_inventory_by_ack_po
from src.service.misc import get_user_from_header_token, get_current_user, get_token, get_users_by_ids
from sync_drug_data.update_drug_data import create_drug_sync_history, get_drug_from_ips
from utils.auth_webservices import send_email_for_drug_req_check_failure, send_email_for_same_ndc_diff_txr
from utils.drug_inventory_webservices import (post_request_data_to_drug_inventory, get_data_by_ndc_from_drug_inventory,
                                              get_current_inventory_data, fetch_pre_order_data)

logger = settings.logger


@log_args_and_response
@validate(required_fields=["ndc_list", "unique_id"])
def epbm_alternate_canisters(args: Dict[str, Any]) -> str:
    """
    Function to return alternate ndc data for which canisters are present for given company.
    """
    ext_ndc_list: str = args['ndc_list']
    unique_id: str = args['unique_id']
    ndc_canister_data_list: List[Dict[str, Any]] = list()
    invalid_ndc_list: List[str] = list()
    response: Dict[str, Any] = dict()
    try:
        ndc_list: List[str] = list(ext_ndc_list.split(','))
        if unique_id.find("##") == 1:
            company_facility_dist_id_list: List[Any] = unique_id.split('##')
        elif unique_id.find("@@") == 1:
            company_facility_dist_id_list: List[Any] = unique_id.split('@@')
        else:
            return error(20004, "The given unique_id {} is not valid.".format(unique_id))

        if len(company_facility_dist_id_list) != 2:
            raise ValueError('Invalid identifier')
        company_id: int = int(company_facility_dist_id_list[0])
        drug_info: Dict[str, Any] = get_drug_info_based_on_ndc_dao(ndc_list=ndc_list)

        for ndc in ndc_list:
            if ndc in drug_info:
                canister_ndc_list: List[Dict[str, Any]] = epbm_get_available_alternate_canister(drug_info[ndc]['txr'],
                                                                                                company_id)
                ndc_canister_data_list.append({"ndc": ndc, "alternate_canister_data": canister_ndc_list})

            else:
                logger.error("Invalid ndc - " + str(ndc))
                invalid_ndc_list.append(ndc)

        response['ndc_canister_data'] = ndc_canister_data_list
        response["invalid_ndc_list"] = invalid_ndc_list
        logger.info("Response of epbm_alternate_canisters {}".format(response))
        return create_response(response)

    except ValueError as e:
        logger.error("Error in getting alternate canister data {}".format(e))
        return error(20004, "The given unique_id {} doesn't exist in the database.".format(unique_id))
    except Exception as e:
        logger.error("Error in getting canister data {}".format(e))
        return error(1000, "Error in getting canister data")


@log_args_and_response
@validate(required_fields=["facility_dist_id", "company_id"])
def get_drug_data_by_facility_dis_id(data_dict: Dict[str, Any]) -> str:
    """
    Place the request for the required drug quantity to the drug inventory.
    """

    facility_dist_id: int = int(data_dict["facility_dist_id"])
    company_id: int = int(data_dict["company_id"])
    pack_id_set: Set[int] = set()
    batch_pack_data: List[Dict[str, Any]] = list()
    drug_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = dict()
    can_drug_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]]
    man_drug_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]]
    request_mapping: Dict[int, Dict[Any, Any]]
    req_department_list: List[str] = list()
    is_exception_or_error: bool = False
    bypassed = False
    try:
        # get the user id from token
        user_data: Dict[str, Any] = get_user_from_header_token()
        if user_data is not None:
            user_id = int(user_data["id"])
        else:
            return error(5019)

        if company_id and facility_dist_id:
            if not validate_facility_dist_id_by_company_id(company_id=company_id, facility_dist_id=facility_dist_id):
                return error(20003)

        unique_id = str(company_id) + "##" + str(facility_dist_id)

        # get the drug data for the packs corresponding to the given facility_dist_id
        current_pack_drug_data: List[Any] = get_batch_drug_data(facility_dist_id=facility_dist_id)

        # get the pack_ids from the current_pack_drug_data to store the transaction data in BatchPackData.
        for data in current_pack_drug_data:
            for pack_id in str(data["pack_id"]).split(","):
                pack_id_set.add(int(pack_id))

        batch_pack_data.append({"unique_id": unique_id,
                                "pack_id_list": list(pack_id_set)})

        # check if there is any drug to be ordered for the given facility_dist_id
        if not len(current_pack_drug_data) > 0:
            update_drug_inventory_couch_db_status(company_id=company_id, facility_dist_id=facility_dist_id,
                                                  status=DRUG_INVENTORY_MANAGEMENT_ADDED_TO_CART_ID)
            return create_response("There are no drugs to be ordered.")

        # group the data by txr & daw
        drug_data, request_mapping = get_drugs_to_order_by_facility_dist_id(drug_data=drug_data,
                                                                            pack_drug_data=current_pack_drug_data)

        # differentiate the drugs by drug type (canister / manual)
        data_dict: Dict[str, Any] = differentiate_by_drug_type(order_data=drug_data, company_id=company_id)

        canister_order_drugs: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = data_dict["canister_order_drugs"]
        manual_order_drugs: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = data_dict["manual_order_drugs"]

        # ordering for the canister_drugs
        order_req, inventory_mapping, bypassed = prepare_order_data_and_place_order(
            robot_order_data=canister_order_drugs,manual_order_data=manual_order_drugs, unique_id=unique_id,
            user_id=user_id, department=EPBM_DOSEPACK_DEPARTMENT,
            facility_dist_id=facility_dist_id, local_di=True,
            company_id=company_id, request_mapping=request_mapping,
            batch_pack_data=batch_pack_data)
        if order_req:
            req_department_list.append(EPBM_DOSEPACK_DEPARTMENT)

        # # ordering for the manual_drugs
        # order_req, inventory_mapping, bypassed = prepare_order_data_and_place_order(
        # robot_order_data=manual_order_drugs, unique_id=unique_id,
        #                                     user_id=user_id, department=EPBM_VIBRANT_DEPARTMENT,
        #                                     facility_dist_id=facility_dist_id, local_di=False,
        #                                     company_id=company_id, bypassed=bypassed)
        # if order_req:
        #     req_department_list.append(EPBM_VIBRANT_DEPARTMENT)

        if not bypassed:
            # update the couchDB doc for the OrderPending status.
            if len(req_department_list) > 0:
                trigger_call: bool = process_dept_for_facility_dist_id(facility_dist_id=facility_dist_id, user_id=user_id,
                                                                       req_dept_list=req_department_list)
                update_drug_inventory_couch_db_status(company_id=company_id, facility_dist_id=facility_dist_id,
                                                      trigger_call=trigger_call,
                                                      status=DRUG_INVENTORY_MANAGEMENT_ORDER_PENDING_ID)
            else:
                update_drug_inventory_couch_db_status(company_id=company_id, facility_dist_id=facility_dist_id,
                                                      trigger_call=True, status=DRUG_INVENTORY_MANAGEMENT_ORDER_PENDING_ID)

            # updating the AlternateDrugOption table with the on hand qty.
            update_ordered_drug_data(company_id=company_id, facility_dist_id=facility_dist_id, user_id=user_id)
        else:
            # Update couchdb with bypassed status
            update_drug_inventory_couch_db_status(company_id=company_id, facility_dist_id=facility_dist_id,
                                                  status=DRUG_INVENTORY_MANAGEMENT_BYPASSED)

        return create_response(SUCCESS_RESPONSE)

    except TokenMissingException as e:
        logger.error(e, exc_info=True)
        is_exception_or_error = True
        return error(20006)
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        is_exception_or_error = True
        return error(2001)
    except APIFailureException as e:
        logger.error(e, exc_info=True)
        is_exception_or_error = True
        return error(20002, "{}".format(e))
    except TokenFetchException as e:
        logger.error(e, exc_info=True)
        is_exception_or_error = True
        return error(20001, "{}".format(e))
    except DrugInventoryInternalException as e:
        logger.error(e, exc_info=True)
        is_exception_or_error = True
        return error(20009, "{}".format(e))
    except DrugInventoryValidationException as e:
        logger.error(e, exc_info=True)
        is_exception_or_error = True
        return error(20010, "{}".format(e))
    except MissingParameterException as e:
        logger.error(e, exc_info=True)
        is_exception_or_error = True
        return error(1001, "{}".format(e))
    except RealTimeDBException as e:
        logger.error(e, exc_info=True)
        is_exception_or_error = True
        return error(11002)
    except Exception as e:
        logger.error(e, exc_info=True)
        is_exception_or_error = True
        return error(2001)
    finally:
        if is_exception_or_error:
            try:
                update_drug_inventory_couch_db_status(company_id=company_id, facility_dist_id=facility_dist_id,
                                                      status=DRUG_INVENTORY_MANAGEMENT_ORDER_PENDING_ID)
            except RealTimeDBException as e:
                logger.error(e, exc_info=True)
                return error(11002)
            except Exception as e:
                logger.error(e, exc_info=True)
                return error(2001)


@log_args_and_response
def get_drugs_to_order_by_facility_dist_id(drug_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]],
                                           pack_drug_data: List[Any], drug_list: List[Any] = []) -> \
        Tuple[Dict[str, Dict[int, Dict[str, Dict[str, Any]]]], Dict[int, Dict[Any, Any]]]:
    """
    This groups the data by txr & daw, and returns the list of unique drugs to be ordered and the mapping_dict
    """
    mapping_dict: Dict[int, Dict[Any, Any]] = dict()
    req_drug_data: Dict[str, Any]
    cur_inventory_mapping_data: Dict[str, List[Dict[str, Any]]]
    try:
        for record in pack_drug_data:
            if drug_list and record['ndc'] not in drug_list:
                continue
            if record["txr"] is None:
                # get the txr for the given NDC from drug Inventory
                txr, unique_drug_id = get_and_update_txr_for_ndc(record)

                record["txr"] = txr
                record["unique_drug_id"] = unique_drug_id

            if (record["txr"] != "") and (record["unique_drug_id"] != 0):
                if record["txr"] not in drug_data:
                    if record['brand_flag'] != GENERIC_FLAG or record["daw"] != 0:
                        record["daw"] = 1
                        drug_data[record["txr"]] = {1: {record["formatted_ndc"]: record}}
                        mapping_dict = add_to_request_mapping(data=record, data_dict=mapping_dict, daw=1)
                    else:
                        drug_data[record["txr"]] = {0: {record["formatted_ndc"]: record}}
                        mapping_dict = add_to_request_mapping(data=record, data_dict=mapping_dict, daw=0)
                else:
                    if record['brand_flag'] != GENERIC_FLAG or record["daw"] != 0:
                        record["daw"] = 1
                        if 1 in drug_data[record["txr"]]:
                            if record["formatted_ndc"] in drug_data[record["txr"]][1]:
                                drug_data[record["txr"]][1][record["formatted_ndc"]]["req_qty"] += record["req_qty"]
                            else:
                                drug_data[record["txr"]][1][record["formatted_ndc"]] = record
                                mapping_dict = add_to_request_mapping(data=record, data_dict=mapping_dict, daw=1)
                        else:
                            drug_data[record["txr"]][1] = {record["formatted_ndc"]: record}
                            mapping_dict = add_to_request_mapping(data=record, data_dict=mapping_dict, daw=1)
                    else:
                        if 0 in drug_data[record["txr"]]:
                            drug_data[record["txr"]][0][
                                list((drug_data[record["txr"]][0]).keys())[0]]["req_qty"] += record["req_qty"]

                            # updating the src_drug_uid list in mapping_dict by appending the unique_drug_id
                            ref_unique_drug_id: int = drug_data[
                                record["txr"]][0][list((drug_data[record["txr"]][0]).keys())[0]]["unique_drug_id"]
                            if 0 in mapping_dict and ref_unique_drug_id in mapping_dict[0]:
                                mapping_dict[0][ref_unique_drug_id]["src_drug_uid"].append(record["unique_drug_id"])
                            else:
                                mapping_dict = add_to_request_mapping(data=record, data_dict=mapping_dict, daw=0)
                        else:
                            drug_data[record["txr"]][0] = {record["formatted_ndc"]: record}
                            mapping_dict = add_to_request_mapping(data=record, data_dict=mapping_dict, daw=0)

            else:
                print("NDC unordered due to NULL TXR: " + record["ndc"])

        return drug_data, mapping_dict

    except APIFailureException as e:
        logger.error(e)
        raise e
    except TokenFetchException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def differentiate_by_drug_type(order_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]],
                               company_id: int) -> Dict[str, Dict[str, Dict[int, Dict[str, Dict[str, Any]]]]]:
    """
    Differentiates the order data by the drug type, i.e. whether canister drug or manual drug.
    """
    can_order_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = dict()
    man_order_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = dict()
    try:
        # get the TXRs and corresponding FNDCs having the canisters
        canister_txr_fndc = get_canister_data_by_txr(company_id=company_id, txr_list=list(order_data.keys()))

        for txr in order_data:
            # if canister exists for the given txr
            if txr in canister_txr_fndc:
                # for non-zero daw flag or non-generic drug, not considering the canister alternate
                if 1 in order_data[txr]:
                    for fndc in order_data[txr][1]:
                        # there exists a canister for the given fndc txr combination, hence canister drug
                        if fndc in canister_txr_fndc[txr]:
                            if txr in can_order_data:
                                if 1 in can_order_data[txr]:
                                    can_order_data[txr][1][fndc] = order_data[txr][1][fndc]
                                else:
                                    can_order_data[txr][1] = {fndc: order_data[txr][1][fndc]}
                            else:
                                can_order_data[txr] = {1: {fndc: order_data[txr][1][fndc]}}
                        # there exist no canister with the mentioned fndc and txr combination, so manual drug
                        else:
                            if txr in man_order_data:
                                if 1 in man_order_data[txr]:
                                    man_order_data[txr][1][fndc] = order_data[txr][1][fndc]
                                else:
                                    man_order_data[txr][1] = {fndc: order_data[txr][1][fndc]}
                            else:
                                man_order_data[txr] = {1: {fndc: order_data[txr][1][fndc]}}

                # for 0 daw flag alternate with same TXR considered and added to canister drug
                if 0 in order_data[txr]:
                    if txr in can_order_data:
                        can_order_data[txr][0] = order_data[txr][0]
                    else:
                        can_order_data[txr] = {0: order_data[txr][0]}
            # if canister doesn't exist for the given txr, add that txr to manual drug
            else:
                man_order_data[txr] = order_data[txr]

        return {"canister_order_drugs": can_order_data, "manual_order_drugs": man_order_data}

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def current_inventory_consideration(local_di: bool,
                                    company_id: int,
                                    robot_order_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = None,
                                    manual_order_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = None) -> \
                                    Tuple[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    This function considers the current inventory status before ordering.
    """
    default_order_dict = defaultdict(lambda: defaultdict(dict))
    cur_inventory_mapping_data: Dict[str, List[Dict[str, Any]]] = dict()
    inventory_data: Dict[str, Dict[str, Any]]
    inventory_priority: Dict[str, List[str]]
    order_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = dict()
    try:

        def default_to_regular(d):
            if isinstance(d, defaultdict):
                d = {k: default_to_regular(v) for k, v in d.items()}
            return d

        inventory_data, inventory_priority = get_current_inventory_data_by_txr(txr_list=list(order_data.keys()),
                                                                               local_di=local_di)

        # add the buffer qty to the canister drugs based on the drug_usage.
        if local_di:
            # get the company settings to get the add the buffer for the canister drugs
            company_setting: Dict[str, Any] = get_company_setting_by_company_id(company_id=company_id)
            usage_to_buffer: Dict[int, Decimal] = dict()
            for usage in USAGE_TO_BUFFER:
                usage_to_buffer[usage] = Decimal(company_setting.get(USAGE_TO_BUFFER[usage], 1))

            for txr in robot_order_data:
                for daw in robot_order_data[txr]:
                    for fndc in robot_order_data[txr][daw]:
                        robot_order_data[txr][daw][fndc]["req_qty"] = Decimal(round(robot_order_data[txr][daw][fndc]["req_qty"] *
                                                                              usage_to_buffer[robot_order_data[txr][daw][
                                                                                  fndc]["drug_usage"]]))
        # [x for x in robot_order_data.keys() if x in manual_order_data.keys()]
        for txr, daws in robot_order_data.items():
            for daw, fndc in daws.items():
                for f, r in fndc.items():
                    try:
                        qty = manual_order_data[txr][daw][f]["req_qty"]
                        pack_id = manual_order_data[txr][daw][f]["pack_id"]
                        del manual_order_data[txr][daw][f]
                    except KeyError:
                        default_order_dict[txr][daw][f] = robot_order_data[txr][daw][f]
                        continue
                    default_order_dict[txr][daw][f] = robot_order_data[txr][daw][f]
                    default_order_dict[txr][daw][f]["req_qty"] = default_order_dict[txr][daw][f].get("req_qty",
                                                                                                         0) + qty
                    default_order_dict[txr][daw][f]["pack_id"] = default_order_dict[txr][daw][f].get("pack_id",
                                                                                                    "") + "," + pack_id

        for txr, daws in manual_order_data.items():
            for daw, fndc in daws.items():
                for f, r in fndc.items():
                    default_order_dict[txr][daw][f] = manual_order_data[txr][daw][f]

        order_data = dict(default_to_regular(default_order_dict))

        for txr in order_data:
            if txr in inventory_data:
                # calculate the actual required quantity for the drugs with daw 1
                if 1 in order_data[txr]:
                    for order_fndc in order_data[txr][1]:
                        if order_fndc in inventory_data[txr]:
                            cur_order_qty: int = order_data[txr][1][order_fndc].get("order_qty", 0)
                            req_qty: int = math.ceil(
                                order_data[txr][1][order_fndc]["req_qty"]) if cur_order_qty == 0 else cur_order_qty
                            inventory_qty: int = math.floor(inventory_data[txr][order_fndc]["quantity"])
                            order_qty: int = inventory_qty - req_qty
                            if inventory_data[txr][order_fndc]["quantity"] > 0:
                                daw_fndc_txr: str = "1" + "##" + order_fndc + "##" + txr
                                reserve_dict: Dict[str, Any] = {
                                    "reserve_ndc": inventory_data[txr][order_fndc]["ndc"],
                                    "reserve_txr": txr,
                                    "reserve_qty": inventory_qty if order_qty < 0 else req_qty,
                                    "is_local": 1 if local_di else 0}
                                if daw_fndc_txr in cur_inventory_mapping_data:
                                    cur_inventory_mapping_data[daw_fndc_txr].append(reserve_dict)
                                else:
                                    cur_inventory_mapping_data[daw_fndc_txr] = [reserve_dict]

                            if order_qty < 0:
                                inventory_data[txr][order_fndc]["quantity"] = 0
                                order_data[txr][1][order_fndc]["order_qty"] = abs(order_qty)
                            else:
                                inventory_data[txr][order_fndc]["quantity"] = order_qty
                                order_data[txr][1][order_fndc]["order_qty"] = 0
                        else:
                            order_data[txr][1][order_fndc]["order_qty"] = math.ceil(
                                order_data[txr][1][order_fndc]["req_qty"])

                # calculate the actual required quantity for the drugs with daw 0
                if 0 in order_data[txr]:
                    for order_fndc in order_data[txr][0]:
                        for inventory_fndc in inventory_priority[txr]:
                            # preventing the on-hand branded drug to be reserved for the generic requirement
                            if inventory_data[txr][inventory_fndc]["brand_flag"] == GENERIC_FLAG or \
                                    order_fndc == inventory_fndc:
                                cur_order_qty: int = order_data[txr][0][order_fndc].get("order_qty", 0)
                                req_qty: int = math.ceil(
                                    order_data[txr][0][order_fndc]["req_qty"]) if cur_order_qty == 0 else cur_order_qty
                                inventory_qty: int = math.floor(inventory_data[txr][inventory_fndc]["quantity"])
                                order_qty: int = inventory_qty - req_qty
                                if inventory_data[txr][inventory_fndc]["quantity"] > 0:
                                    daw_fndc_txr: str = "0" + "##" + order_fndc + "##" + txr
                                    reserve_dict: Dict[str, Any] = {
                                        "reserve_ndc": inventory_data[txr][inventory_fndc]["ndc"],
                                        "reserve_txr": txr,
                                        "reserve_qty": inventory_qty if order_qty < 0 else req_qty,
                                        "is_local": 1 if local_di else 0}
                                    if daw_fndc_txr in cur_inventory_mapping_data:
                                        cur_inventory_mapping_data[daw_fndc_txr].append(reserve_dict)
                                    else:
                                        cur_inventory_mapping_data[daw_fndc_txr] = [reserve_dict]
                                if order_qty < 0:
                                    inventory_data[txr][inventory_fndc]["quantity"] = 0
                                    order_data[txr][0][order_fndc]["order_qty"] = abs(order_qty)
                                else:
                                    inventory_data[txr][inventory_fndc]["quantity"] = order_qty
                                    order_data[txr][0][order_fndc]["order_qty"] = 0
                                    break
                            else:
                                order_data[txr][0][order_fndc]["order_qty"] = math.ceil(order_data[txr][0]
                                                                                        [order_fndc]["req_qty"])
            # drugs with required txr not present in the inventory
            else:
                for daw in order_data[txr]:
                    for order_fndc in order_data[txr][daw]:
                        if "order_qty" in order_data[txr][daw][order_fndc]:
                            cur_order_qty: int = math.ceil(order_data[txr][daw][order_fndc]["order_qty"])
                        else:
                            cur_order_qty: int = math.ceil(order_data[txr][daw][order_fndc]["req_qty"])
                        order_data[txr][daw][order_fndc]["order_qty"] = cur_order_qty

        return order_data, cur_inventory_mapping_data

    except APIFailureException as e:
        logger.error("Error in current_inventory_consideration {}".format(e))
        raise e
    except TokenFetchException as e:
        logger.error("Error in current_inventory_consideration {}".format(e))
        raise e
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in current_inventory_consideration {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in current_inventory_consideration {}".format(e))
        raise e


@log_args_and_response
def prepare_order_data_and_place_order(unique_id: str, department: str, local_di: bool, company_id: int,
                                       robot_order_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = None,
                                       manual_order_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = None,
                                       user_id: Optional[int] = None,
                                       facility_dist_id: Optional[int] = None, add_to_pre_order: Optional[bool] = False,
                                       request_mapping: Optional[Dict[int, Dict[Any, Any]]] = None,
                                       batch_pack_data: Optional[List[Dict[str, Any]]] = None, bypassed: bool =None) -> \
        Tuple[bool, Dict[str, List[Dict[str, Any]]], bool]:
    """
    Based on the requirement data, prepared the data to order and place an order
    """
    batch_drugs: List[Dict[str, Any]] = list()
    drug_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]]
    inventory_mapping: Dict[str, List[Dict[str, Any]]]
    created_list: List[Dict[str, Any]]
    updated_list: List[Dict[str, Any]]
    deleted_list: List[Dict[str, Any]]
    drug_to_order: bool = False
    bypass: bool = False
    bypass_call = False
    if not add_to_pre_order:
        bypass_call = True
    try:
        logger.info("In prepare_order_data_and_place_order: robot_order_drugs: {}".format(robot_order_data))
        logger.info("In prepare_order_data_and_place_order: manual_order_drugs: {}".format(manual_order_data))

        drug_data, inventory_mapping = current_inventory_consideration(robot_order_data=robot_order_data,
                                                                       manual_order_data=manual_order_data,
                                                                       local_di=local_di,
                                                                       company_id=company_id)

        for txr in drug_data:
            for daw in drug_data[txr]:
                for fndc in drug_data[txr][daw]:
                    batch_drugs.append(drug_data[txr][daw][fndc])

        with db.transaction():
            # populating the BatchDrugData table and getting the lists of data for sending it to Inventory
            created_list, updated_list, deleted_list = get_lists_of_ordering_data(batch_drugs=batch_drugs,
                                                                                  facility_dist_id=facility_dist_id,
                                                                                  department=department,
                                                                                  unique_id=unique_id, user_id=user_id,
                                                                                  add_to_pre_order=add_to_pre_order)

            if len(created_list) > 0 or len(updated_list) > 0 or len(deleted_list) > 0:
                if len(created_list) > 0 or len(updated_list) > 0:
                    drug_to_order = True

                # post the data of the required drug quantity to the drug inventory
                if bypassed:
                    inventory_response = []
                else:
                    inventory_response: List[Dict[str, Any]] = post_drug_data_to_inventory(created_list=created_list,
                                                                                       updated_list=updated_list,
                                                                                       deleted_list=deleted_list, bypass_call=bypass_call)
                if inventory_response:
                    if add_to_pre_order:
                        update_adhoc_drug_request_by_inventory_response(response_list=inventory_response,
                                                                        unique_id=unique_id)
                    else:
                        update_batch_drug_data_by_inventory_response(facility_dist_id=facility_dist_id, user_id=user_id,
                                                                     response_list=inventory_response,
                                                                     department=department)
                elif bypass_call:
                    # When dosepack is unable to connect to EPBM server, we insert dummmy data with refrence to past orderinh

                    bypass = True
                    logger.info("In prepare_order_data_and_place_order : Bypassing Order. ")
                    if len(created_list) > 0:
                        created_list.extend(updated_list)
                    status = update_alternate_drug_based_on_past_ordering(created_list, facility_dist_id, user_id, company_id)
            else:
                logger.info("There are no drugs to be ordered.")
                bypass = True if bypassed else False

            # Based on the current inventory data, populates CurrentInventoryMapping to keep a track of
            # which inventory available ndc is considered for the required ndc and the daw flag.
            if not add_to_pre_order and not bypass:
                if inventory_mapping:

                    populate_current_inventory_mapping(facility_dist_id=facility_dist_id, department=department,
                                                       inventory_mapping=inventory_mapping, local_di=local_di)

                # populate the BatchDrugRequestMapping
                if request_mapping:
                    populate_batch_drug_request_mapping(facility_dist_id=facility_dist_id, mapping_dict=request_mapping,
                                                        user_id=user_id)
                # populate BatchPackData table
                if batch_pack_data:

                    populate_batch_pack_data(batch_pack_data_list=batch_pack_data)

        return drug_to_order, inventory_mapping, bypass
    except APIFailureException as e:
        logger.error("Error in prepare_order_data_and_place_order {}".format(e))
        raise e
    except TokenFetchException as e:
        logger.error("Error in prepare_order_data_and_place_order {}".format(e))
        raise e
    except DrugInventoryInternalException as e:
        logger.error("Error in prepare_order_data_and_place_order {}".format(e))
        raise e
    except DrugInventoryValidationException as e:
        logger.error("Error in prepare_order_data_and_place_order {}".format(e))
        raise e
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in prepare_order_data_and_place_order {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in prepare_order_data_and_place_order {}".format(e))
        raise e


@log_args_and_response
def get_non_robot_inventory(local_inventory: List[Any], txr_list: List[str]) -> List[Dict[str, Any]]:
    """
    Gets the inventory data after considering(subtracting) the local inventory as well for the manual drug availability.
    """
    # non_robot_inventory: Dict[str, Dict[str, Any]] = dict()

    try:
        # get ndc wise dict from local_inventory which is from table localdidata
        local_inventory_by_ndc: Dict[str, Dict[str, Any]] = {data["ndc"]: data for data in local_inventory}

        txr_list: List[int] = [int(txr) for txr in txr_list]

        # get on hand inventory data from elite and create dict having key value a pair of ndc and inventory data
        total_inventory_by_ndc: Dict[str, Dict[str, Any]] = {data["ndc"]: data for data in get_current_inventory_data(
            txr_list=txr_list, qty_greater_than_zero=False)}

        for ndc in local_inventory_by_ndc:
            # considering only the +ve qty as they are actual reserved for robot.
            loc_qty: int = int(local_inventory_by_ndc[ndc]["quantity"]) if local_inventory_by_ndc[
                                                                               ndc]["quantity"] > 0 else 0
            if ndc in total_inventory_by_ndc:
                total_inventory_by_ndc[ndc]["quantity"] -= loc_qty
            else:
                total_inventory_by_ndc[ndc] = {"ndc": ndc,
                                               "quantity": -loc_qty,
                                               "cfi": local_inventory_by_ndc[ndc]["txr"],
                                               "brand": local_inventory_by_ndc[ndc]["brand_flag"]}

        return list(total_inventory_by_ndc.values())

    except APIFailureException as e:
        logger.error(e)
        raise e
    except TokenFetchException as e:
        logger.error(e)
        raise e
    except DrugInventoryInternalException as e:
        logger.error(e)
        raise e
    except DrugInventoryValidationException as e:
        logger.error(e)
        raise e
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_current_inventory_data_by_txr(txr_list: List[str],
                                      local_di: bool) -> Tuple[Dict[str, Dict[str, Dict[str, Any]]],
                                                               Dict[str, List[str]]]:
    """
    This functions fetches the inventory data and prepares the data by txr and fndc
    """
    cur_inventory_by_txr: Dict[str, Dict[str, Dict[str, Any]]] = dict()
    fndc_txr_set: Set[str] = set()
    cur_inventory_data = []
    try:
        # cur_inventory_data = local_di_get_inventory_data(txr_list=txr_list)
        # if not local_di:
        #     logger.info("calculate for non robot inventory {}".format(local_di))
        #     cur_inventory_data = get_non_robot_inventory(local_inventory=cur_inventory_data, txr_list=txr_list)

        if cur_inventory_data:
            for data in cur_inventory_data:
                txr: str = str(data["txr"]) if local_di else str(data["cfi"])
                formatted_ndc: str = str(data["formatted_ndc"]) if local_di else str(data["ndc"][:-2])
                fndc_txr_set.add(formatted_ndc + "##" + txr)

                # add the brand flag to avoid branded on-hand being reserved for generic
                brand_flag: Optional[str] = str(data["brand_flag"]) if local_di else None
                if not local_di and "brand" in data:
                    if data["brand"] == "G":
                        brand_flag = GENERIC_FLAG
                    elif data["brand"] == "B":
                        brand_flag = BRAND_FLAG
                    elif data["brand"] == "N":
                        brand_flag = NON_DRUG_FLAG

                if txr in cur_inventory_by_txr:
                    if formatted_ndc in cur_inventory_by_txr[txr]:
                        cur_inventory_by_txr[txr][formatted_ndc]["quantity"] += data["quantity"]
                        if cur_inventory_by_txr[txr][formatted_ndc]["quantity"] > 0 and data["quantity"] > 0:
                            cur_inventory_by_txr[txr][formatted_ndc]["ndc"] = str(data["ndc"])
                    else:
                        cur_inventory_by_txr[txr][formatted_ndc] = {"ndc": str(data["ndc"]), "brand_flag": brand_flag,
                                                                    "quantity": data["quantity"]}
                else:
                    cur_inventory_by_txr[txr] = {formatted_ndc: {"ndc": str(data["ndc"]), "brand_flag": brand_flag,
                                                                 "quantity": data["quantity"]}}

        return prioritize_inventory_drugs(cur_inventory_by_txr=cur_inventory_by_txr, fndc_txr_set=fndc_txr_set)

    except APIFailureException as e:
        logger.error("Error in get_current_inventory_data_by_txr {}".format(e))
        raise e
    except TokenFetchException as e:
        logger.error("Error in get_current_inventory_data_by_txr {}".format(e))
        raise e
    except DrugInventoryInternalException as e:
        logger.error("Error in get_current_inventory_data_by_txr {}".format(e))
        raise e
    except DrugInventoryValidationException as e:
        logger.error("Error in get_current_inventory_data_by_txr {}".format(e))
        raise e
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_current_inventory_data_by_txr {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in get_current_inventory_data_by_txr {}".format(e))
        raise e


@log_args_and_response
def prioritize_inventory_drugs(cur_inventory_by_txr: Dict[str, Dict[str, Dict[str, Any]]],
                               fndc_txr_set: Set[str]) -> Tuple[Dict[str, Dict[str, Dict[str, Any]]],
                                                                Dict[str, List[str]]]:
    """
    Prioritize the drug with canister and having the positive qty from the on-hand drugs.
    """
    cur_inventory_by_txr_positive: Dict[str, Dict[str, Dict[str, Any]]] = dict()
    fndc_txr_priority: Dict[str, List[str]] = dict()
    try:
        if cur_inventory_by_txr and fndc_txr_set:
            fndc_txr_with_canister: List[str] = get_fndc_txr_with_canister(fndc_txr_list=list(fndc_txr_set))
            # considering the availability of the drugs having quantity > 0
            for txr in cur_inventory_by_txr:
                for fndc in cur_inventory_by_txr[txr]:
                    if cur_inventory_by_txr[txr][fndc]["quantity"] > 0:
                        if txr in cur_inventory_by_txr_positive:
                            cur_inventory_by_txr_positive[txr][fndc] = cur_inventory_by_txr[txr][fndc]
                        else:
                            cur_inventory_by_txr_positive[txr] = {fndc: cur_inventory_by_txr[txr][fndc]}

                        # prioritize the drug with canister
                        if txr in fndc_txr_priority:
                            if (fndc + "##" + txr) in fndc_txr_with_canister:
                                fndc_txr_priority[txr].insert(0, fndc)
                            else:
                                fndc_txr_priority[txr].append(fndc)
                        else:
                            fndc_txr_priority[txr] = [fndc]
            # prioritize the drug with higher qty among the canister availability
            for txr_prior in fndc_txr_priority:
                if len(fndc_txr_priority[txr_prior]) > 1:
                    temp_dict: Dict[int, Dict[int, str]] = dict()
                    temp_list: List[str] = list()
                    for fndc_prior in fndc_txr_priority[txr_prior]:
                        if (fndc_prior + "##" + txr_prior) in fndc_txr_with_canister:
                            if 1 in temp_dict:
                                temp_dict[1].update(
                                    {cur_inventory_by_txr_positive[txr_prior][fndc_prior]["quantity"]: fndc_prior})
                            else:
                                temp_dict[1] = {
                                    cur_inventory_by_txr_positive[txr_prior][fndc_prior]["quantity"]: fndc_prior}
                        else:
                            if 0 in temp_dict:
                                temp_dict[0].update(
                                    {cur_inventory_by_txr_positive[txr_prior][fndc_prior]["quantity"]: fndc_prior})
                            else:
                                temp_dict[0] = {
                                    cur_inventory_by_txr_positive[txr_prior][fndc_prior]["quantity"]: fndc_prior}
                    if 1 in temp_dict:
                        for i in reversed(sorted(temp_dict[1].keys())):
                            temp_list.append(temp_dict[1][i])
                    if 0 in temp_dict:
                        for j in reversed(sorted(temp_dict[0].keys())):
                            temp_list.append(temp_dict[0][j])

                    fndc_txr_priority[txr_prior] = temp_list

        return cur_inventory_by_txr_positive, fndc_txr_priority

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_and_update_txr_for_ndc(record: Dict[str, Any]) -> Tuple[str, int]:
    """
    This function fetches the txr for the given NDC and updates the DrugMaster and UniqueDrug tables.
    """
    logger.debug("Inside get_and_update_txr_for_ndc.")
    try:
        inventory_resp = get_data_by_ndc_from_drug_inventory(ndc_list=[record["ndc"]])
        if inventory_resp:
            txr = str(inventory_resp[record["ndc"]]["cfi"])
            update_status = update_txr_in_drug_master_and_unique_drug(txr=str(txr),
                                                                       ndc=str(record["ndc"]))
            logger.info("In get_and_update_txr_for_ndc: txr is updated for ndc: {}".format(update_status))
            unique_drug_id = get_or_create_unique_drug(formatted_ndc=str(record["formatted_ndc"]), txr=txr).id
            return txr, unique_drug_id
        else:
            return "", 0

    except APIFailureException as e:
        logger.error(e)
        raise e
    except TokenFetchException as e:
        logger.error(e)
        raise e
    except DrugInventoryInternalException as e:
        logger.error(e)
        raise e
    except DrugInventoryValidationException as e:
        logger.error(e)
        raise e
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def add_to_request_mapping(data: Dict[str, Any], data_dict: Dict[int, Any], daw: int) -> Dict[int, Any]:
    """
    Function to prepare the data for BatchDrugRequestMapping
    """
    try:
        if daw == 0:
            if len(data_dict) == 0:
                data_dict = {0: {data["unique_drug_id"]: {"txr": data["txr"],
                                                          "src_drug_uid": [data["unique_drug_id"]]}}}
            elif 0 not in data_dict:
                data_dict[0] = {data["unique_drug_id"]: {"txr": data["txr"],
                                                         "src_drug_uid": [data["unique_drug_id"]]}}
            else:
                data_dict[0][data["unique_drug_id"]] = {"txr": data["txr"],
                                                        "src_drug_uid": [data["unique_drug_id"]]}
        else:
            if len(data_dict) == 0:
                data_dict = {1: {data["unique_drug_id"]: {"txr": data["txr"],
                                                          "src_drug_uid": [data["unique_drug_id"]]}}}
            elif 1 not in data_dict:
                data_dict[1] = {data["unique_drug_id"]: {"txr": data["txr"],
                                                         "src_drug_uid": [data["unique_drug_id"]]}}
            else:
                data_dict[1][data["unique_drug_id"]] = {"txr": data["txr"],
                                                        "src_drug_uid": [data["unique_drug_id"]]}
        return data_dict

    except Exception as e:
        logger.error(e)
        raise e


@log_args_and_response
def populate_batch_drug_request_mapping(facility_dist_id: int, mapping_dict: Dict[int, Dict[Any, Any]], user_id: int):
    """
    THis inserts data in the BatchDrugRequestMapping.
    """
    logger.debug("Inside populate_batch_drug_request_mapping")
    batch_drug_request_mapping_data_list: List[Dict[str, Any]] = list()
    try:
        for daw in mapping_dict:
            for req_id in mapping_dict[daw]:
                for uid in mapping_dict[daw][req_id]["src_drug_uid"]:
                    batch_drug_request_mapping_data_list.append({"facility_dist_id": facility_dist_id,
                                                                 "txr": mapping_dict[daw][req_id]["txr"],
                                                                 "daw": daw,
                                                                 "source_unique_drug_id": uid,
                                                                 "requested_unique_drug_id": req_id,
                                                                 "created_by": user_id})
        populate_batch_drug_request_mapping_data(batch_drug_req_map_data_list=batch_drug_request_mapping_data_list)

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        raise e

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_lists_of_ordering_data(batch_drugs: List[dict], unique_id: str, department: str, add_to_pre_order: bool,
                               facility_dist_id: Optional[int] = None, user_id: Optional[int] = None) -> \
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Populates and/or updates BatchDrugData & CurrentInventoryMapping table and gets the lists of ordering data.
    """
    logger.debug("Inside get_lists_of_ordering_data")
    insert_data_list: List[Dict[str, Any]] = list()
    update_data_dict: Dict[str, Any]
    delete_data_list: List[str] = list()
    created_list: List[Dict[str, Any]] = list()
    updated_list: List[Dict[str, Any]] = list()
    deleted_list: List[Dict[str, Any]] = list()
    src_drug_data_dict: Dict[str, Any] = dict()
    tgt_drug_data_dict: Dict[str, Any] = dict()
    try:
        # check if there is any record with the given facility_dist_id in the BatchDrugData table.
        if facility_dist_id:
            drug_data_records: List[Any] = get_records_by_facility_dist_id_and_dept(facility_dist_id=facility_dist_id,
                                                                                    department=department)
        else:
            drug_data_records: List[Any] = get_records_by_unique_id_and_dept(unique_id=unique_id, department=department)

        if len(drug_data_records) <= 0:
            # create dictionary for populating BatchDrugData or AdhocDrugRequest table.
            for batch_drug in batch_drugs:
                if batch_drug["order_qty"] > 0:
                    created_list.append({"uniqueId": unique_id,
                                         "ndc": int(batch_drug["ndc"]),
                                         "daw": True if (batch_drug["daw"] == 1) else False,
                                         "quantity": batch_drug["order_qty"],
                                         "department": department,
                                         "addToPreOrderList": add_to_pre_order})
                if facility_dist_id:
                    insert_data_list.append({"facility_dist_id": batch_drug["facility_dist_id"],
                                             "formatted_ndc": batch_drug["formatted_ndc"],
                                             "txr": batch_drug["txr"],
                                             "daw": batch_drug["daw"],
                                             "ndc": batch_drug["ndc"],
                                             "req_qty": math.ceil(batch_drug["req_qty"]),
                                             "order_qty": batch_drug["order_qty"],
                                             "status_id": DRUG_INVENTORY_MANAGEMENT_ADDED_ID,
                                             "created_by": user_id,
                                             "modified_by": user_id,
                                             "department": department})
                else:
                    insert_data_list.append({"unique_id": unique_id,
                                             "formatted_ndc": batch_drug["formatted_ndc"],
                                             "txr": batch_drug["txr"],
                                             "daw": batch_drug["daw"],
                                             "ndc": batch_drug["ndc"],
                                             "req_qty": math.ceil(batch_drug["req_qty"]),
                                             "order_qty": batch_drug["order_qty"],
                                             "status_id": DRUG_INVENTORY_MANAGEMENT_ADDED_ID,
                                             "department": department})
            if len(insert_data_list) > 0:
                if facility_dist_id:
                    # Inserting data in the BatchDrugData table
                    populate_batch_drug_data(batch_drug_data_list=insert_data_list)
                else:
                    # Inserting data in the AdhocDrugRequest table
                    populate_adhoc_drug_request(adhoc_drug_request_data_list=insert_data_list)
        else:
            # if the drug data already exists in the BatchDrugData or AdhocDrugRequest table
            for rec in drug_data_records:
                if rec["daw"] == 1:
                    identifier: str = str(rec["formatted_ndc"]) + "##" + str(rec["txr"]) + "##" + str(rec["daw"])
                else:
                    identifier: str = str(rec["txr"]) + "##" + str(rec["daw"])
                src_drug_data_dict[identifier] = rec

            # the drug data for the current updated pack list in the given facility distribution id
            for drug in batch_drugs:
                if drug["daw"] == 1:
                    identifier: str = str(drug["formatted_ndc"]) + "##" + str(drug["txr"]) + "##" + str(drug["daw"])
                else:
                    identifier = str(drug["txr"]) + "##" + str(drug["daw"])
                tgt_drug_data_dict[identifier] = drug

            # get the list of drugs that are now deleted
            for src_data in src_drug_data_dict:
                if src_data not in tgt_drug_data_dict:
                    if src_drug_data_dict[src_data]["status_id"] != DRUG_INVENTORY_MANAGEMENT_DELETED_ID:
                        if src_drug_data_dict[src_data]["order_qty"] > 0:
                            deleted_list.append({"uniqueId": unique_id,
                                                 "ndc": int(src_drug_data_dict[src_data]["ndc"]),
                                                 "daw": True if (src_drug_data_dict[src_data]["daw"] == 1) else False,
                                                 "quantity": src_drug_data_dict[src_data]["order_qty"],
                                                 "department": department,
                                                 "addToPreOrderList": add_to_pre_order})
                        delete_data_list.append(src_data)

            for tgt_data in tgt_drug_data_dict:
                # get the list of drugs that are now added
                if tgt_data not in src_drug_data_dict:
                    if tgt_drug_data_dict[tgt_data]["order_qty"] > 0:
                        created_list.append({"uniqueId": unique_id,
                                             "ndc": int(tgt_drug_data_dict[tgt_data]["ndc"]),
                                             "daw": True if (tgt_drug_data_dict[tgt_data]["daw"] == 1) else False,
                                             "quantity": tgt_drug_data_dict[tgt_data]["order_qty"],
                                             "department": department,
                                             "addToPreOrderList": add_to_pre_order})
                    if facility_dist_id:
                        insert_data_list.append({"facility_dist_id": tgt_drug_data_dict[tgt_data]["facility_dist_id"],
                                                 "formatted_ndc": tgt_drug_data_dict[tgt_data]["formatted_ndc"],
                                                 "txr": tgt_drug_data_dict[tgt_data]["txr"],
                                                 "daw": tgt_drug_data_dict[tgt_data]["daw"],
                                                 "ndc": tgt_drug_data_dict[tgt_data]["ndc"],
                                                 "req_qty": math.ceil(tgt_drug_data_dict[tgt_data]["req_qty"]),
                                                 "order_qty": tgt_drug_data_dict[tgt_data]["order_qty"],
                                                 "status_id": DRUG_INVENTORY_MANAGEMENT_ADDED_ID,
                                                 "created_by": user_id,
                                                 "modified_by": user_id,
                                                 "department": department})
                    else:
                        insert_data_list.append({"unique_id": unique_id,
                                                 "formatted_ndc": tgt_drug_data_dict[tgt_data]["formatted_ndc"],
                                                 "txr": tgt_drug_data_dict[tgt_data]["txr"],
                                                 "daw": tgt_drug_data_dict[tgt_data]["daw"],
                                                 "ndc": tgt_drug_data_dict[tgt_data]["ndc"],
                                                 "req_qty": math.ceil(tgt_drug_data_dict[tgt_data]["req_qty"]),
                                                 "order_qty": tgt_drug_data_dict[tgt_data]["order_qty"],
                                                 "status_id": DRUG_INVENTORY_MANAGEMENT_ADDED_ID,
                                                 "department": department})

                # considering the drugs that are now added but were previously in deleted state
                elif src_drug_data_dict[tgt_data]["status_id"] == DRUG_INVENTORY_MANAGEMENT_DELETED_ID:
                    if tgt_drug_data_dict[tgt_data]["order_qty"] > 0:
                        created_list.append({"uniqueId": unique_id,
                                             "ndc": int(tgt_drug_data_dict[tgt_data]["ndc"]),
                                             "daw": True if (tgt_drug_data_dict[tgt_data]["daw"] == 1) else False,
                                             "quantity": tgt_drug_data_dict[tgt_data]["order_qty"],
                                             "department": department,
                                             "addToPreOrderList": add_to_pre_order})
                    if facility_dist_id:
                        update_data_dict = {"req_qty": math.ceil(tgt_drug_data_dict[tgt_data]["req_qty"]),
                                            "order_qty": tgt_drug_data_dict[tgt_data]["order_qty"],
                                            "status_id": DRUG_INVENTORY_MANAGEMENT_ADDED_ID,
                                            "ext_is_success": None,
                                            "ext_note": None,
                                            "modified_by": user_id,
                                            "modified_date": get_current_date_time()}
                        update_batch_drug_data_by_fndc_txr_daw_and_dept(data=update_data_dict, fndc_txr_daw=tgt_data,
                                                                        facility_dist_id=facility_dist_id,
                                                                        department=department)
                    else:
                        update_data_dict = {"req_qty": math.ceil(tgt_drug_data_dict[tgt_data]["req_qty"]),
                                            "order_qty": tgt_drug_data_dict[tgt_data]["order_qty"],
                                            "status_id": DRUG_INVENTORY_MANAGEMENT_ADDED_ID,
                                            "ext_is_success": None,
                                            "ext_note": None,
                                            "modified_date": get_current_date_time()}
                        update_adhoc_drug_request_by_fndc_txr_daw(data=update_data_dict, unique_id=unique_id,
                                                                  fndc_txr_daw=tgt_data)

                # getting the list of the updated drug
                else:
                    if (tgt_drug_data_dict[tgt_data]["order_qty"] != src_drug_data_dict[tgt_data]["order_qty"]) or (
                            tgt_drug_data_dict[tgt_data]["req_qty"] != src_drug_data_dict[tgt_data]["req_qty"]):
                        if tgt_drug_data_dict[tgt_data]["order_qty"] > 0:
                            updated_list.append({"uniqueId": unique_id,
                                                 "ndc": int(src_drug_data_dict[tgt_data]["ndc"]),
                                                 "daw": True if (tgt_drug_data_dict[tgt_data]["daw"] == 1) else False,
                                                 "quantity": tgt_drug_data_dict[tgt_data]["order_qty"],
                                                 "department": department,
                                                 "addToPreOrderList": add_to_pre_order})
                        if facility_dist_id:
                            update_data_dict = {"req_qty": math.ceil(tgt_drug_data_dict[tgt_data]["req_qty"]),
                                                "order_qty": tgt_drug_data_dict[tgt_data]["order_qty"],
                                                "status_id": DRUG_INVENTORY_MANAGEMENT_UPDATED_ID,
                                                "ext_is_success": None,
                                                "ext_note": None,
                                                "modified_by": user_id,
                                                "modified_date": get_current_date_time()}
                            update_batch_drug_data_by_fndc_txr_daw_and_dept(data=update_data_dict,
                                                                            facility_dist_id=facility_dist_id,
                                                                            fndc_txr_daw=tgt_data,
                                                                            department=department)
                        else:
                            update_data_dict = {"req_qty": math.ceil(tgt_drug_data_dict[tgt_data]["req_qty"]),
                                                "order_qty": tgt_drug_data_dict[tgt_data]["order_qty"],
                                                "status_id": DRUG_INVENTORY_MANAGEMENT_UPDATED_ID,
                                                "ext_is_success": None,
                                                "ext_note": None,
                                                "modified_date": get_current_date_time()}
                            update_adhoc_drug_request_by_fndc_txr_daw(data=update_data_dict, unique_id=unique_id,
                                                                      fndc_txr_daw=tgt_data)
            if len(insert_data_list) > 0:
                if facility_dist_id:
                    populate_batch_drug_data(batch_drug_data_list=insert_data_list)
                else:
                    populate_adhoc_drug_request(adhoc_drug_request_data_list=insert_data_list)
            if len(delete_data_list) > 0:
                if facility_dist_id:
                    delete_batch_drug_data(delete_list=delete_data_list, facility_dist_id=facility_dist_id,
                                           user_id=user_id)
                else:
                    delete_adhoc_drug_request_data(delete_list=delete_data_list, unique_id=unique_id)

        return created_list, updated_list, deleted_list
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        raise e

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def populate_current_inventory_mapping(inventory_mapping: Dict[str, List[Dict[str, Any]]], department: str,
                                       facility_dist_id: int, local_di: bool) -> bool:
    """
    Populates the CurrentInventoryMapping table.
    """
    inventory_mapping_data: List[Dict[str, Any]] = list()
    inventory_mapping_insert_data: List[Dict[str, Any]] = list()
    cur_mapping_data: Dict[str, Any] = dict()
    try:
        # get the batch_drug_id for the CurrentInventoryMapping
        for record in get_batch_drug_data_by_facility_dist_id_and_dept(facility_dist_id=facility_dist_id,
                                                                       department=department):
            daw_fndc_txr: str = str(record["daw"]) + "##" + record["formatted_ndc"] + "##" + record["txr"]
            if daw_fndc_txr in inventory_mapping:
                for reserve_dict in inventory_mapping[daw_fndc_txr]:
                    inventory_mapping_data.append({"facility_dist_id": facility_dist_id,
                                                   "batch_drug_id": record["id"],
                                                   "reserve_ndc": reserve_dict["reserve_ndc"],
                                                   "reserve_txr": reserve_dict["reserve_txr"],
                                                   "reserve_qty": reserve_dict["reserve_qty"],
                                                   "is_local": reserve_dict["is_local"]})
        # populate/update the CurrentInventoryMapping table
        existing_data: List[Any] = get_cur_inventory_mapping_data(facility_dist_id=facility_dist_id, only_active=False,
                                                                  local_di=local_di)

        if len(existing_data) > 0:
            cur_mapping_data = {
                (str(data["batch_drug_id"]) + "##" + data["reserve_ndc"] + "##" + data["reserve_txr"]): data for data in
                existing_data}

        if cur_mapping_data:
            # mark all records inactive for the given facility_dist_id
            delete_current_inventory_mapping(facility_dist_id=facility_dist_id)
            for data in inventory_mapping_data:
                batch_drug_id_ndc_txr: str = str(data["batch_drug_id"]) + "##" + data["reserve_ndc"] + "##" + data[
                    "reserve_txr"]
                if batch_drug_id_ndc_txr in cur_mapping_data:
                    update_dict = {"reserve_qty": data["reserve_qty"],
                                   "is_active": True}
                    update_current_inventory_mapping_by_id(update_dict=update_dict,
                                                           update_id=cur_mapping_data[batch_drug_id_ndc_txr]["id"])
                else:
                    inventory_mapping_insert_data.append(data)

            if len(inventory_mapping_insert_data) > 0:
                insert_current_inventory_mapping_data(data_list=inventory_mapping_insert_data)
        else:
            insert_current_inventory_mapping_data(data_list=inventory_mapping_data)
        return True
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e)
        raise e


@log_args_and_response
def post_drug_data_to_inventory(created_list: List[Dict[str, Any]], updated_list: List[Dict[str, Any]],
                                deleted_list: List[Dict[str, Any]], bypass_call: bool) -> List[Dict[str, Any]]:
    """
    This function updates the inventory with the drug data for the upcoming set of packs.
    """
    logger.debug("Inside post_drug_data_to_inventory")
    status: bool
    inventory_resp: Dict[str, Any]
    response_list: List[Dict[str, Any]] = list()
    try:
        inventory_resp = post_request_data_to_drug_inventory(created_list=created_list,
                                                             deleted_list=deleted_list,
                                                             updated_list=updated_list, bypass_call=bypass_call)

        if inventory_resp:
            # create list of ndc from response of webservice
            if inventory_resp.get("created", None):
                response_list.extend(inventory_resp["created"])
            if inventory_resp.get("updated", None):
                response_list.extend(inventory_resp["updated"])
            if inventory_resp.get("deleted", None):
                response_list.extend(inventory_resp["deleted"])

        if not inventory_resp and bypass_call:
            return []

        return response_list

    except APIFailureException as e:
        logger.error(e)
        raise e
    except TokenFetchException as e:
        logger.error(e)
        raise e
    except DrugInventoryInternalException as e:
        logger.error(e)
        raise e
    except DrugInventoryValidationException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise DrugInventoryInternalException(e)


@log_args_and_response
def update_batch_drug_data_by_inventory_response(facility_dist_id: int, response_list: List[Dict[str, Any]],
                                                 user_id: int, department: str) -> bool:
    """
    Update the  BatchDrugData table based on the response from the inventory.
    """
    logger.debug("Inside update_batch_drug_data_by_inventory_response")
    pre_ordered_data_dict: Dict[str, Any] = dict()
    try:
        for key in response_list:
            if key.get("daw", None) is None:
                update_batch_drug_data_dict = {"ext_is_success": key["isSuccess"],
                                               "ext_note": key["note"],
                                               "modified_by": user_id,
                                               "modified_date": get_current_date_time()}
                update_batch_drug_data_by_ndc(data=update_batch_drug_data_dict, facility_dist_id=facility_dist_id,
                                              ndc=key["ndc"])
            else:
                if key["daw"]:
                    identifier: str = str(key["ndc"])[0:9] + "##" + str(key["cfi"]) + "##" + str(1 if key["daw"] else 0)
                else:
                    identifier: str = str(key["cfi"]) + "##" + str(1 if key["daw"] else 0)
                pre_ordered_data_dict[identifier] = key

        for fndc_txr_daw in pre_ordered_data_dict:
            update_batch_drug_data_dict = {"ext_is_success": pre_ordered_data_dict[fndc_txr_daw]["isSuccess"],
                                           "ext_note": pre_ordered_data_dict[fndc_txr_daw]["note"],
                                           "modified_by": user_id,
                                           "modified_date": get_current_date_time()}

            # update the BatchDrugData table based on response from webservice
            update_batch_drug_data_by_fndc_txr_daw_and_dept(data=update_batch_drug_data_dict, fndc_txr_daw=fndc_txr_daw,
                                                            facility_dist_id=facility_dist_id, department=department)
        return True
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_drug_inventory_couch_db_status(company_id: int, facility_dist_id: int, trigger_call: Optional[bool] = False,
                                          status: Optional[int] = None):
    """
    This function updates the couchDB with the order status.
    """
    database_name: str
    cdb: Database
    doc_id: str = EPBM_INVENTORY_COUCH_DB
    table: Dict[str, Any]
    try:
        # update the couchDB doc if the facility_dist_id is in pending state.
        facility_dist_id_status: int = get_facility_dist_id_status(company_id=company_id,
                                                                   facility_dist_id=facility_dist_id)
        if facility_dist_id_status == FACILITY_DISTRIBUTION_PENDING_STATUS:
            database_name = get_couch_db_database_name(company_id=company_id)
            cdb = Database(CONST_COUCHDB_SERVER_URL, database_name)
            cdb.connect()
            table = cdb.get(_id=doc_id)

            if table is None:
                table = {"_id": doc_id, "type": str(doc_id), "data": {
                             "facility_dist_id": None, "inventory_status": None, "trigger_call": None, "uuid": None
                         }}

            if table["data"]["facility_dist_id"] and table["data"]["facility_dist_id"] == facility_dist_id:
                if status:
                    table["data"]["inventory_status"] = status
                    table["data"]["trigger_call"] = trigger_call
                    table["data"]["uuid"] = uuid4().hex
                else:
                    table["data"]["trigger_call"] = trigger_call
                    table["data"]["uuid"] = uuid4().hex
            else:
                if status and status in  [DRUG_INVENTORY_MANAGEMENT_ORDER_PENDING_ID, DRUG_INVENTORY_MANAGEMENT_BYPASSED]:
                    table["data"]["facility_dist_id"] = facility_dist_id
                    table["data"]["inventory_status"] = status
                    table["data"]["trigger_call"] = trigger_call
                    table["data"]["uuid"] = uuid4().hex

            logger.info("updated table in couch db doc {} - {}".format(doc_id, table))
            cdb.save(table)

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        raise RealTimeDBException("Couch db Document update conflict.")

    except Exception as e:
        logger.error(e)
        raise RealTimeDBException('Couch db update failed')


@log_args_and_response
def update_ordered_drug_data(company_id: int, facility_dist_id: int, user_id: int,
                             pre_ordered_data: Optional[List[Dict[str, Any]]] = None) -> bool:
    """
    Updates the data of the ordered drug from the drug inventory.
    """

    pre_ordered_ndc_dict: Dict[str, Any]
    pre_ordered_ndc_list: List[str]
    unique_drug_id_list: List[int] = list()
    alt_drug_option_insert_data: List[Dict[str, Any]] = list()
    alt_drug_option_update_list: List[str] = list()
    missing_ndc_list: List[str] = list()
    error_in_pre_order_data: bool
    try:
        # Populates the BatchOrderDrugData table and gets the list of pre-ordered NDCs
        pre_ordered_ndc_dict, pre_ordered_ndc_list, error_in_pre_order_data = populate_order_data(
            facility_dist_id=facility_dist_id, order_data=pre_ordered_data, user_id=user_id)

        # get the drug info by ndc
        if pre_ordered_ndc_dict and pre_ordered_ndc_list:
            drug_data: Dict[str, Any] = get_drug_data_from_ndc_list(ndc_list=pre_ordered_ndc_list)

            # get the mapping data of requested unique_drug_id for the required unique_drug_ids
            mapping_data = get_mapping_data_by_facility_dist_id(facility_dist_id=facility_dist_id)

            # get the data from AlternateDrugOption table for the given facility_dist_id
            alternate_data = get_alternate_drug_dao(facility_distribution_id=facility_dist_id)
            curr_alternate_drug_option_data = [("{}##{}".format(record["unique_drug_id"], record["alternate_unique_drug_id"])) for record in alternate_data]

            # get the list of the unique_drug_ids that are ordered and the ones for which they are ordered
            for daw_req_ndc in pre_ordered_ndc_dict:
                daw = int(daw_req_ndc.strip().split("##")[0])
                req_ndc = str(daw_req_ndc.strip().split("##")[1])

                identifier = str(daw) + "##" + str(drug_data[req_ndc]["unique_drug_id"])

                # prepare data to update/insert in AlternateDrugOption table.
                for pre_ordered_ndc in pre_ordered_ndc_dict[daw_req_ndc]:
                    if pre_ordered_ndc in drug_data:
                        pre_ordered_unique_drug_id = drug_data[pre_ordered_ndc]["unique_drug_id"]
                        for unique_drug_id in mapping_data[identifier]["source_unique_drug_ids"]:

                            unique_drug_id_list.append(unique_drug_id)
                            unique_alt_drug_id = "{}##{}".format(unique_drug_id, pre_ordered_unique_drug_id)

                            if unique_alt_drug_id in curr_alternate_drug_option_data:
                                alt_drug_option_update_list.append(unique_alt_drug_id)
                            else:
                                alt_drug_option_insert_data.append(
                                    {"facility_dis_id": facility_dist_id,
                                     "unique_drug_id": unique_drug_id,
                                     "alternate_unique_drug_id": pre_ordered_unique_drug_id,
                                     "active": True,
                                     "created_by": user_id,
                                     "modified_by": user_id})
                    else:
                        # get drug data based on preorder ndc
                        new_unique_drug_id = get_drug_data_based_on_ndc(ndc=pre_ordered_ndc,
                                                                        company_id=company_id, user_id=user_id,
                                                                        facility_dist_id=facility_dist_id)
                        if new_unique_drug_id != 0:
                            for unique_drug_id in mapping_data[identifier]["source_unique_drug_ids"]:
                                unique_drug_id_list.append(unique_drug_id)
                                alt_drug_option_insert_data.append({"facility_dis_id": facility_dist_id,
                                                                    "unique_drug_id": unique_drug_id,
                                                                    "alternate_unique_drug_id": new_unique_drug_id,
                                                                    "active": True,
                                                                    "created_by": user_id,
                                                                    "modified_by": user_id,
                                                                    "modified_date": get_current_date_time()})
                        else:
                            missing_ndc_list.append(pre_ordered_ndc)

            # changes in the AlternateDrugOption table based on the order data
            alternate_drug_option_changes_by_order_data(alt_drug_option_insert_data=alt_drug_option_insert_data,
                                                        alt_drug_option_update_list=alt_drug_option_update_list,
                                                        unique_drug_id_list=unique_drug_id_list, user_id=user_id,
                                                        facility_dist_id=facility_dist_id)

            if missing_ndc_list:
                pre_order_missing_ndc(ndc_list=missing_ndc_list, facility_dist_id=facility_dist_id, user_id=user_id)

        return error_in_pre_order_data

    except TokenMissingException as e:
        logger.error(e)
        raise e
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise e
    except DataDoesNotExistException as e:
        logger.error(e, exc_info=True)
        raise e
    except RealTimeDBException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise e


@log_args_and_response
def populate_order_data(facility_dist_id: int, user_id: int, order_data: Optional[List[Dict[str, Any]]] = None) -> \
        Tuple[Dict[str, List[str]], List[str], bool]:
    """
    Adds/Updates the BatchDrugOrderData and returns the pre-ordered NDCs for the txr_daw combination.
    """
    inventory_order_data: List[Dict[str, Any]] = list()
    inventory_order_data_list: List[Dict[str, Any]] = list()
    pre_ordered_ndc_list: List[str]
    pre_ordered_ndc_dict: Dict[str, List[str]] = dict()
    pre_order_ndc_set: Set[str] = set()
    error_in_pre_order_data: bool = False
    try:
        if order_data:
            # get the BatchDrugData records for the given facility_dist_id
            batch_drug_data: Dict[str, Any] = {
                (record["ndc"] + "##" + str(record["daw"]) + "##" + record["department"]): record for record in
                get_records_by_facility_dist_id_and_dept(facility_dist_id=facility_dist_id)
            }
            for data in order_data:
                ndc_daw_dept: str = str(data["ndc"] + "##" + str(1 if data["daw"] else 0) + "##" + data["department"])
                batch_drug_data_id: int = batch_drug_data[ndc_daw_dept]["batch_drug_data_id"] if (
                        ndc_daw_dept in batch_drug_data) else None
                if batch_drug_data_id:
                    if data.get("pre_ordered_ndc", None):
                        daw_ndc: str = str(data["daw"]) + "##" + str(data["ndc"])
                        pre_ordered_ndc_list = [str(data["pre_ordered_ndc"])]
                        pre_ordered_ndc_dict[daw_ndc] = pre_ordered_ndc_list
                        pre_order_ndc_set.update([data["ndc"], data["pre_ordered_ndc"]])

                    inventory_order_data.append({
                        "batch_drug_data_id": batch_drug_data_id,
                        "ndc": data["ndc"],
                        "original_qty": data["original_qty"],
                        "daw": data["daw"],
                        "pack_size": data["pack_size"],
                        "pack_unit": data["pack_unit"],
                        "cfi": data.get("cfi", None),
                        "is_ndc_active": data["is_ndc_active"],
                        "is_sub": data.get("is_sub", None),
                        "sub_reason": data.get("sub_reason", None),
                        "pre_ordered_ndc": data.get("pre_ordered_ndc", None),
                        "pre_ordered_qty": data.get("pre_ordered_qty", None),
                        "pre_ordered_pack_size": data.get("pre_ordered_pack_size", None),
                        "pre_ordered_pack_unit": data.get("pre_ordered_pack_unit", None),
                        "is_processed": data["is_processed"],
                        "message": data.get("message", None),
                        "created_by": user_id,
                        "modified_by": user_id})
                else:
                    error_in_pre_order_data = True

            if len(inventory_order_data) > 0:
                inventory_order_records: List[Any] = get_inventory_order_data_by_facility_dist_id(
                    facility_dist_id=facility_dist_id)
                if len(inventory_order_records) > 0:
                    batch_drug_data_ids: List[int] = [record["batch_drug_data_id"] for record in
                                                      inventory_order_records]

                    for data in inventory_order_data:
                        if data["batch_drug_data_id"] in batch_drug_data_ids:
                            data.pop("created_by", None)
                            data["modified_date"] = get_current_date_time()
                            update_batch_drug_order_data_by_batch_drug_data_id(
                                update_dict=data, batch_drug_data_id=data["batch_drug_data_id"])
                        else:
                            inventory_order_data_list.append(data)
                    if len(inventory_order_data_list) > 0:
                        populate_batch_order_data(batch_order_data_list=inventory_order_data_list)
                else:
                    populate_batch_order_data(batch_order_data_list=inventory_order_data)

        # considering the reserved ndc from the CurrentInventoryMapping for the AlternateDrugOption update.
        pre_ordered_ndc_dict, pre_order_ndc_set = consider_inventory_mapped_data(
            facility_dist_id=facility_dist_id, ndc_dict=pre_ordered_ndc_dict, ndc_set=pre_order_ndc_set)

        return pre_ordered_ndc_dict, list(pre_order_ndc_set), error_in_pre_order_data

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise e

    except Exception as e:
        logger.error(e)
        raise e


@log_args_and_response
def consider_inventory_mapped_data(facility_dist_id: int, ndc_dict: Dict[str, List[str]],
                                   ndc_set: Set[str]) -> Tuple[Dict[str, List[str]], Set[str]]:
    """
    Adds the current inventory mapping data to the pre_order data for the AlternateDrugOption update
    with inventory consideration as well.
    """
    try:
        for record in get_reserve_ndc_by_facility_dist_id(facility_dist_id=facility_dist_id):
            reserved_ndc_set: Set[str] = set()
            reserved_ndc_list: List[str] = list()
            reserved_ndc_set.add(str(record["ndc"]))
            for reserved_ndc in list(record["reserve_ndc_list"].split(",")):
                reserved_ndc_set.add(str(reserved_ndc))
                reserved_ndc_list.append(reserved_ndc)

            daw_ndc: str = str(record["daw"]) + "##" + str(record["ndc"])
            if daw_ndc in ndc_dict:
                pre_order_ndc_set: Set[str] = set(ndc_dict[daw_ndc])
                pre_order_ndc_set.update(reserved_ndc_list)
                ndc_dict[daw_ndc] = list(pre_order_ndc_set)
            else:
                ndc_dict[daw_ndc] = list(reserved_ndc_list)

            ndc_set.update(list(reserved_ndc_set))

        return ndc_dict, ndc_set

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise e

    except Exception as e:
        logger.error(e)
        raise e


@log_args_and_response
def get_drug_data_based_on_ndc(ndc: str, company_id: int, user_id: int, facility_dist_id: int) -> int:
    """
    Get the drug_data based on ndc from ips
    """
    try:
        # get batch_drug_order_data_id of preorder_ndc and facility_dist_id from BatchDrugOrderData
        batch_drug_order_data = get_batch_drug_data_id_from_ndc(ndc_list=[ndc], facility_dist_id=facility_dist_id)
        company_setting: Dict[str, Any] = get_company_setting_by_company_id(company_id=company_id)
        drug_sync_history: Any = create_drug_sync_history(user_id)

        if drug_sync_history is None or company_setting is None:
            logger.error("Couldn't create drug sync history or company_setting unavailable.")
            return 0

        # get drug data from the IPS for preorder_ndc
        return get_drug_from_ips(ndc=ndc, company_settings=company_setting, user_id=user_id, company_id=company_id,
                                 drug_sync_history=drug_sync_history, batch_drug_data_id=batch_drug_order_data[ndc])

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        return 0

    except Exception as e:
        logger.error(e)
        return 0


@log_args_and_response
def alternate_drug_option_changes_by_order_data(alt_drug_option_insert_data: List[Dict[str, Any]], user_id: int,
                                                alt_drug_option_update_list: List[str], unique_drug_id_list: List[int],
                                                facility_dist_id: int) -> bool:
    """
    Inserts or updates the AlternateDrugOption table based on the order data.
    """
    try:
        with db.transaction():
            if len(alt_drug_option_update_list) > 0:
                update_alternate_drug_option_by_order_data(facility_dist_id=facility_dist_id, user_id=user_id,
                                                           unique_alt_drug_id_list=alt_drug_option_update_list,
                                                           unique_drug_id_list=unique_drug_id_list)
            if len(alt_drug_option_insert_data) > 0:
                populate_alternate_drug_option_by_order_data(alternate_drug_option_data=alt_drug_option_insert_data)

        return True
    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def pre_order_missing_ndc(ndc_list: List[str], facility_dist_id: int, user_id: int) -> bool:
    """
    This function prepares the data & populates the PreOrderMissingNdc table.
    """
    pre_order_missing_ndc_data_list: List[Dict[str, Any]] = list()
    try:
        batch_drug_data: Dict[str, int] = get_batch_drug_data_id_from_ndc(ndc_list=ndc_list,
                                                                          facility_dist_id=facility_dist_id)
        for ndc in ndc_list:
            pre_order_missing_ndc_data_list.append({"batch_drug_data_id": batch_drug_data[ndc],
                                                    "ndc": ndc,
                                                    "created_by": user_id})
        return populate_pre_order_missing_ndc(pre_order_missing_ndc_data_list=pre_order_missing_ndc_data_list)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e

    except Exception as e:
        logger.error(e)
        raise e


@log_args_and_response
@validate(required_fields=["facility_dist_id", "company_id"])
def get_pre_order_data_by_facility_dis_id(data_dict: Dict[str, Any]) -> str:
    """
    This function fetches the pre-order and its corresponding data for the given facility_dist_id.
    """
    facility_dist_id: int = data_dict.get("facility_dist_id", 0)
    company_id: int = data_dict.get("company_id", 0)
    req_drug_search: str = data_dict.get("req_drug_search", None)
    avl_pre_order_drug_search: str = data_dict.get("avl_pre_order_drug_search", None)
    filter_by: str = data_dict.get("filter_by", None)
    pre_order_flag: bool = False
    available_flag: bool = False
    batch_data: Dict[str, Dict[str, Any]]
    ndc_set: Set[str]
    unique_drug_id_set: Set[int]
    drug_data: Dict[str, Any] = dict()
    canister_data: Dict[int, Any] = dict()
    try:
        # validate facility_dist_id for the given company_id
        if company_id and facility_dist_id:
            if not validate_facility_dist_id_by_company_id(company_id=company_id, facility_dist_id=facility_dist_id):
                return error(20003)

        if filter_by:
            if filter_by.casefold() == FILTER_PRE_ORDER_EPBM_BATCH_ORDER_DATA:
                pre_order_flag = True
            if filter_by.casefold() == FILTER_AVAILABLE_EPBM_BATCH_ORDER_DATA:
                available_flag = True
        else:
            pre_order_flag = available_flag = True

        # get the requested and pre_order data for the given facility_dist_id
        batch_pre_order_data: List[Any] = get_data_for_modified_drug_list(
            facility_dist_id=facility_dist_id, req_drug_search=req_drug_search,
            avl_pre_order_drug_search=avl_pre_order_drug_search)

        if batch_pre_order_data:
            batch_data, ndc_set, unique_drug_id_set = prepare_required_requested_available_data(
                pre_order_flag=pre_order_flag, available_flag=available_flag, batch_pre_order_data=batch_pre_order_data)

            if batch_data:
                # get the drug details for all the NDCs that are requested or pre_ordered
                if ndc_set:
                    drug_data = get_drug_data_by_ndc_list(ndc_list=list(ndc_set), company_id=company_id)

                # get the canister data corresponding to all the NDCs that are requested or pre_ordered
                if unique_drug_id_set:
                    canister_data = get_canister_data_by_unique_drug_id_list(id_list=list(unique_drug_id_set),
                                                                             company_id=company_id)

                return create_response({"required_requested_available_data": [batch_data[ndc] for ndc in batch_data],
                                        "drug_data": drug_data, "canister_data": canister_data})

        return create_response({"required_requested_available_data": [], "drug_data": drug_data,
                                "canister_data": canister_data})

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        return error(2001)

    except Exception as e:
        logger.error(e)
        return error(2001)


@log_args_and_response
def prepare_required_requested_available_data(batch_pre_order_data: List[Any], pre_order_flag: bool,
                                              available_flag: bool) -> Tuple[Dict[str, Dict[str, Any]],
                                                                             Set[str], Set[int]]:
    """
    Prepares the pre_order and reserved data for the requested, along with all distinct NDCs and unique_drug_ids.
    """
    batch_data: Dict[str, Dict[str, Any]] = dict()
    ndc_set: Set[str] = set()
    unique_drug_id_set: Set[int] = set()
    pre_order_data: Dict[str, Any] = dict()
    available_data: Dict[str, Any] = dict()
    available_ndc_flag: bool
    pre_order_ndc_flag: bool
    result_data: Dict[str, Dict[str, Any]] = dict()
    try:
        for data in batch_pre_order_data:
            # prepare the pre_order_data dictionary.
            pre_order_data.clear()
            if pre_order_flag:
                if data["batch_drug_order_data_id"] and data["pre_ordered_ndc"]:
                    ndc_set.add(data["pre_ordered_ndc"])
                    unique_drug_id_set.add(data["pre_ordered_unique_drug_id"])
                    pre_order_data = {"batch_drug_order_data_ids": [data["batch_drug_order_data_id"]],
                                      "pre_ordered_ndc": data["pre_ordered_ndc"],
                                      "pre_ordered_qty": data["pre_ordered_qty"],
                                      "is_substituted": data["is_substituted"],
                                      "substitution_reason": data["substitution_reason"],
                                      "pre_ordered_unique_drug_id": data["pre_ordered_unique_drug_id"]}

            # prepare the available_data dictionary
            available_data.clear()
            if available_flag:
                if data["current_inventory_mapped_id"] and data["available_is_active"] and data["available_ndc"]:
                    ndc_set.add(data["available_ndc"])
                    unique_drug_id_set.add(data["available_unique_drug_id"])
                    available_data = {"current_inventory_mapped_ids": [data["current_inventory_mapped_id"]],
                                      "available_ndc": data["available_ndc"],
                                      "available_qty": data["available_qty"],
                                      "available_unique_drug_id": data["available_unique_drug_id"]}

            # prepare the required_data dictionary.
            if data["requested_ndc"] in batch_data:
                if data["batch_drug_data_id"] not in batch_data[data["requested_ndc"]]["batch_drug_ids"]:
                    batch_data[data["requested_ndc"]]["batch_drug_ids"].append(data["batch_drug_data_id"])
                    batch_data[data["requested_ndc"]]["required_qty"] += data["required_qty"]
            else:
                ndc_set.add(data["requested_ndc"])
                unique_drug_id_set.add(data["requested_unique_drug_id"])
                # updating the batch_data with the required_data dict
                batch_data[data["requested_ndc"]] = {"batch_drug_ids": [data["batch_drug_data_id"]],
                                                     "requested_ndc": data["requested_ndc"],
                                                     "required_qty": data["required_qty"],
                                                     "requested_unique_drug_id": data["requested_unique_drug_id"]}

            # updating the batch_data with the pre_order data
            if pre_order_data:
                if "pre_ordered" in batch_data[data["requested_ndc"]]:
                    pre_order_ndc_flag = False
                    for pre_order_record in batch_data[data["requested_ndc"]]["pre_ordered"]:
                        if pre_order_record["pre_ordered_ndc"] == pre_order_data["pre_ordered_ndc"]:
                            pre_order_ndc_flag = True
                            pre_order_record["batch_drug_order_data_ids"].append(
                                pre_order_data["batch_drug_order_data_ids"][0])
                            pre_order_record["pre_ordered_qty"] += pre_order_data["pre_ordered_qty"]
                    if not pre_order_ndc_flag:
                        batch_data[data["requested_ndc"]]["pre_ordered"].append(pre_order_data.copy())
                else:
                    batch_data[data["requested_ndc"]]["pre_ordered"] = [pre_order_data.copy()]

            # updating the batch_data with the available data
            if available_data:
                if "available" in batch_data[data["requested_ndc"]]:
                    available_ndc_flag = False
                    for available_record in batch_data[data["requested_ndc"]]["available"]:
                        if available_record["available_ndc"] == available_data["available_ndc"]:
                            available_ndc_flag = True
                            available_record["current_inventory_mapped_ids"].append(
                                available_data["current_inventory_mapped_ids"][0])
                            available_record["available_qty"] += available_data["available_qty"]
                    if not available_ndc_flag:
                        batch_data[data["requested_ndc"]]["available"].append(available_data.copy())
                else:
                    batch_data[data["requested_ndc"]]["available"] = [available_data.copy()]

        for record in batch_data:
            if ("pre_ordered" in batch_data[record]) or ("available" in batch_data[record]):
                result_data[record] = batch_data[record]

        return result_data, ndc_set, unique_drug_id_set

    except Exception as e:
        logger.error(e)
        raise e


@log_args_and_response
@validate(required_fields=["company_id", "time_zone", "system_id_list"])
def check_and_update_drug_req(data_dict: Dict[str, Any]) -> str:
    """
    Check the drug requirements of the upcoming n days and add it to the pre_order list of the Drug Inventory,
    in case of inadequate available quantity.
    """
    company_id: int = data_dict.get("company_id", 0)
    time_zone: str = data_dict.get("time_zone")
    batch_id: str = data_dict.get("batch_id", None)
    system_id_list = data_dict.get("system_id_list") if type(data_dict.get("system_id_list")) is list else [int(x) for x in str(data_dict.get("system_id_list")).split(",")]
    system_id_list = list(map(int, system_id_list))
    current_date: Optional[str] = None
    end_date: str
    current_day_index: int
    pack_id_list: List[int] = list()
    robot_pack_ids_drug_data: List[Any]
    drug_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = dict()
    requirement_data: Tuple[Dict[str, Dict[int, Dict[str, Dict[str, Any]]]], Dict[int, Dict[Any, Any]]]
    inventory_consideration: Dict[str, Dict[str, Dict[str, int]]] = dict()
    batch_pack_data: List[Dict[str, Any]] = list()
    error_msgs: List[str] = list()
    drug_list: list = data_dict.get('drug_list', [])
    robot_order_drugs: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = dict()
    man_order_drugs: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = dict()

    try:
        current_date: str = get_current_day_date_end_date_by_timezone(time_zone=time_zone)[0]
        # get the data from the company_setting table for the given company_id
        company_setting: Dict[str, Any] = get_company_setting_by_company_id(company_id=company_id)

        # check if the parameter NUMBER_OF_DAYS_TO_FETCH_PO present in CompanySetting table
        number_of_days_to_fetch_po: int = int(company_setting.get(NUMBER_OF_DAYS_TO_FETCH_PO, 0))
        if not number_of_days_to_fetch_po:
            send_email_for_drug_req_check_failure(company_id=company_id, current_date=current_date, time_zone=time_zone,
                                                  error_details=(err[20012] + NUMBER_OF_DAYS_TO_FETCH_PO))
            return error(20012, NUMBER_OF_DAYS_TO_FETCH_PO)

        # update the local drug inventory
        error_msgs = update_local_inventory_by_ack_po(no_of_days_for_po=number_of_days_to_fetch_po,
                                                      department=EPBM_DOSEPACK_DEPARTMENT)

        # check if the parameter NUMBER_OF_DAYS_TO_ORDER present in CompanySetting table
        number_of_days: int = int(company_setting.get(NUMBER_OF_DAYS_TO_ORDER, 0))
        if not number_of_days:
            send_email_for_drug_req_check_failure(company_id=company_id, current_date=current_date, time_zone=time_zone,
                                                  error_details=(err[20012] + NUMBER_OF_DAYS_TO_ORDER))
            return error(20012, NUMBER_OF_DAYS_TO_ORDER)

        # check if the all manual parameters present in CompanySetting table
        for param_name in MANUAL_CAPACITY:
            if param_name not in company_setting:
                send_email_for_drug_req_check_failure(company_id=company_id, error_details=(err[20012] + param_name),
                                                      current_date=current_date, time_zone=time_zone)
                return error(20012, param_name)

        # get the data from the system_setting table for the given system_id_list
        system_setting: Dict[int, Dict[str, str]] = get_system_setting_data(system_id_list=system_id_list)

        system_id_list_copy = system_id_list.copy()

        for system_id in system_id_list:
            if system_id not in system_setting:
                system_id_list_copy.remove(system_id)

        if not len(system_id_list_copy):
            send_email_for_drug_req_check_failure(company_id=company_id, current_date=current_date, time_zone=time_zone,
                                                  error_details=(err[20013] + str(system_id_list)))
            return error(20013, str(system_id_list))
        else:
            system_id_list = system_id_list_copy

        # get the date and day information based on the time-zone
        current_date, end_date, current_day_index = get_current_day_date_end_date_by_timezone(
            time_zone=time_zone, number_of_days=number_of_days)

        if batch_id:
            # if called when batch is saved then unique id will have batch id
            unique_id: str = str(company_id) + "@@B" + batch_id
        elif drug_list:
            current_datetime = get_current_datetime_by_timezone(time_zone)
            unique_id: str = str(company_id) + "@@DA" + "".join(re.findall(r"\d+", current_datetime))
        else:
            # generate the unique_id for the ordering of drugs
            unique_id: str = str(company_id) + "@@" + current_date.replace("-", "")

        # calculate the manual and system capacity for upcoming number_of_days
        capacity: Dict[str, Any] = get_capacity_for_upcoming_days(company_setting=company_setting,
                                                                  system_setting=system_setting,
                                                                  number_of_days=number_of_days,
                                                                  current_day_index=current_day_index)

        # get the pack_ids for the robot filling with the delivery dates in the upcoming number_of_days from today.
        robot_pack_ids: List[int] = get_pack_ids_for_upcoming_days(company_id=company_id, system_id_list=system_id_list,
                                                                   current_date=current_date, end_date=end_date,
                                                                   capacity=capacity, pack_type=ROBOT)

        # get the drug data for the packs corresponding to the given pack_id_list
        if robot_pack_ids:
            pack_id_list.extend(robot_pack_ids)
            robot_pack_ids_drug_data: List[Any] = get_batch_drug_data(pack_id_list=robot_pack_ids)

            if len(robot_pack_ids_drug_data) <= 0:
                logger.debug("There are no robot drugs to be ordered.")

            # group the data by txr & daw to get the order data and the inventory_data

            robot_order_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = get_drugs_to_order_by_facility_dist_id(
                drug_data=drug_data, pack_drug_data=robot_pack_ids_drug_data, drug_list=drug_list)[0]

            # differentiate the drugs by drug type (canister / manual)
            data_dict: Dict[str, Any] = differentiate_by_drug_type(order_data=robot_order_data, company_id=company_id)
            robot_order_drugs: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = data_dict["canister_order_drugs"]
            drug_data: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = data_dict["manual_order_drugs"]

        man_pack_ids: List[int] = get_pack_ids_for_upcoming_days(company_id=company_id, system_id_list=system_id_list,
                                                                 current_date=current_date, end_date=end_date,
                                                                 capacity=capacity, pack_type=MANUAL)

        if man_pack_ids:
            pack_id_list.extend(man_pack_ids)
            man_pack_ids_drug_data: List[Any] = get_batch_drug_data(pack_id_list=man_pack_ids)

            if len(drug_data) <= 0 and len(man_pack_ids_drug_data) <= 0:
                logger.debug("There are no manual drugs to be ordered.")

            # group the data by txr & daw to get the order data and the inventory_data
            man_order_drugs: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = get_drugs_to_order_by_facility_dist_id(
                drug_data=drug_data, pack_drug_data=man_pack_ids_drug_data,  drug_list=drug_list)[0]

        if robot_order_drugs or man_order_drugs:
            order_req, inventory_mapping, bypassed = prepare_order_data_and_place_order(
                robot_order_data=robot_order_drugs, manual_order_data=man_order_drugs, unique_id=unique_id, department=EPBM_DOSEPACK_DEPARTMENT,
                company_id=company_id, add_to_pre_order=True, local_di=True)

            if inventory_mapping:
                inventory_consideration["robot"] = dict()
                for data in inventory_mapping:
                    inventory_consideration["robot"][data] = {record["reserve_ndc"]: record["reserve_qty"]
                                                              for record in inventory_mapping[data]}

        '''
        For now from FEB 2023, we are going to order both manual and robot drugs with same department name as DOSEPACK.
        This is as IPS will be going to use VIBRANT department to order PRN drugs from there side.
        In department merge, we are still adding buffer to order canister drug
        '''

        # man_pack_ids: List[int] = get_pack_ids_for_upcoming_days(company_id=company_id, system_id_list=system_id_list,
        #                                                          current_date=current_date, end_date=end_date,
        #                                                          capacity=capacity, pack_type=MANUAL)
        # if man_pack_ids:
        #     pack_id_list.extend(man_pack_ids)
        #     man_pack_ids_drug_data: List[Any] = get_batch_drug_data(pack_id_list=man_pack_ids)
        #
        #     if len(drug_data) <= 0 and len(man_pack_ids_drug_data) <= 0:
        #         logger.debug("There are no manual drugs to be ordered.")
        #
        #     # group the data by txr & daw to get the order data and the inventory_data
        #     man_order_drugs: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = get_drugs_to_order_by_facility_dist_id(
        #         drug_data=drug_data, pack_drug_data=man_pack_ids_drug_data,  drug_list=drug_list)[0]
        #
        #     if man_order_drugs:
        #         order_req, man_inventory_mapping, bypassed = prepare_order_data_and_place_order(
        #             robot_order_data=man_order_drugs, unique_id=unique_id, department=EPBM_VIBRANT_DEPARTMENT,
        #             company_id=company_id, add_to_pre_order=True, local_di=False)
        #
        #         if man_inventory_mapping:
        #             inventory_consideration["manual"] = dict()
        #             for data in man_inventory_mapping:
        #                 inventory_consideration["manual"][data] = {record["reserve_ndc"]: record["reserve_qty"]
        #                                                            for record in man_inventory_mapping[data]}

        # populate BatchPackData table
        batch_pack_data.append({"unique_id": unique_id,
                                "pack_id_list": list(pack_id_list),
                                "inventory_consideration": inventory_consideration})
        populate_batch_pack_data(batch_pack_data_list=batch_pack_data)
        logger.info("Output of check_and_update_drug_req " + SUCCESS_RESPONSE)
        return create_response(SUCCESS_RESPONSE)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        send_email_for_drug_req_check_failure(company_id=company_id, error_details=(err[2001] + str(e)),
                                              current_date=current_date, time_zone=time_zone)
        return error(2001, e)
    except UnknownTimeZoneError as e:
        logger.error(e, exc_info=True)
        send_email_for_drug_req_check_failure(company_id=company_id, error_details=(err[20011] + str(e)),
                                              current_date=current_date, time_zone=time_zone)
        return error(20011, e)
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        send_email_for_drug_req_check_failure(company_id=company_id, error_details=(err[2001] + str(e)),
                                              current_date=current_date, time_zone=time_zone)
        return error(2001)
    except TokenFetchException as e:
        logger.error(e)
        send_email_for_drug_req_check_failure(company_id=company_id, error_details=(err[20001] + str(e)),
                                              current_date=current_date, time_zone=time_zone)
        return error(20001)
    except APIFailureException as e:
        logger.error(e, exc_info=True)
        send_email_for_drug_req_check_failure(company_id=company_id, error_details=(err[20002] + str(e)),
                                              current_date=current_date, time_zone=time_zone)
        return error(20002, "Error from the ElitePBM server: {}.".format(e))
    except Exception as e:
        logger.error(e, exc_info=True)
        send_email_for_drug_req_check_failure(company_id=company_id, error_details=(err[2001] + str(e)),
                                              current_date=current_date, time_zone=time_zone)
        return error(2001)

    finally:
        logger.debug("Inside finally block of check_and_update_drug_req")
        if len(error_msgs) > 0:
            msg_str: str = err[20014]
            for i in range(0, len(error_msgs)):
                msg_str += "<br>" + str(i + 1) + ") " + str(error_msgs[i])

            send_email_for_same_ndc_diff_txr(company_id=company_id, error_details=msg_str)

        return create_response(SUCCESS_RESPONSE)


@log_args_and_response
def get_capacity_for_upcoming_days(company_setting: Dict[str, int], current_day_index: int, number_of_days: int,
                                   system_setting: Dict[int, Dict[str, str]]) -> Dict[str, Any]:
    """
    Calculates the manual and system capacity for the respective company and the given system_id for the upcoming days.
    """
    upcoming_days: List[str] = list()
    manual_capacity: int = 0
    auto_capacity: Dict[int, int] = dict()
    try:
        upcoming_days.append(WEEKDAYS[current_day_index])
        upcoming_days.extend([WEEKDAYS[(current_day_index + i) - len(WEEKDAYS) if current_day_index + i > (
                len(WEEKDAYS) - 1) else current_day_index + i] for i in range(1, number_of_days + 1)])

        logger.info("upcoming_days: {}".format(upcoming_days))

        # per hour manual packs filling by all the Manual Users
        all_manual_per_hour: int = int(company_setting[MANUAL_USER_COUNT]) * int(company_setting[MANUAL_PER_HOUR])

        # calculate the filling capacity for the manual and for all the given system_ids.
        # when one of the upcoming day is Sunday
        if SUNDAY in upcoming_days:
            manual_capacity += all_manual_per_hour * int(company_setting[MANUAL_SUNDAY_HOURS])

            for system_id in system_setting:
                if system_id in auto_capacity:
                    auto_capacity[system_id] += int(system_setting[system_id][AUTOMATIC_PER_HOUR]) * \
                                                int(system_setting[system_id][AUTOMATIC_SUNDAY_HOURS])
                else:
                    auto_capacity[system_id] = int(system_setting[system_id][AUTOMATIC_PER_HOUR]) * \
                                               int(system_setting[system_id][AUTOMATIC_SUNDAY_HOURS])
            upcoming_days.remove(SUNDAY)

        # when one of the upcoming day is Saturday
        if SATURDAY in upcoming_days:
            manual_capacity += all_manual_per_hour * int(company_setting[MANUAL_SATURDAY_HOURS])

            for system_id in system_setting:
                if system_id in auto_capacity:
                    auto_capacity[system_id] += int(system_setting[system_id][AUTOMATIC_PER_HOUR]) * \
                                                int(system_setting[system_id][AUTOMATIC_SATURDAY_HOURS])
                else:
                    auto_capacity[system_id] = int(system_setting[system_id][AUTOMATIC_PER_HOUR]) * \
                                               int(system_setting[system_id][AUTOMATIC_SATURDAY_HOURS])
            upcoming_days.remove(SATURDAY)

        # for weekdays other than Saturday & Sunday
        manual_capacity += (all_manual_per_hour * int(company_setting[MANUAL_PER_DAY_HOURS])) * len(upcoming_days)

        for system_id in system_setting:
            if system_id in auto_capacity:
                auto_capacity[system_id] += int(system_setting[system_id][AUTOMATIC_PER_HOUR]) * \
                                            int(system_setting[system_id][AUTOMATIC_PER_DAY_HOURS]) * len(upcoming_days)
            else:
                auto_capacity[system_id] = int(system_setting[system_id][AUTOMATIC_PER_HOUR]) * \
                                           int(system_setting[system_id][AUTOMATIC_PER_DAY_HOURS]) * len(upcoming_days)

        return {"manual_capacity": manual_capacity, "auto_capacity": auto_capacity}

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_system_setting_data(system_id_list: List[int]) -> Dict[int, Dict[str, str]]:
    """
    get system_setting data for the given system_id_list
    """
    result_dict: Dict[int, Dict[str, str]] = dict()
    try:
        system_setting: List[Any] = get_system_setting_by_system_ids(system_id_list=system_id_list)

        for data in system_setting:
            if data["system_id"] in result_dict:
                result_dict[data["system_id"]][data["name"]] = data["value"]
            else:
                result_dict[data["system_id"]] = {data["name"]: data["value"]}

        for system_id in system_id_list:
            if system_id not in result_dict:
                print("System Capacity Data unavailable for system_id: {}.".format(system_id))

        return result_dict
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_adhoc_drug_request_by_inventory_response(response_list: List[Dict[str, Any]], unique_id: str) -> bool:
    """
    Update the  BatchDrugData table based on the response from the inventory.
    """
    pre_ordered_data_dict: Dict[str, Any] = dict()
    table_update_dict = {}

    try:
        # with db.transaction():
        for key in response_list:
            if key.get("daw", None) is None:
                update_dict = {"ext_is_success": key["isSuccess"],
                               "ext_note": key["note"],
                               "modified_date": get_current_date_time()}
                update_adhoc_drug_request_by_ndc(data=update_dict, unique_id=unique_id, ndc=key["ndc"])
            else:
                if key["daw"]:
                    identifier: str = str(key["ndc"])[0:9] + "##" + str(key["cfi"]) + "##" + str(1 if key["daw"] else 0)
                else:
                    identifier: str = str(key["cfi"]) + "##" + str(1 if key["daw"] else 0)
                pre_ordered_data_dict[identifier] = key
        for fndc_txr_daw in pre_ordered_data_dict:
            update_dict = {"ext_is_success": pre_ordered_data_dict[fndc_txr_daw]["isSuccess"],
                           "ext_note": pre_ordered_data_dict[fndc_txr_daw]["note"]}
            table_update_dict[fndc_txr_daw] = update_dict

            # update the AdhocDrugRequest table based on response from webservice
        if table_update_dict:
            update_adhoc_drug_request_by_fndc_txr_daw_case(data=table_update_dict, unique_id=unique_id)
        return True
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_pack_ids_for_upcoming_days(company_id: int, system_id_list: List[int], current_date: str, end_date: str,
                                   capacity: Dict[str, Any], pack_type: str) -> List[int]:
    """
    Fetches the pack_ids that are to be filled in the upcoming number_of_days.
    """
    manual_pack_data: List[Any]
    auto_pack_data: List[Any]
    pack_ids: List[int] = list()
    try:

        if pack_type == MANUAL:
            # get manual pack details of the packs that are scheduled to be delivered in the upcoming number_of_days
            manual_pack_data = get_manual_pack_ids_for_upcoming_days(company_id=company_id, current_date=current_date,
                                                                     end_date=end_date)

            # if the manual capacity is more than the scheduled delivery packs
            if len(manual_pack_data) < capacity["manual_capacity"]:
                manual_pack_data = get_manual_pack_ids_for_upcoming_days(company_id=company_id,
                                                                         current_date=current_date,
                                                                         manual_capacity=capacity["manual_capacity"])
            pack_ids.extend([int(record["pack_id"]) for record in manual_pack_data])

        if pack_type == ROBOT:
            # get pack details that are scheduled to be delivered in the upcoming number_of_days by each system
            for system_id in system_id_list:
                auto_pack_data = get_auto_pack_ids_for_upcoming_days(company_id=company_id, current_date=current_date,
                                                                     end_date=end_date)

                # if the system capacity is more than the scheduled delivery packs
                if len(auto_pack_data) < capacity["auto_capacity"][system_id]:
                    auto_pack_data = get_auto_pack_ids_for_upcoming_days(company_id=company_id,
                                                                         current_date=current_date,
                                                                         auto_capacity=capacity["auto_capacity"][
                                                                             system_id])
                pack_ids.extend([record["pack_id"] for record in auto_pack_data])

        return pack_ids

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
@validate(required_fields=["unique_id", "department"])
def update_ack_department(data_dict: Dict[str, Any]) -> str:
    """
    Updates the department in the couchDB for which the drug are added to the pre-order list in the drug inventory.
    """
    if "unique_id" in data_dict:
        unique_id: str = data_dict["unique_id"]
    else:
        return error(1001, "Missing Parameter: unique_id")

    if "department" in data_dict:
        department: str = data_dict.get("department", None)
    else:
        return error(1001, "Missing Parameter: department")

    try:
        # get the user id from token
        user_data: Dict[str, Any] = get_user_from_header_token()
        if user_data is not None:
            user_id = int(user_data["id"])
        else:
            return error(5019)

        # ignoring the calls for the daily drug request check.
        if "@@" in unique_id:
            return create_response(SUCCESS_RESPONSE)

        # fetching facility_dist_id from the unique_id
        company_id: int = int(unique_id.strip().split("##")[0])
        facility_dist_id: int = int(unique_id.strip().split("##")[1])

        trigger_call: bool = process_dept_for_facility_dist_id(facility_dist_id=facility_dist_id, user_id=user_id,
                                                               ack_dept=department)

        update_drug_inventory_couch_db_status(company_id=company_id, facility_dist_id=facility_dist_id,
                                              trigger_call=trigger_call)

        return create_response(SUCCESS_RESPONSE)
    except RealTimeDBException as e:
        logger.error(e, exc_info=True)
        return error(11002)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["facility_dist_id", "company_id"])
def fetch_pre_order_data_from_drug_inventory(data_dict: Dict[str, Any]) -> str:
    """
    Fetch the drug added in the pre-order list for the requested drug as part of the given unique_id.
    """
    facility_dist_id: int = int(data_dict.get("facility_dist_id", None))
    company_id: int = int(data_dict.get("company_id", None))
    inventory_data: List[Dict[str, Any]] = list()
    try:
        # get the user id from token
        user_data: Dict[str, Any] = get_user_from_header_token()
        if user_data is not None:
            user_id: int = int(user_data["id"])
        else:
            return error(5019)

        if company_id and facility_dist_id:
            if not validate_facility_dist_id_by_company_id(company_id=company_id, facility_dist_id=facility_dist_id):
                return error(20003)

        unique_id: str = str(company_id) + "##" + str(facility_dist_id)
        inventory_raw_data: List[Dict[str, Any]] = fetch_pre_order_data(unique_id=unique_id)
        if inventory_raw_data:
            for data in inventory_raw_data:
                if data["isAddedToPreOrderList"]:
                    temp_dict: Dict[str, Any] = {
                        "department": str(data["department"]),
                        "ndc": f'{data["ndc"]:011}',
                        "original_qty": int(data["originalQuantity"]),
                        "daw": 1 if data["dAW"] else 0,
                        "pack_size": int(data["packSize"]),
                        "pack_unit": int(data["packUnit"]),
                        "cfi": str(data["cfi"]) if "cfi" in data else None,
                        "is_ndc_active": 1 if data["isNdcActive"] else 0,
                        "is_sub": 1 if data["isSubstitutionMade"] else 0,
                        "sub_reason": str(data["substitutionReason"]) if "substitutionReason" in data else None,
                        "pre_ordered_ndc": f'{data["preOrderListNdc"]:011}',
                        "pre_ordered_qty": int(data["preOrderListQuantity"] * data["preOrderListPackUnit"] *
                                               data["preOrderListPackSize"]),
                        "pre_ordered_pack_size": int(data["preOrderListPackSize"]),
                        "pre_ordered_pack_unit": int(data["preOrderListPackUnit"]),
                        "is_processed": 1 if data["isProcessed"] else 0,
                        "message": str(data["message"]) if "message" in data else None
                    }
                    inventory_data.append(temp_dict.copy())

        error_in_pre_order_data: bool = update_ordered_drug_data(company_id=company_id, pre_ordered_data=inventory_data,
                                                                 facility_dist_id=facility_dist_id, user_id=user_id)

        update_drug_inventory_couch_db_status(company_id=company_id, facility_dist_id=facility_dist_id,
                                              status=DRUG_INVENTORY_MANAGEMENT_ADDED_TO_CART_ID)

        if error_in_pre_order_data:
            return error(20008)

        return create_response(SUCCESS_RESPONSE)
    except TokenMissingException as e:
        logger.error(e, exc_info=True)
        return error(20006)
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except APIFailureException as e:
        logger.error(e, exc_info=True)
        return error(20002, "{}".format(e))
    except TokenFetchException as e:
        logger.error(e, exc_info=True)
        return error(20001, "{}".format(e))
    except DrugInventoryInternalException as e:
        logger.error(e, exc_info=True)
        return error(20009, "{}".format(e))
    except DrugInventoryValidationException as e:
        logger.error(e, exc_info=True)
        return error(20010, "{}".format(e))
    except MissingParameterException as e:
        logger.error(e, exc_info=True)
        return error(1001, "{}".format(e))
    except RealTimeDBException as e:
        logger.error(e, exc_info=True)
        return error(11002)
    except DataDoesNotExistException as e:
        logger.error(e, exc_info=True)
        return error(20005)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def process_dept_for_facility_dist_id(facility_dist_id: int, user_id: int, req_dept_list: Optional[List[str]] = None,
                                      ack_dept: Optional[str] = None) -> bool:
    """
    Checks if to trigger the call to fetch the pre_order data. Updates the FacilityDistributionMaster accordingly.
    """
    req_list: Optional[List[str]]
    ack_list: Optional[List[str]]
    db_ack_list: Optional[str] = ""
    db_req_list: str = ""
    to_trigger: bool = False
    update_db: bool = False
    try:
        req_list, ack_list = get_facility_dist_data_by_id(facility_dist_id=facility_dist_id)

        req_list = req_list if req_list else []
        ack_list = ack_list if ack_list else []

        if req_dept_list:
            if req_list:
                req_list = []
            for req_dept in req_dept_list:
                if ack_list and req_dept in ack_list:
                    ack_list = None
                req_list.append(req_dept)
                update_db = True
            db_ack_list = ",".join(set(ack_list)) if ack_list else None
            db_req_list = ",".join(set(req_list))

        if ack_dept:
            db_req_list = ",".join(set(req_list))
            to_trigger = True
            if ack_dept not in ack_list:
                ack_list.append(ack_dept)
                update_db = True
            for req_dept in req_list:
                if req_dept not in ack_list:
                    to_trigger = False
            db_ack_list = ",".join(set(ack_list))

        if update_db:
            update_data: Dict[str, Any] = {"req_dept_list": db_req_list, "ack_dept_list": db_ack_list,
                                           "modified_by": user_id, "modified_date": get_current_date_time()}

            update_facility_dist_data_by_id(update_data=update_data, facility_dist_id=facility_dist_id)

        return to_trigger

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e

@log_args_and_response
def update_alternate_drug_based_on_past_ordering(drug_list, facility_dist_id, user_id, company_id):
    ndc_list = []
    alt_drug_option_update_list= []
    alt_drug_option_insert_data = []
    unique_drug_id_list = []
    actual_order = {}
    missing_ndc_list = []
    try:
        for order_data in drug_list:
            if order_data['daw'] == False:
                ndc_list.append(str(order_data['ndc']).zfill(11))
                actual_order[int(order_data['ndc'])] = order_data


        # get past orders
        if ndc_list:
            past_orders, all_ndc_list, ordering_data = get_last_order_data_ny_ndc(ndc_list)
            if past_orders:
                status = populate_batch_drug_and_order_data(ordering_data, facility_dist_id, user_id, actual_order)

                logger.info("In update_alternate_drug_based_on_past_ordering: Changing drug based on past order {}".format(past_orders))
                # get unique_drug_data from list
                # insert_data_in_batch DrugData and batchdrug order data
                # ndc_unique_drug = db_get_unique_drug_by_ndc_list(all_ndc_list)

                # add or update alternatedrugoption
                #get current alternate drug  apping:
                alternate_data = get_alternate_drug_dao(facility_distribution_id=facility_dist_id)
                curr_alternate_drug_option_data = [
                    ("{}##{}".format(record["unique_drug_id"], record["alternate_unique_drug_id"])) for record in
                    alternate_data]
                drug_data: Dict[str, Any] = get_drug_data_from_ndc_list(ndc_list=all_ndc_list)

                for old_ndc, alternate_ndc in past_orders.items():

                    unique_drug = drug_data[old_ndc]["unique_drug_id"]
                    if alternate_ndc in drug_data:

                        alternate_unique_drug = drug_data[alternate_ndc]["unique_drug_id"]
                        unique_alt_drug_id = "{}##{}".format(unique_drug, alternate_unique_drug)
                        unique_drug_id_list.append(unique_drug)

                        if unique_alt_drug_id in curr_alternate_drug_option_data:
                            alt_drug_option_update_list.append(unique_alt_drug_id)
                        else:
                            alt_drug_option_insert_data.append(
                                {"facility_dis_id": facility_dist_id,
                                 "unique_drug_id": unique_drug,
                                 "alternate_unique_drug_id": alternate_unique_drug,
                                 "active": True,
                                 "created_by": user_id,
                                 "modified_by": user_id})

                    else:
                        new_unique_drug_id = get_drug_data_based_on_ndc(ndc=alternate_ndc,
                                                                        company_id=company_id, user_id=user_id,
                                                                        facility_dist_id=facility_dist_id)
                        if new_unique_drug_id != 0:
                            unique_drug_id_list.append(unique_drug)
                            alt_drug_option_insert_data.append({"facility_dis_id": facility_dist_id,
                                                                "unique_drug_id": unique_drug,
                                                                "alternate_unique_drug_id": new_unique_drug_id,
                                                                "active": True,
                                                                "created_by": user_id,
                                                                "modified_by": user_id,
                                                                "modified_date": get_current_date_time()})
                        else:
                            missing_ndc_list.append(new_unique_drug_id)


                    # changes in the AlternateDrugOption table based on the order data
            alternate_drug_option_changes_by_order_data(
                                alt_drug_option_insert_data=alt_drug_option_insert_data,
                                alt_drug_option_update_list=alt_drug_option_update_list,
                                unique_drug_id_list=unique_drug_id_list, user_id=user_id,
                                facility_dist_id=facility_dist_id)

            # if missing_ndc_list:
            #     pre_order_missing_ndc(ndc_list=missing_ndc_list, facility_dist_id=facility_dist_id, user_id=user_id)

            update_data: Dict[str, Any] = {"ordering_bypass": True,
                                           "modified_by": user_id, "modified_date": get_current_date_time()}

            update_facility_dist_data_by_id(update_data=update_data, facility_dist_id=facility_dist_id)

        return True

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in update_alternate_drug_based_on_past_ordering: {}".format(e), exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in update_alternate_drug_based_on_past_ordering: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def inventory_mark_in_stock_status(args):
    inventory_update = args.get('inventory_update', [])
    token = get_token()
    user_details = get_current_user(token=token)
    company_id = user_details['company_id']
    updated_drug_list = []
    drug_list = []
    system_device = []
    try:
        for record in inventory_update:
            ndc = str(record['ndc']).zfill(11)
            qty = record['qty']
            drug_info = get_drug_info_based_on_ndc_dao([ndc])
            if ndc in drug_info:
                if record['in_stock'] == 1:
                    status, update_inventory = update_drug_status_dao(drug_info[ndc]['id'], 1, user_details)
                    drug_list.append(ndc)
                    updated_drug_list.append(drug_info[ndc]['id'])

            if drug_list:
                canister_list = get_canister_data_by_ndc_and_company_id_dao(drug_list, company_id)
                # check if canister is goinh to be used in batch and is skipped...
                for canister in canister_list:
                    canister_id = canister['id']
                    pack_analysis_details_update_status, reverted_packs, system_device = update_status_in_pack_analysis_details_for_out_of_stock(
                        canister_id=canister_id,
                        company_id=company_id)

                    if pack_analysis_details_update_status:
                        # current_batch_id = get_import_batch_id_from_system_id_or_device_id(system_id=system_id)
                        # logger.info(f"In revert_replenish_skipped_canister, current_batch_id: {current_batch_id}")

                        status = update_batch_change_tracker_after_replenish_skipped_canister(canister_id=canister_id,
                                                                                              user_id=user_details['id'],
                                                                                              device_id=system_device[1],
                                                                                              reverted_packs=reverted_packs)
                        logger.info(
                            f"In inventory_mark_in_stock_status, batch_change_tracker update status:{status}")

                    logger.info("In inventory_mark_in_stock_status, updating replenish-mini-batch couchdb")
            if system_device and system_device[0]:
                update_replenish_based_on_system(system_device[0])
        return create_response(SUCCESS_RESPONSE)

    except Exception as e:
        logger.error("Error in inventory_mark_in_stock_status{}".format(e))
        return error(1000, "Error in updating drug status")


@log_args_and_response
def inventory_adjust_quantity(args):
    try:

        user_id = args.get("user_id")
        ndc = args.get("ndc")
        adjusted_quantity = args.get("adjusted_quantity")
        company_id = args.get("company_id")
        case_id = args.get("case_id")
        note = args.get("reason", None)
        transaction_type = args.get("transaction_type", None)
        is_replenish = args.get("is_replenish", False)
        drug_info = get_drug_data_from_ndc([ndc])[0]
        drug_id = drug_info['drug_id']
        logger.info("drug_info: {} ".format(drug_info))
        drug_data = {}
        case_quantity_dict = args.get("case_quantity_dict", {})
        if not user_id:
            token = get_token()
            logger.debug("fetching_user_details")
            user_details = get_current_user(token=token)
        else:
            user_details = get_users_by_ids(user_id_list=str(user_id))[str(user_id)]
            user_details['company_id'] = user_details['company']
            user_details['name'] = user_details['last_name'] + ", " + user_details['first_name']

        drug_data[drug_id] = {
            'id': drug_id,
            'ndc': drug_info['ndc'],
            'formatted_ndc': drug_info['formatted_ndc'],
            'txr': drug_info['txr'],
        }
        param = {
            "final_drug_count": {drug_id: {"quantity": adjusted_quantity}},
            "ndc_list": [drug_info['ndc']],
            "drug_data": drug_data,
            "company_id": company_id,
            "transaction_type": transaction_type if transaction_type else settings.EPBM_QTY_ADJUSTMENT_KEY,
            "user_details": user_details,
            "case_id": case_id,
            "note": note,
            "is_replenish": is_replenish,
            "case_quantity_dict": case_quantity_dict
        }
        response = drug_inventory_adjustment(param)
        if response:
            return create_response(settings.SUCCESS_RESPONSE)
        else:
            return error(1000, "Error in invetory_adjust_quantity")
    except DrugInventoryValidationException as e:
        logger.error(e)
        return error(1000, e.args[0][0]['description'])
    except Exception as e:
        logger.error("Error in invetory_adjust_quantity{}".format(e))
        return error(1000, "Error in invetory_adjust_quantity")
