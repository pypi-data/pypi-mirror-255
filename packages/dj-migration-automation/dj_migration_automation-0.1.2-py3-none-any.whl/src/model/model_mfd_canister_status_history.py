from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import get_current_date_time
from src.model.model_action_master import ActionMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_mfd_canister_master import (MfdCanisterMaster)
logger = settings.logger


class MfdCanisterStatusHistory(BaseModel):
    id = PrimaryKeyField()
    mfd_canister_id = ForeignKeyField(MfdCanisterMaster)
    action_id = ForeignKeyField(ActionMaster)
    home_cart = ForeignKeyField(DeviceMaster, related_name='cart')
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_status_history"
