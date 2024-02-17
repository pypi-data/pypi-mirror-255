import datetime
import time
import redis
import logging

from redis.exceptions import WatchError

import settings
from dosepack.error_handling.error_handler import error
from model.model_init import init_redisdb
from src.exceptions import RedisKeyException, RedisConnectionException

logger = logging.getLogger("root")


def set_paginate(paginate):
    if 'page_number' not in paginate:
        raise ValueError('paginate paramater must have key page_number')
    if 'number_of_rows' not in paginate:
        raise ValueError('paginate paramater must have key number_of_rows')

    if paginate['page_number'] > 0:
        paginate['page_number'] -= 1
    offset = paginate['page_number'] * paginate["number_of_rows"]
    limit = offset + paginate["number_of_rows"] - 1

    return offset, limit


def add_records_in_redisdb(redisdb, rediskey, list_of_records):
    if settings.refreshing_redis:
        add_records_in_redisdb(redisdb, rediskey, list_of_records)
    else:

        try:
            settings.refreshing_redis = True
            with redisdb.pipeline() as pipe:
                pipe.multi()
                if pipe.exists(rediskey):
                    pipe.delete(rediskey)
                else:
                    pass
                if list_of_records:
                    for record in list_of_records:
                        pipe.rpush(rediskey, str(record))
                else:
                    pipe.rpush(rediskey, str(list_of_records))
                pipe.execute()
            settings.refreshing_redis = False
        except Exception as e:
            settings.refreshing_redis = False
            raise Exception(e)


def fetch_records_from_redisdb(redisdb,rediskey):
    template_records = []
    formatted_template_records = []
    start = 0
    end = -1
    # if paginate is not None:
    #     start, end = set_paginate(paginate)

    try:
        if redisdb.exists(rediskey):
            template_records = redisdb.lrange(rediskey, start, end)
        else:
            raise RedisKeyException

        if template_records != ['[]']:
            formatted_template_records = [eval(record) for record in template_records]
    except RedisKeyException:
        raise RedisKeyException("No records found in redisdb with specified key")
    except Exception as e:
        raise Exception(e)

    return formatted_template_records

# def add_new_template_records_in_redisDB(template_ids, status, company_id):
#     print("start: add_new_template_records_in_redisDB")
#
#     templates_records = []
#     try:
#
#         for record in TemplateMaster.db_get_templates_by_ids(template_ids, status, company_id):
#             templates_records.append(record)
#
#     except StopIteration as e:
#         logger.error(e, exc_info=True)
#         return error("Pending Template records not found in template_master table")
#
#     for record in templates_records:
#         redisdb.rpush("PendingTemplates:{0}".format(company_id), str(record))
