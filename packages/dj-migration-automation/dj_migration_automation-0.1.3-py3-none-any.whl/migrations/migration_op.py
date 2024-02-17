from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time

import settings


class OverloadedPacks(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    extra_time = DecimalField(decimal_places=2)
    user_id = IntegerField()
    date = DateField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    is_manual = BooleanField(default=0)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "overloaded_pack_timings"


def add_column():
    init_db(db, "database_t1")
    migrator = MySQLMigrator(db)
    print("Migration start : Adding 1 column to overloaded packs")

    try:
        with db.transaction():
            migrate(
                migrator.add_column(OverloadedPacks._meta.db_table,
                                    OverloadedPacks.is_manual.db_column,
                                    OverloadedPacks.is_manual)
            )
    except Exception as e:
        print("error", e)


if __name__ == "__main__":
    add_column()
    print("column is_manual added")
