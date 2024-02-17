import functools
import operator
from peewee import InternalError, IntegrityError, DataError, DoesNotExist, JOIN_LEFT_OUTER, fn

import settings
from dosepack.utilities.utils import log_args_and_response
from src.constants import STATION_ID_MAX_LENGTH
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_canister_master import CanisterMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src.api_utility import get_filters
from src.model.model_container_master import ContainerMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_location_master import LocationMaster

logger = settings.logger


def validate_drawer_name(drawer_name: str, device_id: int) -> bool:
    """
    This function validates if the drawer_name belongs to the given device.
    @param drawer_name:
    @param device_id:
    @return:
    """

    return ContainerMaster.db_verify_drawer_name_by_device(drawer_name=drawer_name, device_id=device_id)


def get_container_id(drawer_name_list: list, device_id: int) -> list:
    """
    get the container_id for the given drawer_name and device_id
    @param drawer_name_list: list
    @param device_id:int
    @return: int
    """
    try:
        container_id_list = ContainerMaster.get_container_id_from_drawer_name_and_device_id(
            drawer_name_list=drawer_name_list,
            device_id=device_id)
        logger.info(
container_id_list)
        return container_id_list
    except (DoesNotExist, DataError, IntegrityError, InternalError) as e:
        logger.error("Error in get_container_id: {}".format(e))
        raise


def get_csr_filters_data(device_id: int, company_id: int) -> dict:
    """
    This function fetches all the filter values for the given CSR device in the given company.
    @param device_id:
    @param company_id:
    @return:
    """

    try:
        # get the unique drawer ids for the given device_id.
        unique_drawer_names = ContainerMaster.get_unique_drawer_name(device_id=device_id)

        # get the unique shelf values for the given device_id.
        unique_shelf_values = ContainerMaster.get_unique_shelf_values(device_id=device_id)

        # get the unique drawer types for the given device_id.
        unique_drawer_types = ContainerMaster.get_unique_drawer_types(device_id=device_id)

        # get the unique drawer sizes for the given device_id.
        unique_drawer_sizes = ContainerMaster.get_unique_drawer_sizes(device_id=device_id)

        # get the unique canister types for the given company_id.
        unique_canister_types = get_unique_canister_types(company_id=company_id)

        # get the unique canister sized for the given company_id.
        unique_canister_sizes = get_unique_canister_sizes(company_id=company_id)

        # creating the response dictionary
        response_dict = {
            "unique_drawer_names": unique_drawer_names,
            "unique_shelf_values": unique_shelf_values,
            "unique_drawer_types": unique_drawer_types,
            "unique_drawer_sizes": unique_drawer_sizes,
            "unique_canister_types": unique_canister_types,
            "unique_canister_sizes": unique_canister_sizes
        }

        return response_dict

    except (DoesNotExist, DataError, IntegrityError, InternalError) as e:
        logger.error("Error in get_csr_filters_data: {}".format(e))
        raise


def get_unique_canister_types(company_id: int) -> list:
    """
    Fetches all the unique canister type for the given company id.
    @return:
    """
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
        logger.error("Error in get_unique_canister_types: {}".format(e))
        raise e


def get_unique_canister_sizes(company_id: int) -> list:
    """
    Fetches all the unique canister size for the given company id.
    @return:
    """
    try:
        query = CanisterMaster.select(fn.DISTINCT(CanisterMaster.canister_type).alias("unique_canister_sizes")).dicts() \
            .where(CanisterMaster.company_id == company_id).order_by(CanisterMaster.id)
        response_list = []
        for record in query:
            response_list.append(record["unique_canister_sizes"])
        return response_list
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_unique_canister_sizes: {}".format(e))
        raise e


def get_csr_drawer_details(container_id_list: list, filter_fields: dict = dict) -> list:
    """
    get the details of canister placed in the given drawer.
    @param filter_fields: list
    @param container_id_list:list
    @return:
    """
    clauses = [[ContainerMaster.id << container_id_list]]
    fields_dict = {
        "display_locations": LocationMaster.display_location
    }
    membership_search_list = ["display_locations"]
    clauses = get_filters(clauses, fields_dict, filter_fields,
                          membership_search_fields=membership_search_list)

    try:
        query = ContainerMaster.select(ContainerMaster.drawer_name,
                                       LocationMaster.id.alias("location_id"),
                                       LocationMaster.display_location,
                                       LocationMaster.is_disabled.alias("disabled_location"),
                                       CanisterMaster.id.alias("canister_id"),
                                       CanisterMaster.available_quantity.alias("quantity"),
                                       CanisterMaster.rfid.alias("electronic_id"),
                                       DrugMaster.ndc,
                                       UniqueDrug.drug_usage.alias('canister_type'),
                                       DrugMaster.concated_drug_name_field(include_ndc=False).alias("drug_name")) \
            .dicts() \
            .join(LocationMaster, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(DrugMaster, JOIN_LEFT_OUTER, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                                   (DrugMaster.txr == UniqueDrug.txr)))
        logger.info(query)

        # location level search where output filtered upon display_locations
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
            logger.info(query)
        response_list = []
        for record in query:
            response_list.append(record)

        return response_list

    except (DoesNotExist, DataError, IntegrityError, InternalError) as e:
        logger.error("Error in get_csr_drawer_details: {}".format(e))
        raise


