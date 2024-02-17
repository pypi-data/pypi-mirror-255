from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_pvs_slot import PVSSlot


def add_pack_id_in_pvs_slot_and_null_constraint_to_slot_header_id():

    try:

        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        with db.transaction():

            if PVSSlot.table_exists():
                # add not null constraint
                migrate(migrator.drop_not_null(PVSSlot._meta.db_table,
                                               PVSSlot.slot_header_id.db_column))
                print("Add null constraint for slot_header_id column in PVSSlot")

            if PVSSlot.table_exists():
                # add column:
                migrate(migrator.add_column(PVSSlot._meta.db_table,
                                            PVSSlot.pack_id.db_column,
                                            PVSSlot.pack_id))
                print("Add 'pack_id' column in PVSSlot")

            print("inserting pack id in pvs_slot")
            query = "update pvs_slot p set pack_id_id = (select slot_header.pack_id_id from pvs_slot join slot_header on slot_header.id = pvs_slot.slot_header_id_id where pvs_slot.id = p.id);"
            db.execute_sql(query)
            print("inserted pack id in pvs_slot")

    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    add_pack_id_in_pvs_slot_and_null_constraint_to_slot_header_id()
