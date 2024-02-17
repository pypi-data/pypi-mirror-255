from peewee import BooleanField
from peewee import ForeignKeyField, PrimaryKeyField, IntegerField, InternalError, IntegrityError, DataError
import settings
from dosepack.base_model.base_model import BaseModel
from src import constants
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_stick import CanisterStick
from src.model.model_code_master import CodeMaster

logger = settings.logger


class TempRecommendedStickCanisterData(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    canister_stick_id = ForeignKeyField(CanisterStick)
    status = ForeignKeyField(CodeMaster)
    order_no = IntegerField()
    user_id = IntegerField()
    recommended_stick = BooleanField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "temp_recommnded_stick_canister"

    @classmethod
    def db_update_tested_stick_canister_status(cls, canister_id, canister_stick_id, tested_canister_status, user_id):
        """
        update canister status (if pass(206) then update status(=pass) of all other canister of same stick)
        @param user_id:
        @param tested_canister_status:
        @param canister_id:
        @param canister_stick_id:
        """
        try:
            if tested_canister_status == constants.CANISTER_TESTING_PASS:
                status = cls.update(status=tested_canister_status).where(cls.canister_stick_id == canister_stick_id, cls.status == constants.CANISTER_TESTING_PENDING, cls.user_id == user_id).execute()
            else:
                status = cls.update(status=tested_canister_status).where(cls.canister_id == canister_id,
                                                                         cls.user_id == user_id).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_recom_stick_canister_data(cls):
        """
        Deletes canisters data from table
        :return:
        """
        try:
            query = cls.select().dicts().where(cls.recommended_stick == True)
            return query
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_delete_canister(cls, user_id):
        """
        Delete canisters data from table
        :return:
        """
        try:
            return cls.delete().where(cls.user_id == user_id).execute()
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def check_if_canister_data_exit_for_user(cls, user_id):
        """
        check if record is exist in table for given user_id
        :return:
        """
        try:
            existence = cls.select(cls.id).where(cls.user_id == user_id).exists()
            return existence
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_insert_canister_data(cls, canister_list):
        """
        insert canisters data to table
        :return:
        """
        try:
            status = cls.insert_many(canister_list).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_order_no(cls, order_no, canister_list):
        """
        update order no
        :return:
        """
        try:
            status = cls.update(order_no=order_no).where(
                    cls.canister_id << canister_list).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise
