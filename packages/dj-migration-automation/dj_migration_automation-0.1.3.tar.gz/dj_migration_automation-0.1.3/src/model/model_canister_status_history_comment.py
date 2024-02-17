from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_canister_status_history import CanisterStatusHistory

logger = settings.logger


class CanisterStatusHistoryComment(BaseModel):
    id = PrimaryKeyField()
    canister_status_history_id = ForeignKeyField(CanisterStatusHistory)
    comment = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_status_history_comment"

    @classmethod
    def insert_canister_status_history_comment_data(cls, data_dict: dict):
        """
        This function inserts multiple records to the canister_transfer_history_comment table.
        @param data_dict:
        @return:
        """
        logger.debug("Inside insert_canister_status_history_comment_data.")

        try:
            record = cls.create(**data_dict)
            return record
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error("Error in insert_canister_status_history_comment_data {}".format(e))
            raise
