import functools
import operator
import time
from collections import defaultdict
from functools import reduce
from typing import List, Any, Tuple

import couchdb
from peewee import InternalError, IntegrityError, DoesNotExist, DataError, JOIN_LEFT_OUTER, fn, SQL

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import log_args_and_response, log_args, get_current_date_time, retry
from src.dao.canister_dao import get_canister_expiry_status
from src.dao.couch_db_dao import initialize_couch_db_doc, get_couch_db_database_name
from src.dao.location_dao import db_get_empty_locations_dao
from src.dao.pack_dao import get_location_id_from_display_location
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_canister_master import CanisterMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_drug_details import DrugDetails
from src.model.model_old_canister_mapping import OldCanisterMapping
from src.model.model_product_details import ProductDetails
from src.model.model_slot_details import SlotDetails
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_dimension import DrugDimension
from src import constants
from src.model.model_canister_testing_status import CanisterTestingStatus
from src.model.model_container_master import ContainerMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_details import PackDetails
from src.model.model_patient_rx import PatientRx
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_batch_master import BatchMaster
from src.service.notifications import Notifications

logger = settings.logger


@log_args_and_response
def get_alternate_canister_data(canister_stick_id: int, zone_id_list: List[int], fndc_txr: str,
                                company_id: int, current_canister_id: int) -> tuple:
    """
    This gets data of all the alternate canisters.
    @param fndc_txr:
    @param current_canister_id:
    @param canister_stick_id:
    @param zone_id_list:
    @param company_id:
    @return:
    """

    untested_canister_data: List[dict] = list()
    drawers_to_unlock: dict = dict()
    order_list: list = list()

    order_list.append(SQL('FIELD(testing_status, {},{},{})'
                          .format(constants.CANISTER_TESTING_PASS,
                                  constants.CANISTER_TESTING_PENDING,
                                  constants.CANISTER_TESTING_FAIL)))

    try:
        query = CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
                                      CanisterMaster.location_id,
                                      LocationMaster.display_location,
                                      ContainerMaster.id.alias("container_id"),
                                      ContainerMaster.drawer_name,
                                      ContainerMaster.serial_number,
                                      ContainerMaster.ip_address,
                                      ContainerMaster.secondary_ip_address,
                                      ContainerMaster.shelf,
                                      DeviceMaster.name.alias("device_name"),
                                      DeviceMaster.device_type_id,
                                      DeviceMaster.id.alias("device_id"),
                                      DeviceMaster.system_id,
                                      DrugMaster.concated_drug_name_field().alias("drug_name"),
                                      DrugMaster.ndc,
                                      DrugMaster.formatted_ndc,
                                      DrugMaster.image_name,
                                      DrugMaster.shape,
                                      DrugMaster.color,
                                      DrugMaster.imprint,
                                      fn.IF(CanisterTestingStatus.status_id.is_null(True),
                                            constants.CANISTER_TESTING_PENDING,
                                            CanisterTestingStatus.status_id).alias('testing_status'),
                                      fn.IF(DrugStockHistory.is_in_stock.is_null(True), 'null',
                                            DrugStockHistory.is_in_stock).alias('is_in_stock'),
                                      fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                            DrugDetails.last_seen_by).alias('last_seen_by'),
                                      ).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(CanisterZoneMapping, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(UniqueDrug, on=(UniqueDrug.concated_fndc_txr_field() == DrugMaster.concated_fndc_txr_field())) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CanisterTestingStatus, JOIN_LEFT_OUTER, on=CanisterTestingStatus.canister_id == CanisterMaster.id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                         (DrugStockHistory.is_active == True) &
                                                         (DrugStockHistory.company_id == CanisterMaster.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == CanisterMaster.company_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .where((CanisterMaster.company_id == company_id), (CanisterZoneMapping.zone_id << zone_id_list),
                   (CanisterMaster.canister_stick_id == canister_stick_id),
                   (DrugMaster.concated_fndc_txr_field() == fndc_txr),
                   (CanisterMaster.id != current_canister_id)) \
            .order_by(order_list)

        for record in query:
            untested_canister_data.append(record)

            if record["drawer_name"]:
                if record["drawer_name"] not in drawers_to_unlock.keys():
                    drawers_to_unlock[record["drawer_name"]] = {"id": record["container_id"],
                                                                "drawer_name": record["drawer_name"],
                                                                "serial_number": record["serial_number"],
                                                                "device_ip_address": record["ip_address"],
                                                                "ip_address": record["ip_address"],
                                                                "secondary_ip_address": record["secondary_ip_address"],
                                                                "from_device": list(),
                                                                "to_device": list(),
                                                                "shelf": record["shelf"],
                                                                "device_type_id": record["device_type_id"],
                                                                "device_id": record["device_id"]
                                                                }

                drawers_to_unlock[record["drawer_name"]]["from_device"].append(record["display_location"])

        return untested_canister_data, drawers_to_unlock
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_alternate_canister_data {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_alternate_canister_data {}".format(e))
        raise e


@log_args_and_response
def validate_canister_id_with_company_id(canister_id: int, company_id: int) -> bool:
    """
    This function validates canister id against company_id
    @param canister_id:
    @param company_id:
    @return:
    """
    try:
        return CanisterMaster.db_verify_canister_id(canister_id=canister_id, company_id=company_id)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in validate_canister_id_with_company_id {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in validate_canister_id_with_company_id {}".format(e))
        raise e


@log_args_and_response
def validate_active_canister_id(canister_id: int) -> bool:
    """
    This function validates canister id against company_id
    @param canister_id:
    @return:
    """
    try:
        return CanisterMaster.db_verify_active_canister_id(canister_id=canister_id)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in validate_active_canister_id {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in validate_active_canister_id {}".format(e))
        raise e


# @log_args_and_response
# def validate_ndc_by_canister_id(ndc: str, canister_id: int) -> bool:
#     """
#     Validate whether the
#     @param ndc:
#     @param canister_id:
#     @return:
#     """
#     logger.debug("Inside validate_ndc_by_canister_id")
#
#     try:
#         query = CanisterMaster.select(CanisterMaster.id).dicts() \
#             .join(UniqueDrug, on=UniqueDrug.drug_id == CanisterMaster.drug_id) \
#             .join(DrugMaster,
#                   on=(DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) & (DrugMaster.txr == UniqueDrug.txr)) \
#             .where((CanisterMaster.id == canister_id) & (DrugMaster.ndc == ndc))
#
#         if query.count() > 0:
#             return True
#         return False
#     except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
#         logger.error(e)
#         raise


@log_args_and_response
def get_canister_testing_status_by_drug(canister_ids: List[int], drug_ids: List[int]) -> Any:
    """
    This function used to get canister testing data by drug
    @param drug_ids:
    @param canister_ids:
    @return:
    """

    try:
        canister_testing_details = dict()
        query = CanisterTestingStatus.select().dicts() \
            .where((CanisterTestingStatus.drug_id << drug_ids), (CanisterTestingStatus.canister_id << canister_ids))

        for record in query:
            canister_testing_details[record["canister_id"]] = record

        return canister_testing_details

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_canister_testing_status_by_drug {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_testing_status_by_drug {}".format(e))
        raise e


@log_args_and_response
def get_alternate_canisters_by_drug_and_canister_stick(canister_stick_id: int, fndc_txr: str,
                                                       zone_id_list: List[int]) -> List[int]:
    """
    This functions gets the list of alternate canister_ids in the same zone and as same fndc_txr as given drug
    and as same canister_stick_id as given canister's canister_stick_id.
    @param canister_stick_id:
    @param fndc_txr:
    @param zone_id_list:
    @return:
    """

    alternate_canister_list: List[int] = list()

    # record = CanisterMaster.get(CanisterMaster.id==canister_id)
    # canister_stick_id = record.canister_stick_id

    try:
        query = CanisterMaster.select(CanisterMaster.id.alias("canister_id")).dicts() \
            .join(CanisterZoneMapping, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .where((CanisterZoneMapping.zone_id.in_(zone_id_list)),
                   (CanisterMaster.canister_stick_id == canister_stick_id),
                   (DrugMaster.concated_fndc_txr_field() == fndc_txr))

        for record in query:
            alternate_canister_list.append(record["canister_id"])

        return alternate_canister_list

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_alternate_canisters_by_drug_and_canister_stick {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_alternate_canisters_by_drug_and_canister_stick {}".format(e))
        raise e


@log_args_and_response
def get_canister_testing_status_by_canister_stick(fndc_txr: str, zone_id_list: List[int]) -> Tuple:
    """
    This functions gets the list of all canister_ids in the same zone and as same fndc_txr as given drug.
    @param fndc_txr:
    @param zone_id_list:
    @return:
    """

    total_sticks, tested_sticks = [], []
    try:
        CanisterMasterAlias = CanisterMaster.alias()
        DrugMasterAlias = DrugMaster.alias()

        query = CanisterMaster.select(fn.GROUP_CONCAT(fn.DISTINCT(CanisterMaster.canister_stick_id))
                                      .coerce(False).alias('total_canister_sticks'),
                                      fn.GROUP_CONCAT(fn.DISTINCT(CanisterMasterAlias.canister_stick_id))
                                      .coerce(False).alias('tested_canister_sticks')).dicts() \
            .join(CanisterZoneMapping, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(CanisterTestingStatus, JOIN_LEFT_OUTER, on=CanisterTestingStatus.drug_id == DrugMaster.id) \
            .join(CanisterMasterAlias, JOIN_LEFT_OUTER, on=CanisterTestingStatus.canister_id ==
                                                           CanisterMasterAlias.id) \
            .join(DrugMasterAlias, JOIN_LEFT_OUTER, on=DrugMasterAlias.id == CanisterMasterAlias.drug_id) \
            .where((CanisterZoneMapping.zone_id << zone_id_list), (DrugMaster.concated_fndc_txr_field() == fndc_txr),
                   (fn.CONCAT(fn.IFNULL(DrugMasterAlias.formatted_ndc, ''), '#',
                              fn.IFNULL(DrugMasterAlias.txr, '')) == fndc_txr))

        for record in query:
            if record["total_canister_sticks"]:
                total_sticks = list(record["total_canister_sticks"].split(","))
            if record["tested_canister_sticks"]:
                tested_sticks = list(record["tested_canister_sticks"].split(","))

            return total_sticks, tested_sticks

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_canister_testing_status_by_canister_stick {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_testing_status_by_canister_stick {}".format(e))
        raise e


@log_args_and_response
def insert_canister_testing_status_data(data_dict_list: List[dict]) -> bool:
    """
    Insert multiple records to the Canister Testing Status table.
    @param data_dict_list:
    @return:
    """
    try:
        return CanisterTestingStatus.insert_canister_testing_status_data(data_dict_list=data_dict_list)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in insert_canister_testing_status_data {}".format(e))
        raise e


@log_args_and_response
def update_canister_testing_status_data(create_dict: dict, update_dict: dict) -> bool:
    """
    Update and create record if not exist.
    @param create_dict:
    @param update_dict:
    @return:
    """
    try:
        return CanisterTestingStatus.db_update_or_create(create_dict=create_dict, update_dict=update_dict)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in update_canister_testing_status_data {}".format(e))
        raise e


@log_args
def get_canister_testing_details(clauses, order_list, zone_id_list: List[int], company_id: int) -> List[dict]:
    """
    This gets data of all the canisters with testing details.
    @param clauses:
    @param zone_id_list:
    @param company_id:
    @return:
    """
    canister_testing_data: List[dict] = list()
    try:
        DrugMasterAlias = DrugMaster.alias()
        clause = [(CanisterMaster.company_id == company_id), (CanisterZoneMapping.zone_id.in_(zone_id_list)),
                  ((DrugMasterAlias.id.is_null(True)) |
                   (fn.CONCAT(fn.IFNULL(DrugMasterAlias.formatted_ndc, ''), '#',
                              fn.IFNULL(DrugMasterAlias.txr, '')) == DrugMaster.concated_fndc_txr_field())),
                  ((CanisterTestingStatus.tested == 1) | (CanisterTestingStatus.status_id.is_null(True) | (
                          CanisterTestingStatus.status_id == constants.CANISTER_TESTING_PENDING)))]
        clauses += clause

        query = CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
                                      CanisterMaster.location_id,
                                      LocationMaster.display_location,
                                      ContainerMaster.id.alias("container_id"),
                                      ContainerMaster.drawer_name,
                                      ContainerMaster.ip_address,
                                      ContainerMaster.secondary_ip_address,
                                      ContainerMaster.shelf,
                                      ContainerMaster.serial_number,
                                      DeviceMaster.serial_number.alias("device_type_name"),
                                      DeviceMaster.name.alias("device_name"),
                                      DeviceMaster.device_type_id,
                                      DrugMaster.concated_drug_name_field().alias("drug_name"),
                                      DrugMaster.ndc,
                                      DrugMaster.formatted_ndc,
                                      DrugMaster.image_name,
                                      DrugMaster.shape,
                                      DrugMaster.color,
                                      DrugMaster.imprint,
                                      fn.IF(DrugStockHistory.is_in_stock.is_null(True), 'null',
                                            DrugStockHistory.is_in_stock).alias('is_in_stock'),
                                      fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                            DrugDetails.last_seen_by).alias('last_seen_by'),
                                      fn.IF(CanisterTestingStatus.status_id.is_null(True),
                                            constants.CANISTER_TESTING_PENDING,
                                            CanisterTestingStatus.status_id).alias('status_id'),
                                      DrugMasterAlias.id.alias('tested_drug_id'),
                                      fn.CONCAT(DrugMasterAlias.drug_name, ' ', DrugMasterAlias.strength_value, ' ',
                                                DrugMasterAlias.strength).alias("tested_drug_name"),
                                      DrugMasterAlias.ndc.alias("tested_ndc"),
                                      CanisterTestingStatus.reason,
                                      CanisterTestingStatus.modified_by.alias("tested_by"),
                                      CanisterTestingStatus.modified_date.alias("tested_at")).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(CanisterTestingStatus, JOIN_LEFT_OUTER, on=(CanisterTestingStatus.canister_id == CanisterMaster.id)) \
            .join(DrugMasterAlias, JOIN_LEFT_OUTER, on=DrugMasterAlias.id == CanisterTestingStatus.drug_id) \
            .join(CanisterZoneMapping, on=CanisterZoneMapping.canister_id == CanisterMaster.id) \
            .join(UniqueDrug,
                  on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                         (DrugStockHistory.is_active == True) &
                                                         (DrugStockHistory.company_id == CanisterMaster.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == CanisterMaster.company_id))) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=LocationMaster.container_id == ContainerMaster.id) \
            .group_by(DrugMaster.concated_fndc_txr_field(), CanisterMaster.canister_stick_id,
                      fn.IF(CanisterTestingStatus.status_id.is_null(True), constants.CANISTER_TESTING_PENDING,
                            CanisterTestingStatus.status_id)) \
            .order_by(LocationMaster.id) \
            .where(functools.reduce(operator.and_, clauses))
        if order_list:
            query = query.order_by(*order_list)

        for record in query:
            if record["device_type_name"]:
                record["device_type_name"] = record["device_type_name"][0:3]
            canister_testing_data.append(record)
        return canister_testing_data
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_canister_testing_details {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_testing_details {}".format(e))
        raise e


@log_args_and_response
def get_location_id_from_display_location_dao(device_id: int, display_location: str) -> tuple:
    """
    This function to get location id from display location
    @param device_id:
    @param display_location:
    @return:
    """
    try:
        return get_location_id_from_display_location(device_id=device_id,
                                                     display_location=display_location)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_location_id_from_display_location_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_location_id_from_display_location_dao {}".format(e))
        raise e


@log_args_and_response
def get_canister_testing_count_dao():
    try:
        total_count = ProductDetails.select().count()
        to_be_highlighted = []
        lot_current_batch_count = defaultdict(int)
        query = (PatientRx.select(ProductDetails.product_id, ProductDetails.lot_number).dicts()
                 .join(PackRxLink, on=PackRxLink.patient_rx_id == PatientRx.id)
                 .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id)
                 .join(BatchMaster, on=BatchMaster.id == PackDetails.batch_id)
                 .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id)
                 .join(ProductDetails, on=ProductDetails.ndc == DrugMaster.ndc)
                 .where(ProductDetails.delivery_date.is_null(False),
                        BatchMaster.status.in_(settings.PACK_PRE_BATCH_STATUS), ProductDetails.is_skipped == False,
                        ProductDetails.status == settings.PRODUCT_TESTING_PENDING,
                        PackDetails.pack_status == settings.PENDING_PACK_STATUS)
                 # .where(BatchMaster.status.in_(settings.UPCOMING_BATCH_STATUS))
                 .distinct())
        query2 = ProductDetails.select(ProductDetails.lot_number).where(
            ProductDetails.delivery_date.is_null(False)).dicts()
        lot_numbers = {lot["lot_number"] for lot in query2}
        logger.info(f"in get_canister_testing_count_dao query is {query}")
        for record in query:
            to_be_highlighted.append(record['product_id'])
            lot_number = record['lot_number']
            lot_current_batch_count[lot_number] += 1
        current_batch_count = len(to_be_highlighted)
        return total_count, current_batch_count, to_be_highlighted, lot_current_batch_count, lot_numbers
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_canister_testing_count_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_canister_testing_count_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_testing_fields_dict():
    try:
        return {
            "product_id": ProductDetails.product_id,
            "lot_number": ProductDetails.lot_number,
            "drug_name": DrugMaster.drug_name,
            "status": ProductDetails.status
        }
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_get_testing_fields_dict {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_testing_fields_dict {}".format(e))
        raise e


@log_args_and_response
def db_get_alternate_fields_dict():
    try:
        return {
            "product_id": ProductDetails.product_id,
            "lot_number": ProductDetails.lot_number
        }
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_get_alternate_fields_dict {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_alternate_fields_dict {}".format(e))
        raise e


@log_args_and_response
def db_get_report_fields_dict():
    try:
        return {
            "canister_id": CanisterMaster.id,
            "ndc": DrugMaster.ndc,
            "drug_name": DrugMaster.drug_name,
            "status": CanisterTestingStatus.status_id,
            "tested_by": CanisterTestingStatus.modified_by
        }
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_get_fields_dict {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_fields_dict {}".format(e))
        raise e


@log_args_and_response
def db_get_products(clauses):
    """
    fetches all the canister data to show from product_details.
    @return:
    """
    try:
        clauses.append(ProductDetails.delivery_date.is_null(False))
        clauses.append(ProductDetails.status != settings.PRODUCT_STATUS_DONE)
        clauses.append(ProductDetails.status != settings.PRODUCT_STATUS_BROKEN)
        all_canisters = []
        query = (ProductDetails.select(ProductDetails, DrugMaster.drug_name, DrugMaster.image_name,
                                       DrugMaster.imprint, CustomDrugShape.name.alias("shape"), DrugMaster.color,
                                       LocationMaster.display_location, ContainerMaster.drawer_name,
                                       ContainerMaster.shelf, DeviceMaster.device_type_id,
                                       DeviceMaster.name.alias("device_name"), ContainerMaster.ip_address,
                                       ContainerMaster.secondary_ip_address,
                                       ContainerMaster.serial_number.alias("csr_serial_number"),
                                       DeviceMaster.serial_number.alias("device_type"),
                                       CanisterMaster.id.alias("new_canister_id")).dicts()
                 .join(DrugMaster, on=DrugMaster.ndc == ProductDetails.ndc)
                 .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                       fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                      (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc))
                 .join(DrugDimension, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDimension.unique_drug_id)
                 .join(CustomDrugShape, JOIN_LEFT_OUTER, on=CustomDrugShape.id == DrugDimension.shape)
                 .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == ProductDetails.transfer_location)
                 .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id)
                 .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id)
                 .join(CanisterMaster, JOIN_LEFT_OUTER,
                       on=CanisterMaster.product_id == ProductDetails.product_id)
                 .where(functools.reduce(operator.and_, clauses))
                 .distinct())
        logger.info(f"in db_get_products, query is {query}")
        for record in query:
            all_canisters.append(record)
        return list(all_canisters)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_get_products {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_products {}".format(e))
        raise e


@log_args_and_response
def db_get_product_ids():
    """
    fetches all the canister data to show from product_details.
    @return:
    """
    try:
        all_canisters = []
        query = (ProductDetails.select(ProductDetails.product_id).dicts()
                 .where(
            ProductDetails.status != settings.PRODUCT_STATUS_DONE and ProductDetails.status != settings.PRODUCT_STATUS_BROKEN
        )
                 .distinct())
        for record in query:
            all_canisters.append(record)
        return list(all_canisters)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_get_product_ids {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_product_ids {}".format(e))
        raise e


@log_args_and_response
def db_get_old_canister(product_id, company_id):
    """
    fetches all the old canister data to show from OldCanisterMapping table.
    @param company_id:
    @param product_id:
    @return:
    """
    try:
        query = (OldCanisterMapping.select(OldCanisterMapping.old_canister_id, LocationMaster.display_location,
                                           CanisterMaster.active.alias("is_active"),
                                           CanisterMaster.available_quantity, ContainerMaster.drawer_name,
                                           ContainerMaster.shelf, DeviceMaster.device_type_id,
                                           ContainerMaster.ip_address, ContainerMaster.secondary_ip_address,
                                           ContainerMaster.serial_number.alias("csr_serial_number"),
                                           CanisterMaster.drug_id, DeviceMaster.serial_number.alias("device_type_name"),
                                           CanisterMaster.expiry_date, CanisterTracker.expiration_date,
                                           DeviceMaster.name.alias("device_name"), DeviceMaster.id.alias("device_id")).dicts()
                 .join(CanisterMaster, JOIN_LEFT_OUTER, on=(CanisterMaster.id == OldCanisterMapping.old_canister_id))
                 .join(LocationMaster, JOIN_LEFT_OUTER, on=(LocationMaster.id == CanisterMaster.location_id))
                 .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id)
                 .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id)
                 .join(CanisterTracker, JOIN_LEFT_OUTER, on=CanisterTracker.canister_id == CanisterMaster.id)
                 .where(OldCanisterMapping.product_id == product_id)
                 .distinct())
        logger.info(f"in db_get_old_canister, query is {query}")
        old_canister_data = [{"old_canister_id": record["old_canister_id"],
                              "drug_id": record["drug_id"],
                              "display_location": record["display_location"],
                              "is_active": record["is_active"],
                              "expiry_date": record["expiry_date"],
                              "expiration_date": record["expiration_date"],
                              "expiry_status": get_canister_expiry_status(canister_id=record['old_canister_id'],
                                                                          company_id=company_id)[0],
                              "available_quantity": record["available_quantity"],
                              "drawer_number": record["drawer_name"],
                              "shelf": record["shelf"],
                              "device_type_id": record["device_type_id"],
                              "ip_address": record["ip_address"],
                              "secondary_ip_address": record["secondary_ip_address"],
                              "serial_number": record["csr_serial_number"],
                              "device_name": record["device_name"],
                              "device_id": record["device_id"],
                              "device_type_name": record["device_type_name"][0:3] if record.get(
                                  "device_type_name") else None
                              } for record in query]
        return old_canister_data
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_get_old_canister {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_get_old_canister {}".format(e))
        raise e


@log_args_and_response
def populate_product_details_dao(create_data: list) -> bool:
    """
    Update and create record if not exist.
    @param create_data:
    @return:
    """
    try:
        for record in create_data:
            status = ProductDetails.db_create_product_details(record)
        return status

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in populate_product_details_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in populate_product_details_dao {}".format(e))
        raise e


@log_args_and_response
def db_update_product_status(product_update_dict):
    """
    Update product status from pending --> transfer_pending or transfer_pending --> done
    @param product_update_dict:
    @return:
    """
    canister_serial_number = product_update_dict.get("canister_serial_number", None)
    location = product_update_dict.get("location", None)
    status = product_update_dict.get("status", None)
    product_id = product_update_dict.get("product_id", None)
    try:
        update_dict = {"status": status,
                       "modified_date": get_current_date_time()}
        logger.info(f"in db_update_product_status, update_dict is {update_dict}")
        if product_id:
            return ProductDetails.update(modified_date=get_current_date_time(), status=status, transfer_location=location).where(
                ProductDetails.product_id == product_id).execute()
        if canister_serial_number:
            return ProductDetails.update(modified_date=get_current_date_time(), status=status, transfer_location=location).where(
                ProductDetails.canister_serial_number == canister_serial_number).execute()
        return False
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_update_product_status {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_update_product_status {}".format(e))
        raise e


@log_args_and_response
def db_get_empty_location():
    """
    fetch the latest registered canister_id
    @return:
    """
    try:
        data = []
        no_select_locations = []
        subquery = LocationMaster.select(LocationMaster.id)\
            .join(CanisterMaster, on=CanisterMaster.location_id == LocationMaster.id)\
            .where(LocationMaster.device_id == '1')
        for i in subquery:
            no_select_locations.append(i)
        query = (ContainerMaster.select(fn.DISTINCT(ContainerMaster.drawer_name)).dicts()
                 .join(DeviceMaster, on=(DeviceMaster.id == ContainerMaster.device_id))
                 .join(LocationMaster, on=(LocationMaster.device_id == DeviceMaster.id))
                 .where(LocationMaster.device_id == 1)
                 .where(LocationMaster.id.not_in(subquery))
                 .order_by(ContainerMaster.drawer_name))
        for record in query:
            data.append(record)
        return data

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_get_canister_id {}".format(e))
        raise e


@log_args_and_response
def populate_old_canister_mapping_dao(create_data: list) -> bool:
    """
    Update and create record if not exist.
    @param create_data:
    @return:
    """
    try:
        status = OldCanisterMapping.db_create_product_mapping(create_data)
        return status

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in populate_old_canister_mapping_dao {}".format(e))
        raise e


@log_args_and_response
def db_check_and_update_product_status(product_id) -> bool:
    """
    checks whether location of canister is updated as required or not and update product status
    @param product_id:
    @return:
    """
    assigned_canister_id = None
    required_location = None
    try:
        query = ProductDetails.select(ContainerMaster.drawer_name, CanisterMaster.id.alias("new_canister_id")).dicts() \
            .join(CanisterMaster, on=CanisterMaster.product_id == ProductDetails.product_id)\
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id)\
            .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id)\
            .where(ProductDetails.product_id == product_id)
        logger.info(f"in db_check_and_update_product_status, query is {query}")
        for record in query:
            assigned_canister_id = record["new_canister_id"]
            required_location = record["drawer_name"]
        if assigned_canister_id:
            current_location = CanisterMaster.select(ContainerMaster.drawer_name) \
                .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .where(
                CanisterMaster.id == assigned_canister_id).scalar()
            if current_location and required_location:
                if required_location == current_location:
                    product_update_dict = {"product_id": product_id,
                                           "status": settings.PRODUCT_STATUS_DONE}
                    return db_update_product_status(product_update_dict)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_check_and_update_product_status {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in db_check_and_update_product_status {}".format(e))
        raise e


@log_args_and_response
def db_update_old_canister_mapping(new_canister_id, canister_serial_number) -> bool:
    """
    checks whether location of canister is updated as required or not and update product status
    @param canister_serial_number:
    @param new_canister_id:
    @return:
    """
    try:
        product_id = ProductDetails.select(ProductDetails.product_id).where(
            ProductDetails.canister_serial_number == canister_serial_number).scalar()
        OldCanisterMapping.update(new_canister_id=new_canister_id).where(
            OldCanisterMapping.product_id == product_id).execute()
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_check_and_update_product_status {}".format(e))
        raise e


@log_args_and_response
def db_validate_canister_and_product(canister_list, product_list):
    """
    checks whether received list of canisters and products are validate or not
    @param product_list:
    @param canister_list:
    @return:
    """
    canister_list = list(set(canister_list))
    product_list = list(set(product_list))
    try:
        count1 = ProductDetails.select(fn.COUNT('*')).where(ProductDetails.product_id.in_(product_list)).scalar()
        count2 = CanisterMaster.select(fn.COUNT('*')).where(CanisterMaster.id.in_(canister_list)).scalar()
        if count1 == len(product_list) and count2 == len(canister_list):
            return True
        else:
            return False
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in db_validate_canister_and_product {}".format(e))
        raise e


@log_args_and_response
def update_product_delivery_date(lot_number):
    """
    update product's delivery date after delivery
    @return:
    """
    try:
        return ProductDetails.db_update_product_delivery(lot_number)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in update_product_delivery_date {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in update_product_delivery_date {}".format(e))
        raise e


@log_args_and_response
def get_drug_list_from_lot_numbers(lot_number_list):
    try:
        query = (ProductDetails.select(DrugMaster.id.alias("drug_id"))
                 .join(DrugMaster, on=DrugMaster.ndc == ProductDetails.ndc).where(
            ProductDetails.lot_number << lot_number_list))

        return list(query.dicts())
    except Exception as e:
        logger.error(f"error occured in get_drug_list_from_lot_numbers {e}")
        return e

@log_args_and_response
def send_canister_testing_notification(company_id):
    """
    This functions send notification for canisters to test when delivered
    @param : company_id
    @return:
    """
    try:
        logger.debug("Inside send_canister_testing_notification.")
        count = get_canister_testing_count_dao()
        notification_message = f"New Canister lot has arrived.  Click on 'Start Testing' to test the Canister(s) \
        (Total no. of canisters: {count[0]})"
        status = Notifications(call_from_client=True, company_id=company_id).send(settings.ALL_USER_NOTIFICATION,
                                                                                  notification_message, flow='dp')
        return settings.SUCCESS_RESPONSE
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in send_canister_testing_notification {}".format(e))
    except Exception as e:
        logger.error("error in send_canister_testing_notification {}".format(e))


@log_args_and_response
def db_get_reserved_tested_location():
    """
    This functions send notification for canisters to test when delivered
    @param : company_id
    @return:
    """
    try:
        logger.debug("Inside db_get_reserved_tested_location.")
        reserved_locations = []
        query = ProductDetails.select(ProductDetails.transfer_location).dicts()
        for record in query:
            reserved_locations.append(record["transfer_location"])
        return reserved_locations
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_get_reserved_tested_location {}".format(e))
    except Exception as e:
        logger.error("error in db_get_reserved_tested_location {}".format(e))


@log_args_and_response
def db_get_product_details(rfid, company_id, system_id):
    """
    This functions gets the product details
    @param : rfid
    @return: {
        "total_canisters_to_test": 13,
        "current_batch_canisters_to_test": 5
    }
    """
    try:
        recommended_location = db_get_empty_locations_dao(company_id=company_id, is_mfd=False, device_id=1, quadrant=None,
                                                          device_type_id=None, system_id=system_id, drawer_number=constants.POST_TESTING_DRAWER_RECOMMENDATION)
        transfer_location = None
        reserved_locations = db_get_reserved_tested_location()
        reserved_locations = list(set(reserved_locations))
        for key in recommended_location:
            transfer_location = key if not reserved_locations or recommended_location[key][0][
                'id'] not in reserved_locations else transfer_location
            if transfer_location:
                break

        if transfer_location:
            query = (ProductDetails.select(ProductDetails, DrugMaster.drug_name, DrugMaster.image_name, DrugMaster.imprint,
                                           DrugMaster.color, CustomDrugShape.name.alias("shape"), DrugMaster.ndc,
                                           ContainerMaster.drawer_name, ContainerMaster.shelf,
                                           ContainerMaster.serial_number.alias("csr_serial_number"),
                                           DeviceMaster.device_type_id, ContainerMaster.ip_address,
                                           ContainerMaster.secondary_ip_address, LocationMaster.display_location,
                                           DeviceMaster.serial_number.alias("device_type"), DrugMaster.strength_value,
                                           DrugMaster.strength, DeviceMaster.name.alias("device_name")).dicts()
                     .join(DrugMaster, on=DrugMaster.ndc == ProductDetails.ndc)
                     .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                           fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                          (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc))
                     .join(DrugDimension, on=UniqueDrug.id == DrugDimension.unique_drug_id)
                     .join(CustomDrugShape, on=CustomDrugShape.id == DrugDimension.shape)
                     .join(LocationMaster, on=LocationMaster.id == recommended_location[transfer_location][0]['id'])
                     .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id)
                     .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id)
                     .where(ProductDetails.rfid == rfid))
            response_dict = {}
            for record in query:
                product_id = record['product_id']
                response_dict = {
                    "product_id": product_id,
                    "rfid": record['rfid'],
                    "ndc": record['ndc'],
                    "lot_number": record['lot_number'],
                    "drug_name": record['drug_name'],
                    "delivery_date": record['delivery_date'],
                    "status": record['status'],
                    "image_name": record['image_name'],
                    "imprint": record['imprint'],
                    "color": record['color'],
                    "drug_shape": record['shape'],
                    "canister_serial_number": record['canister_serial_number'],
                    "drawer_number": record["drawer_name"],
                    "shelf": record["shelf"],
                    "display_location": record["display_location"],
                    "serial_number": record["csr_serial_number"],
                    "device_type_id": record["device_type_id"],
                    "ip_address": record["ip_address"],
                    "secondary_ip_address": record["secondary_ip_address"],
                    "strength": record["strength"],
                    "strength_value": record["strength_value"],
                    "device_name": record["device_name"],
                    "device_type_name": record["device_type"][0:3] if record.get("device_type") else None,
                    "old_canister_data": db_get_old_canister(record['product_id'], company_id) or []
                }
            return response_dict
        else:
            return error(3017)
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_get_product_details {}".format(e))
    except Exception as e:
        logger.error("error in db_get_product_details {}".format(e))


@log_args_and_response
def db_get_product_id(canister_serial_number):
    """
    This functions gets the product id based on serial number
    @param : canister_serial_number
    @return:
    """
    try:
        product_id = ProductDetails.select(ProductDetails.product_id).where(
            ProductDetails.canister_serial_number == canister_serial_number).scalar()
        return product_id
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_get_product_id {}".format(e))
    except Exception as e:
        logger.error("error in db_get_product_id {}".format(e))


@log_args_and_response
def db_get_alternate_products(rfid, clauses=None):
    """
    This functions gets alternate products which can be failed with same reason for same drug init
    @param : None
    """
    try:
        response_dict = []
        ProductDetailsAlias = ProductDetails.alias()
        clauses.append((ProductDetailsAlias.rfid == rfid))
        clauses.append((ProductDetails.status == settings.PRODUCT_TESTING_PENDING))
        query = ProductDetails.select(ProductDetails.product_id, ProductDetails.lot_number, ProductDetails.ndc) \
            .join(ProductDetailsAlias, on=((ProductDetails.rfid != ProductDetailsAlias.rfid) & (
                    ProductDetails.ndc == ProductDetailsAlias.ndc))) \
            .where(functools.reduce(operator.and_, clauses)).dicts()
        if query.exists():
            for record in query:
                response_dict.append({
                    "product_id": record["product_id"],
                    "lot_number": record["lot_number"],
                    "ndc": record["ndc"]
                })
            return True, response_dict
        else:
            return False, response_dict
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_canister_for_testing {}".format(e))
    except Exception as e:
        logger.error("error in get_canister_for_testing {}".format(e))


@retry(3)
def update_canister_testing_data_in_couch_db(document_name, company_id, canister_testing_data, reset_data=False):
    """
    updates couch-db doc for manual fill station of a particular system

    @param canister_testing_data:
    @param document_name:
    @param system_id:
    @param reset_data:
    """
    try:
        logger.info("Inside update_canister_testing_data_in_couch_db -- document_name: {}, system_id: {}, mfs_data: {}, "
                    "reset_data: {}".format(document_name, company_id, canister_testing_data, reset_data))
        document = initialize_couch_db_doc(document_name,
                                           company_id=company_id)
        couchdb_doc = document.get_document()
        couchdb_doc.setdefault("data", {})
        for key, value in canister_testing_data.items():
            couchdb_doc["type"] = "canister_testing"
            couchdb_doc["data"][key] = value
        if reset_data:
            couchdb_doc["data"] = {}
        document.update_document(couchdb_doc)
        return True, True
    except couchdb.http.ResourceConflict:
        settings.logger.info("EXCEPTION: Document update conflict.")
        return False, False
    except Exception as e:
        logger.error(e, exc_info=True)
        return False, False


@log_args_and_response
def db_get_serial_number(product_id):
    """
    This functions gets the canister_serial_number for given product_id
    @return:
    """
    try:
        canister_serial_number = ProductDetails.select(ProductDetails.canister_serial_number).where(
            ProductDetails.product_id == product_id).scalar()
        return canister_serial_number
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_get_serial_number {}".format(e))
    except Exception as e:
        logger.error("error in db_get_serial_number {}".format(e))


@log_args_and_response
def db_get_new_canister_id(product_id):
    """
    This functions gets the new canister id of given product_id
    @return:
    """
    try:
        new_canister_id = CanisterMaster.select(CanisterMaster.id).where(
            CanisterMaster.product_id == product_id).scalar()
        return new_canister_id
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_get_new_canister_id {}".format(e))
    except Exception as e:
        logger.error("error in db_get_new_canister_id {}".format(e))


@log_args_and_response
def db_update_product_status_skipped(lot_numbers):
    """
    This functions updates testing status skipped for given lot products
    @return:
    """
    try:
        data = get_canister_testing_count_dao()
        current_batch_canisters = data[2]
        return ProductDetails.update(is_skipped=True).where(
            ProductDetails.lot_number.in_(lot_numbers) and ProductDetails.product_id.in_(
                current_batch_canisters)).execute()
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_update_product_status_skipped {}".format(e))
    except Exception as e:
        logger.error("error in db_update_product_status_skipped {}".format(e))


@log_args_and_response
def db_get_max_used_ndc_from_fndc(fndc):
    """
    This functions max used ndc from given fndc
    @return:
    """
    try:
        result = (SlotDetails.select(DrugMaster.ndc, SlotDetails.drug_id, fn.COUNT(SlotDetails.drug_id).alias('num_rows'))
                  .join(DrugMaster, on=(DrugMaster.id == SlotDetails.drug_id))
                  .where(DrugMaster.formatted_ndc == fndc)
                  .group_by(SlotDetails.drug_id)
                  .order_by(fn.COUNT(SlotDetails.drug_id).desc())
                  ).dicts()
        if result.exists():
            for record in result:
                ndc = record["ndc"]
                if ndc:
                    return ndc
        else:
            query = DrugMaster.select(DrugMaster.ndc).where(DrugMaster.formatted_ndc == fndc).dicts()
            for record in query:
                ndc = record["ndc"]
                if ndc:
                    return ndc
        return False
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_update_product_status_skipped {}".format(e))
    except Exception as e:
        logger.error("error in db_update_product_status_skipped {}".format(e))


@log_args_and_response
def db_check_all_canisters_tested(canister_serial_number):
    """
    This functions fetches count of remaining canisters to test in lot of given canister_serial_number
    @return:
    """
    try:
        lot_number = ProductDetails.select(ProductDetails.lot_number).where(
            ProductDetails.canister_serial_number == canister_serial_number).scalar()
        count = ProductDetails.select(fn.COUNT(ProductDetails.id).alias('product_count')).where(
            (ProductDetails.lot_number == lot_number) & (ProductDetails.status.not_in(
                [settings.PRODUCT_STATUS_TRANSFER_PENDING, settings.PRODUCT_STATUS_DONE,
                 settings.PRODUCT_STATUS_BROKEN]))
        ).scalar()
        return count, lot_number
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_check_all_canisters_tested {}".format(e))
    except Exception as e:
        logger.error("error in db_check_all_canisters_tested {}".format(e))


@log_args_and_response
def db_get_product_from_lot_number(lot_number):
    """
    This functions fetches data of all tested products for given lot_number
    @return:
    """
    try:
        query = ProductDetails.select(ProductDetails.product_id, CanisterTestingStatus.status_id,
                                      CanisterTestingStatus.modified_by,
                                      CanisterTestingStatus.reason, CanisterMaster.id.alias("new_canister_id")) \
            .join(CanisterMaster, on=CanisterMaster.product_id == ProductDetails.product_id) \
            .join(CanisterTestingStatus, on=CanisterTestingStatus.canister_id == CanisterMaster.id) \
            .where(ProductDetails.lot_number == lot_number).dicts()
        return query
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_get_product_from_lot_number {}".format(e))
    except Exception as e:
        logger.error("error in db_get_product_from_lot_number {}".format(e))


@log_args_and_response
def db_get_old_canisters(canister_serial_number):
    """
    This functions fetches all old canisters for given serial number
    @return:
    """
    try:
        old_canisters = []
        query = OldCanisterMapping.select(OldCanisterMapping.old_canister_id) \
            .join(ProductDetails, ProductDetails.product_id == OldCanisterMapping.product_id) \
            .where(ProductDetails.canister_serial_number == canister_serial_number).dicts()
        for record in query:
            old_canisters.append(record["old_canister_id"])
        return old_canisters
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_get_old_canisters {}".format(e))
    except Exception as e:
        logger.error("error in db_get_old_canisters {}".format(e))


@log_args_and_response
def db_get_old_canister_expiry_date(canister_serial_number):
    """
    This functions fetches old canister's expiry date for given serial number
    @return:
    """
    try:
        expiry_date = None
        query = CanisterMaster.select(CanisterMaster.expiry_date, CanisterMaster.id) \
            .join(OldCanisterMapping, on=OldCanisterMapping.old_canister_id == CanisterMaster.id) \
            .join(ProductDetails, on=ProductDetails.product_id == OldCanisterMapping.product_id) \
            .where(ProductDetails.canister_serial_number == canister_serial_number).dicts()
        for record in query:
            expiry_date = record["expiry_date"]
            status = CanisterMaster.update(expiry_date=None).where(CanisterMaster.id == record["id"]).execute()
            break
        return expiry_date
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in db_get_old_canister_expiry_date {}".format(e))
    except Exception as e:
        logger.error("error in db_get_old_canister_expiry_date {}".format(e))