@log_args_and_response
def get_canister_size_and_type(canister_id: int) -> dict:
    """
    Fetch the canister data for the given canister_id
    @param canister_id:
    @return:
    """
    try:
        canister_id_list = [canister_id]
        response = get_canister_usage_and_type(canister_list=canister_id_list)
        response_dict = dict()

        if len(response):
            response_dict["canister_size"] = response[canister_id]["canister_type"]
            response_dict["canister_type"] = response[canister_id]["canister_usage"]

        return response_dict

    except (DoesNotExist, DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_canister_size_and_type: {}".format(e))
        raise


def get_canister_usage_and_type(canister_list: list) -> dict:
    """
    Fetches all the unique canister type for the given company id.
    @return:
    """
    try:
        query = CanisterMaster.select(CanisterMaster.id, CanisterMaster.canister_type,
                                      UniqueDrug.drug_usage).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .where(CanisterMaster.id << canister_list) \
            .group_by(CanisterMaster.id)

        response_dict = dict()
        for record in query:
            response_dict[record['id']] = {"canister_type": record['canister_type'],
                                           "canister_usage": record['drug_usage']}
        return response_dict
    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_canister_usage_and_type: {}".format(e))
        raise


def update_canister_master(location_id, canister_id):
    dict = {"location_id": location_id}
    res = CanisterMaster.update_canister(dict, canister_id)
    return res


@log_args_and_response
def get_empty_location_for_given_canister(size_key: int, usage_key: int, device_id: int,
                                          reserved_location_list: list) -> dict:
    """
    Fetches one bottom most and left most available empty location from the given device_id based on the size_key and usage.
    @param reserved_location_list:
    @param size_key:
    @param usage_key:
    @param device_id:
    @return:
    """
    try:
        """ TODO: ContainerMaster.drawer_usage == usage_key,  
        removed this as for now we need only nearest location and not on the base of its usage"""

        clauses = [ContainerMaster.device_id == device_id, ContainerMaster.drawer_type == size_key,
                   LocationMaster.is_disabled == False, CanisterMaster.id.is_null(True)]

        if len(reserved_location_list):
            clauses.append(LocationMaster.id.not_in(reserved_location_list))

        query1 = ContainerMaster.select(LocationMaster.display_location,
                                        LocationMaster.id.alias('location_id'),
                                        LocationMaster.container_id,
                                        ContainerMaster.drawer_name,
                                        ContainerMaster.ip_address,
                                        ContainerMaster.secondary_ip_address,
                                        ContainerMaster.shelf,
                                        ContainerMaster.serial_number,
                                        ContainerMaster.ip_address,
                                        ContainerMaster.secondary_ip_address
                                        ) \
            .dicts() \
            .join(LocationMaster, on=LocationMaster.container_id == ContainerMaster.id, ) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .where(*clauses) \
            .order_by(LocationMaster.location_number) \
            .limit(1)

        for record in query1:
            return record
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_empty_location_for_given_canister: {}".format(e))
        raise e


@log_args_and_response
def get_top_drawer_empty_location_for_given_canister(size_key: list, device_id: int,
                                                     reserved_location_list: list):
    """
    Fetches one bottom most and left most available empty location from the given device_id based on the size_key and usage.
    @param reserved_location_list:
    @param size_key:
    @param device_id:
    @return:
    """
    try:
        clauses = [ContainerMaster.device_id == device_id,
                   ContainerMaster.drawer_type << size_key,
                   LocationMaster.is_disabled == False, CanisterMaster.id.is_null(True)]

        if len(reserved_location_list):
            clauses.append(LocationMaster.id.not_in(reserved_location_list))

        query1 = ContainerMaster.select(LocationMaster.display_location,
                                        LocationMaster.id.alias('location_id'),
                                        LocationMaster.container_id,
                                        ContainerMaster.drawer_name,
                                        ContainerMaster.ip_address,
                                        ContainerMaster.secondary_ip_address,
                                        ContainerMaster.shelf,
                                        ContainerMaster.serial_number,
                                        ContainerMaster.ip_address,
                                        ContainerMaster.secondary_ip_address,
                                        DeviceMaster.name.alias('device_name')
                                        ) \
            .dicts() \
            .join(LocationMaster, on=LocationMaster.container_id == ContainerMaster.id, ) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(*clauses) \
            .order_by(LocationMaster.id.desc()) \
            .limit(1)

        for record in query1:
            return record

        return None

    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("Error in get_top_drawer_empty_location_for_given_canister: {}".format(e))
        raise e


def db_get_locations_count_of_device(location_id_list: list, disabled_locations: bool,
                                     empty_locations: bool, active_locations: bool) -> dict:
    """
    Method to get locations count of devices based on type
    @param location_id_list: list of location_ids
    @param disabled_locations: True- if you need disabled_locations count else False
    @param empty_locations: True- if you need empty_locations count else False
    @param active_locations: True- if you need active_locations count else False
    @return: return dict with device id and given location type as keys
    """
    locations_count_dict = dict()
    try:
        logger.info("In db_get_locations_count_of_device")
        # to count the number of disabled_locations for provided location_id_list
        if disabled_locations:
            disabled_loc_count_query = LocationMaster.select(
                fn.COUNT(LocationMaster.id).alias('disabled_locations_count')).dicts() \
                .where((LocationMaster.id << location_id_list), (LocationMaster.is_disabled == True))

            for record in disabled_loc_count_query:
                locations_count_dict["disabled_locations_count"] = record["disabled_locations_count"]

        # to count the number of empty_locations for provided location_id_list
        if empty_locations:
            empty_loc_count_query = LocationMaster.select(
                fn.COUNT(LocationMaster.id).alias("empty_locations_count")).dicts() \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .where((LocationMaster.id << location_id_list), (CanisterMaster.location_id.is_null(True)))

            for record in empty_loc_count_query:
                locations_count_dict["empty_locations_count"] = record["empty_locations_count"]

        # to count the number of active_locations for provided location_id_list
        if active_locations:
            active_loc_count_query = LocationMaster.select(
                fn.COUNT(LocationMaster.id).alias("active_locations_count")).dicts() \
                .where((LocationMaster.id << location_id_list), (LocationMaster.is_disabled == False))

            for record in active_loc_count_query:
                locations_count_dict["active_locations_count"] = record["active_locations_count"]

        logger.info(locations_count_dict)
        return locations_count_dict

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("Error in db_get_locations_count_of_device: {}".format(e))
        raise e


def csr_location_rfid_changed(location, rfid, device_id, zone_id=None, user_id=None):
    zone_ids = list(map(lambda x: int(x), zone_id.split(','))) if (zone_id is not None) else None

    try:
        # Sub query to find the location id of the csr location.
        sub_query = LocationMaster.select(LocationMaster.id).dicts() \
            .where(LocationMaster.device_id == device_id, LocationMaster.location_number == location).get()

        # update query to update the location id of the canister which was present here.a
        location_id = sub_query['id']
        try:
            update_query = CanisterMaster.update(location_id=None) \
                .where(CanisterMaster.location_id == location_id).execute()
            logger.info("In csr_location_rfid_changed: location updated: {}".format(update_query))
        except DoesNotExist as e:
            # This indicates that this location was not assigned to any of the canister before.
            logger.info("In csr_location_rfid_changed: this location was not assigned to any of the canister before: {}".format(e))
            pass

        # update query to update the location id of the canister having new rfid.
        if rfid != settings.NULL_RFID_CSR:
            # This means that there is a canister present at that location.
            new_location_update_query = CanisterMaster.update(location_id=location_id) \
                .where(CanisterMaster.rfid == rfid).execute()
            logger.info("In csr_location_rfid_changed: location updated : {} for rfid: {}".format(new_location_update_query, rfid))
            if zone_ids is not None and user_id is not None:
                CanisterZoneMapping.update_canister_zone_mapping_by_rfid(zone_ids, user_id, rfid)

        # Possible exceptions in these functions are following:
        # 1. We will not get the location id for the given location in the first query then we will get key error in
        # below queries.
        # 2. DoesNotExist in second query which is handled.
        # 3. Canister rfid doesn't exist in third query.
        return True
    except DoesNotExist as e:
        logger.error("Error in csr_location_rfid_changed: {}".format(e))
        raise e
    except IntegrityError as e:
        logger.error("Error in csr_location_rfid_changed: {}".format(e))
        raise e
    except InternalError as e:
        logger.error("Error in csr_location_rfid_changed: {}".format(e))
        raise e
    except DataError as e:
        logger.error("Error in csr_location_rfid_changed: {}".format(e))
        raise e


def get_serial_number_by_station_type_and_id(station_type: int, station_id: str, container_serial_number: bool,
                                             device_serial_number: bool) -> str:
    """
    Method to generate serial number based on station_type and station_id
    @param station_type: Type of station like 81 for csr
    @param station_id: id of station
    @param container_serial_number: True if it wants serial number of container else False
    @param device_serial_number: True if it wants serial number of device else False
    @return: serial number
    """
    try:
        # station type must be pre-defined in CONTAINER_SERIAL_NUMBER_SERIES_DICT or CONTAINER_SERIAL_NUMBER_SERIES_DICT
        data = DeviceTypeMaster.get_code_by_station_type_id(station_type_id=station_type)
        if container_serial_number:
            serial_number_series = data["container_code"]
        elif device_serial_number:
            serial_number_series = data["device_code"]
        else:
            raise ValueError("Any one of container_serial_number or device_serial_number must be true")

        while len(station_id) < STATION_ID_MAX_LENGTH:
            station_id = '0' + station_id

        serial_number = str(serial_number_series) + str(station_id)
        return serial_number
    except (KeyError, ValueError) as e:
        logger.error("Error in get_serial_number_by_station_type_and_id: {}".format(e))
        raise e
