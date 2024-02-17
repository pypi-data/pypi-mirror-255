from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class CanisterParameters(BaseModel):
    """
    It contain the data related to canister parameters and timers to run the canister motors..
    """
    id = PrimaryKeyField()
    speed = IntegerField(null=True)  # drum rotate speed
    wait_timeout = IntegerField(null=True)  # sensor wait timeout  # in ms
    cw_timeout = IntegerField(null=True)  # clockwise # in ms
    ccw_timeout = IntegerField(null=True)  # counter clockwise # in ms
    drop_timeout = IntegerField(null=True)  # total pill drop timeout # # in ms
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)
    pill_wait_time = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_parameters'


def migrate_80():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    migrate(
        migrator.add_column(
            CanisterParameters._meta.db_table,
            CanisterParameters.pill_wait_time.db_column,
            CanisterParameters.pill_wait_time
        ))
    print("Table Modified: Canister Parameters, 'pill_wait_time' column added.")


if __name__ == "__main__":
    migrate_80()
