import csv
import json
import os
import sys
from io import StringIO

import cherrypy
import pytz

import settings
import datetime
from collections import defaultdict
from peewee import InternalError, IntegrityError, DoesNotExist, fn
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.local.lang_us_en import err
from dosepack.utilities.utils import convert_date_to_sql_datetime, get_current_date_time, log_args_and_response, \
    get_utc_time_offset_by_time_zone, get_current_date_time_as_per_time_zone
from dosepack.validation.validate import validate
from src import constants
from src.dao.print_dao import get_print_count
from src.dao.subscription_dao import get_orders_by_company_id, get_orders_by_date, create_order_record, \
    create_order_details_multiple_record, create_order_status_track, update_orders, track_consumable_quantity, \
    get_order_summary_data, get_active_consumables, get_couriers_data, get_consumables_types, get_monthly_stats, \
    create_shipment_tracker_record, create_order_document, get_date_of_last_sent_consumable_data, \
    insert_into_consumable_sent_data_dao
from src.dao.pack_dao import get_filled_pack_count_by_date
from src.exceptions import InventoryBadRequestException, InventoryDataNotFoundException, InventoryBadStatusCode, \
    InventoryConnectionException, InvalidResponseFromInventory
from src.model.model_pack_fill_error_v2 import PackFillErrorV2
from utils.auth_webservices import send_email_update_used_consumable_failure, send_email_monthly_consumable_data
from utils.inventory_webservices import inventory_api_call

logger = settings.logger


