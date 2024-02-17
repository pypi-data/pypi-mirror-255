from collections import OrderedDict

from coverage.annotate import os
from peewee import *
from datetime import date, datetime, timedelta
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, log_args
from src.model.model_pack_details import PackDetails
from src import constants
from src.api_utility import get_orders
from src.exceptions import NoLocationExists
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_history import CanisterHistory
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_status_history import CanisterStatusHistory
from src.model.model_canister_status_history_comment import CanisterStatusHistoryComment
from src.model.model_canister_transfer_cycle_history import CanisterTransferCycleHistory
from src.model.model_canister_transfer_history_comment import CanisterTransferHistoryComment
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_canister_tx_meta import CanisterTxMeta
from src.model.model_container_master import ContainerMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_location_master import LocationMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_slot_details import SlotDetails
from src.model.model_unique_drug import UniqueDrug
from src.model.model_zone_master import ZoneMaster

logger = settings.logger


@log_args_and_response
def db_update_canister_transfers(batch_id: int,
                                 canister_transfers: dict,
                                 canister_csr_destination_location: dict,
                                 canister_cycle_id_dict: dict,
                                 cycle_device_dict: dict,
                                 cycle_device_info_dict: dict):
    """

    @param batch_id:
    @param canister_transfers:
    @param canister_csr_destination_location:
    @param canister_cycle_id_dict:
    @param cycle_device_dict:
    @param cycle_device_info_dict:
    @return:
    """
    if int(os.environ["IS_RUNNING_RECOMMENDCANISTERTRANSFER_API"]) != 1:
        return False, "Update fail. Already updating in other session"
    try:
        logger.info("Transfers {}".format(canister_transfers))
        cycle_device_meta_id = dict()
        for cycle, device_list in cycle_device_dict.items():
            cycle_device_meta_id[cycle] = dict()
            for device in device_list:
                if int(cycle_device_info_dict[cycle][device][
                                   "to_cart_transfer_count"]) == 0:
                    status_id = constants.CANISTER_TRANSFER_TO_TROLLEY_DONE
                else:
                    status_id = constants.CANISTER_TRANSFER_RECOMMENDATION_DONE

                create_dict = {'cycle_id': cycle,
                               'device_id': device,
                               'batch_id': batch_id,
                               'status_id': status_id,
                               'to_cart_transfer_count': cycle_device_info_dict[cycle][device][
                                   "to_cart_transfer_count"],
                               'from_cart_transfer_count': cycle_device_info_dict[cycle][device][
                                   "from_cart_transfer_count"],
                               'normal_cart_count': len(cycle_device_info_dict[cycle][device]["normal_cart_count"]),
                               'elevator_cart_count': len(cycle_device_info_dict[cycle][device]["elevator_cart_count"])
                               }
                canister_tx_meta_data = {'created_date': get_current_date_time(),
                                         'modified_date': get_current_date_time()
                                         }

                meta_update_status = CanisterTxMeta.db_update_or_create(create_dict=create_dict,
                                                                        update_dict=canister_tx_meta_data)

                cycle_device_meta_id[cycle][device] = meta_update_status.id
                logger.info("meta update status for device and cycle {}, {}, {}".format(device,
                                                                                        cycle,
                                                                                        meta_update_status.id))

        for canister_id, transfer_data in canister_transfers.items():
            cycle_id = canister_cycle_id_dict[canister_id]
            dest_device = transfer_data[1]
            source_device = transfer_data[4]
            to_ct_meta_id = cycle_device_meta_id[cycle_id][source_device]
            from_ct_meta_id = cycle_device_meta_id[cycle_id][dest_device]

            create_dict = {'canister_id': canister_id,
                           'batch_id': batch_id}

            update_dict = {'dest_device_id': dest_device,
                           'dest_quadrant': transfer_data[2],
                           'trolley_loc_id': transfer_data[0][0],
                           'to_ct_meta_id': to_ct_meta_id,
                           'from_ct_meta_id': from_ct_meta_id,
                           'transfer_status': constants.CANISTER_TX_PENDING,
                           'modified_date': get_current_date_time()}

            if canister_id in canister_csr_destination_location.keys():
                if canister_csr_destination_location[canister_id]:
                    loc_number, device, drawer_level = canister_csr_destination_location[canister_id]
                    update_dict['dest_location_number'] = int(loc_number)
                else:
                    update_dict['dest_location_number'] = None
            logger.info("query update response update_dict {}".format(update_dict))
            query = CanisterTransfers.db_update_or_create(create_dict=create_dict, update_dict=update_dict)
            logger.info("In db_update_canister_transfers: canister transfer data updated: {}".format(query))
        return True, list(cycle_device_dict.keys())
    except(InternalError, IntegrityError) as e:
        logger.error("error in db_update_canister_transfers {}".format(e))
        return False, e
    except Exception as e:
        logger.error("error in db_update_canister_transfers {}".format(e))
        return False, "Update fail"


# @log_args_and_response
# def update_canister_transfer_skipped(canister_id: int, guided_tx_cycle_id: int) -> bool:
#     """
#     This method changes the status to guided skipped for provided canister id in the GuidedTracker table
#     @param canister_id: int
#     @param guided_tx_cycle_id: int
#     """
#     try:
#         update_canister_status_query = None
#         logger.info("In update_canister_transfer_skipped")
#         validate_canister_id = GuidedTracker.select(fn.IF(GuidedTracker.alt_can_replenish_required.is_null(False),
#                                                           GuidedTracker.alternate_canister_id,
#                                                           GuidedTracker.source_canister_id).alias(
#             "canister_id")).dicts() \
#             .where(GuidedTracker.id == guided_tx_cycle_id)
#         if validate_canister_id.count() == 1:
#             for record in validate_canister_id:
#                 if record['canister_id'] == canister_id:
#                     update_canister_status_query = GuidedTracker.update(
#                         transfer_status=constants.GUIDED_TRACKER_SKIPPED,
#                     modified_date = get_current_date_time()).where(
#                         GuidedTracker.id == guided_tx_cycle_id).execute()
#                     logger.info(update_canister_status_query)
#                 else:
#                     return False
#         if update_canister_status_query == 1:
#             return True
#         else:
#             return False
#
#     except (InternalError, IntegrityError, DataError) as e:
#         logger.error("error in update_replenish_based_on_system {}".format(e))
#         raise


@log_args_and_response
def get_trolley_to_transfer_canisters_to_trolley(batch_id: int, transfer_cycle_id: int, source_device_id: int,
                                                 from_app: bool) -> list:
    """
    Returns list of transfer trolleys for canisters to be transferred from robot to trolley for particular batch
    @param from_app:
    @param batch_id:
    @param transfer_cycle_id:
    @param source_device_id:
    @return:
    """
    try:
        logger.info("in get_trolley_to_transfer_canisters_to_trolley")
        results = list()
        # DeviceMasterAlias = DeviceMaster.alias()
        LocationMasterAlias = LocationMaster.alias()
        query = CanisterTxMeta.select(
            fn.DISTINCT(LocationMasterAlias.device_id).alias('trolley_id'),
            CanisterTransfers.dest_quadrant,
            CanisterTransfers.dest_device_id,
            LocationMaster.device_id,
            LocationMaster.quadrant,
            DeviceMaster.name.alias('trolley_name'),
            DeviceMaster.associated_device,
            DeviceMaster.serial_number,
            DeviceMaster.device_type_id,
            DeviceTypeMaster.device_type_name,
            UniqueDrug.is_delicate
        ) \
            .join(CanisterTransfers, on=CanisterTxMeta.id == CanisterTransfers.to_ct_meta_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=(LocationMaster.id == CanisterMaster.location_id)) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == CanisterTransfers.trolley_loc_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .where(CanisterTransfers.batch_id == batch_id,
                   CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.device_id == source_device_id,
                   CanisterTransfers.batch_id == batch_id,
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_DONE,
                                                             constants.CANISTER_TX_TO_TROLLEY_ALTERNATE_TRANSFER_LATER,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                             constants.CANISTER_TX_TO_TROLLEY_TRANSFERRED_MANUALLY]),
                   CanisterTxMeta.status_id == constants.CANISTER_TRANSFER_RECOMMENDATION_DONE,
                   CanisterTransfers.trolley_loc_id.is_null(False),
                   # (fn.CONCAT(fn.IFNULL(CanisterTransfers.dest_device_id, 0), '_',
                   #            fn.IFNULL(CanisterTransfers.dest_quadrant, 0)) !=
                   #  fn.CONCAT(fn.IFNULL(LocationMaster.device_id, 0), '_',
                   #            fn.IFNULL(LocationMaster.quadrant, 0)))
                   ) \
            .group_by(LocationMasterAlias.device_id) \
            .order_by(LocationMasterAlias.container_id)

        for record in query.dicts():
            # if record['dest_device_id'] == record['device_id'] and record['dest_quadrant'] == record['quadrant']:
            #     if not record['is_delicate']:
            #         continue
            if from_app:
                drawer_data = get_trolley_drawers_data_for_to_trolley_tx(batch_id=batch_id,
                                                                         transfer_cycle_id=transfer_cycle_id,
                                                                         source_device_id=source_device_id,
                                                                         dest_trolley_id=record['trolley_id'])
            else:
                drawer_data = ContainerMaster.get_drawer_data_for_device(record['trolley_id'])
            record['drawer_list'] = drawer_data
            del record['is_delicate']
            results.append(record)
        return results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_trolley_to_transfer_canisters_to_trolley {}".format(e))
        raise


@log_args_and_response
def db_replace_canister_in_canister_transfers(batch_id, canister_id, alt_canister_id):
    try:
        return CanisterTransfers.db_replace_canister(batch_id=batch_id, canister_id=canister_id,
                                                     alt_canister_id=alt_canister_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_replace_canister_in_canister_transfers {}".format(e))
        raise


def get_pending_devices_to_trolleys(batch_id: int, transfer_cycle_id: int, current_device: int) -> list:
    """
    Returns list of pending transfers
    @param current_device:
    @param batch_id:
    @param transfer_cycle_id:
    @return:
    """
    try:
        results = list()
        DeviceMasterAlias = DeviceMaster.alias()
        LocationMasterAlias = LocationMaster.alias()
        query = CanisterTxMeta.select(
            DeviceMasterAlias.name.alias('pending_device_name'),
            LocationMaster.device_id,
            CanisterTransfers.dest_device_id,
            CanisterTransfers.dest_quadrant,
            DeviceMaster.associated_device,
            DeviceMasterAlias.device_type_id
        ) \
            .join(CanisterTransfers, on=CanisterTxMeta.id == CanisterTransfers.to_ct_meta_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == CanisterTransfers.trolley_loc_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .where(CanisterTransfers.batch_id == batch_id,
                   CanisterTransfers.trolley_loc_id.is_null(False),
                   CanisterMaster.active == settings.is_canister_active,
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_DONE,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                             constants.CANISTER_TX_TO_TROLLEY_TRANSFERRED_MANUALLY]),
                   CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.status_id == constants.CANISTER_TRANSFER_RECOMMENDATION_DONE,
                   CanisterTxMeta.device_id != current_device,
                   (fn.CONCAT(fn.IFNULL(CanisterTransfers.dest_device_id, 0), '_',
                              fn.IFNULL(CanisterTransfers.dest_quadrant, 0)) !=
                    fn.CONCAT(fn.IFNULL(LocationMaster.device_id, 0), '_',
                              fn.IFNULL(LocationMaster.quadrant, 0))),
                   DeviceMasterAlias.device_type_id.not_in([settings.DEVICE_TYPES['Canister Transfer Cart'],
                                                            settings.DEVICE_TYPES['Canister Cart w/ Elevator']])) \
            .group_by(LocationMaster.device_id)
        for record in query.dicts():
            results.append(record)
        return results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pending_devices_to_trolleys {}".format(e))
        raise


@log_args_and_response
def get_trolley_drawers_data_for_to_trolley_tx(batch_id: int, transfer_cycle_id: int, source_device_id: int,
                                               dest_trolley_id: int):
    """
    Returns list of trolley drawers for given batch ID, device_id and trolley_id
    """
    try:
        results = list()
        drawer_list = list()
        LocationMasterAlias = LocationMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()

        query = CanisterTxMeta.select(
            CanisterTransfers.canister_id,
            ContainerMaster.drawer_name.alias('drawer_name'),
            ContainerMaster.device_id.alias('source_device_id'),
            LocationMaster.quadrant.alias('source_quadrant'),
            LocationMaster.container_id.alias('source_drawer_id'),
            LocationMaster.display_location.alias('source_display_location'),
            ContainerMasterAlias.device_id.alias('trolley_id'),
            ContainerMasterAlias.id.alias('trolley_drawer_id'),
            ContainerMasterAlias.drawer_name.alias('trolley_drawer_name'),
            ContainerMasterAlias.drawer_level.alias("trolley_drawer_level"),
            ContainerMasterAlias.serial_number,
            ContainerMasterAlias.shelf.alias("trolley_shelf"),
            fn.replace(ContainerMasterAlias.drawer_name, '-', '').alias('trolley_drawer_number')
        ) \
            .join(CanisterTransfers, on=CanisterTxMeta.id == CanisterTransfers.to_ct_meta_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(LocationMasterAlias, on=CanisterTransfers.trolley_loc_id == LocationMasterAlias.id) \
            .join(ContainerMasterAlias, on=ContainerMasterAlias.id == LocationMasterAlias.container_id) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_ALTERNATE_TRANSFER_LATER,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                             constants.CANISTER_TX_TO_TROLLEY_TRANSFERRED_MANUALLY]),
                   CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.device_id == source_device_id,
                   CanisterTxMeta.status_id == constants.CANISTER_TRANSFER_RECOMMENDATION_DONE,
                   ContainerMasterAlias.device_id == dest_trolley_id) \
            .order_by(ContainerMasterAlias.id)

        for record in query.dicts():
            if record['source_device_id'] == dest_trolley_id:
                continue
            if record["trolley_drawer_id"] not in drawer_list:
                drawer_list.append(record["trolley_drawer_id"])
                data = {"trolley_drawer_id": record["trolley_drawer_id"],
                        "serial_number": record["serial_number"],
                        "drawer_level": record["trolley_drawer_level"],
                        "shelf": record["trolley_shelf"],
                        "trolley_drawer_number": record["trolley_drawer_number"],
                        "drawer_name": record["trolley_drawer_name"]
                        }

                if not len(results):
                    data["drawer_to_highlight"] = True
                else:
                    data["drawer_to_highlight"] = False
                results.append(data)

        return results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_trolley_drawers_data_for_to_trolley_tx {}".format(e))
        raise


@log_args_and_response
def get_canisters_to_be_transferred_to_trolley(batch_id: int, source_device_id: int, dest_trolley_drawer_id: int,
                                               sort_fields: list, transfer_cycle_id: int) -> tuple:
    """
        Returns list of canisters to be transfer to particular drawer of given trolley from specified device for particular batch
    @param transfer_cycle_id:
    @param batch_id:
    @param source_device_id:
    @param dest_trolley_drawer_id:
    @param sort_fields:
    @return:
    """
    try:
        order_list = list()
        fields_dict = {

            "source_drawer_number": ContainerMaster.drawer_name

        }
        order_list = get_orders(order_list, fields_dict, sort_fields)
        order_list.append(UniqueDrug.is_delicate.desc())
        order_list.append(LocationMaster.location_number)
        transfer_data = list()
        drawers_to_unlock = dict()
        delicate_drawers_to_unlock = dict()
        DeviceMasterAlias = DeviceMaster.alias()
        LocationMasterAlias = LocationMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()

        query = CanisterTxMeta.select(
            CanisterTransfers.canister_id,
            fn.IF(
                CanisterMaster.expiry_date <= date.today() + timedelta(
                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                constants.EXPIRED_CANISTER,
                fn.IF(
                    CanisterMaster.expiry_date <= date.today() + timedelta(
                        settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                    constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
            DrugMaster.id.alias('drug_id'),
            DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.ndc,
            DrugMaster.image_name,
            DrugMaster.shape.alias("drug_shape"),
            DrugMaster.imprint,
            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
            fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by).alias(
                "stock_updated_by"),
            CustomDrugShape.id,
            CustomDrugShape.name,
            ContainerMaster.device_id.alias('source_device_id'),
            LocationMaster.quadrant.alias('source_quadrant'),
            LocationMaster.container_id.alias('source_drawer_id'),
            DeviceMaster.name.alias("source_device_name"),
            fn.replace(ContainerMaster.drawer_name, '-', '').alias('source_drawer_number'),
            ContainerMaster.drawer_name,
            ContainerMaster.serial_number.alias("source_drawer_serial_number"),
            ContainerMaster.ip_address.alias("source_drawer_ip"),
            ContainerMaster.secondary_ip_address.alias("source_drawer_sec_ip"),
            LocationMaster.location_number.alias('source_location_number'),
            LocationMaster.display_location.alias('source_display_location'),
            ContainerMasterAlias.device_id.alias('trolley_id'),
            ContainerMasterAlias.id.alias('trolley_drawer_id'),
            ContainerMaster.serial_number,
            ContainerMasterAlias.drawer_name.alias('trolley_drawer_number'),
            CanisterTransfers.dest_device_id,
            DeviceMasterAlias.device_type_id.alias('dest_device_type_id'),
            CanisterTransfers.dest_quadrant,
            CanisterTransfers.dest_location_number,
            CanisterTransfers.transfer_status,
            ContainerMaster.shelf,
            DeviceMaster.device_type_id,
            DrugDetails.last_seen_by,
            DrugDetails.last_seen_date,
            UniqueDrug.is_delicate.alias('is_delicate')
        ) \
            .join(CanisterTransfers, on=CanisterTxMeta.id == CanisterTransfers.to_ct_meta_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == CanisterTransfers.dest_device_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER,
                  on=((DrugMaster.id == DrugStockHistory.unique_drug_id) & (DrugStockHistory.is_active == 1)
                      & (DrugStockHistory.company_id == CanisterMaster.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                   (DrugDetails.company_id == CanisterMaster.company_id)) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(LocationMasterAlias, on=CanisterTransfers.trolley_loc_id == LocationMasterAlias.id) \
            .join(ContainerMasterAlias, on=ContainerMasterAlias.id == LocationMasterAlias.container_id) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.device_id == source_device_id,
                   CanisterTxMeta.status_id == constants.CANISTER_TRANSFER_RECOMMENDATION_DONE,
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                             constants.CANISTER_TX_TO_TROLLEY_ALTERNATE_TRANSFER_LATER,
                                                             constants.CANISTER_TX_TO_TROLLEY_TRANSFERRED_MANUALLY]),
                   ContainerMasterAlias.id == dest_trolley_drawer_id)

        if order_list:
            query = query.order_by(*order_list)
        ndc_list = []

        for record in query.dicts():
            if record['source_drawer_id'] == dest_trolley_drawer_id:
                continue
            if record['source_device_id'] != source_device_id:
                record["wrong_location"] = True
                record['current_device'] = record['source_device_id']
                record['current_display_location'] = record['source_display_location']
                record['current_device_name'] = record['source_device_name']

            else:
                record["wrong_location"] = False

            if record['transfer_status'] == constants.CANISTER_TX_TO_TROLLEY_ALTERNATE:
                record['alternate_canister'] = True
            else:
                record['alternate_canister'] = False

            transfer_data.append(record)
            ndc_list.append(int(record['ndc']))

            if record['is_delicate']:
                if record["drawer_name"] not in delicate_drawers_to_unlock.keys():
                    delicate_drawers_to_unlock[record["drawer_name"]] = {"id": record["source_drawer_id"],
                                                                "drawer_name": record["drawer_name"],
                                                                "serial_number": record["source_drawer_serial_number"],
                                                                "device_ip_address": record["source_drawer_ip"],
                                                                "ip_address": record["source_drawer_ip"],
                                                                "secondary_ip_address": record["source_drawer_sec_ip"],
                                                                "from_device": list(),
                                                                "to_device": list(),
                                                                "shelf": record["shelf"],
                                                                "device_type_id": record["device_type_id"]
                                                                }
                delicate_drawers_to_unlock[record["drawer_name"]]["from_device"].append(record["source_display_location"])
            else:

                if record["drawer_name"] not in drawers_to_unlock.keys():
                    drawers_to_unlock[record["drawer_name"]] = {"id": record["source_drawer_id"],
                                                                "drawer_name": record["drawer_name"],
                                                                "serial_number": record["source_drawer_serial_number"],
                                                                "device_ip_address": record["source_drawer_ip"],
                                                                "ip_address": record["source_drawer_ip"],
                                                                "secondary_ip_address": record["source_drawer_sec_ip"],
                                                                "from_device": list(),
                                                                "to_device": list(),
                                                                "shelf": record["shelf"],
                                                                "device_type_id": record["device_type_id"]
                                                                }

                drawers_to_unlock[record["drawer_name"]]["from_device"].append(record["source_display_location"])

        return transfer_data, drawers_to_unlock, delicate_drawers_to_unlock, ndc_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canisters_to_be_transferred_to_trolley {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_canisters_to_be_transferred_to_trolley, {}".format(e))
        raise


@log_args_and_response
def get_trolley_to_transfer_canisters_from_trolley(batch_id: int, transfer_cycle_id: int, dest_device_id: int,
                                                   from_app: bool) -> list:
    """
    Returns list of transfer trolleys for canisters to be transferred from trolley to robot/csr for particular batch
    @param from_app:
    @param dest_device_id:
    @param batch_id:
    @param transfer_cycle_id:
    @return:
    """
    try:
        results = list()
        ContainerMasterAlias = ContainerMaster.alias()
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        order_list = []

        query = CanisterTxMeta.select(
            LocationMasterAlias.device_id.alias('trolley_id'),
            CanisterTransfers.dest_quadrant,
            CanisterTransfers.dest_device_id,
            LocationMaster.device_id,
            LocationMaster.quadrant,
            DeviceMaster.name.alias('trolley_name'),
            DeviceMaster.associated_device,
            DeviceMaster.serial_number,
            DeviceMaster.device_type_id.alias('device_type_id'),
            DeviceTypeMaster.device_type_name,
            CanisterMaster.canister_type,
            ContainerMasterAlias.drawer_type.alias("current_drawer_type"),
            DeviceMasterAlias.device_type_id.alias("current_device_type_id")
        ) \
            .join(CanisterTransfers, on=CanisterTxMeta.id == CanisterTransfers.from_ct_meta_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=(LocationMaster.id == CanisterMaster.location_id)) \
            .join(ContainerMasterAlias, JOIN_LEFT_OUTER, on=ContainerMasterAlias.id == LocationMaster.container_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == ContainerMasterAlias.device_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == CanisterTransfers.trolley_loc_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.device_id == dest_device_id,
                   CanisterTxMeta.status_id.not_in([constants.CANISTER_TRANSFER_TO_ROBOT_DONE,
                                                    constants.CANISTER_TRANSFER_TO_CSR_DONE]),
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_ROBOT_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                             constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_LATER,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                             constants.CANISTER_TX_TO_ROBOT_SKIPPED_AND_ALTERNATE]),
                   CanisterTransfers.trolley_loc_id.is_null(False),
                   CanisterTransfers.batch_id == batch_id,
                   fn.IF((fn.CONCAT(fn.IFNULL(CanisterTransfers.dest_device_id, 0), '_',
                                    fn.IFNULL(CanisterTransfers.dest_quadrant, 0)) !=
                          fn.CONCAT(fn.IFNULL(LocationMaster.device_id, 0), '_',
                                    fn.IFNULL(LocationMaster.quadrant, 0))), True,
                         (fn.IF(CanisterMaster.canister_type == settings.SIZE_OR_TYPE["BIG"],
                                ContainerMasterAlias.drawer_type == settings.SIZE_OR_TYPE["SMALL"], False)))
                   ) \
            .group_by(LocationMasterAlias.device_id)

        order_list.append(SQL('FIELD(device_type_id, {})'.format(settings.DEVICE_TYPES['Canister Cart w/ Elevator']))
                          .desc())
        order_list.append(LocationMasterAlias.container_id)
        query = query.order_by(*order_list)

        for record in query.dicts():
            if from_app:
                drawer_data = get_trolley_drawers_from_trolley_tx(batch_id=batch_id,
                                                                  destination_device_id=dest_device_id,
                                                                  source_trolley_id=record['trolley_id'],
                                                                  transfer_cycle_id=transfer_cycle_id)
            else:
                drawer_data = ContainerMaster.get_drawer_data_for_device(record['trolley_id'])
            record['drawer_list'] = drawer_data
            results.append(record)
        return results
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_trolley_to_transfer_canisters_from_trolley {}".format(e))
        raise


@log_args_and_response
def get_trolley_to_transfer_canisters_from_trolley_to_csr(batch_id: int, transfer_cycle_id: int, dest_device_id: int, from_app: bool) -> list:
    """
    Returns list of transfer trolleys for canisters to be transferred from trolley to robot/csr for particular batch
    @param from_app:
    @param dest_device_id:
    @param batch_id:
    @param transfer_cycle_id:
    @return:
    """
    try:
        results = list()
        ContainerMasterAlias = ContainerMaster.alias()
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()

        query = CanisterTxMeta.select(
            LocationMasterAlias.device_id.alias('trolley_id'),
            CanisterTransfers.dest_quadrant,
            CanisterTransfers.dest_device_id,
            LocationMaster.device_id,
            LocationMaster.quadrant,
            DeviceMaster.name.alias('trolley_name'),
            DeviceMaster.associated_device,
            DeviceMaster.serial_number,
            DeviceMaster.device_type_id,
            DeviceTypeMaster.device_type_name,
            CanisterMaster.canister_type,
            ContainerMasterAlias.drawer_type.alias("current_drawer_type"),
            DeviceMasterAlias.device_type_id.alias("current_device_type_id")
        ) \
            .join(CanisterTransfers, on=CanisterTxMeta.id == CanisterTransfers.from_ct_meta_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=(LocationMaster.id == CanisterMaster.location_id)) \
            .join(ContainerMasterAlias, JOIN_LEFT_OUTER, on=ContainerMasterAlias.id == LocationMaster.container_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == ContainerMasterAlias.device_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == CanisterTransfers.trolley_loc_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMasterAlias.device_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.device_id == dest_device_id,
                   CanisterTxMeta.status_id.not_in([constants.CANISTER_TRANSFER_TO_CSR_DONE]),
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_CSR_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED]),
                   CanisterTransfers.trolley_loc_id.is_null(False),
                   CanisterTransfers.batch_id == batch_id,
                   fn.IF((fn.CONCAT(fn.IFNULL(CanisterTransfers.dest_device_id, 0), '_',
                                    fn.IFNULL(CanisterTransfers.dest_quadrant, 0)) !=
                          fn.CONCAT(fn.IFNULL(LocationMaster.device_id, 0), '_',
                                    fn.IFNULL(LocationMaster.quadrant, 0))), True,
                         (fn.IF(CanisterMaster.canister_type == settings.SIZE_OR_TYPE["BIG"],
                                ContainerMasterAlias.drawer_type == settings.SIZE_OR_TYPE["SMALL"], False)))
                   ) \
            .group_by(LocationMasterAlias.device_id) \
            .order_by(LocationMasterAlias.container_id)

        for record in query.dicts():
            if from_app:
                drawer_data = get_trolley_drawers_from_trolley_tx(batch_id=batch_id,
                                                                  destination_device_id=dest_device_id,
                                                                  source_trolley_id=record['trolley_id'],
                                                                  transfer_cycle_id=transfer_cycle_id)
            else:
                drawer_data = ContainerMaster.get_drawer_data_for_device(record['trolley_id'])
            record['drawer_list'] = drawer_data
            results.append(record)
        return results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_trolley_to_transfer_canisters_from_trolley_to_csr {}".format(e))
        raise


@log_args_and_response
def get_pending_trolleys_for_from_trolley_flow(batch_id: int,
                                               transfer_cycle_id: int,
                                               current_device: int) -> list:
    """
    Returns list of transfer trolleys for canisters to be transferred from trolley to robot/csr for particular batch
    @param current_device:
    @param batch_id:
    @param transfer_cycle_id:
    @return:
    """
    try:
        results = list()
        query = CanisterTxMeta.select(
            fn.DISTINCT(LocationMaster.device_id).alias('trolley_id'),
            CanisterTxMeta.device_id.alias("dest_device_id"),
            DeviceMaster.name.alias('pending_device_name'),
            DeviceMaster.device_type_id
        ) \
            .join(CanisterTransfers, on=CanisterTxMeta.id == CanisterTransfers.from_ct_meta_id) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTxMeta.device_id) \
            .join(LocationMaster, on=LocationMaster.id == CanisterTransfers.trolley_loc_id) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.batch_id == batch_id,
                   DeviceMaster.id != current_device,
                   CanisterTxMeta.status_id.not_in([constants.CANISTER_TRANSFER_TO_ROBOT_DONE,
                                                    constants.CANISTER_TRANSFER_TO_CSR_DONE]),
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_ROBOT_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                             constants.CANISTER_TX_TO_ROBOT_SKIPPED_AND_ALTERNATE]),
                   CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_ROBOT_DONE) \
            .group_by(CanisterTxMeta.device_id) \

        for record in query.dicts():
            results.append(record)
        return results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pending_trolleys_for_from_trolley_flow {}".format(e))
        raise


@log_args_and_response
def get_pending_trolleys_for_from_trolley_flow_csr(batch_id: int,
                                               transfer_cycle_id: int,
                                               current_device: int) -> list:
    """
    Returns list of transfer trolleys for canisters to be transferred from trolley to robot/csr for particular batch
    @param current_device:
    @param batch_id:
    @param transfer_cycle_id:
    @return:
    """
    try:
        results = list()
        query = CanisterTxMeta.select(
            fn.DISTINCT(LocationMaster.device_id).alias('trolley_id'),
            CanisterTxMeta.device_id.alias("dest_device_id"),
            DeviceMaster.name.alias('pending_device_name'),
            DeviceMaster.device_type_id
        ) \
            .join(CanisterTransfers, on=CanisterTxMeta.id == CanisterTransfers.from_ct_meta_id) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTxMeta.device_id) \
            .join(LocationMaster, on=LocationMaster.id == CanisterTransfers.trolley_loc_id) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.batch_id == batch_id,
                   DeviceMaster.id != current_device,
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_CSR_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED]),
                   CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_CSR_DONE) \
            .group_by(CanisterTxMeta.device_id)

        for record in query.dicts():
            results.append(record)

        return results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pending_trolleys_for_from_trolley_flow_csr {}".format(e))
        raise


@log_args_and_response
def get_trolley_drawers_from_trolley_tx_csr(batch_id: int, destination_device_id: int, source_trolley_id: int,
                                            transfer_cycle_id: int) -> list:
    """
    Returns list of trolley drawers for given batch ID, device_id and trolley_id
    @param transfer_cycle_id: int
    @param batch_id: int
    @param destination_device_id: int
    @param source_trolley_id: int
    @return: list
    """
    try:
        results = list()
        drawer_list = list()
        LocationMasterAlias = LocationMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()
        LocationMasterAlias1 = LocationMaster.alias()

        query = CanisterTxMeta.select(
            CanisterMaster.location_id.alias('dest_location_id'),
            CanisterTransfers.canister_id,
            ContainerMaster.device_id.alias('cm_device_id'),
            ContainerMasterAlias.serial_number.alias("trolley_serial_number"),
            LocationMaster.display_location.alias("current_display_location"),
            LocationMaster.quadrant.alias('cm_dest_quadrant'),
            LocationMaster.container_id.alias('cm_dest_drawer_id'),
            LocationMaster.device_id.alias('cm_dest_device_id'),
            LocationMasterAlias1.container_id.alias('dest_drawer_id'),
            LocationMasterAlias1.device_id.alias('dest_device_id'),
            fn.replace(ContainerMaster.drawer_name, '-', '').alias('cm_dest_drawer_number'),
            LocationMaster.location_number.alias('source_location_number'),
            LocationMasterAlias.quadrant.alias('source_trolley_quadrant'),
            ContainerMasterAlias.device_id.alias('trolley_id'),
            ContainerMasterAlias.id.alias('trolley_drawer_id'),
            ContainerMasterAlias.drawer_level.alias("trolley_drawer_level"),
            ContainerMasterAlias.shelf.alias("trolley_shelf"),
            fn.replace(ContainerMasterAlias.drawer_name, '-', '').alias('trolley_drawer_number'),
            CanisterTransfers.dest_device_id,
            CanisterTransfers.dest_quadrant,
            CanisterTransfers.dest_location_number
        ) \
            .join(CanisterTransfers, on=CanisterTransfers.from_ct_meta_id == CanisterTxMeta.id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(LocationMasterAlias, on=CanisterTransfers.trolley_loc_id == LocationMasterAlias.id) \
            .join(ContainerMasterAlias, on=ContainerMasterAlias.id == LocationMasterAlias.container_id) \
            .join(LocationMasterAlias1,
                  on=LocationMasterAlias1.location_number == CanisterTransfers.dest_location_number) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.device_id == destination_device_id,
                   CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_CSR_DONE,
                   CanisterTransfers.batch_id == batch_id,
                   LocationMasterAlias.device_id == source_trolley_id,
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_CSR_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED]),
                   LocationMasterAlias1.device_id == destination_device_id
                   ).order_by(ContainerMasterAlias.id) \
            .order_by(ContainerMasterAlias.id)

        for record in query.dicts():
            if record['dest_device_id'] == record['cm_dest_device_id']:
                continue

            if record['trolley_drawer_id'] not in drawer_list:
                drawer_list.append(record['trolley_drawer_id'])
                data = {"trolley_drawer_id": record["trolley_drawer_id"],
                        "serial_number": record['trolley_serial_number'],
                        "drawer_level": record['trolley_drawer_level'],
                        "shelf": record['trolley_shelf'],
                        "trolley_drawer_number": record['trolley_drawer_number']
                        }
                if not len(results):
                    data["drawer_to_highlight"] = True
                else:
                    data["drawer_to_highlight"] = False
                results.append(data)

        return results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_trolley_drawers_from_trolley_tx_csr {}".format(e))
        raise


@log_args_and_response
def get_trolley_drawers_from_trolley_tx(batch_id: int, destination_device_id: int, source_trolley_id: int,
                                        transfer_cycle_id: int) -> list:
    """
    Returns list of trolley drawers for given batch ID, device_id and trolley_id
    @param transfer_cycle_id: int
    @param batch_id: int
    @param destination_device_id: int
    @param source_trolley_id: int
    @return: list
    """
    try:
        results = list()
        drawer_list = list()
        LocationMasterAlias = LocationMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()

        query = CanisterTxMeta.select(
            CanisterMaster.location_id.alias('dest_location_id'),
            CanisterTransfers.canister_id,
            ContainerMaster.device_id.alias('cm_device_id'),
            ContainerMasterAlias.serial_number.alias("trolley_serial_number"),
            LocationMaster.display_location.alias("current_display_location"),
            LocationMaster.quadrant.alias('cm_dest_quadrant'),
            LocationMaster.container_id.alias('cm_dest_drawer_id'),
            fn.replace(ContainerMaster.drawer_name, '-', '').alias('cm_dest_drawer_number'),
            LocationMaster.location_number.alias('source_location_number'),
            LocationMasterAlias.quadrant.alias('source_trolley_quadrant'),
            ContainerMasterAlias.device_id.alias('trolley_id'),
            ContainerMasterAlias.id.alias('trolley_drawer_id'),
            ContainerMasterAlias.drawer_level.alias("trolley_drawer_level"),
            ContainerMasterAlias.shelf.alias("trolley_shelf"),
            fn.replace(ContainerMasterAlias.drawer_name, '-', '').alias('trolley_drawer_number'),
            CanisterTransfers.dest_device_id,
            CanisterTransfers.dest_quadrant,
            CanisterTransfers.dest_location_number,
            CanisterMaster.canister_type,
            ContainerMaster.drawer_type
        ) \
            .join(CanisterTransfers, on=CanisterTransfers.from_ct_meta_id == CanisterTxMeta.id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(LocationMasterAlias, on=CanisterTransfers.trolley_loc_id == LocationMasterAlias.id) \
            .join(ContainerMasterAlias, on=ContainerMasterAlias.id == LocationMasterAlias.container_id) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.device_id == destination_device_id,
                   CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_ROBOT_DONE,
                   LocationMasterAlias.device_id == source_trolley_id,
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_ROBOT_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                             constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_LATER,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                             constants.CANISTER_TX_TO_ROBOT_SKIPPED_AND_ALTERNATE]),
                   ).order_by(ContainerMasterAlias.id)

        for record in query.dicts():
            if record['cm_device_id'] == record['dest_device_id'] and \
                    record['cm_dest_quadrant'] == record['dest_quadrant'] and \
                    not (record["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and record["drawer_type"] ==
                         settings.SIZE_OR_TYPE["SMALL"]):
                continue
            if record['trolley_drawer_id'] not in drawer_list:
                drawer_list.append(record['trolley_drawer_id'])
                data = {"trolley_drawer_id": record["trolley_drawer_id"],
                        "serial_number": record['trolley_serial_number'],
                        "drawer_level": record['trolley_drawer_level'],
                        "shelf": record['trolley_shelf'],
                        "trolley_drawer_number": record['trolley_drawer_number']
                        }
                if not len(results):
                    data["drawer_to_highlight"] = True
                else:
                    data["drawer_to_highlight"] = False
                results.append(data)

        return results
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_trolley_drawers_from_trolley_tx {}".format(e))
        raise


@log_args_and_response
def get_canister_transfers_for_robot_destination(batch_id: int, dest_device_id: int, source_trolley_drawer_id: int,
                                                 transfer_cycle_id: int, sort_fields: list):
    """
     Returns list of canisters to be transfer from particular drawer of given trolley to specified robot
        for particular batch
    @param batch_id:
    @param dest_device_id:
    @param source_trolley_drawer_id:
    @param transfer_cycle_id:
    @param sort_fields:
    @return:
    """
    try:
        order_list = list()
        fields_dict = {
            "source_drawer_number": ContainerMaster.drawer_name,
            "is_delicate": UniqueDrug.is_delicate.desc(),

        }
        order_list = get_orders(order_list, fields_dict, sort_fields)
        order_list.append(UniqueDrug.is_delicate.desc())
        transfer_data = list()
        source_drawer_list = set()
        dest_quad = False
        canister_type_dict = {"small_canister_count": 0, "big_canister_count": 0,"delicate_canister_count":0}

        LocationMasterAlias = LocationMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        delicate_transfer_data = list()

        query = CanisterTxMeta.select(CanisterMaster.location_id.alias('dest_location_id'),
                                      CanisterMaster.canister_type,
                                      CanisterTransfers.canister_id,
                                      fn.IF(
                                          CanisterMaster.expiry_date <= date.today() + timedelta(
                                              settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                          constants.EXPIRED_CANISTER,
                                          fn.IF(
                                              CanisterMaster.expiry_date <= date.today() + timedelta(
                                                  settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                              constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias(
                                          "expiry_status"),
                                      DrugMaster.id.alias('drug_id'),
                                      DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
                                      DrugMaster.strength,
                                      DrugMaster.strength_value,
                                      DrugMaster.ndc,
                                      DrugMaster.image_name,
                                      DrugMaster.shape.alias("drug_shape"),
                                      DrugMaster.imprint,
                                      fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                            DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                      fn.IF(DrugStockHistory.created_by.is_null(True), None,
                                            DrugStockHistory.created_by).alias(
                                          "stock_updated_by"),
                                      CustomDrugShape.id.alias("custom_drug_id"),
                                      CustomDrugShape.name,
                                      ContainerMaster.device_id.alias('cm_device_id'),
                                      ContainerMaster.serial_number,
                                      LocationMaster.display_location.alias("current_display_location"),
                                      DeviceMaster.name.alias("current_device_name"),
                                      DeviceMaster.device_type_id.alias("current_device_type_id"),
                                      DeviceMaster.id.alias("current_device_id"),
                                      LocationMaster.quadrant.alias('cm_dest_quadrant'),
                                      LocationMaster.container_id.alias('cm_dest_drawer_id'),
                                      ContainerMaster.drawer_name,
                                      ContainerMaster.ip_address,
                                      ContainerMaster.drawer_level.alias("current_drawer_level"),
            ContainerMaster.secondary_ip_address,
            ContainerMaster.secondary_mac_address,
            ContainerMaster.mac_address,
            fn.replace(ContainerMaster.drawer_name, '-', '').alias('cm_dest_drawer_number'),
            LocationMaster.location_number.alias('source_location_number'),
            LocationMasterAlias.quadrant.alias('source_trolley_quadrant'),
            ContainerMasterAlias.device_id.alias('trolley_id'),
            ContainerMasterAlias.id.alias('trolley_drawer_id'),
            fn.replace(ContainerMasterAlias.drawer_name, '-', '').alias('trolley_drawer_number'),
            CanisterTransfers.dest_device_id,
            CanisterTransfers.dest_quadrant,
            CanisterTransfers.dest_location_number,
            CanisterTransfers.transfer_status,
            DrugDetails.last_seen_by,
            DrugDetails.last_seen_date,
            DeviceMasterAlias.device_type_id.alias('dest_device_type_id'),
                                      DeviceMasterAlias.name.alias("dest_device_name"),
                                      CanisterMaster.canister_type,
                                      ContainerMaster.drawer_type,
                                      UniqueDrug.is_delicate.alias('is_delicate'),
                                      ReservedCanister.id.alias('reserved_id'),
                                      ReservedCanister.batch_id.alias('reserved_batch_id')
                                      ) \
            .join(CanisterTransfers, on=CanisterTransfers.from_ct_meta_id == CanisterTxMeta.id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                         (DrugStockHistory.is_active == True) &
                                                         (DrugStockHistory.company_id == CanisterMaster.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                   (DrugDetails.company_id == CanisterMaster.company_id)) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(LocationMasterAlias, on=CanisterTransfers.trolley_loc_id == LocationMasterAlias.id) \
            .join(ContainerMasterAlias, on=ContainerMasterAlias.id == LocationMasterAlias.container_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=CanisterTransfers.dest_device_id == DeviceMasterAlias.id) \
            .join(ReservedCanister, JOIN_LEFT_OUTER,
                  on=(CanisterMaster.id == ReservedCanister.canister_id) & (CanisterTransfers.batch_id == batch_id)) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_ROBOT_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                             constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_LATER,
                                                             constants.CANISTER_TX_TO_ROBOT_SKIPPED_AND_ALTERNATE]),
                   CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.device_id == dest_device_id,
                   CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_ROBOT_DONE,
                   LocationMasterAlias.container_id == source_trolley_drawer_id
                   )

        if order_list:
            query = query.order_by(*order_list)
        delicate_locations = 0
        canister_ids = list()
        ndc_list = []
        for record in query.dicts():
            # if record['reserved_batch_id'] and record['reserved_batch_id'] != batch_id:
            #     continue

            if record['canister_id'] in canister_ids:
                continue

            if not dest_quad:
                dest_quad = record['dest_quadrant']

            # if record['']

            if record['cm_device_id'] == record['dest_device_id'] and \
                    record['cm_dest_quadrant'] == record['dest_quadrant'] and not (record["canister_type"] ==
                                                                                   settings.SIZE_OR_TYPE["BIG"] and
                                                                                   record["drawer_type"] ==
                                                                                   settings.SIZE_OR_TYPE["SMALL"]):
                if record['is_delicate'] and record['reserved_id']:
                    record = get_location_status_for_delicate(record)
                    wrong_location = record.get('wrong_location',None)
                    if not wrong_location:
                        continue
                else:
                    continue

            # If Canister Size = Big and Drawer Size = Small then notify the user about issue with size of canister
            record["wrong_size"] = (True if record["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and
                                            record["drawer_type"] == settings.SIZE_OR_TYPE["SMALL"] else False)

            if record["cm_dest_drawer_id"] != source_trolley_drawer_id and record["cm_device_id"]:
                record["wrong_location"] = True
                record['current_device'] = record['cm_device_id']

            else:
                record["wrong_location"] = False

            if record['canister_type'] == settings.SIZE_OR_TYPE['BIG']:
                canister_type_dict["big_canister_count"] += 1
            else:
                if record["is_delicate"] and record['reserved_id']:
                    canister_type_dict["delicate_canister_count"] += 1
                else:
                    canister_type_dict["small_canister_count"] += 1

            if record['transfer_status'] == constants.CANISTER_TX_TO_ROBOT_ALTERNATE:
                record['alternate_canister'] = True
            else:
                record['alternate_canister'] = False

            if record['transfer_status'] == constants.CANISTER_TX_TO_TROLLEY_SKIPPED:
                record['to_trolley_skipped'] = True
            else:
                record['to_trolley_skipped'] = False
            canister_ids.append(record['canister_id'])
            ndc_list.append(int(record['ndc']))
            if record["is_delicate"] and record['reserved_id']:
                if not delicate_locations:
                    delicate_locations += 1
                delicate_transfer_data.append(record)
            else:
                if delicate_locations == 1:
                    delicate_locations = 2
                transfer_data.append(record)

            source_drawer_list.add(record['cm_dest_drawer_id'])
        if delicate_locations == 2:
            delicate_locations = True
        else:
            delicate_locations = False
        return delicate_transfer_data, transfer_data, list(source_drawer_list), dest_quad, canister_type_dict, delicate_locations, ndc_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canister_transfers_for_robot_destination {}".format(e))
        raise


def get_canisters_transfers_from_trolley_to_csr(batch_id: int, dest_device_id: int, source_trolley_drawer_id: int,
                                                transfer_cycle_id: int, sort_fields: list):
    """
     Returns list of canisters to be transfer from particular drawer of given trolley to specified robot
        for particular batch
    @param batch_id:
    @param dest_device_id:
    @param source_trolley_drawer_id:
    @param transfer_cycle_id:
    @param sort_fields:
    @return:
    """
    try:
        order_list = list()
        ndc_list = []
        fields_dict = {
            "source_drawer_number": ContainerMaster.drawer_name
        }
        order_list = get_orders(order_list, fields_dict, sort_fields)
        order_list.append(UniqueDrug.is_delicate.desc())
        order_list.append(LocationMaster.location_number)
        transfer_data = list()
        # drawer_to_unlock = dict()
        canister_id_list = list()

        LocationMasterAlias = LocationMaster.alias()
        LocationMasterAlias1 = LocationMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()
        # CanisterMasterAlias = CanisterMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()

        query = CanisterTxMeta.select(
            CanisterMaster.canister_type,
            CanisterTransfers.canister_id,
            fn.IF(
                CanisterMaster.expiry_date <= date.today() + timedelta(
                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                constants.EXPIRED_CANISTER,
                fn.IF(
                    CanisterMaster.expiry_date <= date.today() + timedelta(
                        settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                    constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
            CanisterTransfers.dest_location_number,
            CanisterTransfers.transfer_status,
            DrugMaster.id.alias('drug_id'),
            DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.ndc,
            DrugMaster.image_name,
            DrugMaster.shape.alias("drug_shape"),
            DrugMaster.imprint,
            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
            fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by).alias(
                "stock_updated_by"),
            CustomDrugShape.id.alias("custom_drug_id"),
            CustomDrugShape.name,
            ContainerMaster.device_id.alias('cm_device_id'),
            ContainerMaster.serial_number,
            LocationMasterAlias1.id.alias('current_location_id'),
            LocationMasterAlias1.display_location.alias('current_display_location'),
            LocationMasterAlias1.device_id.alias('current_device_id'),
            DeviceMaster.name.alias("current_device_name"),
            LocationMaster.id.alias('dest_location_id'),
            LocationMaster.display_location.alias("dest_display_location"),
            LocationMaster.container_id.alias('dest_drawer_id'),
            LocationMaster.device_id.alias("dest_device_id"),
            DeviceMasterAlias.name.alias("dest_device_name"),
            ContainerMaster.drawer_name.alias('dest_drawer_name'),
            ContainerMaster.serial_number.alias("dest_drawer_serial_number"),
            fn.replace(ContainerMaster.drawer_name, '-', '').alias('dest_drawer_number'),
            ContainerMaster.mac_address.alias("dest_drawer_mac_address"),
            ContainerMaster.secondary_mac_address.alias("dest_sec_mac_address"),
            ContainerMaster.ip_address.alias("dest_drawer_ip_address"),
            ContainerMaster.secondary_ip_address.alias("dest_drawer_secondary_ip"),
            ContainerMaster.shelf,
            LocationMasterAlias.quadrant.alias('source_trolley_quadrant'),
            LocationMasterAlias1.container_id.alias("current_drawer"),
            ContainerMasterAlias.device_id.alias('trolley_id'),
            ContainerMasterAlias.id.alias('trolley_drawer_id'),
            fn.replace(ContainerMasterAlias.drawer_name, '-', '').alias('trolley_drawer_number'),
            DeviceMasterAlias.device_type_id,
            DrugDetails.last_seen_by,
            DrugDetails.last_seen_date,
            ContainerMaster.drawer_type,
            UniqueDrug.is_delicate
        ) \
            .join(CanisterTransfers, on=CanisterTransfers.from_ct_meta_id == CanisterTxMeta.id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                         (DrugStockHistory.is_active == True) &
                                                         (DrugStockHistory.company_id == CanisterMaster.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                   (DrugDetails.company_id == CanisterMaster.company_id)) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
            .join(LocationMaster, on=LocationMaster.location_number == CanisterTransfers.dest_location_number) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(LocationMasterAlias, on=CanisterTransfers.trolley_loc_id == LocationMasterAlias.id) \
            .join(ContainerMasterAlias, on=ContainerMasterAlias.id == LocationMasterAlias.container_id) \
            .join(LocationMasterAlias1, JOIN_LEFT_OUTER, on=LocationMasterAlias1.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMasterAlias1.device_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id, CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.device_id == dest_device_id, LocationMaster.device_id == dest_device_id,
                   CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_CSR_DONE,
                   CanisterTransfers.batch_id == batch_id,
                   CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_CSR_SKIPPED,
                                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED]),
                   LocationMasterAlias.container_id == source_trolley_drawer_id) \
            .order_by(ContainerMaster.id)

        if order_list:
            query = query.order_by(*order_list)

        for record in query.dicts():
            if record['dest_device_id'] == record['current_device_id']:
                continue

            # If Canister Size = Big and Drawer Size = Small then notify the user about issue with size of canister
            record["wrong_size"] = (True if record["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and
                                            record["drawer_type"] == settings.SIZE_OR_TYPE["SMALL"] else False)

            if record["current_drawer"] != source_trolley_drawer_id:
                record["wrong_location"] = False

            else:
                record["wrong_location"] = False

            if record['transfer_status'] == constants.CANISTER_TX_TO_TROLLEY_SKIPPED:
                record['to_trolley_skipped'] = True
            else:
                record['to_trolley_skipped'] = False

            if record['transfer_status'] in [constants.CANISTER_TX_TO_ROBOT_SKIPPED_AND_ALTERNATE, constants.CANISTER_TX_TO_ROBOT_SKIPPED]:
                record['to_robot_skipped'] = True
            else:
                record['to_robot_skipped'] = False

            transfer_data.append(record)
            canister_id_list.append(record['canister_id'])
            ndc_list.append(int(record['ndc']))

        return transfer_data, canister_id_list, ndc_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_canisters_transfers_from_trolley_to_csr {}".format(e))
        raise


@log_args_and_response
def transfer_cycle_status_for_update(update_status: int,
                                     device_id: int,
                                     batch_id: int,
                                     cycle_id: int) -> tuple:
    """
    This function checks to update CanisterTransferMeta table status.
    @param update_status: int
    @param cycle_id: int
    @param batch_id: int
    @param device_id: int
    @return bool
    """
    try:
        current_status = None
        # query to obtain current status for the cycle_id, device_id and batch_id
        current_status_query = CanisterTxMeta.select(CanisterTxMeta.status_id).dicts() \
            .where((CanisterTxMeta.cycle_id == cycle_id), (CanisterTxMeta.batch_id == batch_id),
                   (CanisterTxMeta.device_id == device_id))

        # to validate status for given cycle_id and obtain current_status
        if current_status_query.count() == 1:
            for record in current_status_query:
                current_status = record["status_id"]
        else:
            # when no transfer available with this device then no need to update status in db
            return True, "No transfer available from this device"

        logger.info("update_status: {}".format(update_status))
        logger.info("current_status: {}".format(current_status))

        # to validate update_status must be greater than the current status
        if int(update_status) > int(current_status):
            update_canister_meta_status = CanisterTxMeta.update(status_id=update_status,
                                                                modified_date=get_current_date_time()).where(
                (CanisterTxMeta.cycle_id == cycle_id), (CanisterTxMeta.batch_id == batch_id),
                (CanisterTxMeta.device_id == device_id)).execute()
            logger.info("update_meta_status: {}".format(update_canister_meta_status))
            return True, "success"
        elif int(update_status) == int(current_status):
            return True, "status is already updated"
        else:
            return False, "Can't update previous status"

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in transfer_cycle_status_for_update {}".format(e))
        raise


@log_args_and_response
def check_transfer_recommendation_status(batch_id: int) -> list:
    """
    Function to check if canister tx is already executed before batch import
    @param batch_id: int
    @return: list
    """
    cycle_id_list = list()
    try:
        query = CanisterTxMeta.select(CanisterTxMeta.id, CanisterTxMeta.cycle_id).dicts() \
            .where(CanisterTxMeta.batch_id == batch_id)

        for record in query:
            if record['cycle_id'] not in cycle_id_list:
                cycle_id_list.append(record['cycle_id'])

        return cycle_id_list

    except (InternalError, IntegrityError) as e:
        logger.error("error in check_transfer_recommendation_status {}".format(e))
        raise
    except DoesNotExist as e:
        logger.error("error in check_transfer_recommendation_status {}".format(e))
        return cycle_id_list
    except Exception as e:
        logger.error("error in check_transfer_recommendation_status {}".format(e))
        raise


@log_args_and_response
def check_couch_db_status(status: int, cycle_id: int, batch_id: int) -> tuple:
    """
    This function checks for couch db updates for the given cycle_id and batch_id
    @param status: int
    @param cycle_id: int
    @param batch_id: int
    @return tuple
    """
    try:
        if status == constants.CANISTER_TRANSFER_TO_TROLLEY_DONE:
            canister_meta_status_query = CanisterTxMeta.select(CanisterTxMeta.status_id.alias("current_status")) \
                .dicts().where(CanisterTxMeta.cycle_id == cycle_id, CanisterTxMeta.batch_id == batch_id)

            # to check if all the devices have status as Transfer to trolley done
            for record in canister_meta_status_query:
                if record["current_status"] not in [constants.CANISTER_TRANSFER_TO_TROLLEY_DONE,
                                                    constants.CANISTER_TRANSFER_TO_ROBOT_DONE,
                                                    constants.CANISTER_TRANSFER_TO_CSR_DONE]:
                    return False, None

            return True, None

        if status == constants.CANISTER_TRANSFER_TO_ROBOT_DONE:
            canister_meta_status_query = CanisterTxMeta.select(CanisterTxMeta.status_id.alias("current_status"),
                                                               CanisterTxMeta.cycle_id) \
                .join(DeviceMaster, on=DeviceMaster.id == CanisterTxMeta.device_id) \
                .dicts().where((CanisterTxMeta.cycle_id == cycle_id),
                               (CanisterTxMeta.batch_id == batch_id),
                               (DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT']))

            # check if all devices have completed transfer to robot
            for record in canister_meta_status_query:
                if record["current_status"] not in [constants.CANISTER_TRANSFER_TO_ROBOT_DONE, constants.CANISTER_TRANSFER_TO_CSR_DONE]:
                    return False, None

            return True, None

        if status == constants.CANISTER_TRANSFER_TO_CSR_DONE:
            canister_meta_status_query = CanisterTxMeta.select(CanisterTxMeta.status_id.alias("current_status"),
                                                               CanisterTxMeta.cycle_id) \
                .join(DeviceMaster, on=DeviceMaster.id == CanisterTxMeta.device_id) \
                .dicts().where((CanisterTxMeta.cycle_id == cycle_id),
                               (CanisterTxMeta.batch_id == batch_id),
                               (DeviceMaster.device_type_id == settings.DEVICE_TYPES['CSR']))

            # all the devices have completed the transfer from trolley
            for record in canister_meta_status_query:
                logger.info(record)
                if record["current_status"] != constants.CANISTER_TRANSFER_TO_CSR_DONE:
                    return False, record["cycle_id"]

            # obtain the next cycle id for the current batch
            next_cycle_id = CanisterTxMeta.select(CanisterTxMeta.cycle_id).dicts() \
                .where(CanisterTxMeta.batch_id == batch_id,
                       CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_CSR_DONE) \
                .order_by(CanisterTxMeta.cycle_id).limit(1)

            for record in next_cycle_id:
                if record["cycle_id"]:
                    return True, record["cycle_id"]

            # there is no next cycle id and the transfer is completed
            return True, None

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_couch_db_status {}".format(e))
        raise


@log_args_and_response
def get_empty_locations_for_canister(device_id, quadrant, canister_type_dict):
    """
    Function to get drawer list to unlock for given canister count considering device, quadrant and canister type
    @param canister_type_dict: dict
    @param device_id: int
    @param quadrant: int
    @return:
    """
    drawer_to_unlock = dict()
    try:
        logger.info("Input get_empty_locations_for_canister {}, {}, {}".format(device_id, quadrant, canister_type_dict))
        big_canister_count = canister_type_dict["big_canister_count"]
        small_canister_count = canister_type_dict["small_canister_count"]
        logger.info("get_empty_locations_for_canister {}, {}, {}".format(device_id, quadrant, big_canister_count,
                                                                         small_canister_count))
        temp_big_canister = big_canister_count
        temp_small_canister = small_canister_count
        if not device_id or not quadrant:
            logger.error("Device id or quad is null")
            return drawer_to_unlock

        if big_canister_count == 0 and small_canister_count == 0:
            logger.error("No canisters to be transferred")
            return drawer_to_unlock

        empty_locations_drawer_wise, drawer_data = db_get_drawer_wise_empty_locations(
            device_id=device_id, quadrant=[quadrant])

        for drawer_type, container_data in empty_locations_drawer_wise.items():
            if drawer_type == settings.SIZE_OR_TYPE['BIG'] and big_canister_count > 0:
                for container, display_locations in container_data.items():
                    if temp_big_canister <= 0:
                        break
                    if not len(display_locations):
                        continue
                    location_count = len(display_locations)
                    drawer_data[container]["to_device"] = display_locations[:temp_big_canister]
                    temp_big_canister -= location_count
                    drawer_data[container]["from_device"] = list()
                    drawer_to_unlock[container] = drawer_data[container]
            else:
                for container, display_locations in container_data.items():
                    if temp_small_canister <= 0:
                        break
                    if not len(display_locations):
                        continue
                    location_count = len(display_locations)
                    drawer_data[container]["to_device"] = display_locations[:temp_small_canister]
                    temp_small_canister -= location_count
                    drawer_data[container]["from_device"] = list()
                    drawer_to_unlock[container] = drawer_data[container]

        return drawer_to_unlock

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_empty_locations_for_canister {}".format(e))
        raise

    except Exception as e:
        logger.error("Error in get_empty_locations_for_canister {}".format(e))
        return drawer_to_unlock


@log_args_and_response
def db_get_drawer_wise_empty_locations(device_id, quadrant):
    """
    Returns empty locations for given device id and quadrant
    @param device_id: int
    @param quadrant: list
    @return: dict
    """

    empty_locations, drawer_data = get_locations_from_device_and_quadrant(device_id=device_id, quadrant=quadrant)
    # filling with all locations first
    locations = dict()

    if device_id:
        for record in CanisterMaster.select(LocationMaster.device_id,
                                            LocationMaster.id,
                                            LocationMaster.container_id,
                                            LocationMaster.display_location,
                                            ContainerMaster.drawer_name,
                                            ContainerMaster.drawer_type,
                                            ContainerMaster.drawer_level,
                                            LocationMaster.location_number).dicts() \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
                .where(
                    (CanisterMaster.location_id > 0 | ~(LocationMaster.is_disabled == settings.is_location_active)),
                    LocationMaster.device_id == device_id,
                    LocationMaster.quadrant << [quadrant]):

            if record['drawer_type'] not in locations.keys():
                locations[record['drawer_type']] = dict()

            if record['drawer_name'] not in locations[record['drawer_type']].keys():
                locations[record['drawer_type']][record['drawer_name']] = list()
            locations[record['drawer_type']][record['drawer_name']].append(record['display_location'])

        # remove non-empty and disabled locations from total locations
        for drawer_type, empty_loc in locations.items():
            for container, each_location in empty_loc.items():
                for location in locations[drawer_type][container]:
                    if drawer_type in empty_locations and container in empty_locations[drawer_type] \
                            and location in empty_locations[drawer_type][container]:
                        empty_locations[drawer_type][container].remove(location)
    return empty_locations, drawer_data


def get_locations_from_device_and_quadrant(device_id, quadrant):
    drawer_wise_locations = {}
    drawer_data = dict()
    try:
        query = LocationMaster.select(LocationMaster.id, LocationMaster.display_location,
                                      LocationMaster.location_number, LocationMaster.container_id,
                                      ContainerMaster.drawer_name, ContainerMaster.drawer_type,
                                      ContainerMaster.serial_number,
                                      ContainerMaster.ip_address, ContainerMaster.secondary_ip_address,
                                      ContainerMaster.mac_address, ContainerMaster.secondary_mac_address,
                                      DeviceMaster.ip_address.alias("device_ip_address"),
                                      DeviceMaster.device_type_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
            .where(LocationMaster.device_id == device_id, LocationMaster.quadrant << [quadrant],
                   LocationMaster.is_disabled == settings.is_location_active,
                   ContainerMaster.drawer_type.not_in([settings.SIZE_OR_TYPE["MFD"]])) \
            .order_by(ContainerMaster.id, LocationMaster.id)
        for record in query.dicts():
            if record['drawer_type'] not in drawer_wise_locations.keys():
                drawer_wise_locations[record['drawer_type']] = dict()
            if record['drawer_name'] not in drawer_wise_locations[record['drawer_type']].keys():
                drawer_data[record["drawer_name"]] = {"ip_address": record["ip_address"],
                                                      "secondary_ip_address": record["secondary_ip_address"],
                                                      "mac_address": record["mac_address"],
                                                      "secondary_mac_address": record["secondary_mac_address"],
                                                      "serial_number": record["serial_number"],
                                                      "drawer_name": record["drawer_name"],
                                                      "device_ip_address": record["device_ip_address"],
                                                      "device_type_id": record["device_type_id"],
                                                      "id": record["container_id"]}
                drawer_wise_locations[record['drawer_type']][record['drawer_name']] = list()
            drawer_wise_locations[record['drawer_type']][record['drawer_name']].append(record['display_location'])

        return drawer_wise_locations, drawer_data
    except DoesNotExist as e:
        logger.error("error in get_locations_from_device_and_quadrant {}".format(e))
        raise NoLocationExists



@log_args_and_response
def get_meta_id_from_batch_and_cycle(batch_id: int, cycle_id: int, device_id: int):
    """
    Function to get canister tx meta id from batch cycle and device id
    @param batch_id:
    @param cycle_id:
    @param device_id:
    @return: int
    """
    try:
        query = CanisterTxMeta.select(CanisterTxMeta.id).dicts() \
            .where(CanisterTxMeta.batch_id == batch_id, CanisterTxMeta.cycle_id == cycle_id,
                   CanisterTxMeta.device_id == device_id)

        for record in query:
            return record['id']

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_meta_id_from_batch_and_cycle {}".format(e))
        raise e


@log_args_and_response
def check_transfers_for_trolley(batch_id: int, device_id: int, to_meta_id: int) -> bool:
    """
    This function verifies the location of the canisters before updating the status
    """
    try:
        query = CanisterTransfers.select(CanisterTransfers.canister_id,
                                         CanisterTransfers.trolley_loc_id,
                                         CanisterTransfers.transfer_status,
                                         CanisterMaster.location_id).dicts()\
                                    .join(CanisterMaster, on=CanisterTransfers.canister_id == CanisterMaster.id)\
                                    .where((CanisterTransfers.batch_id == batch_id),
                                           (CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                                                      constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE])),
                                           (CanisterTransfers.to_ct_meta_id == to_meta_id),
                                           (CanisterTransfers.dest_device_id == device_id))
        logger.info(query)
        for record in query:
            if record["trolley_loc_id"] != record["location_id"]:
                logger.info("check_transfers_for_trolley for {}".format(record))
                return False
        return True

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_transfers_for_trolley {}".format(e))
        raise e


@log_args_and_response
def check_to_robot_required_for_meta_id(batch_id: int, from_meta_id: int) -> bool:
    """
    This function verifies the location of the canisters before updating the status
    """
    try:
        query = CanisterTransfers.select(CanisterTransfers.canister_id,
                                         CanisterTransfers.trolley_loc_id,
                                         CanisterMaster.location_id).dicts() \
            .join(CanisterMaster, on=CanisterTransfers.canister_id == CanisterMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTransfers.dest_device_id) \
            .where((CanisterTransfers.batch_id == batch_id),
                   (DeviceMaster.device_type_id == settings.DEVICE_TYPES["ROBOT"]),
                   (CanisterTransfers.from_ct_meta_id == from_meta_id))
        logger.info(query)
        for record in query:
            logger.info("check_to_robot_required_for_meta_id record {}".format(record))
            return True

        return False

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_to_robot_required_for_meta_id {}".format(e))
        raise e


@log_args_and_response
def check_to_csr_required_for_meta_id(batch_id: int, from_meta_id: int) -> bool:
    """
    This function verifies the location of the canisters before updating the status
    """
    try:
        DeviceMasterAlias = DeviceMaster.alias()

        query = CanisterTransfers.select(CanisterTransfers.canister_id,
                                         CanisterTransfers.trolley_loc_id,
                                         CanisterTransfers.transfer_status,
                                         CanisterMaster.location_id).dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTransfers.dest_device_id) \
            .where((CanisterTransfers.batch_id == batch_id),
                   (DeviceMasterAlias.device_type_id << [settings.DEVICE_TYPES['Canister Transfer Cart'],
                                                         settings.DEVICE_TYPES['Canister Cart w/ Elevator']]),
                   (CanisterMaster.active == settings.is_canister_active),
                   (DeviceMaster.device_type_id == settings.DEVICE_TYPES['CSR']),
                   (CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_CSR_SKIPPED,
                                                              constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                              constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE])),
                   (CanisterTransfers.from_ct_meta_id == from_meta_id))

        for record in query:
            logger.info("check_to_csr_required_for_meta_id record {}".format(record))
            return True

        return False

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_to_csr_required_for_meta_id {}".format(e))
        raise e


@log_args_and_response
def check_to_csr_required_for_csr_meta_id(batch_id: int, from_meta_id: int) -> bool:
    """
    This function verifies the location of the canisters before updating the status
    """
    try:
        DeviceMasterAlias = DeviceMaster.alias()

        query = CanisterTransfers.select(CanisterTransfers.canister_id,
                                         CanisterTransfers.trolley_loc_id,
                                         CanisterTransfers.transfer_status,
                                         CanisterMaster.location_id).dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTransfers.dest_device_id) \
            .where((CanisterTransfers.batch_id == batch_id),
                   (CanisterMaster.active == settings.is_canister_active),
                   (DeviceMaster.device_type_id == settings.DEVICE_TYPES['CSR']),
                   (CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_CSR_SKIPPED,
                                                              constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                              constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE])),
                   (CanisterTransfers.from_ct_meta_id == from_meta_id))

        for record in query:
            logger.info("check_to_csr_required_for_csr_meta_id record {}".format(record))
            return True

        return False

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in check_to_csr_required_for_csr_meta_id {}".format(e))
        raise e

def check_transfers_for_device(batch_id: int, device_id: int, from_meta_id: int) -> bool:
    """
    This function verifies the canister transfers to device before updating the status
    """
    try:
        device_data = DeviceMaster.db_get_by_id(device_id=device_id)
        device_type = device_data.device_type_id_id
        if device_type == settings.DEVICE_TYPES["ROBOT"]:
            query = CanisterTransfers.select(LocationMaster.quadrant,
                                             CanisterTransfers.canister_id,
                                             CanisterTransfers.transfer_status,
                                             CanisterTransfers.dest_quadrant).dicts()\
                    .join(CanisterMaster, on=CanisterTransfers.canister_id == CanisterMaster.id)\
                    .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
                    .where((CanisterTransfers.batch_id == batch_id),
                           (CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_ROBOT_SKIPPED,
                                                                      constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                                      constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                                                      constants.CANISTER_TX_TO_ROBOT_SKIPPED_AND_ALTERNATE])),
                           (CanisterTransfers.dest_device_id == device_id),
                           (CanisterTransfers.from_ct_meta_id == from_meta_id))
            logger.info(query)
            for record in query:
                if record["quadrant"] != record["dest_quadrant"]:
                    return False
            return True

        if device_type == settings.DEVICE_TYPES["CSR"]:
            LocationMasterAlias = LocationMaster.alias()
            query = CanisterTransfers.select(LocationMaster.container_id.alias("current_container_id"),
                                             CanisterTransfers.transfer_status,
                                             CanisterTransfers.canister_id,
                                             LocationMasterAlias.container_id.alias("dest_container_id")).dicts() \
                .join(CanisterMaster, on=CanisterTransfers.canister_id == CanisterMaster.id) \
                .join(LocationMasterAlias, on=CanisterTransfers.dest_location_number == LocationMasterAlias.location_number) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
                .where((CanisterTransfers.batch_id == batch_id),
                       (CanisterTransfers.dest_device_id == device_id),
                       (CanisterTransfers.from_ct_meta_id == from_meta_id),
                       (CanisterTransfers.transfer_status.not_in([constants.CANISTER_TX_TO_CSR_SKIPPED,
                                                                  constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                                                  constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE])),
                       (LocationMasterAlias.device_id_id == device_id))
            logger.info(query)
            for record in query:
                logger.info("Transfer pending for record {}".format(record))
                if record["current_container_id"] != record["dest_container_id"]:
                    return False
            return True

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_transfers_for_device {}".format(e))
        raise e


