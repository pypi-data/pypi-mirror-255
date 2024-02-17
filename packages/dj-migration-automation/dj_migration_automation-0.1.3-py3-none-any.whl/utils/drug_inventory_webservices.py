import logging
from typing import Dict, Any, List, Tuple, Optional

from celery.worker.state import requests

import requests

import settings
from dosepack.utilities.utils import call_webservice, log_args, log_args_and_response
from src.dao.company_setting_dao import db_get_elite_token, db_update_elite_token
from src.exceptions import (APIFailureException, DrugInventoryInternalException, DrugInventoryValidationException,
                            TokenFetchException)

logger = logging.getLogger("root")


@log_args_and_response
def drug_inventory_api_call(api_name: str, request_type: str, parameters: Any, bypass_call: bool = None,
                            query_string_parameter=None, use_ssl=settings.ELITE_ON_SSL):
    """
    This is to be used to call the drug inventory APIs
    """
    try:
        # parameters for Login API
        login_parameters = {"username": settings.EPBM_USERNAME,
                            "password": settings.EPBM_PASSWORD,
                            "code": settings.EPBM_CODE}
        if settings.USE_TOKEN_REUSE:
            # first we try using token stored in database
            token = db_get_elite_token()
            status, response_data = call_webservice(base_url=settings.EPBM_BASE_URL, webservice_url=api_name,
                                                    request_type=request_type,
                                                    headers={'x-token': "{}".format(token)},
                                                    parameters=parameters, epbm_api=True, timeout=(8, 60),
                                                    query_string_parameter=query_string_parameter, use_ssl=use_ssl)
            logger.info("Status and response of drug_inventory_api_call {}, {}".format(status, response_data))
            if response_data == 401:
                logger.info("Token for Elite is expired, refreshing token with updated value")
                # call Login webservice to get token
                status, data = call_webservice(base_url=settings.EPBM_BASE_URL,
                                               webservice_url=settings.DRUG_INVENTORY_LOGIN,
                                               parameters=login_parameters, request_type="POST", epbm_api=True,
                                               timeout=(8, 60),
                                               query_string_parameter=query_string_parameter, use_ssl=use_ssl)
                logger.info("Status and response of drug_inventory_api_call for login {}, {}".format(status, data))

                if status and data["status"] and data["status"] == settings.SUCCESS_RESPONSE:
                    token = data["data"]["result"]["token"]
                    # we will update elite token in database
                    status = db_update_elite_token(token)
                    status, response_data = call_webservice(base_url=settings.EPBM_BASE_URL, webservice_url=api_name,
                                                            request_type=request_type,
                                                            headers={'x-token': "{}".format(token)},
                                                            parameters=parameters, epbm_api=True,
                                                            query_string_parameter=query_string_parameter, use_ssl=use_ssl)
                    logger.info("Status and response of drug_inventory_api_call {}, {}".format(status, response_data))
                    if response_data["status"] == settings.SUCCESS_RESPONSE:
                        return True, response_data["data"]["result"]
                    elif response_data["data"]["messages"]:
                        if response_data["data"]["messages"][0].get("code", None) == "GeneralValidation":
                            logger.error("Error in drug_inventory_api_call {}".format(response_data))
                            raise DrugInventoryValidationException(response_data["data"]["messages"])
                    else:
                        logger.error("Error in drug_inventory_api_call {}".format(response_data))
                        raise APIFailureException(response_data["data"]["messages"])
                else:
                    logger.error("Error while fetching the token from ElitePBM in drug_inventory_api_call {}".format(data))
                    if bypass_call:
                        return True, []
                    raise TokenFetchException(data["data"]["messages"])
            elif bypass_call and not status and isinstance(response_data, requests.exceptions.ConnectionError):
                logger.info("In drug_adjustment_api_call. ConnectionError: Bypassing call")
                return True, []
            elif response_data["status"] == settings.SUCCESS_RESPONSE:
                return True, response_data["data"]["result"]

            elif response_data["data"]["messages"]:
                if response_data["data"]["messages"][0].get("code", None) == "GeneralValidation":
                    logger.error("Error in drug_inventory_api_call {}".format(response_data))
                    raise DrugInventoryValidationException(response_data["data"]["messages"])
            else:
                logger.error("Error in drug_inventory_api_call {}".format(response_data))
                raise APIFailureException(response_data["data"]["messages"])
        else:
            # call Login webservice to get token
            status, data = call_webservice(base_url=settings.EPBM_BASE_URL,
                                           webservice_url=settings.DRUG_INVENTORY_LOGIN,
                                           parameters=login_parameters, request_type="POST", epbm_api=True,
                                           timeout=(8, 60),
                                           query_string_parameter=query_string_parameter, use_ssl=use_ssl)
            logger.info("Status and response of drug_inventory_api_call for login {}, {}".format(status, data))

            if status and data["status"] and data["status"] == settings.SUCCESS_RESPONSE:
                token = data["data"]["result"]["token"]

                status, response_data = call_webservice(base_url=settings.EPBM_BASE_URL, webservice_url=api_name,
                                                        request_type=request_type,
                                                        headers={'x-token': "{}".format(token)},
                                                        parameters=parameters, epbm_api=True,
                                                        query_string_parameter=query_string_parameter, use_ssl=use_ssl)
                logger.info("Status and response of drug_inventory_api_call {}, {}".format(status, response_data))

                if response_data["status"] == settings.SUCCESS_RESPONSE:
                    call_webservice(base_url=settings.EPBM_BASE_URL, parameters=None, epbm_api=True,
                                    webservice_url=settings.DRUG_INVENTORY_LOGOUT,
                                    headers={'x-token': "{}".format(token)}, use_ssl=use_ssl)
                    return True, response_data["data"]["result"]

                elif response_data["data"]["messages"][0]["code"] == "GeneralValidation":
                    logger.error("Error in drug_inventory_api_call {}".format(response_data))
                    raise DrugInventoryValidationException(response_data["data"]["messages"])

                else:
                    logger.error("Error in drug_inventory_api_call {}".format(response_data))
                    raise APIFailureException(response_data["data"]["messages"])

            else:
                logger.error("Error while fetching the token from ElitePBM in drug_inventory_api_call {}".format(data))
                if bypass_call:
                    return True, []
                raise TokenFetchException(data["data"]["messages"])

    except APIFailureException as e:
        logger.error("Error in drug_inventory_api_call {}".format(e))
        raise e
    except DrugInventoryValidationException as e:
        logger.error("Error in drug_inventory_api_call {}".format(e))
        raise e
    except TokenFetchException as e:
        logger.error("Error in drug_inventory_api_call {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error exception in drug_inventory_api_call {}".format(e))
        raise DrugInventoryInternalException(e)


