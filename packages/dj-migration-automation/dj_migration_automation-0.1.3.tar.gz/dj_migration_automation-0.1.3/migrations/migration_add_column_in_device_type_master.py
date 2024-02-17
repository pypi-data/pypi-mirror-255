from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField(max_length=50, unique=True)
    device_code = CharField(max_length=10, null=True)
    container_code = CharField(max_length=10, null=True)
    station_type_id = IntegerField(unique=True, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_type_master"

def migrate_add_column_in_device_type_master_details():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    if DeviceTypeMaster.table_exists():
        migrate(
            migrator.add_column(
                DeviceTypeMaster._meta.db_table,
                DeviceTypeMaster.station_type_id.db_column,
                DeviceTypeMaster.station_type_id
            ))
    print("Table Modified: DeviceTypeMaster")

if __name__ == "__main__":
    migrate_add_column_in_device_type_master_details()