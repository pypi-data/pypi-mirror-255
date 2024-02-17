from peewee import (IntegerField, DateTimeField, PrimaryKeyField,
                    InternalError, CharField)
import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
logger = settings.logger


class NoteMaster(BaseModel):
    id = PrimaryKeyField()
    note1 = CharField(null=True)
    note2 = CharField(null=True)
    note3 = CharField(null=True)
    note4 = CharField(null=True)
    note5 = CharField(null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "note_master"

    @classmethod
    def db_update_note_details(cls, dict_note_info, note_id):
        try:
            return NoteMaster.update(**dict_note_info).where(NoteMaster.id == note_id).execute()
        except InternalError as e:
            logger.error(e)
            raise InternalError(e)

