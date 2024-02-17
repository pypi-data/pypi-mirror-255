import csv
import datetime
import json
import logging
import math
import re
import shutil
import time
from collections import OrderedDict
from typing import Tuple, Optional

import pytz
import requests
import magic
from dateutil.parser import parse

import settings
from dosepack.base_model.base_model import db
from settings import FILE_OPERATIONS
from src import constants

# from src.service.drug_search import get_drug_data_by_bottle

# from utils.drug_inventory_webservices import get_drug_data_by_bottle

logger = logging.getLogger("root")
try:
    import _winreg as winreg
except ImportError:
    pass

# Scanned Entity Dict Constants
SCAN_ENTITY_DICT = {"user_entered": 0, "barcode": 1, "data_matrix": 2, "QR": 3, "UPC": 4, "vial_QR": 5}
SCAN_TYPE_COMPATIBILITY = {0: constants.USER_ENTERED, 1: constants.BARCODE, 2: constants.DATA_MATRIX,
                           3: constants.QR_SCAN, 4: constants.UPC_SCAN, 5: constants.VIAL_SCAN}

# FOR NDCFI DIGIT REMOVER
NDCFI_LOCATION_DICT = {1: 0, 2: 5, 3: 9, 4: 5, 5: 9, 6: 10, 7: 0}


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
    else:
        raise TypeError(
            "Unserializable object {} of type {}".format(obj, type(obj))
        )


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, tuple):
            return list(obj)

        return json.JSONEncoder.default(self, obj)


def fn_success(function_name, args):
    """
        @function: success
        @createdBy: Manish Agarwal
        @createdDate: 7/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 08/12/2015
        @type: function
        @param: str,list
        @purpose - returns success message with given input field
    """
    return "function: " + function_name + " executed successfully with input " + str(args)


# Manish Agarwal 4/13/16 BugID: 64753
# Changing date format to MySQL date format
def get_current_date():
    """
        @function: get_current_date
        @createdBy: Manish Agarwal
        @createdDate: 7/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 08/12/2015
        @type: function
        @param: none
        @purpose - return the current date
    """
    return datetime.datetime.utcnow().strftime('%Y-%m-%d')


# Manish Agarwal 4/13/16 BugID: 64753
# Changing date format to MySQL time format
def get_current_time():
    """
        @function: get_current_time
        @createdBy: Manish Agarwal
        @createdDate: 7/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 08/12/2015
        @type: function
        @param: none
        @purpose - return the current time
    """
    return datetime.datetime.utcnow().strftime('%H:%M:%S')


# Changing date format to MySQL datetime format
def get_current_date_time():
    """
        @function: get_current_date_time
        @createdBy: Manish Agarwal
        @createdDate: 7/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 08/12/2015
        @type: function
        @param: none
        @purpose - return the current date and time
    """
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def convert_utc_timezone_into_local_time_zone():
    try:
        current_time = get_current_date_time() + " +0000"
        current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S %z")

        time_zone = settings.DEFAULT_TIME_ZONE

        updated_time = current_time.astimezone(pytz.timezone(time_zone))
        updated_time = datetime.datetime.strftime(updated_time, "%Y-%m-%d %H:%M:%S.%f")[:-3]

        return updated_time
    except Exception as e:
        raise e


# Get local Time zone where code is being executed
def get_current_time_zone():
    time_str: str = str(datetime.datetime.astimezone(datetime.datetime.utcnow()))
    return time_str[len(time_str) - 6: len(time_str)]


def get_current_date_time_as_per_time_zone():
    utc_now = datetime.datetime.utcnow()
    buffer = datetime.datetime.now(pytz.timezone(settings.CURRENT_TIMEZONE)).utcoffset().total_seconds() / 3600
    hours = int(buffer)
    minutes = int((buffer % 1) * 60)
    result_date = utc_now + datetime.timedelta(hours=hours, minutes=minutes)
    return result_date


# Changing date from %m-%d-%y format to %Y-%m-%d %H:%M:%S
def convert_date_to_sql_date(from_date, to_date):
    """
        @function: convert_date_to_sql_date
        @createdBy: Manish Agarwal
        @createdDate: 4/13/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/13/2016
        @type: function
        @param: none
        @purpose - convert the received data to sql date
    """
    try:

        from_date = datetime.datetime.strptime(from_date, '%m-%d-%y')
        from_date = from_date.strftime('%Y-%m-%d')

        to_date = datetime.datetime.strptime(to_date, '%m-%d-%y')
        to_date = to_date.strftime('%Y-%m-%d')

        return from_date, to_date

    except ValueError:
        raise ValueError("Input Dates not in proper format")


# Changing date from %m-%d-%Y format to %Y-%m-%d
def convert_dob_date_to_sql_date(date):
    """
    This function converts dob from %m-%d-%Y format to %Y-%m-%d
    @param date:
    @return:
    @purpose - convert the received dob data to sql date
    """

    date_patterns = ["%Y-%m-%d", "%Y-%d-%m", "%m-%d-%Y", "%d-%m-%Y"]

    try:
        for pattern in date_patterns:
            try:
                date1 = datetime.datetime.strptime(date, pattern)
                return_date = date1.strftime('%Y-%m-%d')
                return return_date
            except Exception as e:
                logger.error(e)
                pass

    except ValueError:
        raise ValueError("Input Dates not in proper format")


def get_next_date_by_timezone(time_zone, type="datetime"):
    """

    @param time_zone:
    @param type:
    @return:
    """
    current_date = datetime.datetime.now(pytz.timezone(time_zone))
    next_date = current_date + datetime.timedelta(days=1)
    if type == "date":
        return next_date.strftime("%Y-%m-%d")
    else:
        return next_date.strftime("%Y-%m-%d %H:%M:%S %Z%z")


def get_current_datetime_by_timezone(time_zone, return_format="datetime"):
    """
    @purpose: Function will return datetime of specific time zone
    @param time_zone:
    @param return_format:
    @return:
    """
    current_date = datetime.datetime.now(pytz.timezone(time_zone))
    if return_format == "date":
        return current_date.strftime("%Y-%m-%d")
    else:
        return current_date.strftime("%Y-%m-%d %H:%M:%S")


def get_current_day_date_end_date_by_timezone(time_zone: str, number_of_days: Optional[int] = 0) -> Tuple[str, str,
                                                                                                          int]:
    """
    This function returns the current date and day for the given timezone.
    """
    current_date: datetime = datetime.datetime.now(pytz.timezone(time_zone))
    end_date: datetime = current_date + datetime.timedelta(days=number_of_days)
    current_day = current_date.weekday()
    return current_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), current_day


def get_epoch_time_start_of_day_and_before_n_days(number_of_days: Optional[int] = 0) -> Tuple[int, int]:
    """
    This function gives the epoch times (in seconds) of today start of the day and the day before n number of days
    """
    time_now: datetime = datetime.datetime.now()
    today_start_of_day: datetime = datetime.datetime(time_now.year, time_now.month, time_now.day)
    n_days_back_start_of_day: datetime = today_start_of_day - datetime.timedelta(days=number_of_days)
    return int(time.mktime(n_days_back_start_of_day.timetuple())), int(time.mktime(today_start_of_day.timetuple()))


def get_date_n_days_back_the_epoch_time(epoch_time: int, number_of_days: Optional[int] = 0,
                                        return_format: Optional[str] = "datetime") -> str:
    """
    This function gets the date of n days back from the given epoch time.
    """
    given_datetime: datetime = datetime.datetime.fromtimestamp(epoch_time)
    required_date: datetime = given_datetime-datetime.timedelta(days=number_of_days)
    if return_format == "date":
        return required_date.strftime("%Y-%m-%d")
    else:
        return required_date.strftime("%Y-%m-%d %H:%M:%S")


def convert_date_to_sql_datetime(from_date, to_date):
    """
        @function: convert_date_to_sql_datetime
        @type: function
        @param: none
        @purpose - Convert the received date to sql datetime (to make sql from and to date filtering easy)
    """
    try:
        logger.info("Input convert_date_to_sql_datetime {}, {}".format(from_date, to_date))
        from_date = datetime.datetime.strptime(from_date, '%m-%d-%y').date()
        from_date = datetime.datetime.combine(from_date, datetime.time(0, 0, 0))
        from_date = from_date.strftime('%Y-%m-%d %H:%M:%S')

        to_date = datetime.datetime.strptime(to_date, '%m-%d-%y').date()
        to_date = datetime.datetime.combine(to_date, datetime.time(23, 59, 59))
        to_date = to_date.strftime('%Y-%m-%d %H:%M:%S')
        logger.info("Output convert_date_to_sql_datetime {}, {}".format(from_date, to_date))
        return from_date, to_date
    except ValueError:
        raise ValueError("Input Dates not in proper format")


# Changing date from %Y-%m-%d %H:%M:%S to %m-%d-%y
def convert_date_from_sql_to_display_date(_date):
    """
        @function: convert_date_from_sql_to_display_date
        @createdBy: Manish Agarwal
        @createdDate: 4/13/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/13/2016
        @type: function
        @param: none
        @purpose - convert date received from sql db to user display format
    """
    try:
        return str(_date.strftime('%m-%d-%y'))
    except ValueError:
        raise ValueError("Input Dates not in proper format")


