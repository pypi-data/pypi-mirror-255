from peewee import InternalError, IntegrityError

import settings
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate
from src.dao.pack_dao import get_pharmacy_data_for_system_id, add_pharmacy_data_dao

logger = settings.logger

@validate(required_fields=["system_id"])
@log_args_and_response
def get_pharmacy(search_filters):
    """
    Returns pharmacy data given system id

    :param search_filters: dict
    :return: json
    """
    system_id = search_filters["system_id"]
    logger.debug("Inside get_pharmacy")

    try:
        pharmacy_data = next(get_pharmacy_data_for_system_id(system_id=system_id))

        logger.info("In get_pharmacy, pharmacy_data : {}".format(pharmacy_data))

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except StopIteration:
        logger.error("In get_pharmacy, No pharmacy found for system id: " + str(system_id))
        return error(1004)

    if not pharmacy_data:
        return error(2001)

    return create_response(pharmacy_data)


@validate(required_fields=["store_name", "store_address", "store_phone",
                           "user_id", "system_id"])
@log_args_and_response
def add_pharmacy(pharmacy_info):
    """
    Creates pharmacy record with given data

    @param pharmacy_info: dict
    :return: json
    """
    user_id = pharmacy_info.pop("user_id")
    pharmacy_info["created_by"] = user_id
    pharmacy_info["modified_by"] = user_id

    logger.debug("Inside add_pharmacy")

    try:
        record = add_pharmacy_data_dao(pharmacy_info)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)

    return create_response(record.id)
