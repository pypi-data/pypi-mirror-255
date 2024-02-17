from peewee import fn, JOIN_LEFT_OUTER, InternalError, IntegrityError

import settings
from dosepack.utilities.utils import convert_dob_date_to_sql_date, log_args_and_response
from src.api_utility import getrecords, is_date
from src.model.model_batch_master import BatchMaster
from src.model.model_code_master import CodeMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_facility_master import FacilityMaster
from src.model.model_file_header import FileHeader
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_user_map import PackUserMap
from src.model.model_partially_filled_pack import PartiallyFilledPack
from src.model.model_patient_master import PatientMaster
from src.model.model_print_queue import PrintQueue

logger = settings.logger


@log_args_and_response
def getuserpacks(filter, dataonly=False):
    try:
        query = PackDetails.select(PackDetails.filled_days,
                                   PackDetails.fill_start_date,
                                   FileHeader.created_by.alias('uploaded_by'),
                                   PackDetails.id,
                                   PackDetails.pack_display_id,
                                   PackDetails.pack_no,
                                   FileHeader.created_date,
                                   FileHeader.created_time,
                                   PackDetails.pack_status,
                                   PackDetails.system_id,
                                   PackDetails.consumption_start_date,
                                   PackDetails.consumption_end_date,
                                   PackHeader.patient_id,
                                   PatientMaster.last_name,
                                   PatientMaster.first_name,
                                   PatientMaster.patient_no,
                                   FacilityMaster.facility_name,
                                   PatientMaster.facility_id,
                                   PackDetails.order_no,
                                   PackDetails.pack_plate_location,
                                   fn.DATE(PackHeader.scheduled_delivery_date).alias('scheduled_delivery_date'),
                                   PackDetails.filled_date,
                                   PatientMaster.dob,
                                   CodeMaster.value,
                                   # CodeMaster.id.alias('pack_status_id'),
                                   PackDetails.batch_id,
                                   BatchMaster.status.alias('batch_status'),
                                   BatchMaster.name.alias('batch_name'),
                                   fields['patient_name'].alias('patient_name'),
                                   PackDetails.fill_time,
                                   fn.IF(PackUserMap.assigned_to.is_null(True), -1, PackUserMap.assigned_to).alias(
                                       'assigned_to'),
                                   fn.IF(PartiallyFilledPack.id.is_null(True), False, True).alias(
                                       'filled_partially'),
                                   fn.IF(PrintQueue.id.is_null(True), 'No', 'Yes').alias('print_requested'),

                                   PackUserMap.modified_by.alias('pack_assigned_by')).dicts() \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .join(FileHeader, on=PackHeader.file_id == FileHeader.id) \
            .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
            .join(PackRxLink, JOIN_LEFT_OUTER, PackRxLink.pack_id == PackDetails.id) \
            .join(PartiallyFilledPack, JOIN_LEFT_OUTER, PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
            .join(PrintQueue, JOIN_LEFT_OUTER, PrintQueue.pack_id == PackDetails.id) \
            .group_by(PackDetails.id)

        if "filters" in filter and filter['filters'].get('patient_name', None) is not None:
            patient_name = filter['filters']['patient_name'][1:-1]
            if is_date(patient_name):
                patient_dob = convert_dob_date_to_sql_date(patient_name)
                if patient_dob:
                    filter['filters']['patient_dob'] = patient_dob
                    filter['filters'].pop('patient_name')

            else:
                patient_no = '%' + patient_name + '%'
                query = query.where((PatientMaster.patient_no ** patient_no) | (fields['patient_name'] ** patient_no))
                filter['filters'].pop('patient_name')

        if "filters" not in filter:
            filter = {"filters": filter}
        if 'sorts' not in filter:
            filter['sorts'] = list()
        filter['sorts'].append(['id', 1])
        data = getrecords(filter, fields, query, False)
        facilities = facilitiesCount(filter, fields)
        patients = patientsCount(filter, fields)
        packs = packsCount(filter, fields)
        data["totalPatients"] = patients["totalRecords"];
        data["totalFacilities"] = facilities["totalRecords"];
        data["totalPacksCount"] = packs;
        return data
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.info("Error in db_get_half_pill_drug_drop_by_pack_id {}".format(e))
        raise


@log_args_and_response
def patientsCount(filter, fields):
    query = PackDetails.select(PatientMaster.id).distinct().dicts() \
        .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
        .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
        .join(FileHeader, on=PackHeader.file_id == FileHeader.id) \
        .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
        .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
        .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
        .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
        .join(PackRxLink, JOIN_LEFT_OUTER, PackRxLink.pack_id == PackDetails.id) \
        .join(PartiallyFilledPack, JOIN_LEFT_OUTER, PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
        .join(PrintQueue, JOIN_LEFT_OUTER, PrintQueue.pack_id == PackDetails.id)
    return getrecords(filter, fields, query, False)


@log_args_and_response
def facilitiesCount(filter, fields):
    try:
        query = PackDetails.select(FacilityMaster.id).distinct().dicts() \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .join(FileHeader, on=PackHeader.file_id == FileHeader.id) \
            .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
            .join(PackRxLink, JOIN_LEFT_OUTER, PackRxLink.pack_id == PackDetails.id) \
            .join(PartiallyFilledPack, JOIN_LEFT_OUTER, PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
            .join(PrintQueue, JOIN_LEFT_OUTER, PrintQueue.pack_id == PackDetails.id)
        return getrecords(filter, fields, query, False)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.info("Error in db_get_half_pill_drug_drop_by_pack_id {}".format(e))
        raise


@log_args_and_response
def packsCount(filter, fields):
    try:

        query = PackDetails.select(fn.COUNT(fn.DISTINCT(PackDetails.id)).alias('PackCount'),
                                   PackDetails.pack_status,
                                   ).dicts() \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .join(FileHeader, on=PackHeader.file_id == FileHeader.id) \
            .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=PackDetails.batch_id == BatchMaster.id) \
            .join(PackRxLink, JOIN_LEFT_OUTER, PackRxLink.pack_id == PackDetails.id) \
            .join(PartiallyFilledPack, JOIN_LEFT_OUTER, PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
            .join(PrintQueue, JOIN_LEFT_OUTER, PrintQueue.pack_id == PackDetails.id) \
            .group_by(PackDetails.pack_status)

        records = getrecords(filter, fields, query, False)

        result_dict = dict()
        for record in records["data"]:
            if record["pack_status"] == settings.MANUAL_PACK_STATUS:
                result_dict["Pending"] = record["PackCount"]
            elif record["pack_status"] == settings.FILLED_PARTIALLY_STATUS:
                result_dict["FilledPartially"] = record["PackCount"]
            elif record["pack_status"] == settings.PROGRESS_PACK_STATUS:
                result_dict["Progress"] = record["PackCount"]

        return result_dict
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.info("Error in db_get_half_pill_drug_drop_by_pack_id {}".format(e))
        raise


fields = {
    "facility_name": FacilityMaster.facility_name,
    "facility_id": PatientMaster.facility_id,
    "patient_id": PatientMaster.id,
    "uploaded_by": FileHeader.created_by,
    "uploaded_date": fn.DATE(FileHeader.created_date),
    "created_date": fn.DATE(PackDetails.created_date),
    "admin_date_from": fn.DATE(PackDetails.consumption_start_date),
    "admin_date_to": fn.DATE(PackDetails.consumption_end_date),
    "delivery_date": fn.DATE(PackHeader.scheduled_delivery_date),
    "status": PackDetails.pack_status,
    "patient_name": fn.Concat(PatientMaster.last_name, ', ', PatientMaster.first_name),
    "user_id": PackUserMap.assigned_to,
    "pack_display_id": fn.CONCAT('', PackDetails.pack_display_id),
    "status_name": CodeMaster.value,
    "fill_start_date": PackDetails.fill_start_date,
    "order_no": PackDetails.order_no,
    "company_id": PackDetails.company_id,
    "all_flag": fn.IF(PackUserMap.assigned_to.is_null(True), '0', '1'),
    "assigned_to": fn.IF(PackUserMap.assigned_to.is_null(True), -1, PackUserMap.assigned_to),
    "system_id": PackDetails.system_id,
    "id": PackDetails.id,
    "print_requested": fn.IF(PrintQueue.id.is_null(True), 'No', 'Yes'),
    "modified_date": PackDetails.modified_date,
    "assigned_date": PackUserMap.modified_date,
    "filled_date": PackDetails.filled_date,
    "patient_no": PatientMaster.patient_no,
    "fill_time": PackDetails.fill_time,
    "patient_dob": PatientMaster.dob,
}
drug_fields = {
    "id": DrugMaster.id,
    "ndc": DrugMaster.ndc,
    "formatted_ndc": DrugMaster.formatted_ndc,
    "is_in_stock": DrugStockHistory.is_in_stock,
    "last_updated_by": DrugStockHistory.created_by,
    "last_updated_date": DrugStockHistory.created_date,
    "last_seen_date": DrugDetails.last_seen_date,
    "last_seen_by": DrugDetails.last_seen_by,
    "pack_id": PackDetails.id,
    "drug_name": DrugMaster.drug_name,
}

@log_args_and_response
def get_patient_list():
    try:
        query = PatientMaster.select(
            fn.CONCAT(PatientMaster.last_name, ', ', PatientMaster.first_name).alias('itemName'),
            PatientMaster.dob,
            PatientMaster.patient_no,
            PatientMaster.id.alias('id')
        ).distinct().dicts() \
            .join(PackHeader, on=PatientMaster.id == PackHeader.patient_id) \
            .join(PackDetails, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id)
        return query
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.info("Error in db_get_half_pill_drug_drop_by_pack_id {}".format(e))
        raise


@log_args_and_response
def get_patient(company_id, available_only=True):
    try:
        query = PatientMaster.select(
            fn.CONCAT(PatientMaster.last_name, ', ', PatientMaster.first_name).alias('itemName'),
            PatientMaster.dob,
            PatientMaster.patient_no,
            PatientMaster.id.alias('id')
        ).distinct().dicts() \
            .join(PackHeader, on=PatientMaster.id == PackHeader.patient_id) \
            .join(PackDetails, on=PackDetails.pack_header_id == PackHeader.id)
        if available_only:
            query.where(PackDetails.pack_status != 5 and PackDetails.company_id == company_id)
        else:
            query.where(PackDetails.company_id == company_id)

        return getrecords({"sorts": [["patient_name", 1]]},
                          {"patient_name": fn.CONCAT(PatientMaster.last_name, ', ', PatientMaster.first_name)},
                          query, True)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.info("Error in db_get_half_pill_drug_drop_by_pack_id {}".format(e))
        raise


@log_args_and_response
def get_facility(company_id, available_only=True):
    try:
        query = FacilityMaster.select(
            FacilityMaster.facility_name.alias('itemName'),
            FacilityMaster.id.alias('id')
        ).distinct().dicts() \
            .join(PatientMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(PackHeader, on=PatientMaster.id == PackHeader.patient_id) \
            .join(PackDetails, on=PackDetails.pack_header_id == PackHeader.id)
        if available_only:
            query.where(PackDetails.pack_status != 5 and PackDetails.company_id == company_id)
        else:
            query.where(PackDetails.company_id == company_id)
        return getrecords({"sorts": [["facility_name", 1]]}, {"facility_name": FacilityMaster.facility_name}, query,
                          True)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.info("Error in db_get_half_pill_drug_drop_by_pack_id {}".format(e))
        raise


@log_args_and_response
def get_facility_list():
    try:
        query = FacilityMaster.select(
            FacilityMaster.facility_name.alias('itemName'),
            FacilityMaster.id.alias('id')
        ).distinct().dicts() \
            .join(PatientMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(PackHeader, on=PatientMaster.id == PackHeader.patient_id) \
            .join(PackDetails, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id)
        return query


    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.info("Error in db_get_half_pill_drug_drop_by_pack_id {}".format(e))
        raise
