"""
    @file: src/model/model_pvs_pack.py
    @type: file
    @desc: model class for db table pvs_pack
"""

from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_details import PackDetails
from src.model.model_device_master import DeviceMaster

logger = settings.logger


class PVSPack(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails, related_name='pvspack_pack_id')
    device_id = ForeignKeyField(DeviceMaster, related_name='pvspack_device_id')
    mfd_status = BooleanField(default=False)
    user_station_status = BooleanField(default=False)
    deleted = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(null=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_pack'



