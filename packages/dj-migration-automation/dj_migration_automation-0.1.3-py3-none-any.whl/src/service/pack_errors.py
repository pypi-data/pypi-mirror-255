import os
import sys
from _ast import arg
from collections import defaultdict
from copy import deepcopy
from decimal import Decimal

from peewee import InternalError, IntegrityError, DoesNotExist, DataError

import settings
from com.pharmacy_software import send_data
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, convert_date_from_sql_to_display_date
from dosepack.validation.validate import validate
from src import constants
from src.dao.canister_dao import db_get_canisters
from src.dao.company_setting_dao import get_ips_communication_settings_dao
from src.dao.drug_tracker_dao import db_get_drug_tracker_data_by_slot_id_pack_id_drug_id_dao, \
    db_update_drug_tracker_by_slot_id_dao, db_delete_drug_tracker_by_slot_id_dao
from src.dao.mfd_dao import db_get_mfd_dropped_pills_v2
from src.dao.mfd_dao import map_pack_location_dao
from src.dao.pack_dao import map_pack_location_dao, get_pack_grid_id_dao, verify_pack_id_by_system_id_dao, \
    get_pack_grid_id_by_slot_number, get_mfd_canister_drugs, get_pharmacy_data_for_system_id, db_get_pack_display_ids, \
    db_get_pack_and_display_ids, db_fetch_store_type_of_pack
from src.dao.pack_errors_dao import get_dropped_quantity_of_unique_drug_in_pack, get_error_details_by_pack_dao, \
    pack_fill_error_update_or_create_dao, delete_slot_fill_error_data_dao, db_get_errors, db_get_dropped_pills_v2, \
    db_slot_details_for_label_printing, get_reported_error_slot_number_query, get_pack_fill_error_slot_details, \
    slot_fill_error_create_multiple_record, add_analytical_data, slot_fill_error_get_or_create, \
    update_dict_slot_fill_error, delete_slot_fill_error_data_by_ids, delete_pack_fill_error_data_and_error_details, \
    get_pack_fill_error_data, get_pack_slot_error, get_fill_error_v2_dao, get_slot_id_from_slot_details, \
    store_error_packs_dao, update_assignation_dao, db_update_slot_wise_error_qty, \
    db_get_slot_wise_qty_for_pack, db_update_fill_error_pack, db_fetch_patient_packs, db_update_verification_status, \
    db_check_rph_pack, db_update_fod_broken_error
from src.dao.pill_vision_system_dao import db_get_pvs_predicted_qty_group_by_drug
from src.service.misc import get_token, get_userid_by_ext_username, get_current_user
from src.service.pack import update_packs_filled_by_in_ips

logger = settings.logger


@log_args_and_response
def get_pack_fill_errors_v2(pack_info):
    """
    Returns pack fill errors for given pack id

    :param pack_info:
    :return: json
    """
    pack_id = pack_info["pack_id"]
    system_id = pack_info["system_id"]
    pvs_data = dict()

    try:
        valid_pack = verify_pack_id_by_system_id_dao(pack_id=pack_id, system_id=system_id)
        if not valid_pack:
            return error(1014)

        reported_errors = db_get_errors(pack_id=pack_id)

        for unique_drug_id, item in db_get_dropped_pills_v2(pack_id).items():
            reported_errors[unique_drug_id]["dropped_pills"] = item

        # fetches drug dropped by mfd canisters
        for unique_drug_id, item in db_get_mfd_dropped_pills_v2(pack_id).items():
            reported_errors[unique_drug_id]["dropped_pills"] = item

        pvs_drug_count_query = db_get_pvs_predicted_qty_group_by_drug(pack_id)
        for item in pvs_drug_count_query:
            pvs_data.setdefault(item["unique_drug_id"], {})
            pvs_data[item["unique_drug_id"]][item["slot_number"]] = item["predicted_qty"]

        for unique_drug_id, item in pvs_data.items():
            if unique_drug_id in reported_errors.keys():
                for slot_number in item.keys():
                    if slot_number in reported_errors[unique_drug_id]["dropped_pills"].keys():
                        reported_errors[unique_drug_id]["dropped_pills"][slot_number].update(
                            {"predicted_qty": item[slot_number]})
                    else:
                        reported_errors[unique_drug_id]["dropped_pills"][slot_number] = {
                            "predicted_qty": item[slot_number]}
        return create_response(reported_errors)


    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_fill_errors_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_pack_fill_errors_v2 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_fill_errors_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)


