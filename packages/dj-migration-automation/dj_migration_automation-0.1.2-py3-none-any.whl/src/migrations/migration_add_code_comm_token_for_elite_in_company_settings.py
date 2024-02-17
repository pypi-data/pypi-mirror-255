from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, DecimalField, CharField

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants
from src.model.model_company_setting import CompanySetting


def migration_add_code_elite_comm_token_in_company_settings():

    try:

        init_db(db, 'database_migration')
        row_data = [
            {
                "company_id": 3,
                "name": "EPBM_COMM_TOKEN",
                "value": 1234,
                "created_by": 2,
                "modified_by": 2
            }
            ]
        if CompanySetting.table_exists():
            CompanySetting.insert_many(row_data).execute()
            print("Added buffer for branded canister")
    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    migration_add_code_elite_comm_token_in_company_settings()