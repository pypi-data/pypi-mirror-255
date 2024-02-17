from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_slot_details import SlotDetails


class SlotTransaction(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    # slot_id = ForeignKeyField(SlotDetails)
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    # drug_id = ForeignKeyField(DrugMaster, related_name="SlotTransaction_drug_id")
    # canister_id = ForeignKeyField(CanisterMaster, related_name="SlotTransaction_canister_id", null=True)
    canister_number = SmallIntegerField(null=True)
    # alternate_drug_id = ForeignKeyField(DrugMaster, null=True, related_name="SlotTransaction_alt_drug_id")
    # alternate_canister_id = ForeignKeyField(CanisterMaster, null=True, related_name="SlotTransaction_alt_canister_id")
    dropped_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    mft_drug = BooleanField(default=False)
    IPS_update_alt_drug = BooleanField(null=True)
    IPS_update_alt_drug_error = CharField(null=True, max_length=150)
    created_by = IntegerField()
    created_date_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_transaction"


class MftDrugSlotDetails(BaseModel):
    id = PrimaryKeyField()
    slot_id = ForeignKeyField(SlotDetails, unique=True)
    qty = DecimalField(decimal_places=2, max_digits=4)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mft_drug_slot_details"


def migrate_mft_changes():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    if SlotTransaction.table_exists():
        migrate(
            migrator.add_column(
                SlotTransaction._meta.db_table,
                SlotTransaction.mft_drug.db_column,
                SlotTransaction.mft_drug
            )
        )

    print('Table(s) updated: SlotTransaction')

    db.create_tables([MftDrugSlotDetails], safe=True)

    print('Table(s) created: MftDrugSlotDetails')


if __name__ == '__main__':
    migrate_mft_changes()
