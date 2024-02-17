import src.constants
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class MfdCanisterTransferHistory(BaseModel):
    id = PrimaryKeyField()
    # mfd_canister_id = ForeignKeyField(MfdCanisterMaster)
    # current_location_id = ForeignKeyField(LocationMaster, null=True, related_name='mfd_current_location_id')
    # previous_location_id = ForeignKeyField(LocationMaster, null=True, related_name='mfd_previous_location_id')
    is_transaction_manual = BooleanField(default=False)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_transfer_history"


def migrate_transferred_manually():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            MfdCanisterTransferHistory._meta.db_table,
            MfdCanisterTransferHistory.is_transaction_manual.db_column,
            MfdCanisterTransferHistory.is_transaction_manual
        )
    )
    print('Table(s) Updated: MfdCanisterTransferHistory')


if __name__ == '__main__':
    migrate_transferred_manually()