import logging

from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src.model.model_unique_drug import UniqueDrug

logger = logging.getLogger("root")


def add_columns_is_powder_pill_in_UniqueDrug():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(UniqueDrug._meta.db_table,
                                UniqueDrug.is_powder_pill.db_column,
                                UniqueDrug.is_powder_pill)
        )
        print("Added column is_powder_pill in UniqueDrug")
    except Exception as e:
        logger.error("Error while adding columns in UniqueDrug: ", str(e))
