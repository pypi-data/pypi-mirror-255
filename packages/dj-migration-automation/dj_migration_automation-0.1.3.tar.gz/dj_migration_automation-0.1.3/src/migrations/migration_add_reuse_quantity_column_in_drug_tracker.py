from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_drug_tracker import DrugTracker


def migration_add_column_reuse_quantity_reuse_pack_in_drug_tracker():
    try:
        # Add column reuse_quantity to track how much quantity of particular drug is reuse

        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        if DrugTracker.table_exists():
            migrate(migrator.add_column(DrugTracker._meta.db_table,
                                        DrugTracker.reuse_quantity.db_column,
                                        DrugTracker.reuse_quantity
                                        )
                    )

            print("In drug_tracker reuse_quantity column added")
            migrate(migrator.add_column(DrugTracker._meta.db_table,
                                        DrugTracker.reuse_pack.db_column,
                                        DrugTracker.reuse_pack
                                        )
                    )
            print("In drug_tracker reuse_pack column added")
    except Exception as e:
        print("Error in migration_add_column_reuse_quantity_column_in_drug_tracker: {}".format(e))
        raise e


if __name__ == '__main__':
    migration_add_column_reuse_quantity_reuse_pack_in_drug_tracker()
