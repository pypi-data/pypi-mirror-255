import logging
from typing import List, Dict

from peewee import ForeignKeyField, PrimaryKeyField, IntegerField, IntegrityError, DataError, InternalError, \
    DoesNotExist
import settings
from dosepack.base_model.base_model import BaseModel
from model.model_code import CodeMaster
from model.model_pack import PackDetails
from model.model_template import TemplateMaster
from src.model.model_ext_change_rx import ExtChangeRx

logger = logging.getLogger("root")


class ExtChangeRxPacks(BaseModel):
    id = PrimaryKeyField()
    ext_change_rx_id = ForeignKeyField(ExtChangeRx)
    ext_pack_display_id = IntegerField()
    template_id = ForeignKeyField(TemplateMaster)
    pack_id = ForeignKeyField(PackDetails, null=True)

    # If pack from IPS is at Pack stage then we need to update Pack Status
    # If pack from IPS is at Template stage then we need to update Template Status
    current_pack_status = ForeignKeyField(CodeMaster, related_name="current_pack_template_status")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ext_change_rx_packs"

    @classmethod
    def insert_ext_change_rx_packs(cls, pack_list: List[Dict]):
        """
        Method to save ext ChangeRx data in table ext_change_rx_packs
        """
        try:
            logger.debug("In insert_ext_change_rx_packs")
            ExtChangeRxPacks.insert_many(pack_list).execute()
        except (IntegrityError, DataError, InternalError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise
