
from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db

from model.model_init import init_db
from src.model.model_ext_pack_details import ExtPackDetails

# packs_delivered

init_db(db, 'database_migration')
migrator = MySQLMigrator(db)


def add_pack_delivered_column_in_ext_pack_details():
    if ExtPackDetails.table_exists():
        migrate(
            migrator.add_column(ExtPackDetails._meta.db_table,
                                ExtPackDetails.packs_delivered.db_column,
                                ExtPackDetails.packs_delivered)
        )
        print("Added column in ExtPackDetails")



if __name__ == "__main__":
    add_pack_delivered_column_in_ext_pack_details()
