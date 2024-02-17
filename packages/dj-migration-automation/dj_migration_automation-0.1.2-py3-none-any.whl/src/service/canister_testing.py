import json
import os
import sys
from typing import List
from unittest import result

from peewee import InternalError, IntegrityError, DoesNotExist, DataError
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, call_webservice
from dosepack.validation.validate import validate
from src import constants
from src.api_utility import get_filters, get_orders
from src.dao.canister_dao import add_canister_status_history, validate_reserved_canisters, delete_canister_dao, \
    activate_canister_dao, db_validate_testing_status, get_canister_expiry_status, db_update_canister_order_status
from src.dao.canister_testing_dao import validate_canister_id_with_company_id, \
    get_alternate_canister_data, update_canister_testing_status_data, \
    get_alternate_canisters_by_drug_and_canister_stick, get_canister_testing_details, \
    get_canister_testing_status_by_drug, get_canister_testing_status_by_canister_stick, \
    get_location_id_from_display_location_dao, get_canister_testing_count_dao, \
    db_get_products, populate_product_details_dao, \
    db_update_product_status, db_get_empty_location, populate_old_canister_mapping_dao, \
    db_check_and_update_product_status, db_update_old_canister_mapping, db_get_old_canister, \
    db_validate_canister_and_product, update_product_delivery_date, \
    db_get_product_ids, db_get_testing_fields_dict, db_get_alternate_products, db_get_report_fields_dict, \
    db_get_alternate_fields_dict, update_canister_testing_data_in_couch_db, db_get_serial_number, \
    db_get_new_canister_id, send_canister_testing_notification, db_update_product_status_skipped, \
    db_get_max_used_ndc_from_fndc, db_check_all_canisters_tested, db_get_product_from_lot_number, \
    db_get_reserved_tested_location, db_get_old_canisters, db_get_old_canister_expiry_date, \
    get_drug_list_from_lot_numbers
from src.dao.location_dao import db_get_empty_locations_dao
from src.dao.refill_device_dao import get_available_quantity_in_canister, get_expiry_date_of_canister, \
    update_canister_master, create_canister_tracker
from src.dao.zone_dao import get_zone_id_list_by_device_id_company_id
from src.dao.drug_dao import get_drug_id_from_ndc, db_get_drug_info_by_canister, get_drug_data_from_ndc
from src.exceptions import InventoryDataNotFoundException, InventoryConnectionException
from src.model.model_drug_dimension import DrugDimension
from src.service.canister import get_canister_data_by_serial_number, _add_canister_info
from src.service.notifications import Notifications
from utils.auth_webservices import send_email_for_daily_check_api_failure
from utils.inventory_webservices import inventory_api_call

logger = settings.logger


# @log_args
# @validate(required_fields=["company_id", "device_id"])
# def get_pending_canister_testing_data(data_dict: dict) -> str:
#     """
#     This function gets list of one canister from the CSR corresponding to each unique drug in the canister master,
#     for which the canister testing is pending.
#     @param data_dict:
#     @return:
#     """
#     logger.debug("Inside get_pending_canister_testing_data")
#
#     company_id: int = int(data_dict["company_id"])
#     device_id: int = int(data_dict["device_id"])
#     device_type_csr: int = int(settings.DEVICE_TYPES["CSR"])
#     zone_id_list: List[int]
#     tested_canister_list: List[int]
#     untested_canister_data: List[dict]
#     untested_canister_dict: Dict[str: Any] = dict()
#
#     try:
#         # get the zone_id_list in which the Canister Testing Device is shared.
#         zone_id_list = get_zone_id_list_by_device_id_company_id(device_id=device_id, company_id=company_id)
#
#         # fetch the list of all the tested canister ids.
#         tested_canister_list = get_tested_canister_list()
#
#         # get data for all the untested canisters of the given company_id and same zone as the Canister Testing Device.
#         untested_canister_data = get_untested_canister_data(tested_canister_list=tested_canister_list,
#                                                             zone_id_list=zone_id_list, company_id=company_id)
#
#         # create a dictionary with ndc as key and that record of the untested_canister_data as value,
#         # as we want single data_dict for each ndc
#         for record in untested_canister_data:
#             if record["ndc"] in list(untested_canister_dict.keys()):
#                 if record["device_type_id"] == device_type_csr:
#                     untested_canister_dict[record["ndc"]] = record
#             else:
#                 untested_canister_dict[record["ndc"]] = record
#
#         return create_response(list(untested_canister_dict.values()))
#
#     except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
#         logger.error(e)
#         return error(2001)
#     except Exception as e:
#         logger.error(e)
#         return error(2001)

@log_args_and_response
def send_lot_tested_mail(lot_number):
    """
    This function sends email suggesting all the canisters in given lot have been tested
    @return:
    """
    try:
        response = db_get_product_from_lot_number(lot_number)
        response_dict = {}
        for record in response:
            if record['status_id'] == 145:
                status = "Pass"
            else:
                status = "Fail"
            response_dict[record["product_id"]] = {
                "status": status,
                "new_canister_id": record["new_canister_id"],
                "user_id": record["modified_by"],
                "reason": record["reason"]
            }
        logger.info(
            f"in send_lot_tested_mail, response_dict is {response_dict}")
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.SEND_EMAIL_FOR_LOT_TESTING_COMPLETION,
                                       parameters={"response_dict": response_dict, "lot_number": lot_number},
                                       use_ssl=settings.AUTH_SSL)
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in send_lot_tested_mail {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in send_lot_tested_mail: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1040)
    except Exception as e:
        logger.error("error in send_lot_tested_mail {}".format(e))


