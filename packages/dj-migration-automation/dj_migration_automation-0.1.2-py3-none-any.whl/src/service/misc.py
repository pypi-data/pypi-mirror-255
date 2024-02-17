import base64
import datetime
import functools
import json
import os
import shutil
import sys
from typing import List, Dict, Any, Optional
from uuid import uuid4

import cherrypy
import couchdb
import pandas as pd
from peewee import DoesNotExist, InternalError, DataError, IntegrityError

import settings
from com.pharmacy_software import send_data
from couch_db_implementation import PrintJobStoreDocument
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response, retry, call_webservice, \
    get_current_date_time, get_current_date_time_millisecond, retry_exception
from dosepack.validation.validate import validate
from src.dao.print_dao import db_get_by_printer_code, rename_printer_in_db, update_printer_in_db, \
    delete_printer_from_db, update_printer_count, update_task_status
from realtime_db.dp_realtimedb_interface import Database
from src import constants
from src.dao.couch_db_dao import initialize_couch_db_doc, get_couch_db_database_name
from src.dao.misc_dao import update_sequence_no_for_pre_processing_wizard, get_batch_id_for_pre_processing_wizard, \
    get_packs_count_for_latest_batch, track_consumed_labels, get_queue_count, \
    get_system_setting_info, get_company_setting_data_by_company_id, \
    system_setting_update_or_create_record, \
    update_company_setting_by_company_id, company_setting_create_multiple_record, get_company_setting_by_company_id, \
    db_add_overloaded_pack_timing_data_dao
from src.exceptions import RealTimeDBException, RedisConnectionException, \
    PharmacySoftwareResponseException, PharmacySoftwareCommunicationException, TokenMissingException
from src.redis_controller import update_pending_template_data_in_redisdb
from src.service.print import db_get_printer

logger = settings.logger


def remove_dir(path):
    """
    Removes dir and ignores error

    :param path:
    :return:
    """
    try:
        shutil.rmtree(path)
    except (OSError, IOError) as e:
        logger.error(e, exc_info=True)


@log_args_and_response
def set_print_queue_status(pack_id, record_ids, status, system_id, company_id=None, printer_unique_code=None,
                           reset_printer_count=0):
    # if not int(pack_id) == 0:  # skip for test print job
    #     valid_pack = PackDetails.db_verify_pack_id_by_system_id(pack_id, system_id)
    #     # checking if pack id is valid
    #     if not valid_pack:
    #         return error(1014)
    # commenting to use record ids directly

    printing_status = int(status)
    try:
        if int(status) and company_id:  # reduce label quantity from quantity tracker
            track_consumed_labels(1, company_id)
    except Exception as e:  # just logging as optional and don't want to stop the flow
        logger.error(e, exc_info=True)

    try:
        record_id_list = record_ids.split(',')
        pack_id = int(pack_id)
        # pack_id_list = pack_id.split(',')
        with db.transaction():
            if pack_id:
                data = update_task_status(record_id_list=record_id_list, status=status)
            else:  # set data 1 for test print job
                data = 1
            status, _ = update_print_job_status_in_couch_db(
                record_id_list, status, system_id
            )
            if not status:
                logger.error('Error in updating status of record(s): ' + str(record_id_list))
                raise RealTimeDBException
    except DataError as e:
        logger.error(e, exc_info=True)
        return error(1001)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except RealTimeDBException as e:
        logger.error(e, exc_info=True)
        return error(2004)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(2005)

    try:
        if printing_status == settings.PRINT_STATUS['Done'] or bool(reset_printer_count):
            printer_update_count_status = update_printer_count(int(reset_printer_count), printer_unique_code, system_id,
                                                               record_id_list, printing_status)
            logger.info(f"set_print_queue_status, printer_update_count_status: {printer_update_count_status}")

    except Exception as e:  # just logging as optional and don't want to stop the flow
        logger.error(e, exc_info=True)

    return create_response(data)


