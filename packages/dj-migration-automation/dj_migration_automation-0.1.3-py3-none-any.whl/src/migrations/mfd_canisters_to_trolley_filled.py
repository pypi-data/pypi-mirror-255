import logging

from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, CharField, SmallIntegerField, BooleanField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_mfd_canister_master import MfdCanisterMaster

logger = logging.getLogger("root")


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


class ContainerMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "container_master"


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    container_id = ForeignKeyField(ContainerMaster, related_name='location_container_id')
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)
    is_disabled = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


def update_mfd_canisters(batch_id: int) -> bool:
    """
    This function updates the mfd canisters for the given status to filled
    """

    update_status_list = [constants.MFD_CANISTER_IN_PROGRESS_STATUS]

    query = MfdAnalysis.select(MfdAnalysis.id,
                               MfdAnalysis.mfd_canister_id,
                               MfdAnalysis.trolley_location_id,
                               LocationMaster.device_id).dicts() \
        .join(LocationMaster, on=MfdAnalysis.trolley_location_id == LocationMaster.id) \
        .where((MfdAnalysis.batch_id == batch_id), (MfdAnalysis.status_id << update_status_list)) \
        .order_by(MfdAnalysis.id)
    trolley_id_list = []
    device_id_list = []
    logger.debug(trolley_id_list)
    for record in query:
        device_id_list.append(record["device_id"])
        if record["device_id"] == device_id_list[len(device_id_list) - 1] or record["device_id"] not in trolley_id_list:
            trolley_id_list.append(record["device_id"])
            mfd_analysis_status = MfdAnalysis.update(status_id=constants.MFD_CANISTER_FILLED_STATUS).where(
                MfdAnalysis.id == record["id"]).execute()
            mfd_analysis_details_status = MfdAnalysisDetails.update(status_id=constants.MFD_DRUG_FILLED_STATUS).where(
                MfdAnalysisDetails.analysis_id == record["id"]).execute()
            mfd_canister_master_status = MfdCanisterMaster.update(location_id=record["trolley_location_id"]).where(
                MfdCanisterMaster.id == record["mfd_canister_id"]).execute()
    print("Transfer completed for batch_id:{}".format(batch_id))
    return True


if __name__ == "__main__":
    init_db(db, 'database_migration')
    update_mfd_canisters(batch_id=745)

