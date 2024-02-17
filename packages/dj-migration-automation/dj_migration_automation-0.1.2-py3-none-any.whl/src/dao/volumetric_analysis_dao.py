import datetime
import decimal
import functools
import operator
import os
import sys
from copy import deepcopy
from datetime import timedelta
from functools import reduce
from itertools import chain
from peewee import InternalError, IntegrityError, JOIN_LEFT_OUTER, fn, SQL, DataError, Clause

import settings
from dosepack.base_model.base_model import between_expression
from dosepack.utilities.utils import log_args, log_args_and_response, get_current_date_time
from src import constants
from src.api_utility import apply_paginate, get_orders, get_filters, get_results
from src.api_utility import get_multi_search, get_results
from src.dao.batch_dao import db_get_last_imported_batch_by_system_dao, get_last_done_batch, get_current_batch
from src.dao.drug_canister_stick_dao import db_get_drugs_for_rule_query_sscp, db_get_drugs_for_rule_query_cscp, \
    db_get_drugs_for_rule_query_dcp
from src.dao.drug_dao import get_custome_drug_shape_by_id, get_ordered_list, dpws_paginate
from src.model.model_canister_orders import CanisterOrders
from src.model.model_drug_tracker import DrugTracker
from src.service.drug_search import get_ndc_list_for_barcode
from src.model.model_batch_master import BatchMaster
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_parameters import CanisterParameters
from src.model.model_canister_stick import CanisterStick
from src.model.model_change_ndc_history import ChangeNdcHistory
from src.model.model_code_master import CodeMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_custom_shape_canister_parameters import CustomShapeCanisterParameters
from src.model.model_device_master import DeviceMaster
from src.model.model_dosage_type import DosageType
from src.model.model_drug_canister_parameters import DrugCanisterParameters
from src.model.model_drug_canister_stick_mapping import DrugCanisterStickMapping
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_dimention_history import DrugDimensionHistory
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_shape_fields import DrugShapeFields
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_frequent_mfd_drugs import FrequentMfdDrugs
from src.model.model_generate_canister import GenerateCanister
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_user_map import PackUserMap
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_slot_details import SlotDetails
from src.model.model_small_canister_stick import SmallCanisterStick
from src.model.model_small_stick_canister_parameters import SmallStickCanisterParameters
from src.model.model_store_separate_drug import StoreSeparateDrug
from src.model.model_unique_drug import UniqueDrug
from utils.auth_webservices import send_email_mismatched_auto_and_manual_drug_shapes
from utils.drug_inventory_webservices import get_current_inventory_data

logger = settings.logger


@log_args
def get_drug_dimension_info(company_id: int, filter_fields: [dict, None], sort_fields: [list, None],
                            paginate: [dict, None]) -> tuple:
    """
    function to get drug dimension info for drug_dimension screen(all drug with dimension and drug without dimension which is present in patient rx)
    @param paginate:
    @param sort_fields:
    @param filter_fields:
    @param company_id:
    @return:
    """

    status_list: list = list()
    clauses: list = list()
    order_list: list = list()
    drug_with_dimension_list: list = list()
    drug_without_dimension_list: list = list()
    extend_list = False
    add_count = False
    mfd_query_pending = False
    high_priority_drug_list: list = list()
    subclauses: list = list()
    drug_dimension_id_list = list()
    auto_dimension = list()
    auto_dimension_data_query = list()
    result1 = list()
    mfd_drugs = None
    unique_drug_qty_map = dict()
    drug_list = list()

    try:
        # apply filter of verification_status in drug dimension screen
        if filter_fields and "verification_status" in filter_fields and filter_fields['verification_status'] is not None:

            for status in filter_fields['verification_status']:
                if status == "Rejected":
                    status_list.append(settings.VERIFICATION_REJECTED_FOR_DRUG)

                if status == "Verification Pending":
                    status_list.append(settings.VERIFICATION_PENDING_FOR_DRUG)

                if status == "Verified":
                    status_list.append(settings.VERIFICATION_DONE_FOR_DRUG)

                # in case of checkbox we have to pass verification_status_id is null in or clause
                if status == "Pending":
                    mfd_query_pending = True
                    subclauses.append(DrugDimension.verification_status_id.is_null(True))
            if status_list:
                subclauses.append(DrugDimension.verification_status_id.in_(status_list))

            filter_fields['verification_status'].clear()

        fields_dict = {
            'drug_name': DrugMaster.concated_drug_name_field(include_ndc=True),
            'txr': DrugMaster.txr,
            'ndc': DrugMaster.ndc,
            'shape': CustomDrugShape.name,
            'shape_id': DrugDimension.shape,
            'accurate_volume': DrugDimension.accurate_volume,
            'approx_volume': DrugDimension.approx_volume,
            'width': DrugDimension.width,
            'depth': DrugDimension.depth,
            'length': DrugDimension.length,
            'fillet': DrugDimension.fillet,
            'dosage_type_name': DosageType.name,
            'dosage_type_code': DosageType.code,
            'dosage_type_id': DosageType.id,
            'fndc_txr': fn.CONCAT(DrugMaster.formatted_ndc, '_', fn.IFNULL(DrugMaster.txr, '')),
            'verification_status': DrugDimension.verification_status_id,
            'verified_date': fn.IF((DrugDimension.verified_date.is_null(False) &
                                    DrugDimension.verification_status_id << (
                                        [settings.VERIFICATION_REJECTED_FOR_DRUG,
                                         settings.VERIFICATION_PENDING_FOR_DRUG]),
                                    None, DrugDimension.verified_date)),
            'id': UniqueDrug.id,
            "total_qty": fn.SUM(MfdAnalysisDetails.quantity),
            "top_five_mfd_drug": fn.IF(FrequentMfdDrugs.id.is_null(True), 0, 1)
        }
        select_fields = [
                            DrugMaster.id.alias('drug_id'),
                            DrugMaster.ndc,
                            DrugMaster.formatted_ndc,
                            DrugMaster.strength,
                            DrugMaster.strength_value,
                            DrugMaster.manufacturer,
                            DrugMaster.txr,
                            DrugMaster.imprint,
                            DrugMaster.color,
                            DrugMaster.image_name,
                            DrugMaster.brand_flag,
                            DrugMaster.brand_drug,
                            DrugMaster.drug_form,
                            fields_dict['id'].alias('unique_drug_id'),
                            UniqueDrug.lower_level,
                            UniqueDrug.drug_usage,
                            UniqueDrug.is_powder_pill,
                            UniqueDrug.packaging_type,
                            UniqueDrug.coating_type,
                            UniqueDrug.is_zip_lock_drug,
                            DrugDimension.width,
                            DrugDimension.length,
                            DrugDimension.depth,
                            UniqueDrug.unit_weight,
                            fields_dict['fillet'],
                            DrugDimension.approx_volume,
                            DrugDimension.accurate_volume,
                            DrugDimension.verified_by,
                            DrugDimension.rejection_note,
                            DrugDimension.modified_by,
                            DrugDimension.modified_date,
                            DrugDimension.id.alias('drug_dimension_id'),
                            DrugMaster.shape.alias('drug_shape'),
                            fields_dict['shape'].alias('shape'),
                            fields_dict['shape_id'].alias('shape_id'),
                            fields_dict['drug_name'].alias('drug_name'),
                            fields_dict['fndc_txr'].alias('fndc_txr'),
                            CodeMaster.id.alias("code_id"),
                            fields_dict['verification_status'].alias('drug_dimension_status'),
                            fn.IF(fields_dict['verification_status'].is_null(True), 'Pending',
                                  fn.IF(fields_dict['verification_status'] == settings.VERIFICATION_PENDING_FOR_DRUG,
                                        "Verification Pending", CodeMaster.value)).alias('verification_status'),
                            fields_dict['verified_date'].alias('verified_date'),
                            fields_dict['dosage_type_name'].alias('dosage_type_name'),
                            fields_dict['dosage_type_code'].alias('dosage_type_code'),
                            fields_dict['dosage_type_id'].alias('dosage_type_id'),
                            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
                            fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                  DrugDetails.last_seen_by).alias('last_seen_with'),
                            fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                                  DrugDetails.last_seen_date).alias('last_seen_on'),
                            fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.id)).coerce(False).alias('canister_ids'),
                            GenerateCanister.requested_canister_count,
                            fn.GROUP_CONCAT(Clause(fn.DISTINCT(DrugDimensionHistory.image_name),SQL(" SEPARATOR ',' "))).alias('drug_dimension_image'),
                            fn.MAX(DrugDimensionHistory.id).alias("drug_dimension_history_id")
        ]
        # append clauses and select_fields for current pack_queue
        if "current_batch_usage" in filter_fields:
            pack_ids = PackQueue.get_pack_ids_pack_queue()
            logger.info("In_progress_batch_found_for_system: {}".format(3))
            if not pack_ids:
                return [], 0
            # select_fields.append(fn.SUM(MfdAnalysisDetails.quantity).alias("total_qty"))
            select_fields.append(FrequentMfdDrugs.id.alias("frequent_mfd_drug_id"))
            select_fields.append(fn.IF(FrequentMfdDrugs.id.is_null(True), 0, 1).alias("top_five_mfd_drug"))
            fields = select_fields.copy()
            clauses.append(PackDetails.id << pack_ids)
            clauses.append(FrequentMfdDrugs.id.is_null(True))

            select_fields.append(fn.SUM(MfdAnalysisDetails.quantity).alias("total_qty"))

        # add created date in field_dict if we get fileter of custom time period
        if "created_date" in filter_fields:
            fields_dict["created_date"] = fn.DATE(PackDetails.created_date)

        between_search_fields = ['width', 'length', 'depth', 'fillet', 'accurate_volume', 'approx_volume',
                                 'created_date']
        exact_search_fields = ['id']
        like_search_fields = ['drug_name', 'txr', 'shape']
        membership_search_fields = ['fndc_txr', 'verification_status']

        global_search = [DrugMaster.concated_drug_name_field(), DrugMaster.ndc]

        # add clause for global search(search by ndc and drug_name)
        if filter_fields and filter_fields.get('global_search', None) is not None:
            multi_search_string = filter_fields['global_search'].split(',')
            multi_search_string.remove('') if '' in multi_search_string else multi_search_string
            clauses = get_multi_search(clauses, multi_search_string, global_search)

        # get drug with dimension from drug dimension table
        drug_with_dimension_query = DrugDimension.db_get_drug_dimension_data()
        for Unique_drug_id in drug_with_dimension_query.dicts():
            drug_with_dimension_list.append(Unique_drug_id['unique_drug_id'])
        logger.info("In get_drug_dimension_info: drug_with_dimension_list: {} ".format(drug_with_dimension_list))

        # get last 3 months date
        current_date = datetime.datetime.now().date()
        days_before = int(constants.TOTAL_MONTHS) * settings.days_in_month
        month_back_date = current_date - timedelta(days=days_before)

        # get unique drugs which are used in pharmacy (present in rx) and does not have drug_dimension
        # patient_drug_query = DrugMaster.select(UniqueDrug.id).dicts() \
        #     .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
        #                           fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
        #                          (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
        #     .join(SlotDetails, on=SlotDetails.drug_id == DrugMaster.id) \
        #     .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
        #     .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
        #     .where(UniqueDrug.id.not_in(drug_with_dimension_list),
        #            PackDetails.company_id == company_id, PackDetails.created_date > month_back_date)\
        #     .group_by(UniqueDrug.id)
        #
        # for record in patient_drug_query:
        #     drug_without_dimension_list.append(record['id'])
        # logger.info("In get_drug_dimension_info: drug_without_dimension_list: {} ".format(drug_without_dimension_list))

        # combine list of drug_with dimension list and drug in patient_rx table
        # unique_drug_id_list = drug_with_dimension_list + drug_without_dimension_list
        # clauses.append(UniqueDrug.id.in_(unique_drug_id_list))

        print("date1", datetime.datetime.now())
        high_priority_drug_query = DrugMaster.select(UniqueDrug.id, SlotDetails.quantity).dicts() \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(SlotDetails, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .where(PackDetails.company_id == company_id,
                   PackDetails.created_date > month_back_date,
                   (DrugDimension.id.is_null(True)) |
                    (DrugDimension.verification_status_id == settings.VERIFICATION_REJECTED_FOR_DRUG))

        for record in high_priority_drug_query:
            if record['id'] not in unique_drug_qty_map:
                unique_drug_qty_map[record['id']] = record['quantity']
            else:
                unique_drug_qty_map[record['id']] += record['quantity']
        print("date2", datetime.datetime.now())
        sorted_drugs = sorted(unique_drug_qty_map.items(), key=operator.itemgetter(1), reverse=True)
        drug_list = [drug[0] for drug in sorted_drugs]
        high_priority_drug_list = drug_list[:settings.HIGH_PRIORITY_PENDING_DRUG_COUNT]
        high_priority_drug_list.reverse()

        unique_drug_id_list = drug_with_dimension_list + drug_list
        clauses.append(UniqueDrug.id.in_(unique_drug_id_list))

        # custom time period filter is apply("created_date" in filter_fields) then add join for batch_master table
        if "created_date" in filter_fields or "current_batch_usage" in filter_fields:
            query = UniqueDrug.select(*select_fields) \
                .join(DrugMaster, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                      fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                     (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .join(DrugDimensionHistory, JOIN_LEFT_OUTER,
                      on=DrugDimension.id == DrugDimensionHistory.drug_dimension_id) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == 1) &
                                                             (DrugStockHistory.company_id == company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                        (DrugDetails.company_id == company_id))) \
                .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == DrugDimension.verification_status_id) \
                .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
                .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == UniqueDrug.dosage_type) \
                .join(SlotDetails, JOIN_LEFT_OUTER, on=SlotDetails.drug_id == DrugMaster.id) \
                .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=SlotDetails.id==MfdAnalysisDetails.slot_id) \
                .join(PackRxLink, JOIN_LEFT_OUTER, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PackDetails, JOIN_LEFT_OUTER, on=PackDetails.id == PackRxLink.pack_id) \
                .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetails.batch_id) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=((CanisterMaster.drug_id == UniqueDrug.drug_id) & (CanisterMaster.rfid.is_null(False)))) \
                .join(GenerateCanister, JOIN_LEFT_OUTER, on=GenerateCanister.drug_id == DrugMaster.id) \
                .join(FrequentMfdDrugs, JOIN_LEFT_OUTER, on=((FrequentMfdDrugs.unique_drug_id == UniqueDrug.id)&(FrequentMfdDrugs.current_pack_queue == 1))) \
                .group_by(UniqueDrug.id)

            if "current_batch_usage" in filter_fields:
                query1 = UniqueDrug.select(*fields,
                                           FrequentMfdDrugs.quantity) \
                    .join(DrugMaster, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                          fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                         (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                    .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                    .join(DrugDimensionHistory, JOIN_LEFT_OUTER,
                          on=DrugDimension.id == DrugDimensionHistory.drug_dimension_id) \
                    .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                                 (DrugStockHistory.is_active == 1) &
                                                                 (DrugStockHistory.company_id == company_id))) \
                    .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                            (DrugDetails.company_id == company_id))) \
                    .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == DrugDimension.verification_status_id) \
                    .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
                    .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == UniqueDrug.dosage_type) \
                    .join(CanisterMaster, JOIN_LEFT_OUTER,
                          on=((CanisterMaster.drug_id == UniqueDrug.drug_id) & (CanisterMaster.rfid.is_null(False)))) \
                    .join(GenerateCanister, JOIN_LEFT_OUTER, on=GenerateCanister.drug_id == DrugMaster.id) \
                    .join(FrequentMfdDrugs,
                          on=((FrequentMfdDrugs.unique_drug_id == UniqueDrug.id) & (FrequentMfdDrugs.current_pack_queue == 1)))
                print(f"filter_fields: {filter_fields}")
                if filter_fields and "verification_status" in filter_fields :
                    if mfd_query_pending:
                        query1 = query1.where(FrequentMfdDrugs.id.is_null(False),
                           FrequentMfdDrugs.current_pack_queue == 1,DrugDimension.verification_status_id.is_null(True))
                    else:
                        query1 = query1.where(FrequentMfdDrugs.id.is_null(False),
                           FrequentMfdDrugs.current_pack_queue == 1, DrugDimension.verification_status_id << status_list)
                else:
                    query1 = query1.where(FrequentMfdDrugs.id.is_null(False),
                           FrequentMfdDrugs.batch_id.is_null(True))
                query1 = query1.group_by(UniqueDrug.id)
                query1 = query1.order_by(FrequentMfdDrugs.quantity.desc())

                result1 = []
                print(f"query1: {query1}")
                for record in query1.dicts():
                    print(record)
                    result1.append(record)
                mfd_drugs = len(result1)

                add_count = True
                if paginate.get("page_number") == 1:
                    extend_list = True
                    paginate["number_of_rows"] = paginate["number_of_rows"] - mfd_drugs

                for record in result1:
                    if record['canister_ids'] is not None:
                        canister_list = list(map(int, record['canister_ids'].split(",")))
                        canister_data_list = get_drug_dimension_canister_data(canister_ids_list=canister_list)
                        record['canister_data_list'] = canister_data_list
                    else:
                        record['canister_data_list'] = []
                    if record['drug_dimension_status'] is None or record['drug_dimension_status'] == \
                            settings.DRUG_VERIFICATION_STATUS['rejected']:
                        record['priority'] = 'high' if record['unique_drug_id'] in high_priority_drug_list else 'low'
                    else:
                        record['priority'] = None
                    if record['drug_dimension_id']:
                        drug_dimension_id_list.append(record['drug_dimension_id'])
        else:
            query = UniqueDrug.select(*select_fields) \
                .join(DrugMaster, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                      fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                     (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .join(DrugDimensionHistory, JOIN_LEFT_OUTER, on=DrugDimension.id == DrugDimensionHistory.drug_dimension_id) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == 1) &
                                                             (DrugStockHistory.company_id == company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                        (DrugDetails.company_id == company_id))) \
                .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == DrugDimension.verification_status_id) \
                .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
                .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == UniqueDrug.dosage_type) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=(
                    (CanisterMaster.drug_id == UniqueDrug.drug_id) & (CanisterMaster.rfid.is_null(False)))) \
                .join(GenerateCanister, JOIN_LEFT_OUTER, on=GenerateCanister.drug_id == DrugMaster.id) \
                .group_by(UniqueDrug.id)

        if high_priority_drug_list:
            order_list.append(SQL('FIELD(unique_drug_id,{})'.format(str(high_priority_drug_list)[1:-1])).desc())

        # orderby based drug in(Pending  -> Rejected -> Verification Pending -> Verified) sequence
        order_list.append(SQL('FIELD(drug_dimension_status,{},{})'.format(settings.VERIFICATION_PENDING_FOR_DRUG,
                                                                          settings.VERIFICATION_DONE_FOR_DRUG)))
        order_list.append(SQL('FIELD(code_id,{})'.format(settings.VERIFICATION_REJECTED_FOR_DRUG)))
        order_list.append(DrugDimension.id.is_null(True))
        if subclauses:
            clauses.append(functools.reduce(operator.or_, subclauses))
        logger.debug(query)
        results, count = get_results(query.dicts(), fields_dict,
                                     filter_fields=filter_fields,
                                     sort_fields=sort_fields,
                                     paginate=paginate,
                                     clauses=clauses,
                                     exact_search_list=exact_search_fields,
                                     like_search_list=like_search_fields,
                                     membership_search_list=membership_search_fields,
                                     between_search_list=between_search_fields,
                                     identified_order=order_list)

        # get canister information from canister ids
        for record in results:
            if record['canister_ids'] is not None:
                canister_list = list(map(int, record['canister_ids'].split(",")))
                canister_data_list = get_drug_dimension_canister_data(canister_ids_list=canister_list)
                record['canister_data_list'] = canister_data_list
            else:
                record['canister_data_list'] = []
            if record['drug_dimension_status'] is None or record['drug_dimension_status'] == settings.DRUG_VERIFICATION_STATUS['rejected']:
                record['priority'] = 'high' if record['unique_drug_id'] in high_priority_drug_list else 'low'
            else:
                record['priority'] = None
            if record['drug_dimension_id']:
                drug_dimension_id_list.append(record['drug_dimension_id'])
        if drug_dimension_id_list:
            sub_query = DrugDimensionHistory.select(fn.MAX(DrugDimensionHistory.id).alias('id'))\
                                            .where(DrugDimensionHistory.drug_dimension_id==DrugDimension.id,DrugDimensionHistory.is_manual==0)
            auto_dimension_data_query = DrugDimension.select(DrugDimension.id.alias('drug_dimension_id'),
                                                             DrugDimensionHistory.width,
                                                             DrugDimensionHistory.length,
                                                             DrugDimensionHistory.depth,
                                                             DrugDimensionHistory.fillet,
                                                             DrugDimensionHistory.approx_volume,
                                                             DrugDimensionHistory.accurate_volume,
                                                             DrugDimensionHistory.shape.alias("shape_id"),
                                                             CustomDrugShape.name.alias("shape")
                                                             ).dicts() \
                .join(DrugDimensionHistory, on=DrugDimensionHistory.drug_dimension_id == DrugDimension.id)\
                .join(CustomDrugShape, on=DrugDimensionHistory.shape == CustomDrugShape.id)\
                .where(DrugDimension.id << drug_dimension_id_list, DrugDimensionHistory.id == sub_query)
        for record in auto_dimension_data_query:
            auto_dimension.append(record)
        if add_count:
            count += mfd_drugs
        if extend_list:
            result1.extend(results)
            for record in result1:
                record['auto_dimension_data'] = dict()
                if record['drug_dimension_id']:
                    for r in auto_dimension:
                        if r['drug_dimension_id'] == record['drug_dimension_id']:
                            record['auto_dimension_data'] = r
            return result1, count

        for record in results:
            if record['drug_dimension_id']:
                for r in auto_dimension:
                    if r['drug_dimension_id'] == record['drug_dimension_id']:
                        record['auto_dimension_data'] = r
                        break
            else:
                record['auto_dimension_data'] = {}
        return results, count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_drug_dimension_info {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args
def get_drug_dimension_details(company_id: int, filter_fields: [dict, None], sort_fields: [list, None],
                            paginate: [dict, None]) -> tuple:
    select_fields = list()
    clauses = list()
    exact_search_fields = list()
    like_search_fields = list()
    membership_search_fields = list()
    between_search_fields = list()
    order_list = list()
    unique_id_list = list()
    drug_dimension_id_list = list()
    status_list = list()
    subclauses = list()
    drug_without_dimension_list = list()
    drug_with_dimension_list = list()
    unique_drug_id_list = list()
    mfd_drugs_clauses = list()
    manual_drugs_clauses = list()
    rejected_drug_list = list()
    unique_drug_quantity_map = dict()
    high_priority_drug_list = list()
    extend_list = False
    add_count = False
    mfd_query_pending = False
    unique_id_top_mfd_drugs = list()

    try:
        # apply filter of verification_status in drug dimension screen
        if filter_fields and "verification_status" in filter_fields and filter_fields['verification_status'] is not None:

            for status in filter_fields['verification_status']:
                if status == "Rejected":
                    status_list.append(settings.VERIFICATION_REJECTED_FOR_DRUG)

                if status == "Verification Pending":
                    status_list.append(settings.VERIFICATION_PENDING_FOR_DRUG)

                if status == "Verified":
                    status_list.append(settings.VERIFICATION_DONE_FOR_DRUG)

                # in case of checkbox we have to pass verification_status_id is null in or clause
                if status == "Pending":
                    mfd_query_pending = True
                    subclauses.append(DrugDimension.verification_status_id.is_null(True))
            if status_list:
                subclauses.append(DrugDimension.verification_status_id.in_(status_list))

            filter_fields['verification_status'].clear()
        fields_dict = {
            'drug_name': DrugMaster.concated_drug_name_field(include_ndc=True),
            'txr': DrugMaster.txr,
            'ndc': DrugMaster.ndc,
            'shape': CustomDrugShape.name,
            'shape_id': DrugDimension.shape,
            'accurate_volume': DrugDimension.accurate_volume,
            'approx_volume': DrugDimension.approx_volume,
            'width': DrugDimension.width,
            'depth': DrugDimension.depth,
            'length': DrugDimension.length,
            'fillet': DrugDimension.fillet,
            'fndc_txr': fn.CONCAT(DrugMaster.formatted_ndc, '_', fn.IFNULL(DrugMaster.txr, '')),
            'verification_status': DrugDimension.verification_status_id,
            'verified_date': fn.IF((DrugDimension.verified_date.is_null(False) &
                                    DrugDimension.verification_status_id << (
                                        [settings.VERIFICATION_REJECTED_FOR_DRUG,
                                         settings.VERIFICATION_PENDING_FOR_DRUG]),
                                    None, DrugDimension.verified_date)),
            'id': UniqueDrug.id,
            "top_five_mfd_drug": fn.IF(FrequentMfdDrugs.id.is_null(True), 0, 1)
        }

        select_fields = [
            DrugMaster.id.alias('drug_id'),
            DrugMaster.ndc,
            DrugMaster.formatted_ndc,
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.txr,
            DrugMaster.imprint,
            DrugMaster.color,
            DrugMaster.image_name,
            DrugMaster.brand_flag,
            DrugMaster.brand_drug,
            DrugMaster.drug_form,
            fields_dict['id'].alias('unique_drug_id'),
            UniqueDrug.is_powder_pill,
            UniqueDrug.packaging_type,
            UniqueDrug.coating_type,
            UniqueDrug.is_zip_lock_drug,
            DrugDimension.width,
            DrugDimension.length,
            DrugDimension.depth,
            UniqueDrug.unit_weight,
            fields_dict['fillet'],
            DrugDimension.approx_volume,
            DrugDimension.accurate_volume,
            DrugDimension.verified_by,
            DrugDimension.rejection_note,
            DrugDimension.modified_by,
            DrugDimension.modified_date,
            DrugDimension.id.alias('drug_dimension_id'),
            DrugMaster.shape.alias('drug_shape'),
            fields_dict['shape'].alias('shape'),
            fields_dict['shape_id'].alias('shape_id'),
            fields_dict['drug_name'].alias('drug_name'),
            fields_dict['fndc_txr'].alias('fndc_txr'),
            fields_dict['verification_status'].alias('drug_dimension_status'),
            fn.IF(fields_dict['verification_status'].is_null(True), 'Pending',
                  fn.IF(fields_dict['verification_status'] == settings.VERIFICATION_PENDING_FOR_DRUG,
                        "Verification Pending", CodeMaster.value)).alias('verification_status'),
            fields_dict['verified_date'].alias('verified_date'),
            CodeMaster.id.alias("code_id"),
            DosageType.name.alias('dosage_type_name'),
            DosageType.code.alias('dosage_type_code'),
            DosageType.id.alias('dosage_type_id'),
            fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.id)).coerce(False).alias('canister_ids'),
            fn.GROUP_CONCAT(Clause(fn.DISTINCT(DrugDimensionHistory.image_name), SQL(" SEPARATOR ',' "))).alias(
                'drug_dimension_image'),
            fn.MAX(DrugDimensionHistory.id).alias("drug_dimension_history_id"),
            select_fields.append(FrequentMfdDrugs.id.alias("frequent_mfd_drug_id")),
            select_fields.append(fn.IF(FrequentMfdDrugs.id.is_null(True), 0, 1).alias("top_five_mfd_drug"))
        ]

        between_search_fields = ['width', 'length', 'depth', 'fillet', 'accurate_volume', 'approx_volume',
                                 'created_date']
        exact_search_fields = ['id']
        like_search_fields = ['drug_name', 'txr', 'shape']
        membership_search_fields = ['fndc_txr', 'verification_status']

        global_search = [DrugMaster.concated_drug_name_field(), DrugMaster.ndc]

        # add clause for global search(search by ndc and drug_name)
        if filter_fields and filter_fields.get('global_search', None) is not None:
            multi_search_string = filter_fields['global_search'].split(',')
            clauses = get_multi_search(clauses, multi_search_string, global_search)

        if 'id' not in filter_fields:
            drug_with_dimension_query = DrugDimension.db_get_drug_dimension_data()
            for Unique_drug_id in drug_with_dimension_query.dicts():
                drug_with_dimension_list.append(Unique_drug_id['unique_drug_id'])
                if Unique_drug_id['verification_status_id'] == settings.VERIFICATION_REJECTED_FOR_DRUG:
                    rejected_drug_list.append(Unique_drug_id['unique_drug_id'])
            logger.info("In get_drug_dimension_info: drug_with_dimension_list: {} ".format(drug_with_dimension_list))
            TOTAL_MONTHS = 1
            current_date = datetime.datetime.now().date()
            days_before = int(TOTAL_MONTHS) * settings.days_in_month
            month_back_date = current_date - timedelta(days=days_before)

            mfd_drugs_query, manual_drugs_query = get_manual_unique_drugs()

            if "custom_time_period" in filter_fields:
                manual_drugs_query = manual_drugs_query.where(PackDetails.created_date.between(filter_fields['custom_time_period']['from'],
                                                                               filter_fields['custom_time_period']['to']))
                mfd_drugs_query = mfd_drugs_query.where(MfdAnalysisDetails.created_date.between(filter_fields['custom_time_period']['from'],
                                                                               filter_fields['custom_time_period']['to']))
            else:
                manual_drugs_query = manual_drugs_query.where(PackDetails.created_date > month_back_date)
                mfd_drugs_query = mfd_drugs_query.where(MfdAnalysisDetails.created_date > month_back_date)

            for record in chain(mfd_drugs_query, manual_drugs_query):
                if record['id'] in unique_drug_quantity_map:
                    unique_drug_quantity_map[record['id']] += record['quantity']
                else:
                    unique_drug_quantity_map[record['id']] = record['quantity']

            sorted_drugs = sorted(unique_drug_quantity_map.items(), key=operator.itemgetter(1), reverse=True)
            drug_list = [drug[0] for drug in sorted_drugs]
            drug_with_dimension_excluding_rejected = list(set(drug_with_dimension_list) - set(rejected_drug_list))
            count = settings.HIGH_PRIORITY_PENDING_DRUG_COUNT
            for drug in drug_list:
                if drug not in drug_with_dimension_list:
                    drug_without_dimension_list.append(drug)
                if drug not in drug_with_dimension_excluding_rejected and count > 0:
                    high_priority_drug_list.append(drug)
                    count -= 1
            high_priority_drug_list.reverse()
            unique_drug_id_list = drug_with_dimension_list + drug_without_dimension_list
            clauses.append(UniqueDrug.id << unique_drug_id_list)
            # high priority drugs should be on top
            if high_priority_drug_list:
                order_list.append(SQL('FIELD(unique_drug_id,{})'.format(str(high_priority_drug_list)[1:-1])).desc())
            # orderby based drug in(Pending  -> Rejected -> Verification Pending -> Verified) sequence
            order_list.append(SQL('FIELD(drug_dimension_status,{},{})'.format(settings.VERIFICATION_PENDING_FOR_DRUG,
                                                                              settings.VERIFICATION_DONE_FOR_DRUG)))
            order_list.append(SQL('FIELD(code_id,{})'.format(settings.VERIFICATION_REJECTED_FOR_DRUG)))
            order_list.append(DrugDimension.id.is_null(True))
            if subclauses:
                clauses.append(functools.reduce(operator.or_, subclauses))
        else:
            # if only id is in filter_fields then no need to find high priority drugs and sorting is not done.
            clauses.append(UniqueDrug.id == filter_fields["id"])

        query = DrugMaster.select(*select_fields) \
                     .join(UniqueDrug, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                           & (DrugMaster.txr == UniqueDrug.txr))) \
                     .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                     .join(DrugDimensionHistory, JOIN_LEFT_OUTER,
                          on=DrugDimension.id == DrugDimensionHistory.drug_dimension_id) \
                     .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == UniqueDrug.dosage_type) \
                     .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
                     .join(CodeMaster, JOIN_LEFT_OUTER, on=DrugDimension.verification_status_id == CodeMaster.id)\
                     .join(CanisterMaster, JOIN_LEFT_OUTER, on=(
                        (CanisterMaster.drug_id == UniqueDrug.drug_id) & (CanisterMaster.rfid.is_null(False))))

        if filter_fields and 'current_batch_usage' in filter_fields:
            pack_ids = PackQueue.get_pack_ids_pack_queue()
            if not pack_ids:
                return [], 0
            query = query.join(SlotDetails, JOIN_LEFT_OUTER, on=SlotDetails.drug_id == DrugMaster.id) \
                         .join(PackRxLink, JOIN_LEFT_OUTER, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                         .join(PackDetails, JOIN_LEFT_OUTER, on=PackDetails.id == PackRxLink.pack_id)
            clauses.append(PackDetails.id << pack_ids)
            query = query.join(FrequentMfdDrugs, JOIN_LEFT_OUTER, on=((FrequentMfdDrugs.unique_drug_id == UniqueDrug.id)&(FrequentMfdDrugs.current_pack_queue == 1)))
            select_fields.append(FrequentMfdDrugs.id.alias("frequent_mfd_drug_id"))
            select_fields.append(fn.IF(FrequentMfdDrugs.id.is_null(True), 0, 1).alias("top_five_mfd_drug"))
            fields = select_fields.copy()
            clauses.append(FrequentMfdDrugs.id.is_null(True))

            # for top 5 mfd drugs
            query1 = UniqueDrug.select(*fields,
                                       FrequentMfdDrugs.quantity) \
                .join(DrugMaster, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                      fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                     (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .join(DrugDimensionHistory, JOIN_LEFT_OUTER,
                      on=DrugDimension.id == DrugDimensionHistory.drug_dimension_id) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == 1) &
                                                             (DrugStockHistory.company_id == company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                        (DrugDetails.company_id == company_id))) \
                .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == DrugDimension.verification_status_id) \
                .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
                .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == UniqueDrug.dosage_type) \
                .join(CanisterMaster, JOIN_LEFT_OUTER,
                      on=((CanisterMaster.drug_id == UniqueDrug.drug_id) & (CanisterMaster.rfid.is_null(False)))) \
                .join(GenerateCanister, JOIN_LEFT_OUTER, on=GenerateCanister.drug_id == DrugMaster.id) \
                .join(FrequentMfdDrugs,
                      on=((FrequentMfdDrugs.unique_drug_id == UniqueDrug.id) & (
                              FrequentMfdDrugs.current_pack_queue == 1)))
            if filter_fields and "verification_status" in filter_fields:
                if mfd_query_pending:
                    query1 = query1.where(FrequentMfdDrugs.id.is_null(False),
                                          FrequentMfdDrugs.current_pack_queue == 1,
                                          DrugDimension.verification_status_id.is_null(True))
                else:
                    query1 = query1.where(FrequentMfdDrugs.id.is_null(False),
                                          FrequentMfdDrugs.current_pack_queue == 1,
                                          DrugDimension.verification_status_id << status_list)
            else:
                query1 = query1.where(FrequentMfdDrugs.id.is_null(False),
                                      FrequentMfdDrugs.batch_id.is_null(True))
            query1 = query1.group_by(UniqueDrug.id)
            query1 = query1.order_by(FrequentMfdDrugs.quantity.desc())

            result1 = []
            for record in query1.dicts():
                unique_id_top_mfd_drugs.append(record['unique_drug_id'])
                result1.append(record)
            mfd_drugs = len(result1)

            add_count = True
            if paginate.get("page_number") == 1:
                extend_list = True
                paginate["number_of_rows"] = paginate["number_of_rows"] - mfd_drugs

        query = query.group_by(UniqueDrug.id)
        logger.debug(query)
        results, count = get_results(query.dicts(), fields_dict,
                                     filter_fields=filter_fields,
                                     sort_fields=sort_fields,
                                     paginate=paginate,
                                     clauses=clauses,
                                     exact_search_list=exact_search_fields,
                                     like_search_list=like_search_fields,
                                     membership_search_list=membership_search_fields,
                                     between_search_list=between_search_fields,
                                     identified_order=order_list)

        for record in results:
            unique_id_list.append(record['unique_drug_id'])
            if record['drug_dimension_id']:
                drug_dimension_id_list.append(record['drug_dimension_id'])
        if "current_batch_usage" in filter_fields:
            unique_id_list.extend(unique_id_top_mfd_drugs)

        if add_count:
            count += mfd_drugs
        if extend_list:
            result1.extend(results)
            results = list()
            results = result1

        drug_stock_history_dict = get_drug_stock_history(unique_id_list=unique_id_list, recent_history=True, company_id=company_id)
        drug_details_list = get_drug_details(unique_id_list, company_id)
        auto_dimension = get_auto_dimension(drug_dimension_id_list)

        for record in results:
            record['auto_dimension_data'] = dict()
            record['last_seen_on'] = None
            record['last_seen_with'] = None
            record['is_in_stock'] = None
            if record['unique_drug_id'] in drug_stock_history_dict:
                drug_stock_history_list = drug_stock_history_dict[record['unique_drug_id']]
                for drug_stock in drug_stock_history_list:
                    record['is_in_stock'] = drug_stock['is_in_stock']
            for unique_drug in drug_details_list:
                if unique_drug['unique_drug_id'] == record['unique_drug_id']:
                    record['last_seen_on'] = unique_drug['last_seen_on']
                    record['last_seen_with'] = unique_drug['last_seen_with']
            if record['canister_ids'] is not None:
                canister_list = list(map(int, record['canister_ids'].split(",")))
                canister_data_list = get_drug_dimension_canister_data(canister_ids_list=canister_list)
                record['canister_data_list'] = canister_data_list
            else:
                record['canister_data_list'] = []
            if record['drug_dimension_id'] and auto_dimension:
                for drug in auto_dimension:
                    if drug['drug_dimension_id'] == record['drug_dimension_id']:
                        record['auto_dimension_data'] = drug
                        break
            if record['drug_dimension_status'] is None or record['drug_dimension_status'] == \
                    settings.DRUG_VERIFICATION_STATUS['rejected']:
                record['priority'] = 'high' if record['unique_drug_id'] in high_priority_drug_list else 'low'
            else:
                record['priority'] = None
        return results, count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_drug_dimension_info {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args
def drug_master_data(company_id: int, filter_fields: [dict, None], sort_fields: [list, None],
                            paginate: [dict, None]):
    try:
        order_list = list()
        clauses = list()
        between_search_fields = ['created_date']
        exact_search_fields = ['id', 'brand_flag']
        like_search_fields = ['drug_name', 'txr', 'manufacturer', 'color_shape']
        membership_search_fields = ['fndc_txr', 'verification_status']
        global_search = [DrugMaster.concated_drug_name_field(), DrugMaster.ndc]
        mfd_query_clauses = list()
        status_list = list()
        subclauses = list()
        unique_id_list = list()
        drug_dimension_id_list = list()
        unique_drug_mfd_qty_map = dict()
        filter_fields_for_mfd = dict()
        unique_drug_ndc_map = dict()
        ndc_list = list()
        ndc_qty_map = dict()

        if sort_fields:
            order_list = sort_fields

        if filter_fields and "verification_status" in filter_fields and filter_fields['verification_status'] is not None:

            for status in filter_fields['verification_status']:
                if status == "Rejected":
                    status_list.append(settings.VERIFICATION_REJECTED_FOR_DRUG)

                if status == "Verification Pending":
                    status_list.append(settings.VERIFICATION_PENDING_FOR_DRUG)

                if status == "Verified":
                    status_list.append(settings.VERIFICATION_DONE_FOR_DRUG)

                # in case of checkbox we have to pass verification_status_id is null in or clause
                if status == "Registration Pending":
                    subclauses.append(DrugDimension.verification_status_id.is_null(True))

            if status_list:
                subclauses.append(DrugDimension.verification_status_id.in_(status_list))

            filter_fields['verification_status'].clear()

        # add clause for global search(search by ndc and drug_name)
        if filter_fields and filter_fields.get('global_search', None) is not None:
            multi_search_string = filter_fields['global_search'].split(',')
            clauses = get_multi_search(clauses, multi_search_string, global_search)

        if filter_fields and filter_fields.get("calibration_pending", None):
            clauses.append(UniqueDrug.unit_weight.is_null(True))

        if not filter_fields.get("id"):
            filter_fields_for_mfd['created_date'] = filter_fields.pop("created_date")
            # apply created_date filter on mfd_analysis_details data.
            mfd_query_clauses = get_filters(mfd_query_clauses,
                                            fields_dict={"created_date": MfdAnalysisDetails.created_date},
                                            filter_dict=filter_fields_for_mfd,
                                            between_search_fields=between_search_fields)

            min_mfd_analysis_query = MfdAnalysisDetails.select(fn.MIN(MfdAnalysisDetails.id).alias('min_mfd_analysis_details_id')).dicts() \
                                                       .where(reduce(operator.and_, mfd_query_clauses)).get()

            mfd_drugs_query = MfdAnalysisDetails.select(UniqueDrug.id, fn.SUM(MfdAnalysisDetails.quantity).alias('mfd_quantity')).dicts() \
                                                .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
                                                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                                                .join(UniqueDrug,
                                                      on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                          (UniqueDrug.txr == DrugMaster.txr))) \
                                                .where(MfdAnalysisDetails.status_id.not_in([constants.MFD_DRUG_PENDING_STATUS]),
                                                       MfdAnalysisDetails.id > min_mfd_analysis_query['min_mfd_analysis_details_id']) \
                                                .group_by(UniqueDrug.id)

            for unique_drug in mfd_drugs_query:
                unique_drug_mfd_qty_map[unique_drug['id']] = unique_drug['mfd_quantity']

        fields_dict = {
            'drug_name': DrugMaster.concated_drug_name_field(include_ndc=True),
            'ndc': DrugMaster.ndc,
            'fndc_txr': fn.CONCAT(DrugMaster.formatted_ndc, '_', fn.IFNULL(DrugMaster.txr, '')),
            'verification_status': DrugDimension.verification_status_id,
            'id': UniqueDrug.id,
            'brand_flag': DrugMaster.brand_flag,
            'color_shape': fn.CONCAT(fn.IFNULL(DrugMaster.color, 'N.A.'), ' & ', fn.IFNULL(CustomDrugShape.name, 'N.A.')),
            'manufacturer': DrugMaster.manufacturer
        }

        select_fields = [
            fn.GROUP_CONCAT(fn.DISTINCT(DrugMaster.ndc)).alias('ndc_list'),
            DrugMaster.id.alias('drug_id'),
            DrugMaster.ndc,
            DrugMaster.formatted_ndc,
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.txr,
            DrugMaster.imprint,
            DrugMaster.color,
            DrugMaster.image_name,
            DrugMaster.brand_flag,
            DrugMaster.brand_drug,
            DrugMaster.drug_form,
            fields_dict['id'].alias('unique_drug_id'),
            UniqueDrug.is_powder_pill,
            UniqueDrug.packaging_type,
            UniqueDrug.coating_type,
            UniqueDrug.is_zip_lock_drug,
            UniqueDrug.unit_weight,
            DrugDimension.width,
            DrugDimension.length,
            DrugDimension.depth,
            DrugDimension.fillet,
            DrugDimension.approx_volume,
            DrugDimension.accurate_volume,
            DrugDimension.verified_by,
            DrugDimension.rejection_note,
            DrugDimension.modified_by,
            DrugDimension.modified_date,
            DrugDimension.id.alias('drug_dimension_id'),
            DrugMaster.shape.alias('drug_shape'),
            CustomDrugShape.name.alias('shape'),
            DrugDimension.shape.alias('shape_id'),
            fields_dict['drug_name'].alias('drug_name'),
            fields_dict['fndc_txr'].alias('fndc_txr'),
            fields_dict['verification_status'].alias('drug_dimension_status'),
            fn.IF(fields_dict['verification_status'].is_null(True), 'Registration Pending',
                  fn.IF(fields_dict['verification_status'] == settings.VERIFICATION_PENDING_FOR_DRUG,
                        "Verification Pending", CodeMaster.value)).alias('verification_status'),
            CodeMaster.id.alias("code_id"),
            DosageType.name.alias('dosage_type_name'),
            DosageType.code.alias('dosage_type_code'),
            DosageType.id.alias('dosage_type_id'),
            fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.id)).coerce(False).alias('canister_ids'),
            fn.GROUP_CONCAT(Clause(fn.DISTINCT(DrugDimensionHistory.image_name), SQL(" SEPARATOR ',' "))).alias(
                'drug_dimension_image'),
            fn.MAX(DrugDimensionHistory.id).alias("drug_dimension_history_id"),
            fields_dict['color_shape'].alias('color_shape'),
            fields_dict['manufacturer'].alias('manufacturer')
        ]
        query = DrugMaster.select(*select_fields) \
                         .join(UniqueDrug, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                               & (DrugMaster.txr == UniqueDrug.txr))) \
                         .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                         .join(DrugDimensionHistory, JOIN_LEFT_OUTER,
                              on=DrugDimension.id == DrugDimensionHistory.drug_dimension_id) \
                        .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == UniqueDrug.dosage_type) \
                        .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
                        .join(CodeMaster, JOIN_LEFT_OUTER, on=DrugDimension.verification_status_id == CodeMaster.id) \
                        .join(CanisterMaster, JOIN_LEFT_OUTER, on=(
                            (CanisterMaster.drug_id == UniqueDrug.drug_id) & (CanisterMaster.rfid.is_null(False)))) \
                        .group_by(UniqueDrug.id)

        if subclauses:
            clauses.append(functools.reduce(operator.or_, subclauses))

        results, count = get_results(query.dicts(), fields_dict,
                                     filter_fields=filter_fields,
                                     clauses=clauses,
                                     exact_search_list=exact_search_fields,
                                     like_search_list=like_search_fields,
                                     membership_search_list=membership_search_fields,
                                     between_search_list=between_search_fields)

        for record in results:
            record['mfd_qty'] = 0
            if record['unique_drug_id'] in unique_drug_mfd_qty_map:
                record['mfd_qty'] = unique_drug_mfd_qty_map[record['unique_drug_id']]

        # change -1 to 1 and 1 to -1 in sort_fields
        for order in order_list:
            order[1] = -1 if order[1] == 1 else 1

        final_results = get_ordered_list(results, order_list)

        # if filter is for a unique_drug then paginate will not be in parameters
        paginated_results = dpws_paginate(final_results, paginate) if paginate else final_results

        for drug in paginated_results:
            unique_id_list.append(drug['unique_drug_id'])
            if drug['drug_dimension_id']:
                drug_dimension_id_list.append(drug['drug_dimension_id'])
            unique_drug_ndc_map[drug['unique_drug_id']] = list(map(int, drug['ndc_list'].split(',')))
            ndc_list.extend(unique_drug_ndc_map[drug['unique_drug_id']])
        drug_stock_history_dict = get_drug_stock_history(unique_id_list=unique_id_list, recent_history=True, company_id=company_id)
        auto_dimension = get_auto_dimension(drug_dimension_id_list)

        inventory_data = get_current_inventory_data(ndc_list=ndc_list, qty_greater_than_zero=False)
        for record in inventory_data:
            ndc_qty_map[record['ndc']] = record['quantity']

        for record in paginated_results:
            record['inventory_count'] = 0
            record['auto_dimension_data'] = dict()
            record['is_in_stock'] = None
            record['canister_data_list'] = list()
            if record['unique_drug_id'] in drug_stock_history_dict:
                drug_stock_history_list = drug_stock_history_dict[record['unique_drug_id']]
                for drug_stock in drug_stock_history_list:
                    record['is_in_stock'] = drug_stock['is_in_stock']
            if record['canister_ids'] is not None:
                canister_list = list(map(int, record['canister_ids'].split(",")))
                canister_data_list = get_drug_dimension_canister_data(canister_ids_list=canister_list)
                record['canister_data_list'] = canister_data_list
            if record['drug_dimension_id'] and auto_dimension:
                if auto_dimension.get(record['drug_dimension_id']):
                    record['auto_dimension_data'] = auto_dimension[record['drug_dimension_id']]
            for ndc in unique_drug_ndc_map[record['unique_drug_id']]:
                if ndc_qty_map.get(str(ndc)):
                    record['inventory_count'] += ndc_qty_map[str(ndc)]
        return paginated_results, count
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in drug_master_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in drug_master_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in drug_master_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args
def get_drug_dimension_canister_data(canister_ids_list: list) -> list:
    """
    function to get drug dimension canister data(all available canister for that drug)
    @param canister_ids_list:
    @return:
    """
    try:
        canister_data_list: list = list()
        select_fields = [CanisterMaster.id,
                         fn.IF(DeviceMaster.name.is_null(True), 'N.A.',
                               DeviceMaster.name).alias('device_name'),
                         fn.IF(ContainerMaster.drawer_name.is_null(True), 'null',
                               ContainerMaster.drawer_name).alias('drawer_id'),
                         LocationMaster.display_location,
                         CanisterMaster.available_quantity,
                         fn.IF(CanisterMaster.active.is_null(True), '0',
                               CanisterMaster.active).alias('active'),
                         ]
        # query to get available canister information of drug
        query = DrugMaster.select(*select_fields).dicts() \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=(DrugMaster.id == CanisterMaster.drug_id)) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=(CodeMaster.id == CanisterMaster.canister_type)) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(CanisterMaster.id.in_(canister_ids_list), CanisterMaster.rfid.is_null(False))\
            .order_by(CanisterMaster.id)

        for record in query:
            canister_data_list.append(record)

        return canister_data_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_drug_dimension_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_drug_master_count_data(company_id: int) -> tuple:
    """
    function to get stats count of drug master screen
    @param company_id:
    @return:
    """
    try:
        verified_drug_dimension: int = 0
        rejected_drug_dimension: int = 0
        verification_pending_drug_dimension: int = 0
        total_drugs: int = 0
        drugs_with_dimension_list: list = list()
        registration_pending_drug_dimension: int = 0

        # get drug with dimension from drug dimension table
        drug_with_dimension_query = DrugDimension.db_get_drug_dimension_data()

        # query to get all unique drugs which are used in pharmacy(present in slot details drug_id_id)
        # and does not have drug_dimension(not in dimension_master table)
        for record in drug_with_dimension_query:
            drugs_with_dimension_list.append(record['unique_drug_id'])
            if record['verification_status_id'] == settings.VERIFICATION_PENDING_FOR_DRUG:
                verification_pending_drug_dimension += 1
            if record['verification_status_id'] == settings.VERIFICATION_DONE_FOR_DRUG:
                verified_drug_dimension += 1
            if record['verification_status_id'] == settings.VERIFICATION_REJECTED_FOR_DRUG:
                rejected_drug_dimension += 1

        # get unique drugs which are used in pharmacy (present in rx) and does not have drug_dimension
        drug_without_dimension_query = UniqueDrug.select(UniqueDrug.id).dicts() \
            .join(DrugMaster, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                                              (DrugMaster.txr == UniqueDrug.txr))) \
            .where(UniqueDrug.id.not_in(drugs_with_dimension_list)) \
            .group_by(UniqueDrug.id)

        registration_pending_drug_dimension = drug_without_dimension_query.count()

        total_unique_drugs = UniqueDrug.select(UniqueDrug.id).dicts() \
                                        .join(DrugMaster, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                                              (DrugMaster.txr == UniqueDrug.txr))) \
                                        .group_by(UniqueDrug.id)
        total_drugs = total_unique_drugs.count()

        return registration_pending_drug_dimension, verification_pending_drug_dimension, verified_drug_dimension, \
            rejected_drug_dimension, total_drugs

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_master_count_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_drug_master_count_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_master_count_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def check_if_drug_dimension_measured_for_ndc(ndc_list: list, drug_scan_type=None) -> tuple:
    """
    function to check if drug dimension is measured for given ndc or not
    @param ndc_list:
    @return:
    """
    logger.debug("Inside check_if_drug_dimension_measure_for_ndc")
    try:
        clauses = [DrugMaster.ndc << ndc_list]
        if drug_scan_type == constants.UPC_SCAN:
            clauses = [DrugMaster.upc << ndc_list]
        # check if drug dimension is measured for given drug or not(if dimension is measured then Unique drug id present in drug dimension master table )
        dimension_query = DrugMaster.select(DrugMaster.ndc,
                                            DrugMaster.formatted_ndc,
                                            DrugMaster.txr,
                                            DrugDimension.id,
                                            DrugDimension.verification_status_id,
                                            UniqueDrug.id.alias('unique_drug_id')).dicts() \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .where(*clauses)\
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr)

        for record in dimension_query:
            if record['id'] is None:
                return False, record
            else:
                return True, record

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in check_if_drug_dimension_measure_for_ndc: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in check_if_drug_dimension_measure_for_ndc {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in check_if_drug_dimension_measure_for_ndc: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_drug_dimension_by_drug_name_ndc_dao(drugsearch, ndc) -> dict:
    """
    function to get drug dimension by drug name or ndc
    @param drugsearch:
    @return:
    """
    try:
        query = DrugDimension.select(DrugDimension,
                                     DrugDimension.shape.alias("shape_id"),
                                     CustomDrugShape.name.alias("shape_name"),
                                     DrugDimension.id.alias("drug_dimension_id"),
                                     DrugMaster,
                                     DrugMaster.concated_drug_name_field(include_ndc=True).alias(
                                         'concat_drug_name')).dicts() \
            .join(UniqueDrug, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(DrugMaster, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
            .where(((DrugMaster.drug_name ** drugsearch) | (DrugMaster.ndc ** drugsearch))) \
            .order_by(DrugMaster.drug_name, DrugMaster.strength_value)

        if len(ndc)>1:
            if len(ndc[0]) == 11:
                if ndc[0].isnumeric():
                    query = DrugDimension.select(DrugDimension,
                                                 DrugDimension.shape.alias("shape_id"),
                                                 CustomDrugShape.name.alias("shape_name"),
                                                 DrugDimension.id.alias("drug_dimension_id"),
                                                 DrugMaster,
                                                 DrugMaster.concated_drug_name_field(include_ndc=True).alias(
                                                     'concat_drug_name')).dicts() \
                        .join(UniqueDrug, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                        .join(DrugMaster, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                              fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                             (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                        .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
                        .where(((DrugMaster.drug_name ** drugsearch) | (DrugMaster.ndc << ndc))) \
                        .order_by(DrugMaster.drug_name, DrugMaster.strength_value)

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_dimension_by_drug_name_ndc_dao {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_drug_dimension_by_drug_name_ndc_dao {}".format(e))
        raise e


@log_args_and_response
def insert_drug_dimension_data_dao(dimension_data: dict, auto_dimension_data: dict = None,
                                   from_top_five_mfd_pop_up = None) -> int:
    """
    function to insert drug dimension data in Drug Dimension table
    @param dimension_data:
    @return:
    :param auto_dimension_data:
    """
    try:
        id = 0
        dimension_history_data = {}
        unique_drug_id  = dimension_data["unique_drug_id"]
        try:
            if dimension_data.get("image_url"):
                image_url = str(dimension_data.pop("image_url"))

            update_dimension = DrugDimension.db_get_drug_dimension_info(unique_drug_id)
            dimension_data["modified_date"] = get_current_date_time()
            if update_dimension:
                for record in update_dimension:
                    id = record['id']
                if id:
                    status = update_drug_dimension_by_dimension_id(drug_dimension_id=id, update_dict=dimension_data)

            else:
                logger.info(f"In db_insert_drug_dimension_data, unique_drug_id:{unique_drug_id}")
                id = DrugDimension.db_insert_drug_dimension_data(dimension_data=dimension_data)

        except (InternalError, IntegrityError, DataError) as e:
            logger.error("error in insert_drug_dimension_data_dao {}".format(e))
            raise e

        except Exception as e:
            logger.error("error in insert_drug_dimension_data_dao {}".format(e))
            raise e

        add_drug_dimension_history_data(dimension_data = dimension_data,dimension_id=id, auto_dimension_data=auto_dimension_data)

        logger.info(f"In insert_drug_dimension_data_dao, id :{id}")
        if from_top_five_mfd_pop_up:
            status = FrequentMfdDrugs.update(status = constants.DONE_MFD_DRUG_DIMENSION_FLOW,
                                             modified_date=get_current_date_time()) \
                            .where(FrequentMfdDrugs.unique_drug_id == unique_drug_id,
                                   FrequentMfdDrugs.status != constants.DONE_MFD_DRUG_DIMENSION_FLOW,
                                   FrequentMfdDrugs.current_pack_queue == 1,
                                   FrequentMfdDrugs.batch_id.is_null(True)) \
                            .execute()
            logger.info(f"In insert_drug_dimension_data_dao, status updated for FrequentMfdDrugs -- status:{status} for drug_id: {unique_drug_id}")

        return id

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in insert_drug_dimension_data_dao {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in insert_drug_dimension_data_dao {}".format(e))
        raise e


@log_args_and_response
def add_drug_dimension_history_data(dimension_data: dict,dimension_id: int, auto_dimension_data: dict = None) -> int:
    """
    adds mapping of canister parameters and drug
    :param mapping_data: dict
    :return:
    """
    parameter_list = ['width', 'length', 'depth', 'fillet', 'approx_volume', 'accurate_volume', 'shape', 'modified_by', 'unit_weight',
                      'image_name', 'verification_status_id']

    dimension_history_data = {}
    try:
        dimension_history_data['drug_dimension_id'] = dimension_id
        dimension_history_data['is_manual'] = 1
        for key in parameter_list:
            if key in dimension_data.keys():
                if key == 'modified_by':
                    dimension_history_data['created_by'] = dimension_data[key]
                else:
                    dimension_history_data[key] = dimension_data[key]

        history_id = DrugDimensionHistory.db_insert_drug_dimension_history_data(
            dimension_history_data=dimension_history_data)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in add_drug_dimension_history_data {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in add_drug_dimension_history_data {}".format(e))
        raise e
    if auto_dimension_data:
        try:
            dimension_history_data = {}
            auto_dimension_data['modified_date'] = dimension_data['modified_date']
            dimension_history_data['drug_dimension_id'] = dimension_id
            dimension_history_data['is_manual'] = 0
            for key in parameter_list:
                if key in auto_dimension_data.keys():
                    if key == 'modified_by':
                        dimension_history_data['created_by'] = auto_dimension_data[key]
                    else:
                        dimension_history_data[key] = auto_dimension_data[key]

            history_id = DrugDimensionHistory.db_insert_drug_dimension_history_data(
                dimension_history_data=dimension_history_data)

            if dimension_data['shape'] != auto_dimension_data['shape']:
                auto_dimension_dict = dict()
                manual_dimension_dict = dict()
                query = UniqueDrug.select(DrugMaster.concated_drug_name_field().alias('drug_name')).dicts() \
                                  .join(DrugMaster, on=DrugMaster.id == UniqueDrug.id) \
                                  .where(UniqueDrug.id == dimension_data['unique_drug_id'])

                for record in query:
                    drug_name = record['drug_name']

                parameters = ['width', 'length', 'depth', 'shape', 'fillet','created_by', 'modified_date', 'verification_status_id']

                for key in parameters:
                    if key == 'verification_status_id':
                        for status, id in settings.DRUG_VERIFICATION_STATUS.items():
                            if id == auto_dimension_data['verification_status_id']:
                                auto_dimension_dict['verification_status'] = status
                                manual_dimension_dict['verification_status'] = status
                                break
                    if key in auto_dimension_data.keys():
                        if key == 'shape':
                            auto_dimension_dict['shape'] = get_custome_drug_shape_by_id(id=auto_dimension_data['shape'])
                        else:
                            auto_dimension_dict[key] = auto_dimension_data[key]
                    if key in dimension_data.keys():
                        if key == 'shape':
                            manual_dimension_dict['shape'] = get_custome_drug_shape_by_id(id=dimension_data['shape'])
                        else:
                            manual_dimension_dict[key] = dimension_data[key]

                mismatched_shapes_drug_data = {
                    "drug_name": drug_name,
                    "auto_dimension_data": auto_dimension_dict,
                    "manual_dimension_data": manual_dimension_dict
                }
                logger.info("Inside add_drug_dimension_history_data, mismatched_shapes_drug_data".format(mismatched_shapes_drug_data))
                send_email_mismatched_auto_and_manual_drug_shapes(mismatched_shapes_drug_data)

        except (InternalError, IntegrityError, DataError) as e:
            logger.error("error in add_drug_dimension_history_data {}".format(e))
            raise e

        except Exception as e:
            logger.error("error in add_drug_dimension_history_data {}".format(e))
            raise e


@log_args_and_response
def add_drug_canister_parameter_mapping(mapping_data) -> int:
    """
    adds mapping of canister parameters and drug
    :param mapping_data: dict
    :return:
    """
    drug_canister_parameters_mapping_data = {
        "canister_parameter_id": mapping_data['canister_parameter_id'],
        "unique_drug_id": mapping_data["unique_drug_id"],
        "created_by": mapping_data["user_id"],
        "modified_by": mapping_data["user_id"]
    }
    try:
        record_id = DrugCanisterParameters.db_add_drug_canister_parameter_mapping(insert_dict=drug_canister_parameters_mapping_data)

        return record_id
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        logger.error("error in add_drug_canister_parameter_mapping {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in add_drug_canister_parameter_mapping {}".format(e))
        raise e


@log_args_and_response
def get_drug_dimension_data_by_dimension_id(dimension_id: int) -> dict:
    """
    function to get drug_dimension data by dimension id
    @param dimension_id:
    @return:
    """
    try:
        data = DrugDimension.db_get_drug_dimension_data_by_dimension_id(dimension_id=dimension_id)
        return data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_dimension_data_by_dimension_id {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_drug_dimension_data_by_dimension_id {}".format(e))
        raise e


@log_args_and_response
def delete_drug_canister_parameter_by_unique_drug(unique_drug_id: int) -> bool:
    """
    function to delete drug canister parameter by unique drug id
    @param unique_drug_id:
    @return:
    """
    try:
        status = DrugCanisterParameters.db_delete_by_unique_drug(unique_drug_id=unique_drug_id)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_drug_canister_parameter_by_unique_drug {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in delete_drug_canister_parameter_by_unique_drug {}".format(e))
        raise e


@log_args_and_response
def delete_drug_canister_stick_by_drug_dimension(drug_dimension_id: int) -> bool:
    """
    function to delete drug canister stick mapping data by drug dimension data
    @param drug_dimension_id:
    @return:
    """
    try:
        status = DrugCanisterStickMapping.db_delete_by_drug_dimension(drug_dimension_id=drug_dimension_id)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_drug_canister_stick_by_drug_dimension {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in delete_drug_canister_stick_by_drug_dimension {}".format(e))
        raise e


@log_args_and_response
def update_drug_dimension_by_dimension_id(drug_dimension_id: int, update_dict: dict) -> bool:
    """
    function to update drug dimension in drug_dimension table by dimension id
    @param update_dict:
    @param drug_dimension_id:
    @return:
    """
    try:
        status = DrugDimension.db_update_drug_dimension_by_dimension_id(dimension_id=drug_dimension_id, update_dict=update_dict)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_drug_dimension_by_dimension_id {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in update_drug_dimension_by_dimension_id {}".format(e))
        raise e


@log_args_and_response
def add_canister_parameters(canister_data) -> int:
    """
    adds canister parameters
    :param canister_data: dict
    :return: json
    """
    canister_parameters = dict()
    canister_parameters['speed'] = canister_data['speed']
    canister_parameters['wait_timeout'] = canister_data['wait_timeout']
    canister_parameters['cw_timeout'] = canister_data['cw_timeout']
    canister_parameters['ccw_timeout'] = canister_data['ccw_timeout']
    canister_parameters['drop_timeout'] = canister_data['drop_timeout']
    canister_parameters['pill_wait_time'] = canister_data['pill_wait_time']
    default_dict = {'created_by': canister_data['user_id'],
                    'modified_by': canister_data['user_id']}
    try:
        record, created = CanisterParameters.get_or_create(defaults=default_dict, **canister_parameters)
        return record.id
    except (InternalError, DataError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("error in add_canister_parameters {}".format(e))
        raise


@log_args_and_response
def get_small_canister_stick_data(from_length, to_length) -> list:
    """
    get small canister stick data
    @param from_length:
    @param to_length:
    """
    try:
        clauses = list()
        canister_stick_data = list()
        if from_length is not None and to_length is not None:
            clauses.append(between_expression(SmallCanisterStick.length, from_length, to_length))

        query = SmallCanisterStick.select(SmallCanisterStick.id,
                                          SmallCanisterStick.length,
                                          fn.COUNT(CanisterStick.id).alias("mapping_count")).dicts() \
            .join(CanisterStick, JOIN_LEFT_OUTER,
                  on=SmallCanisterStick.id == CanisterStick.small_canister_stick_id) \
            .group_by(SmallCanisterStick.id)
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        for record in query:
            canister_stick_data.append(record)
        return canister_stick_data
    except (InternalError, DataError, IntegrityError) as e:
        logger.error("Error in get_small_canister_stick_data {}".format(e))
        raise e

    except Exception as e:
        logger.error("Error in get_small_canister_stick_data {}".format(e))
        raise e


@log_args_and_response
def update_drug_canister_stick_mapping_by_dimension_id(drug_dimension_id: int, update_dict: dict) -> bool:
    """
    function to update canister stick mapping by canister id
    @param update_dict:
    @param drug_dimension_id:
    @return:
    """
    try:
        status = DrugCanisterStickMapping.db_update_drug_canister_stick_mapping_by_dimension_id(drug_dimension_id=drug_dimension_id, update_dict=update_dict)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_drug_canister_stick_mapping_by_dimension_id {}".format(e))
        raise e


@log_args_and_response
def delete_drug_canister_stick_by_id(drug_canister_stick_mapping_id: int) -> bool:
    """
    function to delete drug canister stick mapping data by DrugCanisterStickMapping id
    @param drug_canister_stick_mapping_id:
    @return:
    """
    try:
        status = DrugCanisterStickMapping.db_delete_drug_canister_stick_by_id(id=drug_canister_stick_mapping_id)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_drug_canister_stick_by_id {}".format(e))
        raise e


@log_args_and_response
def update_drug_canister_parameter_mapping(mapping_data) -> bool:
    """
    updates canister parameters and drug mapping
    :param mapping_data:
    :return:
    """
    canister_parameter_data = {
        'user_id': mapping_data['user_id'],
        'speed': mapping_data.get('speed', None),
        'wait_timeout': mapping_data.get('wait_timeout', None),
        'cw_timeout': mapping_data.get('cw_timeout', None),
        'ccw_timeout': mapping_data.get('ccw_timeout', None),
        'drop_timeout': mapping_data.get('drop_timeout', None),
        'pill_wait_time': mapping_data.get('pill_wait_time', None)
    }
    # unique_drug_id = mapping_data['unique_drug_id']
    try:
        canister_parameter_id = add_canister_parameters(canister_parameter_data)
        drug_canister_parameter_mapping_data = dict()
        drug_canister_parameter_mapping_data['created_by'] = \
            drug_canister_parameter_mapping_data['modified_by'] = \
            mapping_data['user_id']
        drug_canister_parameter_mapping_data['canister_parameter_id'] = canister_parameter_id
        create_dict = {"unique_drug_id": mapping_data['unique_drug_id']}
        # update_dict = {}
        status = DrugCanisterParameters.db_update_or_create(create_dict=create_dict,
                                                            update_dict=drug_canister_parameter_mapping_data)
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_drug_canister_parameter_mapping {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in update_drug_canister_parameter_mapping {}".format(e))
        raise e


@log_args_and_response
def get_drugs_for_required_configuration(unique_drug_id, length=0, width=0, depth=0, fillet=0, shape_id=None,
                                         use_database=False) -> list:
    """
    :param unique_drug_id:
    :param length:
    :param width:
    :param depth:
    :param fillet:
    :param shape_id:
    :param use_database:

    :return:
    """
    current_drug_data = dict()
    db_result = list()
    clauses = list()
    try:
        if use_database:
            query = DrugDimension.db_get_drug_dimension_info(unique_drug_id=unique_drug_id)

            for record in query:
                current_drug_data = record
        else:
            current_drug_data = {"length": decimal.Decimal(length), "width": decimal.Decimal(width),
                                 "depth": decimal.Decimal(depth), "fillet": decimal.Decimal(fillet),
                                 "shape": shape_id}

        if (not current_drug_data) and (current_drug_data["shape"] is not None):
            return db_result


        clauses.append(DrugDimension.shape == current_drug_data["shape"])
        if int(current_drug_data["shape"]) == settings.DRUG_SHAPE_ID_CONSTANTS["Capsule"]["shape_id"]:
            depth_minimum = current_drug_data["depth"] - decimal.Decimal(1.5)
            depth_maximum = current_drug_data["depth"] + decimal.Decimal(0.8)

            width_minimum = current_drug_data["width"] - decimal.Decimal(1.5)
            width_maximum = current_drug_data["width"] + decimal.Decimal(0.8)

            clauses.append(DrugDimension.depth.between(depth_minimum, depth_maximum))
            clauses.append(DrugDimension.width.between(width_minimum, width_maximum))

        elif int(current_drug_data["shape"]) == settings.DRUG_SHAPE_ID_CONSTANTS["Round Flat"]["shape_id"]:
            depth_minimum = current_drug_data["depth"] - decimal.Decimal(0.5)
            depth_maximum = current_drug_data["depth"] + decimal.Decimal(0.2)

            width_minimum = current_drug_data["width"] - decimal.Decimal(0.3)
            width_maximum = current_drug_data["width"] + decimal.Decimal(0.1)

            clauses.append(DrugDimension.depth.between(depth_minimum, depth_maximum))
            clauses.append(DrugDimension.width.between(width_minimum, width_maximum))

        elif int(current_drug_data["shape"]) == settings.DRUG_SHAPE_ID_CONSTANTS["Oval"]["shape_id"]:
            depth_minimum = current_drug_data["depth"] - decimal.Decimal(0.5)
            depth_maximum = current_drug_data["depth"] + decimal.Decimal(0.2)

            width_minimum = current_drug_data["width"] - decimal.Decimal(0.3)
            width_maximum = current_drug_data["width"] + decimal.Decimal(0.2)

            clauses.append(DrugDimension.depth.between(depth_minimum, depth_maximum))
            clauses.append(DrugDimension.width.between(width_minimum, width_maximum))

        elif int(current_drug_data["shape"]) == settings.DRUG_SHAPE_ID_CONSTANTS["Round Curved"]["shape_id"]:
            depth_minimum = current_drug_data["depth"] - decimal.Decimal(0.3)
            depth_maximum = current_drug_data["depth"] + decimal.Decimal(0.1)

            width_minimum = current_drug_data["width"] - decimal.Decimal(0.3)
            width_maximum = current_drug_data["width"] + decimal.Decimal(0.15)

            fillet_minimum = current_drug_data["fillet"] - decimal.Decimal(0.3)
            fillet_maximum = current_drug_data["fillet"] + decimal.Decimal(0.15)

            clauses.append(DrugDimension.depth.between(depth_minimum, depth_maximum))
            clauses.append(DrugDimension.width.between(width_minimum, width_maximum))
            clauses.append(DrugDimension.fillet.between(fillet_minimum, fillet_maximum))

        elif int(current_drug_data["shape"]) == settings.DRUG_SHAPE_ID_CONSTANTS["Elliptical"]["shape_id"]:
            depth_minimum = current_drug_data["depth"] - decimal.Decimal(0.5)
            depth_maximum = current_drug_data["depth"] + decimal.Decimal(0.2)

            width_minimum = current_drug_data["width"] - decimal.Decimal(0.3)
            width_maximum = current_drug_data["width"] + decimal.Decimal(0.2)

            clauses.append(DrugDimension.depth.between(depth_minimum, depth_maximum))
            clauses.append(DrugDimension.width.between(width_minimum, width_maximum))
        else:
            return []
        query = DrugDimension.select(DrugDimension.unique_drug_id).dicts().where(functools.reduce(operator.and_, clauses))

        for record in query:
            db_result.append(record["unique_drug_id"])

        return db_result
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drugs_for_required_configuration {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_drugs_for_required_configuration {}".format(e))
        raise e


@log_args_and_response
def get_small_canister_stick_data_by_length(req_length) -> dict or None:
    """
    function to get small canister stick data by length
    @param req_length:
    @return:
    """
    try:
        status = SmallCanisterStick.db_get_data_by_length(req_length=req_length)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_small_canister_stick_data_by_length {}".format(e))
        raise e


@log_args_and_response
def get_drug_shape_fields_by_shape_id(shape_id: int):
    """
    function to get drug shape fields  by shape id
    @param shape_id:
    @return:
    """
    try:
        shape_field = DrugShapeFields.db_get_drug_shape_fields_by_shape_id(shape_id=shape_id)
        return shape_field

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_shape_fields_by_shape_id {}".format(e))
        raise e



@log_args_and_response
def get_drug_canister_stick_mapping_data(filter_fields: [dict, None], sort_fields: [list, None], paginate: [dict, None]) -> tuple:
    """
    function to get drug  canister stick mapping data
    @param paginate:
    @param sort_fields:
    @param filter_fields:
    @return:
    """
    drug_canister_stick_mapping_list: list = list()
    fields_dict = {
        'drug_name': DrugMaster.concated_drug_name_field(),
        'ndc': DrugMaster.ndc,
        'big_canister_stick_width': BigCanisterStick.width,
        'big_canister_stick_depth': BigCanisterStick.depth,
        'small_canister_stick_length': SmallCanisterStick.length,
        'id': DrugCanisterStickMapping.id,
        'big_canister_stick_serial_number': BigCanisterStick.serial_number
    }
    between_search_fields = ['big_canister_stick_width', 'small_canister_stick_length', 'big_canister_stick_depth']
    exact_search_fields = ['big_canister_stick_serial_number', 'id']
    like_search_fields = ['drug_name', 'ndc']

    clauses: list = list()
    clauses = get_filters(clauses, fields_dict, filter_fields, exact_search_fields=exact_search_fields,
                          like_search_fields=like_search_fields,
                          between_search_fields=between_search_fields)
    order_list: list = list()
    order_list = get_orders(order_list, fields_dict, sort_fields)
    order_list.append(DrugCanisterStickMapping.id)
    try:
        query = DrugCanisterStickMapping.select(DrugDimension,
                                                CanisterStick,
                                                DrugMaster,
                                                DrugMaster.shape.alias('drug_shape'),
                                                CustomDrugShape.name.alias('shape'),
                                                DrugDimension.shape.alias('shape_id'),
                                                BigCanisterStick.width.alias("big_canister_stick_width"),
                                                BigCanisterStick.depth.alias("big_canister_stick_depth"),
                                                BigCanisterStick.serial_number.alias(
                                                    "big_canister_stick_serial_number"),
                                                SmallCanisterStick.length.alias("small_canister_stick_length"),
                                                DrugCanisterStickMapping,
                                                fields_dict['drug_name'].alias('drug_name')).dicts() \
            .join(CanisterStick,
                  on=CanisterStick.id == DrugCanisterStickMapping.canister_stick_id) \
            .join(DrugDimension,
                  on=DrugCanisterStickMapping.drug_dimension_id == DrugDimension.id) \
            .join(UniqueDrug,
                  on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(DrugMaster,
                  on=UniqueDrug.drug_id == DrugMaster.id) \
            .join(BigCanisterStick,
                  on=CanisterStick.big_canister_stick_id == BigCanisterStick.id) \
            .join(SmallCanisterStick,
                  on=CanisterStick.small_canister_stick_id == SmallCanisterStick.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER,
                  on=CustomDrugShape.id == DrugDimension.shape)
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        if order_list:
            query = query.order_by(*order_list)
        count = query.count()
        if paginate:
            query = apply_paginate(query, paginate)
        for record in query:
            drug_canister_stick_mapping_list.append(record)

        return drug_canister_stick_mapping_list, count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_canister_stick_mapping_data {}".format(e))
        raise e


    except Exception as e:
        logger.error("error in get_drug_canister_stick_mapping_data {}".format(e))
        raise e


def get_canister_parameter_rule_dao(filter_fields, paginate, sort_fields):
    """

    @param filter_fields:
    @param paginate:
    @param sort_fields:
    @return:
    """
    try:
        query1 = CustomShapeCanisterParameters.select(SQL("'Shape' as rule_name"),
                                                      SQL("'shape' as rule_key"),
                                                      CustomDrugShape.name.alias('rule_value'),
                                                      CustomShapeCanisterParameters.canister_parameter_id.alias(
                                                          'cp_id'),
                                                      CustomShapeCanisterParameters.id.alias('rule_id')
                                                      ) \
            .join(CustomDrugShape, on=CustomDrugShape.id == CustomShapeCanisterParameters.custom_shape_id)
        query2 = SmallStickCanisterParameters.select(SQL("'Small Stick Number' as rule_name"),
                                                     SQL("'small_stick' as rule_key"),
                                                     SmallCanisterStick.length.alias('rule_value'),
                                                     SmallStickCanisterParameters.canister_parameter_id.alias('cp_id'),
                                                     SmallStickCanisterParameters.id.alias('rule_id')
                                                     ) \
            .join(SmallCanisterStick, on=SmallCanisterStick.id == SmallStickCanisterParameters.small_stick_id)
        query3 = DrugCanisterParameters.select(SQL("'Drug' as rule_name"),
                                               SQL("'drug' as rule_key"),
                                               fn.CONCAT(
                                                   DrugMaster.drug_name, ' ', DrugMaster.strength_value, ' ',
                                                   DrugMaster.strength, ' (', DrugMaster.ndc, ')'
                                               ).alias('rule_value'),
                                               DrugCanisterParameters.canister_parameter_id.alias('cp_id'),
                                               DrugCanisterParameters.id.alias('rule_id')
                                               ) \
            .join(UniqueDrug, on=UniqueDrug.id == DrugCanisterParameters.unique_drug_id) \
            .join(DrugMaster, on=DrugMaster.id == UniqueDrug.drug_id)
        rules_q = (query1 | query2 | query3).alias('rules')  # UNION of 3 layers of parameters
        query = CanisterParameters.select(rules_q.c.rule_name,
                                          rules_q.c.rule_value,
                                          rules_q.c.rule_key,
                                          rules_q.c.rule_id,
                                          CanisterParameters
                                          ).dicts() \
            .join(rules_q, on=rules_q.c.cp_id == CanisterParameters.id)
        fields_dict = {'rule_name': query.c.rule_name,
                       'rule_value': query.c.rule_value,
                       'rule_id': query.c.rule_id,
                       'rule_key': query.c.rule_key,
                       'speed': query.c.speed,
                       'wait_timeout': query.c.wait_timeout,
                       'cw_timeout': query.c.cw_timeout,
                       'ccw_timeout': query.c.ccw_timeout,
                       'drop_timeout': query.c.drop_timeout,
                       'pill_wait_time': query.c.pill_wait_time}
        exact_search_list = ['rule_id', 'rule_key']
        like_search_list = ['speed', 'wait_timeout', 'cw_timeout',
                            'ccw_timeout', 'drop_timeout', 'rule_value', 'pill_wait_time']
        membership_search_list = ['rule_name']
        results, count = get_results(query, fields_dict, filter_fields, sort_fields, paginate,
                                     exact_search_list=exact_search_list,
                                     like_search_list=like_search_list,
                                     membership_search_list=membership_search_list)
        return count, results

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_parameter_rule_dao {}".format(e))
        raise e


    except Exception as e:
        logger.error("error in get_canister_parameter_rule_dao {}".format(e))
        raise e


def get_canister_parameter_rule_drugs_dao(filter_fields, paginate, rule_id, rule_key, sort_fields):
    """

    @param filter_fields:
    @param paginate:
    @param rule_id:
    @param rule_key:
    @param sort_fields:
    @return:
    """
    try:
        drug_name_field = DrugMaster.concated_drug_name_field()
        select_fields = [DrugDimension,
                         DrugMaster,
                         drug_name_field.alias('drug_name'),
                         CustomDrugShape.name.alias('custom_shape')
                         ]
        if rule_key == 'small_stick':
            query = db_get_drugs_for_rule_query_sscp(select_fields)
            rule_id_field = SmallStickCanisterParameters.id
        if rule_key == 'shape':
            query = db_get_drugs_for_rule_query_cscp(select_fields)
            rule_id_field = CustomShapeCanisterParameters.id
        if rule_key == 'drug':
            query = db_get_drugs_for_rule_query_dcp(select_fields)
            rule_id_field = DrugCanisterParameters.id
        fields_dict = {'drug_name': drug_name_field,
                       'ndc': DrugMaster.ndc,
                       'txr': DrugMaster.txr,
                       'color': DrugMaster.color,
                       'shape': DrugMaster.shape,
                       'custom_shape': CustomDrugShape.name,
                       'imprint': DrugMaster.imprint,
                       'length': DrugDimension.length,
                       'depth': DrugDimension.depth,
                       'width': DrugDimension.width,
                       'fillet': DrugDimension.fillet,
                       'approx_volume': DrugDimension.approx_volume,
                       'accurate_volume': DrugDimension.accurate_volume,
                       'rule_id': rule_id_field
                       }
        exact_search_list = ['txr']
        like_search_list = ['drug_name', 'ndc', 'color', 'imprint', 'shape']
        membership_search_list = ['length', 'width', 'fillet', 'approx_volume', 'accurate_volume']
        query = query.dicts()
        clauses = [(fields_dict['rule_id'] == rule_id)]
        results, count = get_results(
            query, fields_dict, filter_fields, sort_fields, paginate,
            clauses=clauses,
            exact_search_list=exact_search_list,
            like_search_list=like_search_list,
            membership_search_list=membership_search_list
        )
        return count, results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_parameter_rule_drugs_dao {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_canister_parameter_rule_drugs_dao {}".format(e))
        raise e


def get_drugs_wo_dimension_dao(company_id, filter_fields, only_pending_facility, paginate, sort_fields):
    """
    function get drugs without dimension
    @param company_id:
    @param filter_fields:
    @param only_pending_facility:
    @param paginate:
    @param sort_fields:
    @return:

    """
    try:
        fields_dict = {'drug_name': DrugMaster.concated_drug_name_field(),
                       # 'strength': DrugMaster.concated_drug_name_field(),
                       'ndc': DrugMaster.ndc,
                       'imprint': fn.replace(DrugMaster.imprint, '  ', ' '),
                       'color': DrugMaster.color,
                       'shape': DrugMaster.shape,
                       'drug_id': DrugMaster.id,
                       'unique_drug_id': UniqueDrug.id,
                       'dosage_type_name': DosageType.name,
                       'dosage_type_code': DosageType.code,
                       'dosage_type_id': DosageType.id,
                       'store_separate_drug_id': StoreSeparateDrug.id,
                       'drug': fn.CONCAT(DrugMaster.drug_name, ' ', DrugMaster.strength_value, ' ',
                                         DrugMaster.strength, ' (', DrugMaster.ndc, ')')
                       }
        select_fields = [DrugMaster,
                         fields_dict['drug_id'].alias('drug_id'),
                         fields_dict['unique_drug_id'].alias('unique_drug_id'),
                         fields_dict['drug'].alias('drug'),
                         fields_dict['dosage_type_name'].alias('dosage_type_name'),
                         fields_dict['dosage_type_code'].alias('dosage_type_code'),
                         fields_dict['dosage_type_id'].alias('dosage_type_id'),
                         fields_dict['store_separate_drug_id'].alias('store_separate_drug_id'),
                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True, DrugStockHistory.is_in_stock).alias(
                             "is_in_stock"),
                         fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                               DrugDetails.last_seen_by).alias('last_seen_with'),
                         fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                               DrugDetails.last_seen_date).alias('last_seen_on')
                         ]
        like_search_list = ['drug_name', 'imprint', 'color', 'txr', 'shape', 'drug']
        between_search_list = []
        exact_search_list = ['unique_drug_id']
        membership_search_list = []
        sub_q = DrugDimension.select(DrugDimension.unique_drug_id)
        clauses = [UniqueDrug.id.not_in(sub_q),
                   PatientMaster.company_id == company_id
                   ]
        if "ndc" in filter_fields and filter_fields["ndc"]:
            ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty = DrugMaster.get_ndc_list_for_barcode(
                {"scanned_ndc": filter_fields['ndc'], "required_entity": "ndc"})
            if ndc_list:
                filter_fields["ndc"] = ndc_list
                membership_search_list.append('ndc')
            else:
                like_search_list.append('ndc')

        # get unique drugs which are used in pharmacy (present in rx) and does not have drug_dimension
        query = DrugMaster.select(*select_fields) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER,
                  on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) & (DrugStockHistory.is_active == 1) &
                      (DrugStockHistory.company_id == company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == company_id))) \
            .join(StoreSeparateDrug, JOIN_LEFT_OUTER, on=StoreSeparateDrug.unique_drug_id == UniqueDrug.id) \
            .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == StoreSeparateDrug.dosage_type_id) \
            .join(SlotDetails, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id) \
            .where(UniqueDrug.id.not_in(sub_q),
                   PatientMaster.company_id == company_id)

        if "drug" in filter_fields and filter_fields["drug"]:
            drug = filter_fields["drug"]
            candidate_ndcs, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
                {"scanned_ndc": drug, "required_entity": "ndc"})
            drug = "%" + drug + "%"
            if candidate_ndcs:
                query = query.where((fields_dict['drug'] ** drug)
                                    | (DrugMaster.ndc ** drug)
                                    | (DrugMaster.ndc << candidate_ndcs))
            else:
                query = query.where((fields_dict['drug'] ** drug) | (DrugMaster.ndc ** drug))
            filter_fields.pop('drug', None)

        if only_pending_facility:
            # consider drugs for only pending packs
            query = query.join(PackHeader, on=PackHeader.patient_id == PatientMaster.id) \
                .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id)
            clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]))
            clauses.append((PackDetails.system_id.is_null(True)))

        query = query.group_by(UniqueDrug.id)

        results, count = get_results(query.dicts(), fields_dict, clauses=clauses,
                                     filter_fields=filter_fields,
                                     sort_fields=sort_fields,
                                     paginate=paginate,
                                     exact_search_list=exact_search_list,
                                     like_search_list=like_search_list,
                                     between_search_list=between_search_list,
                                     membership_search_list=membership_search_list,
                                     last_order_field=[fields_dict['unique_drug_id']])
        return count, results

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drugs_wo_dimension_dao {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_drugs_wo_dimension_dao {}".format(e))
        raise e


@log_args_and_response
def update_data_in_unique_drug(unique_drug_id, dosage_type, packaging_type, is_powder_pill, coating_type, is_zip_lock_drug, unit_weight):
    try:
        logger.info("In update_data_in_unique_drug")
        is_delicate = UniqueDrug.select(UniqueDrug.is_delicate).where(UniqueDrug.id == unique_drug_id).scalar()
        if not is_delicate:
            if dosage_type in constants.DELICATE_DOSAGE_TYPES or is_powder_pill == constants.POWDER_PILL or coating_type in constants.DELICATE_COATING_TYPES:
                is_delicate = 1

        status = UniqueDrug.update(dosage_type=dosage_type, packaging_type=packaging_type, is_powder_pill=is_powder_pill,
                                   coating_type=coating_type, is_zip_lock_drug=is_zip_lock_drug, is_delicate=is_delicate,
                                   unit_weight=unit_weight) \
            .where(UniqueDrug.id == unique_drug_id) \
            .execute()
        logger.info(f"In update_data_in_unique_drug, status: {status}")

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_data_in_unique_drug {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in update_data_in_unique_drug {}".format(e))
        raise e


@log_args_and_response
def get_drug_dimension_history_dao(drug_id=None, records_from_date=None):
    try:
        drug_dimension_history_data = dict()
        status_set = set()
        logger.info("Inside get_drug_dimension_history_dao")
        query = DrugMaster.select(fn.CONCAT(DrugMaster.drug_name, ', ', DrugMaster.ndc).alias('drug_name_ndc'),
                                  DrugDimensionHistory.created_by, DrugDimensionHistory.created_date,
                                  DrugDimensionHistory.verification_status_id).dicts() \
                          .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
                          .join(DrugDimension, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                          .join(DrugDimensionHistory, on=DrugDimension.id == DrugDimensionHistory.drug_dimension_id) \
                          .where(DrugDimensionHistory.is_manual == 1)\
                          .order_by(DrugDimensionHistory.created_date.desc())

        if drug_id:
            query = query.where(DrugMaster.id == drug_id)

        if records_from_date:
            query = query.where(fn.DATE(DrugDimensionHistory.created_date) > records_from_date)

        for drug in query:
            verification_status = None

            for status, id in settings.DRUG_VERIFICATION_STATUS.items():
                if drug['verification_status_id'] == id:
                    verification_status = status
                    if drug['verification_status_id'] == settings.VERIFICATION_PENDING_FOR_DRUG:
                        verification_status = 'verification pending'

            if drug['drug_name_ndc'] not in drug_dimension_history_data:
                drug_dimension_history_data[drug['drug_name_ndc']] = list()

            if not len(status_set) or drug['verification_status_id'] != settings.VERIFICATION_PENDING_FOR_DRUG:
                drug_dimension_history_data[drug['drug_name_ndc']].append({
                        'action_taken_by': drug['created_by'],
                        'verification_status': verification_status,
                        'date_time': drug['created_date']
                })
            else:
                if (drug['verification_status_id'] == settings.VERIFICATION_PENDING_FOR_DRUG) and (drug['verification_status_id'] in status_set):
                    drug_dimension_history_data[drug['drug_name_ndc']].append({
                        'action_taken_by': drug['created_by'],
                        'verification_status': 'retaken',
                        'date_time': drug['created_date']
                    })
            status_set.add(drug['verification_status_id'])

        return drug_dimension_history_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_dimension_history_dao {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_drug_dimension_history_dao {}".format(e))
        raise e


@log_args_and_response
def get_drug_stock_history(unique_id_list, company_id, recent_history=None, records_from_date=None):
    try:
        drug_stock_history_dict = dict()
        if unique_id_list:
            sub_query = DrugStockHistory.select(fn.MAX(DrugStockHistory.id).alias('drug_stock_history_id'),
                                                DrugStockHistory.unique_drug_id.alias('unique_drug_id'))\
                                        .group_by(DrugStockHistory.unique_drug_id) \
                                        .alias('sub_query')

            query = UniqueDrug.select(DrugStockHistory.unique_drug_id,
                                      DrugStockHistory.is_in_stock,
                                      DrugStockHistory.created_by,
                                      DrugStockHistory.created_date).dicts() \
                                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                             (DrugStockHistory.company_id == company_id))) \
                                .where(UniqueDrug.id << unique_id_list)

            if recent_history:
                query = query.join(sub_query, on=DrugStockHistory.unique_drug_id == sub_query.c.drug_stock_history_id)

            if records_from_date:
                query = query.where(fn.DATE(DrugStockHistory.created_date) > records_from_date)

            for record in query:
                if not record['unique_drug_id'] in drug_stock_history_dict:
                    drug_stock_history_dict[record['unique_drug_id']] = list()
                drug_stock_history_dict[record['unique_drug_id']].append(record)
        return drug_stock_history_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_stock_history {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_drug_stock_history {}".format(e))
        raise e


@log_args_and_response
def get_drug_details(unique_id_list, company_id=None):
    try:
        drug_details_list = list()
        if unique_id_list:
            query = DrugDetails.select(DrugDetails.last_seen_by.alias('last_seen_with'),
                                       DrugDetails.last_seen_date.alias('last_seen_on'), DrugDetails.unique_drug_id).dicts() \
                                .where(DrugDetails.unique_drug_id << unique_id_list)

            if company_id:
                query = query.where(DrugDetails.company_id == company_id)
            for record in query:
                drug_details_list.append(record)
        return drug_details_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_details {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_drug_details {}".format(e))
        raise e


@log_args_and_response
def get_auto_dimension(drug_dimension_id_list):
    try:
        auto_dimension_data = dict()
        if drug_dimension_id_list:
            sub_query = DrugDimensionHistory.select(fn.MAX(DrugDimensionHistory.id).alias('id'))\
                                            .where(DrugDimensionHistory.drug_dimension_id==DrugDimension.id,
                                                   DrugDimensionHistory.is_manual==0)
            query = DrugDimension.select(DrugDimension.id.alias('drug_dimension_id'),
                                         DrugDimensionHistory.width,
                                         DrugDimensionHistory.length,
                                         DrugDimensionHistory.depth,
                                         DrugDimensionHistory.fillet,
                                         DrugDimensionHistory.approx_volume,
                                         DrugDimensionHistory.accurate_volume,
                                         DrugDimensionHistory.shape.alias("shape_id"),
                                         CustomDrugShape.name.alias("shape")).dicts() \
                .join(DrugDimensionHistory, on=DrugDimensionHistory.drug_dimension_id == DrugDimension.id)\
                .join(CustomDrugShape, on=DrugDimensionHistory.shape == CustomDrugShape.id)\
                .where(DrugDimension.id << drug_dimension_id_list, DrugDimensionHistory.id == sub_query)

            for record in query:
                auto_dimension_data[record['drug_dimension_id']] = record

        return auto_dimension_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_auto_dimension {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_auto_dimension {}".format(e))
        raise e


@log_args_and_response
def get_manual_unique_drugs():
    try:
        logger.info("Inside get_manual_unique_drugs")
        mfd_drugs_query = MfdAnalysisDetails.select(UniqueDrug.id,
                                                    fn.SUM(MfdAnalysisDetails.quantity).alias('quantity')).dicts() \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug,
                  on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
            .where(MfdAnalysisDetails.status_id.not_in([constants.MFD_DRUG_PENDING_STATUS])) \
            .group_by(UniqueDrug.id)

        manual_drugs_query = PackUserMap.select(UniqueDrug.id, fn.SUM(SlotDetails.quantity).alias('quantity')).dicts() \
            .join(PackDetails, on=PackUserMap.pack_id == PackDetails.id) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug,
                  on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
            .where(PackDetails.pack_status.not_in([settings.PARTIALLY_FILLED_BY_ROBOT, settings.DELETED_PACK_STATUS])) \
            .group_by(UniqueDrug.id)

        return mfd_drugs_query, manual_drugs_query
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_manual_drugs {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_manual_drugs {}".format(e))
        raise e


@log_args_and_response
def get_change_ndc_history_dao(paginate, filter_fields):
    try:
        data_list = []
        DrugMasterAlias = DrugMaster.alias()
        UniqueDrugAlias = UniqueDrug.alias()
        DrugDimensionAlias = DrugDimension.alias()
        CustomDrugShapeAlias = CustomDrugShape.alias()

        fields_dict = {
            "old_drug_name": DrugMaster.concated_drug_name_field(),
            "new_drug_name": fn.CONCAT(
                                             DrugMasterAlias.drug_name, ' ', DrugMasterAlias.strength_value, ' ',
                                             DrugMasterAlias.strength
                                         )
        }
        clauses = []
        exact_search_fields = ['old_drug_name', 'new_drug_name']
        if filter_fields:
            clauses = get_filters(clauses=clauses, fields_dict=fields_dict, filter_dict=filter_fields,
                                  exact_search_fields=exact_search_fields)
        query = (ChangeNdcHistory.select(ChangeNdcHistory.id,
                                         ChangeNdcHistory.old_drug_id,
                                         ChangeNdcHistory.old_canister_id,
                                         ChangeNdcHistory.new_drug_id,
                                         ChangeNdcHistory.new_canister_id,
                                         DrugMaster.ndc.alias("old_drug_ndc"),
                                         DrugMasterAlias.ndc.alias("new_drug_ndc"),
                                         DrugMaster.image_name.alias("old_drug_image"),
                                         DrugMasterAlias.image_name.alias("new_drug_image"),
                                         DrugMaster.concated_drug_name_field().alias('old_drug_name'),
                                         fn.CONCAT(
                                             DrugMasterAlias.drug_name, ' ', DrugMasterAlias.strength_value, ' ',
                                             DrugMasterAlias.strength
                                         ).alias('new_drug_name'),
                                         DrugMaster.color.alias("old_drug_color"),
                                         DrugMasterAlias.color.alias("new_drug_color"),
                                         DrugMaster.imprint.alias("old_drug_imprint"),
                                         DrugMasterAlias.imprint.alias("new_drug_imprint"),
                                         CustomDrugShape.name.alias("old_drug_shape"),
                                         CustomDrugShapeAlias.name.alias("new_drug_shape")
                                         )
                 .join(DrugMaster, on=DrugMaster.id == ChangeNdcHistory.old_drug_id)
                 .join(DrugMasterAlias, on=DrugMasterAlias.id == ChangeNdcHistory.new_drug_id)
                 .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                       (UniqueDrug.txr == DrugMaster.txr)))
                 .join(DrugDimension, on=UniqueDrug.id == DrugDimension.unique_drug_id)
                 .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id)
                 .join(UniqueDrugAlias, on=((UniqueDrugAlias.formatted_ndc == DrugMasterAlias.formatted_ndc) &
                                            (UniqueDrugAlias.txr == DrugMasterAlias.txr)))
                 .join(DrugDimensionAlias, on=UniqueDrugAlias.id == DrugDimensionAlias.unique_drug_id)
                 .join(CustomDrugShapeAlias, on=DrugDimensionAlias.shape == CustomDrugShapeAlias.id)
                 .order_by(ChangeNdcHistory.id.desc())
                 )
        old_drug_list = []
        new_drug_list = []
        for record in query.dicts():
            name_ndc = record['old_drug_name'] + '(' + record['old_drug_ndc'] + ')'
            record['old_drug_name'] = name_ndc
            old_drug_list.append(record['old_drug_name'])
            name_ndc = record['new_drug_name'] + '(' + record['new_drug_ndc'] + ')'
            record['new_drug_name'] = name_ndc
            new_drug_list.append(record['new_drug_name'])
            data_list.append(record)
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        count = query.count()
        if paginate:
            query = apply_paginate(query, paginate)
        return list(query.dicts()), list(set(old_drug_list)), list(set(new_drug_list)), count
    except Exception as e:
        return e


@log_args_and_response
def get_canister_order_list_dao(paginate, company_id, filter_fields):
    try:
        drug_id_list = []
        response_drug_list = []
        data_list = []
        fields_dict = {
            "verified_drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),

        }
        clauses = []
        like_search_fields = ['verified_drug_name']

        sub_query = (BatchMaster.select(BatchMaster.id.alias('batch_id'),
                                        BatchMaster.status.alias('batch_status'),
                                        fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.pack_status)).alias("pack_status"))
                     .where(BatchMaster.status.in_([settings.BATCH_MERGED,
                                                    settings.BATCH_IMPORTED,
                                                    settings.BATCH_PROCESSING_COMPLETE]))
                     .join(PackDetails, JOIN_LEFT_OUTER, on=PackDetails.previous_batch_id == BatchMaster.id)
                     .group_by(BatchMaster.id)
                     .order_by(BatchMaster.id.desc()).dicts()
                     )
        imported_batch = True
        batch_list = []
        for record in sub_query:
            if len(batch_list) == 5:
                break
            if record['batch_status'] in [settings.BATCH_IMPORTED, settings.BATCH_PROCESSING_COMPLETE]:
                imported_batch = False
                if record['batch_status'] == settings.BATCH_PROCESSING_COMPLETE:
                    batch_list.append(record['batch_id'])
                continue
            elif record['batch_status'] == settings.BATCH_MERGED and imported_batch and record['pack_status'] != '5':
                continue
            else:
                batch_list.append(record['batch_id'])

        query = (MfdAnalysis.select(DrugTracker.drug_id,
                                    DrugMaster.ndc,
                                    DrugMaster.formatted_ndc,
                                    DrugMaster.txr,
                                    DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                    DrugMaster.image_name,
                                    DrugMaster.imprint,
                                    DrugMaster.color,
                                    CustomDrugShape.name.alias("shape"),
                                    fn.SUM(DrugTracker.drug_quantity).alias('quantity'),
                                    fn.COUNT(fn.DISTINCT(DrugTracker.pack_id)).alias('pack_count'))
                 .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id)
                 .join(DrugTracker, on=DrugTracker.slot_id == MfdAnalysisDetails.slot_id )
                 .join(DrugMaster, on=DrugMaster.id == DrugTracker.drug_id)
                 .join(CanisterOrders, JOIN_LEFT_OUTER, on=CanisterOrders.drug_id == DrugMaster.id)
                 .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                       (UniqueDrug.txr == DrugMaster.txr)))
                 .join(DrugDimension, on=UniqueDrug.id == DrugDimension.unique_drug_id)
                 .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id)
                 .where(
                        MfdAnalysis.batch_id.in_(batch_list),
                        CanisterOrders.id.is_null(True),
                        DrugDimension.verification_status_id == settings.DRUG_VERIFICATION_STATUS['verified'],

                        )
                 .group_by(DrugTracker.drug_id)
                 .order_by(fn.SUM(DrugTracker.drug_quantity).desc())
                 )

        ndc_list = []
        for record in query.dicts():
            drug_id_list.append(record['drug_id'])

        if drug_id_list:
            sub_query = (DrugMaster.select(fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.active)).alias("is_active"),
                                           DrugMaster.id.alias('drug_id')
                                           )
                         .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.drug_id == DrugMaster.id)
                         .where(DrugMaster.id.in_(drug_id_list)).group_by(DrugMaster.id))
            for record in sub_query.dicts():
                if record['is_active'] and '1' in record['is_active']:
                    continue
                response_drug_list.append(record['drug_id'])

        clauses = get_filters(clauses, fields_dict, filter_dict=filter_fields,
                              like_search_fields=like_search_fields)
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        for record in query.dicts():
            if record['drug_id'] in response_drug_list:
                data_list.append(record)
                ndc_list.append(record['ndc'])
        count = len(data_list)
        paginated_result = dpws_paginate(data_list, paginate)
        return paginated_result, count, ndc_list
    except Exception as e:
        return e
