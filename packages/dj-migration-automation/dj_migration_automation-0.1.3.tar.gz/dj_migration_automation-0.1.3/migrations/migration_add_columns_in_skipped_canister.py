import settings
from playhouse.migrate import *

from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from peewee import *

from src import constants
from src.model.model_skipped_canister import SkippedCanister


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


def add_column_skipped_canister():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if GroupMaster.table_exists():
            GroupMaster.insert(id=57, name='SkippedCanister').execute()

        if CodeMaster.table_exists():
            # codes for guided tracker
            CodeMaster.insert(id=constants.SKIPPED_FROM_PACK_PRE_PROCESSING, group_id=constants.GROUP_MASTER_SKIPPED_CANISTER,
                              value="Skipped From Pack Pre Processing").execute()
            CodeMaster.insert(id=constants.SKIPPED_DURING_MISSING_CANISTER, group_id=constants.GROUP_MASTER_SKIPPED_CANISTER,
                              value="Skipped during Missing Canister").execute()
            CodeMaster.insert(id=constants.SKIPPED_DURING_MISSING_PILL,
                              group_id=constants.GROUP_MASTER_SKIPPED_CANISTER,
                              value="Skipped during Missing Pill").execute()
            CodeMaster.insert(id=constants.SKIPPED_DURING_MALFUNCTION,
                              group_id=constants.GROUP_MASTER_SKIPPED_CANISTER,
                              value="Skipped during Malfunction").execute()
            CodeMaster.insert(id=constants.SKIPPED_DURING_TO_BE_REPLENISH_SCREEN,
                              group_id=constants.GROUP_MASTER_SKIPPED_CANISTER,
                              value="Skipped during To Be Replenish Screen").execute()
            print("Added codes in Code Master")

        if SkippedCanister.table_exists():
            migrate(
                migrator.add_column(SkippedCanister._meta.db_table,
                                    SkippedCanister.skipped_from.db_column,
                                    SkippedCanister.skipped_from),
                migrator.add_column(SkippedCanister._meta.db_table,
                                    SkippedCanister.skip_reason.db_column,
                                    SkippedCanister.skip_reason),
                migrator.drop_not_null(SkippedCanister._meta.db_table,
                                       SkippedCanister.batch_id.db_column)
            )
            print("Added columns in SkippedCanister")

    except Exception as e:
        settings.logger.error("Error while adding columns and data in SkippedCanister: ", str(e))


if __name__ == "__main__":
    add_column_skipped_canister()

