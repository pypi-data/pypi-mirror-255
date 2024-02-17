from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.service.zone import prepare_data_for_robot_mfd_locations


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField(max_length=20, unique=True)

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
    # max_canisters = IntegerField(null=True)
    # big_drawers = IntegerField(null=True)
    # small_drawers = IntegerField(null=True)
    # controller = CharField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    # group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class ContainerMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    drawer_name = CharField(max_length=20)
    ip_address = CharField(max_length=20, null=True)
    secondary_ip_address = CharField(max_length=20, null=True)
    mac_address = CharField(max_length=50, null=True)
    secondary_mac_address = CharField(max_length=50, null=True)
    drawer_level = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    drawer_type = ForeignKeyField(CodeMaster, default=77, related_name="drawer_type")
    drawer_usage = ForeignKeyField(CodeMaster, default=79, related_name="drawer_usage")
    shelf = IntegerField(null=True)
    serial_number = CharField(max_length=20, null=True)
    lock_status = BooleanField(default=False) # True-open and False-close

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "container_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


# class DrawerMaster(BaseModel):
#     id = PrimaryKeyField()
#     device_id = ForeignKeyField(DeviceMaster)
#     drawer_number = CharField(max_length=20)
#     drawer_id = SmallIntegerField(null=True)
#     ip_address = CharField(max_length=20, null=True)
#     mac_address = CharField(max_length=50, null=True)
#     drawer_status = BooleanField(default=True)
#     security_code = CharField(default='0000', max_length=8)
#     drawer_type = CharField(default="ROBOT")
#     drawer_level = IntegerField(null=True)
#     max_canisters = IntegerField(null=True)
#     created_by = IntegerField(null=True)
#     modified_by = IntegerField(null=True)
#     created_date = DateTimeField(default=get_current_date_time)
#     modified_date = DateTimeField(default=get_current_date_time)
#     drawer_size = ForeignKeyField(CodeMaster, default=77, related_name="drawer_size")
#     drawer_usage = ForeignKeyField(CodeMaster, default=79, related_name="drawer_usage")
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "drawer_master"
#
#         indexes = (
#             (('device_id', 'drawer_number', 'ip_address'), True),
#         )


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    # drawer_number = CharField() # dropped this field from table and added drawer_id
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)
    container_id = ForeignKeyField(ContainerMaster, null=False)
    is_disabled = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

        indexes = (
            (('device_id', 'location_number'), True),
        )


CURRENT_DATE = get_current_date_time()


def migrate_mfd_drawers():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    all_drawer_data = list()

    with db.transaction():
        drawer_per_row = 10
        location_per_drawer = 8
        mfd_initial = 'M'
        device_query = DeviceMaster.select().dicts() \
            .where(DeviceMaster.version == settings.ROBOT_SYSTEM_VERSIONS['v3'],
                   DeviceMaster.id == 15,
                   DeviceMaster.device_type_id == settings.DEVICE_TYPES['ROBOT']) \
            .order_by(DeviceMaster.id.desc())

        for device in device_query:
            print(device['id'])
            try:
                max_location_number = LocationMaster.select(fn.MAX(LocationMaster.location_number).alias('max_loc_id')
                                                            ).dicts() \
                    .where(LocationMaster.device_id == device['id']).get()
                max_location_number = max_location_number['max_loc_id']
                print(max_location_number)
            except DoesNotExist as e:
                max_location_number = 0
            for i in range(1, drawer_per_row + 1):
                drawer_data = {'device_id': device['id'],
                               'drawer_name': '{}-{}'.format(mfd_initial, i),
                               'drawer_type': settings.SIZE_OR_TYPE['MFD']}
                print(drawer_data)
                drawer_record = BaseModel.db_create_record(drawer_data, ContainerMaster, get_or_create=False)

                location_drawer_initial = '{}{}'.format(mfd_initial, i)
                mfd_derawer_data = prepare_data_for_robot_mfd_locations(location_per_drawer,
                                                                        device['id'],
                                                                        drawer_record.id,
                                                                        max_location_number,
                                                                        original_drawer_number=i,
                                                                        drawer_initial_name=location_drawer_initial,
                                                                        drawer_per_row=10,
                                                                        quadrant_avialable=True)
                all_drawer_data.extend(mfd_derawer_data)
                max_location_number = max_location_number + location_per_drawer
            print(all_drawer_data)
            if all_drawer_data:
                LocationMaster.insert_many(all_drawer_data).execute()


if __name__ == "__main__":
    migrate_mfd_drawers()
