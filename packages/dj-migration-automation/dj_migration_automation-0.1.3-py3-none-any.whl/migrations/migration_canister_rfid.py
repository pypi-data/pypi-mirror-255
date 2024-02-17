from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


class DrugMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class LocationMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=36)
    available_quantity = SmallIntegerField()
    # canister_number = SmallIntegerField(default=0, null=True)
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
    location_id = ForeignKeyField(LocationMaster, null=True, unique=True)
    product_id = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


def migrate_79():
    """
    This migration is to update the max-length of the rfid column to 36 for the EEPROM values of v3 type canisters.
    @return:
    """
    init_db(db, "database_migration")

    db.execute_sql("ALTER TABLE canister_master MODIFY rfid char(32)")
    print("Tables modified: CanisterMaster")


if __name__ == '__main__':
    migrate_79()
