from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from playhouse.migrate import *
import settings
from dosepack.utilities.utils import get_current_date_time
import logging

logger = logging.getLogger("root")


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class DrawerMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    drawer_number = CharField(max_length=20)
    drawer_id = SmallIntegerField(null=True)
    ip_address = CharField(max_length=20, null=True)
    mac_address = CharField(max_length=50, null=True)
    drawer_status = BooleanField(default=True)
    security_code = CharField(default='0000', max_length=8)
    drawer_type = CharField(default="ROBOT")
    drawer_level = IntegerField(null=True)
    max_canisters = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    drawer_size = ForeignKeyField(CodeMaster, default=77, related_name="drawer_size")
    drawer_usage = ForeignKeyField(CodeMaster, default=79, related_name="drawer_usage")
    serial_number = CharField(unique=True, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drawer_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


class LocationMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

        indexes = (
            (('device_id', 'location_number'), True),
        )


def alter_table_drawer_master(migrator):
    # add column security_code and drawer_type in drawer_master
    try:
        if DrawerMaster.table_exists():
            migrate(
                migrator.add_column(
                    DrawerMaster._meta.db_table,
                    DrawerMaster.serial_number.db_column,
                    DrawerMaster.serial_number
                ))
        print("columns added")
    except Exception as e:
        logger.error("Error while modifying table drawer_master", str(e))


def migrate_changes():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    alter_table_drawer_master(migrator)


if __name__ == '__main__':
    migrate_changes()