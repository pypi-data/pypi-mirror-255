from peewee import *
from peewee import DoesNotExist, InternalError, IntegrityError

import settings
import datetime
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import get_current_date_time, log_args_and_response, \
    fn_shorten_drugname, get_canister_volume, get_max_possible_drug_quantities_in_canister, last_day_of_month
from dosepack.validation.validate import validate
from src import constants
from src.api_utility import calculate_max_possible_drug_quantity_in_refill_device
from src.dao.batch_dao import get_progress_batch_id, db_get_last_imported_batch_by_system_dao
from src.dao.canister_dao import db_get_reserved_canister_data, get_replenish_mini_batch_wise, \
    get_import_batch_id_from_system_id_or_device_id, get_canister_device_id_by_pack_analysis, \
    insert_records_in_reserved_canister, remove_pack_canister_from_replenish_skipped_canister, \
    get_empty_location_by_quadrant, get_canister_data_by_canister_ids
from src.dao.canister_transfers_dao import get_canister_replenish_transfer_data_dao
from src.dao.device_manager_dao import get_system_id_based_on_device_type, get_robots_by_system_id_dao
from src.dao.drug_inventory_dao import get_drug_info_based_on_ndc_dao
from src.dao.guided_replenish_dao import trolley_data_for_guided_tx
from src.dao.pack_analysis_dao import get_canister_drug_quantity_required_in_batch, \
    update_status_in_pack_analysis_details, update_batch_change_tracker_after_replenish_skipped_canister
from src.dao.pack_dao import get_filling_pending_pack_ids, get_packs_from_pack_queue_for_system
from src.dao.refill_device_dao import update_canister_master, create_canister_tracker, get_selected_drug_ndc_list, \
    update_calibrated_drug, drug_list_to_calibrate, db_get_canister_info, get_concatenated_fndc_txr_from_ndc_list, \
    validate_canister, get_drug_dimension_data, get_drug_data_dao, get_latest_replenish_lot_info_of_canister, \
    get_drug_dimension_data_based_on_drug_id, \
    get_available_quantity_in_canister, get_ndc_list_for_scanned_ndc, get_expiry_date_of_canister, \
    get_canister_lowest_expiry_date
from src.service.canister_recommendation import revert_canister_usage_by_recom
from src.service.drug_inventory import inventory_adjust_quantity
from utils.drug_inventory_webservices import get_current_inventory_data

logger = settings.logger


@log_args_and_response
def get_drug_list_to_calibrate(filter_fields, paginate, sort_fields, company_id):
    """
    This fetches data for the Drug Calibration Process Screen
    @param paginate:
    @param filter_fields:
    @param sort_fields: optional
    @return: dict
    """
    logger.debug("Inside get_drug_list_to_calibrate.")

    try:
        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        response = drug_list_to_calibrate(paginate=paginate, filter_fields=filter_fields, sort_fields=sort_fields,
                                          company_id=company_id)
        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.info(e)
        return error(2001)


@log_args_and_response
def get_drug_data_for_refilling(args):

    logger.debug("Inside get_drug_data_for_refilling.")

    canister_id = args["canister_id"]
    canister_drug_id = args["canister_drug_id"]
    canister_fndc = args["canister_fndc"]
    canister_txr = args["canister_txr"]
    if canister_txr is None or canister_txr == constants.NULL_STRING:
        canister_txr = ''
    scanned_ndc = args["scanned_ndc"]
    no_of_records = int(args.get("no_of_records", 3))
    response = {"recent_lot_info": list()}
    canister_fndc_txr = '{}#{}'.format(canister_fndc, canister_txr)

    logger.debug("In get_drug_data_for_refilling, caniser_fndc_txr: " + str(canister_fndc_txr))

    try:
        # validate scanned_ndc with canister_ndc
        scanned_ndc_list = get_ndc_list_for_scanned_ndc(scanned_ndc=scanned_ndc)
        logger.debug("In get_drug_data_for_refilling: scanned_ndc_list: {}".format(scanned_ndc_list))
        # ndc not found
        if not scanned_ndc_list:
            logger.error("In get_drug_data_for_refilling, Valid NDC not found")
            return error(9013)

        logger.debug("In get_drug_data_for_refilling, Fetching fndc_txr from scanned_ndc_list")

        scanned_fndc_txr_list = get_concatenated_fndc_txr_from_ndc_list(ndc_list=scanned_ndc_list)

        logger.debug(
            "In get_drug_data_for_refilling, Fetched fndc_txr from scanned_ndc_list: " + str(scanned_fndc_txr_list))

        # scanned bottle drug and canister drug not matched
        if not canister_fndc_txr in scanned_fndc_txr_list:
            logger.error("drug in canister and scanned drug are not same")
            return error(9013)

        logger.debug(
            "In get_drug_data_for_refilling, Fetching recent_replenish_info for canister {}".format(canister_id))
        #  fetch recent replenish info

        recent_replenish_data = get_latest_replenish_lot_info_of_canister(canister_id=canister_id,
                                                                          no_of_records=no_of_records)
        logger.info(f"In get_drug_data_for_refilling, recent_replenish_data: {recent_replenish_data}")

        for replenish_info in recent_replenish_data:
            lot_info = {"lot_number": replenish_info.get("lot_number"),
                        "expiration_date": replenish_info.get("expiration_date")}
            response["recent_lot_info"].append(lot_info)

        logger.debug("Fetched replenish_info {} for canister {}".format(response["recent_lot_info"], canister_id))

        logger.debug(
            "In get_drug_data_for_refilling, Fetching drug dimension data for drug_id " + str(canister_drug_id))

        # fetch drug calibration data
        drug_dimenstion_data = get_drug_dimension_data_based_on_drug_id(drug_id=canister_drug_id)

        logger.debug(
            "In get_drug_data_for_refilling, Fetched drug_dimension data: {} for drug: {}".format(drug_dimenstion_data,
                                                                                                  canister_drug_id))

        if drug_dimenstion_data.get("unit_weight") is None:
            response["drug_calibration_status"] = constants.DRUG_CALIBRATION_PENDING
            response["drug_unit_weight"] = None
            response["max_possible_drug_quantity_in_refill_device"] = None
        else:
            response["drug_calibration_status"] = constants.DRUG_CALIBRATION_DONE
            response["drug_unit_weight"] = drug_dimenstion_data["unit_weight"]
            response[
                "max_possible_drug_quantity_in_refill_device"] = calculate_max_possible_drug_quantity_in_refill_device(
                drug_unit_weight=drug_dimenstion_data["unit_weight"])
        logger.debug("Response of get_drug_data_for_refilling: " + str(response))
        return create_response(response)
    except InternalError as e:
        logger.error(e)
        return error(2001)


@log_args_and_response
def get_drug_data_calibration(drug_data):
    """
    This fetches the drug data for calibration.
    @param drug_data: dict
    @return: dict
    """
    logger.debug("Inside get_drug_data_calibration.")
    try:
        scanned_ndc = drug_data["scanned_ndc"]
        ndc_list = get_ndc_list_for_scanned_ndc(scanned_ndc)
        if ndc_list:
            drug_data_response = get_drug_data_dao(ndc_list=ndc_list)
        else:
            return error(9005)
        drug_data_calibration = {}

        for record in drug_data_response:
            drug_data_calibration["unique_drug_id"] = record["unique_drug_id"]
            drug_data_calibration["drug_name"] = record["drug_name"]
            drug_data_calibration["shortened_drug_name"] = fn_shorten_drugname(drug_name=record["drug_name"],
                                                                               ai_width=18, ai_min=12)
            drug_data_calibration["strength"] = record["strength"]
            drug_data_calibration["strength_value"] = record["strength_value"]
            drug_data_calibration["ndc"] = record["ndc"]
            drug_data_calibration["formatted_ndc"] = record["formatted_ndc"]
            drug_data_calibration["txr"] = record["txr"]
            drug_data_calibration["imprint"] = record["imprint"]
            drug_data_calibration["unit_weight"] = record["unit_weight"]
            drug_data_calibration["shape"] = record["shape_name"]
            drug_data_calibration["drug_image"] = record["drug_image"]

        logger.info(f"In get_drug_data_calibration, drug_data_calibration: {drug_data_calibration}")

        if drug_data_calibration["unit_weight"] is None:
            drug_data_calibration["calibration_status"] = constants.DRUG_CALIBRATION_PENDING
        else:
            drug_data_calibration["calibration_status"] = constants.DRUG_CALIBRATION_DONE

        if drug_data["selected_drug"] is not None:
            selected_drug_id = drug_data["selected_drug"]
            selected_drug_ndc_list = get_selected_drug_ndc_list(unique_drug_id=selected_drug_id)
            if drug_data_calibration["ndc"] in selected_drug_ndc_list:
                return create_response(drug_data_calibration)
            else:
                return error(1037)
        else:
            return create_response(drug_data_calibration)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)


@validate(required_fields=['unique_drug_id', 'unit_weight'])
def save_calibration_data(drug_data):
    """
    To update Drug Dimension with given Unit_weight
    @param drug_data: unique_drug_id and unit_weight
    @return: dict
    """
    logger.debug("inside save_calibration_data")
    try:
        if drug_data and drug_data["unit_weight"] == 0:
            return error(9014)

        drug_status = update_calibrated_drug(drug_data)
        logger.info(f"In save_calibration_data, update_calibrated_drug status: {drug_status}")

        return create_response(settings.SUCCESS_RESPONSE)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["canister_id", "available_quantity", "filled_quantity", "scanned_ndc", "lot_number",
                           "expiration_date", "user_id", "max_canister_capacity", "module_id"],
          non_negative_integer_validation=["filled_quantity", "canister_id", "user_id", "module_id"])
def update_canister_quantity(dict_canister_info):
    """ Updates the canister quantity for the given canister id

        Args:
            dict_canister_info (dict): The key containing the canister id, filled quantity

        Returns:
           json: success or the failure response

        Examples:
            >>> update_canister_quantity({"canister_id":2314, "available_quantity":350, "filled_quantity":50,
                            "canister_drug_id":76479, "lot_number": PZ0493, "expiration_date": "02-2022",
                             "user_id":1, "device_id":12})
                {"status": "success", "data": 1}
    """
    logger.debug("Inside update_canister_quantity")

    available_quantity = dict_canister_info.get("available_quantity")
    if available_quantity is None:
        available_quantity = 0

    filled_quantity = dict_canister_info.get("filled_quantity")
    if filled_quantity is None:
        filled_quantity = 0

    canister_id = dict_canister_info.get("canister_id")
    scanned_ndc = str(dict_canister_info.get("scanned_ndc"))
    user_id = dict_canister_info.get("user_id")
    device_id = dict_canister_info.get("device_id")
    lot_number = dict_canister_info.get("lot_number", None)
    expiration_date = dict_canister_info.get("expiration_date", None)
    drug_scan_type_id = dict_canister_info.get("drug_scan_type", constants.DATA_MATRIX)
    replenish_mode_id = dict_canister_info.get("replenishment_mode", constants.MANUAL_CODE)
    guided_tx_flag = dict_canister_info.get("guided_tx_flag", False)
    guided_tx_cycle_id = dict_canister_info.get("guided_tx_cycle_id", None)
    missing_qty = dict_canister_info.get("missing_qty")
    case_id = dict_canister_info.get("case_id", None)
    module_id = dict_canister_info.get("module_id")
    max_canister_capacity = dict_canister_info.get(
        "max_canister_capacity")
    company_id = dict_canister_info.get("company_id")
    canister_data = None
    try:

        # fetch drug_id of scanned_ndc
        logger.debug("In update_canister_quantity, Fetching drug info based on ndc: ndc - " + scanned_ndc)
        drug_info = get_drug_info_based_on_ndc_dao(ndc_list=[scanned_ndc])[scanned_ndc]

        if not drug_info:
            logger.error("In update_canister_quantity, Invalid ndc - " + scanned_ndc)
            return error(9017)

        logger.debug("In update_canister_quantity, Drug info fetched: {}, for ndc {}".format(drug_info, scanned_ndc))

        drug_id = drug_info["id"]

        # get available quantity of canister from database(canister master table)
        canister_available_quantity = get_available_quantity_in_canister(canister_id=canister_id)
        canister_expiry_date = get_expiry_date_of_canister(canister_id=canister_id)
        logger.debug(
            "In update_canister_quantity, available quantity in canister {} - {} qty.".format(canister_id,
                                                                                              canister_available_quantity))

        if replenish_mode_id == constants.MANUAL_CODE:
            if int(filled_quantity) + int(canister_available_quantity) <= int(max_canister_capacity):
                updated_available_quantity = int(canister_available_quantity) + int(filled_quantity)
                quantity_adjusted = filled_quantity
            else:
                return error(14007)
        else:
            updated_available_quantity = int(filled_quantity)
            quantity_adjusted = int(filled_quantity) - int(available_quantity)

        update_canister_dict = {
            "available_quantity": updated_available_quantity,
            "modified_by": user_id,
            "modified_date": get_current_date_time()
        }
        if canister_expiry_date:
            lowest_canister_expiry_date = get_canister_lowest_expiry_date(canister_id=canister_id)
            if canister_expiry_date < lowest_canister_expiry_date:
                update_canister_dict["expiry_date"] = canister_expiry_date
            else:
                update_canister_dict["expiry_date"] = lowest_canister_expiry_date
        elif not canister_expiry_date:
            expiry = expiration_date.split("-")
            expiry_month = int(expiry[0])
            expiry_year = int(expiry[1])
            expiry_date = last_day_of_month(datetime.date(expiry_year, expiry_month, 1))

            update_canister_dict["expiry_date"] = expiry_date
        if not updated_available_quantity:
            update_canister_dict["expiry_date"] = None

        canister_tracker_create_dict = {
            "canister_id": canister_id,
            "device_id": device_id,
            "drug_id": drug_id,
            "qty_update_type_id": constants.CANISTER_QUANTITY_UPDATE_TYPE_REPLENISHMENT,
            "original_quantity": available_quantity,
            "quantity_adjusted": quantity_adjusted,
            "lot_number": lot_number,
            "expiration_date": expiration_date,
            "drug_scan_type_id": drug_scan_type_id,
            "replenish_mode_id": replenish_mode_id,
            "created_date": get_current_date_time(),
            "created_by": user_id,
            "case_id": case_id
        }

        with db.transaction():
            logger.debug("In update_canister_quantity, updating canister quantity in canister master: " + str(
                update_canister_dict))
            # update drug quantity in canister master
            canister_update_status = update_canister_master(update_dict=update_canister_dict, id=canister_id)

            # whenever we replenish canister we need to update status in pack analysis details as not skipped status
            # for the only those data for which packs are in pending state or progress pending packs and
            # pack analysis details status --> skipped status.
            pack_analysis_details_update_status, reverted_packs, system_device = update_status_in_pack_analysis_details(canister_id=canister_id,
                                                                                                         company_id=company_id,
                                                                                                         device_id=device_id
                                                                                                                        )
            robot_system_id = system_device[0]
            robot_device_id = system_device[1]
            logger.info(
                f"In update_canister_quantity, pack_analysis_details_update_status:{pack_analysis_details_update_status}")

            progress_batch_id = get_progress_batch_id(robot_system_id)
            if progress_batch_id and module_id == constants.MODULE_REPLENISH_SKIPPED_CANISTER:
                if reverted_packs:
                    logger.info(f"In update_canister_quantity, remove reverted pack-canister")
                    remove_status = remove_pack_canister_from_replenish_skipped_canister(pack_ids=list(reverted_packs),
                                                                                         canister_id=canister_id)

                    status = update_batch_change_tracker_after_replenish_skipped_canister(canister_id=canister_id,
                                                                                          user_id=user_id,
                                                                                          device_id=device_id,
                                                                                          reverted_packs=reverted_packs)
                    logger.info(f"In pack_analysis_details_update_status, batch_change_tracker update status:{status}")

                reverted_packs = revert_canister_usage_by_recom(company_id=company_id, device_id=robot_device_id,
                                                                canister_id=canister_id,
                                                                affected_pack_list=reverted_packs,
                                                                batch_id=progress_batch_id)

                batch_id = None
                reserved_canister_data = {batch_id: [canister_id]}
                reserved_canister_status = insert_records_in_reserved_canister(canister_data=reserved_canister_data)
                logger.info("Inserted data into reserved_canister, canister data {}".format(reserved_canister_status))

                # if reverted_packs:
                #     logger.info(f"In update_canister_quantity, remove reverted pack-canister")
                #     remove_status = remove_pack_canister_from_replenish_skipped_canister(pack_ids=list(reverted_packs),
                #                                                                          canister_id=canister_id)
                #
                #     # current_batch_id = get_import_batch_id_from_system_id_or_device_id(device_id=device_id)
                #     # logger.info(f"In update_canister_quantity, current_batch_id: {current_batch_id}")
                #     batch_id = None
                #     reserved_canister_data = {batch_id: [canister_id]}
                #     reserved_canister_status = insert_records_in_reserved_canister(canister_data=reserved_canister_data)
                #     logger.info("Inserted data into reserved_canister, canister data {}".format(reserved_canister_status))
                #
                #     status = update_batch_change_tracker_after_replenish_skipped_canister(canister_id=canister_id,
                #                                                                           user_id=user_id,
                #                                                                           device_id=device_id,
                #                                                                           reverted_packs=reverted_packs)
                #     logger.info(f"In pack_analysis_details_update_status, batch_change_tracker update status:{status}")

            logger.debug("In update_canister_quantity, Updating refilled canister data in canister tracker: " + str(
                canister_tracker_create_dict))
            # add record in canister tracker
            record = create_canister_tracker(create_dict=canister_tracker_create_dict)

            # if canister is currently reserved for any batch then updating replenish queue for v3 system type
            if not reverted_packs:
                canister_data = db_get_reserved_canister_data(canister_id=dict_canister_info["canister_id"])
                if canister_data:
                    robot_system_id = canister_data['system_id']
                robot_device_id = get_canister_device_id_by_pack_analysis(canister_id=dict_canister_info["canister_id"])
                logger.info('In update_canister_quantity, reserved_canister_data_while_replenish: ' + str(canister_data))

            if canister_data or reverted_packs:
                logger.info("In update_canister_quantity, updating_replenish_data_while_adjust_qty")
                update_replenish_based_on_system(system_id=robot_system_id, device_id=robot_device_id)

        logger.debug("In update_canister_quantity, canister quantity updated in canister_master and canister_tracker")

        # return trolley pop-up for GuidedTx flow
        if guided_tx_flag and guided_tx_cycle_id and missing_qty is not None and filled_quantity is not None \
                and (int(missing_qty) <= int(filled_quantity)):

            # obtain the location as well as update the status to replenish
            # check if available qty is equal to missing qty then only update status to replenish
            status, response = trolley_data_for_guided_tx(canister_id=canister_id,
                                                          guided_tx_cycle_id=guided_tx_cycle_id,
                                                          guided_tx_canister_status=constants.GUIDED_TRACKER_REPLENISH)

            logger.info(f"In update_canister_quantity, status: {status} and response: {response}")

            if status:
                return create_response(response)
            else:
                return error(1020, str(response))
        args = {
            "user_id": user_id,
            "ndc": scanned_ndc,
            "adjusted_quantity": quantity_adjusted,
            "company_id": company_id,
            "case_id": case_id,
            "is_replenish": True,
            "transaction_type": settings.EPBM_DRUG_ADJUSTMENT_INCREMENT
        }
        response = inventory_adjust_quantity(args)
        return create_response(settings.SUCCESS_RESPONSE)

    except (IntegrityError, InternalError, DataError):
        return error(2001)


@validate(required_fields=["canister_id", "company_id"])
@log_args_and_response
def get_canister_drug_info(args):
    """
    Gets canister and drug data given canister id
    :return: dict
    """
    logger.debug("Inside get_canister_drug_info")
    try:
        canister_id = args["canister_id"]
        company_id = args["company_id"]
        transfer_data_required = args.get("transfer_data")
        filling_pending_pack_ids: list = list()

        # first check whether scanned canister is of given company or not if not it will raise doesnotexist exception
        canister_drug_info = db_get_canister_info(canister_id=canister_id, company_id=company_id)
        inventory_data = get_current_inventory_data(ndc_list=[int(canister_drug_info['canister_ndc'])], qty_greater_than_zero=False)
        inventory_data_dict = {}
        for item in inventory_data:
            inventory_data_dict[item['ndc']] = item['quantity']
        canister_drug_info['inventory_qty'] = inventory_data_dict.get(canister_drug_info['canister_ndc'], 0)
        canister_drug_info['is_in_stock'] = 0 if canister_drug_info['inventory_qty'] == 0 else 1
        # check canister is active or not
        active_canister = validate_canister(canister_id=canister_id)

        if not active_canister:
            return error(3012)

        unit_drug_volume = canister_drug_info["approx_volume"]

        # get the robot system_id from the given company_id as of now.
        system_id = get_system_id_based_on_device_type(company_id=company_id,
                                                       device_type_id=settings.DEVICE_TYPES["ROBOT"])

        logger.info(f"In get_canister_drug_info, system_id:{system_id}")

        # adding packs which are in progress but yet not processed by robot.
        batch_id = get_progress_batch_id(system_id)
        if batch_id:
            filling_pending_pack_ids = get_filling_pending_pack_ids(company_id=company_id)

        logger.info(f"In get_canister_drug_info, filling_pending_pack_ids:{filling_pending_pack_ids}")

        canister_required_quantity = get_canister_drug_quantity_required_in_batch(canister_id_list=[canister_id],
                                                                                  filling_pending_pack_ids=filling_pending_pack_ids)

        logger.info(f"In get_canister_drug_info, canister_required_quantity: {canister_required_quantity}")

        canister_drug_info['batch_required_quantity'] = canister_required_quantity.get(int(canister_id), 0)

        if unit_drug_volume is not None:
            # find canister volume
            canister_usable_volume = get_canister_volume(canister_type=canister_drug_info["canister_type"])

            logger.info(f"In get_canister_drug_info, canister_usable_volume: {canister_usable_volume}")

            canister_drug_info["canister_capacity"] = get_max_possible_drug_quantities_in_canister(
                canister_volume=canister_usable_volume,
                unit_drug_volume=unit_drug_volume)
        else:
            canister_drug_info["canister_capacity"] = None
        if transfer_data_required :
            canister_data = get_canister_data_by_canister_ids([canister_id], None, None, None)
            if canister_data[0][0]["canister_type"] == constants.SMALL_CANISTER_CODE:
                drawer_type = [constants.SMALL_CANISTER_CODE, constants.BIG_CANISTER_CODE]
            else:
                drawer_type = [constants.BIG_CANISTER_CODE]
            transfer_data = get_canister_replenish_transfer_data_dao(canister_id, batch_id, company_id)
            empty_location_data = get_empty_location_by_quadrant(device_id=transfer_data['device_id'],
                                                                 quadrant=transfer_data['quadrant'], company_id=company_id, drawer_type = drawer_type,exclude_location = [])
            transfer_data['drawer_data'] = {
                "shelf": empty_location_data['shelf'],
                "display_location": empty_location_data["display_location"],
                "ip_address": empty_location_data['ip_address'],
                "secondary_ip_address": empty_location_data["secondary_ip_address"],
                "device_type_id": empty_location_data['device_type_id'],
                "device_serial_number": empty_location_data["device_serial_number"],
                "container_serial_number": empty_location_data["container_serial_number"]
            }
            canister_drug_info['transfer_data'] = transfer_data

        return create_response(canister_drug_info)

    except (InternalError, IntegrityError):
        return error(2001)
    except DoesNotExist:
        return error(1038, "or company_id.")


@log_args_and_response
def update_replenish_based_on_system(system_id, device_id = None):
    try:
        # device_data = DeviceMaster.db_get_robots_by_system_id(system_id,
        #                                                       [settings.ROBOT_SYSTEM_VERSIONS['v3']])
        device_data = get_robots_by_system_id_dao(system_id=system_id, version=[settings.ROBOT_SYSTEM_VERSIONS['v3']])
        logger.info('v3_device_found_for_system: ' + str(device_data))
        if device_data:

            # batch_data = BatchMaster.select(BatchMaster.id, BatchMaster.name).dicts().order_by(
            #     BatchMaster.id.desc()).where(
            #     BatchMaster.status == settings.BATCH_IMPORTED,
            #     BatchMaster.system_id == device_data[0]['system_id'])
            # batch_data = batch_data.get()
            # batch_data = db_get_last_imported_batch_by_system_dao(status=settings.BATCH_IMPORTED,
            #                                                       system_id=device_data[0]['system_id'])
            # logger.info("In_progress_batch_found_for_system: {}".format(system_id))
            # batch_id = batch_data['id']
            # batch_name = batch_data['name']

            pack_queue_packs = get_packs_from_pack_queue_for_system(system_id=system_id)
            if pack_queue_packs:
                logger.info('pack_queue_packs found')
                if device_id:
                    batch_dict = {
                        "device_id": device_id,
                        "system_id": system_id
                    }
                    get_replenish_mini_batch_wise(batch_dict)
                else:
                    for device in device_data:
                        batch_dict = {
                            "device_id": device['id'],
                            "system_id": device['system_id']
                        }
                        get_replenish_mini_batch_wise(batch_dict)
    except DoesNotExist as e:
        logger.info("No_in_progress_batch_found_for_system: {}".format(system_id))
        return True
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise e
    except ValueError as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e