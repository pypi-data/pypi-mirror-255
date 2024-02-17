import copy
import datetime
import functools
import operator
from typing import Dict, Any

from peewee import fn

import settings
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import log_args_and_response, logger, SCAN_ENTITY_DICT, get_current_date_time, \
    SCAN_TYPE_COMPATIBILITY
from src import constants
from src.exceptions import APIFailureException, TokenFetchException, DrugInventoryValidationException, \
    DrugInventoryInternalException, DrugFetchFailedException
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_master import DrugMaster
from src.model.model_unique_drug import UniqueDrug
from src.service.misc import get_token
from sync_drug_data.update_drug_data import get_missing_drug_data
from utils.drug_inventory_webservices import drug_inventory_api_call, get_data_by_ndc_from_drug_inventory, \
    get_current_inventory_data

logger = settings.logger


@log_args_and_response
def get_drug_data_by_bottle(param):
    """
    This function fetches the drug data for the given NDC from Drug Inventory.
    """
    status: bool
    inventory_resp: Dict[str, Any]
    try:
        status, inventory_resp = drug_inventory_api_call(api_name=settings.DRUG_INVENTORY_GET_NDC_DATA,
                                                         parameters=param, request_type="POST")
        if not status:
            raise APIFailureException(inventory_resp)
        if inventory_resp:
            return inventory_resp[0]
        else:
            return None

    except APIFailureException as e:
        logger.error(e)
        raise e
    except TokenFetchException as e:
        logger.error(e)
        raise e
    except DrugInventoryValidationException as e:
        logger.error(e)
        raise e
    except DrugInventoryInternalException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise DrugInventoryInternalException(e)


@log_args_and_response
def find_required_dict_from_entity(scanned_value, entity=SCAN_ENTITY_DICT["data_matrix"],
                                   required_entity="serial_number"):
    """

    :param scanned_value:
    :param entity:
    :param required_entity:
    :return:
    """
    response_dict = {"ndc": None, "expiry_date": None, "lot_number": None, "serial_number": None}

    if len(scanned_value) in [11, 9] and not scanned_value.startswith(constants.CASE_ID_PREFIX) and not scanned_value.startswith(constants.ITEM_ID_PREFIX)\
            and not entity == SCAN_ENTITY_DICT["UPC"]:
        return {}, entity

    if entity == SCAN_ENTITY_DICT["user_entered"]:
        if required_entity == "ndc":
            response_dict["ndc"] = scanned_value

        else:
            if scanned_value[0] == "#":
                scanned_value = scanned_value[1:]

            scanned_value = scanned_value.zfill(17)
            scanned_value = "#DP" + scanned_value

            response_dict["serial_number"] = scanned_value

    elif entity == SCAN_ENTITY_DICT["UPC"]:
        drug_details = get_drug_data_from_upc_list([scanned_value])
        response_dict["ndc"] = drug_details[0]["ndc"]
        entity = SCAN_ENTITY_DICT['UPC']

    elif entity == SCAN_ENTITY_DICT["barcode"]:
        if required_entity == "ndc":
            drug_details = get_drug_data_from_upc_list([scanned_value])
            if drug_details[0].get("ndc"):
                response_dict["ndc"] = drug_details[0]["ndc"]
            elif drug_details[0].get("upc"):
                response_dict["upc"] = drug_details[0]["upc"]
            entity = SCAN_ENTITY_DICT['UPC']
        if not response_dict:
            response_dict["ndc"] = find_ndc_from_barcode(scanned_value)

    elif entity == SCAN_ENTITY_DICT["data_matrix"]:
        status, ndc, lot_number, expiry_date, serial_number = find_drug_data_from_static_matrix(
            matrix_data=scanned_value)
        response_dict["ndc"] = ndc
        logger.info("Formatting expiry_date: " + str(expiry_date))
        response_dict["expiry_date"] = str(expiry_date[2:4]) + '-' + str(datetime.date.today().year)[0:2] + \
                                       str(expiry_date[0:2]) if expiry_date else expiry_date
        response_dict["lot_number"] = lot_number.strip() if lot_number else lot_number
        response_dict["serial_number"] = serial_number
        response_dict["status"] = status
    elif entity == SCAN_ENTITY_DICT['QR'] or entity == SCAN_ENTITY_DICT["vial_QR"]:
        param = {
            "caseId": scanned_value
        }
        response_from_elite = get_drug_data_by_bottle(param)
        response_dict["ndc"] = str(response_from_elite['ndc'])
        expiry_date = response_from_elite['expirationDate']
        expiry_date = expiry_date.replace('/', '-')
        response_dict["expiry_date"] = expiry_date
        # expiry_date = str(inventory_dict[0]['expirationDate'])
        # response_dict["expiry_date"] = str(expiry_date[2:4]) + '-' + str(datetime.date.today().year)[0:2] + \
        #                                str(expiry_date[0:2]) if expiry_date else expiry_date
        response_dict["inventory_quantity"] = response_from_elite['bottleQuantity']
        response_dict["lot_number"] = response_from_elite['lotNo']
        response_dict["case_id"] = response_from_elite['caseId']
        response_dict['bottle_qty'] = {response_dict["ndc"]: response_from_elite['packUnit']}

    if required_entity == "ndc" and entity not in [SCAN_ENTITY_DICT['QR'], SCAN_ENTITY_DICT["UPC"], SCAN_ENTITY_DICT["vial_QR"]]:
        response_dict["ndc"] = get_ndc_list_from_scanned_ndc(response_dict["ndc"])

    return response_dict, entity


def find_ndc_from_barcode(scanned_value):
    drug_ndc = scanned_value[-2:-12:-1][::-1]
    return drug_ndc


def get_ndc_list_from_scanned_ndc(scanned_ndc_value):
    """

    :param scanned_ndc_value:
    :return:
    """
    if len(scanned_ndc_value) > 10:
        ndc = scanned_ndc_value[2:-1]
    else:
        ndc = scanned_ndc_value

    ndc_array = []
    if len(ndc) < 10:
        return
    if len(ndc) > 10:
        ndc = ndc[1, len(ndc) - 1]
    if len(ndc) == 10:
        formatted_ndc1 = '0' + ndc
        formatted_ndc2 = ndc[0: 5] + '0' + ndc[5: 10]
        formatted_ndc3 = ndc[0: 9] + '0' + ndc[9: 10]
        ndc_array.append(formatted_ndc1)
        ndc_array.append(formatted_ndc2)
        ndc_array.append(formatted_ndc3)
        return ndc_array


def find_drug_data_from_static_matrix(matrix_data):
    """

    :param matrix_data:
    :return:
    """
    ndc = ""
    lot_number = ""
    expiry_date = ""
    serial_number = ""

    GTIN_CONSTANTS = {"code": "01", "length": 10}
    LOT_NUMBER_CONSTANTS = {"code": "10", "length": 20}
    EXPIRY_CONSTANTS = {"code": "17", "length": 6}
    SERIAL_NUMBER_CONSTANTS = {"code": "21", "length": 20}

    FNC1_LIST = [chr(29), chr(32), chr(42)]        # group separator, space, *

    string_parsed = False
    if matrix_data[0] in FNC1_LIST:
        matrix_data = matrix_data[1:]

    while not string_parsed:
        if len(matrix_data):
            print("matrix_data: ", matrix_data)
            first_char = matrix_data[0]
            if first_char in FNC1_LIST:
                matrix_data = matrix_data[1:]
            start_point = matrix_data[:2]
            matrix_data = matrix_data.replace(start_point, "", 1)
            matrix_data_copy = matrix_data[:]

            print("Start point: ", start_point)

            if start_point == GTIN_CONSTANTS["code"]:
                # Since GTIN first 3 chars are padding removing them
                matrix_data = matrix_data[3:]

                ndc, matrix_data = update_component_value_from_matrix(component_string=ndc,
                                                                      matrix_data=matrix_data,
                                                                      max_length=GTIN_CONSTANTS["length"],
                                                                      string_separator=FNC1_LIST)
                # Removing checksum bit from matrix data
                matrix_data = matrix_data[1:]

            elif start_point == LOT_NUMBER_CONSTANTS["code"]:
                lot_number, matrix_data = update_component_value_from_matrix(component_string=lot_number,
                                                                             matrix_data=matrix_data,
                                                                             max_length=LOT_NUMBER_CONSTANTS["length"],
                                                                             string_separator=FNC1_LIST)

            elif start_point == EXPIRY_CONSTANTS["code"]:
                expiry_date, matrix_data = update_component_value_from_matrix(component_string=expiry_date,
                                                                              matrix_data=matrix_data,
                                                                              max_length=EXPIRY_CONSTANTS["length"],
                                                                              string_separator=FNC1_LIST)

            elif start_point == SERIAL_NUMBER_CONSTANTS["code"]:
                serial_number, matrix_data = update_component_value_from_matrix(component_string=serial_number,
                                                                                matrix_data=matrix_data,
                                                                                max_length=LOT_NUMBER_CONSTANTS[
                                                                                    "length"],
                                                                                string_separator=FNC1_LIST)

        else:
            string_parsed = True

    if (not ndc) or (not lot_number) or (not expiry_date) or (not serial_number):
        return False, ndc, lot_number, expiry_date, serial_number

    else:
        return True, ndc, lot_number, expiry_date, serial_number


