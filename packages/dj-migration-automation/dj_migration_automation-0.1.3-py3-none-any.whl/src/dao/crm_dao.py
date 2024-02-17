import datetime
import functools
import operator
import os
import sys
from typing import List, Any, Optional

import pytz
from peewee import Clause
from peewee import (DoesNotExist, InternalError, fn, JOIN_LEFT_OUTER, DataError, IntegrityError, SQL)

import settings
from dosepack.utilities.utils import get_current_datetime_by_timezone, is_date, \
    convert_dob_date_to_sql_date
from dosepack.utilities.utils import log_args_and_response, log_args
from src.model.model_batch_master import BatchMaster
from src.model.model_mfd_canister_master import MfdCanisterMaster
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_user_map import PackUserMap
from src.model.model_notification import Notification
from src.model.model_batch_manual_packs import BatchManualPacks

from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_analysis import PackAnalysis
from src import constants
from src.api_utility import get_results, get_multi_search
from src.model.model_canister_master import CanisterMaster
from src.model.model_code_master import CodeMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_ext_pack_details import ExtPackDetails
from src.model.model_facility_master import FacilityMaster
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_status_tracker import PackStatusTracker
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_slot_details import SlotDetails
from src.model.model_temp_mfd_filling import TempMfdFilling
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger


@log_args
def get_drug_info_from_canister_list_pack_queue(canister_list: list, pack_id: int):
    """
    To get drug info from given canister list of a batch
    @param pack_id:
    @param batch_id:
    @param canister_list:
    @return:
    """
    canister_drug_info = list()
    try:
        select_fields = [DrugMaster.id.alias('drug_id'),
                         PackAnalysisDetails.device_id,
                         PackAnalysisDetails.canister_id,
                         fn.IF(DeviceMaster.name.is_null(True), 'null', DeviceMaster.name).alias('device_name'),
                         fn.IF(LocationMaster.location_number.is_null(True), 'null',
                               LocationMaster.display_location).alias('display_location'),
                         fn.IF(DrugMaster.drug_name.is_null(True), 'null', DrugMaster.drug_name).alias('drug_name'),
                         fn.IF(DrugMaster.ndc.is_null(True), 'null', DrugMaster.ndc).alias('drug_ndc'),
                         fn.IF(DrugMaster.txr.is_null(True), 'null', DrugMaster.txr).alias('drug_txr'),
                         fn.IF(DrugMaster.imprint.is_null(True), 'null',
                               fn.replace(fn.replace(DrugMaster.imprint, ' ', ''), '<>', ' ')).alias('drug_imprint'),
                         fn.IF(DrugMaster.color.is_null(True), 'null', DrugMaster.color).alias('drug_color'),
                         fn.IF(DrugMaster.shape.is_null(True), 'null', DrugMaster.shape).alias('drug_shape'),
                         fn.IF(DrugMaster.image_name.is_null(True), 'null', DrugMaster.image_name).alias('image_name'),
                         fn.IF(DrugMaster.strength_value.is_null(True), 'null',
                               DrugMaster.strength_value).alias('strength_value'),
                         fn.IF(DrugMaster.strength.is_null(True), 'null', DrugMaster.strength).alias('strength'),
                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), 'null',
                               DrugStockHistory.is_in_stock).alias('is_in_stock'),
                         fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                               DrugDetails.last_seen_by).alias('last_seen_by'),
                         fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                               DrugDetails.last_seen_date).alias('last_seen_date')
                         ]

        query = PackAnalysis.select(*select_fields).dicts() \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                         (DrugStockHistory.is_active == True) &
                                                         (DrugStockHistory.company_id == CanisterMaster.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == CanisterMaster.company_id))) \
            .where(
            PackAnalysis.pack_id == pack_id,
            PackAnalysisDetails.canister_id << canister_list) \
            .group_by(PackAnalysisDetails.canister_id)

        for record in query:
            drug_info = ","
            str_durg_info = drug_info.join(map(str, list(record.values())))
            canister_drug_info.append(str_durg_info)

        return canister_drug_info

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_drug_info_from_canister_list_pack_queue {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_drug_info_from_canister_list_pack_queue {}".format(e))
        return None


@log_args
def get_manual_drug_info_from_drug_list_pack_queue(drug_list: list, pack_id: int):
    """
    To get drug info from given manual drug list of a batch
    @param pack_id:
    @param batch_id:
    @param drug_list:
    @return:
    """
    manual_drug_info = list()
    drug_ids = list()
    for drug in drug_list:
        drug_ids.append(drug[0])
    try:
        select_fields = [SlotDetails.drug_id,
                         fn.IF(DrugMaster.drug_name.is_null(True), 'null', DrugMaster.drug_name).alias('drug_name'),
                         fn.IF(DrugMaster.ndc.is_null(True), 'null', DrugMaster.ndc).alias('drug_ndc'),
                         fn.IF(DrugMaster.txr.is_null(True), 'null', DrugMaster.txr).alias('drug_txr'),
                         fn.IF(DrugMaster.imprint.is_null(True), 'null',
                               fn.replace(fn.replace(DrugMaster.imprint, ' ', ''), '<>', ' ')).alias('drug_imprint'),
                         fn.IF(DrugMaster.color.is_null(True), 'null', DrugMaster.color).alias('drug_color'),
                         fn.IF(DrugMaster.shape.is_null(True), 'null', DrugMaster.shape).alias('drug_shape'),
                         fn.IF(DrugMaster.image_name.is_null(True), 'null', DrugMaster.image_name).alias('image_name'),
                         fn.IF(DrugMaster.strength_value.is_null(True), 'null',
                               DrugMaster.strength_value).alias('strength_value'),
                         fn.IF(DrugMaster.strength.is_null(True), 'null', DrugMaster.strength).alias('strength'),
                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), 'null',
                               DrugStockHistory.is_in_stock).alias('is_in_stock'),
                         fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                               DrugDetails.last_seen_by).alias('last_seen_by'),
                         fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                               DrugDetails.last_seen_date).alias('last_seen_date')
                         ]

        query = PackDetails.select(*select_fields).dicts() \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                         (DrugStockHistory.is_active == True) &
                                                         (DrugStockHistory.company_id == PackDetails.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id))) \
            .where(SlotDetails.drug_id << drug_ids,
                   PackDetails.id == pack_id) \
            .group_by(DrugMaster.id)

        for record in query:
            drug_info = ","
            drug_info_list = list(record.values())
            # insert None because in case of manual drugs we don't have device and location info
            drug_info_list.insert(1, 'null')
            drug_info_list.insert(2, 'null')
            drug_info_list.insert(3, 'null')
            drug_info_list.insert(4, 'null')
            str_drug_info = drug_info.join(map(str, drug_info_list))

            manual_drug_info.append(str_drug_info)

        return manual_drug_info

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_manual_drug_info_from_drug_list_pack_queue {}".format(e))
        raise


@log_args_and_response
def get_packs_count_for_all_batches(system_id: int) -> dict:
    """
    Function to get batch list and pack count from system id
    @return: dict of pack_count as key and count of packs of the latest batch as value
    """
    batch_list: list = list()
    try:
        batch_query = BatchMaster.db_get_all_batch_list_from_system(system_id=system_id)
        for record in batch_query:
            batch_list.append(record['id'])
        logger.info("In get_packs_count_for_all_batches: batch_list: {}".format(batch_list))
        if not len(batch_list):
            response = {"pack_count": 0, "batch_list": batch_list}
        else:
            total_packs = PackDetails.db_get_total_packs_count_for_batch(batch_list)
            response = {"pack_count": total_packs, "batch_list": batch_list}

        logger.info("get_packs_count_for_all_batches {}".format(response))
        return response

    except (InternalError, IntegrityError, ValueError, IndexError) as e:
        logger.error("Error in get_packs_count_for_all_batches {}".format(e))
        raise


def get_all_batch_pack_queue_data(filter_fields: [dict, None], paginate: [dict, None], debug_mode_flag: bool,
                                  drug_list: [list, None], sort_fields: [list, None],
                                  only_manual: bool, batch_list: list, system_id: int):
    """

    @param filter_fields:
    @param paginate:
    @param debug_mode_flag:
    @param drug_list:
    @param sort_fields:
    @param only_manual:
    @param batch_list:
    @param system_id:
    @return:
    """

    DrugMasterAlias = DrugMaster.alias()
    DrugStockHistoryAlias = DrugStockHistory.alias()
    DrugDetailsAlias = DrugDetails.alias()
    UniqueDrugAlias = UniqueDrug.alias()
    fields_dict = {
        # do not give alias here, instead give it in select_fields,
        # as this can be reused in where clause
        "pack_sequence": PackDetails.order_no,
        "batch_id": PackDetails.batch_id,
        "pack_display_id": PackDetails.pack_display_id,
        "patient_name": PatientMaster.concated_patient_name_field(),
        "patient_id": PatientMaster.patient_no,
        "patient_dob": PatientMaster.dob,
        "pack_status_id": PackDetails.pack_status.alias('status_code'),
        "facility_name": FacilityMaster.facility_name,
        "car_id": PackDetails.car_id,
        "admin_period": fn.CONCAT(PackDetails.consumption_start_date, ' to ', PackDetails.consumption_end_date),
        "delivery_date": PackHeader.scheduled_delivery_date,
        "pack_status": CodeMaster.value,
        # "robot_id_list" : PackAnalysisDetails.robot_id
        "device_id_list": fn.GROUP_CONCAT(Clause(
            SQL('Distinct'),
            fn.IF(PackAnalysisDetails.device_id.is_null(False), PackAnalysisDetails.device_id,
                  MfdAnalysis.dest_device_id),
            SQL('ORDER BY'),
            fn.IF(PackAnalysisDetails.device_id.is_null(False), PackAnalysisDetails.device_id,
                  MfdAnalysis.dest_device_id),
        )).coerce(False),

        "canister_drug_count": fn.COUNT(Clause(SQL('DISTINCT'),
                                               fn.IF(PackAnalysisDetails.canister_id.is_null(False)
                                                     & PackAnalysisDetails.device_id.is_null(False), DrugMasterAlias.id,
                                                     None))),
        "manual_drug_count": (fn.COUNT(Clause(SQL('DISTINCT'),
                                              fn.IF((PackAnalysisDetails.device_id.is_null(True) |
                                                     PackAnalysisDetails.canister_id.is_null(
                                                         True) | SlotDetails.quantity << settings.DECIMAL_QTY_LIST),
                                                    SlotDetails.drug_id,
                                                    None)))),
        "ndc_list": fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(DrugMaster.ndc.is_null(True),
                                                             'null', DrugMaster.ndc)),
                                           SQL(" SEPARATOR ' , ' "))).coerce(False),
        "pack_id": PackDetails.id
    }

    select_fields = [fields_dict['pack_id'].alias('pack_id'),
                     PackDetails.pack_display_id,
                     PackAnalysis.manual_fill_required.alias('manual_fill_require'),
                     PackDetails.order_no.alias('pack_sequence'),
                     PackDetails.pack_plate_location.alias('pack_location'),
                     PackDetails.batch_id,
                     PatientMaster.patient_no.alias('patient_id'),
                     PatientMaster.dob.alias('patient_dob'),
                     fields_dict['pack_status'].alias('pack_status'),
                     fields_dict['car_id'],
                     fields_dict['facility_name'],
                     fields_dict['patient_name'].alias('patient_name'),
                     fields_dict["admin_period"].alias("admin_period"),
                     fields_dict['delivery_date'].alias('delivery_date'),
                     PackDetails.pack_status.alias('pack_status_code'),
                     fields_dict['device_id_list'].alias('device_id_list'),
                     fields_dict['ndc_list'].alias('ndc_list'),
                     fn.COUNT(fn.DISTINCT(SlotDetails.drug_id)).alias("total_drug_count"),
                     fields_dict['canister_drug_count'].alias('canister_drug_count'),
                     fields_dict['manual_drug_count'].alias('manual_drug_count'),
                     fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.status_id)).alias('mfd_status'),
                     fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysisDetails.canister_id)).coerce(False).alias(
                         'canister_ids'),

                     fn.GROUP_CONCAT(Clause(SQL('DISTINCT'), Clause(
                         fn.CONCAT(SlotDetails.drug_id, ',',
                                   fn.IF((PackAnalysisDetails.device_id.is_null(True)) |
                                         (PackAnalysisDetails.canister_id.is_null(True)) | (
                                                 SlotDetails.quantity << settings.DECIMAL_QTY_LIST), 'null', None)
                                   ), SQL("SEPARATOR '|' ")))).coerce(False).alias('manual_drug_ids'),
                     ExtPackDetails.ext_status_id.alias('ext_pack_status_id'),
                     PackStatusTracker.reason.alias('reason')
                     ]

    clauses = [PackDetails.batch_id << batch_list,
               PackDetails.system_id == system_id,
               PackUserMap.id.is_null(True),
               PackDetails.pack_status.not_in(settings.PACK_QUEUE_STATUS_IGNORE)
               ]

    if debug_mode_flag:
        like_search_list = ['patient_name', 'patient_dob', 'admin_period', 'facility_name']
        exact_search_list = ['patient_id', 'car_id']
        membership_search_list = ['pack_status', 'delivery_date']
        having_search_list = ['device_id_list']
        string_search_field = [fields_dict['pack_display_id'], fields_dict['pack_id']]
        multi_search_fields = [filter_fields['pack_display_id']]
        clauses = get_multi_search(clauses, multi_search_fields, string_search_field)

    else:
        like_search_list = ['patient_name', 'patient_dob', 'admin_period', 'facility_name',
                            'pack_display_id']
        exact_search_list = ['patient_id', 'car_id', "batch_id"]
        membership_search_list = ['pack_status', 'delivery_date']
        having_search_list = ['device_id_list']

    clauses_having = []
    clauses_having = add_having_clauses(clauses_having, fields_dict, filter_fields)

    if drug_list:
        subclauses = list()
        for ndc in drug_list:
            ndc = "%" + ndc + "%"
            subclauses.append((fields_dict["ndc_list"] ** ndc))
        clauses_having.append((functools.reduce(operator.or_, subclauses)))

    if only_manual:
        logger.info("only manual")
        clauses.append((PackAnalysis.manual_fill_required == 1))

    order_list = list()
    if sort_fields:
        order_list.extend(sort_fields)

    if len(order_list) == 0:
        order_list.insert(0, ["pack_sequence", 1])

    try:
        sub_query = ExtPackDetails.select(fn.MAX(ExtPackDetails.id).alias('max_ext_pack_details_id'),
                                          ExtPackDetails.pack_id.alias('pack_id')) \
            .group_by(ExtPackDetails.pack_id).alias('sub_query')

        sub_query_reason = PackStatusTracker.select(fn.MAX(PackStatusTracker.id).alias('max_pack_status_id'),
                                                    PackStatusTracker.pack_id.alias('pack_id')) \
            .group_by(PackStatusTracker.pack_id).alias('sub_query_reason')

        query = PackDetails.select(*select_fields) \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(PackAnalysis, JOIN_LEFT_OUTER, on=((PackAnalysis.id == PackAnalysisDetails.analysis_id) &
                                                     (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=((DeviceMaster.id == PackAnalysisDetails.device_id) |
                                                     (DeviceMaster.id == MfdAnalysis.dest_device_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER,
                  on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                      (DrugStockHistory.is_active == True) &
                      (DrugStockHistory.company_id == PackDetails.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id)) \
            .join(DrugMasterAlias, JOIN_LEFT_OUTER, on=(DrugMasterAlias.id == CanisterMaster.drug_id)) \
            .join(DrugStockHistoryAlias, JOIN_LEFT_OUTER,
                  on=(DrugStockHistoryAlias.unique_drug_id_id == DrugMasterAlias.id) & (
                          DrugStockHistoryAlias.is_active == True)) \
            .join(UniqueDrugAlias, JOIN_LEFT_OUTER,
                  on=(fn.IF(DrugMasterAlias.txr.is_null(True), '', DrugMasterAlias.txr) ==
                      fn.IF(UniqueDrugAlias.txr.is_null(True), '', UniqueDrugAlias.txr)) &
                     (DrugMasterAlias.formatted_ndc == UniqueDrugAlias.formatted_ndc)) \
            .join(DrugDetailsAlias, JOIN_LEFT_OUTER, on=(DrugDetailsAlias.unique_drug_id == UniqueDrugAlias.id)) \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=(PackUserMap.pack_id == PackDetails.id)) \
            .join(sub_query, JOIN_LEFT_OUTER, on=(sub_query.c.pack_id == PackDetails.id)) \
            .join(ExtPackDetails, JOIN_LEFT_OUTER, on=ExtPackDetails.id == sub_query.c.max_ext_pack_details_id) \
            .join(sub_query_reason, JOIN_LEFT_OUTER, on=(sub_query_reason.c.pack_id == PackDetails.id)) \
            .join(PackStatusTracker, JOIN_LEFT_OUTER, on=PackStatusTracker.id == sub_query_reason.c.max_pack_status_id) \
            .group_by(PackDetails.id)

        results, count, non_paginate_result = get_results(query.dicts(), fields_dict, filter_fields=filter_fields,
                                                          clauses=clauses, clauses_having=clauses_having,
                                                          sort_fields=order_list,
                                                          paginate=paginate,
                                                          exact_search_list=exact_search_list,
                                                          like_search_list=like_search_list,
                                                          membership_search_list=membership_search_list,
                                                          having_search_list=having_search_list,
                                                          non_paginate_result_field_list=['pack_id',
                                                                                          'device_id_list']
                                                          )

        return results, count, non_paginate_result

    except(InternalError, IntegrityError, ValueError, DoesNotExist) as e:
        logger.error("Error in get_all_batch_pack_queue_data {}".format(e))
        raise


def add_having_clauses(clauses_having, fields_dict, filter_fields):
    if filter_fields and "canister_drug_count" in filter_fields:
        key = fields_dict["canister_drug_count"]
        value = [int(val) for val in filter_fields["canister_drug_count"].split(',')]
        subclauses = list()
        for v in value:
            if v in range(0, 4):
                subclauses.append((key == v))
            else:
                subclauses.append((key >= v))
        clauses_having.append((functools.reduce(operator.or_, subclauses)))
    if filter_fields and "manual_drug_count" in filter_fields:
        key = fields_dict["manual_drug_count"]
        value = [int(val) for val in filter_fields["manual_drug_count"].split(',')]
        subclauses = list()
        for v in value:
            if v in range(0, 4):
                subclauses.append((key == v))
            else:
                subclauses.append((key >= v))
        clauses_having.append((functools.reduce(operator.or_, subclauses)))
    return clauses_having


@log_args_and_response
def get_total_packs_of_batch(pack_status: list, system_id: int) -> list:
    """
    get total packs of batch
    :return: bool
    """
    pack_list: list = list()
    clauses: list = list()
    try:
        clauses.append(PackDetails.pack_status << pack_status)
        # clauses.append(PackDetails.batch_id == batch_id)
        clauses.append(PackDetails.system_id == system_id)

        batch_total_packs = PackDetails.select(PackDetails.id) \
            .join(PackQueue, on=PackDetails.id == PackQueue.pack_id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .order_by(PackDetails.order_no)

        for pack in batch_total_packs.dicts():
            pack_list.append(pack['id'])

        return pack_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_total_packs_of_batch {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_total_packs_of_batch {}".format(e))
        raise e


@log_args_and_response
def db_check_pack_with_ext_pack_details(pack_list: List[int]):
    pack_header_list: List[int] = []
    patient_pack_id_list: List[int] = []
    change_pending_pack_ids: List[int] = []
    try:
        pack_status = settings.PACK_PROGRESS_DONE_STATUS_LIST + [settings.DELETED_PACK_STATUS,
                                                                 settings.MANUAL_PACK_STATUS]
        ext_query = ExtPackDetails.select(PackHeader.patient_id.alias("patient_id"),
                                          fn.GROUP_CONCAT(Clause(fn.DISTINCT(PackHeader.id))).coerce(False)
                                          .alias("pack_header_ids")).dicts() \
            .join(PackDetails, on=ExtPackDetails.pack_id == PackDetails.id) \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .where(ExtPackDetails.pack_id << pack_list) \
            .group_by(PackHeader.patient_id)

        if ext_query.count() > 0:
            logger.debug("Pack Data exists in ExtPackDetails -- {}".format(pack_list))

            for patient in ext_query:
                pack_header_list = []
                if patient["pack_header_ids"] is not None:
                    pack_header_list = list(map(lambda x: int(x), patient["pack_header_ids"].split(',')))

                    pack_query = PackDetails.select(PackDetails.id.alias("pack_id")).dicts() \
                        .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
                        .where(PackHeader.id << pack_header_list,
                               PackDetails.pack_status << pack_status)

                    if pack_query.count() > 0:
                        logger.debug("At least 1 pack found with either Deleted, In Progress, Manual or Done Status.")
                        logger.debug("Continue with Pack dispatch as per the regular sequence.")
                    else:
                        logger.debug("Packs are in pending state and waiting for new packs to arrive. In the meantime, "
                                     "continue with other Auto(Canister) packs and consider these packs to be filled "
                                     "at the end.")
                        patient_pack_id_list = [pack["pack_id"] for pack in pack_query]
                        change_pending_pack_ids.extend(patient_pack_id_list)

        else:
            logger.debug("Pack Data does not exist in ExtPackDetails -- {}".format(pack_list))

        return change_pending_pack_ids

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return []
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_mfd_pack_data(system_id, device_id=None) -> tuple:
    #  todo handle case if pack is to be filled from both the robots
    mfd_packs_dict = dict()
    # pack_mfd_filled = dict()
    pack_trolley_seq = dict()
    trolley_seq = None

    try:
        mfd_can_status = [constants.MFD_CANISTER_SKIPPED_STATUS,
                          constants.MFD_CANISTER_RTS_DONE_STATUS,
                          constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                          constants.MFD_CANISTER_RTS_REQUIRED_STATUS]

        # get mfd data for pending packs if any

        mfd_packs = PackDetails.select(fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.id)).coerce(False).alias('pack_id'),
                                       MfdAnalysis.status_id,
                                       MfdAnalysis.dest_device_id,
                                       MfdAnalysis.dest_quadrant,
                                       MfdAnalysis.transferred_location_id,
                                       MfdAnalysis.trolley_seq,
                                       MfdAnalysis.id.alias('mfd_analysis')).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(MfdAnalysisDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(MfdAnalysis, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .where(PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                   MfdAnalysis.dest_device_id == device_id,
                   MfdAnalysis.status_id.not_in(mfd_can_status),
                   PackDetails.system_id == system_id) \
            .group_by(MfdAnalysis.id) \
            .order_by(PackDetails.order_no)

        for data in mfd_packs:
            pack_ids = list(data['pack_id'].split(","))
            for pack in pack_ids:
                pack = int(pack)
                if not trolley_seq:
                    trolley_seq = data['trolley_seq']
                if pack not in mfd_packs_dict.keys():
                    mfd_packs_dict[pack] = dict()
                    pack_trolley_seq[pack] = data['trolley_seq']
                if data['mfd_analysis'] not in mfd_packs_dict[pack]:
                    mfd_packs_dict[pack][data['mfd_analysis']] = (data['transferred_location_id'], data['trolley_seq'])

        return mfd_packs_dict, trolley_seq, pack_trolley_seq

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_mfd_pack_data {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_mfd_pack_data {}".format(e))
        raise e


@log_args_and_response
def get_automatic_pack_record(pack_status: list, system_id: int, device_id: Optional[int] = None) -> List[Any]:
    """
        get automatic pack record based on device id
        :return: bool
    """
    clauses: list = list()
    try:
        clauses.append(PackDetails.pack_status << pack_status)
        # clauses.append(PackDetails.batch_id == batch_id)
        clauses.append(PackDetails.system_id == system_id)
        if device_id is not None:
            clauses.append(PackAnalysisDetails.device_id == device_id)
            query = PackDetails.select(PackDetails.id).dicts() \
                .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
                .join(PackAnalysis, JOIN_LEFT_OUTER, on=PackAnalysis.pack_id == PackDetails.id) \
                .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .where(functools.reduce(operator.and_, clauses)).group_by(PackDetails.id) \
                .having(fn.GROUP_CONCAT(Clause(SQL('Distinct'), PackAnalysisDetails.device_id,
                                               SQL('ORDER BY'), PackAnalysisDetails.device_id))
                        .coerce(False).startswith(str(device_id))) \
                .group_by(PackDetails.id).order_by(PackDetails.order_no)
        else:
            query = PackDetails.select(PackDetails.id).dicts() \
                .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
                .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .where(functools.reduce(operator.and_, clauses)).group_by(PackDetails.id)

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_automatic_pack_record {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_automatic_pack_record {}".format(e))
        raise e


@log_args_and_response
def get_pending_facility_data(batch_list: list) -> List:
    """
        get pending facility data
        :return: List
    """
    facility_names: list = list()
    try:
        query = PackDetails.select(FacilityMaster.facility_name) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                   PackDetails.batch_id << batch_list) \
            .group_by(PatientMaster.facility_id)

        for record in query.dicts():
            facility_names.append(record['facility_name'])

        return facility_names

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pending_facility_data {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_pending_facility_data {}".format(e))
        raise e


@log_args_and_response
def get_pending_packs_per_robot(pack_status: list, batch_id: int, device_id: Optional[int] = None) -> List:
    """
        get pending packs by robot
        :return: list
    """
    robot_pack_dict: dict = dict()
    pending_pack_per_robot: list = list()
    clauses: list = list()

    try:
        clauses.append(PackDetails.pack_status << pack_status)
        clauses.append(PackDetails.batch_id == batch_id)
        clauses.append(PackAnalysisDetails.device_id.is_null(False))
        if device_id is not None:
            clauses.append(PackAnalysisDetails.device_id == device_id)
        fields_dict = {"device_id": fn.GROUP_CONCAT(Clause(SQL('Distinct'),
                                                           PackAnalysisDetails.device_id,
                                                           SQL('ORDER BY'),
                                                           PackAnalysisDetails.device_id
                                                           )).coerce(False)}

        query = PackDetails.select(PackDetails.id, fields_dict["device_id"].alias("device_id")) \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(DeviceMaster, on=DeviceMaster.id == PackAnalysisDetails.device_id) \
            .where(functools.reduce(operator.and_, clauses)).group_by(PackDetails.id)

        logger.info("In get_pending_packs_per_robot: query:{}".format(query.dicts()))

        for record in query.dicts():
            if record['device_id'] not in robot_pack_dict.keys():
                robot_pack_dict[record['device_id']] = set()
            robot_pack_dict[record['device_id']].add(record['id'])

        for robot, packs in robot_pack_dict.items():
            pending_pack_per_robot.append({"device_id": robot, "pack_list": list(packs)})

        return pending_pack_per_robot

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pending_packs_per_robot {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_pending_packs_per_robot {}".format(e))
        raise e


@log_args_and_response
def get_number_of_drugs_in_pack(pack_id: int, system_id: int) -> int:
    """
        get total number of drugs in pack
        :return: List
    """
    try:
        query = PackDetails.select(fn.COUNT(fn.DISTINCT(SlotDetails.drug_id))) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .where(PackDetails.id == pack_id, PackDetails.system_id == system_id)
        return query.scalar()

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_number_of_drugs_in_pack {}".format(e))
        raise e


@log_args_and_response
def get_manual_pack_list_by_robot_id(batch_id: int, device_id: int) -> list:
    """
        get manual pack list by robot id
        :return: List
    """
    pack_ids: list = list()
    try:
        query = PackAnalysis.select(PackAnalysis.pack_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(DeviceMaster, on=PackAnalysisDetails.device_id == DeviceMaster.id) \
            .where(PackAnalysisDetails.device_id == device_id, PackAnalysis.batch_id == batch_id,
                   PackAnalysis.manual_fill_required > 0).group_by(PackAnalysis.pack_id)
        for record in query.dicts():
            pack_ids.append(record['pack_id'])

        return pack_ids
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_manual_pack_list_by_robot_id {}".format(e))
        raise e


@log_args_and_response
def get_pack_details_by_pack_id(pack_id: int, system_id: int) -> List[Any]:
    """
        get pack details by pack id
        :return: List
    """
    try:
        fields_dict = {"robot_id_list": fn.GROUP_CONCAT(Clause(SQL('Distinct'),
                                                               PackAnalysisDetails.device_id,
                                                               SQL('ORDER BY'),
                                                               PackAnalysisDetails.device_id
                                                               )).coerce(False)}

        select_fields = [PackDetails.id,
                         PackDetails.pack_display_id,
                         PackDetails.pack_status,
                         PackDetails.pack_no,
                         PackDetails.created_date,
                         PackDetails.rfid,
                         # PackDetails.dosage_type.alias('dosage_type_id'),
                         # added because of utilise unit dosage pack flow
                         fn.IF(PackDetails.dosage_type == settings.DOSAGE_TYPE_MULTI,
                               fn.IF(PackDetails.pack_type == constants.WEEKLY_UNITDOSE_PACK,
                                     settings.DOSAGE_TYPE_UNIT,
                                     PackDetails.dosage_type),
                               PackDetails.dosage_type)
                         .alias('dosage_type_id'),
                         # CodeMaster.value.alias('dosage_type'),
                         # added because of utilise unit dosage pack flow
                         fn.IF(PackDetails.dosage_type == settings.DOSAGE_TYPE_MULTI,
                               fn.IF(PackDetails.pack_type == constants.WEEKLY_UNITDOSE_PACK,
                                     settings.UNIT_DOSE,
                                     CodeMaster.value),
                               CodeMaster.value)
                         .alias('dosage_type'),
                         PackAnalysis.manual_fill_required.alias('manual_fill_require'),
                         PackDetails.order_no,
                         PackDetails.pack_plate_location,
                         PackDetails.batch_id,
                         PackDetails.car_id,
                         PatientMaster.id.alias('patient_id'),
                         FacilityMaster.facility_name,
                         PatientMaster.first_name,
                         PatientMaster.last_name,
                         PatientMaster.dob,
                         PatientMaster.allergy,
                         PatientMaster.patient_no,
                         PatientMaster.concated_patient_name_field().alias('patient_name'),
                         PackDetails.pack_plate_location,
                         fields_dict['robot_id_list'].alias('robot_id_list'),
                         fn.CONCAT(PackDetails.consumption_start_date, ' to ', PackDetails.consumption_end_date).alias(
                             "admin_period"),
                         PackHeader.scheduled_delivery_date,
                         PackDetails.pack_status.alias('pack_status_code')
                         ]

        query = PackDetails.select(*select_fields).dicts() \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == PackDetails.dosage_type) \
            .where(PackDetails.id << pack_id, PackDetails.system_id == system_id).group_by(PackDetails.id) \
            .order_by(PackDetails.order_no)
        logger.info(f"In get_pack_details_by_pack_id (query altered as per utilise unit pack flow) : {query}")
        return query
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_details_by_pack_id {}".format(e))
        raise e


@log_args_and_response
def get_mfd_devices(pack_id):
    """
    Function to get device list from which mfd canisters for these packs are to be processed
    @param pack_id:
    @return:
    """
    pack_device_dict: dict = dict()
    try:
        query = PackDetails.select(PackDetails.id, fn.GROUP_CONCAT(Clause(SQL('Distinct'),
                                                                          MfdAnalysis.dest_device_id,
                                                                          SQL('ORDER BY'),
                                                                          MfdAnalysis.dest_device_id
                                                                          )).coerce(False).alias('dest_device_list')) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .where(PackDetails.id << pack_id) \
            .group_by(PackDetails.id)

        for record in query.dicts():
            pack_device_dict[record['id']] = record["dest_device_list"]

        return pack_device_dict

    except DoesNotExist as e:
        logger.info(e)
        return pack_device_dict


@log_args_and_response
def get_pack_count_by_device_id(system_id: int, device_id: Optional[list] = None):
    """
    Function to pack count by device id (Robot ids)
    @param device_id:
    @param system_id:
    @param batch_id:
    @return:
    """
    clauses: list = list()
    try:
        clauses.append(PackDetails.system_id == system_id)

        if device_id is not None:
            clauses.append((PackAnalysisDetails.device_id << device_id |
                            MfdAnalysis.dest_device_id << device_id))

        query = PackDetails.select(PackDetails.id,
                                   fn.IF(PackAnalysisDetails.device_id.is_null(False), PackAnalysisDetails.device_id,
                                         MfdAnalysis.dest_device_id).alias('device_id'),
                                   PackDetails.pack_status, PackDetails.filled_at).dicts() \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(PackDetails.id, PackAnalysisDetails.device_id, MfdAnalysis.dest_device_id)

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_count_by_device_id {}".format(e))
        raise e


@log_args_and_response
def check_notification_sent_or_not(notification_message: str) -> bool:
    """
    function to check if notification is sent or not
    :return: bool
    """
    try:
        notification_status = Notification.db_check_notification_sent_or_not(notification_message)
        return notification_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_notification_sent_or_not {}".format(e))
        raise e


@log_args_and_response
def get_done_pack_count(time_zone, offset, batch_id=None):
    """
    Function to get pack count of done packs for given batch for three conditions.
    1) done packs in last one hour
    2) done packs in last one day
    3) done packs till date
    @param offset:
    @param time_zone:
    @param batch_id:
    @return:
    """
    try:
        clauses = [PackDetails.pack_status << [settings.DONE_PACK_STATUS,
                                               settings.PROCESSED_MANUALLY_PACK_STATUS,
                                               settings.PARTIALLY_FILLED_BY_ROBOT],
                   PackDetails.filled_at.not_in(
                       [settings.FILLED_AT_POST_PROCESSING, settings.FILLED_AT_PRI_BATCH_ALLOCATION,
                        settings.FILLED_AT_PACK_FILL_WORKFLOW, settings.FILLED_AT_PRI_PROCESSING])]
        if batch_id:
            clauses.append(PackDetails.batch_id == batch_id)
        current_date = get_current_datetime_by_timezone(time_zone, return_format="date")
        logger.info("get_done_pack_count current_date {}".format(current_date))
        # last_day = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        today = PackDetails.get_pack_count_by_clauses(clauses, fn.DATE(
            fn.CONVERT_TZ(PackDetails.modified_date, settings.TZ_UTC, offset)) == current_date)
        logger.info("get_done_pack_count today {}".format(today))
        # done_pack_count = PackDetails.get_pack_count_by_clauses(clauses)
        current_time = get_current_datetime_by_timezone(time_zone)
        one_hour = (datetime.datetime.now(pytz.timezone(time_zone)) - datetime.timedelta(hours=1)).strftime(
            '%Y-%m-%d %H:%M:%S')
        last_one_hour = PackDetails.get_pack_count_by_clauses(clauses,
                                                              fn.CONVERT_TZ(PackDetails.modified_date, settings.TZ_UTC,
                                                                            offset).between(one_hour, current_time))
        logger.info("In get_done_pack_count: one hour pack count: {}".format(last_one_hour))
        return today, last_one_hour
    except Exception as e:
        logger.error("error in get_done_pack_count {}".format(e))
        raise e


@log_args_and_response
def get_pending_pack_count_of_working_day(time_zone, utc_time_zone_offset):
    try:
        day_pack_count = []
        date = datetime.datetime.now(pytz.timezone(time_zone))
        current_date = date.date()
        tomorrow_date = date + datetime.timedelta(days=1)
        tomorrow_date = tomorrow_date.date()

        query = PackHeader.select(fn.DATE(PackHeader.scheduled_delivery_date).alias("scheduled_delivery_date"),
                                  fn.COUNT(PackDetails.id).alias("pack_count")).dicts() \
            .join(PackDetails, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                   fn.DATE(PackHeader.scheduled_delivery_date) >= current_date) \
            .order_by(PackHeader.scheduled_delivery_date) \
            .group_by(PackHeader.scheduled_delivery_date) \
            .limit(3)

        for data in query:
            if str(data["scheduled_delivery_date"]) == date.strftime("%Y-%m-%d"):
                label = "Today"
            elif str(data["scheduled_delivery_date"]) == tomorrow_date.strftime("%Y-%m-%d"):
                label = "Tomorrow"
            else:
                date = data["scheduled_delivery_date"]
                day = date.strftime('%a')
                label = day.capitalize() + " " + "(" + date.strftime("%m/%d") + ")"
            day_pack_count.append({"label": label, "count": data["pack_count"]})

        # total_pending_packs_query = PackDetails.select(fn.COUNT(PackDetails.id).alias('pending_packs')).dicts() \
        #                             .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
        #                                    PackDetails.batch_id == batch_id)
        total_pending_packs_query = PackQueue.select(fn.COUNT(PackQueue.id).alias('pending_packs')).dicts()

        for data in total_pending_packs_query:
            day_pack_count.append({"label": "Total Pending", "count": data["pending_packs"]})

        return day_pack_count

    except Exception as e:
        logger.error(f"Error in get_pending_pack_count_of_working_day: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pending_pack_count_of_working_day: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return []

    # try:
    #     logger.info("Inside get_pending_pack_count_of_working_day")
    #     day_pack_count = []
    #     pending_pack_count = {"label": "Total Pending", "count": 0}
    #     last_delivery_date = datetime.datetime.now(pytz.timezone(time_zone)) + datetime.timedelta(days=365)  # set default value
    #
    #     clauses = list()
    #     clauses.append(PackDetails.batch_id == batch_id)
    #     clauses.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS])
    #
    #     last_delivery_date_query = PackHeader.select(PackHeader.scheduled_delivery_date).dicts() \
    #                                 .join(PackDetails, on=PackDetails.pack_header_id == PackHeader.id) \
    #                                 .where(*clauses) \
    #                                 .order_by(PackHeader.scheduled_delivery_date.desc()) \
    #                                 .limit(1)
    #     for data in last_delivery_date_query:
    #         last_delivery_date = data["scheduled_delivery_date"]
    #
    #     if not last_delivery_date:
    #         logger.info(f"In get_pending_pack_count_of_working_day, last_delivery_date:{last_delivery_date}")
    #         return []
    #
    #     date = datetime.datetime.now(pytz.timezone(time_zone))
    #     day = date.strftime('%a')  # gives Mon for the monday, Tue for the tuesday ... .. .
    #     day_count = date.isoweekday() # for the monday, day_count=1 | tuesday, day_count = 2 | ... .. .
    #     # current_day = current_date.isoweekday()
    #     if last_delivery_date.date() < date.date():
    #         logger.error("last_delivery_date was past date")
    #
    #     if day_count == 7:  # if someone hits API on sunday at that time day_count = 7
    #         date = date + datetime.timedelta(1)
    #         day = date.strftime('%a')
    #         day_count = date.isoweekday()
    #
    #     required_day = 1
    #     while required_day<=3:
    #
    #         if day_count in range(1, 7):   # range(1,7) --> monday to saturday, we will not consider sunday(holiday)
    #
    #             query = PackDetails.select(fn.COUNT(PackDetails.id).alias('pack_count')).dicts() \
    #                         .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
    #                         .where(*clauses,
    #                                PackHeader.scheduled_delivery_date == date.strftime("%Y-%m-%d"))
    #             count = 0
    #             for record in query:
    #                 count = record["pack_count"]
    #
    #             if count == 0:
    #                 date = date + datetime.timedelta(1)
    #                 day = date.strftime('%a')
    #                 day_count = date.isoweekday()
    #                 if day_count not in range(1, 7):
    #                     date = date + datetime.timedelta(1)
    #                     day = date.strftime('%a')
    #                     day_count = date.isoweekday()
    #                 continue
    #
    #             if date.date() == datetime.datetime.now(pytz.timezone(time_zone)).date():
    #                 label = "Today"
    #             else:
    #                 label = day.capitalize() + " " + "(" + date.strftime("%m/%d") + ")"
    #             data = {"label": label, "count": count}
    #
    #             logger.info(f"In get_pending_pack_count_of_working_day, data: {data}")
    #
    #             day_pack_count.append(data)
    #
    #             if date.date() == last_delivery_date.date():
    #                 break
    #
    #             required_day += 1
    #
    #             date = date + datetime.timedelta(1)
    #             day = date.strftime('%a')
    #             day_count = date.isoweekday()
    #             if day_count not in range(1, 7):
    #                 date = date + datetime.timedelta(1)
    #                 day = date.strftime('%a')
    #                 day_count = date.isoweekday()
    #
    #     logger.info(f"In get_pending_pack_count_of_working_day, day_pack_count: {day_pack_count}")
    #
    #     total_pending_packs_query = PackDetails.select(fn.COUNT(PackDetails.id).alias('pending_packs')).dicts() \
    #                                             .where(*clauses)
    #     for data in total_pending_packs_query:
    #         pending_pack_count["count"] = data["pending_packs"]
    #     day_pack_count.append(pending_pack_count)
    #
    #     logger.info(f"In get_pending_pack_count_of_working_day, day_pack_count: {day_pack_count}")
    #     return day_pack_count
    #
    # except (InternalError, IntegrityError, DataError) as e:
    #     logger.error("error in get_pending_pack_count_of_working_day {}".format(e))
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     print(
    #         f"Error in get_pending_pack_count_of_working_day: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
    #     raise e
    # except Exception as e:
    #     logger.error(f"Error in get_pending_pack_count_of_working_day: {e}")
    #     raise e


@log_args_and_response
def get_count_of_done_pack_after_system_start_time(system_start_time, time_zone):
    try:
        logger.info("Inside get_count_of_done_pack_after_system_start_time")

        if time_zone == "Asia/Kolkata":
            system_start_time = system_start_time + " +0530"
        elif time_zone == "US/Pacific":
            system_start_time = system_start_time + " -0700"
        else:
            system_start_time = system_start_time + " +0000"

        system_start_time = datetime.datetime.strptime(system_start_time, "%Y-%m-%d %H:%M:%S %z")
        system_start_time = system_start_time.astimezone(pytz.timezone('UTC'))
        # system_start_time = system_start_time.strftime("%Y-%m-%d %H:%M:%S")

        done_packs = 0

        logger.info(f"In get_count_of_done_pack_after_system_start_time, system_start_time in utc: {system_start_time}")

        query = PackDetails.select(fn.COUNT(PackDetails.id).alias("total_done_packs")).dicts() \
            .where(
            PackDetails.filled_at << [settings.FILLED_AT_DOSE_PACKER, settings.FILLED_AT_MANUAL_VERIFICATION_STATION],
            PackDetails.filled_date >= system_start_time)

        for data in query:
            done_packs = data["total_done_packs"]

        logger.info(
            f"In get_count_of_done_pack_after_system_start_time, done_packs: {done_packs} after {system_start_time}")

        return done_packs

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pending_pack_count_of_working_day {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pending_pack_count_of_working_day: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error(f"Error in get_pending_pack_count_of_working_day: {e}")
        raise e


@log_args_and_response
def get_pending_pack_data_by_batch(batch_id: int) -> list:
    """
    Function to get pending pack details
    @param batch_id:
    """

    try:
        query = PackDetails.select(PackDetails.id,
                                   PackDetails.order_no,
                                   fn.DATE(PackHeader.scheduled_delivery_date).alias('scheduled_delivery_date')).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .where(PackDetails.batch_id == batch_id,
                   PackDetails.pack_status == settings.PENDING_PACK_STATUS) \
            .group_by(PackDetails.id) \
            .order_by(PackDetails.order_no)

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pending_pack_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pending_pack_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pending_packs_data_by_batch(batch_id):
    """
       Function to get pending pack details
       @param batch_id:
    """
    pack_info: dict = dict()
    try:
        select_fields = [
            PackDetails.id.alias('pack_id'),
            PackDetails.order_no,
            fn.DATE(PackHeader.scheduled_delivery_date).alias("scheduled_delivery_date"),
            # PackAnalysisDetails.canister_id,
            # PackAnalysisDetails.device_id,
            fn.COUNT(Clause(SQL('DISTINCT'), fn.IF(PackAnalysisDetails.canister_id.is_null(False)
                                                   & PackAnalysisDetails.device_id.is_null(False), DrugMaster.id,
                                                   None))).alias("canister_drug_count"),
            fn.COUNT(Clause(SQL('DISTINCT'), fn.IF((PackAnalysisDetails.device_id.is_null(True) |
                                                    PackAnalysisDetails.canister_id.is_null(
                                                        True) | SlotDetails.quantity << settings.DECIMAL_QTY_LIST),
                                                   SlotDetails.drug_id,
                                                   None))).alias("manual_drug_count"),

        ]
        query = PackDetails.select(*select_fields) \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .where(PackDetails.batch_id == batch_id,
                   PackDetails.pack_status == settings.PENDING_PACK_STATUS) \
            .order_by(PackDetails.order_no) \
            .group_by(PackDetails.id)

        for record in query.dicts():
            pack_info[record['pack_id']] = record

        return pack_info

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pending_packs_data_by_batch {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_pending_packs_data_by_batch {}".format(e))
        raise e


@log_args_and_response
def get_manual_packs_by_batch_id(batch_id: int) -> list:
    """
    function to get manual pack list by batch id
    :return: dict
    """
    try:
        pack_list = BatchManualPacks.db_verify_manual_packs_by_batch_id(batch_id)
        return pack_list

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_pack_status_by_pack_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pack_status_by_pack_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_manual_packs_having_status_skipp_due_to_manual(batch_id):
    try:
        logger.info("Inside get_manual_packs_having_status_skipp_due_to_manual")

        manual_pack_list = []

        if batch_id:

            query = PackAnalysis.select(PackAnalysis.pack_id).dicts() \
                .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
                .where(PackAnalysis.batch_id == batch_id, PackDetails.pack_status.not_in([settings.DELETED_PACK_STATUS]),
                       PackAnalysisDetails.status == constants.SKIPPED_DUE_TO_MANUAL_PACK) \
                .group_by(PackAnalysis.pack_id)

            for data in query:
                manual_pack_list.append(data["pack_id"])

        return manual_pack_list

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_manual_packs_having_status_skipp_due_to_manual {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_packs_having_status_skipp_due_to_manual: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def db_add_batch_manual_packs_dao(manual_pack_list: List[int], batch_id: int, user_id: int) -> bool:
    try:
        return BatchManualPacks.db_add_batch_manual_packs(pack_ids=manual_pack_list, batch_id=batch_id, user_id=user_id)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_add_batch_manual_packs_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_create_manual_packs_dao(manual_pack_list: List[int], pending_manual_packs: List[int], batch_id: int,
                                   user_id: int) -> bool:
    try:
        return BatchManualPacks.db_get_create_manual_packs(pack_id_list=manual_pack_list,
                                                           pending_manual_packs=pending_manual_packs, batch_id=batch_id,
                                                           user_id=user_id)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_get_create_manual_packs_dao {}".format(e))
        raise e


@log_args_and_response
def get_pack_data_for_change_pack_status(pack_id_list: list, system_id: int,
                                         pack_status: Optional[list] = None) -> List:
    """
    function to get pack list to change pack status
    :return: dict
    """
    pack_id_list_data = []
    try:
        clauses = [PackDetails.system_id == system_id]

        if pack_status:
            clauses.append(PackDetails.pack_status << pack_status)

        if len(pack_id_list) == 0:
            query = PackDetails.select(PackDetails.id).join(PackQueue, on=PackQueue.pack_id == PackDetails.id).where(
                functools.reduce(operator.and_, clauses))
            for record in query.dicts():
                pack_id_list_data.append(record["id"])
        else:
            clauses.append(PackDetails.id << pack_id_list)
            query = PackDetails.select(PackDetails.id).join(PackQueue, on=PackQueue.pack_id == PackDetails.id).where(
                functools.reduce(operator.and_, clauses))
            for record in query.dicts():
                pack_id_list_data.append(record["id"])

        return pack_id_list_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_data_for_change_pack_status {}".format(e))
        raise e


@log_args_and_response
def get_pack_queue_by_conveyor_id_pagination_data(filter_fields: [dict, None], sort_fields: [list, None],
                                                  paginate: [dict, None],
                                                  system_id: int, drug_list: [list, None], only_manual: bool):
    """
    @param paginate:
    @param filter_fields:
    @param drug_list:
    @param sort_fields:
    @param only_manual:
    @param batch_id:
    @param system_id:
    @return:
    """
    debug_mode_flag = False
    clauses_having: list = list()
    selected_drug_details: list = list()
    subclauses: list = list()
    order_list: list = list()
    try:
        if filter_fields and filter_fields.get('patient_name', None) is not None:
            if (filter_fields['patient_name']).isdigit():
                patient_id = int(filter_fields['patient_name'])
                filter_fields['patient_id'] = patient_id
                filter_fields.pop('patient_name')

            elif is_date(filter_fields['patient_name']) and filter_fields['patient_name'][0].isdigit():
                patient_dob = convert_dob_date_to_sql_date(filter_fields['patient_name'])
                filter_fields['patient_dob'] = patient_dob
                filter_fields.pop('patient_name')

        if filter_fields is not None and len(filter_fields) > 0:
            if 'delivery_date' in filter_fields.keys():
                delivery_date_list: list = list()
                for date in filter_fields['delivery_date']:
                    d_date = datetime.datetime.strptime(date, "%m-%d-%Y")
                    delivery_date_list.append(d_date.strftime("%Y-%m-%d"))
                filter_fields['delivery_date'] = delivery_date_list

        if filter_fields and filter_fields.get('pack_display_id') and filter_fields.get('pack_id'):
            debug_mode_flag = True
        elif filter_fields and filter_fields.get('pack_display_id') and not filter_fields.get('pack_id'):
            debug_mode_flag = False

        DrugMasterAlias = DrugMaster.alias()
        fields_dict = {
            # do not give alias here, instead give it in select_fields,
            # as this can be reused in where clause
            "pack_sequence": PackDetails.order_no,
            "pack_display_id": PackDetails.pack_display_id,
            "patient_name": PatientMaster.concated_patient_name_field(),
            "patient_id": PatientMaster.patient_no,
            "patient_dob": PatientMaster.dob,
            "pack_status_id": PackDetails.pack_status.alias('status_code'),
            "facility_name": FacilityMaster.facility_name,
            "car_id": PackDetails.car_id,
            "admin_period": fn.CONCAT(PackDetails.consumption_start_date, ' to ', PackDetails.consumption_end_date),
            "delivery_date": PackHeader.scheduled_delivery_date,
            "pack_status": CodeMaster.value,
            # "robot_id_list" : PackAnalysisDetails.robot_id
            "device_id_list": fn.GROUP_CONCAT(Clause(
                SQL('Distinct'),
                fn.IF(PackAnalysisDetails.device_id.is_null(False), PackAnalysisDetails.device_id,
                      MfdAnalysis.dest_device_id),
                SQL('ORDER BY'),
                fn.IF(PackAnalysisDetails.device_id.is_null(False), PackAnalysisDetails.device_id,
                      MfdAnalysis.dest_device_id),
            )).coerce(False),

            "canister_drug_count": fn.COUNT(Clause(SQL('DISTINCT'),
                                                   fn.IF(PackAnalysisDetails.canister_id.is_null(False)
                                                         & PackAnalysisDetails.device_id.is_null(False),
                                                         DrugMasterAlias.id,
                                                         None))),
            "manual_drug_count": (fn.COUNT(Clause(SQL('DISTINCT'),
                                                  fn.IF((PackAnalysisDetails.device_id.is_null(True) |
                                                         PackAnalysisDetails.canister_id.is_null(
                                                             True) | SlotDetails.quantity << settings.DECIMAL_QTY_LIST),
                                                        SlotDetails.drug_id,
                                                        None)))),
            "ndc_list": fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(DrugMaster.ndc.is_null(True),
                                                                 'null', DrugMaster.ndc)),
                                               SQL(" SEPARATOR ' , ' "))).coerce(False),
            "pack_id": PackDetails.id
        }

        select_fields = [fields_dict['pack_id'].alias('pack_id'),
                         PackDetails.pack_display_id,
                         PackAnalysis.manual_fill_required.alias('manual_fill_require'),
                         PackDetails.order_no,  # .alias('pack_sequence'),
                         PackDetails.pack_plate_location.alias('pack_location'),
                         PatientMaster.patient_no.alias('patient_id'),
                         PatientMaster.dob.alias('patient_dob'),
                         fields_dict['pack_status'].alias('pack_status'),
                         fields_dict['car_id'],
                         fields_dict['facility_name'],
                         fields_dict['patient_name'].alias('patient_name'),
                         fields_dict["admin_period"].alias("admin_period"),
                         fields_dict['delivery_date'].alias('delivery_date'),
                         PackDetails.pack_status.alias('pack_status_code'),
                         fields_dict['device_id_list'].alias('device_id_list'),
                         fields_dict['ndc_list'].alias('ndc_list'),
                         fn.COUNT(fn.DISTINCT(SlotDetails.drug_id)).alias("total_drug_count"),
                         fields_dict['canister_drug_count'].alias('canister_drug_count'),
                         fields_dict['manual_drug_count'].alias('manual_drug_count'),
                         fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.status_id)).alias('mfd_status'),
                         fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysisDetails.canister_id)).coerce(False).alias(
                             'canister_ids'),

                         fn.GROUP_CONCAT(Clause(SQL('DISTINCT'), Clause(
                             fn.CONCAT(SlotDetails.drug_id, ',',
                                       fn.IF((PackAnalysisDetails.device_id.is_null(True)) |
                                             (PackAnalysisDetails.canister_id.is_null(True)) | (
                                                     SlotDetails.quantity << settings.DECIMAL_QTY_LIST), 'null', None)
                                       ), SQL("SEPARATOR '|' ")))).coerce(False).alias('manual_drug_ids'),
                         ExtPackDetails.ext_status_id.alias('ext_pack_status_id'),
                         PackStatusTracker.reason.alias('reason')
                         ]

        clauses = [
            PackDetails.system_id == system_id,
            PackUserMap.id.is_null(True),
            PackDetails.pack_status.not_in(settings.PACK_QUEUE_STATUS_IGNORE)
        ]

        clauses_having = add_having_clauses(clauses_having, fields_dict, filter_fields)

        if debug_mode_flag:
            like_search_list = ['patient_name', 'patient_dob', 'admin_period', 'facility_name']
            exact_search_list = ['patient_id', 'car_id']
            membership_search_list = ['pack_status', 'delivery_date']
            having_search_list = ['device_id_list']
            string_search_field = [fields_dict['pack_display_id'], fields_dict['pack_id']]
            multi_search_fields = [filter_fields['pack_display_id']]
            clauses = get_multi_search(clauses, multi_search_fields, string_search_field)

        else:
            like_search_list = ['patient_name', 'patient_dob', 'admin_period', 'facility_name',
                                'pack_display_id']
            exact_search_list = ['patient_id', 'car_id']
            membership_search_list = ['pack_status', 'delivery_date']
            having_search_list = ['device_id_list']

        if drug_list:
            selected_drug_details = DrugMaster.get_drugs_details_by_ndclist(ndc_list=drug_list)
            for ndc in drug_list:
                ndc = "%" + ndc + "%"
                subclauses.append((fields_dict["ndc_list"] ** ndc))
            clauses_having.append((functools.reduce(operator.or_, subclauses)))

        if only_manual:
            logger.info("only manual")
            clauses.append((PackAnalysis.manual_fill_required == 1))

        if sort_fields:
            order_list.extend(sort_fields)

        if len(order_list) == 0:
            order_list.insert(0, ["pack_sequence", 1])

        sub_query = ExtPackDetails.select(fn.MAX(ExtPackDetails.id).alias('max_ext_pack_details_id'),
                                          ExtPackDetails.pack_id.alias('pack_id')) \
            .group_by(ExtPackDetails.pack_id).alias('sub_query')

        sub_query_reason = PackStatusTracker.select(fn.MAX(PackStatusTracker.id).alias('max_pack_status_id'),
                                                    PackStatusTracker.pack_id.alias('pack_id')) \
            .group_by(PackStatusTracker.pack_id).alias('sub_query_reason')

        query = PackDetails.select(*select_fields) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(PackAnalysis, JOIN_LEFT_OUTER, on=((PackAnalysis.id == PackAnalysisDetails.analysis_id) &
                                                     (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=((DeviceMaster.id == PackAnalysisDetails.device_id) |
                                                     (DeviceMaster.id == MfdAnalysis.dest_device_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DrugMasterAlias, JOIN_LEFT_OUTER, on=(DrugMasterAlias.id == CanisterMaster.drug_id)) \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=(PackUserMap.pack_id == PackDetails.id)) \
            .join(sub_query, JOIN_LEFT_OUTER, on=(sub_query.c.pack_id == PackDetails.id)) \
            .join(ExtPackDetails, JOIN_LEFT_OUTER, on=ExtPackDetails.id == sub_query.c.max_ext_pack_details_id) \
            .join(sub_query_reason, JOIN_LEFT_OUTER, on=(sub_query_reason.c.pack_id == PackDetails.id)) \
            .join(PackStatusTracker, JOIN_LEFT_OUTER, on=PackStatusTracker.id == sub_query_reason.c.max_pack_status_id) \
            .group_by(PackDetails.id)

        results, count, non_paginate_result = get_results(query.dicts(), fields_dict, filter_fields=filter_fields,
                                                          clauses=clauses, clauses_having=clauses_having,
                                                          sort_fields=order_list,
                                                          paginate=paginate,
                                                          exact_search_list=exact_search_list,
                                                          like_search_list=like_search_list,
                                                          membership_search_list=membership_search_list,
                                                          having_search_list=having_search_list,
                                                          non_paginate_result_field_list=['pack_id',
                                                                                          'manual_drug_count',
                                                                                          'device_id_list']
                                                          )

        return results, count, non_paginate_result, selected_drug_details

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_queue_by_conveyor_id_pagination_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pack_queue_by_conveyor_id_pagination_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_pack_queue_by_conveyor_id_pagination_data {}".format(e))
        raise e


@log_args_and_response
def get_facility_data_by_batch(batch_id: int):
    """
        This function will be used to get facility data by batch and pending pack ids
        :return: List
        @param batch_id:
    """
    try:
        facility_delivery_date_dict: dict = dict()
        facility_name_id_dict: dict = dict()
        query = PackDetails.select(PackDetails.id,
                                   fn.MIN(fn.DATE(PackHeader.scheduled_delivery_date)).alias('delivery_date'),
                                   FacilityMaster.facility_name,
                                   PatientMaster.first_name,
                                   PatientMaster.last_name,
                                   FacilityMaster.id.alias('facility_id'),
                                   PatientMaster.id.alias('patient_id')) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.batch_id == batch_id, PackDetails.pack_status << [settings.PENDING_PACK_STATUS]) \
            .group_by(FacilityMaster.id)

        for record in query.dicts():
            facility_delivery_date_dict[record['facility_name']] = record['delivery_date']
            facility_name_id_dict[record['facility_name']] = record['facility_id']
        return facility_delivery_date_dict, facility_name_id_dict
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_facility_data_by_batch {}".format(e))
        raise e


@log_args_and_response
def get_facility_data_by_packs(pack_list: list):
    """
        This function will be used to get facility data by pack ids
        :return: List
        @param pack_list:
    """
    try:
        facility_delivery_date_dict: dict = dict()
        facility_name_id_dict: dict = dict()
        query = PackDetails.select(PackDetails.id,
                                   fn.MIN(fn.DATE(PackHeader.scheduled_delivery_date)).alias('delivery_date'),
                                   FacilityMaster.facility_name,
                                   PatientMaster.first_name,
                                   PatientMaster.last_name,
                                   FacilityMaster.id.alias('facility_id'),
                                   PatientMaster.id.alias('patient_id')) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.id << pack_list) \
            .group_by(FacilityMaster.id)

        for record in query.dicts():
            facility_delivery_date_dict[record['facility_name']] = record['delivery_date']
            facility_name_id_dict[record['facility_name']] = record['facility_id']
        return facility_delivery_date_dict, facility_name_id_dict
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_facility_data_by_packs {}".format(e))
        raise e


@log_args_and_response
def get_device_id_for_pack_by_batch(batch_id: int):
    """
    Function to get device list given pack list of a batch
    @param batch_id:
    @return:
    """
    pack_device_dict = dict()

    try:
        query = PackDetails.select(PackDetails.id,
                                   fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(PackAnalysisDetails.device_id.is_null(True),
                                                                            MfdAnalysis.dest_device_id,
                                                                            PackAnalysisDetails.device_id)))).coerce(
                                       False).alias('device_id'),
                                   ) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .where(PackDetails.batch_id == batch_id, PackDetails.pack_status << [settings.PENDING_PACK_STATUS]) \
            .group_by(PackDetails.id)

        for record in query.dicts():
            device_id_list = list(record['device_id'].split())
            for each_device in device_id_list:
                if each_device is not None:
                    pack_device_dict[record['id']] = each_device
                    break

        return pack_device_dict

    except DoesNotExist as e:
        logger.error("Error in get_device_id_for_pack_by_batch {}".format(e))
        raise
    except Exception as e:
        logger.error("Error in get_device_id_for_pack_by_batch {}".format(e))
        raise


@log_args_and_response
def get_done_pack_count_by_time_filter(start_time, end_time, system_id):
    """
    Function to get pack count of done packs for given batch for three conditions.
    1) done packs in last one hour
    2) done packs in last one day
    3) done packs till date
    @param TZ:
    @param time_zone:
    @param batch_id:
    @return:
    """
    try:
        filled_by_robot = [settings.FILLED_AT_MANUAL_VERIFICATION_STATION, settings.FILLED_AT_DOSE_PACKER]

        clauses = [PackDetails.pack_status << [settings.DONE_PACK_STATUS,
                                               settings.PROCESSED_MANUALLY_PACK_STATUS,
                                               settings.PARTIALLY_FILLED_BY_ROBOT],
                   PackDetails.filled_at.in_(filled_by_robot),
                   PackDetails.system_id == system_id]

        pack_count = PackDetails.get_pack_count_by_clauses(clauses,
                                                           fn.CONVERT_TZ(PackDetails.modified_date, settings.TZ_UTC,
                                                                         settings.TZ_UTC).between(start_time, end_time))
        return pack_count
    except Exception as e:
        logger.error("error in get_done_pack_count {}".format(e))
        raise e


@log_args_and_response
def get_pack_count_by_device_id_retail(system_id: int, device_id: Optional[list] = None):
    """
    Function to pack count by device id (Robot ids)
    @param device_id:
    @param system_id:
    @param batch_id:
    @return:
    """
    clauses: list = list()
    try:

        clauses.append(PackDetails.system_id == system_id)

        if device_id is not None:
            clauses.append(PackAnalysisDetails.device_id << device_id)

        query = PackDetails.select(PackDetails.id,
                                   PackAnalysisDetails.device_id,
                                   PackDetails.pack_status, PackDetails.filled_at).dicts() \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(PackDetails.id, PackAnalysisDetails.device_id)

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_count_by_device_id {}".format(e))
        raise e


@log_args_and_response
def get_deleted_pack_count(time_zone, TZ):
    """
    Function to get pack count of done packs for given batch for three conditions.
    1) today deleted packs
    @param TZ:
    @param time_zone:
    @param batch_id:
    @return:
    """
    try:
        clauses = [PackDetails.pack_status << [settings.DELETED_PACK_STATUS]]
        current_date = get_current_datetime_by_timezone(time_zone, return_format="date")
        today_deleted = PackDetails.get_pack_count_by_clauses(clauses, fn.DATE(
            fn.CONVERT_TZ(PackDetails.modified_date, settings.TZ_UTC, TZ)) == current_date)

        logger.info("In get_done_pack_count: today deleted pack count: {}".format(today_deleted))
        return today_deleted
    except Exception as e:
        logger.error("error in get_deleted_pack_count {}".format(e))
        raise e


@log_args_and_response
def db_get_trolley_wise_pack(system_id: int, trolley_seq: list):
    """
    Function to pack count by device id (Robot ids)
    @param device_id:
    @param system_id:
    @param batch_id:
    @return:
    """
    clauses: list = list()
    try:

        query = MfdAnalysis.select(MfdAnalysis.trolley_seq, PackDetails.id, PackDetails.order_no,
                                   MfdAnalysis.order_no.alias("mfd_order_no"), MfdAnalysisDetails.analysis_id,
                                   MfdAnalysis.trolley_location_id, MfdAnalysis.assigned_to,
                                   MfdAnalysis.mfs_device_id,
                                   DeviceMaster.system_id,
                                   PackDetails.pack_status,
                                   MfdAnalysis.dest_device_id,
                                   MfdAnalysis.status_id).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == MfdAnalysis.mfs_device_id) \
            .where(MfdAnalysis.trolley_seq << trolley_seq, PackDetails.system_id == system_id) \
            .group_by(MfdAnalysis.id).order_by(PackDetails.order_no)

        return list(query)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_count_by_device_id {}".format(e))
        raise e


def db_get_trolley_wise_pack_patient_data(system_id, pack_list, paginate, filter_fields):
    """
    Function to pack count by device id (Robot ids)
    @param device_id:
    @param system_id:
    @param batch_id:
    @return:
    """
    clauses: list = list()
    try:
        fields_dict = {
            "pack_sequence": PackDetails.order_no,
            "pack_display_id": PackDetails.pack_display_id,
            "pack_id": PackDetails.id,
            "patient_name": PatientMaster.concated_patient_name_field(),
            "patient_id": PatientMaster.patient_no,
            "admin_period": fn.CONCAT(PackDetails.consumption_start_date, ' to ', PackDetails.consumption_end_date),
            "delivery_date": PackHeader.scheduled_delivery_date,
            "facility_name": FacilityMaster.facility_name
        }
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        query = MfdAnalysis.select(MfdAnalysis.trolley_seq,
                                   PackDetails.batch_id,
                                   fields_dict['pack_id'].alias('pack_id'),
                                   fields_dict['pack_sequence'].alias('pack_sequence'),
                                   fields_dict['pack_display_id'].alias('pack_display_id'),
                                   fields_dict['patient_name'].alias('patient_name'),
                                   fields_dict['patient_id'].alias('patient_id'),
                                   fields_dict['delivery_date'].alias('delivery_date'),
                                   fields_dict['admin_period'].alias('admin_period'),
                                   fields_dict['facility_name'],
                                   PackDetails.id,
                                   PackDetails.pack_status,
                                   MfdAnalysis.transferred_location_id,
                                   MfdAnalysis.order_no.alias("mfd_order_no"),
                                   MfdAnalysisDetails.analysis_id,
                                   MfdAnalysis.status_id,
                                   LocationMaster.device_id,
                                   fn.IF(DeviceMasterAlias.device_type_id ==  settings.DEVICE_TYPES['ROBOT'], True, False).alias("in_robot"),
                                   DeviceMaster.name.alias("device_name"),
                                   PackDetails.pack_header_id).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id==LocationMasterAlias.id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id==DeviceMasterAlias.id) \
            .join(LocationMaster,JOIN_LEFT_OUTER, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster,JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, on=PatientRx.patient_id == PatientMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                   PackDetails.system_id == system_id,
                   MfdAnalysis.status_id.not_in(
                       [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                        constants.MFD_CANISTER_MVS_FILLING_REQUIRED])) \
            .group_by(MfdAnalysis.id) \
            .order_by(PackDetails.order_no)

        like_search_list = ['patient_name', 'admin_period', 'facility_name',
                            'pack_display_id']
        exact_search_list = ['patient_id', 'pack_display_id']
        membership_search_list = ['delivery_date']
        
        # result, count = get_results(query,fields_dict, filter_fields=filter_fields,
        #                             like_search_list=like_search_list,
        #                             exact_search_list=exact_search_list,
        #                             membership_search_list=membership_search_list
        #                             )

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_trolley_wise_pack_patient_data: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in db_get_trolley_wise_pack_patient_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_mfs_filling_progress_trolley():
    """
    Function to pack count by device id (Robot ids)
    @param device_id:
    @param system_id:
    @param batch_id:
    @return:
    """
    trolley_seq = []
    try:
        query = TempMfdFilling.select(MfdAnalysis.trolley_seq).dicts().join(MfdAnalysis,
                    on=MfdAnalysis.id == TempMfdFilling.mfd_analysis_id).group_by(MfdAnalysis.trolley_seq)
        trolley_seq = [record['trolley_seq'] for record in query]
        return trolley_seq

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_trolley_wise_pack_patient_data: {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in db_get_trolley_wise_pack_patient_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
