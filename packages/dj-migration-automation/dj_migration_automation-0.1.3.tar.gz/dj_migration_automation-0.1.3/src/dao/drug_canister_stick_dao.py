import functools
import operator
import os
import sys
from sqlite3 import InternalError
from typing import Any

from peewee import DoesNotExist, JOIN_LEFT_OUTER, IntegrityError, fn, InternalError, DataError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response, log_args
from dosepack.validation.validate import validate
from src.dao.canister_dao import update_canister_stick_of_canister
from src.model.model_canister_drum import CanisterDrum
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src.exceptions import DuplicateCanisterParameterRuleException, DuplicateSerialNumber, ArgumentMissingException
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_canister_parameters import CanisterParameters
from src.model.model_canister_stick import CanisterStick
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_custom_shape_canister_parameters import CustomShapeCanisterParameters
from src.model.model_drug_canister_parameters import DrugCanisterParameters
from src.model.model_drug_canister_stick_mapping import DrugCanisterStickMapping
from src.model.model_drug_dimension import DrugDimension
from src.model.model_missing_stick_recommendation import MissingStickRecommendation
from src.model.model_small_canister_stick import SmallCanisterStick
from src.model.model_small_stick_canister_parameters import SmallStickCanisterParameters


canister_parameter_rules = settings.CANISTER_PARAMETER_RULES

logger = settings.logger


@log_args_and_response
def get_missing_stick_recommendation_by_id(required_id):
    """

    :param required_id:
    :return:
    """
    db_result: dict = dict()

    try:
        query = MissingStickRecommendation.select(DrugMaster.drug_name, DrugMaster.ndc, DrugMaster.txr,
                                                  MissingStickRecommendation.length, MissingStickRecommendation.width,
                                                  MissingStickRecommendation.depth, MissingStickRecommendation.fillet,
                                                  CustomDrugShape.name, MissingStickRecommendation.company_id,
                                                  MissingStickRecommendation.is_manual,
                                                  MissingStickRecommendation.user_id) \
            .join(UniqueDrug, on=MissingStickRecommendation.unique_drug_id == UniqueDrug.id) \
            .join(DrugMaster, on=UniqueDrug.drug_id == DrugMaster.id) \
            .join(CustomDrugShape, on=MissingStickRecommendation.shape_id == CustomDrugShape.id) \
            .where(MissingStickRecommendation.id == required_id)

        return query.dicts().get()
    except DoesNotExist:
        return db_result
    except Exception as e:
        logger.error("Error in get_missing_stick_recommendation_by_id".format(e))
        return db_result


@log_args_and_response
def db_get_drugs_for_rule_query_sscp(select_fields):
    """
    Returns query to get drugs covered by a small stick rule
    :param select_fields: List of peewee.Field
    :return: peewee.SelectQuery
    """
    try:
        select_fields.append(SmallStickCanisterParameters.id.alias('rule_id'))
        query = SmallStickCanisterParameters.select(*select_fields) \
            .join(CanisterParameters, on=CanisterParameters.id == SmallStickCanisterParameters.canister_parameter_id) \
            .join(SmallCanisterStick, on=SmallCanisterStick.id == SmallStickCanisterParameters.small_stick_id) \
            .join(CanisterStick, on=CanisterStick.small_canister_stick_id == SmallCanisterStick.id) \
            .join(DrugCanisterStickMapping, on=DrugCanisterStickMapping.canister_stick_id == CanisterStick.id) \
            .join(DrugDimension, on=DrugDimension.id == DrugCanisterStickMapping.drug_dimension_id) \
            .join(UniqueDrug, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(DrugMaster, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                  & (DrugMaster.txr == UniqueDrug.txr))) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape)
        return query
    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_get_drugs_for_rule_query_sscp".format(e))
        raise


