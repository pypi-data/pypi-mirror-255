import functools
import operator
from src import constants
from peewee import BooleanField, \
    ForeignKeyField, PrimaryKeyField, DecimalField, IntegrityError, InternalError
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_drug_master import DrugMaster
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_slot_header import SlotHeader
# from src.dao.pack_drug_dao import populate_pack_drug_tracker
from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class SlotDetails(BaseModel):
    id = PrimaryKeyField()
    slot_id = ForeignKeyField(SlotHeader)
    pack_rx_id = ForeignKeyField(PackRxLink)
    quantity = DecimalField(decimal_places=2, max_digits=7)
    is_manual = BooleanField()
    drug_id = ForeignKeyField(DrugMaster)
    original_drug_id = ForeignKeyField(DrugMaster, related_name="original_drug_id_id")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_details"

    @classmethod
    def db_update_slot_details_by_slot_id(cls, update_dict: dict, slot_details_id: int) -> bool:
        """
        update slot details data by slot details id
        :return:
        """
        try:
            status = SlotDetails.update(**update_dict).where(SlotDetails.id == slot_details_id).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_drug_details_by_old_drug(cls, drug_case_sequence, clauses):
        try:
            logger.debug("Drug Case Sequence: {}".format(drug_case_sequence))
            logger.debug("Clauses: {}".format(clauses))
            update_slot_drug_status = SlotDetails.update(drug_id=drug_case_sequence) \
                .where(functools.reduce(operator.and_, clauses)).execute()
            logger.debug("Drug Mapping Update Status: {}".format(update_slot_drug_status))

            return update_slot_drug_status
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_drug_id_based_on_slot_id(cls, slot_id):
        try:
            logger.info("Inside db_get_drug_id_based_on_slot_id with slot_id {}".format(slot_id))
            query = SlotDetails.select(SlotDetails.drug_id).where(SlotDetails.id == slot_id).dicts().get()
            return query["drug_id"]
        except Exception as e:
            logger.error("error in db_get_drug_id_based_on_slot_id {}".format(e))
            raise e

    @classmethod
    def db_update_slot_details_by_multiple_slot_id(cls, update_dict: dict, slot_details_ids: list) -> bool:
        """
        update slot details data by multiple slot details id
        :return:
        """
        try:
            logger.info("Inside db_update_slot_details_by_multiple_slot_id with update_dicts {}, slot_ids {}".format(update_dict, slot_details_ids))
            status = SlotDetails.update(**update_dict).where(SlotDetails.id << slot_details_ids).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e
