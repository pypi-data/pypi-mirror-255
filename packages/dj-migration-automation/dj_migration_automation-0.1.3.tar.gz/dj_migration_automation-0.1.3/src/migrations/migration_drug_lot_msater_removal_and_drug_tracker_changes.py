from playhouse.migrate import MySQLMigrator, migrate
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_drug_tracker import DrugTracker

init_db(db, 'database_migration')


def migration_add_column_expiry_date_and_lot_number_in_drug_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(DrugTracker._meta.db_table,
                                DrugTracker.expiry_date.db_column,
                                DrugTracker.expiry_date)
        )
        migrate(
            migrator.add_column(DrugTracker._meta.db_table,
                                DrugTracker.lot_number.db_column,
                                DrugTracker.lot_number)
        )
        print("expiry_date and lot_number columns added in drug_tracker")
    except Exception as e:
        print(e)


def transfer_columns_data_from_drug_lot_master_to_drug_tracker():
    try:
        query1 = DrugLotMaster.select(DrugLotMaster.lot_number, DrugLotMaster.expiry_date, DrugLotMaster.id).dicts() \
            .join(DrugTracker, on=(DrugTracker.drug_lot_master_id == DrugLotMaster.id)) \
            .group_by(DrugLotMaster.id)
        total_count = query1.count()
        count = 0
        for record in query1:
            count += 1
            print(f"record added {count}/{total_count}")
            status = DrugTracker.update(lot_number=record['lot_number'], expiry_date=record["expiry_date"]).where(
                DrugTracker.drug_lot_master_id == record["id"]).execute()
        query2 = DrugLotMaster.select(DrugLotMaster.expiry_date, DrugLotMaster.case_id, DrugLotMaster.lot_number).dicts() \
            .join(DrugTracker, on=(DrugTracker.case_id == DrugLotMaster.case_id)) \
            .group_by(DrugLotMaster.case_id)
        total_count = query2.count()
        count = 0
        for record in query2:
            count += 1
            print(f"record added {count}/{total_count}")
            status = DrugTracker.update(lot_number=record['lot_number'], expiry_date=record["expiry_date"]).where(
                DrugTracker.case_id == record["case_id"]).execute()
        print(f"expiry_date and lot_number updated in drug_tracker from drug_lot_master for {query2.count()}")
    except Exception as e:
        print(e)


def migration_drug_lot_master_removal_changes():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migration_add_column_expiry_date_and_lot_number_in_drug_tracker()
        transfer_columns_data_from_drug_lot_master_to_drug_tracker()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    migration_drug_lot_master_removal_changes()
