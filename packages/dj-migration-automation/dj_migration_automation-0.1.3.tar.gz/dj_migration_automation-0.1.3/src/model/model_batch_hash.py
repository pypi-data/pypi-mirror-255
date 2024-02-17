import hashlib

from peewee import (ForeignKeyField, PrimaryKeyField, CharField, DateTimeField)
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_batch_master import BatchMaster

logger = settings.logger


class BatchHash(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    batch_hash = CharField()  # hash of sorted pack ids separated by ,
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_hash"

    @classmethod
    def generate_batch_hash(cls, pack_list):
        """
        Generate hash for given pack list
        :param pack_list: list
        :return: str
        """
        sorted_pack_str = ",".join(sorted(list(map(str, set(pack_list)))))
        _hash = str(hashlib.sha512(sorted_pack_str.encode()).hexdigest())
        logger.debug('Generated Batch Hash {} for pack list {}, type of hash {}'.format(_hash, pack_list, type(_hash)))
        return _hash
