from peewee import CharField, IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, InternalError
import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src.model.model_pack_details import PackDetails

logger = settings.logger


class PackStatusTracker(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    status = ForeignKeyField(CodeMaster)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    reason = CharField(max_length=500, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_status_tracker"

    @classmethod
    def db_track_status(cls, pack_status_list):
        try:
            with db.transaction():
                status = PackStatusTracker.insert_many(pack_status_list).execute()
                # create record for pack status tracker
            return status
        except InternalError as ex:
            logger.error(ex, exc_info=True)
            return error(1004)

