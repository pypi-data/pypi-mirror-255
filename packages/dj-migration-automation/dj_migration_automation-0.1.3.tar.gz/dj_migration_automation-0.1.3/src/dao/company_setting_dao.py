from peewee import InternalError, IntegrityError, DataError

import settings
from dosepack.utilities.utils import log_args_and_response
from src.model.model_company_setting import CompanySetting

logger = settings.logger


@log_args_and_response
def db_get_template_split_settings_dao(company_id, max_count_threshold=None):
    try:
        return CompanySetting.db_get_template_split_settings(company_id=company_id, max_count_threshold=max_count_threshold)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_get_template_split_settings_dao {}".format(e))
        raise e


@log_args_and_response
def get_ips_communication_settings_dao(company_id):
    try:
        return CompanySetting.db_get_ips_communication_settings(company_id=company_id)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_ips_communication_settings_dao {}".format(e))
        raise e


@log_args_and_response
def db_get_elite_token():
    """
    Returns required token for epbm communication
    :return: dict
    """
    setting_names = settings.EPBM_COMMUNICATION_SETTINGS
    try:
        query = CompanySetting.select(
            CompanySetting.value
        ).where(CompanySetting.name == setting_names)
        value = query.scalar()
        return value

    except (InternalError, IntegrityError) as e:
        logger.error(f"error in db_get_token is {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"error in db_get_token is {e}", exc_info=True)
        raise


@log_args_and_response
def db_update_elite_token(token):
    """
    stores required token for epbm communication
    :return: dict
    """
    try:
        query = CompanySetting.update(value=token).where(CompanySetting.name == settings.EPBM_COMMUNICATION_SETTINGS)
        return query.execute()

    except (InternalError, IntegrityError) as e:
        logger.error(f"error in db_update_elite_token is {e}", exc_info=True)
        raise
