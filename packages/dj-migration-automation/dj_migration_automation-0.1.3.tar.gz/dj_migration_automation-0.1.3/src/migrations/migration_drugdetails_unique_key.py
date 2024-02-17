from peewee import InternalError, IntegrityError
from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from src.model.model_drug_details import DrugDetails
from model.model_init import init_db


def update_company_id():
    try:
        DrugDetails.update(company_id=3).where(DrugDetails.company_id.is_null(True)).execute()
        return True
    except (InternalError, IntegrityError, Exception) as e:
        print("Error in updating Company ID to default value of 3. Error details: {}".format(e))
        return False


def update_index(migrator):
    migrate(
        migrator.add_index(DrugDetails._meta.db_table,
                           (DrugDetails.unique_drug_id.db_column, DrugDetails.company_id.db_column),
                           unique=True),

        migrator.drop_index(DrugDetails._meta.db_table, 'drug_details_unique_drug_id_id')
    )
    print("Unique Index modified for DrugDetails table.")


def migrate_update_unique_key():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    print("Migration started to update Unique Key for DrugDetails Table.")

    print("Update Company ID to default value of 3 if found Null.")
    status = update_company_id()

    if not status:
        print("Migration Failed.")
        return False

    # Modify the Unique key to consider Unique Drug ID and Company ID both
    update_index(migrator)

    print("Migration completed.")


if __name__ == "__main__":
    migrate_update_unique_key()
