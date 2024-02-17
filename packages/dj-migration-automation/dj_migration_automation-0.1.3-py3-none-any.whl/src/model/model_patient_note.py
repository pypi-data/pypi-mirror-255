from peewee import PrimaryKeyField, ForeignKeyField, CharField, IntegerField, DateTimeField, InternalError, \
    IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_patient_master import PatientMaster


logger = settings.logger


class PatientNote(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster, unique=True)
    note = CharField(max_length=500)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_note"

    @classmethod
    def db_get(cls, patient_id):
        try:
            patient_note_data = cls.select(
                cls.note,
                cls.patient_id,
                cls.created_date,
                cls.modified_date,
                cls.created_by,
                cls.modified_by
            ).where(cls.patient_id == patient_id).dicts().get()
            return patient_note_data
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_or_create(cls, patient_id, note, user_id):
        """
        Updates if note of patient is already present else
        :param patient_id: Patient ID
        :param note: Note for the patient
        :param user_id: User ID
        :return: peewee.Model
        """
        try:
            default_data = {
                'note': note,
                'created_by': user_id,
                'modified_by': user_id
            }
            record, created = cls.get_or_create(
                patient_id=patient_id, defaults=default_data
            )
            if not created:
                default_data.pop('created_by', None)
                default_data['modified_date'] = get_current_date_time()
                cls.update(**default_data) \
                    .where(cls.patient_id == patient_id) \
                    .execute()
            return record
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise
