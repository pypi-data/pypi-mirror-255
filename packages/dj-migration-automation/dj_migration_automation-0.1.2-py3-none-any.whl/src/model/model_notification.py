from peewee import PrimaryKeyField, CharField, IntegerField, DateTimeField, DoesNotExist, InternalError, IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class Notification(BaseModel):
    id = PrimaryKeyField()
    message = CharField(null=True, default=None, max_length=500)
    user_id = IntegerField()
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    read_date = DateTimeField(null=True, default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "notifications"

    @classmethod
    def db_check_notification_sent_or_not(cls, message):
        try:
            status = Notification.get(Notification.message ** '%{}%'.format(message)).id
            if status:
                return True
            else:
                return False
        except DoesNotExist:
            return False
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
