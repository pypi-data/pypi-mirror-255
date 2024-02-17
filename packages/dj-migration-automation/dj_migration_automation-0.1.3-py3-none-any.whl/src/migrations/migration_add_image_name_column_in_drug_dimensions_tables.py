import logging

from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_dimention_history import DrugDimensionHistory

logger = logging.getLogger("root")


def add_columns_image_name_in_drug_dimension_history():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(DrugDimensionHistory._meta.db_table,
                                DrugDimensionHistory.image_name.db_column,
                                DrugDimensionHistory.image_name)
        )
        print("Added column image_name in DrugDimensionHistory")
    except Exception as e:
        logger.error("Error while adding columns in DrugDimensionHistory: ", str(e))


if __name__ == "__main__":
    add_columns_image_name_in_drug_dimension_history()
    # add_columns_image_name_in_drug_dimension()
#