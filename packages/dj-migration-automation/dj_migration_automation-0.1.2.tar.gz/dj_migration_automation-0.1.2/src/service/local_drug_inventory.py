import math
from typing import List, Dict, Any, Tuple, Optional, Set
import numpy
from peewee import InternalError, IntegrityError, DoesNotExist, DataError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.local.lang_us_en import err
from dosepack.utilities.utils import (get_epoch_time_start_of_day_and_before_n_days, log_args_and_response,
                                      get_date_n_days_back_the_epoch_time)
from drug_recom_for_big_canister import company_id
from settings import SUCCESS_RESPONSE, GENERIC_FLAG, BRAND_FLAG, NON_DRUG_FLAG
from src.constants import (LOCAL_DI_CONSUMED_FOR_PACK_ID_AND_NDC_MSG, LOCAL_DI_DROPPED_NDC_ADDED_WITH_ZERO_QTY_MSG,
                           LOCAL_DI_QTY_CONSUMED_FOR_SAME_FNDC_TXR_ACTION_ID, LOCAL_DI_QTY_ADDED_ACTION_ID,
                           LOCAL_DI_QTY_CONSUMED_ACTION_ID, LOCAL_DI_CONSUMED_FOR_PACK_ID_MSG,
                           LOCAL_DI_CONSUMED_MORE_THAN_AVAILABLE_MSG, LOCAL_DI_QTY_ADDED_TO_NEGATIVE_FOR_SAME_NDC_MSG,
                           LOCAL_DI_QTY_ADDED_TO_NEGATIVE_FOR_SAME_FNDC_TXR_MSG, EPBM_TXR_LIST_LIMIT,
                           EPBM_NDC_LIST_LIMIT)
from src.dao.local_drug_inventory_dao import (local_di_insert_txn_data, local_di_insert_inventory_data,
                                              local_di_update_inventory_by_ndc, local_di_insert_po_data,
                                              local_di_get_inventory_data, local_di_get_po_data)
from src.exceptions import (APIFailureException, DrugInventoryInternalException, DrugInventoryValidationException,
                            TokenFetchException)
from utils.auth_webservices import send_email_for_same_ndc_diff_txr
from utils.drug_inventory_webservices import (get_po_numbers, get_data_by_po_numbers, get_current_inventory_data,
                                              get_data_by_ndc_from_drug_inventory)

logger = settings.logger


@log_args_and_response
def update_local_inventory_by_slot_transaction(pack_id: int, drop_data: List[Dict[str, Any]]) -> bool:
    """
    Update the local inventory corresponding to the ndc, fndc and txr for the dropped qty from the canister.
    """
    consumption_data: Dict[str, Dict[str, int]] = dict()
    inventory_data: Dict[str, Dict[str, Dict[str, Any]]] = dict()
    error_msgs: List[str] = list()
    try:
        # format the update_dict
        for record in drop_data:
            fndc_txr: str = str(record["formatted_ndc"]) + "##" + str(record["txr"])
            if fndc_txr in consumption_data:
                if record["ndc"] in consumption_data[fndc_txr]:
                    consumption_data[fndc_txr][record["ndc"]] += record["quantity"]
                else:
                    consumption_data[fndc_txr][record["ndc"]] = record["quantity"]
            else:
                consumption_data[fndc_txr] = {record["ndc"]: record["quantity"]}

        with db.transaction():
            # get the local inventory data for all the NDC by the fndc_txr
            for data in local_di_get_inventory_data(fndc_txr_list=list(consumption_data.keys())):
                if data["fndc_txr"] in inventory_data:
                    inventory_data[data["fndc_txr"]][data["ndc"]] = data
                else:
                    inventory_data[data["fndc_txr"]] = {data["ndc"]: data}

            # get the data to update the LocalDIData and LocalDITransaction
            db_data: Dict[str, Any] = prepare_db_data_for_consumption(inventory_data=inventory_data, pack_id=pack_id,
                                                                      consumption_data=consumption_data)
            insert_data: List[Dict[str, Any]] = db_data["insert_date"]
            update_data: Dict[str, Dict[str, int]] = db_data["update_data"]
            txn_data: List[Dict[str, Any]] = db_data["txn_data"]
            error_msgs.extend(db_data["error_data"])

            local_inventory_db_update(local_di_insert_data=insert_data, local_di_txn_data=txn_data,
                                      local_di_update_data=update_data)
        if len(error_msgs) > 0:
            msg_str: str = "For pack_id: {}, ".format(pack_id) + err[20014]
            for i in range(0, len(error_msgs)):
                msg_str += "<br>" + str(i + 1) + ") " + str(error_msgs[i])

            msg_str += "<br><br><br>Consumption Data: " + str(consumption_data)

            send_email_for_same_ndc_diff_txr(company_id=company_id, error_details=msg_str)

        return True

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        return True
    except Exception as e:
        logger.error(e, exc_info=True)
        return True


