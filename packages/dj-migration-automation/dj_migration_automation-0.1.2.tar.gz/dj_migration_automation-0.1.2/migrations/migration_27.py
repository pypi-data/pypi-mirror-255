from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
from src.model.model_patient_master import PatientMaster
from playhouse.migrate import *
import settings

class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        db_table = 'batch_master'


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        db_table = 'canister_master'


class SkippedCanister(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "skipped_canister"


def migrate_27():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)
    db.create_tables([SkippedCanister], safe=True)
    print("Tables created: SkippedCanister")

if __name__ == "__main__":
    migrate_27()
