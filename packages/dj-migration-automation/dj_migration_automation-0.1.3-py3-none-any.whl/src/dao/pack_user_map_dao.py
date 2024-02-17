from peewee import JOIN_LEFT_OUTER, DataError

import settings
from dosepack.utilities.utils import log_args_and_response
from pymysql import InternalError, IntegrityError
from src.model.model_pack_details import PackDetails
from src.model.model_pack_user_map import PackUserMap
logger = settings.logger


def get_pack_user_details(pack_list):
    try:
        query = PackDetails.select(PackDetails.id, PackUserMap.assigned_to.alias('assigned_from')).dicts() \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id) \
            .where(PackDetails.id << pack_list)
        return query
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


def update_or_create_pack_user_map_dao(create_dict, update_dict):
    try:
        PackUserMap.db_update_or_create(create_dict, update_dict)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def suggested_user_id_for_manual_packs_from_previous_record_dao(user_id):
    """
    Returns the last assigned user of manual packs.
    @return:
    user_id
    """
    try:
        suggested_user = PackUserMap.db_suggested_user_id_for_manual_packs_from_previous_record(user_id)
        return suggested_user
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in suggested_user_id_for_manual_packs {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in suggested_user_id_for_manual_packs {}".format(e))
        raise e


