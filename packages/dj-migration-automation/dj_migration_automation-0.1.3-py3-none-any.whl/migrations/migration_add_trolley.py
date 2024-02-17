from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.service.zone import prepare_data_for_device_locations_trolley, prepare_data_for_device_locations


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField(max_length=20, unique=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_type_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


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

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drawer_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )

class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    drawer_id = ForeignKeyField(DrawerMaster)
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

        indexes = (
            (('device_id', 'location_number'), True),
        )


CURRENT_DATE = get_current_date_time()


def insert_device_types_data(DEVICE_TYPES):
    try:
        DeviceTypeMaster.insert_many(DEVICE_TYPES).execute()
    except Exception as e:
        print("Exception came in inserting device types data")
        raise e


def insert_device_master_data(DEVICE_MASTER_DATA):
    try:
        DeviceMaster.insert_many(DEVICE_MASTER_DATA).execute()
    except Exception as e:
        print('Exception came in inserting device_master data: ', e)
        raise e


def insert_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST, device_type):
    try:
        for device in DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST:
            data_list = []
            drawer_list = []
            if device_type == settings.DEVICE_TYPES['REGULAR_TROLLEY']:
                locations_data, drawer_data, drawer_id, latest_num = prepare_data_for_device_locations_trolley(
                    total_drawers=device['total_drawers'],
                    locations_per_drawer=20,
                    device_id=device['device_id'],
                    drawer_per_row=16)

            else:
                locations_data, drawer_data, drawer_id, latest_num = prepare_data_for_device_locations_trolley(
                    total_drawers=device['total_drawers'],
                    locations_per_drawer=device.get(
                        'locations_per_drawer', 20),
                    device_id=device['device_id'],
                    drawer_per_row=8,
                    quadrant_avialable=False)

            data_list.extend(locations_data)
            drawer_list.extend(drawer_data)
            print('**********************************************************************')
            print(data_list)
            DrawerMaster.insert_many(drawer_list).execute()
            LocationMaster.insert_many(data_list).execute()
    except Exception as e:
        print("Exception came in inserting location data: ", e)
        raise e


def migrate_robot_v3():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    device_query = DeviceMaster.select().dicts().order_by(DeviceMaster.id.desc()).get()
    last_device_id = device_query['id']

    DEVICE_TYPES = [
        {'id': 9, 'device_type_name': "REGULAR_TROLLEY"},
        {'id': 10, 'device_type_name': 'LIFT_TROLLEY'}
    ]

    last_device_id += 1
    robot_id1 = last_device_id
    robot_id2 = last_device_id + 1
    robot_id3 = last_device_id + 2
    robot_id4 = last_device_id + 3
    robot_id5 = last_device_id + 4

    company_id = 4

    DEVICE_MASTER_DATA = [
        {'id': robot_id1, 'company_id': company_id, 'name': 'REGULAR_TROLLEY_1', 'serial_number': 'RT101',
         'device_type_id': settings.DEVICE_TYPES["REGULAR_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 320, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
        {'id': robot_id2, 'company_id': company_id, 'name': 'REGULAR_TROLLEY_2', 'serial_number': 'RT102',
         'device_type_id': settings.DEVICE_TYPES["REGULAR_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 320, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
        {'id': robot_id3, 'company_id': company_id, 'name': 'REGULAR_TROLLEY_3', 'serial_number': 'RT103',
         'device_type_id': settings.DEVICE_TYPES["REGULAR_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 320, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
        {'id': robot_id4, 'company_id': company_id, 'name': 'LIFT_TROLLEY_1', 'serial_number': 'LT201',
         'device_type_id': settings.DEVICE_TYPES["LIFT_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 160, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
        {'id': robot_id5, 'company_id': company_id, 'name': 'LIFT_TROLLEY_2', 'serial_number': 'LT202',
         'device_type_id': settings.DEVICE_TYPES["LIFT_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 160, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},

    ]

    DEVICE_ID_TO_MAX_LOCATION_MAPPING_REGULAR_TROLLEY = [
        {"device_id": robot_id1, "total_drawers": 16, "locations_per_drawer": 20},
        {"device_id": robot_id2, "total_drawers": 16, "locations_per_drawer": 20},
        {"device_id": robot_id3, "total_drawers": 16, "locations_per_drawer": 20}
    ]

    DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIFT_TROLLEY = [
        {"device_id": robot_id4, "total_drawers": 8, "locations_per_drawer": 20},
        {"device_id": robot_id5, "total_drawers": 8, "locations_per_drawer": 20}
    ]

    insert_device_types_data(DEVICE_TYPES)
    print("data inserted in device types data")
    insert_device_master_data(DEVICE_MASTER_DATA)
    print("data inserted in device master data")
    insert_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_REGULAR_TROLLEY, settings.DEVICE_TYPES['REGULAR_TROLLEY'])
    print("data inserted in location master regular trolley")
    insert_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIFT_TROLLEY, settings.DEVICE_TYPES['LIFT_TROLLEY'])
    print("data inserted in location master lift trolley")


if __name__ == "__main__":
    migrate_robot_v3()
