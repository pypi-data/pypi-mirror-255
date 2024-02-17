from typing import List

from peewee import ForeignKeyField, PrimaryKeyField, InternalError, IntegrityError, DataError, DoesNotExist, TextField, \
    IntegerField, DateTimeField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_canister_master import CanisterMaster
from src.model.model_code_master import CodeMaster
from src.model.model_drug_master import DrugMaster
from src import constants

logger = settings.logger


class CanisterTestingStatus(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster, null=False)
    drug_id = ForeignKeyField(DrugMaster, null=False)
    status_id = ForeignKeyField(CodeMaster, default=constants.CANISTER_TESTING_PENDING, null=False)
    reason = TextField(null=True)
    tested = IntegerField(default=0)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time())
    modified_by = IntegerField(null=True)
    modified_date = DateTimeField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_testing_status"

    @classmethod
    def insert_canister_testing_status_data(cls, data_dict_list: List[dict]) -> bool:
        """
        This function inserts multiple records to the Canister Testing Status table.
        @param data_dict_list:
        @return:
        """
        logger.debug("Inside insert_canister_testing_status_data.")

        try:
            cls.insert_many(data_dict_list).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e)
            raise

    @classmethod
    def db_update_canister_id(cls, new_canister_id, old_canister_id):
        """
        update order no
        :return:
        """
        try:
            status = cls.update(canister_id=new_canister_id).where(
                        cls.canister_id == old_canister_id).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise
