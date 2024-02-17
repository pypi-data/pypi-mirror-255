import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import (error)
from dosepack.utilities.manage_db_connection import (use_database)
from dosepack.utilities.validate_auth_token import (authenticate)
from dosepack.validation.validate import (validate_request_args)
from scripts.mfd_canister_filling_drug import mfd_canister_filling_drug
from scripts.mfd_canister_transfer import mfd_canister_status_location_change
from scripts.mfd_canister_transfer_for_specific_cart import mfd_canister_status_location_change_filter_by_cart_id
from scripts.mfd_canister_transfer_from_cart_to_mfs import mfd_canister_transfer_from_cart_to_mfs
from scripts.mfd_canister_transfer_from_cart_to_robot import mfd_canister_transfer_from_cart_to_robot
from scripts.mfd_canister_transfer_from_mfs_to_cart import mfd_canister_transfer_from_mfs_to_cart
from src.service.mfd import (get_mfd_batch_data, get_mfd_user_batch_data, get_batch_drug_details,
                             update_mfd_alternate_drug, skip_drug, update_drug_status, update_mfd_analysis,
                             get_similar_canister, update_scanned_trolley, stop_filling, update_mfd_canister_status,
                             scan_drawer, get_drawer_data, get_mfd_filling_canister, get_mfs_data,
                             resume_filling, get_mfd_batch_data_per_mfs, disable_canister_location,
                             update_pack_delete_manual_status, update_transfer_data_mfs, update_mfs_user_access,
                             update_notification_view_list, update_pending_mfd_assignment, update_mfd_current_module,
                             update_mfd_transfer_status_v2, get_mvs_filling_mfd_canister, mark_canister_mvs_filled,
                             reset_scanned_data, skip_mfs_filling, deactivate_mfd_canister,
                             disable_canister_location_transfer, get_batch_drug_trolley_details, get_mfd_batch_drugs,
                             update_mfd_data, check_batch_drug)
from src.service.mfd_recommendation import save_mfd_recommendation


class UpdateMFDAnalysis(object):
    """
        Controller to update trolley data in MFDAnalysis
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_mfd_analysis
            )
        else:
            return error(1001)

        return response


class MFDBatchDetails(object):
    """
    Controller to get pending/in progress mfd batch data for all the users
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, user_id=None, system_id=None, batch_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {'company_id': company_id, 'user_id': user_id, 'system_id': system_id, 'batch_id': batch_id}
        response = get_mfd_batch_data(args)

        return response


class MFDUserBatchDetails(object):
    """
    Controller to get pending/in progress mfd batch data for particular user
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, user_id=None, **kwargs):
        if company_id is None or system_id is None or user_id is None:
            return error(1001, "Missing Parameter(s): company_id or system_id or user_id.")

        args = {'company_id': company_id, 'user_id': user_id, 'system_id': system_id}
        response = get_mfd_user_batch_data(args)

        return response


class MFDDrugList(object):
    """
    Controller to get the drug list of a particular batch
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, batch_id=None, user_id=None, system_id=None, filters=None, sort_fields=None,
            **kwargs):
        if company_id is None or batch_id is None or system_id is None or user_id is None:
            return error(1001, "Missing Parameter(s): company_id or batch_id or system_id or user_id.")

        args = {'company_id': company_id, 'user_id': user_id,
                'batch_id': batch_id, 'system_id': system_id}
        try:

            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        response = get_batch_drug_details(args)

        return response


class MFDTrolleyListByBatch(object):
    """
    Controller to get the Trolley list of a particular batch
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, batch_id=None, user_id=None, system_id=None, **kwargs):
        if company_id is None or batch_id is None or system_id is None or user_id is None:
            return error(1001, "Missing Parameter(s): company_id or batch_id or system_id or user_id.")

        args = {'company_id': company_id, 'user_id': user_id,
                'batch_id': batch_id, 'system_id': system_id}
        response = get_batch_drug_trolley_details(args)

        return response


class MFDDrugListByTrolley(object):
    """
    Controller to get the drug list of a particular batch Trolley-wise
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, batch_id=None, user_id=None, system_id=None, trolley_id_list=None, **kwargs):
        if company_id is None or batch_id is None or system_id is None or user_id is None:
            return error(1001, "Missing Parameter(s): company_id or batch_id or system_id or user_id.")

        args = {'company_id': company_id, 'user_id': user_id,
                'batch_id': batch_id, 'system_id': system_id, 'get_trolley_drugs': True}
        try:
            if trolley_id_list:
                args["trolley_id_list"] = json.loads(trolley_id_list)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        response = get_batch_drug_details(args)

        return response


