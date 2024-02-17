from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.dao.ext_file_dao import update_couch_db_pending_template_count
from src.model.model_template_master import TemplateMaster


def migration_add_column_template_autoprocess(company_ids=None):
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            TemplateMaster._meta.db_table,
            TemplateMaster.with_autoprocess.db_column,
            TemplateMaster.with_autoprocess
        )
    )
    print("with_autoprocess column added in template_master table")

    if not company_ids:
        company_ids = [3]

    for company_id in company_ids:
        update_couch_db_pending_template_count(company_id=company_id)
        print("CouchDB updated with Pending/In Progress template count for company: {}".format(company_id))


if __name__ == "__main__":
    migration_add_column_template_autoprocess()
