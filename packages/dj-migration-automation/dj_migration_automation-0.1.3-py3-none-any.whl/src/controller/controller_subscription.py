import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.subscription import get_subscription_orders, add_subscription_order, update_subscription_order, \
    get_order_summary, get_consumable_types, get_couriers, add_tracking_info, add_invoice_file, get_consumable_stats, \
    update_used_consumable, get_pack_consumption


class Orders(object):
    """
          @class: GetOrders
          @type: class
          @param: object
          @desc: gets required orders
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, company_id=None, **kwargs):

        args = {
            "from_date": from_date,
            "to_date": to_date,
            "company_id": company_id
        }
        response = get_subscription_orders(args)

        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_subscription_order
            )
        else:
            return error(1001)
        return response


class UpdateOrder(object):
    """
          @class: UpdateOrder
          @type: class
          @param: object
          @desc: updates order details
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_subscription_order
            )
        else:
            return error(1001)

        return response


class OrderSummary(object):
    """
          @class: GetOrderSummary
          @type: class
          @param: object
          @desc: gets order summary
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, order_id=None, company_id=None, **kwargs):

        args = {"order_id": order_id, "company_id": company_id}
        response = get_order_summary(args)

        return response


class ConsumableTypes(object):
    """
          @class: ConsumableTypes
          @type: class
          @param: object
          @desc: gets active consumable type
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, active=None, company_id=None, **kwargs):
        if active == '0':
            active = False
        else:
            active = True
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
        args = {"active": active, "company_id": company_id}
        response = get_consumable_types(args)

        return response


class Couriers(object):
    """
          @class: Couriers
          @type: class
          @param: object
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, **kwargs):

        response = get_couriers()

        return response


class Shipments(object):
    """
          @class: Shipments
          @type: class
          @param: object
          @desc: add shipment tracking information
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_tracking_info
            )
        else:
            return error(1001)
        return response


class InvoiceFile(object):
    """
          @class: InvoiceFile
          @type: class
          @param: object
          @desc: Makes file entry for invoice
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_invoice_file
            )
        else:
            return error(1001)
        return response


class ConsumableStats(object):
    """
          @class: ConsumableStats
          @type: class
          @param: object
          @desc: gets how much consumable used per day
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, month=None, year=None, **kwargs):

        args = {"company_id": company_id, "month": month, "year": year}
        response = get_consumable_stats(args)

        return response


class UpdateUsedConsumable(object):
    """
    updated used consumable in inventory module of dose pack
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, time_zone=None, date=None, **kwargs):

        if company_id is None:
            return error(1001)
        args = {"company_id": company_id, "time_zone": time_zone, "date": date}
        response = update_used_consumable(args)

        return response


class OdooConsumableVerify(object):
    """
    fetch consumption's monthly data day wise and for whole month for odoo verification
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, time_zone=None, from_date=None, to_date=None, **kwargs):

        if company_id is None:
            return error(1001)
        args = {"company_id": company_id, "time_zone": time_zone, "from_date": from_date, "to_date": to_date}
        response = get_pack_consumption(args)

        return response
