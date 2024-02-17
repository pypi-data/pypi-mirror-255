from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, DecimalField

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_inventroy_transaction_history import InventoryTransactionHistory


def create_inventroy_transation_history():

    try:

        init_db(db, 'database_migration')

        if not InventoryTransactionHistory.table_exists():
            db.create_tables([InventoryTransactionHistory], safe=True)
            print('Table(s) created: PackVerificationDetails')

    except Exception as e:
        print(e)
        raise


if __name__ == "__main__":
    create_inventroy_transation_history()