@log_args_and_response
def get_pack_fill_errors_v2_new(pack_info):
    """
    Returns pack fill errors for given pack id slot wise This function returns slot wise data >> in particular slot
    >> how many unique drugs >> if error reported, also return that value


    @:param pack_info:
    :return: json
    """
    slot_data: dict = dict()
    pack_id = pack_info["pack_id"]
    system_id = pack_info["system_id"]

    try:
        valid_pack = verify_pack_id_by_system_id_dao(pack_id=pack_id, system_id=system_id)
        if not valid_pack:
            return error(1014)

        mfd_canister_fndc_txr_set, is_mfd_pack = get_mfd_canister_drugs(pack_id=pack_id)
        logger.info("In get_pack_fill_errors_v2_new: get_slots_for_label_printing mfd_can_fndc_txr_set, is_mfd_pack {}, {}".format(mfd_canister_fndc_txr_set,
                                                                                           is_mfd_pack))
        data, txr_list = db_slot_details_for_label_printing(pack_id, system_id, get_robot_to_manual=True,
                                                                   mfd_canister_fndc_txr_dict=mfd_canister_fndc_txr_set)

        for item in data:
            logger.info(f"In get_pack_fill_errors_v2_new: add this record in slot_data: {item}")

            slot_row, slot_column = item["slot_row"], item["slot_column"]
            slot_number = map_pack_location_dao(slot_row=slot_row, slot_column=slot_column)
            slot_data.setdefault(slot_number, {})
            slot_data[slot_number].setdefault("drug_info", {})
            slot_data[slot_number]["drug_info"].setdefault(item['unique_drug_id'], {})
            # if item["dropped_qty"]:
            #     slot_data[slot_number]["drug_info"][item['unique_drug_id']]["dropped_qty"] = item["dropped_qty"]
            # # if mdf
            # else:
            #     slot_data[slot_number]["drug_info"][item['unique_drug_id']]["dropped_qty"] = item["mfd_dropped_quantity"]

            slot_data[slot_number]["drug_info"][item['unique_drug_id']]["required_quantity"] = item["quantity"]

        logger.info(f'In get_pack_fill_errors_v2_new: slot_data: {slot_data}')

        # up to this, slot data >> slot number >> unique drug ids >> dropped qty

        # now we have to update slots >> in which error has reported >> we have to update dropped qty for that drug,
        # need to include broken or foreign object detected if reported.

        # get the slot number in which error has reported.
        query = get_reported_error_slot_number_query(pack_id=pack_id)
        slot_numbers = [number["slot_number"] for number in query]
        logger.info(f'in get_pack_fill_errors_v2_new: slot numbers: {slot_numbers}')

        if slot_numbers:

            for slot_number in slot_numbers:
                logger.info(f"In get_pack_fill_errors_v2_new: slot_number :{slot_number}")
                query = get_pack_fill_error_slot_details(pack_id=pack_id, slot_number=slot_number)

                for data in query:
                    if 'unique_drug_id' in data.keys() and data['unique_drug_id'] is not None:
                        if slot_number not in slot_data.keys():
                            slot_data.setdefault(slot_number, {})
                            slot_data[slot_number].setdefault("drug_info", {})

                        if data['unique_drug_id'] not in slot_data[slot_number]["drug_info"].keys():
                            slot_data[slot_number]["drug_info"].setdefault(data['unique_drug_id'], {})

                        logger.info(f"unique drug id: {data['unique_drug_id']}")

                        drug_info = slot_data[slot_number]["drug_info"][data['unique_drug_id']]

                        logger.info(f"grug_info:{drug_info}")

                        if data["broken"]:
                            drug_info["broken"] = data["broken"]

                        if data["error_qty"] or data["error_qty"] == 0:
                            drug_info["error_quantity"] = float(data["error_qty"])

                        # # in case of deferred pack, to consider the latest record.
                        # for rec in SlotTransaction.select(fn.MAX(SlotTransaction.created_date_time).alias(
                        #         "latest_created_date_time")).dicts().where(SlotTransaction.pack_id == pack_id):
                        #     latest_created_date_time = rec["latest_created_date_time"]
                        #
                        # try:
                        #     query = SlotHeader.select(
                        #         fn.SUM(SlotTransaction.dropped_qty)).dicts() \
                        #         .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                        #         .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
                        #         .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                        #         .join(UniqueDrug, on=(UniqueDrug.txr == DrugMaster.txr) &
                        #                              (UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)) \
                        #         .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.slot_id == SlotDetails.id) \
                        #         .where((SlotTransaction.pack_id == pack_id) & (
                        #             SlotTransaction.created_date_time >= latest_created_date_time),
                        #                UniqueDrug.id == data['unique_drug_id'],
                        #                PackGrid.slot_number == slot_number) \
                        #         .group_by(SlotDetails.id)
                        #
                        #     dropped_quantity = []
                        #     for record in query:
                        #         dropped_quantity.append(record["dropped_qty"])
                        #
                        #     dropped_quantity = dropped_quantity[0]
                        # except:
                        #     dropped_quantity = 0
                        #
                        # logger.info(f"dropped_quantity: {dropped_quantity}")
                        #
                        # if "error_qty" in data.keys():
                        #     if data["error_qty"]:
                        #         logger.info(f"error_quantity: {data['error_qty']}")
                        #         # dropped_quantity = float(dropped_quantity) + float(data["error_qty"])
                        #         dropped_quantity = float(data["actual_qty"])
                        #         drug_info["dropped_qty"] = dropped_quantity

                        logger.info(f"In get_pack_fill_errors_v2_new: slot_data[slot_number]['drug_info'][data['unique_drug_id']]:{slot_data[slot_number]['drug_info'][data['unique_drug_id']]}")

                        # drug_info["dropped_qty"] = dropped_quantity

                    else:
                        logger.info(f"In get_pack_fill_errors_v2_new: foreign_object_detected for slot_number : :{slot_number}")
                        if slot_number not in slot_data.keys():
                            slot_data.setdefault(slot_number, {})
                        slot_data[slot_number]["foreign_object_detected"] = data["foreign_object_detected"]

        response = {"slot_data": slot_data}

        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_pack_fill_errors_v2_new {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_fill_errors_v2_new: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_pack_fill_errors_v2_new {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_fill_errors_v2_new: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_pack_fill_errors_v2_new: " + str(e))


@log_args_and_response
# @validate(required_fields=["pack_id", "slot", "slot_errors", "user_id"])
def report_fill_errors_v2(fill_error_info):
    """
    This function update the PackFillError v2 and SlotFillError v2 table

    args:
    {"system_id”:14,
        “pack_id":62412,
        “user_id”:13,
        "slot_errors":
            {
             1:{
                 "drug_info":{
                           4211:{
                        "error_quantity":2,
                        "broken":false,
                        "actual_quantity":2
                        }
                    },
                 "foreign_object_detected":true
            }
        }
        }

    @param fill_error_info:
    @return:
    """
    logger.info("In report_fill_errors_v2: Data to report fill errors v2: {}".format(fill_error_info))
    pack_id = fill_error_info["pack_id"]
    # unique_drug_id = fill_error_info["unique_drug_id"]
    slot_errors = fill_error_info["slot_errors"]
    # note = fill_error_info["note"]
    user_id = fill_error_info["user_id"]
    current_date_time = get_current_date_time()

    # throwing error as no fill error is provided
    if not slot_errors:
        return error(1020)

    try:

        with db.transaction():

            slot_numbers = list(slot_errors.keys())
            logger.info(f'In report_fill_errors_v2: slot_numbers in which errors reported:{slot_numbers}')

            pack_fill_error = {
                # 'note': note,
                'created_by': user_id,
                'modified_by': user_id,
                'created_date': current_date_time,
                'modified_date': current_date_time
            }
            for slot_number in slot_numbers:
                pack_grid_id = get_pack_grid_id_by_slot_number(slot_number=slot_number)
                if 'drug_info' in slot_errors[slot_number].keys():
                    drug_ids = list(slot_errors[slot_number]['drug_info'].keys())
                    logger.info(f'In report_fill_errors_v2: drug_ids:{drug_ids}')

                    for drug_id in drug_ids:

                        broken =None
                        error_qty = None
                        actual_qty = None
                        counted_error_qty = None

                        slot_error_list = list()
                        drug_error = slot_errors[slot_number]['drug_info'][drug_id]
                        logger.info(f"In report_fill_errors_v2: drug error for drug_id = {drug_id}, drug_error:{drug_error} ")

                        # update if already reported
                        fill_error, _ = pack_fill_error_update_or_create_dao(unique_drug_id=drug_id, pack_id=pack_id, pack_fill_error=deepcopy(pack_fill_error))

                        # todo: move to slot fill error v2 dao file
                        # if user update the error report in particular slot for particular drug in that case first delete that error and after update the table.
                        query = get_pack_slot_error(drug_id=drug_id, pack_grid_id=pack_grid_id, pack_id=pack_id)

                        for records in query:
                            broken = records['broken']
                            error_qty = records['error_qty']
                            actual_qty = records['actual_qty']
                            counted_error_qty = records['counted_error_qty']

                        # if user update the error report in particular slot for particular drug in that case first delete that error and after update the table.
                        status = delete_slot_fill_error_data_dao(fill_error=fill_error, pack_grid_id=pack_grid_id)
                        logger.info("In report_fill_errors_v2: slot fill error data deleted : {}".format(status))

                        # try:
                        #     dropped_qty = get_dropped_quantity_of_unique_drug_in_pack(pack_id=pack_id, pack_grid_id=pack_grid_id, unique_drug_id=drug_id)
                        # except DoesNotExist as e:
                        #     logger.info('In report_fill_errors_v2: No dropped quantity reported by robot for unique_drug_id {} '
                        #                 'for pack {} in pack_grid_id {} '.format(drug_id, pack_id, slot_number))
                        #     dropped_qty = 0

                        if 'required_quantity' in drug_error.keys():
                            error_qty = float(drug_error['error_quantity'])
                            actual_qty = float(drug_error['actual_quantity'])
                            required_qty = float(drug_error["required_quantity"])
                            counted_error_qty = actual_qty - required_qty
                        # else:
                        #     error_qty = None
                        #     actual_qty = None
                        #     counted_error_qty = None

                        if 'broken' in drug_error.keys():
                            broken = drug_error['broken']
                        # else:
                        #     broken = None

                        if 'broken' not in drug_error.keys() and 'actual_quantity' not in drug_error.keys():
                            # this case should not come
                            logger.info("In report_fill_errors_v2: neither qty. error or broken error reported")
                            continue

                        slot_error_list.append({'pack_fill_error_id': fill_error.id,
                                                'pack_grid_id': pack_grid_id, 'broken': broken, 'error_qty': error_qty,
                                                'actual_qty': actual_qty, 'counted_error_qty': counted_error_qty,
                                                'created_by': user_id, 'created_date': current_date_time})
                        logger.info(f"In report_fill_errors_v2: slot_error_list: {slot_error_list}")

                        status = slot_fill_error_create_multiple_record(slot_error_list=slot_error_list)
                        logger.info("In report_fill_errors_v2: SlotFillErrorV2 table updated: {}".format(status))

                        slot_id = get_slot_id_from_slot_details(pack_id, drug_id, slot_number)
                        drug_tracker_data = db_get_drug_tracker_data_by_slot_id_pack_id_drug_id_dao(slot_id, pack_id,
                                                                                                    drug_id)

                        drug_tracker_quantity = 0
                        for record in drug_tracker_data:
                            drug_tracker_quantity += record["drug_quantity"]

                        drug_tracker_quantity = float(drug_tracker_quantity)
                        if actual_qty > required_qty:
                            updated_drug_tracker_quantity = drug_tracker_quantity - (actual_qty - required_qty)
                            if updated_drug_tracker_quantity < required_qty:
                                updated_drug_tracker_quantity = required_qty
                            update_dict = {"drug_quantity": updated_drug_tracker_quantity,
                                           "modified_date": get_current_date_time()
                                           }

                            updated_drug_tracker_status = db_update_drug_tracker_by_slot_id_dao(update_dict,
                                                                                                [slot_id])
                            logger.info("In report_fill_errors_v2: case-1: updated_drug_tracker_status: {}".format(
                                updated_drug_tracker_status))
                        elif actual_qty < required_qty:
                            if broken:
                                if actual_qty == 0:
                                    delete_drug_tracker_status = db_delete_drug_tracker_by_slot_id_dao([slot_id])
                                    logger.info("In report_fill_errors_v2: delete_drug_tracker_status: {}".format(
                                        delete_drug_tracker_status
                                    ))
                                elif actual_qty < drug_tracker_quantity:
                                    update_dict = {"drug_quantity": actual_qty,
                                                   "modified_date": get_current_date_time()
                                                   }

                                    updated_drug_tracker_status = db_update_drug_tracker_by_slot_id_dao(update_dict,
                                                                                                        [slot_id])
                                    logger.info(
                                        "In report_fill_errors_v2: case-2: updated_drug_tracker_status: {}".format(
                                            updated_drug_tracker_status))

                if 'foreign_object_detected' in slot_errors[slot_number].keys():

                    # when user report the foreign_object_detected error >>update PackFillError_v2 and SlotFillError_v2 table
                    # when user unselect slot in which he has already reported the error >> delete that entry

                    # foreign_object_detected per slot so at that time drug_id is null.
                    drug_id = None
                    fill_error, _ = pack_fill_error_update_or_create_dao(unique_drug_id=drug_id, pack_id=pack_id, pack_fill_error=deepcopy(pack_fill_error))
                    logger.info(f"In report_fill_errors_v2: fill_error: {fill_error.id}")
                    if slot_errors[slot_number]['foreign_object_detected']:
                        out_of_class_reported = 1
                    else:
                        out_of_class_reported = 0
                    slot_error_list = list()
                    slot_error_list.append(
                        {'pack_fill_error_id': fill_error.id, 'pack_grid_id': pack_grid_id, 'broken': None,
                            'error_qty': None, 'actual_qty': None, 'counted_error_qty': None, 'created_by': user_id,
                            'created_date': current_date_time, 'out_of_class_reported': out_of_class_reported})

                    logger.info(f"In report_fill_errors_v2: slot_error_list: {slot_error_list}")

                    status = delete_slot_fill_error_data_dao(fill_error=fill_error, pack_grid_id=pack_grid_id)
                    logger.info("In report_fill_errors_v2: slot fill error data deleted: {}".format(status))

                    if out_of_class_reported:
                        status = slot_fill_error_create_multiple_record(slot_error_list=slot_error_list)
                        logger.info("In report_fill_errors_v2: SlotFillErrorV2 table updated: {}".format(status))

        return create_response(True)

    except (InternalError, IntegrityError) as e:
        logger.error("error in report_fill_errors_v2 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in report_fill_errors_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in report_fill_errors_v2 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in report_fill_errors_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in report_fill_errors_v2: " + str(e))


@log_args_and_response
@validate(required_fields=['fill_error_id'])
def delete_fill_error_v2(fill_error):
    """
    Deletes fill error reported by user

    :param fill_error: dict containing fill_error_id
    :return: str
    """
    try:
        with db.atomic():
            fill_error_instance = get_pack_fill_error_data(id=fill_error["fill_error_id"])
            pack_id = fill_error_instance.pack_id
            fill_error_instance.delete_instance(recursive=True, delete_nullable=True)
            add_analytical_data({'pack_id': pack_id})
            return create_response(1)
    except DoesNotExist:
        return error(1004)

    except (InternalError, IntegrityError) as e:
        logger.error("error in delete_fill_error_v2 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_fill_error_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in delete_fill_error_v2 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_fill_error_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in delete_fill_error_v2: " + str(e))


@log_args_and_response
@validate(required_fields=["pack_id", "slot_row", "slot_column", "slot_errors", "user_id"])
def report_fill_errors_single_slot_v2(fill_error_info: dict) -> dict:
    """

    @param fill_error_info:
    @return:
    """
    logger.debug("Data to report fill errors v2: {}".format(fill_error_info))
    pack_id = fill_error_info["pack_id"]
    slot_errors = fill_error_info["slot_errors"]
    slot_row = fill_error_info["slot_row"]
    slot_column = fill_error_info["slot_column"]
    note = fill_error_info.get("note", None)
    user_id = fill_error_info["user_id"]
    current_date_time = get_current_date_time()

    # throwing error as no fill error is provided
    if not slot_errors and not note:
        return error(1020)

    try:
        with db.transaction():
            pack_grid_id = get_pack_grid_id_dao(slot_row=slot_row, slot_column=slot_column)
            print('pack_grid_id', pack_grid_id)
            pack_fill_error = {
                'note': note,
                'created_by': user_id,
                'modified_by': user_id,
                'created_date': current_date_time,
                'modified_date': current_date_time
            }
            delete_slot_fill_error_list = list()
            delete_error_details_list = list()
            if slot_errors:
                # slot_error_list = list()
                for item in slot_errors:
                    broken = item.get('broken', False)
                    # error_quantity = item.get('error_quantity', 0)
                    unique_drug_id = item['unique_drug_id']
                    slot_fill_error_id = item.get('slot_fill_error_id', None)
                    out_of_class = item.get('out_of_class', False)

                    try:
                        dropped_qty = get_dropped_quantity_of_unique_drug_in_pack(pack_id=pack_id, pack_grid_id=pack_grid_id, unique_drug_id=unique_drug_id)
                    except DoesNotExist as e:
                        logger.info('In report_fill_errors_single_slot_v2: No dropped quantity reported by robot for unique_drug_id {} '
                                    'for pack {} in pack_grid_id {} '.format(unique_drug_id, pack_id, pack_grid_id))
                        dropped_qty = 0
                    counted_error_qty = int(item['actual_quantity']) - int(dropped_qty)

                    if not broken and not counted_error_qty:
                        try:
                            delete_in_error_details = get_error_details_by_pack_dao(pack_id=pack_id, pack_grid_id=pack_grid_id, unique_drug_id=unique_drug_id)
                            if not delete_in_error_details["pvs_error_qty"]:
                                delete_error_details_list.append(delete_in_error_details["id"])
                        except DoesNotExist as e:
                            logger.info("In report_fill_errors_single_slot_v2: no previous error")

                        delete_slot_fill_error_list.append(slot_fill_error_id)
                    else:
                        fill_error, _ = pack_fill_error_update_or_create_dao(unique_drug_id=unique_drug_id, pack_id=pack_id,
                                                                            pack_fill_error=pack_fill_error.copy())

                        create_dict = {
                            'pack_fill_error_id': fill_error.id,
                            'pack_grid_id': pack_grid_id
                        }
                        update_dict = {
                            'broken': item.get('broken', False),
                            'error_qty': item['error_quantity'],
                            'actual_qty': int(item['actual_quantity']),
                            'counted_error_qty': int(counted_error_qty),
                            'out_of_class_reported': out_of_class,
                            'created_by': user_id,
                            'created_date': current_date_time
                        }
                        record, created = slot_fill_error_get_or_create(defaults=update_dict, create_dict=create_dict)

                        if not created:
                            status = update_dict_slot_fill_error(update_dict=update_dict, slot_fill_error_id=record.id)
                            logger.info("In report_fill_errors_single_slot_v2: record updated in slot fill error table:{}".format(status))
                        item['fill_error_id'] = fill_error.id
                        item['slot_fill_error_id'] = record.id

                if delete_slot_fill_error_list:
                    delete_status = delete_slot_fill_error_data_by_ids(delete_slot_fill_error_list=delete_slot_fill_error_list)
                    logger.info("In report_fill_errors_single_slot_v2: record deleted from slot fill error table:{}".format(delete_status))

                pack_fill_error_status, error_details_status = delete_pack_fill_error_data_and_error_details(pack_id=pack_id, delete_error_details_list=delete_error_details_list)
                logger.info("In report_fill_errors_single_slot_v2: record deleted from pack fill error table:{} and error details table: {}".format(
                    pack_fill_error_status, error_details_status))

            add_analytical_data({'pack_id': pack_id})

        return create_response(fill_error_info)

    except (InternalError, IntegrityError) as e:
        logger.error("error in report_fill_errors_single_slot_v2 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in report_fill_errors_single_slot_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in report_fill_errors_single_slot_v2 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in report_fill_errors_single_slot_v2: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in report_fill_errors_single_slot_v2: " + str(e))


@validate(required_fields=["from_date", "to_date", "system_id", "time_zone", "company_id"])
def get_fill_errors_data_v2(search_filters):
    """
    Returns data for fill errors report

    :param search_filters:
    :return: json
    """
    from_date, to_date = search_filters['from_date'], search_filters['to_date']
    time_zone = search_filters["time_zone"]
    system_id = search_filters["system_id"]
    company_id = search_filters["company_id"]
    pharmacy_data = dict()
    errors_data = defaultdict(lambda: defaultdict(list))
    drug_canisters = defaultdict(list)

    try:
        for canister in db_get_canisters(company_id, all_flag=True):
            drug_canisters[canister["formatted_ndc"], canister["txr"]].append(canister)

        query = get_fill_error_v2_dao(time_zone=time_zone, system_id=system_id,
                                      from_date=from_date, to_date=to_date)

        for record in query:
            record["reported_date"] = convert_date_from_sql_to_display_date(record["reported_date"])
            record["canister_list"] = drug_canisters[record["formatted_ndc"], record["txr"]]
            drug_name = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"]
            record['original_locations'] = list()
            if record['location_list'] is not None:
                for original_location in record['location_list'].split(','):
                    a, b, c, d = original_location.split('--', maxsplit=3)
                    # `maxsplit` up to 3 as robot_name can have `-`
                    record["original_locations"].append({
                        'device_id': a,
                        'canister_id': b,
                        'display_location': c,
                        'device_name': d
                    })
            # errors_data[record["reason"]][drug_name].append(record)
            add_error_count("missing_count", "Missing Pill", errors_data, drug_name, record)
            add_error_count("broken_count", "Broken Pill", errors_data, drug_name, record)
            add_error_count("extra_count", "Extra Pill Count", errors_data, drug_name, record)
            add_error_count("misplaced_count", "Pill Misplaced", errors_data, drug_name, record)

        try:  # get pharmacy data
            pharmacy_data = next(get_pharmacy_data_for_system_id(system_id=system_id))
        except StopIteration:
            pass  # No pharmacy data found(invalid system id)

        response = {'report_data': errors_data, 'pharmacy_data': pharmacy_data}
        return create_response(response)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def add_error_count(count_key, reason_key, errors_data, drug_name, record):
    """ Helper function for adding error count and maintain format of data """
    if record[count_key]:
        errors_data[reason_key][drug_name].append({
            "drug_name": record["drug_name"],
            "ndc": record["ndc"],
            "strength": record["strength"],
            "strength_value": record["strength_value"],
            "txr": record["txr"],
            "formatted_ndc": record["formatted_ndc"],
            "reported_date": record["reported_date"],
            "canister_list": record["canister_list"],
            "original_locations": record["original_locations"],
            "occurrence": abs(record[count_key])
        })


@log_args_and_response
def store_error_packs(pack_args):
    """
    Stores error reported packs in db
    """
    try:
        for args in pack_args:
            pack_id = args.get("pack_id")
            fill_error_note = args.get("error_note", "") if args.get("error_note", "") else ""
            error_desc = args.get("error_desc", "") if args.get("error_desc", "") else ""
            if fill_error_note and error_desc:
                sum_error = fill_error_note + "\n" + error_desc
            else:
                if fill_error_note:
                    sum_error = fill_error_note
                else:
                    sum_error = error_desc
            ips_username = args.get("updated_by")
            company_id = args.get("company_id")
            user_info = get_userid_by_ext_username(ips_username, company_id)
            status = store_error_packs_dao(reported_by=user_info['id'], pack_id=pack_id,
                                           fill_error_note=sum_error, modified_by=user_info['id'])
        return create_response(settings.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError) as e:
        logger.error("error in store_error_packs: ", e, exc_info=True)
        return error(2001)
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        logger.error("Error in store_error_packs")
        return error(5008)
    except Exception as e:
        logger.error("error in store_error_packs: ", e, exc_info=True)
        return error(2001)


@log_args_and_response
def update_assignation(args):
    """
    Stores error reported packs in db
    """
    try:
        pack_id_list = args.get("pack_id")
        assigned_to = args.get("assigned_to")
        for pack_id in pack_id_list:
            status = update_assignation_dao(assigned_to=assigned_to, pack_id=pack_id,
                                            modified_by=assigned_to, modified_date=get_current_date_time())
        return create_response(settings.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError) as e:
        logger.error("error in store_error_packs: ", e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("error in store_error_packs: ", e, exc_info=True)
        return error(2001)


@log_args_and_response
def save_adjusted_error_qty(args):
    """
    Stores error qty in slot details
    """
    try:
        pack_id = args.get("pack_id")
        cyclic_pack = bool(int(args.get("cyclic_pack")))
        user_id = args.get("user_id")
        adjustment_details = args.get("slot_errors")
        drug_data = {}
        for pack_grid_id, slot_data in adjustment_details.items():
            drug_info = slot_data.get('drug_info', None)
            if drug_info:
                for drug_id, drug_data in drug_info.items():
                    if not cyclic_pack:
                        pack_grid_id = None
                    slot_wise_qty = db_get_slot_wise_qty_for_pack(pack_id,
                                                                  pack_grid_id=pack_grid_id, drug_id=drug_data['drug_id'])
                    initial_slot_wise_qty = slot_wise_qty.copy()
                    qty = -Decimal(drug_data['error_quantity'])
                    for key, value in sorted(slot_wise_qty.items()):
                        if value >= qty:
                            slot_wise_qty[key] -= qty
                            break
                        else:
                            qty -= value
                            slot_wise_qty[key] = 0
                    status = db_update_slot_wise_error_qty(slot_wise_qty=slot_wise_qty,
                                                           doctor_approval=drug_data.get('doctor_approval'),
                                                           initial_slot_wise_qty=initial_slot_wise_qty)
                    status = db_update_fod_broken_error(fod=slot_data.get('foreign_object_detected', False),
                                                        pack_id=pack_id, broken=drug_data.get("broken", False), pack_grid_id=pack_grid_id, drug_id=drug_id, user_id=user_id)
            else:
                status = db_update_fod_broken_error(fod=slot_data.get('foreign_object_detected', False),
                                                    pack_id=pack_id, broken=False,
                                                    pack_grid_id=pack_grid_id, drug_id=None, user_id=user_id)
        return create_response(settings.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError) as e:
        logger.error("error in save_adjusted_error_qty: ", e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("error in save_adjusted_error_qty: ", e, exc_info=True)
        return error(2001)


@log_args_and_response
def fix_error_pack(args):
    """
    mark packs status when error is fixed
    """
    try:
        pack_id = args.get("pack_id")
        company_id = args.get("company_id")
        token = get_token()
        user_details = get_current_user(token)
        status = db_update_fill_error_pack(pack_id=pack_id, user_id=user_details["id"])
        ips_pack_ids = db_get_pack_display_ids([pack_id])
        store_type = db_fetch_store_type_of_pack(pack_id)
        parameters = {"pack_id": int(ips_pack_ids[0]), "resolved_by": user_details['ips_user_name'], "store_type": store_type}
        ips_comm_settings = get_ips_communication_settings_dao(company_id=company_id)
        settings_present = all(key in ips_comm_settings for key in settings.IPS_COMMUNICATION_SETTINGS)
        if settings_present:
            send_data(base_url=ips_comm_settings['BASE_URL_IPS_WEB'].split("//")[1], webservice_url=settings.FIX_ERROR,
                      parameters=parameters, counter=0, request_type="POST", token=token, ips_api=True)
            pack_and_display_ids = db_get_pack_and_display_ids([pack_id])
            update_packs_filled_by_in_ips(pack_ids=ips_pack_ids, ips_username=user_details['ips_user_name'],
                                          pack_and_display_ids=pack_and_display_ids,
                                          ips_comm_settings=ips_comm_settings, token=token, pack_edit_flag=True)
        else:
            raise error(7002)
        return create_response(settings.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError) as e:
        logger.error("error in fix_error_pack: ", e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("error in fix_error_pack: ", e, exc_info=True)
        return error(2001)


@log_args_and_response
def fetch_patient_packs(pack_id, rx_id, company_id=None, system_id=None):
    """
    fetched packs based on patient
    """
    try:
        data = {}
        response, patient_id = db_fetch_patient_packs(pack_id, rx_id)
        data["patient_id"] = patient_id
        data["response"] = response
        return create_response(data)
    except (InternalError, IntegrityError) as e:
        logger.error("error in fetch_patient_packs: ", e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("error in fetch_patient_packs: ", e, exc_info=True)
        return error(2001)


@log_args_and_response
def verify_rph_pack(args):
    """
    update verification status in DP and sync it with IPS
    """
    try:
        with db.transaction():
            ips_pack_ids = []
            pack_list = args.get("pack_list", None)
            rx_id = args.get("rx_id", None)
            verification_status = args.get("verification_status", None)
            store_type = args.get("storeType", None)
            verification_status_name = args.get("verification_status_name", None)
            fill_error_type = args.get("fill_error_type", None) if args.get("fill_error_type", None) else ""
            ips_note = args.get("note", None) if args.get("note", None) else ""
            if fill_error_type and ips_note:
                fill_error_note = fill_error_type + "\n" + ips_note
            else:
                if fill_error_type:
                    fill_error_note = fill_error_type
                else:
                    fill_error_note = ips_note
            ips_username = args.get("ips_username", None)
            company_id = args.get("company_id", None)
            system_id = args.get("system_id", None)
            user_id = args.get("user_id", None)
            other_error = args.get("other_error", None)
            error_values = args.get("error_values", None)
            verification_type = args.get("verification_type", None)
            if pack_list:
                status = db_update_verification_status(pack_list, verification_status, user_id, fill_error_note)
                ips_pack_ids = db_get_pack_display_ids(pack_list)
                ips_pack_ids = ', '.join(map(str, ips_pack_ids))
            parameters = {
                "reported_by": ips_username,
                "fill_status": verification_status_name,
                "verification_type": verification_type,
                "company_id": company_id,
                "note": ips_note,
                "fill_error_values": fill_error_type,
                "other_status": other_error,
                "other_error_values": error_values,
                "store_type": store_type
            }
            if ips_pack_ids:
                parameters["pack_list"] = ips_pack_ids
            if rx_id:
                parameters["rx_id"] = rx_id
            token = get_token()
            if not token:
                logger.debug("verify_rph_pack: token not found")
                return error(5018)
            logger.info(f"In verify_rph_pack, parameters are {parameters}")
            ips_comm_settings = get_ips_communication_settings_dao(company_id=company_id)
            send_data(base_url=ips_comm_settings['BASE_URL_IPS_WEB'].split("//")[1],
                      webservice_url=settings.VERIFICATION_SYNC_API,
                      parameters=parameters, counter=0, request_type="POST", token=token, ips_api=True)
            return create_response(settings.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError) as e:
        logger.error("error in verify_rph_pack: ", e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("error in verify_rph_pack: ", e, exc_info=True)
        return error(2001)


@log_args_and_response
def system_hold_packs(args):
    """
    update verification status in DP and sync it with IPS
    """
    try:
        pass
    except (InternalError, IntegrityError) as e:
        logger.error("error in system_hold_packs: ", e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("error in system_hold_packs: ", e, exc_info=True)
        return error(2001)


@log_args_and_response
def check_rph_pack(pack_display_id, company_id, system_id):
    """
    update verification status in DP and sync it with IPS
    """
    try:
        pack_id = db_check_rph_pack(pack_display_id)
        return pack_id
    except (InternalError, IntegrityError) as e:
        logger.error("error in check_rph_pack: ", e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error("error in check_rph_pack: ", e, exc_info=True)
        return error(2001)
