import functools
import operator
import os
import sys
from collections import defaultdict
from copy import deepcopy
from datetime import date, datetime, timedelta
from peewee import *
from peewee import InternalError, IntegrityError, fn, DataError
from functools import reduce

import settings
from com.pharmacy_software import send_data
from dosepack.base_model.base_model import BaseModel, db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import log_args_and_response, get_canister_volume, \
    get_max_possible_drug_quantities_in_canister, log_args
from src import constants

from src.dao.mfd_dao import get_unique_mfd_drop
from src.exceptions import PharmacySoftwareResponseException, PharmacySoftwareCommunicationException
from src.model.model_action_master import ActionMaster
from src.model.model_batch_change_tracker import BatchChangeTracker
from src.model.model_batch_hash import BatchHash
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_history import CanisterHistory
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_container_master import ContainerMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_facility_master import FacilityMaster
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_mfd_cycle_history import MfdCycleHistory
from src.model.model_mfd_history_comment import MfdCycleHistoryComment
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_fill_error_v2 import PackFillErrorV2
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_header import PackHeader
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_schedule import PatientSchedule
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_skipped_canister import SkippedCanister
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_fill_error_v2 import SlotFillErrorV2
from src.model.model_slot_header import SlotHeader
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_temp_mfd_filling import TempMfdFilling
from src.model.model_unique_drug import UniqueDrug
from src.service.misc import update_couch_db_replenish_wizard
from src.model.model_replenish_skipped_canister import ReplenishSkippedCanister

logger = settings.logger

@log_args_and_response
def get_pack_status_from_ips(pack_list, company_settings):
    """
    :param pack_list: list
    :param company_settings: dict
    :return:
    """
    try:
        data = send_data(
            company_settings["BASE_URL_IPS"],
            settings.IPS_STATUS, {
                "pack_list": pack_list,
                'token': company_settings["IPS_COMM_TOKEN"]
            },
            0, _async=False, token=company_settings["IPS_COMM_TOKEN"], timeout=(5, 25)
        )
        data = data["response"]["data"]
        if not data:
            raise PharmacySoftwareResponseException("Couldn't get ips status from Pharmacy Software. "
                                                    "Kindly contact support.")
        return data

    except (PharmacySoftwareResponseException, PharmacySoftwareCommunicationException) as e:
        logger.error(e, exc_info=True)
        raise PharmacySoftwareResponseException("Couldn't get ips status from Pharmacy Software. "
                                                "Kindly contact support.")

@log_args_and_response
def db_get_progress_filling_left_pack_ids() -> list:
    """
    Replace progress filling left pack ids by batch id
    @param batch_id:
    @return:
    """
    try:
        pack_id_query = PackDetails.select(PackDetails,
                                           PackDetails.id.alias('pack_id')).dicts() \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.pack_id == PackDetails.id) \
            .where(PackDetails.pack_status == settings.PROGRESS_PACK_STATUS,
                   SlotTransaction.id.is_null(True))
        pack_ids = [record['pack_id'] for record in pack_id_query]
        logger.info("In db_get_progress_filling_left_pack_ids, pack_id_query {}".format(pack_id_query))
        return pack_ids
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_progress_filling_left_pack_ids {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_progress_filling_left_pack_ids {}".format(e))
        raise e


@log_args_and_response
def update_pack_analysis_details(analysis_ids):

    try:
        if analysis_ids:
            status = PackAnalysisDetails.update(config_id=None, location_number=None, drop_number=None,
                                                quadrant=None).where(PackAnalysisDetails.id << analysis_ids).execute()
            logger.debug("In update_pack_analysis_details: pack analysis details updated: {}".format(status))
        return True
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in update_pack_analysis_details {}".format(e))
        raise


@log_args_and_response
def update_pack_analysis_details_by_analysis_id(analysis_ids):
    logger.debug("In update_pack_analysis_details")
    try:
        if analysis_ids:
            # status = PackAnalysisDetails.update(config_id=None,
            #                                     location_number=None,
            #                                     drop_number=None,
            #                                     canister_id=None,
            #                                     device_id=None,
            #                                     quadrant=None).where(PackAnalysisDetails.analysis_id << analysis_ids).execute()
            status = PackAnalysisDetails.update(status=constants.SKIPPED_DUE_TO_MANUAL_PACK).where(
                PackAnalysisDetails.analysis_id << analysis_ids).execute()

            logger.info(
                f"In update_pack_analysis_details_by_analysis_id, status updated as SKIPPED_DUE_TO_MANUAL_PACK: {status}")

            return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in update_pack_analysis_details_by_analysis_id {}".format(e))
        raise


@log_args_and_response
def get_pack_list_by_robot(batch_id, device_id):
    logger.debug("In get_pack_list_by_robot")
    try:
        pack_list = list()
        query = PackDetails.select(
            PackDetails.id
        ).join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(PackAnalysisDetails.device_id == device_id, PackDetails.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS])

        for record in query:
            pack_list.append(record.id)
        return list(set(pack_list))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_manual_analysis_ids(quad, drug, pack_list):
    logger.debug("In get_manual_analysis_ids")
    try:
        manual_analysis_ids = []
        query = PackDetails.select(
            PackAnalysisDetails.id,
            PackAnalysisDetails.quadrant,
            fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias('drug'),
        ).join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(PackDetails.id << pack_list, fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr) == drug,
                   PackAnalysisDetails.quadrant == quad)
        for record in query.dicts():
            if record['id'] not in manual_analysis_ids:
                manual_analysis_ids.append(record['id'])
        return manual_analysis_ids
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_canister_drug_quantity_required_in_batch(canister_id_list: list, filling_pending_pack_ids: list):
    """
    Function to get required quantity of canister for current batch and upcoming batch
    @param filling_pending_pack_ids:
    @param canister_id_list:
    @return:
    """
    canister_req_quantity: dict = dict()
    pack_clause: list = list()

    logger.debug("Inside get_canister_drug_quantity_required_in_batch")

    try:
        if len(filling_pending_pack_ids):
            pack_clause.append(((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                                | (PackDetails.id << filling_pending_pack_ids)))

        else:
            pack_clause.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]))

        query = PackAnalysis.select(fn.sum(fn.floor(SlotDetails.quantity)).alias("required_quantity"),
                                    PackAnalysisDetails.canister_id).dicts() \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(pack_clause,
                   (PackAnalysisDetails.canister_id << canister_id_list),
                   (PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED))\
            .group_by(PackAnalysisDetails.canister_id)

        for record in query:
            if record['required_quantity']:
                canister_req_quantity[record['canister_id']] = int(record['required_quantity'])

        return canister_req_quantity

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_canister_drug_quantity_used_in_batch(batch_ids: list):
    """
    Function to get required quantity of canister used in batch
    @param batch_ids:
    @return:
    """
    canister_req_quantity = dict()

    try:
        # batch_status_list = [settings.BATCH_IMPORTED, settings.BATCH_CANISTER_TRANSFER_DONE,
        #                      settings.BATCH_CANISTER_TRANSFER_RECOMMENDED, settings.BATCH_MFD_USER_ASSIGNED]

        query = PackAnalysis.select(fn.sum(fn.floor(SlotDetails.quantity)).alias("required_quantity"),
                                    PackAnalysisDetails.canister_id).dicts() \
                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
                .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                .join(BatchMaster, on=BatchMaster.id == PackAnalysis.batch_id) \
                .where(BatchMaster.id.in_(batch_ids),
                       PackAnalysisDetails.canister_id.is_null(False)) \
                .group_by(PackAnalysisDetails.canister_id)

        for record in query:
            if record['required_quantity']:
                if not record["canister_id"] in canister_req_quantity:
                    canister_req_quantity[record['canister_id']] = 0

                canister_req_quantity[record['canister_id']] += int(record['required_quantity'])

        return canister_req_quantity

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        print("Error in get_canister_drug_quantity_used_in_batch: ", str(e))
        raise

    except Exception as e:
        print("Exception in get_canister_drug_quantity_used_in_batch: ", str(e))


@log_args_and_response
def db_delete_pack_analysis_by_packs(pack_list):
    """
    Function to delete analysis data when mfd recommendation is executed
    to populate re calculated data for this packs
    @param pack_list:
    @return:
    """
    try:
        pack_analysis_ids = list()
        # delete analysis data
        for record in PackAnalysis.select(PackAnalysis.id) \
                .where(PackAnalysis.pack_id << pack_list):
            pack_analysis_ids.append(record.id)
        if pack_analysis_ids:
            status1 = PackAnalysisDetails.delete() \
                .where(PackAnalysisDetails.analysis_id << pack_analysis_ids) \
                .execute()
            status2 = PackAnalysis.delete().where(PackAnalysis.id << pack_analysis_ids) \
                .execute()
            logger.info("In db_delete_pack_analysis_by_packs:  pack analysis data deleted: {}, pack analysis details data deleted: {}".format(status2, status1))
    except (InternalError, IntegerField) as e:
        logger.error(e, exc_info=True)
        raise


