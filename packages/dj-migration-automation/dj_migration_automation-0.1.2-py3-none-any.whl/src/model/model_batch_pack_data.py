from typing import List, Dict, Any

from peewee import (PrimaryKeyField, DateTimeField, TextField, CharField, InternalError, IntegrityError, DataError,
                    DoesNotExist)

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class BatchPackData(BaseModel):
    id = PrimaryKeyField()
    unique_id = CharField(max_length=15)
    pack_id_list = TextField()
    created_date = DateTimeField(default=get_current_date_time)
    inventory_consideration = TextField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_pack_data"

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
