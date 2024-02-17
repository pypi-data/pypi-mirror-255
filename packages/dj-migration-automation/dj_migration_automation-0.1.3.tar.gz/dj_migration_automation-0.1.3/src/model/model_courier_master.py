import settings
from peewee import PrimaryKeyField, CharField, DateTimeField, \
    InternalError, IntegrityError
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
logger = settings.logger


class CourierMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)
    website = CharField(null=True)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "courier_master"

    @staticmethod
    def get_initial_data():
        return [
            dict(id=1, name="FedEx", website="www.fedex.com"),
            dict(id=2, name="DHL", website="www.dhl.com"),
            dict(id=3, name="USPS", website="www.usps.com"),
            dict(id=4, name="UPS", website="www.ups.com")
        ]


    @classmethod
    def db_get_couriers_data(cls):
        try:
            return CourierMaster.select().dicts()
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

