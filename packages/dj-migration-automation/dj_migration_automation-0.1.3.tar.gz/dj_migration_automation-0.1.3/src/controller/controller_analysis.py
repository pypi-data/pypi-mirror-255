import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from scripts.merge_request_check import merge_request_check
from scripts.pack_merge_check import pack_merge_check
from scripts.trolley_order_no_change_check import trolley_order_no_change_check
from src.service.pack_distribution import get_patient_data


class PackFlowManager(object):
    """
        @type: class
        @param: object
        @desc:  add a new canister with fields provided.
    """
    exposed = True

    @authenticate(settings.logger)
    def POST(self, **kwargs):
        response = json.dumps({"status": "success", "error": "none"})
        return response


class BatchMergeRequestCheck(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], merge_request_check
            )
        else:
            return error(1001)

        return response


class PackMergeCheck(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], pack_merge_check
            )
        else:
            return error(1001)

        return response


class TrolleyOrderNoChangeCheck(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], trolley_order_no_change_check
            )
        else:
            return error(1001)

        return response

class BatchDistribution(object):
    """ Returns different mini batches"""
    exposed = True

    # Note: GET is now moved to POST request as pack_list can be very long and may truncate in url
    # POST should be used, Remove GET when POST is in use.

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], get_patient_data
            )
        else:
            return error(1001)

        return response


