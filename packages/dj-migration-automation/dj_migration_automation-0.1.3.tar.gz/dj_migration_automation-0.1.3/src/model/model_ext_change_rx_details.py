import logging
from typing import List, Dict

from peewee import ForeignKeyField, PrimaryKeyField, CharField, DateField, IntegrityError, DataError, InternalError, \
    DoesNotExist, IntegerField, DateTimeField
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_action_master import ActionMaster

from src.model.model_ext_change_rx import ExtChangeRx

logger = logging.getLogger("root")


class ExtChangeRxDetails(BaseModel):
    id = PrimaryKeyField()
    ext_change_rx_id = ForeignKeyField(ExtChangeRx)
    ext_pharmacy_rx_no = CharField(max_length=20)
    action_id = ForeignKeyField(ActionMaster)
    ext_comment = CharField(null=True)
    start_date = DateField(null=True)
    end_date = DateField(null=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ext_change_rx_details"

# class ExtChangeRxDetails(BaseModel):
#     id = PrimaryKeyField()
#     ext_change_rx_id = ForeignKeyField(ExtChangeRx)
#     ext_pharmacy_rx_no = CharField(max_length=20)
#     action_id = ForeignKeyField(ActionMaster)
#     start_date = DateField()
#     end_date = DateField()
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "ext_change_rx_details"

    @classmethod
    def insert_ext_change_rx_details(cls, rx_list: List[Dict]) -> int:
        """
        Method to save ext ChangeRx data in table ext_change_rx_details
        """
        try:
            logger.debug("In insert_ext_change_rx_details")
            return ExtChangeRxDetails.insert_many(rx_list).execute()
        except (IntegrityError, DataError, InternalError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise
