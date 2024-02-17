'''
# for now still in experimental and R&D phase.


import logging
from multiprocessing import Pool

from aiohttp import ClientSession, errors

import asyncio
import settings
from dosepack.utilities.utils import construct_webservice_url, retry

logger = logging.getLogger("root")


class AsyncFactory:
    """
        @class: AsyncFactory
        @createdBy: Manish Agarwal
        @createdDate: 05/28/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 05/28/2016
        @type: function
        @param: dict
        @purpose - Async class to make function asynchronous
        @input -  async = AsyncFactory(func, callback_function)

        @output - {"id": None}

    """
    def __init__(self, func, args, cb_func):
        self.func = func
        self.cb_func = cb_func
        self.args = args
        self.pool = Pool()

    def call(self):
        print(self.pool.apply_async(self.func, args=self.args, callback=self.cb_func))
        self.pool.close()
        self.pool.join()


def default_callback_function(result):
    """
        @function: default_callback_function
        @createdBy: Manish Agarwal
        @createdDate: 05/28/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 05/28/2016
        @type: function
        @param: dict
        @purpose - default callback function
        @input - gets the async function response and
                    prints the result

        @output -

    """
    print("Default Callback function called for the webservice: ")
    print(result)


async def call_webservice(base_url, webservice_url, parameters, callback):
    async with ClientSession() as session:
        try:
            async with session.get(construct_webservice_url(base_url, webservice_url, parameters)) as response:
                response = await response.read()
                callback_response = await callback(response)
                return True, callback_response
        except errors.ClientConnectionError as e:
            return False, e


async def print_response(response):
    print("Got response")
    print(response)
    return "ok"


loop = asyncio.get_event_loop()

import sys


def show_sizeof(x, level=0):
    print("\t" * level, x.__class__, sys.getsizeof(x), x)

    if hasattr(x, '__iter__'):
        if hasattr(x, 'items'):
            for xx in x.items():
                show_sizeof(xx, level + 1)
        else:
            for xx in x:
                show_sizeof(xx, level + 1)

loop.run_until_complete(call_webservice(settings.LOCAL_URL_IPS, settings.PHARMACY_FINALIZE_PACK_URL,
                                        {'batchlist': '1,2'}, print_response))
loop.run_until_complete(call_webservice(settings.LOCAL_URL_IPS, settings.PHARMACY_UPDATE_ALT_DRUG_URL,
                                        {'batchlist': '1,2'}, print_response))
loop.run_until_complete(call_webservice(settings.LOCAL_URL_IPS, settings.PHARMACY_STORE_RX_FILE_URL,
                                        {'batchlist': '1,2'}, print_response))
loop.run_until_complete(call_webservice(settings.LOCAL_URL_IPS, settings.PHARMACY_FINALIZE_PACK_URL,
                                        {'batchlist': '1,2'}, print_response))
'''

