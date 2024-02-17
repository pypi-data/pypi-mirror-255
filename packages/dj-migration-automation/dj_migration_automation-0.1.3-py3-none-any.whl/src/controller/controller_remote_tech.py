import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.remote_tech import add_remote_tech_data, get_remote_tech_data, get_remote_tech_screen_data, \
    assign_rts_to_user, get_remote_tech_user_progress, assign_remote_tech_slot_data, assign_inactive_users_rts_slots, \
    assign_more_crops_for_unique_drug


class RemoteTech(object):
    """
    This class contains methods to add, get and update the data in/from RemoteTechSlot and RemoteTechSlot tables.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_remote_tech_data
            )
        else:
            return error(1001)

        return response

    @use_database(db, settings.logger)
    def GET(self, pvs_slot_id=None):
        if pvs_slot_id is None:
            return error(1001, "Missing Parameter(s): pvs_slot_id.")
        args = {"pvs_slot_id": pvs_slot_id}
        response = get_remote_tech_data(args)

        return create_response(response)

    # @authenticate(settings.logger)
    # @use_database(db, settings.logger)
    # def PUT(self, **kwargs):
    #     if "args" in kwargs:
    #         response = validate_request_args(
    #             kwargs["args"], update_remote_tech_data
    #         )
    #     else:
    #         return error(1001)
    #
    #     return response


class RemoteTechScreen(object):
    """
    This class contains the method for getting the data for the Remote Technician Screen for the user & manager.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None,
            paginate=None,
            user_id=None,
            filter_fields=None,
            advanced_search_fields=None,
            sort_fields=None,
            is_remote_technician=None,
            **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
        if user_id is None:
            return error(1001, "Missing Parameter(s): user_id.")

        args = {"company_id": company_id,
                "user_id": user_id}

        if is_remote_technician is not None:
            args["is_remote_technician"] = json.loads(is_remote_technician)
        if paginate is not None:
            args["paginate"] = json.loads(paginate)
        if filter_fields:
            args["filter_fields"] = json.loads(filter_fields)
        if sort_fields:
            args["sort_fields"] = json.loads(sort_fields)
        if advanced_search_fields:
            args["advanced_search_fields"] = json.loads(advanced_search_fields)
        response = get_remote_tech_screen_data(args)

        return response


class AssignRtsToUser:
    """
    Assign all the slots for given pack_id, slot_number, formatted_ndc, txr or unique_drug to given user.
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], assign_rts_to_user
            )
        else:
            return error(1001)

        return response


class RemoteTechProgress(object):

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, user_id: int=None, start_date=None, end_date=None):

        if user_id is None:
            return error(1001, "Missing Parameter(s): user_id.")
        args = {
            'user_id': int(user_id),
            'start_date': start_date,
            'end_date': end_date
        }
        response = get_remote_tech_user_progress(args)
        return response


class AssignRemoteTechSlots:

    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], assign_remote_tech_slot_data
            )
        else:
            return error(1001)

        return response


class AssignInactiveUsersRtsSlots:
    """
    Cron job if user is inactive for five days then assign its slots to other active users equally
    """

    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], assign_inactive_users_rts_slots
            )
        else:
            response = assign_inactive_users_rts_slots()

        return response


class MoreCropsForUniqueDrug:
    """
    Change unique drug's current_queue status to 2 in RtsSlotAssignInfo table and new crops(250) will be assigned
    when the drug falls into top 10 drugs while assigning 2500 slots.
    """

    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], assign_more_crops_for_unique_drug
            )
        else:
            return error(1001)

        return response