import json

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.generate_templates import get_all_templates, get_template_data, get_template_data_v2, set_template_data, \
    get_rollback_templates, rollback_templates, update_reddis_data, get_store_separate_drugs, add_store_separate_drug, \
    delete_store_separate_drug


class GetTemplates(object):
    """
          @class: GetAllTemplateInfo
          @type: class
          @param: object
          @desc: get all the templates which has same status as provided in parameters.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, status=None, company_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        if status is None:
            status = settings.PENDING_TEMPLATE_LIST

        args = {"status": status, "company_id": company_id}

        response = get_all_templates(args)

        return response


class GetTemplate(object):
    """
          @class: GetTemplateData
          @type: class
          @param: object
          @desc: get the template data for the given patient id, system id and file id
    """
    exposed = False

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, patient_id=None, file_id=None, company_id=None, **kwargs):

        if patient_id is None or file_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): patient_id or file_id or company_id.")

        args = {
            "patient_id": patient_id,
            "file_id": file_id,
            "company_id": company_id
        }

        response = get_template_data(args)

        return response


class GetTemplateV2(object):
    """
          @class: GetTemplateV2
          @type: class
          @param: object
          @desc: get the template data for the given patient id and file id
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, patient_id=None, file_id=None, company_id=None, **kwargs):
        if patient_id is None or file_id is None or company_id is None:
            return error(1001, "Missing Parameter(s): patient_id or file_id or company_id.")

        args = {
            "patient_id": patient_id,
            "file_id": file_id,
            "company_id": company_id
        }
        response = get_template_data_v2(args)

        return create_response(response)


class SaveTemplate(object):
    """
          @class: StoreTemplateData
          @type: class
          @param: object
          @desc: stores the template data for the given patient group no
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], set_template_data
            )
        else:
            return error(1001)

        return response


class RollbackTemplate(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, filters=None, sort_fields=None, paginate=None,
            company_id=None, time_zone=None, **kwargs):
        if company_id is None or time_zone is None:
            return error(1001, "Missing Parameter(s): company_id or time_zone.")
        try:
            args = {
                "company_id": company_id,
                "time_zone": time_zone,
            }
            if paginate is not None:
                args["paginate"] = json.loads(paginate)
            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))

        response = get_rollback_templates(args)

        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], rollback_templates
            )
        else:
            return error(1001)

        return response


class UpdateTemplateQueue(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        response = update_reddis_data(company_id)

        return response


class StoreSeparateDrug(object):
    """ Controller for `StoreSeparateDrug` """
    exposed = True

    # @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, filters=None, sort_fields=None, paginate=None,
            company_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")
        try:
            args = {
                "company_id": company_id
            }
            if paginate is not None:
                args["paginate"] = json.loads(paginate)
            if filters:
                args["filter_fields"] = json.loads(filters)
            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))

        response = get_store_separate_drugs(args)

        return response

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], add_store_separate_drug
            )
        else:
            return error(1001)

        return response


class DeleteStoreSeparateDrug(object):
    """ Controller to delete  """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], delete_store_separate_drug
            )
        else:
            return error(1001)

        return response
