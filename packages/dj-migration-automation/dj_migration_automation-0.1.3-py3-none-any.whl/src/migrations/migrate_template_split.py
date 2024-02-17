from datetime import date, datetime
from typing import List

from peewee import *

import settings
from src.dao.template_dao import db_get_saved_template
from src.model.model_company_setting import CompanySetting

from src.model.model_patient_master import PatientMaster
from src.model.model_file_header import FileHeader
from src.model.model_temp_slot_info import TempSlotInfo
from src.service.generate_templates import db_get_split_info_threshold_and_max_threshold
from collections import defaultdict

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_template_details import TemplateDetails
from src.model.model_template_master import TemplateMaster


def change_default_setting(company_ids=None):
    if not company_ids:
        company_ids = [3]
    try:
        status_1 = CompanySetting.update(value=0.60)\
            .where(CompanySetting.company_id << company_ids,
                   CompanySetting.name == 'MAX_SLOT_VOLUME_THRESHOLD_MARK').execute()
        print('setting update status', status_1)
        status_2 = CompanySetting.update(value=0.46) \
            .where(CompanySetting.company_id << company_ids,
                   CompanySetting.name == 'SLOT_VOLUME_THRESHOLD_MARK').execute()
        print('setting update status', status_2)
    except (InternalError, IntegrityError) as e:
        print(e)
        raise e


def remove_extra_data(company_ids=None):
    invalid_data = list()
    if not company_ids:
        company_ids = [3]
    try:
        query = TemplateDetails.select(TemplateDetails.file_id,
                                       TemplateDetails.patient_id).dicts() \
            .join(PatientMaster, on=PatientMaster.id == TemplateDetails.patient_id)\
            .where(PatientMaster.company_id << company_ids)\
            .group_by(TemplateDetails.patient_id) \
            .having(fn.COUNT(fn.DISTINCT(TemplateDetails.file_id)) != 1)
        for base_record in query:
            patient_id = base_record['patient_id']
            file_id = base_record['file_id']
            invalid_data.append(patient_id)

        if invalid_data:
            status = TemplateDetails.delete()\
                .where(TemplateDetails.patient_id << invalid_data).execute()
            print('deleted incorrect data ', status)
        else:
            print('no incorrect data found')

    except (InternalError, IntegrityError) as e:
        print(e)
        raise e


def update_data(company_ids=None):
    different_patient_file = list()
    same_patient_file = list()
    patient_list_template_update: List[int] = []

    if not company_ids:
        company_ids = [3]
    try:

        # Find the last templates for any patient from last 1 year and determine if there exists any
        # issue with pack split by slot threshold of 6 vs 10
        last_year_date = date(datetime.now().year - 1, datetime.now().month, datetime.now().day)
        max_template = TemplateMaster.select(TemplateMaster.patient_id.alias("patient_id"),
                                             fn.MAX(TemplateMaster.id).alias("last_template")) \
            .where(fn.DATE(TemplateMaster.created_date) >= last_year_date) \
            .group_by(TemplateMaster.patient_id).alias("max_template")

        query = TemplateDetails.select(TemplateDetails.file_id,
                                       TemplateMaster.id.alias('template_master_id'),
                                       TemplateMaster.company_id,
                                       # FileHeader.company_id,
                                       TemplateDetails.patient_id).dicts() \
            .join(max_template, on=TemplateDetails.patient_id == max_template.c.patient_id) \
            .join(TemplateMaster, on=max_template.c.last_template == TemplateMaster.id) \
            .join(TempSlotInfo, on=((TemplateMaster.patient_id == TempSlotInfo.patient_id) &
                                    (TemplateMaster.file_id == TempSlotInfo.file_id))) \
            .where(TemplateMaster.company_id << company_ids) \
            .group_by(TemplateDetails.patient_id) \
            .having(fn.COUNT(fn.DISTINCT(TemplateDetails.file_id)) == 1)

        for base_record in query:
            patient_id = base_record['patient_id']
            file_id = base_record['file_id']
            company_id = base_record['company_id']
            template_master_id = base_record['template_master_id']
            patient_file = '{}#{}'.format(patient_id, file_id)

            new_template_data = defaultdict(list)
            new_temp_hoa_rx_data = list()
            saved_temp_hoa_rx_data = list()
            saved_template_data = defaultdict(list)

            split_args = {
                'file_id': file_id,
                'patient_id': patient_id,
                'company_id': company_id,
                'template_id': template_master_id,
            }
            # template_response = get_split_data(split_args)
            template_response = db_get_split_info_threshold_and_max_threshold(patient_id=patient_id, file_id=file_id,
                                                                              company_id=company_id,
                                                                              template_id=template_master_id)
            existing_template = db_get_saved_template(patient_id=patient_id, file_id=file_id,
                                                      company_id=company_id)
            for record in template_response['template_data']:
                unique_identifier = '{}#{}'.format(record['pharmacy_rx_no'], float(record['quantity']))
                new_template_data[record['column_number']].append(unique_identifier)
            for record in existing_template:
                unique_identifier = '{}#{}'.format(record['pharmacy_rx_no'], float(record['quantity']))
                saved_template_data[record['column_number']].append(unique_identifier)
            print('For patient_id: {} file_id: {} and template_id: {} new_template_data and saved_template_data: {}'
                  .format(patient_id, file_id, template_master_id, new_template_data, saved_template_data))

            for column_number, rx_info in new_template_data.items():
                new_temp_hoa_rx_data.append(sorted(rx_info))
            for column_number, rx_info in saved_template_data.items():
                saved_temp_hoa_rx_data.append(sorted(rx_info))
            print('For patient_id: {} file_id: {} and template_id: {} short new_template_data {} and saved_template_data: {}'
                  .format(patient_id, file_id, template_master_id, new_temp_hoa_rx_data, saved_temp_hoa_rx_data))

            same_split = True
            for rx in new_temp_hoa_rx_data:
                if rx in saved_temp_hoa_rx_data:
                    saved_temp_hoa_rx_data.remove(rx)
                else:
                    same_split = False
                    break
            if same_split:
                if saved_temp_hoa_rx_data:
                    same_split = False
            if not same_split:
                different_patient_file.append(patient_file)
                patient_list_template_update.append(patient_id)
                # break
            else:
                same_patient_file.append(patient_file)

        print('different_patient_file {}'.format(different_patient_file))
        print('same_patient_file {}'.format(same_patient_file))
        if different_patient_file:
            status = TemplateDetails.delete()\
                .where(fn.CONCAT(TemplateDetails.patient_id, '#', TemplateDetails.file_id) <<
                       different_patient_file).execute()
            print('deleted data ', status)

            # Update the pending/progress templates to Yellow if they are Green and needs changes in pack split
            print('Pending Template of following patients needs to be updated: {}'.format(patient_list_template_update))
            if patient_list_template_update:
                status = TemplateMaster.update(is_modified=TemplateMaster.IS_MODIFIED_MAP["YELLOW"]) \
                    .where(TemplateMaster.patient_id << patient_list_template_update,
                           TemplateMaster.status << [settings.PENDING_TEMPLATE_STATUS,
                                                     settings.PROGRESS_TEMPLATE_STATUS],
                           TemplateMaster.is_modified == TemplateMaster.IS_MODIFIED_MAP["GREEN"]) \
                    .execute()
                print('updated data ', status)

    except (InternalError, IntegrityError) as e:
        print(e)
        raise e


def migrate_template_split(company_ids=None):
    init_db(db, "database_migration")
    update_data(company_ids)
    remove_extra_data(company_ids)
    change_default_setting(company_ids)


if __name__ == "__main__":
    migrate_template_split()
