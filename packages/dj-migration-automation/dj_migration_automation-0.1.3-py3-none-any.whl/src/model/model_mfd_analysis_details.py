from peewee import (IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, DecimalField, IntegrityError,
                    InternalError, DoesNotExist, fn)
from playhouse.shortcuts import case

import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
from src.model.model_code_master import CodeMaster
from src.model.model_configuration_master import ConfigurationMaster
from src.model.model_mfd_analysis import (MfdAnalysis)
from src.model.model_slot_details import SlotDetails

logger = settings.logger


class MfdAnalysisDetails(BaseModel):
    id = PrimaryKeyField()
    analysis_id = ForeignKeyField(MfdAnalysis)
    mfd_can_slot_no = IntegerField()
    drop_number = IntegerField()
    config_id = ForeignKeyField(ConfigurationMaster)
    quantity = DecimalField(decimal_places=2, max_digits=4)
    status_id = ForeignKeyField(CodeMaster)
    slot_id = ForeignKeyField(SlotDetails)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_analysis_details"

    @classmethod
    def db_update_drug_status(cls, analysis_details_ids: list, status: int) -> int:
        """
        updates drug status
        :param analysis_details_ids: list
        :param status: int
        :return: int
        """
        try:
            logger.debug("In db_update_drug_status")
            update_status = MfdAnalysisDetails.update(status_id=status) \
                .where(MfdAnalysisDetails.id << analysis_details_ids).execute()
            logger.info("mfd_can_updated_with: " + str(status) + ' status for analysis_details_ids: ' +
                        str(analysis_details_ids))
            return update_status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_status_based_drug(cls, analysis_details_ids: list, status_ids: list) -> list:
        """
        filters analysis_details_id with specific status_list
        :param analysis_details_ids: list
        :param status_ids: list
        :return: list
        """
        try:
            mfd_drug_query = MfdAnalysisDetails.select().dicts() \
                .where(MfdAnalysisDetails.id << analysis_details_ids,
                       MfdAnalysisDetails.status_id << status_ids)

            mfd_analysis_ids = [record['id'] for record in mfd_drug_query]
            return mfd_analysis_ids
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_get_status_based_on_slot_id(cls, slot_id: int):
        try:
            result = MfdAnalysisDetails.select(fn.GROUP_CONCAT(MfdAnalysisDetails.status_id)).dicts()\
                .where(MfdAnalysisDetails.slot_id == slot_id).scalar()

            status_ids = list(map(int, result.split(",")))

            return status_ids
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e
        except Exception as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_slot_id_from_pack_analysis_ids(cls, mfd_analysis_ids):
        try:
            logger.info("In db_get_slot_id_from_pack_analysis_ids with mfd_analysis_ids: {}".format(mfd_analysis_ids))
            slot_id_list: list = list()
            if mfd_analysis_ids:

                query = MfdAnalysisDetails.select(fn.DISTINCT(MfdAnalysisDetails.slot_id).alias('slot_id')).dicts() \
                    .where(MfdAnalysisDetails.analysis_id << mfd_analysis_ids)

                for record in query:
                    slot_id_list.append(record['slot_id'])

                return slot_id_list
            else:
                return slot_id_list
        except (InternalError, IntegrityError) as e:
            raise e
        except Exception as e:
            logger.error("error in db_get_slot_id_from_pack_analysis_ids {}".format(e))
            raise e
