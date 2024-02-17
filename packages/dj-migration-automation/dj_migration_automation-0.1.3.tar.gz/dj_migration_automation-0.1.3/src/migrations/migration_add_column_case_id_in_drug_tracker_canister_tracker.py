from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_drug_tracker import DrugTracker
from src.model.model_inventroy_transaction_history import InventoryTransactionHistory


def add_column_case_id_in_drug_tracker_and_canister_tracker():
    init_db(db, "database_migration")
    # migrator = SchemaMigrator(db)
    migrator = MySQLMigrator(db)

    print("Migration start : Adding case_id column to drug_tracker, drug_lot_master, canister_tracker ")

    try:
        with db.transaction():

            migrate(
                migrator.add_column(CanisterTracker._meta.db_table,
                                    CanisterTracker.case_id.db_column,
                                    CanisterTracker.case_id)
            )
            migrate(
                migrator.add_column(DrugLotMaster._meta.db_table,
                                    DrugLotMaster.case_id.db_column,
                                    DrugLotMaster.case_id)
            )
            migrate(
                migrator.add_column(DrugTracker._meta.db_table,
                                    DrugTracker.case_id.db_column,
                                    DrugTracker.case_id)
            )
            migrate(
                migrator.add_column(InventoryTransactionHistory._meta.db_table,
                                    InventoryTransactionHistory.caseId.db_column,
                                    InventoryTransactionHistory.caseId)
            )
    except Exception as e:
        print("error", e)


if __name__ == "__main__":
    add_column_case_id_in_drug_tracker_and_canister_tracker()
    print("column case_id is added")
