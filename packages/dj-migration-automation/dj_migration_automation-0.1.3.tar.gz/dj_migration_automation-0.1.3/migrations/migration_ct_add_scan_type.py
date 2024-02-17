from src import constants
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


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

        indexes = (
            (('name', 'company_id'), True),
        )


class DrugMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class CanisterTracker(BaseModel):

    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True) #refill_device_id
    drug_id = ForeignKeyField(DrugMaster)
    refill_type = SmallIntegerField(null=True) # 1 for refill-device
    quantity_adjusted = SmallIntegerField()
    original_quantity = SmallIntegerField()
    lot_number = CharField(max_length=30, null=True)
    expiration_date = CharField(max_length=8, null=True)
    # expiration_date = DateField(null=True)
    note = CharField(null=True, max_length=100)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    created_time = TimeField()
    voice_notification_uuid = CharField(null=True)
    drug_scan_type = ForeignKeyField(CodeMaster, default=constants.DATA_MATRIX, related_name="drug_bottle_scan")
    replenish_mode = ForeignKeyField(CodeMaster, default=constants.MANUAL_CODE, related_name="replenish")
    canister_scan_type = ForeignKeyField(CodeMaster, default=constants.DATA_MATRIX, related_name="canister_scan")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tracker"


def migrate_canister_tracker():
    init_db(db, 'database_migration')

    if GroupMaster.table_exists():
        GroupMaster.insert(id=constants.SCAN_TYPE_GROUP_ID, name='ScanType').execute()

    if GroupMaster.table_exists():
        GroupMaster.insert(id=constants.REPLENISH_MODE_GROUP_ID, name='ReplenishMode').execute()

    if CodeMaster.table_exists():
        CodeMaster.insert(id=constants.USER_ENTERED, group_id=constants.SCAN_TYPE_GROUP_ID,
                          key=constants.USER_ENTERED, value="User Entered").execute()
        CodeMaster.insert(id=constants.BARCODE, group_id=constants.SCAN_TYPE_GROUP_ID,
                          key=constants.BARCODE, value="Barcode").execute()
        CodeMaster.insert(id=constants.DATA_MATRIX, group_id=constants.SCAN_TYPE_GROUP_ID,
                          key=constants.DATA_MATRIX, value="Data Matrix").execute()
        CodeMaster.insert(id=constants.REFILL_DEVICE, group_id=constants.REPLENISH_MODE_GROUP_ID,
                          key=constants.REFILL_DEVICE, value="Refill Device").execute()
        CodeMaster.insert(id=constants.MANUAL_CODE, group_id=constants.REPLENISH_MODE_GROUP_ID,
                          key=constants.MANUAL_CODE, value="Manual").execute()

    print('Data Added in GroupMaster, CodeMaster')

    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            CanisterTracker._meta.db_table,
            CanisterTracker.drug_scan_type.db_column,
            CanisterTracker.drug_scan_type
        ),
        migrator.add_column(
            CanisterTracker._meta.db_table,
            CanisterTracker.replenish_mode.db_column,
            CanisterTracker.replenish_mode
        ),
        migrator.add_column(
            CanisterTracker._meta.db_table,
            CanisterTracker.canister_scan_type.db_column,
            CanisterTracker.canister_scan_type
        )
    )
    print("drug_scan_type,replenish_mode, canister_scan_type column added in canister tracker")


if __name__ == "__main__":
    migrate_canister_tracker()
