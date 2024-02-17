import datetime
import functools
import operator

import settings
from src import constants
from peewee import *
from typing import List
from decimal import Decimal

from src.dao.drug_dao import db_get_txr_and_drug_id_by_ndc_dao, db_get_drug_id_by_ndc_dao
from src.model.model_pack_grid import PackGrid
from src.model.model_patient_rx import PatientRx
from src.model.model_drug_master import DrugMaster
from src.model.model_slot_header import SlotHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_drug_tracker import DrugTracker
from src.model.model_pack_details import PackDetails
from src.model.model_slot_details import SlotDetails
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from dosepack.utilities.utils import log_args_and_response
from src.dao.pack_dao import get_manual_pack_ids_for_manual_pack_filling
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger


@log_args_and_response
def get_drug_tracker_info_by_canister_ids(replenish_ids: List[int]) -> dict:
    """
    Method to get drug tracker details by replenish_ids from which we can measure
    total drug quantity used per canister per replenish tracker id till now

    @param replenish_ids: replenish_ids for which drug tracking info required
    @return:
    """
    try:

        drug_tracker_data: dict = dict()

        query = DrugTracker.select(DrugTracker.canister_id, DrugTracker.canister_tracker_id,
                                   fn.sum(DrugTracker.drug_quantity).alias("quantity_used"),
                                   DrugTracker.case_id,
                                   DrugTracker.lot_number,
                                   DrugTracker.expiry_date).dicts() \
            .where(DrugTracker.canister_tracker_id << replenish_ids) \
            .group_by(DrugTracker.canister_id, DrugTracker.canister_tracker_id)

        for record in query:
            canister_id = record["canister_id"]
            drug_tracker_data[canister_id] = record

        return drug_tracker_data

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_drug_tracker_info_by_canister_ids:  {}".format(e))
        raise


@log_args_and_response
def drug_tracker_create_multiple_record(insert_dict: list):
    try:
        status = BaseModel.db_create_multi_record(insert_dict, DrugTracker)
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in drug_tracker_create_multiple_record:  {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in drug_tracker_create_multiple_record:  {}".format(e))
        raise e


@log_args_and_response
def db_update_drug_tracker_by_slot_id_dao(update_dict, slot_ids):
    try:
        status = DrugTracker.db_update_drug_tracker_by_slot_id(update_dict=update_dict,
                                                               slot_ids=slot_ids
                                                               )
        return status
    except Exception as e:
        logger.error("Error in db_update_drug_tracker_by_slot_id_dao: {}".format(e))
        raise e

def db_update_drug_tracker_by_drug_id_dao(update_dict, slot_ids):
    try:
        status = DrugTracker.db_update_drug_tracker_by_slot_id(update_dict=update_dict,
                                                               slot_ids=slot_ids
                                                               )
        return status
    except Exception as e:
        logger.error("Error in db_update_drug_tracker_by_slot_id_dao: {}".format(e))
        raise e

@log_args_and_response
def db_update_drug_tracker_by_drug_tracker_id_dao(update_dict, drug_tracker_ids):
    try:
        status = DrugTracker.db_update_drug_tracker_by_drug_tracker_id(update_dict=update_dict,
                                                                       drug_tracker_ids=drug_tracker_ids)

        return status
    except Exception as e:
        logger.error("error in db_update_drug_tracker_by_drug_tracker_id_dao: {}".format(e))
        raise e


@log_args_and_response
def get_filled_unfilled_slots_by_pack_id_and_drug_id(args, drug_lot_master_args):

    try:
        logger.info("In get_filled_unfilled_slots_by_pack_id_and_drug_id")

        response = dict()
        pack_info = args["pack_info"]
        txr = args["txr"]
        scanned_drug = args["scanned_drug"]
        module_id = args["module_id"]
        ndc_list = set()
        scan_type = args["scan_type"]
        canister_id = args['canister_id']
        case_id = args['case_id']
        update_data = dict()
        update_batch = []
        update_list = []
        delete_list = []
        required_quantity = 0
        # if not canister_id:
        #     case_id_present = drug_lot_master_args.pop("case_id_present")

        select_fields = [SlotDetails.id.alias("slot_details_id"),
                         SlotDetails.drug_id.alias("slot_details_drug"),
                         DrugTracker.drug_id.alias("drug_tracker_drug"),
                         DrugTracker.is_overwrite,
                         PackGrid.slot_number,
                         SlotDetails.quantity.alias("required_quantity"),
                         DrugTracker.drug_quantity.alias("filled_quantity"),
                         SlotDetails.pack_rx_id.alias("pack_rx_id"),
                         ]

        for pack_id, pack_data in pack_info.items():
            for slot_id, ndc_dicts in pack_info[pack_id]['slots_to_filled'].items():
                # current_ndc_list = [(ndc_item.split('_')[0], ndc_item.split('_')[1]) for ndc_item in list(ndc_dicts.keys())]
                # ndc_list.update(current_ndc_list)
                for ndc_item in list(ndc_dicts.keys()):
                    temp_data = ndc_item.split("_")
                    if len(temp_data) > 1:
                        current_ndc_list = [(ndc_item.split('_')[0], ndc_item.split('_')[1])]
                        ndc_list.update(current_ndc_list)
                    else:
                        current_ndc_list = [(ndc_item.split('_')[0], "")]
                        ndc_list.update(current_ndc_list)

        drug_ids = db_get_drug_id_by_ndc_dao(list(ndc_list))
        for pack_id, pack_data in pack_info.items():
            pack_data = {
                        key: {int(sub_key): value for sub_key, value in sub_dict.items()}
                        for key, sub_dict in pack_data.items()
                        }
            diff_slot_number = []
            slots_to_filled = list(map(int, pack_data["slots_to_filled"].keys()))
            slot_info = dict()

            query = SlotDetails.select(*select_fields).dicts()\
                .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id)\
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)\
                .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)\
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id)\
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)\
                .join(DrugTracker, JOIN_LEFT_OUTER, on=DrugTracker.slot_id == SlotDetails.id)\
                .where((PackDetails.id == pack_id) & (DrugMaster.txr == txr))\
                .order_by(PackGrid.slot_number)

            # delete_drug_tracker_ids = []

            for record in query:
                if record["slot_number"] in slots_to_filled:
                    slots_to_filled.remove(record['slot_number'])
                    for ndc_item in list(map(str, pack_data["slots_to_filled"][record["slot_number"]].keys())):

                        drug_quantity = float(pack_data["slots_to_filled"][record["slot_number"]][ndc_item])

                        if len(ndc_item.split('_')) > 1:
                            ndc = ndc_item.split('_')[0]
                            item_id = ndc_item.split('_')[1]
                        else:
                            ndc = ndc_item.split('_')[0]
                            item_id = None

                        drug_quantity_present, drug_tracker_data, drug_lot_data = get_present_drug_quantity(drug_ids[ndc], item_id,
                                                                                             record['slot_details_id'])

                        diff = drug_quantity - drug_quantity_present

                        if diff < 0:
                            if diff == -1 * drug_quantity_present:
                                delete_list.extend(list(drug_tracker_data.keys()))
                            else:
                                delete_list, update_list = get_update_and_delete_list_for_drug_tracker(
                                    drug_tracker_data, (diff * -1), update_list, delete_list)

                        elif diff == 0:
                            continue

                        elif diff > 0:
                            temp_lot_number = drug_lot_data.get(item_id, {}).get('lot_number')
                            temp_expiry_date = drug_lot_data.get(item_id, {}).get('expiry_date')

                            if temp_lot_number != drug_lot_master_args.get("lot_number"):
                                temp_lot_number = drug_lot_master_args.get("lot_number")
                                temp_expiry_date = drug_lot_master_args.get("expiry_date")

                            """
                            commented the lot_number and expiry below code
                            reason: because of the below changes same lot_number and expiry_date inserted
                                    in the drug_tracker if user fill the ndc from different lot_number and expiry
                            """

                            drug_tracker_details_dict = {
                                "slot_id": record["slot_details_id"],
                                "drug_id": drug_ids[ndc],
                                "pack_id": pack_id,
                                "filled_at": settings.FILLED_AT_DICT[module_id],
                                "canister_id": canister_id,
                                # "expiry_date": drug_lot_data.get(item_id, {}).get('expiry_date') if drug_lot_data.get(
                                #     item_id, {}).get('expiry_date') else drug_lot_master_args.get("expiry_date"),
                                # 
                                # "lot_number": drug_lot_data.get(item_id, {}).get('lot_number') if drug_lot_data.get(
                                #     item_id, {}).get('lot_number') else drug_lot_master_args.get("lot_number"),
                                "expiry_date": temp_expiry_date,
                                "lot_number": temp_lot_number,
                                "created_by": drug_lot_master_args["created_by"]
                            }
                            if canister_id or case_id:
                                drug_tracker_details_dict['case_id'] = item_id

                            drug_tracker_data, created = DrugTracker.get_or_create(**drug_tracker_details_dict)

                            if not created:
                                update_data = {
                                    "id": drug_tracker_data.id,
                                    "drug_quantity": float(drug_tracker_data.drug_quantity) + diff,
                                    "modified_date": get_current_date_time(),
                                    }
                                update_list.append(update_data)
                            else:
                                update_data = {
                                    "id": drug_tracker_data.id,
                                    "drug_quantity": diff,
                                    "modified_date": get_current_date_time(),
                                    "canister_id": canister_id,
                                    "scan_type": scan_type
                                }
                                update_list.append(update_data)

                            if scanned_drug == record["slot_details_drug"]:
                                slot_info[record["slot_number"]] = {"slot_id": record["slot_details_id"],
                                                                    "old_drug_id": record["slot_details_drug"],
                                                                    "required_quantity": record["required_quantity"],
                                                                    "filled_quantity": diff,
                                                                    "same_drug": True,
                                                                    "drug_tracker_id": drug_tracker_data.id,
                                                                    "expiry_date": drug_lot_master_args.get("expiry_date"),
                                                                    "lot_number": drug_lot_master_args.get("lot_number")
                                                                    }
                                required_quantity += diff
                            else:
                                slot_info[record["slot_number"]] = {"slot_id": record["slot_details_id"],
                                                                    "old_drug_id": record["slot_details_drug"],
                                                                    "required_quantity": record["required_quantity"],
                                                                    "filled_quantity": diff,
                                                                    "same_drug": False,
                                                                    "drug_tracker_id": drug_tracker_data.id,
                                                                    "expiry_date": drug_lot_master_args.get(
                                                                        "expiry_date"),
                                                                    "lot_number": drug_lot_master_args.get("lot_number")
                                                                    }
                                required_quantity += diff

            if diff_slot_number:
                logger.debug("Wrong unfilled slot_number {}".format(diff_slot_number))
            response[pack_id] = slot_info

        if update_list or list(set(delete_list)):
            # status = update_drug_tracker_quantity(update_list, delete_list)
            status = update_drug_tracker_data(update_list, delete_list)

        return response

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in get_filled_unfilled_slots_by_pack_id_and_drug_id: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def get_slot_is_filled(args):
    try:
        logger.info("In get_slot_is_filled")

        slot_info = dict()
        pack_id = args["pack_id"]
        drug_id = args["drug_id"]
        is_mfd = args["is_mfd_drug"]
        txr = args["txr"]

        select_fields = [SlotDetails.id.alias("slot_details_id"),
                         SlotDetails.drug_id.alias("old_drug"),
                         DrugTracker.drug_id.alias("dropped_drug"),
                         PackGrid.slot_number,
                         SlotDetails.quantity.alias("required_quantity"),
                         fn.SUM(DrugTracker.drug_quantity).alias("filled_quantity")
                         ]

        query = SlotDetails.select(*select_fields).dicts() \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(DrugTracker, JOIN_LEFT_OUTER, on=DrugTracker.slot_id == SlotDetails.id) \
            .where((PackDetails.id == pack_id) & (DrugMaster.txr == txr))\
            .group_by(PackGrid.slot_number)\
            .order_by(PackGrid.slot_number)

        if is_mfd:
            for record in query:
                if record["filled_quantity"]:
                    if record["required_quantity"] <= record["filled_quantity"]:
                        slot_id = record["slot_details_id"]
                        status_ids = MfdAnalysisDetails.db_get_status_based_on_slot_id(slot_id=slot_id)
                        flag = True

                        for status in status_ids:
                            if status not in (constants.MFD_DRUG_DROPPED_STATUS, constants.MFD_DRUG_MVS_FILLED):
                                flag = False
                                break

                        if flag:
                            slot_info[record["slot_number"]] = {"is_filled": 1}
                        else:
                            slot_info[record["slot_number"]] = {"is_filled": 0}
                    else:
                        slot_info[record["slot_number"]] = {"is_filled": 0}
                else:
                    slot_info[record["slot_number"]] = {"is_filled": 0}
        else:
            for record in query:
                if record["filled_quantity"]:
                    if record["required_quantity"] <= record["filled_quantity"]:
                        slot_info[record["slot_number"]] = {"is_filled": 1}
                    else:
                        slot_info[record["slot_number"]] = {"is_filled": 0}
                else:
                    slot_info[record["slot_number"]] = {"is_filled": 0}

        return slot_info
    except Exception as e:
        logger.error("error in get_slot_is_filled:  {}".format(e))
        raise e


@log_args_and_response
def get_drug_is_filled_in_drug_list(args):
    try:
        logger.info("In get_drug_is_filled_in_drug_list")

        old_drug = None
        drug_info = dict()
        filled_quantity = 0
        required_quantity = 0
        pack_id = args["pack_id"]
        drug_id = args["drug_id"]
        select_fields = [SlotDetails.id.alias("slot_details_id"),
                         SlotDetails.drug_id.alias("old_drug"),
                         DrugTracker.drug_id.alias("dropped_drug"),
                         SlotDetails.quantity.alias("required_quantity"),
                         fn.sum(DrugTracker.drug_quantity).alias("filled_quantity")
                         ]

        query = SlotDetails.select(*select_fields).dicts()\
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id)\
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)\
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)\
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id)\
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)\
            .join(DrugTracker, JOIN_LEFT_OUTER, on=((DrugTracker.slot_id == SlotDetails.id) & (DrugTracker.is_overwrite == 0)))\
            .where((PackDetails.id == pack_id) & (DrugTracker.drug_id == drug_id)) \
            .group_by(PackGrid.slot_number) \
            .order_by(PackGrid.slot_number)

        for record in query:
            old_drug = record["old_drug"]
            if record["required_quantity"]:
                required_quantity += record["required_quantity"]
            else:
                required_quantity += 0
            if record["filled_quantity"]:
                filled_quantity += record["filled_quantity"]
            else:
                filled_quantity += 0

        if old_drug is None:
            old_drug = drug_id

        if (required_quantity == filled_quantity) and ((required_quantity != 0) and (filled_quantity != 0)):
            drug_info[old_drug] = {"is_filled": 1}
        else:
            drug_info[old_drug] = {"is_filled": 0}

        return drug_info
    except Exception as e:
        logger.error("error in get_drug_is_filled_in_drug_list:  {}".format(e))
        raise e


