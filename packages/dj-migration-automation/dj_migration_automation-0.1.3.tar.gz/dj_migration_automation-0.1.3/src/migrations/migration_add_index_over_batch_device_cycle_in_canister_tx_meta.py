
from peewee import InternalError, IntegrityError
from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from src.model.model_canister_tx_meta import CanisterTxMeta
from model.model_init import init_db



def update_index(migrator):
    migrate(
        migrator.add_index(CanisterTxMeta._meta.db_table,
                           (CanisterTxMeta.batch_id.db_column, CanisterTxMeta.cycle_id.db_column, CanisterTxMeta.device_id.db_column),
                           unique=True),

    )
    print("Unique Index modified for DrugDetails table.")


def migration_added_index_in_canister_tx_meta():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    update_index(migrator)

    print("Migration completed.")


if __name__ == "__main__":
    migration_added_index_in_canister_tx_meta()
