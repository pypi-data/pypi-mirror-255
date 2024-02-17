import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.misc import remove_printer, update_printer, rename_printer
from src.service.print import get_associated_printers, add_printer


class GetAssociatedPrinters(object):
    """
          @class: GetAssociatedPrinters
          @type: class
          @param: object
          @desc:  gets all the queued packs for printing for which file has been generated
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, system_id=None, **kwargs):
        if system_id is None:
            return error(1001, "Missing Parameter(s): system_id.")
        response = get_associated_printers(system_id)

        return create_response(response)


class RemovePrinter(object):
    """
          @class: GetQueuedPacks
          @type: class
          @param: object
          @desc:  gets all the queued packs for printing
          for which file has been generated
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, unique_code=None, system_id=None, **kwargs):
        if unique_code is None or system_id is None:
            return error(1001, "Missing Parameter(s): unique_code or system_id.")

        response = remove_printer(unique_code, system_id)

        return response


class AddPrinter(object):
    """
          @class: GetQueuedPacks
          @type: class
          @param: object
          @desc:  gets all the queued packs for printing
                  for which file has been generated
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, printer_name=None, ip_address=None, system_id=None,
            printer_type=None, **kwargs):
        if printer_name is None or ip_address is None or system_id is None:
            return error(1001, "Missing Parameter(s): printer_name or ip_address or system_id.")

        response = add_printer(printer_name, ip_address, system_id, printer_type)

        return response


class UpdatePrinter(object):
    """
          @class: UpdatePrinter
          @type: class
          @param: object
          @desc: Updates printer data
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_printer
            )
        else:
            return error(1001)

        return response


class RenamePrinter(object):
    """
    Rename the printer name in the Printers.printer_name
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], rename_printer)
        else:
            return error(1001)

        return create_response(response)
