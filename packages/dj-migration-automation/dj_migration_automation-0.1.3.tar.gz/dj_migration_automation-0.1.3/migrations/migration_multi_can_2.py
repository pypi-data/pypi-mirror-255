from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    # drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=20)
    available_quantity = SmallIntegerField()
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
    # location_id = ForeignKeyField(LocationMaster, null=True, unique=True)
    product_id = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


def migrate_canister():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if CanisterMaster.table_exists():
        migrate(
            migrator.add_column(
                CanisterMaster._meta.db_table,
                CanisterMaster.product_id.db_column,
                CanisterMaster.product_id
            )
        )

        print("Table Modified: CanisterMaster")


if __name__ == "__main__":
    migrate_canister()
