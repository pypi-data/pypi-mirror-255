import datetime

from peewee import InternalError, IntegrityError, DoesNotExist, DataError, JOIN_LEFT_OUTER, fn

import settings
from couch_db_implementation import PrintJobStoreDocument
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import log_args_and_response, get_current_date, get_current_time
from src.model.model_pack_details import PackDetails
from realtime_db.dp_realtimedb_interface import Database
from src.dao.couch_db_dao import get_couch_db_database_name
from src.exceptions import RealTimeDBException
from src.model.model_facility_master import FacilityMaster
from src.model.model_patient_master import PatientMaster
from src.model.model_print_queue import PrintQueue
from src.model.model_printers import Printers

logger = settings.logger


@log_args_and_response
def get_associated_printers_dao(system_id):
    try:
        data = Printers.get_associated_printers(system_id)
        return data
    except Exception as e:
        logger.exception(f"Exception in get_associated_printers_dao: {e}", exc_info=True)
        raise e


@log_args_and_response
def db_get_by_printer_type(printer_type, system_id):
    try:
        printer = Printers.get(printer_type_id=printer_type, system_id=system_id)
        return printer
    except DoesNotExist:
        logger.info("No printer found for system_id: {} and printer_type: {}".format(system_id, printer_type))
    except Exception as e:
        logger.exception(f"Exception in db_get_by_printer_type: {e}", exc_info=True)


@log_args_and_response
def db_get_by_printer_code(unique_code, system_id):
    try:
        printer = Printers.get(unique_code=unique_code, system_id=system_id)
        return printer
    except DoesNotExist:
        logger.info("No printer found for system_id: {} and printer_code: {}".format(system_id, unique_code))
    except Exception as e:
        logger.exception(f"Exception in db_get_by_printer_type: {e}", exc_info=True)


@log_args_and_response
def add_printer_in_db(printer_name, printer_type, unique_code, ip_address, system_id):
    try:

        with db.transaction():
            # check for unique code
            response = {'added': False, "unique_code": None, "id": None}

            if not Printers.check_unique_code_exists(unique_code):
                # check for ip address for given system
                if not Printers.check_ip_exists_for_given_system(ip_address, system_id):
                    data = Printers.db_create_record({
                        "printer_name": printer_name,
                        "ip_address": ip_address,
                        "unique_code": unique_code,
                        "system_id": system_id,
                        "printer_type_id": printer_type
                    }, Printers, get_or_create=False)

                    response["added"] = True
                    response["unique_code"] = unique_code
                    response["id"] = data.id

        return response
    except Exception as e:
        logger.exception(f"Exception in add_printer_in_db: {e}", exc_info=True)
        raise e


@log_args_and_response
def rename_printer_in_db(existing_printer_name, new_printer_name, system_id):
    """
    This method renames the printer_name with new name based on the existing printer_name and system_id
    @param existing_printer_name:
    @param new_printer_name:
    @param system_id:
    @return:
    """
    try:
        query = Printers.update(printer_name=new_printer_name).where(Printers.printer_name == existing_printer_name,
                                                                     Printers.system_id == system_id).execute()
        return query
    except DoesNotExist:
        logger.info("No printer found for system_id: {} and printer_name: {}".format(system_id,
                                                                                     existing_printer_name))
        return None
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def update_printer_in_db(printer_info, unique_code):
    try:
        with db.transaction():
            status = Printers.update(**printer_info) \
                .where(Printers.unique_code == unique_code).execute()
            return status
    except Exception as e:
        logger.exception(f"Exception in update_printer_in_db: {e}", exc_info=True)
        return False


@log_args_and_response
def delete_printer_from_db(system_id, unique_code):
    try:
        with db.transaction():
            data = Printers.delete().where(Printers.unique_code == unique_code,
                                           Printers.system_id == system_id).execute()
            return data
    except Exception as e:
        logger.exception(f"Exception in update_printer_in_db: {e}", exc_info=True)
        return False


@log_args_and_response
def update_printer_count(reset_printer_count, printer_unique_code, system_id, record_id_list, printing_status):
    try:
        update_status = False
        if printing_status == settings.PRINT_STATUS['Done']:
            # when label printed
            count = len(record_id_list)

            if reset_printer_count:
                update_status = Printers.update(print_count=count).where(
                    Printers.unique_code == printer_unique_code, Printers.system_id == system_id).execute()
            else:
                update_status = Printers.update(print_count=Printers.print_count + count).where(
                    Printers.unique_code == printer_unique_code, Printers.system_id == system_id).execute()

        elif reset_printer_count:
            # handle case when we have to reset print count and printing status is not Done.
            # this can be the case when printer counts overhead and printer is offline or no papers available
            update_status = Printers.update(print_count=settings.RESET_PRINT_COUNT_VALUE).where(
                Printers.unique_code == printer_unique_code, Printers.system_id == system_id).execute()

        return update_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.exception(f"Exception in update_printer_count: {e}", exc_info=True)

    except Exception as e:
        logger.exception(f"Exception in update_printer_count: {e}", exc_info=True)


