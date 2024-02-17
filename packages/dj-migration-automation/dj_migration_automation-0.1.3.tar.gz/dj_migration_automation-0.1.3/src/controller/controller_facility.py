import json
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.facility_schedule import get_facility_info, add_schedule, get_schedule_details, get_calender_info, \
    delete_schedule, remove_schedule, get_expected_schedule, add_batch_distribution, get_facility_data_of_pending_packs, \
    pharmacy_delivery_sync, get_patientwise_calender_schedule


class Facility(object):
    """
    Controller to return facility data for given company
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], get_facility_info)
        else:
            return error(1001)
        return create_response(response)


class FacilityBatch(object):
    """Controller for Facility batch distribution"""
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_batch_distribution
            )
        else:
            return error(1001)
        return response


class FacilitySchedule(object):
    """Controller for `Facility Schedule` Model"""

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, current_date=None, facility_list=None, **kwargs):
        if not company_id or not current_date:
            return error(1001, 'Missing Parameter(s): company_id or current_date.')
        if facility_list:
            facility_list = facility_list.split(',')
        response = get_schedule_details(company_id, current_date, facility_list)
        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"],
                add_schedule
            )
            return response
        else:
            return error(1001)


class CalendarSchedule(object):
    """controller for scheduled facility"""

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, start_date=None, end_date=None, facility_list=None, **kwargs):
        if not company_id or not start_date or not end_date:
            return error(1001, "Missing Parameter(s): company_id or start_date or end_date.")
        if facility_list:
            facility_list = facility_list.split(',')
        response = get_calender_info(company_id, start_date, end_date, facility_list)
        return response


class DeleteSchedule(object):
    """controller for deleting facility schedule"""

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"],
                delete_schedule
            )
            return response
        else:
            return error(1001)


class RemoveSchedule(object):
    """controller for deleting facility schedule"""

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"],
                remove_schedule
            )
            return response
        else:
            return error(1001)


class ExpectedSchedule(object):
    """Controller for `Facility Schedule` Model"""

    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, current_date, start_date, delivery_date_offset, fill_cycle, no_of_days=None, **kwargs):
        response = get_expected_schedule(current_date, start_date, delivery_date_offset, fill_cycle, no_of_days)
        return create_response(response)


class GetFacilities(object):
    """
    @class: GetFacilities
    @type: class
    @param: object
    @desc: It returns facility schedule details for given params
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, date_from=None, date_to=None,
            status=None, system_id=None, all_flag=None, filters=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        if date_from is None:
            date_from = settings.DEFAULT_START_DATE
        if date_to is None:
            date_to = settings.DEFAULT_TO_DATE
        if status is None:
            status = settings.PACK_STATUS["Pending"]

        args = {
            "date_from": date_from,
            "date_to": date_to,
            "pack_status": status,
            "company_id": company_id,
            "system_id": system_id
        }
        try:
            if filters:
                args["filter_fields"] = json.loads(filters)
        except json.JSONDecodeError as e:
            return error(1020, str(e))

        if all_flag is not None and int(all_flag):
            args['all_flag'] = True
        else:
            args['all_flag'] = False
        response = get_facility_data_of_pending_packs(args)

        return response


class PharmacyDeliverySync(object):
    """controller for syncing delivery date from IPS to Dosepack and delivery status"""

    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"],
                pharmacy_delivery_sync
            )
            return response
        else:
            return error(1001)


class PatientWiseCalendarSchedule(object):
    """controller for scheduled facility"""

    exposed = True

    @use_database(db, settings.logger)
    def GET(self, company_id=None, start_date=None, end_date=None, facility_list=None, **kwargs):
        if not company_id or not start_date or not end_date:
            return error(1001, "Missing Parameter(s): company_id or start_date or end_date.")
        if facility_list:
            facility_list = facility_list.split(',')
        response = get_patientwise_calender_schedule(company_id, start_date, end_date, facility_list)
        return response