@validate(required_fields=['user_id', 'rule_value'])
@log_args_and_response
def add_small_stick_rule(rule, parameters):
    """

    @param rule:
    @param parameters:
    @return:
    """
    user_id = rule['user_id']
    small_stick_id = rule['rule_value']

    with db.transaction():
        cp, _ = CanisterParameters.db_get_or_create(rule['user_id'], **parameters)
        try:
            if 'rule_id' in rule:
                SmallStickCanisterParameters.db_update(rule['rule_id'], cp.id, user_id)
            else:
                SmallStickCanisterParameters.db_create(small_stick_id, cp.id, user_id)
            return True
        except IntegrityError as e:
            logger.error("Error in add_small_stick_rule".format(e))
            raise DuplicateCanisterParameterRuleException


@log_args_and_response
def add_drug_rule(rule, parameters):
    """

    @param rule:
    @param parameters:
    @return:
    """
    user_id = rule['user_id']
    unique_drug_id = rule['rule_value']

    with db.transaction():
        cp, _ = CanisterParameters.db_get_or_create(rule['user_id'], **parameters)
        try:
            if 'rule_id' in rule:
                DrugCanisterParameters.db_update(rule['rule_id'], cp.id, user_id)
            else:
                DrugCanisterParameters.db_create(unique_drug_id, cp.id, user_id)
            return True
        except IntegrityError as e:
            logger.error("Error in add_drug_rule".format(e))
            raise DuplicateCanisterParameterRuleException


@validate(required_fields=['rule_value', 'user_id'])
@log_args_and_response
def add_shape_rule(rule, parameters):
    """

    @param rule:
    @param parameters:
    @return:
    """
    user_id = rule['user_id']
    custom_shape_id = rule['rule_value']

    with db.transaction():
        cp, _ = CanisterParameters.db_get_or_create(rule['user_id'], **parameters)
        try:
            if 'rule_id' in rule:  # update rule with new parameter
                CustomShapeCanisterParameters.db_update(rule['rule_id'], cp.id, user_id)
            else:
                CustomShapeCanisterParameters.db_create(custom_shape_id, cp.id, user_id)
            return True
        except IntegrityError as e:
            logger.error("Error in add_shape_rule".format(e))
            raise DuplicateCanisterParameterRuleException


@log_args_and_response
def db_get_drugs_for_rule_query_cscp(select_fields):
    """
    Returns query to get drugs covered by a shape rule
    :param select_fields: List of peewee.Field
    :return: peewee.SelectQuery
    """
    try:
        select_fields.append(CustomShapeCanisterParameters.id.alias('rule_id'))
        query = CustomShapeCanisterParameters.select(*select_fields) \
            .join(CustomDrugShape, on=CustomDrugShape.id == CustomShapeCanisterParameters.custom_shape_id) \
            .join(DrugDimension, on=DrugDimension.shape == CustomDrugShape.id) \
            .join(UniqueDrug, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(DrugMaster, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                  & (DrugMaster.txr == UniqueDrug.txr)))
        return query
    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_get_drugs_for_rule_query_cscp".format(e))
        raise


@log_args_and_response
def db_get_drugs_for_rule_query_dcp(select_fields):
    """
    Returns query to get drugs covered by a drug rule
    :param select_fields: List of peewee.Field
    :return: peewee.SelectQuery
    """
    try:
        select_fields.append(DrugCanisterParameters.id.alias('rule_id'))
        query = DrugCanisterParameters.select(*select_fields) \
            .join(UniqueDrug, on=UniqueDrug.id == DrugCanisterParameters.unique_drug_id) \
            .join(DrugMaster, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                  & (DrugMaster.txr == UniqueDrug.txr))) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=DrugDimension.shape == CustomDrugShape.id)
        return query
    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_get_drugs_for_rule_query_dcp".format(e))
        raise


