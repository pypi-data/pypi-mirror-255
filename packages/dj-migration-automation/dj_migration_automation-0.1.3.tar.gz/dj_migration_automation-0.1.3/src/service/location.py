import settings
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response
from src.dao.device_manager_dao import get_zone_wise_device_list, get_location_ids_by_system_id
logger = settings.logger

@log_args_and_response
def get_locations_by_system_id(system_id, device_type=None, device_id=None, version=None, shelf=None, drawer_names=None,
                               company_id= None):
    """
    Function to return location data of devices
    @param shelf: list
    @param company_id: int
    @param version: string
    @param device_id: list
    @param device_type: list
    @param system_id: int
    @param drawer_names:list
    @return: json
    """
    try:
        # todo remove static company id once updated from FE as input parameter
        logger.debug("get_locations_by_system_id")

        if device_type:
            device_type_id = [settings.DEVICE_TYPES[each_type] for each_type in device_type]

            if (settings.DEVICE_TYPES['CSR'] in device_type_id or settings.DEVICE_TYPES[
                'Manual Filling Device'] in device_type_id or settings.DEVICE_TYPES['Refilling Device']
                in device_type_id) and not device_id:
                #  function to get all devices that falls in zone of given device_types
                device_id = get_zone_wise_device_list(company_id, device_type_id, system_id)
            system_id = None

        if not device_type and not device_id:
            device_id = get_zone_wise_device_list(company_id, device_id, system_id)
            system_id = None

        response = get_location_ids_by_system_id(company_id,
                                                 device_type,
                                                 device_id,
                                                 version,
                                                 shelf,
                                                 drawer_names)
        return create_response(response)

    except Exception as e:
        logger.error(e)
        return error(1000, "Unable to get location data.")