import json
from typing import Dict, Any, List

from peewee import IntegrityError, InternalError, ProgrammingError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import ips_response, error, remove_sql_injectors
from dosepack.local.lang_us_en import err
from dosepack.utilities.utils import log_args_and_response, get_current_date_time
from dosepack.validation.validate import validate
from src import constants
from src.dao.ext_change_rx_dao import insert_ext_change_rx_data_dao, \
    db_get_pack_details_by_pack_ids, insert_ext_change_rx_details_dao, db_get_pack_ids_by_pack_display_id_dao, \
    db_get_pack_patient_and_file_info, db_get_templates_by_file_and_patient_info, db_get_templates_by_template_info
from src.dao.pack_ext_dao import db_get_templates_by_pharmacy_fill_ids
from src.dao.template_dao import update_template_status_with_template_id
from src.exceptions import TokenMissingException, InvalidUserTokenException
from src.service.ext_change_rx import get_company_user_id_from_token
from src.service.misc import get_userid_by_ext_username
from src.service.pack_ext import update_ext_pack_status

logger = settings.logger


@log_args_and_response
@validate(required_fields=["error_code", "error_desc", "data"])
def ext_template_split_status(data_ips_dict: Dict[str, Any]) -> str:
    error_code: int
    error_desc: str
    template_status: int
    company_id: int
    user_id: int
    pack_rx_data: Dict[str, Any] = dict()
    rx_change_details: List[Dict[str, Any]] = list()

    try:
        logger.info("change_rx_logger_debug_string: Intimation Call with {}".format(data_ips_dict))
        logger.debug("Check Error Code for API Call...")

        error_code = data_ips_dict.get("error_code")
        if error_code:
            if error_code == settings.PROGRESS_TEMPLATE_STATUS:
                logger.debug("API re-triggered because it was previously left unprocessed as Template status was "
                             "In Progress with error code: {}...".format(error_code))
            elif error_code == constants.ERROR_CODE_CONNECTION_ISSUE_WHILE_FILE_SAVING:
                logger.debug("API re-triggered because it was previously left unprocessed due to error code: {}..."
                             .format(error_code))
            elif error_code == constants.ERROR_CODE_DEFAULT:
                logger.debug("Inside the method to fetch the template status...")
            elif error_code == constants.ERROR_CODE_INVALID_USER_IPS_DOSEPACK:
                logger.debug("User was invalid when called earlier")
            elif error_code == constants.INVALID_API_CALL:
                logger.debug("Error code was invalid earlier, try again this time")
            else:
                logger.debug("API triggered with invalid error codes...")
                return error(21002, "Error Code: {}".format(error_code))

        logger.debug("Fetch Company ID based on Token...")
        company_id, user_id, ips_username = get_company_user_id_from_token()
        # If we get ips username in args use it. because token in IPS belongs to one user only..
        if data_ips_dict.get('rx_change_user_name'):
            ips_username = data_ips_dict.get('rx_change_user_name')
            user_info = get_userid_by_ext_username(ips_username, company_id)
            if user_info and 'id' in user_info:
                user_id = user_info['id']

        pack_rx_data = data_ips_dict.get("data", dict())
        if not pack_rx_data:
            logger.error("empty Pack Dictionary...")
            return error(5008)

        logger.debug("Fetch the Pack Display ID and Rx Change Dictionary...")
        pack_display_ids: List[int] = pack_rx_data["pack_display_id"]
        packs_delivered: List[int] = pack_rx_data["packs_delivered"]
        # cycle_change_delivered_packs: List[int] = pack_rx_data["cycle_change_delivered_packs"]
        rx_change_details = pack_rx_data["rx_change_details"]

        # this flow of bypassing will not be used after partial delivered change rx case
        # if packs_delivered:
        #     """For now, if we receive any delivered packs, we wont accept intimation call and
        #      all the other packs will be treated as normal.
        #     User has to delete it from the IPS and delete sync will be triggered just like existing flow
        #     """
        #     logger.info(
        # "In ext_template_split_status:   received packs
        #         delivered so bypassing changeRx flow. Intimation data = {}".format(
        #             data_ips_dict))
        #
        #     return ips_response(settings.BYPASSING_INTIMATION_CODE, "General Change Rx Delivered Packs Flow.")
        #     # pack_display_ids = pack_display_ids + packs_delivered

        # Get the Template status for them
        template_status = check_pack_template_status(pack_display_ids=pack_display_ids,
                                                     rx_change_details=rx_change_details, company_id=company_id,
                                                     user_id=user_id, ips_username=ips_username,
                                                     packs_delivered=packs_delivered)

        return ips_response(template_status, err.get(template_status, "General Change Rx Flow."))

    except TokenMissingException as e:
        logger.error(e, exc_info=True)
        e = remove_sql_injectors(str(e))
        return error(constants.ERROR_CODE_INVALID_TOKEN, str(e))
    except InvalidUserTokenException as e:
        logger.error(e, exc_info=True)
        e = remove_sql_injectors(str(e))
        return error(constants.ERROR_CODE_INVALID_USER_TOKEN, str(e))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        e = remove_sql_injectors(str(e))
        return error(constants.ERROR_CODE_CONNECTION_ISSUE_WHILE_FILE_SAVING, str(e))
    except ProgrammingError as e:
        logger.error(e, exc_info=True)
        e = remove_sql_injectors(str(e))
        return error(constants.ERROR_CODE_INTERNAL_CHANGE_RX, str(e))
    except Exception as e:
        logger.error(e, exc_info=True)
        e = remove_sql_injectors(str(e))
        return error(constants.ERROR_CODE_INTERNAL_CHANGE_RX, str(e))


