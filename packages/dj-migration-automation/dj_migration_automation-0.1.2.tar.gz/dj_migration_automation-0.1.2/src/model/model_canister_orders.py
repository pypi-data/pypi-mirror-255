from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_drug_master import DrugMaster

logger = settings.logger


class CanisterOrders(BaseModel):
    id = PrimaryKeyField()
    drug_id = ForeignKeyField(DrugMaster, related_name="drug_id")
    order_status = ForeignKeyField(CodeMaster, default=constants.PENDING_ORDER)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_orders"

