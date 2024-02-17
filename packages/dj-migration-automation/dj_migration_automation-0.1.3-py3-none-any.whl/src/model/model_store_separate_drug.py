from peewee import PrimaryKeyField, IntegerField, ForeignKeyField, DateTimeField, DataError, IntegrityError, \
    InternalError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_dosage_type import DosageType
from src.model.model_unique_drug import UniqueDrug


logger = settings.logger


class StoreSeparateDrug(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True)
    dosage_type_id = ForeignKeyField(DosageType, null=True)
    # note = CharField(null=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('company_id', 'unique_drug_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "store_separate_drug"

    @classmethod
    def db_create_store_separate_drug(cls, company_id, unique_drug_id, dosage_type_id, user_id):
        """
        Creates record if not already present returns record otherwise.
        :param company_id: int
        :param unique_drug_id: int
        :param dosage_type_id: int
        :param user_id:int
        :return: tuple
        """
        try:
            record, created = cls.get_or_create(
                company_id=company_id,
                unique_drug_id=unique_drug_id,
                defaults={
                    'created_by': user_id,
                    'modified_by': user_id,
                    'dosage_type_id': dosage_type_id,
                }
            )
            return record, created
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise


    @classmethod
    def db_delete_separate_drug_dao(cls, drug_id_list):
        """
        function to delete store separate drug
        :return:
        """
        try:
            status = StoreSeparateDrug.delete().where(StoreSeparateDrug.id << drug_id_list)
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e
