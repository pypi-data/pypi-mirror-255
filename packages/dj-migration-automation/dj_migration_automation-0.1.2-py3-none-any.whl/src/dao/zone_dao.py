from typing import List

from peewee import IntegrityError, DataError, InternalError, DoesNotExist, fn

import settings
from dosepack.utilities.utils import log_args_and_response
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.dao.canister_testing_dao import logger
from src.model.model_container_master import ContainerMaster
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_unit_conversion import UnitConversion
from src.model.model_unit_master import UnitMaster
from src.model.model_zone_master import ZoneMaster


logger = settings.logger
from src.model.model_zone_master import ZoneMaster


@log_args_and_response
def get_zone_by_device_id(device_id, company_id):
    """
    To get the device details from device_id (Foreign Key of DeviceMaster).
    @param device_id:
    @param company_id:
    :return:
    """
    try:
        query = DeviceLayoutDetails.select(DeviceLayoutDetails,
                                           DeviceLayoutDetails.zone_id,
                                           DeviceMaster.device_type_id,
                                           DeviceMaster.serial_number,
                                           DeviceMaster.name,
                                           DeviceMaster.company_id).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == DeviceLayoutDetails.device_id) \
            .where(DeviceLayoutDetails.device_id == device_id,
                   DeviceMaster.company_id == company_id).get()
        property_name_value = 'drawer_initials_pattern'
        query[property_name_value] = None

        return query

    except IntegrityError as e:
        raise e
    except InternalError as e:
        raise e
    except DataError as e:
        raise e


