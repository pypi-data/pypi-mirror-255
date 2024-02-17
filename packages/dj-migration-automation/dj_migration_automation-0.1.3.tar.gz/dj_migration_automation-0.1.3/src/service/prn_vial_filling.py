import json
import math
import re
from datetime import datetime, timedelta

import pandas as pd
from peewee import IntegrityError, InternalError, DataError, OperationalError, DoesNotExist

import settings
from com.pharmacy_software import send_data
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import get_current_date_time, get_current_date, convert_quantity, log_args_and_response, \
    convert_date_format, get_current_time_zone, get_current_day_date_end_date_by_timezone, get_date_time_by_offset
from dosepack.validation.validate import validate
from src import constants
from src.api_utility import get_filters, get_multi_search, get_orders
from src.dao.company_setting_dao import get_ips_communication_settings_dao
from src.dao.device_manager_dao import get_system_id_based_on_device_type
from src.dao.drug_dao import db_get_drug_data_by_ndc_parser_dao, get_drug_data_from_ndc, get_drug_id_from_ndc
from src.dao.drug_inventory_dao import db_create_record_in_adhoc_drug_request
from src.dao.ext_file_dao import get_files_by_name, add_file
from src.dao.misc_dao import get_company_setting_by_company_id
from src.dao.pack_dao import db_get_pack_display_ids, db_get_pack_and_display_ids, get_pack_grid_id_dao, \
    db_update_delivery_date_of_pack, sync_delivery_dates_with_ips
from src.dao.parser_dao import db_doctor_master_update_or_create, db_patient_rx_update_or_create_dao, PARSING_ERRORS, \
    db_partial_update_create_facility_master_dao
from src.dao.patient_dao import db_patient_master_update_or_create_dao
from src.dao.prn_vial_filling_dao import populate_facility_master, populate_doctor_master, populate_patient_master, \
    populate_patient_rx, generate_template_data_based_on_pack_type, populate_pack_header, populate_pack_details, \
    bulk_pack_ids_prn, populate_pack_rx_link, populate_slot_header, populate_slot_details, populate_pack_user_map, \
    db_get_last_prn_file, db_get_filled_rx_data, get_fields_dict_for_filled_rx, delete_pack_dao, update_queue_type_dao
from src.exc_thread import ExcThread
from src.exceptions import OtherDrugParsingException, DrugFetchFailedException, DuplicateFileException, \
    FileParsingException, PharmacySoftwareCommunicationException, PharmacySoftwareResponseException
from src.label_printing.print_label import add_label_count_request
from src.model.model_pack_details import PackDetails
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.service.drug import fetch_drug_data, drug_filled
from src.service.drug_inventory import post_drug_data_to_inventory
from src.service.misc import get_token, get_current_user, get_userid_by_ext_username
from src.service.pack import check_pharmacy_fill_id, update_packs_filled_by_in_ips, update_prn_fill_details_in_ips
from sync_drug_data.update_drug_data import get_missing_drug_data, get_missing_drug_images

logger = settings.logger


@log_args_and_response
@validate(required_fields=["rx_details", "patient_details", "doctor_details", "drug_details", "fill_details"])
def save_filled_rx(args):
    """
    format of arg for vial filling
                    {
            "rx_details": {
                "patient_pay": 4.29,
                "qty_per_day": 1,
                "bill_id": 2069760,
                "dispensing_pack_qty": 1,
                "last_tran_id": 0,
                "days_supply": 120,
                "bed": 0,
                "evening": 0,
                "noon": 0,
                "morning": 1,
                "remaining_refill": 0,
                "pharmacy_doctor_id": 14936,
                "schedule": 0,
                "qty": 120.5,
                "rx_tran_id": 599142,
                "queue_id": 1478456,
                "patient_id": 32635,
                "bottle_qty": 30,
                "drug_id": 17086,
                "fill_details": [],
                "insurance_name": "",
                "rx_status": "NEW",
                "doctor_dea": "BD1765556",
                "suggested_packing": "Bubble",
                "daw": "0",
                "bill_date": "2023-09-01",
                "on_order_datetime": "0001-01-01",
                "sig_code": "1t po am",
                "true_unit": "False",
                "customization": "False",
                "packing_type": "Multi",
                "separate_packperdose": "N",
                "stop_date": "2023-09-10",
                "in_hospital": "N",
                "is_verify": "Y",
                "start_date": "2023-09-01",
                "sig_english": "Take 1 tablet by mouth in the morning",
                "rx_filled_upto": "2023-08-31",
                "rx_expire_date": "2024-08-31",
                "prescribed_date": "2023-09-01",
                "taper_dose": "N",
                "med_type": "C",
                "rx_id": "590837",
                "last_billed_date": "2023-09-01",
                "tobe_delivered_datetime": "2023-09-01",
                "bill_id": 1234,
                "queue_id": 4321
            },
            "patient_details": {
                "underpaid_amt": 0,
                "facility_id": 6605,
                "patient_id": 32635,
                "patient_allergy": "",
                "patient_no": "14895686003",
                "workphone": "",
                "zip_code": "94605",
                "state": "CA",
                "city": "OAKLAND",
                "address1": "ASDFSFA",
                "patient_picture": "\\\\dosepacktest2\\IPS\\Patient_documents\\",
                "bdate": null,
                "facility_name": "FT9",
                "patient_name": "F, PA"
            },
            "doctor_details": {
                "pharmacy_doctor_id": 14936,
                "doctor_phone": "13344678801565",
                "doctor_name": "ABOUJAOUDA, JORGE"
            },
            "drug_details": {
                "total_req_qty": 120,
                "drug_schedule": 0,
                "drug_id": 17086,
                "txr": "390",
                "refrigerator_flag": "N",
                "caution2": "This drug may impair the ability to operate a vehicle, vessel (e.g., boat), or machinery. Use care until you become familiar with its effects.",
                "caution1": "May cause dizziness",
                "drug_imprint": "LUPIN <> 10",
                "drug_shape": "round",
                "drug_color": "pink",
                "strength_value": "10",
                "strength": "MG",
                "drug_form": "TABLET",
                "drug_name": "LISINOPRIL",
                "upc_code": "368180980032",
                "ndc": "68180098003",
                "drug_full_name": "LISINOPRIL 10 MG (68180098003)",
                "image_name": "LUP05140.JPG",
                "color": "pink",
                "shape": "round",
                "is_in_stock": 0,
                "lastSeenWith": 7,
                "imprint": "LUPIN <> 10",
                "image_url": "https://firebasestorage.googleapis.com/v0/b/dosepack-qa/o/drug_images%2FLUP05140.JPG?alt=media"
            },
            "user_id": 7,
            "ips_user_name": "jim",
            "pack_count": 1,
            "fill_details": [
                {
                    "case_id": "DPARS010",
                    "drug_scan_type": 273,
                    "expiry": "02-2024",
                    "lot_number": "11230",
                    "filled_ndc": "68180098003",
                    "filled_qty": 120.5,
                    "canister_id": null
                }
            ]
        }
    :return:
    """
    with db.transaction():
        try:
            user_id = args.get("user_id")
            fill_data = args.get("fill_details")
            ips_username = args.get("ips_user_name")
            pack_count = 0
            for record in list(args["pack_wise_qty"].values()):
                pack_count += len(record.keys())
            system_id = args.get("system_id", None)
            # vial capacity is added for future scope
            vial_capacity = args.get("vial_capacity", 100)
            is_ltc = args['rx_details'].get("is_ltc", 0)

            logger.debug("save_filled_rx: fetching token")
            token = get_token()
            if not token:
                logger.debug("save_filled_rx: token not found")
                return error(5018)
            logger.debug("save_filled_rx- Fetched token: " + str(token) + ", Now fetching user_details")
            current_user = get_current_user(token)
            logger.debug("save_filled_rx: user_info- {} for token - {}".format(current_user, token))
            if not current_user:
                logger.debug("save_filled_rx: no user found for token - {}".format(token))
                return error(5019)

            company_id = args["company_id"] = current_user["company_id"]
            # get the robot system_id from the given company_id as of now.

            # fetching patient details
            pharmacy_patient_id = args['patient_details']['patient_id']
            patient_name = args['patient_details']['patient_name']
            patient_address_1 = args['patient_details']['address1']
            patient_zip_code = args['patient_details']['zip_code']
            patient_city = args['patient_details']['city']
            patient_state = args['patient_details']['state']
            patient_workphone = args['patient_details']['workphone']
            patient_birthdate = args['patient_details'].get('bdate')
            patient_birth_date = convert_date_format(patient_birthdate) if patient_birthdate else None
            patient_allergy = args['patient_details']['patient_allergy']
            patient_no = args['patient_details'].get('patient_no')
            to_fill_hoa = [item['hoa_time'] for item in args['rx_details']['fill_details']]
            filled_hoa = []

            # fetching rx details
            pharmacy_rx_no = args['rx_details']['rx_id']
            sig = args['rx_details']['sig_english']
            morning = args['rx_details']['morning']
            noon = args['rx_details']['noon']
            evening = args['rx_details']['evening']
            bed = args['rx_details']['bed']
            remaining_refill = args['rx_details']['remaining_refill']
            is_tapered = args['rx_details']['taper_dose']
            daw_code = args['rx_details']['daw']
            queue_no = args['rx_details'].get('queue_no')
            queue_type = args['rx_details'].get('queue_type')
            delivery_date = args['rx_details']['tobe_delivered_datetime']
            bill_id = args['rx_details'].get('bill_id')
            queue_id = args['rx_details'].get('queue_id')
            delivery_date = args['rx_details']['tobe_delivered_datetime']
            prescribed_date = args['rx_details'].get('prescribed_date')
            last_pickup = args['rx_details'].get('last_pickup')
            next_pickup = args['rx_details'].get('next_pickup')

            # to fill qty is the qty required to fill received from IPS.
            # it is different from initial fill qty
            # e.g. -> Rx1 was asked to fill with 60 qty for first time then intial fill qty would be 60 but when same Rx
            # is partially filled to again received with lesser qty, say 40 then to_fill_qty would 40 for current Rx fill run
            to_fill_qty = args['rx_details']['qty']
            admin_duration = args['rx_details']['days_supply']
            last_billed_date = args['rx_details']['last_billed_date']
            delivery_route = args['rx_details'].get('delivery_route', None)
            delivery_route_id = args['rx_details'].get('route_id', None)
            filled_qty = 0
            pack_wise_qty = args.get("pack_wise_qty", {})

            # fill data is the data received which are actually filled using case or canister
            for record in fill_data:
                ndc = record['filled_ndc']
                filled_qty += record['filled_qty']
            total_quantity = filled_qty if (filled_qty < to_fill_qty) else to_fill_qty
            is_partial = True if filled_qty < to_fill_qty else False

            # finding if there are multiple hoas given in args
            fill_details = {}
            if args['rx_details']['fill_details']:
                for record in args['rx_details']['fill_details']:
                    fill_details[record['hoa_time']] = record['quantity'] * admin_duration
                calculated_to_fill_qty = sum(values for key, values in fill_details.items())

                if to_fill_qty > calculated_to_fill_qty:
                    logger.info(f"Qty Mismatch in to fill qty, extra quantity is: {to_fill_qty - calculated_to_fill_qty}")
                    for key, value in fill_details.items():
                        fill_details[key] += (to_fill_qty-calculated_to_fill_qty)
                        break
            fill_data.sort(key=lambda x: list(pack_wise_qty.keys()).index(x["filled_fndc"]))
            if filled_qty > to_fill_qty:
                return error(1000, " : Filled Qty is more than required Qty")

            # for PRN flow we don't receive admin dates we consider it as first for today and last at the end of day supply
            admin_start_date = get_current_date_time()
            admin_end_date = (datetime.strptime(admin_start_date, "%Y-%m-%d %H:%M:%S") + timedelta(
                days=(admin_duration - 1))).strftime(
                "%Y-%m-%d %H:%M:%S")
            filled_days = (datetime.strptime(admin_end_date, "%Y-%m-%d %H:%M:%S") - datetime.strptime(admin_start_date,
                                                                                                      "%Y-%m-%d %H:%M:%S")).days + 1

            # fetching drug details
            to_fill_ndc = args['drug_details'].get('ndc', None)
            if not ndc:
                ndc = to_fill_ndc
            txr = args['drug_details'].get('txr')
            upc = args['drug_details'].get('upc_code', None)
            packaging_type = constants.PACKAGING_TYPES[args['rx_details']['suggested_packing']]
            # default_pack_count = math.ceil(
            #     total_quantity / constants.PACK_WISE_AVAILABLE_QUANTITY.get(packaging_type, total_quantity))
            capacity = math.ceil(constants.PACK_WISE_AVAILABLE_QUANTITY[
                packaging_type] if packaging_type in [constants.PACKAGING_TYPE_BUBBLE_PACK,
                                                      constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4] else total_quantity)
            if pack_count:
                capacity = math.ceil(total_quantity / pack_count)

            pharmacy_facility_id = args['patient_details']['facility_id']
            facility_name = args['patient_details']['facility_name']
            pharmacy_doctor_id = args['doctor_details']['pharmacy_doctor_id']
            doctor_name = args['doctor_details']['doctor_name']
            doctor_phone = args['doctor_details']['doctor_phone']
            caution1 = args['drug_details']['caution1']
            caution2 = args['drug_details']['caution2']

            # setting file name based on previous last generated PRN file
            last_prn_record = db_get_last_prn_file(is_ltc=is_ltc)
            file_constant = constants.PRN_FILE_NAME_CONSTANT if is_ltc else constants.RETAIL_FILE_NAME_CONSTANT
            filename = f"{facility_name}_{file_constant}{last_prn_record+1}_{pharmacy_patient_id}.json"

            try:
                logger.debug("save_filled_rx: checking for existing files for the file_name: {} and company_id: {}"
                             .format(filename, company_id))
                files = get_files_by_name(filename, company_id)
                for file in files:
                    if file["status"] not in [settings.UNGENERATE_FILE_STATUS]:
                        logger.debug("save_filled_rx: existing file name- {}, status - {}"
                                     .format(file["filename"], file["status"]))
                        return error(5011, " Filename: {}, status: {}".format(file["filename"], file["status"]))
                logger.debug("save_filled_rx: New filename found: filename-{}".format(filename))
            except (InternalError, OperationalError, DataError, IntegrityError) as e:
                logger.error(e, exc_info=True)
                return error(5010, str(e))

            # persisting record for file in FileHeader
            file_record = add_file(filename=filename, company_id=company_id, user_id=user_id, manual_upload=False,
                                   file_status=settings.PROCESSED_FILE_STATUS, file_path=settings.PROCESSED_FILE_PATH, message="Success")

        except (InternalError, OperationalError, DataError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            return error(5014, str(e))
        except DuplicateFileException as e:
            logger.error(e, exc_info=True)
            return error(5011)
        except Exception as e:
            logger.error("Error in save_filled_rx: {}".format(e))
            return error(5017, str(e))

        try:
            drug_fill_data = []
            pack_ids = []
            # fetch drug id from db based on ndc if not available, fetch missing ndc's details from IPS
            # original_drug_id = 7565
            # drug_id = 7565
            original_drug_id = fetch_drug_data(company_id=company_id, user_id=user_id, file_id=file_record.id, upc=upc, ndc=to_fill_ndc, token=token)
            drug_id = fetch_drug_data(company_id=company_id, user_id=user_id, file_id=file_record.id, upc=upc, ndc=ndc, token=token)
            logger.debug("drug data insertion done")

            # persisting record in Facility Master
            logger.debug("Inserting records in facility master")
            facility_data = {"pharmacy_facility_id": pharmacy_facility_id,
                             "facility_name": facility_name,
                             "company_id": company_id,
                             "created_by": user_id,
                             "modified_by": user_id,
                             "created_date": get_current_date_time(),
                             "modified_date": get_current_date_time()}
            facility_record = populate_facility_master(pharmacy_facility_id, facility_data)
            if facility_record:
                logger.debug("Records inserted in facility master with ids: " + str(facility_record.id))
            else:
                return error(1040)

            logger.debug("Inserting records in doctor master")
            doctor_first_name = doctor_name.split(", ")[1]
            doctor_last_name = doctor_name.split(", ")[0]
            doctor_data = {"first_name": doctor_first_name,
                           "last_name": doctor_last_name,
                           "workphone": doctor_phone,
                           "company_id": company_id,
                           'created_by': user_id,
                           "modified_by": user_id,
                           "modified_date": get_current_date_time()}
            doctor_record = populate_doctor_master(pharmacy_doctor_id, doctor_data)
            if doctor_record:
                logger.debug("Records inserted in doctor master with ids: " + str(doctor_record.id))
            else:
                return error(1040)

            logger.debug("Inserting records in patient master")
            patient_first_name = patient_name.split(", ")[1]
            patient_last_name = patient_name.split(", ")[0]
            patient_data = {"first_name": patient_first_name,
                            "last_name": patient_last_name,
                            "workphone": patient_workphone,
                            "facility_id": facility_record.id,
                            "address1": patient_address_1,
                            "zip_code": patient_zip_code,
                            "city": patient_city,
                            "state": patient_state,
                            "company_id": company_id,
                            "dob": patient_birth_date,
                            "allergy": patient_allergy,
                            "patient_no": patient_no,
                            'created_by': user_id,
                            "modified_by": user_id,
                            "pharmacy_patient_id": pharmacy_patient_id,
                            "modified_date": get_current_date_time()}
            if delivery_route and delivery_route_id:
                patient_data["delivery_route_name"] = delivery_route
                patient_data["delivery_route_id"] = delivery_route_id
            patient_record = populate_patient_master(pharmacy_patient_id, patient_data)
            if patient_record:
                logger.debug("Records inserted in doctor master with ids: " + str(patient_record.id))
            else:
                return error(1040)

            logger.debug("Inserting records in patient rx")
            patient_rx_record = populate_patient_rx(patient_record.id, original_drug_id, doctor_record.id, morning,
                                                    noon, evening, bed, caution1, caution2, remaining_refill,
                                                    sig, pharmacy_rx_no, user_id, is_tapered, daw_code,
                                                    last_billed_date, to_fill_qty, prescribed_date, next_pickup, last_pickup)
            if patient_rx_record:
                logger.debug("Records inserted in patient_rx with ids: " + str(patient_rx_record))
            else:
                return error(1040)

            logger.debug("creating records for pack generation tables at pack level after bypassing template level")

            time_zone: str = get_current_time_zone()
            try:
                company_settings = get_company_setting_by_company_id(company_id=company_id)
                required_settings = settings.PACK_GENERATION_REQUIRED_SETTINGS
                settings_present = all([key in company_settings for key in required_settings])
                if not settings_present:
                    return error(6001)
            except InternalError:
                return error(2001)

            logger.debug("generate template data from which data can be persisted in tables")
            pack_display_ids = bulk_pack_ids_prn(pack_count, company_settings)
            # pack_display_ids = [1111, 2222, 3333, 4444, 5555, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            logger.debug("Inserting records in pack header")
            pack_header_dict = {'patient_id': patient_record.id, 'file_id': file_record.id,
                                'total_packs': pack_count, 'start_day': 0,
                                'pharmacy_fill_id': pack_display_ids[0], 'delivery_datetime': delivery_date,
                                'scheduled_delivery_date': delivery_date, 'created_by': user_id,
                                'modified_by': user_id}

            pack_header_record = populate_pack_header(pack_header_dict)

            if pack_header_record:
                logger.debug("Records inserted in pack_header with ids: " + str(pack_header_record.id))
            else:
                return error(1040)

            reversed_keys = list(fill_details.keys())[::-1]
            remaining_qty = to_fill_qty - filled_qty
            keys_to_remove = []
            if remaining_qty:
                for key in reversed_keys:
                    if remaining_qty <= 0:
                        break

                    qty_to_reduce = sum(fill_details.values()) - filled_qty

                    fill_details[key] -= qty_to_reduce
                    remaining_qty -= qty_to_reduce

                    if fill_details[key] <= 0:
                        keys_to_remove.append(key)

                for key in keys_to_remove:
                    del fill_details[key]
            pack_no = 0
            pack_send_data = {}
            ndc_qty_map = {}
            for fndc, packs in pack_wise_qty.items():
                for pack_index, pack_qty in packs.items():
                    pack_no += 1
                    fill_details = {key: value for key, value in fill_details.items() if value != 0}
                    slots_to_fill = {}
                    quantity = min(total_quantity, capacity) if packaging_type != constants.PACKAGING_TYPE_OTHER else total_quantity
                    if quantity == capacity:
                        total_quantity -= capacity
                    if pack_wise_qty:
                        quantity = pack_qty
                        capacity = quantity
                    logger.debug("Inserting records in pack details")
                    store_type = constants.STORE_TYPE_NON_CYCLIC if is_ltc else constants.STORE_TYPE_RETAIL
                    pack_details_dict = {'company_id': company_id,
                                         'pack_header_id': pack_header_record.id,
                                         'pack_display_id': pack_display_ids[pack_no - 1],
                                         'batch_id': None,
                                         'pack_no': pack_no,
                                         'consumption_start_date': admin_start_date,
                                         'consumption_end_date': admin_end_date,
                                         'filled_days': filled_days,
                                         'fill_start_date': admin_start_date,
                                         'pack_status': constants.PRN_DONE_STATUS,
                                         'delivery_schedule': "On Demand/PRN",
                                         'filled_date': get_current_date_time(),
                                         'created_by': user_id,
                                         'created_date': get_current_date_time(),
                                         'modified_by': user_id,
                                         'modified_date': get_current_date_time(),
                                         'filled_by': current_user["ips_user_name"],
                                         'store_type': store_type,
                                         'queue_type': queue_type,
                                         'queue_no': queue_no,
                                         'bill_id': bill_id,
                                         'packaging_type': packaging_type
                                         }
                    pack_details_record = populate_pack_details(pack_details_dict)
                    if pack_details_record:
                        logger.debug("Records inserted in pack_details with ids: " + str(pack_details_record.id))
                        pack_ids.append(pack_details_record.id)
                    else:
                        return error(1040)

                    logger.debug("Inserting records in pack_rx_link")
                    pack_rx_link_dict = {'patient_rx_id': patient_rx_record, 'pack_id': pack_details_record.id,
                                         'original_drug_id': drug_id}
                    pack_rx_link_record = populate_pack_rx_link(pack_rx_link_dict)
                    if pack_rx_link_record:
                        logger.debug("Records inserted in pack_rx_link with ids: " + str(pack_rx_link_record.id))
                    else:
                        return error(1040)

                    logger.debug("Inserting records in slot_header")
                    index = 0
                    if len(fill_details.keys()):
                        remaining_slots = min(args['rx_details']['qty'], capacity)
                        slot_index = 0
                        for key, value in fill_details.items():
                            total_rows = settings.PACK_ROW if (packaging_type != constants.PACKAGING_TYPE_BUBBLE_PACK) else (settings.PACK_ROW + 1)
                            slot_col = math.floor(slot_index/total_rows)
                            if slot_col > 0:
                                slot_row = slot_index - (slot_col * total_rows)
                            else:
                                slot_row = slot_index
                            pack_grid_id = get_pack_grid_id_dao(slot_row=slot_row, slot_column=slot_col)
                            slot_index += 1
                            if remaining_slots == 0:
                                continue
                            filled_hoa.append(key)
                            converted_time = f"{key[:2]}:{key[2:4]}:00"
                            slot_header_dict = {'pack_id': pack_details_record.id,
                                                'pack_grid_id': pack_grid_id,
                                                'hoa_time': converted_time}
                            slot_header_record = populate_slot_header(slot_header_dict)
                            index += 1
                            if slot_header_record:
                                logger.debug("Records inserted in slot_header with ids: " + str(slot_header_record.id))
                            else:
                                return error(1040)

                            qty = min([quantity] + [value, remaining_slots, quantity]) if pack_wise_qty else min([value, remaining_slots, quantity])
                            logger.debug("Inserting records in slot_details")
                            slot_details_dict = {'slot_id': slot_header_record.id,
                                                 'pack_rx_id': pack_rx_link_record.id,
                                                 'quantity': qty,
                                                 'is_manual': True,
                                                 'drug_id': drug_id,
                                                 'original_drug_id': original_drug_id}
                            if slot_details_dict['quantity'] == value:
                                remaining_slots -= value
                                fill_details[key] = 0
                            else:
                                fill_details[key] -= remaining_slots
                                remaining_slots = 0
                            slot_details_record = populate_slot_details(slot_details_dict)
                            if slot_details_record:
                                logger.debug(
                                    "Records inserted in slot_details with ids: " + str(slot_details_record.id))
                            else:
                                return error(1040)
                            slots_to_fill[pack_grid_id] = {ndc: slot_details_dict['quantity']}
                    else:
                        pack_grid_id = get_pack_grid_id_dao(slot_row=0, slot_column=0)
                        slot_header_dict = {'pack_id': pack_details_record.id,
                                            'pack_grid_id': pack_grid_id}
                        slot_header_record = populate_slot_header(slot_header_dict)
                        if slot_header_record:
                            logger.debug("Records inserted in slot_header with ids: " + str(slot_header_record.id))
                        else:
                            return error(1040)

                        logger.debug("Inserting records in slot_details")
                        slot_details_dict = {'slot_id': slot_header_record.id,
                                             'pack_rx_id': pack_rx_link_record.id,
                                             'quantity': quantity,
                                             'is_manual': True,
                                             'drug_id': drug_id,
                                             'original_drug_id': original_drug_id}
                        slot_details_record = populate_slot_details(slot_details_dict)
                        if slot_details_record:
                            logger.debug("Records inserted in slot_details with ids: " + str(slot_details_record.id))
                        else:
                            return error(1040)
                        slots_to_fill[pack_grid_id] = {ndc: slot_details_dict['quantity']}

                    logger.debug("Inserting records in pack_user_map")
                    pack_user_map_dict = {'pack_id': pack_details_record.id, 'assigned_to': user_id,
                                          'created_by': user_id, 'modified_by': user_id}
                    pack_user_map_record = populate_pack_user_map(pack_user_map_dict)
                    if pack_user_map_record:
                        logger.debug("Records inserted in pack_user_map with ids: " + str(pack_user_map_record.id))
                    else:
                        return error(1040)

                    remaining_qty = sum(sub_dict[key] for sub_dict in slots_to_fill.values() for key in sub_dict)
                    index = 0
                    min_date = datetime.strptime(fill_data[0]['expiry'], '%m-%Y')
                    check_fill_data = [record for record in fill_data if record["filled_fndc"] == fndc]
                    for item in check_fill_data:
                        if datetime.strptime(item['expiry'], '%m-%Y') <= min_date:
                            to_send_ndc = item["filled_ndc"]
                            to_send_expiry = item["expiry"]
                    filled_drug_id = get_drug_id_from_ndc(to_send_ndc, pharmacy_drug=True)[0]
                    pack_send_data[pack_details_record.id] = (filled_drug_id, to_send_expiry, to_send_ndc)
                    update_slots_to_fill = {}
                    for pack_grid_id, data in slots_to_fill.items():
                        slot_remaining_qty = data[ndc]
                        while remaining_qty != 0 and slot_remaining_qty != 0 and fill_data:
                            fill_record = fill_data[0]
                            index += 1
                            pack_slot_ndc_tuple = (pack_details_record.id, fill_record["filled_ndc"], pack_grid_id)
                            if fill_record["case_id"]:
                                add_string = fill_record["case_id"]
                            elif fill_record["canister_id"]:
                                add_string = str(fill_record["canister_id"])
                            else:
                                add_string = ""
                            if slot_remaining_qty < fill_record['filled_qty']:
                                to_fill_qty = slot_remaining_qty
                                if pack_slot_ndc_tuple not in ndc_qty_map:
                                    ndc_qty_map[pack_slot_ndc_tuple] = to_fill_qty
                                else:
                                    ndc_qty_map[pack_slot_ndc_tuple] += to_fill_qty
                                fill_record['filled_qty'] -= slot_remaining_qty
                                remaining_qty -= slot_remaining_qty
                                remaining_qty = math.floor(remaining_qty)
                                slot_remaining_qty = 0
                                update_slots_to_fill[pack_grid_id] = {
                                    fill_record['filled_ndc'] + "_" + add_string: ndc_qty_map[pack_slot_ndc_tuple]}
                            else:
                                to_fill_qty = fill_record['filled_qty']
                                if pack_slot_ndc_tuple not in ndc_qty_map:
                                    ndc_qty_map[pack_slot_ndc_tuple] = to_fill_qty
                                else:
                                    ndc_qty_map[pack_slot_ndc_tuple] += to_fill_qty
                                remaining_qty -= fill_record['filled_qty']
                                remaining_qty = math.floor(remaining_qty)
                                slot_remaining_qty -= fill_record['filled_qty']
                                fill_record = fill_data.pop(0)
                                update_slots_to_fill[pack_grid_id] = {
                                    fill_record['filled_ndc'] + "_" + add_string: ndc_qty_map[pack_slot_ndc_tuple]}
                            drug_fill_data.append({
                                'ndc': fill_record['filled_ndc'],
                                'txr': txr,
                                'fill_data': {
                                    str(pack_details_record.id): {
                                        'slots_to_filled': update_slots_to_fill,
                                        'overwrite_slots': {}}

                                },
                                'user_id': user_id,
                                'drug_type': None,
                                'expiry': fill_record['expiry'],
                                'lot_number': fill_record['lot_number'],
                                'case_id': fill_record['case_id'],
                                'system_id': system_id,
                                'canister_id': fill_record['canister_id'],
                                'recentScannedDrug': {},
                                'drug_scan_type': fill_record['drug_scan_type'],
                                'module_id': constants.PDT_PRN_FILL_WORKFLOW,
                                'company_id': company_id
                            })
                            update_slots_to_fill = {}
                    extra_hoa = [item for item in to_fill_hoa if item not in filled_hoa]
                    for hoa in extra_hoa:
                        total_rows = settings.PACK_ROW if (packaging_type != constants.PACKAGING_TYPE_BUBBLE_PACK) else (settings.PACK_ROW + 1)
                        slot_col = math.floor(slot_index/total_rows)
                        if slot_col > 0:
                            slot_row = slot_index - (slot_col * total_rows)
                        else:
                            slot_row = slot_index
                        pack_grid_id = get_pack_grid_id_dao(slot_row=slot_row, slot_column=slot_col)
                        slot_index += 1
                        converted_time = f"{hoa[:2]}:{hoa[2:4]}:00"
                        slot_header_dict = {'pack_id': pack_details_record.id,
                                            'pack_grid_id': pack_grid_id,
                                            'hoa_time': converted_time}
                        slot_header_record = populate_slot_header(slot_header_dict)
                        logger.debug("Inserting records in slot_details")
                        slot_details_dict = {'slot_id': slot_header_record.id,
                                             'pack_rx_id': pack_rx_link_record.id,
                                             'quantity': 0,
                                             'is_manual': True,
                                             'drug_id': drug_id,
                                             'original_drug_id': original_drug_id}
                        slot_details_record = populate_slot_details(slot_details_dict)
                        slots_to_fill[pack_grid_id] = {ndc: slot_details_dict['quantity']}

            ips_comm_settings = get_ips_communication_settings_dao(company_id=company_id)
            settings_present = all(key in ips_comm_settings for key in settings.IPS_COMMUNICATION_SETTINGS)
            try:
                status = update_prn_fill_details_in_ips(pharmacy_rx_no, ips_comm_settings, token, pack_ids,
                                                        pack_send_data, is_ltc, bill_id, queue_id, is_partial)
            except Exception as e:
                logger.error("error in get_filled_rx_data {}".format(e))
                return error(21020)
        except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
            logger.error("error in get_filled_rx_data {}".format(e))
            return error(21012)
        except Exception as e:
            logger.error("error in get_filled_rx_data {}".format(e))
            return error(21012)
        logger.info("records inserted on pack level, now inserting records for transaction")

    try:
        logger.debug("Inserting records in drug_tracker")
        for record in drug_fill_data:
            status = drug_filled(record)
        if settings_present:
            ips_pack_ids = db_get_pack_display_ids(pack_ids)
            pack_and_display_ids = db_get_pack_and_display_ids(pack_ids)
            try:
                update_packs_filled_by_in_ips(pack_ids=ips_pack_ids, ips_username=ips_username,
                                              pack_and_display_ids=pack_and_display_ids,
                                              ips_comm_settings=ips_comm_settings)
            except Exception as e:
                logger.error("error in get_filled_rx_data {}".format(e))
                return error(21021)
        else:
            logger.error(
                'In save_filled_rx, Required Settings not present to update filled by in Pharmacy Software.'
                ' company_id: {}'.format(company_id))
        if packaging_type == constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4:
            parameters = {'company_id': company_id, 'user_id': user_id, 'dry_run': 0, 'system_id': system_id, 'pack_ids': pack_ids,
                          'add_in_cdb_jobs': True, 'ips_username': ips_username}
            status = add_label_count_request(parameters)
        return create_response(settings.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_filled_rx_data {}".format(e))
        return error(21012)
    except Exception as e:
        logger.error("error in get_filled_rx_data {}".format(e))
        return error(21012)


@log_args_and_response
def get_filled_rx_data(paginate, filter_fields, sort_fields):
    """
    This functions gets the canister to be tested, received from odoo
    @return:
    """
    try:
        if "queue_type" in filter_fields:
            filter_fields["queue_type"] = [constants.QUEUE_TYPE_MAP[status] for status in filter_fields["queue_type"]]
        page_number = int(paginate.get("page_number"))
        number_of_rows = int(paginate.get("number_of_rows"))
        clauses = []
        order_list = []
        alt_clauses = []
        fields_dict, global_search_fields = get_fields_dict_for_filled_rx()
        if filter_fields and filter_fields.get('global_search', None):
            multi_search_string = [filter_fields['global_search']]
            clauses = get_multi_search(clauses, multi_search_string, global_search_fields)
        membership_search_list = ['patient_name', 'facility_name', 'facility_id', 'patient_id', 'route_id', 'schedule', 'queue_type']
        like_search_list = ['drug', 'rx_id', 'queue_no']
        left_like_search_fields = []

        if sort_fields:
            if any(item[0] == 'tobe_delivered_datetime' for item in sort_fields):
                if not any(item[0] == 'patient_name' for item in sort_fields):
                    sort_fields.append(['patient_name', 1])
            order_list = get_orders(order_list, fields_dict, sort_fields)

        if filter_fields:
            clauses = get_filters(clauses=clauses, fields_dict=fields_dict, filter_dict=filter_fields,
                                  membership_search_fields=membership_search_list,
                                  like_search_fields=like_search_list, left_like_search_fields=left_like_search_fields)
        if filter_fields.get("last_billed_date"):
            FromDate = filter_fields["last_billed_date"]["from"]
            ToDate = filter_fields["last_billed_date"]["to"]
            clauses.append(PatientRx.last_billed_date >= FromDate)
            alt_clauses.append(PatientRx.last_billed_date >= FromDate)
            clauses.append(PatientRx.last_billed_date <= ToDate)
            alt_clauses.append(PatientRx.last_billed_date <= ToDate)
        if filter_fields.get("retail_flag"):
            clauses.append(PackDetails.store_type == constants.STORE_TYPE_RETAIL)
            alt_clauses.append(PackDetails.store_type == constants.STORE_TYPE_RETAIL)
        else:
            clauses.append(PackDetails.store_type == constants.STORE_TYPE_NON_CYCLIC)
            alt_clauses.append(PackDetails.store_type == constants.STORE_TYPE_NON_CYCLIC)
        query1 = db_get_filled_rx_data(clauses=clauses, order_list=order_list, grouping=True)
        response = []
        patients = {}
        facilities = {}
        delivery_routes = {}
        total_patients = set()
        total_facilities = set()
        for record in query1:
            response.append({
                "qty": record["qty"],
                "facility_id": record["facility_id"],
                "patient_id": record["patient_id"],
                "rx_id": record["rx_id"],
                "upc_code": record["upc_code"],
                "ndc": record["ndc"],
                "drug": record["drug"],
                "facility_name": record["facility_name"],
                "patient_name": record["patient_name"],
                "tobe_delivered_datetime": record["delivery_datetime"],
                "last_billed_date": record["last_billed_date"],
                "pack_id": record["pack_id"],
                "pack_display_id": record["pack_display_id"],
                "packaging_type": constants.PACKAGING_TYPES_CODE[record["suggested_packing"]],
                "taper_dose": record["is_tapered"],
                "route_id": record["delivery_route_id"],
                "delivery_route": record["delivery_route_name"],
                "schedule": record["drug_schedule"],
                "pack_size": record["package_size"],
                "dispensing_pack_qty": record["dispense_qty"],
                "queue_type": record["queue_type"],
                "queue_no": record["queue_no"],
                "last_pickup": record["last_pickup_date"],
                "next_pickup": record["next_pickup_date"],
                "prescribed_date": record["prescribed_date"],
                "bill_id": record["bill_id"]
            })
            total_patients.add(record['patient_id'])
            total_facilities.add(record['facility_id'])
        response = [item for item in response if item["qty"] != 0.0]
        paginated_response = response[(page_number - 1) * number_of_rows: number_of_rows * page_number]
        query1 = db_get_filled_rx_data(clauses=alt_clauses, order_list=order_list, grouping=True)
        for record in query1:
            patients[record["patient_id"]] = record["patient_name"]
            facilities[record["facility_id"]] = record["facility_name"]
            if not record["delivery_route_id"] or not record["delivery_route_name"]:
                record["delivery_route_id"] = constants.NULL_ROUTE_NAME_ID
                record["delivery_route_name"] = constants.NULL_ROUTE_NAME
            delivery_routes[record["delivery_route_id"]] = record["delivery_route_name"]
        data = {"result": {"filled_rx_count": len(query1),
                           "response": paginated_response,
                           "patients": patients,
                           "patients_count": len(total_patients),
                           "facilities": facilities,
                           "facilities_count": len(total_facilities),
                           "drug_details": [],
                           "rx_count": len(response),
                           "delivery_routes_list": delivery_routes,
                           "drug_schedule_list": constants.drug_schedule_list}
                }
        return create_response(data)
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_filled_rx_data {}".format(e))
        return e
    except Exception as e:
        logger.error("error in get_filled_rx_data {}".format(e))
        return e


@log_args_and_response
def get_filled_rx_details_of_patient(patient_id, FromDate, ToDate):
    """
    This functions gets data of filled Rx of given patient
    @return:
    """
    try:
        rx_details = []
        patient_details = []
        patient_ids = []
        doctor_details = []
        doctor_ids = []
        drug_details = []
        drug_data = {}
        drug_hoa_map = {}
        clauses = [PatientMaster.pharmacy_patient_id == patient_id]
        if FromDate:
            clauses.append(PatientRx.last_billed_date >= FromDate)
        if ToDate:
            clauses.append(PatientRx.last_billed_date <= ToDate)
        query1 = db_get_filled_rx_data(clauses=clauses, grouping=False)
        for record in query1:
            rx_details.append({
                "qty": record["qty"],
                "sig_english": record["sig_english"],
                "tobe_delivered_datetime": record["delivery_datetime"],
                "drug_id": record["drug_id"],
                "patient_id": record["patient_id"],
                "pharmacy_doctor_id": record["pharmacy_doctor_id"],
                "suggested_packing": constants.PACKAGING_TYPES_CODE[record["suggested_packing"]],
                "rx_id": record["rx_id"],
                "is_filled": True,
                "last_billed_date": record["last_billed_date"],
                "taper_dose": record["is_tapered"],
                "bill_id": record["bill_id"],
                "pack_id": record["pack_id"],
                "pack_display_id": record["pack_display_id"],
                "fill_details": [],
                "schedule": record["drug_schedule"],
                "dispensing_pack_qty": record["dispense_qty"],
                "pack_size": record["package_size"],
                "queue_type": record["queue_type"],
                "queue_no": record["queue_no"]
            })
            if record['patient_id'] not in patient_ids:
                patient_details.append({
                    "patient_id": record["patient_id"],
                    "patient_name": record["patient_name"],
                    "facility_name": record["facility_name"],
                    "workphone": record["workphone"],
                    "bdate": record["dob"].strftime("%m/%d/%Y %H:%M:%S") if record["dob"] else None
                })
                patient_ids.append(record["patient_id"])
            if record["pharmacy_doctor_id"] not in doctor_ids:
                doctor_details.append({
                    "pharmacy_doctor_id": record["pharmacy_doctor_id"],
                    "doctor_phone": record["doctor_phone"],
                    "doctor_name": record["doctor_name"]
                })
                doctor_ids.append(record["pharmacy_doctor_id"])
            if record['drug_id'] not in drug_data:
                drug_data[record['drug_id']] = {
                    "total_req_qty": record["qty"],
                    "drug_id": record["drug_id"],
                    "txr": record["txr"],
                    "drug_imprint": record["drug_imprint"],
                    "drug_shape": record["drug_shape"],
                    "drug_color": record["drug_color"],
                    "strength_value": record["strength_value"],
                    "strength": record["strength"],
                    "drug_form": record["drug_form"],
                    "drug_name": record["drug_name"],
                    "upc_code": record["upc_code"],
                    "ndc": record["ndc"],
                    "caution1": record["caution1"],
                    "caution2": record["caution2"]
                }
                drug_hoa_map[record['drug_id']] = [record["hoa_time"]] if record["hoa_time"] else []
            else:
                drug_data[record['drug_id']]["total_req_qty"] += record["qty"]
                drug_hoa_map[record['drug_id']].append(record["hoa_time"]) if record["hoa_time"] and record["hoa_time"] not in drug_hoa_map[record['drug_id']] else []
        for record in rx_details:
            record["fill_details"] = [{"hoa_time": time.strftime("%H%M")} for time in drug_hoa_map.get(record["drug_id"], [])]

        for key, values in drug_data.items():
            drug_details.append(values)
        result = {
            "rx_details": rx_details,
            "patient_details": patient_details,
            "doctor_details": doctor_details,
            "drug_details": drug_details
        }
        data = {
            "result": result
        }
        return create_response(data)
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_filled_rx_details_of_patient {}".format(e))
    except Exception as e:
        logger.error("error in get_filled_rx_details_of_patient {}".format(e))


@log_args_and_response
@validate(required_fields=["order_data", "company_id", "time_zone"])
def send_drugs_to_elite(args):
    """
    This functions sends ndc data to Elite
    @return:
    """
    try:
        on_order_data = args.get("order_data", None)
        company_id = args.get("company_id", None)
        # time_zone = args.get("time_zone", 'US/Pacific')
        offset = args.get("time_zone", '-08:00')
        current_datetime = get_date_time_by_offset(offset)
        unique_id: str = str(company_id) + str(company_id) + "@@" + "".join(re.findall(r"\d+", current_datetime))
        department = constants.EPBM_VIBRANT_DEPARTMENT
        created_list = []
        updated_list = []
        deleted_list = []
        bypass_call = False
        # daw_qty_0 = 0
        # daw_qty_1 = 0
        for record in on_order_data:
            daw_qty_0 = 0
            daw_qty_1 = 0
            ndc = record["ndc"]
            for rx_record in record["rx_info"]:
                if int(rx_record["daw"]) == 0:
                    daw_qty_0 += rx_record["qty"]
                else:
                    daw_qty_1 += rx_record["qty"]
            if daw_qty_0:
                created_list.append({
                    "uniqueId": unique_id,
                    "ndc": int(ndc),
                    "quantity": daw_qty_0,
                    "daw": False,
                    "department": department,
                    "addToPreOrderList": True
                })
            if daw_qty_1:
                created_list.append({
                    "uniqueId": unique_id,
                    "ndc": int(ndc),
                    "quantity": daw_qty_1,
                    "daw": True,
                    "department": department,
                    "addToPreOrderList": True
                })
        inventory_response = post_drug_data_to_inventory(created_list=created_list,
                                                         updated_list=updated_list,
                                                         deleted_list=deleted_list,
                                                         bypass_call=bypass_call)
        inventory_response = 1
        # to store PRN data in adhoc drug req table
        # if inventory_response:
        #     insert_dict = []
        #     for record in created_list:
        #         drug_record = get_drug_data_from_ndc([str(record["ndc"]).zfill(11)])[0]
        #         insert_dict.append({"unique_id": record["uniqueId"],
        #                             "formatted_ndc": drug_record["formatted_ndc"],
        #                             "txr": drug_record["txr"],
        #                             "daw": record["daw"],
        #                             "ndc": record["ndc"],
        #                             "req_qty": float(record['quantity']),
        #                             "order_qty": int(record["quantity"]),
        #                             "department": record["department"],
        #                             "status_id": constants.DRUG_INVENTORY_MANAGEMENT_ADDED_ID
        #                             })
        #    status = db_create_record_in_adhoc_drug_request(insert_dict)
        return create_response(settings.SUCCESS_RESPONSE)
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in send_drugs_to_elite {}".format(e))
    except Exception as e:
        logger.error("error in send_drugs_to_elite {}".format(e))


@log_args_and_response
def get_suggested_pack_count(pack_type, qty, capacity=None, pack_count=None):
    """
    This function calculates pack count based on given qty and pack_type
    @return:
    """
    try:
        if pack_count:
            pack_count = eval(pack_count)
            qty = eval(qty)
            pack_type = None
        else:
            qty = eval(qty)
        if pack_type == constants.PACKAGING_TYPE_BLISTER_PACK_STRING:
            capacity = constants.PACK_WISE_AVAILABLE_QUANTITY[constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4]
        elif pack_type == constants.PACKAGING_TYPE_BUBBLE_PACK_STRING:
            capacity = constants.PACK_WISE_AVAILABLE_QUANTITY[constants.PACKAGING_TYPE_BUBBLE_PACK]
        else:
            capacity = qty
        if not pack_count:
            pack_count = max(math.ceil(qty/capacity), 1)
        base_qty = math.floor(math.ceil(qty)/pack_count)
        response = {}
        for i in range(pack_count - 1):
            response[i + 1] = base_qty
            qty -= base_qty
        response[pack_count] = qty
        data = {"pack_count": pack_count,
                "pack_wise_qty": response}
        return create_response(data)

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_suggested_pack_count {}".format(e))
    except Exception as e:
        logger.error("error in get_suggested_pack_count {}".format(e))


@log_args_and_response
@validate(required_fields=["fill_details", "company_id", "rx_id"])
def send_slot_wise_filled_rx_data_to_ips(args):
    try:
        fill_details = args.get("fill_details")
        company_id = args.get("company_id")
        rx_id = args.get("rx_id")
        bill_id = args.get("bill_id")
        token = get_token()
        ips_comm_settings = get_ips_communication_settings_dao(company_id=company_id)
        parameters = {"rx_id": rx_id,
                      "bill_id": bill_id,
                      "json_body": json.dumps(fill_details)
                      }

        send_data(base_url=ips_comm_settings['BASE_URL_IPS_WEB'].split("//")[1], webservice_url=settings.CURRENT_FILLED_RX_DETAILS,
                  parameters=parameters, counter=0, request_type="POST", token=token, ips_api=True)
        return create_response(settings.SUCCESS_RESPONSE)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in send_slot_wise_filled_rx_data_to_ips ", e, exc_info=True)
        raise
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error("error in send_slot_wise_filled_rx_data_to_ips ", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("error in send_slot_wise_filled_rx_data_to_ips is ", e, exc_info=True)
        raise


@log_args_and_response
@validate(required_fields=["pack_id"])
def delete_pack(args):
    try:
        pack_id_list = args.get("pack_id")
        pack_id_list = pack_id_list.split(",")
        pack_id_list = list(map(int, pack_id_list))
        status = delete_pack_dao(pack_id_list)
        return create_response(settings.SUCCESS_RESPONSE)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in delete_pack ", e, exc_info=True)
        raise
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error("error in delete_pack ", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("error in delete_pack is ", e, exc_info=True)
        raise


@log_args_and_response
def sync_queue_type(args):
    try:
        for record in args:
            ips_username = record["updated_by"]
            company_id = record["company_id"]
            user_info = get_userid_by_ext_username(ips_username, company_id)
            status = update_queue_type_dao(record["queue_no"], record["queue_type"], user_info["id"])
        return create_response(settings.SUCCESS_RESPONSE)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in sync_queue_type ", e, exc_info=True)
        raise
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error("error in sync_queue_type ", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("error in sync_queue_type is ", e, exc_info=True)
        raise


@log_args_and_response
def sync_delivery_date(args):
    try:
        with db.transaction():
            pack_ids = args.get("pack_ids")
            pack_display_ids = args.get("pack_display_ids")
            delivery_date = args.get("delivery_date")
            user_id = args.get("user_id")
            ips_username = args.get("ips_username")
            company_id = args.get("company_id")
            bill_id = args.get("bill_id")
            queue_id = args.get("queue_id")
            status = db_update_delivery_date_of_pack(pack_ids, user_id, delivery_date)
            status = sync_delivery_dates_with_ips(ips_user_name=ips_username, pack_display_ids=pack_display_ids,
                                                  company_id=company_id, queue_id=queue_id, bill_id=bill_id)
        return create_response(settings.SUCCESS_RESPONSE)

    except (IntegrityError, InternalError, DataError) as e:
        logger.error("error in sync_delivery_date ", e, exc_info=True)
        raise
    except (PharmacySoftwareCommunicationException, PharmacySoftwareResponseException) as e:
        logger.error("error in sync_delivery_date ", e, exc_info=True)
        raise
    except Exception as e:
        logger.error("error in sync_delivery_date is ", e, exc_info=True)
        raise
