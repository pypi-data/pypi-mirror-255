import json

import cherrypy

import settings
import logging
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.canister_testing import activate_canister, delete_canister, delete_multiple_canister
from src.service.canister_recommendation import add_skipped_canister, get_analysis_data, update_analysis_data, \
    flow_handler
from src.service.pack_distribution import delete_reserved_canister, get_alternate_canister_for_batch, \
    update_pack_analysis_canisters, run_recommendations
from src.service.canister import get_canister_data_by_drawer_id, update_canister_type, adhoc_register_canister, \
    _add_canister_info, remove_canister, update_canister, adjust_canister_quantity_v3, adjust_canister_quantity_in_bulk, \
    adjust_quantity_v2, get_canister, get_canister_by_canister_code, update_canisters_by_rfid, \
    get_canister_details_by_rfid, get_canister_by_location_updates, get_canister_location_by_rfid, get_empty_locations, \
    get_canister_details_by_device_id, get_canister_replenish_info, add_canister_drawer, get_canister_drawers, \
    update_canister_drawer, delete_canister_drawer, get_canister_info_v2, get_drug_data_by_company_id, \
    update_canister_drug_id_based_on_rfid, get_empty_location_in_inventory, get_canister_location_in_inventory, \
    get_csr_drawer_rfids, get_available_locations, \
    get_canister_data_by_serial_number, update_canister_category, get_canisters_per_drawer, get_drug_active_canister, \
    discard_expired_canister_drug, get_expired_drug_history, get_canisters_by_pack_ndc, check_valid_canister, \
    order_canisters, get_canister_order_history
from src.service.refill_device import update_canister_quantity
from src.service.test_pack import get_canisters

logger = logging.getLogger("root")


class CanisterDataByDrawer(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, drawer_id, company_id, device_id):
        """
        @param drawer_id: integer
        @param device_id: integer
        @param company_id: integer
        @desc: To obtain canister data using drawer_id, company_id and device_id
        @return: json
        """
        logger.debug("In Class CanisterDataByDrawerId")
        if drawer_id is None or company_id is None or device_id is None:
            return error(1001, "Missing Parameter(s): drawer_id or company_id or device_id")

        response = get_canister_data_by_drawer_id(drawer_id, company_id, device_id)
        return response


class UpdateCanisterType(object):
    """
    This class contains methods to update canister type in canister_master table.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_canister_type
            )
        else:
            return error(1001)

        return response


class DeleteCanister(object):
    """
          @class: DeleteCanister
          @type: class
          @param: object
          @desc:  delete the canister with the given canister_id,
                  device_id and system_id.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], delete_canister
            )
        else:
            return error(1001)

        return response


class DeleteMultipleCanister(object):
    """
          @class: DeleteCanister
          @type: class
          @param: object
          @desc:  delete the canister with the given canister_id,
                  device_id and system_id.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], delete_multiple_canister
            )
        else:
            return error(1001)

        return response


class AdhocRegisterCanister(object):
    """
    Register canisters for V#
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], adhoc_register_canister
            )
        else:
            return error(1001)

        return response


class AddCanister(object):
    """
          @class: AddCanister
          @type: class
          @param: object
          @desc:  add a new canister with fields provided.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], _add_canister_info
            )

        else:
            return error(1001)

        return response


class RemoveCanister(object):
    """
    Sets canister number 0 and robot id NULL for given canister id
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], remove_canister
            )
        else:
            return error(1001)
        return response


class ActivateCanister(object):
    """
             @class: ActivateCanister
             @type: class
             @param: object
             @desc:  activate the canister with the given rfid,canister_id

       """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], activate_canister
            )
        else:
            return error(1001)

        return response


class UpdateCanister(object):
    """
          @class: UpdateCanister
          @type: class
          @param: object
          @desc:  update the canister with the fields provided.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_canister
            )
        else:
            return error(1001)

        return response


class AdjustCanisterQuantity(object):
    """
          @class: AdjustCanisterQuantity
          @type: class
          @param: object
          @desc:  Adjusts a single canister quantity in a given system.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], adjust_canister_quantity_v3
            )
        else:
            return error(1001)

        return response


class AdjustCanisterQuantityInBulk(object):
    """
          @class: AdjustCanisterQuantityInBulk
          @type: class
          @param: object
          @desc:  adjust quantity for multiple canisters at once
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], adjust_canister_quantity_in_bulk)
        else:
            return error(1001)

        return response


class AdjustQuantity(object):
    """
          @class: AdjustCanisterQuantityInBulk
          @type: class
          @param: object
          @desc:  adjust quantity for multiple canisters at once
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], adjust_quantity_v2)
        else:
            return error(1001)

        return response


class Canister(object):
    """
          @class: Canisters
          @type: class
          @param: object
          @desc:  get the canister information for the given canister id
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id, canister_id=None, rfid=None, system_id=None, **kwargs):
        if canister_id is None and rfid is None:
            return error(1001, "Missing Parameter(s): canister_id and rfid.")

        response = get_canister(company_id, canister_id, rfid=rfid, system_id=system_id)

        return response


class GetCanisterByCanisterCode(object):
    """
          @class: GetCanisterByCanisterCode
          @type: class
          @param: object
          @desc:  get the canister information for the given robot id and system id
    """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, canister_code=None, **kwargs):
        if canister_code is None:
            return error(1001, "Missing Parameter(s): canister_code.")
        args = {"canister_code": canister_code}
        response = get_canister_by_canister_code(args)

        return response


class UpdateCanisterV2(object):
    """
    Updates canister location and robot id based on rfids
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_canisters_by_rfid
            )
        else:
            return error(1001)

        return response


class GetCanisterDetailsByRfid(object):
    """
          @class: GetCanisterDetailsByRfid
          @type: class
          @param: object
          @desc:  get the canister information for the given  rfid and system id.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, rfid=None, company_id=None, **kwargs):
        # check if input argument kwargs is present
        if rfid is None or company_id is None:
            return error(1001, "Missing Parameter(s): rfid or company_id.")
        try:
            rfid = rfid.split(',')

            dict_rfid_info = {
                "company_id": company_id,
                "rfid": rfid
            }
            dict_rfid_info.update(kwargs)
            response = get_canister_details_by_rfid(dict_rfid_info)
        except Exception as ex:
            response = json.dumps(
                {"error": str(ex), "status": settings.FAILURE}
            )

        return response


class CanisterByLocationChange(object):
    """ Controller to provide canister data by location updates """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, device_id=None, system_id=None, timestamp=None, **kwargs):
        if device_id is None or system_id is None:
            return error(1001, 'Missing Parameter(s): device_id or system_id.')

        args = {'device_id': device_id, 'system_id': system_id, 'timestamp': timestamp}
        args.update(**kwargs)
        response = get_canister_by_location_updates(args)

        return response


class GetCanisterLocationByRfid(object):
    """
          @class: GetCanisterLocationByRfid
          @type: class
          @param: object
          @desc:  get the canister location for the given  rfid.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, rfid=None, **kwargs):
        # check if input argument kwargs is present

        if rfid is None:
            return error(1001, 'Missing Parameter(s): rfid.')

        try:
            dict_rfid_info = {"rfid": rfid}
            response = get_canister_location_by_rfid(dict_rfid_info)
        except Exception as ex:
            response = json.dumps(
                {"error": str(ex), "status": settings.FAILURE}
            )

        return response


class GetEmptyLocations(object):
    """
          @class: GetEmptyLocations
          @type: class
          @param: object
          @desc:  get all the empty canister locations for a given device
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, drawer_number=None, device_type_id=None, system_id=None,
            quadrant=None, is_mfd=0, **kwargs):
        if company_id is None:
            return error(1000, "Missing Parameter: Company id")
        try:
            # convert drawer_number param to list for data
            if drawer_number is not None:
                drawer_number = eval(drawer_number)
            data = {"device_id": device_id,
                    "company_id": company_id,
                    "drawer_number": drawer_number,
                    "device_type_id": device_type_id,
                    "system_id": system_id,
                    "is_mfd": int(is_mfd),
                    "quadrant": quadrant}
            response = get_empty_locations(data)
        except Exception as ex:
            response = json.dumps(
                {"error": str(ex), "status": settings.FAILURE}
            )

        return response


class GetCanisterDetailsByRobotId(object):
    """
        @class: GetCanisterDetailsByRobotId
        @createdBy: ---
        @createdDate: ---
        @type: class
        @param: object
        @desc: Get canister details
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, device_id=None, system_id=None, **kwargs):
        if device_id is None or system_id is None:
            return error(1001, "Missing Parameter(s): device_id or system_id.")

        response = get_canister_details_by_device_id(
            device_id, system_id
        )

        return response


class CanisterReplenish(object):
    """
    returns canister replenish data in GET and update canister quantity in POST
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, **kwargs):
        if not company_id:
            return error(1001, "Missing Parameter(s): company_id.")
        response = get_canister_replenish_info(company_id, kwargs)
        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_canister_quantity
            )
        else:
            return error(1001)

        return response


class CanisterDrawer(object):
    """
        @class: CanisterDrawer
        @type: class
        @param: object
        @desc:  adds and retries canister drawer
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], add_canister_drawer)
            return response
        else:
            return error(1001)

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, device_id=None, **kwargs):
        if device_id is None:
            return error(1001, "Missing Parameter(s): device_id.")

        response = get_canister_drawers(device_id)
        return response


class UpdateCanisterDrawer(object):
    """
        @class: UpdateCanisterDrawer
        @type: class
        @param: object
        @desc:  updates canister drawer
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_canister_drawer)
        else:
            return error(1001)
        return response


class DeleteCanisterDrawer(object):
    """
        @class: UpdateCanisterDrawer
        @type: class
        @param: object
        @desc:  deletes canister drawer
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], delete_canister_drawer)
            return response
        else:
            return error(1001)


class GetCanisterInfoV2(object):
    exposed = True

    # @authenticate(settings.logger)  # INFO removing authentication to allow Robot Code
    @use_database(db, settings.logger)
    def GET(self, company_id=None, filters=None, sort_fields=None, paginate=None, replenish_canister_flag=0,
            records_from_date=None, manual_search=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id")
        args = {"company_id": company_id,
                "replenish_canister_flag": int(replenish_canister_flag)
                }
        try:

            if paginate is not None:
                args["paginate"] = json.loads(paginate)
            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
            if records_from_date:
                args["records_from_date"] = str(records_from_date)
            if manual_search:
                args["manual_search"] = json.loads(manual_search)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        try:
            response = get_canister_info_v2(args)
        except Exception as ex:
            print(ex)
            return error(1001, "No record found for the given parameters.")

        return response


class GetDrugDataByCompanyId(object):
    """
    Get data about drug whose at least 1 canister is registered for given company id
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, limit=-1, drug_name=None, ndc=None, lot_number=None, page_no=None,
            sort_by_use=0, **kwargs):
        if not company_id:
            return error(1001, "Missing Parameter(s): system_id.")

        if not limit or not page_no:
            return error(1020, 'Missing key(s) in paginate.')

        required_dict = {"limit": limit, "company_id": company_id,
                         "drug_name": drug_name, "ndc": ndc, "lot_number": lot_number, "page_no": page_no,
                         "sort_by_use": sort_by_use}
        response = get_drug_data_by_company_id(required_dict)
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class CanisterDrugIdUpdate(object):
    """
        @class: UpdateCanisterDrawer
        @type: class
        @param: object
        @desc:  deletes canister drawer
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_canister_drug_id_based_on_rfid)
            return response
        else:
            return error(1001)


class EmptyLocation(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, required_locations_count=1, ndc=None):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args_dict = {"company_id": company_id, "required_locations_count": required_locations_count, "ndc": ndc}

        response = get_empty_location_in_inventory(args_dict)
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class CanisterLocation(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, canister_id_list=None, company_id=None, drug_id_list=None):

        if company_id is None or (canister_id_list is None and drug_id_list is None):
            return error(1001, "Missing Parameter(s): company_id or (canister_id_list and drug_id_list).")

        formatted_canister_id_list = list()
        formatted_drug_id_list = list()

        if canister_id_list:
            formatted_canister_id_list = list(map(lambda x: int(x), canister_id_list.split(',')))
        elif drug_id_list:
            formatted_drug_id_list = list(map(lambda x: int(x), drug_id_list.split(',')))

        if len(formatted_canister_id_list) == 0 and len(formatted_drug_id_list) == 0:
            return error(1001, "Missing Parameters.")

        args_dict = {"company_id": company_id, "canister_id_list": formatted_canister_id_list,
                     "drug_id_list": formatted_drug_id_list}

        response = get_canister_location_in_inventory(args_dict)
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class GetRfidData(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, csr_id_list=None, drawer_number_list=None, company_id=None, location_number_list=None):
        if drawer_number_list is None or csr_id_list is None or company_id is None or location_number_list is None:
            return error(1001, "Missing Parameter(s): drawer_number_list or csr_id_list or company_id or "
                               "location_number_list.")

        drawer_numbers = drawer_number_list.split(',')
        drawer_number_list = list(map(lambda x: int(x.split("-")[1]), drawer_number_list.split(',')))

        location_number_list = list(map(lambda x: int(x), location_number_list.split(',')))
        csr_id_list = list(map(lambda x: int(x), csr_id_list.split(',')))
        args_dict = {"csr_id_list": csr_id_list, "company_id": int(company_id),
                     'drawer_number_list': drawer_number_list,
                     'location_number_list': location_number_list, 'drawer_numbers': drawer_numbers}

        response = get_csr_drawer_rfids(csr_data=args_dict)

        return response


