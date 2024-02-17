from playhouse.migrate import MySQLMigrator
from dosepack.base_model.base_model import db
from model.model_init import init_db


def migration_added_index_in_pack_queue():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        query = "ALTER TABLE pack_queue ADD UNIQUE pack_queue_pack_id_id_idx (pack_id_id);"
        db.execute_sql(query)
        print("Migration completed.")
    except Exception as e:
        print("Error in migration_added_index_in_pack_queue.")
        print(e)


if __name__ == "__main__":
    migration_added_index_in_pack_queue()
