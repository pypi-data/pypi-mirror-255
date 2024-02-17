"""
This module contains helper function to create APIs using peewee module.
"""
import functools
import json
import os
from datetime import timedelta
import operator

import settings
import pandas as pd
from functools import reduce
from peewee import fn

from dosepack.error_handling.error_handler import datetime_handler
from dosepack.utilities.utils import log_args_and_response
from src import constants

logger = settings.logger


@log_args_and_response
def get_filters(clauses, fields_dict, filter_dict,
                exact_search_fields=None,
                like_search_fields=None,
                membership_search_fields=None,
                between_search_fields=None,
                left_like_search_fields=None,
                right_like_search_fields=None):
    """
    Appends applicable filters to `clauses` list and return `clauses`
    @param clauses: list List which may contain peewee filters
    @param filter_dict:
    @param fields_dict: dict Dict which contains key as field names and value as peewee fields
    @param exact_search_fields: list List containing field names for exact search
    @param like_search_fields: list List containing field names for search using like operator
    @param membership_search_fields: list List containing field names for search using in operator
    @param between_search_fields: list List containing field names for search using between operator
    @param left_like_search_fields: list List containing field names for searching 'data%' using like operator
    @param right_like_search_fields: list List containing field names for searching '%data' using like operator
    @return: list
    """
    if not filter_dict:
        return clauses
    for k, v in filter_dict.items():
        if exact_search_fields and k in exact_search_fields:
            if v is None:
                clauses.append(fields_dict[k] == v)
            else:
                v = [v] if type(v) is not list else v
                clauses.append(fields_dict[k] << v)

        if like_search_fields and k in like_search_fields:
            data = str(v).translate(str.maketrans({'%': r'\%'}))  # escape % from search string
            search_data = "%" + data + "%"
            clauses.append(fn.CONCAT('', fields_dict[k]) ** search_data)
        if membership_search_fields and k in membership_search_fields and v:
            clauses.append((fields_dict[k] << v))
        # check if from and to value present
        if between_search_fields and k in between_search_fields:
            if 'from' in v and 'to' in v and v['from'] is not None and v['to'] is not None:
                clauses.append((fields_dict[k].between(v['from'], v['to'])))
            elif v.get('from') is not None and v.get('to') is None:
                clauses.append((fields_dict[k] >= v['from']))
            elif v.get('to') is not None and v.get('from') is None:
                clauses.append((fields_dict[k] <= v['to']))
        if left_like_search_fields and k in left_like_search_fields:
            data = str(v).translate(str.maketrans({'%': r'\%'}))  # escape % from search string
            search_data = data + "%"
            clauses.append((fn.CONCAT('', fields_dict[k]) ** search_data))
        if right_like_search_fields and k in right_like_search_fields:
            data = str(v).translate(str.maketrans({'%': r'\%'}))  # escape % from search string
            search_data = "%" + data
            clauses.append((fields_dict[k] ** search_data))

    return clauses


def get_having_clause(clauses, fields_dict, filter_dict, having_clause_dict=None):
    """
    Appends applicable conditions in the clauses list to be used with having clause for checking
    :param clauses: list List which may contain peewee filters
    :param fields_dict: dict Dict which contains key as field names and value as peewee fields
    :param filter_dict: Dictionary for which we need to check if filters can be applied
    :param having_clause_dict: Columns for which we need to check for having clause condition
    :return:
    """
    if not filter_dict:
        return clauses
    for k, v in filter_dict.items():
        if having_clause_dict and k in having_clause_dict:
            if type(v) == list:
                v_list_str = [str(i) for i in v]
                if len(v_list_str) > 1:
                    v_str = ",".join(v_list_str)
                    v_str_2 = ",".join(v_list_str)[::-1]
                else:
                    v_str = ",".join(v_list_str)
                    v_str_2 = ",".join(v_list_str)
            else:
                v_str = v
                v_str_2 = v

            clauses.append((fields_dict[k] == (v_str)))

            if v_str_2 != v_str:
                clauses.append((fields_dict[k] == (v_str_2)))
            print("clauses", clauses)
    return clauses


