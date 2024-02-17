import os
import sys
from calendar import monthrange
from peewee import IntegrityError, InternalError, DataError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate
from src.label_printing.drug_bottle_label import generate_drug_bottle_label
from src.label_printing.generate_label import remove_files
from src.cloud_storage import blob_exists, drug_bottle_label_dir, create_blob
from src.dao.inventory_dao import check_if_lot_number_is_recalled_dao, check_if_lot_number_exists_dao, \
    update_drug_bottle_quantity_for_lot_dao, insert_drug_lot_master_data_dao, check_if_serial_number_exists_dao, \
    insert_drug_bottle_data, get_lot_information_by_filters, update_drug_lot_information_dao, \
    get_drug_bottle_data_from_bottle_id_list, get_drug_bottle_data_from_lot_id, update_bottle_print_status_dao, \
    update_recall_status_for_lot_dao, update_recall_status_for_bottle_by_lot_id_dao, \
    update_drug_bottle_quantity_by_bottle_id_dao, get_lot_information_from_lot_id_dao, \
    get_drug_bottle_quantity_by_lot_id_dao, check_if_lot_has_unprinted_bottle_label_dao, \
    get_bottle_id_for_unprinted_label_by_lot_id_dao, delete_drug_bottle_dao, \
    get_drug_lot_information_from_lot_number_dao, insert_bottle_quantity_tracker_information_dao, \
    get_drug_image_and_id_from_ndc_dao, get_or_create_unique_drug, \
    query_to_get_used_canister, get_last_used_data_time_by_canister_id_list_dao
from src.dao.mfd_dao import get_drug_status_by_drug_id
from src.dao.drug_dao import get_drug_id_list_for_same_configuration_by_drug_id
from src.dao.volumetric_analysis_dao import get_drugs_for_required_configuration

logger = settings.logger


@validate(required_fields=["drug_id", "lot_number", "expiry_date", "total_packages", "created_by", "company_id",
                           "data_matrix_type", "total_quantity"])
@log_args_and_response
def insert_drug_lot_data(drug_lot_data):
    """
        This function will be used to insert drug lot data into the database when a new lot is registered for the company.
        @param drug_lot_data: Dictionary with required keys
        @return:
    """

    drug_lot_data["modified_by"] = drug_lot_data["created_by"]
    lot_data_dict = drug_lot_data.copy()
    del lot_data_dict["data_matrix_type"]
    del lot_data_dict["total_quantity"]
    drug_bottle_id_list: list = list()
    try:
        del lot_data_dict["serial_number_dict"]
    except Exception:
        pass

    try:
        is_recalled = check_if_lot_number_is_recalled_dao(lot_number=lot_data_dict["lot_number"])

        if is_recalled:
            return error(9009)

        status, response = check_if_lot_number_exists_dao(lot_number=lot_data_dict["lot_number"])
        logger.info("In insert_drug_lot_data: drug lot data: {}".format(drug_lot_data))
        with db.transaction():
            if status:
                result = update_drug_bottle_quantity_for_lot_dao(lot_id=response,
                                                                 quantity_to_update=lot_data_dict["total_packages"])
                logger.info("In insert_drug_lot_data: update drug bottle quantity in lot master: {}".format(result))
            else:
                response = insert_drug_lot_master_data_dao(drug_lot_data=lot_data_dict)
                logger.info("In insert_drug_lot_data: insert data in drug lot master table: {}".format(response))

            for i in range(0, int(drug_lot_data["total_packages"])):
                required_dict = {"drug_lot_master_id": response, "total_quantity": drug_lot_data["total_quantity"],
                                 "data_matrix_type": drug_lot_data["data_matrix_type"],
                                 "company_id": drug_lot_data["company_id"], "created_by": drug_lot_data["created_by"]}

                if int(drug_lot_data["data_matrix_type"]) == 0 and "serial_number_dict" in drug_lot_data:
                    required_dict["serial_number"] = drug_lot_data["serial_number_dict"][str(i + 1)]

                    serial_number_response = check_if_serial_number_exists_dao(serial_number=required_dict["serial_number"])

                    if serial_number_response:
                        return error(9010)

                response_id = insert_drug_bottle_data(required_dict, json_response=False)

                drug_bottle_id_list.append(response_id)

        response_dict_api = {"drug_lot_id": response, "bottle_id": drug_bottle_id_list}

        return create_response(response_dict_api)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in insert_drug_lot_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in insert_drug_lot_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in insert_drug_lot_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)


@log_args_and_response
@validate(required_fields=["company_id"])
def get_lot_information(lot_information_filters_dict):
    """
        This function will be used to ger information for various lots based on the filters provided by front end
        @param lot_information_filters_dict:Lot information filters
        @return:
    """
    drug_id, lot_number = None, None
    company_id = lot_information_filters_dict["company_id"]

    if "drug_id" in lot_information_filters_dict:
        drug_id = lot_information_filters_dict["drug_id"]

    if "lot_number" in lot_information_filters_dict:
        lot_number = lot_information_filters_dict["lot_number"]

    try:
        response = get_lot_information_by_filters(company_id=company_id, drug_id=drug_id, lot_number=lot_number)
        return create_response(response)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_lot_information {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_lot_information: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")

    except Exception as e:
        logger.error("Error in get_lot_information {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_lot_information: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_lot_information: " + str(e))


@log_args_and_response
@validate(required_fields=["lot_id", "lot_number", "expiry_date", "total_packages", "user_id"])
def update_drug_lot_data(update_drug_lot_data_args):
    """
    This function will be used to update the details of the lot for a given id
    @param update_drug_lot_data_args: Dictionary with required keys
    @return:
    """
    update_dict: dict = dict()
    try:
        lot_id = update_drug_lot_data_args["lot_id"]

        update_dict["lot_number"] = update_drug_lot_data_args["lot_number"]
        update_dict["expiry_date"] = update_drug_lot_data_args["expiry_date"]
        update_dict["total_packages"] = update_drug_lot_data_args["total_packages"]
        update_dict["modified_by"] = update_drug_lot_data_args["user_id"]

        response = update_drug_lot_information_dao(drug_lot_update_dict=update_dict, drug_lot_id=lot_id)
        return create_response(response)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_drug_lot_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_drug_lot_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")

    except Exception as e:
        logger.error("Error in update_drug_lot_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_drug_lot_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_drug_lot_data: " + str(e))


@log_args_and_response
@validate(required_fields=["lot_id", "company_id"])
def get_drug_bottle_label(drug_bottle_info):
    """
    Generates canister label if not present, returns file name
    @param drug_bottle_info:
    @return: json
    """
    files_to_delete: list = list()
    lot_id = drug_bottle_info["lot_id"]
    # company_id = drug_bottle_info["company_id"]

    if "bottle_id_list" in drug_bottle_info:
        bottle_id_list = drug_bottle_info["bottle_id_list"]
    else:
        bottle_id_list = []

    if bottle_id_list:
        bottle_id_list_str = [str(i) for i in bottle_id_list]
        # bottle_id_str = ",".join(bottle_id_list_str)
        label_name = "bottle_id_" + bottle_id_list_str[0] + ".pdf"
    else:
        label_name = "lot_id_" + str(lot_id) + ".pdf"

    logger.info("In get_drug_bottle_label: label_name: {}".format(label_name))
    if 'regenerate' not in drug_bottle_info:  # flag to regenerate label forcefully
        # If file already exists return
        if blob_exists(label_name, drug_bottle_label_dir):
            response = {'label_name': label_name}
            return create_response(response)

    if not os.path.exists(drug_bottle_label_dir):
        os.makedirs(drug_bottle_label_dir)
    # label_path = os.path.join(drug_bottle_label_dir, label_name)

    try:
        if bottle_id_list:
            drug_bottle_data_list = get_drug_bottle_data_from_bottle_id_list(
                bottle_id_list=bottle_id_list, is_deleted=False)
        else:
            drug_bottle_data_list = get_drug_bottle_data_from_lot_id(lot_id)
        logger.info("In get_drug_bottle_label: drug bottle data list : {}".format(drug_bottle_data_list))
    except (IntegrityError, InternalError) as e:
        logger.error("error in get_drug_bottle_label {}".format(e))
        return error(2001)

    if not drug_bottle_data_list:
        return error(9004)

    for drug_bottle_data in drug_bottle_data_list:
        expiry_list = drug_bottle_data["expiry_date"].split("-")
        days_in_month = monthrange(int(expiry_list[1]), int(expiry_list[0]))
        drug_bottle_data["expiry_date"] = expiry_list[1][2:] + expiry_list[0] + str(days_in_month[1])

    try:
        logger.info('In get_drug_bottle_label: Starting Drug Bottle Label Generation. Bottle ID: {}'.format(lot_id))
        label_path, files_to_delete = generate_drug_bottle_label(bottle_data_list=drug_bottle_data_list)

        logger.info('In get_drug_bottle_label: label path: {} and files to delete: {}'.format(label_path, files_to_delete))
        create_blob(label_path, label_name, drug_bottle_label_dir)  # Upload label to central storage

        if bottle_id_list:
            status = update_bottle_print_status_dao(bottle_id_list=bottle_id_list)
            logger.info('In get_drug_bottle_label: Drug Bottle print status updated {}'.format(status))

        response = {'label_name': label_name}

        return create_response(response)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_bottle_label {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_bottle_label: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")

    except Exception as e:
        logger.error("Error in get_drug_bottle_label {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_bottle_label: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_drug_bottle_label: " + str(e))
    finally:
        remove_files(files_to_delete)


@log_args_and_response
@validate(required_fields=["lot_id"])
def update_lot_recall_status(lot_dict):
    """
    This function will be used to inform that a certain lot id has been recalled and hence those bottles are no
    longer present in inventory
    :param lot_dict:
    :return:
    """
    lot_id = lot_dict["lot_id"]
    # resp = False

    with db.transaction():
        try:
            status = update_recall_status_for_lot_dao(lot_id=lot_id)
            logger.info("In update_lot_recall_status: recall status updated for lot: {}".format(status))
            resp = update_recall_status_for_bottle_by_lot_id_dao(lot_id=lot_id)
            return create_response(resp)

        except (InternalError, IntegrityError) as e:
            logger.error("error in update_lot_recall_status {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in update_lot_recall_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(2001)

        except Exception as e:
            logger.error("Error in update_lot_recall_status {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in update_lot_recall_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in update_lot_recall_status: " + str(e))


@log_args_and_response
@validate(required_fields=["bottle_id", "update_quantity"])
def update_pills_quantity_in_bottle_by_id(bottle_quantity_id_dict):
    """
    This function will be used to update the quantity in the drug bottle
    :param bottle_quantity_id_dict: Dictionary with required keys
    :return: True/False
    """
    try:
        bottle_id = int(bottle_quantity_id_dict["bottle_id"])
        quantity_updated = float(bottle_quantity_id_dict["update_quantity"])

        if quantity_updated < 0:
            quantity_updated = (-1 * quantity_updated)
            update_type = 1
        else:
            update_type = 2

        resp, status = update_drug_bottle_quantity_by_bottle_id_dao(bottle_id=bottle_id,
                                                                    quantity_to_update=quantity_updated,
                                                                    action=update_type)

        if not resp:
            return error(status)

        return create_response(resp)

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_pills_quantity_in_bottle_by_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_pills_quantity_in_bottle_by_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in update_pills_quantity_in_bottle_by_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_pills_quantity_in_bottle_by_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_pills_quantity_in_bottle_by_id: " + str(e))


@log_args_and_response
@validate(required_fields=["lot_number", "ndc"])
def check_details_for_lot_number_and_drug_existence(lot_data_dict):
    """
    This function is used as a quick search for given lot number. If lot exists, it will send information like
    drug lot information, if lot is recalled and number of unprinted bottles it had
    :param lot_data_dict:
    :return:
    """
    lot_number = lot_data_dict["lot_number"]
    ndc = lot_data_dict["ndc"]
    drug_id_list: list = list()

    try:
        if "serial_number" in lot_data_dict.keys():
            serial_number = lot_data_dict["serial_number"]
        else:
            serial_number = None

        is_image_available, drug_id = get_drug_image_and_id_from_ndc_dao(ndc=ndc)
        drug_id_list.append(drug_id)

        response_dict = {"lot_exist": False, "lot_data": dict(), "is_recall": False, "unprinted_bottle_count": 0,
                         "unprinted_bottle_id_list": list(), "serial_number_existence": False}

        if serial_number:
            serial_number_response = check_if_serial_number_exists_dao(serial_number=serial_number)
            response_dict["serial_number_existence"] = serial_number_response

        status, response = check_if_lot_number_exists_dao(lot_number=lot_number, drug_id_list=drug_id_list)

        if status:
            response_dict["lot_exist"] = True

            lot_data = get_lot_information_from_lot_id_dao(lot_id=response)
            bottle_quantity = get_drug_bottle_quantity_by_lot_id_dao(lot_id=response)
            response_dict["lot_data"] = lot_data
            response_dict["lot_data"]["total_quantity"] = bottle_quantity

            is_recalled = check_if_lot_number_is_recalled_dao(lot_number=lot_number)
            response_dict["is_recall"] = is_recalled

            bottle_count = check_if_lot_has_unprinted_bottle_label_dao(lot_id=response)
            response_dict["unprinted_bottle_count"] = bottle_count

            response = get_bottle_id_for_unprinted_label_by_lot_id_dao(lot_id=response)
            response_dict["unprinted_bottle_id_list"] = response

        return create_response(response_dict)

    except (InternalError, IntegrityError) as e:
        logger.error("error in check_details_for_lot_number_and_drug_existence {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in check_details_for_lot_number_and_drug_existence: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in check_details_for_lot_number_and_drug_existence {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in check_details_for_lot_number_and_drug_existence: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in check_details_for_lot_number_and_drug_existence: " + str(e))


@validate(required_fields=["bottle_id_list"])
def delete_drug_bottle(bottle_id_dict):
    """
    This function will be used to delete drug bottle, it will be soft delete with only a flag set as True
    :param bottle_id_dict: Dictionary with bottle id as list
    :return: True/False
    """
    bottle_id_list = bottle_id_dict["bottle_id_list"]

    try:
        with db.transaction():
            response = delete_drug_bottle_dao(bottle_id_list=bottle_id_list)
            if response:
                bottle_data = get_drug_bottle_data_from_bottle_id_list(bottle_id_list=bottle_id_list,
                                                                       data_matrix_type=-1)
                result = update_drug_bottle_quantity_for_lot_dao(lot_id=bottle_data[0]["drug_lot_id"],
                                                                 quantity_to_update=len(bottle_id_list),
                                                                 action_performed=2)
                logger.info("In delete_drug_bottle: update drug bottle quantity in lot master: {}".format(result))
        return create_response(response)


    except (InternalError, IntegrityError) as e:
        logger.error("error in delete_drug_bottle {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_drug_bottle: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in delete_drug_bottle {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_drug_bottle: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in delete_drug_bottle: " + str(e))


@validate(required_fields=["drug_id", "company_id"])
def find_similar_configuration_canister_by_drug_id(drug_data_dict):
    """
    This function will be used to get 2 lists of canisters by drug id
    1. Canisters which do not need new sticks but are of same stick configuration as given drug id
    2. Canister which are not used for a long time and can be used with new sticks.
    @param drug_data_dict:
    :return:
    """
    company_id = drug_data_dict["company_id"]
    db_result: list = list()
    canister_id_list: list = list()
    sanitization: list = list()
    new_sticks: list = list()
    try:

        # Getting drug information for given drug id
        drug_information = get_drug_status_by_drug_id(drug_id=drug_data_dict["drug_id"])

        # Based on the formatted ndc and txr trying to find the unique drug id on which dimension is available
        unique_drug = get_or_create_unique_drug(formatted_ndc=drug_information.formatted_ndc, txr=drug_information.txr)

        # Based on unique drug id trying to find all unique drug ids which are compatible based on dimension
        compatible_drug_id = get_drugs_for_required_configuration(unique_drug_id=unique_drug.id, use_database=True)

        if not compatible_drug_id:
            return create_response(db_result)

        # Getting drug ids of same fndc and txr for unique drug id list
        required_dict = {"drug_id_list": compatible_drug_id}
        same_config_drug_list = get_drug_id_list_for_same_configuration_by_drug_id(required_dict)

        query = query_to_get_used_canister(company_id=company_id, drug_id=drug_data_dict["drug_id"])
        for record in query:
            db_result.append(record)
            canister_id_list.append(record["canister_id"])

        logger.info("In find_similar_configuration_canister_by_drug_id: canister id list: {}".format(canister_id_list))
        # Getting a dictionary of drug id to last time their canister was used.
        last_used_dict = get_last_used_data_time_by_canister_id_list_dao(canister_id_list=canister_id_list)

        for record in db_result:
            record["last_used"] = last_used_dict[record["canister_id"]]

            if record["drug_id"] in same_config_drug_list:
                sanitization.append(record)
            else:
                new_sticks.append(record)

        response_dict = {"sanitization": sanitization, "new_sticks": new_sticks}

        return create_response(response_dict)

    except (InternalError, IntegrityError) as e:
        logger.error("error in find_similar_configuration_canister_by_drug_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in find_similar_configuration_canister_by_drug_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in find_similar_configuration_canister_by_drug_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in find_similar_configuration_canister_by_drug_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in find_similar_configuration_canister_by_drug_id: " + str(e))


@log_args_and_response
def insert_drug_bottle_pill_drop_data(quantity_adjusted, lot_number, created_by):
    """
    @param quantity_adjusted:
    @param lot_number:
    @param created_by:
    :return:
    """
    try:
        lot_drug_data = get_drug_lot_information_from_lot_number_dao(lot_number=lot_number)

        if lot_drug_data:
            required_dict = dict()
            required_dict["lot_id"] = lot_drug_data.id
            required_dict["quantity_adjusted"] = quantity_adjusted
            required_dict["action_performed"] = 1
            required_dict["created_by"] = created_by

            response = insert_bottle_quantity_tracker_information_dao(insert_dict=required_dict)
            logger.info("In insert_drug_bottle_pill_drop_data: {}".format(response))
            return True
        return False

    except (InternalError, IntegrityError) as e:
        logger.error("error in insert_drug_bottle_pill_drop_data {}".format(e))
        raise e

    except Exception as e:
        logger.error("Error in insert_drug_bottle_pill_drop_data {}".format(e))
        raise e
