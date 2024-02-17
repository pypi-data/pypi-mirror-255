from dosepack.base_model.base_model import BaseModel
from src.model.model_action_master import ActionMaster
from dosepack.utilities.utils import get_current_date_time
from peewee import *
import settings
from src.model.model_drug_lot_master import DrugLotMaster

logger = settings.logger


class DrugBottleQuantityTracker(BaseModel):
    id = PrimaryKeyField()
    lot_id = ForeignKeyField(DrugLotMaster)
    bottle_id = IntegerField(null=True)
    quantity_adjusted = SmallIntegerField()
    action_performed = ForeignKeyField(ActionMaster)
    bottle_qty_updated = BooleanField(default=False)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_bottle_quantity_tracker"

    @classmethod
    def insert_bottle_quantity_tracker_information(cls, tracker_data):
        """
        :param tracker_data:
        :return:
        """
        try:
            query_response = BaseModel.db_create_record(tracker_data, DrugBottleQuantityTracker, get_or_create=False)
            return query_response.id

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e
