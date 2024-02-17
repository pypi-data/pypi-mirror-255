from peewee import PrimaryKeyField, CharField, BlobField, DateTimeField, IntegerField, TextField
import settings


class CeleryTaskmeta:
    id = PrimaryKeyField()
    status = CharField(max_length=50)
    task_id = CharField(max_length=155, unique=True)
    result = BlobField(null=True)
    date_done = DateTimeField()
    traceback = TextField()
    name = CharField(max_length=155, null=True)
    args = BlobField
    kwargs = BlobField
    worker = CharField(max_length=155)
    retries = IntegerField()
    queue = CharField(155)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "celery_taskmeta"