@log_args_and_response
def get_big_canister_stick_from_range(from_width, to_width, from_depth, to_depth, serial_number):
    """
    Function to get details about big canister stick data based on range of value for width and depth
    along with serial_number : optional argument.
    @param from_width:
    @param to_width:
    @param from_depth:
    @param to_depth:
    @param serial_number:
    :return:
    """
    clauses = list()
    canister_stick_data = list()

    if from_width is not None and to_width is not None:
        clauses.append(between_expression(BigCanisterStick.width, from_width, to_width))
    if from_depth is not None and to_depth is not None:
        clauses.append(between_expression(BigCanisterStick.depth, from_depth, to_depth))
    if serial_number:
        clauses.append((BigCanisterStick.serial_number == serial_number))

    try:
        query = BigCanisterStick.select(BigCanisterStick.id,
                                        BigCanisterStick.width,
                                        BigCanisterStick.depth,
                                        BigCanisterStick.serial_number,
                                        fn.COUNT(CanisterStick.id).alias("mapping_count")).dicts() \
            .join(CanisterStick, JOIN_LEFT_OUTER,
                  on=BigCanisterStick.id == CanisterStick.big_canister_stick_id) \
            .group_by(BigCanisterStick.id)
        if clauses:
            query = query.where(functools.reduce(operator.and_, clauses))
        for record in query:
            canister_stick_data.append(record)
        return canister_stick_data
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_big_canister_stick_from_range {}".format(e))
        raise e


@log_args_and_response
def get_big_canister_stick_by_value(width, depth):
    """
    Function to get big canister data for given width and depth.
    @param width:
    @param depth:
    :return:
    """
    canister_stick_data = list()

    try:
        query = BigCanisterStick.select(BigCanisterStick.id,
                                        BigCanisterStick.width,
                                        BigCanisterStick.depth,
                                        BigCanisterStick.serial_number,
                                        fn.COUNT(CanisterStick.id).alias("mapping_count")).dicts() \
            .join(CanisterStick, JOIN_LEFT_OUTER,
                  on=BigCanisterStick.id == CanisterStick.big_canister_stick_id) \
            .group_by(BigCanisterStick.id).where((BigCanisterStick.width == width),
                                                 (BigCanisterStick.depth == depth))
        for record in query:
            canister_stick_data.append(record)
        return canister_stick_data
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_big_canister_stick_by_value".format(e))
        raise


def between_expression(field, from_val, to_val):
    """builds peewee expression using between"""
    return field.between(from_val, to_val)


@log_args_and_response
def missing_stick_recomm_get_or_create(width, depth, unique_drug_id, length, fillet,
                                    shape_id, company_id, is_manual, image_url, user_id) -> tuple:
    """
    Function to get or create missing stick recommendation
    @param user_id:
    @param image_url:
    @param fillet:
    @param is_manual:
    @param shape_id:
    @param company_id:
    @param length:
    @param unique_drug_id:
    @param width:
    @param depth:
    :return:
    """
    try:
        return MissingStickRecommendation.get_or_create(width=width,
                                                 depth=depth,
                                                 unique_drug_id=unique_drug_id,
                                                 length=length,
                                                 fillet=fillet,
                                                 shape_id=shape_id,
                                                 company_id=company_id,
                                                 is_manual=is_manual,
                                                 image_url=image_url,
                                                 user_id=user_id)
    except (InternalError, IntegrityError) as e:
        logger.error("error in missing_stick_recomm_get_or_create {}".format(e))
        raise e


@log_args_and_response
def get_recom_new_drug_dimension_data(unique_drug_id: list, small_stick_id: int) -> Any:
    """
    function to get recommended new drug dimension ,stick data
    @param small_stick_id:
    @param unique_drug_id:
    @return:
    """
    try:
        query = DrugDimension.select(DrugCanisterStickMapping.canister_stick_id,
                                             CanisterStick.big_canister_stick_id, CanisterStick.small_canister_stick_id,
                                             BigCanisterStick.id.alias("big_stick_id"),
                                             SmallCanisterStick.id.alias("small_stick_id"),
                                             BigCanisterStick.width.alias("big_stick_width"),
                                             BigCanisterStick.depth.alias("big_stick_depth"),
                                             BigCanisterStick.serial_number.alias("big_stick_serial_number"),
                                             SmallCanisterStick.length.alias("small_stick_length")).join(
                    DrugCanisterStickMapping,
                    on=DrugCanisterStickMapping.drug_dimension_id == DrugDimension.id).join(
                    CanisterStick, on=CanisterStick.id == DrugCanisterStickMapping.canister_stick_id).join(
                    BigCanisterStick,
                    on=CanisterStick.big_canister_stick_id == BigCanisterStick.id).join(
                    SmallCanisterStick,
                    on=SmallCanisterStick.id == CanisterStick.small_canister_stick_id).where(
                    (DrugDimension.unique_drug_id.in_(unique_drug_id)),
                    (SmallCanisterStick.id == small_stick_id))

        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_recom_new_drug_dimension_data {}".format(e))
        raise e


