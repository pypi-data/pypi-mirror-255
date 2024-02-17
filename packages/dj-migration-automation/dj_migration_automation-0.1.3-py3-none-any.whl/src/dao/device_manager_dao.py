import functools
import operator
import os
import sys
from typing import List, Dict

import yaml
from peewee import *
from peewee import IntegrityError, InternalError, DataError, JOIN_LEFT_OUTER, DoesNotExist, fn

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, log_args
from src.model.model_code_master import CodeMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src import constants
from src.exceptions import NoLocationExists
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_code_master import CodeMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_disabled_location_history import DisabledLocationHistory
from src.model.model_drug_master import DrugMaster
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_mfd_canister_master import MfdCanisterMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_slot_details import SlotDetails
from src.model.model_system_setting import SystemSetting
from src.model.model_unit_conversion import UnitConversion
from src.model.model_unit_master import UnitMaster
from src.model.model_zone_master import ZoneMaster
from src.model.model_replenish_skipped_canister import ReplenishSkippedCanister

logger = settings.logger


@log_args_and_response
def get_csr_drawer_data_to_hit_webservice(company_id, device_id_list=None, drawer_number_list=None):
    """
    used in zone.py
    """
    db_result = list()
    clauses = list()
    clauses.append((DeviceMaster.company_id == company_id))
    if device_id_list:
        clauses.append((ContainerMaster.device_id << device_id_list))

    if drawer_number_list:
        clauses.append((ContainerMaster.drawer_name << drawer_number_list))
    try:
        query = ContainerMaster.select(ContainerMaster.ip_address,
                                       ContainerMaster.secondary_ip_address,
                                       ContainerMaster.id).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .where(functools.reduce(operator.and_, clauses))

        for csr_data in query:
            db_result.append(csr_data)

        return db_result
    except IntegrityError as e:
        logger.error("error in get_csr_drawer_data_to_hit_webservice {}".format(e))
        raise e
    except InternalError as e:
        logger.error("error in get_csr_drawer_data_to_hit_webservice {}".format(e))
        raise e


@log_args_and_response
def db_get_system_zone_mapping(system_list):
    try:

        system_zone_mapping = {}
        zone_list = set()
        query = DeviceMaster.select(ZoneMaster.id, DeviceMaster.system_id) \
            .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(ZoneMaster, on=ZoneMaster.id == DeviceLayoutDetails.zone_id) \
            .where(DeviceMaster.system_id << system_list)

        for record in query.dicts():
            system_zone_mapping[record['system_id']] = record['id']
            zone_list.add(record['id'])
        zone_list = list(zone_list)
        return system_zone_mapping, zone_list
    except (InternalError, IntegrityError) as e:
        logger.error("error in db_get_system_zone_mapping {}".format(e))
        return error(2001)


@log_args_and_response
def db_get_disabled_locations(device_ids=None, company_id=None, drawer_numbers=None, drawer_types=None):
    """
    Returns disabled locations for given device ids and drawer numbers

    @param drawer_types:
    @param drawer_numbers:
    @param company_id:
    @param device_ids:
    """
    # if device_ids and company_id:
    #     valid_devices = DeviceMaster.db_verify_devicelist(device_ids, company_id)
    #     if not valid_devices:
    #         raise ValueError('Invalid device_id or company_id')

    if drawer_types is None:
        drawer_types = [settings.SIZE_OR_TYPE['BIG'], settings.SIZE_OR_TYPE['SMALL'], settings.SIZE_OR_TYPE['MFD']]
    try:
        query = LocationMaster.select(
            LocationMaster.location_number.alias('location'),
            DeviceMaster.name.alias('device_name'),
            DeviceMaster.id.alias('device_id'),
            LocationMaster.display_location,
            ContainerMaster.drawer_name.alias('drawer_number'),
            DisabledLocationHistory.id,
            DisabledLocationHistory.comment,
            LocationMaster.location_number,
            DeviceLayoutDetails.zone_id,
            ZoneMaster.name.alias('zone_name'),
            DeviceMaster.system_id,
        ).dicts().join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, on=ZoneMaster.id == DeviceLayoutDetails.zone_id) \
            .join(DisabledLocationHistory, JOIN_LEFT_OUTER, on=((LocationMaster.id == DisabledLocationHistory.loc_id) &
                                                                (DisabledLocationHistory.end_time.is_null(True)))) \
            .where((LocationMaster.is_disabled == 1))
        if device_ids:
            query = query.where(DeviceMaster.id << device_ids, ContainerMaster.drawer_type << drawer_types)
        elif company_id:
            query = query.where(DeviceMaster.company_id == company_id,
                                ContainerMaster.drawer_type << drawer_types)
        if drawer_numbers:
            query = query.where(ContainerMaster.drawer_name << drawer_numbers)

        query = query.order_by(DeviceMaster.id, LocationMaster.location_number)
        return list(query)

    except (IntegrityError, InternalError) as e:
        logger.error("Error in db_get_disabled_locations".format(e))
        raise


@log_args_and_response
def get_previous_used_mfd_trolley(system_id: int, current_batch: int) -> list:
    """
    Function to get trolley list used in previous batch
    @param system_id:
    @param current_batch:
    @return:
    """
    cart_list = list()
    try:
        query = MfdAnalysis.select(fn.GROUP_CONCAT(fn.DISTINCT(LocationMaster.device_id)).coerce(
            False).alias("cart_id")).dicts() \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .where(MfdAnalysis.batch_id.not_in([current_batch]),
                   BatchMaster.system_id == system_id,
                   BatchMaster.status << [settings.BATCH_PROCESSING_COMPLETE],
                   MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_MVS_FILLING_REQUIRED])) \
            .group_by(BatchMaster.id) \
            .order_by(BatchMaster.id.desc()).limit(1)

        for record in query:
            cart_list = [int(i) for i in list(record["cart_id"].split(","))]

        return cart_list

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_previous_used_mfd_trolley".format(e))
        raise

    except DoesNotExist as e:
        logger.error("Error in get_previous_used_mfd_trolley".format(e))
        return cart_list


@log_args_and_response
def get_currently_used_trolley(company_id, system_id):
    """
    Function to get currently used MFD trolley list
    @param company_id: int
    @param system_id: int
    @return: list
    """
    cart_list = list()
    try:

        LocationMasterAlias = LocationMaster.alias()
        # batch_status = [settings.BATCH_IMPORTED,
        #                 settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
        #                 settings.BATCH_ALTERNATE_DRUG_SAVED,
        #                 settings.BATCH_MFD_USER_ASSIGNED,
        #                 settings.BATCH_CANISTER_TRANSFER_DONE]

        mfd_canister_status = [constants.MFD_CANISTER_FILLED_STATUS,
                               constants.MFD_CANISTER_PENDING_STATUS,
                               constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                               constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                               constants.MFD_CANISTER_VERIFIED_STATUS]

        mfd_canister_transfer_pending_status = [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                constants.MFD_CANISTER_DROPPED_STATUS]

        query = MfdAnalysis.select(LocationMaster.device_id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .where(BatchMaster.system_id == system_id,
                   PackDetails.company_id == company_id,
                   ((MfdCanisterMaster.id.is_null(True)) |
                    (MfdCanisterMaster.state_status << [constants.MFD_CANISTER_ACTIVE,
                                                        constants.MFD_CANISTER_MISPLACED])),
                   ((MfdAnalysis.status_id << mfd_canister_status) |
                    ((MfdAnalysis.status_id << mfd_canister_transfer_pending_status) &
                     (DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT'])))) \
            .group_by(LocationMaster.device_id)

        for record in query.dicts():
            if record['device_id']:
                cart_list.append(record['device_id'])

        logger.info('currently_used_trolley_ids: {}'.format(cart_list))
        return cart_list

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_currently_used_trolley".format(e))
        raise

    except DoesNotExist as e:
        logger.error("Error in get_currently_used_trolley".format(e))
        return cart_list


@log_args_and_response
def get_available_device_list_of_a_type(device_type_ids, currently_used_trolley, company_id, system_id):
    """
    Function to get mfd trolley by system id
    @param currently_used_trolley:
    @param device_type_ids: list
    @param company_id: int
    @param system_id: int
    @return: list
    """
    db_result = list()
    try:
        clauses = [DeviceMaster.company_id == company_id,
                   DeviceMaster.device_type_id << device_type_ids,
                   DeviceMaster.system_id == system_id,
                   DeviceMaster.active == settings.is_device_active]

        if len(currently_used_trolley):
            clauses.append(DeviceMaster.id.not_in(currently_used_trolley))

        query = DeviceMaster.select(DeviceMaster.id).dicts() \
            .where(*clauses)

        for device in query:
            db_result.append(device['id'])
        return db_result

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_available_device_list_of_a_type".format(e))
        raise InternalError
    except DoesNotExist as e:
        logger.error("Error in get_available_device_list_of_a_type".format(e))
        return db_result


def db_get_device_name(device_id_list):
    device_name_dict = dict()

    try:
        for record in DeviceMaster.select(DeviceMaster.id, DeviceMaster.name) \
                .where(DeviceMaster.id << device_id_list):
            device_name_dict[record['id']] = record['name']
    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise

    except DoesNotExist as e:
        logger.error(e)
        return device_name_dict


def get_location_data_from_device_ids(device_id_list, drawer_level_list=None):
    location_info = dict()
    drawer_location_info = dict()
    try:
        if device_id_list:
            query = LocationMaster.select(LocationMaster.id.alias('device_location_id'),
                                          LocationMaster.container_id.alias('drawer_id'),
                                          LocationMaster, DeviceMaster.id.alias('device_id'),
                                          DeviceMaster, ContainerMaster) \
                .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .where(LocationMaster.device_id << device_id_list) \
                .order_by(DeviceMaster.id, LocationMaster.container_id, LocationMaster.id)

            if drawer_level_list:
                query = query.where(ContainerMaster.drawer_level << drawer_level_list)

            for record in query.dicts():
                if record['device_type_id'] not in location_info.keys():
                    location_info[record['device_type_id']] = dict()
                    # if record['container_id'] not in location_info[record['device_type_id']].keys():
                    #     location_info[record['device_type_id']][record['container_id']] = list()
                    # location_info[record['device_type_id']][record['container_id']].append(
                if record['device_id'] not in drawer_location_info.keys():
                    drawer_location_info[record['device_id']] = dict()

                if record['drawer_id'] not in drawer_location_info[record['device_id']].keys():
                    drawer_location_info[record['device_id']][record['drawer_id']] = list()
                drawer_location_info[record['device_id']][record['drawer_id']].append(record['device_location_id'])

                if record['drawer_id'] not in location_info[record['device_type_id']].keys():
                    location_info[record['device_type_id']][record['drawer_id']] = list()
                location_info[record['device_type_id']][record['drawer_id']].append(
                    (record['device_location_id'], record['location_number'], record['quadrant'],
                     record['display_location']))
        return location_info, drawer_location_info
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_location_data_from_device_ids".format(e))
        raise e
    except DoesNotExist as e:
        logger.info("IN get_location_data_from_device_ids: no location found: {}".format(e))
        raise NoLocationExists


@log_args_and_response
def get_max_locations_of_a_container(container_id):
    try:
        max_locations = ContainerMaster.select(fn.COUNT(LocationMaster.id).alias('max_locations')).dicts() \
            .join(LocationMaster, on=LocationMaster.container_id == ContainerMaster.id) \
            .where(ContainerMaster.id == container_id).get()
        return max_locations["max_locations"]

    except (DoesNotExist, IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_max_locations_of_a_container".format(e))
        raise e


@log_args_and_response
def get_robot_data_dao(company_id):
    try:
        robot_data = DeviceMaster.get_all_devices_of_a_type([settings.DEVICE_TYPES['ROBOT']], company_id)
        return robot_data
    except(IntegrityError, InternalError) as e:
        logger.error("Error in get_robot_data_dao".format(e))
        raise


@log_args_and_response
def get_robots_by_systems_dao(system_id_list):
    try:
        robot_data = DeviceMaster.db_get_robots_by_systems(system_id_list)
        return robot_data
    except(IntegrityError, InternalError) as e:
        logger.error("Error in get_robot_data_dao".format(e))
        raise


@log_args_and_response
def verify_device_id_dao(device_id, system_id):
    try:
        valid_device = DeviceMaster.db_verify_device_id(device_id, system_id)
        return valid_device
    except(IntegrityError, InternalError, Exception) as e:
        logger.error("Error in verify_device_id_dao".format(e))
        raise


@log_args_and_response
def get_robot_dao(system_id=None, device_id=None, serial_number=None):
    try:
        robot_data = DeviceMaster.db_get(system_id, device_id=device_id, serial_number=serial_number)
        return robot_data
    except(IntegrityError, InternalError) as e:
        logger.error("Error in get_robot_dao".format(e))
        raise


@log_args_and_response
def get_device_name_from_device(device_id_list: list):
    try:
        robot_data = DeviceMaster.db_get_device_name_from_device(device_id_list=device_id_list)
        return robot_data
    except(IntegrityError, InternalError) as e:
        logger.error("Error in get_device_name_from_device".format(e))
        raise


@log_args_and_response
def get_robot_serial_dao(serial_number):
    try:
        robot_data = DeviceMaster.get(serial_number=serial_number)
        return robot_data
    except DoesNotExist as e:
        logger.error("Error in get_robot_serial_dao".format(e))
        raise


@log_args_and_response
def add_robot_dao(robot_info):
    try:
        record = BaseModel.db_create_record({
            "system_id": robot_info["system_id"],
            "company_id": robot_info["company_id"],
            "name": robot_info["name"],
            "device_type_id": robot_info["device_type_id"],
            "serial_number": robot_info["serial_number"],
            "version": robot_info["version"],
            "created_by": robot_info["user_id"],
            "created_date": get_current_date_time(),
            "modified_by": robot_info["user_id"],
            "modified_date": get_current_date_time()
        }, DeviceMaster, get_or_create=False)
        return record.id
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in add_robot_dao".format(e))
        raise


@log_args_and_response
def update_device_data_dao(robot_info, device_id):
    try:
        status = DeviceMaster.update_device_data(dict_robot_info=robot_info, device_id=device_id)
        return status
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in update_device_data_dao".format(e))
        raise


@log_args_and_response
def get_system_id_by_device_id_dao(device_id):
    try:
        system_id = DeviceMaster.db_get_system_id_by_device_id(device_id)
        return system_id
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_system_id_by_device_id_dao".format(e))
        raise


@log_args_and_response
def get_device_shelf_info(device_id):
    try:
        query = DeviceMaster.select(ContainerMaster.shelf).dicts() \
            .join(ContainerMaster, on=ContainerMaster.device_id == DeviceMaster.id) \
            .where(DeviceMaster.id == device_id)
        return list(query)
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_device_shelf_info".format(e))
        raise
    except DoesNotExist as e:
        logger.error("Error in get_device_shelf_info".format(e))
        return list()


@log_args_and_response
def get_device_data_by_device_id_dao(device_id: int):
    try:
        return DeviceMaster.db_get_by_id(device_id=device_id)
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_device_data_by_device_id_dao".format(e))
        raise
    except DoesNotExist as e:
        logger.info("IN get_device_data_by_device_id_dao: no location found: {}".format(e))
        raise DoesNotExist


@log_args_and_response
def get_active_robots_count_by_system_id_dao(system_id):
    try:
        active_robots = DeviceMaster.db_get_active_robots_count_by_system_id(system_id)
        return active_robots
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_active_robots_count_by_system_id_dao".format(e))
        raise


@log_args_and_response
def get_system_capacity_dao(system_id):
    try:
        system_capacity, default_system_capacity_per_robot = SystemSetting.db_get_system_capacity(system_id)
        return system_capacity, default_system_capacity_per_robot
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_system_capacity_dao".format(e))
        raise


@log_args_and_response
def update_system_capacity_dao(update_system_dict, system_id):
    try:
        system_status = SystemSetting.db_update_system_capacity(update_system_dict, system_id)
        return system_status
    except (IntegrityError, InternalError) as e:
        logger.error("Error in update_system_capacity_dao".format(e))
        raise


@log_args_and_response
def get_mfs_data_by_system_id(system_id):
    """
    returns valid mfs_id for a system
    :param system_id: int
    :return: int
    """
    # mfs_list = list()
    try:
        mfs_list = DeviceMaster.get_mfs_id_by_system_id(system_id)
        if not mfs_list:
            raise ValueError('No Manual Fill Stations found for given system.')
        if len(mfs_list) > 1:
            raise ValueError('Multiple Manual Fill Stations found for given system.')
        else:
            return mfs_list[0]
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_mfs_data_by_system_id".format(e))
        return error(2001)


@log_args_and_response
def get_mfs_systems(device_ids):
    """
    returns valid mfs_id for a system
    :param device_ids: list
    :return: int
    """
    try:
        mfs_system_dict, device_associated_device_dict = DeviceMaster.get_mfs_system_by_device(device_ids)
        return mfs_system_dict, device_associated_device_dict
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_mfs_systems".format(e))
        return error(2001)


@log_args_and_response
def get_mfs_device_data(serial_number):
    try:
        mfs_data = DeviceMaster.get(serial_number=serial_number)
        return mfs_data
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_mfs_device_data".format(e))
        return error(2001)


@log_args_and_response
def get_device_type_data_dao(data_dict):
    """
    To get distinct device types company wise
    @param data_dict: dict
    @return: query
    """
    try:
        company_id = data_dict['company_id']
        system_id = data_dict['system_id']

        clauses = [DeviceMaster.company_id == company_id]
        if system_id:
            clauses.append(DeviceMaster.system_id == system_id)

        query = DeviceMaster.select(DeviceTypeMaster).dicts() \
            .join(DeviceTypeMaster, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .where(*clauses) \
            .group_by(DeviceTypeMaster.id)

        return query

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_device_type_data_dao".format(e))
        raise


@log_args_and_response
def get_zone_wise_system_list(company_id: int, device_type: [list, None], system_id: [int, None]) -> list:
    """
    To get all system id's that are in same zone by given company and device type
    @param company_id:
    @param device_type:
    @param system_id:
    @return:
    """
    zone_ids = set()
    system_ids = list()
    try:
        clauses = [DeviceMaster.company_id == company_id,
                   DeviceMaster.active == settings.is_device_active]

        if system_id:
            clauses.append(DeviceMaster.system_id == system_id)

        # get zone_ids by given robot's system_id
        zone_data_query = DeviceLayoutDetails.select(
            fn.group_concat(fn.distinct(DeviceLayoutDetails.zone_id)).alias('zone_id')).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == DeviceLayoutDetails.device_id) \
            .where(*clauses) \
            .group_by(DeviceMaster.system_id)

        for record in zone_data_query:
            if record['zone_id']:
                zone_id_list = list(record['zone_id'].split(','))
                zone_ids.update(set(zone_id_list))

        if zone_ids:
            # get system_id's of devices that are in given zone list
            device_clauses = [DeviceLayoutDetails.zone_id << list(zone_ids),
                              DeviceMaster.company_id == company_id]
            if device_type:
                device_clauses.append(DeviceMaster.device_type_id << device_type)

            device_data_query = DeviceMaster.select(
                DeviceMaster.system_id).dicts() \
                .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .where(*device_clauses)

            for record in device_data_query:
                system_ids.append(record['system_id'])
            return system_ids

        else:
            return system_ids

    except (IntegrityError, InternalError, KeyError, Exception) as e:
        logger.error("Error in get_zone_wise_system_list".format(e))
        raise


@log_args_and_response
def get_zone_wise_device_list(company_id, device_type, system_id, system_device_type=None):
    zone_ids = list()
    try:

        clauses = [DeviceMaster.company_id == company_id,
                   DeviceMaster.active == settings.is_device_active]
        if system_id:
            clauses.append(DeviceMaster.system_id == system_id)
        if system_device_type:
            clauses.append(DeviceMaster.device_type_id << system_device_type)
        else:
            clauses.append(DeviceMaster.device_type_id << [settings.DEVICE_TYPES['ROBOT'],
                                                           settings.DEVICE_TYPES['CSR']])

        zone_data_query = DeviceLayoutDetails.select(
            fn.group_concat(fn.distinct(DeviceLayoutDetails.zone_id)).alias('zone_id')).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == DeviceLayoutDetails.device_id) \
            .where(*clauses)

        for record in zone_data_query:
            if record['zone_id']:
                zone_ids = list(record['zone_id'].split(','))

        if zone_ids:
            device_clauses = [DeviceLayoutDetails.zone_id << zone_ids,
                              DeviceMaster.company_id == company_id]
            if device_type:
                device_clauses.append(DeviceMaster.device_type_id << device_type)

            device_data_query = DeviceMaster.select(
                fn.group_concat(fn.distinct(DeviceMaster.id)).alias('device_id')).dicts() \
                .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .where(*device_clauses)

            for record in device_data_query:
                device_ids = list(record['device_id'].split(','))
                return device_ids

        else:
            return None

    except (IntegrityError, InternalError) as e:
        logger.error(e)
        return e

    except DoesNotExist as e:
        logger.error(e)
        return None

    except Exception as e:
        logger.error("Error in get_zone_wise_device_list".format(e))
        return None


@log_args
def get_device_data_dao(data_dict):
    company_id = data_dict['company_id']
    system_id = data_dict.get('system_id', None)
    device_type = data_dict.get('device_type', None)
    device_id = data_dict.get('device_id', None)
    device_type_id = data_dict.get("device_type_id", None)
    associated_device = data_dict.get('associated_device', None)

    try:
        clauses = [DeviceMaster.company_id == company_id]
        if device_type or device_type_id:
            if not device_type_id:
                device_type = yaml.safe_load(device_type)
                device_type_id = [settings.DEVICE_TYPES[each_type] for each_type in device_type]
            else:
                device_type_id = [int(device_type_id)]

            if (settings.DEVICE_TYPES['CSR'] in device_type_id or settings.DEVICE_TYPES[
                'Manual Filling Device'] in device_type_id or settings.DEVICE_TYPES[
                    'Refilling Device'] in device_type_id) and not device_id:
                #  function to get all devices that fall s in zone of given device_types
                device_ids = get_zone_wise_device_list(company_id, device_type_id, system_id)
                if device_ids:
                    clauses.append(DeviceMaster.id << device_ids)
                    trolley_data = db_get_device_data(clauses)
                    return trolley_data
                else:
                    clauses.append(DeviceMaster.device_type_id << device_type_id)
            else:
                clauses.append(DeviceMaster.device_type_id << device_type_id)

        if system_id:
            clauses.append(DeviceMaster.system_id == system_id)

        if device_id:
            clauses.append(DeviceMaster.id == device_id)

        if associated_device:
            clauses.append(DeviceMaster.associated_device == associated_device)

        trolley_data = db_get_device_data(clauses)
        return trolley_data
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_device_data_dao".format(e))
        raise

    except DoesNotExist as e:
        logger.error("Error in get_device_data_dao".format(e))
        raise

    except KeyError as e:
        logger.error("Error in get_device_data_dao".format(e))
        raise


@log_args_and_response
def get_device_master_data_dao(associated_device=None, serial_number=None):
    try:
        if associated_device:
            device_data = DeviceMaster.get(DeviceMaster.associated_device == associated_device)
            return device_data
        if serial_number:
            robot_data = DeviceMaster.get(serial_number=serial_number)
            return robot_data

    except DoesNotExist as e:
        logger.error("Error in get_device_master_data_dao".format(e))
        raise


@log_args_and_response
def add_device_data_dao(device_info):
    try:
        record = BaseModel.db_create_record({
            "system_id": device_info["system_id"],
            "company_id": device_info['company_id'],
            "name": device_info["name"],
            "device_type_id": device_info["device_type_id"],
            "serial_number": device_info["serial_number"],
            "version": device_info["version"],
            "created_by": device_info["user_id"],
            "modified_by": device_info["user_id"],
            "ip_address": device_info.get("ip_address", None),
            "associated_device": device_info.get("associated_device", None),
            "created_date": get_current_date_time(),
            "modified_date": get_current_date_time(),
            "active": settings.is_device_active
        }, DeviceMaster, get_or_create=False)
        return record.id
    except (IntegrityError, InternalError) as e:
        logger.error("Error in add_device_data_dao".format(e))
        raise


@log_args_and_response
def get_active_mfd_trolley(company_id):

    try:
        with db.transaction():
            query = DeviceMaster.select(DeviceMaster.id, DeviceMaster.name).dicts() \
                .where(DeviceMaster.company_id == company_id,
                       DeviceMaster.active == settings.is_device_active,
                       DeviceMaster.device_type_id == settings.DEVICE_TYPES['Manual Canister Cart']) \
                .order_by(DeviceMaster.id)

            return query

    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_active_mfd_trolley".format(e))
        raise


@log_args_and_response
def set_location_enable_dao(device_id: int, display_location: str) -> dict:
    """
    This function enables the location for the given device and display location
    """

    try:
        with db.transaction():
            enable_location = LocationMaster.enable_location(device_id=device_id, display_location=display_location)
            if enable_location == 1:
                location_id = LocationMaster.get_location_id_by_display_location(device_id, display_location)
                update_enabled_locations = update_enabled_location_history(location_id=location_id,
                                                                           status=settings.LOCATION_ENABLE)
                if update_enabled_locations == 1:
                    return update_enabled_locations
                else:
                    raise Exception("Error in updating Location History, Location Already enabled.")
            else:
                raise Exception("Location already enabled.")

    except (IntegrityError, InternalError) as e:
        logger.error("Error in set_location_enable_dao".format(e))
        raise


@log_args_and_response
def set_location_disable_dao(disable_info_list: list) -> bool:
    try:
        with db.transaction():
            # location_id_list = list()
            location_id_list = [disable_loc["loc_id"] for disable_loc in disable_info_list]
            update_disabled_flag = LocationMaster.disable_location(location_id_list=location_id_list)
            logger.info(update_disabled_flag)
            if update_disabled_flag:
                disabled_locations_status = add_multiple_disable_location_history(data_dict_list=disable_info_list)
                if disabled_locations_status:
                    return True
            return False

    except (IntegrityError, InternalError) as e:
        logger.error("Error in set_location_disable_dao".format(e))
        raise


@log_args_and_response
def locations_to_be_disabled(disable_info_dict_list, locations_to_disable):
    try:
        with db.transaction():
            update_disabled_flag = LocationMaster.disable_location(location_id_list=locations_to_disable)
            logger.info(update_disabled_flag)
            if update_disabled_flag:
                disabled_locations_status = add_multiple_disable_location_history(data_dict_list=disable_info_dict_list)
            if disabled_locations_status:
                return True
            return False

    except (IntegrityError, InternalError) as e:
        logger.error("Error in locations_to_be_disabled".format(e))
        raise


@log_args_and_response
def update_enabled_location_history(location_id, status):
    try:
        with db.transaction():
            disabled_location_history_id = DisabledLocationHistory.get_latest_disabled_id(location_id=location_id)
            logger.info(disabled_location_history_id)
            update_status = DisabledLocationHistory.update_location_status(
                disabled_location_history_id=disabled_location_history_id, status=status)
            logger.info("update_status:" + str(update_status))
            return update_status
    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error("Error in update_enabled_location_history".format(e))
        raise


@log_args_and_response
def add_disable_location_history(data_dict):
    try:
        with db.transaction():
            record = DisabledLocationHistory.add_disabled_location(data_dict=data_dict)
            return record
    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error("Error in add_disable_location_history".format(e))
        raise


@log_args_and_response
def add_multiple_disable_location_history(data_dict_list):
    try:
        with db.transaction():
            record = DisabledLocationHistory.add_multiple_disabled_location(data_dict_list=data_dict_list)
            return record
    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error("Error in add_multiple_disable_location_history".format(e))
        raise


@log_args_and_response
def validate_device_ids_with_company(device_ids: list, company_id: int) -> bool:
    try:
        return DeviceMaster.db_verify_devicelist(device_ids, company_id)
    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error(e)
        return False


@log_args_and_response
def get_location_id_by_display_location_dao(device_id, location):
    try:
        return LocationMaster.get_location_id_by_display_location(device_id, location)
    except DoesNotExist as e:
        logger.error("No location exists for location_number {} in device {}, {}".format(location, device_id, e))
        raise DoesNotExist


@log_args_and_response
def get_location_id_by_display_location_list_dao(device_id: int, location_list: list) -> list:
    try:
        return LocationMaster.get_location_id_by_display_location_list(device_id, location_list)
    except DoesNotExist as e:
        logger.error("No location exists for location_number {} in device {}, {}".format(location_list, device_id, e))
        raise DoesNotExist


@log_args_and_response
def get_location_id_by_location_number_dao(device_id, location_number):
    try:
        return LocationMaster.get_location_id(device_id, location_number=location_number)
    except DoesNotExist as e:
        logger.error("No location exists for location_number {} in device {}".format(location_number, device_id))
        raise e
    except Exception as e:
        logger.error("Error in get_location_id_by_location_number_dao".format(e))
        raise e


@log_args_and_response
def db_location_disabled_details(location_id: int):
    try:
        return DisabledLocationHistory.db_location_disabled(loc_id=location_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in db_location_disabled_details".format(e))
        raise


@log_args_and_response
def disabled_locations_dao(location_id_list: List[int]) -> Dict[int, str]:
    try:
        return LocationMaster.disabled_locations(location_id_list=location_id_list)
    except (InternalError, IntegrityError) as e:
        logger.error("Error in disabled_locations_dao".format(e))
        raise


@log_args_and_response
def create_disabled_location_history(location_info):
    try:
        record = BaseModel.db_create_record(location_info, DisabledLocationHistory, get_or_create=False)
        return record.id
    except (InternalError, IntegrityError) as e:
        logger.error("Error in create_disabled_location_history".format(e))
        raise


@log_args_and_response
def get_disabled_locations_of_devices(device_ids):
    try:
        return LocationMaster.db_get_disabled_locations_of_devices(device_ids=device_ids)
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("Error in get_disabled_locations_of_devices".format(e))
        raise e


@log_args_and_response
def get_robots_by_system_id_dao(system_id, version=None):
    try:
        robot_data = DeviceMaster.db_get_robots_by_system_id(system_id=system_id, version=version)
        return robot_data
    except(IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_robots_by_system_id_dao".format(e))
        raise


@log_args_and_response
def get_max_locations_of_a_device(device_id):
    try:
        max_locations = DeviceMaster.select(fn.COUNT(LocationMaster.id).alias('max_locations')).dicts() \
            .join(LocationMaster, on=LocationMaster.device_id == DeviceMaster.id) \
            .where(DeviceMaster.id == device_id).get()
        return max_locations["max_locations"]

    except (DoesNotExist, IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_max_locations_of_a_device".format(e))
        raise e


@log_args_and_response
def get_csr_data_company_id_dao(company_id):
    try:
        csr_data = DeviceMaster.db_get_csr_by_company_id(company_id)
        return csr_data
    except(IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_csr_data_company_id_dao".format(e))
        raise


@log_args_and_response
def get_drawer_data_dao(device_id: int, shelf_list: list = None) -> list:
    try:
        return ContainerMaster.db_get_drawer_data_of_device(device_ids=[device_id], shelf_list=shelf_list)
    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error("Error in get_drawer_data_dao".format(e))
        raise e


@log_args_and_response
def get_container_data_based_on_serial_numbers_dao(serial_numbers: list) -> list:
    try:
        return ContainerMaster.db_get_container_data_based_on_container_serial_numbers(
            container_serial_numbers=serial_numbers)
    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error("Error in get_container_data_based_on_serial_numbers_dao".format(e))
        raise e


@log_args_and_response
def update_container_lock_status(container_id: int, emlock_status: bool) -> int:
    try:
        return ContainerMaster.update_lock_status(container_id=container_id, emlock_status=emlock_status)
    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error("Error in update_container_lock_status".format(e))
        raise e


@log_args_and_response
def get_device_drawer_info(company_id, system_id=None, device_id=None, station_type=None, station_id=None,
                           serial_number=None):
    try:
        clauses = [DeviceMaster.company_id == company_id]
        if station_type and station_id:
            serial_number = '{}{}{}'.format(station_type, constants.SERIAL_NUMBER_SEPARATOR, station_id)
            clauses.append(DeviceMaster.serial_number == serial_number)

        if serial_number:
            clauses.append(DeviceMaster.serial_number == serial_number)

        if system_id:
            clauses.append(DeviceMaster.system_id == system_id)

        if device_id:
            clauses.append(DeviceMaster.id == device_id)

        device_data = db_get_device_data(clauses)
        drawer_data = list()

        if device_data:
            device_id = device_data[0]['id']
            drawer_data = ContainerMaster.get_csr_drawer_data(device_id=device_id)

        return device_data, drawer_data

    except IntegrityError as e:
        logger.error("Error in get_device_drawer_info".format(e))
        return error(2001)
    except InternalError as e:
        logger.error("Error in get_device_drawer_info".format(e))
        return error(2001)


@log_args_and_response
def db_delete_canister_drawer_by_drawer_name_dao(canister_drawer_data):
    try:
        return ContainerMaster.db_delete_canister_drawer_by_drawer_name(canister_drawer_data=canister_drawer_data)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_delete_canister_drawer_by_drawer_name_dao".format(e))
        raise


@log_args_and_response
def db_update_drawer_ip_by_drawer_name_dao(canister_drawer_data, ip_address, drawer_size):
    try:
        return ContainerMaster.db_update_drawer_ip_by_drawer_name(canister_drawer_data=canister_drawer_data,
                                                                  ip_address=ip_address, drawer_size=drawer_size)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_update_drawer_ip_by_drawer_name_dao".format(e))
        raise


@log_args_and_response
def db_get_device_drawers_quantity(device_id):
    try:
        return DeviceMaster.get_drawers_quantity(device_id=device_id)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in db_get_device_drawers_quantity".format(e))
        raise


@log_args_and_response
def get_csr_drawer_data_dao(device_id):
    try:
        return ContainerMaster.get_csr_drawer_data(device_id=device_id)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_csr_drawer_data_dao".format(e))
        raise


@log_args_and_response
def validate_container_with_company(container_ids: list, company_id: int) -> bool:
    """
    To verify containers with company
    @param container_ids:
    @param company_id: int
    """
    try:
        container_count = ContainerMaster.select() \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .where(ContainerMaster.id << container_ids, DeviceMaster.company_id == company_id).count()

        if container_count == len(set(container_ids)):
            return True
        return False
    except DoesNotExist:
        return False
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in validate_container_with_company".format(e))
        raise e


def db_get_device_name_by_device_id(device_id: int) -> str:
    try:
        query = DeviceMaster.select(DeviceMaster.name).dicts().where(DeviceMaster.id == device_id)
        for record in query:
            device_name = record['name']
            return device_name
    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_get_device_name_by_device_id".format(e))
        raise


def get_max_locations_per_drawer_based_on_device_type(device_type_id: int, company_id: int) -> int:
    """
    Method to get number of max locations per drawer of a device
    @param company_id:
    @param device_type_id:
    @return: location count
    """
    try:
        location_count = LocationMaster.select(fn.COUNT(LocationMaster.id).alias("locations_count")).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(DeviceTypeMaster, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .where(DeviceTypeMaster.id == device_type_id, DeviceMaster.company_id == company_id) \
            .group_by(ContainerMaster.id).get()
        return location_count["locations_count"]
    except DoesNotExist:
        return 0
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_max_locations_per_drawer_based_on_device_type".format(e))
        raise e


def get_max_drawers_per_device_based_on_device_type(device_type_id: int, company_id: int) -> int:
    """
    Method to get number of max drawers per device
    @param company_id:
    @param device_type_id:
    @return: location count
    """
    try:
        drawers_count = ContainerMaster.select(fn.COUNT(ContainerMaster.id).alias("drawers_count")).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(DeviceTypeMaster, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .where(DeviceTypeMaster.id == device_type_id, DeviceMaster.company_id == company_id) \
            .group_by(DeviceMaster.id).get()
        return drawers_count["drawers_count"]
    except DoesNotExist:
        return 0
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_max_drawers_per_device_based_on_device_type".format(e))
        raise e


@log_args_and_response
def get_max_locations_per_drawer_based_on_device_id(device_id: int) -> int:
    """
    Method to get number of max locations per drawer of a device
    @param device_id:
    @return: location count
    """
    try:
        location_count = LocationMaster.select(fn.COUNT(LocationMaster.id).alias("locations_count")).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .where(DeviceMaster.id == device_id) \
            .group_by(ContainerMaster.id).get()
        return location_count["locations_count"]
    except DoesNotExist:
        return 0
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_max_locations_per_drawer_based_on_device_id".format(e))
        raise e


@log_args_and_response
def get_max_drawers_per_device_based_on_device_id(device_id: int) -> int:
    """
    Method to get number of max drawers per device
    @param device_id:
    @return: get max drawers per device
    """
    try:
        drawers_count = ContainerMaster.select(fn.COUNT(ContainerMaster.id).alias("drawers_count")).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .where(DeviceMaster.id == device_id) \
            .group_by(DeviceMaster.id).get()
        return drawers_count["drawers_count"]
    except DoesNotExist:
        return 0
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_max_drawers_per_device_based_on_device_id".format(e))
        raise e


@log_args_and_response
def get_drawer_data(drawer_id: int) -> dict:
    """
         Method to get drawer data
         @param drawer_id: Integer
         @return: dictionary
    """
    try:
        return ContainerMaster.db_get_drawer_data(drawer_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("Error in get_drawer_data".format(e))
        raise e


@log_args_and_response
def get_drawer_data_based_on_serial_number(drawer_serial_number: int, company_id: int) -> dict:
    """
         Method to get drawer data
         @param company_id:
         @param drawer_serial_number: Integer
         @return: dictionary
    """
    try:
        container_data = ContainerMaster.select() \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .where(ContainerMaster.serial_number == drawer_serial_number,
                   DeviceMaster.company_id == company_id).dicts().get()
        return container_data
    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error("Error in get_drawer_data_based_on_serial_number".format(e))
        raise e
    except DoesNotExist as e:
        logger.error("Error in get_drawer_data_based_on_serial_number".format(e))
        return {}


@log_args_and_response
def get_code_by_station_type_id(station_type_id):
    try:
        query = DeviceTypeMaster.select(DeviceTypeMaster.container_code, DeviceTypeMaster.device_code).dicts() \
            .where(DeviceTypeMaster.station_type_id == station_type_id)
        for record in query:
            return record
    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error("Error in get_code_by_station_type_id".format(e))
        raise e


@log_args_and_response
def get_station_type_by_device_container_code(code: str):
    """
    Method to fetch station type based on device code or container code
    @param code:
    @return:
    """
    try:
        query = DeviceTypeMaster.select(DeviceTypeMaster.station_type_id).dicts() \
            .where((DeviceTypeMaster.container_code == code) | (DeviceTypeMaster.device_code == code)).get()
        return query["station_type_id"]
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_station_type_by_device_container_code".format(e))
        raise e
    except DoesNotExist as e:
        logger.error("Error in get_station_type_by_device_container_code".format(e))
        raise e


def get_location_of_canister_based_on_rfid(rfid: str, drawer_type_id: int) -> dict:
    """
    Method to fetch canister location based on rfid
    @param drawer_type_id:
    @param rfid:
    @return:
    """
    try:
        if drawer_type_id == constants.MFD_DRAWER_TYPE_ID:
            canister_location = MfdCanisterMaster.select(LocationMaster).dicts() \
                .join(LocationMaster, on=LocationMaster.id == MfdCanisterMaster.location_id) \
                .where(MfdCanisterMaster.rfid == rfid).get()
        else:
            canister_location = CanisterMaster.select(LocationMaster).dicts() \
                .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
                .where(CanisterMaster.rfid == rfid).get()
        return canister_location
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_location_of_canister_based_on_rfid".format(e))
        raise e
    except DoesNotExist as e:
        raise e


def get_location_data_by_display_location(device_id, display_location):
    """
    Method to fetch location data
    :return:
    """
    try:
        query = LocationMaster.select().where(LocationMaster.device_id == device_id,
                                              LocationMaster.display_location == display_location).get()
        return query
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_location_data_by_display_location".format(e))
        raise e
    except DoesNotExist as e:
        raise e


@log_args_and_response
def get_mfd_locations_for_devices(device_ids) -> dict:
    """
    This function returns all the mfd_locations for given device
    """
    try:
        locations = {}
        for device in device_ids:
            locations[device] = set()
            query = LocationMaster.select(LocationMaster.display_location, LocationMaster.location_number) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .where((LocationMaster.device_id == device),
                       (ContainerMaster.drawer_type == constants.SIZE_OR_TYPE_MFD))
            for record in query.dicts():
                locations[device].add((record["display_location"], record["location_number"]))
        return locations
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("Error in get_mfd_locations_for_devices".format(e))
        raise e


@log_args_and_response
def get_empty_locations_of_drawer(drawer_id: int) -> list:
    """
    Method to fetch empty locations of a drawer
    @param drawer_id:
    @return:
    """
    try:
        locations = list()
        empty_locations_query = LocationMaster.select(LocationMaster.id).dicts() \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=(CanisterMaster.location_id == LocationMaster.id)) \
            .where(LocationMaster.container_id == drawer_id,
                   CanisterMaster.id.is_null(True))
        for record in empty_locations_query:
            locations.append(record["id"])
        return locations
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_empty_locations_of_drawer".format(e))
        raise e


@log_args_and_response
def get_mfd_drawer_quad_capacity_count(device_list):
    """
    Function to get mfd drawer quad capacity count device wise considering
    only active locations
    @param device_list: list
    @return:
    """
    device_quad_loc_count = dict()
    try:
        query = LocationMaster.select(LocationMaster.device_id, LocationMaster.quadrant,
                                      fn.COUNT(LocationMaster.id).alias('location_count')).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .where(LocationMaster.is_disabled == settings.is_location_active,
                   LocationMaster.device_id << device_list,
                   ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE["MFD"]]) \
            .group_by(LocationMaster.device_id, LocationMaster.quadrant)

        for record in query:
            if record['device_id'] not in device_quad_loc_count.keys():
                device_quad_loc_count[record['device_id']] = dict()
            if record['quadrant'] not in device_quad_loc_count[record['device_id']].keys():
                device_quad_loc_count[record['device_id']][record['quadrant']] = 0

            device_quad_loc_count[record['device_id']][record['quadrant']] += record['location_count']

        return device_quad_loc_count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_mfd_drawer_quad_capacity_count".format(e))
        raise


@log_args_and_response
def get_associated_mfs_stations(station_list: list) -> dict:
    """
    Function to get associated mfs stations for given station list
    @param station_list:
    @return:
    """
    station_associated_device = dict()
    try:
        station_list = [int(station) for station in station_list]
        query = DeviceMaster.select(DeviceMaster.id,
                                    DeviceMaster.associated_device).dicts() \
            .where(DeviceMaster.id << station_list)

        for record in query:
            station_associated_device[record['id']] = record['associated_device']

        return station_associated_device

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_associated_mfs_stations".format(e))
        raise


@log_args_and_response
def get_available_canisters_in_device(device_id: int) -> list:
    """
    Method to return list of canisters available in given device
    @param device_id:
    @return:
    """
    try:
        canister_list = list()
        query = LocationMaster.select(fn.DISTINCT(CanisterMaster.id)).dicts() \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .where(LocationMaster.device_id == device_id, CanisterMaster.id.is_null(False))

        for record in query:
            canister_list.append(record["id"])
        return canister_list
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("Error in get_available_canisters_in_device".format(e))
        raise


@log_args_and_response
def db_get_enabled_locations(device_ids: list = None, company_id: list = None, drawer_numbers: list = None) -> list:
    """
    Returns Enabled locations for given device ids and drawer numbers
    """
    drawer_types: list = [settings.SIZE_OR_TYPE['BIG'], settings.SIZE_OR_TYPE['SMALL'],
                          settings.SIZE_OR_TYPE['MFD']]
    try:
        query = LocationMaster.select(
            LocationMaster.id.alias("location_id"),
            DeviceTypeMaster.device_type_name,
            DeviceMaster.name.alias('device_name'),
            DeviceMaster.id.alias('device_id'),
            LocationMaster.display_location,
            ContainerMaster.drawer_name.alias('drawer_number'),
            DeviceLayoutDetails.zone_id,
            ZoneMaster.name.alias('zone_name'),
            DeviceMaster.system_id,
        ).dicts().join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(DeviceTypeMaster, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, on=ZoneMaster.id == DeviceLayoutDetails.zone_id) \
            .where((LocationMaster.is_disabled == 0))
        # check for device_ids
        if device_ids:
            query = query.where(DeviceMaster.id << device_ids, ContainerMaster.drawer_type << drawer_types)
        # check for company_id
        elif company_id:
            query = query.where(DeviceMaster.company_id == company_id,
                                ContainerMaster.drawer_type << drawer_types)
        # check for drawer numbers
        if drawer_numbers:
            query = query.where(ContainerMaster.drawer_name << drawer_numbers)
        # return as per the given order
        query = query.order_by(DeviceMaster.id, LocationMaster.location_number)
        return list(query)

    except (IntegrityError, InternalError) as e:
        logger.error("Error in db_get_enabled_locations".format(e))
        raise


@log_args_and_response
def get_locations_per_drawer(device_id: int) -> int:
    """
    This method gets the count of the locations per drawer.
    @param device_id:
    @return:
    """
    container_id: int
    try:
        # get one container_id of the given device
        container_id = ContainerMaster.get_drawer_data_for_device(device_id=device_id)[0]["trolley_drawer_id"]

        # get location count for the fetched container_id
        count = len(LocationMaster.get_locations_by_container_id(device_id=device_id, container_id=[container_id]))

        return count

    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_locations_per_drawer".format(e))
        raise


@log_args_and_response
def get_disabled_drawers_by_device(device_id: int, locations_per_drawer: int) -> list:
    """
    This method gets the list of disabled drawers.
    @param device_id:
    @param locations_per_drawer:
    @return:
    """
    result_list: list = list()
    try:
        # get the list of disabled drawers

        query = LocationMaster.select(LocationMaster.container_id,
                                      ContainerMaster.drawer_name).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .where((LocationMaster.device_id == device_id) & (LocationMaster.is_disabled == True)) \
            .group_by(LocationMaster.container_id) \
            .having(fn.sum(LocationMaster.is_disabled) == locations_per_drawer)

        for record in query:
            result_list.append(record["drawer_name"])

        return result_list
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_disabled_drawers_by_device".format(e))
        raise


@log_args_and_response
def get_system_id_based_on_device_type(company_id: int, device_type_id: int) -> int:
    """
    This function fetches the vial system id for the given company_id
    """
    try:
        system_id_query = DeviceMaster.select(DeviceMaster.system_id).dicts() \
            .where(DeviceMaster.device_type_id == device_type_id,
                   DeviceMaster.company_id == company_id)
        for record in system_id_query:
            return record["system_id"]

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_system_id_based_on_device_type".format(e))
        raise


@log_args_and_response
def get_location_canister_data_by_display_location(device_id, display_locations):
    """
    Method to fetch location data
    :return:
    """
    try:
        query = LocationMaster.select(LocationMaster.id.alias('loc_id'),
                                      LocationMaster.display_location,
                                      LocationMaster.is_disabled,
                                      CanisterMaster.rfid,
                                      CanisterMaster.id.alias('canister_id')).dicts() \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .where(LocationMaster.device_id == device_id,
                   LocationMaster.display_location << display_locations)
        return query
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_location_canister_data_by_display_location".format(e))
        raise e


@log_args_and_response
def db_get_device_data(clauses):
    device_data = []
    try:
        DeviceMasterAlias = DeviceMaster().alias()
        for record in DeviceMaster.select(DeviceMaster,
                                          DeviceTypeMaster.device_type_name,
                                          DeviceTypeMaster.station_type_id,
                                          DeviceMasterAlias.name.alias('trolley_name'),
                                          DeviceMasterAlias.id.alias('trolley_id'),
                                          DeviceMasterAlias.system_id.alias('trolley_system_id'),
                                          DeviceMasterAlias.active.alias('trolley_active'),
                                          DeviceMasterAlias.serial_number.alias('trolley_serial_number'),
                                          DeviceMasterAlias.associated_device.alias('trolley_associated_device')
                                          ).dicts() \
                .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.associated_device == DeviceMaster.id) \
                .join(DeviceTypeMaster, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                .where(*clauses) \
                .order_by(DeviceMaster.id):
            device_data.append(record)
        return device_data

    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_get_device_data".format(e))
        raise

    except DoesNotExist as e:
        logger.error("Error in db_get_device_data".format(e))
        return device_data


@log_args_and_response
def get_location_info_from_display_location(device_id, display_location):
    """
            formatted location is the location used for the communication with csr hardware
            :return:
            """
    try:
        query = LocationMaster.select(LocationMaster.id, LocationMaster.device_id, LocationMaster.container_id,
                                      ContainerMaster.drawer_name, ContainerMaster.drawer_type,
                                      LocationMaster.quadrant).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .where(LocationMaster.device_id == device_id, LocationMaster.display_location == display_location)

        for record in query:
            return record

    except DoesNotExist as e:
        logger.error("Error in get_location_info_from_display_location".format(e))
        raise NoLocationExists
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_location_info_from_display_location".format(e))
        raise


@log_args_and_response
def get_device_location_category(location_id):
    """

    @param location_id:
    @return:
    """
    try:
        query = LocationMaster.select(ContainerMaster.drawer_size, ContainerMaster.drawer_usage).dicts()\
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.drawer_id)\
                .where(LocationMaster.id == location_id)

        for record in query:
            drawer_size = record['drawer_size']
            drawer_usage = record['drawer_usage']
            return drawer_size, drawer_usage

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_device_location_category".format(e))
        return e
    except DoesNotExist as e:
        logger.error("Error in get_device_location_category".format(e))
        return None, None


@log_args_and_response
def get_devices_of_zone(zone_id, company_id):
    """
    To get the details of the devices present in the given zone_id.
    @param company_id:
    @param zone_id:
    :return:
    """
    db_result = dict()
    db_result['devices'] = list()
    try:
        query = DeviceLayoutDetails.select(DeviceLayoutDetails,
                                           DeviceMaster.device_type_id,
                                           DeviceMaster.serial_number,
                                           DeviceMaster.name,
                                           DeviceMaster.big_drawers,
                                           DeviceMaster.small_drawers,
                                           DeviceMaster.company_id,
                                           DeviceTypeMaster.device_type_name).dicts()\
            .join(DeviceMaster, on=DeviceLayoutDetails.device_id == DeviceMaster.id)\
            .join(DeviceTypeMaster, on=DeviceMaster.device_type_id == DeviceTypeMaster.id)\
            .where(DeviceLayoutDetails.zone_id == zone_id, DeviceLayoutDetails.marked_for_transfer == False,
                   DeviceMaster.company_id == company_id)

        zone_data = dict()
        try:
            zone_data = ZoneMaster.get_zone_data_by_zone_id(zone_id=zone_id, company_id=company_id)
            # conversion_ratio = None
            if zone_data["dimensions_unit_id"] != 5:
                conversion_ratio = UnitConversion.get_conversion_ratio_for_a_unit(convert_from=5,
                                                                                  convert_into=zone_data['dimensions_unit_id'])
            else:
                conversion_ratio = 1
            zone_data['user_entered_height'] = zone_data['height'] * conversion_ratio
            zone_data['user_entered_width'] = zone_data['width'] * conversion_ratio
            zone_data['user_entered_length'] = zone_data['length'] * conversion_ratio
            unit_data = UnitMaster.get_unit_by_unit_id(unit_id=zone_data['dimensions_unit_id'])
            zone_data['unit_name'] = unit_data['name']
            zone_data['unit_symbol'] = unit_data['symbol']
        except DoesNotExist as e:
            pass
        db_result['zone_details'] = zone_data

        return query, db_result

    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_devices_of_zone".format(e))
        raise e


@log_args_and_response
def get_zone_by_system(system_id):

    """
    @param system_id:
    @return:
    """

    db_result = []
    try:
        query = DeviceLayoutDetails.select(DeviceLayoutDetails.zone_id).dicts()\
            .join(DeviceMaster, on=DeviceLayoutDetails.device_id == DeviceMaster.id)\
            .where(DeviceMaster.system_id == system_id)

        for record in query:
            if record['zone_id'] not in db_result:
                db_result.append(record['zone_id'])
        return db_result
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("Error in get_zone_by_system".format(e))
        raise e


@log_args_and_response
def get_location_ids_by_system_id(company_id,
                                  device_type,
                                  device_id,
                                  version=None,
                                  shelf=None,
                                  drawer_names=None):
    """
    @param shelf:
    @param company_id:
    @param device_type: string
    @param device_id: list
    @param version: string
    @param drawer_names:list
    @return:
    """

    try:

        clauses = [DeviceMaster.active == True]

        if company_id:
            clauses.append(DeviceMaster.company_id == company_id)

        if device_type:
            device_type_id = [settings.DEVICE_TYPES[device] for device in device_type]
            clauses.append(DeviceMaster.device_type_id << device_type_id)

        if device_id:
            clauses.append(DeviceMaster.id << device_id)

        if shelf:
            clauses.append(ContainerMaster.shelf << shelf)

        if drawer_names:
            clauses.append(ContainerMaster.drawer_name << drawer_names)

        if not version:
            version = [settings.ROBOT_SYSTEM_VERSIONS['v2'], settings.ROBOT_SYSTEM_VERSIONS['v3']]
        clauses.append(DeviceMaster.version << version)

        # device_id = DeviceMaster.db_get_robots_by_system_id(system_id)
        response = {'device_id_list': list(),
                    'location_info': dict(), 'shelf_info': dict()}

        select_fields = [
            LocationMaster,
            DeviceMaster.id.alias('device'),
            DeviceMaster,
            MfdCanisterMaster.id.alias('mfd_canister_id'),
            ContainerMaster.shelf,
            ContainerMaster.drawer_usage,
            ContainerMaster.drawer_name,
            ContainerMaster.drawer_type,
            ContainerMaster.drawer_level,
            ContainerMaster.serial_number.alias('container_serial_number'),
            CodeMaster.value.alias('drawer_type_name'),
            LocationMaster.is_disabled.alias('disabled_canister_id'),
            fn.IF(CanisterMaster.id.is_null(False), CanisterMaster.id, MfdCanisterMaster.id).alias('canister_id'),
            CanisterMaster.active,
            CanisterMaster.drug_id
        ]
        query = LocationMaster.select(*select_fields).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(CodeMaster, on=CodeMaster.id == ContainerMaster.drawer_type) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .order_by(LocationMaster.location_number)

        for record in query:
            if record['device'] not in response['location_info'].keys():
                device_shelf_data = get_device_shelf_data(record['device'])
                response['shelf_info'][record['device']] = device_shelf_data
                response['device_id_list'].append([record['device'], record['name']])
                response['location_info'][record['device']] = list()

            if record['shelf'] and record['shelf'] not in response['shelf_info'][record['device']]:
                response['shelf_info'][record['device']].append(record['shelf'])
            response['location_info'][record['device']].append(record)
        return response

    except (DoesNotExist, IntegrityError, InternalError, DataError) as e:
        logger.error("Error in get_location_ids_by_system_id".format(e))
        raise e


@log_args_and_response
def get_device_shelf_data(device_id):
    try:
        query = DeviceMaster.select(ContainerMaster.shelf).dicts() \
            .join(ContainerMaster, on=ContainerMaster.device_id == DeviceMaster.id) \
            .where(DeviceMaster.id == device_id, ContainerMaster.shelf.is_null(False)) \
            .group_by(ContainerMaster.shelf)

        data_dict = list(query)
        shelf_list = [int(item['shelf']) for item in data_dict]
        logger.info(shelf_list)
        return shelf_list

    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_device_shelf_data".format(e))
        raise
    except DoesNotExist as e:
        logger.error("Error in get_device_shelf_data".format(e))
        return list()


@log_args_and_response
def find_empty_location(company_id, required_locations_count=None):
    # In this check in canister master table which of the id of the location master is not
    # present there and get only the first location id and return the data related to that device id.
    # Data will be zone_id, zone name, device_id , device name company_id, Drawer number and location number.
    # In Location master table there will be only those devices present which are registered. So device id can not be null.

    # Here we are applying inner join with the inventory layout tables because we have to show the empty locations
    # from those CSRs which are present in the zones so that we can highlight them.
    try:
        clauses = list()
        clauses.append((CanisterMaster.id.is_null(True)))
        clauses.append((DeviceMaster.id.is_null(False)))
        clauses.append((DeviceTypeMaster.device_type_name == settings.DEVICE_TYPES_NAMES['CSR']))
        clauses.append((DeviceMaster.company_id == company_id))


        # todo: Right now if there is no location mapping for ndc then it will give the random empty location
        # irrespective of the fact that whether it is mapped to any another location or not.
        query = LocationMaster.select(LocationMaster.id.alias('location_id'),
                                      ContainerMaster.drawer_name.alias('drawer_number'),
                                      LocationMaster.display_location,
                                      LocationMaster.location_number,
                                      DeviceLayoutDetails.id.alias('device_id'),
                                      DeviceMaster.name.alias('device_name'),
                                      DeviceMaster.big_drawers,
                                      DeviceMaster.small_drawers,
                                      DeviceMaster.company_id,
                                      ZoneMaster.id.alias('zone_id'),
                                      ZoneMaster.name.alias('zone_name'),
                                      ContainerMaster.ip_address,
                                      ContainerMaster.secondary_ip_address,
                                      fn.IF(LocationMaster.display_location, LocationMaster.get_device_location(),
                                            None).alias('csr_location_number')
                                      ).dicts() \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_INNER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_INNER, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_INNER, DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_INNER, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(ZoneMaster, JOIN_INNER, on=ZoneMaster.id == DeviceLayoutDetails.zone_id) \
            .where(functools.reduce(operator.and_, clauses))
        if required_locations_count:
            query = query.limit(required_locations_count)
        # db_data = list()
        # for location_data in query:
        #     location_data['formatted_location'] = int(location_data['display_location'].split('-')[1]) - 1
        #     db_data.append(location_data)
        return list(query)
    except (IntegrityError, InternalError, DataError, DoesNotExist) as e:
        logger.error("Error in find_empty_location".format(e))
        raise e
   


@log_args_and_response
def db_get_robots_by_systems_dao(system_id_list):
    """
    Returns robots data for given system id list
    :param system_id_list: list
    :return: list
    """
    robots_data = dict()
    try:
        if system_id_list:
            for record in DeviceMaster.select(DeviceMaster, fn.COUNT(fn.DISTINCT(LocationMaster.id)).alias("max_canisters")).dicts() \
                    .join(LocationMaster, on=LocationMaster.device_id == DeviceMaster.id) \
                    .where(DeviceMaster.system_id << system_id_list,
                           DeviceMaster.device_type_id == settings.DEVICE_TYPES["ROBOT"],
                           DeviceMaster.active == settings.is_device_active,
                           LocationMaster.is_disabled == settings.is_location_active)\
                    .group_by(LocationMaster.device_id):
                robots_data.setdefault(record["system_id"], list()).append(record)
        return robots_data
    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_get_robots_by_systems_dao".format(e))
        raise


@log_args
def get_mfs_system_device_from_company_id(company_id: int, system_id = None, batch_id: int or None = None) -> dict:
    """
    Function to get MFS system and device id from given company and batch
    @param company_id:
    @param batch_id:
    @return:
    """
    system_device_dict: dict = dict()
    zone_ids: list = list()
    try:
        # get system id from batch_id
        if not system_id:
            system_id = BatchMaster.db_get_system_id_from_batch_id(batch_id=batch_id)

        # get zone from system id
        query = DeviceLayoutDetails.select(DeviceLayoutDetails.zone_id).dicts() \
            .join(DeviceMaster, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .where(DeviceMaster.system_id == system_id)

        for record in query:
            if record['zone_id'] not in zone_ids:
                zone_ids.append(record['zone_id'])

        if not zone_ids:
            return system_device_dict

        # query to get MFS devices with their system id of given zone
        query = DeviceMaster.select(DeviceMaster.id.alias('device_id'),
                                    DeviceMaster.system_id).dicts() \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, on=DeviceMaster.id == DeviceLayoutDetails.device_id) \
            .where(DeviceMaster.company_id == company_id,
                   DeviceMaster.active == settings.is_device_active,
                   DeviceLayoutDetails.zone_id << zone_ids,
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES['Manual Filling Device']) \
            .group_by(DeviceMaster.id).order_by(DeviceMaster.id)

        for record in query:
            system_device_dict[record['system_id']] = record['device_id']

        return system_device_dict

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in get_mfs_system_device_from_company_id: {}".format(e))
        raise



def get_active_mfs_id_by_company_id(company_id: int, system_id: int) -> list:
    """
    Function to get mfs stations by company and system
    @param company_id:
    @param system_id:
    @return:
    """
    manual_fill_stations = list()
    try:
        zone_ids = get_zone_by_system(system_id)
        if not zone_ids:
            return manual_fill_stations
        query = DeviceMaster.select(DeviceMaster.id).dicts() \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, on=DeviceMaster.id == DeviceLayoutDetails.device_id) \
            .where(DeviceMaster.company_id == company_id,
                   DeviceMaster.active == settings.is_device_active,
                   DeviceLayoutDetails.zone_id << zone_ids,
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES['Manual Filling Device']) \
            .group_by(DeviceMaster.id)

        for record in query:
            manual_fill_stations.append(record['id'])
        return manual_fill_stations
    except DoesNotExist as e:
        logger.error("Error in get_active_mfs_id_by_company_id".format(e))
        return manual_fill_stations
    except (InternalError, IntegrityError) as ex:
        logger.error("Error in get_active_mfs_id_by_company_id".format(ex))
        raise


def db_get_mfs_data(company_id, system_id):
    """
    returns active manual fill stations of a company and number of canisters to be filled on that MFS with associated
    device
    @param company_id:
    @param system_id:
    """
    try:
        zone_ids = get_zone_by_system(system_id)
        if not zone_ids:
            return None
        query = DeviceMaster.select(DeviceMaster.id.alias('device_id'),
                                    DeviceMaster.name.alias('device_name'),
                                    DeviceMaster.associated_device,
                                    DeviceMaster.serial_number,
                                    DeviceMaster.system_id,
                                    MfdAnalysis.assigned_to,
                                    fn.COUNT(MfdAnalysis.id).alias('pending_canister')).dicts() \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, on=DeviceMaster.id == DeviceLayoutDetails.device_id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER, on=((MfdAnalysis.mfs_device_id == DeviceMaster.id) &
                                                    (MfdAnalysis.status_id << [
                                                        constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                                        constants.MFD_CANISTER_PENDING_STATUS]))) \
            .where(DeviceMaster.company_id == company_id,
                   DeviceMaster.active == settings.is_device_active,
                   DeviceLayoutDetails.zone_id << zone_ids,
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES['Manual Filling Device']) \
            .group_by(DeviceMaster.id, MfdAnalysis.assigned_to).order_by(DeviceMaster.id)
        return query
    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_get_mfs_data".format(e))
        raise e


@log_args_and_response
def validate_device_id_dao(device_id: int, company_id: int) -> bool:
    """
    This function validates if the device_id belongs to the given company.
    @param device_id:
    @param company_id:
    @return:
    """
    try:
        return DeviceMaster.db_verify_device_id_by_company(device_id=device_id, company_id=company_id)
    except Exception as e:
        logger.error("Error in validate_device_id_dao".format(e))


@log_args_and_response
def get_location_info_from_location_id(location_id: int):
    """
        Function to get location info from id
        @param location_id:
        @return:
        """
    try:
        query = LocationMaster.select(LocationMaster.id, LocationMaster.device_id, LocationMaster.display_location,
                           LocationMaster.location_number, ContainerMaster.drawer_level,
                           ContainerMaster.drawer_name, ContainerMaster.drawer_type).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .where(LocationMaster.id == location_id)

        for record in query:
            return record

    except DoesNotExist as e:
        logger.error("error in get_location_info_from_location_id {}".format(e))
        raise NoLocationExists



@log_args_and_response
def get_quadrant_from_device_location_dao(device_id: int, location: list):

    try:
        quadrant = LocationMaster.get_quadrant_from_device_location(device_id, location)
        return quadrant
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in get_quadrant_from_device_location_dao {}".format(e))
        raise


@log_args_and_response
def get_device_master_data_dao(device_id: int):

    try:
        device_data = DeviceMaster.db_get_device_master_data(device_id=device_id)
        return device_data
    except(IntegrityError, InternalError) as e:
        logger.error("error in get_device_master_data_dao {}".format(e))
        raise e


@log_args_and_response
def get_robot_quad_can_capacity_batch_sch(system_id_list):
    """

    @param system_id_list:
    @return:
    """
    robots_quad_can_data = dict()
    quad_can = list()
    try:
        if system_id_list:
            query = DeviceMaster.select(DeviceMaster,
                                        LocationMaster.quadrant,
                                        fn.COUNT(fn.DISTINCT(LocationMaster.id)).alias("max_canisters")).dicts() \
                    .join(LocationMaster, on=LocationMaster.device_id == DeviceMaster.id) \
                    .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id).dicts() \
                    .where(DeviceMaster.system_id << system_id_list,
                           LocationMaster.is_disabled == settings.is_location_active,
                           ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['BIG'],
                                                           settings.SIZE_OR_TYPE['SMALL']],
                           DeviceMaster.active == settings.is_device_active,
                           DeviceMaster.device_type_id == settings.DEVICE_TYPES["ROBOT"]) \
                    .group_by(DeviceMaster.id, LocationMaster.quadrant)

            for record in query:
                if record['id'] not in robots_quad_can_data.keys():
                    robots_quad_can_data[record['id']] = dict()
                if record['quadrant'] not in robots_quad_can_data[record['id']]:
                    robots_quad_can_data[record['id']][record['quadrant']] = record['max_canisters']

                quad_can.append(record['max_canisters'])

        return robots_quad_can_data, min(quad_can)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_robot_quad_can_capacity_batch_sch {}".format(e))
        raise


def get_device_type(device_id):
    try:
        device_type = DeviceMaster.select(DeviceMaster.device_type_id).dicts().where(
                DeviceMaster.id == device_id)
        return device_type
    except(IntegrityError, InternalError) as e:
        logger.error("error in get_device_type {}".format(e))
        raise e


def get_device_data_from_serial_number_dao(serial_number):
    """
    get device data from serial number
    @param serial_number:
    @return:
    """
    try:
        response = DeviceMaster.get_device_data_from_serial_number(serial_number=serial_number)
        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_device_data_from_serial_number_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_device_data_from_serial_number_dao {}".format(e))
        raise e


def get_device_type_id_dao(device_type_name):
    """
    get device data id from device type name
    @param device_type_name:
    @return:
    """
    try:
        response = DeviceTypeMaster.get_device_type_id(device_type_name=device_type_name)
        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_device_type_id_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_device_type_id_dao {}".format(e))
        raise e


def get_all_devices_of_a_type_dao(device_type_ids, company_id):
    """
    get device of type
    @param device_type_ids:
    @param company_id:
    @return:
    """
    try:
        response = DeviceMaster.get_all_devices_of_a_type(device_type_ids=device_type_ids,
                                                        company_id=company_id)

        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_all_devices_of_a_type_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_all_devices_of_a_type_dao {}".format(e))
        raise e


def get_company_id_of_a_device_dao(device_id):
    """
    get company id of device
    @param device_id:
    @return:
    """
    try:
        response = DeviceMaster.get_company_id_of_a_device(device_id=device_id)

        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_company_id_of_a_device_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_company_id_of_a_device_dao {}".format(e))
        raise e


def db_get_robot_details_dao(device_id, system_id):
    try:
        return DeviceMaster.db_get_robot_details(device_id, system_id)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_company_id_of_a_device_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_company_id_of_a_device_dao {}".format(e))
        raise e


def get_device_type_from_device_dao(device_id_list):
    try:
        return DeviceMaster.get_device_type_from_device(device_id_list=device_id_list)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_device_type_from_device_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_device_type_from_device_dao {}".format(e))
        raise e


@log_args_and_response
def get_device_id_from_serial_number(serial_number, company_id):
    """
    todo: move this function to device master dao
    @param serial_number:
    @param company_id:
    @return:
    """
    try:
        # todo change this to a optimum way

        query = DeviceMaster.select(DeviceMaster.id).where(DeviceMaster.serial_number == serial_number,
                                                           DeviceMaster.company_id == company_id).get()

        return query.id

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise
    except DoesNotExist as e:
        logger.error(e)
        return None


@log_args_and_response
def get_system_zone_mapping(system_list):

    try:
        system_zone_mapping = {}
        zone_list = set()
        query = DeviceMaster.select(ZoneMaster.id, DeviceMaster.system_id) \
            .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(ZoneMaster, on=ZoneMaster.id == DeviceLayoutDetails.zone_id).where(
            DeviceMaster.system_id << system_list)

        for record in query.dicts():
            system_zone_mapping[record['system_id']] = record['id']
            zone_list.add(record['id'])
        zone_list = list(zone_list)
        return system_zone_mapping, zone_list
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def db_get_robots_by_systems(system_id_list):
    """
    Returns robots data for given system id list
    :param system_id_list: list
    :return: list
    """
    robots_data = dict()
    try:
        if system_id_list:
            for record in DeviceMaster.select(DeviceMaster,
                                              fn.COUNT(fn.DISTINCT(LocationMaster.id)).alias("max_canisters")).dicts() \
                    .join(LocationMaster, on=LocationMaster.device_id == DeviceMaster.id)\
                    .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id)\
                    .where(DeviceMaster.system_id << system_id_list,
                            LocationMaster.is_disabled == settings.is_location_active,
                           ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['BIG'], settings.SIZE_OR_TYPE['SMALL']],
                           DeviceMaster.active == settings.is_device_active,
                           DeviceMaster.device_type_id == settings.DEVICE_TYPES["ROBOT"])\
                    .group_by(DeviceMaster.id):
                robots_data.setdefault(record["system_id"], list()).append(record)
        return robots_data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def verify_device_id_list_dao(device_id, system_id):
    try:
        valid_device = DeviceMaster.db_verify_device_id_list(device_id, system_id)
        return valid_device
    except(IntegrityError, InternalError, DoesNotExist) as e:
        logger.error(e)
        return False
    except Exception as e:
        logger.error(e)
        return False


@log_args_and_response
def get_canister_drug_with_location_for_given_drugs(drug_list:list, device_id: int, batch_id: int, pack_list: list):
    """

    @param batch_id:
    @param drug_list:
    @param device_id:
    @return:
    """
    try:
        drug_travelled = list()
        can_reserved_device = dict()
        canister_drugs_set = set()
        robot_quadrant_drug_data = {device_id: {1:{"drugs": set()},
                                                2: {"drugs": set()},
                                                3: {"drugs": set()},
                                                4: {"drugs": set()}
                                                }}
        remaining_drug_canister_location_dict = dict()
        canister_location_number = dict()
        robot_quadrant_drug_canister_info_dict = {device_id: {1: dict(),
                                                              2: dict(),
                                                              3: dict(),
                                                              4: dict(),
                                                              None: dict()}}

        transfer_can = PackAnalysis.select(PackAnalysisDetails.canister_id,
                                                PackAnalysisDetails.device_id,
                                                PackAnalysisDetails.quadrant,
                                           PackAnalysisDetails.location_number).dicts() \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(PackAnalysis.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                   DrugMaster.concated_fndc_txr_field(sep="##") << drug_list)

        for record in transfer_can:
            if record['canister_id'] not in can_reserved_device.keys():
                can_reserved_device[record['canister_id']] = {"device_id": record['device_id'],
                                                            "quadrant": record["quadrant"],
                                                              "location_number": record['location_number']}

        skipped_canister_list = list()
        if pack_list:
            skipped_canister = ReplenishSkippedCanister.select(ReplenishSkippedCanister.canister_id).dicts()\
                .where(ReplenishSkippedCanister.pack_id << pack_list)

            for record in skipped_canister:
                if record["canister_id"] not in skipped_canister_list:
                    skipped_canister_list.append(record["canister_id"])

        query = CanisterMaster.select(DrugMaster.concated_fndc_txr_field(sep="##").alias("drug"),
                                      CanisterMaster.id, LocationMaster.location_number,
                                      CanisterMaster.canister_type,
                                      LocationMaster.device_id, LocationMaster.quadrant) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(DrugMaster.concated_fndc_txr_field(sep="##") << drug_list,
                   CanisterMaster.active == settings.is_canister_active)

        if skipped_canister_list:
            query = query.where(CanisterMaster.id.not_in(skipped_canister_list))

        query = query.order_by(CanisterMaster.available_quantity)

        for record in query.dicts():

            if record['id'] in can_reserved_device and can_reserved_device[record['id']]["device_id"] == device_id:
                drug_travelled.append(record["drug"])
                canister_location_number[record['id']] = can_reserved_device[record['id']]["location_number"]
                quadrant = can_reserved_device[record['id']]["quadrant"]
                robot_quadrant_drug_data[device_id][quadrant]["drugs"].add(record["drug"])
                canister_drugs_set.add(record["drug"])

                if record["drug"] not in robot_quadrant_drug_canister_info_dict[device_id][record['quadrant']].keys():
                    robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]] = list()

                robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]].append(
                    record["id"])

            elif record['id'] not in can_reserved_device and record['device_id'] == device_id:
                quadrant = record['quadrant']
                drug_travelled.append(record["drug"])
                canister_location_number[record['id']] = record['location_number']
                robot_quadrant_drug_data[device_id][quadrant]["drugs"].add(record["drug"])
                if record["drug"] not in robot_quadrant_drug_canister_info_dict[device_id][record['quadrant']].keys():
                    robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]] = list()

                robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]].append(
                    record["id"])
                canister_drugs_set.add(record["drug"])

        for record in query.dicts():
            if record['id'] not in can_reserved_device.keys() and record["drug"] not in drug_travelled:
                    if record["drug"] not in remaining_drug_canister_location_dict:
                        remaining_drug_canister_location_dict[record["drug"]] = list()

                    remaining_drug_canister_location_dict[record["drug"]].append({"device_id": record["device_id"],
                                                                                  "canister_id": record["id"],
                                                                                  "canister_type": record["canister_type"]})

        return robot_quadrant_drug_data, remaining_drug_canister_location_dict, \
               robot_quadrant_drug_canister_info_dict, canister_location_number, canister_drugs_set

    except (InternalError, IntegrityError, DataError, DoesNotExist, ValueError) as e:
        logger.error("Error in get_canister_drug_with_location_for_given_drugs {}".format(e))
        raise
    except Exception as e:
        logger.error("Exception in get_pack_slotwise_canister_drugs_ {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Exception in get_canister_drug_with_location_for_given_drugs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_nx_canister_drug_with_location_for_given_drugs(drug_list: list,
                                                       device_id: int, batch_id: int, pack_list: list,
                                                       canister_ids: list,
                                                       mfd_data= None,
                                                       drug_id = None):
    """

    @param batch_id:
    @param drug_list:
    @param device_id:
    @return:
    """
    try:
        drug_travelled = list()
        canister_drugs_set = set()
        can_reserved_device = dict()
        canister_status_dict = dict()
        skipped_canister_list = list()
        canister_location_number = dict()
        can_reserved_device_all_data = dict()
        remaining_drug_canister_location_dict = dict()

        robot_quadrant_drug_data = {device_id: {1:{"drugs": set()},
                                                2: {"drugs": set()},
                                                3: {"drugs": set()},
                                                4: {"drugs": set()}
                                                }}

        robot_quadrant_drug_canister_info_dict = {device_id: {1: dict(),
                                                              2: dict(),
                                                              3: dict(),
                                                              4: dict(),
                                                              None: dict()}}

        transfer_can = PackAnalysis.select(PackAnalysisDetails.canister_id,
                                                PackAnalysisDetails.device_id,
                                                PackAnalysisDetails.quadrant,
                                           PackAnalysisDetails.location_number).dicts() \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(PackAnalysis.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                   DrugMaster.concated_fndc_txr_field(sep="##") << drug_list)

        for record in transfer_can:
            if record['canister_id'] not in can_reserved_device.keys():
                can_reserved_device[record['canister_id']] = {"device_id": record['device_id'],
                                                              "quadrant": record["quadrant"],
                                                              "location_number": record['location_number']}

            if record['canister_id'] not in can_reserved_device_all_data.keys():
                can_reserved_device_all_data[record['canister_id']] = dict()

            if record['device_id'] not in  can_reserved_device_all_data[record['canister_id']]:
                can_reserved_device_all_data[record['canister_id']][int(record['device_id'])] = dict()
                can_reserved_device_all_data[record['canister_id']][record['device_id']]["quadrant"] = record["quadrant"]
                can_reserved_device_all_data[record['canister_id']][record['device_id']]["location_number"] = record["location_number"]

        if pack_list:
            fndc_txr_set = set()
            # fndc_txr_with_given_canister = DrugMaster.select(DrugMaster.concated_fndc_txr_field(sep="##").alias("drug_id")).dicts()\
            #     .join(CanisterMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
            #     .where(CanisterMaster.id << canister_list)

            # for record in fndc_txr_with_given_canister:
            #     fndc_txr_set.add(record["drug_id"])

            select_fields_for_query_1 = [fn.COUNT(fn.DISTINCT(PackAnalysisDetails.canister_id)).alias("canister_count"),
                                         fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysisDetails.canister_id)).alias("canisters"),
                                         fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysisDetails.status)).alias("status"),
                                         DrugMaster.concated_fndc_txr_field(sep="##").alias("drug_id")
                                         ]

            fndc_txr_with_pack_analysis_details = (CanisterMaster.select(*select_fields_for_query_1)
                                                   .dicts()
                                                   .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)
                                                   .join(PackAnalysisDetails, on=CanisterMaster.id == PackAnalysisDetails.canister_id)
                                                   .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)
                                                   .where((PackAnalysisDetails.device_id == device_id) &
                                                          (PackAnalysis.batch_id == batch_id))
                                                   .group_by(DrugMaster.concated_fndc_txr_field(sep="##"))
                                                   # .having(SQL("canister_count > 1"))
                                                   )

            for record in fndc_txr_with_pack_analysis_details:
                canister_list = list(map(int, record["canisters"].split(",")))
                status_list = list(map(int, record["status"].split(",")))

                if len(canister_list) > 1 and constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED in status_list:
                    fndc_txr_set.add(record["drug_id"])
                else:
                    if record["drug_id"] not in canister_status_dict:
                        canister_status_dict[record["drug_id"]] = dict()
                        canister_status_dict[record["drug_id"]]["canister_ids"] = set()
                        canister_status_dict[record["drug_id"]]["status"] = set()

                    canister_status_dict[record["drug_id"]]["canister_ids"].update(set(canister_list))
                    canister_status_dict[record["drug_id"]]["status"].update(set(status_list))

            logger.info("In get_nx_canister_drug_with_location_for_given_drugs: canister_status_dict: {}"
                        .format(canister_status_dict))

            select_fields_for_query_2 = [fn.COUNT(fn.DISTINCT(ReplenishSkippedCanister.canister_id)).alias("canister_count"),
                                         fn.GROUP_CONCAT(fn.DISTINCT(ReplenishSkippedCanister.canister_id)).alias("canisters"),
                                         DrugMaster.concated_fndc_txr_field(sep="##").alias("drug_id")
                                         ]

            fndc_txr_with_replenish_skipped_canister = (CanisterMaster.select(*select_fields_for_query_2)
                                                        .dicts()
                                                        .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)
                                                        .join(ReplenishSkippedCanister, on=CanisterMaster.id == ReplenishSkippedCanister.canister_id)
                                                        .join(PackDetails, on=PackDetails.id == ReplenishSkippedCanister.pack_id)
                                                        .where((ReplenishSkippedCanister.device_id == device_id) &
                                                               (PackDetails.batch_id == batch_id)
                                                               )
                                                        .group_by(DrugMaster.concated_fndc_txr_field(sep="##"))
                                                        # .having(SQL("canister_count > 1"))
                                                        )

            for record in fndc_txr_with_replenish_skipped_canister:
                canister_list = list(map(int, record["canisters"].split(",")))

                if len(canister_list) > 1:
                    if (record["drug_id"] in canister_status_dict
                            and constants.REPLENISH_CANISTER_TRANSFER_SKIPPED not in canister_status_dict[
                                record["drug_id"]]["status"]):
                        fndc_txr_set.add(record["drug_id"])

                    elif (record["drug_id"] in canister_status_dict
                          and constants.REPLENISH_CANISTER_TRANSFER_SKIPPED in canister_status_dict[
                              record["drug_id"]]["status"]
                          and len(canister_status_dict[record["drug_id"]]["status"]) == 1):
                        skip_canister = set(canister_list) - canister_status_dict[record["drug_id"]]["canister_ids"]
                        for canister in skip_canister:
                            skipped_canister_list.append(canister)

                else:
                    if (record["drug_id"] in canister_status_dict
                            and constants.REPLENISH_CANISTER_TRANSFER_SKIPPED not in canister_status_dict[
                                record["drug_id"]]["status"]):
                        fndc_txr_set.add(record["drug_id"])

            if fndc_txr_set and not mfd_data:
                skipped_canister = ReplenishSkippedCanister.select(ReplenishSkippedCanister.canister_id).dicts() \
                    .join(CanisterMaster, on=CanisterMaster.id == ReplenishSkippedCanister.canister_id) \
                    .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
                    .join(PackDetails, on=PackDetails.id == ReplenishSkippedCanister.pack_id)\
                    .where((PackDetails.batch_id == batch_id) &
                           (DrugMaster.concated_fndc_txr_field(sep="##") << list(fndc_txr_set)) &
                           (PackDetails.pack_status == settings.PENDING_PACK_STATUS)
                           )\
                    .group_by(ReplenishSkippedCanister.canister_id)

                for record in skipped_canister:
                    if record["canister_id"] not in skipped_canister_list:
                        skipped_canister_list.append(record["canister_id"])

            logger.info("In get_nx_canister_drug_with_location_for_given_drugs: skipped_canister_list: {}".
                        format(skipped_canister_list))

        query = CanisterMaster.select(DrugMaster.concated_fndc_txr_field(sep="##").alias("drug"),
                                      DrugMaster.id.alias('canister_drug_id'),
                                      CanisterMaster.id, LocationMaster.location_number,
                                      CanisterMaster.canister_type,
                                      LocationMaster.device_id, LocationMaster.quadrant) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(DrugMaster.concated_fndc_txr_field(sep="##") << drug_list,
                   CanisterMaster.active == settings.is_canister_active)

        if skipped_canister_list:
            query = query.where(CanisterMaster.id.not_in(skipped_canister_list))

        query = query.order_by(CanisterMaster.available_quantity)
        mfd_canister_data = ()
        if mfd_data:

            mfd_query = (MfdAnalysisDetails.select(MfdAnalysis.dest_device_id,
                                                   MfdAnalysis.dest_quadrant,
                                                   CanisterMaster.location_id,
                                                   CanisterMaster.id.alias("canister_id"))
                         .join(MfdAnalysis, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id)
                         .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)
                         .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                         .join(CanisterMaster, on=CanisterMaster.drug_id == DrugMaster.id)
                         .where(MfdAnalysis.batch_id == batch_id,
                                DrugMaster.id == drug_id,
                                MfdAnalysis.dest_device_id == device_id))
            for record in mfd_query.dicts():
                mfd_canister_data = (record['dest_device_id'], record['dest_quadrant'], record['location_id'],
                                     record['canister_id'])

        for record in query.dicts():

            if record['id'] in can_reserved_device and can_reserved_device[record['id']]["device_id"] == device_id:
                drug_travelled.append(record["drug"])
                canister_location_number[record['id']] = can_reserved_device[record['id']]["location_number"]
                quadrant = can_reserved_device[record['id']]["quadrant"]
                robot_quadrant_drug_data[device_id][quadrant]["drugs"].add(record["drug"])
                canister_drugs_set.add(record["drug"])

                if record["drug"] not in robot_quadrant_drug_canister_info_dict[device_id][record['quadrant']].keys():
                    robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]] = list()

                robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]].append(
                    record["id"])

            elif record['id'] not in can_reserved_device and record['device_id'] == device_id:
                quadrant = record['quadrant']
                drug_travelled.append(record["drug"])
                canister_location_number[record['id']] = record['location_number']
                robot_quadrant_drug_data[device_id][quadrant]["drugs"].add(record["drug"])
                if record["drug"] not in robot_quadrant_drug_canister_info_dict[device_id][record['quadrant']].keys():
                    robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]] = list()

                robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]].append(
                    record["id"])
                canister_drugs_set.add(record["drug"])

            elif (record['id'] in can_reserved_device
                  and device_id in can_reserved_device_all_data[record['id']].keys()):
                quadrant = can_reserved_device_all_data[record['id']][device_id]["quadrant"]
                drug_travelled.append(record["drug"])
                canister_location_number[record['id']] = can_reserved_device_all_data[record['id']][device_id]["location_number"]
                robot_quadrant_drug_data[device_id][quadrant]["drugs"].add(record["drug"])
                if record["drug"] not in robot_quadrant_drug_canister_info_dict[device_id][quadrant].keys():
                    robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]] = list()

                robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]].append(
                    record["id"])
                canister_drugs_set.add(record["drug"])

            elif mfd_data and drug_id == record["canister_drug_id"] and record['id'] in canister_ids:
                if record['id'] in can_reserved_device_all_data.keys() and device_id not in can_reserved_device_all_data[record['id']].keys():
                    continue
                quadrant = mfd_canister_data[1]
                device_id = mfd_canister_data[0]
                drug_travelled.append(record["drug"])
                canister_location_number[record['id']] = mfd_canister_data[2]
                robot_quadrant_drug_data[ device_id][quadrant]["drugs"].add(record["drug"])
                if record["drug"] not in robot_quadrant_drug_canister_info_dict[device_id][quadrant].keys():
                    robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]] = list()

                robot_quadrant_drug_canister_info_dict[device_id][quadrant][record["drug"]].append(
                    record["id"])
                canister_drugs_set.add(record["drug"])


        for record in query.dicts():
            if record['id'] not in can_reserved_device.keys() and record["drug"] not in drug_travelled:
                    if record["drug"] not in remaining_drug_canister_location_dict:
                        remaining_drug_canister_location_dict[record["drug"]] = list()

                    remaining_drug_canister_location_dict[record["drug"]].append({"device_id": record["device_id"],
                                                                                  "canister_id": record["id"],
                                                                                  "canister_type": record["canister_type"]})

        return robot_quadrant_drug_data, remaining_drug_canister_location_dict, \
               robot_quadrant_drug_canister_info_dict, canister_location_number, canister_drugs_set

    except (InternalError, IntegrityError, DataError, DoesNotExist, ValueError) as e:
        logger.error("Error in get_nx_canister_drug_with_location_for_given_drugs {}".format(e))
        raise
    except Exception as e:
        logger.error("Exception in get_pack_slotwise_canister_drugs_ {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Exception in get_nx_canister_drug_with_location_for_given_drugs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


def get_mfd_drawer_location_info(device_list):
    """
    Function to get mfd drawer location info device wise considering
    only active locations
    @param device_list: list
    @return:
    """
    device_quad_loc_info = list()
    try:
        query = LocationMaster.select(LocationMaster.device_id, LocationMaster.quadrant,
                                      LocationMaster.id.alias('location_id'),
                                      LocationMaster.display_location.alias('dest_display_location'),
                                      LocationMaster.container_id.alias('dest_drawer_id')
                                      ).dicts() \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .where(LocationMaster.device_id << device_list,
                   ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE["MFD"]],
                   MfdCanisterMaster.id.is_null(True)
                   ) \

        for record in query:
            device_quad_loc_info.append(record)

        return device_quad_loc_info

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_mfd_drawer_quad_capacity_count".format(e))
        raise


