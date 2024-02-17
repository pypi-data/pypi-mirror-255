from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, CharField, BooleanField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_details import PackDetails
from src.model.model_action_master import ActionMaster


class PackHistory(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    action_id = ForeignKeyField(ActionMaster)
    action_taken_by = IntegerField()
    action_date_time = DateTimeField(default=get_current_date_time)
    old_value = CharField(null=True)
    new_value = CharField(null=True)
    from_ips = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_history"