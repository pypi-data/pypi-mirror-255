from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
logger = settings.logger


class DeviceTypeMaster(BaseModel):
    id = PrimaryKeyField()
    device_type_name = CharField(max_length=50, unique=True)
    device_code = CharField(max_length=10, null=True, unique=True)
    container_code = CharField(max_length=10, null=True, unique=True)
    station_type_id = IntegerField(unique=True, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_type_master"

    @classmethod
    def add_device_type(cls, device_type_data):
        logger.debug("In add_device_type")
        try:
            query = BaseModel.db_create_record(device_type_data, DeviceTypeMaster, get_or_create=False)
            return query.id

        except IntegrityError as e:
            raise
        except InternalError as e:
            raise InternalError
        except DataError as e:
            raise DataError

    @classmethod
    def get_device_type_id(cls, device_type_name):
        logger.debug("In get_device_type_id")
        try:
            query = DeviceTypeMaster.select(DeviceTypeMaster.id).dicts().where(
                DeviceTypeMaster.device_type_name == device_type_name).get()

            return query

        except DoesNotExist as e:
            raise DoesNotExist
        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError

    @classmethod
    def get_code_by_station_type_id(cls, station_type_id: int):
        try:
            query = DeviceTypeMaster.select(DeviceTypeMaster.container_code, DeviceTypeMaster.device_code).dicts() \
                .where(DeviceTypeMaster.station_type_id == station_type_id)
            for record in query:
                return record
        except (IntegrityError, InternalError, DoesNotExist) as e:
            raise e
