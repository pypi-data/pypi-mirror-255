from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class PackStatusTracker(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    # status = ForeignKeyField(CodeMaster)
    # created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    reason = CharField(max_length=500, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_status_tracker"


def migrate_13():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)

    if PackStatusTracker.table_exists():
        migrate(migrator.add_column(PackStatusTracker._meta.db_table, PackStatusTracker.reason.db_column,
                                    PackStatusTracker.reason))
        print("Tables(s) Modified: PackStatusTracker")

