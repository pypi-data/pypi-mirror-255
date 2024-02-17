from playhouse.migrate import MySQLMigrator, migrate

import settings
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_action_master import ActionMaster
from src.model.model_code_master import CodeMaster
from src.model.model_drug_tracker import DrugTracker
from src.model.model_fill_error_details import FillErrorDetails
from src.model.model_group_master import GroupMaster
from src.model.model_pack_details import PackDetails
from src.model.model_slot_details import SlotDetails

init_db(db, 'database_migration')


def migration_add_fill_error_codes_in_code_master():
    try:
        group_master_data = [
            dict(id=constants.GROUP_MASTER_RPH_VERIFICATION_STATUS, name="Verification Status")]
        GroupMaster.insert_many(group_master_data).execute()

        code_master_data = [
            dict(id=constants.RPH_VERIFICATION_STATUS_FILL_ERROR, group_id=constants.GROUP_MASTER_RPH_VERIFICATION_STATUS,
                 value="Fill Error"),
            dict(id=constants.RPH_VERIFICATION_STATUS_FIX_ERROR, group_id=constants.GROUP_MASTER_RPH_VERIFICATION_STATUS,
                 value="Fixed Error"),
        ]
        CodeMaster.insert_many(code_master_data).execute()
        print("Fixed Error and Fill Error added in code master")

    except Exception as e:
        print(e)
        raise


def migration_create_table_fill_error_details():
    init_db(db, 'database_migration')
    try:
        init_db(db, 'database_migration')
        if not FillErrorDetails.table_exists():
            db.create_tables([FillErrorDetails], safe=True)
            print('Table(s) created: FillErrorDetails')
    except Exception as e:
        print(e)


def migration_add_column_original_quantity_in_drug_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(DrugTracker._meta.db_table,
                                DrugTracker.original_quantity.db_column,
                                DrugTracker.original_quantity)
        )
        print("original_quantity column added in DrugTracker")
    except Exception as e:
        print(e)


def migration_add_store_type_in_pack_details():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.store_type.db_column,
                                PackDetails.store_type)
        )
        print("store_type column added in PackDetails")
        print("now updating store types for PRN/On Demand packs")
        query = PackDetails.select(PackDetails.id).where(PackDetails.pack_status == constants.PRN_DONE_STATUS).dicts()
        total_updation = query.count()
        for record in query:
            status = PackDetails.update(store_type=constants.STORE_TYPE_NON_CYCLIC).where(PackDetails.id == record["id"]).execute()
        print(f"cyclic_pack flag set True in {total_updation} packs")
    except Exception as e:
        print(e)


def migration_add_store_codes_in_group_and_code_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        group_master_data = [
            dict(id=constants.GROUP_MASTER_STORE_TYPE, name='StoreType')
        ]
        GroupMaster.insert_many(group_master_data).execute()
        code_master_data = [
            dict(id=constants.STORE_TYPE_CYCLIC, group_id=constants.GROUP_MASTER_STORE_TYPE,
                 value="Cyclic"),
            dict(id=constants.STORE_TYPE_NON_CYCLIC, group_id=constants.GROUP_MASTER_STORE_TYPE,
                 value="Non Cyclic"),
            dict(id=constants.STORE_TYPE_RETAIL, group_id=constants.GROUP_MASTER_STORE_TYPE,
                 value="Retail"),
        ]
        CodeMaster.insert_many(code_master_data).execute()
        print("Cyclic, Non Cyclic and Retail added in code master")

    except Exception as e:
        print(e)
        raise


def migration_add_error_reason_in_drug_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(DrugTracker._meta.db_table,
                                DrugTracker.error_reason.db_column,
                                DrugTracker.error_reason)
        )
        print("error_reason column added in DrugTracker")
    except Exception as e:
        print(e)


def migration_add_action_ids_for_fill_error():

    try:
        action_master_data = [
            dict(id=settings.FILL_ERROR_ACTION_ID, group_id=settings.GROUP_MASTER_PACK,
                 value="Pack Error Reported"),
            dict(id=settings.FIX_ERROR_ACTION_ID, group_id=settings.GROUP_MASTER_PACK,
                 value="Pack Error Resolved"),
        ]
        ActionMaster.insert_many(action_master_data).execute()
        print("Fixed Error and Fill Error actions added in action master")

    except Exception as e:
        print(e)
        raise


def migration_for_fill_error_flow():
    init_db(db, 'database_migration')
    try:
        migration_create_table_fill_error_details()
        migration_add_fill_error_codes_in_code_master()
        migration_add_column_original_quantity_in_drug_tracker()
        migration_add_store_codes_in_group_and_code_master()
        migration_add_store_type_in_pack_details()
        migration_add_error_reason_in_drug_tracker()
        migration_add_action_ids_for_fill_error()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    migration_for_fill_error_flow()
