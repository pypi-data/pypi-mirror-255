from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField(unique=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_type_master"


def migrate_device_type_name():
    """
    This migration is to update the max-length of the device_type_name column to 50 for the new devices.
    @return:
    """
    init_db(db, "database_migration")

    db.execute_sql("ALTER TABLE device_type_master MODIFY device_type_name char(50)")
    print("Tables modified: DeviceTypeMaster")


if __name__ == '__main__':
    migrate_device_type_name()