@log_args_and_response
def get_slot_details_pack_drug_tracker_data(drug_data, module_id, assign_user):

    try:
        patient_rx_data: dict = dict()
        slot_details_data: dict = dict()
        pack_drug_tracker_data: list = list()

        for txr, ndc in drug_data.items():
            fetch_txr, drug_id = DrugMaster.db_get_txr_and_drug_id_by_ndc(ndc=ndc)
            logger.info("In get_slot_details_pack_drug_tracker_data drug_id from drug_master: {}".format(drug_id))

            brand_flag, fndc = DrugMaster.db_get_brand_flag_and_fndc_by_drug_id(drug_id=drug_id)
            logger.info("In get_slot_details_pack_drug_tracker_data brand_flag: {}, fndc: {} of drug_id: {}"
                        .format(brand_flag, fndc, drug_id))

            pack_list = get_manual_pack_ids_for_manual_pack_filling(assign_user, txr)
            logger.info("In get_slot_details_pack_drug_tracker_data: pack_list {}".format(pack_list))

            if pack_list:

                select_fields = [DrugMaster.txr,
                                 DrugMaster.ndc,
                                 DrugMaster.brand_flag,
                                 DrugMaster.formatted_ndc,
                                 PackDetails.id.alias("pack_id"),
                                 SlotDetails.id.alias("slot_details_id"),
                                 SlotDetails.drug_id.alias("slot_details_drug"),
                                 SlotDetails.quantity.alias("required_quantity")
                                 ]

                query = (SlotDetails.select(*select_fields)
                         .dicts()
                         .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id)
                         .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                         .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                         .where((PackDetails.id << pack_list) & (DrugMaster.txr == txr))
                         )

                slot_ids: list = list()

                for record in query:
                    allowed = False
                    if record["slot_details_drug"] != drug_id and record["txr"] == txr:
                        if brand_flag == settings.BRAND_FLAG:
                            if record["brand_flag"] == settings.BRAND_FLAG and fndc == record["formatted_ndc"]:
                                allowed = True

                        elif brand_flag == settings.GENERIC_FLAG:
                            if record["brand_flag"] == settings.GENERIC_FLAG:
                                allowed = True

                        # update_dict = {"drug_id": drug_id}
                        if allowed:

                            slot_ids.append(record["slot_details_id"])

                            pack_drug_tracker_dict = dict()
                            pack_drug_tracker_dict["slot_details_id"] = record["slot_details_id"]
                            pack_drug_tracker_dict["previous_drug_id"] = record["slot_details_drug"]
                            pack_drug_tracker_dict["updated_drug_id"] = drug_id
                            pack_drug_tracker_dict["module"] = module_id
                            pack_drug_tracker_dict["created_by"] = assign_user
                            pack_drug_tracker_dict["created_date"] = get_current_date_time()
                            pack_drug_tracker_data.append(pack_drug_tracker_dict)

                if slot_ids:
                    if ndc not in slot_details_data:
                        slot_details_data[ndc] = dict()
                        slot_details_data[ndc]["drug_id"] = drug_id
                        slot_details_data[ndc]["ndc"] = ndc
                        slot_details_data[ndc]["txr"] = txr
                        slot_details_data[ndc]["update_dicts"] = {"drug_id": drug_id}
                        slot_details_data[ndc]["slot_ids"] = slot_ids

                    select_fields_for_patient_rx = [PatientRx.id.alias("patient_rx_id")]

                    query_for_patient_rx = (PatientRx.select(*select_fields_for_patient_rx)
                                            .dicts()
                                            .join(PackRxLink, on=PatientRx.id == PackRxLink.patient_rx_id)
                                            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id)
                                            .where(SlotDetails.id << slot_ids)
                                            )

                    patient_rx_id: list = list()

                    for records in query_for_patient_rx:
                        if records["patient_rx_id"] not in patient_rx_id:
                            patient_rx_id.append(records["patient_rx_id"])

                    if ndc not in patient_rx_data:
                        patient_rx_data[ndc] = dict()
                        patient_rx_data[ndc]["update_dicts"] = {"drug_id": drug_id}
                        patient_rx_data[ndc]["patient_rx_id"] = patient_rx_id
            else:
                logger.info("In get_slot_details_pack_drug_tracker_data: no any pack_ids found: {}".format(pack_list))
        return slot_details_data, pack_drug_tracker_data, patient_rx_data
    except Exception as e:
        logger.error("Error in get_slot_details_pack_drug_tracker_data: {}".format(e))
        raise e


@log_args_and_response
def db_get_drug_tracker_data_by_slot_id_dao(slot_id):
    try:
        return DrugTracker.db_get_drug_tracker_data_by_slot_id(slot_id=slot_id)
    except Exception as e:
        logger.error("Error in db_get_drug_tracker_data_by_slot_id_dao: {}".format(e))
        raise e


@log_args_and_response
def check_case_id_present_in_drug_tracker(case_id):
    try:
        query = (DrugTracker.select(DrugTracker.case_id)
                 .where(DrugTracker.case_id == case_id).limit(1))
        for record in query:
            if record["case_id"]:
                return True
        return False
    except DoesNotExist as e:
        return False
    except Exception as e:
        return False


@log_args_and_response
def update_data_in_drug_tracker_for_canister_tracker(drug_tracker_info_list):
    try:
        status = False
        for item in drug_tracker_info_list:
            status = DrugTracker.update(canister_tracker_id=item['canister_tracker_id']).where(
                DrugTracker.id == item['drug_tracker_id']).execute()
        return status
    except Exception as e:
        logger.error("Error in update_data_in_drug_tracker_for_canister_tracker: {}".format(e))
        raise e


@log_args_and_response
def update_drug_tracker_data(update_drug_tracker, delete_list):
    try:
        status = False
        for item in update_drug_tracker:
           id = item.pop("id")
           status = DrugTracker.update(**item).where(DrugTracker.id == id).execute()

        if delete_list:
            deleted = DrugTracker.delete().where(DrugTracker.id << delete_list).execute()

        return status

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error("Error in update_data_in_drug_tracker_for_canister_tracker: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def get_present_drug_quantity(drug_id,item_id ,slot_id):
    try:

        clauses = []
        clauses.append(DrugTracker.drug_id == drug_id)
        clauses.append(DrugTracker.slot_id == slot_id)

        if item_id:
            clauses.append(DrugTracker.case_id == item_id)

        response_dict = {}
        drug_lot_data = {}
        total_quantity = 0.0
        query = DrugTracker.select(DrugTracker.drug_quantity,
                                   DrugTracker.id,
                                   DrugTracker.case_id,
                                   DrugTracker.lot_number,
                                   DrugTracker.expiry_date).where(functools.reduce(operator.and_, clauses)).dicts()

        for record in query:
            response_dict[record['id']] = {record['case_id']: float(record['drug_quantity'])}
            total_quantity += float(record['drug_quantity'])
            drug_lot_data[record['case_id']] = {
                "expiry_date" : record['expiry_date'],
                "lot_number" : record['lot_number']
            }
        return total_quantity, response_dict, drug_lot_data

    except Exception as e:
        logger.error("Error in get_present_drug_quantity: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def get_update_and_delete_list_for_drug_tracker(drug_tracker_data, drug_quantity, update_list, delete_list):
    try:
        # delete_list = []
        # update_list = []
        for id, case_data in drug_tracker_data.items():
            for case_id, quantity in case_data.items():
                if drug_quantity == quantity:
                    delete_list.append(id)
                    return delete_list, update_list
                drug_quantity -= quantity
                if drug_quantity > 0:
                    delete_list.append(id)
                else:
                    update_data = {
                        "id": id,
                        "drug_quantity": drug_quantity * -1,
                        "modified_date": get_current_date_time(),
                    }
                    update_list.append(update_data)
                if drug_quantity <= 0:
                    return delete_list, update_list
        return delete_list, update_list

    except Exception as e:
        logger.error("Error in get_present_drug_quantity: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def update_drug_tracker_quantity(update_list, delete_list):
    try:
        if update_list:
            for item in update_list:
                for id, quantity in item.items():
                    updated = DrugTracker.update(drug_quantity=quantity,
                                                 modified_date=get_current_date_time()).where(
                        DrugTracker.id == id).execute()
        if delete_list:
            deleted = DrugTracker.delete().where(DrugTracker.id << delete_list).execute()

    except Exception as e:
        logger.error("Error in update_drug_tracker_quantity: {}".format(e), exc_info=True)
        raise e


@log_args_and_response
def db_get_drug_tracker_data_by_slot_id_pack_id_drug_id_dao(slot_id, pack_id, drug_id):
    try:
        query = (DrugTracker.select(DrugTracker)
                 .dicts()
                 .join(DrugMaster, on=DrugMaster.id == DrugTracker.drug_id)
                 .join(UniqueDrug, on=(((fn.IF(DrugMaster.txr.is_null(True),
                                               '', DrugMaster.txr)) == (fn.IF(UniqueDrug.txr.is_null(True),
                                                                              '', UniqueDrug.txr))) &
                                       (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                       )
                       )
                 .where((DrugTracker.pack_id == pack_id),
                        (DrugTracker.slot_id == slot_id),
                        (UniqueDrug.id == drug_id))
                 )

        return query
    except Exception as e:
        logger.error("Error in db_get_drug_tracker_data_by_slot_id_pack_id_drug_id_dao: {}".format(e))
        raise e


@log_args_and_response
def db_delete_drug_tracker_by_slot_id_dao(slot_ids):
    try:
        return DrugTracker.db_delete_drug_tracker_by_slot_id(slot_ids=slot_ids)
    except Exception as e:
        logger.error("Error in db_delete_drug_tracker_by_slot_id_dao: {}".format(e))
        raise e


@log_args_and_response
def db_get_lot_details_by_slot_id(pack_grid_ids, pack_id, drug_id):
    try:
        query = DrugTracker.select(DrugTracker.lot_number, DrugTracker.expiry_date, DrugTracker.case_id,
                                   DrugTracker.drug_quantity, DrugTracker.canister_tracker_id).dicts() \
            .join(SlotHeader, on=SlotHeader.pack_id == DrugTracker.pack_id) \
            .where(DrugTracker.pack_id == pack_id, DrugTracker.drug_id == drug_id, DrugTracker.drug_quantity > 0,
                   SlotHeader.pack_grid_id.in_(pack_grid_ids))
        lot_details = []
        source_details = []
        for record in query:
            if record["lot_number"]:
                source_details.append({"lotNo": record["lot_number"],
                                       "expirationDate": record["expiry_date"],
                                       "caseId": record["case_id"],
                                       "quantity": float(record["drug_quantity"]),
                                       "filledByCanister": True if record["canister_tracker_id"] else False})
                lot_details.append({"lotNo": record["lot_number"],
                                    "expirationDate": record["expiry_date"],
                                    "caseId": record["case_id"]})
        return lot_details, source_details
    except Exception as e:
        logger.error("Error in db_get_lot_details_by_slot_id: {}".format(e), exc_info=True)
        raise e