@log_args_and_response
@validate(required_fields=["ndc", "status_id", "user_id", "company_id", "device_id", "system_id"])
def add_canister_testing_data(data_dict: dict) -> str:
    """
    This functions inserts/update the data_dict from the Canister Testing Device.
    @param data_dict:
    @return:
    """
    logger.debug("Inside add_canister_testing_data")

    canister_id = data_dict.get("canister_id", None)
    canister_serial_number = data_dict.get("canister_serial_number", None)
    ndc: str = str(data_dict["ndc"])
    status_id: int = int(data_dict["status_id"])
    user_id: int = int(data_dict["user_id"])
    reason: str = data_dict.get("reason", None)
    company_id: int = int(data_dict["company_id"])
    device_id: int = int(data_dict["device_id"])
    deactivate_canister: int = int(data_dict.get("deactivate_canister", 1))
    system_id: int = int(data_dict.get("system_id", None))
    canisters_to_active: List[int] = list()
    canisters_to_deactive: List[int] = list()
    reason_type = "drug not compatible"
    quantity = int(data_dict.get("quantity", 0))
    transfer_location = None
    CANISTER_TESTING_COUCH_DB_NAME = "canister_testing"

    try:
        if reason == constants.CANISTER_FAIL_DUE_TO_BROKEN and canister_serial_number:
            # Update the product status
            product_status_update = {
                "canister_serial_number": canister_serial_number,
                "status": settings.PRODUCT_STATUS_BROKEN
            }
            db_update_product_status(product_status_update)

            # Get the canister testing count
            current_batch_count = get_canister_testing_count_dao()[1]

            # Update the canister testing data in CouchDB
            canister_testing_data = {"current_batch_count": current_batch_count}
            update_canister_testing_data_in_couch_db(CANISTER_TESTING_COUCH_DB_NAME, company_id, canister_testing_data)
            return create_response(constants.SUCCESS_RESPONSE)

        recommended_location = db_get_empty_locations_dao(company_id=company_id, is_mfd=False, device_id=1, quadrant=None,
                                                          device_type_id=None, system_id=system_id, drawer_number=constants.POST_TESTING_DRAWER_RECOMMENDATION)
        reserved_locations = {location for location in db_get_reserved_tested_location()}
        if status_id == constants.CANISTER_TESTING_PASS:
            for key in recommended_location:
                transfer_location = key if not reserved_locations or recommended_location[key][0][
                    'id'] not in reserved_locations else transfer_location
                if transfer_location:
                    break
            location_id = recommended_location[transfer_location][0]['id']
        else:
            last_index = 1
            while 1:
                location_id = recommended_location[list(recommended_location.keys())[-1]][-last_index]['id']
                last_index += 1
                if not reserved_locations or location_id not in reserved_locations:
                    break
        if status_id not in [constants.CANISTER_TESTING_PASS, constants.CANISTER_TESTING_FAIL]:
            return error(3015)
        if not canister_id and not canister_serial_number:
            logger.error("In add_canister_testing_data, canister_id and canister_serial_number are missing")
            return error(1001)
        if not canister_id:
            if status_id in [constants.CANISTER_TESTING_PASS] or reason_type == constants.CANISTER_FAIL_DUE_TO_NON_COMPATIBLE_DRUG:
                dict_canister_info = get_canister_data_by_serial_number(canister_serial_number=canister_serial_number,
                                                                        company_id=company_id,
                                                                        auto_register=True, skip_testing=True)
                if isinstance(dict_canister_info, str):
                    dict_canister_info = json.loads(dict_canister_info)
                    if dict_canister_info["status"] == settings.FAILURE_RESPONSE:
                        return error(4002)
                dict_canister_info["reason_type"] = reason_type
                dict_canister_info["company_id"] = company_id
                dict_canister_info["system_id"] = system_id
                dict_canister_info["user_id"] = user_id
                dict_canister_info["auto_register"] = True
                dict_canister_info["quantity"] = dict_canister_info.get("available_quantity", 0) + quantity
                if quantity > 0:
                    dict_canister_info["expiry_date"] = db_get_old_canister_expiry_date(canister_serial_number)
                registered_canister = _add_canister_info(dict_canister_info)
                canister_id = registered_canister['data']["canister_id"]
                status = db_update_old_canister_mapping(canister_id, canister_serial_number)
        # validate canister_id against company_id.
        if not validate_canister_id_with_company_id(canister_id=canister_id, company_id=company_id):
            return error(3016)

        # verify if active canister_id.
        # if not validate_active_canister_id(canister_id=canister_id):
        #     return error(3012)

        # validate ndc against canister_id
        # if not validate_ndc_by_canister_id(canister_id=canister_id, ndc=ndc):
        #     return error(3014)

        # fetch drug_id from ndc.
        drug_id_list = get_drug_id_from_ndc(ndc=ndc)
        drug_id = drug_id_list[0]

        logger.info(f"add_canister_testing_data: drug ids for ndc: {drug_id_list}")

        with db.transaction():
            if reason_type == constants.CANISTER_FAIL_DUE_TO_NON_COMPATIBLE_DRUG:
                if canister_serial_number:
                    logger.info(
                        f"updating status from pending to tested transfer pending for incompatible failure in ProductDetails",
                        data_dict["canister_serial_number"])
                    update_dict_status = {
                        "canister_serial_number": canister_serial_number,
                        "location": location_id,
                        "status": settings.PRODUCT_STATUS_TRANSFER_PENDING
                    }
                    status = db_update_product_status(update_dict_status)

            # zone_id_list = get_zone_id_list_by_device_id_company_id(device_id=device_id, company_id=company_id)

            # preparing the data dict for insertion in the Canister Testing Status table.

            update_dict = {"status_id": status_id,
                           "reason": reason,
                           "created_by": user_id,
                           "created_date": get_current_date_time(),
                           "modified_by": user_id,
                           "modified_date": get_current_date_time(),
                           }
            create_dict = {}

            if status_id == constants.CANISTER_TESTING_PASS:

                # canister_drug_data = db_get_drug_info_by_canister(canister_id=canister_id)
                # canister_stick_id = canister_drug_data["canister_stick_id"]
                # fndc_txr = canister_drug_data["fndc_txr"]
                # get the list of alternate canisters for the given ndc
                # alternate_canister_list = get_alternate_canisters_by_drug_and_canister_stick(
                #     canister_stick_id=canister_stick_id,
                #     fndc_txr=fndc_txr,
                #     zone_id_list=zone_id_list)
                #
                # # logger.debug(f"add_canister_testing_data: alternate_canister_list: {alternate_canister_list}")
                #
                # canister_testing_details = get_canister_testing_status_by_drug(canister_ids=alternate_canister_list,
                #                                                                drug_ids=drug_id_list)
                #
                # logger.info(f"add_canister_testing_data: canister_testing_details: {canister_testing_details}")

                # for canister in alternate_canister_list:
                #     create_dict["canister_id"] = canister
                #
                #     if canister == canister_id:
                #         update_dict["tested"] = 1
                #     else:
                #         update_dict["tested"] = 0
                #
                #     if canister in canister_testing_details:
                #         create_dict["drug_id"] = canister_testing_details[canister]["drug_id"]
                #     else:
                #         create_dict["drug_id"] = drug_id
                #     if canister_serial_number:
                #         old_canisters = db_get_old_canisters(canister_serial_number)
                #     if status_id == constants.CANISTER_TESTING_PASS:
                #         if canister not in old_canisters:
                canisters_to_active.append(canister_id)
                if canister_serial_number:
                    create_dict = {"drug_id": drug_id,
                                   "canister_id": canister_id,
                                   "status_id": status_id,
                                   "reason": reason,
                                   "created_by": user_id,
                                   "created_date": get_current_date_time(),
                                   "modified_by": user_id,
                                   "modified_date": get_current_date_time(),
                                   "tested": 1
                                   }
                update_dict_status = {
                    "canister_serial_number": canister_serial_number,
                    "location": location_id,
                    "status": settings.PRODUCT_STATUS_TRANSFER_PENDING
                }
                db_update_product_status(update_dict_status)
                # update Canister Testing Status table.
                update_canister_testing_status_data(create_dict=create_dict, update_dict=update_dict)
            else:
                create_dict = {"drug_id": drug_id, "canister_id": canister_id}
                update_dict["tested"] = 1

                canister_testing_details = get_canister_testing_status_by_drug(canister_ids=[canister_id],
                                                                               drug_ids=drug_id_list)

                if canister_id in canister_testing_details:
                    create_dict["drug_id"] = canister_testing_details[canister_id]["drug_id"]

                canisters_to_deactive.append(canister_id)

                # update Canister Testing Status table.
                update_canister_testing_status_data(create_dict=create_dict, update_dict=update_dict)

            logger.info(f"add_canister_testing_data: canisters_to_active: {canisters_to_active}")
            for canister in canisters_to_active:
                # To update canister active status in CanisterMaster table
                canister_drug_data = db_get_drug_info_by_canister(canister_id=canister)
                rfid = canister_drug_data["rfid"]
                update_canister_active_status = {"canister_id": canister,
                                                 "company_id": company_id,
                                                 "user_id": user_id,
                                                 "rfid": rfid,
                                                 "update_location": False}
                status = activate_canister(update_canister_active_status)

            if deactivate_canister:
                logger.info(f"add_canister_testing_data: canisters_to_deactive: {canisters_to_deactive}")
                for canister in canisters_to_deactive:
                    # To update canister active status in CanisterMaster table
                    if not reason:
                        reason = "canister_testing_failed"
                    update_canister_active_status = {"canister_id": canister,
                                                     "company_id": company_id,
                                                     "user_id": user_id,
                                                     "comment": reason,
                                                     "update_location": False}
                    status = delete_canister(update_canister_active_status)
            count = get_canister_testing_count_dao()[1]
            canister_testing_data = {"current_batch_count": count}
            status = update_canister_testing_data_in_couch_db(CANISTER_TESTING_COUCH_DB_NAME, company_id, canister_testing_data)
        if canister_serial_number:
            # sending mail if all canisters in this lot are tested
            un_tested_count, lot_number = db_check_all_canisters_tested(canister_serial_number)
            if un_tested_count == 0:
                status = send_lot_tested_mail(lot_number)
            response = {
                "canister_id": canister_id
            }
            return create_response(response)
        return create_response(constants.SUCCESS_RESPONSE)

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in add_canister_testing_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in add_canister_testing_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in add_canister_testing_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in add_canister_testing_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in add_canister_testing_data: " + str(e))