# Changing date from %m-%d-%Y format to %Y-%m-%d
def convert_dob_date_to_sql_date(date):
    """
    This function converts dob from %m-%d-%Y format to %Y-%m-%d
    @param date:
    @return:
    @purpose - convert the received dob data to sql date
    """

    date_patterns = ["%Y-%m-%d", "%Y-%d-%m", "%m-%d-%Y", "%d-%m-%Y", "%m-%d-%y", "%d-%m-%y"]

    try:
        for pattern in date_patterns:
            try:
                date1 = datetime.datetime.strptime(date, pattern)
                return_date = date1.strftime('%Y-%m-%d')

                return return_date

            except:
                pass

        # date = datetime.datetime.strptime(date, '%m-%d-%Y')
        # date = date.strftime('%Y-%m-%d')

        # return date

    except ValueError:
        raise ValueError("Input Dates not in proper format")


def tz_unaware_datetime_to_string(_datetime, timezone='UTC', _format="%Y-%m-%d %H:%M:%S %Z%z"):
    """
        @function: tz_unaware_datetime_to_string
        @type: function
        @param: _datetime - datetime object
                timezone - timezone supported by pytz
                format - format of string to format datetime
        @purpose Sets timezone for datetime object and converts to string
    """
    return _datetime.replace(tzinfo=pytz.timezone(timezone)).strftime(_format)


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def get_input_type_and_formatted_input(string):
    """
    This function identify the type of input and returns the type of the input and the type casted input
    @param string:
    @return: input type, type casted input
    """
    try:
        if string.isdigit():
            input_type = settings.TYPE_INT
            type_casted_input = int(string)
        elif is_date(string):
            input_type = settings.TYPE_DATE
            type_casted_input = convert_dob_date_to_sql_date(string)
        else:
            input_type = settings.TYPE_STRING
            type_casted_input = string
        return input_type, type_casted_input
    except ValueError:
        raise ValueError("Input Data not in proper format")


def fn_shorten_drugname(drug_name, ai_width=14, ai_min=3):
    """
        @function: fn_shorten_drugname
        @createdBy: Abner Famoso
        @createdDate: 02/16/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 02/17/2016
        @type: function
        @param: as_drugname string - Name of the drug
                      as_strength string - Drug strength
                      ai_width smallint - Width of the shortname
                      ai_min smallint - Minimum width per word
        @desc:  Create a short version of the drug name to display on the label
    """

    # Modifying the previous logic. Now drug name wil have the first word of drug name
    # and wil append with DR or ER and it will have full strength too.
    try:
        # Split all the words
        ls_drug_name = drug_name.split(' ')

        # Get the total number of words by type and total width of numeric
        li_tot_num_width = 0

        # Generate the short name
        ls_short_name = ''

        for key, value in enumerate(ls_drug_name):
            ls_first_char = value[0]
            if '0' <= ls_first_char <= '9':
                li_tot_num_width += len(value)
                ls_short_name += ' ' + value

            if value == 'ER' or value == 'DR':
                li_tot_num_width += len(value)
                ls_short_name += ' ' + value

        # Get the width per word, excluding the numeric
        li_div = ai_width - li_tot_num_width
        if li_div < ai_min:
            li_div = ai_min

        short_name = ls_drug_name[0][0:li_div] + ls_short_name

        return short_name
    except Exception as e:
        return drug_name[0:14]


def fn_shorten_drugname_v2(drug_name, strength, strength_value, ai_width=20, ai_min=3, include_strength=False):
    """
    Shortens drug name using first word and selected number of chars(ai_min) of following words
        keeps strength_value at the end
        includes strength (flag based)
    :param drug_name:
    :param strength:
    :param strength_value:
    :param ai_width:
    :param ai_min:
    :param include_strength:
    :return:
    """
    try:
        drug_name = drug_name.replace('VITAMIN', 'VIT').replace('WITH', '+').replace('AND', '&')

        # Split all the words
        # ls_drug_name = drug_name.split(' ')
        ls_drug_name = re.split('[-\s]', drug_name)

        # Get the total number of words by type and total width of numeric
        li_tot_num_width = 0

        # Generate the short name
        ls_short_name = ''
        used_keys = []
        ls_short_name += ' ' + strength_value

        if include_strength:
            ls_short_name += ' ' + strength

        for key, value in enumerate(ls_drug_name):
            if value == 'ER' or value == "DR":
                li_tot_num_width += len(value)
                ls_short_name += ' ' + value
                used_keys.append(key)

        # Get the width per word, excluding the numeric
        li_div = ai_width - li_tot_num_width
        if li_div < ai_min:
            li_div = ai_min

        short_drug_name = ls_drug_name[0][0:li_div]
        used_keys.append(0)

        if ai_width - len(short_drug_name + ls_short_name) >= ai_min:
            for key, value in enumerate(ls_drug_name):
                if key in used_keys:
                    continue

                if ai_width - len(short_drug_name + ls_short_name) < ai_min:
                    break
                else:
                    if key == len(ls_drug_name) - 1:
                        short_drug_name += ' ' + value[0:ai_width - len(short_drug_name + ls_short_name)]
                    else:
                        short_drug_name += ' ' + value[0:ai_min]

        short_name = short_drug_name + ls_short_name

        return short_name
    except Exception as e:
        return drug_name[0:14]


def timef(f, ns=1, dt=60):
    """
        Takes a function and runs it in loop for ns times to calculate the average time.
    """
    import time
    t = t0 = time.time()
    for k in range(1, ns):
        f()
        t = time.time()
        if t - t0 > dt:
            break
    return (t - t0) / k


def format_date_time(value, formats, post_process=None):
    """
        Takes a date value and formats it according to the given format in the input parameters.
    """
    post_process = post_process or (lambda x: x)
    for fmt in formats:
        try:
            return post_process(datetime.datetime.strptime(value, fmt))
        except ValueError:
            pass
    return value


def not_allowed(func):
    """
    Method decorator to indicate a method is not allowed to be called.  Will
    raise a `NotImplementedError`.
    """

    def inner(self, *args, **kwargs):
        raise NotImplementedError('%s is not allowed on %s instances' % (
            func, type(self).__name__))

    return inner


def incorrect_type(required_type):
    """
        @function: incorrect_type
        @createdBy: Manish Agarwal
        @createdDate: 7/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 08/12/2015
        @type: function
        @param: str
        @purpose - returns incorrect type message
    """
    return "required: " + required_type + " other provided"


# Retry decorator with exponential back off
def retry(tries, delay=3, backoff=2):
    """Retries a function or method until it returns True.
    delay sets the initial delay in seconds, and backoff sets the factor by which
    the delay should lengthen after each failure. backoff must be greater than 1,
    or else it isn't really a backoff. tries must be at least 0, and delay
    greater than 0."""

    if backoff <= 1:
        raise ValueError("back off must be greater than 1")

    tries = math.floor(tries)

    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay  # make mutable
            logger.info('Trying time' + str(mtries))

            status, result = f(*args, **kwargs)  # first attempt

            while mtries > 0:

                if status:
                    return True, result

                mtries -= 1  # consume an attempt
                time.sleep(mdelay)  # wait...
                mdelay *= backoff  # make future wait longer

                status, result = f(*args, **kwargs)

            return False, result  # Ran out of tries

        return f_retry  # true decorator -> decorated function

    return deco_retry


def retry_exception(times, exceptions, delay=1, back_off=2):
    """
    Retry Decorator
    Retries the wrapped function/method `times` times if the exceptions listed
    in ``exceptions`` are thrown
    :param times: The number of times to repeat the wrapped function/method
    :type times: Int
    :param Exceptions: Lists of exceptions that trigger a retry attempt
    :type Exceptions: Tuple of Exceptions
    """
    def decorator(func):
        def newfn(*args, **kwargs):
            newdelay = delay
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    print(
                        'Exception thrown when attempting to run %s, attempt '
                        '%d of %d' % (func, attempt, times)
                    )
                    attempt += 1
                    time.sleep(newdelay)
                    newdelay += back_off
            return func(*args, **kwargs)
        return newfn
    return decorator


@retry(3)
def call_webservice(base_url, webservice_url, parameters, cache=False, headers=None, request_type="GET",
                    use_ssl=False, timeout=None, call_electronics_api=False, odoo_api=False, epbm_api=False, ips_api=False,
                    dump_data=False, files=None, query_string_parameter=None):
    """
        @function: call_webservice
        @createdBy: Manish Agarwal
        @createdDate: 05/28/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 05/28/2016
        @type: function
        @param: dict
        @purpose - make a webservice call
        @input - 'localhost:10008/' 'getcanisterinfo', '{"robot_id": 6}'

        @output - {"data":[], "status":1}

    """
    logger.info("Inpur args for call_webservice {}, {}, {}, {}, {}".format(base_url, webservice_url,
                                                                           parameters,epbm_api, odoo_api))
    if request_type == "GET":
        url = construct_webservice_url(base_url, webservice_url, parameters, use_ssl=use_ssl)
    elif request_type == "POST" and query_string_parameter:
        url = construct_webservice_url(base_url, webservice_url, query_string_parameter, use_ssl=use_ssl)
    else:
        url = 'http://' + base_url + webservice_url
    print("url", url)
    if use_ssl:
        connection_adapter = 'https://'
    else:
        connection_adapter = 'http://'
    # Connect to the web service
    try:
        if request_type == "GET":
            data = requests.get(url, headers=headers, timeout=timeout, verify=False)
        elif request_type == "POST" and not odoo_api and not epbm_api and not ips_api:

            data = requests.post(connection_adapter + base_url + webservice_url, data={"args": parameters},
                                 timeout=timeout, verify=False, files=files)
        elif request_type == "POST" and odoo_api and not epbm_api:
            url = connection_adapter + base_url + webservice_url
            data = requests.post(connection_adapter + base_url + webservice_url, data=parameters,
                                 timeout=timeout, headers=headers, verify=False)
        elif request_type == "POST" and epbm_api:
            if query_string_parameter:
                data = requests.post(url, headers=headers,
                                     data=json.dumps(parameters), timeout=timeout, verify=False)
            else:
                data = requests.post(connection_adapter + base_url + webservice_url, headers=headers,
                                     data=json.dumps(parameters), timeout=timeout, verify=False)
        elif request_type == "POST" and ips_api:
            data = requests.post(connection_adapter + base_url + webservice_url, data=json.dumps(parameters),
                                 timeout=timeout, verify=False, headers=headers)
        if call_electronics_api:
            response_data = data.content.decode('utf8').replace("'", '"')
            print("response data for url {}: {}".format(url, response_data))
        elif epbm_api:
            if data.status_code == 401:
                return False, data.status_code
            response_data = data.json()
            print("response data for url {}: {}".format(url, response_data))
        else:
            response_data = json.loads(str(data.content, 'utf-8'))
            print("response data for url {}: {}".format(url, response_data))

    except requests.exceptions.Timeout as e:
        print('Timeout exception for url {}: {}'.format(url, e))
        return False, e

    except requests.ConnectionError as e:
        print('ConnectionError for url {}: {}'.format(url, e))
        return False, e

    except requests.HTTPError as e:
        print('HTTPError for url {}: {}'.format(url, e))
        return False, e

    except Exception as e:
        print('in call_webservices error for url {}: {}'.format(url, e))
        return False, e
    if epbm_api:
        return True, response_data
    return True, response_data


def construct_webservice_url(base_url, webservice_url, parameters, use_ssl=False):
    """
        @function: construct_webservice_url
        @createdBy: Manish Agarwal
        @createdDate: 05/11/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 05/11/2016
        @type: function
        @param: dict
        @purpose - construct GET request url
        @input - 'getcanisterinfo', {"robot_id": 6}

        @output - "http://localhost:10008/getcanisterinfo?robotid=6

    """
    if parameters:
        assert ((type(parameters) == dict) or (type(parameters) == OrderedDict))
    assert (webservice_url is not None)
    url = None
    if use_ssl:
        connection_adapter = 'https://'
    else:
        connection_adapter = 'http://'
    try:
        url = connection_adapter + base_url + webservice_url + "?"
        if parameters:
            for key, value in list(parameters.items()):
                url += key + "=" + str(value) + "&"
    except TypeError as e:
        raise TypeError(e)

    return url[:-1]


def convert_quantity_reverse(qty, is_total_quantity):
    if qty == 0.0:
        return 0
    if is_total_quantity:
        return qty * 1000  # if converting total quantity in file
    else:
        return qty * 100  # if converting morning, noon, eve, bed quantity in file


def convert_quantity(qty, is_total_quantity):
    if qty == 0:
        return 0
    if is_total_quantity:
        return qty / 1000  # if converting total quantity in file
    else:
        return qty / 100  # if converting morning, noon, eve, bed quantity in file
    # if qty == 500:
    #     return 0.5

    # if qty == 50:
    #     return 0.5

    # if qty == 150:
    #     return 1.5

    # if qty == 1500:
    #     return 1.5

    # if qty == 250:
    #     return 2.5

    # if qty == 2500:
    #     return 2.5

    # qty = str(qty)
    # mantissa = qty[0:1]
    # exponent = qty[-1]

    # return float(mantissa + "." + exponent)  # keep code as it might be useful if format of file was decided on this


def convert_time(_time):
    assert (len(_time) == 4)
    try:
        return datetime.time(int(_time[0:2]), int(_time[2:4]))
    except ValueError:
        return None


def copy_file(source_path, destination_path):
    """
        copies the file from the source path to the destination path
    """
    shutil.copy(source_path, destination_path)


