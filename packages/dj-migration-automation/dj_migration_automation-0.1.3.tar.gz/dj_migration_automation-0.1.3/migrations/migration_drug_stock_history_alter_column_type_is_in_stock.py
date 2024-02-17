import json
import base64

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date, get_current_time, get_current_date_time
from model.model_init import init_db
from src.model.model_print_queue import PrintQueue
from src.model.model_printers import Printers
from playhouse.migrate import *
from collections import defaultdict


class UniqueDrug(BaseModel):

    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "unique_drug"


class DrugStockHistory(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    is_in_stock = SmallIntegerField(null=True)
    is_active = BooleanField(default=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_stock_history"


def change_is_in_stock_column_type_in_drug_master():
    """
       This migration is to update the datatype of the is_in_stock column from BooleanField to SmallIntegerField
    """
    init_db(db, 'database_migration')
    db.execute_sql("ALTER TABLE drug_stock_history MODIFY is_in_stock smallint")
    print("Tables modified: DrugStockHistory")


if __name__ == '__main__':
    change_is_in_stock_column_type_in_drug_master()