def update_component_value_from_matrix(component_string, matrix_data, max_length, string_separator):
    """

    :param component_string:
    :param matrix_data:
    :param max_length:
    :return:
    """
    print("update_component_value_from_matrix: ", component_string, matrix_data, max_length, string_separator)
    for value in matrix_data:
        if not (value in string_separator or len(component_string) >= max_length):
            component_string += value
            matrix_data = matrix_data[1:]
        else:
            if value in string_separator:
                matrix_data = matrix_data[1:]
            break
    print(component_string, matrix_data)
    return component_string, matrix_data


@log_args_and_response
def get_ndc_list_for_barcode(ndc_dict, refill=False):
    """
    This function will be used to check if drug image is available for a drug based on its ndc.
    if available then send drug data for the same else return drug id
    :param ndc_dict: Dictionary with ndc from barcode as key
        sample ndc_dict : {"scanned_ndc": scanned_value, "required_entity": "ndc", "user_id":logged_in_user_id}
    :return: Data
    """
    try:
        upc = None
        upc_flag = False
        ndc_upc_list = []
        ndc_list = []
        company_id = ndc_dict.get("company_id")
        scanned_ndc = ndc_dict["scanned_ndc"]
        ndc_allowed = ndc_dict.get('ndc_allowed', True)
        user_id = ndc_dict.get("user_id")
        module_id = int(ndc_dict.get("module_id")) if ndc_dict.get("module_id") is not None else ndc_dict.get("module_id")
        response_dict = {"is_image_available": False, "drug_data": None, "drug_id": 0, "is_data_matrix_present": False,
                         "expiry_date": None, "lot_number": None}
        bottle_qty_req = ndc_dict.get("bottle_qty_req", False)
        bottle_qty: Dict[str, int] = dict()
        token = get_token()
        inventory_data = list()

        print("scanned_ndc: ", scanned_ndc, len(scanned_ndc))

        # If length of the input is less than equal to 13, but not including 9 to 11 as it is user entered, 13 is barcode value
        # If scanned ndc starts with DPARS then it is case id
        # If scanned ndc starts with DPRD then it is as item_id
        if (len(scanned_ndc) in [i for i in range(0, 16) if i not in [0, 1, 2, 3, 4]]
                and not ndc_allowed and scanned_ndc.startswith(constants.ITEM_ID_PREFIX)):
            pass
        elif ((len(scanned_ndc) in [i for i in range(0, 13) if i not in [9, 10, 11, 12, 13]] or not ndc_allowed
               or scanned_ndc.startswith(constants.CANISTER_LABEL_PREFIX))
                and not scanned_ndc.startswith(constants.CASE_ID_PREFIX)):

            if ((not scanned_ndc.startswith(constants.CASE_ID_PREFIX) and not ndc_allowed) or
                    (scanned_ndc.startswith(constants.CANISTER_LABEL_PREFIX))):
                return [], constants.USER_ENTERED, None, None, None, None, None, None

        if scanned_ndc.startswith(constants.CASE_ID_PREFIX):
            scan_type = SCAN_ENTITY_DICT["QR"]

        elif scanned_ndc.startswith(constants.ITEM_ID_PREFIX):
            scan_type = SCAN_ENTITY_DICT["vial_QR"]

        elif len(scanned_ndc) in [9, 10, 11]:
            scan_type = SCAN_ENTITY_DICT["user_entered"]
            if len(scanned_ndc) == 11:
                drug_data = list(DrugMaster.db_get_drug_data_by_ndc_parser([scanned_ndc]))
                if not drug_data:
                    drug_data = DrugMaster.get_drugs_details_by_upclist([scanned_ndc])
                    if drug_data:
                        scan_type = SCAN_ENTITY_DICT["UPC"]

        elif len(scanned_ndc) in [12, 13]:
            scan_type = SCAN_ENTITY_DICT["barcode"]

        else:
            scan_type = SCAN_ENTITY_DICT["data_matrix"]

        response_data, scan_type = find_required_dict_from_entity(scanned_value=scanned_ndc, entity=scan_type,
                                                                  required_entity="ndc")
        case_id = response_data.get('case_id', None)

        print("Response_data: ", response_data)
        logger.info("Response_data: {}".format(response_data))

        if scan_type == SCAN_ENTITY_DICT["data_matrix"]:
            response_dict["is_data_matrix_present"] = True
            if not response_data["status"]:
                return [], constants.DATA_MATRIX, None, None, None, None, None, None
        if scanned_ndc.startswith(constants.CASE_ID_PREFIX) or scan_type == SCAN_ENTITY_DICT['UPC']:
            if response_data.get("ndc"):
                ndc_list = [response_data['ndc']]
            elif response_data.get("upc"):
                upc_flag = True
                ndc_list = [response_data['upc']]
        elif scanned_ndc.startswith(constants.ITEM_ID_PREFIX):
            ndc_list = [response_data['ndc']]
        elif len(scanned_ndc) == 11:
            ndc_list = [scanned_ndc]
        elif len(scanned_ndc) == 9:
            ndc_upc_list = DrugMaster.get_ndc_list_from_fndc_list([scanned_ndc])
            if ndc_upc_list:
                ndc_list = [item[0] for item in ndc_upc_list]
            else:
                if module_id == constants.MODULE_PRN_OTHER_RX:
                    #  if fndc not found and module is prn other rx then it will check in ips.
                    file_id = constants.PRN_DUMMY_FILE
                    # file_id added here is dummy, just for flag purpose
                    get_missing_drug_data(ndc_list=[scanned_ndc], company_id=company_id, user_id=user_id, file_id=file_id,
                                          token=token, fndc_flag=True)
                    valid_ndc_query = DrugMaster.select(DrugMaster,
                                                        DrugMaster.concated_fndc_txr_field().alias(
                                                            'fndc_txr')).dicts().where(
                        DrugMaster.formatted_ndc << [scanned_ndc])

                    for record in valid_ndc_query:
                        ndc_list.append(record['ndc'])
                        upc = record['upc']
        else:
            ndc_list = response_data["ndc"]

        print("NDC list: ", ndc_list)
        logger.info("NDC list: {}".format(ndc_list))
        valid_drug_list = list()
        if ndc_list:
            existing_ndc_list = copy.deepcopy(ndc_list)
            if not upc_flag:
                ndc_list = [x.zfill(11) for x in ndc_list]
                valid_ndc_query = DrugMaster.select(DrugMaster,
                                                    DrugMaster.concated_fndc_txr_field().alias('fndc_txr')).dicts().where(
                    DrugMaster.ndc << ndc_list)
                existing_ndc_list = copy.deepcopy(ndc_list)
                ndc_list = list()

                for record in valid_ndc_query:
                    ndc_list.append(record['ndc'])
                    upc = record['upc']
                    valid_drug_list.append(record)

            logger.info("In get_valid_ndc: valid_drug_list{}".format(valid_drug_list))

            if not ndc_list and existing_ndc_list:

                if module_id == constants.MODULE_PRN_OTHER_RX:
                    # if ndc not found and module is prn other rx then it will check in ips.
                    file_id = constants.PRN_DUMMY_FILE
                    # file_id added here is dummy, just for flag purpose
                    try:
                        get_missing_drug_data(existing_ndc_list, company_id, user_id, file_id)
                    except Exception as e:
                        logger.info("ndc tried to fetch from IPS but didn't received any now trying for upc")
                        get_missing_drug_data(existing_ndc_list, company_id, user_id, file_id, upc_flag=True)

                    valid_ndc_query = DrugMaster.select(DrugMaster,
                                                        DrugMaster.concated_fndc_txr_field().alias(
                                                            'fndc_txr')).dicts().where(
                        DrugMaster.ndc << existing_ndc_list)
                    for record in valid_ndc_query:
                        ndc_list.append(record['ndc'])
                        upc = record['upc']
                        valid_drug_list.append(record)

                    logger.info("In get_valid_ndc: valid_drug_list{}".format(valid_drug_list))
                if not ndc_list:
                    # if no ndc found in drug_master based on 11 digit ndc then check for formatted ndc
                    logger.info("get_valid_ndc: No ndc found in drug_master based on 11 digit ndc "
                                "then check for formatted ndc: {}".format(existing_ndc_list))
                    fndc_list = list(map(lambda ndc: str(ndc)[0:9], existing_ndc_list))
                    ndc_upc_list = DrugMaster.get_ndc_list_from_fndc_list(fndc_list)
                    if ndc_upc_list:
                        ndc_list = [item[0] for item in ndc_upc_list]
                        upc = ndc_upc_list[0][1]
                        logger.info("get_valid_ndc: found ndc_list: {} based on fndc - {}".format(ndc_list, existing_ndc_list))
                        # drug_id = DrugMaster.select(DrugMaster.id).where(DrugMaster.ndc == ndc).scalar()
            if 'DP' not in scanned_ndc:
                if settings.USE_EPBM and not upc_flag:
                    ndc_list_copy = [int(item) for item in ndc_list]
                    inventory_data = get_current_inventory_data(ndc_list=ndc_list_copy, qty_greater_than_zero=False)
                response_data['inventory_quantity'] = 0 if inventory_data else None
                for record in inventory_data:
                    response_data['inventory_quantity'] += record['quantity']

        if valid_drug_list and user_id:
            # add drug details- who scanned the drug bottle
            for drug in valid_drug_list:
                # fetch drug_id from unique_drug table based on fndc and txr of scanned drug(drug_id)
                # this is because we have to keep track of used drug based on unique drug (same fndc, txr)
                unique_drug_id = None
                unique_drug_query = UniqueDrug.select(UniqueDrug).dicts().where(
                    UniqueDrug.concated_fndc_txr_field() == drug['fndc_txr'])
                for unique_drug in unique_drug_query:
                    unique_drug_id = unique_drug['id']
                    break
                if unique_drug_id:
                    dd_update_status = DrugDetails.db_update_or_create({"unique_drug_id": unique_drug_id,
                                                                        "company_id": ndc_dict.get("company_id")},
                                                                       {"last_seen_by": user_id,
                                                                        "last_seen_date": get_current_date_time()})
                    logger.info("In get_ndc_list_for_barcode: drug details update status: {}".format(dd_update_status))

        # function call to get the bottle qty for the given ndc in the ndc_list
        if bottle_qty_req:
            drug_data_from_db = DrugMaster.fetch_drug_bottle_qty(ndc=ndc_list)
            for ndc in ndc_list:
                if drug_data_from_db and ndc in drug_data_from_db.keys():
                    logger.info("Fetched Drug Bottle qty from db")
                    bottle_qty[ndc] = drug_data_from_db[ndc]
                elif settings.USE_EPBM:
                    drug_data = get_data_by_ndc_from_drug_inventory(ndc_list=[ndc], bottle_qty=True)
                    if drug_data:
                        if ndc in drug_data:
                            logger.info("Fetched Drug Bottle qty from elite")
                            bottle_qty[ndc] = drug_data[ndc]["packUnit"]
                        try:
                            with db.transaction():
                                for ndc, qty in bottle_qty.items():
                                    update = DrugMaster.udpate_bottle_qty(qty=qty, ndc=ndc)
                        except Exception as e:
                            logger.error("In get_ndc_list_for_barcode : Unable to update bottle qty")

        return ndc_list, SCAN_TYPE_COMPATIBILITY.get(scan_type), response_data.get("lot_number"), \
            response_data.get("expiry_date"), response_data.get('inventory_quantity'), case_id, upc, bottle_qty

    except DrugFetchFailedException as e:
        logger.error(f"ndc not found in ips {e} ")
        return [], SCAN_TYPE_COMPATIBILITY.get(scan_type), response_data.get("lot_number"), \
            response_data.get("expiry_date"), response_data.get('inventory_quantity'), case_id, upc, bottle_qty

    except Exception as e:
        logger.error("Error in get_ndc_list_for_barcode".format(e))
        raise


@log_args_and_response
def get_multi_search_with_drug_scan(clauses, multi_search_values, model_search_fields, ndc_search_field):
    """
    Appends applicable filters to `subclauses` with  `or` operaor and append sublcauses to `clauses`  list and return `clauses`
    @param clauses:
    @param model_search_fields: list of model to be compare with
    @param multi_search_values: list of values to filter
    @return: list
    """
    try:
        if not multi_search_values:
            return clauses

        # --> Shifted the List variables out of FOR loop because they need to separated by OR operator and are required
        # to be added only once in "clauses" list.

        # --> If they were inside the FOR loop then they were added separately into "clauses" list
        # --> Which means AND condition was applied among different comma separated data entered through multi-search
        subclauses = list()
        reducedsubclauses = list()
        for value in multi_search_values:

            data = str(value).translate(str.maketrans({'%': r'\%'}))  # escape % from search string

            # Need to remove the whitespaces from both ends to apply appropriate LIKE condition in WHERE clause
            search_data = "%" + data.strip() + "%"

            for field in model_search_fields:
                if ndc_search_field and str(field) == str(ndc_search_field):
                    ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                        {"scanned_ndc": value, "required_entity": "ndc"})
                    if ndc_list:
                        subclauses.append((fn.CONCAT('', field) << ndc_list))
                    else:
                        subclauses.append(((fn.CONCAT('', field) ** search_data)))
                else:
                    subclauses.append((fn.CONCAT('', field) ** search_data))

        # All the conditions are separated by OR operator and will be added only once into "clauses"
        # This will help in retrieving data based on all values entered through multi-search
        reducedsubclauses = functools.reduce(operator.or_, subclauses)
        clauses.append(reducedsubclauses)
        return clauses
    except Exception as e:
        print("Error in get_multi_search_with_drug_scan {}".format(e))
        raise


@log_args_and_response
def get_ndq_for_ndc_list(ndc_list, drug_scan_type=None):
    try:
        response = dict()
        for ndc in ndc_list:
            response[ndc] = None
        clauses = [DrugMaster.ndc << ndc_list]
        if drug_scan_type == constants.UPC_SCAN:
            clauses = [DrugMaster.upc << ndc_list]
        query = (DrugMaster.select(DrugMaster.ndc, DrugMaster.dispense_qty)
                 .dicts()
                 .where(*clauses)
                 )
        for record in query:
            if record["ndc"] in response:
                response[record["ndc"]] = record["dispense_qty"]

        return response

    except Exception as e:
        logger.error("Error in get_ndq_for_ndc_list: {}".format(e))
        raise e


@log_args_and_response
def get_drug_data_from_upc_list(upc_list):
    try:
        drug_details = DrugMaster.get_drugs_details_by_upclist(upc_list)
        return drug_details

    except Exception as e:
        logger.error(f"error in get_ndc_from_upc {e}")
        raise e
