from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


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
    lot_number = CharField(unique=True)
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


class DrugBottleQuantityTracker(BaseModel):
    id = PrimaryKeyField()
    lot_id = ForeignKeyField(DrugLotMaster)
    bottle_id = IntegerField(null=True)
    quantity_adjusted = SmallIntegerField()
    action_performed = ForeignKeyField(ActionMaster)
    bottle_qty_updated = BooleanField(default=False)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_bottle_quantity_tracker"


def migrate_43():

    init_db(db, 'database_migration')

    with db.transaction():
        db.create_tables([DrugBottleQuantityTracker])


if __name__ == '__main__':
    migrate_43()

