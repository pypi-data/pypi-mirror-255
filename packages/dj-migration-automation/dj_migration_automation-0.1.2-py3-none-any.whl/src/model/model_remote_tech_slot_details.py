from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import BaseModel
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_unique_drug import UniqueDrug
from src.model.model_pvs_slot_details import PVSSlotDetails
from src.model.model_remote_tech_slot import RemoteTechSlot


class RemoteTechSlotDetails(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_details_id = ForeignKeyField(PVSSlotDetails, related_name='remotetechslotdetails_pvs_slot_details_id')
    remote_tech_slot_id = ForeignKeyField(RemoteTechSlot, related_name='remotetechslotdetails_remote_tech_slot_id')
    label_drug_id = ForeignKeyField(UniqueDrug, null=True)
    mapped_status = ForeignKeyField(CodeMaster, default=constants.SKIPPED_AND_SURE_MAPPED)
    linked_qty = DecimalField(decimal_places=2, max_digits=4, default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'remote_tech_slot_details'

    @classmethod
    def update_status_in_remote_tech_slot_details(cls, remote_tech_slot_details_ids):
        try:
            status = RemoteTechSlotDetails.update(mapped_status=constants.SKIPPED_AND_DELETED) \
                                            .where(RemoteTechSlotDetails.id << remote_tech_slot_details_ids).execute()
            return status
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            settings.logger.error(e, exc_info=True)
            raise e