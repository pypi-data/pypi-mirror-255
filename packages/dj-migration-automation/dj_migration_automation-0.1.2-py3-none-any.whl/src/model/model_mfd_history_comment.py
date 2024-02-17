from peewee import (CharField, ForeignKeyField, PrimaryKeyField, IntegrityError,
                    InternalError)
import settings
from dosepack.base_model.base_model import (BaseModel)
from src.model.model_mfd_cycle_history import MfdCycleHistory
logger = settings.logger


class MfdCycleHistoryComment(BaseModel):
    id = PrimaryKeyField()
    cycle_history_id = ForeignKeyField(MfdCycleHistory)
    comment = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_cycle_history_comment"

    @classmethod
    def db_add_comment_history_data(cls, comment_history_list: list) -> int:
        """
        adds comment history in mfd_cycle_history_comment
        """
        try:
            update_status = cls.insert_many(comment_history_list).execute()
            logger.debug('cycle_comment_history_data_added_with_status: {}'.format(update_status))
            return update_status

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e
