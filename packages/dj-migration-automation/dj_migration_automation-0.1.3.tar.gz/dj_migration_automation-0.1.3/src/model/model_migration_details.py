from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class MigrationDetails(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    status = BooleanField(default=False)
    modified_date = DateTimeField(null=True, default=get_current_date_time())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "migration_details"
