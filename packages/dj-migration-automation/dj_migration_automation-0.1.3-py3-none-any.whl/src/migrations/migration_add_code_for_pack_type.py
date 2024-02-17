from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants
from src.constants import GROUP_MASTER_BATCH_MFD


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


def migration_add_pack_type_status_in_code_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if GroupMaster.table_exists():
            GroupMaster.insert(id=constants.PACK_TYPE,
                               name="PackType").execute()

            print("Data inserted in GroupMaster table.")

        if CodeMaster.table_exists():
            CodeMaster.insert(id=constants.WEEKLY_UNITDOSE_PACK,
                              group_id=constants.PACK_TYPE,
                              value="Weekly Unit dose pack").execute()
            CodeMaster.insert(id=constants.WEEKLY_MULTIDOSE_PACK,
                              group_id=constants.PACK_TYPE,
                              value="Weekly Multi dose pack").execute()

            print("Data inserted in the CodeMaster table.")

    except Exception as e:
        settings.logger.error("Error while adding Code Master ", str(e))


def migration_add_mfd_batch_pre_skipped_status_in_code_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if CodeMaster.table_exists():
            CodeMaster.insert(id=constants.MFD_BATCH_PRE_SKIPPED,
                              group_id=GROUP_MASTER_BATCH_MFD,
                              value="MfdBatchPreSkipped").execute()

            print("Data inserted in the CodeMaster table.")

    except Exception as e:
        settings.logger.error("Error while adding Code Master ", str(e))


if __name__ == "__main__":
    # migration_add_pack_type_status_in_code_master()
    migration_add_mfd_batch_pre_skipped_status_in_code_master()