from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, DecimalField
from playhouse.migrate import MySQLMigrator, migrate

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_drug_dimension import DrugDimension

from src.model.model_drug_dimention_history import DrugDimensionHistory
from src.model.model_unique_drug import UniqueDrug


def migration_create_drug_dimension_history_table():

    try:

        init_db(db, 'database_migration')

        if not DrugDimensionHistory.table_exists():
            db.create_tables([DrugDimensionHistory], safe=True)
            print('Table(s) created: DrugDimensionHistory')

    except Exception as e:
        print(e)
        raise


if __name__ == "__main__":
    migration_create_drug_dimension_history_table()

