from typing import List, Dict, Any

from peewee import (IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, CharField, IntegrityError,
                    InternalError, DataError, DoesNotExist)

import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
from src.model.model_batch_drug_data import BatchDrugData

logger = settings.logger


class PreOrderMissingNdc(BaseModel):
    id = PrimaryKeyField()
    batch_drug_data_id = ForeignKeyField(BatchDrugData)
    ndc = CharField(max_length=14)
    created_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pre_order_missing_ndc"

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Inserts multiple records in the PreOrderMissingNdc.
        """
        logger.debug("Inside PreOrderMissingNdc.insert_data")
        try:
            cls.insert_many(data_list).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
