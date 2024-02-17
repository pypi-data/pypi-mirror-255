from typing import Optional

from dosepack.base_model.base_model import db
from src.model.model_group_master import GroupMaster
from src.model.model_action_master import ActionMaster
from model.model_init import init_db
from model.model_misc import CompanySetting
from src.constants import (LOCAL_DI_GROUP_ID, LOCAL_DI_GROUP_NAME, LOCAL_DI_QTY_ADDED_ACTION_ID,
                           LOCAL_DI_QTY_CONSUMED_ACTION_ID, LOCAL_DI_QTY_ADDED_FOR_SAME_FNDC_TXR_ACTION_ID,
                           LOCAL_DI_QTY_CONSUMED_FOR_SAME_FNDC_TXR_ACTION_ID, LOCAL_DI_QTY_ADDED_ACTION_NAME,
                           LOCAL_DI_QTY_CONSUMED_ACTION_NAME, LOCAL_DI_QTY_ADDED_FOR_SAME_FNDC_TXR_ACTION_NAME,
                           LOCAL_DI_QTY_CONSUMED_FOR_SAME_FNDC_TXR_ACTION_NAME, NUMBER_OF_DAYS_TO_FETCH_PO)
from src.model.model_local_di_data import LocalDIData
from src.model.model_local_di_po_data import LocalDIPOData
from src.model.model_local_di_transaction import LocalDITransaction


def migration_local_di_management(company_id: Optional[int] = None, user_id: Optional[int] = None):
    init_db(db, 'database_migration')
    print("Migration started for the Local Inventory Management")
    create_tables()
    insert_data()
    populate_company_setting(company_id=company_id if company_id else 3, user_id=user_id if user_id else 2)
    print("migration_local_di_management completed successfully")


def create_tables():
    db.create_tables([LocalDIData, LocalDITransaction, LocalDIPOData], safe=True)
    print("Tables Created: LocalDIData, LocalDITransaction, LocalDIPOData")


def insert_data():
    if GroupMaster.table_exists():
        GroupMaster.insert(id=LOCAL_DI_GROUP_ID,
                           name=LOCAL_DI_GROUP_NAME).execute()
        print("Data inserted in GroupMaster table.")

    if ActionMaster.table_exists():
        ActionMaster.insert(id=LOCAL_DI_QTY_ADDED_ACTION_ID, group_id=LOCAL_DI_GROUP_ID,
                            value=LOCAL_DI_QTY_ADDED_ACTION_NAME).execute()
        ActionMaster.insert(id=LOCAL_DI_QTY_CONSUMED_ACTION_ID, group_id=LOCAL_DI_GROUP_ID,
                            value=LOCAL_DI_QTY_CONSUMED_ACTION_NAME).execute()
        ActionMaster.insert(id=LOCAL_DI_QTY_ADDED_FOR_SAME_FNDC_TXR_ACTION_ID, group_id=LOCAL_DI_GROUP_ID,
                            value=LOCAL_DI_QTY_ADDED_FOR_SAME_FNDC_TXR_ACTION_NAME).execute()
        ActionMaster.insert(id=LOCAL_DI_QTY_CONSUMED_FOR_SAME_FNDC_TXR_ACTION_ID, group_id=LOCAL_DI_GROUP_ID,
                            value=LOCAL_DI_QTY_CONSUMED_FOR_SAME_FNDC_TXR_ACTION_NAME).execute()
        print("Data inserted in ActionMaster table.")


def populate_company_setting(company_id, user_id):
    try:
        row_data = [
            {"company_id": company_id, "name": NUMBER_OF_DAYS_TO_FETCH_PO, "value": 5, "created_by": user_id,
             "modified_by": user_id}
        ]
        CompanySetting.insert_many(row_data).execute()
        print("Data Inserted in CompanySetting table.")

    except Exception as e:
        print(e)


if __name__ == '__main__':
    migration_local_di_management()
