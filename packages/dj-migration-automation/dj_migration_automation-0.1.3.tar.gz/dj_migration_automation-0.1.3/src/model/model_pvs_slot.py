"""
    @file: src/model/model_pvs_slot.py
    @type: file
    @desc: model class for db table pvs_slot
"""
from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src.model.model_pack_details import PackDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_device_master import DeviceMaster


class PVSSlot(BaseModel):
    id = PrimaryKeyField()
    slot_header_id = ForeignKeyField(SlotHeader, null=True, related_name='pvsslot_slot_header_id')
    drop_number = IntegerField(null=False)
    slot_image_name = CharField(null=False)
    expected_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    pvs_identified_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    robot_drop_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    mfd_status = BooleanField(default=False)
    created_date = DateTimeField(null=False, default=get_current_date_time)
    modified_date = DateTimeField(null=False)
    us_status = ForeignKeyField(CodeMaster, related_name='pvsslot_us_status')
    device_id = ForeignKeyField(DeviceMaster, related_name='pvsslot_device_id')
    quadrant = SmallIntegerField(null=True)
    associated_device_id = IntegerField(default=1)
    pack_id = ForeignKeyField(PackDetails, unique=False, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot'
