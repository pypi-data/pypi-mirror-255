from peewee import InternalError, IntegrityError

from dosepack.base_model.base_model import db
from model.model_init import init_db

from src.migrations.migrate_template_split import update_data, remove_extra_data
from src.model.model_company_setting import CompanySetting
from src.model.model_template_master import TemplateMaster


def update_template_split_count_threshold(company_ids=None):
    try:
        status_1 = CompanySetting.update(value=6) \
            .where(CompanySetting.company_id << company_ids,
                   CompanySetting.name == 'TEMPLATE_SPLIT_COUNT_THRESHOLD').execute()
        print('Updated Template Split Threshold Count', status_1)

    except (InternalError, IntegrityError) as e:
        print(e)


def update_template_master_yellow_status(company_ids=None):
    try:
        status_1 = TemplateMaster.update(is_modified=TemplateMaster.IS_MODIFIED_MAP['YELLOW']) \
            .where(TemplateMaster.company_id << company_ids,
                   TemplateMaster.is_modified == TemplateMaster.IS_MODIFIED_MAP['RED']).execute()
        print('Updated Template Modified Status to Yellow for any Red status.', status_1)

    except (InternalError, IntegrityError) as e:
        print(e)


def migration_update_template_split_count_threshold(company_ids=None):
    init_db(db, 'database_migration')

    if not company_ids:
        company_ids = [3]

    update_data(company_ids)
    remove_extra_data(company_ids)
    update_template_split_count_threshold(company_ids)
    update_template_master_yellow_status(company_ids)


if __name__ == "__main__":
    migration_update_template_split_count_threshold()
