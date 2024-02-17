import base64
import copy
import datetime
import json
import logging
import math
import os
import sys
from collections import OrderedDict, defaultdict
from copy import deepcopy
from decimal import Decimal
from typing import List, Dict, Any
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

import pandas as pd
from numpy import nanmin
from peewee import InternalError, IntegrityError, DataError, DoesNotExist, Expression
from pytz import UnknownTimeZoneError

import settings
from com.pharmacy_software import send_data
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response, get_current_time, convert_date_to_sql_date, log_args, \
    get_current_day_date_end_date_by_timezone, fn_shorten_drugname, \
    fn_shorten_drugname_v2, batch as batchify, get_current_date, get_datetime, get_current_date_time, last_day_of_month, \
    convert_utc_timezone_into_local_time_zone
from dosepack.validation.validate import validate
from src import constants
from src.api_utility import get_results, getrecords
from src.cloud_storage import drug_blob_dir, blob_as_string, blob_exists, vial_label_dir, create_blob
from src.constants import MVS_OTHER, DELETE_PACK_DESC_SHARED_MFD, MVS_DRUGS_OUT_OF_STOCK, MVS_MISSING_PILLS
from src.dao.batch_dao import get_batch_id_from_pack_list, get_progress_batch_id, get_system_wise_batch_id, \
    update_batch_status_for_empty_pack_queue
from src.dao.canister_dao import db_get_canister_fndc_txr, update_replenish_based_on_system, \
    delete_reserved_canister_for_pack_queue, get_replenish_mini_batch_wise, db_get_total_canister_quantity_by_drug_id
from src.dao.company_setting_dao import get_ips_communication_settings_dao
from src.dao.device_manager_dao import validate_device_id_dao, get_mfs_system_device_from_company_id
from src.dao.drug_dao import get_label_drugs, update_drug_status_dao, get_fndc_txr_wise_inventory_qty, \
    db_get_drug_info_by_canister
from src.dao.drug_inventory_dao import drug_inventory_adjustment
from src.dao.ext_file_dao import db_check_rx_on_hold_for_pack
from src.dao.mfd_dao import db_update_drug_status
from src.dao.mfd_dao import get_batch_manual_drug_list
from src.dao.pack_analysis_dao import db_get_pack_manual_drug_count, get_robot_status, get_pack_status_from_ips, \
    db_fetch_fod_only_slots
from src.dao.pack_dao import db_get_batch_canister_manual_drugs, get_batch_scheduled_start_date_and_packs, \
    update_inventory_v2, update_set_last_seen, get_rx_wise_ndc_fill, verify_pack_list_by_company_id, \
    get_canister_skipped_drug_qty_per_slot, get_dropped_quadrant_data_slot_wise, \
    insert_data_in_pack_verification_and_pack_verification_details, db_get_pack_slot_transaction, \
    get_patient_packs, \
    db_check_change_rx_flag_for_pack, get_pending_packs_by_template_and_user, \
    db_get_mfd_analysis_info_old_packs, get_max_ext_data, \
    get_data_of_slot_with_fill_volume, get_pill_jump_error_slot_for_given_pack, get_drugs_of_reuse_pack_dao, \
    check_for_reuse_pack, get_pack_assigned_to, db_update_assigned_to_pack_details, add_missing_drug_record_dao, \
    db_get_notification_packs_to_update, get_all_same_drug_by_drug_id, get_filled_drug_count_slot_transaction, \
    get_mfd_filled_drug_count, get_manual_partially_filled_packs_drug_count, verify_pack_id_by_system_id, \
    find_filled_partially_packs, get_all_same_ndc_by_drug_id, db_fetch_nearest_exp_date_drug, get_packs_info_dao, \
    check_mfd_canister_on_mfs_station_or_not, db_get_expiry_soon_drug, db_get_packs_with_status, \
    db_get_prn_fill_details_dao, db_get_slot_wise_hoa_for_pack, db_fetch_reuse_pack_data, db_fetch_similar_pack_data, \
    db_check_packs_are_change_rx_or_not, \
    db_get_required_txr_for_packs, db_fetch_reusable_packs, db_discard_reuse_drug_in_reuse_pack_drug, \
    db_discard_pack_in_ext_pack_details_and_reuse_pack_drug, db_update_reuse_pack_drug_by_pack_id_drug_id_dao, \
    db_get_reuse_pack_drug_data_by_pack_id_dao, get_reuse_in_progress_pack_dao, get_reuse_pack_drug_data_dao, \
    db_get_pack_details_by_display_ids_dao, db_get_pack_drug_adjusted_quantity, generate_vial_label, \
    db_get_updated_quantity_data_for_label, db_get_drug_master_data_by_drug_id_dao, \
    get_ndc_list_for_vial_list_for_filling_screen, get_ndc_list_for_vial_list_for_prn_screen, \
    db_update_drugs_status_by_pack_id_dao, db_master_search_dao, db_person_master_search_dao
from src.dao.pack_dao import get_pending_progress_pack_count, get_unscheduled_packs_dao, \
    db_get_pack_and_drug_by_patient, get_pack_wise_delivery_date, db_get_half_pill_drug_drop_by_pack_id, \
    get_packs_by_facility, db_get_packs, db_get_packs_by_facility_id, get_incomplete_packs_for_given_time_and_status, \
    get_pack_details_dao, verify_pack_id, is_print_requested, db_get_pack_details_v2, get_mfd_trolley_for_pack, \
    get_trolley_analysis_ids_by_trolley_seq, check_transfer_filling_pending, db_get_mfd_slot_info, get_deleted_packs, \
    delete_partially_filled_pack, db_get_status_numeric, set_status_pack_details, get_sharing_packs, \
    track_consumed_packs, db_get_pack_display_ids, delete_pack_in_ips, db_get_pack_and_display_ids, \
    get_pending_pack_details_and_patient_name_with_past_delivery_date, \
    get_manual_pack_details_and_patient_name_with_past_delivery_date, \
    get_packs_with_status_partially_filled_by_robot_for_given_pack_display_ids, \
    get_pack_analysis_details_for_given_batch, get_mfd_automatic_packs, get_pack_history_by_pack_id, \
    get_pack_status_by_pack_list, get_patient_manual_packs, get_patient_data_for_packs, \
    db_get_slot_wise_drug_data_for_packs, get_batch_packs, get_drug_data_for_unique_fndc_txr_for_non_manual_packs, \
    add_variable_alternate_drug_available_in_drug_data, update_packs_in_pack_user_map, \
    get_similar_packs_manual_assign_dao, overload_pack_timing_update_or_create_record, set_fill_time_dao, \
    partially_filled_pack_dao, max_order_no, generate_test_packs_dao, db_get_unassociated_packs, \
    get_pack_user_map_dao, get_user_pack_stats_dao, get_manual_packs_data, \
    verify_pack_id_by_system_id_dao, slot_details_for_vision_system_dao, db_slots_for_user_station, \
    map_pack_location_dao, db_vision_slots_for_user_station, get_mfd_canister_drugs, db_get_label_info, \
    get_pharmacy_data_for_system_id, get_patient_details_for_patient_id, db_get_pack_info, get_location_id_from_display_location, db_create_multi_record_in_slot_transaction, \
    db_update_canister_data, get_pack_display_ids_for_given_packs, get_manual_pack_dao, get_user_assigned_packs_dao, \
    get_user_assigned_pack_count_dao, get_user_wise_pack_count_dao, get_pack_id_for_given_status_from_given_packs, \
    get_order_no_for_given_company_id, update_pack_details_for_pack_ids, get_batch_status_from_batch_id, \
    update_scheduled_start_date_for_next_batches, get_latest_print_data, \
    db_get_pvs_dimension, get_pack_grid_data_dao
from src.dao.misc_dao import get_system_setting_by_system_id
from src.dao.pack_errors_dao import db_slot_details_for_label_printing, db_update_drug_tracker_qty
from src.dao.pack_ext_dao import db_get_ext_pack_data_by_pack_ids_dao, \
    db_update_ext_pack_details_by_pack_id_dao
from src.dao.pack_queue_dao import remove_packs_from_queue, get_pack_queue_count
from src.dao.pack_user_map_dao import suggested_user_id_for_manual_packs_from_previous_record_dao
from src.dao.patient_dao import get_next_schedules
from src.dao.rph_verification_dao import db_verify_packlist_by_system, db_get_pack_display_by_pack_id
from src.exc_thread import ExcThread
from src.exceptions import RealTimeDBException, PharmacySoftwareResponseException, \
    PharmacySoftwareCommunicationException, AutoProcessTemplateException
from src.independentclusters import PriorityQueue
from src.label_printing.generate_label import remove_files
from src.model.model_pack_details import PackDetails
from src.model.model_pack_rx_link import PackRxLink

from src.model.model_pill_fill_error import PillJumpError
from src.dao.company_setting_dao import get_ips_communication_settings_dao
from src.service.drug_inventory import check_and_update_drug_req, inventory_adjust_quantity

from src.service.notifications import Notifications
from src.pack_utilities import create_slot
from src.service.drug_tracker import populate_drug_tracker
from src.service.mfd import update_transfer_wizard, update_rts_data
from src.service.notifications import Notifications
from src.service.misc import get_all_dates_between_two_dates, update_manual_packs_count_after_change_rx, \
    update_assigned_to_in_notification_dp_all_for_change_rx_packs, get_token, get_current_user, get_users_by_ids
from src.service.print_label import get_pvs_data
from src.service.revert_batch import reset_mfs_couch_db_documents_batch_revert
from src.service.volumetric_analysis import get_available_drugs_for_recommended_canisters
from static.sample_response import getlabelinfosample
from tasks.celery import celery_app
from utils.auth_webservices import send_email_for_pending_packs_with_past_delivery_date
from src.dao.drug_tracker_dao import get_slot_is_filled, get_drug_is_filled_in_drug_list, \
    drug_tracker_create_multiple_record, db_get_lot_details_by_slot_id
from utils.drug_inventory_webservices import update_drug_inventory_for_same_drug_ndcs, drug_inventory_api_call, \
    create_item_vial_generation_for_rts_reuse_pack, drug_inventory_general_api, get_current_inventory_data
from src.dao.misc_dao import get_company_setting_by_company_id

logger = logging.getLogger("root")


@log_args_and_response
def get_pack_count_for_canister_skip(company_id: int, system_id: int, batch_id: int, canister_id: int, device_id: int):
    """
    Function to get pack count for which these canisters can be skipped, based on number of packs
    that can be processed in pending hours of the day i.e skip for day
    @param company_id:
    @param batch_id:
    @param canister_id:
    @param device_id:
    @return:
    """
    logger.debug("Inside get_pack_count_for_canister_skip")
    try:
        no_of_packs_to_skip = 0
        # define default format of time
        FMT = '%H:%M:%S'
        current_time = get_current_time()
        current_time_formatted = datetime.datetime.strptime(
            current_time, FMT)
        logger.info("get_pack_count_for_canister_skip current_time {}, {}".format(current_time, current_time_formatted))
        formatted_ndc, txr = db_get_drug_info_by_canister(canister_id)['fndc_txr'].split('#')
        inventory_data = get_fndc_txr_wise_inventory_qty([txr])
        inventory_qty = inventory_data.get((formatted_ndc, txr), 0)
        # get system day end time
        system_info = get_system_setting_by_system_id(system_id=system_id)
        logger.info("In get_pack_count_for_canister_skip, system_info {}".format(system_info))

        automatic_per_hour = int(system_info['AUTOMATIC_PER_HOUR'])
        automatic_day_end_time = float(system_info['AUTOMATIC_DAY_END_TIME'])

        day_end_time_in_hour = str(datetime.timedelta(hours=automatic_day_end_time))
        day_end_time_in_hour_formatted = datetime.datetime.strptime(day_end_time_in_hour, FMT)
        logger.info("get_pack_count_for_canister_skip day_end_time_in_hour {}".format(day_end_time_in_hour))

        # if current time is less than pharmacy day end time
        if current_time_formatted < day_end_time_in_hour_formatted:
            # get pending hours calculate packs that can be skipped considerin system capacity per hour
            remaining_time_in_seconds = (day_end_time_in_hour_formatted - current_time_formatted).seconds
            logger.info(
                "get_pack_count_for_canister_skip remaining_time_in_seconds {}".format(remaining_time_in_seconds))

            remaining_time_in_float = remaining_time_in_seconds / settings.AUTO_SECONDS
            logger.info("get_pack_count_for_canister_skip remaining_time_in_float {}".format(remaining_time_in_float))

            if remaining_time_in_float > 0:
                no_of_packs_to_skip = math.ceil((remaining_time_in_float * automatic_per_hour) / 2)

        # get pack count by status id
        packs_list_pending \
            = get_pending_progress_pack_count(system_id,
                                              [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                                              device_id, batch_id)

        batch_pack_count = len(packs_list_pending)

        logger.info(
            "In get_pack_count_for_canister_skip; batch pack count, no of pack to skip, pack count {}, {}, {}".format(
                batch_pack_count,
                no_of_packs_to_skip,
                packs_list_pending))

        if no_of_packs_to_skip > batch_pack_count:
            no_of_packs_to_skip = batch_pack_count

        response = {
            'packs_to_skip': no_of_packs_to_skip,
            'batch_pack_count': batch_pack_count,
            'inventory_qty': inventory_qty
        }
        return response

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in get_pack_count_for_canister_skip {}".format(e))
        raise e


@validate(required_fields=['pack_list'])
@log_args_and_response
def get_unscheduled_packs(args):
    logger.debug("Inside get_unscheduled_packs")
    try:
        pack_list = args['pack_list']
        logger.info("In get_unscheduled_packs, pack_list: {}".format(pack_list))

        list_of_unscheduled_packs = []

        for pack_id in pack_list:
            unscheduled_pack_data = get_unscheduled_packs_dao(pack_id)
            if len(unscheduled_pack_data) > 0:
                list_of_unscheduled_packs.append(unscheduled_pack_data)

        logger.info("In get_unscheduled_packs, list_of_unscheduled_packs: {}".format(list_of_unscheduled_packs))

        return create_response(list_of_unscheduled_packs)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in get_unscheduled_packs {}".format(e))
        raise e


@validate(required_fields=['company_id', 'percentage_packs_for_manual_system', 'pack_list',
                           'maximum_allowed_manual_fill_for_automatic_system'])
@log_args_and_response
def get_manual_packs_with_optimised_manual_fill(args):
    """
    Returns canister packs and manual packs
    :return: json
    """
    logger.info("Inside get_manual_packs_with_optimised_manual_fill")

    company_id = args['company_id']
    user_hours = args.get('user_hours', None)

    logger.info('args for get_manual_packs_with_optimised_manual_fill: {}'.format(args))

    percentage_packs_for_manual_system = args['percentage_packs_for_manual_system']
    percentage_packs_for_automatic_system = 100 - percentage_packs_for_manual_system
    maximum_allowed_manual_fill_for_automatic_system = args['maximum_allowed_manual_fill_for_automatic_system']
    import_state = args.get('import_state', False)
    pack_half_pill_drug_drop_count = dict()
    pack_list_main = args.get("pack_list")

    try:
        # prioritize users based on decreasing order of their working hours
        if user_hours is not None:
            user_hours = OrderedDict(sorted(user_hours.items(), key=lambda x: int(x[1]), reverse=True))

        # parameters to shift packs to robot if pack has more than max_pack_drugs drugs and has canister drugs more than or
        # equal to min_robot_drugs
        try:
            patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(company_id, pack_list_main)
            logger.info(
                "In get_manual_packs_with_optimised_manual_fill, patient_packs:{}, patient_drugs: {}".format(patient_packs,
                                                                                                             patient_drugs))

            patient_delivery_date_dict = get_pack_wise_delivery_date(pack_list_main)

            logger.info("In get_manual_packs_with_optimised_manual_fill, patient_delivery_date_dict: {}".format(
                patient_delivery_date_dict))

            remaining_patient = set()
            pack_list = []

            # list created to add packs with delivery date null. Case added to send pack for manual with delivery date null
            pack_list_null_delivery_date = []
            for patient, packs in patient_packs.items():
                if patient in patient_delivery_date_dict:
                    pack_list.extend(packs)
                else:
                    pack_list_null_delivery_date.extend(packs)
            #     if patient_delivery_date_dict[patient] != None:
            #         pack_list.extend(packs)
            #     else:
            #         remaining_patient.add(patient)
            # print("remaining packs", remaining_patient)
            # for each_patient in remaining_patient:
            #     del patient_packs[each_patient]

            canister_drugs = db_get_canister_fndc_txr(company_id)

            if len(pack_list) > 0:
                pack_half_pill_drug_drop_count = db_get_half_pill_drug_drop_by_pack_id(pack_list)

        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            return error(2001)

        manual_packs = set()
        canister_packs = set()
        manual_packs_by_user = {}
        manual_split_info_dict = {}
        for maximum_manual_count in range(maximum_allowed_manual_fill_for_automatic_system):
            manual_split_info_dict[maximum_manual_count] = {'manual_packs': 0, 'canister_packs': 0}
        total_packs = set([])
        for patient_specific_packs in patient_packs.values():
            total_packs |= patient_specific_packs
        number_of_total_packs = len(total_packs)
        maximum_allowed_canister_packs = (percentage_packs_for_automatic_system * number_of_total_packs) / 100
        patient_can_drug_manual_drug_len_data_list = []
        for patient in list(patient_drugs.keys()):
            patient_drugs_set = patient_drugs[patient]
            patient_drug_length = len(patient_drugs_set)
            patient_canister_drugs = patient_drugs_set & canister_drugs
            patient_canister_drug_length = len(patient_canister_drugs)
            patient_manual_drug_length = patient_drug_length - patient_canister_drug_length
            patient_can_drug_manual_drug_len_data_list.append(
                (patient, patient_manual_drug_length, patient_canister_drug_length))

        # sorting patient_can_drug_manual_drug_len_data_list, we will first sort based on manual drug length in ascending
        # order and after that sort based on can_drug_len in descending order
        new_patient_can_drug_manual_drug_len_data_list = []
        for patient, patient_manual_drug_length, patient_canister_drug_length in patient_can_drug_manual_drug_len_data_list:
            packs_for_given_patient = patient_packs[patient]
            for pack in packs_for_given_patient:
                pack = int(pack)
                if pack not in pack_half_pill_drug_drop_count:
                    continue
                else:
                    patient_manual_drug_length += 1 + int(pack_half_pill_drug_drop_count[pack] / 7)
                    # patient_canister_drug_length -= 1 + int(pack_half_pill_drug_drop_count[pack]/7)
            new_patient_can_drug_manual_drug_len_data_list.append(
                (patient, patient_manual_drug_length, patient_canister_drug_length))
        sorted_patient_len_data = sorted(new_patient_can_drug_manual_drug_len_data_list, key=lambda x: (x[1], -x[2]))

        logger.info(
            "In get_manual_packs_with_optimised_manual_fill, sorted patient len data {}".format(sorted_patient_len_data))

        copy_sorted_patient_len_data = deepcopy(sorted_patient_len_data)
        new_list = []
        for tuple in sorted_patient_len_data:
            if tuple[2] == 0:
                ind = copy_sorted_patient_len_data.index(tuple)
                copy_sorted_patient_len_data.pop(ind)
                new_list.append(tuple)
        copy_sorted_patient_len_data.extend(new_list)
        sorted_patient_len_data = copy_sorted_patient_len_data
        for patient, patient_manual_drug_length, patient_canister_drug_length in sorted_patient_len_data:
            packs_for_given_patient = patient_packs[patient]
            if len(canister_packs) + len(packs_for_given_patient) <= maximum_allowed_canister_packs:
                canister_packs.update(packs_for_given_patient)
            else:
                manual_packs.update(packs_for_given_patient)
            for maximum_manual_count in manual_split_info_dict.keys():
                if patient_manual_drug_length <= maximum_manual_count and patient_canister_drug_length == 0:
                    manual_split_info_dict[maximum_manual_count]["manual_packs"] += len(packs_for_given_patient)
                elif patient_manual_drug_length <= maximum_manual_count:
                    manual_split_info_dict[maximum_manual_count]["canister_packs"] += len(packs_for_given_patient)
                else:
                    manual_split_info_dict[maximum_manual_count]["manual_packs"] += len(packs_for_given_patient)

        if user_hours:
            manual_packs_by_user = dict()
            for user in user_hours:
                manual_packs_by_user[user] = set()

            if len(manual_packs) > 0:

                logger.info(
                    "In get_manual_packs_with_optimised_manual_fill, len of manual packs: {}".format(len(manual_packs)))

                manual_packs = list(map(int, manual_packs))
                logger.info("In get_manual_packs_with_optimised_manual_fill, manual_packs: {}".format(manual_packs))

                manual_packs_by_user = manual_user_distribution_flow_handler(user_hours, manual_packs, company_id)

            if import_state and len(pack_list_null_delivery_date) > 0:

                patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(company_id, pack_list_null_delivery_date)

                logger.info("In get_manual_packs_with_optimised_manual_fill, patient_packs: {}, patient_drugs: {}".format(
                    patient_packs, patient_drugs))

                for patient, packs in patient_packs.items():
                    user = min(manual_packs_by_user, key=lambda k: len(manual_packs_by_user[k]))
                    manual_packs_by_user[user].update(packs)

            response = {'manual_packs_by_user': manual_packs_by_user,
                        'manual_packs': manual_packs,
                        'canister_packs': canister_packs,
                        'manual_split_info_dict': manual_split_info_dict}
        else:
            response = {'manual_packs': manual_packs,
                        'canister_packs': canister_packs,
                        'manual_split_info_dict': manual_split_info_dict}

        return create_response(response)

    except Exception as e:
        logger.error("Error in get_manual_packs_with_optimised_manual_fill: {}".format(e))
        raise


@log_args_and_response
def manual_user_distribution_flow_handler(user_hours, manual_packs, company_id):
    """
    Args is a dictionary which has all the data needed for distribution.
    It contains following keys.
    - user_hours:- Manual user and corresponding working hours for which we will distribute the packs
    - manual_packs:- These are the packs which we are supposed to distribute between users.
    - company_id

    Flow of the method will be as follows:
    1) Prepare needed data structures for manual distribution flow.
    :param args: manual_packs, company_id
    :return: datewise_manual_patient_dict, patient_packs
    """
    try:

        logger.debug("Inside manual_user_distribution_flow_handler")

        datewise_manual_patient_dict = {}
        user_wise_split = dict()
        hours_list = list()

        patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(company_id, manual_packs)

        logger.info(
            "In manual_user_distribution_flow_handler; patient_packs: {}, patient_drugs: {}".format(patient_packs,
                                                                                                    patient_drugs))

        # total_patients = [patient for patient in patient_packs.keys()]
        patient_delivery_date_dict = get_pack_wise_delivery_date(manual_packs)

        logger.info("In manual_user_distribution_flow_handler, patient_delivery_date_dict: {}".format(
            patient_delivery_date_dict))

        for p, d in patient_delivery_date_dict.items():

            if d not in datewise_manual_patient_dict:
                datewise_manual_patient_dict[d] = set()
            datewise_manual_patient_dict[d].add(p)

        datewise_manual_patient_dict = OrderedDict(sorted(datewise_manual_patient_dict.items(), key=lambda x: x[0]))

        logger.info("In manual_user_distribution_flow_handler, datewise_manual_patient_dict: {}".format(
            datewise_manual_patient_dict))

        """
        2) Divide packs based on number of users and corresponding working hours
        We have followed following formula:
        
        Pack count of user1 = (Total number of Packs X Working hours of user1)/(Total working hours of all users)
        :param args:datewise_manual_patient_dict, user_list, patient_packs
        :return: user_pack_list
        
        """

        # calculating total work hours
        for user in user_hours:
            hours_list.append(int(user_hours[user]))
        total_hours = sum(hours_list)

        logger.info("In manual_user_distribution_flow_handler, Total working hours {}:".format(total_hours))
        logger.info("In manual_user_distribution_flow_handler, Total manual packs {}:".format(len(manual_packs)))

        # calculating user wise hour wise manual
        for user in user_hours:
            user_wise_split[user] = math.ceil(len(manual_packs) * int(user_hours[user]) / total_hours)

        logger.info("In manual_user_distribution_flow_handler, User wise manual_pack_split {}:".format(user_wise_split))

        manual_pack_by_user = divide_packs_for_manual_users(datewise_manual_patient_dict, user_hours, user_wise_split,
                                                            patient_packs, company_id, manual_packs)

        print("user pack list", manual_pack_by_user)

        return manual_pack_by_user

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error("Error in db_get_pack_and_drug_by_patient: {}".format(e))
        raise


def divide_packs_for_manual_users(datewise_manual_patient_dict, user_hours, user_wise_split, patient_packs, company_id,
                                  manual_packs):
    """
    In this method packs are divided to users.
    :param args: datewise_manual_patient_dict, user_hours, patient_packs
    :return: manual_packs_by_user (dict having set of packs allocated to each user)

    Flow of this method will be looping over each date and then:
    1) create  facility_packs (facility wise set of packs) dict with help of list of packs.
       :params : facility_pack_count - key: facility_id , values: set of packs by facility
              sorted_facility_pack_count - sorted dict of facility_pack-count

    2) assign one by one pack to each user
       :params : split, free space (number of more packs for that user)
               list_of_packs - to maintain the count of packs remaining to allocate and create
                            pack list of patients of each facility used to create the facility_packs
               user_pack_list - key: user_id , values : set of packs
               facility_patient_packs - dict having key as patient and set of packs as value
               user_list - sorted user list in descending order of their remaining packs
               date_user_pack_dict - dictionary having date as key and user wise allocated packs as value.

    3) Before allocating patient pack to user check whether adding these packs will increase the pack count
       greater than split and if other user have split capacity available for these patient packs

    5) Sort the user_list so as the user having less number of packs goes first on the loop
    :params : manual_packs_by_user - key : user_id, values: total number of packs alllocated to user

    """
    logger.info("Inside divide_packs_for_manual_users")
    date_user_pack_dict = {}
    date_user_pack_count = {}
    manual_packs_by_user = {}

    try:
        user_list = list(user_hours.keys())
        for user_id in user_list:
            manual_packs_by_user[user_id] = set()

        for date, packs in datewise_manual_patient_dict.items():
            user_pack_list = {}
            split = {}
            for user in user_list:
                user_pack_list[user] = set()
            list_of_packs = []
            for patient in packs:
                for p in patient_packs[patient]:
                    list_of_packs.append(p)
            # split = math.ceil(len(list_of_packs) / len(user_list))
            facility_pack_count = {}

            facility_packs = get_packs_by_facility(pack_list=list_of_packs)
            logger.info("In divide_packs_for_manual_users, facility_packs: {}".format(facility_packs))

            for facility, packs in facility_packs.items():
                facility_pack_count[facility] = len(packs)
            sorted_facility_pack_count = OrderedDict(
                sorted(facility_pack_count.items(), key=lambda x: x[1], reverse=True))
            copy_sorted_facility = deepcopy(sorted_facility_pack_count)

            user_remaining_pack_count = {}

            while not len(copy_sorted_facility.keys()) == 0:
                facility = list(copy_sorted_facility)[0]
                logger.info("In divide_packs_for_manual_users, facility: {}".format(facility))

                del copy_sorted_facility[facility]
                for user in user_list:
                    if len(facility_packs[facility]) <= (user_wise_split[user] - len(manual_packs_by_user[user])):
                        user_pack_list[user].update(facility_packs[facility])
                        for one_pack in facility_packs[facility]:
                            list_of_packs.remove(str(one_pack))
                        del facility_packs[facility]
                        del sorted_facility_pack_count[facility]
                        break
                # user_list.clear()
                # for k in sorted(user_pack_list, key=lambda k: len(user_pack_list[k])):
                #     user_list.append(k)

                user_pack_count = {}
                user_remaining_pack_count = {}
                for user in user_list:
                    user_pack_count[user] = len(manual_packs_by_user[user]) + len(user_pack_list[user])
                    user_remaining_pack_count[user] = user_wise_split[user] - user_pack_count[user]
                user_list.clear()
                for k in sorted(user_remaining_pack_count, key=lambda k: user_remaining_pack_count[k], reverse=True):
                    user_list.append(k)

            if len(sorted_facility_pack_count) != 0:
                packs_set = set()
                for facility in sorted_facility_pack_count.keys():
                    packs_set.update(facility_packs[facility])

                s_facility_patient_packs, patient_drugs = db_get_pack_and_drug_by_patient(company_id,
                                                                                          list(packs_set))

                logger.info("In divide_packs_for_manual_users, s_facility_patient_packs: {}, patient_drugs: {}".format(
                    s_facility_patient_packs, patient_drugs))

                facility_patient_packs = OrderedDict(
                    sorted(s_facility_patient_packs.items(), key=lambda x: len(x[1]), reverse=True))

                user_cluster_list = PriorityQueue()
                logger.info("In divide_packs_for_manual_users, user_cluster_list: {}".format(user_cluster_list))

                for user in user_list:
                    new_dict = {"cluster": [], "user": user}
                    user_cluster_list.push(new_dict, len(user_pack_list[user]))

                configuration_priority_queue = PriorityQueue()

                for patient, packs in facility_patient_packs.items():
                    priority = -1 * len(packs)
                    configuration_priority_queue.push(patient, priority)

                while not configuration_priority_queue.isEmpty():
                    # print("item", item, "number of packs", priority_for_item)
                    user_cluster, priority_for_cluster = user_cluster_list.pop()
                    # print("robot cluster", robot_cluster, "number of packs", priority_for_cluster)
                    user = user_cluster["user"]
                    if user_remaining_pack_count[user] >= priority_for_cluster:
                        item, priority_for_item = configuration_priority_queue.pop()
                        priority_for_item *= -1
                        user_cluster["cluster"].append(item)
                        priority_for_cluster += priority_for_item
                    else:
                        priority_for_cluster = len(manual_packs) + 1
                    user_cluster_list.push(user_cluster, priority_for_cluster)

                while not user_cluster_list.isEmpty():
                    user_clust, number_of_packs = user_cluster_list.pop()
                    packs = set()
                    for patient in user_clust["cluster"]:
                        packs.update(facility_patient_packs[patient])
                    user_pack_list[user_clust["user"]].update(packs)

            logger.info("In divide_packs_for_manual_users, user_pack_list: {}".format(user_pack_list))
            user_pack_count = {}

            for user, packs in user_pack_list.items():
                user_pack_count[user] = len(packs)
            date_user_pack_count[str(date)] = user_pack_count
            date_user_pack_dict[str(date)] = user_pack_list

            for user, packs in user_pack_list.items():
                manual_packs_by_user[user].update(map(str, packs))
            # user_list.clear()
            # # for k in sorted(manual_packs_by_user, key=lambda k: len(manual_packs_by_user[k])):
            # for k in manual_packs_by_user:
            #     user_list.append(k)

        logger.info("In divide_packs_for_manual_users, date user pack count {}".format(date_user_pack_count))
        logger.info("In divide_packs_for_manual_users, date user pack dict {}".format(date_user_pack_dict))

        return manual_packs_by_user

    except Exception as e:
        logger.error("Error in divide_packs_for_manual_users: {}".format(e))
        raise


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
    logger.debug("Inside get_packs")
    try:
        results = db_get_packs(
            date_from, date_to, status, filter_fields, company_id,
            system_id=system_id,
            all_flag=all_flag,
        )
        logger.info("In get_packs, results: {}".format(results))

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

        response = {
            'pack_list': packs,
            'schedule_list': schedule_data,
            'schedule_ids': schedule_ids,
            'batch_ids': batches,
            'schedule_facility_ids': schedule_facility_ids,
        }

        logger.info("In get_packs, response: {}".format(response))

        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_packs: {}".format(e))
        raise


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
    logger.debug("Inside get_packs_of_facility")

    date_from, date_to = convert_date_to_sql_date(search_filters['date_from'], search_filters['date_to'])
    company_id = search_filters["company_id"]
    system_id = search_filters.get("system_id", None)
    all_flag = search_filters.get('all_flag', False)
    facility_id = search_filters["facility_id"]
    status = [int(item) for item in str(search_filters["pack_status"]).split(',')]
    filter_fields = search_filters.get('filter_fields', None)
    try:
        response = db_get_packs_by_facility_id(
            date_from, date_to, status, facility_id, filter_fields, company_id,
            system_id=system_id,
            all_flag=all_flag,
        )
        logger.debug("In get_packs_of_facility, Packs data retrieved")
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

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
    logger.debug("Inside get_incomplete_packs")

    date_from, date_to = convert_date_to_sql_date(search_filters['date_from'], search_filters['date_to'])
    system_id = search_filters["system_id"]
    status = settings.PROGRESS_PACK_STATUS

    try:

        response = get_incomplete_packs_for_given_time_and_status(date_from, date_to, status, system_id)

        logger.info("In get_incomplete_packs, response: {}".format(response))

    except InternalError:
        return error(2001)
    except Exception as e:
        logger.error("Error in get_incomplete_packs: {}".format(e))
        raise e

    return create_response(response)


@log_args_and_response
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
    logger.debug("Inside get_pack_details")
    pack_id = dict_pack_info["pack_id"]
    device_id = dict_pack_info["device_id"]
    company_id = dict_pack_info["company_id"]
    non_fractional = dict_pack_info.get("non_fractional", False)
    mft_slots = dict_pack_info.get("mft_slots", False)
    print_status = dict_pack_info.get("print_status", False)
    user_id = dict_pack_info.get("user_id", None)
    module_id = dict_pack_info.get("module_id", None)

    valid_pack = verify_pack_id(pack_id, company_id)
    if not valid_pack:
        return error(1026)

    if "device_id" in dict_pack_info and dict_pack_info["device_id"] and company_id:
        device_id = dict_pack_info["device_id"]
        valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
        if not valid_device:
            return error(1033)

    try:
        response = get_pack_details_dao(pack_id,
                                        device_id,
                                        company_id=company_id,
                                        non_fractional=non_fractional, module_id=module_id)

        logger.info("In get_pack_details, response: {}".format(response))
        response['suggested_manual_user'] = None
        if user_id:
            response['suggested_manual_user'] = suggested_user_id_for_manual_packs_from_previous_record_dao(user_id)
        if print_status:
            if response.get("pack_status_id") == settings.PARTIALLY_FILLED_BY_ROBOT:
                response['print_requested'] = False
            else:
                response['print_requested'] = is_print_requested(pack_id)

        return create_response(response)
    except InternalError:
        return error(2001)
    except Exception as e:
        logger.error("Error in get_pack_details")
        return error(0, e)


@log_args_and_response
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
    logger.debug("Inside get_pack_details_v2")

    pack_id = dict_pack_info["pack_id"]
    device_id = dict_pack_info["device_id"]
    company_id = dict_pack_info["company_id"]
    non_fractional = dict_pack_info.get("non_fractional", False)
    mft_slots = dict_pack_info.get("mft_slots", False)
    print_status = dict_pack_info.get("print_status", False)
    exclude_pack_ids = dict_pack_info.get("exclude_pack_ids", None)

    valid_pack = verify_pack_id(pack_id, company_id)

    if not valid_pack:
        return error(1026)

    if "device_id" in dict_pack_info and dict_pack_info["device_id"] and company_id:
        device_id = dict_pack_info["device_id"]
        valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
        if not valid_device:
            return error(1033)

    try:
        response = db_get_pack_details_v2(
            pack_id, device_id, company_id=company_id,
            non_fractional=non_fractional, exclude_pack_ids=exclude_pack_ids
        )

        logger.info("In get_pack_details_v2, response of db_get_pack_details_v2: {}".format(response))

        if mft_slots and device_id:
            response['mfd_slot_data'] = dict()

            trolley_data = get_mfd_trolley_for_pack(pack_id)

            logger.debug('In get_pack_details_v2; Trolley_data_for_pack_id: {} is {}'.format(pack_id, trolley_data))

            mfd_analysis_ids = []

            if trolley_data:
                mfd_analysis_ids, mfs_system_mapping, dest_devices, batch_system = get_trolley_analysis_ids_by_trolley_seq(
                    trolley_data['batch_id'], trolley_data['trolley_seq'])

            logger.debug(
                'In get_pack_details_v2, mfd_analysis_ids_for_pack_id: {} are: {}'.format(pack_id, mfd_analysis_ids))

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
                                                    response['error_canisters'])

                response['mfd_slot_data'] = mfd_response['mfd_slot_data']
                response['drop_data'] = mfd_response['mfd_dop_data']
                response['error_canisters'] = mfd_response['error_canisters']

        if print_status:
            response['print_requested'] = is_print_requested(pack_id)

        slot_volume_dict = get_data_of_slot_with_fill_volume(pack_id=pack_id)

        logger.info(f"In get_pack_details_v2, slot_volume_dict:{slot_volume_dict}")

        response["slot_volume_dict"] = slot_volume_dict

        return create_response(response)
    except InternalError:
        return error(2001)


@log_args_and_response
def stop_pack_filling(dict_pack_info):

    try:
        user_id = dict_pack_info["user_id"]
        pack_id = dict_pack_info["pack_id"]
        fill_time = dict_pack_info.get('fill_time', None)

        if isinstance(pack_id, list):
            pack_ids = list()
            for indi_pack in pack_id:
                pack_ids.append(int(indi_pack))
        if isinstance(pack_id, str):
            pack_ids = list(map(lambda x: int(x), pack_id.split(',')))  # use if multiple packs are needed
        if isinstance(pack_id, int):
            pack_ids = [int(pack_id)]
        print(pack_ids)

        # for the available packs check any pack is filled partially or not
        filled_partially_packs = find_filled_partially_packs(pack_ids=pack_ids,
                                                             fill_time=fill_time,
                                                             user_id=user_id
                                                             )
        logger.info("In stop_pack_filling: filled_partially_packs: {}".format(filled_partially_packs))

        # if we find the filled partially packs then remove those pack from the packs which are
        # going for the manual
        if filled_partially_packs:
            pack_ids = set(pack_ids) - set(filled_partially_packs)
            pack_ids = list(pack_ids)

        logger.info("In stop_pack_filling: pack_ids after checking filled partially packs or not: {}".format(pack_ids))

        if not pack_ids:
            return create_response(True)
        else:
            dict_pack_info["pack_id"] = pack_ids
            logger.info("In stop_pack_filling: dict_pack_info after changes: {}".format(dict_pack_info))
            response = set_status(dict_pack_info)
            return response
    except Exception as e:
        logger.error("Error in stop_pack_filling: {}".format(e))
        raise e


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
    logger.debug('Inside set_status, args: ' + str(dict_pack_info))

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
    change_rx: bool = dict_pack_info.get('change_rx', False)
    change_rx_token: str = dict_pack_info.get("change_rx_token", "")
    device_id = dict_pack_info.get("device_id")
    update_replenish_data = True
    # We are capturing the following values while user marks any pack as Filled Manually from MVS
    # Reason: Missing Pills OR Drugs Out of Stock
    reason_action: int = dict_pack_info.get("reason_action", MVS_OTHER)
    reason_rx_no_list: List[str] = dict_pack_info.get("reason_rx_no_list", None)
    drug_list: List[int] = dict_pack_info.get("drug_list", None)
    missing_drug_mapping_dict: Dict[str, Any] = dict()
    pack_and_display_ids: Dict[int, int] = dict()
    delete_all_packs: bool = dict_pack_info.get("delete_all_packs", False)
    pack_ids_with_no_transfer_mfd_canister = list()
    module_id = dict_pack_info.get("module_id", 0)
    token = get_token()

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
        valid_packlist = verify_pack_list_by_company_id(pack_list=pack_ids, company_id=company_id)
        if not valid_packlist:
            return error(1026)

    if system_id and not use_company_id:
        valid_packlist = db_verify_packlist_by_system(pack_ids=pack_ids, system_id=system_id)
        if not valid_packlist:
            return error(1014)
    if status == settings.DELETED_PACK_STATUS:
        if not reason or reason == "" or None:
            return error(1001, "Missing Parameter(s): reason for deleted pack")

    try:
        with db.transaction():
            # check if current status of the pack is deleted then add record in pack history
            # if status is done else return error
            logger.debug("In set_status: call to mark packs- {} as {}".format(pack_ids, status))

            deleted_pack_ids, deleted_pack_display_ids = get_deleted_packs(pack_ids=pack_ids, company_id=company_id)

            logger.info("In set_status; deleted_pack_ids: {}, deleted_pack_display_ids: {}".format(deleted_pack_ids,
                                                                                            deleted_pack_display_ids))

            # if deleted packs found then remove this deleted packs from pack_ids
            if deleted_pack_ids:

                logger.debug("In set_status: deleted packs found-{}".format(deleted_pack_ids))

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
            logger.debug('In set_status, forced_pack_manual: {}'.format(forced_pack_manual))

            logger.debug('In set_status, change_rx: {}'.format(change_rx))
            logger.debug('If Delete is due to ChangeRx then we do not need to delete extra related MFD packs. '
                         'Only Delete the packs that are requested.')
            # -- delete_all_packs will be True then we can ignore change_rx flag and continue to delete the
            # shared MFD packs.
            # -- This will happen when we have to process New packs for Change Rx and delete Old packs including
            # removing their entries related to MFD, if any exists.
            if (status in [settings.MANUAL_PACK_STATUS, settings.DELETED_PACK_STATUS, settings.PROCESSED_MANUALLY_PACK_STATUS] or forced_pack_manual) and \
                    (not change_rx):
                affected_mfd_pack_ids, affected_mfd_canister_ids, affected_mfd_analysis_details_ids, canisters_filled = \
                    get_sharing_packs(pack_ids, forced_pack_manual, status_changed_from_ips)

                logger.info('In set_status, affected_mfd_analysis_ids: {} affected_mfd_analysis_details_ids {}'.format(
                    affected_mfd_canister_ids, affected_mfd_analysis_details_ids))

                packs_having_mfd_canister = set(pack_ids).intersection(set(affected_mfd_pack_ids))
                extra_mfd_packs = set(affected_mfd_pack_ids) - packs_having_mfd_canister

                # check whether the mfd_canister for the given pack_ids still available on the MFS station
                pack_ids_with_no_transfer_mfd_canister, mfd_analysis_ids_with_no_transfer_mfd_canister, \
                    mfd_analysis_details_id_with_no_transfer_mfd_canister = \
                    check_mfd_canister_on_mfs_station_or_not(pack_ids)

                logger.info("In set_status: pack_ids_with_no_transfer_mfd_canister: {}, "
                            "mfd_analysis_ids_with_no_transfer_mfd_canister: {}, "
                            "mfd_analysis_details_id_with_no_transfer_mfd_canister: {}"
                            .format(pack_ids_with_no_transfer_mfd_canister,
                                    mfd_analysis_ids_with_no_transfer_mfd_canister,
                                    mfd_analysis_details_id_with_no_transfer_mfd_canister
                                    ))

                if pack_ids_with_no_transfer_mfd_canister and user_confirmation:
                    pack_ids = set(pack_ids) - set(pack_ids_with_no_transfer_mfd_canister.keys())
                    pack_ids = list(pack_ids)

                    affected_mfd_canister_ids = set(affected_mfd_canister_ids) - set(mfd_analysis_ids_with_no_transfer_mfd_canister)

                    affected_mfd_analysis_details_ids = set(affected_mfd_analysis_details_ids) - set(mfd_analysis_details_id_with_no_transfer_mfd_canister)

                logger.info("In set_status: pack_ids: {}, mfd_analysis_id: {}, mfd_analysis_details_id: {} "
                            "after checking the mfd_canister transfer with user_confirmation: {}"
                            .format(pack_ids, affected_mfd_canister_ids,
                                    affected_mfd_analysis_details_ids, user_confirmation))

                if not pack_ids and user_confirmation:
                    pack_ids_with_no_transfer_mfd_canister = ",".join(map(str,
                                                                          pack_ids_with_no_transfer_mfd_canister.values()))
                    return error(21005, "{}".format(pack_ids_with_no_transfer_mfd_canister))

                # if user_confirmation is false and either packs shares mfd canister with other packs or mfd canisters
                # are filled then only information is returned else the action on packs and mfd canisters are taken
                if not user_confirmation and not forced_pack_manual and not status_changed_from_ips:
                    return create_response({'pack_ids': pack_ids,
                                            'mfd_packs': packs_having_mfd_canister,
                                            'affected_mfd_packs': extra_mfd_packs,
                                            'canisters_filled': canisters_filled,
                                            'restricted_packs': pack_ids_with_no_transfer_mfd_canister})
                else:
                    if extra_mfd_packs and not forced_pack_manual:
                        pack_ids = set(pack_ids)
                        pack_ids.update(extra_mfd_packs)
                        pack_ids = list(pack_ids)

                    pack_and_display_ids = db_get_pack_and_display_ids(pack_ids)

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
            # Here inside prepare_pack_reason_dict function, 2nd argument is pack display ID, but it is not in use here,
            # so we are passing pack_id only. In the future, if pack display ID is needed then modifications will be
            # required.
            else:
                pack_and_display_ids = db_get_pack_and_display_ids(pack_ids)
                reason_dict = {pack_id: prepare_pack_reason_dict(pack_id, pack_and_display_ids[pack_id],
                                                                 reason) for pack_id in pack_ids}

            logger.debug('affected packs: ' + str(pack_ids))
            if change_rx and delete_all_packs:
                affected_mfd_canister_ids, affected_mfd_analysis_details_ids = \
                    db_get_mfd_analysis_info_old_packs(pack_ids=pack_ids)

                affected_mfd_canister_ids = set(affected_mfd_canister_ids)
                affected_mfd_analysis_details_ids = set(affected_mfd_analysis_details_ids)
                logger.debug("affected_mfd_canister_ids: {}".format(affected_mfd_canister_ids))
                logger.debug("affected_mfd_analysis_details_ids: {}".format(affected_mfd_analysis_details_ids))

            if status != settings.FILLED_PARTIALLY_STATUS:
                # deleting partially filled data for the packs when status is changed from 51(FILLED_PARTIALLY_STATUS)
                # to any other
                partial_pack_ids = get_pack_id_for_given_status_from_given_packs(pack_ids=pack_ids)
                partial_pack_ids = [item['id'] for item in list(partial_pack_ids)]
                if partial_pack_ids:
                    update_status = delete_partially_filled_pack({'pack_ids': partial_pack_ids})
                logger.info('partially_filled_deleted_pack_ids ' + str(partial_pack_ids))
            if filled_at in [settings.FILLED_AT_PRI_PROCESSING, settings.FILLED_AT_POST_PROCESSING,
                             settings.FILLED_AT_PRI_BATCH_ALLOCATION,
                             settings.FILLED_AT_MANUAL_VERIFICATION_STATION] and \
                    status in [settings.MANUAL_PACK_STATUS, settings.PARTIALLY_FILLED_BY_ROBOT] and \
                    transfer_to_manual_fill_system:
                pack_user_map_list = list()
                order_no = get_order_no_for_given_company_id(company_id=company_id)
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

                update_pack_details_for_pack_ids(pack_ids=pack_ids, order_no_list=order_no_list)

                # When user selects the reason of Drugs out of Stock or Missing Pills from MVS, we need to process
                # the drugs appropriately based on the specified reason
                if reason_action == MVS_DRUGS_OUT_OF_STOCK:
                    missing_drug_mapping_dict = {"reason_action": reason_action,
                                                 "drug_list": drug_list,
                                                 "reason": reason
                                                 }

                if reason_action == MVS_MISSING_PILLS:
                    missing_drug_mapping_dict = {"reason_action": reason_action,
                                                 "reason_rx_no_list": reason_rx_no_list,
                                                 "reason": reason}

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
                    #check if filled from ips
                    ext_data = get_max_ext_data(pack_ids)
                    for record in ext_data:
                        if record["ext_status_id"] == constants.EXT_PACK_STATUS_CODE_DONE and \
                                record["pack_status"] == settings.DONE_PACK_STATUS:
                            return error(7003)

                    ips_comm_settings = get_ips_communication_settings_dao(company_id=company_id)
                    settings_present = all(key in ips_comm_settings for key in settings.IPS_COMMUNICATION_SETTINGS)
                    if settings_present:
                        ips_pack_ids = db_get_pack_display_ids(pack_ids)
                        pack_and_display_ids = db_get_pack_and_display_ids(pack_ids)
                        update_packs_filled_by_in_ips(pack_ids=ips_pack_ids, ips_username=ips_username,
                                                               pack_and_display_ids=pack_and_display_ids,
                                                               ips_comm_settings=ips_comm_settings, token=token)
                    else:
                        logger.error(
                            'In set_status, Required Settings not present to update filled by in Pharmacy Software.'
                            ' company_id: {}'.format(company_id))

                logger.info(
                    "In set_status, before_track_consumed_packs_called : pack ids: " + str(
                        pack_ids) + " status: " + str(status) +
                    " company_id " + str(company_id))

                track_consumed_packs(pack_ids, company_id)
                if status in settings.PACK_FILLING_DONE_STATUS_LIST or status == settings.FILLED_PARTIALLY_STATUS:
                    update_set_last_seen(pack_ids)

            pack_status_dict = {}
            pack_status_list = []

            for pack_id in pack_ids:
                pack_status_dict["pack_id"] = pack_id
                pack_status_dict["old_status"] = db_get_status_numeric(pack_id)
                pack_status_dict["new_status"] = status
                pack_status_list.append(pack_status_dict.copy())
                # when pack status changes to manual after progress in manual pack filling
                # then no need to update replenish_mini_batch document.
                if status == settings.MANUAL_PACK_STATUS \
                        and pack_status_dict.get("old_status", None) == settings.PROGRESS_PACK_STATUS \
                        and update_replenish_data:
                    update_replenish_data = False
            Notifications(call_from_client=call_from_client).add_pack_status_change_history(
                pack_status_list=pack_status_list, pack_status_change_from_ips=status_changed_from_ips)

            # a) Replaced "reason" string parameter with "packid_delete_reason" dictionary parameter where it maps
            # individual pack with its respective reason
            # b) This is done because we need to send back deleted reason to IPS, and it can have more than one reason
            # when packs have shared MFD
            # c) update_ips = True then send call for delete sync to IPS else False
            # This will be false when we have received delete call from IPS and we don't have any shared MFD situation
            # Checking pack status when called from pack queue and deleting or sending manual
            if user_confirmation and status in [settings.MANUAL_PACK_STATUS,
                                                settings.DELETED_PACK_STATUS] and module_id == constants.MODULE_PACK_QUEUE:
                status_list = db_get_packs_with_status(pack_ids, [settings.PROGRESS_PACK_STATUS])
                if status_list.get(settings.PROGRESS_PACK_STATUS, []):
                    return error(7006)

            response = set_status_pack_details(
                pack_ids, status, user_id,
                reason_dict=reason_dict,
                use_company_id=use_company_id,
                system_id=system_id,
                filled_at=filled_at,
                fill_time=fill_time,
                filled_by=ips_username,
                transfer_to_manual_fill_system=transfer_to_manual_fill_system,
                change_rx_token=change_rx_token
            )
            if json.loads(response)["status"] == settings.SUCCESS_RESPONSE and status in settings.DEQUEUE_PACK_STATUS:
                dequeue = remove_packs_from_queue(pack_ids)
                if dequeue:
                    pack_queue_count = get_pack_queue_count()
                    delete_reserved_canister_for_pack_queue(pack_ids)
                    res = update_batch_status_for_empty_pack_queue(pack_queue_count)
                    if res:
                        try:
                            update_replenish_based_on_system(system_id)

                            # bellow reset doc needed in case if all packs deleted from pack queue.
                            logger.info(f"In set_status, reset mfs-v1 and mfd-canister-pre-fill")
                            mfs_system_device = get_mfs_system_device_from_company_id(company_id=company_id,
                                                                                          system_id=system_id)

                            mfs_doc_status = reset_mfs_couch_db_documents_batch_revert(mfs_system_device)
                            logger.info(f"In set_status, mfs_doc_status: {mfs_doc_status}")
                        except (InternalError, IntegrityError) as e:
                            logger.error(e, exc_info=True)
                            return error(2001, e)
                        except ValueError as e:
                            return error(2005, str(e))
            logger.info("db_set_status response for pack_ids: {} is {}, for status, {} reason_dict {} and update_ips {}"
                        .format(pack_ids, json.loads(response), status, reason_dict, update_ips))

            if json.loads(response)["status"] == settings.SUCCESS_RESPONSE and status == settings.PROGRESS_PACK_STATUS and device_id:
                logger.info(f"In set_status, update replenish mini batch doc")
                batch_dict = {
                    "device_id": device_id,
                    "system_id": system_id
                }
                get_replenish_mini_batch_wise(batch_dict)

            # If the packs get deleted then we need to communicate the same back to IPS
            if json.loads(response)["status"] == settings.SUCCESS_RESPONSE and status == settings.DELETED_PACK_STATUS \
                    and company_id and reason_dict:

                for pack_id in reason_dict:
                    pack_display_ids.append(str(reason_dict[pack_id].get("pack_display_id")))
                    delete_reason_list.append(reason_dict[pack_id].get("reason"))

                if update_ips:
                    response_data = delete_pack_in_ips(pack_display_ids, ips_username, delete_reason_list, company_id,
                                                       change_rx)

                logger.info('After response pack_display_ids {}'.format(pack_display_ids))

            if json.loads(response)["status"] == settings.SUCCESS_RESPONSE and company_id and \
                    status in settings.FILLED_PACK_STATUS:
                db_update_rx_changed_packs_manual_count(company_id)

            # if packs having mfd canisters are being deleted or marked manual then rts is required for drugs
            if affected_mfd_analysis_details_ids:
                status = update_rts_data(list(set(affected_mfd_analysis_details_ids)),
                                         list(set(affected_mfd_canister_ids)), company_id=company_id,
                                         user_id=user_id,
                                         action_id=settings.PACK_ACTION_MAP[status],
                                         change_rx=change_rx, delete_all_packs=delete_all_packs)

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
                        if update_replenish_data:
                            update_replenish_based_on_system(system_id)
                    except (InternalError, IntegrityError) as e:
                        logger.error(e, exc_info=True)
                        return error(2001, e)
                    except ValueError as e:
                        return error(2005, str(e))

                if status == settings.DELETED_PACK_STATUS:
                    db_update_rx_changed_packs_manual_count(company_id)

            # If status of other packs changed successfully and there are some deleted packs
            # then send deleted packs in response
            formatted_response = json.loads(response)
            if formatted_response["status"] == settings.SUCCESS_RESPONSE:

                if pack_ids_with_no_transfer_mfd_canister:
                    pack_ids_with_no_transfer_mfd_canister = ",".join(map(str,
                                                                          pack_ids_with_no_transfer_mfd_canister.values()))
                    return error(21005, "{}".format(pack_ids_with_no_transfer_mfd_canister))
                else:
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


@log_args_and_response
def get_pending_packs_with_past_delivery_date(company_id: int, time_zone: str) -> str:
    """
    Sends the email for the pending packs with past delivery dates for the given company_id.
    """
    try:
        result_list = list()
        user_ids = set()
        pack_id = []
        current_date: str = get_current_day_date_end_date_by_timezone(time_zone=time_zone)[0]
        company_settings = get_company_setting_by_company_id(company_id=company_id)
        query1 = get_pending_pack_details_and_patient_name_with_past_delivery_date(company_id=company_id,
                                                                                   current_date=current_date)

        logger.info(f"In get_pending_packs_with_past_delivery_date, query1: {query1}")

        for auto_pack in query1:
            pack_id.append(auto_pack["pack_display_id"])
            result_dict = {"pack_id": auto_pack["pack_display_id"],
                           "admin_start_date": str(auto_pack["consumption_start_date"]),
                           "admin_end_date": str(auto_pack["consumption_end_date"]),
                           "delivery_date": str(auto_pack["scheduled_delivery_date"]),
                           "pack_type": "Robot",
                           "assigned_to": 0,
                           "patient_name": auto_pack["patient_name"],
                           "facility_name": auto_pack["facility_name"]}
            result_list.append(result_dict.copy())

        query2 = get_manual_pack_details_and_patient_name_with_past_delivery_date(company_id=company_id,
                                                                                  current_date=current_date)

        for manual_pack in query2:
            pack_id.append(manual_pack["pack_display_id"])
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

        ips_response = get_pack_status_from_ips(pack_id, company_settings)
        ips_response = {int(key): value for key, value in ips_response.items()}
        for packs in result_list:
            if packs["pack_id"] in ips_response.keys():
                packs["ips_status"] = ips_response[packs["pack_id"]]["status"]
            else:
                packs["ips_status"] = "N.A."

        logger.info(f"In get_pending_packs_with_past_delivery_date, result_list: {result_list}")

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


@log_args
def validate_robot_partially_filled_pack(dict_batch_info: dict) -> dict:
    """
     This function calculates the pack count for auto pilot
    """
    logger.debug("In validate_robot_partially_filled_pack")

    company_id = dict_batch_info["company_id"]
    pack_display_ids = dict_batch_info["pack_display_ids"]
    user_id = dict_batch_info["user_id"]
    valid_pack_ids = set()
    try:

        pack_info = get_packs_with_status_partially_filled_by_robot_for_given_pack_display_ids(user_id=user_id,
                                                                                               pack_display_ids=pack_display_ids,
                                                                                               company_id=company_id)

        logger.info(f"In validate_robot_partially_filled_pack, pack_info: {list(pack_info)}")

        for record in pack_info:
            valid_pack_ids.add(record['pack_display_id'])
        if len(valid_pack_ids) == len(pack_display_ids):
            return create_response(True)
        return create_response(False)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        return e


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
        query = get_pack_analysis_details_for_given_batch(batch_id=batch_id)

        logger.info(f"In get_pack_count_for_auto_pilot, query: {list(query)}")

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

        logger.info(
            f"In get_pack_count_for_auto_pilot; automatic_pack_list: {automatic_pack_list}, mfd_packs: {mfd_packs}")

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


@log_args_and_response
def get_pack_history_data(dict_pack_info):
    logger.debug("Inside get_pack_history_data")
    try:
        pack_id = int(dict_pack_info.get('pack_id'))

        pack_history_data = get_pack_history_by_pack_id(pack_id)

        logger.info(f"In get_pack_history_data, pack_history_data: {pack_history_data}")

        return create_response(pack_history_data)
    except Exception as e:
        logger.error(f"Error in get_pack_history_data: {e}")
        raise e


@log_args_and_response
def get_new_packs_change_rx(template_id, company_id, assigned_to):
    try:
        response = get_pending_packs_by_template_and_user(template_id=template_id, company_id=company_id,
                                                          assigned_to=assigned_to)
        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.info(e)
        return error(1000, e)


@log_args_and_response
def get_manual_packs(company_id, filter_fields, paginate, sort_fields):
    try:
        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        response = dict()
        like_search_list = ['facility_name', 'patient_name', 'patient_dob']
        exact_search_list = ['delivery_date_exact', 'print_requested', 'patient_id', 'change_rx_flag']
        between_search_list = ['admin_start_date', 'delivery_date', 'created_date']
        membership_search_list = ['pack_status', 'assigned_to', 'uploaded_by', 'pack_id']
        left_like_search_fields = ['pack_display_id']
        having_search_list = []

        try:

            query, fields_dict, filter_fields, clauses, order_list, defined_orders = get_manual_pack_dao(company_id=company_id, filter_fields=filter_fields, sort_fields=sort_fields)

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
@validate(required_fields=[ "company_id"])
def get_similar_manual_packs(dict_patient_info):
    date_from = dict_patient_info.get('date_from')
    date_to = dict_patient_info.get('date_to')
    company_id = dict_patient_info.get('company_id')
    patient_id = dict_patient_info.get('patient_id', None)
    patient_id = json.loads(patient_id) if patient_id else None
    date_type = dict_patient_info.get('date_type')
    user_id = dict_patient_info.get('user_id')
    assigned_user_id = dict_patient_info.get('assigned_user_id')
    assigned_user_id = dict_patient_info.get('assigned_user_id')
    pack_master = dict_patient_info.get('pack_master')
    pack_header_id = dict_patient_info.get('pack_header_id')
    if pack_header_id:
        pack_header_id = [json.loads(pack_header_id)] if pack_header_id and type(
            json.loads(pack_header_id)) != list else json.loads(pack_header_id)
    #
    # if pack_master:
    #     pack_data_dict = get_patient_packs(patient_id, company_id, pack_header_id)
    #
    pack_data_dict = get_patient_manual_packs(patient_id, company_id, date_from, date_to, date_type,
                                              user_id, assigned_user_id , pack_header_id, pack_master)

    logger.info("In get_similar_manual_packs, pack_data_dict: {}".format(pack_data_dict))

    return create_response(pack_data_dict)


@log_args_and_response
@validate(required_fields=['pack_list', 'user_list', 'company_id', 'user_id'])
def transfer_manual_packs(manual_packs_dict):
    """
    changes batch_id for pending packs, deletes related data and marks batch as processing done
    :param batch_dict: format: {"batch_id":703, "system_id": 2}
    :return:
    """
    logger.debug("Inside transfer_manual_packs")
    try:
        pack_list = manual_packs_dict['pack_list']
        user_list = manual_packs_dict['user_list']
        company_id = manual_packs_dict['company_id']
        user_id = manual_packs_dict['user_id']

        manual_pack_by_user = manual_user_distribution_flow_handler(user_list, pack_list, company_id)

        logger.info("In transfer_manual_packs, manual_pack_by_user: {}".format(manual_pack_by_user))

        return create_response(manual_pack_by_user)


    except (IntegrityError, InternalError) as e:

        logger.error(e, exc_info=True)

        return error(2001)


@log_args_and_response
def get_pack_drugs(dict_pack_info):
    """
    Returns drug data and patient data for given packs or batch
    :param dict_pack_info:
    :return:
    """
    logger.debug("Inside get_pack_drugs")
    pack_list = list()
    batch_id = dict_pack_info.get('batch_id', None)
    pack_list = []
    txr_list = []
    con_fndc_txr_list = []
    inventory_data = dict()
    if batch_id:
        company_id = dict_pack_info.get('company_id', None)
        pack_list = get_batch_packs(company_id, batch_id, status=[settings.PENDING_PACK_STATUS])

        logger.info(f"In get_pack_drugs, pack_list: {pack_list}")

    pack_id_list = dict_pack_info.get("pack_id_list", None)

    if pack_id_list:
        pack_list = list({int(item) for item in str(pack_id_list).split(',')})
        logger.info(f"In get_pack_drugs, pack_list from pack_id_list: {pack_list}")

    drug_data = dict()
    try:
        # fetch unique drug list for non-manual packs
        canister_fndc_txr_list = get_drug_data_for_unique_fndc_txr_for_non_manual_packs(pack_list)

        logger.info("In get_pack_drugs, canister_fndc_txr_list: " + str(canister_fndc_txr_list))

        patient_list = get_patient_data_for_packs(pack_list)

        logger.info("In get_pack_drugs, patient_list: " + str(patient_list))

        drugs_in_packs = db_get_slot_wise_drug_data_for_packs(pack_list)

        logger.info(f"In get_pack_drugs, drugs_in_packs: {drugs_in_packs}")

        for record in drugs_in_packs:
            txr_list.append(record['txr'])
            con_fndc_txr_list.append(record['con_fndc_txr'])
            # check if pack is from robot to manual or not
            fndc_txr = ','.join([record["formatted_ndc"], record['txr'] if record['txr'] else ''])
            if fndc_txr in canister_fndc_txr_list and (record["dropped_qty"] is None or
                                                       record["dropped_qty"] < record["quantity"]):
                record["is_robot_to_manual"] = True
            else:
                record["is_robot_to_manual"] = False

            if record["dropped_qty"] is None or record["dropped_qty"] < record["quantity"]:
                record["is_manual"] = True
            else:
                record["is_manual"] = False

            if fndc_txr not in drug_data:
                record["daw_list"] = {}
                record["daw_list"][record["daw_code"]] = record["quantity"]

                # del record["daw_code"] # remove this key from record
                record["dawmax"] = max(record["daw_list"])
                drug_data[fndc_txr] = record
            else:
                # updating daw wise quantity
                previous_drug_data = drug_data[fndc_txr]
                previous_drug_data["daw_list"][record["daw_code"]] = record["quantity"]
                # updating total quantity
                previous_drug_data["quantity"] += record["quantity"]
                previous_drug_data["dawmax"] = max(previous_drug_data["daw_list"])
                drug_data[fndc_txr] = previous_drug_data

        logger.info("In get_pack_drugs, checking alternate drug available or not for drugs: " + str(drug_data))
        if txr_list and settings.USE_EPBM:
            inventory_data = get_fndc_txr_wise_inventory_qty(txr_list)

        alternate_drug_flag = add_variable_alternate_drug_available_in_drug_data(con_fndc_txr_list)
        for record in drug_data.values():
            if record['daw_code'] == 0:
                record['alternate_drug_available'] = alternate_drug_flag.get(record['con_fndc_txr'])
            else:
                record['alternate_drug_available'] = False

            record['inventory_qty'] = inventory_data.get((record['formatted_ndc'], record['txr']), None)
            if record['inventory_qty']:
                record['is_in_stock'] = 0 if record['inventory_qty'] <= 0 else 1
            else:
                record['is_in_stock'] = None
        logger.info("In get_pack_drugs, added value for alternate_drug_available key")

        response = {'patient_data': patient_list,
                    'drug_data': list(drug_data.values())}

        return create_response(response)
    except DoesNotExist:
        # current canister invalid or not generic drug, so return empty list
        return create_response(list(drug_data.values()))
    except Exception as e:
        logger.error(f"Error in get_pack_drugs: {e}")
        raise e


@log_args_and_response
def unassign_packs(user_data):

    logger.debug("Inside unassign_packs")

    user_list = [int(item) for item in str(user_data['users']).split(',')]

    logger.info(f"In unassign_packs, user_list: {user_list}")

    update_packs = 0
    try:
        status = update_packs_in_pack_user_map(user_list=user_list)
        return create_response(status)
    except Exception as e:
        logger.error(f"Error in unassign_packs: {e}")


