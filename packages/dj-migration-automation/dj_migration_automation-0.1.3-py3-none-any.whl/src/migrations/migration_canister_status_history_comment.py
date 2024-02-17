from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings
from src.model.model_canister_status_history import CanisterStatusHistory


class CanisterStatusHistoryComment(BaseModel):
    id = PrimaryKeyField()
    canister_status_history_id = ForeignKeyField(CanisterStatusHistory, related_name="canister_status_history_id_id")
    comment = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_status_history_comment"


def migration_add_comment_table():
    init_db(db, 'database_migration')
    db.create_tables([CanisterStatusHistoryComment], safe=True)
    print('Table(s) created: CanisterStatusHistoryComment')
