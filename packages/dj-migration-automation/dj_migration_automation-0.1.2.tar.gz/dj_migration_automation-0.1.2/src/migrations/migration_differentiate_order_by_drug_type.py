import os
import sys
from typing import Optional, List, Dict, Any

from peewee import fn, CharField
from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from src.model.model_canister_master import CanisterMaster
from src.model.model_company_setting import CompanySetting
from src.model.model_drug_master import DrugMaster
from model.model_init import init_db
from src.constants import LOCAL_DI_QTY_ADDED_ACTION_ID, BUFFER_FOR_FAST_MOVING, BUFFER_FOR_MEDIUM_FAST_MOVING, \
    BUFFER_FOR_MEDIUM_SLOW_MOVING, BUFFER_FOR_SLOW_MOVING
from src.model.model_adhoc_drug_request import AdhocDrugRequest
from src.model.model_batch_drug_data import BatchDrugData
from src.model.model_current_inventory_mapping import CurrentInventoryMapping
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_local_di_data import LocalDIData
from src.model.model_local_di_po_data import LocalDIPOData
from src.model.model_local_di_transaction import LocalDITransaction
from utils.drug_inventory_webservices import get_current_inventory_data


def migration_differentiate_order_by_drug_type(company_id: Optional[int] = None, user_id: Optional[int] = None):
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    print("Starting migration_differentiate_order_by_drug_type")
    # update_tables(migrator)
    reset_local_inventory(company_id=company_id if company_id else 3)
    # populate_company_setting(company_id=company_id if company_id else 3, user_id=user_id if user_id else 2)
    print("migration_differentiate_order_by_drug_type completed successfully.")


def update_tables(migrator):
    try:
        if CurrentInventoryMapping.table_exists():
            db.execute_sql("ALTER TABLE current_inventory_mapping ADD COLUMN is_local bool AFTER reserve_qty")
            print("Column added: CurrentInventoryMapping.is_local")
            db.execute_sql("UPDATE current_inventory_mapping SET is_local = 0")
            print("Values added to the column is_local column of the table current_inventory_mapping.")
            migrate(migrator.add_not_null("current_inventory_mapping", "is_local"))
            print("Not null constraint added to the is_local column of the table current_inventory_mapping.")

        if BatchDrugData.table_exists():
            db.execute_sql("ALTER TABLE batch_drug_data ADD COLUMN department VARCHAR(20) AFTER order_qty")
            print("Column added: batch_drug_data.department")
            db.execute_sql("UPDATE batch_drug_data SET department = 'dosepack'")
            print("Values added to the column department column of the table batch_drug_data.")
            migrate(migrator.add_not_null("batch_drug_data", "department"))
            print("Not null constraint added to the department column of the table batch_drug_data.")

        if AdhocDrugRequest.table_exists():
            db.execute_sql("ALTER TABLE adhoc_drug_request ADD COLUMN department VARCHAR(20) AFTER order_qty")
            print("Column added: adhoc_drug_request.department")
            db.execute_sql("UPDATE adhoc_drug_request SET department = 'dosepack'")
            print("Values added to the column department column of the table adhoc_drug_request.")
            migrate(migrator.add_not_null("adhoc_drug_request", "department"))
            print("Not null constraint added to the department column of the table adhoc_drug_request.")

        if FacilityDistributionMaster.table_exists():
            migrate(migrator.add_column("facility_distribution_master", "req_dept_list",
                                        CharField(null=True, default=None)),
                    migrator.add_column("facility_distribution_master", "ack_dept_list",
                                        CharField(null=True, default=None)))
            print("Column added: facility_distribution_master.ack_dept_list, "
                  "facility_distribution_master.ack_dept_list")

    except Exception as e:
        print(e)


def reset_local_inventory(company_id: int):
    print("Resetting Local Inventory")
    local_di_data: List[Dict[str, Any]] = list()
    local_di_txn_data: List[Dict[str, Any]] = list()
    try:
        query = CanisterMaster.select(CanisterMaster.drug_id,
                                      DrugMaster.ndc,
                                      DrugMaster.formatted_ndc,
                                      DrugMaster.txr,
                                      DrugMaster.brand_flag,
                                      fn.SUM(CanisterMaster.available_quantity).alias("quantity"),
                                      fn.COUNT(CanisterMaster.id).alias("count")).dicts() \
            .join(DrugMaster, on=CanisterMaster.drug_id == DrugMaster.id) \
            .where(CanisterMaster.company_id == company_id,
                   DrugMaster.txr.is_null(False)) \
            .group_by(CanisterMaster.drug_id) \
            .having(fn.SUM(CanisterMaster.available_quantity) >= 0) \
            .order_by(DrugMaster.ndc)

        for data in query:
            quantity = 0
            txr_list = [int(data["txr"])]
            # get on hand inventory data from elite and create dict having key value be pair of ndc and inventory data
            total_inventory_by_ndc: Dict[str, Dict[str, Any]] = {data["ndc"]: data for data in
                                                                 get_current_inventory_data(
                                                                     txr_list=txr_list, qty_greater_than_zero=True)}

            print("total_inventory_by_ndc {}".format(total_inventory_by_ndc))

            if data["ndc"] in total_inventory_by_ndc and "quantity" in total_inventory_by_ndc[data["ndc"]]:
                quantity = total_inventory_by_ndc[data["ndc"]]["quantity"]

            temp_dict: Dict[str, Any] = {"ndc": data["ndc"],
                                         "formatted_ndc": data["formatted_ndc"],
                                         "txr": data["txr"],
                                         "brand_flag": data["brand_flag"],
                                         "quantity": quantity}

            local_di_data.append(temp_dict.copy())
            temp_dict.pop("brand_flag")
            temp_dict["action_id"] = LOCAL_DI_QTY_ADDED_ACTION_ID
            temp_dict["comment"] = "Initialized based on the canister available quantity."
            local_di_txn_data.append(temp_dict.copy())

        print("local_di_data {}".format(local_di_data))
        print("local_di_txn_data {}".format(local_di_txn_data))

        if LocalDIPOData.table_exists():
            LocalDIPOData.update(po_ack_data="History").where(LocalDIPOData.id.is_null(False)).execute()
        if LocalDIData.table_exists():
            db.truncate_table(LocalDIData)
            LocalDIData.insert_data(data_list=local_di_data)
        if LocalDITransaction.table_exists():
            db.truncate_table(LocalDITransaction)
            LocalDITransaction.insert_data(data_list=local_di_txn_data)
        print("Local Inventory Reset Done")

    except Exception as e:
        print("Error in reset_local_inventory {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in executing reset_local_inventory: exc_type - {exc_type}, fname - {fname}, line - {exc_tb.tb_lineno}")


def populate_company_setting(company_id, user_id):
    try:
        row_data = [{"company_id": company_id, "name": BUFFER_FOR_FAST_MOVING, "value": 1.5,
                     "created_by": user_id, "modified_by": user_id},
                    {"company_id": company_id, "name": BUFFER_FOR_MEDIUM_FAST_MOVING, "value": 1.2,
                     "created_by": user_id, "modified_by": user_id},
                    {"company_id": company_id, "name": BUFFER_FOR_MEDIUM_SLOW_MOVING, "value": 1,
                     "created_by": user_id, "modified_by": user_id},
                    {"company_id": company_id, "name": BUFFER_FOR_SLOW_MOVING, "value": 1,
                     "created_by": user_id, "modified_by": user_id}]
        CompanySetting.insert_many(row_data).execute()
        print("Data Inserted in CompanySetting table.")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    migration_differentiate_order_by_drug_type()
