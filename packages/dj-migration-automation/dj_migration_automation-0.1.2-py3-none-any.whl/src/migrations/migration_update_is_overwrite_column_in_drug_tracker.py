import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_drug_tracker import DrugTracker


def update_is_overwrite_filled_at_column_in_drug_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if DrugTracker.table_exists():
            sql = 'ALTER TABLE drug_tracker MODIFY is_overwrite smallint NOT NULL default 0;'
            db.execute_sql(sql)
            print("Datatype of the is_overwrite column is updated")

            sql = 'ALTER TABLE drug_tracker MODIFY filled_at int default Null;'
            db.execute_sql(sql)
            print("filled_at column is updated")
    except Exception as e:
        settings.logger.error("Error while updating column in drug_tracker: ", str(e))


if __name__ == "__main__":
    update_is_overwrite_filled_at_column_in_drug_tracker()
