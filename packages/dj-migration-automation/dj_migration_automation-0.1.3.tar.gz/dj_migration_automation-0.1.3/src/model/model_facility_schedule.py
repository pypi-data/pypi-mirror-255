from datetime import timedelta

from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, InternalError, IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
import logging

logger = settings.logger
schedule_logger = logging.getLogger("schedule")



class FacilitySchedule(BaseModel):
    id = PrimaryKeyField()
    fill_cycle = ForeignKeyField(CodeMaster)  # 46=Weekly, 47=Bi-weekly, 48=monthly(28 days) and 49=other
    # week_day = IntegerField(null=True)  # 0=Monday, 1=Tuesday, .. 5=Saturday, 6=Sunday
    days = IntegerField(null=True)  # scheduled after every n days
    start_date = DateTimeField(null=True)  # start date for schedule
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    # Constants
    SCHEDULE_TYPE_WEEKLY = 46
    SCHEDULE_TYPE_BI_WEEKLY = 47
    SCHEDULE_TYPE_MONTHLY = 48
    SCHEDULE_TYPE_OTHER = 49
    FREQUENCY_IN_DAYS_DICT = {SCHEDULE_TYPE_WEEKLY: 7, SCHEDULE_TYPE_BI_WEEKLY: 14, SCHEDULE_TYPE_MONTHLY: 28}
    FREQUENCY_DICT = {k: '{}D'.format(v) for k, v in FREQUENCY_IN_DAYS_DICT.items()}

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'facility_schedule'

    @classmethod
    def db_add_facility_schedule(cls, schedule_data):
        try:
            default_dict = {
                'created_by': schedule_data['created_by'],
                'modified_by': schedule_data['modified_by']
            }
            get_dict = {
                'fill_cycle': schedule_data["fill_cycle"],
                # 'week_day': schedule_data["week_day"],
                'start_date': schedule_data["start_date"],
                'days': schedule_data.get('days'),
            }
            record, created = cls.get_or_create(defaults=default_dict, **get_dict)
            return record
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            return error(2001)

    @classmethod
    def db_update_schedule(cls, schedule_data, schedule_id):
        try:
            status = cls.update(**schedule_data).where(cls.id == schedule_id).execute()
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            return error(2001)

    @staticmethod
    def next_weekday(date, weekday):
        """
        returns specified weekday from given date
        :param date: datetime.date
        :param weekday: int
        :return:
        """
        day_gap = weekday - date.weekday()
        if day_gap < 0:
            day_gap += 7
        return date + timedelta(days=day_gap)