def db_save_analysis(data, batch_id, mfd_slots=None):
    """
    Stores analysis data done when importing packs

    @param data:
    @param batch_id:
    :return:
    @param mfd_slots:
    """
    logger.info('pack_analysis_details_save: ' + str(batch_id) + ' ' + str(data))
    try:
        analysis_list = list()
        detailed_list = list()
        # analysis_v2_temp_data = list()

        for pack in data:
            analysis = dict()
            analysis['batch_id'] = batch_id
            analysis['manual_fill_required'] = pack['manual_fill_required']
            analysis['pack_id'] = pack['pack_id']
            # store pack analysis data
            analysis_list.append(analysis)
            analysis_record = BaseModel.db_create_record(analysis, PackAnalysis, get_or_create=False)
            duplicate_record_check = set()
            for item in pack['ndc_list']:
                # TODO : Need to check this condition because slot_id is not in item.
                # if (item["canister_id"], item["drug_id"], item["slot_id"]) in duplicate_record_check:

                # if drug for slot to be dropped from mfd canister don't add in pack analysis
                if mfd_slots and item["slot_id"] in mfd_slots:
                    continue
                if item["slot_id"] in duplicate_record_check:
                    continue  # do not add if already added
                else:
                    # duplicate_record_check.add((item["canister_id"], item["drug_id"], item["slot_id"]))
                    # changed to temporary support in v2 only
                    # todo: change for v2 and v3
                    # duplicate_record_check.add((item["canister_id"], item["drug_id"], item["slot_id"]))
                    duplicate_record_check.add(item['slot_id'])
                detailed_data = dict()
                detailed_data['analysis_id'] = analysis_record.id
                detailed_data['device_id'] = item['device_id']
                detailed_data['location_number'] = item['location_number']
                detailed_data['canister_id'] = item['canister_id']
                detailed_data['quadrant'] = item['quadrant']
                detailed_data['drop_number'] = item['drop_number']
                detailed_data["config_id"] = next(iter(item["config_id"])) if item[
                                                                                  "config_id"] is not None else None
                detailed_data['slot_id'] = item['slot_id']
                detailed_list.append(deepcopy(detailed_data))
        logger.debug('PackAnalysis Data: {}'.format(analysis_list))
        logger.debug('PackAnalysisDetails Data: {}'.format(detailed_list))
        # store analysis data for all drugs in pack
        if detailed_list:
            BaseModel.db_create_multi_record(detailed_list, PackAnalysisDetails)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        print(e)


@log_args_and_response
def db_delete_pack_analysis(batch_id):
    try:
        pack_analysis_ids = list()
        # delete analysis data
        for record in PackAnalysis.select(PackAnalysis.id) \
                .where(PackAnalysis.batch_id == batch_id):
            pack_analysis_ids.append(record.id)
        if pack_analysis_ids:
            status1 = PackAnalysisDetails.delete() \
                .where(PackAnalysisDetails.analysis_id << pack_analysis_ids) \
                .execute()
            status2 = PackAnalysis.delete().where(PackAnalysis.id << pack_analysis_ids) \
                .execute()
            logger.debug("Deleted {} record from PackAnalysisDetails for batch_id: {}".format(status1, batch_id))
            logger.debug("Deleted {} record from PackAnalysis for batch_id: {}".format(status2, batch_id))
        # delete batch hash as analysis depends on it
        BatchHash.delete().where(BatchHash.batch_id == batch_id).execute()
        # delete suggested canister transfers for batch_id
        CanisterTransfers.delete() \
            .where(CanisterTransfers.batch_id == batch_id).execute()
    except (InternalError, IntegerField) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pack_manual_drug_count(pack_id):
    """
    Returns unique manual drug count required in pack
    @param pack_id:
    @return:
    """
    response = {"manual_drug_count": 0}

    try:
        # pack_analysis_query = PackAnalysis.select(
        #     (fn.COUNT(Clause(SQL('DISTINCT'),
        #                      fn.IF((PackAnalysisDetails.device_id.is_null(True) |
        #                             PackAnalysisDetails.canister_id.is_null(True) |
        #                             PackAnalysisDetails.location_number.is_null(True) |
        #                             SlotDetails.quantity << settings.DECIMAL_QTY_LIST),
        #                            SlotDetails.drug_id, None)))).alias("manual_drug_count")
        #
        # ).dicts() \
        #     .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
        #     .join(SlotDetails, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
        #     .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
        #     .join(PackGrid, on=SlotHeader.pack_grid_id == PackGrid.id) \
        #     .where(PackAnalysis.pack_id == pack_id) \
        #     .group_by(PackAnalysis.pack_id).get()

        # TODO: need to check if condition
        pack_analysis_query = PackAnalysis.select(
            (fn.COUNT(Clause(SQL('DISTINCT'),
                             fn.IF((PackAnalysisDetails.status != constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED |
                                    SlotDetails.quantity << settings.DECIMAL_QTY_LIST),
                                   SlotDetails.drug_id, None)))).alias("manual_drug_count")

        ).dicts() \
            .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackGrid, on=SlotHeader.pack_grid_id == PackGrid.id) \
            .where(PackAnalysis.pack_id == pack_id) \
            .group_by(PackAnalysis.pack_id).get()

        response['manual_drug_count'] = pack_analysis_query['manual_drug_count']
        return response

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise

    except DoesNotExist as e:
        logger.error(e)
        return response


@log_args
def db_get_pack_analysis(pack_id, batch_id, device_id, exclude_pack_ids):
    """
    Returns analysis required in getpackdetails api for a pack
    @param batch_id:
    @param pack_id:
    @param exclude_pack_ids:
    @param device_id:
    :return: dict
    """
    pack_analysis = dict()
    canister_list = list()
    canister_batch_quantity = dict()

    drop_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

    LocationMasterAlias = LocationMaster.alias()
    LocationMasterAlias2 = LocationMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()
    CanisterHistoryAlias = CanisterHistory.alias()
    CanisterMasterAlias = CanisterMaster.alias()
    ContainerMasterAlias2 = ContainerMaster.alias()

    sub_query = CanisterHistoryAlias.select(fn.MAX(CanisterHistoryAlias.id).alias('max_canister_history_id'),
                                            CanisterHistoryAlias.canister_id.alias('canister_id')) \
        .group_by(CanisterHistoryAlias.canister_id).alias('sub_query')

    pack_analysis_query = PackAnalysis.select(
        DrugMaster.formatted_ndc, DrugMaster.txr,
        PackAnalysisDetails.device_id,
        CanisterMaster.drug_id,
        CanisterMaster.available_quantity,
        PackAnalysisDetails.canister_id,
        PackAnalysisDetails.location_number,
        DeviceMaster.name.alias('dest_device_name'),
        CanisterMaster.rfid,
        fn.IF(
            CanisterMaster.expiry_date <= date.today() + timedelta(
                settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
            constants.EXPIRED_CANISTER,
            fn.IF(
                CanisterMaster.expiry_date <= date.today() + timedelta(
                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
        CanisterMaster.canister_type,
        LocationMaster.display_location,
        PackAnalysisDetails.drop_number,
        PackAnalysisDetails.quadrant,
        PackAnalysisDetails.slot_id,
        PackAnalysisDetails.config_id,
        LocationMaster.is_disabled.alias('is_location_disabled'),
        LocationMaster.id.alias('missing_location_id'),
        CanisterHistory.created_date.alias('last_seen_time'),
        DeviceMasterAlias.name.alias('previous_device_name'),
        LocationMasterAlias.id.alias('previous_location_id'),
        LocationMasterAlias.display_location.alias('previous_display_location'),
        PackGrid.slot_row,
        PackGrid.slot_column,
        PackGrid.slot_number,
        UniqueDrug.is_powder_pill,
        DrugDimension.approx_volume,
        LocationMasterAlias2.device_id.alias('current_device_id'),
        LocationMasterAlias2.display_location.alias('current_display_location'),
        LocationMasterAlias2.location_number.alias('current_location_number'),
        LocationMasterAlias2.quadrant.alias('current_quadrant'),
        ContainerMasterAlias2.drawer_name.alias('current_drawer_number'),
        fn.IF(CanisterMasterAlias.id.is_null(True), True, False).coerce(False).alias('is_location_empty')
    ) \
        .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
        .join(SlotDetails, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
        .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
        .join(PackGrid, on=SlotHeader.pack_grid_id == PackGrid.id) \
        .join(DrugMaster, JOIN_LEFT_OUTER, on=DrugMaster.id == SlotDetails.drug_id) \
        .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                               (UniqueDrug.txr == DrugMaster.txr))) \
        .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
        .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
        .join(LocationMaster, JOIN_LEFT_OUTER, on=((LocationMaster.device_id == PackAnalysisDetails.device_id) &
                                                   (LocationMaster.location_number ==
                                                    PackAnalysisDetails.location_number))) \
        .join(CanisterMasterAlias, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMasterAlias.location_id) \
        .join(LocationMasterAlias2, JOIN_LEFT_OUTER, on=LocationMasterAlias2.id == CanisterMaster.location_id) \
        .join(ContainerMasterAlias2, JOIN_LEFT_OUTER,
              on=LocationMasterAlias2.container_id == ContainerMasterAlias2.id) \
        .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id) \
        .join(sub_query, JOIN_LEFT_OUTER,
              on=(sub_query.c.canister_id == CanisterMaster.id)) \
        .join(CanisterHistory, JOIN_LEFT_OUTER, on=(CanisterHistory.id == sub_query.c.max_canister_history_id)) \
        .join(LocationMasterAlias, JOIN_LEFT_OUTER,
              on=(CanisterHistory.previous_location_id == LocationMasterAlias.id)) \
        .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=(LocationMasterAlias.device_id == DeviceMasterAlias.id)) \
        .where(PackAnalysis.batch_id == batch_id,
               PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED,
               PackAnalysis.pack_id == pack_id,
               PackAnalysisDetails.device_id == device_id,
               fn.FLOOR(SlotDetails.quantity) > 0)
    try:
        for record in pack_analysis_query.dicts():
            canister_capacity = None

            if record.get('drop_number', None) and record.get('location_number', None) \
                    and record.get('canister_id', None):
                location = PackGrid.map_pack_location(record["slot_row"], record["slot_column"])
                drop_data[record['drop_number']][record['config_id']][location]['canister_data'].append(
                    '{}{}{}'.format(record["formatted_ndc"], settings.FNDC_TXR_SEPARATOR, record['txr'] or ''))

            if record['canister_id']:
                # add canister in canister list
                canister_list.append(record['canister_id'])
                # fetch canister capacity based on approx_volume of drug
                if record['approx_volume']:
                    canister_volume = get_canister_volume(canister_type=record['canister_type'])
                    canister_capacity = get_max_possible_drug_quantities_in_canister(
                        canister_volume=canister_volume,
                        unit_drug_volume=record['approx_volume'])

                logger.info("getpackdetails can capacity data {}, {}, {}".format(record['approx_volume'],
                                                              canister_capacity, record['canister_id']))

            fndc_txr = (record['formatted_ndc'], record['txr'] or '', record['slot_id'])
            pack_analysis[fndc_txr] = {
                'rfid': record['rfid'],
                'canister_type': record['canister_type'],
                'device_id': record['device_id'],
                'current_device_id': record['current_device_id'],
                'canister_id': record['canister_id'],
                'drawer_number': record['current_drawer_number'],
                'drug_id': record['drug_id'],
                'is_powder_pill': record['is_powder_pill'],
                'available_quantity': record['available_quantity'],
                'location_number': record['location_number'],
                'current_location_number': record['current_location_number'],
                'display_location': record['display_location'],
                'quadrant': record['quadrant'],
                'current_quadrant': record['current_quadrant'],
                'current_display_location': record['current_display_location'],
                'config_id': record['config_id'],
                'drop_number': record['drop_number'],
                'dest_device_name': record['dest_device_name'],
                'fndc_txr': '{}{}{}'.format(record["formatted_ndc"], settings.FNDC_TXR_SEPARATOR, record['txr']),
                'previous_device_name': record['previous_device_name'],
                'previous_location_id': record['previous_location_id'],
                'previous_display_location': record['previous_display_location'],
                'last_seen_time': record['last_seen_time'],
                'is_location_disabled': record['is_location_disabled'],
                'is_location_empty': record['is_location_empty'],
                'missing_location_id': record['missing_location_id'],
                'canister_capacity': canister_capacity,
                'expiry_status': record["expiry_status"]
            }
        print(pack_analysis)

        if canister_list:
            canister_batch_quantity = get_canister_drugs_quantity_required_in_batch(
                canister_id_list=canister_list,
                exclude_pack_ids=exclude_pack_ids)
        return pack_analysis, drop_data, canister_batch_quantity
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_replace_canister(canister_id: int, alt_canister_id: int, batch_id: int = None):
    """
    Replace canister_id with alt_canister_id.
    @param batch_id:
    @param canister_id:
    @param alt_canister_id:
    @return:
    """
    try:
        logger.info("In db_replace_canister")

        affected_packs = set()

        pack_ids = db_get_progress_filling_left_pack_ids()
        logger.info(f"In db_replace_canister, progress_filling_left_pack_ids: {pack_ids}")

        sub_query = PackAnalysis.select(PackAnalysis.id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .where(PackAnalysis.batch_id == batch_id)
        if pack_ids:
            sub_query = sub_query.where((PackDetails.pack_status == settings.PENDING_PACK_STATUS) |
                                        (PackDetails.id << pack_ids))
        else:
            sub_query = sub_query.where(PackDetails.pack_status == settings.PENDING_PACK_STATUS)

        pack_query = PackAnalysisDetails.select(PackAnalysis.pack_id).dicts() \
            .join(PackAnalysis, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(PackAnalysisDetails.analysis_id << sub_query,
                   PackAnalysisDetails.canister_id == canister_id) \
            .group_by(PackAnalysis.pack_id)

        for data in pack_query:
            affected_packs.add(data["pack_id"])
        logger.info(f"In db_replace_canister, affected_packs: {affected_packs}")

        query = PackAnalysisDetails.update(canister_id=alt_canister_id) \
            .where(PackAnalysisDetails.analysis_id << sub_query,
                   PackAnalysisDetails.canister_id == canister_id)
        status = query.execute()

        return status, list(affected_packs)
        # logger.info('PackAnalysisDetails Canister Update Status: {} for canister_id: {} '
        #             'and alt_canister_id: {}'.format(
        #     status, canister_id, alt_canister_id
        # ))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_replace_canister:  {}".format(e))
        raise e


@log_args_and_response
def db_replace_canister_pack_queue(canister_id: int, alt_canister_id: int, batch_id: int = None):
    """
    Replace canister_id with alt_canister_id.
    @param batch_id:
    @param canister_id:
    @param alt_canister_id:
    @return:
    """
    try:
        logger.info("In db_replace_canister")

        affected_packs = set()

        pack_ids = db_get_progress_filling_left_pack_ids()
        logger.info(f"In db_replace_canister, progress_filling_left_pack_ids: {pack_ids}")

        sub_query = PackAnalysis.select(PackAnalysis.id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(PackQueue,on=PackDetails.id == PackQueue.pack_id)
        if pack_ids:
            sub_query = sub_query.where((PackDetails.pack_status == settings.PENDING_PACK_STATUS) |
                                        (PackDetails.id << pack_ids))
        else:
            sub_query = sub_query.where(PackDetails.pack_status == settings.PENDING_PACK_STATUS)

        pack_query = PackAnalysisDetails.select(PackAnalysis.pack_id).dicts() \
            .join(PackAnalysis, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(PackAnalysisDetails.analysis_id << sub_query,
                   PackAnalysisDetails.canister_id == canister_id) \
            .group_by(PackAnalysis.pack_id)

        for data in pack_query:
            affected_packs.add(data["pack_id"])
        logger.info(f"In db_replace_canister, affected_packs: {affected_packs}")

        query = PackAnalysisDetails.update(canister_id=alt_canister_id) \
            .where(PackAnalysisDetails.analysis_id << sub_query,
                   PackAnalysisDetails.canister_id == canister_id)
        status = query.execute()

        return status, list(affected_packs)
        # logger.info('PackAnalysisDetails Canister Update Status: {} for canister_id: {} '
        #             'and alt_canister_id: {}'.format(
        #     status, canister_id, alt_canister_id
        # ))
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_replace_canister:  {}".format(e))
        raise e


@log_args_and_response
def db_get_analysis_data(batch_id, pack_ids=None, pack_queue=False, list_type=None):
    """
        Returns Analysis data stored for given pack ids and batch id

    @param batch_id:
    @param pack_ids:
    @param pack_queue:
    @param list_type:
    @return:
    """

    if batch_id:
        try:
            # sub query to select pack drugs
            # sub_q = PackRxLink.select(PackRxLink.id.alias('pack_rx_id'),
            #                           PatientRx.drug_id,
            #                           PackRxLink.pack_id,
            #                           DrugMaster.formatted_ndc,
            #                           DrugMaster.txr) \
            #     .join(PatientRx,
            #           on=(PatientRx.id == PackRxLink.patient_rx_id)) \
            #     .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            #     .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            #     .where(PackDetails.batch_id == batch_id).alias('pack_drugs')
            # syntax to access subquery fields
            # http://docs.peewee-orm.com/en/latest/peewee/query_examples.html#find-the-top-three-revenue-generating-facilities

            query = PackAnalysisDetails.select(PackAnalysis.pack_id,
                                               fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysis.pack_id)).alias(
                                                   'pack_ids_group'),
                                               fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.pack_display_id)).alias(
                                                   'pack_display_ids_group'),
                                               PackDetails.pack_status,
                                               PackAnalysisDetails.canister_id,
                                               SlotDetails.drug_id,
                                               PackAnalysis.manual_fill_required, PackAnalysisDetails.id,
                                               fn.GROUP_CONCAT(fn.DISTINCT(SlotDetails.quantity)).alias(
                                                   'quantities'),
                                               fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('drug_qty'),
                                               fn.SUM(SlotDetails.quantity).alias('total_qty'),
                                               DrugMaster.drug_name,
                                               DrugMaster.strength,
                                               DrugMaster.strength_value,
                                               DrugMaster.imprint,
                                               DrugMaster.image_name,
                                               DrugMaster.shape,
                                               DrugMaster.color,
                                               DrugMaster.formatted_ndc,
                                               DrugMaster.manufacturer,
                                               DrugMaster.ndc,
                                               DrugMaster.txr,
                                               PackAnalysisDetails.device_id,
                                               PackAnalysisDetails.location_number,
                                               DeviceMaster.name.alias('device_name'),
                                               FacilityMaster.facility_name,
                                               PackDetails.pack_display_id,
                                               PackDetails.order_no,
                                               PackDetails.created_date.alias('uploaded_date'),
                                               PatientMaster.last_name,
                                               PatientMaster.first_name,
                                               PatientMaster.patient_no,
                                               PatientMaster.facility_id,
                                               PackHeader.patient_id,
                                               LocationMaster.display_location,
                                               ContainerMaster.drawer_name.alias('drawer_number'),
                                               CanisterMaster.available_quantity,
                                               fn.IF(CanisterMaster.available_quantity < 0, 0,
                                                     CanisterMaster.available_quantity).alias('display_quantity'),
                                               PackDetails.consumption_start_date,
                                               PackDetails.consumption_end_date,
                                               PackHeader.delivery_datetime,
                                               fn.CONCAT(
                                                   PatientSchedule.schedule_id, ':',
                                                   PatientSchedule.facility_id).coerce(False)
                                               .alias('schedule_facility_id')) \
                .dicts() \
                .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(PackDetails, on=PackAnalysis.pack_id == PackDetails.id) \
                .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
                .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id) \
                .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
                .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == PackAnalysisDetails.device_id) \
                .join(PatientSchedule, JOIN_LEFT_OUTER, on=((PatientSchedule.patient_id == PatientMaster.id) &
                                                            (PatientSchedule.facility_id == FacilityMaster.id))) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id)
            if pack_ids:
                query = query.where(PackAnalysis.batch_id == batch_id,
                                    PackDetails.batch_id == batch_id,
                                    PackDetails.pack_status.not_in([settings.DELETED_PACK_STATUS]),
                                    PackAnalysis.pack_id << pack_ids)
            else:
                query = query.where(PackAnalysis.batch_id == batch_id,
                                    PackDetails.pack_status.not_in([settings.DELETED_PACK_STATUS]),
                                    PackDetails.batch_id == batch_id)

            if pack_queue:
                query = query.where(
                    PackDetails.pack_status << ([settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS]))
                if list_type == "drug":
                    query = query.group_by(SlotDetails.drug_id) \
                        .order_by(DrugMaster.drug_name)
                elif list_type == "patient":
                    query = query.group_by(PatientMaster.id, SlotDetails.drug_id) \
                        .order_by(DrugMaster.drug_name)
                elif list_type == "facility":
                    query = query.group_by(PatientMaster.facility_id, SlotDetails.drug_id) \
                        .order_by(DrugMaster.drug_name)
                else:
                    query = query.group_by(PackAnalysis.pack_id, SlotDetails.drug_id, PackAnalysisDetails.canister_id) \
                        .order_by(PackDetails.order_no)

            else:
                query = query.group_by(PackAnalysis.pack_id, SlotDetails.drug_id, PackAnalysisDetails.canister_id) \
                    .order_by(PackDetails.order_no)
            for record in query.dicts():
                record["patient_name"] = record["last_name"] + ", " + record["first_name"]
                record["drug_qty"] = float(record["drug_qty"])
                record["total_qty"] = float(record["total_qty"])
                record['delivery_datetime'] = str(record['delivery_datetime']) if record[
                    'delivery_datetime'] else None

                yield record
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise


@log_args_and_response
def db_get_canister_data(batch_id):
    try:
        for record in PackAnalysisDetails.select(PackAnalysisDetails.canister_id,
                                                 PackAnalysisDetails.device_id,
                                                 PackAnalysisDetails.location_number,
                                                 PackAnalysisDetails.id,
                                                 PackAnalysisDetails.quadrant,
                                                 PackAnalysisDetails.slot_id,
                                                 PackAnalysisDetails.drop_number,
                                                 PackAnalysis.pack_id,
                                                 CanisterTransfers.dest_quadrant,
                                                 CanisterTransfers.dest_device_id,
                                                 PackAnalysis.id.alias('analysis_id')).dicts() \
                .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                .join(PackDetails, on=PackAnalysis.pack_id == PackDetails.id) \
                .join(CanisterTransfers, JOIN_LEFT_OUTER,
                      on=((PackAnalysisDetails.canister_id == CanisterTransfers.canister_id) &
                          (PackAnalysis.batch_id == CanisterTransfers.batch_id))) \
                .where(PackAnalysis.batch_id == batch_id,
                       PackDetails.pack_status.not_in([settings.DELETED_PACK_STATUS]),
                       CanisterTransfers.batch_id == batch_id):
            yield record
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def update_canister_location_v2(analysis_details_ids, system_id):
    """
    This is v2 of update canister location to update canister location
    in pack analysis details in single query using joined updated feature of MySQL.
    This is implemented to overcome timeout during importing packs into DosePacker.
    @param analysis_details_ids:
    @param system_id:
    """
    try:
        if analysis_details_ids:
            print('{}'.format(', '.join(map(str, analysis_details_ids))))
            update_query = "UPDATE pack_analysis_details pad " \
                           "JOIN pack_analysis pa ON pa.id = pad.analysis_id_id " \
                           "JOIN canister_master cm ON cm.id = pad.canister_id_id " \
                           "LEFT OUTER JOIN location_master lm ON lm.id = cm.location_id_id " \
                           "LEFT OUTER JOIN device_master dm ON dm.id = lm.device_id_id AND dm.system_id = {} " \
                           "SET  pad.device_id_id = dm.id , pad.location_number = lm.location_number , " \
                           "pad.quadrant = lm.quadrant " \
                           "WHERE pad.id IN ({});".format(system_id,
                                                          ', '.join(map(str, analysis_details_ids)))
            # query_args = [', '.join(map(str, analysis_details_ids))]
            print('************ {} ***************'.format(update_query))
            result = db.execute_sql(update_query)
            logger.info('Updated rows count for pack_analysis_details {}'.format(result))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_pack_analysis_update_manual_packs(manual_list, manual):
    try:
        return PackAnalysis.db_update_manual_packs(manual_list, manual)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_pack_analysis_update_manual_canister_location_v2(manual_drug_list):
    try:
        canister_list = list()
        logger.info("Inside db_pack_analysis_update_manual_canister_location_v2, analysis_ids".format(manual_drug_list))
        # add canister to new column so that in case recommendation overwrite canister, we still have track
        status = PackAnalysisDetails.update_manual_canister_location_v2(manual_drug_list)
        # delete canisters from reserved canisters for skipped canisters
        if status:
            canister_list = PackAnalysisDetails.db_get_canister_list_from_pack_analysis_ids(manual_drug_list)
            if canister_list:
                delete_reserved_canister_for_skipped_canister(canister_list=canister_list, analysis_id=manual_drug_list)
        return status, canister_list
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def delete_reserved_canister_for_skipped_canister(canister_list, analysis_id=None, batch_id=None):
    # same function in canister_dao
    try:
        logger.info("In delete_reserved_canister_for_skipped_canister")
        canisters_in_use = set()
        canisters_to_delete = list()
        status = None
        clauses = list()

        batch_status = [settings.BATCH_MFD_USER_ASSIGNED,
                        settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
                        settings.BATCH_CANISTER_TRANSFER_DONE,
                        settings.BATCH_IMPORTED]

        pack_status = [settings.PENDING_PACK_STATUS,
                       settings.PROGRESS_PACK_STATUS]

        query = PackDetails.select(PackAnalysisDetails.canister_id).dicts() \
            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(BatchMaster.status << batch_status,
                   PackDetails.pack_status << pack_status,
                   PackAnalysisDetails.canister_id << list(canister_list)) \
            .group_by(PackAnalysisDetails.canister_id)

        if analysis_id:
            clauses.append(PackAnalysis.id.not_in(analysis_id))

        if batch_id:
            clauses.append(PackAnalysis.batch_id.not_in(batch_id))

        if clauses:
            query = query.where(reduce(operator.and_, clauses))

        for canister in query:
            canisters_in_use.add(canister['canister_id'])

        canisters_to_delete = list(set(canister_list) - canisters_in_use)

        logger.info("In delete_reserved_canister_for_skipped_canister, canisters_to_delete {}, canisters_in_use {}"
                    .format(canisters_to_delete, canisters_in_use))

        if canisters_to_delete:
            status = ReservedCanister.delete() \
                .where(ReservedCanister.canister_id << canisters_to_delete).execute()

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_reserved_canister_for_skipped_canister {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in delete_reserved_canister_for_skipped_canister {}".format(e))
        raise e

@log_args_and_response
def get_robot_status(company_id):
    try:
        system_query = DeviceMaster.select(DeviceMaster.system_id,
                                           BatchMaster.id.alias('batch_id'),
                                           fn.GROUP_CONCAT(fn.DISTINCT(BatchMaster.status)).alias('batch_status'),
                                           fn.GROUP_CONCAT(fn.DISTINCT(DeviceMaster.id)).alias('device_ids')
                                           ).dicts() \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=((BatchMaster.system_id == DeviceMaster.system_id) &
                                                    (BatchMaster.status.not_in([settings.BATCH_PROCESSING_COMPLETE,
                                                                                settings.BATCH_DELETED, settings.BATCH_MERGED])))) \
            .where(DeviceMaster.company_id == company_id,
                   DeviceMaster.active == settings.is_device_active,
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT']) \
            .group_by(DeviceMaster.system_id)
        system_data = dict()
        for record in system_query:
            if record['batch_status']:
                status_list = list(map(lambda x: int(x), record['batch_status'].split(",")))
            else:
                status_list = []
            if not status_list:
                system_status = settings.SYSTEM_STATUS['IDLE']
            else:
                if settings.BATCH_IMPORTED in status_list:
                    system_status = settings.SYSTEM_STATUS['PROGRESS']
                else:
                    system_status = settings.SYSTEM_STATUS['PENDING']
            robot_data = list(map(lambda x: int(x), record['device_ids'].split(",")))
            system_data[record['system_id']] = {
                'active_robot': robot_data,
                'system_status': system_status,
                'idle_robot': robot_data,
                'scheduled_end_date': None
            }
        robot_data = PackAnalysisDetails.select(DeviceMaster.system_id,
                                                fn.GROUP_CONCAT(fn.DISTINCT(DeviceMaster.id)).alias('device_ids')
                                                ).dicts() \
            .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
            .join(PackDetails, on=((PackDetails.id == PackAnalysis.pack_id) &
                                   (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
            .join(DeviceMaster, on=PackAnalysisDetails.device_id == DeviceMaster.id) \
            .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                   BatchMaster.status == settings.BATCH_IMPORTED,
                   DeviceMaster.company_id == company_id,
                   DeviceMaster.active == settings.is_device_active,
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT']) \
            .group_by(DeviceMaster.system_id)
        for record in robot_data:
            processing_robot_data = list(map(lambda x: int(x), record['device_ids'].split(",")))
            ideal_robot = set(system_data[record['system_id']]['idle_robot']) - set(processing_robot_data)
            system_data[record['system_id']]['idle_robot'] = ideal_robot
        return system_data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_replenish_query(batch_id, system_id, device_ids, mini_batch_wise=False,
                           exclude_canisters=None, replenish_canisters=None, ordered_packs=False):

    """
    Method to fetch replenish data of canisters
    @param replenish_canisters:
    @param replenish_canisters:
    @param ordered_packs:
    @param batch_id:
    @param system_id:
    @param device_ids:
    @param mini_batch_wise: True - when need to consider replenish for mini batch only else False
    @param exclude_canisters : list of canisters that we don't want to consider for replenish
    @return:
    """
    try:
        # adding packs which are in progress but yet not processed by robot.
        progress_pack_ids = db_get_progress_filling_left_pack_ids()
        pack_clause = list()
        if progress_pack_ids:
            pack_clause.append((PackDetails.pack_status == settings.PENDING_PACK_STATUS) |
                               (PackDetails.id << progress_pack_ids))
        else:
            pack_clause.append(PackDetails.pack_status == settings.PENDING_PACK_STATUS)

        replenish_query = PackDetails.select(PackAnalysisDetails.canister_id,
                                             LocationMaster.id.alias("can_location_id"),
                                             LocationMaster.display_location,
                                             ContainerMaster.drawer_name.alias('drawer_number'),
                                             LocationMaster.quadrant,
                                             DeviceMaster.device_type_id,
                                             DeviceMaster.serial_number,
                                             DrugMaster.ndc,
                                             DeviceMaster.id,
                                             DrugMaster.image_name,
                                             DrugMaster.shape,
                                             DrugMaster.imprint,
                                             fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                                   DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                             DrugDetails.last_seen_by.alias("last_seen_with"),
                                             LocationMaster.location_number,
                                             DeviceMaster.id.alias("device_id"),
                                             DeviceMaster.name.alias('device_name'),
                                             CanisterMaster.available_quantity,
                                             (fn.SUM(fn.FLOOR(SlotDetails.quantity)) -
                                              CanisterMaster.available_quantity).alias('replenish_qty'),
                                             fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('required_qty'),
                                             DrugMaster.concated_drug_name_field().alias('drug_name'),
                                             CanisterMaster.canister_type,
                                             ContainerMaster.drawer_level,
                                             CanisterMaster.drug_id.alias('canister_drug_id'),
                                             DrugMaster.formatted_ndc,
                                             DrugMaster.txr,
                                             DrugDimension.approx_volume
                                             ).dicts() \
            .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
                                    (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                   (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == 1) &
                                                         (DrugStockHistory.company_id == PackDetails.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id))) \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(pack_clause,
                   PackDetails.batch_id == batch_id,
                   PackDetails.system_id == system_id,
                   PackAnalysisDetails.device_id << device_ids,
                   DeviceMaster.device_type_id << [settings.DEVICE_TYPES['ROBOT']],
                   PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)
        if replenish_canisters:
            replenish_query = replenish_query.where(PackAnalysisDetails.canister_id << replenish_canisters)
        if exclude_canisters:
            replenish_query = replenish_query.where(PackAnalysisDetails.canister_id.not_in(exclude_canisters))
        replenish_query = replenish_query.group_by(PackAnalysisDetails.canister_id).order_by(PackDetails.order_no)
        if mini_batch_wise:
            replenish_query = replenish_query.having(fn.SUM(fn.FLOOR(SlotDetails.quantity)) >
                                                     CanisterMaster.available_quantity)
        if ordered_packs:
            replenish_query = replenish_query.order_by(PackAnalysisDetails.device_id, PackAnalysisDetails.quadrant)

        return replenish_query
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_pack_analysis_canisters_data(replace_canisters: dict, batch_id: int, user_id: int, transfer_replace: bool = True,
                                        robot_utility_call: bool = False, device_id = None, company_id = None) -> bool:
    """
    Updates canister id in pack analysis, which allows user to use another canister for same drug
    :param replace_canisters:
    :param batch_id:
    :param user_id:
    :return:
    """
    valid_canisters = ReservedCanister.db_validate_canisters(canisters=list(replace_canisters.values()))
    if not valid_canisters:
        raise ValueError(" One of the alternate canister is already reserved.")
    logger.info('Replacing Pack Analysis Canister for batch_id {}, user_id {} - '
                'replace_canisters: {}'.format(batch_id, user_id, replace_canisters))
    try:
        with db.transaction():
            for canister_id, alt_canister_id in replace_canisters.items():
                if transfer_replace and not robot_utility_call and batch_id:
                    # update canister in canister transfer
                    status = CanisterTransfers.db_replace_canister(batch_id=batch_id,
                                                                   canister_id=canister_id,
                                                                   alt_canister_id=alt_canister_id)
                    logger.info("In _update_pack_analysis_canisters: canister updated in canister transfer: {}".format(status))

                    # update canister in pack_analysis
                    replace_can_status, affected_packs = db_replace_canister(batch_id=batch_id,
                                                                             canister_id=canister_id,
                                                                             alt_canister_id=alt_canister_id)
                    logger.info("In _update_pack_analysis_canisters: replace_can_status: {}".format(replace_can_status))

                # update canister in pack_analysis
                if robot_utility_call:
                    batch_id = None
                    replace_can_status, affected_packs = db_replace_canister_pack_queue(
                        canister_id=canister_id,
                        alt_canister_id=alt_canister_id)
                    if device_id and company_id:
                        args = {"company_id": company_id,
                                "device_id": device_id,
                                "canister_id": canister_id}
                        status = update_couch_db_replenish_wizard(args)
                        logger.info(f"In update_pack_analysis_canisters_data, replenish-wizard updated. status: {status}")

                else:
                    replace_can_status, affected_packs = db_replace_canister(batch_id=batch_id,
                                                                             canister_id=canister_id,
                                                                             alt_canister_id=alt_canister_id)
                logger.info("In _update_pack_analysis_canisters: replace_can_status: {}".format(replace_can_status))

                # update canister in reserved canister
                reserved_can_status = ReservedCanister.db_replace_canister(canister_id=canister_id,
                                                                           alt_canister_id=alt_canister_id)
                logger.info("In _update_pack_analysis_canisters: update canister in reserved canister: {}".format(
                    reserved_can_status))

            BatchChangeTracker.db_save(batch_id=batch_id,
                                       user_id=user_id,
                                       action_id=ActionMaster.ACTION_ID_MAP[ActionMaster.UPDATE_ALT_CANISTER],
                                       params={"replace_canisters": replace_canisters,
                                               "batch_id": batch_id,
                                               "user_id": user_id},
                                       packs_affected=affected_packs)
        return True

    except (InternalError, IntegrityError, ValueError) as e:
        logger.error("error in _update_pack_analysis_canisters {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in _update_pack_analysis_canisters {}".format(e))
        raise e


@log_args_and_response
def update_pack_analysis_details_by_analysis_slot_id(update_dict: dict, analysis_ids: list, slot_ids: list):
    """
    Function to update pack analysis details by analysis id and slot ids
    @param update_dict:
    @param analysis_ids:
    @param slot_ids:
    @return:
    """
    try:
        pack_analysis_status = PackAnalysisDetails.db_update_pack_analysis_details_by_analysis_id(update_dict=update_dict,
                                                                                                  analysis_id=analysis_ids,
                                                                                                  slot_id=slot_ids)
        return pack_analysis_status

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        print("Error in update_pack_analysis_details_by_analysis_slot_id: ", str(e))
        raise

    except Exception as e:
        print("Exception in update_pack_analysis_details_by_analysis_slot_id: ", str(e))


@log_args_and_response
def db_get_drop_time(device_ids, system_id, pack_ids):
    if pack_ids is None:
        raise ValueError('Invalid argument')

    total_packs = pack_ids
    in_progress_packs = PackDetails.select(PackDetails.id).dicts() \
        .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
                                (PackAnalysis.batch_id == PackDetails.batch_id))) \
        .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
        .join(SlotTransaction, on=SlotTransaction.pack_id == PackDetails.id) \
        .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
        .where(PackDetails.system_id == system_id,
               PackDetails.pack_status << [settings.PROGRESS_PACK_STATUS],
               PackAnalysisDetails.device_id << device_ids) \
        .group_by(PackDetails.id)
    drop_complete_packs = [record['id'] for record in in_progress_packs]
    clauses = list()
    clauses.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS,
                                                settings.PROGRESS_PACK_STATUS]))  # can remove this condition as pack queue have only pending and progress packs only.
    # clauses.append((PackDetails.batch_id == batch_id))
    clauses.append((PackDetails.system_id == system_id))

    if drop_complete_packs:
        pack_ids = list(set(pack_ids) - set(drop_complete_packs))
    if not pack_ids:
        return 0, 0, 0, True
    clauses.append((PackDetails.id << pack_ids))
    mfd_clauses = clauses.copy()
    mfd_clauses.append((MfdAnalysis.dest_device_id << device_ids))
    clauses.append((PackAnalysisDetails.device_id << device_ids))

    try:
        query = PackDetails.select(PackAnalysis.pack_id,
                                   fn.CONCAT(PackAnalysis.pack_id, '#', PackAnalysisDetails.drop_number).coerce(
                                       False).alias('pack_drop'),
                                   PackAnalysisDetails.drop_number).dicts() \
            .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
                                    (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(functools.reduce(operator.and_, clauses))
        query = query.group_by(PackAnalysis.pack_id, PackAnalysisDetails.drop_number)

        mfd_query = get_unique_mfd_drop(mfd_clauses)
        drops = set()
        pending_packs = set()
        for record in query:
            drops.add(record['pack_drop'])
            pending_packs.add(record['pack_id'])
        for record in mfd_query:
            drops.add(record['pack_drop'])
            pending_packs.add(record['pack_id'])

        logger.info('Drops_Info: ' + str(drops))
        logger.info('pending packs current batch: ' + str(pending_packs))
        drop_time = len(list(drops))
        pending_packs_count = len(list(pending_packs))

        # timer_update = PackDetails.select(PackDetails.id, PackDetails.pack_status).dicts() \
        #     .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
        #                             (PackAnalysis.batch_id == PackDetails.batch_id))) \
        #     .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
        #     .where(PackDetails.pack_status << [settings.PROGRESS_PACK_STATUS,
        #                                        settings.DONE_PACK_STATUS,
        #                                        settings.PROCESSED_MANUALLY_PACK_STATUS],
        #            PackDetails.batch_id == batch_id,
        #            PackDetails.system_id == system_id,
        #            PackDetails.id << total_packs,
        #            PackAnalysisDetails.device_id << device_ids) \
        #     .order_by(PackDetails.order_no) \
        #     .group_by(PackDetails.id) \
        #     .count()
        timer_update = 21
        current_mini_batch_time = drop_time * settings.PER_DROP_TIME
        blink_timer = False
        if pending_packs_count <= settings.MINI_BATCH_BLINK_PACK_COUNT:
            blink_timer = True
        return current_mini_batch_time, pending_packs_count, timer_update, blink_timer

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_pending_progress_pack_count(system_id: int, batch_id: int, status_list: list, device_id: int):
    """

    @param system_id:
    @param batch_id:
    @param status_list:
    @param device_id:
    @return:
    """
    try:
        pack_id_query = PackDetails.select(PackDetails,
                                           PackDetails.id.alias('pack_id')).dicts() \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .where(PackDetails.batch_id == batch_id,
                   PackDetails.pack_status << status_list,
                   PackAnalysisDetails.device_id == device_id) \
            .group_by(PackDetails.id)
        pack_ids = [record['pack_id'] for record in pack_id_query]
        return pack_ids

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_canister_drugs_quantity_required_in_batch(canister_id_list: list,
                                                 exclude_pack_ids: list) -> dict:
    """
    Function to get required quantity of canister for given batch
    @param batch_id:
    @param canister_id_list:
    @param exclude_pack_ids:
    @return:
    """
    canister_req_quantity: dict = dict()
    pack_clause: list = list()
    try:
        # adding packs which are in progress but yet not processed by robot.
        pack_id_query = PackDetails.select(PackDetails,
                                           PackDetails.id.alias('pack_id')).dicts() \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.pack_id == PackDetails.id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(PackDetails.pack_status == settings.PROGRESS_PACK_STATUS,
                   SlotTransaction.id.is_null(True))
        pack_ids = [record['pack_id'] for record in pack_id_query]

        if pack_ids:
            if exclude_pack_ids:
                pack_ids = list(set(pack_ids) - set(exclude_pack_ids))
            if pack_ids:
                pack_clause.append(((PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
                                    | (PackDetails.id << pack_ids)))
            else:
                pack_clause.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]))

        else:
            pack_clause.append((PackDetails.pack_status << [settings.PENDING_PACK_STATUS]))

        query = PackAnalysis.select(fn.sum(fn.floor(SlotDetails.quantity)).alias("required_quantity"),
                                    PackAnalysisDetails.canister_id).dicts() \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(pack_clause,
                   (PackAnalysisDetails.canister_id << canister_id_list),
                   (PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)) \
            .group_by(PackAnalysisDetails.canister_id)

        for record in query:
            if record['required_quantity']:
                canister_req_quantity[record['canister_id']] = int(record['required_quantity'])

        return canister_req_quantity

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_device_id_from_pack_list(pack_list: list)-> set:
    """
    Get device_id from which packs is to be processed for given pack id list
    @param pack_list:
    @return:
    """
    try:
        device_id_set = set()
        query = PackDetails.select(fn.GROUP_CONCAT(fn.DISTINCT(PackAnalysisDetails.device_id)).alias("auto_device_id"),
                                   fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.dest_device_id)).alias("mfd_device_id")).dicts() \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(PackAnalysis, JOIN_LEFT_OUTER, on=((PackAnalysis.id == PackAnalysisDetails.analysis_id) &
                                                     (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .where(PackDetails.id << pack_list) \
            .group_by(PackDetails.id)

        for record in query:
            logger.debug("Auto Device ID: {}, MFD Device ID: {}".format(record['auto_device_id'],
                                                                        record['mfd_device_id']))
            if record['auto_device_id']:
                device_id_set.update(set(record['auto_device_id']))

            if record['mfd_device_id']:
                device_id_set.update(set(record['mfd_device_id']))

        return device_id_set

    except Exception as e:
        logger.error("Exception in get_device_id_from_pack_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Exception in get_device_id_from_pack_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_status_in_pack_analysis_details(canister_id, company_id, device_id):
    try:
        logger.info("Inside get_analysis_ids_to_update_status")

        status = None
        fndc_txr = None
        system_id = None
        canister_list = list()
        reverted_packs = set()
        # pack_analysis_ids = set()
        canister_status_list = list()
        pack_analysis_details_ids = set()

        # #packs with progree status and slot transaction not started yet
        # progress_packs_query = PackDetails.select(PackAnalysisDetails.id,
        #                                           PackDetails.id.alias("pack_id"),
        #                                           PackAnalysisDetails.device_id).dicts() \
        #                         .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
        #                         .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
        #                         .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.pack_id == PackDetails.id) \
        #                         .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
        #                         .where(PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_SKIPPED,
        #                                PackDetails.pack_status == settings.PROGRESS_PACK_STATUS,
        #                                PackAnalysisDetails.canister_id == canister_id,
        #                                SlotTransaction.id.is_null(True),
        #                                BatchMaster.status == settings.BATCH_IMPORTED) \
        #                         .group_by(PackAnalysisDetails.id)
        #
        # for record in progress_packs_query:
        #     pack_analysis_ids.add(record["id"])
        #     reverted_packs.add(record["pack_id"])
        #     device_id =record["device_id"]
        #
        # logger.info(
        #     f"In update_status_in_pack_analysis_details, pack_analysis_ids of progress_pending_packs: {pack_analysis_ids}, pack_ids: {reverted_packs}")

        # packs with pending status

        # pending_packs_query = PackQueue.select(PackAnalysisDetails.id,
        #                                        PackDetails.id.alias("pack_id"),
        #                                        PackDetails.system_id,
        #                                        PackAnalysisDetails.device_id).dicts() \
        #                         .join(PackDetails, on=PackDetails.id == PackQueue.pack_id) \
        #                         .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
        #                         .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
        #                         .where(PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_SKIPPED,
        #                                PackDetails.pack_status == settings.PENDING_PACK_STATUS,
        #                                PackAnalysisDetails.canister_id == canister_id) \
        #                         .group_by(PackAnalysisDetails.id)

        # txr = DrugMaster.select(DrugMaster.formatted_ndc, DrugMaster.txr).dicts() \
        #     .join(CanisterMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
        #     .where(CanisterMaster.id == canister_id)

        fndc_txr = DrugMaster.select((DrugMaster.concated_fndc_txr_field(sep="##")).alias("drug_id")).dicts() \
            .join(CanisterMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where(CanisterMaster.id == canister_id)

        for record in fndc_txr:
            fndc_txr = record["drug_id"]

        canister_query_with_replenish_skipped_canister = CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
                                                                               fn.GROUP_CONCAT(fn.DISTINCT(
                                                                                   PackDetails.id
                                                                               )).coerce(False).alias("reverted_packs"),
                                                                               PackDetails.system_id
                                                                               ).dicts()\
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
            .join(ReplenishSkippedCanister, on=CanisterMaster.id == ReplenishSkippedCanister.canister_id)\
            .join(PackDetails, on=PackDetails.id == ReplenishSkippedCanister.pack_id)\
            .join(PackQueue, on=PackDetails.id == PackQueue.pack_id)\
            .where((DrugMaster.concated_fndc_txr_field(sep="##") == fndc_txr) &
                   (ReplenishSkippedCanister.device_id == device_id) &
                   (CanisterMaster.active == settings.is_canister_active) &
                   (PackDetails.pack_status == settings.PENDING_PACK_STATUS))\
            .group_by(CanisterMaster.id)

        for record in canister_query_with_replenish_skipped_canister:
            if record["canister_id"] not in canister_list:
                canister_list.append(record["canister_id"])

            revert_canister_packs = list(map(int, record["reverted_packs"].split(",")))
            # for pack in revert_canister_packs:
            #     reverted_packs.add(pack)
            reverted_packs.update(set(revert_canister_packs))

            # system_id = record["system_id"]

        canister_query_with_pack_analysis_details = CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
                                                                          fn.GROUP_CONCAT(fn.DISTINCT(
                                                                              PackDetails.id
                                                                          )).coerce(False).alias("reverted_packs"),
                                                                          fn.GROUP_CONCAT(fn.DISTINCT(
                                                                              PackAnalysisDetails.status
                                                                          )).coerce(False).alias("status"),
                                                                          PackDetails.system_id
                                                                          ).dicts()\
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
            .join(PackAnalysisDetails, on=CanisterMaster.id == PackAnalysisDetails.canister_id)\
            .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)\
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id)\
            .join(PackQueue, on=PackDetails.id == PackQueue.pack_id)\
            .where((DrugMaster.concated_fndc_txr_field(sep="##") == fndc_txr) &
                   (PackAnalysisDetails.device_id == device_id) &
                   (CanisterMaster.active == settings.is_canister_active) &
                   (PackDetails.pack_status == settings.PENDING_PACK_STATUS)
                   )\
            .group_by(CanisterMaster.id)

        for record in canister_query_with_pack_analysis_details:
            if record["canister_id"] not in canister_list:
                canister_list.append(record["canister_id"])

            status_list = list(map(int, record["status"].split(",")))
            # for status_id in status_list:
            #     canister_status_list.append(status_id)
            canister_status_list.extend(status_list)

            revert_canister_packs = list(map(int, record["reverted_packs"].split(",")))
            # for pack in revert_canister_packs:
            #     reverted_packs.add(pack)
            reverted_packs.update(set(revert_canister_packs))

            system_id = record["system_id"]

        if constants.REPLENISH_CANISTER_TRANSFER_SKIPPED in canister_status_list:
            # pack_analysis_ids_query = PackAnalysis.select(PackAnalysis.id.alias("pack_analysis_ids")).dicts()\
            #     .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id)\
            #     .where(PackDetails.id << list(reverted_packs))

            pack_analysis_details_ids_query = PackAnalysisDetails.select(
                PackAnalysisDetails.id.alias("pack_analysis_details_id")
            ).dicts()\
                .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)\
                .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id)\
                .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
                .where((PackAnalysis.pack_id << list(reverted_packs)) &
                       (DrugMaster.concated_fndc_txr_field(sep="##") == fndc_txr)
                       )

            for record in pack_analysis_details_ids_query:
                pack_analysis_details_ids.add(record["pack_analysis_details_id"])

        logger.info(f"In update_status_in_pack_analysis_details, pack_analysis_details_ids: {pack_analysis_details_ids}, packs: {reverted_packs}")

        if pack_analysis_details_ids:
            # status = PackAnalysisDetails.update(status=constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED) \
            #             .where(PackAnalysisDetails.analysis_id << list(pack_analysis_ids)).execute()
            status = PackAnalysisDetails.update(status=constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)\
                .where(PackAnalysisDetails.id << list(pack_analysis_details_ids)).execute()

            logger.info(f"In update_status_in_pack_analysis_details, update pack analysis details --> status:{status}")

        args = {"company_id": company_id,
                "device_id": device_id,
                "canister_id": canister_id}
        status = update_couch_db_replenish_wizard(args)

        logger.info(f"In update_status_in_pack_analysis_details, replenish-wizaed updated status --> status:{status}")

        return status, reverted_packs, (system_id, device_id)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(f"Error in update_status_in_pack_analysis_details: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in update_status_in_pack_analysis_details: {e}")
        raise e