def get_system_info(company_id=None):
    company_id = company_id
    system_info = dict()
    system_info_updated = dict()
    manual_info = dict()
    all_info = dict()
    try:
        system_setting_query = get_system_setting_info()

        for record in system_setting_query.dicts():
            if record['system_id'] == 0 or record['system_id'] is None:
                manual_info[record['name']] = record['value']
                continue
            if record['name'] not in settings.AUTOMATIC_CAPACITY:
                continue
            if record['system_id'] not in system_info:
                system_info[record['system_id']] = {}
            system_info[record['system_id']][record["name"]] = record["value"]

        company_setting_query = get_company_setting_data_by_company_id(company_id=company_id)
        for record in company_setting_query.dicts():
            manual_info[record['name']] = record['value']

        # for k,v in system_info.items():
        #     for sys,val in v.items():
        #         if sys not in system_info_updated:
        #             system_info_updated[sys] = {}
        #         system_info_updated[sys].update(val)
        all_info = {'automatic_system': system_info, 'manual': manual_info}
        return create_response(all_info)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_system_info {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_system_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_system_info {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_system_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_system_info: " + str(e))


def create_update_system_setting(dict_info):
    """
    :return: response status i.e row created or updated
    """
    try:
        response_dict = {'row_status': []}
        if "automatic" in dict_info:
            for id in range(0, len(dict_info["automatic"])):
                if len(dict_info["automatic"][id]['name']) == len(dict_info["automatic"][id]['value']):
                    for name in range(0, len(dict_info["automatic"][id]['name'])):
                        data_dict = {'system_id': dict_info["automatic"][id]["system_id"],
                                     'name': dict_info["automatic"][id]["name"][name]}
                        update_dict = {'created_by': dict_info["automatic"][id]["user_id"],
                                       'modified_by': dict_info["automatic"][id]["user_id"],
                                       'value': dict_info["automatic"][id]["value"][name]}
                        print("data dict", data_dict)
                        response = system_setting_update_or_create_record(create_dict=data_dict, update_dict=update_dict)
                        response_dict['row_status'].append(response)
                else:
                    return error(2001, "Argument for automatic name does not match with value.")

        if "manual" in dict_info:
            """
            This will save manual user capacity to Company Settings Table
            """
            update_dict: dict = dict()
            for id in range(len(dict_info["manual"])):
                manual_cap_dict = dict(zip(dict_info["manual"][id]["name"], dict_info["manual"][id]["value"]))
                if len(dict_info["manual"][id]['name']) == len(dict_info["manual"][id]['value']):
                    for k, v in manual_cap_dict.items():
                        update_dict = {"value": v, "created_by": dict_info["manual"][id]["user_id"],
                                       "modified_by": dict_info["manual"][id]["user_id"]}
                        status = update_company_setting_by_company_id(update_company_dict=update_dict,
                                                                      company_id=dict_info["manual"][id]["company_id"],
                                                                      name=k)
                        logger.info("In create_update_system_setting: update company setting by company id: {}".format(status))
                else:
                    return error(2001, "Argument for manual name does not match with value.")

            # for id in range(0, len(dict_info["manual"])):
            #     if len(dict_info["manual"][id]['name']) == len(dict_info["manual"][id]['value']):
            #         for name in range(0,len(dict_info["manual"][id]['name'])):
            #             data_dict = {'system_id': 0, 'name': dict_info["manual"][id]["name"][name]}
            #             update_dict = {'created_by': dict_info["manual"][id]["user_id"], 'modified_by': dict_info["manual"][id]["user_id"],'value': dict_info["manual"][id]["value"][name]}
            #             print("data dict", data_dict)
            #             response = SystemSetting.db_update_or_create_record(data_dict, update_dict)
            #             response_dict['row_status'].append(response)
            #     else:
            #         return error(2001, "Argument for manual name does not match with value.")

        return create_response(1)

    except DoesNotExist:
        response = {}
        return response
    except (IntegrityError, InternalError):
        return error(2001)


def save_data(extra_hour_info):
    try:
        final_data_list = []
        for data in extra_hour_info:
            extra_hours = int(data["extra_hours"]) + int(data["minutes"]) / 60
            extra_hours = round(extra_hours, 2)
            final_data = {
                "date": data["date"],
                "system_id": data["system_id"],
                "extra_hours": extra_hours,
                "created_by": data["user_id"],
                "modified_by": data["user_id"]
            }
            final_data_list.append(final_data)
        db_add_overloaded_pack_timing_data_dao(insert_dict=final_data_list)
        return create_response(1)
    except InternalError as e:
        logger.error(str(e))
        return error(2001)
    except DataError:
        return error(2001)


def get_company_setting(company_id):
    """ Returns json of company_settings """
    try:
        company_setting: Dict[str, Any] = get_company_setting_by_company_id(company_id=company_id)
        return create_response(company_setting)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_company_setting {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_company_setting: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_company_setting {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_company_setting: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_company_setting: " + str(e))


@validate(required_fields=["company_id", "data", "user_id"])
def add_company_setting(dict_setting_info):
    """ Creates record of company_setting """
    try:
        setting_data: Dict[str, Any] = get_company_setting_by_company_id(company_id=dict_setting_info["company_id"])
    except InternalError:
        return error(2001)

    for item in dict_setting_info["data"]:
        if item["name"] in setting_data:
            return error(1019, ": " + item["name"])
            # setting name already present
        else:
            item["company_id"] = dict_setting_info["company_id"]
            item["created_by"] = dict_setting_info["user_id"]
            item["modified_by"] = dict_setting_info["user_id"]

    try:
        status = company_setting_create_multiple_record(insert_dict=dict_setting_info["data"])
        logger.info("In add_company_setting: record created in company setting table: {}".format(status))
        return create_response(1)

    except (InternalError, IntegrityError< DataError) as e:
        logger.error("error in add_company_setting {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_company_setting: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in add_company_setting {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_company_setting: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in add_company_setting: " + str(e))


@validate(required_fields=["company_id", "data", "user_id"])
def update_company_setting(dict_setting_info):
    """ Updates company settings  """
    company_id = dict_setting_info["company_id"]
    try:
        setting_data: Dict[str, Any] = get_company_setting_by_company_id(company_id=company_id)
    except InternalError:
        return error(2001)

    # throw error if setting not present already
    for item in dict_setting_info["data"]:
        if item["name"] not in setting_data:
            return error(1004, ": " + item["name"])

    with db.transaction():
        try:
            for item in dict_setting_info["data"]:
                update_company_dict: dict = dict()
                update_company_dict["value"] = item["value"]
                update_company_dict['modified_by'] = dict_setting_info["user_id"]
                status = update_company_setting_by_company_id(update_company_dict=update_company_dict, company_id=company_id,
                                                              name=item["name"])
                logger.info("In update_company_setting: update company setting by company id: {}".format(status))
            return create_response(1)
        except InternalError:
            return error(2001)
        except DataError:
            return error(2001)


@validate(required_fields=["system_id", "unique_code", "printer_type"])
def update_printer(printer_info):
    unique_code = printer_info.pop("unique_code")
    system_id = printer_info.pop("system_id")
    try:
        printer = db_get_by_printer_code(unique_code, system_id)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    if not printer:  # No Printer found
        return error(6002)

    try:
        with db.transaction():
            status = update_printer_in_db(printer_info, unique_code)
            if status:
                update_printer_in_couch_db(system_id, unique_code, printer_info)

            return create_response(status)
    except DataError as e:
        logger.error(e, exc_info=True)
        return error(1020)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except RealTimeDBException:
        logger.error("Error in getting real time db name")
        return error(2004)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(2005)


@retry(3)
def update_couch_db_printjobs_doc(system_id, field_name, existing_value, new_value):
    """
    Updates info in printjobs couch-db doc for a given system.
    """

    database_name = get_couch_db_database_name(int(system_id))
    if database_name is None:
        raise RealTimeDBException

    cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
    try:
        logger.info("attempting to connect to db")
        cdb.connect()
        logger.info("connection successful")

        settings.PRINTJOB_DOCUMENT_OBJ = PrintJobStoreDocument(cdb, settings.CONST_PRINT_JOB_DOC_ID)
        settings.PRINTJOB_DOCUMENT_OBJ.initialize_doc()

        # store the document retrieved from the database
        settings.PRINTJOB_DOC = settings.PRINTJOB_DOCUMENT_OBJ.get_document()

        # get the existing printqueue
        settings.PRINT_JOB_QUEUE = settings.PRINTJOB_DOC["data"]["print_jobs"]
        for index, job in enumerate(settings.PRINT_JOB_QUEUE):
            if job[field_name] == existing_value:
                job[field_name] = new_value

        # now save the document
        settings.PRINTJOB_DOCUMENT_OBJ.update_document(settings.PRINTJOB_DOC)
        logger.info('Updated info in couch_db doc printjobs for system id ' + str(system_id))
        return True, True
    except Exception as ex:
        print("Issues while executing couchdb reference implementation.", ex)
        logger.error("Issues while executing couchdb reference implementation." + str(ex))
        return False, False


@validate(required_fields=["system_id", "existing_printer_name", "new_printer_name"])
def rename_printer(printer_info):
    """
    This method will rename the printer based on the existing printer name and the system_id
    @param printer_info:
    @return:
    """
    existing_printer_name = printer_info["existing_printer_name"]
    new_printer_name = printer_info["new_printer_name"]
    system_id = printer_info["system_id"]

    try:
        response = rename_printer_in_db(existing_printer_name, new_printer_name, system_id)
        if response:
            couch_update_status, _ = update_couch_db_printjobs_doc(system_id=system_id,
                                                                   field_name=settings.STRING_PRINTER_NAME,
                                                                   existing_value=existing_printer_name,
                                                                   new_value=new_printer_name)
            if not couch_update_status:
                raise RealTimeDBException
        return response
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except RealTimeDBException as e:
        logger.error(e, exc_info=True)
        return error(2005)


def remove_printer(unique_code, system_id):
    try:
        with db.transaction():
            data = delete_printer_from_db(system_id, unique_code)

            # remove the printer from couch-db also
            if data > 0:
                remove_printer_from_couch_db(system_id, unique_code)
                response = {'removed': True}
            else:
                response = {'removed': False}
    except DataError as e:
        logger.error(e, exc_info=True)
        return error(1020)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except RealTimeDBException:
        logger.error("Error in getting real time db name")
        return error(2004)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(2005)
    return create_response(response)


def get_token():
    try:
        logger.info("In get_token")
        authorization = cherrypy.request.headers.get("Authorization", None)
        # checks if access_token present in request headers or not
        if authorization:
            access_token = authorization.split()[1]
            logger.info("token_from_args: " + str(access_token))
        else:
            access_token = settings.ACCESS_TOKEN
            logger.info("token_from_settings: " + str(access_token))

        # if settings.ACCESS_TOKEN is None or settings.ACCESS_TOKEN=='':
        #     token = cherrypy.request.headers.get("Authorization")
        # else:
        #     token = settings.ACCESS_TOKEN
        # if token is not None and token.find("Bearer ") == False:
        #     token = token.replace("Bearer ", "")
        #
        # return token
        return access_token
    except Exception as e:
        logger.error(e, exc_info=True)
        return None

# lru_cache gives best result when max size is power of 2


# @functools.lru_cache(maxsize=256)
def get_userid_by_ext_username(ext_username, company_id):
    if not ext_username or not company_id:
        raise ValueError('ext_username and company_id is required')  # one of the arg is required

    try:
        logger.info('Getting user id by ips username')
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.GET_USERDETAILS_BY_EXT_USERNAME_URL,
                                       parameters={"company_id": company_id, "ext_username": ext_username},
                                       use_ssl=settings.AUTH_SSL)
        if not status:
            logger.error("Error in getting user details. Response: " + str(data))
            return None
        if not data["status"] == 'failure':
            response = data["data"]
            return response

        logger.error(data)
        return None
    except Exception as e:
        logger.error(e, exc_info=True)
        return None


# @functools.lru_cache(maxsize=512)
def get_users_by_ids(user_id_list, args_info: Optional[Dict[str, any]] = None):
    if not user_id_list:
        raise ValueError('user_id_list  is required')  # one of the arg is required

    if args_info and args_info.get("token"):
        token = args_info["token"]
    else:
        token = get_token()

    try:
        logger.info('Getting user id by ips username')
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.GET_USERDETAILS_BY_IDS_URL,
                                       parameters={"user_id_list": user_id_list},
                                       use_ssl=settings.AUTH_SSL, headers={"authorization": "Bearer {}".format(token)})
        if not status:
            logger.error("Error in getting user details. Response: " + str(data))
            return None
        if not data["status"] == 'failure':
            response = data["data"]
            return response

        logger.error(data)
        return None
    except Exception as e:
        logger.error(e, exc_info=True)
        return None


# @functools.lru_cache(maxsize=100)
def get_current_user(token):
    try:
        if not token:
            raise ValueError("token parameter is required in args of get_current_user")

        logger.info('Getting current user data by token')
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.GET_CURRENT_USER,
                                       parameters={"access_token": token},
                                       use_ssl=settings.AUTH_SSL)
        if not status:
            logger.error("Error in getting user details. Response: " + str(data))
            return None
        if not data["status"] == 'failure':
            response = data["data"]
            return response

        logger.error(data)
        return None
    except Exception as e:
        logger.error(e, exc_info=True)
        return None


@retry(3)
def update_manual_packs_count_after_change_rx(document_name, system_id=None, company_id=None, raise_exc=False,
                                              update_count: Optional[int] = 0):
    """
    Updates document with current timestamp
    - at least and only one of the system_id or company_id must be present in arg
    :param system_id: int
    :param company_id: int
    :param document_name: str
    :param raise_exc: bool
    :param update_count: Optional int
    :return:
    """
    try:
        logger.info("In update_manual_packs_count_after_change_rx -- document_name: {}, system_id: {}, company_id: {}, "
                    "raise_exc: {}, update_count: {}".format(document_name, system_id, company_id, raise_exc,
                                                             update_count))
        # TODO: COMPANY ID INSTEAD OF SYSTEM ID IN COUCH DB
        document = initialize_couch_db_doc(document_name,
                                           system_id=system_id,
                                           company_id=company_id)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("type", document_name)
        couchdb_doc.setdefault("data", {})

        couchdb_doc["data"].setdefault("rx_changed_count", 0)
        couchdb_doc["data"]["rx_changed_count"] = update_count if update_count else 0
        logger.info("updating Rx Changed Packs Count in doc: " + str(document_name))

        document.update_document(couchdb_doc)
        return True, True
    except RealTimeDBException:
        logger.warning("Function: update_manual_packs_count_after_change_rx -- Real time db not updated. DOCUMENT: "
                       + document_name)
        if raise_exc:
            raise
        return False, False
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Function: update_manual_packs_count_after_change_rx -- General Exception: {}, DOCUMENT: {}"
                     .format(e, document_name))
        if raise_exc:
            raise
        return False, False


@retry_exception(times=3, exceptions=(couchdb.http.ResourceConflict, couchdb.http.HTTPError))
def real_time_db_timestamp_trigger(document_name, system_id=None, company_id=None, raise_exc=False,
                                   update_count_flag: Optional[bool] = False, update_count: Optional[int] = 0):
    """
    Updates document with current timestamp
    - at least and only one of the system_id or company_id must be present in arg
    :param system_id: int
    :param company_id: int
    :param document_name: str
    :param raise_exc: bool
    :param update_count_flag: Optional bool
    :param update_count: Optional int
    :return:
    """
    try:
        logger.info("Function: real_time_db_timestamp_trigger -- document_name: {}, system_id: {}, company_id: {}, "
                    "raise_exc: {}, update_count_flag: {}, update_count: {}"
                    .format(document_name, system_id, company_id, raise_exc, update_count_flag, update_count))

        # TODO: COMPANY ID INSTEAD OF SYSTEM ID IN COUCH DB
        document = initialize_couch_db_doc(document_name,
                                           system_id=system_id,
                                           company_id=company_id)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("type", document_name)
        couchdb_doc.setdefault("data", {})
        if not update_count_flag:
            couchdb_doc["data"].setdefault("timestamp", "")
            couchdb_doc["data"]["timestamp"] = get_current_date_time()
            logger.info("updating time stamp in doc: " + str(document_name))
        else:
            couchdb_doc["data"].setdefault("pending_count", 0)
            couchdb_doc["data"]["pending_count"] = update_count if update_count else 0
            logger.info("updating Pending Templates Count in doc: " + str(document_name))

        document.update_document(couchdb_doc)
    except RealTimeDBException:
        logger.warning("Real time db not updated in file parsing. DOCUMENT: " + document_name)
        if raise_exc:
            raise
    except Exception as e:
        logger.error(e, exc_info=True)
        if raise_exc:
            raise


@retry(3)
def update_queue_count(document_name, count=0, system_id=None, company_id=None,
                       operation=settings.TASK_OPERATION['Add'], update_timestamp=False, raise_exc=False):
    """
    Updates document with current timestamp and count of task
    - at least and only one of the system_id or company_id must be present in arg
    :param document_name:
    :param count: int
    :param system_id:
    :param company_id:
    :param operation: add or remove task count
    :param update_timestamp:
    :param raise_exc:
    :return:
    """
    try:
        logger.info("getting_couch_db_data")
        document = initialize_couch_db_doc(document_name,
                                           system_id=system_id,
                                           company_id=company_id)
        couchdb_doc = document.get_document()
        logger.info("couch_db_data_found")
        couchdb_doc.setdefault("type", document_name)
        couchdb_doc.setdefault("data", {})
        data = couchdb_doc['data']
        pending_tasks = data.get('pending_tasks', 0)
        logger.info('before_update_couchdb: ' + str(couchdb_doc))
        if operation == settings.TASK_OPERATION['Add']:
            count = get_queue_count(company_id)
            logger.info("count_from_queue: " + str(count))
            print("count_from_queue_while_adding: {}".format(count))
            if count is not None:
                pending_tasks = count
            else:
                pending_tasks = 0
            logger.info("count_while_adding: " + str(pending_tasks))
            print("count_while_adding: {}".format(pending_tasks))
        elif operation == settings.TASK_OPERATION['Remove']:
            # commenting this to get data from db always
            # pending_tasks = pending_tasks - count
            # original_reduce_count = pending_tasks
            # if pending_tasks < 10:
            #     count = get_queue_count(company_id)
            #     logger.info("count_from_queue: " + str(count))
            #     if count is not None:
            #         pending_tasks = count
            # logger.info("original_count_while_reducing: " + str(original_reduce_count) + " couch_db_pending_count: " +
            #              str(pending_tasks))
            logger.info('getting_count_from_queue')
            print('getting_count_from_queue')
            count = get_queue_count(company_id)
            logger.info("count_from_queue: " + str(count))
            print("count_from_queue: {}".format(count))
            if count:
                pending_tasks = count
            else:
                # update redis db and timestamp in couch db when count is 0
                try:
                    update_pending_template_data_in_redisdb(company_id)
                except (RedisConnectionException, Exception) as e:
                    logger.error(e)
                pending_tasks = 0
                update_timestamp = True
            logger.info(" couch_db_pending_count: " + str(pending_tasks))
        couchdb_doc["data"]["pending_tasks"] = pending_tasks
        if update_timestamp:
            couchdb_doc["data"].setdefault("timestamp", "")
            couchdb_doc["data"]["timestamp"] = get_current_date_time_millisecond()
        else:
            couchdb_doc["data"]["timestamp"] = data["timestamp"]
        logger.info(couchdb_doc)
        document.update_document(couchdb_doc)
        return True, True
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error(e, exc_info=True)
        if raise_exc:
            return False, False


@retry(3)
def update_print_job_status_in_couch_db(record_id_list, new_printing_status, system_id):
    """
    Updates new job to the couch-db doc for a given system.
    """

    database_name = get_couch_db_database_name(int(system_id))
    if database_name is None:
        raise RealTimeDBException

    cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
    try:
        logger.info("attempting to connect to db")
        cdb.connect()
        logger.info("connection successful")

        settings.PRINTJOB_DOCUMENT_OBJ = PrintJobStoreDocument(cdb, settings.CONST_PRINT_JOB_DOC_ID)
        settings.PRINTJOB_DOCUMENT_OBJ.initialize_doc()

        # store the document retrieved from the database
        settings.PRINTJOB_DOC = settings.PRINTJOB_DOCUMENT_OBJ.get_document()

        # get the existing printqueue
        settings.PRINT_JOB_QUEUE = settings.PRINTJOB_DOC["data"]["print_jobs"]
        record_id_list = list(map(int, record_id_list))
        for index, job in enumerate(settings.PRINT_JOB_QUEUE):
            if int(job["id"]) in record_id_list:
                # todo check if the last line works
                # settings.PRINTJOB_DOC["data"]["print_jobs"][index]['printing_status'] = new_printing_status
                job['printing_status'] = int(new_printing_status)

        # now save the document
        settings.PRINTJOB_DOCUMENT_OBJ.update_document(settings.PRINTJOB_DOC)
        print('Updated job status in couch_db')
        logger.info('Updated job status in couch_db for system id' + str(system_id))
        return True, True
    except Exception as ex:
        print("Issues while executing couchdb reference implementation.", ex)
        logger.error("Issues while executing couchdb reference implementation." + str(ex))
        return False, False


def remove_printer_from_couch_db(system_id, unique_code):
    """
    Updates the list of associated printers in couch_db
    """

    database_name = get_couch_db_database_name(int(system_id))
    if database_name is None:
        raise RealTimeDBException

    cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
    try:
        logger.info("attempting to connect to db")
        print("attempting to connect to db")
        cdb.connect()
        print("connection successful")
        logger.info("connection successful")

        settings.PRINTER_INFORMATION_DOCUMENT_OBJ = PrintJobStoreDocument(cdb, settings.CONST_PRINTER_INFO_DOC_ID)
        settings.PRINTER_INFORMATION_DOCUMENT_OBJ.initialize_doc()

        # store the document retrieved from the database
        settings.PRINTER_INFO_DOC = settings.PRINTER_INFORMATION_DOCUMENT_OBJ.get_document()

        for index, printer in enumerate(settings.PRINTER_INFO_DOC["data"]["printers"]):
            if unique_code == str(printer["unique_code"]):
                settings.PRINTER_INFO_DOC["data"]["printers"].pop(index)

        # now save the document
        settings.PRINTER_INFORMATION_DOCUMENT_OBJ.update_document(settings.PRINTER_INFO_DOC)
        print('removed printer from couch_db')
        logger.info('removed printer from couch_db for system id' + str(system_id))

    except Exception as ex:
        print("Issues while executing couchdb reference implementation.", ex)
        logger.error("Issues while executing couchdb reference implementation." + str(ex))
        raise


def update_printer_in_couch_db(system_id, unique_code, printer_info):
    """
    Updates the list of associated printers in couch_db
    """

    database_name = get_couch_db_database_name(int(system_id))
    if database_name is None:
        raise RealTimeDBException

    cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
    try:
        logger.info("attempting to connect to db")
        cdb.connect()
        logger.info("connection successful")

        settings.PRINTER_INFORMATION_DOCUMENT_OBJ = PrintJobStoreDocument(cdb, settings.CONST_PRINTER_INFO_DOC_ID)
        settings.PRINTER_INFORMATION_DOCUMENT_OBJ.initialize_doc()

        # store the document retrieved from the database
        settings.PRINTER_INFO_DOC = settings.PRINTER_INFORMATION_DOCUMENT_OBJ.get_document()

        for index, printer in enumerate(settings.PRINTER_INFO_DOC["data"]["printers"]):
            if unique_code == str(printer["unique_code"]):
                settings.PRINTER_INFO_DOC["data"]["printers"][index].update(printer_info)

        # now save the document
        settings.PRINTER_INFORMATION_DOCUMENT_OBJ.update_document(settings.PRINTER_INFO_DOC)
        logger.info('Printer updated for printer code' + str(unique_code))

    except Exception as ex:
        logger.error("Issues in updating printer data: " + str(ex))
        raise


@retry(3)
def update_replenish_canisters_couch_db(replenish_data, system_id):
    """
    Updates replenish doc of couch db for given system

    :param replenish_data: list (JSON Serializable)
    :param system_id: int
    :return: bool, bool
    """

    try:
        document = initialize_couch_db_doc(settings.CONST_REPLENISH_DOC, system_id=system_id)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("type", settings.CONST_REPLENISH_DOC_TYPE)
        couchdb_doc.setdefault("data", {})
        couchdb_doc["data"]["timestamp"] = get_current_date_time()
        couchdb_doc["data"]["replenish_data"] = replenish_data
        document.update_document(couchdb_doc)
        return True, True
    except Exception as e:
        logger.error("Replenish drug Couch DB update failed "
                     "for system ID: {}, exc: {}".format(system_id, e))
        return False, False


def update_rfid_in_couchdb(callback_data, company_id=3):
    """
    @desc : To update rfid in couch db (For print Utility)
    @param callback_data:
    @return:
    """
    try:

        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        location_rfid = callback_data["data"]
        location = list(location_rfid.keys())[0]
        rfid = list(location_rfid.values())[0]

        try:
            logger.info("attempting to connect to cdb")
            cdb.connect()
            logger.info("connection successful")
            id = 'ADHOC_canister_register'
            table = cdb.get(id)
            data_dict = {
                "rfid": rfid,
                "Date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            }
            if table is None:
                data_dict = {"_id": id, "data": {location: data_dict}}
            else:
                table["data"][location] = data_dict
                data_dict = table

            cdb.save(data_dict)

        except Exception as e:
            logger.info("Unable to connect to cdb")

        return True

    except Exception as e:
        logger.error("Error in storing data in couch db")
        return False


def get_all_dates_between_two_dates(start_date, end_date):
    dates = list()
    for date in pd.date_range(start=start_date, end=end_date).date:
        dates.append(str(date))
    return dates


def validate_ips_username(company_id, user_name, password):
    try:
        auth_parameters = {
            'company_id': company_id
        }
        status, existing_data = call_webservice(settings.BASE_URL_AUTH, settings.EXISTING_IPS_USERNAMES,
                                                parameters=auth_parameters, use_ssl=False)
        if not status or not existing_data.get('status', None) == settings.AUTH_SUCCESS_RESPONSE:
            return error(8004)
        existing_ips_users = existing_data['data']
        if user_name in existing_ips_users:
            return error(1020, 'Ips user name already in use in dosepack')
        company_settings: Dict[str, Any] = get_company_setting_by_company_id(company_id=company_id)
        required_settings = settings.PACK_GENERATION_REQUIRED_SETTINGS
        settings_present = all([key in company_settings for key in required_settings])
        if not settings_present:
            return error(6001)

        parameters = {
            'token': company_settings["IPS_COMM_TOKEN"],
            'password': base64.b64encode(password.encode('utf-8')),
            'user_name': user_name
        }
        data = send_data(company_settings['BASE_URL_IPS'], settings.IPS_USER_VALIDATION, parameters, 0)
        logger.info("***********ips_user_name*********" + str(data) + "****************")
        if not data:
            return create_response(False)
        data = data["response"]
        if not data:
            return error(7002)
        if data['validation_status'] == 'OK':
            validation_status = True
        else:
            validation_status = False
        return create_response({'validation_status': validation_status, 'is_locked': data.get('is_locked'),
                                'remaining_attempts': data.get('remaining_attempts'),
                                'error_message': data['errormessage']})
    except InternalError:
        return error(2001)
    except (PharmacySoftwareResponseException, PharmacySoftwareCommunicationException) as e:
        logger.error(e, exc_info=True)
        return error(7002)


def get_printer_overhead_status(printer_unique_code, system_id):
    printer_overhead = False
    try:
        printer = db_get_printer(printer_unique_code, system_id)

        if int(printer.print_count) >= settings.PRINT_OVERHEAD_LIMIT:
            printer_overhead = True

        response = {"printer_overhead": printer_overhead}

        return create_response(response)

    except (DoesNotExist, InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)
    # except Exception as ex:
    #     logger.error(ex, exc_info=True)
    #     return error(1034, ex)


@retry_exception(times = 3, exceptions=(couchdb.http.ResourceConflict, couchdb.http.HTTPError))
def update_document_with_revision(original_doc_obj, updated_doc_data, reset_data=False):
    """
    updates couch-db doc for manual fill station of a particular system
    :param original_doc_obj: obj
    :param reset_data: bool
    :param updated_doc_data: dict
    :return: tuple
    """
    try:
        if reset_data:
            updated_doc_data["data"] = {}
        original_doc_obj.update_document(updated_doc_data)
        return True, True
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        raise RealTimeDBException
    except Exception as e:
        logger.error(e, exc_info=True)
        raise RealTimeDBException


def fetch_not_interested_user_for_notification(key):
    if not key:
        raise ValueError('key  is required')  # one of the arg is required
    token = get_token()

    try:
        logger.info('Getting user settings by key')
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.GET_USER_IDS_FOR_NOTIFICATION,
                                       parameters={"key": key, "value": False},
                                       use_ssl=settings.AUTH_SSL, headers={"authorization": "Bearer {}".format(token)})

        if data["status"] == 'success':
            response = data["data"]["user_ids"]
            return response
        elif not status:
            logger.error("Error in getting user details. Response: " + str(data))

        logger.error(data)
        return None
    except Exception as e:
        logger.error(e, exc_info=True)
        return None


def update_mfd_pending_data_in_couch_db(document_name, company_id, mfd_data, reset_data=False):
    """
    updates couch-db doc for manual fill station of a particular system
    :param document_name: str
    :param company_id: int
    :param mfd_data: dict
    :return: tuple
    """
    try:
        document = initialize_couch_db_doc(document_name,
                                           system_id=None,
                                           company_id=company_id)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("type", constants.CONST_MANUAL_FILL_STATION_TYPE)
        couchdb_doc.setdefault("data", {})
        if reset_data:
            couchdb_doc["data"] = {}

        for key, value in mfd_data.items():
            couchdb_doc["data"][key] = value
        document.update_document(couchdb_doc)
        return True
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False


@retry(3)
def update_replenish_queue_count(replenish_data, system_id, device_id):
    """

    :param replenish_data:
    :param system_id:
    :param device_id:
    :return:
    """
    try:
        logger.info('updating_cbd_for_replenish_queue')
        print('updating_cbd_for_replenish_queue')
        document = initialize_couch_db_doc(settings.CONST_REPLENISH_DOC_v3 + str(device_id), system_id=system_id)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("type", settings.CONST_REPLENISH_DOC_TYPE_v3)
        couchdb_doc.setdefault("data", {})
        couchdb_doc["data"]["timestamp"] = get_current_date_time()
        for key, value in replenish_data.items():
            couchdb_doc["data"][key] = value
        document.update_document(couchdb_doc)
        return True, True
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error("Replenish canister Couch DB update failed "
                     "for device ID: {}, exc: {}".format(device_id, e))
        return False, False


def publish_voice_notification(component_device_code, notification_code, system_id, device_id, device_name):
    token = get_token()

    try:
        logger.info('publishing voice notification data')
        parameters = json.dumps({"component_device_code": component_device_code,
                                 "notification_code": notification_code,
                                 "system_id": system_id,
                                 "device_id": device_id,
                                 "region_or_robot": device_name
                                 })
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.PUBLISH_VOICE_NOTIFICATION_DATA,
                                       parameters=parameters,
                                       request_type="POST",
                                       use_ssl=settings.AUTH_SSL, headers={"authorization": "Bearer {}".format(token)})

        if not status:
            logger.error("Error in publishing notification data for parameters {}. Error: "
                         .format(parameters, data))
            return False, data

        if data["status"] == settings.SUCCESS_RESPONSE:
            response = data["data"]
            logger.info("success response from API - {} : {}".format(settings.PUBLISH_VOICE_NOTIFICATION_DATA, data))
            return True, response
        logger.info("failure response from API - {} : {}".format(settings.PUBLISH_VOICE_NOTIFICATION_DATA, data))
        return False, data
    except Exception as e:
        logger.error(e, exc_info=True)
        return False, str(e)


@log_args_and_response
@validate(required_fields=["company_id", "system_id", "user_id"])
def set_logged_in_user_in_couch_db_of_system(args: dict) -> dict:
    try:
        company_id = args["company_id"]
        system_id = args["system_id"]
        user_id = int(args["user_id"])
        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        doc_id = constants.LOGGED_IN_USER_INFO_COUCH_DB_DOC
        table = cdb.get(_id=doc_id)
        logger.debug("couch db doc: {}, data: ".format(doc_id, table))
        if table is not None:
            if "data" in table and str(system_id) in table["data"] and "user_id" in table["data"][str(system_id)]:
                table["data"][str(system_id)]["user_id"] = user_id
            else:
                if not "data" in table:
                    table["data"] = dict()
                if not str(system_id) in table["data"]:
                    table["data"][str(system_id)] = dict()
                table["data"][str(system_id)] = {"user_id": user_id}
        else:
            table = {
                "_id": constants.LOGGED_IN_USER_INFO_COUCH_DB_DOC,
                "type": constants.LOGGED_IN_USER_INFO_COUCH_DB_DOC,
                "data": {
                    str(system_id):
                        {
                            "user_id": user_id
                        }
                }
            }
        logger.debug("couch db doc - {} values {}".format(constants.LOGGED_IN_USER_INFO_COUCH_DB_DOC, table))
        cdb.save(table)
        logger.debug("user id {} updated in couch db doc {} of company_id {}".format(user_id,
                                                                                     constants.LOGGED_IN_USER_INFO_COUCH_DB_DOC,
                                                                                     company_id))
        return create_response(True)
    except Exception as e:
        settings.logger.error("Couch db update failed while updating current logged in user: " + str(e))
        return error(11002)


def get_logged_in_user_from_couch_db_of_system(company_id: int, system_id: int) -> int:
    try:
        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        doc_id = constants.LOGGED_IN_USER_INFO_COUCH_DB_DOC
        table = cdb.get(_id=doc_id)

        if table is not None:
            if "data" in table and str(system_id) in table["data"] and "user_id" in table["data"][str(system_id)]:
                user_id = table["data"][str(system_id)]["user_id"]
                return user_id
    except Exception as e:
        settings.logger.error(e)
        settings.logger.error(
            "Couch db access failed while fetching current logged in user details of system " + str(system_id))
        raise Exception('Couch db access failed while fetching current logged in user details:')


def update_couch_db_for_drawer_status(company_id: int, device_id: int, container_id: int, lock_status: bool,
                                      canister_status: bool = False) -> bool:
    try:
        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        doc_id = str(constants.CSR_DRAWER_EMLOCK_COUCH_DB_DOC) + '-{}'.format(device_id)

        table = cdb.get(_id=doc_id)

        if table is not None:
            # Whenever any canister is placed or taken out of any location from CSR, we need to update timestamp
            if canister_status:
                table["timestamp"] = get_current_date_time()

            # Whenever any drawer/container is locked or unlocked, we need to continue with update of unlocked drawers
            else:
                if lock_status:
                    table["unlocked_drawers"].append(container_id)
                else:
                    if container_id in table["unlocked_drawers"]:
                        table["unlocked_drawers"].remove(container_id)
        else:
            # Added one key value pair for TimeStamp to handle the real time update of canister placement in CSR
            # along with update of empty location count
            table = {"_id": doc_id,
                     "type": constants.CSR_DRAWER_EMLOCK_COUCH_DB_DOC,
                     "unlocked_drawers": [container_id],
                     "timestamp": get_current_date_time()
                     }
        logger.debug("couch db doc - {} values {}".format(doc_id, table))
        cdb.save(table)

        if canister_status:
            logger.debug("Timestamp updated for drawerID: {} for canister status in couch db doc {} of company_id {}".
                         format(container_id, doc_id, company_id))
        else:
            logger.debug(
                "drawer status {} updated in couch db doc {} of company_id {}".format(lock_status, doc_id, company_id))

        return True
    except Exception as e:
        settings.logger.error(e)
        settings.logger.error(
            "Couch db update failed while updating drawer emlock status for company" + str(company_id))
        raise RealTimeDBException("Couch db update failed while updating drawer emlock status")


@validate(required_fields=["company_id"])
@log_args_and_response
def update_canister_transfer_wizard_data_in_couch_db(args):
    """
    Function to add guided transfer meta data in couch db
    @param args: dict
    @return: status
    """
    logger.info("In update_canister_transfer_wizard_data_in_couch_db Input {}".format(args))
    company_id = args.pop("company_id")
    try:
        logger.debug("update_canister_transfer_wizard_data_in_couch_db >> company_id {}".format(company_id))
        database_name = get_couch_db_database_name(company_id=company_id)
        logger.debug("update_canister_transfer_wizard_data_in_couch_db >> database_name {}".format(database_name))
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        logger.debug("update_canister_transfer_wizard_data_in_couch_db Connection established: {}".format(cdb))
        id = constants.CANISTER_TRANSFER_WIZARD
        table = cdb.get(_id=id)

        logger.debug("previous table in update_canister_transfer_wizard_data_in_couch_db {} - {}".format(id, table))
        if table is None:  # when no document available for given device_id
            logger.debug("update_canister_transfer_wizard_data_in_couch_db: Table is None")

            table = {"_id": id, "type": constants.CANISTER_TRANSFER_WIZARD,
                     "data": args}

        elif ("batch_id" not in table["data"]) or (
                "batch_id" in table["data"] and table["data"]["batch_id"] != args["batch_id"]):
            logger.debug("update_canister_transfer_wizard_data_in_couch_db: Table do not have batch_id")

            table["data"] = args

        else:
            logger.info("Transfer pending for batch {}".format(table["data"]))
            return True, settings.SUCCESS_RESPONSE

        logger.info("updated table in update_canister_transfer_wizard_data_in_couch_db {} - {}".format(id, table))
        cdb.save(table)

        return True, settings.SUCCESS_RESPONSE

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return False, error(1000, "Couch db Document update conflict.")

    except RealTimeDBException as e:
        return False, error(1000, str(e))

    except Exception as e:
        logger.error(e, exc_info=True)
        return False, error(1000, "Error while updating couch db doc: " + str(e))


