import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from src.service.location import get_locations_by_system_id


class GetLocationsBySystemID(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, system_id=None, device_type=None, device_id=None, version=None, shelf=None, drawer_names=None,
            **kwargs):
        if system_id is None:
            return error(1001, "Missing Parameter(s): system_id.")
        if device_type:
            device_type = json.loads(device_type)
        if device_id:
            device_id = json.loads(device_id)
        if shelf:
            shelf = json.loads(shelf)
        if drawer_names:
            drawer_names = json.loads(drawer_names)

        try:
            response = get_locations_by_system_id(system_id,
                                                  device_type,
                                                  device_id,
                                                  version,
                                                  shelf,
                                                  drawer_names)
        except Exception as ex:
            return error(1001, "Error in getting device data.")

        return response
