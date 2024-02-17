from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


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


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


class DrawerMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    drawer_number = CharField(max_length=20)
    drawer_id = SmallIntegerField(null=True)
    ip_address = CharField(max_length=20, null=True)
    drawer_size = ForeignKeyField(CodeMaster, default=77, related_name= "drawer_size")
    mac_address = CharField(max_length=50, null=True)
    drawer_status = BooleanField(default=True)
    security_code = CharField(default='0000', max_length=8)
    drawer_usage = ForeignKeyField(CodeMaster, default= 79, related_name= "drawer_usage")
    drawer_type = CharField(default="ROBOT")
    drawer_level = IntegerField(null=True)
    max_canisters = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drawer_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


class OLDDrawerMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    drawer_number = CharField(max_length=20)
    drawer_id = SmallIntegerField(null=True)
    ip_address = CharField(max_length=20, null=True)
    drawer_size = CharField(default="REGULAR")
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

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drawer_master"


group_master_data = [dict(id=19, name="DrawerSize"),
                     dict(id=20, name="DrawerUsage"),
                     ]

code_master_data = [dict(id=settings.DRAWER_TYPE['BIG'], group_id=19,
                         key=settings.DRAWER_TYPE['BIG'], value="Big"),
                    dict(id=settings.DRAWER_TYPE['SMALL'], group_id=19,
                         key=settings.DRAWER_TYPE['SMALL'], value="Small"),
                    dict(id=78, group_id=20, key=78, value="Fast Moving"),
                    dict(id=79, group_id=20, key=79, value="Medium Fast Moving"),
                    dict(id=80, group_id=20, key=80, value="Medium Slow Moving"),
                    dict(id=81, group_id=20, key=81, value="SLow Moving")
                    ]


def migrate_drawer_drug_type():

    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)

    for each_data in group_master_data:
        GroupMaster.create(**each_data)
    print("data inserted in group master")

    for data in code_master_data:
        CodeMaster.create(**data)
    print("data inserted in code master")

    migrate(
        migrator.add_column(
            DrawerMaster._meta.db_table,
            DrawerMaster.drawer_usage.db_column,
            DrawerMaster.drawer_usage
        )
    )

    migrate(
        migrator.drop_column(
            OLDDrawerMaster._meta.db_table,
            OLDDrawerMaster.drawer_size.db_column,
        ),
        migrator.add_column(
            DrawerMaster._meta.db_table,
            DrawerMaster.drawer_size.db_column,
            DrawerMaster.drawer_size
        )
    )

    print('Table updated: DrawerMaster')


if __name__ == '__main__':
    migrate_drawer_drug_type()