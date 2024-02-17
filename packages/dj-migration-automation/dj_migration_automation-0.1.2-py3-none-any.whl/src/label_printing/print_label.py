# -*- coding: utf-8 -*-
"""
    src.print_label
    ~~~~~~~~~~~~~~~~

    This is the core label printing module which takes care of printing the label.

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""
import logging
import os
import random
import subprocess

from peewee import IntegrityError, InternalError, fn, DoesNotExist

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import get_current_date, get_current_time, batch, get_current_date_time, \
    log_args_and_response
from dosepack.validation.validate import validate
from src.dao.alternate_drug_dao import get_canister_by_id_dao
from src.dao.canister_dao import get_serial_number_from_canister_id, db_update_canister_master_label_print_time, \
    get_expired_drug_info
from src.dao.pack_dao import update_pack_details, get_pack_grid_type, call_to_ips_for_label
from src.dao.print_label_dao import get_print_job_cdb_data, update_print_job_cdb_data_for_cron_job
from src.label_printing.canister_label import canister_dir, generate_canister_label, generate_canister_label_v3, \
    generate_expired_drug_label, expired_drug_label_dir
from src.label_printing.generate_label import remove_files
from src.label_printing.pack_error_label import pack_error_dir, generate_pack_error_label
from src.label_printing.pack_label import generate_packid_sticker
from print_queue import add_print_jobs_in_couch_db
from print_queue import (execute_job, add_label_count_jobs_in_couch_db, remove_label_count_jobs_from_couch_db)
from src import constants
from src.cloud_storage import blob_exists, create_blob, pack_error_blob_dir, canister_label_dir
from src.dao.drug_dao import db_get_unique_drugs
from src.dao.print_dao import get_latest_print_record
from src.exc_thread import ExcThread
from src.model.model_canister_master import CanisterMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_print_queue import PrintQueue
from src.service.print import db_get_printer
logger = settings.logger

try:
    import winreg as winreg
except ImportError:
    pass

try:
    import cPickle as pickle
except ImportError as ex:
    import pickle

from src.service.notifications import Notifications

# get the logger for the pack from global configuration file logging.json
logger = logging.getLogger("root")
packsticker_dir = os.path.join('pack_id_stickers')


@validate(required_fields=["print_queue_id"])
def get_print_queue_data(search_filters):
    """
    Returns print queue record

    :param search_filters:
    :return: json
    """
    print_queue_id = search_filters["print_queue_id"]

    try:
        print_queue_data = PrintQueue.db_get_by_id(print_queue_id)
        return create_response(print_queue_data)
    except (IntegrityError, InternalError):
        return error(2001)


@validate(required_fields=["pack_id", "system_id", "patient_id",
                           "pack_display_id", "printer_code"])
def print_pack_label(dict_input_args, packs_in_print_queue=None, bulk_print=False):
    """ Takes the parameter for label printing and prints the label.

        Args:
            dict_input_args(dict): The input parameters for the label printing.

        Returns:
           Boolean: True or False

        Examples:
            >>> print_pack_label(1, 1, 'admin', 1)
                []
    """
    logger.info("dict input args {}".format(dict_input_args))
    generate_locally = dict_input_args.pop('generate_locally')
    pack_id = dict_input_args["pack_id"]
    system_id = dict_input_args["system_id"]
    patient_id = dict_input_args["patient_id"]
    printer_code = dict_input_args["printer_code"]
    force_regenerate = dict_input_args.pop('force_regenerate', False)
    add_in_rtdb = dict_input_args.get("add_in_rtdb", True)
    print_job_list = dict_input_args.get("print_job_list", None)
    thread_based = dict_input_args.get("thread_based", True)
    dry_run = bool(int(dict_input_args.get("dry_run", 0)))
    ips_username = dict_input_args.get("ips_username", None)
    if packs_in_print_queue is None:
        packs_in_print_queue = list()

    if dry_run:
        logger.info("Dry run crm")
        if printer_code and system_id:
            # todo- replace pack_id=0 with pack_id = pack_id when changes done from utility
            test_print_label(printer_code=printer_code, system_id=system_id, pack_id=0, dry_run=dry_run)
        return create_response(0)

    printer = db_get_printer(printer_code, system_id)

    if not printer:
        return error(6002)

    # pending_print_data = PrintQueue.get_pending_print_data(pack_id)
    # if len(pending_print_data) > 0:
    #     if bulk_print:
    #         packs_in_print_queue.append(pending_print_data[0]['pack_display_id'])
    #     return create_response({'6003': err[6003].format(pending_print_data[0]['pack_display_id'])})

    # Commenting to allow printing from different system_id
    # valid_pack = PackDetails.db_verify_pack_id_by_system_id(pack_id, system_id)
    # # if pack is not generated for given system id do not proceed
    # if not valid_pack:
    #     return error(1014)

    dict_input_args["slot_printing"] = 0
    user_id = dict_input_args["user_id"]

    # call the get_unique_drugs api and find the length of unique drugs available for given pack_id
    unique_drugs = db_get_unique_drugs(pack_id)
    total_unique_drugs = len(unique_drugs)
    extra_job = list()
    try:
        with db.transaction():
            if ips_username:
                update_ips_username = PackDetails.update(filled_by=ips_username) \
                    .where(PackDetails.id == pack_id).execute()
                logger.info(
                    "ips_username update requested for" + str(pack_id) + " updated count" + str(update_ips_username))
            filename = str(dict_input_args["pack_id"]) + ".pdf"
            if printer.printer_type_id == constants.PRINTER_TYPE_CRM:
                # if printed from DosePacker printer, then mark filled_at to DosePacker
                PackDetails.update(filled_at=11,
                                   modified_date=get_current_date_time()) \
                    .where(PackDetails.id == pack_id) \
                    .execute()
            page_count = 14 if total_unique_drugs > 14 else 1
            record = PrintQueue.db_create(
                dict_input_args["pack_id"],
                dict_input_args["patient_id"],
                dict_input_args["pack_display_id"],
                user_id,
                filename,
                printer.unique_code,
                page_count=page_count
            )

        print_job = [{
            "id": record.id,
            "pack_id": pack_id,
            "pack_display_id": record.pack_display_id,
            "patient_id": patient_id,
            "user_id": record.created_by,
            "system_id": printer.system_id
        }]
        if thread_based:
            exception_list = []
            t = ExcThread(exception_list, name="Thread: Label Generator " + str(record.id) + "PackID: " + str(pack_id),
                          target=execute_job,
                          args=[print_job, extra_job, generate_locally, force_regenerate, add_in_rtdb, print_job_list])
            t.start()
        else:
            execute_job(print_job, extra_job, generate_locally, force_regenerate, add_in_rtdb, print_job_list)
        # Notifications().print_label(pack_id);
        return create_response(record.id)
    except (InternalError, InternalError, IntegrityError) as ex:
        return error(2001, ex)


@validate(required_fields=["pack_ids", "system_id", "user_id"])
@log_args_and_response
def bulk_print_pack_label(packs_info):
    """
    Creates entry for packs into print_queue and Couch DB to notify DP-Utility
    :param packs_info: dict List of packs, system ID and User ID
    :return: str
    """
    global packs_in_print_queue
    pack_ids = packs_info["pack_ids"]
    system_id = packs_info["system_id"]
    user_id = packs_info["user_id"]
    printer_code = packs_info.get("printer_code", None)
    ips_username = packs_info.get("ips_username", None)
    label_queue = list()
    print_job_list = list()
    thread_list = list()
    pack_id_order = dict()
    bulk_print = True
    packs_in_print_queue = list()
    results = dict()

    try:
        logger.info("Input in db_get_printer {}, {}".format(printer_code, system_id))
        printer = db_get_printer(printer_code, system_id)
        logger.info("Output of db_get_printer {}".format(printer))
        if not printer:
            return error(6002)

        if pack_ids:
            order_fields = [PackDetails.id] + list(map(int, pack_ids))
            if ips_username:
                update_ips_username = PackDetails.update(filled_by=ips_username) \
                    .where(PackDetails.id << pack_ids).execute()
                logger.info(
                    "ips_username update requested for" + str(pack_ids) + " updated count" + str(update_ips_username))
            query = PackDetails.select(
                PackDetails.id.alias('pack_id'),
                PackDetails.pack_display_id,
                PackHeader.patient_id
            ).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .where(PackDetails.id << pack_ids) \
                .order_by(fn.FIELD(*order_fields))
            for index, record in enumerate(query):
                pack_id_order[record['pack_id']] = index
                label_queue.append({
                    'pack_id': record['pack_id'],
                    'system_id': system_id,
                    'patient_id': record['patient_id'],
                    'user_id': user_id,
                    'pack_display_id': record['pack_display_id'],
                    'generate_locally': True,
                    'printer_code': printer_code,
                    'add_in_rtdb': False,
                    'print_job_list': print_job_list,
                    'thread_based': False  # as we want to wait for job to added in print_job_list
                })
        if not label_queue:  # if no pack found in query return false
            return create_response(False)
        for items in batch(label_queue, n=int(os.environ.get("LABEL_BATCH_LIMIT", 25))):
            exception_list = list()
            for pack in items:
                t = ExcThread(
                    exception_list,
                    name="Thread: Pack Label Print Request - PackID: " + str(pack["pack_id"]),
                    target=print_pack_label, args=[pack, packs_in_print_queue, bulk_print]
                )
                thread_list.append(t)
                t.start()
        [t.join() for t in thread_list]  # wait for threads to finish
        if print_job_list:
            print_job_list.sort(key=lambda x: pack_id_order[x['pack_id']])
            add_print_jobs_in_couch_db(print_job_list, printer.system_id)
        # if len(packs_in_print_queue) > 0:
        #     results['6003'] = err[6003].format(','.join([str(item) for item in packs_in_print_queue]))
        # return create_response(results)
        Notifications().print_labels(pack_ids)
        return create_response(True)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.info(e)
        return e


def test_print_label(printer_code, system_id, pack_id=0, dry_run=False):
    """
    Adds print job in couch db for pack ID 0(Test)

    :param printer_code:
    :param system_id:
    :return: json
    """

    # return create_response(0)  # disabling test print label api

    try:
        printer = db_get_printer(printer_code, system_id)
    except InternalError:
        return error(2001)

    if not printer:  # No printer found
        return error(6002)

    test_label_name = 'test_label.pdf'
    random_id = random.randint(1, 1000000)

    test_job_data = [{
        "facility_name": "TEST",
        "last_name": "TEST",
        "first_name": "TEST",
        "patient_id": 0,
        "pack_display_id": pack_id,
        "id": random_id,
        "pack_id": pack_id,
        "printing_status": 0,
        "created_by": 1,
        "created_date": get_current_date(),
        "created_time": get_current_time(),
        "filename": test_label_name,
        "printer_name": printer.printer_name,
        "unique_code": printer_code,
        "patient_name": "TEST, TEST",
        "generate_locally": False,
        "dry_run": dry_run
    }]
    response = add_print_jobs_in_couch_db(test_job_data, printer.system_id)
    if response:  # If print job added
        return create_response(1)
    else:
        return create_response(0)


def send_to_printer(source_path, printer):
    """
        @function: incorrect_type
        @createdBy: Manish Agarwal
        @createdDate: 7/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 08/12/2015
        @type: function
        @param: str
        @purpose - returns incorrect type message
    """

    # Dynamically get path to AcroRD32.exe
    AcroRD32Path = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, 'Software\\Adobe\\Acrobat\Exe')

    acroread = AcroRD32Path

    # The last set of double quotes leaves the printer blank, basically defaulting
    # to the default printer for the system.
    cmd = '{0} /N /T "{1}" "{2}"'.format(acroread, source_path, printer)

    # See what the command line will look like before execution
    print(cmd)

    # Open command line in a different process other than ArcMap
    proc = subprocess.Popen(cmd)

    import time
    time.sleep(5)

    # Kill AcroRD32.exe from Task Manager
    os.system("TASKKILL /F /IM AcroRD32.exe")


@validate(required_fields=["pack_id"])
def generate_pack_sticker(pack_info):
    """
    Generates pack sticker if not present and returns generated file name

    :param canister_info:
    :return: json
    """

    pack_id = pack_info["pack_id"]
    sticker_name = 'retained_pack_' + str(pack_id) + '.pdf'

    # If file already exists return
    if blob_exists(sticker_name, packsticker_dir):
        response = {'sticker_name': sticker_name}
        return create_response(response)

    if not os.path.exists(packsticker_dir):
        os.makedirs(packsticker_dir)
    sticker_path = os.path.join(packsticker_dir, sticker_name)

    try:
        logger.info('Starting Pack Sticker Generation. Pack ID: {}'.format(pack_id))
        generate_packid_sticker(sticker_path, pack_id)
        create_blob(sticker_path, sticker_name, packsticker_dir)  # Upload sticker to central storage
        logger.info('Pack ID Sticker Generated. Pack ID: {}'.format(pack_id))
        response = {'sticker_name': sticker_name}
        return create_response(response)
    except Exception as e:
        logger.error('Pack sticker Generation Failed: ' + str(e), exc_info=True)
        return error(2006)
    finally:
        remove_files([sticker_path])


@validate(required_fields=["pack_id", "system_id", "patient_id", "pack_display_id", "printer_code"])
def print_pack_label_v3(dict_input_args):
    """
    Currently not in use
    :param dict_input_args:
    :return:
    """
    logger.info("dict input args {}".format(dict_input_args))
    generate_locally = dict_input_args.pop('generate_locally')
    pack_id = dict_input_args["pack_id"]
    system_id = dict_input_args["system_id"]
    patient_id = dict_input_args["patient_id"]
    printer_code = dict_input_args["printer_code"]
    force_regenerate = dict_input_args.pop('force_regenerate', False)
    add_in_rtdb = dict_input_args.get("add_in_rtdb", True)
    print_job_list = dict_input_args.get("print_job_list", None)
    thread_based = dict_input_args.get("thread_based", True)
    dry_run = bool(int(dict_input_args.get("dry_run", 0)))
    pack_display_id = dict_input_args["pack_display_id"]
    print_queue_id = dict_input_args["id"]
    user_id = dict_input_args["user_id"]

    if dry_run:
        logger.info("Dry run crm")
        if printer_code and system_id:
            # todo- replace pack_id=0 with pack_id = pack_id when changes done from utility
            test_print_label(printer_code=printer_code, system_id=system_id, pack_id=0, dry_run=dry_run)
        return create_response(0)

    printer = db_get_printer(printer_code, system_id)

    if not printer:
        return error(6002)

    dict_input_args["slot_printing"] = 0

    extra_job = list()
    try:
        with db.transaction():
            print_job = [{
                "id": print_queue_id,
                "pack_id": pack_id,
                "pack_display_id": pack_display_id,
                "patient_id": patient_id,
                "user_id": user_id,
                "system_id": printer.system_id
            }]
            if thread_based:
                exception_list = []
                t = ExcThread(exception_list,
                              name="Thread: Label Generator " + str(print_queue_id) + "PackID: " + str(pack_id),
                              target=execute_job,
                              args=[print_job, extra_job, generate_locally, force_regenerate, add_in_rtdb,
                                    print_job_list])
                t.start()
            else:
                execute_job(print_job, extra_job, generate_locally, force_regenerate, add_in_rtdb, print_job_list)
            # Notifications().print_label(pack_id);
            return create_response(print_queue_id)
    except (InternalError, InternalError, IntegrityError) as ex:
        return error(2001, ex)


def update_job_count(dict_input_args):
    """

    :param dict_input_args:
    :return:
    """
    logger.info("dict input args for update_job_count {}".format(dict_input_args))
    generate_locally = dict_input_args.pop('generate_locally', None)
    pack_count_dict = dict_input_args["pack_count_dict"]
    system_id = dict_input_args["system_id"]
    printer_code = dict_input_args.get("printer_code", None)
    user_id = dict_input_args["user_id"]
    force_regenerate = dict_input_args.pop('force_regenerate', False)
    add_in_cdb_jobs = dict_input_args.get("add_in_cdb_jobs", True)  # whether to add job in couch DB or not
    dry_run = bool(int(dict_input_args.get("dry_run", 0)))
    ips_username = dict_input_args.get("ips_username", None)
    if not pack_count_dict:
        return error(1020, "Pack Count can't be empty")
    label_queue = list()
    thread_list = list()
    try:
        pack_ids = list(map(int, pack_count_dict))
        if dry_run:
            logger.info("Dry run crm")
            if printer_code and system_id:
                # todo- replace pack_id=0 with pack_id = pack_id when changes done from utility
                test_print_label(printer_code=printer_code, system_id=system_id, pack_id=pack_ids[0], dry_run=dry_run)
            return create_response(0)

        printer = db_get_printer(printer_code, system_id)

        if not printer:
            return error(6002)

        with db.transaction():
            if ips_username:
                update_ips_username = PackDetails.update(filled_by=ips_username) \
                    .where(PackDetails.id << pack_ids).execute()
                logger.info("ips_username update requested for" + str(list(pack_count_dict)) + " updated count"
                            + str(update_ips_username))
            if printer.printer_type_id == constants.PRINTER_TYPE_CRM:
                # if printed from DosePacker printer, then mark filled_at to DosePacker
                PackDetails.update(filled_at=11,
                                   modified_date=get_current_date_time()) \
                    .where(PackDetails.id << list(pack_count_dict)) \
                    .execute()
            query = PackDetails.select(
                PackDetails.id.alias('pack_id'),
                PackDetails.pack_display_id,
                PackHeader.patient_id
            ).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .where(PackDetails.id << pack_ids)
            for record in query:
                filename = str(record["pack_id"]) + ".pdf"
                print_record = PrintQueue.db_create(
                    record["pack_id"],
                    record["patient_id"],
                    record["pack_display_id"],
                    user_id,
                    filename,
                    printer.unique_code,
                    page_count=pack_count_dict[str(record["pack_id"])]
                )
                if add_in_cdb_jobs:
                    label_queue.append({
                        'id': print_record.id,
                        'pack_id': record['pack_id'],
                        'system_id': system_id,
                        'patient_id': record['patient_id'],
                        'user_id': user_id,
                        'pack_display_id': record['pack_display_id'],
                        'generate_locally': True,
                        'printer_code': printer_code,
                        'add_in_rtdb': True,
                        'force_regenerate': force_regenerate,
                        'thread_based': False  # as we want to wait for job to added in print_job_list
                    })
        # for items in batch(label_queue, n=int(os.environ.get("LABEL_BATCH_LIMIT", 25))):
        #     exception_list = list()
        #     for pack in items:
        #         t = ExcThread(
        #             exception_list,
        #             name="Thread: Pack Label Print Request - PackID: " + str(pack["pack_id"]),
        #             target=print_pack_label_v3, args=[pack]
        #         )
        #         thread_list.append(t)
        #         t.start()
        # [t.join() for t in thread_list]
        print_pack_label_v2({"print_job": label_queue,
                             "generate_locally": generate_locally,
                             "force_regenerate": force_regenerate,
                             "system_id": system_id})

        if pack_ids:
            remove_label_count_jobs_from_couch_db(pack_ids, system_id)

            return create_response(True)
    except (IntegrityError, InternalError):
        return error(2001)


@validate(required_fields=["pack_ids", "system_id", "company_id"])
def add_label_count_request(dict_input_args):
    """

    :param dict_input_args:
    :return:
    """
    logger.info("dict input args for add_label_count_request {}".format(dict_input_args))
    # currently variables: force_regenerate & generate_locally are not in use. Remove them with optimization.
    generate_locally = dict_input_args.pop('generate_locally', False)
    force_regenerate = dict_input_args.pop('force_regenerate', False)

    pack_ids = dict_input_args["pack_ids"]
    company_id = dict_input_args["company_id"]
    system_id = dict_input_args["system_id"]
    printer_code = dict_input_args.get("printer_code", None)
    dry_run = bool(int(dict_input_args.get("dry_run", 0)))
    user_id = dict_input_args["user_id"]
    ips_username = dict_input_args.get("ips_username", None)
    add_in_cdb_jobs = dict_input_args.get("add_in_cdb_jobs", False)
    bubble_packs = []

    try:
        if dry_run:
            logger.info("Dry run crm")
            if printer_code and system_id:
                # todo- replace pack_id=0 with pack_id = pack_id when changes done from utility
                test_print_label(printer_code=printer_code, system_id=system_id, pack_id=0, dry_run=dry_run)
            return create_response(0)

        pack_with_grid_data = get_pack_grid_type(pack_ids)

        for pack in pack_with_grid_data:
            if pack["packaging_type"] in [constants.PACKAGING_TYPE_BLISTER_PACK_UNIT_8X4,
                                          constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_8X4,
                                          constants.PACKAGING_TYPE_BUBBLE_PACK]:
                pack_ids.remove(pack["id"])
                bubble_packs.append(pack["pack_display_id"])

        printer = db_get_printer(printer_code, system_id)
        if not printer:
            return error(6002)

        valid_packlist = list()
        job_data = list()

        with db.transaction():
            if pack_ids:
                pack_data = PackDetails.db_get_pack_data(pack_ids)
                for pack in pack_data:
                    if pack['company_id'] == int(company_id) and pack['id'] not in valid_packlist:
                        valid_packlist.append(pack['id'])
                        job_data.append({"pack_id": pack['id'],
                                         "user_id": user_id,
                                         "system_id": system_id,
                                         "printer_code": printer_code,
                                         "ips_username": ips_username,
                                         "force_regenerate": force_regenerate,
                                         "dry_run": dry_run,
                                         "generate_locally": generate_locally,
                                         "add_in_cdb_jobs": add_in_cdb_jobs})
            if set(pack_ids) != set(valid_packlist):
                return error(1014)

            if job_data:
                add_label_count_jobs_in_couch_db(job_data, system_id)

            if bubble_packs:
                status = call_to_ips_for_label(bubble_packs, company_id)

            return create_response(True)
    except (InternalError, InternalError, IntegrityError, Exception) as ex:
        return error(2001, ex)


def add_new_job_in_print_queue(pack_ids, user_id):
    """
    In case of reprint adding new data in print-queue for the same pack info. This is to maintain count of label being
    used in inventory management
    :param pack_ids:
    :param user_id:
    :return:
    """
    try:
        pack_count = 0
        # get the latest data of pack
        latest_print_data = get_latest_print_record(pack_ids=pack_ids)
        for record in latest_print_data:
            pack_count += 1

            # if printing has been done then add new record else it's normal call from CRM.
            logger.debug("For pack_id {} printing_status: {} ".format(record['pack_id'], record['printing_status']))
            if record['printing_status'] in [settings.PRINT_STATUS['Done'],
                                             settings.PRINT_STATUS['Cancelled'],
                                             settings.PRINT_STATUS['Error']]:
                logger.debug("For pack_id {} adding new record in print queue".format(record['pack_id']))
                print_record = PrintQueue.db_create(
                        record["pack_id"],
                        record["patient_id"],
                        record["pack_display_id"],
                        user_id,
                        record['filename'],
                        record['printer_code'],
                        file_generated=record['file_generated'],
                        page_count=record['page_count']
                    )
        if pack_count != len(pack_ids):
            raise ValueError('Print info missing')
    except (InternalError, InternalError, IntegrityError) as ex:
        raise ex


@log_args_and_response
@validate(required_fields=["pack_ids", "system_id", "user_id"])
def bulk_print_pack_label_v2(packs_info):
    """
    Creates entry for packs into print_queue and Couch DB to notify DP-Utility
    :param packs_info: dict List of packs, system ID and User ID
    :return: str
    """
    logger.info("dict input args for add_label_count_request {}".format(packs_info))
    pack_ids = packs_info["pack_ids"]
    system_id = packs_info["system_id"]
    user_id = packs_info["user_id"]
    printer_code = packs_info.get("printer_code", None)
    generate_locally = packs_info.pop('generate_locally', False)
    # system_id = dict_input_args["system_id"]
    # printer_code = dict_input_args.get("printer_code", None)
    ips_username = packs_info.get("ips_username", None)
    filled_at = packs_info.get("filled_at", None)
    force_regenerate = packs_info.pop('force_regenerate', False)
    dry_run = bool(int(packs_info.get("dry_run", 0)))
    label_queue = list()
    print_job_list = list()
    pack_id_order = dict()
    job_list = list()

    try:
        if dry_run:
            logger.info("Dry run crm")
            if printer_code and system_id:
                # todo- replace pack_id=0 with pack_id = pack_id when changes done from utility
                test_print_label(printer_code=printer_code, system_id=system_id, pack_id=int(pack_ids[0]), dry_run=dry_run)
            return create_response({'job_list': [0]})

        printer = db_get_printer(printer_code, system_id)
        if not printer:
            return error(6002)

        if pack_ids:
            add_new_job_in_print_queue(pack_ids, user_id)
            order_fields = [PackDetails.id] + list(map(int, pack_ids))

            # update printer code while req pack print from crm
            PrintQueue.update_printer_code(pack_ids, printer_code)

            if ips_username and filled_at:
                current_time = get_current_date_time()
                update_dict = {"filled_by": ips_username, "filled_at": filled_at, "filled_date": current_time}
                status = update_pack_details(update_dict=update_dict, pack_id=pack_ids)
                logger.info("In bulk_print_pack_label_v2: pack details updated for filled by and filled at: {}".format(status))

            query = PackDetails.select(
                PackDetails.id.alias('pack_id'),
                PackDetails.pack_display_id,
                PackHeader.patient_id,
                fn.MAX(PrintQueue.id).alias('job_id')
            ).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .join(PrintQueue, on=PrintQueue.pack_id == PackDetails.id) \
                .where(PackDetails.id << pack_ids) \
                .group_by(PrintQueue.pack_id) \
                .order_by(fn.FIELD(*order_fields))
            for index, record in enumerate(query):
                pack_id_order[record['pack_id']] = index
                job_list.append(record['job_id'])
                label_queue.append({
                    'id': record['job_id'],
                    'pack_id': record['pack_id'],
                    'system_id': system_id,
                    'patient_id': record['patient_id'],
                    'user_id': user_id,
                    'pack_display_id': record['pack_display_id'],
                    'generate_locally': True,
                    'printer_code': printer_code,
                    'add_in_rtdb': False,
                    'print_job_list': print_job_list,
                    'thread_based': False  # as we want to wait for job to added in print_job_list
                })
        if not label_queue:  # if no pack found in query return false
            return create_response(False)
        json_response = print_pack_label_v2({"print_job": label_queue,
                                             "generate_locally": generate_locally,
                                             "force_regenerate": force_regenerate,
                                             "system_id": system_id})
        Notifications().print_labels(pack_ids)
        return create_response({'job_list': job_list})
    except ValueError as e:
        if str(e) == 'Print info missing':
            return error(6003)
        return error(1020, str(e))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.info(e)
        return e


@validate(required_fields=["print_job"])
def print_pack_label_v2(dict_input_args):
    """

    :param dict_input_args:
    :return:
    """
    logger.info("dict input args {}".format(dict_input_args))
    generate_locally = dict_input_args.pop('generate_locally', False)
    print_job = dict_input_args["print_job"]
    # system_id = dict_input_args["system_id"]
    # printer_code = dict_input_args.get("printer_code", None)
    force_regenerate = dict_input_args.pop('force_regenerate', False)
    add_in_rtdb = dict_input_args.get("add_in_rtdb", True)
    print_job_list = dict_input_args.get("print_job_list", None)
    thread_based = dict_input_args.get("thread_based", True)
    # pack_display_id = dict_input_args["pack_display_id"]
    # print_queue_id = dict_input_args["id"]
    # user_id = dict_input_args["user_id"]

    try:
        with db.transaction():
            extra_job = []
            execute_job(print_job, extra_job, generate_locally, force_regenerate, add_in_rtdb, print_job_list)
            # Notifications().print_label(pack_id);
            return create_response(True)
    except (InternalError, InternalError, IntegrityError) as ex:
        return error(2001, ex)


@validate(required_fields=["drug_id", "location", "error_flag", "error_id"])
def get_pack_error_label(error_info):
    """
    Generates error label and returns error label name

    :param error_info:
    :return: json
    """
    error_id = error_info["error_id"]
    error_flag = error_info["error_flag"]
    location = error_info["location"]
    drug_id = error_info["drug_id"]
    label_name = error_flag + '_' + str(error_id) + '.pdf'

    if 'regenerate' not in error_info:  # flag to regenerate label forcefully
        # If file already exists return
        if blob_exists(label_name, pack_error_blob_dir):
            response = {'label_name': label_name}
            return create_response(response)

    try:
        drug_data = DrugMaster.select().dicts() \
            .where(DrugMaster.id == drug_id).get()
    except DoesNotExist:
        return error(1020)

    if not os.path.exists(pack_error_dir):
        os.makedirs(pack_error_dir)
    label_path = os.path.join(pack_error_dir, label_name)
    try:
        logger.info('Starting Pack Error Label Generation. Error ID: {} and Error Flag {}'
                    .format(error_id, error_flag))
        generate_pack_error_label(
            label_path,
            drug_data["drug_name"],
            str(drug_data["ndc"]),
            drug_data["strength"],
            drug_data["strength_value"],
            str(drug_data["imprint"]),
            location
        )
        # Upload label to central storage
        create_blob(label_path, label_name, pack_error_blob_dir)
        logger.info('Pack Error Label Generated. Error ID: {} and Error Flag {}'
                    .format(error_id, error_flag))
        response = {'label_name': label_name}
        return create_response(response)
    except Exception as e:
        logger.error('Pack Error Label Generation Failed: ' + str(e), exc_info=True)
        return error(2006)
    finally:
        remove_files([label_path])


@validate(required_fields=["canister_id"])
def _canister_label(canister_info):
    canister_id = canister_info["canister_id"]
    if isinstance(canister_id, int):
        response = get_canister_label(canister_info)

    elif isinstance(canister_id, list):
        response = get_canister_label_v3(canister_info)
    else:
        return error(2001, "canister_id format not supported.")

    return response


@validate(required_fields=["company_id", "print_details"])
@log_args_and_response
def expired_drug_label(args):
    """
    info_dict: [{"canister_id":1010, "expiry_date": "11-2023"},
                {},
                {},
                ...]
    """
    # expired_drug_label_dir = "/home/meditab/Desktop"
    try:
        company_id = args.get("company_id")
        info_dict = args.get("print_details")
        if len(info_dict) == 0:
            return error(1001)
        if len(info_dict) == 1:
            canister_id = info_dict[0]["canister_id"]
            expiry_date = info_dict[0].get("expiry_date", None)

            if expiry_date:
                expiry_date_l = expiry_date.split("-")
                label_name = str(canister_id) + "_" + str(expiry_date_l[0]) + "_" + str(expiry_date_l[1]) + ".pdf"
            else:
                label_name = str(canister_id) + "None" + ".pdf"
            if blob_exists(label_name, expired_drug_label_dir):
                logger.debug(f"expired_drug_label: label: {label_name} already exist on cloud")
                response = {'label_name': label_name}
                return create_response(response)
        else:
            label_name = "multi_canister_label.pdf"

        response = get_expired_drug_label(canister_expiry_dict=info_dict,
                                          label_name=label_name)
        return response
    except Exception as e:
        logger.error(f"Error in expired_drug_label, e: {e}")
        raise e


@validate(required_fields=["canister_id"])
@log_args_and_response
def get_canister_label(canister_info):
    """
    Generates canister label if not present, returns file name

    :param canister_info:
    :return: json
    """
    canister_id = canister_info["canister_id"]
    label_name = str(canister_id) + '.pdf'

    if 'regenerate' not in canister_info:  # flag to regenerate label forcefully
        # If file already exists return
        if blob_exists(label_name, canister_label_dir):
            logger.debug("canister_label: label already exist on cloud")
            response = {'label_name': label_name}
            return create_response(response)

    if not os.path.exists(canister_dir):
        os.makedirs(canister_dir)
    label_path = os.path.join(canister_dir, label_name)

    try:
        canister = get_canister_by_id_dao(canister_id)
    except (IntegrityError, InternalError) as e:
        logger.error(e)
        return error(2001)

    try:
        logger.info('Starting Canister Label Generation. Canister ID: {}'.format(canister_id))

        if len(str(canister["rfid"])) <= 12:
            canister_version = "v2"
        else:
            canister_version = "v3"

        if not ('big_stick_serial_number' in canister_info or 'small_stick_serial_number' in canister_info or
                'drum_serial_number' in canister_info):
            big_stick_serial_number, small_stick_serial_number, drum_serial_number = \
                get_serial_number_from_canister_id(canister_id)
            canister_info['big_stick_serial_number'] = big_stick_serial_number
            canister_info['small_stick_serial_number'] = small_stick_serial_number
            canister_info['drum_serial_number'] = drum_serial_number

        generate_canister_label(file_name=label_path,
                                drug_name=canister["drug_name"],
                                ndc=str(canister["ndc"]),
                                strength=canister["strength"],
                                strength_value=canister["strength_value"],
                                canister_id=str(canister["canister_id"]),
                                manufacturer=canister['manufacturer'],
                                imprint=canister['imprint'],
                                color=canister['color'],
                                shape=canister['shape'],
                                form=canister['drug_form'],
                                canister_version=canister_version,
                                drug_shape_name=canister['drug_shape_name'],
                                big_canister_stick_id=canister['big_canister_stick_id'],
                                small_canister_stick_id=canister['small_canister_stick_id'],
                                product_id=canister['product_id'],
                                big_stick_serial_number=canister_info['big_stick_serial_number'],
                                small_stick_serial_number=canister_info['small_stick_serial_number'],
                                lower_level=canister['lower_level'],
                                drum_serial_number=canister_info['drum_serial_number'],
                                company_id=canister["company_id"])
        create_blob(label_path, label_name, canister_label_dir)  # Upload label to central storage
        logger.info('Canister Label Generated. Canister ID: {}'.format(canister_id))
        response = {'label_name': label_name, 'canister_version': canister_version}
        # CanisterMaster.update(label_print_time=get_current_date_time()).where(
        #     CanisterMaster.id == canister_id).execute()
        db_update_canister_master_label_print_time(canister_id)

        logger.info("get_canister_label response {}".format(response))
        return create_response(response)
    except Exception as e:
        logger.error('Canister Label Generation Failed: ' + str(e), exc_info=True)
        return error(2006)
    finally:
        remove_files([label_path])


@log_args_and_response
def get_expired_drug_label(canister_expiry_dict, label_name):
    try:
        canister_expired_data_list = get_expired_drug_info(canister_expiry_dict)
        if canister_expired_data_list:
            if not os.path.exists(expired_drug_label_dir):
                os.makedirs(expired_drug_label_dir)
                logger.info(f'In get_expired_drug_label, {expired_drug_label_dir} dir created.')

            label_path = os.path.join(expired_drug_label_dir, label_name)

            status = generate_expired_drug_label(file_name=label_path,expired_drug_dicts=canister_expired_data_list)
            logger.info(f"In get_expired_drug_label, status of generate_expired_drug_label: {status}")

            if status:
                logger.info("In get_expired_drug_label, upload label")
                create_blob(label_path, label_name, expired_drug_label_dir)

            response = {'label_name': label_name}

            return create_response(response)
        else:
            return error(1004)

    except Exception as e:
        logger.error(f"Error in get_expired_drug_label, e: {e}")
        raise e


@validate(required_fields=["canister_id"])
def get_canister_label_v3(canister_info):
    """
    Generates canister label if not present, returns file name

    :param canister_info:
    :return: json
    """
    canister_id_list = canister_info["canister_id"]

    canister_id_list_str = [str(i) for i in canister_id_list]
    canister_id_str = ",".join(canister_id_list_str)
    label_name = "multi_canister_" + canister_id_list_str[0] + ".pdf"

    if 'regenerate' not in canister_info:  # flag to regenerate label forcefully
        # If file already exists return
        if blob_exists(label_name, canister_label_dir):
            response = {'label_name': label_name}
            return create_response(response)

    if not os.path.exists(canister_dir):
        os.makedirs(canister_dir)
    label_path = os.path.join(canister_dir, label_name)

    try:
        canister_list = CanisterMaster.b_get_by_id_list(canister_id_list)
    except (IntegrityError, InternalError):
        return error(2001)

    try:
        logger.info('Starting Canister Label Generation. Canister ID: {}'.format(canister_id_list[0]))
        generate_canister_label_v3(label_path, canister_list)
        create_blob(label_path, label_name, canister_label_dir)  # Upload label to central storage
        logger.info('Canister Label Generated. Canister ID: {}'.format(canister_id_list[0]))
        CanisterMaster.update(label_print_time=get_current_date_time()).where(CanisterMaster.id == canister_id_list[0])
        response = {'label_name': label_name, 'canister_version': "v3"}
        return create_response(response)
    except Exception as e:
        logger.error('Canister Label Generation Failed: ' + str(e), exc_info=True)
        return error(2006)
    finally:
        remove_files([label_path])


@log_args_and_response
@validate(required_fields=["system_id"])
def reset_print_job_couch_db(dict_input_args):
    """
    :param dict_input_args:
    :return:
    """
    system_id_list = dict_input_args.get('system_id')
    print_job_pending_list: list = list()
    print_job_error_list: list = list()
    try:
        for system_id in system_id_list:
            print_job_data = get_print_job_cdb_data(system_id=system_id)
            logger.info("In reset_print_job_couch_db: existing record in print jobs document: {}".format(print_job_data))

            # if total record in print job documents are more than 50 then check for printing status
            if len(print_job_data) > constants.MAX_RECORD_IN_PRINT_JOB_DOC:
                for data in reversed(print_job_data):
                    if data['printing_status'] in [settings.PRINT_STATUS['Pending'],
                                                      settings.PRINT_STATUS['In queue'],
                                                      settings.PRINT_STATUS['Printing']]:
                        print_job_pending_list.append(data)
                    elif data['printing_status'] in [settings.PRINT_STATUS['Done'],
                                                 settings.PRINT_STATUS['Cancelled'],
                                                 settings.PRINT_STATUS['Error']]:
                        print_job_error_list.append(data)

                logger.info("In reset_print_job_couch_db: Pending record in print job document: {}, "
                            "record with error printing status : {}".format(print_job_pending_list, print_job_error_list))

                # if total(printing status in[Pending,In queue, Printing]) printing data < 50 then we have to add (printing status in[Done,Cancelled, Error])
                # until total record length  = 50
                # if pending record = 40 and error record = 30 => total 50 record store ( Pending(40) + error(50-40 = 10) )
                if len(print_job_pending_list) < constants.MAX_RECORD_IN_PRINT_JOB_DOC:
                    add_error_list = print_job_error_list[0:(constants.MAX_RECORD_IN_PRINT_JOB_DOC - len(print_job_pending_list))]
                    logger.info("In reset_print_job_couch_db: add error record list in couch db doc: {}".format(add_error_list))
                    # to find deleted record from couchdb document
                    deleted_record = print_job_error_list[(constants.MAX_RECORD_IN_PRINT_JOB_DOC - len(print_job_pending_list)):]
                    logger.info("In reset_print_job_couch_db: deleted record from print job couch db document: {}".format(deleted_record))

                    updated_print_job_list = print_job_pending_list + add_error_list
                else:
                    # if total(printing status in[Pending,In queue, Printing]) printing data > 50 then we have to store all pending record in print jobs
                    updated_print_job_list = print_job_pending_list

                logger.info("In reset_print_job_couch_db: updated_print_job_list: {}".format(updated_print_job_list))
                data_updated = update_print_job_cdb_data_for_cron_job(system_id=system_id, updated_list=updated_print_job_list)
                logger.info("In reset_print_job_couch_db: print job couch db document updated: {}".format(data_updated))

        return create_response(True)


    except (InternalError, IntegrityError) as e:
        logger.error("error in reset_print_job_couch_db {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in reset_print_job_couch_db {}".format(e))
        return error(1000, "Error in reset_print_job_couch_db: " + str(e))
