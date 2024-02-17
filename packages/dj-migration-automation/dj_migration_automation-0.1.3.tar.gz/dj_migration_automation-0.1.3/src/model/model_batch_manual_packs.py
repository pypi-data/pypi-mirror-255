from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, IntegrityError, InternalError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

from src.model.model_batch_master import BatchMaster
from src.model.model_pack_details import PackDetails


logger = settings.logger


class BatchManualPacks(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    batch_id = ForeignKeyField(BatchMaster)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_manual_packs"

    @classmethod
    def db_get_create_manual_packs(cls, pack_id_list, pending_manual_packs, batch_id, user_id):
        """

        @param pack_id_list:
        @param pending_manual_packs:
        @param batch_id:
        @param user_id:
        @return:
        """
        try:
            packs_to_remove = list(set(pending_manual_packs) - set(pack_id_list))
            packs_to_add = list(set(pack_id_list) - set(pending_manual_packs))

            if len(packs_to_remove) > 0:
                cls.remove_batch_manual_pack(packs_to_remove, user_id)

            if len(packs_to_add) > 0:
                batch_pack_data = [{'pack_id': pack_id, 'created_by': user_id, 'batch_id': batch_id} for pack_id in
                                   packs_to_add]
                cls.insert_many(batch_pack_data).execute()
                logger.info(batch_pack_data)
            return True

        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_add_batch_manual_packs(cls, pack_ids, batch_id, user_id):
        """
        If packs are fully manual at the time of importing batch they are added to BatchManualPacks
        :param pack_ids: list of packs
        :param batch_id:
        :param user_id:
        :return:
        """
        batch_pack_data = [{'pack_id': pack_id, 'created_by': user_id, 'batch_id': batch_id} for pack_id in pack_ids]
        try:
            pack_added = BatchManualPacks.insert_many(batch_pack_data).execute()

        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

        return pack_added

    @classmethod
    def remove_batch_manual_pack(cls, pack_list, user_id):
        """
        If packs are not added for pack fill workflow then they are removed from BatchManualPacks
        :param pack_list: list of packs
        :param user_id:
        :return:
        """

        try:
            pack_removed = BatchManualPacks.delete().where(BatchManualPacks.pack_id << pack_list).execute()

        except IntegrityError as e:
            raise InternalError(e)
        except InternalError as e:
            raise InternalError(e)

        return pack_removed

    @classmethod
    def db_verify_manual_packs_by_batch_id(cls, batch_id):
        pack_list = []
        try:
            # query = BatchManualPacks.select(BatchManualPacks.pack_id).where(BatchManualPacks.batch_id == batch_id)
            # .dicts()
            query = BatchManualPacks.select(BatchManualPacks.pack_id) \
                .where(BatchManualPacks.batch_id == batch_id).dicts()

            for record in query:
                pack_list.append(record['pack_id'])
            return pack_list

        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e
