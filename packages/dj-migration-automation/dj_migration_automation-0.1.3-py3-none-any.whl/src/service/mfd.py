import json
from collections import defaultdict, OrderedDict
from copy import deepcopy
from datetime import datetime
from itertools import cycle
from typing import List, Any, Dict, Optional
from uuid import uuid1, uuid4

import couchdb
from peewee import (InternalError, DoesNotExist, IntegrityError, DataError)

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import (error, create_response, datetime_handler)
from dosepack.local.lang_us_en import err
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, log_args, get_datetime
from dosepack.validation.validate import (validate)
from src.constants import MFD_CANISTER_PENDING_STATUS, MFD_DRUG_PENDING_STATUS
from src.dao.drug_dao import get_drug_data_by_ndc_dao, get_drugs_by_formatted_ndc_txr_dao
from realtime_db.dp_realtimedb_interface import Database
from src import constants
from src.dao.alternate_drug_dao import alternate_drug_update
from src.dao.batch_dao import get_system_id_from_batch_id, db_update_mfd_status, get_progress_batch_id, \
    get_top_batch_id, db_update_mfd_skip
from src.dao.device_manager_dao import (get_location_data_from_device_ids,
                                        get_currently_used_trolley,
                                        get_available_device_list_of_a_type, get_mfs_data_by_system_id,
                                        set_location_disable_dao, db_get_device_name_by_device_id,
                                        get_mfs_systems, set_location_enable_dao,
                                        get_previous_used_mfd_trolley, get_mfd_drawer_quad_capacity_count,
                                        get_associated_mfs_stations, get_active_mfs_id_by_company_id, db_get_mfs_data,
                                        validate_device_id_dao, get_device_data_by_device_id_dao,
                                        get_system_id_by_device_id_dao, get_device_name_from_device,
                                        get_system_id_based_on_device_type)
from src.dao.mfd_canister_dao import (get_device_id_from_serial_number,
                                      get_drawer_canister_data_query,
                                      get_drawer_id_from_serial_number, mfd_misplaced_canister_dao,
                                      check_in_robot,
                                      get_max_order_number_from_mfd_analysis, db_get_mfd_analysis_details_ids,
                                      update_mfd_canister_location,
                                      check_module_update, db_update_canister_active_status,
                                      fetch_empty_trolley_locations_for_rts_canisters, mark_mfd_canister_misplaced,
                                      get_mfd_canister_data_by_analysis_ids, get_mfd_canister_data_by_ids,
                                      db_delete_mfd_analysis_by_analysis_ids, db_get_next_trolley,
                                      get_trolley_analysis_ids, db_get_rts_required_canisters,
                                      mark_mfd_canister_deactivate_status_update, db_get_last_mfd_sequence_for_batch,
                                      db_get_batch_id_from_analysis_ids, db_get_last_mfd_progress_sequence_for_batch)
from src.dao.mfd_dao import (db_get_batch_ids, db_get_mfd_batch_info, db_get_batch_drugs,
                             db_get_drug_analysis_query, db_skip_drug,
                             db_get_min_batch, db_get_canister_data, db_get_analysis_ids_drug, db_update_drug_status,
                             get_similar_canister_analysis_ids,
                             db_get_trolley_first_pack, get_similar_drawer_analysis_ids,
                             map_mfs_location, update_in_progress_canister, db_get_patient_info,
                             db_get_location_info, get_trolley_pending_analysis_ids, db_get_first_trolley_id,
                             get_required_mfd_canister_data, populate_mfd_trolley_data, get_batch_data,
                             get_pack_id_query,
                             db_get_filled_drug_analysis_ids, get_transfer_data, location_mfd_can_info,
                             db_get_canisters_status_based, mfd_transfer_notification_for_batch,
                             get_mfs_transfer_drawer_data, db_get_analysis_details_ids, db_get_current_user_assignment,
                             db_update_current_user_assignment, get_recommendation_pending_data,
                             update_trolley_location, get_next_mfd_transfer_batch, update_transferred_location,
                             get_mfd_canister_batch_id_for_transfers, check_trolley_reuse_required,
                             update_batch_data,
                             db_add_current_filling_data, get_max_order_number, mfd_data_by_order_no,
                             get_pack_mfd_canisters, get_empty_locations,
                             current_mfs_placed_canisters,
                             db_get_filling_pending_analysis_ids, update_dest_location_for_current_mfd_canister,
                             mfd_remove_current_canister_data, db_get_pending_canister_count,
                             db_get_user_pending_canister_count, current_mfs_canisters, update_temp_mfs_data,
                             db_update_canister_status, get_mfd_analysis_ids_for_skip, associate_canister_with_analysis,
                             db_get_skipped_analysis_ids, db_get_rts_analysis_ids, db_get_batch_drugs_by_trolley,
                             db_get_trolley_by_batch, update_mfs_data_in_couch_db,
                             update_mfd_transfer_couch_db, get_filled_drug, update_couch_db_current_mfs,
                             update_couch_db_mfd_canister_master, update_couch_db_mfd_canister_transfer,
                             get_robot_system_info, db_get_mfs_info, db_check_entire_mfd_trolley_skipped,
                             get_trolley_seq_fill_status, get_trolley_data, get_device_id_list_from_trolley_data,
                             update_mfd_couch_db_notification, update_drug_tracker_from_mfd_analysis_details_ids,
                             check_user_in_progress_batch, populate_mfd_analysis_details_status,
                             populate_mfd_analysis_trolley, db_get_mfd_pending_sequence_for_batch,
                             update_mfd_couch_db_notification, update_drug_tracker_from_mfd_analysis_details_ids,
                             get_mfd_batch_drugs_dao, check_batch_drug_dao, get_pending_mfd_pack_list_dao)
from src.dao.misc_dao import update_sequence_no_for_pre_processing_wizard
from src.dao.pack_analysis_dao import update_pack_analysis_details_by_analysis_id, db_get_drop_time
from src.dao.pack_distribution_dao import get_packs_to_be_filled_by_canister, get_affected_pack_list_for_canisters
from src.dao.revert_batch_dao import get_pack_analysis_details_ids_by_batch
from src.exceptions import (NoLocationExists, RealTimeDBException, PharmacySoftwareCommunicationException,
                            PharmacySoftwareResponseException)
from src.service.canister_recommendation import use_other_canisters
from src.service.misc import update_document_with_revision, fetch_systems_by_company, fetch_users_by_company, \
    update_user_access_in_auth, update_mfd_module_couch_db, get_mfd_module_couch_db, get_mfd_transfer_couch_db, update_couch_db_mfd_canister_wizard, get_mfd_wizard_couch_db, \
    update_mfd_transfer_wizard_couch_db, update_timestamp_couch_db_pre_processing_wizard
from src.dao.couch_db_dao import get_couch_db_database_name, get_document_from_couch_db, reset_couch_db_document
from src.service.notifications import Notifications
from src.service.mfd_canister import (get_trolley_drawer_data, check_drop_pending,
                                      get_trolley_drawer_from_serial_number_mfd, update_mfd_canister_history,
                                      mfd_canister_found_update_status,
                                      update_mfd_misplaced_count
                                      )
from src.service.volumetric_analysis import get_canister_stick_details, get_available_drugs_for_recommended_canisters

logger = settings.logger


def get_mfd_batch_data(info_dict):
    """
    Returns pending and in progress batch data and assigned minimum batch_id to notify weather any batch is assigned
    to that particular user(Pharma-tech)
    :param info_dict: dict
    :return: json
    """
    batch_data = list()
    user_id = info_dict['user_id']
    company_id = info_dict['company_id']
    system_id = info_dict['system_id']
    batch_id = info_dict.get('batch_id', None)
    try:
        try:
            mfs_id = get_mfs_data_by_system_id(system_id)
        except ValueError as e:
            return error(1020, '{}.'.format(str(e)))
        if not batch_id:
            batch_ids = db_get_batch_ids(company_id, mfs_id)
        else:
            batch_ids = [batch_id]

        if not batch_ids:
            mfd_data = {'mfd_batch_data': [],
                        'assigned_min_batch': None
                        }
            return create_response(mfd_data)
        query = db_get_mfd_batch_info(batch_ids=batch_ids)

        is_any_batch_scheduled = False

        assigned_min_batch = db_get_min_batch(user_id, company_id, mfs_id)

        for record in query:
            if record['assigned_user_id']:
                record['schedule_allowed'] = True
            else:
                if is_any_batch_scheduled:
                    record['schedule_allowed'] = False
                else:
                    is_any_batch_scheduled = True
                    record['schedule_allowed'] = True
            batch_data.append(record)

        mfd_data = {
            'mfd_batch_data': batch_data,
            'assigned_min_batch': assigned_min_batch
        }

        return create_response(mfd_data)

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return error(2001)


@log_args_and_response
def get_mfd_user_batch_data(info_dict):
    """
    Returns pending and in progress batch data assigned to particular user
    :param info_dict: dict
    :return: json
    """
    batch_data = list()
    user_id = info_dict['user_id']
    company_id = info_dict['company_id']
    system_id = info_dict['system_id']
    try:
        try:
            mfs_id = get_mfs_data_by_system_id(system_id)
        except ValueError as e:
            return error(1020, '{}.'.format(str(e)))
        batch_ids = db_get_batch_ids(company_id, mfs_id)

        if not batch_ids:
            return create_response(batch_data)
        query = db_get_mfd_batch_info(user_id=user_id, mfs_id=mfs_id, company_id=company_id)

        for record in query:
            if record['total_canister'] != record['filled_canister']:
                batch_data.append(record)

        return create_response(batch_data)

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_mfd_user_batch_data: {}".format(e))
        return error(0)


@log_args_and_response
@validate(required_fields=["batch_id", "user_id", "company_id", "system_id"])
def get_batch_drug_details(dict_batch_info):
    """
    returns pending drugs data to be filled by particular user and weather or not alternate selection is allowed for
    whole batch(not drug wise: based on weather the filling is started or not)
    :param dict_batch_info: dict
    :return: json
    """
    filter_fields = dict_batch_info.get('filter_fields', None)
    sort_fields = dict_batch_info.get('sort_fields', None)

    batch_id = dict_batch_info['batch_id']
    user_id = dict_batch_info['user_id']
    # company_id = dict_batch_info['company_id']
    system_id = dict_batch_info.get('system_id')

    get_trolley_drugs: bool = dict_batch_info.get('get_trolley_drugs', False)
    logger.info("MFD Drug List will be retrieved by {}.".format("Trolley" if get_trolley_drugs else "Unique Drugs"))

    try:
        try:
            mfs_id = get_mfs_data_by_system_id(system_id)
        except ValueError as e:
            return error(1020, '{}.'.format(str(e)))

        if not get_trolley_drugs:
            drug_list, count, patient_list, ndc_list = db_get_batch_drugs(batch_id, user_id, mfs_id, filter_fields,
                                                                              sort_fields)
            change_ndc_drug_list = get_available_drugs_for_recommended_canisters(ndc_list)
            for record in drug_list:
                record['change_ndc_available'] = True if record['ndc'] in change_ndc_drug_list else False
            batch_data = dict()
            if drug_list:
                batch_ids = [batch_id]
                batch_data = db_get_mfd_batch_info(batch_ids, user_id)
                batch_data = batch_data[0]
                if int(batch_data['total_canister']) == int(batch_data['pending_canister']):
                    batch_data['disable_alternate'] = False
                else:
                    batch_data['disable_alternate'] = True

            return create_response({"patient_data": patient_list, "drug_list": drug_list, "number_of_records": count,
                                    "batch_data": batch_data})
        else:
            trolley_id_list: List[int] = dict_batch_info.get("trolley_id_list", [])
            trolley_data: Dict[int, Dict[str, Any]] = db_get_batch_drugs_by_trolley(batch_id, user_id, mfs_id,
                                                                                    trolley_id_list)

            return create_response({"trolley_data": trolley_data})

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["batch_id", "user_id", "company_id", "system_id"])
def get_batch_drug_trolley_details(dict_batch_info):
    batch_id = dict_batch_info['batch_id']
    user_id = dict_batch_info['user_id']
    # company_id = dict_batch_info['company_id']
    system_id = dict_batch_info.get('system_id')

    get_trolley_drugs: bool = dict_batch_info.get('get_trolley_drugs', False)
    logger.info("MFD Drug List will be retrieved by {}.".format("Trolley" if get_trolley_drugs else "Unique Drugs"))

    try:
        try:
            mfs_id = get_mfs_data_by_system_id(system_id)
        except ValueError as e:
            return error(1020, '{}.'.format(str(e)))

        trolley_data: Dict[int, Dict[str, Any]] = db_get_trolley_by_batch(batch_id, user_id, mfs_id)
        return create_response({"trolley_data": trolley_data})

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def update_mfd_alternate_drug(request_args):
    """
    updates alternate drug for mfd batch for particular user
    :param request_args: dict
    :return: json
    """
    batch_id = request_args['batch_id']
    old_ndc = request_args['old_ndc']
    new_ndc = request_args['new_ndc']
    user_id = request_args['user_id']
    company_id = request_args['company_id']
    try:
        try:
            old_ndc_record = get_drug_data_by_ndc_dao(ndc=old_ndc)
            new_ndc_record = get_drug_data_by_ndc_dao(ndc=new_ndc)
        except DoesNotExist as e:
            logger.info("Error in update_mfd_alternate_drug: {}".format(e))
            return error(1020, 'Unable to find drug.')

        is_alternate = old_ndc_record.txr == new_ndc_record.txr \
                       and old_ndc_record.formatted_ndc != new_ndc_record.formatted_ndc \
                       and str(old_ndc_record.brand_flag) == settings.GENERIC_FLAG == str(new_ndc_record.brand_flag)
        if not is_alternate:
            return error(1020, "Provided NDCs are not alternate drugs.")
        with db.transaction():
            old_drug_list = list()
            new_drug_list = list()
            # pack_list = list()
            pack_ids = list()
            analysis_ids = list()
            slot_ids = list()

            analysis_id_query = db_get_drug_analysis_query(batch_id, user_id, old_ndc_record)

            for record in analysis_id_query.dicts():
                pack_ids.append(record['pack_id'])
                analysis_ids.append(record['id'])
                slot_ids.append(record['slot_id'])
            # analysis_ids = [record['id'] for record in analysis_id_query.dicts()]
            if not pack_ids:
                return error(1020, 'Unable to find any pack ids to change alternate drug.')

            drug_ids = [item.id for item in get_drugs_by_formatted_ndc_txr_dao(
                formatted_ndc=old_ndc_record.formatted_ndc,
                txr=old_ndc_record.txr)]
            for drug_id in drug_ids:
                old_drug_list.append(int(drug_id))
                new_drug_list.append(int(new_ndc_record.id))
            response = alternate_drug_update({
                'pack_list': ','.join(map(str, pack_ids)),
                'olddruglist': ','.join(map(str, old_drug_list)),
                'newdruglist': ','.join(map(str, new_drug_list)),
                'user_id': user_id,
                'company_id': company_id,
                'send_notification': True,
                'module_id': constants.PDT_MFD_ALTERNATE
            })
            response = json.loads(response)
            if response['status'] != 'success':
                # throwing exception to rollback changes as we could not update IPS
                raise Exception(response['description'])
            return create_response(response['data'])
    except (InternalError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except PharmacySoftwareCommunicationException as e:
        logger.error(e, exc_info=True)
        return error(7001)
    except PharmacySoftwareResponseException as e:
        logger.error(e, exc_info=True)
        return error(7001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(0, str(e))


@log_args_and_response
@validate(required_fields=['batch_id', 'drug_id', 'user_id', 'company_id', 'skip_for_batch', 'system_id'])
def skip_drug(request_args):
    """
    skips drug for particular canisters which are currently placed on particular MFS or for entire batch of a particular
    user
    :param request_args: dict
    :return: json
    """
    batch_id = request_args['batch_id']
    drug_id = request_args['drug_id']
    user_id = request_args['user_id']
    company_id = request_args['company_id']
    skip_for_batch = request_args['skip_for_batch']
    system_id = request_args['system_id']

    logger.info(f"In skip_drug, request_args:{request_args}")

    try:
        with db.transaction():
            try:
                mfs_id = get_mfs_data_by_system_id(system_id)
            except ValueError as e:
                return error(1020, '{}.'.format(str(e)))
            if skip_for_batch:
                canister_status = [constants.MFD_CANISTER_IN_PROGRESS_STATUS, constants.MFD_CANISTER_PENDING_STATUS]
            else:
                canister_status = [constants.MFD_CANISTER_IN_PROGRESS_STATUS]
            analysis_ids, analysis_details_ids = db_get_analysis_ids_drug(company_id, user_id, drug_id, batch_id,
                                                                          canister_status, mfs_id,
                                                                          skip_for_batch=skip_for_batch)
            logger.info(f"In skip_drug, analysis_ids: {analysis_ids}")
            logger.info(f"In skip_drug, analysis_details_ids:{analysis_details_ids}")

            if not analysis_details_ids:
                return error(1020)
            status = db_skip_drug(list(analysis_details_ids))

            logger.info(f"In skip_drug: status:{status}")

            if status:
                canister_updates, skipped_updated_systems, update_mfs_data = skip_drug_canister_status_change(
                    analysis_ids, company_id, user_id, alert=False, mfs_system_id=system_id)

            logger.info('In skip_drug, checking_trolley_reuse_while_skip')
            update_pending_mfd_assignment({'company_id': company_id, 'batch_id': batch_id})
            logger.info('In skip_drug, checking_trolley_reuse_while_skip_done')

            for mfs_system_id, mfs_data in update_mfs_data.items():
                update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID, mfs_system_id, mfs_data)

            return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=['batch_id', 'drug_id', 'user_id', 'company_id', 'system_id', 'action'])
def update_drug_status(request_args):
    """
    updates drug status for canisters which are currently placed on particular MFS
    :param request_args: dict
    :return: json
    """
    batch_id = request_args['batch_id']
    drug_id = request_args['drug_id']
    user_id = request_args['user_id']
    company_id = request_args['company_id']
    system_id = request_args['system_id']
    action = request_args['action']

    valid_actions = ['filled', 'pending']
    if action not in valid_actions:
        return error(1020, 'Action is not valid. Valid Actions: {}.'.format(valid_actions))
    try:
        with db.transaction():
            try:
                mfs_id = get_mfs_data_by_system_id(system_id)
            except ValueError as e:
                return error(1020, '{}.'.format(str(e)))

            if action == 'filled':
                status_id = constants.MFD_DRUG_FILLED_STATUS
                canister_status = [constants.MFD_CANISTER_IN_PROGRESS_STATUS]
            elif action == 'pending':
                canister_status = [constants.MFD_CANISTER_FILLED_STATUS, constants.MFD_CANISTER_VERIFIED_STATUS,
                                   constants.MFD_CANISTER_IN_PROGRESS_STATUS]
                status_id = constants.MFD_DRUG_PENDING_STATUS
            analysis_ids, analysis_details_ids = db_get_analysis_ids_drug(company_id, user_id, drug_id, batch_id,
                                                                          canister_status, mfs_id)

            if not analysis_details_ids:
                return error(1020)
            status = db_update_drug_status(list(analysis_details_ids), status_id)
            if action == 'filled':
                pending_canisters_analysis = db_get_canisters_status_based(list(analysis_ids),
                                                                           [constants.MFD_DRUG_PENDING_STATUS])
                filled_canisters_analysis = analysis_ids - pending_canisters_analysis
                # status_id = constants.MFD_DRUG_FILLED_STATUS
                if filled_canisters_analysis:
                    update_canister_status = db_update_canister_status(list(filled_canisters_analysis),
                                                                       constants.MFD_CANISTER_FILLED_STATUS, user_id)
                    logger.info("In update_drug_status: update_canister_status: {}".format(update_canister_status))
            elif action == 'pending':
                update_canister_status = db_update_canister_status(list(analysis_ids),
                                                                   constants.MFD_CANISTER_IN_PROGRESS_STATUS, user_id)
                logger.info("In update_drug_status:action = pending, update_canister_status: {}".format(update_canister_status))
            return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def get_users_from_station(station_list: list, company_id) -> dict:
    """
    updates couch db doc for user access
    :return: boolean
    @param company_id:
    @param station_list:
    """

    try:
        device_user_mapping = dict()
        device_system, device_associated_device_dict = get_mfs_systems(station_list)
        system_ids = list()
        auth_mfs_systems = list()
        system_user_access = dict()
        for system, device in device_system.items():
            if len(device) > 1:
                raise ValueError('Multiple devices found for given system')
            else:
                system_ids.append(system)
        if len(system_ids) != len(station_list):
            raise ValueError('Invalid devices found')
        system_data = fetch_systems_by_company(company_id=company_id,
                                               system_type=constants.AUTH_MFS_SYSTEM_TYPE,
                                               system_ids=system_ids)
        for system_id, system_details in system_data.items():
            system_id = int(system_id)
            auth_mfs_systems.append(system_id)
            if system_id not in system_user_access:
                system_user_access[system_id] = set()
            user_data = system_details['users']
            for user_info in user_data:
                if user_info['user_id']:
                    system_user_access[system_id].add(user_info['user_id'])

        if system_ids != auth_mfs_systems:
            raise ValueError('Systems not found in auth')
        for system, user in system_user_access.items():
            if not user:
                raise ValueError('No user found for given station')
            else:
                user = list(user)
            if len(user) > 1:
                raise ValueError('Multiple users found for given stations')
            device_user_mapping[device_system[system][0]] = {'user_id': user[0], 'associated_device_id': device_associated_device_dict[device_system[system][0]]}

        return device_user_mapping
    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return error(2001)


@log_args_and_response
def validate_station_selection_on_recommendation(mfd_stations_list: list,
                                                 required_trolley: int,
                                                 station_linked: list):
    """
    FUnction to validate MFS station selection based on required trolley.
    `i.e` if user selects stations more than required trolley then ask to
    link stations.
    @param mfd_stations_list: list
    @param required_trolley: int
    @param station_linked: list
    @return:
    """
    mfd_stations = deepcopy(mfd_stations_list)
    linked_station_selected = False
    try:
        if required_trolley < len(mfd_stations):
            associated_station_selected = get_associated_mfs_stations(station_list=mfd_stations)
            for station in mfd_stations:
                if associated_station_selected[station] in mfd_stations:
                    linked_station_selected = True
                    break
            if not len(station_linked) and linked_station_selected:
                return False, constants.LINK_STATION_MESSAGE

            elif not len(station_linked) and not linked_station_selected:
                return False, constants.STATION_MAX_LIMIT_MESSAGE

            else:
                for stations_list in station_linked:
                    mfd_stations.remove(stations_list[0])
                if required_trolley < len(mfd_stations):
                    return False, constants.LINK_STATION_MESSAGE
                else:
                    return True, True

        else:
            return True, True

    except Exception as e:
        logger.error("Error in validate_station_selection_on_recommendation {}".format(e))
        return False, "Error in validating station"


@log_args_and_response
@validate(required_fields=['company_id', 'batch_id'])
def update_mfd_analysis(data_dict):
    """
    To populate trolley loc id and assigned user id in MFDAnalysis
    @param data_dict: dict
    @return: case 1: count of number of required trolley
            case 2: Dict of Assigned trolley to user and station
            case 3: Update data in mfd analysis and return status success
    """

    logger.info("In update_mfd_analysis")
    batch_id = data_dict['batch_id']
    company_id = data_dict.get('company_id')
    station_linked = data_dict.get('station_linked', None)
    update_mfd_data = data_dict.get("update_mfd_data", False)
    mfd_stations = data_dict.get("mfd_stations", [])
    required_trolley = data_dict.get("required_trolley", None)
    manual_pre_fill = data_dict.get("manual_pre_fill", False)
    user_id = data_dict.get("user_id", None)
    batch_skipped = data_dict.get("batch_skipped", False)
    mfd_station_user = dict()
    device_list = list()
    mfd_pack_patient_dict = dict()
    mfd_canister_destination_dict = dict()
    patient_mfd_canister_slot_pack_dict = dict()
    mfd_canister_patient_pack_dict = dict()
    canister_pack_dict = dict()
    pack_order_no_date_dict = dict()
    pack_travelled_dict = dict()
    pack_quadrant_canister_dict = dict()
    pack_device_dict = dict()
    pack_canister_dict = dict()
    mfd_analysis_ids = set()
    mfd_analysis_detail_ids = set()

    logger.info("In update_mfd_analysis")
    system_id = get_system_id_from_batch_id(batch_id=batch_id)
    args = {"system_id": system_id}
    seq_no = constants.PPP_SEQUENCE_MFD_RECOMMENDATION_DONE


    try:
        if manual_pre_fill:
            pending_trolley_sequence = db_get_mfd_pending_sequence_for_batch(batch_id)
            if not pending_trolley_sequence:
                return error(21009, "Please wait, The page is refreshing")

        with db.transaction():
            batch_data = get_batch_data(batch_id)
            if batch_data.sequence_no == constants.PPP_SEQUENCE_IN_PROGRESS:
                return error(2000)
            else:
                previous_seq_no = batch_data.sequence_no
                logger.info("In update_mfd_analysis: previous sequence: {} for batch_id:{}".format(previous_seq_no,
                                                                                                    batch_id))
                # run update_mfd_analysis if sequence is PPP_SEQUENCE_MFD_RECOMMENDATION_DONE (4)
                if not manual_pre_fill:
                    if previous_seq_no != constants.PPP_SEQUENCE_MFD_RECOMMENDATION_DONE:
                        return error(1020, "Error in update_mfd_analysis, already executed")

                if update_mfd_data:
                    # update sequence_no to PPP_SEQUENCE_IN_PROGRESS(1) in batch master
                    seq_status = update_sequence_no_for_pre_processing_wizard(
                        sequence_no=constants.PPP_SEQUENCE_IN_PROGRESS,
                        batch_id=batch_id)
                    logger.info("In update_mfd_analysis: update_mfd_analysis execution started: {} , changed sequence to {} for batch_id: {}"
                        .format(seq_status, constants.PPP_SEQUENCE_IN_PROGRESS, batch_id))
                    if seq_status:
                        # update couch db timestamp for pack_pre processing wizard change
                        couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=args)
                        logger.info("In update_mfd_analysis: couch db updated for preprocessing sequence for in progress API: {} for batch_id: {}".format(
                            couch_db_status, batch_id))

        if mfd_stations:
            mfd_station_user = get_users_from_station(mfd_stations, company_id)

        mfd_analysis_query = get_required_mfd_canister_data(batch_id, manual_pre_fill, system_id)
        """
        Create required dicts
        """
        for record in mfd_analysis_query:
            mfd_analysis_ids.add(record["analysis_id"])
            mfd_analysis_detail_ids.add(record["id"])
            if record['dest_device_id'] not in device_list:
                device_list.append(int(record['dest_device_id']))

            if record['pack_id'] not in pack_order_no_date_dict:
                mfd_pack_patient_dict[record['pack_id']] = record['patient_id']
                pack_device_dict[record['pack_id']] = record['dest_device_id']
                pack_order_no_date_dict[record['pack_id']] = {"order_no": record['pack_queue_order'],
                                                              "delivery_date": record['delivery_date']}
                pack_travelled_dict[record['pack_id']] = False
                # todo remove hardcoded quadrants
                pack_quadrant_canister_dict[record['pack_id']] = {1: set(), 2: set(), 3: set(), 4: set()}
                pack_canister_dict[record['pack_id']] = list()

            pack_quadrant_canister_dict[record['pack_id']][record['dest_quadrant']].add(record['mfd_analysis_id'])

            if record['mfd_analysis_id'] not in pack_canister_dict[record['pack_id']]\
                    and record['mfd_analysis_id'] not in canister_pack_dict.keys():
                pack_canister_dict[record['pack_id']].append(record['mfd_analysis_id'])

            if record['dest_device_id'] not in mfd_canister_destination_dict.keys():
                mfd_canister_destination_dict[record['dest_device_id']] = dict()

            if record['dest_quadrant'] not in mfd_canister_destination_dict[record['dest_device_id']].keys():
                mfd_canister_destination_dict[record['dest_device_id']][record['dest_quadrant']] = set()

            mfd_canister_destination_dict[record['dest_device_id']][record['dest_quadrant']].add(
                record['mfd_analysis_id'])

            if record['mfd_analysis_id'] not in mfd_canister_patient_pack_dict.keys():
                canister_pack_dict[record['mfd_analysis_id']] = set()
                mfd_canister_patient_pack_dict[record['mfd_analysis_id']] = dict()

            if record['patient_id'] not in patient_mfd_canister_slot_pack_dict.keys():
                patient_mfd_canister_slot_pack_dict[record['patient_id']] = dict()

            if record['mfd_analysis_id'] not in patient_mfd_canister_slot_pack_dict[record['patient_id']]:
                patient_mfd_canister_slot_pack_dict[record['patient_id']][record['mfd_analysis_id']] = list()

            if (record['mfd_can_slot_no'], record['pack_id']) not in \
                    patient_mfd_canister_slot_pack_dict[record['patient_id']][record['mfd_analysis_id']]:
                patient_mfd_canister_slot_pack_dict[record['patient_id']][record['mfd_analysis_id']]\
                    .append((record['mfd_can_slot_no'],
                             record['pack_id']))

            canister_pack_dict[record['mfd_analysis_id']].add(record['pack_id'])
            if record['patient_id'] not in mfd_canister_patient_pack_dict[record['mfd_analysis_id']].keys():
                mfd_canister_patient_pack_dict[record['mfd_analysis_id']][record['patient_id']] = set()

            mfd_canister_patient_pack_dict[record['mfd_analysis_id']][record['patient_id']].add(record['pack_id'])

            """
            Get device wise mini batches
            """
        if not mfd_canister_patient_pack_dict:
            # update sequence_no to PPP_SEQUENCE_UPDATE_MFD_ANALYSIS_DONE(it means update mfd analysis api run successfully)
            seq_no = constants.PPP_SEQUENCE_UPDATE_MFD_ANALYSIS_DONE
            logger.info("In update_mfd_analysis: assign sequence_no to seq_no: {} for batch_id: {}".format(seq_no, batch_id))
            return create_response(True)

        mini_batch, pack_to_transfer_manual = get_device_wise_mini_batches(mfd_canister_destination_dict,
                                                                           pack_quadrant_canister_dict,
                                                                           pack_order_no_date_dict,
                                                                           pack_travelled_dict,
                                                                           pack_device_dict,
                                                                           canister_pack_dict
                                                                           )
        if not mini_batch:
            return error(13006)

        """
        Remove data of packs from mfd analysis and update in pack analysis details for packs 
        for which mfd canisters cannot be filled
        """
        if len(pack_to_transfer_manual):
            moved_manual = delete_update_manual_mfd_packs(batch_id=batch_id,
                                                          pack_list=list(pack_to_transfer_manual),
                                                          pack_canister_dict=pack_canister_dict)
            logger.info("In update_mfd_analysis: delete_update_manual_mfd_packs status: {}".format(moved_manual))

        if batch_skipped:
            skipped_status = db_update_mfd_status(batch=batch_id,
                                                  mfd_status=constants.MFD_BATCH_PRE_SKIPPED,
                                                  user_id=user_id)

            skip_mfd_status = db_update_mfd_skip(mfd_analysis_ids=list(mfd_analysis_ids),
                                                 mfd_analysis_detail_ids=list(mfd_analysis_detail_ids), user_id=user_id)

        # Function to get quad wise count of mfd canisters
        mini_batch_quad_canister_data = get_quad_canister_count(mini_batch, pack_quadrant_canister_dict)
        """
        Distribute canisters between selected users and stations
        """
        status, response = divide_canister_among_stations(mini_batch_quad_canister_data, mfd_station_user,
                                                          station_linked, update_mfd_data, company_id,
                                                          batch_id, pack_canister_dict, pack_order_no_date_dict,
                                                          mfd_pack_patient_dict, patient_mfd_canister_slot_pack_dict,
                                                          system_id, manual_pre_fill, batch_skipped)

        logger.info("divide_canister_among_stations {}, {}".format(status, response))

        if update_mfd_data:
            batch_device_dict = get_mfd_canister_batch_id_for_transfers(system_id=system_id,
                                                                        batch_id=batch_id)
            logger.info('User_assignment: batch_device_dict: {}'.format(batch_device_dict))
            progress_batch = get_progress_batch_id(system_id)
            if not batch_device_dict and not progress_batch:
                batch_device_dict[batch_id] = device_list

            couch_db_wizard = create_couch_db_doc_mfd_canister_wizard(company_id=company_id,
                                                                      batch_device_dict=batch_device_dict,
                                                                      current_batch=batch_id)
            logger.info("create_couch_db_doc_mfd_canister_wizard status {}".format(couch_db_wizard))
            # update sequence_no to PPP_SEQUENCE_UPDATE_MFD_ANALYSIS_DONE(it means UPDATE_MFD_ANALYSIS api run successfully)
            seq_no = constants.PPP_SEQUENCE_UPDATE_MFD_ANALYSIS_DONE
            logger.info("In update_mfd_analysis: update_mfd_data = True, assign sequence_no to seq_no: {} for batch_id: {}".format(seq_no, batch_id))
        else:
            if mfd_stations and required_trolley and not update_mfd_data:
                validate_status, message = validate_station_selection_on_recommendation(mfd_stations_list=mfd_stations,
                                                                                        required_trolley=required_trolley,
                                                                                        station_linked=station_linked)
                if not validate_status:
                    response["selection_validation"] = message
        if status:
            logger.info("update_mfd_analysis {}".format(response))
            return create_response(response)
        else:
            seq_no = previous_seq_no
            logger.info("In update_mfd_analysis: response is false, assign previous_seq_no to seq_no: {} for batch_id: {}".format(seq_no, batch_id))
            return error(1000, response)

    except ValueError as e:
        seq_no = previous_seq_no
        logger.info("In update_mfd_analysis: when exception occurs assign previous_seq_no to seq_no: {} for batch_id: {}".format(
                seq_no, batch_id))
        logger.error(e)
        return error(1020, str(e))

    except Exception as e:
        seq_no = previous_seq_no
        logger.info("In update_mfd_analysis: when exception occurs assign previous_seq_no to seq_no: {} for batch_id: {}".format(
                seq_no, batch_id))
        logger.error(e)
        return error(1000, "Error in updating mfd analysis data.")

    finally:
        sequence_status = update_sequence_no_for_pre_processing_wizard(sequence_no=seq_no, batch_id=batch_id)
        logger.info("In update_mfd_analysis: update_mfd_analysis run successfully: {} , changed sequence to {} for batch_id: {}"
                     .format(sequence_status, seq_no, batch_id))
        if sequence_status:
            # update couch db timestamp for pack_pre processing wizard change
            couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=args)
            logger.info("In update_mfd_analysis: couch db updated for preprocessing sequence : {} for batch_id: {}".format(couch_db_status, batch_id))


@log_args_and_response
def get_quad_canister_count(mini_batch, pack_quadrant_canister_dict):
    """
    Function to get quad wise count of mfd canisters
    @param mini_batch: dict
    @param pack_quadrant_canister_dict: dict
    @return:mini_batch_quad_canister_data : dict
    """
    logger.info("In get_quad_canister_count")

    mini_batch_quad_canister_data = dict()
    for device, batch_packs in mini_batch.items():
        mini_batch_quad_canister_data[device] = list()
        for each_batch in batch_packs:
            can_set = set()
            quad_can_list = {"packs": each_batch, "total_canisters": 0,
                             "quad_canister": {1: set(), 2: set(), 3: set(), 4: set()}}
            for each_pack in each_batch:
                quad_canister_data = pack_quadrant_canister_dict[each_pack]
                for quad, canister_set in quad_canister_data.items():
                    can_set.update(canister_set)
                    quad_can_list["quad_canister"][quad].update(canister_set)
            quad_can_list["total_canisters"] += len(can_set)
            mini_batch_quad_canister_data[device].append(quad_can_list)

    return mini_batch_quad_canister_data


@log_args_and_response
def divide_canister_among_stations(mini_batch_quad_canister_data, mfd_stations, station_linked,
                                   update_mfd_data, company_id, batch_id, pack_canister_dict,
                                   pack_order_no_date_dict, mfd_pack_patient_dict,
                                   patient_mfd_canister_slot_pack_dict, system_id, manual_pre_fill, batch_skipped):
    """
    Distribute canisters between selected users and stations
    @param: mini_batch_quad_canister_data: dict,
            mfd_stations: dict,
            station_linked: list,
            update_mfd_data: Bool

    @return: case 1: if not update_mfd_data and mfd_stations: return count of fillers required
            case2: if not update_mfd_data but mfd_stations: return dict
            case3: if update_mfd_stations: return dict (status success)
    """
    logger.info("In divide_canister_among_stations")
    # station_canister_dict = dict()
    try:
        devices = list(mini_batch_quad_canister_data.keys())
        device_1_batch = deepcopy(mini_batch_quad_canister_data[devices[0]])

        # optimize dynamically assign according to devices
        if len(devices) > 1:
            device_2_batch = deepcopy(mini_batch_quad_canister_data[devices[1]])
        else:
            device_2_batch = []

        main_trolley_batch = list()

        total_batches = len(device_1_batch) + len(device_2_batch)
        mfd_trolley, drawer_location_info, system_id_id = get_required_mfd_trolley(company_id=company_id,
                                                                                batch_id=batch_id,
                                                                                system_id=system_id)

        if not mfd_trolley:
            logger.info(f"In divide_canister_among_stations, No Manual Canister Cart available for transfer")
            mfd_trolley = [0]
            drawer_location_info = dict()
            # return False, "No Manual Canister Cart available for transfer"

        for i in range(0, total_batches+1):
            temp_batch = list()
            if len(device_1_batch):
                temp_batch.append(device_1_batch.pop(0))
            if len(device_2_batch):
                temp_batch.append(device_2_batch.pop(0))
            if len(temp_batch):
                main_trolley_batch.append(temp_batch)

        # main_trolley_batch = [trolley_batch[i:i + 2] for i in range(0, len(trolley_batch), 2)]
        assigned_trolley_batch = list(zip(cycle(mfd_trolley), main_trolley_batch))

        if len(mfd_stations) or (update_mfd_data and batch_skipped):
            # distribute mini batches to selected stations
            trolley_station_linked, station_canister_dict, pack_station_dict = distribute_batches_between_stations(assigned_trolley_batch,
                                                                                                                   mfd_stations,
                                                                                                                   station_linked,
                                                                                                                   pack_canister_dict)

            if update_mfd_data:
                # assign mfd trolley location to mfd canisters
                canister_location_dict = assign_trolley_location_to_mfd_canisters(assigned_trolley_batch,
                                                                                  drawer_location_info,
                                                                                  pack_station_dict,
                                                                                  pack_canister_dict,
                                                                                  pack_order_no_date_dict,
                                                                                  mfd_pack_patient_dict,
                                                                                  patient_mfd_canister_slot_pack_dict,
                                                                                  system_id, batch_skipped)

                data_updated_status = populate_data_in_mfd_tables(canister_location_dict,
                                                                  station_canister_dict, manual_pre_fill, company_id)

                if not manual_pre_fill and not batch_skipped:
                    batch_status_dict = {"status": settings.BATCH_MFD_USER_ASSIGNED}
                    batch_status_update = update_batch_data(batch_id, batch_status_dict)
                    logger.info("In divide_canister_among_stations: batch_status_update: {}".format(batch_status_update))

                return True, data_updated_status

            if len(mfd_stations) and not update_mfd_data:
                for mfd_station in mfd_stations:
                    if mfd_station not in station_canister_dict:
                        station_canister_dict[mfd_station] = {
                            'total_packs': [],
                            'total_canisters': 0,
                            'user_list': [mfd_stations[mfd_station]['user_id']],
                            'associated_device_id': mfd_stations[mfd_station]['associated_device_id']}
                return True, {"user_distribution": station_canister_dict}

        mfs_stations = get_active_mfs_id_by_company_id(company_id, system_id)
        trolley_count = len(assigned_trolley_batch)
        response = {"required_trolley": trolley_count,
                    "user_count": len(mfs_stations) if trolley_count >= len(mfs_stations) else trolley_count}

        return True, response

    except ValueError as e:
        logger.error(e)
        return False, error(1020, str(e))

    except Exception as e:
        logger.error(e)
        return False, "Error in assigning canisters to stations."


@log_args_and_response
def populate_data_in_mfd_tables(canister_location_dict, station_canister_dict, manual_pre_fill, company_id):
    """

    @param canister_location_dict: dict
    @param station_canister_dict: dict
    @return: Boolean
    """
    try:
        # todo move this function to DAO
        logger.info("In populate_data_in_mfd_tables")
        for canister, location_tuple in canister_location_dict.items():
            location_id, trolley_id, order_no, trolley_sequence, station_id = location_tuple

            if not station_canister_dict:
                status = populate_mfd_analysis_trolley(trolley_seq=trolley_sequence, order_no=order_no, analysis_id=canister)
            else:
                update_dict = {"mfs_device_id": int(station_id),
                               "trolley_location_id": location_id,
                               "assigned_to": int(station_canister_dict[station_id]['user_list'][0]),
                               "order_no": order_no,
                               "trolley_seq": trolley_sequence}
                if manual_pre_fill:
                    update_dict = dict()
                    update_dict["status_id"] = MFD_CANISTER_PENDING_STATUS
                    update_dict["mfs_device_id"] = int(station_id)
                    update_dict["assigned_to"] = int(station_canister_dict[station_id]['user_list'][0])

                    system_id_for_robot = get_system_id_based_on_device_type(company_id=company_id,
                                                                             device_type_id=settings.DEVICE_TYPES[
                                                                                 "ROBOT"])
                    progress_batch = get_progress_batch_id(system_id_for_robot)
                    if progress_batch:
                        is_user_assign_pending = check_user_in_progress_batch(progress_batch)
                        if is_user_assign_pending:
                            update_dict["trolley_location_id"] = location_id

                    status = populate_mfd_analysis_details_status(status=MFD_DRUG_PENDING_STATUS,
                                                                  analysis_id=canister)

                updated_status = populate_mfd_trolley_data(analysis_id=canister, update_data=update_dict)
                logger.info("status after updating mfd analysis {}".format(updated_status))

        return True

    except Exception as e:
        logger.error(e)
        return False


@log_args_and_response
def distribute_batches_between_stations(assigned_trolley_batch, mfd_stations, station_linked, pack_canister_dict):
    """
    Note: Assumptions are made that there are only 4 stations
    @param pack_canister_dict:
    @param assigned_trolley_batch:
    @param mfd_stations:
    @param station_linked:
    @return:
    """
    trolley_station_linked = dict()
    station_canister_dict = dict()
    pack_station_dict = dict()
    mfd_stations_updated = deepcopy(mfd_stations)
    logger.info("In distribute_batches_between_stations")
    removed_stations = dict()
    logger.info(station_linked)
    try:
        if len(station_linked):
            for station_group in station_linked:
                removed_stations[station_group[0]] = (station_group[1], mfd_stations_updated[station_group[0]])
                mfd_stations_updated.pop(station_group[0], None)

        if len(assigned_trolley_batch) == len(mfd_stations_updated):
            temp_mfd_stations = deepcopy(list(mfd_stations_updated.keys()))
            for each_batch in assigned_trolley_batch:
                trolley_id, batch_list = each_batch
                station_id = temp_mfd_stations.pop()
                trolley_station_linked[trolley_id] = [station_id]
                user_id = mfd_stations_updated[station_id]['user_id']
                associated_device_id = mfd_stations_updated[station_id]['associated_device_id']
                total_canisters = sum([batch["total_canisters"] for batch in batch_list])
                total_packs = list()
                for batch in batch_list:
                    total_packs.append(batch['packs'])
                    for each_batch_pack in batch['packs']:
                        pack_station_dict[each_batch_pack] = station_id

                if station_id not in station_canister_dict.keys():
                    station_canister_dict[station_id] = {
                        "total_packs": total_packs,
                        "total_canisters": total_canisters,
                        "user_list": [user_id],
                        "associated_device_id": associated_device_id}
                else:
                    station_canister_dict[station_id]["total_drawers"].extend(total_packs)
                    station_canister_dict[station_id]["total_canisters"] += total_canisters
                    if user_id not in station_canister_dict[station_id]["user_list"]:
                        station_canister_dict[station_id]["user_list"].append(user_id)

        elif len(assigned_trolley_batch) > len(mfd_stations_updated):
            temp_mfd_stations = deepcopy(list(mfd_stations_updated.keys()))
            station_trolley = list(zip(cycle(temp_mfd_stations), assigned_trolley_batch))
            for each_data in station_trolley:
                station_id, trolley_batch = each_data
                trolley_id, batch_list = trolley_batch
                trolley_station_linked[trolley_id] = [station_id]
                user_id = mfd_stations_updated[station_id]['user_id']
                associated_device_id = mfd_stations_updated[station_id]['associated_device_id']
                total_canisters = sum([batch["total_canisters"] for batch in batch_list])
                total_packs = list()
                for batch in batch_list:
                    total_packs.append(batch['packs'])
                    for each_batch_pack in batch['packs']:
                        pack_station_dict[each_batch_pack] = station_id

                if station_id not in station_canister_dict.keys():
                    station_canister_dict[station_id] = {
                        "total_packs": total_packs,
                        "total_canisters": total_canisters,
                        "user_list": [user_id],
                        "associated_device_id": associated_device_id}
                else:
                    station_canister_dict[station_id]["total_packs"].extend(total_packs)
                    station_canister_dict[station_id]["total_canisters"] += total_canisters
                    if user_id not in station_canister_dict[station_id]["user_list"]:
                        station_canister_dict[station_id]["user_list"].append(user_id)

        elif len(assigned_trolley_batch) < len(mfd_stations_updated):
            temp_mfd_stations = deepcopy(list(mfd_stations_updated.keys()))
            for each_batch in assigned_trolley_batch:
                trolley_id, batch_list = each_batch
                station_id = temp_mfd_stations.pop()
                trolley_station_linked[trolley_id] = [station_id]
                user_id = mfd_stations_updated[station_id]['user_id']
                associated_device_id = mfd_stations_updated[station_id]['associated_device_id']
                total_canisters = sum([batch["total_canisters"] for batch in batch_list])
                total_packs = list()
                for batch in batch_list:
                    total_packs.append(batch['packs'])
                    for each_batch_pack in batch['packs']:
                        pack_station_dict[each_batch_pack] = station_id

                if station_id not in station_canister_dict.keys():
                    station_canister_dict[station_id] = {
                        "total_packs": total_packs,
                        "total_canisters": total_canisters,
                        "user_list": [user_id],
                        "associated_device_id": associated_device_id}
                else:
                    station_canister_dict[station_id]["total_packs"].extend(total_packs)
                    station_canister_dict[station_id]["total_canisters"] += total_canisters
                    if user_id not in station_canister_dict[station_id]["user_list"]:
                        station_canister_dict[station_id]["user_list"].append(user_id)

        if len(removed_stations):
            trolley_station_linked, station_canister_dict, pack_station_dict = merge_linked_stations(
                trolley_station_linked,
                station_canister_dict,
                removed_stations,
                pack_canister_dict,
                pack_station_dict)

        return trolley_station_linked, station_canister_dict, pack_station_dict

    except ValueError as e:
        logger.error("Error in distribute_batches_between_stations {}".format(e))
        return error(1020, str(e))


