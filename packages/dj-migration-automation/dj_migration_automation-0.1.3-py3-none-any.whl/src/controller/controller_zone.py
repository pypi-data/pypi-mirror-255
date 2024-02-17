import cherrypy

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.utils import hardware_call_webservice
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.misc import set_logged_in_user_in_couch_db_of_system
from src.service.zone import insert_zone_data, remove_devices_from_a_zone, update_device_coordinates, \
    update_zone_coordinates, set_web_service_url_for_csr_drawers, refresh_scan_for_csr_drawers, \
    csr_emlock_status_callback, get_all_csr_devices_list, get_csr_drawers_data, get_zones_by_company


class Zone(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], insert_zone_data)
        else:
            return error(1001)

        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response

    @use_database(db, settings.logger)
    def GET(self, company_id=None):

        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        required_dict = {"company_id": company_id}
        response = get_zones_by_company(required_dict)
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


# not in use from front end
# class DeviceLayoutDetails(object):
#     exposed = True
#
#     @authenticate(settings.logger)
#     @use_database(db, settings.logger)
#     def POST(self, **kwargs):
#
#         if 'args' in kwargs:
#             response = validate_request_args(kwargs['args'], add_device_in_zone)
#         else:
#             return error(1001)
#
#         cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
#         return response
#
#     @use_database(db, settings.logger)
#     def GET(self, zone_id=None, company_id=None):
#
#         if zone_id is None or company_id is None:
#             return error(1001, "Missing Parameter(s): zone_id or company_id.")
#
#         args_dict = {"zone_id": zone_id, "company_id": company_id}
#
#         response = get_devices_of_a_zone(args_dict)
#
#         cherrypy.response.headers['Access-Control_Allow-Origin'] = "*"
#         return response



class TransferDevice(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, transfer_from=None, device_layout_id_list=None, company_id=None, transfer_to=None):

        if device_layout_id_list is None or company_id is None:
            return error(1001, "Missing Parameter(s): device_layout_id_list or company_id.")

        formatted_device_id_list = [int(device_id) for device_id in device_layout_id_list.split(',')]
        args_dict = {"zone_id": transfer_from, "device_layout_id_list": formatted_device_id_list,
                     "command": "transfer", "company_id": company_id, "transfer_to_zone_id": transfer_to}

        response = remove_devices_from_a_zone(args_dict)

        cherrypy.response.headers['Access-Control_Allow-Origin'] = "*"
        return response


class RemoveDevice(object):
    # todo: Have to test this api after confirming the flow.
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, zone_id=None, device_layout_id_list=None, company_id=None):

        if device_layout_id_list is None or company_id is None:
            return error(1001, "Missing Parameter(s): device_layout_id_list or company_id.")

        formatted_device_id_list = [int(device_id) for device_id in device_layout_id_list.split(',')]

        args_dict = {"zone_id": zone_id, "device_layout_id_list": formatted_device_id_list, "command": "delete",
                     "company_id": company_id}

        response = remove_devices_from_a_zone(args_dict)

        cherrypy.response.headers['Access-Control_Allow-Origin'] = "*"
        return response


class UpdateDeviceCoordinates(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if 'args' in kwargs:
            response = validate_request_args(kwargs['args'], update_device_coordinates)
        else:
            return error(1001)

        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class UpdateZoneCoordinates(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if 'args' in kwargs:
            response = validate_request_args(kwargs['args'], update_zone_coordinates)
        else:
            return error(1001)

        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class CommunicateToHardware(object):
    exposed = True

    def GET(self, base_url=None, api_name=None, user_id=None, system_id=None, company_id=None, **kwargs):
        if base_url is None or api_name is None:
            return error(1001, "Missing Parameter(s): base_url or api_name.")
        params = kwargs.copy()
        print(' parameters got are: ', base_url, api_name, params)
        status, response_dict = hardware_call_webservice(base_url=base_url, webservice_url=api_name,
                                                  parameters=params, use_ssl=False, call_electronics_api=True, timeout=2)
        if not status:
            return error(9058)

        # commenting this block as we already decode response inside hardware_call_webservice
        # try:
        #     # response_dict = dict()
        #     # This is done because from electronics side response is not coming properly in string.
        #     # We cannot extract dictionary by using eval, ast.literal_eval etc.
        #     # If we found any better way in the future then implement it.
        #     # string_response = string_response[1:-1]
        #     # string_response = string_response.replace('"', '')
        #     # response_dict = dict((x.strip(), y.strip()) for x, y in (element.split(':') for element in
        #     #                                                          string_response.split(', ')))
        #     response_dict = string_response
        # except Exception as e:
        #     print(" Exception came in formatting the response from csr drawer callback: ", e)

        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        if not status or not len(response_dict.keys()):
            print("Response does not came: ", status, response_dict)
            return error(9058)
        elif 'data' in response_dict.keys():
            additional_info = {}
            if response_dict.get('status') is not None and settings.FAILURE_RESPONSE == response_dict.get('status'):
                additional_info = {'status': settings.FAILURE_RESPONSE}
            else:
                # status - success so use add user_id and system_id in couch db to track who opened hardware drawer
                if user_id and system_id and company_id:
                    args = {"company_id": company_id, "system_id": system_id, "user_id": user_id}
                    update_couch_db_response = set_logged_in_user_in_couch_db_of_system(args)
                    print("couch db update response- "+str(update_couch_db_response))

            return create_response(response_dict.get("data"), additional_info=additional_info)
        else:
            print("Response not formatted: ", response_dict)
            return error(9058)


class SetWebserviceUrl(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id_list=None, company_id=None):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        if device_id_list:
            device_id_list = list(map(lambda x: int(x), device_id_list.split(",")))
        response = set_web_service_url_for_csr_drawers(company_id=int(company_id), device_id_list=device_id_list)

        return response


class RefreshScan(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id_list=None, company_id=None, drawer_id_list=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        if device_id_list:
            device_id_list = list(map(lambda x: int(x), device_id_list.split(",")))

        if drawer_id_list:
            drawer_id_list = list(drawer_id_list.split(","))

        response = refresh_scan_for_csr_drawers(company_id=int(company_id), device_id_list=device_id_list,
                                                       drawer_id_list=drawer_id_list)

        return response


class CsrDrawerLockCallback(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, status=None, serial_number=None, drawer_id=None):
        if status is None or serial_number is None or drawer_id is None:
            return error(1001, "Missing Parameter(s): status or serial_number or drawer_id.")

        args_dict = {"emlock_status": int(status), "serial_number": serial_number, "container_id": int(drawer_id)}
        response = csr_emlock_status_callback(args_dict)
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class CsrDevices(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args_dict = {"company_id": int(company_id)}

        response = get_all_csr_devices_list(company_data=args_dict)
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"

        return response


class CsrDrawers(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
        if device_id is not None:
            args_dict = {"device_id": int(device_id), "company_id": int(company_id)}
        else:
            args_dict = {"device_id": device_id, "company_id": int(company_id)}

        response = get_csr_drawers_data(csr_data=args_dict)
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"

        return response
