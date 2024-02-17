import json
import settings
from dosepack.base_model.base_model import db
from src.service.pack_ext import get_reusable_packs
from dosepack.error_handling.error_handler import error
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.utilities.manage_db_connection import use_database

logger = settings.logger


class GetReusablePacks(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, filters=None, sort_fields=None, paginate=None, user_id=None, **kwargs):
        if company_id is None:
            return error(1001, "Missing Parameter(s): company_id.")

        args = {"company_id": company_id}

        try:
            if paginate is not None:
                args["paginate"] = json.loads(paginate)

            if filters:
                args["filter_fields"] = json.loads(filters)

            if sort_fields:
                args["sort_fields"] = json.loads(sort_fields)
        except json.JSONDecodeError as e:
            return error(1020, str(e))

        try:
            response = get_reusable_packs(args)
            return response
        except Exception as e:
            logger.error("Error in GetReusablePacks: {}".format(e))
            return error(2001)
