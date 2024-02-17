import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_canister_master import CanisterMaster

def add_column_in_canister_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            if CanisterMaster.table_exists():
                migrate(migrator.add_column(CanisterMaster._meta.db_table,
                                            CanisterMaster.threshold.db_column,
                                            CanisterMaster.threshold
                                            )
                        )
                print("Added threshold column in Canister_Master")
    except Exception as e:
        settings.logger.error("Error while adding columns in Canister_Master: ", str(e))


if __name__ == "__main__":
    add_column_in_canister_master()
