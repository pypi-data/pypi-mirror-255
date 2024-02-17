from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class CanisterTransfers(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfers"


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'group_master'


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


class CanisterTransferCycleHistory(BaseModel):
    id = PrimaryKeyField()
    canister_transfer_id = ForeignKeyField(CanisterTransfers)
    action_id = ForeignKeyField(ActionMaster)
    current_status_id = ForeignKeyField(CodeMaster, related_name='current_status')
    previous_status_id = ForeignKeyField(CodeMaster, related_name='previous_state')
    action_taken_by = IntegerField(null=False)
    action_datetime = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfer_cycle_history"


class CanisterTransferHistoryComment(BaseModel):
    id = PrimaryKeyField()
    canister_tx_history_id = ForeignKeyField(CanisterTransferCycleHistory)
    comment = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfer_history_comment"


def migration_add_canister_tx_history_tables():
    init_db(db, 'database_migration')
    db.create_tables([CanisterTransferCycleHistory], safe=True)
    print('Table(s) created: CanisterTransferCycleHistory')
    db.create_tables([CanisterTransferHistoryComment], safe=True)
    print('Table(s) created: CanisterTransferHistoryComment')


