from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings

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

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "company_setting"
        indexes = (
            (('company_id', 'name'), True),
            # keep trailing comma as suggested by peewee doc # unique setting per company
        )


def migrate_company_settings():
    init_db(db, "database_migration")
    insert_in_table(company_id = 4, user_id = 3)


def insert_in_table(company_id, user_id):
    try:
        row_data = [
            {
                 "company_id": company_id,
                "name": "MANUAL_PER_DAY_HOURS",
                "value": 8,
                "created_by": user_id,
                "modified_by": user_id
            },
            {
                 "company_id": company_id,
                "name": "MANUAL_PER_HOUR",
                "value": 8,
                "created_by": user_id,
                "modified_by": user_id
            },
            {
                "company_id": company_id,
                "name": "MANUAL_SUNDAY_HOURS",
                "value": 1,
                "created_by": user_id,
                "modified_by": user_id
            },
            {
                "company_id": company_id,
                "name": "MANUAL_SATURDAY_HOURS",
                "value": 4,
                "created_by": user_id,
                "modified_by": user_id
            },
        ]

        CompanySetting.insert_many(row_data).execute()
        print('Company settings initial data inserted')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    migrate_company_settings()