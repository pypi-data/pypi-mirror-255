# -*- coding: utf-8 -*-
"""
    src.validate
    ~~~~~~~~~~~~~~~~

    The central validation framework which includes all the validation rules
    defined. We can use this validation framework as a decorator.To use it:

    @validate(required_fields=["date_from", "date_to"],
          validate_dates=['date_from', 'date_to'], validate_robot_id='robot_id')

    The @validate decorator takes the required fields followed by all the validation
    rules which are defined for the given function.

    Example:
            $ @validate(required_fields=[], validation_rules=[])

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""

import datetime
import json
import warnings
from functools import wraps

from dosepack.error_handling.error_handler import error


def validate(**validation_rules):
    """
        @function: validate_input_arguments
        @createdBy: Manish Agarwal
        @createdDate: 03/18/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 03/18/2016
        @type: decorator
        @param: dict
        @purpose - check if all the input arguments passed to the function are valid
        @input - ('robot_id', 'client_id', function_name='validate_input_arguments', module='parameters')

        @output -

    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            try:
                if isinstance(args[0], dict):
                    dict_input_dict = args[0]
                else:
                    dict_input_dict = args[1]
            except IndexError:
                return error(1006)

            required_fields = validation_rules['required_fields']

            # check if input type is a dict type.If not log
            # the error message and output it.
            if not valid_data_type(dict_input_dict, dict):
                return error(1012)

            # check if the required fields is not empty. If not
            # log the error msg and output it.
            if not required_fields:
                warnings.warn("Required fields list is empty.")

            # check if the input dict is not empty. If not
            # log the error msg and output it.
            if not dict_input_dict:
                return error(1006)

            # check if the input dict has all the required fields. If not
            # log the error msg and output it.
            for item in required_fields:
                if item not in dict_input_dict:
                    return error(1001, "Missing Parameter(s): " + str(item))

            try:
                print(validation_rules['validate_robot_id'])
                # write validate robot_id logic
            except KeyError:
                warnings.warn("validate_robot_id rule does not exists")

            try:
                date_from, date_to = dict_input_dict[validation_rules['validate_dates'][0]], dict_input_dict[validation_rules['validate_dates'][1]]
                status, err = validate_dates(date_from, date_to)
                if not status:
                    return err
            except KeyError:
                warnings.warn("validate_dates rule does not exists")

            try:
                print(validation_rules['validate_pack_id'])
                # write validate robot_id logic
            except KeyError:
                warnings.warn("validate_pack_id rule does not exists")

            try:
                # This validation is to check integer values i.e., [-n,0,n]
                digit_validation_keys = validation_rules.get("integer_validation")
                if digit_validation_keys:
                    for item in digit_validation_keys:
                        if dict_input_dict.get(item):
                            try:
                                # This will raise valueerror or typeerror in case when we try to convert any instance
                                # to integer other than digit
                                item_value = int(dict_input_dict.get(item))
                            except (ValueError, TypeError):
                                return error(1012, " Value of {} must be an integer".format(item))
            except Exception as e:
                warnings.warn("Exception- {} in integer_validation".format(str(e)))

            try:
                # This validation is for 0 and positive integers only.
                non_negative_values = validation_rules.get("non_negative_integer_validation")
                if non_negative_values:
                    for item in non_negative_values:
                        if dict_input_dict.get(item):
                            try:
                                item_value = int(dict_input_dict.get(item))
                                if item_value < 0:
                                    return error(1012, " Value of {} must be a non negative integer".format(item))
                            except (ValueError, TypeError):
                                return error(1012, " Value of {} must be a non negative integer".format(item))
            except Exception as e:
                warnings.warn("Exception- {} while validating non_negative_integer values".format(str(e)))

            return func(*args, **kwargs)

        return wrapper

    return decorator


def valid_data_type(instance, _type):
    return type(instance) == _type


def validate_dates(from_date, to_date):
    try:
        datetime.datetime.strptime(from_date, '%m-%d-%y')
    except ValueError:
        return False, error(1010)

    try:
        datetime.datetime.strptime(to_date, '%m-%d-%y')
    except ValueError:
        return False, error(1010)

    return True, None


def validate_request_args(args, callback):
    try:
        if len(args) == 0:
            response = error(1011)
        else:
            # convert the json input into python dict
            dict_info = json.loads(args)
            print("Input dict", dict_info)
            response = callback(dict_info)
    # on exception return error
    except ValueError as e:
        response = error(1001, e)
    except SyntaxError as e:
        response = error(1001, e)

    return response


def validate_json_in(func):
    """
        @function: validate_request_arguments
        @createdBy: Manish Agarwal
        @createdDate: 03/18/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 03/18/2016
        @type: decorator
        @param: dict
        @purpose - check if all the input arguments passed to the function are valid
        @input - ('robot_id', 'client_id', function_name='validate_input_arguments', module='parameters')

        @output -

    """
    def wrapper(*args, **kwargs):
        try:
            json.loads(args[1])
        except TypeError:
            raise TypeError("Input JSON not in valid format")
        return func(*args, **kwargs)
    return wrapper