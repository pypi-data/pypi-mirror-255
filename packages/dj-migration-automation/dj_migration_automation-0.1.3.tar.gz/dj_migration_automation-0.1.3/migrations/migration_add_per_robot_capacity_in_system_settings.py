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
    init_db(db, "database_migration")
    insert_in_table(system_id=2, user_id=3)


def insert_in_table(system_id, user_id):
    try:
        row_data = {
                "system_id": system_id,
                "name": "DEFAULT_AUTOMATIC_PER_HOUR_PER_ROBOT",
                "value": 10,
                "created_by": user_id,
                "modified_by": user_id
            }
        SystemSetting.insert(row_data).execute()
        print('In System_settings: a record DEFAULT_AUTOMATIC_PER_HOUR_PER_ROBOT inserted')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    migrate_system_settings()
