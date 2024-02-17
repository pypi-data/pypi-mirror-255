from peewee import InternalError, IntegrityError

import settings
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import difference_between_timestamps, log_args_and_response, log_args
from dosepack.validation.validate import validate
from src.dao.session_dao import get_session_param_dao, get_session_module_meta_dao, create_session, \
    create_and_update_session, get_status_and_create_meta, update_session, create_or_update_session

logger = settings.logger


@log_args
@validate(required_fields=["module_type_id", "screen_sequence", "company_id"])
def get_session_param(args: dict) -> dict:
    """
    @desc: get the session-data details from SessionModuleMaster table
    @param args: dictionary
    @return: dictionary
    """
    try:
        module_type_id = args.get("module_type_id")
        screen_sequence = args.get("screen_sequence")
        company_id = args.get("company_id")
        # obtain the session_module_master data based on given type_id and screen_sequence
        session_param = get_session_param_dao(module_type_id=module_type_id, screen_sequence=screen_sequence,
                                              company_id=company_id)

        return create_response(session_param)

    except TypeError as e:
        logger.error(e)
        raise

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_session_param {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in get_session_param {}".format(e))
        return error(1000, "Error in get_session_param: " + str(e))


@log_args_and_response
@validate(required_fields=["module_id", "identifier_key", "identifier_value", "start_time", "end_time", "user_id",
                           "is_first", "is_last", "system_id", "company_id"])
def post_session_data(session_dict: dict) -> dict:
    """
    @desc: Post data to Session Table for session-data api
    @param session_dict: dictionary
    @return:json
    """
    logger.debug("Inside post_session_data")
    session_module_id = session_dict["module_id"]
    identifier_key = session_dict["identifier_key"]
    identifier_value = session_dict["identifier_value"]
    start_time = session_dict["start_time"]
    end_time = session_dict["end_time"]
    user_id = session_dict["user_id"]
    system_id = session_dict["system_id"]
    company_id = session_dict["company_id"]
    flag_is_first = bool(session_dict["is_first"])
    flag_is_last = bool(session_dict["is_last"])


    try:
        # get the difference in seconds between given start time and end time
        active_time: int = difference_between_timestamps(start_time=start_time, end_time=end_time)

        # get the session_module_meta_id for post session data
        session_module_meta_id = get_session_module_meta_dao(session_module_id=session_module_id)
        # creates single session and updates the same for the null identifier_value
        if identifier_value is None:
            session_create_or_update_status = create_or_update_session(session_module_id=session_module_id,
                                     identifier_key=identifier_key,
                                     start_time=start_time,
                                     end_time=end_time,
                                     active_time=active_time,
                                     user_id=user_id,
                                     system_id=system_id,
                                     company_id=company_id)
            if session_create_or_update_status:
                return create_response(settings.SUCCESS_RESPONSE)
            else:
                return error(1040)
        # creates a new session
        if flag_is_first is True and flag_is_last is True:
            session_create_status = create_session(session_module_id=session_module_id,
                                                   identifier_key=identifier_key,
                                                   identifier_value=identifier_value,
                                                   start_time=start_time,
                                                   end_time=end_time,
                                                   active_time=active_time,
                                                   user_id=user_id,
                                                   system_id=system_id,
                                                   company_id=company_id,
                                                   session_module_meta_id=session_module_meta_id)

            if session_create_status:
                return create_response(settings.SUCCESS_RESPONSE)
            else:
                return error(1040)

        # creates a session and updates identifier value when flag is_first=True and flag_is_last=False
        elif flag_is_first is True and flag_is_last is False:
            session_status_is_last_false = create_and_update_session(session_module_id=session_module_id,
                                                                     identifier_key=identifier_key,
                                                                     identifier_value=identifier_value,
                                                                     start_time=start_time,
                                                                     active_time=active_time,
                                                                     user_id=user_id,
                                                                     system_id=system_id,
                                                                     company_id=company_id)

            if session_status_is_last_false:
                return create_response(settings.SUCCESS_RESPONSE)
            else:
                return error(1040)

        # obtains the existing session and creates meta for the same.
        elif flag_is_first is False and flag_is_last is True:
            meta_status = get_status_and_create_meta(session_module_id=session_module_id,
                                                     session_module_meta_id=session_module_meta_id,
                                                     identifier_key=identifier_key,
                                                     identifier_value=identifier_value,
                                                     active_time=active_time,
                                                     end_time=end_time,
                                                     user_id=user_id,
                                                     system_id=system_id,
                                                     company_id=company_id)
            if meta_status:
                return create_response(settings.SUCCESS_RESPONSE)
            else:
                return error(1040)

        # updates the existing session with active time
        else:
            session_update_status = update_session(session_module_id=session_module_id,
                                                   identifier_key=identifier_key,
                                                   user_id=user_id, system_id=system_id, company_id=company_id,
                                                   active_time=active_time)

            if session_update_status:
                return create_response(settings.SUCCESS_RESPONSE)
            else:
                return error(1040)



    except (InternalError, IntegrityError) as e:
        logger.error("error in post_session_data {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in post_session_data {}".format(e))
        return error(1000, "Error in post_session_data: " + str(e))
