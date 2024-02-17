from peewee import PrimaryKeyField, ForeignKeyField, CharField

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_group_master import GroupMaster
import logging

logger = logging.getLogger("root")


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    # key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    # Constants
    UPDATE_ALT_CANISTER = 'Update Alternate Canister'
    UPDATE_ALT_DRUG_CANISTER = 'Update Alternate Drug Canister'
    UPDATE_ALT_DRUG = 'Update Alternate Drug'
    SKIP_FOR_BATCH = 'Skip for Batch'
    SKIP_FOR_PACKS = 'Skip for Packs'
    PACK_ASSIGNED = 'Pack assigned'
    NDC_CHANGE = 'Ndc change'
    PRINT_LABEL = 'Print label'
    PACK_FILLLED_PARTIALLY = 'Pack filled partially'
    SCAN_LABEL = 'Scan label'
    VERIFICATION = 'Verification'
    OUT_FOR_DELIVERY = 'Out for delivery'
    DELIVERED = 'Delivered'
    REPLENISH_AFTER_SKIP = "Replenish After Skip"

    ACTION_ID_MAP = {
        UPDATE_ALT_CANISTER: 3,
        UPDATE_ALT_DRUG_CANISTER: 4,
        UPDATE_ALT_DRUG: 5,
        SKIP_FOR_BATCH: 6,
        PACK_ASSIGNED: 7,
        NDC_CHANGE: 8,
        PRINT_LABEL: 9,
        PACK_FILLLED_PARTIALLY: 10,
        SCAN_LABEL: 11,
        VERIFICATION: 12,
        OUT_FOR_DELIVERY: 13,
        DELIVERED: 14,
        SKIP_FOR_PACKS: 50,
        REPLENISH_AFTER_SKIP: 53
    }

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"

    # @staticmethod
    # def get_initial_data():
    #     return [
    #         dict(group_id=9, key=1, value="AddQuantity"),
    #         dict(group_id=9, key=2, value="SubtractQuantity")
    #         ]