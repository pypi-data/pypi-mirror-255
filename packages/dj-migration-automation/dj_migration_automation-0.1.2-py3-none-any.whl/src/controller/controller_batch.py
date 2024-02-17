import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.pack import revert_batch
from src.service.batch import create_batch, pre_create_batch, get_packs_by_batch_ids


class PackBatch(object):
    """Controller for Pack Batch"""
    exposed = True

    # authentication added to check this api from crm side
    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], create_batch
            )
        else:
            return error(1001)
        return response


class PackMultiBatch(object):
    """Controller for Pack Multi Batch"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], pre_create_batch
            )
        else:
            return error(1001)
        return response


class GetCreatedMultiBatch(object):
    """Controller for get multi batch details"""
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, system_id=None, filters=None, sort_fields=None, paginate=None, **kwargs):
        if system_id is None:
            return error(1001, "Missing Parameter(s): system_id.")

        args: dict = dict()
        args["system_id"] = int(system_id)

        if paginate is not None:
            args['paginate'] = json.loads(paginate)
        if filters is not None:
            args['filters'] = json.loads(filters)
        if sort_fields is not None:
            args['sort_fields'] = json.loads(sort_fields)

        try:
            response = get_packs_by_batch_ids(args)
        except Exception as ex:
            print(ex)
            return error(1001, ex)

        return response


class RevertBatch(object):
    """ controller for batch revert"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            print(kwargs["args"])
            response = validate_request_args(kwargs["args"], revert_batch)
        else:
            return error(1001)

        return response
