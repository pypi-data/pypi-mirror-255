from dosepack.base_model.base_model import db
from playhouse.migrate import *
from model.model_init import init_db
from src.model.model_batch_master import BatchMaster


def add_column_sequence():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        #  add column sequence no in batch master in order to maintain module in pack preprocessing screen
        if BatchMaster.table_exists():
            migrate(migrator.add_column(
                BatchMaster._meta.db_table,
                BatchMaster.sequence_no.db_column,
                BatchMaster.sequence_no))
            print("Added column in BatchMaster Table")
    except Exception as e:
        print("Error while adding columns in BatchMaster: ", str(e))
        raise


if __name__ == "__main__":
    add_column_sequence()
