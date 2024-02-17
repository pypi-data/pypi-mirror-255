from peewee import PrimaryKeyField, ForeignKeyField, DecimalField, IntegerField, DateTimeField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src.model.model_slot_header import SlotHeader
from src.model.model_pack_verification import PackVerification


class PackVerificationDetails(BaseModel):
    id = PrimaryKeyField()
    pack_verification_id = ForeignKeyField(PackVerification)
    slot_header_id = ForeignKeyField(SlotHeader)
    colour_status = ForeignKeyField(CodeMaster)
    compare_quantity = DecimalField(decimal_places=2, max_digits=4)
    dropped_quantity = DecimalField(decimal_places=2, max_digits=4)
    predicted_quantity = DecimalField(decimal_places=2, max_digits=4, null=True)
    created_by = IntegerField(default=1)
    created_date = DateTimeField(null=False, default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_verification_details"
