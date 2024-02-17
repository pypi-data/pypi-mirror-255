import os
import sys
from datetime import date

from peewee import DoesNotExist, InternalError, IntegrityError, DataError, JOIN_LEFT_OUTER, fn

import settings
from dosepack.utilities.utils import log_args_and_response
from src.constants import MFD_ACTION_FILLED, DONE_MFD_DRUG_DIMENSION_FLOW
from src.model.model_action_master import ActionMaster
from src.model.model_batch_manual_packs import BatchManualPacks
from src.model.model_batch_master import BatchMaster
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_canister_drum import CanisterDrum
from src.model.model_canister_history import CanisterHistory
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_stick import CanisterStick
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_code_master import CodeMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_master import DrugMaster
from src.model.model_frequent_mfd_drugs import FrequentMfdDrugs
from src.model.model_guided_meta import GuidedMeta
from src.model.model_guided_tracker import GuidedTracker
from src.model.model_guided_transfer_cycle_history import GuidedTransferCycleHistory
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_mfd_canister_transfer_history import MfdCanisterTransferHistory
from src.model.model_mfd_cycle_history import MfdCycleHistory
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_fill_error_v2 import PackFillErrorV2
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_status_tracker import PackStatusTracker
from src.model.model_pack_user_map import PackUserMap
from src.model.model_patient_rx import PatientRx
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_small_canister_stick import SmallCanisterStick
from src.model.model_unique_drug import UniqueDrug
from src.model.model_canister_transfer_cycle_history import CanisterTransferCycleHistory
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_pack_header import PackHeader

from src.model.model_pill_fill_error import PillJumpError
from src.model.model_pack_verification_details import PackVerificationDetails
from src.model.model_pvs_drug_count import PVSDrugCount
from src.model.model_pvs_slot import PVSSlot
from src.model.model_prs_drug_details import PRSDrugDetails
from src.model.model_pvs_slot_details import PVSSlotDetails
from src.model.model_pack_verification import PackVerification
from src.model.model_slot_fill_error_v2 import SlotFillErrorV2
from src.model.model_pack_error import PackError


logger = settings.logger


