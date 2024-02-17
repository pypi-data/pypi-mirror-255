import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *


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


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


class CanisterTransfers(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    dest_device_id = ForeignKeyField(DeviceMaster, null=True)
    dest_location_number = SmallIntegerField(null=True)
    dest_quadrant = SmallIntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    trolley_loc_id = ForeignKeyField(LocationMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfers"


def add_column_trolley_location_id_in_canister_transfers(migrator):
    if CanisterTransfers.table_exists():
        migrate(
            migrator.add_column(CanisterTransfers._meta.db_table,
                                CanisterTransfers.trolley_loc_id.db_column,
                                CanisterTransfers.trolley_loc_id)
        )
        print("column trolley_location_id added in table canister_transfers")


if __name__ == '__main__':
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    add_column_trolley_location_id_in_canister_transfers(migrator)
