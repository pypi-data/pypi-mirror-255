
from peewee import InternalError, IntegrityError, DoesNotExist, DataError, fn, JOIN_LEFT_OUTER

import settings
from dosepack.utilities.utils import log_args, log_args_and_response
from src import constants
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_canister_tx_meta import CanisterTxMeta
from src.model.model_frequent_mfd_drugs import FrequentMfdDrugs
from src.model.model_guided_meta import GuidedMeta
from src.model.model_guided_tracker import GuidedTracker
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_user_map import PackUserMap
from src.model.model_patient_master import PatientMaster
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_slot_details import SlotDetails
from src.model.model_temp_mfd_filling import TempMfdFilling
from src.model.model_drug_tracker import DrugTracker
from src.model.model_replenish_skipped_canister import ReplenishSkippedCanister

logger = settings.logger


@log_args_and_response
def get_pack_ids_from_batch_id(batch_id: int) -> tuple:
    """
    Function to get pack list for given batch_id
    @param batch_id:
    @return:
    """
    pack_id_list: list = list()
    pending_pack_id_list: list = list()
    try:
        pack_query = PackDetails.select(PackDetails.id, PackDetails.pack_status).dicts() \
            .where(PackDetails.batch_id == batch_id)

        for data in pack_query:
            pack_id_list.append(data['id'])
            if data['pack_status'] == settings.PENDING_PACK_STATUS:
                pending_pack_id_list.append(data['id'])

        return pack_id_list, pending_pack_id_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_pack_ids_from_batch_id: {}".format(e))
        raise e
    except DoesNotExist as e:
        logger.error(e)
        return pack_id_list, pending_pack_id_list


@log_args_and_response
def get_pack_analysis_details_ids_by_batch(pack_list: list, batch_id: int or None = None) -> list:
    """
    Function to get analysis id list from pack_analysis for given batch
    @param batch_id:
    @param pack_list:
    @return:
    """
    try:
        pack_analysis = PackAnalysis.select().dicts().where(PackAnalysis.pack_id << pack_list)
        if batch_id:
            pack_analysis = pack_analysis.where(PackAnalysis.batch_id == batch_id)

        analysis_ids_list = [item['id'] for item in list(pack_analysis)]
        return analysis_ids_list
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in get_pack_analysis_details_ids_by_batch: {}".format(e))
        raise e


@log_args_and_response
def delete_data_from_pack_analysis_tables(batch_id: int or None, analysis_ids: list) -> bool:
    """
    Function to delete data from pack_analysis and pack_analysis_details for given batch and analysis ids
    @param batch_id:
    @param analysis_ids:
    @return:
    """
    try:
        if analysis_ids:
            pack_analysis = PackAnalysisDetails.delete().where(
                PackAnalysisDetails.analysis_id << analysis_ids).execute()

            if batch_id:
                pack_analysis_details = PackAnalysis.delete().where(PackAnalysis.id << analysis_ids,
                                                                    PackAnalysis.batch_id == batch_id).execute()
            else:
                pack_analysis_details = PackAnalysis.delete().where(PackAnalysis.id << analysis_ids).execute()

            logger.info("In delete_data_from_pack_analysis_tables: pack_analysis and pack_analysis_details delete status {}, {}"
                        .format(pack_analysis, pack_analysis_details))
            return True

        return False

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise e


@log_args_and_response
def delete_reserved_canister_for_batch(batch_id: int or None = None, canister_ids: list = None) -> bool:
    """
    Function to delete data from reserved_canister table for given batch
    @param canister_ids:
    @param batch_id:
    @return:
    """
    try:
        if canister_ids:
            reserved_canister = ReservedCanister.delete().where(ReservedCanister.batch_id == batch_id,
                                                                ReservedCanister.canister_id.not_in(canister_ids)).execute()
        else:
            if batch_id:
                reserved_canister = ReservedCanister.delete().where(ReservedCanister.batch_id == batch_id).execute()
            else:
                reserved_canister = ReservedCanister.delete().execute()
        logger.info("IN delete_reserved_canister_for_batch: reserved_canister delete status {}".format(reserved_canister))
        return reserved_canister

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def get_mfd_analysis_ids_by_batch(pack_list: list, batch_id: int or None = None) -> list:
    """
    Function to get analysis ids from mfd_analysis for given batch
    @param batch_id:
    @param pack_list:
    @return:
    """
    try:
        mfd_analysis = MfdAnalysis.select(fn.DISTINCT(MfdAnalysis.id)).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .where(PackDetails.id << pack_list)
        if batch_id:
            mfd_analysis = mfd_analysis.where(PackDetails.batch_id == batch_id)

        analysis_ids_list = [item['id'] for item in list(mfd_analysis)]
        return analysis_ids_list
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in get_mfd_analysis_ids_by_batch: {}".format(e))
        raise e


@log_args_and_response
def delete_mfd_analysis_data(batch_id: int or None, mfd_analysis_ids: list) -> bool:
    """
    Function to delete data from mfd_analysis and mfd_analysis_details for given batch
    @param batch_id:
    @param mfd_analysis_ids:
    @return:
    """
    try:
        if mfd_analysis_ids:
            temp_mfd_filling = TempMfdFilling.delete().where(TempMfdFilling.mfd_analysis_id << mfd_analysis_ids).execute()
            logger.info("delete_mfd_analysis_data temp_mfd_filling {}".format(temp_mfd_filling))

            mfd_analysis = MfdAnalysisDetails.delete().where(MfdAnalysisDetails.analysis_id << mfd_analysis_ids).execute()

            if batch_id:
                mfd_analysis_details = MfdAnalysis.delete().where(MfdAnalysis.id << mfd_analysis_ids,
                                                              MfdAnalysis.batch_id == batch_id).execute()
            else:
                mfd_analysis_details = MfdAnalysis.delete().where(MfdAnalysis.id << mfd_analysis_ids).execute()

            logger.info("In delete_mfd_analysis_data: mfd_analysis and mfd_analysis_details delete status {}, {}"
                        .format(mfd_analysis, mfd_analysis_details))
            return True

        return False

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def delete_canister_transfers_for_batch(batch_id: int, canister_ids: list = None,
                                        revert_pack_id_list: list = None) -> bool:
    """
    Function to delete data from canister_transfers for given batch
    @param revert_pack_id_list:
    @param canister_ids:
    @param batch_id:
    @return:
    """
    try:
        canister_meta: bool = False
        if revert_pack_id_list:
            if canister_ids:
                canister_transfers = CanisterTransfers.delete().where(CanisterTransfers.batch_id == batch_id,
                                                                      CanisterTransfers.canister_id.not_in(canister_ids)).execute()
            else:
                canister_transfers = CanisterTransfers.delete().where(CanisterTransfers.batch_id == batch_id).execute()
        else:
            canister_transfers = CanisterTransfers.delete().where(CanisterTransfers.batch_id == batch_id).execute()
            canister_meta = CanisterTxMeta.delete().where(CanisterTxMeta.batch_id == batch_id).execute()

        logger.info("canister_transfers and canister_meta delete status {}, {}".format(canister_transfers,
                                                                                       canister_meta))
        return True

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def delete_drug_tracker_data_for_batch(analysis_ids,
                                       mfd_analysis_ids):
    """
    Function to delete data from canister_transfers for given batch
    @param analysis_ids:
    @param mfd_analysis_ids:
    @return:
    """
    try:
        delete_status = None
        slot_ids_for_pack_analysis = PackAnalysisDetails.db_get_slot_id_from_pack_analysis_ids(analysis_ids=analysis_ids)
        slot_ids_for_mfd_analysis = MfdAnalysisDetails.db_get_slot_id_from_pack_analysis_ids(mfd_analysis_ids=mfd_analysis_ids)

        logger.info("In delete_drug_tracker_data_for_batch: slot_ids_for_pack_analysis: {}, slot_ids_for_mfd_analysis: {}"
                    .format(slot_ids_for_pack_analysis, slot_ids_for_mfd_analysis))

        final_slot_ids = slot_ids_for_pack_analysis + slot_ids_for_mfd_analysis

        logger.info("In delete_drug_tracker_data_for_batch: final_slot_ids: {}".format(final_slot_ids))

        if final_slot_ids:
            delete_status = DrugTracker.db_delete_drug_tracker_by_slot_id(slot_ids=final_slot_ids)
            logger.info("In delete_drug_tracker_data_for_batch: delete_status: {}".format(delete_status))

        return delete_status

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in delete_drug_tracker_data_for_batch: {}".format(e))
        raise


@log_args_and_response
def delete_replenish_skipped_canister_data_for_batch(pack_list: list):
    try:
        status = None
        if pack_list:
            status = ReplenishSkippedCanister.delete()\
                .where(ReplenishSkippedCanister.pack_id << pack_list).execute()
            logger.info("In delete_replenish_skipped_canister_data_for_batch: delete_status: {}".format(status))

        return status
    except Exception as e:
        logger.error("Error in delete_replenish_skipped_canister_data_for_batch: {}".format(e))
        raise e


@log_args_and_response
def get_guided_meta_id_for_batch(batch_id: int) -> list:
    """
    Function to get meta_ids from guided_meta for given batch
    @param batch_id:
    @return:
    """
    logger.debug("Inside get_guided_meta_id_for_batch")
    try:
        meta_id = GuidedMeta.select(GuidedMeta.id).dicts().where(GuidedMeta.batch_id == batch_id)
        meta_id_list = [item['id'] for item in list(meta_id)]
        return meta_id_list

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise


@log_args
def delete_guided_data_for_batch(batch_id: int, guided_meta_id: list):
    """
    Function to delete data from guided_meta and guided_tracker for given batch
    @param guided_meta_id:
    @param batch_id:
    @return:
    """
    logger.debug("Inside delete_guided_data_for_batch")
    try:
        if len(guided_meta_id):
            guided_tracker = GuidedTracker.delete().where(GuidedTracker.guided_meta_id << guided_meta_id).execute()
            guided_meta = GuidedMeta.delete().where(GuidedMeta.batch_id == batch_id,
                                                    GuidedMeta.id << guided_meta_id).execute()

            logger.info("guided_tracker and guided_meta delete status {}, {}".format(guided_tracker,
                                                                                     guided_meta))
        return True

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise


@log_args
def update_pack_status_revert_batch(batch_id: int, pack_list: list) -> bool:
    """
    Function to update pack_status to pending for given pack_list
    @param batch_id:
    @param pack_list:
    @return:
    """
    try:
        update_query = PackDetails.update(pack_status=settings.PENDING_PACK_STATUS) \
            .where(PackDetails.id << pack_list,
                   PackDetails.batch_id == batch_id).execute()

        logger.info("update_pack_status_revert_batch {}".format(update_query))
        return update_query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise e


@log_args_and_response
def update_pack_details_data_for_batch(pack_list: list, update_dict: dict, batch_id: int or None = None) -> bool:
    """
    FUnction to update required fields as null in pack_details table
    @param batch_id:
    @param update_dict:
    @param pack_list:
    @return:
    """
    try:
        if batch_id:
            update_query = PackDetails.update(**update_dict) \
                .where(PackDetails.id << pack_list, PackDetails.batch_id == batch_id).execute()
        else:
            update_query = PackDetails.update(**update_dict) \
                .where(PackDetails.id << pack_list).execute()

        if pack_list:

            logger.info("In update_pack_details_data_for_batch, removing packs from pack_queue")
            status = PackQueue.delete().where(PackQueue.pack_id << pack_list).execute()
            logger.info(f"In update_pack_details_data_for_batch, packs removed from pack_queue, status: {status}")

        logger.info("In update_pack_details_data_for_batch for packs {}, batch_id: {}".format(update_query, batch_id))
        return update_query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in update_pack_details_data_for_batch:".format(e))
        raise e


@log_args_and_response
def update_batch_master_revert_batch(batch_update_dict: dict, batch_id: int or None = None) -> bool:
    """
    Function to update status of batch to pending in batch_master
    @param batch_update_dict:
    @param batch_id:
    @return:
    """
    try:
        update_query = None
        if not batch_id:
            batch_id_query = BatchMaster.select(BatchMaster.id).dicts().where(BatchMaster.status == settings.BATCH_IMPORTED).order_by(BatchMaster.id.desc()).limit(1)
            for data in batch_id_query:
                batch_id = data["id"]
        if batch_id:
            update_query = BatchMaster.update(**batch_update_dict).where(BatchMaster.id == batch_id).execute()

        logger.info("update_batch_master_revert_batch {}".format(update_query))
        return update_query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in update_batch_master_revert_batch: {}".format(e))
        raise e


