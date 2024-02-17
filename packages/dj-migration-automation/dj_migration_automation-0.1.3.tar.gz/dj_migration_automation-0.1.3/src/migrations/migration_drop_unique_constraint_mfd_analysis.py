from peewee import InternalError, IntegrityError
from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_mfd_analysis import MfdAnalysis


def update_index_mfd_analysis_remove_unique_key():
    migrator = MySQLMigrator(db)
    migrate(

        migrator.drop_index(MfdAnalysis._meta.db_table, 'mfd_analysis_order_no')
    )
    print("Unique Index modified for MfdAnalysis table.")

if __name__ == "__main__":
    init_db(db, "database_migration")
    update_index_mfd_analysis_remove_unique_key()
