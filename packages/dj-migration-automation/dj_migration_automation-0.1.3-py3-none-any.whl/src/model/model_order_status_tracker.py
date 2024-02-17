import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField
from src.model.model_code_master import CodeMaster
from src.model.model_orders import Orders


class OrderStatusTracker(BaseModel):
    id = PrimaryKeyField()
    order_id = ForeignKeyField(Orders)
    status = ForeignKeyField(CodeMaster, related_name="order_status_tracker")
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "order_status_tracker"
