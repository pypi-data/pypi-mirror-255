from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_replenish_skipped_canister import ReplenishSkippedCanister


def migration_create_replenish_skipped_canister():
    init_db(db, 'database_migration')
    if not ReplenishSkippedCanister.table_exists():
        db.create_tables([ReplenishSkippedCanister], safe=True)
        print('Table(s) created: ReplenishSkippedCanister')


if __name__ == "__main__":
    migration_create_replenish_skipped_canister()
