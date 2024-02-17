from playhouse.migrate import *
from collections import defaultdict
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.service.zone import prepare_data_for_csr_locations, prepare_data_for_robot_locations


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField( max_length=20, unique=True)

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

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    drawer_number = CharField()
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
            if device_type == settings.DEVICE_TYPES['CSR']:
                locations_data = prepare_data_for_csr_locations(total_drawers=device['total_drawers'],
                                                                locations_per_drawer=device.get('locations_per_drawer',
                                                                                                20),
                                                                device_id=device['device_id'],
                                                                drawer_initials='decimal',
                                                                csr_name=device['shelf_name'])
            else:
                locations_data = prepare_data_for_robot_locations(total_drawers=device['total_drawers'],
                                                                  locations_per_drawer=device.get(
                                                                      'locations_per_drawer', 20),
                                                                  device_id=device['device_id'],
                                                                  drawer_per_row=16, quadrant_avialable=True)

            data_list.extend(locations_data)
            print('**********************************************************************')
            print(data_list)
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
        {'id': 9, 'device_type_name': "CANISTER_ROBOT_TROLLEY"},
        {'id': 10, 'device_type_name': 'CANISTER_CSR_TROLLEY'}
    ]

    last_device_id +=1
    robot_id1 = last_device_id
    robot_id2 = last_device_id +1
    robot_id3 = last_device_id +2
    robot_id4 = last_device_id +3
    robot_id5 = last_device_id +4
    robot_id6 = last_device_id +5

    company_id = 3

    DEVICE_MASTER_DATA = [
        {'id': robot_id1, 'company_id': company_id, 'name': 'CAN_ROBOT_TROLLEY-1', 'serial_number': 'CRT1',
         'device_type_id': settings.DEVICE_TYPES["CANISTER_ROBOT_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 320, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
        {'id': robot_id2, 'company_id': company_id, 'name': 'CAN_ROBOT_TROLLEY-2', 'serial_number': 'CRT2',
         'device_type_id': settings.DEVICE_TYPES["CANISTER_ROBOT_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 320, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
        {'id': robot_id3, 'company_id': company_id, 'name': 'CAN_ROBOT_TROLLEY-3', 'serial_number': 'CRT3',
         'device_type_id': settings.DEVICE_TYPES["CANISTER_ROBOT_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 320, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
        {'id': robot_id4, 'company_id': company_id, 'name': 'CAN_ROBOT_TROLLEY-4', 'serial_number': 'CRT4',
         'device_type_id': settings.DEVICE_TYPES["CANISTER_ROBOT_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 320, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
        {'id': robot_id5, 'company_id': company_id, 'name': 'CAN_CSR_TROLLEY-1', 'serial_number': 'CCT1',
         'device_type_id': settings.DEVICE_TYPES["CANISTER_CSR_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 320, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
        {'id': robot_id6, 'company_id': company_id, 'name': 'CAN_CSR_TROLLEY-2', 'serial_number': 'CCT2',
         'device_type_id': settings.DEVICE_TYPES["CANISTER_CSR_TROLLEY"],
         'system_id': None, 'version': '2', 'max_canisters': 320, 'big_drawers': None, 'small_drawers': None,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE}

    ]

    DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST_ROBOT = [
        {"device_id": robot_id1, "total_drawers": 16, "locations_per_drawer": 20},
        {"device_id": robot_id2, "total_drawers": 16, "locations_per_drawer": 20},
        {"device_id": robot_id3, "total_drawers": 16, "locations_per_drawer": 20},
        {"device_id": robot_id4, "total_drawers": 16, "locations_per_drawer": 20},
        {"device_id": robot_id5, "total_drawers": 16, "locations_per_drawer": 20},
        {"device_id": robot_id6, "total_drawers": 16, "locations_per_drawer": 20}

    ]

    insert_device_types_data(DEVICE_TYPES)
    print("data inserted in device types data")
    insert_device_master_data(DEVICE_MASTER_DATA)
    print("data inserted in device master data")
    insert_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST_ROBOT, settings.DEVICE_TYPES['CANISTER_ROBOT_TROLLEY'])
    print("data inserted in location master")


if __name__ == "__main__":
    migrate_robot_v3()