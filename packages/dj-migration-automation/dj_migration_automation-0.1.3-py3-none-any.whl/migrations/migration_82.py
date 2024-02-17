from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time, get_current_date, get_current_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class PackDetails(BaseModel):
    id = PrimaryKeyField()


class PatientMaster(BaseModel):
    id = PrimaryKeyField()


class PrintQueue(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    pack_display_id = IntegerField()
    patient_id = ForeignKeyField(PatientMaster)
    printing_status = SmallIntegerField()
    filename = CharField(null=True, max_length=30)
    printer_code = CharField(max_length=55)
    file_generated = SmallIntegerField(default=0)
    created_by = IntegerField()
    created_date = DateField(default=get_current_date)
    created_time = TimeField(default=get_current_time)
    associated_print = ForeignKeyField('self', null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "print_queue"


def migrate_82():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            PrintQueue._meta.db_table,
            PrintQueue.associated_print.db_column,
            PrintQueue.associated_print
        )
    )
    print("associated_print column added in print queue")


if __name__ == "__main__":
    migrate_82()
