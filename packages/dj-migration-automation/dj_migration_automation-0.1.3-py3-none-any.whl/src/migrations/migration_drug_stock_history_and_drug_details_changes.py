import settings
from playhouse.migrate import *

from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from peewee import *
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster


class DrugStockHistory(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, related_name="drug_stock_history_ud_id")
    company_id = IntegerField(null=True)
    is_in_stock = SmallIntegerField(null=True)
    is_active = BooleanField(default=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_stock_history"


class DrugDetails(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True, related_name="drug_details_ud_id")
    company_id = IntegerField(null=True)
    last_seen_by = IntegerField()
    last_seen_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_details"


def add_column_company_id():
    company_id=3
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    if DrugStockHistory.table_exists():
        migrate(
            migrator.add_column(DrugStockHistory._meta.db_table,
                                DrugStockHistory.company_id.db_column,
                                DrugStockHistory.company_id)
        )
        print("Added column in DrugStockHistory")
        DrugStockHistory.update(company_id=company_id).where(DrugStockHistory.unique_drug_id.is_null(False)).execute()
        print("Updated company id for the existing records")

    if DrugDetails.table_exists():
        migrate(
            migrator.add_column(DrugDetails._meta.db_table,
                                DrugDetails.company_id.db_column,
                                DrugDetails.company_id)
        )
        print("Added column in DrugDetails")
        DrugDetails.update(company_id=company_id).where(DrugDetails.unique_drug_id.is_null(False)).execute()
        print("Updated company id for the existing records")



if __name__ == "__main__":
    add_column_company_id()
