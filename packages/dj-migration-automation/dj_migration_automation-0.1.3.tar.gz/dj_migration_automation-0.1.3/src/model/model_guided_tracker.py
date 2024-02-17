from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_canister_master import CanisterMaster
from src.model.model_code_master import CodeMaster
from src import constants
from src.model.model_guided_meta import GuidedMeta
from src.model.model_location_master import LocationMaster

logger = settings.logger


class GuidedTracker(BaseModel):
    id = PrimaryKeyField()
    guided_meta_id = ForeignKeyField(GuidedMeta)
    source_canister_id = ForeignKeyField(CanisterMaster)
    alternate_canister_id = ForeignKeyField(CanisterMaster, null=True, related_name="alternate_canister_for_tracker")
    alt_can_replenish_required = BooleanField(null=True)
    cart_location_id = ForeignKeyField(LocationMaster)
    destination_location_id = ForeignKeyField(LocationMaster, related_name="dest_location_for_tracker")
    transfer_status = ForeignKeyField(CodeMaster, default=constants.GUIDED_TRACKER_PENDING)
    required_qty = IntegerField(null=False, default=0)
    created_date = DateTimeField(default=get_current_date_time())
    modified_date = DateTimeField(default=get_current_date_time())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "guided_tracker"

    @classmethod
    def db_get_guided_canister_data(cls, guided_tx_cycle_id):
        """ get guided canister data from guided tracker for  guided_tx_cycle_id"""
        try:
            logger.info('In db_get_guided_canister_data: guided_tx_cycle_id: {}'.format(guided_tx_cycle_id))
            transfer_status_list = [constants.GUIDED_TRACKER_PENDING,
                                    constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE,
                                    constants.GUIDED_TRACKER_TO_TROLLEY_DONE]
            canister_data_query = GuidedTracker.select(GuidedTracker.source_canister_id,
                                                       GuidedTracker.alternate_canister_id,
                                                       GuidedTracker.alt_can_replenish_required,
                                                       GuidedTracker.required_qty).dicts() \
                .where((GuidedTracker.guided_meta_id == guided_tx_cycle_id) &
                       (GuidedTracker.transfer_status.in_(transfer_status_list)))
            return canister_data_query
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