@validate(required_fields=["pack_id"])
@log_args_and_response
def get_similar_packs_manual_assign(pack_info):
    """
    Gets pack ids which has all drug similar to given pack id and same pack header id and in
    manual packaging pending state(returns same pack in list)

    :param pack_info:
    :return: json
    """
    pack_id = pack_info["pack_id"]
    date_from = pack_info["date_from"]
    date_to = pack_info["date_to"]
    date_type = pack_info["date_type"]
    batch_distribution = pack_info["batch_distribution"]
    response = list()
    try:

        similar_pack_ids = get_similar_packs_manual_assign_dao(pack_id=pack_id,
                                                               date_type=date_type,
                                                               date_from=date_from,
                                                               date_to=date_to,
                                                               batch_distribution=batch_distribution)

        logger.info(f"In get_similar_packs_manual_assign, similar_pack_ids: {similar_pack_ids}")

        if similar_pack_ids:

            response = list(similar_pack_ids.values())

        return create_response(response)

    except(InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in get_similar_packs_manual_assign:{e}")
        raise e


@log_args_and_response
def create_overloadedpack_data(dict_info):
    """
    Converts hours and minutes in Float and store data in database
    :return: response status i.e row created or updated
    """
    response = str
    try:
        if "automatic" in dict_info:
            for data in dict_info["automatic"]:
                extra_hours = data["extra_hours"]
                minutes = data["minutes"] / 60
                extra_hours = ("%.2f" % (float(extra_hours) + float(minutes)))
                data_dict = {'system_id': data["system_id"], 'date': data["date"]}
                update_dict = {'extra_time': extra_hours, 'created_by': data["user_id"],
                               'modified_by': data["user_id"]}

                logger.info(f"In create_overloadedpack_data, data_dict: {data_dict}, update_dict: {update_dict}")

                response = overload_pack_timing_update_or_create_record(data_dict=data_dict, update_dict=update_dict)

        # commenting below code as we are not saving manual hours now.
        # if "manual" in dict_info:
        #     for data in dict_info["manual"]:
        #         extra_hours = data["extra_hours"]
        #         minutes = data["minutes"] / 60
        #         extra_hours = ("%.2f" % (float(extra_hours) + float(minutes)))
        #         data_dict = {'date': data["date"]}
        #         update_dict = {'user_id': data["user_id"], 'extra_time': extra_hours, 'created_by': data["user_id"],
        #                        'modified_by': data["user_id"], 'is_manual': 1, 'system_id': None}
        #         print("data dict", data_dict)
        #         response = OverLoadedPackTiming.db_update_or_create_record(data_dict, update_dict)

    except DoesNotExist:
        response = {}
    except (IntegrityError, InternalError):
        return error(2001)

    return create_response(response).encode('utf8')


@log_args_and_response
@validate(required_fields=["pack_id_list", "fill_time_list"])
def set_fill_time(pack_info):
    pack_ids = pack_info['pack_id_list']
    fill_time = pack_info['fill_time_list']
    try:
        update_count= set_fill_time_dao(fill_time=fill_time, pack_ids=pack_ids)

        return create_response({'upadated_packs': update_count})

    except Exception as e:
        logger.error(f"Error in set_fill_time: {e}")
        return e


def partially_filled_pack(userpacks):

    try:
        status = partially_filled_pack_dao(userpacks=userpacks)

        return create_response(status)
    except Exception as e:
        logger.error(f"Error in partially_filled_pack: {e}")


def max_order(system_id):
    """ gives the maximum order number for the facility.

        Args:

        Returns:
           json: success or failure

        Examples:
            >>> set_order({})
    """
    try:

        response = max_order_no(system_id)
        return create_response(response)

    except Exception as e:
        logger.error(f"Error in max_order: {e}")


@validate(required_fields=["pack_data", "user_id", "pack_qty", "company_id", "admin_start_date", "admin_end_date"])
def generate_test_packs(data):
    """
    Creates test packs for the given data

    Returns: pack_ids of the test packs

    """
    company_id = data['company_id']
    # system_id = int(data["system_id"])
    test_pack_data = data["pack_data"]
    user_id = data["user_id"]
    pack_quantity = data["pack_qty"]
    date_count = data.get("date_count", 7)
    admin_start_date = data.get("admin_start_date")
    admin_end_date = data.get("admin_end_date")
    logger.info("Starting Test Pack Generation. company_id: {} and pack quantity: {}".format(company_id, pack_quantity))
    all_dates = get_all_dates_between_two_dates(admin_start_date, admin_end_date)
    times = ["08:00", "13:00", "18:00", "22:00"]
    date_count = len(all_dates)
    child_packs_count = int(math.ceil(len(all_dates) / settings.ONE_WEEK))

    try:
        pack_id_list = generate_test_packs_dao(pack_quantity=pack_quantity,
                                               child_packs_count=child_packs_count,
                                               all_dates=all_dates,
                                               date_count=date_count,
                                               user_id=user_id,
                                               company_id=company_id,
                                               test_pack_data=test_pack_data,
                                               times=times)

        logger.info(f"In generate_test_packs, pack_id_list: {pack_id_list}")

        return create_response(pack_id_list)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in generate_test_packs: {e}")


@log_args_and_response
@validate(required_fields=["date_from", "date_to", "system_id"])
def get_all_unassociated_packs(dict_date_info):
    """
        Takes all the packs which do not have rfid associated with them.

        Args:
            dict_date_info (dict): from_date, to_date, system_id

        Returns:
           json response in success or failure

        Examples:
            >>> get_all_unassociated_packs({})
                []
    """
    logger.debug("Inside get_all_unassociated_packs")

    from_date, to_date = convert_date_to_sql_date(dict_date_info["date_from"], dict_date_info["date_to"])

    try:
        response = db_get_unassociated_packs(from_date, to_date, dict_date_info["system_id"])

        logger.info(f"In get_all_unassociated_packs, response: {response}")

    except IntegrityError:
        return error(2001)
    except InternalError:
        return error(2001)

    return create_response(response)


@log_args_and_response
def map_user_pack(userpacks):
    user_id = None
    call_from_client = None
    missing_drug_list_dict: Dict[str, Any] = dict()
    status_update: int = 0

    try:

        status = map_user_pack_dao(userpacks=userpacks)

        return status
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@validate(required_fields=["company_id"])
def get_pack_user_map(dict_pack_info):
    logger.info("get user map pack {}".format(dict_pack_info))

    try:
        company_id = dict_pack_info["company_id"]
        filter_fields = dict_pack_info.get('filter_fields', None)
        sort_fields = dict_pack_info.get('sort_fields', None)
        paginate = dict_pack_info.get('paginate', None)
        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        pack_data, count = get_pack_user_map_dao(company_id=company_id,
                                                 filter_fields=filter_fields,
                                                 sort_fields=sort_fields,
                                                 paginate=paginate)

        return {"pack_data": pack_data, "number_of_records": count}
    except Exception as e:
        logger.error(f"Error in get_pack_user_map: {e}")
        raise e


@validate(required_fields=['company_id', 'date_from', 'date_to'])
def get_user_pack_stats(dict_pack_user):

    logger.debug("Inside get_user_pack_stats")
    try:

        company_id = dict_pack_user['company_id']
        date_from = dict_pack_user['date_from']
        date_to = dict_pack_user['date_to']

        filled_pack_status = [5, 45]

        query = get_user_pack_stats_dao(company_id=company_id,
                                        date_from=date_from,
                                        date_to=date_to)

        logger.error(f"In get_user_pack_stats, query: {query}")

        assigned_packs = 0
        partially_filled_packs = 0
        filled_packs = 0
        rejected_packs = 0
        total_packs = query.count()
        for record in query:
            if record['pack_status'] in filled_pack_status:
                filled_packs += 1
            if record['pack_status'] == settings.FILLED_PARTIALLY_STATUS:
                partially_filled_packs += 1
            if record['assigned_to_user']:
                assigned_packs += 1

        response = {
            'total_packs': total_packs,
            'assigned_packs': assigned_packs,
            'partially_filled_packs': partially_filled_packs,
            'filled_packs': filled_packs,
            'rejected_packs': rejected_packs
        }
        return create_response(response)
    except Exception as e:
        logger.error(f"Error in get_user_pack_stats: {e}")
        raise e


@log_args_and_response
@validate(required_fields=["date_type", "date_from", "date_to", "company_id"])
def get_manual_count_stats(dict_patient_info):
    date_from = dict_patient_info.get('date_from')
    date_to = dict_patient_info.get('date_to')
    company_id = dict_patient_info.get('company_id')
    user_stats = dict_patient_info.get('user_stats', False)
    date_type = dict_patient_info.get('date_type')
    assigned_to = int(dict_patient_info['assigned_to'])
    pack_status_list = dict_patient_info.get('status', None)
    try:
        status_pack_count_dict, value_status_id_dict, total_packs, assigned_user_pack_count = get_manual_packs_data(
            company_id, date_from, date_to, date_type, assigned_to, user_stats, pack_status_list)

        logger.info(
            f"In get_manual_count_stats; status_pack_count_dict: {status_pack_count_dict}, value_status_id_dict: {value_status_id_dict}")

        response_data = {"pack_stats": [], "total_packs": total_packs,
                         "assigned_user_pack_count": assigned_user_pack_count}
        data_dict = {}
        for status, pack_count in status_pack_count_dict.items():
            data_dict['value'] = status
            data_dict['pack_status'] = value_status_id_dict[status]
            data_dict['pack_count'] = pack_count
            response_data['pack_stats'].append(deepcopy(data_dict))

        logger.info(f"In get_manual_count_stats, response_data: {response_data}")

        return create_response(response_data)
    except Exception as e:
        logger.error(e)
        return error(0, e)


@log_args_and_response
def get_slot_details_for_vision_system(dict_pack_info):
    try:
        pack_id = dict_pack_info["pack_id"]
        system_id = int(dict_pack_info["system_id"])
        device_id = int(dict_pack_info["device_id"])
        valid_pack = verify_pack_id_by_system_id_dao(pack_id=pack_id, system_id=system_id)
        if not valid_pack:
            return error(1014)
        slot_details = slot_details_for_vision_system_dao(pack_id, device_id, system_id)

        logger.info(f"In get_slot_details_for_vision_system, slot_details: {slot_details}")

        return create_response(slot_details)
    except Exception as e:
        logger.error(f"Error in get_slot_details_for_vision_system: {e}")
        return e


@log_args_and_response
@validate(required_fields=["pack_id", "system_id"])
def get_slots_for_user_station(dict_pack_info):
    pack_id = dict_pack_info["pack_id"]
    system_id = dict_pack_info["system_id"]

    valid_pack = verify_pack_id_by_system_id_dao(pack_id=pack_id, system_id=system_id)
    if not valid_pack:
        return error(1014)

    try:
        slot_details = defaultdict(dict)
        incorrect_drug_list = {}

        slot_data = db_slots_for_user_station(pack_id)

        logger.info(f"In get_slots_for_user_station, slot_data: {slot_data}")

        vision_slot_data = db_vision_slots_for_user_station(pack_id)

        logger.info(f"In get_slots_for_user_station, vision_slot_data: {vision_slot_data}")

        if slot_data is not None:
            for record in slot_data:
                record["required_qty"] = float(record["required_qty"])
                record["robot_qty"] = float(record["robot_qty"])
                record["vision_qty"] = None
                slot_row, slot_column = record["slot_row"], record["slot_column"]
                location = map_pack_location_dao(slot_row=slot_row, slot_column=slot_column)
                slot_details[location]['hoa_date'] = record["hoa_date"]
                slot_details[location]['hoa_time'] = record["hoa_time"]
                slot_details[location]['slot_row'] = record["slot_row"]
                slot_details[location]['slot_column'] = record["slot_column"]
                slot_details[location].setdefault("drug_details", {})[record["drug_id"]] = record

        if vision_slot_data is not None:
            for record in vision_slot_data:
                record["predicted_qty"] = float(record["predicted_qty"])
                slot_row, slot_column = record["slot_row"], record["slot_column"]
                location = map_pack_location_dao(slot_row=slot_row, slot_column=slot_column)
                if record["predicted_drug_id"] is None:  # for unknown drug todo use record['is_unknown']
                    slot_details[location]["drug_details"][record["predicted_drug_id"]] = {}
                    slot_details[location]["drug_details"][record["predicted_drug_id"]]["drug_name"] = "Unknown Drug"
                    slot_details[location]["drug_details"][record["predicted_drug_id"]]["ndc"] = "unknown"
                    slot_details[location]["drug_details"][record["predicted_drug_id"]]["robot_qty"] = 0
                    slot_details[location]["drug_details"][record["predicted_drug_id"]]["required_qty"] = 0

                slot_details[location]["drug_details"][record["predicted_drug_id"]]["vision_qty"] = record[
                    "predicted_qty"]

        drug_qty = dict()
        for location in slot_details:
            drug_list = slot_details[location]["drug_details"]
            for drug in drug_list:
                incorrect_flag = False
                robot_qty = drug_list[drug]["robot_qty"]
                required_qty = drug_list[drug]["required_qty"]
                # count all required and robot dropped quantity
                if drug not in drug_qty:
                    drug_qty[drug] = {}
                    drug_qty[drug]["robot_qty"] = robot_qty
                    drug_qty[drug]["required_qty"] = required_qty
                    drug_qty[drug]["vision_qty"] = None
                else:
                    drug_qty[drug]["robot_qty"] += robot_qty
                    drug_qty[drug]["required_qty"] += required_qty

                if drug is None or robot_qty != required_qty:
                    incorrect_flag = True

                if "vision_qty" in drug_list[drug] and drug_list[drug]["vision_qty"] is not None:
                    if required_qty != drug_list[drug]["vision_qty"]:
                        incorrect_flag = True
                    if drug_qty[drug]["vision_qty"] is None:
                        drug_qty[drug]["vision_qty"] = drug_list[drug]["vision_qty"]
                    else:
                        drug_qty[drug]["vision_qty"] += drug_list[drug]["vision_qty"]
                if incorrect_flag:
                    drug_list[drug]["is_error"] = True
                    if drug not in incorrect_drug_list:
                        incorrect_drug_list[drug] = copy.deepcopy(drug_list[drug])
                else:
                    drug_list[drug]["is_error"] = False
    except KeyError as ex:
        print(ex)  # todo remove
        logger.error(ex)
    except Exception as e:
        logger.error(e)
        return error(0, e)

    for item in slot_details:  # convert to apt. output format
        temp = slot_details[item]["drug_details"]
        temp = list(temp.values())
        slot_details[item]["drug_details"] = temp

    for item in incorrect_drug_list:  # providing total quantity
        incorrect_drug_list[item]["robot_qty"] = drug_qty[item]["robot_qty"]
        incorrect_drug_list[item]["required_qty"] = drug_qty[item]["required_qty"]
        incorrect_drug_list[item]["vision_qty"] = drug_qty[item]["vision_qty"]

    incorrect_drug_list = list(incorrect_drug_list.values())

    logger.info(f"In get_slots_for_user_station, incorrect_drug_list: {incorrect_drug_list}")

    response = {"slot_data": slot_details, "incorrect_drug_list": incorrect_drug_list}

    return create_response(response)


def op_null_equal(lhs, rhs):
    return Expression(lhs, '<=>', rhs)


@log_args_and_response
def get_drugs_of_reuse_pack(pack_display_id, company_id, similar_pack_ids, is_change_rx_pack):
    try:
        logger.info("In get_drugs_of_reuse_pack")
        # code for validation.
        validation = False
        status = None
        response = []

        if is_change_rx_pack:
            validate_pack = check_for_reuse_pack(pack_display_id, company_id)
            for data in validate_pack:
                validation = True
        else:
            validation = True

        if not validation:
            return error(1043)

        if validation:
            response = get_drugs_of_reuse_pack_dao(pack_display_id, company_id, similar_pack_ids)
        return response

    except Exception as e:
        logger.error(f"Error in get_drugs_of_reuse_pack, e: {e}")
        raise(e)


@log_args_and_response
@validate(required_fields=["pack_id", "system_id"], validate_pack_id='pack_id')
def get_slots_for_label_printing(dict_pack_info, **kwargs):
    """ Take the pack id, system_id and returns the slots associated with the given pack id.

        Args:
            dict_pack_info (dict): The keys in it are pack_id(int), system_id(int)

        Returns:
           json: All the slots and the information associated with it.

        Examples:
            >>> get_slots_for_label_printing({"pack_id":1, "system_id": 2})
    """
    logger.debug("In get_slots_for_label_printing")
    pack_id = dict_pack_info["pack_id"]
    system_id = dict_pack_info["system_id"]
    pvs_data_required = dict_pack_info.get("pvs_data_required", False)
    user_id = dict_pack_info.get("user_id", None)
    call_from_mvs = dict_pack_info.get("call_from_mvs", False)
    max_pack_consumption_end_date = dict_pack_info.get("max_pack_consumption_end_date", None)
    cyclic_flag = dict_pack_info.get("cyclic_flag", True)
    module_id = dict_pack_info.get("module_id", None)
    if module_id:
        module_id = int(module_id)
    pvs_data = dict()
    drug_data = {}
    dict_slot_info = defaultdict(dict)
    txr_list = []
    hoa_day = set()
    date_day_dict = {}
    ndc_list = []
    inventory_data = {}

    # INFO: commenting to allow cross system printing
    # valid_pack = PackDetails.db_verify_pack_id_by_system_id(pack_id, system_id)
    # if not valid_pack:
    #     return error(1014)
    try:
        change_rx_flag = db_check_change_rx_flag_for_pack(pack_id=pack_id)
        hold_rx_dict = db_check_rx_on_hold_for_pack(pack_id=pack_id)
        expiry_soon_fndc_txr = db_fetch_nearest_exp_date_drug(pack_id=pack_id,
                                                              max_pack_consumption_end_date=max_pack_consumption_end_date)
        expiry_soon_drugs = db_get_expiry_soon_drug(pack_id=pack_id,
                                                    max_pack_consumption_end_date=max_pack_consumption_end_date)

        mfd_canister_fndc_txr_set, is_mfd_pack = get_mfd_canister_drugs(pack_id=pack_id)

        logger.info(
            "get_slots_for_label_printing mfd_can_fndc_txr_set, is_mfd_pack {}, {}".format(mfd_canister_fndc_txr_set,
                                                                                           is_mfd_pack))

        slot_data, txr_list = db_slot_details_for_label_printing(pack_id,system_id,get_robot_to_manual=True,
                                                        mfd_canister_fndc_txr_dict=mfd_canister_fndc_txr_set)
        if txr_list and settings.USE_EPBM:
            inventory_data = get_fndc_txr_wise_inventory_qty(txr_list)
        if not slot_data:
            return error(1004)
        if pvs_data_required:
            pvs_data = get_pvs_data(pack_id)  # get pvs data for slots

        for date in slot_data:
            hoa_day.update({date["hoa_date"]})

        sorted_dates = sorted(hoa_day)

        for i in range(len(sorted_dates)):
            date_day_dict[sorted_dates[i]] = i + 1

        # pvs_data = get_pvs_data(pack_id)
        for item in slot_data:
            item["expire_soon"] = True if (item["formatted_ndc"], item["txr"]) in expiry_soon_fndc_txr else False
            item["short_drug_name_v1"] = fn_shorten_drugname(item["drug_name"])
            item["short_drug_name_v2"] = fn_shorten_drugname_v2(item["display_drug_name"], item["strength"],
                                                                item["strength_value"], **kwargs)
            slot_row, slot_column = item["slot_row"], item["slot_column"]
            item["quantity"] = float(item["quantity"])
            location = map_pack_location_dao(slot_row=slot_row, slot_column=slot_column)

            if expiry_soon_drugs and location in expiry_soon_drugs:
                item["expire_soon_drug"] = expiry_soon_drugs[location][item["drug_id"]]["expire_soon_drug"] if item["drug_id"] in expiry_soon_drugs[location] else None
                item["expiry_date"] = expiry_soon_drugs[location][item["drug_id"]]["expiry_date"] if item["drug_id"] in expiry_soon_drugs[location] else None

            dict_slot_info[location]['hoa_date'] = item.get("hoa_date")
            dict_slot_info[location]['hoa_time'] = item.get("hoa_time")
            dict_slot_info[location]['hoa_day'] = item["hoa_date"].strftime('%A') if item["hoa_date"] else None
            dict_slot_info[location]['is_fod'] = item.get('is_fod', False)
            dict_slot_info[location]['day_no'] = date_day_dict[item["hoa_date"]] if item["hoa_date"] else None
            item['inventory_qty'] = inventory_data.get((item['formatted_ndc'], item['txr']), None)
            if item['inventory_qty']:
                item['is_in_stock'] = 0 if item["inventory_qty"] <= 0 else 1
            else:
                item['is_in_stock'] = None
            dict_slot_info[location]['is_in_stock'] = item["is_in_stock"]
            dict_slot_info[location]['slot_row'] = item["slot_row"]
            dict_slot_info[location]['slot_column'] = item["slot_column"]
            dict_slot_info[location]['slot_header_id'] = item["slot_header_id"]
            dict_slot_info[location].setdefault('txr_list', [])
            dict_slot_info[location].setdefault('quantity', 0)
            dict_slot_info[location].setdefault('dropped_qty', 0)
            dict_slot_info[location].setdefault('mfd_skipped_qty', 0)

            dict_slot_info[location].setdefault('modified_quantity', 0)
            dict_slot_info[location].setdefault('modified_dropped_qty', 0)
            # dict_slot_info[location].setdefault('modified_mfd_dropped_quantity', 0)
            dict_slot_info[location].setdefault('modified_mfd_skipped_qty', 0)
            dict_slot_info[location].setdefault('drug_tracker_dropped_qty', 0)
            dict_slot_info[location].setdefault('modified_drug_tracker_dropped_qty', 0)
            if item["txr"] not in dict_slot_info[location]['txr_list']:
                dict_slot_info[location]['txr_list'].append(item["txr"])
                dict_slot_info[location]['quantity'] += item['quantity']
                dict_slot_info[location]['modified_quantity'] += math.ceil(item['quantity'])
            if item["dropped_qty"]:
                item["dropped_qty"] = float(item["dropped_qty"])
                item["modified_dropped_qty"] = math.ceil(float(item["dropped_qty"]))
                dict_slot_info[location]['dropped_qty'] += item['dropped_qty']
                dict_slot_info[location]['modified_dropped_qty'] += item['modified_dropped_qty']
            if item["drug_tracker_dropped_qty"]:
                item["drug_tracker_dropped_qty"] = float(item["drug_tracker_dropped_qty"])
                item["modified_drug_tracker_dropped_qty"] = math.ceil(float(item["drug_tracker_dropped_qty"]))
                dict_slot_info[location]['drug_tracker_dropped_qty'] += item['drug_tracker_dropped_qty']
                dict_slot_info[location]['modified_drug_tracker_dropped_qty'] += item['modified_drug_tracker_dropped_qty']
            if item["mfd_dropped_quantity"]:
                item["mfd_dropped_quantity"] = float(item["mfd_dropped_quantity"])
                item["modified_mfd_dropped_quantity"] = math.ceil(float(item["mfd_dropped_quantity"]))
                dict_slot_info[location]['dropped_qty'] += item['mfd_dropped_quantity']
                dict_slot_info[location]['modified_dropped_qty'] += item['modified_mfd_dropped_quantity']
                dict_slot_info[location]['drug_tracker_dropped_qty'] += item['mfd_dropped_quantity']
                dict_slot_info[location]['modified_drug_tracker_dropped_qty'] += item['modified_mfd_dropped_quantity']

            if item["mfd_manual_filled_quantity"]:
                item["mfd_manual_filled_quantity"] = float(item["mfd_manual_filled_quantity"])
                item["modified_mfd_manual_filled_quantity"] = math.ceil(float(item["mfd_manual_filled_quantity"]))
                dict_slot_info[location]["dropped_qty"] += item["mfd_manual_filled_quantity"]
                dict_slot_info[location]["modified_dropped_qty"] += item["modified_mfd_manual_filled_quantity"]
                dict_slot_info[location]["drug_tracker_dropped_qty"] += item["mfd_manual_filled_quantity"]
                dict_slot_info[location]["modified_drug_tracker_dropped_qty"] += item["modified_mfd_manual_filled_quantity"]

            if item["is_mfd_drug"]:
                args = {"drug_id": item["drug_id"], "pack_id": pack_id, "is_mfd_drug": True, "txr": item["txr"]}
            else:
                args = {"drug_id": item["drug_id"], "pack_id": pack_id, "is_mfd_drug": False, "txr": item["txr"]}

            slot_data = get_slot_is_filled(args)

            if slot_data:
                for slot_number, slot_data in slot_data.items():
                    if slot_number == location:
                        item["is_filled"] = slot_data["is_filled"]

            dict_slot_info[location].setdefault("drug_details", []).append(create_slot(item))

            if item["mfd_skipped_quantity"]:
                dict_slot_info[location]['mfd_skipped_qty'] += item['mfd_skipped_quantity']
                dict_slot_info[location]['modified_mfd_skipped_qty'] += math.ceil(item['mfd_skipped_quantity'])

            if pvs_data:
                if location in pvs_data:
                    dict_slot_info[location]["pvs_data"] = pvs_data[location]
                    # dict_slot_info[location]["pvs_dropped_qty"] = pvs_data[location]['pvs_identified_count']

                else:  # pvs data not available
                    dict_slot_info[location]["pvs_data"] = {}
            else:
                dict_slot_info[location]["pvs_data"] = {}

            if item["drug_id"] not in drug_data:
                logger.info("get_slots_for_label_printing item data {}".format(item["drug_id"]))

                drug_data[item["drug_id"]] = {"drug_id": item["drug_id"]}
                drug_data[item["drug_id"]]["is_removable"] = item["is_removable"]
                drug_data[item["drug_id"]]["original_drug_id"] = item["original_drug_id"]
                drug_data[item["drug_id"]]["original_drug_ndc"] = item["original_drug_ndc"]
                # drug_data[item["drug_id"]]["is_in_stock"] = item["is_in_stock"]
                item['inventory_qty'] = inventory_data.get((item['formatted_ndc'], item['txr']), None)
                if item['inventory_qty']:
                    item['is_in_stock'] = 0 if item["inventory_qty"] <= 0 else 1
                else:
                    item['is_in_stock'] = None
                drug_data[item["drug_id"]]["is_in_stock"] = item["is_in_stock"]
                drug_data[item["drug_id"]]["case_id"] = item["case_id"]
                drug_data[item["drug_id"]]["last_seen_on"] = item["last_seen_on"]
                drug_data[item["drug_id"]]["last_seen_by"] = item["last_seen_by"]
                drug_data[item["drug_id"]]["ndc"] = item["ndc"]
                drug_data[item["drug_id"]]["rx_no"] = item["pharmacy_rx_no"]
                drug_data[item["drug_id"]]["drug_name"] = item["drug_name"]
                drug_data[item["drug_id"]]["strength_value"] = item["strength_value"]
                drug_data[item["drug_id"]]["strength"] = item["strength"]
                drug_data[item["drug_id"]]["drug_full_name"] = item["drug_full_name"]
                drug_data[item["drug_id"]]["sig"] = item["sig"]
                drug_data[item["drug_id"]]["quantity"] = item["quantity"]
                drug_data[item["drug_id"]]["manufacturer"] = item["manufacturer"]
                drug_data[item["drug_id"]]["image_name"] = item["image_name"]
                drug_data[item["drug_id"]]["imprint"] = item["imprint"]
                drug_data[item["drug_id"]]["color"] = item["color"]
                drug_data[item["drug_id"]]["shape"] = item["shape"]
                drug_data[item["drug_id"]]["pack_rx_id"] = item["pack_rx_id"]
                drug_data[item["drug_id"]]["device_id"] = item["device_id"]
                drug_data[item["drug_id"]]["device_name"] = item["device_name"]
                drug_data[item["drug_id"]]["location_number"] = item["location_number"]
                drug_data[item["drug_id"]]["display_location"] = item["display_location"]
                drug_data[item["drug_id"]]["dropped_qty"] = 0 if item["dropped_qty"] is None else item["dropped_qty"]
                drug_data[item["drug_id"]]["drug_tracker_dropped_qty"] = 0 if item["drug_tracker_dropped_qty"] is None else item["drug_tracker_dropped_qty"]
                drug_data[item["drug_id"]]["is_manual"] = False
                drug_data[item["drug_id"]]["is_mfd_drug"] = True
                drug_data[item["drug_id"]]["is_robot_drug"] = True
                drug_data[item["drug_id"]]["is_mfd_to_manual"] = False
                drug_data[item["drug_id"]]["is_robot_to_manual"] = False
                drug_data[item["drug_id"]]["display_drug_name"] = item["display_drug_name"]
                drug_data[item["drug_id"]]["short_drug_name_v1"] = fn_shorten_drugname(item["drug_name"], **kwargs)
                drug_data[item["drug_id"]]["short_drug_name_v2"] = fn_shorten_drugname_v2(item["display_drug_name"],
                                                                                          item["strength"],
                                                                                          item["strength_value"], **kwargs)
                drug_data[item["drug_id"]]["unique_drug_id"] = item["unique_drug_id"]
                drug_data[item["drug_id"]]["txr"] = item["txr"]
                drug_data[item["drug_id"]]["formatted_ndc"] = item["formatted_ndc"]
                drug_data[item["drug_id"]]["caution1"] = item["caution1"]
                drug_data[item["drug_id"]]["caution2"] = item["caution2"]
                drug_data[item["drug_id"]]["canister_id"] = item["canister_id"]  # Canister_id added
                drug_data[item["drug_id"]]["mfd_dropped_quantity"] = 0 if item["mfd_dropped_quantity"] is None else item["mfd_dropped_quantity"]
                drug_data[item["drug_id"]]["mfd_skipped_quantity"] = 0 if item["mfd_skipped_quantity"] is None else item["mfd_skipped_quantity"]
                drug_data[item["drug_id"]]["mfd_manual_filled_quantity"] = 0 if item["mfd_manual_filled_quantity"] is None else item["mfd_manual_filled_quantity"]
                drug_data[item["drug_id"]]["mfd_canister_ids"] = [item['mfd_canister_id']] if item["mfd_canister_id"] is not None else []
                drug_data[item["drug_id"]]["missing_drug"] = item["missing_drug"]
                drug_data[item["drug_id"]]["expire_soon"] = True if (item["formatted_ndc"], item["txr"]) in expiry_soon_fndc_txr else False
                if expiry_soon_drugs:
                    drug_data[item["drug_id"]]["expire_soon_drug"] = expiry_soon_drugs["drug_list"][item["drug_id"]]["expire_soon_drug"] if item["drug_id"] in expiry_soon_drugs["drug_list"] else None
                    drug_data[item["drug_id"]]["expiry_date"] = expiry_soon_drugs["drug_list"][item["drug_id"]]["expiry_date"] if item["drug_id"] in expiry_soon_drugs["drug_list"] else None
                else:
                    drug_data[item["drug_id"]]["expire_soon_drug"] = None
                    drug_data[item["drug_id"]]["expiry_date"] = None
            else:
                drug_data[item["drug_id"]]["quantity"] += item["quantity"]
                drug_data[item["drug_id"]]["dropped_qty"] += 0 if item["dropped_qty"] is None else item["dropped_qty"]
                drug_data[item["drug_id"]]["drug_tracker_dropped_qty"] += 0 if item["drug_tracker_dropped_qty"] is None else item["drug_tracker_dropped_qty"]
                drug_data[item["drug_id"]]["mfd_dropped_quantity"] += 0 if item["mfd_dropped_quantity"] is None else item[
                    "mfd_dropped_quantity"]
                drug_data[item["drug_id"]]["mfd_skipped_quantity"] += 0 if item["mfd_skipped_quantity"] is None else item[
                    "mfd_skipped_quantity"]
                drug_data[item["drug_id"]]["mfd_manual_filled_quantity"] += 0 if item[
                                                                                    "mfd_manual_filled_quantity"] is None else \
                item["mfd_manual_filled_quantity"]
                if item['mfd_canister_id'] and item['mfd_canister_id'] not in drug_data[item["drug_id"]]["mfd_canister_ids"]:
                    drug_data[item["drug_id"]]["mfd_canister_ids"].append(item["mfd_canister_id"])

            if not drug_data[item["drug_id"]]["is_removable"] and item["is_removable"]:
                drug_data[item["drug_id"]]["is_removable"] = item["is_removable"]

            txr_list.append(item["txr"])
            ndc_list.append(item['ndc'])
            # if flag is set True once, do not set False again
            if not drug_data[item["drug_id"]]["is_manual"]:
                drug_data[item["drug_id"]]["is_manual"] = item["is_manual"]
            if not drug_data[item["drug_id"]]["is_robot_to_manual"]:
                drug_data[item["drug_id"]]["is_robot_to_manual"] = item["is_robot_to_manual"]
            if not drug_data[item["drug_id"]]["is_mfd_to_manual"]:
                drug_data[item["drug_id"]]["is_mfd_to_manual"] = item["is_mfd_to_manual"]

            # If drug qty in any slot is missing then its not fully robot drug or mfd drug,
            # so if any one if false its, false
            if not item["is_robot_drug"]:
                drug_data[item["drug_id"]]["is_robot_drug"] = item["is_robot_drug"]
            if not item["is_mfd_drug"]:
                drug_data[item["drug_id"]]["is_mfd_drug"] = item["is_mfd_drug"]

            args = {"drug_id": item["drug_id"], "pack_id": pack_id}

            drug_list_data = get_drug_is_filled_in_drug_list(args)

            if drug_list_data:
                for drug_ig, drug in drug_list_data.items():
                    drug_data[item["drug_id"]]["is_filled"] = drug["is_filled"]

        canister_skipped_qty_dicts = get_canister_skipped_drug_qty_per_slot(pack_id=pack_id)

        quadrant_data = get_dropped_quadrant_data_slot_wise(pack_id=pack_id)

        error_status_set = {constants.PVS_CLASSIFICATION_STATUS_NOT_MATCHED,
                            constants.PVS_CLASSIFICATION_STATUS_BROKEN_PILL,
                            constants.PVS_CLASSIFICATION_STATUS_EXTRA_PILL}

        not_sure_status_set = {constants.PVS_CLASSIFICATION_STATUS_NOT_SURE,
                               constants.PVS_CLASSIFICATION_STATUS_MAY_BE_BROKEN_PILL,
                               constants.PVS_CLASSIFICATION_STATUS_PILL_DIMENSION_CONFUSING,
                               constants.PVS_CLASSIFICATION_STATUS_PILL_DIMENSION_NOT_REGISTERED}

        pack_verified_status = constants.PACK_VERIFIED_STATUS
        if not pvs_data:
            pack_verified_status = constants.PACK_NOT_MONITORED_STATUS
            logger.info(f"pack_verified_status : {pack_verified_status}")

        compare_qty_dict = {}
        dropped_qty_dict = {}
        predicted_qty_dict = {}

        for k in dict_slot_info.keys():
            logger.info(f"slot_number: {k}")
            try:
                canister_skipped_qty = float(canister_skipped_qty_dicts[k]) if float(
                    canister_skipped_qty_dicts[k]) else 0
                dict_slot_info[k]["canister_skipped_qty"] = canister_skipped_qty

            except:
                canister_skipped_qty = 0
                dict_slot_info[k]["canister_skipped_qty"] = canister_skipped_qty

            compare_qty = (dict_slot_info[k]["modified_quantity"]) - float(
                dict_slot_info[k]["modified_mfd_skipped_qty"]) - canister_skipped_qty
            dropped_qty = dict_slot_info[k]["modified_dropped_qty"]
            predicted_qty = None

            quad = [1, 2, 3, 4]
            if k in quadrant_data.keys():

                # quadrant_image_not_required = [element for element in quad if element not in quadrant_data[k]]
                quadrant_image_not_required = list(set(quad) - set(quadrant_data[k]))
                dict_slot_info[k]["pvs_data"]["quadrant_image_not_required"] = quadrant_image_not_required
            else:
                quadrant_image_not_required = [1, 2, 3, 4]
                dict_slot_info[k]["pvs_data"]["quadrant_image_not_required"] = quadrant_image_not_required

            if pvs_data:

                if "data_list" in dict_slot_info[k]["pvs_data"].keys():
                    logger.info(f"dict_slot_info: {dict_slot_info[k]['pvs_data']}")
                    drug_count = len((dict_slot_info[k]["pvs_data"]["data_list"]))
                    predicted_qty = 0
                    classification_list = []
                    # if k in quadrant_data.keys():
                    #     quadrant_image_not_received = quadrant_data[k]
                    # else:
                    #     quadrant_image_not_received = []
                    quadrant_image_not_received = [1, 2, 3, 4]

                    for i in range(drug_count):

                        quadrant = dict_slot_info[k]["pvs_data"]["data_list"][i]["quadrant"]
                        logger.info(f"slot number: {k}, quadrant: {quadrant}")

                        count = dict_slot_info[k]["pvs_data"]["data_list"][i]["predicted_count"]

                        predicted_qty += count

                        if quadrant in quadrant_image_not_received:
                            quadrant_image_not_received.remove(int(quadrant))

                        for j in range(count):
                            status = dict_slot_info[k]["pvs_data"]["data_list"][i]["crop_images"][j][
                                "pvs_classification_status"]
                            classification_list.append(status)

                    if predicted_qty == 0:
                        # This case happens when pvs data has slot image but there is no pill in that image so pvs
                        # didn't identify any pills >> no pvs data for that slot
                        pack_verified_status = constants.PACK_NOT_MONITORED_STATUS

                    dict_slot_info[k]["pvs_data"]["quadrant_image_not_received"] = quadrant_image_not_received

                    classification_set = set(classification_list)

                    if pack_verified_status != constants.PACK_NOT_MONITORED_STATUS:

                        for classification_status in classification_set:

                            if classification_status in not_sure_status_set:
                                pack_verified_status = constants.PACK_NOT_MONITORED_STATUS
                                logger.info(f"pack_verified_status : {pack_verified_status}")
                                break
                            elif classification_status != constants.PVS_CLASSIFICATION_STATUS_MATCHED:
                                pack_verified_status = constants.PACK_MONITORED_STATUS

                    logger.info(f"pack_verified_status : {pack_verified_status}")
                    # pvs_qty = dict_slot_info[k]["pvs_dropped_qty"]

                    logger.info(f"compare_qty: {compare_qty}, dropped_qty:{dropped_qty},predicted_qty: {predicted_qty}")

                    if compare_qty == dropped_qty == predicted_qty:
                        # dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_GREEN
                        if pvs_data_required:
                            if not_sure_status_set.intersection(classification_set):
                                dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_WHITE
                            elif constants.PVS_CLASSIFICATION_STATUS_EXTRA_PILL in classification_set:
                                dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_BLUE
                            elif error_status_set.intersection(classification_set):
                                dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_RED
                            else:
                                if pack_verified_status == constants.PACK_NOT_MONITORED_STATUS:
                                    dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_WHITE

                        #     for i in classification_set:
                        #         if i not in [constants.PVS_CLASSIFICATION_STATUS_MATCHED,
                        #                      constants.PVS_CLASSIFICATION_STATUS_NOT_SURE,
                        #                      constants.PVS_CLASSIFICATION_STATUS_PILL_DIMENSION_CONFUSING,
                        #                      constants.PVS_CLASSIFICATION_STATUS_PILL_DIMENSION_NOT_REGISTERED]:
                        #             dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_RED
                        #             break
                        # #         else:
                        # #             dict_slot_info[k]["slot_colour_status"] = "Green"
                        # #
                        # # else:
                        # #     dict_slot_info[k]["slot_colour_status"] = "Green"

                    else:
                        # if dict_slot_info[k]["pvs_data"]["quadrant_image_not_required"] == [1,2,3,4]:
                        #     dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_GREEN
                        #     continue

                        if pack_verified_status != constants.PACK_NOT_MONITORED_STATUS:
                            for classification_status in classification_set:

                                if classification_status in not_sure_status_set:
                                    pack_verified_status = constants.PACK_NOT_MONITORED_STATUS
                                    logger.info(f"pack_verified_status : {pack_verified_status}")
                                    break
                                else:
                                    pack_verified_status = constants.PACK_MONITORED_STATUS
                        if (dropped_qty > compare_qty) or (predicted_qty > compare_qty ) or (constants.PVS_CLASSIFICATION_STATUS_EXTRA_PILL in classification_set):
                            dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_BLUE
                        else:
                            dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_RED
                        # dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_BLUE if not all(qty < compare_qty for qty in (dropped_qty, predicted_qty)) \
                        #                                                                             else constants.SLOT_COLOUR_STATUS_BLUE if constants.PVS_CLASSIFICATION_STATUS_EXTRA_PILL in classification_set \
                        #                                                                             else constants.SLOT_COLOUR_STATUS_RED

                else:

                    # quadrant_image_not_received = [element for element in quad if
                    #                                element not in quadrant_image_not_required]
                    # quadrant_image_not_received = list(set(quad) - set(quadrant_image_not_required))
                    quadrant_image_not_received = [1, 2, 3, 4]
                    dict_slot_info[k]["pvs_data"]["quadrant_image_not_received"] = quadrant_image_not_received

                    # if all drugs skipped >> no dropped qty >> no PVS data
                    # compare_qty = 0 ==> all drugs are skipped.

                    # if compare_qty:
                    #     pack_verified_status = constants.PACK_NOT_MONITORED_STATUS
                    if dropped_qty:
                        pack_verified_status = constants.PACK_NOT_MONITORED_STATUS

                    if compare_qty == dropped_qty:
                        dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_WHITE
                    else:
                        dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_BLUE if dropped_qty > compare_qty else constants.SLOT_COLOUR_STATUS_RED

            else:

                # quadrant_image_not_received = [element for element in quad if
                #                                element not in quadrant_image_not_required]
                # quadrant_image_not_received = list(set(quad) - set(quadrant_image_not_required))
                quadrant_image_not_received = [1, 2, 3, 4]
                dict_slot_info[k]["pvs_data"]["quadrant_image_not_received"] = quadrant_image_not_received

                if compare_qty == dropped_qty:
                    dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_WHITE
                else:
                    dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_BLUE if dropped_qty > compare_qty else constants.SLOT_COLOUR_STATUS_RED
                    # if dict_slot_info[k]["pvs_data"]["quadrant_image_not_required"] == [1, 2, 3, 4]:
                    #     dict_slot_info[k]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_GREEN

            compare_qty_dict[k] = compare_qty
            dropped_qty_dict[k] = dropped_qty
            predicted_qty_dict[k] = predicted_qty

        pill_jump_error_slot_set = get_pill_jump_error_slot_for_given_pack(pack_id=pack_id)

        for slot in dict_slot_info:
            if "slot_colour_status" not in dict_slot_info[slot].keys():
                if pack_verified_status == constants.PACK_NOT_MONITORED_STATUS:
                    dict_slot_info[slot]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_WHITE
                else:
                    dict_slot_info[slot]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_GREEN

            if int(slot) in pill_jump_error_slot_set:

                if dict_slot_info[slot]["slot_colour_status"] == constants.SLOT_COLOUR_STATUS_RED:
                    dict_slot_info[slot]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_RED_BLUE
                else:
                    dict_slot_info[slot]["slot_colour_status"] = constants.SLOT_COLOUR_STATUS_BLUE

        if call_from_mvs:
            for slot in pill_jump_error_slot_set:
                if (slot) not in dict_slot_info.keys():
                    dict_slot_info[(slot)] = {"slot_colour_status": constants.SLOT_COLOUR_STATUS_BLUE,
                                              "drug_details": []}
                    if pack_verified_status == constants.PACK_VERIFIED_STATUS:
                        pack_verified_status = constants.PACK_MONITORED_STATUS
            # data should be insert in both table when pack reach at MVS screen only
            # This main function calls from 2 place>> In slots API, condition update_pack_verification_required >> true
            # When another func call this function at that time condition >> update_pack_verification_required >> false

            logger.info(f"Inserting data in pack_verification and pack_verification_details table for pack id : {pack_id}")

            status = insert_data_in_pack_verification_and_pack_verification_details(pack_id=pack_id,
                                                                                    dict_slot_info=dict_slot_info,
                                                                                    compare_qty_dict=compare_qty_dict,
                                                                                    dropped_qty_dict=dropped_qty_dict,
                                                                                    predicted_qty_dict=predicted_qty_dict,
                                                                                    pack_verified_status=pack_verified_status,
                                                                                    user_id=user_id)

            logger.info("In get_slots_for_label_printing, insert status of pack_verification_details: {}".format(status))

        change_ndc_drug_list = get_available_drugs_for_recommended_canisters(list(set(ndc_list)))
        change_ndc_drug_list = [x.zfill(11) for x in change_ndc_drug_list]
        if txr_list:
            for record in drug_data.values():
                record['change_ndc_available'] = True if record['ndc'] in change_ndc_drug_list else False
                record['inventory_qty'] = inventory_data.get((record['formatted_ndc'], record['txr']), None)
                if record['inventory_qty']:
                    record['is_in_stock'] = 0 if record["inventory_qty"] <= 0 else 1
                else:
                    record['is_in_stock'] = None

        drug_data = list(drug_data.values())
        pack_manual_drug_info = db_get_pack_manual_drug_count(pack_id)
        manual_drug_count = pack_manual_drug_info['manual_drug_count']
        slot_image_crop_dimension = db_get_pvs_dimension()
        print_info = get_latest_print_data(pack_id=pack_id)
        logger.info("get_slots_for_label_printing print_info {}".format(print_info))
        fod_data = []
        if module_id and module_id == constants.MODULE_FILL_ERROR_FLOW:
            fod_data = db_fetch_fod_only_slots(pack_id)
        qty = 0
        filled_qty = 0
        if not cyclic_flag:
            for key, value in dict_slot_info.items():
                for drug_record in value['drug_details']:
                    qty += value['quantity']
                    filled_qty_to_add = Decimal(0.0) if not drug_record['filled_quantity'] else drug_record[
                        'filled_quantity']
                    filled_qty += filled_qty_to_add
            first_key = list(dict_slot_info.keys())[0]
            dict_slot_info[first_key]['quantity'] = qty
            dict_slot_info[first_key]['drug_details'][0]['quantity'] = qty
            dict_slot_info[first_key]['drug_details'][0]['filled_quantity'] = filled_qty
            dict_slot_info = {first_key: dict_slot_info[first_key]}
            dict_slot_info[first_key]['drug_details'] = [dict_slot_info[first_key]['drug_details'][0]]
            dict_slot_info[first_key]['drug_details'][0]['is_filled'] = 0 if filled_qty < qty else 1

        # bypassing removal of 0 qty as FE will remove by checking qty flag from their end
        updated_dict_slot_info = {}
        for pack_grid_id, slot_data in dict_slot_info.items():
            slot_data["drug_details"] = [d for d in slot_data["drug_details"] if d["quantity"] != 0.00 or d["filled_quantity"] != 0.00]
            if slot_data["drug_details"]:
                updated_dict_slot_info[pack_grid_id] = slot_data
        # adding fod slots to show which have no drug in them
        if module_id and module_id == constants.MODULE_FILL_ERROR_FLOW:
            for fod_pack_grid_id in fod_data:
                updated_dict_slot_info[fod_pack_grid_id] = {"is_fod": True, "drug_details": []}
        response = {"slot_data": updated_dict_slot_info, "drug_list": drug_data,
                    "slot_image_crop_dimension": slot_image_crop_dimension,
                    "manual_drug_count": manual_drug_count, 'mfd_pack': is_mfd_pack,
                    'print_info': print_info, "pack_verified_status": pack_verified_status,
                    "change_rx": change_rx_flag,
                    "hold_rx_dict": hold_rx_dict,
                    "expiry_soon_fndc_txr": expiry_soon_fndc_txr}
        return create_response(response)

    except Exception as e:
        logger.error("Error in get_slots_for_label_printing {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(f"Error in get_slots_for_label_printing: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
        return error(0)


@validate(required_fields=["pack_id", "system_id"], validate_pack_id='pack_id')
@log_args_and_response
def prepare_label_data(dict_pack_info):
    """ Takes the patient_id, pharmacy_id, patient_id, system_id as the input parameters and returns the information
        required for label printing..

        Args:
            dict_pack_info (dict): The information like patient_id, pack_id and pharmacy_id.

        Returns:
           dict: It contains the label printing information

        Examples:
            >>> prepare_label_data({})
    """
    drug_image_key = 'image_name'
    pack_id = int(dict_pack_info["pack_id"])
    system_id = int(dict_pack_info["system_id"])
    # short drug name v1 parameters
    v1_width = int(dict_pack_info.get('v1_width', settings.SHORT_DRUG_V1_WIDTH))
    v1_min = int(dict_pack_info.get('v1_min', settings.SHORT_DRUG_V1_MIN))
    # short drug name v2 parameters
    v2_width = int(dict_pack_info.get('v2_width', settings.SHORT_DRUG_V2_WIDTH))
    v2_min = int(dict_pack_info.get('v2_min', settings.SHORT_DRUG_V2_MIN))
    v2_include_strength = bool(int(dict_pack_info.get('v2_strength_flag', settings.SHORT_DRUG_V2_STRENGTH_FLAG)))
    image_b64 = bool(int(dict_pack_info.get('image_b64', 0)))  # whether to include b64 image data for drug images
    system_setting = dict()
    dry_run = bool(json.loads(str(dict_pack_info.get("dry_run", 'false'))))
    caution_str = ""
    label_version = settings.LABEL_VERSION
    slot_details = {}
    pack_status = None
    is_reseal_pack = False
    updated_quantity_data_for_label = None

    # TODO: When the output of this function changes, also update the below sample response
    # added
    if dry_run or pack_id == 0:
        logger.debug("prepare_label_data: dry_run case- in getlabelinfo")
        getlabelinfosample.pack_id = pack_id
        label_info = getlabelinfosample.get_label_info_sample_data
        logger.info("prepare_label_data: dry_run case- fetched test label info")
        if label_info:
            # changing actual pack_display_id in test response (In dry run case, pack_id is same as pack_display_id).
            logger.info("prepare_label_data: dry_run case- changing pack_display_id-{} in label info"
                         .format(pack_id))
            label_info["pack_info"]["pack_display_id"] = pack_id
            logger.info("prepare_label_data: dry_run case- pack_display_id-{} changed".format(pack_id))
        return create_response(label_info)

    try:
        pack_status_query = db_get_ext_pack_data_by_pack_ids_dao([pack_id])
        for record in pack_status_query:
            pack_status = record["pack_usage_status_id"]

        if pack_status and pack_status == constants.EXT_PACK_USAGE_STATUS_PACK_RESEALED_ID:
            is_reseal_pack = True
    except Exception as e:
        logger.error("Error in prepare_label_data: while fetching the pack status")
        raise e

    try:
        pack_info = next(db_get_label_info(pack_id))
        pack_info["is_reseal_pack"] = is_reseal_pack
        logger.info("Pack info in prepare_label_data")
        pharmacy_data = next(get_pharmacy_data_for_system_id(system_id=system_id))
        logger.info("Pharmacy data info in prepare_label_data")
        patient_details = next(get_patient_details_for_patient_id(patient_id=pack_info["patient_id"]))
        logger.info("Patient details info in prepare_label_data")
    except StopIteration as e:
        logger.error("error in in prepare_label_data")
        logger.error(e, exc_info=True)
        return error(1005)

    try:
        drug_args = {}  # short drug name arguments
        if v2_width:
            drug_args["ai_width"] = v2_width
        if v2_min:
            drug_args["ai_min"] = v2_min
        if v2_include_strength:
            drug_args["include_strength"] = v2_include_strength
        pack_status = pack_info["pack_status"]
        pharmacy_rx_info = get_label_drugs(pack_id, pack_status, **drug_args)
        logger.info("pharmacy_rx_info info in prepare_label_data")
        if is_reseal_pack:
            updated_quantity_data_for_label = db_get_updated_quantity_data_for_label([pack_id])

        temp_pharmacy_rx_info = deepcopy(pharmacy_rx_info)
        if updated_quantity_data_for_label:
            for pharmacy_rx in temp_pharmacy_rx_info:
                if pharmacy_rx["formatted_ndc"] in updated_quantity_data_for_label:
                    index = pharmacy_rx_info.index(pharmacy_rx)
                    pharmacy_rx_info[index]["rx_info"][0]["print_qty"] = updated_quantity_data_for_label[
                        pharmacy_rx["formatted_ndc"]]
                else:
                    pharmacy_rx_info.remove(pharmacy_rx)

        if image_b64:
            get_b64_images(pharmacy_rx_info, drug_image_key, drug_blob_dir, True)
        slot_args = {'pack_id': pack_id, 'system_id': system_id}
        logger.info("Slot args info in prepare_label_data")
        # short drug name arguments
        if v1_min:
            slot_args["ai_min"] = v1_min
        if v1_width:
            slot_args["ai_width"] = v1_width
        if not pack_info['delivery_schedule'] == 'On Demand/PRN':
            slot_details = json.loads(get_slots_for_label_printing(slot_args))
            if 'code' in slot_details.keys():
                return error(slot_details['code'])
            logger.info("slot_details info in prepare_label_data")
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(2001)

    if not (pharmacy_rx_info or pharmacy_data or pack_info or patient_details or slot_details):
        logger.error("error in  info in prepare_label_data")
        return error(1005)

    try:
        system_setting = get_system_setting_by_system_id(system_id=system_id)
    except Exception as e:
        logger.error(e)
        pass

    try:
        modified_slot_details = {}
        if not pack_info['delivery_schedule'] == 'On Demand/PRN':
            modified_slot_details = {"data": {"slot_data": dict()}}
            slot_data = slot_details["data"]["slot_data"]
            expiry_soon_fndc_txr = slot_details["data"]["expiry_soon_fndc_txr"]

            modified_slot_data = dict()
            for slot_location, slot_details in slot_data.items():
                slot_row = slot_details["slot_row"]
                slot_column = slot_details["slot_column"]
                slot_tuple = (slot_row, slot_column)
                modified_slot_location = constants.PACK_GRID_V3_DICT_ACCORDING_TO_V2[slot_tuple]
                modified_slot_data[modified_slot_location] = slot_details

            logger.info(f"In prepare_label_data, modified_slot_data: {modified_slot_data}")

            modified_slot_details["data"]["slot_data"] = modified_slot_data
        else:
            modified_slot_details = {"data": {"slot_data": db_get_slot_wise_hoa_for_pack(pack_id)}}



    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1005, " - Error: {}".format(e))

    try:
        for record in pharmacy_rx_info:
            if not pack_info['delivery_schedule'] == 'On Demand/PRN':
                record['expire_soon'] = True if [record["formatted_ndc"], record["txr"]] in expiry_soon_fndc_txr else False
            if (record["caution1"] is not None) and (str(record["caution1"]).strip() not in caution_str):
                if len(caution_str) == 0:
                    caution_str = str(record["caution1"]).strip()
                else:
                    caution_str = caution_str + " " + str(record["caution1"]).strip()
    except Exception as e:
        logger.error("Error in prepare_label_data {}".format(e))
        pass

    if not modified_slot_details:
        modified_slot_details = {"data": {"slot_data": {"1": {}}}}
    data = {"pharmacy_data": pharmacy_data, "patient_details": patient_details, "pack_info": pack_info,
            "pharmacy_rx_info": pharmacy_rx_info, "slot_details": modified_slot_details,
            "system_setting": system_setting, "caution_str": caution_str, "label_version": label_version}
    logger.info("Response of prepare_label_data {}".format(data))
    return create_response(data)


@log_args_and_response
def get_b64_images(image_list, image_key, blob_dir, drug_image):
    """
    Sets new image key as image_key_b64 (suffix _b64) and base64 data as value for every object in image_list

    :param image_list:
    :param image_key: key name where image name is available
    :return:
    """
    new_key = image_key + '_b64'
    exception_list = list()
    threads = list()
    for item in image_list:
        item[new_key] = None
        try:
            image = item[image_key]
            if image:
                t = ExcThread(exception_list, target=download_image_as_b64, args=[item, image, new_key, blob_dir, drug_image])
                threads.append(t)
                t.start()
        except Exception as e:
            logger.error(e, exc_info=True)
            break
            pass  # passing as no
    [t.join() for t in threads]


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

    if not data:
        logger.info("Output response of populate_slot_transaction no data {}".format(1))# No data was sent, no action needed
        return create_response(1)

    pack_id = data[0]["pack_id"]
    device_id = pack_list_info["device_id"]

    logger.info("Slot Transaction for pack id {} initiated.".format(pack_id))

    canister_dropped_quantity = dict()
    slot_transaction_list = []
    mfd_data_list = []
    mfd_canister_location_dict = dict()
    local_inventory_update_data = list()

    valid_pack = verify_pack_id_by_system_id_dao(pack_id=pack_id, system_id=system_id)
    if not valid_pack:
        return error(1014)

    pack_data = db_get_pack_info(pack_id=pack_id)
    if not pack_data:
        return error(1014)

    # pack_slot_trans = db_get_pack_slot_transaction(pack_id=pack_id)
    # if pack_slot_trans:
    #     logger.info("Output response of populate_slot_transaction already exists {}".format(1))
    #     return create_response(1)

    try:
        with db.transaction():
            for record in data:
                if not record['mfd_drug']:
                    location_id, is_disable = get_location_id_from_display_location(device_id=record.pop('device_id'),
                                                                                    display_location=record.pop(
                                                                                        'display_location'))
                    record["created_by"] = 1  # todo remove as user is not creating slottransaction
                    record['location_id'] = location_id
                    if record['canister_id']:
                        if str(record['canister_id']) not in canister_dropped_quantity.keys():
                            canister_dropped_quantity[str(record['canister_id'])] = 0
                        canister_dropped_quantity[str(record['canister_id'])] += record['dropped_qty']

                    record.pop('mfd_drug', None)
                    slot_transaction_list.append(record)
                else:
                    if record.get('mfd_details', None):

                        for mfd_analysis_id, data in record["mfd_details"].items():
                            location_id, is_disable = get_location_id_from_display_location(
                                device_id=record['device_id'],
                                display_location=data["display_location"])

                            mfd_data_list.extend(data["analysis_details_id"])

                            mfd_canister_location_dict[int(mfd_analysis_id)] = location_id

            logger.info(f"In populate_slot_transaction, slot_transaction_list:{slot_transaction_list}")
            if slot_transaction_list:
                status_1 = db_create_multi_record_in_slot_transaction(slot_transaction_list=slot_transaction_list)
            if slot_transaction_list:
                populate_drug_tracker(slot_transaction_list)

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
            # update_replenish_based_on_device(device_id)

            if pack_list_info.get("error_list"):
                logger.info(f"In populate_slot_transaction, inserting data in pill_jump_error")
                error_list = pack_list_info["error_list"]
                """
                error_list = [
                            {"slot_number":12,"quadrant":2, "drop_number":5, "config_id":7, "device_id": 2, "count": 2},
                            {"slot_number":15,"quadrant":1, "drop_number":5, "config_id":1, "device_id": 2, "count": 1}
                            ]
                """
                insert_list = []

                for info in error_list:
                    info["quantity"] = info.pop('count', None)
                    info["pack_id"] = pack_id
                    insert_list.append(info)

                if insert_list:
                    logger.info(f"In populate_slot_transaction, insert_list: {insert_list}")
                    PillJumpError.insert_many(insert_list).execute()
                    logger.info(f"In populate_slot_transaction, data inserted in pill_jump_error")

        # if len(canister_dropped_quantity):
        #     # update the local inventory with the dropped qty for the Canister Drugs
        #     drug_data = db_get_by_id_list(canister_id_list=list(canister_dropped_quantity.keys()))
        #     for drug in drug_data:
        #         temp_dict = {"ndc": drug["ndc"],
        #                      "formatted_ndc": drug["formatted_ndc"],
        #                      "txr": drug["txr"],
        #                      "quantity": canister_dropped_quantity[str(drug["canister_id"])]}
        #         local_inventory_update_data.append(temp_dict.copy())
        #
        #     update_local_inventory_by_slot_transaction(pack_id=pack_id, drop_data=local_inventory_update_data)
        logger.info("Slot Transaction for pack id {} ended.".format(pack_id))

    except StopIteration as e:
        logger.error("Error in populate_slot_transaction {}".format(e))
        return error(2001)
    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("Error in populate_slot_transaction {}".format(e))
        return error(2001, e)
    except ValueError as e:
        logger.error("Error in populate_slot_transaction {}".format(e))
        return error(2005, str(e))
    logger.info("Output response of populate_slot_transaction is {}".format(status))
    return create_response(status)


def get_pack_data(company_id, pack_ids):
    """
    Check if any pack is deleted
    :param request_params:
    :return: json
    """
    logger.debug("Inside get_pack_data")
    try:
        """
        To update the reddis template data in case of packs are deleted
        """
        pack_ids = list(map(int, pack_ids.split(',')))
        status = settings.DELETED_PACK_STATUS

        pack_list = get_pack_display_ids_for_given_packs(company_id=company_id, pack_ids=pack_ids, status=status)

        response = {'pack_list': pack_list}

        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in get_pack_data: {e}")
        raise e


@validate(required_fields=["company_id"])
def get_user_assigned_packs(dict_pack_info):
    print(dict_pack_info)
    company_id = int(dict_pack_info["company_id"])
    filter_fields = dict_pack_info.get('filters', None)
    if filter_fields:
        filter_fields = json.loads(filter_fields)
    sort_fields = dict_pack_info.get('sort_fields', None)
    if sort_fields:
        sort_fields = json.loads(sort_fields)
    paginate = dict_pack_info.get('paginate', None)
    if paginate:
        paginate = json.loads(paginate)
    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, 'Missing key(s) in paginate.')
    try:
        query, count = get_user_assigned_packs_dao(company_id=company_id, filter_fields=filter_fields, sort_fields=sort_fields)
        pack_data = dict()
        for record in query:
            if record['facility_id'] not in pack_data:
                pack_data[record['facility_id']] = {
                    'facility_id': record['facility_id'],
                    'facility_name': record['facility_name'],
                    'patient_data': list()
                }
                pack_data[record['facility_id']]['patient_data'].append(record)

            else:
                pack_data[record['facility_id']]['patient_data'].append(record)

        pack_data = list(pack_data.values())
        if paginate:
            if 'page_number' not in paginate:
                raise ValueError('paginate paramater must have key page_number')
            if 'number_of_rows' not in paginate:
                raise ValueError('paginate paramater must have key number_of_rows')
            pack_data = pack_data[(paginate['page_number'] - 1) * paginate['number_of_rows']:
                                  paginate['page_number'] * paginate['number_of_rows']]

        return {"pack_data": pack_data, "number_of_records": count}
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["company_id"])
def get_user_assigned_pack_count(user_assigned_pack_dict):

    try:
        company_id = user_assigned_pack_dict['company_id']
        users = user_assigned_pack_dict.get('users', None)

        response = get_user_assigned_pack_count_dao(company_id=company_id, users=users)
        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def getUserWiesPacksCount(company_id):
    try:
        query  = get_user_wise_pack_count_dao(company_id=company_id)

        data = getrecords({}, {}, query, True)
        result = {}
        for row in data:
            result[row["assigned_to"]] = row["count"]
        return result

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in getUserWiesPacksCount: {e}")
        return e


