import json
from typing import List

import cherrypy

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from src.service.notifications import Notifications


@cherrypy.tools.json_out()
class NotificationsController(object):
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def GET(self, company_id=None, user_id=None):
        if company_id is None or user_id is None:
            return error(1001, "Missing Parameter(s): company_id or user_id.")
        Notifications().send(company_id, user_id, 1, "Test Message", flow='dp');

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def DELETE(self, company_id=None, user_id=None, message_id_list=None, clear_all: bool = False,
               document_id_list: List[str] = None):
        """
        --> We have introduced two more fields to ease the handling of Clear All Notifications.
        --> Currently it was sending details of all the Notification IDs in list form and in some instances the API
        failed because it could not handle the larger length of IDs.
        --> As a solution, we are going to get document_ids in list form for which we need to clear the Notifications
        as this will help in reducing the traffic during API communication.
        """

        # Marking any single notification as Read
        if not clear_all:
            if company_id is None or user_id is None or message_id_list is None:
                return error(1001, "Missing Parameter(s): company_id or user_id or message_id_list.")
            else:
                message_id_list = json.loads(message_id_list)

        # Applying Clear All option for Notifications
        else:
            if company_id is None or user_id is None or document_id_list is None:
                return error(1001, "Missing Parameter(s): company_id or user_id or document_id_list.")
            else:
                message_id_list = json.loads(document_id_list)

        Notifications().remove(message_id_list, clear_all)
        return create_response("success")

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            args = json.loads(kwargs['args'])
            if args['company_id'] is None or args['user_id'] is None or args['message_id_list'] is None:
                return error(1001, "Missing Parameter(s): company_id or user_id or message_id_list.")
            status = Notifications().update(args['message_id_list'])
        else:
            return error(1001)
        return create_response(status)
