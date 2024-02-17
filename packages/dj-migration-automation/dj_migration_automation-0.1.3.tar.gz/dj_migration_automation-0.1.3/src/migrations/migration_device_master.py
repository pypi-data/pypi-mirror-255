import logging

from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db

logger = logging.getLogger("root")


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_type_master"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField(max_length=20)
    serial_number = CharField(max_length=20, unique=True)
    device_type_id = ForeignKeyField(DeviceTypeMaster)
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
    associated_device = ForeignKeyField('self', null=True)
    ip_address = CharField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


def migration_device_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    with db.transaction():
        try:
            migrate(
                migrator.drop_column(DeviceMaster._meta.db_table,
                                     DeviceMaster.max_canisters.db_column)
            )
            migrate(
                migrator.drop_column(DeviceMaster._meta.db_table,
                                     DeviceMaster.big_drawers.db_column)
            )
            migrate(
                migrator.drop_column(DeviceMaster._meta.db_table,
                                     DeviceMaster.small_drawers.db_column)
            )
            migrate(
                migrator.drop_column(DeviceMaster._meta.db_table,
                                     DeviceMaster.controller.db_column)
            )
        except (IntegrityError, InternalError) as e:
            print(e)
    print("Table Modified: DeviceMaster")


if __name__ == '__main__':
    migration_device_master()