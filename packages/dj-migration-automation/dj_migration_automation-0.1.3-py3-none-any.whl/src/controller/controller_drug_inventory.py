import json
import logging
from typing import List, Optional

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.dao.drug_inventory_dao import check_drug_inventory
from src.service.drug_inventory import (epbm_alternate_canisters, get_drug_data_by_facility_dis_id,
                                        get_pre_order_data_by_facility_dis_id, check_and_update_drug_req,
                                        update_ack_department, fetch_pre_order_data_from_drug_inventory,
                                        inventory_mark_in_stock_status, inventory_adjust_quantity)
from utils.auth_webservices import send_email_for_drug_req_check_failure

logger = logging.getLogger("root")


class EPBMAlternateCanister(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, ndc_list: Optional[str] = None, unique_id: Optional[str] = None) -> str:
        """
        To obtain canister data using drawer_id, company_id and device_id
        """
        logger.debug("In Class EPBMAlternateCanister")

        if ndc_list is None or unique_id is None:
            return error(1001, "Missing Parameter(s): ndc_list or unique_id")

        return epbm_alternate_canisters({'ndc_list': ndc_list, 'unique_id': unique_id})


class EPBMBatchDrugs(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, facility_dist_id: Optional[int] = None, company_id: Optional[int] = None) -> str:
        """
        Fetch the drug data for the given facility distribution id.
        """
        logger.debug("In Class EPBMBatchDrugs.GET")

        if facility_dist_id is None or company_id is None or facility_dist_id == "" or company_id == "":
            return error(1001, "Missing Parameter(s): facility_dist_id or company_id.")

        return get_drug_data_by_facility_dis_id({"facility_dist_id": facility_dist_id, "company_id": company_id})

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs) -> str:
        """
        Update the pre-order data from Drug Inventory.
        """
        logger.debug("In Class EPBMBatchDrugs.POST")

        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_ack_department)
        else:
            return error(1001)

        return response


class EPBMPreOrderData(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, facility_dist_id: Optional[int] = None, company_id: Optional[int] = None,
            req_drug_search: Optional[str] = None, avl_pre_order_drug_search: Optional[str] = None,
            filter_by: Optional[str] = None) -> str:
        """
        To obtain pre_order data using facility_dist_id & company_id.
        """
        logger.debug("In Class EPBMPreOrderData.GET")

        if facility_dist_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): facility_dist_id or company_id.")

        return get_pre_order_data_by_facility_dis_id({"facility_dist_id": facility_dist_id,
                                                      "company_id": company_id,
                                                      "req_drug_search": req_drug_search,
                                                      "avl_pre_order_drug_search": avl_pre_order_drug_search,
                                                      "filter_by": filter_by})


class EPBMDrugReqCheck(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id: Optional[int] = None, time_zone: Optional[str] = None,
            system_id_list: Optional[List[int]] = None) -> str:
        """
        To obtain pre_order data using facility_dist_id & company_id.
        """
        logger.debug("In Class EPBMDrugReqCheck.GET")

        if company_id is None or time_zone is None or system_id_list is None:
            send_email_for_drug_req_check_failure(company_id=company_id, time_zone=time_zone,
                                                  error_details="Missing Parameter(s): company_id or time_zone or "
                                                                "system_id_list.")
            return error(1001, "Missing Parameter(s): company_id or time_zone or system_id_list.")

        return check_and_update_drug_req({"company_id": company_id,
                                          "time_zone": time_zone,
                                          "system_id_list": system_id_list})


class EPBMFetchPreOrderData(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, facility_dist_id: Optional[int] = None, company_id: Optional[int] = None) -> str:
        """
        Fetch the pre_ordered data for the given unique_id
        """
        if facility_dist_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): facility_dist_id or company_id.")

        return fetch_pre_order_data_from_drug_inventory({"facility_dist_id": facility_dist_id,
                                                         "company_id": company_id})


class EPBMUpdateDrugStatus(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs) -> str:
        """
        Update drug status from inventory.
        """
        logger.debug("In Class EPBMUpdateDrugStatus.POST")

        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], inventory_mark_in_stock_status)
        else:
            return error(1001)

        return response


class EPBMCheckInventory(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, ndc_list=None, case_list=None):
        """
        Fetch the pre_ordered data for the given unique_id
        """
        # args = json.loads(args)
        # ndc_list = args.get('ndc_list', list())
        # case_list = args.get('case_list', list())
        if not len(ndc_list) and not len(case_list):
            return error(1001, "Missing Parameter(s): ndc or case_id. in EPBMCheckInventory")

        return check_drug_inventory(ndc_list, case_list)


class EPBMAdjustQuantity(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs) -> str:

        logger.debug("In Class EPBMAdjustQuantity.POST")

        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], inventory_adjust_quantity)
        else:
            return error(1001)

        return response