class MFDAlternateDrug(object):
    """
    Controller to update the mfd alternate drug
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_mfd_alternate_drug
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class MFDFillCanister(object):
    """
    To get the canister-drug data to be filled on Manual Fill Station
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, batch_id=None, user_id=None, device_id=None, system_id=None, trolley_seq=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {'company_id': company_id, 'user_id': user_id, 'device_id': device_id, 'batch_id': batch_id,
                'system_id': system_id, 'trolley_seq': trolley_seq}

        response = get_mfd_filling_canister(args)

        return response


class MFDSkipDrug(object):
    """
    Controller to skip the drug
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], skip_drug
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class MFDDrugUpdate(object):
    """
    To change the status of mfd drug
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_drug_status
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class SimilarCanister(object):
    """
        To get the canisters' data which has same drugs
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, batch_id=None, analysis_id=None, user_id=None, system_id=None, **kwargs):
        if company_id is None or batch_id is None or analysis_id is None or user_id is None:
            return error(1001, "Missing Parameter(s): company_id or batch_id or analysis_id or user_id.")

        args = {'company_id': company_id, 'user_id': user_id, 'analysis_id': analysis_id, 'batch_id': batch_id,
                'system_id': system_id}

        response = get_similar_canister(args)

        return response


class ScanTrolley(object):
    """
    Controller to scan the trolley
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_scanned_trolley
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class ScanDrawer(object):
    """
    Controller to scan the drawer
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], scan_drawer
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class StopFilling(object):
    """
    Controller to stop filling for a particular batch of a user
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], stop_filling
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class ResumeFilling(object):
    """
    Controller to resume filling for a particular batch of a user
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], resume_filling
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class MFDUpdateCanister(object):
    """
    Controller to update the canister status
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_mfd_canister_status
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class DrawerData(object):
    """
    Controller to get canister data which needs to be placed in the same drawer of a trolley
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, batch_id=None, drawer_id=None, user_id=None, system_id=None, **kwargs):
        if company_id is None or batch_id is None or drawer_id is None or user_id is None:
            return error(1001, "Missing Parameter(s): company_id or batch_id or drawer_id or user_id.")

        args = {'company_id': company_id, 'user_id': user_id, 'drawer_id': drawer_id, 'batch_id': batch_id,
                'system_id': system_id}

        response = get_drawer_data(args)

        return response


class ManualFillStation(object):
    """
    Controller to get manual fill station data of a particular company
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, system_id=None, check_user_assigned=False, batch_id=None, **kwargs):
        if company_id is None or system_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {'company_id': company_id, 'system_id': system_id, 'check_user_assigned': check_user_assigned,
                'batch_id': batch_id}

        response = get_mfs_data(args)

        return response


class MFDBatchDetailsMfsWise(object):
    """
    Controller to get the user, MFS association data of a particular batch
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, user_id=None, batch_id=None, **kwargs):
        if company_id is None or batch_id is None:
            return error(1001, "Missing Parameter(s): company_id or batch_id.")

        args = {'company_id': company_id, 'user_id': user_id, 'batch_id': batch_id}
        response = get_mfd_batch_data_per_mfs(args)

        return response


class MfdDisableLocation(object):
    """
    Controller to disable mfd drawer location
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], disable_canister_location
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class PackStatusUpdateNotification(object):
    """
    Controller to close the pop-up of mfd_canister info of pack delete or manual
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_pack_delete_manual_status
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class UpdateMFSTransfer(object):
    """
    Controller to update drawer data in mfs
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_transfer_data_mfs
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class UpdateUserAccess(object):
    """
    Controller to update user access of mfs-system and assigned canister changes.

    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_mfs_user_access)
                return response

            else:
                return error(1001)
        else:
            return error(1001)


class UpdateViewList(object):
    """
    Controller to update action taken by in notification doc
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_notification_view_list
                )
                return response
            else:
                return error(1001)
        else:
            return error(1001)


