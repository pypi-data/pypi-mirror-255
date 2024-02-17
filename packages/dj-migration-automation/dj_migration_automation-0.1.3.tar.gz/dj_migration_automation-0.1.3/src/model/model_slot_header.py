from peewee import ForeignKeyField, PrimaryKeyField, DateField, TimeField
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_pack_details import PackDetails
from src.model.model_pack_grid import PackGrid


class SlotHeader(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    hoa_date = DateField(null=True)
    hoa_time = TimeField(null=True)
    pack_grid_id = ForeignKeyField(PackGrid, null=True, default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_header"
