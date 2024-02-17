from peewee import PrimaryKeyField, ForeignKeyField, DateTimeField, IntegerField, InternalError, \
    IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_unique_drug import UniqueDrug
from src.model.model_canister_parameters import CanisterParameters

logger = settings.logger


class DrugCanisterParameters(BaseModel):
    """
    It contain the mapping related to canister parameters and drug
    """
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True)
    canister_parameter_id = ForeignKeyField(CanisterParameters)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_canister_parameters'

    @classmethod
    def db_create(cls, unique_drug_id, canister_parameter_id, user_id):
        """
        creates entry in db for unique_drug_id and canister_parameter_id
        :param int unique_drug_id:
        :param int canister_parameter_id:
        :param int user_id:
        :return: peewee.Model
        """
        return cls.create(
            unique_drug_id=unique_drug_id,
            canister_parameter_id=canister_parameter_id,
            created_by=user_id,
            modified_by=user_id
        )

    @classmethod
    def db_update(cls, record_id, canister_parameter_id, user_id):
        """
        updates entry in db for record_id with canister_parameter_id
        :param int record_id:
        :param int canister_parameter_id:
        :param int user_id:
        :return: peewee.Model
        """
        return cls.update(
            canister_parameter_id=canister_parameter_id,
            created_by=user_id,
            modified_by=user_id,
            modified_date=get_current_date_time()
        ).where(cls.id == record_id).execute()

    @classmethod
    def db_delete_by_unique_drug(cls, unique_drug_id) -> bool:
        """
        Deletes mapping between drug and canister parameter for given unique drug id.
        :param unique_drug_id: int
        :return:
        """
        try:
            status = cls.delete() \
                .where(DrugCanisterParameters.unique_drug_id == unique_drug_id) \
                .execute()

            logger.info('In db_delete_by_unique_drug: Deleting drug canister parameters '
                        'for unique drug ID: {}, deleted: {}'
                        .format(unique_drug_id, status))
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise


    @classmethod
    def db_add_drug_canister_parameter_mapping(cls, insert_dict) -> int:
        """
        insert drug canister parameter data in drug canister parameters table
        :return:
        """
        try:
            id = DrugCanisterParameters.insert(**insert_dict).execute()
            return id
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e