@log_args_and_response
def get_mfs_system_device_from_company_id(company_id: int, batch_id: int) -> dict:
    """
    Function to get MFS system and device id from given company and batch
    @param company_id:
    @param batch_id:
    @return:
    """
    system_device_dict: dict = dict()
    zone_ids: list = list()
    try:
        # get system id from batch_id
        system_id = BatchMaster.db_get_system_id_from_batch_id(batch_id=batch_id)

        # get zone from system id
        query = DeviceLayoutDetails.select(DeviceLayoutDetails.zone_id).dicts() \
            .join(DeviceMaster, on=DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .where(DeviceMaster.system_id == system_id)

        for record in query:
            if record['zone_id'] not in zone_ids:
                zone_ids.append(record['zone_id'])
        if not zone_ids:
            return system_device_dict

        # query to get MFS devices with their system id of given zone
        query = DeviceMaster.select(DeviceMaster.id.alias('device_id'),
                                    DeviceMaster.system_id).dicts() \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, on=DeviceMaster.id == DeviceLayoutDetails.device_id) \
            .where(DeviceMaster.company_id == company_id,
                   DeviceMaster.active == settings.is_device_active,
                   DeviceLayoutDetails.zone_id << zone_ids,
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES['Manual Filling Device']) \
            .group_by(DeviceMaster.id).order_by(DeviceMaster.id)

        for record in query:
            system_device_dict[record['system_id']] = record['device_id']

        return system_device_dict

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in get_mfs_system_device_from_company_id: {}".format(e))
        raise


@log_args_and_response
def get_mfd_filled_pack_ids_by_batch(batch_id: int or None = None) -> tuple:
    """
    Function to get mfd filled pack ids by batch
    @param batch_id:
    @return:

    """
    filled_patient_id: list = list()
    filled_mfd_pack_ids: list = list()
    mfd_filled_or_progress_status = [constants.MFD_CANISTER_FILLED_STATUS,
                                     constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                     constants.MFD_CANISTER_VERIFIED_STATUS]
    try:
        mfd_analysis = MfdAnalysis.select(PackDetails.id.alias("pack_id"),
                                          PatientMaster.id.alias("patient_id"),
                                          fn.COUNT(fn.DISTINCT(MfdAnalysis.id)).coerce(False).alias('analysis_id')).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PatientMaster, on=PatientMaster.id == PackHeader.patient_id)

        if batch_id:
            mfd_analysis = mfd_analysis.where(PackDetails.batch_id == batch_id,
                            (MfdAnalysis.status_id.in_(mfd_filled_or_progress_status) | MfdAnalysis.transferred_location_id.is_null(False))) \
                            .group_by(PackDetails.id)
        if not batch_id:
            mfd_analysis = mfd_analysis.join(PackQueue, on=PackQueue.pack_id == PackDetails.id) \
                                        .where((MfdAnalysis.status_id.in_(mfd_filled_or_progress_status) | MfdAnalysis.transferred_location_id.is_null(False))) \
                                        .group_by(PackDetails.id)

        for item in mfd_analysis:
            filled_patient_id.append(item['patient_id'])
            filled_mfd_pack_ids.append(item['pack_id'])

        return filled_patient_id, filled_mfd_pack_ids
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in get_mfd_filled_pack_ids_by_batch: {}".format(e))
        raise e


@log_args
def delete_pack_user_map_by_pack_id(pack_ids: list) -> bool:
    """
    delete pack user map data by pack ids to revert batch from manual fill flow
    @param pack_ids:
    @return:
    """

    try:
        status = PackUserMap.db_delete_data_pack_user_map_by_pack_ids(pack_ids=pack_ids)
        return status

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in delete_pack_user_map_by_pack_id: {}".format(e))
        raise


@log_args
def get_analysis_data_dao(other_packs_of_filled_patient: list, batch_id: int) -> list:
    """
    function to get analysis data (canister used in given pack ids)
    @param batch_id:
    @param other_packs_of_filled_patient:
    @return:
    """
    canister_id_set: set = set()
    try:
        query = PackAnalysis.select(PackAnalysisDetails.canister_id)\
            .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)\
            .where(PackAnalysis.pack_id.in_(other_packs_of_filled_patient),
                   PackAnalysis.batch_id == batch_id)

        for record in query.dicts():
            if record['canister_id']:
                canister_id_set.add(record['canister_id'])
        return list(canister_id_set)

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in get_analysis_data_dao: {}".format(e))
        raise


@log_args
def delete_frequent_mfd_drugs_for_revert_batch(batch_id):
    try:
        if batch_id:
            status = FrequentMfdDrugs.delete().where(FrequentMfdDrugs.batch_id == batch_id).execute()
        else:
            status = FrequentMfdDrugs.delete().where(FrequentMfdDrugs.current_pack_queue == 1,
                                                     FrequentMfdDrugs.batch_id == batch_id).execute()
        logger.info(f"In delete_frequent_mfd_drugs_for_revert_batch, status: {status}")

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in delete_frequent_mfd_drugs_for_revert_batch: {}".format(e))
        raise e

