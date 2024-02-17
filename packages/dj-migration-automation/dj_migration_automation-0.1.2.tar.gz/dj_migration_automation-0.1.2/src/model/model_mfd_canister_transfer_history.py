from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import get_current_date_time
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_canister_master import (MfdCanisterMaster)
logger = settings.logger


class MfdCanisterTransferHistory(BaseModel):
    id = PrimaryKeyField()
    mfd_canister_id = ForeignKeyField(MfdCanisterMaster)
    current_location_id = ForeignKeyField(LocationMaster, null=True, related_name='mfd_current_location_id')
    previous_location_id = ForeignKeyField(LocationMaster, null=True, related_name='mfd_previous_location_id')
    is_transaction_manual = BooleanField(default=False)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_transfer_history"

    @classmethod
    def db_get_latest_record_by_canister_id(cls, mfd_canister_id: int) -> object:
        """
        returns last transaction history for given mfd_canister
        :param mfd_canister_id: int
        :return: record
        """
        try:
            record = MfdCanisterTransferHistory.select() \
                .where(MfdCanisterTransferHistory.mfd_canister_id == mfd_canister_id) \
                .order_by(cls.id.desc()).get()
            return record
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e
        except DoesNotExist as e:
            logger.info(e, exc_info=True)
            return None
