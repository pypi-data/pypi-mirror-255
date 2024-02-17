import json

import cherrypy

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.prn_vial_filling import save_filled_rx, get_filled_rx_data, get_filled_rx_details_of_patient, \
    send_drugs_to_elite, get_suggested_pack_count, send_slot_wise_filled_rx_data_to_ips, delete_pack, sync_queue_type, \
    sync_delivery_date


class GetFilledRx(object):
    """
        This class contains the methods that fetch the data of Filled On Demand Rx
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, PageIndex, PageSize, filters=None, sort_fields=None):
        paginate = {"page_number": PageIndex, "number_of_rows": PageSize}
        filter_fields = {}
        if filters:
            filter_fields = json.loads(filters)
        if sort_fields:
            sort_fields = json.loads(sort_fields)
        return get_filled_rx_data(paginate, filter_fields, sort_fields)


class OtherRxFilling(object):
    """
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        """
        Save Filled PRN, On Demand drugs in DB.
        If package is pack, it will be saved as normal pack
        If package is Vial or other, we will create single slot pack structue and save
        :param kwargs:
        :return:
        """
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], save_filled_rx
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class GetFilledRxDetails(object):
    """
        This class contains the methods that fetch the data of Filled On Demand Rx
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, patient_id, FromDate=None, ToDate=None):
        if patient_id is None or FromDate is None or ToDate is None:
            return error(1001, "Missing Parameter(s)")
        return get_filled_rx_details_of_patient(patient_id, FromDate, ToDate)


class GetSuggestedPackCount(object):
    """
        This API suggests pack count to be used based on pack type, day supply and capacity of container
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, pack_type, qty, capacity=None, pack_count=None):
        if not pack_type or not qty:
            return error(1001, "Missing Parameter(s)")
        return get_suggested_pack_count(pack_type, qty, capacity, pack_count)


class EPBMSendDrugsOnOrder(object):
    """
        This class contains the methods that send list of ndc to Elite for order
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        """
        This API send drugs on order received whose qty are not available for On demand Rxs
        :param kwargs:
        :return:
        """
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], send_drugs_to_elite
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class CurrentFilledRxDetails(object):
    """
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        """
        This API sends current filled data which includes filled drug, case, canister, lot number and expiry to IPS for
        caching
        :param kwargs:
        :return:
        """
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], send_slot_wise_filled_rx_data_to_ips
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class DeletePrnPack(object):
    """
    """
    exposed = True

    @cherrypy.tools.json_in()
    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        """
        This API received pack_id as argument which is filled with On Demand Flow and have to be deleted from IPS
        @param kwargs: 
        @return: 
        """"""
        :return:
        """
        data = cherrypy.request.json
        response = delete_pack(data)
        return response


class RetailQueueSync(object):
    """
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        """
        This API received rx_id as argument which is filled with On Retail Flow and queue type is updated from IPS
        @param kwargs: 
        @return: 
        """"""
        :return:
        """
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], sync_queue_type
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class SyncPRNdelivery(object):
    """
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        """
        This API schedules filled PRN packs in DP and IPS
        @param kwargs: 
        @return:
        """
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], sync_delivery_date
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response
