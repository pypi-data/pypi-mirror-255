from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
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


def migration_guided_transfer():
    """
    To create new GuidedMeta and GuidedTracker table
    @return: Success Message
    """
    init_db(db, "database_migration")
    with db.transaction():

        if GroupMaster.table_exists():
            GroupMaster.insert(id=constants.GUIDED_META_GROUP_ID, name="GuidedMeta").execute()
            GroupMaster.insert(id=constants.GUIDED_TRACKER_GROUP_ID, name="GuidedTracker").execute()

        if CodeMaster.table_exists():
            # codes for guided meta
            CodeMaster.insert(id=constants.GUIDED_META_RECOMMENDATION_DONE, group_id=constants.GUIDED_META_GROUP_ID,
                              key=constants.GUIDED_META_RECOMMENDATION_DONE,
                              value="Guided Tx Recommendation Done").execute()
            CodeMaster.insert(id=constants.GUIDED_META_DRUG_BOTTLE_FETCHED, group_id=constants.GUIDED_META_GROUP_ID,
                              key=constants.GUIDED_META_DRUG_BOTTLE_FETCHED,
                              value="Guided Tx Drug Bottle Fetched").execute()
            CodeMaster.insert(id=constants.GUIDED_META_TO_TROLLEY_DONE, group_id=constants.GUIDED_META_GROUP_ID,
                              key=constants.GUIDED_META_TO_TROLLEY_DONE,
                              value="Guided Tx To Trolley Done").execute()
            CodeMaster.insert(id=constants.GUIDED_META_REPLENISH_DONE, group_id=constants.GUIDED_META_GROUP_ID,
                              key=constants.GUIDED_META_REPLENISH_DONE,
                              value="Guided Tx Replenish Done").execute()
            CodeMaster.insert(id=constants.GUIDED_META_TO_ROBOT_DONE, group_id=constants.GUIDED_META_GROUP_ID,
                              key=constants.GUIDED_META_TO_ROBOT_DONE,
                              value="Guided TX To Robot Done").execute()
            CodeMaster.insert(id=constants.GUIDED_META_TO_CSR_DONE, group_id=constants.GUIDED_META_GROUP_ID,
                              key=constants.GUIDED_META_TO_CSR_DONE,
                              value="Guided Tx To CSR Done").execute()

            # codes for guided tracker
            CodeMaster.insert(id=constants.GUIDED_TRACKER_PENDING, group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              key=constants.GUIDED_TRACKER_PENDING,
                              value="Guided Pending").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_REPLENISH, group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              key=constants.GUIDED_TRACKER_REPLENISH,
                              value="Guided Replenished").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_REPLACED, group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              key=constants.GUIDED_TRACKER_REPLACED,
                              value="Guided Replaced").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_SKIPPED, group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              key=constants.GUIDED_TRACKER_SKIPPED,
                              value="Guided Skipped").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_DONE, group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              key=constants.GUIDED_TRACKER_DONE,
                              value="Guided Done").execute()
        print('Data Added in GroupMaster, CodeMaster')

    db.create_tables([GuidedMeta, GuidedTracker], safe=True)
    print("Table created: GuidedMeta, GuidedTracker")

