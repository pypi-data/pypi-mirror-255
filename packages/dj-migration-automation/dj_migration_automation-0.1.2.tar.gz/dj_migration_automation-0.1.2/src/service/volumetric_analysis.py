# -*- coding: utf-8 -*-
"""
    src.volumetric_analysis
    ~~~~~~~~~~~~~~~~
    This module provides function to provide data of volumetric analysis

    Todo:

    :copyright: (c) 2015 by Dose pack LLC.

"""
import json
import math
import os
import sys
from collections import OrderedDict
from copy import deepcopy
from sqlite3 import InternalError
from typing import Dict

import pandas as pd
from peewee import InternalError, IntegrityError, DataError, DoesNotExist
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import get_current_date_time, call_webservice, log_args_and_response, log_args
from dosepack.validation.validate import validate
from src.dao.canister_dao import db_get_deactive_canisters, add_generate_canister_data, db_get_deactive_canisters_new
from src.dao.data_analysis_dao import get_drug_details_by_drug, get_canister_details_by_drug
from src.dao.drug_canister_stick_dao import get_missing_stick_recommendation_by_id, get_big_canister_stick_by_value, \
    get_big_canister_stick_from_range, missing_stick_recomm_get_or_create, get_recom_new_drug_dimension_data, \
    get_big_canister_stick_dimension_id_dao, get_big_canister_stick_by_bs_serial_number_dao, \
    get_small_canister_stick_by_ss_serial_number_dao, get_canister_drum_id_by_drum_serial_number_dao, \
    get_canister_stick_by_big_stick_small_stick_canister_drum_dao, add_canister_drum, \
    db_get_canister_stick_id_by_big_stick_small_stick_dimension, map_canister_stick, add_big_canister_stick, \
    add_small_canister_stick, add_canister_stick, canister_parameter_rules
from src.dao.drug_dao import get_drug_details_by_ndc, get_custome_drug_shape_by_id, get_fndc_txr_by_unique_id_dao, \
    get_drug_id_from_ndc, get_unique_drug_id_from_ndc, save_drug_dimension_image_to_drug_master
from src.dao.mfd_dao import update_status_in_frequent_mfd_drugs
from src.dao.volumetric_analysis_dao import get_drug_dimension_by_drug_name_ndc_dao, insert_drug_dimension_data_dao, \
    add_drug_canister_parameter_mapping, \
    get_drug_dimension_data_by_dimension_id, delete_drug_canister_parameter_by_unique_drug, \
    delete_drug_canister_stick_by_drug_dimension, update_drug_dimension_by_dimension_id, add_canister_parameters, \
    get_small_canister_stick_data, update_drug_canister_stick_mapping_by_dimension_id, delete_drug_canister_stick_by_id, \
    update_drug_canister_parameter_mapping, get_drugs_for_required_configuration, \
    get_small_canister_stick_data_by_length, get_drug_shape_fields_by_shape_id, get_drug_canister_stick_mapping_data, \
    get_canister_parameter_rule_dao, get_canister_parameter_rule_drugs_dao, get_drugs_wo_dimension_dao, \
    add_drug_dimension_history_data, update_data_in_unique_drug, get_drug_dimension_history_dao, \
    drug_master_data, get_drug_master_count_data, get_change_ndc_history_dao, get_canister_order_list_dao
from src.exc_thread import ExcThread
from src.exceptions import DuplicateSerialNumber, ArgumentMissingException
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_canister_master import CanisterMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_master import DrugMaster
from src.model.model_unique_drug import UniqueDrug
from src.stick_recommandation import StickRecommender
from src.stick_recommandation_1 import StickRecommender1
from utils.utility_functions import read_data, converting_data_frame_to_dict_form

logger = settings.logger
canister_parameter_rules = settings.CANISTER_PARAMETER_RULES


def get_range(_dict, key, threshold_value=None):
    """Returns tuple of two values from `_dict` using `from_key` and `to_key` (in order)"""
    if not threshold_value:
        threshold_value = 1.0
    threshold_value = float(threshold_value)
    field_value = _dict.get(key, None)
    if field_value:
        field_value = float(field_value)
        from_value = field_value - threshold_value
        to_value = field_value + threshold_value
        return from_value, to_value
    return None, None


def cubic_volume(length, width, depth):
    """Returns volume using 3 dimensions of object"""
    return length * width * depth


