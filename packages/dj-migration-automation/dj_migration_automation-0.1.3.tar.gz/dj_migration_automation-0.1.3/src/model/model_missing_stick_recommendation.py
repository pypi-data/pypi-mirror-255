from peewee import PrimaryKeyField, ForeignKeyField, DecimalField, IntegerField, BooleanField, CharField, DateTimeField
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_unique_drug import UniqueDrug
from src.model.model_custom_drug_shape import CustomDrugShape
logger = settings.logger


class MissingStickRecommendation(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    width = DecimalField(decimal_places=3, max_digits=6)  # in mm
    length = DecimalField(decimal_places=3, max_digits=6)  # in mm
    depth = DecimalField(decimal_places=3, max_digits=6)  # in mm
    fillet = DecimalField(decimal_places=3, max_digits=6, null=True)
    shape_id = ForeignKeyField(CustomDrugShape)
    company_id = IntegerField()
    is_manual = BooleanField(default=False)
    image_url = CharField(null=True)
    user_id = IntegerField()
    created_at = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'missing_stick_recommendation'
