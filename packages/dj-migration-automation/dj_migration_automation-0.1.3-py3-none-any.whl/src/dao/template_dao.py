import operator
from collections import defaultdict
from functools import reduce
from math import ceil
from typing import List, Dict, Any

from peewee import fn, InternalError, IntegrityError, JOIN_LEFT_OUTER, Clause, SQL, DataError, DoesNotExist
from playhouse.shortcuts import cast

import settings
import datetime
from dosepack.base_model.base_model import db, BaseModel
from dosepack.error_handling.error_handler import update_dict, error, create_response
from dosepack.utilities.utils import log_args_and_response, get_current_date_time, get_current_date

from settings import SUCCESS
from src import constants
from src.api_utility import get_results
from src.dao.facility_dao import db_add_facility_schedule_dao
from src.exceptions import TemplateAlreadyProcessed, AutoProcessTemplateException
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_celery_task_meta import CeleryTaskmeta
from src.model.model_container_master import ContainerMaster
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_dosage_type import DosageType
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_master import DrugMaster
from src.model.model_ext_change_rx import ExtChangeRx
from src.model.model_ext_change_rx_details import ExtChangeRxDetails
from src.model.model_ext_pack_details import ExtPackDetails
from src.model.model_facility_schedule import FacilitySchedule
from src.model.model_location_master import LocationMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_header import PackHeader
from src.model.model_pack_details import PackDetails
from src.model.model_patient_schedule import PatientSchedule
from src.model.model_slot_header import SlotHeader
from src.model.model_slot_details import SlotDetails
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_facility_master import FacilityMaster
from src.model.model_file_header import FileHeader
from src.model.model_patient_master import PatientMaster
from src.model.model_store_separate_drug import StoreSeparateDrug
from src.model.model_takeaway_template import TakeawayTemplate
from src.model.model_temp_slot_info import TempSlotInfo
from src.model.model_template_details import TemplateDetails
from src.model.model_template_master import TemplateMaster
from src.model.model_unique_drug import UniqueDrug
from src.model.model_zone_master import ZoneMaster

logger = settings.logger


template_is_modified_map = TemplateMaster.IS_MODIFIED_MAP


@log_args_and_response
def db_get_by_template(file_id, patient_id):
    try:
        query = TempSlotInfo.select(
            fn.CONCAT(DrugMaster.formatted_ndc, '#', fn.IFNULL(DrugMaster.txr, '')).alias('fndc_txr')
        ).distinct() \
            .join(PatientRx, on=PatientRx.id == TempSlotInfo.patient_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(UniqueDrug, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                  & (UniqueDrug.txr == DrugMaster.txr))) \
            .join(StoreSeparateDrug, on=UniqueDrug.id == StoreSeparateDrug.unique_drug_id) \
            .join(TemplateMaster, on=((TemplateMaster.patient_id == TempSlotInfo.patient_id) & (
                    TemplateMaster.file_id == TempSlotInfo.file_id))) \
            .where(TempSlotInfo.patient_id == patient_id,
                   TempSlotInfo.file_id == file_id,
                   TemplateMaster.is_bubble == False)
        return set(item['fndc_txr'] for item in query.dicts())

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_base_pack_count_by_admin_duration(patient_id: int, file_id: int) -> int:
    temp_slot_data_list: List[Dict[str, Any]] = []
    base_pack_count: int = 0
    try:
        temp_slot_data_list = db_get_template_admin_duration_dao(patient_id, file_id)
        for record in temp_slot_data_list:
            fill_days = (record["fill_end_date"] - record["fill_start_date"]).days + 1
            base_pack_count = ceil(fill_days / settings.ONE_WEEK)

        return base_pack_count
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_template_admin_duration_dao(patient_id: int, file_id: int):
    try:
        return TemplateMaster.db_get_template_admin_duration(patient_id, file_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_ungenerate_file(file_id, status, message, modified_by, modified_date, company_id):
    try:
        with db.transaction():
            count = TemplateMaster.db_get_template_count_by_status(file_id, [settings.DONE_TEMPLATE_STATUS])
            if count:
                raise TemplateAlreadyProcessed
            FileHeader.update(
                status=status,
                message=message,
                modified_by=modified_by,
                modified_date=modified_date
            ).where(
                FileHeader.id == file_id,
                FileHeader.company_id == company_id
            ).execute()

            yellow_template_query = TemplateMaster.select(TemplateMaster.patient_id) \
                .where(TemplateMaster.file_id == file_id,
                       TemplateMaster.status != settings.UNGENERATED_TEMPLATE_STATUS,
                       TemplateMaster.is_modified == TemplateMaster.IS_MODIFIED_MAP['YELLOW']
                       )
            patient_ids = list()
            for record in yellow_template_query.dicts():
                patient_ids.append(record['patient_id'])
            TemplateMaster.update(
                status=settings.UNGENERATED_TEMPLATE_STATUS,
                reason=message,
                modified_by=modified_by,
                modified_date=modified_date
            ).where(
                TemplateMaster.file_id == file_id,
                TemplateMaster.status != settings.UNGENERATED_TEMPLATE_STATUS
            ).execute()
            TempSlotInfo.delete().where(TempSlotInfo.file_id == file_id).execute()
            if patient_ids:
                TemplateDetails.delete().where(TemplateDetails.file_id == file_id,
                                               TemplateDetails.patient_id << patient_ids).execute()
            pack_ids_list = []
            for record in PackHeader.select(
                    PackDetails.id
            ).dicts() \
                    .join(PackDetails, on=PackDetails.pack_header_id == PackHeader.id) \
                    .where(PackDetails.company_id == company_id,
                           PackHeader.file_id == file_id):
                pack_ids_list.append(record["id"])
            if pack_ids_list:  # if pack is not generated for file pack ids list will be empty
                PackDetails.update(pack_status=settings.UNGENERATED_PACK_STATUS) \
                    .where(PackDetails.id << pack_ids_list) \
                    .execute()

            return SUCCESS

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_template_file_id_by_pharmacy_fill_dao(pharmacy_fill_id_set):
    try:
        return TempSlotInfo.db_get_template_file_id_by_pharmacy_fill(pharmacy_fill_id_set=pharmacy_fill_id_set)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_template_master_create_record(item, add_fields, remove_fields_list, default_data_dict):
    try:
        return BaseModel.db_create_record(
                    item,
                    TemplateMaster,
                    add_fields=add_fields,
                    remove_fields=remove_fields_list,
                    get_or_create=False,
                    default_data_dict=default_data_dict
                )
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_template_master_info_by_template_id_dao(template_id):
    try:
        return TemplateMaster.db_get_template_master_info_by_template_id(template_id=template_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException


@log_args_and_response
def db_temp_slot_info_create_record(item, add_fields, remove_fields_list):
    try:
        return BaseModel.db_create_record(
            item,
            TempSlotInfo,
            default_data_dict=False,
            add_fields=add_fields,
            remove_fields=remove_fields_list,
            get_or_create=False
        )
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_temp_slot_info_create_multi_record(temp_slot_list):
    try:
        return BaseModel.db_create_multi_record(temp_slot_list, TempSlotInfo)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_verify_template_list_dao(template_list, company_id, status):
    try:
        return TemplateMaster.db_verify_templatelist(templatelist=template_list, company_id=company_id, status=status)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_rx_records(pack_id, dict_total_quantity, distinct_date_set):
    """
    Takes a pack data frame and persists the data of the entire pack in the database. It inserts the
    data in the pack_header, pack_details, pack_rx_link, slot_header, slot_details.

    Args:
        pack_id (int): The pack_id for the given pack
        dict_total_quantity (dict): A dict containing all the distinct rx_no along with the total
        quantity associated with them for the given pack_id
        distinct_date_set (set): The set of distinct dates associated with the given pack_id

    Returns:
        pharmacy_rx_list(list) : A list containing distinct pharmacy_rx no for the given pack_id

    Examples:
        >>> db_get_rx_records(1, 882019, 882019, {"34563": 24, "34567": 14}, set('2016-06-05', '2016-06-06'))
            True
    """
    try:
        date_list = [distinct_date_set[0], distinct_date_set[-1]]
        for record in PackRxLink.select(PackRxLink.patient_rx_id, PatientRx.pharmacy_rx_no, TemplateDetails.quantity,
                                        TemplateDetails.hoa_time, TemplateDetails.column_number,
                                        TemplateDetails.patient_id, PackRxLink.pack_id, SlotHeader.hoa_time) \
                .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
                .join(TemplateDetails, on=PatientRx.id == TemplateDetails.patient_rx_id) \
                .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
                .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
                .dicts().distinct() \
                .where(PackRxLink.pack_id == pack_id, TemplateDetails.hoa_time == SlotHeader.hoa_time) \
                .order_by(TemplateDetails.column_number):
            record["hoa_time"] = record["hoa_time"].strftime('%H:%M:%S')
            key = (record["patient_rx_id"], record["hoa_time"], record["column_number"])
            if key in dict_total_quantity:
                # If one time is split into two pack we will get extra hoa time here,
                # we wont find key as column number is not present for that pack
                record["total_quantity"] = float(dict_total_quantity[key])
            else:
                continue
            record["quantity"] = float(record["quantity"])
            record["date_list"] = date_list
            yield record
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def get_ungenerate_files(status, dateFrom, dateTo, company_id):
    try:
        for records in FileHeader.select(FileHeader.id.alias('file_id'),
                                         FileHeader.filename) \
                .where(FileHeader.company_id == company_id,
                       FileHeader.status == status):
            yield records
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def save_template(patient_id, user_id, template_details, takeaway_template_data):
    """
    saves template data
    :param patient_id:
    :param user_id:
    :param template_details: list
    :param takeaway_template_data: list
    :return:
    """
    try:
        with db.transaction():
            template_details_status = TemplateDetails.insert_many(template_details).execute()
            for data in takeaway_template_data:
                week_day = int(data["week_day"])
                week_day = (week_day - 1) % 7  # angular to python weekday conversion
                data["week_day"] = week_day
            takeaway_status = TakeawayTemplate.delete() \
                .where(TakeawayTemplate.patient_id == patient_id).execute()
            if takeaway_template_data:
                takeaway_temp_data_list = []
                for item in takeaway_template_data:
                    takeaway_temp_data_list.append(
                        update_dict(
                            item,
                            add_fields={
                                'patient_id': patient_id,
                                'created_by': user_id,
                                'modified_by': user_id
                            }
                        )
                    )
                takeaway_status = TakeawayTemplate.insert_many(takeaway_temp_data_list).execute()
            return True
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def decode_celery_result(template_result):
    possible_error_messages = ["Couldn't get extra pack IDs from Pharmacy Software. Kindly contact support.",
                               "Error in storing pack(s) data in Pharmacy Software. Kindly contact support.",
                               "Couldn't store pack(s) data in Pharmacy Software. Kindly contact support.",
                               "No Template Found",
                               "Template Already Processed or Rolled Back.",
                               "Internal SQL Error",
                               "Error for the data to be inserted in the table PackHeader",
                               "Error for the data to be inserted in the table PackDetails",
                               "Error for the data to be inserted in the table SlotHeader",
                               "Error for the data to be inserted in the table PackRxLink",
                               "Not able to communicate with pharmacy software to get fill ids",
                               "Invalid response from pharmacy software for fill ids",
                               "Error for the data to be inserted in the table SlotDetails",
                               "Template Already Processed",
                               "Pack generation failed",
                               "Error in fetching patient data",
                               "Internal SQL Error in fetching patient data",
                               "PharmacyRxFile could not be generated",
                               "Template Already added for pack generation"
                               "PharmacySlotFile could not be generated",
                               "Database Connection Failed",
                               "The file/patient details associated with the template has been deleted in the pharmacy "
                               "software. Kindly rollback and proceed further.",
                               "Template(s) for this patient is already present. Take necessary action(s) for them"
                               " before saving/processing this template."]

    error_message = "Error while processing the template."

    try:
        decoded_result_message = template_result.decode('utf-8', 'ignore') if template_result else None

        if decoded_result_message:
            for err in possible_error_messages:
                if err in decoded_result_message:
                    error_message = err
                    break
    except Exception as e:
        logger.error(e, exc_info=True)
        pass
    return error_message


@log_args_and_response
def db_get_template_drug_details(patient_id, file_id):
    """ Takes the patient_id and gets all the template data for the given patient_id.

        Args:
            patient_id (int): The id of the patient
            file_id (int): The id of the file

        Returns:
            List : All the template records for the given patient_id

        Examples:
            >>> TemplateDetails.get_template_data()
            []

    """
    try:
        for record in TempSlotInfo.select(
                TempSlotInfo.quantity, TempSlotInfo.hoa_time, PatientRx.pharmacy_rx_no,
                PatientRx.sig, PatientRx.is_tapered,
                DosageType.name.alias('dosage_name'),
                DosageType.code.alias('dosage_code'),
                DosageType.id.alias('dosage_type_id'),
                # StoreSeparateDrug.note.alias('store_separate_note'),
                StoreSeparateDrug.id.alias('store_separate_drug_id'),
                UniqueDrug.id.alias('unique_drug_id'),
                fn.IF(DrugDimension.unique_drug_id.is_null(True), False, True).alias("is_dimension_available"),
                DrugMaster.ndc, DrugMaster.drug_name, DrugMaster.strength,
                DrugMaster.formatted_ndc, DrugMaster.txr,
                DrugMaster.strength_value, PatientRx.id.alias('patient_rx_id'),
                DrugMaster.id.alias('drug_id'), DrugMaster.image_name,
                DrugMaster.color, DrugMaster.shape, DrugMaster.imprint,
                fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                      DrugStockHistory.is_in_stock).alias("is_in_stock"),
                fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                      DrugDetails.last_seen_by).alias('last_seen_with'),
                TempSlotInfo.patient_id,
                fn.GROUP_CONCAT(
                    Clause(SQL('DISTINCT'), TempSlotInfo.hoa_date, SQL('ORDER BY'),
                           TempSlotInfo.hoa_date)).alias('admin_date_list'),
                DrugDimension.shape.alias('drug_shape'),
                DrugMaster.color,
        ).dicts() \
                .join(PatientRx, on=PatientRx.id == TempSlotInfo.patient_rx_id) \
                .join(FileHeader, on=FileHeader.id == TempSlotInfo.file_id) \
                .join(DrugMaster, on=PatientRx.drug_id == DrugMaster.id) \
                .join(UniqueDrug, JOIN_LEFT_OUTER, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc)
                                                      & (UniqueDrug.txr == DrugMaster.txr)) \
                .join(DrugStockHistory, JOIN_LEFT_OUTER,
                      on=((UniqueDrug.id == DrugStockHistory.unique_drug_id) & (DrugStockHistory.is_active == 1)
                          & DrugStockHistory.company_id == FileHeader.company_id)) \
                .join(DrugDetails, JOIN_LEFT_OUTER, on=(DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                       (DrugDetails.company_id == FileHeader.company_id)) \
                .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
                .join(StoreSeparateDrug, JOIN_LEFT_OUTER, on=StoreSeparateDrug.unique_drug_id == UniqueDrug.id) \
                .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == StoreSeparateDrug.dosage_type_id) \
                .where(TempSlotInfo.patient_id == patient_id,
                       TempSlotInfo.file_id == file_id) \
                .order_by(TempSlotInfo.hoa_time) \
                .group_by(TempSlotInfo.patient_rx_id,
                          TempSlotInfo.hoa_time):
            record["column_number"] = None
            record["admin_date_list"] = record["admin_date_list"].split(',')
            if record['drug_shape']:
                record['drug_shape'] = settings.COLOR_SHAPE_MAPPING[record['drug_shape']]
            # print("record", record)
            yield record

    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_saved_template(patient_id, file_id, company_id):
    """ Takes the patient_id and gets all the template data which already exists.

        Args:
            patient_id (int): The id of the patient
            file_id (int): File ID
            company_id: The id of the company

        Returns:
            List : All the template records for the given patient_id

        Examples:
            >>> TemplateDetails.get_template_data()
            []

    """
    try:
        query = TemplateDetails.select(TemplateDetails.quantity,
                                       TemplateDetails.hoa_time,
                                       TemplateDetails.column_number,
                                       TemplateDetails.patient_id,
                                       TemplateDetails.modified_date.alias('modified_time'),
                                       PatientRx.id.alias('patient_rx_id'),
                                       PatientRx.pharmacy_rx_no,
                                       PatientRx.is_tapered,
                                       PatientRx.sig,
                                       DosageType.name.alias('dosage_name'),
                                       DosageType.code.alias('dosage_code'),
                                       DosageType.id.alias('dosage_type_id'),
                                       UniqueDrug.id.alias('unique_drug_id'),
                                       fn.IF(DrugDimension.unique_drug_id.is_null(True),
                                             False, True).alias('is_dimension_available'),
                                       # StoreSeparateDrug.note.alias('store_separate_note'),
                                       StoreSeparateDrug.id.alias('store_separate_drug_id'),
                                       DrugMaster.ndc,
                                       DrugMaster.drug_name,
                                       DrugMaster.strength,
                                       DrugMaster.strength_value,
                                       DrugMaster.id.alias('drug_id'),
                                       DrugMaster.image_name,
                                       DrugMaster.formatted_ndc,
                                       DrugMaster.txr,
                                       DrugMaster.color,
                                       DrugMaster.shape,
                                       DrugMaster.imprint,
                                       fn.GROUP_CONCAT(Clause(SQL('DISTINCT'), TempSlotInfo.hoa_date, SQL('ORDER BY'),
                                                              TempSlotInfo.hoa_date)).alias('admin_date_list'),
                                       fn.IF(DrugStockHistory.is_in_stock.is_null(True), True,
                                             DrugStockHistory.is_in_stock).alias("is_in_stock"),
                                       fn.IF(DrugStockHistory.created_by.is_null(True), None,
                                             DrugStockHistory.created_by).alias('stock_updated_by'),
                                       fn.IF(DrugDetails.last_seen_by.is_null(True), 'null',
                                             DrugDetails.last_seen_by).alias('last_seen_with'),
                                       fn.IF(DrugDetails.last_seen_date.is_null(True), 'null',
                                             DrugDetails.last_seen_date).alias('last_seen_on')) \
            .join(PatientRx, on=PatientRx.id == TemplateDetails.patient_rx_id) \
            .join(TempSlotInfo, on=((TempSlotInfo.file_id == file_id) &
                                    (TempSlotInfo.patient_rx_id == TemplateDetails.patient_rx_id) &
                                    (TempSlotInfo.hoa_time == TemplateDetails.hoa_time))
                  # This join is done to get admin_date_list for specific rx and its hoa time,
                  # This should be handled differently if taper_drugs splitting is allowed in template
                  ) \
            .join(DrugMaster, on=PatientRx.drug_id == DrugMaster.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                  (UniqueDrug.txr == DrugMaster.txr)) \
            .join(DrugDimension, JOIN_LEFT_OUTER, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(DrugStockHistory, JOIN_LEFT_OUTER, on=((DrugStockHistory.unique_drug_id == UniqueDrug.id) &
                                                         (DrugStockHistory.is_active == True) &
                                                         DrugStockHistory.company_id == company_id)) \
            .join(DrugDetails, JOIN_LEFT_OUTER, on=((DrugDetails.unique_drug_id == UniqueDrug.id) &
                                                    (DrugDetails.company_id == company_id))) \
            .join(StoreSeparateDrug, JOIN_LEFT_OUTER, on=StoreSeparateDrug.unique_drug_id == UniqueDrug.id) \
            .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == StoreSeparateDrug.dosage_type_id) \
            .where(TemplateDetails.patient_id == patient_id, TempSlotInfo.file_id == file_id) \
            .order_by(TemplateDetails.column_number,
                      TemplateDetails.patient_rx_id) \
            .group_by(TemplateDetails.patient_rx_id,
                      TemplateDetails.hoa_time,
                      TemplateDetails.column_number)

        for record in query.dicts():
            record["modified_time"] = record["modified_time"].isoformat()
            record["admin_date_list"] = record["admin_date_list"].split(',')
            yield record

    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def create_template_details_list(data, user_id, file_id):
    """ Returns list of dict to be inserted in `TemplateDetails` """
    template_details = list()

    try:
        current_datetime = get_current_date_time()
        for item in data:
            template_details.append(
                update_dict(
                    item,
                    add_fields={
                        'created_by': user_id,
                        'modified_by': user_id,
                        'modified_date': current_datetime,
                        'file_id': file_id
                    },
                    remove_fields=['display_time']
                )
            )
        return template_details
    except (IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_save_template(file_id, patient_id, data, user_id, modified_time, takeaway_template_data,
                     set_yellow_template_flag=False, set_red_template_flag=False):
    """ Gets the template data along with the patient_id and stores them in the
    template_details table.

        Args:
            file_id (int): The id of the file
            patient_id (int): The id of the patient
            data (list): The list of modified records for the given patient_id template.
            user_id (int): The id of the user who inserted the record
            modified_time(str): Last modified time of record
            takeaway_template_data
            set_yellow_template_flag (bool): Flag for auto-save
            set_red_template_flag (bool): Flag for mandatory verification
        Returns:
            Boolean : True or False given on the status of the data saved.

        Examples:
            >>> TemplateDetails.db_save_template(1, [])
            []
    """
    try:
        logger.info('in_db_save: patient_id: ' + str(patient_id) + 'file_id: ' + str(file_id) +
                    'set_yellow_template_flag: ' + str(set_yellow_template_flag) + 'set_red_template_flag: ' +
                    str(set_red_template_flag))

        current_datetime = get_current_date_time()
        template_details = []
        status4 = False
        # if template is not in pending state, throw error.
        if not TemplateMaster.db_is_pending(file_id, patient_id):
            return error(5003)

        logger.info("saving_file_data")
        with db.transaction():
            previous_status = TemplateMaster.db_get_status(file_id, patient_id)

            template_column_list = [data['column_number'] for data in data]
            takeaway_template_column_list = [data['template_column_number'] for data in takeaway_template_data]
            valid_template_column = set(takeaway_template_column_list).issubset(set(template_column_list))
            if not valid_template_column:
                return error(1020, "Invalid template_column_number, Not present in template data list.")
            pack_type, customization_flag, is_sppd, is_true_unit, is_bubble = get_template_flags(file_id=file_id,
                                                                                      patient_id=patient_id)
            if previous_status or (
                    pack_type == constants.UNIT_DOSE_PER_PACK or customization_flag or is_true_unit or is_sppd):
                # if template has additional data
                # we directly allow the user to save
                status1 = TemplateDetails.db_delete(patient_id)
                modification_status = None
                if set_yellow_template_flag or set_red_template_flag:
                    modification_status = TemplateMaster.IS_MODIFIED_MAP['YELLOW']
                # elif set_red_template_flag:
                #     modification_status = TemplateMaster.IS_MODIFIED_MAP['RED']
                else:
                    modification_status = TemplateMaster.IS_MODIFIED_MAP['GREEN']
                status2 = TemplateMaster.db_update_modification_status(patient_id, file_id, modification_status)

                template_details = create_template_details_list(data, user_id, file_id)

                if not set_red_template_flag:
                    status4 = save_template(patient_id, user_id, template_details, takeaway_template_data)
                # Notifications().pre_process(patient_id, file_id)
            else:
                # get the modified time and compare it with the time sent by the user
                # if the time matches with the time stamp retreived from the server
                # we allow the user to save else we don't allow the user to save
                db_modified_time = str(TemplateDetails.db_get_modified_time(patient_id))

                if modified_time == db_modified_time:
                    logger.debug('***Timings matched**** for:' + 'patient_id')
                    status1 = TemplateDetails.db_delete(patient_id)
                    modification_status = None
                    if set_yellow_template_flag or set_red_template_flag:
                        modification_status = TemplateMaster.IS_MODIFIED_MAP['YELLOW']
                    # elif set_red_template_flag:
                    #     modification_status = TemplateMaster.IS_MODIFIED_MAP['RED']
                    else:
                        modification_status = TemplateMaster.IS_MODIFIED_MAP['GREEN']
                    status2 = TemplateMaster.db_update_modification_status(patient_id, file_id, modification_status)
                    template_details = create_template_details_list(data, user_id, file_id)
                    if not set_red_template_flag:
                        status4 = save_template(patient_id, user_id, template_details, takeaway_template_data)
                    # Notifications().pre_process(patient_id, file_id)
                else:
                    logger.debug("**** Timings do not match **** for: patient_id" + str(patient_id))
                    return error(5002)
        return create_response(status4)

    except InternalError as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except (IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2002)


@log_args_and_response
def db_get_rx_info(patient_id):
    """ Takes patient_id and returns all the rx_no associated with it.

        Args:
            patient_id (int): The id of the patient

        Returns:
            List : List of all the rx_no which belongs to the given patient.

        Examples:
            >>> db_get_rx_info(1)
            >>> True

    """
    # for record in TemplateDetails.select(TemplateDetails.patient_id, TemplateDetails.quantity,
    #                                      TemplateDetails.hoa_time, PatientRx.pharmacy_rx_no, PatientRx.drug_id) \
    #         .join(PatientRx) \
    #         .dicts().where(TemplateDetails.patient_id == patient_id):

    try:
        for record in TemplateDetails.select(PatientRx.pharmacy_rx_no, PatientRx.drug_id, TemplateDetails.patient_id,
                                             TemplateDetails.hoa_time,
                                             fn.sum(TemplateDetails.quantity).alias('total_quantity')) \
                .join(PatientRx, on=PatientRx.id == TemplateDetails.patient_rx_id) \
                .dicts() \
                .where(TemplateDetails.patient_id == patient_id) \
                .group_by(PatientRx.pharmacy_rx_no, TemplateDetails.hoa_time):
            logger.info("Rx info from Template Details:" + str(record))
            yield record
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_template_detail_columns(patient_id):
    """ Takes the patient_id and gets all the unique column numbers

        **Shifted to DAO layer

        Args:
            patient_id (int): The id of the patient

        Returns:
            List : All the template records for the given patient_id

        Examples:
            >>> TemplateDetails.db_template_detail_columns(1)
            []

    """
    try:
        for record in TemplateDetails.select(PatientRx.drug_id,
                                             TemplateDetails.column_number,
                                             TemplateDetails.hoa_time,
                                             TemplateDetails.quantity,
                                             TemplateDetails.patient_rx_id) \
                .join(PatientRx, on=PatientRx.id == TemplateDetails.patient_rx_id).dicts() \
                .where(TemplateDetails.patient_id == patient_id,
                       TemplateDetails.quantity > 0):
            yield record
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pending_templates(status, company_id):
    """ Gets all the template meta data based on the given status

        Args:
            status List(int): The status on which the template is to be fetched
            company_id (int): company id for which templates need to be fetched

        Returns:
            List : List of all the template meta data for the given status.

        Examples:
            >>> TemplateMaster.get_all_templates(1, 2)
            >>> []

    """
    linked_packs_list: List[int] = []
    change_rx_comment_list: List[str] = []

    try:
        TemplateMasterAlias = TemplateMaster.alias()
        pending_template_status = settings.PENDING_PROGRESS_TEMPLATE_LIST
        # slot_data = TemplateMaster.select(TemplateMaster.id.alias('template_id'),
        #                                   fn.GROUP_CONCAT(
        #                                       Clause(SQL('DISTINCT'), TempSlotInfo.hoa_date, SQL('ORDER BY'),
        #                                              TempSlotInfo.hoa_date)).alias('admin_date_list')) \
        #     .join(TempSlotInfo, on=((TempSlotInfo.file_id == TemplateMaster.file_id) &
        #                             (TempSlotInfo.patient_id == TemplateMaster.patient_id))) \
        #     .group_by(TempSlotInfo.file_id, TempSlotInfo.patient_id) \
        #     .where(TemplateMaster.company_id == company_id,
        #            TemplateMaster.status << (
        #                settings.PENDING_TEMPLATE_STATUS, settings.PROGRESS_TEMPLATE_STATUS)).alias('slot_data')

        current_date = get_current_date()
        previous_date = datetime.datetime.strptime(current_date, '%Y-%m-%d') - datetime.timedelta(days=60)
        # if optimization is needed in sub_q 3 filter based on admin dates by adding
        # packdetails.consumption_start_date > previous date

        template_data = TemplateMaster.select(TemplateMaster.patient_id,
                                              TemplateMaster.file_id).dicts() \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMaster.status << pending_template_status)

        file_patient_list = list()
        patient_ids = list()

        # fetching patient_file info to filter temp_slot_info and patinet_ids to filter packs info
        for record in template_data:
            file_patient_list.append('{}#{}'.format(record['patient_id'], record['file_id']))
            patient_ids.append(record['patient_id'])

        if not patient_ids:
            return {}
        packs_query = PackHeader.select(PackHeader.patient_id.alias('patient_id'),
                                        PackDetails.pack_display_id.alias('pack_display_id'),
                                        PackDetails.consumption_start_date.alias('consumption_start_date'),
                                        PackDetails.consumption_end_date.alias('consumption_end_date'),
                                        PackHeader.file_id.alias('file_id')) \
            .join(PackDetails,
                  on=((PackDetails.pack_header_id == PackHeader.id) &
                      (PackDetails.pack_status.not_in([settings.DELETED_PACK_STATUS])))) \
            .where(PackDetails.company_id == company_id,
                   PackDetails.consumption_start_date > previous_date,
                   PackHeader.patient_id << patient_ids).alias('packs_query')

        sub_q_2 = TemplateMaster.select(TemplateMaster.id.alias('temp_id'),
                                        fn.GROUP_CONCAT(fn.DISTINCT(TemplateMasterAlias.id)).coerce(False)
                                        .alias('duplicate_template_ids')) \
            .join(TemplateMasterAlias, on=((TemplateMaster.patient_id == TemplateMasterAlias.patient_id) &
                                           (TemplateMasterAlias.id != TemplateMaster.id))) \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMasterAlias.status << settings.PENDING_PROGRESS_TEMPLATE_LIST,
                   TemplateMaster.status << settings.PENDING_PROGRESS_TEMPLATE_LIST) \
            .group_by(TemplateMaster.id).alias('sub_q_2')

        temp_slot_data = TempSlotInfo.select(TempSlotInfo.patient_id.alias('patient_id'),
                                             TempSlotInfo.hoa_date.alias('hoa_date'),
                                             TempSlotInfo.file_id.alias('file_id')) \
            .where(fn.CONCAT(TempSlotInfo.patient_id, '#', TempSlotInfo.file_id) << file_patient_list).alias(
            'temp_slot_data')

        # query to get packs having overlapping or similar admin period for each template
        sub_q_3 = TemplateMaster.select(TemplateMaster.id.alias('temp_id'),
                                        fn.GROUP_CONCAT(fn.DISTINCT(packs_query.c.pack_display_id)).coerce(False)
                                        .alias('duplicate_pack_ids'),
                                        ) \
            .join(temp_slot_data, on=((temp_slot_data.c.file_id == TemplateMaster.file_id) &
                                      (temp_slot_data.c.patient_id == TemplateMaster.patient_id))) \
            .join(packs_query,
                  on=(
                          (TemplateMaster.patient_id == packs_query.c.patient_id) &
                          (temp_slot_data.c.hoa_date.between(packs_query.c.consumption_start_date,
                                                             packs_query.c.consumption_end_date)
                           ))) \
            .group_by(temp_slot_data.c.file_id, temp_slot_data.c.patient_id) \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMaster.status << settings.PENDING_PROGRESS_TEMPLATE_LIST).alias('sub_q_3')

        sub_ext_change_rx, sub_q_4 = db_get_template_change_rx_info(company_id=company_id, file_id=0, patient_id=0)

        query = TemplateMaster.select(TemplateMaster.status,
                                      TemplateMaster.file_id,
                                      TemplateMaster.patient_id,
                                      TemplateMaster.is_modified.alias('is_template_modified'),
                                      TemplateMaster.created_date,
                                      TemplateMaster.id.alias('template_id'),
                                      TemplateMaster.delivery_datetime,
                                      TemplateMaster.system_id,
                                      PatientMaster.last_name, PatientMaster.first_name,
                                      fn.IF(sub_q_2.c.duplicate_template_ids, 1, 0)
                                      .alias('duplicate_template_present'),
                                      fn.IF(sub_q_3.c.duplicate_pack_ids, 1, 0)
                                      .alias('duplicate_packs_present'),
                                      sub_q_2.c.duplicate_template_ids,
                                      sub_q_3.c.duplicate_pack_ids,
                                      PatientMaster.pharmacy_patient_id, PatientMaster.patient_no,
                                      sub_q_4.c.linked_packs.alias("linked_packs"),
                                      sub_ext_change_rx.c.change_rx_comment.alias("change_rx_comment"),
                                      FacilityMaster.facility_name, FacilityMaster.id.alias("facility_id"),
                                      FacilitySchedule.start_date.alias("delivery_date"),
                                      PatientSchedule.delivery_date_offset,
                                      PatientSchedule.last_import_date,
                                      FacilitySchedule.fill_cycle,
                                      FacilitySchedule.days,
                                      PatientSchedule.id.alias("patient_schedule_id")
                                      ) \
            .join(PatientMaster, on=PatientMaster.id == TemplateMaster.patient_id) \
            .join(PatientSchedule, JOIN_LEFT_OUTER, on=((PatientMaster.id == PatientSchedule.patient_id) &
                                       (PatientMaster.facility_id == PatientSchedule.facility_id))) \
            .join(FacilitySchedule, JOIN_LEFT_OUTER, on=PatientSchedule.schedule_id == FacilitySchedule.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(FileHeader, on=TemplateMaster.file_id == FileHeader.id) \
            .join(sub_q_3, JOIN_LEFT_OUTER, on=sub_q_3.c.temp_id == TemplateMaster.id) \
            .join(sub_q_2, JOIN_LEFT_OUTER, on=sub_q_2.c.temp_id == TemplateMaster.id) \
            .join(sub_ext_change_rx, JOIN_LEFT_OUTER, on=sub_ext_change_rx.c.template_id == TemplateMaster.id) \
            .join(sub_q_4, JOIN_LEFT_OUTER, on=sub_q_4.c.template_id == TemplateMaster.id) \
            .join(TemplateDetails, JOIN_LEFT_OUTER, on=TemplateDetails.patient_id == TemplateMaster.patient_id) \
            .group_by(TemplateMaster.file_id, TemplateMaster.patient_id) \
            .where(FileHeader.company_id == company_id, TemplateMaster.status << status) \
            .order_by(SQL('duplicate_packs_present').desc(),
                      SQL('duplicate_template_present').desc(), SQL('FIELD(is_template_modified, 1,2,0)'),
                      TemplateMaster.id)

        for record in query.dicts():
            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["admin_date_list"] = list()
            temp_slot_data_2 = TempSlotInfo.select(TempSlotInfo.patient_id.alias('patient_id'),
                                                   TempSlotInfo.hoa_date.alias('hoa_date'),
                                                   TempSlotInfo.file_id.alias('file_id')) \
                .where(TempSlotInfo.patient_id == record['patient_id'], TempSlotInfo.file_id == record['file_id']) \
                .order_by(TempSlotInfo.hoa_date).alias('temp_slot_data_2')
            for temp in list(temp_slot_data_2):
                if temp.patient_id_id == record["patient_id"] and temp.file_id_id == record["file_id"]:
                    hoa_date = temp.hoa_date.strftime('%m-%d-%y')
                    if hoa_date not in record["admin_date_list"]:
                        record["admin_date_list"].append(hoa_date)

            if not record.get("admin_date_list", None):
                continue
            record["admin_period"] = str(
                record["admin_date_list"][0] + "  to  " + record["admin_date_list"][
                    len(record["admin_date_list"]) - 1])

            linked_packs_list = []
            if record["linked_packs"] is not None:
                linked_packs_list = list(map(lambda x: int(x), record["linked_packs"].split(',')))
            record["linked_packs"] = linked_packs_list

            change_rx_comment_list = []
            if record["change_rx_comment"] is not None:
                change_rx_comment_list = record["change_rx_comment"].split(',')
            record["change_rx_comment"] = change_rx_comment_list

            record['delivery_datetime'] = str(record['delivery_datetime']) if record['delivery_datetime'] else None
            yield record

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_template(file_id, patient_id):
    """
    Returns template given file id and patient id

    :param file_id:
    :param patient_id:
    :return: Model
    """
    try:
        if CeleryTaskmeta.table_exists():
            query = TemplateMaster.select(TemplateMaster, CeleryTaskmeta.status.alias('celery_task_status')) \
                .join(CeleryTaskmeta, JOIN_LEFT_OUTER, on=TemplateMaster.task_id == CeleryTaskmeta.task_id) \
                .where(TemplateMaster.file_id == file_id, TemplateMaster.patient_id == patient_id).get()
            return query
        else:
            query = TemplateMaster.select() \
                .where(TemplateMaster.file_id == file_id, TemplateMaster.patient_id == patient_id).get()
            return query
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_ext_linked_data_change_rx(company_id: int, file_id: int, patient_id: int):
    linked_packs_list: List[int] = []
    change_rx_comment_list: List[str] = []

    try:
        sub_ext_change_rx, sub_q_4 = db_get_template_change_rx_info(company_id=company_id, file_id=file_id,
                                                                    patient_id=patient_id)

        query = TemplateMaster.select(sub_q_4.c.linked_packs.alias("linked_packs"),
                                      sub_ext_change_rx.c.change_rx_comment.alias("change_rx_comment")) \
            .join(sub_ext_change_rx, JOIN_LEFT_OUTER, on=sub_ext_change_rx.c.template_id == TemplateMaster.id) \
            .join(sub_q_4, JOIN_LEFT_OUTER, on=sub_q_4.c.template_id == TemplateMaster.id) \
            .group_by(TemplateMaster.id) \
            .where(TemplateMaster.company_id == company_id, TemplateMaster.file_id == file_id,
                   TemplateMaster.patient_id == patient_id)

        for record in query.dicts():
            if record["linked_packs"] is not None:
                linked_packs_list = list(map(lambda x: int(x), record["linked_packs"].split(',')))

            if record["change_rx_comment"] is not None:
                change_rx_comment_list = record["change_rx_comment"].split(',')

        return linked_packs_list, change_rx_comment_list
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_template_change_rx_info(company_id: int, file_id: int, patient_id: int):
    clauses_ext_data = list()
    clauses_old_packs = list()
    try:
        clauses_ext_data.append(TemplateMaster.company_id == company_id)
        clauses_ext_data.append(TemplateMaster.status << settings.PENDING_PROGRESS_TEMPLATE_LIST)
        if file_id and patient_id:
            clauses_ext_data.append(TemplateMaster.file_id == file_id)
            clauses_ext_data.append(TemplateMaster.patient_id == patient_id)

        sub_ext_change_rx = TemplateMaster.select(TemplateMaster.id.alias("template_id"),
                                                  TemplateMaster.fill_start_date, TemplateMaster.fill_end_date,
                                                  ExtChangeRx.id.alias("ext_change_rx_id"),
                                                  fn.GROUP_CONCAT(fn.DISTINCT(ExtChangeRxDetails.ext_comment))
                                                  .coerce(False).alias("change_rx_comment"),
                                                  ) \
            .join(ExtChangeRx, on=TemplateMaster.id == ExtChangeRx.new_template) \
            .join(ExtChangeRxDetails, on=ExtChangeRx.id == ExtChangeRxDetails.ext_change_rx_id) \
            .where(reduce(operator.and_, clauses_ext_data)) \
            .group_by(TemplateMaster.patient_id, TemplateMaster.file_id).alias('sub_ext_change_rx')

        clauses_old_packs.append(ExtPackDetails.status_id << settings.PACK_PROGRESS_DONE_STATUS_LIST)
        clauses_old_packs.append(ExtPackDetails.pack_usage_status_id == constants.EXT_PACK_USAGE_STATUS_PENDING_ID)
        clauses_old_packs.append(PackDetails.consumption_start_date >= sub_ext_change_rx.c.fill_start_date)
        clauses_old_packs.append(PackDetails.consumption_end_date <= sub_ext_change_rx.c.fill_end_date)

        sub_q_4 = TemplateMaster.select(TemplateMaster.id.alias("template_id"),
                                        fn.GROUP_CONCAT(fn.DISTINCT(ExtPackDetails.ext_pack_display_id)).coerce(False)
                                        .alias("linked_packs")
                                        ) \
            .join(PackHeader, on=TemplateMaster.patient_id == PackHeader.patient_id) \
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(ExtPackDetails, on=PackDetails.id == ExtPackDetails.pack_id) \
            .join(sub_ext_change_rx, JOIN_LEFT_OUTER, on=sub_ext_change_rx.c.template_id == TemplateMaster.id) \
            .where(reduce(operator.and_, clauses_old_packs)) \
            .group_by(TemplateMaster.id).alias("sub_q_4")

        return sub_ext_change_rx, sub_q_4
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pending_templates_data(company_id):
    """ Gets all the pending template meta data based on the given company

        Args:
            company_id (int): company_id for which templates need to be fetched

        Returns:
            List : List of all the template meta data for the given company_id.

        Examples:
            >>> TemplateMaster.db_get_pending_templates_data(3)
            >>> []

    """
    linked_packs_list: List[int] = []
    change_rx_comment_list: List[str] = []
    try:
        TemplateMasterAlias = TemplateMaster.alias()
        pending_template_status = settings.PENDING_PROGRESS_TEMPLATE_LIST
        pending_template_data = []
        hoa_date_list = defaultdict(set)

        current_date = get_current_date()
        previous_date = datetime.datetime.strptime(current_date, '%Y-%m-%d') - datetime.timedelta(days=60)
        # if optimization is needed in sub_q 3 filter based on admin dates by adding
        # packdetails.consumption_start_date > previous date

        template_data = TemplateMaster.select(TemplateMaster.patient_id,
                                              TemplateMaster.file_id).dicts() \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMaster.status << pending_template_status)

        file_patient_list = list()
        patient_ids = list()

        # fetching patient_file info to filter temp_slot_info and patinet_ids to filter packs info
        for record in template_data:
            file_patient_list.append('{}#{}'.format(record['patient_id'], record['file_id']))
            patient_ids.append(record['patient_id'])

        if not patient_ids:
            return pending_template_data
        packs_query = PackHeader.select(PackHeader.patient_id.alias('patient_id'),
                                        PackDetails.pack_display_id.alias('pack_display_id'),
                                        PackDetails.consumption_start_date.alias('consumption_start_date'),
                                        PackDetails.consumption_end_date.alias('consumption_end_date'),
                                        PackHeader.file_id.alias('file_id')) \
            .join(PackDetails,
                  on=((PackDetails.pack_header_id == PackHeader.id) &
                      (PackDetails.consumption_start_date > previous_date) &
                      (PackDetails.pack_status.not_in([settings.DELETED_PACK_STATUS])))) \
            .where(PackDetails.company_id == company_id,
                   PackHeader.patient_id << patient_ids).alias('packs_query')

        print(file_patient_list)
        sub_q_2 = TemplateMaster.select(TemplateMaster.id.alias('temp_id'),
                                        fn.GROUP_CONCAT(fn.DISTINCT(TemplateMasterAlias.id)).coerce(False)
                                        .alias('duplicate_template_ids')) \
            .join(TemplateMasterAlias, on=((TemplateMaster.patient_id == TemplateMasterAlias.patient_id) &
                                           (TemplateMasterAlias.id != TemplateMaster.id))) \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMasterAlias.status << settings.PENDING_PROGRESS_TEMPLATE_LIST,
                   TemplateMaster.status << settings.PENDING_PROGRESS_TEMPLATE_LIST) \
            .group_by(TemplateMaster.id).alias('sub_q_2')

        temp_slot_data = TempSlotInfo.select(TempSlotInfo.patient_id.alias('patient_id'),
                                             TempSlotInfo.hoa_date.alias('hoa_date'),
                                             TempSlotInfo.file_id.alias('file_id')) \
            .where(fn.CONCAT(TempSlotInfo.patient_id, '#', TempSlotInfo.file_id) << file_patient_list).alias(
            'temp_slot_data') \
            .order_by(TempSlotInfo.hoa_date)

        # query to get packs having overlapping or similar admin period for each template
        sub_q_3 = TemplateMaster.select(TemplateMaster.id.alias('temp_id'),
                                        fn.GROUP_CONCAT(fn.DISTINCT(packs_query.c.pack_display_id)).coerce(False)
                                        .alias('duplicate_pack_ids'),
                                        ) \
            .join(temp_slot_data, on=((temp_slot_data.c.file_id == TemplateMaster.file_id) &
                                      (temp_slot_data.c.patient_id == TemplateMaster.patient_id))) \
            .join(packs_query,
                  on=(
                          (TemplateMaster.patient_id == packs_query.c.patient_id) &
                          (temp_slot_data.c.hoa_date.between(packs_query.c.consumption_start_date,
                                                             packs_query.c.consumption_end_date)
                           ))) \
            .group_by(temp_slot_data.c.file_id, temp_slot_data.c.patient_id) \
            .where(TemplateMaster.company_id == company_id,
                   TemplateMaster.status << settings.PENDING_PROGRESS_TEMPLATE_LIST).alias('sub_q_3')

        sub_ext_change_rx, sub_q_4 = db_get_template_change_rx_info(company_id=company_id, file_id=0, patient_id=0)

        logger.info('main_start' + str(datetime.datetime.now()))
        query = TemplateMaster.select(TemplateMaster.status,
                                      TemplateMaster.file_id,
                                      TemplateMaster.patient_id,
                                      TemplateMaster.is_modified.alias('is_template_modified'),
                                      TemplateMaster.created_date,
                                      TemplateMaster.id.alias('template_id'),
                                      TemplateMaster.delivery_datetime,
                                      TemplateMaster.system_id,
                                      TemplateMaster.id.alias('template_id'),
                                      PatientMaster.last_name, PatientMaster.first_name,
                                      fn.IF(sub_q_2.c.duplicate_template_ids, 1, 0)
                                      .alias('duplicate_template_present'),
                                      fn.IF(sub_q_3.c.duplicate_pack_ids, 1, 0)
                                      .alias('duplicate_packs_present'),
                                      sub_q_2.c.duplicate_template_ids,
                                      sub_q_3.c.duplicate_pack_ids,
                                      PatientMaster.pharmacy_patient_id, PatientMaster.patient_no,
                                      FacilityMaster.facility_name,
                                      FacilityMaster.id.alias("facility_id"),
                                      fn.IF(TemplateMaster.task_id.is_null(False), True, False).alias('is_error'),
                                      sub_q_4.c.linked_packs.alias("linked_packs"),
                                      sub_ext_change_rx.c.change_rx_comment.alias("change_rx_comment"),
                                      CeleryTaskmeta.result.alias("template_result_message"),
                                      FacilitySchedule.start_date.alias("delivery_date"),
                                      PatientSchedule.last_import_date,
                                      PatientSchedule.delivery_date_offset,
                                      FacilitySchedule.fill_cycle,
                                      FacilitySchedule.days,
                                      PatientSchedule.id.alias("patient_schedule_id")
                                      ) \
            .join(PatientMaster, on=PatientMaster.id == TemplateMaster.patient_id) \
            .join(PatientSchedule, JOIN_LEFT_OUTER, on=((PatientMaster.id == PatientSchedule.patient_id) &
                                       (PatientMaster.facility_id == PatientSchedule.facility_id))) \
            .join(FacilitySchedule, JOIN_LEFT_OUTER, on=PatientSchedule.schedule_id == FacilitySchedule.id)  \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(sub_q_3, JOIN_LEFT_OUTER, on=sub_q_3.c.temp_id == TemplateMaster.id) \
            .join(sub_q_2, JOIN_LEFT_OUTER, on=sub_q_2.c.temp_id == TemplateMaster.id) \
            .join(sub_ext_change_rx, JOIN_LEFT_OUTER, on=sub_ext_change_rx.c.template_id == TemplateMaster.id)\
            .join(sub_q_4, JOIN_LEFT_OUTER, on=sub_q_4.c.template_id == TemplateMaster.id)\
            .join(CeleryTaskmeta, JOIN_LEFT_OUTER, on=TemplateMaster.task_id == CeleryTaskmeta.task_id) \
            .group_by(TemplateMaster.id) \
            .order_by(SQL('duplicate_packs_present').desc(),
                      SQL('duplicate_template_present').desc(), SQL('is_error').desc(),
                      SQL('FIELD(is_template_modified, 1,2,0)'), TemplateMaster.id) \
            .where((TemplateMaster.company_id == company_id) &
                   ((TemplateMaster.status << settings.PENDING_TEMPLATE_LIST) |
                    ((TemplateMaster.status == settings.PROGRESS_TEMPLATE_STATUS) & (
                            CeleryTaskmeta.status != settings.PENDING_TEMPLATE_TASK_IN_TASK_QUEUE))))
        for record in query.dicts():
            record["template_result_message"] = decode_celery_result(record["template_result_message"]) if record[
                "is_error"] else None
            record["patient_name"] = record["last_name"] + ", " + record["first_name"]
            record["admin_date_list"] = list()
            temp_slot_data_2 = TempSlotInfo.select(TempSlotInfo.patient_id.alias('patient_id'),
                                                   TempSlotInfo.hoa_date.alias('hoa_date'),
                                                   TempSlotInfo.file_id.alias('file_id')) \
                .where(TempSlotInfo.patient_id == record['patient_id'], TempSlotInfo.file_id == record['file_id']) \
                .order_by(TempSlotInfo.hoa_date).alias('temp_slot_data_2')
            for temp in list(temp_slot_data_2):
                if temp.patient_id_id == record["patient_id"] and temp.file_id_id == record["file_id"]:
                    hoa_date = temp.hoa_date.strftime('%m-%d-%y')
                    if hoa_date not in record["admin_date_list"]:
                        record["admin_date_list"].append(hoa_date)

            if not record.get("admin_date_list", None):
                continue
            record["admin_period"] = str(
                record["admin_date_list"][0] + "  to  " + record["admin_date_list"][
                    len(record["admin_date_list"]) - 1])
            record['delivery_datetime'] = str(record['delivery_datetime']) if record['delivery_datetime'] else None
            record["admin_start_date"] = record["admin_date_list"][0]
            record["admin_end_date"] = record["admin_date_list"][len(record["admin_date_list"]) - 1]

            linked_packs_list = []
            if record["linked_packs"] is not None:
                linked_packs_list = list(map(lambda x: int(x), record["linked_packs"].split(',')))
            record["linked_packs"] = linked_packs_list

            change_rx_comment_list = []
            if record["change_rx_comment"] is not None:
                change_rx_comment_list = record["change_rx_comment"].split(',')
            record["change_rx_comment"] = change_rx_comment_list

            pending_template_data.append(record)
        logger.info('main_end' + str(datetime.datetime.now()))
        return pending_template_data

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error(e, exc_info=True)
        raise Exception


@log_args_and_response
def db_get_file_patient(templatelist, company_id, is_modified):
    """ Returns True if template list is generated for given company_id and having particular status,
        False otherwise

    :param templatelist:
    :param company_id:
    :param is_modified:
    :return: Boolean
    """
    patient_file_dict = defaultdict(list)
    company_id = int(company_id)
    try:
        if CeleryTaskmeta.table_exists():
            template_data = TemplateMaster.select().dicts() \
                .join(CeleryTaskmeta, JOIN_LEFT_OUTER, on=TemplateMaster.task_id == CeleryTaskmeta.task_id) \
                .where(TemplateMaster.id << templatelist,
                       TemplateMaster.company_id == company_id,
                       (TemplateMaster.status << settings.PENDING_TEMPLATE_LIST) |
                       ((TemplateMaster.status == settings.PROGRESS_TEMPLATE_STATUS) &
                        (CeleryTaskmeta.status != settings.PENDING_TEMPLATE_TASK_IN_TASK_QUEUE)),
                       TemplateMaster.is_modified << is_modified
                       )
        else:
            template_data = TemplateMaster.select().dicts() \
                .where(TemplateMaster.id << templatelist,
                       TemplateMaster.company_id == company_id,
                       (TemplateMaster.status << settings.PENDING_PROGRESS_TEMPLATE_LIST),
                       TemplateMaster.is_modified << is_modified
                       )
        print(template_data)
        for record in template_data:
            patient_file_dict[record['patient_id']].append(record['file_id'])
        return patient_file_dict
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_update_pending_progress_templates_by_status(status, reason, user_id, template_ids, company_id):
    try:
        return TemplateMaster.db_update_pending_progress_templates_by_status(status=status, reason=reason,
                                                                             user_id=user_id, template_ids=template_ids,
                                                                             company_id=company_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_delete_templates_by_patient_file_ids(patient_id, file_ids):
    try:
        return TemplateDetails.db_delete_templates_by_patient_file_ids(patient_id=patient_id, file_ids=file_ids)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_delete_temp_slot_by_patient_file_ids(patient_id, file_ids):
    try:
        TempSlotInfo.db_delete_by_patient_file_ids(patient_id=patient_id, file_ids=file_ids)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_file_id_from_template_ids_dao(template_ids, status):
    try:
        return TemplateMaster.db_get_file_id_from_template_ids(template_ids=template_ids, status=status)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_template_by_rolled_back_file_ids(rolled_back_file_ids, other_template_status):
    try:
        return TemplateMaster.db_get_file_ids(file_ids=list(rolled_back_file_ids), status=other_template_status)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_update_rollback_files(to_be_rolled_back_files, status, reason):
    try:
        return FileHeader.db_update(file_ids=list(to_be_rolled_back_files), status=status, message=reason)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_template_master_by_patient_and_file_dao(patient_id, file_id):
    try:
        return TemplateMaster.db_get_template_master_by_patient_and_file(patient_id=patient_id, file_id=file_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_compare_min_admin_date_with_current_date(patient_id, file_id, start_date=None, current_date=None):
    try:
        min_date = TempSlotInfo.select(fn.MIN(TempSlotInfo.hoa_date)).where(TempSlotInfo.patient_id == patient_id,
                                                                            TempSlotInfo.file_id == file_id).scalar()

        is_scheduled = PatientMaster.select(PatientSchedule.schedule_id) \
            .join(PatientSchedule, on=((PatientSchedule.patient_id == PatientMaster.id) & (
                PatientSchedule.facility_id == PatientMaster.facility_id))) \
            .where(PatientMaster.id == patient_id).scalar()
        if start_date:
            if min_date.strftime("%Y-%m-%d") >= start_date:
                return start_date
            else:
                return min_date.strftime("%Y-%m-%d")
        if is_scheduled:
            return settings.SUCCESS_RESPONSE
            # if patient already scheduled no need to auto schedule
        if min_date.strftime("%Y-%m-%d") < current_date:
            return settings.FAILURE_RESPONSE
            # if admin date is past, we will just stop the user on DDT
        if min_date.strftime("%Y-%m-%d") == current_date:
            return current_date
            # if admin start date is today, we schedule the patient for today's delivery
        else:
            return (min_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            # if admin start date is in future, we schedule the patient on admin start date's one day before
        return False
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_setting_previous_facility_schedule_for_new_patient(patient_id, facility_id=None, schedule_id=None,
                                                          delivery_date_offset=None, user_id=None, start_date=None):
    try:
        if schedule_id:
            created = PatientSchedule.insert(facility_id=facility_id, patient_id=patient_id,
                                             schedule_id=schedule_id, total_packs=0,
                                             delivery_date_offset=delivery_date_offset,
                                             active=1, patient_overwrite=1).execute()
            return True
        query = PatientMaster.select(PatientSchedule).dicts() \
            .join(PatientSchedule, on=PatientSchedule.facility_id == PatientMaster.facility_id) \
            .join(FacilitySchedule, on=FacilitySchedule.id == PatientSchedule.schedule_id) \
            .where(PatientMaster.id == patient_id, PatientSchedule.active == 1)
        if query.exists():
            for record in query:
                created = PatientSchedule.insert(facility_id=record["facility_id"], patient_id=patient_id,
                                                 schedule_id=record["schedule_id"], total_packs=0,
                                                 delivery_date_offset=record["delivery_date_offset"],
                                                 active=1).execute()
                break
            return True
        else:
            schedule_info = {
                'fill_cycle': constants.FILL_CYCLE_WEEKLY,
                'start_date': start_date,
                'days': None,
                'created_by': user_id,
                'modified_by': user_id}
            record = db_add_facility_schedule_dao(schedule_info)
            facility_id = PatientMaster.select(PatientMaster.facility_id).where(PatientMaster.id == patient_id).scalar()
            update_dict = {"schedule_id": record.id,
                           "total_packs": 0,
                           "delivery_date_offset": 0,
                           "active": 1
                           }
            create_dict = {"patient_id": patient_id,
                           "facility_id": facility_id
                           }
            created = PatientSchedule.db_update_or_create(create_dict, update_dict)
            if not created:
                return False
            return True
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_update_patient_schedule(patient_schedule_ids, delivery_date_offset=None, fill_cycle=None, user_id=None, days=None, start_date=None):
    try:
        current_date_time = get_current_date_time()
        record = PatientSchedule.update(delivery_date_offset=delivery_date_offset,
                                        modified_date=current_date_time).where(
            PatientSchedule.id.in_(patient_schedule_ids)).execute()
        schedule_id = PatientSchedule.select(PatientSchedule.schedule_id).where(
            PatientSchedule.id.in_(patient_schedule_ids)).scalar()
        if days:
            update = FacilitySchedule.update(fill_cycle=fill_cycle, modified_date=current_date_time,
                                             modified_by=user_id,
                                             days=days, start_date=start_date).where(
                FacilitySchedule.id == schedule_id).execute()
        else:
            update = FacilitySchedule.update(fill_cycle=fill_cycle, modified_date=current_date_time,
                                             modified_by=user_id, start_date=start_date).where(
                FacilitySchedule.id == schedule_id).execute()
        return True
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


def get_template_canisters(file_id, patient_id, company_id):
    """
    Yields canister records for drugs present for given patient_id and file_id
    :param file_id:
    :param patient_id:
    :param company_id:
    :return:
    """

    DrugMasterAlias = DrugMaster.alias()
    sub_q = TempSlotInfo.select(
        fn.CONCAT(DrugMasterAlias.formatted_ndc, '#', fn.IFNULL(DrugMasterAlias.txr, '')).alias('fndc_txr')
    ).distinct() \
        .join(PatientRx, on=PatientRx.id == TempSlotInfo.patient_rx_id) \
        .join(DrugMasterAlias, on=DrugMasterAlias.id == PatientRx.drug_id) \
        .where(TempSlotInfo.patient_id == patient_id,
               TempSlotInfo.file_id == file_id)
    select_fields = [CanisterMaster.id.alias('canister_id'),
                     CanisterMaster.available_quantity,
                     fn.IF(CanisterMaster.available_quantity < 0, 0, CanisterMaster.available_quantity).alias(
                         'display_quantity'),
                     LocationMaster.location_number,
                     CanisterMaster.rfid,
                     DrugMaster.drug_name,
                     DrugMaster.strength_value,
                     DrugMaster.strength,
                     DrugMaster.formatted_ndc,
                     DrugMaster.txr,
                     DrugMaster.imprint,
                     DrugMaster.image_name,
                     DrugMaster.shape,
                     DrugMaster.color,
                     DrugMaster.manufacturer,
                     DrugMaster.ndc,
                     LocationMaster.location_number,
                     ContainerMaster.drawer_name.alias('drawer_number'),
                     LocationMaster.display_location,
                     fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.id.is_null(True), 'null', ZoneMaster.id)),
                                            SQL(" SEPARATOR ' & ' "))).coerce(False).alias('zone_id'),
                     fn.GROUP_CONCAT(Clause(fn.DISTINCT(fn.IF(ZoneMaster.name.is_null(True),
                                                              'null', ZoneMaster.name)),
                                            SQL(" SEPARATOR ' & ' "))).coerce(
                         False).alias('zone_name'),
                     DeviceLayoutDetails.id.alias('device_layout_id'),
                     DeviceMaster.name.alias('device_name'),
                     DeviceMaster.id.alias('device_id'),
                     DeviceTypeMaster.device_type_name,
                     DeviceTypeMaster.id.alias('device_type_id'),
                     ContainerMaster.ip_address,
                     ContainerMaster.secondary_ip_address,
                     DeviceMaster.system_id,
                     # fn.GROUP_CONCAT(Clause(fn.CONCAT(DeviceMaster.name,
                     #                                  ' ',
                     #                                  LocationMaster.display_location,
                     #
                     #                                  ),
                     #                        SQL(" SEPARATOR ', ' "))).coerce(False).alias('canister_list')
                     ]
    clauses = [CanisterMaster.active == settings.is_canister_active,
               CanisterMaster.company_id == company_id,
               fn.CONCAT(DrugMaster.formatted_ndc, '#', fn.IFNULL(DrugMaster.txr, '')) << sub_q]
    query = CanisterMaster.select(*select_fields) \
        .join(DrugMaster, on=DrugMaster.id == CanisterMaster.drug_id) \
        .join(LocationMaster, JOIN_LEFT_OUTER, on=CanisterMaster.location_id == LocationMaster.id) \
        .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
        .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id) \
        .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
        .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
        .join(CanisterZoneMapping, JOIN_LEFT_OUTER, CanisterZoneMapping.canister_id == CanisterMaster.id) \
        .join(ZoneMaster, JOIN_LEFT_OUTER, ZoneMaster.id == CanisterZoneMapping.zone_id) \
        .where(*clauses)
    query = query.group_by(CanisterMaster.id)
    try:
        for record in query.dicts():
            yield record
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


def get_store_separate_drugs_dao(request_params):
    """
    to get get_store_separate_drugs_dao
    @param request_params:
    @return:
    """
    try:
        company_id = request_params['company_id']
        filter_fields = request_params.get('filter_fields', None)
        sort_fields = request_params.get('sort_fields', None)
        paginate = request_params.get('paginate', None)
        fields_dict = {'drug_name': DrugMaster.concated_drug_name_field(),
                       'ndc': DrugMaster.ndc,
                       'imprint': DrugMaster.imprint,
                       'color': DrugMaster.color,
                       'shape': DrugMaster.shape,
                       'drug_form': DrugMaster.drug_form,
                       'image_name': DrugMaster.image_name,
                       'dosage_type_name': DosageType.name,
                       'dosage_type_code': DosageType.code,
                       # 'note': StoreSeparateDrug.note,
                       'store_separate_drug_id': StoreSeparateDrug.id
                       }
        select_fields = [v.alias(k) for k, v in fields_dict.items()]
        like_search_list = ['drug_name', 'ndc', 'color', 'drug_form',
                            'note', 'dosage_type_name', 'dosage_type_code']
        between_search_list = []
        exact_search_list = []
        membership_search_list = ['store_separate_drug_id']
        clauses = list()
        clauses.append((StoreSeparateDrug.company_id == company_id))
        query = StoreSeparateDrug.select(*select_fields) \
            .join(UniqueDrug, on=UniqueDrug.id == StoreSeparateDrug.unique_drug_id) \
            .join(DrugMaster, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)
                                  & (DrugMaster.txr == UniqueDrug.txr))) \
            .join(DosageType, JOIN_LEFT_OUTER, on=DosageType.id == StoreSeparateDrug.dosage_type_id) \
            .group_by(StoreSeparateDrug.id)
        results, count = get_results(query.dicts(), fields_dict, clauses=clauses,
                                     filter_fields=filter_fields,
                                     sort_fields=sort_fields,
                                     paginate=paginate,
                                     exact_search_list=exact_search_list,
                                     like_search_list=like_search_list,
                                     between_search_list=between_search_list,
                                     membership_search_list=membership_search_list,
                                     last_order_field=[fields_dict['store_separate_drug_id']])
        return count, results

    except (InternalError, IntegrityError, ValueError) as e:
        logger.error("error in get_store_separate_drugs_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_store_separate_drugs_dao {}".format(e))
        raise e