@log_args_and_response
def get_canister_testing_data(data_dict: dict) -> str:
    """
    This functions gets the list of canister data with its testing details.
    @param data_dict:
    @return:
    """
    logger.debug("Inside get_canister_testing_data.")

    company_id: int = int(data_dict["company_id"])
    device_id: int = int(data_dict["device_id"])
    paginate = data_dict["paginate"]
    zone_id_list: List[int]
    canister_testing_data: List[dict]
    filter_fields = data_dict.get("filter_fields", None)
    sort_fields = data_dict.get("sort_fields", None)
    order_list = []

    try:
        like_search_list = []
        membership_search_list = []
        exact_search_fields = []
        if filter_fields.get("canister_id", None):
            like_search_list.append("canister_id")
        if filter_fields.get("ndc", None):
            like_search_list.append("ndc")
        if filter_fields.get("drug_name", None):
            like_search_list.append("drug_name")
        if filter_fields.get("tested_by", None):
            membership_search_list.append("tested_by")
        if filter_fields.get("status", None):
            if filter_fields.get("status") == constants.CANISTER_TESTING_PENDING:
                filter_fields['status'] = None
            exact_search_fields.append("status")
        fields_dict = db_get_report_fields_dict()
        clauses = get_filters(clauses=[], fields_dict=fields_dict, filter_dict=filter_fields,
                              membership_search_fields=membership_search_list,
                              like_search_fields=like_search_list,
                              exact_search_fields=exact_search_fields)
        if sort_fields:
            order_list = get_orders(order_list, fields_dict, sort_fields)
        # get the zone_id_list in which the Canister Testing Device is shared.
        zone_id_list = get_zone_id_list_by_device_id_company_id(device_id=device_id, company_id=company_id)

        canister_testing_data = get_canister_testing_details(clauses, zone_id_list=zone_id_list, company_id=company_id,
                                                             order_list=order_list)
        if isinstance(paginate, str):
            paginate = json.loads(paginate)
        start_index = (paginate["page_number"] - 1) * paginate["number_of_rows"]
        end_index = start_index + paginate["number_of_rows"]
        paginated_response = canister_testing_data[start_index:end_index]
        response_data = {
            "history": paginated_response,
            "total_count":  len(canister_testing_data)
        }
        return create_response(response_data)

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_canister_testing_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_canister_testing_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_canister_testing_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_canister_testing_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_canister_testing_data: " + str(e))


@log_args_and_response
def get_alternate_canister_testing_data(data_dict: dict) -> str:
    """
    This function gets the list of alternate canister data for given canister id
    @param data_dict:
    @return:
    """

    company_id: int = int(data_dict["company_id"])
    device_id: int = int(data_dict["device_id"])
    canister_id = (data_dict.get("canister_id", None))
    zone_id_list: List[int]
    source_drawer_dict: dict
    other_canisters_available = False
    rfid = data_dict.get("rfid")
    filter_fields = data_dict.get("filter_fields", None)
    clauses = []

    try:
        if canister_id:
            # get the zone_id_list in which the Canister Testing Device is shared.
            zone_id_list = get_zone_id_list_by_device_id_company_id(device_id=device_id, company_id=company_id)

            canister_drug_data = db_get_drug_info_by_canister(canister_id=canister_id)
            fndc_txr = str(canister_drug_data["fndc_txr"])
            canister_stick_id = canister_drug_data["canister_stick_id"]

            total_sticks, tested_sticks = get_canister_testing_status_by_canister_stick(fndc_txr=fndc_txr,
                                                                                        zone_id_list=zone_id_list)

            logger.info(
                f" get_alternate_canister_testing_data: total sticks: {total_sticks} and tested sticks: {tested_sticks}")

            # get data for all the alternate canisters of the given company_id and same zone.
            alternate_canister_data, source_drawer_dict = get_alternate_canister_data(canister_stick_id=canister_stick_id,
                                                                                      fndc_txr=fndc_txr,
                                                                                      zone_id_list=zone_id_list,
                                                                                      company_id=company_id,
                                                                                      current_canister_id=canister_id)

            if int(len(set(total_sticks) - set(tested_sticks))) >= 1:
                other_canisters_available = True

            response = {"other_canisters_available": other_canisters_available,
                        "canister_data": alternate_canister_data,
                        "drawers_to_unlock": list(source_drawer_dict.values())}
        else:
            if filter_fields:
                like_search_list = []
                if filter_fields.get("product_id", None):
                    like_search_list.append("product_id")
                if filter_fields.get("lot_number", None):
                    like_search_list.append("lot_number")
                fields_dict = db_get_alternate_fields_dict()
                clauses = get_filters(clauses=[], fields_dict=fields_dict, filter_dict=filter_fields,
                                      like_search_fields=like_search_list)
            other_canisters_available, alternate_product_data = db_get_alternate_products(rfid, clauses)

            response = {"other_canisters_available": other_canisters_available,
                        "canister_data": alternate_product_data,
                        "drawers_to_unlock": []}

        return create_response(response)

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_alternate_canister_testing_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_alternate_canister_testing_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_alternate_canister_testing_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_alternate_canister_testing_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_alternate_canister_testing_data: " + str(e))


