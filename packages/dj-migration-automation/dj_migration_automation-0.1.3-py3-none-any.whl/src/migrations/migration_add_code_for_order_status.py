from playhouse.migrate import MySQLMigrator

from dosepack.base_model.base_model import db
from model.model_init import init_db
from settings import logger
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_group_master import GroupMaster


def migration_add_code_for_order_status():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if GroupMaster.table_exists():
            GroupMaster.insert(id=constants.ORDER_STATUS_GROUP_ID,
                               name="OrderStatus").execute()

        if CodeMaster.table_exists():
            # codes for canister testing
            CodeMaster.insert(id=constants.PENDING_ORDER,
                              group_id=constants.ORDER_STATUS_GROUP_ID,
                              value="Pending").execute()

            CodeMaster.insert(id=constants.SHIPPED_ORDER,
                              group_id=constants.ORDER_STATUS_GROUP_ID,
                              value="Shipped").execute()

            CodeMaster.insert(id=constants.DELIVERED_ORDER,
                              group_id=constants.ORDER_STATUS_GROUP_ID,
                              value="Delivered").execute()

            print("Data inserted in the CodeMaster table for order status")

    except Exception as e:
        logger.error("Error while adding Code Master ", str(e))


if __name__ == "__main__":
    migration_add_code_for_order_status()
