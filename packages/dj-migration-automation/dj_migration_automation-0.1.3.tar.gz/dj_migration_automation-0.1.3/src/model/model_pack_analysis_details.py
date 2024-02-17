from peewee import PrimaryKeyField, ForeignKeyField, SmallIntegerField, IntegrityError, \
    InternalError, fn

import settings
from dosepack.base_model.base_model import BaseModel
from src import constants
from src.model.model_slot_details import SlotDetails

from src.model.model_canister_master import CanisterMaster
from src.model.model_configuration_master import ConfigurationMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_code_master import CodeMaster

logger = settings.logger


class PackAnalysisDetails(BaseModel):
    id = PrimaryKeyField()
    analysis_id = ForeignKeyField(PackAnalysis)
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    canister_id = ForeignKeyField(CanisterMaster, null=True)
    # canister_number = SmallIntegerField(null=True)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    location_number = SmallIntegerField(null=True)
    # drug_id = ForeignKeyField(DrugMaster)
    slot_id = ForeignKeyField(SlotDetails)  # combination of drug and slot
    quadrant = SmallIntegerField(null=True)
    drop_number = SmallIntegerField(null=True)
    config_id = ForeignKeyField(ConfigurationMaster, null=True)
    status = ForeignKeyField(CodeMaster, default=constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_analysis_details"

    @classmethod
    def db_update_analysis_by_canister_ids(cls, update_dict: dict, canister_ids: list, analysis_ids: list) -> bool:
        try:
            status = PackAnalysisDetails.update(**update_dict) \
                .where(PackAnalysisDetails.canister_id << canister_ids,
                       PackAnalysisDetails.analysis_id << analysis_ids).execute()
            return status
        except (InternalError, IntegrityError) as e:
            raise e

    @classmethod
    def update_manual_canister_location_v2(cls, analysis_details_ids: list) -> bool:
        """
        updates pack analysis in case canister is not placed at desired location
        :param analysis_details_ids:
        :return:
        """
        try:
            if analysis_details_ids:
                # status = PackAnalysisDetails.update(quadrant=None,
                #                                     canister_id=None,
                #                                     drop_number=None,
                #                                     config_id=None,
                #                                     location_number=None) \
                #     .where(PackAnalysisDetails.id << analysis_details_ids).execute()

                status = PackAnalysisDetails.update(status=constants.REPLENISH_CANISTER_TRANSFER_SKIPPED) \
                            .where(PackAnalysisDetails.id << analysis_details_ids).execute()
                # settings.logger.info('Updated rows count for pack_analysis_details_manual {}'.format(status))
                settings.logger.info(
                    'In update_manual_canister_location_v2, Updated rows count for pack_analysis_details_manual , status updated as skipped due to manual{}'.format(
                        status))
                return status
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_pack_analysis_details_by_analysis_id(cls, update_dict: dict, analysis_id: list, slot_id: list, device_id: int = None) -> bool:
        try:
            if device_id:
                status = PackAnalysisDetails.update(**update_dict) \
                    .where(PackAnalysisDetails.analysis_id << analysis_id,
                           PackAnalysisDetails.slot_id << slot_id,
                           PackAnalysisDetails.device_id == device_id) \
                    .execute()
            else:
                status = PackAnalysisDetails.update(**update_dict) \
                    .where(PackAnalysisDetails.analysis_id << analysis_id,
                           PackAnalysisDetails.slot_id << slot_id) \
                    .execute()
            return status
        except (InternalError, IntegrityError) as e:
            raise e
        except Exception as e:
            logger.error("error in db_update_pack_analysis_details_by_analysis_id {}".format(e))
            raise e

    @classmethod
    def db_get_canister_list_from_pack_analysis_ids(cls, analysis_ids):
        try:
            if analysis_ids:
                canister_list = list()
                query = PackAnalysisDetails.select(fn.DISTINCT(PackAnalysisDetails.canister_id).alias('canister_id')).dicts()   \
                                           .where(PackAnalysisDetails.id << analysis_ids)

                for record in query:
                    canister_list.append(record['canister_id'])
                return canister_list
        except (InternalError, IntegrityError) as e:
            raise e
        except Exception as e:
            logger.error("error in db_get_canister_list_from_pack_analysis_ids {}".format(e))
            raise e

    @classmethod
    def db_get_slot_id_from_pack_analysis_ids(cls, analysis_ids):
        try:
            logger.info("In db_get_slot_id_from_pack_analysis_ids with analysis_ids: {}".format(analysis_ids))
            slot_id_list: list = list()
            if analysis_ids:

                query = PackAnalysisDetails.select(fn.DISTINCT(PackAnalysisDetails.slot_id).alias('slot_id')).dicts()\
                    .where(PackAnalysisDetails.analysis_id << analysis_ids)

                for record in query:
                    slot_id_list.append(record['slot_id'])

                return slot_id_list
            else:
                return slot_id_list
        except (InternalError, IntegrityError) as e:
            raise e
        except Exception as e:
            logger.error("Error in db_get_slot_id_from_pack_analysis_ids {}".format(e))
            raise e
