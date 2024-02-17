from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    # drug_id = ForeignKeyField(DrugMaster)
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


def migrate_52():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            CanisterMaster._meta.db_table,
            CanisterMaster.label_print_time.db_column,
            CanisterMaster.label_print_time
        )
    )
    CanisterMaster.update(label_print_time= get_current_date_time()).execute()
    print('Table(s) Updated: CanisterMaster')


if __name__ == '__main__':
    migrate_52()
