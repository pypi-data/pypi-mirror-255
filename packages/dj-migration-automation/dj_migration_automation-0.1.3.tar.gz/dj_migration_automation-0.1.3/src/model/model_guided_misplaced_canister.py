from peewee import ForeignKeyField, PrimaryKeyField, InternalError, IntegrityError, DataError

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_canister_master import CanisterMaster
from src.model.model_code_master import CodeMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_guided_meta import GuidedMeta

logger = settings.logger


class GuidedMisplacedCanister(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    device_id = ForeignKeyField(DeviceMaster)
    guided_meta_id = ForeignKeyField(GuidedMeta)
    guided_status = ForeignKeyField(CodeMaster)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "guided_misplaced_canister"

    @classmethod
    def db_insert_canister_data(cls, misplaced_canister_data):
        """
        insert misplaced canister data in guided missing canister table
        @param misplaced_canister_data:
        """
        try:
            status = cls.insert_many(misplaced_canister_data).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def check_if_canister_data_exit(cls, canister_id, device_id, guided_meta_id):
        """
        check if record is exist in table for given device and meta id
        :return:
        """
        try:
            existence = cls.select(cls.id).where(cls.canister_id == canister_id, cls.device_id == device_id,
                                                 cls.guided_meta_id == guided_meta_id).exists()
            return existence
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_delete_canister_data(cls, canister_id, device_id, guided_meta_id):
        """
        function to delete canister data from table
        :return:
        """
        try:
            status = cls.delete().where(cls.canister_id == canister_id, cls.device_id == device_id,
                                        cls.guided_meta_id == guided_meta_id).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise
