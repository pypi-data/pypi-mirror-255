from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_pack_queue import PackQueue


def migration_create_packqueue_table():
    init_db(db, 'database_migration')
    try:
        with db.transaction():

            if not PackQueue.table_exists():
                db.create_tables([PackQueue], safe=True)
                print('Table(s) created: PackQueue')
    except Exception as e:
        print(e)


if __name__ == "__main__":
    migration_create_packqueue_table()
