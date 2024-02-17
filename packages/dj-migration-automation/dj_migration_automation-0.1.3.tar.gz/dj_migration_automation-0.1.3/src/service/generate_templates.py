# -*- coding: utf-8 -*-
"""
    src.generate_templates
    ~~~~~~~~~~~~~~~~

    This module takes care of all the template related apis.
    It has helper function to fetch the template metadata based
    on date range, get the template details for the given patient_id,
    stores the template details for the given patient_id,
    generates the column number based on the rx timing, deletes the template
    data, checks if the template already exists for the given patient_id and
    it has been not modified yet.


    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""

import datetime
import json
import logging
import math
from collections import defaultdict, OrderedDict
from pprint import pprint
from typing import Optional, List, Dict, Any

import pandas as pd
from peewee import InternalError, IntegrityError, DoesNotExist, DataError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import convert_time, fn_shorten_drugname, get_current_date_time, log_args_and_response
from dosepack.validation.validate import validate
from settings import SEPARATOR
from src import constants
from src.constants import MAX_TEMPLATE_SPLIT_COUNT_THRESHOLD
from src.dao.company_setting_dao import db_get_template_split_settings_dao
from src.dao.drug_dao import db_get_drugs_volume, create_store_separate_drug_dao, delete_separate_drug_dao
from src.dao.ext_file_dao import update_couch_db_pending_template_count
from src.dao.ext_change_rx_couchdb_dao import update_notifications_couch_db_green_status
from src.dao.file_dao import db_verify_file_id_dao
from src.dao.patient_dao import get_patient_data_dao
from src.dao.pack_dao import get_patient_details_for_patient_id
from src.dao.template_dao import db_get_rx_info, db_get_pending_templates, db_get_pending_templates_data, \
    db_get_file_patient, db_get_by_template, db_get_saved_template, db_save_template, db_get_template_drug_details, \
    db_verify_template_list_dao, db_update_pending_progress_templates_by_status, \
    db_delete_templates_by_patient_file_ids, db_delete_temp_slot_by_patient_file_ids, \
    db_get_file_id_from_template_ids_dao, db_get_template_by_rolled_back_file_ids, db_update_rollback_files, \
    db_get_base_pack_count_by_admin_duration, get_template_canisters, get_store_separate_drugs_dao, \
    get_rollback_templates_dao, get_take_away_template_by_patient_dao, template_get_status_dao, get_template_id_dao, \
    is_other_template_pending_dao, get_template_file_id_dao, update_modification_status_dao, \
    db_get_ext_linked_data_change_rx, get_template_flags
from src.exceptions import UnsplittableTemplateException, RedisKeyException, RedisConnectionException, TemplateException
from src.model.model_celery_task_meta import CeleryTaskmeta
from src.redis_controller import update_pending_template_data_in_redisdb, fetch_template_records_from_redisdb
from src.service.misc import real_time_db_timestamp_trigger

# get the logger for the pack from global configuration file logging.json

logger = logging.getLogger("root")


@validate(required_fields=["patient_id", "company_id", "file_id"])
def get_template_data(dict_patient_info):
    """ Takes the patient_id and gets all the template data for the given patient_id.

        Args:
            dict_patient_info (dict): The dict containing patient id, system id

        Returns:
            List : All the template records for the given patient_id and system id

        Examples:
            >>> get_template_data({"patient_id": 7, "system_id": 2, "file_id": 2})
            []

    """
    patient_id = dict_patient_info["patient_id"]
    company_id = int(dict_patient_info["company_id"])
    file_id = int(dict_patient_info["file_id"])
    template_data = []

    valid_file = db_verify_file_id_dao(file_id=file_id, company_id=company_id)
    # checking whether file_id and system_id are mapped for security check
    if not valid_file:
        return error(1016)

    status = template_get_status_dao(file_id=file_id, patient_id=patient_id)

    try:
        if not status:
            for record in db_get_saved_template(patient_id=patient_id, file_id=file_id,
                                                                company_id=company_id):
                record["quantity"] = float(record["quantity"])
                admin_time = str(record["hoa_time"])
                admin_time = datetime.datetime.strptime(admin_time, "%H:%M:%S").strftime("%I:%M %p")
                record["display_time"] = admin_time
                record["short_drug_name"] = fn_shorten_drugname(record["drug_name"])
                record["file_id"] = file_id
                template_data.append(record)
        else:
            template_column_dict = defaultdict(set)
            unique_hoa_time = list()
            column_number = 0
            duplicate_records = set()
            for record in db_get_template_drug_details(patient_id, file_id):
                _tapered_record = str(record["hoa_time"]) + settings.SEPARATOR + str(record["patient_rx_id"])
                if _tapered_record not in duplicate_records:
                    record["quantity"] = float(record["quantity"])
                    column_number = get_template_column(record["hoa_time"])
                    template_column_dict[column_number].add(record["hoa_time"])
                    admin_time = str(record["hoa_time"])
                    admin_time = datetime.datetime.strptime(admin_time, "%H:%M:%S").strftime("%I:%M %p")
                    record["display_time"] = admin_time
                    modified_time = datetime.datetime.utcnow().__str__()
                    record["modified_time"] = modified_time
                    record["short_drug_name"] = fn_shorten_drugname(record["drug_name"])
                    record["file_id"] = file_id
                    template_data.append(record)
                    duplicate_records.add(_tapered_record)

            column_tracker = {}
            for key, value in template_column_dict.items():
                template_column_dict[key] = list(sorted(value))
                for index, item in enumerate(template_column_dict[key]):
                    column_tracker[str(item)] = key + index

            for item in template_data:
                item["column_number"] = column_tracker[str(item["hoa_time"])]

    except StopIteration as e:
        logger.error(e, exc_info=True)
        return error(1004)

    template_data = sorted(template_data, key=lambda x: x["drug_name"])
    return create_response(template_data)


@log_args_and_response
def prepare_template_data_for_df(template, drug_dimensions, store_separate_drugs):
    for item in template:
        fndc_txr = item['formatted_ndc'], item['txr']
        item['mean_volume'] = None
        if fndc_txr in drug_dimensions:
            volume = float(drug_dimensions[fndc_txr]['approx_volume'])

        else:
            volume = 532.57
            item['mean_volume'] = 1
        item['approx_pill_volume'] = volume
        item['store_separate'] = fndc_txr in store_separate_drugs  # sets bool flag
        item['total_volume'] = volume * item['quantity'] if volume is not None else volume
    return template


def get_default_cell():
    """ default cell in df to split template """
    # (index in list, total_pills_volume, pill quantity, fndc_txr, is_tapered, same_drug_auto_split, mean volume,
    # drug_split_data)
    return None, .0, .0, None, None, False, None, {}


def create_df_from_template(template):
    column_numbers = list()
    rx_numbers = list()
    df_dict = defaultdict(dict)
    column_time_map = dict()
    for item in template:
        column_time_map[item['column_number']] = item['hoa_time']
        if item['column_number'] not in column_numbers:
            column_numbers.append(item['column_number'])
        if item['pharmacy_rx_no'] not in rx_numbers:
            rx_numbers.append(item['pharmacy_rx_no'])
        df_dict[item['pharmacy_rx_no']][item['column_number']] = item['total_volume']

    df = pd.DataFrame(df_dict, columns=column_numbers, index=rx_numbers, )
    for index, item in enumerate(template):
        rx_no, col = item['pharmacy_rx_no'], item['column_number']
        df.loc[rx_no][col] = (index,
                              df_dict[rx_no][col],
                              item['quantity'],
                              '{}#{}'.format(item['formatted_ndc'], item['txr'] or ''),
                              item['is_tapered'],
                              False,
                              item['mean_volume'],
                              {'color': item['color'],
                               'shape': item['drug_shape']})
    # replace math.isnan with default values
    df = df.applymap(lambda x: get_default_cell() if isinstance(x, float) and math.isnan(x) else x)
    return df, column_time_map


def get_pill_qty_list(qty, deduction=1):
    qty_list = []
    while qty > 0:
        if qty >= deduction:
            qty -= deduction
            qty_list.append(deduction)
        else:
            qty_list.append(qty)
            qty -= deduction  # to make sure while loop terminates
    return sorted(qty_list)  # sort to get half pill first


def insert_split_cols_in_df(split_cols, df, column_index, column_resolution=101):
    """
    This is helper function to insert new columns split from a column.
    This makes sure it inserts column with float column index.
    So that columns can be ordered according to column index
    which will arrange columns to its original positions.

    Column resolution is used to make sure order is maintain in which order columns were split
    In below list value before decimal point is original column number
    and value after decimal point is split column index
    [1.1, 1.1, 1.11, 1.12, 1.13, 1.14, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
    On sorting 1.2 goes to the very end. we want it just after 1.1
    The reason of this is we can have only 10 split column if we start from 1
    To solve this we column resolution which is defaults to 101,
    gives 100 columns to insert in an order

    >>> sorted([float('{}.{}'.format(1, 101 + i)) for i in range(0, 15)])
    [1.101, 1.102, 1.103, 1.104, 1.105, 1.106, 1.107, 1.108, 1.109, 1.11, 1.111, 1.112, 1.113, 1.114, 1.115]
    """
    del df[column_index]
    for index, column in enumerate(split_cols):
        index = float('{}.{}'.format(column_index, index + column_resolution))
        df[index] = column


def empty_col_generator(column):
    """ returns list with default cells of length of given template column """
    return list((get_default_cell() for _ in range(len(column))))  # generates empty column


def pack_no_by_column_no(column_number, pack_col=settings.PACK_COL):
    """ Returns which pack number in which column number belongs """
    return int((column_number - 1) / pack_col) + 1


def split_column_by_store_separate_drug(column, separate_drugs):
    outs = list()
    outs.append(list(column))  # add original column
    outs2 = empty_col_generator(column)
    for index, item in enumerate(column):
        # for every rx that needs separate column, add new column, remove from old column
        if item[3] and item[3] in separate_drugs:  # if rx needs to be split into another column
            outs[0][index] = get_default_cell()  # remove from original column
            outs2[index] = item
    outs.append(outs2)
    return outs


@log_args_and_response
def split_separate_drugs(template, store_separate_drugs):
    """
    splits every rx into new column which needs to be stored separate
    :param template: list
    :param store_separate_drugs: set
    :return: tuple
    """
    split_column_times = set()
    try:
        df, col_time_map = create_df_from_template(template)
        for col in df.columns:
            split_required = any(item[3] in store_separate_drugs for item in df[col])
            if split_required:
                split_cols = split_column_by_store_separate_drug(df[col], store_separate_drugs)
                split_column_times.add(col_time_map[col])
                insert_split_cols_in_df(split_cols, df, col)
        df = df[sorted(df.columns)]
        new_column_numbers = [index + 1 for index, item in enumerate(df.columns)]
        df.columns = new_column_numbers
        new_template = get_template_from_df(df, template)
        return new_template, df, split_column_times
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def adjust_columns(cols, key, threshold):
    """
    Adjusts template columns to make split columns balanced.
    :param cols: list of columns
    :param key: key to access from element to compare with threshold
    :param threshold: threshold value (should not exceed for any column)
    :return:
    """
    adjust_error = False
    new_cols = list(list(get_default_cell() for _ in col) for col in cols)
    cols_threshold = [.0 for _ in new_cols]
    cols_indexes = [0 for _ in new_cols]
    all_elements = list()
    elements_to_exclude = set()  # maintaining element indexes which should not be adjusted
    elements_template_index_seen = set()

    for col_index, col in enumerate(cols):  # flatten lists and create a single list
        for row_index, element in enumerate(col):
            if element[0] is not None:
                all_elements.append((col_index, row_index, element))
                if element[0] not in elements_template_index_seen:
                    elements_template_index_seen.add(element[0])
                else:
                    elements_to_exclude.add(element[0])
    for col_index, row_index, element in sorted(all_elements, key=lambda x: x[2][key], reverse=True):
        if element[0] not in elements_to_exclude:
            minimum = min(cols_threshold)
            col_to_insert = cols_threshold.index(minimum)
        else:
            # if a rx was split into two columns, keep those two elements as it is
            # if we put two such element in one column, this will show up wrong on front end
            col_to_insert = col_index
        new_cols[col_to_insert][cols_indexes[col_to_insert]] = element
        cols_threshold[col_to_insert] += element[key]
        cols_indexes[col_to_insert] += 1
        if cols_threshold[col_to_insert] > threshold:
            adjust_error = True
            break
    if adjust_error:  # if at any point we find threshold criteria is exceeded, we return original cols
        return cols
    return new_cols


def split_column_by_count(column, threshold):
    """
    Returns list of series for given series (column of template)
    :param column:
    :param threshold:
    :return:
    """
    current_threshold = 0
    outs = list()
    out1 = list(get_default_cell() for _ in range(len(column)))
    out2 = list(get_default_cell() for _ in range(len(column)))
    for index, item in enumerate(column):
        if type(item) is tuple and item[0] is not None:
            if current_threshold + item[2] <= threshold:  # all pill of a rx can live in a slot
                out1[index] = item
                current_threshold += item[2]
            elif item[2] <= threshold:
                out2[index] = item
            else:
                # allowing taper split: prod issue: count 12 of tapered: > 10 in single slot: allowed split
                # if item[4]:  # if taper drug and total volume of drug exceeds threshold
                #     raise UnsplittableTemplateException('Can not split taper drug with count {} > threshold {}'
                #                                         ', drug {}'.format(item[2], threshold, item[3]),
                #                                         taper_error=True)
                col1_vol, col1_qty = .0, .0  # for this specific rx
                col2_vol, col2_qty = .0, .0  # for this specific rx
                one_pill_vol = (item[1] / item[2])
                for pill_qty in get_pill_qty_list(item[2]):
                    pill_vol = (one_pill_vol * pill_qty)  # pill_qty can be between (0, 1], e.g. 150 mm^3 * 0.5 qty
                    pill_qty = float(pill_qty)
                    if current_threshold + pill_qty <= threshold:
                        col1_vol += pill_vol
                        col1_qty += pill_qty
                        current_threshold += pill_qty
                    else:
                        col2_vol += pill_vol
                        col2_qty += pill_qty
                if col1_qty:
                    out1[index] = (item[0], col1_vol, col1_qty, item[3], item[4])
                out2[index] = (item[0], col2_vol, col2_qty, item[3], item[4])
                # print('Qty', col1_vol, col1_qty, col2_vol, col2_qty)

    outs.append(out1)
    if sum(item[2] for item in out2) > threshold:
        # pprint('recursion')
        pprint(outs)
        outs.extend(split_column_by_count(out2, threshold))  # Recurse if still crosses threshold criteria
    else:
        outs.append(out2)
    outs = adjust_columns(outs, 2, threshold)
    return outs


def adjust_column_by_color_shape(columns, col_info_dict, total_pills, number_of_columns,
                                 volume_threshold, slot_max_pills_threshold, splitted_rx, min_vol, template_id):
    try:
        print(col_info_dict)
        for base_index, base_col in enumerate(columns):
            base_color_shape_rx = col_info_dict[base_index]['color_shape_rx']
            # color_rx = col_info_dict[base_index]['color_rx']
            # shape_rx = col_info_dict[base_index]['shape_rx']
            for individual_rx_index, rx_details in enumerate(base_col):

                if rx_details[0] is not None and rx_details[0] not in splitted_rx and \
                        len(col_info_dict[base_index]['color_shape_rx'][
                                (rx_details[7]['color'], rx_details[7]['shape'])]) > 1 \
                        and rx_details[7]['color'] and rx_details[7]['shape']:
                    color_shape = (rx_details[7]['color'], rx_details[7]['shape'])
                    for index, col in enumerate(columns):
                        if base_index != index:
                            color_shape_rx = col_info_dict[index]['color_shape_rx']
                            if color_shape not in color_shape_rx:
                                logger.info(
                                    'For template_id: {} base_index {} in columns {} with base_color_shape {} : '
                                    'Can transfer to index {} for color_shape {}'
                                        .format(template_id, base_index, columns, base_color_shape_rx, index,
                                                color_shape))
                                # checking only for whole rx(priority)
                                # ignore split rx
                                logger.info('condition match for color shape: {} when col_info_dict: {}'
                                            .format(color_shape, col_info_dict))
                                rx_total_volume = rx_details[1]
                                rx_total_pills = rx_details[2]
                                if col_info_dict[index][
                                    'total_volume'] + rx_total_volume < volume_threshold and \
                                        col_info_dict[index][
                                            'total_pills'] + rx_total_pills <= slot_max_pills_threshold:

                                    logger.info('volume and count match for color shape: {} when col_info_dict: {}'
                                                .format(color_shape, col_info_dict))
                                    # reducing rx from column
                                    count_pills_can_be_added = col_info_dict[base_index][
                                                                   'count_pills_can_be_added'] + \
                                                               rx_total_pills
                                    volume_pills_can_be_added = col_info_dict[base_index][
                                                                    'volume_pills_can_be_added'] + \
                                                                rx_total_volume
                                    total_pills = col_info_dict[base_index]['total_pills'] - rx_total_pills
                                    total_volume = col_info_dict[base_index]['total_volume'] - rx_total_volume
                                    rx_list = col_info_dict[base_index]['rx_list']
                                    rx_list.pop(rx_details[0], None)
                                    # color_shape_rx = col_info_dict[base_index]['color_shape_rx']
                                    color_shape_rx_list = base_color_shape_rx[color_shape]

                                    if rx_details[0] in color_shape_rx_list:
                                        color_shape_rx_list.remove(rx_details[0])
                                    base_color_shape_rx[color_shape] = color_shape_rx_list
                                    # color_shape_rx[color_shape].pop([rx_details[0]], None)

                                    col_info_dict[base_index] = {'total_volume': total_volume,
                                                                 'total_pills': total_pills,
                                                                 'count_pills_can_be_added': count_pills_can_be_added,
                                                                 'volume_pills_can_be_added': volume_pills_can_be_added,
                                                                 'rx_list': rx_list,
                                                                 'color_shape_rx': base_color_shape_rx}

                                    # adding rx in column
                                    count_pills_can_be_added = col_info_dict[index][
                                                                   'count_pills_can_be_added'] - rx_total_pills
                                    volume_pills_can_be_added = col_info_dict[index][
                                                                    'volume_pills_can_be_added'] - rx_total_volume
                                    total_pills = col_info_dict[index][
                                                      'total_pills'] + rx_total_pills
                                    total_volume = col_info_dict[index][
                                                       'total_volume'] + rx_total_volume
                                    rx_list = col_info_dict[index]['rx_list']
                                    rx_list[rx_details[0]] = rx_total_pills
                                    # color_shape_rx = col_info_dict[index]['color_shape_rx']
                                    color_shape_rx[color_shape] = [rx_details[0]]

                                    col_info_dict[index] = {
                                        'total_volume': total_volume,
                                        'total_pills': total_pills,
                                        'count_pills_can_be_added': count_pills_can_be_added,
                                        'volume_pills_can_be_added': volume_pills_can_be_added,
                                        'rx_list': rx_list,
                                        'color_shape_rx': color_shape_rx
                                    }
                                    for rx_index, rx_info in enumerate(columns[index]):
                                        if rx_info[0] is None:
                                            columns[index][rx_index] = rx_details
                                            break

                                    if rx_details in columns[base_index]:
                                        columns[base_index].remove(rx_details)
                                        columns[base_index].append(
                                            (None, 0.0, 0.0, None, None, False, None, {}))
                                        rx_details = (None, 0.0, 0.0, None, None, False, None, {})
                                    # columns = columns_copy.copy()
                                    print(columns)

        return columns
    except (InternalError, IntegrityError) as e:
        raise e


def adjust_column_by_volume_and_count(columns, total_volume_across_columns, total_pills, number_of_columns,
                                      volume_threshold, slot_max_pills_threshold, splitted_rx, min_vol, template_id):
    """
    variable context:
        pills_add_columns: set of columns in which we can add rx to achieve equal split i.e. column that contains
                           less volume and less number of pills
        adjust_pill_count: pills count that can be shifted to get equal split

        col_info_dict[index] = {
                'total_volume': total volume of pills in particular column,
                'total_pills': number of pills in particular column,
                'count_pills_can_be_added': number of pills that can be added in column,
                'volume_pills_can_be_added': volume of pills that cab be accomodated,
                'rx_list': available_rx
            }

    adjust logic:
        1. Find out the columns in which we can shift the rx.
        2. Check if a particular rx is already split across the columns. If yes then check if it's quantity can be
           adjusted and can get equal split in context of volume and rx.
        3. Even after split rx adjustment we don't have balance in columns i.e. quantity of pill in two columns are
           10 and 1 respectively then we try to balance it in 5-6 then we shift whole rx in another column.
        4. We do not split any new rx while balancing if whole rx can be shifted in new column then it's shifted.

    :param columns:
    :param total_volume_across_columns:
    :param total_pills:
    :param number_of_columns:
    :param volume_threshold:
    :param slot_max_pills_threshold:
    :param splitted_rx:
    :return:
    """
    logger.info("in adjust_column_by_volume_and_count")
    pprint(columns)
    max_count = slot_max_pills_threshold
    # pills count that can be shifted to get equal split
    adjust_pill_count = math.floor((total_pills / number_of_columns))
    pills_add_columns = dict()
    col_info_dict = dict()
    # build col_info_dict and find pills_add_columns
    for index, col in enumerate(columns):
        individual_total_volume = sum(item[1] for item in col)
        individual_total_pills = sum(item[2] for item in col)
        if individual_total_volume + min_vol < volume_threshold and individual_total_pills < adjust_pill_count:
            pills_add_columns[index] = True
        available_rx = dict()
        color_shape_rx = defaultdict(list)
        color_rx = defaultdict(list)
        shape_rx = defaultdict(list)
        for row_index, col in enumerate(col):
            if col[0] is not None:
                available_rx[col[0]] = col[2]
                color_shape_rx[col[7].get('color', None), col[7].get('shape', None)].append(col[0])
                # add below fields in col_info_dict if required
                color_rx[col[7].get('color', None)].append(col[0])
                shape_rx[col[7].get('shape', None)].append(col[0])
        col_info_dict[index] = {
            'total_volume': individual_total_volume,
            'total_pills': individual_total_pills,
            'count_pills_can_be_added': adjust_pill_count - individual_total_pills,
            'volume_pills_can_be_added': volume_threshold - individual_total_volume,
            'rx_list': available_rx,
            'color_shape_rx': color_shape_rx
        }
    logger.info('column_volume_count_info {}'.format(col_info_dict))
    logger.info('For template_id: {} columns and col_info_dict before color_shape_adj: {} {}'
                .format(template_id, columns, col_info_dict))
    columns = adjust_column_by_color_shape(columns, col_info_dict, total_pills, number_of_columns, volume_threshold,
                                           slot_max_pills_threshold, splitted_rx, min_vol, template_id=template_id)
    logger.info('For template_id: {} columns and col_info_dict after color_shape_adj: {} {}'
                .format(template_id, columns, col_info_dict))

    # changing count threshold in adjust to be average of columns
    slot_max_pills_threshold = slot_max_pills_threshold / len(columns)

    # build col_info_dict and find pills_add_columns
    for index, col in enumerate(columns):
        individual_total_volume = sum(item[1] for item in col)
        individual_total_pills = sum(item[2] for item in col)
        if individual_total_volume + min_vol < volume_threshold and individual_total_pills < adjust_pill_count:
            pills_add_columns[index] = True
        available_rx = dict()
        color_shape_rx = defaultdict(list)
        color_rx = defaultdict(list)
        shape_rx = defaultdict(list)
        for row_index, col in enumerate(col):
            if col[0] is not None:
                available_rx[col[0]] = col[2]
                color_shape_rx[col[7].get('color', None), col[7].get('shape', None)].append(col[0])
                # add below fields in col_info_dict if required
                color_rx[col[7].get('color', None)].append(col[0])
                shape_rx[col[7].get('shape', None)].append(col[0])
        col_info_dict[index] = {
            'total_volume': individual_total_volume,
            'total_pills': individual_total_pills,
            'count_pills_can_be_added': adjust_pill_count - individual_total_pills,
            'volume_pills_can_be_added': volume_threshold - individual_total_volume,
            'rx_list': available_rx,
            'color_shape_rx': color_shape_rx
        }
    logger.info('column_volume_count_info {}'.format(col_info_dict))
    logger.info('pills_adjust_required_columns {}'.format(pills_add_columns))
    columns_copy = columns.copy()

    if not pills_add_columns:
        logger.info("For template_id: {} return columns from col-vol split with no adjust {}"
                    .format(template_id, columns))
        return columns

    for pill_add_col_index, pills_add_col_status in pills_add_columns.items():
        # adjusting similar rx split
        for col in columns_copy[pill_add_col_index]:
            for key, value in col_info_dict.items():
                if col[0] is not None and col[0] in value['rx_list'].keys() and key not in pills_add_columns:
                    logger.info('similar rx found for template_id {} at column {} for column {}'
                                .format(template_id, key, pill_add_col_index))
                    one_pill_vol = col[1] / col[2]
                    vol_count = math.floor(
                        col_info_dict[pill_add_col_index]['volume_pills_can_be_added'] / one_pill_vol)
                    pill_count = min(min(value['rx_list'][col[0]], value['total_pills'] -
                                         adjust_pill_count),
                                     col_info_dict[pill_add_col_index]['count_pills_can_be_added'])
                    if value['total_pills'] % 1 == 0:
                        pill_count = math.floor(pill_count)
                    pill_shift_count = min(vol_count, pill_count)
                    logger.info("Shifting {} number of pills for min_vol {} and min_pill_c {} for template_id: "
                                .format(pill_shift_count, vol_count, pill_count, template_id))
                    if pill_shift_count > 0:
                        color_shape_rx = col_info_dict[pill_add_col_index]['color_shape_rx']
                        count_pills_can_be_added = col_info_dict[pill_add_col_index]['count_pills_can_be_added'] - \
                                                   pill_shift_count
                        volume_pills_can_be_added = col_info_dict[pill_add_col_index]['volume_pills_can_be_added'] - \
                                                    (one_pill_vol * pill_shift_count)
                        total_pills = col_info_dict[pill_add_col_index]['total_pills'] + pill_shift_count
                        total_volume = col_info_dict[pill_add_col_index]['total_volume'] + (
                                one_pill_vol * pill_shift_count)
                        rx_list = value['rx_list']
                        count = rx_list[col[0]] + pill_shift_count
                        rx_list[col[0]] = count
                        col_info_dict[pill_add_col_index] = {'total_volume': total_volume, 'total_pills': total_pills,
                                                             'count_pills_can_be_added': count_pills_can_be_added,
                                                             'volume_pills_can_be_added': volume_pills_can_be_added,
                                                             'rx_list': rx_list,
                                                             'color_shape_rx': color_shape_rx}
                        if count_pills_can_be_added == 0 or volume_pills_can_be_added < min_vol:
                            pills_add_columns[pill_add_col_index] = False
                        for original_index, original_column in enumerate(columns):
                            if original_index == pill_add_col_index:
                                for original_row_index, original_row in enumerate(original_column):
                                    if original_row[0] == col[0]:
                                        row_1 = original_row[1] + (one_pill_vol * pill_shift_count)
                                        row_2 = original_row[2] + pill_shift_count
                                        row_3 = original_row[3]
                                        row_4 = original_row[4]
                                        row_5 = original_row[5]
                                        row_6 = original_row[6]
                                        row_7 = original_row[7]
                                        re_tuple = (col[0], row_1, row_2, row_3, row_4, row_5, row_6, row_7)
                                        print(re_tuple)
                                        columns[original_index][original_row_index] = re_tuple
                            elif original_index == key:
                                color_shape_rx = col_info_dict[key]['color_shape_rx']
                                count_pills_can_be_added = col_info_dict[key]['count_pills_can_be_added'] + \
                                                           pill_shift_count
                                volume_pills_can_be_added = col_info_dict[key]['volume_pills_can_be_added'] + \
                                                            (one_pill_vol * pill_shift_count)
                                total_pills = col_info_dict[key]['total_pills'] - pill_shift_count
                                total_volume = col_info_dict[key]['total_volume'] - (
                                        one_pill_vol * pill_shift_count)
                                rx_list = col_info_dict[key]['rx_list']
                                count = rx_list[col[0]] - pill_shift_count
                                rx_list[col[0]] = count
                                col_info_dict[key] = {'total_volume': total_volume, 'total_pills': total_pills,
                                                      'count_pills_can_be_added': count_pills_can_be_added,
                                                      'volume_pills_can_be_added': volume_pills_can_be_added,
                                                      'rx_list': rx_list,
                                                      'color_shape_rx': color_shape_rx}
                                for original_row_index, original_row in enumerate(original_column):
                                    if original_row[0] == col[0]:
                                        row_1 = original_row[1] - (one_pill_vol * pill_shift_count)
                                        row_2 = original_row[2] - pill_shift_count
                                        row_3 = original_row[3]
                                        row_4 = original_row[4]
                                        row_5 = original_row[5]
                                        row_6 = original_row[6]
                                        row_7 = original_row[7]
                                        re_tuple = (col[0], row_1, row_2, row_3, row_4, row_5, row_6, row_7)
                                        print(re_tuple)
                                        columns[original_index][original_row_index] = re_tuple
                    columns_copy = columns.copy()
                active_column = sum([int(x) for x in pills_add_columns.values()])
                if not active_column:
                    logger.info("return columns from col-vol split {}".format(columns))
                    return columns

    if pills_add_columns:
        # adjusting through whole rx shift
        logger.info("searching for different rxs")
        for pill_add_col_index, pills_add_col_status in pills_add_columns.items():
            print('initial')
            print(pill_add_col_index)
            for col_index, col in enumerate(columns_copy):
                if not pills_add_col_status:
                    break
                active_column = sum([int(x) for x in pills_add_columns.values()])
                if len(col) > 1 and active_column and col_index not in pills_add_columns.keys():
                    print(col)
                    for rx_details in sorted(col, key=lambda x: x[1], reverse=True):
                        if rx_details[0] is not None and rx_details[0] not in splitted_rx:
                            color_shape = rx_details[7]['color'], rx_details[7]['shape']
                            rx_total_volume = rx_details[1]
                            rx_total_pills = rx_details[2]
                            # TODO: comment condition and uncomment below code for color shape adjust
                            if col_info_dict[pill_add_col_index][
                                'total_volume'] + rx_total_volume < volume_threshold and \
                                    col_info_dict[pill_add_col_index][
                                        'total_pills'] + rx_total_pills <= slot_max_pills_threshold and \
                                    color_shape not in col_info_dict[pill_add_col_index]['color_shape_rx']:
                                color_shape_rx = col_info_dict[col_index]['color_shape_rx']
                                color_shape_rx_list = col_info_dict[col_index]['color_shape_rx'][color_shape]
                                color_shape_rx_list.remove(rx_details[0])
                                if color_shape_rx_list:
                                    color_shape_rx[color_shape] = color_shape_rx_list
                                else:
                                    color_shape_rx.pop(color_shape, None)

                                logger.info('adjusting template_id: {} whole_rx:  {} color_shape in for columns: {} and'
                                            ' col_info_dict {} '.format(
                                    template_id, rx_details[0], columns, col_info_dict))
                                # reducing rx from column
                                count_pills_can_be_added = col_info_dict[col_index]['count_pills_can_be_added'] + \
                                                           rx_total_pills
                                volume_pills_can_be_added = col_info_dict[col_index]['volume_pills_can_be_added'] + \
                                                            rx_total_volume
                                total_pills = col_info_dict[col_index]['total_pills'] - rx_total_pills
                                total_volume = col_info_dict[col_index]['total_volume'] - rx_total_volume
                                rx_list = col_info_dict[col_index]['rx_list']
                                rx_list.pop(rx_details[0], None)

                                col_info_dict[col_index] = {'total_volume': total_volume, 'total_pills': total_pills,
                                                            'count_pills_can_be_added': count_pills_can_be_added,
                                                            'volume_pills_can_be_added': volume_pills_can_be_added,
                                                            'rx_list': rx_list,
                                                            'color_shape_rx': color_shape_rx}

                                # adding rx in column
                                count_pills_can_be_added = col_info_dict[pill_add_col_index][
                                                               'count_pills_can_be_added'] - rx_total_pills
                                volume_pills_can_be_added = col_info_dict[pill_add_col_index][
                                                                'volume_pills_can_be_added'] - rx_total_volume
                                total_pills = col_info_dict[pill_add_col_index]['total_pills'] + rx_total_pills
                                total_volume = col_info_dict[pill_add_col_index]['total_volume'] + rx_total_volume
                                rx_list = col_info_dict[pill_add_col_index]['rx_list']
                                rx_list[rx_details[0]] = rx_total_pills
                                color_shape_rx = col_info_dict[pill_add_col_index]['color_shape_rx']
                                color_shape_rx[color_shape] = [rx_details[0]]

                                col_info_dict[pill_add_col_index] = {
                                    'total_volume': total_volume,
                                    'total_pills': total_pills,
                                    'count_pills_can_be_added': count_pills_can_be_added,
                                    'volume_pills_can_be_added': volume_pills_can_be_added,
                                    'rx_list': rx_list,
                                    'color_shape_rx': color_shape_rx
                                }
                                for index, rx in enumerate(columns_copy[pill_add_col_index]):
                                    if rx[0] is None:
                                        columns_copy[pill_add_col_index][index] = rx_details
                                        break
                                columns_copy[col_index].remove(rx_details)
                                columns_copy[col_index].append((None, 0.0, 0.0, None, None, False, None, {}))
                                columns = columns_copy.copy()
                                logger.info('after adjust: columns {} and col_vol_info_dict: {}'.format(columns,
                                                                                                        col_info_dict))

                                if volume_pills_can_be_added <= min_vol or count_pills_can_be_added <= 0:
                                    print(pills_add_columns)
                                    print(pill_add_col_index)
                                    pills_add_columns[pill_add_col_index] = False
                                    break

            active_column = sum([int(x) for x in pills_add_columns.values()])
            if not active_column:
                logger.info("return columns from col-vol split {}".format(columns))
                return columns
    logger.info("return columns from col-vol split {}".format(columns))
    return columns


def split_column_by_volume(column, threshold, slot_max_pills_threshold, split_rx):
    """
    Returns two series for given series (column of template)
    :param column:
    :param threshold:
    :param slot_max_pills_threshold:
    :param split_rx: rx that split across the cols
    :return:
    """
    current_threshold = 0
    slot_pill_count = 0
    outs = list()
    out1 = list(get_default_cell() for _ in range(len(column)))
    out2 = list(get_default_cell() for _ in range(len(column)))
    for index, item in enumerate(column):
        if type(item) is tuple and item[0] is not None:
            one_pill_vol = (item[1] / item[2])
            if one_pill_vol > threshold:
                # This is required otherwise recursion will go infinite
                raise UnsplittableTemplateException('threshold is very small compared to one pill volume, '
                                                    'cannot handle such scenario. drug: {}'.format(item[3]))
            # if current_threshold + item[1] <= threshold:  # all pill of rx can live in a slot
            if current_threshold + item[1] <= threshold and slot_pill_count + item[
                2] <= slot_max_pills_threshold:  # all pill of rx can live in a slot
                out1[index] = item
                current_threshold += item[1]
                slot_pill_count += item[2]
            # else:  # This is commented, can be used if split only all pills
            #     out2[index] = item
            # elif item[1] <= threshold:
            elif item[1] <= threshold and item[2] <= slot_max_pills_threshold:
                out2[index] = item
            else:
                # allowing taper split: prod issue: count 12 of tapered: > 10 in single slot: allowed split
                # if item[4]:  # if taper drug and total volume of drug exceeds threshold
                #     raise UnsplittableTemplateException('Can not split taper drug with pill volume > threshold'
                #                                         ', drug {}'.format(item[3]), taper_error=True)
                col1_vol, col1_qty = .0, .0  # for this specific rx
                col2_vol, col2_qty = .0, .0  # for this specific rx
                split_rx.add(item[0])
                for pill_qty in get_pill_qty_list(item[2]):
                    pill_vol = (one_pill_vol * pill_qty)  # pill_qty can be between (0, 1], e.g. 150 mm^3 * 0.5 qty
                    pill_qty = float(pill_qty)
                    if (current_threshold + pill_vol <= threshold) and (
                            slot_pill_count + pill_qty <= slot_max_pills_threshold):
                        # if (current_threshold + pill_vol <= threshold):
                        col1_vol += pill_vol
                        col1_qty += pill_qty
                        current_threshold += pill_vol
                        slot_pill_count += pill_qty
                    else:
                        col2_vol += pill_vol
                        col2_qty += pill_qty
                if col1_qty:
                    if item[0] in split_rx:
                        out1[index] = (item[0], col1_vol, col1_qty, item[3], item[4], True, item[6], item[7])
                    else:
                        out1[index] = (item[0], col1_vol, col1_qty, item[3], item[4], False, item[6], item[7])

                if item[0] in split_rx:
                    out2[index] = (item[0], col2_vol, col2_qty, item[3], item[4], True, item[6], item[7])
                else:
                    out2[index] = (item[0], col2_vol, col2_qty, item[3], item[4], False, item[6], item[7])
                # print('Qty', col1_vol, col1_qty, col2_vol, col2_qty)

    outs.append(out1)
    # if sum(item[1] for item in out2) > threshold:
    if sum(item[1] for item in out2) > threshold or sum(item[2] for item in out2) > slot_max_pills_threshold:
        # pprint('recursion')
        pprint(outs)
        outs.extend(split_column_by_volume(out2, threshold, slot_max_pills_threshold,
                                           split_rx))  # Recurse if still crosses threshold criteria
    else:
        outs.append(out2)
    logger.info('before adjust {}'.format(outs))
    # outs = adjust_columns(outs, 1, threshold)
    return outs


@log_args_and_response
def split_template_by_volume(template, customization_flag, seperate_flag, is_true_unit, drug_dimensions, split_config, pack_type, template_id, is_bubble=False):
    """
    @param is_bubble:
    @param template:
    @param drug_dimensions:
    @param split_config:
    @param template_id: For logging purpose
    @param customization_flag
    @param seperate_flag
    @param is_true_unit
    @param pack_type
    @return: Verification_required_count : param returns int value if > 0 then pharmatech verification is required.

    max_threshold: If slot total vol > max_threshold, split slot drugs.
    """
    new_template = template
    df = None
    volume_split_column_times = set()
    count_split_column_times = set()
    verification_required_count = 0
    is_customized = False
    dummy_template = None
    if not is_bubble:
        print(len(template), template)
        print(len(drug_dimensions), drug_dimensions)
        threshold = (
                        settings.SLOT_VOLUME if pack_type == constants.MULTI_DOSE_PER_PACK else settings.UNIT_DOSAGE_SLOT_VOLUME) * \
                    split_config['SLOT_VOLUME_THRESHOLD_MARK']
        max_threshold = (
                            settings.SLOT_VOLUME if pack_type == constants.MULTI_DOSE_PER_PACK else settings.UNIT_DOSAGE_SLOT_VOLUME) * \
                        split_config['MAX_SLOT_VOLUME_THRESHOLD_MARK']
        if pack_type == constants.UNIT_DOSE_PER_PACK:
            slot_pill_count_threshold = split_config['TEMPLATE_SPLIT_COUNT_THRESHOLD_UNIT']
        else:
            slot_pill_count_threshold = split_config['SLOT_COUNT_THRESHOLD']
        logger.info('SLOT_VOLUME_THRESHOLD: {}'.format(threshold))
        verification_required_count = 0
        volume_split_column_times = set()
        count_split_column_times = set()
        is_customized = False
        dummy_template = None

        df, col_time_map = create_df_from_template(template)
        for col in df.columns:
            if int(split_config.get('VOLUME_BASED_TEMPLATE_SPLIT', 1)):  # if volume based split is enabled
                vol_available = all(bool(item[1]) for item in df[col] if item[0] is not None)
                min_vol = min(item[1] / item[2] for item in df[col] if item[0] is not None)
                logger.info('min_vol {}'.format(min_vol))
                mean_vol_used = [item[6] for item in df[col] if item[0] is not None].count(1)
                if mean_vol_used > 0:
                    verification_required_count += 1
                if vol_available:  # check if volume available for all drug in a column
                    volume_list = [item[1] for item in df[col]]
                    quantity_list = [item[2] for item in df[col]]
                    col_volume = sum(volume_list)
                    slot_pill_count = sum(quantity_list)
                    if col_volume > max_threshold or slot_pill_count > slot_pill_count_threshold:
                        volume_split_column_times.add(col_time_map[col])
                        split_rx = set()
                        split_cols = split_column_by_volume(df[col], max_threshold, slot_pill_count_threshold, split_rx)
                        logger.info('before adjust' + str(split_cols))
                        split_cols = adjust_column_by_volume_and_count(split_cols, col_volume, slot_pill_count,
                                                                       len(split_cols), max_threshold,
                                                                       slot_pill_count_threshold, split_rx, min_vol,
                                                                       template_id=template_id)

                        insert_split_cols_in_df(split_cols, df, col)
                    if max_threshold > col_volume > threshold:
                        if mean_vol_used == 0:
                            verification_required_count += 1

                elif int(split_config.get('COUNT_BASED_TEMPLATE_SPLIT', 0)):
                    verification_required_count += 1
                    # Count split will be applied only when volume split enabled
                    # and volume data not available for column
                    count_threshold = int(split_config['TEMPLATE_SPLIT_COUNT_THRESHOLD'])
                    # TEMPLATE_SPLIT_COUNT_THRESHOLD expected as count based split enabled
                    count_list = [item[2] for item in df[col]]
                    total_count = sum(count_list)
                    if total_count > count_threshold:
                        count_split_column_times.add(col_time_map[col])
                        split_cols = split_column_by_count(df[col], count_threshold)
                        insert_split_cols_in_df(split_cols, df, col)
        df = df[sorted(df.columns)]
        new_column_numbers = [index + 1 for index, item in enumerate(df.columns)]
        df.columns = new_column_numbers
        new_template = get_template_from_df(df, template)
        logger.info(
            f"in split_template_by_volume, here pack_type is {pack_type} and customization flag is {customization_flag} "
            f"seperate flag is {seperate_flag} and true unit flag is {is_true_unit} for template id {template_id}")
    # now based on pack type and given flag we will split columns
    if customization_flag:
        # below method consists customization cases for Multi, Unit and True Unit
        new_template, is_customized, dummy_template = splitting_for_packs_with_customization(new_template, is_true_unit, pack_type)
    elif (pack_type == constants.MULTI_DOSE_PER_PACK and seperate_flag) or (pack_type == constants.MULTI_DOSE_PER_PACK and is_bubble):
        # below method consists multi seperate pack per dose
        new_template, is_customized, dummy_template = multi_seperate_pack_per_dose(new_template, is_bubble)
    elif pack_type == constants.UNIT_DOSE_PER_PACK:
        # below method consists cases for unit and unit seperate pack per dose
        new_template, is_customized, dummy_template = unit_dosage_column_reassignation(new_template, seperate_flag)
    return new_template, df, volume_split_column_times, count_split_column_times, verification_required_count, is_customized, dummy_template


def get_template_from_df(df, template):
    new_template = list()
    default_cell = get_default_cell()
    for col in df.columns:
        series = df[col]
        for item in series:
            if item != default_cell:
                old_record = template[item[0]].copy()
                old_record['column_number'] = col
                old_record['quantity'] = item[2]
                old_record['pack_no'] = pack_no_by_column_no(old_record["column_number"])
                old_record['same_drug_auto_split'] = item[5]
                new_template.append(old_record)
    # print('NewTemplate', new_template)
    return new_template


@log_args_and_response
@validate(required_fields=["patient_id", "file_id", "company_id", "template_id"])
def get_split_data(dict_patient_info, max_count_threshold: Optional[int] = None,
                   default_template_info: Optional[List[Dict[str, Any]]] = None):
    """
    """
    patient_id = dict_patient_info["patient_id"]
    company_id = dict_patient_info["company_id"]
    file_id = int(dict_patient_info["file_id"])
    template_id = int(dict_patient_info["template_id"])
    pack_type = int(dict_patient_info["pack_type"])
    customization_flag = int(dict_patient_info["is_customized"])
    seperate_flag = int(dict_patient_info["is_sppd"])
    is_true_unit = int(dict_patient_info["is_true_unit"])
    is_bubble = int(dict_patient_info.get('is_bubble', False))
    template_data = []
    pack_structure_modified = bool()
    drug_canisters = defaultdict(list)
    fndc_txr_set = set()
    # pack_type = dict_patient_info.get("pack_type", constants.MULTI_DOSE_PER_PACK)

    split_config = dict()
    volume_split_error = False
    store_separate_split_error = False
    drug_count_auto_save = False
    # set of hoa time which were split
    split_times1 = set()  # split during separate drug split
    split_times2 = set()  # split during volume split
    split_times3 = set()  # split during count split
    separate_drug_list = set()
    verification_count = 0
    is_customized = False
    dummy_template = None

    try:
        unique_hoa_time = list()
        column_number = 0
        duplicate_records = set()
        modified_time = datetime.datetime.utcnow().isoformat()

        if default_template_info:
            for record in default_template_info:
                fndc_txr = record['formatted_ndc'], record['txr']
                fndc_txr_set.add(fndc_txr)
                template_data.append(record)
        else:
            for record in db_get_template_drug_details(patient_id, file_id):
                _tapered_record = str(record["hoa_time"]) + settings.SEPARATOR + str(record["patient_rx_id"])
                fndc_txr = record['formatted_ndc'], record['txr']
                fndc_txr_set.add(fndc_txr)
                if _tapered_record not in duplicate_records:
                    record["canister_list"] = drug_canisters[record["formatted_ndc"], record["txr"]]
                    record["quantity"] = float(record["quantity"])
                    # we assign the column number only when there is new hoa_time
                    if record["hoa_time"] not in unique_hoa_time:
                        column_number += 1
                        unique_hoa_time.append(record["hoa_time"])
                    record["column_number"] = column_number
                    record["pack_no"] = int((record["column_number"] - 1) / settings.PACK_COL) + 1
                    admin_time = str(record["hoa_time"])
                    admin_time = datetime.datetime.strptime(admin_time, "%H:%M:%S").strftime("%I:%M %p")
                    record["display_time"] = admin_time
                    # setting modified_time to keep data compatible with saved template,
                    # this won't be checked when template will be saved
                    # as it will be saved first time
                    record["modified_time"] = modified_time
                    record["short_drug_name"] = fn_shorten_drugname(record["drug_name"])
                    record["file_id"] = file_id
                    template_data.append(record)
                    duplicate_records.add(_tapered_record)
        split_config = db_get_template_split_settings_dao(company_id=company_id, max_count_threshold=max_count_threshold)
        split_store_separate = bool(split_config.get(constants.SPLIT_STORE_SEPARATE))
        # FUTURE: override store separate drug facility based settings
        drug_dimension_data = db_get_drugs_volume(list(fndc_txr_set))
        logger.info(f"In get_split_data, db_get_drugs_volume: {drug_dimension_data}")
        if split_store_separate:
            separate_drug_list = db_get_by_template(file_id, patient_id)

        template_data = prepare_template_data_for_df(template_data, drug_dimension_data, separate_drug_list)
        try:
            # this case consists unit and unit seperate packs
            if pack_type == constants.UNIT_DOSE_PER_PACK:
                template_data = unit_dosage_splitting(template_data, customization_flag, seperate_flag, is_true_unit, is_bubble)
            elif split_store_separate:
                template_data, df1, split_times1 = split_separate_drugs(template_data, separate_drug_list)
                logger.info('DF1 for template \n {}'.format(df1))
            else:
                split_times1 = set()
        except Exception as e:
            logger.error(e, exc_info=True)
            pass

        try:
            template_data, df2, split_times2, split_times3, verification_count, is_customized, dummy_template = split_template_by_volume(
                template_data, customization_flag, seperate_flag, is_true_unit, drug_dimension_data, split_config, pack_type, template_id=template_id,
                is_bubble=is_bubble
            )
            # volume based hoa splits and count based split
            logger.info('DF2 for template (RX on indexes are not aligned with elements) \n {}'.format(df2))

            # code block to check if every slot of pack is having drug quantity in [1.0,0.5] then to mark such packs
            # as yellow
            hoa_date_quantity_dict = dict()
            hoa_quantity_list = list()
            for each_dict in template_data:
                if each_dict['hoa_time'] not in hoa_date_quantity_dict.keys():
                    hoa_date_quantity_dict[each_dict['hoa_time']] = dict()

                for each_date in each_dict['admin_date_list']:
                    if each_date not in hoa_date_quantity_dict[each_dict['hoa_time']].keys():
                        hoa_date_quantity_dict[each_dict['hoa_time']][each_date] = 0

                    hoa_date_quantity_dict[each_dict['hoa_time']][each_date] += each_dict['quantity']

            for hoa, date in hoa_date_quantity_dict.items():
                quantity_list = list(date.values())
                hoa_quantity_list.extend(quantity_list)
            slot_drug_quantity = [quant if quant in [1.0, 0.5] else None for quant in hoa_quantity_list]

            if all(slot_drug_quantity):
                drug_count_auto_save = True

        except UnsplittableTemplateException as e:
            volume_split_error = True
            logger.error(e, exc_info=True)

    except StopIteration as e:
        logger.error(e, exc_info=True)
        raise e
        # return error(1004)
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        raise e
        # return error(1004)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
        # return error(2001)
    except Exception as e:
        print(e)

    if not customization_flag:
        template_data = sorted(template_data, key=lambda x: x["drug_name"])
    response = {
        "template_data": template_data,
        "pack_structure_modified": pack_structure_modified,
        "store_separate_split": bool(split_times1),
        "volume_split": bool(split_times2.union(split_times3)),
        "store_separate_split_hoa_times": split_times1,
        "volume_split_hoa_times": split_times2.union(split_times3),
        "count_split_hoa_times": split_times3,
        "volume_split_error": volume_split_error,
        "store_separate_split_error": store_separate_split_error,
        "split_config": split_config,
        "verification_count": verification_count,
        "drug_count_auto_save": drug_count_auto_save,
        "is_customized": is_customized,
        "dummy_template": dummy_template
    }
    return response


def get_template_distinct_column_number(template):
    return template["column_number"]


@log_args_and_response
def get_pack_requirement_by_template_column_number(template, base_pack_count_by_admin_duration) -> int:
    max_column_number = max(map(get_template_distinct_column_number, template))
    return math.ceil(max_column_number / settings.PACK_COL) * base_pack_count_by_admin_duration


@log_args_and_response
def db_update_pack_no(template_hoa_rx):
    template_hoa_rx["pack_no"] = \
        math.ceil(template_hoa_rx["column_number"] / settings.PACK_COL)


@log_args_and_response
def get_response_summary_dict(response_max_threshold):
    summary_dict: Dict[int, Any] = {}

    for template_hoa_rx in response_max_threshold['template_data']:
        if template_hoa_rx["column_number"] in summary_dict.keys():
            summary_dict[template_hoa_rx["column_number"]]["total_qty"] += template_hoa_rx["quantity"]
        else:
            sample_dict = {template_hoa_rx["column_number"]:
                               {"hoa_time": template_hoa_rx["hoa_time"],
                                "total_qty": template_hoa_rx["quantity"]
                                }
                           }
            summary_dict.update(sample_dict)

    return summary_dict


@log_args_and_response
def db_get_split_info_threshold_and_max_threshold(patient_id: int, file_id: int, company_id: int, template_id: int,
                                                  pack_type: int, is_customized, is_sppd, is_true_unit, is_bubble=False):
    extra_split_after_threshold_split: bool = False
    summary_dict: Dict[int, Any] = {}
    try:
        # Get the difference of admin duration(from Temp Slot Info based on Patient and File) divide by 7 and
        # apply ceiling value (A)
        logger.debug("Get the minimum pack requirement based on Admin Duration from Temp Slot Info...")
        base_pack_count_by_admin_duration: int = db_get_base_pack_count_by_admin_duration(patient_id=patient_id,
                                                                                          file_id=file_id)

        logger.debug("Get the Split Information based on Current Threshold configured in Company Settings...")
        response = get_split_data({'patient_id': patient_id, 'file_id': file_id,
                                   'company_id': company_id, 'template_id': template_id, 'pack_type': pack_type,
                                   'is_customized': is_customized, 'is_sppd': is_sppd, 'is_true_unit': is_true_unit,
                                   'is_bubble': is_bubble})

        # Identify the number of packs required based on column number (B)
        logger.debug("Get the minimum pack requirement based on Split Information with Current Threshold...")
        if response['template_data']:
            base_pack_count_by_template = \
                get_pack_requirement_by_template_column_number(template=response['template_data'],
                                                               base_pack_count_by_admin_duration=
                                                               base_pack_count_by_admin_duration)

        logger.debug("Compare Minimum pack requirement based on Admin Duration with Minimum pack requirement based "
                     "on Split Information with Current Threshold...")

        # If A != B Then Get the Split Data based on value of Threshold 10
        # Else Go with 6
        if (
                base_pack_count_by_admin_duration != base_pack_count_by_template and pack_type != constants.UNIT_DOSE_PER_PACK) or (
                pack_type == constants.MULTI_DOSE_PER_PACK and (is_sppd or is_customized)):
            logger.debug("Get the Split Information based on Max Threshold {}..."
                         .format(MAX_TEMPLATE_SPLIT_COUNT_THRESHOLD))
            response_max_threshold = get_split_data({'patient_id': patient_id, 'file_id': file_id,
                                                     'company_id': company_id, 'template_id': template_id,
                                                     'pack_type': pack_type,
                                                     'is_customized': is_customized, 'is_sppd': is_sppd,
                                                     'is_true_unit': is_true_unit,
                                                     'is_bubble': is_bubble},
                                                    MAX_TEMPLATE_SPLIT_COUNT_THRESHOLD)

            logger.debug("Get the minimum pack requirement based on Split Information with Max Threshold {}..."
                         .format(MAX_TEMPLATE_SPLIT_COUNT_THRESHOLD))
            if response_max_threshold['template_data']:
                base_pack_count_by_template_with_max_threshold = \
                    get_pack_requirement_by_template_column_number(template=response_max_threshold['template_data'],
                                                                   base_pack_count_by_admin_duration=
                                                                   base_pack_count_by_admin_duration)
                if base_pack_count_by_template != base_pack_count_by_template_with_max_threshold:
                    response = response_max_threshold

            # Identify the number of packs required based on column number (C)
            # If B != C Then Go with 10
            # Else Go with 6
            if base_pack_count_by_admin_duration != base_pack_count_by_template_with_max_threshold and pack_type != constants.UNIT_DOSE_PER_PACK and not is_true_unit and not is_sppd and not is_customized:
                logger.debug("Proceed with Max Threshold of {}...".format(MAX_TEMPLATE_SPLIT_COUNT_THRESHOLD))

                logger.debug("Determine if there are any empty columns, so that we can adjust meds..")
                max_column_number = max(map(get_template_distinct_column_number,
                                            response_max_threshold['template_data']))
                modulo_value = math.ceil(max_column_number % settings.PACK_COL)

                logger.debug("Max column Number: {}, Module Value based on Column Number: {}"
                             .format(max_column_number, modulo_value))
                if modulo_value > 0:
                    extra_split_after_threshold_split = True
                    empty_slot = settings.PACK_COL - modulo_value
                    summary_dict = get_response_summary_dict(response_max_threshold)

                    default_template_column: List[Dict[str, Any]] = []
                    final_template_update: List[Dict[str, Any]] = []
                    logger.debug("Summary Dict Version - 2: {}".format(summary_dict))
                    for empty_slot_iteration in range(empty_slot):
                        summary_dict = OrderedDict(sorted(summary_dict.items(), key=lambda x: x[1]["total_qty"],
                                                          reverse=True))
                        logger.debug("Summary Dict Version - Iteration: {}, Dict: {}"
                                     .format(empty_slot_iteration, summary_dict))
                        for column_number, summary_values in summary_dict.items():
                            if summary_values["total_qty"] > constants.TEMPLATE_SPLIT_COUNT_THRESHOLD:

                                default_template_column = []
                                # Prepare the list of template for column_number = 1
                                for index, template in enumerate(response_max_threshold['template_data']):
                                    if template["column_number"] == column_number:
                                        default_template_column.append(template)
                                    else:
                                        # increment the column number by 1 only for those columns that exceeds the
                                        # current column number
                                        # Eg: Total column numbers are 1, 2, 3, 4 and column_number = 2,
                                        # then we need to increment by column numbers 3 and 4
                                        if template["column_number"] > column_number:
                                            template["column_number"] += 1

                                # Store the template details by excluding the selected column_number entries.
                                # Eg: Total column numbers are 1, 2, 3, 4 and column_number = 2,
                                # then we need to exclude the entries for column_number = 2
                                # because we are going to re-calculate it and then append it back.
                                response_split: List[Dict[str, Any]] = \
                                    [template for template in response_max_threshold['template_data']
                                     if template["column_number"] != column_number]
                                response_max_threshold['template_data'] = response_split

                                # Perform the split for the selected column number
                                if default_template_column:
                                    response_temp_split = get_split_data({'patient_id': patient_id, 'file_id': file_id,
                                                                          'company_id': company_id,
                                                                          'template_id': template_id,
                                                                          'pack_type': pack_type,
                                                                          'is_customized': is_customized,
                                                                          'is_sppd': is_sppd,
                                                                          'is_true_unit': is_true_unit,
                                                                          'is_bubble': is_bubble},
                                                                         default_template_info=default_template_column)

                                    # On every instance from get_split_data, we get column number values starting from 1
                                    # But, if we have to adjust any column number apart from 1 then we need to adjust it
                                    # Eg: Total column numbers are 1, 2, 3, 4 and selected column_number = 2, then
                                    # --> response_max_threshold will have 1, 4, 5 column numbers as 3 and 4
                                    # would have been incremented by 1
                                    # --> response_temp_split will have column numbers 1 and 2. We need to increment
                                    # them by (selected column number value - 1)
                                    for template in response_temp_split["template_data"]:
                                        template["column_number"] += column_number - 1

                                    # Append the newly obtained template split to the main split
                                    response_max_threshold['template_data'] += response_temp_split["template_data"]

                                    # Refresh the flags and other objects with updated value
                                    response_max_threshold["pack_structure_modified"] = \
                                        response_temp_split["pack_structure_modified"] \
                                            if response_temp_split["pack_structure_modified"] \
                                            else response_max_threshold["pack_structure_modified"]

                                    response_max_threshold["store_separate_split"] = \
                                        response_temp_split["store_separate_split"] \
                                            if response_temp_split["store_separate_split"] \
                                            else response_max_threshold["store_separate_split"]

                                    response_max_threshold["volume_split"] = \
                                        response_temp_split["volume_split"] if response_temp_split["volume_split"] \
                                            else response_max_threshold["volume_split"]

                                    response_max_threshold["store_separate_split_hoa_times"] = \
                                        response_max_threshold["store_separate_split_hoa_times"]\
                                        .union(response_temp_split["store_separate_split_hoa_times"])

                                    response_max_threshold["volume_split_hoa_times"] = \
                                        response_max_threshold["volume_split_hoa_times"] \
                                        .union(response_temp_split["volume_split_hoa_times"])

                                    response_max_threshold["count_split_hoa_times"] = \
                                        response_max_threshold["count_split_hoa_times"] \
                                        .union(response_temp_split["count_split_hoa_times"])

                                    response_max_threshold["volume_split_error"] = \
                                        response_temp_split["volume_split_error"] \
                                            if response_temp_split["volume_split_error"] \
                                            else response_max_threshold["volume_split_error"]

                                    response_max_threshold["store_separate_split_error"] = \
                                        response_temp_split["store_separate_split_error"] \
                                            if response_temp_split["store_separate_split_error"] \
                                            else response_max_threshold["store_separate_split_error"]

                                    # refresh summary_dict dictionary with updated data for next iteration
                                    summary_dict = get_response_summary_dict(response_max_threshold)

                                    break

                # Refresh the pack number value if column numbers were modified
                if extra_split_after_threshold_split:
                    for template_hoa_rx in response_max_threshold["template_data"]:
                        db_update_pack_no(template_hoa_rx)

                response = response_max_threshold
            else:
                logger.debug("Proceed with Current Threshold from Company Settings as same number of packs are "
                             "generated with Current Threshold and Max Threshold of {}..."
                             .format(MAX_TEMPLATE_SPLIT_COUNT_THRESHOLD))
        else:
            logger.debug("Proceed with Current Threshold from Company Settings as pack requirement matches "
                         "based on Admin Duration and Split Information...")

        return response
    except StopIteration as e:
        logger.error(e, exc_info=True)
        raise e
    except (DoesNotExist, InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def add_pack_no_key_in_template_data_and_remove_duplicates(template_data, is_customized):
    """
    this function remove all the duplicate packs to show on DDT customize screen and add pack_no in response
    """
    try:
        for record in template_data:
            record['pack_no'] = math.ceil(record['column_number'] / 4)
        if is_customized:
            updated_template_data = []
            template_data = sorted(template_data, key=lambda x: x['column_number'])
            column_count = settings.PACK_COL
            first_admin = set(template_data[0]['admin_date_list'])
            jump_column = 0
            for record in template_data:
                if record['column_number'] > column_count:
                    if not first_admin.intersection(set(record['admin_date_list'])):
                        jump_column = column_count + settings.PACK_COL
                    column_count += settings.PACK_COL

                if record['column_number'] > column_count or record['column_number'] > jump_column:
                    updated_template_data.append(record)
            return updated_template_data
        return template_data
    except Exception as e:
        logger.error("in add_pack_no_key_in_template_data error is", e)


@log_args_and_response
@validate(required_fields=["patient_id", "file_id", "company_id"])
def get_template_data_v2(dict_patient_info, generate_pack_flag=None):
    """ Takes the patient_id and gets all the template data for the given patient_id.

        Args:
            dict_patient_info (dict): The dict containing patient id
            generate_pack_flag (boolean): whether method is called while generating packs or not

        Returns:
            List : All the template records for the given patient_id

        Examples:
            >>> get_template_data({"patient_id": 7, "file_id": 2, "system_id": 2, "version": 2})
            []

    """
    patient_id = dict_patient_info["patient_id"]
    company_id = int(dict_patient_info["company_id"])
    file_id = int(dict_patient_info["file_id"])
    is_file_upload = dict_patient_info.get("file_upload", False)
    template_data = []
    pack_structure_modified = bool()
    drug_canisters = defaultdict(list)
    fndc_txr_set = set()
    takeaway_template_data = []
    patient_note = ''
    patient_data = {}
    is_customized = False
    dummy_template = None

    split_config = dict()
    volume_split = False
    volume_split_error = False
    store_separate_split_error = False
    store_separate_split = False
    drug_count_auto_save = False
    volume_split_hoa_times = set()
    count_split_hoa_times = set()
    store_separate_split_hoa_times = set()
    linked_packs_list: List[int] = []
    change_rx_comment_list: List[str] = []

    # set of hoa time which were split
    split_times1 = set()  # split during separate drug split
    split_times2 = set()  # split during volume split
    split_times3 = set()  # split during count split
    verification_count = 0

    valid_file = db_verify_file_id_dao(file_id=file_id, company_id=company_id)
    # checking whether file_id and system_id are mapped for security check
    if not valid_file:
        return error(1016)

    status = template_get_status_dao(file_id=file_id, patient_id=patient_id)
    template_master_data = get_template_id_dao(file_id=file_id, patient_id=patient_id)
    if not template_master_data:
        return error(5005)
    pack_type, customization_flag, is_sppd, is_true_unit, is_bubble = get_template_flags(file_id=file_id, patient_id=patient_id)
    any_other_template_pending = is_other_template_pending_dao(file_id=file_id, patient_id=patient_id)
    # in case of upload file if any other template is in yellow/red state then split again
    if is_file_upload and any_other_template_pending:
        status = 1

    try:
        linked_packs_list, change_rx_comment_list = \
            db_get_ext_linked_data_change_rx(company_id=company_id, file_id=file_id, patient_id=patient_id)

        patient_data = next(get_patient_details_for_patient_id(patient_id=patient_id))
        for canister in get_template_canisters(file_id, patient_id, company_id):
            # get_template_canisters to fetch only required canister for this template
            # for canister in CanisterMaster.db_get_canister_by_company_id(company_id, in_robot=False):
            drug_canisters[canister["formatted_ndc"], canister["txr"]].append(canister)

        if not status and (
                    pack_type != constants.UNIT_DOSE_PER_PACK and not customization_flag and not is_true_unit and not is_sppd):
            # which means this is the one saved
            column_numbers = [0]  # initializing with 0 so don't have to add 1 every time into index
            unique_hoa_time = list()
            modified_time = None
            for record in db_get_saved_template(patient_id=patient_id, file_id=file_id,
                                                                company_id=company_id):
                # return only modified time of first row from data
                # which was ordered by column_number, patient_rx_id
                if modified_time is None:
                    modified_time = record["modified_time"]
                else:
                    record["modified_time"] = modified_time
                record["canister_list"] = drug_canisters[record["formatted_ndc"], record["txr"]]
                record["quantity"] = float(record["quantity"])
                if record["hoa_time"] not in unique_hoa_time:
                    unique_hoa_time.append(record["hoa_time"])
                admin_time = str(record["hoa_time"])
                admin_time = datetime.datetime.strptime(admin_time, "%H:%M:%S").strftime("%I:%M %p")
                record["display_time"] = admin_time
                record["short_drug_name"] = fn_shorten_drugname(record["drug_name"])
                record["file_id"] = file_id
                record["pack_no"] = pack_no_by_column_no(record["column_number"])
                if record["column_number"] not in column_numbers:
                    column_numbers.append(record["column_number"])
                record["column_number"] = column_numbers.index(record["column_number"])
                template_data.append(record)
            column_number_length = len(column_numbers)
            # check if column number is sequential
            is_column_numbers_sequential = (column_number_length - 1) == column_numbers[column_number_length - 1]
            # check if admin_time_list is ascending in order
            is_hoa_time_list_ascending = all(
                [unique_hoa_time[i] < unique_hoa_time[i + 1] for i in range(len(unique_hoa_time) - 1)])
            if not (is_hoa_time_list_ascending and is_column_numbers_sequential):
                pack_structure_modified = True
            query = get_take_away_template_by_patient_dao(patient_id=patient_id)

            for record in query:
                record["week_day"] = (record["week_day"] + 1) % 7  # python to angular day conversion
                takeaway_template_data.append(record)
        else:  # yellow and red template

            response = db_get_split_info_threshold_and_max_threshold(patient_id=patient_id, file_id=file_id,
                                                                     company_id=company_id,
                                                                     template_id=template_master_data['id'],
                                                                     pack_type=pack_type, is_customized=customization_flag,
                                                                     is_sppd=is_sppd, is_true_unit=is_true_unit,
                                                                     is_bubble=is_bubble)
            template_data = response['template_data']
            pack_structure_modified = response['pack_structure_modified']
            store_separate_split = response['store_separate_split']
            volume_split = response['volume_split']
            drug_count_auto_save = response['drug_count_auto_save']
            verification_count = response['verification_count']
            store_separate_split_hoa_times = response['store_separate_split_hoa_times']
            volume_split_hoa_times = response['volume_split_hoa_times']
            count_split_hoa_times = response['count_split_hoa_times']
            volume_split_error = response['volume_split_error']
            store_separate_split_error = response['store_separate_split_error']
            split_config = response['split_config']
            is_customized = response['is_customized']
            dummy_template = response['dummy_template']

        try:
            patient_note_data = get_patient_data_dao(patient_id=patient_id)
            patient_note = patient_note_data['note']
        except DoesNotExist:
            logger.info("patient note does not exists")
    except StopIteration as e:
        logger.error(e, exc_info=True)
        return error(1004)
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return error(1004)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    template_data = sorted(template_data, key=lambda x: x["drug_name"])
    template = dummy_template if dummy_template else template_data
    if not generate_pack_flag:
        template_data = add_pack_no_key_in_template_data_and_remove_duplicates(template, is_customized)
    response = {
        "template_data": template_data,
        "template_status": template_master_data['status'],
        "pack_structure_modified": pack_structure_modified,
        "note": patient_note,
        "takeaway_template_data": takeaway_template_data,
        "patient_data": patient_data,
        "store_separate_split": store_separate_split,
        "volume_split": volume_split,
        "store_separate_split_hoa_times": store_separate_split_hoa_times,
        "volume_split_hoa_times": volume_split_hoa_times,
        "count_split_hoa_times": count_split_hoa_times,
        "volume_split_error": volume_split_error,
        "store_separate_split_error": store_separate_split_error,
        "split_config": split_config,
        "verification_count": verification_count,
        "drug_count_auto_save": drug_count_auto_save,
        "linked_packs": linked_packs_list,
        "change_rx_comment": change_rx_comment_list,
        "is_customized": is_customized,
        "dummy_template": dummy_template
    }
    return response


@validate(required_fields=["company_id", "file_id", "user_id", "data"])
def set_template_data(dict_template_details):
    """ Gets the template data along with the patient_id and stores them in the
    template_details table.

        Args:
            dict_template_details(dict) : Patient id for which the template data is to be saved, user id, file id, system id
        Returns:
            Boolean : True or False given on the status of the data saved.

        Examples:
            >>> set_template_data([])
            []
    """
    try:
        patient_id = dict_template_details["data"][0]["patient_id"]
    except (LookupError):
        return error(1020)
    user_id = int(dict_template_details["user_id"])
    file_id = dict_template_details["file_id"]
    modified_time = dict_template_details["modified_time"]
    company_id = int(dict_template_details["company_id"])
    takeaway_template_data = dict_template_details.get("takeaway_template_data", None)
    set_yellow_template_flag = dict_template_details.get("set_yellow_template_flag", False)
    logger.info('set_yellow_template_flag' + str(set_yellow_template_flag))
    set_red_template_flag = dict_template_details.get("set_red_template_flag", False)
    logger.info('set_red_template_flag' + str(set_red_template_flag))
    valid_file = db_verify_file_id_dao(file_id=file_id, company_id=company_id)
    if not valid_file:
        return error(1016)  # file is not valid for system so do not save template data

    template_savable = None
    try:
        # is_template_currently_saved = TemplateDetails.is_template_stored(file_id, patient_id)
        # if not is_template_currently_saved:
        saveable_template_file_id = get_template_file_id_dao(patient_id=patient_id,
                                                            status=settings.PENDING_PROGRESS_TEMPLATE_LIST)
        if saveable_template_file_id == int(file_id):
            template_savable = True
    # else:
    #     template_savable = True

    except InternalError as e:
        logger.error(e, exc_info=True)
        return error(2002)

    if not template_savable:
        return error(5001)
    # template_savable = None
    # for template in pending_templates:
    #     # check if there are saved templates present then allow to save only if file id matches
    #     if not template["is_modified"]:
    #         if template["file_id"] == file_id and template_savable != True:
    #             template_savable = True
    #         if template["file_id"] != file_id and template_savable is None:
    #             template_savable = False
    # if template_savable is None: # if none of the pending template is saved, we allow to save template
    #     template_savable = True
    # logger.info('template_savable')
    # logger.info(template_savable)
    # to remove quantity 0 added by front-end
    template_data = list(filter(lambda x: x["quantity"] > 0, dict_template_details["data"]))
    status = db_save_template(file_id, patient_id, template_data, user_id, modified_time,
                              takeaway_template_data, set_yellow_template_flag, set_red_template_flag)

    parsed_response = json.loads(status)
    if parsed_response["status"] == settings.SUCCESS_RESPONSE:
        update_notifications_couch_db_green_status(file_id=file_id, patient_id=patient_id, company_id=company_id)

    if status:
        try:
            update_pending_template_data_in_redisdb(company_id)
        except (RedisConnectionException, Exception):
            pass
    return status


def save_template_details(patient_id, file_id, company_id, user_id, is_modified, file_upload):
    data_dict = {
        'patient_id': patient_id,
        "file_id": file_id,
        "company_id": company_id,
        "file_upload": True
    }
    json_template_data = create_response(get_template_data_v2(data_dict, generate_pack_flag=True))
    template_data = json.loads(json_template_data)
    is_customized = template_data['data']['is_customized']
    verification_count = template_data["data"]["verification_count"]
    drug_count_auto_save = template_data["data"]["drug_count_auto_save"]
    dummy_template = template_data["data"]["dummy_template"]
    template_data = template_data["data"]["template_data"]
    template_data = sorted(template_data, key=lambda x: x['column_number'])

    set_yellow_template_flag = True
    set_red_template_flag = False

    # code for same drug split
    is_same_drug_split = False
    for data in template_data:
        if data.get("same_drug_auto_split", None):
            is_same_drug_split = True
            break

    # if is_same_drug_split or verification_count > 0:
    #     set_yellow_template_flag = False
    #     set_red_template_flag = True

    # if drug_count_auto_save:
    #     set_yellow_template_flag = True
    #     set_red_template_flag = False

    logger.info(
        'before save: patient_id: ' + str(patient_id) + 'file_id: ' + str(file_id) + 'set_yellow_template_flag:' +
        str(set_yellow_template_flag))

    if file_upload:
        logger.debug('in file_upload: ' + str(patient_id) + 'file_id: ' + str(file_id) +
                     'is_modified: ' + str(is_modified))
        if is_other_template_pending_dao(file_id=file_id, patient_id=patient_id):
            # while uploading a file if any other template of a patient is in yellow/red state then only update yellow or
            # red flag for upcoming file data
            logger.debug('in_is_other_template_pending: patient_id: ' + str(patient_id) + 'file_id: ' + str(file_id) +
                         'is_modified:' + str(is_modified))
            # modification_status = None
            # if set_yellow_template_flag:
            modification_status = constants.IS_MODIFIED_MAP['YELLOW']
            # elif set_red_template_flag:
            #     modification_status = TemplateMaster.IS_MODIFIED_MAP['RED']
            status2 = update_modification_status_dao(patient_id=patient_id,
                                                     file_id=file_id,
                                                     modification_status=modification_status)
            return True
        elif is_modified:
            logger.debug("Template_is_modified")
            # modification_status = None
            # if set_yellow_template_flag:
            modification_status = constants.IS_MODIFIED_MAP['YELLOW']
            # elif set_red_template_flag:
            #     modification_status = TemplateMaster.IS_MODIFIED_MAP['RED']
            status2 = update_modification_status_dao(patient_id=patient_id,
                                                     file_id=file_id,
                                                     modification_status=modification_status)
            return True
    else:
        template_details_data_dict = list()
        for template_details in template_data:
            temp_dict = {"patient_id": template_details['patient_id'],
                         "patient_rx_id": template_details['patient_rx_id'],
                         "column_number": template_details['column_number'],
                         "hoa_time": template_details['hoa_time'],
                         "quantity": template_details['quantity'],
                         "file_id": file_id
                         }
            template_details_data_dict.append(temp_dict)
        print(template_details_data_dict)
        temp_dict = {"company_id": company_id,
                     "file_id": file_id,
                     "data": template_details_data_dict,
                     "user_id": user_id,
                     "modified_time": get_current_date_time(),
                     "takeaway_template_data": [],
                     "set_yellow_template_flag": set_yellow_template_flag,
                     "set_red_template_flag": set_red_template_flag
                     }
        logger.info("temp_det_data" + str(temp_dict))
        json_save_response = set_template_data(temp_dict)
        logger.debug("Records inserted in template details with status {}".format(json_save_response))
        save_response = json.loads(json_save_response)
        if save_response["status"] == 'failure' and save_response['code'] == 5001:
            logger.info('template_details_not_stored: ', str(patient_id), str(file_id))
            # if file_upload:
            #     logger.info('in_update_status: patient_id: ' + str(patient_id) + 'file_id: '+ str(file_id))
            #     modification_status = None
            #     if not is_modified:
            #         modification_status = TemplateMaster.IS_MODIFIED_MAP['GREEN']
            #     elif set_yellow_template_flag:
            #         modification_status = TemplateMaster.IS_MODIFIED_MAP['YELLOW']
            #     elif set_red_template_flag:
            #         modification_status = TemplateMaster.IS_MODIFIED_MAP['RED']
            #     status2 = TemplateMaster.db_update_modification_status(patient_id, file_id, modification_status)
            #
            # else:
            raise TemplateException(error(save_response['code']))
        return template_data, is_customized, dummy_template


def get_template_column(hoa_time):
    """ Gets the column number between 1-16 for the given hoa_time.
        info: Obsolete - as template morning, noon, evening, bedtime will not be considered for column_number
        Args:
            hoa_time (time): The input time..
        Returns:
            int : The column number between 1 to 16.

        Examples:
            >>> get_template_column('08:00')
            1
    """
    _time_range = get_time_range(hoa_time)
    return _time_range


def get_time_range(hoa_time):
    """ Gets group number based on the admin time
        info: Obsolete - as template morning, noon, evening, bedtime will not be considered for column_number
        Args:
            hoa_time (time): The input time..
        Returns:
            int : The column number between 1 to 4.

        Examples:
            >>> get_time_range("08:00")
            1
    """
    column_no = None
    if convert_time('1100') >= hoa_time:
        column_no = 1
    elif convert_time('1600') > hoa_time:
        column_no = 5
    elif convert_time('1900') > hoa_time:
        column_no = 9
    elif convert_time('1900') <= hoa_time:
        column_no = 13

    return column_no


def is_template_modified(patient_id, present_rx_no_set, company_id):
    """ Takes a file and creates a data frame from it form the input arguments

        Args:
            patient_id (int): The id of the patient
            present_rx_no_set (set): All the rx no which belongs to the patient
            given patient_id

        Returns:
            Boolean : True if all the template for the patient is present in the template_details table
            otherwise False

        Examples:
            >>> is_template_modified(1, set())
            >>> True

    """
    rx_no_set = set()

    for record in db_get_rx_info(patient_id):
        rx_no_set.add(record["pharmacy_rx_no"].strip() +
                      SEPARATOR + str(round(record["total_quantity"], 1)) +
                      SEPARATOR + str(record["hoa_time"]) +
                      SEPARATOR + str(record["drug_id"])
                      )

    logger.info("Patient Rx set from TemplateDetails" + str(rx_no_set))
    # If both set are similar, template is not modified
    if rx_no_set == present_rx_no_set:
        # previous_template_is_modified = TemplateMaster.db_get_previous_is_modified(patient_id, company_id)
        # if previous_template_is_modified == 1:
        #     return True
        # else:
        return False
    return True


@validate(required_fields=["status", "company_id"])
def get_all_templates(filters):
    """ Gets all the template meta data for the given date range

        Args:
            filters (dict): status(int), system_id(int).

        Returns:
            List : List of all the template meta data for given status.

        Examples:
            >>> get_all_templates({})
            >>> []

    """
    status = filters["status"]
    company_id = filters["company_id"]
    template_records = []
    try:
        if CeleryTaskmeta.table_exists():
            if settings.REDIS_FLAG:
                try:
                    if settings.is_redis_updated:
                        logger.info("redis_is_updated_so_fetching_records_from_redisdb")
                        template_records = fetch_template_records_from_redisdb(company_id)
                    else:
                        logger.info("updating_and_fetching_records_from_redisdb")
                        try:
                            update_pending_template_data_in_redisdb(company_id)
                            template_records = fetch_template_records_from_redisdb(company_id)
                        except (RedisKeyException, RedisConnectionException, Exception) as e:
                            logger.info(e)

                            template_records = db_get_pending_templates_data(company_id)

                except RedisKeyException as e:
                    logger.info(e)
                    logger.info("updating_and_fetching_records_from_redisdb")
                    try:
                        update_pending_template_data_in_redisdb(company_id)
                        template_records = fetch_template_records_from_redisdb(company_id)
                    except (RedisKeyException, RedisConnectionException, Exception) as e:
                        logger.info(e)
                        logger.info("fetching_records_from_mysql_database")
                        template_records = db_get_pending_templates_data(company_id)

                except (RedisConnectionException, Exception) as e:
                    logger.info(e)
                    logger.info("fetching_records_from_mysql_database")
                    try:
                        template_records = db_get_pending_templates_data(company_id)
                    except (InternalError, IntegrityError, DataError, DoesNotExist):
                        return error(2001)

            elif settings.USE_TASK_QUEUE:
                logger.info("fetching_records_from_mysql_redis_flag_off")
                try:
                    template_records = db_get_pending_templates_data(company_id)
                except (InternalError, IntegrityError, DataError, DoesNotExist):
                    return error(2001)

            else:
                try:
                    for record in db_get_pending_templates(status, company_id):
                        template_records.append(record)
                except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
                    logger.error(e)
                    return error(2001)

        else:
            try:
                for record in db_get_pending_templates(status, company_id):
                    template_records.append(record)
            except (InternalError, IntegrityError, DataError, DoesNotExist):
                return error(2001)

    except StopIteration as e:
        logger.error(e, exc_info=True)
        return error(1004)

    return create_response(template_records)


@validate(required_fields=['unique_drug_id', 'user_id', 'company_id', 'dosage_type_id'])
def add_store_separate_drug(drug_info):
    """
    Add given store separate drug
    :param drug_info:
    :return:
    """
    unique_drug_id = drug_info['unique_drug_id']
    user_id = drug_info['user_id']
    company_id = drug_info['company_id']
    dosage_type_id = drug_info['dosage_type_id']
    do_update = drug_info.get('update', 0)

    try:
        record, created = create_store_separate_drug_dao(company_id=company_id,
                                                         unique_drug_id=unique_drug_id,
                                                         dosage_type_id=dosage_type_id,
                                                         user_id=user_id)
        if do_update and not created:  # if user wants to update the old dosage_type_id
            record.dosage_type_id = dosage_type_id
            record.modified_by = user_id
            record.modified_date = get_current_date_time()
            record.save()
            created = True  # mark it created to indicate success

        response = {'id': record.id,
                    'created': created}
        return create_response(response)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@validate(required_fields=['store_separate_drug_ids'])
def delete_store_separate_drug(request_args):
    """ Deletes store separate records for given record ids """
    try:
        status = 0
        record_id_list = request_args['store_separate_drug_ids']
        if record_id_list:
            query = delete_separate_drug_dao(drug_id_list=record_id_list)
            status = query.execute()
        return create_response(status)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@validate(required_fields=['company_id'])
def get_store_separate_drugs(request_params):
    """
    Returns list of store separate drug.
    Optionally provides filtered, ordered and paginated data.
    :param request_params:
    :return:
    """
    try:
        count, results = get_store_separate_drugs_dao(request_params=request_params)
        response = {"records": results, "number_of_records": count}
        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error("Error in replenish_alternate_options {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("Error in replenish_alternate_options {}".format(e))
        return error(2001)


@log_args_and_response
@validate(required_fields=['template_ids', 'user_id', 'company_id', 'reason'])
def rollback_templates(request_args):
    """
    Performs template rollback for given template_ids and file rollback if all templates are rolled back
    :param request_args: dict
    :return: str
    """
    template_ids = request_args['template_ids']
    user_id = request_args['user_id']
    company_id = request_args['company_id']
    reason = request_args['reason']
    redis_flag = settings.REDIS_FLAG
    try:
        with db.transaction():
            print('in')
            # validate_template = TemplateMaster.db_verify_templatelist(template_ids, company_id,
            #                                                           [settings.PENDING_TEMPLATE_STATUS,
            #                                                            settings.PROGRESS_TEMPLATE_STATUS])
            validate_template = db_verify_template_list_dao(template_list=template_ids, company_id=company_id,
                                                            status=settings.PENDING_PROGRESS_TEMPLATE_LIST)
            print(validate_template)
            if not validate_template:
                return error(5005)
            patient_file_data = db_get_file_patient(template_ids, company_id, [constants.IS_MODIFIED_MAP['YELLOW']])

            temp_slot_data_delete = db_get_file_patient(template_ids, company_id,
                                                        [constants.IS_MODIFIED_MAP['YELLOW'],
                                                         constants.IS_MODIFIED_MAP['GREEN'],
                                                         constants.IS_MODIFIED_MAP['RED']])

            print(temp_slot_data_delete)
            # query = TemplateMaster.update(
            #     status=settings.UNGENERATED_TEMPLATE_STATUS,
            #     reason=reason,
            #     modified_by=user_id,
            #     modified_date=get_current_date_time()
            # ).where(TemplateMaster.id << template_ids,
            #         TemplateMaster.company_id == company_id,
            #         TemplateMaster.status << [settings.PENDING_TEMPLATE_STATUS, settings.PROGRESS_TEMPLATE_STATUS])
            # status = query.execute()
            status = db_update_pending_progress_templates_by_status(status=settings.UNGENERATED_TEMPLATE_STATUS,
                                                                    reason=reason, user_id=user_id,
                                                                    template_ids=template_ids, company_id=company_id)
            print(status)
            if status:
                for patient, file_ids in patient_file_data.items():
                    # TemplateDetails.delete().where(TemplateDetails.patient_id == patient,
                    #                                TemplateDetails.file_id << file_ids).execute()
                    db_delete_templates_by_patient_file_ids(patient_id=patient, file_ids=file_ids)

                logger.info("temp_slot_data_delete" + str(temp_slot_data_delete))
                for patient, file_ids in temp_slot_data_delete.items():
                    # TempSlotInfo.delete().where(TempSlotInfo.patient_id == patient,
                    #                             TempSlotInfo.file_id << file_ids).execute()
                    db_delete_temp_slot_by_patient_file_ids(patient_id=patient, file_ids=file_ids)

                # get unique files ids from template ids
                # rolled_back_file_ids = TemplateMaster.db_get_file_id_from_template_ids(
                #     template_ids,
                #     [settings.UNGENERATED_TEMPLATE_STATUS]
                # )
                rolled_back_file_ids = db_get_file_id_from_template_ids_dao(template_ids=template_ids,
                                                                            status=
                                                                            [settings.UNGENERATED_TEMPLATE_STATUS])

                other_template_status = settings.PENDING_PROGRESS_TEMPLATE_LIST + [settings.DONE_TEMPLATE_STATUS]

                # file_ids = TemplateMaster.db_get_file_ids(list(rolled_back_file_ids), other_template_status)
                file_ids = db_get_template_by_rolled_back_file_ids(rolled_back_file_ids=rolled_back_file_ids,
                                                                   other_template_status=other_template_status)
                if rolled_back_file_ids:
                    to_be_rolled_back_files = rolled_back_file_ids - file_ids
                    if to_be_rolled_back_files:
                        # FileHeader.db_update(list(to_be_rolled_back_files), settings.UNGENERATE_FILE_STATUS, reason)
                        db_update_rollback_files(to_be_rolled_back_files=to_be_rolled_back_files,
                                                 status=settings.UNGENERATE_FILE_STATUS, reason=reason)
        if status:
            try:
                update_pending_template_data_in_redisdb(company_id)
            except (RedisConnectionException, Exception):
                pass
        if to_be_rolled_back_files:
            real_time_db_timestamp_trigger(
                settings.CONST_PRESCRIPTION_FILE_DOC_ID,
                company_id=company_id
            )

        update_couch_db_pending_template_count(company_id=company_id)
        return create_response(status)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@validate(required_fields=["company_id", "time_zone"])
def get_rollback_templates(request_params):
    """
    Returns rolled back templates,
    Optionally paginates, filters and sorts records
    :param request_params: dict
    :return: str
    """
    try:
        company_id = request_params["company_id"]
        time_zone = request_params["time_zone"]
        filter_fields = request_params.get('filter_fields', None)
        sort_fields = request_params.get('sort_fields', None)
        paginate = request_params.get('paginate', None)
        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        count, results = get_rollback_templates_dao(company_id, filter_fields, paginate, sort_fields, time_zone)
        response = {"records": results, "number_of_records": count}

        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error("Error in get_rollback_templates {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("Error in get_rollback_templates {}".format(e))
        return error(2001)


@log_args_and_response
def unit_dosage_splitting(template_data, customization_flag, seperate_flag, is_true_unit, is_bubble=False):
    """
    split the pack as per unit pack per dose
    :return: str
    """
    try:
        start_list = []
        end_list = []
        admin_date_list = []
        fake_date_list = []
        date_list = []
        result = []
        # for variable admin dates per Rx, we will consider min of all admins as start and max of all admins as end date
        for temp_record in template_data:
            start_list.append(datetime.datetime.strptime((temp_record['admin_date_list'][0]), '%Y-%m-%d'))
            end_list.append(datetime.datetime.strptime((temp_record['admin_date_list'][-1]), '%Y-%m-%d'))
        start_date = min(start_list)
        end_date = max(end_list)
        # making complete admin_date_list which will used to map with intermittent dated drugs / tapered drugs
        while start_date <= end_date:
            admin_date_list.append(start_date.strftime('%Y-%m-%d'))
            start_date += datetime.timedelta(days=1)
        if not customization_flag:
            for item in template_data:
                fake_date_list = []
                for date in admin_date_list:
                    fake_date_list.append(date)
                    if date in item['admin_date_list']:
                        date_list.append(date)

                    if len(fake_date_list) == (settings.PACK_ROW if not is_bubble else settings.BUBBLE_PACK_ROW):
                        updated_item = item.copy()
                        updated_item['admin_date_list'] = date_list
                        if not date_list:
                            continue
                        result.append(updated_item)
                        if item['admin_date_list'] == date_list:
                            date_list = []
                            fake_date_list = []
                            break
                        date_list = []
                        fake_date_list = []
                if date_list:
                    updated_item = item.copy()
                    updated_item['admin_date_list'] = date_list
                    result.append(updated_item)
                    date_list = []
                    fake_date_list = []
        else:
            result = template_data
        result = sorted(result, key=lambda x: x['admin_date_list'][0])
        if seperate_flag:
            result = sorted(result, key=lambda x: x['hoa_time'])
        if (not customization_flag) or (customization_flag and seperate_flag):
            result = sorted(result, key=lambda x: x['pharmacy_rx_no'])
        prev_rx = result[0]['drug_id']
        response = []
        if is_true_unit:
            column_number = 1
            for temp_record in result:
                rx_qty = temp_record['quantity']
                qty_range = math.ceil(rx_qty)
                qty = 1.0
                for i in range(qty_range):
                    if rx_qty - i == 0.5:
                        qty = 0.5
                    updated_item = temp_record.copy()
                    updated_item['column_number'] = column_number
                    updated_item['quantity'] = qty
                    updated_item['total_volume'] = updated_item['approx_pill_volume'] * qty
                    response.append(updated_item)
                    column_number += 1
        result = response if response else result

        # assigning column numbers expecting there are no split needed if so we will re assign columns based on split
        response = []
        column_number = 1
        for temp_record in result:
            update_data = temp_record.copy()
            if temp_record['drug_id'] == prev_rx:
                update_data['column_number'] = column_number
            else:
                column_number += ((settings.PACK_COL - (
                                    column_number % settings.PACK_COL)) if column_number % settings.PACK_COL else (
                                    column_number % settings.PACK_COL))
                update_data['column_number'] = column_number
                prev_rx = temp_record['drug_id']
            column_number += 1
            response.append(update_data)
        return response

    except (IntegrityError, InternalError) as e:
        logger.error("Error in unit_dosage_splitting {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("Error in unit_dosage_splitting {}".format(e))
        return error(2001)


@log_args_and_response
def unit_dosage_column_reassignation(template_data, seperate_flag):
    """
    re assignation of columns after volume and quantity splitting
    """
    try:
        response = []
        column_number = 1
        prev_rx = template_data[0]['drug_id']
        unique_hoa = []
        unique_admin = []
        range_tuples = []
        start_list = []
        end_list = []
        count_dict = defaultdict(int)
        # find unique admin list to compare with column's admin duration
        # purpose for this list is for some admins we can not directly compare with start or end date of admin,
        # we have to check whether admin is subset of start and end date
        t_data = sorted(template_data, key=lambda x: len(x['admin_date_list']), reverse=True)
        for admin_record in t_data:
            dates = admin_record['admin_date_list']
            if admin_record['hoa_time'] not in unique_hoa:
                unique_hoa.append(admin_record['hoa_time'])
            start_date = min(dates)
            end_date = max(dates)

            for date_range in range_tuples:
                if start_date >= date_range[0] and end_date <= date_range[1]:
                    break
            else:
                unique_admin.append(dates)
                range_tuples.append((start_date, end_date))
        unique_admin = sorted(unique_admin, key=lambda x: x[0])
        # first find total start and end date for tapered drugs or intermittent filling drugs
        for temp_record in template_data:
            if not seperate_flag:
                count_dict[temp_record['drug_id']] += 1
            else:
                rx_hoa_tuple = (temp_record['drug_id'], temp_record['hoa_time'])
                count_dict[rx_hoa_tuple] += 1
            start_list.append(datetime.datetime.strptime((temp_record['admin_date_list'][0]), '%Y-%m-%d'))
            end_list.append(datetime.datetime.strptime((temp_record['admin_date_list'][-1]), '%Y-%m-%d'))
        # find max admin can be filled in one pack
        max_admin_in_one_pack = 1 if math.floor(4 * len(unique_admin) / max(count_dict.values())) == 0 else math.floor(
            4 * len(unique_admin) / max(count_dict.values()))
        """ now we have to re assign columns: as Rx changes we will jump to next pack's first column
        same way if admin changes for same Rx we will check whether there are enough remaining columns to fit next 
        hoa or jump to next pack's first column """
        prev_admin_index = 0
        admin_count = 1
        prev_hoa = template_data[0]['hoa_time']
        for temp_record in template_data:
            current_hoa = temp_record['hoa_time']
            for i, sublist in enumerate(unique_admin):
                if set(temp_record['admin_date_list']).issubset(sublist):
                    admin_index = i
                    break
            # if Rx is changed we will definitely jump to next pack's first column
            if not temp_record['drug_id'] == prev_rx:
                column_number -= 1
                column_number += (((settings.PACK_COL - (
                        column_number % settings.PACK_COL)) if column_number % settings.PACK_COL else (
                        column_number % settings.PACK_COL))) + 1
                prev_rx = temp_record['drug_id']
                prev_admin_index = 0
                admin_count = 1
                prev_hoa = current_hoa
            # if only admin is changed for same Rx, we will check how many admins we are allowed to fit, if more
            # admins is reached we will jump to next pack's first column
            elif seperate_flag and current_hoa != prev_hoa:
                column_number -= 1
                column_number += (((settings.PACK_COL - (
                        column_number % settings.PACK_COL)) if column_number % settings.PACK_COL else (
                        column_number % settings.PACK_COL))) + 1
                prev_hoa = current_hoa
                prev_admin_index = 0
                admin_count = 1
            elif prev_admin_index != admin_index:
                admin_count += 1
                if admin_count > max_admin_in_one_pack:
                    column_number -= 1
                    column_number += (((settings.PACK_COL - (
                            column_number % settings.PACK_COL)) if column_number % settings.PACK_COL else (
                            column_number % settings.PACK_COL))) + 1
                    admin_count = 1
                prev_admin_index = admin_index
            update_data = temp_record.copy()
            update_data['column_number'] = column_number
            column_number += 1
            response.append(update_data)
        result = []

        # below code is to modify any date range into fix 7/8 days duration, it also maps intermittent days
        dummy_template = response
        for item in response:
            dates = item['admin_date_list']

            modified_dates = []

            for date_range in unique_admin:
                if all(date in date_range for date in dates):
                    for date in dates:
                        f_index = date_range.index(date)
                        modified_dates.append(unique_admin[0][f_index])
                    break
            update_data = item.copy()
            update_data['admin_date_list'] = modified_dates
            result.append(update_data)
        return result, True, dummy_template

    except (IntegrityError, InternalError) as e:
        logger.error("Error in unit_dosage_splitting {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("Error in unit_dosage_splitting {}".format(e))
        return error(2001)


@log_args_and_response
def splitting_for_packs_with_customization(template_data, is_true_unit, pack_type):
    """
        split the pack as per customization_for_empty_columns
        @params: template_data - consists the base template after splitting
        @params: is_true_unit
        @params: pack_type
        return: str
    """
    try:
        response = []
        if is_true_unit:
            column_number = 1
            for temp_record in template_data:
                rx_qty = temp_record['quantity']
                qty_range = math.ceil(rx_qty)
                # we will iterate loop as for the number of total pills
                qty = 1.0
                for i in range(qty_range):
                    # default qty we will place as 1 and for last half pill we will set 0.5
                    if rx_qty - i == 0.5:
                        qty = 0.5
                    updated_item = temp_record.copy()
                    updated_item['column_number'] = column_number
                    updated_item['quantity'] = qty
                    updated_item['total_volume'] = updated_item['approx_pill_volume'] * qty
                    response.append(updated_item)
                    column_number += 1
        template_data = response if response else template_data
        # if there are no more than 2 empty columns for 1 pack suggests that there is no need of customization
        max_column_number = template_data[-1]['column_number']
        if max_column_number > 2:
            return template_data, False, None
        else:
            start_list = []
            end_list = []
            admin_date_list = []
            fake_date_list = []
            date_list = []
            result = []
            response = []
            # to find complete admin list which includes all admin dates
            for temp_record in template_data:
                start_list.append(datetime.datetime.strptime((temp_record['admin_date_list'][0]), '%Y-%m-%d'))
                end_list.append(datetime.datetime.strptime((temp_record['admin_date_list'][-1]), '%Y-%m-%d'))
            start_date = min(start_list)
            end_date = max(end_list)

            # dividing Rx dicts in 7/8 days splitted dicts
            while start_date <= end_date:
                admin_date_list.append(start_date.strftime('%Y-%m-%d'))
                start_date += datetime.timedelta(days=1)
            for item in template_data:
                fake_date_list = []
                for date in admin_date_list:
                    fake_date_list.append(date)
                    if date in item['admin_date_list']:
                        date_list.append(date)

                    if len(fake_date_list) == settings.PACK_ROW:
                        updated_item = item.copy()
                        updated_item['admin_date_list'] = date_list
                        if not date_list:
                            continue
                        result.append(updated_item)
                        if item['admin_date_list'] == date_list:
                            date_list = []
                            fake_date_list = []
                            break
                        date_list = []
                        fake_date_list = []
                if date_list:
                    updated_item = item.copy()
                    updated_item['admin_date_list'] = date_list
                    result.append(updated_item)
                    date_list = []
                    fake_date_list = []

            result = sorted(result, key=lambda x: x['admin_date_list'][0])
            unique_admin = []
            range_tuples = []

            # getting unique admins for purpose of comparing intermittent admins with unique admin
            t_data = sorted(result, key=lambda x: len(x['admin_date_list']), reverse=True)
            for admin_record in t_data:
                dates = admin_record['admin_date_list']
                start_date = min(dates)
                end_date = max(dates)

                for date_range in range_tuples:
                    if start_date >= date_range[0] and end_date <= date_range[1]:
                        break
                else:
                    unique_admin.append(dates)
                    range_tuples.append((start_date, end_date))
            max_column_number = 0
            unique_admin = sorted(unique_admin, key=lambda x: x[0])
            # assigning column number as per multi or unit dose pack
            if pack_type == constants.MULTI_DOSE_PER_PACK:
                for item in result:
                    admin_date_list = item['admin_date_list']
                    column_number = item['column_number']

                    if set(unique_admin[0]).issubset(set(admin_date_list)) and column_number > max_column_number:
                        max_column_number = column_number
                for record in result:
                    print(record)
                    admin_dates = record['admin_date_list']
                    for index, date_range in enumerate(unique_admin):
                        if all(date in date_range for date in admin_dates):
                            matching_index = index
                            break
                    update_data = record.copy()
                    update_data['column_number'] = record['column_number'] + (matching_index * max_column_number)
                    response.append(update_data)
            if pack_type == constants.UNIT_DOSE_PER_PACK:
                max_column_number = max(item['column_number'] for item in result)
                response = []
                prev_admin_index = 0
                column_number = 1
                buffer_columns = 0
                for temp_record in result:
                    for i, sublist in enumerate(unique_admin):
                        if set(temp_record['admin_date_list']).issubset(sublist):
                            admin_index = i
                            break
                    if not prev_admin_index == admin_index:
                        if max_column_number > 2:
                            column_number -= 1
                            buffer_columns += ((settings.PACK_COL - (
                                    column_number % settings.PACK_COL)) if column_number % settings.PACK_COL else (
                                    column_number % settings.PACK_COL))
                            column_number += 1
                            prev_admin_index = admin_index
                    update_data = temp_record.copy()
                    update_data['column_number'] = column_number + buffer_columns
                    response.append(update_data)
                    column_number += 1
            result = []
            dummy_template = response
            for item in response:
                dates = item['admin_date_list']

                modified_dates = []

                for date_range in unique_admin:
                    if all(date in date_range for date in dates):
                        for date in dates:
                            f_index = date_range.index(date)
                            modified_dates.append(unique_admin[0][f_index])
                        break
                update_data = item.copy()
                update_data['admin_date_list'] = modified_dates
                result.append(update_data)
            return result, True, dummy_template

    except (IntegrityError, InternalError) as e:
        logger.error("Error in customization_for_empty_columns {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("Error in customization_for_empty_columns {}".format(e))
        return error(2001)


@log_args_and_response
def multi_seperate_pack_per_dose(template_data, is_bubble=False):
    """
    split the pack as per multi separate pack per dose
    :return: str
    """
    try:
        start_list = []
        end_list = []
        admin_date_list = []
        fake_date_list = []
        date_list = []
        result = []
        count_dict = defaultdict(int)
        prev_column_number = 0
        # first find total start and end date for tapered drugs or intermittent filling drugs
        for temp_record in template_data:
            hoa_time = temp_record['hoa_time']
            if not prev_column_number == temp_record['column_number']:
                count_dict[hoa_time] += 1
            start_list.append(datetime.datetime.strptime((temp_record['admin_date_list'][0]), '%Y-%m-%d'))
            end_list.append(datetime.datetime.strptime((temp_record['admin_date_list'][-1]), '%Y-%m-%d'))
            prev_column_number = temp_record['column_number']
        # find max admin can be filled in one pack
        max_admin_in_one_pack = 1 if math.floor(4 / max(count_dict.values())) == 0 else math.floor(
            4 / max(count_dict.values()))
        start_date = min(start_list)
        end_date = max(end_list)

        while start_date <= end_date:
            admin_date_list.append(start_date.strftime('%Y-%m-%d'))
            start_date += datetime.timedelta(days=1)
        for item in template_data:
            fake_date_list = []
            for date in admin_date_list:
                fake_date_list.append(date)
                if date in item['admin_date_list']:
                    date_list.append(date)

                if len(fake_date_list) == (settings.PACK_ROW if not is_bubble else settings.BUBBLE_PACK_ROW):
                    updated_item = item.copy()
                    updated_item['admin_date_list'] = date_list
                    if not date_list:
                        continue
                    result.append(updated_item)
                    if item['admin_date_list'] == date_list:
                        date_list = []
                        fake_date_list = []
                        break
                    date_list = []
                    fake_date_list = []
            if date_list:
                updated_item = item.copy()
                updated_item['admin_date_list'] = date_list
                result.append(updated_item)
                date_list = []
                fake_date_list = []
        result = sorted(result, key=lambda x: x['admin_date_list'][0])
        result = sorted(result, key=lambda x: x['hoa_time'])
        ordered_result = sorted(result, key=lambda x: len(x['admin_date_list']), reverse=True)
        unique_admin = []
        range_tuples = []
        unique_hoa = []

        t_data = sorted(ordered_result, key=lambda x: len(x['admin_date_list']), reverse=True)
        for admin_record in t_data:
            dates = admin_record['admin_date_list']
            if admin_record['hoa_time'] not in unique_hoa:
                unique_hoa.append(admin_record['hoa_time'])
            start_date = min(dates)
            end_date = max(dates)

            for date_range in range_tuples:
                if start_date >= date_range[0] and end_date <= date_range[1]:
                    break
            else:
                unique_admin.append(dates)
                range_tuples.append((start_date, end_date))

        unique_admin = sorted(unique_admin, key=lambda x: x[0])
        response = []
        sum_to_add = 0
        remaining_columns = 0
        prev_hoa = result[0]['hoa_time']
        column_number = 1
        buffer_columns = 0
        lag = 0
        columns_filled = {}
        prev_admin_index = 0
        columns_to_fit = 1
        for record in result:
            for i, sublist in enumerate(unique_admin):
                if set(record['admin_date_list']).issubset(sublist):
                    admin_index = i
                    break
            old_column_number = record['column_number']
            current_hoa = record['hoa_time']
            if current_hoa != prev_hoa:
                columns_filled = {}
                lag = record['column_number'] - 1
                buffer_columns = column_number + ((settings.PACK_COL - (
                            column_number % settings.PACK_COL)) if column_number % settings.PACK_COL else (
                            column_number % settings.PACK_COL))
                prev_hoa = current_hoa
                columns_to_fit = 0
            if prev_admin_index != admin_index:
                if columns_to_fit >= max_admin_in_one_pack:
                    columns_to_fit = 0
                    buffer_columns += ((settings.PACK_COL - (
                                column_number % settings.PACK_COL)) if column_number % settings.PACK_COL else (
                                column_number % settings.PACK_COL))
                if current_hoa == prev_hoa:
                    columns_to_fit += 1
                sum_to_add = sum(len(list(set(lst))) - 1 for lst in columns_filled.values())
                prev_admin_index = admin_index
            column_number = old_column_number - lag + sum_to_add + remaining_columns + buffer_columns + admin_index
            hoa_admin_tuple = (record['hoa_time'], record['admin_date_list'][0])
            if hoa_admin_tuple not in columns_filled:
                columns_filled[hoa_admin_tuple] = [column_number]
            else:
                columns_filled[hoa_admin_tuple].append(column_number)
            update_data = record.copy()
            update_data['column_number'] = column_number
            response.append(update_data)

        result = []
        dummy_template = response
        for item in response:
            dates = item['admin_date_list']

            modified_dates = []

            for date_range in unique_admin:
                if all(date in date_range for date in dates):
                    for date in dates:
                        f_index = date_range.index(date)
                        modified_dates.append(unique_admin[0][f_index])
                    break
            update_data = item.copy()
            update_data['admin_date_list'] = modified_dates
            result.append(update_data)
        return result, True, dummy_template

    except (IntegrityError, InternalError) as e:
        logger.error("Error in multi_seperate_pack_per_dose {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("Error in multi_seperate_pack_per_dose {}".format(e))
        return error(2001)


def update_reddis_data(company_id):
    try:
        update_pending_template_data_in_redisdb(company_id=company_id)
        return create_response(True)
    except RedisConnectionException as e:
        return create_response(True)
    except Exception as e:
        return create_response(True)


if __name__ == '__main__':
    # df print options
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # template = [{'quantity': 2.0, 'hoa_time': datetime.time(8, 0), 'pharmacy_rx_no': '573453', 'sig': 'Take 1 tablet by mouth daily', 'is_tapered': False, 'ndc': '00536404610', 'drug_name': 'MULTIVITAMIN', 'strength': '', 'formatted_ndc': '005364046', 'txr': '2532', 'strength_value': '', 'patient_rx_id': 1632, 'drug_id': 127580, 'image_name': 'ABC00578.JPG', 'color': 'red', 'shape': 'round', 'imprint': None, 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 1, 'canister_list': [{'canister_id': 1777, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '020088CB2869', 'robot_name': None, 'drug_name': 'MULTIVITAMIN', 'strength_value': '', 'strength': '', 'formatted_ndc': '005364046', 'txr': '2532', 'imprint': None, 'image_name': 'ABC00578.JPG', 'shape': 'round', 'color': 'red', 'manufacturer': 'RUGBY', 'ndc': '00536404610'}, {'canister_id': 1781, 'robot_id': 2, 'available_quantity': 326, 'canister_number': 64, 'rfid': '0200880B32B3', 'robot_name': 'Robot 1-2', 'drug_name': 'MULTIVITAMIN', 'strength_value': '', 'strength': '', 'formatted_ndc': '005364046', 'txr': '2532', 'imprint': None, 'image_name': 'ABC00578.JPG', 'shape': 'round', 'color': 'red', 'manufacturer': 'RUGBY', 'ndc': '00536404610'}, {'canister_id': 2128, 'robot_id': 3, 'available_quantity': 394, 'canister_number': 42, 'rfid': '03004EB0C03D', 'robot_name': 'Robot 2-2', 'drug_name': 'MULTIVITAMIN', 'strength_value': '', 'strength': '', 'formatted_ndc': '005364046', 'txr': '2532', 'imprint': None, 'image_name': 'ABC00578.JPG', 'shape': 'round', 'color': 'red', 'manufacturer': 'RUGBY', 'ndc': '00536404610'}, {'canister_id': 3198, 'robot_id': 3, 'available_quantity': 516, 'canister_number': 170, 'rfid': '4400631F152D', 'robot_name': 'Robot 2-2', 'drug_name': 'MULTIVITAMIN', 'strength_value': '', 'strength': '', 'formatted_ndc': '005364046', 'txr': '2532', 'imprint': None, 'image_name': 'ABC00578.JPG', 'shape': 'round', 'color': 'red', 'manufacturer': 'RUGBY', 'ndc': '00536404610'}], 'pack_no': 1, 'display_time': '08:00 AM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'MULTIVITAMIN', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(8, 0), 'pharmacy_rx_no': '548636', 'sig': 'Take 1 tablet by mouth every morning', 'is_tapered': False, 'ndc': '31722082030', 'drug_name': 'ARIPIPRAZOLE', 'strength': 'MG', 'formatted_ndc': '317220820', 'txr': '52898', 'strength_value': '5', 'patient_rx_id': 1633, 'drug_id': 111449, 'image_name': 'CBR08200.JPG', 'color': 'light blue', 'shape': 'rectangular', 'imprint': 'I <> 95', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 1, 'canister_list': [], 'pack_no': 1, 'display_time': '08:00 AM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'ARIPIPRAZOLE', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(8, 0), 'pharmacy_rx_no': '573456', 'sig': 'Take 1 tablet by mouth daily', 'is_tapered': False, 'ndc': '69097012715', 'drug_name': 'AMLODIPINE BESYLATE', 'strength': 'MG', 'formatted_ndc': '690970127', 'txr': '16926', 'strength_value': '5', 'patient_rx_id': 1634, 'drug_id': 112188, 'image_name': 'CIP01270.JPG', 'color': 'white', 'shape': 'round', 'imprint': '127 <> C', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 1, 'canister_list': [], 'pack_no': 1, 'display_time': '08:00 AM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'AMLODIPINE', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(8, 0), 'pharmacy_rx_no': '573454', 'sig': 'Take 1 tablet by mouth 2 times daily', 'is_tapered': False, 'ndc': '43547033650', 'drug_name': 'BENAZEPRIL HCL', 'strength': 'MG', 'formatted_ndc': '435470336', 'txr': '16040', 'strength_value': '10', 'patient_rx_id': 1636, 'drug_id': 100971, 'image_name': 'SLC03360.JPG', 'color': 'red', 'shape': 'round', 'imprint': 'S <> 342', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 1, 'canister_list': [{'canister_id': 2779, 'robot_id': 3, 'available_quantity': 17, 'canister_number': 174, 'rfid': '4400631F427A', 'robot_name': 'Robot 2-2', 'drug_name': 'BENAZEPRIL HCL', 'strength_value': '10', 'strength': 'MG', 'formatted_ndc': '435470336', 'txr': '16040', 'imprint': 'S <> 342', 'image_name': 'SLC03360.JPG', 'shape': 'round', 'color': 'red', 'manufacturer': 'SOLCO HEALTHCAR', 'ndc': '43547033650'}], 'pack_no': 1, 'display_time': '08:00 AM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'BENAZEPRIL', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(8, 0), 'pharmacy_rx_no': '548635', 'sig': 'Take 1 tablet by mouth every morning (also taking 10mg, total of 30mg)', 'is_tapered': False, 'ndc': '13668013705', 'drug_name': 'ESCITALOPRAM OXALATE', 'strength': 'MG', 'formatted_ndc': '136680137', 'txr': '50760', 'strength_value': '20', 'patient_rx_id': 1639, 'drug_id': 27703, 'image_name': 'TOR01370.JPG', 'color': 'white', 'shape': 'round', 'imprint': '11  37 <> 20', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 1, 'canister_list': [{'canister_id': 2241, 'robot_id': 2, 'available_quantity': 61, 'canister_number': 215, 'rfid': '02008803D950', 'robot_name': 'Robot 1-2', 'drug_name': 'ESCITALOPRAM OXALATE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '136680137', 'txr': '50760', 'imprint': '11  37 <> 20', 'image_name': 'TOR01370.JPG', 'shape': 'round', 'color': 'white', 'manufacturer': 'TORRENT PHARMAC', 'ndc': '13668013701'}], 'pack_no': 1, 'display_time': '08:00 AM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'ESCITALOPRAM', 'file_id': 269}, {'quantity': 3.5, 'hoa_time': datetime.time(8, 0), 'pharmacy_rx_no': '573457', 'sig': 'Take 1 capsule by mouth daily', 'is_tapered': False, 'ndc': '00536106410', 'drug_name': 'STOOL SOFTENER', 'strength': 'MG', 'formatted_ndc': '005361064', 'txr': '3011', 'strength_value': '250', 'patient_rx_id': 1641, 'drug_id': 112538, 'image_name': 'GNP02630.JPG', 'color': 'orange-red', 'shape': 'oblong', 'imprint': 'P20', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 1, 'canister_list': [{'canister_id': 1866, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '03004EE8D97C', 'robot_name': None, 'drug_name': 'DOCUSATE STOOL SOFTENER', 'strength_value': '250', 'strength': 'MG', 'formatted_ndc': '005361064', 'txr': '3011', 'imprint': 'P20', 'image_name': 'GNP02630.JPG', 'shape': 'oblong', 'color': 'orange-red', 'manufacturer': 'RUGBY', 'ndc': '00536106401'}, {'canister_id': 1960, 'robot_id': 3, 'available_quantity': 494, 'canister_number': 28, 'rfid': '0200882563CC', 'robot_name': 'Robot 2-2', 'drug_name': 'DOCUSATE STOOL SOFTENER', 'strength_value': '250', 'strength': 'MG', 'formatted_ndc': '005361064', 'txr': '3011', 'imprint': 'P20', 'image_name': 'GNP02630.JPG', 'shape': 'oblong', 'color': 'orange-red', 'manufacturer': 'RUGBY', 'ndc': '00536106401'}, {'canister_id': 2142, 'robot_id': None, 'available_quantity': 500, 'canister_number': 0, 'rfid': '02008897A6BB', 'robot_name': None, 'drug_name': 'DOCUSATE STOOL SOFTENER', 'strength_value': '250', 'strength': 'MG', 'formatted_ndc': '005361064', 'txr': '3011', 'imprint': 'P20', 'image_name': 'GNP02630.JPG', 'shape': 'oblong', 'color': 'orange-red', 'manufacturer': 'RUGBY', 'ndc': '00536106401'}, {'canister_id': 2149, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '0300531B5318', 'robot_name': None, 'drug_name': 'DOCUSATE STOOL SOFTENER', 'strength_value': '250', 'strength': 'MG', 'formatted_ndc': '005361064', 'txr': '3011', 'imprint': 'P20', 'image_name': 'GNP02630.JPG', 'shape': 'oblong', 'color': 'orange-red', 'manufacturer': 'RUGBY', 'ndc': '00536106401'}, {'canister_id': 2160, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '03004EF414AD', 'robot_name': None, 'drug_name': 'DOCUSATE STOOL SOFTENER', 'strength_value': '250', 'strength': 'MG', 'formatted_ndc': '005361064', 'txr': '3011', 'imprint': 'P20', 'image_name': 'GNP02630.JPG', 'shape': 'oblong', 'color': 'orange-red', 'manufacturer': 'RUGBY', 'ndc': '00536106401'}, {'canister_id': 2178, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '0300529DE72B', 'robot_name': None, 'drug_name': 'DOCUSATE STOOL SOFTENER', 'strength_value': '250', 'strength': 'MG', 'formatted_ndc': '005361064', 'txr': '3011', 'imprint': 'P20', 'image_name': 'GNP02630.JPG', 'shape': 'oblong', 'color': 'orange-red', 'manufacturer': 'RUGBY', 'ndc': '00536106401'}, {'canister_id': 2209, 'robot_id': 2, 'available_quantity': 380, 'canister_number': 32, 'rfid': '02008BF088F1', 'robot_name': 'Robot 1-2', 'drug_name': 'DOCUSATE STOOL SOFTENER', 'strength_value': '250', 'strength': 'MG', 'formatted_ndc': '005361064', 'txr': '3011', 'imprint': 'P20', 'image_name': 'GNP02630.JPG', 'shape': 'oblong', 'color': 'orange-red', 'manufacturer': 'RUGBY', 'ndc': '00536106401'}, {'canister_id': 2770, 'robot_id': 3, 'available_quantity': -112, 'canister_number': 39, 'rfid': '4400631D7F45', 'robot_name': 'Robot 2-2', 'drug_name': 'STOOL SOFTENER', 'strength_value': '250', 'strength': 'MG', 'formatted_ndc': '005361064', 'txr': '3011', 'imprint': 'P20', 'image_name': 'GNP02630.JPG', 'shape': 'oblong', 'color': 'orange-red', 'manufacturer': 'RUGBY', 'ndc': '00536106410'}, {'canister_id': 3204, 'robot_id': None, 'available_quantity': -117, 'canister_number': 0, 'rfid': '030052FD14B8', 'robot_name': None, 'drug_name': 'STOOL SOFTENER', 'strength_value': '250', 'strength': 'MG', 'formatted_ndc': '005361064', 'txr': '3011', 'imprint': 'P20', 'image_name': 'GNP02630.JPG', 'shape': 'oblong', 'color': 'orange-red', 'manufacturer': 'RUGBY', 'ndc': '00536106410'}], 'pack_no': 1, 'display_time': '08:00 AM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'STOOL', 'file_id': 269}, {'quantity': 6.0, 'hoa_time': datetime.time(8, 0), 'pharmacy_rx_no': '573442', 'sig': 'Take 1 tablet by mouth once daily', 'is_tapered': False, 'ndc': '69315090510', 'drug_name': 'LORAZEPAM', 'strength': 'MG', 'formatted_ndc': '693150905', 'txr': '3758', 'strength_value': '1', 'patient_rx_id': 1642, 'drug_id': 117527, 'image_name': 'MJR60080.JPG', 'color': 'white', 'shape': 'round', 'imprint': 'EP  905 <> 1', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 1, 'canister_list': [{'canister_id': 2238, 'robot_id': 2, 'available_quantity': 300, 'canister_number': 163, 'rfid': '03004FBF39CA', 'robot_name': 'Robot 1-2', 'drug_name': 'LORAZEPAM', 'strength_value': '1', 'strength': 'mg', 'formatted_ndc': '693150905', 'txr': '3758', 'imprint': 'EP  905 <> 1', 'image_name': 'MJR60080.JPG', 'shape': 'round', 'color': 'white', 'manufacturer': 'LEADING PHARMA', 'ndc': '69315090501'}, {'canister_id': 3214, 'robot_id': 2, 'available_quantity': -110, 'canister_number': 138, 'rfid': '600076839702', 'robot_name': 'Robot 1-2', 'drug_name': 'LORAZEPAM', 'strength_value': '1', 'strength': 'MG', 'formatted_ndc': '693150905', 'txr': '3758', 'imprint': 'EP  905 <> 1', 'image_name': 'MJR60080.JPG', 'shape': 'round', 'color': 'white', 'manufacturer': 'LEADING PHARMA', 'ndc': '69315090510'}], 'pack_no': 1, 'display_time': '08:00 AM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'LORAZEPAM', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(8, 0), 'pharmacy_rx_no': '548637', 'sig': 'Take 1 tablet by mouth every morning (also taking 20mg, total of 30mg)', 'is_tapered': False, 'ndc': '16729016917', 'drug_name': 'ESCITALOPRAM OXALATE', 'strength': 'MG', 'formatted_ndc': '167290169', 'txr': '50712', 'strength_value': '10', 'patient_rx_id': 1643, 'drug_id': 32047, 'image_name': 'ACI01690.JPG', 'color': 'white', 'shape': 'round', 'imprint': '10', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 1, 'canister_list': [], 'pack_no': 1, 'display_time': '08:00 AM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'ESCITALOPRAM', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(21, 0), 'pharmacy_rx_no': '552812', 'sig': 'dissolve on tongue and swallow 1 tablet by mouth at bedtime (with 20mg tablet form for total dose of 40mg at bedtime)', 'is_tapered': False, 'ndc': '60505327803', 'drug_name': 'OLANZAPINE ODT', 'strength': 'MG', 'formatted_ndc': '605053278', 'txr': '47286', 'strength_value': '20', 'patient_rx_id': 1630, 'drug_id': 76850, 'image_name': 'ATX32780.JPG', 'color': 'yellow', 'shape': 'round', 'imprint': 'APO <> OL  20', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 2, 'canister_list': [{'canister_id': 2189, 'robot_id': 2, 'available_quantity': 2, 'canister_number': 202, 'rfid': '020088ED4423', 'robot_name': 'Robot 1-2', 'drug_name': 'OLANZAPINE ODT', 'strength_value': '20', 'strength': 'MG', 'formatted_ndc': '605053278', 'txr': '47286', 'imprint': 'APO <> OL  20', 'image_name': 'ATX32780.JPG', 'shape': 'round', 'color': 'yellow', 'manufacturer': 'APOTEX CORP', 'ndc': '60505327800'}], 'pack_no': 1, 'display_time': '09:00 PM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'OLANZAPINE', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(21, 0), 'pharmacy_rx_no': '573452', 'sig': 'Take 1 tablet by mouth daily (with 10mg, total daily dose of 30mg)', 'is_tapered': False, 'ndc': '68180047903', 'drug_name': 'SIMVASTATIN', 'strength': 'MG', 'formatted_ndc': '681800479', 'txr': '16578', 'strength_value': '20', 'patient_rx_id': 1631, 'drug_id': 95410, 'image_name': 'LUP04790.JPG', 'color': 'tan', 'shape': 'oval', 'imprint': 'LL <> C03', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 2, 'canister_list': [{'canister_id': 1852, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '02008896FBE7', 'robot_name': None, 'drug_name': 'SIMVASTATIN', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '681800479', 'txr': '16578', 'imprint': 'LL <> C03', 'image_name': 'LUP04790.JPG', 'shape': 'oval', 'color': 'tan', 'manufacturer': 'LUPIN PHARMACEU', 'ndc': '68180047901'}, {'canister_id': 1940, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '0200884EDF1B', 'robot_name': None, 'drug_name': 'SIMVASTATIN', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '681800479', 'txr': '16578', 'imprint': 'LL <> C03', 'image_name': 'LUP04790.JPG', 'shape': 'oval', 'color': 'tan', 'manufacturer': 'LUPIN PHARMACEU', 'ndc': '68180047901'}, {'canister_id': 1976, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '020088BE2216', 'robot_name': None, 'drug_name': 'SIMVASTATIN', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '681800479', 'txr': '16578', 'imprint': 'LL <> C03', 'image_name': 'LUP04790.JPG', 'shape': 'oval', 'color': 'tan', 'manufacturer': 'LUPIN PHARMACEU', 'ndc': '68180047901'}, {'canister_id': 1997, 'robot_id': 2, 'available_quantity': 129, 'canister_number': 164, 'rfid': '440062FC459F', 'robot_name': 'Robot 1-2', 'drug_name': 'SIMVASTATIN', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '681800479', 'txr': '16578', 'imprint': 'LL <> C03', 'image_name': 'LUP04790.JPG', 'shape': 'oval', 'color': 'tan', 'manufacturer': 'LUPIN PHARMACEU', 'ndc': '68180047901'}, {'canister_id': 2006, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '0200880CE264', 'robot_name': None, 'drug_name': 'SIMVASTATIN', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '681800479', 'txr': '16578', 'imprint': 'LL <> C03', 'image_name': 'LUP04790.JPG', 'shape': 'oval', 'color': 'tan', 'manufacturer': 'LUPIN PHARMACEU', 'ndc': '68180047901'}, {'canister_id': 2052, 'robot_id': 3, 'available_quantity': 138, 'canister_number': 31, 'rfid': '0200768CBA42', 'robot_name': 'Robot 2-2', 'drug_name': 'SIMVASTATIN', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '681800479', 'txr': '16578', 'imprint': 'LL <> C03', 'image_name': 'LUP04790.JPG', 'shape': 'oval', 'color': 'tan', 'manufacturer': 'LUPIN PHARMACEU', 'ndc': '68180047901'}, {'canister_id': 2186, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '02008BB90434', 'robot_name': None, 'drug_name': 'SIMVASTATIN', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '681800479', 'txr': '16578', 'imprint': 'LL <> C03', 'image_name': 'LUP04790.JPG', 'shape': 'oval', 'color': 'tan', 'manufacturer': 'LUPIN PHARMACEU', 'ndc': '68180047901'}, {'canister_id': 2743, 'robot_id': 2, 'available_quantity': -110, 'canister_number': 115, 'rfid': '440062DF45BC', 'robot_name': 'Robot 1-2', 'drug_name': 'SIMVASTATIN', 'strength_value': '20', 'strength': 'MG', 'formatted_ndc': '681800479', 'txr': '16578', 'imprint': 'LL <> C03', 'image_name': 'LUP04790.JPG', 'shape': 'oval', 'color': 'tan', 'manufacturer': 'LUPIN PHARMACEU', 'ndc': '68180047903'}], 'pack_no': 1, 'display_time': '09:00 PM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'SIMVASTATIN', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(21, 0), 'pharmacy_rx_no': '548634', 'sig': 'Take 1 tablet by mouth at bedtime', 'is_tapered': False, 'ndc': '50111043302', 'drug_name': 'TRAZODONE HCL', 'strength': 'MG', 'formatted_ndc': '501110433', 'txr': '46241', 'strength_value': '50', 'patient_rx_id': 1635, 'drug_id': 51796, 'image_name': 'SMK04330.JPG', 'color': 'white', 'shape': 'round', 'imprint': 'PLIVA  433', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 2, 'canister_list': [{'canister_id': 2697, 'robot_id': 3, 'available_quantity': 86, 'canister_number': 80, 'rfid': '440062879A3B', 'robot_name': 'Robot 2-2', 'drug_name': 'TRAZODONE HCL', 'strength_value': '50', 'strength': 'MG', 'formatted_ndc': '501110433', 'txr': '46241', 'imprint': 'PLIVA  433', 'image_name': 'SMK04330.JPG', 'shape': 'round', 'color': 'white', 'manufacturer': 'TEVA USA', 'ndc': '50111043303'}, {'canister_id': 2852, 'robot_id': 2, 'available_quantity': 288, 'canister_number': 158, 'rfid': '440063009BBC', 'robot_name': 'Robot 1-2', 'drug_name': 'TRAZODONE HCL', 'strength_value': '50', 'strength': 'MG', 'formatted_ndc': '501110433', 'txr': '46241', 'imprint': 'PLIVA  433', 'image_name': 'SMK04330.JPG', 'shape': 'round', 'color': 'white', 'manufacturer': 'TEVA USA', 'ndc': '50111043302'}], 'pack_no': 1, 'display_time': '09:00 PM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'TRAZODONE', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(21, 0), 'pharmacy_rx_no': '573454', 'sig': 'Take 1 tablet by mouth 2 times daily', 'is_tapered': False, 'ndc': '43547033650', 'drug_name': 'BENAZEPRIL HCL', 'strength': 'MG', 'formatted_ndc': '435470336', 'txr': '16040', 'strength_value': '10', 'patient_rx_id': 1636, 'drug_id': 100971, 'image_name': 'SLC03360.JPG', 'color': 'red', 'shape': 'round', 'imprint': 'S <> 342', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 2, 'canister_list': [{'canister_id': 2779, 'robot_id': 3, 'available_quantity': 17, 'canister_number': 174, 'rfid': '4400631F427A', 'robot_name': 'Robot 2-2', 'drug_name': 'BENAZEPRIL HCL', 'strength_value': '10', 'strength': 'MG', 'formatted_ndc': '435470336', 'txr': '16040', 'imprint': 'S <> 342', 'image_name': 'SLC03360.JPG', 'shape': 'round', 'color': 'red', 'manufacturer': 'SOLCO HEALTHCAR', 'ndc': '43547033650'}], 'pack_no': 1, 'display_time': '09:00 PM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'BENAZEPRIL', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(21, 0), 'pharmacy_rx_no': '573455', 'sig': 'Take 1 tablet by mouth daily (with 20mg, total daily dose of 30mg)', 'is_tapered': False, 'ndc': '68180047803', 'drug_name': 'SIMVASTATIN', 'strength': 'MG', 'formatted_ndc': '681800478', 'txr': '16577', 'strength_value': '10', 'patient_rx_id': 1637, 'drug_id': 95407, 'image_name': 'LUP04780.JPG', 'color': 'peach', 'shape': 'oval', 'imprint': 'C02 <> LL', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 2, 'canister_list': [{'canister_id': 2993, 'robot_id': 2, 'available_quantity': 153, 'canister_number': 108, 'rfid': '440062C58261', 'robot_name': 'Robot 1-2', 'drug_name': 'SIMVASTATIN', 'strength_value': '10', 'strength': 'MG', 'formatted_ndc': '681800478', 'txr': '16577', 'imprint': 'C02 <> LL', 'image_name': 'LUP04780.JPG', 'shape': 'oval', 'color': 'peach', 'manufacturer': 'LUPIN PHARMACEU', 'ndc': '68180047803'}], 'pack_no': 1, 'display_time': '09:00 PM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'SIMVASTATIN', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(21, 0), 'pharmacy_rx_no': '573441', 'sig': 'Take 1 tablet by mouth at bedtime', 'is_tapered': False, 'ndc': '00955170310', 'drug_name': 'ZOLPIDEM TARTRATE ER', 'strength': 'MG', 'formatted_ndc': '009551703', 'txr': '59697', 'strength_value': '12.5', 'patient_rx_id': 1638, 'drug_id': 19239, 'image_name': 'SAN17030.JPG', 'color': 'blue', 'shape': 'round', 'imprint': 'ZCR', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 2, 'canister_list': [], 'pack_no': 1, 'display_time': '09:00 PM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'ZOLPIDEM ER', 'file_id': 269}, {'quantity': 1.0, 'hoa_time': datetime.time(21, 0), 'pharmacy_rx_no': '552813', 'sig': 'Take 1 tablet by mouth at bedtime (with 20m ODT form for total dose of 40mg at bedtime)', 'is_tapered': False, 'ndc': '60505314008', 'drug_name': 'OLANZAPINE', 'strength': 'MG', 'formatted_ndc': '605053140', 'txr': '41027', 'strength_value': '20', 'patient_rx_id': 1640, 'drug_id': 76824, 'image_name': 'ATX31400.JPG', 'color': 'light pink', 'shape': 'elliptical', 'imprint': 'APO <> OLA 20', 'patient_id': 238, 'admin_date_list': ['2019-07-30', '2019-07-31', '2019-08-01', '2019-08-02', '2019-08-03', '2019-08-04', '2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', '2019-08-10', '2019-08-11', '2019-08-12'], 'column_number': 2, 'canister_list': [{'canister_id': 1820, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '02004EE82387', 'robot_name': None, 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 1891, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '0200880B38B9', 'robot_name': None, 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 1895, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '02008BE52E42', 'robot_name': None, 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 1898, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '020088C7DD90', 'robot_name': None, 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 1917, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '020088F17803', 'robot_name': None, 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 1999, 'device_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '0200885905D6', 'robot_name': None, 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 2009, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '020088688062', 'robot_name': None, 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 2013, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '020088C897D5', 'robot_name': None, 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 2048, 'robot_id': 2, 'available_quantity': -139, 'canister_number': 31, 'rfid': '02008B9BD6C4', 'robot_name': 'Robot 1-2', 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 2204, 'robot_id': 3, 'available_quantity': 431, 'canister_number': 40, 'rfid': '02008BE2FD96', 'robot_name': 'Robot 2-2', 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 2212, 'robot_id': None, 'available_quantity': 0, 'canister_number': 0, 'rfid': '02004EFCED5D', 'robot_name': None, 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}, {'canister_id': 2249, 'robot_id': 3, 'available_quantity': 313, 'canister_number': 243, 'rfid': '0200885BD203', 'robot_name': 'Robot 2-2', 'drug_name': 'OLANZAPINE', 'strength_value': '20', 'strength': 'mg', 'formatted_ndc': '605053140', 'txr': '41027', 'imprint': 'APO <> OLA 20', 'image_name': 'ATX31400.JPG', 'shape': 'elliptical', 'color': 'light pink', 'manufacturer': 'APOTEX CORP', 'ndc': '60505314000'}], 'pack_no': 1, 'display_time': '09:00 PM', 'modified_time': '2019-07-30T12:11:38.098353', 'short_drug_name': 'OLANZAPINE', 'file_id': 269}]
    # drug_dimension = {('005361064', '3011'): {'id': 1, 'formatted_ndc': '005361064', 'txr': '3011', 'drug_id': 111776, 'unique_drug_id': 13020, 'width': Decimal('7.380'), 'length': Decimal('20.070'), 'depth': Decimal('7.380'), 'fillet': Decimal('0.000'), 'approx_volume': Decimal('1093.100508'), 'accurate_volume': Decimal('753.290000'), 'shape': 1, 'created_date': datetime.datetime(2018, 10, 22, 14, 4, 40), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 35), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2018, 10, 22, 14, 4, 40)}, ('681800479', '16578'): {'id': 7, 'formatted_ndc': '681800479', 'txr': '16578', 'drug_id': 95408, 'unique_drug_id': 95554, 'width': Decimal('6.440'), 'length': Decimal('11.220'), 'depth': Decimal('3.520'), 'fillet': Decimal('2.370'), 'approx_volume': Decimal('254.343936'), 'accurate_volume': Decimal('162.920000'), 'shape': 4, 'created_date': datetime.datetime(2018, 10, 22, 14, 4, 45), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 38), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2018, 10, 22, 14, 4, 45)}, ('605053140', '41027'): {'id': 11, 'formatted_ndc': '605053140', 'txr': '41027', 'drug_id': 76822, 'unique_drug_id': 81149, 'width': Decimal('7.250'), 'length': Decimal('12.910'), 'depth': Decimal('4.260'), 'fillet': Decimal('2.440'), 'approx_volume': Decimal('398.725350'), 'accurate_volume': Decimal('237.600000'), 'shape': 4, 'created_date': datetime.datetime(2018, 10, 22, 14, 4, 47), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 38), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2018, 10, 22, 14, 4, 47)}, ('005364046', '2532'): {'id': 12, 'formatted_ndc': '005364046', 'txr': '2532', 'drug_id': 127580, 'unique_drug_id': 13179, 'width': Decimal('8.170'), 'length': Decimal('8.170'), 'depth': Decimal('4.560'), 'fillet': Decimal('3.150'), 'approx_volume': Decimal('304.374984'), 'accurate_volume': None, 'shape': 5, 'created_date': datetime.datetime(2018, 10, 22, 14, 4, 48), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 36), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2018, 10, 22, 14, 4, 48)}, ('501110433', '46241'): {'id': 27, 'formatted_ndc': '501110433', 'txr': '46241', 'drug_id': 51795, 'unique_drug_id': 57585, 'width': Decimal('8.840'), 'length': Decimal('8.840'), 'depth': Decimal('4.500'), 'fillet': Decimal('2.860'), 'approx_volume': Decimal('351.655200'), 'accurate_volume': None, 'shape': 5, 'created_date': datetime.datetime(2018, 10, 22, 14, 5, 1), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 36), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2018, 10, 22, 14, 5, 1)}, ('681800478', '16577'): {'id': 67, 'formatted_ndc': '681800478', 'txr': '16577', 'drug_id': 95405, 'unique_drug_id': 95553, 'width': Decimal('5.140'), 'length': Decimal('8.610'), 'depth': Decimal('2.510'), 'fillet': Decimal('2.100'), 'approx_volume': Decimal('111.081054'), 'accurate_volume': Decimal('79.180000'), 'shape': 4, 'created_date': datetime.datetime(2018, 10, 22, 14, 5, 31), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 38), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2018, 10, 22, 14, 5, 31)}, ('435470336', '16040'): {'id': 256, 'formatted_ndc': '435470336', 'txr': '16040', 'drug_id': 100970, 'unique_drug_id': 50824, 'width': Decimal('8.170'), 'length': Decimal('8.170'), 'depth': Decimal('3.910'), 'fillet': Decimal('2.530'), 'approx_volume': Decimal('260.988199'), 'accurate_volume': None, 'shape': 5, 'created_date': datetime.datetime(2018, 10, 22, 14, 7, 52), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 37), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2018, 10, 22, 14, 7, 52)}, ('167290169', '50712'): {'id': 475, 'formatted_ndc': '167290169', 'txr': '50712', 'drug_id': 32046, 'unique_drug_id': 33907, 'width': Decimal('7.290'), 'length': Decimal('7.290'), 'depth': Decimal('3.220'), 'fillet': Decimal('3.130'), 'approx_volume': Decimal('171.124002'), 'accurate_volume': None, 'shape': 5, 'created_date': datetime.datetime(2019, 5, 7, 11, 17, 37), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 37), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2019, 5, 7, 11, 17, 37)}, ('136680137', '50760'): {'id': 487, 'formatted_ndc': '136680137', 'txr': '50760', 'drug_id': 27702, 'unique_drug_id': 31572, 'width': Decimal('9.640'), 'length': Decimal('9.640'), 'depth': Decimal('3.850'), 'fillet': Decimal('3.490'), 'approx_volume': Decimal('357.778960'), 'accurate_volume': None, 'shape': 5, 'created_date': datetime.datetime(2019, 5, 7, 11, 17, 37), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 37), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2019, 5, 7, 11, 17, 37)}, ('690970127', '16926'): {'id': 497, 'formatted_ndc': '690970127', 'txr': '16926', 'drug_id': 112187, 'unique_drug_id': 97318, 'width': Decimal('7.540'), 'length': Decimal('7.540'), 'depth': Decimal('2.850'), 'fillet': Decimal('2.430'), 'approx_volume': Decimal('162.027060'), 'accurate_volume': None, 'shape': 5, 'created_date': datetime.datetime(2019, 5, 7, 11, 17, 37), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 37), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2019, 5, 7, 11, 17, 37)}, ('693150905', '3758'): {'id': 515, 'formatted_ndc': '693150905', 'txr': '3758', 'drug_id': 117525, 'unique_drug_id': 97568, 'width': Decimal('2.460'), 'length': Decimal('7.200'), 'depth': Decimal('7.200'), 'fillet': Decimal('2.460'), 'approx_volume': Decimal('127.526400'), 'accurate_volume': None, 'shape': 6, 'created_date': datetime.datetime(2019, 5, 7, 11, 17, 38), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 38), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2019, 5, 7, 11, 17, 38)}, ('605053278', '47286'): {'id': 516, 'formatted_ndc': '605053278', 'txr': '47286', 'drug_id': 76849, 'unique_drug_id': 81170, 'width': Decimal('2.890'), 'length': Decimal('8.800'), 'depth': Decimal('8.800'), 'fillet': Decimal('2.890'), 'approx_volume': Decimal('223.801600'), 'accurate_volume': None, 'shape': 6, 'created_date': datetime.datetime(2019, 5, 7, 11, 17, 38), 'modified_date': datetime.datetime(2019, 5, 7, 11, 17, 38), 'created_by': 1, 'modified_by': 1, 'verified': True, 'verified_by': 1, 'verified_date': datetime.datetime(2019, 5, 7, 11, 17, 38)}, ('317220820', '52898'): {'id': 560, 'formatted_ndc': '317220820', 'txr': '52898', 'drug_id': 111449, 'unique_drug_id': 39713, 'width': Decimal('4.657'), 'length': Decimal('8.221'), 'depth': Decimal('2.613'), 'fillet': Decimal('1.659'), 'approx_volume': Decimal('100.039220'), 'accurate_volume': None, 'shape': 4, 'created_date': datetime.datetime(2019, 6, 23, 0, 17, 6), 'modified_date': datetime.datetime(2019, 6, 23, 0, 17, 6), 'created_by': 7, 'modified_by': 7, 'verified': True, 'verified_by': 7, 'verified_date': datetime.datetime(2019, 6, 23, 0, 17, 6)}, ('009551703', '59697'): {'id': 669, 'formatted_ndc': '009551703', 'txr': '59697', 'drug_id': 19239, 'unique_drug_id': 17831, 'width': Decimal('8.240'), 'length': Decimal('8.240'), 'depth': Decimal('4.664'), 'fillet': Decimal('4.044'), 'approx_volume': Decimal('316.674406'), 'accurate_volume': None, 'shape': 5, 'created_date': datetime.datetime(2019, 6, 28, 23, 31, 5), 'modified_date': datetime.datetime(2019, 6, 28, 23, 31, 5), 'created_by': 7, 'modified_by': 7, 'verified': True, 'verified_by': 7, 'verified_date': datetime.datetime(2019, 6, 28, 23, 31, 5)}}
    # separate_drug_list = {'005364046#2532'}
    # template_data = prepare_template_data_for_df(template, drug_dimension, separate_drug_list)
    # template, df1, s1 = split_separate_drugs(template, separate_drug_list)
    # template, df2, s2, _ = split_template_by_volume(template, drug_dimension, split_config={
    #     'SLOT_VOLUME_THRESHOLD_MARK': 0.53,
    #     # 'SLOT_VOLUME_THRESHOLD_MARK': 0.53,
    # })
    # print("split column hoa's", s1.union(s2))
    # print('====='*5)
    # print('df 1', df1)
    # print('====='*5)
    # print('df 2', df2)
