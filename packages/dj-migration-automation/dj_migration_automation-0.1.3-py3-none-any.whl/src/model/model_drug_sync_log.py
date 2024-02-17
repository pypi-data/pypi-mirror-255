from peewee import PrimaryKeyField, ForeignKeyField, BooleanField

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_sync_history import DrugSyncHistory


class DrugSyncLog(BaseModel):
    id = PrimaryKeyField()
    drug_sync_history_id = ForeignKeyField(DrugSyncHistory)
    drug_id = ForeignKeyField(DrugMaster)
    inserted = BooleanField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_sync_log"



