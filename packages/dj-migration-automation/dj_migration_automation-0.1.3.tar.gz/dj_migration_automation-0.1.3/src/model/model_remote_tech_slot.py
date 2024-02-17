from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_pvs_slot import PVSSlot


class RemoteTechSlot(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_id = ForeignKeyField(PVSSlot, related_name='remotetechslot_pvs_slot_id')
    remote_tech_id = IntegerField(null=True)
    verification_status = ForeignKeyField(CodeMaster, related_name='remotetechslot_verification_status')
    start_time = DateTimeField(default=get_current_date_time)
    end_time = DateTimeField(default=get_current_date_time)
    is_updated = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'remote_tech_slot'

    @classmethod
    def get_remote_tech_slot(self, user_id, status):
        """
        Function to get records from remote_tech_slot
        @return:
        """
        try:
            rts_query = RemoteTechSlot.select(RemoteTechSlot.id).dicts() \
                .where(RemoteTechSlot.is_updated == False,
                       RemoteTechSlot.verification_status << status,
                       RemoteTechSlot.remote_tech_id << user_id) \
                .order_by(RemoteTechSlot.id.desc())

            return rts_query

        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            settings.logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_remote_tech_id(cls, assign_to, rts_id_to_update):
        """
        Function to update remote_tech_id in given slots
        @param assign_to:
        @return:
        """
        try:
            update_query = RemoteTechSlot.update(remote_tech_id=assign_to) \
                .where(RemoteTechSlot.id << (rts_id_to_update)).execute()
            return update_query
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            settings.logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_status_in_remote_tech_slot(cls, remote_tech_ids):
        try:
            status = RemoteTechSlot.update(is_updated=False,verification_status=constants.RTS_USER_SKIPPED) \
                                         .where(RemoteTechSlot.id << remote_tech_ids).execute()

            return status
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            settings.logger.error(e, exc_info=True)
            raise e