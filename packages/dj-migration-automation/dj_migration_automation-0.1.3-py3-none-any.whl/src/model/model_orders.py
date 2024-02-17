import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, CharField, DateTimeField,\
    SmallIntegerField, InternalError, IntegrityError
from src.model.model_code_master import CodeMaster
logger = settings.logger


class Orders(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    inquiry_no = CharField(unique=True)  # company code-timestamp
    status = ForeignKeyField(CodeMaster, related_name="order_status")
    lead_time = SmallIntegerField(null=True)  # in days
    payment_link = CharField(null=True)
    inquired_by = IntegerField()
    approval_date = DateTimeField(null=True)
    approved_by = IntegerField(null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "orders"

    @classmethod
    def db_update_orders(cls, dict_order_info, order_id):
        """ update order table for given order id"""
        try:
            return Orders.update(**dict_order_info).where(Orders.id == order_id).execute()
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e
