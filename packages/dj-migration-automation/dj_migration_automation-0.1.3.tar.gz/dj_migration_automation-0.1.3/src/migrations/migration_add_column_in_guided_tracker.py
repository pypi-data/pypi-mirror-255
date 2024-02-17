import settings
from playhouse.migrate import *

from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from peewee import *

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


class LocationMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"

class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


class GuidedMeta(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    mini_batch_id = IntegerField()
    cart_id = ForeignKeyField(DeviceMaster)
    status = ForeignKeyField(CodeMaster, default=constants.GUIDED_META_RECOMMENDATION_DONE)
    total_transfers = IntegerField(default=0)
    alt_canister_count = IntegerField(default=0)
    alt_can_replenish_count = IntegerField(default=0)
    replenish_skipped_count = IntegerField(default=0)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "guided_meta"


class GuidedTracker(BaseModel):
    id = PrimaryKeyField()
    guided_meta_id = ForeignKeyField(GuidedMeta)
    source_canister_id = ForeignKeyField(CanisterMaster)
    alternate_canister_id = ForeignKeyField(CanisterMaster, null=True, related_name="alternate_canister_for_tracker")
    alt_can_replenish_required = BooleanField(null=True)
    cart_location_id = ForeignKeyField(LocationMaster)
    destination_location_id = ForeignKeyField(LocationMaster, related_name="dest_location_for_tracker")
    transfer_status = ForeignKeyField(CodeMaster, default=constants.GUIDED_TRACKER_PENDING)
    required_qty = IntegerField(null=False, default=0)
    created_date = DateTimeField(default=get_current_date_time())
    modified_date = DateTimeField(default=get_current_date_time())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "guided_tracker"


def add_column_guided_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if GuidedTracker.table_exists():
            migrate(
                # migrator.add_column(GuidedTracker._meta.db_table,
                #                     GuidedTracker.required_qty.db_column,
                #                     GuidedTracker.required_qty),
                migrator.add_column(GuidedTracker._meta.db_table,
                                    GuidedTracker.created_date.db_column,
                                    GuidedTracker.created_date),
                migrator.add_column(GuidedTracker._meta.db_table,
                                    GuidedTracker.modified_date.db_column,
                                    GuidedTracker.modified_date)
            )
            print("Added column in GuidedTracker")

        if GuidedMeta.table_exists():
            migrate(
                migrator.add_column(GuidedMeta._meta.db_table,
                                    GuidedMeta.created_date.db_column,
                                    GuidedMeta.created_date),
                migrator.add_column(GuidedMeta._meta.db_table,
                                    GuidedMeta.modified_date.db_column,
                                    GuidedMeta.modified_date)
            )
            print("Added columns in GuidedMeta")

        if CodeMaster.table_exists():
            # codes for guided tracker
            CodeMaster.insert(id=constants.GUIDED_TRACKER_SKIPPED_AND_REPLACED, group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Skipped and Replaced").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_SKIPPED_AND_DONE, group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Skipped and Done").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_TRANSFER_SKIPPED,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Transfer Skipped").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_TRANSFER_AND_REPLENISH_SKIPPED,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Transfer and Replenish Skipped").execute()
            print("Added codes in Code Master")

    except Exception as e:
        settings.logger.error("Error while adding columns and data in GuidedTracker: ", str(e))


if __name__ == "__main__":
    add_column_guided_tracker()

