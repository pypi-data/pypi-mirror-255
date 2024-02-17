from dosepack.base_model.base_model import db, BaseModel
import os
from model.model_init import init_db
from playhouse.migrate import *
import settings
from src.model.model_drug_master import DrugMaster
from dosepack.utilities.utils import get_current_date_time
from src.service.zone import prepare_data_for_csr_locations, prepare_data_for_robot_locations
from realtime_db.dp_realtimedb_interface import Database
from src.service.misc import get_couch_db_database_name


class RobotMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    company_id = IntegerField()
    name = CharField(max_length=150)
    serial_number = FixedCharField(unique=True, max_length=10)
    version = FixedCharField(max_length=11)
    active = BooleanField(default=True)
    max_canisters = SmallIntegerField()  # number of canisters that robot can hold
    big_drawers = IntegerField(default=4)  # number of big drawers that robot holds
    small_drawers = IntegerField(default=12)  # number of small drawers that robot holds
    # controller used 'AR' for ardiuno and 'BB' for beagle bone 'BBB' for beagle bone black
    controller = CharField(max_length=10, default="AR")
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "robot_master"


class UnitMaster(BaseModel):
    """
    Class to store the unit details.
    """
    id = PrimaryKeyField()
    name = CharField()
    type = CharField()
    symbol = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "unit_master"


class UnitConversion(BaseModel):
    """
    Class to store the unit conversion ratios between the units of the same type.
    """
    id = PrimaryKeyField()
    convert_from = ForeignKeyField(UnitMaster, related_name='converted_from')
    convert_to = ForeignKeyField(UnitMaster, related_name='converted_into')
    conversion_ratio = DecimalField(decimal_places=6)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "unit_conversion"


class ZoneMaster(BaseModel):
    """
        @desc: Class to store the zone details of company.
    """
    id = PrimaryKeyField()
    name = CharField(max_length=25)
    floor = IntegerField()
    length = DecimalField(decimal_places=2)
    height = DecimalField(decimal_places=2)
    width = DecimalField(decimal_places=2)
    company_id = IntegerField()  # Foreign key field of company table of dp auth
    x_coordinate = DecimalField(decimal_places=2)
    y_coordinate = DecimalField(decimal_places=2)
    dimensions_unit_id = ForeignKeyField(UnitMaster)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "zone_master"
        indexes = (
            (('company_id', 'name'), True),
        )


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField(unique=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_type_master"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField()
    serial_number = CharField(unique=True)
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


class DeviceLayoutDetails(BaseModel):
    """
    Class to store the inventory layout related details of various devices.
    """
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster, null=True, unique=True)
    zone_id = ForeignKeyField(ZoneMaster, null=True)
    x_coordinate = DecimalField(decimal_places=2)
    y_coordinate = DecimalField(decimal_places=2)
    marked_for_transfer = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_layout_details"


class DeviceProperties(BaseModel):
    """
    Class to store the device properties related to inventory layout. Right now we store following properties :
    1. number_of_drawers
    2. rotate
    3. drawers_initial_pattern
    4. initials_for_each_column ( For SSR only)
    5. number_of_columns ( For SSR only)
    """
    id = PrimaryKeyField()
    device_layout_id = ForeignKeyField(DeviceLayoutDetails)
    property_name = CharField()
    property_value = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_properties"


class StackedDevices(BaseModel):
    """
    Class to store the stacking details (i.e which device is stacked on which device)
    of the device present in the inventory layout.
    """
    id = PrimaryKeyField()
    device_layout_id = ForeignKeyField(DeviceLayoutDetails, unique=True, related_name='device')
    stacked_on_device_id = ForeignKeyField(DeviceLayoutDetails, null=True, related_name='stacked_on_device')

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "stacked_devices"


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    drawer_number = CharField()
    display_location = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

        indexes = (
            (('device_id', 'location_number'), True),
        )


class LocationMapping(BaseModel):
    id = PrimaryKeyField()
    location_id = ForeignKeyField(LocationMaster, unique=True)
    ndc = CharField(max_length=14, unique=True)

    # todo: Ask whether to link the locations with ndc or formatted ndc.

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_mapping"


class NewCanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    robot_id = ForeignKeyField(RobotMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=20)
    available_quantity = SmallIntegerField()
    canister_number = SmallIntegerField(default=0, null=True)
    canister_type = CharField(max_length=20)
    active = BooleanField()
    reorder_quantity = SmallIntegerField()
    barcode = CharField(max_length=15)
    canister_code = CharField(max_length=25, unique=True, null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    location_id = ForeignKeyField(LocationMaster, null=True, unique=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class IntermediateCanisterDrawers(BaseModel):
    id = PrimaryKeyField()
    robot_id = ForeignKeyField(RobotMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    drawer_id = IntegerField()  # To store the drawer id for electronics api calls.
    drawer_number = IntegerField()  # To store the physical drawer number.
    drawer_name = CharField(null=True)
    ip_address = CharField()
    mac_address = CharField(null=True)
    drawer_status = BooleanField(default=True)
    drawer_size = CharField(default="REGULAR", max_length=20)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drawers"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


class CanisterDrawers(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster, related_name='device_id')
    drawer_id = IntegerField()  # To store the drawer id for electronics api calls.
    drawer_number = CharField(null=True)
    ip_address = CharField()
    mac_address = CharField(null=True)
    drawer_status = BooleanField(default=True)
    drawer_size = CharField(default="REGULAR", max_length=20)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drawers"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


class CanisterDrawers(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    drawer_id = IntegerField()  # To store the drawer id for electronics api calls.
    drawer_number = CharField()  # To store the physical drawer number.
    ip_address = CharField()
    mac_address = CharField(null=True)
    drawer_status = BooleanField(default=True)
    drawer_size = CharField(default="REGULAR", max_length=20)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drawers"

        indexes = (
            (('device_id', 'drawer_number', 'ip_address'), True),
        )


class SequenceGenerator(BaseModel):
    id = PrimaryKeyField()
    seq_name = CharField(max_length=30)
    seq_no = IntegerField(default=1)
    company_id = IntegerField(null=True)
    system_id = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "sequence_generator"


DEVICE_TYPES = [
    {'id': 2, 'device_type_name': "CSR"},
    {'id': 1, 'device_type_name': "Robot"},
    {'id': 3, 'device_type_name': "SSR"},
    {'id': 4, 'device_type_name': "Dosepacker"},
    {'id': 5, 'device_type_name': 'Refill device'}
]

ZONE_DATA = [
    {"id": 1, "name": "Zone 1", "floor": 1, "length": 1500, "height": 1309, "width": 1500, "company_id": 3,
     "x_coordinate": 12.3, "y_coordinate": 12.3, "dimensions_unit_id": 5}
]

STACKED_DEVICES_DATA = [
    {'device_layout_id': 1, 'stacked_on_device_id': None},
]



def migrate_temp():
    migrator = MySQLMigrator(db)
    init_db(db, 'database_migration')

    company_id = 3

    
    device_id = DeviceMaster.select().count()

    csr_device_id = device_id + 1

    CSR_DEVICE_TYPE_ID = settings.DEVICE_TYPES['CSR']

    CURRENT_DATE = get_current_date_time()
    DEVICE_MASTER_DATA = [
        {'id': csr_device_id, 'company_id': 3, 'name': 'Shelf A', 'serial_number': 'CSR010001',
         'device_type_id': CSR_DEVICE_TYPE_ID,
         'system_id': None, 'version': '1', 'max_canisters': 84, 'big_drawers': None, 'small_drawers': 7,
         'controller': None,
         'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
         'modified_date': CURRENT_DATE},
    ]


    print(DEVICE_MASTER_DATA)
    # change
    DEVICE_LAYOUT_DETAILS_DATA = [
        {'id': 1, 'device_id': csr_device_id, 'zone_id': 1, 'x_coordinate': 1, 'y_coordinate': 1}
    ]
    print(DEVICE_LAYOUT_DETAILS_DATA)
    DEVICE_PROPERTIES_DATA = [
        {
            "device_layout_id": 1, "property_name": "drawer_initials_pattern", "property_value": "decimal"
        },
        {
            "device_layout_id": 1, "property_name": "number_of_drawers", "property_value": "7"
        },
        {
            "device_layout_id": 1, "property_name": "rotate", "property_value": "0"
        }
    ]
    print(DEVICE_PROPERTIES_DATA)
    # change
    DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST = [
        {"device_id": csr_device_id, "total_drawers": 7, "shelf_name": 'A'}
    ]
    print(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST)
    STACKED_DEVICES_DATA = [
        {'device_layout_id': 1, 'stacked_on_device_id': None},
        {'device_layout_id': 2, 'stacked_on_device_id': None},
        {'device_layout_id': 3, 'stacked_on_device_id': None},
        {'device_layout_id': 5, 'stacked_on_device_id': None},
        {'device_layout_id': 6, 'stacked_on_device_id': None},
        {'device_layout_id': 7, 'stacked_on_device_id': None},
        {'device_layout_id': 8, 'stacked_on_device_id': None},
    ]

    DRAWERS_IP_ADDRESS_DATA = [
        {"device_id": csr_device_id, 'container_id': 1, 'drawer_number': 'A-1', 'ip_address': '192.168.100.14:10001',
         'mac_address': '70:B3:D5:2B:50:00', 'created_by': 1, 'modified_by': 1},
        {"device_id": csr_device_id, 'container_id': 2, 'drawer_number': 'A-2', 'ip_address': '192.168.100.17:10001',
         'mac_address': '70:B3:D5:2B:50:01', 'created_by': 1, 'modified_by': 1},
        {"device_id": csr_device_id, 'container_id': 3, 'drawer_number': 'A-3', 'ip_address': '192.168.100.22:10001',
         'mac_address': '70:B3:D5:2B:50:02', 'created_by': 1, 'modified_by': 1},
        {"device_id": csr_device_id, 'container_id': 4, 'drawer_number': 'A-4', 'ip_address': '192.168.100.8:10001',
         'mac_address': '70:B3:D5:2B:50:03', 'created_by': 1, 'modified_by': 1},
        {"device_id": csr_device_id, 'container_id': 5, 'drawer_number': 'A-5', 'ip_address': '192.168.100.5:10001',
         'mac_address': '70:B3:D5:2B:50:04', 'created_by': 1, 'modified_by': 1},
        {"device_id": csr_device_id, 'container_id': 6, 'drawer_number': 'A-6', 'ip_address': '192.168.100.11:10001',
         'mac_address': '70:B3:D5:2B:50:05', 'created_by': 1, 'modified_by': 1},
        {"device_id": csr_device_id, 'container_id': 7, 'drawer_number': 'A-7', 'ip_address': '192.168.100.20:10001',
         'mac_address': '70:B3:D5:2B:50:06', 'created_by': 1, 'modified_by': 1},

    ]
    print(DRAWERS_IP_ADDRESS_DATA)


    insert_device_master_data(DEVICE_MASTER_DATA)
    insert_device_layout_data(DEVICE_LAYOUT_DETAILS_DATA)
    insert_device_properties_data(DEVICE_PROPERTIES_DATA)
    insert_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST, settings.DEVICE_TYPES['CSR'])
    insert_stacked_devices_data()

    insert_csr_drawers_data(DRAWERS_IP_ADDRESS_DATA)
    #
    # setup_custom_ca_bundle()
    #
    # # generate_couch_db_documents_for_all_csrs(DEVICE_MASTER_DATA)
    add_sequence_name_for_dosepacker_system()


def setup_custom_ca_bundle():
    cafile_path = os.path.join(
        settings.CUSTOM_CA_BUNDLE_PATH,
        settings.CUSTOM_CA_BUNDLE_FILE
    )
    os.environ['SSL_CERT_FILE'] = cafile_path
    os.environ["REQUESTS_CA_BUNDLE"] = cafile_path


def insert_units():
    UnitMaster.create(name='centimeter', type='length', symbol='cm')
    UnitMaster.create(name='meter', type='length', symbol='m')
    UnitMaster.create(name='foot', type='length', symbol='ft')
    UnitMaster.create(name='rupees', type='currency', symbol='rs')
    UnitMaster.create(name='millimeter', type='length', symbol='mm')
    UnitMaster.create(name='inch', type='length', symbol='in')
    UnitMaster.create(name='yard', type='length', symbol='yd')


def insert_unit_conversion():
    UnitConversion.create(convert_from_id=5, convert_to_id=1, conversion_ratio=0.10)
    UnitConversion.create(convert_from_id=1, convert_to_id=5, conversion_ratio=10)
    UnitConversion.create(convert_from_id=5, convert_to_id=2, conversion_ratio=0.001)
    UnitConversion.create(convert_from_id=2, convert_to_id=5, conversion_ratio=1000)
    UnitConversion.create(convert_from_id=5, convert_to_id=3, conversion_ratio=0.003281)
    UnitConversion.create(convert_from_id=3, convert_to_id=5, conversion_ratio=304.8)
    UnitConversion.create(convert_from_id=5, convert_to_id=6, conversion_ratio=0.0393701)
    UnitConversion.create(convert_from_id=6, convert_to_id=5, conversion_ratio=25.4)
    UnitConversion.create(convert_from_id=5, convert_to_id=7, conversion_ratio=0.0277778)
    UnitConversion.create(convert_from_id=7, convert_to_id=5, conversion_ratio=36)


def insert_device_types_data():
    try:
        DeviceTypeMaster.insert_many(DEVICE_TYPES).execute()
    except Exception as e:
        print("Exception came in inserting device types data")
        raise e


def insert_zones():
    try:
        ZoneMaster.insert_many(ZONE_DATA).execute()
    except Exception as e:
        print("Exception in inserting zone data: ", e)
        raise e


def insert_device_master_data(DEVICE_MASTER_DATA):
    try:
        DeviceMaster.insert_many(DEVICE_MASTER_DATA).execute()
    except Exception as e:
        print('Exception came in inserting device_master data: ', e)
        raise e


def insert_device_layout_data(DEVICE_LAYOUT_DETAILS_DATA):
    try:
        DeviceLayoutDetails.insert_many(DEVICE_LAYOUT_DETAILS_DATA).execute()
    except Exception as e:
        print("Exception in inserting DEVICE LAYOUT DATA data")
        raise e


def insert_device_properties_data(DEVICE_PROPERTIES_DATA):
    try:
        DeviceProperties.insert_many(DEVICE_PROPERTIES_DATA).execute()
    except Exception as e:
        print("Exception in inserting device properties data.")
        raise e


def insert_location_data(DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST, device_type):
    try:
        for device in DEVICE_ID_TO_MAX_LOCATION_MAPPING_LIST:
            data_list = []
            if device_type == settings.DEVICE_TYPES['CSR']:
                locations_data = prepare_data_for_csr_locations(total_drawers=device['total_drawers'],
                                                                locations_per_drawer=device.get('locations_per_drawer',
                                                                                                12),
                                                                device_id=device['device_id'],
                                                                drawer_initials='decimal',
                                                                csr_name=device['shelf_name'])
            else:
                locations_data = prepare_data_for_robot_locations(total_drawers=device['total_drawers'],
                                                                  locations_per_drawer=device.get(
                                                                      'locations_per_drawer', 12),
                                                                  device_id=device['device_id'],
                                                                  drawer_per_row=4)

            data_list.extend(locations_data)
            print(data_list)
            LocationMaster.insert_many(data_list).execute()
    except Exception as e:
        print("Exception came in inserting location data: ", e)
        raise e


def insert_stacked_devices_data(stacked_devices_data=None):
    if stacked_devices_data is None:
        stacked_devices_data = STACKED_DEVICES_DATA
    try:
        StackedDevices.insert_many(stacked_devices_data).execute()
    except Exception as e:
        print('Exception came in inserting stacked devices data')





def add_mac_address_drawer_status_column_in_canister_drawers():
    try:
        with db.atomic():
            # init_db(db, 'database_dev')
            migrator = MySQLMigrator(db)
            migrate(
                migrator.add_column(CanisterDrawers._meta.db_table,
                                    CanisterDrawers.mac_address.db_column,
                                    CanisterDrawers.mac_address
                                    ),
                migrator.add_column(CanisterDrawers._meta.db_table,
                                    CanisterDrawers.drawer_status.db_column,
                                    CanisterDrawers.drawer_status
                                    )
            )
            print('column added in CanisterDrawers')
    except Exception as e:
        print('Exception got in adding location column in cansiter master: ', e)



def insert_csr_drawers_data(drawers_ip_address_data):
    try:
        query = CanisterDrawers.insert_many(drawers_ip_address_data).execute()

        return True
    except Exception as e:
        raise e


def add_sequence_name_for_dosepacker_system():
    try:
        SequenceGenerator.create(seq_name=settings.SECONDARY_STORAGE_RACK_SEQ_NAME, seq_no=0, company_id=3, system_id=2)
    except Exception as e:
        print('Exception got in generating the sequence: ', e)


if __name__ == "__main__":
    migrate_temp()