@log_args_and_response
@validate(required_fields=["status_id", "user_id", "company_id"])
def update_alternate_canister_testing_status_data(data_dict: dict) -> str:
    """
    This function is update testing status of given alternate canister list
    @param data_dict:
    @return:
    """

    company_id: int = int(data_dict["company_id"])
    user_id: int = int(data_dict["user_id"])
    tested_canister_id = data_dict.get("tested_canister_id", None)
    ndc: str = str(data_dict["ndc"])
    canister_ids: List[int] = data_dict.get("canister_ids", [])
    status_id: int = int(data_dict["status_id"])
    tested_product_id: List[int] = data_dict.get("tested_product_id", None)
    product_ids: List[int] = data_dict.get("product_ids", None)
    system_id = data_dict.get("system_id", None)
    location_id = None

    try:
        recommended_location = db_get_empty_locations_dao(company_id=company_id, is_mfd=False, device_id=1, quadrant=None,
                                                          device_type_id=None, system_id=system_id,
                                                          drawer_number=constants.POST_TESTING_DRAWER_RECOMMENDATION)
        if tested_product_id and product_ids:
            tested_canister_id = db_get_new_canister_id(tested_product_id)
            for product_id in product_ids:
                i = 1
                reserved_locations = list(set(db_get_reserved_tested_location()))
                while 1:
                    location_id = recommended_location[list(recommended_location.keys())[-1]][-i]['id']
                    i += 1
                    if not reserved_locations or location_id not in reserved_locations:
                        break
                canister_serial_number = db_get_serial_number(product_id)
                dict_canister_info = get_canister_data_by_serial_number(canister_serial_number, company_id=company_id, skip_testing=True, auto_register=True)
                if isinstance(dict_canister_info, str):
                    dict_canister_info = json.loads(dict_canister_info)
                    if dict_canister_info["status"] == settings.FAILURE_RESPONSE:
                        return error(4002)
                dict_canister_info["company_id"] = company_id
                dict_canister_info["system_id"] = system_id
                dict_canister_info["user_id"] = user_id
                dict_canister_info["auto_register"] = True
                dict_canister_info["reason_type"] = constants.CANISTER_FAIL_DUE_TO_NON_COMPATIBLE_DRUG
                registered_canister = _add_canister_info(dict_canister_info)
                canister_id = registered_canister["data"]["canister_id"]
                canister_ids.append(canister_id)
                logger.info(
                    f"updating status from pending to tested transfer pending for incompatible failure in ProductDetails",
                    product_id)
                update_dict_status = {
                    "product_id": product_id,
                    "location": location_id,
                    "status": settings.PRODUCT_STATUS_TRANSFER_PENDING
                }
                status = db_update_product_status(update_dict_status)
        # fetch drug_id from ndc.
        drug_ids = get_drug_id_from_ndc(ndc=ndc)
        logger.info(f"update_alternate_canister_testing_status_data: drug ids for ndc: {drug_ids}")

        canister_ids.append(tested_canister_id)
        canister_testing_details = get_canister_testing_status_by_drug(canister_ids=canister_ids,
                                                                       drug_ids=drug_ids)

        canister_ids.remove(tested_canister_id)

        reason = canister_testing_details[tested_canister_id]["reason"]
        drug_id = canister_testing_details[tested_canister_id]["drug_id"]

        logger.info(
            f"update_alternate_canister_testing_status_data: canister_testing_details: {canister_testing_details}")

        with db.transaction():

            update_dict = {"status_id": status_id,
                           "reason": reason,
                           "tested": 0,
                           "created_by": user_id,
                           "created_date": get_current_date_time(),
                           "modified_by": user_id,
                           "modified_date": get_current_date_time(),
                           }

            for canister in canister_ids:

                create_dict = {"drug_id": drug_id, "canister_id": canister}

                if canister in canister_testing_details:
                    create_dict = {"drug_id": canister_testing_details[canister].drug_id}

                # update Canister Testing Status table.
                update_canister_testing_status_data(create_dict=create_dict, update_dict=update_dict)

                canister_drug_data = db_get_drug_info_by_canister(canister_id=canister)
                rfid = canister_drug_data["rfid"]
                update_canister_active_status = {"canister_id": canister,
                                                 "company_id": company_id,
                                                 "user_id": user_id,
                                                 "rfid": rfid,
                                                 "update_location": False}

                if status_id == constants.CANISTER_TESTING_PASS:
                    activate_canister(update_canister_active_status)

                if status_id == constants.CANISTER_TESTING_FAIL:
                    update_canister_active_status["comment"] = reason
                    delete_canister(update_canister_active_status)

        return create_response(constants.SUCCESS_RESPONSE)

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in update_alternate_canister_testing_status_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in update_alternate_canister_testing_status_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_alternate_canister_testing_status_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in update_alternate_canister_testing_status_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_alternate_canister_testing_status_data: " + str(e))


@log_args_and_response
@validate(required_fields=["rfid", "canister_id", "user_id"],
          validate_canister_id=['canister_id'])
def activate_canister(dict_canister_info):
    """ activate the canister with the given rfid.
        It sets location of the canister to given location_id and active=True.

        Args:
            dict_canister_info (dict): The key containing the canister id

        Returns:
           json: success or the failure response along with the id of the canister activated.

        Examples:
            >>> activate_canister({"canister_id":5,"company_id":3,"user_id":5 , "drug_id":2334,
                            "display_location":"A1-5","device_id":2,"rfid":"44006313EDD9"})
                {"status": "success", "data": 1}
    """
    # get the value canister_id from input dict
    canister_id = dict_canister_info["canister_id"]
    rfid = dict_canister_info["rfid"]
    company_id = dict_canister_info.get("company_id", None)
    user_id = dict_canister_info.get("user_id", None)
    update_location = dict_canister_info.get("update_location", True)
    auto_register = dict_canister_info.get("auto_register", None)

    try:

        if canister_id is not None and company_id is not None:
            valid_canister = validate_canister_id_with_company_id(canister_id=canister_id, company_id=company_id)
            if not valid_canister:
                return error(1018)

        device_id = dict_canister_info.get("device_id", None)
        location_id = None

        if device_id is not None and dict_canister_info.get("display_location", None) is not None:
            location_id, is_disable = get_location_id_from_display_location_dao(device_id=device_id,
                                                                                display_location=dict_canister_info[
                                                                                    "display_location"])

        with db.transaction():
            status = activate_canister_dao(user_id=user_id, location_id=location_id, rfid=rfid,
                                           update_location=update_location)

            # populate data in canister history tables
            # data_dict = {
            #     "canister_id": canister_id,
            #     "previous_location_id": None,
            #     "current_location_id": location_id,
            #     "created_by": user_id,
            #     "modified_by": user_id
            # }
            # canister_history = add_canister_history(data_dict=data_dict)

            status_data_dict = {"canister_id": canister_id,
                                "action": constants.CODE_MASTER_CANISTER_REACTIVATE,
                                "created_by": user_id,
                                "created_date": get_current_date_time()
                                }
            canister_status_history = add_canister_status_history(data_dict=status_data_dict)
            logger.info("In activate_canister: Data added in canister status history {}"
                        .format(canister_status_history.id))
            return create_response(status)

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in activate_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in activate_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in activate_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in activate_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in activate_canister: " + str(e))


