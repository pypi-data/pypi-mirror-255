import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_ext_pack_details import ExtPackDetails


def add_packs_delivery_status_column_in_ext_pack_details():

    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            if ExtPackDetails.table_exists():
                migrate(migrator.add_column(ExtPackDetails._meta.db_table,
                                            ExtPackDetails.packs_delivery_status.db_column,
                                            ExtPackDetails.packs_delivery_status
                                            )
                        )

                print("Added packs_delivery_status column in ext_pack_details")

    except Exception as e:
        settings.logger.error("Error while adding packs_delivery_status column in ext_pack_details: ", str(e))


if __name__ == "__main__":
    add_packs_delivery_status_column_in_ext_pack_details()
