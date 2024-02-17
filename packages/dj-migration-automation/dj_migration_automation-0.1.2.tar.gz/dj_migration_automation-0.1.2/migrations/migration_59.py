from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
import settings


class RobotMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    company_id = IntegerField()
    name = CharField(max_length=150)
    serial_number = FixedCharField(unique=True, max_length=10)
    version = FixedCharField(max_length=11)
    active = BooleanField(default=True)
    max_canisters = SmallIntegerField() # number of canisters that robot can hold
    big_drawers = IntegerField(default=4) # number of big drawers that robot holds
    small_drawers = IntegerField(default=12) # number of small drawers that robot holds
    # controller used 'AR' for ardiuno and 'BB' for beagle bone 'BBB' for beagle bone black
    controller = CharField(max_length=10, default="AR")
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "robot_master"


class DrugMaster(BaseModel):
    id = PrimaryKeyField()
    drug_name = CharField(max_length=255)
    ndc = CharField(max_length=14, unique=True)
    formatted_ndc = CharField(max_length=12, null=True)
    strength = CharField(max_length=50)
    strength_value = CharField(max_length=16)
    manufacturer = CharField(null=True, max_length=100)
    txr = CharField(max_length=8, null=True)
    imprint = CharField(null=True, max_length=82)
    color = CharField(null=True, max_length=30)
    shape = CharField(null=True, max_length=30)
    image_name = CharField(null=True, max_length=255)
    brand_flag = CharField(null=True, max_length=1)
    brand_drug = CharField(null=True, max_length=50)
    drug_form = CharField(null=True, max_length=15)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class CanisterMaster(BaseModel):
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
    label_print_time = DateTimeField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class CanisterTracker(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    robot_id = ForeignKeyField(RobotMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster)
    refill_type = SmallIntegerField(null=True)
    quantity_adjusted = SmallIntegerField()
    original_quantity = SmallIntegerField()
    lot_number = CharField(max_length=30, null=True)
    expiration_date = CharField(max_length=8, null=True)
    note = CharField(null=True, max_length=100)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    created_time = TimeField()
    voice_notification_uuid = CharField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tracker"


def add_voice_notification_uuid_column():
    try:
        migrator = MySQLMigrator(db)
        migrate(
            migrator.add_column(CanisterTracker._meta.db_table,
                                CanisterTracker.voice_notification_uuid.db_column,
                                CanisterTracker.voice_notification_uuid
                                )
        )
        print('New column added successfully in Canister Tracker table')
    except Exception as e:
        print('Exception got in adding voice_notification_uuid column in canister tracker table: ', e)


def migrate_59():
    print('Migration 59 starts')
    init_db(db, "database_migration")
    add_voice_notification_uuid_column()


