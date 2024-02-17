import datetime
from typing import Dict, Any

from dateutil import parser
from peewee import InternalError, IntegrityError, DoesNotExist, DataError
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response, get_current_date_time
from dosepack.validation.validate import validate
from src.dao.alternate_drug_dao import alternate_drug_update_facility
from src.constants import MVS_MISSING_PILLS, MVS_DRUGS_OUT_OF_STOCK
from src.dao.misc_dao import get_system_setting_by_system_id
from src.dao.pack_dao import db_verify_packlist_by_company, db_max_order_no_dao, add_missing_drug_record_dao, \
    update_facility_distribution_id, get_ordered_pack_list, update_schedule_id_null_dao, db_set_pack_status_dao, \
    db_get_packs_by_batch
from src.service.pack import update_drugs_out_of_stock
from src.dao.batch_dao import db_reset_batch, get_batch_record, db_update_batch_status_from_create_batch, \
    update_batch_pack_status_create_batch, db_update_batch_status_from_create_multi_batch, \
    update_batch_pack_status_create_multi_batch, db_get_batch_id_from_system, get_system_status_dao, \
    check_batch_id_assign_for_packs
from src.dao.pack_user_map_dao import get_pack_user_details, update_or_create_pack_user_map_dao
from src.exc_thread import ExcThread
from src.exceptions import PharmacySoftwareCommunicationException, PharmacySoftwareResponseException
from src.service.drug_inventory import check_and_update_drug_req
from src.service.notifications import Notifications
from src.service.misc import get_weekdays

logger = settings.logger


@validate(required_fields=['system_id', 'user_id'])
@log_args_and_response
def create_batch(batch_info: dict) -> dict:
    """
    Creates batch for given pack ids
    - sets order of pack and resets batch info given reset flag
    :param batch_info:
    :return:
    """
    logger.debug(batch_info)
    pack_list = batch_info.get('pack_list', [])
    user_id = batch_info['user_id']
    batch_id = batch_info.get('batch_id', None)
    progress_batch_id = batch_info.get('progress_batch_id', None)
    crm = batch_info.get('crm', False)  # is crm requesting
    batch_packs = batch_info.get('batch_packs', None)
    system_allocation = batch_info.get('system_allocation', None)
    # if packs does not belong to any system and if system allocation is true
    # set system id for packs
    reset = batch_info.get('reset', None)
    status = batch_info.get('status', None)
    try:
        if batch_id and not crm:
            # validation for imported batch
            batch_record = get_batch_record(batch_id)
            pre_import_status_list = (
                settings.BATCH_PENDING,
                settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
                settings.BATCH_CANISTER_TRANSFER_DONE
            )
            # status can not be reverted to pre_import_status as already imported
            if batch_record.status.id not in pre_import_status_list and \
                    batch_record.status.id == settings.BATCH_IMPORTED:
                return error(1020, "Already Imported.")
        # To handle batch status, just update status
        if status and batch_id:
            db_update_batch_status_from_create_batch(status, [batch_id], progress_batch_id, batch_packs)
            response = {
                'batch_id': batch_id,
                'batch_status': status
            }
            return create_response(response)
        if pack_list:
            company_id = batch_info['company_id']
            valid_pack_list = db_verify_packlist_by_company(company_id=company_id, pack_list=pack_list)
            if not valid_pack_list:
                return error(1026)

        system_id = batch_info['system_id']
        _max_order_no = db_max_order_no_dao(system_id)
        pack_orders = [_max_order_no + index + 1 for index, item in enumerate(pack_list)]

        if 'batch_name' not in batch_info:
            return error(1020, 'The parameter batch_name is required.')

        with db.transaction():
            batch_name = batch_info['batch_name']
            if reset:
                db_reset_batch(batch_id, user_id)
                status = settings.BATCH_PENDING
            if pack_list:
                update_batch_pack_status_create_batch(batch_id, system_id, user_id, batch_name, batch_record, pack_list,
                                                      pack_orders)
        response = {
            'batch_id': batch_id,
            'batch_status': status
        }
        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return error(1020, "The parameter batch_id does not exist.")


@validate(required_fields=['automatic_system_pack_info', 'manual_system_pack_info'])
@log_args_and_response
def pre_create_batch(system_pack_info):
    """
    @param: pack_list >> to get facility distribution id of packs and change status in
                      facility distribution master from pending to batch distribution done
    """

    response = {}
    response1 = {}
    pack_list = []
    system_id_list = list()
    time_zone = settings.CURRENT_TIMEZONE
    company_id = system_pack_info.get('company_id', 2)

    try:
        with db.transaction():
            if len(system_pack_info["automatic_system_pack_info"]) > 0:
                response_list = []
                logger.info("automatic_system_pack_info : " + str(system_pack_info["automatic_system_pack_info"]))
                for batch_info in system_pack_info["automatic_system_pack_info"]:
                    pack_list.extend(batch_info['pack_list'])
                    if pack_list:
                        batch_id_assign_count = check_batch_id_assign_for_packs(pack_list=pack_list)
                        if batch_id_assign_count != 0:
                            return error(2009)
                    if batch_info['system_id'] not in system_id_list:
                        system_id_list.append(batch_info['system_id'])
                    response = create_multi_batch(batch_info)
                    response_list.append(response)

            if len(system_pack_info["manual_system_pack_info"]) > 0:
                logger.info("manual_system_pack_info : " + str(system_pack_info["manual_system_pack_info"]))
                for manual_pack in system_pack_info["manual_system_pack_info"]:
                    pack_list.extend(batch_info['pack_list'])
                    response1 = map_user_pack_multi_user(manual_pack)

            if "alternate_drug_info" in system_pack_info:
                logger.info("alternate_drug_info : " + str(system_pack_info["alternate_drug_info"]))
                for zone, alternate_drug_info in system_pack_info['alternate_drug_info'].items():
                    if len(alternate_drug_info) == 0:
                        continue
                    logger.info(zone)
                    logger.info(alternate_drug_info)
                    print(alternate_drug_info)
                    alternate_response = alternate_drug_update_facility(alternate_drug_info)

            if len(pack_list) > 0:
                status, resp, facility_distribution_id = update_facility_distribution_id(company_id, pack_list)
                if not status:
                    logger.error("Error in update_facility_distribution_id: " + resp)
                    return error(0, resp)
                status = update_schedule_id_null_dao(pack_list, facility_distribution_id, update=False)

            if system_id_list and response:
                # order drugs required for filling all pending packs
                try:
                    args = {"company_id": company_id,
                            "time_zone": time_zone,
                            "batch_id": str(response['batch_id']),
                             "system_id_list": system_id_list}
                    exception_list = []
                    t = ExcThread(exception_list, name="drug_req_check", target=check_and_update_drug_req,
                                  args=[args])
                    t.start()
                except Exception as e:
                    logger.error(e, exc_info=True)
                # epbm_order_request = check_and_update_drug_req({"company_id": company_id,
                #                                                 "time_zone": time_zone,
                #                                                 "batch_id": str(response['batch_id']),
                #                                                 "system_id_list": system_id_list})

        if len(system_pack_info["manual_system_pack_info"]) > 0 and len(
                system_pack_info["automatic_system_pack_info"]) > 0:
            return create_response(response, response1)
        elif len(system_pack_info["automatic_system_pack_info"]) > 0:
            return create_response(response)
        else:
            return create_response(response1)

    except (InternalError, DataError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)
    except PharmacySoftwareCommunicationException as e:
        logger.error(e, exc_info=True)
        return error(7001, e)
    except PharmacySoftwareResponseException as e:
        logger.error(e, exc_info=True)
        return error(7001, e)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(0, e)


