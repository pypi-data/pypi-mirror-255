# -*- coding: utf-8 -*-
"""
    src.pack
    ~~~~~~~~~~~~~~~~

    This is the core pack module and has set of core functions defined which maps
    to the pack related web services. The core functionality includes getting pack
    information, getting and setting pack status , updating inventory after pack
    is processed and getting the label printing information for the packs.

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""

import functools
import json
import operator

from peewee import fn, DataError, InternalError, IntegrityError, DoesNotExist, JOIN_LEFT_OUTER, SQL, Clause

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import get_current_date_time, \
    log_args_and_response, \
    log_args
from dosepack.validation.validate import validate
# from label_printing.pack_stencil_label import generate_stencil_label
from src.dao.alternate_drug_dao import alternate_drug_update_facility
from src.api_utility import  get_results
from src.dao.pack_dao import max_order_no, get_ordered_pack_list, get_sharing_packs
from src.dao.batch_dao import  db_reset_batch
from src.dao.reserve_canister_dao import db_update_available_canister, db_delete_reserved_canister
from src.service.drug_search import get_ndc_list_for_barcode
from src.dao.pack_dao import db_slot_details
from src.exceptions import PharmacySoftwareResponseException, PharmacySoftwareCommunicationException
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_user_map import PackUserMap
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_unique_drug import UniqueDrug
from src.service.batch import map_user_pack
from src.service.misc import update_replenish_queue_count
from src.service.pack import map_user_pack

logger = settings.logger


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
    company_id = system_pack_info.get('company_id', 2)

    try:
        with db.transaction():
            if len(system_pack_info["automatic_system_pack_info"]) > 0:
                response_list = []
                logger.info("automatic_system_pack_info : " + str(system_pack_info["automatic_system_pack_info"]))
                for batch_info in system_pack_info["automatic_system_pack_info"]:
                    pack_list.extend(batch_info['pack_list'])
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
                    logger.warning("Error in update_facility_distribution_id: " + resp)
                    return error(0, resp)
                status = PackDetails.update_schedule_id_null(pack_list, facility_distribution_id, update=True)

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
            PackDetails.db_set_pack_status(userpacks)
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
            batch_record = BatchMaster.get(id=batch_id)
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
            if int(status) == settings.BATCH_IMPORTED:
                # If batch is imported, update reserved canister
                db_update_available_canister(batch_id)
            if int(status) == settings.BATCH_PROCESSING_COMPLETE:
               db_delete_reserved_canister(batch_id=batch_id)
            BatchMaster.update(status=status) \
                .where(BatchMaster.id == batch_id).execute()
            response = {
                'batch_id': batch_id,
                'batch_status': status
            }
            return create_response(response)
        if pack_list:
            company_id = batch_info['company_id']
            valid_pack_list = PackDetails.db_verify_packlist(pack_list, company_id)
            if not valid_pack_list:
                return error(1026)

        system_id = batch_info['system_id']
        _max_order_no = max_order_no(system_id)
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
                record = BaseModel.db_create_record({
                    'name': batch_name,
                    'system_id': system_id,
                    'status': status,
                    'created_by': user_id,
                    'modified_by': user_id,
                    'estimated_processing_time': estimated_processing_time,
                    'scheduled_start_time': scheduled_start_time
                }, BatchMaster, get_or_create=False)
                batch_id = record.id
            else:  # update batch data
                status = batch_record.status.id
                update_dict = {
                    'name': batch_name,
                    'system_id': system_id,
                    'modified_date': get_current_date_time(),
                    'modified_by': user_id
                }
                BatchMaster.update(**update_dict) \
                    .where(BatchMaster.id == batch_id).execute()
            # if pack list provided, update pack order
            update_pack_dict = {
                'batch_id': batch_id,
                'modified_date': get_current_date_time(),
                'modified_by': user_id,
                'system_id': system_id
            }
            logger.info("packdetails update info : " + str(update_pack_dict))
            PackDetails.update(**update_pack_dict) \
                .where(PackDetails.id << pack_list).execute()
            PackDetails.db_update_pack_order_no({
                'pack_ids': ','.join(list(map(str, pack_list))),
                'order_nos': ','.join(list(map(str, pack_orders))),
                'system_id': system_id
            })

        response = {
            'batch_id': batch_id,
            'batch_status': status
        }
        return response
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except (DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


def update_facility_distribution_id(company_id, pack_list):
    """
    Function to get list of facility distribution id's from the given pack list
    and update status of respective id in db
    """
    if len(pack_list) > 0:
        try:
            facility_ids = PackDetails.db_get_facility_distribution_ids(pack_list)
            if len(facility_ids) > 1:
                return False, "update_facility_distribution_id: Multiple facility ids found", None
            response = FacilityDistributionMaster.db_update_facility_distribution_status(company_id, list(facility_ids))
            return True, response, facility_ids.pop()
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            return False, str(e), None


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
    crm = batch_info.get('crm', False)  # is crm requesting
    system_allocation = batch_info.get('system_allocation', None)
    # if packs does not belong to any system and if system allocation is true
    # set system id for packs
    reset = batch_info.get('reset', None)
    status = batch_info.get('status', None)
    try:
        if batch_id and not crm:
            # validation for imported batch
            batch_record = BatchMaster.get(id=batch_id)
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
            with db.transaction():
                if int(status) == settings.BATCH_IMPORTED:
                    # If batch is imported, update reserved canister
                    db_update_available_canister(batch_id)
                    BatchMaster.update(imported_date=get_current_date_time()) \
                        .where(BatchMaster.id == batch_id).execute()
                if int(status) == settings.BATCH_PROCESSING_COMPLETE:
                    # truncating GuidedTracker Table in batch completion
                    # todo-uncomment below when we change structure of guided_transfer_cycle_history
                    # guided_tracker_changes = delete_from_guided_tracker(batch_id=batch_id)
                    # if guided_tracker_changes:
                    #     print("Guided Tracker table cleared for batch :{}".format(batch_id))
                    db_delete_reserved_canister(batch_id=batch_id)
                    pending_packs = PackDetails.select(PackDetails.id).dicts() \
                        .where(PackDetails.batch_id == batch_id,
                               PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS])
                    pending_pack_ids = [pack['id'] for pack in pending_packs]
                    if pending_pack_ids:
                        logger.info("Marking packs as done at batch end for packs having "
                                    "pending_progress_status: {}".format(pending_pack_ids))
                        update_status = PackDetails.update(pack_status=settings.DONE_PACK_STATUS,
                                                           modified_date=get_current_date_time()) \
                            .where(PackDetails.id << pending_pack_ids).execute()
                BatchMaster.update(status=status) \
                    .where(BatchMaster.id == batch_id).execute()
            response = {
                'batch_id': batch_id,
                'batch_status': status
            }
            return create_response(response)
        if pack_list:
            company_id = batch_info['company_id']
            valid_pack_list = PackDetails.db_verify_packlist(pack_list, company_id)
            if not valid_pack_list:
                return error(1026)

        system_id = batch_info['system_id']
        _max_order_no = max_order_no(system_id)
        pack_orders = [_max_order_no + index + 1 for index, item in enumerate(pack_list)]

        if 'batch_name' not in batch_info:
            return error(1020, 'The parameter batch_name is required.')

        with db.transaction():
            batch_name = batch_info['batch_name']
            if reset:
                db_reset_batch(batch_id, user_id)
                status = settings.BATCH_PENDING
            if pack_list:
                if not batch_id:
                    status = settings.BATCH_PENDING
                    record = BaseModel.db_create_record({
                        'name': batch_name,
                        'system_id': system_id,
                        'status': status,
                        'created_by': user_id,
                        'modified_by': user_id,
                    }, BatchMaster, get_or_create=False)
                    batch_id = record.id
                else:  # update batch data
                    status = batch_record.status.id
                    update_dict = {
                        'name': batch_name,
                        'system_id': system_id,
                        'modified_date': get_current_date_time(),
                        'modified_by': user_id
                    }
                    BatchMaster.update(**update_dict) \
                        .where(BatchMaster.id == batch_id).execute()
                # if pack list provided, update pack order
                PackDetails.db_update_pack_order_no({
                    'pack_ids': ','.join(list(map(str, pack_list))),
                    'order_nos': ','.join(list(map(str, pack_orders))),
                    'system_id': system_id
                })
                update_pack_dict = {
                    'batch_id': batch_id,
                    'modified_date': get_current_date_time(),
                    'modified_by': user_id,
                    'system_id': system_id
                }
                PackDetails.update(**update_pack_dict) \
                    .where(PackDetails.id << pack_list).execute()
        response = {
            'batch_id': batch_id,
            'batch_status': status
        }
        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except (DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return error(1020, "The parameter batch_id does not exist.")


@validate(required_fields=['company_id', 'user_id'])
def add_batch_distribution(batch_info):
    """
    Adds batch id i.e schedule id in pack details for given pack ids
    - creates data in batch formation
    :param batch_info:
    :return:
    """
    logger.debug(batch_info)
    pack_list = batch_info.get('pack_list', [])
    user_id = batch_info['user_id']
    status = batch_info['status_id']
    company_id = batch_info['company_id']
    facility_dis_id = batch_info.get('facility_distribution_id', None)
    response = {}
    try:
        if status != "Pending":
            return error(1020, "Batch already in process.")
        else:
            with db.transaction():
                status_id = settings.FACILITY_DISTRIBUTION_PENDING_STATUS

                valid_pack_list = PackDetails.db_verify_packlist(pack_list, company_id)
                if not valid_pack_list:
                    return error(1026)

                if facility_dis_id is None:
                    facility_dis_id = FacilityDistributionMaster.db_update_or_create_bdm(user_id, status_id, company_id)
                    print(facility_dis_id)
                    response['status'] = PackDetails.update_schedule_id(pack_list, facility_dis_id)
                    response['facility_dis_id'] = facility_dis_id

                else:
                    response['status'] = PackDetails.update_schedule_id_null(pack_list, facility_dis_id)
                    response['facility_dis_id'] = None

                return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return error(2001)


@validate(required_fields=["date_from", "date_to", "company_id"],
          validate_dates=['date_from', 'date_to'], validate_robot_id='device_id')
def get_packs(search_filters):
    """ Take the search filters which includes the date_from, to_date and retrieves all the
        packs which satisfies the search criteria.

        Args:
            search_filters (dict): The keys in it are from_date(Date), to_date(Date),
                                   pack_status(str), system_id(int)

        Returns
           list: List of all the packs which falls in the search criteria.

        Examples:
            >>> get_packs({"from_date": '01-01=01', "to_date": '01-12-16', \
                            "pack_status": '1', 'system_id': 2})
                []
    """

    date_from, date_to = convert_date_to_sql_date(search_filters['date_from'], search_filters['date_to'])
    company_id = search_filters["company_id"]
    system_id = search_filters.get("system_id", None)
    all_flag = search_filters.get('all_flag', False)
    schedule_start_date = search_filters.get('schedule_start_date', None)
    schedule_end_date = search_filters.get('schedule_end_date', None)
    status = [int(item) for item in str(search_filters["pack_status"]).split(',')]
    # status.append(settings.PROGRESS_PACK_STATUS)
    schedule_data = {}
    filter_fields = search_filters.get('filter_fields', None)
    try:
        results = PackDetails.db_get_packs(
            date_from, date_to, status, filter_fields, company_id,
            system_id=system_id,
            all_flag=all_flag,
        )
        facility_filter_fields = {}
        schedule_ids = results['schedule_ids']
        patient_schedule_ids = results['patient_schedule_ids']
        packs = results['packs']
        batches = results['batches']
        schedule_facility_ids = results['schedule_facility_ids']
        facility_ids = [(sfi.split(':')[1]) for sfi in schedule_facility_ids]
        facility_filter_fields['facility_ids'] = facility_ids
        if schedule_start_date and schedule_end_date and packs:
            # if schedule date is sent then provide scheduling data, otherwise empty data
            df = pd.DataFrame(packs)
            df['delivery_datetime'].replace(to_replace=[None], value="", inplace=True)
            # # df.fillna(None)
            # print(df['delivery_datetime'])
            df['scheduled_delivery_date'].replace(to_replace=[None], value="", inplace=True)
            # print(df['scheduled_delivery_date'])
            # ips_delivery_dict = df.groupby(["facility_id"]).agg({'delivery_datetime':'max'}).to_dict()["delivery_datetime"]
            scheduled_delivery_dict = df.groupby(["facility_id"]).agg({'scheduled_delivery_date': nanmin}).to_dict()[
                "scheduled_delivery_date"]
            scheduled_delivery_dict = results['facility_min_delivery_date']
            print(scheduled_delivery_dict)

            schedule_data = get_next_schedules(company_id, active=True,
                                               filter_fields=facility_filter_fields,
                                               schedule_facility_ids=schedule_facility_ids,
                                               scheduled_delivery_dict=scheduled_delivery_dict,
                                               patient_schedule_ids=patient_schedule_ids)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    response = {
        'pack_list': packs,
        'schedule_list': schedule_data,
        'schedule_ids': schedule_ids,
        'batch_ids': batches,
        'schedule_facility_ids': schedule_facility_ids,
    }

    return create_response(response)


@log_args
@validate(required_fields=["date_from", "date_to", "company_id", "facility_id"],
          validate_dates=['date_from', 'date_to'])
def get_packs_of_facility(search_filters):
    """ Take the search filters which includes the date_from, to_date and retrieves all the
        packs which satisfies the search criteria.

        Args:
            search_filters (dict): The keys in it are date_from(Date), date_to(Date),
                                   pack_status(str), system_id(int), company_id(int), facility_id(int)

        Returns
           list: List of all the packs which falls in the search criteria.

        Examples:
            >>> get_packs_of_facility({"from_date": '01-01=01', "to_date": '01-12-16', \
                            "pack_status": '1', 'system_id': 2})
                []
    """

    date_from, date_to = convert_date_to_sql_date(search_filters['date_from'], search_filters['date_to'])
    company_id = search_filters["company_id"]
    system_id = search_filters.get("system_id", None)
    all_flag = search_filters.get('all_flag', False)
    facility_id = search_filters["facility_id"]
    status = [int(item) for item in str(search_filters["pack_status"]).split(',')]
    filter_fields = search_filters.get('filter_fields', None)
    try:
        response = PackDetails.db_get_packs_by_facility_id(
            date_from, date_to, status, facility_id, filter_fields, company_id,
            system_id=system_id,
            all_flag=all_flag,
        )
        logger.debug("Packs data retrieved")
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    return create_response(response)


@log_args
@validate(required_fields=["date_from", "date_to", "company_id"],
          validate_dates=['date_from', 'date_to'])
def get_facility_data_of_pending_packs(search_filters):
    """ Take the search filters which includes the date_from, to_date and retrieves all the
        facilities which satisfies the search criteria.

        Args:
            search_filters (dict): The keys in it are date_from(Date), date_to(Date),
                                   pack_status(str), system_id(int), company_id(int)

        Returns
           list: List of all the facilities which falls in the search criteria.

        Examples:
            >>> get_facility_data_of_pending_packs({"from_date": '01-01=01', "to_date": '01-12-16', \
                            "pack_status": '1', 'system_id': 2})
    """
    logger.debug("args for get_facility_data_of_pending_packs: " + str(search_filters))
    date_from, date_to = convert_date_to_sql_date(search_filters['date_from'], search_filters['date_to'])
    company_id = search_filters["company_id"]
    system_id = search_filters.get("system_id", None)
    all_flag = search_filters.get('all_flag', False)
    status = [int(item) for item in str(search_filters["pack_status"]).split(',')]
    filter_fields = search_filters.get('filter_fields', None)
    try:
        facility_list, facility_ids = PackDetails.db_get_facility_data_v3(
            date_from, date_to, status, filter_fields, company_id,
            system_id=system_id,
            all_flag=all_flag,
        )
        logger.debug("Pending packs Facility data retrieved")
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    response = {"facility_list": facility_list,
                "facility_ids": facility_ids}
    return create_response(response)


@validate(required_fields=["date_from", "date_to", "system_id"],
          validate_dates=['date_from', 'date_to'])
def get_incomplete_packs(search_filters):
    """ Take the search filters which includes the date_from, to_date ,
        system_id and retrieves all the
        packs which satisfies the search criteria.

        Args:
            search_filters (dict): The keys in it are from_date(Date), to_date(Date), system_id(int)

        Returns:
           list: List of all the packs which falls in the search criteria.

        Examples:
            >>> get_packs({"from_date": '01-01=01', "to_date": '01-12-16', "system_id": 2})
                []
    """

    date_from, date_to = convert_date_to_sql_date(search_filters['date_from'], search_filters['date_to'])
    system_id = search_filters["system_id"]
    status = settings.PROGRESS_PACK_STATUS
    try:
        response = PackDetails.db_get_incomplete_packs(date_from, date_to, status, system_id)
    except InternalError:
        return error(2001)

    return create_response(response)


@validate(required_fields=["pack_id", "device_id", "company_id"])
def get_pack_details(dict_pack_info):
    """ Returns the pack details for the given pack id.

        Args:
            dict_pack_info (dict): The keys in it are pack_id(int), system_id(int)

        Returns:
           dict: pack information for the given pack id.

        Examples:
            >>> get_pack_details({"pack_id": 3, "system_id": 2})
                []
    """

    pack_id = dict_pack_info["pack_id"]
    device_id = dict_pack_info["device_id"]
    company_id = dict_pack_info["company_id"]
    non_fractional = dict_pack_info.get("non_fractional", False)
    mft_slots = dict_pack_info.get("mft_slots", False)
    print_status = dict_pack_info.get("print_status", False)

    valid_pack = PackDetails.db_verify_pack_id(pack_id, company_id)
    if not valid_pack:
        return error(1026)

    if "device_id" in dict_pack_info and dict_pack_info["device_id"] and company_id:
        device_id = dict_pack_info["device_id"]
        valid_device = DeviceMaster.db_verify_device_id_by_company(device_id, company_id)
        if not valid_device:
            return error(1033)

    try:
        response = get_pack_details_dao(
            pack_id, device_id, company_id=company_id,
            non_fractional=non_fractional
        )
        if print_status:
            response['print_requested'] = PrintQueue.is_print_requested(pack_id)
        return create_response(response)
    except (InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        return error(0, e)


@validate(required_fields=["pack_id", "device_id", "company_id"])
def get_pack_details_v2(dict_pack_info):
    """ Returns the pack details for the given pack id.

        Args:
            dict_pack_info (dict): The keys in it are pack_id(int), system_id(int)

        Returns:
           dict: pack information for the given pack id.

        Examples:
            >>> get_pack_details({"pack_id": 3, "system_id": 2})
                []
    """

    pack_id = dict_pack_info["pack_id"]
    device_id = dict_pack_info["device_id"]
    company_id = dict_pack_info["company_id"]
    non_fractional = dict_pack_info.get("non_fractional", False)
    mft_slots = dict_pack_info.get("mft_slots", False)
    print_status = dict_pack_info.get("print_status", False)
    exclude_pack_ids = dict_pack_info.get("exclude_pack_ids", None)
    # todo: remove after testing of the build
    # logger.debug('type of exclude_pack_ids: {}'.format(type(exclude_pack_ids)))

    valid_pack = PackDetails.db_verify_pack_id(pack_id, company_id)
    if not valid_pack:
        return error(1026)

    if "device_id" in dict_pack_info and dict_pack_info["device_id"] and company_id:
        device_id = dict_pack_info["device_id"]
        valid_device = DeviceMaster.db_verify_device_id_by_company(device_id, company_id)
        if not valid_device:
            return error(1033)

    try:
        response = PackDetails.db_get_pack_details_v2(
            pack_id, device_id, company_id=company_id,
            non_fractional=non_fractional, exclude_pack_ids=exclude_pack_ids
        )
        if mft_slots and device_id:
            response['mfd_slot_data'] = dict()

            trolley_data = get_mfd_trolley_for_pack(pack_id)
            logger.debug('Trolley_data_for_pack_id: {} is {}'.format(pack_id, trolley_data))
            mfd_analysis_ids = []
            if trolley_data:
                mfd_analysis_ids, mfs_system_mapping, dest_devices, batch_system = get_trolley_analysis_ids_by_trolley_seq(
                    trolley_data['batch_id'], trolley_data['trolley_seq'])
            logger.debug('mfd_analysis_ids_for_pack_id: {} are: {}'.format(pack_id, mfd_analysis_ids))
            if mfd_analysis_ids:
                filling_done_status, transfer_done_status, trolley_data = check_transfer_filling_pending(
                    mfd_analysis_ids=mfd_analysis_ids, device_id=device_id)

                logger.debug('mfd_received_status: pack_id: {}, filling_done_status: {} and transfer_done: {}'.format(
                    pack_id, filling_done_status, transfer_done_status))
                if not filling_done_status or not transfer_done_status:
                    pack_status = 2  # transfer pending
                    if not filling_done_status:
                        pack_status = 1  # filling pending
                    filling_transfer_pending = {
                        'mfd_filling_status': pack_status,
                        'cart_data': trolley_data
                    }
                    return create_response(filling_transfer_pending)
                mfd_response = db_get_mfd_slot_info(pack_id, device_id, company_id, response['drop_data'],
                                                    response['missing_canisters'])
                response['mfd_slot_data'] = mfd_response['mfd_slot_data']
                response['drop_data'] = mfd_response['mfd_dop_data']
                response['missing_canisters'] = mfd_response['missing_canisters']

        if print_status:
            response['print_requested'] = PrintQueue.is_print_requested(pack_id)
        return create_response(response)
    except InternalError:
        return error(2001)


# @validate(required_fields=["pack_id", "robot_id", "system_id"])
# def get_pack_details_v2(dict_pack_info):
#     """
#     Returns the pack details for the given pack id.
#
#         Args:
#             dict_pack_info (dict): The keys in it are pack_id(int), system_id(int)
#
#         Returns:
#             dict: pack information for the given pack id.
#
#         Examples:
#             >>> get_pack_details({"pack_id": 3, "system_id": 2, "robot_id": None})
#                 []
#     """
#
#     pack_id = dict_pack_info["pack_id"]
#     robot_id = dict_pack_info["robot_id"]
#     system_id = dict_pack_info["system_id"]
#     non_fractional = dict_pack_info.get("non_fractional", False)
#
#     valid_pack = PackDetails.db_verify_pack_id_by_system_id(pack_id, system_id)
#     if not valid_pack:
#         return error(1014)
#
#     if robot_id and system_id:
#         valid_robot = RobotMaster.db_verify_robot_id(robot_id, system_id)
#         if not valid_robot:
#             return error(1015)
#
#     try:
#         response = PackDetails.db_get_pack_details_v2(
#             pack_id, robot_id,
#             system_id, non_fractional=non_fractional
#         )
#         return create_response(response)
#     except (InternalError, IntegrityError):
#         return error(2001)


@log_args_and_response
@validate(required_fields=["pack_id", "status", "user_id"])
def set_status(dict_pack_info):
    """ Take the pack id, system id and sets the status of the given pack according to the given pack id.

        Args:
            dict_pack_info (dict): The keys in it are pack_id(int), status(int), company_id(int)

        Returns:
           Boolean: If status update is successful or unsuccessful

        Examples:
            >>> set_status({"pack_id":1, "status": 2, "company_id": 2, "user_id": 1})
            True
    """
    logger.debug('SetStatus: ' + str(dict_pack_info))
    if "call_from_client" in dict_pack_info and "call_from_client" is not None:
        call_from_client = True
    else:
        call_from_client = False
    pack_id = dict_pack_info["pack_id"]
    if isinstance(pack_id, list):
        pack_ids = list()
        for indi_pack in pack_id:
            pack_ids.append(int(indi_pack))
    if isinstance(pack_id, str):
        pack_ids = list(map(lambda x: int(x), pack_id.split(',')))  # use if multiple packs are needed
    if isinstance(pack_id, int):
        pack_ids = [int(pack_id)]
    print(pack_ids)
    status = dict_pack_info["status"]
    company_id = dict_pack_info.get("company_id", None)
    system_id = dict_pack_info.get("system_id", None)
    use_company_id = dict_pack_info.get("use_company_id",
                                        False)  # flag to set system_id. To allocate system while making pack manual
    user_id = dict_pack_info["user_id"]
    reason = dict_pack_info.get("reason", None)
    filled_at = dict_pack_info.get("filled_at", None)
    ips_username = dict_pack_info.get('ips_username', None)
    # fill_time = None
    # if status in settings.FILLED_PACK_STATUS:
    fill_time = dict_pack_info.get('fill_time', None)
    assigned_to = dict_pack_info.get('assigned_to', None)
    transfer_to_manual_fill_system = dict_pack_info.get('transfer_to_manual_fill_system', None)
    user_confirmation = dict_pack_info.get('user_confirmation', True)
    status_changed_from_ips = dict_pack_info.get("status_changed_from_ips", False)
    forced_pack_manual = dict_pack_info.get('forced_pack_manual', False)
    affected_mfd_analysis_details_ids = list()
    pack_details = list()
    reason_dict = dict()
    update_ips = bool(False)
    delete_affected_mfd_pack_display_ids = list()
    pack_display_ids: List[str] = list()
    delete_reason_list: List[str] = list()
    changerx_flow: bool = dict_pack_info.get('changerx_flow', False)
    change_rx: bool = dict_pack_info.get('change_rx', False)

    # We are capturing the following values while user marks any pack as Filled Manually from MVS
    # Reason: Missing Pills OR Drugs Out of Stock
    reason_action: int = dict_pack_info.get("reason_action", MVS_OTHER)
    reason_rx_no_list: List[str] = dict_pack_info.get("reason_rx_no_list", None)
    drug_list: List[int] = dict_pack_info.get("drug_list", None)
    missing_drug_mapping_dict: Dict[str, Any] = dict()
    pack_and_display_ids: Dict[int, int] = dict()

    try:
        status = settings.PACK_STATUS[status]
    except KeyError:
        pass
    try:
        status = int(status)
    except ValueError:
        return error(1020, "Invalid status.")
    if use_company_id and not company_id:
        return error(1020, "The parameter company_id is required when use_company_id is true.")
    if not company_id and not system_id:
        return error(1001, "Missing Parameter(s): company_id or system_id.")

    if company_id:
        valid_packlist = PackDetails.db_verify_packlist(pack_ids, company_id)
        if not valid_packlist:
            return error(1026)
    if system_id and not use_company_id:
        valid_packlist = PackDetails.db_verify_packlist_by_system_id(pack_ids, system_id)
        if not valid_packlist:
            return error(1014)
    if status == settings.DELETED_PACK_STATUS:
        if not reason or reason == "" or None:
            return error(1001, "Missing Parameter(s): reason for deleted pack")
    try:
        with db.transaction():
            # check if current status of the pack is deleted then add record in pack history
            # if status is done else return error
            logger.debug("set_status: call to mark packs- {} as {}".format(pack_ids, status))
            deleted_pack_ids, deleted_pack_display_ids = get_deleted_packs(pack_ids=pack_ids, company_id=company_id)

            # if deleted packs found then remove this deleted packs from pack_ids
            if deleted_pack_ids:
                logger.debug("set_status: deleted packs found-{}".format(deleted_pack_ids))
                pack_ids = list(set(pack_ids).difference(set(deleted_pack_ids)))
                logger.debug("set_status: pack_ids-{} after removing deleted packs".format(pack_ids))

                if status == settings.DONE_PACK_STATUS:
                    # update pack history table
                    pack_status_list = []
                    for pack_id in deleted_pack_ids:
                        pack_status_history_dict1 = {"pack_id": pack_id,
                                                     "old_status": settings.DELETED_PACK_STATUS,
                                                     "new_status": status}
                        pack_status_history_dict2 = {"pack_id": pack_id,
                                                     "old_status": status,
                                                     "new_status": settings.DELETED_PACK_STATUS}
                        pack_status_list.extend([pack_status_history_dict1, pack_status_history_dict2])

                    Notifications(user_id=user_id, call_from_client=call_from_client).add_pack_status_change_history(
                        pack_status_list)

                    logger.debug("set_status: Records saved in pack history for pack_ids- {}"
                                 .format(deleted_pack_ids))

                # after removal of deleted packs if pack_ids list is empty then return success response
                if not pack_ids:
                    return create_response(data=0, additional_info={"deleted_packs": deleted_pack_display_ids})

            # if packs are marked delete or manual then their mfd status and mfd canister sharing is checked to inform
            # user about the same
            logger.debug('forced_pack_manual: {}'.format(forced_pack_manual))
            if status in [settings.MANUAL_PACK_STATUS, settings.DELETED_PACK_STATUS] or forced_pack_manual:
                affected_mfd_pack_ids, affected_mfd_canister_ids, affected_mfd_analysis_details_ids, canisters_filled = \
                    get_sharing_packs(pack_ids, forced_pack_manual, status_changed_from_ips)
                logger.info('affected_mfd_analysis_ids: {} affected_mfd_analysis_details_ids {}'.format(
                    affected_mfd_canister_ids, affected_mfd_analysis_details_ids))
                packs_having_mfd_canister = set(pack_ids).intersection(set(affected_mfd_pack_ids))
                extra_mfd_packs = set(affected_mfd_pack_ids) - packs_having_mfd_canister

                # if user_confirmation is false and either packs shares mfd canister with other packs or mfd canisters
                # are filled then only information is returned else the action on packs and mfd canisters are taken
                if not user_confirmation and not forced_pack_manual and not status_changed_from_ips:
                    return create_response({'pack_ids': pack_ids,
                                            'mfd_packs': packs_having_mfd_canister,
                                            'affected_mfd_packs': extra_mfd_packs,
                                            'canisters_filled': canisters_filled})
                else:
                    if extra_mfd_packs and not forced_pack_manual:
                        pack_ids = set(pack_ids)
                        pack_ids.update(extra_mfd_packs)
                        pack_ids = list(pack_ids)

                    pack_and_display_ids = PackDetails.db_get_pack_and_display_ids(pack_ids)

                    # In the scenario where we don't have shared MFD
                    if not extra_mfd_packs:
                        # Delete is triggered from IPS
                        if status_changed_from_ips:
                            update_ips = False
                        # Delete is triggered from DosePack
                        else:
                            update_ips = True

                        # Associate every pack with its respective Delete Reason
                        reason_dict = {pack_id: prepare_pack_reason_dict(pack_id, pack_and_display_ids[pack_id],
                                                                         reason) for pack_id in pack_ids}

                    # In the scenario where we have a shared MFD and Delete is triggered from IPS or DosePack
                    else:
                        # Store the list of packs that are actually deleted so that they can be used as part of delete
                        # reason with the other packs that has shared MFD
                        user_deleted_packs = set(pack_ids) - extra_mfd_packs
                        user_deleted_pack_display_ids = [str(pack_and_display_ids[pack_id]) for pack_id in
                                                         user_deleted_packs]

                        # Prepare pack display ID due to which shared MFD gets deleted
                        # Get the pack display ID delimited by hyphen instead of comma to avoid parsing errors in IPS
                        user_deleted_pack_display_ids = '-'.join(user_deleted_pack_display_ids)

                        # Associate every pack with its respective Delete Reason
                        for pack_id in pack_ids:
                            if pack_id in extra_mfd_packs:
                                reason_dict[pack_id] = prepare_pack_reason_dict(pack_id, pack_and_display_ids[pack_id],
                                                                                DELETE_PACK_DESC_SHARED_MFD.format(
                                                                                    user_deleted_pack_display_ids))
                            else:
                                reason_dict[pack_id] = prepare_pack_reason_dict(pack_id, pack_and_display_ids[pack_id],
                                                                                reason)
                        update_ips = True

            # To handle the scenarios when pack status is not deleted or manual or forced manual
            # Here inside prepare_pack_reason_dict function, 2nd argument is pack display ID but it is not in use here
            # so we are passing pack_id only. In future, if pack display ID is needed then modifications will be
            # required.
            else:
                reason_dict = {pack_id: prepare_pack_reason_dict(pack_id, pack_id,
                                                                 reason) for pack_id in pack_ids}

            logger.debug('affected packs: ' + str(pack_ids))
            if status != settings.FILLED_PARTIALLY_STATUS:
                # deleting partially filled data for the packs when status is changed from 51(FILLED_PARTIALLY_STATUS)
                # to any other
                partial_pack_ids = PackDetails.select(PackDetails.id).dicts() \
                    .where(PackDetails.id << pack_ids, PackDetails.pack_status == settings.FILLED_PARTIALLY_STATUS)
                partial_pack_ids = [item['id'] for item in list(partial_pack_ids)]
                if partial_pack_ids:
                    update_status = PartiallyFilledPack.delete_partially_filled_pack({'pack_ids': partial_pack_ids})
                logger.info('partially_filled_deleted_pack_ids ' + str(partial_pack_ids))
            if filled_at in [settings.FILLED_AT_PRI_PROCESSING, settings.FILLED_AT_POST_PROCESSING,
                             settings.FILLED_AT_PRI_BATCH_ALLOCATION,
                             settings.FILLED_AT_MANUAL_VERIFICATION_STATION] and \
                    status in [settings.MANUAL_PACK_STATUS, settings.PARTIALLY_FILLED_BY_ROBOT] and \
                    transfer_to_manual_fill_system:
                pack_user_map_list = list()
                order_no = PackDetails.select(fn.MAX(PackDetails.order_no).alias('order_no')) \
                    .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id).dicts() \
                    .where(PackDetails.company_id == company_id).get()
                length = len(pack_ids)
                order_no = order_no['order_no']
                if order_no is None:
                    order_no = 1
                elif (order_no == 0) | (order_no + length >= settings.DB_MAX_INT_VALUE):
                    order_no = 1
                else:
                    order_no += 1

                # assigning orders to packs
                order_no_list = list(range(order_no, order_no + length))

                updated_pack_query = PackDetails.select(PackDetails.id) \
                    .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
                    .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
                    .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                    .where(PackDetails.id << pack_ids) \
                    .order_by(PackHeader.scheduled_delivery_date, FacilityMaster.facility_name, PackDetails.id)
                updated_list = list(updated_pack_query.dicts())
                for index, item in enumerate(order_no_list):
                    update_info = PackDetails.update(order_no=order_no_list[index]).where(
                        PackDetails.id == int(updated_list[index]['id'])).execute()

                # When user selects the reason of Drugs out of Stock or Missing Pills from MVS, we need to process
                # the drugs appropriately based on the specified reason
                if reason_action == MVS_DRUGS_OUT_OF_STOCK:
                    missing_drug_mapping_dict = {"reason_action": reason_action,
                                                 "drug_list": drug_list}

                if reason_action == MVS_MISSING_PILLS:
                    missing_drug_mapping_dict = {"reason_action": reason_action,
                                                 "reason_rx_no_list": reason_rx_no_list}

                # update pack_user_map and send notification
                user_pack_mapping_list = {"pack_id_list": pack_ids, "assigned_to": assigned_to, "user_id": user_id,
                                          "call_from_client": call_from_client}
                user_pack_mapping_list.update(missing_drug_mapping_dict)
                pack_assign_status = map_user_pack([user_pack_mapping_list])
                if not pack_assign_status:
                    return error(2001)

            if status in settings.PACK_FILLING_DONE_STATUS_LIST and company_id and \
                    not transfer_to_manual_fill_system:
                if status != settings.DISCARDED_PACK_STATUS and ips_username:
                    # If pack is not discarded and marked filled
                    # then update IPS about it if ips_username is provided
                    ips_comm_settings = CompanySetting.db_get_ips_communication_settings(company_id)
                    settings_present = all(key in ips_comm_settings for key in settings.IPS_COMMUNICATION_SETTINGS)
                    if settings_present:
                        ips_pack_ids = PackDetails.db_get_pack_display_ids(pack_ids)
                        pack_and_display_ids = PackDetails.db_get_pack_and_display_ids(pack_ids)
                        t = ExcThread([], name='ips_updatefilledby',
                                      target=update_packs_filled_by_in_ips,
                                      args=(ips_pack_ids, ips_username, pack_and_display_ids, ips_comm_settings))
                        t.start()
                    else:
                        logger.error('Required Settings not present to update filled by in Pharmacy Software.'
                                     ' company_id: {}'.format(company_id))
                logger.info(
                    "before_track_consumed_packs_called : pack ids: " + str(pack_ids) + " status: " + str(status) +
                    " company_id " + str(company_id))
                track_consumed_packs(pack_ids, company_id)
                if status in settings.PACK_FILLING_DONE_STATUS_LIST or status == settings.FILLED_PARTIALLY_STATUS:
                    update_set_last_seen(pack_ids)

            pack_status_dict = {}
            pack_status_list = []

            for pack_id in pack_ids:
                pack_status_dict["pack_id"] = pack_id
                pack_status_dict["old_status"] = PackDetails.db_get_status_numeric(pack_id)
                pack_status_dict["new_status"] = status
                pack_status_list.append(pack_status_dict.copy())
            Notifications(call_from_client=call_from_client).add_pack_status_change_history(
                pack_status_list=pack_status_list, pack_status_change_from_ips=status_changed_from_ips)

            # a) Replaced "reason" string parameter with "packid_delete_reason" dictionary parameter where it maps
            # individual pack with its respective reason
            # b) This is done because we need to send back the delete reason to IPS and it can have more than one reason
            # when packs have shared MFD
            # c) update_ips = True then send call for delete sync to IPS else False
            # This will be false when we have received delete call from IPS and we don't have any shared MFD situation
            response = PackDetails.db_set_status(
                pack_ids, status, user_id,
                reason_dict=reason_dict,
                use_company_id=use_company_id,
                system_id=system_id,
                filled_at=filled_at,
                fill_time=fill_time,
                filled_by=ips_username,
                transfer_to_manual_fill_system=transfer_to_manual_fill_system
            )
            logger.info("db_set_status response for pack_ids: {} is {}, for status, {} reason_dict {} and update_ips {}"
                        .format(pack_ids, json.loads(response), status, reason_dict, update_ips))

            # If the packs get deleted then we need to communicate the same back to IPS
            # Do not Trigger Delete Call to IPS during the Change Rx flow
            if json.loads(response)["status"] == settings.SUCCESS_RESPONSE and status == settings.DELETED_PACK_STATUS \
                    and company_id and reason_dict:

                for pack_id in reason_dict:
                    pack_display_ids.append(str(reason_dict[pack_id].get("pack_display_id")))
                    delete_reason_list.append(reason_dict[pack_id].get("reason"))
                if update_ips and not change_rx:
                    response_data = delete_pack_in_ips(pack_display_ids, ips_username, delete_reason_list, company_id,
                                                   changerx_flow)

                logger.info('After response pack_display_ids {}'.format(pack_display_ids))

            # if packs having mfd canisters are being deleted or marked manual then rts is required for drugs
            if affected_mfd_analysis_details_ids:
                status = update_rts_data(list(set(affected_mfd_analysis_details_ids)),
                                         list(set(affected_mfd_canister_ids)), company_id=company_id,
                                         user_id=user_id,
                                         action_id=settings.PACK_ACTION_MAP[status])

            update_schedule_date = False
            if status in [settings.DELETED_PACK_STATUS, settings.MANUAL_PACK_STATUS]:
                batch_id, system_id = get_batch_id_from_pack_list(pack_ids)
                if batch_id is not None:
                    batch_status = get_batch_status_from_batch_id(batch_id)
                    if batch_status in [settings.BATCH_PENDING, settings.BATCH_CANISTER_TRANSFER_RECOMMENDED]:
                        update_schedule_date = True
                    if update_schedule_date:
                        update_status = update_scheduled_start_date_for_next_batches(pack_ids)
                    try:
                        update_replenish_based_on_system(system_id)
                    except (InternalError, IntegrityError) as e:
                        logger.error(e, exc_info=True)
                        return error(2001, e)
                    except ValueError as e:
                        return error(2005, str(e))

            # If status of other packs changed successfully and there are some deleted packs
            # then send deleted packs in response
            formatted_response = json.loads(response)
            if formatted_response["status"] == settings.SUCCESS_RESPONSE:
                return create_response(data=formatted_response["data"],
                                       additional_info={"deleted_packs": deleted_pack_display_ids,
                                                        "delete_pack_display_ids": pack_display_ids})
            return response

    except RealTimeDBException as e:
        return error(2001, str(e))
    except (PharmacySoftwareResponseException, PharmacySoftwareCommunicationException) as e:
        logger.error(e, exc_info=True)
        return error(7002)
    except Exception as e:  # just logging as optional and don't want to stop the flow
        logger.error(e, exc_info=True)


def get_batch_status_from_batch_id(batch_id):
    try:
        query = BatchMaster.select(BatchMaster.status).where(BatchMaster.id == batch_id).dicts().get()
        return query['status']
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def track_consumed_packs(pack_ids, company_id):
    """ Reduces consumed pack quantity from consumable tracker and updates consumable used
    """
    logger.info("in_track_consumed_packs : pack ids: " + str(pack_ids) + " company_id " + str(company_id))
    consumed_data = dict()
    consumed_data[settings.CONSUMABLE_TYPE_PACK_DOSEPACK_MULTIDOSE] = len(set(pack_ids))
    ConsumableTracker.db_remove_consumed_items(consumed_data, company_id)
    current_date = get_current_date()
    used_data = dict()
    used_data["used_quantity"] = len(set(pack_ids))
    ConsumableUsed.db_update_or_create(company_id, settings.CONSUMABLE_TYPE_PACK_DOSEPACK_MULTIDOSE, current_date,
                                       used_data)


def update_packs_filled_by_in_ips(pack_ids, ips_username, pack_and_display_ids, ips_comm_settings):
    """
    Iterates over pack_ids in batch and calls IPS webservice to set filled by
    default batch size: 4
    :param pack_ids: list
    :param ips_username: str
    :param pack_and_display_ids: dict
    :param ips_comm_settings: dict
    :return:
    """
    try:
        batch_size = int(os.environ.get('IPS_FILLED_BY_UPDATE_BATCH_SIZE', 4))
        logger.info('updating filled_by: {} in IPS for packs: {}'
                    .format(ips_username, pack_ids))
        for packs in batchify(pack_ids, batch_size):
            threads = list()
            for pack in packs:
                t = ExcThread([],
                              target=update_pack_filled_by_in_ips,
                              args=[pack, ips_username, pack_and_display_ids, ips_comm_settings])
                t.start()
                threads.append(t)
            [t.join() for t in threads]  # wait for threads to finish job

    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise RealTimeDBException
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error(e, exc_info=True)
        raise


@validate(required_fields=["pack_id", "company_id"], validate_pack_id='pack_id')
def get_slot_details(dict_pack_info):
    """ Take the pack id and returns the slots associated with the given pack id.

        Args:
            dict_pack_info (dict): The keys in it are pack_id(int)

        Returns:
           json: All the slots and the information associated with it.

        Examples:
            >>> get_slot_details({"pack_id":1})
    """
    pack_id = int(dict_pack_info["pack_id"])
    device_id = int(dict_pack_info["device_id"])
    company_id = int(dict_pack_info["company_id"])
    slot_data, _, _ = db_slot_details(pack_id, device_id, company_id)

    if not slot_data:
        return error(1004)

    return create_response(slot_data)


def store_slot_transaction(dict_slot_info):
    """ Gets the information from the processing robot and stores it in
    the database on the number of pills dropped by the robot.

        Args:
            dict_slot_info (dict): The information corresponding to each slot.

        Returns:
           Boolean: True or False

        Examples:
            >>> store_slot_transaction({})
    """
    slot_transaction_list = []
    for record in dict_slot_info:
        slot_transaction_list.append(record)
    with db.atomic():
        SlotTransaction.insert_many(slot_transaction_list).execute()


def get_canister_list_for_adjustment(pack_id, device_id, company_id):
    """
    @function: get_canister_list_for_adjustment
    @createdBy: Manish Agarwal
    @createdDate: 7/22/2015
    @lastModifiedBy: Manish Agarwal
    @lastModifiedDate: 08/12/2015
    @type: function
    @param: int
    @purpose - Get the list of canister numbers to be used by the given
                pack id.
    @input -   {"pack_id" : 1}
    @output -  {0: 56, 1:34, 7:23}
    """
    dict_canister_quantity = {}

    # get the slot details
    slot_details = get_slot_details({"pack_id": pack_id, "device_id": device_id, "company_id": company_id})
    slot_details = json.loads(slot_details)
    slot_details = slot_details["data"]

    for key, value in slot_details.items():
        # iterate over key value pair in slot details
        for item in value:
            canister_id = item["canister_id"]
            quantity = int(item["quantity"])
            if canister_id in dict_canister_quantity:
                dict_canister_quantity[canister_id] += quantity
            else:
                dict_canister_quantity[canister_id] = quantity
    return dict_canister_quantity

def update_canister_quantity_after_pack_is_processed(dict_canister_update_info, device_id):
    """
    @function: update_canister_quantity_after_pack_is_processed
    @createdBy: Manish Agarwal
    @createdDate: 7/22/2015
    @lastModifiedBy: Manish Agarwal
    @lastModifiedDate: 08/12/2015
    @type: function
    @param: dict, str, date
    @purpose - update the canister quantity with given asjusted quantity
    @input - {"1":56, "2":90}
    @output - {"status": "success|failure",  "error": "none|error_msg"}
    """
    # begin transaction
    with db.transaction():
        # iterate over the key value pairs
        for key, value in dict_canister_update_info.items():
            # update the canister quantity
            if int(key) > 0:
                update_inventory_after_pack_is_processed(
                    {"available_quantity": CanisterMaster.available_quantity - int(value)}, key, device_id)


def update_inventory_after_pack_is_processed(dict_canister_info, canister_id, device_id):
    # todo need to check why device_id is being sent ad param but not being used
    try:
        status = CanisterMaster.update(**dict_canister_info). \
            where(CanisterMaster.id == canister_id)
        status = status.execute()
        return True, status
    except Exception as ex:
        return False, ex


# def stencil_label(stencil_id, seq_no, regenerate=False):
#     """
#     Generates stencil label and uploads to cloud storage
#
#     :param stencil_id: str
#     :param regenerate: str
#     :param regenerate: bool
#     :return: str
#     """
#     file_name = '{}.pdf'.format(stencil_id)
#     if not os.path.exists(pack_stencil_label_dir):
#         os.makedirs(pack_stencil_label_dir)
#     label_path = os.path.join(pack_stencil_label_dir, file_name)
#     if not regenerate:
#         if blob_exists(file_name, pack_stencil_label_dir):
#             return file_name
#     logger.info('Starting Stencil Label Generation with ID {}'.format(stencil_id))
#     generate_stencil_label(label_path, stencil_id, seq_no)
#     create_blob(label_path, file_name, pack_stencil_label_dir)
#     logger.info('Stencil Label Generated with ID {}'.format(stencil_id))
#
#     return file_name
#

def get_pack_canister_usage_data(data):
    time_zone = data.get('time_zone', None)
    analytical_date = data.get('fill_date', None)
    pack_id = data.get('pack_id', None)
    clauses = list()
    fill_date = fn.date(fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC, time_zone))
    if time_zone and analytical_date:
        clauses.append(
            (fill_date == analytical_date) | (PackDetails.pack_status == settings.PACK_STATUS['Progress']))
    if pack_id:
        clauses.append((PackDetails.id == pack_id))
    try:
        join_condition = ((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                          (UniqueDrug.txr == DrugMaster.txr))

        pack_details = SlotTransaction.select(SlotTransaction.pack_id.alias('pack_id'),
                                              UniqueDrug.id.alias('unique_drug_id'),
                                              SlotTransaction.location_id,
                                              SlotHeader.pack_grid_id,
                                              SlotTransaction.canister_id).dicts() \
            .join(SlotDetails, on=SlotDetails.id == SlotTransaction.slot_id) \
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotTransaction.drug_id) \
            .join(UniqueDrug, on=join_condition) \
            .join(PackDetails, on=SlotTransaction.pack_id == PackDetails.id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(SlotTransaction.pack_id, SlotHeader.pack_grid_id, UniqueDrug.id)
        return list(pack_details)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise


@validate(required_fields=["batch_id", "system_id", "company_id"])
def get_batch_drug_details(dict_batch_info):
    batch_id = dict_batch_info['batch_id']
    system_id = dict_batch_info['system_id']
    company_id = dict_batch_info['company_id']

    if len(dict_batch_info['filter_fields']) > 0:
        filter_fields = json.loads(dict_batch_info['filter_fields'])
    else:
        filter_fields = dict_batch_info['filter_fields']

    if len(dict_batch_info['paginate']) > 0:
        paginate = json.loads(dict_batch_info['paginate'])
    else:
        paginate = dict_batch_info['paginate']

    if len(dict_batch_info['sort_fields']) > 0:
        sort_fields = json.loads(dict_batch_info['sort_fields'])
    else:
        sort_fields = dict_batch_info['sort_fields']

    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, 'Missing key(s) in paginate.')

    drug_data = []
    response = {}
    clauses = list()
    clauses.append((PackDetails.system_id == system_id))
    clauses.append((PackDetails.batch_id == batch_id))

    like_search_list = ['ndc', 'imprint', 'color', 'shape', 'drug_name']
    exact_search_list = ['strength', 'canister_id']
    membership_search_list = []
    having_search_list = []
    order_list = []

    if sort_fields:
        order_list.extend(sort_fields)

    fields_dict = {
        # do not give alias here, instead give it in select_fields,
        # as this can be reused in where clause
        "canister_master_id": CanisterMaster.id,
        "ndc": DrugMaster.ndc,
        "imprint": DrugMaster.imprint,
        "strength": DrugMaster.strength_value,
        "color": DrugMaster.color,
        "shape": CustomDrugShape.name,
        "drug_fndc_txr": DrugMaster.concated_fndc_txr_field("##"),
        "location_number": PackAnalysisDetails.location_number,
        "drug_name": DrugMaster.drug_name,
        "display_location": LocationMaster.display_location,
        "canister_id": PackAnalysisDetails.canister_id,
        "available_quantity": CanisterMaster.available_quantity

    }

    try:
        select_fields = [fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysisDetails.canister_id)).alias('canister_id'),
                         DrugMaster.id.alias('drug_master_id'),
                         DrugMaster.strength,
                         DrugMaster.strength_value,
                         DrugMaster.drug_name,
                         DrugMaster.txr,
                         DrugMaster.ndc,
                         DrugMaster.formatted_ndc,
                         DrugMaster.color,
                         DrugMaster.imprint,
                         fields_dict['drug_fndc_txr'].alias('drug_fndc_txr'),
                         fn.sum(SlotDetails.quantity).alias("required_quantity"),

                         fn.GROUP_CONCAT(
                             Clause(fn.CONCAT(fn.IF(SlotDetails.quantity.is_null(True), 'null',
                                                    SlotDetails.quantity), ',',
                                              fn.IF(SlotDetails.is_manual.is_null(True), 'null',
                                                    SlotDetails.is_manual)),
                                    SQL(" SEPARATOR ' | ' "))).coerce(False).alias('slot_details'),

                         fn.GROUP_CONCAT(
                             DeviceMaster.name, '-', LocationMaster.display_location
                         ).coerce(False).alias('canister_list'),

                         fn.GROUP_CONCAT(Clause(fn.CONCAT
                                                (fn.IF(CanisterMaster.id.is_null(True), 'null',
                                                       CanisterMaster.id), ',',
                                                 fn.IF(CanisterMaster.available_quantity.is_null(True), 'null',
                                                       CanisterMaster.available_quantity), ',',
                                                 fn.IF(CanisterMaster.drug_id.is_null(True), 'null',
                                                       CanisterMaster.drug_id), ',',

                                                 fn.IF(CanisterMaster.rfid.is_null(True), 'null',
                                                       CanisterMaster.rfid), ',',
                                                 fn.IF(CanisterMaster.active.is_null(True), 'null',
                                                       CanisterMaster.active), ',',
                                                 fn.IF(CanisterMaster.canister_type.is_null(True), 'null',
                                                       CanisterMaster.canister_type), ',',
                                                 fn.IF(LocationMaster.display_location.is_null(True), 'null',
                                                       LocationMaster.display_location), ',',
                                                 fn.IF(LocationMaster.location_number.is_null(True), 'null',
                                                       LocationMaster.location_number), ',',
                                                 fn.IF(PackAnalysisDetails.device_id.is_null(True), 'null',
                                                       PackAnalysisDetails.device_id), ',',
                                                 fn.IF(DeviceMaster.name.is_null(True), 'N.A.', DeviceMaster.name)),
                                                SQL(" SEPARATOR ' | ' "))).coerce(False).alias('canister_id_list'),

                         DrugDimension.id.alias('drug_dimension_id'),
                         DrugDimension.shape,
                         DrugDimension.depth, DrugDimension.width, DrugDimension.length, DrugDimension.fillet,
                         DrugDimension.unique_drug_id,
                         CustomDrugShape.name.alias("shape_name"),
                         CustomDrugShape.image_name,
                         CustomDrugShape.id.alias('custom_shape_id'),
                         ]

        query = PackDetails.select(*select_fields).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackAnalysis, JOIN_LEFT_OUTER,
                  on=((PackAnalysis.pack_id == PackDetails.id) &
                      (PackDetails.batch_id == PackAnalysis.batch_id))) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER,
                  on=((PackAnalysisDetails.analysis_id == PackAnalysis.id)
                      & (PackAnalysisDetails.slot_id == SlotDetails.id))) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=UniqueDrug.drug_id == DrugMaster.id) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=DrugDimension.shape == CustomDrugShape.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr)

        results, count, non_paginate_result = get_results(query.dicts(), fields_dict, filter_fields=filter_fields,
                                                          clauses=clauses,
                                                          sort_fields=order_list,
                                                          paginate=paginate,
                                                          exact_search_list=exact_search_list,
                                                          like_search_list=like_search_list,
                                                          membership_search_list=membership_search_list,
                                                          having_search_list=having_search_list,
                                                          non_paginate_result_field_list=['drug_fndc_txr']
                                                          )

        for record in results:

            drug_id = record['formatted_ndc'] + "##" + record['txr']
            if drug_id not in drug_data:
                response_dict = {
                    'formatted_ndc_txr': drug_id,
                    'drug_name': record["drug_name"] + " " + record["strength_value"] + " " + record["strength"]
                }

                if record['canister_id_list'] is not None:
                    record['canister_id_list'] = set(record['canister_id_list'].split(' | '))
                else:
                    record['canister_id_list']

                if record['canister_list'] is not None:
                    record['canister_list'] = set(record['canister_list'].split(','))
                else:
                    record['canister_list']
                response_dict.update(record)
                drug_data.append(response_dict)

        response['records'] = drug_data
        response['total_drugs'] = count
        response['drug_fndc_txr'] = non_paginate_result

        logger.info(response)
        return create_response(response)

    except IntegrityError as ex:
        logger.error(ex, exc_info=True)
        raise IntegrityError
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError
    except Exception as e:
        logger.info(e)


@validate(required_fields=['batch_id', 'system_id'])
def revert_batch(batch_dict):
    """
    changes batch_id for pending packs, deletes related data and marks batch as processing done
    :param batch_dict: format: {"batch_id":703, "system_id": 2}
    :return:
    """
    try:
        with db.transaction():
            batch_id = batch_dict['batch_id']
            system_id = batch_dict['system_id']
            pack_id_query = PackDetails.select().dicts().where(PackDetails.batch_id == batch_id,
                                                               PackDetails.system_id == system_id,
                                                               PackDetails.pack_status == settings.PENDING_PACK_STATUS)
            pack_ids = [item['id'] for item in list(pack_id_query)]

            if pack_ids:
                pack_analysis = PackAnalysis.select().dicts().where(PackAnalysis.pack_id << pack_ids,
                                                                    PackAnalysis.batch_id == batch_id)

                analysis_ids = [item['id'] for item in list(pack_analysis)]

                if analysis_ids:
                    status1 = PackAnalysisDetails.delete().where(
                        PackAnalysisDetails.analysis_id << analysis_ids).execute()

                    status2 = PackAnalysis.delete().where(PackAnalysis.id << analysis_ids).execute()

                pack_status = PackDetails.update(batch_id=None, system_id=None, facility_dis_id=None).where(
                    PackDetails.id << pack_ids).execute()

            status3 = ReservedCanister.delete().where(ReservedCanister.batch_id == batch_id).execute()

            batch_update_status = BatchMaster.update(status=settings.BATCH_PROCESSING_COMPLETE) \
                .where(BatchMaster.id == batch_id).execute()

            device_data = DeviceMaster.db_get_robots_by_system_id(system_id, [settings.ROBOT_SYSTEM_VERSIONS['v3']])
            for device in device_data:
                response = {
                    'canister_list': [],
                    'batch_to_be_highlited': [],
                    'pending_packs': 0,
                    'current_batch_processing_time': 0,
                    'device_id': device['id'],
                    'time_update': 0,
                    'blink_timer': False,
                    'batch_name': None,
                    'batch_id': None,
                }
                status, data = update_replenish_queue_count(response, device['system_id'], device['id'])
                if not status:
                    raise ValueError('Error in updating couch-db')

        return create_response({'status': True})
    except (IntegrityError, InternalError):
        return error(2001)
    except ValueError as e:
        return error(2005, str(e))


@validate(required_fields=["batch_id", "system_id", "company_id"])
def get_batch_drug_details(dict_batch_info):
    logger.info("In get_batch_drug_details")

    try:
        batch_id = json.loads(dict_batch_info['batch_id'])
        system_id = dict_batch_info['system_id']
        company_id = dict_batch_info['company_id']
        upcoming_batches = dict_batch_info.get('upcoming_batches', False)

        if type(batch_id) == int or type(batch_id) == str:
            batch_id = [batch_id]

        batch_status = BatchMaster.db_get_batch_status(batch_id[0])

        logger.info("Input args of get_batch_drug_details {}".format(dict_batch_info))

        if len(dict_batch_info['filter_fields']) > 0:
            filter_fields = json.loads(dict_batch_info['filter_fields'])
        else:
            filter_fields = dict_batch_info['filter_fields']

        if len(dict_batch_info['paginate']) > 0:
            paginate = json.loads(dict_batch_info['paginate'])
        else:
            paginate = dict_batch_info['paginate']

        if len(dict_batch_info['sort_fields']) > 0:
            sort_fields = json.loads(dict_batch_info['sort_fields'])
        else:
            sort_fields = dict_batch_info['sort_fields']

        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        if batch_status == settings.BATCH_IMPORTED:
            return get_batch_drug_imported(system_id=system_id, batch_id=batch_id[0],
                                           filter_fields=filter_fields, paginate=paginate,
                                           sort_fields=sort_fields)
        else:
            logger.info("get_batch_drug_details {}".format(upcoming_batches))
            return get_batch_drug_not_imported(batch_id=batch_id, filter_fields=filter_fields,
                                               sort_fields=sort_fields, paginate=paginate,
                                               company_id=company_id)

    except ValueError as e:
        logger.error("Error in get_batch_drug_details {}".format(e))
        return error(0)

    except Exception as e:
        logger.error("Error in get_batch_drug_details {}".format(e))
        return error(0)


@log_args
def get_batch_drug_not_imported(batch_id, filter_fields, sort_fields, paginate, company_id):
    logger.debug("In get_batch_drug_not_imported")

    try:
        response = dict()
        like_search_list = ["drug_name"]
        membership_search_list = []
        order_list = list()

        if sort_fields:
            order_list.extend(sort_fields)
        else:
            order_list = [["drug_name", 1]]

        fields_dict = {"ndc": DrugMaster.ndc,
                       "drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
                       "available_quantity": CanisterMaster.available_quantity,
                       "updated_by": DrugStockHistory.created_by
                       }
        if "ndc" in filter_fields and filter_fields["ndc"]:
            ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id , upc, bottle_total_qty= get_ndc_list_for_barcode(
                {"scanned_ndc": filter_fields['ndc'], "required_entity": "ndc"})
            if ndc_list:
                membership_search_list.append("ndc")
                filter_fields[
                    "ndc"], drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                    {"scanned_ndc": filter_fields['ndc'],
                     "required_entity": "ndc"})
            else:
                response = {"drug_data": [], "total_drug_count": 0}
                return create_response(response)

        unique_drugs = PackDetails.select(fn.DISTINCT(DrugMaster.id).alias('drug_id'),
                                          DrugMaster.concated_fndc_txr_field().alias('fndc_txr'),
                                          fn.SUM(SlotDetails.quantity).alias('required_qty')).dicts() \
            .join(BatchMaster, on=PackDetails.batch_id == BatchMaster.id) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(BatchMaster.id << batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS]) \
            .group_by(DrugMaster.concated_fndc_txr_field())
        logger.debug(unique_drugs)

        unique_drug_dict = {}
        for record in unique_drugs:
            unique_drug_dict[record['fndc_txr']] = int(record['required_qty'])
        print(unique_drug_dict)

        if len(unique_drug_dict):
            query = DrugMaster.select(DrugMaster.id.alias('drug_id'),
                                      DrugMaster.strength,
                                      DrugMaster.strength_value,
                                      DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                      DrugMaster.concated_fndc_txr_field().alias('fndc_txr'),
                                      DrugMaster.ndc,
                                      DrugMaster.image_name,
                                      DrugMaster.shape,
                                      DrugMaster.imprint,
                                      fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                            DrugDetails.last_seen_by, ).alias('last_seen_with'),
                                      fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                                            DrugDetails.last_seen_date).alias('last_seen_on'),
                                      fn.SUM(CanisterMaster.available_quantity).alias('available_qty'),
                                      fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                            DrugStockHistory.is_in_stock).alias(
                                          "is_in_stock"),
                                      fn.IF(DrugStockHistory.created_by.is_null(True), None,
                                            DrugStockHistory.created_by) \
                                      .alias('stock_updated_by')).dicts() \
                .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                      & (UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                        (DrugDetails.company_id == company_id))) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == settings.is_drug_active) &
                                                             (DrugStockHistory.company_id == company_id))) \
                .where(DrugMaster.concated_fndc_txr_field() << list(unique_drug_dict.keys())) \
                .group_by(DrugMaster.concated_fndc_txr_field())

            results, count, non_paginate_result = get_results(query.dicts(), fields_dict=fields_dict,
                                                              filter_fields=filter_fields,
                                                              like_search_list=like_search_list,
                                                              sort_fields=order_list,
                                                              paginate=paginate,
                                                              membership_search_list=membership_search_list,
                                                              non_paginate_result_field_list=['fndc_txr'])

            for data in results:
                logger.debug(data['drug_id'])
                if data['fndc_txr'] in unique_drug_dict.keys():
                    data['required_qty'] = unique_drug_dict[data['fndc_txr']]

            response['drug_data'] = results

            response['total_drug_count'] = count
            response['drug_fndc_txr'] = non_paginate_result

        return create_response(response)

    except IntegrityError as ex:
        logger.error(ex, exc_info=True)
        raise IntegrityError
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError


def get_canister_info_from_canister_list(batch_id, canister_list):
    """
    Function to get canister location info from canister list after batch import
    @param batch_id:
    @param canister_list:
    @return:
    """
    try:
        canister_info_list = list()
        device_info = list()
        clauses = list()
        clauses.append((PackDetails.batch_id == batch_id))
        clauses.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS])
        if len(canister_list):
            canister_list = [int(can) for can in canister_list]
            clauses.append(PackAnalysisDetails.canister_id << canister_list)

            select_fields = [fn.IF(CanisterMaster.id.is_null(True), 'null',
                                   CanisterMaster.id).alias('canister_id'),
                             fn.IF(CanisterMaster.available_quantity.is_null(True), 'null',
                                   CanisterMaster.available_quantity).alias('available_quantity'),
                             fn.IF(CanisterMaster.drug_id.is_null(True), 'null',
                                   CanisterMaster.drug_id).alias('drug_id'),

                             fn.IF(CanisterMaster.rfid.is_null(True), 'null',
                                   CanisterMaster.rfid).alias('rfid'),
                             fn.IF(CanisterMaster.active.is_null(True), 'null',
                                   CanisterMaster.active).alias('active'),
                             fn.IF(CanisterMaster.canister_type.is_null(True), 'null',
                                   CanisterMaster.canister_type).alias('canister_type'),
                             fn.IF(LocationMaster.display_location.is_null(True), 'null',
                                   LocationMaster.display_location).alias('display_location'),
                             fn.IF(LocationMaster.location_number.is_null(True), 'null',
                                   LocationMaster.location_number).alias('location_number'),
                             fn.IF(PackAnalysisDetails.device_id.is_null(True), 'null',
                                   PackAnalysisDetails.device_id).alias('device_id'),
                             fn.IF(DeviceMaster.name.is_null(True), 'N.A.', DeviceMaster.name).alias('name'),
                             fn.GROUP_CONCAT(
                                 DeviceMaster.name, '-', LocationMaster.display_location
                             ).alias('canister_list'),
                             ]

            query = PackDetails.select(*select_fields) \
                .join(PackAnalysis, JOIN_LEFT_OUTER,
                      on=((PackAnalysis.pack_id == PackDetails.id) &
                          (PackDetails.batch_id == PackAnalysis.batch_id))) \
                .join(PackAnalysisDetails, JOIN_LEFT_OUTER,
                      on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .group_by(CanisterMaster.id) \
                .where(*clauses)

            for record in query.dicts():
                can_info = [record['canister_id'],
                            record['available_quantity'],
                            record['drug_id'],
                            record['rfid'],
                            record['active'],
                            record['canister_type'],
                            record['display_location'],
                            record['location_number'],
                            record['device_id'],
                            record['name']]

                if record['canister_list']:
                    device_name_loc = list(record['canister_list'].split(","))

                    for device_name_loc_data in device_name_loc:
                        if device_name_loc_data not in device_info:
                            device_info.append(device_name_loc_data)

                else:
                    device_info = None

                canister_info_list.append(','.join(can_info))

        return canister_info_list, device_info

    except IntegrityError as ex:
        logger.error(ex, exc_info=True)
        raise IntegrityError
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError
    except Exception as e:
        logger.info(e)
        return None, None


@log_args
def get_batch_drug_imported(batch_id, filter_fields, sort_fields, paginate, system_id):
    logger.debug("In get_batch_drug_imported")
    """
    @desc: get_batch_drug_imported
    @param batch_id:
    @return:
    """
    # batch_status = BatchMaster.db_get_batch_status(batch_id)
    # logger.info("batch status for batch unique drugs {}".format(batch_status))
    drug_data = []
    response = {}
    clauses = list()
    clauses.append((PackDetails.system_id == system_id))
    clauses.append((PackDetails.batch_id == batch_id))
    clauses.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS])
    # clauses.append(CanisterMaster.active == settings.is_canister_active)
    # clauses.append(CanisterMaster.company_id == company_id)

    like_search_list = ['imprint', 'color', 'shape', 'drug_name']
    exact_search_list = ['strength', 'canister_id']
    membership_search_list = ['ndc']
    having_search_list = []
    order_list = [["drug_name", 1]]

    if sort_fields:
        order_list.extend(sort_fields)

    fields_dict = {
        # do not give alias here, instead give it in select_fields,
        # as this can be reused in where clause
        "canister_master_id": CanisterMaster.id,
        "ndc": DrugMaster.ndc,
        "imprint": DrugMaster.imprint,
        "strength": DrugMaster.strength_value,
        "color": DrugMaster.color,
        "shape": CustomDrugShape.name,
        "drug_fndc_txr": DrugMaster.concated_fndc_txr_field("##"),
        "location_number": PackAnalysisDetails.location_number,
        "drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
        "display_location": LocationMaster.display_location,
        "canister_id": PackAnalysisDetails.canister_id,
        "available_quantity": CanisterMaster.available_quantity

    }

    try:
        select_fields = [fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.id)).alias('canister_id'),
                         DrugMaster.id.alias('drug_master_id'),
                         DrugMaster.strength,
                         DrugMaster.strength_value,
                         DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                         DrugMaster.txr,
                         DrugMaster.ndc,
                         DrugMaster.formatted_ndc,
                         DrugMaster.color,
                         DrugMaster.imprint,
                         DrugMaster.image_name,
                         DrugMaster.shape.alias("shape_name"),
                         fields_dict['drug_fndc_txr'].alias('drug_fndc_txr'),
                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                               DrugStockHistory.is_in_stock).alias("is_in_stock"),
                         fn.IF(DrugStockHistory.created_by.is_null(True), None,
                               DrugStockHistory.created_by).alias('stock_updated_by'),
                         fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                               DrugDetails.last_seen_by, ).alias('last_seen_with'),
                         fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                               DrugDetails.last_seen_date).alias('last_seen_on'),
                         fn.sum(SlotDetails.quantity).alias("required_quantity"),
                         fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.id)).alias('pack_id_list'),
                         DrugDimension.id.alias('drug_dimension_id'),
                         DrugDimension.shape,
                         DrugDimension.depth, DrugDimension.width, DrugDimension.length, DrugDimension.fillet,
                         DrugDimension.unique_drug_id,
                         CustomDrugShape.id.alias('custom_shape_id')
                         # fn.GROUP_CONCAT(
                         #     Clause(fn.CONCAT(fn.IF(SlotDetails.quantity.is_null(True), 'null',
                         #                            SlotDetails.quantity), ',',
                         #                      fn.IF(SlotDetails.is_manual.is_null(True), 'null',
                         #                            SlotDetails.is_manual)),
                         #            SQL(" SEPARATOR ' | ' "))).coerce(False).alias('slot_details'),
                         ]
        if "ndc" in filter_fields and filter_fields["ndc"]:
            ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                {"scanned_ndc": filter_fields['ndc'], "required_entity": "ndc"})
            if ndc_list:
                filter_fields[
                    "ndc"], drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                    {"scanned_ndc": filter_fields['ndc'],
                     "required_entity": "ndc"})
            else:
                response = {"records": [], "total_drugs": 0, "drug_fndc_txr": {}}
                return create_response(response)

        query = PackDetails.select(*select_fields).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id))) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=DrugDimension.shape == CustomDrugShape.id) \
            .join(PackAnalysis, JOIN_LEFT_OUTER,
                  on=((PackAnalysis.pack_id == PackDetails.id) &
                      (PackDetails.batch_id == PackAnalysis.batch_id))) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER,
                  on=((PackAnalysisDetails.analysis_id == PackAnalysis.id)
                      & (PackAnalysisDetails.slot_id == SlotDetails.id))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == settings.is_drug_active) &
                                                         (DrugStockHistory.company_id == PackDetails.company_id))) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
        logger.info(query)

        results, count, non_paginate_result = get_results(query.dicts(), fields_dict, filter_fields=filter_fields,
                                                          clauses=clauses,
                                                          sort_fields=order_list,
                                                          paginate=paginate,
                                                          exact_search_list=exact_search_list,
                                                          like_search_list=like_search_list,
                                                          membership_search_list=membership_search_list,
                                                          having_search_list=having_search_list,
                                                          non_paginate_result_field_list=['drug_fndc_txr']
                                                          )

        for record in results:
            if record["txr"] is not None:
                drug_id = record['formatted_ndc'] + "##" + record['txr']
            else:
                drug_id = record['formatted_ndc'] + "##"
            if drug_id not in drug_data:
                response_dict = {
                    'formatted_ndc_txr': drug_id,
                    'drug_name': record["drug_name"]
                }

                if record['canister_id'] is not None:
                    record['canister_id_list'], device_info = get_canister_info_from_canister_list(batch_id,
                                                                                                   list(record[
                                                                                                       'canister_id'].split(
                                                                                                       ',')))
                    record['canister_list'] = device_info
                else:
                    record['canister_id_list'] = list()
                    record['canister_list'] = set()

                response_dict.update(record)
                drug_data.append(response_dict)

        response['records'] = drug_data
        response['total_drugs'] = count
        response['drug_fndc_txr'] = non_paginate_result

        logger.info(response)
        return create_response(response)

    except IntegrityError as ex:
        logger.error(ex, exc_info=True)
        raise IntegrityError
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError
    except Exception as e:
        logger.info(e)
        return error(0)


def get_pack_history_data(dict_pack_info):
    pack_id = int(dict_pack_info.get('pack_id'))
    pack_history_data = PackHistory.get_pack_history_by_pack_id(pack_id)
    return create_response(pack_history_data)


@validate(required_fields=["date_type", "date_from", "date_to", "company_id"])
def get_manual_count_stats(dict_patient_info):
    date_from = dict_patient_info.get('date_from')
    date_to = dict_patient_info.get('date_to')
    company_id = dict_patient_info.get('company_id')
    user_stats = dict_patient_info.get('user_stats', False)
    date_type = dict_patient_info.get('date_type')
    assigned_to = int(dict_patient_info['assigned_to'])
    pack_status_list = dict_patient_info.get('status', None)

    status_pack_count_dict, value_status_id_dict, total_packs, assigned_user_pack_count = PackDetails.get_manual_packs_data(
        company_id, date_from, date_to, date_type, assigned_to, user_stats, pack_status_list)
    response_data = {"pack_stats": [], "total_packs": total_packs, "assigned_user_pack_count": assigned_user_pack_count}
    data_dict = {}
    for status, pack_count in status_pack_count_dict.items():
        data_dict['value'] = status
        data_dict['pack_status'] = value_status_id_dict[status]
        data_dict['pack_count'] = pack_count
        response_data['pack_stats'].append(deepcopy(data_dict))
    return create_response(response_data)


@validate(required_fields=["date_from", "date_to", "date_type", "company_id", "patient_id", "user_id"])
def get_similar_manual_packs(dict_patient_info):
    date_from = dict_patient_info.get('date_from')
    date_to = dict_patient_info.get('date_to')
    company_id = dict_patient_info.get('company_id')
    patient_id = json.loads(dict_patient_info.get('patient_id'))
    date_type = dict_patient_info.get('date_type')
    user_id = dict_patient_info.get('user_id')
    assigned_user_id = dict_patient_info.get('assigned_user_id')

    pack_data_dict = PackDetails.get_patient_manual_packs(patient_id, company_id, date_from, date_to, date_type,
                                                          user_id, assigned_user_id)
    return create_response(pack_data_dict)


@validate(required_fields=["batch_id", "system_id", "company_id"])
def get_batch_canister_manual_drugs(dict_batch_info):
    logger.info("input args for get_batch_canister_manual_drugs {}".format(dict_batch_info))
    batch_id = dict_batch_info['batch_id']
    system_id = dict_batch_info['system_id']
    company_id = dict_batch_info['company_id']
    pack_queue = dict_batch_info.get('pack_queue', True)
    drug_type = dict_batch_info['drug_type']
    list_type = str(dict_batch_info['list_type'])
    pack_id_list = dict_batch_info.get('pack_id_list', list())
    drug_data = dict()
    patient_data = dict()
    facility_data = dict()
    pack_display_ids_group = dict()
    response = {}

    try:
        if drug_type == "canister":
            query = PackAnalysisDetails.db_get_batch_canister_manual_drugs(batch_id=batch_id,
                                                                           list_type=list_type,
                                                                           pack_ids=pack_id_list,
                                                                           pack_queue=True)
        elif drug_type == "manual":
            query = get_batch_manual_drug_list(batch_id=batch_id,
                                               list_type=list_type,
                                               pack_ids=pack_id_list,
                                               pack_queue=True)


        else:
            return error(1020)

        for record in query:

            if list_type == "drug":
                txr = record['txr'] if record['txr'] is not None else ''
                drug_id = record['formatted_ndc'] + "##" + txr
                if drug_id not in drug_data.keys():
                    drug_data[drug_id] = list()

                if 'total_quantities' in record:
                    total_quant = record['total_quantities'].split(",")
                    req_quantity = sum([float(i) for i in total_quant])
                    record['required_quantity'] = int(req_quantity) if (
                                                                           req_quantity.is_integer()) is True else req_quantity
                    drug_data[drug_id].append(record)

                else:
                    record['required_quantity'] = None

            elif list_type == "patient":
                if record['patient_id'] not in patient_data.keys():
                    patient_data[record['patient_id']] = []
                    pack_display_ids_group[record['patient_id']] = set()

                if 'total_quantities' in record:
                    total_quant = record['total_quantities'].split(",")
                    req_quantity = sum([float(i) for i in total_quant])
                    record['required_quantity'] = int(req_quantity) if (
                                                                           req_quantity.is_integer()) is True else req_quantity

                else:
                    record['required_quantity'] = None

                pack_display_id_list = str(record['pack_display_ids_group']).split(",")
                pack_display_ids_group[record['patient_id']].update(pack_display_id_list)
                record['pack_display_ids_group'] = pack_display_ids_group[record['patient_id']]
                patient_data[record['patient_id']].append(record)

            elif list_type == "facility":
                if record['facility_id'] not in facility_data.keys():
                    facility_data[record['facility_id']] = list()

                if 'total_quantities' in record:
                    total_quant = record['total_quantities'].split(",")
                    req_quantity = sum([float(i) for i in total_quant])
                    record['required_quantity'] = int(req_quantity) if (
                                                                           req_quantity.is_integer()) is True else req_quantity

                else:
                    record['required_quantity'] = None

                facility_data[record['facility_id']].append(record)

        response["drug_wise"] = drug_data
        response["patient_wise"] = patient_data
        response["facility_wise"] = facility_data

        return create_response(response)

    except IntegrityError as ex:
        logger.error(ex, exc_info=True)
        raise IntegrityError
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError
    except Exception as e:
        logger.info(e)
        return error(1020)


@validate(required_fields=["facility_distribution_id", "user_id", "company_id"])
def add_all_alternate_drug(info_dict):
    # temporary check
    create_response(True)
    try:
        if not info_dict["facility_distribution_id"] or not info_dict["company_id"] or not info_dict["user_id"]:
            return error(1001, "Missing Parameter(s): facility_distribution_id or company_id or user_id.")
        response = save_alternate_drug_option({
            'facility_distribution_id': info_dict['facility_distribution_id'],
            'company_id': info_dict['company_id'],
            'user_id': info_dict['user_id'],
            'save_alternate_drug_option': True
        })
        return response
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def get_manual_packs(company_id, filter_fields, paginate, sort_fields):
    try:
        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        response = dict()
        clauses = [PackDetails.company_id == company_id]

        if filter_fields and filter_fields.get('patient_name', None) is not None:
            if (filter_fields['patient_name']).isdigit():
                patient_id = int(filter_fields['patient_name'])
                filter_fields['patient_id'] = patient_id
                filter_fields.pop('patient_name')

            elif is_date(filter_fields['patient_name']):
                patient_dob = convert_dob_date_to_sql_date(filter_fields['patient_name'])
                filter_fields['patient_dob'] = patient_dob
                filter_fields.pop('patient_name')

        like_search_list = ['facility_name', 'patient_name', 'patient_dob']
        exact_search_list = ['delivery_date_exact', 'print_requested', 'patient_id']
        between_search_list = ['admin_start_date', 'delivery_date', 'created_date']
        membership_search_list = ['pack_status', 'assigned_to', 'uploaded_by', 'pack_id']
        left_like_search_fields = ['pack_display_id']
        having_search_list = []
        order_list = list()
        defined_orders = list()

        if sort_fields:
            # adding pack status predefined order
            for index, item in enumerate(sort_fields):
                if item[0] == "pack_status":
                    logger.debug("getmanualpacks: got pack_status in sort_fields- before pop: " + str(sort_fields))
                    pack_status_order = sort_fields.pop(index)
                    if pack_status_order[1] == 1:
                        defined_orders.append(SQL('FIELD(pack_status, {},{},{},{},{},{})'
                                                  .format(settings.PARTIALLY_FILLED_BY_ROBOT,
                                                          settings.PROGRESS_PACK_STATUS, settings.MANUAL_PACK_STATUS,
                                                          settings.FILLED_PARTIALLY_STATUS, settings.DONE_PACK_STATUS,
                                                          settings.DELETED_PACK_STATUS)))
                    else:
                        defined_orders.append(SQL('FIELD(pack_status, {},{},{},{},{},{})'
                                                  .format(settings.DELETED_PACK_STATUS, settings.DONE_PACK_STATUS,
                                                          settings.FILLED_PARTIALLY_STATUS,
                                                          settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS,
                                                          settings.PARTIALLY_FILLED_BY_ROBOT)))
                    logger.debug("getmanualpacks: got pack_status in sort_fields- after pop: " + str(sort_fields))
                    break

        # again checking for sort fields as we popped pack_status order
        if sort_fields:
            order_list.extend(sort_fields)

        fields_dict = {
            "facility_name": FacilityMaster.facility_name,
            "facility_id": PatientMaster.facility_id,
            "patient_id": PatientMaster.patient_no,
            "patient_dob": PatientMaster.dob,
            "uploaded_by": FileHeader.created_by,
            "uploaded_date": fn.DATE(FileHeader.created_date),
            "created_date": fn.DATE(PackDetails.created_date),
            "admin_start_date": fn.DATE(PackDetails.consumption_start_date),
            "admin_end_date": fn.DATE(PackDetails.consumption_end_date),
            "delivery_date": fn.DATE(PackHeader.scheduled_delivery_date),
            "delivery_date_exact": fn.DATE(PackHeader.scheduled_delivery_date),
            "pack_status": fn.IF(PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
                                 fn.IF((PackHeader.change_rx_flag.is_null(True) |
                                        (PackHeader.change_rx_flag == False)),
                                       PackDetails.pack_status, settings.PACK_STATUS_CHANGE_RX),
                                 PackDetails.pack_status),
            "patient_name": PatientMaster.concated_patient_name_field(),
            "user_id": PackUserMap.assigned_to,
            "pack_display_id": PackDetails.pack_display_id,
            "status_name": fn.IF(PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
                                 fn.IF((PackHeader.change_rx_flag.is_null(True) |
                                        (PackHeader.change_rx_flag == False)),
                                       CodeMaster.value, constants.EXT_CHANGE_RX_PACKS_DESC),
                                 CodeMaster.value),
            "fill_start_date": PackDetails.fill_start_date,
            "order_no": PackDetails.order_no,
            "company_id": PackDetails.company_id,
            "all_flag": fn.IF(PackUserMap.assigned_to.is_null(True), '0', '1'),
            "assigned_to": fn.IF(PackUserMap.assigned_to.is_null(True), -1, PackUserMap.assigned_to),
            "system_id": PackDetails.system_id,
            "pack_id": PackDetails.id,
            "print_requested": fn.IF(PrintQueue.id.is_null(True), 'No', 'Yes'),
            "filled_date": PackDetails.filled_date,
        }

        global_search = [
            PatientMaster.concated_patient_name_field(),
            FacilityMaster.facility_name,
            PackDetails.pack_display_id,
            PackDetails.pack_status,
            fields_dict['delivery_date'],
            fields_dict['admin_start_date'],
            fields_dict['admin_end_date']
        ]
        if filter_fields and filter_fields.get('global_search', None) is not None:
            multi_search_string = filter_fields['global_search'].split(',')
            clauses = get_multi_search(clauses, multi_search_string, global_search)

        try:
            select_fields = [
                PackDetails.filled_days,
                PackDetails.fill_start_date,
                fields_dict['uploaded_by'].alias('uploaded_by'),
                fields_dict['pack_id'].alias('pack_id'),
                fields_dict['pack_display_id'],
                PackDetails.pack_no,
                FileHeader.created_date.alias('uploaded_date'),
                PackDetails.created_date,
                FileHeader.created_time,
                fn.IF(PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
                      fn.IF((PackHeader.change_rx_flag.is_null(True) | (PackHeader.change_rx_flag == False)),
                            PackDetails.pack_status, settings.PACK_STATUS_CHANGE_RX),
                      PackDetails.pack_status).alias('pack_status'),
                # PackDetails.pack_status.alias('pack_status'),
                PackDetails.system_id,
                fields_dict['admin_start_date'].alias('admin_start_date'),
                fields_dict['admin_end_date'].alias('admin_end_date'),
                PackHeader.patient_id,
                PatientMaster.last_name,
                PatientMaster.first_name,
                fields_dict["patient_id"],
                FacilityMaster.facility_name,
                PatientMaster.facility_id,
                PackDetails.order_no,
                PackDetails.pack_plate_location,
                fn.DATE(PackHeader.scheduled_delivery_date).alias('delivery_date'),
                PackDetails.filled_date,
                PatientMaster.dob,
                fn.IF(PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
                      fn.IF((PackHeader.change_rx_flag.is_null(True) | (PackHeader.change_rx_flag == False)),
                            CodeMaster.value, constants.EXT_CHANGE_RX_PACKS_DESC),
                      CodeMaster.value).alias("value"),
                # CodeMaster.value,
                PackDetails.batch_id,
                BatchMaster.status.alias('batch_status'),
                BatchMaster.name.alias('batch_name'),
                fields_dict['patient_name'].alias('patient_name'),
                PackDetails.fill_time,
                fields_dict['delivery_date_exact'].alias('delivery_date_exact'),
                fields_dict['assigned_to'].alias('assigned_to'),
                fn.IF(PartiallyFilledPack.id.is_null(True), False, True).alias(
                    'filled_partially'),
                fields_dict['print_requested'].alias('print_requested'),
                PackUserMap.modified_by.alias('pack_assigned_by'),
                ExtPackDetails.ext_status_id.alias('ext_pack_status_id'),
                PackStatusTracker.reason.alias('reason')
            ]

            sub_query = ExtPackDetails.select(fn.MAX(ExtPackDetails.id).alias('max_ext_pack_details_id'),
                                              ExtPackDetails.pack_id.alias('pack_id')) \
                .group_by(ExtPackDetails.pack_id).alias('sub_query')

            sub_query_reason = PackStatusTracker.select(fn.MAX(PackStatusTracker.id).alias('max_pack_status_id'),
                                                        PackStatusTracker.pack_id.alias('pack_id')) \
                .group_by(PackStatusTracker.pack_id).alias('sub_query_reason')

            query = PackDetails.select(*select_fields).dicts() \
                .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
                .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
                .join(FileHeader, on=PackHeader.file_id == FileHeader.id) \
                .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
                .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
                .join(PackRxLink, JOIN_LEFT_OUTER, PackRxLink.pack_id == PackDetails.id) \
                .join(PartiallyFilledPack, JOIN_LEFT_OUTER, PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
                .join(PrintQueue, JOIN_LEFT_OUTER, PrintQueue.pack_id == PackDetails.id) \
                .join(sub_query, JOIN_LEFT_OUTER, on=(sub_query.c.pack_id == PackDetails.id)) \
                .join(ExtPackDetails, JOIN_LEFT_OUTER, on=ExtPackDetails.id == sub_query.c.max_ext_pack_details_id) \
                .join(sub_query_reason, JOIN_LEFT_OUTER, on=(sub_query_reason.c.pack_id == PackDetails.id)) \
                .join(PackStatusTracker, JOIN_LEFT_OUTER,
                      on=PackStatusTracker.id == sub_query_reason.c.max_pack_status_id) \
                .group_by(PackDetails.id).order_by(PackDetails.order_no)

            results, count, non_paginate_result = get_results(query.dicts(), fields_dict, filter_fields=filter_fields,
                                                              clauses=clauses,
                                                              sort_fields=order_list,
                                                              paginate=paginate,
                                                              exact_search_list=exact_search_list,
                                                              like_search_list=like_search_list,
                                                              membership_search_list=membership_search_list,
                                                              having_search_list=having_search_list,
                                                              non_paginate_result_field_list=['pack_id', 'facility_id',
                                                                                              'patient_id'],
                                                              between_search_list=between_search_list,
                                                              left_like_search_fields=left_like_search_fields,
                                                              identified_order=defined_orders,
                                                              )

            response['pack_data'] = results
            response['total_packs'] = count
            if 'pack_id' in non_paginate_result.keys():
                response['pack_id_list'] = non_paginate_result['pack_id']
                response['facility_set'] = set(non_paginate_result['facility_id'])
                response['patient_set'] = set(non_paginate_result['patient_id'])
                response['pack_status'] = get_pack_status_by_pack_list(pack_list=non_paginate_result['pack_id'])

                if "from_scan" in filter_fields and len(non_paginate_result['pack_id']) == 1:
                    logger.info("Notification for scan with user_id {}".format(non_paginate_result['pack_id'][0]))
                    Notifications().scan(non_paginate_result['pack_id'][0])
                    response['scan_barcode'] = True

            return create_response(response)

        except IntegrityError as ex:
            logger.error(ex, exc_info=True)
            raise IntegrityError

        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError

    except (IntegrityError, InternalError) as e:
        logger.info(e)
        return error(1000, e)


@log_args_and_response
def get_drug_stock_status(company_id, filter_fields):
    """

    @param args:
    @return:
    """
    results, count, non_paginate_result = PackDetails.get_drug_stock_by_status(company_id, filter_fields)
    response = {"drug_data": results, "total_drugs": count, "drug_id_list": non_paginate_result}
    return create_response(response)


@validate(required_fields=["pack_id"])
def get_altered_drugs_of_pack(args):
    """
    Returns all altered drugs of a pack
    @param args: {"pack_id": int}
    @return: dict
    """
    pack_id = args.get("pack_id")
    try:
        response = PackRxLink.get_altered_drugs(pack_id)

        return create_response(response)

    except (InternalError, IntegrityError, DoesNotExist):
        return error(2001)


@log_args_and_response
@validate(required_fields=["drug_id", "is_in_stock"])
def update_drug_status(args):
    """
    Update Drug status
    @param args: {"drug_id": int, "is_in_stock": int, "user_id": int}
    @return: status

    Examples:
            >>> update_drug_status({"drug_id": 106940, "is_in_stock": 0, "user_id":10})
            "is_in_stock": 0 - to mark drug as out of stock
            "is_in_stock": 1 - to mark drug as  in stock
            "is_in_stock": 2 -  to mark drug as discontinue
    """

    try:
        drug_id = args.get("drug_id")
        is_in_stock = args.get("is_in_stock")
        logger.debug("fetching token")
        token = get_token()
        logger.debug("fetching_user_details")
        user_details = get_current_user(token=token)
        unique_drug_id = None
        with db.atomic():
            query = UniqueDrug.select(UniqueDrug.id).dicts() \
                .join(DrugMaster, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                      (UniqueDrug.txr == DrugMaster.txr))) \
                .where(DrugMaster.id == drug_id)

            for record in query:
                unique_drug_id = record["id"]
                break

            if not unique_drug_id:
                return error(1017)

            status = DrugStockHistory.update(is_active=False).where(
                DrugStockHistory.unique_drug_id == unique_drug_id,
                DrugStockHistory.company_id == user_details["company_id"]).execute()
            logger.debug("Drug Stock History Update Result = {} for Unique Drug ID: {}.".format(status, unique_drug_id))

            DrugStockHistory.insert(**{"unique_drug_id": unique_drug_id, "is_in_stock": is_in_stock, "is_active": True,
                                       "created_by": user_details["id"], "company_id": user_details["company_id"],
                                       "created_date": datetime.datetime.now()}).execute()

        drug = get_drug_status_by_drug_id(drug_id=drug_id, dicts=True)

        # update the unique drug last_seen_by and last_seen_time for DrugDetails
        formatted_ndc_txr_list = list()
        formatted_ndc_txr = str(drug["formatted_ndc"] + '_' + drug["txr"])
        formatted_ndc_txr_list.append(formatted_ndc_txr)
        # get the unique_drug_id for the provided fndc_txr
        unique_drug_id_dict = UniqueDrug.db_get_unique_drug_id(formatted_ndc_txr_list=formatted_ndc_txr_list)
        create_dict = {"unique_drug_id": unique_drug_id_dict[formatted_ndc_txr],
                       "company_id": user_details["company_id"]}
        update_dict = {"last_seen_by": user_details["id"],
                       "last_seen_date": get_current_date_time()}
        # update or creates new record in DrugDetails table
        DrugDetails.db_update_or_create(create_dict=create_dict, update_dict=update_dict)

        drug_name = " ".join((drug["drug_name"], drug["strength_value"], drug["strength"]))
        if is_in_stock == 2:
            Notifications().send_with_username(0, settings.NOTIFICATION_MESSAGE_CODE_DICT["DRUG_DISCONTINUE"].format(
                drug_name, drug["ndc"]), flow='pfw,dp')
        else:
            Notifications().send_with_username(0, settings.NOTIFICATION_MESSAGE_CODE_DICT["DRUG_STOCK_CHANGE"].format(
                drug_name, drug["ndc"], "in stock" if is_in_stock else "out of stock"), flow='pfw,dp')

        return status
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1036)


@log_args_and_response
def update_replenish_based_on_device(device_id):
    try:
        device_data = DeviceMaster.get_device_data(device_id, settings.DEVICE_TYPES['ROBOT'],
                                                   [settings.ROBOT_SYSTEM_VERSIONS['v3']])
        if device_data:
            batch_query = BatchMaster.select(BatchMaster.id, BatchMaster.name).dicts().order_by(
                BatchMaster.id.desc()).where(
                BatchMaster.status == settings.BATCH_IMPORTED, BatchMaster.system_id == device_data["system_id"]).get()
            logger.info("batch_id {}".format(batch_query['id']))
            batch_id = batch_query['id']
            batch_name = batch_query['name']

            if batch_id:
                batch_dict = {
                    "device_id": device_id,
                    "batch_id": batch_id,
                    "batch_name": batch_name,
                    "system_id": device_data["system_id"]
                }
                get_replenish_mini_batch_wise(batch_dict)
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return None
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)
    except ValueError as e:
        return error(2005, str(e))


def update_replenish_based_on_system(system_id):
    try:
        device_data = DeviceMaster.db_get_robots_by_system_id(system_id,
                                                              [settings.ROBOT_SYSTEM_VERSIONS['v3']])
        if device_data:

            batch_data = BatchMaster.select(BatchMaster.id, BatchMaster.name).dicts().order_by(
                BatchMaster.id.desc()).where(
                BatchMaster.status == settings.BATCH_IMPORTED,
                BatchMaster.system_id == device_data[0]['system_id']).get()
            logger.info("batch_id {}".format(batch_data['id']))
            batch_id = batch_data['id']
            batch_name = batch_data['name']

            if batch_id:
                for device in device_data:
                    batch_dict = {
                        "device_id": device['id'],
                        "batch_id": batch_id,
                        "batch_name": batch_name,
                        "system_id": device['system_id']
                    }
                    get_replenish_mini_batch_wise(batch_dict)
    except DoesNotExist as e:
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except ValueError as e:
        raise e


@validate(required_fields=["data", "system_id"])
@log_args_and_response
def populate_slot_transaction(pack_list_info):
    """ Take the webservice response and creates slot record in the slot transaction table.

    Args:
        pack_list_info (dict): The list of dict to be inserted in the SlotTransaction table.

    Returns:
        json response of success or failure

    Examples:
        >>> populate_slot_transaction()
        {}

    """
    system_id = pack_list_info["system_id"]
    data = pack_list_info["data"]

    if not data:  # No data was sent, no action needed
        return create_response(1)

    pack_id = data[0]["pack_id"]
    device_id = pack_list_info["device_id"]

    slot_header_transaction = set()
    existing_slot_header_transaction = set()
    slot_header_list = []
    canister_dropped_quantity = dict()
    slot_transaction_list = []
    mfd_data_list = []
    mfd_canister_location_dict = dict()
    local_inventory_update_data = list()

    valid_pack = PackDetails.db_verify_pack_id_by_system_id(pack_id, system_id)
    if not valid_pack:
        return error(1014)

    pack_data = PackDetails.db_get_pack_info(pack_id)
    if not pack_data:
        return error(1014)

    status_1 = status_2 = status_3 = False
    # info: (for interface) will have comma separated slot header ids for which slots will have issue while filling
    # if pack_list_info["manual_fill_required"] != "":
    #     slot_header_transaction = pack_list_info["manual_fill_required"].split(',')
    #     slot_header_transaction = set(map(int, slot_header_transaction))
    # commenting above code for now to disable manual fill required entry as not getting from Robot
    # todo: add required field when enable above code

    try:
        with db.transaction():
            for record in data:
                location_id, is_disable = LocationMaster.get_location_id_from_display_location(record.pop('device_id'),
                                                                                 record.pop('display_location'))
                record["created_by"] = 1  # todo remove as user is not creating slottransaction
                record['location_id'] = location_id
                if record['canister_id']:
                    if str(record['canister_id']) not in canister_dropped_quantity.keys():
                        canister_dropped_quantity[str(record['canister_id'])] = 0
                    canister_dropped_quantity[str(record['canister_id'])] += record['dropped_qty']
                if not record['mfd_drug']:
                    record.pop('mfd_drug', None)
                    slot_transaction_list.append(record)
                else:
                    if record.get('mfd_analysis_details_id', None):
                        mfd_data_list.extend(record['mfd_analysis_details_id'])
                        mfd_canister_location_dict[record['mfd_analysis_id']] = location_id
            if slot_transaction_list:
                status_1 = BaseModel.db_create_multi_record(
                    slot_transaction_list, SlotTransaction
                )

            # if slot_transaction_list:
            #     populate_drug_tracker(slot_transaction_list)

            if mfd_data_list:
                logger.debug("In slot_transaction_for_pack_id {}, mfd_data_list: {}".format(pack_id, mfd_data_list))
                status_2 = db_update_drug_status(mfd_data_list, constants.MFD_DRUG_DROPPED_STATUS)
                logger.debug("In slot_transaction_for_pack_id {}, mfd_canister_location_dict: {}".
                             format(pack_id, mfd_canister_location_dict))
                status_3 = db_update_canister_data(mfd_canister_location_dict, pack_id, 1)

                update_transfer_wizard(device_id, pack_data['company_id'], system_id,
                                       analysis_ids=list(mfd_canister_location_dict.keys()))

            logger.info("Inventory canister_dropped_quantity {}, {}".format(canister_dropped_quantity, pack_id))
            if len(canister_dropped_quantity):
                inventor_status = update_inventory_v2({"dropped_qty": canister_dropped_quantity})
                logger.info("Inventory update status {}".format(inventor_status))
            status = True
            update_replenish_based_on_device(device_id)

        if len(canister_dropped_quantity):
            # update the local inventory with the dropped qty for the Canister Drugs
            drug_data = db_get_by_id_list(canister_id_list=list(canister_dropped_quantity.keys()))
            for drug in drug_data:
                temp_dict = {"ndc": drug["ndc"],
                             "formatted_ndc": drug["formatted_ndc"],
                             "txr": drug["txr"],
                             "quantity": canister_dropped_quantity[str(drug["canister_id"])]}
                local_inventory_update_data.append(temp_dict.copy())

            update_local_inventory_by_slot_transaction(pack_id=pack_id, drop_data=local_inventory_update_data)

    except StopIteration:
        return error(2001)
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)
    except ValueError as e:
        return error(2005, str(e))
    return create_response(status)


