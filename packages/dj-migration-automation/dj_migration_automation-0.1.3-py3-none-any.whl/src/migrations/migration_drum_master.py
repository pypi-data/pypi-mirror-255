from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class CanisterDrum(BaseModel):
    id = PrimaryKeyField()
    serial_number = CharField(unique=True, max_length=10, null=False)
    width = DecimalField(decimal_places=3, max_digits=6, null=False)
    depth = DecimalField(decimal_places=3, max_digits=6, null=False)
    length = DecimalField(decimal_places=3, max_digits=6, null=False)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(null=False)
    modified_by = IntegerField(null=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drum"


def migration_drum_master():
    init_db(db, 'database_migration')
    db.create_tables([CanisterDrum], safe=True)
    print('Table(s) created: CanisterDrum')


