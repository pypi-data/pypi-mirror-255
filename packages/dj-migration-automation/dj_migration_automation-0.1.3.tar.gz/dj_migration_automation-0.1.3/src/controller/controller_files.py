import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.file import get_files, ungenerate_files, show_ungenerate_files
from src.service.file_validation import get_file_validation_error


class GetFile(object):
    """
          @class: GetFileInfo
          @type: class
          @param: object
          @desc:  get the uploaded file information by date, status and system id
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, date_from=None, date_to=None, status=None, company_id=None, time_zone=None, **kwargs):
        if company_id is None:
            return error(1001, 'Missing Parameter(s): company_id.')
        if time_zone is None:
            return error(1001, 'Missing Parameter(s): time_zone.')

        if date_from is None:
            date_from = settings.DEFAULT_START_DATE
        if date_to is None:
            date_to = settings.DEFAULT_TO_DATE
        if status is None or status == str(settings.ALL_FILE_STATUS) \
                or status == str(settings.NULL):
            status = settings.NULL

        args = {
            "date_from": date_from,
            "date_to": date_to,
            "status": status,
            "company_id": company_id,
            "time_zone": time_zone
        }

        response = get_files(args)

        return response


class UngenerateFile(object):
    """
          @class: Ungenerate FileFrom Dose packer
          @type: class
          @param: object
          @desc:  make all the data related to that file in-active in database.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, date_from=None, date_to=None, company_id=None, **kwargs):
        if company_id is None:
            return error(1001, 'Missing Parameter(s): company_id.')
        if date_from is None:
            date_from = settings.DEFAULT_START_DATE
        if date_to is None:
            date_to = settings.DEFAULT_TO_DATE

        args = {
            "date_from": date_from,
            "date_to": date_to,
            "company_id": company_id
        }

        response = show_ungenerate_files(args)

        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], ungenerate_files)
        else:
            return error(1001)

        return response


class FileValidationError(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, file_id=None, **kwargs):
        if file_id is None:
            return error(1001, 'Missing Parameter(s): file_id.')

        response = get_file_validation_error(file_id)
        return response