@log_args_and_response
def get_orders(orders, fields_dict, order_list):
    """
    Appends applicable orders to `orders` list and return `orders`

    :param orders: list List which may contain peewee fields to order
    :param fields_dict: dict Dict which contains key as field names and value as peewee fields
    :param order_list: list Every element should be list of two element. first is field_name
    from fields_dict and second is order direction 1 for ascending and -1 for descending
    :return: list
    """
    if not order_list:
        return orders
    for item in order_list:
        if item[1] == -1:  # descending order
            orders.append(fields_dict[item[0]].desc())
        elif item[1] == 1:  # ascending order
            orders.append(fields_dict[item[0]])
    return orders


def apply_paginate(query, paginate):
    """
    Returns query with pagination on it.
    :param query: peewee.SelectQuery query query on which pagination should be applied
    :param paginate: dict Dict containing keys ["page_number", "number_of_rows"]
    :return: peewee.SelectQuery
    """
    if 'page_number' not in paginate:
        raise ValueError('paginate paramater must have key page_number')
    if 'number_of_rows' not in paginate:
        raise ValueError('paginate paramater must have key number_of_rows')

    return query.paginate(paginate['page_number'], paginate['number_of_rows'])


@log_args_and_response
def get_results(query,
                fields_dict,
                filter_fields=None,
                sort_fields=None,
                paginate=None,
                clauses=None,
                clauses_having=None,
                exact_search_list=None,
                like_search_list=None,
                having_search_list=None,
                membership_search_list=None,
                non_paginate_result_field_list=None,
                distinct_non_paginate_results=False,
                between_search_list=None,
                last_order_field=None,
                left_like_search_fields=None,
                identified_order=None,
                limit_records=False):
    """
    Returns returns paginated result, total count of result in tuple.
    This function is wrapper to filter, sort and paginate using request args on query
    - Use this function if filtering, sorting and pagination is
    straight forward on a given `query`
    :param query: peewee.SelectQuery query on filtering needs to be done
    :param fields_dict: dict fields required for filtering, sorting
    :param filter_fields: dict fields to filter
    :param sort_fields: list fields to sort data (order matters)
    :param paginate: dict page_number and number_of_rows keys to paginate
    :param clauses: list filters which should already applied on query, can be empty
    :param exact_search_list: list fields which will have `=` filter
    :param like_search_list: list fields which will have `like` filter
    :param membership_search_list: list fields which will have `in` filter
    :param between_search_list: list fields which will have `between` filter
    :param last_order_field: peewee.Field field to provide consistent sorted data
    (required when user orders using fields which can have multiple rows with same data)
    :param clauses_having
    :param having_search_list
    :return: tuple
    """
    results = list()
    if clauses is None:
        clauses = list()

    if clauses_having is None:
        clauses_having = list()

    if identified_order:
        order_list = identified_order
    else:
        order_list = list()
    clauses = get_filters(clauses, fields_dict, filter_fields,
                          exact_search_fields=exact_search_list,
                          like_search_fields=like_search_list,
                          membership_search_fields=membership_search_list,
                          between_search_fields=between_search_list,
                          left_like_search_fields=left_like_search_fields
                          )

    clauses_having = get_having_clause(clauses_having, fields_dict, filter_fields, having_search_list)
    order_list = get_orders(order_list, fields_dict, sort_fields)
    if last_order_field:
        order_list.extend(last_order_field)  # To provide consistent result
    if clauses:
        query = query.where(reduce(operator.and_, clauses))
    if clauses_having:
        query = query.having(reduce(operator.and_, clauses_having))
    if order_list:
        query = query.order_by(*order_list)

    if not limit_records:
        count = query.count()

    if non_paginate_result_field_list:
        non_paginate_result = {}
        for record in query:
            for field in non_paginate_result_field_list:
                if not distinct_non_paginate_results:
                    if field not in non_paginate_result:
                        non_paginate_result[field] = []
                    non_paginate_result[field].append(record[field])
                else:
                    if field not in non_paginate_result:
                        non_paginate_result[field] = set()
                    non_paginate_result[field].add(record[field])

    if paginate:
        query = apply_paginate(query, paginate)
    for record in query:
        results.append(record)

    if limit_records:
        count = settings.NUMBER_OF_RECORDS_LIMIT

    if non_paginate_result_field_list:
        return results, count, non_paginate_result

    else:
        return results, count


def get_results_prs(query,
                    fields_dict,
                    filter_fields=None,
                    sort_fields=None,
                    paginate=None,
                    clauses=None,
                    clauses_having=None,
                    exact_search_list=None,
                    like_search_list=None,
                    having_search_list=None,
                    membership_search_list=None,
                    non_paginate_result_field_list=None,
                    distinct_non_paginate_results=False,
                    between_search_list=None,
                    last_order_field=None,
                    left_like_search_fields=None,
                    identified_order=None):
    """
    Returns returns paginated result, total count of result in tuple.
    This function is wrapper to filter, sort and paginate using request args on query
    - Use this function if filtering, sorting and pagination is
    straight forward on a given `query`
    :param query: peewee.SelectQuery query on filtering needs to be done
    :param fields_dict: dict fields required for filtering, sorting
    :param filter_fields: dict fields to filter
    :param sort_fields: list fields to sort data (order matters)
    :param paginate: dict page_number and number_of_rows keys to paginate
    :param clauses: list filters which should already applied on query, can be empty
    :param exact_search_list: list fields which will have `=` filter
    :param like_search_list: list fields which will have `like` filter
    :param membership_search_list: list fields which will have `in` filter
    :param between_search_list: list fields which will have `between` filter
    :param last_order_field: peewee.Field field to provide consistent sorted data
    (required when user orders using fields which can have multiple rows with same data)
    :param clauses_having
    :param having_search_list
    :return: tuple
    """
    results = list()
    count = 0

    if clauses is None:
        clauses = list()

    if clauses_having is None:
        clauses_having = list()

    if identified_order:
        order_list = identified_order
    else:
        order_list = list()
    clauses = get_filters(clauses, fields_dict, filter_fields,
                          exact_search_fields=exact_search_list,
                          like_search_fields=like_search_list,
                          membership_search_fields=membership_search_list,
                          between_search_fields=between_search_list,
                          left_like_search_fields=left_like_search_fields
                          )

    clauses_having = get_having_clause(clauses_having, fields_dict, filter_fields, having_search_list)
    order_list = get_orders(order_list, fields_dict, sort_fields)
    if last_order_field:
        order_list.extend(last_order_field)  # To provide consistent result
    if clauses:
        query = query.where(reduce(operator.and_, clauses))
    if clauses_having:
        query = query.having(reduce(operator.and_, clauses_having))
    if order_list:
        query = query.order_by(*order_list)

    if non_paginate_result_field_list:
        non_paginate_result = {"pvs_slot_id": list(),
                               "pack_id": list()}

        for record in query:
            non_paginate_result['pvs_slot_id'].append(record['pvs_slot_id'])
            non_paginate_result['pack_id'].append(record['pack_id'])

    if paginate:
        query = apply_paginate(query, paginate)
    for record in query:
        results.append(record)

    if non_paginate_result_field_list:
        return results, count, non_paginate_result

    else:
        return results, count


def get_multi_search(clauses, multi_search_values, model_search_fields, ndc_search_field=None,
                     ndc_search_function=None, or_search_field=None, left_like_search=False):
    """
    Appends applicable filters to `subclauses` with  `or` operaor and append sublcauses to `clauses`  list and return `clauses`
    @param clauses:
    @param model_search_fields: list of model to be compare with
    @param multi_search_values: list of values to filter
    @return: list
    """
    if not multi_search_values:
        return clauses
    subclauses = list()
    for value in multi_search_values:
        # subclauses = list()
        data = str(value).translate(str.maketrans({'%': r'\%'}))  # escape % from search string
        if left_like_search:
            search_data = data + "%"
        else:
            search_data = "%" + data + "%"
        for field in model_search_fields:
            subclauses.append((fn.CONCAT('', field) ** search_data))
        if or_search_field:
            subclauses.extend((or_search_field))
    reducedsubclauses = functools.reduce(operator.or_, subclauses)
    clauses.append(reducedsubclauses)
    return clauses


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


