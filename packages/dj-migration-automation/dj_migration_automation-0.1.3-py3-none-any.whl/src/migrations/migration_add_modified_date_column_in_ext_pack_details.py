import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_ext_pack_details import ExtPackDetails


def add_modified_date_in_ext_pack_details():

    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            if ExtPackDetails.table_exists():

                migrate(migrator.add_column(ExtPackDetails._meta.db_table,
                                            ExtPackDetails.ext_modified_date.db_column,
                                            ExtPackDetails.ext_modified_date
                                            )
                        )

                print("Added ext_modified_date column in ext_pack_details")

                db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
                db.execute_sql("SET SQL_SAFE_UPDATES=0")

                sql = "update ext_pack_details set ext_modified_date = ext_created_date;"
                db.execute_sql(sql)

                print("Updated ext_modified_date column in ext_pack_details")

    except Exception as e:
        settings.logger.error("Error while add or update ext_modified_date column in ext_pack_details: ", str(e))


if __name__ == "__main__":
    add_modified_date_in_ext_pack_details()
