import logging

from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_drug_dimention_history import DrugDimensionHistory
from src.model.model_group_master import GroupMaster
from src.model.model_remote_tech_slot import RemoteTechSlot
from src.model.model_unique_drug import UniqueDrug

logger = logging.getLogger("root")

init_db(db, 'database_migration')
migrator = MySQLMigrator(db)


def add_coating_type_and_is_zip_lock_drug_column_in_unique_drug():

    try:
        if UniqueDrug.table_exists():
            migrate(
                migrator.add_column(UniqueDrug._meta.db_table,
                                    UniqueDrug.coating_type.db_column,
                                    UniqueDrug.coating_type)
            )
            print("Added coating_type column in UniqueDrug")

            migrate(
                migrator.add_column(UniqueDrug._meta.db_table,
                                    UniqueDrug.is_zip_lock_drug.db_column,
                                    UniqueDrug.is_zip_lock_drug)
            )
            print("Added is_zip_lock_drug column in UniqueDrug")


    except Exception as e:
        settings.logger.error("Error while adding coating_type and is_zip_lock_drug columns in UniqueDrug: ", str(e))


def add_column_verification_status_id_in_drug_dimension_history_table():
    try:
        query = 'alter table drug_dimension_history add column verification_status_id_id int not null default {},' \
                 'add foreign key (verification_status_id_id) references code_master(id);'.format(settings.VERIFICATION_PENDING_FOR_DRUG)
        db.execute_sql(query)

    except Exception as e:
        logger.error("Error while adding verification_status_id columns in DrugDimensionHistory: ", str(e))


def add_column_coating_type_in_unique_drug():
    add_coating_type_and_is_zip_lock_drug_column_in_unique_drug()
    add_column_verification_status_id_in_drug_dimension_history_table()


if __name__ == '__main__':
    add_column_coating_type_in_unique_drug()