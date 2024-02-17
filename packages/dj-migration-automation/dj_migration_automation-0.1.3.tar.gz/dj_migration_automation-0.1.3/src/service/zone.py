import threading
from collections import OrderedDict
from peewee import IntegrityError, InternalError, DataError, DoesNotExist
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import call_webservice, log_args_and_response
from dosepack.validation.validate import validate
from src.dao.device_manager_dao import get_csr_drawer_data_to_hit_webservice, get_device_data_from_serial_number_dao, \
    get_device_type_id_dao, get_all_devices_of_a_type_dao, get_company_id_of_a_device_dao
from src.dao.unit_dao import get_conversion_ratio_for_a_unit_dao, get_unit_data_by_name_dao
from src.dao.zone_dao import create_zone_dao, validate_zone_id, validate_device_layout_id_list, \
    transfer_device_from_zone_dao, remove_device_from_zone_dao, update_zone_configuration_dao, \
    update_zone_dimensions_dao, update_csr_emlock_status_dao, get_csr_drawer_data_dao, \
    get_zone_id_list_for_a_company_dao, get_zones

logger = settings.logger


@validate(required_fields=["name", "floor", "length", "height", "width", "company_id"])
def insert_zone_data(zone_data):
    """
    Converts the zone dimensions into mm and inserts the new zone data in the zone_master table.

    :param zone_data:
    :return: json
    """
    try:
        zone_data_dict = zone_data.copy()
        default_unit_data = get_unit_data_by_name_dao(unit_name=settings.DEFAULT_UNIT_TYPE_IN_INVENTORY)
        default_unit_id = default_unit_data['id']
        if "x_coordinate" not in zone_data_dict.keys():
            zone_data_dict["x_coordinate"] = 0
        if "y_coordinate" not in zone_data_dict.keys():
            zone_data_dict["y_coordinate"] = 0
        if "dimensions_unit_id" not in zone_data_dict.keys():
            zone_data_dict["dimensions_unit_id"] = default_unit_id  # todo: make this a constant

        # Conversion of units to mm
        if zone_data_dict["dimensions_unit_id"] != default_unit_id:
            conversion_ratio = get_conversion_ratio_for_a_unit_dao(convert_from=zone_data_dict["dimensions_unit_id"],
                                                                   convert_into=default_unit_id)
            zone_data_dict['height'] *= conversion_ratio
            zone_data_dict['width'] *= conversion_ratio
            zone_data_dict['length'] *= conversion_ratio

        with db.transaction():
            response = create_zone_dao(zone_data=zone_data_dict)
            return create_response(response)

    except IntegrityError as e:
        if e.args[0] == 1062:
            return error(1019, "for company_id and name.")
        else:
            return error(2001)
    except InternalError as e:
        logger.error("Error in insert_zone_data: {}".format(e))
        return error(2001)
    except DataError as e:
        logger.error("Error in insert_zone_data: {}".format(e))
        return error(1020)


def remove_devices_from_a_zone(device_data):
    """
    This either delete or transfer devices from a zone based on the command coming
    into device_data after validating zone id and device ids.
    :param device_data:
    :return: json
    """
    company_id = device_data["company_id"]
    try:
        zone_id = device_data['zone_id']
    except Exception as e:
        # zone id will be null for the devices that are outside of zones, and we might
        # have to delete them or transfer them to another zone.
        zone_id = None
    device_layout_id_list = device_data['device_layout_id_list']
    response = False
    zone_id_validation_status = True
    if zone_id is not None:
        zone_id_validation_status = validate_zone_id(zone_id=zone_id, company_id=company_id)
    if zone_id_validation_status is False:
        return error(9050)
    else:
        device_layout_id_validation_status = validate_device_layout_id_list(device_list=device_layout_id_list,
                                                                            zone_id=zone_id)
        if device_layout_id_validation_status is False:
            return error(9051)
        else:
            try:
                if device_data['command'] == 'transfer':
                    transfer_to_zone = device_data['transfer_to_zone_id']
                    transfer_zone_id_validation_status = True
                    if transfer_to_zone is not None:
                        transfer_zone_id_validation_status = validate_zone_id(zone_id=transfer_to_zone,
                                                                              company_id=company_id)
                    if transfer_zone_id_validation_status is False:
                        print('Transfer to zone id status false')
                        return error(9050)
                    else:
                        response = transfer_device_from_zone_dao(zone_id=zone_id,
                                                                 device_id_list=device_layout_id_list,
                                                                 transfer_to_zone=transfer_to_zone)
                elif device_data['command'] == 'delete':
                    with db.transaction():
                        response = remove_device_from_zone_dao(device_id_list=device_layout_id_list)
            except (IntegrityError, InternalError) as e:
                return error(2001)
            except DataError as e:
                logger.error("Error in remove_devices_from_a_zone: {}".format(e))
                return error(1020)

    return create_response(response)


@validate(required_fields=["zone_id", "device_list", "company_id"])
def update_device_coordinates(updated_configuration):
    """
    Updates the devices x_coordinate, y_coordinate in device_layout_details and stacking properties
    in stacked_devices table after validating zone id and device ids.
    @return:
    @param updated_configuration:
    @return:
    """
    zone_id = updated_configuration['zone_id']
    device_list = updated_configuration['device_list']
    company_id = updated_configuration["company_id"]
    zone_id_validation_status = validate_zone_id(zone_id=zone_id, company_id=company_id)
    if zone_id_validation_status is False:
        return error(9050)
    else:
        device_layout_id_list = list()
        stacking_list = list()
        rotation_data_list = list()
        for device in device_list:
            device_layout_id_list.append(device['id'])
            if device['stacked_on'] is not None:
                stacking_list.append(device['stacked_on'])
            if 'properties' in device.keys() and 'rotate' in device['properties'].keys():
                rotate_data = dict()
                rotate_data['device_layout_id'] = device['id']
                rotate_data['rotate'] = device['properties']['rotate']
                rotation_data_list.append(rotate_data)
        device_layout_id_validation_status = validate_device_layout_id_list(device_list=device_layout_id_list,
                                                                            zone_id=zone_id)
        if device_layout_id_validation_status is False:
            return error(9051)
        else:
            try:
                with db.transaction():
                    stacked_on_device_validation_status = validate_device_layout_id_list(device_list=stacking_list,
                                                                                         zone_id=zone_id)
                    if stacked_on_device_validation_status is True:
                        pass
                        # stacking_response = StackedDevices.update_stacked_devices(stacking_device_list=device_list)
                    else:
                        return error(9051)
                    response = update_zone_configuration_dao(zone_id=zone_id, device_list=device_list)

                    return create_response(response)
            except (IntegrityError, InternalError) as e:
                logger.error("Error in update_device_coordinates: {}".format(e))
                return error(2001)
            except DataError as e:
                logger.error("Error in update_device_coordinates: {}".format(e))
                return error(1020)
            except DoesNotExist as e:
                logger.error("Error in update_device_coordinates: {}".format(e))
                return error(1004)


@validate(required_fields=["zone_list", "company_id"])
def update_zone_coordinates(updated_configuration):
    """
    Updates the zones x_coordinate, y_coordinate in zone_master table after validating zone id.
    @param updated_configuration:
    :return: json
    """
    company_id = updated_configuration['company_id']
    zone_list = updated_configuration['zone_list']
    zone_id_list = list()
    for device in zone_list:
        zone_id_list.append(device['id'])
    device_layout_id_validation_status = validate_zone_id_list(zone_list=zone_id_list, company_id=company_id)
    if device_layout_id_validation_status is False:
        return error(9050)
    else:
        try:
            response = update_zone_dimensions_dao(company_id=company_id, zone_list=zone_list)
        except (IntegrityError, InternalError) as e:
            logger.error("Error in update_zone_coordinates: {}".format(e))
            return error(2001)
        except DataError as e:
            logger.error("Error in update_zone_coordinates: {}".format(e))
            return error(1020)

        return create_response(response)


def set_web_service_url_for_csr_drawers(company_id, device_id_list):
    """
    This function will be used to set webservice url for given csr drawers.
    :param company_id:
    :param device_id_list:
    :return:
    """
    try:
        response_dict_of_set_webservice = dict()

        dpws_ip_address = settings.CSR_SERVER_SERVICE_IP
        dpws_port = int(settings.CSR_SERVER_SERVICE_PORT)
        csr_drawers_list = get_csr_drawer_data_to_hit_webservice(company_id=company_id,
                                                                 device_id_list=device_id_list)

        thread_pool = list()
        for csr_drawer in csr_drawers_list:
            response_dict_of_set_webservice[csr_drawer['id']] = -1
            drawer_id = csr_drawer['container_id']
            csr_ip_address = csr_drawer['ip_address']
            csr_table_id = csr_drawer['id']

            params = dict()
            params['container_id'] = drawer_id
            params['ip_address'] = dpws_ip_address
            params['port'] = dpws_port
            t = threading.Thread(target=call_webservice_url_in_threads,
                                 args=[response_dict_of_set_webservice, drawer_id,
                                       csr_ip_address, csr_table_id, params, settings.CSR_SET_WEBSERVICE_API],
                                 daemon=True)
            thread_pool.append(t)
            t.start()

        for thread in thread_pool:
            thread.join()

        return create_response(response_dict_of_set_webservice)
    except(InternalError, IntegrityError):
        return error(2001)
    except Exception as e:
        print('Exception came in settings webservice url: ', e)


