from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from playhouse.migrate import *
import settings


class PackFillError(BaseModel):
    id = PrimaryKeyField()
    # pack_rx_id = ForeignKeyField(PackRxLink)
    note = CharField(null=True, max_length=1000)  # note provided by user for any filling error
    pill_misplaced = BooleanField(default=False)
    created_by = IntegerField()
    modified_by = IntegerField()
    # created_date = DateTimeField(default=get_current_date_time)
    # modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_fill_error"


class SlotFillError(BaseModel):
    id = PrimaryKeyField()
    pack_fill_error_id = ForeignKeyField(PackFillError)
    slot_row = SmallIntegerField()
    slot_column = SmallIntegerField()
    broken = BooleanField()  # flag to indicate broken pills
    error_quantity = DecimalField(decimal_places=2, max_digits=4)
    # `error_quantity` is relative to dropped quantity

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error"


def migrate_24():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    db.create_tables([SlotFillError], safe=True)
    print('Tables Created: SlotFillError')
    if PackFillError.table_exists():
        migrate(migrator.add_column(PackFillError._meta.db_table,
                                    PackFillError.pill_misplaced.db_column,
                                    PackFillError.pill_misplaced))
        print('Table Modified: PackFillError')


def rollback_24():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)
    if PackFillError.table_exists():
        migrate(
            migrator.drop_column(PackFillError._meta.db_table,
                                 PackFillError.pill_misplaced.db_column)
        )