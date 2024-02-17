import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from src.service.dashboard import get_drug_stat, get_top_drugs, get_pack_error_instances, \
    get_pack_error_distribution, get_extra_pill_error_instances, get_missing_pill_error_instances, \
    get_broken_pill_error_instances, get_misplaced_pill_instances, get_lost_pill_instances, get_pack_error_stats


class GetDrugStats(object):
    """
          @type: class
          @param: object
          @desc:  get the stats of the drugs for past n no of days.
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, no_of_days=None, device_id=None, company_id=None, **kwargs):

        if no_of_days is None or device_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): no_of_days or device_id or company_id.")

        response = get_drug_stat(int(no_of_days), int(device_id), int(company_id))

        return response


class PackErrorStats(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, system_id=None,
            time_zone=None, **kwargs):

        if from_date is None or to_date is None or system_id is None \
                or time_zone is None:
            return error(1001, "Missing Parameter(s): from_date or to_date or system_id or time_zone.")
        args = {
            'from_date': from_date,
            'to_date': to_date,
            'time_zone': time_zone,
            'system_id': system_id
        }
        response = get_pack_error_stats(args)
        return response


class TopDrugs(object):
    """
    Controller for TopDrugs
    """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, system_id=None, from_date=None, to_date=None,
            number_of_drugs=None, **kwargs):
        if not system_id:
            return error(1001, "Missing Parameter(s): system_id.")
        args = {
            "system_id": system_id,
            "from_date": from_date,
            "to_date": to_date
        }
        if number_of_drugs:
            args["number_of_drugs"] = int(number_of_drugs)

        response = get_top_drugs(args)

        return response


class PackErrorInstances(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, system_id=None, company_id=None, time_zone=None,
            period_cycle=None, **kwargs):
        if from_date is None or to_date is None or system_id is None or company_id is None or time_zone is None:
            return error(1001, "Missing Parameter(s): from_date or to_date or system_id or company_id or time_zone.")

        args = {'from_date': from_date, 'to_date': to_date, 'system_id': system_id, 'company_id': company_id,
                'time_zone': time_zone, }

        if period_cycle:
            args['period_cycle'] = period_cycle
        response = get_pack_error_instances(args)
        return response


class PackErrorDistribution(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, system_id=None, company_id=None, time_zone=None,
            period_cycle=None, **kwargs):
        if from_date is None or to_date is None or system_id is None or company_id is None or time_zone is None:
            return error(1001, "Missing Parameter(s): from_date or to_date or system_id or company_id or time_zone.")

        args = {'from_date': from_date, 'to_date': to_date, 'system_id': system_id, 'company_id': company_id,
                'time_zone': time_zone, }

        if period_cycle:
            args['period_cycle'] = period_cycle
        response = get_pack_error_distribution(args)
        return response


class ExtraPillErrors(object):

    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, system_id=None, company_id=None, time_zone=None,
            group=None, graph=None, canister_id=None, location_number=None, device_id=None,
            period_cycle=None, **kwargs):
        if from_date is None or to_date is None or system_id is None or company_id is None or time_zone is None\
                or group is None or graph is None:
            return error(1001, "Missing Parameter(s): from_date or to_date or system_id or company_id or time_zone or "
                               "group or graph.")

        args = {'from_date': from_date, 'to_date': to_date, 'system_id': system_id, 'company_id': company_id,
                'time_zone': time_zone, 'group': group, 'graph': graph}
        if canister_id:
            args['canister_id'] = canister_id
        if location_number and device_id:
            args["location_number"] = location_number
            args["device_id"] = device_id
        if period_cycle:
            args['period_cycle'] = period_cycle
        response = get_extra_pill_error_instances(args)
        return response


class MissingPillErrors(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, system_id=None, company_id=None, time_zone=None,
            group=None, graph=None, canister_id=None, location_number=None, device_id=None,
            period_cycle=None, **kwargs):
        if from_date is None or to_date is None or system_id is None or company_id is None or time_zone is None \
                or group is None or graph is None:  # TODO: graph required or not?
            return error(1001, "Missing Parameter(s): from_date or to_date or system_id or company_id or time_zone or "
                               "group or graph.")
        args = {'from_date': from_date, 'to_date': to_date, 'system_id': system_id, 'company_id': company_id,
                'time_zone': time_zone, 'group': group, 'graph': graph}
        if canister_id:
            args['canister_id'] = canister_id
        if location_number and device_id:
            args["location_number"] = location_number
            args["device_id"] = device_id
        if period_cycle:
            args['period_cycle'] = period_cycle
        response = get_missing_pill_error_instances(args)
        return response


class BrokenPillErrors(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, system_id=None, company_id=None, time_zone=None,
            group=None, graph=None, period_cycle=None, drug=None, total_error_instances=None, **kwargs):
        if from_date is None or to_date is None or system_id is None or company_id is None or time_zone is None \
                or graph is None:
            return error(1001, "Missing Parameter(s): from_date or to_date or system_id or company_id or time_zone or "
                               "graph.")

        args = {'from_date': from_date, 'to_date': to_date, 'system_id': system_id, 'company_id': company_id,
                'time_zone': time_zone, 'graph': graph}

        if period_cycle:
            args['period_cycle'] = period_cycle

        if group:
            args['group'] = group

        if drug:
            args['drug'] = drug

        if total_error_instances:
            args['total_error_instances'] = int(total_error_instances)

        response = get_broken_pill_error_instances(args)
        return response


class MisplacedPillErrors(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, system_id=None, company_id=None, time_zone=None, period_cycle=None, **kwargs):
        if from_date is None or to_date is None or system_id is None or company_id is None or time_zone is None:
            return error(1001, "Missing Parameter(s): from_date or to_date or system_id or company_id or time_zone.")

        args = {'from_date': from_date, 'to_date': to_date, 'system_id': system_id, 'company_id': company_id,
                'time_zone': time_zone}

        if period_cycle:
            args['period_cycle'] = period_cycle

        response = get_misplaced_pill_instances(args)
        return response


class LostPillErrors(object):
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, system_id=None, company_id=None, time_zone=None, **kwargs):
        if system_id is None or company_id is None or time_zone is None:
            return error(1001, "Missing Parameter(s): system_id or company_id or time_zone.")
        args = {'system_id': system_id, 'company_id': company_id, 'time_zone': time_zone}
        response = get_lost_pill_instances(args)
        return response