def refresh_scan_for_csr_drawers(company_id, device_id_list, drawer_id_list):
    """
    This function will be used to toggle debug mode for csr drawers.
    @param company_id:
    @param device_id_list:
    @return:
    @param drawer_id_list:
    """
    try:
        response_dict_of_set_webservice = dict()
        if not drawer_id_list:
            csr_drawers_list = get_csr_drawer_data_to_hit_webservice(company_id=company_id,
                                                                     device_id_list=device_id_list)
        else:
            csr_drawers_list = get_csr_drawer_data_to_hit_webservice(company_id=company_id,
                                                                     drawer_number_list=drawer_id_list)

        thread_pool = list()
        for csr_drawer in csr_drawers_list:
            response_dict_of_set_webservice[csr_drawer['id']] = -1
            drawer_id = csr_drawer['container_id']
            csr_ip_address = csr_drawer['ip_address']
            csr_table_id = csr_drawer['id']

            params = OrderedDict()
            params['container_id'] = drawer_id
            t = threading.Thread(target=call_webservice_url_in_threads,
                                 args=[response_dict_of_set_webservice, drawer_id,
                                       csr_ip_address, csr_table_id, params, settings.CSR_REFRESH_SCAN],
                                 daemon=True)
            thread_pool.append(t)
            t.start()

        for thread in thread_pool:
            thread.join()

        return create_response(response_dict_of_set_webservice)
    except(InternalError, IntegrityError):
        return error(2001)
    except Exception as e:
        print('Exception came in settings webservice url: ', e)


def csr_emlock_status_callback(location_data):
    try:
        device_data = get_device_data_from_serial_number_dao(serial_number=location_data['serial_number'])
        if device_data and len(device_data.keys()) > 0:
            device_id = device_data['id']
            drawer_id = location_data['container_id']
            emlock_status = location_data['emlock_status']

            response = update_csr_emlock_status_dao(device_id=device_id,
                                                    emlock_status=emlock_status)


        else:
            return error(9054)

        return create_response(True)
    except (IntegrityError, InternalError) as e:
        logger.error("Error in csr_emlock_status_callback: {}".format(e))
        return error(2001)
    except DoesNotExist as e:
        logger.error("Error in csr_emlock_status_callback: {}".format(e))
        return error(9054)
    except DataError as e:
        logger.error("Error in csr_emlock_status_callback: {}".format(e))
        return error(1020)


def get_all_csr_devices_list(company_data):
    try:
        device_type_id = get_device_type_id_dao(device_type_name=settings.DEVICE_TYPES_NAMES['CSR'])

        csr_devices_data = get_all_devices_of_a_type_dao(device_type_ids=[device_type_id['id']],
                                                                  company_id=company_data['company_id'])

        return create_response(csr_devices_data)

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("Error in get_all_csr_devices_list: {}".format(e))
        return error(2001)


def get_csr_drawers_data(csr_data):
    try:
        if csr_data['device_id'] is not None:
            company_data = get_company_id_of_a_device_dao(device_id=csr_data['device_id'])
            if company_data['company_id'] == csr_data['company_id']:
                response = get_csr_drawer_data_dao(device_id=csr_data['device_id'])
            else:
                return error(9054)
        else:
            response = get_csr_drawer_data_dao(device_id=csr_data['device_id'])

        return create_response(response)
    except (InternalError, IntegrityError):
        return error(2001)
    except DoesNotExist:
        return error(9054)


def validate_zone_id_list(zone_list, company_id):
    """
    Helper function to validate whether zone ids are present for a company id.
    @param zone_list:
    @param company_id:
    @return:
    """
    zone_id_list = get_zone_id_list_for_a_company_dao(company_id=company_id)
    for device in zone_list:
        if device not in zone_id_list:
            return False
    return True


def call_webservice_url_in_threads(response_dict, drawer_id, csr_ip_address, csr_drawer_table_id, params, api_name):
    """
    This function will be used to send the api calls to csr. It will be called in threads from another functions.
    @param response_dict:
    @param drawer_id:
    @param csr_ip_address:
    @param csr_drawer_table_id:
    @param params:
    @param api_name:
    """
    status, response = call_webservice(base_url=csr_ip_address, webservice_url=api_name,
                                       parameters=params, use_ssl=False, call_electronics_api=True)

    if status:
        formatted_response = eval(response)
        if "status" in formatted_response.keys() and formatted_response["status"] == "success":
            response_dict[csr_drawer_table_id] = 1


@log_args_and_response
def get_zones_by_company(company_data):
    """
    Gets the zones data for a particular company.

    :param company_data:
    :return: json
    """
    company_id = company_data['company_id']
    try:
        response = get_zones(company_id=company_id)
        response_dict = dict()
        response_dict['zone_list'] = response

        return create_response(response_dict)
    except (IntegrityError, InternalError) as e:
        return error(2001)

