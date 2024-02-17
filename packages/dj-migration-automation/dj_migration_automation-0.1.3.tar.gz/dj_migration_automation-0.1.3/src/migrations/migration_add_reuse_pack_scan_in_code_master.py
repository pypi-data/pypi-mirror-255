import settings
from src import constants
from playhouse.migrate import *
from model.model_init import init_db
from src.model.model_code_master import CodeMaster
from dosepack.base_model.base_model import db, BaseModel


def add_reuse_pack_scan_in_code_master():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        with (db.transaction()):
            if CodeMaster.table_exists():
                CodeMaster.insert(id=constants.REUSE_PACK_SCAN,
                                  group_id=constants.SCAN_TYPE_GROUP_ID,
                                  value="Reuse Pack Scan"
                                  ).execute()

                print("Reuse Pack Scan status added in code_master")

                CodeMaster.insert(id=constants.VIAL_SCAN,
                                  group_id=constants.SCAN_TYPE_GROUP_ID,
                                  value="Vial Scan"
                                  ).execute()

                print("Vial Scan status added in code_master")

    except Exception as e:
        settings.logger.error("Error in add_reuse_pack_scan_in_code_master: {}".format(e))
        raise e


if __name__ == "__main__":
    add_reuse_pack_scan_in_code_master()
