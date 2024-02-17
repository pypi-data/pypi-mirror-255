import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src import constants
from src.service.canister import send_email_for_ordering_canisters
from src.service.canister_testing import add_canister_testing_data, \
    get_canister_testing_data, get_alternate_canister_testing_data, update_alternate_canister_testing_status_data, \
    get_canister_for_testing, save_canisters_in_product_details, \
    save_old_canister_mapping, update_delivered_canisters, get_current_batch_canisters, \
    update_canister_testing_quantity, skip_canister_testing
from utils.auth_webservices import send_email_for_daily_check_api_failure


class CanisterTesting(object):
    """
    This class contains methods to add and get data to/from Canister Testing Data and Canister Testing Status tables.
    """
    exposed = True

    # @use_database(db, settings.logger)
    # def GET(self, company_id=None, device_id=None):
    #     if company_id is None or device_id is None:
    #         return error(1001, "Missing Parameter(s): company_id or device_id.")
    #     args = {
    #         "company_id": company_id,
    #         "device_id": device_id
    #     }
    #     return get_pending_canister_testing_data(args)

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_canister_testing_data
            )
        else:
            return error(1001)

        return response


class CanisterTestingReport(object):
    """
    This class contains the methods that fetch the report for the Canister Testing
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, device_id=None, paginate=None, filters=None, sort_fields=None, **kwargs):
        if company_id is None or device_id is None:
            return error(1001, "Missing Parameter(s): company_id or device_id.")
        args = {
            "company_id": company_id,
            "device_id": device_id,
        }
        if paginate is None:
            args["paginate"] = {"page_number": 1, "number_of_rows": 1}
        else:
            args["paginate"] = paginate
        if filters:
            args["filter_fields"] = json.loads(filters)
        if sort_fields:
            args["sort_fields"] = json.loads(sort_fields)
        return get_canister_testing_data(args)


class AlternateCanisters(object):
    """
    This class contains methods to get data from Canister Testing Status tables for alternate canisters.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], get_alternate_canister_testing_data
            )
        else:
            return error(1001)

        return response


class AlternateCanisterTesting(object):
    """
    This class contains methods to update data of Canister Testing Status tables for alternate canisters.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_alternate_canister_testing_status_data
            )
        else:
            return error(1001)

        return response


class GetCanisterDataForTesting(object):
    """
    This class contains the methods that fetch the data of Canisters for Testing
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, paginate=None, filters=None):
        if paginate is None:
            paginate = {"page_number": 1, "number_of_rows": 1}
        try:
            if filters:
                filter_fields = json.loads(filters)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id")
        return get_canister_for_testing(paginate, filter_fields)


class StoreShippedCanisters(object):
    """
    This class contains the methods that store the canisters in ProductDetails table received from odoo when shipped
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id: [int] = None, time_zone: [str] = None, ):
        if company_id is None or time_zone is None:
            send_email_for_daily_check_api_failure(time_zone=time_zone,
                                                   error_details="Missing Parameter(s): company_id or time_zone",
                                                   api_name=constants.DAILY_SHIPPED_CANISTERS_CHECK, company_id=company_id)
            return error(1001, "Missing Parameter(s): company_id or time_zone or system_id_list.")

        return save_canisters_in_product_details(company_id=company_id, time_zone=time_zone)


class UpdateDeliveredCanisters(object):
    """
    This class contains the methods that set the delivery_date of products when delivered and send notification
    for testing
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id: [str] = None, time_zone: [str] = None, ):
        if company_id is None or time_zone is None:
            send_email_for_daily_check_api_failure(company_id=company_id, time_zone=time_zone,
                                                   error_details="Missing Parameter(s): company_id or time_zone",
                                                   api_name=constants.DAILY_DELIVERED_CANISTERS_CHECK)
            return error(1001, "Missing Parameter(s): company_id or time_zone or system_id_list.")

        return update_delivered_canisters(company_id=company_id, time_zone=time_zone)


class OrderNewCanisters(object):
    """
    This class contains the methods for sending mail for canister orders
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id: [int] = None):

        return send_email_for_ordering_canisters(company_id=company_id)


class SaveOldCanisterMapping(object):
    """
    This class contains the methods that stores the mapping for old and ordered new canister
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], save_old_canister_mapping
            )
        else:
            return error(1001)
        return response


class GetCurrentBatchCanisters(object):
    """
    This class contains the methods that fetch the count of current batch canisters to test with their lot number
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self):
        return get_current_batch_canisters()


class UpdateCanisterQuantityInTesting(object):
    """
    This class contains the methods that update canister quantity while canister testing
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_canister_testing_quantity
            )
        else:
            return error(1001)
        return response


class SkipCanisterTesting(object):
    """
    This class contains the methods that update product status as skipped in PPP screen
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], skip_canister_testing
            )
        else:
            return error(1001)
        return response
