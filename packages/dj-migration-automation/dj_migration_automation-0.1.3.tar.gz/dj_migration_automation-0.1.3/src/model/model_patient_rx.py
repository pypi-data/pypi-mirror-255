from peewee import PrimaryKeyField, IntegerField, ForeignKeyField, CharField, FixedCharField, BooleanField, \
    DateTimeField, FloatField, DecimalField, \
    SmallIntegerField, IntegrityError, InternalError, DataError, DateField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_doctor_master import DoctorMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_patient_master import PatientMaster

logger = settings.logger


class PatientRx(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster)
    drug_id = ForeignKeyField(DrugMaster)
    doctor_id = ForeignKeyField(DoctorMaster)
    pharmacy_rx_no = FixedCharField(max_length=20)
    to_fill_qty = DecimalField(decimal_places=2, max_digits=7, null=True)
    initial_fill_qty = DecimalField(decimal_places=2, max_digits=7, null=True)
    sig = CharField(max_length=1000)
    morning = FloatField(null=True)
    noon = FloatField(null=True)
    evening = FloatField(null=True)
    bed = FloatField(null=True)
    caution1 = CharField(null=True, max_length=300)
    caution2 = CharField(null=True, max_length=300)
    remaining_refill = DecimalField(decimal_places=2, max_digits=5)
    is_tapered = BooleanField(null=True)
    daw_code = SmallIntegerField(default=0)
    last_billed_date = DateField(null=True)
    packaging_type = ForeignKeyField(CodeMaster, default=constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4)
    last_pickup_date = DateField(null=True)
    next_pickup_date = DateField(null=True)
    prescribed_date = DateField(null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('patient_id', 'pharmacy_rx_no'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_rx"

    @classmethod
    def db_update_or_create_rx(cls, patient_id, pharmacy_rx_no, data, add_fields=None, remove_fields=None,
                               default_data_dict=None, stop_data=None):
        """
        Creates patient rx record using get_or_create, if already present then update data

        @param patient_id: Patient ID (will be used to get record)
        @param pharmacy_rx_no: Pharmacy rx no (will be used to get record)
        @param data: The record dict to be inserted in table.
        @param add_fields: The additional data to be added to record dict.
        @param remove_fields: The data to be removed from record dict.
        @param default_data_dict: The default data to be added along the record.
        :param stop_data:
        :return:
        """
        if default_data_dict:
            data.update(default_data_dict)

        # List of fields to be removed from data dictionary
        if remove_fields:
            for item in remove_fields:
                data.pop(item, 0)

        # List of additional fields to be added to data dictionary
        if add_fields:
            data.update(add_fields)

        try:
            record, created = PatientRx.get_or_create(patient_id=patient_id, pharmacy_rx_no=pharmacy_rx_no,
                                                      defaults=data)
            if not created:
                # Assuming when there is stop date, there is no chane in any other data in RX
                if stop_data or (record.pharmacy_rx_no == data['pharmacy_rx_no'] and \
                                 record.morning == data['morning'] and \
                                 record.sig == data['sig'] and \
                                 float(record.remaining_refill) == float(data['remaining_refill']) and \
                                 record.is_tapered == data['is_tapered'] and \
                                 float(record.noon) == float(data['noon']) and \
                                 float(record.evening) == float(data['evening']) and \
                                 float(record.bed) == float(data['bed']) and \
                                 record.caution1 == data['caution1'] and \
                                 record.caution2 == data['caution2'] and \
                                 record.daw_code == data['daw_code'] and \
                                 record.patient_id_id == data['patient_id'] and \
                                 record.drug_id_id == data['drug_id'] and \
                                 record.doctor_id_id == data['doctor_id'] and \
                                 record.packaging_type == data['packaging_type']):
                    return record
                else:
                    PatientRx.update(**data).where(PatientRx.id == record.id).execute()
            return record
        except (IntegrityError, InternalError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_patient_rx_data(cls, update_dict: dict, patient_rx_id: int) -> bool:
        """
        update patient rx data by patient rx id
        :return:
        """
        try:
            status = PatientRx.update(**update_dict).where(PatientRx.id == patient_rx_id).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_multiple_patient_rx_data(cls, update_dict: dict, patient_rx_id: list) -> bool:
        """
        update patient rx data by patient rx id
        :return:
        """
        try:
            status = PatientRx.update(**update_dict).where(PatientRx.id << patient_rx_id).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e
