"""
    @file: src/model/model_pvs_dimension.py
    @type: file
    @desc: model class for db table pvs_slot_image_dimension
"""
from playhouse.migrate import *

import settings
from settings import logger
from dosepack.base_model.base_model import BaseModel
from src.model.model_device_master import DeviceMaster


class PVSDimension(BaseModel):
    id = PrimaryKeyField()
    company_id = SmallIntegerField(null=False)
    device_id = ForeignKeyField(DeviceMaster, related_name='pvsdimension_device_id')
    quadrant = SmallIntegerField(default=0)
    left_value = IntegerField(default=0)
    right_value = IntegerField(default=1280)
    top_value = IntegerField(default=0)
    bottom_value = IntegerField(default=720)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pvs_dimension"

