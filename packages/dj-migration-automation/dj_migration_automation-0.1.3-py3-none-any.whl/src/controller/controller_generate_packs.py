"""
    @file: http_service.py
    @type: file
    @desc: Contains wrappers for python functions into web services
"""

import json

import settings
from src import constants
from src.service.generate_packs import generate
from dosepack.error_handling.error_handler import error
from dosepack.validation.validate import validate_request_args
from src.service.parser import Parser

from dosepack.base_model.base_model import db
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate


class GeneratePacks(object):
    """
          @class: GeneratePacksFromFile
          @type: class
          @param: object
          @desc: generates packs from file for the given file ids
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], generate)
        else:
            return error(1001)

        return response


class GeneratePacksV2(object):
    """
          @class: GeneratePacksFromFile
          @type: class
          @param: object
          @desc: generates packs from file for the given file ids and patient ids
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            args = json.loads(kwargs["args"])

            # version 2 will generate pack acc requirement of IER #15552
            args["version"] = constants.GENERATE_PACK_VERSION
            args = json.dumps(args)
            response = validate_request_args(args, generate)
            return response
        else:
            return error(1001)

        # return response


class Parse(object):
    """
          @class: GetFileInfo
          @type: class
          @param: object
          @desc:  get the uploaded file information by date
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            try:
                received_data = json.loads(kwargs['args'])
                user_id = received_data["user_id"]
                filename = received_data["filename"]
                data = received_data["data"]
                company_id = int(received_data["company_id"])
                process_pharmacy_file = Parser(
                    user_id,
                    filename,
                    company_id,
                    data=data,
                    from_dict=True
                )
                response = process_pharmacy_file.start_processing()
            except KeyError:
                return error(1001, "Missing parameters.")
        else:
            return error(1001)
        return response
