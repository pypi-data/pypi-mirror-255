from peewee import PrimaryKeyField, IntegerField, DateTimeField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
logger = settings.logger


class CanisterParameters(BaseModel):
    """
    It contains the data related to canister parameters and timers to run the canister motors.
    """
    id = PrimaryKeyField()
    speed = IntegerField(null=True)  # drum rotate speed
    wait_timeout = IntegerField(null=True)  # sensor wait timeout  # in ms
    cw_timeout = IntegerField(null=True)  # clockwise # in ms
    ccw_timeout = IntegerField(null=True)  # counterclockwise # in ms
    drop_timeout = IntegerField(null=True)  # total pill drop timeout # # in ms
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)
    pill_wait_time = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_parameters'

    @classmethod
    def db_get_or_create(cls, user_id, speed=None, wait_timeout=None,
                         cw_timeout=None, ccw_timeout=None,
                         drop_timeout=None, pill_wait_time=None):
        """

        @param user_id:
        @param speed:
        @param wait_timeout:
        @param cw_timeout:
        @param ccw_timeout:
        @param drop_timeout:
        @param pill_wait_time:
        :return:
        """
        record, created = cls.get_or_create(
            speed=speed, wait_timeout=wait_timeout,
            cw_timeout=cw_timeout, ccw_timeout=ccw_timeout,
            drop_timeout=drop_timeout, pill_wait_time=pill_wait_time,
            defaults={
                'created_by': user_id,
                'modified_by': user_id,
            }
        )
        return record, created
