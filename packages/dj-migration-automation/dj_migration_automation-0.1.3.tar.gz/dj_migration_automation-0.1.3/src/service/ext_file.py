import json
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, List

from peewee import OperationalError
import settings
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import convert_quantity_reverse, log_args_and_response, call_webservice
from dosepack.validation.validate import validate
from pymysql import InternalError, DataError, IntegrityError
from src import constants
from src.cloud_storage import save_and_upload_file_to_cloud, download_blob, rx_file_blob_dir
from src.dao.device_manager_dao import get_system_id_based_on_device_type
from src.dao.ext_file_dao import get_files_by_name, add_file, update_couch_db_pending_template_count, \
    insert_ext_hold_rx_data_dao
from src.dao.ext_change_rx_dao import db_get_linked_packs
from src.dao.ext_file_dao import get_files_by_name, add_file
from src.exceptions import DuplicateFileException
from src.service.misc import get_token, get_userid_by_ext_username, get_current_user
from src.service.parser import Parser

logger = settings.logger


@log_args_and_response
def validate_prescription(prescription: dict, change_rx: Optional[bool] = False) -> str:
    """
    Validate prescription data
    @param prescription:
    @param change_rx:
    @return:
    """
    missing_keys = set()
    empty_fields = set()
    qty_mismatch = set()
    validation_error_message = ""
    rx_details_key: str = "rx_details"
    rx_status: int = constants.EXTCHANGERXACTIONS_ADD

    try:
        logger.debug("in validate_prescription")

        if not change_rx:
            # check patient info fields
            for key in constants.REQUIRED_PATIENT_INFO_KEYS:
                if key not in prescription.keys():
                    missing_keys.add(key)
                else:
                    # check for empty values, comparing with None and empty string to allow 0 as a value in
                    # field like daw_code
                    if key in constants.REQUIRED_PATIENT_INFO_VALUES and \
                            (prescription[key] is None or prescription[key] == ''):
                        empty_fields.add(key)

        logger.debug("validate_prescription: patient info verified")

        if change_rx:
            rx_details_key = "rx_change_details"

        # check for rx details
        if rx_details_key in prescription.keys():
            for rx in prescription[rx_details_key]:
                logger.debug("validate_prescription: verifying rx info")

                if change_rx:
                    rx_status = rx["status"]

                rx_total_qty = 0
                hoa_wise_total_qty = 0

                for rx_key in constants.REQUIRED_RX_KEYS:
                    if rx_key not in rx.keys():
                        missing_keys.add(rx_key)
                    else:
                        if rx_key in constants.REQUIRED_RX_VALUES and (rx[rx_key] is None or rx[rx_key] == ''):
                            if (not change_rx) or (change_rx and rx_status != constants.EXTCHANGERXACTIONS_DELETE):
                                empty_fields.add(rx_key)
                    rx_total_qty = rx.get("total_qty", 0)

                # check for fill details
                if "fill_details" in rx.keys():
                    for fill_data in rx["fill_details"]:
                        for fill_key in constants.REQUIRED_FILL_DETAILS_KEYS:
                            if fill_key not in fill_data.keys():
                                missing_keys.add(fill_key)
                            else:
                                if fill_key in constants.REQUIRED_FILL_DETAILS_VALUES and \
                                        (fill_data[fill_key] is None or fill_data[fill_key] == ''):
                                    empty_fields.add(fill_key)
                        qty_list = fill_data.get("quantity", [])
                        hoa_wise_total_qty += sum(map(float, qty_list))

                if rx_total_qty != hoa_wise_total_qty:
                    qty_mismatch.add(rx["pharmacy_rx_no"])

        logger.debug("validate_prescription: missing fields - {}, empty_fields - {}".format(list(missing_keys),
                                                                                            list(empty_fields)))

        if missing_keys:
            validation_error_message = "Missing Keys(s): {}".format(list(missing_keys))
        if empty_fields:
            if validation_error_message:
                validation_error_message += " and Missing Value(s) for Key(s): {}".format(list(empty_fields))
            else:
                validation_error_message = "Missing Value(s) for Key(s): {}".format(list(empty_fields))
        if qty_mismatch:
            if validation_error_message:
                validation_error_message += " and quantity mismatch for pharmacy rx no.: {}".format(list(qty_mismatch))
            else:
                validation_error_message = "Qty mismatch for pharmacy rx no.: {}".format(list(qty_mismatch))
        return validation_error_message
    except Exception as e:
        raise e


@log_args_and_response
def format_prescription_dict(data: dict, change_rx: Optional[bool] = False, template_master_data=None ):
    """
    Method to format prescription dict to create data frame same as old format
    @param data:
    @param change_rx
    @return:
    """
    try:
        stop_data: bool = False
        logger.debug("In format_prescription_dict")
        data_list = list()
        hold_rx_dict = dict()

        data.pop("company_id", None)
        rx_status: int = constants.EXTCHANGERXACTIONS_ADD

        if not change_rx:
            file_name = data.pop("file_name")
            data.pop("ips_username", None)
            fill_start_date = datetime.strptime(data["fill_start_date"], "%Y%m%d").date()
            fill_end_date = datetime.strptime(data["fill_end_date"], "%Y%m%d").date()
        else:
            file_name = "NA"
            data.pop("pack_display_id", None)

        if not change_rx:
            rx_details = data.pop("rx_details")
        else:
            rx_details = data.pop("rx_change_details")

        for rx in rx_details:
            # fetch fill_details
            logger.info("current Rx to fill {}".format(rx))
            to_fill = rx.get("to_fill", True)
            if not to_fill:
                # rx is on hold so just add data in ext_hold_rx table
                hold_rx_dict[rx["pharmacy_rx_no"]] = rx.get("fill_note", "")
                continue

            rx.pop("total_qty", None)
            rx["morning"] = round(convert_quantity_reverse(float(rx["morning"]), is_total_quantity=False))
            rx["noon"] = round(convert_quantity_reverse(float(rx["noon"]), is_total_quantity=False))
            rx["evening"] = round(convert_quantity_reverse(float(rx["evening"]), is_total_quantity=False))
            rx["bed"] = round(convert_quantity_reverse(float(rx["bed"]), is_total_quantity=False))
            rx["remaining_refill"] = round(convert_quantity_reverse(float(rx["remaining_refill"]),
                                                                    is_total_quantity=False))
            rx["is_tapered"] = 'Y' if rx["is_tapered"] else 'N'

            if change_rx:
                rx_status = rx["status"]
                fill_start_date = datetime.strptime(rx["start_date"], "%Y%m%d").date()
                fill_end_date = datetime.strptime(rx["end_date"], "%Y%m%d").date()
                rx.pop("start_date", None)
                rx.pop("end_date", None)
                rx["fill_start_date"] = fill_start_date.strftime('%Y%m%d')
                rx["fill_end_date"] = fill_end_date.strftime('%Y%m%d')
                rx["filled_by"] = rx["rx_change_user_name"]
                for template in template_master_data:
                    if template['fill_start_date'].strftime("%Y%m%d") != fill_start_date or template[
                        'fill_end_date'].strftime("%Y%m%d") != fill_end_date:
                        stop_data = True

            fill_details = rx.pop("fill_details")
            if (not change_rx) or (change_rx and rx_status != constants.EXTCHANGERXACTIONS_DELETE):
                for fill in fill_details:
                    quantity_list = fill["quantity"]
                    hoa_date = fill_start_date
                    for qty in quantity_list:
                        # check for hoa_date: it must be between fill_start_date and fill_end_date including both
                        if hoa_date > fill_end_date:
                            logger.debug(
                                "format_prescription_dict: hoa_date > fill_end_date for file- {}".format(file_name))
                            break
                        if float(qty):
                            quantity = round(convert_quantity_reverse(float(qty), is_total_quantity=True))
                            hoa_dict = {"hoa_time": fill["hoa_time"], "hoa_date": hoa_date.strftime('%Y%m%d'),
                                        "quantity": quantity}
                            hoa_time_rx_level_dict = {**data, **rx, **hoa_dict}
                            data_list.append(hoa_time_rx_level_dict)
                        hoa_date = hoa_date + timedelta(days=1)
            else:
                rx["pharmacy_doctor_id"] = 1
                rx["doctor_name"] = "NA"
                rx["delivery_schedule"] = "NA"
                rx["drug_name"] = "NA"
                rx["ndc"] = "00000000000"
                hoa_date = datetime.strptime("19000101", "%Y%m%d").date()
                hoa_dict = {"hoa_time": "0000", "hoa_date": hoa_date.strftime('%Y%m%d'),
                            "quantity": round(convert_quantity_reverse(float(1), is_total_quantity=True))}
                hoa_time_rx_level_dict = {**data, **rx, **hoa_dict}
                data_list.append(hoa_time_rx_level_dict)

            logger.debug("format_prescription_dict: formatted till rx-{}".format(rx["pharmacy_rx_no"]))
        logger.debug("format_prescription_dict: Formatting done file: {} with length {}"
                     .format(file_name, len(data_list)))

        return data_list, stop_data, hold_rx_dict

    except Exception as e:
        logger.error("format_prescription_dict: Error while formatting prescription - " + str(e))
        raise e