@log_args_and_response
def db_create_canister_zone_mapping_dao(canister_master_id, zone_id, user_id):
    try:
        CanisterZoneMapping.db_create_canister_zone_mapping(canister_master_id, zone_id, user_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_canister_zone_mapping_insert_bulk_data_dao(insert_zone_data):
    try:
        return CanisterZoneMapping.db_canister_zone_mapping_insert_bulk_data(insert_zone_data=insert_zone_data)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_zone_wise_system_ids(system_id_list):
    try:
        zone_system_dict = {}
        query = DeviceMaster.select(ZoneMaster.id, DeviceMaster.system_id) \
            .join(DeviceLayoutDetails, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(ZoneMaster, on=ZoneMaster.id == DeviceLayoutDetails.zone_id).where(
            DeviceMaster.system_id << system_id_list)

        for record in query.dicts():
            if record['id'] not in zone_system_dict:
                zone_system_dict[record['id']] = []
            if record['system_id'] not in zone_system_dict[record['id']]:
                zone_system_dict[record['id']].append(record['system_id'])
        return zone_system_dict
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        print(e)
        raise


@log_args_and_response
def get_zone_wise_canister_drugs(company_id, zone_list):
    try:
        fndc_txrs = set()
        zone_canister_drug_dict = {}
        canister_drug_zone_dict = {}
        for zone in zone_list:
            zone_canister_drug_dict[zone] = set()
        query = CanisterMaster.select(
            fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, ''))
                .alias('fndc_txr'), CanisterZoneMapping.zone_id
        ) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(CanisterZoneMapping, on=CanisterMaster.id == CanisterZoneMapping.canister_id).where(
            CanisterMaster.company_id == company_id,
            CanisterMaster.active == settings.is_canister_active)
        for record in query.dicts():
            if record['fndc_txr'] not in canister_drug_zone_dict:
                canister_drug_zone_dict[record['fndc_txr']] = set()
            if record['zone_id'] not in zone_canister_drug_dict:
                zone_canister_drug_dict[record['zone_id']] = set()
            zone_canister_drug_dict[record['zone_id']].add(record['fndc_txr'])
            canister_drug_zone_dict[record['fndc_txr']].add(record['zone_id'])
            fndc_txrs.add(record['fndc_txr'])
        return zone_canister_drug_dict, canister_drug_zone_dict

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_zone_id_list_by_device_id_company_id(device_id: int, company_id: int) -> List[int]:
    """
    This function fetches the zone_id for the given device_id and the company_id
    @param device_id:
    @param company_id:
    @return:
    """
    zone_id_list: List[int] = list()
    try:
        query = DeviceLayoutDetails.select(DeviceLayoutDetails.zone_id).dicts() \
            .join(DeviceMaster, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .where(DeviceLayoutDetails.device_id == device_id, DeviceMaster.company_id == company_id)

        for record in query:
            zone_id_list.append(int(record["zone_id"]))

        return zone_id_list

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_zone_id_list_by_device_id_company_id {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_zone_id_list_by_device_id_company_id {}".format(e))
        raise e


@log_args_and_response
def create_zone_dao(zone_data):
    """
      Create record for the new zone entry.
     @param zone_data:
     @return:
    """
    try:
        data = ZoneMaster.create_zone(zone_data=zone_data)
        return data

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in create_zone_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in create_zone_dao {}".format(e))
        raise e


def validate_zone_id(zone_id, company_id):
    """
    validate zone id by company id
    @param zone_id:
    @param company_id:
    @return:
    """
    try:
        validation_status = ZoneMaster.verify_zone_id_for_company(company_id=company_id, zone_id=zone_id)
        return validation_status

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in validate_zone_id {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in validate_zone_id {}".format(e))
        raise e


def validate_device_layout_id_list(device_list, zone_id):
    """
    Helper function to validate whether device layout ids are present for a zone id.
    @param device_list:
    @param zone_id:
    @return:
    """
    try:
        device_layout_id_list = DeviceLayoutDetails.get_device_id_list_for_a_zone(zone_id=zone_id)
        for device in device_list:
            if device not in device_layout_id_list:
                return False
        return True

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in validate_device_layout_id_list {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in validate_device_layout_id_list {}".format(e))
        raise e


def transfer_device_from_zone_dao(zone_id: int, device_id_list: list, transfer_to_zone: int):
    """
    validate zone id by company id
    @param transfer_to_zone:
    @param device_id_list:
    @param zone_id:
    @return:
    """
    try:
        response = DeviceLayoutDetails.transfer_device_from_zone(zone_id=zone_id,
                                                                 device_id_list=device_id_list,
                                                                 transfer_to_zone=transfer_to_zone)
        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in transfer_device_from_zone_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in transfer_device_from_zone_dao {}".format(e))
        raise e


def remove_device_from_zone_dao(device_id_list):
    """
    validate zone id by company id
    @param device_id_list:
    @return:
    """
    try:
        response = DeviceLayoutDetails.remove_device_from_zone(device_id_list=device_id_list)
        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in remove_device_from_zone_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in remove_device_from_zone_dao {}".format(e))
        raise e


def update_zone_configuration_dao(zone_id, device_list):
    """
    update zone configuration
    @param zone_id:
    @param device_list:
    @return:
    """
    try:
        response = DeviceLayoutDetails.update_zone_configuration(zone_id=zone_id, device_list=device_list)
        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in update_zone_configuration_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in update_zone_configuration_dao {}".format(e))
        raise e


def update_zone_dimensions_dao(company_id, zone_list):
    """
    validate zone id by company id
    @param company_id:
    @param zone_list:
    @return:
    """
    try:
        response = ZoneMaster.update_zone_dimensions(company_id=company_id, zone_list=zone_list)
        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in update_zone_configuration_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in update_zone_configuration_dao {}".format(e))
        raise e



def update_csr_emlock_status_dao(device_id, emlock_status):
    """
    update csr emlock status
    @param device_id:
    @param emlock_status:
    @return:
    @return:
    """
    try:
        response = ContainerMaster.update_csr_emlock_status(device_id=device_id,
                                                 emlock_status=emlock_status)
        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in update_csr_emlock_status_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in update_csr_emlock_status_dao {}".format(e))
        raise e


def get_csr_drawer_data_dao(device_id):
    """
    update csr drawer data
    @param device_id:
    @return:
    """
    try:
        response = ContainerMaster.get_csr_drawer_data(device_id=device_id)
        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_csr_drawer_data_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_csr_drawer_data_dao {}".format(e))
        raise e


def get_zone_id_list_for_a_company_dao(company_id):
    """
    get zone lid list for a company dao
    @param company_id:
    @return:
    """
    try:
        zone_id_list = ZoneMaster.get_zone_id_list_for_a_company(company_id=company_id)
        return zone_id_list

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_zone_id_list_for_a_company_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_zone_id_list_for_a_company_dao {}".format(e))
        raise e


def get_zones(company_id):
    """
     Returns the details of the zones present for a company.
    @param company_id:
    :return: zones details of a company.
    """
    try:
        db_result = list()
        query = ZoneMaster.select().dicts().where(ZoneMaster.company_id == company_id)
        for zone in query:
            conversion_ratio = None
            if zone['dimensions_unit_id'] != 5:
                conversion_ratio = UnitConversion.get_conversion_ratio_for_a_unit(convert_from=5,
                                                                                  convert_into=
                                                                                  zone['dimensions_unit_id'])
            else:
                conversion_ratio = 1
            zone['user_entered_height'] = zone['height'] * conversion_ratio
            zone['user_entered_width'] = zone['width'] * conversion_ratio
            zone['user_entered_length'] = zone['length'] * conversion_ratio
            unit_data = UnitMaster.get_unit_by_unit_id(unit_id=zone['dimensions_unit_id'])
            zone['unit_name'] = unit_data['name']
            zone['unit_symbol'] = unit_data['symbol']
            db_result.append(zone)
        return db_result

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in get_zones {}".format(e))
        raise e