@log_args_and_response
def get_pending_canister_transfers_for_batch(batch_id: int) -> tuple:
    """
    Function to get pending canister transfers for batch `i.e` canisters that are present in trolley
    @param batch_id: int
    @return: tuple
    """
    canister_info_dict = dict()
    cycle_id_list = list()
    device_list = list()
    cart_type_dict = {settings.DEVICE_TYPES['Canister Transfer Cart']: list(),
                      settings.DEVICE_TYPES['Canister Cart w/ Elevator']: list()}

    try:
        DeviceMasterAlias = DeviceMaster.alias()

        query = CanisterTxMeta.select(CanisterTxMeta.id.alias('canister_tx_meta'),
                                      CanisterMaster.id.alias('canister_id'),
                                      CanisterTxMeta.device_id,
                                      CanisterTransfers.dest_device_id,
                                      CanisterTxMeta.status_id,
                                      CanisterTxMeta.cycle_id,
                                      DeviceMaster.id.alias('cart_device_id'),
                                      DeviceMaster.device_type_id,
                                      ).dicts() \
            .join(CanisterTransfers, on=CanisterTransfers.from_ct_meta_id == CanisterTxMeta.id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == CanisterTransfers.dest_device_id) \
            .where(CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.status_id.not_in([constants.CANISTER_TRANSFER_TO_CSR_DONE]),
                   DeviceMasterAlias.device_type_id.not_in([settings.DEVICE_TYPES['CSR']]),
                   DeviceMaster.device_type_id << [settings.DEVICE_TYPES['Canister Transfer Cart'],
                                                   settings.DEVICE_TYPES['Canister Cart w/ Elevator']])

        for record in query:
            # add device (ROBOT) id's for which canister transfer is skipped
            if record['dest_device_id'] not in device_list:
                device_list.append(record['dest_device_id'])

            # add pending cycle ids
            if record['cycle_id'] not in cycle_id_list:
                cycle_id_list.append(record['cycle_id'])

            # canister dict for which transfer to robot is skipped
            canister_info_dict[record['canister_id']] = record

            if record['cart_device_id'] not in cart_type_dict[record['device_type_id']]:
                cart_type_dict[record['device_type_id']].append(record['cart_device_id'])

        return canister_info_dict, cycle_id_list, device_list, cart_type_dict

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_pending_canister_transfers_for_batch {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_pending_canister_transfers_for_batch {}".format(e))
        return None, None, None


@log_args_and_response
def get_to_trolley_pending_canister_transfers_for_batch(batch_id: int) :
    """
    Function to get pending canister transfers for batch `i.e` canisters for which to trolley is pending
    @param batch_id: int
    @return: list
    """
    canister_list = list()
    canister_list_cycle_wise = dict()

    try:

        query = CanisterTxMeta.select(CanisterTxMeta.id.alias('canister_tx_meta'),
                                      CanisterMaster.id.alias('canister_id'),
                                      CanisterTxMeta.cycle_id
                                      ).dicts() \
            .join(CanisterTransfers, on=CanisterTransfers.from_ct_meta_id == CanisterTxMeta.id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .where(CanisterTxMeta.batch_id == batch_id,
                   CanisterTransfers.transfer_status == constants.CANISTER_TX_PENDING,
                   CanisterTransfers.trolley_loc_id.is_null(False))

        for record in query:
            # add canister id's for which canister transfer to trolley is pending
            canister_list_cycle_wise.setdefault(record['cycle_id'],list())
            canister_list_cycle_wise[record['cycle_id']].append(record['canister_id'])
            canister_list.append(record['canister_id'])

        return canister_list, canister_list_cycle_wise

    except (InternalError, IntegrityError) as e:
        logger.info("Error in get_to_trolley_pending_canister_transfers_for_batch {}".format(e))
        raise


@log_args_and_response
def update_canister_loc_in_canister_transfers(batch_id: int,
                                              canister_id: int,
                                              dest_device_id: int,
                                              dest_location_number: int,
                                              dest_quadrant: [int, None]):
    """

    @param canister_id:
    @param dest_quadrant:
    @param dest_location_number:
    @param dest_device_id:
    @param batch_id:
    @return:
    """
    try:
        status = CanisterTransfers.update(dest_device_id=dest_device_id,
                                          dest_location_number=dest_location_number,
                                          dest_quadrant=dest_quadrant) \
            .where(CanisterTransfers.batch_id == batch_id,
                   CanisterTransfers.canister_id == canister_id).execute()

        return status

    except (InternalError, IntegrityError) as e:
        logger.info("Error in update_canister_loc_in_canister_transfers {}".format(e))
        raise


@log_args_and_response
def update_cycle_done_for_pending_cycles(batch_id: int, tx_meta_id: int):
    """
    Function to update cycle done for pending cycles of this batch in case of skip canister transfer
    @param tx_meta_id:
    @param batch_id: int
    @return:
    """
    try:
        if not batch_id or not tx_meta_id:
            return False

        # update status as transfer from trolley done for all pending cycles
        pending_cycle_update = CanisterTxMeta.update(status_id=constants.CANISTER_TRANSFER_TO_CSR_DONE) \
            .where(CanisterTxMeta.batch_id == batch_id, CanisterTxMeta.id.not_in([tx_meta_id])) \
            .execute()

        logger.info("update_cycle_done_for_pending_cycles pending cycle update {}".format(pending_cycle_update))

        # update status as transfer from trolley done for current cycle
        existing_cycle_update = CanisterTxMeta.update(status_id=constants.CANISTER_TRANSFER_TO_TROLLEY_DONE) \
            .where(CanisterTxMeta.id == tx_meta_id, CanisterTxMeta.batch_id == batch_id).execute()

        logger.info("update_cycle_done_for_pending_cycles update {}".format(existing_cycle_update))

        return True

    except (InternalError, IntegrityError) as e:
        logger.info(e)
        raise
    except Exception as e:
        logger.error("error in update_cycle_done_for_pending_cycles {}".format(e))
        return False


@log_args_and_response
def check_pending_canister_transfers(system_id: int) -> list:
    """
    Function to check if canister tx is pending for any batch or not
    @return: list
    """
    try:
        query = CanisterTxMeta.select(CanisterTxMeta,
                                      DeviceMaster.name.alias("device_name"),
                                      DeviceMaster.system_id).dicts() \
            .join(BatchMaster, on=BatchMaster.id == CanisterTxMeta.batch_id) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTxMeta.device_id) \
            .where(CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_CSR_DONE,
                   BatchMaster.system_id == system_id)

        return list(query)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_pending_canister_transfers {}".format(e))
        raise e


@log_args_and_response
def get_pending_canister_transfer_batch_id(system_id: int) -> int:
    """
    Function to get batch_id for which canister transfer is pending
    @param system_id:
    @return:
    """
    batch_id = 0
    batch_status = [settings.BATCH_CANISTER_TRANSFER_RECOMMENDED, settings.BATCH_MFD_USER_ASSIGNED,
                    settings.BATCH_ALTERNATE_DRUG_SAVED]
    try:
        query = CanisterTransfers.select(CanisterTransfers.batch_id,
                                         fn.GROUP_CONCAT(fn.DISTINCT(CanisterTxMeta.id)).alias("meta_id")).dicts() \
            .join(CanisterTxMeta, JOIN_LEFT_OUTER, on=((CanisterTxMeta.id == CanisterTransfers.to_ct_meta_id) |
                                                       (CanisterTxMeta.id == CanisterTransfers.from_ct_meta_id))) \
            .join(BatchMaster, on=BatchMaster.id == CanisterTransfers.batch_id) \
            .where(BatchMaster.system_id == system_id,
                   BatchMaster.status << batch_status) \
            .order_by(BatchMaster.id) \
            .group_by(CanisterTransfers.batch_id)

        for record in query:
            if not record['meta_id']:
                batch_id = record['batch_id']
                break
        return batch_id

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pending_canister_transfer_batch_id {}".format(e))
        raise e


@log_args
def get_canister_tx_transfer_device_ids_by_status(batch_id: int, transfer_cycle_id: int, status: list,
                                                  device_id: int) -> tuple:
    """
    Function to get canister_tx_transfer data for given status and batch
    @param device_id:
    @param batch_id:
    @param transfer_cycle_id:
    @param status:
    @return:
    """
    device_system_dict = dict()
    logger.info("Inside get_canister_tx_transfer_data_by_status")

    try:
        device_count = CanisterTxMeta.select(CanisterTxMeta.id) \
            .where(CanisterTxMeta.batch_id == batch_id, CanisterTxMeta.cycle_id == transfer_cycle_id).count()

        query = CanisterTxMeta.select(CanisterTxMeta.device_id, DeviceMaster.system_id).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTxMeta.device_id) \
            .where(CanisterTxMeta.batch_id == batch_id, CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.status_id << status, CanisterTxMeta.device_id.not_in([device_id]))

        for record in query:
            device_system_dict[record['device_id']] = record['system_id']

        return device_system_dict, device_count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_canister_tx_transfer_device_ids_by_status {}".format(e))
        raise


@log_args_and_response
def get_batch_canister_list_sorted_by_quantity(batch_id: int, company_id: int) -> dict:
    """
    Function to get batch canister list sorted by quantity
    @param batch_id:
    @param company_id:
    @return:
    """
    logger.info("Inside get_batch_canister_list_sorted_by_quantity")
    canister_quantity_dict = dict()

    try:
        query = PackDetails.select(PackAnalysisDetails.canister_id,
                                   fn.SUM(fn.FLOOR(SlotDetails.quantity)).alias('required_qty')).dicts() \
            .join(PackAnalysis, on=((PackAnalysis.pack_id == PackDetails.id) &
                                    (PackAnalysis.batch_id == PackDetails.batch_id))) \
            .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
            .join(SlotDetails, on=SlotDetails.id == PackAnalysisDetails.slot_id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                   PackDetails.batch_id == batch_id,
                   PackDetails.company_id == company_id,
                   PackAnalysisDetails.status == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED
                   ) \
            .group_by(PackAnalysisDetails.canister_id).order_by(PackDetails.order_no)

        for record in query:
            if record['required_qty']:
                canister_quantity_dict[record['canister_id']] = float(record['required_qty'])

        sorted_canister_qty_dict = dict(sorted(canister_quantity_dict.items(), key=lambda item: item[1], reverse=True))

        return sorted_canister_qty_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_batch_canister_list_sorted_by_quantity {}".format(e))
        raise


@log_args
def add_alt_canister_in_canister_transfers(alt_canister: dict, batch_id: int, existing_canister_data: dict,
                                           transfer_status: int) -> bool:
    """
    FUnction to add alternate canister in canister transfer and update status of original canister
    @param transfer_status:
    @param existing_canister_data:
    @param alt_canister:
    @param batch_id:
    @return:
    """
    try:
        for original_can, alt_can in alt_canister.items():
            original_can = int(original_can)
            alt_can = int(alt_can)

            create_dict = {'canister_id': alt_can,
                           'batch_id': batch_id}

            update_dict = {'dest_device_id': existing_canister_data[original_can]['dest_device_id'],
                           'dest_quadrant': existing_canister_data[original_can]['dest_quadrant'],
                           'trolley_loc_id': existing_canister_data[original_can]['trolley_loc_id'],
                           'to_ct_meta_id': existing_canister_data[original_can]['to_ct_meta_id'],
                           'from_ct_meta_id': existing_canister_data[original_can]['from_ct_meta_id'],
                           'transfer_status': transfer_status,
                           'modified_date': get_current_date_time(),
                           'dest_location_number': None}

            logger.info("add_alt_canister_in_canister_transfers update_dict {}".format(update_dict))
            query = CanisterTransfers.db_update_or_create(create_dict=create_dict, update_dict=update_dict)
            logger.info("add_alt_canister_in_canister_transfers alternate canister added : {}".format(query))

        return True

    except ValueError as e:
        logger.error("Error in add_alt_canister_in_canister_transfers {}".format(e))
        raise ValueError
    except (InternalError, IntegrityError) as e:
        logger.error("Error in add_alt_canister_in_canister_transfers {}".format(e))
        raise


@log_args_and_response
def add_data_in_canister_transfer_history_tables(existing_canisters_data: dict,
                                                 original_canister: list,
                                                 skip_status: int,
                                                 action: int,
                                                 comment: [str, None],
                                                 user_id: int):
    """
    Function to insert data in canister transfer cycle history and canister transfer history comment
    @param existing_canisters_data:
    @param original_canister:
    @param skip_status:
    @param action:
    @param comment:
    @param user_id:
    @return:
    """
    try:
        for canister in original_canister:
            insert_data = {'canister_transfer_id': existing_canisters_data[canister]['id'],
                           'action_id': action,
                           'current_status_id': skip_status,
                           'previous_status_id': existing_canisters_data[canister]['transfer_status'],
                           'action_taken_by': user_id,
                           'action_datetime': get_current_date_time()
                           }

            # add data in CanisterTransferCycleHistory
            record = CanisterTransferCycleHistory.insert_canister_transfer_cycle_history_data(data_dict=insert_data)
            transfer_cycle_history = record.id
            logger.info("Data added in canister transfer cycle history {}".format(insert_data))

            if comment:
                comment_data = {'canister_tx_history_id': transfer_cycle_history, 'comment': comment}
                # add data in CanisterTransferHistoryComment
                comment_record = CanisterTransferHistoryComment.insert_canister_transfer_history_comment_data(data_dict=comment_data)
                comment_record_id = comment_record.id
                logger.info("Data added in canister transfer cycle history comment {}".format(comment_data))

                logger.info("Data added in canister transfer history tables {}, {}".format(transfer_cycle_history, comment_record_id))

        return True

    except ValueError as e:
        logger.error("Error in add_data_in_canister_transfer_history_tables {}".format(e))
        raise ValueError
    except (InternalError, IntegrityError) as e:
        logger.error("Error in add_data_in_canister_transfer_history_tables {}".format(e))
        raise


@log_args_and_response
def get_csr_canister_tx_meta_id_for_batch(batch_id: int) -> dict:
    """
    Function to get canister tx meta id for batch
    @param batch_id: int
    @return: tuple
    """
    cycle_status_dict = dict()

    try:

        query = CanisterTxMeta.select(CanisterTxMeta.id.alias('canister_tx_meta'),
                                      CanisterTxMeta.device_id,
                                      CanisterTxMeta.cycle_id,
                                      CanisterTxMeta.status_id,
                                      ).dicts() \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTxMeta.device_id) \
            .where(CanisterTxMeta.batch_id == batch_id,
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES['CSR'])

        for record in query:
            # cycle id in cycle id dict
            if record['cycle_id'] not in cycle_status_dict:
                cycle_status_dict[record['cycle_id']] = (record['canister_tx_meta'], record['status_id'])

        return cycle_status_dict

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_csr_canister_tx_meta_id_for_batch {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_csr_canister_tx_meta_id_for_batch {}".format(e))
        return cycle_status_dict


def add_record_in_canister_tx_meta(create_dict: dict, update_dict: dict) -> int:
    """
    Function to add record in canister tx meta
    @param create_dict:
    @param update_dict:
    @return:
    """

    try:
        query = CanisterTxMeta.db_update_or_create(create_dict=create_dict, update_dict=update_dict)
        return query.id

    except (InternalError, IntegrityError) as e:
        logger.error("error in add_record_in_canister_tx_meta {}".format(e))
        raise


@log_args_and_response
def get_pending_canister_transfers_by_device(batch_id: int, dest_device_id: int,
                                            transfer_cycle_id: int, sort_fields: list):
    """
    Function to get pending canisters list `i.e` for which transfer_later was done,
     or canisters that were on shelf and need to be transferred in given device
    @param batch_id:
    @param dest_device_id:
    @param transfer_cycle_id:
    @param sort_fields:
    @return:
    """
    try:
        order_list = list()
        fields_dict = {
            "source_drawer_number": ContainerMaster.drawer_name
        }
        order_list = get_orders(order_list, fields_dict, sort_fields)

        transfer_data = list()
        source_drawer_list = set()
        quad_type_dict = dict()
        canister_type_dict = {"small_canister_count": 0, "big_canister_count": 0, "delicate_canister_count": 0}
        LocationMasterAlias = LocationMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()

        query = CanisterTxMeta.select(
            CanisterMaster.location_id.alias('dest_location_id'),
            CanisterMaster.canister_type,
            CanisterMaster.active,
            CanisterTransfers.canister_id,
            DrugMaster.id.alias('drug_id'),
            DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.ndc,
            DrugMaster.image_name,
            DrugMaster.shape.alias("drug_shape"),
            DrugMaster.imprint,
            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
            fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by).alias(
                "stock_updated_by"),
            CustomDrugShape.id.alias("custom_drug_id"),
            CustomDrugShape.name,
            ContainerMaster.device_id.alias('cm_device_id'),
            ContainerMaster.serial_number,
            LocationMaster.display_location.alias("current_display_location"),
            DeviceMaster.device_type_id.alias('source_device_type_id'),
            LocationMaster.display_location.alias('source_display_location'),
            DeviceMaster.name.alias("current_device_name"),
            LocationMaster.quadrant.alias('cm_dest_quadrant'),
            LocationMaster.container_id.alias('cm_dest_drawer_id'),
            ContainerMaster.drawer_name,
            ContainerMaster.ip_address,
            ContainerMaster.secondary_ip_address,
            ContainerMaster.secondary_mac_address,
            ContainerMaster.mac_address,
            fn.replace(ContainerMaster.drawer_name, '-', '').alias('cm_dest_drawer_number'),
            LocationMaster.location_number.alias('source_location_number'),
            LocationMasterAlias.quadrant.alias('source_trolley_quadrant'),
            ContainerMasterAlias.device_id.alias('trolley_id'),
            ContainerMasterAlias.id.alias('trolley_drawer_id'),
            fn.replace(ContainerMasterAlias.drawer_name, '-', '').alias('trolley_drawer_number'),
            CanisterTransfers.dest_device_id,
            CanisterTransfers.dest_quadrant,
            CanisterTransfers.dest_location_number,
            CanisterTransfers.transfer_status,
            DeviceMasterAlias.device_type_id.alias('dest_device_type_id'),
            DeviceMasterAlias.name.alias("dest_device_name"),
            CanisterMaster.canister_type,
            ContainerMaster.drawer_type,
            DrugDetails.last_seen_by,
            DrugDetails.last_seen_date,
            UniqueDrug.is_delicate
        ) \
            .join(CanisterTransfers, on=CanisterTransfers.from_ct_meta_id == CanisterTxMeta.id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER,
                  on=(DrugStockHistory.unique_drug_id == DrugMaster.id) & (DrugStockHistory.is_active == True)) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                   (DrugDetails.company_id == CanisterMaster.company_id)) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(LocationMasterAlias, on=CanisterTransfers.trolley_loc_id == LocationMasterAlias.id) \
            .join(ContainerMasterAlias, on=ContainerMasterAlias.id == LocationMasterAlias.container_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=CanisterTransfers.dest_device_id == DeviceMasterAlias.id) \
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTransfers.transfer_status << [constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_LATER,
                                                         constants.CANISTER_TX_TO_ROBOT_ALTERNATE],
                    CanisterTxMeta.batch_id == batch_id,
                    CanisterTransfers.dest_device_id == dest_device_id,
                    CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_CSR_DONE
                   )\

        if order_list:
            query = query.order_by(*order_list)
        print("canister transfer to robot query: " + str(query))

        for record in query.dicts():
            if record['dest_quadrant'] not in quad_type_dict.keys():
                quad_type_dict[record['dest_quadrant']] = canister_type_dict

            if record['cm_device_id'] == record['dest_device_id'] and \
                    record['cm_dest_quadrant'] == record['dest_quadrant'] and not \
                    (record["canister_type"] == settings.SIZE_OR_TYPE["BIG"] and record["drawer_type"] == settings.SIZE_OR_TYPE["SMALL"]):
                continue

            if record['canister_type'] == settings.SIZE_OR_TYPE['BIG']:
                quad_type_dict[record['dest_quadrant']]["big_canister_count"] += 1
            else:
                if record['is_delicate']:
                    quad_type_dict[record['dest_quadrant']]["delicate_canister_count"] += 1
                else:
                    quad_type_dict[record['dest_quadrant']]["small_canister_count"] += 1

            if record['transfer_status'] == constants.CANISTER_TX_TO_ROBOT_ALTERNATE:
                record['alternate_canister'] = True
            else:
                record['alternate_canister'] = False

            transfer_data.append(record)
            source_drawer_list.add(record['cm_dest_drawer_id'])

        return transfer_data, list(source_drawer_list), quad_type_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in get_pending_canister_transfers_by_device {}".format(e))
        raise


@log_args_and_response
def get_pending_canisters_to_be_transferred_to_trolley(batch_id: int, source_device_id: int,
                                                      sort_fields: list, transfer_cycle_id: int) -> tuple:
    """
        Returns list of canisters to be transfer to particular drawer of given trolley from specified device for particular batch
    @param batch_id:
    @param source_device_id:
    @param transfer_cycle_id:
    @param sort_fields:
    @return:
    """
    try:
        order_list = list()
        fields_dict = {
            "source_drawer_number": ContainerMaster.drawer_name
        }
        order_list = get_orders(order_list, fields_dict, sort_fields)
        order_list.append(LocationMaster.location_number)
        transfer_data = list()
        drawers_to_unlock = dict()
        delicate_drawers_to_unlock = dict()

        DeviceMasterAlias = DeviceMaster.alias()
        LocationMasterAlias = LocationMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()
        DeviceMasterAlias2 = DeviceMaster.alias()

        query = CanisterTxMeta.select(
            CanisterMaster.active,
            CanisterTransfers.canister_id,
            DrugMaster.id.alias('drug_id'),
            DrugMaster.concated_drug_name_field(include_ndc=True).alias('drug_name'),
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.ndc,
            DrugMaster.image_name,
            DrugMaster.shape.alias("drug_shape"),
            DrugMaster.imprint,
            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
            fn.IF(DrugStockHistory.created_by.is_null(True), None, DrugStockHistory.created_by).alias(
                "stock_updated_by"),
            CustomDrugShape.id,
            CustomDrugShape.name,
            ContainerMaster.device_id.alias('source_device_id'),
            LocationMaster.quadrant.alias('source_quadrant'),
            LocationMaster.container_id.alias('source_drawer_id'),
            DeviceMaster.name.alias("current_device_name"),
            fn.replace(ContainerMaster.drawer_name, '-', '').alias('source_drawer_number'),
            ContainerMaster.drawer_name,
            ContainerMaster.serial_number.alias("source_drawer_serial_number"),
            ContainerMaster.ip_address.alias("source_drawer_ip"),
            ContainerMaster.secondary_ip_address.alias("source_drawer_sec_ip"),
            LocationMaster.location_number.alias('source_location_number'),
            LocationMaster.display_location.alias('source_display_location'),
            ContainerMasterAlias.device_id.alias('trolley_id'),
            ContainerMasterAlias.id.alias('trolley_drawer_id'),
            ContainerMaster.serial_number,
            ContainerMasterAlias.drawer_name.alias('trolley_drawer_number'),
            CanisterTransfers.dest_device_id,
            DeviceMasterAlias.device_type_id.alias('dest_device_type_id'),
            CanisterTransfers.dest_quadrant,
            CanisterTransfers.dest_location_number,
            CanisterTransfers.transfer_status,
            ContainerMaster.shelf,
            DeviceMaster.device_type_id,
            LocationMasterAlias.container_id,
            LocationMasterAlias.display_location.alias("trolley_location"),
            LocationMasterAlias.device_id.alias("trolley_device_id"),
            DrugDetails.last_seen_by,
            DrugDetails.last_seen_date,
            DeviceMasterAlias2.name.alias("trolley_device_name"),
            UniqueDrug.is_delicate
        ) \
            .join(CanisterTransfers, on=CanisterTxMeta.id == CanisterTransfers.to_ct_meta_id) \
            .join(DeviceMasterAlias, on=DeviceMasterAlias.id == CanisterTransfers.dest_device_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER,
                  on=(DrugStockHistory.unique_drug_id == DrugMaster.id) & (DrugStockHistory.is_active == True)
                  & (DrugStockHistory.company_id == CanisterMaster.company_id)) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                   (DrugDetails.company_id == CanisterMaster.company_id)) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id)\
            .join(LocationMasterAlias, on=CanisterTransfers.trolley_loc_id == LocationMasterAlias.id) \
            .join(ContainerMasterAlias, on=ContainerMasterAlias.id == LocationMasterAlias.container_id) \
            .join(DeviceMasterAlias2, on=DeviceMasterAlias2.id == ContainerMasterAlias.device_id)\
            .where(CanisterTxMeta.cycle_id == transfer_cycle_id,
                   CanisterTxMeta.batch_id == batch_id,
                   CanisterTxMeta.device_id == source_device_id,
                   CanisterTxMeta.status_id == constants.CANISTER_TRANSFER_RECOMMENDATION_DONE,
                   CanisterMaster.active == settings.is_canister_active,
                   CanisterTransfers.transfer_status << [constants.CANISTER_TX_TO_TROLLEY_ALTERNATE_TRANSFER_LATER,
                                                         constants.CANISTER_TX_TO_TROLLEY_ALTERNATE])

        if order_list:
            query = query.order_by(*order_list)

        print("canister transfer to trolley query: " + str(query))
        for record in query.dicts():
            if record['source_drawer_id'] == record['container_id']:
                continue

            if record['transfer_status'] == constants.CANISTER_TX_TO_TROLLEY_ALTERNATE:
                record['alternate_canister'] = True
            else:
                record['alternate_canister'] = False

            transfer_data.append(record)
            if record["is_delicate"]:
                if record["drawer_name"] not in delicate_drawers_to_unlock.keys():
                    delicate_drawers_to_unlock[record["drawer_name"]] = {"id": record["source_drawer_id"],
                                                                "drawer_name": record["drawer_name"],
                                                                "serial_number": record["source_drawer_serial_number"],
                                                                "ip_address": record["source_drawer_ip"],
                                                                "secondary_ip_address": record["source_drawer_sec_ip"],
                                                                "from_device": list(),
                                                                "to_device": list(),
                                                                "shelf": record["shelf"],
                                                                "device_type_id": record["device_type_id"]
                                                                }
                    delicate_drawers_to_unlock[record["drawer_name"]]["from_device"].append(record["source_display_location"])
            else:
                if record["drawer_name"] not in drawers_to_unlock.keys():
                    drawers_to_unlock[record["drawer_name"]] = {"id": record["source_drawer_id"],
                                                                "drawer_name": record["drawer_name"],
                                                                "serial_number": record["source_drawer_serial_number"],
                                                                "ip_address": record["source_drawer_ip"],
                                                                "secondary_ip_address": record["source_drawer_sec_ip"],
                                                                "from_device": list(),
                                                                "to_device": list(),
                                                                "shelf": record["shelf"],
                                                                "device_type_id": record["device_type_id"]
                                                                }

                drawers_to_unlock[record["drawer_name"]]["from_device"].append(record["source_display_location"])

        return transfer_data, drawers_to_unlock,delicate_drawers_to_unlock
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pending_canisters_to_be_transferred_to_trolley {}".format(e))
        raise

@log_args_and_response
def db_canister_transfer_replace_canister(batch_id, canister_id, alt_canister_id):
    try:
        return CanisterTransfers.db_replace_canister(batch_id, canister_id, alt_canister_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_canister_transfer_replace_canister {}".format(e))
        raise


@log_args_and_response
def canister_transfer_get_or_create_data(batch_id, canister_id, update_dict):
    try:
        return CanisterTransfers.get_or_create(batch_id=batch_id, canister_id=canister_id, defaults=update_dict)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in canister_transfer_get_or_create_data {}".format(e))
        raise


@log_args_and_response
def db_reserved_canister_replace_canister(canister_id, alt_canister_id):
    try:
        return ReservedCanister.db_replace_canister(canister_id=canister_id,
                                                    alt_canister_id=alt_canister_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_reserved_canister_replace_canister {}".format(e))
        raise


@log_args_and_response
def db_get_quad_drawer_type_wise_empty_unreserved_locations(company_id: int, batch_id: int, system_id: int,
                                                            device_type: int) -> tuple:
    """
    Function to get
    @param device_type:
    @param batch_id:
    @param company_id:
    @param system_id: int
    @return:
    """
    device_quad_drawer_empty_locations = dict()
    device_quad_drawer_unreserved_locations = dict()
    device_quad_drawer_non_delicate_unreserved_locations = dict()
    slow_movers_quad_drawer_empty_locations = dict()
    not_slow_movers_quad_drawer_empty_locations = dict()

    clauses = [LocationMaster.is_disabled == settings.is_location_active]
    try:
        reserved_canisters = ReservedCanister.db_get_reserved_canister(company_id=company_id,
                                                                       batch_id=batch_id,
                                                                       skip_canisters=None)

        if len(reserved_canisters):
            clauses.append(((CanisterMaster.id.is_null(True)) | (CanisterMaster.id.not_in(reserved_canisters))))

        if device_type:
            clauses.extend([DeviceMaster.device_type_id == device_type,
                            DeviceMaster.system_id == system_id])

        clauses.append(ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['BIG'],
                                                       settings.SIZE_OR_TYPE['SMALL']])
    #
        # query to get available empty and unreserved locations
        empty_locations = LocationMaster.select(LocationMaster,
                                                CanisterMaster.id.alias('existing_canister_id'),
                                                CanisterMaster.canister_type,
                                                ContainerMaster.ip_address,
                                                ContainerMaster.secondary_ip_address,
                                                ContainerMaster.mac_address,
                                                ContainerMaster.secondary_mac_address,
                                                ContainerMaster.id.alias('container_id'),
                                                ContainerMaster.serial_number,
                                                ContainerMaster.drawer_type,
                                                ContainerMaster.drawer_level,
                                                DeviceMaster.name.alias("device_name"),
                                                DeviceMaster.device_type_id,
                                                ContainerMaster.drawer_name.alias('drawer_number'),
                                                UniqueDrug.drug_usage,
                                                UniqueDrug.is_delicate).dicts() \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=((CanisterMaster.location_id == LocationMaster.id) &
                                                       (CanisterMaster.company_id == company_id))) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DrugMaster, JOIN_LEFT_OUTER, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                   (UniqueDrug.txr == DrugMaster.txr))) \
            .where(*clauses) \
            .order_by(ContainerMaster.drawer_level, CanisterMaster.id,UniqueDrug.is_delicate)

        # create the response dict with keeping device, quad, drawer_type as the key
        for record in empty_locations:
            if record["device_id"] not in device_quad_drawer_empty_locations.keys():
                device_quad_drawer_empty_locations[record["device_id"]] = dict()
                device_quad_drawer_unreserved_locations[record["device_id"]] = dict()
                device_quad_drawer_non_delicate_unreserved_locations[record["device_id"]] = dict()

            if record["quadrant"] not in device_quad_drawer_empty_locations[record["device_id"]].keys():
                device_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]] = dict()
                device_quad_drawer_unreserved_locations[record["device_id"]][record["quadrant"]] = dict()
                device_quad_drawer_non_delicate_unreserved_locations[record["device_id"]][record["quadrant"]] = dict()

            if record["drawer_type"] not in device_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]].keys():
                device_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]][
                    record["drawer_type"]] = list()
                device_quad_drawer_unreserved_locations[record["device_id"]][record["quadrant"]][
                    record["drawer_type"]] = list()
                device_quad_drawer_non_delicate_unreserved_locations[record["device_id"]][record["quadrant"]][
                    record["drawer_type"]] = list()

            if record["existing_canister_id"]:
                if not record['is_delicate'] and record['drawer_level']>1 and record['drawer_level']<5:
                    device_quad_drawer_non_delicate_unreserved_locations[record["device_id"]][record["quadrant"]][
                        record["drawer_type"]].append(record)
                else:
                    device_quad_drawer_unreserved_locations[record["device_id"]][record["quadrant"]][
                        record["drawer_type"]].append(record)
            else:
                device_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]][
                    record["drawer_type"]].append(record)
        # slow_movers = CanisterMaster.select(LocationMaster,
        #                                     CanisterMaster.id.alias('existing_canister_id'),
        #                                     CanisterMaster.canister_type,
        #                                     ContainerMaster.ip_address,
        #                                     ContainerMaster.id.alias('container_id'),
        #                                     ContainerMaster.secondary_ip_address,
        #                                     ContainerMaster.mac_address,
        #                                     ContainerMaster.secondary_mac_address,
        #                                     ContainerMaster.serial_number,
        #                                     ContainerMaster.drawer_type,
        #                                     ContainerMaster.drawer_level,
        #                                     DeviceMaster.name.alias("device_name"),
        #                                     DeviceMaster.device_type_id,
        #                                     ContainerMaster.drawer_name.alias('drawer_number'),
        #                                     UniqueDrug.drug_usage,
        #                                     UniqueDrug.is_delicate,
        #                                     CanisterTransfers.dest_quadrant,
        #                                     CanisterTransfers.dest_device_id).dicts() \
        #     .join(LocationMaster, on=((CanisterMaster.location_id == LocationMaster.id) &
        #                                         (CanisterMaster.company_id == company_id)))\
        #     .join(CanisterTransfers, on=CanisterMaster.id == CanisterTransfers.canister_id)\
        #     .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
        #     .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
        #     .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
        #     .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
        #                           (UniqueDrug.txr == DrugMaster.txr))) \
        #     .where(DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT'],
        #            ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['BIG'],
        #                                            settings.SIZE_OR_TYPE['SMALL']],
        #            ContainerMaster.drawer_level <= constants.MAX_DELICATE_DRAWER_LEVEL,
        #            LocationMaster.is_disabled == settings.is_location_active,
        #            CanisterTransfers.batch_id == batch_id,
        #            UniqueDrug.is_delicate != constants.DELICATE_CANISTER) \
        #     .order_by(ContainerMaster.drawer_level, CanisterMaster.id)
        # for record in slow_movers:
        #     if record['dest_device_id'] == record['device_id'] and record['dest_quadrant'] == record['quadrant']:
        #         if record['drug_usage'] == constants.USAGE_SLOW_MOVING:
        #             if record["device_id"] not in slow_movers_quad_drawer_empty_locations.keys():
        #                 slow_movers_quad_drawer_empty_locations[record["device_id"]] = dict()
        #
        #             if record["quadrant"] not in slow_movers_quad_drawer_empty_locations[record["device_id"]].keys():
        #                 slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]] = dict()
        #             if record["drawer_type"] not in slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]].keys():
        #                 slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]][
        #                     record["drawer_type"]] = list()
        #             slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]][
        #                 record["drawer_type"]].append(record)
        #         else:
        #             if record["device_id"] not in not_slow_movers_quad_drawer_empty_locations.keys():
        #                 not_slow_movers_quad_drawer_empty_locations[record["device_id"]] = dict()
        #
        #             if record["quadrant"] not in not_slow_movers_quad_drawer_empty_locations[record["device_id"]].keys():
        #                 not_slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]] = dict()
        #             if record["drawer_type"] not in not_slow_movers_quad_drawer_empty_locations[record["device_id"]][
        #                 record["quadrant"]].keys():
        #                 not_slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]][
        #                     record["drawer_type"]] = list()
        #             not_slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]][
        #                 record["drawer_type"]].append(record)
        return device_quad_drawer_empty_locations, device_quad_drawer_unreserved_locations, \
            device_quad_drawer_non_delicate_unreserved_locations

    except(IntegrityError, IntegrityError, ValueError, DataError) as e:
        logger.error("error in db_get_quad_drawer_type_wise_empty_unreserved_locations {}".format(e))
        raise

    except DoesNotExist as e:
        logger.error("error in db_get_quad_drawer_type_wise_empty_unreserved_locations {}".format(e))
        return device_quad_drawer_empty_locations, device_quad_drawer_unreserved_locations, \
            slow_movers_quad_drawer_empty_locations
    except Exception as e:
        logger.error("error in db_get_quad_drawer_type_wise_empty_unreserved_locations {}".format(e))
        return e


@log_args_and_response
def db_update_canister_tx_meta(update_dict: dict, meta_id: int):
    """

    @param update_dict:
    @param meta_id:
    @return:
    """
    try:
        status = CanisterTxMeta.update_canister_tx_data(update_dict=update_dict,
                                                        meta_id=meta_id)
        return status
    except(IntegrityError, IntegrityError, ValueError, DataError) as e:
        logger.error("error in db_update_canister_tx_meta {}".format(e))
        raise


@log_args_and_response
def get_location_data_from_device_ids(device_id_list):
    try:
        location_info = dict()
        drawer_location_info = dict()
        location_device_dict = dict()
        query = LocationMaster.select(LocationMaster.id.alias('device_location_id'), LocationMaster, DeviceMaster.id.alias('device_id'),
                           DeviceMaster, LocationMaster.container_id.alias('drawer_id')) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, on=ContainerMaster.device_id == DeviceMaster.id) \
            .where(LocationMaster.device_id << device_id_list) \
            .order_by(DeviceMaster.id, LocationMaster.container_id, LocationMaster.id) \
            .group_by(LocationMaster.id)

        for record in query.dicts():
            if record['device_type_id'] not in location_info.keys():
                location_info[record['device_type_id']] = dict()

            # if record['device_id'] not in location_info[record['device_type_id']].keys():
            #     location_info[record['device_type_id']][record['device_id']] = dict()

            if record['device_id'] not in drawer_location_info.keys():
                drawer_location_info[record['device_id']] = dict()

            if record['drawer_id'] not in drawer_location_info[record['device_id']].keys():
                drawer_location_info[record['device_id']][record['drawer_id']] = list()
            drawer_location_info[record['device_id']][record['drawer_id']].append(record['device_location_id'])

            if record['drawer_id'] not in location_info[record['device_type_id']].keys():
                location_info[record['device_type_id']][record['drawer_id']] = list()
            location_info[record['device_type_id']][record['drawer_id']].append(
                (record['device_location_id'], record['location_number'], record['quadrant'],
                 record['display_location']))
            location_device_dict[record['device_location_id']] = record['device_id']

        return location_info, drawer_location_info, location_device_dict
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_location_data_from_device_ids {}".format(e))
        raise
    except DoesNotExist as e:
        logger.error("error in get_location_data_from_device_ids {}".format(e))
        raise NoLocationExists


@log_args_and_response
def insert_canister_transfer_cycle_history_data_dao(data_dict: dict):
    """
    This function inserts multiple records to the canister_transfer_cycle_history table.
    """
    try:
        return CanisterTransferCycleHistory.insert_canister_transfer_cycle_history_data(data_dict=data_dict)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in insert_canister_transfer_cycle_history_data_dao:  {}".format(e))
        raise e


@log_args_and_response
def add_canister_history_data_dao(canister_history_dict: dict) -> object:
    try:
        return BaseModel.db_create_record(canister_history_dict, CanisterHistory)
    except (DataError, IntegrityError, InternalError) as e:
        logger.error("error in add_canister_history_data_dao:  {}".format(e))
        raise e


@log_args_and_response
def db_update_canister_tx_status_dao(batch_id, canister_id_list, status):
    try:
        return CanisterTransfers.db_update_canister_tx_status(batch_id, canister_id_list, status)
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_update_canister_tx_status_dao {}".format(e))
        raise e


@log_args_and_response
def get_canister_transfer_data(batch_id: int, canister_id_list: list, transfer_status: [list, None]) -> dict:
    """

    @param transfer_status:
    @param batch_id:
    @param canister_id_list:
    @return:
    """
    logger.info("Input of db_get_canister_transfer_data {}, {}".format(batch_id, canister_id_list))
    canister_info_dict = dict()
    try:
        clauses = [CanisterTransfers.canister_id << canister_id_list,
                   CanisterTransfers.batch_id == batch_id]

        if transfer_status:
            clauses.append((CanisterTransfers.transfer_status << transfer_status))
        else:
            clauses.append((CanisterTransfers.transfer_status.not_in(constants.canister_tx_existing_status_list)))

        query = CanisterTransfers.select(CanisterTransfers,
                                         LocationMaster.id.alias('location_id'),
                                         DeviceMaster.device_type_id,
                                         LocationMaster.display_location.alias('can_display_location')).dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .where(*clauses)

        for record in query:
            canister_info_dict[int(record['canister_id'])] = record

        logger.info("Output of get_canister_transfer_data {}".format(canister_info_dict))
        return canister_info_dict

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_canister_transfer_data {}".format(e))
        raise


@log_args_and_response
def db_get_pending_transfers(batch_id):
    """
    List of pending canisters need to put in Robot for given batch ID
    Now suggestion can be to put particular canister to csr so adding robot check
    :param batch_id: Batch ID
    :return: generator
    """
    try:
        DeviceMasterAlias = DeviceMaster.alias()

        CanisterHistoryAlias = CanisterHistory.alias()

        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias2 = DeviceMaster.alias()
        CanisterTransferCycleHistoryAlias = CanisterTransferCycleHistory.alias()

        sub_query = CanisterHistoryAlias.select(fn.MAX(CanisterHistoryAlias.id).alias('max_canister_history_id'),
                                                CanisterHistoryAlias.canister_id.alias('canister_id')) \
            .group_by(CanisterHistoryAlias.canister_id).alias('sub_query')

        sub_query_1 = CanisterTransferCycleHistoryAlias.select(
            fn.MAX(CanisterTransferCycleHistoryAlias.id).alias('max_canister_transfer_cycle_id'),
            CanisterTransferCycleHistoryAlias.canister_transfer_id.alias('canister_transfer_id')) \
            .group_by(CanisterTransferCycleHistoryAlias.canister_transfer_id).alias('sub_query_1')

        sub_query_skip_deactivate_reason = CanisterStatusHistory.select(
            fn.MAX(CanisterStatusHistory.id).alias("max_status_history_id"),
            CanisterStatusHistory.canister_id.alias("canister_status_canister_id")) \
            .where(CanisterStatusHistory.action == constants.CODE_MASTER_CANISTER_DEACTIVATE).group_by(
            CanisterStatusHistory.canister_id).alias('sub_query_skip_deactivate_reason')

        query = CanisterTransfers.select(DrugMaster,
                                         CanisterTransfers.id.alias('canister_transfer_id'),
                                         CanisterTransfers.dest_device_id,
                                         CanisterTransfers.dest_quadrant,
                                         CanisterTransfers.batch_id,
                                         CanisterTransfers.transfer_status,
                                         CanisterTransferCycleHistory.action_id,
                                         fn.IF(
                                             CanisterTransferCycleHistory.action_id == constants.CANISTER_TX_SKIPPED_AND_DEACTIVATE_ACTION,
                                             CanisterStatusHistoryComment.comment,
                                             CanisterTransferHistoryComment.comment).alias('comment'),
                                         CanisterMaster.id,
                                         CanisterMaster.rfid,
                                         CanisterMaster.active,
                                         CanisterMaster.canister_type,
                                         fn.IF(
                                             CanisterMaster.expiry_date <= date.today() + timedelta(
                                                 settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                                             constants.EXPIRED_CANISTER,
                                             fn.IF(
                                                 CanisterMaster.expiry_date <= date.today() + timedelta(
                                                     settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                                                 constants.EXPIRES_SOON_CANISTER,
                                                 constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
                                         CanisterMaster.expiry_date,
                                         UniqueDrug.drug_usage,
                                         LocationMaster.device_id.alias('source_device_id'),
                                         LocationMaster.quadrant.alias('source_quadrant'),
                                         DeviceMaster.name.alias('source_device_name'),
                                         DeviceMaster.serial_number.alias('source_serial_number'),
                                         ContainerMaster.drawer_level.alias('source_drawer_level'),
                                         LocationMaster.container_id.alias('source_container_id'),
                                         ContainerMaster.drawer_type.alias('source_drawer_type'),
                                         DeviceMasterAlias.serial_number.alias('dest_serial_number'),
                                         DeviceMasterAlias.name.alias('dest_device_name'),
                                         DeviceMasterAlias.device_type_id.alias('dest_device_type_id'),
                                         LocationMaster.location_number,
                                         CanisterMaster.available_quantity,
                                         fn.IF(CanisterMaster.available_quantity < 0, 0,
                                               CanisterMaster.available_quantity).alias('display_quantity'),
                                         LocationMaster.location_number,
                                         ContainerMaster.drawer_name.alias('source_drawer_name'),
                                         ContainerMaster.drawer_level,
                                         ContainerMaster.id.alias('container_id'),
                                         LocationMaster.display_location,
                                         DeviceMaster.device_type_id.alias('source_device_type_id'),
                                         ZoneMaster.id.alias('zone_id'),
                                         ZoneMaster.name.alias('zone_name'),
                                         DeviceLayoutDetails.id.alias('device_layout_id'),
                                         DeviceMaster.name.alias('device_name'),
                                         DeviceMaster.id.alias('device_id'),
                                         DeviceTypeMaster.device_type_name,
                                         DeviceTypeMaster.id.alias('device_type_id'),
                                         ContainerMaster.ip_address,
                                         ContainerMaster.secondary_ip_address,
                                         fn.IF(CanisterHistory.previous_location_id.is_null(True), None,
                                               CanisterHistory.created_date).alias('last_seen_time'),
                                         DeviceMasterAlias2.name.alias('previous_device_name'),
                                         LocationMasterAlias.id.alias('previous_location_id'),
                                         LocationMasterAlias.display_location.alias('previous_display_location'),
                                         fn.IF(CanisterMaster.location_id.is_null(True), -1,
                                               LocationMaster.get_device_location()).alias('canister_location'),
                                         UniqueDrug.is_delicate.alias('is_delicate')
                                         ).dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                  & (fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                     fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)))) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, DeviceMasterAlias.id == CanisterTransfers.dest_device_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
            .join(ZoneMaster, JOIN_LEFT_OUTER, DeviceLayoutDetails.zone_id == ZoneMaster.id) \
            .join(sub_query_1, JOIN_LEFT_OUTER, on=sub_query_1.c.canister_transfer_id == CanisterTransfers.id) \
            .join(CanisterTransferCycleHistory, JOIN_LEFT_OUTER,
                  on=CanisterTransferCycleHistory.id == sub_query_1.c.max_canister_transfer_cycle_id) \
            .join(CanisterTransferHistoryComment, JOIN_LEFT_OUTER,
                  on=CanisterTransferHistoryComment.canister_tx_history_id == CanisterTransferCycleHistory.id) \
            .join(sub_query, JOIN_LEFT_OUTER,
                  on=(sub_query.c.canister_id == CanisterMaster.id)) \
            .join(CanisterHistory, JOIN_LEFT_OUTER, on=(CanisterHistory.id == sub_query.c.max_canister_history_id)) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER,
                  on=(CanisterHistory.previous_location_id == LocationMasterAlias.id)) \
            .join(DeviceMasterAlias2, JOIN_LEFT_OUTER, on=(LocationMasterAlias.device_id == DeviceMasterAlias2.id)) \
            .join(sub_query_skip_deactivate_reason, JOIN_LEFT_OUTER,
                  on=(sub_query_skip_deactivate_reason.c.canister_status_canister_id == CanisterMaster.id)) \
            .join(CanisterStatusHistoryComment, JOIN_LEFT_OUTER,
                  on=(
                              sub_query_skip_deactivate_reason.c.max_status_history_id ==
                              CanisterStatusHistoryComment.canister_status_history_id)) \
            .where(CanisterTransfers.batch_id == batch_id,
                   CanisterTransfers.dest_device_id.is_null(False),
                   DeviceMasterAlias.device_type_id == settings.DEVICE_TYPES['ROBOT']
                   # CanisterTransfers.dest_robot_id != fn.IFNULL(CanisterMaster.robot_id, 0),
                   # commenting to show replenish required canisters
                   ).order_by(UniqueDrug.is_delicate.desc())
        for record in query:
            yield record
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_pending_transfers {}".format(e))
        raise


@log_args_and_response
def db_get_remove_canister_list(batch_id, system_id):
    """
    Canisters list which needs to be
    :param batch_id: Batch ID
    :param system_id: System ID
    :return: generator
    """
    try:
        required_canister = CanisterTransfers.select(CanisterTransfers.canister_id, ) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTransfers.dest_device_id) \
            .where(DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT'],
                   CanisterTransfers.batch_id == batch_id)

        CanisterTransfersAlias = CanisterTransfers.alias()
        CanisterHistoryAlias = CanisterHistory.alias()

        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()

        CanisterTransferCycleHistoryAlias = CanisterTransferCycleHistory.alias()

        # for getting csr destination info
        LocationMasterAlias1 = LocationMaster.alias()
        DeviceMasterAlias1 = DeviceMaster.alias()
        ContainerMasterAlias = ContainerMaster.alias()

        sub_query = CanisterHistoryAlias.select(fn.MAX(CanisterHistoryAlias.id).alias('max_canister_history_id'),
                                                CanisterHistoryAlias.canister_id.alias('canister_id')) \
            .group_by(CanisterHistoryAlias.canister_id).alias('sub_query')

        sub_query_1 = CanisterTransferCycleHistoryAlias.select(
            fn.MAX(CanisterTransferCycleHistoryAlias.id).alias('max_canister_transfer_cycle_id'),
            CanisterTransferCycleHistoryAlias.canister_transfer_id.alias('canister_transfer_id')) \
            .group_by(CanisterTransferCycleHistoryAlias.canister_transfer_id).alias('sub_query_1')

        sub_query_skip_deactivate_reason = CanisterStatusHistory.select(
            fn.MAX(CanisterStatusHistory.id).alias("max_status_history_id"),
            CanisterStatusHistory.canister_id.alias("canister_status_canister_id")) \
            .where(CanisterStatusHistory.action == constants.CODE_MASTER_CANISTER_DEACTIVATE).group_by(
            CanisterStatusHistory.canister_id).alias('sub_query_skip_deactivate_reason')

        query = CanisterMaster.select(
            DrugMaster,
            CanisterMaster.id,
            CanisterMaster.rfid,
            CanisterMaster.canister_type,
            fn.IF(
                CanisterMaster.expiry_date <= date.today() + timedelta(
                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                constants.EXPIRED_CANISTER,
                fn.IF(
                    CanisterMaster.expiry_date <= date.today() + timedelta(
                        settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                    constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
            CanisterMaster.expiry_date,
            UniqueDrug.drug_usage,
            LocationMaster.device_id.alias('source_device_id'),
            LocationMaster.quadrant.alias('source_quadrant'),
            DeviceMaster.id.alias('source_device_id'),
            DeviceMaster.name.alias('source_device_name'),
            ContainerMaster.id.alias('source_container_id'),
            ContainerMaster.drawer_name.alias('source_drawer_name'),
            ContainerMaster.drawer_level.alias('source_drawer_level'),
            ContainerMaster.drawer_type.alias('source_drawer_type'),
            DeviceMaster.device_type_id.alias('source_device_type_id'),
            DeviceMaster.serial_number.alias('source_serial_number'),
            CanisterMaster.available_quantity,
            fn.IF(CanisterMaster.available_quantity < 0, 0, CanisterMaster.available_quantity).alias(
                'display_quantity'),
            LocationMaster.location_number,
            CanisterMaster.active,
            CanisterMaster.canister_type,
            LocationMaster.display_location,
            fn.IF(CanisterHistory.previous_location_id.is_null(True), None, CanisterHistory.created_date).alias(
                'last_seen_time'),
            DeviceMasterAlias.name.alias('previous_device_name'),
            LocationMasterAlias.id.alias('previous_location_id'),
            LocationMasterAlias.display_location.alias('previous_display_location'),
            CanisterTransfersAlias.id.alias('canister_transfer_id'),
            CanisterTransfersAlias.dest_device_id,
            CanisterTransfersAlias.dest_quadrant,
            CanisterTransfersAlias.transfer_status,
            fn.IF(CanisterTransferCycleHistory.action_id == constants.CANISTER_TX_SKIPPED_AND_DEACTIVATE_ACTION,
                  CanisterStatusHistoryComment.comment,
                  CanisterTransferHistoryComment.comment).alias('comment'),
            DeviceMasterAlias1.device_type_id.alias('dest_device_type_id'),
            DeviceMasterAlias1.name.alias('dest_device_name'),
            DeviceMasterAlias1.serial_number.alias('dest_serial_number'),
            ContainerMasterAlias.id.alias('dest_container_id'),
            ContainerMasterAlias.drawer_name.alias('dest_drawer_name'),
            ContainerMasterAlias.drawer_level.alias('dest_drawer_level'),
            ContainerMasterAlias.drawer_type.alias('dest_drawer_type'),
            fn.IF(CanisterMaster.location_id.is_null(True), -1,
                  LocationMaster.get_device_location()).alias('canister_location'),
            UniqueDrug.is_delicate.alias('is_delicate')
        ) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(sub_query, JOIN_LEFT_OUTER,
                  on=(sub_query.c.canister_id == CanisterMaster.id)) \
            .join(CanisterHistory, JOIN_LEFT_OUTER, on=(CanisterHistory.id == sub_query.c.max_canister_history_id)) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER,
                  on=(CanisterHistory.previous_location_id == LocationMasterAlias.id)) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=(LocationMasterAlias.device_id == DeviceMasterAlias.id)) \
            .join(CanisterTransfersAlias, JOIN_LEFT_OUTER,
                  on=((CanisterTransfersAlias.canister_id == CanisterMaster.id)
                      & (CanisterTransfersAlias.batch_id == batch_id))) \
            .join(sub_query_1, JOIN_LEFT_OUTER, on=sub_query_1.c.canister_transfer_id == CanisterTransfersAlias.id) \
            .join(CanisterTransferCycleHistory, JOIN_LEFT_OUTER,
                  on=CanisterTransferCycleHistory.id == sub_query_1.c.max_canister_transfer_cycle_id) \
            .join(CanisterTransferHistoryComment, JOIN_LEFT_OUTER,
                  on=CanisterTransferHistoryComment.canister_tx_history_id == CanisterTransferCycleHistory.id) \
            .join(LocationMasterAlias1, JOIN_LEFT_OUTER, on=(
                (LocationMasterAlias1.location_number == CanisterTransfersAlias.dest_location_number) &
                (LocationMasterAlias1.device_id == CanisterTransfersAlias.dest_device_id))) \
            .join(DeviceMasterAlias1, JOIN_LEFT_OUTER, on=DeviceMasterAlias1.id == LocationMasterAlias1.device_id) \
            .join(ContainerMasterAlias, JOIN_LEFT_OUTER,
                  on=ContainerMasterAlias.id == LocationMasterAlias1.container_id) \
            .join(sub_query_skip_deactivate_reason, JOIN_LEFT_OUTER,
                  on=(sub_query_skip_deactivate_reason.c.canister_status_canister_id == CanisterMaster.id)) \
            .join(CanisterStatusHistoryComment, JOIN_LEFT_OUTER,
                  on=(
                              sub_query_skip_deactivate_reason.c.max_status_history_id == CanisterStatusHistoryComment.canister_status_history_id)) \
            .where(DeviceMaster.system_id == system_id,
                   DeviceMaster.device_type_id.not_in([settings.DEVICE_TYPES['CSR']]),
                   CanisterMaster.id.not_in(required_canister))\
            .order_by(UniqueDrug.is_delicate.desc())
        # (CanisterTransfersAlias.id.is_null(True)) | (CanisterTransfersAlias.batch_id == batch_id))

        for record in query.dicts():
            yield record
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_get_remove_canister_list {}".format(e))
        raise


@log_args_and_response
def get_canister_destination(batch_id):
    """
    Returns destination of canister for given batch ID
    - format: dict - key = canister_id, value = dict containing destination data
    :param batch_id:
    :return:
    """
    try:
        results = dict()
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        query = CanisterTransfers.select(
            CanisterTransfers.canister_id,
            CanisterTransfers.dest_device_id,
            DeviceMaster.name.alias('dest_device_name'),
            DeviceMasterAlias.name.alias('source_device_name'),
            DeviceMasterAlias.id.alias('source_device_id'),
        ) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=CanisterTransfers.dest_device_id == DeviceMaster.id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMasterAlias.id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMasterAlias.device_id) \
            .where(CanisterTransfers.batch_id == batch_id)
        for record in query.dicts():
            results[record["canister_id"]] = record
        return results
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_canister_destination {}".format(e))
        raise


@log_args_and_response
def db_get_latest_canister_transfer_data_for_a_canister_from_robot_csr(canister_id):
    """
    @return latest canister transfer data of given canister from given device
    """
    try:
        LocationMasterAlias = LocationMaster.alias()
        DeviceMasterAlias = DeviceMaster.alias()
        # CanisterTxMetaAlias = CanisterTxMeta.alias()
        #
        # sub_query = CanisterTransfers.select(fn.MAX(CanisterTransfers.id).alias('latest_canister_transfer_id')) \
        #     .join(CanisterTxMeta, on=CanisterTransfers.to_ct_meta_id == CanisterTxMeta.id) \
        #     .where(CanisterTransfers.canister_id == canister_id,
        #            CanisterTransfers.trolley_loc_id.is_null(False),
        #            CanisterTxMeta.status_id == constants.CANISTER_TRANSFER_RECOMMENDATION_DONE)\
        #     .alias('sub_query')
        # logger.info("sub: " + str(sub_query.dicts().get()))
        # latest_canister_transfer_id = sub_query.dicts().get()['latest_canister_transfer_id']
        query = CanisterTransfers.select(
            CanisterTransfers.canister_id,
            CanisterTransfers.dest_device_id,
            CanisterTransfers.batch_id,
            DeviceMaster.system_id.alias('dest_system_id'),
            CanisterTransfers.trolley_loc_id,
            CanisterTransfers.transfer_status,
            CanisterTxMeta.status_id,
            BatchMaster.status.alias("batch_status_id"),
            CanisterTransfers.id.alias('transfer_id'),
            LocationMaster.id.alias('can_source_loc_id'),
            LocationMaster.device_id.alias('source_device_id'),
            LocationMaster.container_id.alias('source_drawer_id'),
            DeviceMasterAlias.device_type_id.alias('source_device_type_id'),
            LocationMasterAlias.device_id.alias('trolley_id'),
            LocationMasterAlias.container_id.alias('trolley_drawer_id'),
        ) \
            .join(CanisterTxMeta, on=((CanisterTxMeta.id == CanisterTransfers.to_ct_meta_id) |
                                      (CanisterTxMeta.id == CanisterTransfers.from_ct_meta_id))) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTransfers.dest_device_id) \
            .join(BatchMaster, on=BatchMaster.id == CanisterTransfers.batch_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMasterAlias, JOIN_LEFT_OUTER, on=DeviceMasterAlias.id == LocationMaster.device_id) \
            .join(LocationMasterAlias, on=CanisterTransfers.trolley_loc_id == LocationMasterAlias.id) \
            .where(CanisterTransfers.canister_id == canister_id,
                   CanisterTransfers.trolley_loc_id.is_null(False),
                   CanisterTransfers.transfer_status.not_in(constants.canister_tx_existing_status_list),
                   CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_CSR_DONE) \
            .order_by(CanisterTransfers.id.desc())

        logger.info("canister transfer to trolley query: " + str(query))
        logger.info("canister_transfer_info: " + str(query.dicts().get()))

        return query.dicts().get()
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_latest_canister_transfer_data_for_a_canister_from_robot_csr {}".format(e))
        raise
    except DoesNotExist:
        return {}


@log_args_and_response
def db_get_latest_canister_transfer_data_to_robot_from_trolley(canister_id):
    """
        @return canister transfer data of given canister from trolley to dest device
    """
    try:
        LocationMasterAlias = LocationMaster.alias()
        # sub_query = CanisterTransfers.select(fn.MAX(CanisterTransfers.id).alias('latest_canister_transfer_id')) \
        #     .where(CanisterTransfers.canister_id == canister_id,
        #            CanisterTransfers.trolley_loc_id.is_null(False)) \
        #     .alias('sub_query')
        # logger.info("sub: " + str(sub_query.dicts().get()))

        query = CanisterTransfers.select(CanisterTransfers.canister_id,
                                         CanisterTransfers.trolley_loc_id,
                                         LocationMaster.device_id.alias('trolley_id'),
                                         LocationMaster.container_id.alias('trolley_drawer_id'),
                                         CanisterTransfers.dest_device_id,
                                         CanisterTransfers.id.alias('transfer_id'),
                                         CanisterTransfers.transfer_status,
                                         DeviceMaster.system_id.alias('dest_system_id'),
                                         CanisterTransfers.dest_quadrant,
                                         CanisterTxMeta.status_id,
                                         LocationMasterAlias.device_id.alias('updated_dest_device_id'),
                                         LocationMasterAlias.quadrant.alias('updated_dest_quadrant'),
                                         CanisterMaster.canister_type,
                                         ContainerMaster.drawer_type,
                                         CanisterTxMeta.batch_id
                                         ) \
            .join(LocationMaster, on=CanisterTransfers.trolley_loc_id == LocationMaster.id) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTransfers.dest_device_id) \
            .join(CanisterTxMeta, on=CanisterTxMeta.id == CanisterTransfers.from_ct_meta_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMasterAlias, on=LocationMasterAlias.id == CanisterMaster.location_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMasterAlias.container_id) \
            .where(CanisterTransfers.canister_id == canister_id,
                   CanisterTransfers.transfer_status.not_in(constants.canister_tx_existing_status_list),
                   CanisterTransfers.trolley_loc_id.is_null(False),
                   CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_ROBOT_DONE) \
            .order_by(CanisterTransfers.id.desc())

        logger.info("canister transfer to trolley query: " + str(query))
        logger.info("canister_transfer_info: " + str(query.dicts().get()))

        return query.dicts().get()
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_latest_canister_transfer_data_to_robot_from_trolley {}".format(e))
        raise
    except DoesNotExist:
        return {}
    except Exception as e:
        logger.error("error in db_get_latest_canister_transfer_data_to_robot_from_trolley {}".format(e))
        return {}


@log_args_and_response
def db_get_latest_canister_transfer_data_to_csr_from_trolley(canister_id):
    """
        @return canister transfer data of given canister from trolley to dest device
    """
    try:
        LocationMasterAlias = LocationMaster.alias()
        LocationMasterAlias1 = LocationMaster.alias()

        # sub_query = CanisterTransfers.select(fn.MAX(CanisterTransfers.id).alias('latest_canister_transfer_id')) \
        #     .where(CanisterTransfers.canister_id == canister_id,
        #            CanisterTransfers.trolley_loc_id.is_null(False)) \
        #     .alias('sub_query')
        # logger.info("sub: " + str(sub_query.dicts().get()))

        query = CanisterTransfers.select(CanisterTransfers.canister_id,
                                         CanisterTransfers.trolley_loc_id,
                                         LocationMaster.device_id.alias('trolley_id'),
                                         LocationMaster.container_id.alias('trolley_drawer_id'),
                                         CanisterTransfers.dest_device_id,
                                         CanisterTransfers.dest_quadrant,
                                         CanisterTransfers.id.alias('transfer_id'),
                                         CanisterTransfers.transfer_status,
                                         CanisterTransfers.batch_id,
                                         CanisterTxMeta.status_id,
                                         DeviceMaster.system_id.alias('dest_system_id'),
                                         LocationMasterAlias.device_id.alias('updated_dest_device_id'),
                                         LocationMasterAlias.container_id.alias('updated_dest_container_id'),
                                         LocationMasterAlias1.container_id.alias("recommended_container_id")
                                         ) \
            .join(LocationMaster, on=CanisterTransfers.trolley_loc_id == LocationMaster.id) \
            .join(CanisterTxMeta, on=CanisterTxMeta.id == CanisterTransfers.from_ct_meta_id) \
            .join(DeviceMaster, on=DeviceMaster.id == CanisterTransfers.dest_device_id) \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(LocationMasterAlias, JOIN_LEFT_OUTER, on=LocationMasterAlias.id == CanisterMaster.location_id) \
            .join(LocationMasterAlias1, JOIN_LEFT_OUTER, on=LocationMasterAlias1.location_number ==
                                                            CanisterTransfers.dest_location_number) \
            .where(CanisterTransfers.canister_id == canister_id,
                   CanisterTransfers.transfer_status.not_in(constants.canister_tx_existing_status_list),
                   CanisterTransfers.trolley_loc_id.is_null(False),
                   CanisterTxMeta.status_id != constants.CANISTER_TRANSFER_TO_CSR_DONE) \
            .order_by(CanisterTransfers.id.desc())

        logger.info("canister transfer to trolley query: " + str(query))
        logger.info("canister_transfer_info: " + str(query.dicts().get()))

        return query.dicts().get()
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_get_latest_canister_transfer_data_to_csr_from_trolley {}".format(e))
        raise
    except DoesNotExist:
        return {}
    except Exception as e:
        logger.error("error in db_get_latest_canister_transfer_data_to_csr_from_trolley {}".format(e))
        return {}


