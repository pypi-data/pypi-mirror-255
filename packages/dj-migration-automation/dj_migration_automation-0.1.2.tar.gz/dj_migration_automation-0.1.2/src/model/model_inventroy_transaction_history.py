from typing import List, Dict, Any

from peewee import (PrimaryKeyField, DateTimeField, TextField, CharField, InternalError, IntegrityError, DataError,
                    DoesNotExist, DecimalField, BooleanField)

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class InventoryTransactionHistory(BaseModel):
    id = PrimaryKeyField()
    uid = CharField(max_length=15, null=True)
    ndc = CharField(max_length=14, null=True)
    quantity = DecimalField(decimal_places=2, null=True)
    adjustmentDate = DateTimeField(default=get_current_date_time)
    typeOfTransaction = TextField(null=True)
    note = TextField(null=True)
    lotNumber = TextField(null=True)
    expirationDate = TextField(null=True)
    caseId = CharField(null=True, default=None)
    isCanisterAdjustment = BooleanField(null=True, default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "inventory_transaction_history"

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Inserts multiple records in the BatchPackData.
        """
        logger.debug("Inside BatchPackData.insert_data")
        try:
            cls.insert_many(data_list).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
