
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.rph_verification import start_rph_check, get_rph_check_details, mark_rph_check_status, \
    get_notes_from_ips


class StartRPHCheck(object):
    """ Controller to initiate RPh process with IPS """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], start_rph_check
            )
        else:
            return error(1001)
        return response


class GetRPHCheckDetails(object):
    """ Controller to get RPh Details from IPS for alerts """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, pack_id=None, **kwargs):
        if company_id is None or pack_id is None or system_id is None:
            return error(1001, "Missing Parameter(s): company_id or pack_id or system_id.")

        args = {'company_id': company_id, 'pack_id': pack_id,
                'system_id': system_id}
        response = get_rph_check_details(args)

        return response


class MarkRPHCheckStatus(object):
    """ Controller to update IPS with Approve or Reject Status """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], mark_rph_check_status
            )
        else:
            return error(1001)
        return response


class GetNotesFromIPS(object):
    """ Controller to get Notes from IPS """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, pack_id=None, note_type=0, **kwargs):
        if company_id is None or pack_id is None or system_id is None:
            return error(1001, "Missing Parameter(s): company_id or pack_id or system_id.")

        args = {'company_id': company_id, 'pack_id': pack_id,
                'system_id': system_id, 'note_type': note_type}
        response = get_notes_from_ips(args)

        return response
