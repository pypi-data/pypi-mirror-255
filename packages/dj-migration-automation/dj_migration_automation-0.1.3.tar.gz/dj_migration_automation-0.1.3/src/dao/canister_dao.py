import functools
import math
import operator
import os
import sys
import threading
from collections import defaultdict, OrderedDict
from copy import deepcopy
from typing import List, Any, Optional, Dict, Set
from peewee import DoesNotExist, InternalError, IntegrityError, DataError, JOIN_LEFT_OUTER, fn, Clause, SQL
from datetime import datetime, timedelta, date
from functools import reduce
from playhouse.shortcuts import case, cast

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import fn_shorten_drugname_v2, get_current_date, \
    escape_wrap_wildcard, get_canister_volume, get_max_possible_drug_quantities_in_canister, log_args_and_response, \
    last_day_of_month
from dosepack.utilities.utils import log_args_and_response, log_args, get_current_date_time
from migrations.migration_for_zone_implementation_in_canister_master import CanisterZoneMapping
from src.api_utility import apply_paginate, get_results, get_filters, get_orders
from src.dao.canister_transfers_dao import get_slow_movers_for_device
from src.dao.drug_tracker_dao import get_drug_tracker_info_by_canister_ids
# from src.dao.mfd_dao import get_unique_mfd_drop
from src.dao.pack_dao import db_get_progress_filling_left_pack_ids, db_get_current_location_details_by_canisters, \
    get_packs_from_pack_queue_for_system
from src.dao.device_manager_dao import get_device_data_by_device_id_dao, get_location_id_by_location_number_dao
from src.dao.drug_dao import get_drug_id_list_for_same_configuration_by_drug_id, get_drug_stocks_and_dimension_details, \
    get_fndc_txr_wise_inventory_qty
from src.dao.inventory_dao import get_drug_lot_information_from_lot_number_dao, \
    get_drug_bottle_count_by_drug_and_company_id
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_orders import CanisterOrders
from src.model.model_canister_parameters import CanisterParameters
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_change_ndc_history import ChangeNdcHistory
from src.model.model_custom_shape_canister_parameters import CustomShapeCanisterParameters
from src.model.model_drug_canister_parameters import DrugCanisterParameters
from src.model.model_drug_canister_stick_mapping import DrugCanisterStickMapping
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_drug_status import DrugStatus
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_tracker import DrugTracker
from src.model.model_generate_canister import GenerateCanister
from src.model.model_guided_meta import GuidedMeta
from src.model.model_guided_tracker import GuidedTracker
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_replenish_skipped_canister import ReplenishSkippedCanister
from src.model.model_product_details import ProductDetails
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_skipped_canister import SkippedCanister
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_small_stick_canister_parameters import SmallStickCanisterParameters
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src import constants
from src.exceptions import CanisterNotExist
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_canister_drum import CanisterDrum
from src.model.model_canister_history import CanisterHistory
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_status_history import CanisterStatusHistory
from src.model.model_canister_status_history_comment import CanisterStatusHistoryComment
from src.model.model_canister_stick import CanisterStick
from src.model.model_canister_testing_status import CanisterTestingStatus
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_code_master import CodeMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_drug_dimension import DrugDimension
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_canister_master import MfdCanisterMaster
from src.model.model_small_canister_stick import SmallCanisterStick
from src.model.model_zone_master import ZoneMaster
from src.dao.pack_analysis_dao import get_canister_drug_quantity_required_in_batch, db_get_drop_time
from src.service.misc import update_replenish_queue_count, publish_voice_notification
from utils.drug_inventory_webservices import get_current_inventory_data

logger = settings.logger


mfd_latest_analysis_sub_query = MfdAnalysis.select(fn.MAX(MfdAnalysis.order_no).alias('max_order_number'),
                                                   MfdAnalysis.mfd_canister_id.alias('mfd_canister_id'),
                                                   MfdAnalysis.status_id.alias("status_id")) \
    .group_by(MfdAnalysis.mfd_canister_id).alias('sub_query')


@log_args_and_response
def get_canister_present_on_location(location_id_list: list) -> object:

    try:
        return CanisterMaster.get(CanisterMaster.location_id.in_(location_id_list))

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_canister_present_on_location {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_present_on_location {}".format(e))
        raise e


@log_args_and_response
def get_empty_locations_count_of_drawers_dao(drawer_ids: list) -> dict:
    db_result = dict()
    try:

        # applied an extra condition to fetch the empty locations that are not disabled
        query = ContainerMaster.select(ContainerMaster.id.alias('drawer_id'),
                                       (fn.COUNT(fn.Distinct(LocationMaster.id)) - fn.COUNT(CanisterMaster.id))
                                       .alias('empty_locations_count'),
                                       ).dicts() \
            .join(LocationMaster, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .where((ContainerMaster.id << drawer_ids), (LocationMaster.is_disabled == 0)) \
            .group_by(ContainerMaster.id)

        for record in query:
            db_result[record["drawer_id"]] = record["empty_locations_count"]
        return db_result

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_empty_locations_count_of_drawers_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_empty_locations_count_of_drawers_dao {}".format(e))
        raise e


@log_args_and_response
def get_canister_data_by_rfid_dao(rfid: str) -> dict:
    try:
        return CanisterMaster.db_get_canister_data_by_rfid(rfid=rfid)

    except CanisterNotExist as e:
        logger.error("error in get_canister_data_by_rfid_dao {}".format(e))
        raise e

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_canister_data_by_rfid_dao {}".format(e))
        raise e


@log_args_and_response
def get_canister_data_by_canister_ids(canister_ids, filters, paginate, sort_fields):
    try:
        clauses = [CanisterMaster.id << canister_ids]
        drug_list = []
        data_list = []
        order_list = []
        fields_dict = {
            'drawer_id': cast(
                fn.Substr(ContainerMaster.drawer_name, 1, fn.instr(ContainerMaster.drawer_name, '-') - 1), 'CHAR'),
            'location_id': cast(
                fn.Substr(ContainerMaster.drawer_name, fn.instr(ContainerMaster.drawer_name, '-') + 1), 'SIGNED'),
            "canister_id": CanisterMaster.id,
            "drug_name": DrugMaster.concated_drug_name_field(),
            "zone_name": ZoneMaster.id,
            "device_name": DeviceMaster.id,
            # "display_location": LocationMaster.display_location
        }
        exact_search_fields = ['canister_id', 'drug_name']

        if canister_ids:
            sub_query_1 = (
                CanisterStatusHistory.select(fn.MAX(CanisterStatusHistory.id).alias("canister_status_history_id"),
                                             CanisterStatusHistory.canister_id.alias("canister_id"))
                .group_by(CanisterStatusHistory.canister_id).alias("sub_query_1"))

            sub_query = (CanisterStatusHistoryComment.select(sub_query_1.c.canister_id.alias("canister_id"),
                                                             CanisterStatusHistoryComment.comment.alias("comment"),
                                                             CanisterStatusHistoryComment.canister_status_history_id)
                         .join(sub_query_1,
                               on=CanisterStatusHistoryComment.canister_status_history_id == sub_query_1.c.canister_status_history_id).alias(
                "sub_query"))
            query = (CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
                                           CanisterMaster.canister_type,
                                           DrugMaster.ndc,
                                           DrugMaster.concated_drug_name_field().alias('drug_name'),
                                           DrugMaster.image_name.alias("image_name"),
                                           DrugMaster.imprint,
                                           DrugMaster.color,
                                           CustomDrugShape.name.alias("shape"),
                                           LocationMaster.id.alias("location_id"),
                                           DeviceMaster.name.alias("device_name"),
                                           DeviceMaster.system_id.alias("system_id"),
                                           ZoneMaster.id.alias("zone_id"),
                                           ZoneMaster.name.alias("zone_name"),
                                           LocationMaster.display_location,
                                           sub_query.c.comment.alias("reason"),
                                           ContainerMaster.drawer_name)
                     .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)
                     .join(LocationMaster, JOIN_LEFT_OUTER, LocationMaster.id == CanisterMaster.location_id)
                     .join(ContainerMaster, JOIN_LEFT_OUTER, LocationMaster.container_id == ContainerMaster.id)
                     .join(DeviceMaster, JOIN_LEFT_OUTER, DeviceMaster.id == LocationMaster.device_id)
                     .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id)
                     .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id)
                     .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                           (UniqueDrug.txr == DrugMaster.txr)))
                     .join(DrugDimension, on=UniqueDrug.id == DrugDimension.unique_drug_id)
                     .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id)
                     .join(CanisterTestingStatus, JOIN_LEFT_OUTER,
                           on=CanisterMaster.id == CanisterTestingStatus.canister_id)
                     .join(sub_query, JOIN_LEFT_OUTER, on=sub_query.c.canister_id == CanisterMaster.id)
                     .where(functools.reduce(operator.and_, clauses))
                     )
            for record in query.dicts():

                drug_list.append(record['drug_name'])

            clauses = get_filters(clauses, fields_dict, filter_dict=filters, exact_search_fields=exact_search_fields)
            if clauses:
                query = query.where(functools.reduce(operator.and_, clauses))
            if sort_fields:
                order_list = get_orders(order_list, fields_dict, sort_fields)
            if order_list:
                query = query.order_by(*order_list)
            count = query.count()

            if paginate:
                query = apply_paginate(query, paginate)
            for record in query.dicts():
                record["drug_name"] = record['drug_name'] + '(' + record['ndc'] + ')'
                data_list.append(record)

            return data_list, list(set(drug_list)), count
        return [], drug_list, 0

    except Exception as e:
        logger.error("error in get_canister_data_by_canister_ids {}".format(e))
        return e


@log_args_and_response
def update_canister_location_based_on_rfid(location_id: int or None, rfid: str) -> int:
    try:
        return CanisterMaster.update_canister_location_based_on_rfid(location_id=location_id, rfid=rfid)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_canister_location_based_on_rfid {}".format(e))
        raise e


@log_args_and_response
def get_canister_history_latest_record_can_id_dao(canister_id: int):
    try:
        return CanisterHistory.db_get_latest_record_by_canister_id(canister_id=canister_id)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_history_latest_record_can_id_dao {}".format(e))
        raise e


@log_args_and_response
def update_canister_history_by_id_dao(dict_canister_info: dict, canister_history_id: int) -> int:
    try:
        return CanisterHistory.update_canister_history_by_id(dict_canister_info, canister_history_id)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_canister_history_by_id_dao {}".format(e))
        raise e


@log_args_and_response
def update_canister_by_rfid_dao(dict_canister_info, rfid):
    try:
        return CanisterMaster.update_canister_by_rfid(dict_canister_info=dict_canister_info, rfid=rfid)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in update_canister_by_rfid_dao {}".format(e))
        raise e


@log_args_and_response
def db_create_canister_master_dao(insert_canister_data):
    try:
        return CanisterMaster.db_create_canister_master(insert_canister_data=insert_canister_data)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_create_canister_master_dao {}".format(e))
        raise e


@log_args_and_response
def db_create_change_ndc_history_dao(insert_canister_data):
    try:
        return ChangeNdcHistory.insert(**insert_canister_data).execute()
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_create_canister_master_dao {}".format(e))
        raise e


@log_args_and_response
def update_canister_zone_mapping_by_rfid_dao(zone_ids, user_id, rfid):
    try:
        CanisterZoneMapping.update_canister_zone_mapping_by_rfid(zone_ids, user_id, rfid)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in update_canister_zone_mapping_by_rfid_dao {}".format(e))
        raise e


@log_args_and_response
def create_canister_history_record(data, table_name=CanisterHistory, add_fields=None, remove_fields=None,
                                   fn_transform=None,
                                   fn_validate=None, default_data_dict=None, get_or_create=True) -> dict:
    try:
        return CanisterHistory.db_create_record(data=data, table_name=table_name, add_fields=add_fields,
                                                remove_fields=remove_fields, fn_transform=fn_transform,
                                                fn_validate=fn_validate, default_data_dict=default_data_dict,
                                                get_or_create=get_or_create)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in create_canister_history_record {}".format(e))
        raise e


@log_args_and_response
def update_canister_dao(update_dict: dict, id: int) -> int:
    try:
        return CanisterMaster.update_canister(update_dict, id)
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("error in update_canister_dao {}".format(e))
        raise


@log_args_and_response
def db_get_canisters_by_rfid_list(rfid_list):
    try:
        return CanisterMaster.get_canister_ids(rfid_list=rfid_list)
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("error in db_get_canisters_by_rfid_list {}".format(e))
        raise


@log_args_and_response
def db_update_canister_master_history_zone_mapping(dict_canister_info, canister_id, canister_history, zone_ids,
                                                   user_id):
    try:
        status = update_canister_dao(update_dict=dict_canister_info, id=canister_id)

        if canister_history:
            BaseModel.db_create_record(canister_history, CanisterHistory)

        if zone_ids is not None:
            CanisterZoneMapping.update_canister_zone_mapping_by_canister_id(zone_ids, user_id, canister_id)

        return status
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("error in db_update_canister_master_history_zone_mapping {}".format(e))
        raise


@log_args
def add_canister_history(data_dict: dict) -> object:
    try:
        return BaseModel.db_create_record(data_dict, CanisterHistory, get_or_create=False)
    except (DataError, IntegrityError, InternalError) as e:
        logger.error("error in add_canister_history {}".format(e))
        raise


@log_args_and_response
def add_canister_status_history(data_dict: dict):
    try:
        return BaseModel.db_create_record(data_dict, CanisterStatusHistory, get_or_create=False)
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in add_canister_status_history {}".format(e))
        raise e


@log_args_and_response
def db_update_canister_master_label_print_time(canister_id):
    try:
        CanisterMaster.update_canister({"label_print_time": get_current_date_time()}, canister_id)
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_update_canister_master_label_print_time {}".format(e))
        raise e


@log_args_and_response
def db_create_canister_tracker_dao(canister_tracker_info):
    try:
        CanisterTracker.db_create_canister_tracker(canister_tracker_info=canister_tracker_info)
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_create_canister_tracker_dao {}".format(e))
        raise e


@log_args_and_response
def db_delete_by_batch_dao(batch_id):
    try:
        return SkippedCanister.db_delete_by_batch(batch_id=batch_id)
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_delete_by_batch_dao {}".format(e))
        raise e


@log_args_and_response
def db_skipped_canisters_insert_many_dao(skipped_canister_list):
    try:
        return SkippedCanister.db_insert_many(skipped_canister_list=skipped_canister_list)
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_skipped_canisters_insert_many_dao {}".format(e))
        raise e


@log_args_and_response
def get_canisters_by_device_system_company(system_id, device_ids, company_id):
    data = []
    distinct_drug_name = []

    try:
        DrugMasterAlias = DrugMaster.alias()
        # using drug master alias to return all unique drugs
        select_fields = [
            CanisterMaster.id,
            LocationMaster.device_id,
            PatientRx.id.alias('rx_id'),
            LocationMaster.location_number,
            ContainerMaster.drawer_name.alias('drawer_number'),
            LocationMaster.display_location,
            DrugMasterAlias.drug_name,
            DrugMasterAlias.ndc,
            DrugMasterAlias.strength,
            DrugMasterAlias.strength_value
        ]

        query = PatientRx.select(*select_fields) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(DrugMasterAlias, on=(DrugMasterAlias.formatted_ndc == DrugMaster.formatted_ndc)
                                      & (DrugMasterAlias.txr == DrugMaster.txr)) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.drug_id == DrugMasterAlias.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id)

        query = query.where(CanisterMaster.active == settings.is_canister_active)
        if device_ids:
            query = query.where(LocationMaster.device_id << device_ids)

            query = query.group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
            for record in query.distinct().dicts():
                drug_name = record["drug_name"] + " " + record["strength_value"] + " " + record[
                    "strength"] + " [" + str(record["canister_number"]) + "]"
                if record["ndc"] not in distinct_drug_name:
                    data.append({
                        "value": record["rx_id"],
                        "text": drug_name,
                        "robot": str(record["device_id"]),
                        "location_number": record["location_number"],
                        "drawer_number": record["drawer_number"]
                    })
                    distinct_drug_name.append(record["ndc"])
        else:
            query = query.where(CanisterMaster.location_id.is_null(False))  # only canister which are in robot
            if company_id:
                query = query.where(CanisterMaster.company_id == company_id)
            if system_id:
                query = query.where(DeviceMaster.system_id == system_id)
            query = query.group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
            for record in query.distinct().dicts():
                drug_name = record["drug_name"] + " " + record["strength_value"] + " " + record[
                    "strength"] + " [" + str(record["display_location"]) + "]"
                if record["ndc"] not in distinct_drug_name:
                    data.append({"value": record["rx_id"], "text": drug_name, "robot": str(record["device_id"]),
                                 "location_number": record["location_number"],
                                 "drawer_number": record["drawer_number"]})
                    distinct_drug_name.append(record["ndc"])
        return data
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in get_canisters_by_device_system_company {}".format(e))
        raise


@log_args_and_response
def db_get_available_locations_dao(dict_robot_info):
    device_id = dict_robot_info.get("device_id", None)
    company_id = dict_robot_info["company_id"]
    # device_type_id: int = dict_robot_info.get("device_type_id", None)
    system_id: int = dict_robot_info.get("system_id", None)
    quadrant: int = dict_robot_info.get("quadrant", None)
    drawer_number: str = dict_robot_info.get("drawer_number", None)
    canister_id: int = dict_robot_info.get("canister_id", None)
    is_mfd: bool = dict_robot_info.get("is_mfd", False)
    both_canister: bool = dict_robot_info.get("both_canister", False)
    location_count: int = dict_robot_info.get("location_count", None)
    paginate: dict = dict_robot_info.get("paginate", None)
    # reserved_locations: list = dict_robot_info.get("reserved_locations", None)
    response_dict: Dict[str, Any] = dict()
    clauses = list()

    try:
        # fetch device_type based on id to differentiate between robot and csr to suggest destination drawers
        device_data = get_device_data_by_device_id_dao(device_id=device_id)
        if not device_data:
            return error(1020, "device_id")
        device_type_id = device_data.device_type_id_id
        logger.info("get_available_locations device_type_id: " + str(device_type_id))

        if device_type_id == settings.DEVICE_TYPES["ROBOT"]:
            logger.info("get_available_locations Robot device_type_id")
            reserved_canisters = ReservedCanister.db_get_reserved_canister(company_id=company_id,
                                                                           skip_canisters=None)
            if len(reserved_canisters):
                clauses.append(((CanisterMaster.id.is_null(True)) | (CanisterMaster.id.not_in(reserved_canisters))))

            clauses.extend([DeviceMaster.device_type_id == device_type_id,
                            DeviceMaster.system_id == system_id])

        elif device_type_id == settings.DEVICE_TYPES["CSR"]:
            logger.info("get_available_locations CSR device_type_id")
            clauses.append(CanisterMaster.id.is_null(True))

        if device_id:
            clauses.append(LocationMaster.device_id == device_id)

        if quadrant:
            clauses.append(LocationMaster.quadrant == quadrant)

        if drawer_number:
            clauses.append(ContainerMaster.drawer_name << drawer_number)

        if both_canister:
            clauses.append(((ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['MFD']] & (MfdCanisterMaster.id.is_null(True)) )| (ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['BIG'],
                                                                   settings.SIZE_OR_TYPE['SMALL']]) & (CanisterMaster.id.is_null(True))))
        else:
            if is_mfd:
                if canister_id:
                    clauses.append(LocationMaster.is_disabled == settings.is_location_active)
                clauses.append(ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['MFD']])
                # todo: if specific trolley needs to be checked then add filter on mfdanalysis trolley location
                clauses.append((MfdCanisterMaster.id.is_null(True) |
                                (mfd_latest_analysis_sub_query.c.status_id.is_null(True) |
                                 (mfd_latest_analysis_sub_query.c.status_id.not_in([constants.MFD_CANISTER_FILLED_STATUS,
                                                                constants.MFD_CANISTER_VERIFIED_STATUS])))))
            else:
                if canister_id:
                    clauses.append(LocationMaster.is_disabled == settings.is_location_active)
                    canister_data = get_canister_details_by_canister_id(canister_id=canister_id)
                    logger.info("get_available_locations canister data {}".format(canister_data))
                    if canister_data['canister_type'] == settings.SIZE_OR_TYPE["BIG"]:
                        clauses.append(ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['BIG']])

                    else:
                        clauses.append(ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['BIG'],
                                                                       settings.SIZE_OR_TYPE['SMALL']])

                else:
                    clauses.append(ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['BIG'],
                                                                   settings.SIZE_OR_TYPE['SMALL']])

        fields_dict = {
            "location_id": LocationMaster.id
        }

        # query to get available empty and unreserved locations
        empty_locations = LocationMaster.select(LocationMaster,
                                                fields_dict['location_id'].alias("location_id"),
                                                CanisterMaster.id.alias('existing_canister_id'),
                                                CanisterMaster.canister_type,
                                                ContainerMaster.ip_address,
                                                ContainerMaster.secondary_ip_address,
                                                ContainerMaster.mac_address,
                                                ContainerMaster.secondary_mac_address,
                                                ContainerMaster.serial_number,
                                                DeviceMaster.name.alias("device_name"),
                                                DeviceMaster.device_type_id,
                                                mfd_latest_analysis_sub_query.c.mfd_canister_id,
                                                mfd_latest_analysis_sub_query.c.status_id.alias('mfd_canister_status'),
                                                ContainerMaster.drawer_name.alias('drawer_number')) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=((CanisterMaster.location_id == LocationMaster.id) &
                                                       (CanisterMaster.company_id == company_id))) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=((MfdCanisterMaster.location_id == LocationMaster.id) &
                                                          (MfdCanisterMaster.company_id == company_id))) \
            .join(mfd_latest_analysis_sub_query, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(*clauses)

        if not is_mfd and location_count:
            empty_locations = empty_locations.order_by(CanisterMaster.id, ContainerMaster.id,
                                                       CanisterMaster.active.desc(),
                                                       LocationMaster.id)
        elif not is_mfd:
            empty_locations = empty_locations.order_by(ContainerMaster.id,
                                                       CanisterMaster.active.desc(),
                                                       LocationMaster.id)

        else:
            empty_locations = empty_locations.order_by(ContainerMaster.id,
                                                       LocationMaster.id)

        if location_count:
            empty_locations = empty_locations.limit(int(location_count))

        results, count, non_paginate_records = get_results(empty_locations.dicts(),
                                                           fields_dict,
                                                           paginate=paginate,
                                                           non_paginate_result_field_list=["location_id"])

        # create the response dict with keeping drawer_number as the key
        for record in results:
            if record["drawer_number"] not in response_dict.keys():
                response_dict[record["drawer_number"]] = []
                response_dict[record["drawer_number"]].append(record)
            else:
                response_dict[record["drawer_number"]].append(record)

        return response_dict
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_get_available_locations_dao {}".format(e))
        raise


@log_args_and_response
def get_canisters_per_drawer_dao(company_id, device_id, drawer_number_list):
    try:
        canister_data = LocationMaster.select(LocationMaster,
                                              ContainerMaster.drawer_name.alias('drawer_number'),
                                              fn.GROUP_CONCAT(Clause(fn.DISTINCT(
                                                  fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                                  SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                                  'zone_id'),
                                              fn.GROUP_CONCAT(Clause(fn.DISTINCT(
                                                  fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                                  SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                                  'zone_name'),
                                              DeviceMaster.system_id,
                                              CanisterMaster,
                                              DrugMaster,
                                              CanisterMaster.id.alias('canister_id')).dicts() \
            .join(CanisterMaster, on=((CanisterMaster.location_id == LocationMaster.id) &
                                      (CanisterMaster.company_id == company_id))) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, DeviceMaster.id == LocationMaster.device_id) \
            .where(ContainerMaster.drawer_name << drawer_number_list,
                   LocationMaster.device_id == device_id).group_by(CanisterZoneMapping.canister_id)

        # drug_data = []
        mfd_canister_data = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id'),
                                                     fn.MAX(MfdAnalysis.id).alias('last_mfd_canister_id'),
                                                     LocationMaster.display_location,
                                                     PatientMaster.concated_patient_name_field().alias('patient_name')
                                                     ).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(MfdAnalysis, on=MfdAnalysis.mfd_canister_id == MfdCanisterMaster.id) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, on=PatientRx.patient_id == PatientMaster.id) \
            .where(MfdCanisterMaster.company_id == company_id,
                   ContainerMaster.drawer_name << drawer_number_list,
                   LocationMaster.device_id == device_id) \
            .group_by(MfdCanisterMaster.id)

        mfd_canister_data_list = []
        for record in mfd_canister_data:
            mfd_canister_data_response: dict = dict()
            mfd_canister_data_response["mfd_canister_id"] = record["mfd_canister_id"]
            mfd_canister_data_response["display_location"] = record["display_location"]
            mfd_canister_data_response["patient_name"] = record["patient_name"]
            mfd_canister_data_list.append(mfd_canister_data_response)

        return canister_data, mfd_canister_data_list
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in get_canisters_per_drawer_dao {}".format(e))
        raise


@log_args_and_response
def get_canister_replenish_info_by_canister(canister_id, company_id, filling_pending_pack_ids,
                                            records_from_date=None, number_of_records=None):
    CodeMasterAlias1 = CodeMaster.alias()
    CodeMasterAlias2 = CodeMaster.alias()
    replenish_data = list()

    try:
        query = CanisterTracker.select(DrugMaster,
                                       CanisterMaster.available_quantity,
                                       fn.IF(CanisterMaster.available_quantity < 0, 0,
                                             CanisterMaster.available_quantity).alias('display_quantity'),
                                       CanisterMaster.company_id,
                                       fn.IF(
                                           CanisterMaster.expiry_date <= date.today() + timedelta(
                                               settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                           constants.EXPIRED_CANISTER,
                                           fn.IF(
                                               CanisterMaster.expiry_date <= date.today() + timedelta(
                                                   settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                               constants.EXPIRES_SOON_CANISTER,
                                               constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                       CanisterTracker.quantity_adjusted,
                                       CanisterTracker.qty_update_type_id,
                                       CodeMasterAlias2.value.alias('quantity_update_type'),
                                       CanisterTracker.original_quantity,
                                       CanisterTracker.lot_number,
                                       CanisterTracker.expiration_date,
                                       CanisterTracker.note, CanisterTracker.id,
                                       CanisterTracker.created_by,
                                       CanisterTracker.created_date,
                                       CanisterTracker.canister_id,
                                       CanisterTracker.drug_id,
                                       CanisterTracker.drug_scan_type_id.alias('drug_scan_type'),
                                       CanisterTracker.replenish_mode_id.alias('replenish_mode'),
                                       CodeMaster.value.alias('drug_scan_value'),
                                       CodeMasterAlias1.value.alias('replenish_mode_value'),
                                       LocationMaster.location_number,
                                       ContainerMaster.drawer_name.alias('drawer_number'),
                                       LocationMaster.display_location,
                                       LocationMaster.is_disabled.alias('is_location_disabled'),
                                       fn.GROUP_CONCAT(Clause(
                                           fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                           SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                                       fn.GROUP_CONCAT(Clause(fn.DISTINCT(
                                           fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                           SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                           'zone_name'),
                                       DeviceMaster.system_id,
                                       DeviceLayoutDetails.id.alias('device_layout_id'),
                                       DeviceMaster.name.alias('device_name'),
                                       DeviceMaster.id.alias('device_id'),
                                       DeviceTypeMaster.device_type_name,
                                       DeviceTypeMaster.id.alias('device_type_id'),
                                       ContainerMaster.ip_address,
                                       ContainerMaster.secondary_ip_address).dicts() \
            .join(DrugMaster, on=CanisterTracker.drug_id == DrugMaster.id) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == CanisterTracker.drug_scan_type_id) \
            .join(CodeMasterAlias1, JOIN_LEFT_OUTER, on=CodeMasterAlias1.id == CanisterTracker.replenish_mode_id) \
            .join(CodeMasterAlias2, JOIN_LEFT_OUTER, on=CodeMasterAlias2.id == CanisterTracker.qty_update_type_id) \
            .join(CanisterMaster, on=CanisterTracker.canister_id == CanisterMaster.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .where(CanisterTracker.canister_id == canister_id,
                   CanisterTracker.lot_number.is_null(False),
                   CanisterTracker.lot_number != '',
                   CanisterMaster.company_id == company_id).group_by(CanisterTracker.id) \
            .order_by(CanisterTracker.created_date.desc())

        if number_of_records:
            query = query.limit(number_of_records)

        if records_from_date:
            query = query.where(fn.DATE(CanisterTracker.created_date) > records_from_date)

        for record in query:
            canister_required_quantity = get_canister_drug_quantity_required_in_batch(
                canister_id_list=[canister_id],
                filling_pending_pack_ids=filling_pending_pack_ids)
            record['batch_required_quantity'] = canister_required_quantity.get(int(canister_id), 0)
            replenish_data.append(record)

        return replenish_data
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in get_canister_replenish_info_by_canister {}".format(e))
        raise


@log_args_and_response
def get_canister_replenish_info_by_lot_number(lot_number, company_id, filling_pending_pack_ids):
    CodeMasterAlias1 = CodeMaster.alias()
    CodeMasterAlias2 = CodeMaster.alias()
    replenish_data = list()
    try:
        query = CanisterTracker.select(DrugMaster,
                                       CanisterMaster.id.alias("canister_master_id"),
                                       CanisterMaster.available_quantity,
                                       fn.IF(CanisterMaster.available_quantity < 0, 0,
                                             CanisterMaster.available_quantity).alias('display_quantity'),
                                       CanisterMaster.company_id,
                                       fn.IF(
                                           CanisterMaster.expiry_date <= date.today() + timedelta(
                                               settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                           constants.EXPIRED_CANISTER,
                                           fn.IF(
                                               CanisterMaster.expiry_date <= date.today() + timedelta(
                                                   settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                               constants.EXPIRES_SOON_CANISTER,
                                               constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                       fn.SUM(CanisterTracker.quantity_adjusted).alias("total_quantity_adjusted"),
                                       CanisterTracker.qty_update_type_id,
                                       CodeMasterAlias2.value.alias('quantity_update_type'),
                                       CanisterTracker.original_quantity,
                                       CanisterTracker.lot_number,
                                       CanisterTracker.expiration_date,
                                       CanisterTracker.note, CanisterTracker.id,
                                       CanisterTracker.created_by,
                                       fn.MAX(CanisterTracker.created_date).alias('last_replenished_date'),
                                       CanisterTracker.canister_id,
                                       CanisterTracker.drug_id,
                                       CanisterTracker.drug_scan_type_id.alias('drug_scan_type'),
                                       CanisterTracker.replenish_mode_id.alias('replenish_mode'),
                                       CodeMaster.value.alias('drug_scan_value'),
                                       CodeMasterAlias1.value.alias('replenish_mode_value'),
                                       DeviceMaster.name.alias('device_name'),
                                       LocationMaster.location_number,
                                       ContainerMaster.drawer_name.alias('drawer_number'),
                                       LocationMaster.display_location,
                                       LocationMaster.is_disabled.alias('is_location_disabled'),
                                       fn.GROUP_CONCAT(Clause(
                                           fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                           SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                                       fn.GROUP_CONCAT(Clause(fn.DISTINCT(
                                           fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                           SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                           'zone_name'),
                                       DeviceMaster.system_id,
                                       DeviceLayoutDetails.id.alias('device_layout_id'),
                                       DeviceMaster.name.alias('device_name'),
                                       DeviceMaster.id.alias('device_id'),
                                       DeviceTypeMaster.id.alias('device_type_id'),
                                       DeviceTypeMaster.device_type_name,
                                       ContainerMaster.ip_address,
                                       ContainerMaster.secondary_ip_address
                                       ).dicts() \
            .join(DrugMaster, on=CanisterTracker.drug_id == DrugMaster.id) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == CanisterTracker.drug_scan_type_id) \
            .join(CodeMasterAlias1, JOIN_LEFT_OUTER, on=CodeMasterAlias1.id == CanisterTracker.replenish_mode_id) \
            .join(CodeMasterAlias2, JOIN_LEFT_OUTER, on=CodeMasterAlias2.id == CanisterTracker.qty_update_type_id) \
            .join(CanisterMaster, on=CanisterTracker.canister_id == CanisterMaster.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .group_by(CanisterTracker.canister_id) \
            .order_by(CanisterTracker.created_date.desc()) \
            .where(CanisterTracker.lot_number == lot_number,
                   CanisterMaster.company_id == company_id).group_by(CanisterTracker.id)
        for record in query:
            canister_required_quantity = get_canister_drug_quantity_required_in_batch(
                canister_id_list=[record['canister_master_id']],
                filling_pending_pack_ids=filling_pending_pack_ids)
            record['batch_required_quantity'] = canister_required_quantity.get(int(record['canister_master_id']), 0)
            replenish_data.append(record)

        return replenish_data
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in get_canister_replenish_info_by_lot_number {}".format(e))
        raise


@log_args_and_response
def get_canister_details_by_device_dao(device_id, is_active, system_id):
    canister_data = list()
    try:
        for record in CanisterMaster.select(
                CanisterMaster.drug_id,
                CanisterMaster.rfid,
                CanisterMaster.available_quantity,
                fn.IF(CanisterMaster.available_quantity < 0, 0, CanisterMaster.available_quantity).alias(
                    'display_quantity'),
                LocationMaster.location_number,
                fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                       SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                       SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_name'),
                DeviceMaster.system_id,
                CanisterMaster.active,
                CanisterMaster.reorder_quantity,
                CanisterMaster.barcode,
                CanisterMaster.created_date,
                CanisterMaster.modified_date
        ) \
                .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(DeviceTypeMaster, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
                .dicts().where(
            LocationMaster.device_id == device_id,
            CanisterMaster.active == is_active,
            DeviceMaster.system_id == system_id
        ).group_by(CanisterMaster.id):
            canister_data.append(record)

        return canister_data
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in get_canister_details_by_device_dao {}".format(e))
        raise


@log_args_and_response
def db_canister_master_remove_dao(modified_by, modified_date, canister_id, company_id):
    try:
        status = CanisterMaster.update(
            location_id=None,
            modified_by=modified_by,
            modified_date=modified_date
        ).where(
            CanisterMaster.id == canister_id,
            CanisterMaster.company_id == company_id
        ).execute()

        canister = CanisterMaster.get(id=canister_id)
        # get canister data for drug id

        BaseModel.db_create_record({
            "canister_id": canister_id,
            "current_location_id": None,
            "previous_location_id": canister.location_id,
            "created_by": modified_by,
            "modified_by": modified_by,
        }, CanisterHistory, get_or_create=False)

        return status
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_canister_master_remove_dao {}".format(e))
        raise


@log_args
def add_canister_status_history_comment(comment_data: dict) -> object:
    try:
        # add data in CanisterStatusHistoryComment
        comment_record = CanisterStatusHistoryComment.insert_canister_status_history_comment_data(
            data_dict=comment_data)
        comment_record_id = comment_record.id
        logger.info("Data added in canister status history comment {}".format(comment_record_id))
        return comment_record_id

    except (DataError, IntegrityError, InternalError) as e:
        logger.error("Error in add_canister_status_history_comment {}".format(e))
        raise


@log_args_and_response
def db_get_canister_drug_ids(company_id):
    try:
        return CanisterMaster.db_get_drug_ids(company_id=company_id)
    except (DoesNotExist, InternalError, IntegrityError, Exception) as ex:
        logger.error("error in db_get_canister_drug_ids {}".format(ex))
        raise ex


@log_args_and_response
def get_canister_status_history_data(canister_list: list, status: int) -> dict:
    """

    @param canister_list:
    @param status:
    @return:
    """
    canister_status_dict = dict()
    try:
        query = CanisterStatusHistory.select(CanisterStatusHistory.canister_id,
                                             CanisterStatusHistory.action,
                                             CanisterStatusHistoryComment.comment).dicts() \
            .join(CanisterStatusHistoryComment, JOIN_LEFT_OUTER,
                  on=CanisterStatusHistoryComment.canister_status_history_id == CanisterStatusHistory.id) \
            .where(CanisterStatusHistory.canister_id << canister_list,
                   CanisterStatusHistory.action == status) \
            .order_by(CanisterStatusHistory.id.desc())

        for record in query:
            if record['canister_id'] not in canister_status_dict.keys():
                canister_status_dict['canister_id'] = record

        return canister_status_dict

    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_canister_status_history_data {}".format(e))
        raise


@log_args_and_response
def get_canister_info_by_drawer_id(drawer_type_id: int, drawer_id: int, company_id: int, device_id: int) -> list:
    """
        @param drawer_type_id:
        @param drawer_id: integer
        @param device_id: integer
        @param company_id: integer
        @desc: To get data of canisters using drawer_id, company_id and device_id from tables
        @return: list
    """
    logger.info("In function get_canister_info_by_drawer_id")
    data = []
    try:
        if drawer_type_id == constants.MFD_DRAWER_TYPE_ID:
            mfd_canister_data = LocationMaster.select(ContainerMaster.device_id,
                                                      ContainerMaster.id.alias("container_id"),
                                                      LocationMaster.id.alias("location_id"),
                                                      LocationMaster.display_location,
                                                      LocationMaster.quadrant,
                                                      MfdCanisterMaster.id.alias("canister_id"),
                                                      MfdCanisterMaster.rfid).dicts() \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
                .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
                .where(ContainerMaster.id == drawer_id,
                       ContainerMaster.device_id == device_id,
                       DeviceMaster.company_id == company_id)
            for record in mfd_canister_data:
                record["is_mfd_canister"] = True
                data.append(record)
            return data

        else:
            canister_data = LocationMaster.select(ContainerMaster.device_id,
                                                  ContainerMaster.id.alias("container_id"),
                                                  LocationMaster.id.alias("location_id"),
                                                  LocationMaster.display_location,
                                                  LocationMaster.quadrant,
                                                  CanisterMaster.id.alias("canister_id"),
                                                  CanisterMaster.rfid).dicts() \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .where(ContainerMaster.id == drawer_id,
                       ContainerMaster.device_id == device_id,
                       DeviceMaster.company_id == company_id)
            for record in canister_data:
                record["is_mfd_canister"] = False
                data.append(record)
            return data
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("error in get_canister_info_by_drawer_id {}".format(e))
        raise e


@log_args_and_response
def db_get_current_canister_location(canister):
    """

    @param canister:
    @return:
    """
    try:
        query = CanisterMaster.select(LocationMaster.device_id, LocationMaster.container_id,
                                      LocationMaster.id, CanisterMaster.canister_type,
                                      CanisterMaster.company_id).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .where(CanisterMaster.id == canister)

        for record in query:
            return record

    except DoesNotExist as e:
        logger.error("error in db_get_current_canister_location {}".format(e))
        return None
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_current_canister_location {}".format(e))
        raise


@log_args_and_response
def db_get_current_canister_based_on_location(location_id):
    """

    @param location_id:
    @return:
    """
    try:
        query = CanisterMaster.select(LocationMaster.device_id, LocationMaster.container_id,
                                      LocationMaster.id, CanisterMaster.canister_type,
                                      CanisterMaster.company_id,
                                      CanisterMaster.id.alias('canister_id')).dicts() \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .where(LocationMaster.id == location_id)

        for record in query:
            return record

    except DoesNotExist as e:
        logger.error("error in db_get_current_canister_based_on_location {}".format(e))
        return None
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_current_canister_based_on_location {}".format(e))
        raise


@log_args_and_response
def assign_cart_location_to_canister(canister, trolley_location_id):
    """
    Function to assign cart location to canister when it is removed from robot or CSR
    @param canister:
    @param trolley_location_id:
    @return:
    """
    try:
        logger.info("In assign_cart_location_to_canister")
        with db.transaction():
            canister_update_status1 = CanisterMaster.update_canister_location_id(canister_id=canister,
                                                                                 location_id=trolley_location_id)
        return canister_update_status1

    except(InternalError, IntegrityError, DataError) as e:
        logger.error("error in assign_cart_location_to_canister {}".format(e))
        raise e


@log_args_and_response
def db_get_location_ids_by_device_and_location_number(device_id, location_number_list):
    try:
        return LocationMaster.get_location_ids(device_id=device_id, location_number_list=location_number_list)
    except(InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_get_location_ids_by_device_and_location_number {}".format(e))
        raise e


@log_args_and_response
def db_update_canister_location_shelf_dao(user_id, location_id_list):
    try:
        return CanisterMaster.db_update_canister_location_shelf(user_id, location_id_list)
    except(InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_update_canister_location_shelf_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_canister_by_location_updates_dao(timestamp, device_id, v2_width, v2_min, v2_include_strength, system_id):
    removed_canisters = list()  # maintain list of canister number where canister was removed
    results = list()

    try:
        select_fields = [
            CanisterMaster.id.alias('canister_id'),
            CanisterMaster.rfid,
            CanisterMaster.available_quantity,
            fn.IF(CanisterMaster.available_quantity < 0, 0, CanisterMaster.available_quantity).alias(
                'display_quantity'),
            LocationMaster.location_number,
            LocationMaster.is_disabled.alias('is_location_disabled'),
            LocationMaster.display_location,
            ContainerMaster.drawer_name.alias('drawer_number'),
            fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                   SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
            fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                   SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_name'),
            DeviceMaster.system_id,
            CanisterMaster.drug_id,
            DrugMaster.drug_name,
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.ndc,
            DrugMaster.formatted_ndc,
            CanisterMaster.reorder_quantity,
            CanisterMaster.barcode
        ]

        LocationMasterAlias = LocationMaster.alias()
        if timestamp and device_id:
            # return data where canister locations were updated after given `timestamp`
            canister_location_set = set()
            timestamp = timestamp[:19]  # consider only date and time
            query = CanisterHistory.select(CanisterHistory,
                                           LocationMaster.device_id.alias('current_device_id'),
                                           LocationMasterAlias.device_id.alias('previous_device_id'),
                                           LocationMasterAlias.location_number.alias('previous_location_number'),
                                           LocationMaster.location_number.alias('current_location_number')) \
                .join(LocationMaster, JOIN_LEFT_OUTER, CanisterHistory.current_location_id == LocationMaster.id) \
                .join(LocationMasterAlias, JOIN_LEFT_OUTER,
                      CanisterHistory.previous_location_id == LocationMasterAlias.id) \
                .where(
                CanisterHistory.created_date >= timestamp,
                ((LocationMasterAlias.device_id == device_id) |
                 (LocationMaster.device_id == device_id))
            )
            for record in query.dicts():
                if record["current_device_id"] == device_id:
                    canister_location_set.add(record["current_location_number"])
                if record["previous_device_id"] == device_id:
                    canister_location_set.add(record["previous_location_number"])
                    removed_canisters.append(record["previous_location_number"])

            canister_location_set.discard(0)  # remove location number 0 which is not robot location
            results_dict = {item: {"rfid": None, "location_number": item} for item in removed_canisters}
            if canister_location_set:  # if change in location
                query = CanisterMaster.select(*select_fields) \
                    .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                    .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
                    .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                    .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
                    .join(CanisterZoneMapping, JOIN_LEFT_OUTER,
                          CanisterZoneMapping.canister_id == CanisterMaster.id) \
                    .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
                    .where(LocationMaster.location_number << list(canister_location_set),
                           LocationMaster.device_id == device_id) \
                    .group_by(CanisterMaster.id)

                for record in query.dicts():
                    record["short_drug_name_v2"] = fn_shorten_drugname_v2(
                        record["drug_name"],
                        record["strength"],
                        record["strength_value"],
                        ai_width=v2_width,
                        ai_min=v2_min,
                        include_strength=v2_include_strength
                    )
                    results_dict[record["location_number"]] = record
                results = list(results_dict.values())
        elif device_id:
            # get all canisters data for given robot
            query = CanisterMaster.select(*select_fields) \
                .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
                .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
                .where(DeviceMaster.system_id == system_id,
                       LocationMaster.device_id == device_id) \
                .group_by(CanisterMaster.id)
            for record in query.dicts():
                record["short_drug_name_v2"] = fn_shorten_drugname_v2(
                    record["drug_name"],
                    record["strength"],
                    record["strength_value"],
                    ai_width=v2_width,
                    ai_min=v2_min,
                    include_strength=v2_include_strength
                )
                results.append(record)
        return results

    except(InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_get_canister_by_location_updates_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_canister_remove_list(new_rfids, device_id, log_enabled, disabled_locations, user_id, rfid_location_new):
    location_rfid = dict()
    location_canister = dict()
    rfid_canisters = dict()
    canister_dict = dict()
    update_dict = dict()
    disabled_locations_overlap = list()
    remove_list = list()

    try:
        query = CanisterMaster.select(LocationMaster.device_id,
                                      LocationMaster.location_number,
                                      CanisterMaster.rfid,
                                      CanisterMaster.id.alias('canister_id'),
                                      CanisterMaster.drug_id
                                      ) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id)

        if new_rfids:
            query = query.where((CanisterMaster.rfid << list(new_rfids)) | (LocationMaster.device_id == device_id))
        else:
            query = query.where(LocationMaster.device_id == device_id)

        for record in query.dicts():
            if record['device_id'] == device_id:
                location_rfid[record["location_number"]] = record["rfid"]
                location_canister[record["location_number"]] = record
            if record["rfid"]:
                rfid_canisters[record["rfid"]] = record
                if record["rfid"] in new_rfids:
                    canister_dict[record["rfid"]] = record["canister_id"]

        if log_enabled:
            logger.info('location_canister: {}'.format(location_canister))
            logger.info('rfid_canisters: {}'.format(rfid_canisters))
        for location_number, rfid in rfid_location_new.items():
            if rfid:  # rfid detected for location
                if location_number not in disabled_locations:
                    update_dict[rfid] = {
                        "location_number": location_number,
                        "device_id": device_id,
                        "modified_date": get_current_date_time(),
                        "modified_by": user_id
                    }
                else:
                    # canister location is disabled, so keeping canister outside robot
                    disabled_locations_overlap.append(
                        [location_number, device_id]
                    )
                    canister_dict.pop(rfid, None)
                    # Commented the below, to update the location in the canister master even if the location
                    # is disabled.
                    # update_dict[rfid]["location_number"] = 0
                    # update_dict[rfid]["device_id"] = None
                if location_number in location_rfid and location_rfid[location_number] != rfid:
                    remove_list.append(location_number)
                    # canister already present and new rfid detected
            else:  # rfid not detected for location so remove canister from robot
                remove_list.append(location_number)

        return location_rfid, location_canister, rfid_canisters, canister_dict, update_dict, \
               disabled_locations_overlap, remove_list

    except(InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_get_canister_remove_list {}".format(e))
        raise e


@log_args_and_response
def db_canister_history_create_multi_record_dao(canister_history_list):
    try:
        CanisterHistory.db_canister_history_create_multi_record(canister_history_list)
    except(InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_canister_history_create_multi_record_dao {}".format(e))
        raise e


@log_args_and_response
def get_canister_details_by_id_dao(canister_id: int, company_id: int) -> dict:
    """
    Method to get canister details based on canister_id
    @param canister_id:
    @param company_id:
    @return:
    """
    try:
        return (CanisterMaster.select(CanisterMaster,
                                      DrugMaster.ndc)
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id).dicts().where(CanisterMaster.id == canister_id,
                                                     CanisterMaster.company_id == company_id).get())

    except DoesNotExist as e:
        logger.error("Invalid canister_id - {} or company_id - {}".format(canister_id, company_id))
        raise e

    except InternalError as e:
        logger.error("error in get_canister_details_by_id_dao {}".format(e))
        raise e


@log_args_and_response
def get_recently_replenished_drug_info(canister_id: int, record_after_id: int = None, record_before_id: int = None,
                                       exception_ids: int = None) -> list:
    """
    Method to get recently replenished drug info
    @param exception_ids:
    @param record_before_id:
    @param record_after_id:
    @param canister_id:
    @return:
    """
    try:
        logger.info("In get_recently_replenished_drug_info")
        query = CanisterTracker.select().dicts().where(CanisterTracker.canister_id == canister_id,
                                                       CanisterTracker.qty_update_type_id ==
                                                       constants.CANISTER_QUANTITY_UPDATE_TYPE_REPLENISHMENT) \
            .order_by(SQL('Field(replenish_mode_id_id, {},{},{})'.format(
                constants.MANUAL_CODE,
                constants.REPLENISHED_WITH_ENTIRE_DRUG_BOTTLE,
                constants.REFILL_DEVICE)))
        if record_after_id:
            query = query.where(CanisterTracker.id > record_after_id)
        if record_before_id:
            query = query.where(CanisterTracker.id < record_before_id)
        if exception_ids:
            query = query.where(CanisterTracker.id.not_in(exception_ids))

        return list(query)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_recently_replenished_drug_info {}".format(e))
        raise e


@log_args_and_response
def get_latest_adjusted_canister_record_by_canister_id(canister_id: int, exception_ids: list = None) -> dict:
    """
    Method to get the latest adjuster canister record based on canister_id
    @param exception_ids:
    @param canister_id:
    @return:
    """

    try:
        logger.info("In get_latest_adjusted_canister_record_by_canister_id")
        query = CanisterTracker.select().dicts().where(CanisterTracker.canister_id == canister_id,
                                                       CanisterTracker.qty_update_type_id ==
                                                       constants.CANISTER_QUANTITY_UPDATE_TYPE_ADJUSTMENT) \
            .order_by(CanisterTracker.id.desc())

        if exception_ids:
            query = query.where(CanisterTracker.id.not_in(exception_ids))

        return query.get()

    except DoesNotExist as e:
        logger.error("error in get_latest_adjusted_canister_record_by_canister_id {}".format(e))
        logger.error("No record of adjustment found in canister tracker for canister_id - " + str(canister_id))
        return {}
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_latest_adjusted_canister_record_by_canister_id {}".format(e))
        raise e


@log_args
def get_empty_location_by_quadrant(device_id: int, quadrant: int, company_id: int, drawer_type: list,
                                   exclude_location: list) -> dict:
    """
    :param device_id:
    :param quadrant:
    :param company_id:
    :param exclude_location:
    :param drawer_type:
    :return:
    """
    logger.info("In function get_empty_location_by_quadrant")
    data = {}
    try:
        query = LocationMaster.select(ContainerMaster.device_id,
                                      ContainerMaster.id.alias("container_id"),
                                      LocationMaster.id.alias("location_id"),
                                      LocationMaster.display_location,
                                      LocationMaster.quadrant,
                                      ContainerMaster.drawer_name,
                                      ContainerMaster.shelf,
                                      LocationMaster.display_location,
                                      ContainerMaster.serial_number.alias("container_serial_number"),
                                      ContainerMaster.ip_address,
                                      ContainerMaster.secondary_ip_address,
                                      DeviceMaster.device_type_id,
                                      DeviceMaster.serial_number.alias("device_serial_number")
                                      ).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .where(LocationMaster.quadrant == quadrant,
                   ContainerMaster.device_id == device_id,
                   LocationMaster.is_disabled == False,
                   CanisterMaster.id.is_null(True),
                   DeviceMaster.company_id == company_id)
        if exclude_location:
            query = query.where(LocationMaster.id.not_in(exclude_location))
        if drawer_type:
            query = query.where(ContainerMaster.drawer_type << drawer_type)

        query = query.limit(1)
        for record in query:
            data = {
                'location_id': record['location_id'],
                'display_location': record['display_location'],
                "shelf": record['shelf'],
                "ip_address": record['ip_address'],
                "secondary_ip_address": record["secondary_ip_address"],
                "device_type_id": record['device_type_id'],
                "device_serial_number": record["device_serial_number"],
                "container_serial_number": record["container_serial_number"]
            }
        return data
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in get_empty_location_by_quadrant {}".format(e))
        raise e


@log_args_and_response
def check_canisters_present_in_cart(system_id: int) -> list:
    """
    Function to check if canisters are present in canister transfer cart or Canister Cart w/ Elevator
    @param system_id: int
    @return: list
    """
    logger.info("Inside check_canisters_present_in_cart")
    canister_list = list()
    try:
        device_types = [settings.DEVICE_TYPES['Canister Transfer Cart'],
                        settings.DEVICE_TYPES['Canister Cart w/ Elevator']]

        query = CanisterMaster.select(CanisterMaster.id).dicts() \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(DeviceMaster.system_id == system_id,
                   DeviceMaster.device_type_id << device_types)

        for record in query:
            canister_list.append(record['id'])

        logger.info("check_canisters_present_in_cart response {}".format(canister_list))
        return canister_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in check_canisters_present_in_cart {}".format(e))
        raise
    except DoesNotExist as e:
        logger.error("Error in check_canisters_present_in_cart {}".format(e))
        return canister_list


@log_args_and_response
def get_canister_by_rfid(rfid: str) -> dict:
    """
    Returns canister data(dict) by RFID, None if no canister found
    :param rfid: RFID of canister
    :return: dict
    """
    canister = dict()
    try:
        canister = CanisterMaster.select(
            DrugMaster,
            DrugMaster.id.alias('drug_id'),
            LocationMaster.device_id,
            CanisterMaster.company_id,
            LocationMaster.location_number,
            LocationMaster.display_location,
            LocationMaster.is_disabled.alias('is_location_disabled'),
            fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                   SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
            fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                   SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_name'),
            DeviceMaster.system_id,
            CanisterMaster.rfid,
            CanisterMaster.available_quantity,
            fn.IF(CanisterMaster.available_quantity < 0, 0, CanisterMaster.available_quantity).alias(
                'display_quantity'),
            CanisterMaster.drug_id,
            CanisterMaster.canister_type,
            CanisterMaster.reorder_quantity,
            CanisterMaster.id.alias('canister_id'),
            CanisterMaster.active,
        ).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .where(CanisterMaster.rfid == rfid).group_by(CanisterMaster.id) \
            .get()
        return canister
    except(IntegrityError, IntegrityError) as e:
        logger.error("error in get_canister_by_rfid {}".format(e))
    except DoesNotExist as e:
        logger.info('No Canister found for RFID {}, exc: {}'
                     .format(rfid, e))
        return canister


@log_args_and_response
def update_canister_location(canister_data):
    canister_id = canister_data['canister_id']
    location_id = canister_data['location_id']
    company_id = canister_data['company_id']
    zone_ids = list(map(lambda x: int(x), canister_data["zone_id"].split(','))) if (
            "zone_id" in canister_data.keys() and canister_data["zone_id"] is not None) else None
    user_id = canister_data['user_id']
    try:
        response = CanisterMaster.update_canister_location(canister_id=canister_id, location_id=location_id,
                                                           company_id=company_id)
        if zone_ids is not None and user_id is not None:
            CanisterZoneMapping.update_canister_zone_mapping_by_canister_id(zone_ids, user_id, canister_id)
        return create_response(response)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_canister_location {}".format(e))
        return error(1020)


@log_args_and_response
def get_canister_data_by_txr(company_id: int, txr: Optional[str] = None,
                             txr_list: Optional[List[str]] = None) -> Dict[str, Set[Any]]:
    """
    returns canister data for given txr and company
    """
    fndc_txr_canister_data = defaultdict(set)
    clauses: List[Any] = [CanisterMaster.company_id == company_id,
                          CanisterMaster.active == settings.is_canister_active]

    if txr:
        clauses.extend([DrugMaster.txr == txr,
                        DrugMaster.brand_flag == settings.GENERIC_FLAG])
    elif txr_list:
        clauses.append(DrugMaster.txr.in_(txr_list))
    else:
        return fndc_txr_canister_data

    try:
        query = CanisterMaster.select(
            CanisterMaster.id.alias('canister_id'),
            DrugMaster.drug_name,
            DrugMaster.ndc,
            DrugMaster.txr,
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.imprint,
            DrugMaster.image_name,
            DrugMaster.shape,
            DrugMaster.color,
            DrugMaster.formatted_ndc,
            DrugMaster.manufacturer,
            DrugMaster.brand_flag,
            DrugMaster.drug_form,
            DrugMaster.concated_fndc_txr_field(sep='##').alias('fndc_txr')
        ).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(*clauses)

        for record in query:
            if txr:
                dict_key = '{}##{}'.format(record['formatted_ndc'], record['txr'])
                fndc_txr_canister_data[dict_key].add(record['canister_id'])
            elif txr_list:
                fndc_txr_canister_data[record['txr']].add(record['formatted_ndc'])

        return fndc_txr_canister_data
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_canister_data_by_txr {}".format(e))
        raise


@log_args_and_response
def epbm_get_available_alternate_canister(txr: str, company_id: int) -> list:
    """
    Returns list of drug data for which canisters are present in given company
    :param txr:
    :param company_id:
    :return: dict
    """
    canister_data = dict()
    canister_fndc_txr = get_canister_data_by_txr(txr=txr, company_id=company_id)
    fndc_txr_list = list(canister_fndc_txr)

    try:
        if fndc_txr_list:
            query = DrugMaster.select(
                DrugMaster.drug_name,
                DrugMaster.ndc,
                DrugMaster.txr,
                DrugMaster.formatted_ndc,
                DrugMaster.concated_fndc_txr_field(sep='##').alias('fndc_txr')
            ).dicts() \
                .where(DrugMaster.concated_fndc_txr_field(sep='##') << fndc_txr_list)

            for record in query:
                record.update({'canister_count': len(canister_fndc_txr[record['fndc_txr']])})
                canister_data[record['ndc']] = record
        return list(canister_data.values())
    except (InternalError, IntegrityError) as e:
        logger.error("error in epbm_get_available_alternate_canister {}".format(e))
        raise


@log_args_and_response
def delete_canister_dao(dict_canister_info: dict):
    """
    deactivate the canister with the given canister id.
        It sets the location of the canister to -1(deleted)
    @param dict_canister_info:
    @return:
    """
    canister_id = dict_canister_info["canister_id"]
    # company_id = int(dict_canister_info["company_id"])
    user_id = dict_canister_info["user_id"]
    comment = dict_canister_info["comment"]
    update_location = dict_canister_info.get("update_location", True)

    device_id = dict_canister_info.get("device_id", None)
    # location_id = None
    if device_id:
        # location_id = LocationMaster.get_location_id(device_id,  dict_canister_info["location_number"])
        location_id = LocationMaster.get_location_id_by_display_location(device_id=device_id,
                                                                         display_location=dict_canister_info[
                                                                             "display_location"])
        logger.info("In delete_canister_dao: location id : {}".format(location_id))
    try:
        with db.transaction():
            status = CanisterMaster.delete_canister(canister_id, user_id, update_location)

            # populate data in canister history tables
            status_data_dict = {
                "canister_id": canister_id,
                "action": constants.CODE_MASTER_CANISTER_DEACTIVATE,
                "created_by": user_id,
                "created_date": get_current_date_time()
            }
            canister_status_history = add_canister_status_history(data_dict=status_data_dict)
            logger.info("Data added in canister status history {}".format(canister_status_history.id))

            comment_data = {"comment": comment, "canister_status_history_id": canister_status_history.id}
            canister_status_history_comment = add_canister_status_history_comment(comment_data=comment_data)
            logger.info("Data added in canister_status_history_comment: {}".format(canister_status_history_comment))

            return status

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in delete_canister_dao {}".format(e))
        raise


@log_args_and_response
def get_canister_id_canister_type_available_quantity_approx_drug_volume(company_id: int) -> list:
    """
    Return canister_id, canister_type, available_quantity
    @param company_id:
    @return list: list of canister_id, canister_type, available_quantity
    """
    try:
        canister_id_canister_type_available_quantity = list()

        query = CanisterMaster.select(CanisterMaster.id.alias("canister_id"), CanisterMaster.canister_type,
                                      CodeMaster.value.alias('canister_type_name'),
                                      CanisterMaster.available_quantity, DrugDimension.approx_volume).dicts() \
            .join(CodeMaster, on=CodeMaster.id == CanisterMaster.canister_type) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .where(CanisterMaster.company_id == company_id)

        for record in query:
            canister_id_canister_type_available_quantity.append(record)

        return canister_id_canister_type_available_quantity
    except InternalError as e:
        logger.error("error in get_canister_id_canister_type_available_quantity_approx_drug_volume {}".format(e))
        raise e


@log_args_and_response
def get_serial_number_from_canister_id(canister_id: int):
    """
    returns big canister stick serial number, small canister stick serial number and drum serial number from canister_id
    :param canister_id:
    :return:
    """
    big_stick_serial_number = None
    small_stick_serial_number = None
    drum_serial_number = None
    try:
        query = CanisterMaster.select(
            CanisterMaster.id.alias('canister_id'),
            CanisterMaster.canister_stick_id,
            BigCanisterStick.serial_number.alias("big_stick_serial_number"),
            SmallCanisterStick.length.alias("small_stick_serial_number"),
            CanisterDrum.serial_number.alias("drum_serial_number")
        ).dicts() \
            .join(CanisterStick, on=CanisterStick.id == CanisterMaster.canister_stick_id) \
            .join(BigCanisterStick, JOIN_LEFT_OUTER, on=BigCanisterStick.id == CanisterStick.big_canister_stick_id) \
            .join(SmallCanisterStick, JOIN_LEFT_OUTER,
                  on=SmallCanisterStick.id == CanisterStick.small_canister_stick_id) \
            .join(CanisterDrum, JOIN_LEFT_OUTER, on=CanisterDrum.id == CanisterStick.canister_drum_id) \
            .where(CanisterMaster.id == canister_id)
        for record in query:
            big_stick_serial_number = record["big_stick_serial_number"]
            small_stick_serial_number = record["small_stick_serial_number"]
            drum_serial_number = record["drum_serial_number"]
        return big_stick_serial_number, small_stick_serial_number, drum_serial_number
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_serial_number_from_canister_id {}".format(e))
        raise


@log_args_and_response
def update_canister_testing_status(new_canister_id: int, old_canister_id: int):
    """
    update new canister id in canister testing status table
    :return: bool
    """
    try:
        status = CanisterTestingStatus.db_update_canister_id(new_canister_id=new_canister_id,
                                                             old_canister_id=old_canister_id)

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_canister_testing_status {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in update_canister_testing_status {}".format(e))
        raise e


@log_args_and_response
def get_replenish_info_by_drug_usage_status(canister_ids: List[int], status: List[int]) -> dict:
    """
    Method to get replenish details for given canister_ids filtered by given usage_consideration_status
    @param canister_ids: canister_ids for which replenish info required
    @param status: usage_consideration_status by which filtration needed

    @return:
    """
    try:
        logger.info("Inside get_replenish_info_by_drug_usage_status.")

        replenish_data: dict = dict()
        replenish_info = CanisterTracker.select().dicts().where(CanisterTracker.canister_id << canister_ids,
                                                                CanisterTracker.usage_consideration << status) \
            .order_by(CanisterTracker.id)

        for info in replenish_info:
            canister_id = info["canister_id"]
            if canister_id not in replenish_data:
                replenish_data[canister_id] = []
            replenish_data[canister_id].append(info)

        return replenish_data

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_replenish_info_by_drug_usage_status {}".format(e))
        raise

@log_args_and_response
def get_replenish_info_by_drug_usage_status_in_reverse(canister_ids: List[int], status: List[int]) -> dict:
    try:
        logger.info("Inside get_replenish_info_by_drug_usage_status_in_reverse.")

        replenish_data: dict = dict()
        replenish_info = CanisterTracker.select().dicts().where(CanisterTracker.canister_id << canister_ids,
                                                                CanisterTracker.usage_consideration << status) \
            .order_by(CanisterTracker.id.desc())

        for info in replenish_info:
            if info["id"] not in replenish_data:
                replenish_data[info["id"]] = []
            replenish_data[info["id"]].append(info)
        if not len(replenish_info):
            replenish_info = CanisterTracker.select().dicts().where(CanisterTracker.canister_id << canister_ids,
                                                                    CanisterTracker.usage_consideration << status) \
                .order_by(CanisterTracker.id.desc())
            for info in replenish_info:
                if info["id"] not in replenish_data:
                    replenish_data[info["id"]] = []
                replenish_data[info["id"]].append(info)

        return replenish_data

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_replenish_info_by_drug_usage_status_in_reverse {}".format(e))
        raise


@log_args_and_response
def update_drug_usage_status_in_canister_tracker(replenish_ids: List[int], status: int) -> int:
    """
    Method to update usage_consideration status in CanisterTracker
    @param replenish_ids: primary ids of CanisterTracker for which we want to update usage_consideration
    @param status: usage_consideration to update
    @return:
    """
    try:
        return CanisterTracker.update_usage_consideration_status(replenish_ids, status)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in update_drug_usage_status_in_canister_tracker {}".format(e))
        raise


@log_args_and_response
def update_canister_expiry_date(tracker_ids):
    try:
        logger.info(f"In update_canister_expiry_date")
        update_dict = dict()
        status = None
        query = CanisterTracker.select(CanisterTracker.canister_id,
                                       CanisterTracker.expiration_date).dicts() \
                .where(CanisterTracker.id.in_(tracker_ids))

        for data in query:
            if data["expiration_date"]:
                expiry = data["expiration_date"].split("-")
                expiry_month = int(expiry[0])
                expiry_year = int(expiry[1])
                expiry_date = last_day_of_month(date(expiry_year, expiry_month, 1))

                update_dict[data["canister_id"]] = (data["canister_id"], expiry_date)
        if update_dict:
            logger.info(f"In update_canister_expiry_dict, update_dict:{update_dict}")
            canister_expiry_date_case = case(CanisterMaster.id, list(update_dict.values()))
            canister_ids = list(update_dict.keys())
            status = CanisterMaster.update(expiry_date=canister_expiry_date_case).where(CanisterMaster.id.in_(canister_ids)).execute()
            print(f"In update_canister_expiry_date. status: {status}")

        return status
    except Exception as e:
        logger.error(f"Error in update_canister_expiry_date, e: {e}")
        raise e


@log_args_and_response
def db_get_robot_canister_with_locations(device_id):
    # device id in form of list
    try:
        canister_location_info_dict = {}
        reserved_location = set()
        query = CanisterMaster.select(
            CanisterMaster.id,
            LocationMaster.device_id,
            LocationMaster.id.alias('location_id'),
            LocationMaster.quadrant,
            LocationMaster.display_location,
            CanisterMaster.rfid,
            LocationMaster.location_number,
            DeviceMaster.name.alias('device_name')
        ).join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(CanisterMaster.location_id.is_null(False), CanisterMaster.active == settings.is_canister_active,
                   LocationMaster.device_id << device_id)

        for record in query.dicts():
            if record['id'] not in canister_location_info_dict:
                canister_location_info_dict[record['id']] = ()
            canister_location_info_dict[record['id']] = (
                record['device_id'], record['quadrant'], record['display_location'], record['rfid'],
                record['location_number'], record['device_name'])
            reserved_location.add(record['location_id'])
        return canister_location_info_dict, reserved_location
    except (InternalError, IntegrityError) as e:
        logger.error("error in db_get_robot_canister_with_locations {}".format(e))
        raise


@log_args_and_response
def db_get_robot_canister_with_ids(canister_ids, canister_location_info_dict, reserved_location):
    # device id in form of list
    try:
        query = CanisterMaster.select(
            CanisterMaster.id,
            LocationMaster.device_id,
            LocationMaster.id.alias('location_id'),
            LocationMaster.quadrant,
            LocationMaster.display_location,
            CanisterMaster.rfid,
            LocationMaster.location_number,
            DeviceMaster.name.alias('device_name')
        ).join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(CanisterMaster.id << canister_ids,
                   CanisterMaster.active == settings.is_canister_active,
                   )

        for record in query.dicts():
            if record['id'] not in canister_location_info_dict:
                canister_location_info_dict[record['id']] = ()
            canister_location_info_dict[record['id']] = (
                record['device_id'], record['quadrant'], record['display_location'], record['rfid'],
                record['location_number'], record['device_name'])
            reserved_location.add(record['location_id'])
        return canister_location_info_dict, reserved_location
    except (InternalError, IntegrityError) as e:
        logger.error("error in db_get_robot_canister_with_ids {}".format(e))
        raise


@log_args_and_response
def update_canister_category_dao(update_canister_dict):
    """
    Function to update canister category in canister master
    `i.e` canister type/size and canister usage
    @param update_canister_dict:
    @return:
    """
    try:
        canister_type_dict = update_canister_dict["canister_type"]
        drug_usage_dict = update_canister_dict["canister_size"]
        for type, canister_list in canister_type_dict.items():
            status = CanisterMaster.update(canister_type=settings.CANISTER_TYPE["SMALL"]) \
                .where(CanisterMaster.id << canister_list).execute()
            logger.info(status)

        for usage, canister_list in drug_usage_dict.items():
            if len(canister_list):
                drug_list = get_drug_data_from_canister_list(canister_list)

                status = UniqueDrug.update(drug_usage=usage) \
                    .where(UniqueDrug.drug_id << drug_list).execute()
                logger.info(status)

        return True

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in update_canister_category_dao {}".format(e))
        raise
    except Exception as e:
        logger.error("error in update_canister_category_dao {}".format(e))


@log_args_and_response
def get_drug_data_from_canister_list(canister_list):
    try:
        drug_ids = list()
        query = CanisterMaster.select(UniqueDrug.drug_id).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .where(CanisterMaster.id << canister_list)

        for record in query:
            drug_ids.append(record['drug_id'])

        return drug_ids

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_drug_data_from_canister_list {}".format(e))
        raise e

    except DoesNotExist as e:
        logger.error("error in get_drug_data_from_canister_list {}".format(e))
        raise


@log_args_and_response
def get_zonewise_avilability_by_drug(alternate_drug_ids, company_id):
    try:
        drug_zone_canister_count_dict = {}
        drug_zone_avail_quantity_dict = {}
        zone_list = set()
        alternate_drug_ids = list(alternate_drug_ids)
        query = CanisterMaster.select(CanisterMaster.drug_id, CanisterMaster.id, CanisterZoneMapping.zone_id,
                                      CanisterMaster.available_quantity) \
            .join(CanisterZoneMapping, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .where((CanisterMaster.drug_id << alternate_drug_ids) & (
                CanisterMaster.active == settings.is_canister_active) & (
                           CanisterMaster.company_id == company_id))

        for record in query.dicts():
            if record['drug_id'] not in drug_zone_canister_count_dict:
                drug_zone_canister_count_dict[record['drug_id']] = {}
            if record['drug_id'] not in drug_zone_avail_quantity_dict:
                drug_zone_avail_quantity_dict[record['drug_id']] = {}
            if record['zone_id'] not in drug_zone_canister_count_dict[record['drug_id']]:
                drug_zone_canister_count_dict[record['drug_id']][record['zone_id']] = 0
            if record['zone_id'] not in drug_zone_avail_quantity_dict[record['drug_id']]:
                drug_zone_avail_quantity_dict[record['drug_id']][record['zone_id']] = 0
            zone_list.add(record['zone_id'])
            drug_zone_canister_count_dict[record['drug_id']][record['zone_id']] += 1
            drug_zone_avail_quantity_dict[record['drug_id']][record['zone_id']] += record['available_quantity']
        return drug_zone_canister_count_dict, drug_zone_avail_quantity_dict, list(zone_list)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_zonewise_avilability_by_drug {}".format(e))
        raise e


@log_args_and_response
def db_get_canisters(company_id, all_flag=False, system_id=None):
    # todo decide based on deleted canister
    canister_list = []
    clauses = list()
    clauses.append((CanisterMaster.active == settings.is_canister_active))
    clauses.append((CanisterMaster.company_id == company_id))
    CodeMasterAlias = CodeMaster.alias()

    # device_property_clauses = list()

    # device_property_clauses.append((DeviceProperties.property_name == 'drawers_initial_pattern'))
    # device_property_clauses.append((DeviceProperties.device_layout_id == DeviceLayoutDetails.id))

    if system_id:
        if all_flag:  # On shelf plus placed in a specific system
            clauses.append(((DeviceMaster.system_id == system_id) | (CanisterMaster.location_id.is_null(True)) |
                            (DeviceMaster.device_type_id << [settings.DEVICE_TYPES['Canister Transfer Cart'],
                                                             settings.DEVICE_TYPES['Canister Cart w/ Elevator'],
                                                             settings.DEVICE_TYPES['CSR']])))
        else:
            clauses.append((DeviceMaster.system_id == system_id))
    try:
        for record in CanisterMaster.select(
                CanisterMaster.id.alias('canister_id'),
                CanisterMaster.rfid,
                CanisterMaster.available_quantity,
                fn.IF(CanisterMaster.available_quantity < 0, 0, CanisterMaster.available_quantity).alias(
                    'display_quantity'),
                LocationMaster.location_number,
                LocationMaster.container_id,
                ContainerMaster.drawer_name,
                ContainerMaster.drawer_type,
                ContainerMaster.drawer_level,
                ContainerMaster.drawer_usage,
                UniqueDrug.drug_usage,
                CanisterMaster.canister_type,
                LocationMaster.is_disabled.alias('is_location_disabled'),
                CanisterMaster.drug_id,
                DrugMaster.drug_name,
                DrugMaster.strength, DrugMaster.image_name,
                DrugMaster.strength_value,
                DrugMaster.ndc, DrugMaster.imprint,
                DrugMaster.color, DrugMaster.shape,
                DrugMaster.formatted_ndc, DrugMaster.txr,
                CanisterMaster.reorder_quantity,
                CanisterMaster.barcode,
                ContainerMaster.drawer_name.alias('drawer_number'),
                LocationMaster.display_location,
                fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                       SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                       SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_name'),
                DeviceMaster.system_id,
                DeviceMaster.device_type_id,
                # DeviceLayoutDetails.id.alias('device_layout_id'),
                # DeviceProperties.property_value.alias('drawers_initial_pattern'),
                DeviceMaster.name.alias('device_name'),
                DeviceMaster.id.alias('device_id'),
                DeviceTypeMaster.device_type_name,
                DeviceTypeMaster.id.alias('device_type_id'),
                ContainerMaster.ip_address,
                ContainerMaster.secondary_ip_address,
        ).dicts() \
                .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                      fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                     (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(CodeMaster, JOIN_LEFT_OUTER, on=ContainerMaster.drawer_usage == CodeMaster.id) \
                .join(CodeMasterAlias, JOIN_LEFT_OUTER, on=UniqueDrug.drug_usage == CodeMasterAlias.id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
                .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
                .where(functools.reduce(operator.and_, clauses)).group_by(CanisterMaster.id):
            record["drug_name"] = record["drug_name"] + " " + record["strength_value"] \
                                  + " " + record["strength"]
            if all_flag:
                record['is_mfd_canister'] = False
                canister_list.append(record)
            else:
                record['is_mfd_canister'] = False
                if record["location_number"] == 0:
                    canister_list.append(record)

        return canister_list

    except InternalError as e:
        logger.error("error in db_get_canisters {}".format(e))
        raise InternalError


@log_args_and_response
def db_get_deactive_canisters(company_id, all_flag=False, fndc_txr=None, exclude_ndc=None):
    # todo decide based on deleted canister
    unique_ndc_canister_dict = dict()
    canister_list = []
    clauses = list()
    clauses.append((CanisterMaster.active == 0))
    clauses.append(CanisterMaster.rfid.is_null(False))
    clauses.append((CanisterMaster.company_id == company_id))

    if all_flag:  # On shelf plus placed in a specific system
        clauses.append(CanisterMaster.location_id.is_null(True))

    if fndc_txr:
        clauses.append((fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, ''))) << fndc_txr)

    if exclude_ndc:
        clauses.append((DrugMaster.ndc.not_in([exclude_ndc])))

    sub_query = CanisterStatusHistory.select(fn.MAX(CanisterStatusHistory.id).alias('max_canister_history_id'),
                                             CanisterStatusHistory.canister_id.alias('canister_id')) \
        .group_by(CanisterStatusHistory.canister_id).alias('sub_query')

    try:
        for record in CanisterMaster.select(
                CanisterMaster.id.alias('canister_id'),
                CanisterMaster.rfid,
                CanisterMaster.available_quantity,
                CanisterMaster.drug_id,
                DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                DrugMaster.ndc,
                DrugMaster.image_name,
                DrugMaster.shape.alias("drug_shape"),
                DrugMaster.imprint,
                fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                      DrugStockHistory.is_in_stock).alias("is_in_stock"),
                fn.IF(DrugStockHistory.created_by.is_null(True), None,
                      DrugStockHistory.created_by).alias(
                    "stock_updated_by"),
                CustomDrugShape.id.alias("custom_drug_id"),
                CustomDrugShape.name,
                LocationMaster.location_number,
                ContainerMaster.drawer_name.alias('drawer_number'),
                LocationMaster.display_location,
                LocationMaster.container_id.alias('drawer_id'),
                DeviceMaster.system_id,
                DeviceMaster.name.alias('device_name'),
                DeviceMaster.id.alias('device_id'),
                DeviceTypeMaster.device_type_name,
                DeviceTypeMaster.id.alias('device_type_id'),
                DeviceLayoutDetails.id.alias('device_layout_id'),
                ZoneMaster.id.alias('zone_id'),
                ZoneMaster.name.alias('zone_name'),
                ContainerMaster.ip_address,
                ContainerMaster.secondary_ip_address,
                ContainerMaster.serial_number,
                ContainerMaster.shelf,
                DrugDetails.last_seen_by,
                DrugDetails.last_seen_date,
                CanisterStatusHistoryComment.comment.alias('reason'),
        ).dicts() \
                .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                      fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                     (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                .join(sub_query, JOIN_LEFT_OUTER,
                      on=(sub_query.c.canister_id == CanisterMaster.id)) \
                .join(CanisterStatusHistory, JOIN_LEFT_OUTER,
                      on=(CanisterStatusHistory.id == sub_query.c.max_canister_history_id)) \
                .join(CanisterStatusHistoryComment, JOIN_LEFT_OUTER,
                      on=CanisterStatusHistoryComment.canister_status_history_id == CanisterStatusHistory.id) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                             (DrugStockHistory.is_active == True) &
                                                             (
                                                                     DrugStockHistory.company_id == CanisterMaster.company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                       (DrugDetails.company_id == CanisterMaster.company_id)) \
                .join(DrugDimension, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
                .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
                .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
                .where(functools.reduce(operator.and_, clauses)) \
                .order_by(LocationMaster.location_number):

            if record['ndc'] not in unique_ndc_canister_dict:
                unique_ndc_canister_dict[record['ndc']] = record
            else:
                canister_list.append(record)

        if len(unique_ndc_canister_dict):
            canister_list = list(unique_ndc_canister_dict.values()) + canister_list

        return canister_list
    except Exception as e:
        logger.error("error in db_get_deactive_canisters {}".format(e))
        return e

    except InternalError as e:
        logger.error("error in db_get_deactive_canisters {}".format(e))
        raise InternalError


@log_args_and_response
def get_canister_details_by_rfid_dao(rfid):
    try:
        for record in CanisterMaster.select(CanisterMaster.canister_type, UniqueDrug.drug_usage) \
                .dicts() \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                      fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                     (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
                .where(CanisterMaster.rfid == rfid) \
                .group_by(CanisterMaster.id):
            return record['canister_type'], record['drug_usage']

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_canister_details_by_rfid_dao {}".format(e))
        raise

    except DoesNotExist as e:
        logger.error("error in get_canister_details_by_rfid_dao {}".format(e))
        return None, None


@log_args_and_response
def get_canister_details_by_canister_id(canister_id, company_id=None):
    try:
        clauses = []
        if company_id:
            clauses.append(CanisterMaster.company_id == company_id)
        clauses.append(CanisterMaster.id == canister_id)
        usage_status = [constants.USAGE_CONSIDERATION_IN_PROGRESS, constants.USAGE_CONSIDERATION_PENDING]
        for record in CanisterMaster.select(CanisterMaster.id,
                                            CanisterMaster.rfid,
                                            CanisterMaster.drug_id,
                                            CanisterMaster.product_id,
                                            CanisterMaster.canister_type,
                                            CanisterMaster.available_quantity,
                                            fn.IF(
                                                CanisterMaster.expiry_date <= date.today() + timedelta(
                                                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                                constants.EXPIRED_CANISTER,
                                                fn.IF(
                                                    CanisterMaster.expiry_date <= date.today() + timedelta(
                                                        settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                                    constants.EXPIRES_SOON_CANISTER,
                                                    constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                            DrugMaster.drug_name,
                                            DrugMaster.strength,
                                            DrugMaster.strength_value,
                                            DrugMaster.ndc,
                                            DrugMaster.upc,
                                            CanisterTracker.expiration_date.alias("expiry_date"),
                                            CanisterTracker.lot_number,
                                            CanisterTracker.case_id) \
                .dicts() \
                .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(CanisterTracker, JOIN_LEFT_OUTER, on=((CanisterTracker.canister_id == CanisterMaster.id) & (CanisterTracker.usage_consideration.in_(usage_status)))) \
                .where(functools.reduce(operator.and_, clauses)) \
                .group_by(CanisterMaster.id):
            return record

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_canister_details_by_canister_id {}".format(e))
        raise


@log_args_and_response
def get_canister_details(_id, company_id, _type=1):
    try:
        drug_id, device_id, canister_id, current_qty = None, None, None, None
        if _type == 1:
            for record in CanisterMaster.select(
                    CanisterMaster.id,
                    CanisterMaster.available_quantity,
                    CanisterMaster.drug_id, LocationMaster.device_id
            ) \
                    .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                    .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                    .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                    .dicts() \
                    .where(CanisterMaster.id == _id,
                           CanisterMaster.company_id == company_id):
                drug_id, device_id, canister_id, current_qty = record["drug_id"], record["device_id"], \
                                                               record["id"], record["available_quantity"]
        elif _type == 2:
            for record in CanisterMaster.select(
                    CanisterMaster.id, CanisterMaster.available_quantity,
                    CanisterMaster.drug_id, LocationMaster.device_id
            ) \
                    .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                    .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                    .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                    .dicts() \
                    .where(CanisterMaster.rfid == _id,
                           CanisterMaster.company_id == company_id):
                drug_id, device_id, canister_id, current_qty = record["drug_id"], record["device_id"], \
                                                               record["id"], record["available_quantity"]
        else:
            raise InternalError("Invalid type to distinguish canister.")
    except DoesNotExist as ex:
        logger.error("error in get_canister_details {}".format(ex))
        raise ex
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_canister_details {}".format(e))
        raise

    return drug_id, device_id, canister_id, current_qty


@log_args_and_response
def db_get_canister_details_by_rfid(rfid, company_id, ai_width=14, ai_min=3, include_strength=False):
    try:
        data = []
        for canister_record in CanisterMaster.select(
                CanisterMaster.id.alias('canister_id'),
                CanisterMaster.rfid,
                CanisterMaster.available_quantity,
                fn.IF(CanisterMaster.available_quantity < 0, 0, CanisterMaster.available_quantity).alias(
                    'display_quantity'),
                LocationMaster.location_number,
                LocationMaster.is_disabled.alias('is_location_disabled'),
                fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                       SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                       SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_name'),
                DeviceMaster.system_id,
                CanisterMaster.drug_id,
                DrugMaster.drug_name,
                DrugMaster.strength,
                DrugMaster.strength_value,
                DrugMaster.ndc,
                DrugMaster.formatted_ndc,
                CanisterMaster.reorder_quantity,
                CanisterMaster.barcode
        ) \
                .dicts() \
                .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
                .where(CanisterMaster.rfid << rfid,
                       CanisterMaster.company_id == company_id).group_by(CanisterMaster.id):
            canister_record["short_drug_name_v2"] = fn_shorten_drugname_v2(
                canister_record["drug_name"],
                canister_record["strength"],
                canister_record["strength_value"],
                ai_width=ai_width,
                ai_min=ai_min,
                include_strength=include_strength
            )
            data.append(canister_record)
        return data
    except (DoesNotExist, InternalError, IntegrityError, Exception) as ex:
        logger.error("error in db_get_canister_details_by_rfid: {}".format(ex))
        raise ex


@log_args_and_response
def db_get_canister_location_by_rfid(rfid):
    try:
        # get the current quantity from the canister based on canister id
        location = CanisterMaster.select(LocationMaster.location_number,
                                         LocationMaster.display_location,
                                         LocationMaster.quadrant,
                                         DeviceMaster.device_type_id,
                                         DeviceMaster.ip_address.alias('device_ip_address'),
                                         DeviceMaster.name.alias('device_name'),
                                         LocationMaster.is_disabled.alias('is_location_disabled'),
                                         ContainerMaster,
                                         fn.GROUP_CONCAT(Clause(
                                             fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                             SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                                         fn.GROUP_CONCAT(Clause(fn.DISTINCT(
                                             fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                             SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                             'zone_name'),
                                         DeviceMaster.system_id,
                                         ) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(CanisterMaster.rfid == rfid).group_by(CanisterMaster.id).dicts().get()
        return location
    except DoesNotExist as ex:
        logger.error("error in db_get_canister_location_by_rfid {}".format(ex))
        raise DoesNotExist(ex)
    except InternalError as e:
        logger.error("error in db_get_canister_location_by_rfid {}".format(e))
        raise InternalError(e)


@log_args_and_response
def db_get_canister_by_canister_code(canister_code):
    canister_data = dict()
    try:
        for record in CanisterMaster.select(
                CanisterMaster.id.alias('canister_id'),
                CanisterMaster.rfid,
                CanisterMaster.available_quantity,
                fn.IF(CanisterMaster.available_quantity < 0, 0, CanisterMaster.available_quantity).alias(
                    'display_quantity'),
                LocationMaster.location_number,
                LocationMaster.is_disabled.alias('is_location_disabled'),
                fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                       SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                       SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_name'),
                DeviceMaster.system_id,
                CanisterMaster.drug_id,
                DrugMaster.drug_name,
                DrugMaster.strength,
                DrugMaster.strength_value,
                DrugMaster.ndc,
                DrugMaster.formatted_ndc,
                CanisterMaster.reorder_quantity,
                CanisterMaster.barcode,
                CanisterMaster.canister_code
        ).dicts() \
                .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
                .where(CanisterMaster.canister_code == canister_code).group_by(CanisterMaster.id):
            canister_data = record

        return canister_data
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_canister_by_canister_code {}".format(e))
        raise


@log_args_and_response
def db_get_by_id_list(canister_id_list):
    """
    Returns dict of canister data

    :param canister_id_list:
    :return: dict
    """
    canister_data_list = list()
    try:
        for record in CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                            CanisterMaster.drug_id,
                                            LocationMaster.location_number,
                                            CanisterMaster.available_quantity,
                                            fn.IF(CanisterMaster.available_quantity < 0, 0,
                                                  CanisterMaster.available_quantity).alias('display_quantity'),
                                            CanisterMaster.rfid,
                                            DrugMaster.drug_name,
                                            DrugMaster.ndc,
                                            DrugMaster.strength,
                                            DrugMaster.strength_value,
                                            DrugMaster.imprint,
                                            DrugMaster.image_name,
                                            DrugMaster.shape,
                                            DrugMaster.color,
                                            DrugMaster.formatted_ndc,
                                            DrugMaster.txr,
                                            DrugMaster.drug_form,
                                            DrugMaster.manufacturer).dicts() \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                .where(CanisterMaster.id.in_(canister_id_list)):
            canister_data_list.append(record)
    except (InternalError, IntegrityError) as e:
        logger.error("error in db_get_by_id_list {}".format(e))
        raise

    return canister_data_list


@log_args_and_response
def db_get_canister_by_company_id(company_id, in_robot=False):
    """

    :param company_id:
    :param in_robot:
    :return:
    """

    clauses = list()

    clauses.append((CanisterMaster.company_id == company_id))

    LocationMasterAlias = LocationMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()
    CanisterHistoryAlias = CanisterHistory.alias()

    sub_query = CanisterHistoryAlias.select(fn.MAX(CanisterHistoryAlias.id).alias('max_canister_history_id'),
                                            CanisterHistoryAlias.canister_id.alias('canister_id')) \
        .group_by(CanisterHistoryAlias.canister_id).alias('sub_query')

    if in_robot:  # if you need only robot canisters
        clauses.append((DeviceTypeMaster.id == settings.DEVICE_TYPES['ROBOT']))
    else:
        clauses.append((CanisterMaster.active == settings.is_canister_active))

    try:
        for record in CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                            CanisterMaster.available_quantity,
                                            fn.IF(CanisterMaster.available_quantity < 0, 0,
                                                  CanisterMaster.available_quantity).alias('display_quantity'),
                                            LocationMaster.location_number,
                                            CanisterMaster.rfid,
                                            CanisterMaster.product_id,
                                            DrugMaster.drug_name,
                                            DrugMaster.strength_value,
                                            DrugMaster.strength,
                                            DrugMaster.formatted_ndc,
                                            DrugMaster.txr,
                                            DrugMaster.imprint,
                                            DrugMaster.image_name,
                                            DrugMaster.shape,
                                            DrugMaster.color,
                                            DrugMaster.manufacturer,
                                            DrugMaster.ndc,
                                            LocationMaster.location_number,
                                            ContainerMaster.drawer_name.alias('drawer_number'),
                                            LocationMaster.display_location,
                                            LocationMaster.quadrant,
                                            ZoneMaster.id.alias('zone_id'),
                                            ZoneMaster.name.alias('zone_name'),
                                            DeviceLayoutDetails.id.alias('device_layout_id'),
                                            DeviceMaster.name.alias('device_name'),
                                            DeviceMaster.id.alias('device_id'),
                                            DeviceTypeMaster.device_type_name,
                                            DeviceTypeMaster.id.alias('device_type_id'),
                                            ContainerMaster.ip_address,
                                            ContainerMaster.secondary_ip_address,
                                            CanisterHistory.created_date.alias('last_seen_time'),
                                            DeviceMasterAlias.name.alias('previous_device_name'),
                                            LocationMasterAlias.id.alias('previous_location_id'),
                                            LocationMasterAlias.display_location.alias('previous_display_location'),
                                            fn.IF(LocationMaster.display_location.is_null(False),
                                                  LocationMaster.get_device_location(), -1).alias(
                                                'canister_location'),
                                            ).dicts() \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
                .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, DeviceLayoutDetails.zone_id == ZoneMaster.id) \
                .join(sub_query, JOIN_LEFT_OUTER,
                      on=(sub_query.c.canister_id == CanisterMaster.id)) \
                .join(CanisterHistory, JOIN_LEFT_OUTER,
                      on=(CanisterHistory.id == sub_query.c.max_canister_history_id)) \
                .join(LocationMasterAlias, JOIN_LEFT_OUTER,
                      on=(CanisterHistory.previous_location_id == LocationMasterAlias.id)) \
                .join(DeviceMasterAlias, JOIN_LEFT_OUTER,
                      on=(LocationMasterAlias.device_id == DeviceMasterAlias.id)) \
                .where(functools.reduce(operator.and_, clauses)):
            yield record
    except (InternalError, IntegrityError) as e:
        logger.error("error in db_get_canister_by_company_id {}".format(e))
        raise


@log_args_and_response
def get_available_trolley_data(device_type_ids, company_id):
    """
    Function to return list of available devices(trolley) by device_type
    @param device_type_ids:
    @param company_id:
    @return db_result: {device_type_ids: [devices] }
    """

    # TODO : make function generic to be used in case of any devices
    try:
        db_result = dict()
        DeviceMasterAlias = DeviceMaster.alias()
        sub_query = DeviceMasterAlias.select(DeviceMasterAlias.id) \
            .join(LocationMaster, on=LocationMaster.device_id == DeviceMasterAlias.id) \
            .join(CanisterMaster, on=CanisterMaster.location_id == LocationMaster.id) \
            .where(DeviceMasterAlias.company_id == company_id,
                   DeviceMasterAlias.active == settings.is_device_active,
                   DeviceMasterAlias.device_type_id << device_type_ids) \
            .group_by(DeviceMasterAlias.id).alias('sub_query')

        data = list()
        for record in sub_query.dicts():
            data.append(record['id'])

        query = DeviceMaster.select(DeviceMaster.id,
                                    DeviceMaster.name,
                                    DeviceMaster.device_type_id,
                                    DeviceMaster.active,
                                    DeviceMaster.serial_number) \
            .join(sub_query, JOIN_LEFT_OUTER, on=sub_query.c.id == DeviceMaster.id) \
            .where(DeviceMaster.company_id == company_id,
                   DeviceMaster.active == settings.is_device_active,
                   DeviceMaster.device_type_id << device_type_ids) \
            .group_by(DeviceMaster.id)

        if len(data):
            query = query.where(DeviceMaster.id.not_in(data))

        for record in query.dicts():
            if record['device_type_id'] not in db_result.keys():
                db_result[record['device_type_id']] = list()
            db_result[record['device_type_id']].append(record)

        return db_result

    except InternalError as e:
        logger.error("error in get_available_trolley_data {}".format(e))
        raise e
    except IntegrityError as e:
        logger.error("error in get_available_trolley_data {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_available_trolley_data {}".format(e))
        return e


@log_args_and_response
def find_canister_location_in_csr(canister_id_list, company_id, drug_id_list):
    try:

        clauses = list()
        clauses.append((CanisterMaster.company_id == company_id))
        clauses.append((DeviceTypeMaster.device_type_name == settings.DEVICE_TYPES_NAMES['CSR']))
        # Have to add this condition as this api is to tell about the location of canisters in the csr. If we have to
        # send the location of canisters in the robot then we have to handle that part in
        # get_and_format_device_location_data function.
        if len(canister_id_list) > 0:
            clauses.append((CanisterMaster.id << canister_id_list))
        elif len(drug_id_list) > 0:
            clauses.append((CanisterMaster.drug_id << drug_id_list))
        query = LocationMaster.select(LocationMaster.id.alias('location_id'),
                                      ContainerMaster.drawer_name.alias('drawer_number'),
                                      LocationMaster.display_location,
                                      LocationMaster.location_number,
                                      LocationMaster.is_disabled.alias('is_location_disabled'),
                                      DeviceLayoutDetails.id.alias('device_id'),
                                      DeviceMaster.name.alias('device_name'),
                                      DeviceMaster.system_id,
                                      fn.GROUP_CONCAT(Clause(
                                          fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                          SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                                      fn.GROUP_CONCAT(Clause(fn.DISTINCT(
                                          fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                          SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                          'zone_name'),
                                      DeviceMaster.company_id,
                                      ZoneMaster.id.alias('zone_id'),
                                      ZoneMaster.name.alias('zone_name'),
                                      CanisterMaster.id.alias('canister_id'),
                                      ContainerMaster.ip_address,
                                      ContainerMaster.secondary_ip_address,
                                      fn.IF(LocationMaster.display_location, LocationMaster.get_device_location(),
                                            None).alias('csr_location_number')
                                      ).dicts() \
            .join(CanisterMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(DeviceTypeMaster, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .where(functools.reduce(operator.and_, clauses)).group_by(CanisterMaster.id)

        # db_data = list()
        # for location_data in query:
        #     location_data['formatted_location'] = int(location_data['display_location'].split('-')[1]) - 1
        #     db_data.append(location_data)
        return list(query)
    except (IntegrityError, InternalError, DataError, DoesNotExist) as e:
        logger.error("error in get_available_trolley_data {}".format(e))
        raise e



@log_args_and_response
def db_get_canister_fndc_txr(company_id):
    """
    Returns set of fndc_txr present in canister for given company_id
    :param company_id:
    :return:
    """
    try:
        fndc_txrs = set()
        query = CanisterMaster.select(
            fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, '')).alias('fndc_txr')
        ).distinct() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(CanisterMaster.company_id == company_id,
                   CanisterMaster.active == settings.is_canister_active)
        for record in query.dicts():
            fndc_txrs.add(record['fndc_txr'])
        return fndc_txrs
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_canister_fndc_txr {}".format(e))
        raise


@log_args_and_response
def get_all_canisters_of_a_csr(device_id_list, drawer_number_list, location_number_dict, company_id):
    db_result = []
    try:
        location_number_list = list(location_number_dict.keys())
        query = CanisterMaster.select(CanisterMaster.rfid,
                                      CanisterMaster.available_quantity,
                                      CanisterMaster.id.alias('canister_id'),
                                      fn.GROUP_CONCAT(Clause(
                                          fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                          SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                                      fn.GROUP_CONCAT(Clause(fn.DISTINCT(
                                          fn.IF(ZoneMaster.name.is_null(True), 'null', ZoneMaster.name)),
                                          SQL(" SEPARATOR ' & ' "))).coerce(False).alias(
                                          'zone_name'),
                                      DeviceMaster.system_id,
                                      ContainerMaster.drawer_name.alias('drawer_number'),
                                      LocationMaster.device_id.alias('device_id'),
                                      DrugMaster.ndc,
                                      DrugMaster.txr,
                                      DrugMaster.concated_drug_name_field().alias('drug_name'),
                                      LocationMaster.location_number,
                                      ).dicts() \
            .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, DeviceMaster.id == LocationMaster.device_id) \
            .where(LocationMaster.device_id << device_id_list,
                   ContainerMaster.drawer_name << drawer_number_list,
                   LocationMaster.location_number << location_number_list,
                   CanisterMaster.company_id == company_id).group_by(CanisterMaster.id)

        for canister_data in query:
            canister_data['formatted_location_number'] = location_number_dict[canister_data['location_number']]
            db_result.append(canister_data)

        return db_result
    except (IntegrityError, InternalError, DataError, DoesNotExist) as e:
        logger.error("error in get_all_canisters_of_a_csr {}".format(e))
        raise e


@log_args_and_response
def get_unique_canister_types(company_id: int) -> list:
    """
    Fetches all the unique canister type for the given company id.
    @return:
    """
    logger.info("In get_unique_canister_types")
    try:
        query = CanisterMaster.select(fn.DISTINCT(UniqueDrug.drug_usage).alias("unique_canister_types")).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .where(CanisterMaster.company_id == company_id) \
            .order_by(CanisterMaster.id)

        response_list = []
        for record in query:
            response_list.append(record["unique_canister_types"])
        return response_list
    except (IntegrityError, InternalError) as e:
        logger.error("error in get_unique_canister_types {}".format(e))
        raise e


@log_args_and_response
def get_unique_canister_sizes(company_id: int) -> list:
    """
    Fetches all the unique canister size for the given company id.
    @return:
    """
    logger.info("In get_unique_canister_sizes")
    try:
        query = CanisterMaster.select(fn.DISTINCT(CanisterMaster.canister_type).alias("unique_canister_sizes")).dicts() \
            .where(CanisterMaster.company_id == company_id).order_by(CanisterMaster.id)
        response_list = []
        for record in query:
            response_list.append(record["unique_canister_sizes"])
        return response_list
    except (IntegrityError, InternalError) as e:
        logger.error("error in get_unique_canister_sizes {}".format(e))
        raise e


@log_args_and_response
def db_is_canister_present(device_id, location_number):
    """
    @param device_id:
    @param location_number:
    :return: status of query execution, canister present or not
    """
    try:
        location_id = None
        if device_id and location_number:
            location_id = LocationMaster.get_location_id(device_id=device_id, location_number=location_number)
        record = CanisterMaster.get(CanisterMaster.location_id == location_id)
        if record.location_id is not None:
            return True, True
        return True, False
    except DoesNotExist as ex:
        logger.error("error in db_is_canister_present {}".format(ex))
        return True, False  # status: True and canister present: False
    except InternalError as e:
        logger.error("error in db_is_canister_present {}".format(e))
        return False, False


@log_args_and_response
def update_canister_status_by_location_dao(status: bool, location_id: int):
    try:
        return CanisterMaster.update_canister_status_by_location(status=status, location_id=location_id)
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("error in update_canister_status_by_location_dao {}".format(e))
        raise


@log_args_and_response
def db_get_last_canister_id_dao():
    try:
        return CanisterMaster.db_get_last_canister_id()
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_get_last_canister_id_dao {}".format(e))
        raise


@log_args_and_response
def db_check_canister_available_dao(rfid):
    try:
        return CanisterMaster.get_canister_id_by_rfid(rfid=rfid)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_check_canister_available_dao {}".format(e))
        raise


@log_args_and_response
def db_create_canister_record_dao(dict_canister_info, company_id, canister_code, user_id, location_id):
    try:
        return CanisterMaster.db_create_canister_record(dict_canister_info, company_id, canister_code, user_id,
                                                        location_id)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_create_canister_record_dao {}".format(e))
        raise


@log_args_and_response
def validate_reserved_canisters(canister_list: list) -> bool:
    """
    check if canister is reserved or not if canister is reserved then False, otherwise True
    """
    try:
        return ReservedCanister.db_validate_canisters(canisters=canister_list)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in validate_reserved_canisters:  {}".format(e))
        raise e


@log_args_and_response
def db_get_canister_data_by_location_id_dao(location_id: int) -> dict:
    """
    function to get canister data(dict) by location_id, raise exception if no canister found
    """
    try:
        return CanisterMaster.db_get_canister_data_by_location_id(location_id=location_id)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_canister_data_by_location_id_dao:  {}".format(e))
        raise e


@log_args_and_response
def db_add_canister_drawer_dao(canister_drawer_data, default_dict):
    try:
        return CanisterTracker.db_add_canister_drawer(canister_drawer_data, default_dict)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_add_canister_drawer_dao {}".format(e))
        raise e


@log_args_and_response
def get_drug_data_by_company_id_dao(canister_data_dict):
    company_id = int(canister_data_dict["company_id"])

    if "limit" in canister_data_dict:
        limit = int(canister_data_dict["limit"])
    else:
        limit = -1

    sort_by_usage = int(canister_data_dict["sort_by_use"])
    drug_name = canister_data_dict["drug_name"]
    ndc = canister_data_dict["ndc"]
    lot_number = canister_data_dict["lot_number"]
    page_number = int(canister_data_dict["page_no"])

    current_date = get_current_date()
    previous_date = datetime.strptime(current_date, '%Y-%m-%d') - timedelta(days=120)
    current_date = datetime.strptime(current_date, '%Y-%m-%d')

    db_result = []
    try:
        clauses = list()
        clauses.append((CanisterMaster.company_id == company_id))

        if drug_name is not None:
            drug_name = escape_wrap_wildcard(drug_name)
            clauses.append((DrugMaster.drug_name ** drug_name))

        if ndc is not None:
            ndc = escape_wrap_wildcard(ndc)
            clauses.append((DrugMaster.ndc ** ndc))

        if lot_number is not None:
            lot_drug_data = get_drug_lot_information_from_lot_number_dao(lot_number=lot_number)
            drug_id = lot_drug_data.drug_id
            clauses.append((DrugMaster.id == drug_id))

        query = DrugMaster.select(DrugMaster).join(DrugTracker, JOIN_LEFT_OUTER,
                                                   on=DrugMaster.id == DrugTracker.drug_id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=(CanisterMaster.drug_id == DrugMaster.id))

        if sort_by_usage:
            clauses.append((PackDetails.company_id == company_id))
            clauses.append(PackDetails.created_date.between(previous_date, current_date))

            query = query.join(SlotDetails, on=SlotDetails.drug_id == DrugMaster.id) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                .where(functools.reduce(operator.and_, clauses)) \
                .group_by(DrugMaster.formatted_ndc, DrugMaster.txr).order_by(
                fn.SUM(SlotDetails.quantity).desc())

        else:
            query = query.where(functools.reduce(operator.and_, clauses)).group_by(DrugMaster.formatted_ndc,
                                                                                   DrugMaster.txr)

        query_count = query.count()

        if page_number != -1 and limit != -1:
            required_dict = {"page_number": page_number, "number_of_rows": limit}
            query = apply_paginate(query=query, paginate=required_dict)

        elif limit != -1:
            query = query.limit(limit)

        for data in query.dicts():
            db_result.append(data)

            required_dict = {"drug_id_list": [data["id"]]}
            drug_id_list = get_drug_id_list_for_same_configuration_by_drug_id(required_dict)
            drug_canister_dict = CanisterMaster.get_canister_count_by_drug_and_company_id(company_id=company_id,
                                                                                          drug_id_list=drug_id_list)
            drug_bottle_dict = get_drug_bottle_count_by_drug_and_company_id(company_id=company_id,
                                                                            drug_id_list=drug_id_list)
            try:
                data["bottle_count"] = drug_bottle_dict[data["id"]]
            except Exception as e:
                data["bottle_count"] = 0

            try:
                data["canister_count"] = drug_canister_dict[data["id"]]
            except Exception as e:
                data["canister_count"] = 0

        resp_dict = {"total_results": query_count, "drug_data": db_result}
        return resp_dict
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_drug_data_by_company_id_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_canister_data_by_rfid_company_dao(rfid, company_id):
    try:
        return CanisterMaster.db_get_canister_data_by_rfid_company(rfid=rfid, company_id=company_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_canister_data_by_rfid_company_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_reserved_canister_data(canister_id: int):
    """
        get reserved canister data
    """
    logger.info("Inside db_get_reserved_canister_data")
    try:
        canister_data = ReservedCanister.select(ReservedCanister, BatchMaster, LocationMaster.device_id).dicts() \
            .join(BatchMaster, on=ReservedCanister.batch_id == BatchMaster.id)\
            .join(CanisterMaster, on=CanisterMaster.id == ReservedCanister.canister_id)\
            .join(LocationMaster, JOIN_LEFT_OUTER ,on=LocationMaster.id == CanisterMaster.location_id)\
            .where(ReservedCanister.canister_id == canister_id).get()
        logger.info('reserved_canister_found: ' + str(canister_data))

        return canister_data

    except DoesNotExist as e:
        logger.error("error in db_get_reserved_canister_data {}".format(e))
        return None

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_reserved_canister_data:  {}".format(e))
        raise e


@log_args_and_response
def get_canister_device_id_by_pack_analysis(canister_id: int):
    """
        get reserved canister data
    """
    logger.info("Inside get_canister_device_id_by_pack_analysis")
    device_id = 0
    try:
        canister_location = PackAnalysisDetails.select(PackAnalysisDetails.device_id).dicts().where(
            PackAnalysisDetails.canister_id == canister_id)
        for record in canister_location:
            device_id = record['device_id']

        return device_id

    except DoesNotExist as e:
        logger.error("error in get_canister_device_id_by_pack_analysis {}".format(e))
        return None

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_canister_device_id_by_pack_analysis:  {}".format(e))
        raise e


@log_args_and_response
def db_canister_tracker_insert_data(insert_dict_list):
    try:
        return CanisterTracker.insert_many(insert_dict_list).execute()
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_canister_tracker_insert_data {}".format(e))
        raise e


@log_args_and_response
def add_generate_canister_data(args: dict) -> tuple:
    """
    function to add generate canister data
    """
    try:
        return GenerateCanister.db_add_generate_canister_data(args)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in add_generate_canister_data:  {}".format(e))
        raise e


@log_args_and_response
def update_canister_stick_of_canister(canister_id: int, canister_stick_id: int) -> bool:
    """
    function to update canister stick id of canister
    @param canister_stick_id:
    @param canister_id:
    @return:
    """
    try:
        status = CanisterMaster.db_update_canister_stick_of_canister(canister_id=canister_id, canister_stick_id=canister_stick_id)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_canister_stick_of_canister {}".format(e))
        raise e


@log_args_and_response
def get_alternate_canister_for_batch_data(company_id: int, alt_in_robot: bool = True, alt_available: bool = True,
                                          ignore_reserve_status: bool = False, current_not_in_robot: bool = True, canister_ids: list = None,
                                          device_id: int = None, skip_canisters: bool = None, alt_in_csr: bool = False,
                                          guided_transfer: bool = False, alt_canister_for_guided: bool = False, batch_id = None):
    """
    Function to get alternate canister for batch
    @param company_id:
    @param alt_in_robot:
    @param alt_available:
    @param ignore_reserve_status:
    @param current_not_in_robot:
    @param canister_ids:
    @param device_id:
    @param skip_canisters:
    @param alt_in_csr:
    @param guided_transfer:
    @param alt_canister_for_guided:
    @return:
    @param batch_id:
    """
    # CanisterMasterAlias1 = CanisterMaster.alias()
    CanisterMasterAlias2 = CanisterMaster.alias()
    LocationMasterAlias = LocationMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()

    DrugMasterAlias = DrugMaster.alias()

    canister_list = []
    if batch_id:
        query = CanisterTransfers.select(CanisterTransfers.canister_id).dicts() \
                .where(CanisterTransfers.batch_id == batch_id)
        for data in query:
            canister_list.append(data['canister_id'])
    else:
        pack_queue_canister_query = PackQueue.select(PackAnalysisDetails.canister_id).dicts() \
                                    .join(PackAnalysis, on=PackAnalysis.pack_id == PackQueue.pack_id) \
                                    .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                                    .group_by(PackAnalysisDetails.canister_id)
        # TODO: need to test this flow. removed batch id from canister transfer and added canister_id check, which will used in packs of packqueue
        for data in pack_queue_canister_query:
            canister_list.append(data["canister_id"])

    try:
        if skip_canisters:
            skip_canisters = [
                item.id for item in CanisterMaster.select(CanisterMaster.id)
                    .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id)
                    .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id)
                    .where(LocationMaster.device_id == device_id |
                           CanisterMaster.location_id.is_null(True) |
                           DeviceMaster.device_type_id == settings.DEVICE_TYPES['CSR'])
            ]
        else:
            skip_canisters = None

        logger.info("In _get_alternate_canister_for_batch: skip_canisters: {} ".format(skip_canisters))
        reserved_canisters = ReservedCanister.db_get_reserved_canister_query(company_id=company_id,
                                                                             skip_canisters=skip_canisters)
        logger.info("In _get_alternate_canister_for_batch: reserved canister: {} ".format(reserved_canisters))

        # candidate alternate canisters which are not reserved
        alternate_canister = CanisterMasterAlias2.select(CanisterMasterAlias2.id.alias('canister_id'),
                                                         CanisterMasterAlias2.available_quantity,
                                                         fn.IF(CanisterMasterAlias2.available_quantity < 0, 0,
                                                               CanisterMasterAlias2.available_quantity).alias(
                                                             'display_quantity'),
                                                         CanisterMasterAlias2.rfid.alias('rfid'),
                                                         CanisterMasterAlias2.canister_type.alias('canister_type'),
                                                         fn.IF(
                                                             CanisterMasterAlias2.expiry_date <= date.today() + timedelta(
                                                                 settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                                             constants.EXPIRED_CANISTER,
                                                             fn.IF(
                                                                 CanisterMasterAlias2.expiry_date <= date.today() + timedelta(
                                                                     settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                                                 constants.EXPIRES_SOON_CANISTER,
                                                                 constants.NORMAL_EXPIRY_CANISTER)).alias(
                                                             "expiry_status"),
                                                         CanisterMasterAlias2.expiry_date,
                                                         DrugMasterAlias.formatted_ndc,
                                                         DrugMasterAlias.txr,
                                                         DrugMasterAlias.ndc,
                                                         DrugMasterAlias.drug_name,
                                                         DrugMasterAlias.strength_value,
                                                         DrugMasterAlias.strength,
                                                         UniqueDrug.is_powder_pill,
                                                         LocationMasterAlias.location_number,
                                                         ContainerMaster.id.alias('container_id'),
                                                         ContainerMaster.drawer_name.alias('drawer_name'),
                                                         LocationMasterAlias.display_location,
                                                         ZoneMaster.id.alias('zone_id'),
                                                         ZoneMaster.name.alias('zone_name'),
                                                         DeviceLayoutDetails.id.alias('device_layout_id'),
                                                         DeviceMasterAlias.name.alias('device_name'),
                                                         DeviceMasterAlias.id.alias('device_id'),
                                                         DeviceMasterAlias.ip_address.alias('device_ip_address'),
                                                         DeviceTypeMaster.device_type_name,
                                                         DeviceTypeMaster.id.alias('device_type_id'),
                                                         ContainerMaster.drawer_level,
                                                         ContainerMaster.ip_address,
                                                         ContainerMaster.secondary_ip_address,
                                                         ContainerMaster.serial_number,
                                                         DrugDetails.last_seen_by.alias('last_seen_with'),
                                                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                                               DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                                         fn.IF(DrugStockHistory.created_by.is_null(True), None,
                                                               DrugStockHistory.created_by).alias("stock_updated_by"),
                                                         UniqueDrug.is_delicate) \
            .join(DrugMasterAlias, on=DrugMasterAlias.id == CanisterMasterAlias2.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=(UniqueDrug.formatted_ndc == DrugMasterAlias.formatted_ndc)
                                                  & (UniqueDrug.txr == DrugMasterAlias.txr)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER,
                  on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) & (DrugStockHistory.is_active == 1)
                      & (DrugStockHistory.company_id == CanisterMasterAlias2.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                   (DrugDetails.company_id == CanisterMasterAlias2.company_id)) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, on=CanisterZoneMapping.canister_id == CanisterMasterAlias2.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, on=CanisterZoneMapping.zone_id == ZoneMaster.id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, CanisterMasterAlias2.location_id == LocationMasterAlias.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMasterAlias.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMasterAlias.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMasterAlias.id)
        alternate_canister = alternate_canister.where(CanisterMasterAlias2.company_id == company_id,
                                                      CanisterMasterAlias2.active == settings.is_canister_active)

        if alt_in_robot:  # if alt canister must be present in robot
            alternate_canister = alternate_canister.where(DeviceMasterAlias.device_type_id == settings.DEVICE_TYPES['ROBOT'])
        if alt_in_csr:
            alternate_canister = alternate_canister.where(DeviceMasterAlias.device_type_id == settings.DEVICE_TYPES["CSR"])
        if not ignore_reserve_status:
            alternate_canister = alternate_canister.where(CanisterMasterAlias2.id.not_in(reserved_canisters))
        # alternate_canister = alternate_canister.order_by(CanisterMasterAlias2.available_quantity.desc())
        alternate_canister = alternate_canister.alias('alternate_canister')

        order_list: list = list()
        on_condition = ((alternate_canister.c.formatted_ndc == DrugMaster.formatted_ndc)
                        & (alternate_canister.c.txr == DrugMaster.txr)
                        & (alternate_canister.c.canister_id != CanisterMaster.id))
        if alt_in_robot:
            on_condition = on_condition & (alternate_canister.c.device_id == CanisterTransfers.dest_device_id)

        if not guided_transfer:
            query = CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
                                             LocationMaster.device_id,
                                             LocationMaster.location_number,
                                             LocationMaster.display_location,
                                             LocationMaster.quadrant,
                                             ZoneMaster.id.alias('zone_id'),
                                             DeviceMaster.name.alias('device_name'),
                                             DeviceMaster.device_type_id,
                                             DeviceMaster.ip_address.alias('device_ip_address'),
                                             ContainerMaster.id.alias('drawer_id'),
                                             ContainerMaster.drawer_name.alias('drawer_number'),
                                             ContainerMaster.serial_number,
                                             ContainerMaster.ip_address,
                                             ContainerMaster.mac_address,
                                             ContainerMaster.secondary_mac_address,
                                             ContainerMaster.secondary_ip_address,
                                             DeviceMaster.id.alias('device_id'),
                                             alternate_canister.c.canister_id.alias('alt_canister_id'),
                                             alternate_canister.c.canister_type.alias('alt_canister_type'),
                                             alternate_canister.c.drawer_level.alias('alt_can_drawer_level'),
                                             alternate_canister.c.device_id.alias('alt_device_id'),
                                             alternate_canister.c.device_type_id.alias('alt_device_type_id'),
                                             alternate_canister.c.location_number.alias('alt_location_number'),
                                             alternate_canister.c.ndc.alias('alt_ndc'),
                                             alternate_canister.c.drug_name.alias('alt_drug_name'),
                                             alternate_canister.c.is_powder_pill.alias('is_powder_pill'),
                                             alternate_canister.c.strength.alias('alt_strength'),
                                             alternate_canister.c.strength_value.alias('alt_strength_value'),
                                             alternate_canister.c.device_name.alias('alt_device_name'),
                                             alternate_canister.c.available_quantity.alias('alt_available_quantity'),
                                             alternate_canister.c.rfid.alias('alt_rfid'),
                                             alternate_canister.c.drawer_name.alias('alt_drawer_number'),
                                             alternate_canister.c.display_location.alias('alt_display_location'),
                                             alternate_canister.c.container_id.alias('alt_drawer_id'),
                                             alternate_canister.c.ip_address.alias('alt_ip_address'),
                                             alternate_canister.c.zone_id.alias('alt_zone_id'),
                                             alternate_canister.c.zone_name.alias('alt_zone_name'),
                                             alternate_canister.c.secondary_ip_address.alias(
                                                 'alt_secondary_ip_address'),
                                             alternate_canister.c.serial_number.alias('alt_serial_number'),
                                             alternate_canister.c.last_seen_with.alias('last_seen_with'),
                                             alternate_canister.c.is_in_stock.alias('is_in_stock'),
                                             alternate_canister.c.stock_updated_by.alias('stock_updated_by'),
                                             alternate_canister.c.container_id.alias('container_id'),
                                             alternate_canister.c.device_ip_address.alias('alt_device_ip_address'),
                                             alternate_canister.c.expiry_status.alias('alt_expiry_status'),
                                             DrugMaster.drug_name,
                                             DrugMaster.strength_value,
                                             DrugMaster.strength,
                                             DrugMaster.ndc,
                                             DrugMaster.shape, DrugMaster.color,
                                             DrugMaster.imprint, DrugMaster.image_name,
                                             alternate_canister.c.is_delicate.alias('alt_is_delicate'),
                                          UniqueDrug.is_delicate

                                          ) \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                      & (UniqueDrug.txr == DrugMaster.txr)) \
                .join(CanisterZoneMapping, JOIN_LEFT_OUTER, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, on=CanisterZoneMapping.zone_id == ZoneMaster.id) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .join(alternate_canister, JOIN_LEFT_OUTER, on=on_condition)

            # filters = [(CanisterTransfers.batch_id == batch_id)]
            filters = [(CanisterMaster.id.in_(canister_list))]

        else:
            query = GuidedTracker.select(GuidedTracker.source_canister_id,
                                         GuidedTracker.alternate_canister_id,
                                         GuidedTracker.transfer_status,
                                         LocationMaster.device_id,
                                         LocationMaster.location_number,
                                         LocationMaster.display_location,
                                         LocationMaster.quadrant,
                                         ZoneMaster.id.alias('zone_id'),
                                         DeviceMaster.name.alias('device_name'),
                                         DeviceMaster.ip_address.alias('device_ip_address'),
                                         alternate_canister.c.canister_id.alias('alt_canister_id'),
                                         alternate_canister.c.canister_type.alias('alt_canister_type'),
                                         alternate_canister.c.drawer_level.alias('alt_can_drawer_level'),
                                         alternate_canister.c.device_id.alias('alt_device_id'),
                                         alternate_canister.c.device_type_id.alias('alt_device_type_id'),
                                         alternate_canister.c.location_number.alias('alt_location_number'),
                                         alternate_canister.c.ndc.alias('alt_ndc'),
                                         alternate_canister.c.is_powder_pill.alias('is_powder_pill'),
                                         alternate_canister.c.drug_name.alias('alt_drug_name'),
                                         alternate_canister.c.strength.alias('alt_strength'),
                                         alternate_canister.c.strength_value.alias('alt_strength_value'),
                                         alternate_canister.c.device_name.alias('alt_device_name'),
                                         alternate_canister.c.available_quantity.alias('alt_available_quantity'),
                                         alternate_canister.c.rfid.alias('alt_rfid'),
                                         alternate_canister.c.drawer_name.alias('alt_drawer_number'),
                                         alternate_canister.c.display_location.alias('alt_display_location'),
                                         alternate_canister.c.container_id.alias('alt_drawer_id'),
                                         alternate_canister.c.ip_address.alias('alt_ip_address'),
                                         alternate_canister.c.zone_id.alias('alt_zone_id'),
                                         alternate_canister.c.zone_name.alias('alt_zone_name'),
                                         alternate_canister.c.secondary_ip_address.alias('alt_secondary_ip_address'),
                                         alternate_canister.c.serial_number.alias('alt_serial_number'),
                                         alternate_canister.c.last_seen_with.alias('last_seen_with'),
                                         alternate_canister.c.is_in_stock.alias('is_in_stock'),
                                         alternate_canister.c.stock_updated_by.alias('stock_updated_by'),
                                         alternate_canister.c.container_id.alias('container_id'),
                                         alternate_canister.c.device_ip_address.alias('alt_device_ip_address'),
                                         alternate_canister.c.expiry_status.alias('alt_expiry_status'),
                                         DrugMaster.drug_name,
                                         DrugMaster.strength_value,
                                         DrugMaster.strength,
                                         DrugMaster.ndc,
                                         DrugMaster.shape, DrugMaster.color,
                                         DrugMaster.imprint, DrugMaster.image_name,
                                         alternate_canister.c.is_delicate.alias('alt_is_delicate'),
                                         UniqueDrug.is_delicate
                                         ) \
                .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
                .join(CanisterMaster,
                      on=(fn.IF(GuidedTracker.alternate_canister_id.is_null(False), GuidedTracker.alternate_canister_id,
                                GuidedTracker.source_canister_id)) == CanisterMaster.id) \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                      & (UniqueDrug.txr == DrugMaster.txr)) \
                .join(CanisterZoneMapping, JOIN_LEFT_OUTER, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, on=CanisterZoneMapping.zone_id == ZoneMaster.id) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .join(alternate_canister, JOIN_LEFT_OUTER, on=on_condition)

            filters = [GuidedMeta.status != constants.GUIDED_META_TO_CSR_DONE,
                       (GuidedTracker.transfer_status.not_in([constants.GUIDED_TRACKER_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                              constants.GUIDED_TRACKER_TO_ROBOT_SKIPPED_AND_ALTERNATE,
                                                              constants.GUIDED_TRACKER_TO_TROLLEY_TRANSFER_LATER_SKIP,
                                                              constants.GUIDED_TRACKER_TO_ROBOT_TRANSFER_LATER_SKIP]))]

        if current_not_in_robot:
            filters.append((CanisterMaster.location_id.is_null(True)) |
                           (DeviceMaster.device_type_id == settings.DEVICE_TYPES['CSR']))
        if canister_ids:  # alternate canister for specific canister ids
            filters.append((CanisterMaster.id << canister_ids))
        if alt_available:
            filters.append((alternate_canister.c.canister_id.is_null(False)))

        order_list.append(
            SQL('FIELD(alt_expiry_status, {},{},{})'.format(constants.EXPIRES_SOON_CANISTER, constants.EXPIRED_CANISTER,
                                                            constants.NORMAL_EXPIRY_CANISTER)))
        # order_list.append(alternate_canister.c.expiry_date)
        order_list.append(alternate_canister.c.available_quantity.desc())
        # to keep on shelf canisters at the end
        order_list.append(SQL('alt_device_type_id is null'))

        if alt_canister_for_guided:
            order_list.append(SQL('FIELD(alt_device_type_id, {},{},{},{})'
                                  .format(settings.DEVICE_TYPES['CSR'],
                                          settings.DEVICE_TYPES['ROBOT'],
                                          settings.DEVICE_TYPES['Canister Transfer Cart'],
                                          settings.DEVICE_TYPES['Canister Cart w/ Elevator'])))
        else:
            order_list.append(SQL('FIELD(alt_device_type_id, {},{},{},{})'
                                  .format(settings.DEVICE_TYPES['ROBOT'],
                                          settings.DEVICE_TYPES['CSR'],
                                          settings.DEVICE_TYPES['Canister Transfer Cart'],
                                          settings.DEVICE_TYPES['Canister Cart w/ Elevator'])))

        query = query.where(*filters) \
            .order_by(*order_list).group_by(alternate_canister.c.canister_id)

        # for record in query.dicts():
        #     if record['alt_is_delicate'] and not record['is_delicate']:
        #         empty_locations, drawer_data = db_get_drawer_wise_empty_locations(device_id,
        #                                                                           record["quadrant"])
        #         if constants.SMALL_CANISTER_CODE in empty_locations.keys():
        #             small_canisters = empty_locations[constants.SMALL_CANISTER_CODE]
        #             small_canisters = sorted(small_canisters.keys())
        #             for key in small_canisters:
        #                 record["display_location"] = key + '-' + small_canisters[key][0]
        #                 break
        response_list = []
        ndc_list = []
        for record in query.dicts():
            if record['alt_is_delicate']:
                ndc_list.append(int(record['alt_ndc']))
                slow_movers, canister_id = get_slow_movers_for_device(device_id, record["quadrant"])
                if canister_id:
                    record['slow_movers'] = slow_movers
                    record['slow_movers'][canister_id] = record["slow_movers"][canister_id][0]
            response_list.append(record)

        inventory_data = get_current_inventory_data(ndc_list=ndc_list, qty_greater_than_zero=False)
        inventory_data_dict = {}
        for item in inventory_data:
            inventory_data_dict[item['ndc']] = item['quantity']

        for record in response_list:
            record['inventory_qty'] = inventory_data_dict.get(record['alt_ndc'],0)
            record['is_in_stock'] = 0 if record["inventory_qty"] == 0 else 1
        return response_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_alternate_canister_for_batch_data {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_alternate_canister_for_batch_data {}".format(e))
        raise e


def get_canister_data_by_drug_and_company_id_dao(drug_id_list, company_id):
    try:
        canister_data = CanisterMaster.get_canister_data_by_drug_and_company_id(drug_id_list=drug_id_list,
                                                                                company_id=company_id)
        return canister_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_data_by_drug_and_company_id_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_data_by_drug_and_company_id_dao {}".format(e))
        raise e


@log_args_and_response
def activate_canister_dao(user_id: int, location_id: int, rfid: str, update_location: bool) -> bool:
    """
    This function to get location id from display location
    @param user_id:
    @param location_id:
    @param rfid:
    @param update_location:
    @return:
    """
    try:
        return CanisterMaster.activate_canister(user_id=user_id,
                                                location_id=location_id,
                                                rfid=rfid,
                                                update_location=update_location)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in activate_canister_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in activate_canister_dao {}".format(e))
        raise e


def update_replenish_based_on_system(system_id):
    try:
        device_data = DeviceMaster.db_get_robots_by_system_id(system_id,
                                                              [settings.ROBOT_SYSTEM_VERSIONS['v3']])
        if device_data:

            for device in device_data:
                batch_dict = {
                    "device_id": device['id'],
                    "system_id": device['system_id']
                }
                get_replenish_mini_batch_wise(batch_dict)
    except DoesNotExist as e:
        logger.error("error in update_replenish_based_on_system {}".format(e))
        return True
    except (InternalError, IntegrityError) as e:
        logger.error("error in update_replenish_based_on_system {}".format(e))
        raise e
    except ValueError as e:
        logger.error("error in update_replenish_based_on_system {}".format(e))
        raise e

@log_args_and_response
def get_canister_threshold_value_by_rfids(rfids):
    """
    Returns threshold value for given rfids of canister
    ``
    @param rfids: list
    @return: dict
    """

    logger.info("Inside the get_canister_threshold_value_by_rfids")

    rfids = set(rfids)
    parameters = dict()

    if not rfids:
        return parameters

    try:
        select_fields = [CanisterMaster.rfid, CanisterMaster.threshold]

        query = CanisterMaster.select(*select_fields).\
            where(CanisterMaster.rfid << list(rfids))

        for items in query.dicts():
            if items['threshold'] is None:
                parameters[items['rfid']] = None
            else:
                parameters[items['rfid']] = {"threshold": items['threshold']}

        return parameters
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_canister_threshold_value_by_rfids {}".format(e))
        raise

@log_args_and_response
def get_canister_parameter_by_rfids(rfids):
    """
    Returns canister parameters given rfids of canisters
    ``
    :param rfids: list
    :return: dict
    """
    rfids = set(rfids)
    parameters = dict()
    if not rfids:
        return parameters

    try:
        select_fields = [
            CanisterParameters.speed,
            CanisterParameters.wait_timeout,
            CanisterParameters.cw_timeout,
            CanisterParameters.ccw_timeout,
            CanisterParameters.drop_timeout,
            CanisterParameters.pill_wait_time,
            CanisterMaster.rfid,
            CanisterMaster.id.alias('canister_id'),
            LocationMaster.device_id,
            LocationMaster.location_number,
            LocationMaster.is_disabled.alias('is_location_disabled'),
        ]
        base_query = CanisterMaster.select(*select_fields) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                  & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, DeviceTypeMaster.id == DeviceMaster.device_type_id)
        query1 = base_query.join(DrugCanisterParameters, on=UniqueDrug.id == DrugCanisterParameters.unique_drug_id) \
            .join(CanisterParameters, on=CanisterParameters.id == DrugCanisterParameters.canister_parameter_id)

        _set_canister_parameters(query1, rfids, parameters)

        if rfids:
            query2 = base_query.join(DrugDimension, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .join(DrugCanisterStickMapping, on=DrugCanisterStickMapping.drug_dimension_id == DrugDimension.id) \
                .join(CanisterStick, on=CanisterStick.id == DrugCanisterStickMapping.canister_stick_id) \
                .join(SmallCanisterStick, on=SmallCanisterStick.id == CanisterStick.small_canister_stick_id) \
                .join(SmallStickCanisterParameters,
                      on=SmallStickCanisterParameters.small_stick_id == SmallCanisterStick.id) \
                .join(CanisterParameters,
                      on=CanisterParameters.id == SmallStickCanisterParameters.canister_parameter_id)
            _set_canister_parameters(query2, rfids, parameters)

        if rfids:
            query3 = base_query.join(DrugDimension, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .join(CustomDrugShape, on=CustomDrugShape.id == DrugDimension.shape) \
                .join(CustomShapeCanisterParameters,
                      on=CustomDrugShape.id == CustomShapeCanisterParameters.custom_shape_id) \
                .join(CanisterParameters,
                      on=CanisterParameters.id == CustomShapeCanisterParameters.canister_parameter_id)
            _set_canister_parameters(query3, rfids, parameters)
        return parameters
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_canister_parameter_by_rfids {}".format(e))
        raise


@log_args_and_response
def _set_canister_parameters(query, rfids, parameters):
    """
    This helper functions iterates and
    removes rfid from `rfids` for which canister parameter is available in `query`.
    Canister parameter will be set in `parameters`

    @param query: query to iterate, must have rfid column selected
    @param rfids: set of rfids which needs
    @param parameters: dict to set parameters, key will be rfid
    """
    try:
        query = query.where(CanisterMaster.rfid << list(rfids))
        for record in query.dicts():
            rfids.remove(record['rfid'])
            parameters[record['rfid']] = record
    except Exception as e:
        logger.error("error in _set_canister_parameters {}".format(e))
        raise


@log_args_and_response
def get_ordered_packs_of_batch(system_id: int, device_ids: list) -> list:
    try:
        # get that packs which are assign to particular system from pack_queue table >>
        # removed batch id condition as PackQueue has that packs
        pack_order_query = PackDetails.select().dicts() \
            .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
                                    (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(PackDetails.system_id == system_id,
                   PackAnalysisDetails.device_id << device_ids) \
            .order_by(PackDetails.order_no) \
            .group_by(PackDetails.id)
        return list(pack_order_query)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_ordered_packs_of_batch {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_ordered_packs_of_batch {}".format(e))
        raise


@log_args_and_response
def get_replenish_mini_batch_wise(batch_dict):
    """
    divides packs in mini batches and assigns replenish batch according to replenish required in mini batch.
    @param batch_dict:
    @return:
    """
    logger.info('in_update_replenish_queue')
    device_id = batch_dict["device_id"]
    # batch_id = batch_dict["batch_id"]
    # batch_name = batch_dict["batch_name"]
    system_id = batch_dict["system_id"]
    canister_id_set = set()
    canister_dict = dict()
    batch_to_be_highlited = list()
    canister_list = list()
    pack_order_set =set()
    txr_list = []
    try:
        # ordered_packs = get_ordered_packs_of_batch(system_id=system_id,device_ids=[device_id])

        batch_pack_dicts = dict()
        # batch_pack_order_dicts = dict()
        # pack_ids = [record['id'] for record in ordered_packs]
        # pack_order_no = [record["order_no"] for record in ordered_packs]
        # pack_status_list = [record['pack_status'] for record in ordered_packs]
        # mini_batch_packs = []

        first_mini_batch_packs, remaining_packs = get_first_mini_batch_packs(system_id, [device_id])
        logger.info(f"In get_replenish_mini_batch_wise, first_mini_batch_packs count: {len(first_mini_batch_packs)}")
        first_mini_batch_pack_list = [data[0] for data in first_mini_batch_packs]
        first_mini_batch_pack_order = [data[2] for data in first_mini_batch_packs]
        # user wants always red colour for first mini batch so commenting bellow code
        # first_mini_batch_pack_status = [int(data[1]) for data in first_mini_batch_packs]
        # if set(first_mini_batch_pack_status).intersection({settings.PROGRESS_PACK_STATUS}):
        #     batch_to_be_highlited = [1, 2]
        # else:
        #     batch_to_be_highlited = [1]

        mini_batch_id = 1
        if first_mini_batch_pack_list:
            # mini_batch_id += 1
            batch_pack_dicts[mini_batch_id] = first_mini_batch_pack_list

        #TODO:  if we want replenish canister for all mini batch >>  uncomment below code.

        remaining_pack_list = [data[0] for data in remaining_packs]
        print(f"len(remaining_pack_list): {len(remaining_pack_list)}")
        for i in range(0, len(remaining_pack_list), settings.MINI_BATCH_PACK_COUNT):
            mini_batch_id += 1
            current_mini_batch_packs = remaining_pack_list[i: i + settings.MINI_BATCH_PACK_COUNT]
            batch_pack_dicts[mini_batch_id] = current_mini_batch_packs
        if batch_pack_dicts:
            batch_to_be_highlited = [1, 2]
            logger.info(f"in get_replenish_mini_batch_wise, batch_to_be_highlited: {batch_to_be_highlited}")

        #     current_mini_batch_packs = pack_ids[i: i + settings.MINI_BATCH_PACK_COUNT]
        #     pack_status = set(pack_status_list[i: i + settings.MINI_BATCH_PACK_COUNT])
        #     if pack_status.intersection((settings.DONE_PACK_STATUS, settings.PROGRESS_PACK_STATUS)):
        #         batch_to_be_highlited = [1, 2]
        #     if pack_status.intersection((settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS)):
        #         mini_batch_id += 1
        #         batch_pack_dicts[mini_batch_id] = current_mini_batch_packs
        #         batch_pack_order_dicts[mini_batch_id] = pack_order_no[i: i + settings.MINI_BATCH_PACK_COUNT]
        # if not batch_to_be_highlited:
        #     batch_to_be_highlited = [1]
        # total_mini_batches = len(batch_pack_dicts)
        # logger.info("total_mini_batches: " + str(total_mini_batches))
        # print('pack_ids_before: ', pack_ids)
        if not batch_pack_dicts:
            response = {
                'canister_list': [],
                'batch_to_be_highlited': [],
                'pending_packs': 0,
                'current_batch_processing_time': 0,
                'device_id': device_id,
                'time_update': 0,
                'blink_timer': False,
                'batch_id': None,
                'batch_name': None,
            }
            status, data = update_replenish_queue_count(response, system_id, device_id)
            if not status:
                raise ValueError('Error in updating couch-db')
            # if system_id in settings.MINI_BATCH_NOTIFICATION_DICT and \
            #         device_id in settings.MINI_BATCH_NOTIFICATION_DICT[system_id] and \
            #         batch_id in settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id]:
            #     removed_value = settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id].pop(batch_id)
            #     logger.info("removed notification_info of batch {} from MINI_BATCH_NOTIFICATION_DICT: {}"
            #                 .format(batch_id, removed_value))
            return response

        # logger.info('pack_list_pending' + str(pack_ids))
        logger.info('batch_pack_dicts' + str(batch_pack_dicts))

        current_batch_processing_time, pending_packs, timer_update, blink_timer = db_get_drop_time(
            device_ids=[device_id], system_id=system_id,
            pack_ids=batch_pack_dicts.get(1, batch_pack_dicts.get(2)))
        logger.info("current_batch_processing_time: " + str(current_batch_processing_time))
        replenish_canisters = db_get_replenish_canisters(system_id, [device_id])
        if replenish_canisters:
            for m_batch_id, pack_ids in batch_pack_dicts.items():
                # replenish_query = PackAnalysisDetails.db_get_replenish_query(batch_id, system_id, pack_ids,
                # [device_id], replenish_canisters=replenish_canisters)
                replenish_query = get_replenish_query_batch(system_id=system_id,
                                                            device_ids=[device_id],
                                                            replenish_canisters=replenish_canisters,
                                                            pack_ids=pack_ids)

                for record in replenish_query:
                    txr_list.append(record['txr'])
                    if record['location_number'] == None:
                        record['location_number'] = 0

                    if not canister_dict.get(record['canister_id'], None):
                        # record['current_batch_replenish_required_quantity'] = float(abs(record['replenish_qty']))
                        record['current_batch_required_quantity'] = float(abs(record['required_qty']))
                        canister_dict[record['canister_id']] = record

                    else:
                        canister_dict[record['canister_id']]['current_batch_required_quantity'] += float(
                            abs(record['required_qty']))
                        # canister_dict[record['canister_id']]['current_batch_replenish_required_quantity'] = \
                        #     canister_dict[record['canister_id']]['current_batch_required_quantity'] - record[
                        #         'available_quantity']

                    # Assign canister to mini batch based on replenish requirement.>>
                    # If required qty < available qty --> wait for another mini batch
                    # And also assign max_remaining_replenish_time
                    if record['canister_id'] not in canister_id_set and canister_dict[record['canister_id']]['current_batch_required_quantity'] > record['available_quantity']:

                        canister_dict[record['canister_id']]['batch_number'] = m_batch_id
                        canister_dict[record['canister_id']]['pack_order_no_ref'] = record["pack_order_no"]
                        canister_dict[record['canister_id']].setdefault("max_remaining_replenish_time", None)
                        # canister_dict[record['canister_id']]["max_remaining_replenish_time"] = get_max_remaining_replenish_time(batch_id=batch_id,
                        #                                                                        canister_id=record['canister_id'],
                        #                                                                        system_id=system_id,
                        #                                                                        device_ids=[device_id],
                        #                                                                        pack_ids=pack_ids)
                        canister_id_set.add(record['canister_id'])
                        # for i,order_no in batch_pack_order_dicts:
                        #     if record["canister_id"] not in canister_id_set:
                        #         if order_no not in pack_canister_dict:
                        #             pack_canister_dict.setdefault(order_no, set())
                        #
                        #             pack_canister_dict[order_no].add(record["canister_id"])
                        # if record["pack_order_no"] not in pack_canister_dict:
                        #     pack_canister_dict[record["pack_order_no"]] = [record["canister_id"]]
                        # else:
                        #     pack_canister_dict[record["pack_order_no"]].append(record["canister_id"])
                        pack_order_set.add(record["pack_order_no"])

                    canister_dict[record['canister_id']]['batch_required_quantity'] = float(abs(record['required_qty']))
                    canister_dict[record['canister_id']]['replenish_required_quantity'] = float(
                        abs(record['replenish_qty']))


                    # fetch canister capacity based on approx_volume of drug
                    if record['approx_volume'] is None:
                        canister_dict[record['canister_id']]['canister_capacity'] = None
                    else:
                        canister_volume = get_canister_volume(canister_type=record['canister_type'])
                        canister_dict[record['canister_id']][
                            'canister_capacity'] = get_max_possible_drug_quantities_in_canister(
                            canister_volume=canister_volume,
                            unit_drug_volume=record['approx_volume'])

                    logger.info("can capacity data {}, {}".format(record['approx_volume'],
                                                                  canister_dict[record['canister_id']]))
                    del record['approx_volume']
                    del record['replenish_qty']
                    del record['required_qty']

            # fetch the required and replenish qty. for the current and upcoming batch
            inventory_data = get_fndc_txr_wise_inventory_qty(txr_list)

            replenish_query = get_replenish_query_batch(system_id=system_id,
                                                        device_ids=[device_id],
                                                        replenish_canisters=list(canister_dict.keys()))
            for record in replenish_query:
                canister_dict[record['canister_id']]['inventory_qty'] = inventory_data.get(
                    (record['formatted_ndc'], record['txr']), 0)
                canister_dict[record['canister_id']]['is_in_stock'] = 0 if canister_dict[record['canister_id']][
                                                                               'inventory_qty'] == 0 else 1
                canister_dict[record['canister_id']]['batch_required_quantity'] = float(abs(record['required_qty']))
                canister_dict[record['canister_id']]['replenish_required_quantity'] = float(
                    abs(record['replenish_qty']))

            logger.info(f"pack_order_set: {pack_order_set}")
            pack_order_drop_no_list, first_mini_batch_drops = get_max_remaining_replenish_time(pack_order_no=max(pack_order_set),
                                                                       system_id=system_id,
                                                                       device_ids=[device_id],
                                                                       first_mini_batch_pack_order=first_mini_batch_pack_order)
            logger.info(f"pack_order_drop_no_list: {pack_order_drop_no_list}")
            first_mini_batch_time = len(first_mini_batch_drops) * settings.PER_DROP_TIME
            logger.info(f"In get_replenish_mini_batch_wise, first_mini_batch_time: {first_mini_batch_time}")
            # Todo: need to check for required pack id, need to check for packs before j["pack_order_no"]
            try:
                for i,j in canister_dict.items():
                    logger.info(f"canister_info: {j}")
                    if j["pack_order_no_ref"] in first_mini_batch_pack_order:
                        for drop in first_mini_batch_drops:
                            order_no = drop.split("#")
                            if j["pack_order_no_ref"] > int(order_no[0]):
                                index =first_mini_batch_drops.index(drop)
                                total_drops = len(first_mini_batch_drops[index:])
                                canister_dict[i]["max_remaining_replenish_time"] = (total_drops * settings.PER_DROP_TIME)
                                break
                    else:
                        for drop in pack_order_drop_no_list:
                            order_no = drop.split("#")
                            if j["pack_order_no_ref"] > int(order_no[0]):
                                index =pack_order_drop_no_list.index(drop)
                                total_drops = len(pack_order_drop_no_list[index:])
                                canister_dict[i]["max_remaining_replenish_time"] = (total_drops * settings.PER_DROP_TIME) + first_mini_batch_time
                                break
            except Exception as e:
                logger.error(f"Error in get_replenish_mini_batch_wise in calculating time : {e}")

            canister_list = sorted(list(canister_dict.values()), key=lambda index: (index['batch_number'],
                                                                                    index['location_number']))
        response = {
            'canister_list': canister_list,
            'batch_to_be_highlited': batch_to_be_highlited,
            'pending_packs': pending_packs,
            'current_batch_processing_time': current_batch_processing_time,
            'device_id': device_id,
            'time_update': timer_update,
            'blink_timer': blink_timer,
            'batch_name': None,
            'batch_id': None
        }
        status, data = update_replenish_queue_count(response, system_id, device_id)
        if not status:
            raise ValueError('Error in updating couch-db')

        logger.info("adding notification if required")
        # notification_status, notification_response = send_notification_for_current_batch(batch_id,
        #                                                                                  current_batch_processing_time,
        #                                                                                  device_id, system_id,
        #                                                                                  total_mini_batches)
        # logger.info("In get_replenish_mini_batch_wise: notification_status: {}, notification_response: {}"
        #             .format(notification_status, notification_response))

        return response

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_replenish_mini_batch_wise {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_replenish_mini_batch_wise: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_replenish_mini_batch_wise {}".format(e))
        raise e


@log_args_and_response
def get_max_remaining_replenish_time(pack_order_no, system_id, device_ids, first_mini_batch_pack_order=None):
    try:
        logger.info("Inside get_max_remaining_replenish_time")
        max_remaining_replenish_time = None
        drop_list = []
        first_mini_batch_drops = []
        # clauses_for_order_no: list = list()
        # pack_order_no = None
        # clauses_for_order_no.append(PackAnalysis.batch_id == batch_id)
        # clauses_for_order_no.append(PackAnalysisDetails.canister_id == canister_id)
        # clauses_for_order_no.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
        # clauses_for_order_no.append(PackDetails.system_id == system_id)
        # clauses_for_order_no.append(PackDetails.id << pack_ids)
        #
        # logger.info(
        #     f"In get_max_remaining_replenish_time, fetch minimum pack order no. from pack_ids: {pack_ids} to replenish canister: {canister_id} ")
        #
        # pack_order_query = PackAnalysis.select(PackDetails.order_no).dicts() \
        #             .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
        #             .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
        #             .where(*clauses_for_order_no) \
        #             .group_by(PackAnalysis.pack_id) \
        #             .order_by(PackDetails.order_no)
        #
        # for record in pack_order_query:
        #     pack_order_no = record['order_no']
        #     break

        logger.info(f"In get_max_remaining_replenish_time, pack_order_no: {pack_order_no}")
        if pack_order_no:
            clauses: list = list()

            clauses.append(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS])
            clauses.append(PackDetails.system_id == system_id)
            clauses.append(PackDetails.order_no < pack_order_no)

            mfd_clauses = clauses.copy()
            mfd_clauses.append((MfdAnalysis.dest_device_id << device_ids))
            clauses.append(PackAnalysisDetails.device_id << device_ids)
            clauses.append(PackAnalysisDetails.canister_id.is_null(False))

            query = PackDetails.select(PackAnalysis.pack_id,
                                       fn.CONCAT(PackDetails.order_no, '#', PackAnalysisDetails.drop_number).coerce(
                                           False).alias('pack_drop'),
                                       PackAnalysisDetails.drop_number).dicts() \
                .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
                                        (PackAnalysis.batch_id == PackDetails.batch_id))) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
                .where(functools.reduce(operator.and_, clauses)) \
                .group_by(PackAnalysis.pack_id, PackAnalysisDetails.drop_number)
            logger.info(f"In get_max_remaining_replenish_time, query: {query}")

            # mfd_query = get_unique_mfd_drop(mfd_clauses)
            mfd_query = MfdAnalysis.select(fn.CONCAT(PackDetails.order_no, '#', MfdAnalysisDetails.drop_number)
                                       .coerce(False).alias('pack_drop'),
                                       SlotHeader.pack_id).dicts() \
                .join(MfdAnalysisDetails, on=(MfdAnalysisDetails.analysis_id == MfdAnalysis.id)) \
                .join(SlotDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
                .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
                .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id) \
                .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
                .where(functools.reduce(operator.and_, mfd_clauses))
            mfd_query = mfd_query.group_by(SlotHeader.pack_id, MfdAnalysisDetails.drop_number)
            # logger.info(f"In get_max_remaining_replenish_time, mfd_query: {mfd_query.dicts()}, {list(mfd_query)}")

            drops = set()
            for record in query:
                drops.add(record['pack_drop'])
            for record in mfd_query:
                drops.add(record['pack_drop'])

            logger.info(f"In get_max_remaining_replenish_time, total_drops : {len(drops)}")

            # max_remaining_replenish_time = len(list(drops)) * settings.PER_DROP_TIME
            #
            # logger.info(f"In get_max_remaining_replenish_time, max_remaining_replenish_time:{max_remaining_replenish_time}")
            drop_list = sorted(list(drops), key=lambda index:(int(index.split("#")[0]), int(index.split("#")[1])), reverse=True)

            if first_mini_batch_pack_order:
                first_mini_batch_pack_order.sort(reverse=True)
                drop_list_copy = deepcopy(drop_list)
                for pack_drop in drop_list_copy:
                    pack_drop_list = pack_drop.split("#")
                    if int(pack_drop_list[0]) in first_mini_batch_pack_order:
                        drop_list.remove(pack_drop)
                        first_mini_batch_drops.append(pack_drop)

        return drop_list, first_mini_batch_drops

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_max_remaining_replenish_time {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_max_remaining_replenish_time: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_max_remaining_replenish_time {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_max_remaining_replenish_time: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


def send_notification_for_current_batch(batch_id, current_batch_processing_time, device_id, system_id,
                                        total_mini_batches):
    if not system_id in settings.MINI_BATCH_NOTIFICATION_DICT:
        logger.info("adding system_id {} in MINI_BATCH_NOTIFICATION_DICT".format(system_id))
        settings.MINI_BATCH_NOTIFICATION_DICT[system_id] = dict()
    if not device_id in settings.MINI_BATCH_NOTIFICATION_DICT[system_id]:
        logger.info("adding device_id {} in MINI_BATCH_NOTIFICATION_DICT".format(device_id))
        settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id] = dict()
    if not batch_id in settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id]:
        logger.info("adding batch_id {} in MINI_BATCH_NOTIFICATION_DICT".format(batch_id))
        settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id][batch_id] = dict()

    logger.info("check for replenish notification")
    try:
        # send voice notification if current mini batch remaining processing time 15 minutes
        if current_batch_processing_time <= settings.VOICE_NOTIFICATION_MINI_BATCH_PROCESSING_TIME_LEFT_2 and \
                (not settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id][batch_id] or
                 not settings.MINI_BATCH_15_MIN_LEFT_CODE in
                     settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id][batch_id] or
                 settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id][batch_id][
                     settings.MINI_BATCH_15_MIN_LEFT_CODE] != total_mini_batches):
            try:
                logger.info("fetching device_info for device_id {}".format(device_id))
                device_info = DeviceMaster.db_get_by_id(device_id=device_id)
                logger.info("device_info {} for device_id {}".format(device_info, device_id))
            except (InternalError, DoesNotExist) as e:
                logger.error("error in get_latest_adjusted_canister_record_by_canister_id {}".format(e))
                return False, str(e)

            logger.info("adding replenish notification: 15 minutes left for current mini batch {}, batch {}"
                        .format(total_mini_batches, batch_id))
            status, data = publish_voice_notification(component_device_code=settings.DPWS_COMPONENT_DEVICE_CODE,
                                                      notification_code=settings.MINI_BATCH_15_MIN_LEFT_CODE,
                                                      system_id=system_id, device_id=device_id,
                                                      device_name=device_info.name)
            if status:
                logger.info("replenish notification added: 15 minutes left for current mini batch {}, batch {}"
                            .format(total_mini_batches, batch_id))
                settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id][batch_id][
                    settings.MINI_BATCH_15_MIN_LEFT_CODE] = total_mini_batches
                return True, data
            else:
                logger.info(
                    "Error in adding replenish notification: 15 minutes left for mini batch {} of batch {}"
                        .format(total_mini_batches, batch_id))
                return False, data
        # send voice notification if current mini batch remaining processing time is between 15 minutes and 30 minutes
        elif current_batch_processing_time in range(settings.VOICE_NOTIFICATION_MINI_BATCH_PROCESSING_TIME_LEFT_2 + 1,
                                                    settings.VOICE_NOTIFICATION_MINI_BATCH_PROCESSING_TIME_LEFT_1 + 1) and \
                (not settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id][batch_id] or
                 not settings.MINI_BATCH_30_MIN_LEFT_CODE in
                     settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id][batch_id] or
                 settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id][batch_id]
                 [settings.MINI_BATCH_30_MIN_LEFT_CODE] != total_mini_batches):
            try:
                logger.info("fetching device_info for device_id {}".format(device_id))
                device_info = DeviceMaster.db_get_by_id(device_id=device_id)
                logger.info("device_info {} for device_id {}".format(device_info, device_id))
            except (InternalError, DoesNotExist) as e:
                logger.error("error in get_latest_adjusted_canister_record_by_canister_id {}".format(e))
                return False, str(e)

            logger.info("adding replenish notification: 30 minutes left for mini batch {} of batch {}"
                        .format(total_mini_batches, batch_id))
            status, data = publish_voice_notification(component_device_code=settings.DPWS_COMPONENT_DEVICE_CODE,
                                                      notification_code=settings.MINI_BATCH_30_MIN_LEFT_CODE,
                                                      system_id=system_id, device_id=device_id,
                                                      device_name=device_info.name)
            if status:
                logger.info("replenish notification added: 30 minutes left for mini batch {} of batch {}"
                            .format(total_mini_batches, batch_id))
                settings.MINI_BATCH_NOTIFICATION_DICT[system_id][device_id][batch_id][settings.MINI_BATCH_30_MIN_LEFT_CODE] = total_mini_batches
                return True, data
            else:
                logger.info(
                    "Error in adding replenish notification: 30 minutes left for current mini batch {} of batch {}"
                        .format(total_mini_batches, batch_id))
                return True, data
        else:
            logger.info("No need to add replenish notification right now for mini batch {} of batch."
                        .format(total_mini_batches, batch_id))
            return True, None
    except Exception as e:
        logger.error("error in send_notification_for_current_batch {}".format(e))
        return False, str(e)


@log_args_and_response
def db_get_replenish_canisters(system_id, device_ids):
    """
    Method to fetch replenish required canisters
    @param batch_id:
    @param system_id:
    @param device_ids:
    @return:
    """
    replenish_required_canisters = list()
    # adding packs which are in progress but yet not processed by robot.
    pack_id_query = PackDetails.select(PackDetails,
                                       PackDetails.id.alias('pack_id')).dicts() \
        .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.pack_id == PackDetails.id) \
        .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
        .where(PackDetails.pack_status == settings.PROGRESS_PACK_STATUS,
               SlotTransaction.id.is_null(True))
    pack_ids = [record['pack_id'] for record in pack_id_query]
    logger.info("In db_get_progress_filling_left_pack_ids, pack_id_query {}".format(pack_id_query))
    pack_clause = list()
    if pack_ids:
        pack_clause.append((PackDetails.pack_status == settings.PENDING_PACK_STATUS) |
                           (PackDetails.id << pack_ids))
    else:
        pack_clause.append(PackDetails.pack_status == settings.PENDING_PACK_STATUS)
    # pack_clause.append(PackDetails.id << pack_ids)
    try:
        replenish_query = PackDetails.select(PackAnalysisDetails.canister_id,
                                             LocationMaster.id.alias("can_location_id"),
                                             LocationMaster.display_location,
                                             ContainerMaster.drawer_name.alias('drawer_number'),
                                             LocationMaster.quadrant,
                                             DeviceMaster.device_type_id,
                                             DeviceMaster.serial_number,
                                             DrugMaster.ndc,
                                             DeviceMaster.id,
                                             DrugMaster.image_name,
                                             LocationMaster.location_number,
                                             DeviceMaster.id.alias("device_id"),
                                             DeviceMaster.name.alias('device_name'),
                                             CanisterMaster.available_quantity,
                                             (fn.SUM(fn.FLOOR(SlotDetails.quantity)) -
                                              CanisterMaster.available_quantity).alias('replenish_qty'),
                                             fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('required_qty'),
                                             DrugMaster.concated_drug_name_field().alias('drug_name'),
                                             CanisterMaster.canister_type,
                                             ContainerMaster.drawer_level).dicts() \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(pack_clause,
                   PackDetails.system_id == system_id,
                   PackAnalysisDetails.device_id << device_ids,
                   PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED
                   ) \
            .group_by(PackAnalysisDetails.canister_id).having(
            fn.SUM(fn.FLOOR(SlotDetails.quantity)) > CanisterMaster.available_quantity)

        for record in replenish_query:
            replenish_required_canisters.append(record['canister_id'])
        return replenish_required_canisters
    except (InternalError, IntegrityError) as e:
        logger.error("error in db_get_replenish_canisters {}".format(e))
        raise e


@log_args_and_response
def get_replenish_query_batch(system_id: int, device_ids: list, replenish_canisters: list,
                              pack_ids: list = None):
    """
    Method to fetch replenish data of canisters for current and upcoming batch
    @param batch_id:
    @param replenish_canisters:
    @param system_id:
    @param device_ids:
    @param pack_ids:
    @return:

    """
    pack_clause: list = list()
    try:
        # adding packs which are in progress but yet not processed by robot.
        progress_pack_ids = db_get_progress_filling_left_pack_ids()
        # if progress_pack_ids:
        #     pack_clause.append((PackDetails.pack_status == settings.PENDING_PACK_STATUS) |
        #                        (PackDetails.id << progress_pack_ids))
        # else:
        #     pack_clause.append(PackDetails.pack_status == settings.PENDING_PACK_STATUS)
        #
        # if pack_ids:
        #     pack_clause.append(PackDetails.id << pack_ids)

        if pack_ids:
            pack_clause.append(PackDetails.id << pack_ids)
        else:
            if progress_pack_ids:
                pack_clause.append((PackDetails.pack_status == settings.PENDING_PACK_STATUS) |
                                   (PackDetails.id << progress_pack_ids))
            else:
                pack_clause.append(PackDetails.pack_status == settings.PENDING_PACK_STATUS)

        replenish_query = PackDetails.select(PackAnalysisDetails.canister_id,
                                             fn.MIN(PackDetails.order_no).alias("pack_order_no"),
                                             LocationMaster.id.alias("can_location_id"),
                                             LocationMaster.display_location,
                                             ContainerMaster.drawer_name.alias('drawer_number'),
                                             LocationMaster.quadrant,
                                             DeviceMaster.device_type_id,
                                             DeviceMaster.serial_number,
                                             DrugMaster.ndc,
                                             DeviceMaster.id,
                                             DrugMaster.image_name,
                                             DrugMaster.shape,
                                             DrugMaster.imprint,
                                             fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                                   DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                             DrugDetails.last_seen_by.alias("last_seen_with"),
                                             LocationMaster.location_number,
                                             DeviceMaster.id.alias("device_id"),
                                             DeviceMaster.name.alias('device_name'),
                                             CanisterMaster.available_quantity,
                                             (fn.SUM(fn.FLOOR(SlotDetails.quantity)) -
                                              CanisterMaster.available_quantity).alias('replenish_qty'),
                                             fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('required_qty'),
                                             DrugMaster.concated_drug_name_field().alias('drug_name'),
                                             CanisterMaster.canister_type,
                                             ContainerMaster.drawer_level,
                                             CanisterMaster.drug_id.alias('canister_drug_id'),
                                             fn.IF(
                                                 CanisterMaster.expiry_date <= date.today() + timedelta(
                                                     settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                                 constants.EXPIRED_CANISTER,
                                                 fn.IF(
                                                     CanisterMaster.expiry_date <= date.today() + timedelta(
                                                         settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                                     constants.EXPIRES_SOON_CANISTER,
                                                     constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                             DrugMaster.formatted_ndc,
                                             DrugMaster.txr,
                                             UniqueDrug.is_powder_pill,
                                             DrugDimension.approx_volume,
                                             UniqueDrug.is_delicate
                                             ).dicts() \
            .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
                                    (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                   (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == 1) &
                                                         (DrugStockHistory.company_id == PackDetails.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id))) \
            .join(LocationMaster,JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster,JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster,JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(pack_clause,
                   (PackDetails.system_id == system_id),
                   (PackAnalysisDetails.device_id << device_ids),
                   PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)

        if replenish_canisters:
            replenish_query = replenish_query.where(PackAnalysisDetails.canister_id << replenish_canisters)
        replenish_query = replenish_query.group_by(PackAnalysisDetails.canister_id).order_by(PackDetails.order_no)

        # logger.info(f"In get_replenish_query_batch, replenish_query: {list(replenish_query)}")

        return replenish_query
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_replenish_query_batch {}".format(e))
        raise e


def update_replenish_based_on_device(device_id):
    try:
        logger.info("in_updating_replenish_queue_via_device")
        device_data = DeviceMaster.get_device_data(device_id, settings.DEVICE_TYPES['ROBOT'],
                                                   [settings.ROBOT_SYSTEM_VERSIONS['v3']])
        if device_data:

            pack_queue_packs = get_packs_from_pack_queue_for_system(system_id=device_data["system_id"])

            logger.info("updating_replenish_queue_via_device")
            if pack_queue_packs:
                batch_dict = {
                    "device_id": device_id,
                    "system_id": device_data["system_id"]
                }
                get_replenish_mini_batch_wise(batch_dict)

                # t = threading.Thread(target=get_replenish_mini_batch_wise, args=(batch_dict,))
                # logger.info(f"In update_replenish_based_on_device, threading start")
                # t.start()

    except DoesNotExist as e:
        logger.error("error in update_replenish_based_on_device {}".format(e))
        return None
    except (InternalError, IntegrityError) as e:
        logger.error("error in update_replenish_based_on_device {}".format(e))
        return error(2001, e)
    except ValueError as e:
        return error(2005, str(e))


@log_args_and_response
def update_canister_movement(canister_id, drug_id, new_canister_number, new_device_id, user_id, zone_id=None):
    """
    Updates canisters location_id and creates canister history for given canister

    :param canister_id: The cansiter id
    :param drug_id: The drug id of drug in canister
    :param new_canister_number: Canister number to be updated
    :param new_device_id: Robot id to be updated
    :param action: Canister history action
    :param user_id: User id of user who is updating

    :return: bool, CanisterHistory  (update status of canister, caniser_history_record)
    """
    canister_data = CanisterMaster.get(id=canister_id)
    old_location_id = canister_data.location_id
    new_location_id = get_location_id_by_location_number_dao(device_id=new_device_id,
                                                             location_number=new_canister_number)
    status = CanisterMaster.update(location_id=new_location_id,
                                   modified_by=user_id) \
        .where(CanisterMaster.id == canister_id).execute()

    if zone_id is not None:
        CanisterZoneMapping.update_canister_zone_mapping_by_canister_id(zone_id, user_id, canister_id)

    canister_history = create_canister_history_data(canister_id, old_location_id, new_location_id, drug_id,
                                                    user_id)
    canister_history_record = BaseModel.db_create_record(canister_history, CanisterHistory, get_or_create=False)
    return status, canister_history_record


@log_args_and_response
def create_canister_history_data(canister_id, old_location_id, new_location_id, drug_id,
                                 user_id):
    """
    Returns dictionary with required data for a record in CanisterHistory

    :return:
    """
    return {
        "canister_id": canister_id,
        "current_lcoation_id": new_location_id,
        "previous_location_id": old_location_id,
        "created_by": user_id,
        "modified_by": user_id,
    }


@log_args_and_response
def get_canister_info_data(canister_ids: list, batch_id: int, quad_drug_canister_dict: dict, quad_canisters: dict, canister_drug_info_dict: dict) -> tuple:
    try:
        query = PackAnalysis.select(fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias('drug'),
            fn.CONCAT(DrugMaster.drug_name, ' ', DrugMaster.strength_value, ' ', DrugMaster.strength).alias(
                'drug_name'),
            DrugMaster.strength,
            DrugMaster.ndc,
            CanisterMaster.id,
                                    PackAnalysisDetails.quadrant) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(CanisterMaster, on=PackAnalysisDetails.canister_id == CanisterMaster.id) \
            .join(PackDetails, on=((PackDetails.id == PackAnalysis.pack_id) &
                                   (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(PackAnalysisDetails.canister_id << canister_ids,
                   PackAnalysis.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS,
                                               settings.PROGRESS_PACK_STATUS])

        for record in query.dicts():
            if record['quadrant'] is None:
                continue
            if record['quadrant'] not in quad_canisters:
                quad_canisters[record['quadrant']] = set()
            if record['quadrant'] not in quad_drug_canister_dict:
                quad_drug_canister_dict[record['quadrant']] = {}
            if record['id'] not in canister_drug_info_dict:
                canister_drug_info_dict[record['id']] = {}
            if record['drug'] not in quad_drug_canister_dict[record['quadrant']]:
                quad_drug_canister_dict[record['quadrant']][record['drug']] = set()
            quad_drug_canister_dict[record['quadrant']][record['drug']].add(record['id'])
            quad_canisters[record['quadrant']].add(record['id'])
            canister_drug_info_dict[record['id']]['fndc_txr'] = record['drug']
            canister_drug_info_dict[record['id']]['drug_name'] = record['drug_name']
            canister_drug_info_dict[record['id']]['ndc'] = record['ndc']
        logger.info(quad_drug_canister_dict)
        logger.info(quad_canisters)
        logger.info(canister_drug_info_dict)
        return quad_drug_canister_dict, quad_canisters, canister_drug_info_dict
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_canister_info_data {}".format(e))
        raise e


def get_canister_data_by_serial_number_v3_dao(canister_data):
    try:
        query = UniqueDrug.select(DrugMaster).dicts() \
            .join(DrugMaster, on=DrugMaster.id == UniqueDrug.drug_id) \
            .where(fn.CONCAT(UniqueDrug.formatted_ndc, '##', fn.IFNULL(UniqueDrug.txr, '')) ==
                   canister_data['ndc##txr']).get()
        return query
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_canister_data_by_serial_number_v3_dao {}".format(e))
        raise e


@log_args_and_response
def get_quad_drug_req_qty_for_packs(pack_list):
    try:
        quad_drug_req_qty_dict = {}
        quad_drug_req_qty_ordered_dict = {}
        total_required_unique_drug = set()
        # quad_drug_analysis_ids = {}
        for quad in range(1, 5):
            quad_drug_req_qty_dict[quad] = OrderedDict()
            quad_drug_req_qty_ordered_dict[quad] = []
        query = PackDetails.select(
            PackAnalysisDetails.quadrant,
            fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias('drug'),
            fn.SUM(SlotDetails.quantity).alias('req_qty')
        ).join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(PackDetails.id << pack_list, PackAnalysisDetails.canister_id.is_null(False),
                   PackAnalysisDetails.quadrant.is_null(False)) \
            .group_by(PackAnalysisDetails.quadrant, DrugMaster.formatted_ndc, DrugMaster.txr) \
            .order_by(PackAnalysisDetails.quadrant, fn.SUM(SlotDetails.quantity))

        for record in query.dicts():
            # if record['quadrant'] == 4:
            #     if record['quadrant'] not in quad_drug_req_qty_dict:
            #         quad_drug_req_qty_dict[record['quadrant']] = OrderedDict()
            #     if record['quadrant'] not in quad_drug_req_qty_ordered_dict:
            #         quad_drug_req_qty_ordered_dict[record['quadrant']] = []
            #     quad_drug_req_qty_ordered_dict[record['quadrant']].append(('d1', 20.0))
            #     quad_drug_req_qty_dict[record['quadrant']]['d1'] = 20.0
            #     total_required_unique_drug.add('d1')
            if record['quadrant'] not in quad_drug_req_qty_dict:
                quad_drug_req_qty_dict[record['quadrant']] = OrderedDict()
            if record['quadrant'] not in quad_drug_req_qty_ordered_dict:
                quad_drug_req_qty_ordered_dict[record['quadrant']] = []
            quad_drug_req_qty_ordered_dict[record['quadrant']].append((record['drug'], record['req_qty']))
            quad_drug_req_qty_dict[record['quadrant']][record['drug']] = record['req_qty']
            total_required_unique_drug.add(record['drug'])

        return quad_drug_req_qty_dict, quad_drug_req_qty_ordered_dict, total_required_unique_drug

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_quad_drug_req_qty_for_packs {}".format(e))
        raise


@log_args_and_response
def get_pack_list_by_robot(batch_id: int, device_id: int) -> list:
    """
    To obtain list of packs for the given device_id
    """
    try:
        filling_pending_pack_ids = db_get_progress_filling_left_pack_ids()
        clauses = [PackAnalysisDetails.device_id == device_id,
                   PackDetails.batch_id == batch_id]
        if filling_pending_pack_ids:
            clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                           | (PackDetails.id << filling_pending_pack_ids))
        else:
            clauses.append(PackDetails.pack_status << [settings.PROGRESS_PACK_STATUS])
        pack_list = list()
        query = PackDetails.select(
            PackDetails.id
        ).join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(*clauses)
        for record in query:
            pack_list.append(record.id)
        return list(set(pack_list))
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_pack_list_by_robot {}".format(e))
        raise e


@log_args_and_response
def get_skip_canister_dao(batch_id):
    try:
        return SkippedCanister.db_get(batch_id)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_skip_canister_dao {}".format(e))
        raise e


@log_args_and_response
def get_empty_locations_count_quadwise(device_ids: list) -> dict:
    db_result = dict()
    try:
        # todo add drawer type constraint
        # applied an extra condition to fetch the empty locations that are not disabled
        query = ContainerMaster.select(ContainerMaster.id.alias('drawer_id'),
                                       LocationMaster.device_id,
                                       LocationMaster.quadrant,
                                       (fn.COUNT(fn.Distinct(LocationMaster.id)) - fn.COUNT(CanisterMaster.id))
                                       .alias('empty_locations_count'),
                                       ).dicts() \
            .join(LocationMaster, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .where((LocationMaster.device_id << device_ids), (LocationMaster.is_disabled == 0)) \
            .group_by(LocationMaster.device_id, LocationMaster.quadrant)

        for record in query:
            if record['device_id'] not in db_result.keys():
                db_result[record['device_id']] = dict()
            db_result[record['device_id']][record["quadrant"]] = record["empty_locations_count"]
        return db_result

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_empty_locations_count_of_drawers_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_empty_locations_count_of_drawers_dao {}".format(e))
        raise e


@log_args_and_response
def get_import_batch_id_from_system_id_or_device_id(system_id=None, device_id=None):

    try:
        logger.info("Inside get_import_batch_id_from_system_id")

        batch_id = None

        if not system_id:
            if device_id:
                query_for_system_id = DeviceMaster.select(DeviceMaster.system_id).dicts().where(DeviceMaster.id == device_id)
                for data in query_for_system_id:
                    system_id = data["system_id"]

        if system_id:

            query = BatchMaster.select(BatchMaster.id).dicts() \
                        .where(BatchMaster.status == settings.BATCH_IMPORTED,
                               BatchMaster.system_id == system_id) \
                        .group_by(BatchMaster.id.desc())

            logger.info(f"In get_import_batch_id_from_system_id, query: {query}")

            for data in query:
                batch_id = data["id"]

            logger.info(f"In get_import_batch_id_from_system_id, batch_id : {batch_id}")

        return batch_id

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_import_batch_id_from_system_id {}".format(e))
        raise e


@log_args_and_response
def get_skipped_replenish_canister(system_id, device_id, progress_pack_ids=None):
    try:

        clause: list = list()
        skipped_canister: list = list()

        if progress_pack_ids:
            clause.append((PackDetails.id << progress_pack_ids) | (PackDetails.pack_status == settings.PENDING_PACK_STATUS))
        else:
            clause.append(PackDetails.pack_status == settings.PENDING_PACK_STATUS)

        logger.info("In get_skipped_canister")

        # query = PackDetails.select(PackAnalysisDetails.canister_id).dicts() \
        #             .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
        #             .join(PackAnalysis, on=PackDetails.id == PackAnalysis.pack_id) \
        #             .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
        #             .where(clause,
        #                    PackDetails.system_id == system_id,
        #                    PackAnalysisDetails.device_id == device_id,
        #                    PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_SKIPPED,
        #                    PackAnalysisDetails.canister_id.is_null(False)) \
        #             .group_by(PackAnalysisDetails.canister_id)

        query = PackQueue.select(ReplenishSkippedCanister.canister_id).dicts() \
                .join(PackDetails, on=PackDetails.id == PackQueue.pack_id) \
                .join(ReplenishSkippedCanister, on=ReplenishSkippedCanister.pack_id == PackDetails.id) \
                .where(clause,
                       PackDetails.system_id == system_id,
                       ReplenishSkippedCanister.device_id == device_id) \
                .group_by(ReplenishSkippedCanister.canister_id)

        logger.info(f"In get_skipped_replenish_canister, query: {query}")

        for record in query:
            skipped_canister.append(record["canister_id"])

        logger.info(f"In get_skipped_replenish_canister, skipped_canister:{skipped_canister}")

        return skipped_canister

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_skipped_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_skipped_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)
    except Exception as e:
        logger.error("error in get_skipped_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_skipped_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_skipped_canister: " + str(e))


@log_args_and_response
def get_skipped_replenish_query(system_id, device_id, progress_pack_ids, skipped_canister, all_packs=None):

    try:
        logger.info("Inside get_skipped_replenish_query")

        pack_clause: list = list()

        if progress_pack_ids:
            pack_clause.append((PackDetails.pack_status == settings.PENDING_PACK_STATUS) |
                                   (PackDetails.id << progress_pack_ids))
        else:
            pack_clause.append(PackDetails.pack_status == settings.PENDING_PACK_STATUS)

        if all_packs:
            # This condition applied when we need required qty of canister for current + upcoming batch
            pack_clause.append(
                (BatchMaster.status == settings.BATCH_IMPORTED) | (BatchMaster.status.in_(settings.UPCOMING_BATCH_STATUS)))

        #need only those canisters which are skipped
        pack_clause.append(PackDetails.system_id == system_id)
        pack_clause.append(ReplenishSkippedCanister.device_id == device_id)

        # we need qty of all packs if user wants to replenish canister which was skipped.
        # >> so we skipp only manual packs data.
        # pack_clause.append(ReplenishSkippedCanister.status != constants.SKIPPED_DUE_TO_MANUAL_PACK)

        # This Alias will give the destination data. and PackAnalysisDetails quadrant --> dest quadrant
        DeviceMasterAlias = DeviceMaster.alias()
        # This Alias used to fetch all the drug_ids from drug_master which have same fndc##txr
        DrugMasterAlias = DrugMaster.alias()

        if not all_packs:
            # query = PackDetails.select(PackAnalysisDetails.canister_id,
            #                            CanisterMaster.canister_type,
            #                            CanisterMaster.drug_id.alias("canister_drug_id"),
            #                            fn.IF(
            #                                CanisterMaster.expiry_date <= date.today() + timedelta(
            #                                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
            #                                constants.EXPIRED_CANISTER,
            #                                fn.IF(
            #                                    CanisterMaster.expiry_date <= date.today() + timedelta(
            #                                        settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
            #                                    constants.EXPIRES_SOON_CANISTER,
            #                                    constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
            #                            LocationMaster.id.alias("can_location_id"),
            #                            LocationMaster.display_location,
            #                            LocationMaster.location_number,
            #                            LocationMaster.quadrant,
            #                            ContainerMaster.drawer_name.alias('drawer_number'),
            #                            ContainerMaster.drawer_level,
            #                            ContainerMaster.ip_address,
            #                            ContainerMaster.secondary_ip_address,
            #                            DeviceMaster.id.alias("device_id"),
            #                            DeviceMaster.device_type_id,
            #                            DeviceMaster.serial_number,
            #                            DeviceMaster.name.alias("device_name"),
            #                            DeviceMaster.ip_address.alias("device_ip_address"),
            #                            PackAnalysisDetails.quadrant.alias("dest_quadrant"),
            #                            PackAnalysisDetails.device_id.alias("dest_device_id"),
            #                            DeviceMasterAlias.id.alias("dest_device_id"),
            #                            DeviceMasterAlias.name.alias("dest_device_name"),
            #                            DeviceMasterAlias.device_type_id.alias("dest_device_type_id"),
            #                            DeviceMasterAlias.serial_number.alias("dest_serial_number"),
            #                            DeviceMasterAlias.ip_address.alias("dest_ip_address"),
            #                            DrugMaster.concated_drug_name_field().alias("drug_name"),
            #                            DrugMaster.ndc,
            #                            DrugMaster.formatted_ndc,
            #                            DrugMaster.txr,
            #                            DrugMaster.image_name,
            #                            DrugMaster.shape,
            #                            DrugMaster.imprint,
            #                            UniqueDrug.is_powder_pill,
            #                            DrugDimension.approx_volume,
            #                            DrugDetails.last_seen_by.alias("last_seen_with"),
            #                            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
            #                                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
            #                            CanisterMaster.available_quantity,
            #                            (fn.SUM(fn.FLOOR(SlotDetails.quantity)) -
            #                             CanisterMaster.available_quantity).alias('replenish_qty'),
            #                            fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias("required_qty"),
            #                            fn.MIN(PackDetails.order_no).alias("pack_order_no")
            #                            ).dicts() \
            #         .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
            #                                 (PackAnalysis.batch_id == PackDetails.batch_id))) \
            #         .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            #         .join(BatchMaster, on=BatchMaster.id == PackAnalysis.batch_id) \
            #         .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            #         .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            #         .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            #         .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
            #                                                (UniqueDrug.txr == DrugMaster.txr))) \
            #         .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            #         .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
            #                                                      (DrugStockHistory.is_active == 1) &
            #                                                      (DrugStockHistory.company_id == PackDetails.company_id))) \
            #         .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
            #                                                 (DrugDetails.company_id == PackDetails.company_id))) \
            #         .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            #         .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            #         .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id)\
            #         .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=PackAnalysisDetails.device_id == DeviceMasterAlias.id) \
            #         .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            #         .where(*pack_clause,
            #                PackAnalysisDetails.canister_id << skipped_canister) \
            #         .group_by(PackAnalysisDetails.canister_id)
            query = (PackDetails.select(ReplenishSkippedCanister.canister_id,
                                        CanisterMaster.canister_type,
                                        CanisterMaster.drug_id.alias("canister_drug_id"),
                                        fn.IF(
                                            CanisterMaster.expiry_date <= date.today() + timedelta(
                                                settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                            constants.EXPIRED_CANISTER,
                                            fn.IF(
                                                CanisterMaster.expiry_date <= date.today() + timedelta(
                                                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                                constants.EXPIRES_SOON_CANISTER,
                                                constants.NORMAL_EXPIRY_CANISTER
                                            )
                                        ).alias("expiry_status"),
                                        LocationMaster.id.alias("can_location_id"),
                                        LocationMaster.display_location,
                                        LocationMaster.location_number,
                                        LocationMaster.quadrant,
                                        ContainerMaster.drawer_name.alias('drawer_number'),
                                        ContainerMaster.drawer_level,
                                        ContainerMaster.ip_address,
                                        ContainerMaster.secondary_ip_address,
                                        DeviceMaster.id.alias("device_id"),
                                        DeviceMaster.device_type_id,
                                        DeviceMaster.serial_number,
                                        DeviceMaster.name.alias("device_name"),
                                        DeviceMaster.ip_address.alias("device_ip_address"),
                                        ReplenishSkippedCanister.quadrant.alias("dest_quadrant"),
                                        ReplenishSkippedCanister.device_id.alias("dest_device_id"),
                                        DeviceMasterAlias.id.alias("dest_device_id"),
                                        DeviceMasterAlias.name.alias("dest_device_name"),
                                        DeviceMasterAlias.device_type_id.alias("dest_device_type_id"),
                                        DeviceMasterAlias.serial_number.alias("dest_serial_number"),
                                        DeviceMasterAlias.ip_address.alias("dest_ip_address"),
                                        DrugMaster.concated_drug_name_field().alias("drug_name"),
                                        DrugMaster.ndc,
                                        DrugMaster.formatted_ndc,
                                        DrugMaster.txr,
                                        DrugMaster.image_name,
                                        DrugMaster.shape,
                                        DrugMaster.imprint,
                                        UniqueDrug.is_powder_pill,
                                        DrugDimension.approx_volume,
                                        DrugDetails.last_seen_by.alias("last_seen_with"),
                                        fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                              DrugStockHistory.is_in_stock
                                              ).alias("is_in_stock"),
                                        CanisterMaster.available_quantity,
                                        (fn.SUM(
                                            fn.FLOOR(SlotDetails.quantity)) -
                                         CanisterMaster.available_quantity
                                         ).alias('replenish_qty'),
                                        fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias("required_qty"),
                                        fn.MIN(PackDetails.order_no).alias("pack_order_no"),
                                        UniqueDrug.is_delicate).dicts() \
                     .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
                     .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
                     .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                     .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                     .join(DrugMasterAlias, on=((DrugMaster.formatted_ndc == DrugMasterAlias.formatted_ndc) &
                                                (DrugMaster.txr == DrugMasterAlias.txr)
                                                )
                           )\
                     .join(CanisterMaster, on=CanisterMaster.drug_id == DrugMasterAlias.id) \
                     .join(ReplenishSkippedCanister, on=((ReplenishSkippedCanister.canister_id == CanisterMaster.id) &
                                                    (PackDetails.id == ReplenishSkippedCanister.pack_id))) \
                     .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                       (UniqueDrug.txr == DrugMaster.txr))) \
                     .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                     .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == 1) &
                                                             (DrugStockHistory.company_id == PackDetails.company_id))) \
                     .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                        (DrugDetails.company_id == PackDetails.company_id))) \
                     .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
                     .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                     .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                     .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=ReplenishSkippedCanister.device_id == DeviceMasterAlias.id) \
                     .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
                     .where(*pack_clause,
                            ReplenishSkippedCanister.canister_id << skipped_canister) \
                     .group_by(ReplenishSkippedCanister.canister_id))
        else:
            # query = PackDetails.select(PackAnalysisDetails.canister_id,
            #                            CanisterMaster.canister_type,
            #                            CanisterMaster.drug_id.alias("canister_drug_id"),
            #                            fn.IF(
            #                                CanisterMaster.expiry_date <= date.today() + timedelta(
            #                                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
            #                                constants.EXPIRED_CANISTER,
            #                                fn.IF(
            #                                    CanisterMaster.expiry_date <= date.today() + timedelta(
            #                                        settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
            #                                    constants.EXPIRES_SOON_CANISTER,
            #                                    constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
            #                            LocationMaster.id.alias("can_location_id"),
            #                            LocationMaster.display_location,
            #                            LocationMaster.location_number,
            #                            LocationMaster.quadrant,
            #                            ContainerMaster.drawer_name.alias('drawer_number'),
            #                            ContainerMaster.drawer_level,
            #                            ContainerMaster.ip_address,
            #                            ContainerMaster.secondary_ip_address,
            #                            DeviceMaster.id.alias("device_id"),
            #                            DeviceMaster.device_type_id,
            #                            DeviceMaster.serial_number,
            #                            DeviceMaster.name.alias("device_name"),
            #                            DeviceMaster.ip_address.alias("device_ip_address"),
            #                            PackAnalysisDetails.quadrant.alias("dest_quadrant"),
            #                            PackAnalysisDetails.device_id.alias("dest_device_id"),
            #                            DeviceMasterAlias.id.alias("dest_device_id"),
            #                            DeviceMasterAlias.name.alias("dest_device_name"),
            #                            DeviceMasterAlias.device_type_id.alias("dest_device_type_id"),
            #                            DeviceMasterAlias.serial_number.alias("dest_serial_number"),
            #                            DeviceMasterAlias.ip_address.alias("dest_ip_address"),
            #                            DrugMaster.concated_drug_name_field().alias("drug_name"),
            #                            DrugMaster.ndc,
            #                            DrugMaster.formatted_ndc,
            #                            DrugMaster.txr,
            #                            DrugMaster.image_name,
            #                            DrugMaster.shape,
            #                            DrugMaster.imprint,
            #                            UniqueDrug.is_powder_pill,
            #                            DrugDimension.approx_volume,
            #                            DrugDetails.last_seen_by.alias("last_seen_with"),
            #                            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
            #                                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
            #                            CanisterMaster.available_quantity,
            #                            (fn.SUM(fn.FLOOR(SlotDetails.quantity)) -
            #                             CanisterMaster.available_quantity).alias('replenish_qty'),
            #                            fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias("required_qty"),
            #                            fn.MIN(PackDetails.order_no).alias("pack_order_no")
            #                            ).dicts() \
            #     .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
            #                             (PackAnalysis.batch_id == PackDetails.batch_id))) \
            #     .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            #     .join(BatchMaster, on=BatchMaster.id == PackAnalysis.batch_id) \
            #     .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            #     .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            #     .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            #     .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
            #                                            (UniqueDrug.txr == DrugMaster.txr))) \
            #     .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            #     .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
            #                                                  (DrugStockHistory.is_active == 1) &
            #                                                  (DrugStockHistory.company_id == PackDetails.company_id))) \
            #     .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
            #                                             (DrugDetails.company_id == PackDetails.company_id))) \
            #     .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            #     .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            #     .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            #     .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=PackAnalysisDetails.device_id == DeviceMasterAlias.id) \
            #     .where(*pack_clause,
            #            PackAnalysisDetails.canister_id << skipped_canister) \
            #     .group_by(PackAnalysisDetails.canister_id)
            query = PackDetails.select(ReplenishSkippedCanister.canister_id,
                                       CanisterMaster.canister_type,
                                       CanisterMaster.drug_id.alias("canister_drug_id"),
                                       fn.IF(
                                           CanisterMaster.expiry_date <= date.today() + timedelta(
                                               settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                           constants.EXPIRED_CANISTER,
                                           fn.IF(
                                               CanisterMaster.expiry_date <= date.today() + timedelta(
                                                   settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                               constants.EXPIRES_SOON_CANISTER,
                                               constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                       LocationMaster.id.alias("can_location_id"),
                                       LocationMaster.display_location,
                                       LocationMaster.location_number,
                                       LocationMaster.quadrant,
                                       ContainerMaster.drawer_name.alias('drawer_number'),
                                       ContainerMaster.drawer_level,
                                       ContainerMaster.ip_address,
                                       ContainerMaster.secondary_ip_address,
                                       DeviceMaster.id.alias("device_id"),
                                       DeviceMaster.device_type_id,
                                       DeviceMaster.serial_number,
                                       DeviceMaster.name.alias("device_name"),
                                       DeviceMaster.ip_address.alias("device_ip_address"),
                                       ReplenishSkippedCanister.quadrant.alias("dest_quadrant"),
                                       ReplenishSkippedCanister.device_id.alias("dest_device_id"),
                                       DeviceMasterAlias.id.alias("dest_device_id"),
                                       DeviceMasterAlias.name.alias("dest_device_name"),
                                       DeviceMasterAlias.device_type_id.alias("dest_device_type_id"),
                                       DeviceMasterAlias.serial_number.alias("dest_serial_number"),
                                       DeviceMasterAlias.ip_address.alias("dest_ip_address"),
                                       DrugMaster.concated_drug_name_field().alias("drug_name"),
                                       DrugMaster.ndc,
                                       DrugMaster.formatted_ndc,
                                       DrugMaster.txr,
                                       DrugMaster.image_name,
                                       DrugMaster.shape,
                                       DrugMaster.imprint,
                                       UniqueDrug.is_powder_pill,
                                       DrugDimension.approx_volume,
                                       DrugDetails.last_seen_by.alias("last_seen_with"),
                                       fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                             DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                       CanisterMaster.available_quantity,
                                       (fn.SUM(fn.FLOOR(SlotDetails.quantity)) -
                                        CanisterMaster.available_quantity).alias('replenish_qty'),
                                       fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias("required_qty"),
                                       fn.MIN(PackDetails.order_no).alias("pack_order_no"),
                                       UniqueDrug.is_delicate).dicts() \
                .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
                .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(DrugMasterAlias, on=((DrugMaster.formatted_ndc == DrugMasterAlias.formatted_ndc) &
                                           (DrugMaster.txr == DrugMasterAlias.txr)
                                           )
                      ) \
                .join(CanisterMaster, on=CanisterMaster.drug_id == DrugMasterAlias.id) \
                .join(ReplenishSkippedCanister, on=((ReplenishSkippedCanister.canister_id == CanisterMaster.id) &
                                                    (PackDetails.id == ReplenishSkippedCanister.pack_id))) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                       (UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == 1) &
                                                             (DrugStockHistory.company_id == PackDetails.company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                        (DrugDetails.company_id == PackDetails.company_id))) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=ReplenishSkippedCanister.device_id == DeviceMasterAlias.id) \
                .where(*pack_clause,
                       ReplenishSkippedCanister.canister_id << skipped_canister) \
                .group_by(ReplenishSkippedCanister.canister_id)
        logger.info(f"In get_skipped_replenish_query, query: {query}")
        logger.info(f"In get_skipped_replenish_query, list of data from query: {list(query)}")

        return query

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_skipped_replenish_query {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_skipped_replenish_query: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise error(2001)
    except Exception as e:
        logger.error("error in get_skipped_replenish_query {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_skipped_replenish_query: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise error(1000, "Error in get_skipped_replenish_query: " + str(e))

@log_args_and_response
def get_replenish_query_batch_optimised(batch_id: int, system_id: int, device_ids: list, replenish_canisters: list,
                              pack_ids: list = None):
    """
    Method to fetch replenish data of canisters for current and upcoming batch
    @param batch_id:
    @param replenish_canisters:
    @param system_id:
    @param device_ids:
    @param pack_ids:
    @return:

    """
    fndc_txr_list = []
    canister_list = []
    replenish_data = []
    pack_clause: list = list()
    try:
        # adding packs which are in progress but yet not processed by robot.
        progress_pack_ids = db_get_progress_filling_left_pack_ids()
        # if progress_pack_ids:
        #     pack_clause.append((PackDetails.pack_status == settings.PENDING_PACK_STATUS) |
        #                        (PackDetails.id << progress_pack_ids))
        # else:
        #     pack_clause.append(PackDetails.pack_status == settings.PENDING_PACK_STATUS)
        #
        # if pack_ids:
        #     pack_clause.append(PackDetails.id << pack_ids)

        if pack_ids:
            pack_clause.append(PackDetails.id << pack_ids)
        else:
            if progress_pack_ids:
                pack_clause.append((PackDetails.pack_status == settings.PENDING_PACK_STATUS) |
                                   (PackDetails.id << progress_pack_ids))
            else:
                pack_clause.append(PackDetails.pack_status == settings.PENDING_PACK_STATUS)

        replenish_query = PackDetails.select(PackAnalysisDetails.canister_id,
                                             fn.MIN(PackDetails.order_no).alias("pack_order_no"),
                                             DrugMaster.ndc,
                                             DrugMaster.image_name,
                                             DrugMaster.shape,
                                             DrugMaster.imprint,
                                             CanisterMaster.available_quantity,
                                             (fn.SUM(fn.FLOOR(SlotDetails.quantity)) -
                                              CanisterMaster.available_quantity).alias('replenish_qty'),
                                             fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('required_qty'),
                                             DrugMaster.concated_drug_name_field().alias('drug_name'),
                                             CanisterMaster.canister_type,
                                             CanisterMaster.drug_id.alias('canister_drug_id'),
                                             DrugMaster.formatted_ndc,
                                             DrugMaster.txr,
                                             DrugMaster.concated_fndc_txr_field().alias('fndc_txr')
                                             ).dicts() \
            .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
                                    (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(BatchMaster, on=BatchMaster.id == PackAnalysis.batch_id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(pack_clause,
                   (PackDetails.system_id == system_id),
                   (PackAnalysisDetails.device_id << device_ids),
                   (BatchMaster.status.in_(settings.CURRENT_AND_UPCOMING_BATCH_STATUS_LIST)),
                   (((BatchMaster.status == settings.BATCH_IMPORTED) & (
                       PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)) |
                    ((BatchMaster.status.in_(settings.UPCOMING_BATCH_STATUS)) & (
                        PackAnalysisDetails.status != constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED))))

        if replenish_canisters:
            replenish_query = replenish_query.where(PackAnalysisDetails.canister_id << replenish_canisters)
        replenish_query = replenish_query.group_by(PackAnalysisDetails.canister_id).order_by(PackDetails.order_no)

        # logger.info(f"In get_replenish_query_batch, replenish_query: {list(replenish_query)}")

        for record in replenish_query:
            fndc_txr_list.append(record['fndc_txr'])
            canister_list.append((record['canister_id']))
            replenish_data.append(record)

        drug_data = get_drug_stocks_and_dimension_details(fndc_txr_list)
        canister_data = db_get_current_location_details_by_canisters(canister_list)
        for record in replenish_data:
            record['last_seen_with'] = None
            record['approx_volume'] = None
            record['is_in_stock'] = True
            record['can_location_id'] = None
            record['display_location'] = None
            record['quadrant'] = None
            record['location_number'] = None
            record['device_type_id'] = None
            record['serial_number'] = None
            record['id'] = None
            record['device_id'] = None
            record['device_name'] = None
            record['drawer_number'] = None
            record['drawer_level'] = None
            if drug_data and record['fndc_txr'] in drug_data.keys():
                record['last_seen_with'] = drug_data[record['fndc_txr']]['last_seen_with']
                record['approx_volume'] = drug_data[record['fndc_txr']]['approx_volume']
                record['is_in_stock'] = drug_data[record['fndc_txr']]['is_in_stock']
            if drug_data and record['canister_id'] in canister_data.keys():
                record['can_location_id'] = canister_data[record['canister_id']]['location_id']
                record['display_location'] = canister_data[record['canister_id']]['display_location']
                record['quadrant'] = canister_data[record['canister_id']]['quadrant']
                record['location_number'] = canister_data[record['canister_id']]['location_number']
                record['device_type_id'] = canister_data[record['canister_id']]['device_type_id']
                record['serial_number'] = canister_data[record['canister_id']]['device_serial_number']
                record['id'] = canister_data[record['canister_id']]['device_id']
                record['device_id'] = canister_data[record['canister_id']]['device_id']
                record['device_name'] = canister_data[record['canister_id']]['device_name']
                record['drawer_number'] = canister_data[record['canister_id']]['drawer_name']
                record['drawer_level'] = canister_data[record['canister_id']]['drawer_level']

        return replenish_data
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_replenish_query_batch_optimised {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_replenish_query_batch_optimised: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise error(2001)
    except Exception as e:
        logger.error("error in get_replenish_query_batch_optimised {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_replenish_query_batch_optimised: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise error(1000, "Error in get_replenish_query_batch_optimised: " + str(e))


@log_args_and_response
def get_drug_active_canister_dao(company_id):

    """ fetches drugs with active canisters """

    try:
        query = CanisterMaster.select(DrugMaster.formatted_ndc,
                                      DrugMaster.txr,
                                      DrugMaster.id) \
                                .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                                .where(CanisterMaster.active==True, CanisterMaster.company_id == company_id)\
                                .group_by(DrugMaster.id) \
                                .order_by(DrugMaster.id) \

        drug_canister_list = [drug for drug in query.dicts()]
        return drug_canister_list
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_drug_active_canister_dao {}".format(e))
        raise error(2001)
    except Exception as e:
        logger.error("Error in get_drug_active_canister_dao {}".format(e))
        raise error(1000, "Error in get_drug_active_canister_dao: " + str(e))


@log_args_and_response
def db_get_inactive_canisters_from_canister_stick_id(canister_stick_id_list):
    canister_list = []
    clauses = list()
    clauses.append((CanisterMaster.active == 0))
    clauses.append(CanisterMaster.rfid.is_null(False))
    clauses.append(CanisterStick.id << canister_stick_id_list)

    try:
        query = CanisterMaster.select(
                CanisterMaster.id.alias('canister_id'),
                CanisterStick.id.alias('canister_stick_id')
                ).dicts() \
                .join(CanisterStick, JOIN_LEFT_OUTER, on=CanisterStick.id == CanisterMaster.canister_stick_id) \
                .where(functools.reduce(operator.and_, clauses))
        for record in query:
            canister_list.append(record)
        return canister_list
    except Exception as e:
        logger.info(e)
        return e

    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError


@log_args_and_response
def get_canister_drug_quadrant(canister_ids):

    try:
        canister_quad_drug = {}
        quad = int
        drug = str
        query = CanisterMaster.select(LocationMaster.quadrant, DrugMaster.concated_fndc_txr_field(sep='##').alias('drug'),
                                      CanisterMaster.id).dicts().join(LocationMaster,
                                                                on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DrugMaster, on=DrugMaster.id==CanisterMaster.drug_id)\
            .where(CanisterMaster.id << canister_ids)

        for record in query:
            quad = record['quadrant']
            drug = record['drug']
            canister_quad_drug[record['id']] = {quad: drug}

        return canister_quad_drug
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_empty_location_details_at_csr():
    """
    @return: query results
    """
    try:
        subquery = CanisterMaster.select(CanisterMaster.location_id.alias('canister_location_id')) \
            .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id).where(DeviceMaster.id == 1)

        query = LocationMaster.select(LocationMaster.id.alias('empty_location_id'),
                                         LocationMaster.device_id.alias('empty_location_device_id')) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id).where(LocationMaster.id.not_in(subquery),
                                                                                      LocationMaster.device_id == 1)

        canister_details_list = list()

        for record in query.dicts():
            canister_details_list.append(record)

        return canister_details_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_big_canister_id_in_robot_not_used_in_this_batch(device_id, quadrant, canister_id_list, user_id):
    """
    @return: query results
    """
    try:
        query = CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                         CanisterMaster.company_id.alias('company_id'),
                                      CanisterMaster.location_id.alias("robot_location_id")) \
            .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id).where(DeviceMaster.id == device_id,
                                                                                      LocationMaster.quadreant == quadrant,
        CanisterMaster.id.not_in(canister_id_list), CanisterMaster.canister_type == 70).limit(1)

        canister_details_list = list()

        for record in query.dicts():
            record["user_id"] = user_id
            canister_details_list.append(record)

        return canister_details_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_small_canister_id_in_robot_not_used_in_this_batch(device_id, quadrant, canister_id_list, user_id):
    """
    @return: query results
    """
    try:
        query = CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                         CanisterMaster.company_id.alias('company_id'),
                                      CanisterMaster.location_id.alias("robot_location_id")) \
            .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id).where(DeviceMaster.id == device_id,
                                                                                      LocationMaster.quadrant == quadrant,
        CanisterMaster.id.not_in(canister_id_list), CanisterMaster.canister_type == 71).limit(1)

        canister_details_list = list()

        for record in query.dicts():
            record["user_id"] = user_id
            canister_details_list.append(record)

        return canister_details_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_canister_id_in_robot_not_used_in_this_batch(device_id, quadrant, batch_id):
    """
    @return: query results
    """
    try:
        subquery = ReservedCanister.select(ReservedCanister.canister_id).where(ReservedCanister.batch_id == batch_id)

        query = CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                         CanisterMaster.company_id.alias('company_id'),
                                      CanisterMaster.location_id.alias("robot_location_id"),
                                      LocationMaster.quadrant.alias("robot_quadrant"),
                                      LocationMaster.device_id.alias("robot_device_id")
                                      ) \
            .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id).where(DeviceMaster.id == device_id,
                                                                                      LocationMaster.quadrant == quadrant,
        CanisterMaster.id.not_in(subquery))

        canister_details_list = list()

        for record in query.dicts():
            canister_details_list.append(record)

        return canister_details_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
@log_args_and_response
def get_alternate_canister_from_canister_id(company_id: int, canister_ids: list = None):
    """
    Function to get alternate canister for batch
    @param company_id:
    @param alt_in_robot:
    @param alt_available:
    @param ignore_reserve_status:
    @param current_not_in_robot:
    @param canister_ids:
    @param device_id:
    @param skip_canisters:
    @param alt_in_csr:
    @param guided_transfer:
    @param alt_canister_for_guided:
    @return:
    @param batch_id:
    """
    # CanisterMasterAlias1 = CanisterMaster.alias()
    CanisterMasterAlias2 = CanisterMaster.alias()
    LocationMasterAlias = LocationMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()

    DrugMasterAlias = DrugMaster.alias()

    try:
        skip_canisters = None

        reserved_canisters = ReservedCanister.db_get_reserved_canister_query(company_id=company_id,
                                                                             skip_canisters=skip_canisters)
        logger.info("In _get_alternate_canister_for_batch: reserved canister: {} ".format(reserved_canisters))

        # candidate alternate canisters which are not reserved
        alternate_canister = CanisterMasterAlias2.select(CanisterMasterAlias2.id.alias('canister_id'),
                                                         CanisterMasterAlias2.available_quantity,
                                                         fn.IF(CanisterMasterAlias2.available_quantity < 0, 0,
                                                               CanisterMasterAlias2.available_quantity).alias(
                                                             'display_quantity'),
                                                         CanisterMasterAlias2.rfid.alias('rfid'),
                                                         CanisterMasterAlias2.canister_type.alias('canister_type'),
                                                         DrugMasterAlias.formatted_ndc,
                                                         DrugMasterAlias.txr,
                                                         DrugMasterAlias.ndc,
                                                         DrugMasterAlias.drug_name,
                                                         DrugMasterAlias.strength_value,
                                                         DrugMasterAlias.strength,
                                                         LocationMasterAlias.location_number,
                                                         ContainerMaster.id.alias('container_id'),
                                                         ContainerMaster.drawer_name.alias('drawer_name'),
                                                         LocationMasterAlias.display_location,
                                                         ZoneMaster.id.alias('zone_id'),
                                                         ZoneMaster.name.alias('zone_name'),
                                                         DeviceLayoutDetails.id.alias('device_layout_id'),
                                                         DeviceMasterAlias.name.alias('device_name'),
                                                         DeviceMasterAlias.id.alias('device_id'),
                                                         DeviceMasterAlias.ip_address.alias('device_ip_address'),
                                                         DeviceTypeMaster.device_type_name,
                                                         DeviceTypeMaster.id.alias('device_type_id'),
                                                         ContainerMaster.drawer_level,
                                                         ContainerMaster.ip_address,
                                                         ContainerMaster.secondary_ip_address,
                                                         ContainerMaster.serial_number,
                                                         DrugDetails.last_seen_by.alias('last_seen_with'),
                                                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                                               DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                                         fn.IF(DrugStockHistory.created_by.is_null(True), None,
                                                               DrugStockHistory.created_by).alias("stock_updated_by")) \
            .join(DrugMasterAlias, on=DrugMasterAlias.id == CanisterMasterAlias2.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=(UniqueDrug.formatted_ndc == DrugMasterAlias.formatted_ndc)
                                                  & (UniqueDrug.txr == DrugMasterAlias.txr)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER,
                  on=((DrugMasterAlias.id == DrugStockHistory.unique_drug_id) & (DrugStockHistory.is_active == 1)
                      & (DrugStockHistory.company_id == CanisterMasterAlias2.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                   (DrugDetails.company_id == CanisterMasterAlias2.company_id)) \
            .join(CanisterZoneMapping, JOIN_LEFT_OUTER, on=CanisterZoneMapping.canister_id == CanisterMasterAlias2.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, on=CanisterZoneMapping.zone_id == ZoneMaster.id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, CanisterMasterAlias2.location_id == LocationMasterAlias.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMasterAlias.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMasterAlias.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMasterAlias.id)
        alternate_canister = alternate_canister.where(CanisterMasterAlias2.company_id == company_id,
                                                      CanisterMasterAlias2.active == settings.is_canister_active)


        alternate_canister = alternate_canister.where(CanisterMasterAlias2.id.not_in(reserved_canisters))
        # alternate_canister = alternate_canister.order_by(CanisterMasterAlias2.available_quantity.desc())
        alternate_canister = alternate_canister.alias('alternate_canister')

        order_list: list = list()
        on_condition = ((alternate_canister.c.formatted_ndc == DrugMaster.formatted_ndc)
                        & (alternate_canister.c.txr == DrugMaster.txr)
                        & (alternate_canister.c.canister_id != CanisterMaster.id))

        query = CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                             LocationMaster.device_id,
                                             LocationMaster.location_number,
                                             LocationMaster.display_location,
                                             ZoneMaster.id.alias('zone_id'),
                                             DeviceMaster.name.alias('device_name'),
                                             DeviceMaster.device_type_id,
                                             DeviceMaster.ip_address.alias('device_ip_address'),
                                             ContainerMaster.id.alias('drawer_id'),
                                             ContainerMaster.drawer_name.alias('drawer_number'),
                                             ContainerMaster.serial_number,
                                             ContainerMaster.ip_address,
                                             ContainerMaster.mac_address,
                                             ContainerMaster.secondary_mac_address,
                                             ContainerMaster.secondary_ip_address,
                                             DeviceMaster.id.alias('device_id'),
                                             alternate_canister.c.canister_id.alias('alt_canister_id'),
                                             alternate_canister.c.canister_type.alias('alt_canister_type'),
                                             alternate_canister.c.drawer_level.alias('alt_can_drawer_level'),
                                             alternate_canister.c.device_id.alias('alt_device_id'),
                                             alternate_canister.c.device_type_id.alias('alt_device_type_id'),
                                             alternate_canister.c.location_number.alias('alt_location_number'),
                                             alternate_canister.c.ndc.alias('alt_ndc'),
                                             alternate_canister.c.drug_name.alias('alt_drug_name'),
                                             alternate_canister.c.strength.alias('alt_strength'),
                                             alternate_canister.c.strength_value.alias('alt_strength_value'),
                                             alternate_canister.c.device_name.alias('alt_device_name'),
                                             alternate_canister.c.available_quantity.alias('alt_available_quantity'),
                                             alternate_canister.c.rfid.alias('alt_rfid'),
                                             alternate_canister.c.drawer_name.alias('alt_drawer_number'),
                                             alternate_canister.c.display_location.alias('alt_display_location'),
                                             alternate_canister.c.container_id.alias('alt_drawer_id'),
                                             alternate_canister.c.ip_address.alias('alt_ip_address'),
                                             alternate_canister.c.zone_id.alias('alt_zone_id'),
                                             alternate_canister.c.zone_name.alias('alt_zone_name'),
                                             alternate_canister.c.secondary_ip_address.alias(
                                                 'alt_secondary_ip_address'),
                                             alternate_canister.c.serial_number.alias('alt_serial_number'),
                                             alternate_canister.c.last_seen_with.alias('last_seen_with'),
                                             alternate_canister.c.is_in_stock.alias('is_in_stock'),
                                             alternate_canister.c.stock_updated_by.alias('stock_updated_by'),
                                             alternate_canister.c.container_id.alias('container_id'),
                                             alternate_canister.c.device_ip_address.alias('alt_device_ip_address'),
                                             DrugMaster.drug_name,
                                             DrugMaster.strength_value,
                                             DrugMaster.strength,
                                             DrugMaster.ndc,
                                             DrugMaster.shape, DrugMaster.color,
                                             DrugMaster.imprint, DrugMaster.image_name) \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(CanisterZoneMapping, JOIN_LEFT_OUTER, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, on=CanisterZoneMapping.zone_id == ZoneMaster.id) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .join(alternate_canister, JOIN_LEFT_OUTER, on=on_condition)
        filters = []
        if canister_ids:  # alternate canister for specific canister ids
            filters.append((CanisterMaster.id << canister_ids))
        filters.append((alternate_canister.c.canister_id.is_null(False)))

        # to keep on shelf canisters at the end
        order_list.append(SQL('alt_device_type_id is null'))

        order_list.append(SQL('FIELD(alt_device_type_id, {},{},{},{})'
                                  .format(settings.DEVICE_TYPES['ROBOT'],
                                          settings.DEVICE_TYPES['CSR'],
                                          settings.DEVICE_TYPES['Canister Transfer Cart'],
                                          settings.DEVICE_TYPES['Canister Cart w/ Elevator'])))
        order_list.append(alternate_canister.c.available_quantity.desc())

        query = query.where(*filters) \
            .order_by(*order_list)

        return list(query.dicts())

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_alternate_canister_for_batch_data {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_alternate_canister_for_batch_data {}".format(e))
        raise e

@log_args_and_response
def db_get_canister_id_details_on_shelf_csr_trolley():
    """
    @return: query results
    """
    try:
        query = CanisterMaster.select(CanisterMaster.id.alias('canister_id'), LocationMaster.device_id) \
            .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id)\
            .where(DeviceMaster.id.is_null(True) | DeviceMaster.id << [1, 23, 24, 25]).order_by(LocationMaster.device_id)

        canister_details_list = list()

        for record in query.dicts():
            canister_details_list.append(record)

        return canister_details_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def delete_reserved_canister_for_pack_queue(packids: list):
    try:
        logger.info("In delete_reserved_canister_for_pack_queue")
        current_pack_canister_set = set()
        canisters_in_use = set()
        status = None
        canisters_to_delete = list()
        if packids:
            query = PackAnalysis.select(PackAnalysisDetails.canister_id) \
                    .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id).dicts() \
                    .where(PackAnalysis.pack_id << packids,
                           PackAnalysisDetails.canister_id.is_null(False)) \
                    .group_by(PackAnalysisDetails.canister_id)

            for canister_id in query:
                current_pack_canister_set.add(canister_id['canister_id'])

            logger.info("In delete_reserved_canister_for_pack_queue, current_pack_canister_set {}"
                        .format(current_pack_canister_set))

            if current_pack_canister_set:

                batch_status = [settings.BATCH_MFD_USER_ASSIGNED,
                                settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
                                settings.BATCH_CANISTER_TRANSFER_DONE,
                                settings.BATCH_IMPORTED,
                                settings.BATCH_MERGED]

                pack_status = [settings.PENDING_PACK_STATUS,
                               settings.PROGRESS_PACK_STATUS]

                query2 = PackDetails.select(PackAnalysisDetails.canister_id).dicts() \
                            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
                            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
                            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                            .where(BatchMaster.status << batch_status,
                                   PackDetails.pack_status << pack_status,
                                   PackAnalysisDetails.canister_id << list(current_pack_canister_set)) \
                            .group_by(PackAnalysisDetails.canister_id)

                for canister in query2:
                    canisters_in_use.add(canister['canister_id'])

                canisters_to_delete = list(current_pack_canister_set - canisters_in_use)
                logger.info("In delete_reserved_canister_for_pack_queue, canisters_to_delete {}"
                            .format(canisters_to_delete))

                if canisters_to_delete:
                    status = ReservedCanister.delete() \
                       .where(ReservedCanister.canister_id << canisters_to_delete).execute()

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_reserved_canister_for_pack_queue {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in delete_reserved_canister_for_pack_queue {}".format(e))
        raise e


@log_args_and_response
def get_order_wise_packs_and_mfd_trolley_details(system_id,device_ids: list):
    try:
        mfd_status = [constants.MFD_CANISTER_PENDING_STATUS,
                      constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                      constants.MFD_CANISTER_FILLED_STATUS]

        query = PackQueue.select(PackDetails.id,
                                 PackDetails.pack_status,
                                 PackDetails.order_no,
                                 fn.GROUP_CONCAT(fn.DISTINCT(fn.COALESCE(MfdAnalysis.transferred_location_id, "None"))).alias("transferred_locations"),
                                 fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.id)).alias("mfd_analysis_ids"),
                                 fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.status_id)).alias("mfd_analysis_status"),
                                 fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.mfd_canister_id)).alias("mfd_canister_ids"),
                                 MfdAnalysis.trolley_seq,
                                 fn.GROUP_CONCAT(fn.DISTINCT(fn.COALESCE(MfdAnalysis.trolley_location_id, "None"))).alias("trolley_location_ids")
                                 ).dicts() \
                .join(PackDetails, on=PackDetails.id == PackQueue.pack_id) \
                .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                .join(PackAnalysisDetails, JOIN_LEFT_OUTER,on=PackAnalysisDetails.slot_id == SlotDetails.id) \
                .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
                .join(MfdAnalysis, JOIN_LEFT_OUTER, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
                .where(PackDetails.system_id == system_id,
                       (PackAnalysisDetails.device_id.in_(device_ids) | MfdAnalysis.dest_device_id.in_(device_ids)),
                       (MfdAnalysis.status_id.in_(mfd_status) | MfdAnalysis.status_id.is_null(True))) \
                .order_by(PackDetails.order_no) \
                .group_by(PackDetails.id)

        pack_list_order_wise = []
        trolley_seq : dict = OrderedDict()

        logger.info(f"In get_order_wise_packs_and_mfd_trolley_details, query: {query}")

        for data in query:
            print(f"data: {data}")

            tuple = (int(data["id"]), data["pack_status"], int(data["order_no"]), None if data["trolley_seq"] is  None else int(data["trolley_seq"]))
            logger.info(f"In get_order_wise_packs_and_mfd_trolley_details, tuple: {tuple}")

            pack_list_order_wise.append(tuple)

            if data["trolley_seq"]:
                trolley_sequence = int(data["trolley_seq"])
                if not trolley_seq.get(trolley_sequence):
                    trolley_seq[trolley_sequence] = {"require_transfer_count": 0,
                                                            "transferred_location_count": 0,
                                                            "trolley_status": "Filled",
                                                            "trolley_packs": 0}
                if not trolley_seq[trolley_sequence].get("first_pack"):
                    trolley_seq[trolley_sequence]["first_pack_order_no"] = int(data["order_no"])
                trolley_seq[trolley_sequence]["last_pack_order_no"] = int(data["order_no"])
                trolley_seq[trolley_sequence]["trolley_packs"] += 1

                total_canister = len(set(map(eval, (data["trolley_location_ids"]).split(","))) - {None})
                transferred_canisters = len(set(map(eval, (data["transferred_locations"]).split(","))) - {None})
                trolley_seq[trolley_sequence]["require_transfer_count"] += (total_canister - transferred_canisters)
                trolley_seq[trolley_sequence]["transferred_location_count"] += transferred_canisters

                if trolley_seq[trolley_sequence]["trolley_status"] == "Filled":
                    trolley_seq[trolley_sequence]["trolley_status"] = "Filled" if not {constants.MFD_CANISTER_PENDING_STATUS,constants.MFD_CANISTER_IN_PROGRESS_STATUS}.intersection(set(map(eval, (data["mfd_analysis_status"]).split(",")))) else "Unfilled"

        return pack_list_order_wise, trolley_seq
    except Exception as e:
        logger.error("error in get_order_wise_packs_and_mfd_trolley_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_order_wise_packs_and_mfd_trolley_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_first_mini_batch_packs(system_id, device_ids: list):
    try:
        pack_list_order_wise, trolley_sequence_dict = get_order_wise_packs_and_mfd_trolley_details(system_id,device_ids)

        if not pack_list_order_wise:
            return [], []

        n = settings.MINI_BATCH_PACK_COUNT
        pack_list_order_wise_copy = deepcopy(pack_list_order_wise)
        # last_filled_trolley_seq_pack = tuple()
        # for trolley, data in trolley_sequence_dict.items():
        #     if data["trolley_status"] == "Filled":
        #         last_filled_trolley_seq_pack = (trolley, data["last_pack"])
        #     if data["trolley_status"] == "Unfilled":
        #         break
        first_mini_batch_packs_without_buffer = []
        trolley_for_first_mini_batch_packs = set()
        first_mini_batch_pack_list = []
        max_order_no_for_first_mini_batch = pack_list_order_wise[-1][2]
        for pack_data in pack_list_order_wise:
            if not pack_data[3]:
                first_mini_batch_packs_without_buffer.append(pack_data)
                pack_list_order_wise_copy.remove(pack_data)
            else:
                if trolley_sequence_dict[pack_data[3]]["trolley_status"] == "Filled":
                    first_mini_batch_packs_without_buffer.append(pack_data)
                    pack_list_order_wise_copy.remove(pack_data)
                    if trolley_sequence_dict[pack_data[3]]["require_transfer_count"]:
                        trolley_for_first_mini_batch_packs.add(pack_data[3])

            if len(first_mini_batch_packs_without_buffer) == n:
                max_order_no_for_first_mini_batch = int(pack_data[2])
                break

        logger.info(f"In get_first_mini_batch_packs, trolley_for_first_mini_batch_packs: {trolley_for_first_mini_batch_packs}")
        first_mini_batch_pack_list.extend(first_mini_batch_packs_without_buffer)

        for trolley in trolley_for_first_mini_batch_packs:
            logger.info(f"get_first_mini_batch_packs, trolley: {trolley}")
            buffer_packs = 0
            if trolley_sequence_dict[trolley]["require_transfer_count"] == 0:
                continue

                # canister already in the robot
                # for data in pack_list_order_wise_copy:
                #     first_mini_batch_pack_list.append(data)
                #     pack_list_order_wise_copy.remove(data)
                #
                #     if data[2] == trolley_sequence_dict[trolley]["last_pack_order_no"]:
                #         break

            if trolley_sequence_dict[trolley]["require_transfer_count"] != 0:
                                # ------- 1 -------
                # first check that any trolley_seq will available for this first mini batch or not
                # if it is available >> count how many packs require to remove those canisters
                # find canister count from previous trolley seq
                previous_trolley = trolley_sequence_dict.get(trolley - 1)
                if previous_trolley:

                    no_of_canister_require_transfer = previous_trolley["require_transfer_count"] + \
                                                      previous_trolley["transferred_location_count"]
                    buffer_packs += math.ceil((int(no_of_canister_require_transfer) * settings.TIME_TO_TRANSFER_MFD_CANISTER) / settings.TIME_TO_PROCESS_PACK)
                                # ------- 2 -------
                # find how many packs require to transfer canisters from trolley to robot
                no_of_canister_require_transfer = trolley_sequence_dict[trolley]["require_transfer_count"]
                buffer_packs += math.ceil((int(no_of_canister_require_transfer) * settings.TIME_TO_TRANSFER_MFD_CANISTER) / settings.TIME_TO_PROCESS_PACK)

            if buffer_packs:
                # trolley_pack = trolley_sequence_dict[trolley]["trolley_packs"]
                for data in pack_list_order_wise_copy:

                    if data[3] and data[3] != trolley:
                        continue

                    # if not data[3]:
                    #     if buffer_packs:
                    #         buffer_packs -= 1
                    # if data[3] == trolley:
                    #     if trolley_pack:
                    #         trolley_pack -= 1
                    buffer_packs -= 1

                    first_mini_batch_pack_list.append(data)
                    index = pack_list_order_wise_copy.index(data)
                    pack_list_order_wise_copy.remove(data)
                    pack_list_order_wise_copy.insert(index, (0, 0, 0, 0))

                    # if not buffer_packs and trolley_pack and data[2] > max_order_no_for_first_mini_batch:
                    #     break
                    # if not buffer_packs and not trolley_pack and len(first_mini_batch_pack_list)>=n:
                    #     break
                    if not buffer_packs:
                        break
        pack_list_order_wise_copy = [data for data in pack_list_order_wise_copy if data[0] != 0]
        if len(first_mini_batch_pack_list) < n and len(pack_list_order_wise_copy):
            require_pack_count = n - len(first_mini_batch_pack_list)
            logger.info(f"In get_first_mini_batch_packs, require_pack_count : {require_pack_count}")
            first_mini_batch_pack_list.extend(pack_list_order_wise_copy[: require_pack_count])
            pack_list_order_wise_copy = pack_list_order_wise_copy[require_pack_count:]

        return first_mini_batch_pack_list, pack_list_order_wise_copy

    except Exception as e:
        logger.error("error in get_first_mini_batch_packs {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_first_mini_batch_packs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        # return error(2001)
        # logger.error(f"Error in get_first_mini_batch_packs, e: {e}")
        raise e


@log_args_and_response
def get_canister_data_by_ndc_and_company_id_dao(ndc_list, company_id):
    try:

        canister_data = []
        DrugMasterAlias = DrugMaster.alias()
        query = CanisterMaster.select().dicts().join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(DrugMasterAlias, on=((DrugMaster.formatted_ndc == DrugMasterAlias.formatted_ndc) & (
                    DrugMaster.txr == DrugMasterAlias.txr))) \
            .where(DrugMasterAlias.ndc << ndc_list, CanisterMaster.active == settings.is_canister_active,
            CanisterMaster.company_id == company_id)

        for record in query:
            canister_data.append(record)
        return canister_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_data_by_ndc_and_company_id_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_data_by_ndc_and_company_id_dao {}".format(e))
        raise e


@log_args_and_response
def get_canister_expiry_status(canister_id,company_id):
    try:
        logger.info("In get_canister_expiry_status")
        query = CanisterMaster.select(CanisterMaster.id, CanisterMaster.expiry_date,
                                      fn.IF(
                                          CanisterMaster.expiry_date <= date.today() + timedelta(
                                              settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                          constants.EXPIRED_CANISTER,
                                          fn.IF(
                                              CanisterMaster.expiry_date <= date.today() + timedelta(
                                                  settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                              constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status")
                                      ).dicts() \
                .where(CanisterMaster.company_id == company_id,
                       CanisterMaster.id == canister_id).get()

        return query["expiry_status"], query["expiry_date"]
    except DoesNotExist as e:
        logger.error(f"Error in get_canister_expiry_status, e: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Error in get_canister_expiry_status, e: {e}")


@log_args_and_response
def discard_canister_tracker(canister_id, quantity, user_id):
    try:

        usage_status = [constants.USAGE_CONSIDERATION_PENDING, constants.USAGE_CONSIDERATION_IN_PROGRESS]
        canister_qty = deepcopy(quantity)

        drug_id_query = CanisterMaster.select(CanisterMaster.drug_id).dicts().where(CanisterMaster.id == canister_id).get()
        tracker_dict = {}
        epbm_data = {}
        canister_tracker_ids = []
        discard_expiry_date = None
        discard_lot = None
        query = CanisterTracker.select(CanisterTracker.id,
                                       CanisterTracker.canister_id,
                                       CanisterTracker.lot_number,
                                       CanisterTracker.expiration_date,
                                       CanisterTracker.quantity_adjusted,
                                       DrugMaster.ndc,
                                       CanisterTracker.usage_consideration,
                                       CanisterTracker.case_id
                                       ).dicts() \
                .join(DrugMaster, on=DrugMaster.id == CanisterTracker.drug_id) \
                .where(CanisterTracker.canister_id == canister_id,
                       CanisterTracker.usage_consideration.in_(usage_status)) \
                .order_by(CanisterTracker.id.desc())
        for data in query:
            logger.info(f"In discard_canister_tracker, data: {data}")
            if not data["expiration_date"]:
                continue
            discard_lot = data["lot_number"]
            discard_case_id = data["case_id"]
            discard_expiry_date = data["expiration_date"]
            if data["usage_consideration"] == constants.USAGE_CONSIDERATION_IN_PROGRESS:
                trash_qty = min(quantity, int(data["quantity_adjusted"]))
            else:
                quantity -= int(data["quantity_adjusted"])
                trash_qty = int(data["quantity_adjusted"])

            expiry = data["expiration_date"].split("-")
            expiry_month = int(expiry[0])
            expiry_year = int(expiry[1])
            expiry_date = last_day_of_month(date(expiry_year, expiry_month, 1))

            canister_tracker_ids.append(data['id'])
            if not epbm_data.get(data['ndc']):
                epbm_data[data['ndc']] = {}
            if not epbm_data[data['ndc']].get(data["lot_number"]):
                epbm_data[data['ndc']][data["lot_number"]] = {"trash_qty": trash_qty,
                                                              "expiry_date": expiry_date,
                                                              "note": "Expired drug",
                                                              "case_id": data["case_id"]}
            else:
                epbm_data[data['ndc']][data["lot_number"]]["trash_qty"] += trash_qty

            canister_tracker_ids.append(data['id'])

            status = CanisterTracker.insert(canister_id=canister_id,
                                            device_id=None,
                                            drug_id=drug_id_query["drug_id"],
                                            qty_update_type_id=constants.CANISTER_QUANTITY_UPDATE_TYPE_DISCARD,
                                            quantity_adjusted=-trash_qty,
                                            original_quantity=trash_qty,
                                            lot_number=discard_lot,
                                            expiration_date=discard_expiry_date,
                                            note=None,
                                            created_by=user_id,
                                            voice_notification_uuid=None,
                                            drug_scan_type_id=None,
                                            replenish_mode_id=None,
                                            usage_consideration=constants.USAGE_CONSIDERATION_DISCARD,
                                            case_id=discard_case_id).execute()

            logger.info(f"In discard_canister_tracker, canister tracker insert status: {status}")

            # tracker_dict[data["id"]] = {"ndc": data["ndc"],
            #                             "trash_qty": trash_qty,
            #                             "lot_number": data["lot_number"],
            #                             "expiry_date":expiry_date,
            #                             "note": note}

        if canister_tracker_ids:
            status = CanisterTracker.update(usage_consideration=constants.USAGE_CONSIDERATION_DISCARD) \
                                    .where(CanisterTracker.id.in_(canister_tracker_ids)).execute()

            logger.info(f"In discard_canister_tracker, canister tracker update status: {status}")

        # status = CanisterTracker.insert(canister_id=canister_id,
        #                            device_id=None,
        #                            drug_id=drug_id_query["drug_id"],
        #                            qty_update_type_id=constants.CANISTER_QUANTITY_UPDATE_TYPE_DISCARD,
        #                            quantity_adjusted= -canister_qty,
        #                            original_quantity=canister_qty,
        #                            lot_number=discard_lot,
        #                            expiration_date=discard_expiry_date,
        #                            note=None,
        #                            created_by=user_id,
        #                            voice_notification_uuid=None,
        #                            drug_scan_type_id= None,
        #                            replenish_mode_id=None,
        #                            usage_consideration=constants.USAGE_CONSIDERATION_DISCARD).execute()
        #
        # logger.info(f"In discard_canister_tracker, canister tracker insert status: {status}")

        return epbm_data

    except Exception as e:
        logger.error("error in discard_canister_tracker {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in discard_canister_tracker: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

#
# @log_args_and_response
# def get_expired_canister_data_dao(company_id, device_id=None):
#     try:
#         logger.info(f'In get_expired_canister_data')
#
#         query = CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
#                                       CanisterMaster.expiry_date,
#                                       CanisterMaster.active,
#                                       CanisterMaster.available_quantity,
#                                       DrugMaster.concated_drug_name_field(include_ndc=True).alias("drug_full_name"),
#                                       DrugMaster.formatted_ndc,
#                                       DrugMaster.txr,
#                                       DrugMaster.ndc,
#                                       LocationMaster.device_id,
#                                       DeviceMaster.name.alias("device_name"),
#                                       ContainerMaster.drawer_name,
#                                       LocationMaster.display_location,
#                                       DeviceMaster.ip_address,
#                                       ContainerMaster.ip_address
#                                       ).dicts() \
#                 .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
#                 .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
#                 .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
#                 .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
#                 .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
#                 .where(CanisterMaster.company_id == company_id,
#                        CanisterMaster.expiry_date <= date.today()+settings.TIME_DELTA_FOR_EXPIRED_CANISTER)
#         if device_id:
#             query = query.where(LocationMaster.device_id == device_id)
#
#         logger.info(f"In get_expired_canister_data, query: {query}")
#         return query
#     except Exception as e:
#         logger.error("error in get_expired_canister_data {}".format(e))
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(
#             f"Error in get_expired_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
#         raise e


@log_args_and_response
def check_canister_uses_in_pack_queue(canister_id):
    try:
        logger.info("In check_canister_uses_in_pack_queue")

        query = PackQueue.select(PackDetails.system_id,
                                 PackAnalysisDetails.device_id).dicts() \
                .join(PackDetails, on=PackDetails.id == PackQueue.pack_id) \
                .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .where(PackAnalysisDetails.canister_id == canister_id,
                       PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)

        for data in query:
            return True, data["device_id"], data["system_id"]
        return False, None, None

    except Exception as e:
        logger.error(f'Error in check_canister_uses_in_pack_queue, e: {e}')
        return False, None, None


@log_args_and_response
def delete_reserved_canister_for_skipped_canister(canister_list, analysis_id=None, batch_id=None):
    # same function in pack_analysis_dao
    try:
        logger.info("In delete_reserved_canister_for_skipped_canister")
        canisters_in_use = set()
        canisters_to_delete = list()
        status = None
        clauses = list()

        batch_status = [settings.BATCH_MFD_USER_ASSIGNED,
                        settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
                        settings.BATCH_CANISTER_TRANSFER_DONE,
                        settings.BATCH_IMPORTED]

        pack_status = [settings.PENDING_PACK_STATUS,
                       settings.PROGRESS_PACK_STATUS]

        query = PackDetails.select(PackAnalysisDetails.canister_id).dicts() \
            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(BatchMaster.status << batch_status,
                   PackDetails.pack_status << pack_status,
                   PackAnalysisDetails.canister_id << list(canister_list)) \
            .group_by(PackAnalysisDetails.canister_id)

        if analysis_id:
            clauses.append(PackAnalysis.id.not_in(analysis_id))

        if batch_id:
            clauses.append(PackAnalysis.batch_id.not_in(batch_id))

        if clauses:
            query = query.where(reduce(operator.and_, clauses))

        for canister in query:
            canisters_in_use.add(canister['canister_id'])

        canisters_to_delete = list(set(canister_list) - canisters_in_use)

        logger.info("In delete_reserved_canister_for_skipped_canister, canisters_to_delete {}, canisters_in_use {}"
                    .format(canisters_to_delete, canisters_in_use))

        if canisters_to_delete:
            status = ReservedCanister.delete() \
                .where(ReservedCanister.canister_id << canisters_to_delete).execute()

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_reserved_canister_for_skipped_canister {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in delete_reserved_canister_for_skipped_canister {}".format(e))
        raise e


@log_args_and_response
def insert_records_in_reserved_canister(canister_data):
    try:
        logger.info("Inside insert_records_in_reserved_canister, canister data: {}".format(canister_data))

        status = ReservedCanister.db_save(canister_data)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_reserved_canister_for_skipped_canister {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in delete_reserved_canister_for_skipped_canister {}".format(e))
        raise e


@log_args_and_response
def db_get_total_canister_quantity_by_drug_id(drug_list):
    drug_quantity_dict = {}
    canister_dict = {}

    try:

        query = CanisterMaster.select(CanisterMaster.id, CanisterMaster.available_quantity).dicts().where(CanisterMaster.drug_id << drug_list)

        canister_dict = {r['id']:r['available_quantity'] for r in query}

        if list(canister_dict.keys()):
            for canister, qty in canister_dict.items():
                can_drug_dict = db_get_canister_current_qty_drug_wise(canister, qty)
                for drug, drug_data in can_drug_dict.items():
                    for case_id, quantity in drug_data.items():
                        drug_quantity_dict.setdefault(drug,dict())
                        drug_quantity_dict[drug][case_id] = drug_quantity_dict[drug].get(case_id, 0) + quantity

        return drug_quantity_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_total_canister_quantity_by_drug_id {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_total_canister_quantity_by_drug_id {}".format(e))
        raise e


@log_args_and_response
def db_get_canister_current_qty_drug_wise(canister_id, available_qty):
    drug_qty_dict = {}
    try:
        usage_status = [constants.USAGE_CONSIDERATION_PENDING, constants.USAGE_CONSIDERATION_IN_PROGRESS]

        drug_id_query = CanisterMaster.select(CanisterMaster.drug_id).dicts().where(
            CanisterMaster.id == canister_id).get()

        query = CanisterTracker.select(CanisterTracker.id,
                                       CanisterTracker.canister_id,
                                       CanisterTracker.lot_number,
                                       CanisterTracker.expiration_date,
                                       CanisterTracker.quantity_adjusted,
                                       DrugMaster.ndc,
                                       CanisterTracker.drug_id,
                                       CanisterTracker.usage_consideration,
                                       CanisterTracker.case_id
                                       ).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterTracker.drug_id) \
            .where(CanisterTracker.canister_id == canister_id,
                   CanisterTracker.usage_consideration.in_(usage_status)) \
            .order_by(CanisterTracker.id.desc())

        for r in query:
            if available_qty == 0:
                break
            if r['usage_consideration'] == constants.USAGE_CONSIDERATION_PENDING and r[
                'quantity_adjusted'] > available_qty:
                drug_qty_dict.setdefault(r['drug_id'],dict())
                drug_qty_dict[r['drug_id']][r['case_id']] = drug_qty_dict[r['drug_id']].get(r['case_id'], 0) + available_qty
                break
            if r['usage_consideration'] == constants.USAGE_CONSIDERATION_PENDING and r[
                'quantity_adjusted'] <= available_qty:
                drug_qty_dict.setdefault(r['drug_id'], dict())
                available_qty -= r['quantity_adjusted']
                drug_qty_dict[r['drug_id']][r['case_id']] = drug_qty_dict[r['drug_id']].get(r['case_id'], 0) + r['quantity_adjusted']
                continue
            if r['usage_consideration'] == constants.USAGE_CONSIDERATION_IN_PROGRESS and r[
                'quantity_adjusted'] > available_qty:
                drug_qty_dict.setdefault(r['drug_id'], dict())
                drug_qty_dict[r['drug_id']][r['case_id']] = drug_qty_dict[r['drug_id']].get(r['case_id'], 0) + available_qty
                available_qty -= r['quantity_adjusted']
                continue

        return drug_qty_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_canister_current_qty_drug_wise {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_canister_current_qty_drug_wise {}".format(e))
        raise e


@log_args_and_response
def get_expired_drug_info(canister_expiry_dict):
    try:
        logger.info('In get_expired_drug_info')

        expired_drug_list = []
        clauses = []

        for data in canister_expiry_dict:
            c = []
            if data.get("canister_id", None):
                c.append((CanisterTracker.canister_id == data["canister_id"]))
            else:
                continue
            if data.get("expiry_date", None):
                c.append((CanisterTracker.expiration_date == data["expiry_date"]))
            else:
                c.append((CanisterTracker.expiration_date.is_null(True)))

            clauses.append(functools.reduce(operator.and_, c))
        clauses = functools.reduce(operator.or_, clauses)
        c = []
        c.append(clauses)
        c.append((CanisterTracker.usage_consideration == constants.USAGE_CONSIDERATION_DISCARD))
        c.append((CanisterTracker.qty_update_type_id == constants.CANISTER_QUANTITY_UPDATE_TYPE_DISCARD))
        query = CanisterTracker.select(CanisterTracker.canister_id,
                                       CanisterTracker.expiration_date,
                                       CanisterTracker.lot_number,
                                       (fn.FLOOR(CanisterTracker.quantity_adjusted) * (-1)).alias("trashed_qty"),
                                       DrugMaster.concated_drug_name_field().alias("drug_name"),
                                       DrugMaster.ndc,
                                       DrugMaster.manufacturer).dicts() \
                .join(DrugMaster, on=DrugMaster.id == CanisterTracker.drug_id) \
                .where(functools.reduce(operator.and_, c))
        print(query)
        print(len(list(query)))
        print(list(query))
        for data in query:
            expired_drug_list.append(data)

        return expired_drug_list
    except Exception as e:
        logger.error(f'Error in get_expired_drug_info')
        raise e


@log_args_and_response
def remove_pack_canister_from_replenish_skipped_canister(pack_ids, canister_id):
    try:
        status = ReplenishSkippedCanister.delete().where(ReplenishSkippedCanister.pack_id.in_(pack_ids),
                                                         ReplenishSkippedCanister.canister_id == canister_id).execute()

        logger.info(f"In remove_pack_canister_from_replenish_skipped_canister, delete status: {status}")

        return status
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error in remove_pack_canister_from_replenish_skipped_canister: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")
        raise e

def get_empty_locations_of_quadrant(device_id,quadrant):
    try:
        locations = []

        if device_id:
            for record in CanisterMaster.select(LocationMaster.device_id,
                                                LocationMaster.id,
                                                LocationMaster.container_id,
                                                LocationMaster.display_location,
                                                ContainerMaster.drawer_name,
                                                ContainerMaster.drawer_type,
                                                ContainerMaster.drawer_level,
                                                LocationMaster.location_number).dicts() \
                    .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                    .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                    .where(
                    (CanisterMaster.location_id > 0 | ~(LocationMaster.is_disabled == settings.is_location_active)),
                    LocationMaster.device_id == device_id,
                    LocationMaster.quadrant << quadrant,
                    ContainerMaster.drawer_type.not_in([settings.SIZE_OR_TYPE["MFD"]])):
                locations.append((record['id'],record['drawer_level']))

        return locations

    except Exception as e:
        logger.error(f'Error in get_expired_drug_info')
        raise e
@log_args_and_response
def db_validate_testing_status(rfid):
    try:
        query = CanisterTestingStatus.select().dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTestingStatus.canister_id) \
            .where(CanisterMaster.rfid == rfid)
        if not query.exists():
            return True
        else:
            return False
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_validate_testing_status {}".format(e))
        raise e
    except Exception as e:
        logger.error(f'Error in db_validate_testing_status {e}')
        raise e

@log_args_and_response
def get_canister_history_dao(canister_id, records_from_date):
    try:
        query = CanisterStatusHistory.select(CanisterStatusHistory.created_by, CanisterStatusHistory.created_date,
                                             CanisterStatusHistoryComment.comment).dicts() \
                                     .join(CanisterStatusHistoryComment, on=CanisterStatusHistory.id ==
                                                        CanisterStatusHistoryComment.canister_status_history_id) \
                                     .where(CanisterStatusHistory.canister_id == canister_id,
                                            fn.DATE(CanisterStatusHistory.created_date) > records_from_date) \
                                     .order_by(CanisterStatusHistory.created_date.desc()) \

        return list(query)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_history_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_history_dao {}".format(e))
        raise e


@log_args_and_response
def get_canister_last_replenished_drug_dao(canister_id):
    try:
        drug_id = CanisterTracker.db_get_canister_last_replenished_drug_dao(canister_id)
        return drug_id
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_last_replenished_drug_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_last_replenished_drug_dao {}".format(e))
        raise e


@log_args_and_response
def db_create_canister_orders(canister_orders_list):
    try:
        status = CanisterOrders.insert_many(canister_orders_list).execute()
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_create_canister_orders {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_create_canister_orders {}".format(e))
        raise e


@log_args_and_response
def get_canister_order_history_dao(filter_fields, sort_fields, paginate):
    try:
        clauses = []
        exact_search_fields = ['drug_name']
        membership_search_fields = ['status']
        fields_dict = {
            "drug_name": DrugMaster.concated_drug_name_field(),
            "status": CanisterOrders.order_status,
            "order_date": CanisterOrders.created_date

        }
        order_list = []
        # order_list = [CanisterOrders.id.desc()]
        if filter_fields:
            clauses = get_filters(clauses=clauses, fields_dict=fields_dict, filter_dict=filter_fields,
                                  exact_search_fields=exact_search_fields, membership_search_fields=membership_search_fields)
        if sort_fields:
            order_list = get_orders(order_list, fields_dict, sort_fields)
        query = (CanisterOrders.select(CanisterOrders,
                                       DrugMaster.ndc,
                                       DrugMaster.concated_drug_name_field().alias('drug_name'),
                                       DrugMaster.image_name,
                                       DrugMaster.imprint,
                                       DrugMaster.color,
                                       CustomDrugShape.name.alias("shape"),
                                       CanisterOrders.order_status)
                 .join(DrugMaster, on=CanisterOrders.drug_id == DrugMaster.id)
                 .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                       (UniqueDrug.txr == DrugMaster.txr)))
                 .join(DrugDimension, on=UniqueDrug.id == DrugDimension.unique_drug_id)
                 .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id)
                 )

        drug_list = []
        for record in query.dicts():
            name_ndc = record['drug_name'] + '(' + record['ndc'] + ')'
            drug_list.append(name_ndc)
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        count = query.count()

        if not order_list:
            order_list = [CanisterOrders.created_date.desc()]

        if order_list:
            query = query.order_by(*order_list)
        if paginate:
            query = apply_paginate(query, paginate)

        return list(query.dicts()), drug_list, count
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_order_history_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_order_history_dao {}".format(e))
        raise e


@log_args_and_response
def get_ndc_list_for_deactivated_canisters(ndc_list):
    try:
        response_ndc_list = []
        if ndc_list:
            query = (DrugMaster.select(fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.active)).alias("is_active"),
                                           DrugMaster.ndc.alias('ndc')
                                           )
                         .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.drug_id == DrugMaster.id)
                         .where(DrugMaster.ndc.in_(ndc_list)).group_by(DrugMaster.id))
            for record in query.dicts():
                if record['is_active'] and '1' in record['is_active']:
                    continue
                response_ndc_list.append(record['ndc'])
        return response_ndc_list
    except Exception as e:
        raise e


@log_args_and_response
def get_data_for_order_canister():
    try:
        current_date = get_current_date()
        query = (CanisterOrders.select(
            fn.DATE(CanisterOrders.created_date).alias("order_date"),
            CanisterOrders.id.alias("order_id"),
                                       CanisterOrders.drug_id,
                                       DrugMaster.ndc,
                                       DrugMaster.drug_name,
                                       DrugMaster.formatted_ndc,
                                       DrugMaster.txr,
                                       DrugMaster.strength,
                                       DrugMaster.strength_value,
                                       DrugDimension.width,
                                       DrugDimension.depth,
                                       DrugDimension.length,
                                       DrugDimension.fillet,
                                       CustomDrugShape.name.alias("shape")
                                       )
                 .join(DrugMaster, on= DrugMaster.id == CanisterOrders.drug_id)
                 .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                       (UniqueDrug.txr == DrugMaster.txr)))
                 .join(DrugDimension, on=UniqueDrug.id == DrugDimension.unique_drug_id)
                 .join(CustomDrugShape, on=CustomDrugShape.id == DrugDimension.shape).where(
            fn.DATE(CanisterOrders.created_date) == current_date)
        )
        return list(query.dicts())
    except Exception as e:
        logger.error("error in get_data_for_order_canister {}".format(e))
        return e


@log_args_and_response
def db_update_canister_order_status(drug_list, status):
    try:
        status = CanisterOrders.update(order_status=status).where(CanisterOrders.drug_id << drug_list).execute()
        return status

    except Exception as e:
        logger.error(e)
        return e


@log_args_and_response
def db_get_deactive_canisters_new(width, depth, length, all_flag=False):
    # todo decide based on deleted canister

    sub_query_1 = (CanisterStatusHistory.select(fn.MAX(CanisterStatusHistory.id).alias("canister_status_history_id"),
                                               CanisterStatusHistory.canister_id.alias("canister_id"))
                   .group_by(CanisterStatusHistory.canister_id).alias("sub_query_1"))

    sub_query = (CanisterStatusHistoryComment.select(sub_query_1.c.canister_id.alias("canister_id"),
                                                     CanisterStatusHistoryComment.comment.alias("comment"),
                                                     CanisterStatusHistoryComment.canister_status_history_id)
                 .join(sub_query_1, on=CanisterStatusHistoryComment.canister_status_history_id == sub_query_1.c.canister_status_history_id).alias("sub_query"))
    canister_list = []
    clauses = list()
    clauses.append((CanisterMaster.active == 0))
    clauses.append(CanisterMaster.rfid.is_null(False))
    clauses.append(BigCanisterStick.width == float(width))
    clauses.append(BigCanisterStick.depth == float(depth))
    clauses.append(SmallCanisterStick.length == float(length))
    clauses.append(ChangeNdcHistory.id.is_null(True))
    clauses.append((sub_query.c.comment.not_in([constants.DEACTIVE_REASON_ISSUE_WITH_EERPROM,
                                                constants.DEACTIVE_REASON_BROKEN_CANISTER])) |
                   (sub_query.c.comment.is_null(True)))

    try:
        query = BigCanisterStick.select(
            CanisterMaster.id.alias('canister_id'),
            BigCanisterStick.width.alias('Recommended_Big_Stick_Width'),
            BigCanisterStick.depth.alias('Recommended_Big_Stick_Depth'),
            BigCanisterStick.serial_number.alias('Recommended_Big_Stick_Serial_Number'),
            SmallCanisterStick.length.alias('Recommended_Small_Stick_Serial_Number_Length'),
        ).dicts() \
            .join(CanisterStick, JOIN_LEFT_OUTER, on=CanisterStick.big_canister_stick_id == BigCanisterStick.id) \
            .join(SmallCanisterStick, JOIN_LEFT_OUTER,
                  on=CanisterStick.small_canister_stick_id == SmallCanisterStick.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.canister_stick_id == CanisterStick.id) \
            .join(ChangeNdcHistory, JOIN_LEFT_OUTER, on=CanisterMaster.id == ChangeNdcHistory.old_canister_id)\
            .join(sub_query, JOIN_LEFT_OUTER, on=(sub_query.c.canister_id == CanisterMaster.id))\
            .where(functools.reduce(operator.and_, clauses))
        for record in query:
            canister_list.append(record)
        return canister_list
    except Exception as e:
        logger.info(e)
        return e

    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError


@log_args_and_response
def db_update_canister_quantity(canister_id, quantity):
    try:
        status = CanisterMaster.update(available_quantity=quantity).where(CanisterMaster.id == canister_id).execute()
        return status
    except Exception as e:
        return e


@log_args_and_response
def db_update_canister_tracker(canister_id, quantity):
    try:
        case_quantity_dict = {}
        status = None
        if quantity > 0:
            orders = [CanisterTracker.id.desc()]
        else:
            orders = [CanisterTracker.id.asc()]

        query = ((CanisterTracker.select(CanisterTracker.id,
                                        CanisterTracker.canister_id,
                                        CanisterTracker.case_id,
                                        CanisterTracker.quantity_adjusted)
                 .where(CanisterTracker.canister_id == canister_id,
                        CanisterTracker.usage_consideration.in_([constants.USAGE_CONSIDERATION_PENDING])))
                 .order_by(*orders))
        if quantity > 0:
            if list(query.dicts()):
                update_data = list(query.dicts())[0]
                updated_quantity = update_data['quantity_adjusted'] + quantity
                status = (CanisterTracker.update(quantity_adjusted=updated_quantity)
                          .where(CanisterTracker.id == update_data['id']).execute())
                case_quantity_dict[update_data['case_id']] = updated_quantity
            return status, case_quantity_dict
        else:
            usage_list = []
            quantity_data = {}
            for record in query.dicts():
                if quantity >= 0:
                    break
                if record['quantity_adjusted'] + quantity <= 0:
                    quantity = record['quantity_adjusted'] + quantity
                    usage_list.append(record['id'])
                else:
                    quantity = record['quantity_adjusted'] + quantity
                    quantity_data = {
                        "quantity_adjusted": quantity,
                        "id": record['id']
                    }
                    case_quantity_dict[record['case_id']] = quantity
            if usage_list:
                status = (CanisterTracker.update(usage_consideration=constants.USAGE_CONSIDERATION_DONE)
                          .where(CanisterTracker.id.in_(usage_list)).execute())
            if quantity_data:
                status = (CanisterTracker.update(quantity_adjusted=quantity_data['quantity_adjusted'])
                          .where(CanisterTracker.id == quantity_data['id']).execute())
            return status, case_quantity_dict

    except Exception as e:
        return e


@log_args_and_response
def db_get_last_canister_replenish_id_dao(canister_id):
    try:
        replenish_data = CanisterTracker.db_get_last_canister_replenish_id(canister_id)
        return replenish_data
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in db_get_last_canister_replenish_id {}".format(e))
        raise e
    except Exception as e:
        logger.error("Error in db_get_last_canister_replenish_id {}".format(e))
        raise e