@log_args_and_response
@validate(required_fields=["drug"])
def get_drug_dimension_by_drug(data):
    """
    returns drug dimension based on drug data
    :param data:
    :return:
    """
    drug_data = list()
    drug = data["drug"]
    drug = drug.translate(str.maketrans({'%': r'\%'}))  # escape % from search string
    drugsearch = "%" + drug + "%"
    ndc = drug.split(",")

    try:
        query = get_drug_dimension_by_drug_name_ndc_dao(drugsearch=drugsearch, ndc=ndc)
        for record in query:
            if record["ndc"]:
                # to show just name wherever required
                record["display_name"] = record["drug_name"]
                record["drug_name"] = record['concat_drug_name']
                record["countblacklist"] = 0
                drug_data.append(record)
        return create_response(drug_data)

    except (InternalError, IntegrityError, DataError, ValueError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension_by_drug: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_drug_dimension_by_drug {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension_by_drug: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_drug_dimension_by_drug: " + str(e))


@log_args
@validate(required_fields=["company_id"])
def get_drug_master_data(dimension_data: dict) -> dict:
    """
    Returns list of drugs and its dimension data
    :param dimension_data: dict
    :return: json
    """
    company_id = dimension_data.get('company_id')
    filter_fields = dimension_data.get('filter_fields', None)
    sort_fields = dimension_data.get('sort_fields', None)
    paginate = dimension_data.get('paginate', None)
    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, ' Missing key(s) in paginate.')
    try:
        # get dimension data of drug
        results, count = drug_master_data(company_id=company_id, filter_fields=filter_fields,
                                          sort_fields=sort_fields, paginate=paginate)
        response_data = {"drug_data": results,
                         "number_of_records": count}
        return create_response(response_data)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_master_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_drug_dimension {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_drug_master_data: " + str(e))


@log_args_and_response
@validate(required_fields=["unique_drug_id", "user_id"])
def add_drug_dimension(dimension_data):
    """
    Adds drug dimension data to `DrugDimension`
    - will calculate approx_volume using length, width and depth

    @:param dimension_data: dict Data for drug dimension,
                           requires Keys: "unique_drug_id", "user_id", "length", "width", "depth"
    :return: json
    {'unique_drug_id': 5716, 'canister_parameters': {}, 'shape': 1, 'depth': 5, 'length': 13.9,
    'accurate_volume': None, 'user_id': 7, 'verification_status': 53, 'verified': 1, 'verified_by': 7,
    'company_id': 3, 'is_manual': 0,
    'image_url': '2022-09-13_05:35:22_707000150_33530_capsule_5.308_14.084_5.397676496872207_None.jpg',
    'missing_recommendation': 1,
    'auto_dimension': {'depth': 5.397676496872207, 'length': 14.084, 'shape': 1}}
    """
    canister_parameters: dict = dict()
    missing_recommendation: int = 0
    try:
        auto_dimension = None
        user_id = dimension_data["user_id"]
        verification_status_id = dimension_data.pop('verification_status', None)
        verified = dimension_data.pop('verified', None)
        auto_dimension_data = dimension_data.pop('auto_dimension', None)
        image_name = dimension_data.get('image_url', None)
        coating_type = dimension_data.pop('coating_type', None)
        is_zip_lock_drug = dimension_data.pop('is_zip_lock_drug', None)
        unique_drug_id = dimension_data['unique_drug_id']
        add_canister = dimension_data.pop('add_canister', False)
        unit_weight = dimension_data.pop('unit_weight', None)
        if not add_canister:
            is_powder_pill = dimension_data.pop('is_powder_pill', None)
            dosage_type = int(dimension_data.pop('dosage_type'))
            packaging_type = int(dimension_data.pop('packaging_type'))
        from_top_five_mfd_pop_up = dimension_data.pop('from_top_five_mfd_pop_up', None)
        if "canister_parameters" in dimension_data:
            canister_parameters = dimension_data.pop('canister_parameters')

        dimension_data["created_by"] = dimension_data["modified_by"] = dimension_data.pop("user_id")

        drug_shape_name = get_custome_drug_shape_by_id(id=dimension_data["shape"])
        logger.info("In add_drug_dimension: drug shape name: {}".format(drug_shape_name))
        if drug_shape_name is None:
            return create_response([])

        dimension_data = get_correct_dimensions(dimension_data)

        dimension_data = get_drug_dimension_parameters(dimension_data, drug_shape_name)
        logger.info("In add_drug_dimension: dimension data: {}".format(dimension_data))

        if "missing_recommendation" in dimension_data:
            missing_recommendation = int(dimension_data.pop("missing_recommendation"))
            if missing_recommendation:
                company_id = int(dimension_data.pop("company_id"))
                is_manual = int(dimension_data.pop("is_manual"))
                image_url = str(dimension_data.pop("image_url"))

        dimension_data["approx_volume"] = cubic_volume(
            dimension_data["length"],
            dimension_data["width"],
            dimension_data["depth"])

        logger.info("In add_drug_dimension: verified status id: {}".format(verification_status_id))

        if verification_status_id is not None:
            if 'verified_by' not in dimension_data:
                return error(1020, 'verified_by field is missing.')
            dimension_data['verification_status_id'] = verification_status_id
            if verification_status_id != settings.DRUG_VERIFICATION_STATUS['pending']:
                dimension_data['verified_date'] = get_current_date_time()

        if auto_dimension_data:
            auto_dimension = deepcopy(dimension_data)
            auto_dimension['shape'] = auto_dimension_data.get('shape', None)
            auto_dimension['depth'] = auto_dimension_data.get('depth', None)
            auto_dimension['image_name'] = image_name
            auto_dimension['width'] = auto_dimension_data.get('width', None)
            auto_dimension['fillet'] = auto_dimension_data.get('fillet', None)
            auto_dimension['length'] = auto_dimension_data.get('length', None)
            auto_dimension = get_drug_dimension_parameters(auto_dimension, drug_shape_name)
            auto_dimension["approx_volume"] = cubic_volume(
                auto_dimension["length"],
                auto_dimension["width"],
                auto_dimension["depth"])

        logger.info("In add_drug_dimension: dimension data: {}".format(dimension_data))
        with db.transaction():
            record_id = insert_drug_dimension_data_dao(dimension_data=dimension_data,
                                                       auto_dimension_data=auto_dimension,
                                                       from_top_five_mfd_pop_up=from_top_five_mfd_pop_up)

            t = ExcThread([], name='save_image_to_drug_master_thread',
                          target=save_drug_dimension_image_to_drug_master,
                          args=(unique_drug_id, image_name))
            t.start()

            if not add_canister:
                logger.info(f"In add_drug_dimension, updating data in unique_drug for unique_drug : {unique_drug_id}")
                status = update_data_in_unique_drug(unique_drug_id=unique_drug_id,
                                                    dosage_type=dosage_type,
                                                    packaging_type=packaging_type,
                                                    is_powder_pill=is_powder_pill,
                                                    coating_type=coating_type,
                                                    is_zip_lock_drug=is_zip_lock_drug,
                                                    unit_weight=unit_weight)
            logger.info(f"In add_drug_dimension, data updated in unique drug. status: {status}")

            if canister_parameters:
                canister_parameters_data = {
                    'speed': canister_parameters['speed'],
                    'user_id': user_id,
                    'wait_timeout': canister_parameters.get('wait_timeout', None),
                    'cw_timeout': canister_parameters.get('cw_timeout', None),
                    'ccw_timeout': canister_parameters.get('ccw_timeout', None),
                    'drop_timeout': canister_parameters.get('drop_timeout', None),
                    'pill_wait_time': canister_parameters.get('pill_wait_time', None)
                }
                canister_parameters_id = add_canister_parameters(canister_data=canister_parameters_data)
                drug_canister_parameters_mapping_data = {
                    "canister_parameter_id": canister_parameters_id,
                    "unique_drug_id": dimension_data["unique_drug_id"],
                    "user_id": user_id
                }
                drug_canister_parameter_id = add_drug_canister_parameter_mapping(mapping_data=drug_canister_parameters_mapping_data)
                logger.info("In add_drug_dimension: data added in drug canister parameter table: {}".format(drug_canister_parameter_id))
            if missing_recommendation:
                response = report_missing_canister_recommendation(unique_drug_id=dimension_data["unique_drug_id"],
                                                                  length=dimension_data["length"],
                                                                  width=dimension_data["width"],
                                                                  depth=dimension_data["depth"],
                                                                  fillet=dimension_data["fillet"],
                                                                  shape_id=dimension_data["shape"],
                                                                  company_id=company_id,
                                                                  is_manual=is_manual,
                                                                  image_url=image_url,
                                                                  user_id=user_id)
                logger.info("In add_drug_dimension: Response from missing canister recommendation: {}".format(response))

            return create_response(record_id)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        if e.args[0] == 1062:  # integrity of unique_drug_id failed
            return error(1019)
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_drug_dimension: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1012)
    except Exception as e:
        logger.error("Error in add_drug_dimension {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_drug_dimension: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in add_drug_dimension: " + str(e))


@log_args_and_response
@validate(required_fields=["id", "user_id"])
def update_drug_dimension(dimension_data):
    """
    Updates drug dimension data using id of `DrugDimension`
    - will calculate approx_volume using length, width and depth

     @:param dimension_data: dict requires Keys: "id", "user_id"
    :return: json
    """
    try:
        record_id = dimension_data.pop("id")
        user_id = dimension_data.pop("user_id")
        verified = dimension_data.pop('verified', 0)
        auto_dimension_data = dimension_data.pop('auto_dimension', None)
        image_name = dimension_data.get('image_url', None)
        verification_status = dimension_data.pop('verification_status', None)
        delete_mappings = dimension_data.pop('delete_mappings', True)
        unit_weight = dimension_data.pop('unit_weight', None)
        # as drug dimension is changes, parameter and stick mapping should be changed too
        dimension_data["modified_by"] = user_id
        dimension_data["modified_date"] = get_current_date_time()
        auto_dimension = None
        add_canister = dimension_data.pop("add_canister", False)
        if not add_canister:
            dosage_type = dimension_data.pop('dosage_type')
            if dosage_type is not None:
                dosage_type = int(dosage_type)
            packaging_type = dimension_data.pop('packaging_type')
            if packaging_type is not None:
                packaging_type = int(packaging_type)
            coating_type = dimension_data.pop('coating_type', None)
        is_powder_pill = dimension_data.pop('is_powder_pill', None)
        is_zip_lock_drug = dimension_data.pop('is_zip_lock_drug', None)

        drug_shape_name = get_custome_drug_shape_by_id(id=dimension_data["shape"])
        logger.info("In update_drug_dimension: drug shape name: {}".format(drug_shape_name))
        if drug_shape_name is None:
            return create_response([])

        dimension_data = get_drug_dimension_parameters(dimension_data, drug_shape_name)
        logger.info("In update_drug_dimension: dimension_data: {}".format(dimension_data))

        missing_recommendation = 0
        if "missing_recommendation" in dimension_data:
            missing_recommendation = int(dimension_data.pop("missing_recommendation"))
            if missing_recommendation:
                company_id = int(dimension_data.pop("company_id"))
                is_manual = int(dimension_data.pop("is_manual"))
                image_url = str(dimension_data.pop("image_url"))

        dimension_data["approx_volume"] = cubic_volume(
            dimension_data["length"],
            dimension_data["width"],
            dimension_data["depth"]
        )
        canister_parameters = dict()
        if 'canister_parameters' in dimension_data:
            canister_parameters = dimension_data.pop("canister_parameters")
        # if verified:
        #     if 'verified_by' not in dimension_data:
        #         return error(1020, ' verified_by field is missing.')
        #     dimension_data['verified'] = verified
        #     dimension_data['verified_date'] = get_current_date_time()
        # else:
        #     dimension_data['verified'] = False
        #     dimension_data['verified_date'] = None
        #     dimension_data['verified_by'] = 0
        logger.info("In update_drug_dimension: verification_status: {}".format(verification_status))
        if verification_status is not None:
            if 'verified_by' not in dimension_data:
                return error(1020, 'verified_by field is missing.')
            if verification_status == settings.DRUG_VERIFICATION_STATUS['rejected']:
                if 'rejection_note' not in dimension_data:
                    return error(1020, 'rejection_note field is missing.')

            dimension_data['verified_date'] = get_current_date_time()
            dimension_data['verification_status_id'] = verification_status

        else:
            dimension_data['verified_date'] = None
            dimension_data['verified_by'] = 0
        if auto_dimension_data:
            auto_dimension = deepcopy(dimension_data)
            auto_dimension['shape'] = auto_dimension_data.get('shape', None)
            auto_dimension['depth'] = auto_dimension_data.get('depth', None)
            auto_dimension['width'] = auto_dimension_data.get('width', None)
            auto_dimension['image_name'] = image_name
            auto_dimension['fillet'] = auto_dimension_data.get('fillet', None)
            auto_dimension['length'] = auto_dimension_data.get('length', None)
            auto_dimension = get_drug_dimension_parameters(auto_dimension, drug_shape_name)
            auto_dimension["approx_volume"] = cubic_volume(
                auto_dimension["length"],
                auto_dimension["width"],
                auto_dimension["depth"])
            auto_dimension['created_by'] = user_id

        drug_dimension_data = get_drug_dimension_data_by_dimension_id(dimension_id=record_id)
        logger.info("In update_drug_dimension: drug_dimension_data: {}".format(drug_dimension_data))
        with db.transaction():
            unique_drug_id = drug_dimension_data.pop("unique_drug_id")

            if delete_mappings:
                drug_canister_par_delete_status = delete_drug_canister_parameter_by_unique_drug(unique_drug_id=unique_drug_id)
                logger.info("In update_drug_dimension: data deleted from drug canister parameter mapping table: {}"
                            .format(drug_canister_par_delete_status))

                drug_canister_stick_delete_status = delete_drug_canister_stick_by_drug_dimension(drug_dimension_id=record_id)
                logger.info("In update_drug_dimension: data deleted from drug canister stick mapping table: {}".format(
                        drug_canister_stick_delete_status))

            if "image_url" in dimension_data:
                dimension_data.pop("image_url")
            status = update_drug_dimension_by_dimension_id(drug_dimension_id=record_id, update_dict=dimension_data)
            logger.info(f"In update_drug_dimension, updating data in unique_drug for unique_drug : {unique_drug_id}")
            if not add_canister:
                status = update_data_in_unique_drug(unique_drug_id=unique_drug_id,
                                                    dosage_type=dosage_type,
                                                    packaging_type=packaging_type,
                                                    is_powder_pill=is_powder_pill,
                                                    coating_type=coating_type,
                                                    is_zip_lock_drug=is_zip_lock_drug,
                                                    unit_weight=unit_weight)
            logger.info(f"In update_drug_dimension, data updated in unique drug. status: {status}")
            dimension_data['created_by'] = user_id
            add_drug_dimension_history_data(dimension_data=dimension_data, auto_dimension_data=auto_dimension,
                                            dimension_id=record_id)
            logger.info("In update_drug_dimension: drug dimension dat updated in drug dimension table: {}".format(status))

            if canister_parameters:
                drug_canister_parameter_mapping_data = {'user_id': user_id,
                                                        'unique_drug_id': unique_drug_id,
                                                        'speed': canister_parameters.get('speed', None),
                                                        'wait_timeout': canister_parameters.get('wait_timeout', None),
                                                        'cw_timeout': canister_parameters.get('cw_timeout', None),
                                                        'ccw_timeout': canister_parameters.get('ccw_timeout', None),
                                                        'drop_timeout': canister_parameters.get('drop_timeout', None),
                                                        'pill_wait_time': canister_parameters.get('pill_wait_time',
                                                                                                  None)
                                                        }
                mapping_status = update_drug_canister_parameter_mapping(drug_canister_parameter_mapping_data)
                logger.info("In update_drug_dimension: drug canister parameter mapping status: {}".format(mapping_status))

            if status:
                if missing_recommendation:
                    pass
                    response = report_missing_canister_recommendation(unique_drug_id=dimension_data["unique_drug_id"],
                                                                      length=dimension_data["length"],
                                                                      width=dimension_data["width"],
                                                                      depth=dimension_data["depth"],
                                                                      fillet=dimension_data["fillet"],
                                                                      shape_id=dimension_data["shape"],
                                                                      company_id=company_id,
                                                                      is_manual=is_manual,
                                                                      image_url=image_url,
                                                                      user_id=user_id)
                    logger.info("In update_drug_dimension: Response from missing canister recommendation: {}".format(response))
            return create_response(status)

    except DoesNotExist:
        logger.info('record not found while updating drug_dimension')
        return error(1020, 'Unable to find record using id.')

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_drug_dimension: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_drug_dimension {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_drug_dimension: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_drug_dimension: " + str(e))


@log_args_and_response
def get_big_canister_stick(fillters):
    """
    returns list of big canister stick
    :param fillters: dict
    :return: json
    """

    try:
        width_threshold = fillters.get("width_threshold", None)
        depth_threshold = fillters.get("depth_threshold", None)
        from_width, to_width = get_range(fillters, "width", width_threshold)
        from_depth, to_depth = get_range(fillters, "depth", depth_threshold)
        serial_number = fillters.get('serial_number', None)
        response = get_big_canister_stick_from_range(from_width, to_width, from_depth, to_depth,
                                                                  serial_number)
        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_big_canister_stick: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_big_canister_stick {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_big_canister_stick: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_big_canister_stick: " + str(e))


@log_args_and_response
def get_small_canister_stick(fillters):
    """
    returns list of small canister stick
    :param fillters: dict
    :return: json
    """
    length_threshold = fillters.get("length_threshold", None)
    from_length, to_length = get_range(fillters, "length", length_threshold)

    try:
        canister_stick_data = get_small_canister_stick_data(from_length=from_length, to_length=to_length)
        return create_response(canister_stick_data)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_small_canister_stick: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_small_canister_stick {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_small_canister_stick: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_small_canister_stick: " + str(e))


@validate(required_fields=['drug_dimension_id', 'user_id'])
def add_drug_canister_stick_mapping(map_data):
    """
    adds mapping of drug and canister stick
    :param map_data: dict
    :return: json
    """
    with db.transaction():
        try:
            default_dict = dict()
            drug_dimension_id = map_data["drug_dimension_id"]
            try:
                response_data = map_canister_stick(map_data)
            except DuplicateSerialNumber:
                return error(1028)
            except ArgumentMissingException:
                return error(1001, "Missing Parameter(s): drug_dimension_id or user_id.")
            # canister_stick_id = response_data["canister_stick_id"]
            # default_dict["created_by"] = map_data["user_id"]
            # default_dict["modified_by"] = map_data["user_id"]
            # record, created = DrugCanisterStickMapping.get_or_create(drug_dimension_id=drug_dimension_id,
            #                                                          canister_stick_id=canister_stick_id,
            #                                                          defaults=default_dict)
            # response_data["drug_canister_stick_mapping_id"] = record.id

            return create_response(response_data)
        except(InternalError, IntegrityError) as e:
            logger.error("Error in add_drug_canister_stick_mapping {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in add_drug_canister_stick_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(2001)
        except DataError as e:
            logger.error("Error in add_drug_canister_stick_mapping {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in add_drug_canister_stick_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in add_drug_canister_stick_mapping: " + str(e))


@validate(required_fields=['drug_dimension_id', 'user_id'])
def update_drug_canister_stick_mapping(map_data):
    """
    updates mapping of drug canister stick
    :param map_data:
    :return:
    """
    try:
        drug_canister_stick_mapping_data = dict()
        drug_dimension_id = map_data["drug_dimension_id"]
        try:
            stick_id_data = map_canister_stick(map_data)
        except DuplicateSerialNumber:
            return error(1028)
        except ArgumentMissingException:
            return error(1001, "Missing Parameter(s): drug_dimension_id or user_id.")
        drug_canister_stick_mapping_data["canister_stick_id"] = stick_id_data["canister_stick_id"]
        drug_canister_stick_mapping_data["created_by"] = map_data["user_id"]
        drug_canister_stick_mapping_data["modified_by"] = map_data["user_id"]
        status = update_drug_canister_stick_mapping_by_dimension_id(drug_dimension_id=drug_dimension_id,
                                                                    update_dict=drug_canister_stick_mapping_data)
        logger.info('In update_drug_canister_stick_mapping: update drug canister stick mapping by dimension id: {}'.format(status))
        return create_response(status)
    except(InternalError, IntegrityError) as e:
        logger.error("Error in update_drug_canister_stick_mapping {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_drug_canister_stick_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)
    except DataError as e:
        logger.error("Error in update_drug_canister_stick_mapping {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_drug_canister_stick_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_drug_canister_stick_mapping: " + str(e))


@validate(required_fields=['drug_canister_stick_mapping_id'])
def delete_drug_canister_stick_mapping(map_data):
    """
    deletes mapping of drug and canister stick
    :param map_data: dict
    :return: json
    """
    drug_canister_stick_mapping_id = map_data["drug_canister_stick_mapping_id"]
    try:
        status = delete_drug_canister_stick_by_id(drug_canister_stick_mapping_id=drug_canister_stick_mapping_id)
        logger.info('In delete_drug_canister_stick_mapping: drug canister stick mapping data deleted: {}'.format(status))

        return create_response(status)

    except(InternalError, IntegrityError) as e:
        logger.error("Error in add_canister_stick_mapping {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_drug_canister_stick_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)
    except DataError as e:
        logger.error("Error in delete_drug_canister_stick_mapping {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_drug_canister_stick_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1012)


@log_args_and_response
def get_drug_canister_stick_mapping(map_data):
    """
     get mapping of drug and canister stick
    :param map_data:
    :return:
    """
    filter_fields = sort_fields = paginate = None
    try:
        if 'filters' in map_data:
            filter_fields = json.loads(map_data['filters'])
        if 'sort_fields' in map_data:
            sort_fields = json.loads(map_data['sort_fields'])
        if 'paginate' in map_data:
            paginate = json.loads(map_data["paginate"])
    except json.JSONDecodeError as e:
        return error(1020, str(e))
    try:
        drug_canister_stick_mapping_list, count = get_drug_canister_stick_mapping_data(filter_fields=filter_fields, sort_fields=sort_fields, paginate=paginate)
        return create_response(
            {"drug_canister_stick_mapping_data": drug_canister_stick_mapping_list, "number_of_records": count})

    except(InternalError, IntegrityError) as e:
        logger.error("Error in get_drug_canister_stick_mapping {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_canister_stick_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)
    except DataError as e:
        logger.error("Error in get_drug_canister_stick_mapping {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_canister_stick_mapping: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_drug_canister_stick_mapping: " + str(e))


@log_args_and_response
def get_drug_dimension_parameters(drug_dimension_data, drug_shape_name):
    """
    get drug dimension parameters
      :return:
      @param drug_shape_name:
      @param drug_dimension_data:
    """
    try:
        if not settings.DRUG_SHAPE_ID_CONSTANTS[drug_shape_name]["parameters"]:
            return drug_dimension_data

        else:
            required_rules_list = settings.DRUG_SHAPE_ID_CONSTANTS[drug_shape_name]["parameters"]

            for element in required_rules_list:
                for req_key in element:
                    try:
                        drug_dimension_data[req_key] = drug_dimension_data[element[req_key]]
                    except Exception as e:
                        drug_dimension_data[req_key] = element[req_key]

        return drug_dimension_data

    except Exception as e:
        logger.error("error in get_drug_dimension_parameters {}".format(e))
        raise e


@log_args_and_response
def get_drug_canister_recommendation_by_dimension(width, depth, shape_id):
    """
      get drug canister recommendation by dimension
      @param shape_id:
      @param depth:
      @param width:
    """
    try:
        if int(shape_id) == settings.DRUG_SHAPE_ID_CONSTANTS["Capsule"]["shape_id"]:
            return {}

        elif int(shape_id) == settings.DRUG_SHAPE_ID_CONSTANTS["Round Curved"]["shape_id"]:
            required_dict = {"width": width, "depth": depth}
            from_width, to_width = get_range(required_dict, "width", 0.6)
            from_depth, to_depth = get_range(required_dict, "depth", 0.5)
            response = get_big_canister_stick_from_range(from_width, to_width, from_depth, to_depth, None)

            if response:
                response_dict = {"big_stick_id": response[0]["id"], "big_stick_width": response[0]["width"],
                                 "big_stick_depth": response[0]["depth"],
                                 "big_stick_serial_number": response[0]["serial_number"], }
                return response_dict
            else:
                return {}

        elif int(shape_id) in [settings.DRUG_SHAPE_ID_CONSTANTS["Oval"]["shape_id"],
                               settings.DRUG_SHAPE_ID_CONSTANTS["Round Flat"]["shape_id"]]:
            required_dict = {"width": -1, "depth": -1}
            for req_tuple in settings.DRUG_WIDTH_TUPLE_STICK_LIST:
                if float(width) > req_tuple[0]:
                    required_dict["width"] = req_tuple[1]
                    break

            for req_tuple in settings.DRUG_DEPTH_TUPLE_STICK_LIST:
                if float(depth) > req_tuple[0]:
                    required_dict["depth"] = req_tuple[1]
                    break

            if -1 not in required_dict.values():
                response = get_big_canister_stick_by_value(required_dict["width"], required_dict["depth"])

                if response:
                    response_dict = {"big_stick_id": response[0]["id"], "big_stick_width": response[0]["width"],
                                     "big_stick_depth": response[0]["depth"],
                                     "big_stick_serial_number": response[0]["serial_number"]}
                    return response_dict
                else:
                    return {}

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_canister_recommendation_by_dimension {}".format(e))
        raise e


    except Exception as e:
        logger.error("error in get_drug_canister_recommendation_by_dimension {}".format(e))
        raise e


@log_args_and_response
def get_recommendation_for_new_drug_sticks(drug_id, length, width, depth, fillet, shape_id, user_id=1):
    """
       get recommendation for new drug sticks
      :param map_data:
      :return:
      @param user_id:
      @param shape_id:
      @param fillet:
      @param depth:
      @param width:
      @param length:
      @param drug_id:
    """
    # resp = find_brush_distance_for_drug_canister(length)
    logger.info("get_recommendation_for_new_drug_sticks input {}, {}, {},{}, {}, {}, {}".format(drug_id,
                                                                                                length,
                                                                                                width,
                                                                                                depth,
                                                                                                fillet,
                                                                                                shape_id,
                                                                                                user_id))
    try:
        drug_shape_name = get_custome_drug_shape_by_id(id=shape_id)
        required_dict = {"length": length, "width": width, "depth": depth, "fillet": fillet}
        updated_dict = get_drug_dimension_parameters(required_dict, drug_shape_name)

        length = updated_dict["length"]
        width = updated_dict["width"]
        depth = updated_dict["depth"]
        fillet = updated_dict["fillet"]

        if float(length) < settings.PILL_LENGTH_RANGE[0]:
            return error(10001)
        elif float(length) > settings.PILL_LENGTH_RANGE[1]:
            return error(10002)
        elif float(width) < settings.PILL_WIDTH_RANGE[0]:
            return error(10003)
        elif float(width) > settings.PILL_WIDTH_RANGE[1]:
            return error(10004)
        elif float(depth) < settings.PILL_DEPTH_RANGE[0]:
            return error(10005)
        elif float(depth) > settings.PILL_DEPTH_RANGE[1]:
            return error(10006)

        big_canister_configuration = get_drug_canister_recommendation_by_dimension(depth=depth, width=width,
                                                                                   shape_id=shape_id)

        if (float(length) % 1) * 10 > 5:
            required_length = math.floor(float(length))
        else:
            required_length = math.floor(float(length) - 1)

        small_stick_data = get_small_canister_stick_data_by_length(req_length=required_length)
        logger.info("In get_recommendation_for_new_drug_sticks: small_stick data by length{}".format(small_stick_data))

        if small_stick_data:
            small_stick_id = small_stick_data["id"]
        else:
            logger.info("get_recommendation_for_new_drug_sticks empty response")
            return create_response({})

        if not big_canister_configuration:
            compatible_unique_drug_id_list = get_drugs_for_required_configuration(drug_id, length, width, depth, fillet,
                                                                                  shape_id, use_database=False)

            if compatible_unique_drug_id_list:
                query = get_recom_new_drug_dimension_data(unique_drug_id=compatible_unique_drug_id_list, small_stick_id=small_stick_id)

                db_response = dict()
                try:
                    db_response = query.dicts().get()
                except DoesNotExist as e:
                    logger.info("No result found for dimensions: {}.".format(e))

                logger.info("get_recommendation_for_new_drug_sticks db response {}".format(db_response))
                return create_response(db_response)

            else:
                logger.info("get_recommendation_for_new_drug_sticks empty response")
                return create_response({})
        else:
            logger.info("get_recommendation_for_new_drug_sticks in else part of not big_canister_configuration")
            required_dict = {"big_canister_stick_id": big_canister_configuration["big_stick_id"],
                             "small_canister_stick_id": small_stick_id, "user_id": user_id}

            response = add_canister_stick(required_dict)

            big_canister_configuration["small_stick_length"] = required_length
            big_canister_configuration["small_stick_id"] = small_stick_id
            big_canister_configuration["canister_stick_id"] = response
            logger.info("get_recommendation_for_new_drug_sticks response {}".format(big_canister_configuration))
            return create_response(big_canister_configuration)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_recommendation_for_new_drug_sticks: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_recommendation_for_new_drug_sticks {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_recommendation_for_new_drug_sticks: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_recommendation_for_new_drug_sticks: " + str(e))


@log_args_and_response
def report_missing_canister_recommendation(unique_drug_id, length, width, depth, fillet, shape_id, company_id,
                                           is_manual, image_url, user_id):
    """
    1. Insert the data we got into db
    2. Get the data from db for mail api
    3. Send email using call webservices
    :return:
    """
    try:

        record, created = missing_stick_recomm_get_or_create(width=width,
                                                                   depth=depth,
                                                                   unique_drug_id=unique_drug_id,
                                                                   length=length,
                                                                   fillet=fillet,
                                                                   shape_id=shape_id,
                                                                   company_id=company_id,
                                                                   is_manual=is_manual,
                                                                   image_url=image_url,
                                                                   user_id=user_id)

    except InternalError as e:
        logger.error("Error in report_missing_canister_recommendation {}".format(e))
        raise e
    except IntegrityError as e:
        logger.error("Error in report_missing_canister_recommendation {}".format(e))
        raise DuplicateSerialNumber
    except DataError as e:
        logger.error("Error in report_missing_canister_recommendation {}".format(e))
        raise e
    response = get_missing_stick_recommendation_by_id(required_id=record.id)
    drug_shape_name = get_custome_drug_shape_by_id(id=shape_id)

    if response:
        response["is_manual"] = int(response["is_manual"])
        response["local_db_id"] = int(record.id)
        response["shape_name"] = drug_shape_name

        status, data = call_webservice(settings.BASE_URL_AUTH, settings.MISSING_CANISTER_STICK_RECOMMENDATION_API,
                                       parameters=response, use_ssl=settings.AUTH_SSL)

        logger.info("In report_missing_canister_recommendation: Response from the api call for email for stick recommendation: " + str(data))

    return True


@log_args_and_response
def get_drug_shape_fields_by_shape(shape_id):
    """
    This function will be used to get fields for the front end for given shape id
    :param shape_id: Shape id for which we need to find the data
    :return: List of dictionaries
    """
    try:
        db_result = get_drug_shape_fields_by_shape_id(shape_id=shape_id)
        return create_response(db_result)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_shape_fields_by_shape: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_drug_shape_fields_by_shape {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_shape_fields_by_shape: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_drug_shape_fields_by_shape: " + str(e))


@log_args_and_response
def get_recommendation_for_canister_by_ndc(company_id, system_id, ndc):
    data = {"drug": ndc}
    logger.info("In get_recommendation_for_canister_by_ndc {}, {}, {}".format(company_id, system_id, ndc))

    try:
        drug_dimension_data = json.loads(get_drug_dimension_by_drug(data))
        response = dict()
        logger.info("In get_recommendation_for_canister_by_ndc : drug dimension data: {}".format(drug_dimension_data))

        if 'data' in drug_dimension_data:
            for drug_dimension_info in drug_dimension_data['data']:
                if drug_dimension_info['verification_status_id'] == settings.DRUG_VERIFICATION_STATUS['pending']:
                    return error(9019)

                elif drug_dimension_info['verification_status_id'] == settings.DRUG_VERIFICATION_STATUS['rejected']:
                    return error(9020)

                response['drug_dimension_info'] = drug_dimension_info
                unique_drug_id = drug_dimension_info['unique_drug_id']
                length = drug_dimension_info['length']
                width = drug_dimension_info['width']
                depth = drug_dimension_info['depth']
                fillet = drug_dimension_info['fillet']
                shape = drug_dimension_info['shape_id']
                list_of_unique_ids = get_drugs_for_required_configuration(unique_drug_id, length=length, width=width,
                                                                          depth=depth, fillet=fillet, shape_id=shape,
                                                                          use_database=False)

                unique_drug_data = get_fndc_txr_by_unique_id_dao(unique_ids=list_of_unique_ids)
                logger.info("get_recommendation_for_canister_by_ndc unique_drug_data {}".format(unique_drug_data))
                fndc_txr_list = []
                for each_drug_data in unique_drug_data:
                    fndc_txr_list.append(each_drug_data['formatted_ndc'] + '##' + each_drug_data['txr'])

                logger.info("get_recommendation_for_canister_by_ndc fndc_txr_list {}".format(fndc_txr_list))
                canister_id_list = db_get_deactive_canisters(company_id=company_id, all_flag=False,
                                                                            fndc_txr=fndc_txr_list,
                                                                            exclude_ndc=ndc)
                response["canister_id_list"] = canister_id_list

            logger.info("response get_recommendation_for_canister_by_ndc {}".format(response))
            return create_response(response)


    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_recommendation_for_canister_by_ndc: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_recommendation_for_canister_by_ndc {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_recommendation_for_canister_by_ndc: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_recommendation_for_canister_by_ndc: " + str(e))


@log_args_and_response
def generate_canister_ndc(args):
    response: dict = dict()
    try:
        status, data_id = add_generate_canister_data(args=args)
        logger.info("In generate_canister_ndc: generate canister data added:{}, data_id: {}".format(status, data_id))
        response['row_updated'] = data_id
        logger.info("In generate_canister_ndc: response: {}".format(response))
        if status:
            return create_response(response)
        else:
            return error(1001, data_id)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in generate_canister_ndc: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in generate_canister_ndc {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in generate_canister_ndc: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in generate_canister_ndc: " + str(e))


@log_args_and_response
@validate(required_fields=["company_id"])
def get_drug_master_count_stats(dict_drug_master_info: dict) -> dict:
    """
    return drug master stats counts for drug master screen
    @param dict_drug_master_info:
    @return:
    """
    company_id = dict_drug_master_info.get('company_id')
    try:
        # get count of drug in various stats
        registration_pending_drug_dimension, verification_pending_drug_dimension, verified_drug_dimension, rejected_drug_dimension, \
            total_drug_dimension = get_drug_master_count_data(company_id=company_id)
        logger.info(
            "In get_drug_master_count_stats : registration_pending_drug_dimension: {},verification_pending_drug_dimension: {},"
            "verified_drug_dimension: {},rejected_drug_dimension: {},total_drug_dimension:{}"
                .format(registration_pending_drug_dimension, verification_pending_drug_dimension, verified_drug_dimension,
                        rejected_drug_dimension, total_drug_dimension))
        response_data = {"verification_pending_drug_dimension": verification_pending_drug_dimension,
                         "registration_pending_drug_dimension": registration_pending_drug_dimension,
                         "verified_drug_dimension": verified_drug_dimension,
                         "rejected_drug_dimension": rejected_drug_dimension,
                         "total_drug_dimension": total_drug_dimension}

        return create_response(response_data)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_master_count_stats: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)
    except Exception as e:
        logger.error("Error in get_drug_master_count_stats {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_master_count_stats: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_drug_master_count_stats: " + str(e))


@log_args_and_response
def get_drug_canister_recommendation_by_ndc_dimension(dict_drug_info):
    """
    1. Displays canister stick ids based on ndc
    @param:
    @return:
    """
    canister_stick_id_list = list()
    big_stick_serial_number_list = list()
    small_stick_serial_number_list = list()
    available_mold_list = list()
    drum_width1_3D = list()
    drum_width2_3D = list()
    drum_depth1_3D = list()
    drum_depth2_3D = list()
    small_stick_3D = list()
    drum_length_3D = list()
    depth_brush_3D = list()

    ndc = dict_drug_info.get("ndc", None)
    depth = dict_drug_info.get("depth", None)
    width = dict_drug_info.get("width", None)
    length = dict_drug_info.get("length", None)
    fillet = dict_drug_info.get("fillet", None)
    strength = dict_drug_info.get("strength", None)
    strength_value = dict_drug_info.get("strength_value", None)
    shape = dict_drug_info.get("shape", None)
    drug_name = dict_drug_info.get("drug_name", None)
    # canister_stick_id_list = list()
    # big_stick_serial_number_list = list()
    # small_stick_serial_number_list = list()
    response = {}
    try:
        """
        Input data from database and files
        """
        drug_ndc_dimensions_dict, big_stick_id_size_mapping_dict, drug_list, big_stick_id_dimension_tuple_mapping, \
            big_stick_dimension_tuple_id_mapping, all_big_stick_mold_dimension_tuple_mapping, \
        all_big_stick_dimension_tuple_mold_id_mapping = get_drug_data(ndc=ndc, depth=depth, width=width, length=length,
                                                             fillet=fillet, strength=strength,
                                                             strength_value=strength_value, shape=shape,
                                                             drug_name=drug_name)

        """
        Define all necessary variables useful for stick recommendation within stick recommendation class
        """
        sr = StickRecommender(big_stick_id_size_mapping_dict=big_stick_id_size_mapping_dict,
                              big_stick_id_dimension_tuple_mapping=big_stick_id_dimension_tuple_mapping,
                              big_stick_dimension_tuple_id_mapping=big_stick_dimension_tuple_id_mapping,
                              all_big_stick_mold_dimension_tuple_mapping=all_big_stick_mold_dimension_tuple_mapping,
                              all_big_stick_dimension_tuple_mold_id_mapping=
                              all_big_stick_dimension_tuple_mold_id_mapping
                              )
        """
        Algorithm for stick recommendation
        """
        required_data_dict = sr.recommend_stick_dimensions(drugndc_dimensions_dict=drug_ndc_dimensions_dict)
        for required_data in required_data_dict:
            big_stick_id_list = required_data["available_big_stick_inventory"]
            small_stick_length = required_data["Small Stick"]
            canister_stick_id_list, big_stick_serial_number_list, small_stick_serial_number_list = \
                db_get_canister_stick_id_by_big_stick_small_stick_dimension(big_stick_id_list, small_stick_length)
            available_mold_list.append(required_data["available_mold_id_list"])
            drum_width1_3D.append(required_data["drum_width1_3D"])
            drum_width2_3D.append(required_data["drum_width2_3D"])
            drum_depth1_3D.append(required_data["drum_depth1_3D"])
            drum_depth2_3D.append(required_data["drum_depth2_3D"])
            small_stick_3D.append(required_data["small_stick_3D"])
            drum_length_3D.append(required_data["drum_length_3D"])
            depth_brush_3D.append(required_data["depth_brush_3D"])

        response["canister_stick_id_list"] = canister_stick_id_list
        response["big_stick_serial_number_list"] = big_stick_serial_number_list
        response["small_stick_serial_number_list"] = small_stick_serial_number_list
        response["available_mold_list"] = required_data_dict[0]["available_mold_id_list"]
        response["3D drum width1"] = drum_width1_3D
        response["3D drum width2"] = drum_width2_3D
        response["3D drum depth1"] = drum_depth1_3D
        response["3D drum depth2"] = drum_depth2_3D
        response["3D small stick length"] = small_stick_3D
        response["3D drum length"] = drum_length_3D
        response["3D brush depth"] = depth_brush_3D
        # below changes done only for testing in Basement DB
        # response["canister_stick_id_list"] = [5]
        # response["big_stick_serial_number_list"] = ["125"]
        # response["small_stick_serial_number_list"] = [8.0]
        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_canister_recommendation_by_ndc_dimension: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_drug_canister_recommendation_by_ndc_dimension {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_canister_recommendation_by_ndc_dimension: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1001, "Error in get_drug_canister_recommendation_by_ndc_dimension: " + str(e))


@log_args_and_response
def get_drug_data(depth, width, length, fillet, strength, strength_value, shape, drug_name, ndc):
    """
    function for getting drug dimension data from database
    """

    big_stick_id_size_mapping_dict: dict = dict()
    big_stick_id_dimension_tuple_mapping: dict = dict()
    big_stick_dimension_tuple_id_mapping: dict = dict()
    drug_list: list = list()
    drug_dimension_dict = OrderedDict()
    priority = 1
    drug_ndc = ''
    all_big_stick_mold_size_mapping_dict = {}
    all_big_stick_mold_dimension_tuple_mapping = {}
    all_big_stick_dimension_tuple_mold_id_mapping = {}
    """
    Required dictionaries as input to our stick_recommendation function
    """
    try:
        """
        Data fetching related to drug and canister from database
        """
        if ndc is not None:
            ndc = ndc.zfill(11)
            drug_dimension_priority_info_list = get_drug_details_by_ndc(ndc)
            if drug_dimension_priority_info_list:
                for drug_dict in drug_dimension_priority_info_list:
                    drug_ndc = str(drug_dict["ndc"])
                    depth = str(drug_dict["depth"])
                    width = str(drug_dict["width"])
                    length = str(drug_dict["length"])
                    fillet = str(drug_dict["fillet"])
                    strength_value = str(drug_dict["strength_value"])
                    strength = str(drug_dict["strength"])
                    shape = str(drug_dict["custom_shape"])
                    priority = '1'
                    drug_name = str(drug_dict["drug_name"])
            else:
                if shape is not None:
                    shape = get_custome_drug_shape_by_id(id=shape)

                    drug_dimension_data = dict()
                    if float(depth) != 0:
                        drug_dimension_data["depth"] = float(depth)
                    if float(width) != 0:
                        drug_dimension_data["width"] = float(width)
                    if float(length) != 0:
                        drug_dimension_data["length"] = float(length)
                    if float(fillet) != 0:
                        drug_dimension_data["fillet"] = float(fillet)

                    drug_dimension_data = get_drug_dimension_parameters(drug_dimension_data, shape)

                    depth = drug_dimension_data["depth"]
                    width = drug_dimension_data["width"]
                    length = drug_dimension_data["length"]
                    fillet = drug_dimension_data["fillet"]

                    drug_ndc = str(ndc)
                else:
                    raise Exception('shape of the drug is missing')
        """
        Data fetching related to canister which are available in production
        """
        big_stick_in_inventory_list = get_big_canister_stick_dimension_id_dao()
        for big_stick_dict in big_stick_in_inventory_list:
            stick_id = str(big_stick_dict["id"])
            data_dict = {"width": float(big_stick_dict["width"]), "depth": float(big_stick_dict["depth"])}
            big_stick_id_size_mapping_dict[stick_id] = data_dict
            big_stick_id_dimension_tuple_mapping[stick_id] = (
                float(big_stick_dict["width"]), float(big_stick_dict["depth"]))
            big_stick_dimension_tuple_id_mapping[
                float(big_stick_dict["width"]), float(big_stick_dict["depth"])] = stick_id

        """
        Data fetching related dummy pill and canister from csv
        """
        df_mold_total = read_data(is_excel_or_csv=False, file_name='BS_mold_made.csv')
        df_mold_total_dict = converting_data_frame_to_dict_form(df=df_mold_total)

        for row_index, row_element in df_mold_total_dict.items():
            mold_id = str(row_element[0]["BS"])
            stick_dimension = str(row_element[0]["Dimension"])
            stick_dimension = stick_dimension.split('X')
            data_dict = {"width": stick_dimension[0], "depth": stick_dimension[1]}
            all_big_stick_mold_size_mapping_dict[mold_id] = data_dict
            all_big_stick_mold_dimension_tuple_mapping[mold_id] = (stick_dimension[0], stick_dimension[1])
            all_big_stick_dimension_tuple_mold_id_mapping[(stick_dimension[0], stick_dimension[1])] = mold_id

        data_dict = {"fndc": drug_ndc, "drug_name": drug_name, "depth": depth, "width": width, "length": length,
                     "fillet": fillet, "shape": shape, "strength": strength, "strength_value": strength_value,
                     "priority": priority}
        drug_dimension_dict[drug_ndc] = data_dict
        drug_list.append(drug_ndc)

        return drug_dimension_dict, big_stick_id_size_mapping_dict, drug_list, big_stick_id_dimension_tuple_mapping, \
               big_stick_dimension_tuple_id_mapping, all_big_stick_mold_dimension_tuple_mapping, \
               all_big_stick_dimension_tuple_mold_id_mapping

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_data:  {}".format(e))
        raise e

    except Exception as e:
        logger.error("Error in get_drug_data {}".format(e))
        raise e

@log_args_and_response
def get_drug_data_csv(ndc_list=None):
    """
    Input data from database and files
    """
    try:
        if ndc_list:
            drug_data = {'priority': [i+1 for i in range(len(ndc_list))],
                         'ndc': ndc_list,
                         'drug_count': [0 for i in range(len(ndc_list))],
                         'pack_count': [0 for i in range(len(ndc_list))]}

            df_drug_info = pd.DataFrame(drug_data)
        else:
            filename = r'NDC_data.xlsx'
            logger.info("1")
            df_drug_info = pd.read_excel(filename, engine='openpyxl')
            df_drug_info = df_drug_info.dropna()
        df_drug_info['ndc'] = df_drug_info['ndc'].astype(int)
        ndc_list = df_drug_info['ndc'].astype(str).tolist()
        ndc_list = [ndc.zfill(11) for ndc in ndc_list]

        if pd.Series(
                ['ndc', 'fndc_txr', 'drug_name', 'strength', 'strength_value', 'width', 'length', 'depth', 'fillet',
                 'custom_shape','drug_count','pack_count']).isin(df_drug_info.columns).all():
            df_drug_dimension_priority_info_dict = df_drug_info.to_dict('records')
            df_drug_dimension_priority_info = pd.DataFrame(df_drug_dimension_priority_info_dict)
            df_drug_dimension_priority_info['ndc'] = df_drug_dimension_priority_info['ndc'].astype(str).astype(int)
            df_drug = df_drug_dimension_priority_info

        elif 'ndc' in df_drug_info:
            """
            Data fetching related to drug from database
            """
            df_drug_dimension_priority_info_dict = get_drug_details_by_drug(ndc_list)
            if df_drug_dimension_priority_info_dict:
                df_drug_dimension_priority_info = pd.DataFrame(df_drug_dimension_priority_info_dict)
                df_drug_dimension_priority_info['ndc'] = df_drug_dimension_priority_info['ndc'].astype(str).astype(int)
                if 'drug_count' in df_drug_dimension_priority_info.columns:
                    df_drug_dimension_priority_info['drug_count'] = df_drug_dimension_priority_info['drug_count'].astype(str).astype(int)
                if 'pack_count' in df_drug_dimension_priority_info.columns:
                    df_drug_dimension_priority_info['pack_count'] = df_drug_dimension_priority_info['pack_count'].astype(str).astype(int)
                df_drug = pd.merge(df_drug_info, df_drug_dimension_priority_info, on='ndc')
            else:
                raise error(1004, 'No drug dimension exists for any of the NDC')

        """
        Data fetching related to canister from database
        """
        drug_existing_canister_info_dict = get_canister_details_by_drug(ndc_list)
        if drug_existing_canister_info_dict:
            drug_existing_canister_info_dict = pd.DataFrame(drug_existing_canister_info_dict)
            drug_existing_canister_info_dict['ndc'] = drug_existing_canister_info_dict['ndc'].astype(str).astype(int)
            df_drug = pd.merge(df_drug, drug_existing_canister_info_dict, on='ndc', how='left')

        """
        Data fetching related dummy pill and canister from csv
        """
        df_drug_dimension_priority_info_dict = converting_data_frame_to_dict_form(df=df_drug)
        df_big_stick_in_inventory = read_data(is_excel_or_csv=False, file_name='production_received.csv')
        df_big_stick_in_inventory_dict = converting_data_frame_to_dict_form(df=df_big_stick_in_inventory)
        df_mold_total = read_data(is_excel_or_csv=False, file_name='BS_mold_made.csv')
        df_mold_total_dict = converting_data_frame_to_dict_form(df=df_mold_total)
        df_dummy_pill_stock = read_data(is_excel_or_csv=False, file_name='dummy_pill.csv')
        df_dummy_pill_stock_dict = converting_data_frame_to_dict_form(df=df_dummy_pill_stock)

        """
        Required dictionaries as input to our stick_recommendation function
        """
        big_stick_id_size_mapping_dict = {}
        big_stick_id_dimension_tuple_mapping = {}
        big_stick_dimension_tuple_id_mapping = {}
        all_big_stick_mold_size_mapping_dict = {}
        all_big_stick_mold_dimension_tuple_mapping = {}
        all_big_stick_dimension_tuple_mold_id_mapping = {}
        stock_pill_dict = []
        drug_list = []
        drug_dimension_dict = OrderedDict()

        for row_index, row_element in df_big_stick_in_inventory_dict.items():
            stick_id = str(row_element[0]["BS"])
            stick_dimension = str(row_element[0]["Dimension"])
            stick_dimension = stick_dimension.split('X')
            data_dict = {"width": stick_dimension[0], "depth": stick_dimension[1]}
            big_stick_id_size_mapping_dict[stick_id] = data_dict
            big_stick_id_dimension_tuple_mapping[stick_id] = (stick_dimension[0], stick_dimension[1])
            big_stick_dimension_tuple_id_mapping[(stick_dimension[0], stick_dimension[1])] = stick_id

        for row_index, row_element in df_mold_total_dict.items():
            mold_id = str(row_element[0]["BS"])
            stick_dimension = str(row_element[0]["Dimension"])
            stick_dimension = stick_dimension.split('X')
            data_dict = {"width": stick_dimension[0], "depth": stick_dimension[1]}
            all_big_stick_mold_size_mapping_dict[mold_id] = data_dict
            all_big_stick_mold_dimension_tuple_mapping[mold_id] = (stick_dimension[0], stick_dimension[1])
            all_big_stick_dimension_tuple_mold_id_mapping[(stick_dimension[0], stick_dimension[1])] = mold_id

        for row_index, row_element in df_drug_dimension_priority_info_dict.items():
            drug_ndc = str(row_element[0]["ndc"])
            fndc_txr = str(row_element[0]["fndc_txr"])
            depth = str(row_element[0]["depth"])
            width = str(row_element[0]["width"])
            length = str(row_element[0]["length"])
            fillet = str(row_element[0]["fillet"])
            strength_value = str(row_element[0]["strength_value"])
            strength = str(row_element[0]["strength"])
            shape = str(row_element[0]["custom_shape"])
            priority = str(row_element[0]["priority"])
            drug_name = str(row_element[0]["drug_name"])
            canister_id = str(row_element[0]["canister_id"])
            big_stick_serial_number = str(row_element[0]['big_canister_stick_serial_number'])
            big_stick_width = str(row_element[0]['big_canister_stick_width'])
            big_stick_depth = str(row_element[0]['big_canister_stick_depth'])
            small_stick_serial_number_length = str(row_element[0]['small_canister_stick_serial_number_length'])
            canister_drum_serial_number = str(row_element[0]['canister_drum_serial_number'])
            canister_activation_status = str(row_element[0]['canister_activation_status'])
            drug_count = str(row_element[0]['drug_count'])
            pack_count = str(row_element[0]['pack_count'])

            data_dict = {"fndc": drug_ndc, "drug_name": drug_name, "depth": depth, "width": width, "length": length,
                         "fndc_txr": fndc_txr,
                         "fillet": fillet, "shape": shape, "strength": strength, "strength_value": strength_value,
                         "priority": priority, "canister_id": canister_id,
                         "big_stick_serial_number": big_stick_serial_number,
                         "big_stick_width": big_stick_width,
                         "big_stick_depth": big_stick_depth,
                         "small_stick_serial_number_length": small_stick_serial_number_length,
                         "canister_drum_serial_number": canister_drum_serial_number,
                         "canister_activation_status": canister_activation_status,
                         "drug_count": drug_count,
                         "pack_count": pack_count}
            drug_dimension_dict[drug_ndc] = data_dict
            drug_list.append(drug_ndc)

        for row_index, row_element in df_dummy_pill_stock_dict.items():
            pill_no = str(row_element[0]["Pill_no"])
            depth = str(row_element[0]["Depth"])
            width = str(row_element[0]["Width"])
            length = str(row_element[0]["Length"])
            fillet = str(row_element[0]["Fillet"])
            shape = str(row_element[0]["shape"])
            data_dict = (pill_no, depth, width, length, fillet, shape)
            stock_pill_dict.append(data_dict)

        return drug_dimension_dict, drug_existing_canister_info_dict, big_stick_id_size_mapping_dict, drug_list, \
               big_stick_id_dimension_tuple_mapping, big_stick_dimension_tuple_id_mapping, \
               all_big_stick_mold_dimension_tuple_mapping, all_big_stick_dimension_tuple_mold_id_mapping, stock_pill_dict

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.info(e)
        raise e

@log_args_and_response
def get_canister_stick_id_by_serial_number(bs_serial_number: str, ss_serial_number: str,
                                           drum_serial_number: str, canister_detail: dict) -> int or None:
    """
    #  1. get the id based on the serial number
    """
    try:
        logger.info("In get_canister_stick_id_by_serial_number")
        big_canister_stick_id: int = 0
        small_canister_stick_id: int = 0
        canister_drum_id: int = 0
        canister_stick_id: int = 0
        canister_stick_data: Dict[str, int] = dict()
        big_canister_stick_data = dict()
        small_canister_stick_data = dict()
        canister_drum_data = dict()

        if bs_serial_number:
            # Get the big canister stick id based on big canister stick serial number
            big_canister_stick_id = get_big_canister_stick_by_bs_serial_number_dao(bs_serial_number=bs_serial_number)
            logger.info("In get_canister_stick_id_by_serial_number: big canister stick id : {}".format(
                big_canister_stick_id))
            if not big_canister_stick_id:
                big_canister_stick_data['serial_number'] = bs_serial_number
                big_canister_stick_data['width'] = canister_detail['big_stick_width']
                big_canister_stick_data['depth'] = canister_detail['big_stick_depth']
                big_canister_stick_data['user_id'] = 2
                big_canister_stick_id = add_big_canister_stick(big_canister_stick_data)
                logger.info("bs_Serial_number {}, bs_width {}, bs_depth, bs_id is {}.".format(
                    big_canister_stick_data['serial_number'], big_canister_stick_data['width'],
                    big_canister_stick_data['depth'], big_canister_stick_id))

        if ss_serial_number:
            # Get the small canister stick id based on small canister stick serial number
            small_canister_stick_id = get_small_canister_stick_by_ss_serial_number_dao(ss_serial_number=ss_serial_number)
            logger.info("In get_canister_stick_id_by_serial_number: small canister stick id : {}".format(small_canister_stick_id))
            if not small_canister_stick_id:
                small_canister_stick_data['serial_number'] = ss_serial_number
                small_canister_stick_data['length'] = canister_detail['small_stick_length']
                small_canister_stick_data['user_id'] = 2
                small_canister_stick_id = add_small_canister_stick(small_canister_stick_data)
                logger.info("ss_Serial_number {}, ss_width {}, ss_depth, ss_id is {}.".format(
                    small_canister_stick_data['serial_number'], small_canister_stick_data['width'],
                    small_canister_stick_data['depth'], small_canister_stick_id))

        if drum_serial_number:
            # Get the canister drum id based on drum serial number
            canister_drum_id = get_canister_drum_id_by_drum_serial_number_dao(drum_serial_number=drum_serial_number)
            logger.info("In get_canister_stick_id_by_serial_number: canister drug id : {}".format(
                canister_drum_id))
            if not canister_drum_id:
                canister_drum_data['serial_number'] = drum_serial_number
                canister_drum_data['width'] = canister_detail['drum_width']
                canister_drum_data['depth'] = canister_detail['drum_depth']
                canister_drum_data['length'] = canister_detail['drum_length']
                canister_drum_data['user_id'] = 2
                canister_drum_id = add_canister_drum(canister_drum_data)
                logger.info("drum_Serial_number {}, drum_width {}, drum_depth, drum_id is {}.".format(
                    canister_drum_data['serial_number'], canister_drum_data['width'],
                    canister_drum_data['depth'], canister_drum_id))

        # Get the canister stick id based on bs_id, ss_id and drum_id
        canister_stick_id = get_canister_stick_by_big_stick_small_stick_canister_drum_dao(big_canister_stick_id=big_canister_stick_id,
                                                                                          small_canister_stick_id=small_canister_stick_id,
                                                                                          canister_drum_id=canister_drum_id)

        logger.info("In get_canister_stick_id_by_serial_number: canister stick id : {}".format(canister_stick_id))
        if not canister_stick_id:
            # 3. if no entry exist for the given set of bs & ss id, create record in canister_stick and get the id
            canister_stick_data['big_canister_stick_id'] = big_canister_stick_id if big_canister_stick_id != 0 else None
            canister_stick_data[
                'small_canister_stick_id'] = small_canister_stick_id if small_canister_stick_id else None
            canister_stick_data['canister_drum_id'] = canister_drum_id if canister_drum_id != 0 else None
            canister_stick_data['user_id'] = 2
            canister_stick_id = add_canister_stick(canister_stick_data)

        return canister_stick_id
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("Error in get_canister_stick_id_by_serial_number {}".format(e))
        return None
    except Exception as e:
        logger.error("Error in get_canister_stick_id_by_serial_number {}".format(e))
        return None


@log_args_and_response
def get_canister_parameter_rules(request_info):
    """
    Returns list of rules defined for canister parameters
    :param request_info: dict
    :return: str
    """
    filter_fields = request_info.get('filter_fields', None)
    sort_fields = request_info.get('sort_fields', None)
    paginate = request_info.get('paginate', None)
    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, 'Missing key(s) in paginate.')

    try:
        count, results = get_canister_parameter_rule_dao(filter_fields=filter_fields,
                                                         paginate=paginate,
                                                         sort_fields=sort_fields)
        response = {"rule_list": results, "number_of_records": count}
        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_canister_parameter_rules {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("Error in get_canister_parameter_rules {}".format(e))
        return error(1000, "Error in get_canister_parameter_rules: " + str(e))


@validate(required_fields=['rule_key', 'rule_id'])
@log_args_and_response
def get_canister_parameter_rule_drugs(request_info):
    """
    Returns drug covered in given rule
    - Optionally paginates, sorts and filters data
    :param request_info: dict
    :return: str
    """
    try:
        filter_fields = request_info.get('filter_fields', None)
        sort_fields = request_info.get('sort_fields', None)
        paginate = request_info.get('paginate', None)
        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')


        rule_key = request_info.pop('rule_key')
        rule_id = request_info.pop('rule_id')

        if rule_key not in canister_parameter_rules:
            return error(1020, "The parameter rule_key can only be one of the following."
                               " {}.".format(list(canister_parameter_rules)))

        count, results = get_canister_parameter_rule_drugs_dao(filter_fields=filter_fields,
                                                               paginate=paginate,
                                                               rule_id=rule_id,
                                                               rule_key=rule_key,
                                                               sort_fields=sort_fields)
        response = {"drug_list": results, "number_of_records": count}
        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_canister_parameter_rule_drugs {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("Error in get_canister_parameter_rule_drugs {}".format(e))
        return error(1000, "Error in get_canister_parameter_rule_drugs: " + str(e))


def get_drug_without_dimension(company_id, filter_fields, sort_fields, paginate,
                               only_pending_facility=False):
    """
    Returns drug list without dimension
    :param company_id:
    :param filter_fields:
    :param sort_fields:
    :param paginate:
    :param only_pending_facility:
    :return:
    """
    try:
        count, results = get_drugs_wo_dimension_dao(company_id=company_id,
                                                    filter_fields=filter_fields,
                                                    only_pending_facility=only_pending_facility,
                                                    paginate=paginate,
                                                    sort_fields=sort_fields)
        response = {'results': results,
                    'number_of_records': count}
        return create_response(response)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def skip_drug_dimension_flow(args):
    """
    to update status in FrequentMfdDrugs table >> status: skipped
    """
    # batch_id = args["batch_id"]
    ndc = args["ndc"]

    try:
        logger.info(f"Inside skip_drug_dimension_flow")
        drug_id_list = get_drug_id_from_ndc(ndc)
        drug_id = drug_id_list[0]

        unique_drug_id = get_unique_drug_id_from_ndc(ndc=ndc)

        status = update_status_in_frequent_mfd_drugs(drug_id=unique_drug_id)
        logger.info(f"In skip_drug_dimension_flow, status update in FrequentMfdDrugs : {status}")

        if status:
            response = {"status_updated": True}
            return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in skip_drug_dimension_flow: {e}")


@log_args_and_response
@validate(required_fields=["company_id", "drug_id"])
def get_drug_dimension_history(args):
    try:
        drug_id = args.get('drug_id', None)
        logger.info("Inside get_drug_dimension_history")
        drug_dimension_history_data = dict()
        drug_dimension_history_data = get_drug_dimension_history_dao(drug_id=drug_id)
        return create_response(drug_dimension_history_data)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"Error in get_drug_dimension_history: {e}")


@log_args_and_response
def get_correct_dimensions(drug_dimension_data):
    try:
        shape_id = drug_dimension_data["shape"]
        length = drug_dimension_data.pop('length', None)
        fillet = drug_dimension_data.pop('fillet', None)
        width = drug_dimension_data.pop('width', None)
        depth = drug_dimension_data.pop('depth', None)

        all_dimension = [length, fillet, width, depth]
        dimension = [value for value in all_dimension if value is not None]
        sorted_dimensions = sorted(set(dimension), reverse=True)

        if fillet:
            drug_dimension_data['fillet'] = fillet

        if shape_id == settings.DRUG_SHAPE_CAPSULE:
            width = width if width is not None else depth

            drug_dimension_data["length"], \
                drug_dimension_data["width"], \
                drug_dimension_data["depth"] = sorted([length, width, width], reverse=True)

        elif shape_id == settings.DRUG_SHAPE_ELLIPTICAL or shape_id == settings.DRUG_SHAPE_OVAL:
            drug_dimension_data["length"] = sorted_dimensions[0]
            drug_dimension_data["width"] = sorted_dimensions[1]
            drug_dimension_data["depth"] = sorted_dimensions[2]

        elif shape_id == settings.DRUG_SHAPE_ROUND_CURVED:
            drug_dimension_data["length"] = drug_dimension_data["width"] = sorted_dimensions[0]
            drug_dimension_data["depth"] = sorted_dimensions[1]
            drug_dimension_data["fillet"] = sorted_dimensions[2]

        elif shape_id == settings.DRUG_SHAPE_ROUND_FLAT:
            if not all([width, depth]):
                width = width if width is not None else length
                depth = depth if depth is not None else fillet

            if width > depth:
                drug_dimension_data["length"] = drug_dimension_data["width"] = width
                drug_dimension_data["depth"] = drug_dimension_data["fillet"] = depth

            else:
                drug_dimension_data["length"] = drug_dimension_data["width"] = depth
                drug_dimension_data["depth"] = drug_dimension_data["fillet"] = width

        return drug_dimension_data

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error(f"Error in get_correct_dimensions: {e}")


@log_args_and_response
def get_canister_stick_details(ndc_list=None, file_needed=False):
    """
    1. Displays current drug dimension and canister stick mapping
    2. Recommend new big stick ids, small stick ids, drum ids as per new algorithm
    3. Recommend deactivated canisters based on recommended big stick ids, small stick ids and drum ids
    @param:
    @return:
    """
    try:
        """
        Input data from database and files
        """
        drugndc_dimensions_dict, drug_existing_canister_info_dict, big_stick_id_size_mapping_dict, drug_list, \
        big_stick_id_dimension_tuple_mapping, big_stick_dimension_tuple_id_mapping, \
        all_big_stick_mold_dimension_tuple_mapping, all_big_stick_dimension_tuple_mold_id_mapping, stock_pill_dict = \
            get_drug_data_csv(ndc_list)
        # else:
        #     print("No drug dimension exists for any of the ndc")
        #     return
        """
        Define all neccessary variables useful for stick recommendation within stick recommendation class
        """
        sr = StickRecommender1(big_stick_id_size_mapping_dict=big_stick_id_size_mapping_dict,
                              big_stick_id_dimension_tuple_mapping=big_stick_id_dimension_tuple_mapping,
                              big_stick_dimension_tuple_id_mapping=big_stick_dimension_tuple_id_mapping,
                              all_big_stick_mold_dimension_tuple_mapping=all_big_stick_mold_dimension_tuple_mapping,
                              all_big_stick_dimension_tuple_mold_id_mapping=
                              all_big_stick_dimension_tuple_mold_id_mapping,
                              stock_pill_dict=stock_pill_dict)
        """
        Algorithm for stick recommendation
        """
        required_data_dict = sr.recommend_stick_dimensions(drugndc_dimensions_dict=drugndc_dimensions_dict)

        """
        Get Deactivated canisters and corresponding data and format and insert the data into dictionary 
        according to number of big stick recommendations we receive
        """
        df_dict = get_deactivated_canister_and_format_data(required_data_dict=required_data_dict,
                                                           drug_ndc_dimensions_dict=drugndc_dimensions_dict)
        df = pd.DataFrame(df_dict)
        molded_df = pd.DataFrame()
        printed_3d_df = pd.DataFrame()
        df.drop_duplicates(subset=['Drug_NDC', 'Recommended_Canister_Id'], keep="first", inplace=True)
        if file_needed:
            for index, row in df.iterrows():

                if row['mft'] == 2 or (row['mft'] == 0 and not row['available_mold_id_list']):
                    selected_columns = ['priority', 'Drug_Name', 'Strength_Value', 'Strength', 'formatted_ndc_txr',
                                        'Custom_Shape', 'Width', 'Depth', 'Length', 'Fillet', 'drum_width1_3D',
                                        'drum_width2_3D', 'drum_depth1_3D', 'drum_depth2_3D', 'drum_length_3D', 'Big_Stick',
                                        'recommended_small_stick']
                    row_to_append = pd.Series({col: row[col] for col in selected_columns})
                    printed_3d_df = printed_3d_df.append(row_to_append, ignore_index=True)
                elif row['mft'] == 0:
                    selected_columns = ['priority', 'Drug_Name', 'Strength_Value', 'Strength', 'formatted_ndc_txr',
                                        'Custom_Shape', 'Width', 'Depth', 'Length', 'Fillet', 'recommended_big_stick',
                                        'recommended_small_stick',
                                        ]
                    row_to_append = pd.Series({col: row[col] for col in selected_columns})
                    molded_df = molded_df.append(row_to_append, ignore_index=True)

            selected_columns_for_molding = ['priority', 'Drug_Name', 'Strength_Value', 'Strength', 'formatted_ndc_txr',
                                            'Custom_Shape', 'Width', 'Depth', 'Length', 'Fillet', 'recommended_big_stick',
                                            'recommended_small_stick']

            if len(molded_df):
                molded_df = molded_df[selected_columns_for_molding]
            selected_columns_for_printed_3d = ['priority', 'Drug_Name', 'Strength_Value', 'Strength', 'formatted_ndc_txr',
                                               'Custom_Shape', 'Width', 'Depth', 'Length', 'Fillet', 'drum_width1_3D',
                                               'drum_width2_3D', 'drum_depth1_3D', 'drum_depth2_3D', 'drum_length_3D',
                                               'Big_Stick', 'recommended_small_stick']
            if len(printed_3d_df):
                printed_3d_df = printed_3d_df[selected_columns_for_printed_3d]

            molding_file = "Molding.xlsx"
            printed_3d_file = "Printed_3d.xlsx"
            molded_df.to_excel(molding_file, index=False)
            printed_3d_df.to_excel(printed_3d_file, index=False)

            file_name = 'Canister_Recommendation.xlsx'
            logger.info("3")
            df.to_excel(file_name)
        return df
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return error(1004, "error in get_drug_data()")
    except Exception as e:
        logger.info(e)
        return error(1004, "error in get_drug_data()")


@log_args_and_response
def get_deactivated_canister_and_format_data(required_data_dict: dict, drug_ndc_dimensions_dict: dict) -> dict:
    """
    Get Deactivated canisters and corresponding data and format and insert the data into dictionary
    according to number of big stick recommendations we receive
    @param: required_data_dict, drugndc_dimensions_dict
    @return df_dict: dictionary containing final data for canister recommendation
    """
    try:
        index = 0
        drug_dict = dict()
        df_dict = dict()
        for record in required_data_dict:
            ndc_txr = record['NDC##TXR']
            if record['Big Stick']:
                for big_stick_record in record['Big Stick']:
                    big_stick_dimensions = big_stick_record.split("x")
                    canister_stick_details_list = db_get_deactive_canisters_new(
                        width=big_stick_dimensions[0],
                        depth=big_stick_dimensions[1],
                        length=record['Small Stick'],
                        all_flag=False)
                    if canister_stick_details_list:
                        big_stick_width = [float(dict['Recommended_Big_Stick_Width']) for dict in
                                           canister_stick_details_list]
                        big_stick_width = set(big_stick_width)
                        big_stick_depth = [float(dict['Recommended_Big_Stick_Depth']) for dict in
                                           canister_stick_details_list]
                        big_stick_depth = set(big_stick_depth)
                        big_stick = str(big_stick_width) + 'x' + str(big_stick_depth)
                        Recommended_Big_Stick_Serial_Number = [dict['Recommended_Big_Stick_Serial_Number'] for dict in
                                                               canister_stick_details_list]
                        Recommended_Big_Stick_Serial_Number = set(Recommended_Big_Stick_Serial_Number)
                        canister_id = [dict_element["canister_id"] for dict_element in canister_stick_details_list]
                        drug_dict = insert_drug_canister_details(drug_record=record, big_stick=big_stick,
                                                                 Recommended_Big_Stick_Serial_Number=
                                                                 Recommended_Big_Stick_Serial_Number,
                                                                 canister_id=canister_id,
                                                                 drug_ndc_dimensions_dict=drug_ndc_dimensions_dict[
                                                                     ndc_txr],
                                                                 drug_dict=drug_dict)
                    else:
                        big_stick = {}
                        Recommended_Big_Stick_Serial_Number = {}
                        canister_id = []
                        for b_record in BigCanisterStick.select(
                                BigCanisterStick.width.alias('Recommended_Big_Stick_Width'),
                                BigCanisterStick.depth.alias('Recommended_Big_Stick_Depth'),
                                BigCanisterStick.serial_number.alias('Recommended_Big_Stick_Serial_Number')
                        ).dicts() \
                                .where(BigCanisterStick.width == float(big_stick_dimensions[0]),
                                       BigCanisterStick.depth == float(big_stick_dimensions[1])):
                            big_stick = str(b_record['Recommended_Big_Stick_Width']) + 'x' + str(
                                b_record['Recommended_Big_Stick_Depth'])
                            Recommended_Big_Stick_Serial_Number = str(b_record['Recommended_Big_Stick_Serial_Number'])
                        if not big_stick:
                            big_stick = ''
                            Recommended_Big_Stick_Serial_Number = {}
                            canister_id = []
                        drug_dict = insert_drug_canister_details(drug_record=record, big_stick=big_stick,
                                                                     Recommended_Big_Stick_Serial_Number=
                                                                     Recommended_Big_Stick_Serial_Number,
                                                                     canister_id=canister_id,
                                                                     drug_ndc_dimensions_dict=drug_ndc_dimensions_dict[
                                                                         ndc_txr],
                                                                     drug_dict=drug_dict)
                    for key in drug_dict.keys():
                        try:
                            df_dict.setdefault(key, []).append(drug_dict[key])
                        except KeyError:
                            pass
            else:
                big_stick = ''
                Recommended_Big_Stick_Serial_Number = {}
                canister_id = []
                drug_dict = insert_drug_canister_details(drug_record=record, big_stick=big_stick,
                                                         Recommended_Big_Stick_Serial_Number=
                                                         Recommended_Big_Stick_Serial_Number,
                                                         canister_id=canister_id,
                                                         drug_ndc_dimensions_dict=drug_ndc_dimensions_dict[ndc_txr],
                                                         drug_dict=drug_dict)
                for key in drug_dict.keys():
                    try:
                        df_dict.setdefault(key, []).append(drug_dict[key])
                    except KeyError:
                        pass
            index = index + 1
        return df_dict
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.info(e)
        raise e


def insert_drug_canister_details(drug_record: dict, big_stick: str, Recommended_Big_Stick_Serial_Number,
                                 canister_id: list,
                                 drug_ndc_dimensions_dict: dict,
                                 drug_dict) -> dict:
    """
    Insert drug and canister details in dictionary
    @param: drug_record, big_stick, canister_stick_details_list, drugndc_dimensions_dict, drug_dict
    @return record: dictionary containing all the details related to drug, existing canister and recommended canisters
    """
    try:
        drug_dict['priority'] = drug_ndc_dimensions_dict['priority']
        drug_dict['Drug_NDC'] = drug_ndc_dimensions_dict['fndc']
        drug_dict['formatted_ndc_txr'] = drug_ndc_dimensions_dict['fndc_txr']
        drug_dict['Drug_Name'] = drug_ndc_dimensions_dict['drug_name']
        drug_dict['Strength_Value'] = drug_ndc_dimensions_dict['strength_value']
        drug_dict['Strength'] = drug_ndc_dimensions_dict['strength']
        drug_dict['Width'] = drug_ndc_dimensions_dict['width']
        drug_dict['Depth'] = drug_ndc_dimensions_dict['depth']
        drug_dict['Length'] = drug_ndc_dimensions_dict['length']
        drug_dict['Fillet'] = drug_ndc_dimensions_dict['fillet']
        drug_dict['Custom_Shape'] = drug_ndc_dimensions_dict['shape']
        drug_dict['Canister_Id'] = drug_ndc_dimensions_dict['canister_id']
        drug_dict['Big_Stick_Serial_Number'] = drug_ndc_dimensions_dict['big_stick_serial_number']
        drug_dict['Big_Stick_Width'] = drug_ndc_dimensions_dict['big_stick_width']
        drug_dict['Big_Stick_Depth'] = drug_ndc_dimensions_dict['big_stick_depth']
        drug_dict['Small_Stick_Serial_Number_Length'] = drug_ndc_dimensions_dict[
            'small_stick_serial_number_length']
        drug_dict['Canister_Drum_Serial_Number'] = drug_ndc_dimensions_dict['canister_drum_serial_number']
        drug_dict['available_big_stick_inventory'] = drug_record['available_big_stick_inventory']
        drug_dict['available_mold_id_list'] = drug_record['available_mold_id_list']
        drug_dict['recommended_small_stick'] = drug_record['Small Stick']
        drug_dict['mft'] = drug_record['mft']
        # drug_dict['width_3D'] = drug_record['width_3D']
        # drug_dict['depth_3D'] = drug_record['depth_3D']
        drug_dict['Big_Stick'] = drug_record['Big Stick']
        drug_dict['drum_width1_3D'] = drug_record['drum_width1_3D']
        drug_dict['drum_width2_3D'] = drug_record['drum_width2_3D']
        drug_dict['drum_depth1_3D'] = drug_record['drum_depth1_3D']
        drug_dict['drum_depth2_3D'] = drug_record['drum_depth2_3D']
        drug_dict['small_stick_3D'] = drug_record['small_stick_3D']
        drug_dict['drum_length_3D'] = drug_record['drum_length_3D']
        drug_dict['depth_brush_3D'] = drug_record['depth_brush_3D']
        drug_dict['recommended_big_stick'] = str(big_stick)
        drug_dict['Recommended_Big_Stick_Serial_Number'] = Recommended_Big_Stick_Serial_Number
        drug_dict['Recommended_Canister_Id'] = str(canister_id)
        deactivated_canister_comment = CanisterMaster.db_get_deactive_canisters_comment(
            canister_id=canister_id)
        if deactivated_canister_comment:
            comment = [dict["comment"] for dict in deactivated_canister_comment]
            canister_id2 = [dict["id"] for dict in deactivated_canister_comment]
            drug_dict['Reason for Deactivation'] = str(canister_id2) + ':' + str(comment)
        else:
            drug_dict['Reason for Deactivation'] = 'No Reason Found'
        drug_dict['drug_count'] = drug_record['drug_count']
        drug_dict['pack_count'] = drug_record['pack_count']
        if drug_ndc_dimensions_dict['small_stick_serial_number_length'] != 'None':
            values = drug_ndc_dimensions_dict['small_stick_serial_number_length'].split(',')
            values = [float(value) for value in values]
            drug_dict['brush_height'] = float(sum(values) / len(values)) - 4
        else:
            drug_dict['brush_height'] = 0
        if drug_record['available_mold_id_list']:
            if drug_ndc_dimensions_dict['big_stick_depth'] != 'None':
                values = drug_ndc_dimensions_dict['big_stick_depth'].split(',')
                values = [float(value) for value in values]
                drug_dict['brush_length'] = min(math.floor(sum(values) / len(values) - 0.2) + 0.5, 3.5)
            else:
                drug_dict['brush_length'] = 0
        else:
            if drug_record['drum_depth1_3D'] != 0:
                drug_dict['brush_length'] = math.floor(drug_record['drum_depth1_3D'] - 0.5) + 0.5
            elif drug_record['drum_depth2_3D'] != 0:
                drug_dict['brush_length'] = math.floor(drug_record['drum_depth2_3D'] - 0.5) + 0.5
            else:
                drug_dict['brush_length'] = 0

        return drug_dict
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.info(e)
        raise e


@log_args_and_response
def get_available_drugs_for_recommended_canisters(ndc_list):
    try:
        canisters_df = get_canister_stick_details(ndc_list)
        if isinstance(canisters_df, str):
            return error(1004)
        canisters_list = canisters_df.to_dict(orient='records')
        # drug_list = [record['Drug_NDC'] for record in canisters_list if record['Recommended_Canister_Id']]
        drug_list = []
        for record in canisters_list:
            if isinstance(record['Recommended_Canister_Id'], str):
                record['Recommended_Canister_Id'] = json.loads(record['Recommended_Canister_Id'])
            if record['Recommended_Canister_Id']:
                drug_list.append(record['Drug_NDC'])

        return list(set(drug_list))

    except Exception as e:
        return e


@log_args_and_response
def get_change_ndc_history(paginate, filter_fields):
    """
    Function to get change ndc history list for given filters
    """
    try:

        response_list, old_drug_list, new_drug_list, count = get_change_ndc_history_dao(paginate, filter_fields)
        old_drug_list = sorted(old_drug_list)
        new_drug_list = sorted(new_drug_list)
        response_dict = {"change_ndc_history_list": response_list,
                         "old_drug_list": old_drug_list,
                         "new_drug_list": new_drug_list,
                         "count": count}
        return create_response(response_dict)
    except Exception as e:
        return e


@log_args_and_response
def get_canister_order_list(paginate, company_id, filter_fields):
    """
    Function to get canister orders list which are ordered.
    """
    try:
        response_list, count, ndc_list = get_canister_order_list_dao(paginate, company_id,filter_fields)
        if ndc_list:
            change_ndc_drug_list = get_available_drugs_for_recommended_canisters(ndc_list)
            change_ndc_drug_list = [x.zfill(11) for x in change_ndc_drug_list]
            for record in response_list:
                record['change_ndc_available'] = True if record['ndc'] in change_ndc_drug_list else False
        response_data = {
            "canister_list": response_list,
            "total_count": count
        }
        return create_response(response_data)
    except Exception as e:
        logger.error(f"error occured in get_canister_order_list {e}")
        return e
