from peewee import PrimaryKeyField, ForeignKeyField, DecimalField, BooleanField, CharField, DateTimeField, IntegerField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_drug_master import DrugMaster
from src.model.model_vision_drug_prediction import VisionDrugPrediction, logger


# This table has vision system prediction information
class VisionCountPrediction (BaseModel):
    id = PrimaryKeyField()
    vision_drug_prediction_id = ForeignKeyField(VisionDrugPrediction)
    predicted_pill_count = DecimalField(decimal_places=2, max_digits=4) # vision system detected pill count
    actual_pill_count = DecimalField(decimal_places=2, max_digits=4) # number of pills to be dropped by that robot
    predicted_drug_id = ForeignKeyField(DrugMaster, null=True)
    is_unknown = BooleanField(null=True) # flag for unknown drug (from vision system)
    pill_extra_data = CharField(null=True, max_length=500) # coordinates of drugs present in Image, accuracy for each pill
    error_reported = BooleanField(null=True) # flag to store reported error by the user
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField (null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "vision_count_prediction"
