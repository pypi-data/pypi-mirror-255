import functools
import operator
from pprint import pprint

import numpy as np
import pandas as pd

from playhouse.shortcuts import case

import settings
from peewee import InternalError, IntegrityError, DataError, fn, JOIN_LEFT_OUTER

from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args
from src.dao.device_manager_dao import get_location_id_by_location_number_dao
from src.model.model_canister_master import CanisterMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_error_details import ErrorDetails
from src.model.model_location_master import LocationMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_canister_usage import PackCanisterUsage
from src.model.model_pack_details import PackDetails
from src.model.model_pack_error import PackError
from src.model.model_pack_fill_error_v2 import PackFillErrorV2
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_status_tracker import PackStatusTracker
from src.model.model_patient_rx import PatientRx
from src.model.model_pharmacy_master import PharmacyMaster
from src.model.model_slot_details import SlotDetails
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger

graph_type_flags = frozenset(["pie", "line"])
group_flags = frozenset(["canister_id", "canister_location", "unique_drug", "canister_level"])
period_cycle_flags = frozenset(["year", "month", "quarter", "week"])

@log_args
def get_active_canister_count(device_id):
    """
    function to get active canister count
    @param device_id:
    @return:
    """
    try:

        active_canisters = CanisterMaster.select().dicts() \
            .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(CanisterMaster.active == settings.is_canister_active,
                   LocationMaster.device_id == device_id) \
            .count()
        return active_canisters

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_active_canister_count {}".format(e))
        raise e


@log_args
def get_max_canister_count(device_id):
    """
        function to get max canister count
        @param device_id:
        @return:
    """
    try:
        max_canisters = DeviceMaster.db_get_by_id(device_id).max_canisters
        return max_canisters

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_max_canister_count {}".format(e))
        raise e


@log_args
def get_drug_state_dao(company_id, current_date, pack_status_list, previous_date):
    """
           function to get max canister count
           @param company_id:
           @param current_date:
           @param pack_status_list:
           @param previous_date:
           @return:
    """
    try:
        query = SlotDetails.select(
            SlotDetails.quantity,
            SlotDetails.is_manual,
            SlotDetails.pack_rx_id,
            PackRxLink.patient_rx_id,
            PackDetails.id.alias("pack_id"),
            PackDetails.modified_date,
            DrugMaster.drug_name,
            DrugMaster.ndc,
            DrugMaster.strength,
            DrugMaster.strength_value,
            PackStatusTracker.created_date
        ).dicts() \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.pack_rx_id) \
            .join(PackStatusTracker, on=PackDetails.id == PackStatusTracker.pack_id) \
            .where(PackDetails.company_id == company_id,
                   PackStatusTracker.status << pack_status_list,
                   PackStatusTracker.created_date.between(previous_date, current_date))
        return query

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_drug_state_dao {}".format(e))
        raise e

#
@log_args
def get_pack_error_stats_dao(filters):
    """
    @return:
    @param filters:
    @return:
    """
    try:
        system_id = filters['system_id']
        from_date = filters['from_date']
        to_date = filters['to_date']
        _time_zone = filters['time_zone']
        pack_date = fn.DATE(fn.CONVERT_TZ(PackDetails.modified_date, settings.TZ_UTC, _time_zone))
        pack_status_list = [settings.MANUAL_PACK_STATUS,
                            settings.DONE_PACK_STATUS,
                            settings.PROCESSED_PACK_STATUS,
                            settings.PROCESSED_MANUALLY_PACK_STATUS]
        sub_q = PackDetails.select(pack_date.alias('process_date'),
                                   PackDetails.id.alias('pack_id'),
                                   fn.IF(fn.COUNT(PackFillErrorV2.id) == 0, 0, 1).alias('is_error')).dicts() \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackFillErrorV2, JOIN_LEFT_OUTER, on=PackFillErrorV2.pack_id == PackDetails.id) \
            .where(PackDetails.system_id == system_id,
                   pack_date.between(from_date, to_date),
                   PackDetails.pack_status << pack_status_list) \
            .group_by(PackDetails.id).alias('pack_error_query')
        # query = sub_q.select(sub_q.c.process_date,
        #                      fn.COUNT(sub_q.c.pack_id).alias('total_packs'),
        #                      fn.COUNT(sub_q.c.is_error).alias('error_packs')).dicts()\
        #         .group_by(sub_q.c.process_date)
        # above implementation does not work as expected, so will do redundant join with PackDetails
        # to get it work with peewee
        query = PackDetails.select(sub_q.c.process_date,
                                   fn.COUNT(sub_q.c.pack_id).alias('total_packs'),
                                   fn.SUM(sub_q.c.is_error).alias('error_packs')
                                   ).dicts() \
            .join(sub_q, on=sub_q.c.pack_id == PackDetails.id) \
            .group_by(sub_q.c.process_date)
        return query

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_pack_error_stats_dao {}".format(e))
        raise e

