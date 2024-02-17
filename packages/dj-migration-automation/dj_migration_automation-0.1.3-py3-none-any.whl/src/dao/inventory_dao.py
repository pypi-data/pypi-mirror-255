import functools
import operator
import settings
from peewee import InternalError, IntegrityError, DataError, DoesNotExist, fn
from dosepack.base_model.base_model import db, BaseModel
from dosepack.error_handling.error_handler import create_response
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate
from src.model.model_canister_master import CanisterMaster
from src.model.model_drug_bottle_master import DrugBottleMaster
from src.model.model_drug_bottle_quantity_tracker import DrugBottleQuantityTracker
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_location_master import LocationMaster
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_unique_drug import UniqueDrug
from dosepack.utilities.utils import get_current_date_time
logger = settings.logger


@log_args_and_response
def insert_drug_lot_master_data_dao(drug_lot_data: dict) -> int:
    """
     This method will be used to insert information for a lot that is being added into inventory
        :param drug_lot_data: Data dict we need to add for the lot
    """
    try:
        return DrugLotMaster.insert_drug_lot_master_data(drug_lot_data=drug_lot_data)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in insert_drug_lot_master_data_dao {}".format(e))
        raise e


@log_args_and_response
def update_drug_lot_information_dao(drug_lot_update_dict: dict, drug_lot_id: int) -> bool:
    """
     This method will be used to update the information about a given lot based on drug lot id
    """
    try:
        return DrugLotMaster.update_drug_lot_information(drug_lot_update_dict=drug_lot_update_dict, drug_lot_id=drug_lot_id)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_drug_lot_information_dao {}".format(e))
        raise e


@log_args_and_response
def get_drug_lot_master_data_dao(lot_number, drug_id, expiry_date):
    try:
        return DrugLotMaster.get_drug_lot_master_data(lot_number=lot_number,
                                                      drug_id=drug_id,
                                                      expiry_date=expiry_date)
    except Exception as e:
        logger.error("error in get_drug_lot_master_data_dao: {}".format(e))
        raise e

@log_args_and_response
def check_if_lot_number_exists_dao(lot_number: int, drug_id_list=-1):
    """
     This function will be used to check if given lot number exist or not, if it exists then we need to return
    """
    try:
        return DrugLotMaster.check_if_lot_number_exists(lot_number=lot_number, drug_id_list=drug_id_list)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_if_lot_number_exists_dao {}".format(e))
        raise e


@log_args_and_response
def check_if_lot_number_is_recalled_dao(lot_number: int) -> bool:
    """
     This function will return if given lot number is recalled or not
    """
    try:
        return DrugLotMaster.check_if_lot_number_is_recalled(lot_number=lot_number)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_if_lot_number_is_recalled_dao {}".format(e))
        raise e


@log_args_and_response
def update_drug_bottle_quantity_for_lot_dao(lot_id, quantity_to_update, action_performed=1) -> bool:
    """
     This function will be used to update the quantity of bottle in the lot based on the given data
    """
    try:
        return DrugLotMaster.update_drug_bottle_quantity_for_lot(lot_id=lot_id,
                                                                 quantity_to_update=quantity_to_update,
                                                                 action_performed=action_performed)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_drug_bottle_quantity_for_lot_dao {}".format(e))
        raise e


@log_args_and_response
def get_lot_information_by_filters(company_id, drug_id=None, drug_id_list=None, lot_number=None) -> list:
    """
        This method will be used to get information based given filters
        @param drug_id: Drug id will be present if we need to search by drug id
        @param company_id: Company id for which we need to get the data
        @param lot_number: Lot number will be present if we need to search by lot number
        @param drug_id_list:
    """
    db_result: list = list()
    clauses: list = list()

    clauses.append((DrugLotMaster.company_id == company_id))
    clauses.append(DrugLotMaster.is_recall == False)

    try:
        if drug_id:
            clauses.append((DrugLotMaster.drug_id == drug_id))

        if lot_number:
            clauses.append((DrugLotMaster.lot_number == lot_number))

        if drug_id_list:
            clauses.append((DrugLotMaster.drug_id.in_(drug_id_list)))

        query = DrugLotMaster.select(DrugMaster.ndc, DrugLotMaster)\
            .join(DrugMaster, on=(DrugMaster.id == DrugLotMaster.drug_id))

        query = query.where(functools.reduce(operator.and_, clauses))
        logger .info("In get_lot_information_by_filters: final_query :{}".format(query))
        for data in query.dicts():
            data["bottle_quantity"] = DrugBottleMaster.get_drug_bottle_quantity_by_lot_id(lot_id=data["id"])
            db_result.append(data)

        return db_result

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_lot_information_by_filters {}".format(e))
        raise e


@log_args_and_response
def get_drug_lot_information_from_lot_number_dao(lot_number):
    """
     This function will be used to get drug lot information from lot number
    """
    try:
        return DrugLotMaster.get_drug_lot_information_from_lot_number(lot_number=lot_number)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_lot_information_from_lot_number_dao {}".format(e))
        raise e


@log_args_and_response
def get_lot_information_from_lot_id_dao(response):
    """
     This function will be used to get drug lot information from lot number
    """
    try:
        return DrugLotMaster.get_lot_information_from_lot_id(lot_id=response)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_lot_information_from_lot_number_dao {}".format(e))
        raise e


@log_args_and_response
def update_recall_status_for_lot_dao(lot_id) -> bool:
    """
     This function will be used to update recall status for lot id
    """
    try:
        return DrugLotMaster.update_recall_status_for_lot(lot_id=lot_id)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_recall_status_for_lot_dao {}".format(e))
        raise e


@validate(required_fields=["drug_lot_master_id", "total_quantity",
                           "data_matrix_type", "company_id", "created_by"])
@log_args_and_response
def insert_drug_bottle_data(drug_bottle_data_dict, json_response=True):
    """
    This function will be used to insert drug bottle data into the database so that we can keep track of all bottles
    in our inventory
    @param drug_bottle_data_dict:  Dictionary of the data which we need to insert
    @param json_response:
    """

    drug_bottle_data_dict["modified_by"] = drug_bottle_data_dict["created_by"]
    drug_bottle_data_dict["available_quantity"] = drug_bottle_data_dict["total_quantity"]
    # response_id = -1
    try:
        with db.transaction():
            response_id = DrugBottleMaster.db_insert_drug_bottle_data(drug_bottle_data=drug_bottle_data_dict)
            logger.info("In insert_drug_bottle_data: record inserted in drug bottle master table: {}".format(response_id))
            if "serial_number" not in drug_bottle_data_dict:
                temp_serial_number = "#DP" + str(response_id).zfill(17)
                update_dict = {"serial_number": temp_serial_number}
                status = DrugBottleMaster.update_drug_bottle_information(drug_bottle_update_dict=update_dict,
                                                                         drug_bottle_id=response_id)
                logger.info("In insert_drug_bottle_data: drug bottle information updated: {}".format(status))
        if json_response:
            return create_response(response_id)
        else:
            return response_id

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in insert_drug_bottle_data {}".format(e))
        raise e


@log_args_and_response
def get_drug_bottle_data_by_filter(company_id, lot_number=None, drug_id=None, drug_id_list=None,
                                   is_recall=None) -> list:
    """
        This function will be used to get data about drug bottle in system based on the filters given
        @param company_id: Company id for which we need to find the data
        @param lot_number: If search by lot number filter is required, this value will be present
        @param drug_id: If search by drug id filter is required, this value will be present
        @param is_recall: If we need to search for recalled bottle, then this will be present
        @param drug_id_list:
        :return: Data/Error

    """
    db_result: list = list()
    clauses: list = list()

    try:
        clauses.append((DrugBottleMaster.available_quantity > 0))
        clauses.append((DrugBottleMaster.company_id == company_id))

        if lot_number:
            clauses.append((DrugBottleMaster.drug_lot_master_id == lot_number))

        if drug_id:
            clauses.append(DrugLotMaster.drug_id == drug_id)

        if is_recall:
            clauses.append((DrugBottleMaster.drug_id == is_recall))
        else:
            clauses.append((DrugBottleMaster.is_deleted == False))

        if drug_id_list:
            clauses.append((DrugLotMaster.drug_id.in_(drug_id_list)))

        query = DrugBottleMaster.select(DrugBottleMaster, DrugLotMaster.lot_number,
                                        DrugLotMaster.expiry_date, DrugMaster.ndc). \
            join(DrugLotMaster, on=(DrugLotMaster.id == DrugBottleMaster.drug_lot_master_id))\
            .join(DrugMaster, on=(DrugLotMaster.drug_id == DrugMaster.id))\
            .where(functools.reduce(operator.and_, clauses))

        for data in query.dicts():
            db_result.append(data)
        return db_result

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_bottle_data_by_filter {}".format(e))
        raise e


@log_args_and_response
def get_drug_bottle_data_from_lot_id(lot_id: int) -> list:
    """
        This function will be used to get information about the drug bottle based on the drug bottle lot id
        :param lot_id: Lot id for which we need information
        :return: Data for drug
    """
    db_result: list = list()
    try:
        query = DrugBottleMaster.select(DrugBottleMaster.serial_number,
                                        DrugLotMaster.lot_number,
                                        DrugLotMaster.expiry_date,
                                        DrugMaster.ndc, DrugBottleMaster.id).dicts() \
            .join(DrugLotMaster, on=DrugLotMaster.id == DrugBottleMaster.drug_lot_master_id) \
            .join(DrugMaster, on=DrugMaster.id == DrugLotMaster.drug_id) \
            .where((DrugBottleMaster.drug_lot_master_id == lot_id) & (DrugBottleMaster.data_matrix_type == 1) &
                   (DrugBottleMaster.is_deleted == False))
        for record in query:
            db_result.append(record)
        return db_result

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_bottle_data_from_lot_id {}".format(e))
        raise e


@log_args_and_response
def get_drug_bottle_data_from_bottle_id_list(bottle_id_list, data_matrix_type=1, is_deleted=None) -> list:
    """
        This function will be used to get information about drug bottle based on the bottle id.
        Extra filters can be applied based on the requirement
        :param bottle_id_list: Bottle id list
        :param data_matrix_type: Type of data matrix requested, if -1 filter is not applied
        :param is_deleted: To check if is deleted bottles are required or not.
        :return: List of data
    """
    db_result: list = list()
    clauses: list = list()
    try:

        clauses.append((DrugBottleMaster.id.in_(bottle_id_list)))
        if data_matrix_type != -1:
            clauses.append((DrugBottleMaster.data_matrix_type == data_matrix_type))
        if is_deleted is not None:
            clauses.append((DrugBottleMaster.is_deleted == is_deleted))

        query = DrugBottleMaster.select(DrugBottleMaster.serial_number,
                                        DrugLotMaster.lot_number,
                                        DrugLotMaster.expiry_date,
                                        DrugMaster.ndc, DrugBottleMaster.id,
                                        DrugLotMaster.id.alias("drug_lot_id")).dicts()\
            .join(DrugLotMaster, on=DrugLotMaster.id == DrugBottleMaster.drug_lot_master_id)\
            .join(DrugMaster, on=DrugMaster.id == DrugLotMaster.drug_id)\
            .where(functools.reduce(operator.and_, clauses))

        for record in query:
            db_result.append(record)

        return db_result

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_bottle_data_from_bottle_id_list {}".format(e))
        raise e


@log_args_and_response
def update_drug_bottle_quantity_by_bottle_id_dao(bottle_id: int, quantity_to_update: float, action=1):
    """
     This function will be used to update drug bottle quantity by drug bottle
    """
    try:
        return DrugBottleMaster.update_drug_bottle_quantity_by_bottle_id(bottle_id=bottle_id,
                                                                         quantity_to_update=quantity_to_update,
                                                                         action=action)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_drug_bottle_quantity_by_bottle_id_dao {}".format(e))
        raise e


@log_args_and_response
def get_drug_bottle_quantity_by_lot_id_dao(lot_id) -> int:
    """
     This function will be used to get the quantity of drug bottle  by lot id
    """
    try:
        return DrugBottleMaster.get_drug_bottle_quantity_by_lot_id(lot_id=lot_id)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_bottle_quantity_by_lot_id_dao {}".format(e))
        raise e


@log_args_and_response
def get_drug_bottle_count_by_drug_and_company_id(company_id: int, drug_id_list: list) -> dict:
    """
    @param company_id:
    @param drug_id_list:
    :return:
    """
    lot_id_dict: dict = dict()
    drug_count_dict: dict = dict()
    try:
        for drug_id in drug_id_list:
            lot_id_list = DrugLotMaster.get_lot_id_list_from_drug_id(drug_id=drug_id)
            lot_id_dict[drug_id] = lot_id_list
        logger.info("In get_drug_bottle_count_by_drug_and_company_id: location id dict: {}".format(lot_id_dict))
        for drug in lot_id_dict.keys():
            if lot_id_dict[drug]:
                bottle_count = DrugBottleMaster.db_get_drug_bottle_count_by_drug_and_company_id(company_id=company_id, drug_lot_master_id_list=lot_id_dict[drug])
            else:
                bottle_count = 0

            drug_count_dict[drug] = bottle_count
        return drug_count_dict

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_bottle_count_by_drug_and_company_id {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_drug_bottle_count_by_drug_and_company_id {}".format(e))
        raise e


@log_args_and_response
def update_recall_status_for_bottle_by_lot_id_dao(lot_id) -> bool:
    """
     This function will be used to update recall status for bottle by lot id
    """
    try:
        return DrugBottleMaster.update_recall_status_for_bottle_by_lot_id(lot_id=lot_id)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_recall_status_for_bottle_by_lot_id_dao {}".format(e))
        raise e


@log_args_and_response
def check_if_lot_has_unprinted_bottle_label_dao(lot_id) -> int:
    """
     This function will be used to check if given lot id has bottles which have unprinted data matrix
    """
    try:
        return DrugBottleMaster.check_if_lot_has_unprinted_bottle_label(lot_id=lot_id)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_if_lot_has_unprinted_bottle_label_dao {}".format(e))
        raise e


@log_args_and_response
def get_bottle_id_for_unprinted_label_by_lot_id_dao(lot_id) -> list:
    """
     This function will be used  to get list of id of bottles whose label is not printed for the given lot id
    """
    try:
        return DrugBottleMaster.get_bottle_id_for_unprinted_label_by_lot_id(lot_id=lot_id)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_bottle_id_for_unprinted_label_by_lot_id_dao {}".format(e))
        raise e


@log_args_and_response
def delete_drug_bottle_dao(bottle_id_list: list) -> bool:
    """
     This function will be used to delete drug bottle because it is of no use
    """
    try:
        return DrugBottleMaster.delete_drug_bottle(bottle_id_list=bottle_id_list)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in delete_drug_bottle_dao {}".format(e))
        raise e


@log_args_and_response
def update_bottle_print_status_dao(bottle_id_list: list) -> bool:
    """
     This function will be used to update print status of drug bottle
    """
    try:
        return DrugBottleMaster.update_bottle_print_status(bottle_id_list=bottle_id_list)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_bottle_print_status_dao {}".format(e))
        raise e


@log_args_and_response
def check_if_serial_number_exists_dao(serial_number) -> bool:
    """
     This function will be used to check if serial number is exits in drug bottle master table
    """
    try:
        return DrugBottleMaster.check_if_serial_number_exists(serial_number=serial_number)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_if_serial_number_exists_dao {}".format(e))
        raise e


@log_args_and_response
def insert_bottle_quantity_tracker_information_dao(insert_dict: dict) -> bool:
    """
     This function will be used to insert drug quantity tracker information
    """
    try:
        return DrugBottleQuantityTracker.insert_bottle_quantity_tracker_information(tracker_data=insert_dict)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in insert_bottle_quantity_tracker_information_dao {}".format(e))
        raise e


@log_args_and_response
def get_drug_image_and_id_from_ndc_dao(ndc: str) -> bool:
    """
    get drug image and name from ndc
    """
    try:
        return DrugMaster.get_drug_image_and_id_from_ndc(ndc=ndc)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_drug_image_and_id_from_ndc_dao {}".format(e))
        raise e


@log_args_and_response
def get_or_create_unique_drug(formatted_ndc, txr, drug_id=None):
    """
        Returns `UniqueDrug` for given formatted ndc, txr combination
        :param formatted_ndc:
        :param txr:
        :param drug_id:
        :return:
    """
    try:
        clauses = list()
        clauses.append((UniqueDrug.formatted_ndc == formatted_ndc))
        if txr is None:
            clauses.append((UniqueDrug.txr.is_null(True)))
        else:
            clauses.append((UniqueDrug.txr == txr))
        return UniqueDrug.select().where(functools.reduce(operator.and_, clauses)).get()
    except DoesNotExist:
        if not drug_id:
            clauses = list()
            clauses.append((DrugMaster.formatted_ndc == formatted_ndc))
            if txr is None:
                clauses.append((DrugMaster.txr.is_null(True)))
            else:
                clauses.append((DrugMaster.txr == txr))
            drug = DrugMaster.select().where(functools.reduce(operator.and_, clauses)).get()
            drug_id = drug.id
        unique_drug = UniqueDrug.create(**{
            'formatted_ndc': formatted_ndc,
            'txr': txr,
            'drug_id': drug_id
        })
        return unique_drug


@log_args_and_response
def query_to_get_used_canister(drug_id, company_id):
    """
       query to get used canister
    """
    sub_query_canister_id_list: list = list()
    try:
        sub_query = SlotTransaction.db_get_distinct_canister_from_slot_transaction()
        # Subquery to find list of canister id which are used in given time frame
        for record in sub_query:
            sub_query_canister_id_list.append(record["canister_id"])
        logger.info("In query_to_get_used_canister: canister id list: {}".format(sub_query_canister_id_list))

        # From canister master taking canister which are of same dimension but not used in given time frame.
        query = CanisterMaster.select(LocationMaster.location_number,
                                      CanisterMaster.rfid,
                                      CanisterMaster.available_quantity,
                                      fn.IF(CanisterMaster.available_quantity < 0, 0,
                                            CanisterMaster.available_quantity).alias('display_quantity'),
                                      DrugMaster.drug_name,
                                      DrugMaster.ndc,
                                      CanisterMaster.id.alias("canister_id"),
                                      DrugMaster.id.alias("drug_id")
                                      ).dicts() \
            .join(DrugMaster, on=(DrugMaster.id == CanisterMaster.drug_id)) \
            .join(LocationMaster, on=LocationMaster.id == CanisterMaster.location_id) \
            .where((CanisterMaster.id.not_in(sub_query_canister_id_list)) & (
                    CanisterMaster.active == settings.is_canister_active)
                   & (CanisterMaster.company_id == company_id) & (CanisterMaster.drug_id != drug_id))

        return query
    except (DoesNotExist, IntegrityError, InternalError, DataError) as e:
        logger.error("error in query_to_get_used_canister {}".format(e))
        raise e


@log_args_and_response
def get_last_used_data_time_by_canister_id_list_dao(canister_id_list: list) -> dict:
    """
    get last used date and time by canister id list
    """
    try:
        return SlotTransaction.get_last_used_data_time_by_canister_id_list(canister_id_list=canister_id_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_last_used_data_time_by_canister_id_list_dao {}".format(e))
        raise e

@log_args_and_response
def crud_process_for_drug_lot_master(args):
    """
    this function is used for do all the process on drug_lot_master for 11_digit_ndc_slot_wise flow
    """
    logger.info("In crud_process_for_drug_lot_master")
    try:
        drug_id = args["drug_id"]
        lot_number = args["lot_number"]
        created_by = args["created_by"]
        company_id = args["company_id"]
        modified_by = args["modified_by"]
        expiry_date = args["expiry_date"]
        required_quantity = args["required_quantity"]

        drug_lot_data = {
            "drug_id": drug_id,
            "total_packages": 0,
            "total_quantity": 0,
            "available_quantity": 0,
            "lot_number": lot_number,
            "company_id": company_id,
            "created_by": created_by,
            "modified_by": modified_by,
            "expiry_date": expiry_date
        }

        try:
            status = DrugLotMaster.get_or_create(lot_number=lot_number,
                                                 drug_id=drug_id,
                                                 expiry_date=expiry_date,
                                                 defaults=drug_lot_data
                                                 )
        except Exception as e:
            raise e

        drug_lot_master_data = get_drug_lot_master_data_dao(lot_number, drug_id, expiry_date)

        available_quantity = drug_lot_master_data.available_quantity
        available_quantity -= required_quantity

        drug_lot_master_update_dict = {"modified_by": modified_by,
                                       "available_quantity": available_quantity,
                                       "modified_date": get_current_date_time()
                                       }

        update_status = update_drug_lot_information_dao(drug_lot_master_update_dict,
                                                        drug_lot_master_data.id
                                                        )

        return drug_lot_master_data.id
    except Exception as e:
        logger.error("error in crud_process_for_drug_lot_master: {}".format(e))
        raise e


@log_args_and_response
def update_or_create_drug_lot_master(drug_lot_master_data,case_id_present):
    try:
        expiry_date = drug_lot_master_data["expiry_date"]
        drug_lot_master_data["total_packages"] = 0
        drug_lot_master_data["total_quantity"] = 0
        drug_lot_master_data["available_quantity"] = 0
        case_id = drug_lot_master_data['case_id']
        drug_id = drug_lot_master_data["drug_id"]
        lot_number = drug_lot_master_data["lot_number"]
        created_by = drug_lot_master_data["created_by"]
        company_id = drug_lot_master_data["company_id"]
        modified_by = drug_lot_master_data["modified_by"]
        expiry_date = drug_lot_master_data["expiry_date"]
        available_quantity = 0


        update_data = {"expiry_date": expiry_date}
        if not case_id_present:
            if case_id:

                drug_lot_master_id = DrugLotMaster.insert(**drug_lot_master_data).execute()
                logger.info("entry created for case_id in drug_lot_master ")

            else:
                drug_lot_data = {
                    "drug_id": drug_id,
                    "total_packages": 0,
                    "total_quantity": 0,
                    "available_quantity": 0,
                    "lot_number": lot_number,
                    "company_id": company_id,
                    "created_by": created_by,
                    "modified_by": modified_by,
                    "expiry_date": expiry_date
                }

                drug_lot_master_data, status = DrugLotMaster.get_or_create(lot_number=lot_number,
                                                                           drug_id=drug_id,
                                                                           expiry_date=expiry_date,
                                                                           defaults=drug_lot_data
                                                                           )
                drug_lot_master_id = drug_lot_master_data.id
                available_quantity = drug_lot_master_data.available_quantity

        else:
            case_id = drug_lot_master_data.pop("case_id")
            drug_lot_master_data = DrugLotMaster.select(DrugLotMaster.id,
                                                        DrugLotMaster.available_quantity).where(
                DrugLotMaster.case_id == case_id).get()
            drug_lot_master_id = drug_lot_master_data.id
            available_quantity = drug_lot_master_data.available_quantity
            status = DrugLotMaster.update(**update_data).where(DrugLotMaster.case_id == case_id).execute()
            logger.info("entry updated for case_id in drug_lot_master ")

        return drug_lot_master_id,available_quantity
    except Exception as e:
        logger.error("error in update_or_create_drug_lot_master: {}".format(e))
        raise e