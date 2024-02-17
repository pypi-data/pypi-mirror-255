import logging
from peewee import *

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_code_master import CodeMaster
from src.model.model_device_master import DeviceMaster

logger = settings.logger


# added batch_master here, to resolve import error
class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class CanisterTxMeta(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    cycle_id = IntegerField()
    device_id = ForeignKeyField(DeviceMaster)
    status_id = ForeignKeyField(CodeMaster)
    to_cart_transfer_count = IntegerField()
    from_cart_transfer_count = IntegerField()
    normal_cart_count = IntegerField()
    elevator_cart_count = IntegerField()
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        indexes = (
            (('batch_id', 'cycle_id', 'device_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tx_meta"

    @classmethod
    def update_canister_tx_data(cls, update_dict, meta_id):
        try:
            logger.info("update_canister_tx_data {}, {}".format(update_dict, meta_id))
            return CanisterTxMeta.update(**update_dict).where(CanisterTxMeta.id == meta_id).execute()

        except (IntegrityError, InternalError, DataError) as e:
            logger.error("Error in updating canister tx data {}".format(e))
            raise


    @classmethod
    def db_update_canister_tx_meta_by_batch_id(cls, update_dict, batch_id, cycle_id=None):
        try:
            logger.info("db_update_canister_tx_meta_by_batch_id {}, {}".format(update_dict, batch_id))
            if cycle_id:
                return CanisterTxMeta.update(**update_dict).where(CanisterTxMeta.batch_id == batch_id,
                                                                  CanisterTxMeta.cycle_id == cycle_id).execute()
            return CanisterTxMeta.update(**update_dict).where(CanisterTxMeta.batch_id == batch_id).execute()

        except (IntegrityError, InternalError, DataError) as e:
            logger.error("Error in db_update_canister_tx_meta_by_batch_id {}".format(e))
            raise
