from playhouse.migrate import MySQLMigrator

from dosepack.base_model.base_model import db
from model.model_init import init_db
from settings import logger
from src import constants
from src.model.model_code_master import CodeMaster


def migration_add_code_for_upc_scan_type():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if CodeMaster.table_exists():
            # codes for canister testing
            CodeMaster.insert(id=constants.UPC_SCAN,
                              group_id=constants.SCAN_TYPE_GROUP_ID,
                              value="UPC Scan").execute()

            print("Data inserted in the CodeMaster table for UPC scan.")

    except Exception as e:
        logger.error("Error while adding Code Master ", str(e))


if __name__ == "__main__":
    migration_add_code_for_upc_scan_type()
