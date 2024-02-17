from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_testing_status import CanisterTestingStatus
from src.model.model_drug_master import DrugMaster


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class CanisterTestingData(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster, null=False)
    drug_id = ForeignKeyField(DrugMaster, null=False)
    status_id = ForeignKeyField(CodeMaster, null=False)
    reason = TextField(null=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_testing_data"

# def migration_canister_testing():
#     init_db(db, 'database_migration')
#
#     if not CanisterTestingData.table_exists():
#         db.create_tables([CanisterTestingData], safe=True)
#         print('Table created: CanisterTestingData')
#     if not CanisterTestingStatus.table_exists():
#         db.create_tables([CanisterTestingStatus], safe=True)
#         print('Table created: CanisterTestingStatus')
#
#     if GroupMaster.table_exists():
#         GroupMaster.insert(id=constants.CANISTER_TESTING_GROUP_ID, name="CanisterTesting").execute()
#     if CodeMaster.table_exists():
#         CodeMaster.insert(id=constants.CANISTER_TESTING_PASS, group_id=constants.CANISTER_TESTING_GROUP_ID,
#                           value='Canister Testing Pass').execute()
#         CodeMaster.insert(id=constants.CANISTER_TESTING_FAIL, group_id=constants.CANISTER_TESTING_GROUP_ID,
#                           value='Canister Testing Fail').execute()
#     print("Insertion in Group Master and Code Master completed.")


def migration_canister_testing_db_changes():
    init_db(db, 'database_migration')

    if CanisterTestingStatus.table_exists():
        db.drop_table(CanisterTestingStatus)
        print("Tables dropped: CanisterTestingStatus")

    if CanisterTestingData.table_exists():
        db.drop_table(CanisterTestingData)
        print("Tables dropped: CanisterTestingStatus")

    if not CanisterTestingStatus.table_exists():
        db.create_tables([CanisterTestingStatus], safe=True)
        print('Table created: CanisterTestingStatus')


if __name__ == '__main__':
    # migration_canister_testing()
    migration_canister_testing_db_changes()
