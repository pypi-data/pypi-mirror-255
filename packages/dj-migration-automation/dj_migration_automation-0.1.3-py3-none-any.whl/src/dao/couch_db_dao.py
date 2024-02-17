import functools

import couchdb

import settings
from couch_db_implementation import CouchDBDocument
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import call_webservice, retry, log_args_and_response
from dosepack.validation.validate import validate
from realtime_db.dp_realtimedb_interface import Database
from src import constants
from src.exceptions import RealTimeDBException

logger = settings.logger


def initialize_couch_db_doc(doc_id, system_id=None, company_id=None):
    """
    Returns document from couch db
    - at least and only one of the system_id or company_id must be present in arg
    :param doc_id: The id of couch db document to be initialized
    :param system_id: The id of system
    :param company_id: The id of system
    :return: CouchDBDocument
    """

    db_name = get_couch_db_database_name(system_id=system_id, company_id=company_id)
    if not db_name:
        logger.error("Couldn't fetch couch db name")
        raise RealTimeDBException("Couldn't fetch couch db name")
    logger.info(db_name)
    logger.info(settings.CONST_COUCHDB_SERVER_URL)
    logger.info(db_name)
    cdb = Database(settings.CONST_COUCHDB_SERVER_URL, db_name)
    try:
        cdb.connect()
    except TimeoutError as e:
        logger.error(e, exc_info=True)
        raise RealTimeDBException("Timeout error while connecting to couch db")
    couchdb_doc = CouchDBDocument(cdb, doc_id)
    couchdb_doc.initialize_doc()
    return couchdb_doc


# @functools.lru_cache(maxsize=256)
def get_couch_db_database_name(system_id=None, company_id=None):
    """
    Returns couch db database name for given system id or company_id
    :param system_id: int System ID
    :param company_id: int Company ID
    :return: str | None
    """
    logger.debug("Inside get_couch_db_database_name system {} company {}".format(system_id, company_id))
    if not system_id and not company_id:
        raise ValueError('system_id or company_id is required')  # one of the arg is required

    if company_id:
        return "company-{}".format(company_id)  # couch db name for company
    try:
        logger.info('Getting couch-db-name')
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.GET_SYSTEM_URL,
                                       parameters={"system_id": system_id}, use_ssl=settings.AUTH_SSL)
        if not status:
            logger.error("Error in getting db name. Response: " + str(data))
            return None
        if not data["status"] == 'failure':
            response = data["data"]
            if response["status"]:
                system_code = response["system_code"]
                db_name = 'config-db-' + str(system_code)
                return db_name

        logger.error(data)
        return None
    except Exception as e:
        logger.error("error in get_couch_db_database_name {}".format(e))
        return None


@retry(3)
def get_document_from_couch_db(document_name, system_id=None, company_id=None):
    """
    returns couch-db document of a particular system
    :param document_name: str
    :param system_id: int
    :param company_id: int
    :return: dict
    """
    try:
        logger.info(f"In get_document_from_couch_db, document_name: {document_name}")
        if system_id is None and company_id is None:
            return False, False
        document = initialize_couch_db_doc(document_name,
                                           system_id=system_id,
                                           company_id=company_id)
        return True, document
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error("error in get_document_from_couch_db {}".format(e))
        return False, False


@log_args_and_response
@validate(required_fields=["document_name", "key_name", "couchdb_level"])
def reset_couch_db_document(args):
    logger.debug("in reset_couch_db_document: found args - {}".format(args))
    document_name = args.get("document_name", None)
    key_name = args.get("key_name", None)
    couchdb_level = args.get("couchdb_level", None)
    company_id = args.get("company_id", None)
    system_id = args.get("system_id", None)

    if not company_id and not system_id:
        logger.debug("missing company_id and system_id")
        return error(1002, "any one of company_id or system_id is required")

    try:
        if couchdb_level == constants.STRING_COMPANY:
            logger.debug("company level database")
            # document = initialize_couch_db_doc(doc_id=document_name,
            #                                    company_id=company_id)
            db_name = get_couch_db_database_name(company_id=company_id)
        elif couchdb_level == constants.STRING_SYSTEM:
            logger.debug("system level database")
            # document = initialize_couch_db_doc(doc_id=document_name,
            #                                    system_id=system_id)
            db_name = get_couch_db_database_name(system_id=system_id)

        else:
            logger.error("found couchdb_level other than company and system")
            return error(1000, "invalid couchdb_level")

        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, db_name)
        cdb.connect()
        table = cdb.get(_id=document_name)

        logger.debug("couch db doc: {}".format(str(document_name)))

        if table is not None:
            if 'data' in table:
                if key_name == "data":
                    table['data'] = {}
                elif str(key_name) in table['data']:
                    logger.debug("clearing key: " + str(key_name))
                    if type(table['data'][str(key_name)]) == dict:
                        table['data'][str(key_name)] = dict()
                    elif type(table['data'][str(key_name)]) == list:
                        table['data'][str(key_name)] = list()
                    elif type(table[str(key_name)]) == set:
                        table['data'][str(key_name)] = set()
                    else:
                        table['data'][str(key_name)] = None
                else:
                    logger.error("key- {} not found in doc".format(key_name))
                cdb.save(table)
                logger.debug("couch db doc updated")
        return create_response(True)

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return error(1000, "Document update conflict.")
    except RealTimeDBException as e:
        logger.error("error in reset_couch_db_document {}".format(e))
    except Exception as e:
        logger.error("error in reset_couch_db_document {}".format(e))
        return error(1000, "Error while clearing couch db doc: " + str(e))
