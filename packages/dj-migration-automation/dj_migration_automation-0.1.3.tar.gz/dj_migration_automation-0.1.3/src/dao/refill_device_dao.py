from peewee import *
from peewee import InternalError

import settings
from dosepack.utilities.utils import fn_shorten_drugname, log_args_and_response, get_current_date_time, \
    last_day_of_month
from src.dao.drug_dao import logger
from src.service.drug_search import get_ndc_list_for_barcode
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_canister_master import CanisterMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_drug_details import DrugDetails
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_dimension import DrugDimension
from src.model.model_custom_drug_shape import CustomDrugShape
from src import constants
from src.api_utility import get_results, get_multi_search
from datetime import date, timedelta, datetime

logger = settings.logger


@log_args_and_response
def drug_list_to_calibrate(paginate, filter_fields, sort_fields, company_id):
    """
    It fetches the data for the Drug Calibration Process Screen.
    @param company_id:
    @param paginate:
    @param filter_fields:
    @param sort_fields:
    @return:
    """
    logger.debug("Inside drug_list_to_calibrate.")
    try:
        response = dict()
        clauses = []
        like_search_list = ["drug_name", "ndc"]
        membership_search_list = ["shape", "calibration_status"]
        order_list = []
        if sort_fields:
            order_list.extend(sort_fields)

        fields_dict = {"drug_name": DrugMaster.concated_drug_name_field(),
                       "unique_drug_id": UniqueDrug.id,
                       "imprint": DrugMaster.imprint,
                       "ndc": DrugMaster.ndc,
                       "shape": CustomDrugShape.name,
                       "calibration_status": fn.IF(UniqueDrug.unit_weight.is_null(False), 'Done', 'Pending')}

        global_search = []
        for value in fields_dict.values():
            global_search.append(value)
        if filter_fields and filter_fields.get('global_search', None) is not None:
            multi_search_string = filter_fields['global_search'].split(',')
            multi_search_string.remove('') if '' in multi_search_string else multi_search_string
            clauses = get_multi_search(clauses, multi_search_string, global_search)

        shape_list_data = DrugDimension.select(CustomDrugShape.name.alias('shape')).dicts() \
            .join(CustomDrugShape, on=DrugDimension.shape == CustomDrugShape.id) \
            .group_by(CustomDrugShape.id)

        logger.info(f"In drug_list_to_calibrate, shape_list_data: {shape_list_data}")

        shape_list = {'shape': []}
        for record in shape_list_data.dicts():
            shape_list['shape'].append(record['shape'])

        logger.info(f"In drug_list_to_calibrate, shape_list: {shape_list}")

        query = DrugDimension.select(fields_dict["drug_name"].alias("drug_name"),
                                     fields_dict["unique_drug_id"].alias("unique_drug_id"),
                                     fields_dict["imprint"],
                                     fields_dict["ndc"],
                                     fields_dict["shape"].alias("shape"),
                                     DrugMaster.color,
                                     DrugDetails.last_seen_by.alias('last_seen_with'),
                                     fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                           DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                     fields_dict["calibration_status"].alias("calibration_status"),
                                     UniqueDrug.unit_weight,
                                     DrugMaster.image_name.alias("drug_image")
                                     ) \
            .join(UniqueDrug, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
            .join(DrugMaster, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                  & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(CustomDrugShape, on=CustomDrugShape.id == DrugDimension.shape) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                      (DrugDetails.company_id == company_id)))\
            .join(DrugStockHistory, JOIN_LEFT_OUTER, ((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                              (DrugStockHistory.is_active == True) &
                                                      (DrugStockHistory.company_id == company_id)))

        exact_search_list = None
        if "ndc" in filter_fields:
            filter_fields['ndc'] = filter_fields['ndc'].split(',')
            if len(filter_fields['ndc'][0]) == 11:
                if filter_fields['ndc'][0].isnumeric():
                    exact_search_list = ["ndc"]
                    like_search_list = ["drug_name"]

        results, count = get_results(query.dicts(), fields_dict=fields_dict,
                                                   filter_fields=filter_fields,
                                                   clauses=clauses,
                                                   like_search_list=like_search_list,
                                                   membership_search_list=membership_search_list,
                                                   sort_fields=order_list,
                                                   paginate=paginate,
                                                   last_order_field=[fields_dict["calibration_status"].desc(),
                                                                     fields_dict["drug_name"]],
                                                   exact_search_list = exact_search_list)
        response['calibration_drug_list'] = results
        response['total_drugs'] = count
        response['shape_list'] = shape_list
        return response

    except (IntegrityError, InternalError) as e:
        logger.info(e)
        raise


@log_args_and_response
def get_drug_data_dao(ndc_list, **kwargs):
    """
    This function returns drug data corresponding to given ndc and selected_drug
    @param ndc_list: list of ndc when scanned
    @param kwargs:
    @return:
    """
    logger.debug("Inside get_drug_data_dao.")
    try:
        query = DrugMaster.select(
            UniqueDrug.id.alias('unique_drug_id'),
            DrugMaster.concated_drug_name_field().alias("drug_name"),
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.ndc,
            DrugMaster.formatted_ndc,
            DrugMaster.txr,
            DrugMaster.imprint,
            UniqueDrug.unit_weight,
            CustomDrugShape.name.alias('shape_name'),
            DrugMaster.image_name.alias('drug_image')).dicts() \
            .join(UniqueDrug, on=((DrugMaster.txr == UniqueDrug.txr) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc))) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, JOIN_LEFT_OUTER, on=DrugDimension.shape == CustomDrugShape.id) \
            .where(DrugMaster.ndc << ndc_list)

        logger.info(f"In get_drug_data_dao, query: {query}")

        return list(query)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise
    except DoesNotExist as e:
        return []
        pass


@log_args_and_response
def get_selected_drug_ndc_list(unique_drug_id):
    logger.debug("Inside get_selected_drug_ndc.")
    ndc_list = list()
    try:
        query = UniqueDrug.select(DrugMaster.ndc).dicts() \
            .join(DrugMaster, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .where(UniqueDrug.id == unique_drug_id)
        for record in query:
            ndc_list.append(record["ndc"])

        logger.info(f"Inside get_selected_drug_ndc, ndc_list: {ndc_list}")

        return ndc_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def get_latest_replenish_lot_info_of_canister(canister_id: int, no_of_records: int) -> list:
    """
    Method to get the latest lot info based on recent replenishment data of a canister
    @param canister_id:
    @param no_of_records:
    @return:
    """
    logger.debug("Inside get_latest_replenish_lot_info_of_canister")

    try:
        query = CanisterTracker.select(fn.Distinct(CanisterTracker.lot_number),
                                       CanisterTracker.expiration_date).dicts() \
            .where(CanisterTracker.canister_id == canister_id,
                   CanisterTracker.qty_update_type_id ==
                   constants.CANISTER_QUANTITY_UPDATE_TYPE_REPLENISHMENT,
                   CanisterTracker.lot_number.is_null(False),
                   CanisterTracker.lot_number != '') \
            .order_by(CanisterTracker.created_date.desc()) \
            .limit(no_of_records)
        return list(query)
    except InternalError as e:
        logger.error(e)
        raise


@log_args_and_response
def get_drug_dimension_data_based_on_drug_id(drug_id):

    logger.debug("Inside get_drug_dimension_data_based_on_drug_id")
    try:
        drug_query = DrugDimension.select(DrugDimension, UniqueDrug.unit_weight) \
            .join(UniqueDrug, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(DrugMaster,
                  on=(DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) & (DrugMaster.txr == UniqueDrug.txr)) \
            .where(DrugMaster.id == drug_id).dicts().get()
        return drug_query
    except InternalError as e:
        logger.error(e)
        raise
    except DoesNotExist as e:
        logger.error(e)
        return {}


@log_args_and_response
def update_canister_master(update_dict, **kwargs):
    logger.debug("Inside update_canister_master")
    try:
        update_status = CanisterMaster.db_update(update_dict=update_dict, **kwargs)
        return update_status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


def create_canister_tracker(create_dict):
    logger.debug("Inside create_canister_tracker")
    try:
        record = CanisterTracker.db_create_record(data=create_dict, table_name=CanisterTracker, get_or_create=False)
        return record
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def update_calibrated_drug(drug_data):
    logger.debug("inside update_calibrated_drug")
    try:
        update_dict = {}
        unique_drug_id = drug_data["unique_drug_id"]
        update_dict['unit_weight'] = drug_data['unit_weight']
        update_dict['modified_date'] = get_current_date_time()
        logger.info(
            f"In update_calibrated_drug, update DrugDimension >> unique_drug_id:{unique_drug_id}, update_dict:{update_dict}")

        status = UniqueDrug.db_update(update_dict=update_dict, id=unique_drug_id)

        return status
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_drug_dimension_data(unique_drug_id: int) -> dict:
    """
    This function fetches the drug_dimension data for the given drug
    """
    logger.debug("In get_drug_dimension_data")
    try:
        return DrugDimension.db_get_data(unique_drug_id=unique_drug_id)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_canister_info(canister_id: int, company_id: int) -> dict:
    """
        Returns dict of canister with drug data
        @param canister_id:
        @param company_id: int
        :return: dict
    """
    logger.debug("Inside db_get_canister_info")
    try:
        canister_drug_data = CanisterMaster.select(
            CanisterMaster.id.alias('canister_id'),
            fn.IF(
                CanisterMaster.expiry_date <= date.today() + timedelta(
                    settings.TIME_DELTA_FOR_EXPIRED_CANISTER),
                constants.EXPIRED_CANISTER,
                fn.IF(
                    CanisterMaster.expiry_date <= date.today() + timedelta(
                        settings.TIME_DELTA_FOR_EXPIRED_CANISTER + settings.TIME_DELTA_FOR_EXPIRES_SOON_CANISTER),
                    constants.EXPIRES_SOON_CANISTER, constants.NORMAL_EXPIRY_CANISTER)).alias("expiry_status"),
            CanisterMaster.drug_id.alias('canister_drug_id'),
            CanisterMaster.available_quantity,
            fn.IF(CanisterMaster.available_quantity < 0, 0, CanisterMaster.available_quantity).alias(
                'display_quantity'),
            CanisterMaster.canister_type,
            CanisterMaster.product_id,
            DrugMaster.drug_name,
            DrugMaster.ndc.alias('canister_ndc'),
            DrugMaster.formatted_ndc,
            DrugMaster.txr,
            DrugMaster.strength,
            DrugMaster.strength_value,
            DrugMaster.imprint,
            DrugMaster.image_name,
            DrugMaster.brand_flag,
            DrugMaster.shape,
            DrugMaster.color,
            UniqueDrug.is_powder_pill,
            fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                  DrugStockHistory.is_in_stock).alias("is_in_stock"),
            DrugDetails.last_seen_by.alias('last_seen_with'),
            DrugDimension.approx_volume,
            UniqueDrug.id.alias('unique_drug_id'),
            DrugMaster.concated_drug_name_field(include_ndc=True).alias('concat_drug_name')
        ).dicts() \
            .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) &
                                                         (DrugStockHistory.is_active == 1) &
                                                         (DrugStockHistory.company_id == CanisterMaster.company_id))) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == CanisterMaster.company_id))) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .where(CanisterMaster.id == canister_id,
                   CanisterMaster.company_id == company_id).get()

        canister_drug_data["shortened_drug_name"] = fn_shorten_drugname(canister_drug_data["drug_name"])
        return canister_drug_data

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except (DoesNotExist, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_concatenated_fndc_txr_from_ndc_list(ndc_list):

    logger.debug("Inside get_concatenated_fndc_txr_from_ndc_list")
    try:
        concatenated_fndc_txr_list = list()
        for record in DrugMaster.select(DrugMaster.concated_fndc_txr_field().alias('fndc_txr')) \
                .where(DrugMaster.ndc << ndc_list).dicts():
            concatenated_fndc_txr_list.append(record['fndc_txr'])
        return concatenated_fndc_txr_list
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise


def validate_canister(canister_id: int) -> bool:
    logger.debug("Inside validate_canister")
    try:
        canister = CanisterMaster.get(id=canister_id)
        return canister.active
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_available_quantity_in_canister(canister_id):
    logger.debug("Inside get_available_quantity_in_canister")
    try:

        canister_available_quantity = CanisterMaster.get_available_quantity(canister_id=canister_id)
        return canister_available_quantity
    except InternalError as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_expiry_date_of_canister(canister_id):
    try:
        expiry_date = CanisterMaster.select(CanisterMaster.expiry_date).dicts().where(CanisterMaster.id == canister_id).get()
        return expiry_date["expiry_date"]
    except InternalError as e:
        logger.error(f"error in get_expiry_date_of_canister, e: {e}")
        raise e
    except Exception as e:
        logger.error(f"error in get_expiry_date_of_canister, e: {e}")
        raise e


@log_args_and_response
def get_ndc_list_for_scanned_ndc(scanned_ndc):
    logger.debug("Inside get_ndc_list_for_scanned_ndc.")
    ndc_dict = {"scanned_ndc": scanned_ndc}
    try:
        ndc_list, drug_scan_type, lot_no, expiration_date, bottle_qty, case_id, upc, bottle_total_qty = get_ndc_list_for_barcode(ndc_dict,
                                                                                                               refill=True)
        return ndc_list
    except InternalError as e:
        logger.error(e)
        raise
    except Exception as e:
        logger.error(e)
        raise


@log_args_and_response
def get_canister_lowest_expiry_date(canister_id):
    try:
        expiry_date = None
        expiry_date_query = (CanisterTracker.select(fn.MIN(
            fn.STR_TO_DATE(CanisterTracker.expiration_date, "%m-%Y")).alias("canister_expiry"))
                             .dicts()
                             .where(CanisterTracker.canister_id == canister_id,
                                    CanisterTracker.usage_consideration << [constants.USAGE_CONSIDERATION_PENDING,
                                                                            constants.USAGE_CONSIDERATION_IN_PROGRESS]))

        for record in expiry_date_query:
            expiry_date = record["canister_expiry"]

        if expiry_date:
            expiry_date = "-".join(expiry_date.split("-")[:-1])
            expiry_date = datetime.strptime(expiry_date, "%Y-%m").strftime("%m-%Y")
            expiry_date = datetime.strptime(expiry_date, "%m-%Y").date()
            expiry_date = last_day_of_month(expiry_date)
        else:
            expiry_date = CanisterMaster.select(CanisterMaster.expiry_date).dicts().where(CanisterMaster.id == canister_id).get()
            expiry_date = expiry_date["expiry_date"]

        return expiry_date
    except InternalError as e:
        logger.error(f"error in get_canister_lowest_expiry_date, e: {e}")
        raise e
    except Exception as e:
        logger.error(f"error in get_canister_lowest_expiry_date, e: {e}")
        raise e
