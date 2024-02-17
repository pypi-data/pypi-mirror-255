import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.session import get_session_param, post_session_data


class SessionData(object):
    """
        @class: ModuleParam
        @desc: GET and POST method implementation for session data API.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, module_type_id=None, screen_sequence=None, company_id=None, **kwargs):

        """
        @param module_type_id: integer
        @param screen_sequence: integer
        @param company_id: integer
        @desc: To obtain Parameters of module whose module_id and sequence is provided for session_implementation
        @return: json
        """
        if module_type_id is None or screen_sequence is None or company_id is None:
            return error(1001, "Missing parameters.")
        try:
            args = {
                "module_type_id": module_type_id,
                "screen_sequence": screen_sequence,
                "company_id": company_id
            }
            response = get_session_param(args)

            return response
        except Exception as e:
            print(e)
            return error(1004)

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        """
        @desc: Implementation for session data POST Api to validate and call post_session_data
        @return:json
        """
        try:
            if "args" in kwargs:
                return validate_request_args(kwargs["args"], post_session_data)
        except Exception as e:
            print(e)
            return error(1004)
