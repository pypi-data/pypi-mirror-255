from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


class FileHeader(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_header"


class FileValidationError(BaseModel):
    id = PrimaryKeyField()
    file_id = ForeignKeyField(FileHeader)
    patient_name = CharField(max_length=100)
    patient_no = CharField(max_length=50)
    column = CharField(max_length=50)
    value = CharField(max_length=400)
    message = CharField(max_length=700)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_validation_error"

            indexes = (
                (('file_id', 'patient_no', 'column', 'value', 'message'), True),
            )


def migrate_34():
    init_db(db, 'database_migration')

    db.create_tables([FileValidationError], safe=True)
    print('table created: FileValidationError')
