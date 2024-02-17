import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.alternate_drug import get_selected_alternate_drug_list, update_saved_alternate_drug, \
    replenish_alternate_options, save_replenish_alternate, get_alternate_drugs, add_all_alternate_drug, \
    add_alternate_drug_data, get_alternate_drug_option, remove_alternate_drug_option, get_altered_drugs_of_pack, \
    update_alternate_drug_for_batch_manual_canister, get_manual_drug_manual_pack, save_alternate_drug, \
    alternate_drug_update_manual_packs


class AlternateDrugsPackPre(object):
    """
    Controller for alternate drugs selection in pack pre-processing .
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, batch_id=None, system_id=None, sort_fields=None, paginate=None, filter_fields=None,**kwargs):
        if company_id is None or batch_id is None or system_id is None:
            return error(1001, "Missing Parameter(s): company_id or batch_id or system_id.")
        data_dict = {
            'company_id': company_id,
            'batch_id': batch_id,
            'system_id': system_id,
        }
        try:

            if paginate is not None:
                data_dict["paginate"] = json.loads(paginate)
            if filter_fields:
                data_dict["filter_fields"] = json.loads(filter_fields)
            if sort_fields:
                data_dict["sort_fields"] = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        response = get_selected_alternate_drug_list(data_dict)

        return response


class UpdateAlternateDrugsPackPre(object):
    """
    Controller for alternate drugs selection after batch scheduling algo.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_saved_alternate_drug
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class ReplenishAlternates(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, canister_id=None, device_id=None, guided_transfer=False,
            batch_id=None, robot_utiltiy_call=False, **kwargs):
        if company_id is None or  canister_id is None or device_id is None:
            return error(1001, "Missing Parameter(s): company_id or canister_id or device_id.")
        response = replenish_alternate_options(company_id, canister_id, device_id, guided_transfer, batch_id,
                                               robot_utiltiy_call)
        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], save_replenish_alternate
            )
        else:
            return error(1001)

        return response


class AlternateManualDrugUpdate(object):
    """
          @type: class
          @param: object
          @desc: Updates alternate drugs for the packs assigned to user for manual fill
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], alternate_drug_update_manual_packs
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class AlternateDrug(object):
    """
    Returns Alternate drug and canister info for alternate drug
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, drug_id=None, company_id=None, sort_fields=None, paginate=None, **kwargs):
        if drug_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): drug_id or company_id.")

        args = {"drug_id": drug_id, "company_id": company_id, "device_id": device_id}
        if paginate is not None:
            args["paginate"] = json.loads(paginate)
        if sort_fields:
            args["sort_fields"] = json.loads(sort_fields)
        response = get_alternate_drugs(args)

        return response


class AddAllAlternateOption(object):
    """Controller to save all alternate option for particular batch_distribution"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], add_all_alternate_drug)
            return response
        else:
            return error(1001)


class MultipleAlternateDrug(object):
    """Controller to and  view alternate option for particular batch_distribution"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], add_alternate_drug_data)
        else:
            return error(1001)
        return response

    @use_database(db, settings.logger)
    def GET(self, company_id=None, facility_distribution_id=None, **kwargs):

        if not company_id or not facility_distribution_id:
            return error(1001, "Missing Parameter(s): facility_distribution_id or company_id.")
        else:
            response = get_alternate_drug_option(company_id=company_id, facility_distribution_id=facility_distribution_id)
            return response


class RemoveAlternateDrug(object):
    """Controller to remove alternate option for particular batch_distribution"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], remove_alternate_drug_option
            )
            return response
        else:
            return error(1001)


class GetAlteredDrugs(object):
    """
        @desc: get altered drugs of a pack if any.
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None):
        if pack_id is None:
            return error(1001, "Missing Parameter(s): pack_id.")
        args = {"pack_id": pack_id}
        return get_altered_drugs_of_pack(args)


class AlternateDrugUpdateMV(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_alternate_drug_for_batch_manual_canister)
        else:
            return error(1001)
        return response


class ManualAlternateDrug(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, drug_id=None, **kwargs):
        if not drug_id:
            return error(1001, "Missing Parameter(s): drug_id.")

        response = get_manual_drug_manual_pack(drug_id=drug_id)

        return response


class SaveAlternates(object):
    """
    Controller for alternate drugs selection after batch scheduling algo.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], save_alternate_drug
                )
                return response
            else:
                return error(1001)
        else:
            return error(1001)
