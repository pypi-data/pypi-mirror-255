from typing import List, Any
from peewee import (PrimaryKeyField, IntegerField, CharField, DateTimeField, DoesNotExist, InternalError,
                    IntegrityError, DataError)
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class SystemSetting(BaseModel):
    """
        @class: SystemSetting
        @createdBy: Dushyant Parmar
        @createdDate: 01/11/2018
        @lastModifiedBy: Dushyant Parmar
        @lastModifiedDate: 01/11/2018
        @type: class
        @desc: stores settings of system
    """
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField()
    value = CharField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "system_setting"
        indexes = (
            (('system_id', 'name'), True),  # keep trailing comma as suggested by peewee doc # unique setting per system
        )

    @classmethod
    def db_get_by_system_id(cls, system_id):
        system_settings: dict = dict()
        try:
            for record in SystemSetting.select(SystemSetting.name, SystemSetting.value).dicts() \
                    .where(SystemSetting.system_id == system_id):
                system_settings[record["name"]] = record["value"]
            return system_settings

        except IntegrityError as e:
            logger.error(e, exc_info=True)
            raise IntegrityError
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError

    @classmethod
    def db_update_or_create_record(cls, create_dict, update_dict):
        """
        checks if for the system id and name the data is created in system settings
        if created than updated or else create new row
        @param update_dict:
        @param create_dict:
        """
        try:
            record, created = SystemSetting.get_or_create(defaults=update_dict, **create_dict)
            response = "row created"
            if not created:
                update_dict['modified_date'] = get_current_date_time()
                SystemSetting.update(**update_dict).where(SystemSetting.id == record.id).execute()
                response = "row updated"
            return response

        except DataError as e:
            raise DataError(e)
        except IntegrityError as e:
            raise InternalError(e)
        except InternalError as e:
            raise InternalError(e)

    @classmethod
    def db_get_system_capacity(cls, system_id):
        try:
            capacity_value = float(SystemSetting.select(SystemSetting.value)
                                   .where((SystemSetting.system_id == system_id),
                                          (SystemSetting.name == settings.AUTOMATIC_PER_HOUR))
                                   .get().value)

            default_system_capacity_per_robot = SystemSetting.select(cls.value) \
                .where(cls.system_id == system_id,
                       cls.name == settings.DEFAULT_AUTOMATIC_PER_HOUR_PER_ROBOT) \
                .get().value
            return capacity_value, default_system_capacity_per_robot

        except IntegrityError as e:
            logger.error(e, exc_info=True)
            raise IntegrityError
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError

    @classmethod
    def db_update_system_capacity(cls, update_dict, system_id):

        try:
            system_status = SystemSetting.update(**update_dict) \
                .where((SystemSetting.system_id == system_id),
                       (SystemSetting.name == settings.AUTOMATIC_PER_HOUR)).execute()

            return system_status

        except IntegrityError as e:
            logger.error(e, exc_info=True)
            raise IntegrityError
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError

    @classmethod
    def db_get_by_system_id_list(cls, system_id_list: List[int]) -> List[Any]:
        """
        Fetches the data from the SystemSetting for the given list of system_ids.
        """
        try:
            return cls.select().dicts().where(cls.system_id.in_(system_id_list))
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_system_setting_info(cls):
        """
        Fetches the data from the SystemSetting
        """
        try:
            query = SystemSetting.select(
                SystemSetting.id,
                SystemSetting.system_id,
                SystemSetting.name,
                SystemSetting.value,
            )
            return query
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
