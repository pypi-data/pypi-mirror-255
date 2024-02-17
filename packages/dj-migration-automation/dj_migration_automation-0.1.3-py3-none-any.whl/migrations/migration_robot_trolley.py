from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


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

        indexes = (
            (('name', 'company_id'), True),
        )


CURRENT_DATE = get_current_date_time()

DEVICE_MASTER_DATA = {'company_id': 3, 'name': 'Robot-Trolley-1-v3', 'serial_number': 'RBTV30344',
                      'device_type_id': settings.DEVICE_TYPES["Drug Dispenser Trolley"],
                      'system_id': None, 'version': '2', 'max_canisters': None, 'big_drawers': None,
                      'small_drawers': None,
                      'controller': None,
                      'created_by': 2, 'modified_by': 2, 'active': 1, 'created_date': CURRENT_DATE,
                      'modified_date': CURRENT_DATE, 'associated_device': None, 'ip_address': None}


def migrate_mfd():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            DeviceMaster._meta.db_table,
            DeviceMaster.associated_device.db_column,
            DeviceMaster.associated_device
        ),
        migrator.add_column(
            DeviceMaster._meta.db_table,
            DeviceMaster.ip_address.db_column,
            DeviceMaster.ip_address
        )
    )
    print("associated_device and ip_address columns added in device master")
    DeviceTypeMaster.create(**{'id': settings.DEVICE_TYPES['ROBOT_TROLLEY'], 'device_type_name': 'Robot Trolley'})
    print(" Data in device type master added")
    DeviceMaster.create(**DEVICE_MASTER_DATA)
    print(" Data in device master added")


if __name__ == "__main__":
    migrate_mfd()
