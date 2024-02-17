"""
    Controller for refill device flow
"""
import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.canister import update_canister_master
from src.service.refill_device import get_drug_data_calibration, save_calibration_data, get_drug_data_for_refilling, \
    get_drug_list_to_calibrate, update_canister_quantity, get_canister_drug_info


class DrugListToCalibrate(object):
    """
    Controller to get the drug list with calibration details.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, paginate=None, filters=None, sort_fields=None, company_id=None, **kwargs):
        try:
            if not company_id:
                return error(1001, "Missing Parameter(s): company_id")
            if paginate is not None:
                paginate = json.loads(paginate)
            if filters:
                filter_fields = json.loads(filters)
            else:
                filter_fields = None
            if sort_fields:
                sort_fields = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        try:
            response = get_drug_list_to_calibrate(filter_fields=filter_fields, paginate=paginate,
                                                  sort_fields=sort_fields, company_id=company_id)
        except Exception as ex:
            print(ex)
            return error(1004)

        return response


class GetDrugDataToRefill(object):
    """
        To validate and get drug details based on scanned bottle to refill given canister
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, canister_id=None, canister_drug_id=None, canister_ndc=None, canister_fndc=None, canister_txr=None,
                                scanned_ndc=None, no_of_records=None, **kwargs):
        if not canister_id or not canister_drug_id or not canister_fndc or not canister_txr or not scanned_ndc:
            return error(1001, "Missing Parameter(s): canister_id or canister_drug_id or canister_fndc or "
                               "canister_txr or scanned_ndc.")
        args = {
                "canister_id": canister_id,
                "canister_drug_id": canister_drug_id,
                "canister_ndc": canister_ndc,
                "canister_fndc": canister_fndc,
                "canister_txr": canister_txr,
                "scanned_ndc": scanned_ndc,
                "no_of_records": no_of_records if no_of_records else 3
                }
        return get_drug_data_for_refilling(args)


class DrugDataForCalibration(object):
    """
    @desc: To get drug details when scanned drug bottle.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, selected_drug=None, scanned_ndc=None, **kwargs):
        if scanned_ndc is None:
            return error(1001, "Missing Parameter(s): scanned_ndc.")

        args = {"selected_drug": selected_drug, "scanned_ndc": scanned_ndc}
        response = get_drug_data_calibration(args)

        return response


class UpdateCanisterQuantity(object):
    """
         @desc:  To update a refilled canister quantity
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_canister_master
            )
        else:
            return error(1001)

        return response


class SaveDrugCalibrationData(object):
    """Controller to save drug unit_weight"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], save_calibration_data
            )
        else:
            return error(1001)

        return response


class GetCanisterDrugInfo(object):
    """
          @class: Canisters
          @type: class
          @param: object
          @desc:  get the canister information for the given canister id
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, canister_id=None, company_id=None, transfer_data=False, **kwargs):
        if canister_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): canister_id or company_id")
        args = {
            "canister_id": canister_id,
            "company_id": company_id,
            "transfer_data": transfer_data
        }
        response = get_canister_drug_info(args)

        return response
