from peewee import PrimaryKeyField, DateTimeField, ForeignKeyField, SmallIntegerField, InternalError, IntegrityError
from sqlalchemy import case

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_tx_meta import CanisterTxMeta
from src.model.model_code_master import CodeMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_location_master import LocationMaster

logger = settings.logger


class CanisterTransfers(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    dest_device_id = ForeignKeyField(DeviceMaster, null=True)
    dest_location_number = SmallIntegerField(null=True)
    dest_quadrant = SmallIntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    trolley_loc_id = ForeignKeyField(LocationMaster, null=True)
    to_ct_meta_id = ForeignKeyField(CanisterTxMeta, null=True, related_name="to_cart_meta_id")
    from_ct_meta_id = ForeignKeyField(CanisterTxMeta, null=True, related_name="from_cart_meta_id")
    transfer_status = ForeignKeyField(CodeMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfers"

    @classmethod
    def db_update_canister_tx_status(cls, batch_id: int, canister_id_list: list, status: int):
        """
        Function to update transfer status in canister transfer
        @param batch_id:
        @param canister_id_list:
        @param status:
        @return:
        """
        logger.info("Input of db_update_canister_tx_status {}, {}, {}".format(batch_id, canister_id_list, status))
        try:
            status_update = cls.update(transfer_status=status) \
                .where(cls.batch_id == batch_id,
                       cls.canister_id << canister_id_list).execute()

            logger.info("Output of db_update_canister_tx_status {}".format(status_update))
            return True

        except (InternalError, IntegrityError) as e:
            logger.error("Error in db_update_canister_tx_status {}".format(e))
            raise

    @classmethod
    def db_replace_canister(cls, batch_id: int, canister_id: int, alt_canister_id: int) -> bool:
        """
        Replace Canister for given batch_id.
        alt_canister_id will be replaced for canister_id
        :param batch_id:
        :param canister_id:
        :param alt_canister_id:
        :return:
        """
        try:
            query = CanisterTransfers.update(canister_id=alt_canister_id) \
                .where(CanisterTransfers.batch_id == batch_id,
                       CanisterTransfers.canister_id == canister_id)
            status = query.execute()
            # logger.info('Canister Transfer Update Status: {} for canister_id: {} '
            #             'and alt_canister_id: {}'.format(
            #     status, canister_id, alt_canister_id
            # ))
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_replace_canister_list(cls, batch_id, canister_list=None, alt_canister_list=None, case_sequence=None):
        """
        Replaces canister_list to it's respective alt_canister_list
        :param batch_id:
        :param canister_list:
        :param alt_canister_list:
        :param case_sequence:
        :return:
        """
        try:
            if not case_sequence:
                if len(canister_list) != len(alt_canister_list):
                    raise ValueError('Length of canister_list and alt_canister_list should be same ')
                new_seq_tuple = list(tuple(zip(canister_list, alt_canister_list)))
                case_sequence = case(CanisterTransfers.canister_id, new_seq_tuple)

            status = CanisterTransfers.update(canister_id=case_sequence) \
                .where(CanisterTransfers.batch_id == batch_id, CanisterTransfers.canister_id << canister_list).execute()
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_remove_canister(cls, batch_id: int, canister_ids: list) -> bool:
        """
        Removes unwanted canisters
        :param batch_id:
        :param canister_ids:
        :return:
        """
        try:
            status = CanisterTransfers.delete() \
                .where(CanisterTransfers.canister_id << canister_ids, CanisterTransfers.batch_id == batch_id).execute()
            logger.info('db_remove_canister_status: {} for canister_ids: {} and batch_id: {}'.format(status,
                                                                                                     canister_ids,
                                                                                                     batch_id))
            return status

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_canister_transfers(cls, update_dict: dict, canister_id_list: list, batch_id:int):
        """
        Function to update canister transfer
        @param update_dict:
        @param canister_id_list:
        @return:
        """
        try:
            status = CanisterTransfers.update(**update_dict).where(
                CanisterTransfers.canister_id << canister_id_list,
                CanisterTransfers.batch_id == batch_id).execute()
            return status

        except (InternalError, IntegrityError) as e:
            logger.error("Error in db_update_canister_tx {}".format(e))
            raise

