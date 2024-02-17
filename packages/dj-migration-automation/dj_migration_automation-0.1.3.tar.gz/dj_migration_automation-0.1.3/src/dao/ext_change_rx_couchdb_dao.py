import logging
from typing import Dict, Any
from uuid import uuid4

import couchdb
from peewee import IntegrityError, InternalError

import settings
from dosepack.utilities.utils import log_args_and_response, retry
from realtime_db.dp_realtimedb_interface import Database
from src import constants
from src.constants import CHANGE_RX_TEMPLATE_COUCH_DB
from src.dao.generate_templates_dao import db_get_ext_change_rx_by_template
from src.exceptions import RealTimeDBException
from src.model.model_template_master import TemplateMaster
from src.service.misc import get_couch_db_database_name, update_notifications_couch_db_status

logger = logging.getLogger("root")


@log_args_and_response
def update_notifications_couch_db_green_status(file_id: int, patient_id: int, company_id: int):
    try:
        template_data: Dict[str, Any] = TemplateMaster.db_get_template_id(file_id=file_id, patient_id=patient_id)

        if template_data:
            ext_change_rx_data: Dict[str, Any] = db_get_ext_change_rx_by_template(template_data["id"])
            ext_change_rx_id: int = ext_change_rx_data.get("ext_change_rx_id", None)

            # TODO: We have commented the below code as we are not removing any notification as of now.
            # TODO: As, these are not going to appear on Notifications area.
            # if ext_change_rx_id:
            #     logger.debug("Update CouchDB notifications document to remove Notifications for File ID: {} "
            #                  "and Patient ID: {} ".format(file_id, patient_id))
            #     update_notifications_couch_db_status(old_pharmacy_fill_id=[], company_id=company_id, file_id=file_id,
            #                                          remove_action=True)

            # Update Couch DB for incoming New Template or Change Rx Template document
            logger.debug("Update CouchDB document along with uuid for New or Change Rx Template...")
            update_customize_template_couch_db_status(company_id=company_id, file_id=file_id,
                                                      patient_id=patient_id, add_flag=False)

    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise Exception


@retry(3)
def update_couch_db_batch_distribution_status(company_id: int, refresh_screen: int):
    logger.info("Inside update_couch_db_batch_distribution_status -- company_id: {}, refresh_screen: {}"
                .format(company_id, refresh_screen))
    database_name: str
    cdb: Database
    doc_id: str = CHANGE_RX_TEMPLATE_COUCH_DB
    table: Dict[str, Any]

    try:
        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        table = cdb.get(_id=doc_id)

        if table is None:
            table = {"_id": doc_id, "type": str(doc_id)}

        if refresh_screen == constants.REFRESH_BATCH_DISTRIBUTION:
            table.update({constants.AUTO_REFRESH_BATCH_UUID_KEY: uuid4().hex})
        elif refresh_screen == constants.REFRESH_PACK_QUEUE:
            table.update({constants.AUTO_REFRESH_QUEUE_UUID_KEY: uuid4().hex})

        logger.info("updated table in couch db doc {} - {}".format(doc_id, table))
        cdb.save(table)
        logger.info("updated successfully for update_couch_db_batch_distribution_status")

        return True, True
    except couchdb.http.ResourceConflict as e:
        logger.error(e, exc_info=True)
        logger.error("EXCEPTION: update_couch_db_batch_distribution_status -- Document update conflict.")
        return False, False

    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error('update_couch_db_batch_distribution_status -- General Exception, Couch db update failed')
        return False, False


@retry(3)
def update_customize_template_couch_db_status(company_id: int, file_id: int, patient_id: int, add_flag: bool = True):
    """
    * This function updates the couchDB with the Change Rx details related to File ID and Patient ID.
    * It also takes care of adding or removing the data from CouchDB.
    """
    logger.info("Inside update_customize_template_couch_db_status -- company_id: {}, file_id: {}, patient_id: {}, "
                "add_flag: {}".format(company_id, file_id, patient_id, add_flag))
    database_name: str
    cdb: Database
    doc_id: str = CHANGE_RX_TEMPLATE_COUCH_DB
    table: Dict[str, Any]
    data_update_flag: bool = False
    try:
        database_name = get_couch_db_database_name(company_id=company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        table = cdb.get(_id=doc_id)

        if table is None:
            if add_flag:
                table = {"_id": doc_id, "type": str(doc_id),
                         "data": {file_id: {"patient_id": patient_id, "uuid": uuid4().hex}}}
                data_update_flag = True
        else:
            couchdb_update_dict: Dict[int, Dict[str, Any]]
            if file_id not in table["data"].keys():
                if add_flag:
                    couchdb_update_dict = {file_id: {"patient_id": patient_id, "uuid": uuid4().hex}}
                    table["data"].update(couchdb_update_dict)
            else:
                if add_flag:
                    table["data"][file_id]["uuid"] = uuid4().hex
                else:
                    table["data"].pop(file_id)

            data_update_flag = True

        logger.info("updated table in couch db doc {} - {}".format(doc_id, table))
        if data_update_flag:
            cdb.save(table)
        return True, True

    except couchdb.http.ResourceConflict as e:
        logger.error(e, exc_info=True)
        logger.error("EXCEPTION: Document update conflict.")
        return False, False

    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error('Couch db update failed')
        return False, False
