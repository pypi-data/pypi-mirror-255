from playhouse.migrate import MySQLMigrator, migrate

import settings
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_company_setting import CompanySetting
from src.model.model_group_master import GroupMaster
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_rx import PatientRx
from src.model.model_patient_schedule import PatientSchedule
from src.model.model_pharmacy_master import PharmacyMaster
from src.model.model_template_master import TemplateMaster
from src.model.model_slot_fill_error_v2 import SlotFillErrorV2

init_db(db, 'database_migration')


def migration_add_columns_queue_no_queue_type_in_pack_details():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.queue_no.db_column,
                                PackDetails.queue_no)
        )
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.queue_type.db_column,
                                PackDetails.queue_type)
        )
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.verification_status.db_column,
                                PackDetails.verification_status)
        )
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.pack_checked_by.db_column,
                                PackDetails.pack_checked_by)
        )
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.pack_checked_time.db_column,
                                PackDetails.pack_checked_time)
        )
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.delivered_date.db_column,
                                PackDetails.delivered_date)
        )
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.delivery_status.db_column,
                                PackDetails.delivery_status)
        )
        migrate(
            migrator.add_column(PatientSchedule._meta.db_table,
                                PatientSchedule.patient_overwrite.db_column,
                                PatientSchedule.patient_overwrite)
        )

        print("queue_no, queue_type, verification_status, pack_checked_by and pack_checked_time column added in PackDetails")
    except Exception as e:
        print(e)


def migration_add_rph_verification_codes_in_code_master():
    try:
        code_master_data = [
            dict(id=constants.RPH_VERIFICATION_STATUS_NOT_CHECKED,
                 group_id=constants.GROUP_MASTER_RPH_VERIFICATION_STATUS,
                 value="Not Checked"),
            dict(id=constants.RPH_VERIFICATION_STATUS_CHECKED, group_id=constants.GROUP_MASTER_RPH_VERIFICATION_STATUS,
                 value="Checked"),
            dict(id=constants.RPH_VERIFICATION_STATUS_ON_HOLD_SYSTEM,
                 group_id=constants.GROUP_MASTER_RPH_VERIFICATION_STATUS,
                 value="System Hold"),
            dict(id=constants.RPH_VERIFICATION_STATUS_ON_HOLD_MANUAL,
                 group_id=constants.GROUP_MASTER_RPH_VERIFICATION_STATUS,
                 value="Manual Hold")
        ]
        CodeMaster.insert_many(code_master_data).execute()
        print("Not Checked, Checked, System Hold and Manual Hold added in code master")

    except Exception as e:
        print(e)
        raise


def migration_add_delivery_status_codes_in_code_master():
    try:
        group_master_data = [
            dict(id=constants.GROUP_MASTER_DELIVERY_STATUS, name="Delivery Status")]
        GroupMaster.insert_many(group_master_data).execute()

        code_master_data = [
            dict(id=constants.DELIVERY_STATUS_NOT_DELIVERED,
                 group_id=constants.GROUP_MASTER_DELIVERY_STATUS,
                 value="Not Delivered"),
            dict(id=constants.DELIVERY_STATUS_TO_BE_DELIVERED, group_id=constants.GROUP_MASTER_DELIVERY_STATUS,
                 value="To Be Delivered"),
            dict(id=constants.DELIVERY_STATUS_DELIVERED,
                 group_id=constants.GROUP_MASTER_DELIVERY_STATUS,
                 value="Delivered"),
            dict(id=constants.DELIVERY_STATUS_CANCELLED,
                 group_id=constants.GROUP_MASTER_DELIVERY_STATUS,
                 value="Cancelled")
        ]
        CodeMaster.insert_many(code_master_data).execute()
        print("Not Delivered, To Be Delivered, Delivered and Cancelled added in code master")

    except Exception as e:
        print(e)
        raise


def migration_add_ext_date_columns_in_patient_rx():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(PatientRx._meta.db_table,
                                PatientRx.prescribed_date.db_column,
                                PatientRx.prescribed_date)
        )
        migrate(
            migrator.add_column(PatientRx._meta.db_table,
                                PatientRx.last_pickup_date.db_column,
                                PatientRx.last_pickup_date)
        )
        migrate(
            migrator.add_column(PatientRx._meta.db_table,
                                PatientRx.next_pickup_date.db_column,
                                PatientRx.next_pickup_date)
        )

        print("prescribed_date, last_pickup_date, next_pickup_date columns added in PatientRx")
    except Exception as e:
        print(e)


def migration_add_code_use_retail_in_company_settings():

    try:

        init_db(db, 'database_migration')
        row_data = [
            {
                "company_id": 3,
                "name": "USE_RETAIL",
                "value": 1,
                "created_by": 2,
                "modified_by": 2
            }
            ]
        if CompanySetting.table_exists():
            CompanySetting.insert_many(row_data).execute()
            print("Added retail flag in company settings")
    except Exception as e:
        print(e)
        raise e


def migration_update_existing_code_and_add_new_code_for_packaging_type():
    try:
        updated = CodeMaster.update(value="Blister Pack (7x4) (Multi)").where(
            CodeMaster.id == constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4).execute()
        print("updated code value from Blister pack to Blister Pack (7x4) (Multi)")

        code_master_data = [
            dict(id=constants.PACKAGING_TYPE_BLISTER_PACK_UNIT_7X4,
                 group_id=constants.PACKAGING_TYPE_GROUP_ID,
                 value="Blister Pack (7x4) (Unit)"),
            dict(id=constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_8X4, group_id=constants.PACKAGING_TYPE_GROUP_ID,
                 value="Blister Pack (8x4) (Multi)"),
            dict(id=constants.PACKAGING_TYPE_BLISTER_PACK_UNIT_8X4,
                 group_id=constants.PACKAGING_TYPE_GROUP_ID,
                 value="Blister Pack (8x4) (Unit)")
        ]
        CodeMaster.insert_many(code_master_data).execute()
        print("Blister pack types packaging type added in code master")
    except Exception as e:
        print(e)
        raise e


def migration_add_column_packaging_type_in_pack_details():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.packaging_type.db_column,
                                PackDetails.packaging_type)
        )
        print("packaging_type column added in PackDetails")

        query = PatientRx.select(PackRxLink.pack_id, PatientRx.packaging_type, PackDetails.grid_type,
                                 TemplateMaster.pack_type).dicts() \
            .join(PackRxLink, on=PackRxLink.patient_rx_id == PatientRx.id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(TemplateMaster, on=(TemplateMaster.patient_id == PackHeader.patient_id) & (
                    TemplateMaster.file_id == PackHeader.file_id))
        x = query.count()
        count = 0
        for record in query:
            count += 1
            to_set_packaging_type = record["packaging_type"]
            if record["pack_type"] == constants.UNIT_DOSE_PER_PACK:
                if record["grid_type"] == constants.PACK_GRID_ROW_7x4:
                    to_set_packaging_type = constants.PACKAGING_TYPE_BLISTER_PACK_UNIT_7X4
                else:
                    to_set_packaging_type = constants.PACKAGING_TYPE_BLISTER_PACK_UNIT_8X4
            else:
                if record["grid_type"] == constants.PACK_GRID_ROW_7x4:
                    to_set_packaging_type = constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4
                else:
                    to_set_packaging_type = constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_8X4
            print(f"Progress: [{count}/{x}] {'#' * (count * 20 // x)}{' ' * ((x - count) * 20 // x)}", end='\r')
            updated = PackDetails.update(packaging_type=to_set_packaging_type).where(
                PackDetails.id == record["pack_id"]).execute()
        print(f"packaging types transferred from PatientRx to PackDetails for {x} RXs")
    except Exception as e:
        print(e)


def migration_add_columns_in_slot_fill_error():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(SlotFillErrorV2._meta.db_table,
                                SlotFillErrorV2.rph_error.db_column,
                                SlotFillErrorV2.rph_error)
        )
        migrate(
            migrator.add_column(SlotFillErrorV2._meta.db_table,
                                SlotFillErrorV2.rph_error_resolved.db_column,
                                SlotFillErrorV2.rph_error_resolved)
        )
        migrate(
            migrator.add_column(SlotFillErrorV2._meta.db_table,
                                SlotFillErrorV2.modified_by.db_column,
                                SlotFillErrorV2.modified_by)
        )
        migrate(
            migrator.add_column(SlotFillErrorV2._meta.db_table,
                                SlotFillErrorV2.modified_date.db_column,
                                SlotFillErrorV2.modified_date)
        )

        print("rph_error, rph_error_resolved, modified_by, modified_date columns added in SlotFillErrorV2")
    except Exception as e:
        print(e)


def migration_add_code_use_rts_in_company_settings():

    try:

        init_db(db, 'database_migration')
        row_data = [
            {
                "company_id": 3,
                "name": "USE_RTS_FLOW",
                "value": 1,
                "created_by": 2,
                "modified_by": 2
            }
            ]
        if CompanySetting.table_exists():
            CompanySetting.insert_many(row_data).execute()
            print("Added rts flag in company settings")
    except Exception as e:
        print(e)
        raise e


def migration_add_allowed_scan_types_in_company_settings():

    try:

        init_db(db, 'database_migration')
        row_data = [
            {
                "company_id": 3,
                "name": "ALLOWED_SCAN_TYPE",
                "value": "77, 78, 79, 256, 273, 275, 298, 299",
                "created_by": 2,
                "modified_by": 2
            }
            ]
        if CompanySetting.table_exists():
            CompanySetting.insert_many(row_data).execute()
            print("Added allowed scan type codes in company settings")
    except Exception as e:
        print(e)
        raise e


def migration_add_opening_hours_in_pharmacy_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(PharmacyMaster._meta.db_table,
                                PharmacyMaster.opening_hours.db_column,
                                PharmacyMaster.opening_hours)
        )

        print("opening_hours column added in PharmacyMaster")
    except Exception as e:
        print(e)


def migration_for_solvera():
    init_db(db, 'database_migration')
    try:
        migration_add_delivery_status_codes_in_code_master()
        migration_add_rph_verification_codes_in_code_master()
        migration_add_columns_queue_no_queue_type_in_pack_details()
        migration_add_ext_date_columns_in_patient_rx()
        migration_add_code_use_retail_in_company_settings()
        migration_update_existing_code_and_add_new_code_for_packaging_type()
        migration_add_column_packaging_type_in_pack_details()
        migration_add_columns_in_slot_fill_error()
        migration_add_code_use_rts_in_company_settings()
        migration_add_allowed_scan_types_in_company_settings()
        migration_add_opening_hours_in_pharmacy_master()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    migration_for_solvera()