@log_args_and_response
@validate(required_fields=["canister_id", "company_id", "user_id", "comment"], validate_canister_id=['canister_id'])
def delete_canister(dict_canister_info):
    """ deactivate the canister with the given canister id.
        It sets the location of the canister to -1(deleted).

        Args:
            dict_canister_info (dict): The key containing the canister id

        Returns:
           json: success or the failure response along with the id of the canister deleted.

        Examples:
            >>> delete_canister({"canister_id": 1, "company_id": 2, "device_id": 2)
                {"status": "success", "data": 1}
    """
    # get the value canister_id from input dict
    canister_id = dict_canister_info["canister_id"]
    company_id = int(dict_canister_info["company_id"])
    check_for_reserved_canister = dict_canister_info.get("check_reserve", False)

    try:
        valid_canister = validate_canister_id_with_company_id(canister_id=canister_id, company_id=company_id)
        if not valid_canister:
            return error(1018)

        if check_for_reserved_canister:
            validate_reserved_canister = validate_reserved_canisters(canister_list=[canister_id])
            if not validate_reserved_canister:
                return error(1042)

        status = delete_canister_dao(dict_canister_info=dict_canister_info)
        return create_response(status)

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in delete_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in delete_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in delete_canister: " + str(e))


@log_args_and_response
@validate(required_fields=["canister_ids", "company_id", "user_id", "comment"])
def delete_multiple_canister(dict_canister_info):
    """ deactivate the canister with the given canister id.
        It sets the location of the canister to -1(deleted).

        Args:
            dict_canister_info (dict): The key containing the canister id

        Returns:
           json: success or the failure response along with the id of the canister deleted.

        Examples:
            >>> delete_canister({"canister_id": 1, "company_id": 2, "device_id": 2)
                {"status": "success", "data": 1}
    """
    try:
        final_status = list()
        dict_single_canister_info = dict()
        status1 = dict()
        canister_id_list = dict_canister_info["canister_ids"].split(",")
        for canister_id in canister_id_list:
            dict_single_canister_info["canister_id"] = canister_id
            dict_single_canister_info["company_id"] = int(dict_canister_info["company_id"])
            dict_single_canister_info["user_id"] = dict_canister_info["user_id"]
            dict_single_canister_info["comment"] = dict_canister_info["comment"]
            dict_single_canister_info["check_reserve"] = dict_canister_info.get("check_reserve", False)
            status = delete_canister(dict_single_canister_info)
            status = json.loads(status)
            status1["canister_id"] = canister_id
            if "data" in status:
                if status["data"] == 1:
                    status1["status"] = "success"
                else:
                    status1["status"] = "failure"
            elif "code" in status:
                status1["code"] = status["code"]
                status1["description"] = status["description"]
                status1["status"] = status["status"]
            final_status.append(status1.copy())
        return create_response(final_status)

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in delete_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in delete_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in delete_canister: " + str(e))


@log_args_and_response
def get_canister_for_testing(paginate, filter_fields=None):
    """
    This functions gets the canister to be tested, received from odoo
    @return:
    """
    like_search_list = []
    membership_search_list = []
    exact_search_fields = []
    if filter_fields.get("product_id", None):
        like_search_list.append("product_id")
    if filter_fields.get("drug_name", None):
        like_search_list.append("drug_name")
    if filter_fields.get("lot_number", None):
        membership_search_list.append("lot_number")
    if filter_fields.get("status", None):
        exact_search_fields.append("status")
    fields_dict = db_get_testing_fields_dict()

    if isinstance(paginate, str):
        paginate = json.loads(paginate)
    try:
        logger.debug("Inside get_canister_testing_data.")
        db_data = get_canister_testing_count_dao()
        response_dict = {}
        result_dict = {}
        current_batch_count = 0
        all_canisters = db_get_product_ids()
        for record in all_canisters:
            status = db_check_and_update_product_status(product_id=record['product_id'])
        clauses = get_filters(clauses=[], fields_dict=fields_dict, filter_dict=filter_fields, membership_search_fields=membership_search_list,
                              like_search_fields=like_search_list, exact_search_fields=exact_search_fields)
        for record in db_get_products(clauses):
            product_id = record['product_id']
            if product_id in db_data[2]:
                current_batch = True
                current_batch_count += 1
            else:
                current_batch = False
            response_dict[product_id] = {
                    "rfid": record['rfid'],
                    "lot_number": record['lot_number'],
                    "drug_name": record['drug_name'],
                    "image_name": record['image_name'],
                    "color": record['color'],
                    "shape": record['shape'],
                    "imprint": record['imprint'],
                    "delivery_date": record['delivery_date'],
                    "current_batch": current_batch,
                    "status": record['status'],
                    "serial_number": record['csr_serial_number'],
                    "display_location": record['display_location'],
                    "drawer_number": record['drawer_name'],
                    "shelf": record['shelf'],
                    "device_type_id": record['device_type_id'],
                    "ip_address": record['ip_address'],
                    "secondary_ip_address": record['secondary_ip_address'],
                    "device_name": record["device_name"],
                    "device_type_name": record["device_type"][0:3] if record.get("device_type") else None,
                    "canister_id": record["new_canister_id"]
                }
        logger.info(f"in get_canister_for_testing, response_dict is {response_dict}")
        sorted_dict = dict(sorted(response_dict.items(), key=lambda item: item[1]["status"], reverse=False))
        sorted_dict = dict(sorted(sorted_dict.items(), key=lambda item: item[1]["current_batch"], reverse=True))
        start_index = (paginate["page_number"] - 1) * paginate["number_of_rows"]
        end_index = start_index + paginate["number_of_rows"]
        paginated_dict = {}
        for index, key in enumerate(sorted_dict.keys()):
            if start_index <= index < end_index:
                paginated_dict[key] = sorted_dict[key]
        result_dict["product_details"] = paginated_dict
        result_dict["total_count"] = len(sorted_dict.keys())
        result_dict["lot_numbers"] = db_data[4]
        result_dict["current_batch_count"] = current_batch_count
        if db_data[4]:
            result_dict["status"] = settings.ALL_PRODUCT_STATUS
        else:
            result_dict["status"] = []
        return create_response(result_dict)
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_canister_for_testing {}".format(e))
    except Exception as e:
        logger.error("error in get_canister_for_testing {}".format(e))


