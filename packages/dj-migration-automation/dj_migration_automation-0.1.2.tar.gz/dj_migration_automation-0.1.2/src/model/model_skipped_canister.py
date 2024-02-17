from peewee import (IntegerField, ForeignKeyField, PrimaryKeyField, IntegrityError, InternalError, DateTimeField,
                    CharField)
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src import constants
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_code_master import CodeMaster

logger = settings.logger


class SkippedCanister(BaseModel):
    # Stores canister id and batch id which were not followed by user in pack pre-processing
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster, null=True)
    canister_id = ForeignKeyField(CanisterMaster)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    skipped_from = ForeignKeyField(CodeMaster, default=constants.SKIPPED_FROM_PACK_PRE_PROCESSING)
    skip_reason = CharField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "skipped_canister"

    @classmethod
    def db_get(cls, batch_id):
        """
        Returns skipped canister ids for given batch_id
        :param batch_id: int
        :return: list
        """
        results = list()
        try:
            query = SkippedCanister.select(SkippedCanister.canister_id) \
                .where(SkippedCanister.batch_id == batch_id) \
                .dicts()
            for record in query:
                results.append(record["canister_id"])
            return results
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_delete_by_batch(cls, batch_id):
        try:
            return SkippedCanister.delete().where(SkippedCanister.batch_id == batch_id).execute()
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_insert_many(cls, skipped_canister_list):
        try:
            return SkippedCanister.insert_many(skipped_canister_list).execute()
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise
