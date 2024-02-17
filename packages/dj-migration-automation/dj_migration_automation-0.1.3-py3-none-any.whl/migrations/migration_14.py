from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class DrugMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class CanisterRegister(BaseModel):  # To store register canister recommendation
    id = PrimaryKeyField()
    system_id = IntegerField()
    drug_id = ForeignKeyField(DrugMaster)
    canister_quantity = SmallIntegerField(default=1)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_register"


def migrate_14():
    init_db(db, 'database_migration')

    db.create_tables([CanisterRegister], safe=True)
    print("Tables(s) Created: CanisterRegister")
