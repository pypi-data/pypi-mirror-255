from playhouse.migrate import *
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from collections import defaultdict


class PartiallyFilledPack(BaseModel):
    id = PrimaryKeyField()
    # pack_rx_id = ForeignKeyField(PackRxLink)
    missing_qty = IntegerField()
    missing_qty_fix = DecimalField(decimal_places=2, max_digits=4, default=0)
    note = CharField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    # created_date = DateTimeField(default=get_current_date_time)
    # modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_rx_id', 'missing_qty'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "partially_filled_pack"


def update_quantity_data():
    try:
        quantity_id_dict = defaultdict(list)
        query = PartiallyFilledPack.select(PartiallyFilledPack.id, PartiallyFilledPack.missing_qty).dicts()
        for record in query:
            quantity_id_dict[record['missing_qty']].append(record['id'])
        for quantity, partially_filled_rx_id in quantity_id_dict.items():
            status = PartiallyFilledPack.update(missing_qty_fix=quantity)\
                .where(PartiallyFilledPack.id << partially_filled_rx_id).execute()
            print('update count: ', status)

    except (InternalError, IntegrityError) as e:
        print(e)
        raise


def migrate_missing_qty():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)

    migrate(
        migrator.add_column(
            PartiallyFilledPack._meta.db_table,
            PartiallyFilledPack.missing_qty_fix.db_column,
            PartiallyFilledPack.missing_qty_fix
        )
    )
    print("column added: PartiallyFilledPack")

    update_quantity_data()
    print("Data updated: PartiallyFilledPack")

    migrate(
        migrator.drop_column(
            PartiallyFilledPack._meta.db_table,
            PartiallyFilledPack.missing_qty.db_column
        )
    )
    print("column dropped: missing_qty")
    migrate(
        migrator.rename_column(PartiallyFilledPack._meta.db_table,
                               PartiallyFilledPack.missing_qty_fix.db_column,
                               PartiallyFilledPack.missing_qty.db_column)
    )
    print("column renamed: missing_qty")


if __name__ == '__main__':
    migrate_missing_qty()
