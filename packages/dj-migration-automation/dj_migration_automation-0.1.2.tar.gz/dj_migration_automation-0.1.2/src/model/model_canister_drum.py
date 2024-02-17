from peewee import PrimaryKeyField, IntegerField, DateTimeField, CharField, DecimalField, \
    IntegrityError, InternalError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
logger = settings.logger


class CanisterDrum(BaseModel):
    id = PrimaryKeyField()
    serial_number = CharField(unique=True, max_length=10, null=False)
    width = DecimalField(decimal_places=3, max_digits=6, null=False)
    depth = DecimalField(decimal_places=3, max_digits=6, null=False)
    length = DecimalField(decimal_places=3, max_digits=6, null=False)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(null=False)
    modified_by = IntegerField(null=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drum"

    @classmethod
    def get_canister_drum_id_by_drum_serial_number(cls, drum_serial_number: str) -> int:
        """
        Function to get canister_drum_id for given drum_serial_number.
        :param drum_serial_number:
        :return canister_drum_id:
        """
        logger.info("In get_canister_drum_id_by_drum_serial_number")
        canister_drum_id: int = 0

        try:
            query = CanisterDrum.select(CanisterDrum.id.alias('canister_drum_id')).dicts() \
                .where(CanisterDrum.serial_number == drum_serial_number)
            for record in query:
                canister_drum_id = record['canister_drum_id']
            return canister_drum_id
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
