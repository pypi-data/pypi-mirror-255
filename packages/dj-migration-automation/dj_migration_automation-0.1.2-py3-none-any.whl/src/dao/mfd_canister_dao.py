import functools
import operator
from collections import defaultdict
from itertools import chain

from peewee import (InternalError, IntegrityError, JOIN_LEFT_OUTER, DoesNotExist, DataError, fn, SQL)

import settings
from dosepack.utilities.utils import (log_args_and_response)
from drug_recom_for_big_canister import batch_id
from realtime_db.dp_realtimedb_interface import Database
from src.dao.couch_db_dao import get_couch_db_database_name
from src.model.model_pack_details import PackDetails
from src import constants
from src.api_utility import get_results, get_multi_search, get_orders
from src.service.drug_search import get_ndc_list_for_barcode, get_multi_search_with_drug_scan
from src.dao.mfd_dao import map_pack_location_dao
from src.model.model_action_master import ActionMaster
from src.model.model_code_master import CodeMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_facility_master import FacilityMaster
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_analysis import (MfdAnalysis)
from src.model.model_mfd_analysis_details import (MfdAnalysisDetails)
from src.model.model_mfd_canister_master import (MfdCanisterMaster)
from src.model.model_mfd_canister_status_history import MfdCanisterStatusHistory
from src.model.model_mfd_canister_transfer_history import MfdCanisterTransferHistory
from src.model.model_mfd_cycle_history import MfdCycleHistory
from src.model.model_mfd_history_comment import MfdCycleHistoryComment
from src.model.model_mfd_status_history_comment import MfdStatusHistoryComment
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_master import PatientMaster
from src.model.model_slot_details import SlotDetails
from src.model.model_temp_mfd_filling import TempMfdFilling
from src.model.model_unique_drug import UniqueDrug
from src.model.model_pack_grid import PackGrid
from src.model.model_slot_header import SlotHeader
from src.model.model_patient_rx import PatientRx
from src.model.model_batch_master import BatchMaster

logger = settings.logger

mfd_latest_analysis_sub_query = MfdAnalysis.select(fn.MAX(MfdAnalysis.order_no).alias('max_order_number'),
                                                   MfdAnalysis.mfd_canister_id.alias('mfd_canister_id')) \
    .group_by(MfdAnalysis.mfd_canister_id).alias('sub_query')

mfd_latest_history_sub_query = MfdCycleHistory.select(fn.MAX(MfdCycleHistory.id).alias('max_history_id'),
                                                      MfdCycleHistory.analysis_id.alias('mfd_analysis_id')) \
    .group_by(MfdCycleHistory.analysis_id).alias('history_sub_query')

mfd_latest_state_status_sub_query = MfdCanisterStatusHistory.select(
    fn.MAX(MfdCanisterStatusHistory.id).alias('max_status_history_id'),
    MfdCanisterStatusHistory.mfd_canister_id.alias('mfd_canister_id')) \
    .group_by(MfdCanisterStatusHistory.mfd_canister_id).alias('state_sub_query')


def get_drawer_canister_data_query(batch_id: int, device_id: int, trolley_id: int, drawer_id: int or None = None):
    """
    @param batch_id: int
    @param device_id: int
    @param trolley_id: int
    @param drawer_id: int
    @return: query
    """
    try:
        LocationMasterAlias = LocationMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()

        LocationMasterAlias2 = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        sub_query = MfdCanisterTransferHistory.select(fn.MAX(MfdCanisterTransferHistory.id)
                                                      .alias('max_canister_history_id'),
                                                      MfdCanisterTransferHistory.mfd_canister_id
                                                      .alias('mfd_canister_id')
                                                      ) \
            .group_by(MfdCanisterTransferHistory.mfd_canister_id).alias('sub_query_1')

        query = MfdCanisterMaster.select(MfdAnalysis.mfd_canister_id,
                                         MfdCanisterMaster.rfid,
                                         MfdCanisterMaster.fork_detected,
                                         MfdAnalysis.status_id,
                                         DeviceMaster.id.alias('current_device'),
                                         DeviceMaster.name.alias('current_device_name'),
                                         DeviceMaster.device_type_id,
                                         LocationMasterAlias.display_location.alias('current_display_location'),
                                         MfdAnalysis.trolley_location_id,
                                         MfdAnalysis.trolley_seq,
                                         LocationMasterAlias.id.alias('current_location_id'),
                                         MfdAnalysis.id.alias('mfd_analysis_id'),
                                         LocationMasterAlias.quadrant.alias('current_quadrant'),
                                         LocationMasterAlias.device_id.alias('current_device'),
                                         MfdAnalysis.dest_device_id,
                                         LocationMaster.device_id.alias('source_trolley'),
                                         ContainerMaster.drawer_name.alias('trolley_drawer_name'),
                                         ContainerMasterAlias.drawer_level.alias('current_drawer_level'),
                                         MfdAnalysis.dest_quadrant,
                                         MfdCanisterTransferHistory.created_date.alias('last_seen_time'),
                                         DeviceMasterAlias.name.alias('previous_device_name'),
                                         LocationMasterAlias2.id.alias('previous_location_id'),
                                         LocationMasterAlias2.display_location.alias('previous_display_location'),
                                         MfdCanisterTransferHistory.id.alias('mfd_transfer_history')
                                         ).dicts() \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=mfd_latest_analysis_sub_query.c.max_order_number == MfdAnalysis.order_no) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == MfdCanisterMaster.location_id) \
            .join(ContainerMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.container_id == ContainerMasterAlias.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(sub_query, JOIN_LEFT_OUTER,
                  on=(sub_query.c.mfd_canister_id == MfdCanisterMaster.id)) \
            .join(MfdCanisterTransferHistory, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.id == sub_query.c.max_canister_history_id)) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.previous_location_id == LocationMasterAlias2.id)) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER,
                  on=(LocationMasterAlias2.device_id == DeviceMasterAlias.id)) \
            .where(MfdAnalysis.batch_id == batch_id,
                   MfdCanisterMaster.state_status == constants.MFD_CANISTER_ACTIVE,
                   LocationMaster.device_id == trolley_id,
                   MfdAnalysis.dest_device_id == device_id,
                   MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_PENDING_STATUS,
                                                 constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                                 constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                 constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                 constants.MFD_CANISTER_SKIPPED_STATUS,
                                                 constants.MFD_CANISTER_DROPPED_STATUS
                                                 ])
                   )
        if drawer_id:
            query = query.where(LocationMaster.container_id == drawer_id)

        query = query.order_by(MfdAnalysis.id)
        return query

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_drawer_id_from_serial_number(serial_number: str, company_id: int or None = None):
    """
    todo: move this function to drawer master dao
    @param serial_number: str
    @param company_id: int
    @return: int
    """
    logger.info("In get_drawer_id_from_serial_number")
    try:

        query = ContainerMaster.select(ContainerMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .where(ContainerMaster.serial_number == serial_number,
                   DeviceMaster.company_id == company_id).get()

        return query.id

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise
    except DoesNotExist as e:
        logger.error(e)
        return None


@log_args_and_response
def get_device_id_from_drawer_serial_number(drawer_serial_number: str, company_id: int):
    """
    @param company_id:
    @param drawer_serial_number:
    @return:
    """
    logger.info("In get_device_id_from_drawer_serial_number")
    try:
        # todo change this to a optimum way
        query = DeviceMaster.select(DeviceMaster.id) \
            .join(ContainerMaster, on=ContainerMaster.device_id == DeviceMaster.id) \
            .where(ContainerMaster.serial_number == drawer_serial_number,
                   DeviceMaster.company_id == company_id).get()

        return query.id

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise
    except DoesNotExist as e:
        logger.error(e)
        return None


@log_args_and_response
def get_device_id_from_serial_number(serial_number: str, company_id: int):
    """
    todo: move this function to device master dao
    @param serial_number: str
    @param company_id: int
    @return: int
    """
    logger.info("In get_device_id_from_serial_number")
    try:
        # todo change this to a optimum way
        query = DeviceMaster.select(DeviceMaster.id).where(DeviceMaster.serial_number == serial_number,
                                                           DeviceMaster.company_id == company_id).get()

        return query.id

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise
    except DoesNotExist as e:
        logger.error(e)
        return None


def get_trolley_drawer_query(device_id: int, batch_id: int, trolley_id_list: list):
    """
    Query to get trolley drawer data
    @param device_id:
    @param batch_id:
    @param trolley_id_list:
    @return: query
    """
    # todo check conditions
    try:
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()

        query = MfdCanisterMaster.select(LocationMaster.device_id,
                                         DeviceMaster.name,
                                         fn.GROUP_CONCAT(fn.DISTINCT(MfdCanisterMaster.id)).alias('mfd_canister_ids'),
                                         fn.GROUP_CONCAT(fn.DISTINCT(MfdCanisterMaster.fork_detected)).
                                         alias('group_fork_detected'),
                                         ContainerMaster.serial_number,
                                         DeviceMaster.device_type_id,
                                         ContainerMaster.id.alias('container_id'),
                                         ContainerMaster.drawer_name.alias('drawer_number')).dicts() \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=(LocationMasterAlias.id == MfdCanisterMaster.location_id)) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMasterAlias.device_id) \
            .where(LocationMaster.device_id << trolley_id_list,
                   MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.dest_device_id == device_id,
                   MfdCanisterMaster.state_status == constants.MFD_CANISTER_ACTIVE,
                   (((MfdAnalysis.status_id << [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                constants.MFD_CANISTER_MVS_FILLING_REQUIRED]) &
                     (DeviceMaster.id != LocationMasterAlias.device_id)) |
                    ((MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                    constants.MFD_CANISTER_MVS_FILLING_REQUIRED])) &
                     ((MfdCanisterMaster.fork_detected == 0) |
                      (MfdAnalysis.dest_device_id != LocationMasterAlias.device_id) |
                      (MfdAnalysis.dest_quadrant != LocationMasterAlias.quadrant)))),
                   MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_PENDING_STATUS,
                                                 constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                                 constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                 constants.MFD_CANISTER_SKIPPED_STATUS,
                                                 constants.MFD_CANISTER_DROPPED_STATUS,
                                                 constants.MFD_CANISTER_MVS_FILLED_STATUS
                                                 ])
                   ) \
            .order_by(ContainerMaster.id) \
            .group_by(ContainerMaster.id)

        return query

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_mfd_trolley_drawer_data(trolley_id: int):
    """
    Query to get mfd trolley drawer data
    @param: trolley_id: int
    @return: list
    """
    response = ContainerMaster.get_drawer_data_for_device(trolley_id)
    return response


@log_args_and_response
def get_device_mfd_trolley_data(device_id: int, batch_id: int):
    """
    Returns next trolley's data for given robot
    @param device_id:
    @param batch_id:
    @return: query
    """
    # todo add condition to check trolley is filled or not
    try:
        analysis_id_list = list()
        # LocationMasterAlias = LocationMaster.alias()
        # DeviceMasterAlias = DeviceMaster.alias()
        next_trolley, system_id, next_trolley_name, next_trolley_seq = db_get_next_trolley(batch_id, device_id)
        if next_trolley:
            analysis_id_list, mfs_system_mapping, dest_devices, batch_system = get_trolley_analysis_ids(batch_id,
                                                                                                        next_trolley)
        if analysis_id_list:
            query = MfdAnalysis.select(DeviceMaster.serial_number,
                                       DeviceMaster.name,
                                       DeviceMaster.device_type_id,
                                       LocationMaster.device_id.alias('trolley_id')).dicts() \
                .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
                .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
                .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
                .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
                .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
                .where(MfdAnalysis.id.in_(analysis_id_list),
                       MfdAnalysis.status_id << [constants.MFD_CANISTER_PENDING_STATUS,
                                                 constants.MFD_CANISTER_IN_PROGRESS_STATUS
                                                 ]) \
                .group_by(LocationMaster.device_id) \
                .order_by(MfdAnalysis.order_no)

            return query, next_trolley_name, next_trolley
        else:
            return {}, next_trolley_name, next_trolley

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def duplicate_rfid_check(rfid: str, input_args: dict) -> tuple:
    """
    Function to check if mfd canister with input rfid is already registered or not
    @param rfid: string
    @param input_args: dict
    @return: True/False, response
    """
    logger.info(rfid, input_args)
    response = dict()
    try:  # check for duplicate rfid
        response = MfdCanisterMaster.select().where(MfdCanisterMaster.rfid == rfid).dicts().get()
        logger.error('Duplicate rfid {} found while adding canister for canister data {}'
                     .format(rfid, input_args))
        return True, response

    except DoesNotExist as e:
        logger.error(e)
        return False, response

    except (InternalError, IntegrityError) as e:
        logger.error(e)
        raise


def get_mfd_canister_home_cart_count(company_id: int):
    """
    Function to get home_cart wise count for registered mfd canisters
    @param company_id:
    @return: query
    """
    try:
        query = MfdCanisterMaster.select(MfdCanisterMaster.home_cart_id,
                                         DeviceMaster.name.alias('home_cart_name'),
                                         fn.COUNT(fn.DISTINCT(MfdCanisterMaster.id)).alias(
                                             'mfd_canister_count')).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == MfdCanisterMaster.home_cart_id) \
            .where(MfdCanisterMaster.company_id == company_id) \
            .group_by(MfdCanisterMaster.home_cart_id)
        return query
    except DataError as e:
        raise DataError(e)
    except IntegrityError as e:
        raise InternalError(e)
    except InternalError as e:
        raise InternalError(e)
    except DoesNotExist as e:
        raise DoesNotExist(e)


def add_data_in_mfd_canister_master(data_dict: dict) -> object:
    """
    Method to add record in mfd canister master
    @data_dict = dict of data to be inserted
    @return: created_record
    """
    try:
        record = MfdCanisterMaster.db_create_record(data_dict, MfdCanisterMaster, get_or_create=False)
        logger.info("Added record {} in mfd canister master".format(record))
        return record.id
    except DataError as e:
        raise DataError(e)
    except IntegrityError as e:
        raise InternalError(e)
    except InternalError as e:
        raise InternalError(e)


def get_mfd_canister_from_pack(multi_search_string: list, left_search=False) -> list:
    """
    Method to return mfd canisters of particular pack
    @data_dict = dict of data to be inserted
    @return: created_record
    """
    mfd_canister_ids = list()
    try:
        clauses = list()
        global_search = [PackDetails.pack_display_id]
        clauses = get_multi_search(clauses, multi_search_string, global_search, left_like_search=left_search)
        # data = str(pack_id).translate(str.maketrans({'%': r'\%'}))  # escape % from search string
        # search_data = data + "%"
        # clauses.append(fn.CONCAT('', fields_dict[k]) ** search_data)
        query = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id')) \
            .join(mfd_latest_analysis_sub_query, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER,
                  on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, JOIN_LEFT_OUTER, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, JOIN_LEFT_OUTER, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, JOIN_LEFT_OUTER, on=PackDetails.id == PackRxLink.pack_id) \
            .where(*clauses)
        query = query.group_by(MfdCanisterMaster.id)
        for record in query.dicts():
            mfd_canister_ids.append(record['mfd_canister_id'])
        return mfd_canister_ids
    except DataError as e:
        raise DataError(e)
    except IntegrityError as e:
        raise InternalError(e)
    except InternalError as e:
        raise InternalError(e)


