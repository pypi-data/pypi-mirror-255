from peewee import IntegrityError, InternalError

import settings
from dosepack.error_handling.error_handler import error, create_response
from dosepack.validation.validate import validate
from src.dao.drug_canister_stick_dao import add_small_stick_rule, add_drug_rule, add_shape_rule
from src.dao.drug_dao import get_custome_drug_shape_dao
from src.exceptions import DuplicateCanisterParameterRuleException

canister_parameter_rules = settings.CANISTER_PARAMETER_RULES
logger = settings.logger


@validate(required_fields=["rule_key", "rule_value"])
def add_parameter_rules(rule_info):
    """
    Creates canister parameter rules
    - takes parameter rule name and rule value and associated canister parameters
    - if no parameter record exist then new entry will be created for canister parameters
    :return: str
    """
    response = False
    rule_key = rule_info.pop('rule_key')
    if rule_key not in canister_parameter_rules:
        return error(1020, "The parameter rule_key can only be one of the following."
                           " {}.".format(list(canister_parameter_rules)))
    try:
        parameters = _get_canister_parameter_dict(rule_info)
        if rule_key == 'shape':
            response = add_shape_rule(rule_info, parameters)
        if rule_key == 'small_stick':
            response = add_small_stick_rule(rule_info, parameters)
        if rule_key == 'drug':
            response = add_drug_rule(rule_info, parameters)

        return create_response(response)
    except DuplicateCanisterParameterRuleException as e:
        logger.error(e, exc_info=True)
        return error(1029)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(0, e)


def _get_canister_parameter_dict(params):
    """ Helper function to create dict to insert into canister parameter """
    parameter_keys = ['speed', 'cw_timeout', 'ccw_timeout',
                      'drop_timeout', 'wait_timeout', 'pill_wait_time']
    # all(item in for item in parameter_keys) check if validation needed
    parameters = {k: params.get(k) or None for k in parameter_keys}
    return parameters


def get_custom_drug_shape(rules_required):
    """
    Returns list of custom drug shape defined for volumetric analysis of drugs
    :return: str
    """
    try:
        results = get_custome_drug_shape_dao()
        if rules_required:
            for data in results:
                data["rules"] = settings.DRUG_SHAPE_ID_CONSTANTS[data["name"]]["parameters"]
        return create_response(results)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
