from playhouse.migrate import MySQLMigrator, migrate
from dosepack.base_model.base_model import BaseModel, db
from model.model_init import init_db
from src.model.model_pack_details import PackDetails

init_db(db, 'database_migration')


def migration_for_adding_bill_id_column_in_pack_details():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.bill_id.db_column,
                                PackDetails.bill_id)
        )
        print("bill_id column added in PackDetails")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    migration_for_adding_bill_id_column_in_pack_details()
