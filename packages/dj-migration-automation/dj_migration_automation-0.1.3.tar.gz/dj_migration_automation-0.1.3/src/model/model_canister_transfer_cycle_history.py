from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_action_master import ActionMaster
from src.model.model_code_master import CodeMaster

logger = settings.logger


# TODO change this when canister transfer function are moved inside
class CanisterTransfers(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfers"


class CanisterTransferCycleHistory(BaseModel):
    id = PrimaryKeyField()
    canister_transfer_id = ForeignKeyField(CanisterTransfers)
    action_id = ForeignKeyField(ActionMaster)
    current_status_id = ForeignKeyField(CodeMaster, related_name='current_status')
    previous_status_id = ForeignKeyField(CodeMaster, related_name='previous_state')
    action_taken_by = IntegerField(null=False)
    action_datetime = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfer_cycle_history"

    @classmethod
    def insert_canister_transfer_cycle_history_data(cls, data_dict: dict):
        """
        This function inserts multiple records to the canister_transfer_cycle_history table.
        @param data_dict:
        @return:
        """
        logger.info("Input of insert_canister_transfer_cycle_history_data {}".format(data_dict))
        try:
            record = cls.create(**data_dict)
            return record
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e)
            raise
