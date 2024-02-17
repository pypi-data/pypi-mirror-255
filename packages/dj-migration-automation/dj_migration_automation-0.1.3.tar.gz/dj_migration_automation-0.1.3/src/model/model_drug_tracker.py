import settings
from peewee import *
from src.model.model_code_master import CodeMaster
from src.model.model_drug_master import DrugMaster
from dosepack.base_model.base_model import BaseModel
from src.model.model_slot_details import SlotDetails
from src.model.model_pack_details import PackDetails
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_canister_master import CanisterMaster
from dosepack.utilities.utils import get_current_date_time
from src.model.model_canister_tracker import CanisterTracker
from peewee import ForeignKeyField, DateTimeField, PrimaryKeyField, IntegerField, DecimalField, SmallIntegerField

logger = settings.logger


class DrugTracker(BaseModel):
    id = PrimaryKeyField()
    slot_id = ForeignKeyField(SlotDetails, related_name="slot_details_slot_id")
    canister_id = ForeignKeyField(CanisterMaster, null=True, related_name="canister_master_canister_id")
    drug_id = ForeignKeyField(DrugMaster, related_name="drug_master_drug_id")
    drug_quantity = DecimalField(decimal_places=2, max_digits=4)
    canister_tracker_id = ForeignKeyField(CanisterTracker, null=True,
                                          related_name="canister_tracker_canister_tracker_id")
    comp_canister_tracker_id = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    # is_deleted = BooleanField(default=False)
    drug_lot_master_id = ForeignKeyField(DrugLotMaster, null=True)
    filled_at = IntegerField(default=None)
    created_by = IntegerField(default=None)
    pack_id = ForeignKeyField(PackDetails, null=True)
    is_overwrite = SmallIntegerField(default=0)
    scan_type = ForeignKeyField(CodeMaster, default=None, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    case_id = CharField(null=True, default=None)
    reuse_quantity = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    reuse_pack = IntegerField(null=True, default=None)
    item_id = CharField(null=True)
    original_quantity = DecimalField(decimal_places=2, max_digits=7, null=True, default=None)
    expiry_date = CharField(null=True)
    lot_number = CharField(null=True)
    error_reason = CharField(null=True, default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_tracker"

    @classmethod
    def db_update_drug_tracker_by_slot_id(cls, update_dict, slot_ids):
        logger.info("In db_update_drug_tracker_by_slot_id")
        try:
            status = DrugTracker.update(**update_dict).where(DrugTracker.slot_id << slot_ids).execute()
            return status
        except Exception as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_drug_tracker_by_drug_tracker_id(cls, update_dict, drug_tracker_ids):
        logger.info("In db_update_drug_tracker_by_drug_tracker_id")
        try:
            status = DrugTracker.update(**update_dict).where(DrugTracker.id << drug_tracker_ids).execute()
            return status
        except Exception as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_drug_tracker_data_by_slot_id(cls, slot_id):
        logger.info("In db_get_drug_tracker_data_by_slot_id")
        try:
            data = DrugTracker.select().dicts()\
                .where((DrugTracker.slot_id == slot_id) & (DrugTracker.is_overwrite == 0))\
                .execute()
            return data
        except Exception as e:
            logger.error("Error in db_get_drug_tracker_data_by_slot_id: {}".format(e))
            raise e

    @classmethod
    def db_delete_drug_tracker_by_slot_id(cls, slot_ids):
        logger.info("In db_delete_drug_tracker_by_slot_id")
        try:
            status = DrugTracker.delete().where(DrugTracker.slot_id << slot_ids).execute()
            logger.info("Deleting from table -- DrugTracker ||| Row Deleted: {}".format(status))

            return status
        except Exception as e:
            logger.error("Error in db_delete_drug_tracker_by_slot_id: {}".format(e))
            raise e