@log_args_and_response
def merge_linked_stations(trolley_station_linked, station_canister_dict, removed_stations,
                          pack_canister_dict, pack_station_dict):
    """
    Function will merge two stations that are linked.
    @return:
    """
    trolley_station_linked_updated = deepcopy(trolley_station_linked)
    for station, station_user in removed_stations.items():
        linked_station, user = station_user
        if linked_station in station_canister_dict.keys():
            total_packs = station_canister_dict[linked_station]['total_packs']
            station_1_packs = list()
            station_2_packs = list()
            can1 = 0
            can2 = 0
            for each_trolley_packs in total_packs:
                pack_list = deepcopy(each_trolley_packs)
                while len(pack_list):
                    if len(pack_list):
                        each_pack = pack_list.pop(0)
                        pack_station_dict[each_pack] = linked_station
                        station_1_packs.append(each_pack)
                        can1 += len(pack_canister_dict[each_pack])
                    if len(pack_list):
                        each_pack = pack_list.pop(0)
                        pack_station_dict[each_pack] = station
                        station_2_packs.append(each_pack)
                        can2 += len(pack_canister_dict[each_pack])

            station_canister_dict[linked_station]['total_packs'] = station_1_packs
            station_canister_dict[linked_station]['total_canisters'] = can1
            station_canister_dict[station] = {"total_canisters": can2,
                                              'user_list': [user['user_id']],
                                              'associated_device_id': user['associated_device_id'],
                                              'total_packs': station_2_packs}

            for trolley, station_linked in trolley_station_linked.items():
                if linked_station in station_linked:
                    trolley_station_linked_updated[trolley].append(station)

    return trolley_station_linked_updated, station_canister_dict, pack_station_dict


@log_args_and_response
def get_required_mfd_trolley(company_id, batch_id, system_id=None):
    """
    Get required mfd trolley for transfer and also their drawer locations info
    @param: company_id
    @return: mfd_trolley: list
             drawer_location_info: dict
    """
    try:
        if not system_id:
            system_id = get_system_id_from_batch_id(batch_id)
        previous_batch_trolley = get_previous_used_mfd_trolley(system_id=system_id,
                                                               current_batch=batch_id)

        if system_id:
            currently_used_trolley = get_currently_used_trolley(company_id=company_id,
                                                                system_id=system_id)

            mfd_trolley = get_available_device_list_of_a_type(device_type_ids=[settings.DEVICE_TYPES['Manual Canister Cart']],
                                                              currently_used_trolley=currently_used_trolley,
                                                              company_id=company_id,
                                                              system_id=system_id)

            if not mfd_trolley:
                logger.info(f"In get_required_mfd_trolley, No trolley found for batch_id: {batch_id}")
                return False, None, None

            if len(previous_batch_trolley):
                previous_batch_trolley = set(mfd_trolley).intersection(set(previous_batch_trolley))
                mfd_trolley = list(set(mfd_trolley) - previous_batch_trolley)
                mfd_trolley.extend(list(previous_batch_trolley))

            trolley_locations, drawer_location_info = get_location_data_from_device_ids(mfd_trolley,
                                                                                        settings.MFD_TROLLEY_FILLED_DRAWER_LEVEL)
            return mfd_trolley, drawer_location_info, system_id

        else:
            return False, None, None

    except InternalError as e:
        logger.error(e)
        raise


def check_if_patient_pack_share_canister_and_return_order(patient_mfd_canister_slot_info: dict):
    """
    Function to check if patient packs share canisters arrange them according to drop and slot
    @param patient_mfd_canister_slot_info:
    @return: list
    """
    ordered_pack_list = list()
    # add other packs only if they share canisters
    try:
        for mfd_analysis_id in sorted(patient_mfd_canister_slot_info.keys()):
            for slot_info in patient_mfd_canister_slot_info[mfd_analysis_id]:
                if slot_info[1] not in ordered_pack_list:
                    ordered_pack_list.append(slot_info[1])

        return ordered_pack_list

    except Exception as e:
        logger.error("Error in check_if_patient_pack_share_canister_and_return_order {}".format(e))
        raise


def assign_order_number_sorted_by_date(batch_list: list,
                                       pack_station_dict: dict,
                                       order_no: int,
                                       pack_order_no_date_dict: dict,
                                       pack_canister_dict: dict,
                                       mfd_pack_patient_dict: dict,
                                       patient_mfd_canister_slot_pack_dict: dict) -> tuple:
    """
    Function to assign order number to pack of one trolley sorted by delivery date
    @param mfd_pack_patient_dict:
    @param patient_mfd_canister_slot_pack_dict:
    @param pack_canister_dict:
    @param batch_list:
    @param pack_station_dict:
    @param order_no:
    @param pack_order_no_date_dict:
    @return:
    """
    canister_order_no_dict = dict()
    canister_station_dict = dict()
    pack_date_dict = dict()
    pack_travelled = list()
    try:
        for batch_data in batch_list:
            for pack in batch_data['packs']:
                pack_date_dict[pack] = pack_order_no_date_dict[pack]["delivery_date"]

        sorted_pack_list = OrderedDict(sorted(pack_date_dict.items(), key=lambda k: k[1]))

        for each_pack in list(sorted_pack_list.keys()):
            if each_pack not in pack_travelled:
                ordered_pack_list = check_if_patient_pack_share_canister_and_return_order(
                    patient_mfd_canister_slot_pack_dict[mfd_pack_patient_dict[each_pack]])
                for ordered_pack in ordered_pack_list:
                    pack_travelled.append(ordered_pack)
                    for each_canister in pack_canister_dict[ordered_pack]:
                        if not pack_station_dict:
                            canister_order_no_dict[each_canister] = order_no
                            order_no += 1
                        if each_canister not in canister_order_no_dict.keys():
                            canister_station_dict[each_canister] = pack_station_dict[ordered_pack]
                            canister_order_no_dict[each_canister] = order_no
                            order_no += 1

        return canister_station_dict, canister_order_no_dict, order_no

    except Exception as e:
        logger.error("Error in assign_order_number_sorted_by_date {}".format(e))
        return None, None, None


@log_args_and_response
def assign_trolley_location_to_mfd_canisters(assigned_trolley_batch,
                                             drawer_location_info,
                                             pack_station_dict,
                                             pack_canister_dict,
                                             pack_order_no_date_dict,
                                             mfd_pack_patient_dict,
                                             patient_mfd_canister_slot_pack_dict,
                                             system_id, batch_skipped):
    """
    assigned trolley batch = dict
    drawer_location_info = dict
    @return:
    """
    logger.info("In assign_trolley_location_to_mfd_canisters")
    trolley_list = list()
    trolley_sequence = 0
    canister_location_dict = dict()
    order_no = get_max_order_number_from_mfd_analysis()

    progress_batch = get_progress_batch_id(system_id)
    if progress_batch:
        last_sequence = db_get_last_mfd_progress_sequence_for_batch(progress_batch)
        trolley_sequence = last_sequence
    # # todo: batch_less_dev Get last trolley sequence for imported batch
    try:
        for each_batch in assigned_trolley_batch:
            trolley_id, batch_list = each_batch
            # stations = trolley_station_linked[trolley_id]
            trolley_sequence += 1
            logger.info("Trolley sequence {}".format(trolley_sequence))
            canister_station_dict, canister_order_no_dict, order_no = assign_order_number_sorted_by_date(batch_list,
                                                                                                         pack_station_dict,
                                                                                                         order_no,
                                                                                                         pack_order_no_date_dict,
                                                                                                         pack_canister_dict,
                                                                                                         mfd_pack_patient_dict,
                                                                                                         patient_mfd_canister_slot_pack_dict)

            if trolley_id not in trolley_list and trolley_id != 0:
                trolley_list.append(trolley_id)
                drawer_location = deepcopy(drawer_location_info[trolley_id])
                drawer_ids = deepcopy(list(drawer_location.keys()))
                for batch_data in batch_list:
                    quad_canister = batch_data["quad_canister"]

                    for quad, canister_set in quad_canister.items():
                        current_drawer = drawer_ids.pop(0)
                        location_ids = deepcopy(list(drawer_location[current_drawer]))
                        for canister in canister_set:
                            if batch_skipped:
                                canister_location_dict[canister] = (
                                    None, None, canister_order_no_dict[canister], trolley_sequence, None)
                            else:
                                canister_location_dict[canister] = (location_ids.pop(0),
                                                                    trolley_id,
                                                                    canister_order_no_dict[canister],
                                                                    trolley_sequence,
                                                                    canister_station_dict[canister])

            else:
                logger.info("Trolley reuse for id {}".format(trolley_id))
                for batch_data in batch_list:
                    quad_canister = batch_data["quad_canister"]
                    for quad, canister_set in quad_canister.items():
                        for canister in canister_set:
                            if batch_skipped:
                                canister_location_dict[canister] = (
                                    None, None, canister_order_no_dict[canister], trolley_sequence, None)
                            else:
                                canister_location_dict[canister] = (None,
                                                                    trolley_id,
                                                                    canister_order_no_dict[canister],
                                                                    trolley_sequence,
                                                                    canister_station_dict[canister])

        return canister_location_dict

    except InternalError as e:
        logger.error(e)
        raise


@log_args_and_response
def get_device_wise_mini_batches(mfd_canister_destination_dict,
                                 pack_quadrant_canister_dict,
                                 pack_order_no_date_dict,
                                 pack_travelled_dict,
                                 pack_device_dict,
                                 canister_pack_dict):
    """
    Function to assign canisters to trolley according to quad wise device capacity
    and trolley drawers.
    @return: mini_batch: dict
    """
    logger.info("In get_device_wise_mini_batches")
    try:
        device_ids = list(mfd_canister_destination_dict.keys())
        pack_ids = list(pack_order_no_date_dict.keys())
        temp_pack_list = deepcopy(pack_ids)
        mini_batch = {device: list() for device in device_ids}
        device_quad_capacity = {device: {1: 0, 2: 0, 3: 0, 4: 0} for device in device_ids}
        pack_list = list()
        mini_batch_pack_list = dict()
        pack_to_transfer_manual = set()

        # get enable mfd location count group by device and quadrant
        mfd_quad_loc_capacity_dict = get_mfd_drawer_quad_capacity_count(device_list=device_ids)

        while not len(pack_ids) == len(pack_list) + len(pack_to_transfer_manual):

            continue_while = False
            pack = temp_pack_list[0]
            device_id = pack_device_dict[pack]
            if device_id not in mfd_quad_loc_capacity_dict:
                mfd_quad_loc_capacity_dict[device_id] = {1: 0, 2: 0, 3: 0, 4: 0}
            if device_id not in mini_batch_pack_list.keys():
                mini_batch_pack_list[device_id] = list()
            quad_canister = pack_quadrant_canister_dict[pack]

            if not pack_travelled_dict[pack]:
                # considering both packs are to be filled from same device
                similar_packs = get_same_canister_packs(pack_quadrant_canister_dict, canister_pack_dict, {pack})
                if len(similar_packs) > 1:
                    # merge quad count of similar canister packs
                    updated_quad_canister = get_merged_quad_canister_data(similar_packs, pack_quadrant_canister_dict)
                    temp_quad = {1: 0, 2: 0, 3: 0, 4: 0}
                    use_pack = True

                    for each_quad, can_set in updated_quad_canister.items():
                        if each_quad not in mfd_quad_loc_capacity_dict[device_id]:
                            mfd_quad_loc_capacity_dict[device_id][each_quad] = 0
                        if len(can_set) > mfd_quad_loc_capacity_dict[device_id][each_quad]:
                            logger.error("Error while assigning can to quad {}, {}, {}".format(updated_quad_canister,
                                                                                               similar_packs,
                                                                                               mfd_quad_loc_capacity_dict))
                            pack_to_transfer_manual.update(similar_packs)
                            for each_pack in similar_packs:
                                pack_travelled_dict[each_pack] = True
                                temp_pack_list.remove(each_pack)
                            continue_while = True
                            break

                    if continue_while:
                        continue

                    for quad, canister_set in updated_quad_canister.items():
                        if use_pack:
                            if device_quad_capacity[device_id][quad] + len(
                                    canister_set) <= mfd_quad_loc_capacity_dict[device_id][quad]:
                                temp_quad[quad] += len(canister_set)
                            else:
                                temp_quad = {1: 0, 2: 0, 3: 0, 4: 0}
                                use_pack = False

                    if use_pack:
                        for each_pack in similar_packs:
                            pack_travelled_dict[each_pack] = True
                            temp_pack_list.remove(each_pack)
                        for quad, capacity in temp_quad.items():
                            device_quad_capacity[device_id][quad] += capacity
                        mini_batch_pack_list[device_id].extend(list(similar_packs))
                        pack_list.extend(list(similar_packs))

                    else:
                        mini_batch[device_id].append(mini_batch_pack_list[device_id])
                        device_quad_capacity[device_id] = {1: 0, 2: 0, 3: 0, 4: 0}
                        mini_batch_pack_list[device_id] = list()

                else:
                    temp_quad = {1: 0, 2: 0, 3: 0, 4: 0}
                    use_pack = True

                    for each_quad, can_set in quad_canister.items():
                        if each_quad not in mfd_quad_loc_capacity_dict[device_id]:
                            mfd_quad_loc_capacity_dict[device_id][each_quad] = 0
                        if len(can_set) > mfd_quad_loc_capacity_dict[device_id][each_quad]:
                            logger.error("Error while assigning can to quad {}, {}, {}".format(quad_canister,
                                                                                               similar_packs,
                                                                                               mfd_quad_loc_capacity_dict))
                            pack_to_transfer_manual.add(pack)
                            pack_travelled_dict[pack] = True
                            temp_pack_list.remove(pack)
                            continue_while = True
                            break

                    if continue_while:
                        continue

                    for quad, canister_set in quad_canister.items():
                        if use_pack:
                            if device_quad_capacity[device_id][quad] + len(
                                    canister_set) <= mfd_quad_loc_capacity_dict[device_id][quad]:
                                temp_quad[quad] += len(canister_set)
                            else:
                                temp_quad = {1: 0, 2: 0, 3: 0, 4: 0}
                                use_pack = False

                    if use_pack:
                        pack_travelled_dict[pack] = True
                        temp_pack_list.remove(pack)
                        pack_list.append(pack)
                        mini_batch_pack_list[device_id].append(pack)
                        for quad, capacity in temp_quad.items():
                            device_quad_capacity[device_id][quad] += capacity

                    else:
                        mini_batch[device_id].append(mini_batch_pack_list[device_id])
                        device_quad_capacity[device_id] = {1: 0, 2: 0, 3: 0, 4: 0}
                        mini_batch_pack_list[device_id] = list()

        # todo take pack list device wise
        for device, packs in mini_batch_pack_list.items():
            if len(packs):
                mini_batch[device].append(mini_batch_pack_list[device])

        return mini_batch, pack_to_transfer_manual

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_device_wise_mini_batches {}".format(e))
        raise

    except Exception as e:
        logger.error("Error in get_device_wise_mini_batches {}".format(e))
        return None, None


@log_args_and_response
def get_merged_quad_canister_data(similar_packs, pack_quadrant_canister_dict):
    """
    Function to merge quad count of similar canister packs
    @param similar_packs: list
    @param pack_quadrant_canister_dict: dict
    @return: quad_canister: dict
    """
    quad_canister = dict()
    for pack in similar_packs:
        temp_quad_canister = pack_quadrant_canister_dict[pack]
        for quad, canister_set in temp_quad_canister.items():
            if quad not in quad_canister:
                quad_canister[quad] = set()
            quad_canister[quad].update(canister_set)

    return quad_canister


def get_same_canister_packs(pack_quadrant_canister_dict, canister_pack_dict, pack):
    """
    Return list of packs to be filled from same mfd canisters
    @param pack_quadrant_canister_dict:
    @param pack:
    @return:
    @param canister_pack_dict: dict,
            pack_quadrant_canister_dict: dict
            pack : int
    @return: packs: list
    """
    try:
        canister_list = list()
        for each_pack in pack:
            canister_list.extend(list(pack_quadrant_canister_dict[each_pack].values()))
        packs = set()
        for canister_set in canister_list:
            for canister in canister_set:
                packs.update(canister_pack_dict[canister])

        if len(packs) > len(pack):
            return get_same_canister_packs(pack_quadrant_canister_dict, canister_pack_dict, packs)
        else:
            return packs

    except Exception as e:
        logger.error(e)
        return error(1001, "Error in getting similar canister packs.")


@validate(required_fields=['batch_id', 'analysis_id', 'user_id', 'system_id', 'company_id'])
def get_similar_canister(request_args):
    """
    returns canister data which has same drugged and same quantity of drug in every slot of canister
    :param request_args: dict
    :return: json
    """
    batch_id = request_args['batch_id']
    analysis_id = request_args['analysis_id']
    user_id = request_args['user_id']
    company_id = request_args['company_id']
    system_id = request_args['system_id']

    try:
        try:
            mfs_id = get_mfs_data_by_system_id(system_id)
        except ValueError as e:
            return error(1020, '{}.'.format(str(e)))
        similar_canister_analysis_ids = get_similar_canister_analysis_ids(company_id, user_id, analysis_id, batch_id,
                                                                          mfs_id)
        if not similar_canister_analysis_ids:
            return error(1020, 'Unable to find similar canister for particular canister.')
        canister_data, ndc_list = db_get_canister_data(batch_id, user_id, mfs_id, list(similar_canister_analysis_ids))
        return create_response(canister_data)
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_similar_canister: {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=['batch_id', 'trolley_id', 'system_id', 'user_id', 'company_id'])
def update_scanned_trolley(request_args):
    """
    updates couch-db doc with trolley_scan_required status if currently scanned trolley is valid
    :param request_args: dict
    :return: json
    """
    logger.info('ScanTrolley: {}'.format(request_args))
    trolley_serial_number = request_args['trolley_id']
    batch_id = request_args['batch_id']
    system_id = request_args['system_id']
    company_id = request_args['company_id']

    try:
        trolley_id = get_device_id_from_serial_number(trolley_serial_number, company_id)
        logger.info("trolley_id {}".format(trolley_id))

        if not trolley_id:
            return error(1001, "Missing Parameter(s): trolley_id or Invalid trolley.")

        status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                      system_id=system_id)
        couch_db_doc = document.get_document()

        couch_db_data = couch_db_doc.get('data', {})
        required_trolley_id = couch_db_data.get('trolley_id', None)
        current_batch_id = couch_db_data.get('batch_id', None)
        logger.info('required_trolley: {} and trolley_scanned: {} for system: {} and batch: {}'
                     .format(required_trolley_id, trolley_id, system_id, current_batch_id))
        if current_batch_id != batch_id:
            return error(1020, 'Invalid batch_id.')
        if required_trolley_id != trolley_id:
            return error(1020, 'Invalid Trolley scanned.')

        trolley_data = {'trolley_scan_required': False}
        logger.info('updating trolley_scan_required to false for {}'.format(system_id))
        status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                  system_id, trolley_data)
        logger.info("In update_scanned_trolley: status: {}, doc: {}".format(status, doc))

        module_data = {
            'batch_id': current_batch_id,
            'trolley_scanned': True,
            'current_module': constants.MFD_MODULES['SCHEDULED_BATCH']
        }
        status, doc = update_mfd_module_couch_db(constants.CONST_MFD_PRE_FILL_DOC_ID, system_id,
                                                  module_data)

        return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error("error in update_scanned_trolley: {}".format(e))
        return error(2001)


@validate(required_fields=['batch_id', 'system_id', 'user_id', 'company_id'])
def stop_filling(request_args):
    """
    updates couch db doc if user stops filling via update_timer flag
    :param request_args: dict
    :return: json
    """
    system_id = request_args['system_id']
    user_id = request_args['user_id']

    try:
        trolley_data = dict()
        trolley_data['update_timer'] = False
        trolley_data['user_id'] = user_id
        trolley_data['stop_timestamp'] = get_current_date_time()
        status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID, system_id,
                                                  trolley_data)
        return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error("error in stop_filling: {}".format(e))
        return error(2001)


@validate(required_fields=['system_id', 'user_id', 'company_id'])
def resume_filling(request_args):
    """
    updates couch db doc if user resumes filling via update_timer flag
    :param request_args:
    :return:
    """
    system_id = request_args['system_id']
    user_id = request_args['user_id']

    try:
        trolley_data = dict()
        trolley_data['update_timer'] = True
        trolley_data['user_id'] = user_id
        status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID, system_id,
                                                  trolley_data)
        return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error("error in resume_filling: {}".format(e))
        return error(2001)


@validate(required_fields=['batch_id', 'drawer_id', 'system_id', 'user_id', 'company_id'])
def scan_drawer(request_args):
    """
    updates couch-db with currently scanned drawer
    :param request_args: dict
    :return: json
    """
    # batch_id = request_args['batch_id']
    drawer_serial_number = request_args['drawer_id']
    system_id = request_args['system_id']
    user_id = request_args['user_id']
    company_id = request_args['company_id']
    # pack_ids = list()

    try:
        status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                      system_id=system_id)
        couch_db_doc = document.get_document()

        couch_db_data = couch_db_doc.get('data', {})
        # required_trolley_id = couch_db_data.get('trolley_id', None)
        # current_batch_id = couch_db_data.get('batch_id', None)
        trolley_scan_required = couch_db_data.get("trolley_scan_required", True)
        if trolley_scan_required:
            return error(1020, 'Please scan trolley.')

        drawer_id = get_drawer_id_from_serial_number(drawer_serial_number, company_id)
        logger.info("drawer_id {}".format(drawer_id))
        if not drawer_id:
            return error(1001, "Missing Parameter(s): drawer_id or Invalid drawer.")

        logger.info('in scan drawer:')
        trolley_data = dict()
        # todo: check weather the drawer is valid or not
        trolley_data['user_id'] = user_id

        drawer_data = couch_db_data.get("drawer_data", [])
        current_analysis_ids = couch_db_data.get("current_analysis_ids", [])
        if current_analysis_ids:
            if drawer_data:
                if drawer_id == drawer_data[0]:
                    trolley_data['scanned_drawer'] = drawer_id
                else:
                    return error(1020, 'Invalid drawer for transfer')
            else:
                return error(1020, 'No scan required')
        else:
            trolley_data['scanned_drawer'] = None
        trolley_data['drawer_data'] = drawer_data

        logger.info('couch_db_doc_update_at_scan_drawer_time:' + str(trolley_data))
        status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                  system_id, trolley_data)
        return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error("error in scan_drawer: {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=['analysis_ids', 'user_id', 'company_id', 'system_id', 'action'])
def update_mfd_canister_status(request_args):
    """
    updates canister status for valid actions if drugs are filled or skipped of a particular canister
    :param request_args:
    :return:
    """
    batch_id = request_args.get('batch_id')
    analysis_ids = request_args['analysis_ids']
    user_id = request_args['user_id']
    company_id = request_args['company_id']
    system_id = request_args['system_id']
    action = request_args['action']
    reason = request_args.get('reason', None)
    mark_canister_misplaced = request_args.get('mark_canister_misplaced', False)
    mfd_canister_home_cart_dict = defaultdict(list)
    canister_history_update_list = list()
    valid_canister_set = set()
    mfd_misplaced_canister_ids = list()

    valid_actions = ['verification', 'skip', 'fill_at_mvs']
    if action not in valid_actions:
        return error(1020, 'Action is not valid. Valid Actions: {}.'.format(valid_actions))
    try:
        with db.transaction():
            # analysis_ids = list(map(lambda x: int(x), analysis_ids.split(',')))

            if action == 'verification':
                try:
                    mfs_id = get_mfs_data_by_system_id(system_id)
                except ValueError as e:
                    return error(1020, '{}.'.format(str(e)))
                status_id = constants.MFD_CANISTER_VERIFIED_STATUS
                analysis_ids, analysis_details_ids = db_get_filled_drug_analysis_ids(company_id, user_id, analysis_ids,
                                                                                     batch_id, mfs_id, action)

                if not analysis_ids:
                    return error(1020)
                status = db_update_canister_status(list(analysis_ids), status_id, user_id, reason)
                return create_response(status)
            elif action == 'skip':
                action_id = None
                valid_drug_status = [constants.MFD_DRUG_FILLED_STATUS,
                                     constants.MFD_DRUG_PENDING_STATUS]
                valid_canister_status = [constants.MFD_CANISTER_FILLED_STATUS,
                                         constants.MFD_CANISTER_PENDING_STATUS,
                                         constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                         constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                         constants.MFD_CANISTER_VERIFIED_STATUS]
                mfd_analysis_ids, mfd_analysis_details_ids = db_get_analysis_details_ids(mfd_analysis_ids=analysis_ids,
                                                                                         canister_status=valid_canister_status,
                                                                                         drug_status=valid_drug_status)
                if not mfd_analysis_ids:
                    return error(1020)
                if mark_canister_misplaced:
                    action_id = constants.MFD_CANISTER_MARKED_MISPLACED
                if mark_canister_misplaced:
                    canister_query = get_mfd_canister_data_by_analysis_ids(list(analysis_ids), company_id)
                    for record in canister_query:
                        if record['home_cart_id']:
                            mfd_misplaced_canister_ids.append(record['mfd_canister_id'])
                            mfd_canister_home_cart_dict[record['home_cart_id']].append(record['mfd_canister_id'])
                            if record['location_id'] is not None:
                                history_dict = {
                                    'mfd_canister_id': record['mfd_canister_id'],
                                    'current_location_id': None,
                                    'user_id': user_id,
                                    'is_transaction_manual': True
                                }
                                canister_history_update_list.append(history_dict)
                        valid_canister_set.add(record['mfd_canister_id'])
                    if len(set(analysis_ids)) != len(valid_canister_set):
                        return error(1020, 'Invalid mfd_canister_id or company_id')

                    # update mfd canister data
                    logger.info('marking_misplaced_mfd_canister_ids: {}'.format(mfd_misplaced_canister_ids))
                    if mfd_misplaced_canister_ids:
                        update_status = mark_mfd_canister_misplaced(mfd_canister_home_cart_dict)

                        if update_status:
                            # update in canister status history
                            db_update_canister_active_status(mfd_canister_home_cart_dict,
                                                             constants.MFD_CANISTER_MARKED_MISPLACED, user_id, reason)
                            # update in transfer history
                            if canister_history_update_list:
                                mfd_canister_history_update = update_mfd_canister_history(canister_history_update_list)
                                logger.info("In update_mfd_canister_status: mfd_canister_history_update: {}".format(
                                    mfd_canister_history_update))

                status = update_rts_data(list(mfd_analysis_details_ids), list(mfd_analysis_ids), company_id=company_id,
                                         user_id=user_id, action_id=action_id, change_rx=False, delete_all_packs=False)
                return create_response(status)
            elif action == 'fill_at_mvs':
                status_id = constants.MFD_CANISTER_MVS_FILLING_REQUIRED
                action_id = None
                if mark_canister_misplaced:
                    action_id = constants.MFD_CANISTER_MARKED_MISPLACED
                status = db_update_canister_status(list(analysis_ids), status_id, user_id, reason, action_id)
                if status:
                    update_mfd_couch_db_notification(analysis_id=list(analysis_ids), user_id=user_id)
                if mark_canister_misplaced:
                    canister_query = get_mfd_canister_data_by_analysis_ids(list(analysis_ids), company_id)
                    for record in canister_query:
                        if record['home_cart_id']:
                            mfd_misplaced_canister_ids.append(record['mfd_canister_id'])
                            mfd_canister_home_cart_dict[record['home_cart_id']].append(record['mfd_canister_id'])
                            if record['location_id'] is not None:
                                history_dict = {
                                    'mfd_canister_id': record['mfd_canister_id'],
                                    'current_location_id': None,
                                    'user_id': user_id,
                                    'is_transaction_manual': True
                                }
                                canister_history_update_list.append(history_dict)
                        valid_canister_set.add(record['mfd_canister_id'])

                    if len(set(analysis_ids)) != len(valid_canister_set):
                        return error(1020, 'Invalid mfd_canister_id or company_id')

                    logger.info('marking_misplaced_mfd_canister_ids: {}'.format(mfd_misplaced_canister_ids))
                    if mfd_misplaced_canister_ids:
                        update_status = mark_mfd_canister_misplaced(mfd_canister_home_cart_dict)

                        if update_status:
                            # update in canister status history
                            db_update_canister_active_status(mfd_canister_home_cart_dict,
                                                             constants.MFD_CANISTER_MARKED_MISPLACED, user_id, reason)
                            # update in transfer history
                            if canister_history_update_list:
                                mfd_canister_history_update = update_mfd_canister_history(canister_history_update_list)
                                logger.info("In update_mfd_canister_status: mfd_canister_history_update: {}".format(mfd_canister_history_update))

            return create_response(status)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@validate(required_fields=['batch_id', 'drawer_id', 'user_id', 'system_id', 'company_id'])
def get_drawer_data(request_args):
    """
    returns canister data which are to be placed in a particular drawer
    :param request_args:
    :return:
    """
    batch_id = request_args['batch_id']
    drawer_id = request_args['drawer_id']
    user_id = request_args['user_id']
    company_id = request_args['company_id']
    system_id = request_args['system_id']

    try:
        try:

            mfs_id = get_mfs_data_by_system_id(system_id)
        except ValueError as e:
            return error(1020, '{}.'.format(str(e)))
        status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                      system_id=system_id)
        couch_db_doc = document.get_document()

        couch_db_data = couch_db_doc.get('data', {})
        current_analysis_ids = couch_db_data.get("current_analysis_ids", [])
        canister_data = couch_db_data.get("canister_data", [])
        drawer_id = drawer_id.split(',')
        mfs_location_number = list()
        for mfs_loc, can_data in canister_data.items():
            if can_data['canister_required']:
                mfs_location_number.append(mfs_loc)
        similar_drawer_analysis_ids = get_similar_drawer_analysis_ids(company_id, user_id, drawer_id, batch_id, mfs_id,
                                                                      current_analysis_ids, mfs_location_number)
        if not similar_drawer_analysis_ids:
            return error(1020, 'No canister for particular drawer.')
        canister_data, ndc_list = db_get_canister_data(batch_id, user_id, mfs_id, list(similar_drawer_analysis_ids), ignore_progress_condition=True)
        return create_response(canister_data)
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_drawer_data: {}".format(e))
        return error(2001)


@log_args_and_response
def get_trolley_wise_batch_data(user_id, batch_id, mfs_id, system_id, trolley_data, update_couch_db):
    """
    updates trolley wise batch data in couch-db doc
    :param user_id: int
    :param batch_id: int
    :param mfs_id: int
    :param system_id: int
    :param trolley_data: dict
    :param update_couch_db: boolean
    :return: dict
    """
    """
        returns pending time for filling the mfd canisters, total canisters assigned to user, pending canisters
         and batch's info and updates couch-db doc based on update_couch_db flag
    """
    try:
        trolley_scan_required = True
        trolley_data['trolley_scan_required'] = trolley_scan_required

        # couch db data added for timer to appear on scan trolley screen
        batch_data = get_batch_data(batch_id)
        pack_ids = list()
        analysis_ids = get_trolley_pending_analysis_ids(batch_id, trolley_data['trolley_id'])
        min_order_no, robot_id = db_get_trolley_first_pack(user_id, analysis_ids, batch_id)
        pack_id_query = get_pack_id_query(min_order_no, batch_id)
        for record in pack_id_query:
            pack_ids.append(record['id'])
        current_batch_processing_time, pending_packs, timer_update, blink_timer = db_get_drop_time([robot_id],
                                                                                                   batch_data.system_id,
                                                                                                   pack_ids)
        # based on the batch status calculates the pending time from batch start to first pack in which mfd canister
        # of the particular trolley is used
        if batch_data.status_id in [settings.BATCH_PENDING, settings.BATCH_ALTERNATE_DRUG_SAVED]:
            if batch_data.scheduled_start_time >= datetime.now():
                time_difference = (batch_data.scheduled_start_time - datetime.now())
                seconds_dif = time_difference.total_seconds()
                current_batch_processing_time += int(seconds_dif)
        trolley_data['time_pending'] = current_batch_processing_time
        trolley_data['update_timer'] = True
        trolley_data['batch_id'] = int(batch_id)
        trolley_data['batch_name'] = batch_data.name
        trolley_data['user_id'] = user_id
        trolley_data['pack_manual_delete'] = False
        # trolley_data['timestamp'] = get_current_date_time()
        trolley_data['timestamp'] = datetime_handler(get_datetime())
        batch_ids = [batch_id]

        # gets the pending and total canister of batch for live time update for user
        query_2 = db_get_mfd_batch_info(batch_ids=batch_ids, user_id=user_id, mfs_id=mfs_id)
        for record in query_2:
            trolley_data['total_canisters'] = int(record['total_canister'])
            trolley_data['filled_canisters'] = int(record['filled_canister'])

        # updates mfd batch status to in progress
        if batch_data.mfd_status_id in [constants.MFD_BATCH_PENDING, constants.MFD_BATCH_PRE_SKIPPED]:
            # mark batch mfd status in progress
            batch_update_status = db_update_mfd_status(batch=batch_id, mfd_status=constants.MFD_BATCH_IN_PROGRESS, user_id=1)
            logger.info("In get_trolley_wise_batch_data: batch_update_status: {}".format(batch_update_status))
        if update_couch_db:
            trolley_data['new_data_added'] = False
            status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                      system_id, trolley_data)
            logger.info("In get_trolley_wise_batch_data: status: {}, doc: {}".format(status, doc))
        return trolley_data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def get_location_data_for_couch_db(location_number_list, max_location_number):
    canister_data = dict()
    for i in range(1, max_location_number+1):
        canister_data[i] = {
            "canister_required": i in location_number_list,
            "current_canister_id": None,
            "required_canister_id": None,
            "error_message": None,
            "is_in_error": False,
            "transfer_done": False,
            "message_location": None
        }
    return canister_data


@log_args_and_response
@validate(required_fields=["batch_id", "user_id", "company_id"])
def get_mfd_filling_canister(dict_batch_info):
    """
    returns trolley scan info if required and if trolley is scanned then returns canister placement info for MFS.
    @param dict_batch_info: dict
    :return: json
    """
    batch_id = dict_batch_info.get('batch_id', None)
    user_id = dict_batch_info['user_id']
    company_id = dict_batch_info['company_id']
    system_id = dict_batch_info['system_id']
    trolley_seq = dict_batch_info.get('trolley_seq', None)
    # trolley_scan_required = False
    # scanned_trolley = None
    couch_db_trolley_scan_required = True
    # if function is called to get the data only and not to update cdb(Not reflected on front end)
    update_cdb = dict_batch_info.get('update_cdb', True)
    pending_trolley_seq = False
    try:
        with db.transaction():
            try:
                mfs_id = get_mfs_data_by_system_id(system_id)
            except ValueError as e:
                if not update_cdb:
                    return False, {}
                return error(1020, '{}.'.format(str(e)))

            # if any current canister-data on mfs then return the data
            canister_data, ndc_list = db_get_canister_data(batch_id, user_id, mfs_id)
            change_ndc_drug_list = get_available_drugs_for_recommended_canisters(ndc_list)
            change_ndc_drug_list = [x.zfill(11) for x in change_ndc_drug_list]
            if canister_data:
                for analysis_id, data in canister_data.items():
                    can_slot_data = data['can_slot_data']
                    for can_slot_num, slot_data in can_slot_data.items():
                        for item in slot_data:
                            item['change_ndc_available'] = True if item['ndc'] in change_ndc_drug_list else False
                if not update_cdb:
                    return False, {}
                cdb_data_update: dict = dict()
                cdb_data_update['new_data_added'] = False
                status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID, system_id,
                                                          cdb_data_update)
                logger.info("In get_mfd_filling_canister: status: {}, doc: {}".format(status, doc))
                return create_response(canister_data)

            # Fetch couch db data to check if there is any error pending
            status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                          system_id=system_id)
            couch_db_doc = document.get_document()

            logger.info("couch_db_data_mfs: " + str(couch_db_doc))
            couch_db_data = {}
            if couch_db_doc:
                couch_db_data = couch_db_doc.get("data", {})
            logger.info('checking_pending_error')
            if couch_db_data and update_cdb:
                # if any current canister-data on mfs then return the data
                pending_error = False
                canister_data = couch_db_data.get("canister_data", {})
                for can_data in canister_data.values():
                    pending_error = pending_error or can_data['is_in_error']
                if pending_error:
                    if not update_cdb:
                        return False, {}
                    return create_response(err[13002])

            # gets the trolley information required for canister placement on MFS for the given user. If no trolley data
            # found then either user has not been assigned any canisters or canisters are filled.
            if trolley_seq:
                # check if current trolley seq is pending or not
                pending_trolley_seq = get_trolley_seq_fill_status(trolley_seq, batch_id)
            if pending_trolley_seq:
                trolley_data = db_get_first_trolley_id(batch_id, user_id, mfs_id, trolley_seq)
            else:
                trolley_data = db_get_first_trolley_id(batch_id, user_id, mfs_id)
            if not trolley_data:
                reuse_required = check_trolley_reuse_required(batch_id, user_id, mfs_id)
                # For front end to wait for trolley to get empty and reassign for filling.
                if reuse_required:
                    if not update_cdb:
                        return True, {}
                    return error(13005)
                else:
                    if not update_cdb:
                        return True, {}
                    return create_response(True)

            logger.info(trolley_data)
            if couch_db_data:
                scanned_trolley = couch_db_data.get('trolley_id', None)
                couch_db_trolley_scan_required = couch_db_data.get('trolley_scan_required', True)
            else:
                scanned_trolley = None
            if couch_db_trolley_scan_required:
                # if couch db has trolley information as required then don't update couch-db data and return trolley
                # information else update the couch-db trolley data and return trolley information
                if scanned_trolley != trolley_data['trolley_id']:
                    update_trolley_cdb = True
                    if not update_cdb:
                        update_trolley_cdb = False
                    trolley_data = get_trolley_wise_batch_data(user_id, batch_id, mfs_id, system_id,
                                                               trolley_data, update_trolley_cdb)
                    if not update_cdb:
                        return True, trolley_data
                    return create_response(trolley_data)
                else:
                    trolley_data = get_trolley_wise_batch_data(user_id, batch_id, mfs_id, system_id,
                                                               trolley_data, False)
                    if not update_cdb:
                        return True, trolley_data
                    return create_response(trolley_data)
                logger.info("Inside get_mfd_filling_canister, trolley_data {}".format(trolley_data))
            else:
                trolley_seq = couch_db_data.get('trolley_seq', None)
                if not trolley_seq:
                    if not update_cdb:
                        logger.info('missing_trolley_seq')
                        return False, {}
                    return error(1020, 'Missing trolley seq')
                if scanned_trolley != trolley_data['trolley_id'] or trolley_seq != trolley_data['trolley_seq']:
                    update_trolley_cdb = True
                    if not update_cdb:
                        update_trolley_cdb = False
                    trolley_data = get_trolley_wise_batch_data(user_id, batch_id, mfs_id, system_id,
                                                               trolley_data, update_trolley_cdb)
                    if not update_cdb:
                        return True, trolley_data
                    return create_response(trolley_data)
                else:
                    clauses = []
                    filter_fields = {'home_cart_id': scanned_trolley}
                    paginate = {'page_number': 1, 'number_of_rows': 1}
                    try:
                        results, rts_count = db_get_rts_required_canisters(company_id=company_id,
                                                                           filter_fields=filter_fields,
                                                                           sort_fields=[],
                                                                           paginate=paginate,
                                                                           clauses=clauses,
                                                                           trolley_seq=trolley_seq,
                                                                           batch_id=batch_id)

                        if rts_count:
                            if not update_cdb:
                                return True, {}
                            return error(13007)
                    except ValueError as e:
                        logger.error("error in get_mfd_filling_canister: {}".format(e))
                        if not update_cdb:
                            logger.info('got_valued_error')
                            return True, {}
                        return error(1020, 'Invalid data for rts')
                    if couch_db_data:
                        if couch_db_data.get("canister_data", None):
                            pending_error = False
                            canister_data = couch_db_data.get("canister_data", {})
                            if update_cdb:
                                for can_data in canister_data.values():
                                    pending_error = pending_error or can_data['is_in_error']
                                if pending_error:
                                    return create_response(err[13002])
                    analysis_ids = get_trolley_pending_analysis_ids(batch_id, trolley_data['trolley_id'], user_id)
                    patient_hoa_dict, min_order_no = db_get_patient_info(analysis_ids)
                    location_mapping = db_get_location_info(mfs_id, 16)
                    analysis_id_list, location_number_list = map_mfs_location(patient_hoa_dict, min_order_no,
                                                                              location_mapping, company_id, user_id,
                                                                              batch_id, mfs_id)
                    status = update_in_progress_canister(analysis_id_list, location_number_list, user_id)
                    logger.info("In get_mfd_filling_canister: status: {}".format(status))
                    couch_db_location_data = get_location_data_for_couch_db(location_number_list, 16)
                    data = {'canister_data': couch_db_location_data, 'current_analysis_ids': analysis_id_list}
                    status = db_add_current_filling_data(analysis_id_list, batch_id, mfs_id)
                    logger.info("In get_mfd_filling_canister: status: {}".format(status))
                    if not update_cdb:
                        return True, data
                    data['new_data_added'] = False
                    status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID, system_id,
                                                              data)
                    logger.info("In get_mfd_filling_canister:update_mfs_data_in_couch_db status: {}, doc: {}".format(status, doc))
                    canister_data, ndc_list = db_get_canister_data(batch_id, user_id, mfs_id, analysis_id_list)
                    change_ndc_drug_list = get_available_drugs_for_recommended_canisters(ndc_list)
                    change_ndc_drug_list = [x.zfill(11) for x in change_ndc_drug_list]
                    for analysis_id, data in canister_data.items():
                        can_slot_data = data['can_slot_data']
                        for can_slot_num, slot_data in can_slot_data.items():
                            for item in slot_data:
                                item['change_ndc_available'] = True if item['ndc'] in change_ndc_drug_list else False
                    return create_response(canister_data)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        if not update_cdb:
            raise e
        return error(2001)


