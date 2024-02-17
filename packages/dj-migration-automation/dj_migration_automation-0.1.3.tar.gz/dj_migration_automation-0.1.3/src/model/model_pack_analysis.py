from peewee import PrimaryKeyField, ForeignKeyField, BooleanField, DateTimeField, DoesNotExist, IntegrityError, \
    InternalError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_batch_master import BatchMaster
from src.model.model_pack_details import PackDetails

logger = settings.logger


class PackAnalysis(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    pack_id = ForeignKeyField(PackDetails)
    manual_fill_required = BooleanField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_analysis"


    @classmethod
    def db_update_manual_packs(cls, analysis_ids: list, manual: bool) -> bool:
        try:
            if analysis_ids:
                status = PackAnalysis.update(manual_fill_required=manual) \
                    .where(PackAnalysis.id << analysis_ids).execute()
                return status
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise
