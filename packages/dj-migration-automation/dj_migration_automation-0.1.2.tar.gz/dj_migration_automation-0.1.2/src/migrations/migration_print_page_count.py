from playhouse.migrate import *
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel


class PrintQueue(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    pack_display_id = IntegerField()
    # patient_id = ForeignKeyField(PatientMaster)
    printing_status = SmallIntegerField()
    filename = CharField(null=True, max_length=30)
    printer_code = CharField(max_length=55)
    file_generated = SmallIntegerField(default=0)
    created_by = IntegerField()
    # created_date = DateField(default=get_current_date)
    # created_time = TimeField(default=get_current_time)
    associated_print = ForeignKeyField('self', null=True)
    page_count = SmallIntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "print_queue"


def update_print_data():
    update_count_id = list()
    delete_print_id = list()
    try:
        multiple_print_query = PrintQueue.select(PrintQueue.id,
                                                 PrintQueue.associated_print) \
            .where(PrintQueue.associated_print.is_null(False),
                   PrintQueue.id != PrintQueue.associated_print)\
            .order_by(PrintQueue.id)
        for record in multiple_print_query.dicts():
            update_count_id.append(record['associated_print'])
            delete_print_id.append(record['id'])

        if update_count_id:
            print('updating count to 2 for {}'.format(update_count_id))
            update_status = PrintQueue.update(page_count=2).where(PrintQueue.id << update_count_id).execute()
            print('update status {}'.format(update_status))
        if delete_print_id:
            print('deleting extra req  ids: {}'.format(delete_print_id))
            delete_status = PrintQueue.delete().where(PrintQueue.id << delete_print_id).execute()
            print('delete status {}'.format(delete_status))

    except (InternalError, IntegrityError) as e:
        print(e)
        raise


def migrate_label_page_count():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)

    migrate(
        migrator.add_column(
            PrintQueue._meta.db_table,
            PrintQueue.page_count.db_column,
            PrintQueue.page_count
        )
    )
    print("column added: PrintQueue")

    update_print_data()
    print("Data updated: PrintQueue")

    migrate(
        migrator.drop_column(
            PrintQueue._meta.db_table,
            PrintQueue.associated_print.db_column
        )
    )
    print("column dropped: associated_print")


if __name__ == '__main__':
    migrate_label_page_count()
