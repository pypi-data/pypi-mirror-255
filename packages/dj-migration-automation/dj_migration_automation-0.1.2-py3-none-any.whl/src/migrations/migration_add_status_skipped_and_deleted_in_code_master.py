import datetime

from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db
from model.model_init import init_db

from src import constants
from src.model.model_code_master import CodeMaster


def migration_add_status_skipped_and_deleted_in_code_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if CodeMaster.table_exists():
            # codes for canister testing
            CodeMaster.insert(id=constants.SKIPPED_AND_DELETED,
                              group_id=constants.SKIPPED_AND_MAPPED_RTS_DRUG_STATUS_ID,
                              value="Skipped And Deleted").execute()

            print("Data inserted in the CodeMaster table.")

    except Exception as e:
        settings.logger.error("Error while adding Code Master ", str(e))


if __name__ == "__main__":
    migration_add_status_skipped_and_deleted_in_code_master()