import datetime
import functools
import operator
from builtins import list

from peewee import InternalError, IntegrityError, DataError, fn, JOIN_LEFT_OUTER, DoesNotExist

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response, get_current_date_time
from src import constants
from src.model.model_drug_tracker import DrugTracker
from src.model.model_ext_pack_details import ExtPackDetails
from src.model.model_fill_error_details import FillErrorDetails
from src.model.model_pack_details import PackDetails
from src.model.model_canister_master import CanisterMaster
from src.model.model_code_master import CodeMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_error_details import ErrorDetails
from src.model.model_location_master import LocationMaster
from src.model.model_missing_drug_pack import MissingDrugPack
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_canister_usage import PackCanisterUsage
from src.model.model_pack_error import PackError
from src.model.model_pack_fill_error_v2 import PackFillErrorV2
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_pvs_drug_count import PVSDrugCount
from src.model.model_pvs_slot import PVSSlot
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_fill_error_v2 import SlotFillErrorV2
from src.model.model_slot_header import SlotHeader
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger



@log_args_and_response
def get_dropped_quantity_of_unique_drug_in_pack(pack_id: int, pack_grid_id: int, unique_drug_id: int):
    """
    get dropped quantity of unique drug in pack id
    """
    try:
        dropped_qty = SlotDetails.select(fn.floor(SlotDetails.quantity).alias('quantity')) \
                            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
                            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                  (DrugMaster.txr == UniqueDrug.txr))) \
                            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.slot_id == SlotDetails.id) \
                            .where(SlotHeader.pack_id == pack_id,
                                   SlotHeader.pack_grid_id == pack_grid_id,
                                   UniqueDrug.id == unique_drug_id).get()

        return dropped_qty.quantity

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_dropped_quantity_of_unique_drug_in_pack {}".format(e))
        raise e


@log_args_and_response
def get_error_details_by_pack_dao(pack_id: int, pack_grid_id: int, unique_drug_id: int):
    """
    get error details by pack id and drug id in pack grid
    """
    try:
        data = ErrorDetails.select().dicts() \
                                .where(ErrorDetails.pack_id == pack_id,
                                       ErrorDetails.unique_drug_id == unique_drug_id,
                                       ErrorDetails.pack_grid_id == pack_grid_id).get()
        return data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_error_details_by_pack_dao {}".format(e))
        raise e


@log_args_and_response
def pack_fill_error_update_or_create_dao(unique_drug_id: int or None, pack_id: int, pack_fill_error: dict):
    """
    create or update record in pack fill error table
    """
    try:

        return PackFillErrorV2.db_update_or_create(unique_drug_id=unique_drug_id, pack_id=pack_id,
                                                   data=pack_fill_error)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in pack_fill_error_update_or_create_dao {}".format(e))
        raise e


@log_args_and_response
def delete_slot_fill_error_data_dao(fill_error, pack_grid_id) -> bool:
    """
    delete record from slot fill error v2 by fill error id and pack grid id
    """
    try:
        return SlotFillErrorV2.db_delete_slot_fill_error_data(fill_error=fill_error, pack_grid_id=pack_grid_id)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_slot_fill_error_data_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_errors(pack_id):
    """
    Returns reported errors with quantity
    :param pack_id:
    :return: dict
    """
    results: dict = dict()
    unique_rx_ids: set = set()
    try:
        query = SlotHeader.select(
            UniqueDrug.id.alias('unique_drug_id'),
            fn.IF(PackFillErrorV2.id.is_null(True), False, True).alias('error_reported'),
            PackFillErrorV2.note,
            PackFillErrorV2.id.alias('fill_error_id'),
            PackGrid.slot_row,
            PackGrid.slot_column,
            SlotFillErrorV2.broken,
            SlotFillErrorV2.error_qty,
            SlotFillErrorV2.id.alias('slot_fill_error_id'),
            PackFillErrorV2.created_by.alias('reported_by'),
            PackFillErrorV2.created_date.alias('reported_date')
        ).dicts() \
            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.txr == DrugMaster.txr) &
                                 (UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)) \
            .join(PackFillErrorV2,
                  JOIN_LEFT_OUTER, on=(PackFillErrorV2.unique_drug_id == UniqueDrug.id) &
                                      (PackFillErrorV2.pack_id == SlotHeader.pack_id)) \
            .join(SlotFillErrorV2,
                  JOIN_LEFT_OUTER, on=(SlotFillErrorV2.pack_fill_error_id == PackFillErrorV2.id)) \
            .join(PackGrid, JOIN_LEFT_OUTER, on=(SlotFillErrorV2.pack_grid_id == PackGrid.id)) \
            .where(SlotHeader.pack_id == pack_id)
        for record in query:
            if record["unique_drug_id"] not in unique_rx_ids:
                unique_rx_ids.add(record["unique_drug_id"])
                results[record["unique_drug_id"]] = {
                    "unique_drug_id": record["unique_drug_id"],
                    "error_reported": record["error_reported"],
                    "note": record["note"],
                    "fill_error_id": record["fill_error_id"],
                    "reported_by": record["reported_by"],
                    "reported_date": record["reported_date"],
                    "dropped_pills": {},
                    "slot_errors": {}
                }
            if record["slot_fill_error_id"]:
                loc = PackGrid.map_pack_location(
                    record["slot_row"], record["slot_column"]
                )
                results[record["unique_drug_id"]]["slot_errors"][loc] = {
                    "slot_row": record["slot_row"],
                    "slot_column": record["slot_column"],
                    "error_quantity": record["error_qty"],
                    "broken": record["broken"],
                    "slot_fill_error_id": record["slot_fill_error_id"]
                }

        return results
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in delete_slot_fill_error_data_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_dropped_pills_v2(pack_id):
    """
    Returns dropped pill count for given pack_rx_id
    @param pack_id:
    :return: list
    """
    latest_created_date_time = datetime.datetime.now()
    try:
        # in case of deferred pack, to consider the latest record.
        # for rec in SlotTransaction.select(fn.MAX(SlotTransaction.created_date_time).alias(
        #         "latest_created_date_time")).dicts().where(SlotTransaction.pack_id == pack_id):
        #     latest_created_date_time = rec["latest_created_date_time"]
        # no need to check for defereed pack >> now no concept of deferred pack >> so no need to check SlotTransaction data
        # according to latest_created_date_time

        results = dict()
        query = SlotHeader.select(
            PackGrid.slot_row,
            PackGrid.slot_column,
            fn.SUM(SlotTransaction.dropped_qty).alias('dropped_quantity'),
            SlotHeader.id.alias('slot_header_id'),
            UniqueDrug.id.alias('unique_drug_id')
        ).dicts() \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.txr == DrugMaster.txr) &
                                 (UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)) \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.slot_id == SlotDetails.id) \
            .where((SlotTransaction.pack_id == pack_id)) \
            .group_by(SlotDetails.id)
        for item in query:
            loc = PackGrid.map_pack_location(item["slot_row"], item["slot_column"])
            results.setdefault(item["unique_drug_id"], {})
            results[item["unique_drug_id"]].setdefault(loc, {})
            results[item["unique_drug_id"]][loc] = {
                "dropped_qty": item["dropped_quantity"]
            }
        return results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_slot_fill_error_data_dao {}".format(e))
        raise e


@log_args_and_response
def db_slot_details_for_label_printing(pack_id, canister_based_manual=False,
                                       get_robot_to_manual=False,
                                       mfd_canister_fndc_txr_dict=None):
    """
    Returns slot data of pack ID
    canister_based_manual is used to mark drug manual based on canister present or not
    default for manual marking of drug is based on slot transaction (canister_based_manual=False)

    @param pack_id:
    @param canister_based_manual:
    @param mfd_canister_fndc_txr_dict:
    @param get_robot_to_manual:
    """
    txr_list = []
    slot_data: list = list()
    canister_fndc_txr_set: set = set()
    if not mfd_canister_fndc_txr_dict:
        mfd_canister_fndc_txr_dict: dict = dict()

    try:
        DrugMasterAlias = DrugMaster.alias()
        DrugMasterAlias1 = DrugMaster.alias()
        DrugTrackerAlias = DrugTracker.alias()
        UniqueDrugAlias = UniqueDrug.alias()

        if canister_based_manual or get_robot_to_manual:
            pack_status = get_pack_status_value(pack_id=pack_id)
            # batch_id = PackAnalysis.db_get_max_batch_id(pack_id)
            if pack_status.upper() != settings.MANUAL:
                for record in PackAnalysis.select(DrugMaster.txr,
                                                  DrugMaster.formatted_ndc,
                                                  PackAnalysisDetails.canister_id) \
                        .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                        .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
                        .join(CanisterMaster, on=PackAnalysisDetails.canister_id == CanisterMaster.id) \
                        .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id).dicts() \
                        .where(PackAnalysis.batch_id == PackDetails.batch_id,
                               PackAnalysis.pack_id == pack_id,
                               PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED):
                    canister_fndc_txr_set.add((record["formatted_ndc"], record["txr"]))

        query = SlotHeader.select(SlotHeader.hoa_date,
                                  SlotHeader.hoa_time,
                                  PackGrid.slot_row,
                                  PackGrid.slot_column,
                                  SlotHeader.id.alias('slot_header_id'),
                                  SlotDetails.quantity,
                                  fn.SUM(DrugTracker.drug_quantity).alias('filled_quantity'),
                                  SlotDetails.is_manual,
                                  SlotDetails.original_drug_id.alias("original_drug_id"),
                                  PatientRx.pharmacy_rx_no,
                                  PatientRx.sig,
                                  PatientRx.caution1,
                                  PatientRx.caution2,
                                  DrugMasterAlias.ndc.alias("original_drug_ndc"),
                                  fn.IF(DrugMasterAlias1.drug_name.is_null(True), DrugMaster.drug_name,
                                        DrugMasterAlias1.drug_name).alias("drug_name"),
                                  fn.IF(DrugMasterAlias1.ndc.is_null(True), DrugMaster.ndc,
                                        DrugMasterAlias1.ndc).alias("ndc"),
                                  fn.IF(DrugMasterAlias1.strength.is_null(True), DrugMaster.strength,
                                        DrugMasterAlias1.strength).alias("strength"),
                                  fn.IF(DrugMasterAlias1.strength_value.is_null(True), DrugMaster.strength_value,
                                        DrugMasterAlias1.strength_value).alias("strength_value"),
                                  fn.IF(DrugMasterAlias1.drug_name.is_null(False), fn.CONCAT(DrugMasterAlias1.drug_name, ' ', DrugMasterAlias1.strength_value, ' ', DrugMasterAlias1.strength, ' (', DrugMasterAlias1.ndc, ')'),
                                        fn.CONCAT(DrugMaster.drug_name, ' ', DrugMaster.strength_value, ' ', DrugMaster.strength, ' (', DrugMaster.ndc, ')')).alias("drug_full_name"),
                                  fn.IF(DrugMasterAlias1.imprint.is_null(True), DrugMaster.imprint,
                                        DrugMasterAlias1.imprint).alias("imprint"),
                                  fn.IF(DrugMasterAlias1.color.is_null(True), DrugMaster.color,
                                        DrugMasterAlias1.color).alias("color"),
                                  fn.IF(DrugMasterAlias1.shape.is_null(True), DrugMaster.shape,
                                        DrugMasterAlias1.shape).alias("shape"),
                                  fn.IF(DrugMasterAlias1.image_name.is_null(True), DrugMaster.image_name,
                                        DrugMasterAlias1.image_name).alias("image_name"),
                                  fn.IF(DrugMasterAlias1.formatted_ndc.is_null(True), DrugMaster.formatted_ndc,
                                        DrugMasterAlias1.formatted_ndc).alias("formatted_ndc"),
                                  fn.IF(DrugMasterAlias1.id.is_null(True), DrugMaster.id,
                                        DrugMasterAlias1.id).alias("drug_id"),
                                  fn.IF(DrugTracker.id.is_null(True), True,
                                        fn.IF(DrugTracker.drug_quantity != DrugTracker.original_quantity, True,
                                              False)).alias("is_removable"),
                                  fn.IF(DrugMasterAlias1.txr.is_null(True), DrugMaster.txr,
                                        DrugMasterAlias1.txr).alias("txr"),
                                  fn.IF(DrugMasterAlias1.manufacturer.is_null(True), DrugMaster.manufacturer,
                                        DrugMasterAlias1.manufacturer).alias("manufacturer"),
                                  fn.IF(UniqueDrugAlias.id.is_null(True), UniqueDrug.id, UniqueDrugAlias.id).alias("unique_drug_id"),
                                  SlotTransaction.id.alias('slot_trans_id'),
                                  fn.sum(SlotTransaction.dropped_qty).alias('dropped_qty'),
                                  fn.sum(DrugTrackerAlias.drug_quantity).alias('drug_tracker_dropped_qty'),
                                  SlotDetails.pack_rx_id, DrugMaster.txr,
                                  LocationMaster.device_id,
                                  DeviceMaster.name.alias('device_name'),
                                  LocationMaster.location_number,
                                  LocationMaster.display_location,
                                  SlotTransaction.canister_id,  # Canister_id added
                                  CanisterMaster.rfid,
                                  fn.IF(
                                      CanisterMaster.expiry_date <= datetime.date.today() + datetime.timedelta(
                                          settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                      constants.EXPIRED_CANISTER,
                                      fn.IF(
                                          CanisterMaster.expiry_date <= datetime.date.today() + datetime.timedelta(
                                              settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                          constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias(
                                      "expiry_status"),
                                  fn.IFNULL(fn.GROUP_CONCAT(SlotTransaction.mft_drug).coerce(False), '').alias(
                                      'is_mfd_drug'),
                                  fn.SUM((1 - SlotTransaction.mft_drug) * SlotTransaction.dropped_qty).alias(
                                      'pure_robot_drug_qty'),
                                  PackRxLink.id.alias('pack_rx_link_id'),
                                  # total_dropped_qty - total_mft_dropped_qty = pure_robot_drug_qty
                                  DrugStockHistory.is_in_stock,
                                  DrugDetails.last_seen_date.alias('last_seen_on'),
                                  DrugDetails.last_seen_by,
                                  SlotDetails.id.alias('slot_details_id'),
                                  fn.IF(MissingDrugPack.id.is_null(True), False, True).alias('missing_drug'),
                                  DrugTracker.case_id,
                                  SlotFillErrorV2.broken.alias("is_broken_pill"),
                                  SlotFillErrorV2.out_of_class_reported.alias("is_fod")
                                  ) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(DrugMasterAlias, on=DrugMasterAlias.id == SlotDetails.original_drug_id) \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotDetails.id == SlotTransaction.slot_id) \
            .join(DrugTrackerAlias, JOIN_LEFT_OUTER, on=((SlotDetails.id == DrugTrackerAlias.slot_id) &
                                                         (
                                                                     DrugTrackerAlias.filled_at == settings.FILLED_AT_DOSE_PACKER))) \
            .join(DrugTracker, JOIN_LEFT_OUTER, on=SlotDetails.id == DrugTracker.slot_id) \
            .join(DrugMasterAlias1, JOIN_LEFT_OUTER, on=DrugMasterAlias1.id == DrugTracker.drug_id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(UniqueDrugAlias, JOIN_LEFT_OUTER, on=(fn.IF(DrugMasterAlias1.txr.is_null(True), '', DrugMasterAlias1.txr) ==
                                       fn.IF(UniqueDrugAlias.txr.is_null(True), '', UniqueDrugAlias.txr)) &
                                      (DrugMasterAlias1.formatted_ndc == UniqueDrugAlias.formatted_ndc)) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == SlotTransaction.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=SlotTransaction.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER,
                  on=(DrugStockHistory.unique_drug_id == UniqueDrug.id) & (DrugStockHistory.is_active == True) &
                     (PackDetails.company_id == DrugStockHistory.company_id)) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id))) \
            .join(MissingDrugPack, JOIN_LEFT_OUTER, on=(PackRxLink.id == MissingDrugPack.pack_rx_id)) \
            .join(PackFillErrorV2, JOIN_LEFT_OUTER,
                  on=((PackFillErrorV2.pack_id == PackDetails.id) & (PackFillErrorV2.unique_drug_id == UniqueDrug.id))) \
            .join(SlotFillErrorV2, JOIN_LEFT_OUTER, on=((SlotFillErrorV2.pack_fill_error_id == PackFillErrorV2.id) & (
                SlotFillErrorV2.pack_grid_id == PackGrid.id) & (SlotFillErrorV2.rph_error == True) & (
                                                                SlotFillErrorV2.rph_error_resolved == False))) \
            .where(SlotHeader.pack_id == pack_id) \
            .group_by(SlotDetails.id, DrugTracker.drug_id, DrugTracker.case_id)
        for record in query.dicts():
            slot_details_id = record['slot_details_id']
            record["dropped_qty"] = float(record["dropped_qty"]) if record["dropped_qty"] is not None else None
            record["drug_tracker_dropped_qty"] = float(record["drug_tracker_dropped_qty"]) if record["drug_tracker_dropped_qty"] is not None else None
            record["display_drug_name"] = record['drug_name']  # adding new key to keep api backward compatible
            record["drug_name"] = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"]

            fndc_txr = (record["formatted_ndc"], record["txr"])
            if not canister_based_manual:
                if record["dropped_qty"] is None or record["dropped_qty"] < record["quantity"]:
                    record["is_manual"] = True
                else:
                    record["is_manual"] = False
            else:
                if (record["quantity"] % 1) != 0 or fndc_txr not in canister_fndc_txr_set:
                    record["is_manual"] = True
                else:
                    record["is_manual"] = False
            if slot_details_id in mfd_canister_fndc_txr_dict and fndc_txr in mfd_canister_fndc_txr_dict[slot_details_id]:
                mfd_skipped_qty = mfd_canister_fndc_txr_dict[slot_details_id][fndc_txr]['mfd_skipped_quantity']
                mfd_dropped_qty = mfd_canister_fndc_txr_dict[slot_details_id][fndc_txr]['mfd_dropped_quantity']
                mfd_canister_id = mfd_canister_fndc_txr_dict[slot_details_id][fndc_txr]['mfd_canister_id']
                mfd_manual_filled_qty = mfd_canister_fndc_txr_dict[slot_details_id][fndc_txr][
                    'mfd_manual_filled_quantity']
                record['mfd_dropped_quantity'] = mfd_dropped_qty
                record['mfd_skipped_quantity'] = mfd_skipped_qty
                record['mfd_manual_filled_quantity'] = mfd_manual_filled_qty
                record['mfd_canister_id'] = mfd_canister_id
                if not mfd_skipped_qty and mfd_dropped_qty and not mfd_manual_filled_qty:
                    record['is_mfd_drug'] = True
                else:
                    record['is_mfd_drug'] = False
                if mfd_canister_fndc_txr_dict[slot_details_id][fndc_txr]['mfd_skipped_quantity']:
                    record['is_mfd_to_manual'] = True
                else:
                    record['is_mfd_to_manual'] = False

            else:
                record['is_mfd_drug'] = False
                record['is_mfd_to_manual'] = False
                record['mfd_dropped_quantity'] = 0
                record['mfd_skipped_quantity'] = 0
                record['mfd_manual_filled_quantity'] = 0
                record['mfd_canister_id'] = None

            if get_robot_to_manual:
                fndc_txr = (record["formatted_ndc"], record["txr"])
                if fndc_txr in canister_fndc_txr_set:
                    if record["dropped_qty"] is None or record["dropped_qty"] < record["quantity"]:
                        record["is_robot_to_manual"] = True
                        record['is_robot_drug'] = False
                    else:
                        record["is_robot_to_manual"] = False
                        record["is_robot_drug"] = True
                else:
                    if record["dropped_qty"] is not None and record['slot_trans_id']:

                        if record["dropped_qty"] == record["quantity"]:
                            record["is_robot_to_manual"] = False
                            record['is_robot_drug'] = True
                        else:
                            record["is_robot_to_manual"] = True
                            record['is_robot_drug'] = False
                    else:
                        record['is_robot_drug'] = False
                        record["is_robot_to_manual"] = False

            dropped_qty = record['dropped_qty'] if record['dropped_qty'] is not None else 0
            if fndc_txr in canister_fndc_txr_set:
                record['is_manual'] = False

            else:
                if dropped_qty < record['quantity']:
                    record['is_manual'] = True
                elif record['mfd_manual_filled_quantity']:
                    record['is_manual'] = True
                # adding this for fill error flow when slot detail's qty becomes 0 due to non doctor approval but the
                # is_manual value shouldn't change for that
                elif not record['quantity']:
                    pass
                else:
                    record['is_manual'] = False

            # Update the integer values to boolean for frontend processing.
            if record["missing_drug"] == 1:
                record["missing_drug"] = True
            else:
                record["missing_drug"] = False
            txr_list.append(record['txr'])
            slot_data.append(record)
        return slot_data, txr_list
    except DoesNotExist as e:
        logger.error("error in db_slot_details_for_label_printing {}".format(e))
        return None
    except InternalError as e:
        logger.error("error in db_slot_details_for_label_printing {}".format(e))
        return None


@log_args_and_response
def get_pack_status_value(pack_id: int):
    """
    get pack status value by pack id
    """
    try:
        query = PackDetails.select(CodeMaster.value,
                                  CodeMaster.id.alias('pack_status_id')).dicts() \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .where(PackDetails.id == pack_id).get()

        status = query["value"]
        return status

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_pack_status_value {}".format(e))
        raise e


@log_args_and_response
def get_reported_error_slot_number_query(pack_id: int):
    """
    get reported error slot number
    """
    try:
        query = PackFillErrorV2.select(PackGrid.slot_number).dicts() \
            .join(SlotFillErrorV2, on=PackFillErrorV2.id == SlotFillErrorV2.pack_fill_error_id) \
            .join(PackGrid, on=PackGrid.id == SlotFillErrorV2.pack_grid_id) \
            .where(PackFillErrorV2.pack_id == pack_id) \
            .order_by(SlotFillErrorV2.pack_grid_id)

        return query

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_reported_error_slot_number_query {}".format(e))
        raise e


@log_args_and_response
def get_pack_fill_error_slot_details(pack_id: int, slot_number: int):
    """
    get pack fill error slot data from slot fill errorV2 table
    """
    try:
        query = PackFillErrorV2.select(PackFillErrorV2.unique_drug_id,
                                       SlotFillErrorV2.error_qty,
                                       SlotFillErrorV2.broken,
                                       SlotFillErrorV2.out_of_class_reported.alias(
                                           "foreign_object_detected"),
                                       SlotFillErrorV2.actual_qty).dicts() \
            .join(SlotFillErrorV2, on=PackFillErrorV2.id == SlotFillErrorV2.pack_fill_error_id) \
            .join(PackGrid, on=PackGrid.id == SlotFillErrorV2.pack_grid_id) \
            .where(PackFillErrorV2.pack_id == pack_id,
                   PackGrid.slot_number == slot_number)

        return query

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_pack_fill_error_slot_details {}".format(e))
        raise e


@log_args_and_response
def slot_fill_error_create_multiple_record(slot_error_list: list):
    """
    create entry in slot_fill_error for multiple record
    """
    try:
        record = SlotFillErrorV2.db_create_multi_record(slot_error_list, SlotFillErrorV2)
        return record

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in slot_fill_error_create_multiple_record {}".format(e))
        raise e


@log_args_and_response
def add_analytical_data(data: dict) -> dict:
    """
    @param data: dict
    @return: dict
    """
    try:
        logger.info("In add_analytical_data: analysing error_data for " + str(data))
        error_details = get_error_details(data)
        logger.info("In add_analytical_data: error_details_data " + str(error_details))
        pack_canister_usage_details = get_pack_canister_usage_data(data)

        # todo: move in error details dao file
        with db.transaction():
            if error_details:
                error_ids = ErrorDetails.db_add_update_errors(error_details)
                logger.info("In add_analytical_data: error_ids: {}".format(error_ids))
            if pack_canister_usage_details:
                pack_canister_usage_data = PackCanisterUsage.add_pack_canister_usage_details(
                    pack_canister_usage_details)
                logger.info("In add_analytical_data: pack_canister_usage_data: {}".format(pack_canister_usage_data))
            return create_response(True)

    except (InternalError, IntegrityError) as e:
        logger.error("error in add_analytical_data {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in add_analytical_data {}".format(e))
        raise e


