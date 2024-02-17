from typing import List, Dict, Any, Optional

from peewee import (PrimaryKeyField, CharField, DateTimeField, InternalError, IntegrityError, DataError, DoesNotExist,
                    TextField)
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class LocalDIPOData(BaseModel):
    id = PrimaryKeyField()
    po_number = CharField(max_length=20, unique=True)
    po_ack_data = TextField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "local_di_po_data"

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Inserts multiple records in the LocalDIPOData.
        """
        logger.debug("Inside LocalDIPOData.insert_data")
        try:
            cls.insert_many(data_list).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def get_data(cls, created_after_date: Optional[str] = None) -> List[Any]:
        """
        Fetches the data for the records created after the given date
        """
        logger.debug("Inside LocalDIPOData.get_data_created_after_given_date")
        try:
            if created_after_date:
                return cls.select().dicts().where(cls.created_date > created_after_date)
            else:
                return cls.select().dicts()
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
