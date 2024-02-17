from typing import List, Dict, Any

from peewee import (PrimaryKeyField, DecimalField, CharField, ForeignKeyField, DateTimeField, InternalError,
                    IntegrityError, DataError, DoesNotExist)

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_action_master import ActionMaster

logger = settings.logger


class LocalDITransaction(BaseModel):
    id = PrimaryKeyField()
    ndc = CharField(max_length=14)
    formatted_ndc = CharField(max_length=12)
    txr = CharField(max_length=8, null=True)
    quantity = DecimalField(decimal_places=2)
    action_id = ForeignKeyField(ActionMaster, null=False)
    comment = CharField(null=True, default=None)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "local_di_transaction"

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Inserts multiple records in the LocalDITransaction.
        """
        logger.debug("Inside LocalDITransaction.insert_data")
        try:
            cls.insert_many(data_list).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
