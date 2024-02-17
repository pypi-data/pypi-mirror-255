from playhouse.migrate import MySQLMigrator, migrate

import settings
from dosepack.base_model.base_model import BaseModel, db
from model.model_init import init_db
from src import constants
from src.migrations.migration_add_columns_in_drug_tracker import DrugTracker
from src.model.model_code_master import CodeMaster
from src.model.model_company_setting import CompanySetting
from src.model.model_drug_master import DrugMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader

init_db(db, 'database_migration')


def migration_add_packaging_types_in_code_master():

    try:
        code_master_data = [
            dict(id=constants.PACKAGING_TYPE_VIAL, group_id=constants.PACKAGING_TYPE_GROUP_ID,
                 value="Vial"),
            dict(id=constants.PACKAGING_TYPE_BUBBLE_PACK, group_id=constants.PACKAGING_TYPE_GROUP_ID,
                 value="Bubble Pack"),
            dict(id=constants.PACKAGING_TYPE_OTHER, group_id=constants.PACKAGING_TYPE_GROUP_ID,
                 value="Other Rx"),
            dict(id=constants.PRN_DONE_STATUS, group_id=settings.GROUP_MASTER_PACK,
                 value="PRN Done"),
        ]
        CodeMaster.insert_many(code_master_data).execute()

    except Exception as e:
        print(e)
        raise


def migration_add_nullables_in_slot_header():
    migrator = MySQLMigrator(db)
    try:
        if SlotHeader.table_exists():
            # add not null constraint
            migrate(migrator.drop_not_null(SlotHeader._meta.db_table,
                                           SlotHeader.hoa_date.db_column))

            migrate(migrator.drop_not_null(SlotHeader._meta.db_table,
                                           SlotHeader.hoa_time.db_column))

            migrate(migrator.drop_not_null(SlotHeader._meta.db_table,
                                           SlotHeader.pack_grid_id.db_column))

            migrate(migrator.drop_not_null(DrugMaster._meta.db_table,
                                           DrugMaster.ndc.db_column))

            print("Addeed null constraint for hoa_date, hoa_column and pack_grid_id column in SlotHeader , "
                  "ndc in drug_master")
    except Exception as e:
        raise e


def migration_add_column_last_billed_date_in_patient_rx():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(PatientRx._meta.db_table,
                                PatientRx.initial_fill_qty.db_column,
                                PatientRx.initial_fill_qty)
        )
        migrate(
            migrator.add_column(PatientRx._meta.db_table,
                                PatientRx.last_billed_date.db_column,
                                PatientRx.last_billed_date)
        )
        migrate(
            migrator.add_column(PatientRx._meta.db_table,
                                PatientRx.packaging_type.db_column,
                                PatientRx.packaging_type)
        )
        migrate(
            migrator.add_column(PatientRx._meta.db_table,
                                PatientRx.to_fill_qty.db_column,
                                PatientRx.to_fill_qty)
        )
        print("initial_fill_qty, last_billed_date, packaging_type, to_fill_qty column added in PatientRx")
    except Exception as e:
        print(e)


def migration_add_column_pharmacy_drug_id_in_drug_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(DrugMaster._meta.db_table,
                                DrugMaster.pharmacy_drug_id.db_column,
                                DrugMaster.pharmacy_drug_id)
        )
        print("pharmacy_drug_id column added in DrugMaster")
    except Exception as e:
        print(e)


def migration_add_base_url_ips_web():

    try:

        init_db(db, 'database_migration')
        row_data = [
            {
                "company_id": 3,
                "name": "BASE_URL_IPS_WEB",
                "value": "http://172.16.4.60:443",
                "created_by": 2,
                "modified_by": 2
            }
            ]
        if CompanySetting.table_exists():
            CompanySetting.insert_many(row_data).execute()
            print("Added IPS web base url")
    except Exception as e:
        print(e)
        raise e


def migration_update_slot_details_quantity_column_max_length_threshold():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if SlotDetails.table_exists():
            sql = 'ALTER TABLE `slot_details` MODIFY `quantity` DECIMAL(7,2) NOT NULL;'
            db.execute_sql(sql)
            print("Max digit of quantity column in slot_details is updated to 7")
        if DrugTracker.table_exists():
            sql = 'ALTER TABLE `drug_tracker` MODIFY `drug_quantity` DECIMAL(6,2) NOT NULL DEFAULT 0.00;'
            db.execute_sql(sql)
            print("Max digit of quantity column in drug_tracker is updated to 6")
    except Exception as e:
        settings.logger.error("Error while updating column in slot_details and drug_tracker: ", str(e))


def migration_for_prn_other_rx():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migration_update_slot_details_quantity_column_max_length_threshold()
        migration_add_packaging_types_in_code_master()
        migration_add_nullables_in_slot_header()
        migration_add_column_last_billed_date_in_patient_rx()
        migration_add_base_url_ips_web()
        migration_add_column_pharmacy_drug_id_in_drug_master()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    migration_for_prn_other_rx()
