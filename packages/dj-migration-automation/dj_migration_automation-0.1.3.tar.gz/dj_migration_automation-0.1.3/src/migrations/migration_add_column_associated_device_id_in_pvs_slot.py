from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_pvs_slot import PVSSlot


def add_associated_device_id_column_in_pvs_slot():

    try:

        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        with db.transaction():

            if PVSSlot.table_exists():
                # add column:
                migrate(migrator.add_column(PVSSlot._meta.db_table,
                                            PVSSlot.associated_device_id.db_column,
                                            PVSSlot.associated_device_id))
                print("Add 'associated_device_id' in PVSSlot")

            PVSSlot.update(associated_device_id = 12) \
                                    .where(PVSSlot.device_id == 2) \
                                    .execute()
            print("status updated for device id 2")

            PVSSlot.update(associated_device_id=11) \
                .where(PVSSlot.device_id == 3) \
                .execute()
            print("status updated for device id 3")

    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    add_associated_device_id_column_in_pvs_slot()