def move_file(source_path, destination_path):
    """
    moves the file from the source path to the destination path
    """
    shutil.move(source_path, destination_path)


def create_nested_json(key, source):
    result = {'name': key, 'children': []}
    for key, value in source.items():
        if isinstance(value, list):
            result['children'] = value
        else:
            child = create_nested_json(key, value)
            result['children'].append(child)

    return result


def print_info(msg, *args):
    """
        Prints the given info into log file
        TODO: needs fix on printing error traces
    """
    try:
        msg = msg.__str__()
        if args is None:
            print(msg)
        else:
            print(str(msg) % args)
    except Exception as ex:
        print(ex)


try:
    import win32api
except ImportError:
    pass

try:
    import win32print
except ImportError:
    pass

import subprocess
import os


def send_to_printer(source_path, printer):
    """@type: function

                @function: incorrect_type
                @createdBy: Manish Agarwal
                @createdDate: 7/23/2015
                @lastModifiedBy: Manish Agarwal
                @lastModifiedDate: 08/12/2015
                   @param: str
                @purpose - returns incorrect type message
    """
    # This is where you would specify the path to your pdf
    pdf = source_path  # "pack_labels\\hello.pdf"

    # Dynamically get path to AcroRD32.exe
    AcroRD32Path = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, 'Software\\Adobe\\Acrobat\Exe')

    acroread = AcroRD32Path

    # The last set of double quotes leaves the printer blank, basically defaulting
    # to the default printer for the system.

    cmd = '{0} /N /T "{1}" "{2}"'.format(acroread, pdf, printer)

    # Open command line in a different process other than ArcMap
    proc = subprocess.Popen(cmd)

    import time
    time.sleep(5)

    # Kill AcroRD32.exe from Task Manager
    os.system("TASKKILL /F /IM AcroRD32.exe")

    import time
    time.sleep(3)


def create_error_notification(msg, car_id=0, pack_id=0):
    return json.dumps({"status": "error", "msg": msg, "car_id": car_id, "pack_id": pack_id})


def create_retry_notification(msg, button_id, car_id, pack_id, action_api=None, args=None, label=""):
    return json.dumps({"status": "retry", "info": msg, "car_id": car_id, "pack_id": pack_id, "id": button_id,
                       "interrupt_id": button_id, "action_api": action_api, "args": args, "label": label})


def encode_dict(d, codec='utf8'):
    ks = d.keys()
    for k in ks:
        val = d.pop(k)
        if isinstance(val, unicode):
            val = val.encode(codec)
        elif isinstance(val, dict):
            val = encode_dict(val, codec)
        elif isinstance(val, list):
            for index, item in enumerate(val):
                if isinstance(item, dict):
                    val = encode_dict(item, codec)
                else:
                    val[index] = item.encode(codec)
        if isinstance(k, unicode):
            k = k.encode(codec)

        d[k] = val

    return d


def validate_rfid_checksum(rfid):
    """
    check if the rfid is valid or not by doing the checksum check with the last two bytes.
    """
    rfid = str(rfid)

    if len(rfid) == 32:
        try:
            hex = int(rfid, 16)
            return True

        except ValueError:
            print("Data not in hexadecimal format")
            return False

    else:
        try:
            hex = int(rfid, 16)
        except ValueError:
            print("Data not in hexadecimal format")
            return False

        if not rfid:
            return False

        try:
            from binascii import unhexlify
            rfid = unhexlify(rfid)
            _ord = list(rfid)
            # _ord = [ord(x) for x in rfid]

            if not _ord:
                return False

            _checksum_result = _ord.pop()

            _xor_res = 0
            for item in _ord:
                _xor_res ^= item

            if _xor_res == _checksum_result:
                return True
            else:
                return False
        except TypeError:
            return False
        except UnicodeDecodeError:
            return False


def before_request_handler():
    db.connect()
    return True


def after_request_handler():
    db.close()


def batch(iterable, n=10):
    """
    creates batches of given iterable

    :param iterable:
    :param n: no of items in a batch
    :return: generator
    """
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def get_gtin_from_ndc(ndc_value):
    """
    This function will return the gtin value to be placed in data matrix using the ndc
    :param ndc_value:
    :return:
    """
    ndc_value = "003" + ndc_value

    multiplication_list = [3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3]
    gtin_sum = 0

    if len(ndc_value) == len(multiplication_list):
        for index in range(0, len(ndc_value)):
            multiplied_value = int(ndc_value[index]) * multiplication_list[index]
            gtin_sum += multiplied_value

        nearest_divisible = int(math.ceil(int(gtin_sum) / 10.0)) * 10

        last_digit = abs(gtin_sum - nearest_divisible)

        ndc_value = ndc_value + str(last_digit)

        return ndc_value

    else:
        return None


def convert_11_digit_ndc_to_10(ndc_value, ndc_fi_value):
    """
    :param ndc_value:
    :return:
    """
    if int(ndc_fi_value) not in NDCFI_LOCATION_DICT.keys():
        return None
    else:
        location_to_remove = NDCFI_LOCATION_DICT[int(ndc_fi_value)]

        ndc_10 = ndc_value[:location_to_remove] + ndc_value[(location_to_remove + 1):]
        return ndc_10


def escape_wildcard(_input):
    """
    Escapes % from string
    :param _input:
    :return: str
    """
    return _input.translate(str.maketrans({'%': r'\%'}))


def escape_wrap_wildcard(x):
    """
    Wraps wildcard(%) around given string after escaping wildcard

    :param x:
    :return: str
    """
    x = escape_wildcard(x)
    return '%' + x + '%'


def log_args_and_response(func):
    """
    Decorator for logging funcion input args and output response, will
    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        try:
            logger.info("Input args for {} - args: {}, kwargs: {}".format(func, args, kwargs))
        except Exception:
            pass
        response = func(*args, **kwargs)
        try:
            logger.info("Output response for {}: {}".format(func, response))
        except Exception:
            pass
        return response

    return wrapper


def log_args(func):
    """
    Decorator for logging funcion input args
    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        try:
            logger.debug("Input args for {} - args: {}, kwargs: {}".format(func, args, kwargs))
        except Exception:
            pass
        return func(*args, **kwargs)

    return wrapper

def log_args_and_response_dict(func):
    """
    Decorator for logging funcion input args and output response, will
    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        try:
            logger.info("Input args for {} - args: {}, kwargs: {}".format(func, args, kwargs))
        except Exception:
            pass
        response = func(*args, **kwargs)
        try:
            if type(response) == dict:
                for key, value in response.items():
                    logger.info("Output response for {} || key: value {}: {}".format(func, key, value))
            else:
                logger.info("Output response for {}: {}".format(func, response))
        except Exception:
            pass
        return response

    return wrapper


def return_roman_translation(num):
    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)])


def convert_number_to_alphabet(num):
    if 0 < num < 27:
        return chr(num + 64)


def generate_csv_file(file_path, data_list, columns_name_list=None):
    with open(file_path, 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(data_list)

    csvFile.close()


def read_csv_file_data(file_path, delete_file=False):
    data_list = list()
    with open(file_path, 'r') as csvFile:
        reader = csv.reader(csvFile)

        data_list = list(reader)

    csvFile.close()

    for data in data_list:
        if len(data) == 0:
            data_list.remove(data)

    if delete_file:
        os.remove(file_path)
    return data_list


def generate_file(file_data, upload_path):
    upload_file = os.path.join(upload_path, file_data.filename)
    with open(upload_file, 'wb') as out:
        while True:
            data = file_data.file.read(8192)
            if not data:
                break
            out.write(data)
    out.close()

    return upload_file


def perform_file_operations(file_path, file_operation, file_data=None):
    if file_operation == FILE_OPERATIONS["READ"]:
        with open(file_path, 'r+') as f:
            data = f.read()
            f.close()
            return data
    elif file_operation == FILE_OPERATIONS["WRITE"]:
        if file_data is not None:
            with open(file_path, 'w+') as f:
                f.write(file_data)
            return True
        else:
            return False
    elif file_operation == FILE_OPERATIONS["CREATE"]:
        with open(file_path, 'w+') as f:
            pass
        f.close()
        return True
    elif file_operation == FILE_OPERATIONS["DELETE"]:
        os.remove(file_path)
        return True


@log_args_and_response
def get_canister_volume(canister_type=constants.SMALL_CANISTER_CODE):
    if canister_type == constants.SMALL_CANISTER_CODE:
        CANISTER_USABLE_VOLUME = float(
            float(constants.CANISTER_LENGTH * constants.CANISTER_BREADTH * constants.SMALL_CANISTER_HEIGHT) *
            float(constants.CANISTER_USABLE_VOLUME_PERCENT / 100))
    else:
        CANISTER_USABLE_VOLUME = float(
            float(constants.CANISTER_LENGTH * constants.CANISTER_BREADTH * constants.BIG_CANISTER_HEIGHT) *
            float(constants.CANISTER_USABLE_VOLUME_PERCENT / 100))
    return CANISTER_USABLE_VOLUME


@log_args_and_response
def get_max_possible_drug_quantities_in_canister(canister_volume, unit_drug_volume):
    if float(unit_drug_volume) != float(0):
        return int(float(canister_volume) / float(unit_drug_volume))
    return None


def get_current_date_time_millisecond():
    """
        Timestamp to include milli seconds as well
    """
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')


def get_current_modified_datetime():
    created_date = get_current_date_time()
    modified_date = created_date
    return created_date, modified_date


def image_convert(s):
    s = s.replace(".png", ".jpg")
    return s


def difference_between_timestamps(start_time: str, end_time: str) -> int:
    """
    This function returns the difference between 2 timestamps.
    @param start_time:str
    @param end_time: str
    @return: int
    """
    std_format = '%Y-%m-%d %H:%M:%S'
    difference = datetime.datetime.strptime(end_time, std_format) - datetime.datetime.strptime(start_time, std_format)
    return difference.days * 24 * 3600 + difference.seconds


@log_args
def hardware_call_webservice(base_url, webservice_url, parameters, cache=False, headers=None, request_type="GET",
                             use_ssl=False, timeout=None, call_electronics_api=False, odoo_api=False,
                             dump_data=False):
    """
    Method to call hardware webservice without any retry
    @param base_url: str
    @param webservice_url: str
    @param parameters: dict
    @param cache: bool
    @param headers: dict
    @param request_type:
    @param use_ssl: bool
    @param timeout: int
    @param call_electronics_api: bool
    @param odoo_api: bool
    @param dump_data: bool
    @return:
    """
    if request_type == "GET":
        url = construct_webservice_url(base_url, webservice_url, parameters, use_ssl=use_ssl)
    else:
        url = base_url + webservice_url
    print("url", url)
    if use_ssl:
        connection_adapter = 'https://'
    else:
        connection_adapter = 'http://'
    # Connect to the web service
    try:
        if request_type == "GET":
            data = requests.get(url, headers=headers, timeout=timeout, verify=False)
        elif request_type == "POST" and not odoo_api:
            data = requests.post(connection_adapter + base_url + webservice_url, data={"args": parameters},  # TODO
                                 timeout=timeout, verify=False)
        elif request_type == "POST" and odoo_api:
            url = connection_adapter + base_url + webservice_url
            data = requests.post(connection_adapter + base_url + webservice_url, data=parameters,
                                 timeout=timeout, headers=headers, verify=False)

        if call_electronics_api:
            response_data = data.content.decode('utf8').replace("'", '"')
            response_data = json.loads(response_data)
        else:
            response_data = json.loads(str(data.content, 'utf-8'))

        print("response data for url {}: {}".format(url, response_data))

    except requests.exceptions.Timeout as e:
        print('Timeout exception for url {}: {}'.format(url, e))
        return False, e

    except requests.ConnectionError as e:
        print('ConnectionError for url {}: {}'.format(url, e))
        return False, e

    except requests.HTTPError as e:
        print('HTTPError for url {}: {}'.format(url, e))
        return False, e

    return True, response_data


def get_datetime():
    """
    Returns utc datetime

    :return: datetime
    """
    return datetime.datetime.utcnow()


@log_args_and_response
def get_utc_time_offset_by_time_zone(time_zone):
    """"
    Function to get UTC time offset by timezone
    `i.e` : timezone = 'US/Pacific' ==> offset = -0700 or -0800
            timezone = 'Asia/Kolkata' ==> offset = +0530
    @param time_zone:
    """
    # get offset by timezone
    offset = datetime.datetime.now(pytz.timezone(time_zone)).strftime('%z')

    # utc_time_zone_offset = -07:00
    utc_time_zone_offset = "".join(offset[0:3]) + ":" + "".join(offset[3:])

    return utc_time_zone_offset


@log_args_and_response
def get_date_time_by_offset(offset):
    """"

    @param time_zone:
    """
    offset_parts = offset.split(':')
    offset_hours = int(offset_parts[0])
    offset_minutes = int(offset_parts[1])
    utc_time = datetime.datetime.utcnow()
    offset_seconds = (offset_hours * 3600) + (offset_minutes * 60)
    offset_timedelta = datetime.timedelta(seconds=offset_seconds)
    current_datetime = utc_time + offset_timedelta

    return current_datetime.strftime("%Y-%m-%d %H:%M:%S")

@log_args_and_response
def last_day_of_month(any_day):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - datetime.timedelta(days=next_month.day)


@log_args_and_response
def get_the_content_type_of_the_uploaded_file(file_obj):
    try:
        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(file_obj.file.read())
        file_obj.file.seek(0)  # back to the beginning of the file
        return content_type
    except Exception as e:
        raise e


@log_args_and_response
def convert_date_format(date_str):
    try:
        return f"{date_str[6:10] }-{date_str[0:2] }-{date_str[3:5]}"
    except Exception as e:
        raise e
