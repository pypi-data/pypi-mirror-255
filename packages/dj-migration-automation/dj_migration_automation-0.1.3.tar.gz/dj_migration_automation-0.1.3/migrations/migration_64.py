from playhouse.migrate import *
from dosepack.base_model.base_model import db
from model.model_init import init_db
from model.model_pill_vision import PVSSlotDetails


def migrate_64():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    print("Migration start : Adding 3 columns in pvs_slot_details: pill_centre_x, pill_centre_y and radius.")

    try:
        with db.transaction():
            migrate(
                migrator.add_column(PVSSlotDetails._meta.db_table,
                                    PVSSlotDetails.pill_centre_x.db_column,
                                    PVSSlotDetails.pill_centre_x),
                migrator.add_column(PVSSlotDetails._meta.db_table,
                                    PVSSlotDetails.pill_centre_y.db_column,
                                    PVSSlotDetails.pill_centre_y),
                migrator.add_column(PVSSlotDetails._meta.db_table,
                                    PVSSlotDetails.radius.db_column,
                                    PVSSlotDetails.radius)
            )
    except Exception as e:
        print ("error", e)

if __name__ == "__main__":
    migrate_64()
    print("Migration complete.")