@validate(required_fields=['company_id'])
def get_mfs_data(request_args):
    """
    returns active manual fill stations of a company and number of canisters to be filled on that MFS
    :param request_args: dict
    :return: json
    """
    company_id = request_args['company_id']
    system_id = request_args['system_id']
    check_user_assigned = request_args.get('check_user_assigned', False)
    batch_id = request_args.get('batch_id')
    mfs_data = dict()

    try:
        if check_user_assigned:
            batch_data = get_batch_data(batch_id)
            logger.info(f"In get_mfs_data, batch : {batch_id}, status: {batch_data.status.id}")
            if int(batch_data.status.id) != settings.BATCH_IMPORTED:
                return error(14017)

            system_id_for_robot = get_system_id_based_on_device_type(company_id=company_id,
                                                                     device_type_id=settings.DEVICE_TYPES["ROBOT"])
            progress_batch = get_progress_batch_id(system_id_for_robot)
            if progress_batch:
                pending_trolley_sequence = db_get_mfd_pending_sequence_for_batch(progress_batch)
                if not pending_trolley_sequence:
                    return error(21009, "Please wait, The page is refreshing")
                is_user_assign_pending = check_user_in_progress_batch(progress_batch)
                if not is_user_assign_pending:
                    return error(1004, "User already assigned")

        mfs_data_query = db_get_mfs_data(company_id, system_id)
        if not mfs_data_query:
            return create_response([])
        for record in mfs_data_query:
            if record['device_id'] not in mfs_data:
                mfs_data[record['device_id']] = {'device_id': record['device_id'],
                                                 'device_name': record['device_name'],
                                                 'associated_device': record['associated_device'],
                                                 'serial_number': record['serial_number'],
                                                 'system_id': record['system_id'],
                                                 'user_canister_count': list()}
            user_data = {'user_id': record['assigned_to'],
                         'pending_canister_count': record['pending_canister']}
            mfs_data[record['device_id']]['user_canister_count'].append(user_data)

        return create_response(list(mfs_data.values()))
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_mfs_data: {}".format(e))
        return error(2001)


def get_mfd_batch_data_per_mfs(info_dict):
    """
    returns manual fill station wise data of batch, user and trolley association
    :param info_dict: dict
    :return: json
    """
    batch_data = list()
    # user_id = info_dict['user_id']
    # company_id = info_dict['company_id']
    batch_id = info_dict['batch_id']
    try:
        batch_ids = [batch_id]

        query = db_get_mfd_batch_info(batch_ids=batch_ids, mfs_wise_data=True)

        for record in query:
            batch_data.append(record)

        return create_response(batch_data)

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return error(2001)


@validate(required_fields=['user_id', 'company_id', 'device_id'])
def disable_canister_location_transfer(request_args):
    """
    disables canister location and if canister is placed on that location then returns transfer data for that canister
    :param request_args:
    :return:
    """
    # user_id = request_args['user_id']
    company_id = request_args['company_id']
    device_id = request_args['device_id']
    display_locations = request_args.get('display_locations', None)
    mfd_canister_loc_info = request_args.get('mfd_canister_loc_info', None)
    if not mfd_canister_loc_info and not display_locations:
        return error(1020, 'Argument missing')
    transfer_data = dict()

    try:
        with db.transaction():
            valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
            if not valid_device:
                return error(1033)

            if display_locations:
                # display_locations = display_locations.split(",")
                transfer_data = disable_canister_location_transfer_by_display_location({
                    'display_locations': display_locations,
                    'device_id': device_id
                })
            elif mfd_canister_loc_info:
                transfer_data_from_ids = disable_canister_location_transfer_by_canister_ids({
                    'mfd_canister_info': mfd_canister_loc_info,
                    'device_id': device_id,
                    'company_id': company_id
                })
                transfer_data.update(transfer_data_from_ids)
            return create_response(transfer_data)
    except NoLocationExists as e:
        return error(1020, str(e))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@validate(required_fields=['device_id', 'display_locations'])
def disable_canister_location_transfer_by_display_location(request_args):
    """
    disables canister location and if canister is placed on that location then returns transfer data for that canister
    :param request_args:
    :return:
    """
    device_id = request_args['device_id']
    display_locations = request_args['display_locations']
    exclude_locations = display_locations
    transfer_data = dict()

    try:
        with db.transaction():
            location_mfd_can_data = location_mfd_can_info(device_id, display_locations)

            for mfd_can_loc in location_mfd_can_data:
                if mfd_can_loc['mfd_canister_id']:
                    canister_transfer_data = get_transfer_data(device_id, mfd_can_loc['display_location'],
                                                               mfd_can_loc, mfd_can_loc['loc_id'], exclude_locations)
                    transfer_data[mfd_can_loc['display_location']] = canister_transfer_data

            return transfer_data
    except NoLocationExists as e:
        return error(1020, str(e))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@validate(required_fields=['device_id', 'mfd_canister_info'])
def disable_canister_location_transfer_by_canister_ids(request_args):
    """
    disables canister location and if canister is placed on that location then returns transfer data for that canister
    :param request_args:
    :return:
    """
    device_id = request_args['device_id']
    mfd_canister_info = request_args['mfd_canister_info']
    company_id = request_args['company_id']
    transfer_data = dict()
    display_location_id = dict()

    try:
        with db.transaction():
            mfd_canister_ids = list(mfd_canister_info.keys())
            exclude_locations = list(mfd_canister_info.values())
            location_mfd_can_data_by_mfd_can_id = get_mfd_canister_data_by_ids(mfd_canister_ids, company_id)
            loc_from_display_info = location_mfd_can_info(device_id, list(mfd_canister_info.values()))
            for record in loc_from_display_info:
                display_location_id[record['display_location']] = record['loc_id']

            for mfd_can_loc in location_mfd_can_data_by_mfd_can_id:
                if mfd_can_loc['mfd_canister_id']:
                    canister_transfer_data = get_transfer_data(device_id, mfd_canister_info[str(mfd_can_loc['mfd_canister_id'])],
                                                               mfd_can_loc, display_location_id[mfd_canister_info[str(mfd_can_loc['mfd_canister_id'])]], exclude_locations)
                    transfer_data[mfd_canister_info[str(mfd_can_loc['mfd_canister_id'])]] = canister_transfer_data

            return transfer_data
    except NoLocationExists as e:
        return error(1020, str(e))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=['system_id', 'company_id'])
def update_pack_delete_manual_status(request_args):
    """
    updates couch-db doc and marks pop-flag to false
    :param request_args: dict
    :return: json
    """
    system_id = request_args['system_id']
    company_id = request_args['company_id']
    reset_rts_for_transfer = request_args.get('reset_rts_for_transfer', False)
    update_wizard = False
    module_to_update = False
    try:
        if not reset_rts_for_transfer:
            mfs_data = {'pack_manual_delete': False}
            status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID, system_id,
                                                      mfs_data)
            return create_response(status)
        else:
            batch_id = request_args['batch_id']
            trolley_id = request_args['trolley_id']
            device_id = request_args['device_id']
            rts_data = {'rts_changes': False}
            # if while deleting/marking packs manual all the canisters of trolley are marked as RTS then updating wizard
            transfer_to_robot_done, rts_canister_in_robot = check_module_update(device_id, batch_id, [trolley_id])
            if not transfer_to_robot_done:
                logger.info('checking_module_update on rts refresh for Batch: {} Trolley: {} Canister_required for '
                            'transfer in robot so passing module update'.format(batch_id, trolley_id))
            else:
                if rts_canister_in_robot:
                    rts_data.update({"scanned_drawer": None,
                                     "scanned_trolley": None,
                                     "currently_scanned_drawer_sr_no": None,
                                     "previously_scanned_drawer_sr_no": None,
                                     "timestamp": get_current_date_time(),
                                     "uuid": uuid1().int})
                    update_wizard = True
                    module_to_update = constants.MFD_TRANSFER_WIZARD_MODULES["RTS_SCREEN_WIZARD"]
            status = update_mfd_transfer_couch_db(device_id, system_id, rts_data)
            if update_wizard:
                update_couch_db_mfd_canister_wizard(company_id=company_id,
                                                    device_id=device_id,
                                                    module_id=module_to_update,
                                                    batch_id=batch_id,
                                                    mfd_transfer_to_device=False)
            return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error("error in update_pack_delete_manual_status: {}".format(e))
        return error(2001)


def get_mfd_notification_info(system_id: int = None, device_id: int = None):

    """
    To check if mfd canister transfer is pending or mfd canister filling is pending
    @param system_id:
    @param system_id:
    @param device_id:
    @param batch_id: int
    @return status
    """
    # this function is changed assuming there can be a gap in time when both the robots require mfd canisters.
    try:
        mfd_notification_data = mfd_transfer_notification_for_batch(device_id=device_id)
        mfs_message_filling_device_ids = dict()
        mfs_message_transfer_device_ids = dict()
        notification_filling_pending_device = set()
        notification_transfer_pending_device = set()
        device_data = get_device_data_by_device_id_dao(device_id=device_id)
        device_name = device_data.name
        for record in mfd_notification_data:
            # to check for pending filling device
            if record['status_id'] in [constants.MFD_CANISTER_PENDING_STATUS,
                                       constants.MFD_CANISTER_IN_PROGRESS_STATUS] or record['device_type_id'] == \
                    settings.DEVICE_TYPES['Manual Filling Device']:
                if record['mfs_device_id'] not in mfs_message_filling_device_ids:
                    mfs_message_filling_device_ids[record['mfs_device_id']] = record['mfs_system_id']
                    notification_filling_pending_device.add(device_id)

            # to check for pending transfer device
            if record['trolley_location_id'] == record['current_location_id']:
                if record['mfs_device_id'] not in mfs_message_filling_device_ids:
                    mfs_message_transfer_device_ids[record['mfs_device_id']] = record['mfs_system_id']
                    notification_transfer_pending_device.add(device_id)

        logger.info("In get_mfd_notification_info: notification_filling_device_list: {}".format(notification_filling_pending_device))
        logger.info("In get_mfd_notification_info: notification_transfer_device_list: {}".format(notification_transfer_pending_device))

        # filling message for robot
        if notification_filling_pending_device:
            for notification_filling_pending_device in notification_filling_pending_device:
                notification_device_name = db_get_device_name_by_device_id(device_id=notification_filling_pending_device)
                notification_robot_message = dict()
                notification_message = "The {} is waiting for the manual canisters to be filled to continue processing"\
                    .format(notification_device_name)
                notification_robot_message[device_id] = notification_message
                send_robot_notification_message = Notifications(user_id=None, call_from_client=True) \
                    .send_transfer_notification(user_id=None,
                                                system_id=system_id,
                                                batch_id=batch_id,
                                                device_message=notification_robot_message,
                                                flow='mfd')
                logger.info("In get_mfd_notification_info: send_robot_notification_message: {}".format(send_robot_notification_message))
        # transfer message for robot
        if notification_transfer_pending_device:
            for notification_transfer_pending_device in notification_transfer_pending_device:
                notification_device_name = db_get_device_name_by_device_id(device_id=notification_transfer_pending_device)
                notification_robot_message = {}
                notification_message = "The {} is waiting for the manual canisters to be transferred to continue " \
                                       "processing".format(notification_device_name)

                notification_robot_message[device_id] = notification_message
                send_mfs_notification_message = Notifications(user_id=None, call_from_client=True)\
                    .send_transfer_notification(user_id=None,
                                                system_id=system_id,
                                                batch_id=batch_id,
                                                device_message=notification_robot_message)
                logger.info("In get_mfd_notification_info: send_robot_notification_message: {}".format(
                    send_mfs_notification_message))
        logger.info("In get_mfd_notification_info: mfs_message_filling_device_ids: {}".format(mfs_message_filling_device_ids))
        logger.info("In get_mfd_notification_info: mfs_message_transfer_device_ids: {}".format(mfs_message_transfer_device_ids))
        # filling message for mfs_screen
        if mfs_message_filling_device_ids:
            notification_mfs_message = {}
            for mfs_device_id, mfs_system_id in mfs_message_filling_device_ids.items():
                notification_message = "The {} is waiting for the manual canisters to be filled to continue" \
                                       " processing".format(device_name)
                notification_mfs_message[mfs_device_id] = notification_message
                send_mfs_notification_message = Notifications(user_id=None, call_from_client=True) \
                    .send_transfer_notification(user_id=None,
                                                system_id=mfs_system_id,
                                                batch_id=batch_id,
                                                device_message=notification_mfs_message)
                logger.info("In get_mfd_notification_info: send_robot_notification_message: {}".format(
                    send_mfs_notification_message))
        # transfer message for mfs_screen
        if mfs_message_transfer_device_ids:
            notification_mfs_message = {}
            for mfs_device_id, mfs_system_id in mfs_message_transfer_device_ids:
                notification_message = "The {} is waiting for the manual canisters to be transferred to continue" \
                                       " processing".format(device_name)
                notification_mfs_message[mfs_device_id] = notification_message
                send_mfs_notification_message = Notifications(user_id=None,
                                                              call_from_client=True).send_transfer_notification(
                    user_id=None,
                    system_id=mfs_system_id,
                    batch_id=batch_id,
                    device_message=notification_mfs_message)
                logger.info("In get_mfd_notification_info: send_robot_notification_message: {}".format(
                    send_mfs_notification_message))

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
@validate(required_fields=['system_id'])
def update_transfer_data_mfs(request_args):
    """
    updates couch-db doc for transfer data
    :param request_args: dict
    :return: json
    """
    system_id = request_args['system_id']
    try:
        mfd_data = dict()
        try:
            mfs_id = get_mfs_data_by_system_id(system_id)
        except ValueError as e:
            return error(1020, '{}.'.format(str(e)))
        couch_db_drawer_data = get_mfs_transfer_drawer_data(mfs_id)
        mfd_data['drawer_data'] = couch_db_drawer_data

        logger.info('couch_db_data' + str(mfd_data))
        status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID, system_id,
                                                  mfd_data)
        logger.info("In update_transfer_data_mfs:update_mfs_data_in_couch_db status: {}, doc: {}".format(status, doc))
        return create_response(True)

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_transfer_data_mfs: {}".format(e))
        return error(2001)


def update_user_count_couch_db(request_args):
    """
    updates couch db doc for user access
    :param request_args: dict
    :return: boolean
    """

    try:
        for system_id, system_info in request_args.items():
            mfd_data = {'user_id': system_info['user_id']}
            # module_data = {'user_id': system_info['user_id']}
            batch_id = system_info['batch_id']
            mfs_id = system_info['mfs_id']
            user_id = system_info['user_id']
            query_2 = db_get_mfd_batch_info(batch_ids=[batch_id], user_id=user_id, mfs_id=mfs_id)
            for record in query_2:
                mfd_data['filled_canisters'] = int(record['filled_canister'])
                mfd_data['total_canisters'] = int(record['total_canister'])
            status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID, system_id,
                                                      mfd_data)
            if not status:
                raise RealTimeDBException('Error while updating couch-db')
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return error(2001)


def update_user_in_prefill(request_args):
    """
    updates couch db doc for user access
    :param request_args: dict
    :return: boolean
    """

    try:
        for system_id, user_id in request_args.items():
            module_data = {'user_id': int(user_id) if user_id else None}
            status, couch_db_doc = get_mfd_module_couch_db(constants.CONST_MFD_PRE_FILL_DOC_ID,
                                                           system_id)
            logger.info('current_couch_db_da' + str(couch_db_doc))
            couch_db_data = couch_db_doc.get("data", {})
            if not couch_db_data:
                module_data['current_module'] = constants.MFD_MODULES['SCHEDULED_BATCH']
                module_data['batch_id'] = 0
            status, doc = update_mfd_module_couch_db(constants.CONST_MFD_PRE_FILL_DOC_ID, system_id, module_data)
            if not status:
                raise RealTimeDBException('Error while updating couch-db')
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e)
        return error(2001)


