import json
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.utils import convert_dob_date_to_sql_date, is_date
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.crm import get_pack_queue_all_batch, get_packs_count_by_status, \
    assign_car_id_for_pack, change_pack_status, get_packs_count_by_robot_id, \
    get_pack_id_list_from_packs_by_status, update_unloading_time, get_pack_details_from_pack_id, \
    get_packs_per_robot_by_status, \
    update_pack_priority_by_pack_list, \
    update_pack_count_couch_db, get_pack_queue, dispatch_new_pack, update_pack_sequence, pack_analysis_v2, \
    get_system_packs_count_by_status, get_packs_count_by_system, \
    get_processed_pack_count_by_filled_time, get_packs_count_for_batch, get_packs_count_by_status_by_batch, \
    update_trolley_seq_pack_queue, get_trolley_seq_data


class GetPackCountForSystem(object):
    """returns pack count for batch which is imported"""
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, status=None, batch_id=None, system_id=None, time_zone=None, system_start_time=None, **kwargs):

        if system_id is None:
            return error(1001, "Missing Parameter(s): system_id.")

        if status is None:
            response = get_packs_count_by_system(batch_id, system_id)
        else:
            args = {
                "batch_id": batch_id,
                "status": json.loads(status),
                "system_id": system_id
            }
            if time_zone:
                args["time_zone"] = time_zone
                args["system_start_time"] = None if system_start_time == 'None' else system_start_time
            response = get_system_packs_count_by_status(args)

        return response


class GetPacksPerRobotByStatus(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, status=None, device_id=None, system_id=None, **kwargs):
        args = {
            "status": json.loads(status),
            "device_id": device_id,
            "system_id": system_id,
            "data": 1
        }
        response = get_packs_per_robot_by_status(args)
        return response


class AssignCarIdForPack(object):
    """ Controller to assign packs to a system """

    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:

            response = validate_request_args(
                kwargs["args"], assign_car_id_for_pack
            )
        else:
            return error(1001)
        return response


class UpdatePackStatus(object):
    """ Controller to assign packs to a system """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], change_pack_status
            )
        else:
            return error(1001)
        return response

class GetPackIdListFromPacksByStatus(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id_list=None, status=None, system_id=None, **kwargs):
        if status is None:
            return error(1001, "Missing Parameter(s): status.")

        args = {
            "pack_id_list": pack_id_list,
            "status": json.loads(status),
            "system_id": system_id
        }
        print(args)
        response = get_pack_id_list_from_packs_by_status(args)
        return response


class UpdateUnloadingTime(object):
    """ Controller to assign packs to a system """

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_unloading_time
            )
        else:
            return error(1001)
        return response


class GetPackDetailsFromPackId(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, pack_id=None, system_id=None, company_id=None, **kwargs):
        if pack_id is None:
            return error(1001, "Missing Parameter(s): pack_id.")
        args = {
            "pack_id": json.loads(pack_id),
            "system_id": system_id,
            "company_id": company_id
        }
        response = get_pack_details_from_pack_id(args)
        return create_response(response)



class GetRobotPackCount(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, batch_id=None, device_id=None, system_id=None, **kwargs):
        args = {
            "device_id": device_id,
            "system_id": system_id
        }
        response = get_packs_count_by_robot_id(args)
        return create_response(response)


class UpdatePackPriorityByPackList(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_pack_priority_by_pack_list
            )
        else:
            return error(1001)
        return create_response(response)


class UpdatePackCountCouchDb(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_pack_count_couch_db
            )
        else:
            return error(1001)
        return response


class DispatchNewPack(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            status, response = validate_request_args(
                kwargs["args"], dispatch_new_pack
            )
        else:
            return error(1001)
        return response


class GetPackQueue(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, only_manual=None, filter_fields=None, paginate=None, sort_fields=None, system_id=None, drug_list=None,
            current_batch=None, **kwargs):

        if system_id is None:
            return error(1001, "Missing Parameter(s): system_id.")

        only_manual = json.loads(only_manual)
        filter_fields = json.loads(filter_fields)
        sort_fields = json.loads(sort_fields)
        paginate = json.loads(paginate)
        current_batch = json.loads(current_batch)

        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        if drug_list:
            drug_list = json.loads(drug_list)

        if filter_fields and "patient_name" in filter_fields and filter_fields['patient_name'] is not None:
            patient_search = filter_fields['patient_name']
            if is_date(patient_search) and not patient_search.isdigit():
                try:
                    convert_dob_date_to_sql_date(filter_fields['patient_name'])
                except ValueError:
                    return error(1009)

        if current_batch:
            status, response = get_pack_queue(only_manual, filter_fields, paginate, sort_fields, system_id, drug_list)
        else:
            status, response = get_pack_queue_all_batch(only_manual, filter_fields, paginate, sort_fields, system_id, drug_list)

        if status:
            return create_response(response)
        else:
            print("Error in get_pack_queue {}".format(response))
            return error(0)


class UpdatePackSequence(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_pack_sequence
            )
        else:
            return error(1001)
        return response


class PackAnalysisV2(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], pack_analysis_v2
            )
        else:
            return error(1001)
        return response


class ImportToDosepacker(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], pack_analysis_v2
            )
        else:
            return error(1001)
        return response



class GetProcessedPackCountByFilledTime(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, start_time=None, end_time=None, system_id=None, **kwargs):
        args = {
            "start_time" : start_time,
            "end_time" : end_time,
            "system_id" : system_id
        }
        response = get_processed_pack_count_by_filled_time(args)

        return response


class GetPackCountForBatch(object):
    """returns pack count for batch which is imported"""
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, status=None, batch_id=None, system_id=None, **kwargs):

        if system_id is None:
            return error(1001, "Missing Parameter(s): system_id.")

        if status is None:
            response = get_packs_count_for_batch(batch_id, system_id)
        else:
            args = {
                "batch_id": batch_id,
                "status": json.loads(status),
                "system_id": system_id
            }
            response = get_packs_count_by_status_by_batch(args)

        return response




class UpdateMfdTrolleySeqPackQueue(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self,system_id=None, pack_list=None, paginate=None,filter_fields=None):
        
        if system_id is None:
            return error(1001, "Missing Parameter(s): system_id.")
        pack_list = json.loads(pack_list) if pack_list else None

        response = get_trolley_seq_data(system_id, pack_list, paginate, filter_fields)
        return response


    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_trolley_seq_pack_queue
            )
        else:
            return error(1001)
        return response