def map_user_pack_multi_user(userpacks):
    try:
        with db.transaction():
            # for item in userpacks:
            # print([int(item) for item in str(item["pack_list"]).split(',')])
            db_set_pack_status_dao(userpacks)
            pack_list = userpacks["pack_list"]
            assigned_to = userpacks['assigned_to']
            user_id = userpacks['user_id']
            pack_details = list()
            # update pack_user_map and send notification
            user_pack_mapping_list = [{"pack_id_list": pack_list, "assigned_to": assigned_to, "user_id": user_id}]
            pack_assign_status = map_user_pack(user_pack_mapping_list)
            response = {
                'manual_status': "success"
            }
            return response
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def create_multi_batch(batch_info):
    """
        Creates batch for given pack ids
        - sets order of pack and resets batch info given reset flag
        :param batch_info:
        :return:
        """
    logger.debug(batch_info)
    pack_list = batch_info.get('pack_list', [])
    user_id = batch_info['user_id']
    scheduled_start_time = batch_info['scheduled_start_time']
    estimated_processing_time = batch_info['estimated_processing_time']
    batch_id = batch_info.get('batch_id', None)
    crm = batch_info.get('crm', False)  # is crm requesting
    system_allocation = batch_info.get('system_allocation', None)
    # if packs does not belong to any system and if system allocation is true
    # set system id for packs
    reset = batch_info.get('reset', None)
    status = batch_info.get('status', None)
    try:
        if batch_id and not crm:
            # validation for imported batch
            batch_record = get_batch_record(batch_id)
            pre_import_status_list = (
                settings.BATCH_PENDING,
                settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
                settings.BATCH_CANISTER_TRANSFER_DONE
            )
            # status can not be reverted to pre_import_status as already imported
            if batch_record.status.id not in pre_import_status_list and \
                    batch_record.status.id == settings.BATCH_IMPORTED:
                return error(1020, "Already Imported.")
        # To handle batch status, just update status
        if status and batch_id:
            db_update_batch_status_from_create_multi_batch(status, batch_id)
            response = {
                'batch_id': batch_id,
                'batch_status': status
            }
            return create_response(response)
        if pack_list:
            company_id = batch_info['company_id']
            valid_pack_list = db_verify_packlist_by_company(company_id=company_id, pack_list=pack_list)
            if not valid_pack_list:
                return error(1026)

        system_id = batch_info['system_id']
        _max_order_no = db_max_order_no_dao(system_id)
        pack_list = get_ordered_pack_list(pack_list)
        pack_orders = [_max_order_no + index + 1 for index, item in enumerate(pack_list)]

        if 'batch_name' not in batch_info:
            return error(1020, 'The parameter batch_name is required.')

        batch_name = batch_info['batch_name']
        if reset:
            db_reset_batch(batch_id, user_id)
            status = settings.BATCH_PENDING
        if pack_list:
            if not batch_id:
                status = settings.BATCH_PENDING
            else:
                status = batch_record.status.id
            status, batch_id = update_batch_pack_status_create_multi_batch(batch_id, system_id, user_id, batch_name,
                                                                           status,
                                                                           pack_list, pack_orders, scheduled_start_time,
                                                                           estimated_processing_time)

        response = {
            'batch_id': batch_id,
            'batch_status': status
        }
        return response
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


def map_user_pack(userpacks):
    user_id = None
    call_from_client = None
    missing_drug_list_dict: Dict[str, Any] = dict()
    status_update: int = 0

    try:
        pack_details = list()
        with db.transaction():
            for item in userpacks:
                if "user_id" in item and "call_from_client" in item:
                    user_id = item["user_id"]
                    call_from_client = item["call_from_client"]
                if isinstance(item["pack_id_list"], list):
                    pack_list = [int(item) for item in item["pack_id_list"]]
                if isinstance(item["pack_id_list"], str):
                    pack_list = [int(item) for item in str(item["pack_id_list"]).split(',')]
                if isinstance(item["pack_id_list"], int):
                    pack_list = [item["pack_id_list"]]

                # Prepare the dictionary to update the Missing Drug status for respective Packs
                if "reason_action" in item:
                    missing_drug_list_dict = {"pack_ids": pack_list, "created_date": get_current_date_time(),
                                              "created_by": item['user_id'], "reason_action": item["reason_action"]}

                    if item["reason_action"] == MVS_MISSING_PILLS:
                        missing_drug_list_dict.update({"rx_no_list": item["reason_rx_no_list"]})

                    if item["reason_action"] == MVS_DRUGS_OUT_OF_STOCK:
                        missing_drug_list_dict.update({"drug_list": item["drug_list"]})

                assigned_to = item['assigned_to']
                modified_by = created_by = item['user_id']
                for item in pack_list:
                    update_dict = {
                        'created_by': created_by,
                        'assigned_to': assigned_to,
                        'created_date': get_current_date_time(),
                        'modified_by': modified_by,
                        'modified_date': get_current_date_time()
                    }
                    create_dict = {
                        'pack_id': item
                    }
                    pack_user = get_pack_user_details(pack_list)
                    for row in pack_user:
                        if row["id"] == item:
                            pack_details.append(
                                {'pack_id': item, "assigned_to": assigned_to, "assigned_from": row["assigned_from"]})
                    update_or_create_pack_user_map_dao(create_dict, update_dict)

                # Trigger the appropriate method based on MVS reason of Drugs Out of Stock or Missing Pills
                if missing_drug_list_dict:
                    if missing_drug_list_dict["reason_action"] == MVS_MISSING_PILLS:
                        status_update, drug_list = add_missing_drug_record_dao([missing_drug_list_dict])

                    if missing_drug_list_dict["reason_action"] == MVS_DRUGS_OUT_OF_STOCK:
                        status_update = update_drugs_out_of_stock([missing_drug_list_dict], user_id=created_by)

                    if status_update == 0:
                        return False

        # Notifications(call_from_client=call_from_client).check_and_send_assign_message(pack_details)

        return True
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_packs_by_batch_ids(dict_info):
    system_id = dict_info['system_id']
    filter_fields = dict_info.get('filters', None)
    sort_fields = dict_info.get('sort_fields', None)
    paginate = dict_info.get('paginate', None)
    response = dict()
    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, 'Missing key(s) in paginate.')
    batch_ids = db_get_batch_id_from_system(system_id)

    try:
        if len(batch_ids):
            response = db_get_packs_by_batch(batch_ids, filter_fields, sort_fields, paginate)
            if response is None:
                return error(1004)

            # recalculate processing time of batch in case if packs are deleted or moved to manual
            response = get_estimated_processing_time_of_batch(batch_info=response,
                                                              system_id=system_id)

            logger.info("Response of get_packs_by_batch_ids {}".format(response))

        return create_response(response)

    except InternalError:
        return error(2001)


def get_estimated_processing_time_of_batch(batch_info: dict, system_id: int):
    """
    Function to calculate processing time of batch
    @param system_id:
    @param batch_info:
    @return:
    """
    logger.debug("In get_estimated_processing_time_of_batch")
    batch_processing_time_dict = dict()
    try:
        for batch, pack_details in batch_info.items():
            # initialize required variables
            processing_hours = 0
            last_batch_packs_count = len(pack_details)
            last_batch_start_date = pack_details[0]["scheduled_start_time"]
            system_timings = get_system_setting_by_system_id(system_id=system_id)
            AUTOMATIC_PER_DAY_HOURS = int(system_timings['AUTOMATIC_PER_DAY_HOURS'])
            AUTOMATIC_PER_HOUR = int(system_timings['AUTOMATIC_PER_HOUR'])
            AUTOMATIC_SATURDAY_HOURS = int(system_timings['AUTOMATIC_SATURDAY_HOURS'])
            AUTOMATIC_SUNDAY_HOURS = int(system_timings['AUTOMATIC_SUNDAY_HOURS'])

            while last_batch_packs_count > 0:
                last_batch_start_date = parser.parse(str(last_batch_start_date)).date()
                last_batch_start_date_str = str(last_batch_start_date)
                batch_date_day = get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                              int(last_batch_start_date_str.split('-')[1]),
                                              int(last_batch_start_date_str.split('-')[2]))
                if batch_date_day == settings.SATURDAY:
                    if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                        last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS
                        last_batch_start_date += datetime.timedelta(days=1)
                        processing_hours += AUTOMATIC_SATURDAY_HOURS
                        if last_batch_packs_count == 0:
                            batch_processing_time_dict[batch] = processing_hours
                    elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                        processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                        last_batch_packs_count = 0
                        batch_processing_time_dict[batch] = processing_hours
                elif batch_date_day == settings.SUNDAY:
                    if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                        last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS
                        last_batch_start_date += datetime.timedelta(days=1)
                        processing_hours += AUTOMATIC_SUNDAY_HOURS
                        if last_batch_packs_count == 0:
                            batch_processing_time_dict[batch] = processing_hours
                    elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                        processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                        last_batch_packs_count = 0
                        batch_processing_time_dict[batch] = processing_hours
                else:
                    if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                        last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS
                        last_batch_start_date += datetime.timedelta(days=1)
                        processing_hours += AUTOMATIC_PER_DAY_HOURS
                        if last_batch_packs_count == 0:
                            batch_processing_time_dict[batch] = processing_hours
                    elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                        processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                        last_batch_packs_count = 0
                        batch_processing_time_dict[batch] = processing_hours
            pack_details[0]["estimated_processing_time"] = round(batch_processing_time_dict[batch], 2)

        logger.info("batch_processing_time_dict {}".format(batch_processing_time_dict))
        return batch_info

    except Exception as e:
        logger.error(e)
        return None


@log_args_and_response
def get_system_status(system_id_list):
    """
    Returns status for system if pack batch is allocated to system

    :param system_id_list: list
    :return: str
    """
    system_idle = dict()
    if not system_id_list:
        return create_response(system_idle)
    non_idle_status_list = [
        settings.BATCH_PROCESSING_COMPLETE,
        settings.BATCH_IMPORTED
    ]
    try:
        for item in system_id_list:
            system_idle[item] = True
        data = get_system_status_dao(system_id_list, non_idle_status_list)
        # set system status not idle if batch is pending
        for record in data:
            system_idle[str(record['system_id'])] = False

        return create_response(system_idle)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)