@log_args_and_response
def get_packs_partially_filled_by_robot(track_date, offset, system_id: int, company_id: int):
    """
    Function to get total no. of packs partially filled by robot
    @param track_date: date - track_date's date
    @param system_id: int
    @param company_id: int
    @param offset: for timezone conversion
    @return: int
    """
    try:
        return PackDetails.db_get_packs_partially_filled_by_robot(track_date, offset, system_id, company_id)

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_packs_partially_filled_by_robot {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_packs_partially_filled_by_robot: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_packs_processed_today(track_date, offset, company_id: int):
    """
    Function to get total no. of packs processed today
    @param track_date: date - track_date's date
    @param company_id: int
    @param offset: for timezone conversion
    @return: int
    """
    try:
        robot_pack_count = 0
        manual_pack_count = 0

        pack_count_list = PackDetails.db_get_filled_pack_count_by_date(company_id=company_id, from_date=track_date,
                                                                       to_date=track_date,
                                                                       offset=offset)

        logger.info("In get_packs_processed_today: {}".format(pack_count_list))

        if pack_count_list:
            for item in pack_count_list:
                if item['filled_at'] in [settings.FILLED_AT_DOSE_PACKER,
                                         settings.FILLED_AT_MANUAL_VERIFICATION_STATION]:
                    robot_pack_count += item['pack_count']
                elif item['filled_at'] in [settings.FILLED_AT_PRI_PROCESSING, settings.FILLED_AT_POST_PROCESSING,
                                           settings.FILLED_AT_PRI_BATCH_ALLOCATION, settings.FILLED_AT_FILL_ERROR]:
                    manual_pack_count += item['pack_count']

        logger.info(
            "In get_packs_processed_today: robot_packs_count: {}, manual_pack_count: {}".format(robot_pack_count,
                                                                                                manual_pack_count))

        total_pack_count = int(robot_pack_count or 0) + int(manual_pack_count or 0)

        return robot_pack_count, manual_pack_count, total_pack_count

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_packs_processed_today {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_packs_processed_today: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_batch_in_progress_today(track_date, utc_time_zone_offset, system_id: int):
    """
    Function to get total no. of packs processed today
    @param track_date: date for which we require data
    @param utc_time_zone_offset: offset for converting one timezone to other timezone
    @param system_id: int
    @return: int
    """
    try:
        batch_id = BatchMaster.db_get_top_batch_id_with_any_status(track_date, utc_time_zone_offset,
                                                                   system_id)
        return batch_id

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_batch_in_progress_today {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_batch_in_progress_today: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pack_count_with_error(track_date, offset, company_id: int):
    """
    Function to get total no. of packs with error
    @param track_date: date - track_date's date
    @param system_id: int
    @param company_id: int
    @param offset: for timezone conversion
    @return: int
    """
    try:
        query = PackDetails.select(fn.COUNT(fn.distinct(PackDetails.id)).alias("id")).dicts() \
            .join(PackAnalysis, on=PackDetails.id == PackAnalysis.pack_id) \
            .join(PackFillErrorV2, on=PackDetails.id == PackFillErrorV2.pack_id) \
            .where(fn.DATE(fn.CONVERT_TZ(PackFillErrorV2.created_date, settings.TZ_UTC,
                                         offset)) == track_date,
                   PackDetails.company_id == company_id)

        logger.info("In get_pack_count_with_error query:{}".format(query))

        return query.scalar()

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_batch_in_progress_today {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pack_count_with_error: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pack_fill_workflow_drops(track_date, offset, company_id: int, batch_ids: list):
    """
    Function to get total no. of drugs filled in pack fill workflow
    @param track_date: date - track_date's date
    @param company_id: int
    @param offset: for timezone conversion
    @param batch_ids: list of batch ids
    @return: int
    """
    try:
        query = PackUserMap.select(fn.SUM(SlotDetails.quantity).alias("PFW_drop_count")).dicts() \
            .join(PackDetails, on=PackDetails.id == PackUserMap.pack_id) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetails.batch_id) \
            .where(PackDetails.company_id == company_id, PackAnalysisDetails.id.is_null(True))

        if track_date:
            query = query.where(fn.DATE(fn.CONVERT_TZ(PackUserMap.created_date, settings.TZ_UTC,
                                         offset)) == track_date)

        if batch_ids:
            query = query.where(BatchMaster.id << batch_ids)

        logger.info("In get_pack_fill_workflow_drops query:{}".format(query))

        return query.scalar()

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_batch_in_progress_today {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pack_fill_workflow_drops: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_robot_drops_skipped_filled_manually(track_date, offset, system_id: int, company_id: int, batch_ids: list):
    """
    Function to get total no. of drops skipped by robot and filled in pack fill workflow / MVS
    @param track_date: date - track_date's date
    @param system_id: int
    @param company_id: int
    @param offset: for timezone conversion
    @parma batch_ids: list of batch_id
    @return: int
    """
    try:
        query = PackDetails.select(
            fn.SUM(fn.floor(SlotDetails.quantity)).alias("robot_drop_skipped_and_filled_manually_count")).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails,
                  on=(SlotDetails.pack_rx_id == PackRxLink.id) & (SlotDetails.id == PackAnalysisDetails.slot_id)) \
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotTransaction.slot_id == SlotDetails.id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetails.batch_id) \
            .where(PackDetails.company_id == company_id, PackDetails.system_id ==
                   system_id, SlotTransaction.id.is_null())

        if track_date:
            query = query.where(fn.DATE(fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC,
                                         offset)) == track_date)

        if batch_ids:
            query = query.where(BatchMaster.id << batch_ids)

        logger.info("In get_robot_drops_skipped_filled_manually:{}".format(query))

        return query.scalar()

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_robot_drops_skipped_filled_manually {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_robot_drops_skipped_filled_manually: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_slots_filled_by_robot_canister(track_date, offset):
    """
    Function to get slots filled by robot canister
    @param track_date: date - track_date's date
    @param offset: for timezone conversion
    @return: list
    """
    try:
        query = SlotTransaction.select(fn.COUNT(fn.DISTINCT(SlotDetails.slot_id)).alias("slot_count")).dicts() \
            .join(SlotDetails, on=SlotDetails.id == SlotTransaction.slot_id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .where(fn.DATE(fn.CONVERT_TZ(SlotTransaction.created_date_time, settings.TZ_UTC,
                                         offset)) == track_date,
                   PackAnalysisDetails.canister_id.is_null(False))

        logger.info("In get_slots_filled_by_robot_canister query:{}".format(query))

        return query.scalar()

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_slots_filled_by_robot_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_slots_filled_by_robot_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_slots_filled_by_mfd_canister(track_date, offset):
    """
    Function to get total no. of slots filled by MFD canister
    @param track_date: date - track_date's date
    @param offset: for timezone conversion
    @return: list
    """
    try:
        query = SlotDetails.select(fn.COUNT(fn.DISTINCT(SlotDetails.slot_id)).alias("slot_count")).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdCycleHistory, on=MfdCycleHistory.analysis_id == MfdAnalysisDetails.analysis_id) \
            .where(fn.DATE(fn.CONVERT_TZ(MfdCycleHistory.action_date_time, settings.TZ_UTC,
                                         offset)) == track_date,
                   MfdCycleHistory.current_status_id == 69)

        logger.info("In get_slots_filled_by_mfd_canister query:{}".format(query))

        return query.scalar()

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_slots_filled_by_mfd_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_slots_filled_by_mfd_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_mfd_drops(track_date, offset, system_id: int, company_id: int, batch_ids: list):
    """
    Function to get total no. of drops by MFD canister
    @param track_date: date - track_date's date
    @param system_id: int
    @param company_id: int
    @param offset: for timezone conversion
    @return: int
    """
    try:
        query = PackDetails.select(
            fn.SUM(SlotDetails.quantity).alias("MFD_drop_count")).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdCycleHistory, on=MfdCycleHistory.analysis_id == MfdAnalysisDetails.analysis_id) \
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetails.batch_id) \
            .where(PackDetails.company_id == company_id, PackDetails.system_id ==
                   system_id, MfdCycleHistory.current_status_id == 69)

        logger.info("In get_mfd_drops:{}".format(query))

        if track_date:
            query = query.where(fn.DATE(fn.CONVERT_TZ(MfdCycleHistory.action_date_time, settings.TZ_UTC,
                                         offset)) == track_date)
        if batch_ids:
            query = query.where(BatchMaster.id << batch_ids)

        return query.scalar()

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_mfd_drops {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_mfd_drops: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_mfd_drops_skipped_filled_manually(track_date, offset, system_id: int, company_id: int, batch_ids: list):
    """
    Function to get total no. of drops skipped by MFD canister and filled by Pack fill workflow/MVS
    @param track_date: date - track_date's date
    @param system_id: int
    @param company_id: int
    @param offset: for timezone conversion
    @param batch_ids: list of batch_ids
    @return: int
    """
    try:
        query = PackDetails.select(
            fn.SUM(SlotDetails.quantity).alias("MFD_drop_count")) \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdCycleHistory, on=MfdCycleHistory.analysis_id == MfdAnalysisDetails.analysis_id) \
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetails.batch_id) \
            .where(PackDetails.company_id == company_id, PackDetails.system_id ==
                   system_id, MfdAnalysisDetails.status_id == 62, SlotDetails.quantity.is_null(False))

        if track_date:
            query = query.where(fn.DATE(fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC,
                                         offset)) == track_date)
        if batch_ids:
            query = query.where(BatchMaster.id << batch_ids)

        logger.info("In get_mfd_drops_skipped_filled_manually:{}".format(query))

        return query.scalar()

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_mfd_drops_skipped_filled_manually {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_mfd_drops_skipped_filled_manually: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_robot_drops(track_date, offset, system_id: int, company_id: int, batch_ids: list):
    """
    Function to get total no. of drops by robot canister
    @param track_date: date - track_date's date
    @param system_id: int
    @param company_id: int
    @param offset: for timezone conversion
    @return: int
    """
    try:
        query = PackDetails.select(
            fn.SUM(fn.floor(SlotDetails.quantity)).alias("robot_drop_count")).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails,
                  on=(SlotDetails.pack_rx_id == PackRxLink.id) & (SlotDetails.id == PackAnalysisDetails.slot_id)) \
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(SlotTransaction, on=SlotTransaction.slot_id == SlotDetails.id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetails.batch_id) \
            .where(PackDetails.company_id == company_id, PackDetails.system_id ==
                   system_id, PackAnalysisDetails.canister_id.is_null(False))

        if track_date:
            query = query.where(fn.DATE(fn.CONVERT_TZ(SlotTransaction.created_date_time, settings.TZ_UTC,
                                         offset)) == track_date)
        if batch_ids:
            query = query.where(BatchMaster.id << batch_ids)

        logger.info("In get_robot_drops:{}".format(query))

        return query.scalar()

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_robot_drops {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_robot_drops: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_mfd_data(track_date, offset):
    """
    Function to get total no. of drops by robot canister
    @param track_date: date - track_date's date
    @param offset: for timezone conversion
    @return: int
    """
    try:
        mfd_batch_id_canister_id_action_datetime = list()

        query = MfdCycleHistory.select(MfdAnalysis.batch_id, MfdAnalysis.mfd_canister_id,
                                       ActionMaster.value.alias("action_value"),
                                       fn.CONVERT_TZ(MfdCycleHistory.action_date_time, settings.TZ_UTC,
                                                     offset).alias('action_date_time')
                                       ).dicts() \
            .join(MfdAnalysis, on=MfdAnalysis.id == MfdCycleHistory.analysis_id) \
            .join(ActionMaster, on=ActionMaster.id == MfdCycleHistory.action_id).distinct().dicts() \
            .where(fn.DATE(fn.CONVERT_TZ(MfdCycleHistory.action_date_time, settings.TZ_UTC,
                                         offset)) == track_date, MfdCycleHistory.action_id == MFD_ACTION_FILLED)

        logger.info("In get_mfd_data:{}".format(query))

        for record in query:
            record['batch_id'] = int(record['batch_id'])
            mfd_batch_id_canister_id_action_datetime.append(record)

        return mfd_batch_id_canister_id_action_datetime

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_mfd_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_mfd_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_top_5_manual_drugs_without_drug_dimensions(track_date, offset, system_id: int, company_id: int, batch_id):
    """
    Function to get track_date's top 5 manual drugs
    @param track_date: date - track_date's date
    @param system_id: int
    @param company_id: int
    @param offset: for timezone conversion
    @return: list
    """
    try:
        top_5_manual_drugs = list()
        sub_query = CanisterMaster.select(fn.CONCAT(
            DrugMaster.formatted_ndc, '#', DrugMaster.txr).alias(
            'fndc_txr')).join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id).where(CanisterMaster.active == 1)

        query = BatchMaster.select(
            fn.Concat(DrugMaster.drug_name, ' ', DrugMaster.strength_value, ' ', DrugMaster.strength).alias("Drug"),
            FrequentMfdDrugs.status.alias("FrequentMfdDrugsStatus"), fn.max(FrequentMfdDrugs.id),
            fn.SUM(SlotDetails.quantity).alias('drug_count'),
            fn.COUNT(fn.distinct(PackDetails.id)).alias('pack_count')).dicts() \
            .join(PackDetails, on=BatchMaster.id == PackDetails.batch_id) \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER,
                  on=fn.CONCAT(DrugMaster.formatted_ndc, '#', DrugMaster.txr) ==
                     fn.CONCAT(UniqueDrug.formatted_ndc, '#', UniqueDrug.txr)) \
            .join(FrequentMfdDrugs,
                  on=UniqueDrug.id == FrequentMfdDrugs.unique_drug_id) \
            .join(DrugDimension, JOIN_LEFT_OUTER,
                  on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER,
                  on=DrugDimension.shape == CustomDrugShape.id) \
            .where(PackDetails.company_id == company_id, PackDetails.system_id ==
                   system_id, fn.DATE(fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC,
                                                    offset)) == track_date,
                   FrequentMfdDrugs.batch_id == int(batch_id),
                   fn.CONCAT(DrugMaster.formatted_ndc, '#', DrugMaster.txr).not_in(sub_query)).group_by(
            FrequentMfdDrugs.unique_drug_id).order_by(
            fn.COUNT(fn.distinct(
                PackDetails.id)).desc(), fn.SUM(SlotDetails.quantity).desc()).limit(5)

        logger.info("In get_top_5_manual_drugs_without_drug_dimensions:{}".format(query))

        for record in query:
            if record["FrequentMfdDrugsStatus"] != DONE_MFD_DRUG_DIMENSION_FLOW:
                top_5_manual_drugs.append(record)

        return top_5_manual_drugs

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_top_5_manual_drugs_without_drug_dimensions {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_top_5_manual_drugs_without_drug_dimensions: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_manual_drugs_for_imported_batch_db(batch_id: int, system_id: int, company_id: int):
    """
    Function to get manual drugs for imported batch
    @param batch_id: imported batch_id
    @param system_id:
    @param company_id:
    @return: list
    """
    try:
        manual_drugs = list()
        count = 0
        sub_query = CanisterMaster.select(fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, '')).alias(
            'fndc_txr')).join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id).where(CanisterMaster.active == 1)

        clauses = [(PackDetails.company_id == company_id) & (PackDetails.system_id == system_id) &
                   (fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, '')).not_in(sub_query))]

        query = PackDetails.select(
            fn.Concat(DrugMaster.drug_name, ' ', DrugMaster.strength_value, ' ', DrugMaster.strength).alias("Drug"),
            fn.CONCAT(
                DrugMaster.formatted_ndc, '##', DrugMaster.txr).alias(
                'fndc_txr'),
            DrugMaster.ndc, DrugDimension.id.alias("drug_dimension_id"),
            fn.SUM(SlotDetails.quantity).alias('drug_count'),
            fn.COUNT(fn.distinct(PackDetails.id)).alias('pack_count')).dicts() \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(UniqueDrug,
                  on=fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr) ==
                    fn.CONCAT(UniqueDrug.formatted_ndc, '##', UniqueDrug.txr)) \
            .join(DrugDimension, JOIN_LEFT_OUTER,
                  on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER,
                  on=DrugDimension.shape == CustomDrugShape.id) \
            .where(*clauses).group_by(fn.CONCAT(
            DrugMaster.formatted_ndc, '##', DrugMaster.txr)).order_by(
            fn.COUNT(fn.distinct(
                PackDetails.id)).desc(), fn.SUM(SlotDetails.quantity).desc())

        query = query.where(
            (PackDetails.batch_id == int(batch_id)) | (PackDetails.previous_batch_id == int(batch_id)))

        logger.info("In get_manual_drugs_for_imported_batch_db:{}".format(query))

        for record in query:
            count = count + 1
            if record['drug_dimension_id'] is None:
                record['drug_dimension_taken'] = "No"
            else:
                record['drug_dimension_taken'] = "Yes"
            record["drug_count"] = int(record["drug_count"])
            manual_drugs.append(record)

        return manual_drugs, count

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_manual_drugs_for_imported_batch_db {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_drugs_for_imported_batch_db: exc_type - {exc_type}, filename - {filename}, line - "
            f"{exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_canister_drugs_for_imported_batch_db(batch_id: int, system_id: int, company_id: int):
    """
    Function to get canister drugs for imported batch
    @param batch_id: imported batch_id
    @param system_id:
    @param company_id:
    @return: list
    """
    try:
        manual_drugs = list()
        count = 0
        sub_query = CanisterMaster.select(fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, '')).alias(
            'fndc_txr')).join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id).where(CanisterMaster.active == 1)

        clauses = [(PackDetails.company_id == company_id) & (PackDetails.system_id == system_id) &
                   (fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, '')) << sub_query)]

        query = PackDetails.select(
            fn.COUNT(fn.distinct(fn.CONCAT(DrugMaster.formatted_ndc, '##', fn.IFNULL(DrugMaster.txr, ''))))).dicts() \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(UniqueDrug,
                  on=fn.CONCAT(DrugMaster.formatted_ndc, '##', DrugMaster.txr) ==
                    fn.CONCAT(UniqueDrug.formatted_ndc, '##', UniqueDrug.txr)) \
            .join(DrugDimension, JOIN_LEFT_OUTER,
                  on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER,
                  on=DrugDimension.shape == CustomDrugShape.id) \
            .where(*clauses)
        query = query.where(
            (PackDetails.batch_id == int(batch_id)) | (PackDetails.previous_batch_id == int(batch_id)))

        logger.info("In get_canister_drugs_for_imported_batch_db:{}".format(query))

        return query.scalar()

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_canister_drugs_for_imported_batch_db {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_canister_drugs_for_imported_batch_db: exc_type - {exc_type}, filename - {filename}, line - "
            f"{exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_batch_id_canister_transfer_datetime(from_date: date, to_date: date, offset) -> list:
    """
    Get batch_id and other canister transfer details from CanisterTransfers and CanisterTransferCycleHistory
    :param from_date: date from which we need canister transfer details
    :param to_date: date up to which we need canister transfer details
    :param offset: offset for converting one timezone to other timezone
    :return list: list of batch_id and other canister transfer details from CanisterTxMeta and CanisterTransfers
    """
    try:
        batch_id_min_max_canister_transfer_date = list()

        query = CanisterTransfers.select(CanisterTransfers.batch_id,
                                         fn.CONVERT_TZ(CanisterTransfers.created_date, settings.TZ_UTC,
                                                       offset).alias('canistertxmeta_created_date'),
                                         fn.CONVERT_TZ(CanisterTransfers.modified_date, settings.TZ_UTC,
                                                       offset).alias('modified_date'),
                                         CanisterTransfers.canister_id,
                                         ActionMaster.value.alias('action_taken_on_canister')) \
            .join(CanisterTransferCycleHistory, on=CanisterTransferCycleHistory.canister_transfer_id ==
                                                   CanisterTransfers.id) \
            .join(ActionMaster, on=ActionMaster.id == CanisterTransferCycleHistory.action_id).dicts() \
            .where((fn.CONVERT_TZ(CanisterTransfers.created_date, settings.TZ_UTC,
                                  offset)).between(from_date, to_date))

        logger.info("In get_batch_id_canister_transfer_datetime:{}".format(query))

        for record in query:
            batch_id_min_max_canister_transfer_date.append(record)

        return batch_id_min_max_canister_transfer_date

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_batch_id_canister_transfer_datetime {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_batch_id_canister_transfer_datetime: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_canister_transfer_details_from_canister_history(from_date: date, to_date: date, canister_id_list: list,
                                                        offset) -> list:
    """
    Return canister transfer details from canister history table
    @param from_date: date from which canister transfer details required
    @param to_date: date up to which canister transfer details required
    @param canister_id_list: list of canister ids for which canister transfer details required
    @param offset: offset for converting one timezone to other timezone
    @return: list of canister transfer details from canister history table
    """
    try:
        LocationMaster_alias = LocationMaster.alias()
        DeviceMaster_alias = DeviceMaster.alias()
        canister_transfer_details = list()
        query = CanisterHistory.select(CanisterHistory.canister_id,
                                       fn.CONVERT_TZ(CanisterHistory.created_date, settings.TZ_UTC,
                                                     offset).alias('canister_history_created_date'),
                                       fn.CONVERT_TZ(CanisterHistory.modified_date, settings.TZ_UTC,
                                                     offset).alias('canister_history_modified_date'),
                                       LocationMaster.device_id.alias('from_device'),
                                       LocationMaster_alias.device_id.alias('to_device'),
                                       DeviceMaster.name.alias('from_device_name'),
                                       DeviceMaster_alias.name.alias('to_device_name')
                                       ).distinct().dicts() \
            .join(LocationMaster, on=LocationMaster.id == CanisterHistory.previous_location_id) \
            .join(LocationMaster_alias, on=LocationMaster_alias.id == CanisterHistory.current_location_id) \
            .join(DeviceMaster, on=LocationMaster.device_id == DeviceMaster.id) \
            .join(DeviceMaster_alias, on=LocationMaster_alias.device_id == DeviceMaster_alias.id) \
            .where((fn.CONVERT_TZ(CanisterHistory.created_date, settings.TZ_UTC,
                                  offset)).between(from_date, to_date) &
                   (CanisterHistory.previous_location_id != CanisterHistory.current_location_id) &
                   (CanisterHistory.canister_id << canister_id_list))

        logger.info("In get_canister_transfer_details_from_canister_history:{}".format(query))

        for record in query:
            canister_transfer_details.append(record)

        return canister_transfer_details

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_canister_transfer_details_from_canister_history {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_canister_transfer_details_from_canister_history: exc_type - {exc_type}, filename - {filename}, "
            f"line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_drug_replenish_guided_details(from_date: date, to_date: date, offset) -> list:
    """
    Return date wise, user wise count of manual filled packs
    @param from_date: date from which drug replenish guided details required
    @param to_date: date up to which drug replenish guided details required
    @param offset: offset for converting one timezone to other timezone
    @return:
    """
    try:
        CodeMaster_alias = CodeMaster.alias()
        drug_replenish_guided_details = list()
        query = GuidedTransferCycleHistory.select(GuidedMeta.batch_id,
                                                  GuidedMeta.mini_batch_id,
                                                  GuidedTracker.guided_meta_id,
                                                  GuidedTransferCycleHistory.guided_tracker_id,
                                                  GuidedTracker.source_canister_id.alias('canister_id'),
                                                  GuidedTracker.alternate_canister_id,
                                                  GuidedMeta.total_transfers,
                                                  GuidedMeta.alt_canister_count,
                                                  GuidedMeta.alt_can_replenish_count,
                                                  GuidedMeta.replenish_skipped_count,
                                                  CodeMaster.value.alias('previous_status'),
                                                  CodeMaster_alias.value.alias('current_status'),
                                                  fn.CONVERT_TZ(GuidedTransferCycleHistory.action_datetime,
                                                                settings.TZ_UTC,
                                                                offset).alias('action_datetime'),
                                                  fn.CONVERT_TZ(GuidedMeta.created_date, settings.TZ_UTC,
                                                                offset).alias('guided_meta_created_date'),
                                                  fn.CONVERT_TZ(GuidedMeta.modified_date, settings.TZ_UTC,
                                                                offset).alias('guided_meta_modified_date')
                                                  ).distinct().dicts() \
            .join(GuidedTracker, on=GuidedTracker.id == GuidedTransferCycleHistory.guided_tracker_id) \
            .join(GuidedMeta, on=GuidedMeta.id == GuidedTracker.guided_meta_id) \
            .join(CodeMaster, on=CodeMaster.id == GuidedTransferCycleHistory.previous_status_id) \
            .join(CodeMaster_alias, on=CodeMaster_alias.id == GuidedTransferCycleHistory.current_status_id) \
            .where((fn.CONVERT_TZ(GuidedTransferCycleHistory.action_datetime, settings.TZ_UTC,
                                  offset)).between(from_date, to_date))

        logger.info("In get_drug_replenish_guided_details:{}".format(query))

        for record in query:
            drug_replenish_guided_details.append(record)

        return drug_replenish_guided_details

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_drug_replenish_guided_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_drug_replenish_guided_details: exc_type - {exc_type}, filename - {filename}, "
            f"line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_drug_replenish_details_from_canister_tracker(from_date: date, to_date: date, offset) -> list:
    """
    Return datewise, user wise count of manual filled packs
    @param from_date:date from which we require drug_replenish details from canister_tracker
    @param to_date:date up to which we require drug_replenish details from canister_tracker
    @param offset: offset for converting one timezone to other timezone
    @return:
    """
    try:
        drug_replenish_details_from_canister_tracker = CanisterTracker \
            .get_drug_replenish_details_from_canister_tracker(from_date=from_date, to_date=to_date, offset=offset)

        return drug_replenish_details_from_canister_tracker

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_drug_replenish_details_from_canister_tracker {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_drug_replenish_details_from_canister_tracker: exc_type - {exc_type}, filename - {filename}, "
            f"line - {exc_tb.tb_lineno}")
        raise e


def get_mfd_batch_id_canister_id_action_datetime_details(from_date: date, to_date: date, offset) -> list:
    """
    Gets the list of mfd_batch_id, mfd_canister_id, action and action datetime
    @param from_date:date from which we require mfd_batch_id, mfd_canister_id, action and action datetime details
    @param to_date:date up to which we require mfd_batch_id, mfd_canister_id, action and action datetime details
    @param offset: offset for converting one timezone to other timezone
    """
    try:
        mfd_batch_id_canister_id_action_datetime = list()

        query = MfdCycleHistory.select(MfdAnalysis.batch_id, MfdAnalysis.mfd_canister_id,
                                       ActionMaster.value.alias("action_value"),
                                       fn.CONVERT_TZ(MfdCycleHistory.action_date_time, settings.TZ_UTC,
                                                     offset).alias('action_date_time')
                                       ) \
            .join(MfdAnalysis, on=MfdAnalysis.id == MfdCycleHistory.analysis_id) \
            .join(ActionMaster, on=ActionMaster.id == MfdCycleHistory.action_id).distinct().dicts() \
            .where((fn.CONVERT_TZ(MfdCycleHistory.action_date_time, settings.TZ_UTC,
                                  offset)).between(from_date, to_date))

        logger.info("In get_mfd_batch_id_canister_id_action_datetime_details:{}".format(query))

        for record in query:
            record['batch_id'] = int(record['batch_id'])
            mfd_batch_id_canister_id_action_datetime.append(record)

        return mfd_batch_id_canister_id_action_datetime

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_mfd_batch_id_canister_id_action_datetime_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_mfd_batch_id_canister_id_action_datetime_details: exc_type - {exc_type}, filename - {filename}, "
            f"line - {exc_tb.tb_lineno}")
        raise e


def get_mfd_canister_transfer_details_from_mfd_canister_transfer_history(from_date: date, to_date: date,
                                                                         offset) -> list:
    """
    Return date wise, user wise count of manual filled packs
    @param from_date:date from which we require date wise, user wise count of manual filled packs
    @param to_date:date up to which we require date wise, user wise count of manual filled packs
    @param offset: offset for converting one timezone to other timezone
    @return:
    """
    try:
        LocationMaster_alias = LocationMaster.alias()
        DeviceMaster_alias = DeviceMaster.alias()
        canister_transfer_details = list()
        query = MfdCanisterTransferHistory.select(MfdCanisterTransferHistory.mfd_canister_id,
                                                  fn.CONVERT_TZ(MfdCanisterTransferHistory.created_date,
                                                                settings.TZ_UTC,
                                                                offset).alias(
                                                      'mfd_canister_transfer_history_created_date'),
                                                  fn.CONVERT_TZ(MfdCanisterTransferHistory.modified_date,
                                                                settings.TZ_UTC,
                                                                offset).alias(
                                                      'mfd_canister_transfer_history_modified_date'),
                                                  LocationMaster.device_id.alias('from_device'),
                                                  DeviceMaster.name.alias('from_device_name'),
                                                  LocationMaster_alias.device_id.alias('to_device'),
                                                  DeviceMaster_alias.name.alias('to_device_name')
                                                  ).distinct().dicts() \
            .join(LocationMaster, on=LocationMaster.id == MfdCanisterTransferHistory.previous_location_id) \
            .join(LocationMaster_alias, on=LocationMaster_alias.id == MfdCanisterTransferHistory.current_location_id) \
            .join(DeviceMaster, on=LocationMaster.device_id == DeviceMaster.id) \
            .join(DeviceMaster_alias, on=LocationMaster_alias.device_id == DeviceMaster_alias.id) \
            .where(fn.CONVERT_TZ(MfdCanisterTransferHistory.created_date, settings.TZ_UTC,
                                 offset).between(from_date, to_date),
                   ~ (((DeviceMaster.id == 4) & (DeviceMaster_alias.id == 4))
                      | ((DeviceMaster.id == 5) & (DeviceMaster_alias.id == 5))
                      | ((DeviceMaster.id == 6) & (DeviceMaster_alias.id == 6))
                      | ((DeviceMaster.id == 7) & (DeviceMaster_alias.id == 7))))

        logger.info("In get_mfd_canister_transfer_details_from_mfd_canister_transfer_history:{}".format(query))

        for record in query:
            canister_transfer_details.append(record)

        return canister_transfer_details

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_mfd_canister_transfer_details_from_mfd_canister_transfer_history {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_mfd_canister_transfer_details_from_mfd_canister_transfer_history: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_batch_id_imported_date_pack_id_status_created_filled_date_details(from_date: date, to_date: date,
                                                                          offset) -> list:
    """
    Get list of batch_id, batch_imported_date, pack id, pack status, pack status created date and pack_filled_date
    @param from_date: date from which we require list of batch_id, batch_imported_date, pack id, pack status, pack
    status created date and pack_filled_date
    @param to_date: date up to which we require list of batch_id, batch_imported_date, pack id, pack status, pack
    status created date and pack_filled_date
    @param offset: offset for converting one timezone to other timezone
    @return batch_id_imported_date_pack_id_status_created_filled_date: list of batch_id, batch_imported_date, pack id,
    pack status, pack status created date and pack_filled_date
    """
    try:
        batch_id_imported_date_pack_id_status_created_filled_date = []
        robot_pack_id_list = list()
        subquery = PackDetails.select(PackDetails.id.alias('pack_id')).dicts() \
            .join(SlotTransaction, on=PackDetails.id == SlotTransaction.pack_id) \
            .where(PackDetails.modified_date >= from_date)

        for record in subquery:
            robot_pack_id_list.append(record['pack_id'])

        if not robot_pack_id_list:
            return batch_id_imported_date_pack_id_status_created_filled_date
        query = PackStatusTracker.select(fn.CONVERT_TZ(PackDetails.modified_date, settings.TZ_UTC,
                                                       offset).alias('created_date_time'),
                                         BatchMaster.id.alias("batch_id"),
                                         fn.CONVERT_TZ(BatchMaster.imported_date, settings.TZ_UTC,
                                                       offset).alias('batch_imported_date_time'),
                                         PackDetails.id.alias("pack_id"),
                                         CodeMaster.value.alias("transfer_status"),
                                         fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC,
                                                       offset).alias('filled_date')
                                         ).distinct().dicts() \
            .join(PackDetails, on=PackDetails.id == PackStatusTracker.pack_id) \
            .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id) \
            .join(CodeMaster, on=CodeMaster.id == PackDetails.pack_status) \
            .where((fn.CONVERT_TZ(PackDetails.modified_date, settings.TZ_UTC,
                                  offset)).between(from_date, to_date) &
                   (fn.CONVERT_TZ(PackDetails.consumption_end_date, settings.TZ_UTC,
                                  offset) >= from_date),
                   (PackDetails.id << robot_pack_id_list))

        logger.info("In get_batch_id_imported_date_pack_id_status_created_filled_date_details:{}".format(query))

        for record in query:
            batch_id_imported_date_pack_id_status_created_filled_date.append(record)

        return batch_id_imported_date_pack_id_status_created_filled_date

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_batch_id_imported_date_pack_id_status_created_filled_date_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_batch_id_imported_date_pack_id_status_created_filled_date_details: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def db_get_ndc_list_last_3_months_usage(track_date: date, system_id, company_id, offset) -> list:
    """
    Get ndc percentile usage
    @param track_date:
    @param system_id:
    @param company_id:
    """
    try:
        ndc_details = []
        query = PackDetails.select(
            fn.Concat(DrugMaster.drug_name, ' ', DrugMaster.strength_value, ' ', DrugMaster.strength).alias("Drug"),
            fn.CONCAT(
                DrugMaster.formatted_ndc, '#', DrugMaster.txr).alias(
                'fndc_txr'),
            DrugMaster.ndc,
            fn.SUM(SlotDetails.quantity).alias('drug_count'),
            fn.COUNT(fn.distinct(PackDetails.id)).alias('pack_count')).dicts() \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(UniqueDrug,
                  on=fn.CONCAT(DrugMaster.formatted_ndc, '#', DrugMaster.txr) ==
                     fn.CONCAT(UniqueDrug.formatted_ndc, '#', UniqueDrug.txr)) \
            .join(DrugDimension, JOIN_LEFT_OUTER,
                  on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER,
                  on=DrugDimension.shape == CustomDrugShape.id) \
            .where(PackDetails.company_id == company_id, PackDetails.system_id ==
                   system_id).group_by(fn.CONCAT(
            DrugMaster.formatted_ndc, '#', DrugMaster.txr)).order_by(
            fn.COUNT(fn.distinct(
                PackDetails.id)).desc(), fn.SUM(SlotDetails.quantity).desc(),
            fn.DATE(fn.CONVERT_TZ(
                PackDetails.modified_date, settings.TZ_UTC,
                offset)) >= track_date
        )

        logger.info("In db_get_ndc_list_last_3_months_usage:{}".format(query))

        for record in query:
            ndc_details.append(record)

        return ndc_details

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in db_get_ndc_list_last_3_months_usage {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in db_get_ndc_list_last_3_months_usage: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_pvs_data(slot_list, slot_header_list):
    pvs_data = []
    query = PVSSlot.select(PVSSlot.slot_image_name.alias("image_name"),
                           SlotDetails.id.alias("slot_id"),
                           PackVerificationDetails.predicted_quantity.alias("pvs_predicted_qty_total"),
                           PVSDrugCount.predicted_qty.alias("pvs_predicated_qty")) \
        .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
        .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
        .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
        .join(UniqueDrug,
                      on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                         (UniqueDrug.txr == DrugMaster.txr)) \
        .join(PVSDrugCount, on=(PVSSlot.id == PVSDrugCount.pvs_slot_id) &
                                       (PVSDrugCount.unique_drug_id == UniqueDrug.id))\
        .join(PackVerificationDetails, on=PackVerificationDetails.slot_header_id == SlotHeader.id) \
        .where(SlotDetails.id << slot_list & SlotHeader.id << slot_header_list).dicts()

    for record in query:
        pvs_data.append(record)

    return pvs_data

def get_drug_data(drug_id_list):
    drug_list = []

    query = DrugDimension.select(UniqueDrug.id.alias("unique_drug_id"),
                                 DrugDimension.length.alias("drug_length"),
                                 DrugDimension.width.alias("drug_width"),
                                 DrugDimension.depth.alias("drug_depth"),
                                 DrugDimension.fillet.alias("drug_fillet"),
                                 CustomDrugShape.name.alias("drug_shape_name"))\
        .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id) \
        .join(UniqueDrug, on=DrugDimension.unique_drug_id == UniqueDrug.id)\
        .where(DrugDimension.unique_drug_id << drug_id_list).dicts()

    for record in query:
        drug_list.append(record)

    return drug_list


def get_location_data(canister_id_list):
    location_data = []
    query = LocationMaster.select(LocationMaster.display_location.alias("display_location"),
                                  CanisterMaster.rfid.alias("canister_rfid"),
                                  CanisterMaster.id.alias("canister_id")) \
        .join(CanisterMaster, on=LocationMaster.id == CanisterMaster.location_id) \
        .where(CanisterMaster.id << canister_id_list).dicts()

    for record in query:
        location_data.append(record)

    return location_data

@log_args_and_response
def get_pvs_sensor_dropping_data(system_id, company_id, track_date, offset):
    try:
        drop_error_data = []
        query = SlotTransaction.select(PackDetails.batch_id.alias("batch_id"),
                                       PackDetails.id.alias('pack_id'),
                                       PackGrid.slot_number.alias('slot_number'),
                                       SlotHeader.id.alias("slot_header_id"),
                                       SlotDetails.id.alias("slot_id"),
                                       UniqueDrug.id.alias("unique_drug_id"),
                                       DrugMaster.drug_name.alias("drug_name"),
                                       DrugMaster.image_name.alias("drug_image"),
                                       DrugMaster.ndc.alias("drug_ndc"),
                                       SlotTransaction.canister_id.alias("canister_id"),
                                       PackAnalysisDetails.device_id.alias("device_id"),
                                       PackAnalysisDetails.drop_number.alias("drop_number"),
                                       PackAnalysisDetails.config_id.alias("config_id"),
                                       PackAnalysisDetails.quadrant.alias("quadrant"),
                                       SlotDetails.quantity.alias("actual_qty"),
                                       fn.SUM(SlotTransaction.dropped_qty).alias("sensor_drop_quantity"),
                                       ((SlotDetails.quantity)-
                                       (fn.SUM(SlotTransaction.dropped_qty))).alias("sensor_dropping_error"),
                                       fn.DATE(fn.CONVERT_TZ(
                                           SlotTransaction.created_date_time, settings.TZ_UTC,
            offset)).alias("sensor_created_date"))\
            .join(SlotDetails, on=SlotDetails.id == SlotTransaction.slot_id)\
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id)\
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id)\
            .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id)\
            .join(PackAnalysisDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                             (UniqueDrug.txr == DrugMaster.txr)) \
            .where((PackAnalysisDetails.location_number.is_null(False)),
                   (fn.DATE(fn.CONVERT_TZ(
                       SlotTransaction.created_date_time, settings.TZ_UTC,
            offset)) == track_date))\
            .group_by(SlotDetails.id, SlotTransaction.canister_id).dicts()

        for record in query:
            drop_error_data.append(record)

        return drop_error_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_pvs_sensor_dropping_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pvs_sensor_dropping_data: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pills_with_width_length_slot_wise(system_id, company_id, track_date, offset):
    try:
        drop_error_data = []
        query = PackDetails.select(PackDetails.id.alias("pack_id"),
                                       SlotHeader.id.alias("slot_header_id"),
                                       DrugMaster.ndc.alias("drug_ndc"),
                                       fn.CONCAT(DrugMaster.drug_name, ' ', DrugMaster.strength, ' ', DrugMaster.strength_value).alias('drug_name'),
                                       DrugDimension.length.alias("length"),
                                       DrugDimension.width.alias("width")
                                       )\
            .join(SlotHeader, on=PackDetails.id == SlotHeader.pack_id) \
            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(SlotTransaction, on=SlotDetails.id == SlotTransaction.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PatientRx, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(UniqueDrug,
                  on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                     (UniqueDrug.txr == DrugMaster.txr)) \
            .join(DrugDimension,on=DrugDimension.unique_drug_id == UniqueDrug.id)\
            .where((PackDetails.system_id == system_id),
                   (PackDetails.company_id == company_id),
                   (fn.DATE(fn.CONVERT_TZ(
                       PackDetails.filled_date, '+00:00', offset)) == track_date)).dicts()

        for record in query:
            drop_error_data.append(record)

        return drop_error_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_pills_with_width_length_slot_wise {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pills_with_width_length_slot_wise: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def get_sensor_dropping_data(system_id, company_id, track_date, offset):
    """
                        get_sensor_drug_error_data
    """
    try:
        drop_error_data = []
        query = SlotTransaction.select(PackDetails.batch_id.alias("batch_id"),
                                       PackDetails.id.alias('pack_id'),
                                       PackGrid.slot_number.alias('slot_number'),
                                       SlotHeader.id.alias("slot_header_id"),
                                       SlotDetails.id.alias("slot_id"),
                                       UniqueDrug.id.alias("unique_drug_id"),
                                       DrugMaster.drug_name.alias("drug_name"),
                                       DrugMaster.image_name.alias("drug_image"),
                                       DrugMaster.ndc.alias("drug_ndc"),
                                       fn.CONCAT(DrugMaster.strength_value, " ", DrugMaster.strength).alias("strength_value"),
                                       DrugMaster.color.alias("color"),
                                       SlotTransaction.canister_id.alias("canister_id"),
                                       PackAnalysisDetails.device_id.alias("device_id"),
                                       PackAnalysisDetails.drop_number.alias("drop_number"),
                                       PackAnalysisDetails.config_id.alias("config_id"),
                                       PackAnalysisDetails.quadrant.alias("quadrant"),
                                       SlotDetails.quantity.alias("actual_qty"),
                                       fn.SUM(SlotTransaction.dropped_qty).alias("sensor_drop_quantity"),
                                       ((SlotDetails.quantity)-
                                       (fn.SUM(SlotTransaction.dropped_qty))).alias("sensor_dropping_error"),
                                       fn.DATE(fn.CONVERT_TZ(
                                           SlotTransaction.created_date_time, settings.TZ_UTC,
            offset)).alias("sensor_created_date"))\
            .join(SlotDetails, on=SlotDetails.id == SlotTransaction.slot_id)\
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id)\
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id)\
            .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id)\
            .join(PackAnalysisDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                             (UniqueDrug.txr == DrugMaster.txr)) \
            .where((PackAnalysisDetails.location_number.is_null(False)),
                   (fn.DATE(fn.CONVERT_TZ(
                       SlotTransaction.created_date_time, settings.TZ_UTC,
            offset)) == track_date))\
            .group_by(SlotDetails.id, SlotTransaction.canister_id).dicts()

        for record in query:
            drop_error_data.append(record)

        return drop_error_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_sensor_dropping_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_sensor_dropping_data: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_pvs_dropping_data(slot_list, slot_header_list):
    """
                        get_sensor_drug_error_data
    """
    try:
        pvs_data = []
        query = PVSSlot.select(PVSSlot.slot_image_name.alias("image_name"),
                               SlotDetails.id.alias("slot_id"),
                               PackVerificationDetails.predicted_quantity.alias("pvs_predicted_qty_total"),
                               PVSDrugCount.predicted_qty.alias("pvs_predicted_qty")) \
            .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug,
                  on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr)) \
            .join(PVSDrugCount, on=(PVSSlot.id == PVSDrugCount.pvs_slot_id) &
                                           (PVSDrugCount.unique_drug_id == UniqueDrug.id))\
            .join(PackVerificationDetails, on=PackVerificationDetails.slot_header_id == SlotHeader.id) \
            .where(SlotDetails.id << slot_list & SlotHeader.id << slot_header_list).dicts()

        for record in query:
            pvs_data.append(record)

        return pvs_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_pvs_dropping_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pvs_dropping_data: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_pack_id_and_slot_number(track_date, offset):
    """
                        get_sensor_drug_error_data
    """
    try:
        pill_jump_error_list = []

        query = PillJumpError.select(PillJumpError.pack_id.alias("pack_id"), PillJumpError.slot_number.alias("slot_number")) \
            .join(PackDetails, on=PackDetails.id == PillJumpError.pack_id) \
            .join(SlotHeader, on=PackDetails.id == SlotHeader.pack_id) \
            .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(SlotTransaction, on=SlotDetails.id == SlotTransaction.slot_id) \
            .where(fn.DATE(fn.CONVERT_TZ(
            SlotTransaction.created_date_time, settings.TZ_UTC,
            offset)) == track_date).dicts()

        for record in query:
            pill_jump_error_list.append(record)

        return pill_jump_error_list

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_pack_id_and_slot_number {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pack_id_and_slot_number: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_drug_data_of_error_slot(drug_id_list):
    """
                        get_sensor_drug_error_data
    """
    try:
        drug_list = []

        query = DrugDimension.select(UniqueDrug.id.alias("unique_drug_id"),
                                     DrugDimension.length.alias("drug_length"),
                                     DrugDimension.width.alias("drug_width"),
                                     DrugDimension.depth.alias("drug_depth"),
                                     DrugDimension.fillet.alias("drug_fillet"),
                                     CustomDrugShape.name.alias("drug_shape_name"))\
            .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id) \
            .join(UniqueDrug, on=DrugDimension.unique_drug_id == UniqueDrug.id)\
            .where(DrugDimension.unique_drug_id << drug_id_list).dicts()

        for record in query:
            drug_list.append(record)

        return drug_list
    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_drug_data_of_error_slot {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_drug_data_of_error_slot: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e



def get_location_data_of_error_slot(canister_id_list):
    """
                    get_sensor_drug_error_data
    """
    try:
        location_data = []
        query = CanisterMaster.select(LocationMaster.display_location.alias("display_location"),
                                      CanisterMaster.rfid.alias("canister_rfid"),
                                      CanisterMaster.id.alias("canister_id")) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .where(CanisterMaster.id << canister_id_list).dicts()

        for record in query:
            location_data.append(record)

        return location_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_location_data_of_error_slot {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_location_data_of_error_slot: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e




@log_args_and_response
def get_sensor_dropping_data_for_success_sensor_drug_drop(track_date, offset):
    """
                get_success_sensor_drug_drop
    """
    try:
        drop_error_data = []
        query = SlotTransaction.select(PackDetails.batch_id.alias("batch_id"),
                                       PackDetails.id.alias('pack_id'),
                                       PackGrid.slot_number.alias('slot_number'),
                                       SlotHeader.id.alias("slot_header_id"),
                                       SlotDetails.id.alias("slot_id"),
                                       DrugMaster.drug_name.alias("drug_name"),
                                       DrugMaster.image_name.alias("drug_image"),
                                       DrugMaster.ndc.alias("drug_ndc"),
                                       DrugMaster.formatted_ndc.alias("fndc"),
                                       DrugMaster.txr.alias("txr"),
                                       CanisterMaster.rfid.alias("canister_rfid"),
                                       SlotTransaction.canister_id.alias("canister_id"),
                                       PackAnalysisDetails.device_id.alias("device_id"),
                                       PackAnalysisDetails.drop_number.alias("drop_number"),
                                       PackAnalysisDetails.config_id.alias("config_id"),
                                       SlotDetails.quantity.alias("actual_qty"),
                                       fn.SUM(SlotTransaction.dropped_qty).alias("sensor_drop_quantity"),
                                       fn.DATE(fn.CONVERT_TZ(
                                           SlotTransaction.created_date_time, settings.TZ_UTC,
                                           offset)).alias("sensor_created_date")) \
            .join(SlotDetails, on=SlotDetails.id == SlotTransaction.slot_id) \
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id) \
            .join(PackAnalysisDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(CanisterMaster, on=CanisterMaster.id == SlotTransaction.canister_id)\
            .where((PackAnalysisDetails.location_number.is_null(False)),
                   (fn.DATE(fn.CONVERT_TZ(
                       SlotTransaction.created_date_time, settings.TZ_UTC,
                       offset)) == track_date)) \
            .group_by(SlotDetails.id, SlotTransaction.canister_id).dicts()

        for record in query:
            drop_error_data.append(record)

        return drop_error_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_sensor_dropping_data_for_success_sensor_drug_drop {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_sensor_dropping_data_for_success_sensor_drug_drop: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pill_jump_error_count(pack_id_for_sensor_data):
    """
        pvs_detection_problem_classification
    """
    try:
        pilljumperror_data= []
        query = PillJumpError.select(PillJumpError.pack_id.alias('pack_id'),
                                     PackVerification.pack_verified_status.alias('pack_verified_status'),
                                     fn.Count(fn.Distinct(PackVerification.pack_id)).alias("count"))\
            .join(PackVerification, on=PackVerification.pack_id == PillJumpError.pack_id)\
            .where(PackVerification.pack_id << pack_id_for_sensor_data)\
            .group_by(PackVerification.pack_verified_status).dicts()

        for record in query:
            pilljumperror_data.append(record)

        return pilljumperror_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_pill_jump_error_count {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pill_jump_error_count: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e
@log_args_and_response
def get_sensor_dropping_data_for_pvs_classification(system_id, company_id, pack_id_for_sensor_data):
    """
        pvs_detection_problem_classification
    """
    try:
        drop_error_data = []
        query = SlotDetails.select(PackDetails.id.alias('pack_id'),
                                       SlotHeader.id.alias("slot_header_id"),
                                       UniqueDrug.id.alias("unique_drug_id"),
                                       fn.CONCAT(UniqueDrug.formatted_ndc, '_', UniqueDrug.txr).alias('fndc_txr'),
                                       SlotDetails.quantity.alias("actual_qty"),
                                       fn.SUM(SlotTransaction.dropped_qty).alias("sensor_drop_quantity"),)\
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotDetails.id == SlotTransaction.slot_id)\
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id)\
            .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id)\
            .join(PackAnalysisDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                             (UniqueDrug.txr == DrugMaster.txr)) \
            .where((PackAnalysisDetails.location_number.is_null(False)),
                   (PackDetails.id << pack_id_for_sensor_data))\
            .group_by(SlotDetails.id, SlotTransaction.canister_id).dicts()

        for record in query:
            drop_error_data.append(record)

        return drop_error_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_sensor_dropping_data_for_pvs_classification {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_sensor_dropping_data_for_pvs_classification: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_drug_wise_count_for_packs(pack_id_for_sensor_data):
    """
        pvs_detection_problem_classification
    """
    try:
        drug_data = []
        query = SlotDetails.select(PackDetails.id.alias('pack_id'),
                                       SlotHeader.id.alias("slot_header_id"),
                                       UniqueDrug.id.alias("unique_drug_id"),
                                       fn.CONCAT(UniqueDrug.formatted_ndc, '_', UniqueDrug.txr).alias('fndc_txr'),
                                       fn.SUM(SlotDetails.quantity).alias("actual_qty"))\
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id)\
            .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id)\
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                             (UniqueDrug.txr == DrugMaster.txr)) \
            .where(PackDetails.id << pack_id_for_sensor_data)\
            .group_by(fn.CONCAT(UniqueDrug.formatted_ndc, '_', UniqueDrug.txr)).dicts()

        for record in query:
            drug_data.append(record)

        return drug_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_drug_wise_count_for_packs {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_drug_wise_count_for_packs: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_manual_pack_assigned_by_user_or_partially_filled_by_robot(from_date, to_date, offset):
    """
        pvs_detection_problem_classification
    """
    try:
        manual_pack_data = []
        PackStatusTrackerAlias = PackStatusTracker.alias()
        query = PackStatusTracker.select(PackStatusTracker.pack_id.alias("pack_id"),
                                       PackStatusTracker.status.alias("pack_status_id"),
                                         fn.DATE(fn.CONVERT_TZ(
                                             PackStatusTracker.created_date, settings.TZ_UTC,
                                             offset)).alias("pack_status_created_date"),
                                        PackUserMap.created_by, PackAnalysis.id.alias("pack_analysis_id"),
                                        PackAnalysisDetails.status.alias("pack_analysis_status"),
                                        PackHeader.change_rx_flag.alias("change_rx_flag"))\
            .join(PackUserMap, on=PackUserMap.pack_id == PackStatusTracker.pack_id)\
            .join(PackAnalysis, JOIN_LEFT_OUTER, on=PackAnalysis.pack_id == PackStatusTracker.pack_id) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
            .join(PackDetails, on=PackDetails.id == PackStatusTracker.pack_id)\
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id)\
            .where(((PackStatusTracker.status == settings.MANUAL_PACK_STATUS) |
                    (PackStatusTracker.status == settings.PARTIALLY_FILLED_BY_ROBOT)),
                   (fn.DATE(fn.CONVERT_TZ(
                       PackStatusTracker.created_date, settings.TZ_UTC,
            offset)).between(from_date, to_date))).dicts()

        for record in query:
            manual_pack_data.append(record)

        return manual_pack_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_manual_pack_assigned_by_user {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_pack_assigned_by_user: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e
@log_args_and_response
def get_manual_pack_assigned_by_user_and_done_with_from_date_to_date(from_date, to_date, offset, pack_ids):
    """
        pvs_detection_problem_classification
    """
    try:
        manual_pack_data = []
        query = PackStatusTracker.select(PackStatusTracker.pack_id.alias("pack_id"),
                                       PackStatusTracker.status.alias("pack_second_status_id"))\
            .where((PackStatusTracker.status == 5), (PackStatusTracker.pack_id << pack_ids),
                   (fn.DATE(fn.CONVERT_TZ(
                       PackStatusTracker.created_date, settings.TZ_UTC,
            offset)).between(from_date, to_date))).dicts()

        for record in query:
            manual_pack_data.append(record)

        return manual_pack_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_manual_pack_assigned_by_user {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_pack_assigned_by_user: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def get_manual_pack_assigned_by_user_or_partially_filled_by_robot_for_analyzer(track_date, offset):
    """
        pvs_detection_problem_classification
    """
    try:
        manual_pack_data = []
        query = PackStatusTracker.select(PackStatusTracker.pack_id.alias("pack_id"),
                                         PackStatusTracker.status.alias("pack_status_id"),
                                         fn.DATE(fn.CONVERT_TZ(
                                             PackStatusTracker.created_date, settings.TZ_UTC,
                                             offset)).alias("pack_status_created_date"),
                                         PackUserMap.created_by, PackAnalysis.id.alias("pack_analysis_id"),
                                         BatchManualPacks.pack_id.alias("batch_manual_pack_id"),
                                         PackHeader.change_rx_flag.alias("change_rx_flag")) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackStatusTracker.pack_id) \
            .join(PackAnalysis, JOIN_LEFT_OUTER, on=PackAnalysis.pack_id == PackStatusTracker.pack_id) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
            .join(PackDetails, on=PackDetails.id == PackStatusTracker.pack_id) \
            .join(BatchManualPacks, JOIN_LEFT_OUTER, on=BatchManualPacks.pack_id == PackDetails.id) \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .where(((PackStatusTracker.status == settings.MANUAL_PACK_STATUS) |
                    (PackStatusTracker.status == settings.PARTIALLY_FILLED_BY_ROBOT)),
                   (fn.DATE(fn.CONVERT_TZ(
                       PackStatusTracker.created_date, settings.TZ_UTC,
                       offset)) == track_date)).dicts()

        for record in query:
            manual_pack_data.append(record)

        return manual_pack_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_manual_pack_assigned_by_user {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_pack_assigned_by_user: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def get_manual_pack_assigned_by_user_and_done(track_date, offset, pack_ids):
    """
        pvs_detection_problem_classification
    """
    try:
        manual_pack_data = []
        query = PackStatusTracker.select(PackStatusTracker.pack_id.alias("pack_id"),
                                       PackStatusTracker.status.alias("pack_second_status_id"))\
            .where((PackStatusTracker.status == 5), (PackStatusTracker.pack_id << pack_ids),
                   (fn.DATE(fn.CONVERT_TZ(
                       PackStatusTracker.created_date, settings.TZ_UTC,
            offset)) == track_date)).dicts()

        for record in query:
            manual_pack_data.append(record)

        return manual_pack_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_manual_pack_assigned_by_user {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_pack_assigned_by_user: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e
@log_args_and_response
def get_change_rx_manual_pack_details(track_date, offset):
    """
        pvs_detection_problem_classification
    """
    try:
        manual_pack_data = []
        PackStatusTrackerAlias = PackStatusTracker.alias()
        query = PackStatusTracker.select(PackStatusTracker.pack_id.alias("pack_id"),
                                       PackStatusTracker.status.alias("pack_status_id"),
                                       PackStatusTracker.created_date.alias("pack_status_created_date"),
                                       CodeMaster.value.alias("pack_second_status"),
                                       PackStatusTrackerAlias.created_date.alias("pack_second_status_created_date"),
                                         PackUserMap.assigned_to, PackAnalysis.id.alias("pack_analysis_id"))\
            .join(PackStatusTrackerAlias, on=(PackStatusTracker.pack_id == PackStatusTrackerAlias.pack_id) and
                                             (PackStatusTracker.status != PackStatusTrackerAlias.status))\
            .join(PackUserMap, on=PackUserMap.pack_id == PackStatusTracker.pack_id)\
            .join(CodeMaster, on=CodeMaster.id == PackStatusTrackerAlias.status)\
            .join(PackAnalysis, JOIN_LEFT_OUTER, on=PackAnalysis.pack_id == PackStatusTracker.pack_id) \
            .where(((PackStatusTracker.status == settings.MANUAL_PACK_STATUS) or
                    (PackStatusTracker.status == settings.PARTIALLY_FILLED_BY_ROBOT)),
                   (fn.DATE(fn.CONVERT_TZ(
                       PackStatusTracker.created_date, settings.TZ_UTC,
            offset)) == track_date)).dicts()

        for record in query:
            manual_pack_data.append(record)

        return manual_pack_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_manual_pack_assigned_by_user {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_manual_pack_assigned_by_user: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_pvs_slot_data_and_drug_status(slot_header_list):
    """
            pvs_detection_problem_classification
    """
    try:
        pvs_data = []
        query = PVSSlot.select(PVSSlot.id.alias('pvs_slot_id'),
                               PackAnalysisDetails.quadrant.alias("quadrant"),
                               SlotDetails.id.alias("slot_id"),
                               SlotHeader.id.alias("slot_header_id"),
                               UniqueDrug.id.alias("unique_drug_id"),
                               fn.CONCAT(UniqueDrug.formatted_ndc,'_',UniqueDrug.txr).alias('fndc_txr'),
                               PRSDrugDetails.status.alias("status"))\
            .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(PackAnalysisDetails, on=(SlotDetails.id == PackAnalysisDetails.slot_id) & (PVSSlot.quadrant==PackAnalysisDetails.quadrant)) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                 (UniqueDrug.txr == DrugMaster.txr))\
            .join(PRSDrugDetails, on=PRSDrugDetails.unique_drug_id == UniqueDrug.id)\
            .where(SlotHeader.id << slot_header_list).dicts()

        for record in query:
            pvs_data.append(record)

        return pvs_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_pvs_slot_data_and_drug_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pvs_slot_data_and_drug_status: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def get_pvs_data_header_wise(slot_header_list):
    """
            pvs_detection_problem_classification
    """
    try:
        pvs_data = []

        query = PackVerificationDetails.select(SlotHeader.id.alias("slot_header_id"),
                               PackVerificationDetails.predicted_quantity.alias("pvs_predicted_qty_total")) \
            .join(SlotHeader, on=PackVerificationDetails.slot_header_id == SlotHeader.id)\
            .where(SlotHeader.id << slot_header_list).dicts()

        for record in query:
            pvs_data.append(record)

        return pvs_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_pvs_data_header_wise {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pvs_data_header_wise: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def get_pvs_slot_details_data_for_pvs_classification(pvs_slot):
    """
            pvs_detection_problem_classification
    """
    try:
        pvs_slot_details = []

        query = PVSSlotDetails.select(PVSSlotDetails.pvs_slot_id.alias("pvs_slot_id"), fn.GROUP_CONCAT(fn.DISTINCT(PVSSlotDetails.pvs_classification_status))
                                      .coerce(False).alias('pvs_classification_status')).where(PVSSlotDetails.pvs_slot_id << pvs_slot)\
            .group_by(PVSSlotDetails.pvs_slot_id).dicts()

        for record in query:
            pvs_slot_details.append(record)

        return pvs_slot_details

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_pvs_slot_details_data_for_pvs_classification {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pvs_slot_details_data_for_pvs_classification: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e

@log_args_and_response
def get_sensor_dropping_data_for_csv(system_id, company_id, track_date, offset):
    """
                    For getcsvdataforsensorerror
    """
    try:
        drop_error_data = []
        query = SlotTransaction.select(PackDetails.batch_id.alias("batch_id"),
                                       PackDetails.id.alias("pack_id"),
                                       PackGrid.slot_number.alias('slot_number'),
                                       SlotHeader.id.alias("slot_header_id"),
                                       SlotDetails.id.alias("slot_id"),
                                       CanisterMaster.rfid.alias("rfid"),
                                       CanisterMaster.threshold.alias("threshold"),
                                       UniqueDrug.id.alias("unique_drug_id"),
                                       DrugMaster.drug_name.alias("drug_name"),
                                       DrugMaster.image_name.alias("drug_image"),
                                       DrugMaster.ndc.alias("drug_ndc"),
                                       DrugMaster.formatted_ndc.alias("fndc"),
                                       DrugMaster.txr.alias("txr"),
                                       DrugDimension.length.alias("drug_length"),
                                       DrugDimension.width.alias("drug_width"),
                                       DrugDimension.depth.alias("drug_depth"),
                                       DrugDimension.fillet.alias("drug_fillet"),
                                       CustomDrugShape.name.alias("drug_shape_name"),
                                       SlotTransaction.canister_id.alias("canister_id"),
                                       PackAnalysisDetails.device_id.alias("device_id"),
                                       PackAnalysisDetails.drop_number.alias("drop_number"),
                                       PackAnalysisDetails.config_id.alias("config_id"),
                                       PackAnalysisDetails.quadrant.alias("quadrant"),
                                       LocationMaster.display_location.alias("display_location"),
                                       SlotDetails.quantity.alias("actual_qty"),
                                       fn.SUM(SlotTransaction.dropped_qty).alias("sensor_drop_quantity")) \
            .join(SlotDetails, on=SlotDetails.id == SlotTransaction.slot_id) \
            .join(CanisterMaster, on=CanisterMaster.id == SlotTransaction.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id)\
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id)\
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id)\
            .join(PackDetails, on=PackDetails.id == SlotHeader.pack_id)\
            .join(PackAnalysisDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                             (UniqueDrug.txr == DrugMaster.txr)) \
            .join(DrugDimension, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id) \
            .where((PackAnalysisDetails.location_number.is_null(False)),
                   (fn.DATE(fn.CONVERT_TZ(
                       SlotTransaction.created_date_time, settings.TZ_UTC,
            offset)) == track_date))\
            .group_by(SlotDetails.id, SlotTransaction.canister_id).dicts()

        for record in query:
            drop_error_data.append(record)

        return drop_error_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_sensor_dropping_data_for_csv {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_sensor_dropping_data_for_csv: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_pvs_dropping_data_for_csv(slot_list, slot_header_list):
    """
                        getcsvdataforsensorerror
    """
    try:
        pvs_data = []
        query = PVSSlot.select(SlotDetails.id.alias("slot_id"),
                               PVSSlot.slot_image_name.alias("image_name"),
                               PackVerificationDetails.predicted_quantity.alias("pvs_predicted_qty_total")) \
            .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug,
                  on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr)) \
            .join(PVSDrugCount, on=(PVSSlot.id == PVSDrugCount.pvs_slot_id) &
                                   (PVSDrugCount.unique_drug_id == UniqueDrug.id)) \
            .join(PackVerificationDetails, on=PackVerificationDetails.slot_header_id == SlotHeader.id) \
            .where(SlotDetails.id << slot_list & SlotHeader.id << slot_header_list).dicts()

        for record in query:
            pvs_data.append(record)

        return pvs_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_pvs_dropping_data_for_csv {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pvs_dropping_data_for_csv: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_filled_slot_count_of_pack_with_packid_batchid(pack_ids):
    """
                        getfilledslotcountforpack
    """
    try:
        pack_data = []
        query = SlotHeader.select(SlotHeader.pack_id.alias("event_pack_id"),
                                   fn.COUNT(SlotHeader.id).alias('slot_count')) \
            .where(SlotHeader.pack_id << pack_ids)\
            .group_by(SlotHeader.pack_id).dicts()

        for record in query:
            pack_data.append(record)

        return pack_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_filled_slot_count_of_pack_with_packid_batchid {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_filled_slot_count_of_pack_with_packid_batchid: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_user_report_pack_detail(from_date, to_date, offset):
    """
                        get_user_report_pack_detail
    """
    try:
        user_report_error_pack_data = []
        query = PackFillErrorV2.select(PackFillErrorV2.unique_drug_id.alias("unique_drug_id"),
                                       PackFillErrorV2.pack_id.alias('pack_id'),
                                       PackFillErrorV2.unique_drug_id.alias('unique_drug_id'),
                                       PackVerification.id.alias('pack_verification_id'),
                                       PackVerification.pack_verified_status.alias('pack_verification_status'),
                                       SlotHeader.id.alias('slot_header_id'),
                                       PackVerificationDetails.colour_status.alias('slot_color_status'),
                                       PackVerificationDetails.predicted_quantity.alias('pvs_quantity'),
                                       PackVerificationDetails.dropped_quantity.alias('sensor_quantity'),
                                       PackVerificationDetails.compare_quantity.alias('compare_quantity'),
                                       CodeMaster.value.alias('color_status_value'),
                                       PackGrid.slot_number.alias('slot_number'),
                                       SlotFillErrorV2.broken.alias('broken'),
                                       SlotFillErrorV2.actual_qty.alias('actual_qty'),
                                       SlotFillErrorV2.counted_error_qty.alias('counted_error_qty'),
                                       SlotFillErrorV2.out_of_class_reported.alias('out_of_class_reported'),
                                       SlotFillErrorV2.id.alias('slot_fill_id'),
                                       PackError.comments.alias('user_comment'),
                                       PackFillErrorV2.created_by.alias('created_by'),
                                       fn.DATE(fn.CONVERT_TZ(
                                           PackFillErrorV2.created_date, settings.TZ_UTC, offset)).alias('date')
                                       )\
            .join(SlotFillErrorV2, on=SlotFillErrorV2.pack_fill_error_id == PackFillErrorV2.id) \
            .join(PackGrid, on=PackGrid.id == SlotFillErrorV2.pack_grid_id)\
            .join(SlotHeader, on=(SlotHeader.pack_grid_id == PackGrid.id) &
                                 (SlotHeader.pack_id == PackFillErrorV2.pack_id))\
            .join(PackVerification, on=PackVerification.pack_id == PackFillErrorV2.pack_id) \
            .join(PackVerificationDetails, on=PackVerificationDetails.slot_header_id == SlotHeader.id) \
            .join(CodeMaster, on=CodeMaster.id == PackVerificationDetails.colour_status) \
            .join(PackError,JOIN_LEFT_OUTER, on=PackError.pack_id == PackFillErrorV2.pack_id)\
            .where((fn.DATE(fn.CONVERT_TZ(
                       PackFillErrorV2.created_date, settings.TZ_UTC, offset)).between(from_date, to_date))).dicts()

        for record in query:
            user_report_error_pack_data.append(record)

        return user_report_error_pack_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_user_report_pack_detail {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_user_report_pack_detail: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_graph_data_for_slot_header(slot_header, pack_id, offset):
    """
                        get_user_report_pack_detail
    """
    try:
        slot_header_data = []
        query = PVSSlot.select(PVSSlot.slot_image_name.alias("slot_image_name"),
                                PVSSlot.slot_header_id.alias('slot_header_id'),
                               PVSSlot.quadrant.alias('quadrant')) \
            .where(PVSSlot.slot_header_id << slot_header).dicts()

        for record in query:
            slot_header_data.append(record)
        pack_date = []
        query = SlotTransaction.select(fn.DATE(fn.CONVERT_TZ(
                       SlotTransaction.created_date_time, settings.TZ_UTC, offset)).alias('sensor_date'),
                                       SlotTransaction.pack_id.alias('pack_id')) \
            .where(SlotTransaction.pack_id << pack_id).dicts()

        for record in query:
            pack_date.append(record)

        return slot_header_data, pack_date

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_graph_data_for_slot_header {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_graph_data_for_slot_header: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_slot_header_detail(slot_header):
    """
                        get_user_report_pack_detail
    """
    try:
        slot_header_data = []
        slot_header_pvs_data = []
        query = SlotDetails.select(SlotDetails.slot_id.alias('slot_header_id'),
                                   SlotDetails.id.alias('slot_id'),
                                   SlotDetails.quantity.alias('quantity'),
                                   fn.SUM(SlotTransaction.dropped_qty).alias("sensor_drop_quantity"),
                                   DrugMaster.id.alias('drug_id'),
                                   DrugMaster.drug_name.alias('drug_name'),
                                   DrugMaster.image_name.alias('image_name'),
                                   fn.CONCAT(
                                      DrugMaster.strength_value, ' ', DrugMaster.strength).alias(
                                      'strength'),
                                   UniqueDrug.id.alias('unique_drug_id'),
                                   UniqueDrug.formatted_ndc.alias('fndc'),
                                   UniqueDrug.txr.alias('txr'),
                                   CanisterMaster.id.alias('canister_id'),
                                   CanisterMaster.rfid.alias('rfid'),
                                   PackAnalysisDetails.device_id.alias("device_id"),
                                   PackAnalysisDetails.drop_number.alias("drop_number"),
                                   PackAnalysisDetails.config_id.alias("config_id"),
                                   PackAnalysisDetails.quadrant.alias("quadrant"),
                                   LocationMaster.display_location.alias("display_location"),
                                   )\
            .join(SlotTransaction, JOIN_LEFT_OUTER, on=SlotDetails.id == SlotTransaction.slot_id)\
            .join(PackAnalysisDetails, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                            (UniqueDrug.txr == DrugMaster.txr)) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id)\
            .where(SlotDetails.slot_id << slot_header) \
            .group_by(SlotDetails.id, SlotTransaction.canister_id).dicts()
        query2 = PVSSlot.select(PVSDrugCount.predicted_qty.alias('pvs_predicted_quantity'),
                                PVSDrugCount.unique_drug_id.alias('unique_drug_id'),
                                PVSSlot.slot_header_id.alias('slot_header_id'))\
            .join(PVSDrugCount, on=PVSSlot.id == PVSDrugCount.pvs_slot_id) \
            .where(PVSSlot.slot_header_id << slot_header).dicts()

        for record in query:
            slot_header_data.append(record)
        for record in query2:
            slot_header_pvs_data.append(record)

        return slot_header_data, slot_header_pvs_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_slot_header_detail {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_slot_header_detail: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e


def get_pack_count_for_user_report_error(from_date, to_date, offset):
    """
            get_pack_count_for_user_report_error
    """
    try:
        filled_date = fn.DATE(fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC, offset))
        pack_count_list = dict()
        pack_count_query = PackDetails.select(fn.COUNT(PackDetails.id).alias('pack_count')) \
            .where(filled_date.between(from_date, to_date), PackDetails.filled_at << [3, 11]).dicts()

        for pack in pack_count_query:
            pack_count_list['pack_count'] = pack['pack_count']
        print(pack_count_list)
        return pack_count_list
    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in get_pack_count_for_user_report_error {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in get_pack_count_for_user_report_error: exc_type - {exc_type}, "
            f"filename - {filename}, "f"line - {exc_tb.tb_lineno}")
        raise e

def get_drug_details_by_drug(ndc: list) -> list:
    """
    1. Displays current drug and drug dimension related details
    @param values: ndc
    @return record: current drug and drug dimension related details of particular drug
    """
    drug_details = list()
    clauses = list()
    clauses.append((DrugMaster.ndc << ndc))
    try:
        query = DrugMaster.select(DrugMaster.ndc.alias('ndc'),
                                  DrugMaster.concated_fndc_txr_field().alias('fndc_txr'),
                                  DrugMaster.drug_name,
                                  DrugMaster.strength,
                                  DrugMaster.strength_value,
                                  DrugDimension.width,
                                  DrugDimension.length,
                                  DrugDimension.depth,
                                  DrugDimension.fillet,
                                  CustomDrugShape.name.alias('custom_shape')
                                  ).dicts() \
            .join(UniqueDrug, on=(DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                 (DrugMaster.txr == UniqueDrug.txr)) \
            .join(DrugDimension, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id).where(DrugMaster.ndc << ndc) \
            .group_by(DrugMaster.concated_fndc_txr_field())
        # if clauses:
        #     query = query.where(functools.reduce(operator.and_, clauses))
        for record in query:
            drug_details.append(record)
        return drug_details
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.info(e)
        raise e

def get_canister_details_by_drug(drug_ndc: list) -> list:
    """
    1. Displays current drug and drug dimension related details
    @param values: drug ndc
    @return record: current drug and drug dimension related details of particular drug
    """
    canister_details = list()
    try:
        query = DrugMaster.select(DrugMaster.ndc.alias('ndc'),
                                  fn.group_concat(fn.DISTINCT(CanisterMaster.id)).alias('canister_id'),
                                  fn.group_concat(fn.CONCAT(CanisterMaster.id, ':', BigCanisterStick.serial_number, ':',
                                                            CanisterMaster.active)).alias(
                                      'big_canister_stick_serial_number'),
                                  fn.group_concat(fn.DISTINCT(BigCanisterStick.width)).alias(
                                      'big_canister_stick_width'),
                                  fn.group_concat(fn.DISTINCT(BigCanisterStick.depth)).alias(
                                      'big_canister_stick_depth'),
                                  fn.group_concat(fn.DISTINCT(SmallCanisterStick.length)).alias(
                                      'small_canister_stick_serial_number_length'),
                                  fn.group_concat(fn.CONCAT(CanisterMaster.id, ':', CanisterDrum.serial_number, ':',
                                                            CanisterMaster.active)).alias(
                                      'canister_drum_serial_number'),
                                  fn.group_concat(CanisterMaster.active.concat('-')).alias('canister_activation_status')
                                  ).dicts() \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(CanisterStick, JOIN_LEFT_OUTER, on=CanisterMaster.canister_stick_id == CanisterStick.id) \
            .join(BigCanisterStick, JOIN_LEFT_OUTER, on=CanisterStick.big_canister_stick_id == BigCanisterStick.id) \
            .join(SmallCanisterStick, JOIN_LEFT_OUTER,
                  on=CanisterStick.small_canister_stick_id == SmallCanisterStick.id) \
            .join(CanisterDrum, JOIN_LEFT_OUTER, on=CanisterStick.canister_drum_id == CanisterDrum.id) \
            .where(DrugMaster.ndc << drug_ndc).group_by(DrugMaster.ndc)
        for record in query:
            canister_details.append(record)
        return canister_details
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.info(e)
        raise e
