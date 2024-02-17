
from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db

from model.model_init import init_db
from src.model.model_ext_pack_details import ExtPackDetails

# packs_delivered

init_db(db, 'database_migration')
migrator = MySQLMigrator(db)


def add_pharmacy_pack_status_id_column_in_ext_pack_details():
    if ExtPackDetails.table_exists():
        migrate(
            migrator.add_column(ExtPackDetails._meta.db_table,
                                ExtPackDetails.pharmacy_pack_status_id.db_column,
                                ExtPackDetails.pharmacy_pack_status_id)
        )
        print("Added column in ExtPackDetails")


if __name__ == "__main__":
    add_pharmacy_pack_status_id_column_in_ext_pack_details()
