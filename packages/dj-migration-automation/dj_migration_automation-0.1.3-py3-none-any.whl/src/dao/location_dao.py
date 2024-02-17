from collections import OrderedDict
from typing import Any, Dict

from peewee import InternalError, IntegrityError, JOIN_LEFT_OUTER, fn

import settings
from dosepack.utilities.utils import log_args_and_response
from src.dao.device_manager_dao import get_disabled_locations_of_devices
from src.model.model_canister_master import CanisterMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_canister_master import MfdCanisterMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails

logger = settings.logger


@log_args_and_response
def get_location_number_from_display_location_dao(device_id, display_location):
    try:
        return LocationMaster.get_location_number_from_display_location(device_id=device_id,
                                                                        display_location=display_location)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_location_number_from_display_location_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_empty_locations_dao(company_id, is_mfd, device_id, quadrant, device_type_id, system_id, drawer_number):
    response_dict: Dict[str, Any] = dict()

    try:
        empty_locations = LocationMaster.select(LocationMaster,
                                                ContainerMaster.ip_address,
                                                ContainerMaster.secondary_ip_address,
                                                ContainerMaster.mac_address,
                                                ContainerMaster.secondary_mac_address,
                                                ContainerMaster.serial_number,
                                                DeviceMaster.name.alias("device_name"),
                                                DeviceMaster.device_type_id,
                                                ContainerMaster.drawer_name.alias('drawer_number')).dicts() \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=((CanisterMaster.location_id == LocationMaster.id) &
                                                       (CanisterMaster.company_id == company_id))) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=((MfdCanisterMaster.location_id == LocationMaster.id) &
                                                          (MfdCanisterMaster.company_id == company_id))) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id)
        if is_mfd:
            empty_locations = empty_locations.where(MfdCanisterMaster.id.is_null(True),
                                                    ContainerMaster.drawer_type == settings.SIZE_OR_TYPE['MFD'])
        else:
            empty_locations = empty_locations.where(CanisterMaster.id.is_null(True),
                                                    ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['BIG'],
                                                                                    settings.SIZE_OR_TYPE['SMALL']])
        # to find empty locations for the given device_id and company_id
        if device_id:
            empty_locations = empty_locations.where(LocationMaster.device_id == device_id)
        if quadrant:
            empty_locations = empty_locations.where(LocationMaster.quadrant == quadrant)
        if device_type_id:
            empty_locations = empty_locations.where(DeviceMaster.device_type_id == device_type_id,
                                                    DeviceMaster.system_id == system_id)

        if drawer_number:
            empty_locations = empty_locations.where(ContainerMaster.drawer_name << drawer_number)
        empty_locations = empty_locations.order_by(LocationMaster.location_number)

        # create the response dict with keeping drawer_number as the key
        for record in empty_locations:
            if record["drawer_number"] not in response_dict.keys():
                response_dict[record["drawer_number"]] = []
                response_dict[record["drawer_number"]].append(record)
            else:
                response_dict[record["drawer_number"]].append(record)

        return response_dict
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_empty_locations_dao {}".format(e))
        raise e


@log_args_and_response
def get_all_location_info(device_id: int) -> tuple:
    try:
        # drug_ids = set()
        # canister_ids = []
        quad_canisters = {}
        canister_drug_info_dict = {}
        quad_drug_canister_dict = {}
        query = CanisterMaster.select(
            fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias('drug'),
            fn.CONCAT(DrugMaster.drug_name, ' ', DrugMaster.strength_value, ' ', DrugMaster.strength).alias(
                'drug_name'),
            DrugMaster.strength,
            DrugMaster.ndc,
            CanisterMaster.id,
            LocationMaster.quadrant
        ).join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(CanisterMaster.location_id.is_null(False), LocationMaster.device_id == device_id)

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
        logger.debug(quad_drug_canister_dict)
        logger.debug(quad_canisters)
        logger.debug(canister_drug_info_dict)
        return quad_drug_canister_dict, quad_canisters, canister_drug_info_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_disabled_location_info_by_canister_ids(canister_ids: list, batch_id: int) -> tuple:
    logger.debug("In get_disabled_location_info")
    try:
        # drug_ids = set()
        # disable_location_canister_ids = []
        quad_canisters = {}
        quad_drug_canister_dict = OrderedDict()

        query = PackAnalysis.select(PackAnalysisDetails.canister_id,
                                    fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias('drug'),
                                    PackAnalysisDetails.quadrant)\
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(CanisterMaster, on=PackAnalysisDetails.canister_id == CanisterMaster.id) \
            .join(PackDetails, on=((PackDetails.id == PackAnalysis.pack_id) &
                                   (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
            .where(PackAnalysisDetails.canister_id << canister_ids,
                   PackAnalysis.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS,
                                               settings.PROGRESS_PACK_STATUS])

        for record in query.dicts():
            if record['quadrant'] not in quad_canisters:
                quad_canisters[record['quadrant']] = set()
            if record['quadrant'] not in quad_drug_canister_dict:
                quad_drug_canister_dict[record['quadrant']] = OrderedDict()
            if record['drug'] not in quad_drug_canister_dict[record['quadrant']]:
                quad_drug_canister_dict[record['quadrant']][record['drug']] = set()
            quad_drug_canister_dict[record['quadrant']][record['drug']] = record['canister_id']
            quad_canisters[record['quadrant']].add(record['canister_id'])
        return quad_drug_canister_dict, quad_canisters
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_disabled_location_info_by_display_location(display_locations: list, batch_id: int, device_id: int,
                                                   quad_drug_canister_dict: OrderedDict, quad_canisters: dict) -> tuple:
    logger.debug("In get_disabled_location_info")
    try:
        query = PackAnalysis.select(PackAnalysisDetails.canister_id,
                                    fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias('drug'),
                                    PackAnalysisDetails.quadrant)\
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(CanisterMaster, on=PackAnalysisDetails.canister_id == CanisterMaster.id) \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(PackDetails, on=((PackDetails.id == PackAnalysis.pack_id) &
                                   (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
            .where(LocationMaster.display_location << display_locations,
                   LocationMaster.device_id == device_id,
                   PackAnalysis.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS,
                                               settings.PROGRESS_PACK_STATUS])

        for record in query.dicts():
            if record['quadrant'] not in quad_canisters:
                quad_canisters[record['quadrant']] = set()
            if record['quadrant'] not in quad_drug_canister_dict:
                quad_drug_canister_dict[record['quadrant']] = OrderedDict()
            if record['drug'] not in quad_drug_canister_dict[record['quadrant']]:
                quad_drug_canister_dict[record['quadrant']][record['drug']] = set()
            quad_drug_canister_dict[record['quadrant']][record['drug']] = record['canister_id']
            quad_canisters[record['quadrant']].add(record['canister_id'])
        return quad_drug_canister_dict, quad_canisters
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_quad_wise_location_info(location_ids) -> tuple:
    try:
        quad_location_info_dict = {}
        location_data = {}
        for quad in settings.TOTAL_QUADRANTS:
            quad_location_info_dict[quad] = {'display_location': list(), 'location_number': list(),
                                             'location_id': list()}
        if location_ids:
            query = LocationMaster.select(LocationMaster.id, LocationMaster.quadrant, LocationMaster.device_id,
                                          LocationMaster.display_location, LocationMaster.location_number) \
                .where(LocationMaster.id << list(location_ids)).order_by(LocationMaster.id.desc())
            for record in query.dicts():
                if record['quadrant'] not in quad_location_info_dict:
                    quad_location_info_dict[record['quadrant']] = {'display_location': list(),
                                                                   'location_number': list(),
                                                                   'location_id': list()}
                quad_location_info_dict[record['quadrant']]['display_location'].append(record['display_location'])
                quad_location_info_dict[record['quadrant']]['location_number'].append(record['location_number'])
                quad_location_info_dict[record['quadrant']]['location_id'].append(record['id'])
                location_data[record['id']] = {'display_location': record['display_location'],
                                               'location_number': record['location_number'],
                                               'quadrant': record['quadrant']}
            #
            # for quad,empty_loc in quad_location_info_dict.items():
            #     if empty_loc['display_location']:
            #         quad_location_info_dict[quad]['display_location'] = sorted(empty_loc['display_location'],reverse=True)

        return quad_location_info_dict, location_data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_empty_locations_by_device(device_id, reserved_location_ids):
    try:
        total_location_ids = LocationMaster.get_location_ids_from_device_id(device_id)
        robot_disabled_locations = {record["id"] for record in
                                    LocationMaster.db_get_disabled_locations_of_devices(device_ids=[device_id])}
        # robot_disabled_locations = get_disabled_location_for_device(device_id)
        empty_locations = set(total_location_ids) - set(reserved_location_ids) - set(robot_disabled_locations)
        return empty_locations, robot_disabled_locations
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_mfd_cart_empty_location_details_at_lower_drawer():
    """
    @return: query results
    """
    try:
        subquery = MfdCanisterMaster.select(MfdCanisterMaster.location_id.alias('mfd_canister_placed_location_id')) \
            .join(LocationMaster, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id).where(ContainerMaster.drawer_level <<
                                                                                      (1,2,3,4),
                                                                                      LocationMaster.device_id.between(13, 22))

        query = LocationMaster.select(LocationMaster.id.alias('empty_location_id'),
                                         LocationMaster.device_id.alias('empty_location_cart_id'),
                                        ContainerMaster.drawer_level.alias("empty_drawer_level")) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id).where(LocationMaster.id.not_in(subquery),
                                                                                      LocationMaster.device_id.between(13, 22)
                                                                                       , ContainerMaster.drawer_level << (1,2,3,4))

        mfd_canister_details_list = list()

        for record in query.dicts():
            mfd_canister_details_list.append(record)

        return mfd_canister_details_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e