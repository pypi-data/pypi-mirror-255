from peewee import (PrimaryKeyField, IntegerField, DateTimeField, DateField, InternalError,
                    IntegrityError, DataError, FloatField)
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
logger = settings.logger


class OverLoadedPackTiming(BaseModel):
    id = PrimaryKeyField()
    date = DateField()
    system_id = IntegerField()
    extra_time = FloatField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "overloaded_pack_timings"

    @classmethod
    def db_update_or_create_record(cls, create_dict, update_dict):
        """
        checks if for the system and user the data is created in overloaded packs
        timing table if not then inserts a row and if created than updates the values
        @param update_dict:
        @param create_dict:
        """
        try:
            record, created = OverLoadedPackTiming.get_or_create(defaults=update_dict, **create_dict)
            print("record", record.id)
            print("created", created)
            response = "row created"
            if not created:
                update_dict['modified_date'] = get_current_date_time()
                OverLoadedPackTiming.update(**update_dict).where(OverLoadedPackTiming.id == record.id).execute()
                response = "row updated"
            return response
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def get_extra_hours(cls, date_range, system_id):
        date_extra_hours = {}
        try:
            for record in OverLoadedPackTiming.select(OverLoadedPackTiming.date, OverLoadedPackTiming.system_id,
                                                      OverLoadedPackTiming.extra_time).dicts() \
                    .where(OverLoadedPackTiming.system_id == system_id, OverLoadedPackTiming.date in date_range):
                date_extra_hours[str(record["date"])] = record["extra_time"]
            return date_extra_hours

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_add_overloaded_pack_timing_data(cls, insert_dict: list) -> bool:
        """
        adds overloaded pack timing data in overloaded pack table
        """
        try:
            insert_status = cls.insert_many(insert_dict).execute()
            logger.info('In db_add_overloaded_pack_timing_data: {}'.format(insert_status))
            return insert_status

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e