@log_args_and_response
def get_big_canister_stick_dimension_id_dao() -> list:
    """
    get big canister stick dimension id
    """
    try:
        return BigCanisterStick.get_big_canister_stick_dimension_id()
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_big_canister_stick_dimension_id_dao:  {}".format(e))
        raise e


@log_args_and_response
def get_big_canister_stick_by_bs_serial_number_dao(bs_serial_number: str) -> int:
    """
    function to get big canister stick id for given bs_serial_number.
    """
    try:
        return BigCanisterStick.get_big_canister_stick_by_bs_serial_number(bs_serial_number=bs_serial_number)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_big_canister_stick_by_bs_serial_number_dao:  {}".format(e))
        raise e


@log_args_and_response
def get_small_canister_stick_by_ss_serial_number_dao(ss_serial_number: str) -> int:
    """
     Function to get small canister stick id for given ss_serial_number.
    """
    try:
        return SmallCanisterStick.get_small_canister_stick_by_ss_serial_number(ss_serial_number=ss_serial_number)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_small_canister_stick_by_ss_serial_number_dao:  {}".format(e))
        raise e


@log_args_and_response
def get_canister_drum_id_by_drum_serial_number_dao(drum_serial_number: str) -> int:
    """
      Function to get canister_drum_id for given drum_serial_number.
    """
    try:
        return CanisterDrum.get_canister_drum_id_by_drum_serial_number(drum_serial_number=drum_serial_number)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_drum_id_by_drum_serial_number_dao:  {}".format(e))
        raise e


@log_args_and_response
def get_canister_stick_by_big_stick_small_stick_canister_drum_dao(big_canister_stick_id: int, small_canister_stick_id: int, canister_drum_id: int) -> int:
    """
      Function to get canister stick id for given big_canister_stick_id, small_canister_stick_id, canister_drum_id.
    """
    try:
        return CanisterStick.get_canister_stick_by_big_stick_small_stick_canister_drum(big_canister_stick_id=big_canister_stick_id,
                                                                                       small_canister_stick_id=small_canister_stick_id,
                                                                                       canister_drum_id=canister_drum_id)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_stick_by_big_stick_small_stick_canister_drum_dao:  {}".format(e))
        raise e


@log_args_and_response
def add_canister_drum(canister_drum_data) -> int:
    """
    adds dimension for small canister stick
    :param canister_drum_data: dict
    :return: json
    """
    default_dict = dict()
    width = canister_drum_data['width']
    depth = canister_drum_data['depth']
    length = canister_drum_data['length']
    serial_number = canister_drum_data['serial_number']
    default_dict["created_by"] = canister_drum_data['user_id']
    default_dict["modified_by"] = canister_drum_data['user_id']
    try:
        record, created = CanisterDrum.get_or_create(width=width,
                                                     depth=depth,
                                                     length=length,
                                                     serial_number=serial_number,
                                                     defaults=default_dict)
        return record.id
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in add_canister_drum:  {}".format(e))
        raise e


@log_args_and_response
def db_get_canister_stick_id_by_big_stick_small_stick_dimension(big_stick_id_list: list, small_stick_length) -> tuple:
    """
        Get canister stick id by big stick ids and small stick length
        :param big_stick_id_list:
        :param small_stick_length:
        :return:
        """
    canister_stick_id_list: list = list()
    big_stick_serial_number_list: list = list()
    small_stick_serial_number_list: list = list()

    try:
        if big_stick_id_list:
            query = CanisterStick.select(CanisterStick.id.alias("Canister_Stick_Id"), BigCanisterStick.serial_number
                                         .alias("Big_Stick_Serial_Number"), SmallCanisterStick.length.alias
                                         ("Small_Stick_Serial_Number")).dicts().join(SmallCanisterStick,
                                                                                     on=SmallCanisterStick.id ==
                                                                                        CanisterStick.small_canister_stick_id) \
                .join(BigCanisterStick, on=BigCanisterStick.id == CanisterStick.big_canister_stick_id) \
                .where(CanisterStick.big_canister_stick_id << big_stick_id_list,
                       SmallCanisterStick.length == small_stick_length)

            for record in query:
                canister_stick_id_list.append(record["Canister_Stick_Id"])
                big_stick_serial_number_list.append(record["Big_Stick_Serial_Number"])
                small_stick_serial_number_list.append(record["Small_Stick_Serial_Number"])
            return canister_stick_id_list, big_stick_serial_number_list, small_stick_serial_number_list
        else:
            return canister_stick_id_list, big_stick_serial_number_list, small_stick_serial_number_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_stick_by_big_stick_small_stick_canister_drum_dao:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in db_get_canister_stick_id_by_big_stick_small_stick_dimension {}".format(e))
        raise e