def db_get_empty_enabled_location_on_robot(device_id, disable_include):
    """
    Function to get empty enabled location on robot
    @return:
    """
    robot_empty_enabled_loc_info = list()
    location_info = list()
    try:
        clauses = list()

        subquery2 = LocationMaster.select(LocationMaster.id).where(LocationMaster.display_location.startswith("M"))

        if disable_include == 0:
            clauses.append((LocationMaster.is_disabled == False))

        clauses.append((LocationMaster.id.not_in(location_info)))
        clauses.append((LocationMaster.device_id == device_id))
        clauses.append((LocationMaster.id.not_in(subquery2)))

        subquery = CanisterMaster.select(CanisterMaster.location_id).dicts() \
            .where(CanisterMaster.active == 1 and CanisterMaster.location_id.is_null(False))

        for record in subquery:
            location_info.append(record["location_id"])

        query = LocationMaster.select(LocationMaster.id.alias("empty_location_id"), LocationMaster.device_id).dicts() \
            .where(functools.reduce(operator.and_, clauses))

        for record in query:
            robot_empty_enabled_loc_info.append(record)

        return robot_empty_enabled_loc_info

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_mfd_drawer_quad_capacity_count".format(e))
        raise


@log_args_and_response
def db_get_device_data_by_type(device_type_id, system_id):
    device_data = []
    try:
        for record in DeviceMaster.select(DeviceMaster).dicts() \
                .where(DeviceMaster.device_type_id == device_type_id, DeviceMaster.system_id == system_id,
                       DeviceMaster.active == 1) \
                .order_by(DeviceMaster.id):
            device_data.append(record)
        return device_data

    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_get_device_data_by_type".format(e))
        raise

    except DoesNotExist as e:
        logger.error("Error in db_get_device_data_by_type".format(e))
        return device_data


@log_args_and_response
def db_get_in_robot_mfd_trolley(system_id):
    trolley_ids = []
    try:

        query = LocationMaster.select(MfdCanisterMaster.home_cart_id).dicts()\
            .join(MfdCanisterMaster, on=MfdCanisterMaster.location_id == LocationMaster.id).group_by(MfdCanisterMaster.home_cart_id)
        trolley_ids = [int(record['home_cart_id']) for record in query]
        return trolley_ids

    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_get_device_data_by_type".format(e))
        return trolley_ids

    except DoesNotExist as e:
        logger.error("Error in db_get_device_data_by_type".format(e))
        return trolley_ids



