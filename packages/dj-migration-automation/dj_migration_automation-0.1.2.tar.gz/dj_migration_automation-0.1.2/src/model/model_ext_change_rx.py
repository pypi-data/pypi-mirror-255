import logging
from typing import Any, Dict

from peewee import IntegerField, DateTimeField, PrimaryKeyField, IntegrityError, DataError, \
    InternalError, DoesNotExist, ForeignKeyField, BooleanField
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

from src.model.model_code_master import CodeMaster
from src.model.model_template_master import TemplateMaster

logger = logging.getLogger("root")


class ExtChangeRx(BaseModel):
    id = PrimaryKeyField()
    current_template = ForeignKeyField(TemplateMaster)
    ext_action = ForeignKeyField(CodeMaster)
    new_template = ForeignKeyField(TemplateMaster, null=True, related_name='new_template')
    company_id = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(null=True)
    # old_pack_state = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ext_change_rx"

    @classmethod
    def insert_ext_change_rx_data(cls, data_list: dict) -> int:
        """
        Method to insert data into ext_Change_Rx table
        """
        try:
            logger.debug("In insert_ext_change_rx_data")
            record_id = ExtChangeRx.insert(**data_list).execute()
            return record_id
        except (IntegrityError, DataError, InternalError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_ext_change_rx_new_template(cls, data_list: Dict[str, Any], ext_change_rx_id: list):
        try:
            logger.debug("In update_ext_change_rx_data")
            ExtChangeRx.update(**data_list).where(ExtChangeRx.id << ext_change_rx_id).execute()
        except (IntegrityError, DataError, InternalError, DoesNotExist, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get(cls, template_id: int) -> Dict[str, Any]:
        ext_change_rx_dict: Dict[str, Any] = dict()

        try:
            logger.debug("In ExtChangeRx --> db_get")
            query = ExtChangeRx.select(ExtChangeRx.id.alias("ext_change_rx_id"))\
                .where(ExtChangeRx.new_template == template_id)

            for ext_data in query.dicts():
                ext_change_rx_dict["ext_change_rx_id"] = ext_data["ext_change_rx_id"]

            return ext_change_rx_dict

        except (IntegrityError, DataError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_old_template_by_new_template(cls, template_id: int):
        old_template_id: int = 0
        try:
            query = ExtChangeRx.select(ExtChangeRx).dicts()\
                .where(ExtChangeRx.new_template == template_id,
                       ExtChangeRx.ext_action == settings.PENDING_CHANGE_RX_TEMPLATE_STATUS_PACK)

            for record in query:
                old_template_id = record["current_template"]

            return old_template_id
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return 0
        except (IntegrityError, DataError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise
