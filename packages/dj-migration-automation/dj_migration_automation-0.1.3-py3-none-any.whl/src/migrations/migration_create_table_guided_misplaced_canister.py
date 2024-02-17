from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_guided_misplaced_canister import GuidedMisplacedCanister


def migration_create_guided_misplaced_canister():
    init_db(db, 'database_migration')
    if not GuidedMisplacedCanister.table_exists():
        db.create_tables([GuidedMisplacedCanister], safe=True)
        print('Table(s) created: GuidedMisplacedCanister')


if __name__ == "__main__":
    migration_create_guided_misplaced_canister()
