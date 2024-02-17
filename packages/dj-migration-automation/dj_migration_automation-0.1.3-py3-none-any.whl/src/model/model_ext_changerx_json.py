import logging
from typing import List, Dict

from peewee import PrimaryKeyField, ForeignKeyField, TextField, IntegrityError, DataError, InternalError, DoesNotExist

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_ext_change_rx import ExtChangeRx

logger = logging.getLogger("root")


class ExtChangeRxJson(BaseModel):
    id = PrimaryKeyField()
    ext_change_rx_id = ForeignKeyField(ExtChangeRx)
    ext_data = TextField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ext_change_rx_json"

    @classmethod
    def insert_ext_change_rx_json(cls, rx_json_list: List[Dict]) -> int:
        try:
            logger.debug("In insert_ext_change_rx_json")
            return cls.insert_many(rx_json_list).execute()
        except (IntegrityError, DataError, InternalError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise
