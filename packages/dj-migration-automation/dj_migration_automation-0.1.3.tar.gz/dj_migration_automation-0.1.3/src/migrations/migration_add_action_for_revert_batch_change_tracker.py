from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
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


def migration_add_action_for_revert_batch_batch_change_tracker():
    init_db(db, "database_migration")
    insert_in_table()


def insert_in_table():
    try:

        ACTION_MASTER_DATA = [dict(id=51, group_id=11, value="Revert Batch or Packs")]

        ActionMaster.insert_many(ACTION_MASTER_DATA).execute()
        print('ActionMaster initial data inserted')

    except Exception as e:
        print(e)


if __name__ == '__main__':
    migration_add_action_for_revert_batch_batch_change_tracker()
