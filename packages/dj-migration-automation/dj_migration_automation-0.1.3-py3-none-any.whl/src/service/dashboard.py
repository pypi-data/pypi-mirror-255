import functools
import operator
import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

import numpy as np
import pandas as pd

from peewee import InternalError, IntegrityError, fn

import settings
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import get_current_date, log_args
from dosepack.validation.validate import validate
from src.dao.dashboard_dao import get_active_canister_count, get_drug_state_dao, get_max_canister_count, \
    get_top_drug_dao, get_pack_error_instances_dao, \
    get_pack_error_distribution_dao, get_error_pill_instances, get_error_pill_instances_by_canister, \
    get_error_pill_instances_by_group, graph_type_flags, get_error_drug_count_query, group_flags, \
    get_error_instances_count_query, get_lost_pill_instances_dao, get_pharmacy_master_data_dao, get_pack_error_stats_dao
from src.model.model_drug_master import DrugMaster

logger = settings.logger


def get_drug_stat(no_of_days, device_id, company_id, max_handfilled_drug=5):
    """
    Takes robot_id, company_id and no of days and returns the stats of the drug.

    Returns: Returns an object containing various stats for the drugs for the given company_id and robot.

    """

    drug_filled_data: dict = dict()
    hand_filled_drug_data = {}
    ndc_drugname_map: dict = dict()
    data: dict = dict()

    # adding max_hand filled_drugs as optional field to make flexible code, default max 5 hand filled drug
    current_date = get_current_date()
    previous_date = datetime.strptime(current_date, '%Y-%m-%d') - timedelta(days=no_of_days)
    current_date = datetime.strptime(current_date, '%Y-%m-%d')
    pack_status_list = [settings.PROCESSED_PACK_STATUS,
                        settings.DONE_PACK_STATUS,
                        settings.VERIFIED_PACK_STATUS]
    pack_list: list = list()

    try:
        active_canisters = get_active_canister_count(device_id)
        logger.info("In get_drug_stat: active_canisters: {}".format(active_canisters))

        max_canisters = get_max_canister_count(device_id)
        logger.info("In get_drug_stat: max_canisters: {}".format(max_canisters))

        query = get_drug_state_dao(company_id=company_id,
                                   current_date=current_date,
                                   pack_status_list=pack_status_list,
                                   previous_date=previous_date)

        for record in query:
            record["quantity"] = float(record["quantity"])
            record["created_date"] = datetime.strftime(record["created_date"], '%Y-%m-%d')

            if record["pack_id"] not in pack_list:
                pack_list.append(record["pack_id"])
            if record["created_date"] not in drug_filled_data:
                drug_filled_data[record["created_date"]] = {}
                drug_filled_data[record["created_date"]]["manual_drug_count"] = 0
                drug_filled_data[record["created_date"]]["robot_drug_count"] = 0
            if record["is_manual"] == True:
                drug_filled_data[record["created_date"]]["manual_drug_count"] += 1
                if record["ndc"] not in hand_filled_drug_data:
                    hand_filled_drug_data[record["ndc"]] = 0
                    ndc_drugname_map[record["ndc"]] = record["drug_name"] + " " + record["strength_value"] + " " + record[
                        "strength"]
                hand_filled_drug_data[record["ndc"]] += 1
            else:
                drug_filled_data[record["created_date"]]["robot_drug_count"] += 1

        hand_filled_drug_data = sorted(hand_filled_drug_data.items(),
                                       key=operator.itemgetter(1), reverse=True)
        hand_filled_drug_data = hand_filled_drug_data[:max_handfilled_drug]  # top 5 manually filled drugs

        pack_verified_with_failure = 0
        pack_verified_with_success = 0

        # pack_verification_query = get_pack_verification_data_dao(pack_list=pack_list)
        #
        # if len(pack_list) > 0:
        #     for record in pack_verification_query:
        #         if record["pack_fill_status"] == 20:
        #             pack_verified_with_failure += 1
        #         elif record["pack_fill_status"] == 19:
        #             pack_verified_with_success += 1

        data["active_canisters"] = active_canisters
        data["max_canisters"] = max_canisters
        data["processed_packs"] = len(pack_list)
        data["drugs_filled"] = drug_filled_data
        data["hand_filled_drugs"] = hand_filled_drug_data
        data["ndc_drugname_map"] = ndc_drugname_map
        if pack_verified_with_failure + pack_verified_with_success > 0:
            data["error_rate"] = (pack_verified_with_failure /
                                  (pack_verified_with_success + pack_verified_with_failure)
                                  ) * 100
        else:
            data["error_rate"] = 0
        return create_response(data)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_drug_stat {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_stat: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_drug_stat {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_stat: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_drug_stat: " + str(e))


def get_pack_error_stats(filters):
    """
    Returns no. of error packs and total packs date wise
    @param filters: dict
    :return: json
    """
    system_id = filters['system_id']
    results: list = list()
    try:
        query = get_pack_error_stats_dao(filters=filters)

        for record in query:
            record['error_packs'] = int(record['error_packs'])
            results.append(record)
        pharmacy_data = next(get_pharmacy_master_data_dao(system_id))

        response = {'error_stats': results, 'pharmacy_data': pharmacy_data}
        return create_response(response)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_drug_stat {}".format(e))
        return error(1000, "Error in get_drug_stat: " + str(e))


@validate(required_fields=['system_id'])
def get_top_drugs(data):
    """
    returns top n number of drugs in pharmacy specified by user if not specified than top 10
    :param data: dictionary
    :return: json
    """
    try:
        query, top_drugs_data = get_top_drug_dao(data)

        for record in query:
            top_drugs_data.append(record)
        return create_response(top_drugs_data)
    except(InternalError, IntegrityError) as e:
        logger.error(e, exec_info=True)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_drug_stat {}".format(e))
        return error(1000, "Error in get_drug_stat: " + str(e))


@validate(required_fields=["from_date", "to_date", "system_id", "time_zone"])
def get_pack_error_instances(data):
    """
        function to get pack error instance
        :param data: dictionary
        :return: json
    """
    try:
        query = get_pack_error_instances_dao(data=data)

        error_pack_instances = list()

        for item in query.dicts():
            item["error_less_packs"] = item['total_packs'] - item['error_packs']
            error_pack_instances.append(item)

        if "period_cycle" in data:
            return create_response(error_pack_instances)
        else:
            return create_response(error_pack_instances[0])

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_drug_stat {}".format(e))
        return error(1000, "Error in get_drug_stat: " + str(e))


@validate(required_fields=["from_date", "to_date", "system_id", "time_zone"])
def get_pack_error_distribution(data):
    """
    @param data:
    @return:

    """
    try:
        error_distribution_list: list = list()
        query = get_pack_error_distribution_dao(data=data)

        for item in query.dicts():
            item["total_error_instances"] = item["broken_instances"] \
                                            + item["misplaced_instances"] \
                                            + item["extra_instances"] \
                                            + item["missing_instances"]
            error_distribution_list.append(item)
        if "period_cycle" in data:
            return create_response(error_distribution_list)
        else:
            return create_response(error_distribution_list[0])
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_pack_error_distribution {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in get_pack_error_distribution {}".format(e))
        return error(1000, "Error in get_pack_error_distribution: " + str(e))


@log_args
@validate(required_fields=["from_date", "to_date", "system_id", "time_zone", "group", "graph"])
def get_extra_pill_error_instances(data):
    """
    @param data:
    @return:
    """
    try:
        response: dict = dict()
        if data["graph"] not in graph_type_flags:
            return error(1020, 'Incorrect value for graph.')

        if data["graph"] == "pie":
            response = get_error_pill_instances(data, "extra")

        if data["graph"] == "line":
            if "canister_id" in data or ("location_number" in data and "device_id" in data):
                response = get_error_pill_instances_by_canister(data, "extra")
            else:
                response = get_error_pill_instances_by_group(data, "extra")

        return response

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_extra_pill_error_instances {}".format(e))
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_extra_pill_error_instances {}".format(e))
        return error(1000, "Error in get_extra_pill_error_instances: " + str(e))


@validate(required_fields=["from_date", "to_date", "system_id", "time_zone", "group", "graph"])
def get_missing_pill_error_instances(data):
    """

    @param data:
    @return:
    """
    try:
        response = {}
        if data["graph"] not in graph_type_flags:
            return error(1020, 'Incorrect value for graph.')

        if data["graph"] == "pie":
            response = get_error_pill_instances(data, "missing")

        if data["graph"] == "line":
            if "canister_id" in data or ("location_number" in data and "device_id" in data):
                response = get_error_pill_instances_by_canister(data, "missing")
            else:
                response = get_error_pill_instances_by_group(data, "missing")

        return response
    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_missing_pill_error_instances {}".format(e))
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_missing_pill_error_instances {}".format(e))
        return error(1000, "Error in get_missing_pill_error_instances: " + str(e))


@validate(required_fields=["from_date", "to_date", "system_id", "time_zone", "graph"])
def get_broken_pill_error_instances(data):
    """
    @param data:
    @return:
    """
    if data["graph"] not in graph_type_flags:
        return error(1020, 'Incorrect value for graph.')

    error_drug_count_query = get_error_drug_count_query(data)

    error_drug_count_query = error_drug_count_query.alias("error_drug_count")

    try:
        if data["graph"] == "pie":
            if 'group' not in data:
                return error(1020, 'Pie graph requires Group value.')

            if data["group"] not in group_flags:
                return error(1020, 'Incorrect value for group.')

            if data["group"] == "unique_drug":
                select_fields = [DrugMaster.drug_name,
                                 DrugMaster.strength_value,
                                 DrugMaster.strength]

                where_field, query = get_error_instances_count_query(data, "broken", select_fields)
                query = query.where(where_field == 1).group_by(query.c.unique_drug_id)
                print('final', query)

            if data["group"] == "canister_level":
                if not 'drug' in data or not 'total_error_instances' in data:
                    return error(1020, 'The parameter canister_level requires drug and total_error_instances.')
                select_fields = [DrugMaster.drug_name,
                                 DrugMaster.strength_value,
                                 DrugMaster.strength]
                where_field, query = get_error_instances_count_query(data, "broken", select_fields)
                clauses = list()
                clauses.append((where_field == True))
                drug = data.get('drug', None)
                clauses.append((query.c.unique_drug_id == drug))
                query = query.group_by(query.c.canister_level).where(functools.reduce(operator.and_, clauses))
            response_data = list()
            total_broken_instances = 0
            level_error_list = list()
            for item in query.dicts():
                total_broken_instances += item["broken_error_instance"]

                print(item)
                response_data.append(item)
                print(response_data)
            recommendation = list()
            if 'total_error_instances' in data:
                total_error_instances = data['total_error_instances']
                level_percentage_error_threshold = data.get('level_error_threshold', settings.LEVEL_PERCENTAGE_ERROR_THRESHOLD)
                level_error_threshold = (level_percentage_error_threshold * total_broken_instances) /100
                total_percentage_error_threshold = data.get('total_error_threshold',
                                                            settings.TOTAL_PERCENTAGE_ERROR_THRESHOLD)
                percentage_error = (total_percentage_error_threshold * total_error_instances) / 100

                if total_broken_instances >= percentage_error:
                    for record in response_data:
                        if record['broken_error_instance'] > level_error_threshold:
                            level_error_list.append(record['canister_level'])
                            drug_name = record['drug_name']
                            strength_value = record['strength_value']
                            strength = record['strength']

                    if level_error_list:
                        level_error_list.sort()
                        recommendation_level = settings.RECOMMENDATION[level_error_list[0] -1]
                        # recommendation.append('You should not store {} {} {} at Level-{} instead {}'.format(drug_name, strength_value, strength, level_error_list[0], recommendation_level))
                        recommendation.append({
                            'drug_name': '{} {} {}'.format(drug_name, strength_value, strength),
                            'current_level': level_error_list[0],
                            'expected_level': recommendation_level
                        })

            return create_response({"total_instances": total_broken_instances, "error_data": response_data,
                                    'recommendation': recommendation})

        if data["graph"] == "line":
            response = get_error_pill_instances_by_group(data, "broken")
            return response
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_broken_pill_error_instances {}".format(e))
        return error(1000, "Error in get_broken_pill_error_instances: " + str(e))


@validate(required_fields=["from_date", "to_date", "system_id", "time_zone"])
def get_misplaced_pill_instances(data):
    """

    @param data:
    @return:
    """
    try:
        if "period_cycle" in data:
            response = get_error_pill_instances_by_group(data, "misplaced")
            return response
        else:
            error_drug_count_query = get_error_drug_count_query(data)

            error_drug_count_query = error_drug_count_query.alias("error_drug_count")

            where_field, query = get_error_instances_count_query(data, "misplaced")
            query = query.where(where_field > 0).group_by(fn.DATE(error_drug_count_query.c.created_date))

            error_data = list()
            error_date_dict = dict()
            total_instances = 0
            for item in query.dicts():
                total_instances += item["misplaced_error_instance"]
                error_data.append(item)
                error_date_dict[item['created_date']] = item["misplaced_error_instance"]

            error_list = list()
            for i in sorted(error_date_dict.keys()):
                error_list.append(error_date_dict[i])

            series_error_data = pd.Series(np.array(error_list))
            recommendation = list()
            window = data.get('window', 4)
            threshold_value = data.get('threshold_value', 3)
            moving_average = series_error_data.rolling(window=window).mean()
            pprint(moving_average)
            moving_average = moving_average[(window - 1):]
            moving_average = list(moving_average)
            pprint(moving_average)
            # date_list = date_list[window:]
            for i in range(len(moving_average)):
                if moving_average[i] > threshold_value:
                    if 'canister_id' in data:
                        recommendation.append({'days': window})
                        break

            return create_response(
                {"total_instances": total_instances, "error_data": error_data, 'recommendation': recommendation})
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    except Exception as e:
        logger.error("Error in get_misplaced_pill_instances {}".format(e))
        return error(1000, "Error in get_misplaced_pill_instances: " + str(e))


@validate(required_fields=["system_id", "company_id"])
def get_lost_pill_instances(data):
    """
    @param data:
    @return:
    """
    try:
        query = get_lost_pill_instances_dao(data)

        response = list(query.dicts())
        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("Error in get_lost_pill_instances {}".format(e))
        return error(1000, "Error in get_lost_pill_instances: " + str(e))
