from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


def data_insertion_in_group_master_and_code_master():
    init_db(db, 'database_dp_ips')

    if GroupMaster.table_exists():
        GroupMaster.insert(id=14, name='extPackDetailsFromIPS').execute()
    if CodeMaster.table_exists():
        CodeMaster.insert(id=60, group_id=14, key=60, value='checked').execute()
        CodeMaster.insert(id=61, group_id=14, key=61, value='error').execute()
        CodeMaster.insert(id=62, group_id=14, key=62, value='fixed error').execute()
        CodeMaster.insert(id=63, group_id=14, key=63, value='filled').execute()
        CodeMaster.insert(id=64, group_id=14, key=64, value='deleted').execute()
        CodeMaster.insert(id=65, group_id=14, key=65, value='to be delivered').execute()
        CodeMaster.insert(id=66, group_id=14, key=66, value='delivered').execute()
        CodeMaster.insert(id=67, group_id=14, key=67, value='delivery cancelled').execute()
        CodeMaster.insert(id=68, group_id=1, key=68, value='RPH checked and success').execute()
        CodeMaster.insert(id=69, group_id=1, key=69, value='RPH reported error').execute()
        CodeMaster.insert(id=70, group_id=1, key=70, value='fixed errors').execute()
        CodeMaster.insert(id=71, group_id=1, key=71, value='reuse pack').execute()
        CodeMaster.insert(id=72, group_id=1, key=72, value='to be delivered').execute()
        CodeMaster.insert(id=73, group_id=1, key=73, value='delivered').execute()
    print("Insertion in Group Master and Code Master completed.")


if __name__ == "__main__":
    data_insertion_in_group_master_and_code_master()
