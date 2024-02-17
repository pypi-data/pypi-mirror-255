import json
import logging
from typing import Any, Optional, Tuple, Dict, List

import settings
from dosepack.utilities.utils import call_webservice, log_args_and_response
from src import constants
from src.exceptions import APIFailureException

logger = logging.getLogger("root")


@log_args_and_response
def auth_api_call(api_name: str, request_type: str, parameters: Any) -> Tuple[bool,
                                                                              Any]:
    """
    This is to be used to call the auth APIs
    """
    try:
        print("parameters ==> ", parameters)
        status, data = call_webservice(base_url=settings.BASE_URL_AUTH, webservice_url=api_name, parameters=parameters,
                                       request_type=request_type, use_ssl=settings.AUTH_SSL)
        return status, data

    except APIFailureException as e:
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def send_email_for_drug_req_check_failure(company_id: Optional[int] = None, error_details: Optional[str] = None,
                                          current_date: Optional[str] = None, time_zone: Optional[str] = None) -> bool:
    """
    Function to send an email when the drug req check API fails.
    """
    parameters: Dict[str, Any] = dict()
    try:
        if company_id:
            parameters["company_id"] = company_id
        if error_details:
            parameters["error_details"] = error_details
        if current_date:
            parameters["current_date"] = current_date
        elif time_zone:
            parameters["time_zone"] = time_zone

        auth_api_call(api_name=settings.DRUG_REQ_CHECK_FAILURE_EMAIL, request_type="GET", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_for_pending_packs_with_past_delivery_date(company_id: int, pending_packs_data: List[Dict[str, Any]],
                                                         user_ids: List[int]) -> bool:
    """
    Function to send an email when the drug req check API fails.
    """
    try:
        parameters: str = json.dumps({"company_id": company_id,
                                      "pending_packs_data": pending_packs_data,
                                      "user_ids": user_ids})

        auth_api_call(api_name=settings.PACKS_WITH_PAST_DELIVERY_DATE_EMAIL, request_type="POST", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_for_weekly_robot_update(weekly_update_data) -> bool:
    """
    Function to send weekly robot update email.
    """
    try:
        parameters: str = json.dumps(weekly_update_data)

        auth_api_call(api_name=settings.ROBOT_WEEKLY_UPDATE_EMAIL, request_type="POST", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_for_imported_batch_manual_drugs(manual_drug_data) -> bool:
    """
    Function to send an email for list of manual drugs for newly imported batch.
    """
    try:
        parameters: str = manual_drug_data

        auth_api_call(api_name=settings.IMPORTED_BATCH_MANUAL_DRUG_EMAIL, request_type="POST", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_for_same_ndc_diff_txr(company_id: int, error_details: str) -> bool:
    """
    Function to send an email when the drug req check API fails.
    """
    try:
        parameters: str = json.dumps({"company_id": company_id, "message": error_details})

        auth_api_call(api_name=settings.SAME_NDC_DIFF_TXR_EMAIL, request_type="POST", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_for_defective_skip_canister(company_id: int, skip_defective_canister_data) -> bool:
    """
    Function to send an email when the drug req check API fails.
    """
    try:
        for canister in skip_defective_canister_data:
            module_id = canister['skipped_from']
            module_name = None
            for module in constants.SKIPPED_MODULE_NAME:
                if constants.SKIPPED_MODULE_NAME[module] == module_id:
                    module_name = module
            canister['skipped_from'] = module_name
        parameters: str = json.dumps({"company_id": company_id,
                                      "skip_defective_canister_data": skip_defective_canister_data})

        logger.info("Inside send_email_for_defective_skip_canister, parameters are {}".format(parameters))

        auth_api_call(api_name=settings.SKIPPED_DEFECTIVE_CANISTER_DETAILS_EMAIL,
                      request_type="POST", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_mismatched_auto_and_manual_drug_shapes(mismatched_shapes_drug_data):
    """
    Function to send an email when the auto fetched and manually fetched drug shapes are different.
    """
    try:
        parameters: str = json.dumps({"mismatched_shapes_drug_data": mismatched_shapes_drug_data})

        logger.info("Inside send_email_mismatched_auto_and_manual_drug_shapes, parameters are {}".format(parameters))

        auth_api_call(api_name=settings.MISMATCHED_AUTO_AND_MANUAL_DRUG_SHAPE_EMAIL, request_type="POST",
                      parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_for_pill_combination_in_given_length_width_range(pill_combination_data) -> bool:
    """
    Function to send an email for list of manual drugs for newly imported batch.
    """
    try:
        parameters: str = json.dumps(pill_combination_data)

        auth_api_call(api_name=settings.PILL_COMBINATION_IN_GIVEN_LENGTH_WIDTH_RANGE, request_type="POST", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_for_pvs_detection_problem_classification(pvs_detection_data) -> bool:
    """
    Function to send weekly robot update email.
    """
    try:
        parameters: str = json.dumps(pvs_detection_data)

        auth_api_call(api_name=settings.PVS_DETECTION_EMAIL, request_type="POST", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_for_daily_check_api_failure(api_name, error_details=None, current_date=None, time_zone=None, company_id=None):
    """
    Function to send an email when the shipped canisters check API fails.
    """
    parameters: Dict[str, Any] = dict()
    try:
        if company_id:
            parameters["company_id"] = company_id
        if error_details:
            parameters["error_details"] = error_details
        if current_date:
            parameters["current_date"] = current_date
        elif time_zone:
            parameters["time_zone"] = time_zone
        if api_name:
            parameters["api_name"] = api_name

        auth_api_call(api_name=settings.SHIPPED_CANISTERS_CHECK_FAILURE_EMAIL, request_type="GET", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True



@log_args_and_response
def send_email_for_user_reported_error_of_green_slot(user_error_data) -> bool:
    """
    Function to send weekly robot update email.
    """
    try:
        parameters: str = json.dumps(user_error_data)

        auth_api_call(api_name=settings.USER_REPORTED_ERROR_OF_GREEN_SLOT_MAIL, request_type="POST", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True

@log_args_and_response
def send_email_for_user_reported_error(user_error_data) -> bool:
    """
    Function to send weekly robot update email.
    """
    try:
        parameters: str = json.dumps(user_error_data)

        auth_api_call(api_name=settings.USER_REPORTED_ERROR_MAIL, request_type="POST", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_update_used_consumable_failure(company_id: Optional[int] = None, error_details: Optional[str] = None,
                                          current_date: Optional[str] = None, time_zone: Optional[str] = None) -> bool:
    """
    Function to send an email when the update used consumable API fails.
    """
    try:

        parameters = json.dumps({"company_id": company_id, "error_details": error_details, "current_date": current_date,
                                 "time_zone": time_zone})

        auth_api_call(api_name=settings.UPDATE_USED_CONSUMABLE_FAILURE_EMAIL, request_type="POST", parameters=parameters)

        return True

    except Exception as e:
        logger.error(e)
        return True


@log_args_and_response
def send_email_monthly_consumable_data(company_id: int, total_pack_inventory: list, pack_inventory_data_day_wise: list, start_date: str, end_date: str):
    """
    API to send monthly consumable data email.
    @param company_id:
    @param total_pack_inventory:
    @param pack_inventory_data_day_wise:
    @param start_date:
    @param end_date:
    @return:
    """
    try:
        parameters = json.dumps({"company_id": company_id, "total_pack_inventory": total_pack_inventory, "pack_inventory_data_day_wise": pack_inventory_data_day_wise,
                                 "start_date": start_date, "end_date": end_date})
        auth_api_call(api_name=settings.MONTHLY_CONSUMABLE_DATA_EMAIL, request_type="POST", parameters=parameters)
        return True
    except Exception as e:
        logger.error(e)
        return True

