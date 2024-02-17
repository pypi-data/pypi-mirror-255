from src.model.model_pack_details import PackDetails
from src.model.model_pack_history import PackHistory
from src import constants
from src.model.model_container_master import ContainerMaster
from src.model.model_device_master import DeviceMaster
from dosepack.utilities.utils import get_current_date_time, log_args_and_response
import settings
from peewee import *

logger = settings.logger


@log_args_and_response
def validate_asrs_device(device_id: int, system_id: int, company_id: int) -> bool:
    """
    To validate device with system and company
    @param device_id:
    @param system_id:
    @param company_id:
    @return:
    """
    try:
        asrs_device_data = DeviceMaster.get_device_data(device_id=device_id)

        # obtain system_id and company_id from device_data
        device_system_id = asrs_device_data["system_id"]
        device_company_id = asrs_device_data["company_id"]

        if device_company_id == company_id and device_system_id == system_id:
            return True
        else:
            return False

    except IntegrityError as e:
        logger.error("error in validate_asrs_device {}".format(e))
        raise e
    except InternalError as e:
        logger.error("error in validate_asrs_device {}".format(e))
        raise e


@log_args_and_response
def validate_devices(device_ids: list, company_id: int) -> bool:
    """
    validate if the list of devices belong to the given company_id and are of the expected device_type
    @param device_ids:
    @param company_id:
    @return:
    """
    logger.info("In validate_devices.")
    device_type_ids = [settings.DEVICE_TYPES["ASRS"], settings.DEVICE_TYPES["ASRS Storage"]]
    fetched_device_ids = list()
    try:
        device_details = DeviceMaster.get_all_devices_of_a_type(device_type_ids=device_type_ids, company_id=company_id)
        for device in device_details:
            fetched_device_ids.append(device["id"])

        if set(device_ids).issubset(set(fetched_device_ids)):
            return True
        else:
            return False
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in validate_devices {}".format(e))
        raise e


def db_verify_packlist_by_system(system_id, pack_list):
    """
    Function to validate pack list for given company_id and system_id
    @param system_id: int
    @param pack_list: list
    @return: status
    """
    valid_pack = PackDetails.db_verify_packlist_by_system_id(pack_list, system_id)
    if not valid_pack:
        return False

    return True


def update_container_for_pack(company_id, system_id, pack_id, container_id):
    """
    Function to update container id in pack details for given pack
    @param company_id: int
    @param system_id: int
    @param pack_id: int
    @param container_id: int
    @return: int
    """
    update_status = PackDetails.update(container_id=container_id,
                                       modified_date=get_current_date_time()) \
        .where(PackDetails.company_id == company_id,
               PackDetails.system_id == system_id,
               PackDetails.id == pack_id).execute()
    logger.info("Updated status {}".format(update_status))
    return update_status


def get_containers_linked_with_device(device_id):
    try:
        container_count = ContainerMaster.select(fn.COUNT(ContainerMaster.id).alias('container_count')) \
            .where(ContainerMaster.device_id == device_id).get().container_count

        return container_count

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_containers_linked_with_device {}".format(e))
        raise
    except DoesNotExist as e:
        logger.error("error in get_containers_linked_with_device {}".format(e))
        return None


@log_args_and_response
def db_dissociate_container_from_device(container_id, asrs_storage_device, user_id):
    """
    Function to dissociate container from given device
    @param container_id: int
    @param asrs_storage_device: int
    @param user_id: int
    @return: status
    """

    try:
        update_status = ContainerMaster.update(device_id=asrs_storage_device,
                                               shelf=None,
                                               modified_by=user_id,
                                               modified_date=get_current_date_time()) \
            .where(ContainerMaster.id == container_id).execute()
        return update_status

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in db_dissociate_container_from_device {}".format(e))
        raise


def db_associate_container_with_device(container_id, device_id, user_id, container_position):
    """
    Function to associate container with device
    @param container_position: int
    @param container_id: int
    @param device_id: int
    @param user_id: int
    @return: status
    """

    try:
        update_status = ContainerMaster.update(device_id=device_id,
                                               shelf=container_position,
                                               modified_by=user_id,
                                               modified_date=get_current_date_time()
                                               )\
                        .where(ContainerMaster.id == container_id).execute()
        logger.info(f"db_associate_container_with_device, update_status: {update_status}")
        return update_status

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in db_associate_container_with_device {}".format(e))
        raise


@log_args_and_response
def get_asrs_storage_device(company_id):
    """
    Function to get asrs storage device
    @param company_id: int
    @return: int
    """
    logger.info("In get_asrs_storage_device")

    try:
        query = DeviceMaster.select(DeviceMaster.id).dicts() \
            .where(DeviceMaster.device_type_id == settings.DEVICE_TYPES['ASRS Storage'],
                   DeviceMaster.company_id == company_id)

        for record in query:
            return record['id']

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_asrs_storage_device {}".format(e))
        raise

    except DoesNotExist as e:
        logger.error("error in get_asrs_storage_device {}".format(e))
        return None


@log_args_and_response
def get_packs_of_container(container_id: int) -> list:
    """
    Function to get pack list of given container_id
    @param container_id: int
    @return: list
    """
    try:
        pack_list = list()
        pack_query = PackDetails.select(PackDetails.id).dicts().where(PackDetails.container_id == container_id)
        for record in pack_query:
            pack_list.append(record["id"])
        return pack_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_packs_of_container {}".format(e))
        raise e


def remove_packs_from_container(pack_list: list) -> int:
    """
    Function to remove given packs from container
    @param pack_list:
    @return:
    """
    logger.info("In remove_packs_from_container")
    try:
        return PackDetails.update(container_id=None).where(PackDetails.id << pack_list).execute()
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in remove_packs_from_container {}".format(e))
        raise e


def add_pack_details_in_pack_history(pack_ids: list, user_id: int, container_id: int) -> bool:
    """
    To add data in pack_history
    @param container_id: container id of pack
    @param pack_ids: list of pack ids
    @param user_id: action taken by user
    @return:
    """
    try:
        pack_history_list = list()
        for pack_id in pack_ids:
            pack_history = {"pack_id": pack_id, "action_id": constants.ACTION_PACK_REMOVED_FROM_CONTAINER,
                            "action_taken_by": user_id, "old_value": container_id}
            pack_history_list.append(pack_history)

        pack_history_status = PackHistory.insert_many(pack_history_list).execute()
        return pack_history_status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in add_pack_details_in_pack_history {}".format(e))
        raise e


@log_args_and_response
def get_container_data(device_ids: list) -> list:
    """
    Fetches the container data for the given list of the devices.
    @param device_ids:
    @return:
    """
    # result_data = list()
    try:

        query = ContainerMaster.select(ContainerMaster.id,
                                       ContainerMaster.device_id,
                                       ContainerMaster.drawer_name,
                                       ContainerMaster.serial_number,
                                       ContainerMaster.shelf.alias("container_position"),
                                       fn.IF(PackDetails.container_id.is_null(True), True, False).alias("is_empty"),
                                       fn.COUNT(fn.DISTInct(PackDetails.id)).alias("pack_count")
                                       ).dicts() \
            .join(PackDetails, JOIN_LEFT_OUTER, on=PackDetails.container_id == ContainerMaster.id) \
            .where(ContainerMaster.device_id << device_ids) \
            .group_by(ContainerMaster.id)

        return list(query)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_container_data {}".format(e))
        raise e


@log_args_and_response
def get_container_data_by_id(container_id: list) -> list:
    """
    Fetches the container data for the given list of the devices.
    @param container_id:
    @return:
    """

    try:
        query = ContainerMaster.select(ContainerMaster,
                                       fn.IF(PackDetails.container_id.is_null(True), True, False).alias("is_empty"),
                                       fn.COUNT(fn.DISTInct(PackDetails.id)).alias("pack_count")
                                       ).dicts() \
            .join(PackDetails, JOIN_LEFT_OUTER, on=PackDetails.container_id == ContainerMaster.id) \
            .where(ContainerMaster.id == container_id) \
            .group_by(ContainerMaster.id)

        return list(query)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_container_data_by_id {}".format(e))
        raise e


@log_args_and_response
def get_container_at_location(device_id: int, position: int):

    try:
        container_data = ContainerMaster.select().dicts() \
            .where(ContainerMaster.device_id == device_id,
                   ContainerMaster.shelf == position).get()

        return container_data

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_container_at_location {}".format(e))
        raise
    except DoesNotExist as e:
        logger.error("error in get_container_at_location {}".format(e))
        return None