@log_args_and_response
def db_update_canister_tx_status_dao(batch_id: int, canister_id_list: list, status: int) -> bool:
    """
        Function to update transfer status in canister transfer
        @param batch_id:
        @param canister_id_list:
        @param status:
        @return:
    """
    try:
        return CanisterTransfers.db_update_canister_tx_status(batch_id=batch_id,
                                                                  canister_id_list=canister_id_list,
                                                                  status=status)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_update_canister_tx_status_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_update_canister_tx_status_dao {}".format(e))
        raise e


@log_args_and_response
def update_canister_transfers(update_dict: dict, canister_id_list: list, batch_id: int) -> bool:
    """
        Function to update transfer
        @param update_dict:
        @param canister_id_list:
        @param batch_id:
        @return:
    """
    try:

        return CanisterTransfers.db_update_canister_transfers(update_dict=update_dict,
                                                              canister_id_list=canister_id_list,
                                                              batch_id=batch_id)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in update_canister_tx {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in update_canister_tx {}".format(e))
        raise e


@log_args_and_response
def get_total_canister_transfer_data_dao(batch_id, cycle_id, skip_canister):
    """
    to get total canister and skip canister from canister_transfer if  skip_canister = True => find skip canister for batch
    @param batch_id:
    @param skip_canister:
    @return:
    """
    try:
        total_canister_transfer_list: list = list()
        if skip_canister:
            query = CanisterTransfers.select(CanisterTransfers.canister_id, ) \
                .join(CanisterTxMeta, on=CanisterTransfers.to_ct_meta_id == CanisterTxMeta.id) \
                .where(CanisterTransfers.batch_id == batch_id,
                       CanisterTransfers.trolley_loc_id.is_null(False),
                       CanisterTransfers.transfer_status == constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                       CanisterTxMeta.cycle_id == cycle_id)
        else:
            query = CanisterTransfers.select(CanisterTransfers.canister_id,) \
                .join(CanisterTxMeta, on=CanisterTransfers.to_ct_meta_id == CanisterTxMeta.id) \
                .where(CanisterTransfers.batch_id == batch_id,
                       CanisterTransfers.trolley_loc_id.is_null(False),
                       CanisterTxMeta.cycle_id == cycle_id)

        for record in query.dicts():
            total_canister_transfer_list.append(record['canister_id'])
        return total_canister_transfer_list

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_total_canister_transfer_data_dao {}".format(e))
        raise e


@log_args_and_response
def update_canister_tx_meta_by_batch_id(update_dict: dict, batch_id: int,cycle_id = None) -> bool:
    """
        Function to update transfer
        @param update_dict:
        @param batch_id:
        @return:
    """
    try:
        if cycle_id:
            return CanisterTxMeta.db_update_canister_tx_meta_by_batch_id(update_dict=update_dict,
                                                                         batch_id=batch_id,
                                                                         cycle_id=cycle_id)

        return CanisterTxMeta.db_update_canister_tx_meta_by_batch_id(update_dict=update_dict,
                                                                     batch_id=batch_id)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in update_canister_tx_meta_by_batch_id {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in update_canister_tx_meta_by_batch_id {}".format(e))
        raise e


@log_args_and_response
def db_get_quad_drawer_type_wise_non_delicate_reserved_locations(company_id: int, batch_id: int, system_id: int):
    try:
        slow_movers_quad_drawer_empty_locations = dict()
        non_slow_movers_quad_drawer_empty_locations = dict()

        slow_movers = CanisterMaster.select(LocationMaster,
                                            CanisterMaster.id.alias('existing_canister_id'),
                                            CanisterMaster.canister_type,
                                            ContainerMaster.ip_address,
                                            ContainerMaster.id.alias('container_id'),
                                            ContainerMaster.secondary_ip_address,
                                            ContainerMaster.mac_address,
                                            ContainerMaster.secondary_mac_address,
                                            ContainerMaster.serial_number,
                                            ContainerMaster.drawer_type,
                                            ContainerMaster.drawer_level,
                                            DeviceMaster.name.alias("device_name"),
                                            DeviceMaster.device_type_id,
                                            ContainerMaster.drawer_name.alias('drawer_number'),
                                            UniqueDrug.drug_usage,
                                            UniqueDrug.is_delicate,
                                            CanisterTransfers.dest_quadrant,
                                            CanisterTransfers.dest_device_id).dicts() \
            .join(LocationMaster, on=((CanisterMaster.location_id == LocationMaster.id) &
                                      (CanisterMaster.company_id == company_id))) \
            .join(CanisterTransfers, on=CanisterMaster.id == CanisterTransfers.canister_id) \
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                  (UniqueDrug.txr == DrugMaster.txr))) \
            .where(DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT'],
                   ContainerMaster.drawer_type << [settings.SIZE_OR_TYPE['BIG'],
                                                   settings.SIZE_OR_TYPE['SMALL']],
                   ContainerMaster.drawer_level <= constants.MAX_DELICATE_DRAWER_LEVEL,
                   LocationMaster.is_disabled == settings.is_location_active,
                   CanisterTransfers.batch_id == batch_id,
                   UniqueDrug.is_delicate != constants.DELICATE_CANISTER) \
            .order_by(ContainerMaster.drawer_level, CanisterMaster.id)
        for record in slow_movers:
            if record['dest_device_id'] == record['device_id'] and record['dest_quadrant'] == record['quadrant']:
                if record['drug_usage'] == constants.USAGE_SLOW_MOVING:
                    if record["device_id"] not in slow_movers_quad_drawer_empty_locations.keys():
                        slow_movers_quad_drawer_empty_locations[record["device_id"]] = dict()

                    if record["quadrant"] not in slow_movers_quad_drawer_empty_locations[record["device_id"]].keys():
                        slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]] = dict()
                    if record["drawer_type"] not in slow_movers_quad_drawer_empty_locations[record["device_id"]][
                        record["quadrant"]].keys():
                        slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]][
                            record["drawer_type"]] = list()
                    slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]][
                        record["drawer_type"]].append(record)
                else:
                    if record["device_id"] not in non_slow_movers_quad_drawer_empty_locations.keys():
                        non_slow_movers_quad_drawer_empty_locations[record["device_id"]] = dict()

                    if record["quadrant"] not in non_slow_movers_quad_drawer_empty_locations[
                        record["device_id"]].keys():
                        non_slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]] = dict()
                    if record["drawer_type"] not in non_slow_movers_quad_drawer_empty_locations[record["device_id"]][
                        record["quadrant"]].keys():
                        non_slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]][
                            record["drawer_type"]] = list()
                    non_slow_movers_quad_drawer_empty_locations[record["device_id"]][record["quadrant"]][
                        record["drawer_type"]].append(record)
        return slow_movers_quad_drawer_empty_locations, non_slow_movers_quad_drawer_empty_locations
    except Exception as e:
        return e

@log_args_and_response
def sorted_csr_canister_list_by_big_canisters(csr_canister_list):
    try:
        query = CanisterMaster.select(CanisterMaster.id)\
            .where(CanisterMaster.id << csr_canister_list,
                   )\
            .order_by(CanisterMaster.canister_type)
        csr_canister_list = [item['id'] for item in query.dicts()]
        return csr_canister_list
    except Exception as e:
        logger.error("sorted_csr_canister_list_by_big_canisters {}".format(e))
        return e


@log_args_and_response
def get_location_status_for_delicate(record,):

    try:
        empty_locations, drawer_data = db_get_drawer_wise_empty_locations(record['dest_device_id'],
                                                                          record["dest_quadrant"])
        first_empty_key = ''
        first_empty_loc = None
        if constants.SMALL_CANISTER_CODE in empty_locations.keys():
            small_canisters = empty_locations[constants.SMALL_CANISTER_CODE]
            keys_to_remove = [key for key, value in small_canisters.items() if len(value) == 0]
            for key in keys_to_remove:
                del small_canisters[key]
            small_canisters_drawer = sorted(small_canisters.keys())
            for key in small_canisters_drawer:
                first_empty_key = key[0]
                first_empty_loc = small_canisters[key][0]
                break
        drawer_level = constants.ROBOT_DRAWER_LEVELS[first_empty_key]
        if drawer_level < 5 and record["current_drawer_level"] > 4 and first_empty_loc:
            record["wrong_location"] = True
            record["empty_location"] = first_empty_loc

        return record
    except Exception as e:
        logger.error("error in get_location_status_for_delicate {}".format(e))
        return e


@log_args_and_response
def get_delicate_drawers(device_id, quadrant, canister_type_dict):

    drawer_to_unlock = dict()
    delicate_drawers_to_unlock = dict()
    delicate_drawers = ['A','B','C']
    try:
        logger.info(
            "Input get_empty_locations_for_canister {}, {}, {}".format(device_id, quadrant, canister_type_dict))
        big_canister_count = canister_type_dict["big_canister_count"]
        small_canister_count = canister_type_dict["small_canister_count"]
        delicate_canister_count = canister_type_dict["delicate_canister_count"]
        logger.info("get_empty_locations_for_canister {}, {}, {}".format(device_id, quadrant, big_canister_count,
                                                                         small_canister_count))
        temp_big_canister = big_canister_count
        temp_small_canister = small_canister_count
        temp_delicate_canister_count = delicate_canister_count
        if not device_id or not quadrant:
            logger.error("Device id or quad is null")
            return drawer_to_unlock, delicate_drawers_to_unlock

        if big_canister_count == 0 and small_canister_count == 0 and delicate_canister_count == 0:
            logger.error("No canisters to be transferred")
            return drawer_to_unlock, delicate_drawers_to_unlock

        empty_locations_drawer_wise, drawer_data = db_get_drawer_wise_empty_locations(
            device_id=device_id, quadrant=[quadrant])
        temp_empty_locations_drawer_wise = dict()

        for drawer_type, container_data in empty_locations_drawer_wise.items():
            if drawer_type == settings.SIZE_OR_TYPE['BIG'] and big_canister_count > 0:
                for container, display_locations in container_data.items():
                    if temp_big_canister <= 0:
                        break
                    if not len(display_locations):
                        continue
                    location_count = len(display_locations)
                    drawer_data[container]["to_device"] = display_locations[:temp_big_canister]
                    empty_locations_drawer_wise[drawer_type][container] = display_locations[temp_big_canister:]
                    temp_big_canister -= location_count
                    drawer_data[container]["from_device"] = list()
                    drawer_to_unlock[container] = drawer_data[container]
            elif small_canister_count > 0 or delicate_canister_count > 0:
                for container, display_locations in container_data.items():
                    delicate_over = 0
                    for item in delicate_drawers:
                        if len(display_locations) and item in display_locations[0] and temp_delicate_canister_count <= 0:
                            if drawer_type not in temp_empty_locations_drawer_wise.keys():
                                temp_empty_locations_drawer_wise[drawer_type] = dict()
                            temp_empty_locations_drawer_wise[drawer_type][container]=list()
                            temp_empty_locations_drawer_wise[drawer_type][container].append(display_locations)
                            delicate_over = 1
                            break
                    if delicate_over:
                        continue
                    if temp_delicate_canister_count > 0:
                        if temp_delicate_canister_count <= 0:
                            break
                        if not len(display_locations):
                            continue
                        location_count = len(display_locations)
                        drawer_data[container]["to_device"] = display_locations[:temp_delicate_canister_count]
                        temp_delicate_canister_count -= location_count
                        drawer_data[container]["from_device"] = list()
                        delicate_drawers_to_unlock[container] = drawer_data[container]
                    else:
                        if temp_small_canister <= 0:
                            break
                        if not len(display_locations):
                            # if drawer_type not in temp_empty_locations_drawer_wise.keys():
                            #     temp_empty_locations_drawer_wise[drawer_type] = dict()
                            # temp_empty_locations_drawer_wise[drawer_type][container] = list()
                            # temp_empty_locations_drawer_wise[drawer_type][container].append(display_locations)
                            continue

                        location_count = len(display_locations)
                        drawer_data[container]["to_device"] = display_locations[:temp_small_canister]
                        if drawer_type == settings.SIZE_OR_TYPE['BIG']:
                            empty_locations_drawer_wise[drawer_type][container] = display_locations[temp_small_canister:]
                        temp_small_canister -= location_count
                        drawer_data[container]["from_device"] = list()
                        drawer_to_unlock[container] = drawer_data[container]
        if temp_small_canister:
            for drawer_type, container_data in empty_locations_drawer_wise.items():
                if drawer_type == settings.SIZE_OR_TYPE['BIG']:
                    for container, display_locations in container_data.items():
                        if temp_small_canister <= 0:
                            break
                        if not len(display_locations):
                            continue
                        location_count = len(display_locations)
                        if "to_device" in drawer_data[container]:
                            drawer_data[container]["to_device"].extend(display_locations[:temp_small_canister])
                        else:
                            drawer_data[container]["to_device"] = display_locations[:temp_small_canister]
                        temp_small_canister -= location_count
                        drawer_data[container]["from_device"] = list()
                        drawer_to_unlock[container] = drawer_data[container]
        if temp_small_canister:
            temp_empty_locations_drawer_wise = OrderedDict(sorted(temp_empty_locations_drawer_wise.items()))
            for drawer_type, container_data in temp_empty_locations_drawer_wise.items():
                for container, display_locations in container_data.items():
                    if temp_small_canister <= 0:
                        break
                    if not len(display_locations):
                        continue
                    location_count = len(display_locations)
                    drawer_data[container]["to_device"] = display_locations[:temp_small_canister]
                    temp_small_canister -= location_count
                    drawer_data[container]["from_device"] = list()
                    drawer_to_unlock[container] = drawer_data[container]

        return drawer_to_unlock, delicate_drawers_to_unlock

    except Exception as e:
        logger.error("error in update_canister_tx_meta_by_batch_id {}".format(e))
        return e


def get_slow_movers_for_device(device_id: int, quadrant):
    try:
        slow_movers = {}
        canister_id = None
        query = CanisterTransfers.select(CanisterMaster.id,
                                         ContainerMaster.drawer_name,
                                         ContainerMaster.drawer_level,
                                         UniqueDrug.drug_usage,
                                         LocationMaster.display_location,
                                         LocationMaster.id.alias('location_id'),
                                         UniqueDrug.is_delicate
                                         )\
            .join(CanisterMaster, on=CanisterTransfers.canister_id == CanisterMaster.id)\
            .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id)\
            .join(ContainerMaster, on=LocationMaster.container_id == ContainerMaster.id)\
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                   (UniqueDrug.txr == DrugMaster.txr)))\
            .where(LocationMaster.device_id == device_id,
                   LocationMaster.quadrant == quadrant,
                   ContainerMaster.drawer_level <= 4,
                   CanisterMaster.active == 1,
                   UniqueDrug.is_delicate != 1)\
            .order_by(UniqueDrug.drug_usage.desc())
        for record in query.dicts():
            if record['id'] not in slow_movers.keys():
                canister_id = record['id']
                slow_movers[record['id']] = (record['display_location'], record['location_id'])
                break

        return slow_movers, canister_id

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in update_canister_tx_meta_by_batch_id {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in update_canister_tx_meta_by_batch_id {}".format(e))
        raise e


@log_args_and_response
def get_csr_tx_status(tx_id):
    try:
        query = CanisterTxMeta.select(CanisterTxMeta.status_id).where(CanisterTxMeta.id == tx_id)

        for record in query.dicts():
            return record['status_id']

    except Exception as e:
        logger.error("get_csr_tx_status {}".format(e))
        return e


@log_args_and_response
def db_update_canister_tx_meta_status_dao(tx_meta_id):
    try:
        status = CanisterTxMeta.update(status_id=constants.CANISTER_TRANSFER_TO_ROBOT_DONE).where(
             CanisterTxMeta.id == tx_meta_id).execute()
        return status

    except (InternalError, IntegrityError) as e:
        logger.error("Error in db_update_canister_tx_meta_status_dao {}".format(e))
        raise

def get_csr_canister_tx_meta_id(canister_id: int,batch_id: int):
    try:
        cycle_status_dict = dict()
        robot_tx_meta_id = None
        cycle_id = 0
        robot_tx_query = CanisterTransfers.select(CanisterTransfers.from_ct_meta_id.alias("canister_tx_meta"),
                                                  CanisterTxMeta.cycle_id,
                                                  CanisterTxMeta.status_id)\
            .join(CanisterTxMeta, on=CanisterTxMeta.id == CanisterTransfers.from_ct_meta_id)\
            .where(CanisterTransfers.dest_device_id in [2, 3],
                   CanisterTransfers.canister_id == canister_id,
                   CanisterTransfers.batch_id == batch_id)
        for record in robot_tx_query.dicts():
            cycle_id = record['cycle_id']
        csr_tx_query = CanisterTxMeta.select(CanisterTxMeta.id, CanisterTxMeta.status_id).where(
            CanisterTxMeta.batch_id == batch_id,
            CanisterTxMeta.cycle_id == cycle_id,
            CanisterTxMeta.device_id == 1)

        for record in csr_tx_query.dicts():
            # cycle id in cycle id dict
            if cycle_id not in cycle_status_dict:
                cycle_status_dict[cycle_id] = (record['id'], record['status_id'])
        return cycle_status_dict

    except (InternalError, IntegrityError) as e:
        logger.error("Error in get_csr_canister_tx_meta_id {}".format(e))
        raise e


@log_args_and_response
def get_canister_replenish_transfer_data_dao(canister_id, batch_id, company_id):
    try:
        transfer_data = {}
        affected_packs = []
        query = ((PackAnalysis.select(PackAnalysisDetails.device_id,
                                      PackAnalysisDetails.quadrant,
                                      DeviceMaster.name.alias('device_name'),
                                      DeviceMaster.device_type_id,
                                      DeviceMaster.serial_number.alias("device_serial_number"),
                                      PackAnalysis.pack_id,
                                      DrugMaster.id.alias('drug_id'))
                  .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)
                  .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id)
                  .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id)
                  .join(DeviceMaster, on=DeviceMaster.id == PackAnalysisDetails.device_id)
                  .where(PackAnalysis.batch_id == batch_id,
                         PackAnalysisDetails.canister_id == canister_id))
                 .group_by(PackAnalysis.pack_id))
        drug_id = None
        for record in query.dicts():
            affected_packs.append(record['pack_id'])
            drug_id = record['drug_id']
            transfer_data['device_id'] = record['device_id']
            transfer_data['device_name'] = record['device_name']
            transfer_data['quadrant'] = record['quadrant']
        required_quantity = (PackDetails.select(fn.SUM(SlotDetails.quantity))
                             .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id)
                             .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id).where(
            SlotDetails.drug_id == drug_id,
            PackDetails.id << affected_packs).group_by(SlotDetails.drug_id)).scalar()

        transfer_data['req_qty'] = required_quantity
        return transfer_data

    except Exception as e:
        logger.error(f"error in get_canister_replenish_transfer_data_dao : {e}")
        return e
