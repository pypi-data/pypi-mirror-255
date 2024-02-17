from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src import constants
from src.model.model_device_master import DeviceMaster

logger = settings.logger


class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class GuidedMeta(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster, null=True)
    mini_batch_id = IntegerField()
    cart_id = ForeignKeyField(DeviceMaster)
    status = ForeignKeyField(CodeMaster, default=constants.GUIDED_META_RECOMMENDATION_DONE)
    total_transfers = IntegerField(default=0)
    alt_canister_count = IntegerField(default=0)
    alt_can_replenish_count = IntegerField(default=0)
    replenish_skipped_count = IntegerField(default=0)
    created_date = DateTimeField(default=get_current_date_time())
    modified_date = DateTimeField(default=get_current_date_time())
    pack_ids = TextField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "guided_meta"












