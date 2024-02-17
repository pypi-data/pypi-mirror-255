from typing import Tuple

from peewee import InternalError, IntegrityError, DataError

import settings
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response
from src import constants
from src.dao.rph_verification_dao import db_verify_packlist_by_company, db_verify_packlist_by_system, rph_init_call_ips, \
    rph_get_alert_from_ips, mark_rph_status_in_ips, get_notes_from_ips_dao
from src.exc_thread import ExcThread
from src.exceptions import PharmacySoftwareResponseException, PharmacySoftwareCommunicationException, \
    TokenMissingException, InvalidUserTokenException
from src.service.misc import get_token, get_current_user

logger = settings.logger


def get_company_user_id_from_token() -> Tuple[int, int, str]:
    """
    Returns a Company ID based on the token received during API call from IPS

    Returns: tuple(bool, int) --> boolean value returns False for any error with Error ID.
            Else it returns True with Company ID
    """
    try:
        # fetch company_id based on token
        token = get_token()
        if not token:
            logger.info("process_rx: token not found")
            raise TokenMissingException

        logger.info("process_rx- Fetched token: " + str(token) + ", Now fetching user_details")
        current_user = get_current_user(token)
        logger.info("process_rx: user_info- {} for token - {}".format(current_user, token))
        if not current_user:
            logger.info("process_rx: no user found for token - {}".format(token))
            raise InvalidUserTokenException

        return current_user["company_id"], current_user["id"], current_user["ips_user_name"]
    except TokenMissingException as e:
        logger.error(e, exc_info=True)
        raise TokenMissingException
    except InvalidUserTokenException as e:
        logger.error(e, exc_info=True)
        raise InvalidUserTokenException
    except Exception as e:
        logger.error(e, exc_info=True)
        raise Exception


