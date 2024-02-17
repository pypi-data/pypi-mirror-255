from src import constants
from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


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
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()
    associated_device = ForeignKeyField('self', null=True)
    ip_address = CharField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


class OldContainerMaster(BaseModel):
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
    drawer_type = ForeignKeyField(CodeMaster, default=77, related_name="old_container_drawer_type")
    drawer_usage = ForeignKeyField(CodeMaster, default=79, related_name="old_container_drawer_usage")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "container_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


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
    drawer_usage = ForeignKeyField(CodeMaster, default=79, related_name="container_drawer_usage")
    shelf = IntegerField(null=True)
    serial_number = CharField(max_length=20, null=True)
    lock_status = BooleanField(default=False) # True-open and False-close

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "container_master"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


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

        indexes = (
            (('device_id', 'location_number'), True),
        )


def add_columns(migrator):
    try:
        migrate(
            migrator.drop_column(
                OldContainerMaster._meta.db_table,
                OldContainerMaster.drawer_id.db_column)
        )
        print("Removed Column drawer_id from ContainerMaster")
        migrate(
            migrator.rename_column(OldContainerMaster._meta.db_table,
                                   OldContainerMaster.drawer_number.db_column,
                                   'drawer_name')
        )
        print("Renamed drawer_number to drawer_name")

        migrate(
            migrator.add_column(ContainerMaster._meta.db_table,
                                ContainerMaster.lock_status.db_column,
                                ContainerMaster.lock_status)
        )
        print("Added column lock_status in container_master")

        migrate(
            migrator.add_column(ContainerMaster._meta.db_table,
                                ContainerMaster.secondary_ip_address.db_column,
                                ContainerMaster.secondary_ip_address)
        )
        migrate(
            migrator.add_column(ContainerMaster._meta.db_table,
                                ContainerMaster.secondary_mac_address.db_column,
                                ContainerMaster.secondary_mac_address)
        )
        migrate(
            migrator.add_column(ContainerMaster._meta.db_table,
                                ContainerMaster.shelf.db_column,
                                ContainerMaster.shelf)
        )
        migrate(
            migrator.add_column(ContainerMaster._meta.db_table,
                                ContainerMaster.serial_number.db_column,
                                ContainerMaster.serial_number)
        )
        print("Added column secondary_ip_address, secondary_mac_address,shelf and serial_number in ContainerMaster")

    except Exception as e:
        settings.logger.error("Error while adding columns in Container Master", str(e))


def add_device():
    try:
        DEVICE_MASTER_DATA = {'company_id': 3, 'name': 'CSR', 'serial_number': 'CSR00001',
                              'device_type_id': settings.DEVICE_TYPES["CSR"],
                              'system_id': None, 'version': '1', 'created_by': 2, 'modified_by': 2,
                              'active': 1, 'created_date': get_current_date_time(),
                              'modified_date': get_current_date_time(), 'associated_device': None, 'ip_address': None}
        DeviceMaster.insert(DEVICE_MASTER_DATA).execute()
        print("Added CSR in DeviceMaster")

    except Exception as e:
        print('Exception came in inserting device_master data: ', e)
        raise e