@validate(required_fields=["batch_id", "system_id", "company_id"])
def get_batch_canister_manual_drugs(dict_batch_info):
    logger.info("input args for get_batch_canister_manual_drugs {}".format(dict_batch_info))
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
            query = db_get_batch_canister_manual_drugs(system_id=system_id,
                                                                           list_type=list_type,
                                                                           pack_ids=pack_id_list,
                                                                           pack_queue=True)
        elif drug_type == "manual":
            query = get_batch_manual_drug_list(list_type=list_type,
                                               pack_ids=pack_id_list,
                                               pack_queue=True,
                                               system_id=system_id)


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


def get_scheduled_till_date(dict_batch_info):
    company_id = dict_batch_info['company_id']
    system_robot_data = get_robot_status(company_id)
    if not system_robot_data:
        return system_robot_data
    system_max_batch_id_dict = get_system_wise_batch_id(list(system_robot_data.keys()))
    system_end_date_dict = {}
    for system, batch in system_max_batch_id_dict.items():
        system_info = get_system_setting_by_system_id(system_id=system)
        total_packs,scheduled_start_date = get_batch_scheduled_start_date_and_packs(batch)
        scheduled_end_date = get_end_date(system_info,total_packs,scheduled_start_date)
        system_robot_data[system]['scheduled_end_date'] = scheduled_end_date
    return system_robot_data


@log_args_and_response
def get_end_date(system_info, total_packs, start_date):
    try:
        AUTOMATIC_PER_DAY_HOURS = int(system_info['AUTOMATIC_PER_DAY_HOURS'])
        AUTOMATIC_PER_HOUR = int(system_info['AUTOMATIC_PER_HOUR'])
        AUTOMATIC_SATURDAY_HOURS = int(system_info['AUTOMATIC_SATURDAY_HOURS'])
        AUTOMATIC_SUNDAY_HOURS = int(system_info['AUTOMATIC_SUNDAY_HOURS'])
        batch_date_day_dict = {}
        rem_cap = 0
        processing_hours = 0

        last_batch_start_date = start_date
        last_batch_start_date_str = str(last_batch_start_date)  # this is in date format
        last_batch_packs_count = total_packs  # will take from db

        batch_date_day_dict[last_batch_start_date] = get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                  int(last_batch_start_date_str.split('-')[1]),
                                                                  int(last_batch_start_date_str.split('-')[2]))
        while last_batch_packs_count > 0:
            last_batch_start_date_str = str(last_batch_start_date)
            batch_date_day_dict[last_batch_start_date] = get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                      int(last_batch_start_date_str.split('-')[1]),
                                                                      int(last_batch_start_date_str.split('-')[2]))
            if batch_date_day_dict[last_batch_start_date] == settings.SATURDAY:
                if AUTOMATIC_SATURDAY_HOURS == 0:
                    last_batch_start_date += datetime.timedelta(days=1)
                elif last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_SATURDAY_HOURS
                    if last_batch_packs_count == 0:
                        scheduled_end_date = last_batch_start_date - datetime.timedelta(days=1)
                        # self.batch_processing_time_dict[self.batch_count] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                    # rem_cap = AUTOMATIC_PER_HOUR*AUTOMATIC_SATURDAY_HOURS - batch_packs_count
                    # if rem_cap <= AUTOMATIC_PER_HOUR:
                    #     last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0
                    scheduled_end_date = last_batch_start_date
                    # self.batch_processing_time_dict[self.batch_count] = processing_hours
            elif batch_date_day_dict[last_batch_start_date] == settings.SUNDAY:
                if AUTOMATIC_SUNDAY_HOURS == 0:
                    last_batch_start_date += datetime.timedelta(days=1)
                elif last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS and AUTOMATIC_SUNDAY_HOURS > 0:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_SUNDAY_HOURS
                    if last_batch_packs_count == 0:
                        scheduled_end_date = last_batch_start_date - datetime.timedelta(days=1)
                        # self.batch_processing_time_dict[self.batch_count] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                    last_batch_packs_count = 0
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0
                    scheduled_end_date = last_batch_start_date
                    # self.batch_processing_time_dict[self.batch_count] = processing_hours
            else:
                if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                    last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS
                    last_batch_start_date += datetime.timedelta(days=1)
                    processing_hours += AUTOMATIC_PER_DAY_HOURS
                    if last_batch_packs_count == 0:
                        scheduled_end_date = last_batch_start_date - datetime.timedelta(days=1)
                        # self.batch_processing_time_dict[self.batch_count] = processing_hours
                elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                    processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                    last_batch_packs_count = 0
                    scheduled_end_date = last_batch_start_date
        return scheduled_end_date

    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def get_weekdays(year, month, day):
    try:
        thisXMas = datetime.date(year, month, day)
        thisXMasDay = thisXMas.weekday()
        weekday = settings.WEEKDAYS[thisXMasDay]
        return weekday
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def prepare_pack_reason_dict(pack_id: int, pack_display_id: int, delete_reason: str) -> Dict[str, Any]:
    """
    To return consistent dictionary data containing pack_id, pack_display_id and delete_reason and associate it
    with respective Pack ID

    :param pack_id: Pack ID
    :param pack_display_id: Pack Display ID
    :param delete_reason: Delete Reason
    """
    return {
        "pack_id": pack_id,
        "pack_display_id": pack_display_id,
        "reason": delete_reason
    }


@log_args_and_response
def update_packs_filled_by_in_ips(pack_ids, ips_username, pack_and_display_ids, ips_comm_settings,
                                  token=settings.ACCESS_TOKEN, pack_edit_flag=False):
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
        token = get_token() if (token == None or token == "") else token
        batch_size = int(os.environ.get('IPS_FILLED_BY_UPDATE_BATCH_SIZE', 4))
        logger.info('updating filled_by: {} in IPS for packs: {}'
                    .format(ips_username, pack_ids))
        for packs in batchify(pack_ids, batch_size):
            for pack in packs:
                update_pack_filled_by_in_ips(pack_id=pack, ips_username=ips_username,
                                             pack_and_display_ids=pack_and_display_ids,
                                             ips_comm_settings=ips_comm_settings, token=token,
                                             pack_edit_flag=pack_edit_flag)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("update_packs_filled_by_in_ips", e, exc_info=True)
        raise RealTimeDBException
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error("update_packs_filled_by_in_ips", e, exc_info=True)
        raise


@log_args_and_response
def update_pack_filled_by_in_ips(pack_id, ips_username, pack_and_display_ids, ips_comm_settings, token,
                                 pack_edit_flag=False):
    try:
        rx_ndc_dict = get_rx_wise_ndc_fill(pack_id=pack_id, pack_and_display_ids=pack_and_display_ids)

        parameters = {
            "batchid": pack_id,
            "username": ips_username,
            "newdruglist": rx_ndc_dict,
            "token": token,
            "pack_edit": pack_edit_flag
        }
        print(parameters)
        send_data(base_url=ips_comm_settings['BASE_URL_IPS_WEB'].split("//")[1], webservice_url=settings.FILLED_BY_URL,
                  parameters=parameters, counter=0, request_type="POST", token=token, ips_api=True)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e, exc_info=True)
        pass


@log_args_and_response
def download_image_as_b64(data, image, key_name, blob_dir, drug_image=False):
    """
    Downloads image as string and adds b64encoded data into key_name key.

    :param data: dict
    :param image: str
    :param key_name: str
    :param blob_dir: str
    :return:
    """
    try:
        bin_image = blob_as_string(image, blob_dir, drug_image)
        img_string = base64.b64encode(bin_image).decode()
        data[key_name] = img_string
    except Exception as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error in download_image_as_b64: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
        logger.error('Error in getting image: {} as base64 string'.format(image))
        raise


@log_args_and_response
def get_pack_grid_data(pack_id, grid_type):
    """
        Fetches to get pack grid data
        :return:
    """

    try:
        grid_type = constants.PACK_GRID_ROW_7x4 if not grid_type else int(grid_type)
        if pack_id:
            packaging_type = int(db_get_pack_info(pack_id)['packaging_type'])
            grid_type = constants.PACK_GRID_ROW_8x4 if packaging_type in [
                constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_8X4,
                constants.PACKAGING_TYPE_BLISTER_PACK_UNIT_8X4] else constants.PACK_GRID_ROW_7x4
        # get pack grid data slot wise and pack grid row and pack grid column
        pack_grid_data, pack_grid_row, pack_grid_column = get_pack_grid_data_dao(grid_type)

        # return total row (we consider row = 0 to 6 ,total = 7 row) and column (we consider column = 0 to 3 ,total = 4 column)
        response_data = {"pack_grid_data": pack_grid_data,
                         "pack_grid_column": pack_grid_column + 1,
                         "pack_grid_row": pack_grid_row + 1}

        return create_response(response_data)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_pack_grid_data {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in get_pack_grid_data {}".format(e))
        return error(1000, "Error in get_pack_grid_data: " + str(e))


@log_args_and_response
def db_update_rx_changed_packs_manual_count(company_id):
    change_rx_count_flag: bool = False
    try:
        date_type = "admin_start_date"
        date_to_date = get_datetime() + datetime.timedelta(days=45)
        date_to: str = date_to_date.strftime('%Y-%m-%d')

        date_from_date = datetime.datetime.strptime(date_to, '%Y-%m-%d') - datetime.timedelta(days=90)
        date_from: str = date_from_date.strftime('%Y-%m-%d')

        pack_status_list = [settings.MANUAL_PACK_STATUS, settings.PACK_STATUS_CHANGE_RX]
        assigned_to = 0
        user_stats = False

        status_pack_count_dict, value_status_id_dict, total_packs, assigned_user_pack_count = get_manual_packs_data(
            company_id, date_from, date_to, date_type, assigned_to, user_stats, pack_status_list)

        for status, pack_count in status_pack_count_dict.items():
            if value_status_id_dict[status] == settings.PACK_STATUS_CHANGE_RX:
                change_rx_count_flag = True
                logger.debug("Update Rx Change Packs Count in Manual Filling. Status: {}, Pack Count: {}..."
                             .format(status, pack_count))
                update_manual_packs_count_after_change_rx(document_name=settings.CONST_TEMPLATE_MASTER_DOC_ID,
                                                          company_id=company_id, raise_exc=False,
                                                          update_count=pack_count)
        if not change_rx_count_flag:
            update_manual_packs_count_after_change_rx(document_name=settings.CONST_TEMPLATE_MASTER_DOC_ID,
                                                      company_id=company_id, raise_exc=False,
                                                      update_count=0)

    except (IntegrityError, InternalError, DataError, AutoProcessTemplateException, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException


@log_args_and_response
def map_user_pack_dao(userpacks):
    user_id = None
    call_from_client = None
    missing_drug_list_dict: Dict[str, Any] = dict()
    status_update: int = 0
    pack_details = list()
    update_notification_packs = []

    try:

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
                if "rx_change_pack_ids" in item.keys():
                    if item["rx_change_pack_ids"]:
                        update_notification_packs = [int(item) for item in item["rx_change_pack_ids"]]
                company_id = item["company_id"] if 'company_id' in item.keys() else None

                # Prepare the dictionary to update the Missing Drug status for respective Packs
                if "reason_action" in item:
                    missing_drug_list_dict = {"pack_ids": pack_list, "created_date": get_current_date_time(),
                                              "created_by": item['user_id'], "reason_action": item["reason_action"],
                                              "reason": item.get("reason")}

                    if item["reason_action"] == MVS_MISSING_PILLS:
                        missing_drug_list_dict.update({"rx_no_list": item["reason_rx_no_list"]})

                    if item["reason_action"] == MVS_DRUGS_OUT_OF_STOCK:
                        missing_drug_list_dict.update({"drug_list": item["drug_list"]})

                query = get_pack_assigned_to(pack_list)
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
                    for row in query:
                        if row["id"] == item:
                            pack_details.append(
                                {'pack_id': item, "assigned_to": assigned_to, "assigned_from": row["assigned_from"]})
                    db_update_assigned_to_pack_details(create_dict, update_dict)

                # Trigger the appropriate method based on MVS reason of Drugs Out of Stock or Missing Pills
                if missing_drug_list_dict:
                    if missing_drug_list_dict["reason_action"] == MVS_MISSING_PILLS:
                        # now, drug will be out of stock in case of missing pills and not enough drug quantity.
                        status_update, drug_list = add_missing_drug_record_dao([missing_drug_list_dict])
                        missing_drug_list_dict["drug_list"] = drug_list
                        status = update_drugs_out_of_stock([missing_drug_list_dict])

                    if missing_drug_list_dict["reason_action"] == MVS_DRUGS_OUT_OF_STOCK:
                        status_update = update_drugs_out_of_stock([missing_drug_list_dict])

                    if status_update == 0:
                        return False

        # Notifications(call_from_client=call_from_client).check_and_send_assign_message(pack_details)
        logger.info("Updating couchdb for notification_dp_all if change RX is triggered or not. {} .... {}".format(update_notification_packs, company_id))
        if update_notification_packs and company_id:

            notify_change_rx_templates = db_get_notification_packs_to_update(update_notification_packs)
            status, notification_status = update_assigned_to_in_notification_dp_all_for_change_rx_packs(notify_change_rx_templates, assigned_to, company_id)

        #     Update notification for packs.
        # Notifications(call_from_client=call_from_client).check_and_send_assign_message(pack_details)

        return True

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in map_user_pack_dao: {e}")
        return e


@log_args_and_response
def update_drugs_out_of_stock(drug_data: List[Dict[str, Any]], user_id=None) -> int:
    status: int = 0

    try:
        if settings.USE_EPBM:
            drug_args = {"drug_id": drug_data[0]["drug_list"], "is_in_stock": 0, "user_id": drug_data[0]["created_by"],
                         "user_confirmation": True, "reason": drug_data[0]['reason']}
            response = update_drug_status(drug_args)
            if isinstance(response, str):
                response_json = json.loads(response)
                error_status = response_json.get("status", None)
                if error_status and error_status == settings.FAILURE_RESPONSE:
                    raise Exception
            else:
                status = 1
        else:
            status = 1

        return status
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def add_task_elite(param):
    try:
        logger.info(celery_app.conf.broker_url)
        logger.debug('Adding Task to elite API call')
        task_args = tuple(param.items())
        task_id = celery_app.send_task(
            'tasks.dpws_single_worker_tasks.update_drug_inventory_task',
            task_args,
            retry=True
        )
        logger.debug(f"Task to call Elite API with params: {param} with task_id: {task_id}")

        return True
    except Exception as e:
        logger.error(e, exc_info=True)


@log_args_and_response
@validate(required_fields=["drug_id", "is_in_stock"])
def update_drug_status(args):
    try:
        drug_id_arg = args.get("drug_id")
        if not isinstance(drug_id_arg, list):
            drug_id_arg = [drug_id_arg]
        is_in_stock = args.get("is_in_stock")
        reason = args.get("reason")
        logger.debug("fetching token")
        user_id = args.get("user_id")
        device_id = args.get("device_id")
        company_id = args.get("company_id")
        system_id = args.get("system_id")
        token = args.get("token")
        user_confirmation = args.get("user_confirmation")
        data_dict = {}
        drugs_to_update = []
        exception_list = list()
        threads = list()
        update_inventory = None
        drug_data = get_all_same_drug_by_drug_id(drug_id_arg)

        txr_list = []
        formatted_ndc = []
        for k, r in drug_data.items():
            txr_list.append(r['txr'])
            formatted_ndc.append(r['formatted_ndc'])
        if not user_confirmation and not is_in_stock:
            inventory_data = get_fndc_txr_wise_inventory_qty(txr_list)
            for k, v in inventory_data.items():
                if k[0] in formatted_ndc:
                    return {"confirmation_req": True, "qty": v}
        if not user_id:
            if not token:
                token = get_token()
            logger.debug("fetching_user_details")
            user_details = get_current_user(token=token)
        else:
            args_info = {"token": token}
            user_details = get_users_by_ids(user_id_list=str(user_id), args_info=args_info)[str(user_id)]
            user_details['company_id'] = user_details['company']
            user_details['name'] = user_details['last_name'] + ", " + user_details['first_name']
        # Handle list of drug_ids
        for drug_id in drug_id_arg:
            status, update_inventory = update_drug_status_dao(drug_id, is_in_stock, user_details, reason)
            if update_inventory:
                drugs_to_update.append(drug_id)
            if is_in_stock:
                if system_id and device_id:
                    data_dict = {
                        'system_id': system_id,
                        'device_id': device_id,
                    }
                    logger.info(f"In update_drug_status, update replenish_mini_batch doc.")
        if data_dict:
            get_replenish_mini_batch_wise(data_dict)
        if update_inventory and is_in_stock:
            ndc_concatenated = get_all_same_ndc_by_drug_id(drug_id)
            param = {
                "ndcList": ndc_concatenated
            }
            t = ExcThread(exception_list, target=update_drug_inventory_for_same_drug_ndcs,
                          args=[param])
            threads.append(t)
            t.start()

        if settings.SEND_OUT_OF_STOCK_ALERT_TO_INVENTORY and not is_in_stock and drugs_to_update:
            drug_data = get_all_same_drug_by_drug_id(drugs_to_update)
            drug_list = list(drug_data.keys())
            ndc_list = [r['ndc'] for k, r in drug_data.items()]
            # # 1 get progress & partially filled packs
            robot_packs_qty = get_filled_drug_count_slot_transaction(drug_list)

            # 2 get mfd filled drug count
            mfd_drugs = get_mfd_filled_drug_count(drug_list)

            # 3 get partially filled packs
            partial_packs_qty = get_manual_partially_filled_packs_drug_count(drug_list)

            # 4 get canister filled quantity
            canister_qty = db_get_total_canister_quantity_by_drug_id(drug_list)
            # final_drug_count = {
            #     key: int(robot_packs_qty.get(key, 0)) + int(mfd_drugs.get(key, 0)) + int(partial_packs_qty.get(key, 0))
            #          + int(canister_qty.get(key, 0))
            #     for key in set(robot_packs_qty) | set(mfd_drugs) | set(partial_packs_qty) | set(canister_qty)
            # }
            final_drug_count = {}

            data_dicts = [robot_packs_qty, mfd_drugs, partial_packs_qty, canister_qty]
            for data_dict in data_dicts:
                for drug_id, quantity_data in data_dict.items():
                    for case_id, quantity in quantity_data.items():
                        final_drug_count.setdefault(drug_id, dict())
                        final_drug_count[drug_id][case_id] = int(
                            final_drug_count[drug_id].get(case_id, 0)) + quantity
                        final_drug_count[drug_id].setdefault('quantity', 0)
                        final_drug_count[drug_id]['quantity'] += quantity

            param = {
                "final_drug_count": final_drug_count,
                "ndc_list": ndc_list,
                "drug_data": drug_data,
                "company_id": user_details.get("company_id"),
                "transaction_type": settings.EPBM_QTY_ADJUSTMENT_KEY,
                "user_details": user_details,
                "note": reason
            }
            if settings.USE_CELERY_ELITE_CALL:
                status = add_task_elite(param)
            else:
                t = ExcThread(exception_list, target=update_drug_inventory_and_reorder_drugs,
                              args=[param])
                threads.append(t)
                t.start()
        return {"confirmation_req": False, "qty": 0}
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in update_drug_status: e".format(e))
        return error(1036)


@log_args_and_response
def update_drug_inventory_and_reorder_drugs(args):
    try:
        inventory_response = drug_inventory_adjustment(args)
        if inventory_response:
            # reordering drug with drug list
            ordering_args = {"company_id": args.get("company_id"),
                             "drug_list": args.get("ndc_list"),
                             "time_zone": settings.DEFAULT_TIME_ZONE,
                             "system_id_list": ['14']}
            # todo: remove this hard code
            check_and_update_drug_req(ordering_args)

    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in update_drug_status: e".format(e))
        return error(1036)


@validate(required_fields=["pack_id"])
@log_args_and_response
def verify_pack(args):
    try:
        pack_id = args.get('pack_id', None)
        valid_pack = verify_pack_id_by_system_id(pack_id)
        if not valid_pack:
            return error(1014)
        return create_response(True)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)


@validate(required_fields=['company_id', 'time_zone', 'system_id'])
@log_args_and_response
def get_packs_info(request_params):
    logger.info("Parameters for get_packs_info: {}"
                .format(request_params))
    company_id = request_params["company_id"]
    system_id = request_params.get("system_id", None)
    time_zone = request_params["time_zone"]
    filter_fields = request_params.get('filter_fields', None)
    paginate = request_params.get('paginate', None)
    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, 'Missing key(s) in paginate.')

    try:
        count, results = get_packs_info_dao(company_id=company_id,
                                            filter_fields=filter_fields,
                                            time_zone=time_zone,
                                            paginate=paginate)

        response = {"pack_list": list(results), "number_of_records": count}
        return create_response(response)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)


@log_args_and_response
def check_pharmacy_fill_id(pharmacy_fill_id):
    try:
        status = PackDetails.select().where(PackDetails.pack_display_id == pharmacy_fill_id).dicts()
        if status.exists():
            return False
        return True
    except (InternalError, IntegrityError) as e:
        logger.error("in check_pharmacy_fill_id error is", e)
        return error(2001)
    except Exception as e:
        logger.error("in check_pharmacy_fill_id error is", e)
        return error(2001)


@log_args_and_response
def update_prn_fill_details_in_ips(rx_id, ips_comm_settings, token, pack_ids, pack_send_data, is_ltc, bill_id, queue_id, is_partial):
    """
    this method is used for sending fill details after completely filling of PRN packs
    :return:
    """
    try:
        fill_details = db_get_prn_fill_details_dao(rx_id, pack_ids, pack_send_data, is_ltc, bill_id, queue_id, is_partial)
        send_data(base_url=ips_comm_settings['BASE_URL_IPS_WEB'].split("//")[1], webservice_url=settings.PRN_FILL_DETAILS,
                  parameters=fill_details, counter=0, request_type="POST", token=token, ips_api=True)
        return True
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("in update_prn_fill_details_in_ips error is", e, exc_info=True)
        raise RealTimeDBException
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error("in update_prn_fill_details_in_ips error is", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("in update_prn_fill_details_in_ips error is", e, exc_info=True)
        raise


@log_args_and_response
def reuse_pack(args):
    try:
        user_id = args["user_id"]
        company_id = args.get("company_id", None)
        reuse_pack_id = args.get("reuse_pack_id", None)
        similar_pack_ids = args.get("similar_pack_ids", None)

        if reuse_pack_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): reuse_pack_id or company_id.")

        if not similar_pack_ids:
            return error(1001, "Missing Parameter(s): similar_pack_ids")

        reuse_pack_id_data = db_get_pack_details_by_display_ids_dao([reuse_pack_id])
        for pack_id, pack_data in reuse_pack_id_data.items():
            reuse_pack_id = pack_id

        drug_tracker_insert_data = list()
        reuse_pack_drug_update_dict = {reuse_pack_id: dict()}

        # fetch the data for reusable pack
        reuse_pack_data = db_fetch_reuse_pack_data(reuse_pack_id, similar_pack_ids)

        if reuse_pack_data is None:
            return error(21015)

        if reuse_pack_data == 21016:
            return error(21016)

        # fetch the required drug data for current packs to be filled
        new_pack_data = db_fetch_similar_pack_data(similar_pack_ids)

        for record in new_pack_data:
            if record["filled_quantity"] is None:
                record["filled_quantity"] = 0
            if record["txr"] in reuse_pack_data[reuse_pack_id] and record["required_quantity"] > record["filled_quantity"]:
                required_quantity = record["required_quantity"] - record["filled_quantity"]
                reuse_allowed = False
                final_fndc = None

                if (record["formatted_ndc"]
                        in reuse_pack_data[reuse_pack_id][record["txr"]]
                        and reuse_pack_data[reuse_pack_id][record["txr"]][record["formatted_ndc"]]["available_quantity"] > 0):
                    final_fndc = record["formatted_ndc"]
                    reuse_allowed = True

                else:
                    if record["patient_id"] == reuse_pack_data[reuse_pack_id]["patient_id"]:
                        for fndc in reuse_pack_data[reuse_pack_id][record["txr"]].keys():
                            if fndc != "patient_id":
                                if reuse_pack_data[reuse_pack_id][record["txr"]][fndc]["available_quantity"] > 0:
                                    final_fndc = fndc
                                    reuse_allowed = True
                                    break

                    elif record["daw_code"] == 0:
                        if record["brand_flag"] == settings.GENERIC_FLAG:
                            for fndc in reuse_pack_data[reuse_pack_id][record["txr"]].keys():
                                if fndc != "patient_id":
                                    if (reuse_pack_data[reuse_pack_id][record["txr"]][fndc]["brand_flag"]
                                            == settings.GENERIC_FLAG
                                            and reuse_pack_data[reuse_pack_id][record["txr"]][fndc]["available_quantity"] > 0):
                                        final_fndc = fndc
                                        reuse_allowed = True
                                        break

                if reuse_allowed:
                    drug_tracker_info = {"canister_id": None,
                                         "drug_id": reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["drug_id"],
                                         "canister_tracker_id": None,
                                         "comp_canister_tracker_id": None,
                                         "drug_lot_master_id": None,
                                         "filled_at": settings.FILLED_AT_PACK_FILL_WORKFLOW,
                                         "created_by": user_id,
                                         "is_overwrite": 0,
                                         "pack_id": record["pack_id"],
                                         "drug_quantity": required_quantity if float(required_quantity) < float(
                                             reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc][
                                                 "available_quantity"]) else reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["available_quantity"],
                                         "slot_id": record["slot_details_id"],
                                         "scan_type": constants.REUSE_PACK_SCAN,
                                         "case_id": reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["item_id"],
                                         "reuse_pack": reuse_pack_id,
                                         "expiry_date": reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["expiry_date"],
                                         "lot_number": reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["lot_number"]
                                         }

                    reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["available_quantity"] -= (
                        float(drug_tracker_info["drug_quantity"]))

                    if (reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["drug_id"]
                            not in reuse_pack_drug_update_dict):
                        reuse_pack_drug_update_dict[reuse_pack_id][
                            reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["drug_id"]] = dict()

                    reuse_pack_drug_update_dict[reuse_pack_id][
                        reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["drug_id"]]["available_quantity"] = (
                        reuse_pack_data)[reuse_pack_id][record["txr"]][final_fndc]["available_quantity"]

                    if reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["available_quantity"] == 0:
                        reuse_pack_drug_update_dict[reuse_pack_id][
                            reuse_pack_data[reuse_pack_id][record["txr"]][final_fndc]["drug_id"]][
                            "status_id"] = constants.REUSE_DRUG_STATUS_DRUG_REUSE_DONE_ID

                    drug_tracker_insert_data.append(drug_tracker_info)

        logger.info("In reuse_pack: drug_tracker_insert_data: {}".format(drug_tracker_insert_data))
        logger.info("In reuse_pack: reuse_pack_drug_update_dict: {}".format(reuse_pack_drug_update_dict))

        if drug_tracker_insert_data:
            drug_tracker_status = drug_tracker_create_multiple_record(drug_tracker_insert_data)
            logger.info("In reuse_pack: drug_tracker_status: {}".format(drug_tracker_status))

        for pack_id, pack_data in reuse_pack_drug_update_dict.items():
            pack_reuse_in_progress = None
            if pack_data:
                pack_reuse_in_progress = True
            else:
                return error(21016)

            for drug_id, update_dict in pack_data.items():
                update_dict["modified_date"] = get_current_date_time()
                status = db_update_reuse_pack_drug_by_pack_id_drug_id_dao(pack_id, drug_id, update_dict)

            pack_reuse_done = True
            reuse_pack_drug_data = db_get_reuse_pack_drug_data_by_pack_id_dao([pack_id])
            for record in reuse_pack_drug_data:
                if record["status_id"] != constants.REUSE_DRUG_STATUS_DRUG_REUSE_DONE_ID:
                    pack_reuse_done = False

                if record["status_id"] not in [constants.REUSE_DRUG_STATUS_DRUG_REUSE_DONE_ID,
                                               constants.REUSE_DRUG_STATUS_DRUG_RTS_DONE_ID,
                                               constants.REUSE_DRUG_STATUS_DRUG_DISCARDED_ID]:
                    update_dict = {"modified_date": get_current_date_time(),
                                   "status_id": constants.REUSE_DRUG_STATUS_DRUG_REUSE_IN_PROGRESS_ID}
                    status = db_update_reuse_pack_drug_by_pack_id_drug_id_dao(pack_id, record["drug_id"], update_dict)

            if pack_reuse_done:
                update_status = db_update_ext_pack_details_by_pack_id_dao([pack_id],
                                                                          {
                                                                              "pack_usage_status_id": constants.EXT_PACK_USAGE_STATUS_DONE_ID,
                                                                              "ext_modified_date": get_current_date_time()})
                logger.info("In reuse_pack: pack_update_status: {}".format(update_status))
            elif pack_reuse_in_progress:
                update_status = db_update_ext_pack_details_by_pack_id_dao([pack_id],
                                                                          {
                                                                              "pack_usage_status_id": constants.EXT_PACK_USAGE_STATUS_PROGRESS_ID,
                                                                              "ext_modified_date": get_current_date_time()})
                logger.info("In reuse_pack: pack_update_status: {}".format(update_status))

        return create_response(True)
    except Exception as e:
        logger.error("In reuse_pack_dao: {}".format(e))
        return error(2001)


@log_args_and_response
def recommend_reuse_pack(args):
    try:
        user_id = args["user_id"]
        company_id = args.get("company_id", None)
        current_pack_ids = args.get("current_pack_ids", None)

        if current_pack_ids is None or company_id is None:
            return error(1001, "Missing Parameter(s): current_pack_ids or company_id.")

        # check that current packs to filled packs are change rx packs or not also fetch the patient_id
        is_change_rx, patient_id = db_check_packs_are_change_rx_or_not(current_pack_ids)

        reusable_packs_dict, asrs_dict = (
            db_fetch_reusable_packs(current_pack_ids, patient_id, company_id, is_change_rx))

        response = {"reusable_packs_dict": reusable_packs_dict,
                    "asrs_dict": asrs_dict
                    }

        return create_response(response)

    except Exception as e:
        logger.error("Error in recommend_reuse_pack: {}".format(e))
        return error(2001)


@log_args_and_response
def discard_pack_drug(discard_data):
    try:
        with db.transaction():
            if discard_data is None:
                return error(1001, "Missing Parameter(s): discard_data.")

            expired_drug_response = None
            system_id = discard_data["system_id"]
            company_id = discard_data["company_id"]
            discard_data = discard_data["discard_data"]

            for pack_id, pack_data in discard_data.items():
                if settings.DISCARDED_REUSE_PACK:
                    status = db_discard_pack_in_ext_pack_details_and_reuse_pack_drug(pack_id)
                    logger.info("In discard_pack_drug: discard_pack_status: {}".format(status))

                expiry_list = list()
                for drug_id, drug_data in pack_data["drug_list"].items():
                    if not settings.DISCARDED_REUSE_PACK:
                        status = db_discard_reuse_drug_in_reuse_pack_drug(pack_id, drug_id)
                        logger.info("In discard_pack_drug: discard_drug_status: {}".format(status))

                    expiry_dict = {"ndc": drug_data["ndc"],
                                   "trash_qty": drug_data["quantity"],
                                   "lot_number": drug_data["lot_number"],
                                   "expiry_date": drug_data["expiry_date"],
                                   "case_id": drug_data["item_id"]
                                   }
                    expiry_list.append(expiry_dict)

                user_details = get_users_by_ids(user_id_list=str(pack_data["user_id"]))[str(pack_data["user_id"])]
                user_details['company_id'] = user_details['company']
                user_details['name'] = user_details['last_name'] + ", " + user_details['first_name']

                expired_drug_dict = {"user_details": user_details,
                                     "transaction_type": settings.EPBM_EXPIRY,
                                     "expiry_list": expiry_list}

                logger.info("In discard_pack_drug: expired_drug_dict: {}".format(expired_drug_dict))
                logger.info("In discard_pack_drug: sending call to elite for discard the drug****")
                expired_drug_response = drug_inventory_adjustment(expired_drug_dict)
                logger.info("In discard_pack_drug: expired_drug_response: {}".format(expired_drug_response))

            return create_response(expired_drug_response)
    except Exception as e:
        logger.error("Error in discard_pack_drug: {}".format(e))
        return error(2001)


@log_args_and_response
def reseal_pack(args):
    try:
        with db.transaction():
            user_id = args["user_id"]
            system_id = args["system_id"]
            company_id = args["company_id"]
            reseal_pack_data = args["reseal_data"]

            if reseal_pack_data:
                resealed_pack_update_dict = dict()

                for pack_id, pack_data in reseal_pack_data.items():

                    drug_data = db_get_reuse_pack_drug_data_by_pack_id_dao([pack_id])
                    logger.info("In resealed_pack: drug_data: {}".format(drug_data))

                    for record in drug_data:
                        if (str(record["drug_id"]) in pack_data
                                and record["status_id"] in [constants.REUSE_DRUG_STATUS_DRUG_REUSE_PENDING_ID,
                                                            constants.REUSE_DRUG_STATUS_DRUG_REUSE_IN_PROGRESS_ID]):
                            if pack_id not in resealed_pack_update_dict:
                                resealed_pack_update_dict[pack_id] = dict()

                            if record["drug_id"] not in resealed_pack_update_dict[pack_id]:
                                resealed_pack_update_dict[pack_id][record["drug_id"]] = dict()
                                resealed_pack_update_dict[pack_id][record["drug_id"]]["status_id"] = (
                                    constants.REUSE_DRUG_STATUS_DRUG_RESEALED_ID)
                                resealed_pack_update_dict[pack_id][record["drug_id"]]["available_quantity"] = (
                                    pack_data)[str(record["drug_id"])]["available_quantity"]
                                # if pack_data[str(record["drug_id"])]["reason"]:
                                #     resealed_pack_update_dict[pack_id][record["drug_id"]]["reason"] = ", ".join(
                                #         pack_data[str(record["drug_id"])]["reason"])

                            ndc_query = db_get_drug_master_data_by_drug_id_dao(record["drug_id"])
                            ndc = None
                            for data in ndc_query:
                                ndc = data["ndc"]

                            if pack_data[str(record["drug_id"])]["reason"]:
                                if pack_data[str(record["drug_id"])]["total_quantity"] > pack_data[str(record["drug_id"])]["available_quantity"]:
                                    diff = pack_data[str(record["drug_id"])]["total_quantity"] - pack_data[str(record["drug_id"])]["available_quantity"]
                                    quantity_adjustment_args = {"user_id": user_id,
                                                                "ndc": ndc,
                                                                "adjusted_quantity": diff,
                                                                "company_id": company_id,
                                                                "case_id": record["item_id"],
                                                                "reason": ",".join(pack_data[str(record["drug_id"])]["reason"]),
                                                                "transaction_type": settings.EPBM_DRUG_ADJUSTMENT_DECREMENT
                                                                }
                                    logger.info("In reseal_pack: quantity_adjustment_args: {}".format(quantity_adjustment_args))
                                    logger.info(
                                        "In reseal_pack: sending data to elite for EPBM_DRUG_ADJUSTMENT_DECREMENT******")
                                    adjust_quantity_response = inventory_adjust_quantity(quantity_adjustment_args)
                                    logger.info("In reseal_pack: adjust_quantity_response: {}".format(adjust_quantity_response))

                                elif pack_data[str(record["drug_id"])]["total_quantity"] < pack_data[str(record["drug_id"])]["available_quantity"]:
                                    diff = pack_data[str(record["drug_id"])]["available_quantity"] - pack_data[str(record["drug_id"])]["total_quantity"]
                                    quantity_adjustment_args = {"user_id": user_id,
                                                                "ndc": ndc,
                                                                "adjusted_quantity": diff,
                                                                "company_id": company_id,
                                                                "case_id": record["item_id"],
                                                                "reason": ",".join(pack_data[str(record["drug_id"])]["reason"]),
                                                                "transaction_type": settings.EPBM_DRUG_ADJUSTMENT_INCREMENT
                                                                }
                                    logger.info("In reseal_pack: quantity_adjustment_args: {}".format(quantity_adjustment_args))
                                    logger.info(
                                        "In reseal_pack: sending data to elite for EPBM_DRUG_ADJUSTMENT_DECREMENT******")
                                    adjust_quantity_response = inventory_adjust_quantity(quantity_adjustment_args)
                                    logger.info("In reseal_pack: adjust_quantity_response: {}".format(adjust_quantity_response))

                logger.info("In resealed_pack: resealed_pack_update_dict: {}".format(resealed_pack_update_dict))

                for pack_id, pack_data in resealed_pack_update_dict.items():

                    update_pack_status = (
                        db_update_ext_pack_details_by_pack_id_dao([pack_id],
                                                                 {
                                                                     "pack_usage_status_id": constants.EXT_PACK_USAGE_STATUS_PACK_RESEALED_ID,
                                                                     "ext_modified_date": get_current_date_time()}))

                    for drug_id, update_dict in pack_data.items():
                        update_dict["modified_date"] = get_current_date_time()
                        status = db_update_reuse_pack_drug_by_pack_id_drug_id_dao(pack_id, drug_id, update_dict)
            else:
                return error(1001, "Missing Parameter(s): reseal_pack_data")
            return create_response(True)

    except Exception as e:
        logger.error("Error in resealed_pack: {}".format(e))
        return error(2001)


@log_args_and_response
def get_reuse_in_progress_pack(current_pack_ids):
    try:
        temp_pack_list = list()
        reuse_in_progress_packs = list()
        reuse_in_progress_pack_query = get_reuse_in_progress_pack_dao(eval(current_pack_ids))

        for record in reuse_in_progress_pack_query:
            if record["reuse_pack"] not in temp_pack_list:
                temp_dict = dict()
                temp_dict["pack_id"] = record["reuse_pack"]
                temp_dict["pack_display_id"] = record["pack_display_id"]
                temp_dict["packs_delivery_status"] = record["packs_delivery_status"]
                temp_pack_list.append(record["reuse_pack"])
                reuse_in_progress_packs.append(temp_dict)

        return create_response(reuse_in_progress_packs)

    except Exception as e:
        logger.error("Error in get_reuse_in_progress_pack: {}".format(e))
        return error(2001)


@log_args_and_response
def get_reuse_pack_drug_data(pack_ids, company_id):
    try:
        reuse_pack_drug_data = dict()

        reuse_pack_drug_data_query = get_reuse_pack_drug_data_dao(pack_ids)

        for record in reuse_pack_drug_data_query:
            if record["pack_id"] not in reuse_pack_drug_data:
                reuse_pack_drug_data[record["pack_id"]] = dict()
                reuse_pack_drug_data[record["pack_id"]]["drug_list"] = list()
                reuse_pack_drug_data[record["pack_id"]]["pack_display_id"] = record["pack_display_id"]
                # reuse_pack_drug_data[record["pack_id"]]["lot_number"] = record["lot_number"]
                reuse_pack_drug_data[record["pack_id"]]["expiry_flag"] = settings.DISCARDED_REUSE_PACK

            if record["available_quantity"] > 0:
                inventory_data = get_current_inventory_data(ndc_list=[int(record["ndc"])], qty_greater_than_zero=False)
                logger.info(
                    "get_reuse_pack_drug_data: inventory_data: {} for ndc: {}".format(inventory_data, record["ndc"]))
                is_in_stock = None
                if inventory_data:
                    is_in_stock = 1 if inventory_data[0]["quantity"] > 0 else 0
                temp_dict = {"ndc": record["ndc"],
                             "item_id": record["item_id"],
                             "color": record["color"],
                             "drug_id": record["drug_id"],
                             "shape": record["shape"],
                             "strength": record["strength"],
                             "drug_name": record["drug_name"],
                             "imprint": record["imprint"],
                             "strength_value": record["strength_value"],
                             "image_name": record["image_name"],
                             "total_quantity": record["total_quantity"],
                             "available_quantity": record["available_quantity"],
                             "expiry_date": str(datetime.datetime.strptime(record["expiry_date"], "%m-%Y").date()),
                             "manufacturer": record["manufacturer"],
                             "adjusted_full_quantity": 0,
                             "adjusted_half_quantity": 0,
                             "lot_number": record["lot_number"],
                             "last_seen_with": record.get("last_seen_by", None),
                             "is_in_stock": is_in_stock
                             }

                expiry = datetime.datetime.strptime(record["expiry_date"], "%m-%Y").date()
                expiry = last_day_of_month(expiry)
                if expiry > datetime.datetime.today().date():
                    temp_dict["is_expired"] = 0
                else:
                    temp_dict["is_expired"] = 1

                if record["total_quantity"] == record["available_quantity"]:

                    adjusted_quantity = db_get_pack_drug_adjusted_quantity(record["pack_id"], record["fndc_txr"])

                    for data in adjusted_quantity:
                        if data["mfd_status"]:
                            mfd_status_list = data["mfd_status"].split(",")
                            if (str(constants.MFD_DRUG_DROPPED_STATUS)
                                    in mfd_status_list or str(constants.MFD_DRUG_MVS_FILLED) in mfd_status_list):
                                if float(data["mfd_quantity"]).is_integer():
                                    temp_dict["adjusted_full_quantity"] += float(data["mfd_quantity"])
                                else:
                                    if data["drug_quantity"] == 0.50:
                                        temp_dict["adjusted_half_quantity"] += float(1)
                                    else:
                                        temp_dict["adjusted_full_quantity"] += (float(data["mfd_quantity"]) - 0.50)
                                        temp_dict["adjusted_half_quantity"] += float(1)
                        else:
                            if float(data["drug_quantity"]).is_integer():
                                temp_dict["adjusted_full_quantity"] += float(data["drug_quantity"])
                            else:
                                if data["drug_quantity"] == 0.50:
                                    temp_dict["adjusted_half_quantity"] += float(1)
                                else:
                                    temp_dict["adjusted_full_quantity"] += (float(data["drug_quantity"]) - 0.50)
                                    temp_dict["adjusted_half_quantity"] += float(1)
                else:
                    if record["available_quantity"] > 0:
                        if float(record["available_quantity"]).is_integer():
                            temp_dict["adjusted_full_quantity"] = float(record["available_quantity"])
                            temp_dict["adjusted_half_quantity"] = 0
                        else:
                            temp_dict["adjusted_full_quantity"] = int(record["available_quantity"])
                            temp_dict["adjusted_half_quantity"] = 1

                reuse_pack_drug_data[record["pack_id"]]["drug_list"].append(temp_dict)

        return create_response(reuse_pack_drug_data)

    except Exception as e:
        logger.error("Error in get_reuse_pack_drug_data: {}".format(e))
        return error(2001)


@log_args_and_response
def rts_of_pack(args):
    try:
        with db.transaction():
            company_id = args["company_id"]
            system_id = args["system_id"]
            rts_data = args["rts_data"]

            lot_details = []
            pack_grid_ids = []
            vial_label = None
            inventory_resp = None
            vial_label_list = list()
            rts_pack_update_dict = dict()
            rts_of_pack_dict = {"created": list()}
            rts_flag = bool(int(get_company_setting_by_company_id(company_id).get("USE_RTS_FLOW", 0)))


            # fetching itemid for fill error RTS case
            if args.get('fill_error_flag'):
                for pack_id, pack_data in rts_data.items():
                    drug_data = pack_data['drug_list']
                    for drug_id, data in drug_data.items():
                        available_qty = sum(float(value) for value in data["fill_error_data"].values())
                        reduce_qty = available_qty
                        if data.get("fill_error_data"):
                            pack_grid_map = data["fill_error_data"].copy()
                            for key, value in data["fill_error_data"].items():
                                if available_qty > 0:
                                    if value <= available_qty:
                                        pack_grid_map[key] = value
                                        available_qty -= value
                                    else:
                                        pack_grid_map[key] = available_qty
                                        available_qty = 0
                                else:
                                    pack_grid_map[key] = 0
                            pack_grid_map = {key: value for key, value in pack_grid_map.items() if value != 0}
                            status = db_update_drug_tracker_qty(drug_id=drug_id, qty=reduce_qty,
                                                                pack_id=pack_id, pack_grid_map=pack_grid_map)
                            lot_details, source_details = db_get_lot_details_by_slot_id(
                                pack_grid_ids=list(pack_grid_map.keys()), pack_id=pack_id,
                                drug_id=drug_id)
                        created_dict = {"created": [{"department": "dosepack",
                                                     "ndc": data['ndc'],
                                                     "lot": "P" + str(pack_data['pack_display_id']) + "N1" if len(
                                                         source_details) > 1 else source_details[0].get("lotNo"),
                                                     "exp": data['expiry_date'],
                                                     "qty": data['available_quantity'],
                                                     "create": settings.ITEM,
                                                     "sourceItems": source_details,
                                                     "packId": pack_data['pack_display_id'],
                                                     "adjustmentDate": convert_utc_timezone_into_local_time_zone(),
                                                     "packType": settings.FULL_PILL_VIAL,
                                                     "userId": pack_data["user_id"],
                                                     "lotDetails": lot_details,
                                                     "packInProgress": False,
                                                     "isFillError": True
                                                     }]}
                        try:
                            if settings.USE_EPBM and rts_flag:
                                response = create_item_vial_generation_for_rts_reuse_pack(created_dict)
                                rts_data[pack_id]['drug_list'][drug_id]['item_id'] = response['created'][0]['ItemId']
                        except Exception as e:
                            logger.error("Error in rts_of_pack while fill error case: {}".format(e))
                            raise e
            if settings.USE_EPBM and rts_flag:
                for pack_id, pack_data in rts_data.items():
                    pack_display_id = pack_data["pack_display_id"]
                    rts_pack_update_dict[pack_display_id] = dict()
                    for drug_id, drug_data in pack_data["drug_list"].items():
                        rts_pack_update_dict[pack_display_id][drug_data["ndc"]] = dict()

                        if drug_data["adjusted_full_quantity"] > 0:
                            temp_dict = {
                                "department": "dosepack",
                                "ndc": drug_data["ndc"],
                                "lot": drug_data["lot_number"],
                                "exp": drug_data["expiry_date"],
                                "qty": drug_data["adjusted_full_quantity"],
                                "create": settings.FULL_PILL_VIAL,
                                "sourceItems": [
                                    {
                                        "lotNo": drug_data["lot_number"],
                                        "expirationDate": drug_data["expiry_date"],
                                        "caseId": drug_data["item_id"],
                                        "quantity": drug_data["adjusted_full_quantity"],
                                        "filledByCanister": False
                                    }
                                ],
                                "packId": pack_display_id,
                                "userId": pack_data["user_id"],
                                "adjustmentDate": convert_utc_timezone_into_local_time_zone(),
                                "packType": settings.FULL_PILL_VIAL
                            }
                            rts_of_pack_dict["created"].append(temp_dict)

                            rts_pack_update_dict[pack_display_id][drug_data["ndc"]][
                                settings.FULL_PILL_VIAL] = {"ndc": drug_data["ndc"],
                                                            "color": drug_data["color"],
                                                            "drug_name": drug_data["drug_name"],
                                                            "manufacturer": drug_data["manufacturer"],
                                                            "drug_id": drug_id,
                                                            "lot_number": drug_data["lot_number"],
                                                            "expiry_date": drug_data["expiry_date"],
                                                            "quantity": drug_data["adjusted_full_quantity"],
                                                            "item_id": None,
                                                            "pack_id": pack_id,
                                                            "imprint": drug_data["imprint"],
                                                            "pack_display_id": pack_display_id,
                                                            "status": constants.REUSE_DRUG_STATUS_DRUG_RTS_DONE_ID,
                                                            "available_quantity": drug_data["available_quantity"]
                                                            }

                        if drug_data["adjusted_half_quantity"] > 0:
                            temp_dict = {
                                "department": "dosepack",
                                "ndc": drug_data["ndc"],
                                "lot": drug_data["lot_number"],
                                "exp": drug_data["expiry_date"],
                                "qty": drug_data["adjusted_half_quantity"],
                                "create": settings.HALF_PILL_VIAL,
                                "sourceItems": [
                                    {
                                        "lotNo": drug_data["lot_number"],
                                        "expirationDate": drug_data["expiry_date"],
                                        "caseId": drug_data["item_id"],
                                        "quantity": drug_data["adjusted_half_quantity"],
                                        "filledByCanister": False
                                    }
                                ],
                                "packId": pack_display_id,
                                "userId": pack_data["user_id"],
                                "adjustmentDate": convert_utc_timezone_into_local_time_zone(),
                                "packType": settings.HALF_PILL_VIAL
                            }
                            rts_of_pack_dict["created"].append(temp_dict)

                            rts_pack_update_dict[pack_display_id][drug_data["ndc"]][
                                settings.HALF_PILL_VIAL] = {"ndc": drug_data["ndc"],
                                                            "color": drug_data["color"],
                                                            "drug_name": drug_data["drug_name"],
                                                            "manufacturer": drug_data["manufacturer"],
                                                            "drug_id": drug_id,
                                                            "lot_number": drug_data["lot_number"],
                                                            "expiry_date": drug_data["expiry_date"],
                                                            "quantity": (drug_data["adjusted_half_quantity"]/2),
                                                            "item_id": None,
                                                            "pack_id": pack_id,
                                                            "imprint": drug_data["imprint"],
                                                            "pack_display_id": pack_display_id,
                                                            "status": constants.REUSE_DRUG_STATUS_DRUG_RTS_DONE_ID,
                                                            "available_quantity": drug_data["available_quantity"]
                                                            }

                        if drug_data["reason"]:
                            if drug_data["total_quantity"] > drug_data["available_quantity"]:
                                if drug_data["available_quantity"] == 0:
                                    if len(pack_data["drug_list"]) == 1:
                                        update_pack_status = (
                                            db_update_ext_pack_details_by_pack_id_dao([pack_id],
                                                                                      {
                                                                                          "pack_usage_status_id": constants.EXT_PACK_USAGE_STATUS_RTS_DONE_ID,
                                                                                          "ext_modified_date": get_current_date_time()}))

                                    update_dict = {"status_id": constants.REUSE_DRUG_STATUS_DRUG_RTS_DONE_ID,
                                                   "available_quantity": drug_data["available_quantity"],
                                                   "modified_date": get_current_date_time()
                                                   }

                                    status = db_update_reuse_pack_drug_by_pack_id_drug_id_dao(pack_id,
                                                                                              drug_id,
                                                                                              update_dict)

                                diff = drug_data["total_quantity"] - drug_data["available_quantity"]
                                quantity_adjustment_args = {"user_id": pack_data["user_id"],
                                                            "ndc": drug_data["ndc"],
                                                            "adjusted_quantity": diff,
                                                            "company_id": company_id,
                                                            "case_id": drug_data["item_id"],
                                                            "reason": ",".join(drug_data["reason"]),
                                                            "transaction_type": settings.EPBM_DRUG_ADJUSTMENT_DECREMENT
                                                            }

                                logger.info("In rts_of_pack: quantity_adjustment_args: {}".format(quantity_adjustment_args))
                                logger.info("In rts_of_pack: sending data to elite for EPBM_DRUG_ADJUSTMENT_DECREMENT******")
                                adjust_quantity_response = inventory_adjust_quantity(quantity_adjustment_args)
                                logger.info("In rts_of_pack: adjust_quantity_response: {}".format(adjust_quantity_response))

                            elif drug_data["total_quantity"] < drug_data["available_quantity"]:
                                diff = drug_data["available_quantity"] - drug_data["total_quantity"]
                                quantity_adjustment_args = {"user_id": pack_data["user_id"],
                                                            "ndc": drug_data["ndc"],
                                                            "adjusted_quantity": diff,
                                                            "company_id": company_id,
                                                            "case_id": drug_data["item_id"],
                                                            "reason": ",".join(drug_data["reason"]),
                                                            "transaction_type": settings.EPBM_DRUG_ADJUSTMENT_INCREMENT
                                                            }
                                logger.info("In rts_of_pack: quantity_adjustment_args: {}".format(quantity_adjustment_args))
                                logger.info("In rts_of_pack: sending data to elite for EPBM_DRUG_ADJUSTMENT_INCREMENT ****")
                                adjust_quantity_response = inventory_adjust_quantity(quantity_adjustment_args)
                                logger.info("In rts_of_pack: adjust_quantity_response: {}".format(adjust_quantity_response))

                logger.info("In rts_of_pack: rts_of_pack_list: {}".format(rts_of_pack_dict))
                logger.info("In rts_of_pack: rts_pack_update_dict: {}".format(rts_pack_update_dict))
                logger.info("In rts_of_pack: sending data to elite for vial_generation ******")

                if rts_of_pack_dict["created"]:
                    inventory_resp = create_item_vial_generation_for_rts_reuse_pack(rts_of_pack_dict)
                if inventory_resp:
                    for record in inventory_resp["created"]:
                        pack_id = rts_pack_update_dict[int(record["PackId"])][record["Ndc"]][record["vialType"]]["pack_id"]

                        update_pack_status = (
                            db_update_ext_pack_details_by_pack_id_dao([pack_id],
                                                                     {
                                                                         "pack_usage_status_id": constants.EXT_PACK_USAGE_STATUS_RTS_DONE_ID,
                                                                         "ext_modified_date": get_current_date_time()}))

                        update_dict = {"status_id": rts_pack_update_dict[int(record["PackId"])][record["Ndc"]][record["vialType"]]["status"],
                                       "available_quantity": rts_pack_update_dict[int(record["PackId"])][record["Ndc"]][record["vialType"]]["available_quantity"],
                                       "modified_date": get_current_date_time()
                                       }

                        if record["vialType"] == settings.FULL_PILL_VIAL:
                            rts_pack_update_dict[int(record["PackId"])][record["Ndc"]][settings.FULL_PILL_VIAL]["vial_id"] = record[
                                "VialId"]
                            rts_pack_update_dict[int(record["PackId"])][record["Ndc"]][settings.FULL_PILL_VIAL]["item_id"] = record[
                                "ItemId"]
                        elif record["vialType"] == settings.HALF_PILL_VIAL:
                            rts_pack_update_dict[int(record["PackId"])][record["Ndc"]][settings.HALF_PILL_VIAL]["vial_id"] = record[
                                "VialId"]
                            rts_pack_update_dict[int(record["PackId"])][record["Ndc"]][settings.HALF_PILL_VIAL]["item_id"] = record[
                                "ItemId"]

                        status = db_update_reuse_pack_drug_by_pack_id_drug_id_dao(pack_id,
                                                                                  rts_pack_update_dict[int(record["PackId"])][
                                                                                      record["Ndc"]][record["vialType"]][
                                                                                      "drug_id"],
                                                                                  update_dict)

                        vial_details = rts_pack_update_dict[int(record["PackId"])][record["Ndc"]][record["vialType"]]
                        vial_label_list.append(vial_details)

                    vial_label_args = {"company_id": company_id,
                                       "system_id": system_id,
                                       "vial_details": vial_label_list}
                    vial_label = get_vial_label(vial_label_args)

                    return create_response(vial_label)
                else:
                    return create_response(None)
            return create_response(settings.SUCCESS_RESPONSE)
    except Exception as e:
        logger.error("Error in rts_of_pack: {}".format(e))
        return error(2001)


@log_args_and_response
def get_vial_label(vial_label_args):
    company_id = vial_label_args["company_id"]
    system_id = vial_label_args["system_id"]
    vial_details = vial_label_args["vial_details"]

    if len(vial_details) > 1:
        vial_id_list = [str(i["vial_id"]) for i in vial_details]
        vial_ids = ",".join(vial_id_list)
        vial_label_name = "multi_vial_label_" + vial_ids + ".pdf"
    else:
        vial_id = vial_details[0]["vial_id"]
        vial_label_name = str(vial_id) + '.pdf'

        try:
            if blob_exists(vial_label_name, vial_label_dir):
                logger.info("vial_label: {} already exist on cloud".format(vial_label_name))
                response = {"vial_label_name": vial_label_name}
                return response

        except Exception as e:
            logger.error("Error in checking vial_label on cloud: {}".format(e))
            return error(2001)

    vial_dir = os.path.join("vial_labels")

    if not os.path.exists(vial_dir):
        os.makedirs(vial_dir)
    vial_label_path = os.path.join(vial_dir, vial_label_name)

    try:
        generate_vial_label(vial_details, vial_label_path)
        create_blob(vial_label_path, vial_label_name, vial_label_dir)

        logger.info("vial_label generated successfully with name: {}".format(vial_label_name))
        response = {"vial_label_name": vial_label_name}

        return response
    except Exception as e:
        logger.error("Error in get_vial_label: {}".format(e))
    finally:
        remove_files([vial_label_path])


@log_args_and_response
def epbm_general_api(args, query_string_parameter, api_name, api_type):
    try:
        logger.info("In epbm_general_api: sending data for elite****")
        response = drug_inventory_general_api(args, query_string_parameter, api_name, api_type)

        return create_response(response)
    except Exception as e:
        logger.error("Error in epbm_general_api: {}".format(e))
        return error(2001)


@log_args_and_response
def get_vial_list(args):
    try:
        vial_list = dict()
        final_response = dict()
        system_id = args["system_id"]
        company_id = args["company_id"]
        patient_ndc_data = args.get("patient_ndc_data", None)
        pharmacy_patient_ndc_data = args.get("pharmacy_patient_ndc_data", None)

        final_ndc_dict = None
        final_ndc_list = None
        if pharmacy_patient_ndc_data:
            for patient, ndc_list in pharmacy_patient_ndc_data.items():
                for ndc in ndc_list:
                    vial_list[int(ndc)] = list()

            final_ndc_dict, final_ndc_list = get_ndc_list_for_vial_list_for_prn_screen(
                ndc_data=pharmacy_patient_ndc_data)

        elif patient_ndc_data:
            for patient, ndc_list in patient_ndc_data.items():
                for ndc in ndc_list:
                    vial_list[int(ndc)] = list()

            final_ndc_dict, final_ndc_list = get_ndc_list_for_vial_list_for_filling_screen(ndc_data=patient_ndc_data)

        parameters = {'ndc': final_ndc_list,
                      'packType': [settings.FULL_PILL_VIAL, settings.HALF_PILL_VIAL]
                      }

        logger.info("In get_vial_list: sending call to elite for getting vial list*******")
        response = drug_inventory_general_api(param=parameters,
                                              query_string_parameter={"page": 1, "size": 99999},
                                              api_name=settings.DRUG_INVENTORY_GET_VIALS_DATA,
                                              api_type="POST")

        for record in response[0]["vialData"]:
            if record["ndc"] in final_ndc_dict:
                ndc_from_response = str(record["ndc"])
                original_ndc = str(final_ndc_dict[record["ndc"]])

                # to show the alternate drug vial
                if ndc_from_response == original_ndc or ndc_from_response[:-2] == original_ndc[:-2]:
                    record["is_alternate"] = 0
                else:
                    record["is_alternate"] = 1

                vial_list[final_ndc_dict[record["ndc"]]].append(record)

        final_response["vial_scan_required"] = settings.VIAL_SCAN_REQUIRED
        final_response["vial_list"] = vial_list

        return create_response(final_response)

    except Exception as e:
        logger.error("Error in get_vial_list: {}".format(e))
        return error(2001)



@log_args_and_response
def master_search(company_id, filters, sort_fields, paginate):


    try:
        search_result, count = db_master_search_dao(company_id, filters, sort_fields, paginate)

        response_data = {"result_data": search_result,
                         "count": count
                         }

        return create_response(response_data)
    except Exception as e:
        logger.error("error in master search ", e)
        raise e


@log_args_and_response
def person_master_search(company_id, filters, sort_fields, paginate):
    try:
        if filters:
            filters = {"global_search": filters}
            search_result, count = db_person_master_search_dao(company_id, filters, sort_fields, paginate)

            response_data = {"result_data": search_result,
                             "count": count
                             }

            return create_response(response_data)
        else:
            response_data = {"result_data": [],
                             "count": 0
                             }

            return create_response(response_data)

    except Exception as e:
        logger.error("error in master search ", e)
        raise e
