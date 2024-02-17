from typing import List, Any, Dict
from peewee import (IntegerField, DateTimeField, PrimaryKeyField,
                    InternalError, ForeignKeyField, IntegrityError, DataError)
import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
from src.model.model_pack_rx_link import PackRxLink

logger = settings.logger


class MissingDrugPack(BaseModel):
    id = PrimaryKeyField()
    pack_rx_id = ForeignKeyField(PackRxLink)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "missing_drug_pack"

    @classmethod
    def add_missing_drug_record(cls, missing_drug_list_insert_dict: List[Dict[str, Any]]):
        try:
            status = cls.insert_many(missing_drug_list_insert_dict).execute()
            return status
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise
