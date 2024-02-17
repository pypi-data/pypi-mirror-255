from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_unique_drug import UniqueDrug


logger = settings.logger


class DrugDetails(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True)
    company_id = IntegerField()
    last_seen_by = IntegerField()
    last_seen_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_details"
