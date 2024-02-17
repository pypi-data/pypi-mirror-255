import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, CharField, DateTimeField
from src.model.model_courier_master import CourierMaster
from src.model.model_orders import Orders
logger = settings.logger


class ShipmentTracker(BaseModel):
    id = PrimaryKeyField()
    order_id = ForeignKeyField(Orders)
    courier_id = ForeignKeyField(CourierMaster)
    tracking_number = CharField(max_length=36)
    created_by = IntegerField()
    created_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "shipment_tracker"
