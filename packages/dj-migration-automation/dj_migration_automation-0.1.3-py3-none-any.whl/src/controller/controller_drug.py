import json

import cherrypy

import settings
from controller.controller_drug_sync import logger
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.canister import get_replenish_drugs, get_skipped_canister_during_replenish, \
    revert_replenish_skipped_canister, initiate_replenish_update
from src.service.drug import get_drug, get_drug_information_by_ndc, get_drug_information_by_drug, \
    check_drug_image_and_data_from_formatted_ndc, find_drug_and_bottle_details_from_drug_id, \
    get_drug_dosage_types_and_coating_types, \
    get_valid_ndc, change_status_by_ips, get_manual_drugs, batch_drugs, get_batch_drug_details, get_drug_stock_status, \
    get_unique_drugs, get_no_of_drug_by_pack_id, search_drug_fields, register_powder_pill, \
    get_drug_information_from_ips_by_ndc, separate_pack_canister_drug_from_scanned_value, get_drug_detail_slotwise, \
    get_inventory_quantity_from_elite, get_drug_image_data, get_lot_no_from_ndc, get_valid_ndc
from src.exc_thread import ExcThread
from src.service.drug import validate_scanned_drug, drug_filled, last_scanned_ndc_manual_pack_filling
from src.service.pack import get_batch_canister_manual_drugs, update_drug_status

from sync_drug_data import sync_settings
from sync_drug_data.update_drug_data import start_sync
from utils.drug_inventory_webservices import get_data_by_ndc_from_drug_inventory


class Drug(object):
    """
    Returns list of drug matching filter criteria (and based filter)
    """
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, device_id=None,
            company_id=None, canister_search=None, filters=None, sort_fields=None, paginate=None,
            records_from_date=None, **kwargs):
        canister_search = canister_search if canister_search else 0
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
        args = {
            "company_id": company_id, "canister_search": canister_search,
            "device_id": device_id
        }
        if paginate is not None:
            args["paginate"] = json.loads(paginate)
        if sort_fields:
            args["sort_fields"] = json.loads(sort_fields)
        if filters:
            args["filters"] = json.loads(filters)
        if records_from_date:
            args["records_from_date"] = str(records_from_date)
        response = get_drug(args)

        return response


class GetDrugInfoFromIPS(object):
    exposed = True

    @authenticate(sync_settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, ndc_list=None, company_id=None, **kwargs):
        if ndc_list is None or company_id is None:
            return error(1001, "Missing Parameter(s): NDC or company_id.")

        args = {"ndc_list": json.loads(ndc_list), "company_id": company_id}
        response = get_drug_information_from_ips_by_ndc(args)

        return response


class DrugField(object):
    """
    Searches in drug fields
    """
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, field=None, field_value=None, all_flag=None, **kwargs):
        if field is None or (field_value is None and all_flag is None):
            return error(1001, "Missing Parameter(s): field or (field_value and all_flag).")
        response = search_drug_fields(field, field_value, all_flag)

        return response


class GetDrugInformationByNdc(object):
    """
          @class: GetCanisterInfo
          @type: class
          @param: object
          @desc:  get the drug information using ndc
    """
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, ndc=None, blacklist=None, **kwargs):
        if ndc is None or blacklist is None:
            return error(1001, "Missing Parameter(s): ndc or blacklist.")

        args = {"ndc": ndc, "blacklist": blacklist}
        # 16 Mar 16 Abner - Include blacklist flag
        response = get_drug_information_by_ndc(args)

        return response


class GetDrugDataFromInventory(object):
    """
    get the drug information using ndc
    """
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, ndc_list=None):
        if ndc_list is None:
            return error(1001, "Missing Parameter(s): ndc or blacklist.")

        return create_response(get_data_by_ndc_from_drug_inventory(ndc_list=ndc_list.split(",")))


class GetDrugInformationByDrugName(object):
    """
          @class: GetCanisterInfo
          @type: class
          @param: object
          @desc:  get the drug information using drugname
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, drug_name=None, blacklist=None, unique_drugs=None,
            limit=None, **kwargs):
        if drug_name is None or blacklist is None:
            return error(1001, "Missing Parameter(s): drug_name or blacklist.")

        # 16 Mar 16 Abner - Include blacklist flag
        args = {"drug_name": drug_name.upper(), "blacklist": blacklist}
        try:
            if unique_drugs:  # expected value 0,1
                args['unique_drugs'] = bool(int(unique_drugs))
            if limit:
                args['limit'] = int(limit)
        except (TypeError, ValueError) as e:
            return error(1020, "Integer expected for unique_drugs and limit.")
        response = get_drug_information_by_drug(args)

        return response


class GetDrugInformationByDrug(object):
    """
          Arguments: drug (string)
                     blacklist (string)
          Description: Returns the list of drugs based on the passed arguments

    """
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, drug=None, system_id=None, blacklist=None, **kwargs):
        if drug is None or blacklist is None or system_id is None:
            return error(1001, "Missing Parameter(s): drug or blacklist or system_id.")
        else:
            args = {"drug": drug, "blacklist": blacklist}  # 16 Mar 16 Abner - Include blacklist flag
            response = get_drug_information_by_drug(args)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = ["localhost"]  # todo check why localhost
        return response


class CheckDrugImageForBarcodeNdc(object):
    """
    Check for drug image based on ndc given and get its details
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, drug_ndc=None, **kwargs):
        # check if robotid is present.If not present throw error
        # otherwise call callback function attached to it.
        if drug_ndc is None:  # system id won't be used
            return error(1001, "Missing Parameter(s): drug_ndc.")
        else:
            args = {"scanned_ndc": drug_ndc}
            response = check_drug_image_and_data_from_formatted_ndc(args)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class GetDrugAndBottleDetailsFromDrugId(object):
    """
    Checks for drug and bottle details based on drug id
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, drug_id=None, company_id=None, require_canister_data=0, **kwargs):
        # check if robotid is present.If not present throw error
        # otherwise call callback function attached to it.
        if drug_id is None or company_id is None:  # system id won't be used
            return error(1001, "Missing Parameter(s): drug_id or company_id.")
        else:
            args = {"drug_id": drug_id, "company_id": company_id, "require_canister_data": int(require_canister_data)}
            response = find_drug_and_bottle_details_from_drug_id(args)

        # we have to add 'Access-Control-Allow-Origin' to the response header
        # to support cross-domain
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        return response


class DosageTypeAndCoatingType(object):
    """ Controller for `DosageType` """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, **kwargs):
        response = get_drug_dosage_types_and_coating_types()
        return response


class GetValidNdc(object):
    """Controller for GetValidNdc"""
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, ndc=None, user_id=None, bottle_qty_req=False, company_id=None, is_mvs=False, ndc_allowed=True,
            module_id=None, ndq_required=None, **kwargs):
        if ndc is None:
            return error(1001, "Missing Parameter(s): ndc or company_id.")
        input_args = {"ndc": ndc, "user_id": user_id, "bottle_qty_req": bottle_qty_req,
                      "company_id": company_id, "is_mvs": is_mvs, "ndc_allowed": ndc_allowed,
                      "module_id": module_id, "ndq_required": ndq_required}
        response = get_valid_ndc(input_args)
        return response


class DrugStatus(object):
    """Controller for updating drug status by IPS"""
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"],
                change_status_by_ips
            )
            return response
        else:
            return error(1001)


class ManualDrugs(object):
    """
      @lastModifiedDate: 10/16/2017
      @type: class
      @param: object
      @desc:  gets the manual drug list for given pack list and system.
    """
    exposed = True

    @authenticate(sync_settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, batch_id=None, system_id=None, **kwargs):
        if batch_id is None or system_id is None:
            return error(1001, "Missing Parameter(s): batch_id or system_id.")
        else:
            # 16 Mar 16 Abner - Include blacklist flag
            args = {
                "batch_id": batch_id,
                "system_id": int(system_id)
            }
            response = get_manual_drugs(args)

        return response


class BatchDrugs(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, company_id=None, batch_id=None, system_id=None, number_of_packs=None, type_of_drug=None,
            replenish_required=None, extra_canister_data=None, **kwargs):
        if company_id is None or batch_id is None:
            return error(1001, "Missing Parameter(s): company_id or batch_id.")
        response = batch_drugs(company_id, batch_id, system_id, number_of_packs, type_of_drug,
                               replenish_required, extra_canister_data)
        return response


class DrugSync(object):
    """ Run drug sync task
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def POST(self, **kwargs):
        logger.debug(kwargs)
        if sync_settings.DRUG_SYNCING:
            return create_response("Already Syncing")
        if "args" in kwargs:
            args = json.loads(kwargs['args'])
            if not args.get('system_id', None) or not args.get('user_id', None):
                return error(1002)
            user_id = args['user_id']
            system_id = args['system_id']
            all_drug = args.get('all_drug', False)  # sync all drug or not
            use_file = args.get('use_file', False)  # True when big drug data is causing memory issue
            company_id = args.get('company_id')
            exception_list = []
            t = ExcThread(
                exception_list,
                name="drug_sync_thread",
                target=start_sync,
                args=[user_id, company_id, all_drug, system_id, use_file]
            )
            t.start()
            return create_response("Syncing Started")
        else:
            return error(1001)