@log_args_and_response
def check_pack_template_status(pack_display_ids: List[int], rx_change_details: List[Dict[str, Any]], company_id: int,
                               user_id: int, ips_username: str, packs_delivered: List[int]) -> int:
    pack_ids: Dict[int, int] = dict()
    # template_info: List[Dict[str, Any]] = list()
    template_dict: Dict[int, Any] = dict()
    template_master_pack_data: List[Dict[str, Any]] = list()
    template_master_data: List[Dict[str, Any]] = list()
    file_ids: List[int] = list()
    patient_ids: List[int] = list()
    template_in_progress: bool = False
    ext_change_rx_dict: Dict[str, Any] = dict()
    ext_pack_details_dict: Dict[str, Any] = dict()
    response_dict: Dict[str, Dict[str, Any]] = dict()

    # Default status for SQL Error
    status_code: int = constants.ERROR_CODE_CONNECTION_ISSUE_WHILE_FILE_SAVING

    ext_change_rx_id: int
    ext_change_rx_details_list: List[Dict[str, Any]] = list()
    pack_details: Dict[int, Any] = {}
    pack_status_list: List[int] = []
    pack_id_list_for_change_rx: List[int] = []
    delete_change_rx: bool = False
    template_packs: list = list()

    try:
        logger.info("change_rx_logger_debug_string: check_pack_template_status")

        # template_dict = db_get_templates_by_pharmacy_fill_ids(pharmacy_fill_ids=pack_display_ids,
        #                                                       company_id=company_id)

        # template_info = TempSlotInfo.db_get_temp_data_based_on_pharmacy_fill_ids(pharmacy_fill_ids=pack_display_ids)

        # if not template_dict:
        #     logger.debug("No Templates are present to proceed further with Change Rx...")
        #     return constants.ERROR_CODE_NO_TEMPLATES_FOUND

        # template_master_data = db_get_templates_by_template_info(template_dict)

        logger.debug("change_rx_logger_debug_string: "
                     "Check if Template processing is already done for Pack IDs: {}...".format(pack_display_ids))
        pack_ids = db_get_pack_ids_by_pack_display_id_dao(pack_display_ids=pack_display_ids, company_id=company_id)
        if pack_ids and len(pack_ids.keys()) != len(pack_display_ids):
            # Found pack which is on template level..
            template_packs = [pack for pack in pack_display_ids if pack not in pack_ids.keys()]

        if pack_ids:
            logger.debug("change_rx_logger_debug_string: "
                         "Get the Template details to fetch their status based on Pack IDs: {}..."
                         .format(pack_display_ids))
            pack_file_patient_dict = db_get_pack_patient_and_file_info(pack_id_list=list(pack_ids.values()))
            for patient_id, file_id_list in pack_file_patient_dict.items():
                patient_ids = [patient_id]
                file_ids = file_id_list

            if patient_ids and file_ids:
                template_master_pack_data = db_get_templates_by_file_and_patient_info(file_ids=file_ids,
                                                                                 patient_ids=patient_ids)
            if not template_master_pack_data:
                logger.debug("change_rx_logger_debug_string: "
                             "No Templates are present to proceed further with Change Rx...")
                return constants.ERROR_CODE_NO_TEMPLATES_FOUND
        if template_packs or not pack_ids:

            template_dict = db_get_templates_by_pharmacy_fill_ids(
                pharmacy_fill_ids=template_packs if pack_ids else pack_display_ids, company_id=company_id)
            if not template_dict:
                logger.debug("change_rx_logger_debug_string: "
                             "No Templates are present to proceed further with Change Rx...")
                return constants.ERROR_CODE_NO_TEMPLATES_FOUND

            template_master_data = db_get_templates_by_template_info(template_dict)

        with db.transaction():
            if pack_ids:
                logger.info("change_rx_logger_debug_string: check_pack_template_status: Templates are already processed")

                for template in template_master_pack_data:
                    current_template = template['id']
                    logger.debug("change_rx_logger_debug_string: Insert data into ext_change_rx table...")
                    ext_change_rx_dict = {"current_template": template["id"],
                                          "ext_action": settings.PENDING_CHANGE_RX_TEMPLATE_STATUS_PACK,
                                          "company_id": company_id}
                    ext_change_rx_id = insert_ext_change_rx_data_dao(ext_change_rx_dict=ext_change_rx_dict)
                    # missing something

                    logger.info("change_rx_logger_debug_string: Get all the packs by linking Pack Header "
                                "and Pack Details...")
                    pack_display_list_for_change_rx, pack_details = \
                        db_get_pack_details_by_pack_ids(pack_ids=list(pack_ids.values()),
                                                        packs_delivered=packs_delivered, current_template=current_template)

                    logger.info("change_rx_logger_debug_string Process Delete operation for Pack Display ID: {} "
                                "through ext_pack_details "
                                "table...".format(pack_display_list_for_change_rx))

                    ext_pack_details_dict = {"pack_display_ids": pack_display_list_for_change_rx,
                                             "technician_fill_status": constants.EXT_PACK_STATUS_CODE_DELETED,
                                             "technician_user_name": ips_username,
                                             "technician_fill_comment": constants.DELETE_REASON_EXT_CHANGE_RX,
                                             "user_id": user_id,
                                             "company_id": company_id,
                                             "change_rx": True,
                                             "ext_change_rx_id": ext_change_rx_id,
                                             "delivered_packs": packs_delivered}
                    response_dict = json.loads(update_ext_pack_status(ext_pack_details_dict))
                    status_code = response_dict.get("code", constants.ERROR_CODE_CONNECTION_ISSUE_WHILE_FILE_SAVING)
                    if status_code != constants.IPS_STATUS_CODE_OK:
                        logger.info("change_rx_logger_debug_string: Issue with processing delete operation for "
                                    "Pack Display ID: {}. "
                                    "Received Status = {}".format(pack_display_list_for_change_rx, status_code))
                        return status_code

                    for rx_change_iteration in rx_change_details:
                        logger.info("change_rx_logger_debug_string: Prepare ext_change_rx_details Dictionary.")

                        rx_change_user_name = rx_change_iteration["rx_change_user_name"]
                        user_info = get_userid_by_ext_username(rx_change_user_name, company_id)
                        if user_info and "id" in user_info:
                            ext_user_id = user_info["id"]
                        else:
                            logger.error("change_rx_logger_debug_string: Error while fetching user_info for rx_change_user_name {}".
                                         format(rx_change_user_name))
                            return constants.ERROR_CODE_INVALID_USER_IPS_DOSEPACK

                        logger.info("change_rx_logger_debug_string: userinfo: {} for ips_username: {}".format(user_info, rx_change_user_name))

                        ext_change_rx_details_list.append({
                            "ext_change_rx_id": ext_change_rx_id,
                            "ext_pharmacy_rx_no": rx_change_iteration["pharmacy_rx_no"],
                            "action_id": rx_change_iteration["status"],
                            "ext_comment": rx_change_iteration["rx_change_comment"],
                            "created_date": rx_change_iteration["rx_change_datetime"],
                            "created_by": ext_user_id
                        })

                    if ext_change_rx_details_list:
                        logger.info("change_rx_logger_debug_string: Insert into ext_change_rx_details...")
                        insert_ext_change_rx_details_dao(ext_change_rx_details_list)

                logger.info("change_rx_logger_debug_string: Return back to IPS to trigger New Template...")
                if template_packs and template_master_data:
                    logger.info(
                        "change_rx_logger_debug_string: check_pack_template_status: Template Found with Packs {} ".
                        format(template_master_data))
                    for template in template_master_data:
                        if template["status"] == settings.PROGRESS_TEMPLATE_STATUS:
                            logger.info(
                                "change_rx_logger_debug_string: In Progress Template found for Patient ID: {}. "
                                "Return back to IPS to re-trigger "
                                "the process...".format(template["id"]))
                            return settings.PROGRESS_TEMPLATE_STATUS
                        # Delete old template
                        update_dict = {"status": settings.UNGENERATED_TEMPLATE_STATUS,
                                       "modified_by": user_id,
                                       "modified_date": get_current_date_time()}
                        update_template_status_with_template_id(template['id'], update_dict)
                        ext_change_rx_dict = {"current_template": template["id"],
                                              "ext_action": settings.TEMPLATE_DELETED_DRUE_TO_CHANGE_RX,
                                              "company_id": company_id}
                        insert_ext_change_rx_data_dao(ext_change_rx_dict)

                return settings.DONE_TEMPLATE_STATUS

            if template_packs or not pack_ids:
                logger.info("change_rx_logger_debug_string: check_pack_template_status: Templates are not processed..")

                for template in template_master_data:
                    if template["status"] == settings.PROGRESS_TEMPLATE_STATUS:
                        logger.info("change_rx_logger_debug_string: In Progress Template found for Patient ID: {}."
                                    " Return back to IPS to re-trigger "
                                    "the process...".format(template["id"]))
                        template_in_progress = True
                        break

                if template_in_progress:
                    return settings.PROGRESS_TEMPLATE_STATUS
                else:
                    if len(template_master_data) > 1:
                        logger.info(
                            "change_rx_logger_debug_string: check_pack_template_status: Multiple template found: {} ".
                            format(template_master_data))
                        # delete all template
                        for template in template_master_data:
                            update_dict = {"status": settings.UNGENERATED_TEMPLATE_STATUS,
                                           "modified_by": user_id,
                                           "modified_date": get_current_date_time()}
                            update_template_status_with_template_id(template['id'], update_dict)
                            ext_change_rx_dict = {"current_template": template["id"],
                                                  "ext_action": settings.TEMPLATE_DELETED_DRUE_TO_CHANGE_RX,
                                                  "company_id": company_id}
                            insert_ext_change_rx_data_dao(ext_change_rx_dict)

                        return settings.DONE_TEMPLATE_STATUS

                    logger.info(
                        "change_rx_logger_debug_string: check_pack_template_status: Pending Templates found to "
                        "process Change Rx for Pack IDs: {}...".
                        format(pack_display_ids))

                    # logger.debug("Pending Templates found to process Change Rx for Pack IDs: {}...".
                    #              format(pack_display_ids))
                    return settings.PENDING_TEMPLATE_STATUS if not pack_ids else settings.DONE_TEMPLATE_STATUS

    except ProgrammingError as e:
        logger.error(e, exc_info=True)
        e = remove_sql_injectors(str(e))
        raise
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise
