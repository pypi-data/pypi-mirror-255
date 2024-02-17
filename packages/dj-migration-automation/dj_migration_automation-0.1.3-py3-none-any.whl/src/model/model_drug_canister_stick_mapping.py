from peewee import PrimaryKeyField, ForeignKeyField, DateTimeField, IntegerField, IntegrityError, InternalError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_canister_stick import CanisterStick
from src.model.model_drug_dimension import DrugDimension

logger = settings.logger


class DrugCanisterStickMapping(BaseModel):
    """
    This table maps the DrugDimension and CanisterStickDimension.
    """
    id = PrimaryKeyField()
    drug_dimension_id = ForeignKeyField(DrugDimension)
    canister_stick_id = ForeignKeyField(CanisterStick)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_canister_stick_mapping'

    @classmethod
    def db_delete_by_drug_dimension(cls, drug_dimension_id) -> bool:
        """
        Deletes mapping of drug dimension and canister stick
        :param drug_dimension_id: int ID of drug dimension table
        :return:
        """
        try:
            status = cls.delete()\
                .where(cls.drug_dimension_id == drug_dimension_id)\
                .execute()
            logger.info('In db_delete_by_drug_dimension: Deleting drug canister stick mapping '
                        'for drug dimension ID: {}, deleted: {}'
                        .format(drug_dimension_id, status))
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_update_drug_canister_stick_mapping_by_dimension_id(cls, drug_dimension_id, update_dict) -> bool:
        """
        update canister stick mapping by drug dimension id
        :return:
        """
        try:
            status = DrugCanisterStickMapping.update(**update_dict) \
                .where(DrugCanisterStickMapping.drug_dimension_id == drug_dimension_id).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_delete_drug_canister_stick_by_id(cls, id) -> bool:
        """
        delete drug canister stick mapping by DrugCanisterStickMapping id
        :return:
        """
        try:
            status = DrugCanisterStickMapping.delete(). \
                where(DrugCanisterStickMapping.id == id).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

