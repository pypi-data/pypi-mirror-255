# -*- coding: utf-8 -*-
"""
    comm.pharmacy_software
    ~~~~~~~~~~~~~~~~

    This module contains the connection details to send information to the pharmacy software.
    The protocol followed is through web service requests. The currently supported method for
    making web service calls  is GET. The default response format that is received from the
    pharmacy software is : {'response': {'status': 'OK', 'errorcode': '', 'errormessage': ''}}
    Here the status defines if the webservice call made is success or failure.

    Example:
        $

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""

from dosepack.utilities.utils import call_webservice, get_datetime
from src.exceptions import PharmacySoftwareCommunicationException, PharmacySoftwareResponseException
import json
import settings
import logging
import threading

logger = logging.getLogger("root")


def acknowledge():
    raise NotImplementedError("Not Support Currently")


def set_authorization_headers(token, auth_type=None, preset_headers=None):
    """
    Returns dict for headers for IPS comm

    :param token: Token
    :param auth_type: Authentication type
    :param preset_headers: To update preset headers
    :return: dict
    """
    if not token:
        return None

    headers = dict()
    if preset_headers:
        headers = preset_headers

    #  add different auth type if needed
    if auth_type is None:  # IPS robot webservice uses token directly without any auth type
        headers.update({'Authorization': token})
        return headers

    return None


def send_data(base_url, webservice_url, parameters, counter, _async=False, response_handler=None, pack_header_id=None,
              checks=False, token=None, timeout=None, request_type="GET", use_ssl = settings.IPS_ON_SSL, ips_api=False):
    """ Makes the webservice call based on the request url and
    parameters. It also takes async as optional parameter to make
    the type of request call.

    Args:
        base_url (str): The base url to make the webservice call
        webservice_url (str): The webservice url to serve the purpose
        parameters (dict): The url parameters
        async (bool): To indicate if the webservice call to be made is synchronous or asynchronous
        response_handler (func) The response handler function after webservice is called
        counter(int) - To keep track the number of web services calls made.
        timeout (tuple) - Tuple of (connection timeout, read timeout) for web service call
        request_type (str) -  HTTP Method name

    Returns:
        json : Response of the webservice call made

    Examples:
        >>> send_data()
        []

    """
    # if checks:
    #     flag = PackLifeCycle.db_check_packs(pack_header_id)
    #     while not flag and counter < settings.MAX_RETRIES:
    #         time.sleep(3 ** (counter+1))
    #         flag = PackLifeCycle.db_check_packs(pack_header_id)
    #         counter += 1
    #     if counter == settings.MAX_RETRIES:
    #         logger.debug(threading.currentThread().getName() + "Maximum retries for finalizepackdata exceeded. Exiting.")
    #         return
    headers = set_authorization_headers(token)
    start_time = get_datetime()
    status, response_data = call_webservice(base_url, webservice_url, parameters, headers=headers,
                                            use_ssl=use_ssl, timeout=timeout,
                                            request_type=request_type, ips_api=ips_api)
    end_time = get_datetime()
    logger.debug("Calling webservice: {} {} {} time taken: {}".format(base_url, webservice_url, parameters,
                                                                      (end_time - start_time).total_seconds()))
    if not status:
        raise PharmacySoftwareCommunicationException("Maximum retries exceeded for Pharmacy Software Communication")

    if response_handler:
        response_handler(response_data)
    else:
        if is_response_valid(response_data, ips_api):
            return response_data
        else:
            raise PharmacySoftwareResponseException("Invalid response received from the pharmacy software for the webservice call.")


def default_response_handler(response):
    """ Handles the response which it gets after the webservice call is made.

    Args:
        response (json): Thr response received from the webservice call being made

    Returns:
        boolean : True if response is valid otherwise False

    Examples:
        >>> default_response_handler()
        []

    """
    logger.debug(threading.currentThread().getName() + "response handler called")
    logger.debug(threading.currentThread().getName() + str(response))


def parse_response(response, response_format="json"):
    """ Take the webservice response and parses it according to the
    response format provided.

    Args:
        response (str): The base url to make the webservice call
        response_format (str): The format in which the response is received.

    Returns:
        json : Parsed Response

    Raises:
        Not Implemented Error: If the response format is other than json.

    Examples:
        >>> parse_response()
        []

    """
    if response:
        if response_format == "json":
            parsed_response = json.loads(response)
            return parsed_response
        else:
            raise NotImplementedError("Other"
                                      " response format not supported currently.")
    return response


def is_response_valid(response, ips_api=None):
    """ Take the webservice response and checks if the status code
    of the received response is valid or not valid.

    Args:
        response (json): The response received from webservice

    Returns:
        boolean : True if the status code is ok otherwise False

    Raises:
        KeyError: If the status code is present in parse response.

    Examples:
        >>> is_response_valid()
        True

    """
    if not ips_api:
        try:
            logger.info("is_response_valid - {}".format(response))
            status = response['response']['status']
        except KeyError:
            return False

        if status.upper() == 'OK':
            return True
        return False
    else:
        logger.info("is_response_valid - {}".format(response))
        if response['status'] == "success":
            return True

def alt_drug_response_handler(response, pack_id_list=None, drug_id_list=None, alt_drug_id_list=None):
    """ Take the webservice response and updates the table based on the response
    received.

    Args:
        response (json): The response received from webservice
        pack_id_list (list): The list of pack ids to be updated
        drug_id_list (list) The  list of drug ids to be updated
        alt_drug_id_list (list) The  list of alt drug ids to be updated

    Returns:
        None

    Examples:
        >>> alt_drug_response_handler()
        None

    """
    logger.debug(threading.currentThread().getName() + "alternate drug update response handler called")
    # if is_response_valid(response):
    #     update_info = {"IPS_update_alt_drug": True}
    # else:
    #     update_info = {"IPS_update_alt_drug": False, "IPS_update_alt_drug_error": response["response"]["errormessage"]}
    # response = SlotTransaction.db_update(pack_id_list, drug_id_list, alt_drug_id_list, update_info)
    logger.info(response)