@validate(required_fields=["company_id"])
@log_args_and_response
def update_cycle_module_in_canister_tx_wizard_couch_db(args):
    """
    Function to add guided transfer meta data in couch db
    @param args: dict
    @return: status
    """
    logger.debug("In update_canister_transfer_wizard_data_in_couch_db Input {}".format(args))
    company_id = args.pop("company_id")
    transfer_cycle_id = args.get("transfer_cycle_id", None)
    module_id = args.get("module_id", None)
    batch_id = args.pop("batch_id")

    try:
        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = constants.CANISTER_TRANSFER_WIZARD
        table = cdb.get(_id=id)

        if table is None:  # when no document available for given device_id
            return False, "Canister recommendation is not executed"
        else:
            if 'batch_id' in table['data'] and table['data']['batch_id'] == batch_id:
                table['data']['module_id'] = module_id
                if transfer_cycle_id:
                    table['data']['transfer_cycle_id'] = transfer_cycle_id

        logger.info("updated table in couch db doc {} - {}".format(id, table))
        cdb.save(table)

        return True, "success"

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return False, error(1000, "Couch db Document update conflict.")

    except RealTimeDBException as e:
        return False, error(1000, str(e))

    except Exception as e:
        logger.error(e, exc_info=True)
        return False, error(1000, "Error while updating couch db doc: " + str(e))


@validate(required_fields=["company_id"])
@log_args_and_response
def update_guided_tx_meta_data_in_couch_db(args):
    """
    Function to add guided transfer meta data in couch db
    @param args: dict
    @return: status
    """
    logger.debug("In update_guided_transfer_meta_data_in_couch_db Input {}".format(args))
    company_id = args.pop("company_id")
    try:
        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = constants.GUIDED_TRANSFER_WIZARD
        table = cdb.get(_id=id)

        if table is None:  # when no document available for given device_id
            table = {"_id": id, "type": constants.GUIDED_TRANSFER_WIZARD,
                     "data": args}
        else:
            table["data"] = args

        logger.info("updated table in couch db doc {} - {}".format(id, table))
        cdb.save(table)

        return True, "success"

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return False, error(1000, "Couch db Document update conflict.")

    except RealTimeDBException as e:
        return False, error(1000, str(e))

    except Exception as e:
        logger.error(e, exc_info=True)
        return False, error(1000, "Error while clearing couch db doc: " + str(e))


def fetch_systems_by_company(company_id: int, system_ids: list = None, system_type: str = None) -> dict:
    """
    gets mfs-system and assigned user from auth
    :param company_id: whose system is to be fetched: int
    :param system_ids: if any particular system's data is to be found: list
    :param system_type: filter of particular type to be fetched: str
    :return:
    """
    token = get_token()
    try:
        parameters = {"company_id": company_id}
        if system_ids:
            parameters['system_ids'] = system_ids
        if system_type:
            parameters['system_type'] = system_type
        logger.info('Getting systems of a company')
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.FETCH_SYSTEMS_BY_COMPANY,
                                       parameters=parameters,
                                       headers={"authorization": "Bearer {}".format(token)},
                                       use_ssl=settings.AUTH_SSL)

        if data["status"] == 'success':
            response = data["data"]["data"]
            return response
        elif not status:
            logger.error("Error in getting system details. Response: " + str(data))

        logger.error(data)
        return None
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def fetch_users_by_company(company_id: int) -> dict:
    """
    fetches user of a company
    :param company_id: int
    :return:
    """
    token = get_token()
    try:
        logger.info('Getting systems of a company')
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.FETCH_USERS_BY_COMPANY,
                                       parameters={"company_id": company_id},
                                       headers={"authorization": "Bearer {}".format(token)},
                                       use_ssl=settings.AUTH_SSL)

        if data["status"] == 'success':
            response = data["data"]
            return response
        elif not status:
            logger.error("Error in getting user details. Response: " + str(data))

        logger.error(data)
        return None
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def update_user_access_in_auth(access_data: list) -> dict:
    """
    updates user access in auth
    :param access_data:
    :return:
    """
    token = get_token()
    try:
        logger.info('Getting systems of a company')
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.UPDATE_USER_ACCESS,
                                       parameters={"access_list": access_data},
                                       headers={"authorization": "Bearer {}".format(token)},
                                       use_ssl=settings.AUTH_SSL)

        if data["status"] == 'success':
            response = data["data"]
            if not response:
                raise InternalError("Couldn't update data in auth")
            return response
        elif not status:
            logger.error("Error in getting system details. Response: " + str(data))

        logger.error(data)
        return None
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


# @retry(3)
@retry_exception(times = 3, exceptions=(couchdb.http.ResourceConflict, couchdb.http.HTTPError))
def update_mfd_module_couch_db(document_name, system_id, mfs_data, reset_data=False):
    """
    updates wizard doc for manual fill station of a particular system
    :param document_name: str
    :param system_id: int
    :param mfs_data: dict
    :return: tuple
    """
    try:
        document = initialize_couch_db_doc(document_name,
                                           system_id=system_id,
                                           company_id=None)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("type", constants.CONST_MFD_PRE_FILL_DOC_TYPE)
        couchdb_doc.setdefault("data", {})
        for key, value in mfs_data.items():
            couchdb_doc["data"][key] = value
        if reset_data:
            couchdb_doc["data"] = {}
        document.update_document(couchdb_doc)
        return True, True
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False, False


@retry(3)
def get_mfd_module_couch_db(document_name, system_id):
    """
    returns wizard document of a particular mfs system
    :param document_name: str
    :param system_id: int
    :return: dict
    """
    try:
        document = initialize_couch_db_doc(document_name,
                                           system_id=system_id,
                                           company_id=None)
        couchdb_doc = document.get_document()
        return True, couchdb_doc
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False, False


def get_csr_station_id_loc_by_serial_number(serial_number: str, display_location: str) -> tuple:
    """
    Method to fetch station_type, station_id and location
    @param display_location:
    @param serial_number:
    @return:
    """
    try:
        station_id_without_zeros = int(serial_number[3:].lstrip("0"))
        disp_loc_number = int(display_location.split("-")[1])

        if disp_loc_number <= constants.LOCATIONS_PER_PCB_IN_CSR:
            new_station_id = (station_id_without_zeros * 2) - 1
            loc_number = disp_loc_number
        else:
            new_station_id = station_id_without_zeros * 2
            loc_number = disp_loc_number - constants.LOCATIONS_PER_PCB_IN_CSR

        return new_station_id, loc_number

    except (KeyError, ValueError) as e:
        logger.error(e)
        raise e


@retry(3)
def get_mfd_transfer_couch_db(device_id, system_id):
    """
    returns transfer document of a particular robot
    :param device_id: str
    :param system_id: int
    :return: dict
    """
    try:
        document_name = '{}_{}'.format(constants.MFD_TRANSFER_COUCH_DB, device_id)
        document = initialize_couch_db_doc(document_name,
                                           system_id=system_id,
                                           company_id=None)
        couchdb_doc = document.get_document()
        return True, couchdb_doc
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False, False


@log_args_and_response
def update_couch_db_mfd_canister_wizard(company_id: int,
                                        device_id: int,
                                        batch_id: int,
                                        module_id: int,
                                        mfd_transfer_to_device: bool = False,
                                        ) -> bool:
    """
    This function updates the couch db for the mfd transfer wizard
    """
    logger.debug("In update_couch_db_mfd_canister_wizard")
    try:
        if batch_id and company_id and device_id:
            database_name = get_couch_db_database_name(company_id=company_id)
            cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
            cdb.connect()
            doc_id = str(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME) + "-" + str(device_id)
            table = cdb.get(_id=doc_id)
            logger.info("Previous table in update_couch_db_mfd_canister_wizard {}".format(table))
            # Bellow is a patch where batch_id gets updated while checking for transfers as user has
            # putted some mfd canisters that are not going to be used in this batch but was used in past batched
            if table is not None:
                table_batch_id = table["data"].get('batch_id')
                if table_batch_id and table_batch_id > batch_id:
                    logger.info(
                        "In update_couch_db_mfd_canister_wizard Issue Found where udpating batch id for past batch current batch: {} past batch {}".format(
                            table_batch_id, batch_id))
                    batch_id = table_batch_id
                table["data"]["batch_id"] = batch_id
                table["data"]["module_id"] = module_id
                table["data"]["mfd_transfer_to_device"] = mfd_transfer_to_device
            else:
                table = {"_id": doc_id, "type": str(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME),
                         "data": {"batch_id": batch_id, "module_id": module_id,
                                  "mfd_transfer_to_device": mfd_transfer_to_device}}

            logger.info("Updated table in update_couch_db_mfd_canister_wizard {}".format(table))
            cdb.save(table)
        return True

    except Exception as e:
        logger.info("Unable to connect to couch db")
        raise


