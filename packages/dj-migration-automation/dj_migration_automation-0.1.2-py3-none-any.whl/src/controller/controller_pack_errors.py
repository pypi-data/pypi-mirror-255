import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.pack_errors import report_fill_errors_v2, report_fill_errors_single_slot_v2, \
    get_pack_fill_errors_v2, delete_fill_error_v2, get_pack_fill_errors_v2_new, \
    get_fill_errors_data_v2, store_error_packs, update_assignation, save_adjusted_error_qty, fix_error_pack, \
    fetch_patient_packs, verify_rph_pack, system_hold_packs, check_rph_pack


class GetPackFillErrors(object):
    """
    Controller for Errors in pack filling
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, pack_id=None, system_id=None, **kwargs):
        if pack_id is None or system_id is None:
            return error(1001, "Missing Parameter(s): pack_id or system_id.")

        args = {
            'pack_id': pack_id,
            'system_id': system_id
        }
        response = get_pack_fill_errors_v2_new(args)

        return response


class FillErrorsV2(object):
    """
    Controller for Errors in pack filling
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, pack_id=None, system_id=None, pack_rx_id=None, **kwargs):
        if pack_id is None or system_id is None:
            return error(1001, "Missing Parameter(s): pack_id or system_id.")

        args = {
            'pack_id': pack_id,
            'system_id': system_id,
            'pack_rx_id': pack_rx_id
        }
        response = get_pack_fill_errors_v2(args)

        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], report_fill_errors_v2
            )
        else:
            return error(1001)

        return response


class DeleteFillErrorsV2(object):
    """ Controller to delete reported fill error """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], delete_fill_error_v2)
        else:
            return error(1001)
        return response


class FillErrorPerSlotV2(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], report_fill_errors_single_slot_v2
            )
        else:
            return error(1001)

        return response


class FillErrorReportV2(object):
    """
    Controller for Report of errors in pack filling
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, system_id=None, time_zone=None, company_id=None, **kwargs):
        if from_date is None or to_date is None or system_id is None or time_zone is None or company_id is None:
            return error(1001, "Missing Parameter(s): from_date or to_date or system_id or time_zone or company_id.")

        args = {
            'from_date': from_date,
            'to_date': to_date,
            'system_id': system_id,
            'time_zone': time_zone,
            'company_id': company_id
        }
        response = get_fill_errors_data_v2(args)

        return response


class ReportErrorPack(object):
    """
    Controller for store reported error packs received from IPS
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], store_error_packs
            )
        else:
            return error(1001)

        return response


class UpdateFillErrorAssignee(object):
    """
    Controller for updating assignation for fixing fill error
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_assignation
            )
        else:
            return error(1001)

        return response


class SaveErrorAdjustment(object):
    """
    Controller for storing adjustment in qty after for resolving error
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], save_adjusted_error_qty
            )
        else:
            return error(1001)

        return response


class FixError(object):
    """
    Controller for marking pack when error is fixed
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], fix_error_pack
            )
        else:
            return error(1001)

        return response


class FetchPatientPacks(object):
    """
    Controller for fetching packs based on patient
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, rx_id=None, company_id=None, system_id=None, **kwargs):
        if not pack_id and not rx_id:
            return error(1001, "Missing Parameter(s): patient_id.")
        response = fetch_patient_packs(pack_id, rx_id, company_id, system_id)

        return response


class VerifyRphPacks(object):
    """
    Controller for marking pack when error is fixed
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], verify_rph_pack
            )
        else:
            return error(1001)

        return response


class PackHoldSync(object):
    """
    Controller for marking pack on system hold from IPS
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], system_hold_packs
            )
        else:
            return error(1001)

        return response


class IsRphPack(object):
    """
    Controller for checking whether pack is rph or not
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_display_id, company_id=None, system_id=None,**kwargs):
        if not pack_display_id:
            return error(1001, "Missing Parameter(s): patient_id.")
        response = check_rph_pack(pack_display_id, company_id, system_id)

        return response
