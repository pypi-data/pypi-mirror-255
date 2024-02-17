from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, InternalError, IntegrityError, \
    DataError, DoesNotExist

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_details import PackDetails
logger = settings.logger


class PackUserMap(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    assigned_to = IntegerField(null=True, default=None)  # Pack is assigned to the user for filling manually
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_id', 'assigned_to'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_user_map"

    @classmethod
    def db_delete_data_pack_user_map_by_pack_ids(cls, pack_ids) -> bool:
        """
        delete pack user map data by pack ids
        @param pack_ids:
        """
        try:
            status = PackUserMap.delete().where(PackUserMap.pack_id.in_(pack_ids)).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_insert_pack_user_map_data(cls, pack_id, user_id, date, created_by=None) -> bool:
        """
        delete pack user map data by pack ids
        @param pack_id:
        @param user_id:
        @param date:
        @return:
        @param pack_ids:
        """
        try:
            if user_id:
                created_by = user_id
            status = PackUserMap.insert(pack_id=pack_id, assigned_to=user_id,
                                        created_by=created_by, modified_by=created_by,
                                        created_date=date,
                                        modified_date=date).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_check_pack_user_map_data(cls, pack_id: int):
        try:
            pack_query = PackUserMap.select(PackUserMap.pack_id).dicts().where(PackUserMap.pack_id == pack_id)
            if pack_query.count() > 0:
                return True

            return False
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            logger.error("Function: db_check_pack_user_map_data -- {}".format(e))
            return False
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            logger.error("Function: db_check_pack_user_map_data -- {}".format(e))
            raise e

    @classmethod
    def db_suggested_user_id_for_manual_packs_from_previous_record(cls, user_id):
        try:
            suggested_user_id = None
            suggested_user_query = PackUserMap.select(PackUserMap.assigned_to).dicts() \
                .join(PackDetails, on=PackDetails.id == PackUserMap.pack_id) \
                .where(PackUserMap.modified_by == user_id,
                       PackDetails.pack_status << [settings.DONE_PACK_STATUS, settings.PARTIALLY_FILLED_BY_ROBOT]) \
                .order_by(PackUserMap.id.desc()).limit(1)
            for record in suggested_user_query:
                suggested_user_id = record['assigned_to']
            return suggested_user_id
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            logger.error("Function: suggested_user_id_for_manual_packs_from_previous_record -- {}".format(e))
            return None
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            logger.error("Function: suggested_user_id_for_manual_packs_from_previous_record -- {}".format(e))
            raise e