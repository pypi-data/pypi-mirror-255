import logging

from peewee import IntegrityError, InternalError

from dosepack.error_handling.error_handler import create_response, error
from src.model.model_reason_master import ReasonMaster
logger = logging.getLogger("root")


def db_get_reasons_dao(reason_group):
    try:
        return ReasonMaster.db_get_reasons(reason_group)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)