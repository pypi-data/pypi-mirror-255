import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.label_printing.print_label import get_print_queue_data, print_pack_label, bulk_print_pack_label, \
    test_print_label, \
    generate_pack_sticker, update_job_count, add_label_count_request, bulk_print_pack_label_v2, get_pack_error_label, \
    _canister_label, reset_print_job_couch_db, expired_drug_label
from src.label_printing.utils import api_callback
from src.service.mfd_canister import mfd_canister_label
logger = settings.logger

class PrintQueue(object):
    """
          @class: PrintQueue
          @type: class
          @param: object
          @desc:  Fetches print queue record
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, print_queue_id=None, **kwargs):
        if print_queue_id is None:
            return error(1001, 'Missing Parameter(s): print_queue_id.')

        dict_input_args = {'print_queue_id': print_queue_id}
        response = get_print_queue_data(dict_input_args)

        return response


class PrintPackLabel(object):
    """
          @type: class
          @param: object
          @desc:  Makes entry in PrintQueue and RealTimeDB
                  which will be used by dose pack utility to generate and print label
    """
    exposed = False

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, pack_display_id=None, patient_id=None,
            user_id=None, system_id=None, printer_code=None,
            generate_locally=None, force_regenerate=0, ips_username=None, dry_run=0, **kwargs):

        if pack_id is None or pack_display_id is None or patient_id is None or \
                user_id is None or system_id is None:
            return error(1001, 'Missing Parameter(s): pack_id or pack_display_id or patient_id or user_id or system_id.')

        if generate_locally and int(generate_locally):
            generate_locally = True
        else:
            generate_locally = False
        if force_regenerate and int(force_regenerate):
            # If file needs to be re-generate or not
            force_regenerate = True
        else:
            force_regenerate = False
        dict_input_args = {
            'pack_id': int(pack_id),
            'pack_display_id': pack_display_id,
            'patient_id': int(patient_id),
            'user_id': int(user_id),
            'system_id': system_id,
            "printer_code": printer_code,
            'generate_locally': generate_locally,
            'force_regenerate': force_regenerate,
            'ips_username': ips_username,
            'dry_run': dry_run
        }
        response = print_pack_label(dict_input_args)

        return response


class BulkPrintPackLabel(object):
    """
    Controller for bulk print pack label request
    """
    exposed = False

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], bulk_print_pack_label)
            return response
        else:
            return error(1001)


class TestPrintLabel(object):
    """
        @class: TestPrintLabel
        @type: class
        @param: object
        @desc:  generates test pdf
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, system_id=None, printer_code=None, **kwargs):
        response = test_print_label(printer_code, system_id)

        return response


class CanisterLabel(object):
    """
        @class: CanisterLabel
        @type: class
        @param: object
        @desc: Generates canister label file and returns file name
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], _canister_label
            )
        else:
            return error(1001)

        return response


class ExpiredDrugLabel(object):
    """
        @class: CanisterLabel
        @type: class
        @param: object
        @desc: Generates canister label file and returns file name
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], expired_drug_label
            )
        else:
            return error(1001)

        return response

class PackErrorLabel(object):
    """
        @class: PackErrorLabel
        @type: class
        @param: object
        @desc: Generates pack error label file and returns file name
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], get_pack_error_label
            )
        else:
            return error(1001)

        return response


class GeneratePackSticker(object):
    """
        @class: GeneratePackSticker
        @type: class
        @param: object
        @desc: Generate pack sticker for given pack ID
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], generate_pack_sticker
            )
        else:
            return error(1001)

        return response


class Callback(object):
    """
    @class: Callback
    @desc : Saves canister data in couch db (print utility)
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, args):
        if args is None:
            return error(1001, "Missing Parameters.")

        response = api_callback(args)

        return response


class MFDCanisterLabel(object):
    """
        @class: MFDCanisterLabel
        @type: class
        @param: object
        @desc: Generates mfd canister label and returns file name
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], mfd_canister_label
            )
        else:
            return error(1001)

        return response


class UpdatePackLabelCount(object):
    """
        To add data in PrintQueue and PrintJobs(couch db) depending upon source of API call
    """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_job_count)
            return response
        else:
            return error(1001)


class AddPackLabelDataCouchDB(object):
    """
        To reset couch db document
    """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], add_label_count_request)
        else:
            return error(1001)

        return response


class BulkPrintPackLabelV2(object):
    """
    Controller for bulk print pack label request
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], bulk_print_pack_label_v2)
            return response
        else:
            return error(1001)


class ResetPrintJobCouchDB(object):
    """
    Controller for reset print job couch db document
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        logger.debug(kwargs)
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], reset_print_job_couch_db)
            return response
        else:
            return error(1001)