@log_args_and_response
def get_printed_tasks(record_ids, lastdatetime='00:00:00'):
    try:
        data = []
        lastdate = str(get_current_date())
        if lastdatetime is None:
            lasttime = str(get_current_time())
        else:
            lasttime = lastdatetime

        filter_timestamp = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        filter_date = filter_timestamp.date()

        for record in PrintQueue.select(
                FacilityMaster.facility_name,
                PatientMaster.last_name,
                PatientMaster.first_name,
                PrintQueue.patient_id,
                PrintQueue.pack_display_id,
                PrintQueue.id,
                PrintQueue.pack_id,
                PrintQueue.printing_status,
                PrintQueue.created_by,
                PrintQueue.created_date,
                PrintQueue.created_time,
                PrintQueue.filename,
                PrintQueue.page_count,
                Printers.printer_name,
                Printers.printer_type_id,
                Printers.unique_code).dicts() \
                .join(PatientMaster, JOIN_LEFT_OUTER, on=(PatientMaster.id == PrintQueue.patient_id)) \
                .join(FacilityMaster, JOIN_LEFT_OUTER, on=(FacilityMaster.id == PatientMaster.facility_id)) \
                .join(Printers, JOIN_LEFT_OUTER, on=(Printers.unique_code == PrintQueue.printer_code)) \
                .where(PrintQueue.file_generated == 1, PrintQueue.id << record_ids) \
                .order_by(PrintQueue.created_date.asc(), PrintQueue.created_time.asc()):
            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["created_date"] = datetime.datetime.combine(record["created_date"], record["created_time"])

            data.append(record)
            # for 24 hrs implementation
            # if record["created_date"] >= filter_timestamp:
            #     data.append(record)

        return data
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        raise DoesNotExist(ex)
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError(e)


@log_args_and_response
def get_print_count(company_id, from_date, to_date, offset):
    """
    @param company_id:
    @param from_date:
    @param to_date:
    @param offset:
    @return:
    """
    date_print_count_dict = dict()
    try:
        print_queue_date_time = fn.CONVERT_TZ(fn.CONCAT(PrintQueue.created_date, ' ',
                                             PrintQueue.created_time), settings.TZ_UTC, offset)

        print_count_query = PrintQueue.select(fn.SUM(PrintQueue.page_count).alias('per_day_page_count'),
                                              fn.DATE(print_queue_date_time).alias('date')) \
            .join(PackDetails, on=PackDetails.id == PrintQueue.pack_id).dicts() \
            .where(PrintQueue.printing_status == settings.PRINT_STATUS['Done'],
                   print_queue_date_time.between(from_date, to_date),
                   PackDetails.company_id == company_id) \
            .group_by(fn.DATE(print_queue_date_time))

        logger.info("In get_print_count: print_count_query: {}".format(print_count_query))
        for record in print_count_query:
            date_print_count_dict[record['date']] = record['per_day_page_count']
        return date_print_count_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_latest_print_record(pack_ids):
    """
    Returns latest record of pack label from print_queue table
    :param pack_ids:
    :return:
    """
    try:
        print_sub_query = PrintQueue.select(fn.MAX(PrintQueue.id).alias('max_id'),
                                            PrintQueue.pack_id.alias('print_pack_id')) \
            .group_by(PrintQueue.pack_id).alias('sub_query')
        print_data = PrintQueue.select().dicts() \
            .join(print_sub_query, on=PrintQueue.id == print_sub_query.c.max_id) \
            .where(PrintQueue.pack_id << pack_ids)
        return print_data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def update_task_status(record_id_list, status):
    try:
        data = PrintQueue.db_update_task_status(record_id_list, status)
        return data
    except Exception as e:
        logger.exception(f"Exception in update_task_status: {e}", exc_info=True)
        raise e


def add_printers_in_couch_db(system_id, printer):
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

        # append new printers
        settings.PRINTER_INFO_DOC.setdefault('type', settings.CONST_PRINTER_INFO_TYPE)
        settings.PRINTER_INFO_DOC.setdefault('data', {})
        settings.PRINTER_INFO_DOC['data'].setdefault("printers", [])
        settings.PRINTER_INFO_DOC["data"]["printers"].append(printer)

        # now save the document
        settings.PRINTER_INFORMATION_DOCUMENT_OBJ.update_document(settings.PRINTER_INFO_DOC)
        print('added printer in couch_db')
        logger.info('added printer in couch_db for system id' + str(system_id))

    except Exception as ex:
        print("Issues while executing couchdb reference implementation.", ex)
        logger.error("Issues while executing couchdb reference implementation." + str(ex))
        raise
