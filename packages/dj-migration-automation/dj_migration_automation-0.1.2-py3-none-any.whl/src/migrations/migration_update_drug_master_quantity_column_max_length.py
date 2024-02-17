from playhouse.migrate import MySQLMigrator

import settings
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_drug_master import DrugMaster


def migration_update_drug_master_quantity_column_max_length_threshold():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if DrugMaster.table_exists():
            sql = 'ALTER TABLE `drug_master` MODIFY `dispense_qty` DECIMAL(7,4) NOT NULL;'
            db.execute_sql(sql)
            print("Max digit of dispense quantity column in drug_master is updated to 7 ")
    except Exception as e:
        settings.logger.error("Error while updating column in drug_master: ", str(e))


if __name__ == "__main__":
    migration_update_drug_master_quantity_column_max_length_threshold()