@log_args
def get_top_drug_dao(data):
    """
        @return:
        @param data:
        @return:
    """
    try:

        clauses = list()
        system_id = data['system_id']
        from_date = data.get('from_date', None)
        to_date = data.get('to_date', None)
        number_of_drugs = data.get('number_of_drugs', 10)
        clauses.append((PackDetails.system_id == system_id))
        if to_date and from_date:
            clauses.append((PackDetails.created_date.between(from_date, to_date)))
        top_drugs_data = list()
        query = DrugMaster.select(DrugMaster.drug_name,
                                  DrugMaster.ndc,
                                  DrugMaster.strength,
                                  DrugMaster.strength_value,
                                  DrugMaster.color,
                                  DrugMaster.imprint,
                                  DrugMaster.image_name,
                                  DrugMaster.shape,
                                  fn.SUM(SlotDetails.quantity).alias('total_quantity')).dicts() \
            .join(PatientRx, on=PatientRx.drug_id == DrugMaster.id) \
            .join(PackRxLink, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr) \
            .order_by(fn.SUM(SlotDetails.quantity).desc()) \
            .limit(number_of_drugs)
        return query, top_drugs_data

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_top_drug_dao {}".format(e))
        raise e


@log_args
def get_error_drug_count_query(data):
    """
    @param data:
    @return:

    """
    try:
        time_zone = data["time_zone"]
        system_id = data["system_id"]
        company_id = data["company_id"]

        created_date = fn.DATE(fn.CONVERT_TZ(ErrorDetails.created_date, settings.TZ_UTC, time_zone))
        if "from_date" in data and "to_date" in data:
            from_date = data["from_date"]
            to_date = data["to_date"]
            where_fields = [created_date.between(from_date, to_date),
                            PackDetails.system_id == system_id,
                            PackDetails.company_id == company_id,
                            ErrorDetails.out_of_class_reported == 0]
        else:
            where_fields = [PackDetails.system_id == system_id,
                            PackDetails.company_id == company_id,
                            ErrorDetails.out_of_class_reported == 0]

        # pvs_error_qty = PVSDrugCount.predicted_qty - PVSDrugCount.expected_qty
        # PackGridAlias = PackGrid.alias()
        #
        # select_fields = [
        #     fn.COALESCE(PackFillErrorV2.pack_id, PVSDrugCount.pack_id).alias("pack_id"),
        #     fn.COALESCE(PackFillErrorV2.unique_drug_id, PVSDrugCount.unique_drug_id).alias("unique_drug_id"),
        #     UniqueDrug.txr.alias("txr"),
        #     UniqueDrug.formatted_ndc.alias("formatted_ndc"),
        #     fn.COALESCE(SlotFillErrorV2.pack_grid_id, PVSDrugCount.pack_grid_id).alias("pack_grid_id"),
        #     SlotFillErrorV2.error_qty.alias("error_qty"),
        #     pvs_error_qty.alias("pvs_error_qty"),
        #     (fn.IFNULL(SlotFillErrorV2.error_qty, 0) - fn.IFNULL(pvs_error_qty, 0)).alias("mpse_qty"),
        #     fn.IF(
        #         fn.ABS((fn.IFNULL(SlotFillErrorV2.error_qty, 0) - fn.IFNULL(pvs_error_qty, 0))) == 0,
        #         None,
        #         fn.ABS((fn.IFNULL(SlotFillErrorV2.error_qty, 0) - fn.IFNULL(pvs_error_qty, 0)))
        #     ).alias("misplaced_qty"),
        #     fn.IF(((SlotFillErrorV2.error_qty > 0) & (pvs_error_qty > 0)),
        #           fn.LEAST(fn.ABS(SlotFillErrorV2.error_qty), fn.ABS(pvs_error_qty)), None).alias("extra_qty"),
        #     fn.IF(((SlotFillErrorV2.error_qty < 0) & (pvs_error_qty < 0)),
        #           fn.LEAST(fn.ABS(SlotFillErrorV2.error_qty), fn.ABS(pvs_error_qty)), None).alias("missing_qty"),
        #     fn.IF(SlotFillErrorV2.broken == True, SlotFillErrorV2.broken, None).alias("broken"),
        #     created_date.alias("created_date")
        # ]
        #
        # query1 = SlotFillErrorV2.select(*select_fields)\
        #     .join(PackFillErrorV2, on=PackFillErrorV2.id == SlotFillErrorV2.pack_fill_error_id)\
        #     .join(UniqueDrug, on=UniqueDrug.id == PackFillErrorV2.unique_drug_id) \
        #     .join(PackDetails, on=PackDetails.id == PackFillErrorV2.pack_id)\
        #     .join(PVSDrugCount, JOIN_LEFT_OUTER,
        #           on=(PackFillErrorV2.pack_id == PVSDrugCount.pack_id) &
        #              (PackFillErrorV2.unique_drug_id == PVSDrugCount.unique_drug_id) &
        #              (SlotFillErrorV2.pack_grid_id == PVSDrugCount.pack_grid_id))\
        #     .join(PackGrid, on=SlotFillErrorV2.pack_grid_id == PackGrid.id)\
        #     .where(functools.reduce(operator.and_, where_fields))
        #
        # query2 = PVSDrugCount.select(*select_fields) \
        #     .join(UniqueDrug, on=UniqueDrug.id == PVSDrugCount.unique_drug_id) \
        #     .join(PackDetails, on=PackDetails.id == PVSDrugCount.pack_id) \
        #     .join(PackFillErrorV2, JOIN_LEFT_OUTER,
        #           on=(PackFillErrorV2.pack_id == PackDetails.id) &
        #              (PackFillErrorV2.unique_drug_id == PVSDrugCount.unique_drug_id))\
        #     .join(SlotFillErrorV2, JOIN_LEFT_OUTER,
        #           on=(SlotFillErrorV2.pack_fill_error_id == PackFillErrorV2.id) &
        #              (SlotFillErrorV2.pack_grid_id == PVSDrugCount.pack_grid_id)) \
        #     .join(PackGridAlias, on=PackGridAlias.id == PVSDrugCount.pack_grid_id)\
        #     .where(functools.reduce(operator.and_, where_fields))
        #
        # query = (query1 | query2)
        # temp_query = query
        # for item in temp_query:
        #     print(item)
        #
        query = ErrorDetails.select(PackDetails.id.alias('pack_id'),
                                    ErrorDetails.unique_drug_id.alias('unique_drug_id'),
                                    UniqueDrug.txr,
                                    UniqueDrug.formatted_ndc,
                                    ErrorDetails.pack_grid_id.alias("pack_grid_id"),
                                    fn.IF(ErrorDetails.error_qty > 0, ErrorDetails.error_qty, None),
                                    fn.IF(ErrorDetails.pvs_error_qty > 0, ErrorDetails.pvs_error_qty, None),
                                    ErrorDetails.mpse.alias('mpse_qty'),
                                    fn.IF(ErrorDetails.missing > 0, ErrorDetails.missing, None).alias('missing_qty'),
                                    fn.IF(ErrorDetails.extra > 0, ErrorDetails.extra, None).alias('extra_qty'),
                                    fn.IF(fn.ABS(ErrorDetails.mpse) > 0, fn.ABS(ErrorDetails.mpse), None).alias(
                                        'misplaced_qty'),
                                    fn.IF(ErrorDetails.broken == True, ErrorDetails.broken, None).alias('broken'),
                                    ErrorDetails.out_of_class_reported,
                                    ErrorDetails.created_date).dicts() \
            .join(PackDetails, on=PackDetails.id == ErrorDetails.pack_id) \
            .join(PackGrid, on=PackGrid.id == ErrorDetails.pack_grid_id) \
            .join(UniqueDrug, on=ErrorDetails.unique_drug_id == UniqueDrug.id) \
            .where(functools.reduce(operator.and_, where_fields))

        print("query", query)

        return query

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_error_drug_count_query {}".format(e))
        raise e


