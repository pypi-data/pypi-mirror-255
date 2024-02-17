from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.migrations.migrate_template_split import update_data, remove_extra_data


def migration_adjust_template_threshold_6_and_10(company_ids=None):
    init_db(db, 'database_migration')

    if not company_ids:
        company_ids = [3]

    update_data(company_ids)
    remove_extra_data(company_ids)
    print("Execution of Migration done successfully for handling the Pack Split by Slot Threshold of 6 and 10.")


if __name__ == "__main__":
    migration_adjust_template_threshold_6_and_10()