@retry(3)
def get_mfd_wizard_couch_db(company_id, device_id):
    """
    returns mfd transfer wizard document of a particular robot
    :param device_id: int
    :param company_id: int
    :return: dict
    """
    try:
        document_name = '{}-{}'.format(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME, device_id)
        document = initialize_couch_db_doc(document_name,
                                           system_id=None,
                                           company_id=company_id)
        couchdb_doc = document.get_document()
        return True, couchdb_doc
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False, False


@retry(3)
def update_mfd_transfer_wizard_couch_db(device_id, company_id, mfd_data, reset_data=False):
    """
    updates wizard doc for mfd transfer
    :param device_id: int
    :param company_id: int
    :param mfd_data: dict
    :return: tuple
    """
    try:
        document_name = '{}-{}'.format(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME, device_id)
        document = initialize_couch_db_doc(document_name,
                                           system_id=None,
                                           company_id=company_id)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("type", constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME)
        couchdb_doc.setdefault("data", {})
        for key, value in mfd_data.items():
            couchdb_doc["data"][key] = value
        if reset_data:
            couchdb_doc["data"] = {}
        logger.info('wizard data {}'.format(couchdb_doc))
        document.update_document(couchdb_doc)
        return True, True
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False, False


@log_args_and_response
def get_replenish_list_of_device(device_id: int, system_id: int) -> int:
    """
    Function to fetch scanned drawer id in guided transfer flow in couch db
    @param args: dict
    @return: status
    """
    logger.debug("In check_for_replenish_list_for_device")

    try:
        canister_list = list()
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = settings.CONST_REPLENISH_DOC_v3 + str(device_id)
        table = cdb.get(_id=id)

        logger.info("Table in guided transfer {}".format(table))
        if table is not None:
            if "data" in table.keys() and "canister_list" in table['data'] and table['data']['canister_list']:
                canister_list = table['data']['canister_list']

        return canister_list

    except RealTimeDBException as e:
        raise RealTimeDBException(e)

    except ValueError as e:
        logger.error(e)
        raise e

    except Exception as e:
        logger.error(e)
        raise Exception('Couch db access failed while transferring canisters')


def get_weekdays(year, month, day):
    thisXMas = datetime.date(year, month, day)
    thisXMasDay = thisXMas.weekday()
    weekday = settings.WEEKDAYS[thisXMasDay]
    return weekday


@log_args_and_response
def get_pre_processing_wizard_sequence_module(data: dict):
    """
        This function to return current completed sequence and module
        if batch status in [34,35,36,38,130]
        - return pack count, batch info
    """
    response_data: dict = dict()
    company_id = data.get("company_id")
    system_id = data.get("system_id")
    try:
        # get batch id from batch master (1st batch which status in [34,35,36,38,130])
        batch_data = get_batch_id_for_pre_processing_wizard()
        logger.info("IN get_pre_processing_wizard_sequence_module: batch_data {}".format(batch_data))

        # get current completed sequence and module
        if batch_data:
            # get pack count for current batch
            pack_count_data = json.loads(get_packs_count_for_latest_batch(batch_data['id']))
            logger.info("IN get_pre_processing_wizard_sequence_module: pack_count_data {}".format(pack_count_data))
            if batch_data['sequence_no'] in constants.PRE_PROCESSING_MODULE_MAPPING.keys():
                current_module = constants.PRE_PROCESSING_MODULE_MAPPING[batch_data['sequence_no']]
                response_data = {'batch_id': batch_data['id'],
                                 'batch_name': batch_data['name'],
                                 'batch_status': batch_data['status'],
                                 'sequence_no': batch_data['sequence_no'],
                                 'current_module': current_module,
                                 'pack_count': pack_count_data['data']['pack_count']}
            elif batch_data['sequence_no'] == constants.PPP_SEQUENCE_IN_PROGRESS:
                response_data = {'batch_id': batch_data['id'],
                                 'batch_name': batch_data['name'],
                                 'batch_status': batch_data['status'],
                                 'sequence_no': constants.PPP_SEQUENCE_IN_PROGRESS,
                                 'current_module': 0,
                                 'pack_count': pack_count_data['data']['pack_count']}
        else:
            response_data = {'batch_id': None,
                             'batch_name': None,
                             'batch_status': None,
                             'sequence_no': constants.PPP_SEQUENCE_IN_PENDING,
                             'current_module': constants.PRE_PROCESSING_MODULE_MAPPING[
                                 constants.PPP_SEQUENCE_IN_PENDING],
                             'pack_count': None}
        logger.info("IN get_pre_processing_wizard_sequence_module: response_data {}".format(response_data))
        return create_response(response_data)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pre_processing_wizard_sequence_module: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_pre_processing_wizard_sequence_module: " + str(e))

    except Exception as e:
        logger.error("Error in get_drug_dimension {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pre_processing_wizard_sequence_module: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_pre_processing_wizard_sequence_module: " + str(e))


@log_args_and_response
def update_pre_processing_wizard_sequence(args: dict):
    """
        update sequence_no in batch_master when user click on next in canister_recommendation
    """
    try:
        sequence_no = args.get('sequence_no')
        batch_id = args.get('batch_id')
        # if API is called from schedule batch than save it as PPP_SAVE_ALTERNATE
        if sequence_no == constants.PPP_SEQUENCE_IN_PENDING:
            current_sequence_no = constants.PPP_SEQUENCE_SAVE_ALTERNATES
        else:
            current_sequence_no = sequence_no+1
        logger.debug("update_pre_processing_wizard_sequence update sequence {}".format(args["sequence_no"]))
        # update pre processing wizard sequence in batch master
        seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=int(current_sequence_no),
                                                                  batch_id=batch_id)
        logger.debug("In update_pre_processing_wizard_sequence: couch db update_sequence_no_for_pre_processing_wizard updated: {} for batch_id: {}".format(seq_status, batch_id))

        if seq_status:
            # update couch db timestamp for pack_pre processing wizard change
            couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=args)
            logger.debug("In update_pre_processing_wizard_sequence couch db  pre-processing-wizard-sequence updated: {}".format(couch_db_status))

        return create_response(seq_status)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_pre_processing_wizard_sequence: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_pre_processing_wizard_sequence: " + str(e))

    except Exception as e:
        logger.error("Error in update_pre_processing_wizard_sequence {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_pre_processing_wizard_sequence: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_pre_processing_wizard_sequence: " + str(e))


@retry(3)
def update_timestamp_couch_db_pre_processing_wizard(args):
    """
    Function to update timestamp couch db for pre processing wizard
    @param args: dict
    @return: status
    """
    logger.info("In update_timestamp_couch_db_pre_processing_wizard -- args: {}".format(args))
    system_id = args["system_id"]
    change_rx: bool = False

    try:
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = '{}'.format(constants.PRE_PROCESSING_WIZARD)
        table = cdb.get(_id=id)

        logger.info("previous table in pre-processing-wizard-sequence {}".format(table))
        if table is None:  # when no document available for given device_id
            table = {"_id": id, "type": 'pre-processing-wizard-sequence',
                     "data": dict()}

        table['data']['timestamp'] = get_current_date_time_millisecond()
        change_rx = args.get("change_rx", False)
        if change_rx:
            table['data'][constants.AUTO_REFRESH_BATCH_UUID_KEY] = uuid4().hex

        logger.info("updated table pre-processing-wizard-sequence  {}".format(table))
        cdb.save(table)
        return True, True

    except couchdb.http.ResourceConflict as e:
        logger.error(e, exc_info=True)
        logger.error("Function: update_timestamp_couch_db_pre_processing_wizard -- EXCEPTION: Document update conflict.")
        return False, False

    except RealTimeDBException as e:
        logger.error(e, exc_info=True)
        logger.error("Function: update_timestamp_couch_db_pre_processing_wizard -- EXCEPTION: Realtime DB conflict.")
        return False, False

    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error('Function: update_timestamp_couch_db_pre_processing_wizard -- Couch db update failed for '
                     'pre-processing-wizard-sequence')
        return False, False


