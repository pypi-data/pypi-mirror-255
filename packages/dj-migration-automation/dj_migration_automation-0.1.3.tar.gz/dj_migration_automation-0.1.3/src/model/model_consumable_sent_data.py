import settings
from dosepack.base_model.base_model import BaseModel
from peewee import PrimaryKeyField, IntegerField, DateTimeField, InternalError, IntegrityError, fn, TextField, DateField

from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class ConsumableSentData(BaseModel):
    id = PrimaryKeyField()
    sent_data = TextField()
    company_id = IntegerField()
    stock_req_date = DateField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "consumable_sent_data"

    @classmethod
    def db_get_date_of_last_sent_consumable_data(cls, company_id):
        try:
            logger.info("In db_get_date_of_last_sent_consumable_data")
            query = cls.select(fn.MAX(ConsumableSentData.stock_req_date).alias('max_date')).where(cls.company_id==company_id)
            for date in query.dicts():
                return date['max_date']
            return None
        except (InternalError, IntegrityError) as e:
            logger.info("Error in db_get_date_of_last_sent_consumable_data: {}".format(e))
            raise e