class UpdatePendingRecommendation(object):
    """
    Controller to update trolley recommendation when any trolley gets free
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_pending_mfd_assignment
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class UpdateMfdModule(object):
    """
    Controller to update user's mfd module
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], update_mfd_current_module
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class UpdateMFDTransferStatus(object):
    """
        Controller to update MFD Transfer Status wizard
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_mfd_transfer_status_v2
            )
        else:
            return error(1001, "args keyword not found in the input parameters.")

        return response


class MVSMFDCanisters(object):
    """
    Controller to get/update mfd canister data required to fill pack manually at mvs or pfw
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, pack_id=None, **kwargs):
        if company_id is None or pack_id is None:
            return error(1001, "Missing Parameter(s): company_id or pack_id.")

        response = get_mvs_filling_mfd_canister(pack_id, company_id)

        return response

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], mark_canister_mvs_filled)
        else:
            return error(1001)

        return response


class ResetScannedData(object):
    """
    Controller to reset drawer scan in mfd transfer flow
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], reset_scanned_data)
        else:
            return error(1001)

        return response


class SkipMfsFilling(object):
    """
    Controller to skip mfd filling from mfs for rest of the canisters of a batch
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], skip_mfs_filling)
        else:
            return error(1001)

        return response


class DeactivateMFDCanister(object):
    """
    To deactivate mfd canister
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], deactivate_mfd_canister)
        else:
            return error(1001)

        return response


class MfdDisableLocationTransfer(object):
    """
    Controller to get transfer suggestion while disabling robot's mfd locations
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], disable_canister_location_transfer
                )
            else:
                return error(1001)
        else:
            return error(1001)
        return response


class MfdRecommendation(object):
    """
    Controller for MFD Recommendation algo.
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if kwargs:
            if "args" in kwargs:
                response = validate_request_args(
                    kwargs["args"], save_mfd_recommendation
                )
                return response
            else:
                return error(1001)
        else:
            return error(1001)


class MfdCanisterLocationStatusChange(object):
    """
    Controller to change pending status of mfd canisters and place them to empty location of lower drawer of home cart
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], mfd_canister_status_location_change)
        else:
            return error(1001)
        return response


class MfdCanisterTransferForSpecificCart(object):
    """
    Controller to transfer MFD Canister for specific cart
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], mfd_canister_status_location_change_filter_by_cart_id)
        else:
            return error(1001)
        return response


class MfdCanisterTransferFromCartToMfs(object):
    """
    Controller to transfer mfd canister from cart to mfs
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], mfd_canister_transfer_from_cart_to_mfs)
        else:
            return error(1001)
        return response


class MfdCanisterTransferFromMfsToCart(object):
    """
    Controller to transfer mfd canister from mfd to cart
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], mfd_canister_transfer_from_mfs_to_cart)
        else:
            return error(1001)
        return response


class MfdCanisterTransferFromCartToRobot(object):
    """
    Controller to transfer mfd canister from cart to robot
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], mfd_canister_transfer_from_cart_to_robot)
        else:
            return error(1001)
        return response


class MfdCanisterFillingDrug(object):
    """
    Controller to get/update mfd canister data required to fill pack manually at mvs or pfw
    """
    exposed = True
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], mfd_canister_filling_drug)
        else:
            return error(1001)
        return response


class MfdBatchDrugs(object):
    """
    Controller to getmfdbatchdrugs which dimensions are available and there is no activated canisters
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, filters=None, paginate=None, company_id=None, **kwargs):
        filter_fields = {}
        if filters:
            filter_fields = json.loads(filters)
        if paginate:
            paginate = json.loads(paginate)
        response = get_mfd_batch_drugs(filter_fields, paginate)

        return response


class UpdateAnalysisData(object):
    """
    controller for updating mfd analysis and pack analysis data when canister is usable
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], update_mfd_data)
        else:
            return error(1001)

        return response


class CheckBatchDrug(object):
    """
    controller for checking the drug is available for the batch or not
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self,canister_id, ndc=None,company_id=None, **kwargs):
        response = check_batch_drug(ndc, canister_id)

        return response