@log_args
def get_pack_error_instances_dao(data):
    """
    @param data:
    @return:
    """
    try:
        error_drug_count_query = get_error_drug_count_query(data)
        error_drug_count_query = error_drug_count_query.alias("error_drug_count")
        filled_date = fn.DATE(fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC, data["time_zone"]))
        pack_status_list = [settings.MANUAL_PACK_STATUS,
                            settings.DONE_PACK_STATUS,
                            settings.PROCESSED_PACK_STATUS,
                            settings.PROCESSED_MANUALLY_PACK_STATUS,
                            settings.VERIFIED_PACK_STATUS]
        query = PackDetails.select(fn.COUNT(fn.DISTINCT(PackDetails.id)).alias("total_packs"),
                                   fn.COUNT(fn.DISTINCT(error_drug_count_query.c.pack_id)).alias("error_packs"),
                                   filled_date.alias("created_date"),
                                   fn.WEEK(filled_date).alias("week"),
                                   fn.MONTH(filled_date).alias("month"),
                                   fn.YEAR(filled_date).alias("year"),
                                   fn.QUARTER(filled_date).alias("quarter")) \
            .join(error_drug_count_query, JOIN_LEFT_OUTER, on=PackDetails.id == error_drug_count_query.c.pack_id) \
            .where(filled_date.between(data["from_date"], data["to_date"]),
                   PackDetails.company_id == data['company_id'],
                   PackDetails.system_id == data['system_id'],
                   PackDetails.pack_status << pack_status_list)
        if "period_cycle" in data:
            if data["period_cycle"] == "year":
                query = query.group_by(fn.YEAR(filled_date))

            if data["period_cycle"] == "quarter":
                query = query.group_by(fn.QUARTER(filled_date),
                                       fn.YEAR(filled_date))

            if data["period_cycle"] == "month":
                query = query.group_by(fn.MONTH(filled_date),
                                       fn.YEAR(filled_date))

            if data["period_cycle"] == "week":
                query = query.group_by(fn.WEEK(filled_date),
                                       # fn.MONTH(filled_date),
                                       fn.YEAR(filled_date))
        return query

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_pack_error_instances_dao {}".format(e))
        raise e