class ValidateDrugScan(object):
    """ Validate Scanned Drug to update in slot details and do update. """

    exposed = True

    @authenticate(sync_settings.logger)
    @use_database(db, sync_settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], validate_scanned_drug
            )
        else:
            return error(1001)
        return response


class DrugFilled(object):
    """ Drug Filled to insert the data in drug_tracker. """

    exposed = True

    @authenticate(sync_settings.logger)
    @use_database(db, sync_settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], drug_filled
            )
        else:
            return error(1001)
        return response


class LastScannedNdcManualPackFilling(object):
    """
    LastScannedNdcManualPackFilling for update the slot_details if filled drug in current pack is different from
    the drug in slot_details table
    """

    exposed = True

    @authenticate(sync_settings.logger)
    @use_database(db, sync_settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], last_scanned_ndc_manual_pack_filling
            )
        else:
            return error(1001)
        return response


class GetBatchCanisterManualDrugs(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, batch_id=None, system_id=None, company_id=None, pack_queue=True, pack_id_list=None, list_type=None,
            drug_type=None, **kwargs):

        # check if input argument kwargs is present
        if list_type and drug_type:
            list_type = json.loads(list_type)
            drug_type = json.loads(drug_type)

        if pack_id_list is not None:
            pack_id_list = json.loads(pack_id_list)

        dict_batch_info = {"batch_id": batch_id, "system_id": system_id, "company_id": company_id,
                           "pack_queue": pack_queue, "list_type": list_type, "pack_id_list": pack_id_list,
                           "drug_type": drug_type}
        response = get_batch_canister_manual_drugs(dict_batch_info)

        return response


class GetBatchUniqueDrugs(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, batch_id=None, system_id=None, company_id=None, filter_fields=dict(), paginate=dict(),
            sort_fields=list(), pack_queue=False, upcoming_batches=False, **kwargs):
        # check if input argument kwargs is present
        # if batch_id is None:
        #     return error(1001, "Missing Parameter(s): batch_id.")

        dict_batch_info = {"batch_id": batch_id,
                           "system_id": system_id,
                           "company_id": company_id,
                           "filter_fields": filter_fields,
                           "sort_fields": sort_fields,
                           "paginate": paginate,
                           "pack_queue": pack_queue,
                           "upcoming_batches": upcoming_batches
                           }

        response = get_batch_drug_details(dict_batch_info)

        return response


class UpdateDrugStatus(object):
    """
        @class: UpdateDrugStatus
        @desc: Controller to update drug status.
    """
    exposed = True

    @authenticate(sync_settings.logger)
    @use_database(db, sync_settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_drug_status)
        else:
            return error(1001)
        return create_response(response)


class GetDrugStockStatus(object):
    """
    @class: GetDrugStockStatus
    @desc: To get drugs by their stock status (in stock, out of stock, discontinue)
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, company_id=None, filter_fields=None):
        if company_id is None or filter_fields is None:
            return error(1002, "Missing Parameter(s): filter_fields or company_id.")

        filter_fields = json.loads(filter_fields)
        company_id = int(company_id)

        response = get_drug_stock_status(company_id, filter_fields)
        return response


class GetUniqueDrugs(object):
    """
        @class: GetUniqueDrugs
        @type: class
        @param: object
        @desc: Get all the unique drugs for the pack.
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, sync_settings.logger)
    def GET(self, pack_id=None, **kwargs):
        # check if input argument kwargs is present
        if pack_id is None:
            return error(1001, "Missing Parameter(s): pack_id.")

        dict_pack_info = {
            "pack_id": pack_id,
        }
        response = get_unique_drugs(dict_pack_info)

        return response


class GetNoOfDrugsByPackId(object):
    """
          Arguments: pack_id (number)
          Description: Returns the number of unique drugs for the given pack_id
    """
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, pack_id=None, system_id=None, **kwargs):
        if pack_id is None or system_id is None:
            return error(1001, "Missing Parameter(s): pack_id or system_id.")

        args = {
            "pack_id": int(pack_id),
            "system_id": int(system_id)
        }
        response = get_no_of_drug_by_pack_id(args)

        return response


class Replenish(object):
    """ Controller for Replenish """

    exposed = True

    @authenticate(sync_settings.logger)
    @use_database(db, sync_settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], get_replenish_drugs
            )
        else:
            return error(1001)

        return response


class ReplenishSkippedCanister(object):
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, system_id=None, device_id=None, company_id=None, **kwargs):
        if system_id is None or device_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): device_id or system_id or company_id")

        args = {"system_id": int(system_id),
                "device_id": int(device_id),
                "company_id": int(company_id)
                }

        response = get_skipped_canister_during_replenish(args)

        return response


class RevertReplenishSkippedCanister(object):
    exposed = True

    @authenticate(sync_settings.logger)
    @use_database(db, sync_settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], revert_replenish_skipped_canister
            )
        else:
            return error(1001)

        return response


class ReplenishUpdate(object):
    exposed = True

    @use_database(db, sync_settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], initiate_replenish_update
            )
        else:
            return error(1001)

        return response


class RegisterPowderPill(object):
    exposed = True

    @use_database(db, sync_settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], register_powder_pill
            )
        else:
            return error(1001)

        return response


class SeparateDrugCanisterPack(object):
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, company_id=None, scanned_value=None, system_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id or scanned_value or system_id")

        args = {"scanned_value": scanned_value,
                "company_id": int(company_id),
                "system_id": int(system_id)
                }

        response = separate_pack_canister_drug_from_scanned_value(args)

        return response


class GetDrugDetailSlotwise(object):
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, pack_id=None,system_id=None,company_id=None,**kwargs):

        if company_id is None or pack_id is None:
            return error(1001, "Missing Parameter(s): company_id or pack_id")

        args = {
            "system_id": system_id,
            "pack_id": pack_id,
            "company_id": company_id
        }

        response = get_drug_detail_slotwise(args)

        return response


class GetDrugDataOnDemand(object):
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, ndc_list, company_id, **kwargs):
        if ndc_list is None or company_id is None:
            return error(1001, "Missing Parameter(s)")
        if not isinstance(ndc_list, list):
            ndc_list = [ndc_list]

        response = get_drug_image_data(ndc_list, company_id)

        return response


class GetInventoryQuantity(object):
    """
        This class contains the methods that fetch inventory quantity from elite based on ndc or txr
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, ndc_list):
        if isinstance(ndc_list, str):
            ndc_list = [ndc_list]
        if ndc_list:
            return get_inventory_quantity_from_elite(ndc_list)
        else:
            return error(1001, "Missing Parameter(s): ndc_list")


class GetLotNoFromNdc(object):
    exposed = True

    @use_database(db, sync_settings.logger)
    def GET(self, ndc, no_of_records, **kwargs):
        if ndc is None:
            return error(1001, "Missing Parameter(s): ndc")

        response = get_lot_no_from_ndc(ndc, no_of_records)

        return response
