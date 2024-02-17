import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.template_split_status import ext_template_split_status


class GetTemplateSplitStatus(object):
    """
    Controller to process request from IPS and return them whether any Pack is at Template or Pack stage at DosePack
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], ext_template_split_status
            )
        else:
            return error(1001, "Missing Parameter(s): args")

        return response