@validate(required_fields=['company_id', 'user_access', 'user_id'])
def update_mfs_user_access(request_args):
    """
    updates user access in auth, assigned user in mfd-analysis for pending canisters, mfs couch-doc and pre-fill
    couch-db doc if its valid data
    :param request_args: dict
    :return:
    """
    company_id = request_args['company_id']
    user_access = request_args['user_access']

    system_ids = list()
    user_ids = list()
    couch_db_update_dict = dict()
    couch_db_user_dict = dict()

    update_mfd_user_assignment = dict()
    user_role = dict()

    for system_id, user_id in user_access.items():
        if system_id:
            system_ids.append(int(system_id))
        if user_id:
            user_ids.append(int(user_id))

    # validation for unique system_ids and user_ids received in request.
    if len(system_ids) != len(set(system_ids)):
        return error(1020, 'Unique systems not found')
    # if len(user_ids) != len(set(user_ids)):
    #     return error(1020, 'Unique users not found')
    # if len(system_ids) != len(user_ids):
    #     return error(1020, 'Length of system and user should match.')
    system_user_access = defaultdict(set)
    company_systems = list()
    try:
        # validate systems against company
        system_data = fetch_systems_by_company(company_id=company_id,
                                               system_type=constants.AUTH_MFS_SYSTEM_TYPE)
        for system_id, system_details in system_data.items():
            if system_details['system_type'] == "MFS":
                company_systems.append(int(system_id))
                if system_id not in system_user_access:
                    system_user_access[system_id] = set()
                user_data = system_details['users']
                for user_info in user_data:
                    if user_info['user_id']:
                        system_user_access[system_id].add(user_info['user_id'])
        mfs_system_mapping = dict()

        if len(set(company_systems).intersection(set(system_ids))) != len(system_ids):
            return error(1020, 'Invalid system for given company')

        # validate users against company
        user_data = fetch_users_by_company(company_id=company_id)
        company_users = list()
        for user_info in user_data:
            company_users.append(user_info['id'])
        if len(set(company_users).intersection(set(user_ids))) != len(user_ids):
            return error(1020, 'Invalid user for given company')

        # check if currently a mfs system has multiple users and return error
        for system, users in system_user_access.items():
            if len(users) > 1:
                return error(1020, 'Multiple user assigned')
            else:
                if users:
                    mfs_system_mapping[system] = int(list(users)[0])
                else:
                    mfs_system_mapping[system] = None

        # dict to check weather after changing the user access it won't result into a user has multiple mfs assigned to
        # him and changes to be done in user roles in auth.
        for system_id, updated_user in user_access.items():
            current_user = mfs_system_mapping[system_id]
            mfs_system_mapping[system_id] = updated_user
            couch_db_user_dict[system_id] = updated_user
            if current_user:
                if current_user in user_role:
                    user_role[current_user].update({
                        'removed_access': system_id,
                        'user_id': current_user,
                        'created_by': request_args['user_id']
                    })
                else:
                    user_role[current_user] = {
                        'removed_access': system_id,
                        'user_id': current_user,
                        'created_by': request_args['user_id']
                    }
            if updated_user:
                if updated_user in user_role:
                    user_role[updated_user].update({
                        'added_access': system_id,
                        'user_id': user_access[system_id],
                        'created_by': request_args['user_id']
                    })
                else:
                    user_role[updated_user] = {
                        'added_access': system_id,
                        'user_id': user_access[system_id],
                        'created_by': request_args['user_id']
                    }

        updated_user_access = defaultdict(set)
        for system, updated_user in mfs_system_mapping.items():
            if updated_user:
                updated_user_access[updated_user].add(system)
                if len(updated_user_access[updated_user]) > 1:
                    return error(1020, 'Invalid user selection. A user has multiple systems')

        # update mfd-analysis
        current_pending_user_data = db_get_current_user_assignment(system_ids)
        for system_id, system_info in current_pending_user_data.items():
            system_id = str(system_id)
            # current_user = system_info['associated_user']
            analysis_ids = system_info['mfd_analysis_ids']
            update_couch_db = system_info['update_couch_db']
            if analysis_ids:
                if user_access[system_id]:
                    update_mfd_user_assignment[user_access[system_id]] = analysis_ids
                    if update_couch_db:
                        couch_db_update_dict[system_id] = {
                            'mfs_id': system_info['mfs_id'],
                            'batch_id': system_info['batch_id'],
                            'user_id': user_access[system_id]
                        }
                else:
                    return error(13009)

        # update user assignment for pending canisters in mfd_analysis.
        if update_mfd_user_assignment:
            db_update_current_user_assignment(update_mfd_user_assignment)

        # update user-access in auth.
        auth_response = update_user_access_in_auth(list(user_role.values()))
        logger.info("In update_mfs_user_access: auth_response: {}".format(auth_response))

        # update couch-db of user for count of canisters.
        if couch_db_update_dict:
            update_user_count_couch_db(couch_db_update_dict)

        # update user in wizard docs.
        if couch_db_user_dict:
            update_user_in_prefill(couch_db_user_dict)

        return create_response(True)

    except RealTimeDBException as e:
        logger.error("error in update_mfs_user_access: {}".format(e))
        return error(11002)
    except (InternalError, IntegrityError) as e:
        logger.error("error in update_mfs_user_access: {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=['system_id', 'device_id', 'message_id_list'])
def update_notification_view_list(request_args):
    """
    updates couch-db doc for transfer data
    :param request_args: dict
    :return: json
    """
    system_id = request_args['system_id']
    device_id = request_args['device_id']
    message_id_list = request_args['message_id_list']
    try:
        notification_status = Notifications().update_transfer_notification_view_list(message_id_list,
                                                                                     system_id,
                                                                                     device_id)
        return create_response(notification_status)

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_notification_view_list: {}".format(e))
        return error(2001)
    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return False, error(1000, "Couch db Document update conflict.")

    except Exception as e:
        logger.error(e, exc_info=True)
        return False, error(1000, "Error while updating couch db doc: " + str(e))


@log_args_and_response
def assign_trolley_location_to_pending_mfd_canisters(trolley_user_quadrant, drawer_location_info):
    """
    @param drawer_location_info:
    @param trolley_user_quadrant:
    """
    mfd_analysis_id_list = list()
    trolley_location_list = list()
    trolley_ids = list(drawer_location_info.keys())
    logger.info("In assign_trolley_location_to_mfd_canisters")
    for trolley_seq, user_assignment_data in trolley_user_quadrant.items():
        drawer_location = drawer_location_info.pop(trolley_ids[0])
        trolley_ids.pop(0)

        drawer_ids = deepcopy(list(drawer_location.keys()))
        for user, quadrant_data in user_assignment_data.items():
            for quad, canister_set in quadrant_data.items():
                current_drawer = drawer_ids.pop(0)
                location_ids = deepcopy(list(drawer_location[current_drawer]))
                for canister in canister_set:
                    mfd_analysis_id_list.append(canister)
                    trolley_location_list.append(location_ids.pop(0))

    return mfd_analysis_id_list, trolley_location_list


@validate(required_fields=['company_id', 'batch_id'])
def update_pending_mfd_assignment(request_args):
    """
    checks unfilled trolley and assigns it for
    :param request_args: dict
    :return: json
    """
    company_id = request_args['company_id']
    batch_id = request_args['batch_id']

    try:
        with db.transaction():
            logger.info('in_update_pending_mfd_assignment_with: {}'.format(request_args))
            trolley_ids, trolley_drawer_data, system_id = get_required_mfd_trolley(company_id, batch_id)
            logger.info('found trolley_ids {} for : {}'.format(trolley_ids, request_args))
            if trolley_drawer_data:
                trolley_user_quadrant = get_recommendation_pending_data(len(trolley_ids), system_id)
                if trolley_user_quadrant:
                    mfd_analysis_ids, trolley_location_ids = assign_trolley_location_to_pending_mfd_canisters(
                        trolley_user_quadrant, trolley_drawer_data)
                    update_status = update_trolley_location(mfd_analysis_ids, trolley_location_ids)
                    logger.info("In update_pending_mfd_assignment: update_trolley_location status: {}".format(update_status))
            return create_response(True)

    except (InternalError, IntegrityError) as e:
        logger.error("Error in update_pending_mfd_assignment {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("Error in update_pending_mfd_assignment {}".format(e))
        return error(0)


@log_args
@validate(required_fields=['system_id', 'next_module', 'user_id'])
def update_mfd_current_module(request_args: dict) -> json:
    """
    updates uer module for mfd after validation
    :param request_args: dict
    :return: json
    """
    try:
        system_id = request_args['system_id']
        next_module = request_args['next_module']
        user_id = request_args['user_id']
        batch_id = request_args.get('batch_id', None)

        status, couch_db_doc = get_mfd_module_couch_db(constants.CONST_MFD_PRE_FILL_DOC_ID,
                                                       system_id)
        if not status:
            return error(11002)
        logger.info('current_couch_db_da' + str(couch_db_doc))
        trolley_scanned = couch_db_doc["data"].get('trolley_scanned', False)
        couch_db_user = couch_db_doc["data"].get('user_id', False)
        if user_id != couch_db_user:
            return error(1020, 'Invalid user')
        if not trolley_scanned:
            if next_module == constants.MFD_MODULES['SCHEDULED_BATCH']:
                module_data = {
                    'current_module': constants.MFD_MODULES['SCHEDULED_BATCH'],
                    'batch_id': 0
                }
            elif next_module == constants.MFD_MODULES['DRUG_LIST']:
                module_data = {
                    'current_module': constants.MFD_MODULES['DRUG_LIST'],
                    'batch_id': batch_id
                }
                batch_data = get_batch_data(batch_id)
                logger.info(f"In update_mfd_current_module, batch : {batch_id}, status: {batch_data.status.id}")
                if int(batch_data.status.id) != settings.BATCH_IMPORTED:
                    return error(14017)
            else:
                return error(1020, 'Invalid module')

            status, doc = update_mfd_module_couch_db(constants.CONST_MFD_PRE_FILL_DOC_ID, system_id,
                                                     module_data)
            logger.info("In update_mfd_current_module: status: {}, doc: {}".format(status, doc))
        return create_response(True)
    except (InternalError, IntegrityError) as e:
        logger.error("error in update_mfd_current_module: {}".format(e))
        return error(2001)


@log_args_and_response
def get_drawer_canister_data(batch_id, device_id, trolley_id):
    """
    Function to get canister data of given device drawer.
    @param batch_id: int
    @param device_id: int
    @param trolley_id: int
    @return: list
    """
    try:
        analysis_location_dict = dict()
        drawer_canister_query = get_drawer_canister_data_query(batch_id, device_id, trolley_id)
        for record in drawer_canister_query:
            if record['status_id'] in constants.MFD_CANISTER_DONE_LIST:
                if record['dest_device_id'] == record['current_device'] and \
                        record['dest_quadrant'] == record['current_quadrant']:
                    analysis_location_dict[record['mfd_analysis_id']] = record['current_location_id']
                else:
                    logger.info('error occurred for canister id {}'.format(record['mfd_canister_id']))
                    raise ValueError('Canister not placed in robot')
            elif record['status_id'] in [constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                         constants.MFD_CANISTER_RTS_REQUIRED_STATUS]:
                if record['source_trolley'] == record['current_device'] and \
                        record['current_drawer_level'] in constants.MFD_TROLLEY_FILLED_DRAWER_LEVEL:
                    continue
                else:
                    logger.info('error occurred for canister id {}'.format(record['mfd_canister_id']))
                    raise ValueError('Canister not placed in trolley')
            else:
                raise ValueError('Invalid status for canister id {}'.format(record['mfd_canister_id']))
        return analysis_location_dict

    except InternalError as e:
        logger.error(e)
        raise


@log_args_and_response
def create_couch_db_doc_mfd_canister_wizard(company_id, batch_device_dict, current_batch):
    """
    Function to create couch db doc for mfd canister transfer wizard
    @param current_batch: int
    @param company_id: int
    @param batch_device_dict: dict
    @return:
    """
    try:
        for batch, device_list in batch_device_dict.items():
            for device_id in device_list:
                database_name = get_couch_db_database_name(company_id=company_id)
                cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
                cdb.connect()
                doc_id = str(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME) + "-" + str(device_id)
                table = cdb.get(_id=doc_id)
                logger.info("Previous table of create_couch_db_doc_mfd_canister_wizard {}".format(table))
                if table is None:
                    table = {"_id": doc_id, "type": str(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME),
                             "data": {"batch_id": None, "module_id": 0, "mfd_transfer_to_device": False}}

                logger.info('comparing with batch {} and current batch: {} with type {} and {}'.format(batch,
                                                                                                        current_batch,
                                                                                                        type(batch),
                                                                                                        type(current_batch)))
                if batch == current_batch:
                    table["data"]["batch_id"] = batch
                    table["data"]["module_id"] = constants.MFD_TRANSFER_WIZARD_MODULES["TRANSFER_TO_ROBOT_WIZARD"]
                    table["data"]["mfd_transfer_to_device"] = False

                logger.info("Updated table create_couch_db_doc_mfd_canister_wizard {}".format(table))
                cdb.save(table)
        return True

    except couchdb.http.ResourceConflict:
        logger.info("EXCEPTION: Document update conflict.")
        raise RealTimeDBException("conflict_while_saving_document")

    except Exception as e:
        logger.error("Error in create_couch_db_doc_mfd_canister_wizard {}".format(e))
        raise Exception("Couch db update failed while transferring canisters")


@validate(required_fields=['company_id', 'device_id', 'display_location'])
def enable_mfd_location(request_args):
    """
    enables mfd location
    """
    company_id = request_args['company_id']
    device_id = request_args['device_id']
    display_location = request_args['display_location']

    try:
        with db.transaction():
            # validate the device_id for the given company
            valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
            if not valid_device:
                return error(1033)

            # mark location as enable in location master
            set_location_enable = set_location_enable_dao(device_id=device_id, display_location=display_location)

            if "failure" in str(set_location_enable):
                return set_location_enable
            else:
                return create_response(settings.SUCCESS_RESPONSE)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)


@log_args_and_response
def canister_batch_update(mfd_data, batch_id, user_id, mfs_id, pending_error, system_id, company_id, trolley_id):
    try:
        reset_couch_db_data = False
        logger.info('batch_found:' + str(batch_id))
        query_2 = db_get_mfd_batch_info(batch_ids=[batch_id], user_id=user_id, mfs_id=mfs_id)
        filled_canisters = None
        total_canisters = None
        # for checking current trolley fillig
        if 'data' in mfd_data:
            trolley_seq = mfd_data['data'].get('trolley_seq', None)
        for record in query_2:
            filled_canisters = int(record['filled_canister'])
            total_canisters = int(record['total_canister'])
        mfd_data['data']['total_canisters'] = total_canisters
        mfd_data['data']['filled_canisters'] = filled_canisters
        progress_canisters = db_get_user_pending_canister_count(batch_id, user_id, mfs_id)
        logger.info("in_progress_canisters_current_placement_count: {}".format(progress_canisters))
        if not progress_canisters and not pending_error:
            logger.info('No canister found on mfs for current batch: resetting scanned data')
            mfd_data['data']['scanned_drawer'] = None
            mfd_data['data']['canister_data'] = {}
            mfd_data['data']['current_analysis_ids'] = []
            mfd_data['data']['drawer_data'] = {}
            mfd_data['data']['previously_scanned_drawer'] = None
            logger.info('removing current canister data')
            temp_data = mfd_remove_current_canister_data(mfs_id)
            logger.info('removed_from_temp_filling_with_count: {}'.format(temp_data))
            trolley_pending_count = db_get_pending_canister_count(batch_id, trolley_id=trolley_id)
            logger.info("Trolley_pending_count for batch_id {} and trolley_id {} is: {}"
                         .format(batch_id, trolley_id, trolley_pending_count))
            mfd_filling_dict = {
                'update_cdb': False,
                'batch_id': batch_id,
                'user_id': user_id,
                'system_id': system_id,
                'company_id': company_id,
                'trolley_seq': trolley_seq
            }
            logger.info('fetching_next_placement_with: {}'.format(mfd_filling_dict))
            update_data, cdb_updated_data = get_mfd_filling_canister(mfd_filling_dict)
            logger.info('data_from_mfd_filling_with_status: {} and {}'.format(update_data, cdb_updated_data))
            if cdb_updated_data:
                mfd_data['data'].update(cdb_updated_data)
            if update_data:
                mfd_data['data']['new_data_added'] = True
            if not trolley_pending_count:
                mfd_analysis_ids, mfs_system_mapping, dest_devices, batch_system = get_trolley_analysis_ids(
                    batch_id, trolley_id)
                logger.info('dest_devices: {}'.format(dest_devices))
                if dest_devices:
                    for device_data in dest_devices:
                        device_message = dict()
                        drop_pending_canister_count = check_drop_pending(device_ids=[device_data])
                        logger.info(
                            'callback_checking_drop_pending_status: {}'.format(drop_pending_canister_count))
                        if not drop_pending_canister_count:
                            next_trolley, batch_system_id, next_trolley_name, next_trolley_seq = db_get_next_trolley(batch_id,
                                                                                                   device_data)
                            system_in_progress_batch = get_progress_batch_id(batch_system_id)
                            logger.info('checking_current_batch_for_callback_notification {}'
                                         .format(system_in_progress_batch))
                            send_notification = False
                            if system_in_progress_batch:
                                logger.info('callback_current_batch: {} and in_progress_batch {}'.
                                             format(batch_id, system_in_progress_batch))
                                if system_in_progress_batch == batch_id:
                                    send_notification = True
                            else:
                                upcoming_batch = get_top_batch_id(system_id=batch_system_id)
                                logger.info('callback_current_batch: {} and upcoming_batch {}'.
                                             format(batch_id, upcoming_batch))
                                if upcoming_batch == batch_id:
                                    send_notification = True
                            logger.info('callback_notification_flag_value: {}'.format(send_notification))
                            if send_notification:
                                logger.info("checking type of next_trolley: {}".format(type(next_trolley)))
                                logger.info("checking type of trolley_id: {}".format(type(trolley_id)))
                                if next_trolley == trolley_id:
                                    robot_data = get_device_name_from_device([device_data])
                                    device_message[device_data] = "{} is ready for transfer. Kindly start the Manual" \
                                                                  " Canister Transfer flow for {}" \
                                        .format(next_trolley_name, robot_data[device_data])
                                    unique_id = int(str(next_trolley) + str(next_trolley_seq) + str(device_data))
                                    logger.info("In canister_batch_update, message {}, unique_id {}".format(device_message, unique_id))
                                    Notifications(user_id=user_id, call_from_client=True) \
                                        .send_transfer_notification(user_id=user_id, system_id=batch_system_id,
                                                                    device_message=device_message,
                                                                    unique_id=unique_id,
                                                                    batch_id=batch_id, flow='mfd')
                                    logger.info('getting transfer_wizard_data')
                                    status, transfer_wizard_data = get_mfd_wizard_couch_db(company_id=company_id,
                                                                                           device_id=device_data)
                                    logger.info('getting_transfer_wizard data {} with status'
                                                .format(transfer_wizard_data, status))
                                    wizard_couch_db_data = transfer_wizard_data.get("data", {})
                                    if wizard_couch_db_data:
                                        current_module = wizard_couch_db_data.get('module_id', None)
                                        transfer_status = wizard_couch_db_data.get('mfd_transfer_to_device', True)
                                        if transfer_status and \
                                                current_module == constants.MFD_TRANSFER_WIZARD_MODULES[
                                                "TRANSFER_TO_ROBOT_WIZARD"]:
                                            wizard_data = {
                                                'mfd_transfer_to_device': False,
                                                'batch_id': batch_id,
                                                'module_id': constants.MFD_TRANSFER_WIZARD_MODULES[
                                                    "TRANSFER_TO_ROBOT_WIZARD"]}
                                            logger.info('updating_transfer_wizard_data: {}'.format(wizard_data))
                                            update_mfd_transfer_wizard_couch_db(device_data, company_id,
                                                                                wizard_data)
                                    else:
                                        wizard_data = {
                                            'mfd_transfer_to_device': False,
                                            'batch_id': batch_id,
                                            'module_id': constants.MFD_TRANSFER_WIZARD_MODULES[
                                                "TRANSFER_TO_ROBOT_WIZARD"]}
                                        logger.info('updating_transfer_wizard_data: {}'.format(wizard_data))
                                        update_mfd_transfer_wizard_couch_db(device_data, company_id, wizard_data)
        user_pending_count = db_get_pending_canister_count(batch_id, user_id=user_id)
        logger.info("user_pending_count for batch_id {} and user_id {} is: {}"
                     .format(batch_id, user_id, user_pending_count))
        if not user_pending_count and not pending_error:
            logger.info('No pending canister found for user: {} and batch_id: {}'.format(user_id, batch_id))
            reset_couch_db_data = True
            module_data = {
                'batch_id': 0,
                'trolley_scanned': False,
                'current_module': constants.MFD_MODULES["SCHEDULED_BATCH"]
            }
            logger.info('couch_db_module_reset: {}'.format(module_data))
            status, doc = update_mfd_module_couch_db(constants.CONST_MFD_PRE_FILL_DOC_ID, system_id,
                                                     module_data)
            logger.info("In canister_batch_update:update_mfs_data_in_couch_db status: {}, doc: {}".format(status, doc))
        pending_canisters = db_get_pending_canister_count(batch_id)
        logger.info("canister_pending_count for batch_id {} is: {}"
                     .format(batch_id, pending_canisters))
        if not pending_canisters and not pending_error:
            logger.info('No pending canister found for current batch: marking batch done: ' + str(batch_id))
            batch_status = db_update_mfd_status(batch=batch_id, mfd_status=constants.MFD_BATCH_FILLED, user_id=1)
            logger.info('updated_mfd_batch_status: {}'.format(batch_status))
            reset_couch_db_data = True

        return mfd_data, reset_couch_db_data
    except Exception as e:
        raise e


@log_args_and_response
def db_skip_canister(analysis_ids, company_id, user_id, alert=False, mfs_system_id=None):
    """
    marks the canister as skipped If the canister are on mfs then changing its destination location as those canisters
    should be placed in empty drawers of trolley
    @param analysis_ids:
    @param company_id:
    @param user_id:
    @param alert:
    @return:
    """
    try:
        logger.info(f"In db_skip_canister")
        skip_system = list()
        mfs_data_update = dict()
        exclude_delete = set()
        # current_mfs_canisters_data fetches the currently placed mfd_analysis for which canisters are not placed yet.
        current_mfs_data = current_mfs_canisters(analysis_ids)
        logger.info(f"In db_skip_canister, current_mfs_data: {current_mfs_data}")
        status = db_update_canister_status(analysis_ids, constants.MFD_CANISTER_SKIPPED_STATUS, user_id)

        # checking if canisters are on mfs
        current_mfs_analysis_dict = current_mfs_placed_canisters(analysis_ids)
        logger.info(f"In db_skip_canister, current_mfs_analysis_dict: {current_mfs_analysis_dict}")

        for home_cart, analysis_data in current_mfs_analysis_dict.items():
            # if canisters are on mfs then change its location in mfd_analysis
            current_suggested_dest_location_ids = analysis_data['skip_locations']
            current_mfs_analysis_ids = analysis_data['skip_analysis_ids']
            location_update = update_dest_location_for_current_mfd_canister(current_mfs_analysis_ids,
                                                                            current_suggested_dest_location_ids,
                                                                            home_cart)
            logger.info("In db_skip_canister: location_update: {}".format(location_update))
        logger.info('In db_skip_canister, currently_placed_on_mfs_without_canister:' + str(current_mfs_data))
        if current_mfs_data:
            system_wise_data = dict()
            mfs_device_ids = list()
            for analysis_id, mfs_data in current_mfs_data.items():
                mfs_device_ids.append(mfs_data['mfs_device_id'])
                if mfs_data['system_id'] not in system_wise_data:
                    system_wise_data[mfs_data['system_id']] = {
                        'mfs_location_number': list(),
                        'mfs_id': mfs_data['mfs_device_id']
                    }
                system_wise_data[mfs_data['system_id']]['mfs_location_number'].append(mfs_data['mfs_location_number'])

            for system_id, mfs_location_info in system_wise_data.items():
                status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                              system_id=system_id)
                reset_couch_db_data = False
                couch_db_doc = document.get_document()
                couch_db_data = couch_db_doc.get("data", {})
                couch_db_canister_data = couch_db_data.get('canister_data', {})
                batch_id = couch_db_data.get('batch_id', None)
                user_id = couch_db_data.get('user_id', None)
                mfs_id = mfs_location_info['mfs_id']
                trolley_id = couch_db_doc["data"].get('trolley_id', None)
                location_info = mfs_location_info['mfs_location_number']
                pending_error = False
                for can_data in couch_db_canister_data.values():
                    pending_error = pending_error or can_data['is_in_error']
                for loc in location_info:
                    if couch_db_canister_data.get(str(loc), {}):
                        couch_db_canister_data[str(loc)].update({'canister_required': False})
                    else:
                        couch_db_canister_data[str(loc)] = {
                            'canister_required': False,
                            'is_in_error': False,
                            'current_canister_id': None,
                            'required_canister_id': None,
                            'error_message': None
                        }
                mfd_data = couch_db_doc
                mfd_data['data']['canister_data'] = couch_db_canister_data
                for loc, can_data in couch_db_canister_data.items():
                    if can_data.get('is_in_error', False):
                        exclude_delete.add(mfs_id)
                if batch_id:
                    skip_system.append(system_id)
                    mfd_data, reset_couch_db_data = canister_batch_update(mfd_data, batch_id, user_id, mfs_id, pending_error,
                                                                          system_id, company_id, trolley_id)
                if alert:
                    mfd_data['data']['pack_manual_delete'] = True
                mfs_data_update[system_id] = {'mfd_data': mfd_data,
                                              'original_doc': document,
                                              'reset_couch_db_data': reset_couch_db_data}

            logger.info('mfs_device_ids_while_marking_can_skip: {}'.format(mfs_device_ids))
            logger.info('mfs_device_ids_with_error_while_marking_can_skip: {}'.format(exclude_delete))
            update_mfs_data_list = list(set(mfs_device_ids) - set(exclude_delete))
            if update_mfs_data_list:
                logger.info('update_mfs_data_list_while_skip: '.format(update_mfs_data_list))
                current_data_delete_status = update_temp_mfs_data(update_mfs_data_list)
                logger.info('IN db_skip_canister: current_data_delete_status: {}'.format(current_data_delete_status))
        else:
            if mfs_system_id:
                update_mfd_couch_db_notification(analysis_id=analysis_ids, user_id=user_id)

        return status, skip_system, mfs_data_update
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def skip_drug_canister_status_change(mfd_analysis_ids, company_id, user_id, alert=False, action_id=None, mfs_system_id=None):
    """
    skips drug for particular canisters which are currently placed on particular MFS or for entire batch of a particular
    user
    :param mfd_analysis_ids: list
    :param company_id: list
    :param user_id: list
    :param alert: boolean
    :param action_id: int
    :return:
    """

    try:
        logger.info("In skip_drug_canister_status_change")
        skipped_updated_systems = list()
        mfs_data_update = dict()
        # if the whole canisters drugs are skipped then marking canister as skipped
        canister_skipped_analysis_ids = db_get_skipped_analysis_ids(mfd_analysis_ids)
        logger.info('In skip_drug_canister_status_change, canister_skipped_analysis_ids: {}'.format(canister_skipped_analysis_ids))
        if canister_skipped_analysis_ids:
            canister_status, skipped_updated_systems, mfs_data_update = db_skip_canister(canister_skipped_analysis_ids,
                                                                                         company_id=company_id,
                                                                                         user_id=user_id,
                                                                                         alert=alert,
                                                                                         mfs_system_id=mfs_system_id)

        # marking rts-required on canister level here so half skipped and half rts required drug-can can be marked as
        # rts required canister
        rts_analysis_ids = db_get_rts_analysis_ids(mfd_analysis_ids)
        logger.info('In skip_drug_canister_status_change, found rts_analysis_ids:' + str(rts_analysis_ids))
        if rts_analysis_ids:
            canister_status = db_update_canister_status(rts_analysis_ids,
                                                        constants.MFD_CANISTER_RTS_REQUIRED_STATUS, user_id,
                                                        action_id=action_id)
            logger.info('In skip_drug_canister_status_change: canister_status:' + str(canister_status))
        # if canister has only skipped and filled drugs marking canister as filled.
        action_pending_canisters = list(
            set(mfd_analysis_ids) - set(canister_skipped_analysis_ids) - set(rts_analysis_ids))
        logger.info('action_pending_canisters: {}'.format(action_pending_canisters))
        if action_pending_canisters:
            filling_pending_canisters = db_get_filling_pending_analysis_ids(action_pending_canisters)
            filled_canisters = set(action_pending_canisters) - set(filling_pending_canisters)
            logger.info('filled_canisters_found: {}'.format(filled_canisters))
            if filled_canisters:
                db_update_canister_status(list(filled_canisters), constants.MFD_CANISTER_FILLED_STATUS, user_id)

        return True, skipped_updated_systems, mfs_data_update
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_rts_data(mfd_analysis_details_id, mfd_analysis_ids, company_id, user_id, action_id=None,
                    change_rx: Optional[bool] = False, delete_all_packs: Optional[bool] = False):
    """
    The drugs are marked as RTS required and if canisters are on MFS then pop-up is shown on MFS screen
    :param mfd_analysis_details_id:
    :param mfd_analysis_ids:
    :param company_id:
    :param user_id:
    :param comment:
    :param change_rx:
    :param delete_all_packs:
    :return:
    @param mfd_analysis_details_id:
    @param mfd_analysis_ids:
    @param company_id:
    @param user_id:
    @return:
    @param action_id:
    @param change_rx:
    @param delete_all_packs:
    """
    try:
        # skipped_updated_systems = []
        # canister_skipped_analysis_ids = []
        # updating drug status to rts required if drugs are filled else mark drug as skipped.
        filled_drugs = get_filled_drug(mfd_analysis_details_id, [constants.MFD_DRUG_FILLED_STATUS])
        if filled_drugs:
            status = db_update_drug_status(filled_drugs, constants.MFD_DRUG_RTS_REQUIRED_STATUS)
            logger.info('updated_mfd_drugs_to_rts: ' + str(filled_drugs) + ' with_status ' + str(status))

            drug_tracker_status = update_drug_tracker_from_mfd_analysis_details_ids(mfd_analysis_details_ids=filled_drugs)
            logger.info("In update_rts_data, drug_tracker_status: {}".format(drug_tracker_status))

        pending_drugs = get_filled_drug(mfd_analysis_details_id, [constants.MFD_DRUG_PENDING_STATUS])
        if pending_drugs:
            status = db_update_drug_status(pending_drugs, constants.MFD_DRUG_SKIPPED_STATUS)
            logger.info('updated_mfd_drugs_to_skip: ' + str(pending_drugs) + ' with_status ' + str(status))

        canister_updates, skipped_updated_systems, update_mfs_data = skip_drug_canister_status_change(mfd_analysis_ids,
                                                                                                      company_id=company_id,
                                                                                                      alert=True,
                                                                                                      user_id=user_id,
                                                                                                      action_id=action_id)

        # based on canister status mfs document is being updated.
        skipped_updated_systems = update_couch_db_current_mfs(mfd_analysis_ids, skipped_updated_systems)

        # updates couch-db document with pending rts mfd canister count
        update_couch_db_mfd_canister_master(mfd_analysis_ids)

        # update transfer couch-db for rts canisters
        if filled_drugs:
            update_couch_db_mfd_canister_transfer(mfd_analysis_ids)

        system_robot_info = get_robot_system_info(mfd_analysis_ids)
        mfs_system_mapping = db_get_mfs_info(mfd_analysis_ids)

        batch_company_dict = dict()
        for system_id, mfs_info in mfs_system_mapping.items():
            batch_company_dict[mfs_info['batch_id']] = {
                'company_id': mfs_info['company_id'],
                'batch_id': mfs_info['batch_id']
            }
        logger.debug("batch_company_dict_for_trolley_reuse: {}".format(batch_company_dict))
        for batch_id, batch_info in batch_company_dict.items():
            update_pending_mfd_assignment(batch_info)
        logger.debug("trolley_reuse_check_done")

        if not change_rx and not delete_all_packs:
            for mfs_system_id, mfs_data_dict in update_mfs_data.items():
                original_doc = mfs_data_dict['original_doc']
                mfd_data = mfs_data_dict['mfd_data']
                reset_couch_db_data = mfs_data_dict['reset_couch_db_data']
                if reset_couch_db_data:
                    mfd_data['data'] = {'pack_manual_delete': True}
                status, doc = update_document_with_revision(original_doc, mfd_data, False)
                logger.info("In update_rts_data: update_document_with_revision:doc: {},status: {}".format(status, doc))
                # update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID, mfs_system_id, mfs_data)

        if not change_rx and not delete_all_packs:
            for mfs_system_id, mfs_data in mfs_system_mapping.items():
                if mfs_system_id not in skipped_updated_systems:
                    mfs_id = mfs_data['mfs_device_id']
                    status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                                  system_id=mfs_system_id)
                    couch_db_doc = document.get_document()

                    couch_db_data = couch_db_doc.get("data", {})
                    couch_db_canister_data = couch_db_data.get('canister_data', {})
                    batch_id = couch_db_data.get('batch_id', None)
                    user_id = couch_db_data.get('user_id', None)
                    trolley_id = couch_db_data.get('trolley_id', None)
                    pending_error = False
                    for can_data in couch_db_canister_data.values():
                        pending_error = pending_error or can_data['is_in_error']
                    mfd_data = couch_db_doc
                    mfd_data['data']['pack_manual_delete'] = True
                    mfd_data, reset_couch_db_data = canister_batch_update(mfd_data, batch_id, user_id, mfs_id,
                                                                          pending_error,
                                                                          mfs_system_id, company_id, trolley_id)
                    if reset_couch_db_data:
                        mfd_data['data'] = {'pack_manual_delete': True}
                    status, doc = update_document_with_revision(document, mfd_data, False)
                    logger.info("In update_rts_data: update_document_with_revision:doc: {},status: {}"
                                .format(status, doc))

        logger.info('checking_wizard_update: {}'.format(system_robot_info))
        for robot_info in system_robot_info:
            logger.debug('in_update_wizard_check')
            update_transfer_wizard(robot_info['dest_device_id'], robot_info['company_id'],
                                   robot_info['dest_system_id'], analysis_ids=mfd_analysis_ids)

        return True
    except RealTimeDBException as e:
        raise e
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_next_canister_trolley_id(analysis_ids: list) -> tuple:
    """
    to obtain home_cart for next trolley
    @param analysis_ids: list
    """
    try:
        batch_id: int = 0
        order_number: int = 0
        mfd_analysis_details = get_max_order_number(analysis_ids)
        logger.info(analysis_ids)
        for record in mfd_analysis_details:
            logger.info("mfd_canister_id {}".format(record["mfd_canister_id"]))
            batch_id = record["batch_id"]
            order_number = record["order_no"]
        logger.info(order_number)
        order_number_to_check = order_number + 1
        logger.info(order_number_to_check)
        trolley_id = None
        trolley_name = None
        mfd_canister_home_cart_query = mfd_data_by_order_no(order_number)
        logger.info(mfd_canister_home_cart_query)
        for record in mfd_canister_home_cart_query:
            trolley_id = record['device_id']
            trolley_name = record['name']
            trolley_seq = record['trolley_seq']
        return batch_id, trolley_id, trolley_name, trolley_seq

    except(InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def update_transfer_wizard(device_id, company_id, system_id, analysis_ids):
    """
    The drugs are marked as RTS required and if canisters are on MFS then pop-up is shown on MFS screen
    :param device_id:
    :param company_id:
    :param system_id:
    :param analysis_ids:
    :return:
    """
    try:
        logger.info('checking if analysis is in robot')
        robot_list = check_in_robot(analysis_ids)
        logger.info('robot_list_for_analysis_ids_in_robot: {} for analysis_ids: {}'.format(robot_list, analysis_ids))
        if device_id not in robot_list:
            return True
        drop_pending_count = check_drop_pending(device_ids=[device_id])
        logger.info('drop_pending_check_for_device_with {} {}'.format(device_id, drop_pending_count))

        if not drop_pending_count:
            # to obtain batch_id and next canister trolley id based on analysis id
            batch_id = db_get_batch_id_from_analysis_ids(analysis_ids)
            next_trolley_id, system, next_trolley_name, next_trolley_seq = db_get_next_trolley(batch_id, device_id)

            logger.info("batch_id: {}".format(batch_id))
            logger.info("next_trolley_id: {}".format(next_trolley_id))
            # to notify when transfers are pending for the batch
            logger.info('getting transfer_wizard_data')
            status, transfer_wizard_data = get_mfd_wizard_couch_db(company_id=company_id,
                                                                   device_id=device_id)
            logger.info('getting_transfer_wizard data {}'.format(transfer_wizard_data))
            wizard_couch_db_data = transfer_wizard_data.get("data", {})
            if wizard_couch_db_data:
                current_module = wizard_couch_db_data.get('module_id', None)
                transfer_status = wizard_couch_db_data.get('mfd_transfer_to_device', True)
                logger.info('checking transfer update status {} and current module {}'
                             .format(transfer_status, current_module))
                if transfer_status and current_module == constants.MFD_TRANSFER_WIZARD_MODULES[
                                                            "TRANSFER_TO_ROBOT_WIZARD"]:
                    if next_trolley_id is not None:
                        robot_data = get_device_name_from_device([device_id])
                        message = "Kindly start the manual canister transfer flow from {} for {}".format(
                            next_trolley_name, robot_data[device_id])
                        device_message: dict = dict()
                        device_message[device_id] = message
                        unique_id = int(str(next_trolley_id) + str(next_trolley_seq) + str(device_id))
                        logger.info("In update_transfer_wizard, message {}, unique_id {}".format(message, unique_id))
                        Notifications(user_id=None, call_from_client=True) \
                            .send_transfer_notification(user_id=None, batch_id=batch_id, system_id=system_id, unique_id=unique_id,
                                                        device_message=device_message, flow='mfd')

                    # to notify when the transfers are completed for the batch
                    else:
                        message = "Kindly start the Canister Transfer"
                        device_message: dict = dict()
                        device_message[device_id] = message
                        logger.info("In update_transfer_wizard, message {}".format(message))
                        Notifications(user_id=None, call_from_client=True) \
                            .send_transfer_notification(user_id=None, batch_id=batch_id, system_id=system_id,
                                                        device_message=device_message, unique_id=None,
                                                        flow='mfd')

                    logger.info("updating_wizard_doc_dropping_done: {}".format(batch_id))
                    update_couch_db_mfd_canister_wizard(company_id=company_id,
                                                        device_id=device_id,
                                                        module_id=constants.MFD_TRANSFER_WIZARD_MODULES[
                                                            "RTS_SCREEN_WIZARD"],
                                                        batch_id=batch_id,
                                                        mfd_transfer_to_device=False)
            return True
    except RealTimeDBException as e:
        raise e
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_mvs_filling_mfd_canister(pack_id, company_id):
    """
    Returns mfd canister data that are to be used to fill drugs on mvs.
    @param company_id:
    @param pack_id:
    :return:
    """
    try:
        status_ids = [constants.MFD_CANISTER_MVS_FILLING_REQUIRED]
        mfd_mvs_canisters = get_pack_mfd_canisters(pack_id, company_id, status_ids)
        return create_response(mfd_mvs_canisters)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@validate(required_fields=["batch_id", "mfd_analysis_id", "company_id", "pack_id"])
def mark_canister_mvs_filled(mfd_data):
    """
    updates drug and canister status and marks them to mvs filled.
    @param mfd_data:
    :return:
    """
    company_id = mfd_data['company_id']
    batch_id = mfd_data['batch_id']
    pack_id = mfd_data['pack_id']
    user_id = mfd_data['user_id']
    mfd_analysis_id = mfd_data['mfd_analysis_id']
    canister_status = 0
    dest_container_name = None
    rts_required = False
    rts_mfd_analysis_details_ids = list()
    try:
        with db.transaction():
            # getting drugs for whom mvs filling was required.
            mfd_analysis_details_ids, home_cart_id, mfd_canister_id, pack_mfd_analysis_details_ids, canister_done, \
                mfd_canistser_state_status, container_name, pack_status_list, home_cart_device_name = db_get_mfd_analysis_details_ids(
                    mfd_analysis_id, company_id, constants.MFD_DRUG_FILLED_STATUS, pack_id)
            if not pack_mfd_analysis_details_ids:
                return error(1020, 'No mvs filling required for given canister.')

            if canister_done:
                # checking if rts drugs are present
                rts_mfd_analysis_details_ids, rts_home_cart_id, rts_mfd_canister_id, rts_pack_mfd_analysis_details_ids, \
                    rts_canister_done, rts_mfd_canister_state_status, container_name, pack_status_list, home_cart_device_name = db_get_mfd_analysis_details_ids(
                        mfd_analysis_id, company_id, constants.MFD_DRUG_RTS_REQUIRED_STATUS)
                logger.info('rts_required while marking_mvs_filled: {}'.format(rts_mfd_analysis_details_ids))
                # if rts then marking canister status rts required
                if rts_mfd_analysis_details_ids:
                    # If canister is skipped at mvs or pfs then whole canister is marked RTS. Here we will only have
                    # rts canisters if one of the pack is marked manual or deleted
                    action_id = settings.MANUAL_PACK_ACTION
                    if settings.DELETED_PACK_STATUS in pack_status_list:
                        action_id = settings.DELETE_PACK_ACTION
                    rts_canister_status = db_update_canister_status([mfd_analysis_id],
                                                                    constants.MFD_CANISTER_RTS_REQUIRED_STATUS, user_id,
                                                                    action_id)
                    logger.info("In mark_canister_mvs_filled: rts_canister_status: {}".format(rts_canister_status))

                else:
                    if home_cart_id:
                        empty_location = get_empty_locations(constants.MFD_TROLLEY_EMPTY_DRAWER_TYPE, 1, home_cart_id)
                        logger.info('empty_Location: {}'.format(empty_location))

                        if not empty_location:
                            return error(1020, 'No empty location found')
                        # updating canister's location
                        canister_location_dict = {mfd_canister_id: empty_location[0]}

                        canister_location_update = update_mfd_canister_location(canister_location_dict)
                        logger.info("In mark_canister_mvs_filled: canister_location_update: {}".format(canister_location_update))

                    canister_status = db_update_canister_status([mfd_data['mfd_analysis_id']],
                                                                constants.MFD_CANISTER_MVS_FILLED_STATUS, user_id)


                logger.info('checking_trolley_reuse_while_mvs_filled')
                update_pending_mfd_assignment({'company_id': company_id, 'batch_id': batch_id})
                logger.info('checking_trolley_reuse_while_mvs_filled_done')

                if mfd_canistser_state_status == constants.MFD_CANISTER_MISPLACED:
                    mfd_canister_home_cart_dict = {home_cart_id: [mfd_canister_id]}
                    update_status = mfd_canister_found_update_status(mfd_canister_home_cart_dict, user_id)
                    logger.info("In mark_canister_mvs_filled: mfd_canister_found_update_status: {}".format(update_status))

            # marking mvs filled on drug level.
            drug_update_status = db_update_drug_status(pack_mfd_analysis_details_ids, constants.MFD_DRUG_MVS_FILLED)

            if canister_status == 0:
                if container_name:
                    dest_container_name = container_name
                elif home_cart_id:
                    empty_locations_list_for_rts_canisters = fetch_empty_trolley_locations_for_rts_canisters(
                        trolley_id=home_cart_id)
                    if empty_locations_list_for_rts_canisters:
                        dest_container_name = empty_locations_list_for_rts_canisters[0]['drawer_name']

            if rts_mfd_analysis_details_ids:
                rts_required = True

            return create_response({'canister_status': canister_status,
                                    'drug_status': drug_update_status,
                                    'rts_required': rts_required,
                                    'canister_active_status': mfd_canistser_state_status,
                                    'dest_drawer_name': dest_container_name})
    except (InternalError, IntegrityError) as e:
        logger.error("Error in reset_scanned_data : {}".format(e))
        return error(2001)


@validate(required_fields=["device_id", "system_id", "company_id", "document"])
def reset_scanned_data(mfd_data):
    """
    updates drug and canister status and marks them to mvs filled.
    @param mfd_data:
    :return:
    """
    # company_id = mfd_data['company_id']
    device_id = mfd_data['device_id']
    system_id = mfd_data['system_id']
    document = mfd_data['document']
    # canister_status = 0
    try:
        if document == 'mfd_transfer':
            mfd_data = {"scanned_drawer": None}
            update_mfd_transfer_couch_db(device_id=device_id,
                                         system_id=system_id,
                                         mfd_data=mfd_data
                                         )

            return create_response(True)
    except (InternalError, IntegrityError) as e:
        logger.error("Error in reset_scanned_data : {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=["company_id", "user_id", "reason"])
def skip_mfs_filling(mfd_data):
    """
    updates drug and canister status and marks them to mvs filled.
    @param mfd_data:
    :return:
    """
    company_id = mfd_data['company_id']
    reason = mfd_data['reason']
    user_id = mfd_data['user_id']
    batch_id = mfd_data.get('batch_id', None)
    trolley_seq = mfd_data.get("trolley_seq")
    skip_for_all_devices = False
    skip_for_all_devices_status = None
    system_id = mfd_data.get("system_id", None)

    try:
        with db.transaction():
            if system_id and not batch_id:
                batch_id = get_progress_batch_id(system_id)

            if batch_id:
                skip_analysis_ids, skip_analysis_details_ids, trolley_seq_info = get_mfd_analysis_ids_for_skip(batch_id,
                                                                                                               trolley_seq)

            if skip_analysis_ids:
                db_update_canister_status(skip_analysis_ids, constants.MFD_CANISTER_SKIPPED_STATUS, user_id, reason)
                status = db_update_drug_status(list(skip_analysis_details_ids), constants.MFD_DRUG_SKIPPED_STATUS)
                logger.info("In skip_mfs_filling: db_update_drug_status: {}".format(status))

            for trolley_seq, trolley_data in trolley_seq_info.items():
                reset_couch_db_data = False
                status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                              system_id=trolley_data['system_id'])
                couch_db_doc = document.get_document()
                logger.info('current_couch_db_data' + str(couch_db_doc))
                couch_db_canister_data = couch_db_doc["data"].get('canister_data', {})
                if couch_db_canister_data:
                    if trolley_data['skip_analysis_ids']:
                        if trolley_data['locations_to_be_skipped']:
                            for location in list(trolley_data['locations_to_be_skipped']):
                                couch_db_canister_data[str(location)]['canister_required'] = False
                if not trolley_data['is_canister_present']:
                    batch_id_from_couchdb = couch_db_doc["data"].get('batch_id', None)
                    couch_db_drawer_data = get_mfs_transfer_drawer_data(trolley_data['mfs_device_id'])
                    logger.info("In skip_mfs_filling: couch_db_drawer_data: {}".format(couch_db_drawer_data))
                    pending_error = False
                    for can_data in couch_db_canister_data.values():
                        pending_error = pending_error or can_data['is_in_error']
                    if batch_id_from_couchdb:
                        couch_db_doc, reset_couch_db_data = canister_batch_update(couch_db_doc, batch_id_from_couchdb, user_id,
                                                                                  trolley_data['mfs_device_id'],
                                                                                  pending_error, trolley_data['system_id'],
                                                                                  company_id, trolley_data['trolley_id'])
                if trolley_data['skip_analysis_ids']:
                    skip_for_all_devices_status = update_mfd_couch_db_notification(analysis_id=list(trolley_data['skip_analysis_ids']),
                                                                                   user_id=user_id)
                if not skip_for_all_devices and skip_for_all_devices_status:
                    skip_for_all_devices = True
                status, doc = update_document_with_revision(document, couch_db_doc, reset_couch_db_data)
                if not status:
                    raise ValueError(error(11002))

            if skip_analysis_ids and skip_for_all_devices:
                logger.debug("Run the Pending Recommendation")
                response_dict = json.loads(update_pending_mfd_assignment({"company_id": company_id,
                                                                          "batch_id": batch_id}))
                status_code = response_dict.get("status", settings.FAILURE_RESPONSE)
                if status_code != settings.SUCCESS_RESPONSE:
                    raise Exception
            return create_response(True)
    except (InternalError, IntegrityError) as e:
        logger.error("error in skip_mfs_filling: {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Unknown error- " + str(e))


@log_args_and_response
@validate(required_fields=["batch_id", "system_id", "company_id", "device_id", "module_id"])
def update_mfd_transfer_status_v2(args: dict) -> dict:
    """
     This function updates the couch db for the given module_id
     @param args: dict
     @return dict
    """
    logger.info("In update_mfd_transfer_status")
    try:
        batch_id = args.get("batch_id", None)
        company_id = args.get("company_id", None)
        module_id = args.get("module_id", None)
        device_id = args.get("device_id", None)
        system_id = args.get("system_id", None)
        misplaced_canister_count = args.get("misplaced_canister_count", None)
        if company_id is None or system_id is None or device_id is None or batch_id is None or module_id is None:
            return error(1001, "Missing Parameter(s): company_id or system_id or device_id or batch_id or module_id.")

        # check for misplaced canisters if current module is RTS_SCREEN_WIZARD and update modules accordingly
        if module_id == constants.MFD_TRANSFER_WIZARD_MODULES["RTS_SCREEN_WIZARD"]:
            trolley_serial_number = args.get('trolley_serial_number', None)
            if not trolley_serial_number:
                logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} no trolley_serial_number: "
                             "returning 1001".format(device_id, module_id))
                return error(1001)
            trolley_id, drawer_id = get_trolley_drawer_from_serial_number_mfd(
                trolley_serial_number=trolley_serial_number,
                drawer_serial_number=None,
                company_id=company_id)
            logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} trolley_id {}, drawer_id {}"
                        .format(device_id, module_id, trolley_id, drawer_id))
            misplaced_canisters, rts_misplaced_canister_count = mfd_misplaced_canister_dao(batch_id=batch_id,
                                                                                           device_id=device_id,
                                                                                           trolley_id=trolley_id)
            logger.info("update_mfd_transfer_status_v2: for device_id: {}, on module: {} for trolley: {} "
                         "misplaced_canisters {}, rts_misplaced_canister_count {}"
                .format(device_id, module_id, trolley_id, misplaced_canisters, rts_misplaced_canister_count))

            # if misplaced canisters then add count in cdb
            if misplaced_canisters:
                logger.info("update_mfd_transfer_status_v2: for device_id: {}, on module: {} for trolley: {} "
                             "misplaced_canister_count: {}, count from FE: {}"
                    .format(device_id, module_id, trolley_id, len(misplaced_canisters), misplaced_canister_count))
                if misplaced_canister_count == 0:
                    update_mfd_misplaced_count(device_id=device_id, system_id=system_id,
                                               batch_id=batch_id, module_id=module_id, company_id=company_id,
                                               trolley_serial_number=trolley_serial_number,
                                               count=len(misplaced_canisters))

            # update the couch-db with EMPTY_CANISTER_WIZARD if there are no misplaced canisters
            else:
                logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} updating wizard to: {}"
                    .format(device_id, module_id, constants.MFD_TRANSFER_WIZARD_MODULES["EMPTY_CANISTER_WIZARD"]))
                transfer_data = {
                    "scanned_drawer": None,
                    "currently_scanned_drawer_sr_no": None,
                    "previously_scanned_drawer_sr_no": None,
                }
                update_mfd_transfer_couch_db(device_id, system_id, transfer_data)
                update_couch_db_mfd_canister_wizard(company_id=company_id,
                                                    device_id=device_id,
                                                    module_id=constants.MFD_TRANSFER_WIZARD_MODULES[
                                                        "EMPTY_CANISTER_WIZARD"],
                                                    batch_id=batch_id)
                logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} updated successfully"
                             " wizard to: {}".format(device_id, module_id,
                                                     constants.MFD_TRANSFER_WIZARD_MODULES["EMPTY_CANISTER_WIZARD"]))
            return create_response(settings.SUCCESS_RESPONSE)

        # check for any next batch if current module is EMPTY_CANISTER_WIZARD and update modules accordingly
        elif module_id == constants.MFD_TRANSFER_WIZARD_MODULES["EMPTY_CANISTER_WIZARD"]:
            trolley_serial_number = args.get('trolley_serial_number', None)
            if not trolley_serial_number:
                logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} no trolley_serial_number: "
                             "returning 1001".format(device_id, module_id))
                return error(1001, 'trolley_serial_number missing')
            trolley_id, drawer_id = get_trolley_drawer_from_serial_number_mfd(
                trolley_serial_number=trolley_serial_number,
                drawer_serial_number=None,
                company_id=company_id)
            logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} trolley_id {}, drawer_id {}"
                        .format(device_id, module_id, trolley_id, drawer_id))
            misplaced_canisters, rts_misplaced_canister_count = mfd_misplaced_canister_dao(batch_id=batch_id,
                                                                                           device_id=device_id,
                                                                                           trolley_id=trolley_id)
            logger.info("update_mfd_transfer_status_v2: for device_id: {}, on module: {} for trolley: {} "
                         "misplaced_canisters {}, rts_misplaced_canister_count {}"
                .format(device_id, module_id, trolley_id, misplaced_canisters, rts_misplaced_canister_count))

            # update the couch-db with MISPLACED_CANISTER_WIZARD if there are misplaced canisters
            if misplaced_canisters:
                logger.info("update_mfd_transfer_status_v2: for device_id: {}, on module: {} for trolley: {} "
                             "misplaced_canister_count: {}, count from FE: {}"
                             .format(device_id, module_id, trolley_id, len(misplaced_canisters),
                                     misplaced_canister_count))
                if misplaced_canister_count == 0:
                    update_mfd_misplaced_count(device_id=device_id, system_id=system_id,
                                               batch_id=batch_id, module_id=module_id, company_id=company_id,
                                               trolley_serial_number=trolley_serial_number,
                                               count=len(misplaced_canisters))
                return create_response(settings.SUCCESS_RESPONSE)
            # check for the current batch status and for next batch
            in_robot_batch_id, pending_batch_id, status, in_robot_can_status = get_next_mfd_transfer_batch(
                device_id=device_id)
            logger.info("update_mfd_transfer_status_v2: for device_id: {}, on module: {} trolley_id: {}"
                         "get_next_mfd_transfer_batch response: {}, {}, {}".format(device_id, module_id,
                                                                                   trolley_id,
                                                                                   in_robot_batch_id,
                                                                                   pending_batch_id,
                                                                                   status))
            if status:
                # update module after checking if empty canister are left to remove
                if in_robot_batch_id:
                    if constants.MFD_CANISTER_RTS_REQUIRED_STATUS in in_robot_can_status:
                        couch_db_module_id = constants.MFD_TRANSFER_WIZARD_MODULES["RTS_SCREEN_WIZARD"]
                    else:
                        couch_db_module_id = constants.MFD_TRANSFER_WIZARD_MODULES["EMPTY_CANISTER_WIZARD"]
                    updated_batch_id = in_robot_batch_id
                else:
                    couch_db_module_id = constants.MFD_TRANSFER_WIZARD_MODULES["TRANSFER_TO_ROBOT_WIZARD"]
                    updated_batch_id = pending_batch_id

                logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} trolley_id: {}"
                             " updating wizard to: {} batch_id: {} and flag false"
                             .format(device_id, module_id, trolley_id, couch_db_module_id, batch_id))

                # update the couch-db with TRANSFER_TO_ROBOT_WIZARD if the current batch has pending transfers
                update_couch_db_mfd_canister_wizard(company_id=company_id,
                                                    device_id=device_id,
                                                    module_id=couch_db_module_id,
                                                    batch_id=updated_batch_id,
                                                    mfd_transfer_to_device=False)

            # reset the couch db if there is no new batch with pending transfers
            else:
                logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} trolley_id: {} "
                             "resetting data".format(device_id, module_id, trolley_id))

                # reset the couch-db document for wizard
                doc_name = str(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME) + "-" + str(device_id)
                reset_couch_db_dict_for_reset = {"company_id": company_id,
                                                 "document_name": doc_name,
                                                 "couchdb_level": constants.STRING_COMPANY,
                                                 "key_name": "data"}
                reset_couch_db_document(reset_couch_db_dict_for_reset)
                # reset the couch-db document for mfd_transfers at system level
                transfer_data = {
                    "scanned_trolley": None,
                    "scanned_drawer": None,
                    "currently_scanned_drawer_sr_no": None,
                    "previously_scanned_drawer_sr_no": None,
                }
                update_mfd_transfer_couch_db(device_id, system_id, transfer_data)
            return create_response(settings.SUCCESS_RESPONSE)
        elif module_id == constants.MFD_TRANSFER_WIZARD_MODULES["TRANSFER_TO_ROBOT_WIZARD"]:
            # check for the current batch status and for next batch
            status, couch_db_doc = get_mfd_transfer_couch_db(device_id, system_id)
            couch_db_data = couch_db_doc.get("data", {})
            trolley_id = couch_db_data.get("scanned_trolley", None)
            logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} scanned_trolley_id: {}  "
                         .format(device_id, module_id, trolley_id))
            if trolley_id:
                trolley_drawer_list, serial_number_list, drawer_highlight_serial_number = get_trolley_drawer_data(
                    device_id=device_id,
                    batch_id=batch_id,
                    trolley_id=trolley_id)
                logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} scanned_trolley_id: {}" 
                             " trolley_drawer_list: {}, serial_number_list {}, drawer_highlight_serial_number: {} "
                             .format(device_id, module_id, trolley_id, trolley_drawer_list, serial_number_list,
                                     drawer_highlight_serial_number))
                if not trolley_drawer_list:
                    analysis_location_dict = get_drawer_canister_data(batch_id, device_id, trolley_id)
                    logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} scanned_trolley_id: {}" 
                                 "  analysis_location_dict: {}"
                                 .format(device_id, module_id, trolley_id, analysis_location_dict))
                    if analysis_location_dict:
                        update_transferred_location(analysis_location_dict)
                    logger.info("update_mfd_transfer_status_v2: for device_id: {} on module: {} trolley_id: {} "
                                 "updating wizard to: {} batch_id: {} and flag true"
                                 .format(device_id, module_id, trolley_id,
                                         constants.MFD_TRANSFER_WIZARD_MODULES["TRANSFER_TO_ROBOT_WIZARD"], batch_id))

                    next_trolley, system_id, next_trolley_name, next_trolley_seq = db_get_next_trolley(batch_id, device_id)
                    logger.info(f"1 update_mfd_transfer_status_v2, next_trolley: {next_trolley}, system_id: {system_id}, next_trolley_name: {next_trolley_name}")
                    if next_trolley:
                        mfd_transfer_to_device = False
                    else:
                        mfd_transfer_to_device = True

                    update_couch_db_mfd_canister_wizard(company_id=company_id,
                                                        device_id=device_id,
                                                        module_id=constants.MFD_TRANSFER_WIZARD_MODULES[
                                                            "TRANSFER_TO_ROBOT_WIZARD"],
                                                        batch_id=batch_id,
                                                        mfd_transfer_to_device=mfd_transfer_to_device)
                    transfer_data = {
                        "scanned_trolley": None,
                        "scanned_drawer": None,
                        "currently_scanned_drawer_sr_no": None,
                        "previously_scanned_drawer_sr_no": None,
                    }
                    update_mfd_transfer_couch_db(device_id, system_id, transfer_data)

            # in case there is no data available to transfer into robot then updating flag true
            else:
                logger.info("2 update_mfd_transfer_status_v2: for device_id: {} on module: {} trolley_id: {} "
                            "updating wizard to: {} batch_id: {} and flag true as no trolley found"
                            .format(device_id, module_id, trolley_id,
                                    constants.MFD_TRANSFER_WIZARD_MODULES["TRANSFER_TO_ROBOT_WIZARD"], batch_id))

                update_couch_db_mfd_canister_wizard(company_id=company_id,
                                                    device_id=device_id,
                                                    module_id=constants.MFD_TRANSFER_WIZARD_MODULES[
                                                        "TRANSFER_TO_ROBOT_WIZARD"],
                                                    batch_id=batch_id,
                                                    mfd_transfer_to_device=True)
            return create_response(settings.SUCCESS_RESPONSE)
        else:
            return error(1020, 'Invalid module_id')

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(13008)

    except ValueError as e:
        logger.error(e)
        return error(1020, 'pending_transfer')

    except Exception as e:
        logger.error(e)
        return error(11002)