@log_args_and_response
def update_batch_change_tracker_after_replenish_skipped_canister(canister_id, user_id, device_id, reverted_packs):
    """
    when user skip canister, we insert those data in batch change tracker
    but when user replenish skip canister,we need to insert data of actually which packs are affected due to skip
    :param canister_id:
    :param batch_id:
    :param user_id:
    :param device_id:
    :return:
    """
    try:
        logger.info("Inside update_batch_change_tracker_after_replenish_skipped_canister")

        # affected_packs: list = list()
        # insert_dict: dict = dict()
        status = None
        batch_id = None

        logger.info(f"In update_batch_change_tracker_after_replenish_skipped_canister, batch_id: {batch_id}")
        # pack_query = PackDetails.select(PackDetails.id).dicts() \
        #             .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
        #             .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
        #             .where(PackDetails.batch_id == batch_id,
        #                    PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_SKIPPED,
        #                    PackAnalysisDetails.canister_id == canister_id) \
        #             .group_by(PackDetails.id)
        #
        # logger.info(f"In update_batch_change_tracker_after_replenish_skipped_canister, pack_query:{pack_query}")
        #
        # for pack in pack_query:
        #     affected_packs.append(pack["id"])
        #
        # logger.info(
        #     f"In update_batch_change_tracker_after_replenish_skipped_canister, affected_packs: {affected_packs}")

        if reverted_packs:

            logger.info(f"In update_batch_change_tracker_after_replenish_skipped_canister")

            BatchChangeTracker.db_save(batch_id=batch_id,
                                       user_id=user_id,
                                       action_id=constants.ACTION_ID_MAP[constants.REPLENISH_REVERTED_PACKS],
                                       params={"canister_list": [canister_id],
                                               "batch_id": batch_id,
                                               "user_id": user_id},
                                       packs_affected=list(reverted_packs)
                                       )
            logger.info(f"In update_batch_change_tracker_after_replenish_skipped_canister, inserted in batch change tracker.")
            status = True
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(f"Error in update_batch_change_tracker_after_replenish_skipped_canister: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in update_batch_change_tracker_after_replenish_skipped_canister: {e}")
        raise e


@log_args_and_response
def db_delete_pack_analysis_details_slots(slot_ids):
    """
    Function to delete manual slots from PackAnalysisDetails
    @param slot_ids:
    @return:
    """
    try:
        if slot_ids:
            status1 = PackAnalysisDetails.delete() \
                .where(PackAnalysisDetails.slot_id << slot_ids) \
                .execute()

            logger.debug("Deleted {} record from PackAnalysisDetails for batch_id".format(status1))

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_pack_wise_skipped_drug(pack_list: list, device_id):
    try:
        batch_id = None
        test_pack_id = None
        pack_wise_skipped_drug = dict()

        batch_id_query = PackDetails.select(PackDetails.batch_id).dicts()\
            .where(PackDetails.id << pack_list).group_by(PackDetails.batch_id)
        for batch in batch_id_query:
            batch_id = batch["batch_id"]

        query = PackAnalysisDetails.select(PackDetails.id.alias("pack_id"),
                                           fn.GROUP_CONCAT(
                                               fn.DISTINCT(
                                                   PackAnalysisDetails.canister_id)
                                           ).alias("canister_ids"),
                                           fn.GROUP_CONCAT(
                                               fn.DISTINCT(
                                                   PackAnalysisDetails.status)
                                           ).coerce(False).alias("status"),
                                           fn.GROUP_CONCAT(
                                               fn.DISTINCT(
                                                   PackAnalysisDetails.slot_id)
                                           ).coerce(False).alias("slots"),
                                           PackAnalysis.id.alias("analysis_id"),
                                           DrugMaster.concated_fndc_txr_field(sep="##").alias("drug_id")
                                           ).dicts()\
            .join(PackAnalysis, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)\
            .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id)\
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id)\
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
            .where((PackDetails.id << pack_list) &
                   (PackDetails.pack_status == settings.PENDING_PACK_STATUS) &
                   (PackDetails.batch_id == batch_id) &
                   (PackAnalysisDetails.device_id == device_id))\
            .group_by(PackDetails.id, DrugMaster.concated_fndc_txr_field(sep="##"))

        for record in query:
            status_list = list(map(int, record["status"].split(",")))
            if constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED not in status_list:
                # fndc_txr = record["drug_id"]
                #
                # canister_list = list()
                # canister_query = PackAnalysis.select(fn.GROUP_CONCAT(
                #                                          fn.DISTINCT(
                #                                              PackAnalysisDetails.canister_id
                #                                          )
                #                                      ).coerce(False).alias("canister_ids")
                #                                      ).dicts()\
                #     .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)\
                #     .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id)\
                #     .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id)\
                #     .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)\
                #     .where((PackDetails.batch_id == batch_id) &
                #            (DrugMaster.concated_fndc_txr_field(sep="##") == fndc_txr) &
                #            (PackAnalysisDetails.device_id == device_id))\
                #     .group_by(DrugMaster.txr)
                #
                # for canisters in canister_query:
                canister_list = list(map(int, record["canister_ids"].split(",")))

                if len(canister_list) == 1:

                    if record["pack_id"] not in pack_wise_skipped_drug:
                        pack_wise_skipped_drug[record["pack_id"]] = dict()
                        pack_wise_skipped_drug[record["pack_id"]]["analysis_id"] = set()
                        pack_wise_skipped_drug[record["pack_id"]]["slot_ids"] = set()
                        pack_wise_skipped_drug[record["pack_id"]]["skipped_drug"] = set()
                        pack_wise_skipped_drug[record["pack_id"]]["canister_ids"] = set()

                    slots_list = list(map(int, record["slots"].split(",")))
                    # for slots in slots_list:
                    #     pack_wise_skipped_drug[record["pack_id"]]["slot_ids"].add(slots)
                    pack_wise_skipped_drug[record["pack_id"]]["slot_ids"].update(set(slots_list))
                    pack_wise_skipped_drug[record["pack_id"]]["analysis_id"].add(record["analysis_id"])
                    pack_wise_skipped_drug[record["pack_id"]]["skipped_drug"].add(record["drug_id"])
                    pack_wise_skipped_drug[record["pack_id"]]["canister_ids"].update(set(canister_list))

        return pack_wise_skipped_drug
    except Exception as e:
        logger.error("Error in get_pack_wise_skipped_drug: {}".format(e))
        raise e


@log_args_and_response
def db_update_analysis_data(data, batch_id, pack_wise_skipped_drug, mfd_analysis_dict=None, analysis_ids = None):
    """
    Stores analysis data done when importing packs

    @param data:
    @param batch_id:
    :return:
    @param mfd_slots:
    """
    logger.info('pack_analysis_details_save: ' + str(batch_id) + ' ' + str(data))
    try:
        analysis_list = list()
        detailed_list = list()
        # analysis_v2_temp_data = list()

        for pack in data:
            analysis_id = (PackAnalysis.select(PackAnalysis.id).where(PackAnalysis.pack_id == pack['pack_id'],
                                                                     PackAnalysis.batch_id == batch_id)).scalar()
            # store pack analysis data
            try:
                delete_analysis_details = PackAnalysisDetails.delete().where(PackAnalysisDetails.analysis_id == analysis_id).execute()
            except (InternalError, IntegrityError) as e:
                logger.error(e, exc_info=True)
                return error(2001)
            except DataError as e:
                logger.error(e, exc_info=True)
                return error(1020)
            duplicate_record_check = set()
            for item in pack['ndc_list']:
                # TODO : Need to check this condition because slot_id is not in item.
                # if (item["canister_id"], item["drug_id"], item["slot_id"]) in duplicate_record_check:

                # if drug for slot to be dropped from mfd canister don't add in pack analysis

                if item["slot_id"] in duplicate_record_check:
                    continue  # do not add if already added
                else:
                    # duplicate_record_check.add((item["canister_id"], item["drug_id"], item["slot_id"]))
                    # changed to temporary support in v2 only
                    # todo: change for v2 and v3
                    # duplicate_record_check.add((item["canister_id"], item["drug_id"], item["slot_id"]))
                    duplicate_record_check.add(item['slot_id'])

                if item['canister_id'] is not None and item['drop_number'] and item['config_id']:
                    detailed_data = dict()
                    detailed_data['analysis_id'] = analysis_id
                    detailed_data['device_id'] = item['device_id']
                    detailed_data['location_number'] = item['location_number']
                    detailed_data['canister_id'] = item['canister_id']
                    detailed_data['quadrant'] = item['quadrant']
                    detailed_data['drop_number'] = item['drop_number']
                    detailed_data["config_id"] = next(iter(item["config_id"])) if item[
                                                                                      "config_id"] is not None else None
                    detailed_data['slot_id'] = item['slot_id']
                    if pack_wise_skipped_drug:
                        if pack["pack_id"] in pack_wise_skipped_drug and \
                                item["slot_id"] in pack_wise_skipped_drug[pack['pack_id']]["slot_ids"] and \
                                item["canister_id"] in pack_wise_skipped_drug[pack['pack_id']]["canister_ids"]:

                            detailed_data["status"] = constants.REPLENISH_CANISTER_TRANSFER_SKIPPED
                    detailed_list.append(deepcopy(detailed_data))
        logger.debug('PackAnalysis Data: {}'.format(analysis_list))
        logger.debug('PackAnalysisDetails Data: {}'.format(detailed_list))
        # store analysis data for all drugs in pack

        if detailed_list:
            BaseModel.db_create_multi_record(detailed_list, PackAnalysisDetails)

        if mfd_analysis_dict:
            # whenenver mfd drug will be used in current batch in robot then entry will be deleted in
            # mfd_analysis_details and mfd_analysis
            mfd_analysis_ids = []
            for analysis_id in mfd_analysis_dict:
                mfd_analysis_ids.extend(mfd_analysis_dict[analysis_id])
            delete_mfd_analysis_details = MfdAnalysisDetails.delete().where(
                MfdAnalysisDetails.id << mfd_analysis_ids).execute()
            if analysis_ids:
                mfd_cycle_history_ids = []
                mfd_query = MfdCycleHistory.select(MfdCycleHistory.id).where(MfdCycleHistory.analysis_id << analysis_ids)
                for record in mfd_query.dicts():
                    mfd_cycle_history_ids.append(record['id'])
                if mfd_cycle_history_ids:
                    delete_mfd_cycle_history_comment_records = MfdCycleHistoryComment.delete().where(
                        MfdCycleHistoryComment.cycle_history_id << mfd_cycle_history_ids).execute()
                delete_mfd_cycle_records = MfdCycleHistory.delete().where(
                    MfdCycleHistory.analysis_id << analysis_ids).execute()
                delete_temp_mfd_records = (TempMfdFilling.delete().
                                           where(TempMfdFilling.mfd_analysis_id << analysis_ids).execute())
                delete_mfd_analysis = MfdAnalysis.delete().where(
                    MfdAnalysis.id << analysis_ids).execute()

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        print(e)


@log_args_and_response
def get_reserved_location_no_by_batch_and_device(batch_id: int, device_id: int):
    """
    Function to get reserved location numbers for given batch_id and device_id
    @param batch_id:
    @param device_id:
    @return:
    """
    try:
        location_number_list = list()
        query = PackDetails.select(
            LocationMaster.id.alias('location_id')
        ).dicts().join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(LocationMaster, on=(LocationMaster.location_number == PackAnalysisDetails.location_number) &
                                     (LocationMaster.device_id == PackAnalysisDetails.device_id)) \
            .where(PackAnalysisDetails.device_id == device_id, PackDetails.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS])\
            .group_by(LocationMaster.id)

        for record in query:
            location_number_list.append(record['location_id'])
        return location_number_list
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


def db_get_first_existing_pending_pack_order_no_id_pack_status(merged_pack_ids):
    """
    get query to get first existing pending pack order no.,pack id, pack status
    @param merged_pack_ids:
    """
    try:
        first_existing_pending_pack_details = list()
        query = PackDetails.select(fn.MIN(PackDetails.order_no).alias("first_existing_processed_pack_order_no"),
                                   PackDetails.id.alias("pack_id"), PackDetails.pack_status).dicts() \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
            .where(PackDetails.pack_status == 2, PackDetails.order_no != 0, PackDetails.id.not_in(merged_pack_ids))
        for record in query:
            first_existing_pending_pack_details.append(record)
        return first_existing_pending_pack_details
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


def db_get_pack_seq_order_no_detail():
    """
    get query to get pack sequence and order number details
    """
    try:
        pack_seq_order_no_details = list()
        query = PackDetails.select(PackDetails.order_no.alias("order_no"),
                                   PackDetails.pack_sequence.alias("pack_seq")).dicts() \
            .join(PackQueue, on=PackQueue.pack_id == PackDetails.id).where(PackDetails.order_no != 0)
        for record in query:
            pack_seq_order_no_details.append(record)
        return pack_seq_order_no_details
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def update_status_in_pack_analysis_details_for_out_of_stock(canister_id, company_id):
    try:
        logger.info("Inside update_status_in_pack_analysis_details_for_out_of_stock")

        pack_analysis_ids = set()
        reverted_packs = set()
        status = None
        device_id = None
        system_id = None
        batch_id = None

        pending_packs_query = PackQueue.select(PackAnalysisDetails.id,
                                               PackDetails.id.alias("pack_id"),
                                               PackDetails.system_id,
                                               PackAnalysisDetails.device_id,
                                               PackDetails.batch_id).dicts() \
                                .join(PackDetails, on=PackDetails.id == PackQueue.pack_id) \
                                .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
                                .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
                                .where(PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_SKIPPED,
                                       PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                                       PackAnalysisDetails.canister_id == canister_id) \
                                .group_by(PackAnalysisDetails.id)

        for data in pending_packs_query:
            pack_analysis_ids.add(data["id"])
            reverted_packs.add(data["pack_id"])
            device_id = data["device_id"]
            system_id = data["system_id"]
            batch_id = data["batch_id"]

        logger.info(f"In update_status_in_pack_analysis_details_for_out_of_stock, pack_analysis_ids: {pack_analysis_ids}, packs: {reverted_packs}")
        reason_out_of_stock = db_check_canister_reason(canister_id, batch_id, "Drug out of stock")

        if pack_analysis_ids and canister_id in reason_out_of_stock:

            status = PackAnalysisDetails.update(status=constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED) \
                        .where(PackAnalysisDetails.id << list(pack_analysis_ids)).execute()

            logger.info(f"In update_status_in_pack_analysis_details_for_out_of_stock, update pack analysis details --> status:{status}")

            args = {"company_id": company_id,
                    "device_id": device_id,
                    "canister_id": canister_id}
            status = update_couch_db_replenish_wizard(args)

            logger.info(f"In update_status_in_pack_analysis_details_for_out_of_stock, replenish-wizaed updated status --> status:{status}")

        return status, reverted_packs, (system_id, device_id)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(f"Error in update_status_in_pack_analysis_details_for_out_of_stock: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in update_status_in_pack_analysis_details_for_out_of_stock: {e}")
        raise e


@log_args_and_response
def db_check_canister_reason(canister_id, batch_id, reason):
    try:
        query = SkippedCanister.select(SkippedCanister.canister_id.alias('canister_id'), SkippedCanister.skip_reason) \
            .where( SkippedCanister.canister_id == canister_id).order_by(SkippedCanister.created_date.desc())
        canister_details_list = list()

        for record in query.dicts():
            if record['skip_reason'] == reason:
                canister_details_list.append(canister_id)
            break

        return canister_details_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_fetch_fod_only_slots(pack_id):
    try:
        grid_ids = []
        query = PackFillErrorV2.select(SlotFillErrorV2.pack_grid_id).dicts() \
            .join(SlotFillErrorV2, on=SlotFillErrorV2.pack_fill_error_id == PackFillErrorV2.id) \
            .where(PackFillErrorV2.pack_id == pack_id, PackFillErrorV2.unique_drug_id == None)
        for record in query:
            grid_ids.append(record["pack_grid_id"])
        return grid_ids
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e