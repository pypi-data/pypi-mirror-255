from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_drug_tracker import DrugTracker


def add_item_id_column_in_drug_tracker():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        with db.transaction():
            if DrugTracker.table_exists():
                migrate(migrator.add_column(DrugTracker._meta.db_table,
                                            DrugTracker.item_id.db_column,
                                            DrugTracker.item_id
                                            )
                        )

                print("item_id column is successfully added in drug_tracker")
    except Exception as e:
        print("Error in add_item_id_column_in_drug_tracker: {}".format(e))
        raise e


if __name__ == "__main__":
    add_item_id_column_in_drug_tracker()