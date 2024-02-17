"""
    @file: controller_volumetric_analysis.py
    @type: file
    @desc: Provides Controller for Volumetric Analysis
"""
import json
from dosepack.utilities.manage_db_connection import use_database
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.validation.validate import validate_request_args
from dosepack.utilities.validate_auth_token import authenticate
from src.service.volumetric_analysis import \
    add_drug_dimension, update_drug_dimension, add_drug_canister_stick_mapping, \
    get_small_canister_stick, get_big_canister_stick, \
    delete_drug_canister_stick_mapping, update_drug_canister_stick_mapping, \
    get_drug_canister_stick_mapping, \
    get_drug_dimension_by_drug, get_recommendation_for_new_drug_sticks, \
    get_drug_shape_fields_by_shape, get_recommendation_for_canister_by_ndc, generate_canister_ndc, \
    get_drug_canister_recommendation_by_ndc_dimension, get_canister_parameter_rules, \
    get_canister_parameter_rule_drugs, get_drug_without_dimension, skip_drug_dimension_flow, get_drug_dimension_history, \
    get_canister_stick_details, get_drug_master_data, get_drug_master_count_stats, get_change_ndc_history, \
    get_canister_order_list
from src.service.drug_canister_stick import add_parameter_rules, get_custom_drug_shape
from src.service.canister import update_canister_ndc_multiple, update_canister_ndc, get_recommended_canisters
import settings


class GetDrugDimensionByDrug(object):
    """ Controller for getting drug dimension data from drug information """

    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, **kwargs):
        response = get_drug_dimension_by_drug(kwargs)
        return response


class GetDrugMasterData(object):
    """Controller for `GetDrugMasterData` Model"""
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, filters=None, sort_fields=None, paginate=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
        args = {"company_id": company_id}
        try:
            if paginate is not None:
                args["paginate"] = json.loads(paginate)
            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        try:
            response = get_drug_master_data(args)
        except Exception as ex:
            response = json.dumps({"error": str(ex), "status": settings.FAILURE})
        return response


class DrugDimension(object):
    exposed = True
    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"],
                add_drug_dimension
            )
            return response
        else:
            return error(1001)


class UpdateDrugDimension(object):
    """Controller for `DrugDimension` Model"""

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"],
                update_drug_dimension
            )
            return response
        else:
            return error(1001)


class SmallCanisterStick(object):
    """Controller for 'SmallCanisterStick' model"""

    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, **kwargs):
        response = get_small_canister_stick(kwargs)
        return response


class BigCanisterStick(object):
    """Controller for 'BigCanisterStick' model"""

    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, **kwargs):
        response = get_big_canister_stick(kwargs)
        return response


class DrugCanisterStickMapping(object):
    """Controller for 'DrugCanisterStickMapping' model"""

    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, **kwargs):
        paginate = kwargs.get('paginate', None)
        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')
        response = get_drug_canister_stick_mapping(kwargs)
        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], add_drug_canister_stick_mapping)
            return response
        else:
            return error(1001)


class DeleteDrugCanisterStickMapping(object):
    """Controller for 'DrugCanisterStickMapping' model"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], delete_drug_canister_stick_mapping)
            return response
        else:
            return error(1001)


class UpdateDrugCanisterStickMapping(object):
    """Controller for 'DrugCanisterStickMapping' model"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_drug_canister_stick_mapping)
            return response
        else:
            return error(1001)


class CustomDrugShape(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, rules_required=0):
        response = get_custom_drug_shape(rules_required)
        return response


class CanisterParameterRules(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, filters=None, sort_fields=None, paginate=None):
        try:
            args = dict()
            if paginate is not None:
                args["paginate"] = json.loads(paginate)
            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
            return get_canister_parameter_rules(args)
        except json.JSONDecodeError as e:
            return error(1020, str(e))

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        """ Add different rules to be applied on canister parameter """
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], add_parameter_rules)
            return response
        else:
            return error(1001)


class CanisterParameterRuleDrugs(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, rule_key=None, rule_id=None, filters=None, sort_fields=None, paginate=None):
        try:
            if rule_key is None or rule_id is None:
                return error(1001, "Missing Parameter(s): rule_key or rule_id.")

            args = {'rule_key': rule_key, 'rule_id': rule_id}
            if paginate is not None:
                args["paginate"] = json.loads(paginate)
            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
            return get_canister_parameter_rule_drugs(args)
        except json.JSONDecodeError as e:
            return error(1020, str(e))


class RecommendCanisterSticks(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, drug_id=0, length=0, width=0, depth=0, fillet=0, shape_id=0, user_id=1, **kwargs):
        if not drug_id or not shape_id:
            return error(1001, "Missing Parameter(s): drug_id or shape_id.")
        try:
            response = get_recommendation_for_new_drug_sticks(drug_id=drug_id, length=length, width=width, depth=depth,
                                                              fillet=fillet, shape_id=shape_id, user_id=user_id)
            return response
        except json.JSONDecodeError as e:
            return error(1020, str(e))


class RecommendCanisterSticksOptimized(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, ndc=None, depth=0, width=0, length=0, fillet=0, strength_value=None, strength=None,
            shape=None, drug_name=None, **kwargs):
        if ndc is not None or (depth is not None and width is not None and length is not None and fillet is not None
                               and strength is not None and strength_value is not None and shape is not None and
                               drug_name is not None):
            args = {"ndc": ndc, "depth": depth, "width": width, "length": length, "fillet": fillet,
                    "strength": strength,
                    "strength_value": strength_value, "shape": shape, "drug_name": drug_name}
        else:
            return error(1001,
                         "Missing Parameter(s): enter either ndc or all drug dimension parameter: depth, width, "
                         "length, fillet, strength_value, strength, shape, drug_name")
        try:
            response = get_drug_canister_recommendation_by_ndc_dimension(args)
            return response
        except json.JSONDecodeError as e:
            return error(1020, str(e))


class DrugShapeFields(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, shape_id=0):
        if not shape_id:
            return error(1001, "Missing Parameter(s): shape_id.")
        try:
            response = get_drug_shape_fields_by_shape(shape_id=shape_id)
            return response
        except json.JSONDecodeError as e:
            return error(1020, str(e))


class GetMappedCanisterList(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, system_id=None, company_id=None, ndc=None):

        if not system_id:
            return error(1001, "Missing Parameter(s): system_id.")
        try:
            response = get_recommendation_for_canister_by_ndc(company_id, system_id, ndc)
            return response

        except json.JSONDecodeError as e:
            return error(1020, str(e))


class SaveMappedCanister(object):
    """Controller for 'DrugCanisterStickMapping' model"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_canister_ndc)
            print("response of update_canister_ndc ", response)
            return response

        else:
            return error(1001)


class SaveMappedCanisterMultiple(object):
    """Controller for 'DrugCanisterStickMapping' model"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_canister_ndc_multiple)
            print("response of update_canister_ndc ", response)
            return response

        else:
            return error(1001)


class GenerateCanisterForNdc(object):
    """Controller for 'DrugCanisterStickMapping' model"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], generate_canister_ndc)
            return response
        else:
            return error(1001)


class DrugMasterCountStats(object):
    """Controller for `DrugDimensionCountStats` Model"""
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id ")

        dict_drug_master_info = {"company_id": company_id}

        response = get_drug_master_count_stats(dict_drug_master_info)

        return response


class DrugsWODimension(object):
    """
    Returns drug list which does not have dimension and are used in pharmacy.
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, filters=None, sort_fields=None, paginate=None,
            only_pending_facility=0):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
        try:
            filter_fields = None
            if paginate is not None:
                paginate = json.loads(paginate)
            if filters:
                filter_fields = json.loads(filters)
            if sort_fields:
                sort_fields = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        response = get_drug_without_dimension(company_id,
                                              filter_fields,
                                              sort_fields,
                                              paginate,
                                              only_pending_facility=bool(int(only_pending_facility)))
        return response


class SkipDrugDimensionFlow(object):
    """
    to update status as a skipped in FrequentMfdDrugs table
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], skip_drug_dimension_flow
                )
                return response
            else:
                return error(1001)
        else:
            return error(1001)


class GetDrugDimensionHistory(object):
    """
        to get history of drug dimension data
    """

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, drug_id=None):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
        args = {
            'company_id': company_id,
            'drug_id': drug_id
        }
        try:
            response = get_drug_dimension_history(args)
        except Exception as ex:
            response = json.dumps({"error": str(ex), "status": settings.FAILURE})
        return response

class GetCanisterStickRecommendProd(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, ndc=0, **kwargs):
        try:
            response = get_canister_stick_details()
            return response
        except json.JSONDecodeError as e:
            return error(1020, str(e))


class GetRecommendedCanisterForDrug(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, ndc_list=None, paginate=None, filters=None, sort_fields=None, company_id=None, **kwargs):
        try:
            filter_fields = {}
            if filters:
                filter_fields = json.loads(filters)
            if paginate:
                paginate = json.loads(paginate)
            if sort_fields:
                sort_fields = json.loads(sort_fields)
            response = get_recommended_canisters(ndc_list, filter_fields, paginate, sort_fields)
            return response
        except json.JSONDecodeError as e:
            return error(1020, str(e))


class GetChangeNdcHistory(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, paginate=None, filters=None, company_id=None, **kwargs):
        try:
            filter_fields = {}
            if filters:
                filter_fields = json.loads(filters)
            if paginate:
                paginate = json.loads(paginate)
            response = get_change_ndc_history(paginate, filter_fields)
            return response
        except json.JSONDecodeError as e:
            return error(1020, str(e))


class GetCanisterOrderList(object):
    """
    Controller to get drug list for which can be ordered
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, paginate, company_id=None, filters=None, **kwargs):
        try:

            if paginate:
                paginate = json.loads(paginate)
            filter_fields = {}
            if filters:
                filter_fields = json.loads(filters)
            response = get_canister_order_list(paginate, company_id, filter_fields)
            return response
        except json.JSONDecodeError as e:
            return error(1020, str(e))
