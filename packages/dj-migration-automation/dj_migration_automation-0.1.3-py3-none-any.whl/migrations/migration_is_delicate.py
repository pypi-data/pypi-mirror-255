from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time


import settings
from src.model.model_unique_drug import UniqueDrug


def add_column_is_delicate():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    print("Migration start : Adding is_delicate column to unique drug table")

    try:
        with db.transaction():
            migrate(
                migrator.add_column(UniqueDrug._meta.db_table,
                                    UniqueDrug.is_delicate.db_column,
                                    UniqueDrug.is_delicate)
            )
    except Exception as e:
        print("error", e)


if __name__ == "__main__":
    add_column_is_delicate()
    print("column is_delicate added")