@log_args_and_response
def add_canister_stick_mapping(map_data: dict, canister_id: int) -> Any:
    with db.transaction():
        try:
            # default_dict = dict()
            # drug_dimension_id = map_data["drug_dimension_id"]
            try:
                response_data = map_canister_stick(map_data)
            except DuplicateSerialNumber:
                return error(1028)
            except ArgumentMissingException:
                return error(1001, "Missing Parameter(s): drug_dimension_id or user_id.")

            status = update_canister_stick_of_canister(canister_id=canister_id, canister_stick_id=response_data['canister_stick_id'])
            logger.info('In add_canister_stick_mapping: update canister stick of canister: {}'.format(status))
            return create_response(response_data)
        except(InternalError, IntegrityError) as e:
            logger.error("Error in add_canister_stick_mapping {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in add_canister_stick_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(2001)
        except DataError as e:
            logger.error("Error in add_canister_stick_mapping {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in add_canister_stick_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in add_canister_stick_mapping: " + str(e))


@log_args_and_response
def map_canister_stick(map_data: dict) -> dict:
    """
    Function to add canister drum data or add big canister stick data or small canister stick data
    @param map_data:
    @return:
    """
    try:
        with db.transaction():
            big_canister_stick_id = map_data.get("big_canister_stick_id", None)
            small_canister_stick_id = map_data.get("small_canister_stick_id", None)
            drum_serial_number = map_data.get("drum_serial_number", None)

            if drum_serial_number:
                # check if we have data for given drum_serial_number, returns if exist or inserts new record
                canister_drum_id = add_canister_drum_data(map_data)
            else:
                canister_drum_id = None
                if not big_canister_stick_id:
                    if not "depth" in map_data or not "width" in map_data or not "serial_number":
                        raise ArgumentMissingException
                    big_canister_stick_id = add_big_canister_stick(map_data)
                if not small_canister_stick_id:
                    if not "length" in map_data:
                        raise ArgumentMissingException
                    small_canister_stick_id = add_small_canister_stick(map_data)

            canister_data = {"big_canister_stick_id": big_canister_stick_id,
                             "small_canister_stick_id": small_canister_stick_id,
                             "canister_drum_id": canister_drum_id,
                             "user_id": map_data["user_id"]
                             }
            canister_stick_id = add_canister_stick(canister_data)
            stick_ids = {"big_canister_stick_id": big_canister_stick_id,
                         "small_canister_stick_id": small_canister_stick_id,
                         "canister_drum_id": canister_drum_id,
                         "canister_stick_id": canister_stick_id
                         }
            return stick_ids

    except ValueError as e:
        logger.error("error in map_canister_stick {}".format(e))
        raise e
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in map_canister_stick {}".format(e))
        raise e


@log_args
def add_canister_drum_data(canister_stick_data: dict) -> int:
    """
    get or creates canister dimension for big canister stick
    :param canister_stick_data:  dict
    :return: json
    """
    default_dict = dict()
    width = canister_stick_data['drum_width']
    depth = canister_stick_data['drum_depth']
    length = canister_stick_data['drum_length']
    serial_number = canister_stick_data['drum_serial_number']
    default_dict["created_by"] = canister_stick_data['user_id']
    default_dict["modified_by"] = canister_stick_data['user_id']
    try:
        record, created = CanisterDrum.get_or_create(width=width,
                                                     depth=depth,
                                                     length=length,
                                                     serial_number=serial_number,
                                                     defaults=default_dict)

        return record.id
    except InternalError as e:
        logger.error("Error in add_canister_drum_data".format(e))
        raise
    except IntegrityError:
        raise DuplicateSerialNumber
    except DataError as e:
        logger.error("Error in add_canister_drum_data".format(e))
        raise


@log_args_and_response
def add_big_canister_stick(canister_stick_data: dict) -> int:
    """
    adds canister dimension for big canister stick
    :param canister_stick_data:  dict
    :return: json
    """
    default_dict = dict()
    width = canister_stick_data['width']
    depth = canister_stick_data['depth']
    serial_number = canister_stick_data['serial_number']
    default_dict["created_by"] = canister_stick_data['user_id']
    default_dict["modified_by"] = canister_stick_data['user_id']
    try:
        record, created = BigCanisterStick.get_or_create(width=width,
                                                         depth=depth,
                                                         serial_number=serial_number,
                                                         defaults=default_dict)
        return record.id
    except InternalError as e:
        logger.error("Error in add_big_canister_stick".format(e))
        return error(2001)
    except IntegrityError:
        raise DuplicateSerialNumber
    except DataError as e:
        logger.error("Error in add_big_canister_stick".format(e))
        return error(1012)

    except Exception as e:
        logger.error("Error in add_big_canister_stick {}".format(e))
        raise e


@log_args_and_response
def add_small_canister_stick(canister_stick_data: dict) -> int:
    """
    adds dimension for small canister stick
    :param canister_stick_data: dict
    :return: json
    """
    default_dict = dict()
    default_dict["created_by"] = canister_stick_data['user_id']
    default_dict["modified_by"] = canister_stick_data['user_id']
    try:
        record, created = SmallCanisterStick.get_or_create(length=canister_stick_data['length'],
                                                           defaults=default_dict)
        return record.id
    except (InternalError, IntegrityError) as e:
        logger.error("Error in add_small_canister_stick {}".format(e))
        raise e
    except DataError as e:
        logger.error("Error in add_small_canister_stick {}".format(e))
        raise e

    except Exception as e:
        logger.error("Error in add_small_canister_stick {}".format(e))
        raise e


@log_args_and_response
def add_canister_stick(canister_stick_data: dict) -> int:
    """
    adds canister stick info
    :param canister_stick_data: dict
    :return: json
    """
    big_canister_stick_id = canister_stick_data['big_canister_stick_id']
    small_canister_stick_id = canister_stick_data['small_canister_stick_id']
    canister_drum_id = canister_stick_data['canister_drum_id']
    default_dict = dict()
    default_dict["created_by"] = canister_stick_data['user_id']
    default_dict["modified_by"] = canister_stick_data['user_id']
    try:
        record, created = CanisterStick.get_or_create(big_canister_stick_id=big_canister_stick_id,
                                                      small_canister_stick_id=small_canister_stick_id,
                                                      canister_drum_id=canister_drum_id,
                                                      defaults=default_dict)
        return record.id
    except (InternalError, IntegrityError) as e:
        logger.error("Error in add_canister_stick {}".format(e))
        return error(2001)
    except DataError as e:
        logger.error("Error in add_canister_stick {}".format(e))
        return error(1012)
    except Exception as e:
        logger.error("Error in add_canister_stick {}".format(e))
        raise e
