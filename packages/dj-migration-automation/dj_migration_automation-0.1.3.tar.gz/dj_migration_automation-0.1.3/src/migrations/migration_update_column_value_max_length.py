import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_company_setting import CompanySetting


def update_max_length_value_column_in_company_settings():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if CompanySetting.table_exists():
            sql = 'ALTER TABLE company_setting MODIFY COLUMN value VARCHAR(400);'
            db.execute_sql(sql)
            print("Max Length of value column in company_settings is updated")
    except Exception as e:
        settings.logger.error("Error while updating column in company_settings: ", str(e))


if __name__ == "__main__":
    update_max_length_value_column_in_company_settings()
