from datetime import timedelta
import pandas as pd
from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, SmallIntegerField, BooleanField, DateTimeField, \
    InternalError, IntegrityError, DoesNotExist
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_facility_master import FacilityMaster
from src.model.model_patient_master import PatientMaster
from src.model.model_facility_schedule import FacilitySchedule
import logging

logger = settings.logger
schedule_logger = logging.getLogger("schedule")


class PatientSchedule(BaseModel):
    id = PrimaryKeyField()
    facility_id = ForeignKeyField(FacilityMaster)
    patient_id = ForeignKeyField(PatientMaster)
    schedule_id = ForeignKeyField(FacilitySchedule, null=True)
    total_packs = IntegerField()
    delivery_date_offset = SmallIntegerField(null=True, default=None)
    active = BooleanField(default=True)
    last_import_date = DateTimeField(default=get_current_date_time)
    patient_overwrite = BooleanField(default=0)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('facility_id', 'patient_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'patient_schedule'

    @classmethod
    def db_get_or_create_schedule(cls, patient_id, facility_id, total_packs):
        record, created = cls.get_or_create(patient_id= patient_id, facility_id=facility_id,
                                            defaults={'schedule_id': None, 'total_packs': total_packs})
        return record, created

    @staticmethod
    def get_schedule_dict(record):
        fields = ['schedule_id', 'schedule_date', 'facility_name', 'data_from_facility_schedule', 'fill_cycle', 'value', 'days',
                  'ips_delivery_date', 'facility_id', 'delivery_date', 'last_import_date', 'scheduled_patient_ids',
                  'patient_ids', 'delivery_date_offset']
        _date_format = '%m-%d-%y'
        offset = record['delivery_date_offset']
        ips_delivery_date = record['ips_delivery_date']

        # if pack_header_delivery_date != "":
        #     record['delivery_date'] = pack_header_delivery_date
        #     record['data_from_facility_schedule'] = False
        if offset is not None:
            record['delivery_date'] = record['schedule_date'] + timedelta(days=offset)
            record['delivery_date'] = record['delivery_date'].strftime(_date_format)
            record['data_from_facility_schedule'] = True
        else:
            record['delivery_date'] = None
            record['data_from_facility_schedule'] = False

        record['schedule_date'] = record['schedule_date'].strftime(_date_format)
        if record['last_import_date']:
            record['last_import_date'] = record['last_import_date'].date().strftime(_date_format)
        return record

    @classmethod
    def get_next_schedule_from_last_import(cls, record):
        """
        Returns next schedule based on next delivery date greater than last_import date
        :param record: dict with keys ['fill_cycle', 'days', 'last_import_date',
                                       'start_date', 'delivery_date_offset']
        :return:
        """

        schedule_logger.info('Schedule ID: {}'.format(record['schedule_facility_id']))
        try:
            freq_dict = FacilitySchedule.FREQUENCY_DICT
            freq_in_days_dict = FacilitySchedule.FREQUENCY_IN_DAYS_DICT
            frequency = freq_dict[record['fill_cycle']]
            freq_in_days = freq_in_days_dict[record['fill_cycle']]
        except KeyError as e:
            frequency = "{}D".format(record['days'])
            freq_in_days = record['days']
        schedule_logger.info('Frequency: {}'.format(frequency))

        if record['delivery_date_offset'] is None:
            schedule_logger.warning('Schedule ID: {} does not have '
                                    'delivery_date_offset'.format(record["schedule_facility_id"]))
            record['delivery_date'] = record
        last_import_date = record['last_import_date']
        start_date = record['start_date'].date()
        schedule_logger.info('Found Start Date: {}'.format(start_date))
        end_date = start_date if last_import_date.date() <= start_date else last_import_date
        # pick the date further away in future between start date and last_import_date
        end_date = end_date + timedelta(days=freq_in_days * 1)
        schedules = pd.date_range(start_date, end=end_date, freq=frequency)
        schedule_logger.info('Schedules: {}'.format(schedules))
        found = False

        # if import date not available, consider first schedule (should not be the actual case)
        if last_import_date and record['delivery_date_offset'] is not None:
            # iterate through schedules, reverse as high chance to get it at the end
            schedules = sorted(schedules, reverse=True)
            for index, sd in enumerate(schedules):
                delivery_date = sd + timedelta(days=record['delivery_date_offset'])
                if delivery_date.date() < last_import_date.date():
                    try:
                        record['schedule_date'] = schedules[index - 1].date()
                    except IndexError as e:
                        schedule_logger.error(
                            'Could not find schedule date, IndexError: {}'.format(e))
                        break
                    found = True
                    schedule_logger.info('schedule_date: {} found in schedules, schedules: {}'
                                         .format(record['schedule_date'], schedules))
                    break
        if not found:  # schedule date in future
            schedule_logger.info('Could not find any schedule less '
                                 'than last_import_date {} in schedules: {}'
                                 .format(last_import_date, schedules))
            schedule_logger.info('Selecting schedule: {}'.format(schedules[-1]))
            record['schedule_date'] = schedules[-1].date()
        return cls.get_schedule_dict(record)

    @classmethod
    def db_get_patient_schedule_data(cls, facility_id, patient_id):
        try:
            return PatientSchedule.select().dicts() \
                .where(PatientSchedule.facility_id == facility_id,
                       PatientSchedule.active == True,
                       PatientSchedule.patient_id != patient_id).get()
        except (InternalError, IntegrityError, DoesNotExist, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_patient_schedule_data_dao(cls, patient_schedule_id, update_dict):
        try:
            return PatientSchedule.update(**update_dict).where(PatientSchedule.id == patient_schedule_id).execute()
        except (InternalError, IntegrityError, DoesNotExist, Exception) as e:
            logger.error(e, exc_info=True)
            raise
