from peewee import PrimaryKeyField, IntegerField, CharField, TextField, BlobField, DateTimeField
import settings
from dosepack.base_model.base_model import BaseModel


class CeleryTaskmeta(BaseModel):
    id = PrimaryKeyField()
    task_id = CharField(max_length=155, unique=True)
    status = CharField(max_length=50)
    result = BlobField()
    date_done = DateTimeField()
    traceback = TextField(null=True)
    name = CharField(max_length=155, null=True)
    args = BlobField()
    kwargs = BlobField()
    worker = CharField(max_length=155, null=True)
    retries = IntegerField()
    queue = CharField(max_length=155, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "celery_taskmeta"
