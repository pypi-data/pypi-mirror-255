import json

import cherrypy

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from src.service.csr import get_csr_data, get_csr_filters, get_csr_drawer_data, recommend_csr_location, \
    csr_emlock_status_callback_v3


class CSRFilters(object):
    """
    Controller to get the filters for the CSR.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None):
        if device_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): company_id or device_id.")

        args = {
            "device_id": device_id,
            "company_id": company_id
        }

        return get_csr_filters(args)


class CSRData(object):
    """
    Controller to get the CSR Data.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, filter_fields=None, paginate=None, device_id=None, company_id=None, list_view=None,
            empty_locations=None, sort_fields=None, **kwargs):
        if device_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): company_id or device_id.")
        try:
            args = {"device_id": device_id,
                    "company_id": company_id,
                    "list_view": 0 if list_view is None else list_view,
                    "empty_locations": 0 if empty_locations is None else empty_locations}

            if paginate:
                args["paginate"] = json.loads(paginate)
            if filter_fields:
                args["filter_fields"] = json.loads(filter_fields)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))

        return get_csr_data(args)


class CSRDrawerData(object):
    """
    Controller to get the Drawer Data for the CSR.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, drawer_name=None, device_id=None, company_id=None, filter_fields=None, **kwargs):
        if drawer_name is None or device_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): drawer_name or device_id or company_id.")

        args = {
            "drawer_name": drawer_name,
            "device_id": device_id,
            "company_id": company_id,
        }
        if filter_fields:
            args["filter_fields"] = json.loads(filter_fields)

        return get_csr_drawer_data(args)


class RecommendCSRLocation(object):
    """
    Controller to get the Drawer Data for the CSR.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, canister_id=None, device_id=None, company_id=None, reserved_location_list=None, recommend_top_drawer=None,
            call_from_robot=False, system_id=None, **kwargs):
        if canister_id is None or device_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): company_id or device_id or canister_id.")

        if recommend_top_drawer:
            recommend_top_drawer = json.loads(recommend_top_drawer)

        args = {
            "canister_id": canister_id,
            "device_id": device_id,
            "company_id": company_id,
            "recommend_top_drawer": recommend_top_drawer,
            "call_from_robot": call_from_robot,
            "system_id": system_id
        }
        if reserved_location_list:
            args["reserved_location_list"] = eval(reserved_location_list)

        return recommend_csr_location(args)


# class UpdateCSRCanister(object):
#     """
#         Updates csr location in canister based on rids
#     """
#     exposed = True
#
#     @use_database(db, settings.logger)
#     def GET(self, eeprom_dict=None, station_type=None, station_id=None):
#         if eeprom_dict is None or station_type is None or station_id is None:
#             return error(1001, "Missing Parameter(s): eeprom_dict or station_type or station_id.")
#         response = update_csr_canister(loc_rfid_dict=json.loads(eeprom_dict), station_type=int(station_type),
#                                        station_id=str(station_id))
#         cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
#         return response


class CSREMLockStatus(object):
    """
        Controller to update lock status of csr drawer
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, status=None, station_type=None, station_id=None):
        if status is None or station_type is None or station_id is None:
            return error(1001, "Missing Parameter(s): status or station_type or station_id.")
        response = csr_emlock_status_callback_v3(emlock_status=bool(int(status)), station_type=int(station_type),
                                                 station_id=station_id)
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response
