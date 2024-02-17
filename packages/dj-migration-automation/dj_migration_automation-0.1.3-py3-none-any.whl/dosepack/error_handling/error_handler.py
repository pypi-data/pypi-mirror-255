# -*- coding: utf-8 -*-
"""
    src.error_handler
    ~~~~~~~~~~~~~~~~
    This is the central error handling module. It creates the error response from the error code
    provided. It also contains the response handler. It gets the response and converts it to json.

    Example:

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""

import json
from collections import namedtuple
import datetime
from decimal import Decimal
from typing import Optional

import settings
from dosepack.local.lang_us_en import err
from dosepack.utilities.utils import tz_unaware_datetime_to_string
from src.constants import IPS_STATUS_CODE_OK

Error = namedtuple('Error', 'status code description')
Response = namedtuple('Response', 'data status')


def date_handler(obj):
    """
        @function: date_handler
        @createdBy: Manish Agarwal
        @createdDate: 7/22/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 08/12/2015
        @type: function
        @param: date
        @purpose - Parse the date object to isoformat so that it
                    can be handled by json
    """
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj


def datetime_handler(obj):
    """
        @function: datetime_handler
        @type: function
        @param: date
        @purpose - converts the datetime object to javascript parsable string,
        For non-datetime object custom date handler will be used
    """
    if isinstance(obj, datetime.datetime):
        return tz_unaware_datetime_to_string(obj)
    else:
        return date_handler(obj)


def create_response(data, additional_info=None, default=datetime_handler):
    response = {"data": data, "status": settings.SUCCESS_RESPONSE}
    if additional_info:
        response.update(additional_info)
    return json.dumps(response, default=default, indent=4)


def error(code=0, *args, additional_info=None):
    desc = err[code]
    for args in args:
        desc += str(args)
    response = {"code": code, "description": desc, "status": settings.FAILURE_RESPONSE}
    if additional_info:
        response.update(additional_info)
    return json.dumps(response)


def update_dict(base_dict, remove_fields=None, add_fields=None):
    if add_fields:
        base_dict.update(add_fields)
    if remove_fields:
        for item in remove_fields:
            base_dict.pop(item, 0)
    return base_dict


def ips_response(code: Optional[int] = IPS_STATUS_CODE_OK, *args):
    desc = ''
    for args in args:
        desc += str(args).replace("'", " ").replace('"', ' ').replace(")", "_").replace("(", "_").replace("/"," ").replace("\\", "")
    return json.dumps({"code": code, "description": desc, "status": settings.SUCCESS_RESPONSE})


def remove_sql_injectors(string):
    return string.replace("_", " ").replace("'", " ").replace('"', ' ').replace(")", "_").replace("(", "_").replace("/"," ").replace("\\", "")