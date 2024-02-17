import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from peewee import *
from model.model_volumetric_analysis import BigCanisterStick, SmallCanisterStick
from src.model.model_canister_drum import CanisterDrum


class MfdCanisterMaster(BaseModel):
    id = PrimaryKeyField()
    rfid = FixedCharField(null=True, unique=True, max_length=32)
    # location_id = ForeignKeyField(LocationMaster, null=True, unique=True, related_name='mfd_loc_id')
    canister_type = CharField()
    active = BooleanField()
    label_print_time = DateTimeField(null=True, default=None)
    erp_product_id = IntegerField(null=True, unique=True)
    company_id = IntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    # home_cart_id = ForeignKeyField(DeviceMaster, null=True)
    fork_detected = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_master"


def add_fork_detected_mfd_canister_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(MfdCanisterMaster._meta.db_table,
                                MfdCanisterMaster.fork_detected.db_column,
                                MfdCanisterMaster.fork_detected)
        )
        print("Added column fork_detected in MfdCanisterMaster")
    except Exception as e:
        settings.logger.error("Error while adding columns in MfdCanisterMaster: ", str(e))


if __name__ == "__main__":
    add_fork_detected_mfd_canister_master()