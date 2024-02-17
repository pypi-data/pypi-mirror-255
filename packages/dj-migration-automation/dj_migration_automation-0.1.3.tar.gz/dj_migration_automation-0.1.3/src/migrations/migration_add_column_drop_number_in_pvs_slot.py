from dosepack.base_model.base_model import db, BaseModel
from playhouse.migrate import *
from dosepack.utilities.utils import get_current_date_time
import settings
from model.model_init import init_db


class SlotHeader(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'slot_header'


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


class PVSSlot(BaseModel):
    id = PrimaryKeyField()
    slot_header_id = ForeignKeyField(SlotHeader)
    drop_number = SmallIntegerField(null=False, default=0)
    slot_image_name = CharField(null=False)
    expected_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    pvs_identified_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    robot_drop_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    mfd_status = BooleanField(default=False)
    created_date = DateTimeField(null=False, default=get_current_date_time)
    modified_date = DateTimeField(null=False)
    us_status = ForeignKeyField(CodeMaster)
    device_id = ForeignKeyField(DeviceMaster)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot'


def add_column_drop_number():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if PVSSlot.table_exists():
            migrate(migrator.add_column(
                PVSSlot._meta.db_table,
                PVSSlot.drop_number.db_column,
                PVSSlot.drop_number))
            print("Added column in PVSSlot Table")
    except Exception as e:
        print("Error while adding columns in PVSSlot: ", str(e))
        raise


if __name__ == "__main__":
    add_column_drop_number()
