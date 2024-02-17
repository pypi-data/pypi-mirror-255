from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
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


class RobotMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        db_table = 'robot_master'


class CanisterTransfers(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    dest_robot_id = ForeignKeyField(RobotMaster, null=True)
    dest_canister_number = SmallIntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfers"


def migrate_10():
    init_db(db, 'database_migration')
    db.create_tables([CanisterTransfers], safe=True)
    print('Table(s) created: CanisterTransfers')
