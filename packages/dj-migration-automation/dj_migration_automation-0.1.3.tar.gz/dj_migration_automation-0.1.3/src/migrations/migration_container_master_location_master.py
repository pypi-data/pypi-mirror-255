from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

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
    drawer_status = BooleanField(default=True) # drop it
    security_code = CharField(default='0000', max_length=8) # drop it
    drawer_type = CharField(default="ROBOT") # drop it
    drawer_level = IntegerField(null=True)
    max_canisters = IntegerField(null=True) # drop it
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    drawer_size = ForeignKeyField(CodeMaster, default=77, related_name="drawer_size") # rename as drawer_type and add mfd as a type
    drawer_usage = ForeignKeyField(CodeMaster, default=79, related_name="drawer_usage")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drawer_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


class ContainerMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    drawer_number = CharField(max_length=20)
    drawer_id = SmallIntegerField(null=True)
    ip_address = CharField(max_length=20, null=True)
    mac_address = CharField(max_length=50, null=True)
    drawer_level = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    drawer_type = ForeignKeyField(CodeMaster, default=77, related_name="drawer_type")
    drawer_usage = ForeignKeyField(CodeMaster, default=79, related_name="container_drawer_usage")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "container_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


class OLDLocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    drawer_id = ForeignKeyField(DrawerMaster)
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    container_id = ForeignKeyField(ContainerMaster)
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)
    is_disabled = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


def rename_model_name(migrator):
    try:
        migrate(
            migrator.rename_table(DrawerMaster._meta.db_table, ContainerMaster._meta.db_table)
        )
        print("table drawer_master renamed to container_master")

    except Exception as e:
        settings.logger.error("Error while renaming table canister_drawer", str(e))


def drop_columns(migrator):
    try:
        migrate(
            migrator.drop_column(
                DrawerMaster._meta.db_table,
                DrawerMaster.drawer_status.db_column,
                DrawerMaster.drawer_status
            ),
            migrator.drop_column(
                DrawerMaster._meta.db_table,
                DrawerMaster.security_code.db_column,
                DrawerMaster.security_code
            ),
            migrator.drop_column(
                DrawerMaster._meta.db_table,
                DrawerMaster.drawer_type.db_column,
                DrawerMaster.drawer_type
            ),
            migrator.drop_column(
                DrawerMaster._meta.db_table,
                DrawerMaster.max_canisters.db_column,
                DrawerMaster.max_canisters
            ),
        )
        print("Columns dropped from table drawer_master: drawer_status, security_code, drawer_type, max_canisters")

    except Exception as e:
        settings.logger.error("Error while dropping columns from table drawer_master", str(e))


def rename_columns(migrator):
    try:
        migrate(
            migrator.rename_column(DrawerMaster._meta.db_table,
                                   DrawerMaster.drawer_size.db_column,
                                   ContainerMaster.drawer_type.db_column),
            migrator.rename_column(LocationMaster._meta.db_table,
                                   OLDLocationMaster.drawer_id.db_column,
                                   LocationMaster.container_id.db_column)
        )
        print("Rename column drawer_size to drawer_type")

    except Exception as e:
        settings.logger.error("Error while Renaming column drawer_size to drawer_type", str(e))


def add_data_in_code_master():
    try:
        code_dict = dict(id=settings.DRAWER_TYPE['MFD'], group_id_id=19,
                         key=settings.DRAWER_TYPE['MFD'], value="Mfd")
        CodeMaster.create(**code_dict)
        print("Code 96 - mfd added in codemaster")

    except Exception as e:
        settings.logger.error("Error while adding code in code_master: ", str(e))


def add_columns(migrator):
    try:

        migrate(
            migrator.add_column(DrawerMaster._meta.db_table,
                                DrawerMaster.drawer_level.db_column,
                                DrawerMaster.drawer_level),
            migrator.add_column(LocationMaster._meta.db_table,
                                LocationMaster.is_disabled.db_column,
                                LocationMaster.is_disabled)
        )
        print("Added column drawer_level added in drawer_master and is_disabled in location_master")
    except Exception as e:
        settings.logger.error("Error while adding columns in drawer_master and location_master: ", str(e))


def migrate_container_master_changes():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    # add column
    add_columns(migrator)
    # drop columns
    drop_columns(migrator)
    # # rename columns
    rename_columns(migrator)
    # # rename model name
    rename_model_name(migrator)
    # Add a status in drawer_type : mfd
    add_data_in_code_master()

if __name__ == '__main__':
    migrate_container_master_changes()
