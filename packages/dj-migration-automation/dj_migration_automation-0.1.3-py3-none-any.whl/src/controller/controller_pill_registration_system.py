import json
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.pill_registration_system import get_prs_drug_images, get_prs_data, update_prs_data, \
    unlink_mapped_crops, get_filters_prs

logger = settings.logger


class UpdatePRSData(object):
    """Controller to add multi drug error per pack"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_prs_data
            )
        else:
            return error(1001)

        return response



class GetPRSDrugImages(object):
    """
        Controller for GetPRSDrugImages
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, prs_mode=None, unique_drug_ids=None, paginate=None, drug_status=None, **kwargs):

        args = {
            "prs_mode": prs_mode,
            "unique_drug_ids": unique_drug_ids,
            "drug_status": drug_status
        }
        if paginate:
            args['paginate'] = json.loads(paginate)

        response = get_prs_drug_images(args)

        return response


class GetPRSData(object):
    """
        @class: GetPRSData
        @type: class
        @param: object
        @desc: get the Pill registration screen data for given params
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, filter_fields=None, sort_fields=None, paginate=None, mode=None,  **kwargs):
        args = {}
        try:
            if not company_id:
                return error(1001, "Missing Parameter(s): company_id.")
            else:
                args["company_id"] = json.loads(company_id)
            if paginate is not None:
                args["paginate"] = json.loads(paginate)
            if filter_fields:
                args["filter_fields"] = json.loads(filter_fields)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)

            args["mode"] = mode

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        try:
            response = get_prs_data(args)
        except Exception as ex:
            print(ex)
            return error(1004)

        return response


class UnlinkMappedCrops(object):
    """
        Controller to unlink mapped crops in rts
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], unlink_mapped_crops
            )
        else:
            return error(1001)

        return response


class GetFiltersPrs(object):

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, **kwargs):
        try:
            response = get_filters_prs()
            return response
        except Exception as ex:
            print(ex)
            return error(1004)

