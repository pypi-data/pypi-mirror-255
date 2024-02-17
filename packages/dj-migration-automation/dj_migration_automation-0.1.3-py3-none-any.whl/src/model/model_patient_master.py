from peewee import PrimaryKeyField, IntegerField, ForeignKeyField, CharField, FixedCharField, BooleanField, DateField, \
    DateTimeField, fn, DoesNotExist, InternalError, DataError, IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src import constants
from src.model.model_facility_master import FacilityMaster

logger = settings.logger


class PatientMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    facility_id = ForeignKeyField(FacilityMaster)
    pharmacy_patient_id = IntegerField()
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    patient_picture = CharField(null=True)
    address1 = CharField()
    zip_code = CharField(max_length=9)
    city = CharField(max_length=50, null=True)
    state = CharField(max_length=50, null=True)
    address2 = CharField(null=True)
    cellphone = FixedCharField(max_length=14, null=True)
    workphone = FixedCharField(max_length=14, null=True)
    fax = FixedCharField(max_length=14, null=True)
    email = CharField(max_length=320, null=True)
    website = CharField(null=True, max_length=50)
    active = BooleanField(null=True)
    dob = DateField(null=True)
    allergy = CharField(null=True, max_length=500)
    patient_no = FixedCharField(null=True, max_length=35)
    delivery_route_name = CharField(default=constants.NULL_ROUTE_NAME)
    delivery_route_id = IntegerField(default=constants.NULL_ROUTE_NAME_ID)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pharmacy_patient_id', 'company_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_master"

    @classmethod
    def db_get_patient_name_from_patient_id(cls, patient_ids):
        patient_id_name_dict = {}
        try:
            query = PatientMaster.select(PatientMaster.id, PatientMaster.first_name, PatientMaster.last_name)\
                .where(PatientMaster.id << patient_ids)
            for record in query.dicts():
                patient_id_name_dict[record['id']] = record['last_name'] + ',' + record['first_name']

            return patient_id_name_dict
        except (InternalError, IntegrityError, Exception) as ex:
            logger.error(ex, exc_info=True)
            raise

    @classmethod
    def db_get_patient_name_patient_no_from_patient_id(cls, patient_id):
        try:
            return PatientMaster.select(PatientMaster.id, PatientMaster.first_name, PatientMaster.last_name,
                                        PatientMaster.concated_patient_name_field().alias("patient_name"),
                                        PatientMaster.patient_no.alias("patient_no")).dicts() \
                .where(PatientMaster.id == patient_id)

        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            return []
        except (InternalError, IntegrityError, Exception) as ex:
            logger.error(ex, exc_info=True)
            raise

    @classmethod
    def concated_patient_name_field(cls, sep=', '):
        """ returns concated peewee.Field for format "last_name, first_name" """
        return fn.CONCAT(cls.last_name, sep, cls.first_name)

    @classmethod
    def db_update_or_create(cls, data, pharmacy_patient_id, company_id, add_fields=None, remove_fields=None,
                            fn_transform=None, fn_validate=None, default_data_dict=None):
        """ Takes data from the file and updates the data if exists else creates new record.

            Args:
                data (dict): The record dict to be inserted in table.
                pharmacy_patient_id: Value against which record will be identified uniquely.
                company_id: The id of the Company
                add_fields (optional argument) (dict): The additional data to be added to record dict.
                remove_fields (optional argument) (dict): The data to be removed from record dict.
                fn_transform (optional argument) (dict): The transformation rules if any for the record.
                fn_validate (optional argument) (dict): The validation rules if any for the record dict.
                default_data_dict (optional argument) (boolean): The default data to be added along the record.

            Returns:
               Model.Record : Returns the record containing data.

            Raises:
                IntegrityError: If the record with the provided primary key already exists
                InternalError: If the record to be inserted does not have have valid fields.

            Examples:
                >>> create_record([], [])
                [0, 1, 2, 3]
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
            record, created = PatientMaster.get_or_create(
                pharmacy_patient_id=pharmacy_patient_id,
                company_id=company_id,
                defaults=data
            )
            if not created:
                PatientMaster.update(**data) \
                    .where(PatientMaster.pharmacy_patient_id == pharmacy_patient_id,
                           PatientMaster.company_id == company_id).execute()

        except DataError as e:
            raise DataError(e)
        except IntegrityError as e:
            raise InternalError(e)
        except InternalError as e:
            raise InternalError(e)
        return record

    @classmethod
    def db_get_patient_info_by_patient_id(cls, patient_id):
        try:
            return PatientMaster.get(id=patient_id)
        except (DataError, InternalError, IntegrityError) as e:
            raise e
