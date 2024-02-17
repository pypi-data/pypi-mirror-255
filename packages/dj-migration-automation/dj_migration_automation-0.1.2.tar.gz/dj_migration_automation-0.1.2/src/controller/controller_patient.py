
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.patient import get_patient_note, create_patient_note, get_patients


class PatientNote(object):
    """ Controller for Patient Note """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, patient_id=None):
        if patient_id is None:
            return error(1001, 'Missing Parameter(s): patient_id.')

        response = get_patient_note(patient_id)

        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if 'args' in kwargs:
            response = validate_request_args(
                kwargs["args"], create_patient_note
            )
            return response
        else:
            return error(1001)


class Patient(object):
    """ Controller for Patient """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # POST instead of GET as patient_id list may truncate in GET url
        if 'args' in kwargs:
            response = validate_request_args(
                kwargs["args"], get_patients
            )
            return response
        else:
            return error(1001)
