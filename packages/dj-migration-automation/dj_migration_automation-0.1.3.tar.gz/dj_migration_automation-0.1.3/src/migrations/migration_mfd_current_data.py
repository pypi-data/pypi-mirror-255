import src.constants
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class BatchMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    # name = CharField(null=True)
    # status = ForeignKeyField(CodeMaster, null=True)
    # created_date = DateTimeField(default=get_current_date_time, null=True)
    # modified_date = DateTimeField(default=get_current_date_time, null=True)
    # created_by = IntegerField()
    # modified_by = IntegerField(null=True)
    # split_function_id = IntegerField(null=True)
    # scheduled_start_time = DateTimeField(default=get_current_date_time(), null=True)
    # estimated_processing_time = FloatField(null=True)
    # imported_date = DateTimeField(null=True)
    #
    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class MfdAnalysis(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster, related_name='batch_id')
    # mfd_canister_id = ForeignKeyField(MfdCanisterMaster, null=True, related_name='mfd_can_id')
    # order_no = IntegerField()
    # assigned_to = IntegerField(null=True)
    # status_id = ForeignKeyField(CodeMaster, related_name='can_status')
    # dest_device_id = ForeignKeyField(DeviceMaster, related_name='robot_id')
    # mfs_device_id = ForeignKeyField(DeviceMaster, null=True, related_name='manual_fill_station')
    # mfs_location_number = IntegerField(null=True)
    # dest_quadrant = IntegerField()
    # trolley_location_id = ForeignKeyField(LocationMaster, related_name='trolley_loc_id', null=True)
    # dropped_location_id = ForeignKeyField(LocationMaster, null=True, related_name='dropped_loc_id')
    # created_by = IntegerField(null=True)
    # modified_by = IntegerField(null=True)
    # created_date = DateTimeField(default=get_current_date_time)
    # modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_analysis"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField(max_length=20)
    serial_number = CharField(max_length=20, unique=True)
    # device_type_id = ForeignKeyField(DeviceTypeMaster)
    system_id = IntegerField(null=True)
    version = CharField(null=True)
    active = IntegerField(null=True)
    max_canisters = IntegerField(null=True)
    big_drawers = IntegerField(null=True)
    small_drawers = IntegerField(null=True)
    controller = CharField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


class TempMfdFilling(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    mfd_analysis_id = ForeignKeyField(MfdAnalysis, null=True)
    mfs_device_id = ForeignKeyField(DeviceMaster, null=True)
    transfer_done = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "temp_mfd_filling"


def migrate_mfd_temp_data():
    init_db(db, 'database_migration')

    db.create_tables([TempMfdFilling], safe=True)

    print("Table(s) Created: TempMfdFilling")


if __name__ == "__main__":
    migrate_mfd_temp_data()
