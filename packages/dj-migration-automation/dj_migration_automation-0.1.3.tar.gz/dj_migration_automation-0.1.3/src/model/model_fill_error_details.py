from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_pack_details import PackDetails

logger = settings.logger


class FillErrorDetails(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    fill_error_note = CharField(null=True, default=None)
    assigned_to = IntegerField()
    reported_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time())
    modified_date = DateTimeField(default=get_current_date_time())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "fill_error_details"

