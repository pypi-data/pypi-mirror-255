from peewee import InternalError, IntegrityError, DataError, fn

import settings
from dosepack.utilities.utils import log_args_and_response, log_args
from src.model.model_pack_details import PackDetails
from src import constants
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_session import Session
from src.model.model_session_meta import SessionMeta
from src.model.model_session_module_master import SessionModuleMaster
from src.model.model_session_module_meta import SessionModuleMeta

logger = settings.logger


@log_args
def get_session_param_dao(module_type_id: int, screen_sequence: int, company_id: int) -> dict:
    """
    This function fetches the details of session
    @param module_type_id: int
    @param screen_sequence: int
    @param company_id: int
    @return dict
    """
    try:
        logger.debug("In get_session_param_dao")
        session_param_response = {}
        # obtain the session_module_master data based on the given parameters
        query = SessionModuleMaster.select(SessionModuleMaster).dicts() \
            .where((SessionModuleMaster.session_module_type_id == module_type_id),
                   (SessionModuleMaster.screen_sequence == screen_sequence),
                   (SessionModuleMaster.company_id == company_id))
        # update the session_param_response dictionary with the query result
        for response in query:
            session_param_response["module_id"] = response["id"]
            session_param_response["session_module_type_id"] = response["session_module_type_id"]
            session_param_response["screen_sequence"] = response["screen_sequence"]
            session_param_response["max_idle_time"] = response["max_idle_time"]
            session_param_response["screen_interaction"] = response["screen_interaction"]

        return session_param_response

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_session_param_dao {}".format(e))
        raise


@log_args
def get_session_meta_value(facility_distribution_id: int = None):
    """
    To calculate the distinct entries for Alternate drug screen
    @param facility_distribution_id: int
    @return: int
    """
    try:
        logger.debug("In get_session_meta_value")
        value = 0
        query = PackRxLink.select(fn.COUNT((fn.DISTINCT(PackRxLink.bs_drug_id))).alias("count")).dicts() \
                           .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                           .join(FacilityDistributionMaster, on=FacilityDistributionMaster.id == PackDetails.facility_dis_id) \
                           .where(FacilityDistributionMaster.id == facility_distribution_id)

        for record in query:
            value = record["count"]

        return value

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_session_meta_value {}".format(e))
        raise e


@log_args
def get_session_module_meta_dao(session_module_id: int) -> int:
    """
    This function fetches the session_module_meta id for the given session_module_id
    @param session_module_id: int
    @return int
    """
    try:
        logger.debug("In get_session_module_meta_dao")
        # obtain the session_module_master id for the given session module id
        session_module_meta_id = SessionModuleMeta.get_session_module_meta_id(session_module_id=session_module_id)
        return session_module_meta_id
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_session_module_meta_dao {}".format(e))
        raise


@log_args_and_response
def create_session(session_module_id: int, session_module_meta_id: int, identifier_key: int, identifier_value: int,
                   start_time: str,
                   end_time: str,
                   active_time: int,
                   user_id: int,
                   system_id: int,
                   company_id: int) -> bool:
    """
    This function creates a session when both flag_is_first and flag_is_last is true
    @param session_module_id: int,
    @param session_module_meta_id: int,
    @param identifier_key: int,
    @param identifier_value: int,
    @param start_time: str,
    @param end_time: str,
    @param active_time: str,
    @param user_id: int,
    @param system_id: int,
    @param company_id: int
    @return bool
    """
    try:
        logger.debug("In create_session")
        start_id = None
        if int(session_module_id) == constants.MODULE_TYPE_SELECT_FACILITY_SCREEN:
            start_id = Session.get_start_id(session_module_id)
            logger.debug(start_id)
        response = Session.insert_session_data(session_module_id=session_module_id, identifier_key=identifier_key,
                                               identifier_value=identifier_value, start_time=start_time,
                                               end_time=end_time, active_time=active_time, user_id=user_id,
                                               system_id=system_id, company_id=company_id)

        if int(session_module_id) == constants.MODULE_TYPE_SELECT_FACILITY_SCREEN:
            logger.debug("Inside update condition")
            if identifier_value is not None:
                Session.update_identifier_value_for_select_facility(start_id=start_id,
                                                                    identifier_value=identifier_value,
                                                                    end_id=response)

        session_id = Session.get_session_id(session_module_id=session_module_id)
        logger.debug("session_id :{}".format(session_id))
        value = get_session_meta_value(facility_distribution_id=identifier_value)
        logger.debug("value for session meta:{}".format(value))
        if session_module_meta_id == constants.MODULE_META_ALTERNATE_DRUG_SELECTION_AND_DESELECTION:
            SessionMeta.insert_session_meta_data(session_id=session_id,
                                                 session_module_meta_id=constants.MODULE_META_ALTERNATE_DRUG_SELECTION_AND_DESELECTION,
                                                 value=value)
        if response is not None:
            return True
        else:
            return False

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in create_session {}".format(e))
        raise


