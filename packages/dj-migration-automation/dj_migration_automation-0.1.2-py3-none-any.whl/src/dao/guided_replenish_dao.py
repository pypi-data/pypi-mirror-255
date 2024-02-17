import os
import sys

import couchdb
from peewee import fn, JOIN_LEFT_OUTER, DoesNotExist, InternalError, IntegrityError, DataError, SQL
from playhouse.shortcuts import cast
from datetime import datetime, date, timedelta
import settings
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, get_canister_volume, \
    get_max_possible_drug_quantities_in_canister
from src.dao.canister_transfers_dao import db_get_drawer_wise_empty_locations
from src.model.model_batch_master import BatchMaster
from src.dao.pack_dao import db_get_progress_filling_left_pack_ids
from src.model.model_canister_master import CanisterMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_drug_details import DrugDetails
from src.model.model_pack_queue import PackQueue
from src.model.model_slot_details import SlotDetails
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster

from src.model.model_pack_details import PackDetails
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_analysis import PackAnalysis
from realtime_db.dp_realtimedb_interface import Database
from src import constants
from src.api_utility import get_results
from src.dao.couch_db_dao import get_couch_db_database_name
from src.exceptions import RealTimeDBException, NoLocationExists
from src.model.model_container_master import ContainerMaster
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_drug_dimension import DrugDimension
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_guided_meta import GuidedMeta
from src.model.model_guided_misplaced_canister import GuidedMisplacedCanister
from src.model.model_guided_tracker import GuidedTracker
from src.model.model_guided_transfer_cycle_history import GuidedTransferCycleHistory
from src.model.model_guided_transfer_history_comment import GuidedTransferHistoryComment
from src.model.model_location_master import LocationMaster

logger = settings.logger


@log_args_and_response
def get_canister_transfer_to_trolley_guided(company_id, device_id, mini_batch, trolley_id, drawer_id):
    try:
        # canister_list = list()
        device_id = int(device_id)
        couch_db_canisters = list()
        response_list = list()
        drawers_to_unlock = dict()
        delicate_drawers_to_unlock = dict()
        LocationMasterAlias1 = LocationMaster.alias()
        LocationMasterAlias2 = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        status_list = constants.guided_tracker_to_trolley_status_list
        status_list.append(constants.GUIDED_TRACKER_TO_TROLLEY_DONE)
        # commenting this query as now it is merged to below query
        # canister_list_query = GuidedTracker.select(
        #     fn.IF(GuidedTracker.alternate_canister_id.is_null(False), GuidedTracker.alternate_canister_id,
        #           GuidedTracker.source_canister_id).alias('transfer_canister')).dicts() \
        #     .join(LocationMasterAlias2, JOIN_LEFT_OUTER, on=LocationMasterAlias2.id == GuidedTracker.cart_location_id) \
        #     .where(GuidedTracker.guided_meta_id == mini_batch,
        #            GuidedTracker.transfer_status << constants.guided_tracker_to_trolley_status_list,
        #            LocationMasterAlias2.device_id == trolley_id,
        #            LocationMasterAlias2.container_id == drawer_id,
        #            )
        #
        # for record in canister_list_query:
        #     canister_list.append(record['transfer_canister'])

        query = GuidedTracker.select(CanisterMaster.active,
                                     GuidedTracker.transfer_status,
                                     CanisterMaster.id.alias('canister_id'),
                                     fn.IF(
                                         CanisterMaster.expiry_date <= date.today() + timedelta(
                                             settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                         constants.EXPIRED_CANISTER,
                                         fn.IF(
                                             CanisterMaster.expiry_date <= date.today() + timedelta(
                                                 settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                             constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias(
                                         "expiry_status"),
                                     DrugMaster.id.alias('drug_id'),
                                     DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                     DrugMaster.imprint,
                                     DrugMaster.image_name,
                                     DrugMaster.color,
                                     DrugMaster.shape,
                                     DeviceMasterAlias.device_type_id.alias('dest_device_type_id'),
                                     LocationMaster.id.alias('source_canister_location'),
                                     LocationMaster.container_id.alias('source_container'),
                                     LocationMaster.display_location.alias('source_display_location'),
                                     LocationMaster.device_id.alias('source_can_device'),
                                     DeviceMaster.ip_address.alias("device_ip_address"),
                                     DeviceMaster.name.alias('source_device_name'),
                                     DeviceMaster.device_type_id.alias('source_device_type_id'),
                                     ContainerMaster.id.alias("container_id"),
                                     ContainerMaster.serial_number,
                                     ContainerMaster.drawer_name,
                                     ContainerMaster.secondary_ip_address,
                                     ContainerMaster.secondary_mac_address,
                                     ContainerMaster.ip_address,
                                     ContainerMaster.mac_address,
                                     ContainerMaster.shelf,
                                     DrugDetails.last_seen_by,
                                     DrugDetails.last_seen_date,
                                     fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                           DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                     fn.IF(GuidedTracker.transfer_status ==
                                           constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE, True, False)
                                     .alias('highlight_alternate_canister'),
                                     UniqueDrug.is_delicate.alias('is_delicate')).dicts() \
            .join(CanisterMaster,
                  on=(fn.IF(GuidedTracker.alternate_canister_id.is_null(False), GuidedTracker.alternate_canister_id,
                            GuidedTracker.source_canister_id)) == CanisterMaster.id) \
            .join(LocationMasterAlias1, JOIN_LEFT_OUTER, on=LocationMasterAlias1.id == GuidedTracker.cart_location_id) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER,
                  on=LocationMasterAlias2.id == GuidedTracker.destination_location_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMasterAlias2.device_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == settings.is_drug_active) &
                                                         (DrugStockHistory.company_id == company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=DrugDetails.unique_drug_id == UniqueDrug.id) \
            .where(CanisterMaster.company_id == company_id,
                   GuidedTracker.guided_meta_id == mini_batch,
                   ((DeviceMaster.id == device_id) | (DeviceMaster.id.is_null(True)) | (
                               GuidedTracker.transfer_status == constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE)),
                   GuidedTracker.transfer_status << status_list,
                   LocationMasterAlias1.device_id == trolley_id,
                   LocationMasterAlias1.container_id == drawer_id) \
            .group_by(CanisterMaster.id) \
            .order_by(UniqueDrug.is_delicate.desc(),
                      LocationMaster.id)

        for record in query:
            if record['canister_id']:
                couch_db_canisters.append(record['canister_id'])

            if record['transfer_status'] == constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE:
                record['alternate_canister'] = True
            else:
                record['alternate_canister'] = False

            if record['source_can_device'] and int(record['source_can_device']) == device_id:
                if not record['is_delicate']:
                    if record['drawer_name'] not in drawers_to_unlock.keys():
                        drawers_to_unlock[record['drawer_name']] = {'id': record["container_id"],
                                                                    'drawer_name': record["drawer_name"],
                                                                    'serial_number': record["serial_number"],
                                                                    "device_ip_address": record["device_ip_address"],
                                                                    'ip_address': record['ip_address'],
                                                                    'secondary_ip_address': record['secondary_ip_address'],
                                                                    'device_type_id': record['source_device_type_id'],
                                                                    'shelf': record['shelf'],
                                                                    'to_device': list(),
                                                                    'from_device': list()}
                    if record["source_display_location"] not in drawers_to_unlock[record['drawer_name']]["from_device"]:
                        drawers_to_unlock[record['drawer_name']]["from_device"].append(record["source_display_location"])
                else:
                    if record['drawer_name'] not in delicate_drawers_to_unlock.keys():
                        delicate_drawers_to_unlock[record['drawer_name']] = {'id': record["container_id"],
                                                                    'drawer_name': record["drawer_name"],
                                                                    'serial_number': record["serial_number"],
                                                                    "device_ip_address": record["device_ip_address"],
                                                                    'ip_address': record['ip_address'],
                                                                    'secondary_ip_address': record['secondary_ip_address'],
                                                                    'device_type_id': record['source_device_type_id'],
                                                                    'shelf': record['shelf'],
                                                                    'to_device': list(),
                                                                    'from_device': list()}
                    if record["source_display_location"] not in delicate_drawers_to_unlock[record['drawer_name']]["from_device"]:
                        delicate_drawers_to_unlock[record['drawer_name']]["from_device"].append(record["source_display_location"])
            response_list.append(record)

        return response_list, drawers_to_unlock, delicate_drawers_to_unlock, couch_db_canisters
    except DoesNotExist as e:
        logger.error("error in get_canister_transfer_to_trolley_guided {}".format(e))
        raise DoesNotExist
    except InternalError as e:
        logger.error("error in get_canister_transfer_to_trolley_guided {}".format(e))
        raise InternalError


@log_args_and_response
def get_canister_transfer_from_trolley_guided(company_id, device_id, mini_batch, trolley_id,
                                              drawer_id, guided_canister_status):
    try:
        device_id = int(device_id)
        canister_list = list()
        response_list = list()
        # swap_canister = list()
        # alternate_source_canister = dict()
        # drawers_to_unlock = dict()
        LocationMasterAlias1 = LocationMaster.alias()
        LocationMasterAlias2 = LocationMaster.alias()
        LocationMasterAlias3 = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()
        dest_quad = None
        canister_type_dict = {"small_canister_count": 0, "big_canister_count": 0,"delicate_canister_count":0}

        canister_list_query = GuidedTracker.select(LocationMasterAlias1.container_id, ContainerMaster.drawer_name,
                                                   fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                         GuidedTracker.alternate_canister_id,
                                                         GuidedTracker.source_canister_id).alias(
                                                       'transfer_canister'),
                                                   fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                         True,
                                                         False).alias(
                                                       'swap_canister'),
                                                   LocationMasterAlias1.device_id.alias("dest_device"),
                                                   LocationMasterAlias1.quadrant.alias("dest_quadrant"),
                                                   LocationMasterAlias3.device_id.alias("current_device"),
                                                   LocationMasterAlias3.quadrant.alias("current_quadrant"),
                                                   ContainerMasterAlias.drawer_type.alias("current_drawer_type"),
                                                   ContainerMasterAlias.drawer_level.alias("current_drawer_level"),
                                                   DeviceMaster.name.alias("current_device_name"),
                                                   GuidedTracker.source_canister_id,
                                                   GuidedTracker.alternate_canister_id,
                                                   ContainerMaster.ip_address,
                                                   ContainerMaster.mac_address,
                                                   ContainerMaster.secondary_ip_address,
                                                   ContainerMaster.secondary_mac_address,
                                                   CanisterMaster.canister_type,
                                                   fn.IF(GuidedTracker.transfer_status ==
                                                         constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE, True, False)
                                                   .alias('highlight_alternate_canister'),
                                                   UniqueDrug.is_delicate
                                                   ).dicts() \
            .join(LocationMasterAlias1, on=GuidedTracker.destination_location_id == LocationMasterAlias1.id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias1.container_id) \
            .join(LocationMasterAlias2, on=LocationMasterAlias2.id == GuidedTracker.cart_location_id) \
            .join(CanisterMaster, on=(fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                            GuidedTracker.alternate_canister_id,
                                            GuidedTracker.source_canister_id)) == CanisterMaster.id) \
            .join(DrugMaster, on = CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(LocationMasterAlias3, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMasterAlias3.id) \
            .join(ContainerMasterAlias, JOIN_LEFT_OUTER,
                  on=ContainerMasterAlias.id == LocationMasterAlias3.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMasterAlias3.device_id == DeviceMaster.id) \
            .where(GuidedTracker.guided_meta_id == mini_batch,
                   GuidedTracker.transfer_status << guided_canister_status,
                   LocationMasterAlias1.device_id == device_id,
                   LocationMasterAlias2.device_id == trolley_id,
                   LocationMasterAlias2.container_id == drawer_id
                   )
        for record in canister_list_query:
            if record["dest_device"] == record["current_device"] and \
                    record["dest_quadrant"] == record["current_quadrant"] and \
                    not (record["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and
                         record["current_drawer_type"] == settings.SIZE_OR_TYPE["SMALL"]):
                if record['is_delicate'] :
                    empty_locations, drawer_data = db_get_drawer_wise_empty_locations(record['dest_device'],
                                                                                      record["dest_quadrant"])
                    first_empty_key = ''
                    if constants.SMALL_CANISTER_CODE in empty_locations.keys():
                        small_canisters = empty_locations[constants.SMALL_CANISTER_CODE]
                        keys_to_remove = [key for key, value in small_canisters.items() if len(value) == 0]
                        for key in keys_to_remove:
                            del small_canisters[key]
                        small_canisters_drawer = sorted(small_canisters.keys())
                        for key in small_canisters_drawer:
                            first_empty_key = key[0]
                            first_empty_loc = small_canisters[key][0]
                            break
                    drawer_level = constants.ROBOT_DRAWER_LEVELS[first_empty_key]
                    if drawer_level < 5 and record["current_drawer_level"] > 4:
                        record["wrong_location"] = True
                        record["empty_location"] = first_empty_loc
                    if not record["wrong_location"]:
                        continue
                else:
                    continue
            elif record["dest_device"] == record["current_device"] and record["dest_quadrant"] != record["current_quadrant"]:
                record["wrong_location"] = True
            canister_list.append(record['transfer_canister'])

        if len(canister_list):
            query = CanisterMaster.select(CanisterMaster.active,
                                          CanisterMaster.id.alias('canister_id'),
                                          CanisterMaster.canister_type,
                                          fn.IF(
                                              CanisterMaster.expiry_date <= date.today() + timedelta(
                                                  settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                              constants.EXPIRED_CANISTER,
                                              fn.IF(
                                                  CanisterMaster.expiry_date <= date.today() + timedelta(
                                                      settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                                  constants.EXPIRES_SOON_CANISTER,
                                                  constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                          DrugMaster.id.alias('drug_id'),
                                          DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                          LocationMaster.device_id.alias('dest_can_device'),
                                          LocationMaster.quadrant.alias('dest_quadrant'),
                                          DeviceMasterAlias.name.alias('dest_device_name'),
                                          DeviceMasterAlias.device_type_id.alias('dest_device_type_id'),
                                          ContainerMaster.drawer_name,
                                          ContainerMasterAlias.drawer_name.alias('current_drawer_name'),
                                          ContainerMasterAlias.secondary_ip_address,
                                          ContainerMasterAlias.secondary_mac_address,
                                          ContainerMasterAlias.ip_address,
                                          ContainerMasterAlias.mac_address,
                                          ContainerMasterAlias.serial_number,
                                          LocationMasterAlias1.display_location.alias('current_display_location'),
                                          LocationMasterAlias1.quadrant.alias('current_quadrant'),
                                          LocationMasterAlias1.device_id.alias('current_device_id'),
                                          DeviceMaster.name.alias('current_device_name'),
                                          DeviceMaster.device_type_id.alias('current_device_type_id'),
                                          DrugMaster.imprint,
                                          DrugMaster.image_name,
                                          DrugMaster.color,
                                          DrugMaster.shape,
                                          DrugDetails.last_seen_by,
                                          DrugDetails.last_seen_date,
                                          GuidedTracker.transfer_status,
                                          fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                                DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                          CanisterMaster.canister_type,
                                          ContainerMasterAlias.drawer_type,
                                          UniqueDrug.is_delicate.alias('is_delicate')
                                          ).dicts() \
                .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(GuidedTracker, on=(fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                               GuidedTracker.alternate_canister_id,
                                               GuidedTracker.source_canister_id)) == CanisterMaster.id) \
                .join(LocationMaster, on=LocationMaster.id == GuidedTracker.destination_location_id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMasterAlias, on=DeviceMasterAlias.id == ContainerMaster.device_id) \
                .join(LocationMasterAlias1, JOIN_LEFT_OUTER, on=LocationMasterAlias1.id == CanisterMaster.location_id) \
                .join(ContainerMasterAlias, JOIN_LEFT_OUTER,
                      on=ContainerMasterAlias.id == LocationMasterAlias1.container_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias1.device_id) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                       & (UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == settings.is_drug_active)
                                                             & (DrugStockHistory.company_id == company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                        (DrugDetails.company_id == CanisterMaster.company_id))) \
                .where(CanisterMaster.company_id == company_id,
                       GuidedTracker.guided_meta_id == mini_batch,
                       GuidedTracker.transfer_status << guided_canister_status,
                       CanisterMaster.id << canister_list) \
                .group_by(CanisterMaster.id) \
                .order_by(UniqueDrug.is_delicate,LocationMaster.container_id)

            for record in query:
                # flag to show this are for placing canisters in robot
                record["to_device"] = True
                # Added Below condition to guide user to place canister at recommend quadrant
                # if user placed a canister at wrong quadrant or device

                # If Canister Size = Big and Drawer Size = Small then notify the user about issue with size of canister
                record["wrong_size"] = (True if record["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and
                                                record["drawer_type"] == settings.SIZE_OR_TYPE["SMALL"] else False)

                if record['current_device_id'] == trolley_id:
                    record["wrong_location"] = False

                # elif record['is_delicate'] and record['dest_quadrant'] == record['current_quadrant']:
                #     empty_locations, drawer_data = db_get_drawer_wise_empty_locations(record['dest_can_device'],
                #                                                                       record["dest_quadrant"])
                #     first_empty_key = ''
                #     if constants.SMALL_CANISTER_CODE in empty_locations.keys():
                #         small_canisters = empty_locations[constants.SMALL_CANISTER_CODE]
                #         small_canisters = sorted(small_canisters.keys())
                #         for key in small_canisters:
                #             first_empty_key = key[0]
                #             first_empty_loc = small_canisters[key][0]
                #             break
                #     drawer_level = constants.ROBOT_DRAWER_LEVELS[first_empty_key]
                #     if drawer_level < 5 and record["current_drawer_level"] > 4:
                #         record["wrong_location"] = True
                #         record["empty_location"] = first_empty_loc

                else:
                    record["wrong_location"] = True
                    record["current_device"] = record["current_device_id"]
                    record["current_device_name"] = record["current_device_name"]

                if record['transfer_status'] == constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE:
                    record['alternate_canister'] = True
                else:
                    record['alternate_canister'] = False

                if not dest_quad:
                    dest_quad = record['dest_quadrant']

                if record['canister_type'] == settings.SIZE_OR_TYPE['BIG']:
                    canister_type_dict["big_canister_count"] += 1
                else:
                    if record['is_delicate']:
                        canister_type_dict["delicate_canister_count"] += 1
                    else:
                        canister_type_dict["small_canister_count"] += 1
                response_list.append(record)

        return response_list, dest_quad, canister_type_dict
    except DoesNotExist as e:
        logger.error("error in get_canister_transfer_from_trolley_guided {}".format(e))
        raise DoesNotExist
    except InternalError as e:
        logger.error("error in get_canister_transfer_from_trolley_guided {}".format(e))
        raise InternalError
    except Exception as e:
        logger.error("error in get_canister_transfer_from_trolley_guided {}".format(e))


@log_args_and_response
def get_canister_transfer_from_trolley_guided_csr(company_id, device_id, mini_batch, trolley_id,
                                                  drawer_id, guided_canister_status):
    try:
        device_id = int(device_id)
        canister_list = list()
        response_list = list()
        # drawers_to_unlock = dict()
        canisters_to_be_transferred = list()
        LocationMasterAlias1 = LocationMaster.alias()
        LocationMasterAlias2 = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()

        canister_list_query = GuidedTracker.select(
            fn.IF(GuidedTracker.transfer_status.in_(constants.guided_tracker_to_robot_skipped_codes),
                  fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                        GuidedTracker.alternate_canister_id,
                        GuidedTracker.source_canister_id),
                  GuidedTracker.source_canister_id).alias('transfer_canister'),
            LocationMasterAlias1.container_id.alias("dest_container_id"),
            LocationMasterAlias1.display_location,
            ContainerMaster.drawer_name,
            ContainerMaster.serial_number,
            ContainerMaster.ip_address,
            ContainerMaster.secondary_ip_address,
        ).dicts() \
            .join(LocationMasterAlias1, on=GuidedTracker.destination_location_id == LocationMasterAlias1.id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias1.container_id) \
            .join(LocationMasterAlias2, on=LocationMasterAlias2.id == GuidedTracker.cart_location_id) \
            .where(GuidedTracker.guided_meta_id == mini_batch,
                   GuidedTracker.transfer_status << guided_canister_status,
                   LocationMasterAlias1.device_id == device_id,
                   LocationMasterAlias2.device_id == trolley_id,
                   LocationMasterAlias2.container_id == drawer_id,
                   )

        for record in canister_list_query:
            canister_list.append(record['transfer_canister'])

        if len(canister_list):
            query = CanisterMaster.select(CanisterMaster.active,
                                          CanisterMaster.id.alias('canister_id'),
                                          fn.IF(
                                              CanisterMaster.expiry_date <= date.today() + timedelta(
                                                  settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                              constants.EXPIRED_CANISTER,
                                              fn.IF(
                                                  CanisterMaster.expiry_date <= date.today() + timedelta(
                                                      settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                                  constants.EXPIRES_SOON_CANISTER,
                                                  constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                          GuidedTracker.transfer_status,
                                          DrugMaster.id.alias('drug_id'),
                                          DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                          LocationMaster.container_id.alias('dest_container'),
                                          LocationMaster.display_location.alias('dest_display_location'),
                                          LocationMaster.device_id.alias('dest_can_device'),
                                          DeviceMasterAlias.name.alias("dest_device_name"),
                                          DeviceMasterAlias.ip_address.alias("device_ip_address"),
                                          ContainerMaster.drawer_name,
                                          ContainerMaster.serial_number.alias("dest_serial_number"),
                                          ContainerMaster.ip_address,
                                          ContainerMaster.secondary_ip_address,
                                          LocationMasterAlias1.display_location.alias('current_disp_loc'),
                                          LocationMasterAlias1.container_id.alias('current_container'),
                                          LocationMasterAlias1.device_id.alias('current_device_id'),
                                          DeviceMaster.name.alias('current_device_name'),
                                          DeviceMaster.device_type_id.alias('current_device_type_id'),
                                          DrugMaster.imprint,
                                          DrugMaster.image_name,
                                          DrugMaster.color,
                                          DrugMaster.shape,
                                          DrugDetails.last_seen_by,
                                          DrugDetails.last_seen_date,
                                          fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                                DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                          CanisterMaster.canister_type,
                                          ContainerMasterAlias.drawer_type,
                                          UniqueDrug.is_delicate
                                          ).dicts() \
                .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(GuidedTracker,
                      on=fn.IF(GuidedTracker.transfer_status.in_(constants.guided_tracker_to_robot_skipped_codes),
                               fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                     GuidedTracker.alternate_canister_id,
                                     GuidedTracker.source_canister_id),
                               GuidedTracker.source_canister_id) == CanisterMaster.id) \
                .join(LocationMaster, on=LocationMaster.id == GuidedTracker.destination_location_id) \
                .join(DeviceMasterAlias, on=DeviceMasterAlias.id == LocationMaster.device_id) \
                .join(LocationMasterAlias1, JOIN_LEFT_OUTER, on=LocationMasterAlias1.id == CanisterMaster.location_id) \
                .join(ContainerMasterAlias, JOIN_LEFT_OUTER,
                      on=LocationMasterAlias1.container_id == ContainerMasterAlias.id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias1.device_id) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                       & (UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == settings.is_drug_active) &
                                                             (DrugStockHistory.company_id == company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=DrugDetails.unique_drug_id == UniqueDrug.id) \
                .where(CanisterMaster.company_id == company_id,
                       GuidedTracker.guided_meta_id == mini_batch,
                       DeviceMaster.id != device_id,
                       GuidedTracker.transfer_status << guided_canister_status,
                       CanisterMaster.id << canister_list) \
                .group_by(CanisterMaster.id) \
                .order_by(LocationMaster.container_id)

            for record in query:
                canisters_to_be_transferred.append(record["canister_id"])
                record['swap_canister'] = False

                # If Canister Size = Big and Drawer Size = Small then notify the user about issue with size of canister
                record["wrong_size"] = (True if record["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and
                                                record["drawer_type"] == settings.SIZE_OR_TYPE["SMALL"] else False)

                # commenting below code to recommend dynamic location
                # if record['drawer_name'] not in drawers_to_unlock:
                #     drawers_to_unlock[record['drawer_name']] = {'id': record["dest_container"],
                #                                                 'drawer_name': record["drawer_name"],
                #                                                 'serial_number': record["dest_serial_number"],
                #                                                 "device_ip_address": record["device_ip_address"],
                #                                                 'ip_address': record['ip_address'],
                #                                                 'secondary_ip_address': record['secondary_ip_address'],
                #                                                 'to_device': list(),
                #                                                 'from_device': list()}
                # if record["dest_display_location"] not in drawers_to_unlock[record['drawer_name']]["to_device"]:
                #     drawers_to_unlock[record['drawer_name']]["to_device"].append(record["dest_display_location"])

                # Added Below condition to guide user to place canister in recommended drawer
                # if user placed a canister at wrong drawer or device
                if record['current_device_id'] == trolley_id:
                    record["wrong_location"] = False
                    record["current_display_location"] = None
                    record["current_device"] = None
                    record["current_device_name"] = None
                else:
                    record["wrong_location"] = True
                    record["current_display_location"] = record["current_disp_loc"]
                    record["current_device"] = record["current_device_name"]
                    record["current_device_name"] = record["current_device_name"]

                response_list.append(record)

        return response_list, canisters_to_be_transferred
    except DoesNotExist as e:
        logger.error("error in get_canister_transfer_from_trolley_guided_csr {}".format(e))
        raise DoesNotExist
    except InternalError as e:
        logger.error("error in get_canister_transfer_from_trolley_guided_csr {}".format(e))
        raise InternalError


@log_args_and_response
def get_guided_trolley_from_mini_batch(cycle_id):
    """
    Function to get guided trolley id from cycle id
    @param cycle_id: int
    @return: int
    """
    try:
        query = GuidedMeta.select(GuidedMeta.cart_id).dicts() \
            .where(GuidedMeta.id == cycle_id)

        for record in query:
            return record['cart_id']

    except DoesNotExist as e:
        logger.error("error in get_guided_trolley_from_mini_batch {}".format(e))
        raise DoesNotExist
    except InternalError as e:
        logger.error("error in get_guided_trolley_from_mini_batch {}".format(e))
        raise InternalError


@log_args_and_response
def check_if_guided_replenish_exist_for_batch(batch_id):
    """
    Function to check if there is any guided replenish executed for batch
    @param batch_id: int
    @return: bool
    """
    try:
        query = GuidedMeta.select().dicts() \
            .where(GuidedMeta.batch_id == batch_id)

        for record in query:
            logger.info("In check_if_guided_replenish_exist_for_batch: guided_meta_id: {}".format(record["id"]))
            return True
        return False

    except DoesNotExist as e:
        logger.error("error in check_if_guided_replenish_exist_for_batch {}".format(e))
        raise DoesNotExist
    except InternalError as e:
        logger.error("error in check_if_guided_replenish_exist_for_batch {}".format(e))
        raise InternalError
    except Exception as e:
        logger.error("error in check_if_guided_replenish_exist_for_batch {}".format(e))
        raise


@log_args_and_response
def update_guided_tracker_location(cycle_id, canister_location_dict):
    try:
        for canister, location in canister_location_dict.items():
            status = GuidedTracker.update(destination_location_id=location,
                                          modified_date=get_current_date_time()) \
                .where(GuidedTracker.guided_meta_id == cycle_id,
                       ((GuidedTracker.source_canister_id == canister) |
                        (GuidedTracker.alternate_canister_id == canister))).execute()
            logger.info(status)

        return None

    except DoesNotExist as e:
        logger.error("error in update_guided_tracker_location {}".format(e))
        return None

    except InternalError as e:
        logger.error("error in update_guided_tracker_location {}".format(e))
        raise InternalError


@log_args_and_response
def update_guided_tracker_status(guided_tracker_ids: list, status: int):
    """
    Function to update canister status in guided tracker
    @param guided_tracker_ids:
    @param status: int
    @return: status
    """
    try:
        update_status = GuidedTracker.update(transfer_status=status,
                                             modified_date=get_current_date_time()).where(
            GuidedTracker.id << guided_tracker_ids).execute()
        logger.info('updated_status {} for guided_tracker_ids: {} with update status: {}'
                    .format(status, guided_tracker_ids, update_status))
        return update_status
    except DoesNotExist as e:
        logger.error("error in update_guided_tracker_status {}".format(e))
        return None
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in update_guided_tracker_status {}".format(e))
        raise e


@log_args_and_response
def update_guided_tracker_status_of_cycle_id(guided_tracker_ids: list, status: int):
    """
    Function to update canister status in guided tracker
    @param guided_tracker_ids:
    @param status: int
    @return: status
    """
    try:
        update_status = GuidedTracker.update(transfer_status=status,
                                             modified_date=get_current_date_time()).where(
            GuidedTracker.id << guided_tracker_ids).execute()
        return update_status
    except DoesNotExist as e:
        logger.error("error in update_guided_tracker_status_of_cycle_id {}".format(e))
        return None
    except InternalError as e:
        logger.error("error in update_guided_tracker_status_of_cycle_id {}".format(e))
        raise InternalError


@log_args_and_response
def update_guided_tracker(update_dict: dict, guided_tracker_id: int):
    """
    Function to update guided tracker
    @param update_dict:
    @param guided_tracker_id:
    @return:
    """
    try:
        canister_update_status1 = GuidedTracker.update(**update_dict) \
            .where(GuidedTracker.id == guided_tracker_id).execute()

        return canister_update_status1

    except(InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_guided_tracker {}".format(e))
        raise e


@log_args_and_response
def db_get_latest_guided_canister_transfer_data(canister_id):
    """
    Function to get canister transfer info if guided transfer flow is in progress
    @param canister_id: int
    @return:
    """
    try:
        LocationMasterAlias = LocationMaster.alias()
        query = GuidedTracker.select(GuidedTracker.source_canister_id,
                                     GuidedTracker.alternate_canister_id,
                                     GuidedTracker.destination_location_id,
                                     GuidedTracker.cart_location_id,
                                     GuidedTracker.guided_meta_id,
                                     GuidedTracker.transfer_status,
                                     LocationMaster.device_id.alias('trolley_id'),
                                     LocationMaster.container_id.alias('trolley_container_id'),
                                     GuidedMeta.batch_id,
                                     GuidedTracker.id.alias('guided_tracker_id'),
                                     LocationMasterAlias.device_id.alias('dest_device'),
                                     LocationMasterAlias.quadrant.alias('dest_quadrant'),
                                     LocationMasterAlias.container_id.alias("dest_container_id"),
                                     LocationMasterAlias.quadrant.alias('dest_quadrant'),
                                     LocationMasterAlias.device_id.alias('dest_device'),
                                     GuidedMeta.status.alias("guided_meta_status"),
                                     DeviceMaster.system_id.alias("dest_system_id")
                                     ).dicts() \
            .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
            .join(LocationMaster, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == GuidedTracker.destination_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .where(((GuidedTracker.source_canister_id == canister_id) |
                    (GuidedTracker.alternate_canister_id == canister_id)),
                   GuidedTracker.transfer_status.not_in(constants.guided_tracker_existing_status_list),
                   GuidedMeta.status.not_in([constants.GUIDED_META_RECOMMENDATION_DONE,
                                             constants.GUIDED_META_TO_CSR_DONE])) \
            .order_by(GuidedTracker.id.desc())

        for record in query:
            return record

    except DoesNotExist as e:
        logger.error("error in db_get_latest_guided_canister_transfer_data {}".format(e))
        return None
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_latest_guided_canister_transfer_data {}".format(e))
        raise


@log_args_and_response
def get_trolley_and_pending_devices_for_guided_transfer_to_trolley(device_id, guided_tx_cycle_id,
                                                                   trolley_id):
    """
    Function to get trolley for guided transfer to trolley flow
    @param device_id: int
    @param guided_tx_cycle_id: int
    @param trolley_id: int
    @return: int
    """
    canister_list = list()
    pending_devices = list()
    device_id = int(device_id)

    try:
        LocationMasterAlias = LocationMaster.alias()
        logger.info("get_trolley_and_pending_devices_for_guided_transfer_to_trolley")
        status_list = constants.guided_tracker_to_trolley_status_list
        status_list.append(constants.GUIDED_TRACKER_TO_TROLLEY_DONE)
        canister_list_query = GuidedTracker.select(
            LocationMasterAlias.device_id,
            fn.IF(GuidedTracker.alternate_canister_id.is_null(True), GuidedTracker.source_canister_id,
                  GuidedTracker.alternate_canister_id).alias('transfer_canister')).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(CanisterMaster,
                  on=fn.IF(GuidedTracker.alternate_canister_id.is_null(False), GuidedTracker.alternate_canister_id,
                           GuidedTracker.source_canister_id) == CanisterMaster.id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == CanisterMaster.location_id) \
            .where(GuidedTracker.guided_meta_id == guided_tx_cycle_id,
                   GuidedTracker.transfer_status << status_list,
                   LocationMaster.device_id == trolley_id)

        for record in canister_list_query:
            logger.info("get_trolley_and_pending_devices_for_guided_transfer_to_trolley record {}".format(record))
            canister_list.append(record['transfer_canister'])

        logger.info("get_trolley_and_pending_devices_for_guided_transfer_to_trolley: canister_list: {}"
                     .format(canister_list))

        if canister_list:
            # todo optimize query to one
            get_current_device_pending_transfer = CanisterMaster.select(CanisterMaster.id).dicts() \
                .join(GuidedTracker, on=((GuidedTracker.source_canister_id == CanisterMaster.id) | (
                        GuidedTracker.alternate_canister_id == CanisterMaster.id))) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
                .where(((LocationMaster.device_id == device_id) | (LocationMaster.id.is_null(True)) | (
                        GuidedTracker.transfer_status == constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE)),
                       CanisterMaster.id << canister_list)

            can_count = get_current_device_pending_transfer.count()

            get_pending_transfer = CanisterMaster.select(LocationMaster.device_id.alias("pending_device_id"),
                                                         DeviceMaster.name.alias("pending_device_name"),
                                                         DeviceMaster.device_type_id.alias("pending_device_type_id"),
                                                         DeviceMaster.system_id.alias(
                                                             "pending_device_system_id")).dicts() \
                .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(DeviceMaster, on=LocationMaster.device_id == DeviceMaster.id) \
                .where(CanisterMaster.id << canister_list,
                       DeviceMaster.device_type_id.not_in([settings.DEVICE_TYPES['Canister Transfer Cart'],
                                                           settings.DEVICE_TYPES['Canister Cart w/ Elevator']])) \
                .group_by(LocationMaster.device_id)

            for record in get_pending_transfer:
                pending_devices.append(record)

            if can_count:
                return trolley_id, pending_devices

        return None, pending_devices

    except DoesNotExist as e:
        logger.error("error in get_trolley_and_pending_devices_for_guided_transfer_to_trolley {}".format(e))
        return None, pending_devices
    except InternalError as e:
        logger.error("error in get_trolley_and_pending_devices_for_guided_transfer_to_trolley {}".format(e))
        raise InternalError


@log_args_and_response
def get_replaced_and_to_robot_skipped_canister_list(cycle_id):
    """
    Function to get replaced canister list from cycle id
    @param batch_id:
    @param cycle_id:
    @return:
    """
    canister_list = list()
    canisters_involved_in_guided_replenish = list()

    try:
        # merged with below query .
        # query = GuidedTracker.select(GuidedTracker.source_canister_id).dicts() \
        #     .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
        #     .join(LocationMaster, on=GuidedTracker.destination_location_id == LocationMaster.id) \
        #     .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
        #     .where(GuidedMeta.batch_id == batch_id,
        #            GuidedTracker.alternate_canister_id.is_null(False),
        #            GuidedTracker.guided_meta_id == cycle_id,
        #            DeviceMaster.device_type_id << [settings.DEVICE_TYPES['ROBOT']],
        #            GuidedTracker.transfer_status << [constants.GUIDED_TRACKER_REPLACED,
        #                                              constants.GUIDED_TRACKER_SKIPPED_AND_REPLACED])

        # to_csr_canisters = GuidedTracker.select(fn.IF(GuidedTracker.transfer_status
        #                                               .in_(constants.guided_tracker_to_robot_skipped_codes),
        #                                               fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
        #                                                     GuidedTracker.alternate_canister_id,
        #                                                     GuidedTracker.source_canister_id),
        #                                               GuidedTracker.source_canister_id).alias("canister_id")).dicts() \
        #     .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
        #     .join(LocationMaster, on=GuidedTracker.destination_location_id == LocationMaster.id) \
        #     .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
        #     .where(GuidedMeta.batch_id == batch_id,
        #            GuidedTracker.guided_meta_id == cycle_id,
        #            DeviceMaster.device_type_id << [settings.DEVICE_TYPES['ROBOT']],
        #            GuidedTracker.transfer_status << constants.guided_tracker_to_csr_status_list)

        query = GuidedTracker.select().dicts() \
            .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
            .join(LocationMaster, on=GuidedTracker.destination_location_id == LocationMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(GuidedTracker.guided_meta_id == cycle_id,
                   DeviceMaster.device_type_id << [settings.DEVICE_TYPES['ROBOT']])

        for record in query:
            if record["alternate_canister_id"]:
                canisters_involved_in_guided_replenish.append(record["alternate_canister_id"])
            if record["source_canister_id"]:
                canisters_involved_in_guided_replenish.append(record["source_canister_id"])

        if canisters_involved_in_guided_replenish:
            canisters_in_transfer_cart = CanisterMaster.select().dicts() \
                .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
                .where(CanisterMaster.id << canisters_involved_in_guided_replenish,
                       DeviceMaster.device_type_id << [settings.DEVICE_TYPES["Canister Transfer Cart"],
                                                       settings.DEVICE_TYPES["Canister Cart w/ Elevator"]])

            for record in canisters_in_transfer_cart:
                canister_list.append(record['id'])

        # # Add skipped canisters - merged with above query
        # skipped_canister_query = GuidedTracker.select(fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
        #                                                     GuidedTracker.alternate_canister_id,
        #                                                     GuidedTracker.source_canister_id).alias("canister_id")) \
        #     .dicts() \
        #     .join(LocationMaster, on=GuidedTracker.destination_location_id == LocationMaster.id) \
        #     .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
        #     .where(GuidedTracker.guided_meta_id == cycle_id,
        #            DeviceMaster.device_type_id << [settings.DEVICE_TYPES['ROBOT']],
        #            GuidedTracker.transfer_status << [constants.GUIDED_TRACKER_TRANSFER_SKIPPED])
        # for record in skipped_canister_query.dicts():
        #     canister_list.append(record['canister_id'])

        return canister_list

    except DoesNotExist as e:
        logger.error("error in get_replaced_and_to_robot_skipped_canister_list {}".format(e))
        return canister_list
    except InternalError as e:
        logger.error("error in get_replaced_and_to_robot_skipped_canister_list {}".format(e))
        raise InternalError


@log_args_and_response
def get_trolley_for_guided_transfer_from_trolley_csr(device_id, mini_batch,
                                                     mini_batch_trolley,
                                                     guided_canister_status,
                                                     canister_list_csr):
    """
    Function to get trolley for guided transfer to csr flow
    @param device_id: int
    @param mini_batch: int
    @param mini_batch_trolley: int
    @param guided_canister_status: list
    @param canister_list_csr: list
    @return: int
    """
    try:
        # pending_canisters = list()

        if len(canister_list_csr):
            canister_list = canister_list_csr
        else:
            canister_list = list()
            LocationMasterAlias = LocationMaster.alias()
            LocationMasterAlias1 = LocationMaster.alias()

            canister_list_query = GuidedTracker.select(GuidedTracker.destination_location_id,
                                                       LocationMasterAlias.device_id,
                                                       fn.IF(
                                                           GuidedTracker.transfer_status
                                                               .in_(constants.guided_tracker_to_robot_skipped_codes),
                                                           fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                                 GuidedTracker.alternate_canister_id,
                                                                 GuidedTracker.source_canister_id),
                                                           GuidedTracker.source_canister_id).alias(
                                                           'transfer_canister')).dicts() \
                .join(LocationMaster, on=LocationMaster.id == GuidedTracker.cart_location_id) \
                .join(LocationMasterAlias, on=GuidedTracker.destination_location_id == LocationMasterAlias.id) \
                .join(CanisterMaster, on=fn.IF(GuidedTracker.transfer_status
                                               .in_([constants.GUIDED_TRACKER_TRANSFER_SKIPPED,
                                                     constants.GUIDED_TRACKER_TO_ROBOT_SKIPPED]),
                                               fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                     GuidedTracker.alternate_canister_id,
                                                     GuidedTracker.source_canister_id),
                                               GuidedTracker.source_canister_id) == CanisterMaster.id) \
                .join(LocationMasterAlias1, on=LocationMasterAlias1.id == CanisterMaster.location_id) \
                .join(DeviceMaster, on=DeviceMaster.id == LocationMasterAlias1.device_id) \
                .where(GuidedTracker.guided_meta_id == mini_batch,
                       GuidedTracker.transfer_status << guided_canister_status,
                       LocationMasterAlias1.device_id != device_id,
                       DeviceMaster.device_type_id << [settings.DEVICE_TYPES['Canister Transfer Cart'],
                                                       settings.DEVICE_TYPES['Canister Cart w/ Elevator']],
                       LocationMaster.device_id == mini_batch_trolley)

            for record in canister_list_query:
                canister_list.append(record['transfer_canister'])

        # Commenting below code to return trolley when last canister is placed at wrong location and
        # user reload the screen or reset data
        # if len(canister_list):
        #     get_pending_transfer = CanisterMaster.select(CanisterMaster.id, LocationMaster.device_id).dicts() \
        #         .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
        #         .where(CanisterMaster.id << canister_list, LocationMaster.device_id == mini_batch_trolley) \
        #         .group_by(LocationMaster.device_id)
        #
        #     for record in get_pending_transfer:
        #         pending_canisters.append(record['device_id'])
        #     logger.info(pending_canisters)

        if len(canister_list):
            return mini_batch_trolley
        else:
            return None

    except DoesNotExist as e:
        logger.error("error in get_trolley_for_guided_transfer_from_trolley_csr {}".format(e))
        raise DoesNotExist
    except InternalError as e:
        logger.error("error in get_trolley_for_guided_transfer_from_trolley_csr {}".format(e))
        raise InternalError


@log_args_and_response
def get_trolley_for_guided_transfer_from_trolley(device_id, mini_batch, mini_batch_trolley,
                                                 guided_canister_status):
    """
    Function to get trolley for guided transfer to robot flow
    @param device_id: int
    @param mini_batch: int
    @param mini_batch_trolley: int
    @param guided_canister_status: int
    @return: int
    """
    try:
        device_id = int(device_id)
        device_canister_dict = dict()
        # pending_canisters = list()

        LocationMasterAlias = LocationMaster.alias()
        LocationMasterAlias1 = LocationMaster.alias()
        canister_list_query = GuidedTracker.select(GuidedTracker.destination_location_id,
                                                   LocationMasterAlias.device_id,
                                                   LocationMasterAlias1.device_id.alias('can_current_device'),
                                                   fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                         GuidedTracker.alternate_canister_id,
                                                         GuidedTracker.source_canister_id).alias(
                                                       'transfer_canister')).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(LocationMasterAlias, on=GuidedTracker.destination_location_id == LocationMasterAlias.id) \
            .join(CanisterMaster, on=fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                           GuidedTracker.alternate_canister_id,
                                           GuidedTracker.source_canister_id) == CanisterMaster.id) \
            .join(LocationMasterAlias1, JOIN_LEFT_OUTER, on=LocationMasterAlias1.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .where(GuidedTracker.guided_meta_id == mini_batch,
                   GuidedTracker.transfer_status << guided_canister_status,
                   LocationMaster.device_id == mini_batch_trolley,
                   LocationMasterAlias.device_id == device_id,
                   fn.IF((fn.CONCAT(fn.IFNULL(LocationMasterAlias.device_id, '0'),
                                    "_", fn.IFNULL(LocationMasterAlias.quadrant, '0'))
                          != fn.CONCAT(fn.IFNULL(LocationMasterAlias1.device_id, '0'),
                                       "_", fn.IFNULL(LocationMasterAlias1.quadrant, '0'))), True,
                         (fn.IF(CanisterMaster.canister_type == settings.SIZE_OR_TYPE["BIG"],
                                ContainerMaster.drawer_type == settings.SIZE_OR_TYPE["SMALL"], False)))

                   )

        for record in canister_list_query:
            logger.info("get_trolley_for_guided_transfer_from_trolley record {}".format(record))
            if record['device_id'] not in device_canister_dict:
                device_canister_dict[record['device_id']] = list()
            device_canister_dict[record['device_id']].append(record['transfer_canister'])

        # Commenting below code to return trolley in that case also when alternate canister placed in robot
        # but their source canisters are yet to be removed from robot
        # if device_id in device_canister_dict.keys() and len(device_canister_dict[device_id]):
        #     canister_list = device_canister_dict[device_id]
        #     get_pending_transfer = CanisterMaster.select(CanisterMaster.id, LocationMaster.device_id).dicts() \
        #         .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
        #         .where(CanisterMaster.id << canister_list, LocationMaster.device_id == mini_batch_trolley) \
        #         .group_by(LocationMaster.device_id)
        #
        #     for record in get_pending_transfer:
        #         pending_canisters.append(record['device_id'])
        #     logger.info(pending_canisters)

        if device_canister_dict:
            return mini_batch_trolley
        else:
            return None

    except DoesNotExist as e:
        logger.error("error in get_trolley_for_guided_transfer_from_trolley {}".format(e))
        raise DoesNotExist
    except InternalError as e:
        logger.error("error in get_trolley_for_guided_transfer_from_trolley {}".format(e))
        raise InternalError


@log_args_and_response
def get_drawer_for_guided_transfer_to_trolley(device_id, guided_tx_cycle_id, trolley_id):
    """
    Function to get trolley drawer list for which transfers are to be done from robot
    @param device_id: int
    @param guided_tx_cycle_id: int
    @param trolley_id: int
    @return: list
    """
    try:
        drawer_list = list()
        status_list = constants.guided_tracker_to_trolley_status_list
        status_list.append(constants.GUIDED_TRACKER_TO_TROLLEY_DONE)
        LocationMasterAlias = LocationMaster.alias()

        canister_list_query = GuidedTracker.select(GuidedTracker.cart_location_id,
                                                   ContainerMaster.drawer_name,
                                                   ContainerMaster.serial_number,
                                                   LocationMaster.container_id,
                                                   ContainerMaster.ip_address,
                                                   ContainerMaster.mac_address,
                                                   ContainerMaster.serial_number,
                                                   fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                         GuidedTracker.alternate_canister_id,
                                                         GuidedTracker.source_canister_id).alias(
                                                       'transfer_canister')).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(CanisterMaster,
                  on=fn.IF(GuidedTracker.alternate_canister_id.is_null(False), GuidedTracker.alternate_canister_id,
                           GuidedTracker.source_canister_id) == CanisterMaster.id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == CanisterMaster.location_id) \
            .where(GuidedTracker.guided_meta_id == guided_tx_cycle_id,
                   GuidedTracker.transfer_status << status_list,
                   LocationMaster.device_id == trolley_id,
                   ((LocationMasterAlias.device_id == device_id) | (LocationMasterAlias.id.is_null(True)) | (
                               GuidedTracker.transfer_status == constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE))
                   ).group_by(ContainerMaster.id)

        for record in canister_list_query:
            if not drawer_list:
                record["drawer_to_highlight"] = True
            else:
                record["drawer_to_highlight"] = False
            drawer_list.append(record)

        logger.info(drawer_list)
        return drawer_list

    except DoesNotExist as e:
        logger.error("error in get_drawer_for_guided_transfer_to_trolley {}".format(e))
        return None
    except InternalError as e:
        logger.error("error in get_drawer_for_guided_transfer_to_trolley {}".format(e))
        raise InternalError


@log_args_and_response
def get_drawer_for_guided_transfer_from_trolley_csr(device_id, mini_batch, trolley_id,
                                                    guided_canister_status):
    """
    Function to get drawer list for guided transfer to CSR
    @param device_id: int
    @param mini_batch: int
    @param trolley_id: int
    @param guided_canister_status: list
    @return: list
    """
    try:
        drawer_list = list()
        LocationMasterAlias = LocationMaster.alias()
        LocationMasterAlias1 = LocationMaster.alias()

        canister_list_query = GuidedTracker.select(GuidedTracker.cart_location_id,
                                                   LocationMaster.device_id.alias("trolley_id"),
                                                   ContainerMaster.drawer_name,
                                                   ContainerMaster.serial_number,
                                                   ContainerMaster.id.alias("container_id"),
                                                   fn.IF(
                                                       GuidedTracker.transfer_status.in_(
                                                           constants.guided_tracker_to_robot_skipped_codes),
                                                       fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                             GuidedTracker.alternate_canister_id,
                                                             GuidedTracker.source_canister_id),
                                                       GuidedTracker.source_canister_id).alias('transfer_canister')) \
            .dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(CanisterMaster, on=fn.IF(GuidedTracker.transfer_status
                                           .in_(constants.guided_tracker_to_robot_skipped_codes),
                                           fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                 GuidedTracker.alternate_canister_id,
                                                 GuidedTracker.source_canister_id),
                                           GuidedTracker.source_canister_id) == CanisterMaster.id) \
            .join(LocationMasterAlias, on=GuidedTracker.destination_location_id == LocationMasterAlias.id) \
            .join(LocationMasterAlias1, JOIN_LEFT_OUTER, on=LocationMasterAlias1.id == CanisterMaster.location_id) \
            .where(GuidedTracker.guided_meta_id == mini_batch,
                   GuidedTracker.transfer_status << guided_canister_status,
                   LocationMaster.device_id == trolley_id,
                   LocationMasterAlias.device_id == device_id,
                   LocationMasterAlias1.device_id != device_id
                   ).group_by(ContainerMaster.id)

        for record in canister_list_query:
            if not drawer_list:
                record["drawer_to_highlight"] = True
            else:
                record["drawer_to_highlight"] = False
            drawer_list.append(record)

        logger.info(drawer_list)
        return drawer_list

    except DoesNotExist as e:
        logger.error("error in get_drawer_for_guided_transfer_from_trolley_csr {}".format(e))
        return None
    except InternalError as e:
        logger.error("error in get_drawer_for_guided_transfer_from_trolley_csr {}".format(e))
        raise InternalError


@log_args_and_response
def get_drawer_for_guided_transfer_from_trolley(device_id, mini_batch, trolley_id, guided_canister_status):
    """
    Function to get drawer list for guided transfer to Robot
    @param device_id: int
    @param mini_batch: int
    @param trolley_id: int
    @param guided_canister_status: list
    @return: list
    """
    try:
        # fetch drawer data for canisters to be placed in robot
        drawer_list = list()
        LocationMasterAlias = LocationMaster.alias()
        LocationMasterAlias1 = LocationMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()
        canister_list_query = GuidedTracker.select(GuidedTracker.cart_location_id,
                                                   ContainerMaster.drawer_name,
                                                   ContainerMaster.serial_number,
                                                   LocationMaster.container_id,
                                                   fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                         GuidedTracker.alternate_canister_id,
                                                         GuidedTracker.source_canister_id).alias(
                                                       'transfer_canister')).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(CanisterMaster,
                  on=fn.IF(GuidedTracker.alternate_canister_id.is_null(False), GuidedTracker.alternate_canister_id,
                           GuidedTracker.source_canister_id) == CanisterMaster.id) \
            .join(LocationMasterAlias1, on=GuidedTracker.destination_location_id == LocationMasterAlias1.id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == CanisterMaster.location_id) \
            .join(ContainerMasterAlias, JOIN_LEFT_OUTER, on=ContainerMasterAlias.id == LocationMasterAlias.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMasterAlias.device_id) \
            .where(GuidedTracker.guided_meta_id == mini_batch,
                   GuidedTracker.transfer_status << guided_canister_status,
                   LocationMaster.device_id == trolley_id,
                   LocationMasterAlias1.device_id == device_id,
                   fn.IF((fn.CONCAT(fn.IFNULL(LocationMasterAlias.device_id, '0'),
                                    "_", fn.IFNULL(LocationMasterAlias.quadrant, '0'))
                          != fn.CONCAT(fn.IFNULL(LocationMasterAlias1.device_id, '0'),
                                       "_", fn.IFNULL(LocationMasterAlias1.quadrant, '0'))), True,
                         (fn.IF(CanisterMaster.canister_type == settings.SIZE_OR_TYPE["BIG"],
                                ContainerMasterAlias.drawer_type == settings.SIZE_OR_TYPE["SMALL"], False)))
                   ).group_by(ContainerMaster.id)
        logger.info("get_drawer_for_guided_transfer_from_trolley: drawer_list_query: " + str(canister_list_query))
        for record in canister_list_query:
            if not drawer_list:
                record["drawer_to_highlight"] = True
            else:
                record["drawer_to_highlight"] = False
            drawer_list.append(record)
        logger.info("Drawer list for canisters to be placed in robot - " + str(drawer_list))

        if not drawer_list:
            # if drawer_list is empty then check if there are any canisters that are yet to be removed from robot
            logger.info("fetching drawer data for canisters to be removed from robot")

            to_be_removed_canister_query = \
                GuidedTracker.select(GuidedTracker.source_canister_id).dicts() \
                    .join(CanisterMaster, on=CanisterMaster.id == GuidedTracker.source_canister_id) \
                    .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
                    .join(LocationMasterAlias, JOIN_LEFT_OUTER,
                          on=LocationMasterAlias.id == GuidedTracker.cart_location_id) \
                    .where(GuidedTracker.transfer_status << guided_canister_status,
                           LocationMaster.device_id == device_id, GuidedTracker.alternate_canister_id.is_null(False),
                           GuidedTracker.guided_meta_id == mini_batch, LocationMasterAlias.device_id == trolley_id)
            to_be_removed_canister_count = to_be_removed_canister_query.count()

            logger.info("canisters_to_be_removed_canister_count: " + str(to_be_removed_canister_count))
            if to_be_removed_canister_count:
                logger.info("There are canisters that are to be removed from robot so fetching drawer list")
                # There are canisters that are yet to be removed so now recommend cart drawer
                drawer_list = recommend_cart_drawers_to_place_replaced_canisters(trolley_id=trolley_id,
                                                                                 guided_cycle_id=mini_batch)

        return drawer_list

    except DoesNotExist as e:
        logger.error("error in get_drawer_for_guided_transfer_from_trolley {}".format(e))
        return None
    except InternalError as e:
        logger.error("error in get_drawer_for_guided_transfer_from_trolley {}".format(e))
        raise InternalError


@log_args_and_response
def get_canister_to_be_replenished_next_dao(system_id: int, device_ids: list) -> tuple:
    """
    Method to fetch canisters to be replenished for the next batch
    @param device_ids:
    @param batch_id:
    @param system_id:
    @return:
    """
    replenish_list = list()
    pending_packs_for_timer = list()
    try:
        logger.info("get_canister_to_be_replenished_next_dao: fetching ordered packs")
        current_mini_batch_id = None
        mini_batch_packs = []
        ordered_packs = get_ordered_packs_of_batch(system_id=system_id,
                                                   device_ids=device_ids)
        logger.info("get_canister_to_be_replenished_next_dao: fetched ordered_packs - " + str(len(ordered_packs)))

        if not ordered_packs:
            logger.info("get_canister_to_be_replenished_next_dao: No pending packs available")
            return False, "14003", current_mini_batch_id, mini_batch_packs, replenish_list, pending_packs_for_timer

        pending_mini_batch_pack_dicts = dict()

        pack_ids = [record['id'] for record in ordered_packs]
        pack_status_list = [record['pack_status'] for record in ordered_packs]
        # mini_batch_packs = []

        mini_batch_id = 0
        for i in range(0, len(pack_ids), settings.GUIDED_MINI_BATCH_PACK_COUNT):
            mini_batch_id += 1
            current_mini_batch_packs = pack_ids[i: i + settings.GUIDED_MINI_BATCH_PACK_COUNT]
            pack_status = set(pack_status_list[i: i + settings.GUIDED_MINI_BATCH_PACK_COUNT])
            if pack_status.intersection((settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS)):
                pending_mini_batch_pack_dicts[mini_batch_id] = current_mini_batch_packs
        total_pending_mini_batches = len(pending_mini_batch_pack_dicts)
        logger.info(
            "get_canister_to_be_replenished_next_dao: total_pending_mini_batches- " + str(total_pending_mini_batches))
        if not total_pending_mini_batches:
            logger.info("get_canister_to_be_replenished_next_dao: no pending mini batch")
            return False, "14001", current_mini_batch_id, mini_batch_packs, replenish_list, pending_packs_for_timer

        # fetch list of canisters skipped today in same batch, we won't consider these canisters for replenish
        logger.info("fetching canister list to be excluded for replenish")
        exclude_canister_list = get_last_skipped_canisters_by_batch_and_current_date()
        logger.info("fetched exclude_canister_list - " + str(exclude_canister_list))
        for m_batch_id, pack_ids in pending_mini_batch_pack_dicts.items():
            logger.info("fetching replenish for mini batch - " + str(m_batch_id))
            replenish_query = db_get_replenish_query(system_id=system_id,
                                                     device_ids=device_ids,
                                                     mini_batch_wise=True,
                                                     exclude_canisters=exclude_canister_list,
                                                     ordered_packs=True)
            for record in replenish_query:
                unit_drug_volume = record["approx_volume"]
                if unit_drug_volume is not None:
                    logger.info("unit_drug_volume is not None so fetching canister_usable_volume")
                    # find canister volume
                    canister_usable_volume = get_canister_volume(canister_type=record["canister_type"])
                    logger.info(
                        "canister_usable_volume: {} for canister {}".format(canister_usable_volume,
                                                                            record["canister_id"]))

                    record["canister_capacity"] = get_max_possible_drug_quantities_in_canister(
                        canister_volume=canister_usable_volume,
                        unit_drug_volume=unit_drug_volume)
                    logger.info("canister_capacity in canister {} : {}".format(record["canister_id"],
                                                                                record["canister_capacity"]))
                    if record["canister_capacity"] and int(record["available_quantity"]) >= int(
                            record["canister_capacity"]):
                        logger.info(
                            "get_canister_to_be_replenished_next_dao available qty is max capacity {}".format(record))
                        continue
                else:
                    record["canister_capacity"] = None

                replenish_list.append(record)
            logger.info("get_canister_to_be_replenished_next_dao replenish list {}".format(replenish_list))

            if replenish_list:
                # break the loop with that mini batch if we get replenish for that batch
                current_mini_batch_id = m_batch_id
                mini_batch_packs = pack_ids
                logger.info("get_canister_to_be_replenished_next_dao: found replenish for mini batch - " + str(
                    current_mini_batch_id))
                break
            else:
                pending_packs_for_timer.extend(pack_ids)
        if not current_mini_batch_id:
            logger.info("get_canister_to_be_replenished_next_dao: no more replenish")
            return False, "14001", 0, mini_batch_packs, replenish_list, pending_packs_for_timer

        return True, "success", current_mini_batch_id, mini_batch_packs, replenish_list, pending_packs_for_timer
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_canister_to_be_replenished_next_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_to_be_replenished_next_dao {}".format(e))
        raise e


@log_args_and_response
def get_system_id_from_guided_tx_cycle_id(guided_tx_cycle_id):
    try:
        logger.info("In get_system_id_from_guided_tx_cycle_id")
        pack_ids = []
        system_id = None
        query = GuidedMeta.select(GuidedMeta.pack_ids).dicts() \
                .where(GuidedMeta.id == guided_tx_cycle_id)

        for data in query:
            pack_ids = list(map(int, (data["pack_ids"]).split(",")))

        if pack_ids:
            logger.info(f"In get_system_id_from_guided_tx_cycle_id, pack_ids are available for guided_tx_cycle_id: {guided_tx_cycle_id}")
            query = PackDetails.select(PackDetails.system_id).dicts()\
                    .where(PackDetails.id.in_(pack_ids))\
                    .group_by(PackDetails.system_id)
            for data in query:
                system_id =  data["system_id"]
                return system_id

        return system_id

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_system_id_from_guided_tx_cycle_id {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_system_id_from_guided_tx_cycle_id {}".format(e))
        raise e

@log_args_and_response
def guided_cycle_status_for_update(update_status: int, guided_tx_cycle_id: int) -> tuple:
    """
    This function checks to update meta table status.
    @param update_status: int
    @param guided_tx_cycle_id: int
    @param batch_id: int
    @return bool
    """
    try:
        current_status = None
        current_mini_batch = None
        current_batch_id = None
        # query to obtain current status for the guided_tx_cycle_id and batch_id
        current_status_query = GuidedMeta.select(GuidedMeta.status, GuidedMeta.mini_batch_id,
                                                 GuidedMeta.batch_id).dicts() \
            .where((GuidedMeta.id == guided_tx_cycle_id))
        logger.info("current_status_query :{}".format(current_status_query))

        # to validate status for given guided_tx_cycle_id and obtain current_status
        if current_status_query.count() == 1:
            for record in current_status_query:
                current_status = record["status"]
                current_mini_batch = record["mini_batch_id"]
                current_batch_id = record["batch_id"]
        else:
            return False, current_mini_batch

        logger.info("update_status: {}".format(update_status))
        logger.info("current_status: {}".format(current_status))

        # to validate update_status must be greater than the current status
        if int(update_status) > int(current_status):
            update_meta_status = GuidedMeta.update(status=update_status, modified_date=get_current_date_time()).where(
                (GuidedMeta.id == guided_tx_cycle_id),
                (GuidedMeta.mini_batch_id == current_mini_batch)).execute()
            logger.info("update_meta_status: {}".format(update_meta_status))
            # validate if status updated
            if update_meta_status == 1:
                return True, current_mini_batch
            else:
                return False, current_mini_batch
        # if status is same, return only the current_mini_batch
        if int(update_status) == int(current_status):
            return True, current_mini_batch
        else:
            return False, current_mini_batch
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in guided_cycle_status_for_update {}".format(e))
        raise


@log_args_and_response
def trolley_data_for_guided_tx(canister_id: int, guided_tx_cycle_id: int, guided_tx_canister_status: int) -> tuple:
    """
    This function returns Trolley Data for Canister on UpdateCanisterQuantity api call
    @param guided_tx_cycle_id:
    @param guided_tx_canister_status:
    @param canister_id: int
    """
    try:
        logger.info("In trolley_data_for_guided_tx, guided_tx_canister_status {}".format(guided_tx_canister_status))
        # validate canister with given guided_tx_cycle_id

        validate_canister_id = GuidedTracker.select(fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                          GuidedTracker.alternate_canister_id,
                                                          GuidedTracker.source_canister_id).alias('canister_id'),
                                                    GuidedTracker.cart_location_id.alias('cart_location'),
                                                    GuidedTracker.id.alias('guided_tracker_id')).dicts() \
            .where((GuidedTracker.guided_meta_id == guided_tx_cycle_id),
                   (GuidedTracker.transfer_status.not_in([constants.GUIDED_TRACKER_TO_TROLLEY_SKIPPED,
                                                          constants.GUIDED_TRACKER_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                          constants.GUIDED_TRACKER_TO_TROLLEY_TRANSFER_LATER_SKIP,
                                                          constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE_TRANSFER_LATER])),
                   ((GuidedTracker.source_canister_id == canister_id) | (
                           GuidedTracker.alternate_canister_id == canister_id)))

        logger.info("In trolley_data_for_guided_tx, validate_canister_id query: {}".format(validate_canister_id))

        cart_location_id = None
        cart_container_id = None
        cart_device_id = None
        # obtain the location as well as update the status to replenish
        for record in validate_canister_id:

            logger.info(f"In trolley_data_for_guided_tx, record: {record}")

            if record['canister_id'] == canister_id:
                cart_location_id = record['cart_location']

                logger.info("In trolley_data_for_guided_tx, update canister transfer_status in GuidedTracker")

                update_canister_status_query = GuidedTracker.update(
                    transfer_status=guided_tx_canister_status,
                    modified_date=get_current_date_time()) \
                    .where(GuidedTracker.id == record['guided_tracker_id']).execute()

                logger.info("In trolley_data_for_guided_tx, update_canister_status_query: {}".format(
                    update_canister_status_query))

        # to update replenished_skipped_count in GuidedMeta
        if guided_tx_canister_status == constants.GUIDED_TRACKER_SKIPPED:
            current_count_query = GuidedMeta.select(GuidedMeta.replenish_skipped_count).dicts().where(
                GuidedMeta.id == guided_tx_cycle_id).get()
            updated_count = int(current_count_query["replenish_skipped_count"]) + 1

            logger.info("In trolley_data_for_guided_tx, replenish_skipped_count :{}".format(updated_count))

            update_meta_skipped_count = GuidedMeta.update(replenish_skipped_count=updated_count,
                                                          modified_date=get_current_date_time()).where(
                GuidedMeta.id == guided_tx_cycle_id).execute()

            logger.info(f"In trolley_data_for_guided_tx, update_meta_skipped_count: {update_meta_skipped_count}")

        # obtain device and container data based on location_id
        if cart_location_id:
            cart_container_id_query = LocationMaster.select(LocationMaster.device_id,
                                                            LocationMaster.container_id).dicts() \
                .where(LocationMaster.id == cart_location_id)

            logger.info(f"In trolley_data_for_guided_tx, cart_container_id_query: {cart_container_id_query}")

            for record in cart_container_id_query:
                cart_container_id = record['container_id']
                cart_device_id = record['device_id']

            trolley_data_query = ContainerMaster.select(DeviceTypeMaster.device_type_name,
                                                        DeviceMaster.id.alias('device_id'),
                                                        DeviceMaster.name.alias('device_name'),
                                                        ContainerMaster.drawer_name,
                                                        fn.IF(ContainerMaster.id == cart_container_id, True,
                                                              False).alias('to_be_highlight')) \
                .dicts() \
                .join(DeviceMaster, on=ContainerMaster.device_id == DeviceMaster.id) \
                .join(DeviceTypeMaster, on=DeviceMaster.device_type_id == DeviceTypeMaster.id) \
                .where(DeviceMaster.id == cart_device_id).order_by(ContainerMaster.serial_number)

            logger.info(f"In trolley_data_for_guided_tx, trolley_data_query: {trolley_data_query}")

            device_data = {}
            container_data = []
            # trolley data
            for record in trolley_data_query:
                container_data_dict = {}
                if record['device_id'] not in device_data.keys():
                    device_data['device_id'] = record['device_id']
                    device_data['device_name'] = record['device_name']
                    device_data['device_type_name'] = record['device_type_name']
                container_data_dict['drawer_name'] = record['drawer_name']
                container_data_dict['to_be_highlight'] = record['to_be_highlight']
                container_data.append(container_data_dict)
            response: dict = dict()
            response['device_data'] = device_data
            response['container_data'] = container_data
            return True, response
        else:
            return False, "Invalid canister_id"
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in trolley_data_for_guided_tx {}".format(e))
        raise


def add_record_in_guided_meta(guided_meta_dict: dict) -> int:
    """
    Method to add record in guided meta and return id
    @param guided_meta_dict:
    @return:
    """
    try:
        record = GuidedMeta.create(**guided_meta_dict)
        return record.id
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in add_record_in_guided_meta {}".format(e))
        raise


@log_args_and_response
def add_records_in_guided_tracker(guided_tracker_list: list) -> int:
    try:
        status = GuidedTracker.insert_many(guided_tracker_list).execute()
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in add_records_in_guided_tracker {}".format(e))
        raise


@log_args_and_response
def get_incomplete_guided_meta(batch_id: int) -> dict:
    """
    Method to fetch incomplete cycle id if available
    @param batch_id:
    @return:
    """
    try:
        query = GuidedMeta.select().dicts().where(GuidedMeta.batch_id == batch_id,
                                                  GuidedMeta.status != constants.GUIDED_META_TO_CSR_DONE) \
            .order_by(GuidedMeta.id).get()
        logger.info("in get_incomplete_guided_meta - found data: " + str(query))
        return query
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_incomplete_guided_meta {}".format(e))
        raise
    except DoesNotExist:
        logger.error("No incomplete mini get_incomplete_guided_meta available in guided meta")
        raise


@log_args_and_response
def replace_canister_in_pack_analysis_details(system_id: int, original_canister: int, new_canister: int) -> int:
    """
    Method to replaced original_canister ids with new canister id in pack analysis details
    @param system_id:
    @param original_canister:
    @param new_canister:
    @return:
    """
    try:
        location_number = None
        pack_analysis_ids = list()
        batch_id = BatchMaster.db_get_latest_progress_batch_id(system_id=system_id)
        location_info = get_location_details_by_canister_id(canister_id=new_canister)
        if location_info and 'location_number' in location_info:
            location_number = location_info['location_number']

        filling_pending_pack_ids = db_get_progress_filling_left_pack_ids()

        # clauses = [(PackAnalysis.batch_id == batch_id),
        #            (PackAnalysisDetails.canister_id == original_canister),
        #            (PackAnalysisDetails.location_number.is_null(False)),
        #            (PackAnalysisDetails.quadrant.is_null(False))]

        clauses = [(PackAnalysis.batch_id == batch_id),
                   (PackAnalysisDetails.canister_id == original_canister),
                   (PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)]

        if len(filling_pending_pack_ids):
            clauses.append(((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                            | (PackDetails.id << filling_pending_pack_ids)))

        else:
            clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]))

        pack_analysis = PackAnalysisDetails.select(PackAnalysisDetails.id).dicts() \
            .join(PackAnalysis, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .where(*clauses)

        for record in pack_analysis:
            pack_analysis_ids.append(record['id'])

        if pack_analysis_ids:
            status = PackAnalysisDetails.update(canister_id=new_canister, location_number=location_number) \
                .where(PackAnalysisDetails.id << pack_analysis_ids).execute()
            return status
        else:
            return 0
    except (InternalError, IntegrityError) as e:
        logger.error("error in replace_canister_in_pack_analysis_details {}".format(e))
        raise e
    except DoesNotExist as e:
        logger.error("error in replace_canister_in_pack_analysis_details {}".format(e))
        return 0


@log_args_and_response
def get_last_skipped_canisters_by_batch_and_current_date() -> list:
    """
    Method to fetch list of last skipped canisters in a batch
    @param batch_id:
    @return:
    """
    try:
        canister_list = list()
        canister_query = GuidedTracker.select(fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                    GuidedTracker.alternate_canister_id,
                                                    GuidedTracker.source_canister_id).alias("canister_id")).dicts() \
            .join(GuidedMeta, on=GuidedTracker.guided_meta_id == GuidedMeta.id) \
            .where(GuidedTracker.transfer_status <<
                   constants.guided_tracker_skipped_canister_code_list,
                   fn.DATE(GuidedTracker.modified_date) == fn.DATE(get_current_date_time()))
        # removed check of batch id and no need of other check as already check is available on date.
        for record in canister_query:
            canister_list.append(record["canister_id"])
        logger.info(
            "In get_last_skipped_canisters_by_batch_and_current_date: exclude_canister_list: " + str(canister_list))
        return canister_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_last_skipped_canisters_by_batch_and_current_date {}".format(e))
        raise e


def get_guided_reserved_location(batch_id: int, device_id: int) -> list:
    """
    This functions returns the set of locations which are already recommended for guided location.
    """
    try:
        guided_reserved_locations = []
        guided_reserved_location_query = GuidedTracker.select(
            GuidedTracker.destination_location_id.alias('location_id')).dicts() \
            .join(GuidedMeta, on=GuidedTracker.guided_meta_id == GuidedMeta.id) \
            .join(LocationMaster, on=GuidedTracker.destination_location_id == LocationMaster.id) \
            .where((GuidedMeta.batch_id == batch_id),
                   (LocationMaster.device_id == device_id),
                   (GuidedMeta.status.not_in([constants.GUIDED_META_TO_ROBOT_DONE,
                                              constants.GUIDED_META_TO_CSR_DONE])))

        for record in guided_reserved_location_query:
            guided_reserved_locations.append(record["location_id"])

        return guided_reserved_locations

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_guided_reserved_location {}".format(e))
        raise e


def delete_from_guided_tracker(batch_id: int) -> bool:
    """
    Deletes data from the GuidedTracker table when status of batch is marked as BATCH_PROCESSING_COMPLETE or BATCH_DELETED
    """
    try:
        cycle_id_list = []
        cycle_status_set = set()
        for record in GuidedMeta.select(GuidedMeta.id, GuidedMeta.status).dicts() \
                .where(GuidedMeta.batch_id == batch_id):
            cycle_id_list.append(record["id"])
            cycle_status_set.add(record["status"])

        if cycle_id_list and not cycle_status_set.difference({constants.GUIDED_META_TO_CSR_DONE}):
            status = GuidedTracker.delete().where(GuidedTracker.guided_meta_id << cycle_id_list).execute()
            logger.info("In delete_from_guided_tracker: record deleted from guided tracker: {} ".format(status))
            return True
        return False

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_from_guided_tracker {}".format(e))
        raise e


@log_args_and_response
def fetch_guided_tracker_ids_based_on_destination_device(dest_device_id: int, guided_tx_cycle_id: int,
                                                         transfer_status_list: list = None) -> tuple:
    """
    Function to fetch guided tracker ids
    @param transfer_status_list:
    @param guided_tx_cycle_id:
    @param dest_device_id:
    @return: status
    """
    try:
        all_guided_tracker_ids = list()
        alt_guided_tracker_ids = list()
        source_guided_tracker_ids = list()
        LocationMasterAlias = LocationMaster.alias()
        query = GuidedTracker.select(GuidedTracker.id,
                                     GuidedTracker.alternate_canister_id,
                                     GuidedMeta.cart_id,
                                     LocationMasterAlias.device_id).dicts() \
            .join(LocationMaster, on=LocationMaster.id == GuidedTracker.destination_location_id) \
            .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == GuidedTracker.alternate_canister_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER,
                  on=LocationMasterAlias.id == GuidedTracker.destination_location_id) \
            .where(LocationMaster.device_id == dest_device_id,
                   GuidedTracker.guided_meta_id == guided_tx_cycle_id)
        if transfer_status_list:
            query = query.where(GuidedTracker.transfer_status << transfer_status_list)
        for record in query:
            all_guided_tracker_ids.append(record["id"])

            if record["alternate_canister_id"] and record["device_id"] and record["cart_id"] == record["device_id"]:
                # consider alternate canisters which are already transferred to cart to tx them to csr
                alt_guided_tracker_ids.append(record["id"])
            else:
                source_guided_tracker_ids.append(record["id"])
        return all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids
    except InternalError as e:
        logger.error("error in fetch_guided_tracker_ids_based_on_destination_device {}".format(e))
        raise InternalError


@log_args_and_response
def fetch_guided_tracker_ids_by_destination_device_and_batch(dest_device_id: int, batch_id: int,
                                                             transfer_status_list: list = None) -> tuple:
    """
    Function to fetch guided tracker ids
    @param transfer_status_list:
    @param batch_id:
    @param dest_device_id:
    @return: status
    """
    try:
        all_guided_tracker_ids = list()
        alt_guided_tracker_ids = list()
        source_guided_tracker_ids = list()
        query = GuidedTracker.select(GuidedTracker.id,
                                     GuidedTracker.alternate_canister_id).dicts() \
            .join(LocationMaster, on=LocationMaster.id == GuidedTracker.destination_location_id) \
            .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
            .where(LocationMaster.device_id == dest_device_id,
                   GuidedMeta.id == batch_id)
        if transfer_status_list:
            query = query.where(GuidedTracker.transfer_status << transfer_status_list)
        for record in query:
            all_guided_tracker_ids.append(record["id"])

            if record["alternate_canister_id"]:
                alt_guided_tracker_ids.append(record["id"])
            else:
                source_guided_tracker_ids.append(record["id"])
        return all_guided_tracker_ids, alt_guided_tracker_ids, source_guided_tracker_ids
    except InternalError as e:
        logger.error("error in fetch_guided_tracker_ids_by_destination_device_and_batch {}".format(e))
        raise InternalError


@log_args_and_response
def fetch_guided_meta_data_based_on_cycle_id(guided_cycle_id: int) -> dict:
    """
    Method to fetch mini batch id based on guided cycle id
    @param guided_cycle_id:
    @return:
    """
    try:
        return GuidedMeta.select().dicts().where(GuidedMeta.id == guided_cycle_id).get()
    except DoesNotExist:
        return {}
    except InternalError as e:
        logger.error("error in fetch_guided_meta_data_based_on_cycle_id {}".format(e))
        raise InternalError


@log_args_and_response
def update_guided_meta_status_by_batch(status: int) -> int:
    """
    Method to fetch mini batch id based on guided cycle id
    @param batch_id:
    @param status:
    @return:
    """
    try:
        if status == constants.GUIDED_META_TO_CSR_DONE:
            return GuidedMeta.update(status=status).where(GuidedMeta.status != constants.GUIDED_META_TO_CSR_DONE).execute()
    except InternalError as e:
        logger.error("error in update_guided_meta_status_by_batch {}".format(e))
        raise InternalError


@log_args_and_response
def recommend_cart_drawers_to_place_replaced_canisters(trolley_id: int, guided_cycle_id: int) -> list:
    """
    Method to recommend cart drawers to remove and place canisters which are replaced by alternate canisters
    @param trolley_id:
    @param guided_cycle_id:
    @return:
    """
    try:
        LocationMasterAlias = LocationMaster.alias()
        CanisterMasterAlias = CanisterMaster.alias()
        drawer_list = list()
        empty_locations_query = GuidedTracker.select(ContainerMaster.id.alias('container_id'),
                                                     ContainerMaster.drawer_name,
                                                     ContainerMaster.serial_number,
                                                     fn.COUNT(LocationMasterAlias.id).alias("empty_location_count"),
                                                     fn.GROUP_CONCAT(LocationMasterAlias.id).coerce(False).alias(
                                                         "empty_locations")).dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == GuidedTracker.source_canister_id) \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.container_id == ContainerMaster.id) \
            .join(CanisterMasterAlias, JOIN_LEFT_OUTER,
                  on=CanisterMasterAlias.location_id == LocationMasterAlias.id) \
            .where(GuidedTracker.alternate_canister_id.is_null(False), LocationMaster.device_id == trolley_id,
                   GuidedTracker.guided_meta_id == guided_cycle_id, CanisterMasterAlias.id.is_null(True)) \
            .group_by(LocationMasterAlias.container_id) \
            .order_by(SQL("empty_location_count").desc())
        for record in empty_locations_query:
            record["drawer_to_highlight"] = True
            drawer_list.append(record)
            return drawer_list

        if not drawer_list:
            logger.info(
                "No cart drawer available having some empty location so fetching containers having max empty location")
            # No cart drawer available having some empty location where some canisters are already there to tx to csr
            empty_drawer_query = LocationMaster.select(ContainerMaster.id.alias('container_id'),
                                                       ContainerMaster.drawer_name,
                                                       ContainerMaster.serial_number,
                                                       fn.COUNT(LocationMaster.id).alias("empty_location_count"),
                                                       fn.GROUP_CONCAT(LocationMaster.id).coerce(False).alias(
                                                           "empty_locations")).dicts() \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .where(CanisterMaster.id.is_null(True), LocationMaster.device_id == trolley_id) \
                .group_by(LocationMaster.container_id) \
                .order_by(SQL("empty_location_count").desc(), ContainerMaster.id)
            for record in empty_drawer_query:
                logger.info("recommend_cart_drawers_to_place_replaced_canisters: Found empty drawer- " + str(record))
                record["drawer_to_highlight"] = True
                drawer_list.append(record)
                return drawer_list
        return drawer_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in recommend_cart_drawers_to_place_replaced_canisters {}".format(e))
        raise e


@log_args_and_response
def check_pending_guided_canister_transfer(system_id: int) -> list:
    """
    Function to check if guided tx is pending for any batch or not
    @return: list
    """
    try:
        query = GuidedMeta.select().dicts() \
            .where(GuidedMeta.status != constants.GUIDED_META_TO_CSR_DONE) \
            .order_by(GuidedMeta.id)

        return list(query)

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in check_pending_guided_canister_transfer {}".format(e))
        raise e


@log_args_and_response
def fetch_guided_tracker_ids_based_on_meta_id(guided_tx_cycle_id: int, transfer_status_list: list = None) -> list:
    """
    Function to fetch guided tracker ids based on guided tx cycle id and status
    @param transfer_status_list:
    @param guided_tx_cycle_id:
    @return: status
    """
    try:
        guided_tracker_ids = list()
        query = GuidedTracker.select(GuidedTracker.id).dicts().where(GuidedTracker.guided_meta_id == guided_tx_cycle_id)
        if transfer_status_list:
            query = query.where(GuidedTracker.transfer_status << transfer_status_list)
        for record in query:
            guided_tracker_ids.append(record["id"])

        return guided_tracker_ids
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in fetch_guided_tracker_ids_based_on_meta_id {}".format(e))
        raise e


@log_args_and_response
def fetch_guided_tracker_ids_by_canister_ids(canister_ids: list, guided_tx_cycle_id: int,
                                             transfer_status_list: list = None) -> list:
    """
    Function to fetch guided tracker ids based on guided tx cycle id and status
    @param canister_ids:
    @param transfer_status_list:
    @param guided_tx_cycle_id:
    @return: status
    """
    try:
        guided_tracker_ids = list()
        query = GuidedTracker.select(GuidedTracker.id).dicts() \
            .where(GuidedTracker.guided_meta_id == guided_tx_cycle_id,
                   (GuidedTracker.source_canister_id << canister_ids |
                    GuidedTracker.alternate_canister_id << canister_ids))
        if transfer_status_list:
            query = query.where(GuidedTracker.transfer_status << transfer_status_list)
        for record in query:
            guided_tracker_ids.append(record["id"])

        return guided_tracker_ids
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in fetch_guided_tracker_ids_by_canister_ids {}".format(e))
        raise e


@log_args_and_response
def get_guided_tracker_based_on_status(guided_cycle_id: int, transfer_status_list: list) -> list:
    """
    Method to get guided tracker data based on status list and guided cycle id
    @param guided_cycle_id:
    @param transfer_status_list:
    @return:
    """
    try:
        guided_tracker_list = list()
        query = GuidedTracker.select().dicts() \
            .where(GuidedTracker.guided_meta_id == guided_cycle_id,
                   GuidedTracker.transfer_status << transfer_status_list)
        for record in query:
            guided_tracker_list.append(record)
        return guided_tracker_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_guided_tracker_based_on_status {}".format(e))
        raise e


@log_args_and_response
def get_serial_number_and_name_from_device(device_id):
    try:
        device_data = DeviceMaster.select(DeviceMaster, DeviceTypeMaster).dicts() \
            .join(DeviceTypeMaster, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .where(DeviceMaster.id == device_id)
        for record in device_data:
            return record['serial_number'], record['name'], record['device_type_name'], record['device_type_id']
    except DoesNotExist as e:
        logger.error("error in get_serial_number_and_name_from_device {}".format(e))
        return None
    except InternalError as e:
        logger.error("error in get_serial_number_and_name_from_device {}".format(e))
        raise InternalError


@log_args_and_response
def get_pending_transfer_to_trolley_device(mini_batch, trolley_id):
    try:
        canister_list = list()
        pending_devices = list()
        canister_list_query = GuidedTracker.select(
            fn.IF(GuidedTracker.alternate_canister_id.is_null(False), GuidedTracker.alternate_canister_id,
                  GuidedTracker.source_canister_id).alias('transfer_canister')).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .where(GuidedTracker.guided_meta_id == mini_batch,
                   GuidedTracker.transfer_status << [constants.GUIDED_TRACKER_PENDING],
                   LocationMaster.device_id == trolley_id
                   )

        for record in canister_list_query:
            canister_list.append(record['transfer_canister'])
        logger.info(canister_list)

        if canister_list:
            get_pending_transfer = CanisterMaster.select(LocationMaster.device_id.alias("pending_device_id"),
                                                         DeviceMaster.name.alias("pending_device_name"),
                                                         DeviceMaster.device_type_id.alias("pending_device_type_id"),
                                                         DeviceMaster.system_id.alias(
                                                             "pending_device_system_id")).dicts() \
                .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(DeviceMaster, on=LocationMaster.device_id == DeviceMaster.id) \
                .where(CanisterMaster.id << canister_list,
                       DeviceMaster.device_type_id.not_in([settings.DEVICE_TYPES['Canister Transfer Cart'],
                                                           settings.DEVICE_TYPES['Canister Cart w/ Elevator']])) \
                .group_by(LocationMaster.device_id)

            for record in get_pending_transfer:
                pending_devices.append(record)
            logger.info("Pending device_dict: " + str(pending_devices))

        return pending_devices

    except DoesNotExist as e:
        logger.error("error in get_pending_transfer_to_trolley_device {}".format(e))
        return None
    except InternalError as e:
        logger.error("error in get_pending_transfer_to_trolley_device {}".format(e))
        raise InternalError


@log_args_and_response
def get_pending_transfer_from_trolley_to_robot(mini_batch,
                                               trolley_id,
                                               guided_canister_status,
                                               system_id):
    try:
        LocationMasterALias = LocationMaster.alias()
        LocationMasterAlias1 = LocationMaster.alias()
        pending_devices = list()
        # device_list = list()
        # device_types = list()

        pending_devices_query = GuidedTracker.select(DeviceMaster.id.alias('pending_device_id'),
                                                     DeviceMaster.name.alias('pending_device_name'),
                                                     DeviceMaster.device_type_id.alias('pending_device_type_id'),
                                                     DeviceMaster.system_id.alias('pending_device_system_id')
                                                     ).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(LocationMasterALias, on=LocationMasterALias.id == GuidedTracker.destination_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterALias.device_id) \
            .join(CanisterMaster, on=fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                           GuidedTracker.alternate_canister_id,
                                           GuidedTracker.source_canister_id) == CanisterMaster.id) \
            .join(LocationMasterAlias1, on=LocationMasterAlias1.id == CanisterMaster.location_id) \
            .where(GuidedTracker.guided_meta_id == mini_batch,
                   GuidedTracker.transfer_status << guided_canister_status,
                   LocationMasterAlias1.device_id != DeviceMaster.id,
                   LocationMaster.device_id == trolley_id,
                   DeviceMaster.system_id == system_id) \
            .group_by(DeviceMaster.id)

        for record in pending_devices_query:
            pending_devices.append(record)

        # if canister_list:
        #     get_pending_transfer = CanisterMaster.select(LocationMaster.device_id).dicts() \
        #         .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
        #         .where(CanisterMaster.id << canister_list, LocationMaster.device_id == trolley_id) \
        #         .group_by(LocationMaster.device_id)
        #
        #     for record in get_pending_transfer:
        #         device_list.append(record['device_id'])
        #     logger.info(device_list)

        return pending_devices

    except DoesNotExist as e:
        logger.error("error in get_pending_transfer_from_trolley_to_robot {}".format(e))
        return None
    except InternalError as e:
        logger.error("error in get_pending_transfer_from_trolley_to_robot {}".format(e))
        raise InternalError


@log_args_and_response
def get_transfer_cycle_drug_data(guided_tx_cycle_id: int,
                                 company_id: int, sort_fields: list, filter_fields: dict) -> tuple:
    """
    To obtain drug and canister replenish data for transfer flow
    @param guided_tx_cycle_id: int
    @param company_id: int
    @param sort_fields:list
    @param filter_fields: dict
    @return: dict
    """
    try:
        # system_id = system_id
        company_id = company_id
        order_list: list = list()
        count = 0
        results: dict = dict()
        if sort_fields:
            order_list.extend(sort_fields)
        fields_dict = {
            "drug_name": DrugMaster.concated_drug_name_field(include_ndc=True),
            "drawer_initial": cast(
                fn.Substr(ContainerMaster.drawer_name, 1, fn.instr(ContainerMaster.drawer_name, '-') - 1), 'CHAR'),
            "drawer_number": cast(
                fn.Substr(ContainerMaster.drawer_name, fn.instr(ContainerMaster.drawer_name, '-') + 1), 'SIGNED'),
            "canister_location": fn.IF(CanisterMaster.location_id.is_null(True), -1,
                                       LocationMaster.get_device_location()),
            "location_number": LocationMaster.location_number,
            "ndc": DrugMaster.ndc,
            "drug_id": DrugMaster.id
        }
        like_search_list = ['drug_name', 'ndc']

        # to obtain canister data from given guided_tx_cycle_id
        unique_drugs: dict = dict()
        # alt_canister_drug_dict if alternate canister is available for source canister
        alt_can_dic: dict = dict()
        canister_data_query = GuidedTracker.db_get_guided_canister_data(guided_tx_cycle_id=guided_tx_cycle_id)

        logger.info("In get_transfer_cycle_drug_data: canister_data_query:{}".format(canister_data_query))
        for record in canister_data_query:
            if record['alternate_canister_id']:
                if not record['alt_can_replenish_required']:
                    pass
                else:
                    unique_drugs[record['alternate_canister_id']] = record['required_qty']
                    if record['alternate_canister_id'] not in alt_can_dic.keys():
                        alt_can_dic[record['alternate_canister_id']] = dict()
                        alt_can_dic[record['alternate_canister_id']][record['source_canister_id']] = record[
                            'required_qty']
            else:
                unique_drugs[record['source_canister_id']] = record['required_qty']
        logger.info("In get_transfer_cycle_drug_data: unique_drugs: {}".format(unique_drugs))

        # query to obtain drug data based on ndc list of canisters
        if unique_drugs:
            drug_ndc_query = DrugMaster.select(DrugMaster.id.alias('drug_id'),
                                               DrugMaster.concated_drug_name_field().alias('drug_name_for_drug'),
                                               fields_dict["drug_name"].alias(
                                                   'drug_name_for_canister'),
                                               DrugMaster.strength,
                                               DrugMaster.strength_value,
                                               fields_dict["ndc"],
                                               DrugMaster.formatted_ndc,
                                               DrugMaster.txr,
                                               DrugMaster.imprint,
                                               UniqueDrug.is_powder_pill,
                                               DrugMaster.image_name,
                                               DrugMaster.color,
                                               DrugMaster.shape,
                                               DrugDetails.last_seen_by,
                                               DrugDetails.last_seen_date,
                                               fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                                     DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                               fn.IF(DrugStockHistory.created_by.is_null(True), None,
                                                     DrugStockHistory.created_by).alias('stock_updated_by'),
                                               DrugStockHistory.created_date.alias('stock_updated_on'),
                                               CanisterMaster.id.alias('canister_id'),
                                               fn.IF(
                                                   CanisterMaster.expiry_date <= date.today() + timedelta(
                                                       settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                                   constants.EXPIRED_CANISTER,
                                                   fn.IF(
                                                       CanisterMaster.expiry_date <= date.today() + timedelta(
                                                           settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                                       constants.EXPIRES_SOON_CANISTER,
                                                       constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                               CanisterMaster.available_quantity,
                                               LocationMaster.display_location,
                                               LocationMaster.location_number,
                                               DrugDimension.approx_volume,
                                               UniqueDrug.unit_weight,
                                               CanisterMaster.canister_type,
                                               UniqueDrug.drug_usage,
                                               UniqueDrug.id.alias("unique_drug_id")
                                               ).dicts() \
                .join(CanisterMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                       & (UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.company_id == company_id) &
                                                             (DrugStockHistory.is_active == settings.is_drug_active) &
                                                             (DrugStockHistory.company_id == company_id))) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=ContainerMaster.device_id == DeviceMaster.id) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=DrugDetails.unique_drug_id == UniqueDrug.id) \
                .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .where(CanisterMaster.id << list(unique_drugs.keys())) \
                .group_by(CanisterMaster.id)
            logger.info("In get_transfer_cycle_drug_data: drug_ndc_query :{}".format(drug_ndc_query))
            results, count = get_results(drug_ndc_query.dicts(),
                                         fields_dict=fields_dict,
                                         filter_fields=filter_fields,
                                         like_search_list=like_search_list,
                                         sort_fields=order_list)
            logger.info("In get_transfer_cycle_drug_data: results :{}".format(results))
            # max_refill_device_capacity = None
            # fill_extra = False
        return results, count, unique_drugs, alt_can_dic

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_transfer_cycle_drug_data {}".format(e))
        raise


@log_args_and_response
def validate_guided_tx_cycle_id_dao(guided_tx_cycle_id):
    try:
        guided_data = GuidedMeta.get(id=guided_tx_cycle_id)
        if guided_data:
            return True
        return False
    except (IntegrityError, InternalError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False


@log_args_and_response
def get_next_cycle_id(current_mini_batch: int) -> int:
    """
    This function obtains the next cycle id for the provided batch and mini_batch_id.
    @param batch_id: int
    @param current_mini_batch: int
    @return: int
    """
    try:
        next_cycle_id = None
        # obtain the next cycle id for the given mini batch and batch id whose status is pending
        next_guided_tx_cycle_id_query = GuidedMeta.select(GuidedMeta.id).dicts() \
            .where((GuidedMeta.mini_batch_id == current_mini_batch),
                   (GuidedMeta.status != constants.GUIDED_META_TO_CSR_DONE)) \
            .order_by(GuidedMeta.id).limit(1)
        if next_guided_tx_cycle_id_query.count() == 1:
            for record in next_guided_tx_cycle_id_query:
                next_cycle_id = record["id"]
        return next_cycle_id

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_next_cycle_id {}".format(e))
        raise e


@log_args_and_response
def get_system_device_for_batch() -> dict:
    """
    This function obtains the system id and device id for the given batch.
    @param batch_id: int
    @return dict
    """
    try:
        robot_zone_id: int = 0
        # robot_dict = BatchMaster.select(BatchMaster.system_id,
        #                                 DeviceMaster.id,
        #                                 DeviceLayoutDetails.zone_id
        #                                 ).dicts() \
        #     .join(DeviceMaster, on=DeviceMaster.system_id == BatchMaster.system_id) \
        #     .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
        #     .join(DeviceTypeMaster, on=DeviceMaster.device_type_id == DeviceTypeMaster.id) \
        #     .where((BatchMaster.id == batch_id), (DeviceTypeMaster.device_type_name << ["ROBOT"]))

        robot_dict = PackQueue.select(PackDetails.system_id,
                                      DeviceMaster.id,
                                      DeviceLayoutDetails.zone_id
                                      ).dicts() \
                        .join(PackDetails, on=PackDetails.id == PackQueue.pack_id) \
                        .join(DeviceMaster, on=DeviceMaster.system_id == PackDetails.system_id) \
                        .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
                        .join(DeviceTypeMaster, on=DeviceMaster.device_type_id == DeviceTypeMaster.id) \
                        .where(DeviceTypeMaster.device_type_name << ["ROBOT"]) \
                        .group_by(PackDetails.system_id)
        robot_device_ids = []
        robot_system_id = None
        for record in robot_dict:
            robot_zone_id = record['zone_id']
            robot_system_id = record['system_id']
            robot_device_ids.append(record['id'])
        csr_device_id_query = DeviceMaster.select(DeviceMaster.id.alias('csr_device_id'),
                                                  DeviceMaster.system_id.alias('csr_system_id')).dicts() \
            .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(DeviceTypeMaster, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .where((DeviceLayoutDetails.zone_id == robot_zone_id), (DeviceTypeMaster.device_type_name << ['CSR']))
        csr_device_id = []
        csr_system_id = None
        for record in csr_device_id_query:
            csr_system_id = record['csr_system_id']
            csr_device_id.append(record['csr_device_id'])
        response_dict = {robot_system_id: robot_device_ids,
                         csr_system_id: csr_device_id}
        return response_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_system_device_for_batch {}".format(e))
        raise e



@log_args_and_response
def get_empty_drawer_data_with_locations(device_id: int, quadrant: int, canister_type_dict: dict) -> tuple:
    """
    Function to get drawer list to unlock for given canister count considering device, quadrant and canister type
    @param canister_type_dict: dict
    @param device_id: int
    @param quadrant: int
    @return:
    """
    drawer_to_unlock = dict()  # key-drawer name
    locations_for_big_canisters = list()
    locations_for_small_canisters = list()
    delicate_drawers_to_unlock = dict()
    locations_for_delicate_canisters = list()

    try:
        logger.info("Input get_empty_locations_for_canister {}, {}, {}".format(device_id, quadrant, canister_type_dict))
        big_canister_count = canister_type_dict["big_canister_count"]
        small_canister_count = canister_type_dict["small_canister_count"]
        delicate_canister_count = canister_type_dict["delicate_canister_count"]
        logger.info("get_empty_locations_for_canister {}, {}, {}".format(device_id, quadrant, big_canister_count,
                                                                         small_canister_count))
        temp_big_canister = big_canister_count
        temp_small_canister = small_canister_count
        temp_delicate_canister = delicate_canister_count
        delicate_drawers = ['A', 'B', 'C']


        if not device_id or not quadrant:
            logger.error("Device id or quad is null")
            return drawer_to_unlock, delicate_drawers_to_unlock, locations_for_small_canisters, locations_for_big_canisters,\
            locations_for_delicate_canisters

        if big_canister_count == 0 and small_canister_count == 0 and delicate_canister_count == 0:
            logger.error("No canisters to be transferred")
            return drawer_to_unlock, delicate_drawers_to_unlock, locations_for_small_canisters, locations_for_big_canisters,\
            locations_for_delicate_canisters

        empty_locations_drawer_wise = db_get_drawer_wise_empty_locations_data(device_id=device_id,
                                                                              quadrant=quadrant)

        for drawer_type, container_data in empty_locations_drawer_wise.items():
            if drawer_type == settings.SIZE_OR_TYPE['BIG'] and big_canister_count > 0:
                for container, data in container_data.items():
                    if temp_big_canister <= 0:
                        break
                    if not len(data["empty_locations"]):
                        continue
                    location_count = len(data["empty_locations"])
                    data["empty_locations"] = list(data["empty_locations"])[:temp_big_canister]
                    drawer_to_unlock[str(container)] = data
                    locations_for_big_canisters.extend(data["empty_locations"])
                    temp_big_canister -= location_count
            elif drawer_type == settings.SIZE_OR_TYPE['SMALL'] and (small_canister_count>0 or delicate_canister_count > 0):
                for container, data in container_data.items():
                    if temp_delicate_canister > 0:
                        if any(substring in container for substring in delicate_drawers):
                            if temp_delicate_canister <= 0:
                                break
                            if not len(data["empty_locations"]):
                                continue
                            location_count = len(data["empty_locations"])
                            data["empty_locations"] = list(data["empty_locations"])[:temp_delicate_canister]
                            delicate_drawers_to_unlock[str(container)] = data
                            locations_for_delicate_canisters.extend(data["empty_locations"])
                            temp_delicate_canister -= location_count
                        else:
                            if temp_delicate_canister <= 0:
                                break
                            if not len(data["empty_locations"]):
                                continue
                            location_count = len(data["empty_locations"])
                            data["empty_locations"] = list(data["empty_locations"])[:temp_delicate_canister]
                            delicate_drawers_to_unlock[str(container)] = data
                            locations_for_delicate_canisters.extend(data["empty_locations"])
                            temp_delicate_canister -= location_count
                    else:
                        if temp_small_canister <= 0:
                            break
                        if not len(data["empty_locations"]):
                            continue
                        location_count = len(data["empty_locations"])
                        data["empty_locations"] = list(data["empty_locations"])[:temp_small_canister]
                        drawer_to_unlock[str(container)] = data
                        locations_for_small_canisters.extend(data["empty_locations"])
                        temp_small_canister -= location_count
            if temp_small_canister <= 0 and temp_big_canister <= 0 and temp_delicate_canister <=0:
                break

        return drawer_to_unlock, delicate_drawers_to_unlock, locations_for_small_canisters, locations_for_big_canisters,\
            locations_for_delicate_canisters

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_empty_drawer_data_with_locations {}".format(e))
        raise

    except Exception as e:
        logger.error("Error in get_empty_drawer_data_with_locations {}".format(e))
        return drawer_to_unlock, delicate_drawers_to_unlock, locations_for_small_canisters, locations_for_big_canisters,\
            locations_for_delicate_canisters


@log_args_and_response
def fetch_empty_locations_count_quadrant_wise_based_on_device_ids(device_ids: list,
                                                                  consider_higher_drawers: bool) -> dict:
    """
    Method to fetch empty locations of devices
    @param consider_higher_drawers:
    @param device_ids:
    @return:
    """
    try:
        empty_locations_dict = dict()
        query = LocationMaster.select(LocationMaster.device_id, LocationMaster.quadrant,
                                      fn.COUNT(LocationMaster.id).alias("empty_locations_count")).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .where(LocationMaster.device_id << device_ids, CanisterMaster.id.is_null(True),
                   ContainerMaster.drawer_type != constants.MFD_DRAWER_TYPE_ID) \
            .group_by(LocationMaster.device_id, LocationMaster.quadrant)

        if not consider_higher_drawers:
            query = query.where(ContainerMaster.drawer_level.not_in(settings.DRAWER_LEVEL["lift_trolley"]))

        for record in query:
            if not record["device_id"] in empty_locations_dict.keys():
                empty_locations_dict[record["device_id"]] = dict()
            empty_locations_dict[record["device_id"]][record["quadrant"]] = record["empty_locations_count"]

        return empty_locations_dict
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in fetch_empty_locations_count_quadrant_wise_based_on_device_ids {}".format(e))
        raise e


@log_args_and_response
def get_canisters_to_be_removed_from_robot(device_id: int, container_id: int, guided_tx_cycle_id: int,
                                           no_of_canisters: int, drawers_to_unlock: dict, quadrant: int,
                                           delicate_drawers_to_unlock:dict) -> tuple:
    """
    Method to get canisters that are to be removed from robot that are to be replaced by alternate canisters
    @param container_id:
    @param no_of_canisters:
    @param device_id:
    @param guided_tx_cycle_id:
    @param drawers_to_unlock:
    @param quadrant:
    @return:
    """
    try:
        canister_list = list()
        canister_ids = list()

        if not quadrant:
            logger.info("get_canisters_to_be_removed_from_robot: quadrant is None so fetching it")
            try:
                # first fetch quadrant based on trolley drawer id
                LocationMasterAlias1 = LocationMaster.alias()
                query = GuidedTracker.select(LocationMasterAlias1.quadrant).dicts() \
                    .join(LocationMaster, on=LocationMaster.id == GuidedTracker.cart_location_id) \
                    .join(LocationMasterAlias1, on=GuidedTracker.destination_location_id == LocationMasterAlias1.id) \
                    .where(LocationMasterAlias1.device_id == device_id, LocationMaster.container_id == container_id,
                           GuidedTracker.guided_meta_id == guided_tx_cycle_id).get()
                quadrant = query["quadrant"]
            except DoesNotExist as e:
                logger.info(
                    "get_canisters_to_be_removed_from_robot: No quadrant attached with scanned drawer: {}".format(e))
                pass

        if quadrant:
            logger.info("get_canisters_to_be_removed_from_robot: Fetching canisters to be removed first from quadrant:"
                         " " + str(quadrant))
            quadrant_query = GuidedTracker.select(GuidedTracker.source_canister_id.alias("canister_id"),
                                                  CanisterMaster.active,
                                                  DrugMaster.id.alias('drug_id'),
                                                  DrugMaster.concated_drug_name_field(include_ndc=True).alias(
                                                      'drug_name'),
                                                  LocationMaster.container_id.alias("current_container_id"),
                                                  LocationMaster.display_location.alias('current_display_location'),
                                                  LocationMaster.quadrant.alias('current_quadrant'),
                                                  LocationMaster.device_id.alias('current_device_id'),
                                                  DeviceMaster.ip_address.alias("device_ip_address"),
                                                  DeviceMaster.device_type_id.alias('current_device_type_id'),
                                                  ContainerMaster.drawer_name,
                                                  ContainerMaster.serial_number,
                                                  ContainerMaster.ip_address,
                                                  ContainerMaster.secondary_ip_address,
                                                  ContainerMaster.shelf,
                                                  DrugMaster.imprint,
                                                  DrugMaster.image_name,
                                                  DrugMaster.color,
                                                  DrugMaster.shape,
                                                  DrugDetails.last_seen_by,
                                                  DrugDetails.last_seen_date,
                                                  GuidedTracker.transfer_status,
                                                  fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                                        DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                                  UniqueDrug.is_delicate).dicts() \
                .join(CanisterMaster, on=CanisterMaster.id == GuidedTracker.source_canister_id) \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(DeviceMaster, on=LocationMaster.device_id == DeviceMaster.id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                       & (UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == settings.is_drug_active) &
                                                             (
                                                                     DrugStockHistory.company_id == CanisterMaster.company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=DrugDetails.unique_drug_id == UniqueDrug.id) \
                .where(GuidedTracker.alternate_canister_id.is_null(False),
                       GuidedTracker.guided_meta_id == guided_tx_cycle_id, LocationMaster.device_id == device_id,
                       LocationMaster.quadrant == quadrant,
                       GuidedTracker.transfer_status.in_(constants.guided_tracker_to_robot_status_list)) \
                .group_by(CanisterMaster.id) \
                .order_by(LocationMaster.id) \
                .limit(no_of_canisters)

            for record in quadrant_query:
                record["to_device"] = False

                if record['transfer_status'] == constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE:
                    record['alternate_canister'] = True
                else:
                    record['alternate_canister'] = False
                if record['is_delicate']:
                    if not record["drawer_name"] in delicate_drawers_to_unlock.keys():
                        delicate_drawers_to_unlock[record["drawer_name"]] = {'id': record["current_container_id"],
                                                                    'drawer_name': record["drawer_name"],
                                                                    'serial_number': record["serial_number"],
                                                                    "device_ip_address": record["device_ip_address"],
                                                                    'ip_address': record['ip_address'],
                                                                    'secondary_ip_address': record['secondary_ip_address'],
                                                                    'device_type_id': record['current_device_type_id'],
                                                                    'shelf': record['shelf'],
                                                                    'to_device': list(),
                                                                    'from_device': list()}
                    if record["current_display_location"] not in delicate_drawers_to_unlock[record["drawer_name"]]["from_device"]:
                        delicate_drawers_to_unlock[record["drawer_name"]]["from_device"].append(record["current_display_location"])
                else:
                    if not record["drawer_name"] in drawers_to_unlock.keys():
                        drawers_to_unlock[record["drawer_name"]] = {'id': record["current_container_id"],
                                                                    'drawer_name': record["drawer_name"],
                                                                    'serial_number': record["serial_number"],
                                                                    "device_ip_address": record["device_ip_address"],
                                                                    'ip_address': record['ip_address'],
                                                                    'secondary_ip_address': record['secondary_ip_address'],
                                                                    'device_type_id': record['current_device_type_id'],
                                                                    'shelf': record['shelf'],
                                                                    'to_device': list(),
                                                                    'from_device': list()}
                    if record["current_display_location"] not in drawers_to_unlock[record["drawer_name"]]["from_device"]:
                        drawers_to_unlock[record["drawer_name"]]["from_device"].append(record["current_display_location"])
                canister_list.append(record)
                canister_ids.append(record["canister_id"])

        canister_count = len(canister_list)
        if canister_count < no_of_canisters:
            logger.info("get_canisters_to_be_removed_from_robot: There are empty locations in cart drawer"
                         " so fetching more canisters to be removed")
            no_of_canisters -= canister_count

            query = GuidedTracker.select(GuidedTracker.source_canister_id.alias("canister_id"),
                                         GuidedTracker.transfer_status,
                                         CanisterMaster.active,
                                         fn.IF(
                                             CanisterMaster.expiry_date <= date.today() + timedelta(
                                                 settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                             constants.EXPIRED_CANISTER,
                                             fn.IF(
                                                 CanisterMaster.expiry_date <= date.today() + timedelta(
                                                     settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                                 constants.EXPIRES_SOON_CANISTER,
                                                 constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                         DrugMaster.id.alias('drug_id'),
                                         DrugMaster.concated_drug_name_field(include_ndc=True).alias(
                                             'drug_name'),
                                         LocationMaster.display_location.alias('current_display_location'),
                                         LocationMaster.quadrant.alias('current_quadrant'),
                                         LocationMaster.device_id.alias('current_device_id'),
                                         DeviceMaster.ip_address.alias("device_ip_address"),
                                         DeviceMaster.device_type_id.alias('current_device_type_id'),
                                         ContainerMaster.drawer_name,
                                         ContainerMaster.id.alias("current_container_id"),
                                         ContainerMaster.serial_number,
                                         ContainerMaster.ip_address,
                                         ContainerMaster.secondary_ip_address,
                                         ContainerMaster.shelf,
                                         DrugMaster.imprint,
                                         DrugMaster.image_name,
                                         DrugMaster.color,
                                         DrugMaster.shape,
                                         DrugDetails.last_seen_by,
                                         DrugDetails.last_seen_date,
                                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                               DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                         ).dicts() \
                .join(CanisterMaster, on=CanisterMaster.id == GuidedTracker.source_canister_id) \
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(DeviceMaster, on=LocationMaster.device_id == DeviceMaster.id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                       & (UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == settings.is_drug_active) &
                                                             (
                                                                     DrugStockHistory.company_id == CanisterMaster.company_id))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=DrugDetails.unique_drug_id == UniqueDrug.id) \
                .where(GuidedTracker.alternate_canister_id.is_null(False),
                       GuidedTracker.guided_meta_id == guided_tx_cycle_id,
                       LocationMaster.device_id == device_id,
                       GuidedTracker.transfer_status.in_(constants.guided_tracker_to_robot_status_list)
                       ) \
                .group_by(CanisterMaster.id) \
                .order_by(LocationMaster.id) \
                .limit(no_of_canisters)

            if canister_ids:
                query = query.where(GuidedTracker.source_canister_id.not_in(canister_ids))

            for record1 in query:
                record1["to_device"] = False

                if record1['transfer_status'] == constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE:
                    record1['alternate_canister'] = True
                else:
                    record1['alternate_canister'] = False

                if not record1["drawer_name"] in drawers_to_unlock.keys():
                    drawers_to_unlock[record1["drawer_name"]] = {'id': record1["current_container_id"],
                                                                 'drawer_name': record1["drawer_name"],
                                                                 'serial_number': record1["serial_number"],
                                                                 "device_ip_address": record1["device_ip_address"],
                                                                 'ip_address': record1['ip_address'],
                                                                 'secondary_ip_address': record1[
                                                                     'secondary_ip_address'],
                                                                 'device_type_id': record1['current_device_type_id'],
                                                                 'shelf': record1['shelf'],
                                                                 'to_device': list(),
                                                                 'from_device': list()}
                if record1["current_display_location"] not in drawers_to_unlock[record1["drawer_name"]]["from_device"]:
                    drawers_to_unlock[record1["drawer_name"]]["from_device"].append(record1["current_display_location"])

                canister_list.append(record1)

        return canister_list, drawers_to_unlock
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canisters_to_be_removed_from_robot {}".format(e))
        raise e

def get_transferred_canisters_of_robot_to_trolley(container_id: int, guided_cycle_id: int) -> list:
    """
    Method to fetch source canisters having alternate canisters in guided tracker and are already transferred to trolley
    @param container_id:
    @param guided_cycle_id:
    @return:
    """
    try:
        canisters_query = GuidedTracker.select(CanisterMaster.id.alias("canister_id")).dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == GuidedTracker.source_canister_id) \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .where(GuidedTracker.alternate_canister_id.is_null(False), LocationMaster.container_id == container_id,
                   GuidedTracker.guided_meta_id == guided_cycle_id)
        return list(canisters_query)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_transferred_canisters_of_robot_to_trolley {}".format(e))
        raise e


@log_args_and_response
def db_get_existing_guided_canister_transfer_data(canister_list: list,
                                                  filter_status: [list, None]) -> tuple:
    """
    Function to get canister data from guided transfer tables for given canister list
    @param filter_status:
    @param canister_list:
    @param batch_id:
    @return:
    """
    canister_info_dict = dict()
    guided_tracker_ids = set()
    canister_ids = set()

    try:
        #remove batch id from clauses. >> already clauses have check on status.

        clauses = [((GuidedTracker.source_canister_id << canister_list) |
                    (GuidedTracker.alternate_canister_id << canister_list)),
                   GuidedMeta.status.not_in([constants.GUIDED_META_RECOMMENDATION_DONE,
                                             constants.GUIDED_META_TO_CSR_DONE])
                   ]

        if filter_status:
            clauses.append(GuidedTracker.transfer_status << filter_status)

        LocationMasterAlias = LocationMaster.alias()
        # LocationMasterAlias1 = LocationMaster.alias()
        # DeviceMasterAlias = DeviceMaster.alias()

        query = GuidedTracker.select(GuidedTracker.source_canister_id,
                                     GuidedTracker.alternate_canister_id,
                                     GuidedTracker.destination_location_id,
                                     GuidedTracker.cart_location_id,
                                     GuidedTracker.guided_meta_id,
                                     GuidedTracker.transfer_status,
                                     GuidedTracker.required_qty,
                                     LocationMaster.device_id.alias('trolley_id'),
                                     LocationMaster.container_id.alias('trolley_container_id'),
                                     GuidedMeta.batch_id,
                                     GuidedTracker.id.alias('guided_tracker_id'),
                                     LocationMasterAlias.device_id.alias('dest_device'),
                                     LocationMasterAlias.quadrant.alias('dest_quadrant'),
                                     LocationMasterAlias.container_id.alias("dest_container_id"),
                                     LocationMasterAlias.quadrant.alias('dest_quadrant'),
                                     LocationMasterAlias.device_id.alias('dest_device'),
                                     GuidedMeta.status.alias("guided_meta_status"),
                                     DeviceMaster.system_id.alias("dest_system_id"),
                                     DeviceMaster.device_type_id.alias("dest_device_type_id"),
                                     # todo - check where this is required.
                                     # DeviceMasterAlias.device_type_id.alias('current_device_type_id')

                                     ).dicts() \
            .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
            .join(LocationMaster, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == GuidedTracker.destination_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .where(*clauses) \
            .order_by(GuidedTracker.id.desc())

        # todo- add below join to uncomment current_device_type_id
        # .join(CanisterMaster, on=(fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
        #                                 GuidedTracker.alternate_canister_id,
        #                                 GuidedTracker.source_canister_id)) == CanisterMaster.id) \
        # .join(LocationMasterAlias1, JOIN_LEFT_OUTER, on=LocationMasterAlias1.id == CanisterMaster.location_id) \
        # .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMasterAlias1.device_id) \
        for record in query:
            # get canister data from guided tables - there can be source or alternate or both source
            # and alternate canisters can be there in canisters list so considering both
            canister_id1 = record['source_canister_id'] if record['source_canister_id'] in canister_list else None
            canister_id2 = record['alternate_canister_id'] if record["alternate_canister_id"] \
                                                              and record[
                                                                  "alternate_canister_id"] in canister_list else None

            if canister_id1 and canister_id1 not in canister_ids:
                canister_ids.add(canister_id1)
                canister_info_dict[canister_id1] = record
                guided_tracker_ids.add(record['guided_tracker_id'])

            if canister_id2 and canister_id2 not in canister_ids:
                canister_ids.add(canister_id2)
                canister_info_dict[canister_id2] = record
                guided_tracker_ids.add(record['guided_tracker_id'])

        return canister_info_dict, list(guided_tracker_ids)

    except (InternalError, IntegrityError, ValueError) as e:
        logger.error("Error in db_get_existing_guided_canister_transfer_data {}".format(e))
        raise


@log_args_and_response
def add_data_in_guided_transfer_history_tables(existing_canisters_data: dict,
                                               original_canister: list,
                                               skip_status: int,
                                               action: int,
                                               comment: [str, None],
                                               user_id: int):
    """
    Function to insert data in canister transfer cycle history and canister transfer history comment
    @param existing_canisters_data:
    @param original_canister:
    @param skip_status:
    @param action:
    @param comment:
    @param user_id:
    @return:
    """
    try:
        for canister in original_canister:
            insert_data = {'guided_tracker_id': existing_canisters_data[canister]['guided_tracker_id'],
                           'canister_id': canister,
                           'action_id': action,
                           'current_status_id': skip_status,
                           'previous_status_id': existing_canisters_data[canister]['transfer_status'],
                           'action_taken_by': user_id,
                           'action_datetime': get_current_date_time()
                           }

            # add data in GuidedTransferCycleHistory
            record = GuidedTransferCycleHistory.insert_guided_transfer_cycle_history_data(data_dict=insert_data)
            transfer_cycle_history = record.id
            logger.info("Data added in guided transfer cycle history {}".format(insert_data))

            if comment:
                comment_data = {'guided_transfer_history_id': transfer_cycle_history, 'comment': comment}

                # add data in GuidedTransferHistoryComment
                comment_record = GuidedTransferHistoryComment.insert_guided_transfer_history_comment_data(
                    data_dict=comment_data)
                comment_record_id = comment_record.id
                logger.info("Data added in guided transfer cycle history comment {}".format(comment_data))

                logger.info("Data added in guided transfer history tables {}, {}".format(transfer_cycle_history,
                                                                                         comment_record_id))

        return True

    except ValueError as e:
        logger.error("Error in add_data_in_guided_transfer_history_tables {}".format(e))
        raise ValueError
    except (InternalError, IntegrityError) as e:
        logger.error("Error in add_data_in_guided_transfer_history_tables {}".format(e))
        raise


@log_args_and_response
def add_data_in_guided_transfer_cycle_history(insert_data: list) -> bool:
    """
    Function to add data in guided transfer cycle history
    @param insert_data:
    @return:
    """
    try:
        # add data in GuidedTransferCycleHistory
        response = GuidedTransferCycleHistory.add_multiple_guided_transfer_cycle_history_data(insert_data=insert_data)
        return response

    except ValueError as e:
        logger.error("Error in add_data_in_guided_transfer_cycle_history {}".format(e))
        return False
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in add_data_in_guided_transfer_cycle_history {}".format(e))
        return False


@log_args_and_response
def get_out_of_stock_tx_ids(guided_tx_cycle_id: int, user_id, company_id) -> tuple:
    guided_tracker_list = list()
    guided_tracker_history_list = list()
    recommended_alternate_canisters = list()
    try:
        canister_data_query = GuidedTracker.select(GuidedTracker.source_canister_id,
                                                   GuidedTracker.alternate_canister_id,
                                                   GuidedTracker.id.alias('guided_tracker_id'),
                                                   GuidedTracker.alt_can_replenish_required,
                                                   GuidedTracker.required_qty).dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == GuidedTracker.source_canister_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == settings.is_drug_active) &
                                                         (DrugStockHistory.company_id == company_id))) \
            .where(GuidedTracker.guided_meta_id == guided_tx_cycle_id,
                   GuidedTracker.transfer_status == constants.GUIDED_TRACKER_PENDING,
                   DrugStockHistory.id.is_null(False),
                   DrugStockHistory.is_in_stock != settings.is_drug_active)
        for canister in canister_data_query:
            guided_tracker_list.append(canister['guided_tracker_id'])
            if canister["alternate_canister_id"]:
                recommended_alternate_canisters.append(canister["alternate_canister_id"])

            insert_data = {'guided_tracker_id': canister['guided_tracker_id'],
                           'canister_id': canister['alternate_canister_id'] if canister['alternate_canister_id'] else
                           canister['source_canister_id'],
                           'action_id': constants.GUIDED_TRACKER_TRANSFER_ACTION,
                           'current_status_id': constants.GUIDED_TRACKER_DRUG_SKIPPED,
                           'previous_status_id': constants.GUIDED_TRACKER_PENDING,
                           'action_taken_by': user_id,
                           'action_datetime': get_current_date_time()
                           }
            guided_tracker_history_list.append(insert_data)

        return guided_tracker_list, guided_tracker_history_list, recommended_alternate_canisters

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_out_of_stock_tx_ids {}".format(e))
        raise

@log_args_and_response
def get_pending_canister_transfer_to_trolley_guided(company_id, device_id, guided_meta_id, trolley_id):
    try:
        device_id = int(device_id)
        couch_db_canisters = list()
        response_list = list()
        drawers_to_unlock = dict()
        delicate_drawers_to_unlock = dict()
        LocationMasterAlias1 = LocationMaster.alias()
        LocationMasterAlias2 = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        DeviceMasterAlias1 = DeviceMaster.alias()
        GuidedTransferCycleHistoryAlias = GuidedTransferCycleHistory.alias()

        sub_query = GuidedTransferCycleHistoryAlias.select(
            fn.MAX(GuidedTransferCycleHistoryAlias.id).alias('max_guided_transfer_cycle_id'),
            GuidedTransferCycleHistoryAlias.guided_tracker_id.alias('guided_tracker_id')) \
            .group_by(GuidedTransferCycleHistoryAlias.guided_tracker_id).alias('sub_query')

        select_fields = [CanisterMaster.active,
                         GuidedTracker.transfer_status,
                         GuidedTransferHistoryComment.comment,
                         GuidedTransferCycleHistory.action_id,
                         GuidedTransferCycleHistory.current_status_id,
                         GuidedTransferCycleHistory.previous_status_id,
                         CanisterMaster.id.alias('canister_id'),
                         fn.IF(
                             CanisterMaster.expiry_date <= date.today() + timedelta(
                                 settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                             constants.EXPIRED_CANISTER,
                             fn.IF(
                                 CanisterMaster.expiry_date <= date.today() + timedelta(
                                     settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                 constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias(
                             "expiry_status"),
                         DrugMaster.id.alias('drug_id'),
                         DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                         LocationMaster.id.alias('source_canister_location'),
                         LocationMaster.container_id.alias('source_container'),
                         LocationMaster.display_location.alias('source_display_location'),
                         LocationMaster.device_id.alias('source_can_device'),
                         DeviceMaster.name.alias('current_device_name'),
                         DeviceMaster.device_type_id.alias('source_device_type_id'),
                         ContainerMaster.id.alias("container_id"),
                         ContainerMaster.serial_number,
                         ContainerMaster.drawer_name,
                         ContainerMaster.secondary_ip_address,
                         ContainerMaster.secondary_mac_address,
                         ContainerMaster.ip_address,
                         ContainerMaster.mac_address,
                         ContainerMaster.drawer_name.alias('source_drawer_name'),
                         DrugMaster.imprint,
                         DrugMaster.image_name,
                         DrugMaster.color,
                         DrugMaster.shape,
                         DrugDetails.last_seen_by,
                         DrugDetails.last_seen_date,
                         LocationMasterAlias2.display_location.alias('dest_display_location'),
                         DeviceMasterAlias.device_type_id.alias('dest_device_type_id'),
                         DeviceMasterAlias1.id.alias('dest_device_id'),
                         DeviceMasterAlias1.name.alias('dest_device_name'),
                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                               DrugStockHistory.is_in_stock).alias("is_in_stock"),
                         fn.IF(GuidedTracker.transfer_status ==
                               constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE, True, False)
                             .alias('alternate_canister'),
                         UniqueDrug.is_delicate
                         ]

        query = GuidedTracker.select(*select_fields).dicts() \
            .join(CanisterMaster, on=(fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                            GuidedTracker.alternate_canister_id,
                                            GuidedTracker.source_canister_id)) == CanisterMaster.id) \
            .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
            .join(sub_query, JOIN_LEFT_OUTER, on=sub_query.c.guided_tracker_id == GuidedTracker.id) \
            .join(GuidedTransferCycleHistory, JOIN_LEFT_OUTER,
                  on=GuidedTransferCycleHistory.id == sub_query.c.max_guided_transfer_cycle_id) \
            .join(GuidedTransferHistoryComment, JOIN_LEFT_OUTER,
                  on=GuidedTransferHistoryComment.guided_transfer_history_id == sub_query.c.max_guided_transfer_cycle_id) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER,
                  on=LocationMasterAlias2.id == GuidedTracker.cart_location_id) \
            .join(DeviceMasterAlias1, JOIN_LEFT_OUTER, on=DeviceMasterAlias1.id == LocationMasterAlias2.device_id) \
            .join(LocationMasterAlias1, on=GuidedTracker.destination_location_id == LocationMasterAlias1.id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == LocationMasterAlias1.device_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                   & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == settings.is_drug_active) &
                                                         (DrugStockHistory.company_id == company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == company_id))) \
            .where(((LocationMaster.device_id == device_id) | (LocationMaster.id.is_null(True)) |
                    (GuidedTracker.transfer_status << [constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE_TRANSFER_LATER,
                                                       constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE])),
                   CanisterMaster.company_id == company_id,
                   GuidedTracker.guided_meta_id == guided_meta_id,
                   GuidedTracker.transfer_status << [constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE_TRANSFER_LATER,
                                                     constants.GUIDED_TRACKER_TO_TROLLEY_SKIPPED,
                                                     constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE],
                   LocationMasterAlias2.device_id == trolley_id) \
            .order_by(LocationMaster.id)

        for record in query:
            if record['canister_id']:
                couch_db_canisters.append(record['canister_id'])
            if record['is_delicate']:
                if record['drawer_name'] and record['drawer_name'] not in delicate_drawers_to_unlock.keys():
                    delicate_drawers_to_unlock[record['drawer_name']] = {'id': record["container_id"],
                                                                'drawer_name': record["drawer_name"],
                                                                'serial_number': record["serial_number"],
                                                                'ip_address': record['ip_address'],
                                                                'secondary_ip_address': record['secondary_ip_address'],
                                                                'device_type_id': record['source_device_type_id'],
                                                                'to_device': list(),
                                                                'from_device': list()}
                if record["source_display_location"] and \
                        record["source_display_location"] not in delicate_drawers_to_unlock[record['drawer_name']]["from_device"]:
                    delicate_drawers_to_unlock[record['drawer_name']]["from_device"].append(record["source_display_location"])
            else:
                if record['drawer_name'] and record['drawer_name'] not in drawers_to_unlock.keys():
                    drawers_to_unlock[record['drawer_name']] = {'id': record["container_id"],
                                                                'drawer_name': record["drawer_name"],
                                                                'serial_number': record["serial_number"],
                                                                'ip_address': record['ip_address'],
                                                                'secondary_ip_address': record['secondary_ip_address'],
                                                                'device_type_id': record['source_device_type_id'],
                                                                'to_device': list(),
                                                                'from_device': list()}
                if record["source_display_location"] and \
                        record["source_display_location"] not in drawers_to_unlock[record['drawer_name']]["from_device"]:
                    drawers_to_unlock[record['drawer_name']]["from_device"].append(record["source_display_location"])
            response_list.append(record)

        return response_list, drawers_to_unlock,delicate_drawers_to_unlock, couch_db_canisters
    except DoesNotExist as e:
        logger.error("error in get_pending_canister_transfer_to_trolley_guided {}".format(e))
        raise DoesNotExist
    except InternalError as e:
        logger.error("error in get_pending_canister_transfer_to_trolley_guided {}".format(e))
        raise InternalError


@log_args_and_response
def get_pending_canister_transfer_from_trolley_guided(company_id, device_id, guided_meta_id, trolley_id):
    try:
        device_id = int(device_id)
        canister_list = list()
        response_list = list()
        LocationMasterAlias1 = LocationMaster.alias()
        LocationMasterAlias2 = LocationMaster.alias()
        LocationMasterAlias3 = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()

        guided_transfer_canister_comment = dict()
        quad_canister_type_dict: dict = dict()

        GuidedTransferCycleHistoryAlias = GuidedTransferCycleHistory.alias()

        sub_query = GuidedTransferCycleHistoryAlias.select(
            fn.MAX(GuidedTransferCycleHistoryAlias.id).alias('max_guided_transfer_cycle_id'),
            GuidedTransferCycleHistoryAlias.guided_tracker_id.alias('guided_tracker_id')) \
            .group_by(GuidedTransferCycleHistoryAlias.guided_tracker_id).alias('sub_query')

        canister_list_query = GuidedTracker.select(LocationMasterAlias1.container_id, ContainerMaster.drawer_name,
                                                   fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                         GuidedTracker.alternate_canister_id,
                                                         GuidedTracker.source_canister_id).alias(
                                                       'transfer_canister'),
                                                   fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                         True,
                                                         False).alias(
                                                       'swap_canister'),
                                                   LocationMasterAlias1.device_id.alias("dest_device"),
                                                   LocationMasterAlias1.quadrant.alias("dest_quadrant"),
                                                   LocationMasterAlias3.device_id.alias("current_device"),
                                                   LocationMasterAlias3.quadrant.alias("current_quadrant"),
                                                   ContainerMasterAlias.drawer_type.alias("current_drawer_type"),
                                                   DeviceMaster.name.alias("current_device_name"),
                                                   DeviceMaster.device_type_id.alias("current_device_type_id"),
                                                   LocationMasterAlias3.display_location.alias(
                                                       "current_display_location"),
                                                   GuidedTracker.transfer_status,
                                                   GuidedTransferHistoryComment.comment,
                                                   GuidedTransferCycleHistory.action_id,
                                                   GuidedTransferCycleHistory.current_status_id,
                                                   GuidedTransferCycleHistory.previous_status_id,
                                                   ContainerMaster.ip_address,
                                                   ContainerMaster.mac_address,
                                                   ContainerMaster.secondary_ip_address,
                                                   ContainerMaster.secondary_mac_address,
                                                   CanisterMaster.canister_type,
                                                   ).dicts() \
            .join(LocationMasterAlias1, on=GuidedTracker.destination_location_id == LocationMasterAlias1.id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias1.container_id) \
            .join(LocationMasterAlias2, on=LocationMasterAlias2.id == GuidedTracker.cart_location_id) \
            .join(CanisterMaster, on=(fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                            GuidedTracker.alternate_canister_id,
                                            GuidedTracker.source_canister_id)) == CanisterMaster.id) \
            .join(LocationMasterAlias3, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMasterAlias3.id) \
            .join(ContainerMasterAlias, JOIN_LEFT_OUTER,
                  on=ContainerMasterAlias.id == LocationMasterAlias3.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMasterAlias3.device_id == DeviceMaster.id) \
            .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
            .join(sub_query, JOIN_LEFT_OUTER, on=sub_query.c.guided_tracker_id == GuidedTracker.id) \
            .join(GuidedTransferCycleHistory, JOIN_LEFT_OUTER,
                  on=GuidedTransferCycleHistory.id == sub_query.c.max_guided_transfer_cycle_id) \
            .join(GuidedTransferHistoryComment, JOIN_LEFT_OUTER,
                  on=GuidedTransferHistoryComment.guided_transfer_history_id == GuidedTransferCycleHistory.id) \
            .where(GuidedTracker.guided_meta_id == guided_meta_id,
                   GuidedTracker.transfer_status << [constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE_TRANSFER_LATER,
                                                     constants.GUIDED_TRACKER_TO_ROBOT_SKIPPED,
                                                     constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE],
                   LocationMasterAlias1.device_id == device_id,
                   LocationMasterAlias2.device_id == trolley_id
                   )

        for record in canister_list_query:
            if record["dest_device"] == record["current_device"] and \
                    record["dest_quadrant"] == record["current_quadrant"] and \
                    not (record["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and
                         record["current_drawer_type"] == settings.SIZE_OR_TYPE["SMALL"]):
                continue
            canister_list.append(record['transfer_canister'])
            guided_transfer_canister_comment[record['transfer_canister']] = record["comment"]

        select_fields = [GuidedTracker.transfer_status,
                         CanisterMaster.active,
                         CanisterMaster.id.alias('canister_id'),
                         fn.IF(
                             CanisterMaster.expiry_date <= date.today() + timedelta(
                                 settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                             constants.EXPIRED_CANISTER,
                             fn.IF(
                                 CanisterMaster.expiry_date <= date.today() + timedelta(
                                     settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                 constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias(
                             "expiry_status"),
                         CanisterMaster.canister_type,
                         DrugMaster.id.alias('drug_id'),
                         DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                         LocationMaster.device_id.alias('dest_can_device'),
                         LocationMaster.quadrant.alias('dest_quadrant'),
                         DeviceMasterAlias.name.alias('dest_device_name'),
                         DeviceMasterAlias.device_type_id.alias('dest_device_type_id'),
                         ContainerMaster.drawer_name,
                         LocationMasterAlias1.display_location.alias('current_disp_loc'),
                         LocationMasterAlias1.display_location.alias('current_display_location'),
                         LocationMasterAlias1.quadrant.alias('current_quadrant'),
                         LocationMasterAlias1.device_id.alias('current_device_id'),
                         DeviceMaster.name.alias('current_device_name'),
                         DeviceMaster.device_type_id.alias('source_device_type_id'),
                         ContainerMasterAlias.id.alias("source_container_id"),
                         ContainerMasterAlias.serial_number,
                         ContainerMasterAlias.drawer_name.alias('source_drawer_name'),
                         ContainerMasterAlias.secondary_ip_address,
                         ContainerMasterAlias.secondary_mac_address,
                         ContainerMasterAlias.ip_address,
                         ContainerMasterAlias.mac_address,
                         DrugMaster.imprint,
                         DrugMaster.image_name,
                         DrugMaster.color,
                         DrugMaster.shape,
                         DrugDetails.last_seen_by,
                         DrugDetails.last_seen_date,
                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                               DrugStockHistory.is_in_stock).alias("is_in_stock"),
                         fn.IF(GuidedTracker.transfer_status ==
                               constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE, True, False)
                             .alias('alternate_canister'),
                         UniqueDrug.is_delicate
                         ]

        if len(canister_list):
            query = CanisterMaster.select(*select_fields).dicts() \
                .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
                .join(GuidedTracker, on=(fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                               GuidedTracker.alternate_canister_id,
                                               GuidedTracker.source_canister_id)) == CanisterMaster.id) \
                .join(LocationMaster, on=LocationMaster.id == GuidedTracker.destination_location_id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMasterAlias, on=DeviceMasterAlias.id == ContainerMaster.device_id) \
                .join(LocationMasterAlias1, JOIN_LEFT_OUTER, on=LocationMasterAlias1.id == CanisterMaster.location_id) \
                .join(ContainerMasterAlias, JOIN_LEFT_OUTER,
                      on=ContainerMasterAlias.id == LocationMasterAlias1.container_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias1.device_id) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugMaster.id == DrugStockHistory.unique_drug_id) &
                                                             (DrugStockHistory.is_active == settings.is_drug_active))) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                       & (UniqueDrug.txr == DrugMaster.txr))) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=DrugDetails.unique_drug_id == UniqueDrug.id) \
                .where(CanisterMaster.company_id == company_id,
                       GuidedTracker.guided_meta_id == guided_meta_id,
                       GuidedTracker.transfer_status << [constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE_TRANSFER_LATER,
                                                         constants.GUIDED_TRACKER_TO_ROBOT_SKIPPED,
                                                         constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE],
                       CanisterMaster.id << canister_list) \
                .group_by(CanisterMaster.id) \
                .order_by(LocationMaster.container_id)

            for record in query:
                # flag to show this are for placing canisters in robot
                record["to_device"] = True
                # Added Below condition to guide user to place canister at recommend quadrant
                # if user placed a canister at wrong quadrant or device

                record["current_display_location"] = record["current_disp_loc"]
                record["current_device"] = record["current_device_id"]
                record["current_device_name"] = record["current_device_name"]

                record["comment"] = guided_transfer_canister_comment[record['canister_id']]

                if record['dest_quadrant'] not in quad_canister_type_dict.keys():
                    canister_type_dict = {"small_canister_count": 0, "big_canister_count": 0,"delicate_canister_count":0}
                    quad_canister_type_dict[record['dest_quadrant']] = canister_type_dict

                if record['canister_type'] == settings.SIZE_OR_TYPE['BIG']:
                    quad_canister_type_dict[record['dest_quadrant']]["big_canister_count"] += 1
                else:
                    if record['is_delicate']:
                        quad_canister_type_dict[record['dest_quadrant']]["delicate_canister_count"] +=1
                    else:
                        quad_canister_type_dict[record['dest_quadrant']]["small_canister_count"] += 1
                response_list.append(record)

        return response_list, quad_canister_type_dict
    except DoesNotExist as e:
        logger.error("error in get_pending_canister_transfer_from_trolley_guided {}".format(e))
        raise DoesNotExist
    except InternalError as e:
        logger.error("error in get_pending_canister_transfer_from_trolley_guided {}".format(e))
        raise InternalError
    except Exception as e:
        logger.error("error in get_pending_canister_transfer_from_trolley_guided {}".format(e))


