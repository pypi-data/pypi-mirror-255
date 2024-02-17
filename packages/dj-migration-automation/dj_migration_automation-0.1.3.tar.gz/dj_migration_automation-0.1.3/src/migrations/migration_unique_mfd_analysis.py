from playhouse.migrate import *
from collections import defaultdict
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time


class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        db_table = 'batch_master'


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


class MfdAnalysis(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster, related_name='batch_id')
    # mfd_canister_id = ForeignKeyField(MfdCanisterMaster, null=True, related_name='mfd_can_id')
    order_no = IntegerField()
    assigned_to = IntegerField(null=True)
    # status_id = ForeignKeyField(CodeMaster, related_name='can_status')
    # dest_device_id = ForeignKeyField(DeviceMaster, related_name='robot_id')
    # mfs_device_id = ForeignKeyField(DeviceMaster, null=True, related_name='manual_fill_station')
    mfs_location_number = IntegerField(null=True)
    dest_quadrant = IntegerField()
    # trolley_location_id = ForeignKeyField(LocationMaster, related_name='trolley_loc_id', null=True)
    # dropped_location_id = ForeignKeyField(LocationMaster, null=True, related_name='dropped_loc_id')
    # transferred_location_id = ForeignKeyField(LocationMaster, null=True, related_name='transferred_loc_id')
    trolley_seq = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_analysis"


class TempMfdFilling(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    mfd_analysis_id = ForeignKeyField(MfdAnalysis, null=True, unique=True)
    mfs_device_id = ForeignKeyField(DeviceMaster, null=True)
    transfer_done = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "temp_mfd_filling"


def migrate_mfd_analysis_unique_key():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    if TempMfdFilling.table_exists():
        temp_filling_data = TempMfdFilling.select(TempMfdFilling).dicts().group_by(TempMfdFilling.mfd_analysis_id)
        filling_data = list()
        for record in temp_filling_data:
            mfs_loc_data = {'batch_id': record['batch_id'],
                            'mfd_analysis_id': record['mfd_analysis_id'],
                            'mfs_device_id': record['mfs_device_id']}
            filling_data.append(mfs_loc_data)
        db.drop_tables([TempMfdFilling])
        print("Table dropped: TempMfdFilling")

        db.create_tables([TempMfdFilling], safe=True)
        print("Tables created: TempMfdFilling")

        if filling_data:
            TempMfdFilling.insert_many(filling_data).execute()
            print("data added: TempMfdFilling")
        else:
            print('No data found')


if __name__ == "__main__":
    migrate_mfd_analysis_unique_key()