@log_args_and_response
@validate(required_fields=["company_id", "mfd_canister_ids", "user_id", "comment"])
def deactivate_mfd_canister(data_dict: dict) -> dict:
    """
    This Method will mark canister deactivates and remove its trolley association
    @param data_dict: data dict with required keys "company_id", "mfd_canister_id", "user_id"
    @return: dict - generated label name and canister data
    """
    logger.info("Inside deactivate_mfd_canister: {}".format(data_dict))
    company_id = data_dict["company_id"]
    mfd_canister_ids = data_dict["mfd_canister_ids"]
    user_id = data_dict["user_id"]
    comment = data_dict["comment"]
    from_robot = data_dict.get("from_robot", False)
    mfd_canister_home_cart_dict = defaultdict(list)
    valid_canister_set = set()
    min_batch = None
    drug_filled_canister_ids = list()
    mfs_system_update = defaultdict(list)
    remove_association_dict = dict()
    mfs_canister_list = list()
    canister_status = None
    try:
        with db.transaction():

            # validate mfd canister
            logger.info('Validating_mfd_canister_for: {} and company_id: {}'.format(mfd_canister_ids, company_id))
            canister_query = get_mfd_canister_data_by_ids(mfd_canister_ids, company_id)
            mfd_analysis_ids = set()
            for record in canister_query:
                canister_status = record['mfd_canister_status_id']
                if record['device_type_id'] == settings.DEVICE_TYPES['Manual Filling Device']:
                    mfs_system_update[record['system_id']].append(record['current_location_number'])
                    # association is removed only if it's filling is on going
                    if record['temp_mfd_filling_id']:
                        remove_association_dict[record['mfd_analysis_id']] = None
                    mfs_canister_list.append(record['mfd_canister_id'])
                if min_batch is None or record['batch_id'] < min_batch:
                    min_batch = record['batch_id']
                mfd_canister_home_cart_dict[record['home_cart_id']].append(record['mfd_canister_id'])
                valid_canister_set.add(record['mfd_canister_id'])
                if record['mfd_canister_status_id'] in constants.MFD_CANISTER_DONE_LIST:
                    mfd_analysis_ids.add(record['mfd_analysis_id'])
                if record['mfd_drug_status_id']:
                    mfd_drug_ids = list(map(int, record['mfd_drug_status_id'].split(',')))
                else:
                    mfd_drug_ids = set()
                if set(mfd_drug_ids).intersection(set([constants.MFD_DRUG_FILLED_STATUS])):
                    drug_filled_canister_ids.append(record['mfd_canister_id'])
            if set(mfd_canister_ids) != valid_canister_set:
                return error(1020, 'Invalid mfd_canister_id or company_id')
            if drug_filled_canister_ids and not from_robot:
                if canister_status in [constants.MFD_CANISTER_MVS_FILLING_REQUIRED]:
                    return error(1000, 'Drug(s) in the canister having ID: {} needs to be filled in the upcoming '
                                       'packs. Please wait until the drugs are transferred to the pack to deactivate '
                                       'it.'.format(drug_filled_canister_ids[0]))
                return error(1000, 'The manual canister having ID:{} is currently being used in the batch. '
                                   'If you want to deactivate the it, kindly do it from the Robot Utility.'
                             .format(drug_filled_canister_ids[0]))

            # update mfd canister data
            logger.info('deactivating_mfd_canister_ids: {}'.format(mfd_canister_ids))
            for mfd_canister in mfd_canister_ids:
                update_location = True
                if mfd_canister in mfs_canister_list:
                    update_location = False
                update_status = mark_mfd_canister_deactivate([mfd_canister], user_id, update_location)

            if update_status:
                db_update_canister_active_status(mfd_canister_home_cart_dict, constants.MFD_CANISTER_DEACTIVATED,
                                                 user_id, comment)

                if mfd_analysis_ids:
                    status_id = constants.MFD_CANISTER_MVS_FILLING_REQUIRED
                    status = db_update_canister_status(list(mfd_analysis_ids), status_id, user_id, comment,
                                                       constants.MFD_ACTION_DEACTIVATE_AND_SKIP)
                    logger.info("In deactivate_mfd_canister: db_update_canister_status:{}".format(status))

                if min_batch:
                    update_pending_mfd_assignment({'company_id:': company_id, 'batch_id': min_batch})

                if remove_association_dict:
                    remove_status = associate_canister_with_analysis(remove_association_dict)
                    logger.info("In deactivate_mfd_canister: associate_canister_with_analysis status :{}".format(remove_status))
                    for system_id, locations in mfs_system_update.items():
                        mfs_update_deactivate_canister({'system_id': system_id, 'locations': locations})
        return create_response(update_status)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["system_id", "locations"])