@log_args_and_response
def get_pending_transfer_from_trolley_to_csr(mini_batch,
                                             trolley_id,
                                             guided_canister_status,
                                             system_id):
    try:
        LocationMasterALias = LocationMaster.alias()
        LocationMasterAlias1 = LocationMaster.alias()
        pending_devices = list()

        pending_devices_query = GuidedTracker.select(DeviceMaster.id.alias('pending_device_id'),
                                                     DeviceMaster.name.alias('pending_device_name'),
                                                     DeviceMaster.device_type_id.alias('pending_device_type_id'),
                                                     DeviceMaster.system_id.alias('pending_device_system_id')
                                                     ).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(LocationMasterALias, on=LocationMasterALias.id == GuidedTracker.destination_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterALias.device_id) \
            .join(CanisterMaster, on=fn.IF(GuidedTracker.transfer_status.in_([constants.GUIDED_TRACKER_TRANSFER_SKIPPED,
                                                                              constants.GUIDED_TRACKER_TO_ROBOT_SKIPPED]),
                                           fn.IF(GuidedTracker.alternate_canister_id.is_null(False),
                                                 GuidedTracker.alternate_canister_id,
                                                 GuidedTracker.source_canister_id),
                                           GuidedTracker.source_canister_id) == CanisterMaster.id) \
            .join(LocationMasterAlias1, on=LocationMasterAlias1.id == CanisterMaster.location_id) \
            .where(GuidedTracker.guided_meta_id == mini_batch,
                   GuidedTracker.transfer_status << guided_canister_status,
                   LocationMasterAlias1.device_id != DeviceMaster.id,
                   LocationMaster.device_id == trolley_id,
                   DeviceMaster.system_id == system_id) \
            .group_by(DeviceMaster.id)

        for record in pending_devices_query:
            pending_devices.append(record)

        return pending_devices

    except DoesNotExist as e:
        logger.error("error in get_pending_transfer_from_trolley_to_csr {}".format(e))
        return None
    except InternalError as e:
        logger.error("error in get_pending_transfer_from_trolley_to_csr {}".format(e))
        raise InternalError


@log_args_and_response
def add_data_in_guided_misplaced_canister(canister: int, canister_location_info: dict, system_id: int, device_id: int,
                                          canister_removed: bool) -> bool:
    """
    Method to add misplaced canister data in guided misplaced canister table if below condition is satisfy
    1. Guided to replenish flow is running for batch
    2. check canister not in guided tracker table
    3. canister in reserved canister
    @param canister:
    @param canister_location_info:
    @param system_id:
    @param device_id:
    @param canister_removed:
    @return:
    """
    try:
        # current_location_id = canister_location_info['id']
        # current_device_id = canister_location_info['device_id']
        # current_device_drawer = canister_location_info['container_id']

        # 1. check if guided flow is already running or not
        logger.info("In add_data_in_guided_misplaced_canister: checking for pending guided canister cycle")
        pending_guided_cycles = check_pending_guided_canister_transfer(system_id=system_id)
        logger.info("In add_data_in_guided_misplaced_canister: Pending guided canister cycles - " +
                    str(pending_guided_cycles))

        # 3. check if canister is reserved
        reserved_canister = get_reserved_canister_list_for_ongoing_batch(canister_list=[canister])
        logger.info("In add_data_in_guided_misplaced_canister: reserved canister list: {}".format(reserved_canister))

        pending_cycle = None
        if pending_guided_cycles:
            for cycle in pending_guided_cycles:
                pending_cycle = cycle
                break
            # 2. check if canister is in guided tracker table or not
            canister_in_guided_tracker = fetch_guided_tracker_ids_by_canister_ids(canister_ids=[canister],
                                                                                  guided_tx_cycle_id=pending_cycle["id"])

            logger.info("In add_data_in_guided_misplaced_canister: if canister in guided_tracker table "
                        "then guided_tracker_id is: {}".format(canister_in_guided_tracker))

            # get canister destination location from pack_analysis_details
            canister_analysis_data = get_destination_location_for_canister(batch_id=pending_cycle["batch_id"],
                                                                           canister_id=canister)

            # if canister is not in guided tracker, but it is in reserved canister and guided is already running
            # then add canister data in table
            if not canister_in_guided_tracker and canister in reserved_canister and canister_analysis_data['quadrant'] \
                    and canister_analysis_data['device_id']:

                # if canister is placed in robot
                if not canister_removed:
                    # if canister is placed in same location as it's destination location in pack_analysis_details
                    # then -> if canister is in guidedmisplacedcanister table then delete it and update couchdb
                    if canister_location_info['device_to_update'] == canister_analysis_data['device_id'] and \
                            canister_location_info['quadrant_to_update'] == canister_analysis_data['quadrant'] and \
                            not (canister_location_info["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and
                                 canister_location_info["drawer_type"] == settings.SIZE_OR_TYPE["SMALL"]):

                        # check if canister data already present in table for given meta_id and
                        # device_id delete canister from table
                        status = GuidedMisplacedCanister.check_if_canister_data_exit(canister_id=canister,
                                                                                     device_id=canister_analysis_data[
                                                                                         'device_id'],
                                                                                     guided_meta_id=pending_cycle["id"])
                        logger.info("In add_data_in_guided_misplaced_canister: canister: {} is present : {} for "
                                    "guided_meta_id: {} and device_id: {}".format(canister, status,
                                                                                  pending_cycle["id"],
                                                                                  canister_analysis_data['device_id']))

                        if status:
                            status = GuidedMisplacedCanister.db_delete_canister_data(canister_id=canister,
                                                                                     device_id=device_id,
                                                                                     guided_meta_id=pending_cycle["id"])
                            logger.info("In add_data_in_guided_misplaced_canister: canister_id: {} is deleted "
                                        "from guided_misplaced_canister table:{}".format(canister, status))

                            couch_db_update = guided_transfer_couch_db_timestamp_update(system_id, device_id)
                            logger.info("In add_data_in_guided_misplaced_canister: couch_db_update {}"
                                        .format(couch_db_update))

                    else:
                        # check if canister data already present in table for given meta_id and device_id
                        # then only update couchdb for device
                        status = GuidedMisplacedCanister.check_if_canister_data_exit(canister_id=canister,
                                                                                     device_id=canister_analysis_data[
                                                                                         'device_id'],
                                                                                     guided_meta_id=pending_cycle["id"])
                        logger.info("In add_data_in_guided_misplaced_canister: canister: {} is present for "
                                    "guided_meta_id: {} and device_id: {}".format(canister, pending_cycle["id"],
                                                                                  canister_analysis_data['device_id']))
                        misplaced_canister_data = [{"canister_id": canister,
                                                    "device_id": canister_analysis_data['device_id'],
                                                    "guided_meta_id": pending_cycle["id"],
                                                    "guided_status": pending_cycle["status"]}]

                        # if canister is not present in table then insert record in table
                        if not status:
                            status = GuidedMisplacedCanister.db_insert_canister_data(misplaced_canister_data=misplaced_canister_data)
                            logger.info("In add_data_in_guided_misplaced_canister: misplaced canister data: {} "
                                        "inserted in table:{}".format(misplaced_canister_data, status))

                        # update couch db according to current wizard
                        couch_db_update = guided_transfer_couch_db_timestamp_update(system_id, device_id)
                        logger.info("In add_data_in_guided_misplaced_canister: couch_db_update {}"
                                    .format(couch_db_update))

                # when canister is removed from robot
                else:
                    # check if canister data already present in table for given meta_id and device_id
                    # then only update couchdb for device
                    status = GuidedMisplacedCanister.check_if_canister_data_exit(canister_id=canister,
                                                                                 device_id=canister_analysis_data['device_id'],
                                                                                 guided_meta_id=pending_cycle["id"])
                    logger.info("In add_data_in_guided_misplaced_canister: canister: {} is present: {} for "
                                "guided_meta_id: {} and device_id: {}".format(canister, status, pending_cycle["id"],
                                                                              canister_analysis_data['device_id']))
                    misplaced_canister_data = [{"canister_id": canister,
                                                "device_id": canister_analysis_data['device_id'],
                                                "guided_meta_id": pending_cycle["id"],
                                                "guided_status": pending_cycle["status"]}]

                    # if canister is not present in table then insert record in table
                    if not status:
                        status = GuidedMisplacedCanister.db_insert_canister_data(misplaced_canister_data=misplaced_canister_data)
                        logger.info("In add_data_in_guided_misplaced_canister: misplaced canister data: {} "
                                    "inserted in table:{}".format(misplaced_canister_data, status))

                    # update couch db according to current wizard
                    couch_db_update = guided_transfer_couch_db_timestamp_update(system_id, device_id)
                    logger.info("In add_data_in_guided_misplaced_canister: couch_db_update {} for "
                                "device_id: {}".format(couch_db_update, device_id))

        return True

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_delete_canister_data_dao {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_data_in_guided_misplaced_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in insert_requested_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_data_in_guided_misplaced_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_destination_location_for_canister(batch_id: int, canister_id: int) -> dict:
    """
    function to get destination location for canister from pack analysis and pack_analysis_details
    @param batch_id:
    @param canister_id:
    @return:
    """
    try:
        # query to get destination location from pack_analysis and pack_analysis_details table
        query = PackAnalysis.select(PackAnalysisDetails.canister_id,
                                    PackAnalysisDetails.device_id, PackAnalysisDetails.quadrant).dicts() \
            .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
            .where(PackAnalysis.batch_id == batch_id, PackAnalysisDetails.canister_id == canister_id) \
            .group_by(PackAnalysisDetails.canister_id)

        for record in query:
            return record

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_delete_canister_data_dao {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_destination_location_for_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_destination_location_for_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_destination_location_for_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_guided_misplaced_canister_data(company_id: int, device_id: int, guided_meta_id: int) -> tuple:
    """
    function to get guided misplaced canister data
    @param company_id:
    @param device_id:
    @param guided_meta_id:
    @param batch_id:
    @return:
    """
    try:
        misplaced_canister_list: list = list()
        quad_type_dict: dict = dict()
        # misplace_canister_drawers_to_unlock: dict = dict()
        pack_ids = []
        logger.info(f"In get_guided_misplaced_canister_data, fetch pack_ids from meta id")
        pack_ids_query = GuidedMeta.select(GuidedMeta.pack_ids).dicts() \
                    .where(GuidedMeta.id == guided_meta_id)

        for data in pack_ids_query:
            pack_ids = list(map(int, (data["pack_ids"]).split(",")))
        logger.info(f"In get_guided_misplaced_canister_data, pack ids fetched")

        query = GuidedMisplacedCanister.select(GuidedMisplacedCanister.canister_id,
                                               CanisterMaster.canister_type,
                                               CanisterMaster.active,
                                               DrugMaster.id.alias('drug_id'),
                                               DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                               DrugMaster.imprint,
                                               DrugMaster.image_name,
                                               DrugMaster.color,
                                               DrugMaster.shape,
                                               DeviceMaster.name.alias('current_device_name'),
                                               DeviceMaster.device_type_id.alias('source_device_type_id'),
                                               LocationMaster.id.alias('source_canister_location'),
                                               LocationMaster.container_id.alias('source_container'),
                                               LocationMaster.display_location.alias('source_display_location'),
                                               LocationMaster.device_id.alias('source_can_device'),
                                               ContainerMaster.id.alias("container_id"),
                                               ContainerMaster.serial_number,
                                               ContainerMaster.secondary_ip_address,
                                               ContainerMaster.secondary_mac_address,
                                               ContainerMaster.ip_address,
                                               ContainerMaster.mac_address,
                                               ContainerMaster.drawer_name.alias('source_drawer_name'),
                                               DeviceMaster.device_type_id.alias('source_device_type_id'),
                                               PackAnalysisDetails.quadrant.alias('destination_quadrant'),
                                               PackAnalysisDetails.device_id.alias('destination_device_id'),
                                               fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                                     DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                               DrugDetails.last_seen_by,
                                               DrugDetails.last_seen_date,
                                               ).dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == GuidedMisplacedCanister.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.canister_id == GuidedMisplacedCanister.canister_id) \
            .join(PackAnalysis, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                                   fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                                  (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == settings.is_drug_active) &
                                                         (DrugStockHistory.company_id == company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == company_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .where(GuidedMisplacedCanister.device_id == device_id,
                   CanisterMaster.company_id == company_id,
                   GuidedMisplacedCanister.guided_meta_id == guided_meta_id, PackAnalysis.pack_id << pack_ids) \
            .group_by(GuidedMisplacedCanister.canister_id)

        for record in query:
            if record['destination_quadrant'] not in quad_type_dict.keys():
                canister_type_dict = {"small_canister_count": 0, "big_canister_count": 0}
                quad_type_dict[record['destination_quadrant']] = canister_type_dict

            if record['canister_type'] == settings.SIZE_OR_TYPE['BIG']:
                quad_type_dict[record['destination_quadrant']]["big_canister_count"] += 1
            else:
                quad_type_dict[record['destination_quadrant']]["small_canister_count"] += 1
            misplaced_canister_list.append(record)

        return misplaced_canister_list, quad_type_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_delete_canister_data_dao {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_guided_misplaced_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_guided_misplaced_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_guided_misplaced_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_container_data_from_display_location(unlock_display_location: int):
    """
    get container data(drawer_data) from display location
    :return: bool
    """
    try:
        query = LocationMaster.select(LocationMaster, ContainerMaster).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id).where(
            LocationMaster.display_location == unlock_display_location).get()

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_delete_canister_data_dao {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_container_data_from_display_location: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_container_data_from_display_location {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_container_data_from_display_location: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def guided_transfer_couch_db_timestamp_update(system_id,
                                              device_id):
    """
    Function to update couch db when transfer to CSR to transfer from CSR is performed
    @param system_id: int
    @param device_id: int
    """

    logger.info("guided_transfer_decrement_count_couch_db Input {}".format(system_id, device_id))

    try:
        database_name = get_couch_db_database_name(system_id=system_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        id = 'guided_canister_transfer_{}'.format(device_id)
        table = cdb.get(_id=id)

        logger.info("previous table in guided_transfer_couch_db_timestamp_update {}".format(table))
        if table is not None:
            if 'data' not in table:
                table["data"] = {}
            table['data']['timestamp'] = get_current_date_time()

        logger.info("updated table in guided_transfer_couch_db_timestamp_update {}".format(table))
        cdb.save(table)
        return True

    except couchdb.http.ResourceConflict:
        logger.error("EXCEPTION: Document update conflict.")
        return error(1000, "Document update conflict.")

    except RealTimeDBException as e:
        return error(1000, str(e))

    except Exception as e:
        logger.error("error in guided_transfer_couch_db_timestamp_update {}".format(e))
        raise Exception('Couch db update failed while transferring canisters')


@log_args_and_response
def get_reserved_canister_list_for_ongoing_batch(canister_list: list):
    """
        Returns canisters that are reserved for any batch from given canister list
        :param canister_list:
        :return:
    """
    canister_data = list()
    try:

        query = ReservedCanister.select(ReservedCanister.canister_id).dicts() \
            .join(BatchMaster, on=ReservedCanister.batch_id == BatchMaster.id) \
            .where(ReservedCanister.canister_id << canister_list,
                   BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST))

        for record in query:
            canister_data.append(record['canister_id'])

        logger.info(
            'In db_get_reserved_canister_list_for_ongoing_batch: reserved_canister_found: ' + str(canister_data))
        return canister_data

    except DoesNotExist as e:
        logger.error("error in get_reserved_canister_list_for_ongoing_batch {}".format(e))
        return None

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_reserved_canister_list_for_ongoing_batch {}".format(e))
        raise


@log_args_and_response
def get_location_details_by_canister_id(canister_id):
    try:
        for record in CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                            LocationMaster.id,
                                            LocationMaster.device_id,
                                            LocationMaster.quadrant,
                                            LocationMaster.location_number) \
                .dicts() \
                .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
                .where(CanisterMaster.id == canister_id):
            return record

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_location_details_by_canister_id {}".format(e))
        raise
    except DoesNotExist as e:
        logger.error("error in get_location_details_by_canister_id {}".format(e))
        return None


@log_args_and_response
def db_get_drawer_wise_empty_locations_data(device_id, quadrant):
    """
    Returns empty locations for given device id and quadrant
    @param device_id: int
    @param quadrant: int
    @return: dict
    """

    locations = get_display_locations_from_device_and_quadrant(device_id=device_id,
                                                               quadrant=quadrant)
    non_empty_or_disabled_locations = dict()

    if device_id:
        for record in LocationMaster.select(LocationMaster.device_id,
                                            LocationMaster.id,
                                            LocationMaster.container_id,
                                            LocationMaster.display_location,
                                            ContainerMaster.drawer_name,
                                            ContainerMaster.drawer_type,
                                            LocationMaster.location_number,
                                            ContainerMaster.serial_number,
                                            ContainerMaster.ip_address,
                                            ContainerMaster.secondary_ip_address).dicts() \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                .where((CanisterMaster.id.is_null(False) |
                        LocationMaster.is_disabled == True),
                       LocationMaster.device_id == device_id,
                       LocationMaster.quadrant == quadrant) \
                .order_by(LocationMaster.id):

            if record['drawer_type'] not in non_empty_or_disabled_locations.keys():
                non_empty_or_disabled_locations[record['drawer_type']] = dict()

            if record['drawer_name'] not in non_empty_or_disabled_locations[record['drawer_type']].keys():
                non_empty_or_disabled_locations[record['drawer_type']][record['drawer_name']] = list()
            non_empty_or_disabled_locations[record['drawer_type']][record['drawer_name']].append(
                record['display_location'])

        # remove non-empty and disabled locations from total locations
        for drawer_type, non_empty_loc in non_empty_or_disabled_locations.items():
            for container, container_locations in non_empty_loc.items():
                for loc in container_locations:
                    if drawer_type in locations and container in locations[drawer_type] and \
                            "empty_locations" in locations[drawer_type][container] and \
                            loc in locations[drawer_type][container]["empty_locations"]:
                        locations[drawer_type][container]["empty_locations"].remove(loc)

    return locations


def get_display_locations_from_device_and_quadrant(device_id, quadrant):
    drawer_wise_locations = {}
    try:
        query = LocationMaster.select(LocationMaster.id, LocationMaster.display_location,
                                      LocationMaster.location_number, LocationMaster.container_id,
                                      ContainerMaster.drawer_name, ContainerMaster.drawer_type,
                                      ContainerMaster.serial_number,
                                      ContainerMaster.ip_address, ContainerMaster.secondary_ip_address,
                                      ContainerMaster.shelf,
                                      DeviceMaster.device_type_id.alias('device_type_id'),
                                      DeviceMaster.ip_address.alias('device_ip_address')) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=LocationMaster.device_id == DeviceMaster.id) \
            .where(LocationMaster.device_id == device_id, LocationMaster.quadrant == quadrant) \
            .order_by(LocationMaster.id)
        for record in query.dicts():
            if record['drawer_type'] not in drawer_wise_locations.keys():
                drawer_wise_locations[record['drawer_type']] = dict()
            if record['drawer_name'] not in drawer_wise_locations[record['drawer_type']].keys():
                drawer_wise_locations[record['drawer_type']][record['drawer_name']] = {
                    'id': record["container_id"],
                    'drawer_name': record["drawer_name"],
                    'serial_number': record["serial_number"],
                    'ip_address': record['ip_address'],
                    'device_ip_address': record['device_ip_address'],
                    'secondary_ip_address': record['secondary_ip_address'],
                    'shelf': record['shelf'],
                    'empty_locations': list(),
                    'device_type_id': record['device_type_id'],
                }
            drawer_wise_locations[record['drawer_type']][record['drawer_name']]["empty_locations"].append(
                record['display_location'])
        return drawer_wise_locations
    except DoesNotExist as e:
        logger.error("error in get_display_locations_from_device_and_quadrant {}".format(e))
        raise NoLocationExists


@log_args_and_response
def check_if_canister_data_exit_dao(canister_id: int, device_id: int, guided_meta_id: int):
    """
    function to check if canister data exist in misplaced canister or not
    :return: bool
    """
    try:
        status = GuidedMisplacedCanister.check_if_canister_data_exit(canister_id=canister_id,
                                                                     device_id=device_id,
                                                                     guided_meta_id=guided_meta_id)

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_if_canister_data_exit_dao {}".format(e))
        raise e


@log_args_and_response
def db_delete_canister_data_dao(canister_id: int, device_id: int, guided_meta_id: int):
    """
    function to check if canister data exist in misplaced canister or not
    :return: bool
    """
    try:
        status = GuidedMisplacedCanister.db_delete_canister_data(canister_id=canister_id,
                                                                 device_id=device_id,
                                                                 guided_meta_id=guided_meta_id)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_delete_canister_data_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_replenish_query(system_id, device_ids, mini_batch_wise=False,
                           exclude_canisters=None, replenish_canisters=None, ordered_packs=False):
    """
    Method to fetch replenish data of canisters
    @param replenish_canisters:
    @param replenish_canisters:
    @param ordered_packs:
    @param batch_id:
    @param system_id:
    @param device_ids:
    @param mini_batch_wise: True - when need to consider replenish for mini batch only else False
    @param exclude_canisters : list of canisters that we don't want to consider for replenish
    @return:
    """
    try:
        # adding packs which are in progress but yet not processed by robot.
        progress_pack_ids = db_get_progress_filling_left_pack_ids()
        pack_clause = list()
        if progress_pack_ids:
            pack_clause.append((PackDetails.pack_status == settings.PENDING_PACK_STATUS) |
                               (PackDetails.id << progress_pack_ids))
        else:
            pack_clause.append(PackDetails.pack_status == settings.PENDING_PACK_STATUS)

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
                                             DrugMaster.formatted_ndc,
                                             DrugMaster.txr,
                                             DrugDimension.approx_volume,
                                             UniqueDrug.is_delicate
                                             ).dicts() \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
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
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(pack_clause,
                   PackDetails.system_id == system_id,
                   PackAnalysisDetails.device_id << device_ids,
                   DeviceMaster.device_type_id << [settings.DEVICE_TYPES['ROBOT']],
                   PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)
        if replenish_canisters:
            replenish_query = replenish_query.where(PackAnalysisDetails.canister_id << replenish_canisters)
        if exclude_canisters:
            replenish_query = replenish_query.where(PackAnalysisDetails.canister_id.not_in(exclude_canisters))
        replenish_query = replenish_query.group_by(PackAnalysisDetails.canister_id).order_by(PackDetails.order_no)
        if mini_batch_wise:
            replenish_query = replenish_query.having(fn.SUM(fn.FLOOR(SlotDetails.quantity)) >
                                                     CanisterMaster.available_quantity)
        if ordered_packs:
            replenish_query = replenish_query.order_by(PackAnalysisDetails.device_id, PackAnalysisDetails.quadrant)

        return replenish_query
    except (InternalError, IntegrityError) as e:
        logger.error("error in db_get_replenish_query {}".format(e))
        raise e


@log_args_and_response
def get_ordered_packs_of_batch(system_id: int, device_ids: list) -> list:
    try:
        pack_order_query = PackDetails.select().dicts() \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
                                    (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
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
        raise e


@log_args_and_response
def db_get_guided_transfer_to_dd_details(guided_meta_id: int) -> list:
    try:
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        CanisterMasterAlias = CanisterMaster.alias()
        guided_transfer_to_dd_query = GuidedTracker.select(DeviceMasterAlias.id.alias("device_id"),
                                                           DeviceMaster.serial_number.alias("trolley_serial_number"),
                                                           ContainerMaster.serial_number.alias("drawer_serial_number"),
                                                           CanisterMaster.id.alias("source_canister_id"),
                                                           CanisterMaster.rfid.alias("source_canister_rfid"),
                                                           CanisterMasterAlias.id.alias("alternate_canister_id"),
                                                           CanisterMasterAlias.rfid.alias("alternate_canister_rfid"),
                                                           DeviceMaster.device_type_id.alias("source_device_type_id"),
                                                           DeviceMaster.id.alias("source_device_id"),
                                                           LocationMaster.container_id.alias("source_drawer_id"),
                                                           DeviceMasterAlias.system_id.alias("dest_system_id"),
                                                           DeviceMasterAlias.device_type_id.alias(
                                                               "dest_device_type_id"),
                                                           DeviceMasterAlias.id.alias("dest_device_id"),
                                                           LocationMasterAlias.container_id.alias("dest_drawer_id"),
                                                           LocationMasterAlias.display_location.alias("dest_display_location")
                                                           ).dicts() \
            .join(LocationMaster, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == GuidedTracker.destination_location_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == LocationMasterAlias.device_id) \
            .join(CanisterMaster, on=CanisterMaster.id == GuidedTracker.source_canister_id) \
            .join(CanisterMasterAlias, on=CanisterMasterAlias.id == GuidedTracker.alternate_canister_id) \
            .where(GuidedTracker.guided_meta_id == guided_meta_id,
                   DeviceMasterAlias.id << (2,3))

        guided_transfer_details_list = list()

        for record in guided_transfer_to_dd_query.dicts():
            guided_transfer_details_list.append(record)

        return guided_transfer_details_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_guided_transfer_to_dd_details {}".format(e))
        raise
    except Exception as e:
        logger.error("error in db_get_guided_transfer_to_dd_details {}".format(e))
        raise e


@log_args_and_response
def db_get_guided_transfer_to_csr_details(guided_meta_id: int) -> list:
    try:
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        CanisterMasterAlias = CanisterMaster.alias()
        guided_transfer_to_dd_query = GuidedTracker.select(DeviceMasterAlias.id.alias("device_id"),
                                                           DeviceMaster.serial_number.alias("trolley_serial_number"),
                                                           ContainerMaster.serial_number.alias("drawer_serial_number"),
                                                           CanisterMaster.id.alias("source_canister_id"),
                                                           CanisterMaster.rfid.alias("source_canister_rfid"),
                                                           CanisterMasterAlias.id.alias("alternate_canister_id"),
                                                           CanisterMasterAlias.rfid.alias("alternate_canister_rfid"),
                                                           DeviceMaster.device_type_id.alias("source_device_type_id"),
                                                           DeviceMaster.id.alias("source_device_id"),
                                                           LocationMaster.container_id.alias("source_drawer_id"),
                                                           DeviceMasterAlias.system_id.alias("dest_system_id"),
                                                           DeviceMasterAlias.device_type_id.alias(
                                                               "dest_device_type_id"),
                                                           DeviceMasterAlias.id.alias("dest_device_id"),
                                                           LocationMasterAlias.container_id.alias("dest_drawer_id"),
                                                           LocationMasterAlias.display_location.alias("dest_display_location")
                                                           ).dicts() \
            .join(LocationMaster, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == GuidedTracker.destination_location_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == LocationMasterAlias.device_id) \
            .join(CanisterMaster, on=CanisterMaster.id == GuidedTracker.source_canister_id) \
            .join(CanisterMasterAlias, on=CanisterMasterAlias.id == GuidedTracker.alternate_canister_id) \
            .where(GuidedTracker.guided_meta_id == guided_meta_id,
                   DeviceMasterAlias.id == 1)

        guided_transfer_details_list = list()

        for record in guided_transfer_to_dd_query.dicts():
            guided_transfer_details_list.append(record)

        return guided_transfer_details_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_guided_transfer_to_csr_details {}".format(e))
        raise
    except Exception as e:
        logger.error("error in db_get_guided_transfer_to_csr_details {}".format(e))
        raise e


@log_args_and_response
def db_get_guided_transfer_to_cart_details(guided_meta_id: int) -> list:
    try:
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        guided_transfer_to_dd_query = GuidedTracker.select(DeviceMasterAlias.id.alias("device_id"),
                                                           DeviceMaster.serial_number.alias("trolley_serial_number"),
                                                           ContainerMaster.serial_number.alias("drawer_serial_number"),
                                                           CanisterMaster.id.alias("source_canister_id"),
                                                           ).dicts() \
            .join(CanisterMaster,
                  on=fn.IF(GuidedTracker.alternate_canister_id.is_null(False), GuidedTracker.alternate_canister_id,
                           GuidedTracker.source_canister_id) == CanisterMaster.id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == CanisterMaster.location_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == LocationMasterAlias.device_id) \
            .join(LocationMaster, on=LocationMaster.id == GuidedTracker.cart_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .where(GuidedTracker.guided_meta_id == guided_meta_id)

        guided_transfer_details_list = list()

        for record in guided_transfer_to_dd_query.dicts():
            guided_transfer_details_list.append(record)

        return guided_transfer_details_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_guided_transfer_to_cart_details {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_guided_transfer_to_cart_details {}".format(e))
        raise e

    