@log_args_and_response
def save_canisters_in_product_details(company_id, time_zone):
    """
    This function inserts details received from odoo for canister products which are shipped
    @return:
    """
    ndc_list = []
    try:
        logger.debug("Inside save_canisters_in_product_details.")
        received_response = inventory_api_call(api_name=settings.STORE_SHIPPED_CANISTERS, data={"customer_id": company_id}, request_type="GET")
        if not isinstance(received_response, list) or not received_response:
            send_email_for_daily_check_api_failure(company_id=company_id, time_zone=time_zone,
                                                   error_details=error(4005),
                                                   api_name=constants.DAILY_SHIPPED_CANISTERS_CHECK)
            return error(4005)
        create_data = []
        for data_dict in received_response:
            for key, record in data_dict.items():
                lot_number = key
                for lot_record in record:
                    product_id: int = int(lot_record.get("product_id", None))
                    ndc_txr: str = str(lot_record.get("ndc_txr_id", None))
                    formatted_ndc = ndc_txr.split("##")[0]
                    ndc = db_get_max_used_ndc_from_fndc(formatted_ndc)
                    if not ndc:
                        return error(9017)
                    rfid: str = str(lot_record.get("rfid", None))
                    barcode = str(lot_record.get("canister_serial_number", None))
                    canister_serial_number = barcode.split("/")
                    canister_serial_number = canister_serial_number[0] + canister_serial_number[-2] + canister_serial_number[-1]
                    development_needed = data_dict.get("development_needed", False)

                    if not product_id or not ndc or not lot_number or not rfid or not canister_serial_number:
                        return error(1002)
                    create_dict = {"product_id": product_id,
                                   "ndc": ndc,
                                   "lot_number": lot_number,
                                   "rfid": rfid,
                                   "created_date": get_current_date_time(),
                                   "modified_date": get_current_date_time(),
                                   "canister_serial_number": canister_serial_number,
                                   "development_needed": development_needed
                                   }
                    ndc_list.append(ndc)
                    create_data.append(create_dict)
        if create_data:
            status = populate_product_details_dao(create_data)
        if ndc_list:
            drug_data = get_drug_data_from_ndc(ndc_list)
            drug_ids = [record['drug_id'] for record in drug_data]
            status = db_update_canister_order_status(drug_ids, constants.SHIPPED_ORDER)
        return create_response(constants.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError, DataError) as e:
        send_email_for_daily_check_api_failure(api_name=constants.DAILY_SHIPPED_CANISTERS_CHECK, company_id=company_id, time_zone=time_zone,
                                               error_details=error(2001))
        logger.error("error in save_canisters_in_product_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in save_canisters_in_product_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1040)
    except InventoryDataNotFoundException as e:
        logger.warning("in save_canisters_in_product_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"in save_canisters_in_product_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(4002)
    except InventoryConnectionException as e:
        send_email_for_daily_check_api_failure(api_name=constants.DAILY_SHIPPED_CANISTERS_CHECK, company_id=company_id,
                                               time_zone=time_zone,
                                               error_details="Connection to odoo Failed")
        logger.error("error in save_canisters_in_product_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in save_canisters_in_product_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(4002)
    except Exception as e:
        send_email_for_daily_check_api_failure(company_id=company_id, time_zone=time_zone,
                                               error_details=error(2001),
                                               api_name=constants.DAILY_SHIPPED_CANISTERS_CHECK)
        logger.error("error in save_canisters_in_product_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in save_canisters_in_product_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return create_response(e)


@log_args_and_response
@validate(required_fields=["mapping_dict"])
def save_old_canister_mapping(data_dict: dict):
    """
    This function inserts records for old canister mapping in OldCanisterMapping table
    @param data_dict:
    @return:
    """
    try:
        logger.debug("Inside save_old_canister_mapping.")
        mapping_dict = data_dict.get("mapping_dict")
        user_id = data_dict.get("user_id", None)
        create_data = []
        canister_list = []
        product_list = []
        for key, value in mapping_dict.items():
            old_canister_ids = mapping_dict[key].split(",")
            for old_canister_id in old_canister_ids:
                canister_list.append(old_canister_id)
                product_list.append(key)
                create_dict = {"product_id": int(key),
                               "old_canister_id": int(old_canister_id),
                               "created_by": user_id,
                               "created_date": get_current_date_time(),
                               "modified_date": get_current_date_time(),
                               }
                create_data.append(create_dict)
        status = db_validate_canister_and_product(canister_list, product_list)
        if status:
            status = populate_old_canister_mapping_dao(create_data)
            return create_response(constants.SUCCESS_RESPONSE)
        else:
            return error(21007)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in save_old_canister_mapping {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in save_old_canister_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1040)
    except Exception as e:
        logger.error("error in save_old_canister_mapping {}".format(e))


# @validate(required_fields=["lot_number", "company_id"])
@log_args_and_response
def update_delivered_canisters(company_id, time_zone):
    """
    This function updates delivery date of delivered canisters
    @return:
    """
    try:
        logger.debug("Inside update_delivered_canisters.")
        received_response = inventory_api_call(api_name=settings.UPDATE_DELIVERED_CANISTERS, data={"customer_id": company_id}, request_type="GET")
        # received_response = [{'lot_number': ['PACK0000201'], 'company_id': 3}]
        if not isinstance(received_response, list) or not received_response:
            send_email_for_daily_check_api_failure(company_id=company_id, time_zone=time_zone,
                                                   error_details=error(4005),
                                                   api_name=constants.DAILY_DELIVERED_CANISTERS_CHECK)
            return error(4005)
        lot_numbers_list = []
        for data_dict in received_response:
            delivered_lots = data_dict.get("lot_number", None)
            for delivered_lot in delivered_lots:
                status = update_product_delivery_date(delivered_lot)
                lot_numbers_list.append(delivered_lot)

        drug_data = get_drug_list_from_lot_numbers(lot_numbers_list)
        drug_list = [record["drug_id"] for record in drug_data]
        if drug_list:
            status = db_update_canister_order_status(drug_list, constants.DELIVERED_ORDER)

            # return create_response(send_canister_testing_notification(company_id))
        count = get_canister_testing_count_dao()
        canister_testing_data = {"current_batch_count": count[1]}
        status = update_canister_testing_data_in_couch_db("canister_testing", company_id, canister_testing_data)
        return create_response(settings.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_delivered_canisters {}".format(e))
        send_email_for_daily_check_api_failure(company_id=company_id, time_zone=time_zone,
                                               error_details=error(2001),
                                               api_name=constants.DAILY_DELIVERED_CANISTERS_CHECK)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in update_delivered_canisters: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1040)
    except InventoryDataNotFoundException as e:
        logger.warning("in update_delivered_canisters {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"in update_delivered_canisters: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(4002)
    except Exception as e:
        logger.error("error in update_delivered_canisters {}".format(e))
        send_email_for_daily_check_api_failure(company_id=company_id, time_zone=time_zone,
                                               error_details=e,
                                               api_name=constants.DAILY_DELIVERED_CANISTERS_CHECK)
        return create_response(e)


@log_args_and_response
def get_current_batch_canisters():
    """
    This functions gets the current batch canisters to test, received from odoo
    @return:
    """
    try:
        logger.debug("Inside get_current_batch_canisters.")
        data = get_canister_testing_count_dao()
        return create_response(data[3])
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_current_batch_canisters {}".format(e))
    except Exception as e:
        logger.error("error in get_current_batch_canisters {}".format(e))


@log_args_and_response
@validate(required_fields=["canister_id", "user_id"])
def update_canister_testing_quantity(args):
    """
    This functions updates old and new canister quantity as per argument
    @return:
    """
    device_id = args.get("device_id", None)
    canister_id = args.get("canister_id")
    drug_id = args.get("drug_id", None)
    user_id = args.get("user_id")
    lot_number = args.get("lot_number", None)
    available_quantity = args.get("available_quantity", None)
    expiration_date = args.get("expiration_date", None)
    drug_scan_type_id = args.get("drug_scan_type", constants.USER_ENTERED)
    replenish_mode_id = args.get("replenishment_mode", constants.MANUAL_CODE)

    try:
        logger.debug("Inside update_canister_testing_quantity.")

        if available_quantity is None:
            available_quantity = 0
        quantity_adjusted = available_quantity * (-1)

        canister_tracker_create_dict = {
            "canister_id": canister_id,
            "device_id": device_id,
            "drug_id": drug_id,
            "qty_update_type_id": constants.CANISTER_QUANTITY_UPDATE_TYPE_DISCARD,
            "original_quantity": available_quantity,
            "quantity_adjusted": quantity_adjusted,
            "lot_number": lot_number,
            "expiration_date": expiration_date,
            "drug_scan_type_id": drug_scan_type_id,
            "replenish_mode_id": replenish_mode_id,
            "created_date": get_current_date_time(),
            "created_by": user_id,
            "usage_consideration": constants.USAGE_CONSIDERATION_DISCARD
        }
        update_canister_dict = {
            "available_quantity": 0,
            "modified_by": user_id,
            "modified_date": get_current_date_time()
        }
        logger.debug("In update_canister_quantity, updating canister quantity in canister master: " + str(
            update_canister_dict))
        # update drug quantity in canister master
        canister_update_status = update_canister_master(update_dict=update_canister_dict, id=canister_id)
        logger.debug("In update_canister_quantity, Updating refilled canister data in canister tracker: " + str(
            canister_tracker_create_dict))
        # add record in canister tracker
        record = create_canister_tracker(create_dict=canister_tracker_create_dict)
        return create_response(settings.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in update_canister_testing_quantity {}".format(e))
    except Exception as e:
        logger.error("error in update_canister_testing_quantity {}".format(e))


@log_args_and_response
@validate(required_fields=["lot_numbers", "company_id"])
def skip_canister_testing(args):
    """
    This function updates testing status as skipped
    @return:
    """
    lot_numbers = args.get("lot_numbers")
    company_id = args.get("company_id")
    try:
        logger.debug("Inside skip_canister_testing.")
        status = db_update_product_status_skipped(lot_numbers)
        count = get_canister_testing_count_dao()
        canister_testing_data = {"current_batch_count": count[1]}
        status = update_canister_testing_data_in_couch_db("canister_testing", company_id, canister_testing_data)
        return create_response(settings.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in skip_canister_testing {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in skip_canister_testing: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1040)
    except Exception as e:
        logger.error("error in skip_canister_testing {}".format(e))
