
import settings
from model.model_init import init_redisdb
from src.dao.generate_templates_dao import db_get_pending_templates_data
from src.dao.template_dao import db_get_pending_templates_data
from src.exceptions import RedisConnectionException, RedisKeyException
from src.redis_utility import add_records_in_redisdb, fetch_records_from_redisdb
import logging

logger = logging.getLogger("root")


def update_pending_template_data_in_redisdb(company_id):
    logger.info("updating_pending_template_data_in_redisdb")
    try:
        redisdb = init_redisdb('redis_server_db_0')
        template_records = []
        rediskey = "PendingTemplates:{0}".format(company_id)
        logger.info("Fetching_from_db_for_redis_update")
        template_records = db_get_pending_templates_data(company_id)
        logger.info("Fetching_done_updating_redis")
        add_records_in_redisdb(redisdb, rediskey, template_records)
        logger.info("redis_update_done")
        settings.is_redis_updated = True
        # logger.info("updated_pending_template_data_in_redisdb: "+str(rediskey))
    except RedisConnectionException as e:
        settings.is_redis_updated = False
        logger.info("redisdb_update_fails")
        raise RedisConnectionException(e)
    except Exception as e:
        settings.is_redis_updated = False
        logger.info("redisdb_update_fails")
        raise Exception(e)


def fetch_template_records_from_redisdb(company_id):
    template_records = []
    try:
        redisdb = init_redisdb('redis_server_db_0')
        rediskey = "PendingTemplates:{0}".format(company_id)
        template_records = fetch_records_from_redisdb(redisdb, rediskey)
        # logger.info("fetched_template_records_from_redisdb: "+str(rediskey))
    except RedisKeyException as e:
        raise RedisKeyException(e)
    except RedisConnectionException as e:
        raise RedisConnectionException(e)
    except Exception as e:
        raise Exception(e)
    return template_records