@log_args_and_response
def prepare_db_data_for_consumption(inventory_data: Dict[str, Dict[str, Dict[str, Any]]],
                                    consumption_data: Dict[str, Dict[str, int]],
                                    pack_id: int) -> Dict[str, Any]:
    """
    Returns the data to update the LocalDIData and LocalDITransaction after consumption.
    """
    insert_data_dict: Dict[str, Dict[str, Dict[str, Any]]] = dict()
    update_data_dict: Dict[str, Dict[str, int]] = dict()
    transaction_list: List[Dict[str, Any]] = list()
    insert_data_list: List[Dict[str, Any]] = list()
    error_msgs: List[str] = list()
    data_dict: Dict[str, Any]
    try:
        for fndc_txr in consumption_data:
            formatted_ndc: str = fndc_txr.split("##")[0]
            txr: str = fndc_txr.split("##")[1]
            # when the filled fndc_txr is available in the local drug inventory
            if fndc_txr in inventory_data:
                inventory_for_fndc_txr: Dict[str, Any] = inventory_data[fndc_txr]

                for con_ndc in consumption_data[fndc_txr]:
                    dropped_qty: int = math.ceil(consumption_data[fndc_txr][con_ndc])

                    # when the filled ndc is unavailable in the local drug inventory
                    if con_ndc not in inventory_for_fndc_txr:
                        # initialize the ndc in the local inventory
                        action_id: int = LOCAL_DI_QTY_ADDED_ACTION_ID
                        comment: str = LOCAL_DI_DROPPED_NDC_ADDED_WITH_ZERO_QTY_MSG.format(pack_id, con_ndc)
                        transaction_list = get_local_di_txn_data(ndc=con_ndc, fndc=formatted_ndc, txr=txr,
                                                                 data_list=transaction_list, quantity=0,
                                                                 comment=comment, action_id=action_id)

                        # prepare the data to the insert in the LocalDIData table
                        quantity: int = 0 - dropped_qty
                        insert_data_dict = get_local_di_insert_data(ndc=con_ndc, qty=quantity, txr=txr,
                                                                    fndc=formatted_ndc, data_dict=insert_data_dict)

                        # add the record for the consumed_ndc with 0 qty
                        inventory_for_fndc_txr[con_ndc] = {"id": 0, "ndc": con_ndc, "fndc_txr": fndc_txr, "quantity": 0}

                    # when filled ndc is available in the local drug inventory
                    if inventory_for_fndc_txr[con_ndc]["quantity"] > 0:
                        data_dict = consume_same_ndc(inventory_details=inventory_for_fndc_txr, txr=txr, pack_id=pack_id,
                                                     consumed_ndc=con_ndc, consumed_qty=dropped_qty, fndc=formatted_ndc,
                                                     update_dict=update_data_dict, transaction_data=transaction_list)
                        dropped_qty = data_dict["consumed_qty"]
                        transaction_list = data_dict["transaction_data"]
                        update_data_dict = data_dict["update_dict"]
                        inventory_for_fndc_txr = data_dict["inventory_details"]

                    # when the dropped qty is more than the inventory qty for the dropped ndc
                    if dropped_qty > 0:
                        data_dict = consume_ndc_with_same_fndc_txr(inventory_details=inventory_for_fndc_txr, txr=txr,
                                                                   consumed_ndc=con_ndc, consumed_qty=dropped_qty,
                                                                   fndc=formatted_ndc, update_dict=update_data_dict,
                                                                   pack_id=pack_id, transaction_data=transaction_list)
                        dropped_qty = data_dict["consumed_qty"]
                        transaction_list = data_dict["transaction_data"]
                        update_data_dict = data_dict["update_dict"]
                        inventory_for_fndc_txr = data_dict["inventory_details"]

                    # when dropped_qty is greater than the aggregated inventory qty for the fndc_txr.
                    if dropped_qty > 0:
                        # prepare details and update transaction data
                        action_id: int = LOCAL_DI_QTY_CONSUMED_ACTION_ID
                        comment: str = LOCAL_DI_CONSUMED_MORE_THAN_AVAILABLE_MSG.format(pack_id)
                        transaction_list = get_local_di_txn_data(ndc=con_ndc, fndc=formatted_ndc, comment=comment,
                                                                 data_list=transaction_list, txr=txr,
                                                                 action_id=action_id, quantity=dropped_qty)

                        # update the quantity in the inventory data dict
                        inventory_for_fndc_txr[con_ndc]["quantity"] -= dropped_qty

                        # update the qty in insert dict to prevent extra update db calls.
                        if con_ndc in insert_data_dict and fndc_txr in insert_data_dict[con_ndc]:
                            insert_data_dict[con_ndc][fndc_txr]["quantity"] -= dropped_qty
                        else:
                            # update the qty to be updated in the LocalDIData table
                            update_data_dict[inventory_for_fndc_txr[con_ndc]["ndc"]] = {
                                "quantity": inventory_for_fndc_txr[con_ndc]["quantity"]}
                # update the inventory after the consumption calculation
                inventory_data[fndc_txr] = inventory_for_fndc_txr

            # when the filled fndc_txr is unavailable in the local drug inventory
            else:
                inventory_data[fndc_txr] = {}
                for con_ndc in consumption_data[fndc_txr]:
                    dropped_qty: int = math.ceil(consumption_data[fndc_txr][con_ndc])
                    # initialize the NDC in the local inventory
                    action_id: int = LOCAL_DI_QTY_ADDED_ACTION_ID
                    comment: str = LOCAL_DI_DROPPED_NDC_ADDED_WITH_ZERO_QTY_MSG.format(pack_id, con_ndc)
                    transaction_list = get_local_di_txn_data(ndc=con_ndc, fndc=formatted_ndc, txr=txr, comment=comment,
                                                             data_list=transaction_list, action_id=action_id,
                                                             quantity=0)

                    # prepare details and update transaction data
                    action_id: int = LOCAL_DI_QTY_CONSUMED_ACTION_ID
                    comment: str = LOCAL_DI_CONSUMED_MORE_THAN_AVAILABLE_MSG.format(pack_id)
                    transaction_list = get_local_di_txn_data(ndc=con_ndc, fndc=formatted_ndc, txr=txr, comment=comment,
                                                             data_list=transaction_list, action_id=action_id,
                                                             quantity=dropped_qty)

                    # prepare the data to the insert in the LocalDIData table
                    quantity: int = 0 - dropped_qty
                    insert_data_dict = get_local_di_insert_data(ndc=con_ndc, qty=quantity, txr=txr, fndc=formatted_ndc,
                                                                data_dict=insert_data_dict)

                    # update the inventory data as per the insertion
                    inventory_data[fndc_txr][con_ndc] = {"id": 0, "ndc": con_ndc, "fndc_txr": fndc_txr,
                                                         "quantity": 0 - dropped_qty}

        # check valid insertion by ndc for the LocalDIData table.
        if insert_data_dict:
            insert_data, error_msg_list = check_valid_ndc_to_insert(check_data_dict=insert_data_dict)
            insert_data_list.extend(insert_data)
            error_msgs.extend(error_msg_list)

        return {"insert_date": insert_data_list, "update_data": update_data_dict,
                "txn_data": transaction_list, "error_data": error_msgs}

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def consume_same_ndc(inventory_details: Dict[str, Any], consumed_ndc: str, consumed_qty: int, fndc: str,
                     txr: str, pack_id: int, transaction_data: List[Dict[str, Any]],
                     update_dict: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
    """
    Considering the inventory qty of the dropped NDC.
    """
    try:
        inventory_qty: int = math.floor(inventory_details[consumed_ndc]["quantity"])
        qty_diff: int = inventory_qty - consumed_qty

        # prepare details and update transaction data
        action_id: int = LOCAL_DI_QTY_CONSUMED_ACTION_ID
        comment: str = LOCAL_DI_CONSUMED_FOR_PACK_ID_MSG.format(pack_id)
        quantity: int = inventory_qty if qty_diff < 0 else consumed_qty
        transaction_data = get_local_di_txn_data(ndc=consumed_ndc, fndc=fndc, data_list=transaction_data,
                                                 txr=txr, comment=comment, action_id=action_id,
                                                 quantity=quantity)
        # update the qty to be updated in the LocalDIData table
        update_dict[inventory_details[consumed_ndc]["ndc"]] = {"quantity": 0 if qty_diff < 0 else abs(qty_diff)}
        inventory_details[consumed_ndc]["quantity"] = 0 if qty_diff < 0 else abs(qty_diff)
        # consumed remaining qty
        consumed_qty = abs(qty_diff) if qty_diff < 0 else 0

        return {"consumed_qty": consumed_qty, "transaction_data": transaction_data,
                "update_dict": update_dict, "inventory_details": inventory_details}

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def consume_ndc_with_same_fndc_txr(inventory_details: Dict[str, Any], consumed_ndc: str, consumed_qty: int, fndc: str,
                                   txr: str, pack_id: int, transaction_data: List[Dict[str, Any]],
                                   update_dict: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
    """
    In case when the dropped NDC is not having the enough qty, considering the NDCs with similar fndc_txr.
    """
    try:
        for inv_ndc in inventory_details:
            inventory_qty: int = math.ceil(inventory_details[inv_ndc]["quantity"])

            if inventory_qty > 0:
                qty_diff: int = inventory_qty - consumed_qty

                # prepare details and update transaction data
                action_id: int = LOCAL_DI_QTY_CONSUMED_FOR_SAME_FNDC_TXR_ACTION_ID
                comment: str = LOCAL_DI_CONSUMED_FOR_PACK_ID_AND_NDC_MSG.format(pack_id, consumed_ndc)
                quantity: int = inventory_qty if qty_diff < 0 else consumed_qty

                transaction_data = get_local_di_txn_data(fndc=fndc, ndc=inv_ndc, comment=comment, txr=txr,
                                                         action_id=action_id, quantity=quantity,
                                                         data_list=transaction_data)

                # update the qty to be updated in the LocalDIData table
                update_dict[inventory_details[inv_ndc]["ndc"]] = {"quantity": 0 if qty_diff < 0 else abs(qty_diff)}
                inventory_details[inv_ndc]["quantity"] = 0 if qty_diff < 0 else abs(qty_diff)
                # consumed remaining qty
                consumed_qty = abs(qty_diff) if qty_diff < 0 else 0

                if qty_diff >= 0:
                    break

        return {"consumed_qty": consumed_qty, "transaction_data": transaction_data,
                "update_dict": update_dict, "inventory_details": inventory_details}
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_local_inventory_by_ack_po(no_of_days_for_po: int, department: str) -> List[str]:
    """
    Update the local inventory based on the confirmed POs.
    """
    inventory_data: Dict[str, Dict[str, Dict[str, Any]]] = dict()
    negative_qty_data: Dict[str, List[str]] = dict()
    po_data: Dict[str, List[Dict[str, Any]]]
    ack_data: Dict[str, Dict[str, int]]
    brand_data: Dict[str, str]
    error_msgs: List[str] = list()
    try:
        new_po_no_list: List[str] = check_new_po_ack(department, no_of_days_for_po)

        # if all ack PO numbers are synced, return error_msgs
        if not new_po_no_list:
            return error_msgs
        po_data, ack_data, brand_data = get_po_data(po_number_list=new_po_no_list)

        po_insert_data: List[Dict[str, Any]] = [{"po_number": k, "po_ack_data": v} for k, v in po_data.items()]

        with db.transaction():
            # get the local inventory data for all the NDC by the fndc_txr
            for data in local_di_get_inventory_data(fndc_txr_list=list(ack_data.keys())):
                if data["fndc_txr"] in inventory_data:
                    inventory_data[data["fndc_txr"]][data["ndc"]] = data
                else:
                    inventory_data[data["fndc_txr"]] = {data["ndc"]: data}

                if data["quantity"] < 0:
                    if data["fndc_txr"] in negative_qty_data:
                        negative_qty_data[data["fndc_txr"]].append(data["ndc"])
                    else:
                        negative_qty_data[data["fndc_txr"]] = [data["ndc"]]

            db_data: Dict[str, Any] = prepare_db_data_for_addition(inventory_data=inventory_data,
                                                                   addition_data=ack_data, brand_data=brand_data,
                                                                   negative_qty_data=negative_qty_data)

            insert_data: List[Dict[str, Any]] = db_data["insert_date"]
            update_data: Dict[str, Dict[str, int]] = db_data["update_data"]
            txn_data: List[Dict[str, Any]] = db_data["txn_data"]
            error_msgs.extend(db_data["error_data"])

            local_inventory_db_update(local_di_insert_data=insert_data, local_di_txn_data=txn_data,
                                      local_di_update_data=update_data, local_di_po_data=po_insert_data)

        return error_msgs

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
def check_new_po_ack(department: str, no_of_days_for_po: int) -> List[str]:
    """
    Returns the list of the POs that are acknowledged and are yet to be synced to update the Local Drug Inventory.
    """
    start_time: int
    end_time: int
    try:
        start_time, end_time = get_epoch_time_start_of_day_and_before_n_days(number_of_days=no_of_days_for_po)

        # get the PO numbers for the given department between the start_time and end_time
        po_no_list: List[str] = get_po_numbers(start_time=(start_time * 1000), end_time=(end_time * 1000),
                                               department=department)

        # get the list of PO numbers that are added to the local inventory in past n number of days
        po_created_after_date: str = get_date_n_days_back_the_epoch_time(epoch_time=end_time, number_of_days=30,
                                                                         return_format="date")
        # get the PO numbers created after the given_date
        existing_po_no_list: List[str] = [data["po_number"] for data in
                                          local_di_get_po_data(created_after_date=po_created_after_date)]

        new_po_no_list: Set[str] = set(po_no_list).difference(set(existing_po_no_list))

        return list(new_po_no_list)

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
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_po_data(po_number_list: List[str]) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, int]],
                                                    Dict[str, str]]:
    """
    Get the drug and inventory data corresponding to the list of the acknowledged PO numbers.
    """
    po_data: Dict[str, List[Dict[str, Any]]] = dict()
    ack_data: Dict[str, Dict[str, int]] = dict()
    brand_data: Dict[str, str] = dict()
    try:
        po_data_from_src: List[Dict[str, Any]] = get_data_by_po_numbers(po_number_list=po_number_list)
        # format the po_data_from_src
        for record in po_data_from_src:
            # prepare the data for the po insert
            if record["poNumber"] in po_data:
                po_data[record["poNumber"]].extend(record["orderDetails"])
            else:
                po_data[record["poNumber"]] = record["orderDetails"]

            # prepare the data for the inventory update
            for order in record["orderDetails"]:
                ndc: str = str(order["ackNdc"])
                fndc_txr: str = ndc[0:9] + "##" + str(order["cfi"])

                brand_flag: Optional[str] = None
                if "brand" in order:
                    if order["brand"] == "G":
                        brand_flag = GENERIC_FLAG
                    elif order["brand"] == "B":
                        brand_flag = BRAND_FLAG
                    elif order["brand"] == "N":
                        brand_flag = NON_DRUG_FLAG

                # prepare the drug data corresponding to the acknowledged PO.
                if fndc_txr in ack_data:
                    if ndc in ack_data[fndc_txr]:
                        ack_data[fndc_txr][ndc] += order["ackQuantity"]
                    else:
                        ack_data[fndc_txr][ndc] = order["ackQuantity"]
                else:
                    ack_data[fndc_txr] = {ndc: order["ackQuantity"]}

                # prepare the brand data by fndc_txr
                brand_data[fndc_txr] = brand_flag

        return po_data, ack_data, brand_data

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
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def prepare_db_data_for_addition(inventory_data: Dict[str, Dict[str, Dict[str, Any]]], brand_data: Dict[str, str],
                                 addition_data: Dict[str, Dict[str, int]],
                                 negative_qty_data: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Returns the data to update the LocalDIData and LocalDITransaction after PO acknowledgements.
    """
    insert_data_dict: Dict[str, Dict[str, Dict[str, Any]]] = dict()
    update_data_dict: Dict[str, Dict[str, int]] = dict()
    transaction_list: List[Dict[str, Any]] = list()
    insert_data_list: List[Dict[str, Any]] = list()
    error_msgs: List[str] = list()
    data_dict: Dict[str, Any]
    try:
        for fndc_txr in addition_data:
            formatted_ndc: str = fndc_txr.split("##")[0]
            txr: str = fndc_txr.split("##")[1]

            inventory_for_fndc_txr: Dict[str, Any] = inventory_data[fndc_txr] if fndc_txr in inventory_data else {}

            if (fndc_txr in inventory_data) and (fndc_txr in negative_qty_data):
                # try to add the qty for the same ndc to compensate the -ve qty.
                for neg_ndc in negative_qty_data[fndc_txr]:
                    if neg_ndc in addition_data[fndc_txr]:
                        qty_to_add: int = math.floor(addition_data[fndc_txr][neg_ndc])
                        curr_qty: int = math.floor(inventory_for_fndc_txr[neg_ndc]["quantity"])
                        qty_diff: int = curr_qty + qty_to_add

                        # prepare details and update transaction data
                        action_id: int = LOCAL_DI_QTY_ADDED_ACTION_ID
                        comment: str = LOCAL_DI_QTY_ADDED_TO_NEGATIVE_FOR_SAME_NDC_MSG
                        quantity: int = qty_to_add if qty_diff < 0 else abs(curr_qty)
                        transaction_list = get_local_di_txn_data(quantity=quantity, fndc=formatted_ndc, txr=txr,
                                                                 action_id=action_id, ndc=neg_ndc, comment=comment,
                                                                 data_list=transaction_list)
                        # maintaining the data to create or update the qty NDC in the local inventory.
                        update_data_dict[neg_ndc] = {"quantity": qty_diff if qty_diff < 0 else 0}
                        addition_data[fndc_txr][neg_ndc] = 0 if qty_diff < 0 else qty_diff
                        inventory_for_fndc_txr[neg_ndc]["quantity"] = qty_diff if qty_diff < 0 else 0

                        if qty_diff >= 0:
                            negative_qty_data[fndc_txr].remove(neg_ndc)

                # when the added qty of the exact NDC is not sufficient to compensate it's -ve qty, using the added
                # qty of same fndc_txr to compensate the -ve qty
                if len(negative_qty_data[fndc_txr]) > 0:
                    for neg_ndc in negative_qty_data[fndc_txr]:
                        for add_ndc in addition_data[fndc_txr]:
                            qty_to_add: int = math.floor(addition_data[fndc_txr][add_ndc])
                            if qty_to_add > 0:
                                curr_qty: int = math.floor(inventory_for_fndc_txr[neg_ndc]["quantity"])
                                qty_diff: int = curr_qty + qty_to_add

                                # prepare details and update transaction data
                                action_id: int = LOCAL_DI_QTY_CONSUMED_FOR_SAME_FNDC_TXR_ACTION_ID
                                comment: str = LOCAL_DI_QTY_ADDED_TO_NEGATIVE_FOR_SAME_FNDC_TXR_MSG.format(add_ndc)
                                quantity: int = qty_to_add if qty_diff < 0 else abs(curr_qty)
                                transaction_list = get_local_di_txn_data(quantity=quantity, fndc=formatted_ndc,
                                                                         action_id=action_id, ndc=neg_ndc, txr=txr,
                                                                         comment=comment, data_list=transaction_list)

                                # maintaining the data to create or update the qty NDC in the local inventory.
                                update_data_dict[neg_ndc] = {"quantity": qty_diff if qty_diff < 0 else 0}
                                addition_data[fndc_txr][add_ndc] = 0 if qty_diff < 0 else qty_diff
                                inventory_for_fndc_txr[neg_ndc]["quantity"] = qty_diff if qty_diff < 0 else 0

                                if qty_diff >= 0:
                                    break

                # create or update the qty for the remaining NDC in the local inventory.
                for ndc in addition_data[fndc_txr]:
                    qty_to_add: int = math.floor(addition_data[fndc_txr][ndc])
                    brand_flag: str = brand_data[fndc_txr]
                    data_dict = add_or_create_for_same_ndc(ndc=ndc, transaction_data=transaction_list,
                                                           fndc=formatted_ndc, insert_data=insert_data_dict,
                                                           txr=txr, inventory_details=inventory_for_fndc_txr,
                                                           add_qty=qty_to_add, update_dict=update_data_dict,
                                                           brand_flag=brand_flag)
                    insert_data_dict = data_dict["insert_data"]
                    transaction_list = data_dict["transaction_data"]
                    update_data_dict = data_dict["update_dict"]
                    inventory_for_fndc_txr = data_dict["inventory_details"]

            # when the acknowledged fndc_txr does not exist in the local drug inventory or is not having -ve qty.
            else:
                for ndc in addition_data[fndc_txr]:
                    qty_to_add: int = math.floor(addition_data[fndc_txr][ndc])
                    brand_flag: str = brand_data[fndc_txr]
                    data_dict = add_or_create_for_same_ndc(ndc=ndc, transaction_data=transaction_list,
                                                           fndc=formatted_ndc, insert_data=insert_data_dict,
                                                           txr=txr, inventory_details=inventory_for_fndc_txr,
                                                           add_qty=qty_to_add, update_dict=update_data_dict,
                                                           brand_flag=brand_flag)
                    insert_data_dict = data_dict["insert_data"]
                    transaction_list = data_dict["transaction_data"]
                    update_data_dict = data_dict["update_dict"]
                    inventory_for_fndc_txr = data_dict["inventory_details"]

            # update the inventory after the consumption calculation
            inventory_data[fndc_txr] = inventory_for_fndc_txr

        # check valid insertion by ndc for the LocalDIData table.
        if insert_data_dict:
            insert_data, error_msg_list = check_valid_ndc_to_insert(check_data_dict=insert_data_dict)
            insert_data_list.extend(insert_data)
            error_msgs.extend(error_msg_list)

        return {"insert_date": insert_data_list, "update_data": update_data_dict, "txn_data": transaction_list,
                "error_data": error_msgs}

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def add_or_create_for_same_ndc(ndc: str, add_qty: int, fndc: str, txr: str, insert_data: Dict[str, Any],
                               inventory_details: Dict[str, Any], transaction_data: List[Dict[str, Any]],
                               update_dict: Dict[str, Dict[str, int]], brand_flag: str) -> Dict[str, Any]:
    """
    Adding qty for the same NDC as the acknowledged NDC.
    """
    try:
        action_id: int = LOCAL_DI_QTY_ADDED_ACTION_ID
        if ndc in inventory_details:
            if add_qty > 0:
                # prepare details and update transaction data
                transaction_data = get_local_di_txn_data(ndc=ndc, fndc=fndc, txr=txr, action_id=action_id,
                                                         quantity=add_qty, data_list=transaction_data)
                add_qty += math.floor(inventory_details[ndc]["quantity"])
                update_dict[ndc] = {"quantity": add_qty}
                inventory_details[ndc]["quantity"] = add_qty
        else:
            # prepare details and update transaction data
            transaction_data = get_local_di_txn_data(ndc=ndc, fndc=fndc, txr=txr, action_id=action_id, quantity=add_qty,
                                                     data_list=transaction_data)
            # prepare the data to the insert in the LocalDIData table
            insert_data = get_local_di_insert_data(ndc=ndc, qty=add_qty, txr=txr, fndc=fndc, brand_flag=brand_flag,
                                                   data_dict=insert_data)

            # update the inventory data as per the insertion
            inventory_details[ndc] = {"id": 0, "ndc": ndc, "fndc_txr": fndc + "##" + txr,
                                      "quantity": add_qty}
        return {"transaction_data": transaction_data, "update_dict": update_dict,
                "inventory_details": inventory_details, "insert_data": insert_data}

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_local_di_insert_data(data_dict: Dict[str, Any], ndc: str, qty: int, fndc: str, txr: str,
                             brand_flag: Optional[str] = None) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Prepare the data for inserting in the LocalDIData table.
    """
    try:
        fndc_txr: str = str(fndc) + "##" + str(txr)
        temp_dict: Dict[str, Any] = {"ndc": ndc, "formatted_ndc": fndc, "txr": txr, "quantity": qty,
                                     "brand_flag": brand_flag}
        if ndc in data_dict:
            data_dict[ndc][fndc_txr] = temp_dict
        else:
            data_dict[ndc] = {fndc_txr: temp_dict}

        return data_dict

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_local_di_txn_data(ndc: str, fndc: str, data_list: List[Dict[str, Any]], txr: str, action_id: int,
                          quantity: int, comment: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Prepare the data for inserting in the LocalDITransaction table.
    """
    try:
        data_list.append({"ndc": ndc, "formatted_ndc": fndc, "txr": txr, "quantity": quantity,
                          "action_id": action_id, "comment": comment})
        return data_list

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def check_valid_ndc_to_insert(check_data_dict: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Check if the ndc to insert in the LocalDIData is valid corresponding to the given fndc_txr
    or a duplicate with other fndc txr.
    """
    result_list: List[Dict[str, Any]] = list()
    error_msg_list: List[str] = list()
    try:
        existing_inventory_data = local_di_get_inventory_data(ndc_list=list(check_data_dict.keys()))

        if len(existing_inventory_data) > 0:
            for data in existing_inventory_data:
                for fndc_txr1 in check_data_dict[data["ndc"]]:
                    if fndc_txr1 == data["fndc_txr"]:
                        error_msg: str = "Wrong Insertion Data. NDC: {} and FNDC_TXR: {}.".format(data["ndc"],
                                                                                                  fndc_txr1)
                        logger.error(error_msg)
                        error_msg_list.append(error_msg)
                    else:
                        error_msg: str = "Same NDC {} corresponds to different FNDC_TXR. Inventory FNDC_TXR: {} & " \
                                         "Consumed FNDC_TXR: {}.".format(data["ndc"], data["fndc_txr"], fndc_txr1)
                        logger.error(error_msg)
                        error_msg_list.append(error_msg)
                check_data_dict.pop(data["ndc"])

        for ndc in check_data_dict:
            for fndc_txr2 in check_data_dict[ndc]:
                result_list.append(check_data_dict[ndc][fndc_txr2])

        return result_list, error_msg_list
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def local_inventory_db_update(local_di_insert_data: Optional[List[Dict[str, Any]]] = None,
                              local_di_txn_data: Optional[List[Dict[str, Any]]] = None,
                              local_di_update_data: Optional[Dict[str, Dict[str, Any]]] = None,
                              local_di_po_data: Optional[List[Dict[str, Any]]] = None) -> bool:
    """
    Function to update the database tables corresponding to the Local Drug Inventory.
    """
    try:
        # insert the data in the LocalDIData table
        if local_di_insert_data:
            local_di_insert_inventory_data(data_list=local_di_insert_data)

        # update the qty in the LocalDIData table by ndc
        if local_di_update_data:
            for ndc in local_di_update_data:
                local_di_update_inventory_by_ndc(update_dict=local_di_update_data[ndc], ndc=ndc)

        # insert the data in the LocalDITransaction table
        if local_di_txn_data:
            local_di_insert_txn_data(data_list=local_di_txn_data)

        # insert the data in the LocalDIPOData table
        if local_di_po_data:
            local_di_insert_po_data(data_list=local_di_po_data)

        return True
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def local_di_update_brand_flag() -> str:
    """
    Checks and updates the brand-flag of the available NDCs in the Local Drug Inventory from ElitePBM.
    """
    local_di_dict: Dict[str, str] = dict()
    local_di_txr_set: Set[int] = set()
    update_dict: Dict[str, Dict[str, str]] = dict()
    try:
        # get the data of ndc and corresponding brand_flag in the local drug inventory.
        local_di_data: List[Any] = local_di_get_inventory_data()
        if not local_di_data:
            return create_response(SUCCESS_RESPONSE)

        for record in local_di_data:
            local_di_dict[record["ndc"]] = record["brand_flag"]
            local_di_txr_set.add(int(record["txr"]))

        if len(local_di_txr_set) > EPBM_TXR_LIST_LIMIT:
            no_of_chunks: int = math.ceil(len(local_di_txr_set) / EPBM_TXR_LIST_LIMIT)
            for txr_list in numpy.array_split(list(local_di_txr_set), no_of_chunks):
                local_di_dict, update_dict = get_brand_from_inventory_by_txr(ndc_brand_dict=local_di_dict,
                                                                             txr_list=[int(txr) for txr in txr_list],
                                                                             update_dict=update_dict)

        else:
            local_di_dict, update_dict = get_brand_from_inventory_by_txr(ndc_brand_dict=local_di_dict,
                                                                         txr_list=list(local_di_txr_set),
                                                                         update_dict=update_dict)
        if len(local_di_dict) > 0:
            no_of_chunks: int = math.ceil(len(local_di_dict) / EPBM_NDC_LIST_LIMIT)
            for ndc_list in numpy.array_split(list(local_di_dict.keys()), no_of_chunks):
                local_di_dict, update_dict = get_brand_from_inventory_by_ndc(ndc_brand_dict=local_di_dict,
                                                                             ndc_list=[str(ndc) for ndc in ndc_list],
                                                                             update_dict=update_dict)
        elif len(local_di_dict) > 0:
            local_di_dict, update_dict = get_brand_from_inventory_by_ndc(ndc_brand_dict=local_di_dict,
                                                                         ndc_list=list(local_di_dict.keys()),
                                                                         update_dict=update_dict)

        if update_dict:
            local_inventory_db_update(local_di_update_data=update_dict)

        return create_response(SUCCESS_RESPONSE)
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
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_brand_from_inventory_by_txr(ndc_brand_dict: Dict[str, str], txr_list: List[int],
                                    update_dict: Dict[str, Dict[str, str]]) -> Tuple[Dict[str, str],
                                                                                     Dict[str, Dict[str, str]]]:
    """
    Fetches the brand flag for the list of txr and returns the update_dict where the brand flags doesn't match.
    """
    try:
        inventory_data: List[Dict[str, Any]] = get_current_inventory_data(txr_list=txr_list,
                                                                          qty_greater_than_zero=False)
        if inventory_data:
            for data in inventory_data:
                if data["ndc"] in ndc_brand_dict:

                    inventory_brand_flag: Optional[str] = None
                    if "brand" in data:
                        if data["brand"] == "G":
                            inventory_brand_flag = GENERIC_FLAG
                        elif data["brand"] == "B":
                            inventory_brand_flag = BRAND_FLAG
                        elif data["brand"] == "N":
                            inventory_brand_flag = NON_DRUG_FLAG

                    curr_brand_flag = ndc_brand_dict[data["ndc"]]

                    # remove the ndc from the ndc_brand_dict
                    ndc_brand_dict.pop(data["ndc"])

                    # if the brand flags are not same add to the update_dict
                    if inventory_brand_flag != curr_brand_flag:
                        update_dict[data["ndc"]] = {"brand_flag": inventory_brand_flag}

        return ndc_brand_dict, update_dict

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
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_brand_from_inventory_by_ndc(ndc_brand_dict: Dict[str, str], ndc_list: List[str],
                                    update_dict: Dict[str, Dict[str, str]]) -> Tuple[Dict[str, str],
                                                                                     Dict[str, Dict[str, str]]]:
    """
    Fetches the brand flag for the list of txr and returns the update_dict where the brand flags doesn't match.
    """
    try:
        inventory_data: Dict[str, Dict[str, Any]] = get_data_by_ndc_from_drug_inventory(ndc_list=ndc_list)
        if inventory_data:
            for ndc in inventory_data:
                if ndc in ndc_brand_dict:

                    inventory_brand_flag: Optional[str] = None
                    if "brand" in inventory_data[ndc]:
                        if inventory_data[ndc]["brand"] == "G":
                            inventory_brand_flag = GENERIC_FLAG
                        elif inventory_data[ndc]["brand"] == "B":
                            inventory_brand_flag = BRAND_FLAG
                        elif inventory_data[ndc]["brand"] == "N":
                            inventory_brand_flag = NON_DRUG_FLAG

                    curr_brand_flag = ndc_brand_dict[ndc]

                    # remove the ndc from the ndc_brand_dict
                    ndc_brand_dict.pop(ndc)

                    # if the brand flags are not same add to the update_dict
                    if inventory_brand_flag != curr_brand_flag:
                        update_dict[ndc] = {"brand_flag": inventory_brand_flag}

        return ndc_brand_dict, update_dict

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
        logger.error(e, exc_info=True)
        raise e
