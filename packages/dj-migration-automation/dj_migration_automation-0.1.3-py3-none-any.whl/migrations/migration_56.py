from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class PackDetails(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class PackUserMap(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    assigned_to = IntegerField()  # Pack is assigned to the user for filling manually
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_id', 'assigned_to'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_user_map"


def migrate_56():
    init_db(db, "database_migration")
    migrator= MySQLMigrator(db)
    migrate(
        migrator.drop_not_null(
            PackUserMap._meta.db_table,
            PackUserMap.assigned_to.db_column
        )
    )
    print('Table(s) Updated: PackUserMap')


if __name__ == '__main__':
    migrate_56()