@log_args
def get_pack_count_for_auto_pilot(dict_batch_info: dict) -> dict:
    """
     This function calculates the pack count for auto pilot
    """
    logger.debug("In get_pack_count_for_auto_pilot")

    system_id = dict_batch_info.get("system_id", None)
    automatic_pack_list = list()
    pending_pack_list = list()
    progress_pack_list = list()
    pending_pack_count = int()
    progress_pack_count = int()

    try:
        batch_id = get_progress_batch_id(system_id=system_id)
        if not batch_id:
            logger.info("No batch for the system")
            return create_response({"pack_count": 0, "pending_pack_count": 0, "progress_pack_count": 0})
        # Query to fetch the pack analysis details for the given batch
        query = PackAnalysisDetails.select(PackDetails.id.alias("pack_id"),
                                           PackDetails.car_id,
                                           PackDetails.pack_status,
                                           (fn.COUNT(Clause(SQL('DISTINCT'),
                                                            fn.IF((PackAnalysisDetails.device_id.is_null(
                                                                True) | PackAnalysisDetails.canister_id.is_null(True)
                                                                   | PackAnalysisDetails.location_number.is_null(True)),
                                                                  True,
                                                                  None)))).alias("is_manual"),
                                           ).dicts() \
            .join(PackAnalysis, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
            .where((BatchMaster.id == batch_id),
                   (PackDetails.pack_status << [settings.PACK_STATUS['Pending'], settings.PACK_STATUS['Progress']])) \
            .group_by(PackDetails.id)
        logger.debug(query)
        # updates the list with the manual packs
        for record in query:
            if record["pack_id"] not in automatic_pack_list:
                if record["is_manual"] != 1:
                    if record["pack_status"] == settings.PACK_STATUS['Pending']:
                        automatic_pack_list.append(record["pack_id"])
                        pending_pack_list.append(record["pack_id"])
                    if record["pack_status"] == settings.PACK_STATUS['Progress'] and record['car_id'] is None:
                        automatic_pack_list.append(record["pack_id"])
                        progress_pack_list.append(record["pack_id"])
        # fetch the mfd packs whose canisters are not present in robot
        mfd_packs = get_mfd_automatic_packs(batch_id=batch_id)

        # combine the mfd as well as manual packs
        final_deduction_list = set(automatic_pack_list) - set(mfd_packs)
        for pack in final_deduction_list:
            if pack in pending_pack_list:
                pending_pack_count += 1
            if pack in progress_pack_list:
                progress_pack_count += 1

        response_dict = {"pack_count": len(final_deduction_list),
                         "pending_pack_count": pending_pack_count,
                         "progress_pack_count": progress_pack_count}
        return create_response(response_dict)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        return e


@log_args
def validate_robot_partially_filled_pack(dict_batch_info: dict) -> dict:
    """
     This function calculates the pack count for auto pilot
    """
    logger.debug("In get_pack_count_for_auto_pilot")

    company_id = dict_batch_info["company_id"]
    pack_display_ids = dict_batch_info["pack_display_ids"]
    user_id = dict_batch_info["user_id"]

    try:
        pack_info = PackUserMap.select().dicts() \
            .join(PackDetails, on=PackDetails.id == PackUserMap.pack_id) \
            .where(PackUserMap.assigned_to == user_id,
                   PackDetails.pack_display_id << pack_display_ids,
                   PackDetails.pack_status == settings.PARTIALLY_FILLED_BY_ROBOT,
                   PackDetails.company_id == company_id)
        valid_pack_ids = set()
        for record in pack_info:
            valid_pack_ids.add(record['pack_display_id'])
        if len(valid_pack_ids) == len(pack_display_ids):
            return create_response(True)
        return create_response(False)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        return e


@log_args_and_response
def _update_alternate_drug_for_batch_manual_canister(update_drug_dict):
    # update patient_rx, IPS
    try:
        drug_id = update_drug_dict['drug_id']
        alt_drug_id = update_drug_dict['alt_drug_id']
        batch_id = update_drug_dict.get('batch_id', None)
        current_pack_id = update_drug_dict['current_pack_id']
        # robot_id = update_drug_dict['robot_id']
        user_id = update_drug_dict['user_id']
        company_id = update_drug_dict['company_id']
        alternate_drug = get_drug_status_by_drug_id(alt_drug_id, dicts=True)
        current_drug = get_drug_status_by_drug_id(drug_id, dicts=True)
        valid_alternate_drug = current_drug and alternate_drug \
                               and current_drug['formatted_ndc'] != alternate_drug['formatted_ndc'] \
                               and current_drug['txr'] == alternate_drug['txr'] \
                               and str(current_drug['brand_flag']) == \
                               str(alternate_drug['brand_flag']) == settings.GENERIC_FLAG
        if not valid_alternate_drug:
            raise ValueError(' drug_id and alt_drug_id are not alternate drugs')

        old_drug_ids = [item.id for item in DrugMaster.get_drugs_by_formatted_ndc_txr(
            current_drug['formatted_ndc'],
            current_drug['txr']
        )]
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise

    # drug_id = current_drug['drug_id']
    alt_drug_id = alternate_drug['id']
    analysis_data = PackDetails.select(PackDetails,
                                       SlotDetails.id.alias('slot_id'),
                                       PackAnalysisDetails,
                                       PackAnalysis).dicts() \
        .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
                                (PackAnalysis.batch_id == PackDetails.batch_id))) \
        .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
        .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
        .where(PackDetails.id == current_pack_id,
               SlotDetails.drug_id == drug_id)
    # PackDetails.pack_status << [settings.PENDING_PACK_STATUS])

    only_current_pack_update = True
    # for data in analysis_data:
    #     if batch_id is None:
    #         batch_id = data['batch_id']
    #
    #     if data['device_id'] is not None and data['canister_id'] is not None:
    #         only_current_pack_update = True
    if batch_id is None:
        batch_id = PackDetails.db_get_batch_id_from_packs([int(current_pack_id)])

    # clauses = [PackDetails.batch_id == batch_id,
    #            PatientRx.daw_code == 0]
    # # if only_current_pack_update:
    # #     clauses.append((PackDetails.id == current_pack_id))
    # # else:
    # clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]))

    pending_packs = PackDetails.select(PackDetails.id).distinct() \
        .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
        .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
        .where(((PackDetails.batch_id == batch_id) & (PatientRx.daw_code == 0) &
                ((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]) |
                 (PackDetails.id == current_pack_id))))
    print(list(pending_packs))
    packs_clauses = list()
    packs_clauses.append((SlotDetails.drug_id << old_drug_ids))
    if not only_current_pack_update:
        packs_clauses.append(
            (PackAnalysisDetails.device_id.is_null(True) or PackAnalysisDetails.canister_id.is_null(True)))
        # packs_clauses.append(())
        packs_clauses.append((PackAnalysis.pack_id << pending_packs))
    else:
        packs_clauses.append((PackAnalysis.pack_id == current_pack_id))
    packs_to_update = PackAnalysis.select(PackAnalysis.pack_id,
                                          SlotDetails.id.alias('slot_id'),
                                          PackAnalysis.id.alias('analysis_id')) \
        .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
        .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
        .where(functools.reduce(operator.and_, packs_clauses))
    print(packs_to_update)
    try:
        analysis_ids = list()
        pack_ids = list()
        drug_list = list()
        alt_drug_list = list()
        slot_ids = list()
        for record in packs_to_update.dicts():
            pack_ids.append(record['pack_id'])
            analysis_ids.append(record['analysis_id'])
            slot_ids.append(record['slot_id'])
        print(pack_ids)
        if not pack_ids or not old_drug_ids:
            # as no packs needs update, so returning True as no action required
            return create_response(False)
        query = PackRxLink.select(PackRxLink.pack_id,
                                  SlotDetails.drug_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .where(PackRxLink.pack_id << pack_ids,
                   SlotDetails.drug_id << old_drug_ids)
        pack_list = list()
        for record in query.dicts():
            pack_list.append(record['pack_id'])
            if record['drug_id'] not in drug_list:
                drug_list.append(record['drug_id'])
                alt_drug_list.append(alt_drug_id)
        with db.transaction():
            update_dict = {
                'canister_id': None,
                'device_id': None,
            }
            if analysis_ids and old_drug_ids:

                # ReservedCanister.delete().where(ReservedCanister.canister_id == canister_id).execute()
                response = alternate_drug_update({
                    'pack_list': ','.join(map(str, pack_list)),
                    'olddruglist': ','.join(map(str, drug_list)),
                    'newdruglist': ','.join(map(str, alt_drug_list)),
                    'user_id': user_id,
                    'company_id': company_id,
                    'module_id': constants.PDT_MVS_MANUAL_FILL
                })
                response = json.loads(response)
                if response['status'] != 'success':
                    # throwing exception to rollback changes as we could not update IPS
                    # raise AlternateDrugUpdateException(response['code'])
                    return error(response['code'])
                PackAnalysisDetails.update(**update_dict) \
                    .where(PackAnalysisDetails.analysis_id << analysis_ids,
                           PackAnalysisDetails.slot_id << slot_ids) \
                    .execute()
                BatchChangeTracker.db_save(
                    batch_id,
                    user_id,
                    action_id=ActionMaster.ACTION_ID_MAP[ActionMaster.UPDATE_ALT_DRUG],
                    params={
                        "alt_drug_id": alt_drug_id,
                        "batch_id": batch_id,
                        "current_pack_id": current_pack_id,
                        "user_id": user_id,
                        "changed_from_mvs": True
                    },
                    packs_affected=pack_list
                )
                logger.info("Inside pack.py / _update_alternate_drug_for_batch_manual_canister, pack updated {}".format(
                    pack_list))
                return create_response(pack_list)
            else:
                return create_response(False)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_mfd_drug_list_(batch_id, mfs_device_id):
    try:
        analysis_ids: list = list()
        query1 = TempMfdFilling.select(TempMfdFilling.mfd_analysis_id).dicts().where(
            TempMfdFilling.batch_id == batch_id, TempMfdFilling.mfs_device_id == mfs_device_id)
        for record in query1:
            if record['mfd_analysis_id']:
                analysis_ids.append(record['mfd_analysis_id'])
        logger.info("In get_mfd_drug_list_ {} ".format(analysis_ids))
        logger.info("In get_mfd_drug_list_ {} ".format(query1))

        query = DrugMaster.select(DrugMaster.id, DrugMaster.ndc, DrugMaster.formatted_ndc, DrugMaster.txr,
                                  DrugMaster.brand_flag, PatientRx.daw_code).dicts() \
            .join(SlotDetails, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id).where(
            MfdAnalysis.id << analysis_ids).group_by(DrugMaster.id)
        return query
    except DataError as e:
        logger.error(e)
        return e


@log_args_and_response
def get_slots_to_update_pack_wise(pack_ids, old_drug):
    try:
        query = SlotDetails.select(
            SlotDetails.id,
            SlotDetails.drug_id,
            PackRxLink.pack_id).dicts() \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .where((PackRxLink.pack_id << pack_ids),
                   (SlotDetails.drug_id == old_drug))

        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_packs_to_update_drug_mff(user_id):
    pack_id_list: list = list()
    try:
        query = PackDetails.select(PackDetails.id).dicts() \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .where(
            (PackDetails.pack_status << [settings.MANUAL_PACK_STATUS, settings.PROGRESS_PACK_STATUS,
                                         settings.FILLED_PARTIALLY_STATUS, settings.PARTIALLY_FILLED_BY_ROBOT]), (
                    PackUserMap.assigned_to == user_id))

        for record in query:
            pack_id_list.append(record['id'])
        return pack_id_list
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_slots_to_update_mfs(batch_id, user_id, old_drug, mfs_device_id):
    """
        returns query to get the slot info for the specified ndc to update drug for that use
        @param batch_id:
        @param user_id:
        @param mfs_device_id:
        @param old_drug:
        """
    try:
        analysis_id_query = MfdAnalysis.select(SlotDetails.id, SlotDetails.drug_id,
                                               PackRxLink.pack_id).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.pack_id == PackDetails.id) \
            .where(SlotDetails.drug_id == old_drug,
                   MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.assigned_to == user_id,
                   # MfdAnalysisDetails.status_id == constants.MFD_DRUG_PENDING_STATUS,
                   MfdAnalysis.status_id << [constants.MFD_CANISTER_PENDING_STATUS,
                                             constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                             constants.MFD_CANISTER_SKIPPED_STATUS],
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                   SlotTransaction.id.is_null(True),
                   MfdAnalysis.mfs_device_id == mfs_device_id)
        return analysis_id_query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_same_fndc_drug_by_module(company_id, user_id, batch_id, new_drug, old_drug, module, pack_ids=None,
                                    mfs_device_id=None):
    """
    Update Drug ids in slot detalis for same fndc_txr
    @param company_id:
    @param user_id:
    @param batch_id:
    @param new_drug:
    @param old_drug:
    @param module:
    @param pack_ids:
    @param mfs_device_id:
    @return: True or packs affected
    """

    slot_details_updation: dict = dict()
    pack_drug_tracker_details: list = list()
    pack_id_list: list = list()

    try:
        if module == constants.PDT_MVS_MANUAL_FILL:
            with db.transaction():

                slot_data = get_slots_to_update_pack_wise(pack_ids, old_drug)
                for record in slot_data:
                    slot_details_updation[record["id"]] = {"prev_drug_id": record["drug_id"],
                                                           "drug_id": new_drug}

                    pack_drug_tracker_info = {"slot_details_id": record["id"], "previous_drug_id": record["drug_id"],
                                              "updated_drug_id": new_drug,
                                              "module": constants.PDT_MVS_MANUAL_FILL,
                                              "created_by": user_id, "created_date": get_current_date_time()}

                    pack_drug_tracker_details.append(pack_drug_tracker_info)
                logger.info("In update_same_fndc_drug_by_module - MVS - slots data going to update {}".format(
                    pack_drug_tracker_info))
                for slot_details_id, slot_drugs in slot_details_updation.items():
                    drug_id = slot_drugs["drug_id"]
                    prev_drug_id = slot_drugs["prev_drug_id"]
                    logger.info("In update_same_fndc_drug_by_module -- updating Drug id in slot details {}".format(
                        slot_details_id))

                    slot_details_update_status = SlotDetails.update(
                        drug_id=drug_id
                    ).where(SlotDetails.id == slot_details_id).execute()

                populate_pack_drug_tracker(pack_drug_tracker_details)
                logger.info("Drug Id updated successfully")
                pack_ids = list(set(pack_ids))
                return pack_ids

        elif module == constants.PDT_PACK_FILL_WORKFLOW:

            pack_id_list = get_packs_to_update_drug_mff(user_id)
            slot_data = get_slots_to_update_pack_wise(pack_id_list, old_drug)
            with db.transaction():
                for record in slot_data:
                    slot_details_updation[record["id"]] = {"prev_drug_id": record["drug_id"],
                                                           "drug_id": new_drug}

                    pack_drug_tracker_info = {"slot_details_id": record["id"], "previous_drug_id": record["drug_id"],
                                              "updated_drug_id": new_drug,
                                              "module": constants.PDT_PACK_FILL_WORKFLOW,
                                              "created_by": user_id, "created_date": get_current_date_time()}

                    pack_drug_tracker_details.append(pack_drug_tracker_info)
                    logger.info("In update_same_fndc_drug_by_module - MFF - slots data going to update {}".format(
                        pack_drug_tracker_info))

                for slot_details_id, slot_drugs in slot_details_updation.items():
                    drug_id = slot_drugs["drug_id"]
                    prev_drug_id = slot_drugs["prev_drug_id"]
                    logger.info("In update_same_fndc_drug_by_module -- updating Drug id in slot details {}".format(
                        slot_details_id))

                    slot_details_update_status = SlotDetails.update(
                        drug_id=drug_id
                    ).where(SlotDetails.id == slot_details_id).execute()

                populate_pack_drug_tracker(pack_drug_tracker_details)
                logger.info("Drug Id updated successfully")
                pack_id_list = list(set(pack_id_list))
                return pack_id_list

        elif module == constants.PDT_MFD_ALTERNATE:
            slot_data = get_slots_to_update_mfs(batch_id, user_id, old_drug, mfs_device_id)
            with db.transaction():
                for record in slot_data:
                    logger.info(record)
                    pack_id_list.append(record['pack_id'])

                    slot_details_updation[record["id"]] = {"prev_drug_id": record["drug_id"],
                                                           "drug_id": new_drug}

                    pack_drug_tracker_info = {"slot_details_id": record["id"], "previous_drug_id": record["drug_id"],
                                              "updated_drug_id": new_drug,
                                              "module": constants.PDT_MFD_ALTERNATE,
                                              "created_by": user_id, "created_date": get_current_date_time()}

                    pack_drug_tracker_details.append(pack_drug_tracker_info)
                    logger.info("In update_same_fndc_drug_by_module - MFD - slots data going to update {}".format(
                        pack_drug_tracker_info))

                for slot_details_id, slot_drugs in slot_details_updation.items():
                    drug_id = slot_drugs["drug_id"]
                    prev_drug_id = slot_drugs["prev_drug_id"]
                    logger.info("In update_same_fndc_drug_by_module -- updating Drug id in slot details {}".format(
                        slot_details_id))

                    slot_details_update_status = SlotDetails.update(
                        drug_id=drug_id
                    ).where(SlotDetails.id == slot_details_id).execute()

                populate_pack_drug_tracker(pack_drug_tracker_details)
                logger.info("Drug Id updated successfully")
                pack_id_list = list(set(pack_id_list))
                return pack_id_list
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)


