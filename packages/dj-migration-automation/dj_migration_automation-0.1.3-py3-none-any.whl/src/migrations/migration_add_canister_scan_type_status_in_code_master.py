from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'group_master'


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


def migration_add_canister_scan_type_status_in_code_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if CodeMaster.table_exists():
            CodeMaster.insert(id=constants.CANISTER_SCAN,
                              group_id=constants.SCAN_TYPE_GROUP_ID,
                              value="Canister Scan").execute()

            print("Data inserted in the CodeMaster table.")

    except Exception as e:
        settings.logger.error("Error while adding Code Master ", str(e))


if __name__ == "__main__":
    migration_add_canister_scan_type_status_in_code_master()
