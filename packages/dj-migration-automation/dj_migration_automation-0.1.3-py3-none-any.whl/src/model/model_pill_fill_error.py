from peewee import IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, DecimalField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_details import PackDetails
from src.model.model_slot_header import SlotHeader

logger = settings.logger


class PillJumpError(BaseModel):

    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails, unique=False)
    slot_number = IntegerField()
    quantity = DecimalField(decimal_places=2, max_digits=4, null=True)
    device_id = IntegerField()
    quadrant = IntegerField()
    drop_number = IntegerField()
    config_id = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pill_jump_error"

