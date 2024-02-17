from peewee import InternalError, IntegrityError, DataError, JOIN_LEFT_OUTER, fn,SQL, Clause

import settings
from drug_recom_for_big_canister import company_id
from src.model.model_facility_master import FacilityMaster
from src.model.model_facility_schedule import FacilitySchedule
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_schedule import PatientSchedule

logger = settings.logger

def update_patient_schedule_dao(update_dict, schedule_detail):
    try:
        PatientSchedule.update(schedule_id=update_dict["schedule_id"],
                               delivery_date_offset=update_dict["delivery_date_offset"],
                               modified_date=update_dict["modified_date"]) \
            .where(PatientSchedule.id << schedule_detail['patient_schedule_ids']).execute()

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_max_canister_count {}".format(e))
        raise e


def get_schedule_details_dao(company_id, facility_list = None):
    try:
        query = PatientSchedule.select(PatientSchedule,
                                       FacilitySchedule,
                                       FacilityMaster.facility_name,
                                       FacilityMaster.company_id,
                                       PatientMaster.patient_no,
                                       PatientMaster.first_name,
                                       PatientMaster.last_name,
                                       PatientSchedule.modified_date,
                                       FacilitySchedule.created_date,
                                       PatientSchedule.id.alias('patient_schedule_id'),
                                       FacilitySchedule.id.alias('facility_schedule_id'),
                                       FacilitySchedule.days,
                                       FacilitySchedule.fill_cycle).dicts() \
            .join(FacilityMaster, on=PatientSchedule.facility_id == FacilityMaster.id) \
            .join(FacilitySchedule, on=PatientSchedule.schedule_id == FacilitySchedule.id) \
            .join(PatientMaster, on=PatientMaster.id == PatientSchedule.patient_id) \
            .where(FacilityMaster.company_id == company_id,
                   PatientSchedule.active == True)

        if facility_list:
            query = query.where(FacilityMaster.id << facility_list)
        return query

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_max_canister_count {}".format(e))
        raise e


def get_calender_info_dao(company_id, facility_list = None):
    try:
        query = PatientSchedule.select(fn.COUNT(PatientSchedule.id).alias('total_patient'),
                               fn.GROUP_CONCAT(PatientSchedule.id).coerce(False).alias('patient_schedule_ids'),
                               fn.GROUP_CONCAT(Clause(fn.CONCAT(PatientMaster.last_name, ', ',
                                                                PatientMaster.first_name), SQL(" SEPARATOR ':' ")))
                               .coerce(False).alias('patient_names'),
                               fn.GROUP_CONCAT(PatientMaster.patient_no).alias('patient_nos'),
                               FacilitySchedule,
                               FacilityMaster,
                               PatientSchedule,
                               FacilitySchedule.id.alias('facility_schedule_id'),
                               fn.SUM(PatientSchedule.total_packs).alias('total_packs'),
                               FacilitySchedule.created_date).dicts() \
            .join(FacilityMaster, on=PatientSchedule.facility_id == FacilityMaster.id) \
            .join(FacilitySchedule, on=PatientSchedule.schedule_id == FacilitySchedule.id) \
            .join(PatientMaster, on=PatientMaster.id == PatientSchedule.patient_id) \
            .where(FacilityMaster.company_id == company_id, PatientSchedule.active == True) \
            .group_by(PatientSchedule.facility_id, PatientSchedule.schedule_id)
        if facility_list:
            query = query.where(FacilityMaster.id << facility_list)

        return query

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_max_canister_count {}".format(e))
        raise e


def delete_schedule_dao(update_dict, patient_schedule_id_list):
    try:
        PatientSchedule.update(schedule_id=update_dict["schedule_id"],
                               delivery_date_offset=update_dict["delivery_date_offset"],
                               modified_date=update_dict["modified_date"],
                               active=update_dict["active"]) \
            .where(PatientSchedule.id << patient_schedule_id_list).execute()

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in delete_schedule_dao {}".format(e))
        raise e


def create_patient_schedule_dao(patient_id, facility_id, total_packs):
    try:
        return PatientSchedule.db_get_or_create_schedule(patient_id, facility_id, total_packs)

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in create_patient_schedule_dao {}".format(e))
        raise e


def get_patient_schedule_data_dao(facility_id, patient_id):
    try:
        return PatientSchedule.db_get_patient_schedule_data(facility_id=facility_id, patient_id=patient_id)

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_patient_schedule_data_dao {}".format(e))
        raise e


def update_patient_schedule_data_dao(patient_schedule_id, update_dict):
    try:
        return PatientSchedule.db_update_patient_schedule_data_dao(patient_schedule_id=patient_schedule_id, update_dict=update_dict)

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in update_patient_schedule_data_dao {}".format(e))
        raise e


def get_patientwise_calender_schedule_dao(company_id, facility_list = None):
    try:
        query = PatientSchedule.select(PatientSchedule.id.alias('patient_schedule_id'),
                                       fn.CONCAT(PatientMaster.last_name, ', ',
                                                                PatientMaster.first_name).alias('patient_name'),
                                       PatientMaster.patient_no.alias('patient_no'),
                                       FacilitySchedule,
                                       FacilityMaster.facility_name,
                                       FacilityMaster.id.alias('facility_id'),
                                       PatientSchedule,
                                       FacilitySchedule.id.alias('facility_schedule_id'),
                                       PatientSchedule.total_packs.alias('packs'),
                                       FacilitySchedule.created_date).dicts() \
            .join(FacilityMaster, on=PatientSchedule.facility_id == FacilityMaster.id) \
            .join(FacilitySchedule, on=PatientSchedule.schedule_id == FacilitySchedule.id) \
            .join(PatientMaster, on=PatientMaster.id == PatientSchedule.patient_id) \
            .where(FacilityMaster.company_id == company_id, PatientSchedule.active == True) \
            .group_by(PatientSchedule.id)
        if facility_list:
            query = query.where(FacilityMaster.id << facility_list)

        return query

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_patientwise_calender_schedule_dao {}".format(e))
        raise e