@log_args_and_response
def start_rph_check(pack_data):
    try:
        pack_id: int = pack_data.get("pack_id", 0)
        company_id: int = pack_data.get("company_id", 0)
        system_id: int = pack_data.get("system_id", 0)
        # valid_pack_list: bool = False

        if company_id == 0 or pack_id == 0 or system_id == 0:
            return error(1001, "Missing Parameter(s): company_id or pack_id or system_id.")

        # -------------- Fetch Company ID based on Token --------------
        company_id, token_user_id, token_user_name = get_company_user_id_from_token()
        valid_pack_list = db_verify_packlist_by_company(pack_id=pack_id, company_id=company_id)

        if not valid_pack_list:
            return error(1026)

        valid_pack_list = db_verify_packlist_by_system(pack_ids=[pack_id], system_id=system_id)
        if not valid_pack_list:
            return error(1014)

        t = ExcThread([], name='ips_rphinitcall',
                      target=rph_init_call_ips,
                      args=(pack_id, company_id, token_user_name))
        t.start()
        # rph_init_call_ips(pack_id=pack_id, company_id=company_id, ips_username=token_user_name)
        logger.info("After Thread Call..")

        return create_response(settings.SUCCESS)

    except (PharmacySoftwareResponseException, PharmacySoftwareCommunicationException) as e:
        logger.error("error in start_rph_check {}".format(e))
        return error(7002)
    except TokenMissingException as e:
        logger.error("error in start_rph_check {}".format(e))
        return error(constants.ERROR_CODE_INVALID_TOKEN, str(e))
    except InvalidUserTokenException as e:
        logger.error("error in start_rph_check {}".format(e))
        return error(constants.ERROR_CODE_INVALID_USER_TOKEN, str(e))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in start_rph_check {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("error in start_rph_check {}".format(e))
        return error(2001)


@log_args_and_response
def get_rph_check_details(pack_data):
    try:
        pack_id: int = pack_data.get("pack_id", 0)
        company_id: int = pack_data.get("company_id", 0)
        system_id: int = pack_data.get("system_id", 0)
        # valid_pack_list: bool = False
        # ips_response: bool = False

        if company_id == 0 or pack_id == 0 or system_id == 0:
            return error(1001, "Missing Parameter(s): company_id or pack_id or system_id.")

        # -------------- Fetch Company ID based on Token --------------
        company_id, token_user_id, token_user_name = get_company_user_id_from_token()

        valid_pack_list = db_verify_packlist_by_company(pack_id=pack_id, company_id=company_id)
        if not valid_pack_list:
            return error(1026)

        valid_pack_list = db_verify_packlist_by_system(pack_ids=[pack_id], system_id=system_id)
        if not valid_pack_list:
            return error(1014)

        ips_response = rph_get_alert_from_ips(pack_id=pack_id, company_id=company_id, ips_username=token_user_name)
        logger.info("Data Response from IPS: {}".format("Data Found.." if ips_response else "No Data Found..."))

    except PharmacySoftwareCommunicationException as e:
        logger.error("error in get_rph_check_details {}".format(e))
        return error(7002)
    except TokenMissingException as e:
        logger.error("error in get_rph_check_details {}".format(e))
        return error(constants.ERROR_CODE_INVALID_TOKEN, str(e))
    except InvalidUserTokenException as e:
        logger.error("error in get_rph_check_details {}".format(e))
        return error(constants.ERROR_CODE_INVALID_USER_TOKEN, str(e))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_rph_check_details {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("error in get_rph_check_details {}".format(e))
        return error(2001)


@log_args_and_response
def mark_rph_check_status(pack_data):
    try:
        pack_id: int = pack_data.get("pack_id", 0)
        company_id: int = pack_data.get("company_id", 0)
        system_id: int = pack_data.get("system_id", 0)
        rph_action: int = pack_data.get("rph_action", 0)
        reason: str = pack_data.get("reason", "")
        # valid_pack_list: bool = False

        if company_id == 0 or pack_id == 0 or system_id == 0 or rph_action == 0:
            return error(1001, "Missing Parameter(s): company_id or pack_id or system_id or rph_action.")

        # -------------- Fetch Company ID based on Token --------------
        company_id, token_user_id, token_user_name = get_company_user_id_from_token()

        valid_pack_list = db_verify_packlist_by_company(pack_id=pack_id, company_id=company_id)
        if not valid_pack_list:
            return error(1026)

        valid_pack_list = db_verify_packlist_by_system(pack_ids=[pack_id], system_id=system_id)
        if not valid_pack_list:
            return error(1014)

        mark_rph_status_in_ips(pack_id=pack_id, company_id=company_id, ips_username=token_user_name,
                               rph_action=rph_action, reason=reason)

        return create_response(settings.SUCCESS)

    except (PharmacySoftwareResponseException, PharmacySoftwareCommunicationException) as e:
        logger.error("error in mark_rph_check_status {}".format(e))
        return error(7002)
    except TokenMissingException as e:
        logger.error("error in mark_rph_check_status {}".format(e))
        return error(constants.ERROR_CODE_INVALID_TOKEN, str(e))
    except InvalidUserTokenException as e:
        logger.error("error in mark_rph_check_status {}".format(e))
        return error(constants.ERROR_CODE_INVALID_USER_TOKEN, str(e))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in mark_rph_check_status {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("error in mark_rph_check_status {}".format(e))
        return error(2001)


@log_args_and_response
def get_notes_from_ips(pack_data):
    try:
        pack_id: int = pack_data.get("pack_id", 0)
        company_id: int = pack_data.get("company_id", 0)
        system_id: int = pack_data.get("system_id", 0)
        note_type: int = pack_data.get("note_type", 0)
        # valid_pack_list: bool = False

        if company_id == 0 or pack_id == 0 or system_id == 0:
            return error(1001, "Missing Parameter(s): company_id or pack_id or system_id.")

        valid_pack_list = db_verify_packlist_by_company(pack_id=pack_id, company_id=company_id)
        if not valid_pack_list:
            return error(1026)

        valid_pack_list = db_verify_packlist_by_system(pack_ids=[pack_id], system_id=system_id)
        if not valid_pack_list:
            return error(1014)

        # mark_rph_status_in_ips(pack_id=pack_id, company_id=company_id, rph_action=rph_action, reason=reason)
        get_notes_from_ips_dao(pack_id=pack_id, company_id=company_id, note_type=note_type)

        return create_response(settings.SUCCESS)

    except (PharmacySoftwareResponseException, PharmacySoftwareCommunicationException) as e:
        logger.error("error in get_notes_from_ips {}".format(e))
        return error(7002)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_notes_from_ips {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("error in get_notes_from_ips {}".format(e))
        return error(2001)
