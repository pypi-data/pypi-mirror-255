from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class CustomDrugShape(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'custom_drug_shape'


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


class DrugDimension(BaseModel):
    """
    It contain the data related to drug dimensions.
    """
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True)
    width = DecimalField(decimal_places=3, max_digits=6)  # in mm
    length = DecimalField(decimal_places=3, max_digits=6)  # in mm
    depth = DecimalField(decimal_places=3, max_digits=6)  # in mm
    fillet = DecimalField(decimal_places=3, max_digits=6, null=True)
    approx_volume = DecimalField(decimal_places=6, max_digits=10)  # in mm^3
    # approx_volume must be calculated using length*width*depth on every insert and update
    accurate_volume = DecimalField(decimal_places=6, max_digits=10, null=True)  # in mm^3  # provided by user
    shape = ForeignKeyField(CustomDrugShape, null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)
    verification_status_id = ForeignKeyField(CodeMaster, default=settings.DRUG_VERIFICATION_STATUS['pending'])
    verified_by = IntegerField(default=None, null=True)  # verification needs to be done by second pharmacy tech.
    verified_date = DateTimeField(default=None, null=True)
    rejection_note = CharField(default=None, null=True, max_length=1000)
    unit_weight = DecimalField(default=None, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension'


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


def migrate_refill_device():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(DrugDimension._meta.db_table, DrugDimension.unit_weight.db_column,
                            DrugDimension.unit_weight)
    )
    print("Column added in DrugDimension")
    if DeviceMaster.table_exists():
        DeviceMaster.create(company_id=4, name='REFILL_DEVICE_1', serial_number='RFL1', device_type_id=5, active=1,
                            version=1.0,
                            created_date=get_current_date_time(), modified_date=get_current_date_time())
    print("Added Refill Device in DeviceMaster Table")


if __name__ == '__main__':
    migrate_refill_device()
