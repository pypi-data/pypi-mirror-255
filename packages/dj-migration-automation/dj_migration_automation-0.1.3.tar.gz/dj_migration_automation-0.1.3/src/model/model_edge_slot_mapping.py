from peewee import PrimaryKeyField, SmallIntegerField, TextField

import settings
from dosepack.base_model.base_model import BaseModel


class EdgeSlotMapping(BaseModel):
    id = PrimaryKeyField()
    group_no = SmallIntegerField()
    slots = TextField()
    configuration_mapping = TextField()
    quadrant = TextField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "edge_slot_mapping"

