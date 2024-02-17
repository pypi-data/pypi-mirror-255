import settings
from dosepack.base_model.base_model import db
from dosepack.utilities.manage_db_connection import use_database
from dosepack.error_handling.error_handler import error
from dosepack.validation.validate import validate_request_args
from src.service.pack_ext import update_ext_pack_status

from dosepack.utilities.validate_auth_token import authenticate


class UpdateExtPackStatus(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_ext_pack_status
            )
        else:
            return error(1001)

        return response
