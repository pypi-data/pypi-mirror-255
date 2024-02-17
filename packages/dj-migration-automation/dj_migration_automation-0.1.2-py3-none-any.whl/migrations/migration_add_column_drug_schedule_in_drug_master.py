import logging
from playhouse.migrate import *

from src.model.model_drug_master import DrugMaster
from dosepack.base_model.base_model import db
from model.model_init import init_db

logger = logging.getLogger("root")


def migration_for_adding_PRN_columns_in_drug_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(DrugMaster._meta.db_table,
                                DrugMaster.drug_schedule.db_column,
                                DrugMaster.drug_schedule)
        )
        migrate(
            migrator.add_column(DrugMaster._meta.db_table,
                                DrugMaster.package_size.db_column,
                                DrugMaster.package_size)
        )
        migrate(
            migrator.add_column(DrugMaster._meta.db_table,
                                DrugMaster.dispense_qty.db_column,
                                DrugMaster.dispense_qty)
        )
        print("drug_schedule, package_size and dispense_qty column added in DrugMaster")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    migration_for_adding_PRN_columns_in_drug_master()



