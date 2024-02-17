from peewee import (DoesNotExist, InternalError, fn, JOIN_LEFT_OUTER, DataError, IntegrityError, SQL)

import settings
from dosepack.utilities.utils import log_args_and_response
from src.model.model_pack_details import PackDetails
from src.model.model_pack_queue import PackQueue

logger = settings.logger


@log_args_and_response
def insert_packs_to_pack_queue(pack_ids):
    try:
        status = PackQueue.insert_pack_ids(pack_ids)
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in insert_packs_to_pack_queue {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in insert_packs_to_pack_queue {}".format(e))
        raise e


@log_args_and_response
def remove_pack_from_pack_queue(ids):
    try:
        status = None
        if ids:
            status = PackQueue.remove_pack_from_pack_queue(ids)
            return status
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in remove_pack_from_pack_queue {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in remove_pack_from_pack_queue {}".format(e))
        raise e


def get_pack_queue_data():
    try:
        query = PackQueue.select().dicts()
        records = [record for record in query]
        return records
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_queue_data {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_pack_queue_data {}".format(e))
        raise e


@log_args_and_response
def remove_packs_from_queue(pack_ids):
    try:
        pack_queue_ids = []
        dequeue_pack_ids = []
        incorrect_pack_ids = []
        query = PackQueue.select().dicts()
        in_queue_packs = [record for record in query]
        logger.info("TOTAL_PACKS_IN_QUEUE {}".format(in_queue_packs))

        pack_queue_data = get_pack_queue_data()
        if pack_queue_data:
            for record in in_queue_packs:
                if record["pack_id"] in pack_ids:
                    pack_queue_ids.append(record['id'])
                    dequeue_pack_ids.append(record['pack_id'])
                else:
                    incorrect_pack_ids.append(record['pack_id'])
            logger.info("In remove_packs_from_queue pack_ids getting removed from queue are {}".format(dequeue_pack_ids))
            logger.error("In remove_packs_from_queue: PACKS NOT FOUND IN QUEUE {}".format(incorrect_pack_ids))
            status = remove_pack_from_pack_queue(pack_queue_ids)
            if status:
                return True
            else:
                return False
        else:
            return True
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in remove_packs_from_queue {}".format(e))
        raise e
        return False

    except Exception as e:
        logger.error("error in remove_packs_from_queue {}".format(e))
        raise e
        return False


@log_args_and_response
def get_pack_queue_count():
    try:
        query = PackQueue.select(fn.COUNT(PackQueue.id))
        return query.scalar()
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_pack_queue_data {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in get_pack_queue_data {}".format(e))
        raise e


@log_args_and_response
def get_packs_from_pack_queue(company_id=None, system_id=None, status=None):
    try:
        logger.info("In get_packs_from_pack_queue")

        clauses = []

        query = PackQueue.select(PackDetails).dicts() \
                .join(PackDetails, on=PackQueue.pack_id == PackDetails.id)

        if company_id:
            clauses.append(PackDetails.company_id == company_id)

        if system_id:
            clauses.append(PackDetails.system_id == system_id)

        if status:
            clauses.append(PackDetails.pack_status == status)

        if clauses:
            query = query.where(*clauses)

        return query

    except Exception as e:
        logger.error("error in get_packs_from_pack_queue {}".format(e))
        raise e


@log_args_and_response
def check_packs_in_pack_queue_or_not(pack_ids):
    try:
        logger.info("In check_packs_in_pack_queue_or_not")

        in_pack_queue = None

        in_pack_queue = PackQueue.packs_in_pack_queue_or_not(pack_ids)

        return in_pack_queue
    except Exception as e:
        logger.error("error in check_packs_in_pack_queue_or_not {}".format(e))
        raise e