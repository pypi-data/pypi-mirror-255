import settings
from playhouse.migrate import *
from playhouse.shortcuts import case
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_drug_tracker import DrugTracker

def add_update_modified_date_column_in_drug_tracker():

    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            if DrugTracker.table_exists():
                migrate(migrator.add_column(DrugTracker._meta.db_table,
                                            DrugTracker.modified_date.db_column,
                                            DrugTracker.modified_date
                                            )
                        )

                print("Added modified_date column in drug_tracker")

                drug_tracker_list: list = list()
                # created_date_list: list = list()

                query = DrugTracker.select(DrugTracker.id, DrugTracker.created_date).dicts()

                for record in query:
                    drug_tracker_list.append(record["id"])
                    # date_time_str = record["created_date"].strftime("%Y-%m-%d %H:%M:%S")
                    # created_date_list.append(date_time_str)

                # new_seq_tuple = list(tuple(zip(map(str, drug_tracker_list), map(str, created_date_list))))
                # case_sequence = case(DrugTracker.id, new_seq_tuple)
                update_status = DrugTracker.update(modified_date=None)\
                    .where(DrugTracker.id.in_(drug_tracker_list)).execute()

                print("modified_date column in drug_tracker is updated")

    except Exception as e:
        settings.logger.error("Error while add or updated modified_date column in drug_tracker: ", str(e))


if __name__ == "__main__":
    add_update_modified_date_column_in_drug_tracker()
