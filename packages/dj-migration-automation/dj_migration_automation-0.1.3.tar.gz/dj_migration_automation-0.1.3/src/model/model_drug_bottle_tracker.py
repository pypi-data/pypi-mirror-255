from dosepack.base_model.base_model import BaseModel
from src.model.model_action_master import ActionMaster
from dosepack.utilities.utils import get_current_date_time
from peewee import *
import settings
from src.model.model_drug_bottle_master import DrugBottleMaster

logger = settings.logger


class DrugBottleTracker(BaseModel):
    """
    Table to store the update in quantity of the Bottle
    """
    id = PrimaryKeyField()
    bottle_id = ForeignKeyField(DrugBottleMaster)
    quantity_adjusted = SmallIntegerField()
    action_performed = ForeignKeyField(ActionMaster)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_bottle_tracker"
