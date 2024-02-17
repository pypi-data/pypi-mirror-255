import functools
import operator
from typing import Optional, List

from peewee import IntegrityError, InternalError, DataError, DoesNotExist, fn

import settings
from com.pharmacy_software import send_data
from dosepack.utilities.utils import log_args_and_response, logger, get_current_date_time
from src import constants
from src.dao.parser_dao import PARSING_ERRORS
from src.exceptions import FileParsingException, PharmacySoftwareResponseException, \
    PharmacySoftwareCommunicationException
from src.model.model_doctor_master import DoctorMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_tracker import DrugTracker
from src.model.model_facility_master import FacilityMaster
from src.model.model_file_header import FileHeader
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_status_tracker import PackStatusTracker
from src.model.model_pack_user_map import PackUserMap
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.service.misc import get_token, get_current_user


@log_args_and_response
def db_get_filled_rx_data(clauses, order_list=None, grouping=True):
    """ to fetch filled on demand Rx records from db"""
    try:
        clauses.append(PackDetails.pack_status == constants.PRN_DONE_STATUS)
        query1 = PackDetails.select((fn.SUM(DrugTracker.drug_quantity)).alias("qty"),
                                    FacilityMaster.pharmacy_facility_id.alias("facility_id"),
                                    FacilityMaster.facility_name, PatientRx.pharmacy_rx_no.alias("rx_id"),
                                    DrugMaster.id.alias("drug_id"), DrugMaster.upc.alias("upc_code"), DrugMaster.ndc,
                                    fn.CONCAT(DrugMaster.drug_name, " ", DrugMaster.strength_value, " ",
                                              DrugMaster.strength).alias("drug"),
                                    fn.CONCAT(PatientMaster.last_name, ", ", PatientMaster.first_name).alias(
                                        "patient_name"), DrugMaster.txr, PatientRx.caution1, PatientRx.caution2,
                                    DrugMaster.imprint.alias("drug_imprint"), DrugMaster.drug_form,
                                    DrugMaster.shape.alias("drug_shape"),
                                    DrugMaster.color.alias("drug_color"), DrugMaster.strength,
                                    DrugMaster.strength_value,
                                    PatientMaster.pharmacy_patient_id.alias("patient_id"), PackHeader.delivery_datetime,
                                    PatientRx.last_billed_date, PatientRx.sig.alias("sig_english"),
                                    PatientMaster.workphone, PatientMaster.dob,
                                    fn.CONCAT(DoctorMaster.first_name, ", ", DoctorMaster.last_name).alias(
                                        "doctor_name"), DoctorMaster.workphone.alias("doctor_phone"),
                                    DrugMaster.drug_name, PackDetails.packaging_type.alias("suggested_packing"),
                                    DoctorMaster.pharmacy_doctor_id, PackDetails.pack_display_id,
                                    PackDetails.id.alias("pack_id"), PatientRx.is_tapered, SlotHeader.hoa_time,
                                    PatientMaster.delivery_route_name, PatientMaster.delivery_route_id,
                                    DrugMaster.drug_schedule, DrugMaster.package_size, DrugMaster.dispense_qty,
                                    PackDetails.queue_type, PackDetails.queue_no, PatientRx.last_pickup_date,
                                    PatientRx.next_pickup_date, PatientRx.prescribed_date, PackDetails.bill_id).dicts() \
            .join(PackRxLink, on=(PackDetails.id == PackRxLink.pack_id)) \
            .join(PatientRx, on=(PatientRx.id == PackRxLink.patient_rx_id)) \
            .join(PatientMaster, on=(PatientMaster.id == PatientRx.patient_id)) \
            .join(FacilityMaster, on=(FacilityMaster.id == PatientMaster.facility_id)) \
            .join(PackHeader, on=(PackHeader.id == PackDetails.pack_header_id)) \
            .join(DoctorMaster, on=(DoctorMaster.id == PatientRx.doctor_id)) \
            .join(SlotHeader, on=(SlotHeader.pack_id == PackDetails.id)) \
            .join(SlotDetails, on=(SlotDetails.slot_id == SlotHeader.id)) \
            .join(DrugTracker, on=DrugTracker.slot_id == SlotDetails.id)    \
            .join(DrugMaster, on=(DrugMaster.id == DrugTracker.drug_id)) \
            .where(functools.reduce(operator.and_, clauses)) \
            .order_by(PackDetails.id.desc())
        if not grouping:
            query1 = query1.group_by(PackDetails.id, SlotHeader.hoa_time, DrugMaster.id)
        else:
            query1 = query1.group_by(PackDetails.id, DrugMaster.id)
        if order_list:
            query1 = query1.order_by(*order_list)

        logger.info(f"in db_get_filled_rx_data, query1 is {query1}")
        return query1

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        logger.error(("Error in db_get_filled_rx_data. {}".format(e)))
    except DoesNotExist as e:
        return 0
    except Exception as e:
        logger.error(e)
        logger.error(("Error in db_get_filled_rx_data. {}".format(e)))


