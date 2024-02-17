import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.pharmacy import get_pharmacy, add_pharmacy


class Pharmacy(object):
    """
          @class: Pharmacy
          @type: class
          @param: object
          @desc:  End points for pharmacy (Create and Retrieve)
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, system_id=None, **kwargs):
        if system_id is None:
            return error(1001, "Missing Parameter(s): system_id.")

        args = {"system_id": system_id}
        response = get_pharmacy(args)

        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_pharmacy
            )
        else:
            return error(1001)

        return response
