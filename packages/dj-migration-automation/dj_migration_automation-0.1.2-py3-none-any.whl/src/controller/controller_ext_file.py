import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.ext_file import process_rx, process_existing_rx


class ProcessRx(object):
    """
        Controller to process prescription of a patient
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], process_rx
            )
        else:
            return error(1001, "Missing Parameter(s): args")

        return response


class ProcessExistingRx(object):
    """
        Controller to process prescription of a patient
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], process_existing_rx
            )
        else:
            return error(1001, "Missing Parameter(s): args")

        return response