@log_args_and_response
def db_get_last_prn_file(is_ltc):
    """ to fetch last PRN file record from db"""
    try:
        file_constant = constants.PRN_FILE_NAME_CONSTANT if is_ltc else constants.RETAIL_FILE_NAME_CONSTANT
        record = FileHeader.select(FileHeader.filename).where(FileHeader.filename ** f"%{file_constant}%").order_by(
            FileHeader.id.desc()).get()
        file_name = record.filename
        return int((file_name.split(file_constant)[1]).split("_")[0])

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        logger.error(("Error in db_get_last_prn_file. {}".format(e)))
    except DoesNotExist as e:
        return 0
    except Exception as e:
        logger.error(e)
        logger.error(("Error in db_get_last_prn_file. {}".format(e)))


@log_args_and_response
def populate_facility_master(pharmacy_facility_id, facility_data):
    """ to insert records received from FE in facility_master """
    try:
        facility_record, created = FacilityMaster.get_or_create(pharmacy_facility_id=pharmacy_facility_id, defaults=facility_data)
        if not created:
            created_by = facility_data.pop("created_by", None)
            created_date = facility_data.pop("created_date", None)
            FacilityMaster.update(**facility_data).where(FacilityMaster.pharmacy_facility_id == pharmacy_facility_id).execute()
        return facility_record
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("in populate_facility_master, error is", e, exc_info=True)
        return e


@log_args_and_response
def populate_doctor_master(pharmacy_doctor_id, doctor_data):
    """ to insert records received from FE in doctor_master """
    try:
        doctor_record, created = DoctorMaster.get_or_create(pharmacy_doctor_id=pharmacy_doctor_id, defaults=doctor_data)
        if not created:
            created_by = doctor_data.pop("created_by", None)
            created_date = doctor_data.pop("created_date", None)
            DoctorMaster.update(**doctor_data).where(DoctorMaster.pharmacy_doctor_id == pharmacy_doctor_id).execute()
        return doctor_record
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("in populate_doctor_master, error is", e, exc_info=True)
        return e


@log_args_and_response
def populate_patient_master(pharmacy_patient_id, patient_data):
    """ to insert records received from FE in patient_master """
    try:
        patient_record, created = PatientMaster.get_or_create(pharmacy_patient_id=pharmacy_patient_id,
                                                              defaults=patient_data)
        if not created:
            created_by = patient_data.pop("created_by", None)
            created_date = patient_data.pop("created_date", None)
            PatientMaster.update(**patient_data).where(PatientMaster.pharmacy_patient_id == pharmacy_patient_id).execute()
        return patient_record
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("in populate_patient_master, error is", e, exc_info=True)
        return e


@log_args_and_response
def populate_patient_rx(patient_id, drug_id, doctor_id, morning,
                        noon, evening, bed, caution1, caution2, remaining_refill,
                        sig, pharmacy_rx_no, user_id, is_tapered, daw_code, last_billed_date,
                            to_fill_qty, prescribed_date, next_pickup, last_pickup):
    """ to insert records received from FE in patient_rx """
    try:
        data = {
                "pharmacy_rx_no": pharmacy_rx_no,
                "morning": morning,
                "sig": sig,
                "remaining_refill": remaining_refill,
                "is_tapered": is_tapered,
                "noon": noon,
                "evening": evening,
                "bed": bed,
                "caution1": caution1,
                "caution2": caution2,
                "daw_code": daw_code,
                "patient_id": patient_id,
                "drug_id": drug_id,
                "doctor_id": doctor_id,
                "last_billed_date": last_billed_date,
                "to_fill_qty": to_fill_qty,
                "initial_fill_qty": to_fill_qty,
                "prescribed_date": prescribed_date,
                "next_pickup_date": next_pickup,
                "last_pickup_date": last_pickup,
                "created_by": user_id,
                "modified_by": user_id,
                "modified_date": get_current_date_time()
        }
        patient_rx_record, created = PatientRx.get_or_create(patient_id=patient_id, pharmacy_rx_no=pharmacy_rx_no,
                                                             defaults=data)
        if not created:
            previous_record = list(PatientRx.select(PatientRx.to_fill_qty).dicts().where(
                PatientRx.pharmacy_rx_no == pharmacy_rx_no))[0]
            if previous_record["to_fill_qty"]:
                data.pop("initial_fill_qty")
            data.pop("created_by")
            status = PatientRx.update(**data).where(PatientRx.id == patient_rx_record.id).execute()
        return patient_rx_record.id
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("in populate_patient_rx, error is", e, exc_info=True)
        return e


@log_args_and_response
def populate_pack_header(pack_header_dict):
    """ to insert records received from FE in pack_header """
    try:
        pack_header_record, created = PackHeader.get_or_create(**pack_header_dict)
        return pack_header_record
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("in populate_pack_header, error is", e, exc_info=True)
        return e


@log_args_and_response
def populate_pack_details(pack_details_dict):
    """ to insert records received from FE in pack_details """
    try:
        pack_details_record, created = PackDetails.get_or_create(**pack_details_dict)
        return pack_details_record
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("in populate_pack_details, error is", e, exc_info=True)
        return e


@log_args_and_response
def populate_pack_rx_link(pack_rx_link_dict):
    """ to insert records received from FE in pack_rx_link """
    try:
        pack_rx_link_record, created = PackRxLink.get_or_create(**pack_rx_link_dict)
        return pack_rx_link_record
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("in populate_pack_rx_link, error is", e, exc_info=True)
        return e


@log_args_and_response
def populate_slot_header(slot_header_dict):
    """ to insert records received from FE in slot_header """
    try:
        slot_header_record, created = SlotHeader.get_or_create(**slot_header_dict)
        return slot_header_record
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("in populate_slot_header, error is", e, exc_info=True)
        return e


@log_args_and_response
def populate_slot_details(slot_details_dict):
    """ to insert records received from FE in slot_details """
    try:
        slot_details_record, created = SlotDetails.get_or_create(**slot_details_dict)
        return slot_details_record
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("in populate_slot_details, error is", e, exc_info=True)
        return e


@log_args_and_response
def populate_pack_user_map(pack_user_map_dict):
    """ to insert records received from FE in pack_user_map """
    try:
        pack_user_map_record, created = PackUserMap.get_or_create(**pack_user_map_dict)
        return pack_user_map_record
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("in populate_pack_user_map, error is", e, exc_info=True)
        return e


@log_args_and_response
def generate_template_data_based_on_pack_type(total_qty, packaging_type, fill_details, admin_start_date=None, admin_end_date=None):
    """ to insert records received from FE in patient_rx """
    try:
        pass
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("in generate_template_data_based_on_pack_type, error is", e, exc_info=True)
        return e
    except Exception as e:
        logger.error("in generate_template_data_based_on_pack_type, error is", e, exc_info=True)
        return e


@log_args_and_response
def bulk_pack_ids_prn(qty, company_settings):
    """
    This method is used to fetch required pack display ids based on given count of packs

    :param gen_pack_instances: list
    :param company_settings: dict
    :return:
    @param company_settings:
    @param qty:
    """
    try:
        data = send_data(
            company_settings["BASE_URL_IPS"],
            settings.BULK_PACK_IDS_URL, {
                "qty": qty,
                'token': company_settings["IPS_COMM_TOKEN"]
            },
            0, _async=False, token=company_settings["IPS_COMM_TOKEN"], timeout=(5, 25)
        )

        data = data["response"]["data"]
        if not data:
            raise PharmacySoftwareResponseException("Couldn't get extra pack IDs from Pharmacy Software. "
                                                    "Kindly contact support.")
        return data
    except (PharmacySoftwareResponseException, PharmacySoftwareCommunicationException) as e:
        logger.error(e, exc_info=True)
        raise PharmacySoftwareResponseException("Couldn't get extra pack IDs from Pharmacy Software. "
                                                "Kindly contact support.")


@log_args_and_response
def get_fields_dict_for_filled_rx():
    """ to insert records received from FE in patient_rx """
    try:
        fields_dict = {"patient_name": fn.CONCAT(PatientMaster.last_name, ", ", PatientMaster.first_name),
                       "facility_name": FacilityMaster.facility_name,
                       "drug": fn.CONCAT(DrugMaster.drug_name, " ", DrugMaster.strength_value, " ",
                                         DrugMaster.strength, " ", DrugMaster.ndc),
                       "rx_id": fn.CONCAT(PatientRx.pharmacy_rx_no, " ", PackDetails.pack_display_id),
                       "last_billed_date": PatientRx.last_billed_date,
                       "patient_id": PatientMaster.pharmacy_patient_id,
                       "facility_id": FacilityMaster.pharmacy_facility_id,
                       "route_id": PatientMaster.delivery_route_id,
                       "schedule": DrugMaster.drug_schedule,
                       "queue_type": PackDetails.queue_type,
                       "queue_no": PackDetails.queue_no,
                       "tobe_delivered_datetime": PackHeader.scheduled_delivery_date
                       }
        global_search = [
            fn.CONCAT(PatientMaster.last_name, ", ", PatientMaster.first_name),
            FacilityMaster.facility_name,
            fn.CONCAT(DrugMaster.drug_name, " ", DrugMaster.strength_value, " ",
                      DrugMaster.strength),
            PatientRx.pharmacy_rx_no,
            PackDetails.pack_display_id,
            DrugMaster.ndc
        ]

        return fields_dict, global_search
    except (IntegrityError, InternalError, DataError) as e:
        logger.error("in get_fields_dict_for_filled_rx, error is", e, exc_info=True)
        return e
    except Exception as e:
        logger.error("in get_fields_dict_for_filled_rx, error is", e, exc_info=True)
        return e


@log_args_and_response
def delete_pack_dao(pack_id_list):
    """ to update pack status as deleted from pack details and store it in pack status tracker """
    try:
        status = PackDetails.update(pack_status=settings.DELETED_PACK_STATUS).where(
            PackDetails.pack_display_id.in_(pack_id_list)).execute()
        token = get_token()
        user_details = get_current_user(token)
        for pack_id in pack_id_list:
            pack_id = PackDetails.select(PackDetails.id).where(PackDetails.pack_display_id == pack_id).scalar()
            # getting user id using session token instead of getting from front end directly
            pack_status_history_dict = {"pack_id": pack_id, "status": settings.DELETED_PACK_STATUS,
                                        'created_by': user_details['id'],
                                        'reason': None}
            status = PackStatusTracker.insert(**pack_status_history_dict).execute()
        return status
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("in delete_pack_dao, error is", e, exc_info=True)
        return e


@log_args_and_response
def update_queue_type_dao(queue_no, queue_type, modified_by):
    """ to update queue type from Patient Rx received from IPS"""
    try:
        status = PackDetails.update(queue_type=queue_type, modified_date=get_current_date_time(), modified_by=modified_by).where(
            PackDetails.queue_no == queue_no).execute()
        return status
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("in delete_pack_dao, error is", e, exc_info=True)
        return e
