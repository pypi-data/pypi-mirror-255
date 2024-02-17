from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.service.zone import prepare_data_for_device_locations
from src.model.model_container_master import ContainerMaster


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
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()
    associated_device = ForeignKeyField('self', null=True)
    ip_address = CharField(null=True)

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

    @classmethod
    def get_max_drawer_id(cls):
        try:
            drawer_id = cls.select(fn.MAX(cls.id)).scalar()
            return drawer_id

        except DoesNotExist as e:
            raise DoesNotExist
        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    container_id = ForeignKeyField(ContainerMaster, related_name='location_container_id')
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)
    is_disabled = BooleanField(default=False)

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

        drawer_ids_list = [(1, [1, 2]), (2, [3, 4]), (3, [5, 6]), (4, [7, 8]), (5, [9, 10]),
                           (6, [11, 12]), (7, [13, 14]), (8, [15, 16])]

        for device in DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST:
            index = DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST.index(device)
            data_list = []
            drawer_list = []
            drawer_id = ContainerMaster.get_max_drawer_id()
            if device_type == settings.DEVICE_TYPES['Manual Canister Cart']:
                loc_num = 0
                for each_drawer_data in drawer_ids_list:
                    drawer_level, ed = each_drawer_data
                    locations_data, drawer_data, drawer_id_updated, loc_num_updated = prepare_data_for_device_locations(
                        total_drawers=1,
                        locations_per_drawer=20,
                        device_id=device['device_id'],
                        drawer_per_row=2, quadrant_avialable=False,
                        drawer_id_list=ed,
                        drawer_id=drawer_id,
                        loc_num=loc_num,
                        drawer_level = drawer_level)

                    loc_num = loc_num_updated
                    drawer_id = drawer_id_updated
                    drawer_list.extend(drawer_data)
                    data_list.extend(locations_data)
            else:
                locations_data, drawer_data = prepare_data_for_device_locations(total_drawers=device['total_drawers'],
                                                                                locations_per_drawer=device.get(
                                                                                    'locations_per_drawer', 20),
                                                                                device_id=device['device_id'],
                                                                                drawer_per_row=8,
                                                                                quadrant_avialable=False)

            # data_list.extend(locations_data)
            print(drawer_list)
            print('**********************************************************************')
            print(data_list)
            ContainerMaster.insert_many(drawer_list).execute()
            LocationMaster.insert_many(data_list).execute()
    except DoesNotExist as ex:
        print(ex)
        raise DoesNotExist
    except InternalError as e:
        print(e)
        raise InternalError

    except Exception as e:
        print("Exception came in inserting location data: ", e)
        raise e


def migrate_robot_v3():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    device_query = DeviceMaster.select().dicts().order_by(DeviceMaster.id.desc()).get()
    # last_device_id = device_query['id']
    last_device_id = 51

    DEVICE_TYPES = [
        {'id': 8, 'device_type_name': "MFD_TROLLEY"}
    ]

    company_id = 4

    DEVICE_MASTER_DATA = list()
    DEVICE_ID_TO_MAX_LOCATION_MAPPING_CSR = list()

    for i in range(1, 7):
        trolley_id = last_device_id + i
        data_dict = {'id': trolley_id, 'company_id': company_id, 'name': 'MFD_TROLLEY_{}'.format(i),
                     'serial_number': 'MFD_TROLLEY_{}'.format(trolley_id),
                     'device_type_id': settings.DEVICE_TYPES["Manual Canister Cart"],
                     'system_id': None, 'version': '2.0',
                     'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                     'modified_date': CURRENT_DATE}

        DEVICE_MASTER_DATA.append(data_dict)

        location_data = {"device_id": trolley_id, "total_drawers": 16, "locations_per_drawer": 20}
        DEVICE_ID_TO_MAX_LOCATION_MAPPING_CSR.append(location_data)

    insert_device_types_data(DEVICE_TYPES)
    print("data inserted in device types data")
    insert_device_master_data(DEVICE_MASTER_DATA)
    print("data inserted in device master data")
    insert_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_CSR, settings.DEVICE_TYPES['MFD_TROLLEY'])
    print("data inserted in location master regular trolley")


if __name__ == "__main__":
    migrate_robot_v3()
