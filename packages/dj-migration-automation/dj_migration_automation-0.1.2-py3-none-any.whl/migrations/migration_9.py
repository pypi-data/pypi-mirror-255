from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class PackDetails(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class SkipUSPack(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "skip_us_pack"


class NewFillDrug(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    formatted_ndc = CharField(max_length=12, null=True)
    txr = CharField(max_length=8, null=True)
    new = BooleanField(default=True)
    packs_filled = SmallIntegerField(default=0)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "new_fill_drug"


def migrate_9():
    init_db(db, 'database_migration')
    db.create_tables([SkipUSPack, NewFillDrug], safe=True)
    print('Table(s) created: SkipUSPack, NewFillDrug')
