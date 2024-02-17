from playhouse.migrate import MySQLMigrator

import settings
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_pack_error import PackError


def migration_add_pack_error_table():

    init_db(db, 'database_migration')

    if PackError.table_exists():
        db.drop_table(PackError)
        print('Table(s) dropped: PackError')

    if not PackError.table_exists():
        db.create_tables([PackError], safe=True)
        print('Table(s) created: PackError')


def migration_add_codes_for_ips_pack_error():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if CodeMaster.table_exists():
            # codes for canister testing
            CodeMaster.insert(id=constants.IPS_PACK_ERROR_CODE,
                              group_id=constants.PACK_VERIFICATION_STATUS_GROUP_ID,
                              value="Marked as Error in Filling from IPS").execute()

            print("Data inserted in the CodeMaster table.")

    except Exception as e:
        settings.logger.error("Error while adding Code Master ", str(e))


if __name__ == "__main__":
    migration_add_pack_error_table()
    migration_add_codes_for_ips_pack_error()
