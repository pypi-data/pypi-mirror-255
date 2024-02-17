import csv
import itertools
import json
import os
import sys
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import pytz
from peewee import InternalError, IntegrityError

import settings
from canister_transfer_workflow_efficiency import CanisterTransferWorkflowEfficiency
from dosepack.utilities.utils import log_args_and_response, get_utc_time_offset_by_time_zone
from drug_replenish_workflow_efficiency import DrugReplenishWorkflowEfficiency
from mfd_canister_transfer_workflow_efficiency import MFDCanisterTransferWorkflowEfficiency
from robot_processing_workflow_efficiency import RobotProcessingWorkflowEfficiency
from src.dao.data_analysis_dao import get_packs_partially_filled_by_robot, \
    get_slots_filled_by_robot_canister, get_slots_filled_by_mfd_canister, get_pack_fill_workflow_drops, \
    get_robot_drops_skipped_filled_manually, get_mfd_drops, get_mfd_drops_skipped_filled_manually, get_robot_drops, \
    get_top_5_manual_drugs_without_drug_dimensions, get_packs_processed_today, get_pack_count_with_error, \
    get_batch_in_progress_today, \
    get_mfd_data, get_manual_drugs_for_imported_batch_db, db_get_ndc_list_last_3_months_usage, \
    get_sensor_dropping_data, get_pack_id_and_slot_number, get_pills_with_width_length_slot_wise, \
    get_sensor_dropping_data_for_success_sensor_drug_drop, get_pvs_dropping_data, get_drug_data_of_error_slot, \
    get_location_data_of_error_slot, get_sensor_dropping_data_for_pvs_classification, get_pvs_slot_data_and_drug_status, \
    get_pvs_data_header_wise, get_pvs_slot_details_data_for_pvs_classification, \
    get_sensor_dropping_data_for_csv, get_pvs_dropping_data_for_csv, \
    get_manual_pack_assigned_by_user_or_partially_filled_by_robot, \
    get_manual_pack_assigned_by_user_or_partially_filled_by_robot_for_analyzer, \
    get_manual_pack_assigned_by_user_and_done, \
    get_manual_pack_assigned_by_user_and_done_with_from_date_to_date, get_canister_drugs_for_imported_batch_db, \
    get_filled_slot_count_of_pack_with_packid_batchid, get_user_report_pack_detail, get_graph_data_for_slot_header,\
    get_slot_header_detail, get_pill_jump_error_count, get_pack_count_for_user_report_error, get_drug_wise_count_for_packs

from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_pack_details import PackDetails
from src.model.model_batch_change_tracker import get_batch_id_by_action_id
from utils.auth_webservices import send_email_for_weekly_robot_update, send_email_for_imported_batch_manual_drugs, \
    send_email_for_pill_combination_in_given_length_width_range, send_email_for_pvs_detection_problem_classification, \
    send_email_for_user_reported_error, send_email_for_user_reported_error_of_green_slot
from src.model.model_pack_verification import get_pack_verification_status_count

logger = settings.logger