@retry(3)
def update_notifications_couch_db_status(old_pharmacy_fill_id: List[int], company_id: int, file_id: int,
                                         old_template_id: int, new_template_id: int,
                                         autoprocess_template_flag: bool = False, new_pack_ids: List[int] = [],
                                         remove_action: bool = False, other_templates: list = []):
    notification_found: bool = False
    try:
        logger.info(
            "Inside update_notifications_couch_db_status... old_pharmacy_fill_id: {}, company_id: {},\
             file_id: {}, old_template_id: {}, new_template_id: {}, "
            "autoprocess_template_flag: {}, new_pack_ids: {}, remove_action: {}"
            .format(old_pharmacy_fill_id, company_id, file_id, old_template_id, new_template_id,
                    autoprocess_template_flag, new_pack_ids, remove_action))

        database_name: str = get_couch_db_database_name(company_id=company_id)
        cdb: Database = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        logger.info("Update CouchDB for Notifications update for Deleted Old Packs and map them with New Template...")
        update_template_dict: Dict[str, Any] = dict()
        document_old_template_id: int
        change_rx: bool = False
        file_id_update_done: bool = False

        # for couch_db_document in settings.NOTIFICATIONS_DOCUMENT_ALL:
        document_id: str = "notifications_{}_all".format(settings.DOSEPACK)
        logger.debug("Check the Document: {}".format(document_id))
        table = cdb.get(_id=document_id)

        # logger.debug("Check the Table: {}".format(table))
        if table:
            if not remove_action:
                file_id_update_done = False
                # TODO: Code is commented because we are going to update notifications through Old Template ID
                # for pack_display_id in old_pharmacy_fill_id:
                #     logger.debug("Iterate : pack_display_id --  {}".format(pack_display_id))
                for index, notification in enumerate(table["data"]):
                    more_info_details = notification.get("more_info", None)
                    if more_info_details:
                        change_rx = more_info_details.get("change_rx", False)
                        logger.debug("change_rx :{}".format(change_rx))
                        if change_rx:
                            logger.debug("Perform Add Action to attach File ID...")
                            more_info_old_template_id = more_info_details.get("old_template_id", 0)
                            if old_template_id == more_info_old_template_id:
                                notification_found = True
                                if new_template_id > 0:
                                    update_template_dict = {"new_template_id": new_template_id,
                                                            "autoprocess_template": autoprocess_template_flag,
                                                            "other_templates": other_templates}
                                    table["data"][index]["more_info"].update(update_template_dict)
                                    file_id_update_done = True
                                    logger.info("Update CouchDB for Old Template ID: {} inside {} document is "
                                                "applied...".format(old_template_id, document_id))

                                if new_pack_ids:
                                    logger.debug("Update CouchDB by appending more packs to the existing Pack ID list."
                                                 "PackIDs: {}".format(new_pack_ids))
                                    existing_pack_ids = more_info_details.get("pack_ids", [])
                                    logger.debug("Existing pack IDs: {}".format(existing_pack_ids))
                                    if not existing_pack_ids:
                                        table["data"][index]["more_info"].setdefault(["pack_ids"], [])

                                    for pack in new_pack_ids:
                                        table["data"][index]["more_info"]["pack_ids"].append(pack)
                                break

                # TODO: Code is commented because now we have only one for loop to break
                # if file_id_update_done:
                #     break
            else:
                logger.debug("CouchDB Document: {}. Perform Delete Action to remove the data from Couch DB for "
                             "Old Template ID: {}...".format(document_id, old_template_id))
                for index, notification in enumerate(table["data"]):
                    more_info_details = notification.get("more_info", None)
                    if more_info_details:
                        document_old_template_id = more_info_details.get("old_template_id", None)
                        if document_old_template_id:
                            if document_old_template_id == int(old_template_id):
                                logger.debug("Old Template ID {} found and now removing the associated dictionary from "
                                             "CouchDB...".format(old_template_id))
                                table["data"].pop(index)

        cdb.save(table)
        logger.info("Notification Response: {}".format(notification_found))
        return True, notification_found
    except Exception as ex:
        logger.error("update_notifications_couch_db_status: Issue with CouchDB Document update.")
        logger.error("Issues while executing couchdb reference implementation." + str(ex))
        return False, False


@log_args_and_response
def update_couch_db_replenish_wizard(args):
    """
    function to update batch_uuid in replenish-wizard
    :param args:
    :return:
    """
    logger.debug(f"update_couch_db_replenish_wizard for canister: {args['canister_id']}")
    try:
        company_id = args["company_id"]
        device_id = args["device_id"]

        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = '{}'.format(constants.REPLENISH_WIZARD+"-"+str(device_id))
        table = cdb.get(_id=id)

        logger.info("In update_couch_db_replenish_wizard , previous table: {}".format(table))
        if table is None:  # when no document available for given device_id
            table = {"_id": id, "type": 'replenish-wizard',
                     "data": dict()}

        table['data']['batch_uuid'] = uuid4().hex

        logger.info("In update_couch_db_replenish_wizard, updated table replenish-wizard {}".format(table))

        cdb.save(table)
        return True
    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return error(1000, "Document update conflict.")

    except RealTimeDBException as e:
        return error(1000, str(e))

    except Exception as e:
        logger.error(e)
        raise Exception('Error in update_couch_db_replenish_wizard, Couch db update failed for replenish-wizard')


# @functools.lru_cache(maxsize=100)
def get_user_from_header_token():
    try:
        token = get_token()
        if token == '' or token is None:
            raise TokenMissingException

        logger.info('Getting current user data by token')
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.GET_CURRENT_USER,
                                       parameters={"access_token": token},
                                       use_ssl=settings.AUTH_SSL)
        if not status:
            logger.error("Error in getting user details. Response: " + str(data))
            return None
        if not data["status"] == 'failure':
            response = data["data"]
            return response

        logger.error(data)
        return None
    except Exception as e:
        logger.error(e, exc_info=True)
        return None


@log_args_and_response
def update_assigned_to_in_notification_dp_all_for_change_rx_packs(template_ids, assigned_to, company_id):
    notification_found = False

    try:
        logger.info("Inside update_assigned_to_in_notification_dp_all_for_change_rx_packs...")

        database_name: str = get_couch_db_database_name(company_id=company_id)
        cdb: Database = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        logger.info("Update CouchDB Notifications for new changeRx packs assigning to user...")

        # for couch_db_document in settings.NOTIFICATIONS_DOCUMENT_ALL:
        document_id: str = "notifications_{}_all".format(settings.DOSEPACK)
        logger.debug("Check the Document: {}".format(document_id))
        table = cdb.get(_id=document_id)

        # logger.debug("Check the Table: {}".format(table))
        if table["data"]:
            for index, notification in enumerate(table["data"]):
                more_info_details = notification.get("more_info", None)
                if more_info_details:
                    document_new_template_id = more_info_details.get("new_template_id", None)
                    if document_new_template_id:
                        if document_new_template_id in template_ids:
                            logger.debug("Before updating assigned to in notification_dp_all for index, table {}".format(table["data"][index]))

                            logger.debug("Old Template ID {} found and updaing assigned to "
                                         "CouchDB...".format(document_new_template_id))
                            update_notification = {'new_pack_assigned_to': assigned_to }
                            table["data"][index]["more_info"].update(update_notification)
                            notification_found = True
                            logger.debug("After updating assigned to in notification_dp_all for index, table {}".format(table["data"][index]))

        cdb.save(table)
        logger.info("Notification Response: {}".format(notification_found))
        return True, notification_found

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return error(1000, "Document update conflict.")
    except RealTimeDBException as e:
        return error(1000, str(e))
    except Exception as e:
        logger.error(e)
        raise Exception('Error in update_assigned_to_in_notification_dp_all_for_change_rx_packs, Couch db update failed.')


@log_args_and_response
def update_mfd_error_notification(args):
    """
    :param args:
    :return:
    """
    try:
        system_id = args["system_id"]
        device_id = args["device_id"]
        modified_time = args['modified_time']
        error_data = args['error_data']
        if not error_data:
            logger.info("In update_mfd_error_notification , resetting table")

        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = '{}'.format(constants.MFD_TRANSFERS_ERROR+"-"+str(device_id))
        table = cdb.get(_id=id)

        logger.info("In update_mfd_error_notification , previous table: {}".format(table))
        if table is None:  # when no document available for given device_id
            table = {"_id": id, "type": constants.MFD_TRANSFERS_ERROR,
                     "data": {"error_data": dict(), "modified_time": modified_time}}

        table['data']['modified_time'] = modified_time
        table['data']['error_data'] = error_data

        logger.info("In update_mfd_error_notification, updated table mfd-transfers-error {}".format(table))

        cdb.save(table)
        return True
    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict. update_mfd_error_notification")
        return error(1000, "Document update conflict.")

    except RealTimeDBException as e:
        return error(1000, str(e))

    except Exception as e:
        logger.error(e)
        raise Exception('Error in update_mfd_error_notification, Couch db update failed for replenish-wizard')

