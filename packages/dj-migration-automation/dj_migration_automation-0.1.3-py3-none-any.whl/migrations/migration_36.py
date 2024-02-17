from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
from src.model.model_patient_master import PatientMaster
from playhouse.migrate import *
import settings


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"



class DrugMaster(BaseModel):
    """
        @class: drug_master.py
        @createdBy: Manish Agarwal
        @createdDate: 04/19/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/19/2016
        @type: file
        @desc: logical class for table drug_master
    """
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


class DrugLotMaster(BaseModel):
    """
    Database table to manager the data about each lot of drugs
    """
    id = PrimaryKeyField()
    drug_id = ForeignKeyField(DrugMaster)
    lot_number = CharField()
    expiry_date = CharField()
    total_packages = IntegerField()
    company_id = IntegerField()
    is_recall = BooleanField(default=False)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_lot_master"


class DrugBottleMaster(BaseModel):
    """
    Class to maintain inventory of all the bottles of the drugs registered
    """
    id = PrimaryKeyField()
    drug_lot_master_id = ForeignKeyField(DrugLotMaster)
    available_quantity = IntegerField()
    total_quantity = IntegerField()
    serial_number = CharField(null=True)
    rfid = CharField(max_length=12, null=True)
    data_matrix_type = SmallIntegerField()  # 0: Drug bottle, 1: Dosepacker
    label_printed = BooleanField(default=False)
    is_deleted = BooleanField(default=False)
    bottle_location = CharField(null=True)
    company_id = IntegerField()
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_bottle_master"


class DrugBottleTracker(BaseModel):
    """
    Table to store the update in quantity of the Bottle
    """
    id = PrimaryKeyField()
    bottle_id = DrugBottleMaster()
    quantity_adjusted = SmallIntegerField()
    action_performed = ForeignKeyField(ActionMaster)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_bottle_tracker"

def migrate_36():
    init_db(db, 'database_migration')

    if DrugBottleTracker.table_exists():
        db.drop_tables([DrugBottleTracker])
        print("Table dropped: DrugBottleTracker")

    if DrugBottleMaster.table_exists():
        db.drop_tables([DrugBottleMaster])
        print("Table dropped: DrugBottleMaster")

    if DrugLotMaster.table_exists():
        db.drop_tables([DrugLotMaster])
        print("Table dropped: DrugLotMaster")

    if ActionMaster.table_exists():
        db.drop_tables([ActionMaster])
        print("Table dropped: ActionMaster")


    db.create_tables([ActionMaster, DrugLotMaster, DrugBottleMaster, DrugBottleTracker], safe=True)
    GroupMaster.create(name="DrugBottle")
    ActionMaster.create(group_id=9, key=1, value="AddQuantity")
    ActionMaster.create(group_id=9, key=2, value="SubtractQuantity")
    print("Table created: ActionMaster, DrugLotMaster, DrugBottleMaster, DrugBottleTracker")


if __name__ == "__main__":
    migrate_36()

