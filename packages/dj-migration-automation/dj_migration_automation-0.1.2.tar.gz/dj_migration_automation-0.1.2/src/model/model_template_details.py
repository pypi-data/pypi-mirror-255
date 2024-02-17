from peewee import PrimaryKeyField, ForeignKeyField, SmallIntegerField, TimeField, IntegerField, DecimalField, \
    DateTimeField, InternalError, IntegrityError, DataError, DoesNotExist

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_patient_rx import PatientRx
from src.model.model_file_header import FileHeader
from src.model.model_patient_master import PatientMaster


logger = settings.logger


class TemplateDetails(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster)
    file_id = ForeignKeyField(FileHeader)
    patient_rx_id = ForeignKeyField(PatientRx)
    column_number = SmallIntegerField()
    hoa_time = TimeField()
    quantity = DecimalField(decimal_places=2, max_digits=4)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_details"

    @classmethod
    def db_delete(cls, patient_id):
        """ Deletes the template records from the template_details
            table for the given patient_id.
            Args:
                patient_id (int): The patient_id for the given patient.
            Returns:
                Boolean : Returns True if deletion is successful or else False

            Examples:
                >>> TemplateDetails.delete_template_details(1)
                >>> True
        """
        try:
            template_data = cls.delete() \
                .where(cls.patient_id == patient_id)
            template_data.execute()

        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_delete_templates_by_patient_file_ids(cls, patient_id, file_ids):
        try:
            status = TemplateDetails.delete().where(TemplateDetails.patient_id == patient_id,
                                                    TemplateDetails.file_id << file_ids).execute()
            return status
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_modified_time(cls, patient_id):
        """ Takes patient_id and returns the last modified time of the corresponding template.

             Args:
                 patient_id (int): The id of the patient

             Returns:
                 List : Last modified_time of the template

             Examples:
                 >>> db_get_modified_time()
         """
        try:
            query = cls.select(cls.modified_date).where(
                cls.patient_id == patient_id
            ).order_by(cls.column_number, cls.patient_rx_id)
            # ordering to keep modified date consistent with template returned to front-end
            modified_time = query.get().modified_date
            return modified_time

        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_column_number(cls, patient_rx_id, hoa_time, quantity):
        """ Returns the pack column number for the given rx_id, quantity and time.

            Args:
                patient_rx_id (int): The rx_id associated with the patient
                hoa_time (time): The time associated with the rx_id
                quantity(float): The quantity associated with the rx_id

            Returns:
                int : column_number for the given parameters

            Examples:
                >>> db_get_column_number(1)
                >>> True

        """
        try:
            return cls.get(patient_rx_id=patient_rx_id, hoa_time=hoa_time, quantity=quantity).column_number
        except DoesNotExist:
            return None