@log_args_and_response
def update_alternate_drug_by_module(company_id, user_id, batch_id, new_drug, old_drug, module, pack_ids=None):
    """
    Update Drug Id in slot details for alternate drugs
    @param company_id:
    @param user_id:
    @param batch_id:
    @param new_drug:
    @param old_drug:
    @param module:
    @param pack_ids:
    @return: True or Packs Affected
    """
    data_dict: dict = dict()
    logger.info("In update_alternate_drug_by_module")
    try:
        if module == constants.PDT_MVS_MANUAL_FILL:

            data_dict = {
                'company_id': company_id,
                'alt_drug_id': new_drug,
                'drug_id': old_drug,
                'batch_id': batch_id,
                'current_pack_id': pack_ids,
                'user_id': user_id,
                'module': module
            }
            response = _update_alternate_drug_for_batch_manual_canister(data_dict)
            response = json.loads(response)
            print(response)
            if response['status'] == "success":

                if not response['data']:
                    return False
                logger.info("Alternate Drug updated Successfully")
                return response

            if response['status'] == "failure":
                return False

        elif module == constants.PDT_PACK_FILL_WORKFLOW:
            data_dict = {
                "olddruglist": str(old_drug),
                "newdruglist": str(new_drug),
                "company_id": company_id,
                "assigned_user_id": user_id,
                "user_id": user_id,
                "module": module

            }
            response = alternate_drug_update_manual_packs(data_dict)
            response = json.loads(response)
            if response['status'] == "success":
                logger.info("Alternate Drug updated Successfully")
                return response

            if response['status'] == "failure":
                return False

        elif module == constants.PDT_MFD_ALTERNATE:
            old_ndc = (DrugMaster.get(id=old_drug)).ndc
            new_ndc = (DrugMaster.get(id=new_drug)).ndc
            data_dict = {
                "batch_id": str(batch_id),
                "old_ndc": str(old_ndc),
                "new_ndc": new_ndc,
                "user_id": user_id,
                "company_id": company_id

            }
            response = update_mfd_alternate_drug(data_dict)
            response = json.loads(response)
            if response['status'] == "success":
                logger.info("Alternate Drug updated Successfully")
                return response

            if response['status'] == "failure":
                return False
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)


@log_args_and_response
def get_drug_info_based_on_ndc(ndc):
    try:
        query = DrugMaster.select(DrugMaster.id, DrugMaster.ndc, DrugMaster.formatted_ndc, DrugMaster.txr,
                                  DrugMaster.brand_flag, DrugStatus.ext_status, DrugMaster.drug_name).dicts().join(
            DrugStatus, on=DrugMaster.id == DrugStatus.drug_id) \
            .where(DrugMaster.ndc == ndc)
        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return False
    except Exception as e:
        logger.error(e)
        return False


@validate(required_fields=["company_id", "user_id", "ndc", "module"])
@log_args_and_response
def validate_scanned_drug(scanned_data):
    """
    Validated scanned drug bottle to update drugs in packs
    @param scanned_data:
    @return:
    """
    # todo : do proper spacing, comments and loggers
    company_id = scanned_data['company_id']
    user_id = scanned_data['user_id']
    batch_id = scanned_data.get('batch_id', None)
    scanned_ndc = (scanned_data['ndc'])
    pack_ids = scanned_data.get('pack_ids', None)
    confirmation = scanned_data.get('confirmation', False)
    module = scanned_data['module']
    mfs_device_id = scanned_data.get('mfs_device_id', None)
    # filled_ndc_list = scanned_data.get('filled_ndc', None)
    mfs_filled_drug = scanned_data.get('mfs_filled_drug', None)
    mfs_filled_drug_list: list = list()

    response_data: dict = dict()
    new_ndc: str = str()
    old_ndc: str = str()
    ndc_updated: bool = False
    drug_type: int = int()
    new_drug_info: dict = dict()
    additional_info: dict = dict()
    pack_drugs: dict = dict()
    db_update: dict = dict()
    scanned_fndc: str = str()
    scanned_txr: str = str()
    scanned_drug_id: str = str()
    scanned_drug_brand: str = str()



    scanned_drug = get_drug_info_based_on_ndc(scanned_ndc)
    if not scanned_drug:
        return error(9021)
    for data in scanned_drug:
        if data['ext_status'] == settings.INVALID_EXT_STATUS:
            return error(9024)
        scanned_fndc = data['formatted_ndc']
        scanned_txr = data['txr']
        scanned_drug_id = data['id']
        scanned_drug_brand = data['brand_flag']

    if not pack_ids:
        if not mfs_device_id:
            return error(9018)

    # if filled_ndc_list:
    #     if scanned_ndc in filled_ndc_list:
    #         return error(9025)

    if mfs_filled_drug:
        for i in mfs_filled_drug:
            temp = get_drug_info_based_on_ndc(i)
            logger.info(temp)
            for record in temp:
                if scanned_ndc == record['ndc'] or (
                        scanned_fndc == record['formatted_ndc'] and scanned_txr == record['txr']) or scanned_txr == record['txr']:
                    return error(9025)

    if not batch_id:
        batch_id, system_id = get_batch_id_from_pack_list(pack_ids)

    #  create 3 list: list1 will contain all ndc that are in packs (drug type 1)
    #  list2 will contain all the alternate NDC's fetched from db for given NDC's present in packs (drug type 2)
    #  list 3 will contain all the alternate drug NDC's fetched from db for given NDC's present in packs (drug type 3)
    #  then check the ndc in input with all the list and find drug type

    logger.info("Scanned Drug Data {}".format(scanned_drug))
    if pack_ids:
        pack_drugs = db_get_pack_wise_drug_data_dao(pack_ids)
    if mfs_device_id:
        pack_drugs = get_mfd_drug_list_(batch_id, mfs_device_id)
    try:
        if pack_drugs:
            for data in pack_drugs:
                logger.info("Pack Drug consideration {}".format(data))
                if scanned_ndc == data['ndc']:
                    drug_type = constants.SAME_NDC
                    new_ndc = scanned_ndc
                    old_ndc = scanned_ndc
                    ndc_updated = False
                    break
                elif scanned_fndc == data['formatted_ndc'] and scanned_txr == data['txr']:
                    logger.info("Different packaging code found {}".format(data))

                    new_ndc = scanned_ndc
                    old_ndc = data['ndc']
                    new_drug = scanned_drug_id
                    old_drug = data['id']
                    drug_type = constants.SAME_DRUG

                    db_update = update_same_fndc_drug_by_module(company_id=company_id, user_id=user_id,
                                                                batch_id=batch_id, new_drug=new_drug, old_drug=old_drug,
                                                                module=module, pack_ids=pack_ids,
                                                                mfs_device_id=mfs_device_id)
                    if db_update:
                        ndc_updated = True
                        new_drug_info = fetch_drug_info(new_drug,company_id)[0]
                        additional_info = {
                            "updated_pack_display_ids": db_update
                        }
                    break

                elif scanned_txr and data['txr']:
                    if str(scanned_txr) == data['txr']:
                        logger.info("Alternate drug scan found")
                        if scanned_drug_brand == settings.BRAND_FLAG:
                            return error(9023)
                        if data['brand_flag'] == settings.BRAND_FLAG:
                            return error(9026)

                        if data['brand_flag'] != settings.GENERIC_FLAG or scanned_drug_brand != settings.GENERIC_FLAG:
                            return error(9023)
                        if data['daw_code'] == 1:
                            return error(9022)
                        drug_type = constants.ALTERNATE_DRUG
                        new_drug = scanned_drug_id

                        old_drug = data['id']
                        old_ndc = data['ndc']
                        new_drug_info = fetch_drug_info(new_drug,company_id)[0]
                        new_ndc = scanned_ndc
                        if confirmation:
                            if pack_ids:
                                db_update = update_alternate_drug_by_module(company_id=company_id, user_id=user_id,
                                                                            batch_id=batch_id, new_drug=new_drug,
                                                                            old_drug=old_drug,
                                                                            module=module, pack_ids=pack_ids)
                            if mfs_device_id:
                                db_update = update_alternate_drug_by_module(company_id=company_id, user_id=user_id,
                                                                            batch_id=batch_id, new_drug=new_drug,
                                                                            old_drug=old_drug,
                                                                            module=module)
                            if db_update:
                                ndc_updated = True
                                additional_info = db_update

                        break

        if drug_type == constants.SAME_NDC:
            response_data = {'drug_type': drug_type,
                             'old_ndc': old_ndc,
                             'new_ndc': new_ndc,
                             'ndc_updated': ndc_updated,
                             'new_drug_info': new_drug_info,
                             'additional_info': additional_info
                             }
        elif drug_type == constants.SAME_DRUG:
            response_data = {'drug_type': drug_type,
                             'old_ndc': old_ndc,
                             'new_ndc': new_ndc,
                             'ndc_updated': ndc_updated,
                             'new_drug_info': new_drug_info,
                             'additional_info': additional_info
                             }
        elif drug_type == constants.ALTERNATE_DRUG:
            if not confirmation:
                response_data = {'drug_type': drug_type,
                                 'old_ndc': old_ndc,
                                 'new_ndc': new_ndc,
                                 'ndc_updated': ndc_updated,
                                 'new_drug_info': new_drug_info,
                                 'additional_info': additional_info
                                 }
            if confirmation:
                response_data = {'drug_type': drug_type,
                                 'old_ndc': old_ndc,
                                 'new_ndc': new_ndc,
                                 'ndc_updated': ndc_updated,
                                 'new_drug_info': new_drug_info,
                                 'additional_info': additional_info
                                 }
        else:
            return error(9021)
        return create_response(response_data)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)


def get_pending_packs_with_past_delivery_date(company_id: int, time_zone: str) -> str:
    """
    Sends the email for the pending packs with past delivery dates for the given company_id.
    """
    try:
        result_list = list()
        user_ids = set()
        current_date: str = get_current_day_date_end_date_by_timezone(time_zone=time_zone)[0]
        query1 = PackDetails.select(PackDetails.pack_display_id,
                                    PackDetails.consumption_start_date,
                                    PackDetails.consumption_end_date,
                                    PackHeader.scheduled_delivery_date,
                                    fn.Concat(PatientMaster.last_name, ', ',
                                              PatientMaster.first_name).alias("patient_name"),
                                    FacilityMaster.facility_name).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.company_id == company_id, PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                   PackHeader.scheduled_delivery_date < current_date) \
            .order_by(PackHeader.scheduled_delivery_date)

        for auto_pack in query1:
            result_dict = {"pack_id": auto_pack["pack_display_id"],
                           "admin_start_date": str(auto_pack["consumption_start_date"]),
                           "admin_end_date": str(auto_pack["consumption_end_date"]),
                           "delivery_date": str(auto_pack["scheduled_delivery_date"]),
                           "pack_type": "Robot",
                           "assigned_to": 0,
                           "patient_name": auto_pack["patient_name"],
                           "facility_name": auto_pack["facility_name"]}
            result_list.append(result_dict.copy())

        query2 = PackDetails.select(PackDetails.pack_display_id,
                                    PackDetails.consumption_start_date,
                                    PackDetails.consumption_end_date,
                                    PackHeader.scheduled_delivery_date,
                                    fn.IF(PackUserMap.assigned_to.is_null(True), 0, PackUserMap.assigned_to).alias(
                                        "assigned_to"),
                                    fn.Concat(PatientMaster.last_name, ', ',
                                              PatientMaster.first_name).alias("patient_name"),
                                    FacilityMaster.facility_name).dicts() \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.company_id == company_id, PackDetails.pack_status == settings.MANUAL_PACK_STATUS,
                   PackHeader.scheduled_delivery_date < current_date) \
            .order_by(PackHeader.scheduled_delivery_date)

        for manual_pack in query2:
            result_dict = {"pack_id": manual_pack["pack_display_id"],
                           "admin_start_date": str(manual_pack["consumption_start_date"]),
                           "admin_end_date": str(manual_pack["consumption_end_date"]),
                           "delivery_date": str(manual_pack["scheduled_delivery_date"]),
                           "pack_type": "Manual",
                           "assigned_to": manual_pack["assigned_to"],
                           "patient_name": manual_pack["patient_name"],
                           "facility_name": manual_pack["facility_name"]}
            user_ids.add(manual_pack["assigned_to"])
            result_list.append(result_dict.copy())

        if len(result_list) > 0:
            send_email_for_pending_packs_with_past_delivery_date(company_id=company_id, pending_packs_data=result_list,
                                                                 user_ids=list(user_ids))

        return create_response(settings.SUCCESS_RESPONSE)

    except UnknownTimeZoneError as e:
        logger.error(e, exc_info=True)
        return error(20011, e)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)


def main():
    from dosepack.base_model.base_model import db
    db.init("dosepack_new", user="root".encode("utf-8"), password="root".encode("utf-8"))
    db.connect()
    arg = {"pack_id": 30}
    get_slot_details(arg)


if __name__ == "__main__":
    # execute only if run as a script
    main()