class GetRegisteredCanisterData(object):
    """
        @class: GetRegisteredCanisterData
        @type: class
        @param: object
        @desc:  Fetches Canister Data from Odoo based on production label.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, canister_serial_number=None, skip_testing=None, company_id=None, **kwargs):
        if not canister_serial_number or not company_id:
            return error(1001, "Missing Parameter(s): company_id or serial_number.")

        response = get_canister_data_by_serial_number(canister_serial_number=canister_serial_number,
                                                      company_id=company_id, skip_testing=skip_testing)
        return response


class UpdateCanisterCategory(object):
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_canister_category)
            return response

        else:
            return error(1001)


class GetAvailableLocations(object):
    """
          @class: GetEmptyLocations
          @type: class
          @param: object
          @desc:  To get all empty or unreserved locations where canister that is required in batch can be placed
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, device_id=None, company_id=None, device_type_id=None, system_id=None, drawer_number=None,
            quadrant=None, canister_id=None, batch_id=None, location_count=None, paginate=None, reserved_locations=None,
            is_mfd=False, both_canister=False, **kwargs):
        if company_id is None:
            return error(1000, "Missing Parameter: Company id")
        try:
            if drawer_number:
                drawer_number = eval(drawer_number)

            if paginate:
                paginate = eval(paginate)

            if is_mfd:
                is_mfd = eval(is_mfd)
            if both_canister:
                both_canister = eval(both_canister)

            data = {"device_id": device_id,
                    "company_id": company_id,
                    "device_type_id": device_type_id,
                    "system_id": system_id,
                    "drawer_number": drawer_number,
                    "canister_id": canister_id,
                    "quadrant": quadrant,
                    "location_count": location_count,
                    "paginate": paginate,
                    "is_mfd": is_mfd,
                    "reserved_locations": reserved_locations,
                    "both_canister": both_canister}
            response = get_available_locations(data)

        except Exception as ex:
            return error(0, ex)

        return response


class GetCanisters(object):
    """
        @class: GetCanisters
        @createdBy: ---
        @createdDate: ---
        @type: class
        @param: object
        @desc: Gives the canister information for the given robot.

    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, device_id=None, system_id=None, **kwargs):
        if not company_id:
            return error(1001, "Missing Parameter(s): company_id.")
        if system_id:
            system_id = int(system_id)

        if device_id:  # to get multiple robot's canisters
            device_ids = device_id.split(',')
        else:
            device_ids = None

        response = get_canisters(system_id, device_ids, company_id)

        return response


class SkippedCanister(object):
    """
    Controller for skipped canister transfers in pack pre-processing
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if 'args' in kwargs:
            response = validate_request_args(kwargs['args'], add_skipped_canister)
            return response
        else:
            return error(2001)


class DeleteReservedCanister(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], delete_reserved_canister
            )
        else:
            return error(1001)

        return response


class PackAnalysisCanister(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, batch_id, company_id, alt_in_robot=None,
            alt_available=None, ignore_reserve_status=None, **kwargs):
        if batch_id is None and company_id is None:
            return error(1001, "Missing Parameter(s): batch_id and company_id.")
        if alt_in_robot:
            alt_in_robot = bool(int(alt_in_robot))  # expected value 0,1
        else:
            alt_in_robot = True
        if alt_available:
            alt_available = bool(int(alt_available))  # expected value 0,1
        else:
            alt_available = True
        if ignore_reserve_status:
            ignore_reserve_status = bool(int(ignore_reserve_status))  # expected value 0,1
        else:
            ignore_reserve_status = False
        response = get_alternate_canister_for_batch(
            batch_id, company_id,
            alt_in_robot=alt_in_robot,
            alt_available=alt_available,
            ignore_reserve_status=ignore_reserve_status
        )
        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_pack_analysis_canisters
            )
        else:
            return error(1001)

        return response


class CanisterPerDrawer(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id, device_id=None, drawer_numbers=None, **kwargs):
        if not company_id:
            return error(1001, "Missing Parameter(s): company_id.")

        response = get_canisters_per_drawer(company_id=int(company_id), device_id=device_id,
                                            drawer_numbers=drawer_numbers)
        return response


class DrugActiveCanister(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id, system_id=None, user_id=None, **kwargs):
        if not company_id:
            return error(1001, "Missing Parameter(s): company_id.")
        dict_info = {
            "company_id": company_id,
            "system_id": system_id,
            "user_id": user_id
        }
        response = get_drug_active_canister(dict_info)

        return response


class DiscardExpiredCanisterDrug(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], discard_expired_canister_drug
            )
        else:
            return error(1001)

        return response


class GetExpiredDrugHistory(object):
    exposed = True

    # @authenticate(settings.logger)  # INFO removing authentication to allow Robot Code
    @use_database(db, settings.logger)
    def GET(self, company_id=None, filters=None, sort_fields=None, paginate=None,**kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id")
        args = {"company_id": company_id}
        try:
            if paginate is not None:
                if "number_of_rows" not in paginate or "page_number" not in paginate:
                    return error(1020, ' Missing key(s) in paginate.')
                args["paginate"] = json.loads(paginate)
            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        try:
            response = get_expired_drug_history(args)
        except Exception as ex:
            print(ex)
            return error(1001, "No record found for the given parameters.")

        return response


class GetCanisterList(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id, pack_id=None, ndc=None, mfd_analysis_ids=None, **kwargs):
        if not company_id or not ndc:
            return error(1001, "Missing Parameter(s): company_id or pack_id or ndc")
        if mfd_analysis_ids and isinstance(mfd_analysis_ids, str):
            mfd_analysis_ids = json.loads(mfd_analysis_ids)
        response = get_canisters_by_pack_ndc(company_id=int(company_id), ndc=ndc, pack_id=pack_id, mfd_analysis_ids=mfd_analysis_ids)
        return response



class PackAnalysis(object):
    """
    Controller to get data for pack analysis data
    """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, packlist=None, batch_id=None, system_id=None, **kwargs):

        if packlist is None or system_id is None or batch_id is None:
            return error(1001, "Missing Parameter(s): packlist or system_id or batch_id.")
        else:
            packlist = packlist.split(',')
            system_id = int(system_id)
            args = {
                "packlist": packlist,
                "system_id": system_id,
                "batch_id": batch_id
            }
            response = get_analysis_data(args)

        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_analysis_data
            )

            return response


class GetPackAnalysis(object):
    """
    Controller to get data for pack analysis data using POST to prevent url truncation
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], get_analysis_data
            )

            return response


class CanisterRecommendation(object):
    """
        Controller for recommending canisters
    """

    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, recommendation=None, system_id=None, batch_id=None, company_id=None,
            re_run=False, user_id=None, idle_robot_ids=None, include_skipped=False, version_type='c', **kwargs):
        if recommendation is None or system_id is None or user_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): recommendation or system_id or user_id or company_id.")
        if re_run:
            re_run = bool(int(re_run))  # expected values 0,1
        if include_skipped:  # flag to indicate skipped canister list should be included
            include_skipped = bool(int(include_skipped))

        response = flow_handler(
            system_id, recommendation,
            user_id, company_id, batch_id,
            re_run=re_run,
            idle_robot_ids=idle_robot_ids,
            include_skipped=include_skipped,
            version_type=version_type
        )
        return response


class PackDistributionByBatch(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], run_recommendations  # ,save_distributed_packs_by_batch
            )
        else:
            return error(1001)

        return response


class CheckValidCanister(object):
    """
        Controller to check canister is valid or not for change ndc
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, canister_id, ndc_list, company_id=None, **kwargs):
        response = check_valid_canister(ndc_list, canister_id)
        return response


class OrderCanisters(object):
    """
    controller for ordering new canisters.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], order_canisters
            )
        else:
            return error(1001)

        return response


class GetCanisterOrderHistory(object):
    """
    controller to get order history of canisters which are ordered.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, filters=None, paginate=None, company_id=None, sort_fields=None, **kwargs):
        filter_fields = {}
        if filters:
            filter_fields = json.loads(filters)
        if paginate:
            paginate = json.loads(paginate)
        if sort_fields:
            sort_fields = json.loads(sort_fields)
        response = get_canister_order_history(filter_fields, paginate, sort_fields)
        return response
