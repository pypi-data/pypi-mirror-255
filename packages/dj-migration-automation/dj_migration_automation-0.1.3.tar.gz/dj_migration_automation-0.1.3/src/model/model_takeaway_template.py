from peewee import PrimaryKeyField, ForeignKeyField, SmallIntegerField, IntegerField, DateTimeField, InternalError, \
    IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_patient_master import PatientMaster


logger = settings.logger


class TakeawayTemplate(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster)
    week_day = SmallIntegerField()
    template_column_number = SmallIntegerField()
    column_number = SmallIntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "takeaway_template"

    @classmethod
    def db_get(cls, patient_id):
        try:
            query = cls.select(
                cls.patient_id,
                cls.week_day,
                cls.column_number,
                cls.template_column_number
            ).dicts() \
                .where(cls.patient_id == patient_id)
            for record in query:
                yield record
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise


    @classmethod
    def db_get_take_away_template_by_patient(cls, patient_id):
        """
        function get template by patient id
        :return:
        """
        try:
            query = TakeawayTemplate.select(TakeawayTemplate.week_day,
                                            TakeawayTemplate.column_number,
                                            TakeawayTemplate.template_column_number,
                                            TakeawayTemplate.patient_id,
                                            TakeawayTemplate.id).dicts() \
                .where(TakeawayTemplate.patient_id == patient_id)
            return query
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e