@log_args_and_response
def create_and_update_session(session_module_id: int,
                              identifier_key: int, identifier_value: int,
                              start_time: str,
                              active_time: int,
                              user_id: int,
                              system_id: int,
                              company_id: int) -> bool:
    """
    This function creates a session and updates identifier value when flag is_first=True and flag_is_last=False
    @param session_module_id: int,
    @param identifier_key: int,
    @param identifier_value: int,
    @param start_time: str,
    @param active_time: str,
    @param user_id: int,
    @param system_id: int,
    @param company_id:
    @return bool
    """
    try:
        start_id = None
        if int(session_module_id) == constants.MODULE_TYPE_SELECT_FACILITY_SCREEN:
            start_id = Session.get_start_id(session_module_id)
            logger.debug(start_id)

        response = Session.insert_session_data(session_module_id=session_module_id, identifier_key=identifier_key,
                                               identifier_value=identifier_value, start_time=start_time,
                                               active_time=active_time, user_id=user_id, system_id=system_id,
                                               company_id=company_id)
        logger.info(response)
        if int(session_module_id) == constants.MODULE_TYPE_SELECT_FACILITY_SCREEN:
            logger.debug("Inside update condition")
            if identifier_value is not None:
                Session.update_identifier_value_for_select_facility(start_id=start_id,
                                                                    identifier_value=identifier_value,
                                                                    end_id=response)
        if response is not None:
            return True
        else:
            return False

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in create_and_update_session {}".format(e))
        raise


@log_args_and_response
def get_status_and_create_meta(session_module_id: int, session_module_meta_id: int, identifier_key: int,
                               identifier_value: int,
                               active_time: int,
                               end_time: str,
                               user_id: int,
                               system_id: int,
                               company_id: int) -> bool:
    """
    This function obtains the existing session and creates meta for the same.
    @param session_module_id: int,
    @param session_module_meta_id: int
    @param identifier_key: int,
    @param identifier_value: int,
    @param end_time: str,
    @param active_time: str,
    @param user_id: int,
    @param system_id: int,
    @param company_id:
    @return bool
    """
    try:
        # obtain the session table data for the given module id
        session_record = Session.get_session_data(session_module_id=session_module_id,
                                                  identifier_key=identifier_key, identifier_value=identifier_value,
                                                  user_id=user_id, system_id=system_id, company_id=company_id)

        # update the active time and session data with active time
        if session_record is not None:
            session_record_id = session_record["id"]
            session_record_active_time = session_record["active_time"]
            active_time = active_time + session_record_active_time
            response = Session.update_session_data(id=session_record_id, active_time=active_time, end_time=end_time)
            # obtain the value for the session meta and update accordingly
            value = get_session_meta_value(facility_distribution_id=identifier_value)
            SessionMeta.insert_session_meta_data(session_id=session_record_id,
                                                 session_module_meta_id=session_module_meta_id,
                                                 value=value)

            if response is not None:
                return True
            else:
                return False
        else:
            return False

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_status_and_create_meta {}".format(e))
        raise


@log_args_and_response
def update_session(session_module_id: int, identifier_key: int, active_time: int, user_id: int,
                   system_id: int, company_id: int) -> bool:
    """
    This function updates the existing session.
    @param session_module_id: int,
    @param identifier_key: int,
    @param active_time: str,
    @param user_id: int,
    @param system_id: int,
    @param company_id:
    @return bool
    """
    try:
        logger.debug("In update_session")
        # get the session_record for the current module_id and identifier key
        session_record = Session.get_session_data(session_module_id=session_module_id,
                                                  identifier_key=identifier_key,
                                                  user_id=user_id, system_id=system_id, company_id=company_id)
        # update the active time for the record with the given active time
        if session_record is not None:
            session_record_id = session_record["id"]
            session_record_active_time = session_record["active_time"]
            active_time = active_time + session_record_active_time

            response = Session.update_session_data(id=session_record_id, active_time=active_time)
            if response is not None:
                return True
            else:
                return False
        else:
            return False

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in update_session {}".format(e))
        raise


def create_or_update_session(session_module_id: int, identifier_key: int, start_time, end_time,
                             active_time: int, user_id: int, system_id: int, company_id: int) -> bool:
    """This function creates a single row for null identifier value"""
    try:

        session_id_query = Session.select(Session.id, Session.active_time.alias("current_active_time")).dicts()\
                                                                .where(Session.session_module_id == session_module_id,
                                                                  Session.identifier_key == identifier_key,
                                                                  Session.identifier_value == None,
                                                                  Session.user_id == user_id,
                                                                  Session.system_id == system_id,
                                                                  Session.company_id == company_id)
        if session_id_query.count() > 0:
            for record in session_id_query:
                logger.debug(record)
                active_time = active_time+record["current_active_time"]
                logger.debug(active_time)
                Session.update(active_time=active_time, end_time=end_time).where(Session.id == record["id"]).execute()
        else:
            Session.insert_session_data(session_module_id=session_module_id,
                                        identifier_key=identifier_key,
                                        identifier_value=None,
                                        start_time=start_time,
                                        end_time=end_time,
                                        active_time=active_time,
                                        user_id=user_id,
                                        company_id=company_id,
                                        system_id=system_id)
        return True

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in create_or_update_session {}".format(e))
        raise
