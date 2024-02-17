from dosepack.base_model.base_model import db
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from model.model_init import init_db
from src.constants import DRUG_INVENTORY_MANAGEMENT_GROUP_ID, DRUG_INVENTORY_MANAGEMENT_GROUP_NAME, \
    DRUG_INVENTORY_MANAGEMENT_ADDED_ID, DRUG_INVENTORY_MANAGEMENT_ADDED_NAME, DRUG_INVENTORY_MANAGEMENT_UPDATED_ID, \
    DRUG_INVENTORY_MANAGEMENT_UPDATED_NAME, DRUG_INVENTORY_MANAGEMENT_DELETED_ID, \
    DRUG_INVENTORY_MANAGEMENT_DELETED_NAME, DRUG_INVENTORY_MANAGEMENT_ORDER_PENDING_ID, \
    DRUG_INVENTORY_MANAGEMENT_ORDER_PENDING_NAME, DRUG_INVENTORY_MANAGEMENT_ADDED_TO_CART_ID, \
    DRUG_INVENTORY_MANAGEMENT_ADDED_TO_CART_NAME
from src.model.model_batch_drug_data import BatchDrugData
from src.model.model_batch_drug_order_data import BatchDrugOrderData
from src.model.model_batch_drug_request_mapping import BatchDrugRequestMapping
from src.model.model_current_inventory_mapping import CurrentInventoryMapping
from src.model.model_pre_order_missing_ndc import PreOrderMissingNdc


def migration_drug_inventory():
    init_db(db, 'database_migration')
    print("Migration started for the Drug Inventory")
    drop_tables()
    create_tables()
    # insert_data()
    print("migration_drug_inventory completed successfully")


def drop_tables():
    db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
    db.drop_tables(
        [BatchDrugData, BatchDrugOrderData, BatchDrugRequestMapping, PreOrderMissingNdc, CurrentInventoryMapping],
        safe=True)
    db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
    print("Tables dropped: BatchDrugData, BatchDrugOrderData, BatchDrugRequestMapping," +
          " PreOrderMissingNdc, CurrentInventoryMapping")


def create_tables():
    db.create_tables(
        [BatchDrugData, BatchDrugOrderData, BatchDrugRequestMapping, PreOrderMissingNdc, CurrentInventoryMapping],
        safe=True)
    print("Tables Created: BatchDrugData, BatchDrugOrderData, BatchDrugRequestMapping," +
          " PreOrderMissingNdc, CurrentInventoryMapping")


def insert_data():
    if GroupMaster.table_exists():
        GroupMaster.insert(id=DRUG_INVENTORY_MANAGEMENT_GROUP_ID,
                           name=DRUG_INVENTORY_MANAGEMENT_GROUP_NAME).execute()
        print("Data inserted in GroupMaster table.")

    if CodeMaster.table_exists():
        CodeMaster.insert(id=DRUG_INVENTORY_MANAGEMENT_ADDED_ID, group_id=DRUG_INVENTORY_MANAGEMENT_GROUP_ID,
                          value=DRUG_INVENTORY_MANAGEMENT_ADDED_NAME).execute()
        CodeMaster.insert(id=DRUG_INVENTORY_MANAGEMENT_UPDATED_ID, group_id=DRUG_INVENTORY_MANAGEMENT_GROUP_ID,
                          value=DRUG_INVENTORY_MANAGEMENT_UPDATED_NAME).execute()
        CodeMaster.insert(id=DRUG_INVENTORY_MANAGEMENT_DELETED_ID, group_id=DRUG_INVENTORY_MANAGEMENT_GROUP_ID,
                          value=DRUG_INVENTORY_MANAGEMENT_DELETED_NAME).execute()
        CodeMaster.insert(id=DRUG_INVENTORY_MANAGEMENT_ORDER_PENDING_ID, group_id=DRUG_INVENTORY_MANAGEMENT_GROUP_ID,
                          value=DRUG_INVENTORY_MANAGEMENT_ORDER_PENDING_NAME).execute()
        CodeMaster.insert(id=DRUG_INVENTORY_MANAGEMENT_ADDED_TO_CART_ID, group_id=DRUG_INVENTORY_MANAGEMENT_GROUP_ID,
                          value=DRUG_INVENTORY_MANAGEMENT_ADDED_TO_CART_NAME).execute()
        print("Data inserted in CodeMaster table.")


if __name__ == '__main__':
    migration_drug_inventory()
