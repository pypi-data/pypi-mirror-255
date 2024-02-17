from peewee import PrimaryKeyField, DateTimeField, IntegerField, DoesNotExist, InternalError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time


class DrugSyncHistory(BaseModel):
    id = PrimaryKeyField()
    sync_time = DateTimeField(null=True)
    created_by = IntegerField(null=True)
    created_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_sync_history"

    @classmethod
    def db_get_last_update_datetime(cls):
        try:
            record = DrugSyncHistory.select() \
                .where(DrugSyncHistory.sync_time.is_null(False)) \
                .order_by(DrugSyncHistory.sync_time.desc()).get()
            return record.sync_time
        except DoesNotExist:
            raise DoesNotExist
        except InternalError:
            raise DoesNotExist