@log_args_and_response
def calculate_max_possible_drug_quantity_in_refill_device(drug_unit_weight):
    if float(drug_unit_weight) != float(0):
        max_drug_quantity = float(constants.WEIGHING_LIMITATION_OF_REFILL_DEVICE) / float(drug_unit_weight)
        return int(max_drug_quantity)
    return None


@log_args_and_response
def get_expected_delivery_date(admin_start_date, start_date, delivery_date_offset, fill_cycle, no_of_days):
    """
    returns expected schedule for given data
    :param admin_start_date:
    :param start_date:
    :param delivery_date_offset:
    :param fill_cycle:
    :param no_of_days:
    :return: dict
    """
    # start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    # admin_start_date = datetime.datetime.strptime(admin_start_date, "%Y-%m-%d")
    response = {}
    if start_date is None:
        response['next_delivery_date'] = None
        return response
    # start_date = start_date
    # admin_start_date = admin_start_date.date()
    # current_date = datetime.datetime.now().date()
    delivery_date_offset = int(delivery_date_offset)
    if no_of_days is not None:
        no_of_days = int(no_of_days)
    freq_dict = {46: '7D', 47: '14D', 48: '28D'}
    days = {46: 7, 47: 14, 48: 28}
    fill_cycle = int(fill_cycle)
    try:
        frequency = freq_dict[fill_cycle]
        day = days[fill_cycle]
    except KeyError as e:
        frequency = "{}D".format(no_of_days)
        day = no_of_days
    # current_date = current_date.date()
    days_buffer_for_delivery = int(os.environ.get('DELIVERY_BUFFER', 0))
    end_date = admin_start_date
    admin_start_date = admin_start_date - timedelta(days=days_buffer_for_delivery)  # delivered before a day
    schd = pd.date_range(start_date, end_date, freq=frequency)
    schd = sorted(schd, reverse=True)
    logger.info('In get_expected_delivery_date, schedules_admin_delivery_date {}'.format(str(schd)))
    # sch_date_list = list()
    # for i in schd:
    #     sch_date_list.append(i.date())
    # if admin_start_date <= start_date:
    #     response['next_schedule_date'] = start_date
    # elif admin_start_date in sch_date_list:
    #     response["next_schedule_date"] = admin_start_date
    # else:
    #     last_schedule_date = sch_date_list[-2]
    #     last_schedule_date = datetime.datetime.combine(last_schedule_date, datetime.datetime.min.time())
    #     delivery_date = last_schedule_date + timedelta(days=delivery_date_offset)
    #     delivery_date = delivery_date.date()
    #     # import_date = datetime.datetime.combine(import_date, datetime.datetime.min.time())
    #     if admin_start_date <= delivery_date:
    #         response['next_schedule_date'] = last_schedule_date
    #     else:
    #         last_schedule_date = sch_date_list[-1]
    #         response['next_schedule_date'] = last_schedule_date
    # sch_date_list = list()
    for i in schd:
        delivery_date = i + timedelta(days=delivery_date_offset)
        if delivery_date <= admin_start_date:
            response['next_delivery_date'] = delivery_date.to_pydatetime()
            return response
    response['next_delivery_date'] = None
    return response


def getdatarows(query):
    data = list()
    for record in query:
        data.append(record)
    return handledate(data)


def handledate(response):
    return json.loads(json.dumps(response, default=datetime_handler, indent=4))


