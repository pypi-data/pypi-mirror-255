from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
from playhouse.migrate import *
import settings


class OverloadedPacks(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField(null=True, default=None)
    extra_time = DecimalField(decimal_places=2)
    user_id = IntegerField()
    date = DateField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "overloaded_pack_timing"


def add_table():
    init_db(db, 'database_t1')

    migrator = MySQLMigrator(db)
    db.create_tables([OverloadedPacks], safe=True)
    print("Tables created: OverloadedPacks")

if __name__ == "__main__":
    add_table()
