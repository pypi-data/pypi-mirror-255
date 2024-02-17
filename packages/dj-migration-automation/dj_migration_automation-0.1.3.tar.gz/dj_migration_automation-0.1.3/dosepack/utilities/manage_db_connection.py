import os
import time

import cherrypy
from peewee import MySQLDatabase

from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from functools import wraps
from pymysql.err import OperationalError
from sqlalchemy.exc import OperationalError as SQLOperational
from peewee import OperationalError as PeeWeeOperational
connection_dict = {}
API_WATCH = {}

def use_database(db_instance, logger_instance):
    """
    this decorator is used for opening and closing connection to the database
    """

    def decorator(function):
        @wraps(function)
        def connection_handler(*args, **kwargs):
            if not isinstance(db_instance, MySQLDatabase):
                logger_instance.info("Invalid database instance")
                return error(1013)
            if int(os.environ.get('USE_CONNECTION_POOL', 0)):
                in_use = db._in_use
            else:
                in_use = {}
            fn_name = str(function.__qualname__)

            path_info = cherrypy.request.path_info
            params = cherrypy.request.params
            body_params = cherrypy.request.body_params
            query_string = cherrypy.request.query_string


            logger_instance.info("API Request from : {}:{} | with request_line {} | API header {} | db_connection_in_use_before_api = {}".format(
                cherrypy.request.remote.ip, cherrypy.request.remote.port, cherrypy.request.request_line,
                cherrypy.request.headers, len(in_use)))
            logger_instance.info("Opening DB Connection for: " + str(function))
            connection_dict.update({
                str(function): len(in_use)
            })
            logger_instance.info("Connection_dict: {}".format(connection_dict))

            if not before_request_handler(db_instance, logger_instance):
                return error(1003)
            start = time.perf_counter()
            try:

                # if fn_name not in API_WATCH:
                #     API_WATCH.update({
                #         fn_name: 1}
                #     )
                # else:
                #     API_WATCH[fn_name] += 1
                # logger_instance.info("API_WATCH {}".format(API_WATCH))


                response = function(*args, **kwargs)
                return response
            finally:
                logger_instance.info("Closing DB Connection for: " + str(function))

                request_time = time.perf_counter() - start
                logger_instance.info(
                    "API URL : {} time_taken : {} sec, params : {}, query_string : {}".format(str(path_info), request_time, str(params), str(query_string)))
                # logger_instance.info("API TIMER | {} Took {} seconds to execute".format(fn_name, request_time))

                # if fn_name in API_WATCH:
                #     API_WATCH[fn_name] -= 1
                # logger_instance.info("OUT API_WATCH {}".format(API_WATCH))
                after_request_handler(db_instance)

        return connection_handler
    return decorator


def use_database_celery(db_instance, logger_instance):
    """
    This decorator is used for opening and closing connection to the database
    """

    def decorator(function):
        @wraps(function)
        def connection_handler(*args, **kwargs):
            if not isinstance(db_instance, MySQLDatabase):
                logger_instance.info("Invalid database instance")
                return error(1013)

            fn_name = str(function.__qualname__)

            path_info = cherrypy.request.path_info
            params = cherrypy.request.params
            query_string = cherrypy.request.query_string

            logger_instance.info("API Request from: {}:{} | with request_line {} | API header {}".format(
                cherrypy.request.remote.ip, cherrypy.request.remote.port, cherrypy.request.request_line,
                cherrypy.request.headers))
            logger_instance.info("Opening DB Connection for: " + str(function))

            if not before_request_handler(db_instance, logger_instance):
                return error(1003)
            start = time.perf_counter()
            try:
                with db_instance.atomic():
                    db_instance.connect()

                    response = function(*args, **kwargs)
                    return response
            finally:
                db_instance.close()
                logger_instance.info("Closing DB Connection for: " + str(function))

                request_time = time.perf_counter() - start
                logger_instance.info(
                    "API URL: {} time_taken: {} sec, params: {}, query_string: {}".format(str(path_info), request_time, str(params), str(query_string)))
                after_request_handler(db_instance)

        return connection_handler

    return decorator


def before_request_handler(db_instance, logger_instance):
    try:
        # switching to get_conn from connect() # need to check performance and connection issue
        db_instance.get_conn()
        return True
    except (Exception, OperationalError, SQLOperational, PeeWeeOperational) as e:
        print("in_exception: ", str(e))
        logger_instance.info("in_exception: " + str(e))
        logger_instance.error("error in opening database connection: " + str(e))
        return False


def after_request_handler(db_instance):
    if not db_instance.is_closed():
        db_instance.close()
