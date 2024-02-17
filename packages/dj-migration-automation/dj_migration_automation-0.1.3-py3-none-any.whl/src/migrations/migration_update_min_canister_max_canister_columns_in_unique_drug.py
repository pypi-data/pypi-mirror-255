import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_unique_drug import UniqueDrug


def update_min_canister_max_canister_in_drug_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if UniqueDrug.table_exists():
            sql = 'ALTER TABLE unique_drug MODIFY min_canister varchar(3) NOT NULL default 2;'
            db.execute_sql(sql)
            print("min_canister column is updated")

            sql = 'ALTER TABLE unique_drug MODIFY max_canister varchar(3) NOT NULL default 2;'
            db.execute_sql(sql)
            print("max_canister column is updated")
    except Exception as e:
        settings.logger.error("Error while updating column in unique_drug: ", str(e))


if __name__ == "__main__":
    update_min_canister_max_canister_in_drug_tracker()
