"""
This script runs multiple threads, with each thread calls apis and detects any database connection issue.
Script runs infinite if doesn't found any error in API or any database connection error.
Logs every apis data

Example:
    $ python ./tests/test_db_connection.py  (From project root dir)
"""

import logging
from logging.config import dictConfig
from itertools import cycle
import threading
import os
import time
import json
import datetime

from dosepack.utilities.utils import call_webservice


def get_filename():
    filename = os.path.join("logs", str(datetime.datetime.now().strftime("%Y")),
                               str(datetime.datetime.now().strftime("%m")), "test_db_conn.log")
    return filename


logging_config = dict(
    version=1,
    formatters={
        'simple': {'format':
              '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
        },
    handlers={
        'h': {"encoding": "utf8",
               "level": "DEBUG",
               "when": "midnight",
               "filename": get_filename(),
               "formatter": "simple",
               "class": "logging.handlers.TimedRotatingFileHandler"}
        },

    loggers={
        'root': {'handlers': ['h'],
                 'level': logging.DEBUG}
        }
)

dictConfig(logging_config)

path = os.path.join("../logs", str(datetime.datetime.now().strftime(
        "%Y")), str(datetime.datetime.now().strftime("%m")))

if not os.path.exists(path):
    os.makedirs(path)


RUN = True
THREAD_COUNT = 5  # No of threads
SSL_CALL = False  # whether to use http(False) or https(True)
LOG_API_DATA = True
access_token = None  # to store access token to be use for api calls
BASE_URL = 'localhost:10008'  # Base URL of server
headers = dict()
apis_data = {'/templates': {'system_id': 16},
             '/files': {'date_from': '4-3-18', 'date_to': '4-4-18', 'system_id': 10, 'status': 0},
             '/packs': {'date_to': '04-04-18' , 'date_from': '12-05-17', 'status': 2, 'system_id': 10}
             }  # All GET APIs to be used # key: api name,  value: parameters


logger = logging.getLogger("root")


def call_and_log_api(api_endpoint, parameters):
    """
    Calls api using api name and base url defined, If detects any error, stops all threads

    :param api_endpoint:
    :param parameters:
    :return:
    """
    try:
        global RUN
        status, response = call_webservice(BASE_URL, api_endpoint, parameters, use_ssl=SSL_CALL, headers=headers)
        if not status:
            logger.error('Errors in API call, HTTP REQUEST ERROR')
            RUN = False  # error in api call
        if LOG_API_DATA:
            logger.debug('API: ' + api_endpoint + ' Status: ' + str(status) + ' Response: ' +str(response))
        response = str(response)
        if response.find('database') > 0 and response.find('connection') > 0:
            logger.error('Errors in API call, CUSTOM ERROR')
            RUN = False  # found error for database connection
    except json.JSONDecodeError as e:
        logger.error(e, exc_info=True)
        logger.error('Errors in API call, DATA ERROR')
        RUN = False


def call_apis():
    """
    Calls All apis in cycle one by one defined in apis_data

    :return:
    """
    logger.info('Thread ID: ' + str(threading.get_ident()))
    apis_list = list(apis_data.keys())
    apis = cycle(apis_list)
    while RUN:
        time.sleep(0.5)
        api = next(apis)
        try:
            call_and_log_api(api, apis_data[api])
        except Exception as e:
            logger.error('Error while calling API: ' + api + str(e), exc_info=True)


if __name__ == '__main__':
    print('Starting db connection test')
    logger.info('Starting db connection test')

    if not access_token:  # If not token present ask for access token
        access_token = input('Please paste access token for api requests')
    headers["Authorization"] = 'Bearer ' + str(access_token)

    thread_list = list()
    for i in range(THREAD_COUNT):
        t = threading.Thread(target=call_apis)
        thread_list.append(t)
        t.start()

    try:  # Keep script alive
        while RUN:
            pass
    except KeyboardInterrupt:
        RUN = False

    print('Stopping db connection test')
    logger.info('Stopping db connection test')

