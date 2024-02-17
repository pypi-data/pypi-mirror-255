from peewee import PrimaryKeyField, ForeignKeyField, DateTimeField, IntegerField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_small_canister_stick import SmallCanisterStick
from src.model.model_canister_parameters import CanisterParameters


class SmallStickCanisterParameters(BaseModel):
    """
    Mapping for small stick canister parameter
    """
    id = PrimaryKeyField()
    small_stick_id = ForeignKeyField(SmallCanisterStick, unique=True)
    canister_parameter_id = ForeignKeyField(CanisterParameters)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'small_stick_canister_parameters'

    @classmethod
    def db_create(cls, small_stick_id, canister_parameter_id, user_id):
        """
        creates entry in db for small_stick_id and canister_parameter_id
        :param int small_stick_id:
        :param int canister_parameter_id:
        :param int user_id:
        :return: peewee.Model
        """
        return cls.create(
            small_stick_id=small_stick_id,
            canister_parameter_id=canister_parameter_id,
            created_by=user_id,
            modified_by=user_id
        )

    @classmethod
    def db_update(cls, record_id, canister_parameter_id, user_id):
        """
        updates entry in db for record_id with canister_parameter_id
        :param int record_id:
        :param int canister_parameter_id:
        :param int user_id:
        :return: peewee.Model
        """
        return cls.update(
            canister_parameter_id=canister_parameter_id,
            created_by=user_id,
            modified_by=user_id,
            modified_date=get_current_date_time()
        ).where(cls.id == record_id).execute()