@log_args_and_response
@validate(required_fields=["error_code", "error_desc", "data"])
def process_rx(file_args):
    """
    Method to process patient prescription
    @param file_args:
    @return:
    """
    logger.debug("In process_rx")
    error_code = file_args.get("error_code")
    error_desc = file_args.get("error_desc")
    args = file_args.get("data")

    autoprocess_template: int = 0

    filename = args.get("file_name")
    file_record = None
    if not filename:
        logger.debug("process_rx: missing file_name")
        return error(5012, "Missing Parameter: file_name")

    try:
        # fetch company_id based on token
        logger.debug("process_rx: fetching token")
        token = get_token()
        if not token:
            logger.debug("process_rx: token not found")
            return error(5018)
        logger.debug("process_rx- Fetched token: " + str(token) + ", Now fetching user_details")
        current_user = get_current_user(token)
        logger.debug("process_rx: user_info- {} for token - {}".format(current_user, token))
        if not current_user:
            logger.debug("process_rx: no user found for token - {}".format(token))
            return error(5019)
        company_id = args["company_id"] = current_user["company_id"]

        # check file exists or not if no error code available or error code other than 5015
        if error_code and error_code == constants.ERROR_CODE_CONNECTION_ISSUE_AFTER_FILE_SAVED:
            logger.debug("process_rx: API re-triggered for file: {}, with error_desc: {}."
                         " So no need to existing file of same name".format(filename, error_desc))
        else:
            try:
                logger.debug("process_rx: checking for existing files for the file_name: {} and company_id: {}"
                             .format(filename, company_id))
                files = get_files_by_name(filename, company_id)
                for file in files:
                    if file["status"] not in [settings.UNGENERATE_FILE_STATUS]:
                        logger.debug("process_rx: existing file name- {}, status - {}"
                                     .format(file["filename"], file["status"]))
                        return error(5011, " Filename: {}, status: {}".format(file["filename"], file["status"]))
                logger.debug("process_rx: New filename found: filename-{}".format(filename))
            except (InternalError, OperationalError, DataError, IntegrityError) as e:
                logger.error(e, exc_info=True)
                return error(5010, str(e))

        # validate file with required keys and values
        validation_error_message = validate_prescription(args)

        if validation_error_message:
            send_file_validation_failure_email(file_name=filename, error_message=validation_error_message,
                                               company_id=company_id, current_user=current_user.get("id"),
                                               patient_name=args.get("patient_name", "Missing"),
                                               facility_name=args.get("facility_name", "Missing"))
            logger.error("process_rx: error found while validating prescription data format - {}"
                         .format(validation_error_message))
            validation_error_message = validation_error_message.replace("'", "")
            return error(5012, validation_error_message)
        logger.debug("process_rx: prescription validated.")

        # upload file to cloud
        if error_code and error_code in [constants.ERROR_CODE_CONNECTION_ISSUE_AFTER_FILE_SAVED,
                                        constants.ERROR_CODE_CONNECTION_ISSUE_WHILE_FILE_SAVING]:
            logger.debug("process_rx: API re-triggered for file: {}, with error_desc: {}. "
                         "So need to upload file to cloud".format(filename, error_desc))
        else:
            logger.debug("process_rx: saving and uploading file to cloud")
            try:
                save_and_upload_file_to_cloud(args)
            except Exception as e:
                logger.error("Error while uploading file to cloud - {}".format(e))
                return error(5013)
            logger.debug("process_rx: file uploaded in cloud")
            # logger.debug("process_rx: SKIP Google Cloud Process")

        # fetch userid based on ips_username
        ips_user_name = args["ips_username"]
        logger.debug("process_rx: fetching user_id based on ips_username: {}".format(args["ips_username"]))
        user_info = get_userid_by_ext_username(args["ips_username"], company_id)
        if user_info and "id" in user_info:
            logger.info("userinfo: {} for ips_username: {}".format(user_info, args["ips_username"]))
            user_id = user_info["id"]
        else:
            logger.error("Error while fetching user_info for ips_user_name {}".format(args["ips_username"]))
            user_id = current_user["id"]

        # adding extension in filename
        filename += ".json"

        if error_code and error_code == constants.ERROR_CODE_CONNECTION_ISSUE_AFTER_FILE_SAVED:
            logger.debug("process_rx: API triggered for file: {}, with error_desc: {}. So instead of saving file, "
                         "fetching recent file data with same name".format(filename, error_desc))
            files_with_same_name = get_files_by_name(filename, company_id)
            if not files_with_same_name:
                return error(5012, "Invalid file_name or company_id or error_code")
            file_record = files_with_same_name[0]
            logger.debug("process_rx: fetched file_record: {}".format(file_record))
        else:
            file_record = add_file(filename=filename, company_id=company_id, user_id=user_id, manual_upload=False)
            logger.debug("process_rx: saved file_record: {}".format(file_record))
    except (InternalError, OperationalError, DataError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(5014, str(e))
    except DuplicateFileException as e:
        logger.error(e, exc_info=True)
        return error(5011)
    except Exception as e:
        logger.error("Error in process_rx: {}".format(e))
        return error(5017, str(e))

    # flow after saving prescription
    try:
        # get the robot system_id from the given company_id as of now.
        system_id = get_system_id_based_on_device_type(company_id=company_id,
                                                       device_type_id=settings.DEVICE_TYPES["ROBOT"])

        daycare_program = args.pop("daycare_program", 0)
        if not daycare_program:
            autoprocess_template = 1
        logger.debug("Auto-Process Template: {}".format(autoprocess_template))

        logger.debug("process_rx: Fetch the Old Pharmacy Fill ID information...")
        pharmacy_patient_id = args["pharmacy_patient_id"]
        fill_start_date = datetime.strptime(args["fill_start_date"], "%Y%m%d").date()
        fill_end_date = datetime.strptime(args["fill_end_date"], "%Y%m%d").date()
        old_pharmacy_fill_id: List[int] = db_get_linked_packs(pharmacy_patient_id, company_id, fill_start_date,
                                                              fill_end_date)

        logger.debug("process_rx: formatting prescription data")
        # format the data dict to create same data frame as per old format
        data, stop_data, hold_rx_dict = format_prescription_dict(data=args)
        logger.debug("process_rx: prescription data formatted")

        # process the file
        logger.debug("process_rx: Initiating Parser")
        process_pharmacy_file = Parser(user_id=user_id, filename=filename, company_id=company_id,
                                       system_id=system_id, from_dict=True, data=data, upload_file_to_gcs=False)
        logger.debug("process_rx: parser initiated")

        # Need this type check as we used existing methods to save the data as well as to fetch the data, and
        # we have different type of response found in both the methods dict and object
        if isinstance(file_record, dict):
            process_pharmacy_file.file_id = file_record["id"]
        else:
            process_pharmacy_file.file_id = file_record.id

        if hold_rx_dict:
            status = insert_ext_hold_rx_data_dao(hold_rx_dict, process_pharmacy_file.file_id)

        if old_pharmacy_fill_id:
            logger.debug("process_rx: Change Rx and Call for New JSON")
            process_pharmacy_file.old_pharmacy_fill_id = old_pharmacy_fill_id

        if autoprocess_template:
            process_pharmacy_file.autoprocess_template = autoprocess_template
        process_pharmacy_file.ips_user_name = ips_user_name
        process_pharmacy_file.token = token

        logger.debug("process_rx: Parser initiated, now calling start_processing")
        response = process_pharmacy_file.start_processing(update_prescription_v1=True)
        logger.debug("process_rx: start_processing done with response - {}".format(response))

        parsed_response = json.loads(response)
        if parsed_response["status"] == settings.FAILURE_RESPONSE:
            return error(5016, parsed_response["description"])

        if not autoprocess_template:
            update_couch_db_pending_template_count(company_id=company_id)

        return response
    except (InternalError, OperationalError) as e:
        logger.error(e, exc_info=True)
        return error(5015, str(e))
    except (DataError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(5016, str(e))
    except Exception as e:
        logger.error("Error in process_rx: {}".format(e))
        return error(5017, str(e))


@log_args_and_response
@validate(required_fields=["company_id", "user_id", "filename"])
def process_existing_rx(request_args):
    """
    Method to process patient prescription
    @param request_args:
    @return:
    """
    logger.debug("process_existing_rx")
    try:
        file_name = request_args["filename"]
        company_id = request_args["company_id"]
        user_id = request_args["user_id"]
        file_id = request_args["file_id"]

        file_dir = os.path.join(settings.PENDING_FILE_PATH, str(company_id))
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_path = os.path.join(file_dir, file_name)
        logger.debug("process_existing_rx: downloading file - {}".format(file_name))
        with open(file_path, 'wb') as writefile:
            download_blob('{}/{}'.format(company_id, file_name), writefile, rx_file_blob_dir)
        writefile.close()
        logger.debug("process_existing_rx: downloaded file- {}".format(file_name))

        # fetch data from file
        rx_file = open(file_path)
        args = json.load(rx_file)

        # get the robot system_id from the given company_id as of now.
        logger.debug("process_existing_rx: fetching system_id ")
        system_id = get_system_id_based_on_device_type(company_id=company_id,
                                                       device_type_id=settings.DEVICE_TYPES["ROBOT"])

        # format the data dict to create same data frame as per old format
        data, stop_data, hold_rx_dict = format_prescription_dict(data=args)
        logger.debug("process_existing_rx: data formatted for file - {}".format(file_name))

        # process the file
        logger.debug("process_existing_rx: Parser init")
        process_pharmacy_file = Parser(user_id=user_id, filename=file_name, company_id=company_id,
                                       system_id=system_id, from_dict=True, data=data, upload_file_to_gcs=False)
        logger.debug("process_existing_rx: Parser initiated")
        process_pharmacy_file.file_id = file_id

        if hold_rx_dict:
            status = insert_ext_hold_rx_data_dao(hold_rx_dict, file_id)

        logger.debug("process_existing_rx: start_processing")
        response = process_pharmacy_file.start_processing(update_prescription_v1=True)
        logger.debug("process_existing_rx: end file processing")
        return response
    except (InternalError, DataError, IntegrityError) as ex:
        logger.error(ex, exc_info=True)
        return error(2001, str(ex))
    except Exception as e:
        logger.error("Error in process_existing_rx: {}".format(e))
        return error(5017, str(e))


@log_args_and_response
def send_file_validation_failure_email(file_name, error_message, company_id, current_user, patient_name, facility_name):
    """
    This function sends email suggesting all the canisters in given lot have been tested
    @return:
    """
    try:
        logger.info("In, send_file_validation_failure_email")
        status, data = call_webservice(settings.BASE_URL_AUTH, settings.FILE_VALIDATION_FAILURE_EMAIL,
                                       parameters={"file_name": file_name, "error_message": error_message,
                                                   "company_id": company_id, "user_id": current_user,
                                                   "patient_name": patient_name, "facility_name": facility_name},
                                       use_ssl=settings.AUTH_SSL)
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in send_file_validation_failure_email {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in send_file_validation_failure_email: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1040)
    except Exception as e:
        logger.error("error in send_file_validation_failure_email {}".format(e))