@log_args_and_response
def post_request_data_to_drug_inventory(created_list: List[Dict[str, Any]], deleted_list: List[Dict[str, Any]],
                                        updated_list: List[Dict[str, Any]], bypass_call: bool) -> Dict[str, Any]:
    """
    This function posts the request data to the drug_inventory.
    """
    post_data: Dict[str, Any] = dict()
    status: bool
    inventory_resp: Dict[str, Any]
    try:
        post_data["created"] = created_list
        post_data["updated"] = updated_list
        post_data["deleted"] = deleted_list
        status, inventory_resp = drug_inventory_api_call(api_name=settings.DRUG_INVENTORY_POST_BATCH_DATA,
                                                         parameters=post_data, request_type="POST", bypass_call = bypass_call)
        if not status:
            raise APIFailureException(inventory_resp)
        if status and bypass_call and not inventory_resp:
            return {}
        return inventory_resp

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
def get_data_by_ndc_from_drug_inventory(ndc_list: List[str],
                                        bottle_qty: Optional[bool] = False) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    This function fetches the drug data for the given NDC from Drug Inventory.
    """
    post_data: Dict[str, List[int]] = dict()
    try:
        post_data["ndc"] = [int(ndc) for ndc in ndc_list]
        status, inventory_resp = drug_inventory_api_call(api_name=settings.DRUG_INVENTORY_FETCH_DRUG_DATA,
                                                         parameters=post_data, request_type="POST")
        if not status:
            raise APIFailureException(inventory_resp)
        if inventory_resp:
            return {data["ndc"]: data for data in inventory_resp}
        else:
            return None

    except APIFailureException as e:
        logger.error(e)
        if bottle_qty:
            return None
        else:
            raise e
    except DrugInventoryValidationException as e:
        logger.error(e)
        if bottle_qty:
            return None
        else:
            raise e
    except DrugInventoryInternalException as e:
        logger.error(e)
        if bottle_qty:
            return None
        else:
            raise e
    except TokenFetchException as e:
        logger.error(e)
        if bottle_qty:
            return None
        else:
            raise e
    except Exception as e:
        logger.error(e)
        if bottle_qty:
            return None
        else:
            raise e


@log_args_and_response
def get_current_inventory_data(txr_list: Optional[List[int]] = None, ndc_list: Optional[List[int]] = None,
                               qty_greater_than_zero: Optional[bool] = True) -> List[Dict[str, Any]]:
    """
    Fetches the available qty from the drug inventory for the given list of txr or ndc.
    """
    post_data: Dict[str, Any] = dict()
    status: bool
    inventory_resp: List[Dict[str, Any]] = list()
    try:
        if settings.USE_EPBM:
            post_data["ndc"] = ndc_list if ndc_list else []
            post_data["cfi"] = txr_list if txr_list else []
            post_data["qtyGreaterThenZero"] = qty_greater_than_zero
            status, inventory_resp = drug_inventory_api_call(api_name=settings.DRUG_INVENTORY_CHECK_INVENTORY,
                                                             parameters=post_data, request_type="POST")
            if not status:
                logger.error("Error in get_current_inventory_data {}, {}".format(status, inventory_resp))
                raise APIFailureException(inventory_resp)
        return inventory_resp

    except APIFailureException as e:
        logger.error("Error in get_current_inventory_data {}".format(e))
        raise e
    except TokenFetchException as e:
        logger.error("Error in get_current_inventory_data {}".format(e))
        raise e
    except DrugInventoryValidationException as e:
        logger.error("Error in get_current_inventory_data {}".format(e))
        raise e
    except DrugInventoryInternalException as e:
        logger.error("Error in get_current_inventory_data {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in get_current_inventory_data {}".format(e))
        raise e


@log_args_and_response
def get_po_numbers(start_time: int, end_time: int, department: str, only_ack: Optional[bool] = True) -> List[str]:
    """
    Fetches the list of the PO numbers that received acknowledgements between the start_time and end_time
    for the given department.
    """
    post_data: Dict[str, Any] = dict()
    status: bool
    inventory_resp: List[str]
    try:
        post_data["createdDateFrom"] = start_time
        post_data["createdDateTo"] = end_time
        post_data["department"] = department
        post_data["isAck"] = only_ack
        status, inventory_resp = drug_inventory_api_call(api_name=settings.DRUG_INVENTORY_GET_PO_NUMBERS,
                                                         parameters=post_data, request_type="POST")
        if not status:
            raise APIFailureException(inventory_resp)

        return inventory_resp

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
        raise e


@log_args_and_response
def get_data_by_po_numbers(po_number_list: List[str]) -> List[Dict[str, Any]]:
    """
    Fetches the data corresponding to the given list of the PO numbers.
    """
    post_data: Dict[str, Any] = dict()
    status: bool
    inventory_resp: List[Dict[str, Any]]
    try:
        post_data["poNumber"] = po_number_list
        status, inventory_resp = drug_inventory_api_call(api_name=settings.DRUG_INVENTORY_DATA_BY_PO_NUMBERS,
                                                         parameters=post_data, request_type="POST")
        if not status:
            raise APIFailureException(inventory_resp)
        return inventory_resp

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
        raise e


@log_args_and_response
def fetch_pre_order_data(unique_id: str) -> List[Dict[str, Any]]:
    """
    Fetch the pre-ordered data for the given unique_id.
    """
    post_data: Dict[str, Any] = dict()
    status: bool
    inventory_resp: List[Dict[str, Any]]
    try:
        post_data["uniqueId"] = unique_id
        status, inventory_resp = drug_inventory_api_call(api_name=settings.DRUG_INVENTORY_FETCH_BATCH_DATA,
                                                         parameters=post_data, request_type="POST")
        if not status:
            raise APIFailureException(inventory_resp)
        return inventory_resp
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
        raise e


@log_args_and_response
def post_adjustment_data_to_drug_inventory(created_list: List[Dict[str, Any]], deleted_list: List[Dict[str, Any]],
                                        updated_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    This function posts the drug adjustment request data to the drug_inventory.
    """
    post_data: Dict[str, Any] = dict()
    status: bool
    inventory_resp: Dict[str, Any]
    try:
        post_data["created"] = created_list
        post_data["updated"] = updated_list
        post_data["deleted"] = deleted_list
        status, inventory_resp = drug_inventory_api_call(api_name=settings.DRUG_INVENTORY_POST_DRUG_ADJUSTMENT_DATA,
                                                         parameters=post_data, request_type="POST")
        if not status:
            raise APIFailureException(inventory_resp)
        return inventory_resp

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
def update_drug_inventory_for_same_drug_ndcs(param):
    """
    This function ...
    """
    status: bool
    inventory_resp: Dict[str, Any]
    try:
        status, inventory_resp = drug_inventory_api_call(api_name=settings.DRUG_INVENTORY_DRUG_IN_STOCK,
                                                         parameters=param, request_type="GET")
        if not status:
            raise APIFailureException(inventory_resp)
        return inventory_resp

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
def create_item_vial_generation_for_rts_reuse_pack(param):
    """
    This function call the api of elite which generate the item ids for the RTS Reuse packs
    also this api used for the generation of vial from the RTS pack
    """
    status: bool
    inventory_resp: Dict[str, Any]
    try:
        status, inventory_resp = drug_inventory_api_call(api_name=settings.DRUG_INVENTORY_ITEM_GENERATION,
                                                         parameters=param, request_type="POST")
        if not status:
            raise APIFailureException(inventory_resp)
        return inventory_resp

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
def drug_inventory_general_api(param, query_string_parameter, api_name, api_type):
    """
    This function call the api of elite which generate the item ids for the RTS Reuse packs
    also this api used for the generation of vial from the RTS pack
    """
    status: bool
    inventory_resp: Dict[str, Any]
    try:
        status, inventory_resp = drug_inventory_api_call(api_name=api_name,
                                                         parameters=param, request_type=api_type,
                                                         query_string_parameter=query_string_parameter
                                                         )
        if not status:
            raise APIFailureException(inventory_resp)
        return inventory_resp

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