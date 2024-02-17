import settings
from peewee import PrimaryKeyField, CharField, BooleanField, DateTimeField, \
    InternalError, IntegrityError
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
logger = settings.logger


class ConsumableTypeMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)
    description = CharField(max_length=255, null=True)
    active = BooleanField(default=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "consumable_type_master"

    type_data = {
        'Blister Pack': 1,
        'Label': 2,
        'Vial': 3
    }

    @classmethod
    def db_get_consumables_types(cls):
        """
        Returns all consumable types
        :return: list
        """
        consumable_types = list()
        try:
            for record in ConsumableTypeMaster.select(ConsumableTypeMaster.name,
                                                      ConsumableTypeMaster.id,
                                                      ConsumableTypeMaster.description).dicts():
                consumable_types.append(record)

            return consumable_types
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