def get_rollback_templates_dao(company_id, filter_fields, paginate, sort_fields, time_zone):
    try:
        CHAR = 'CHAR'
        fields_dict = {
            'modified_datetime': cast(fn.CONVERT_TZ(TemplateMaster.modified_date, settings.TZ_UTC, time_zone), CHAR),
            'modified_time': cast(fn.TIME(fn.CONVERT_TZ(TemplateMaster.modified_date, settings.TZ_UTC, time_zone)), 'CHAR'),
            'modified_date': fn.DATE(fn.CONVERT_TZ(TemplateMaster.modified_date, settings.TZ_UTC, time_zone)),
            'modified_by': TemplateMaster.modified_by,
            'reason': TemplateMaster.reason,
            'template_id': TemplateMaster.id,
            'patient_name': PatientMaster.concated_patient_name_field(),
            'patient_no': PatientMaster.patient_no,
            'system_id': TemplateMaster.system_id
        }
        select_fields = [v.alias(k) for k, v in fields_dict.items()]
        like_search_list = ['patient_name', 'patient_no', 'reason']
        between_search_list = ['modified_date', 'modified_datetime', 'modified_time']
        exact_search_list = []
        membership_search_list = ['system_id', 'template_id']
        clauses = [
            (TemplateMaster.status == settings.UNGENERATED_TEMPLATE_STATUS),
            (TemplateMaster.company_id == company_id),
        ]
        order_list = list()
        if sort_fields:
            order_list.extend(sort_fields)
        query = TemplateMaster.select(*select_fields) \
            .join(PatientMaster, on=PatientMaster.id == TemplateMaster.patient_id)
        results, count = get_results(query.dicts(), fields_dict, clauses=clauses,
                                     filter_fields=filter_fields,
                                     sort_fields=order_list,
                                     paginate=paginate,
                                     exact_search_list=exact_search_list,
                                     like_search_list=like_search_list,
                                     between_search_list=between_search_list,
                                     membership_search_list=membership_search_list,
                                     last_order_field=[fields_dict['modified_datetime'].desc()])
        return count, results

    except (InternalError, IntegrityError, ValueError) as e:
        logger.error("error in get_rollback_templates_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_rollback_templates_dao {}".format(e))
        raise e


