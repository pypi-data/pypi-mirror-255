from peewee import (CharField, ForeignKeyField, PrimaryKeyField, IntegrityError, InternalError)
import settings
from dosepack.base_model.base_model import (BaseModel)
from src.model.model_mfd_canister_status_history import MfdCanisterStatusHistory
logger = settings.logger


class MfdStatusHistoryComment(BaseModel):
    id = PrimaryKeyField()
    status_history_id = ForeignKeyField(MfdCanisterStatusHistory)
    comment = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_status_history_comment"

    @classmethod
    def db_add_status_comment_history_data(cls, comment_history_list: list) -> int:
        """
        adds comment history in mfd_status_history_comment
        """
        try:
            update_status = cls.insert_many(comment_history_list).execute()
            logger.debug('cycle_comment_history_data_added_with_status: {}'.format(update_status))
            return update_status

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e