@log_args_and_response
def get_robot_daily_update(data_dict):
    """
    This fetches data for robot daily update report
    @param data_dict:contains company_id and system_id
    @return: dict
    """
    time_zone = data_dict.get('time_zone', 'UTC')
    time_zone = settings.TIME_ZONE_MAP[time_zone]
    system_id = data_dict["system_id"]
    company_id = data_dict["company_id"]
    batch_ids = []
    # track_date = datetime.now(pytz.timezone(time_zone)).strftime('%y-%m-%d')
    track_date = (datetime.now(pytz.timezone(time_zone)) - timedelta(days=1)).strftime('%y-%m-%d')
    from_date = (datetime.now(pytz.timezone(time_zone)) - timedelta(days=1)).strftime('%y-%m-%d')
    # to_date = (datetime.now(pytz.timezone(time_zone)) - timedelta(days=1)).strftime('%y-%m-%d')
    to_date = datetime.now(pytz.timezone(time_zone))
    utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
    _date_format = '%Y-%m-%d'
    try:
        response = {}

        # function to get the latest batch
        batch_in_progress_today = get_batch_in_progress_today(track_date, utc_time_zone_offset,
                                                              system_id)

        # function to get total no.of packs processed today
        pack_count_processed_by_robot_today, pack_count_pack_fill_workflow, pack_count_processed_today = \
            get_packs_processed_today(track_date, utc_time_zone_offset, company_id)

        # function to get total no.of packs marked as partially filled by robot
        pack_count_partially_filled_by_robot = get_packs_partially_filled_by_robot(track_date, utc_time_zone_offset,
                                                                                   system_id, company_id)

        # function to get total no. of packs filled in Pack Fill Workflow
        pack_count_with_error = get_pack_count_with_error(track_date, utc_time_zone_offset, company_id)

        # function to get total no. of slots filled by canister
        number_of_slots_filled = get_slots_filled(track_date, utc_time_zone_offset)

        # function to get total no. of manual drop
        pack_fill_workflow_drops, robot_drops_skipped_filled_manually, mfd_drops, mfd_drops_skipped_filled_manually, \
        number_of_manual_drops = get_number_of_manual_drop(track_date, utc_time_zone_offset, system_id, company_id,
                                                           batch_ids)

        # function to get total no. of robot drop
        number_of_robot_drops = get_robot_drops(track_date, utc_time_zone_offset, system_id, company_id, batch_ids)

        # finding total pills dropped today
        total_number_of_drops = int(number_of_manual_drops or 0) + int(number_of_robot_drops or 0)

        # finding percentage of Pack Fill Workflow drops
        if total_number_of_drops != 0:
            percentage_of_pack_fill_workflow_drops = round((int(pack_fill_workflow_drops or 0) / total_number_of_drops)
                                                           * 100, 2)
            percentage_of_robot_drops_skipped_filled_manually = round((int(robot_drops_skipped_filled_manually or 0) /
                                                                       total_number_of_drops) * 100, 2)
            percentage_of_mfd_drops = round((int(mfd_drops or 0) / total_number_of_drops) * 100, 2)
            percentage_of_mfd_drops_skipped_filled_manually = round(
                (int(mfd_drops_skipped_filled_manually or 0) / total_number_of_drops) * 100, 2)
            percentage_of_robot_drops = round((int(number_of_robot_drops or 0) / total_number_of_drops) * 100, 2)
        else:
            percentage_of_pack_fill_workflow_drops = 0
            percentage_of_robot_drops_skipped_filled_manually = 0
            percentage_of_mfd_drops = 0
            percentage_of_mfd_drops_skipped_filled_manually = 0
            percentage_of_robot_drops = 0

        # top 5 manual drugs for today
        top_5_manual_drugs = get_top_5_manual_drugs_without_drug_dimensions(track_date, utc_time_zone_offset, system_id,
                                                                            company_id,
                                                                            batch_in_progress_today['id'])

        data_dict = {
            'from_date': from_date,
            'to_date': to_date,
            'time_zone': time_zone,
            'robot_daily_update_flag': True
        }
        dict_robot_efficiency_details_state_wise_day_wise = get_efficiency_stats(data_dict)

        dict_robot_efficiency_details_state_wise_day_wise = pd.DataFrame(
            dict_robot_efficiency_details_state_wise_day_wise).to_dict()

        effective_uptime = datetime.strptime('00:00:00', '%H:%M:%S').time()
        effective_uptime_except_filling = datetime.strptime('00:00:00', '%H:%M:%S').time()

        if dict_robot_efficiency_details_state_wise_day_wise:
            dict_effective_uptime = dict_robot_efficiency_details_state_wise_day_wise["effective_uptime"]
            for key in dict_effective_uptime:
                value1 = datetime.strptime(dict_effective_uptime[key], '%H:%M:%S').time()
                effective_uptime = timedelta(hours=effective_uptime.hour + value1.hour, minutes=
                effective_uptime.minute + value1.minute, seconds=effective_uptime.second + value1.second)
                effective_uptime = datetime.strptime(str(effective_uptime), '%H:%M:%S').time()

            dict_effective_uptime_except_filling = \
                dict_robot_efficiency_details_state_wise_day_wise["effective_uptime_except_filling"]
            for key in dict_effective_uptime_except_filling:
                value1 = datetime.strptime(dict_effective_uptime_except_filling[key], '%H:%M:%S').time()
                effective_uptime_except_filling = timedelta(hours=
                                                            effective_uptime_except_filling.hour + value1.hour,
                                                            minutes=
                                                            effective_uptime_except_filling.minute + value1.minute,
                                                            seconds=effective_uptime_except_filling.second + value1.second)
                effective_uptime_except_filling = datetime.strptime(
                    str(effective_uptime_except_filling), '%H:%M:%S').time()

        # mfd filling details
        mfd_filling_details = get_mfd_filling_details(track_date, utc_time_zone_offset)
        if len(mfd_filling_details) != 0:
            mfd_filling_time = str(mfd_filling_details["filling_time"])
            mfd_filling_time = mfd_filling_time[2:-2]
            mfd_total_canisters_filled = str(mfd_filling_details["total_canisters_filled"])
            mfd_total_canisters_filled = mfd_total_canisters_filled[1:-1]
            mfd_canisters_filled_per_hour = str(mfd_filling_details["canisters_per_hour"])
            mfd_canisters_filled_per_hour = mfd_canisters_filled_per_hour[1:-1]
        else:
            mfd_filling_time = ""
            mfd_total_canisters_filled = ""
            mfd_canisters_filled_per_hour = ""

        response['Date'] = (datetime.now(pytz.timezone(time_zone)) - timedelta(days=1)).strftime('%m-%d-%Y')
        response['Batch Id'] = batch_in_progress_today['id']
        response['Total packs processed'] = pack_count_processed_today
        response['Packs processed by robot'] = pack_count_processed_by_robot_today
        response['Partially filled by robot'] = pack_count_partially_filled_by_robot
        response['Pack filled by PFW'] = pack_count_pack_fill_workflow
        response['System Start time / Stop time'] = ""
        response['Working hours / Man hours'] = effective_uptime
        response[
            'Working hours / Man hours except filling'] = effective_uptime_except_filling
        response["RobotA uptime"] = ""
        response["RobotB uptime"] = ""
        response["RobotA downtime"] = ""
        response["RobotB downtime"] = ""
        response["Packs per hour"] = ""
        response['MFD filling details'] = mfd_filling_details
        response['MFD filling time'] = mfd_filling_time
        response["MFD total canisters filled"] = mfd_total_canisters_filled
        response["MFD canisters filled per hour"] = mfd_canisters_filled_per_hour
        response['Total slots filled'] = number_of_slots_filled
        response['Total pills dropped'] = total_number_of_drops
        response['Pack Fill Workflow drop quantity'] = pack_fill_workflow_drops
        response['Pack Fill Workflow drop percentage'] = percentage_of_pack_fill_workflow_drops
        response['Robot drop skipped and filled manually quantity'] = robot_drops_skipped_filled_manually
        response['Robot drop skipped and filled manually percentage'] = \
            percentage_of_robot_drops_skipped_filled_manually
        response['MFD drop quantity'] = mfd_drops
        response['MFD drop percentage'] = percentage_of_mfd_drops
        response['MFD drops skipped and filled manually quantity'] = mfd_drops_skipped_filled_manually
        response['MFD drops skipped and filled manually percentage'] = percentage_of_mfd_drops_skipped_filled_manually
        response['Robot drop quantity'] = number_of_robot_drops
        response['Robot drop percentage'] = percentage_of_robot_drops
        response['Erroneous packs'] = pack_count_with_error
        response['Error Type slot wise'] = ""
        response['Issue with canister'] = ""
        response['MFD incorrect fill'] = ""
        response['Stuck in PF trays'] = ""
        response['Total Missing drug'] = ""
        response['Missing drugs Data'] = ""
        response['Top 5 Manual_drugs'] = top_5_manual_drugs

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_robot_daily_update {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_robot_daily_update: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_slots_filled(track_date, offset):
    """
    Function to check total no. of slots filled track_date
    @param track_date: date - track_date's date
    @param offset: for timezone conversion
    @return: dict
    """
    try:
        robot_canister_slot_count = get_slots_filled_by_robot_canister(track_date, offset)
        mfd_canister_slot_count = get_slots_filled_by_mfd_canister(track_date, offset)

        slot_count = int(robot_canister_slot_count or 0) + int(mfd_canister_slot_count or 0)

        return slot_count

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_slots_filled {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_slots_filled: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_ndc_percentile_usage(data_dict):
    """
    Function to check percentile usage of ndc
    @param data_dict:
    """
    try:
        time_zone = data_dict.get('time_zone', 'UTC')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        system_id = data_dict["system_id"]
        company_id = data_dict["company_id"]
        ndc = data_dict["ndc"]
        ndc = str(ndc).zfill(11)
        track_date = (datetime.now(pytz.timezone(time_zone)) - timedelta(days=90)).strftime('%y-%m-%d')
        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        ndc_list_last_3_months_usage = db_get_ndc_list_last_3_months_usage(track_date, system_id, company_id,
                                                                           utc_time_zone_offset)
        df_ndc_list_last_3_months_usage = pd.DataFrame(ndc_list_last_3_months_usage)
        df_ndc_list_last_3_months_usage['coverage'] = df_ndc_list_last_3_months_usage['pack_count'] / \
                                                   df_ndc_list_last_3_months_usage['pack_count'].sum()
        df_ndc_list_last_3_months_usage = df_ndc_list_last_3_months_usage.sort_values(by='pack_count',
                                                                                ascending=True)
        df_ndc_list_last_3_months_usage['cum coverage'] = df_ndc_list_last_3_months_usage['coverage'].cumsum()

        result_df = df_ndc_list_last_3_months_usage[df_ndc_list_last_3_months_usage['ndc'] == ndc]
        dict_result = result_df.to_dict('list')
        return dict_result

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_ndc_percentile_usage {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_ndc_percentile_usage: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_number_of_manual_drop(track_date, offset, system_id: int, company_id: int, batch_ids: list):
    """
    Function to check track_date's total no. of manual drop
    @param track_date: date - track_date's date
    @param system_id
    @param company_id
    @param offset: for timezone conversion
    @param batch_ids: list of batch_ids
    @return: dict
    """
    try:
        pack_fill_workflow_drops = get_pack_fill_workflow_drops(track_date, offset, company_id, batch_ids)
        robot_drops_skipped_filled_manually = get_robot_drops_skipped_filled_manually(track_date, offset, system_id,
                                                                                      company_id, batch_ids)
        mfd_drops = get_mfd_drops(track_date, offset, system_id, company_id, batch_ids)
        mfd_drops_skipped_filled_manually = get_mfd_drops_skipped_filled_manually(track_date, offset, system_id,
                                                                                  company_id, batch_ids)

        total_manual_drop_count = float(pack_fill_workflow_drops or 0) + int(robot_drops_skipped_filled_manually or 0) + \
                                  float(mfd_drops or 0) + float(mfd_drops_skipped_filled_manually or 0)

        return pack_fill_workflow_drops, robot_drops_skipped_filled_manually, mfd_drops, \
               mfd_drops_skipped_filled_manually, total_manual_drop_count

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_number_of_manual_drop {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_number_of_manual_drop: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_number_of_robot_drop(track_date: date, offset, system_id: int, company_id: int):
    """
    Function to check track_date's total no. of robot drop
    @param track_date: date - track_date's date
    @param system_id: int
    @param company_id: int
    @param offset: for timezone conversion
    @return: dict
    """
    try:
        robot_drops = get_robot_drops(track_date, offset, system_id, company_id)

        return robot_drops

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_number_of_robot_drop {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_number_of_robot_drop: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_mfd_filling_details(track_date, offset):
    """
    Function to get_mfd_filling_details
    @param track_date: date - track_date's date
    @param offset: for timezone conversion
    @return: dict
    """
    try:
        mfd_data = get_mfd_data(track_date, offset)
        df_mfd_data = pd.DataFrame(mfd_data)

        if df_mfd_data.empty:
            dict_mfd_data = {}
            return dict_mfd_data

        # fetch action_date_time_hour and action_date_time_day for hour wise day wise grouping
        df_mfd_data.loc[:, 'action_date_time_hour'] = df_mfd_data.loc[:, 'action_date_time'].apply(lambda x: x.hour)
        df_mfd_data.loc[:, 'action_date_time_day'] = df_mfd_data.loc[:, 'action_date_time'].apply(lambda x: x.day)

        # mfd batch wise efficiency stats group by day hour
        df_mfd_data = df_mfd_data.groupby(['batch_id', 'action_date_time_day', 'action_date_time_hour']) \
            .agg(total_canisters_filled=('mfd_canister_id', 'nunique'), start_date_time=('action_date_time', 'min'),
                 end_date_time=('action_date_time', 'max'), ).reset_index()

        # calculating total_time_taken_in_time_delta
        df_mfd_data.loc[:, 'filling_time'] = df_mfd_data.loc[:, 'end_date_time'] - df_mfd_data.loc[:, 'start_date_time']

        # mfd batch wise efficiency stats group by day hour
        df_mfd_data = df_mfd_data.groupby(['batch_id']) \
            .agg(filling_time=('filling_time', 'sum'), total_canisters_filled=('total_canisters_filled', 'sum'),
                 ).reset_index()

        df_mfd_data.loc[:, 'filling_time2'] = df_mfd_data.apply(lambda row: float(row.filling_time /
                                                                                  timedelta(hours=1) if row.filling_time != 0 else 0), axis=1)

        df_mfd_data.loc[:, 'filling_time2'] = round(df_mfd_data['filling_time2'], 2)

        df_mfd_data.loc[:, 'filling_time'] = df_mfd_data["filling_time"].astype(str).map(lambda x: x[7:])

        df_mfd_data.loc[:, 'canisters_per_hour'] = df_mfd_data.apply(lambda row: round((row.total_canisters_filled /
                                                                                        row.filling_time2 if row.filling_time2 != 0 else 0), 2),
                                                                     axis=1)

        df_mfd_data = df_mfd_data[['filling_time', 'total_canisters_filled', 'canisters_per_hour']]

        dict_mfd_data = df_mfd_data.to_dict('list')
        return dict_mfd_data

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_mfd_filling_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_mfd_filling_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_efficiency_stats(data_dict):
    """
    Function to measure efficiency of pack fill workflow as well as robot process
    :param data_dict containing company_id, system_id and from_date
    :return:
    """
    time_zone = data_dict.get('time_zone', 'UTC')
    time_zone = settings.TIME_ZONE_MAP[time_zone]

    utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
    robot_daily_update_flag = data_dict['robot_daily_update_flag']
    _date_format = '%Y-%m-%d'
    if data_dict["from_date"] is not None and data_dict["to_date"] is not None:
        from_date_in_date_format = data_dict["from_date"]
        to_date_in_date_format = data_dict["to_date"]
    else:
        from_date_in_date_format = (datetime.now(pytz.timezone(time_zone)) - timedelta(days=7)).strftime('%y-%m-%d')
        to_date_in_date_format = (datetime.now(pytz.timezone(time_zone)) - timedelta(days=1)).strftime('%y-%m-%d')

    try:
        # function to show canister transfer work flow efficiency stats
        ct = CanisterTransferWorkflowEfficiency()
        df_canister_transfer_details_batch_wise_device_wise = ct.get_canister_transfer_efficiency(
            from_date=from_date_in_date_format, to_date=to_date_in_date_format, offset=utc_time_zone_offset)

        # function to show drug replenish work flow efficiency stats
        dr = DrugReplenishWorkflowEfficiency()
        df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change = \
            dr.get_drug_replenish_efficiency(from_date=from_date_in_date_format, to_date=to_date_in_date_format,
                                             offset=utc_time_zone_offset)

        # function to show mfd canister transfer work flow efficiency stats
        mct = MFDCanisterTransferWorkflowEfficiency()
        df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day = \
            mct.get_mfd_workflow_efficiency(from_date=from_date_in_date_format, to_date=to_date_in_date_format,
                                            offset=utc_time_zone_offset)

        # function to show robot processing work flow efficiency stats
        rp = RobotProcessingWorkflowEfficiency()
        df_batch_id_imported_date_pack_id_status_created_filled_date_status_wise_group_by_day_hour = \
            rp.get_robot_processing_time_efficiency(from_date=from_date_in_date_format, to_date=to_date_in_date_format,
                                                    offset=utc_time_zone_offset)

        dict_robot_efficiency_details_state_wise_day_wise, dict_mfd_filled_details_group_by_day, \
        dict_drug_replenish_details_whole = get_analysis_tables(df_canister_transfer_details_batch_wise_device_wise,
                                                                df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change,
                                                                df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day,
                                                                df_batch_id_imported_date_pack_id_status_created_filled_date_status_wise_group_by_day_hour
                                                                )

        response = {"Auto Packs: Day Wise Time Stats": dict_robot_efficiency_details_state_wise_day_wise,
                    "Manual Filling Time Stats": dict_mfd_filled_details_group_by_day,
                    "Drug Replenish Details": dict_drug_replenish_details_whole}

        if robot_daily_update_flag:
            return dict_robot_efficiency_details_state_wise_day_wise
        else:
            if response:
                send_email_for_weekly_robot_update(weekly_update_data=response)
                return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_efficiency_stats {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_efficiency_stats: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_analysis_tables(df_canister_transfer_details_batch_wise_device_wise,
                        df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change,
                        df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day,
                        df_batch_id_imported_date_pack_id_status_created_filled_date_status_wise_group_by_day_hour):
    """
    Function to prepare efficiency tables for email
    :param df_canister_transfer_details_batch_wise_device_wise:
    :param df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change:
    :param df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day:
    :param df_batch_id_imported_date_pack_id_status_created_filled_date_status_wise_group_by_day_hour:
    :return:
    """
    try:
        dict_robot_efficiency_details_state_wise_day_wise, dict_mfd_filled_details_group_by_day, \
        dict_drug_replenish_details_whole = get_auto_packs_day_wise_time_stats(
            df_canister_transfer_details_batch_wise_device_wise,
            df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change,
            df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day,
            df_batch_id_imported_date_pack_id_status_created_filled_date_status_wise_group_by_day_hour, )

        return dict_robot_efficiency_details_state_wise_day_wise, dict_mfd_filled_details_group_by_day, \
               dict_drug_replenish_details_whole

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_analysis_tables {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_analysis_tables: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_manual_filling_time_stats(df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day):
    """
    Function to prepare efficiency tables for email
    :param df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day:
    :return:
    """
    try:
        dict_mfd_filled_details_group_by_day = {}

        if df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day.empty:
            return dict_mfd_filled_details_group_by_day

        df_mfd_filled_details = df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day[
            df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day['transfer_status'] == 'Filled']

        if df_mfd_filled_details.empty:
            return dict_mfd_filled_details_group_by_day

        # calculating total time taken for each workflow day-hour group
        df_mfd_filled_details.loc[:, 'total_time_taken_in_time_delta'] = \
            df_mfd_filled_details['end_date_time'] - \
            df_mfd_filled_details['start_date_time']

        df_mfd_filled_details_group_by_day = \
            df_mfd_filled_details.groupby(['modified_date_day']).agg(filling_time=
                                                                     ('total_time_taken_in_time_delta', 'sum'),
                                                                     total_canisters_filled=('total_canisters', 'sum'),
                                                                     manual_filling_date=('end_date_time', 'first'),
                                                                     batch_id=('batch_id', 'first')).reset_index()

        df_mfd_filled_details_group_by_day.loc[:, 'manual_filling_date'] = \
            df_mfd_filled_details_group_by_day[
                "manual_filling_date"].astype(str).map(lambda x: x[:10])

        df_mfd_filled_details_group_by_day.loc[:, 'filling_time2'] = \
            df_mfd_filled_details_group_by_day.apply(lambda row: float(row.filling_time / timedelta(hours=1)),
                                                     axis=1)

        df_mfd_filled_details_group_by_day.loc[:, 'filling_time2'] = round(df_mfd_filled_details_group_by_day
                                                                           ['filling_time2'], 2)

        df_mfd_filled_details_group_by_day.loc[:, 'filling_time'] = \
            df_mfd_filled_details_group_by_day[
                "filling_time"].astype(str).map(lambda x: x[7:])

        df_mfd_filled_details_group_by_day.loc[:, 'canisters_per_hour'] = \
            df_mfd_filled_details_group_by_day.apply(
                lambda row: round((row.total_canisters_filled / row.filling_time2) if row.filling_time2 > 1 else
                                  row.total_canisters_filled, 2), axis=1)

        df_mfd_filled_details_group_by_day = \
            df_mfd_filled_details_group_by_day[['manual_filling_date', 'batch_id', 'filling_time',
                                                'total_canisters_filled', 'canisters_per_hour']]

        df_mfd_filled_details_group_by_day["batch_id"] = df_mfd_filled_details_group_by_day["batch_id"].astype(int)

        df_mfd_filled_details_group_by_day = df_mfd_filled_details_group_by_day.sort_values(['manual_filling_date'],
                                                                                            ascending=[True])

        dict_mfd_filled_details_group_by_day = df_mfd_filled_details_group_by_day.to_dict('records')
        return dict_mfd_filled_details_group_by_day

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_manual_filling_time_stats {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_filling_time_stats: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_auto_packs_day_wise_time_stats(df_canister_transfer_details_batch_wise_device_wise,
                                       df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change,
                                       df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day,
                                       df_batch_id_imported_date_pack_id_status_created_filled_date_status_wise_group_by_day_hour):
    """
    Function to prepare efficiency tables for auto packs day wise time stats
    :param df_canister_transfer_details_batch_wise_device_wise:
    :param df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change:
    :param df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day:
    :param df_batch_id_imported_date_pack_id_status_created_filled_date_status_wise_group_by_day_hour:
    :return:
    """
    try:
        # combining canister_transfer, drug_replenish, mfd_canister transfer and robot processing efficiency details
        # to get over all robot efficiency
        dict_robot_efficiency_details_state_wise_day_wise = {}
        dict_mfd_filled_details_group_by_day = {}
        dict_drug_replenish_details_whole = {}

        if not df_canister_transfer_details_batch_wise_device_wise.empty:
            df_canister_transfer_details_batch_wise_device_wise.loc[:, "work_flow"] = "canister_transfer"

        if not df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change.empty:
            df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change.loc[:, "work_flow"] \
                = "drug_replenish"

        if not df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day.empty:
            df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day.loc[:, "work_flow"] = \
                "mfd_canister_transfer"

        if not df_batch_id_imported_date_pack_id_status_created_filled_date_status_wise_group_by_day_hour.empty:
            df_batch_id_imported_date_pack_id_status_created_filled_date_status_wise_group_by_day_hour.loc[:,
            "work_flow"] = "robot_processing"

        df_robot_efficiency_details_state_wise = df_canister_transfer_details_batch_wise_device_wise.append(
            [df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change,
             df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day,
             df_batch_id_imported_date_pack_id_status_created_filled_date_status_wise_group_by_day_hour])

        if df_robot_efficiency_details_state_wise.empty:
            return dict_robot_efficiency_details_state_wise_day_wise, dict_mfd_filled_details_group_by_day, \
                   dict_drug_replenish_details_whole

        df_robot_efficiency_details_state_wise = df_robot_efficiency_details_state_wise[
            ~df_robot_efficiency_details_state_wise['transfer_status'].isin(['Filled', 'Deleted'])]

        # performing operations on robot efficiency dataframe for efficiency analysis
        if 'total_canisters' in df_robot_efficiency_details_state_wise.columns and 'total_pack_count_status' in \
                df_robot_efficiency_details_state_wise.columns:
            df_robot_efficiency_details_state_wise.loc[:, "total_canisters_or_packs"] = \
            df_robot_efficiency_details_state_wise.loc[:, ['total_canisters', 'total_pack_count_status']].sum(axis=1)
        elif 'total_canisters' in df_robot_efficiency_details_state_wise.columns:
            df_robot_efficiency_details_state_wise.loc[:, "total_canisters_or_packs"] = \
                df_robot_efficiency_details_state_wise.loc[:, 'total_canisters']
        elif 'total_pack_count_status' in df_robot_efficiency_details_state_wise.columns:
            df_robot_efficiency_details_state_wise.loc[:, "total_canisters_or_packs"] = \
                df_robot_efficiency_details_state_wise.loc[:, 'total_pack_count_status']

        # keeping required columns only
        df_robot_efficiency_details_state_wise = df_robot_efficiency_details_state_wise[['batch_id', 'transfer_status',
                                                                                         'start_date_time',
                                                                                         'end_date_time',
                                                                                         'total_time_taken',
                                                                                         'work_flow',
                                                                                         'total_packs',
                                                                                         'total_canisters',
                                                                                         'total_canisters_or_packs'
                                                                                         ]]
        # check different day and hour when different process executes
        df_robot_efficiency_details_state_wise.loc[:, 'start_date_time_hour'] = \
            df_robot_efficiency_details_state_wise['start_date_time'].apply(lambda x: x.hour)
        df_robot_efficiency_details_state_wise.loc[:, 'start_date_time_day'] = \
            df_robot_efficiency_details_state_wise['start_date_time'].apply(lambda x: x.day)

        df_robot_efficiency_details_state_wise_day_wise_batch_detail = df_robot_efficiency_details_state_wise.groupby(
            ['start_date_time_day', 'start_date_time_hour']).agg(batch_id=('batch_id', 'last')).reset_index()

        df_robot_efficiency_details_state_wise = df_robot_efficiency_details_state_wise.merge(
            df_robot_efficiency_details_state_wise_day_wise_batch_detail, on=['start_date_time_day',
                                                                              'start_date_time_hour'], how='left')

        df_robot_efficiency_details_state_wise['batch_id'] = np.where(
            (df_robot_efficiency_details_state_wise.batch_id_x == 0),
            df_robot_efficiency_details_state_wise.batch_id_y,
            df_robot_efficiency_details_state_wise.batch_id_x)

        # calculating time efficiency day wise hour wise
        df_robot_efficiency_details_state_wise_group_by_hour_day = df_robot_efficiency_details_state_wise.groupby(
            ['batch_id', 'start_date_time_day', 'start_date_time_hour']).agg(start_date_time=('start_date_time', 'min'),
                                                                             end_date_time=(
                                                                                 'end_date_time', 'max')).reset_index()

        # getting batch wise workflow wise time efficiency stats
        df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow = \
            df_robot_efficiency_details_state_wise.groupby(['batch_id', 'start_date_time_day', 'start_date_time_hour',
                                                            'work_flow']).agg(
                start_date_time=('start_date_time', 'min'),
                end_date_time=('end_date_time', 'max'), total_canisters_or_packs=
                ('total_canisters_or_packs', 'sum')).reset_index()

        # separating robot_processing workflow data separately for calculating robot processing time separately
        df_robot_efficiency_details_robot_processing_state = \
            df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow[
                df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow['work_flow'] == 'robot_processing']

        # calculating total time taken for each day-hour group
        df_robot_efficiency_details_robot_processing_state.loc[:, 'total_time_taken_in_time_delta'] = \
            df_robot_efficiency_details_robot_processing_state['end_date_time'] - \
            df_robot_efficiency_details_robot_processing_state['start_date_time']

        # formatting total time for better visualization
        df_robot_efficiency_details_robot_processing_state.loc[:, 'total_time'] = \
            df_robot_efficiency_details_robot_processing_state[
                "total_time_taken_in_time_delta"].astype(str).map(lambda x: x[7:])

        # calculating total time taken for each workflow day-hour group
        df_robot_efficiency_details_robot_processing_state.loc[:, 'total_time_taken_in_time_delta'] = \
            df_robot_efficiency_details_robot_processing_state['end_date_time'] - \
            df_robot_efficiency_details_robot_processing_state['start_date_time']

        # formatting total time for better visualization
        df_robot_efficiency_details_robot_processing_state.loc[:, 'total_time'] = \
            df_robot_efficiency_details_robot_processing_state[
                "total_time_taken_in_time_delta"].astype(str).map(lambda x: x[7:])

        # getting data of robot processing where packs completed in robot state
        df_robot_efficiency_details_robot_processing_state_done = df_robot_efficiency_details_state_wise[
            df_robot_efficiency_details_state_wise['transfer_status'].isin(['Done', 'Partially Filled by Robot',
                                                                            'Processed Manually'])]

        # calculating total time of robot state done
        df_robot_efficiency_details_robot_processing_state_done.loc[:, 'total_time_taken_in_time_delta'] = \
            df_robot_efficiency_details_robot_processing_state_done['end_date_time'] - \
            df_robot_efficiency_details_robot_processing_state_done['start_date_time']

        # calculating total packs done batch_wise
        df_robot_efficiency_details_robot_processing_state_done_batch_wise = \
            df_robot_efficiency_details_robot_processing_state_done.groupby(
                ['batch_id']).agg(total_packs_done_batch_wise=('total_canisters_or_packs', 'sum')).reset_index()

        # calculating batch wise state wise total time taken
        df_robot_efficiency_details_robot_processing_state_batch_wise = \
            df_robot_efficiency_details_robot_processing_state.groupby(['batch_id']).agg(total_time_taken_batch_wise=
            (
                'total_time_taken_in_time_delta',
                'sum')).reset_index()

        # merging state wise batch wise data with robot state done data for calculating packs done per hour
        df_robot_efficiency_details_robot_processing_state_batch_wise = \
            df_robot_efficiency_details_robot_processing_state_batch_wise.merge(
                df_robot_efficiency_details_robot_processing_state_done_batch_wise, on=['batch_id'],
                how='inner').reset_index()

        # calculating time taken in hour
        df_robot_efficiency_details_robot_processing_state_batch_wise.loc[:, 'time_taken_in_hour'] = \
            df_robot_efficiency_details_robot_processing_state_batch_wise.apply(
                lambda row: float((row.total_time_taken_batch_wise.total_seconds()) / 3600), axis=1)

        # calculating packs done per hour
        df_robot_efficiency_details_robot_processing_state_batch_wise.loc[:, 'packs_done_per_hour'] = \
            df_robot_efficiency_details_robot_processing_state_batch_wise.apply(
                lambda row: float((row.total_packs_done_batch_wise / row.time_taken_in_hour)) if
                row.time_taken_in_hour != 0 else 0, axis=1)

        # calculating total time taken for each day-hour group
        df_robot_efficiency_details_state_wise_group_by_hour_day.loc[:, 'total_time_taken_in_time_delta'] = \
            df_robot_efficiency_details_state_wise_group_by_hour_day['end_date_time'] - \
            df_robot_efficiency_details_state_wise_group_by_hour_day['start_date_time']

        # formatting total time for better visualization
        df_robot_efficiency_details_state_wise_group_by_hour_day.loc[:, 'total_time'] = \
            df_robot_efficiency_details_state_wise_group_by_hour_day[
                "total_time_taken_in_time_delta"].astype(str).map(lambda x: x[7:])

        # calculating total time taken for each workflow day-hour group
        df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow.loc[:, 'total_time_taken_in_time_delta'] = \
            df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow['end_date_time'] - \
            df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow['start_date_time']

        # formatting total time for better visualization
        df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow.loc[:, 'total_time'] = \
            df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow[
                "total_time_taken_in_time_delta"].astype(str).map(lambda x: x[7:])

        # calculating total time for robot efficiency details batch wise
        df_robot_efficiency_details_state_wise.loc[:, 'total_time_taken_in_time_delta'] = \
            df_robot_efficiency_details_state_wise['end_date_time'] - \
            df_robot_efficiency_details_state_wise['start_date_time']

        df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow_per_batch = \
            df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow

        # sort records in increasing order of end date time
        df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow_per_batch = \
            df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow_per_batch.sort_values(['end_date_time'],
                                                                                                     ascending=[True])

        # getting list of total days
        day_list = \
            df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow_per_batch['start_date_time_day'].unique()

        df_robot_efficiency_details_work_flow_combined1 = pd.DataFrame()

        for day in day_list:
            # gantt chart work flow wise showing total canisters/packs of each status of workflow along with transfer
            # status
            df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow_per_batch_per_day = \
                df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow[
                    df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow['start_date_time_day']
                    == day]
            df_robot_efficiency_details_robot_processing_state_done_batch_wise_per_day = \
                df_robot_efficiency_details_robot_processing_state_done[
                    df_robot_efficiency_details_robot_processing_state_done['start_date_time_day'] == day]

            df_robot_efficiency_details_day_wise_group_by_day = \
                df_robot_efficiency_details_state_wise_group_by_hour_day[
                    df_robot_efficiency_details_state_wise_group_by_hour_day['start_date_time_day'] == day]

            # fill NaN with zero
            df_robot_efficiency_details_robot_processing_state_done_batch_wise_per_day.loc[:,
            'total_canisters_or_packs'].fillna(value=0, inplace=True)

            # grouping robot processing state done batch wise
            df_robot_efficiency_details_robot_processing_state_done_batch_wise_per_day = \
                df_robot_efficiency_details_robot_processing_state_done_batch_wise_per_day.groupby(
                    ['batch_id']).agg(total_packs_done=('total_canisters_or_packs', 'sum')).reset_index()

            # grouping robot efficiency details day wise
            df_robot_efficiency_details_day_wise_group_by_day = df_robot_efficiency_details_day_wise_group_by_day \
                .merge(df_robot_efficiency_details_robot_processing_state_done_batch_wise_per_day, how=
            'left', on='batch_id')

            df_robot_efficiency_details_state_wise_group_by_work_flow = \
                df_robot_efficiency_details_state_wise_group_by_hour_day_work_flow_per_batch_per_day.groupby(
                    ['work_flow', 'batch_id']).agg(
                    total_time_taken_in_time_delta=('total_time_taken_in_time_delta', 'sum'),
                    total_canisters_or_packs_in_different_states=('total_canisters_or_packs', 'sum'),
                    processing_date=('end_date_time', 'first')).reset_index()

            df_robot_efficiency_details_state_wise_group_by_work_flow.loc[:, 'processing_date'] = \
                df_robot_efficiency_details_state_wise_group_by_work_flow[
                    "processing_date"].astype(str).map(lambda x: x[:10])

            df_robot_efficiency_details_day_wise_group_by_day = \
                df_robot_efficiency_details_day_wise_group_by_day.groupby(
                    ['batch_id']).agg(total_time_taken_in_time_delta=('total_time_taken_in_time_delta', 'sum'),
                                      total_packs_done=('total_packs_done', 'first'),
                                      processing_date=('end_date_time', 'first')
                                      ).reset_index()

            df_robot_efficiency_details_state_wise_group_by_work_flow.loc[:, 'day'] = str(day)

            df_robot_efficiency_details_day_wise_group_by_day.loc[:, 'effective_uptime'] = \
                df_robot_efficiency_details_day_wise_group_by_day[
                    "total_time_taken_in_time_delta"].astype(str).map(lambda x: x[7:])

            df_robot_efficiency_details_day_wise_group_by_day['effective_uptime_in_hours'] \
                = df_robot_efficiency_details_day_wise_group_by_day.apply(lambda row:
                                                                          round((
                                                                                    row.total_time_taken_in_time_delta) / timedelta(
                                                                              hours=1), 2), axis=1)

            df_robot_efficiency_details_day_wise_group_by_day['packs_per_hour'] \
                = df_robot_efficiency_details_day_wise_group_by_day.apply(lambda row:
                                                                          round((
                                                                                    row.total_packs_done) / row.effective_uptime_in_hours,
                                                                                2) if row.effective_uptime_in_hours > 1 else
                                                                          row.total_packs_done,
                                                                          axis=1)

            df_robot_processing = df_robot_efficiency_details_state_wise_group_by_work_flow \
                [df_robot_efficiency_details_state_wise_group_by_work_flow['work_flow'] == \
                 'robot_processing']

            df_robot_processing = df_robot_processing[['batch_id', 'total_time_taken_in_time_delta']]

            df_robot_efficiency_details_day_wise_group_by_day = df_robot_efficiency_details_day_wise_group_by_day \
                .merge(df_robot_processing, how='left', on='batch_id')

            df_robot_efficiency_details_day_wise_group_by_day.loc[:, 'robot_processing_time'] = \
                df_robot_efficiency_details_day_wise_group_by_day[
                    "total_time_taken_in_time_delta_y"].astype(str).map(lambda x: x[7:])

            df_robot_efficiency_details_day_wise_group_by_day['total_time_in_robot_processing'] \
                = df_robot_efficiency_details_day_wise_group_by_day.apply(lambda row:
                                                                          round((
                                                                                    row.total_time_taken_in_time_delta_y) / timedelta(
                                                                              hours=1), 2), axis=1)

            df_robot_efficiency_details_day_wise_group_by_day['packs_per_hour_in_robot_processing'] \
                = df_robot_efficiency_details_day_wise_group_by_day.apply(lambda row:
                                                                          round(row.total_packs_done /
                                                                                row.total_time_in_robot_processing,
                                                                                2) if row.total_time_in_robot_processing > 1 else
                                                                          row.total_packs_done,
                                                                          axis=1)

            df_robot_efficiency_details_day_wise_group_by_day.loc[:, 'start_date_time_day'] = str(day)

            # robot efficiency details day wise combine
            df_robot_efficiency_details_work_flow_combined1 = \
                df_robot_efficiency_details_work_flow_combined1.append(
                    df_robot_efficiency_details_day_wise_group_by_day)

        df_robot_efficiency_details_state_wise_day_wise = \
            df_robot_efficiency_details_work_flow_combined1[['start_date_time_day', 'processing_date', 'batch_id',
                                                             'effective_uptime',
                                                             'total_packs_done', 'packs_per_hour',
                                                             'packs_per_hour_in_robot_processing',
                                                             'robot_processing_time']]

        df_robot_efficiency_details_state_wise_day_wise.drop_duplicates(subset=['start_date_time_day',
                                                                                'total_packs_done'], keep="first",
                                                                        inplace=True)

        df_robot_efficiency_details_state_wise_day_wise.loc[:, 'processing_date'] = \
            df_robot_efficiency_details_state_wise_day_wise["processing_date"].astype(str).map(lambda x:
                                                                                               x[:10])

        df_robot_efficiency_details_state_wise_day_wise["effective_uptime"] = pd.to_timedelta(
            df_robot_efficiency_details_state_wise_day_wise["effective_uptime"]
        )
        df_robot_efficiency_details_state_wise_day_wise = df_robot_efficiency_details_state_wise_day_wise.groupby([
            'batch_id', 'processing_date']).agg(
            start_date_time_day=('start_date_time_day', 'last'), effective_uptime=('effective_uptime', 'sum'),
            total_packs_done=('total_packs_done', 'last'),
            packs_per_hour_in_robot_processing=('packs_per_hour_in_robot_processing', 'last'),
            robot_processing_time=('robot_processing_time', 'last')).reset_index()

        df_robot_efficiency_details_state_wise_day_wise.drop(
            df_robot_efficiency_details_state_wise_day_wise[(df_robot_efficiency_details_state_wise_day_wise[
                                                                 'effective_uptime'] == "00:00:00")].index,
            inplace=True)

        df_robot_efficiency_details_state_wise_day_wise = \
            df_robot_efficiency_details_state_wise_day_wise.dropna().reset_index(drop=True)

        dict_mfd_filled_details_group_by_day = get_manual_filling_time_stats(
            df_mfd_canister_transfer_details_batch_device_wise_group_by_hour_day)
        dict_drug_replenish_details_whole = get_drug_replenish_details(
            df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change)

        df_mfd_filled_details_group_by_day = pd.DataFrame(dict_mfd_filled_details_group_by_day)

        if not df_mfd_filled_details_group_by_day.empty:
            df_mfd_filled_details_group_by_day.rename(
                columns={'manual_filling_date': 'processing_date'}, inplace=True)
            df_mfd_filled_details_group_by_day.rename(
                columns={'manual_filling_date': 'processing_date'}, inplace=True)
            df_robot_efficiency_details_state_wise_day_wise = df_robot_efficiency_details_state_wise_day_wise.merge(
                df_mfd_filled_details_group_by_day, on=['processing_date', 'batch_id'], how='outer')
        else:
            df_robot_efficiency_details_state_wise_day_wise["filling_time"] = "0 days 00:00:00"

        # fill NaN with zero
        df_robot_efficiency_details_state_wise_day_wise["filling_time"].fillna(value="0 days 00:00:00", inplace=True)
        df_robot_efficiency_details_state_wise_day_wise["filling_time"] = pd.to_timedelta(
            df_robot_efficiency_details_state_wise_day_wise[
                "filling_time"])

        df_robot_efficiency_details_state_wise_day_wise["effective_uptime"] = pd.to_timedelta(
            df_robot_efficiency_details_state_wise_day_wise[
                "effective_uptime"])

        df_robot_efficiency_details_state_wise_day_wise.rename(
            columns={'effective_uptime': 'effective_uptime_except_filling'},
            inplace=True)

        df_robot_efficiency_details_state_wise_day_wise["effective_uptime_except_filling"].fillna(
            value="0 days 00:00:00", inplace=True)

        df_robot_efficiency_details_state_wise_day_wise['effective_uptime'] = \
            df_robot_efficiency_details_state_wise_day_wise['effective_uptime_except_filling'] \
            # + \
            # df_robot_efficiency_details_state_wise_day_wise['filling_time']

        df_robot_efficiency_details_state_wise_day_wise["effective_uptime"].fillna(
            value="0 days 00:00:00", inplace=True)

        df_robot_efficiency_details_state_wise_day_wise['effective_uptime'] = \
            df_robot_efficiency_details_state_wise_day_wise["effective_uptime"].astype(str).str[7:]

        df_robot_efficiency_details_state_wise_day_wise['effective_uptime_except_filling'] = \
            df_robot_efficiency_details_state_wise_day_wise["effective_uptime_except_filling"].astype(
                str).str[7:]

        df_robot_efficiency_details_state_wise_day_wise['filling_time'] = \
            df_robot_efficiency_details_state_wise_day_wise["filling_time"].astype(str).str[7:]

        df_robot_efficiency_details_state_wise_day_wise["effective_uptime_except_filling"].fillna(
            value="00:00:00", inplace=True)

        df_robot_efficiency_details_state_wise_day_wise["filling_time"].fillna(
            value="00:00:00", inplace=True)

        df_robot_efficiency_details_state_wise_day_wise = df_robot_efficiency_details_state_wise_day_wise.replace("",
                                                                                                                  "00:00:00")

        df_robot_efficiency_details_state_wise_day_wise["total_packs_done"].fillna(
            value="0.0", inplace=True)

        df_robot_efficiency_details_state_wise_day_wise["packs_per_hour_in_robot_processing"].fillna(
            value="0.0", inplace=True)

        df_robot_efficiency_details_state_wise_day_wise = \
            df_robot_efficiency_details_state_wise_day_wise[['processing_date', 'batch_id',
                                                             'effective_uptime',
                                                             'effective_uptime_except_filling',
                                                             'filling_time',
                                                             'robot_processing_time',
                                                             'total_packs_done',
                                                             'packs_per_hour_in_robot_processing']]

        df_robot_efficiency_details_state_wise_day_wise = \
            df_robot_efficiency_details_state_wise_day_wise.sort_values(['processing_date'], ascending=[True])

        df_robot_efficiency_details_state_wise_day_wise["batch_id"] = \
            df_robot_efficiency_details_state_wise_day_wise["batch_id"].astype(int)
        dict_robot_efficiency_details_state_wise_day_wise = df_robot_efficiency_details_state_wise_day_wise.to_dict(
            'records')

        return dict_robot_efficiency_details_state_wise_day_wise, dict_mfd_filled_details_group_by_day, \
               dict_drug_replenish_details_whole

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_auto_packs_day_wise_time_stats {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_auto_packs_day_wise_time_stats: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_drug_replenish_details(
        df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change):
    """
    Function to prepare drug replenish details tables
    :param df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change:
    :return:
    """
    try:
        dict_drug_replenish_details_whole = {}
        if df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change.empty:
            return dict_drug_replenish_details_whole

        df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change["total_time_taken"] = \
            pd.to_timedelta(df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change[
                                "total_time_taken"])

        df_drug_replenish_details_whole = \
            df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change[
                df_drug_replenish_guided_details_guided_meta_wise_status_wise_group_by_hour_day_change
                ["transfer_status"].isin(["R1 : Guided Replenish With Drug_bottle", "R1 : Guided Replenish With "
                                                                                    "Refill_device"])]

        if df_drug_replenish_details_whole.empty:
            return dict_drug_replenish_details_whole

        df_drug_replenish_details_whole = df_drug_replenish_details_whole.groupby(['status_datetime_day',
                                                                                   'transfer_status']).agg(
            batch_id=('batch_id', 'last'),
            start_date_time=('start_date_time', 'min'), end_date_time=('start_date_time', 'max'),
            total_canisters=('total_canisters', 'sum'),
            total_time_drug_replenish=('total_time_taken', 'sum'),
            total_time_drug_replenish_in_minutes=('total_time_drug_replenish_in_minutes', 'sum')).reset_index()

        df_drug_replenish_details_whole['canisters_replenished_per_hour'] = \
            df_drug_replenish_details_whole.apply(
                lambda row: round((row.total_canisters / (row.total_time_drug_replenish_in_minutes / 60)), 2) if
                (row.total_time_drug_replenish_in_minutes / 60) > 1 else row.total_canisters, axis=1)

        df_drug_replenish_details_whole.loc[:, 'drug_replenish_date'] = df_drug_replenish_details_whole[
            "start_date_time"].astype(str).map(lambda x: x[:10])

        df_drug_replenish_details_whole.rename(
            columns={'transfer_status': 'replenish_mode',
                     'total_canisters': 'total_canisters_replenished'}, inplace=True)

        # renaming different replenish_mode for better visualization
        df_drug_replenish_details_whole[
            "replenish_mode"] \
            .replace({"R1 : Guided Replenish With Drug_bottle": "Drug Bottle",
                      "R1 : Guided Replenish With Refill_device": "Refill Device"
                      },
                     inplace=True)

        df_drug_replenish_details_whole['total_time_drug_replenish'] = df_drug_replenish_details_whole[
            "total_time_drug_replenish"].astype(str)

        df_drug_replenish_details_whole[
            'total_time_drug_replenish'] = df_drug_replenish_details_whole.total_time_drug_replenish.str.replace(
            "0 days ", "")

        # keeping required columns only
        df_drug_replenish_details_whole = df_drug_replenish_details_whole[['drug_replenish_date', 'replenish_mode',
                                                                           'total_time_drug_replenish', 'batch_id',
                                                                           'total_canisters_replenished',
                                                                           'canisters_replenished_per_hour'
                                                                           ]]

        df_drug_replenish_details_whole = df_drug_replenish_details_whole.sort_values(['drug_replenish_date'],
                                                                                      ascending=[True])

        dict_drug_replenish_details_whole = df_drug_replenish_details_whole.to_dict('records')
        return dict_drug_replenish_details_whole

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_drug_replenish_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_drug_replenish_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_manual_drugs_for_imported_batch(data_dict):
    """
    Function to measure efficiency of pack fill workflow as well as robot process
    :param data_dict containing company_id, system_id and from_date
    :return:
    """
    batch_id = data_dict['batch_id']
    system_id = data_dict['system_id']
    company_id = data_dict['company_id']

    try:
        imported_batch_manual_drugs, manual_drug_count = get_manual_drugs_for_imported_batch_db(batch_id, system_id, company_id)

        canister_drug_count = get_canister_drugs_for_imported_batch_db(batch_id, system_id, company_id)

        total_packs_for_imported_batch = PackDetails.db_get_total_packs_count_for_imported_batch_or_merged_batch(batch_id)

        total_mfd_canister_count_to_be_used_for_imported_batch = MfdAnalysis.db_get_total_mfd_canister_to_be_used_by_batch(batch_id)

        if total_mfd_canister_count_to_be_used_for_imported_batch == 0:
            total_mfd_canister_count_to_be_used_for_imported_batch = "Batch is merged so there is no data for mfd_canister"

        response = {'Manual_drugs': imported_batch_manual_drugs,
                    'batch_id': batch_id,
                    'manual_drug_count': manual_drug_count,
                    'canister_drug_count': canister_drug_count,
                    'total_packs': total_packs_for_imported_batch,
                    'total_mfd_canister_to_be_used': total_mfd_canister_count_to_be_used_for_imported_batch
                    }

        if response:
            send_email_for_imported_batch_manual_drugs(manual_drug_data=json.dumps(response))
            return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_manual_drugs_for_imported_batch {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_drugs_for_imported_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_batch_wise_drop_count_percentage(data_dict):
    """
    Function to measure efficiency of pack fill workflow as well as robot process
    :param data_dict containing company_id, system_id and from_date
    :return:
    """
    batch_ids = list(data_dict['batch_ids'].split(","))
    system_id = data_dict['system_id']
    company_id = data_dict['company_id']
    response = {}

    try:
        # top 5 manual drugs for today
        track_date = ""
        utc_time_zone_offset = ""
        pack_fill_workflow_drops, robot_drops_skipped_filled_manually, mfd_drops, mfd_drops_skipped_filled_manually, \
        number_of_manual_drops = get_number_of_manual_drop(track_date, utc_time_zone_offset, system_id, company_id,
                                                           batch_ids)

        # function to get total no. of robot drop
        number_of_robot_drops = get_robot_drops(track_date, utc_time_zone_offset, system_id, company_id, batch_ids)

        # finding total pills dropped today
        total_number_of_drops = int(number_of_manual_drops or 0) + int(number_of_robot_drops or 0)

        # finding percentage of Pack Fill Workflow drops
        if total_number_of_drops != 0:
            percentage_of_pack_fill_workflow_drops = round((int(pack_fill_workflow_drops or 0) / total_number_of_drops)
                                                           * 100, 2)
            percentage_of_robot_drops_skipped_filled_manually = round((int(robot_drops_skipped_filled_manually or 0) /
                                                                       total_number_of_drops) * 100, 2)
            percentage_of_mfd_drops = round((int(mfd_drops or 0) / total_number_of_drops) * 100, 2)
            percentage_of_mfd_drops_skipped_filled_manually = round(
                (int(mfd_drops_skipped_filled_manually or 0) / total_number_of_drops) * 100, 2)
            percentage_of_robot_drops = round((int(number_of_robot_drops or 0) / total_number_of_drops) * 100, 2)
        else:
            percentage_of_pack_fill_workflow_drops = 0
            percentage_of_robot_drops_skipped_filled_manually = 0
            percentage_of_mfd_drops = 0
            percentage_of_mfd_drops_skipped_filled_manually = 0
            percentage_of_robot_drops = 0

        response['Total pills dropped'] = total_number_of_drops
        response['Pack Fill Workflow drop quantity'] = pack_fill_workflow_drops
        response['Pack Fill Workflow drop percentage'] = percentage_of_pack_fill_workflow_drops
        response['Robot drop skipped and filled manually quantity'] = robot_drops_skipped_filled_manually
        response['Robot drop skipped and filled manually percentage'] = \
            percentage_of_robot_drops_skipped_filled_manually
        response['MFD drop quantity'] = mfd_drops
        response['MFD drop percentage'] = percentage_of_mfd_drops
        response['MFD drops skipped and filled manually quantity'] = mfd_drops_skipped_filled_manually
        response['MFD drops skipped and filled manually percentage'] = percentage_of_mfd_drops_skipped_filled_manually
        response['Robot drop quantity'] = number_of_robot_drops
        response['Robot drop percentage'] = percentage_of_robot_drops

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_manual_drugs_for_imported_batch {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_batch_wise_drop_count_percentage: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_sensor_drug_error_data(data_dict):
    """
        Function to measure difference between error of sensor data and error of pvs data
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        track_date = data_dict.get('date')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        system_id = data_dict["system_id"]
        company_id = data_dict["company_id"]
        if track_date is None:
            track_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        sensor_dropping_data = get_sensor_dropping_data(system_id, company_id, track_date, utc_time_zone_offset)
        if len(sensor_dropping_data) == 0:
            response = {
                "sensor_error_data": 0,
            }
            return response
        df_sensor_dropping_data = pd.DataFrame(sensor_dropping_data)

        slot_list = df_sensor_dropping_data["slot_id"].values.tolist()
        slot_header_list = df_sensor_dropping_data["slot_header_id"].values.tolist()
        pvs_data = get_pvs_dropping_data(slot_list, slot_header_list)
        df_pvs_dropping_data = pd.DataFrame(pvs_data)
        df_pvs_dropping_data.drop_duplicates(inplace=True)

        df_pvs_sensor_dropping_data = df_pvs_dropping_data.merge(df_sensor_dropping_data, on='slot_id', how='left')
        if len(sensor_dropping_data) == 0:
            response = {
                "pvs_sensor_dropping_data_drug_wise": 0,
                "pvs_sensor_dropping_data_header_wise": 0,
                "sensor_error_data": 0,
                "number_of_data_dict": 0,
                "error_status": 0
            }
            return response

        batch_list = df_pvs_sensor_dropping_data["batch_id"].values.tolist()

        # Get pack_affected list remove that pack data from data
        pack_affected_list = get_batch_id_by_action_id(batch_list)

        df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
            ~df_pvs_sensor_dropping_data["pack_id"].isin(pack_affected_list)]

        # Get pack_id and slot_number from pill_jump_error table to remove from output
        list_pack_id_and_slot_number = get_pack_id_and_slot_number(track_date, utc_time_zone_offset)

        df_pvs_sensor_dropping_data["pack_id_slot_number"] = df_pvs_sensor_dropping_data.pack_id.astype(str).str \
            .cat(df_pvs_sensor_dropping_data.slot_number.astype(str), sep=',')

        if len(list_pack_id_and_slot_number):
            df_pack_affected_list = pd.DataFrame(list_pack_id_and_slot_number)

            df_pack_affected_list["pack_id_slot_number"] = df_pack_affected_list.pack_id.astype(str).str \
                .cat(df_pack_affected_list.slot_number.astype(str), sep=',')

            skip_pack_id_slot_number_list = df_pack_affected_list['pack_id_slot_number'].tolist()

            df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
                ~df_pvs_sensor_dropping_data["pack_id_slot_number"].isin(skip_pack_id_slot_number_list)]


        df_pvs_sensor_dropping_data.drop('pack_id_slot_number', axis=1, inplace=True)

        df_pvs_sensor_dropping_data_drug_wise = df_pvs_sensor_dropping_data


        df_pvs_sensor_dropping_data_header_wise = df_pvs_sensor_dropping_data.groupby(['slot_header_id']) \
            .agg({'batch_id': 'last', 'pack_id': 'last',
                  'actual_qty': 'sum',
                  'sensor_drop_quantity': 'sum',
                  'pvs_predicted_qty': 'sum',
                  'sensor_dropping_error': 'sum',
                  'pvs_predicted_qty_total': 'last',
                  'sensor_created_date': 'last'}).reset_index()


        number_of_data_dict = dict()

        number_of_data_dict['total_data'] = len(df_pvs_sensor_dropping_data_header_wise)
        # Get Sensor Error data from total data
        df_sensor_error_data = df_pvs_sensor_dropping_data_header_wise[df_pvs_sensor_dropping_data_header_wise[
                                                                           "pvs_predicted_qty_total"] !=
                                                                       df_pvs_sensor_dropping_data_header_wise[
                                                                           "sensor_drop_quantity"]]
        df_sensor_error_data = df_sensor_error_data[df_sensor_error_data[
                                                        "actual_qty"] !=
                                                    df_sensor_error_data[
                                                        "sensor_drop_quantity"]]

        # Slot header list of sensor error
        error_slot_header = df_sensor_error_data["slot_header_id"].values.tolist()

        # Drug wise data for slot header which have error
        df_drug_wise_data_of_error_slot = df_pvs_sensor_dropping_data_drug_wise[
            df_pvs_sensor_dropping_data_drug_wise.slot_header_id.isin(error_slot_header)]

        drug_id_list = df_drug_wise_data_of_error_slot["unique_drug_id"].values.tolist()
        canister_id_list = df_drug_wise_data_of_error_slot["canister_id"].values.tolist()
        if len(drug_id_list) == 0:
            response = {
                "pvs_sensor_dropping_data_drug_wise": 0,
                "pvs_sensor_dropping_data_header_wise": 0,
                "sensor_error_data": 1,
                "number_of_data_dict": 0,
                "error_status": 1
            }
            return response
        # get drug information and location data for slot header which have error
        drug_data_of_error_slot = get_drug_data_of_error_slot(drug_id_list)
        location_id_of_error_slot = get_location_data_of_error_slot(canister_id_list)
        df_drug_data_of_error_slot = pd.DataFrame(drug_data_of_error_slot)
        df_location_data_of_error_slot = pd.DataFrame(location_id_of_error_slot)
        df_drug_wise_data_of_error_slot = df_drug_wise_data_of_error_slot.merge(df_drug_data_of_error_slot,
                                                                                on='unique_drug_id', how='inner')
        df_drug_wise_data_of_error_slot = df_drug_wise_data_of_error_slot.merge(df_location_data_of_error_slot,
                                                                                on='canister_id', how='left')

        number_of_data_dict['sensor_error_data_length'] = len(df_sensor_error_data)
        number_of_data_dict['non_sensor_error_data_length'] = number_of_data_dict['total_data'] - number_of_data_dict[
            'sensor_error_data_length']

        response = {
            "pvs_sensor_dropping_data_drug_wise": df_drug_wise_data_of_error_slot.to_dict('records'),
            "pvs_sensor_dropping_data_header_wise": df_pvs_sensor_dropping_data_header_wise.to_dict('records'),
            "sensor_error_data": df_sensor_error_data.to_dict('records'),
            "number_of_data_dict": number_of_data_dict,
            "error_status": 0
        }

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_sensor_drug_error_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_sensor_drug_error_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pill_analysis_falling_on_3D_printed_part(data_dict):
    """
        Function to measure difference between error of sensor data and error of pvs data
        :param:
        :return:
    """
    global drug_ndc2, drug_ndc3, drug_ndc1, drug_name1, drug_name2, drug_name3
    try:
        time_zone = data_dict.get('time_zone')
        track_date = data_dict.get('date')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        system_id = data_dict["system_id"]
        company_id = data_dict["company_id"]
        min_value = float(data_dict["min_value"])
        max_value = float(data_dict["max_value"])
        if track_date is None:
            track_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        pills_with_width_length_slot_wise = get_pills_with_width_length_slot_wise(system_id, company_id, track_date, utc_time_zone_offset)
        df_pills_with_width_length_slot_wise = pd.DataFrame(pills_with_width_length_slot_wise)

        if not df_pills_with_width_length_slot_wise.empty:
            df_pills_with_width_length_slot_wise["length"] = df_pills_with_width_length_slot_wise["length"].astype(str)
            df_pills_with_width_length_slot_wise["width"] = df_pills_with_width_length_slot_wise["width"].astype(str)
            df_pills_with_width_length_slot_wise_2  = df_pills_with_width_length_slot_wise.groupby(['pack_id','slot_header_id'], as_index=False)[["length","width"]].agg(','.join)
            df_result = pd.DataFrame(columns=['pack_id','slot_header_id','drug_ndc','drug_name','length_combination','width_combination',
                                              'length_width_combination','width_length_combination','sum'])

            i1 = 0
            for ind in df_pills_with_width_length_slot_wise_2.index:
                flag=False
                length_list = list(df_pills_with_width_length_slot_wise_2["length"][ind].split(","))
                width_list = list(df_pills_with_width_length_slot_wise_2["width"][ind].split(","))
                length_list = [float(value) for value in length_list]
                width_list = [float(value) for value in width_list]

                for numbers in itertools.combinations(length_list, 2):
                    if min_value <= sum(numbers) <= max_value:
                        df_result.loc[i1,'pack_id'] = df_pills_with_width_length_slot_wise_2["pack_id"][ind]
                        df_result.loc[i1,'slot_header_id'] = df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)

                        df_result1 = df_pills_with_width_length_slot_wise[
                            (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                            df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                            (df_pills_with_width_length_slot_wise["length"].astype(float) == numbers[0])]
                        if not df_result1.empty:
                            df_result1.reset_index(inplace=True)
                            drug_ndc1 = df_result1["drug_ndc"][0]
                            drug_name1 = df_result1["drug_name"][0]

                        df_result2 = df_pills_with_width_length_slot_wise[
                            (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                             df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                            (df_pills_with_width_length_slot_wise["length"].astype(float) == numbers[1])]
                        if not df_result2.empty:
                            df_result2.reset_index(inplace=True)
                            drug_ndc2 = df_result2["drug_ndc"][0]
                            drug_name2 = df_result2["drug_name"][0]
                        if not df_result1.empty and not df_result2.empty:
                            drug_ndc = drug_ndc1 + "," + drug_ndc2
                            drug_name = drug_name1 +"," + drug_name2
                            df_result.loc[i1,"drug_ndc"] = drug_ndc
                            df_result.loc[i1, "drug_name"] = drug_name
                            df_result.loc[i1,"length_combination"] = str(numbers[0]) + "," + str(numbers[1])
                            df_result.loc[i1, "sum"] = sum(numbers)
                            i1 = i1 + 1
                        else:
                            df_result.drop(i1, axis=0, inplace=True)
                for numbers in itertools.combinations(width_list, 2):
                    if min_value <= sum(numbers) <= max_value:
                        df_result.loc[i1,'pack_id'] = df_pills_with_width_length_slot_wise_2["pack_id"][ind]
                        df_result.loc[i1,"slot_header_id"] = df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)

                        df_result1 = df_pills_with_width_length_slot_wise[
                            (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                             df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                            (df_pills_with_width_length_slot_wise["width"].astype(float) == numbers[0])]
                        if not df_result1.empty:
                            df_result1.reset_index(inplace=True)
                            drug_ndc1 = df_result1["drug_ndc"][0]
                            drug_name1 = df_result1["drug_name"][0]

                        df_result2 = df_pills_with_width_length_slot_wise[
                            (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                             df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                            (df_pills_with_width_length_slot_wise["width"].astype(float) == numbers[1])]
                        if not df_result2.empty:
                            df_result2.reset_index(inplace=True)
                            drug_ndc2 = df_result2["drug_ndc"][0]
                            drug_name2 = df_result1["drug_name"][0]
                        if not df_result1.empty and not df_result2.empty:
                            drug_ndc = drug_ndc1 + "," + drug_ndc2
                            drug_name = drug_name1 + "," + drug_name2
                            df_result.loc[i1,"drug_ndc"] = drug_ndc
                            df_result.loc[i1, "drug_name"] = drug_name
                            df_result.loc[i1,"width_combination"] = str(numbers[0]) + "," + str(numbers[1])
                            df_result.loc[i1, "sum"] = sum(numbers)
                            i1 = i1 + 1
                        else:
                            df_result.drop(i1, axis=0, inplace=True)
                for numbers in itertools.combinations(length_list, 3):
                    if min_value <= sum(numbers) <= max_value:
                        df_result.loc[i1,'pack_id'] = df_pills_with_width_length_slot_wise_2["pack_id"][ind]
                        df_result.loc[i1,"slot_header_id"] = df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)

                        df_result1 = df_pills_with_width_length_slot_wise.loc[
                            (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                             df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                            (df_pills_with_width_length_slot_wise["length"].astype(float) == numbers[0])]
                        if not df_result1.empty:
                            df_result1.reset_index(inplace=True)
                            drug_ndc1 = df_result1["drug_ndc"][0]
                            drug_name1 = df_result1["drug_name"][0]

                        df_result2 = df_pills_with_width_length_slot_wise[
                            (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                             df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                            (df_pills_with_width_length_slot_wise["length"].astype(float) == numbers[1])]
                        if not df_result2.empty:
                            df_result2.reset_index(inplace=True)
                            drug_ndc2 = df_result2["drug_ndc"][0]
                            drug_name2 = df_result2["drug_name"][0]

                        df_result3 = df_pills_with_width_length_slot_wise[
                            (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                             df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                            (df_pills_with_width_length_slot_wise["length"].astype(float) == numbers[2])]

                        if not df_result3.empty:
                            df_result3.reset_index(inplace=True)
                            drug_ndc3 = df_result3["drug_ndc"][0]
                            drug_name3 = df_result3["drug_name"][0]

                        if not df_result1.empty and not df_result2.empty and not df_result3.empty:
                            drug_ndc = drug_ndc1 + "," + drug_ndc2 + "." + drug_ndc3
                            drug_name = drug_name1 + "," + drug_name2 + "." + drug_name3
                            df_result.loc[i1,"drug_ndc"] = drug_ndc
                            df_result.loc[i1, "drug_name"] = drug_name
                            df_result.loc[i1,"length_combination"] = str(numbers[0]) + "," + str(numbers[1]) + "," + str(numbers[2])
                            df_result.loc[i1, "sum"] = sum(numbers)
                            i1 =i1 + 1
                        else:
                            df_result.drop(i1, axis=0, inplace=True)

                for numbers in itertools.combinations(width_list, 3):
                    if min_value <= sum(numbers) <= max_value:
                        df_result.loc[i1,"pack_id"] = df_pills_with_width_length_slot_wise_2["pack_id"][ind]
                        df_result.loc[i1,"slot_header_id"] = df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)

                        df_result1 = df_pills_with_width_length_slot_wise[
                            (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                             df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                            (df_pills_with_width_length_slot_wise["width"].astype(float) == numbers[0])]
                        if not df_result1.empty:
                            df_result1.reset_index(inplace=True)
                            drug_ndc1 = df_result1["drug_ndc"][0]
                            drug_name1 = df_result1["drug_name"][0]

                        df_result2 = df_pills_with_width_length_slot_wise[
                            (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                             df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                            (df_pills_with_width_length_slot_wise["width"].astype(float) == numbers[1])]
                        if not df_result2.empty:
                            df_result2.reset_index(inplace=True)
                            drug_ndc2 = df_result2["drug_ndc"][0]
                            drug_name2 = df_result2["drug_name"][0]

                        df_result3 = df_pills_with_width_length_slot_wise[
                            (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                             df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                            (df_pills_with_width_length_slot_wise["width"].astype(float) == numbers[2])]
                        if not df_result3.empty:
                            df_result3.reset_index(inplace=True)
                            drug_ndc3 = df_result3["drug_ndc"][0]
                            drug_name3 = df_result3["drug_name"][0]

                        if not df_result1.empty and not df_result2.empty and not df_result3.empty:
                            drug_ndc = drug_ndc1 + "," + drug_ndc2 + "." + drug_ndc3
                            drug_name = drug_name1 + "," + drug_name2 + "." + drug_name3
                            df_result.loc[i1,"drug_ndc"] = drug_ndc
                            df_result.loc[i1, "drug_name"] = drug_name
                            df_result.loc[i1,"width_combination"] = str(numbers[0]) + "," + str(numbers[1]) + "," + str(
                            numbers[2])
                            df_result.loc[i1, "sum"] = sum(numbers)
                            i1 = i1 + 1
                        else:
                            df_result.drop(i1, axis=0, inplace=True)

                for i in range(len(length_list)):
                    length_width_list = list()
                    length_width_list.append(length_list[i])
                    for j in range(len(width_list)):
                        if i != j:
                            length_width_list.append(width_list[j])
                            for numbers in itertools.combinations(length_width_list, 2):
                                if not flag:
                                    if min_value <= sum(numbers) <= max_value:
                                        df_result.loc[i1,"pack_id"] = df_pills_with_width_length_slot_wise_2["pack_id"][ind]
                                        df_result.loc[i1,"slot_header_id"] = df_pills_with_width_length_slot_wise_2["slot_header_id"][
                                        ind].astype(int)

                                        df_result1 = df_pills_with_width_length_slot_wise[
                                        (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                                         df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                                        (df_pills_with_width_length_slot_wise["length"].astype(float) == numbers[0])]
                                        if not df_result1.empty:
                                            df_result1.reset_index(inplace=True)
                                            drug_ndc1 = df_result1["drug_ndc"][0]
                                            drug_name1 = df_result1["drug_name"][0]

                                        df_result2 = df_pills_with_width_length_slot_wise[
                                        (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                                         df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                                        (df_pills_with_width_length_slot_wise["width"].astype(float) == numbers[1])]
                                        if not df_result2.empty:
                                            df_result2.reset_index(inplace=True)
                                            drug_ndc2 = df_result2["drug_ndc"][0]
                                            drug_name2 = df_result2["drug_name"][0]
                                        if not df_result1.empty and not df_result2.empty:
                                            drug_ndc = drug_ndc1 + "," + drug_ndc2
                                            drug_name = drug_name1 + "," + drug_name2
                                            df_result.loc[i1,"drug_ndc"] = drug_ndc
                                            df_result.loc[i1, "drug_name"] = drug_name
                                            df_result.loc[i1,"length_width_combination"] = str(numbers[0]) + "," + str(numbers[1])
                                            df_result.loc[i1, "sum"] = sum(numbers)
                                            i1 = i1 + 1
                                            flag = True
                                        else:
                                            df_result.drop(i1, axis=0, inplace=True)
                            for numbers in itertools.combinations(length_width_list, 3):
                                if not flag:
                                    if min_value <= sum(numbers) <= max_value:
                                        df_result.loc[i1,"pack_id"] = df_pills_with_width_length_slot_wise_2["pack_id"][ind]
                                        df_result.loc[i1,"slot_header_id"] = df_pills_with_width_length_slot_wise_2["slot_header_id"][
                                        ind].astype(int)

                                        df_result1 = df_pills_with_width_length_slot_wise[
                                        (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                                         df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                                        (df_pills_with_width_length_slot_wise["length"].astype(float) == numbers[0])]
                                        if not df_result1.empty:
                                            df_result1.reset_index(inplace=True)
                                            drug_ndc1 = df_result1["drug_ndc"][0]
                                            drug_name1 = df_result1["drug_name"][0]

                                        df_result2 = df_pills_with_width_length_slot_wise[
                                        (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                                         df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                                        (df_pills_with_width_length_slot_wise["width"].astype(float) == numbers[1])]
                                        if not df_result2.empty:
                                            df_result2.reset_index(inplace=True)
                                            drug_ndc2 = df_result2["drug_ndc"][0]
                                            drug_name2 = df_result2["drug_name"][0]

                                        df_result3 = df_pills_with_width_length_slot_wise[
                                        (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                                         df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                                        (df_pills_with_width_length_slot_wise["width"].astype(float) == numbers[2])]
                                        if not df_result3.empty:
                                            df_result3.reset_index(inplace=True)
                                            drug_ndc3 = df_result3["drug_ndc"][0]
                                            drug_name3 = df_result3["drug_name"][0]

                                        if not df_result1.empty and not df_result2.empty and not df_result3.empty:
                                            drug_ndc = drug_ndc1 + "," + drug_ndc2 + "," + drug_ndc3
                                            drug_name = drug_name1 + "," + drug_name2 + "," + drug_name3
                                            df_result.loc[i1,"drug_ndc"] = drug_ndc
                                            df_result.loc[i1, "drug_name"] = drug_name
                                            df_result.loc[i1,"length_width_combination"] = str(numbers[0]) + "," + str(numbers[1]) + "," + str(numbers[2])
                                            df_result.loc[i1, "sum"] = sum(numbers)
                                            i1 = i1 + 1
                                            flag = True
                                        else:
                                            df_result.drop(i1, axis=0, inplace=True)
                for i in range(len(width_list)):
                    width_length_list = list()
                    width_length_list.append(width_list[i])
                    for j in range(len(length_list)):
                        if i != j:
                            width_length_list.append(length_list[j])
                            for numbers in itertools.combinations(width_length_list, 2):
                                if not flag:
                                    if min_value <= sum(numbers) <= max_value:
                                        df_result.loc[i1,"pack_id"] = df_pills_with_width_length_slot_wise_2["pack_id"][ind]
                                        df_result.loc[i1,"slot_header_id"] = df_pills_with_width_length_slot_wise_2["slot_header_id"][
                                        ind].astype(int)

                                        df_result1 = df_pills_with_width_length_slot_wise[
                                        (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                                         df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                                        (df_pills_with_width_length_slot_wise["width"].astype(float) == numbers[0])]
                                        if not df_result1.empty:
                                            df_result1.reset_index(inplace=True)
                                            drug_ndc1 = df_result1["drug_ndc"][0]
                                            drug_name1 = df_result1["drug_name"][0]

                                        df_result2 = df_pills_with_width_length_slot_wise[
                                        (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                                         df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                                        (df_pills_with_width_length_slot_wise["length"].astype(float) == numbers[1])]
                                        if not df_result2.empty:
                                            df_result2.reset_index(inplace=True)
                                            drug_ndc2 = df_result2["drug_ndc"][0]
                                            drug_name2 = df_result2["drug_name"][0]
                                        if not df_result1.empty and not df_result2.empty:
                                            drug_ndc = drug_ndc1 + "," + drug_ndc2
                                            drug_name = drug_name1 + "," + drug_name2
                                            df_result.loc[i1,"drug_ndc"] = drug_ndc
                                            df_result.loc[i1, "drug_name"] = drug_name
                                            df_result.loc[i1,"width_length_combination"] = str(numbers[0]) + "," + str(numbers[1])
                                            df_result.loc[i1, "sum"] = sum(numbers)
                                            i1 = i1 + 1
                                            flag=True
                                        else:
                                            df_result.drop(i1,axis=0,inplace=True)
                            for numbers in itertools.combinations(width_length_list, 3):
                                if not flag:
                                    if min_value <= sum(numbers) <= max_value:
                                        df_result.loc[i1,"pack_id"] = df_pills_with_width_length_slot_wise_2["pack_id"][ind]
                                        df_result.loc[i1,"slot_header_id"] = df_pills_with_width_length_slot_wise_2["slot_header_id"][
                                        ind].astype(int)

                                        df_result1 = df_pills_with_width_length_slot_wise[
                                        (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                                         df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                                        (df_pills_with_width_length_slot_wise["width"].astype(float) == numbers[0])]
                                        if not df_result1.empty:
                                            df_result1.reset_index(inplace=True)
                                            drug_ndc1 = df_result1["drug_ndc"][0]
                                            drug_name1 = df_result1["drug_name"][0]

                                        df_result2 = df_pills_with_width_length_slot_wise[
                                        (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                                         df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                                        (df_pills_with_width_length_slot_wise["length"].astype(float) == numbers[1])]
                                        if not df_result2.empty:
                                            df_result2.reset_index(inplace=True)
                                            drug_ndc2 = df_result2["drug_ndc"][0]
                                            drug_name2 = df_result2["drug_name"][0]

                                        df_result3 = df_pills_with_width_length_slot_wise[
                                        (df_pills_with_width_length_slot_wise["slot_header_id"] ==
                                         df_pills_with_width_length_slot_wise_2["slot_header_id"][ind].astype(int)) &
                                        (df_pills_with_width_length_slot_wise["length"].astype(float) == numbers[2])]
                                        if not df_result3.empty:
                                            df_result3.reset_index(inplace=True)
                                            drug_ndc3 = df_result3["drug_ndc"][0]
                                            drug_name3 = df_result3["drug_name"][0]

                                        if not df_result1.empty and not df_result2.empty and not df_result3.empty:
                                            drug_ndc = drug_ndc1 + "," + drug_ndc2 + "," + drug_ndc3
                                            drug_name = drug_name1 + "," + drug_name2 + "," + drug_name3
                                            df_result.loc[i1,"drug_ndc"] = drug_ndc
                                            df_result.loc[i1, "drug_name"] = drug_name
                                            df_result.loc[i1,"width_length_combination"] = str(numbers[0]) + "," + str(numbers[1]) + "," + str(numbers[2])
                                            df_result.loc[i1, "sum"] = sum(numbers)
                                            i1 = i1 + 1
                                            flag = True
                                        else:
                                            df_result.drop(i1, axis=0, inplace=True)
            df_result = df_result.fillna(0)
            decimals = 2
            df_result['sum'] = df_result['sum'].apply(lambda x: round(x, decimals))
            df_result["slot_header_id"] = df_result["slot_header_id"].astype(str)
            df_result = \
            df_result.groupby(['pack_id', 'drug_ndc', 'drug_name', 'length_combination', 'width_combination',
                               'length_width_combination', 'width_length_combination', 'sum'],
                              as_index=False)[["slot_header_id"]].agg(','.join)
            df_result.drop_duplicates(inplace=True)
            dict_result = df_result.to_dict('records')
            response = {'Pill_Combinations': dict_result}
            if response:
                send_email_for_pill_combination_in_given_length_width_range(pill_combination_data=response)
        else:
            response = "There is no data available for this date"
        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_pill_analysis_falling_on_3D_printed_part {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pill_analysis_falling_on_3D_printed_part: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

def get_success_sensor_drug_drop(data_dict):
    """
        Function to get data when required quantity, sensor drug quantity are same and successfully dropped
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        track_date = data_dict.get('track_date')
        number_of_graphs = data_dict.get('number_of_graphs')
        time_zone = settings.TIME_ZONE_MAP[time_zone]

        fndc = data_dict['fndc']
        txr = data_dict['txr']

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        sensor_dropping_data = get_sensor_dropping_data_for_success_sensor_drug_drop(track_date, utc_time_zone_offset)
        if len(sensor_dropping_data) == 0:
            response = {
                'success_drug_data': 0
            }
            return response
        df_sensor_dropping_data = pd.DataFrame(sensor_dropping_data)
        convert_dict = {'fndc': str,
                        'txr': str
                        }

        df_sensor_dropping_data = df_sensor_dropping_data.astype(convert_dict)
        slot_list = df_sensor_dropping_data["slot_id"].values.tolist()
        slot_header_list = df_sensor_dropping_data["slot_header_id"].values.tolist()
        pvs_data = get_pvs_dropping_data(slot_list, slot_header_list)
        df_pvs_dropping_data = pd.DataFrame(pvs_data)

        df_pvs_sensor_dropping_data = df_pvs_dropping_data.merge(df_sensor_dropping_data, on='slot_id', how='left')


        batch_list = df_pvs_sensor_dropping_data["batch_id"].values.tolist()

        # Get pack_affected list remove that pack data from data
        pack_affected_list = get_batch_id_by_action_id(batch_list)

        df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
            ~df_pvs_sensor_dropping_data["pack_id"].isin(pack_affected_list)]

        # Get pack_id and slot_number from pill_jump_error table to remove from output
        list_pack_id_and_slot_number = get_pack_id_and_slot_number(track_date, utc_time_zone_offset)

        df_pvs_sensor_dropping_data["pack_id_slot_number"] = df_pvs_sensor_dropping_data.pack_id.astype(str).str \
            .cat(df_pvs_sensor_dropping_data.slot_number.astype(str), sep=',')

        if len(list_pack_id_and_slot_number):
            df_pack_affected_list = pd.DataFrame(list_pack_id_and_slot_number)

            df_pack_affected_list["pack_id_slot_number"] = df_pack_affected_list.pack_id.astype(str).str \
                .cat(df_pack_affected_list.slot_number.astype(str), sep=',')

            skip_pack_id_slot_number_list = df_pack_affected_list['pack_id_slot_number'].tolist()

            df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
                ~df_pvs_sensor_dropping_data["pack_id_slot_number"].isin(skip_pack_id_slot_number_list)]

        df_pvs_sensor_dropping_data.drop('pack_id_slot_number', axis=1, inplace=True)

        df_pvs_sensor_dropping_data_header_wise = df_pvs_sensor_dropping_data.groupby(['slot_header_id']) \
            .agg({'batch_id': 'last', 'pack_id': 'last',
                  'actual_qty': 'sum',
                  'sensor_drop_quantity': 'sum',
                  'pvs_predicted_qty': 'sum',
                  'pvs_predicted_qty_total': 'last',
                  'sensor_created_date': 'last'}).reset_index()



        df_sensor_success_drop_data = df_pvs_sensor_dropping_data_header_wise[(df_pvs_sensor_dropping_data_header_wise[
                                                                                       "pvs_predicted_qty_total"] ==
                                                                                   df_pvs_sensor_dropping_data_header_wise[
                                                                                       "sensor_drop_quantity"]) & (
                                                                                              df_pvs_sensor_dropping_data_header_wise[
                                                                                                  "actual_qty"] ==
                                                                                              df_pvs_sensor_dropping_data_header_wise[
                                                                                                  "sensor_drop_quantity"])]
        success_slot_header_list = df_sensor_success_drop_data["slot_header_id"].values.tolist()

        # get data for particular fndc ,txr where slot header in success slot header list (i.e. required qty == sensor predicted qty == pvs predicted qty)
        df_success_dropping_data_drug_wise = df_pvs_sensor_dropping_data[
            df_pvs_sensor_dropping_data["slot_header_id"].isin(success_slot_header_list)]
        df_success_dropping_data_for_given_fndc_txr = df_success_dropping_data_drug_wise[
            (df_success_dropping_data_drug_wise["fndc"] == fndc) &
            (df_success_dropping_data_drug_wise["txr"] == txr)]

        success_dropping_data_for_given_fndc_txr_length = len(df_success_dropping_data_for_given_fndc_txr)

        response = {
            "success_drug_data": df_success_dropping_data_for_given_fndc_txr.to_dict('records'),
            "len": success_dropping_data_for_given_fndc_txr_length,
        }

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_manual_drugs_for_imported_batch {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_drugs_for_imported_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def pvs_detection_problem_classification(data_dict):
    """
        Function to pvs detection problem classification for classification
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        track_date = data_dict.get('date')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        system_id = data_dict["system_id"]
        company_id = data_dict["company_id"]
        if track_date is None:
            track_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        # Get Sensor data drug wise and store in dataframe
        pack_verification_status_count, pack_id_in_pack_verification = get_pack_verification_status_count(system_id, company_id, track_date,
                                                             utc_time_zone_offset)

        pack_id_for_sensor_data = []
        for record in pack_id_in_pack_verification:
            pack_id_for_sensor_data.append(record['pack_id'])
        pill_jump_error_count_with_status = get_pill_jump_error_count(pack_id_for_sensor_data)
        for record in pack_verification_status_count:
            if len(pill_jump_error_count_with_status):
                for re in pill_jump_error_count_with_status:
                    if re['pack_verified_status'] == record['pack_verified_status']:
                        record['pill_jump_error_pack'] = re['count']
                        record['pack_without_pill_jump_error'] = record['count']-re['count']
                if 'pill_jump_error_pack' not in record.keys():
                    record['pill_jump_error_pack'] = 0
                    record['pack_without_pill_jump_error'] = record['count']
            else:
                record['pill_jump_error_pack'] = 0
                record['pack_without_pill_jump_error'] = record['count']
        pack_verification_status_count_dict = dict()
        pack_verification_status_count_dict["Total_pack"] = 0
        pack_verification_status_count_dict['Total_pill_jump_error_pack'] = 0
        for record in pack_verification_status_count:
            pack_verification_status_count_dict['pill_jump_error({})'.format(record["value"])] = str(record['pill_jump_error_pack'])
            pack_verification_status_count_dict['pack_without_pill_jump({})'.format(record["value"])] = str(
                record['pack_without_pill_jump_error'])
            pack_verification_status_count_dict["Total_pack"] += record['count']
            pack_verification_status_count_dict['Total_pill_jump_error_pack'] += record['pill_jump_error_pack']

        pack_verification_status_count_dict["Total_pack"] = str(pack_verification_status_count_dict["Total_pack"])
        sensor_dropping_data = get_sensor_dropping_data_for_pvs_classification(system_id, company_id, pack_id_for_sensor_data)
        drug_count = get_drug_wise_count_for_packs(pack_id_for_sensor_data)
        df_drug_count = pd.DataFrame(drug_count)
        df_sensor_dropping_data = pd.DataFrame(sensor_dropping_data)

        if len(sensor_dropping_data) == 0:
            response = {
                "pack_verification_status_count_dict": pack_verification_status_count_dict,
                "data": "No data for {} date".format(track_date)
            }
            return response

        df_sensor_dropping_data_header_wise = df_sensor_dropping_data.groupby(['slot_header_id']) \
            .agg({'pack_id': 'last',
                  'actual_qty': 'sum',
                  'sensor_drop_quantity': 'sum'}).reset_index()

        slot_header_list_for_get_pvs_data = df_sensor_dropping_data_header_wise["slot_header_id"].values.tolist()
        pvs_data_slot_header_wise = get_pvs_data_header_wise(slot_header_list_for_get_pvs_data)
        df_pvs_dropping_data_header_wise = pd.DataFrame(pvs_data_slot_header_wise)
        df_pvs_dropping_data_header_wise.drop_duplicates(subset="slot_header_id",
                                      keep="first", inplace=True)

        # Merge data of sensor and pvs slot header wise
        df_pvs_sensor_dropping_data_header_wise = df_pvs_dropping_data_header_wise.merge(
            df_sensor_dropping_data_header_wise, on='slot_header_id', how='left')

        data_count = dict()
        header_wise_data_count = dict()
        header_wise_data_count["date"] = track_date

        header_wise_data_count['total_slot_header_wise_data'] = len(df_pvs_sensor_dropping_data_header_wise)

        # Slot header wise matched data (i.e. required quantity==pvs_predicted_quantity==sensor_drop_quantity)
        df_matched_data = df_pvs_sensor_dropping_data_header_wise[(df_pvs_sensor_dropping_data_header_wise[
                                                                       "pvs_predicted_qty_total"] ==
                                                                   df_pvs_sensor_dropping_data_header_wise[
                                                                       "actual_qty"]) & (
                                                                          df_pvs_sensor_dropping_data_header_wise[
                                                                              "actual_qty"] ==
                                                                          df_pvs_sensor_dropping_data_header_wise[
                                                                              "sensor_drop_quantity"])]

        header_wise_data_count['matched_data_length'] = len(df_matched_data)
        header_wise_data_count['not_matched_data_length'] = \
            header_wise_data_count['total_slot_header_wise_data'] - header_wise_data_count['matched_data_length']


        # For get pvs slot data and drug status for classification of matched data
        slot_header_match_list = df_matched_data["slot_header_id"].values.tolist()
        if not slot_header_match_list:
            response = {
                "pack_verification_status_count_dict": pack_verification_status_count_dict,
                "data_": "No data found",
            }
            return response
        sub_drop_wise_total_data_drug_wise = get_pvs_slot_data_and_drug_status(slot_header_match_list)
        unregistered_drug_fndc_txr = []
        unregistered_drug_fndc_txr_ = []

        # for unregistered drug list
        for record in sub_drop_wise_total_data_drug_wise:
            if record["status"] == 90:
                if record["fndc_txr"] not in unregistered_drug_fndc_txr:
                    unregistered_drug_fndc_txr.append(record["fndc_txr"])
                    total_count_of_the_day = df_drug_count[df_drug_count['fndc_txr'] ==
                                                                         record["fndc_txr"]]
                    fndc_txr = list(record["fndc_txr"].split("_"))
                    fndc = fndc_txr[0]
                    txr = fndc_txr[1]
                    if total_count_of_the_day is not None:
                        total_count_not_manual = df_sensor_dropping_data.loc[df_sensor_dropping_data['fndc_txr'] ==
                                                                         record["fndc_txr"], 'actual_qty'].sum()
                        if total_count_not_manual:
                            unregistered_drug = {
                                "formatted_ndc": str(fndc),
                                "txr": str(txr),
                                "Total_count_of_the_day": str(total_count_of_the_day['actual_qty'].iloc[0])
                            }
                        else:
                            unregistered_drug = {
                                "formatted_ndc": str(fndc) + "(manual)",
                                "txr": str(txr),
                                "Total_count_of_the_day": str(total_count_of_the_day['actual_qty'].iloc[0])
                            }
                        unregistered_drug_fndc_txr_.append(unregistered_drug)


        unregistered_drug_fndc_txr_.sort(key=lambda x: x['Total_count_of_the_day'], reverse=True)
        df_sub_drop_total_data_drug_wise = pd.DataFrame(sub_drop_wise_total_data_drug_wise)
        df_sub_drop_total_data_drug_wise.sort_values(by='slot_header_id', ascending=True, inplace=True)


        df_sub_drop_total_data_drug_wise["slot_id"] = df_sub_drop_total_data_drug_wise["slot_id"].astype(str)
        df_sub_drop_total_data_drug_wise["unique_drug_id"] = \
            df_sub_drop_total_data_drug_wise["unique_drug_id"].astype(str)
        df_sub_drop_total_data_drug_wise["status"] = df_sub_drop_total_data_drug_wise["status"].astype(str)


        df_sub_drop_wise_total_data = df_sub_drop_total_data_drug_wise.groupby(['slot_header_id', 'quadrant'])\
            .agg({'status': lambda x: ','.join(x), 'unique_drug_id': lambda x: ', '.join(x), 'pvs_slot_id': 'last',
                  'slot_id': lambda x: ', '.join(x), 'fndc_txr': lambda x: ', '.join(x)})
        data_count['sub_drop_wise_total_data'] = len(df_sub_drop_wise_total_data)
        pvs_slot_total = df_sub_drop_wise_total_data["pvs_slot_id"].values.tolist()


        sub_drop_wise_data_of_matched_list = df_sub_drop_wise_total_data.to_dict('records')
        data_count["register_sub_drop_drugs"] = 0
        data_count["dd_confusion"] = 0
        data_count["not_identified"] = 0
        data_count["properly_identified"] = 0
        data_count["not_matched_86"] = 0
        pvs_slot_not_registered = []
        pvs_slot_registered = []
        not_registered_drug = dict()
        not_registered_drug["not_register_sub_drop_drugs"] = 0


        # Check drug status for sub drop registered or not
        for record in sub_drop_wise_data_of_matched_list:
            status = list(record["status"].split(","))
            if str(90) in status:
                pvs_slot_not_registered.append(record['pvs_slot_id'])
                not_registered_drug["not_register_sub_drop_drugs"] += 1

        for li in pvs_slot_total:
            if li not in pvs_slot_not_registered:
                pvs_slot_registered.append(li)

        header_wise_data_count['matched_data_length'] = str(header_wise_data_count['matched_data_length'])
        header_wise_data_count['not_matched_data_length'] = str(header_wise_data_count['not_matched_data_length'])
        header_wise_data_count['total_slot_header_wise_data'] = str(
            header_wise_data_count['total_slot_header_wise_data'])
        # get data of registered sub drop drugs
        if not pvs_slot_registered:
            data_count['sub_drop_wise_total_data'] = str(data_count['sub_drop_wise_total_data'])
            data_count["register_sub_drop_drugs"] = str(data_count["register_sub_drop_drugs"])
            data_count["dd_confusion"] = str(data_count["dd_confusion"])
            data_count["not_identified"] = str(data_count["not_identified"])
            data_count["properly_identified"] = str(data_count["properly_identified"])
            data_count["not_matched_86"] = str(data_count["not_matched_86"])
            for dic in unregistered_drug_fndc_txr_:
                dic["Total_count_of_the_day"] = str(dic["Total_count_of_the_day"])
            response = {
                "pack_verification_status_count_dict": pack_verification_status_count_dict,
                "sub_drop_count_for_unregistered_drug": str(not_registered_drug["not_register_sub_drop_drugs"]),
                "unregistered_drug_fndc_txr": unregistered_drug_fndc_txr_[0:10],
                "header_wise_data_count": header_wise_data_count,
                "data_count": data_count,
            }
            if response:
                send_email_for_pvs_detection_problem_classification(pvs_detection_data=response)
                return response
        pvs_slot_detail_data = get_pvs_slot_details_data_for_pvs_classification(pvs_slot_registered)
        # Check drug status for sub drop registered
        for record in pvs_slot_detail_data:
            pvs_classification_status = list(record["pvs_classification_status"].split(","))
            if str(106) in pvs_classification_status:
                data_count["dd_confusion"] += 1
            elif str(88) in pvs_classification_status:
                data_count["not_identified"] += 1
            elif str(86) in pvs_classification_status:
                data_count["not_matched_86"] += 1
            else:
                data_count["properly_identified"] += 1

        data_count["register_sub_drop_drugs"] = data_count['sub_drop_wise_total_data'] - not_registered_drug[
            'not_register_sub_drop_drugs']

        data_count['sub_drop_wise_total_data'] = str(data_count['sub_drop_wise_total_data'])
        data_count["register_sub_drop_drugs"] = str(data_count["register_sub_drop_drugs"])
        data_count["dd_confusion"] = str(data_count["dd_confusion"])
        data_count["not_identified"] = str(data_count["not_identified"])
        data_count["properly_identified"] = str(data_count["properly_identified"])
        data_count["not_matched_86"] = str(data_count["not_matched_86"])

        for dic in unregistered_drug_fndc_txr_:
            dic["Total_count_of_the_day"] = str(dic["Total_count_of_the_day"])

        response = {
            "pack_verification_status_count_dict": pack_verification_status_count_dict,
            "sub_drop_count_for_unregistered_drug": str(not_registered_drug["not_register_sub_drop_drugs"]),
            "unregistered_drug_fndc_txr": unregistered_drug_fndc_txr_[0:10],
            "header_wise_data_count": header_wise_data_count,
            "data_count": data_count
        }

        if response:
            send_email_for_pvs_detection_problem_classification(pvs_detection_data=response)
            return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in pvs_detection_problem_classification {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in pvs_detection_problem_classification: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_manual_pack_filling_details(data_dict):
    """
        Function to pvs detection problem classification for classification
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        from_date = data_dict.get('from_date')
        to_date = data_dict.get('to_date')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        if to_date is None:
            to_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        # Get Manual PAck assigned by user or partially filled by robot
        manual_pack_assigned_by_user_or_partially_filled_by_robot = get_manual_pack_assigned_by_user_or_partially_filled_by_robot(from_date, to_date,
                                                             utc_time_zone_offset)
        # change_rx_manual_pack_details = get_change_rx_manual_pack_details(track_date, utc_time_zone_offset)

        df_manual_pack_assigned_by_user_or_partially_filled_by_robot = pd.DataFrame(manual_pack_assigned_by_user_or_partially_filled_by_robot)
        df_manual_pack_assigned_by_user_or_partially_filled_by_robot.drop_duplicates(inplace=True)
        manual_pack_id = df_manual_pack_assigned_by_user_or_partially_filled_by_robot['pack_id'].values.tolist()
        done_manual_pack_assigned_by_user_or_partially_filled_by_robot = get_manual_pack_assigned_by_user_and_done_with_from_date_to_date(from_date, to_date, utc_time_zone_offset, manual_pack_id)
        df_done_manual_pack_assigned_by_user_or_partially_filled_by_robot = pd.DataFrame(
            done_manual_pack_assigned_by_user_or_partially_filled_by_robot)
        df_manual_pack_assigned_by_user_or_partially_filled_by_robot = \
            df_manual_pack_assigned_by_user_or_partially_filled_by_robot.merge(
                df_done_manual_pack_assigned_by_user_or_partially_filled_by_robot, on='pack_id', how='left')

        df_manual_pack_assigned_by_user_or_partially_filled_by_robot['pack_analysis_status'] = \
            df_manual_pack_assigned_by_user_or_partially_filled_by_robot['pack_analysis_status'].astype(str)
        df_manual_pack_assigned_by_user_or_partially_filled_by_robot = df_manual_pack_assigned_by_user_or_partially_filled_by_robot.groupby(
            ['pack_id'], as_index=False) \
            .agg({'pack_second_status_id': 'last', 'assigned_to': 'last', 'pack_status_created_date': 'last',
                  'pack_status_id': 'last', 'pack_analysis_id': 'last', 'pack_analysis_status': lambda x: ','.join(x),
                  'change_rx_flag': 'last'})

        df_manual_pack_assigned_by_user_or_partially_filled_by_robot['Total_count'] = np.zeros(len(df_manual_pack_assigned_by_user_or_partially_filled_by_robot))
        df_manual_pack_assigned_by_user_or_partially_filled_by_robot['Done_count'] = np.zeros(
            len(df_manual_pack_assigned_by_user_or_partially_filled_by_robot))
        df_total_count_user_wise = df_manual_pack_assigned_by_user_or_partially_filled_by_robot.groupby(['assigned_to', 'pack_status_created_date'], as_index=False).agg({'Total_count': 'count'})
        df_total_done_count_user_wise = df_manual_pack_assigned_by_user_or_partially_filled_by_robot[df_manual_pack_assigned_by_user_or_partially_filled_by_robot['pack_second_status_id'] == 5]
        df_total_done_count_user_wise = df_total_done_count_user_wise.groupby(['assigned_to', 'pack_status_created_date'], as_index=False).agg({'Done_count': 'count'})
        df_user_wise_total_data = df_total_count_user_wise.merge(
            df_total_done_count_user_wise, on=['assigned_to', 'pack_status_created_date'], how='outer')

        df_change_rx_flag = df_manual_pack_assigned_by_user_or_partially_filled_by_robot[
            df_manual_pack_assigned_by_user_or_partially_filled_by_robot["change_rx_flag"] == True]
        df_change_rx_flag_total_count = df_change_rx_flag.groupby(['assigned_to', 'pack_status_created_date'], as_index=False).agg({'Total_count': 'count'})
        df_change_rx_flag_done_count = df_change_rx_flag[
            df_change_rx_flag['pack_second_status_id'] == 5]
        df_change_rx_flag_done_count = df_change_rx_flag_done_count.groupby(
            ['assigned_to', 'pack_status_created_date'], as_index=False).agg(
            {'Done_count': 'count'})
        df_change_rx_flag_count_data = df_change_rx_flag_done_count.merge(
            df_change_rx_flag_total_count, on=['assigned_to', 'pack_status_created_date'], how='outer')
        df_change_rx_flag_count_data.rename(
            columns={'Total_count': 'Total_count_of_change_Rx', 'Done_count': 'Done_count_of_change_Rx'},
            inplace=True)

        df_manual_pack_assigned_by_user = df_manual_pack_assigned_by_user_or_partially_filled_by_robot[
            (df_manual_pack_assigned_by_user_or_partially_filled_by_robot["pack_status_id"] == settings.MANUAL_PACK_STATUS) &
            (df_manual_pack_assigned_by_user_or_partially_filled_by_robot["change_rx_flag"] == False)]
        df_total_manual_pack_assigned_by_user_count = df_manual_pack_assigned_by_user.groupby(
            ['assigned_to', 'pack_status_created_date'], as_index=False).agg({'Total_count': 'count'})
        df_total_manual_pack_assigned_by_user_marked_done_count = df_manual_pack_assigned_by_user[
            df_manual_pack_assigned_by_user['pack_second_status_id'] == 5]
        df_total_manual_pack_assigned_by_user_marked_done_count = df_total_manual_pack_assigned_by_user_marked_done_count.groupby(['assigned_to','pack_status_created_date'], as_index=False).agg(
            {'Done_count': 'count'})
        df_total_manual_pack_assigned_by_user_data = df_total_manual_pack_assigned_by_user_count.merge(
            df_total_manual_pack_assigned_by_user_marked_done_count, on=['assigned_to', 'pack_status_created_date'], how='outer')
        df_total_manual_pack_assigned_by_user_data.rename(columns={'Total_count': 'Total_count_of_assigned_by_user', 'Done_count': 'Done_count_of_assigned_by_user'}, inplace=True)


        df_manual_pack_assigned_by_user_from_different_modules = df_manual_pack_assigned_by_user[
            df_manual_pack_assigned_by_user["pack_analysis_id"].isnull()]
        df_total_manual_pack_assigned_by_user_from_different_modules = df_manual_pack_assigned_by_user_from_different_modules.groupby(
            ['assigned_to', 'pack_status_created_date'], as_index=False).agg({'Total_count': 'count'})
        df_done_manual_pack_assigned_by_user_from_different_modules = df_manual_pack_assigned_by_user_from_different_modules[
            df_manual_pack_assigned_by_user_from_different_modules['pack_second_status_id'] == 5]
        df_done_manual_pack_assigned_by_user_from_different_modules = df_done_manual_pack_assigned_by_user_from_different_modules.groupby(
            ['assigned_to', 'pack_status_created_date'], as_index=False).agg(
            {'Done_count': 'count'})
        df_total_manual_pack_assigned_by_user_from_different_module_data = df_total_manual_pack_assigned_by_user_from_different_modules.merge(
            df_done_manual_pack_assigned_by_user_from_different_modules, on=['assigned_to', 'pack_status_created_date'], how='outer')


        df_manual_pack_assigned_by_user_due_to_recommendations_or_pack_queue = df_manual_pack_assigned_by_user[
            df_manual_pack_assigned_by_user["pack_analysis_id"].isnull() == False]
        df_manual_pack_assigned_by_user_due_to_recommendations = df_manual_pack_assigned_by_user_due_to_recommendations_or_pack_queue[
            df_manual_pack_assigned_by_user_due_to_recommendations_or_pack_queue["pack_analysis_status"].str.contains('229')]
        df_total_manual_pack_assigned_by_user_due_to_recommendations = df_manual_pack_assigned_by_user_due_to_recommendations.groupby(
            ['assigned_to', 'pack_status_created_date'], as_index=False).agg({'Total_count': 'count'})
        df_done_manual_pack_assigned_by_user_due_to_recommendations = df_manual_pack_assigned_by_user_due_to_recommendations[
            df_manual_pack_assigned_by_user_due_to_recommendations['pack_second_status_id']==5]
        df_done_manual_pack_assigned_by_user_due_to_recommendations = df_done_manual_pack_assigned_by_user_due_to_recommendations.groupby(
            ['assigned_to','pack_status_created_date'], as_index=False).agg(
            {'Done_count': 'count'})
        df_total_manual_pack_assigned_by_user_due_to_recommendations_data = df_total_manual_pack_assigned_by_user_due_to_recommendations.merge(
            df_done_manual_pack_assigned_by_user_due_to_recommendations, on=['assigned_to', 'pack_status_created_date'], how='outer')
        df_total_manual_pack_assigned_by_user_due_to_recommendations_data.rename(
            columns={'Total_count': 'Total_count_of_assigned_by_user_due_to_recommendation', 'Done_count': 'Done_count_of_assigned_by_user_due_to_recommendation' },
            inplace=True)


        df_manual_pack_assigned_by_user_in_pack_queue_module = df_manual_pack_assigned_by_user_due_to_recommendations_or_pack_queue[
            ~df_manual_pack_assigned_by_user_due_to_recommendations_or_pack_queue["pack_analysis_status"].str.contains('229')]
        df_total_manual_pack_assigned_by_user_in_pack_queue_module = df_manual_pack_assigned_by_user_in_pack_queue_module.groupby(
            ['assigned_to','pack_status_created_date'], as_index=False).agg({'Total_count': 'count'})
        df_done_manual_pack_assigned_by_user_in_pack_queue_module = \
        df_manual_pack_assigned_by_user_in_pack_queue_module[
            df_manual_pack_assigned_by_user_in_pack_queue_module['pack_second_status_id'] == 5]
        df_done_manual_pack_assigned_by_user_in_pack_queue_module = df_done_manual_pack_assigned_by_user_in_pack_queue_module.groupby(
            ['assigned_to','pack_status_created_date'], as_index=False).agg(
            {'Done_count': 'count'})
        df_total_manual_pack_assigned_by_user_in_pack_queue_module_data = df_total_manual_pack_assigned_by_user_in_pack_queue_module.merge(
            df_done_manual_pack_assigned_by_user_in_pack_queue_module, on=['assigned_to', 'pack_status_created_date'], how='outer')
        df_total_manual_pack_assigned_by_user_from_different_module_data_or_pack_queue_module_data = pd.concat([df_total_manual_pack_assigned_by_user_in_pack_queue_module_data,df_total_manual_pack_assigned_by_user_from_different_module_data], axis=0)
        df_total_manual_pack_assigned_by_user_from_different_module_data_or_pack_queue_module_data = df_total_manual_pack_assigned_by_user_from_different_module_data_or_pack_queue_module_data.groupby(
            ['assigned_to', 'pack_status_created_date'], as_index=False).agg({'Total_count': 'sum', 'Done_count': 'sum'})
        df_total_manual_pack_assigned_by_user_from_different_module_data_or_pack_queue_module_data.rename(
            columns={'Total_count': 'Total_count_of_assigned_by_user_from_different_module',
                     'Done_count': 'Done_count_of_assigned_by_user_from_different_module' },
            inplace=True)
        df_total_manual_pack_assigned_by_user_data = df_total_manual_pack_assigned_by_user_data.merge(
                                                     df_total_manual_pack_assigned_by_user_from_different_module_data_or_pack_queue_module_data,on=['assigned_to', 'pack_status_created_date'], how='outer')
        df_total_manual_pack_assigned_by_user_data = df_total_manual_pack_assigned_by_user_data.merge(
            df_total_manual_pack_assigned_by_user_due_to_recommendations_data,
            on=['assigned_to', 'pack_status_created_date'], how='outer')

        df_manual_pack_partially_filled_by_robot = df_manual_pack_assigned_by_user_or_partially_filled_by_robot[
            (df_manual_pack_assigned_by_user_or_partially_filled_by_robot[
                "pack_status_id"] == settings.PARTIALLY_FILLED_BY_ROBOT) &
            (df_manual_pack_assigned_by_user_or_partially_filled_by_robot["change_rx_flag"] == False)]
        df_total_manual_pack_partially_filled_by_robot = df_manual_pack_partially_filled_by_robot.groupby(
            ['assigned_to','pack_status_created_date'], as_index=False).agg({'Total_count': 'count'})
        df_done_manual_pack_partially_filled_by_robot = \
            df_manual_pack_partially_filled_by_robot[
                df_manual_pack_partially_filled_by_robot['pack_second_status_id'] == 5]
        df_done_manual_pack_partially_filled_by_robot = df_done_manual_pack_partially_filled_by_robot.groupby(
            ['assigned_to','pack_status_created_date'], as_index=False).agg(
            {'Done_count': 'count'})
        df_total_manual_pack_partially_filled_by_robot_data = df_total_manual_pack_partially_filled_by_robot.merge(
            df_done_manual_pack_partially_filled_by_robot, on=['assigned_to', 'pack_status_created_date'], how='outer')
        df_total_manual_pack_partially_filled_by_robot_data.rename(
            columns={'Total_count': 'Total_count_of_manual_pack_partially_filled_by_robot',
                     'Done_count': 'Done_count_of_manual_pack_partially_filled_by_robot'},
            inplace=True)
        df_user_wise_total_data.sort_values(by='pack_status_created_date', ascending=True, inplace=True)
        df_user_wise_total_data.fillna(0, inplace=True)
        df_user_wise_total_data['Not_done_count'] = df_user_wise_total_data['Total_count'] - df_user_wise_total_data['Done_count']
        df_user_wise_total_data['Not_done_count'] = df_user_wise_total_data['Total_count'] - df_user_wise_total_data[
            'Done_count']
        convert_dict = {'assigned_to': int,
                        'Total_count': int,
                        'Done_count': int,
                        'Not_done_count': int
                        }
        df_user_wise_total_data = df_user_wise_total_data.astype(convert_dict)
        convert_dict = {'assigned_to': str,
                        'Total_count': str,
                        'Done_count': str,
                        'Not_done_count': str
                        }
        df_user_wise_total_data = df_user_wise_total_data.astype(convert_dict)
        df_total_manual_pack_partially_filled_by_robot_data.sort_values(by='pack_status_created_date', ascending=True,inplace=True)
        df_total_manual_pack_partially_filled_by_robot_data.fillna(0, inplace=True)
        df_total_manual_pack_partially_filled_by_robot_data['Not_done_count_of_manual_pack_partially_filled_by_robot'] = \
            df_total_manual_pack_partially_filled_by_robot_data['Total_count_of_manual_pack_partially_filled_by_robot'] - \
            df_total_manual_pack_partially_filled_by_robot_data['Done_count_of_manual_pack_partially_filled_by_robot']
        convert_dict = {'assigned_to': int,
                        'Total_count_of_manual_pack_partially_filled_by_robot': int,
                        'Done_count_of_manual_pack_partially_filled_by_robot': int,
                        'Not_done_count_of_manual_pack_partially_filled_by_robot': int
                        }
        df_total_manual_pack_partially_filled_by_robot_data = df_total_manual_pack_partially_filled_by_robot_data.astype(
            convert_dict)
        convert_dict = {'assigned_to': str,
                        'Total_count_of_manual_pack_partially_filled_by_robot': str,
                        'Done_count_of_manual_pack_partially_filled_by_robot': str,
                        'Not_done_count_of_manual_pack_partially_filled_by_robot': str
                        }
        df_total_manual_pack_partially_filled_by_robot_data = df_total_manual_pack_partially_filled_by_robot_data.astype(convert_dict)
        df_total_manual_pack_assigned_by_user_data.sort_values(by='pack_status_created_date', ascending=True,inplace=True)
        df_total_manual_pack_assigned_by_user_data.fillna(0, inplace=True)
        df_total_manual_pack_assigned_by_user_data['Not_done_count_of_assigned_by_user_from_different_module'] = df_total_manual_pack_assigned_by_user_data['Total_count_of_assigned_by_user_from_different_module'] - \
                                                                       df_total_manual_pack_assigned_by_user_data['Done_count_of_assigned_by_user_from_different_module']
        df_total_manual_pack_assigned_by_user_data['Not_done_count_of_assigned_by_user_due_to_recommendation'] = \
        df_total_manual_pack_assigned_by_user_data['Total_count_of_assigned_by_user_due_to_recommendation'] - \
        df_total_manual_pack_assigned_by_user_data['Done_count_of_assigned_by_user_due_to_recommendation']
        df_total_manual_pack_assigned_by_user_data['Not_done_count_of_assigned_by_user'] = \
            df_total_manual_pack_assigned_by_user_data['Total_count_of_assigned_by_user'] - \
            df_total_manual_pack_assigned_by_user_data['Done_count_of_assigned_by_user']
        convert_dict = {'assigned_to': int,
                        'Total_count_of_assigned_by_user_from_different_module': int,
                        'Done_count_of_assigned_by_user_from_different_module': int,
                        'Not_done_count_of_assigned_by_user_from_different_module': int,
                        'Total_count_of_assigned_by_user_due_to_recommendation': int,
                        'Done_count_of_assigned_by_user_due_to_recommendation': int,
                        'Not_done_count_of_assigned_by_user_due_to_recommendation': int,
                        'Total_count_of_assigned_by_user': int,
                        'Done_count_of_assigned_by_user': int,
                        'Not_done_count_of_assigned_by_user': int
                        }
        df_total_manual_pack_assigned_by_user_data = df_total_manual_pack_assigned_by_user_data.astype(convert_dict)
        convert_dict = {'assigned_to': str,
                        'Total_count_of_assigned_by_user_from_different_module': str,
                        'Done_count_of_assigned_by_user_from_different_module': str,
                        'Not_done_count_of_assigned_by_user_from_different_module': str,
                        'Total_count_of_assigned_by_user_due_to_recommendation': str,
                        'Done_count_of_assigned_by_user_due_to_recommendation': str,
                        'Not_done_count_of_assigned_by_user_due_to_recommendation': str,
                        'Total_count_of_assigned_by_user': str,
                        'Done_count_of_assigned_by_user': str,
                        'Not_done_count_of_assigned_by_user': str
                        }
        df_total_manual_pack_assigned_by_user_data = df_total_manual_pack_assigned_by_user_data.astype(convert_dict)
        df_change_rx_flag_count_data.sort_values(by='pack_status_created_date', ascending=True,inplace=True)
        df_change_rx_flag_count_data.fillna(0, inplace=True)
        df_change_rx_flag_count_data['Not_done_count_of_change_Rx'] = df_change_rx_flag_count_data['Total_count_of_change_Rx'] - df_change_rx_flag_count_data[
            'Done_count_of_change_Rx']
        convert_dict = {'assigned_to': int,
                        'Total_count_of_change_Rx': int,
                        'Done_count_of_change_Rx': int,
                        'Not_done_count_of_change_Rx': int,
                        }
        df_change_rx_flag_count_data = df_change_rx_flag_count_data.astype(convert_dict)
        convert_dict = {'assigned_to': str,
                        'Total_count_of_change_Rx': str,
                        'Done_count_of_change_Rx': str,
                        'Not_done_count_of_change_Rx': str,
                        }
        df_change_rx_flag_count_data = df_change_rx_flag_count_data.astype(convert_dict)
        response = {
            'user_wise_manual_packs_count': df_user_wise_total_data.to_dict('records'),
            'user_wise_manual_packs_count_assigned_by_user': df_total_manual_pack_assigned_by_user_data.to_dict('records'),
            'user_wise_manual_packs_count_partially_filled_by_robot': df_total_manual_pack_partially_filled_by_robot_data.to_dict('records'),
            'user_wise_manual_packs_change_rx_count': df_change_rx_flag_count_data.to_dict('records')
        }
        data_file = open('user_wise_manual_packs_count_2.csv', 'w', newline='')
        csv_writer = csv.writer(data_file)

        count = 0
        for data in response['user_wise_manual_packs_count']:
            if count == 0:
                header = data.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(data.values())

        data_file.close()

        data_file = open('user_wise_manual_packs_count_assigned_by_user_2.csv', 'w', newline='')
        csv_writer = csv.writer(data_file)

        count = 0
        for data in response['user_wise_manual_packs_count_assigned_by_user']:
            if count == 0:
                header = data.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(data.values())

        data_file.close()

        data_file = open('user_wise_manual_packs_count_partially_filled_by_robot_2.csv', 'w', newline='')
        csv_writer = csv.writer(data_file)

        count = 0
        for data in response['user_wise_manual_packs_count_partially_filled_by_robot']:
            if count == 0:
                header = data.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(data.values())

        data_file.close()

        data_file = open('user_wise_manual_packs_change_rx_count_2.csv', 'w', newline='')
        csv_writer = csv.writer(data_file)

        count = 0
        for data in response['user_wise_manual_packs_change_rx_count']:
            if count == 0:
                header = data.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(data.values())

        data_file.close()


        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in pvs_detection_problem_classification {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in pvs_detection_problem_classification: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def get_csv_data_for_sensor_error(data_dict):
    """
        Function to get sensor error data for csv
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        track_date = data_dict.get('date')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        system_id = data_dict["system_id"]
        company_id = data_dict["company_id"]
        if track_date is None:
            track_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        sensor_dropping_data = get_sensor_dropping_data_for_csv(system_id, company_id, track_date, utc_time_zone_offset)
        if len(sensor_dropping_data) == 0:
            response = {
                "sensor_error_data": 0
            }
            return response
        df_sensor_dropping_data = pd.DataFrame(sensor_dropping_data)

        slot_list = df_sensor_dropping_data["slot_id"].values.tolist()
        slot_header_list = df_sensor_dropping_data["slot_header_id"].values.tolist()
        pvs_data = get_pvs_dropping_data_for_csv(slot_list, slot_header_list)
        df_pvs_dropping_data = pd.DataFrame(pvs_data)

        df_pvs_sensor_dropping_data = df_pvs_dropping_data.merge(df_sensor_dropping_data, on='slot_id', how='left')

        batch_list = df_pvs_sensor_dropping_data["batch_id"].values.tolist()

        # Get pack_affected list remove that pack data from data
        pack_affected_list = get_batch_id_by_action_id(batch_list)

        df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
            ~df_pvs_sensor_dropping_data["pack_id"].isin(pack_affected_list)]

        # Get pack_id and slot_number from pill_jump_error table to remove from output
        list_pack_id_and_slot_number = get_pack_id_and_slot_number(track_date, utc_time_zone_offset)

        df_pvs_sensor_dropping_data["pack_id_slot_number"] = df_pvs_sensor_dropping_data.pack_id.astype(str).str \
            .cat(df_pvs_sensor_dropping_data.slot_number.astype(str), sep=',')

        if len(list_pack_id_and_slot_number):
            df_pack_affected_list = pd.DataFrame(list_pack_id_and_slot_number)

            df_pack_affected_list["pack_id_slot_number"] = df_pack_affected_list.pack_id.astype(str).str \
                .cat(df_pack_affected_list.slot_number.astype(str), sep=',')

            skip_pack_id_slot_number_list = df_pack_affected_list['pack_id_slot_number'].tolist()

            df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
                ~df_pvs_sensor_dropping_data["pack_id_slot_number"].isin(skip_pack_id_slot_number_list)]


        df_pvs_sensor_dropping_data.drop('pack_id_slot_number', axis=1, inplace=True)

        df_pvs_sensor_dropping_data['file_number'] = df_pvs_sensor_dropping_data['pack_id'].astype(str) + \
                                                     df_pvs_sensor_dropping_data['drop_number'].astype(str) + \
                                                     df_pvs_sensor_dropping_data['config_id'].astype(str)

        df_pvs_sensor_dropping_data_drug_wise = df_pvs_sensor_dropping_data


        df_pvs_sensor_dropping_data_header_wise = df_pvs_sensor_dropping_data.groupby(['slot_header_id']) \
            .agg({'batch_id': 'last', 'pack_id': 'last',
                  'actual_qty': 'sum',
                  'sensor_drop_quantity': 'sum',
                  'pvs_predicted_qty_total': 'last'}).reset_index()


        df_sensor_error_data = df_pvs_sensor_dropping_data_header_wise[df_pvs_sensor_dropping_data_header_wise[
                                                                           "pvs_predicted_qty_total"] !=
                                                                       df_pvs_sensor_dropping_data_header_wise[
                                                                           "sensor_drop_quantity"]]
        df_sensor_error_data = df_sensor_error_data[df_sensor_error_data[
                                                        "actual_qty"] !=
                                                    df_sensor_error_data[
                                                        "sensor_drop_quantity"]]

        # Slot header list of sensor error
        error_slot_header = df_sensor_error_data["slot_header_id"].values.tolist()
        df_pvs_sensor_dropping_data.drop(['pvs_predicted_qty_total', 'slot_number', 'batch_id', "canister_id", 'config_id', 'drop_number', 'pack_id', 'slot_id', 'drug_image', 'image_name'], axis=1, inplace=True)
        drug_data = df_pvs_sensor_dropping_data_drug_wise.to_dict('records')
        for record in drug_data:
            if record['actual_qty'] != record['sensor_drop_quantity'] and record['slot_header_id'] in error_slot_header:
                record["sensor_error"] = "Yes"
            else:
                record["sensor_error"] = "No"

        df_drug_data = pd.DataFrame(drug_data)
        df_error_data = df_drug_data[df_drug_data['sensor_error'] == "Yes"]
        df_error_data.drop_duplicates(inplace=True)
        # df_error_data.drop(['actual_qty', 'sensor_drop_quantity'], axis=1, inplace=True)
        error_data = df_error_data.to_dict('records')

        response = {
            "drug_data": df_drug_data.to_dict('records'),
            "sensor_error_data": error_data,
        }

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_csv_data_for_sensor_error {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_csv_data_for_sensor_error: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_drug_data_for_graph_regeneration(data_dict):
    """
        Function to get sensor error data for csv
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        track_date = data_dict.get('date')
        fndc = data_dict.get('fndc')
        txr = data_dict.get('txr')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        system_id = data_dict["system_id"]
        company_id = data_dict["company_id"]
        if track_date is None:
            track_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        sensor_dropping_data = get_sensor_dropping_data_for_csv(system_id, company_id, track_date, utc_time_zone_offset)
        if len(sensor_dropping_data) == 0:
            response = {
                "sensor_error_data": 0
            }
            return response
        df_sensor_dropping_data = pd.DataFrame(sensor_dropping_data)

        slot_list = df_sensor_dropping_data["slot_id"].values.tolist()
        slot_header_list = df_sensor_dropping_data["slot_header_id"].values.tolist()
        pvs_data = get_pvs_dropping_data_for_csv(slot_list, slot_header_list)
        df_pvs_dropping_data = pd.DataFrame(pvs_data)

        df_pvs_sensor_dropping_data = df_pvs_dropping_data.merge(df_sensor_dropping_data, on='slot_id', how='left')

        batch_list = df_pvs_sensor_dropping_data["batch_id"].values.tolist()

        # Get pack_affected list remove that pack data from data
        pack_affected_list = get_batch_id_by_action_id(batch_list)

        df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
            ~df_pvs_sensor_dropping_data["pack_id"].isin(pack_affected_list)]

        # Get pack_id and slot_number from pill_jump_error table to remove from output
        list_pack_id_and_slot_number = get_pack_id_and_slot_number(track_date, utc_time_zone_offset)

        df_pvs_sensor_dropping_data["pack_id_slot_number"] = df_pvs_sensor_dropping_data.pack_id.astype(str).str \
            .cat(df_pvs_sensor_dropping_data.slot_number.astype(str), sep=',')

        if len(list_pack_id_and_slot_number):
            df_pack_affected_list = pd.DataFrame(list_pack_id_and_slot_number)

            df_pack_affected_list["pack_id_slot_number"] = df_pack_affected_list.pack_id.astype(str).str \
                .cat(df_pack_affected_list.slot_number.astype(str), sep=',')

            skip_pack_id_slot_number_list = df_pack_affected_list['pack_id_slot_number'].tolist()

            df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
                ~df_pvs_sensor_dropping_data["pack_id_slot_number"].isin(skip_pack_id_slot_number_list)]


        df_pvs_sensor_dropping_data.drop('pack_id_slot_number', axis=1, inplace=True)

        df_pvs_sensor_dropping_data['file_number'] = df_pvs_sensor_dropping_data['pack_id'].astype(str) + \
                                                     df_pvs_sensor_dropping_data['drop_number'].astype(str) + \
                                                     df_pvs_sensor_dropping_data['config_id'].astype(str)

        df_pvs_sensor_dropping_data_drug_wise = df_pvs_sensor_dropping_data


        df_pvs_sensor_dropping_data_header_wise = df_pvs_sensor_dropping_data.groupby(['slot_header_id']) \
            .agg({'batch_id': 'last', 'pack_id': 'last',
                  'actual_qty': 'sum',
                  'sensor_drop_quantity': 'sum',
                  'pvs_predicted_qty_total': 'last'}).reset_index()


        df_sensor_error_data = df_pvs_sensor_dropping_data_header_wise[df_pvs_sensor_dropping_data_header_wise[
                                                                           "pvs_predicted_qty_total"] !=
                                                                       df_pvs_sensor_dropping_data_header_wise[
                                                                           "sensor_drop_quantity"]]
        df_sensor_error_data = df_sensor_error_data[df_sensor_error_data[
                                                        "actual_qty"] !=
                                                    df_sensor_error_data[
                                                        "sensor_drop_quantity"]]

        # Slot header list of sensor error
        error_slot_header = df_sensor_error_data["slot_header_id"].values.tolist()
        df_pvs_sensor_dropping_data.drop(['pvs_predicted_qty_total', 'slot_number', 'batch_id', "canister_id", 'config_id', 'drop_number', 'pack_id', 'slot_id'], axis=1, inplace=True)
        drug_data = df_pvs_sensor_dropping_data_drug_wise.to_dict('records')
        for record in drug_data:
            if record['actual_qty'] != record['sensor_drop_quantity'] and record['slot_header_id']:
                record["sensor_error"] = "Yes"
            else:
                record["sensor_error"] = "No"

        df_drug_data = pd.DataFrame(drug_data)
        df_error_data = df_drug_data[(df_drug_data['sensor_error'] == "Yes") & (df_drug_data['fndc'] == fndc) & (df_drug_data['txr'] == txr)]
        df_success_data = df_drug_data[(df_drug_data['sensor_error'] == "No") & (df_drug_data['fndc'] == fndc) & (df_drug_data['txr'] == txr)]
        df_error_data.drop_duplicates(subset="slot_header_id",
                             keep="first", inplace=True)
        df_success_data.drop_duplicates(subset="slot_header_id",
                                      keep="first", inplace=True)
        # df_error_data.drop(['actual_qty', 'sensor_drop_quantity'], axis=1, inplace=True)
        error_data = df_error_data.to_dict('records')
        success_record = df_success_data.to_dict('records')

        response = {
            "drug_data": df_drug_data.to_dict('records'),
            "sensor_error_data": error_data,
            "success_record": success_record
        }

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_csv_data_for_sensor_error {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_csv_data_for_sensor_error: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def get_manual_pack_filling_details_for_analyzer(data_dict):
    """
        Function to get_manual_pack_filling_details_for_analyzer
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        track_date = data_dict.get('date')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        if track_date is None:
            track_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)

        # Get Manual PAck assigned by user or partially filled by robot
        manual_pack_assigned_by_user_or_partially_filled_by_robot = \
            get_manual_pack_assigned_by_user_or_partially_filled_by_robot_for_analyzer(
                track_date,
                utc_time_zone_offset)

        if not manual_pack_assigned_by_user_or_partially_filled_by_robot:
            response = {
                'track_date': track_date,
                "total_manual_pack": 0,
                "manual_pack_details": {}
            }
            return response
        df_manual_pack_assigned_by_user_or_partially_filled_by_robot = pd.DataFrame(
            manual_pack_assigned_by_user_or_partially_filled_by_robot)
        df_manual_pack_assigned_by_user_or_partially_filled_by_robot.drop_duplicates(subset="pack_id",
                                                                                     keep="first", inplace=True)
        df_manual_pack_assigned_by_user_or_partially_filled_by_robot.fillna(0, inplace=True)

        df_manual_pack_assigned_by_user_or_partially_filled_by_robot.loc[
            (df_manual_pack_assigned_by_user_or_partially_filled_by_robot.pack_status_id ==
             settings.MANUAL_PACK_STATUS) & (
                    df_manual_pack_assigned_by_user_or_partially_filled_by_robot.change_rx_flag ==
                    False) & (
                    df_manual_pack_assigned_by_user_or_partially_filled_by_robot.pack_analysis_id == 0),
            'manual_pack_category'] = "manual_pack_assigned_by_user"

        df_manual_pack_assigned_by_user_or_partially_filled_by_robot.loc[
            (df_manual_pack_assigned_by_user_or_partially_filled_by_robot.pack_status_id ==
             settings.PARTIALLY_FILLED_BY_ROBOT), 'manual_pack_category'] = "partially_filled_by_robot"

        df_manual_pack_assigned_by_user_or_partially_filled_by_robot.loc[
            (df_manual_pack_assigned_by_user_or_partially_filled_by_robot.pack_status_id ==
             settings.MANUAL_PACK_STATUS) & (
                    df_manual_pack_assigned_by_user_or_partially_filled_by_robot.change_rx_flag ==
                    False) & (
                    df_manual_pack_assigned_by_user_or_partially_filled_by_robot.pack_analysis_id != 0)
            & (df_manual_pack_assigned_by_user_or_partially_filled_by_robot.batch_manual_pack_id != 0),
            'manual_pack_category'] = "manual_pack_due_to_flow"

        df_manual_pack_assigned_by_user_or_partially_filled_by_robot.loc[
            (df_manual_pack_assigned_by_user_or_partially_filled_by_robot.pack_status_id ==
             settings.MANUAL_PACK_STATUS) & (
                    df_manual_pack_assigned_by_user_or_partially_filled_by_robot.change_rx_flag ==
                    False) & (
                    df_manual_pack_assigned_by_user_or_partially_filled_by_robot.pack_analysis_id != 0)
            & (df_manual_pack_assigned_by_user_or_partially_filled_by_robot.batch_manual_pack_id == 0),
            'manual_pack_category'] = "manual_pack_assigned_by_user"

        df_manual_pack_assigned_by_user_or_partially_filled_by_robot.loc[
            (df_manual_pack_assigned_by_user_or_partially_filled_by_robot.pack_status_id ==
             settings.MANUAL_PACK_STATUS) &
            (df_manual_pack_assigned_by_user_or_partially_filled_by_robot.change_rx_flag ==
             True), 'manual_pack_category'] = "manual_pack_after_change_rx"

        table = pd.pivot_table(df_manual_pack_assigned_by_user_or_partially_filled_by_robot, index=["created_by"],
                               columns=["manual_pack_category"],
                               aggfunc={"manual_pack_category": np.count_nonzero})

        table.columns = ['_'.join(str(s).strip() for s in col if s) for col in table.columns]
        table.reset_index(inplace=True)

        table.fillna(0, inplace=True)

        sum = table.sum()
        sum.name = "Sum"
        table = table.append(sum.transpose())

        table["user_wise_sum"] = table.drop('created_by', axis=1).sum(axis=1)
        if "manual_pack_category_manual_pack_after_change_rx" in table:
            table["manual_pack_category_manual_pack_after_change_rx"] = table[
                "manual_pack_category_manual_pack_after_change_rx"].astype(int).astype(str)
        else:
            table["manual_pack_category_manual_pack_after_change_rx"] = 0
        if "manual_pack_category_manual_pack_assigned_by_user" in table:
            table["manual_pack_category_manual_pack_assigned_by_user"] = table[
                "manual_pack_category_manual_pack_assigned_by_user"].astype(int).astype(str)
        else:
            table["manual_pack_category_manual_pack_assigned_by_user"] = 0
        if "manual_pack_category_partially_filled_by_robot" in table:
            table["manual_pack_category_partially_filled_by_robot"] = table[
                "manual_pack_category_partially_filled_by_robot"].astype(int).astype(str)
        else:
            table["manual_pack_category_partially_filled_by_robot"] = 0
        if "manual_pack_category_manual_pack_due_to_flow" in table:
            table["manual_pack_category_manual_pack_due_to_flow"] = table[
                "manual_pack_category_manual_pack_due_to_flow"].astype(int).astype(str)
        else:
            table["manual_pack_category_manual_pack_due_to_flow"] = 0
        table["created_by"] = table["created_by"].astype(int).astype(str)
        table["user_wise_sum"] = table["user_wise_sum"].astype(int).astype(str)
        table["created_by"].iloc[-1] = "category_wise_sum"
        total_manual_pack = table["user_wise_sum"].iloc[-1]

        response = {"total_manual_pack": total_manual_pack, "manual_pack_details": table.to_dict('records'),
                    "track_date": track_date}
        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_manual_pack_filling_details_for_analyzer {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_pack_filling_details_for_analyzer: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def get_sensor_error_count_robot_wise(data_dict):
    """
        Function to get sensor error count robot wise
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        if time_zone is None:
            time_zone = "PST"
        track_date = data_dict.get('date')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        system_id = 14
        company_id = 3
        if track_date is None:
            track_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        sensor_dropping_data = get_sensor_dropping_data_for_csv(system_id, company_id, track_date, utc_time_zone_offset)
        df_sensor_dropping_data = pd.DataFrame(sensor_dropping_data)

        slot_list = df_sensor_dropping_data["slot_id"].values.tolist()
        slot_header_list = df_sensor_dropping_data["slot_header_id"].values.tolist()
        pvs_data = get_pvs_dropping_data_for_csv(slot_list, slot_header_list)
        df_pvs_dropping_data = pd.DataFrame(pvs_data)

        df_pvs_sensor_dropping_data = df_pvs_dropping_data.merge(df_sensor_dropping_data, on='slot_id', how='left')
        if len(sensor_dropping_data) == 0:
            response = {
                "pvs_sensor_dropping_data_drug_wise": 0,
                "pvs_sensor_dropping_data_header_wise": 0,
                "sensor_error_data": 0,
                "number_of_data_dict": 0,
            }
            return response

        batch_list = df_pvs_sensor_dropping_data["batch_id"].values.tolist()

        # Get pack_affected list remove that pack data from data
        pack_affected_list = get_batch_id_by_action_id(batch_list)

        df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
            ~df_pvs_sensor_dropping_data["pack_id"].isin(pack_affected_list)]

        # Get pack_id and slot_number from pill_jump_error table to remove from output
        list_pack_id_and_slot_number = get_pack_id_and_slot_number(track_date, utc_time_zone_offset)

        df_pvs_sensor_dropping_data["pack_id_slot_number"] = df_pvs_sensor_dropping_data.pack_id.astype(str).str \
            .cat(df_pvs_sensor_dropping_data.slot_number.astype(str), sep=',')

        if len(list_pack_id_and_slot_number):
            df_pack_affected_list = pd.DataFrame(list_pack_id_and_slot_number)

            df_pack_affected_list["pack_id_slot_number"] = df_pack_affected_list.pack_id.astype(str).str \
                .cat(df_pack_affected_list.slot_number.astype(str), sep=',')

            skip_pack_id_slot_number_list = df_pack_affected_list['pack_id_slot_number'].tolist()

            df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
                ~df_pvs_sensor_dropping_data["pack_id_slot_number"].isin(skip_pack_id_slot_number_list)]


        df_pvs_sensor_dropping_data.drop('pack_id_slot_number', axis=1, inplace=True)

        df_pvs_sensor_dropping_data['file_number'] = df_pvs_sensor_dropping_data['pack_id'].astype(str) + \
                                                     df_pvs_sensor_dropping_data['drop_number'].astype(str) + \
                                                     df_pvs_sensor_dropping_data['config_id'].astype(str)

        df_pvs_sensor_dropping_data_drug_wise = df_pvs_sensor_dropping_data


        df_pvs_sensor_dropping_data_header_wise = df_pvs_sensor_dropping_data.groupby(['slot_header_id']) \
            .agg({'batch_id': 'last', 'pack_id': 'last',
                  'actual_qty': 'sum',
                  'sensor_drop_quantity': 'sum',
                  'pvs_predicted_qty_total': 'last'}).reset_index()


        df_sensor_error_data = df_pvs_sensor_dropping_data_header_wise[df_pvs_sensor_dropping_data_header_wise[
                                                                           "pvs_predicted_qty_total"] !=
                                                                       df_pvs_sensor_dropping_data_header_wise[
                                                                           "sensor_drop_quantity"]]
        df_sensor_error_data = df_sensor_error_data[df_sensor_error_data[
                                                        "actual_qty"] !=
                                                    df_sensor_error_data[
                                                        "sensor_drop_quantity"]]

        # Slot header list of sensor error
        error_slot_header = df_sensor_error_data["slot_header_id"].values.tolist()
        df_pvs_sensor_dropping_data.drop(['pvs_predicted_qty_total', 'slot_number', 'batch_id', "canister_id", 'config_id', 'drop_number', 'slot_id', 'drug_image', 'image_name'], axis=1, inplace=True)
        drug_data = df_pvs_sensor_dropping_data_drug_wise.to_dict('records')
        for record in drug_data:
            if record['actual_qty'] != record['sensor_drop_quantity'] and record['slot_header_id'] in error_slot_header:
                record["sensor_error"] = "Yes"
            else:
                record["sensor_error"] = "No"

        df_drug_data = pd.DataFrame(drug_data)
        df_error_data = df_drug_data[df_drug_data['sensor_error'] == "Yes"]
        df_error_data.drop_duplicates(subset="slot_header_id",
                             keep="first", inplace=True)

        df_robot_A_error = df_error_data[df_error_data["device_id"] == 2]
        robot_A_error_packs = df_robot_A_error['pack_id'].values.tolist()
        robot_A_error_packs = [*set(robot_A_error_packs)]
        df_robot_B_error = df_error_data[df_error_data["device_id"] == 3]
        robot_B_error_packs = df_robot_B_error['pack_id'].values.tolist()
        robot_B_error_packs = [*set(robot_B_error_packs)]
        # df_error_data.drop(['actual_qty', 'sensor_drop_quantity'], axis=1, inplace=True)
        error_data = df_error_data.to_dict('records')

        response = {
            "robot_'A'_error_count": str(len(df_robot_A_error)),
            "robot_A_error_packs": robot_A_error_packs,
            "robot_'B'_error_count": str(len(df_robot_B_error)),
            "robot_B_error_packs": robot_B_error_packs,
        }

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_csv_data_for_sensor_error {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_csv_data_for_sensor_error: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def get_sensor_data_with_different_condition(data_dict):
    """
        Function to measure difference between error of sensor data and error of pvs data
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        track_date = data_dict.get('date')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        if track_date is None:
            track_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        sensor_dropping_data = get_sensor_dropping_data(14, 3, track_date, utc_time_zone_offset)
        df_sensor_dropping_data = pd.DataFrame(sensor_dropping_data)

        slot_list = df_sensor_dropping_data["slot_id"].values.tolist()
        slot_header_list = df_sensor_dropping_data["slot_header_id"].values.tolist()
        pvs_data = get_pvs_dropping_data(slot_list, slot_header_list)
        df_pvs_dropping_data = pd.DataFrame(pvs_data)
        df_pvs_dropping_data.drop_duplicates(inplace=True)

        df_pvs_sensor_dropping_data = df_pvs_dropping_data.merge(df_sensor_dropping_data, on='slot_id', how='left')
        if len(sensor_dropping_data) == 0:
            response = {
                "pvs_sensor_dropping_data_drug_wise": 0,
                "pvs_sensor_dropping_data_header_wise": 0,
                "sensor_error_data": 0,
                "number_of_data_dict": 0,
            }
            return response

        batch_list = df_pvs_sensor_dropping_data["batch_id"].values.tolist()

        # Get pack_affected list remove that pack data from data
        pack_affected_list = get_batch_id_by_action_id(batch_list)

        df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
            ~df_pvs_sensor_dropping_data["pack_id"].isin(pack_affected_list)]

        # Get pack_id and slot_number from pill_jump_error table to remove from output
        list_pack_id_and_slot_number = get_pack_id_and_slot_number(track_date, utc_time_zone_offset)

        df_pvs_sensor_dropping_data["pack_id_slot_number"] = df_pvs_sensor_dropping_data.pack_id.astype(str).str \
            .cat(df_pvs_sensor_dropping_data.slot_number.astype(str), sep=',')

        if len(list_pack_id_and_slot_number):
            df_pack_affected_list = pd.DataFrame(list_pack_id_and_slot_number)

            df_pack_affected_list["pack_id_slot_number"] = df_pack_affected_list.pack_id.astype(str).str \
                .cat(df_pack_affected_list.slot_number.astype(str), sep=',')

            skip_pack_id_slot_number_list = df_pack_affected_list['pack_id_slot_number'].tolist()

            df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data[
                ~df_pvs_sensor_dropping_data["pack_id_slot_number"].isin(skip_pack_id_slot_number_list)]


        df_pvs_sensor_dropping_data.drop('pack_id_slot_number', axis=1, inplace=True)

        drug_id_list = df_pvs_sensor_dropping_data["unique_drug_id"].values.tolist()
        canister_id_list = df_pvs_sensor_dropping_data["canister_id"].values.tolist()
        df_pvs_sensor_dropping_data_header_wise = df_pvs_sensor_dropping_data.groupby(['slot_header_id']) \
            .agg({'batch_id': 'last', 'pack_id': 'last',
                  'actual_qty': 'sum',
                  'sensor_drop_quantity': 'sum',
                  'pvs_predicted_qty_total': 'last',
                  'sensor_created_date': 'last'}).reset_index()
        drug_data_of_error_slot = get_drug_data_of_error_slot(drug_id_list)
        location_id_of_error_slot = get_location_data_of_error_slot(canister_id_list)
        df_drug_data_of_error_slot = pd.DataFrame(drug_data_of_error_slot)
        df_location_data_of_error_slot = pd.DataFrame(location_id_of_error_slot)
        df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data.merge(df_drug_data_of_error_slot,
                                                                                on='unique_drug_id', how='inner')
        df_pvs_sensor_dropping_data = df_pvs_sensor_dropping_data.merge(df_location_data_of_error_slot,
                                                                                on='canister_id', how='left')

        number_of_data_dict = dict()

        number_of_data_dict['total_data'] = len(df_pvs_sensor_dropping_data_header_wise)
        # df_pvs_sensor_dropping_data_header_wise['a != p != s'] = np.zeros(
        #     len(df_pvs_sensor_dropping_data_header_wise))
        # df_pvs_sensor_dropping_data_header_wise['a = p = s'] = np.zeros(
        #     len(df_pvs_sensor_dropping_data_header_wise))
        # df_pvs_sensor_dropping_data_header_wise['a = p != s'] = np.zeros(
        #     len(df_pvs_sensor_dropping_data_header_wise))
        # df_pvs_sensor_dropping_data_header_wise['a = s != p'] = np.zeros(
        #     len(df_pvs_sensor_dropping_data_header_wise))
        # df_pvs_sensor_dropping_data_header_wise['a != p = s'] = np.zeros(
        #     len(df_pvs_sensor_dropping_data_header_wise))
        # Get Sensor Error data from total data
        df_sensor_data_with_condition_one = df_pvs_sensor_dropping_data_header_wise[(df_pvs_sensor_dropping_data_header_wise[
                                                                           "pvs_predicted_qty_total"] !=
                                                                       df_pvs_sensor_dropping_data_header_wise[
                                                                           "sensor_drop_quantity"]) &
                                                                                    (df_pvs_sensor_dropping_data_header_wise["actual_qty"] !=
                                                                                                df_pvs_sensor_dropping_data_header_wise[
                                                                                                    "sensor_drop_quantity"]) &
                                                                                    (df_pvs_sensor_dropping_data_header_wise["actual_qty"] !=
                                                                                                df_pvs_sensor_dropping_data_header_wise[
                                                                                                    "pvs_predicted_qty_total"])]
        condition_1_slot_header = df_sensor_data_with_condition_one["slot_header_id"].values.tolist()
        df_drug_wise_data_of_condition_one = df_pvs_sensor_dropping_data[
            df_pvs_sensor_dropping_data.slot_header_id.isin(condition_1_slot_header)]

        # df_sensor_data_with_condition_one = df_sensor_data_with_condition_one.groupby(['sensor_created_date'], as_index=False).agg(
        #     {'a != p != s': 'count'})
        df_sensor_data_with_condition_two = df_pvs_sensor_dropping_data_header_wise[
            (df_pvs_sensor_dropping_data_header_wise[
                 "pvs_predicted_qty_total"] ==
             df_pvs_sensor_dropping_data_header_wise[
                 "sensor_drop_quantity"]) &
            (df_pvs_sensor_dropping_data_header_wise["actual_qty"] ==
             df_pvs_sensor_dropping_data_header_wise[
                 "sensor_drop_quantity"])]
        condition_2_slot_header = df_sensor_data_with_condition_two["slot_header_id"].values.tolist()
        df_drug_wise_data_of_condition_two = df_pvs_sensor_dropping_data[
            df_pvs_sensor_dropping_data.slot_header_id.isin(condition_2_slot_header)]
        # df_sensor_data_with_condition_two = df_sensor_data_with_condition_two.groupby(['sensor_created_date'],
        #                                                                               as_index=False).agg({'a = p = s': 'count'})
        df_sensor_data_with_condition_three = df_pvs_sensor_dropping_data_header_wise[
            (df_pvs_sensor_dropping_data_header_wise[
                 "pvs_predicted_qty_total"] !=
             df_pvs_sensor_dropping_data_header_wise[
                 "sensor_drop_quantity"]) &
            (df_pvs_sensor_dropping_data_header_wise["actual_qty"] ==
             df_pvs_sensor_dropping_data_header_wise[
                 "pvs_predicted_qty_total"])]
        condition_3_slot_header = df_sensor_data_with_condition_three["slot_header_id"].values.tolist()
        df_drug_wise_data_of_condition_three = df_pvs_sensor_dropping_data[
            df_pvs_sensor_dropping_data.slot_header_id.isin(condition_3_slot_header)]
        # df_sensor_data_with_condition_three = df_sensor_data_with_condition_three.groupby(['sensor_created_date'],
        #                                                                               as_index=False).agg({'a = p != s': 'count'})
        df_sensor_data_with_condition_four = df_pvs_sensor_dropping_data_header_wise[
            (df_pvs_sensor_dropping_data_header_wise[
                 "pvs_predicted_qty_total"] !=
             df_pvs_sensor_dropping_data_header_wise[
                 "sensor_drop_quantity"]) &
            (df_pvs_sensor_dropping_data_header_wise["actual_qty"] ==
             df_pvs_sensor_dropping_data_header_wise[
                 "sensor_drop_quantity"])]
        condition_4_slot_header = df_sensor_data_with_condition_four["slot_header_id"].values.tolist()
        df_drug_wise_data_of_condition_four = df_pvs_sensor_dropping_data[
            df_pvs_sensor_dropping_data.slot_header_id.isin(condition_4_slot_header)]
        # df_sensor_data_with_condition_four = df_sensor_data_with_condition_four.groupby(['sensor_created_date'],
        #                                                                                 as_index=False).agg({'a = s != p': 'count'})
        df_sensor_data_with_condition_five = df_pvs_sensor_dropping_data_header_wise[
            (df_pvs_sensor_dropping_data_header_wise[
                 "actual_qty"] !=
             df_pvs_sensor_dropping_data_header_wise[
                 "sensor_drop_quantity"]) &
            (df_pvs_sensor_dropping_data_header_wise["pvs_predicted_qty_total"] ==
             df_pvs_sensor_dropping_data_header_wise[
                 "sensor_drop_quantity"])]
        condition_5_slot_header = df_sensor_data_with_condition_five["slot_header_id"].values.tolist()
        df_drug_wise_data_of_condition_five = df_pvs_sensor_dropping_data[
            df_pvs_sensor_dropping_data.slot_header_id.isin(condition_5_slot_header)]
        # df_sensor_data_with_condition_five = df_sensor_data_with_condition_five.groupby(['sensor_created_date'],
        #                                                                                 as_index=False).agg({'a != p = s': 'count'})


        response = {
            'header_wise_data_of_condition_one': df_sensor_data_with_condition_one.to_dict('records'),
            'header_wise_data_of_condition_two': df_sensor_data_with_condition_two.to_dict('records'),
            'header_wise_data_of_condition_three': df_sensor_data_with_condition_three.to_dict('records'),
            'header_wise_data_of_condition_four': df_sensor_data_with_condition_four.to_dict('records'),
            'header_wise_data_of_condition_five': df_sensor_data_with_condition_five.to_dict('records'),
            'drug_wise_data_of_condition_one': df_drug_wise_data_of_condition_one.to_dict('records'),
            'drug_wise_data_of_condition_two': df_drug_wise_data_of_condition_two.to_dict('records'),
            'drug_wise_data_of_condition_three': df_drug_wise_data_of_condition_three.to_dict('records'),
            'drug_wise_data_of_condition_four': df_drug_wise_data_of_condition_four.to_dict('records'),
            'drug_wise_data_of_condition_five': df_drug_wise_data_of_condition_five.to_dict('records'),
            'pvs_sensor_dropping_data_header_wise': df_pvs_sensor_dropping_data_header_wise.to_dict('records')
        }

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_sensor_drug_error_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_sensor_drug_error_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

def get_filled_slot_count_of_pack(data_dict):
    """
        Function to measure difference between error of sensor data and error of pvs data
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        pack_ids = data_dict.get('pack_ids')
        pack_ids = list(pack_ids.split(", "))
        pack_ids[0] = pack_ids[0][1:]
        pack_ids[-1] = pack_ids[-1][:-1]
        pack_ids = [eval(i) for i in pack_ids]
        filled_slot_count_for_pack = get_filled_slot_count_of_pack_with_packid_batchid(pack_ids)

        response = {
            "Pack_id_with_filled_slot_count": filled_slot_count_for_pack
        }

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_sensor_drug_error_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_sensor_drug_error_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


def get_user_reported_error_data(data_dict):
    """
        Function to get data of user reported error pack
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        to_date = data_dict.get('to_date')
        from_date = data_dict.get('from_date')
        if time_zone is None:
            time_zone = settings.CURRENT_TIMEZONE
        else:
            time_zone = settings.TIME_ZONE_MAP[time_zone]
        if from_date and to_date is None:
            from_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')
            to_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')
        if to_date is None:
            to_date = datetime.now(pytz.timezone(time_zone)).strftime('%Y-%m-%d')

        utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)

        user_report_error_pack_data = get_user_report_pack_detail(from_date, to_date, utc_time_zone_offset)
        if len(user_report_error_pack_data) == 0:
            response = {
                "user_report_error_pack": 0,
                "error_detail_with_pack_verified_status": 0,
                "error_detail_with_pack_monitor": 0,
                "error_detail_with_pack_not_monitor": 0,
                "slot_header_data": 0,
                "green_pack_green_slot_error": 0,
                "green_slot_but_error_data": 0,
                "pvs_data_of_error": 0,
                "slot_process_date": 0,
                "user_reported_pack_count": 0,
                "total_pack_count": 0
            }
            return response
        df_user_report_error_pack_data = pd.DataFrame(user_report_error_pack_data)
        slot_header_id = df_user_report_error_pack_data['slot_header_id'].tolist()
        pack_id = df_user_report_error_pack_data['pack_id'].tolist()
        user_reported_pack_id = [*set(pack_id)]
        pack_count = get_pack_count_for_user_report_error(from_date, to_date, utc_time_zone_offset)
        slot_header_detail, slot_header_pvs_data = get_slot_header_detail(slot_header_id)
        df_slot_header_data = pd.DataFrame(slot_header_detail)
        df_slot_header_pvs_data = pd.DataFrame(slot_header_pvs_data)
        df_slot_header_data = pd.merge(df_slot_header_data, df_slot_header_pvs_data,
                                       on=['slot_header_id', 'unique_drug_id'], how='left')
        df_slot_header_data = pd.merge(df_slot_header_data, df_user_report_error_pack_data,
                                       on=['slot_header_id', 'unique_drug_id'], how='left')

        slot_header_data_of_error, slot_process_date = get_graph_data_for_slot_header(slot_header_id,
                                                                                      pack_id,
                                                                                      utc_time_zone_offset)
        df_pvs_data_of_error = pd.DataFrame(slot_header_data_of_error)
        df_slot_process_date = pd.DataFrame(slot_process_date)
        df_slot_process_date.drop_duplicates(inplace=True)

        df_green_pack_green_slot_error = df_user_report_error_pack_data[
            (df_user_report_error_pack_data['slot_color_status'] == 214) &
            (df_user_report_error_pack_data['pack_verification_status'] == 212)]

        df_green_slot_but_error_data = df_user_report_error_pack_data[
            df_user_report_error_pack_data['slot_color_status'] == 214]

        df_error_detail_with_pack_verified_status = df_user_report_error_pack_data[
            df_user_report_error_pack_data['pack_verification_status'] == 212]
        df_error_detail_with_pack_monitor = df_user_report_error_pack_data[
            df_user_report_error_pack_data['pack_verification_status'] == 211]
        df_error_detail_with_pack_not_monitor = df_user_report_error_pack_data[
            df_user_report_error_pack_data['pack_verification_status'] == 210]

        response = {
            "user_report_error_pack": df_user_report_error_pack_data.to_dict('records'),
            "error_detail_with_pack_verified_status": df_error_detail_with_pack_verified_status.to_dict('records'),
            "error_detail_with_pack_monitor": df_error_detail_with_pack_monitor.to_dict('records'),
            "error_detail_with_pack_not_monitor": df_error_detail_with_pack_not_monitor.to_dict('records'),
            "slot_header_data": df_slot_header_data.to_dict('records'),
            "green_pack_green_slot_error": df_green_pack_green_slot_error.to_dict('records'),
            "green_slot_but_error_data": df_green_slot_but_error_data.to_dict('records'),
            "pvs_data_of_error": df_pvs_data_of_error.to_dict('records'),
            "slot_process_date": df_slot_process_date.to_dict('records'),
            "user_reported_pack_count": len(user_reported_pack_id),
            "total_pack_count": pack_count['pack_count']
        }
        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_sensor_drug_error_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_user_reported_error_data: exc_type - {exc_type}, filename - {filename},"
            f" line - {exc_tb.tb_lineno}")
        raise e


def user_reported_error_mail(data_dict):
    """
        Function to get data of user reported error pack
        :param:
        :return:
    """
    try:
        time_zone = data_dict.get('time_zone')
        track_date = data_dict.get('date')
        if time_zone is None:
            time_zone = settings.CURRENT_TIMEZONE
        else:
            time_zone = settings.TIME_ZONE_MAP[time_zone]
        if track_date is None:
            track_date = (datetime.now(pytz.timezone(time_zone)) - timedelta(1)).strftime('%Y-%m-%d')

        # utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
        data_dict_for_get_data = {
            'time_zone': time_zone,
            'from_date': track_date,
            "to_date": track_date
        }
        user_report_error_data = get_user_reported_error_data(data_dict_for_get_data)
        api_response = dict()
        if user_report_error_data['user_report_error_pack'] == 0:
            api_response = {
                'date': track_date,
                'total_error': 0,
                'user_report_error_data': 0,
                'mail_send': False,
                'data_status': False
            }
            return api_response
        df_user_report_error_data = pd.DataFrame(user_report_error_data['slot_header_data'])
        df_user_report_error_data.dropna(subset=['pack_id', 'pack_verification_id'], inplace=True)
        df_total_error_data = pd.DataFrame(user_report_error_data['user_report_error_pack'])
        df_total_error_data = df_total_error_data[df_total_error_data['unique_drug_id'].isnull()]
        df_user_report_error_data = pd.concat([df_user_report_error_data, df_total_error_data], ignore_index=True)
        green_pack_status = 0
        if len(user_report_error_data['green_slot_but_error_data']) != 0:
            green_pack_status = 1
            df_user_report_error_of_green_slot = df_user_report_error_data[df_user_report_error_data['slot_color_status'] == 214]
            error_slot_header = df_user_report_error_of_green_slot['slot_header_id'].tolist()
            error_slot_header = [*set(error_slot_header)]
            user_report_error_of_green_slot = df_user_report_error_of_green_slot.to_dict('records')
            urls = []
            for record in user_report_error_of_green_slot:
                if str(record['unique_drug_id']) == "nan":
                    record['url'] = 'http://{}/sensor_dashboard/user_reported_green_slots_or_packs?from_date={}&' \
                                    'to_date={}&slot_wise=True&slot_header={}'.format(
                        settings.BASE_URL_ANALYTICS, track_date, track_date, int(record['slot_header_id']))
                else:
                    record['url'] = 'http://{}/sensor_dashboard/user_reported_green_slots_or_packs?from_date={}&' \
                                    'to_date={}&slot_wise=True&slot_header={}&slot_id={}'.format(
                        settings.BASE_URL_ANALYTICS, track_date, track_date, int(record['slot_header_id']), int(record['slot_id']))
                urls.append(record['url'])

            response = {
                'date': track_date,
                'total_slot_error': str(len(error_slot_header)),
                'total_error': str(len(urls)),
                'user_report_error_data': urls
            }
            send_email_for_user_reported_error_of_green_slot(user_error_data=response)
            api_response = {
                'date': track_date,
                'total_error': str(len(error_slot_header)),
                'user_report_error_data': urls,
                'mail_send': True,
                'data_status': True
            }
        error_slot_header = df_user_report_error_data['slot_header_id'].tolist()
        error_slot_header = [*set(error_slot_header)]
        df_verified_pack_error = df_user_report_error_data[df_user_report_error_data['pack_verification_status'] == 212]
        df_monitored_pack_error = df_user_report_error_data[
            df_user_report_error_data['pack_verification_status'] == 211]
        df_not_monitored_pack_error = df_user_report_error_data[
            df_user_report_error_data['pack_verification_status'] == 210]
        verified_pack_error = df_verified_pack_error.to_dict('records')
        monitored_pack_error = df_monitored_pack_error.to_dict('records')
        not_monitored_pack_error = df_not_monitored_pack_error.to_dict('records')
        urls = []
        for record in verified_pack_error:
            if str(record['unique_drug_id']) == "nan":
                record['url'] = 'http://{}/sensor_dashboard/user_reported_error_detail?from_date={}&' \
                                'to_date={}&pack_verified=True&slot_header={}'.format(
                    settings.BASE_URL_ANALYTICS, track_date, track_date, int(record['slot_header_id']))
            else:
                record['url'] = 'http://{}/sensor_dashboard/user_reported_error_detail?from_date={}&' \
                                'to_date={}&pack_verified=True&slot_header={}&slot_id={}'.format(
                    settings.BASE_URL_ANALYTICS, track_date, track_date, int(record['slot_header_id']), int(record['slot_id']))
            urls.append(record['url'])
        for record in monitored_pack_error:
            if str(record['unique_drug_id']) == "nan":
                record['url'] = 'http://{}/sensor_dashboard/user_reported_error_detail?from_date={}&' \
                                'to_date={}&pack_monitored=True&slot_header={}'.format(
                    settings.BASE_URL_ANALYTICS, track_date, track_date, int(record['slot_header_id']))
            else:
                record['url'] = 'http://{}/sensor_dashboard/user_reported_error_detail?from_date={}&' \
                                'to_date={}&pack_monitored=True&slot_header={}&slot_id={}'.format(
                    settings.BASE_URL_ANALYTICS, track_date, track_date, int(record['slot_header_id']), int(record['slot_id']))
            urls.append(record['url'])
        for record in not_monitored_pack_error:
            if str(record['unique_drug_id']) == "nan":
                record['url'] = 'http://{}/sensor_dashboard/user_reported_error_detail?from_date={}&' \
                                'to_date={}&pack_not_monitored=True&slot_header={}'.format(
                    settings.BASE_URL_ANALYTICS, track_date, track_date, int(record['slot_header_id']))
            else:
                record['url'] = 'http://{}/sensor_dashboard/user_reported_error_detail?from_date={}&' \
                                'to_date={}&pack_not_monitored=True&slot_header={}&slot_id={}'.format(
                    settings.BASE_URL_ANALYTICS, track_date, track_date, int(record['slot_header_id']), int(record['slot_id']))

            urls.append(record['url'])
        response = {
            'date': track_date,
            'total_slot_error': str(len(error_slot_header)),
            'total_error': str(len(urls)),
            'user_report_error_data': urls
        }
        # send_email_for_user_reported_error(user_error_data=response)
        if green_pack_status == 0:
            api_response = {
                    'date': track_date,
                    'total_error': 0,
                    'user_report_error_data': 0,
                    'mail_send': False,
                    'data_status': True
                }
        return api_response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_sensor_drug_error_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_user_reported_error_data: exc_type - {exc_type}, filename - {filename},"
            f" line - {exc_tb.tb_lineno}")
        raise e