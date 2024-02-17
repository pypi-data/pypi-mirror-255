"""
    @file: src/model/model_pvs_slot_details.py
    @type: file
    @desc: model class for db table pvs_slot_details
"""
from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src.model.model_unique_drug import UniqueDrug
from src.model.model_pvs_slot import PVSSlot


class PVSSlotDetails(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_id = ForeignKeyField(PVSSlot, related_name='pvsslotdetails_pvs_slot_id')
    crop_image_name = CharField(null=False)
    predicted_label_drug_id = ForeignKeyField(UniqueDrug, related_name='pvsslotdetails_predicted_label_drug_id',
                                              null=True)
    pvs_classification_status = ForeignKeyField(CodeMaster, related_name='pvsslotdetails_pvs_classification_status',
                                                null=True)
    pill_centre_x = FloatField(null=True)
    pill_centre_y = FloatField(null=True)
    radius = FloatField(null=True)
    created_date = DateTimeField(null=False, default=get_current_date_time)
    modified_date = DateTimeField(null=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot_details'