@log_args
def get_pack_error_distribution_dao(data):
    try:
        # use base query to find all combined error instances for all type
        error_drug_count_query = get_error_drug_count_query(data)
        error_drug_count_query = error_drug_count_query.alias("error_drug_count")
        query = PackFillErrorV2.select(fn.COUNT(error_drug_count_query.c.broken).alias("broken_instances"),
                                       fn.COUNT(error_drug_count_query.c.misplaced_qty).alias("misplaced_instances"),
                                       fn.COUNT(error_drug_count_query.c.extra_qty).alias("extra_instances"),
                                       fn.COUNT(error_drug_count_query.c.missing_qty).alias("missing_instances"),
                                       error_drug_count_query.c.created_date.alias("created_date"),
                                       fn.WEEK(error_drug_count_query.c.created_date).alias("week"),
                                       fn.MONTH(error_drug_count_query.c.created_date).alias("month"),
                                       fn.YEAR(error_drug_count_query.c.created_date).alias("year"),
                                       fn.QUARTER(error_drug_count_query.c.created_date).alias("quarter")
                                       ) \
            .from_(error_drug_count_query)
        if "period_cycle" in data:
            if data["period_cycle"] == "year":
                query = query.group_by(fn.YEAR(error_drug_count_query.c.created_date))

            if data["period_cycle"] == "quarter":
                query = query.group_by(fn.QUARTER(error_drug_count_query.c.created_date),
                                       fn.YEAR(error_drug_count_query.c.created_date))

            if data["period_cycle"] == "month":
                query = query.group_by(fn.MONTH(error_drug_count_query.c.created_date),
                                       fn.YEAR(error_drug_count_query.c.created_date))

            if data["period_cycle"] == "week":
                query = query.group_by(fn.WEEK(error_drug_count_query.c.created_date),
                                       fn.YEAR(error_drug_count_query.c.created_date))
        return query

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_pack_error_distribution_dao {}".format(e))
        raise e


def get_error_pill_instances(data, error_type):
    """
    @param data:
    @param error_type:
    @return:
    """
    if data["group"] not in group_flags:
        return error(1020, 'Incorrect value for group.')

    select_fields = [DrugMaster.drug_name,
                     DrugMaster.strength_value,
                     DrugMaster.strength]

    if data["group"] == "canister_location":
        group_by_field = LocationMaster.location_number, LocationMaster.device_id
    else:
        group_by_field = PackCanisterUsage.canister_id,

    try:
        where_field, query = get_error_instances_count_query(data, error_type, select_fields)
        query = query.group_by(*group_by_field).where(where_field > 0).dicts()
        print('group by query', query)
        data = list()
        total_instances = 0
        erro_instance_key = '{}_error_instance'.format(error_type)
        for item in query:
            total_instances += item[erro_instance_key]
            data.append(item)
        # response = list(query.dicts())
        return create_response({"total_instances": total_instances, "error_data": data})
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_error_pill_instances {}".format(e))
        return error(2001)


def get_error_instances_count_query(data, error_type, extra_select_fields=None):
    """
    @param data:
    @param error_type:
    @param extra_select_fields:
    @return:
    """
    try:
        select_field = []
        error_drug_count_query = get_error_drug_count_query(data)

        error_drug_count_query = error_drug_count_query.alias("error_drug_count")

        level_tuples = [
            ((LocationMaster.location_number.between(1, 64)), 1),
            (LocationMaster.location_number.between(65, 128), 2),
            (LocationMaster.location_number.between(129, 192), 3),
            (LocationMaster.location_number.between(193, 256), 4)
        ]
        where_field = None
        if error_type == "extra":
            select_field = [fn.COUNT(error_drug_count_query.c.extra_qty).alias("extra_error_instance"),
                            fn.SUM(error_drug_count_query.c.extra_qty).alias("extra_qty")]
            where_field = error_drug_count_query.c.extra_qty
        if error_type == "missing":
            select_field = [fn.COUNT(error_drug_count_query.c.missing_qty).alias("missing_error_instance"),
                            fn.SUM(error_drug_count_query.c.missing_qty).alias("missing_qty")]
            where_field = error_drug_count_query.c.missing_qty
        if error_type == "broken":
            select_field = [fn.COUNT(error_drug_count_query.c.broken).alias("broken_error_instance"),
                            case(None, level_tuples).alias("canister_level")
                            ]
            where_field = error_drug_count_query.c.broken
        if error_type == "misplaced":
            select_field = [fn.COUNT(error_drug_count_query.c.misplaced_qty).alias("misplaced_error_instance"),
                            fn.SUM(error_drug_count_query.c.misplaced_qty).alias("misplaced_qty")]
            where_field = error_drug_count_query.c.misplaced_qty

        if extra_select_fields is None:
            extra_select_fields = list()

        # query = SlotTransaction.select(SlotTransaction.canister_id,
        #                                SlotTransaction.canister_number,
        #                                SlotTransaction.device_id,
        #                                RobotMaster.name.alias('device_name'),
        #                                error_drug_count_query.c.created_date,
        #                                error_drug_count_query.c.unique_drug_id.alias('unique_drug_id'),
        #                                *select_field,
        #                                *extra_select_fields) \
        #     .join(SlotDetails, on=SlotTransaction.slot_id == SlotDetails.id) \
        #     .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
        #     .join(RobotMaster, on=RobotMaster.id == SlotTransaction.device_id) \
        #     .join(DrugMaster, on=SlotTransaction.drug_id == DrugMaster.id) \
        #     .join(error_drug_count_query, on=(error_drug_count_query.c.formatted_ndc == DrugMaster.formatted_ndc)
        #                                      & (error_drug_count_query.c.txr == DrugMaster.txr)
        #                                      & (error_drug_count_query.c.pack_id == SlotTransaction.pack_id)
        #                                      & (error_drug_count_query.c.pack_grid_id == SlotHeader.pack_grid_id))
        #
        join_condition = ((error_drug_count_query.c.pack_id == PackCanisterUsage.pack_id) &
                          (error_drug_count_query.c.unique_drug_id == PackCanisterUsage.unique_drug_id) &
                          (error_drug_count_query.c.pack_grid_id == PackCanisterUsage.pack_grid_id))

        query = PackCanisterUsage.select(PackCanisterUsage.canister_id,
                                         LocationMaster.location_number,
                                         LocationMaster.device_id,
                                         error_drug_count_query.c.created_date,
                                         error_drug_count_query.c.unique_drug_id.alias('unique_drug_id'),
                                         *select_field,
                                         *extra_select_fields) \
            .join(error_drug_count_query, on=join_condition) \
            .join(LocationMaster, on=LocationMaster.id == PackCanisterUsage.location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id)\
            .join(UniqueDrug, on=UniqueDrug.id == PackCanisterUsage.unique_drug_id) \
            .join(DrugMaster, on=UniqueDrug.drug_id == DrugMaster.id)

        print(query)
        return where_field, query

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_error_instances_count_query {}".format(e))
        raise e


def get_error_pill_instances_by_canister(data, error_type):
    """

    @param data:
    @param error_type:
    @return:
    """
    if data["group"] not in group_flags:
        return error(1020, 'Incorrect value for group.')

    select_fields = [DrugMaster.drug_name,
                     DrugMaster.strength_value,
                     DrugMaster.strength]
    try:
        error_drug_count_query = get_error_drug_count_query(data)

        error_drug_count_query = error_drug_count_query.alias("error_drug_count")

        where_field, query = get_error_instances_count_query(data, error_type, select_fields)

        if data["group"] == "canister_location":
            final_query = query.where(LocationMaster.location_number == data["location_number"],
                                      LocationMaster.device_id == data["device_id"],
                                      where_field > 0)
        else:
            final_query = query.where(PackCanisterUsage.canister_id == data["canister_id"],
                                      where_field > 0)
        print("final query", final_query)
        query = final_query.group_by(fn.DATE(error_drug_count_query.c.created_date)).dicts()

        canister_used_list = get_pack_canister_usage_details(data)
        # date_list = list()
        error_type = '{}_error_instance'.format(error_type)
        # error_list = list()
        # error_date_dict = dict()
        canister_used_dict = dict()   # todo get all the dates when the drug/canister was used
        error_data = list(final_query.group_by(fn.DATE(error_drug_count_query.c.created_date)).dicts())
        for i in range(len(canister_used_list)):
            canister_used_dict[canister_used_list[i]['filled_date']] = 0
        pprint(canister_used_dict)
        for record in query:
            print(record['created_date'].date())
            canister_used_dict[record['created_date'].date()] = record[error_type]
        pprint(canister_used_dict)

        error_list = list()
        for i in sorted(canister_used_dict.keys()):
            error_list.append(canister_used_dict[i])
        # error_list = list(canister_used_dict.values())
        series_error_data = pd.Series(np.array(error_list))

        window = data.get('window', settings.ANALYSIS_DAYS_WINDOW)
        threshold_value = data.get('threshold_pill_count', settings.LEVEL_ERROR_THRESHOLD)
        recommendation = list()
        moving_average = series_error_data.rolling(window=window).mean()
        pprint(moving_average)
        moving_average = moving_average[(window-1):]
        moving_average = list(moving_average)
        pprint(moving_average)
        # date_list = date_list[window:]
        for i in range(len(moving_average)):
            if moving_average[i] > threshold_value:
                if 'canister_id' in data:
                    recommendation.append({'canister_id': data["canister_id"],
                                           'drug_name': '{} {} {}'.format(error_data[0]['drug_name'],
                                                 error_data[0]['strength_value'], error_data[0]['strength']),
                                           'days': window})
                    # recommendation.append('Cannister id - {} containing {} {}{} has dropped extra pills for a '
                    #                       'consecutive {} days, cannister is damaged and should be replaced'.
                    #                       format(data["canister_id"], error_data[0]['drug_name'],
                    #                              error_data[0]['strength_value'], error_data[0]['strength'], window))
                    break
                elif "location_number" in data and "device_id" in data:
                    device_name = error_data[0]['device_name']
                    recommendation.append({'location_number': data["location_number"],
                                           'device_id': data['device_id'],
                                           'device_name': device_name,
                                           'drug_name': '{} {} {}'.format(error_data[0]['drug_name'],
                                                                         error_data[0]['strength_value'],
                                                                         error_data[0]['strength']),
                                           'days': window})
                    break

        return create_response({'error_data': error_data, 'recommendation': recommendation})

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_error_pill_instances_by_canister {}".format(e))
        raise e


def get_error_pill_instances_by_group(data, error_type):
    """

    @param data:
    @param error_type:
    @return:
    """

    try:
        if data["period_cycle"] not in period_cycle_flags:
            return error(1020, 'Incorrect value for period_cycle.')

        error_drug_count_query = get_error_drug_count_query(data)

        error_drug_count_query = error_drug_count_query.alias("error_drug_count")

        select_fields = [fn.YEAR(error_drug_count_query.c.created_date).alias("year"),
                         fn.QUARTER(error_drug_count_query.c.created_date).alias("quarter"),
                         fn.MONTH(error_drug_count_query.c.created_date).alias("month"),
                         fn.WEEK(error_drug_count_query.c.created_date).alias("week")]

        where_field, query = get_error_instances_count_query(data, error_type, select_fields)
        new_query = query
        print("response of trends")
        pprint(list(new_query.dicts()))
        if data["period_cycle"] == "year":
            final_query = query.group_by(fn.YEAR(error_drug_count_query.c.created_date))

        if data["period_cycle"] == "quarter":
            final_query = query.group_by(fn.QUARTER(error_drug_count_query.c.created_date),
                                         fn.YEAR(error_drug_count_query.c.created_date))

        if data["period_cycle"] == "month":
            final_query = query.group_by(fn.MONTH(error_drug_count_query.c.created_date),
                                         fn.YEAR(error_drug_count_query.c.created_date))

        if data["period_cycle"] == "week":
            final_query = query.group_by(fn.WEEK(error_drug_count_query.c.created_date),
                                         fn.YEAR(error_drug_count_query.c.created_date))

        response = list(final_query.where(where_field).dicts())
        return create_response(response)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_error_pill_instances_by_group {}".format(e))
        raise e


def get_lost_pill_instances_dao(data):
    """

    @param data:
    @return:
    """
    try:
        error_drug_count_query = get_error_drug_count_query(data)
        error_drug_count_query = error_drug_count_query.alias("error_drug_count")
        query = UniqueDrug.select(DrugMaster.drug_name,
                                  DrugMaster.strength_value,
                                  DrugMaster.strength,
                                  DrugMaster.imprint,
                                  DrugMaster.image_name,
                                  DrugMaster.ndc,
                                  error_drug_count_query.c.unique_drug_id,
                                  fn.SUM(error_drug_count_query.c.mpse_qty).alias("lost_qty")) \
            .join(DrugMaster, on=(DrugMaster.id == UniqueDrug.drug_id)) \
            .join(error_drug_count_query, on=(error_drug_count_query.c.unique_drug_id == UniqueDrug.id)) \
            .group_by(error_drug_count_query.c.unique_drug_id) \
            .having(fn.SUM(error_drug_count_query.c.mpse_qty) != 0)
        return query

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_lost_pill_instances_dao {}".format(e))
        raise e


def get_pack_canister_usage_details(fill_detials):
    company_id = fill_detials['company_id']
    system_id = fill_detials['system_id']
    from_date = fill_detials['from_date']
    to_date = fill_detials['to_date']
    canister_id = fill_detials.get('canister_id', None)
    location_number = fill_detials.get('location_number', None)
    device_id = fill_detials.get('device_id', None)

    clauses = list()
    if company_id:
        clauses.append((PackDetails.company_id == company_id))
    if system_id:
        clauses.append((PackDetails.system_id == system_id))
    if from_date and to_date:
        clauses.append((PackDetails.filled_date.between(from_date, to_date)))
    if canister_id:
        clauses.append((PackCanisterUsage.canister_id == canister_id))
    if device_id and location_number:
        location_id = get_location_id_by_location_number_dao(device_id=device_id, location_number=location_number)
        clauses.append((PackCanisterUsage.location_id == location_id))

    pack_fill_details = PackCanisterUsage.select(
        fn.DISTINCT(fn.DATE(PackDetails.filled_date)).alias('filled_date')).dicts() \
        .join(PackDetails, on=PackDetails.id == PackCanisterUsage.pack_id) \
        .where(functools.reduce(operator.and_, clauses))

    print('canister_used_list')
    from pprint import pprint
    pprint(list(pack_fill_details))
    return list(pack_fill_details)


def get_pharmacy_master_data_dao(system_id):
    """
    @param system_id:
    @return:
    """
    try:
        return PharmacyMaster.db_get(system_id)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_pharmacy_master_data_dao {}".format(e))
        raise e


def db_get_pharmacy_master_data_dao():
    try:
        return PharmacyMaster.db_get_pharmacy_data()

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_pharmacy_master_data_dao {}".format(e))
        raise e