def add_containers_for_csr():
    rows = 'ABCDEFGHIJ'
    container_dict = {}
    container_list = []
    location_list = []
    location_dict = {}
    location_number = 0
    serial_number = 'CRD00'
    device_query = DeviceMaster.select().dicts().order_by(DeviceMaster.id.desc()).get()
    last_device_id = device_query['id']
    location_query = ContainerMaster.select().dicts().order_by(ContainerMaster.id.desc()).get()
    last_container_id = location_query['id']
    for r in rows:
        if r == 'A' or r == 'B':
            for c in range(1, 27):
                if 9 <= c <= 18:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_BIG
                    container_dict['drawer_usage'] = constants.USAGE_FAST_MOVING
                    container_list.append(container_dict.copy())
                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())
                else:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_BIG
                    container_dict['drawer_usage'] = constants.USAGE_MEDIUM_FAST_MOVING
                    container_list.append(container_dict.copy())

                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())

        if r == 'C' or r == 'D' or r == 'E':
            for c in range(1, 27):
                if 9 <= c <= 18:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_SMALL
                    container_dict['drawer_usage'] = constants.USAGE_FAST_MOVING
                    container_list.append(container_dict.copy())
                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())
                else:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_SMALL
                    container_dict['drawer_usage'] = constants.USAGE_MEDIUM_FAST_MOVING
                    container_list.append(container_dict.copy())
                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())

        if r == 'F':
            for c in range(1, 27):
                if 9 <= c <= 18:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_SMALL
                    container_dict['drawer_usage'] = constants.USAGE_FAST_MOVING
                    container_list.append(container_dict.copy())
                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())
                else:
                    container_dict['drawer_name'] = r + '-' + str(c)
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_SMALL
                    container_dict['drawer_usage'] = constants.USAGE_MEDIUM_SLOW_MOVING
                    container_list.append(container_dict.copy())
                    for i in range(1, 21):
                        location_dict['location_number'] = location_number + 1
                        location_number += 1
                        location_dict['display_location'] = r + str(c) + '-' + str(i)
                        location_list.append(location_dict.copy())
        if r == 'G':
            for c in range(1, 27):
                container_dict['drawer_name'] = r + '-' + str(c)
                container_dict['drawer_type'] = constants.SIZE_OR_TYPE_SMALL
                container_dict['drawer_usage'] = constants.USAGE_MEDIUM_SLOW_MOVING
                container_list.append(container_dict.copy())
                for i in range(1, 21):
                    location_dict['location_number'] = location_number + 1
                    location_number += 1
                    location_dict['display_location'] = r + str(c) + '-' + str(i)
                    location_list.append(location_dict.copy())
        if r == 'H' or r == 'I' or r == 'J':
            for c in range(1, 27):
                if r == 'I':
                    container_dict['drawer_type'] = constants.SIZE_OR_TYPE_BIG
                else:
                    container_dict['drawer_type']=constants.SIZE_OR_TYPE_SMALL
                container_dict['drawer_name'] = r + '-' + str(c)
                container_dict['drawer_usage'] = constants.USAGE_SLOW_MOVING
                container_list.append(container_dict.copy())
                for i in range(1, 21):
                    location_dict['location_number'] = location_number + 1
                    location_number += 1
                    location_dict['display_location'] = r + str(c) + '-' + str(i)
                    location_list.append(location_dict.copy())

    # To add corresponding serial_numbers to drawers
    li_serial = []
    li_url = []
    for i in range(1, 261):
        li_url.append('dose_'+str(81)+'_'+str(i*2-1)+','+str(i*2)+'.'+'127.0.0.1')
        if len(str(i)) == 1:
            li_serial.append(serial_number + '00' + str(i))
        if len(str(i)) == 2:
            li_serial.append(serial_number + '0' + str(i))
        if len(str(i)) == 3:
            li_serial.append(serial_number + str(i))
    # To add corresponding shelf to drawers
    li_shelf = []
    for each_data in range(10):
        for i in range(1, 27):
            li_shelf.append(i)
    li_level = []
    for i in range(1, 11):
        for j in range(26):
            li_level.append(i)

    for each_data in container_list:
        each_data['url'] = li_url.pop(0)
        each_data['serial_number'] = li_serial.pop(0)
        each_data['shelf'] = li_shelf.pop(0)
        each_data['drawer_level'] = li_level.pop(0)
        each_data['device_id'] = last_device_id
        each_data['created_by'] = 1
        each_data['modified_by'] = 1
        each_data['created_date'] = get_current_date_time()
        each_data['modified_date'] = get_current_date_time()

    # To add corresponding container_ids to locations
    container_id = last_container_id
    li_containers = []
    for i in range(260):
        container_id = container_id + 1
        for j in range(20):
            li_containers.append(container_id)
    for each_data in location_list:
        each_data['container_id'] = li_containers.pop(0)
        each_data['device_id'] = last_device_id
    try:
        # with db.transaction():
        ContainerMaster.insert_many(container_list).execute()
        LocationMaster.insert_many(location_list).execute()
        print("Data Added in ContainerMaster and LocationMaster")
    except (IntegrityError, InternalError) as e:
        raise e


def migration_csr_data():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    add_columns(migrator)
    add_device()
    add_containers_for_csr()