def mfs_update_deactivate_canister(data_dict: dict) -> bool:
    """
    This Method will mark canister deactivates and remove its trolley association
    @param data_dict: data dict with required keys "company_id", "mfd_canister_id", "user_id"
    @return: dict - generated label name and canister data
    """
    system_id = data_dict['system_id']
    locations = data_dict['locations']
    try:
        status, document = get_document_from_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                      system_id=system_id)
        couch_db_doc = document.get_document()
        logger.info('current_couch_db_data' + str(couch_db_doc))
        couch_db_canister_data = couch_db_doc["data"].get('canister_data', {})
        for location in locations:
            location = str(location)
            couch_db_canister_data[location].update({
                'error_message': constants.MFD_ERROR_MESSAGES['DEACTIVATE_CANISTER'],
                'is_in_error': True,
                'transfer_done': False,
                'required_canister_id': None})
        status, doc = update_document_with_revision(document, couch_db_doc, False)
        logger.info("In mfs_update_deactivate_canister update_document_with_revision {}, {}".format(status, doc))
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def delete_update_manual_mfd_packs(batch_id: int, pack_list: list, pack_canister_dict: dict):
    """
    Function to update null configurations in
    pack analysis details for packs that can't be filled from MFD because number of locations in quadrant is very less
    and delete their info from mfd analysis and mfd analysis details
    @param pack_canister_dict:
    @param batch_id:
    @param pack_list:
    @return:
    """
    try:
        mfd_analysis_id_list = list()

        pack_analysis_ids = get_pack_analysis_details_ids_by_batch(batch_id=batch_id,
                                                                   pack_list=pack_list)
        logger.info("delete_update_manual_mfd_packs pack_analysis_ids {}".format(pack_analysis_ids))

        for pack in pack_list:
            mfd_analysis_id_list.extend(pack_canister_dict[pack])
        logger.info("delete_update_manual_mfd_packs mfd_analysis_id_list {}".format(mfd_analysis_id_list))

        pack_analysis_update = update_pack_analysis_details_by_analysis_id(analysis_ids=pack_analysis_ids)
        logger.info("delete_update_manual_mfd_packs updated in pack analysis details tables: {}".format(pack_analysis_update))
        mfd_analysis_delete = db_delete_mfd_analysis_by_analysis_ids(mfd_analysis_list=mfd_analysis_id_list)
        logger.info("delete_update_manual_mfd_packs deleted from mfd analysis tables : {}".format(mfd_analysis_delete))

        return True

    except Exception as e:
        logger.error("Error in delete_update_manual_mfd_packs {}".format(e))
        return False


@validate(required_fields=['user_id', 'company_id', 'device_id', 'display_locations'])
def disable_canister_location(request_args):
    """
    disables canister location and if canister is placed on that location then returns transfer data for that canister
    :param request_args:
    :return:
    """
    user_id = request_args['user_id']
    company_id = request_args['company_id']
    device_id = request_args['device_id']
    comment = request_args.get("comment", 'Test')
    display_locations = request_args['display_locations']

    try:
        with db.transaction():
            set_location_disable = None
            already_disabled_loc = list()
            valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
            if not valid_device:
                return error(1033)
            # display_locations = display_locations.split(",")
            location_info_list = list()
            canister_present_location_dict = dict()
            location_mfd_can_data = location_mfd_can_info(device_id, display_locations)
            for mfd_can_loc in location_mfd_can_data:
                if mfd_can_loc['is_disabled']:
                    already_disabled_loc.append(mfd_can_loc['display_location'])
                    continue
                if not mfd_can_loc['mfd_canister_id']:
                    current_time = get_current_date_time()
                    location_info = {"loc_id": mfd_can_loc['loc_id'],
                                     "created_by": user_id,
                                     "comment": comment,
                                     "start_time": current_time,
                                     "created_date": current_time
                                     }
                    location_info_list.append(location_info)
                else:
                    canister_present_location_dict[mfd_can_loc['display_location']] = {'mfd_canister_id': mfd_can_loc['loc_id'],
                                                                        'mfd_canister_rfid': mfd_can_loc['rfid']}

            if location_info_list:
                set_location_disable = set_location_disable_dao(disable_info_list=location_info_list)
            return create_response({'disable_location': set_location_disable,
                                    'already_disabled_loc': already_disabled_loc,
                                    'canister_present_location': canister_present_location_dict})

    except NoLocationExists as e:
        return error(1020, str(e))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def mark_mfd_canister_deactivate(mfd_canister_ids: list, user_id: int, update_location: bool = True) -> bool:
    """
    Method to validate mfd canister against company
    @mfd_canister_ids = list of canisters to be validated
    @company_id = registered company of mfd canisters
    @return: created_record
    """
    update_dict = {'state_status': 0, 'home_cart_id': None}
    if update_location:
        update_dict['location_id'] = None
    try:
        canister_history_update_list = list()
        status = mark_mfd_canister_deactivate_status_update(mfd_canister_ids, update_dict)
        for mfd_canister_id in mfd_canister_ids:
            history_dict = {
                'mfd_canister_id': mfd_canister_id,
                'current_location_id': None,
                'user_id': user_id,
                'is_transaction_manual': True
            }
            canister_history_update_list.append(history_dict)
        if canister_history_update_list:
            mfd_canister_history_update = update_mfd_canister_history(canister_history_update_list)
            logger.info("In mark_mfd_canister_deactivate: mfd canister history updated: {}".format(mfd_canister_history_update))
        return status
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in mark_mfd_canister_deactivate {}".format(e))
        raise e


@log_args_and_response
def update_trolley_seq_couchdb(request_args):
    """
    updates couch db doc for user access
    :param request_args: dict
    :return: boolean
    """

    try:
        for system_id, trolley_seq_id in request_args.items():
            module_data = {'trolley_seq': int(trolley_seq_id),
                           'trolley_uuid': uuid4().hex}
            status, couch_db_doc = get_mfd_module_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                           system_id)
            logger.info('In update_trolley_seq_couchdb: Before changing sequence: couchdb = ' + str(couch_db_doc))
            logger.info('In update_trolley_seq_couchdb: trolley_data = ' + str(module_data))
            couch_db_data = couch_db_doc.get("data", {})
            status, doc = update_mfd_module_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID, system_id, module_data)
            if not status:
                raise RealTimeDBException('Error while updating couch-db')
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e)
        logger.error("Error in update_trolley_seq_couchdb: {}".format(e))
        return False
    except Exception as e:
        logger.error(e)
        logger.error("Error in update_trolley_seq_couchdb: {}".format(e))
        return False

#
# @log_args_and_response
# def remove_notifications_for_skipped_mfs_filling(system_id, device_id, trolley_name):
#     try:
#         database_name = get_couch_db_database_name(system_id=system_id)
#         cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
#         cdb.connect()
#         id = 'mfd_notifications_{}'.format(device_id)
#         logger.info("notification_document_name: " + str(id))
#         table = cdb.get(_id=id)
#         if table is not None:
#             data = table.get("data", {})
#             if data:
#                 notification_data = table["data"].get("notification_data")
#                 if notification_data:
#                     notifications_list = list()
#                     robot_data = get_device_name_from_device([device_id])
#                     message_to_remove = constants.REQUIRED_MFD_CART_MESSAGE.format(trolley_name, robot_data[device_id])
#                     for record in notification_data:
#                         message = record['message']
#                         if message == message_to_remove:
#                             continue
#                         notifications_list.append(record)
#                     table['data']['notification_data'] = notifications_list
#                     logger.info("In remove_notifications_for_skipped_mfs_filling: notification_data {}".format(notifications_list))
#                     cdb.save(table)
#     except Exception as e:
#         logger.error(e)
#         logger.error("Error in remove_notifications_for_skipped_mfs_filling: {}".format(e))
#         raise e


@log_args_and_response
def get_mfd_batch_drugs(filter_fields, paginate):
    """
    get mfd drugs which will be used in batch and dimensions are verified.
    """

    try:
        mfd_data, count, drug_list = get_mfd_batch_drugs_dao(paginate, filter_fields)
        ndc_list = [item['ndc'] for item in mfd_data]
        change_ndc_drug_list = get_available_drugs_for_recommended_canisters(ndc_list)
        change_ndc_drug_list = [x.zfill(11) for x in change_ndc_drug_list]
        for record in mfd_data:
            record['change_ndc_available'] = True if record['ndc'] in change_ndc_drug_list else False
        response = {
            "mfd_data": mfd_data,
            "drug_list": drug_list,
            "count": count
        }
        return create_response(response)

    except Exception as e:
        logger.error(e)
        logger.error("Error in get_mfd_batch_drugs: {}".format(e))
        return e


@log_args_and_response
def update_mfd_data(args):
    try:
        canister_id_list = [args.get('canister_id')]
        company_id = args.get('company_id')
        device_id = args.get('device_id', None)
        system_id = args.get('system_id')

        response = use_other_canisters(device_id, canister_id_list, company_id, mfd_data=True)
        if isinstance(response, str):
            return response
        return create_response(response)
    except Exception as e:
        logger.error("Error in update_mfd_data: {}".format(e))
        return e


@log_args_and_response
def check_batch_drug(ndc, canister_id):
    """
    This function is used for the drug is used in current batch or not
    """
    try:
        response = check_batch_drug_dao(ndc)
        if not response:
            # device_id = None
            # affected_packs, device_id = get_affected_pack_list_for_canisters([canister_id])
            # if device_id:
            #     response = {"device_id": device_id}
            #     return create_response(response)
            # else:
            return error(21014)
        else:
            affected_pack_list, mfd_analysis_dict, analysis_ids, batch_id, drug_id, device_id = get_pending_mfd_pack_list_dao(
                [canister_id])
            response = {"device_id": device_id}
            return create_response(response)
    except Exception as e:
        logger.error("Error in check_batch_drug: {}".format(e))
        return e
