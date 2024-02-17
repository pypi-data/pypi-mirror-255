import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from peewee import *


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    # key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


def add_batch_status():
    init_db(db, 'database_migration')

    CODE_MASTER_DATA = [
        dict(id=settings.BATCH_MFD_USER_ASSIGNED, group_id=settings.BATCH_GROUP_CODE, value="Mfd User Assigned"),
    ]

    CodeMaster.insert_many(CODE_MASTER_DATA).execute()

    print("Table modified: CodeMaster")


if __name__ == '__main__':
    add_batch_status()