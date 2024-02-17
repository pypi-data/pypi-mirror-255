import base64
import copy
import datetime
import json
import logging
import math
import base64
import copy
import datetime
import json
import logging
import math
import os
import sys
from collections import OrderedDict, defaultdict
from copy import deepcopy
from typing import List, Dict, Any

import pandas as pd
from numpy import nanmin
from peewee import InternalError, IntegrityError, DataError, DoesNotExist, Expression
from pytz import UnknownTimeZoneError

import settings
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response
from src import constants
from src.dao.batch_dao import get_progress_batch_id
from src.dao.crm_dao import get_done_pack_count, check_notification_sent_or_not, get_deleted_pack_count
from src.dao.misc_dao import get_packs_count_for_system
from src.dao.pack_dao import get_filled_packs_count_for_system
from src.service.batch import create_batch
from src.service.crm import get_system_packs_count_by_status, get_packs_count_by_robot_id_retail
from src.service.notifications import Notifications

logger = settings.logger

@log_args_and_response
def get_dashlet_data(args):

    try:
        time_zone = args.get('time_zone', 'UTC')
        time_zone = settings.TIME_ZONE_MAP[time_zone]
        TZ = settings.TZ_MAP[time_zone]

        system_id = args['system_id']
        company_id = args['company_id']

        response_data = json.loads(get_system_packs_count_by_status(args))
        response_data['data']['pending_packs_count'] = response_data['data'].pop('pending_pack_count')
        response_data['data']['progress_packs_count'] = response_data['data'].pop('progress_pack_count')
        response = response_data["data"]
        if not response['pack_count']:
            # return error(14018)
            # This error has been replaced with dummy response as requested from FE.
            # Now empty queue will be handled by FE
            dummy_response = {"system_id": "14",
                              "pack_count": 0,
                              "pending_packs_count": 0,
                              "progress_packs_count": 0,
                              }
            return create_response(dummy_response)

        # if settings.CLIENT_TYPE == constants.RETAIL_CARE_PHARMACY:
        #     batch_id = get_progress_batch_id(system_id)
        #     if not batch_id:
        #         return error(14002)
        #     response['batch_id']= batch_id

        robot_pack_data_list = get_packs_count_by_robot_id_retail(
            {"status": None, "system_id": system_id})
        # response1 = response1_data['data']
        logger.info("IN get_dashlet_data: robot_pack_data_list: {}".format(robot_pack_data_list))
        response['robot_pack_data'] = robot_pack_data_list
        total_pack_count = get_packs_count_for_system(system_id=system_id)

        # if total_pack_count == 0:
        #     response['batch_update_flag'] = True
        #     batch_info = {"user_id": args['user_id'],
        #                   "batch_id": batch_id,
        #                   "status": settings.BATCH_PROCESSING_COMPLETE,
        #                   "system_id": args['system_id'],
        #                   "crm": True}
        #     response['pack_batch'] = json.loads(create_batch(batch_info))
        #     notification_message = "No packs left for processing in batch {}".format(batch_id)
        #     notification_sent_status = check_notification_sent_or_not(notification_message=notification_message)
        #     if not notification_sent_status:
        #         Notifications(call_from_client=True, company_id=company_id).send(settings.ALL_USER_NOTIFICATION,
        #                                                                          notification_message, flow='dp')
        # else:
        #     response['batch_update_flag'] = False
        #     if pending_packs_count == settings.PACKS_LEFT_FOR_PROCESSING_100:
        #         notification_message = "100 packs remains to be processed in batch {}".format(batch_id)
        #         notification_sent_status = check_notification_sent_or_not(notification_message=notification_message)
        #         if not notification_sent_status:
        #             Notifications(call_from_client=True, company_id=company_id).send(settings.ALL_USER_NOTIFICATION,
        #                                                                              notification_message, flow='dp')
        #
        #     elif pending_packs_count == settings.PACKS_LEFT_FOR_PROCESSING_30:
        #         notification_message = "30 packs remains to be processed in batch {}".format(batch_id)
        #         notification_sent_status = check_notification_sent_or_not(notification_message=notification_message)
        #         if not notification_sent_status:
        #             Notifications(call_from_client=True, company_id=company_id).send(settings.ALL_USER_NOTIFICATION,
        #                                                                              notification_message, flow='dp')
        today, last_one_hour = get_done_pack_count(time_zone, TZ)
        # response['done_pack_count'] = done_pack_count
        response['today'] = today
        response['last_one_hour'] = last_one_hour
        response["packs_deleted_today"] = get_deleted_pack_count(time_zone, TZ)

        return create_response(response)
    except UnknownTimeZoneError as e:
        logger.error(e, exc_info=True)
        return error(20011, e)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)