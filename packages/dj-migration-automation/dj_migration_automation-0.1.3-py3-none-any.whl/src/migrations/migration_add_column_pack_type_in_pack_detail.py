import logging

from playhouse.migrate import *

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_pack_details import PackDetails

logger = logging.getLogger("root")


def add_column_pack_type_status_in_pack_details():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate( 
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.pack_type.db_column,
                                PackDetails.pack_type)
        )
        print("add column pack_type in PackDetail")
    except Exception as e:
        logger.error("Error while adding column in PackDetail: ", str(e))


if __name__ == "__main__":
    add_column_pack_type_status_in_pack_details()