@log_args_and_response
def get_mfd_canisters_query(filter_fields: dict, sort_fields, clauses, paginate, exact_search_list, like_search_list,
                            membership_search_list=None,
                            left_like_search_list=None):
    """
    @param filter_fields:
    @param sort_fields:
    @param clauses:
    @param paginate:
    @param exact_search_list:
    @param like_search_list:
    @param membership_search_list:
    @param left_like_search_list:
    @return:
    """

    try:
        DeviceMasterAlias = DeviceMaster.alias()
        DeviceMasterAlias2 = DeviceMaster.alias()
        DeviceMasterAlias3 = DeviceMaster.alias()
        LocationMasterAlias2 = LocationMaster.alias()
        ContainerMasterAlias2 = ContainerMaster.alias()

        fields_dict = {"mfd_canister_id": MfdCanisterMaster.id,
                       "source_drawer_name": ContainerMaster.drawer_name,
                       "home_cart_id": MfdCanisterMaster.home_cart_id,
                       "home_cart_name": DeviceMasterAlias3.name,
                       "state_status": MfdCanisterMaster.state_status,
                       "source_device_name": DeviceMaster.name,
                       "source_display_location": fn.IF(DeviceMaster.device_type_id ==
                                                        settings.DEVICE_TYPES['Manual Canister Cart'], None,
                                                        LocationMaster.display_location),
                       "status": fn.IF(MfdAnalysis.status_id.is_null(False),
                                       fn.IF(MfdAnalysis.status_id.in_([constants.MFD_CANISTER_SKIPPED_STATUS,
                                                                        constants.MFD_CANISTER_DROPPED_STATUS,
                                                                        constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                                        constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                                        constants.MFD_CANISTER_PENDING_STATUS]),
                                             constants.MFD_CANISTER_PENDING_STATUS,
                                             fn.IF(MfdAnalysis.status_id.in_([constants.MFD_CANISTER_FILLED_STATUS,
                                                                              constants.MFD_CANISTER_VERIFIED_STATUS]),
                                                   constants.MFD_CANISTER_FILLED_STATUS, MfdAnalysis.status_id)),
                                       constants.MFD_CANISTER_PENDING_STATUS),
                       "status_id": MfdAnalysis.status_id,
                       "last_used_by": MfdAnalysis.assigned_to,
                       "pack_display_id": PackDetails.pack_display_id,
                       "dest_device_name": fn.IF(MfdAnalysis.id.is_null(False),
                                                 fn.IF(MfdAnalysis.status_id << [
                                                     constants.MFD_CANISTER_IN_PROGRESS_STATUS],
                                                       DeviceMasterAlias2.name,
                                                       fn.IF(MfdAnalysis.status_id << [
                                                           constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                           constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                           constants.MFD_CANISTER_SKIPPED_STATUS,
                                                           constants.MFD_CANISTER_DROPPED_STATUS,
                                                           constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                           constants.MFD_CANISTER_MVS_FILLING_REQUIRED, ],
                                                             fn.IF(DeviceMaster.device_type_id << [
                                                                 settings.DEVICE_TYPES['Manual Filling Device'],
                                                                 settings.DEVICE_TYPES['ROBOT']],
                                                                   DeviceMasterAlias2.name,
                                                                   None),
                                                             fn.IF(MfdAnalysis.status_id << [
                                                                 constants.MFD_CANISTER_FILLED_STATUS,
                                                                 constants.MFD_CANISTER_VERIFIED_STATUS],
                                                                   fn.IF(DeviceMaster.device_type_id << [
                                                                       settings.DEVICE_TYPES['Manual Filling Device'],
                                                                       settings.DEVICE_TYPES['ROBOT']],
                                                                         DeviceMasterAlias2.name,
                                                                         DeviceMasterAlias.name),
                                                                   None
                                                                   ),
                                                             )), None
                                                 ),
                       "dest_device_type": fn.IF(MfdAnalysis.id.is_null(False),
                                                 fn.IF(MfdAnalysis.status_id << [
                                                     constants.MFD_CANISTER_IN_PROGRESS_STATUS],
                                                       DeviceMasterAlias2.device_type_id,
                                                       fn.IF(MfdAnalysis.status_id << [
                                                           constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                           constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                           constants.MFD_CANISTER_SKIPPED_STATUS,
                                                           constants.MFD_CANISTER_DROPPED_STATUS,
                                                           constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                           constants.MFD_CANISTER_MVS_FILLING_REQUIRED, ],
                                                             fn.IF(DeviceMaster.device_type_id << [
                                                                 settings.DEVICE_TYPES['Manual Filling Device'],
                                                                 settings.DEVICE_TYPES['ROBOT']],
                                                                   DeviceMasterAlias2.device_type_id,
                                                                   None),
                                                             fn.IF(MfdAnalysis.status_id << [
                                                                 constants.MFD_CANISTER_FILLED_STATUS,
                                                                 constants.MFD_CANISTER_VERIFIED_STATUS],
                                                                   fn.IF(DeviceMaster.device_type_id << [
                                                                       settings.DEVICE_TYPES['Manual Filling Device'],
                                                                       settings.DEVICE_TYPES['ROBOT']],
                                                                         DeviceMasterAlias2.device_type_id,
                                                                         DeviceMasterAlias.device_type_id),
                                                                   None
                                                                   ),
                                                             )), None
                                                 ),
                       "dest_drawer_name": fn.IF(MfdAnalysis.id.is_null(False),
                                                 fn.IF(DeviceMaster.device_type_id ==
                                                       settings.DEVICE_TYPES['Manual Filling Device'],
                                                       fn.IF(MfdAnalysis.status_id << [
                                                           constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                           constants.MFD_CANISTER_FILLED_STATUS,
                                                           constants.MFD_CANISTER_VERIFIED_STATUS,
                                                           constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                                                           constants.MFD_CANISTER_MVS_FILLING_REQUIRED, ],
                                                             ContainerMasterAlias2.drawer_name, None), None), None),

                       "dest_quadrant": fn.IF(MfdAnalysis.id.is_null(False),
                                              fn.IF(DeviceMaster.device_type_id ==
                                                    settings.DEVICE_TYPES['Manual Canister Cart'],
                                                    fn.IF(
                                                        MfdAnalysis.status_id << [constants.MFD_CANISTER_FILLED_STATUS,
                                                                                  constants.MFD_CANISTER_VERIFIED_STATUS],
                                                        MfdAnalysis.dest_quadrant, None),
                                                    fn.IF(DeviceMaster.device_type_id.is_null(True),
                                                          fn.IF(MfdAnalysis.status_id << [
                                                              constants.MFD_CANISTER_FILLED_STATUS,
                                                              constants.MFD_CANISTER_VERIFIED_STATUS],
                                                                MfdAnalysis.dest_quadrant, None), None)), None),
                       "location_id": MfdCanisterMaster.location_id,
                       "patient_name": PatientMaster.concated_patient_name_field(),
                       "facility_name": FacilityMaster.facility_name,
                       "drug_name": DrugMaster.concated_drug_name_field(),
                       "ndc": DrugMaster.formatted_ndc
                       }

        query = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id'),
                                         MfdCanisterMaster.rfid,
                                         MfdCanisterMaster.state_status,
                                         MfdCanisterMaster.erp_product_id,
                                         MfdCanisterMaster.label_print_time,
                                         MfdCanisterMaster.state_status.alias('mfd_can_state_status'),
                                         MfdCanisterMaster.location_id.alias("source_location_id"),
                                         MfdCanisterMaster.home_cart_id.alias("home_cart_id"),
                                         DeviceMasterAlias3.name.alias("home_cart_name"),
                                         fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.pack_display_id)).alias(
                                             'pack_display_id'),
                                         fn.GROUP_CONCAT(fn.DISTINCT(PackDetails.id)).alias('pack_id'),
                                         LocationMaster.device_id.alias('source_device_id'),
                                         DeviceMaster.name.alias('source_device_name'),
                                         DeviceMaster.device_type_id.alias('source_device_type'),
                                         DeviceMaster.ip_address.alias('source_device_ip_address'),
                                         ContainerMaster.shelf.alias('source_shelf'),
                                         ContainerMaster.ip_address.alias('source_ip_address'),
                                         ContainerMaster.secondary_ip_address.alias('source_secondary_ip_address'),
                                         ContainerMaster.mac_address.alias('source_mac_address'),
                                         ContainerMaster.serial_number.alias('source_serial_number'),
                                         ContainerMaster.drawer_name.alias('source_drawer_name'),
                                         fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisDetails.status_id)).alias(
                                             'drug_status'),
                                         fn.IF(DeviceMaster.device_type_id ==
                                               settings.DEVICE_TYPES['Manual Canister Cart'], None,
                                               LocationMaster.display_location).alias('source_display_location'),
                                         fields_dict['dest_device_name'].alias('dest_device_name'),
                                         fields_dict['dest_device_type'].alias('dest_device_type'),
                                         DeviceMaster.system_id,
                                         fields_dict['dest_drawer_name'].alias('dest_drawer_name'),
                                         fields_dict['status'].alias('canister_status'),
                                         MfdAnalysis.status_id,
                                         CodeMaster.value.alias('status'),
                                         MfdAnalysis.id.alias('mfd_analysis_id'),
                                         MfdAnalysis.assigned_to.alias('last_used_by'),
                                         fields_dict['dest_quadrant'].alias('dest_quadrant'),
                                         fields_dict['patient_name'].alias('patient_name'),
                                         fields_dict['facility_name'].alias('facility_name'),
                                         fn.IF(MfdAnalysis.status_id == constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                               fn.IF(DeviceMaster.device_type_id ==
                                                     settings.DEVICE_TYPES["Manual Canister Cart"],
                                                     True, fn.IF(LocationMaster.id.is_null(True),
                                                                 True, False)), False).alias('rts_allowed'),
                                         MfdAnalysis.assigned_to,
                                         ActionMaster.value.alias('reason_to_return'),
                                         MfdCycleHistory.action_id,
                                         MfdCycleHistoryComment.comment,
                                         ) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(mfd_latest_analysis_sub_query, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER,
                  on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, JOIN_LEFT_OUTER, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, JOIN_LEFT_OUTER, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, JOIN_LEFT_OUTER, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PatientRx, JOIN_LEFT_OUTER, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, JOIN_LEFT_OUTER, on=PatientMaster.id == PatientRx.patient_id) \
            .join(DrugMaster, JOIN_LEFT_OUTER, on=((DrugMaster.id == SlotDetails.drug_id) &
                                                   (MfdAnalysisDetails.status_id << [constants.MFD_DRUG_FILLED_STATUS,
                                                                                     constants.MFD_DRUG_RTS_REQUIRED_STATUS]))) \
            .join(FacilityMaster, JOIN_LEFT_OUTER, on=PatientMaster.facility_id == FacilityMaster.id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=MfdAnalysis.dest_device_id == DeviceMasterAlias.id) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER, on=LocationMasterAlias2.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMasterAlias2, JOIN_LEFT_OUTER, on=LocationMasterAlias2.device_id == DeviceMasterAlias2.id) \
            .join(ContainerMasterAlias2, JOIN_LEFT_OUTER,
                  on=ContainerMasterAlias2.id == LocationMasterAlias2.container_id) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == MfdAnalysis.status_id) \
            .join(DeviceMasterAlias3, JOIN_LEFT_OUTER, on=MfdCanisterMaster.home_cart_id == DeviceMasterAlias3.id) \
            .join(mfd_latest_history_sub_query, JOIN_LEFT_OUTER,
                  on=MfdAnalysis.id == mfd_latest_history_sub_query.c.mfd_analysis_id) \
            .join(MfdCycleHistory, JOIN_LEFT_OUTER,
                  on=MfdCycleHistory.id == mfd_latest_history_sub_query.c.max_history_id) \
            .join(ActionMaster, JOIN_LEFT_OUTER, on=MfdCycleHistory.action_id == ActionMaster.id) \
            .join(MfdCycleHistoryComment, JOIN_LEFT_OUTER,
                  on=MfdCycleHistory.id == MfdCycleHistoryComment.cycle_history_id) \
            .group_by(MfdCanisterMaster.id)

        results, count = get_results(query.dicts(), fields_dict, filter_fields=filter_fields,
                                     clauses=clauses,
                                     sort_fields=sort_fields,
                                     paginate=paginate,
                                     exact_search_list=exact_search_list,
                                     like_search_list=like_search_list,
                                     left_like_search_fields=left_like_search_list,
                                     membership_search_list=membership_search_list,
                                     last_order_field=[SQL('FIELD(canister_status, {}, {}, {}, {}, {})'.
                                                           format(constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                                  constants.MFD_CANISTER_PENDING_STATUS,
                                                                  constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                                  constants.MFD_CANISTER_FILLED_STATUS,
                                                                  constants.MFD_CANISTER_IN_PROGRESS_STATUS)),
                                                       SQL('FIELD(mfd_can_state_status, {}, {}, {})'.
                                                           format(constants.MFD_CANISTER_ACTIVE,
                                                                  constants.MFD_CANISTER_MISPLACED,
                                                                  constants.MFD_CANISTER_INACTIVE)),
                                                       MfdCanisterMaster.id]
                                     )

        return results, count

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return None

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_canister_data_by_rfid(rfid: str):
    """
    returns canister data by rfid
    :param rfid: str
    :return: dict
    """
    try:
        LocationMasterAlias2 = LocationMaster.alias()
        LocationMasterAlias3 = LocationMaster.alias()
        DeviceMasterAlias2 = DeviceMaster.alias()
        DeviceMasterAlias3 = DeviceMaster.alias()
        response = MfdCanisterMaster.select(MfdCanisterMaster,
                                            ContainerMaster.drawer_name.alias('trolley_drawer_name'),
                                            MfdAnalysis.status_id,
                                            MfdAnalysis.dest_device_id,
                                            TempMfdFilling.id.alias('temp_filling_id'),
                                            LocationMasterAlias2.display_location.alias('mfs_display_location'),
                                            DeviceMaster.name.alias('trolley_name'),
                                            DeviceMaster.id.alias('trolley_id'),
                                            TempMfdFilling.transfer_done,
                                            TempMfdFilling.id.alias('is_currently_in_progress'),
                                            DeviceMasterAlias3.device_type_id.alias('current_device_type_id'),
                                            LocationMasterAlias3.location_number.alias('current_loc_number'),
                                            DeviceMasterAlias3.serial_number.alias('current_serial_number'),
                                            TempMfdFilling.transfer_done,
                                            MfdAnalysis.batch_id,
                                            BatchMaster.system_id).dicts() \
            .join(mfd_latest_analysis_sub_query, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER,
                  on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdAnalysis.trolley_location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id) \
            .join(TempMfdFilling, JOIN_LEFT_OUTER, on=TempMfdFilling.mfd_analysis_id == MfdAnalysis.id) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER,
                  on=((MfdAnalysis.mfs_device_id == LocationMasterAlias2.device_id) &
                      (MfdAnalysis.mfs_location_number == LocationMasterAlias2.location_number))) \
            .join(DeviceMasterAlias2, JOIN_LEFT_OUTER, on=DeviceMasterAlias2.id == LocationMasterAlias2.device_id) \
            .join(LocationMasterAlias3, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMasterAlias3.id) \
            .join(DeviceMasterAlias3, JOIN_LEFT_OUTER, on=DeviceMasterAlias3.id == LocationMasterAlias3.device_id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .where(MfdCanisterMaster.rfid == rfid).get()
        return response
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return None

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_canister_data_by_location_id(location_id: int):
    """
    returns canister present at given location
    :param location_id: int
    :return: dict
    """
    LocationMasterAlias2 = LocationMaster.alias()
    DeviceMasterAlias2 = DeviceMaster.alias()
    MfdCanisterMasterAlias = MfdCanisterMaster.alias()
    try:
        logger.info("LocationId {}".format(location_id))
        response = MfdCanisterMaster.select(MfdCanisterMaster,
                                            MfdAnalysis.id.alias('mfd_analysis_id'),
                                            MfdAnalysis.transferred_location_id,
                                            MfdAnalysis.trolley_location_id,
                                            MfdAnalysis.dest_device_id,
                                            ContainerMaster.id.alias('source_drawer_id'),
                                            TempMfdFilling.id.alias('temp_filling_id'),
                                            LocationMasterAlias2.display_location.alias('mfs_display_location'),
                                            DeviceMaster.name.alias('trolley_name'),
                                            DeviceMaster.id.alias('trolley_id'),
                                            TempMfdFilling.transfer_done,
                                            TempMfdFilling.id.alias('is_currently_in_progress'),
                                            TempMfdFilling.transfer_done,
                                            MfdAnalysis.status_id,
                                            MfdAnalysis.batch_id,
                                            fn.IF(MfdCanisterMasterAlias.id.is_null(True), True, False).alias(
                                                'is_loc_empty'),
                                            BatchMaster.system_id).dicts() \
            .join(mfd_latest_analysis_sub_query, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER,
                  on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdAnalysis.trolley_location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id) \
            .join(TempMfdFilling, JOIN_LEFT_OUTER, on=TempMfdFilling.mfd_analysis_id == MfdAnalysis.id) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER,
                  on=((MfdAnalysis.mfs_device_id == LocationMasterAlias2.device_id) &
                      (MfdAnalysis.mfs_location_number == LocationMasterAlias2.location_number))) \
            .join(DeviceMasterAlias2, JOIN_LEFT_OUTER, on=DeviceMasterAlias2.id == LocationMasterAlias2.device_id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(MfdCanisterMasterAlias, JOIN_LEFT_OUTER,
                  on=MfdCanisterMasterAlias.location_id == MfdAnalysis.trolley_location_id) \
            .where(MfdCanisterMaster.location_id == location_id).get()

        return response

    except DoesNotExist as e:
        logger.error(e)
        return {}
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


def get_mfd_canister_data_query(company_id: int, mfd_canister_id: int, mfd_canister_status: int or None = None,
                                pack_id: int or None = None, mvs_filling: bool = False):
    """
    Query to get mfd canister location and drug data
    @param company_id:  check its use
    @param mfd_canister_id: int
    @param mfd_canister_status:
    @param pack_id:
    @param mvs_filling:
    @return: query

    """
    mfd_canister_info = dict()
    pack_slot_data = defaultdict(set)
    CodeMasterAlias = CodeMaster.alias()
    try:
        query = MfdCanisterMaster.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                         MfdAnalysis.mfs_location_number,
                                         DrugMaster.concated_drug_name_field(include_ndc=True).alias("drug_name"),
                                         DrugMaster.ndc,
                                         DrugMaster.formatted_ndc,
                                         DrugMaster.strength,
                                         DrugMaster.strength_value,
                                         DrugMaster.manufacturer,
                                         DrugMaster.txr,
                                         DrugMaster.imprint,
                                         DrugMaster.color,
                                         DrugMaster.shape,
                                         DrugMaster.image_name,
                                         fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                               DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                         fn.IF(DrugStockHistory.created_by.is_null(True), None,
                                               DrugStockHistory.created_by).alias('stock_updated_by'),
                                         PatientRx.sig,
                                         SlotHeader.hoa_date,
                                         SlotHeader.hoa_time,
                                         PackGrid.slot_column,
                                         PackGrid.slot_row,
                                         MfdAnalysisDetails.quantity,
                                         PatientMaster.id.alias('patient_id'),
                                         PatientMaster.concated_patient_name_field().alias('patient_name'),
                                         MfdAnalysisDetails.mfd_can_slot_no,
                                         CodeMasterAlias.value.alias('drug_status'),
                                         PackDetails.id.alias('pack_id'),
                                         PackDetails.pack_display_id,
                                         MfdAnalysis,
                                         LocationMaster.container_id,
                                         LocationMaster.display_location,
                                         LocationMaster.device_id,
                                         LocationMaster.is_disabled,
                                         LocationMaster.quadrant,
                                         ContainerMaster.drawer_name,
                                         ContainerMaster.drawer_level,
                                         ContainerMaster.drawer_type,
                                         ContainerMaster.drawer_usage,
                                         ContainerMaster.serial_number,
                                         ContainerMaster.ip_address,
                                         ContainerMaster.secondary_ip_address,
                                         ContainerMaster.mac_address,
                                         ContainerMaster.secondary_mac_address,
                                         ContainerMaster.shelf,
                                         DeviceMaster.ip_address.alias('device_ip_address'),
                                         DeviceMaster.serial_number.alias('device_serial_number'),
                                         fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                               DrugDetails.last_seen_by).alias('last_seen_with'),
                                         fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                                               DrugDetails.last_seen_date).alias('last_seen_on')).dicts() \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, on=PatientRx.patient_id == PatientMaster.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(CodeMaster, on=MfdAnalysis.status_id == CodeMaster.id) \
            .join(CodeMasterAlias, on=MfdAnalysisDetails.status_id == CodeMasterAlias.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                   (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == 1) &
                                                         (DrugStockHistory.company_id == PackDetails.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id))) \
            .where(MfdAnalysis.mfd_canister_id == mfd_canister_id,
                   MfdCanisterMaster.company_id == company_id)
        if mvs_filling:
            query = query.where(MfdAnalysisDetails.status_id == constants.MFD_DRUG_FILLED_STATUS)
        if mfd_canister_status:
            query = query.where(MfdAnalysis.status_id == mfd_canister_status)
        else:
            query = query.where(MfdAnalysis.status_id << [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                          constants.MFD_CANISTER_FILLED_STATUS,
                                                          constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                          constants.MFD_CANISTER_VERIFIED_STATUS])

        for record in query:
            mfd_can_slot_no = str(record['mfd_can_slot_no'])
            if mfd_can_slot_no not in mfd_canister_info.keys():
                mfd_canister_info[mfd_can_slot_no] = list()
            location = map_pack_location_dao(slot_row=record['slot_row'], slot_column=record['slot_column'])
            if pack_id and record['pack_id'] == int(pack_id):
                pack_slot_data[location].add(record['mfd_can_slot_no'])
            record['pack_location'] = location
            mfd_canister_info[mfd_can_slot_no].append(record)
        return mfd_canister_info, pack_slot_data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def update_mfd_canister_location(canister_location_dict: dict) -> int:
    """
    updates current location of canister
    :param canister_location_dict: dict
    :return: int
    """
    canister_ids = list(canister_location_dict.keys())
    location_ids = list(canister_location_dict.values())

    try:
        status = MfdCanisterMaster.db_update_canister_id(canister_ids, location_ids)
        return status
    except (InternalError, IntegrityError) as e:
        raise e


def get_mfd_canister_data_by_id(canister_id: int, raise_exc=True):
    """
    returns mfd canister data from id
    :param canister_id:
    :param raise_exc:
    :return:
    """
    try:
        return MfdCanisterMaster.db_get_by_id(canister_id=canister_id)
    except DoesNotExist:
        if raise_exc:
            raise
        return None
    except (DoesNotExist, InternalError):
        raise


def get_mfd_canister_home_cart_name(device_id: int):
    """
    returns device info
    :param device_id:
    :return:
    """
    try:
        return DeviceMaster.db_get_by_id(device_id)
    except (DoesNotExist, InternalError):
        raise


def update_mfd_canister(update_dict: dict, **kwargs):
    """
    updates mfd_canister_master's data
    :param update_dict:
    :param kwargs:
    :return:
    """
    try:
        return MfdCanisterMaster.db_update(update_dict=update_dict, **kwargs)
    except (InternalError, IntegrityError):
        raise


def get_mfd_canister_data(mfd_analysis_id: int, sort_fields: list, drug_status: list or None = None):
    """
    Query to get drug data of a particular mfd canister
    @param sort_fields:
    @param drug_status:
    @param mfd_analysis_id:
    @return: query
    """
    try:
        fields_dict = {"drug_full_name": DrugMaster.concated_drug_name_field(),
                       "quantity": fn.SUM(MfdAnalysisDetails.quantity),
                       "ndc": DrugMaster.ndc
                       }

        order_list = []
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdAnalysis.mfs_location_number,
                                   DrugMaster,
                                   DrugMaster.concated_drug_name_field().alias('drug_full_name'),
                                   fn.SUM(MfdAnalysisDetails.quantity).alias('quantity'),
                                   PatientMaster.concated_patient_name_field().alias('patient_name'),
                                   DrugDetails.last_seen_by,
                                   DrugDetails.last_seen_date,
                                   DrugStockHistory.is_in_stock,
                                   ).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(PatientMaster, on=PatientRx.patient_id == PatientMaster.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(CodeMaster, on=MfdAnalysis.status_id == CodeMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                   (UniqueDrug.txr == DrugMaster.txr))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == PackDetails.company_id))) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == settings.is_drug_active) &
                                                         (DrugStockHistory.company_id == PackDetails.company_id))) \
            .where(MfdAnalysis.id == mfd_analysis_id)
        if drug_status:
            query = query.where(MfdAnalysisDetails.status_id << drug_status)

        query = query.group_by(DrugMaster.formatted_ndc, DrugMaster.txr)

        order_list = get_orders(order_list, fields_dict, sort_fields)
        if order_list:
            query = query.order_by(*order_list)

        drug_data = dict()
        for record in query:
            drug_data['{}#{}'.format(record['formatted_ndc'], record['txr'])] = record
        return drug_data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_mfd_analysis_details_ids(mfd_analysis_id: int, company_id: int, drug_status: int,
                                    pack_id: int or None = None):
    """
    to return particular MFD data for mfd_analysis_id
    @param mfd_analysis_id:
    @param company_id:
    @param drug_status:
    :return: list
    @param pack_id:
    """
    try:
        mfd_analysis_details_ids = set()
        pack_mfd_analysis_details_ids = set()
        home_cart_id = None
        mfd_canister_id = None
        mfd_canister_state_status = None
        home_cart_device_name = None
        dest_container = None
        pack_status_list = set()
        DeviceMasterAlias = DeviceMaster.alias()

        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   MfdCanisterMaster.home_cart_id,
                                   MfdCanisterMaster.state_status,
                                   MfdCanisterMaster.id.alias('mfd_canister_id'),
                                   MfdAnalysisDetails.id.alias('mfd_analysis_details_id'),
                                   PackRxLink.pack_id,
                                   DeviceMaster.device_type_id,
                                   ContainerMaster.drawer_name,
                                   PackDetails.pack_status,
                                   DeviceMasterAlias.name.alias('home_cart_device_name'),
                                   MfdAnalysisDetails.status_id.alias('mfd_drug_status')).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(MfdCanisterMaster, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == MfdCanisterMaster.home_cart_id) \
            .where(MfdAnalysis.id == mfd_analysis_id,
                   MfdAnalysisDetails.status_id == drug_status,
                   MfdCanisterMaster.company_id == company_id)

        for record in query:
            mfd_analysis_details_ids.add(record['mfd_analysis_details_id'])
            pack_status_list.add(record['pack_status'])
            if pack_id and record['pack_id'] == int(pack_id):
                pack_mfd_analysis_details_ids.add(record['mfd_analysis_details_id'])
            home_cart_id = record['home_cart_id']
            mfd_canister_id = record['mfd_canister_id']
            mfd_canister_state_status = record['state_status']
            home_cart_device_name = record['home_cart_device_name']
            if record['device_type_id'] == settings.DEVICE_TYPES['Manual Canister Cart']:
                dest_container = record['drawer_name']

        different_slots = mfd_analysis_details_ids.difference(pack_mfd_analysis_details_ids)
        canister_done = True
        if different_slots:
            canister_done = False
        return list(mfd_analysis_details_ids), home_cart_id, mfd_canister_id, list(pack_mfd_analysis_details_ids), \
               canister_done, mfd_canister_state_status, dest_container, list(pack_status_list), home_cart_device_name
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_mfd_canister_master_filters(company_id: int) -> tuple:
    """
    Function to get filter data query for mfd canister master screen
    @param company_id: int
    @return: query
    """
    logger.info("In get_mfd_canister_master_filters")
    try:
        DeviceMasterAlias = DeviceMaster.alias()
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias2 = DeviceMaster.alias()
        # query to fetch the source device
        source_device_name_query = MfdCanisterMaster.select(
            fn.DISTINCT(DeviceMaster.name).alias('source_device_name')).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(MfdCanisterMaster.company_id == company_id,
                   MfdCanisterMaster.rfid.is_null(False),
                   DeviceMaster.name.is_null(False)).order_by(DeviceMaster.id)
        # query to fetch the home_carts for the filters
        home_cart_query = MfdCanisterMaster.select(fn.DISTINCT(DeviceMaster.name).alias("home_cart_name")).dicts() \
            .join(DeviceMaster, on=MfdCanisterMaster.home_cart_id == DeviceMaster.id) \
            .where(MfdCanisterMaster.company_id == company_id,
                   MfdCanisterMaster.rfid.is_null(False),
                   DeviceMaster.name.is_null(False)).order_by(DeviceMaster.id)

        # query to fetch the destination device for the filters
        dest_device_query = MfdAnalysis.select(fn.MAX(MfdAnalysis.order_no),
                                               MfdAnalysis.mfd_canister_id,
                                               MfdAnalysis.status_id,
                                               MfdAnalysis.dest_device_id,
                                               MfdAnalysis.trolley_location_id,
                                               DeviceMaster.device_type_id,
                                               DeviceMaster.name,
                                               DeviceMasterAlias.name.alias("analysis_device_name"),
                                               DeviceMasterAlias2.name.alias("trolley_name")).dicts() \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == MfdAnalysis.dest_device_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMasterAlias2, JOIN_LEFT_OUTER, on=DeviceMasterAlias2.id == LocationMasterAlias.device_id) \
            .where(MfdCanisterMaster.company_id == company_id,
                   MfdCanisterMaster.rfid.is_null(False)) \
            .group_by(MfdAnalysis.mfd_canister_id)

        query = MfdCanisterMaster.select(
            fn.GROUP_CONCAT(fn.DISTINCT(
                fn.IF(MfdAnalysis.status_id.is_null(False),
                      fn.IF(MfdAnalysis.status_id.in_(
                          [constants.MFD_CANISTER_SKIPPED_STATUS,
                           constants.MFD_CANISTER_DROPPED_STATUS,
                           constants.MFD_CANISTER_RTS_DONE_STATUS,
                           constants.MFD_CANISTER_MVS_FILLED_STATUS,
                           constants.MFD_CANISTER_PENDING_STATUS]),
                          constants.MFD_CANISTER_PENDING_STATUS,
                          fn.IF(MfdAnalysis.status_id.in_(
                              [constants.MFD_CANISTER_FILLED_STATUS,
                               constants.MFD_CANISTER_VERIFIED_STATUS]),
                              constants.MFD_CANISTER_FILLED_STATUS, MfdAnalysis.status_id)),
                      constants.MFD_CANISTER_PENDING_STATUS))).alias('status'),
            fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.assigned_to)).alias('last_used_by')).dicts() \
            .join(mfd_latest_analysis_sub_query, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER,
                  on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == MfdAnalysis.status_id) \
            .where(MfdCanisterMaster.company_id == company_id,
                   MfdCanisterMaster.rfid.is_null(False)) \
            .group_by(MfdCanisterMaster.company_id)

        state_status_query = MfdCanisterMaster.select(
            fn.DISTINCT(MfdCanisterMaster.state_status).alias("state_status")).dicts() \
            .where(MfdCanisterMaster.company_id == company_id,
                   MfdCanisterMaster.rfid.is_null(False)).order_by(MfdCanisterMaster.state_status)

        return query, source_device_name_query, home_cart_query, dest_device_query, state_status_query

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise e


def get_unique_rts_filters(company_id: int) -> tuple:
    """
    To get unique source device ids and state_status
    :param company_id: int
    :return: list
    """
    source_device_ids = dict()
    source_devices = list()
    state_status = list()
    device_names = list()
    try:
        query = MfdCanisterMaster.select(fn.GROUP_CONCAT(fn.DISTINCT(DeviceMaster.name)).alias('source_device_name'),
                                         fn.GROUP_CONCAT(fn.DISTINCT(MfdCanisterMaster.state_status)).coerce(
                                             False).alias('can_state_status'),
                                         fn.GROUP_CONCAT(fn.DISTINCT(DeviceMaster.id)).alias('source_device_id')
                                         ).dicts() \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(MfdAnalysisDetails, on=((MfdAnalysisDetails.analysis_id == MfdAnalysis.id) &
                                          (MfdAnalysisDetails.status_id == constants.MFD_DRUG_RTS_REQUIRED_STATUS))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .where(MfdCanisterMaster.company_id == company_id,
                   MfdCanisterMaster.rfid.is_null(False)) \
            .group_by(MfdCanisterMaster.company_id)
        for record in query:
            if record['source_device_id']:
                source_devices = record['source_device_id'].split(',')
            if record['source_device_name']:
                device_names = record['source_device_name'].split(',')
            if record['can_state_status']:
                state_status = str(record['can_state_status']).split(',')
        while source_devices:
            source_device_ids[source_devices.pop(0)] = device_names.pop(0)
        return source_device_ids, state_status
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_empty_drawers_for_locations_dao(device_id: int, no_of_locations_required: int, quadrant: int = None) -> dict:
    """
    Method to fetch unique empty drawers based input parameters
    @param device_id: int
    @param quadrant: int
    @param no_of_locations_required: int
    @return: list unique empty drawers
    """
    try:
        drawers_to_unlock = dict()

        clauses = [
            LocationMaster.device_id == device_id,
            LocationMaster.is_disabled == settings.is_location_active,
            ContainerMaster.drawer_type == constants.SIZE_OR_TYPE_MFD,
            MfdCanisterMaster.id.is_null(True)
        ]
        if quadrant:
            clauses.append((LocationMaster.quadrant == quadrant))

        drawer_query = LocationMaster.select(ContainerMaster.id,
                                             LocationMaster.display_location,
                                             ContainerMaster.drawer_name,
                                             ContainerMaster.serial_number,
                                             ContainerMaster.ip_address,
                                             ContainerMaster.secondary_ip_address,
                                             ContainerMaster.mac_address,
                                             ContainerMaster.secondary_mac_address
                                             ).dicts() \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=(MfdCanisterMaster.location_id == LocationMaster.id)) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=(ContainerMaster.id == LocationMaster.container_id)) \
            .where(functools.reduce(operator.and_, clauses)) \
            .order_by(LocationMaster.id) \
            .limit(no_of_locations_required)

        for record in drawer_query:
            display_location = record.get("display_location")
            if record["drawer_name"] not in drawers_to_unlock.keys():
                record["from_device"] = list()
                record["to_device"] = list()
                drawers_to_unlock[record["drawer_name"]] = record

            drawers_to_unlock[record["drawer_name"]]["to_device"].append(display_location)

        return drawers_to_unlock
    except (InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_home_cart_data_for_mfd_canister_in_robot(device_id: int) -> list:
    """
    Function to obtain home cart name for mfd canisters placed in given device_id
    :param device_id:
    :return:
    """
    try:
        query = LocationMaster.select(DeviceMaster.id.alias('trolley_id'),
                                      DeviceMaster.name.alias("trolley_name"),
                                      DeviceMaster.serial_number.alias("trolley_serial_number")).dicts() \
            .join(MfdCanisterMaster, on=(MfdCanisterMaster.location_id == LocationMaster.id)) \
            .join(DeviceMaster, on=(DeviceMaster.id == MfdCanisterMaster.home_cart_id)) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .where(LocationMaster.device_id == device_id) \
            .group_by(MfdCanisterMaster.home_cart_id)
        return list(query)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return []


@log_args_and_response
def check_drop_pending(device_ids: list) -> list:
    """
    Function to check if filled canister are present in robot
    :param device_ids:
    :return:
    """
    try:
        query = LocationMaster.select(DeviceMaster.id.alias('trolley_id'),
                                      DeviceMaster.name.alias("trolley_name"),
                                      MfdAnalysis.batch_id,
                                      fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.id)).alias("mfd_analysis_ids"),
                                      DeviceMaster.serial_number.alias("trolley_serial_number")).dicts() \
            .join(MfdCanisterMaster, on=(MfdCanisterMaster.location_id == LocationMaster.id)) \
            .join(DeviceMaster, on=(DeviceMaster.id == MfdCanisterMaster.home_cart_id)) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .where(LocationMaster.device_id << device_ids,
                   MfdAnalysis.status_id << [constants.MFD_CANISTER_FILLED_STATUS,
                                             constants.MFD_CANISTER_VERIFIED_STATUS]) \
            .group_by(MfdCanisterMaster.home_cart_id)
        print(query)
        return list(query)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return []


def check_in_robot(analysis_ids: list) -> list:
    """
    Function to obtain home cart name for mfd canisters placed in given device_id
    :param analysis_ids:
    :return:
    """
    try:
        canister_in_robot_list = list()
        if not analysis_ids:
            logger.info('No analysis_ids found returning')
            return canister_in_robot_list
        query = LocationMaster.select(DeviceMaster.id.alias('robot_id'),
                                      DeviceMaster.name.alias("robot_name"),
                                      DeviceMaster.serial_number.alias("trolley_serial_number")).dicts() \
            .join(MfdCanisterMaster, on=(MfdCanisterMaster.location_id == LocationMaster.id)) \
            .join(DeviceMaster, on=(DeviceMaster.id == LocationMaster.device_id)) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .where(DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT'],
                   MfdAnalysis.id << analysis_ids) \
            .group_by(DeviceMaster.id)
        for record in query:
            canister_in_robot_list.append(record['robot_id'])
        return canister_in_robot_list
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return []


@log_args_and_response
def get_mfd_rts_canisters(device_id: int, trolley_id: int, batch_id: int, required_canisters: int = None) -> list:
    """
    Method to fetch list of rts required canisters for given device, trolley and batch_id
    @param required_canisters: no of required canister
    @param device_id: id of robot device - source location of canister
    @param trolley_id: home trolley of canister
    @param batch_id: running batch id
    @return: list of canisters
    """
    try:
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        sub_query = MfdCanisterTransferHistory.select(
            fn.MAX(MfdCanisterTransferHistory.id).alias('max_canister_history_id'),
            MfdCanisterTransferHistory.mfd_canister_id.alias('mfd_canister_id')) \
            .group_by(MfdCanisterTransferHistory.mfd_canister_id).alias('sub_query_1')

        rts_canister_query = LocationMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id'),
                                                   MfdCanisterMaster.rfid,
                                                   MfdAnalysis.id.alias('mfd_analysis_id'),
                                                   LocationMaster.id.alias('location_id'),
                                                   LocationMaster.display_location,
                                                   ContainerMaster.id.alias('drawer_id'),
                                                   ContainerMaster.drawer_name,
                                                   ContainerMaster.serial_number,
                                                   ContainerMaster.ip_address,
                                                   ContainerMaster.secondary_ip_address,
                                                   ContainerMaster.mac_address,
                                                   ContainerMaster.secondary_mac_address,
                                                   MfdCanisterTransferHistory.created_date.alias('last_seen_time'),
                                                   DeviceMasterAlias.name.alias('previous_device_name'),
                                                   LocationMasterAlias.id.alias('previous_location_id'),
                                                   LocationMasterAlias.display_location
                                                   .alias('previous_display_location'),
                                                   ).dicts() \
            .join(ContainerMaster, on=(ContainerMaster.id == LocationMaster.container_id)) \
            .join(MfdCanisterMaster, on=(MfdCanisterMaster.location_id == LocationMaster.id)) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(sub_query, JOIN_LEFT_OUTER,
                  on=(sub_query.c.mfd_canister_id == MfdCanisterMaster.id)) \
            .join(MfdCanisterTransferHistory, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.id == sub_query.c.max_canister_history_id)) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.previous_location_id == LocationMasterAlias.id)) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER,
                  on=(LocationMasterAlias.device_id == DeviceMasterAlias.id)) \
            .where(LocationMaster.device_id == device_id,
                   ContainerMaster.drawer_type == constants.SIZE_OR_TYPE_MFD,
                   MfdCanisterMaster.home_cart_id == trolley_id,
                   MfdAnalysis.batch_id == batch_id,
                   MfdCanisterMaster.state_status == constants.MFD_CANISTER_ACTIVE,
                   MfdAnalysis.status_id == constants.MFD_CANISTER_RTS_REQUIRED_STATUS) \
            .order_by(ContainerMaster.id,
                      LocationMaster.id)
        print(rts_canister_query)
        if required_canisters:
            rts_canister_query = rts_canister_query.limit(required_canisters)
        return list(rts_canister_query)
    except (InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise


def get_mfd_non_rts_canisters(device_id: int, trolley_id: int, batch_id: int) -> list:
    """
    Method to fetch list of rts required canisters for given device, trolley and batch_id
    @param device_id: id of robot device - source location of canister
    @param trolley_id: home trolley of canister
    @param batch_id: running batch id
    @return: list of canisters
    """
    try:
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        sub_query = MfdCanisterTransferHistory.select(fn.MAX(MfdCanisterTransferHistory.id)
                                                      .alias('max_canister_history_id'),
                                                      MfdCanisterTransferHistory.mfd_canister_id.alias(
                                                          'mfd_canister_id')) \
            .group_by(MfdCanisterTransferHistory.mfd_canister_id).alias('sub_query_1')

        rts_canister_query = LocationMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id'),
                                                   MfdCanisterMaster.rfid,
                                                   MfdAnalysis.id.alias('mfd_analysis_id'),
                                                   LocationMaster.id.alias('location_id'),
                                                   LocationMaster.display_location,
                                                   ContainerMaster.id.alias('drawer_id'),
                                                   ContainerMaster.drawer_name,
                                                   ContainerMaster.serial_number,
                                                   ContainerMaster.ip_address,
                                                   ContainerMaster.mac_address,
                                                   ContainerMaster.secondary_mac_address,
                                                   ContainerMaster.secondary_ip_address,
                                                   MfdCanisterTransferHistory.created_date.alias('last_seen_time'),
                                                   DeviceMasterAlias.name.alias('previous_device_name'),
                                                   LocationMasterAlias.id.alias('previous_location_id'),
                                                   LocationMasterAlias.display_location
                                                   .alias('previous_display_location'),
                                                   ).dicts() \
            .join(ContainerMaster, on=(ContainerMaster.id == LocationMaster.container_id)) \
            .join(MfdCanisterMaster, on=(MfdCanisterMaster.location_id == LocationMaster.id)) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(sub_query, JOIN_LEFT_OUTER,
                  on=(sub_query.c.mfd_canister_id == MfdCanisterMaster.id)) \
            .join(MfdCanisterTransferHistory, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.id == sub_query.c.max_canister_history_id)) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.previous_location_id == LocationMasterAlias.id)) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER,
                  on=(LocationMasterAlias.device_id == DeviceMasterAlias.id)) \
            .where(LocationMaster.device_id == device_id,
                   ContainerMaster.drawer_type == constants.SIZE_OR_TYPE_MFD,
                   MfdCanisterMaster.home_cart_id == trolley_id,
                   MfdAnalysis.batch_id == batch_id,
                   MfdCanisterMaster.state_status == constants.MFD_CANISTER_ACTIVE,
                   MfdAnalysis.status_id == constants.MFD_CANISTER_DROPPED_STATUS) \
            .order_by(ContainerMaster.id,
                      LocationMaster.id)

        return list(rts_canister_query)
    except (InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def fetch_empty_trolley_locations_for_rts_canisters(trolley_id: int) -> list:
    """
    Method to fetch empty locations of given mfd trolley to put rts canisters
    @param trolley_id: id of trolley
    @return: list of records
    """
    try:
        empty_locations_list = list()
        empty_locations_query = LocationMaster.select(
            ContainerMaster.id.alias('container_id'),
            ContainerMaster.serial_number,
            ContainerMaster.drawer_name,
            fn.count(fn.distinct(LocationMaster.id)).alias('empty_locations_count'),
            fn.GROUP_CONCAT(fn.distinct(LocationMaster.id)).alias('empty_locations')
        ).dicts() \
            .join(ContainerMaster, on=(ContainerMaster.id == LocationMaster.container_id)) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .where(LocationMaster.device_id == trolley_id,
                   LocationMaster.is_disabled == False,
                   ContainerMaster.drawer_level > constants.MFD_TROLLEY_MIDDLE_LEVEL,
                   MfdCanisterMaster.id.is_null(True)) \
            .group_by(ContainerMaster.id) \
            .order_by(ContainerMaster.drawer_level.desc(), ContainerMaster.id)
        for record in empty_locations_query:
            record["empty_locations"] = record["empty_locations"].split(",")
            empty_locations_list.append(record)
        return empty_locations_list
    except (InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise


def fetch_empty_trolley_locations_for_non_rts_canisters(trolley_id: int) -> list:
    """
    Method to fetch empty locations of given mfd trolley to put empty mfd canisters
    @param trolley_id: id of trolley
    @return: list of records
    """
    try:
        empty_locations_list = list()
        empty_locations_query = LocationMaster.select(
            ContainerMaster.id.alias('container_id'),
            ContainerMaster.serial_number,
            ContainerMaster.drawer_name,
            fn.count(fn.distinct(LocationMaster.id)).alias('empty_locations_count'),
            fn.GROUP_CONCAT(fn.distinct(LocationMaster.id)).alias('empty_locations')
        ).dicts() \
            .join(ContainerMaster, on=(ContainerMaster.id == LocationMaster.container_id)) \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .where(LocationMaster.device_id == trolley_id,
                   ContainerMaster.drawer_level < constants.MFD_TROLLEY_MIDDLE_LEVEL,
                   MfdCanisterMaster.id.is_null(True)) \
            .group_by(ContainerMaster.id) \
            .order_by(ContainerMaster.drawer_level.desc(), ContainerMaster.id)
        for record in empty_locations_query:
            record["empty_locations"] = record["empty_locations"].split(",")
            empty_locations_list.append(record)
        return empty_locations_list
    except (InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise


def fetch_empty_locations_of_mfd_container(device_id: int, container_id: int) -> list:
    """
    Method to fetch empty locations of given mfd device id and container id
    @param container_id: id of container
    @param device_id: id of de
    @return: list of records
    """
    try:
        empty_locations_query = LocationMaster.select().dicts() \
            .join(MfdCanisterMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .where(LocationMaster.device_id == device_id,
                   LocationMaster.is_disabled == False,
                   LocationMaster.container_id == container_id,
                   MfdCanisterMaster.id.is_null(True))
        return list(empty_locations_query)
    except (InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise


def db_get_rts_drugs(company_id: int, home_cart: int = None, trolley_seq: int = None, batch_id: int = None) -> list:
    """
    Returns drug data filled in rts canisters
    :param company_id: int
    :param home_cart: int
    :param trolley_seq: int
    :param batch_id: int
    :return: list
    """

    clauses = list()
    clauses.append((MfdCanisterMaster.company_id == company_id))
    clauses.append((MfdCanisterMaster.rfid.is_null(False)))
    if home_cart:
        clauses.append((MfdCanisterMaster.home_cart_id == home_cart))

    # for rts drugs of previously used trolley canisters
    if trolley_seq and batch_id:
        min_order_number = get_min_order_from_batch_trolley(batch_id, trolley_seq)
        if not min_order_number:
            raise ValueError('Invalid data for rts')
        clauses.append((MfdAnalysis.order_no < min_order_number))

    try:
        query = MfdCanisterMaster.select(DrugMaster,
                                         DrugMaster.concated_drug_name_field(include_ndc=False).alias('drug_name'),
                                         fn.SUM(MfdAnalysisDetails.quantity).alias('quantity'),
                                         fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysis.mfd_canister_id))
                                         .alias('canister_ids')).dicts() \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(MfdAnalysisDetails, on=((MfdAnalysisDetails.analysis_id == MfdAnalysis.id) &
                                          (MfdAnalysisDetails.status_id == constants.MFD_DRUG_RTS_REQUIRED_STATUS))) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .where(*clauses) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr) \
            .order_by(DrugMaster.drug_name)

        data = list(query)
        return data

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_current_trolley_seq(batch_id: int, device_id: int) -> int:
    """
    returns trolley seq
    :param batch_id:
    :param device_id:
    :return:
    """
    try:
        query = MfdAnalysis.select(MfdAnalysis.trolley_seq).dicts() \
            .where(MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.dest_device_id == device_id,
                   MfdAnalysis.mfd_canister_id.is_null(False),
                   MfdAnalysis.mfs_device_id.is_null(False)) \
            .order_by(MfdAnalysis.order_no.desc())

        for record in query:
            return record["trolley_seq"]

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def mfd_misplaced_canister_dao(batch_id: int, device_id: int, trolley_id: int) -> tuple:
    """
    This function obtains the misplaced canisters list for the given batch_id and device_id
    :param batch_id:
    :param device_id:
    :param trolley_id:
    :return:
    """
    logger.info("In mfd_misplaced_canister_dao")
    LocationMasterAlias = LocationMaster.alias()
    DeviceMasterAlias = DeviceMaster.alias()
    DeviceMasterAlias2 = DeviceMaster.alias()

    LocationMasterAlias2 = LocationMaster.alias()
    DeviceMasterAlias3 = DeviceMaster.alias()
    try:
        sub_query = MfdCanisterTransferHistory.select(fn.MAX(MfdCanisterTransferHistory.id)
                                                      .alias('max_canister_history_id'),
                                                      MfdCanisterTransferHistory.mfd_canister_id
                                                      .alias('mfd_canister_id')
                                                      ) \
            .group_by(MfdCanisterTransferHistory.mfd_canister_id).alias('sub_query_1')

        # trolley_seq = get_current_trolley_seq(batch_id=batch_id,
        #                                       device_id=device_id)
        misplaced_canister_list = []
        rts_canister_misplaced_count = 0
        misplaced_canister_query = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id'),
                                                            MfdCanisterMaster.location_id.alias(
                                                                "current_location_id"),
                                                            LocationMaster.display_location.alias(
                                                                "current_display_location"),
                                                            DeviceMasterAlias2.name.alias('dest_device_name'),
                                                            ContainerMaster.drawer_name.alias('current_drawer_name'),
                                                            ContainerMaster.device_id.alias("current_device_id"),
                                                            DeviceMaster.name.alias("current_device_name"),
                                                            DeviceMaster.device_type_id.alias("current_device_type_id"),
                                                            ContainerMaster.ip_address.alias("current_ip_address"),
                                                            ContainerMaster.secondary_ip_address.alias(
                                                                "current_secondary_ip_address"),
                                                            DeviceMaster.device_type_id.alias("current_device_type_id"),
                                                            ContainerMaster.drawer_level,
                                                            MfdAnalysis.trolley_seq,
                                                            MfdAnalysis.status_id.alias('current_status'),
                                                            CodeMaster.value.alias('current_status_value'),
                                                            DeviceMasterAlias.name.alias('home_cart_device_name'),
                                                            DeviceMasterAlias.serial_number.alias(
                                                                'home_cart_serial_number'),
                                                            MfdCanisterTransferHistory.created_date.alias(
                                                                'last_seen_time'),
                                                            DeviceMasterAlias3.name.alias('previous_device_name'),
                                                            LocationMasterAlias2.id.alias('previous_location_id'),
                                                            LocationMasterAlias2.display_location.alias(
                                                                'previous_display_location'),
                                                            MfdCanisterMaster.home_cart_id.alias(
                                                                'home_cart_id')).dicts() \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=mfd_latest_analysis_sub_query.c.max_order_number == MfdAnalysis.order_no) \
            .join(DeviceMasterAlias2, on=MfdAnalysis.dest_device_id == DeviceMasterAlias2.id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == MfdCanisterMaster.home_cart_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(CodeMaster, on=MfdAnalysis.status_id == CodeMaster.id) \
            .join(sub_query, JOIN_LEFT_OUTER,
                  on=(sub_query.c.mfd_canister_id == MfdCanisterMaster.id)) \
            .join(MfdCanisterTransferHistory, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.id == sub_query.c.max_canister_history_id)) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.previous_location_id == LocationMasterAlias2.id)) \
            .join(DeviceMasterAlias3, JOIN_LEFT_OUTER,
                  on=(LocationMasterAlias2.device_id == DeviceMasterAlias3.id)) \
            .where((MfdAnalysis.batch_id == batch_id),
                   (LocationMasterAlias.device_id == trolley_id),
                   (MfdCanisterMaster.state_status == constants.MFD_CANISTER_ACTIVE),
                   (MfdAnalysis.status_id << [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                              constants.MFD_CANISTER_DROPPED_STATUS]),
                   (MfdAnalysis.dest_device_id == device_id)) \
            .order_by(ContainerMaster.id,
                      LocationMaster.id)
        for record in misplaced_canister_query:
            record["recommended_drawer_name"] = None
            record["recommended_display_loc"] = None
            record["recommended_drawer_id"] = None
            # RTS Canister and on-shelf
            if record['current_status'] == constants.MFD_CANISTER_RTS_REQUIRED_STATUS:
                if record['current_location_id'] is None or record['current_device_type_id'] in \
                        [settings.DEVICE_TYPES['Manual Filling Device']]:
                    misplaced_canister_list.append(record)
                    rts_canister_misplaced_count += 1
            elif record['current_status'] == constants.MFD_CANISTER_DROPPED_STATUS:
                # Non RTS canister and In trolley
                if record['current_location_id'] is not None and record['drawer_level'] in \
                        constants.MFD_TROLLEY_FILLED_DRAWER_LEVEL and record['current_device_type_id'] in \
                        [settings.DEVICE_TYPES['Manual Canister Cart']]:
                    misplaced_canister_list.append(record)
                # Non RTS Canister and on shelf
                if record['current_location_id'] is None or record['current_device_type_id'] in \
                        [settings.DEVICE_TYPES['Manual Filling Device']]:
                    misplaced_canister_list.append(record)
        return misplaced_canister_list, rts_canister_misplaced_count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_max_order_number_from_mfd_analysis():
    """
    Function to get max order number from mfd analysis
    @return: int
    """
    try:
        order_no = MfdAnalysis.db_get_max_order_number()
        if not order_no:
            return 1
        return order_no + 1

    except Exception as e:
        logger.error(e, exc_info=True)
        return None


def get_min_order_from_batch_trolley(batch_id: int, trolley_seq: int):
    """
    Function to get min order number for scanned trolley
    @return: int
    """
    try:
        order_no = MfdAnalysis.db_get_min_analysis_id(batch_id, trolley_seq)
        return order_no

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        return None


@log_args_and_response
def get_latest_record_by_canister_id(mfd_canister_id: int):
    """
    returns last transaction history for given mfd_canister
    :param mfd_canister_id: int
    :return: record
    """
    try:
        record = MfdCanisterTransferHistory.db_get_latest_record_by_canister_id(mfd_canister_id)
        return record
    except (IntegrityError, InternalError) as e:
        raise e


@log_args_and_response
def update_mfd_canister_transfer_data(update_dict: dict, mfd_canister_id: int) -> int:
    """
    updates canister transfer data for given mfd_canister_id
    :param mfd_canister_id: int
    :param update_dict: dict
    :return: status(number of updated rows)
    """
    try:
        status = MfdCanisterTransferHistory.db_update(update_dict, id=mfd_canister_id)
        return status
    except (IntegrityError, InternalError) as e:
        raise e


@log_args_and_response
def add_mfd_canister_history(canister_history_list: list) -> int:
    """
    inserts history data
    :param canister_history_list: list
    :return: status
    """
    try:
        status = MfdCanisterTransferHistory.db_create_multi_record(canister_history_list, MfdCanisterTransferHistory)
        return status
    except (IntegrityError, InternalError) as e:
        raise e


@log_args_and_response
def update_mfd_canister_location_with_fork(canister_location_dict: dict) -> int:
    """
    updates current location and fork detection flag of canister
    :param canister_location_dict: dict
    :return: int
    """
    canister_ids = list()
    location_ids = list()
    fork_detection = list()

    for canister_id, canister_info in canister_location_dict.items():
        canister_ids.append(canister_id)
        location_ids.append(canister_info['location_id'])
        fork_detection.append(canister_info['fork_detection'])

    try:
        status = MfdCanisterMaster.db_update_canister_location_and_fork(canister_ids, location_ids, fork_detection)
        return status
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def mfd_misplaced_canister_transfer_to_robot(batch_id: int, device_id: int, trolley_id: int, drawer_id: int) -> tuple:
    """
    This function obtains the misplaced canisters list for the given batch_id and device_id
    :param batch_id:
    :param device_id:
    :param trolley_id:
    :param drawer_id:
    :return:
    """
    logger.info("In mfd_misplaced_canister_dao")
    LocationMasterAlias2 = LocationMaster.alias()
    DeviceMasterAlias3 = DeviceMaster.alias()
    ContainerMasterAlias = ContainerMaster.alias()
    try:
        sub_query = MfdCanisterTransferHistory.select(fn.MAX(MfdCanisterTransferHistory.id)
                                                      .alias('max_canister_history_id'),
                                                      MfdCanisterTransferHistory.mfd_canister_id
                                                      .alias('mfd_canister_id')
                                                      ) \
            .group_by(MfdCanisterTransferHistory.mfd_canister_id).alias('sub_query_1')

        LocationMasterALias = LocationMaster.alias()
        DeviceMasterALias = DeviceMaster.alias()
        DeviceMasterALias2 = DeviceMaster.alias()
        misplaced_canister_ids = []
        quadrant_wise_count = defaultdict(set)
        misplaced_canister_query = MfdCanisterMaster.select(MfdAnalysis.mfd_canister_id,
                                                            MfdCanisterMaster.rfid,
                                                            MfdCanisterMaster.fork_detected,
                                                            MfdCanisterMaster.state_status,
                                                            MfdAnalysis.status_id,
                                                            DeviceMaster.id.alias('home_cart_id'),
                                                            DeviceMaster.name.alias('home_cart_device_name'),
                                                            LocationMaster.container_id.alias('home_cart_drawer_id'),
                                                            DeviceMasterALias.name.alias('current_device_name'),
                                                            DeviceMasterALias.id.alias('current_device_id'),
                                                            DeviceMaster.device_type_id,
                                                            LocationMasterALias.display_location.alias(
                                                                'current_display_location'),
                                                            MfdAnalysis.trolley_location_id,
                                                            MfdAnalysis.trolley_seq,
                                                            LocationMasterALias.id.alias('current_location_id'),
                                                            MfdAnalysis.id.alias('mfd_analysis_id'),
                                                            LocationMasterALias.quadrant.alias('current_quadrant'),
                                                            LocationMasterALias.device_id.alias('current_device'),
                                                            MfdAnalysis.dest_device_id,
                                                            DeviceMasterALias2.name.alias('dest_device_name'),
                                                            DeviceMasterALias.device_type_id.alias(
                                                                'current_device_type_id'),
                                                            ContainerMaster.drawer_name.alias('trolley_drawer_name'),
                                                            MfdAnalysis.dest_quadrant,
                                                            MfdCanisterTransferHistory.created_date.alias(
                                                                'last_seen_time'),
                                                            DeviceMasterAlias3.name.alias('previous_device_name'),
                                                            LocationMasterAlias2.id.alias('previous_location_id'),
                                                            LocationMasterAlias2.display_location.alias(
                                                                'previous_display_location'),
                                                            ContainerMasterAlias.secondary_ip_address.alias(
                                                                'current_secondary_ip_address'),
                                                            ContainerMasterAlias.ip_address.alias(
                                                                'current_ip_address')).dicts() \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=mfd_latest_analysis_sub_query.c.max_order_number == MfdAnalysis.order_no) \
            .join(DeviceMasterALias2, on=DeviceMasterALias2.id == MfdAnalysis.dest_device_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(LocationMasterALias, JOIN_LEFT_OUTER, on=LocationMasterALias.id == MfdCanisterMaster.location_id) \
            .join(ContainerMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterALias.container_id == ContainerMasterAlias.id) \
            .join(DeviceMasterALias, JOIN_LEFT_OUTER, on=LocationMasterALias.device_id == DeviceMasterALias.id) \
            .join(CodeMaster, on=MfdAnalysis.status_id == CodeMaster.id) \
            .join(sub_query, JOIN_LEFT_OUTER,
                  on=(sub_query.c.mfd_canister_id == MfdCanisterMaster.id)) \
            .join(MfdCanisterTransferHistory, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.id == sub_query.c.max_canister_history_id)) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.previous_location_id == LocationMasterAlias2.id)) \
            .join(DeviceMasterAlias3, JOIN_LEFT_OUTER,
                  on=(LocationMasterAlias2.device_id == DeviceMasterAlias3.id)) \
            .where(MfdAnalysis.batch_id == batch_id,
                   DeviceMaster.id == trolley_id,
                   ContainerMaster.id != drawer_id,
                   MfdCanisterMaster.state_status == constants.MFD_CANISTER_ACTIVE,
                   (MfdCanisterMaster.location_id.is_null(True) |
                    ((DeviceMasterALias.device_type_id != settings.DEVICE_TYPES["Manual Canister Cart"]) &
                     ((LocationMasterALias.device_id != MfdAnalysis.dest_device_id) |
                      (LocationMasterALias.quadrant != MfdAnalysis.dest_quadrant) |
                      (MfdCanisterMaster.fork_detected != 1)))),
                   MfdAnalysis.status_id << [constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                             constants.MFD_CANISTER_FILLED_STATUS,
                                             constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                             constants.MFD_CANISTER_VERIFIED_STATUS],
                   MfdAnalysis.dest_device_id == device_id)
        misplaced_canister_query = misplaced_canister_query.order_by(ContainerMaster.id,
                                                                     LocationMaster.id)

        deactivate_misplaced_query = mfd_deactivate_other_trolley_misplaced(device_id=device_id)
        for record in chain(misplaced_canister_query, deactivate_misplaced_query):
            if record['state_status'] == constants.MFD_CANISTER_INACTIVE:
                record['home_cart_id'] = None
                record['home_cart_device_name'] = None
                record['home_cart_drawer_id'] = None
                record['trolley_drawer_name'] = None
            if (record['current_quadrant'] != record['dest_quadrant'] or
                record['current_device'] != record['dest_device_id']) and \
                    record['current_device_type_id'] == settings.DEVICE_TYPES["ROBOT"]:
                record['placed_in_robot'] = True
            else:
                record['placed_in_robot'] = False
            if record['status_id'] in [constants.MFD_CANISTER_FILLED_STATUS,
                                       constants.MFD_CANISTER_VERIFIED_STATUS]:
                quadrant_wise_count[record['dest_quadrant']].add(record['mfd_canister_id'])
                record['to_be_placed_in_robot'] = True
            else:
                record['to_be_placed_in_robot'] = False
            record['fork_detection_error'] = not (record['fork_detected'])
            misplaced_canister_ids.append(record)

        return misplaced_canister_ids, quadrant_wise_count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_mfd_canister_data_by_ids(canister_ids: list, company_id: int = None):
    """
    returns canister data
    :param canister_ids: list
    :param company_id: int
    :return: dict
    """
    try:
        query = MfdCanisterMaster.select(MfdCanisterMaster,
                                         MfdAnalysis.batch_id,
                                         MfdCanisterMaster.id.alias('mfd_canister_id'),
                                         LocationMaster.display_location,
                                         DeviceMaster.device_type_id,
                                         DeviceMaster.system_id,
                                         DeviceMaster.id.alias('current_device_id'),
                                         MfdAnalysis.mfs_location_number,
                                         MfdAnalysis.dest_quadrant,
                                         MfdAnalysis.dest_device_id,
                                         MfdAnalysis.id.alias('mfd_analysis_id'),
                                         MfdAnalysis.status_id.alias('mfd_canister_status_id'),
                                         LocationMaster.location_number.alias('current_location_number'),
                                         TempMfdFilling.id.alias('temp_mfd_filling_id'),
                                         fn.GROUP_CONCAT(fn.DISTINCT(MfdAnalysisDetails.status_id)).alias(
                                             'mfd_drug_status_id'),
                                         ).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id) \
            .join(mfd_latest_analysis_sub_query, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER,
                  on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(TempMfdFilling, JOIN_LEFT_OUTER, on=MfdAnalysis.id == TempMfdFilling.mfd_analysis_id) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .where(MfdCanisterMaster.id << canister_ids) \
            .group_by(MfdCanisterMaster.id)
        if company_id:
            query = query.where(MfdCanisterMaster.company_id == company_id)

        return query

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def check_module_update(device_id: int, batch_id: int, trolley_id_list: list) -> tuple:
    """
    checking if trolley has any canisters filled and not in robot or rts and in robot
    @param device_id:
    @param batch_id:
    @param trolley_id_list:
    @return: query
    """
    try:
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        transfer_to_robot_done = True
        rts_canister_in_robot = False

        query = MfdCanisterMaster.select(LocationMaster.device_id,
                                         DeviceMaster.name,
                                         MfdCanisterMaster.id.alias('mfd_canister_id'),
                                         MfdCanisterMaster.fork_detected,
                                         ContainerMaster.serial_number,
                                         DeviceMaster.device_type_id,
                                         fn.MAX(MfdAnalysis.trolley_seq).alias('max_trolley_seq'),
                                         MfdAnalysis.status_id.alias('canister_status'),
                                         ContainerMaster.id.alias('container_id'),
                                         ContainerMaster.drawer_name.alias('drawer_number')).dicts() \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=(LocationMasterAlias.id == MfdCanisterMaster.location_id)) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMasterAlias.device_id) \
            .where(LocationMaster.device_id << trolley_id_list,
                   MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.dest_device_id == device_id,
                   ((MfdAnalysis.status_id << constants.MFD_CANISTER_DONE_LIST) |
                    (((MfdAnalysis.status_id.in_([constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                  constants.MFD_CANISTER_MVS_FILLING_REQUIRED])) &
                      (DeviceMasterAlias.id != DeviceMaster.id))))) \
            .order_by(MfdAnalysis.status_id) \
            .group_by(MfdCanisterMaster.id)

        for record in query:
            if record['canister_status'] in [constants.MFD_CANISTER_VERIFIED_STATUS,
                                             constants.MFD_CANISTER_FILLED_STATUS,
                                             constants.MFD_CANISTER_MVS_FILLING_REQUIRED]:
                logger.info('checking_module_update on rts refresh for Batch: {} Trolley: {}'
                             ' transfer_pending_canister_id: {}'.format(batch_id, trolley_id_list,
                                                                        record['mfd_canister_id']))
                transfer_to_robot_done = False
                break
            elif record['canister_status'] == constants.MFD_CANISTER_RTS_REQUIRED_STATUS:
                logger.info('checking_module_update on rts refresh for Batch: {} Trolley: {} rts_canister_in_robot: {}'
                             .format(batch_id, trolley_id_list, record['mfd_canister_id']))
                rts_canister_in_robot = True

        logger.info('checking_module_update on rts refresh for Batch: {} Trolley: {} returning data: '
                     'transfer_to_robot_done: {} rts_canister_in_robot: {}'.
                     format(batch_id, trolley_id_list, transfer_to_robot_done, rts_canister_in_robot))
        return transfer_to_robot_done, rts_canister_in_robot

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def validate_mfd_canister_by_company(mfd_canister_ids: list, company_id: int) -> bool:
    """
    Method to validate mfd canister against company
    @mfd_canister_ids = list of canisters to be validated
    @company_id = registered company of mfd canisters
    @return: created_record
    """
    try:
        return MfdCanisterMaster.db_verify_mfd_canister_ids(mfd_canister_ids, company_id)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise e


def mark_mfd_canister_deactivate_status_update(mfd_canister_ids: list, update_dict: dict) -> bool:
    """
    Method to deactivate mfd canister in mfd_canister_master table
    @mfd_canister_ids = list of canisters to be deactivated
    @update_dict = dict data to be updated
    @return: created_record
    """
    try:
        status = MfdCanisterMaster.db_update_data_by_mfd_canister_id(mfd_canister_ids, update_dict)
        return status
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_mark_mfd_canister_activate(mfd_canister_home_cart_dict: dict) -> bool:
    """
    method to mark canister active/found in mfd canister master
    @mfd_canister_home_cart_dict = dict
    @return: bool
    """

    try:
        for home_cart_id, mfd_canister_ids in mfd_canister_home_cart_dict.items():
            update_dict = {'state_status': 1, 'home_cart_id': home_cart_id}
            status = MfdCanisterMaster.db_update_data_by_mfd_canister_id(mfd_canister_ids, update_dict)
            logger.info("In db_mark_mfd_canister_activate: mfd canister data updated: {}".format(status))
        return True
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


def add_mfd_canister_status_history(data_dict: list) -> object:
    """
    Method to add record in mfd canister status history
    @data_dict = dict of data to be inserted
    @return: created_record
    """
    try:
        record = MfdCanisterStatusHistory.insert_many(data_dict).execute()
        logger.info("Added record {} in mfd canister master status".format(record))
        return record
    except DataError as e:
        logger.error(e, exc_info=True)
        raise DataError(e)
    except IntegrityError as e:
        logger.error(e, exc_info=True)
        raise InternalError(e)
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise InternalError(e)


@log_args_and_response
def mark_mfd_canister_misplaced(mfd_canister_home_cart_dict: dict) -> bool:
    """
    Marks canister misplaced
    @mfd_canister_home_cart_dict = list of canisters to be validated
    @return: bool
    """

    try:
        for home_cart_id, mfd_canister_ids in mfd_canister_home_cart_dict.items():
            update_dict = {'state_status': 2, 'home_cart_id': home_cart_id, 'location_id': None}
            status = MfdCanisterMaster.db_update_data_by_mfd_canister_id(mfd_canister_ids, update_dict)
            logger.info("In mark_mfd_canister_misplaced: mfd canister data updated by canister id: {}".format(status))
        return True
    except (IntegrityError, InternalError) as e:
        raise e


def get_latest_mfd_status_history_data(mfd_canister_ids: list, comment: str or None) -> tuple:
    """
    creates dict with the latest history for insertion in tables
    :param comment:
    :param mfd_canister_ids:
    :return: tuple
    """
    try:
        history_comment_dict = dict()
        mfd_canister_home_cart_dict = dict()
        current_history_data = get_previous_cart(mfd_canister_ids)
        for record in current_history_data:
            history_comment_dict[record['mfd_canister_id']] = {'status_history_id': record['max_status_history_id'],
                                                               'comment': comment}
            mfd_canister_home_cart_dict[record['mfd_canister_id']] = {'mfd_canister_id': record['mfd_canister_id'],
                                                                      'home_cart_device': record['home_cart']}
        return list(history_comment_dict.values()), mfd_canister_home_cart_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_update_canister_active_status(mfd_canister_home_cart_dict: dict, action_id: int, user_id: int,
                                     comment: str or None = None):
    """
    updates mfd canister state_status and adds history data in respective tables
    :param mfd_canister_home_cart_dict:
    :param action_id:
    :param user_id:
    :param comment:
    :return:
    """
    try:
        mfd_canister_ids = list()
        canister_status_history_list = list()
        for home_cart_id, mfd_canister_home_cart_dict in mfd_canister_home_cart_dict.items():
            for mfd_canister_id in mfd_canister_home_cart_dict:
                mfd_canister_ids.append(mfd_canister_id)
                canister_status_history_list.append({
                    "mfd_canister_id": mfd_canister_id,
                    "home_cart": home_cart_id,
                    "action_id": action_id,
                    "created_by": user_id,
                    "modified_by": user_id,
                })
        if canister_status_history_list:
            canister_status_history = add_mfd_canister_status_history(canister_status_history_list)
            logger.info("In db_update_canister_active_status: Added record {} in mfd canister master status".format(canister_status_history))
            if comment:
                latest_status_history_data, history_mfd_canister_home_cart_dict = get_latest_mfd_status_history_data(
                    mfd_canister_ids, comment)
                logger.info('latest_status_history_data: {}'.format(latest_status_history_data))
                if latest_status_history_data:
                    comment_add_status = MfdStatusHistoryComment.db_add_status_comment_history_data(
                        latest_status_history_data)
                    logger.info(
                        "In db_update_canister_active_status: comment history data added: {}".format(
                            comment_add_status))
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_canister_data_by_id(canister_id: int):
    """
    returns canister data by mfd_canister_id
    :param canister_id: int
    :return: dict
    """
    try:
        LocationMasterAlias2 = LocationMaster.alias()
        LocationMasterAlias3 = LocationMaster.alias()
        DeviceMasterAlias2 = DeviceMaster.alias()
        DeviceMasterAlias3 = DeviceMaster.alias()
        response = MfdCanisterMaster.select(MfdCanisterMaster,
                                            ContainerMaster.drawer_name.alias('trolley_drawer_name'),
                                            ContainerMaster.id.alias('source_drawer_id'),
                                            MfdAnalysis.status_id,
                                            MfdAnalysis.dest_device_id,
                                            TempMfdFilling.id.alias('temp_filling_id'),
                                            MfdAnalysis.trolley_location_id,
                                            LocationMasterAlias2.display_location.alias('mfs_display_location'),
                                            DeviceMaster.name.alias('trolley_name'),
                                            TempMfdFilling.transfer_done,
                                            TempMfdFilling.id.alias('is_currently_in_progress'),
                                            DeviceMasterAlias3.device_type_id.alias('current_device_type_id'),
                                            LocationMasterAlias3.location_number.alias('current_loc_number'),
                                            DeviceMasterAlias3.serial_number.alias('current_serial_number'),
                                            TempMfdFilling.transfer_done).dicts() \
            .join(mfd_latest_analysis_sub_query, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER,
                  on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdAnalysis.trolley_location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id) \
            .join(TempMfdFilling, JOIN_LEFT_OUTER, on=TempMfdFilling.mfd_analysis_id == MfdAnalysis.id) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER,
                  on=((MfdAnalysis.mfs_device_id == LocationMasterAlias2.device_id) &
                      (MfdAnalysis.mfs_location_number == LocationMasterAlias2.location_number))) \
            .join(DeviceMasterAlias2, JOIN_LEFT_OUTER, on=DeviceMasterAlias2.id == LocationMasterAlias2.device_id) \
            .join(LocationMasterAlias3, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMasterAlias3.id) \
            .join(DeviceMasterAlias3, JOIN_LEFT_OUTER, on=DeviceMasterAlias3.id == LocationMasterAlias3.device_id) \
            .where(MfdCanisterMaster.id == canister_id).get()
        return response
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return None

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_mfd_canister_data_by_analysis_ids(mfd_analysis_ids, company_id: int = None):
    """
    returns mfd canister data for given mfd_analysis_ids
    :param mfd_analysis_ids: list
    :param company_id: int
    :return: dict
    """
    try:
        query = MfdCanisterMaster.select(MfdCanisterMaster,
                                         MfdCanisterMaster.id.alias('mfd_canister_id'),
                                         LocationMaster.display_location,
                                         DeviceMaster.device_type_id,
                                         MfdAnalysis.id.alias('mfd_analysis_id'),
                                         MfdAnalysis.status_id.alias('mfd_canister_status_id'),
                                         ).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=LocationMaster.device_id == DeviceMaster.id) \
            .join(mfd_latest_analysis_sub_query, JOIN_LEFT_OUTER,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER,
                  on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .where(MfdAnalysis.id << mfd_analysis_ids)
        if company_id:
            query = query.where(MfdCanisterMaster.company_id == company_id)

        return query

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_unique_rts_actions(company_id: int) -> dict:
    """
    To get unique drugs that requires RTS
    :param company_id: int
    :return: list
    """
    action_dict = dict()
    try:
        query = MfdCanisterMaster.select(ActionMaster.value, ActionMaster.id.alias('action_id')
                                         ).dicts() \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(MfdAnalysisDetails, on=((MfdAnalysisDetails.analysis_id == MfdAnalysis.id) &
                                          (MfdAnalysisDetails.status_id == constants.MFD_DRUG_RTS_REQUIRED_STATUS))) \
            .join(mfd_latest_history_sub_query, on=MfdAnalysis.id == mfd_latest_history_sub_query.c.mfd_analysis_id) \
            .join(MfdCycleHistory, on=MfdCycleHistory.id == mfd_latest_history_sub_query.c.max_history_id) \
            .join(ActionMaster, on=MfdCycleHistory.action_id == ActionMaster.id) \
            .where(MfdCanisterMaster.company_id == company_id,
                   MfdCanisterMaster.rfid.is_null(False)) \
            .group_by(ActionMaster.id)
        for record in query:
            action_dict[record['value']] = record['action_id']
        return action_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def get_previous_cart(mfd_canister_ids: list):
    """
    To get last associated cart
    :param mfd_canister_ids: list
    :return: list
    """
    # action_dict = dict()
    try:
        query = MfdCanisterMaster.select(MfdCanisterStatusHistory.home_cart,
                                         MfdCanisterStatusHistory.id.alias('max_status_history_id'),
                                         MfdCanisterStatusHistory.mfd_canister_id
                                         ).dicts() \
            .join(mfd_latest_state_status_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_state_status_sub_query.c.mfd_canister_id) \
            .join(MfdCanisterStatusHistory,
                  on=MfdCanisterStatusHistory.id == mfd_latest_state_status_sub_query.c.max_status_history_id) \
            .where(MfdCanisterMaster.id << mfd_canister_ids)
        return query
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


def mfd_deactivate_other_trolley_misplaced(device_id: int) -> tuple:
    """
    @param device_id:
    :return:
    """
    logger.info("In mfd_misplaced_canister_dao")
    try:
        LocationMasterALias = LocationMaster.alias()
        DeviceMasterALias = DeviceMaster.alias()
        DeviceMasterALias2 = DeviceMaster.alias()

        LocationMasterAlias2 = LocationMaster.alias()
        DeviceMasterAlias3 = DeviceMaster.alias()

        sub_query = MfdCanisterTransferHistory.select(fn.MAX(MfdCanisterTransferHistory.id)
                                                      .alias('max_canister_history_id'),
                                                      MfdCanisterTransferHistory.mfd_canister_id
                                                      .alias('mfd_canister_id')
                                                      ) \
            .group_by(MfdCanisterTransferHistory.mfd_canister_id).alias('sub_query_1')

        misplaced_canister_query = MfdCanisterMaster.select(MfdAnalysis.mfd_canister_id,
                                                            MfdCanisterMaster.rfid,
                                                            MfdCanisterMaster.fork_detected,
                                                            MfdCanisterMaster.state_status,
                                                            MfdAnalysis.status_id,
                                                            DeviceMaster.id.alias('home_cart_id'),
                                                            DeviceMaster.name.alias('home_cart_device_name'),
                                                            LocationMaster.container_id.alias('home_cart_drawer_id'),
                                                            DeviceMasterALias.name.alias('current_device_name'),
                                                            DeviceMaster.device_type_id,
                                                            LocationMasterALias.display_location.alias(
                                                                'current_display_location'),
                                                            MfdAnalysis.trolley_location_id,
                                                            MfdAnalysis.trolley_seq,
                                                            LocationMasterALias.id.alias('current_location_id'),
                                                            MfdAnalysis.id.alias('mfd_analysis_id'),
                                                            LocationMasterALias.quadrant.alias('current_quadrant'),
                                                            LocationMasterALias.device_id.alias('current_device'),
                                                            MfdAnalysis.dest_device_id,
                                                            DeviceMasterALias2.name.alias('dest_device_name'),
                                                            DeviceMasterALias.device_type_id.alias(
                                                                'current_device_type_id'),
                                                            ContainerMaster.drawer_name.alias('trolley_drawer_name'),
                                                            MfdAnalysis.dest_quadrant).dicts() \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=mfd_latest_analysis_sub_query.c.max_order_number == MfdAnalysis.order_no) \
            .join(DeviceMasterALias2, on=DeviceMasterALias2.id == MfdAnalysis.dest_device_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(LocationMasterALias, JOIN_LEFT_OUTER, on=LocationMasterALias.id == MfdCanisterMaster.location_id) \
            .join(DeviceMasterALias, JOIN_LEFT_OUTER, on=LocationMasterALias.device_id == DeviceMasterALias.id) \
            .join(CodeMaster, on=MfdAnalysis.status_id == CodeMaster.id) \
            .join(sub_query, JOIN_LEFT_OUTER,
                  on=(sub_query.c.mfd_canister_id == MfdCanisterMaster.id)) \
            .join(MfdCanisterTransferHistory, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.id == sub_query.c.max_canister_history_id)) \
            .join(LocationMasterAlias2, JOIN_LEFT_OUTER,
                  on=(MfdCanisterTransferHistory.previous_location_id == LocationMasterAlias2.id)) \
            .join(DeviceMasterAlias3, JOIN_LEFT_OUTER,
                  on=(LocationMasterAlias2.device_id == DeviceMasterAlias3.id)) \
            .where(((MfdCanisterMaster.state_status == constants.MFD_CANISTER_INACTIVE) &
                    (DeviceMasterALias.id == device_id)))
        misplaced_canister_query = misplaced_canister_query.order_by(ContainerMaster.id,
                                                                     LocationMaster.id)
        return misplaced_canister_query

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_delete_mfd_analysis_by_analysis_ids(mfd_analysis_list: list):
    """
    Function to delete data of packs that are to be moved manual from mfd analysis and mfd analysis details
    @param mfd_analysis_list:
    @return:
    """
    try:
        # delete analysis data
        if mfd_analysis_list:
            status1 = MfdAnalysisDetails.delete() \
                .where(MfdAnalysisDetails.analysis_id << mfd_analysis_list) \
                .execute()
            status2 = MfdAnalysis.delete().where(MfdAnalysis.id << mfd_analysis_list) \
                .execute()
            logger.info("In db_delete_mfd_analysis_by_analysis_ids: data deleted from mfd analysis : {}, data deleted from mfd analysis details: {}".format(status2, status1))
        return True

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in db_delete_pack_analysis_by_packs {}".format(e))
        raise


@log_args_and_response
def db_get_rts_required_canisters_query(filter_fields: dict, sort_fields: list,
                                        paginate: dict,
                                        clauses: list, exact_search_list=None, like_search_list=None,
                                        left_like_search_list=None, membership_search_list=None):
    """

    @param filter_fields:
    @param sort_fields:
    @param paginate:
    @param clauses:
    @param exact_search_list:
    @param like_search_list:
    @param left_like_search_list:
    @param membership_search_list:
    @return:
    """

    fields_dict = {"mfd_canister_id": MfdCanisterMaster.id,
                   "source_device_id": DeviceMaster.id,
                   "drug_name": DrugMaster.concated_drug_name_field(),
                   "ndc": DrugMaster.formatted_ndc,
                   "source_display_location": LocationMaster.display_location,
                   "home_cart_id": MfdCanisterMaster.home_cart_id,
                   "reason_to_return": ActionMaster.id,
                   "state_status": MfdCanisterMaster.state_status,
                   "source_device_name": DeviceMaster.name,
                   "source_drawer_name": ContainerMaster.drawer_name}

    try:
        query = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id'),
                                         MfdCanisterMaster.rfid,
                                         MfdCanisterMaster.state_status,
                                         MfdCanisterMaster.erp_product_id,
                                         MfdCanisterMaster.label_print_time,
                                         MfdCycleHistory.action_id,
                                         MfdCycleHistoryComment.comment,
                                         LocationMaster.device_id.alias('source_device_id'),
                                         DeviceMaster.name.alias('source_device_name'),
                                         DeviceMaster.device_type_id.alias('source_device_type'),
                                         ContainerMaster.drawer_name.alias('source_drawer_name'),
                                         LocationMaster.display_location.alias('source_display_location'),
                                         DeviceMaster.system_id,
                                         MfdAnalysis.status_id,
                                         CodeMaster.value.alias('status'),
                                         fn.IF(DeviceMaster.device_type_id == settings.DEVICE_TYPES[
                                             "Manual Canister Cart"],
                                               True, fn.IF(LocationMaster.id.is_null(True),
                                                           True, False)).alias('rts_allowed'),
                                         MfdAnalysis.assigned_to,
                                         MfdAnalysis.id.alias('mfd_analysis_id'),
                                         PackRxLink.pack_id,
                                         ActionMaster.value.alias('reason_to_return')) \
            .join(mfd_latest_analysis_sub_query,
                  on=MfdCanisterMaster.id == mfd_latest_analysis_sub_query.c.mfd_canister_id) \
            .join(MfdAnalysis, on=MfdAnalysis.order_no == mfd_latest_analysis_sub_query.c.max_order_number) \
            .join(mfd_latest_history_sub_query, on=MfdAnalysis.id == mfd_latest_history_sub_query.c.mfd_analysis_id) \
            .join(MfdCycleHistory, on=MfdCycleHistory.id == mfd_latest_history_sub_query.c.max_history_id) \
            .join(ActionMaster, on=MfdCycleHistory.action_id == ActionMaster.id) \
            .join(MfdAnalysisDetails, on=((MfdAnalysisDetails.analysis_id == MfdAnalysis.id) &
                                          (MfdAnalysisDetails.status_id == constants.MFD_DRUG_RTS_REQUIRED_STATUS))) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
            .join(MfdCycleHistoryComment, JOIN_LEFT_OUTER,
                  on=MfdCycleHistory.id == MfdCycleHistoryComment.cycle_history_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == MfdCanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(CodeMaster, JOIN_LEFT_OUTER, on=CodeMaster.id == MfdAnalysis.status_id) \
            .group_by(MfdCanisterMaster.id)

        results, count = get_results(query.dicts(), fields_dict, filter_fields=filter_fields,
                                     clauses=clauses,
                                     sort_fields=sort_fields,
                                     paginate=paginate,
                                     exact_search_list=exact_search_list,
                                     like_search_list=like_search_list,
                                     left_like_search_fields=left_like_search_list,
                                     membership_search_list=membership_search_list,
                                     # The canister on which action can be taken are in the trolley
                                     # so keeping them first by ordering them on device type
                                     last_order_field=[SQL('FIELD(source_device_type, {})'.
                                                           format(settings.DEVICE_TYPES['Manual Canister Cart'])).desc(),
                                                       MfdCanisterMaster.id])

        return results, count

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_next_trolley(batch_id, device_id=None):
    """
    returns count of canisters currently placed on mfs
    in trolley
    :param batch_id: int
    :param device_id: int
    :return: int
    """
    # same function in mfd_dao
    try:
        query = MfdAnalysis.select(LocationMaster.device_id,
                                   DeviceMaster.name,
                                   BatchMaster.system_id,
                                   MfdAnalysis.trolley_seq).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(MfdAnalysis.batch_id == batch_id,
                   MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_SKIPPED_STATUS,
                                                 constants.MFD_CANISTER_RTS_DONE_STATUS,
                                                 constants.MFD_CANISTER_DROPPED_STATUS,
                                                 constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                 constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                 constants.MFD_CANISTER_RTS_REQUIRED_STATUS]),
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS,
                                               settings.PROGRESS_PACK_STATUS])
        if device_id:
            query = query.where(MfdAnalysis.dest_device_id == device_id)

        query = query.order_by(MfdAnalysis.order_no).group_by(LocationMaster.device_id).get()

        next_trolley = query['device_id']
        next_trolley_name = query['name']
        system_id = query['system_id']
        next_trolley_seq = query['trolley_seq']
        logger.info("db_get_next_trolley Input {} {} and output {} {} {}".format(batch_id, device_id, next_trolley,
                                                                                  system_id, next_trolley_name))
        return next_trolley, system_id, next_trolley_name, next_trolley_seq

    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return None, None, None, None

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_trolley_analysis_ids(batch_id, trolley_id):
    """
    returns analysis_ids for user's upcoming trolley
    :param batch_id: int
    :param trolley_id: int
    :return: list
    """
    mfs_system_mapping = dict()
    dest_devices = set()
    DeviceMasterAlias = DeviceMaster.alias()
    batch_system = None

    try:
        query = MfdAnalysis.select(MfdAnalysis.id.alias('mfd_analysis_id'),
                                   DeviceMaster.id.alias('trolley_id'),
                                   DeviceMaster.name.alias('trolley_name'),
                                   DeviceMasterAlias.system_id.alias('mfs_system_id'),
                                   BatchMaster.system_id,
                                   MfdAnalysis).dicts() \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .join(LocationMaster, on=LocationMaster.id == MfdAnalysis.trolley_location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == MfdAnalysis.mfs_device_id) \
            .where(BatchMaster.status.not_in(settings.BATCH_PROCESSING_DONE_LIST),
                   MfdAnalysis.batch_id == batch_id,
                   DeviceMaster.id == trolley_id,
                   MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_DROPPED_STATUS,
                                                 constants.MFD_CANISTER_SKIPPED_STATUS,
                                                 constants.MFD_CANISTER_MVS_FILLING_REQUIRED,
                                                 constants.MFD_CANISTER_MVS_FILLED_STATUS,
                                                 constants.MFD_CANISTER_RTS_REQUIRED_STATUS,
                                                 constants.MFD_CANISTER_RTS_DONE_STATUS])) \
            .order_by(MfdAnalysis.order_no) \
            .limit(160)
        analysis_id_list = list()

        for record in query:
            if trolley_id == record['trolley_id']:
                mfs_system_mapping[record['mfs_device_id']] = record['mfs_system_id']
                dest_devices.add(record['dest_device_id'])
                analysis_id_list.append(record['mfd_analysis_id'])
                batch_system = record['system_id']
            else:
                break
        logger.info('get_trolley_analysis_ids Input: {} {} and Output {} {} {} {}'.format(
            batch_id, trolley_id, analysis_id_list, mfs_system_mapping, list(dest_devices), batch_system))
        return analysis_id_list, mfs_system_mapping, list(dest_devices), batch_system
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_canister_transfer_info(company_id: int, filter_fields: dict, sort_fields: list, paginate: dict,
                                  clauses: list or None = None):
    """
    Function to get mfd canister info
    @param company_id: int
    @param filter_fields: dict
    @param sort_fields: list
    @param paginate: dict
    @param clauses: list
    @return: query results, count, paginate data
    """
    if clauses is None:
        clauses = list()

    clauses.append((MfdCanisterMaster.company_id == company_id))
    clauses.append((MfdCanisterMaster.rfid.is_null(False)))

    global_search = [MfdCanisterMaster.id]

    exact_search_list = ["location_id"]
    like_search_list = ["patient_name", "facility_name", "drug_name"]
    left_like_search_list = ["mfd_canister_id"]
    membership_search_list = ["home_cart_name", "source_device_name", "dest_device_name", "status", "last_used_by",
                              "state_status"]

    if "ndc" in filter_fields and filter_fields["ndc"]:
        ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
            {"scanned_ndc": filter_fields['ndc'],
             "required_entity": "ndc"})
        if ndc_list:
            formatted_ndc_list = list(map(lambda x: x[:9], ndc_list))
            filter_fields["ndc"] = formatted_ndc_list
            membership_search_list.append('ndc')
        else:
            filter_fields["ndc"] = filter_fields["ndc"][:9]
            like_search_list.append('ndc')

    if filter_fields and filter_fields.get('global_search', None) is not None:
        multi_search_string = filter_fields['global_search'].split(',')
        multi_search_string.remove('') if '' in multi_search_string else multi_search_string
        mfd_canister_ids = get_mfd_canister_from_pack(multi_search_string)
        if mfd_canister_ids:
            or_clause = [MfdCanisterMaster.id << mfd_canister_ids]
            clauses = get_multi_search(clauses, multi_search_string, global_search, or_search_field=or_clause)
        else:
            clauses = get_multi_search(clauses, multi_search_string, global_search)

    if filter_fields and filter_fields.get('state_status', None) is not None:
        state_status_filter = filter_fields['state_status']
        state_status_list = list()
        for status in state_status_filter:
            state_status_list.extend(constants.MFD_STATE_FILTERS_LIST[status])
        if state_status_list:
            filter_fields['state_status'] = state_status_list
        else:
            return [], 0
    if filter_fields and filter_fields.get('pack_display_id', None) is not None:
        mfd_canister_ids = get_mfd_canister_from_pack([str(filter_fields['pack_display_id'])], left_search=True)
        if mfd_canister_ids:
            clauses.append((MfdCanisterMaster.id << mfd_canister_ids))
        else:
            return [], 0

    mfd_sort_fields = None
    if sort_fields:
        for data in sort_fields:
            if "drug_full_name" in data or "ndc" in data or "quantity" in data:
                mfd_sort_fields = sort_fields
                sort_fields = None
        else:
            sort_fields = sort_fields
    try:
        results, count = get_mfd_canisters_query(filter_fields, sort_fields, clauses, paginate, exact_search_list,
                                                 like_search_list, membership_search_list,
                                                 left_like_search_list)

        for record in results:
            if record['canister_status']:
                record['canister_status_code'] = constants.USER_MFD_CANISTER_STATUS[record['canister_status']]
                if record['canister_status'] in [constants.MFD_CANISTER_PENDING_STATUS,
                                                 constants.MFD_CANISTER_IN_PROGRESS_STATUS]:
                    record['content_available'] = False
                else:
                    record['content_available'] = True
            else:
                record['canister_status_code'] = None
                record['content_available'] = False
            if record['drug_status']:
                record['drug_status'] = list(map(int, record['drug_status'].split(',')))
            # uncomment below code once FE has changes.
            # if record['state_status']:
            #     record['state_status'] = constants.MFD_STATE_LIST[record['state_status']]
            record['drug_data'] = get_mfd_canister_data(mfd_analysis_id=record['mfd_analysis_id'],
                                                        sort_fields=mfd_sort_fields,
                                                        drug_status=[constants.MFD_DRUG_FILLED_STATUS,
                                                                     constants.MFD_DRUG_RTS_REQUIRED_STATUS])

        return results, count

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def check_trolley_seq_for_batch(trolley_seq,batch_id):
    try:
        logger.info(f"In check_trolley_seq_for_batch")
        min_analysis_id = MfdAnalysis.db_get_min_analysis_id(batch_id, trolley_seq)
        if not min_analysis_id:
            return False
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(f"Error in check_trolley_seq_for_batch, e: {e}")
        logger.error(e, exc_info=True)
        raise e

@log_args_and_response
def db_get_rts_required_canisters(company_id: int, filter_fields: dict, sort_fields: list, paginate: dict,
                                  clauses: list or None = None, trolley_seq: int or None = None,
                                  batch_id: int or None = None, skip_misplaced_rts: bool = False):
    """
    Function to get mfd canister that requires rts
    @param company_id: int
    @param filter_fields: dict
    @param sort_fields: list
    @param paginate: dict
    @param clauses: list
    @param trolley_seq: int
    @param batch_id: int
    @param skip_misplaced_rts: bool
    @return: query results, count
    """
    if clauses is None:
        clauses = list()

    if trolley_seq and batch_id:
        # here seq for every batch starts from 1 but order_no is unique across the table. So instead of directly using
        # seq used order number
        min_order_number = get_min_order_from_batch_trolley(batch_id, trolley_seq)
        if not min_order_number:
            raise ValueError('Invalid data for rts')
        clauses.append((MfdAnalysis.order_no < min_order_number))
    clauses.append((MfdCanisterMaster.rfid.is_null(False)))
    clauses.append((MfdCanisterMaster.company_id == company_id))
    if skip_misplaced_rts:
        clauses.append((MfdCanisterMaster.state_status << [constants.MFD_CANISTER_ACTIVE]))

    exact_search_list = ['home_cart_id']

    like_search_list = []
    left_like_search_list = ["mfd_canister_id", "drug_name"]
    membership_search_list = ["source_device_id", "reason_to_return", "state_status"]

    if filter_fields and filter_fields.get('state_status', None) is not None:
        state_status_filter = filter_fields['state_status']
        state_status_list = list()
        for status in state_status_filter:
            state_status_list.extend(constants.MFD_STATE_FILTERS_LIST[status])
        if state_status_list:
            filter_fields['state_status'] = state_status_list
        else:
            return [], 0

    if "ndc" in filter_fields and filter_fields["ndc"]:
        ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(
            {"scanned_ndc": filter_fields['ndc'],
             "required_entity": "ndc"})
        if ndc_list:
            formatted_ndc_list = list(map(lambda x: x[:9], ndc_list))
            filter_fields["ndc"] = formatted_ndc_list
            membership_search_list.append('ndc')
        else:
            filter_fields["ndc"] = filter_fields["ndc"][:9]
            like_search_list.append('ndc')

    if filter_fields and filter_fields.get('global_search', None) is not None:
        string_search_field = [
            DrugMaster.ndc,
            MfdCanisterMaster.id,
            DrugMaster.concated_drug_name_field()
        ]
        multi_search_string = filter_fields['global_search'].split(',')
        multi_search_string.remove('') if '' in multi_search_string else multi_search_string
        clauses = get_multi_search_with_drug_scan(clauses, multi_search_values=multi_search_string,
                                                  model_search_fields=string_search_field,
                                                  ndc_search_field=DrugMaster.ndc)
    mfd_sort_fields = None
    if sort_fields:
        for data in sort_fields:
            if "drug_full_name" in data or "ndc" in data or "quantity" in data:
                mfd_sort_fields = sort_fields
                sort_fields = None
        else:
            sort_fields = sort_fields

    try:
        results, count = db_get_rts_required_canisters_query(filter_fields, sort_fields,
                                                             paginate, clauses, exact_search_list=exact_search_list,
                                                             like_search_list=like_search_list,
                                                             left_like_search_list=left_like_search_list,
                                                             membership_search_list=membership_search_list)
        # To return the whole canister data when the canister is filtered drug based
        for record in results:
            record['drug_data'] = get_mfd_canister_data(mfd_analysis_id=record['mfd_analysis_id'],
                                                        sort_fields=mfd_sort_fields,
                                                        drug_status=[constants.MFD_DRUG_RTS_REQUIRED_STATUS])
        return results, count

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_mfd_canister_master_filled_canister_details(batch_id):
    """
    @return: query results
    """
    try:
        subquery = ""

        if batch_id:
            subquery = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id')) \
            .join(MfdAnalysis, on=MfdCanisterMaster.id == MfdAnalysis.mfd_canister_id) \
            .where(MfdAnalysis.batch_id << batch_id)

        query = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id'),
                                         MfdCanisterMaster.home_cart_id.alias('mfd_canister_home_cart_id'),
                                         LocationMaster.device_id.alias('mfd_canister_device_id'),
                                         MfdCanisterMaster.location_id.alias('mfd_canister_location_id'),
                                         ContainerMaster.drawer_level.alias('drawer_level')) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id).where(((LocationMaster.device_id.between(13, 22) &
                                                                                        ContainerMaster.drawer_level << (
                                                                                                        5, 6, 7, 8))
                                                                                       | LocationMaster.device_id.between(2,7)
                                                                                       | (MfdCanisterMaster.location_id.is_null(True) &
                                                                                          MfdCanisterMaster.home_cart_id.is_null(False))))

        if subquery:
            query = query.where(MfdCanisterMaster.id.not_in(subquery))

        mfd_canister_details_list = list()

        for record in query.dicts():
            mfd_canister_details_list.append(record)

        return mfd_canister_details_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_mfd_canister_master_filled_canister_details_by_mfd_cart_device_id(mfd_cart_device_id):
    """
    @return: query results
    """
    try:
        query = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id'),
                                         MfdCanisterMaster.home_cart_id.alias('mfd_canister_home_cart_id'),
                                         LocationMaster.device_id.alias('mfd_canister_device_id'),
                                         MfdCanisterMaster.location_id.alias('mfd_canister_location_id'),
                                         ContainerMaster.drawer_level.alias('drawer_level')) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id)\
            .where(((LocationMaster.device_id == mfd_cart_device_id) & (ContainerMaster.drawer_level << (5, 6, 7, 8)))
            | ((LocationMaster.device_id != mfd_cart_device_id) & (MfdCanisterMaster.home_cart_id == mfd_cart_device_id)))

        mfd_canister_details_list = list()

        for record in query.dicts():
            mfd_canister_details_list.append(record)

        return mfd_canister_details_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_mfd_canister_master_empty_canister_details(source_device_id):
    """
    @return: query results
    """
    try:
        query = MfdCanisterMaster.select(MfdCanisterMaster.id.alias('mfd_canister_id'),
                                         MfdCanisterMaster.rfid.alias('source_canister_rfid')) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=MfdCanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where((LocationMaster.device_id == source_device_id) & (ContainerMaster.drawer_level << (1, 2, 3, 4)))

        mfd_canister_details_list = list()

        for record in query.dicts():
            mfd_canister_details_list.append(record)

        return mfd_canister_details_list

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_last_mfd_sequence_for_batch(batch_id):
    max_trolley = 0
    try:
        max_trolley_seq = MfdAnalysis.select(fn.MAX(MfdAnalysis.trolley_seq)).where(
            MfdAnalysis.batch_id == batch_id).scalar()

        if max_trolley_seq:
            return max_trolley_seq
        return max_trolley
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except (DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return max_trolley


@log_args_and_response
def db_get_last_mfd_progress_sequence_for_batch(batch_id):
    max_trolley = 0
    try:
        max_trolley_seq = MfdAnalysis.select(fn.MAX(MfdAnalysis.trolley_seq)).where(
            MfdAnalysis.batch_id == batch_id, MfdAnalysis.status_id == constants.MFD_CANISTER_IN_PROGRESS_STATUS).scalar()

        if max_trolley_seq:
            return max_trolley_seq
        return max_trolley
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return max_trolley


@log_args_and_response
def db_check_mfd_filling_for_batch(batch_id):
    not_pending_trolley = 0
    try:
        query = MfdAnalysis.select(MfdAnalysis.trolley_seq, MfdAnalysis.status_id).dicts().where(
            MfdAnalysis.batch_id == batch_id, MfdAnalysis.status_id.not_in([constants.MFD_CANISTER_PENDING_STATUS])).group_by(
            MfdAnalysis.trolley_seq)

        for record in query:
            not_pending_trolley = MfdAnalysis.trolley_seq

        return not_pending_trolley
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_batch_id_from_analysis_ids(analysis_ids):
    try:
        query = MfdAnalysis.select(MfdAnalysis.batch_id)\
                            .where(MfdAnalysis.id << analysis_ids) \
                            .group_by(MfdAnalysis.batch_id)
        for record in query.dicts():
            return record['batch_id']
        return None
    except (InternalError, IntegrityError) as e:
        logger.error(f"Error in db_get_device_id_from_analysis_ids, e: {e}")
        logger.error(e, exc_info=True)
        raise e