@validate(required_fields=["from_date", "to_date", "company_id"])
def get_subscription_orders(search_filters):
    """
        Fetches records of orders based on filter criteria
        :param search_filters: search filters to filter all the orders record
        :return:
    """
    orders_list: list = list()
    from_date, to_date = convert_date_to_sql_datetime(search_filters['from_date'], search_filters['to_date'])
    company_id = search_filters["company_id"]
    try:
        if company_id is not None:
            order_values_list = get_orders_by_company_id(company_id, from_date, to_date)
            for record in order_values_list:
                orders_list.append(record)
        else:
            order_values_list = get_orders_by_date(from_date, to_date)
            for record in order_values_list:
                orders_list.append(record)
        logger.info("In get_subscription_orders: orders_list :{}".format(orders_list))
        return create_response(orders_list)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_subscription_orders {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_subscription_orders: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_subscription_orders {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in find_pack_id_by_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_subscription_orders: " + str(e))


@validate(required_fields=["company_id", "user_id", "company_code", "consumables"])
def add_subscription_order(dict_order_info):
    """
    Makes Entry in Orders and OrderDetails with given data
    :param dict_order_info: required data for order entry
    :return: json
    """
    if not dict_order_info["consumables"]:
        return error(1020)

    current_datetime = datetime.datetime.utcnow()
    dict_order_info["inquiry_no"] = str(dict_order_info["company_code"])
    dict_order_info["inquiry_no"] += "-" + current_datetime.strftime(settings.INQUIRY_NO_FORMAT_SUFFIX)  # company_code-timestamp

    logger.info("In add_subscription_order: dict_order_info: {}".format(dict_order_info))
    order_insert_dict = create_order_insert_dict(dict_order_info)
    with db.transaction():
        try:
            order_record = create_order_record(order_insert_dict=order_insert_dict)
            logger.info("In add_subscription_order: record:{]".format(order_record))
            for item in dict_order_info["consumables"]:
                item["order_id"] = order_record.id

            order_details_record = create_order_details_multiple_record(order_details_insert_dict=dict_order_info["consumables"])
            logger.info("In add_subscription_order: order_details_record: {}".format(order_details_record))

            order_status_tracker_record = create_order_status_track(order_record.id, settings.INQUIRY_DEFAULT_STATUS, dict_order_info["user_id"])
            logger.info("In add_subscription_order: order_status_tracker_record: {}".format(order_status_tracker_record))

            return create_response(order_record.id)

        except (InternalError, IntegrityError) as e:
            logger.error("error in add_subscription_order {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in add_subscription_order: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(2001)

        except Exception as e:
            logger.error("Error in add_subscription_order {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in add_subscription_order: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in add_subscription_order: " + str(e))


def create_order_insert_dict(dict_order_info):
    payment_link = dict_order_info.get("payment_link", None)

    return {"company_id": dict_order_info["company_id"],
            "inquiry_no": dict_order_info["inquiry_no"],
            "status": settings.INQUIRY_DEFAULT_STATUS,
            "payment_link": payment_link,
            "inquired_by": dict_order_info["user_id"],
            "created_by": dict_order_info["user_id"],
            "modified_by": dict_order_info["user_id"]}


@validate(required_fields=["order_id", "user_id"])
def update_subscription_order(dict_order_info):
    """
    Updates order data by id
    :param dict_order_info:
    :return:
    """
    with db.transaction():
        try:
            order_id = dict_order_info.pop("order_id")
            dict_order_info["modified_by"] = dict_order_info.pop("user_id")
            dict_order_info["modified_date"] = get_current_date_time()
            logger.info("In update_subscription_order:  dict_order_info: {}".format(dict_order_info))

            if "approved_by" in dict_order_info and dict_order_info["approved_by"]:
                dict_order_info["approval_date"] = get_current_date_time()

            update_status = update_orders(dict_order_info=dict_order_info, order_id=order_id)
            logger.info("In update_subscription_order: update order in orders table: {}".format(update_status))

            if "status" in dict_order_info:
                #  track status changes
                order_status_tracker_record = create_order_status_track(order_id, dict_order_info["status"], dict_order_info["modified_by"])
                logger.info("In update_subscription_order: order_status_tracker_record: {}".format(order_status_tracker_record))

                if dict_order_info['status'] == settings.INQUIRY_STATUS_DELIVERED:  # add in stock as delivered
                    track_consumable_quantity(order_id)

            return create_response(1)

        except (InternalError, IntegrityError) as e:
            logger.error("error in update_subscription_order {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in update_subscription_order: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(2001)

        except Exception as e:
            logger.error("Error in update_subscription_order {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in update_subscription_order: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in update_subscription_order: " + str(e))


@validate(required_fields=["order_id", "company_id"])
def get_order_summary(order_info):
    """
    Fetches order summary given order id and company id
    :param order_info:
    :return:
    """
    company_id = order_info["company_id"]
    order_id = order_info["order_id"]
    try:
        summary_data = get_order_summary_data(order_id=order_id, company_id=company_id)
        logger.info("In get_order_summary: summary_data: {}".format(summary_data))
        return create_response(summary_data)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_order_summary {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_order_summary: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except DoesNotExist as e:
        logger.error("error in get_order_summary {}".format(e))
        return error(1020)

    except Exception as e:
        logger.error("Error in get_order_summary {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_order_summary: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_order_summary: " + str(e))


@validate(required_fields=["active", "company_id"])
def get_consumable_types(search_filters):
    """
    Fetches active consumable types, company id to provide current quantity of consumable
    :param search_filters:
    :return:
    """
    company_id = search_filters["company_id"]
    try:
        consumables = get_active_consumables(company_id, active=search_filters["active"])
        logger.info("In get_consumable_types: active_consumable_types: {}".format(consumables))
        return create_response(consumables)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_consumable_types {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_consumable_types: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_consumable_types {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_consumable_types: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_consumable_types: " + str(e))


def get_couriers():
    """
    Fetches supported couriers list
    :return: json
    """
    couriers: list = list()
    try:
        query = get_couriers_data()
        for record in query:
            couriers.append(record)
        logger.info("In get_couriers: couriers: {}".format(couriers))
        return create_response(couriers)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_couriers {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_couriers: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_couriers {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_couriers: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_couriers: " + str(e))


@validate(required_fields=["order_id", "courier_id", "name", "tracking_number", "user_id"])
def add_tracking_info(dict_tracking_info):
    """
    Makes entry for shipment details for order id
    :param dict_tracking_info:
    :return: json
    """
    dict_tracking_info["created_by"] = dict_tracking_info.pop("user_id")
    try:
        record = create_shipment_tracker_record(dict_tracking_info=dict_tracking_info)
        logger.info("In add_tracking_info: record: {}".format(record))
        return create_response(record.id)

    except (InternalError, IntegrityError) as e:
        logger.error("error in add_tracking_info {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_tracking_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except DoesNotExist as e:
        logger.error("error in add_tracking_info {}".format(e))
        return error(1020)

    except Exception as e:
        logger.error("Error in add_tracking_info {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_tracking_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in add_tracking_info: " + str(e))


@validate(required_fields=["file_name", "order_id", "user_id", "document_type"])
def add_invoice_file(file_info):
    """
    Makes entry for uploaded document file
    :param file_info:
    :return: json
    """
    try:
        if int(file_info["document_type"]) not in settings.ORDER_DOCS_CODE:
            return error(1020)
        file_info["created_by"] = file_info.pop("user_id")

        record, created = create_order_document(file_info=file_info)
        logger.info("In add_invoice_file: record:{}, created:{}".format(record, created))

        return create_response(record.id)

    except (InternalError, IntegrityError) as e:
        logger.error("error in add_invoice_file {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_invoice_file: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in add_invoice_file {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_invoice_file: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in add_invoice_file: " + str(e))


@validate(required_fields=["month", "year", "company_id"])
def get_consumable_stats(search_filters):
    """
    Gets statistics of monthly consumption of consumables for given company
    :param search_filters:
    :return: json
    """
    month = int(search_filters["month"])
    year = int(search_filters["year"])
    company_id = search_filters["company_id"]
    stats_data = defaultdict(list)
    try:
        consumable_types = get_consumables_types()
        logger.info("In get_consumable_stats: consumable_types:{}".format(consumable_types))

        for record in get_monthly_stats(company_id, month, year):
            _key = record["month_name"] + ", " + str(record["year"])
            stats_data[_key].append(record)

        logger.info("In get_consumable_stats: stats_data:{}".format(stats_data))
        response = {'stats': stats_data, 'consumable_types': consumable_types}
        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_consumable_stats {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_consumable_stats: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_consumable_stats {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_consumable_stats: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_consumable_stats: " + str(e))


@log_args_and_response
def update_used_consumable(args):
    """
    :return:
    @param args:
    """
    company_id = args.get('company_id')
    time_zone = args.get('time_zone', 'UTC')
    date = args.get("date", None)
    time_zone = settings.TIME_ZONE_MAP[time_zone]

    utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
    track_date = (datetime.datetime.now(pytz.timezone(time_zone)) - datetime.timedelta(days=1)).strftime('%m-%d-%y') if not date else date
    consumable_count_dict = dict()
    consumable_sent_data = list()
    consumable_count_data = list()
    pack_inventory_data = list()

    try:
        logger.info("In update_used_consumable: track_date: {}".format(track_date))
        last_sent_date = get_date_of_last_sent_consumable_data(company_id=company_id)
        if last_sent_date:
            from_date = (last_sent_date + datetime.timedelta(days=1)).strftime('%m-%d-%y')
            to_date = track_date
        else:
            from_date = to_date = track_date
        from_date, to_date = convert_date_to_sql_datetime(from_date, to_date)
        logger.info("In update_used_consumable: from_date: {}, to_date: {}".format(from_date, to_date))

        start_date = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')
        delta = end_date - start_date  # returns timedelta
        logger.info("In update_used_consumable: delta: {}".format(delta))

        for i in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=i)
            consumable_count_dict[day.date()] = {
                "label_count": 0,
                "robot_packs_count_unit_dose": 0,
                "robot_packs_count": 0,
                "manual_packs_count_unit_dose": 0,
                "manual_pack_count": 0,
                "error_pack_count_multi": 0,
                "error_pack_count_unit": 0
            }
        used_label_count = get_print_count(company_id, from_date=from_date, to_date=to_date, offset=utc_time_zone_offset)
        logger.info("In update_used_consumable: used_label_count: {}".format(used_label_count))
        for date, label_count in used_label_count.items():
            consumable_count_dict[date]["label_count"] = label_count

        pack_count_list = get_filled_pack_count_by_date(company_id=company_id, from_date=from_date, to_date=to_date,
                                                        offset=utc_time_zone_offset)
        logger.info("In update_used_consumable: pack_count_list: {}".format(pack_count_list))

        error_pack_count_unit, error_pack_count_multi = PackFillErrorV2.db_get_error_pack_count_by_date(
                                                                        from_date=from_date,
                                                                        to_date=to_date,
                                                                        offset=utc_time_zone_offset)
        logger.info("In update_used_consumable: error_pack_count_unit_list: {}".format(error_pack_count_unit))
        logger.info("In update_used_consumable: error_pack_count_multi_list: {}".format(error_pack_count_multi))

        if pack_count_list:
            for item in pack_count_list:
                if item['filled_at'] in [settings.FILLED_AT_DOSE_PACKER, settings.FILLED_AT_MANUAL_VERIFICATION_STATION]:
                    if item['pack_type'] == constants.WEEKLY_UNITDOSE_PACK or item['dosage_type'] == settings.DOSAGE_TYPE_UNIT:
                        consumable_count_dict[item['filled_date']]["robot_packs_count_unit_dose"] += item['pack_count']
                    else:
                        consumable_count_dict[item['filled_date']]["robot_packs_count"] += item['pack_count']
                elif item['filled_at'] in [settings.FILLED_AT_PRI_PROCESSING, settings.FILLED_AT_POST_PROCESSING,
                                           settings.FILLED_AT_PRI_BATCH_ALLOCATION, settings.FILLED_AT_FILL_ERROR]:
                    if item['pack_type'] == constants.WEEKLY_UNITDOSE_PACK or item['dosage_type'] == settings.DOSAGE_TYPE_UNIT:
                        consumable_count_dict[item['filled_date']]["manual_packs_count_unit_dose"] += item['pack_count']
                    else:
                        consumable_count_dict[item['filled_date']]["manual_pack_count"] += item['pack_count']

        for date, count in error_pack_count_multi.items():
            consumable_count_dict[date]["robot_packs_count"] = consumable_count_dict[date]["robot_packs_count"] - count
            consumable_count_dict[date]["error_pack_count_multi"] = count

        for date, count in error_pack_count_unit.items():
            consumable_count_dict[date]["robot_packs_count_unit_dose"] = consumable_count_dict[date][
                                                                             "robot_packs_count_unit_dose"] - count
            consumable_count_dict[date]["error_pack_count_unit"] = count

        logger.info("In update_used_consumable, consumable_count_dict: {}".format(consumable_count_dict))

        for date, count_data in consumable_count_dict.items():
            date = str(date)
            pack_inventory_data = [
                {
                    "product_id": settings.CONSUMABLE_TYPE_LABEL,
                    "customer_id": company_id,
                    "qty": count_data["label_count"],
                    "scrap_qty": 0,
                    "stock_req_date": date,
                    "time_zone": time_zone
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_DOSEPACK_MULTIDOSE,
                    "customer_id": company_id,
                    "qty": count_data["robot_packs_count"],
                    "scrap_qty": 0,
                    "stock_req_date": date,
                    "time_zone": time_zone
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_DOSEPACK_UNITDOSE,
                    "customer_id": company_id,
                    "qty": count_data["robot_packs_count_unit_dose"],
                    "scrap_qty": 0,
                    "stock_req_date": date,
                    "time_zone": time_zone
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_MANUAL_MULTIDOSE,
                    "customer_id": company_id,
                    "qty": count_data["manual_pack_count"],
                    "scrap_qty": 0,
                    "stock_req_date": date,
                    "time_zone": time_zone
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_MANUAL_UNITIDOSE,
                    "customer_id": company_id,
                    "qty": count_data["manual_packs_count_unit_dose"],
                    "scrap_qty": 0,
                    "stock_req_date": date,
                    "time_zone": time_zone
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_ERROR_PACK_MULTIDOSE,
                    "customer_id": company_id,
                    "qty": count_data["error_pack_count_multi"],
                    "scrap_qty": 0,
                    "stock_req_date": date,
                    "time_zone": time_zone
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_ERROR_PACK_UNITDOSE,
                    "customer_id": company_id,
                    "qty": count_data["error_pack_count_unit"],
                    "scrap_qty": 0,
                    "stock_req_date": date,
                    "time_zone": time_zone
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_DOSEPACK_UNITDOSE_8x4,
                    "customer_id": company_id,
                    "qty": 0,
                    "scrap_qty": 0,
                    "stock_req_date": date,
                    "time_zone": time_zone
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_MANUAL_UNITIDOSE_8x4,
                    "customer_id": company_id,
                    "qty": 0,
                    "scrap_qty": 0,
                    "stock_req_date": date,
                    "time_zone": time_zone
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_ERROR_PACK_UNITDOSE_8x4,
                    "customer_id": company_id,
                    "qty": 0,
                    "scrap_qty": 0,
                    "stock_req_date": date,
                    "time_zone": time_zone
                },
            ]

            inventory_api_status = inventory_api_call(api_name=settings.UPDATE_USED_CONSUMABLE,
                                                      json_data={"data": pack_inventory_data})
            logger.info("In update_used_consumable, inventory_api_status: {}, pack_inventory_data: {}".format(
                                                                                inventory_api_status,
                                                                                pack_inventory_data))
            if inventory_api_status:
                consumable_sent_data.append({"sent_data": json.dumps(pack_inventory_data),
                                             "company_id": company_id,
                                             "stock_req_date": date})
                consumable_count_data.extend(pack_inventory_data)

        if consumable_sent_data:
            consumable_insert_status = insert_into_consumable_sent_data_dao(consumable_sent_data=consumable_sent_data)
            logger.info("In update_used_consumable, consumable_insert_status: {}".format(consumable_insert_status))

        response = {"pack_inventory_data": consumable_count_data}
        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_used_consumable {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        send_email_update_used_consumable_failure(company_id=company_id, error_details=(err[2001] + str(e)),
                                                  current_date=track_date, time_zone=time_zone)
        print(f"Error in update_used_consumable: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except InventoryBadRequestException as e:
        logger.error("Error in update_used_consumable {}".format(e))
        send_email_update_used_consumable_failure(company_id=company_id, error_details=err[4001],
                                                  current_date=track_date, time_zone=time_zone)
        return error(4001, "- Error: {}.".format(e))

    except InventoryDataNotFoundException as e:
        logger.error("Error in update_used_consumable {}".format(e))
        send_email_update_used_consumable_failure(company_id=company_id, error_details=err[4002],
                                                  current_date=track_date, time_zone=time_zone)
        return error(4002, "- Error: {}.".format(e))

    except InventoryBadStatusCode as e:
        logger.error("Error in update_used_consumable {}".format(e))
        send_email_update_used_consumable_failure(company_id=company_id, error_details=err[4004],
                                                  current_date=track_date, time_zone=time_zone)
        return error(4004, "- Error: {}.".format(e))

    except InventoryConnectionException as e:
        logger.error("Error in update_used_consumable {}".format(e))
        send_email_update_used_consumable_failure(company_id=company_id, error_details=err[4003],
                                                  current_date=track_date, time_zone=time_zone)
        return error(4003, "- Error: {}.".format(e))

    except InvalidResponseFromInventory as e:
        logger.error("Error in update_used_consumable {}".format(e))
        send_email_update_used_consumable_failure(company_id=company_id, error_details=err[4005],
                                                  current_date=track_date, time_zone=time_zone)
        return error(4005, "- Error: {}.".format(e))

    except Exception as e:
        logger.error("Error in update_used_consumable {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_used_consumable: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        send_email_update_used_consumable_failure(company_id=company_id, error_details=(err[1000] + str(e)),
                                                  current_date=track_date, time_zone=time_zone)
        return error(1000, "Error in update_used_consumable: " + str(e))


@log_args_and_response
def get_pack_consumption(args):
    """
    :return:
    @param args:
    """
    info_dict: dict = dict()

    company_id = args.get('company_id')
    info_dict['company_id'] = company_id
    time_zone = args.get('time_zone', 'UTC')
    from_date_args = args.get("from_date", None)
    to_date_args = args.get("to_date", None)
    time_zone = settings.TIME_ZONE_MAP[time_zone]

    if not to_date_args and not from_date_args:
        current_date = get_current_date_time_as_per_time_zone()
        first_day_of_current_month = current_date.replace(day=1)

        # Calculate last day of the previous month
        last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)

        # Format dates in mm-dd-yy format
        from_date_args = last_day_of_previous_month.replace(day=1).strftime('%m-%d-%y')
        to_date_args = last_day_of_previous_month.strftime('%m-%d-%y')

    utc_time_zone_offset = get_utc_time_offset_by_time_zone(time_zone=time_zone)
    from_date, to_date = convert_date_to_sql_datetime(from_date_args, to_date_args)

    try:
        pack_inventory_data_day_wise = []

        start_date = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
        stop_date = datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')
        total_label_count = 0
        total_robot_packs_count = 0
        total_robot_packs_count_unit_dose = 0
        total_manual_pack_count = 0
        total_manual_packs_count_unit_dose = 0
        total_error_pack_count_multi = 0
        total_error_pack_count_unit = 0

        consumable_count_dict = dict()
        delta = stop_date - start_date
        for i in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=i)
            consumable_count_dict[day.date()] = {
                "label_count": 0,
                "robot_packs_count_unit_dose": 0,
                "robot_packs_count": 0,
                "manual_packs_count_unit_dose": 0,
                "manual_pack_count": 0,
                "error_pack_count_multi": 0,
                "error_pack_count_unit": 0
            }
        used_label_count = get_print_count(company_id, from_date=from_date, to_date=to_date,
                                           offset=utc_time_zone_offset)
        logger.info("In update_used_consumable: used_label_count: {}".format(used_label_count))
        for date, label_count in used_label_count.items():
            consumable_count_dict[date]["label_count"] = label_count
            total_label_count += label_count
        logger.info("In update_used_consumable: consumable_used_data: {}".format(consumable_count_dict))

        pack_count_list = get_filled_pack_count_by_date(company_id=company_id, from_date=from_date, to_date=to_date,
                                                        offset=utc_time_zone_offset)
        logger.info("In update_used_consumable: pack_count_list: {}".format(pack_count_list))

        error_pack_count_unit, error_pack_count_multi = PackFillErrorV2.db_get_error_pack_count_by_date(
            from_date=from_date, to_date=to_date,
            offset=utc_time_zone_offset)
        logger.info("In update_used_consumable: error_pack_count_unit_list: {}".format(error_pack_count_unit))
        logger.info("In update_used_consumable: error_pack_count_multi_list: {}".format(error_pack_count_multi))

        if pack_count_list:
            for item in pack_count_list:
                if item['filled_at'] in [settings.FILLED_AT_DOSE_PACKER,
                                         settings.FILLED_AT_MANUAL_VERIFICATION_STATION]:
                    if item['pack_type'] == constants.WEEKLY_UNITDOSE_PACK or item[
                        'dosage_type'] == settings.DOSAGE_TYPE_UNIT:
                        consumable_count_dict[item['filled_date']]["robot_packs_count_unit_dose"] += item['pack_count']
                        total_robot_packs_count_unit_dose += item['pack_count']
                    else:
                        consumable_count_dict[item['filled_date']]["robot_packs_count"] += item['pack_count']
                        total_robot_packs_count += item['pack_count']

                elif item['filled_at'] in [settings.FILLED_AT_PRI_PROCESSING, settings.FILLED_AT_POST_PROCESSING,
                                           settings.FILLED_AT_PRI_BATCH_ALLOCATION, settings.FILLED_AT_FILL_ERROR]:
                    if item['pack_type'] == constants.WEEKLY_UNITDOSE_PACK or item[
                        'dosage_type'] == settings.DOSAGE_TYPE_UNIT:
                        consumable_count_dict[item['filled_date']]["manual_packs_count_unit_dose"] += item['pack_count']
                        total_manual_packs_count_unit_dose += item['pack_count']
                    else:
                        consumable_count_dict[item['filled_date']]["manual_pack_count"] += item['pack_count']
                        total_manual_pack_count += item['pack_count']

        for date, count in error_pack_count_multi.items():
            consumable_count_dict[date]["error_pack_count_multi"] = count
            consumable_count_dict[date]["robot_packs_count"] = consumable_count_dict[date]["robot_packs_count"] - count
            total_robot_packs_count -= count
            total_error_pack_count_multi += count

        for date, count in error_pack_count_unit.items():
            consumable_count_dict[date]["error_pack_count_unit"] = count
            consumable_count_dict[date]["robot_packs_count_unit_dose"] = consumable_count_dict[date][
                                                                             "robot_packs_count_unit_dose"] - count
            total_robot_packs_count_unit_dose -= count
            total_error_pack_count_unit += count

        for date, count_data in consumable_count_dict.items():
            date = str(date)
            pack_inventory_data_day_wise += [
                {
                    "product_id": settings.CONSUMABLE_TYPE_LABEL,
                    "product": "[PET Label 420x196] 420mm Label Paper, 7X4",
                    "customer_id": company_id,
                    "qty": count_data["label_count"],
                    "scrap_qty": 0,
                    "stock_req_date": date
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_DOSEPACK_MULTIDOSE,
                    "product": "[PTM 7x4] Plastic Tray 7x4 Multi",
                    "customer_id": company_id,
                    "qty": count_data["robot_packs_count"],
                    "scrap_qty": 0,
                    "stock_req_date": date
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_DOSEPACK_UNITDOSE,
                    "product": "[PTM 7x4] Plastic Tray 7x4 Unit",
                    "customer_id": company_id,
                    "qty": count_data["robot_packs_count_unit_dose"],
                    "scrap_qty": 0,
                    "stock_req_date": date
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_MANUAL_MULTIDOSE,
                    "product": "[Plastic Tray M] Plastic Tray M",
                    "customer_id": company_id,
                    "qty": count_data["manual_pack_count"],
                    "scrap_qty": 0,
                    "stock_req_date": date
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_MANUAL_UNITIDOSE,
                    "product": "[PTM 7x4 - M] Plastic Tray 7x4 Unit - Manual",
                    "customer_id": company_id,
                    "qty": count_data["manual_packs_count_unit_dose"],
                    "scrap_qty": 0,
                    "stock_req_date": date
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_ERROR_PACK_MULTIDOSE,
                    "product": "[PTM 7x4 - RE] Plastic Tray 7x4 Multi - RE",
                    "customer_id": company_id,
                    "qty": count_data["error_pack_count_multi"],
                    "scrap_qty": 0,
                    "stock_req_date": date
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_ERROR_PACK_UNITDOSE,
                    "product": "[PTM 7x4 - RE] Plastic Tray 7x4 Unit - RE",
                    "customer_id": company_id,
                    "qty": count_data["error_pack_count_unit"],
                    "scrap_qty": 0,
                    "stock_req_date": date
                }
            ]

        pack_inventory_data = [
                {
                    "product_id": settings.CONSUMABLE_TYPE_LABEL,
                    "product": "[PET Label 420x196] 420mm Label Paper, 7X4",
                    "customer_id": company_id,
                    "qty": total_label_count,
                    "scrap_qty": 0,
                    "stock_req_date": f"{from_date_args} to {to_date_args}"
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_DOSEPACK_MULTIDOSE,
                    "product": "[PTM 7x4] Plastic Tray 7x4 Multi",
                    "customer_id": company_id,
                    "qty": total_robot_packs_count,
                    "scrap_qty": 0,
                    "stock_req_date": f"{from_date_args} to {to_date_args}"
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_DOSEPACK_UNITDOSE,
                    "product": "[PTM 7x4] Plastic Tray 7x4 Unit",
                    "customer_id": company_id,
                    "qty": total_robot_packs_count_unit_dose,
                    "scrap_qty": 0,
                    "stock_req_date": f"{from_date_args} to {to_date_args}"
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_MANUAL_MULTIDOSE,
                    "product": "[Plastic Tray M] Plastic Tray M",
                    "customer_id": company_id,
                    "qty": total_manual_pack_count,
                    "scrap_qty": 0,
                    "stock_req_date": f"{from_date_args} to {to_date_args}"
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_PACK_MANUAL_UNITIDOSE,
                    "product": "[PTM 7x4 - M] Plastic Tray 7x4 Unit - Manual",
                    "customer_id": company_id,
                    "qty": total_manual_packs_count_unit_dose,
                    "scrap_qty": 0,
                    "stock_req_date": f"{from_date_args} to {to_date_args}"
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_ERROR_PACK_MULTIDOSE,
                    "product": "[PTM 7x4 - RE] Plastic Tray 7x4 Multi - RE",
                    "customer_id": company_id,
                    "qty": total_error_pack_count_multi,
                    "scrap_qty": 0,
                    "stock_req_date": f"{from_date_args} to {to_date_args}"
                },
                {
                    "product_id": settings.CONSUMABLE_TYPE_ERROR_PACK_UNITDOSE,
                    "product": "[PTM 7x4 - RE] Plastic Tray 7x4 Unit - RE",
                    "customer_id": company_id,
                    "qty": total_error_pack_count_unit,
                    "scrap_qty": 0,
                    "stock_req_date": f"{from_date_args} to {to_date_args}"
                },
                {}
            ]
        status = send_email_monthly_consumable_data(company_id=company_id, total_pack_inventory=pack_inventory_data,
                                                    pack_inventory_data_day_wise=pack_inventory_data_day_wise, start_date=str(start_date.date()),
                                                    end_date=str(stop_date.date()))
        logger.info("In get_pack_consumption, status of email sent: {}".format(status))
        return create_response({"total_pack_inventory": pack_inventory_data,
                                "pack_inventory_data_day_wise": pack_inventory_data_day_wise})

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_used_consumable {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in update_used_consumable: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_used_consumable {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_used_consumable: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_used_consumable: " + str(e))
