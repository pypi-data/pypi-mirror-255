from peewee import PrimaryKeyField, ForeignKeyField, DecimalField, CharField, IntegerField, DateTimeField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_rx_link import PackRxLink


class PartiallyFilledPack(BaseModel):
    id = PrimaryKeyField()
    pack_rx_id = ForeignKeyField(PackRxLink)
    missing_qty = DecimalField(decimal_places=2, max_digits=4)
    note = CharField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_rx_id', 'missing_qty'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "partially_filled_pack"