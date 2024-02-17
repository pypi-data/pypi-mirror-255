from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings

class SystemSetting(BaseModel):
    """
        @class: SystemSetting
        @type: class
        @desc: insert data in system setting
    """
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField()
    value = CharField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "system_setting"


def migrate_system_settings():
    init_db(db, "database_t1")
    insert_in_table(system_id = 2, user_id = 3)


def insert_in_table(system_id, user_id):
    try:
        row_data = [
            {
                "system_id": system_id,
                "name": "AUTOMATIC_PER_HOUR",
                "value": 10,
                "created_by": user_id,
                "modified_by": user_id
            },
            {
                "system_id": system_id,
                "name": "AUTOMATIC_PER_DAY_HOURS",
                "value": 8,
                "created_by": user_id,
                "modified_by": user_id
            },
            {
                 "system_id": system_id,
                "name": "MANUAL_PER_DAY_HOURS",
                "value": 8,
                "created_by": user_id,
                "modified_by": user_id
            },
            {
                 "system_id": system_id,
                "name": "MANUAL_PER_HOUR",
                "value": 8,
                "created_by": user_id,
                "modified_by": user_id
            },
            {
                "system_id": system_id,
                "name": "AUTOMATIC_SATURDAY_HOURS",
                "value": 4,
                "created_by": user_id,
                "modified_by": user_id
            },
            {
                "system_id": system_id,
                "name": "AUTOMATIC_SUNDAY_HOURS",
                "value": 1,
                "created_by": user_id,
                "modified_by": user_id
            },
            {
                "system_id": system_id,
                "name": "MANUAL_SUNDAY_HOURS",
                "value": 1,
                "created_by": user_id,
                "modified_by": user_id
            },
            {
                "system_id": system_id,
                "name": "MANUAL_SATURDAY_HOURS",
                "value": 4,
                "created_by": user_id,
                "modified_by": user_id
            },
        ]

        SystemSetting.insert_many(row_data).execute()
        print('System settings initial data inserted')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    migrate_system_settings()