@log_args_and_response
def get_pack_canister_usage_data(data):
    """
    @param data:
    @return:
    """
    time_zone = data.get('time_zone', None)
    analytical_date = data.get('fill_date', None)
    pack_id = data.get('pack_id', None)
    clauses = list()
    fill_date = fn.date(fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC, time_zone))
    if time_zone and analytical_date:
        clauses.append(
            (fill_date == analytical_date) | (PackDetails.pack_status == settings.PACK_STATUS['Progress']))
    if pack_id:
        clauses.append((PackDetails.id == pack_id))
    try:
        join_condition = ((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                          (UniqueDrug.txr == DrugMaster.txr))

        pack_details = SlotTransaction.select(SlotTransaction.pack_id.alias('pack_id'),
                                              UniqueDrug.id.alias('unique_drug_id'),
                                              SlotTransaction.location_id,
                                              SlotHeader.pack_grid_id,
                                              SlotTransaction.canister_id).dicts() \
            .join(SlotDetails, on=SlotDetails.id == SlotTransaction.slot_id) \
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotTransaction.drug_id) \
            .join(UniqueDrug, on=join_condition) \
            .join(PackDetails, on=SlotTransaction.pack_id == PackDetails.id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(SlotTransaction.pack_id, SlotHeader.pack_grid_id, UniqueDrug.id)
        return list(pack_details)

    except (IntegrityError, InternalError) as e:
        logger.error("error in get_pack_canister_usage_data {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_pack_canister_usage_data {}".format(e))
        raise e


@log_args_and_response
def get_error_details(data: dict) -> list:
    """
    This function obtains the error details for the given pack
    @param data: dict
    @return: dict
    """
    time_zone = data.get('time_zone', None)
    analytical_date = data.get('fill_date', None)
    pack_id = data.get('pack_id', None)
    slot_error_list = list()
    clauses = list()

    created_date = fn.DATE(fn.CONVERT_TZ(fn.COALESCE(SlotFillErrorV2.created_date,
                                                     PVSDrugCount.created_date), settings.TZ_UTC, time_zone))
    pvs_error_qty = PVSDrugCount.predicted_qty - PVSDrugCount.expected_qty
    PackGridAlias = PackGrid.alias()

    select_fields = [
        fn.COALESCE(PackFillErrorV2.pack_id, SlotHeader.pack_id).alias("pack_id"),
        fn.COALESCE(PackFillErrorV2.unique_drug_id, PVSDrugCount.unique_drug_id).alias("unique_drug_id"),
        UniqueDrug.txr.alias("txr"),
        UniqueDrug.formatted_ndc.alias("formatted_ndc"),
        fn.COALESCE(SlotFillErrorV2.pack_grid_id, SlotHeader.pack_grid_id).alias("pack_grid_id"),
        SlotFillErrorV2.counted_error_qty.alias("error_qty"),
        pvs_error_qty.alias("pvs_error_qty"),
        (fn.IFNULL(SlotFillErrorV2.counted_error_qty, 0) - fn.IFNULL(pvs_error_qty, 0)).alias("mpse_qty"),
        fn.IF(
            fn.ABS((fn.IFNULL(SlotFillErrorV2.counted_error_qty, 0) - fn.IFNULL(pvs_error_qty, 0))) == 0,
            None,
            fn.ABS((fn.IFNULL(SlotFillErrorV2.counted_error_qty, 0) - fn.IFNULL(pvs_error_qty, 0)))
        ).alias("misplaced_qty"),
        fn.IF(((SlotFillErrorV2.counted_error_qty > 0) & (pvs_error_qty > 0)),
              fn.LEAST(fn.ABS(SlotFillErrorV2.counted_error_qty), fn.ABS(pvs_error_qty)), None).alias("extra_qty"),
        fn.IF(((SlotFillErrorV2.counted_error_qty < 0) & (pvs_error_qty < 0)),
              fn.LEAST(fn.ABS(SlotFillErrorV2.counted_error_qty), fn.ABS(pvs_error_qty)), None).alias("missing_qty"),
        fn.IF(SlotFillErrorV2.broken == True, SlotFillErrorV2.broken, False).alias("broken"),
        created_date.alias("created_date"),
        fn.IF(SlotFillErrorV2.out_of_class_reported == True, True,
              fn.IF(PVSDrugCount.expected_qty == 0,  fn.IF(PVSDrugCount.predicted_qty > 0, True, False), False))
    ]
    if time_zone and analytical_date:
        clauses.append(
            (created_date == analytical_date) | (PackDetails.pack_status == settings.PACK_STATUS['Progress']))
    if pack_id:
        clauses.append((PackDetails.id == pack_id))
    with db.transaction():
        try:
            query1 = SlotFillErrorV2.select(*select_fields) \
                .join(PackFillErrorV2, on=PackFillErrorV2.id == SlotFillErrorV2.pack_fill_error_id) \
                .join(UniqueDrug, on=UniqueDrug.id == PackFillErrorV2.unique_drug_id) \
                .join(PackDetails, on=PackDetails.id == PackFillErrorV2.pack_id) \
                .join(SlotHeader, on=((SlotHeader.pack_id == PackDetails.id) &
                                      (SlotHeader.pack_grid_id == SlotFillErrorV2.pack_grid_id))) \
                .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
                .join(PVSSlot, JOIN_LEFT_OUTER, on=PVSSlot.slot_header_id == SlotHeader.id) \
                .join(PVSDrugCount, JOIN_LEFT_OUTER,
                      on=((PVSDrugCount.pvs_slot_id == PVSSlot.id) &
                         (PackFillErrorV2.unique_drug_id == PVSDrugCount.unique_drug_id))) \
                .where(functools.reduce(operator.and_, clauses))

            query2 = PVSDrugCount.select(*select_fields) \
                .join(UniqueDrug, on=UniqueDrug.id == PVSDrugCount.unique_drug_id) \
                .join(PVSSlot, on=PVSSlot.id == PVSDrugCount.pvs_slot_id) \
                .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
                .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id) \
                .join(PackGridAlias, on=PackGridAlias.id == SlotHeader.pack_grid_id) \
                .join(PackFillErrorV2, JOIN_LEFT_OUTER,
                      on=((PackFillErrorV2.pack_id == PackDetails.id) &
                         (PackFillErrorV2.unique_drug_id == PVSDrugCount.unique_drug_id))) \
                .join(SlotFillErrorV2, JOIN_LEFT_OUTER,
                      on=((SlotFillErrorV2.pack_fill_error_id == PackFillErrorV2.id) &
                         (SlotFillErrorV2.pack_grid_id == SlotHeader.pack_grid_id))) \
                .where(functools.reduce(operator.and_, clauses))

            query = (query1 | query2)
            for record in query:
                slot_error_list.append({
                    'pack_id': record.pack_id,
                    'unique_drug_id': record.unique_drug_id,
                    'pack_grid_id': record.pack_grid_id,
                    'error_qty': record.error_qty,
                    'pvs_error_qty': record.pvs_error_qty,
                    'missing': record.missing_qty,
                    'extra': record.extra_qty,
                    'mpse': record.mpse_qty,
                    'broken': record.broken,
                    'out_of_class_reported': record.out_of_class_reported
                })
            return slot_error_list

        except (IntegrityError, InternalError) as e:
            logger.error("error in get_error_details {}".format(e))
            raise e

        except Exception as e:
            logger.error("error in get_error_details {}".format(e))
            raise e


def slot_fill_error_get_or_create(defaults: dict, create_dict: dict) -> tuple:
    """
    get or create record in slot_fill_error
    @param defaults:
    @param create_dict:
    @return:
    """
    try:
        return SlotFillErrorV2.get_or_create(defaults=defaults, **create_dict)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in slot_fill_error_get_or_create {}".format(e))
        raise e


@log_args_and_response
def update_dict_slot_fill_error(update_dict: dict, slot_fill_error_id: int) -> bool:
    """
    Update dict in slot fill error table for given slot fill error id
    """
    try:
        update_status = SlotFillErrorV2.db_update_dict_slot_fill_error(update_dict=update_dict, slot_fill_error_id=slot_fill_error_id)
        return update_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_dict_slot_fill_error {}".format(e))
        raise e


@log_args_and_response
def delete_slot_fill_error_data_by_ids(delete_slot_fill_error_list: list) -> bool:
    """
    delete slot fill error data by slot fill error id
    """
    try:
        delete_status = SlotFillErrorV2.db_delete_slot_fill_error_data_by_ids(delete_slot_fill_error_list=delete_slot_fill_error_list)
        return delete_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_slot_fill_error_data_by_ids {}".format(e))
        raise e



@log_args_and_response
def delete_pack_fill_error_data_and_error_details(pack_id: int, delete_error_details_list: list) -> tuple:
    """
    delete data from pack fill errors data and error details table
    """
    delete_pack_fill_error_ids: list = list()
    pack_fill_error_delete_status = False
    error_details_delete_status = False
    try:
        query = PackFillErrorV2.select(PackFillErrorV2.id).dicts() \
            .join(SlotFillErrorV2, JOIN_LEFT_OUTER, on=SlotFillErrorV2.pack_fill_error_id == PackFillErrorV2.id) \
            .where(PackFillErrorV2.pack_id == pack_id,
                   SlotFillErrorV2.id.is_null(True))

        for record in query:
            delete_pack_fill_error_ids.append(record['id'])

        logger.info("In delete_pack_fill_error_data_and_error_details: pack fill error ids to delete: {}".format(delete_pack_fill_error_ids))
        logger.info('In delete_pack_fill_error_data_and_error_details: delete_error_details ' + str(delete_error_details_list))

        if delete_pack_fill_error_ids:
            pack_fill_error_delete_status = PackFillErrorV2.db_delete_pack_fill_errors_data(delete_pack_fill_error_ids=delete_pack_fill_error_ids)
        if delete_error_details_list:
            error_details_delete_status = ErrorDetails.db_delete_error_details_by_id(delete_error_details_list=delete_error_details_list)

        return pack_fill_error_delete_status, error_details_delete_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_slot_fill_error_data_by_ids {}".format(e))
        raise e


@log_args_and_response
def get_pack_fill_error_data(id: int):
    """
    get pack fill error data by id
    """
    try:
        delete_status = PackFillErrorV2.db_get_pack_fill_error_data(id=id)
        return delete_status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_fill_error_data {}".format(e))
        raise e


@log_args_and_response
def get_pack_slot_error(drug_id, pack_grid_id, pack_id):
    """
       get slot fill error data
    """
    try:
        query = PackFillErrorV2.select(SlotFillErrorV2).dicts() \
            .join(SlotFillErrorV2, on=SlotFillErrorV2.pack_fill_error_id == PackFillErrorV2.id) \
            .where(PackFillErrorV2.pack_id == pack_id,
                   PackFillErrorV2.unique_drug_id == drug_id,
                   SlotFillErrorV2.pack_grid_id == pack_grid_id)
        return query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_slot_error {}".format(e))
        raise e


def get_fill_error_v2_dao(time_zone, system_id, from_date, to_date):

    try:

        reported_date = fn.DATE(fn.CONVERT_TZ(ErrorDetails.created_date, settings.TZ_UTC, time_zone))
        slot_transaction_date = fn.DATE(fn.CONVERT_TZ(SlotTransaction.created_date_time, settings.TZ_UTC, time_zone))

        # query to get slot transaction to get original lcoation of canister

        sub_query = SlotTransaction.select(DeviceMaster.name.alias('device_name'),
                                           LocationMaster.device_id.alias('device_id'),
                                           SlotTransaction.canister_id.alias('canister_id'),
                                           LocationMaster.location_number,
                                           LocationMaster.display_location,
                                           DrugMaster.formatted_ndc,
                                           DrugMaster.txr,
                                           SlotTransaction.pack_id.alias('pack_id')).distinct() \
            .join(DrugMaster, on=DrugMaster.id == SlotTransaction.drug_id) \
            .join(LocationMaster, on=SlotTransaction.location_id == LocationMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(PackDetails, on=PackDetails.id == SlotTransaction.pack_id) \
            .where(PackDetails.system_id == system_id,
                   slot_transaction_date.between(from_date, to_date)).alias('slot_transaction_query')
        query = ErrorDetails.select(
            fn.SUM(ErrorDetails.mpse).alias('misplaced_count'),
            fn.SUM(ErrorDetails.broken).alias('broken_count'),
            fn.SUM(ErrorDetails.extra).alias("extra_count"),
            fn.SUM(ErrorDetails.missing).alias("missing_count"),
            DrugMaster.drug_name,
            DrugMaster.ndc,
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.txr,
            DrugMaster.formatted_ndc,
            reported_date.alias('reported_date'),
            fn.GROUP_CONCAT(
                fn.DISTINCT(
                    fn.CONCAT(
                        sub_query.c.device_id, '--',
                        sub_query.c.canister_id, '--',
                        sub_query.c.display_location, '--',
                        sub_query.c.device_name
                    )
                )
            ).alias('location_list')).dicts() \
            .join(PackDetails, on=ErrorDetails.pack_id == PackDetails.id) \
            .join(UniqueDrug, on=UniqueDrug.id == ErrorDetails.unique_drug_id) \
            .join(DrugMaster, on=DrugMaster.id == UniqueDrug.drug_id) \
            .join(sub_query, JOIN_LEFT_OUTER, on=((sub_query.c.pack_id == PackDetails.id)
                                                  & (sub_query.c.formatted_ndc == UniqueDrug.formatted_ndc)
                                                  & (sub_query.c.txr == UniqueDrug.txr))) \
            .where(reported_date.between(from_date, to_date),
                   PackDetails.system_id == system_id) \
            .group_by(reported_date,
                      DrugMaster.formatted_ndc,
                      DrugMaster.txr)

        return query
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        return error(1020)


@log_args_and_response
def save_pack_error_from_ips(pack_error_list):
    try:
        record = PackError.insert_data(pack_error_list)
        return record
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in save_pack_error_from_ips")
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in save_pack_error_from_ips")
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in save_pack_error_from_ips")
        return error(1020)


@log_args_and_response
def get_slot_id_from_slot_details(pack_id, drug_id, slot_number):
    try:
        slot_id = None
        query = (SlotDetails.select(SlotDetails.id)
                 .dicts()
                 .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id)
                 .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id)
                 .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id)
                 .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                 .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)
                 .join(UniqueDrug, on=(((fn.IF(DrugMaster.txr.is_null(True),
                                               '', DrugMaster.txr)) == (fn.IF(UniqueDrug.txr.is_null(True),
                                                                              '', UniqueDrug.txr))) &
                                       (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                       )
                       )
                 .where((PackDetails.id == pack_id),
                        (UniqueDrug.id == drug_id),
                        (PackGrid.slot_number == slot_number)
                        )
                 )
        for record in query:
            slot_id = record["id"]
            break
        return slot_id
    except Exception as e:
        logger.error("Error in get_slot_id_from_slot_details: {}".format(e))
        raise e


@log_args_and_response
def store_error_packs_dao(reported_by, fill_error_note, pack_id, modified_by):
    try:
        with db.transaction():
            assigned_to = (PackDetails.get(PackDetails.pack_display_id == pack_id)).modified_by
            pack_id = (PackDetails.get(PackDetails.pack_display_id == pack_id)).id
            updated = FillErrorDetails.update(reported_by=reported_by, assigned_to=assigned_to,
                                              fill_error_note=fill_error_note, modified_by=modified_by).where(
                FillErrorDetails.pack_id == pack_id).execute()
            if not updated:
                created = FillErrorDetails.get_or_create(pack_id=pack_id, reported_by=reported_by,
                                                         assigned_to=assigned_to,
                                                         fill_error_note=fill_error_note, modified_by=modified_by)
            updated = PackDetails.update(verification_status=constants.RPH_VERIFICATION_STATUS_FILL_ERROR).where(
                PackDetails.id == pack_id).execute()
            # history_recorded = PackHistory.insert(pack_id=pack_id, action_id=settings.FILL_ERROR_ACTION_ID,
            #                                       action_taken_by=reported_by, old_value=settings.DONE_PACK_STATUS,
            #                                       new_value=settings.FILL_ERROR_STATUS, from_ips=1).execute()
            # pack_status_track_recorded = PackStatusTracker.insert(pack_id=pack_id, status=settings.FILL_ERROR_STATUS,
            #                                                       created_by=reported_by,
            #                                                       reason=constants.FILL_ERROR_REASON).execute()
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in store_error_packs_dao")
        raise e
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in store_error_packs_dao")
        raise e
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        logger.error("Error in store_error_packs_dao")
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in store_error_packs_dao")
        raise e


@log_args_and_response
def update_assignation_dao(assigned_to, pack_id, modified_by, modified_date):
    try:
        status = FillErrorDetails.update(modified_by=modified_by, modified_date=modified_date,
                                         assigned_to=assigned_to).where(FillErrorDetails.pack_id == pack_id).execute()
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in store_error_packs_dao")
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in store_error_packs_dao")
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in store_error_packs_dao")
        return error(1020)


@log_args_and_response
def db_get_slot_wise_qty_for_pack(pack_id, drug_id=None, pack_grid_id=None):
    try:
        clauses = [DrugTracker.pack_id == pack_id, DrugTracker.drug_quantity != 0.00]
        if drug_id:
            clauses.append(DrugTracker.drug_id == drug_id)
        if pack_grid_id:
            clauses.append(SlotHeader.pack_grid_id == pack_grid_id)
        response = {}
        query = SlotHeader.select(DrugTracker.drug_quantity, DrugTracker.id.alias("dt_id"), SlotDetails.id).dicts() \
            .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(DrugTracker, on=DrugTracker.slot_id == SlotDetails.id) \
            .where(*clauses)
        for record in query:
            response[(record["dt_id"], record["id"])] = record["drug_quantity"]
        return response
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_get_slot_wise_qty_for_prn_pack")
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_get_slot_wise_qty_for_prn_pack")
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_get_slot_wise_qty_for_prn_pack")
        return error(1020)


@log_args_and_response
def db_update_slot_wise_error_qty(slot_wise_qty, doctor_approval, initial_slot_wise_qty):
    try:
        with db.transaction():
            original_updation_keys = [key for key in slot_wise_qty if slot_wise_qty[key] != initial_slot_wise_qty.get(key)]
            reason = constants.DOCTOR_APPROVAL_REASON if doctor_approval else constants.PILL_MISSING_REASON

            for key, value in slot_wise_qty.items():
                original_qty = DrugTracker.select(DrugTracker.original_quantity).where(
                    DrugTracker.id == key[0]).scalar()
                if not original_qty and key in original_updation_keys:
                    status = DrugTracker.update({DrugTracker.original_quantity: DrugTracker.drug_quantity, DrugTracker.modified_date: get_current_date_time()}).where(
                        DrugTracker.id == key[0]).execute()
                if key in original_updation_keys:
                    status = DrugTracker.update({DrugTracker.error_reason: reason, DrugTracker.modified_date: get_current_date_time()}).where(
                        DrugTracker.id == key[0]).execute()
                if doctor_approval:
                    sum_for_target = 0.0
                    for key, value in slot_wise_qty.items():
                        if key[1] == key[1]:
                            sum_for_target += float(value)
                    status = SlotDetails.update(quantity=sum_for_target).where(
                        SlotDetails.id.in_([key[1]])).execute()
                else:
                    status = DrugTracker.update(drug_quantity=value, modified_date=get_current_date_time()).where(
                        DrugTracker.id.in_([key[0]])).execute()

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_slot_wise_error_qty")
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_slot_wise_error_qty")
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_slot_wise_error_qty")
        return error(1020)


@log_args_and_response
def db_update_fill_error_pack(pack_id, user_id):
    try:
        updated = PackDetails.update(verification_status=constants.RPH_VERIFICATION_STATUS_FIX_ERROR).where(
            PackDetails.id == pack_id).execute()
        # history_recorded = PackHistory.insert(pack_id=pack_id, action_id=settings.FIX_ERROR_ACTION_ID,
        #                                       action_taken_by=user_id, old_value=settings.FILL_ERROR_STATUS,
        #                                       new_value=settings.FIXED_ERROR_STATUS, from_ips=0).execute()
        # pack_status_track_recorded = PackStatusTracker.insert(pack_id=pack_id, status=settings.FIXED_ERROR_STATUS,
        #                                                       created_by=user_id,
        #                                                       reason=constants.FIX_ERROR_REASON).execute()
        updated = DrugTracker.update({DrugTracker.drug_quantity: DrugTracker.original_quantity}).where(
            DrugTracker.original_quantity <= DrugTracker.drug_quantity,
            DrugTracker.error_reason == constants.PILL_MISSING_REASON, DrugTracker.pack_id == pack_id).execute()
        query = PackFillErrorV2.select(PackFillErrorV2.id.alias("error_id")).dicts().where(
                PackFillErrorV2.pack_id == pack_id)
        if query.exists():
            fill_error_ids = [record['error_id'] for record in list(query)]
            if fill_error_ids:
                updated = SlotFillErrorV2.update(rph_error_resolved=True, modified_by=user_id,
                                                 modified_date=get_current_date_time()).where(
                    SlotFillErrorV2.pack_fill_error_id.in_(fill_error_ids)).execute()
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_fill_error_pack")
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_fill_error_pack")
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_fill_error_pack")
        return error(1020)


@log_args_and_response
def db_update_fod_broken_error(fod, pack_id, broken, pack_grid_id, drug_id, user_id):
    try:
        record, created = PackFillErrorV2.get_or_create(unique_drug_id=drug_id, pack_id=pack_id,
                                                        defaults={"created_by": user_id, "modified_by": user_id,
                                                                  "note": None})
        if not created:
            updated = PackFillErrorV2.update(note=None, modified_by=user_id).where(PackFillErrorV2.pack_id == pack_id,
                                                                                   PackFillErrorV2.unique_drug_id == drug_id).execute()
        update_dict = {
            "broken": broken,
            "out_of_class_reported": fod,
            "rph_error": True,
            "modified_by": user_id,
            "created_by": user_id}
        slot_record, created = SlotFillErrorV2.get_or_create(pack_fill_error_id=record.id, pack_grid_id=pack_grid_id,
                                                             defaults=update_dict)
        if not created:
            updated = SlotFillErrorV2.update(
                broken=broken,
                out_of_class_reported=fod, rph_error=True, modified_by=user_id).where(
                SlotFillErrorV2.id == slot_record.id).execute()
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_fod_broken_error")
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_fod_broken_error")
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_fod_broken_error")
        return error(1020)


@log_args_and_response
def db_update_drug_tracker_qty(drug_id, qty, pack_id, pack_grid_map):
    try:
        # query = DrugTracker.select(DrugTracker.drug_quantity, DrugTracker.original_quantity, DrugTracker.id).dicts() \
        #     .where((DrugTracker.pack_id == pack_id) & (DrugTracker.drug_id == drug_id) & (
        #             DrugTracker.original_quantity < DrugTracker.drug_quantity))
        #
        # qty_map = {}
        # if query.exists():
        #     for record in query:
        #         if qty <= (record['drug_quantity'] - record['original_quantity']):
        #             qty_map[record['id']] = (float(record['drug_quantity']) - float(qty))
        #             qty = 0
        #             break
        #         else:
        #             qty_map[record['id']] = record['original_quantity']
        #             qty -= (record['drug_quantity'] - record['original_quantity'])
        # print(qty_map)
        # for drug_tracker_id, update_qty in qty_map.items():
        #     status = DrugTracker.update(drug_quantity=update_qty, modified_date=get_current_date_time()).where(DrugTracker.id == drug_tracker_id).execute()

        # if there is still some qty left means it is due to doctor approval case, so we gonna remove that by mapping pack grids
        if qty:
            reduce_qty = qty
            qty_map = {}
            for key, value in pack_grid_map.items():
                if reduce_qty > 0:
                    if value <= reduce_qty:
                        pack_grid_map[key] = value
                        reduce_qty -= value
                    else:
                        pack_grid_map[key] = reduce_qty
                        reduce_qty = 0
                else:
                    pack_grid_map[key] = 0
            pack_grid_map = {key: value for key, value in pack_grid_map.items() if value != 0}
            query = DrugTracker.select(DrugTracker.drug_quantity, DrugTracker.id, SlotHeader.pack_grid_id).dicts() \
                .join(SlotDetails, on=SlotDetails.id == DrugTracker.slot_id) \
                .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
                .where(DrugTracker.pack_id == pack_id, DrugTracker.drug_id == drug_id,
                       DrugTracker.drug_quantity != 0.00,
                       SlotHeader.pack_grid_id.in_(list(pack_grid_map.keys())))
            qty_map = {}
            if query.exists():
                for record in query:
                    if not pack_grid_map[str(record["pack_grid_id"])]:
                        continue
                    qty_to_reduce = pack_grid_map[str(record["pack_grid_id"])]
                    if record["drug_quantity"] >= qty_to_reduce:
                        qty_map[record['id']] = (float(record['drug_quantity']) - float(qty_to_reduce))
                        pack_grid_map[str(record["pack_grid_id"])] -= float(qty_to_reduce)
                    else:
                        qty_map[record['id']] = 0
                        pack_grid_map[str(record["pack_grid_id"])] -= (float(record['drug_quantity']))

            print(qty_map)
            for drug_tracker_id, qty in qty_map.items():
                status = DrugTracker.update(drug_quantity=qty, modified_date=get_current_date_time()).where(DrugTracker.id == drug_tracker_id).execute()
        return True

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_drug_tracker_qty")
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_drug_tracker_qty")
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_drug_tracker_qty")
        return error(1020)


@log_args_and_response
def db_fetch_patient_packs(pack_id, rx_id):
    try:
        clauses = []
        query_clauses = [PackDetails.pack_status.in_(
            [constants.PRN_DONE_STATUS, settings.DONE_PACK_STATUS, settings.PROCESSED_MANUALLY_PACK_STATUS]),
            PackDetails.delivery_status == None]
        if pack_id:
            clauses.append(PackRxLink.pack_id == pack_id)
        if rx_id:
            clauses.append(PatientRx.pharmacy_rx_no == rx_id)
        patient_id = PackRxLink.select(PatientRx.patient_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id).where(clauses).scalar()
        if pack_id:
            query_clauses.append(PatientRx.patient_id == patient_id)
        if rx_id:
            query_clauses.append(PatientRx.pharmacy_rx_no == rx_id)
        query = PatientRx.select(PackRxLink.pack_id, PackDetails.pack_display_id, PackDetails.packaging_type,
                                 PackDetails.store_type, PackDetails.verification_status,
                                 PackDetails.pack_status, FillErrorDetails.fill_error_note,
                                 PatientRx.pharmacy_rx_no).dicts() \
            .join(PackRxLink, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(ExtPackDetails, JOIN_LEFT_OUTER, on=(ExtPackDetails.pack_id == PackDetails.id,
                                                       ExtPackDetails.packs_delivery_status != constants.PACK_DELIVERY_STATUS_RETURN_FROM_THE_DELIVERY_ID)) \
            .join(FillErrorDetails, JOIN_LEFT_OUTER, on=FillErrorDetails.pack_id == PackDetails.id) \
            .where(*query_clauses) \
            .group_by(PackDetails.id)

        return list(query), patient_id

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_fetch_patient_packs")
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_fetch_patient_packs")
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_fetch_patient_packs")
        return error(1020)


@log_args_and_response
def db_update_verification_status(pack_list, verification_status, user_id, fill_error_note=None):
    try:
        current_time = get_current_date_time()
        if verification_status == constants.RPH_VERIFICATION_STATUS_CHECKED:
            for pack in pack_list:
                updated = PackDetails.update(verification_status=verification_status, modified_by=user_id,
                                             pack_checked_by=user_id, modified_date=current_time,
                                             pack_checked_time=current_time).where(PackDetails.id == pack).execute()
        elif verification_status == constants.RPH_VERIFICATION_STATUS_FILL_ERROR:
            for pack in pack_list:
                updated = PackDetails.update(verification_status=verification_status, modified_by=user_id,
                                             modified_date=current_time).where(PackDetails.id == pack).execute()
                assigned_to = (PackDetails.get(PackDetails.id == pack)).modified_by
                updated = FillErrorDetails.update(reported_by=user_id, assigned_to=assigned_to,
                                                  fill_error_note=fill_error_note, modified_by=user_id).where(
                    FillErrorDetails.pack_id == pack).execute()
                if not updated:
                    created = FillErrorDetails.get_or_create(pack_id=pack, reported_by=user_id,
                                                             assigned_to=assigned_to,
                                                             fill_error_note=fill_error_note, modified_by=user_id)
        elif verification_status == constants.RPH_VERIFICATION_STATUS_NOT_CHECKED:
            for pack in pack_list:
                updated = PackDetails.update(verification_status=verification_status, modified_by=user_id,
                                             modified_date=current_time, pack_checked_by=None,
                                             pack_checked_time=None).where(PackDetails.id == pack).execute()
        else:
            for pack in pack_list:
                updated = PackDetails.update(verification_status=verification_status, modified_by=user_id,
                                             modified_date=current_time).where(PackDetails.id == pack).execute()
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_verification_status")
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_verification_status")
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_update_verification_status")
        return error(1020)


@log_args_and_response
def db_check_rph_pack(pack_display_id):
    try:
        query = PackDetails.select(PackDetails.id,
                                        fn.CONCAT(PatientMaster.first_name, " ", PatientMaster.last_name).alias(
                                            "patient_name"), PackDetails.verification_status, PackDetails.modified_by,
                                   PackDetails.delivery_status).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
            .where(PackDetails.pack_display_id == pack_display_id, PackDetails.pack_status.in_(
            [constants.PRN_DONE_STATUS, settings.PROCESSED_MANUALLY_PACK_STATUS, settings.DONE_PACK_STATUS]))
        if not query.exists():
            return error(5008)
        record = list(query)[0]
        if record["verification_status"] in [constants.RPH_VERIFICATION_STATUS_ON_HOLD_SYSTEM,
                                             constants.RPH_VERIFICATION_STATUS_ON_HOLD_SYSTEM]:
            patient_name = record["patient_name"]
            user = record["modified_by"]
            return error(21018, f"{patient_name} was put on hold by {user}. No Transaction can be made for patient.")
        if record["delivery_status"] != None:
            return error(21019)
        return create_response(record["id"])

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_check_rph_pack")
        return error(2001)
    except DataError as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_check_rph_pack")
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error("Error in db_check_rph_pack")
        return error(1020)