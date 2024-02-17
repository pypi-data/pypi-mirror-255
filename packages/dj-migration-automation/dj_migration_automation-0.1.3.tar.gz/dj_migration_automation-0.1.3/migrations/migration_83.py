from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class FileHeader(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    # status = ForeignKeyField(CodeMaster)
    filename = CharField(max_length=150)
    filepath = CharField(null=True, max_length=200)
    manual_upload = BooleanField(null=True) # added - Amisha
    message = CharField(null=True, max_length=500)
    task_id = CharField(max_length=155, null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    # created_date = DateField(default=get_current_date)
    # created_time = TimeField(default=get_current_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_header"

def migrate_83():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if FileHeader.table_exists():
        migrate(
            migrator.add_column(
                FileHeader._meta.db_table,
                FileHeader.task_id.db_column,
                FileHeader.task_id
            )
        )

    print("Table Modified: FileHeader")


if __name__ == "__main__":
    migrate_83()
