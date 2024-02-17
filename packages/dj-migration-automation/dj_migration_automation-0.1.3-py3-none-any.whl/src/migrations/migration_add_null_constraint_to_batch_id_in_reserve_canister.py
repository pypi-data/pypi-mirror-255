from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_unique_drug import UniqueDrug
from model.model_init import init_db

from src.model.model_reserved_canister import ReservedCanister


def add_null_constraint_in_batch_id_column_in_ReservedCanister():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        if ReservedCanister.table_exists():
            # add not null constraint
            migrate(migrator.drop_not_null(ReservedCanister._meta.db_table,
                                          ReservedCanister.batch_id.db_column))
            print("Add null constraint for batch_id column in ReservedCanister")


    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    add_null_constraint_in_batch_id_column_in_ReservedCanister()
