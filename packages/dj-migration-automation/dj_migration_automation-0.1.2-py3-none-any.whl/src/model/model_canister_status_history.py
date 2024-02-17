from peewee import PrimaryKeyField, IntegerField, DateTimeField, ForeignKeyField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster


class CanisterMaster(BaseModel):
    """
        @desc: logical class for table canister_master
    """
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class CanisterStatusHistory(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    action = ForeignKeyField(CodeMaster)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    associated_canister = ForeignKeyField('self', null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_status_history"
