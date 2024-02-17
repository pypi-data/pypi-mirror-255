from peewee import PrimaryKeyField, ForeignKeyField, DateTimeField, IntegerField, InternalError, IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_small_canister_stick import SmallCanisterStick
from src.model.model_canister_drum import CanisterDrum

logger = settings.logger


class CanisterStick(BaseModel):
    """
    It contains the data related to small and big stick combination
    """
    id = PrimaryKeyField()
    big_canister_stick_id = ForeignKeyField(BigCanisterStick, related_name='big_canister_stick', null=True)
    small_canister_stick_id = ForeignKeyField(SmallCanisterStick, related_name='small_canister_stick', null=True)
    canister_drum_id = ForeignKeyField(CanisterDrum, related_name='canister_drum', null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_stick'

    @classmethod
    def get_canister_stick_by_big_stick_small_stick_canister_drum(cls, big_canister_stick_id: int,
                                                                  small_canister_stick_id: int, canister_drum_id: int) -> int:
        """
        Function to get canister stick id for given big_canister_stick_id, small_canister_stick_id, canister_drum_id.
        :param big_canister_stick_id:
        :param small_canister_stick_id:
        :param canister_drum_id
        :return canister_stick_id:
        """
        logger.info("In get_canister_stick_by_big_stick_small_stick_canister_drum")
        canister_stick_id: int = 0

        try:
            query = CanisterStick.select(CanisterStick.id.alias('canister_stick_id')).dicts() \
                .where((CanisterStick.big_canister_stick_id == big_canister_stick_id) and
                       (CanisterStick.small_canister_stick_id == small_canister_stick_id) and
                       (CanisterStick.canister_drum_id == canister_drum_id))
            if query:
                for record in query:
                    canister_stick_id = record['canister_stick_id']
            return canister_stick_id
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_canister_stick_id_by_big_stick_small_stick_dimension(cls, big_stick_id_list, small_stick_length):
        """
        Get canister stick id by big stick ids and small stick length
        :param big_stick_id_list:
        :param small_stick_length:
        :return:
        """
        canister_stick_id_list = list()
        big_stick_serial_number_list = list()
        small_stick_serial_number_list = list()

        try:
            if big_stick_id_list:
                query = CanisterStick.select(CanisterStick.id.alias("Canister_Stick_Id"), BigCanisterStick.serial_number
                                             .alias("Big_Stick_Serial_Number"), SmallCanisterStick.length.alias
                                             ("Small_Stick_Serial_Number")).dicts().join(SmallCanisterStick,
                                                                                         on=SmallCanisterStick.id ==
                                                                                            CanisterStick.small_canister_stick_id) \
                    .join(BigCanisterStick, on=BigCanisterStick.id == CanisterStick.big_canister_stick_id) \
                    .where(CanisterStick.big_canister_stick_id << big_stick_id_list,
                           SmallCanisterStick.length == small_stick_length)

                for record in query:
                    canister_stick_id_list.append(record["Canister_Stick_Id"])
                    big_stick_serial_number_list.append(record["Big_Stick_Serial_Number"])
                    small_stick_serial_number_list.append(record["Small_Stick_Serial_Number"])
                return canister_stick_id_list, big_stick_serial_number_list, small_stick_serial_number_list
            else:
                return canister_stick_id_list, big_stick_serial_number_list, small_stick_serial_number_list
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise
