from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_pack_details import PackDetails
from src.model.model_code_master import CodeMaster


def add_column_previous_batch_id_in_pack_details():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        with db.transaction():
            #add column previous_batch_id in pack_details column
            if PackDetails.table_exists():
                migrate(migrator.add_column(PackDetails._meta.db_table,
                                            PackDetails.previous_batch_id.db_column,
                                            PackDetails.previous_batch_id))

            print("inserted previous_batch_id in pack_details")

            # Add new row in code_master
            query = CodeMaster.insert(id=245, group_id=7, value='Batch Merged')
            query.execute()
            print("Inserted new record in code_master")

    except Exception as e:
        print(e)
        raise e

if __name__ == "__main__":
    add_column_previous_batch_id_in_pack_details()