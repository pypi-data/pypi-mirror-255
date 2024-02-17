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


class PackRxLink(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_rx_link"


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


class PartiallyFilledPack(BaseModel):
    id = PrimaryKeyField()
    pack_rx_id = ForeignKeyField(PackRxLink)
    missing_qty = IntegerField()
    note = CharField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)


    class Meta:
        indexes = (
            (('pack_rx_id', 'missing_qty'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "partially_filled_pack"

def migrate_51():
    init_db(db, "database_migration")
    db.create_tables([PackUserMap, PartiallyFilledPack], safe=True)
    print('Table(s) Created: PackUserMap, PartiallyFilledPack')


if __name__ == '__main__':
    migrate_51()
