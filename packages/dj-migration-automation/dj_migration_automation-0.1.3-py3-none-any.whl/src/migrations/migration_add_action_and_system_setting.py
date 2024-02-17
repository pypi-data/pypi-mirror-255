from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


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


def migrate_system_settings(system_id, user_id):
    init_db(db, "database_migration")
    insert_in_table(system_id=system_id, user_id=user_id)


def insert_in_table(system_id, user_id):
    try:
        row_data = [
            {
                "system_id": system_id,
                "name": "AUTOMATIC_DAY_END_TIME",
                "value": 20.30,
                "created_by": user_id,
                "modified_by": user_id
            }
        ]

        SystemSetting.insert_many(row_data).execute()
        print('System settings initial data inserted')

        ACTION_MASTER_DATA = [
            dict(id=50, group_id=11,
                 value="Skip for Packs")
        ]

        ActionMaster.insert_many(ACTION_MASTER_DATA).execute()
        print('ActionMaster initial data inserted')

    except Exception as e:
        print(e)


if __name__ == '__main__':
    migrate_system_settings(system_id=14, user_id=2)
