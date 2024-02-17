import json
import base64

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date, get_current_time
from model.model_init import init_db
from src.model.model_print_queue import PrintQueue
from src.model.model_printers import Printers
from playhouse.migrate import *
from collections import defaultdict


class OLDPrinters(BaseModel):
    id = PrimaryKeyField()
    printer_name = CharField(max_length=50)
    printer_type = SmallIntegerField(null=True, default=None)  # 1 = CRM, 2 = User Station
    unique_code = CharField(max_length=55, unique=True)
    ip_address = CharField()
    system_id = IntegerField()
    added_date = DateField(default=get_current_date)
    added_time = TimeField(default=get_current_time)

    class Meta:
         db_table = "printers"


class Printers(BaseModel):
    id = PrimaryKeyField()
    printer_name = CharField(max_length=50)
    printer_type = SmallIntegerField(null=True, default=None)  # 1 = CRM, 2 = User Station
    unique_code = CharField(max_length=55, unique=True)
    ip_address = CharField()
    system_id = IntegerField()
    added_date = DateField(default=get_current_date)
    added_time = TimeField(default=get_current_time)
    print_count = IntegerField(default=0)

    class Meta:
        db_table = "printers"


def migrate_81():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    if OLDPrinters.table_exists():
        migrate(
            migrator.add_column(Printers._meta.db_table,
                                Printers.print_count.db_column,
                                Printers.print_count)
        )
        print("column print_count added in table printers")


if __name__ == '__main__':
    migrate_81()

