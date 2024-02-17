import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from model.model_device_manager import DeviceMaster
from src.model.model_slot_header import SlotHeader
from peewee import *


class PVSSlot(BaseModel):
    id = PrimaryKeyField()
    slot_header_id = ForeignKeyField(SlotHeader, related_name='pvsslot_slot_header_id')
    drop_number = IntegerField(null=False)
    slot_image_name = CharField(null=False)
    expected_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    pvs_identified_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    robot_drop_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    mfd_status = BooleanField(default=False)
    created_date = DateTimeField(null=False, default=get_current_date_time)
    modified_date = DateTimeField(null=False)
    us_status = ForeignKeyField(CodeMaster, related_name='pvsslot_us_status')
    device_id = ForeignKeyField(DeviceMaster, related_name='pvsslot_device_id')
    quadrant = SmallIntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot'


def add_column_pvs_slot():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if PVSSlot.table_exists():
            migrate(
                migrator.add_column(PVSSlot._meta.db_table,
                                    PVSSlot.quadrant.db_column,
                                    PVSSlot.quadrant)
            )
            print("Added column in PVSSlot")
    except Exception as e:
        settings.logger.error("Error while adding columns in PVSSlot: ", str(e))


if __name__ == "__main__":
    add_column_pvs_slot()