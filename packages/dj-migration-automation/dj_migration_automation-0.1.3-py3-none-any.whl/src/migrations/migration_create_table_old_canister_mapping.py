from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_old_canister_mapping import OldCanisterMapping


def migration_create_table_old_canister_mapping():
    init_db(db, 'database_migration')
    if not OldCanisterMapping.table_exists():
        db.create_tables([OldCanisterMapping], safe=True)
        print('Table(s) created: OldCanisterMapping')


if __name__ == "__main__":
    migration_create_table_old_canister_mapping()
