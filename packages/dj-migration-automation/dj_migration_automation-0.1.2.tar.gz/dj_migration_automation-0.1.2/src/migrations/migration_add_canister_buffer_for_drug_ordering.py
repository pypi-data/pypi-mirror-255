from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, DecimalField, CharField

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants

class CompanySetting(BaseModel):
    """ stores setting for a company """
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField()
    value = CharField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    # Constant for template_settings
    SLOT_VOLUME_THRESHOLD_MARK = 'SLOT_VOLUME_THRESHOLD_MARK'
    SPLIT_STORE_SEPARATE = 'SPLIT_STORE_SEPARATE'
    VOLUME_BASED_TEMPLATE_SPLIT = 'VOLUME_BASED_TEMPLATE_SPLIT'
    COUNT_BASED_TEMPLATE_SPLIT = 'COUNT_BASED_TEMPLATE_SPLIT'
    TEMPLATE_SPLIT_COUNT_THRESHOLD = 'TEMPLATE_SPLIT_COUNT_THRESHOLD'
    SLOT_COUNT_THRESHOLD = 'SLOT_COUNT_THRESHOLD'
    TEMPLATE_AUTO_SAVE = 'TEMPLATE_AUTO_SAVE'
    MAX_SLOT_VOLUME_THRESHOLD_MARK = 'MAX_SLOT_VOLUME_THRESHOLD_MARK'
    MANUAL_PER_DAY_HOURS = "MANUAL_PER_DAY_HOURS"
    MANUAL_PER_HOUR = "MANUAL_PER_HOUR"
    MANUAL_SUNDAY_HOURS = "MANUAL_SUNDAY_HOURS"
    MANUAL_SATURDAY_HOURS = "MANUAL_SATURDAY_HOURS"
    MANUAL_USER_COUNT = "MANUAL_USER_COUNT"

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "company_setting"
        indexes = (
            (('company_id', 'name'), True),
            # keep trailing comma as suggested by peewee doc # unique setting per company
        )



def migration_add_canister_buffer_to_company_settings():

    try:

        init_db(db, 'database_migration')
        row_data = [


            {
                "company_id": 3,
                "name": "BUFFER_FOR_FAST_MOVING_BRANDED",
                "value": 1,
                "created_by": 2,
                "modified_by": 2
            },
            {
                "company_id": 3,
                "name": "BUFFER_FOR_MEDIUM_FAST_MOVING_BRANDED",
                "value": 1,
                "created_by": 2,
                "modified_by": 2
            },
            {
                "company_id": 3,
                "name": "BUFFER_FOR_MEDIUM_SLOW_MOVING_BRANDED",
                "value": 1,
                "created_by": 2,
                "modified_by": 2
            },
            {
                "company_id": 3,
                "name": "BUFFER_FOR_SLOW_MOVING_BRANDED",
                "value": 1,
                "created_by": 2,
                "modified_by": 2
            },
        ]


        if CompanySetting.table_exists():
            CompanySetting.insert_many(row_data).execute()
            print("Added buffer for branded canister")



    except Exception as e:
        print(e)
        raise



if __name__ == "__main__":
    migration_add_canister_buffer_to_company_settings()

