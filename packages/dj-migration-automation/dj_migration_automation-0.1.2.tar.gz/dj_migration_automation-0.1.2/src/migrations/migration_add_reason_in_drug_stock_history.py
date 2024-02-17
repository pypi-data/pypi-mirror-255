from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from playhouse.migrate import *
from src.model.model_drug_stock_history import DrugStockHistory


def add_column_reason_in_drug_stock_history():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            DrugStockHistory._meta.db_table,
            DrugStockHistory.reason.db_column,
            DrugStockHistory.reason
        )
    )
    print("associated_canister column added in DrugStockHistory table")


if __name__ == "__main__":
    # add associated_canister(canister_status_history id)in canister status history table
    add_column_reason_in_drug_stock_history()