@log_args_and_response
def get_take_away_template_by_patient_dao(patient_id):
    try:
        return TakeawayTemplate.db_get_take_away_template_by_patient(patient_id=patient_id)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_take_away_template_by_patient_dao {}".format(e))
        raise e


@log_args_and_response
def template_get_status_dao(file_id, patient_id):
    try:
        return TemplateMaster.db_get_status(file_id=file_id, patient_id=patient_id)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in template_get_status_dao {}".format(e))
        raise e


@log_args_and_response
def get_template_id_dao(file_id, patient_id):
    try:
        return TemplateMaster.db_get_template_id(file_id=file_id, patient_id=patient_id)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_template_id_dao {}".format(e))
        raise e


@log_args_and_response
def get_template_flags(file_id, patient_id):
    try:
        result = TemplateMaster.select().where(TemplateMaster.file_id == file_id,
                                               TemplateMaster.patient_id == patient_id).get()
        return result.pack_type_id, result.customized, result.seperate_pack_per_dose, result.true_unit, result.is_bubble
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_template_flags {}".format(e))
        raise e


@log_args_and_response
def is_other_template_pending_dao(file_id, patient_id):
    try:
        return TemplateMaster.is_other_template_pending(file_id=file_id, patient_id=patient_id)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in is_other_template_pending_dao {}".format(e))
        raise e


@log_args_and_response
def get_template_file_id_dao(patient_id, status):
    try:
        return TemplateMaster.db_get_file_id(patient_id=patient_id, status=status)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_template_file_id_dao {}".format(e))
        raise e


@log_args_and_response
def update_modification_status_dao(patient_id, file_id, modification_status):
    try:
        return TemplateMaster.db_update_modification_status(patient_id, file_id, modification_status)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in update_modification_status_dao {}".format(e))
        raise e


@log_args_and_response
def update_template_status_with_template_id(template_id, update_dict):
    """
    update dict by template id
    @param template_id:
    @param update_dict:
    @return:
    """
    try:
        return TemplateMaster.db_update_status_with_id(template_id=template_id, update_dict=update_dict)

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in update_template_status_with_template_id {}".format(e))
        raise e


@log_args_and_response
def get_template_id_from_display_id(pack_display_id):

    try:
        template_id = None
        query = TemplateMaster.select(TemplateMaster.id).dicts() \
                .join(PackHeader, JOIN_LEFT_OUTER, on=((PackHeader.patient_id == TemplateMaster.patient_id) & (PackHeader.file_id == TemplateMaster.file_id))) \
                .join(PackDetails, JOIN_LEFT_OUTER, on=PackDetails.pack_header_id == PackHeader.id) \
                .where((PackDetails.pack_display_id.in_(pack_display_id) | TemplateMaster.pharmacy_fill_id.in_(pack_display_id))) \
                .group_by(TemplateMaster.id)
        for data in query:
            template_id = data["id"]
            return template_id
        return template_id
    except DoesNotExist as e:
        return False
    except Exception as e:
        logger.info(f"In validate_template_id, e: {e}")
        raise e