def getrecords(body, fields, query, onlydata=False):
    filter = {"paginate": {"page_number": 1, "number_of_rows": 100000 if onlydata else 10}, "sorts": [], "filters": {}}
    filter.update(body)
    clauses = list()
    global_clauses = list()
    for k, v in filter["filters"].items():
        if v is not None:
            if k == "global":
                va = '%' + v + '%'
                for fk, fv in fields.items():
                    global_clauses.append(fn.CONCAT('', fv) ** va)
            else:
                if k in fields:
                    if isinstance(v, dict):
                        if 'from' in v and 'to' in v and v['from'] is not None and v['to'] is not None:
                            clauses.append((fields[k].between(v['from'], v['to'])))
                        elif 'from' in v and v['from'] is not None and (
                                'to' not in v or ('to' in v and v['to'] is None)):
                            clauses.append((fields[k] >= v['from']))
                        elif 'to' in v and v['to'] is not None and (
                                'from' not in v or ('from' in v and v['from'] is None)):
                            clauses.append((fields[k] <= v['to']))
                    elif isinstance(v, list):
                        if len(v) > 0:
                            clauses.append((fields[k] << v))
                    elif v is not None and (k.find("date_from") >= 0 or k.find("date_to") >= 0):
                        if k.find("date_from") >= 0:
                            clauses.append((fields[k] >= v))
                        if k.find("date_to") >= 0:
                            clauses.append((fields[k] <= v))
                    else:
                        sv = str(v)
                        if len(sv) > 0:
                            if sv[0] == "%" and sv[len(sv) - 1] == "%":
                                val = str(sv[1:len(sv) - 1]).translate(str.maketrans({'%': r'\%'}))
                                clauses.append((fields[k] ** sv))
                            elif sv[0] == "%":
                                val = str(sv[1:len(sv)]).translate(str.maketrans({'%': r'\%'}))
                                clauses.append((fields[k] ** sv))
                            elif sv[len(sv) - 1] == "%":
                                val = str(sv[0:len(sv) - 1]).translate(str.maketrans({'%': r'\%'}))
                                clauses.append((fields[k] ** sv))
                            else:
                                clauses.append(fields[k] == v)
    orders = list()
    for item in filter["sorts"]:
        if item[0] in fields:
            if item[1] == -1:  # descending order
                orders.append(fields[item[0]].desc())
            elif item[1] == 1:  # ascending order
                orders.append(fields[item[0]])
    if len(clauses) > 0:
        if len(global_clauses) > 0:
            query = query.where(functools.reduce(operator.and_, clauses),
                                functools.reduce(operator.or_, global_clauses))
        else:
            query = query.where(functools.reduce(operator.and_, clauses))
    if len(orders) > 0:
        query = query.order_by(*orders)
    print(query)
    count = query.count()
    query = query.paginate(filter["paginate"]['page_number'], filter["paginate"]['number_of_rows'])
    data = getdatarows(query)
    if "select" in filter:
        rows = list()
        for i in range(len(data)):
            row = {}
            for ind, key in enumerate(filter["select"]):
                if key in data[i] and key in fields:
                    row[key] = data[i][key]
            rows.append(row)
        data = rows
    if onlydata:
        return data
    return {"data": data, "totalRecords": count}


@log_args_and_response
def get_pack_module(pack_status, batch_id=None, batch_status=None, facility_dist_id=None, user_id=None):
    if pack_status in [settings.DONE_PACK_STATUS, settings.DELETED_PACK_STATUS, settings.PROCESSED_MANUALLY_PACK_STATUS]:
        return settings.PACK_MODULE_PACK_MASTER
    elif pack_status in settings.MANUAL_FILLING_STATUS and user_id:
        return settings.PACK_MODULE_MANUAL_FILLING
    elif batch_id and batch_status in settings.PACK_PRE_BATCH_STATUS and not user_id:
        return settings.PACK_MODULE_PACK_PRE
    elif batch_id and batch_status == settings.BATCH_IMPORTED and not user_id and pack_status in [
        settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS]:
        return settings.PACK_MODULE_PACK_QUEUE
    elif not user_id and not batch_id and pack_status == settings.PENDING_PACK_STATUS:
        return settings.PACK_MODULE_BATCH_DISTRIBUTION
    else:
        return None
