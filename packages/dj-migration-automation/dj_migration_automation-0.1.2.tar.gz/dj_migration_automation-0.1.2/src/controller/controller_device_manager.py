import settings
import json
import logging
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.device_manager import (add_robot, get_robot_info, update_robot,
                                        get_robots_by_system_list, get_robots_by_company_id, get_device_data,
                                       save_disabled_location_transfers,
                                        update_device, update_id_address, add_device_data,
                                        get_disabled_locations, disable_canister_location,
                                        api_callback_v3, get_device_drawer_data,
                                        get_device_type_data, get_enabled_locations, get_disabled_drawers,
                                        enable_location)

logger = logging.getLogger("root")


class Robot(object):
    """ Controller to get robot data """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, system_id=None, robot_id=None, system_id_list=None, company_id=None, **kwargs):
        if company_id:  # if company id is present then return all robots for given company
            response = get_robots_by_company_id(company_id)
            return response
        # if system id list is present then provide robots for given system ids
        if system_id_list:
            system_id_list = system_id_list.split(",")
            response = get_robots_by_system_list(system_id_list)
        # if system id is present then provide robots of system else return error
        else:
            if system_id is None:
                return error(1001, "Missing Parameter(s): system_id.")
            args = {"system_id": system_id}
            if robot_id:
                args["robot_id"] = robot_id

            response = get_robot_info(args)

        return response


class AddRobot(object):
    """Controller to add robot"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_robot
            )
        else:
            return error(1001)

        return response


class UpdateRobot():
    """ Controller to update robot """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_robot
            )
        else:
            return error(1001)

        return response


class GetDeviceTypes(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id, system_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id")

        args: dict = dict()
        args["company_id"] = company_id
        args["system_id"] = system_id

        response = get_device_type_data(data_dict=args)

        return response


class GetDevices(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id, system_id=None, device_id=None,
            device_type=None, associated_device=None,
            device_type_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id")
        # if all_flag:
        #     all_flag = json.loads(all_flag)
        args: dict = dict()
        args["company_id"] = company_id
        args["system_id"] = system_id
        args["device_id"] = device_id
        args["associated_device"] = associated_device
        args["device_type"] = device_type
        args["device_type_id"] = device_type_id
        response = get_device_data(data_dict=args)

        return response


class UpdateDevice(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_device
            )
        else:
            return error(1001)

        return response


class UpdateIPAddress(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_id_address
            )
        else:
            return error(1001)

        return response


class AddDeviceData(object):
    """Controller to add robot"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_device_data
            )
        else:
            return error(1001)

        return response


class DisabledLocationsV2(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], save_disabled_location_transfers)
        else:
            return error(1001)
        return response


class DisabledLocations(object):
    """
      @class: DisabledLocations
      @type: class
      @param: object
      @desc:  handles get and post for disabled locations
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, device_ids=None, company_id=None, drawer_numbers=None, **kwargs):
        if device_ids is None and company_id is None:
            return error(1001, "Missing Parameter(s): device_ids and company_id.")
        response = get_disabled_locations(
            device_ids, company_id, container_numbers=drawer_numbers
        )
        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"],
                disable_canister_location
            )
        else:
            return error(1001)
        return response


class CallbackV3(object):
    """
    @class: CallbackV3
    @desc : Generic callback api for all stations
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, args):
        if args is None:
            return error(1001, "Missing Parameters.")

        try:
            callback_data = json.loads(args)
            logger.info(callback_data)
        except Exception as e:
            logger.error(e)
            try:
                callback_data = eval(args)
            except Exception as e:
                logger.error(1001, "api_callback - Exception: {} ".format(e))
                return error(1008)

        response = api_callback_v3(callback_data)

        return response


class DeviceDrawerData(object):
    """Controller to add robot"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id, system_id=None, device_id=None, station_type=None, station_id=None, serial_number=None,
            **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        if device_id is None and (station_id is None or station_type is None) and serial_number is None:
            return error(1001, 'Missing Parameter(s): device_id and (station_id or station_type).')
        response = get_device_drawer_data(company_id, system_id, device_id, station_id, station_type, serial_number)

        return response


class EnableLocation(object):
    """
      @class: EnableLocations
      @type: class
      @param: object
      @desc:  deletes disabled location
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"],
                enable_location
            )
        else:
            return error(1001)
        return response


class GetEnabledLocations(object):
    """
      @class: GetEnabledLocations
      @type: class
      @param: object
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_ids=None, company_id=None, drawer_numbers=None, **kwargs):
        if device_ids is None and company_id is None:
            return error(1001, "Missing Parameter(s): device_ids and company_id.")
        response = get_enabled_locations(
            device_ids=device_ids, company_id=company_id, container_numbers=drawer_numbers
        )
        return response


class DisabledDrawerData(object):
    """
    This class contains the methods to fetch the disabled drawers if all the locations of a drawer are disabled.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, **kwargs):
        if device_id is None and company_id is None:
            return error(1001, "Missing Parameter(s): device_ids and company_id.")
        response = get_disabled_drawers(device_id=device_id, company_id=company_id)

        return response
