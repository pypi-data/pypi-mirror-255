import settings
from playhouse.migrate import *
from model.model_init import init_db
from src.model.model_code_master import CodeMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_slot_details import SlotDetails
from src.model.model_pack_details import PackDetails
from dosepack.base_model.base_model import db, BaseModel
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_canister_master import CanisterMaster
from dosepack.utilities.utils import get_current_date_time
from src.model.model_canister_tracker import CanisterTracker


class DrugTracker(BaseModel):
    id = PrimaryKeyField()
    slot_id = ForeignKeyField(SlotDetails)
    canister_id = ForeignKeyField(CanisterMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster)
    drug_quantity = DecimalField(decimal_places=2, max_digits=4)
    canister_tracker_id = ForeignKeyField(CanisterTracker, null=True)
    comp_canister_tracker_id = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    # is_deleted = BooleanField(default=False)
    drug_lot_master_id = ForeignKeyField(DrugLotMaster, null=True)
    filled_at = IntegerField(default=None)
    created_by = IntegerField(default=1)
    pack_id = ForeignKeyField(PackDetails, null=True)
    is_overwrite = SmallIntegerField(default=0)
    scan_type = ForeignKeyField(CodeMaster, default=None, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    case_id = CharField(null=True, default=None)
    reuse_quantity = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    reuse_pack = IntegerField(null=True, default=None)
    item_id = CharField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_tracker"


def db_drop_reuse_quantity_column_in_drug_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            if DrugTracker.table_exists():
                migrate(migrator.drop_column(DrugTracker._meta.db_table,
                                             DrugTracker.reuse_quantity.db_column
                                             )
                        )

                print("reuse_quantity column is dropped")
    except Exception as e:
        settings.logger.error("Error while dropping reuse_quantity column in drug_tracker: ", str(e))


if __name__ == "__main__":
    db_drop_reuse_quantity_column_in_drug_tracker()