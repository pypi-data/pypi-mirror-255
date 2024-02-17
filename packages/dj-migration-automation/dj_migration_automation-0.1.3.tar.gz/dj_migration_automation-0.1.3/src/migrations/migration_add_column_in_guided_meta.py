import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_guided_meta import GuidedMeta

def add_pack_ids_column_in_guided_meta():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(GuidedMeta._meta.db_table,
                                GuidedMeta.pack_ids.db_column,
                                GuidedMeta.pack_ids),
        )
        print("Added column pack_ids in GuidedMeta")
    except Exception as e:
        settings.logger.error("Error while adding columns in GuidedMeta: ", str(e))


if __name__ == '__main__':
    add_pack_ids_column_in_guided_meta()