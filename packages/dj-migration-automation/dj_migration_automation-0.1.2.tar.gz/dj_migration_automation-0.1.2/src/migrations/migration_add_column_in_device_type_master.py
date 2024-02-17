import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from peewee import *


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField(max_length=20, unique=True)
    device_code = CharField(null=True)
    container_code = CharField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_type_master"


def add_columns_device_type_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        migrate(
            migrator.add_column(DeviceTypeMaster._meta.db_table,
                                DeviceTypeMaster.device_code.db_column,
                                DeviceTypeMaster.device_code),
            migrator.add_column(DeviceTypeMaster._meta.db_table,
                                DeviceTypeMaster.container_code.db_column,
                                DeviceTypeMaster.container_code)
        )
        print("Added column device_code and container_code in DeviceTypeMaster")
    except Exception as e:
        settings.logger.error("Error while adding columns in DeviceTypeMaster: ", str(e))


if __name__ == '__main__':
    add_columns_device_type_master()