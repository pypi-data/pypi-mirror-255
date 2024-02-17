from peewee import PrimaryKeyField, ForeignKeyField, CharField, InternalError, IntegrityError, IntegerField, TextField, \
    DateTimeField
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_device_type_master import DeviceTypeMaster

logger = settings.logger


class ConfigurationMaster(BaseModel):
    # todo: verify with robot team what data they want in it
    id = PrimaryKeyField()
    company_id = IntegerField()
    device_type_id = ForeignKeyField(DeviceTypeMaster)
    device_version = CharField(null=True)
    configuration_name = CharField(max_length=50)
    configuration_value = TextField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "configuration_master"

    @staticmethod
    def get_initial_data():
        return [
            dict(id=1, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(1,1),(2,2),(3,3),(4,4)}", device_version="3.0"),
            dict(id=2, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(1,2),(4,3)}", device_version="3.0"),
            dict(id=3, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(1,4),(2,3)}", device_version="3.0"),
            dict(id=4, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(2,1),(3,4)}", device_version="3.0"),
            dict(id=5, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(3,1),(4,2)}", device_version="3.0"),
            dict(id=6, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(1,3)}", device_version="3.0"),
            dict(id=7, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(2,4)}", device_version="3.0"),
            dict(id=8, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(3,1)}", device_version="3.0"),
            dict(id=9, company_id=3, device_type_id=settings.DEVICE_TYPES["ROBOT"], configuration_name="alignment",
                 configuration_value="{(4,2)}}", device_version="3.0")
        ]
