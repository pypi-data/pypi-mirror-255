import ast
import json

import cherrypy

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.controller.controller_misc import myFieldStorage
from src.service.verification import get_packs_master, \
    associate_rfid_with_pack_id, get_all_unassociated_packs, store_photo_in_server


class GetPacksMaster(object):
    """
    @class: GetProcessedPacks
    @type: class
    @param: object
    @desc: It returns all the packs processed.
    """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, filters=None, sort_fields=None, paginate=None,
            company_id=None, time_zone=None, print_labels=None,
            user_id=None, module=None, **kwargs):
        if company_id is None or time_zone is None:
            return error(1001, "Missing Parameter(s): company_id or time_zone.")
        try:
            args = {
                "company_id": company_id,
                "time_zone": time_zone,
                "print_labels": bool(int(print_labels or 0)),  # expected values 0,1
                "user_id": user_id
            }
            if 'system_id' in kwargs and kwargs['system_id']:
                args['system_id'] = kwargs['system_id']
            if paginate is not None:
                args["paginate"] = json.loads(paginate)
            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
            if module:
                args["module"] = int(module)
        except json.JSONDecodeError as e:
            return error(1020, str(e))

        response = get_packs_master(args)

        return response


class AssociateRfidWithPackId(object):
    """
    @class: AssociateRfidWithPackId
    @type: class
    @param: object
    @desc: Associate the rfid for the pack once
           it is processed by the system.

    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            print("From robot" + str(kwargs["args"]))
            response = associate_rfid_with_pack_id(
                ast.literal_eval(kwargs["args"])
            )
        else:
            return error(1001)
        return response

    @use_database(db, settings.logger)
    def GET(self, pack_id=None, rfid=None, system_id=None, **kwargs):
        if pack_id is None or rfid is None or system_id is None:
            return error(1001, "Missing Parameter(s): pack_id or rfid or system_id.")

        args = {
            "pack_id": pack_id,
            "rfid": rfid,
            "system_id": system_id
        }

        response = associate_rfid_with_pack_id(args)
        return response


class GetAllUnassociatedPacks(object):
    """
    @class: GetAllUnassociatedPacks
    @type: class
    @param: object
    @desc: Get all the packs who do not have the rfid associated for a given system.

    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, system_id=None, **kwargs):
        if from_date is None or to_date is None or system_id is None:
            return error(1001, "Missing Parameter(s): from_date or to_date or system_id.")

        args = {
            "date_from": from_date,
            "date_to": to_date,
            "system_id": int(system_id)
        }

        response = get_all_unassociated_packs(args)

        return response


class StorePhotoInServer(object):
    exposed = False  # removing api, If you need use cloud bucket
    file_path = ""  # Variable to store the path of image uploaded

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    @cherrypy.tools.noBodyProcess()
    def POST(self, theFile=None):
        # convert the header keys to lower case
        lcHDRS = {}
        for key, val in cherrypy.request.headers.items():
            lcHDRS[key.lower()] = val

        # create our version of cgi.FieldStorage to parse the MIME encoded
        # form data where the file is contained
        formFields = myFieldStorage(
            fp=cherrypy.request.rfile,
            headers=lcHDRS,
            environ={'REQUEST_METHOD': 'POST'},
            keep_blank_values=True
        )

        # get the filename
        theFile = formFields['theFile']

        data = {"file_name": theFile.filename, "img_data": theFile.file}

        # write the file contents in the file and store the file in appropriate location
        response = store_photo_in_server(data)
        return response
