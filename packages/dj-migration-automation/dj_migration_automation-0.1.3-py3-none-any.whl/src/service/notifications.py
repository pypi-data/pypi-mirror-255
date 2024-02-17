import logging
from typing import List

import couchdb
from couchdb import HTTPError

import settings
from dosepack.utilities.utils import get_current_date_time
from src.exceptions import RealTimeDBException
from src.model.model_pack_details import PackDetails
from src.model.model_notification import Notification
from src.model.model_pack_history import PackHistory
from realtime_db.dp_realtimedb_interface import Database
from src.model.model_pack_header import PackHeader
from src.service.misc import get_token, get_users_by_ids, get_current_user, fetch_not_interested_user_for_notification
from src.dao.couch_db_dao import get_couch_db_database_name

logger = logging.getLogger("root")


def db_update_notifications_read(notification_ids: List[int]):
    logger.debug("remove_notification: updating read time for notification_ids - {}".format(notification_ids))
    now = get_current_date_time()
    read_time_update_status = Notification.update(read_date=now).where(
        Notification.id << notification_ids).execute()
    logger.debug("remove_notification: updated read time with status - {}".format(read_time_update_status))


class Notifications:
    _current_user = None
    _company_id = None
    _created_by = None
    _current_user_name = None

    def __init__(self, token=None, user_id=None, call_from_client=False, company_id=None) -> object:

        print("In_Notification: " + str(token) + ' ' + str(user_id) + ' ' + str(call_from_client))

        if call_from_client and user_id is not None:
            print("fetch user details from user id")
            print("current user_id: " + str(user_id))
            self._user_details = get_users_by_ids(str(user_id))

            if self._user_details:
                self._current_user = self._user_details[str(user_id)]
                self._current_user["company_id"] = self._current_user["company"]
            logger.info("current user from user_id:" + str(self._current_user))
        else:
            print("fetch user details by token")
            logger.info('Getting token')
            if not token:
                token = get_token()
            logger.info("token: " + str(token))
            if token != '':
                self._current_user = get_current_user(token)
                logger.info("current user based on token:" + str(self._current_user))

            else:
                self._current_user = {"id": 1, "company_id": 3, "last_name": 'admin', "first_name": 'admin'}
                logger.info("default user as token is null:" + str(self._current_user))

        if self._current_user is not None:
            self._company_id = self._current_user["company_id"] if self._current_user["company_id"] is not None else company_id
            self._created_by = self._current_user["id"]
            self._current_user_name = "{}, {}".format(self._current_user["last_name"],
                                                      self._current_user["first_name"])

    def _insert_history(self, pack_id, action_id, action_date_time=None,
                        old_value=None, new_value=None, message=None, user_id=None, flow=None, from_ips=False,
                        action_taken_by=None):
        """
        This function is to insert details in the PackHistory Table
        @param pack_id: int
        @param action_id: int
        @param action_date_time: datetime
        @param old_value: varchar
        @param new_value: varchar
        @param message: varchar
        @param user_id: int
        @param flow:
        @return: bool
        """
        pack_history_detail = PackHistory(pack_id_id=pack_id, action_id=action_id,
                                          action_taken_by=self._created_by, old_value=old_value,
                                          new_value=new_value, from_ips=from_ips)

        logger.info("1notification_action_time_for_pack_id_{}_for_action_{}: {}".format(pack_id, action_id,
                                                                                         action_date_time))
        if action_date_time is not None:
            pack_history_detail.action_date_time = action_date_time
        else:
            pack_history_detail.action_date_time = get_current_date_time() # passing externally because of default datetime issue

        logger.info("2notification_action_time_for_pack_id_{}_for_action_{}: {}".format(pack_id, action_id,
                                                                                pack_history_detail.action_date_time))

        logger.info("3notification_action_taken_by_for_pack_id_{}_for_action_{}: {}".format(pack_id, action_id,
                                                                                         action_taken_by))
        if action_taken_by is not None:
            pack_history_detail.action_taken_by = action_taken_by

        logger.info("3notification_action_taken_by_for_pack_id_{}_for_action_{}: {}".format(pack_id, action_id,
                                                                                pack_history_detail.action_taken_by))

        pack_history_detail.save()
        if message is not None and user_id is not None and flow is not None:
            self._send_notification(user_id=user_id, message=message, flow=flow)
        return pack_history_detail

    def _send_notification(self, user_id, message, flow='dp', more_info=None,add_current_user=True):
        try:
            logger.info("Input _send_notification {} and {} and {}".format(user_id, message, flow))
            if more_info:
                logger.info("if _send_notification: more_info {}".format(more_info))
            notification = Notification(message=message, created_by=self._created_by, user_id=user_id)
            notification.save()
            database_name = get_couch_db_database_name(company_id=self._company_id)
            user_id = int(user_id)
            cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
            cdb.connect()
            logger.info(
                'notifications {}: message: {}, user_id:{}, flow:{}, created_by:{} '.format(str(self._company_id), message,
                                                                                            str(user_id), flow,
                                                                                            str(self._created_by)))

            for f in flow.split(','):
                notification_data = {
                    "userId": user_id,
                    "message": message,
                    "createdDate": get_current_date_time(),
                    "users": [self._created_by] if add_current_user else [],
                    "view_list": [self._created_by],
                    "more_info": more_info if more_info else {}
                }
                logger.info("In send_notification: notification_data = {}".format(notification_data))
                user_ids = list()
                if user_id == 0:
                    if f == settings.PACK_FILL_WORKFLOW and (settings.DRUG_STOCK_NOTIFICATION_KEYWORD in message):
                        # Find users who don't want notification for drug stock status change in pack fill workflow
                        user_ids = fetch_not_interested_user_for_notification(settings.NOTIFY_PFW_DRUG_STOCK)
                    elif f == settings.PACK_FILL_WORKFLOW and settings.DRUG_ALTERED_NOTIFICATION_KEYWORD in message:
                        # Find users who don't want notification for altered drug in pack fill workflow
                        user_ids = fetch_not_interested_user_for_notification(settings.NOTIFY_PFW_ALTERNATE_DRUG_CHANGE)

                    if user_ids is not None and len(user_ids) > 0:
                        notification_data["users"].extend(user_ids)
                        notification_data["view_list"].extend(user_ids)
                    id = "notifications_{}_all".format(f)
                else:
                    id = "notifications_{}_user_{}".format(f, user_id)
                table = cdb.get(_id=id)
                logger.info("notifications {}: doc_id: {}".format(str(self._company_id), str(id)))
                if table is None:
                    notification_data["_id"] = "{}_{}_{}".format(f, ('c' if user_id == 0 else 'n'), notification.id)
                    table = {"_id": id, "type": id, "data": [notification_data]}
                else:
                    notification_data["_id"] = "{}_{}_{}".format(f, ('c' if user_id == 0 else 'n'), notification.id)
                    table["data"].append(notification_data)
                try:
                    cdb.save(table)
                except (couchdb.http.ResourceConflict, HTTPError) as e:
                    raise RealTimeDBException("Couldn't udpate notification")
            logger.info('notification {} updated: message: {}, user_id:{}, flow:{}, created_by:{} '
                        .format(str(self._company_id), message, str(user_id), flow, str(self._created_by)))
            return notification
        except RealTimeDBException as e:
            raise RealTimeDBException("Couldn't udpate notification")
        except Exception as e:
            logger.error("Error in sending notification: {}".format(e))
            raise e

    def _remove_notification(self, message_id_list, clear_all: bool = False):
        """
        @modified_by: Payal Wadhwani
        @latest_change: input parameter changed to list from string to handle clear all notification case
        @param message_id_list:
        @return:
        """

        logger.debug("In remove_notification: {} to be removed - {} for user- ".format('Messages' if not clear_all else
                                                                                       'Documents', message_id_list,
                                                                                       self._created_by))
        cdb_notification_dict = dict()
        notification_ids: List[int] = list()

        for message_id in message_id_list:

            # Storing Individual Message IDs to remove them for the user
            if not clear_all:
                flow = message_id.split('_')[0]
                message_type = message_id.split('_')[1]
                id = message_id.split('_')[2]
                notification_ids.append(id)

                coudb_db_doc = "notifications_{}_{}".format(flow, 'all' if message_type == 'c' else 'user_{}'.
                                                            format(self._created_by))
            # Storing Document IDs when Clear All option is applied
            else:
                coudb_db_doc = message_id

            if coudb_db_doc not in cdb_notification_dict.keys():
                cdb_notification_dict[coudb_db_doc] = list()
            cdb_notification_dict[coudb_db_doc].append(message_id)

        # For clearing single notification, we have created a common function to update read date because we are going
        # to use it while using Clear All option as well.
        if not clear_all and notification_ids:
            db_update_notifications_read(notification_ids)

        logger.debug("remove_notification: Connecting with couch db")
        database_name = get_couch_db_database_name(company_id=self._company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        logger.debug("remove_notification: Couch db connection successful")

        logger.debug("remove_notification: notification dict - {}".format(cdb_notification_dict))

        for doc_id, notification_message_ids in cdb_notification_dict.items():
            logger.debug("remove_notification: removing notifications - {} for user_id - from doc - {}"
                         .format(notification_message_ids, self._created_by, doc_id))
            table = cdb.get(_id=doc_id)
            items_to_be_popped = list()

            # When Clear All option is applied, we need to store the list of Notification IDs that needs to be marked
            # as read for the user.
            clear_message_ids: List[int] = list()

            if table is not None:
                for i, item in enumerate(table["data"]):
                    # ** For single notification, we are processing the removal for matching Notification ID in the
                    # Couch DB document.
                    # ** For Clear All, we are going to process all the Notification IDs for the selected Couch DB
                    # document.
                    if item["_id"] in notification_message_ids or clear_all:
                        logger.debug("remove_notification: message to be removed: {}".format(item["_id"]))
                        message_type = item["_id"].split('_')[1]
                        if message_type == 'n':
                            # remove notification from the couch db doc as this couch doc is at user level
                            items_to_be_popped.append(item)
                        else:
                            # add user id in users so front end wont show this notification to user
                            if "users" in table["data"][i].keys():
                                table["data"][i]["users"].append(self._created_by)
                            else:
                                table["data"][i]["users"] = [self._created_by]

                    # During Clear All, we need to gather all the Notification IDs from the Couch DB Document to update
                    # appropriately in Database.
                    if clear_all:
                        id = item["_id"].split('_')[2]
                        clear_message_ids.append(id)

                if clear_all and clear_message_ids:
                        db_update_notifications_read(clear_message_ids)

                logger.debug("remove_notification: {} to be popped - {}".format("messages" if not clear_all else
                                                                                "documents", items_to_be_popped))

                for item in items_to_be_popped:
                    table["data"].pop(table["data"].index(item))
                cdb.save(table)
                logger.debug("remove_notification: Removed notification from doc - {}".format(doc_id))
        logger.debug("remove_notification: Removed notifications from all the docs")
        return True

    def _update_notification(self, message_id_list):
        """
        @created_by: Shital Lathiya
        @modified_by: Shital Lathiya
        @latest_change: update notification message in couch db document
        @param message_id_list:
        @return:
        """
        logger.debug("In _update_notification: viewed messages - {}".format(message_id_list))
        cdb_notification_dict = dict()
        for message_id in message_id_list:
            flow = message_id.split('_')[0]
            message_type = message_id.split('_')[1]

            coudb_db_doc = "notifications_{}_{}".format(flow, 'all' if message_type == 'c' else 'user_{}'.format(
                self._created_by))
            if coudb_db_doc not in cdb_notification_dict.keys():
                cdb_notification_dict[coudb_db_doc] = list()
            cdb_notification_dict[coudb_db_doc].append(message_id)

        logger.debug("_update_notification: notification dict - {}".format(cdb_notification_dict))

        logger.debug("_update_notification: Connecting with couch db")
        database_name = get_couch_db_database_name(company_id=self._company_id)
        cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
        cdb.connect()
        logger.debug("_update_notification: Couch db connection successful")

        for doc_id, notification_message_ids in cdb_notification_dict.items():
            logger.debug("_update_notification: updating viewlist with user_id of notifications - {} from doc - {}"
                    .format(self._created_by, notification_message_ids, doc_id))
            table = cdb.get(_id=doc_id)
            if table is not None:
                for i, item in enumerate(table["data"]):
                    if item["_id"] in notification_message_ids:
                        # add user id in view_list so front end wont show as new notification to the user
                        if "view_list" in table["data"][i].keys():
                            table["data"][i]["view_list"].append(self._created_by)
                        else:
                            table["data"][i]["view_list"] = [self._created_by]
                cdb.save(table)
                logger.debug("_update_notification: Updated viewlist of notification in doc - {}".format(doc_id))
        logger.debug("_update_notification: Update viewlist of notifications in all the docs")
        return True

    def send(self, user_id, message, flow, more_info=None):
        return self._send_notification(user_id, message, flow, more_info)

    def send_with_username(self, user_id, message, flow, more_info=None,add_current_user=True):
        return self._send_notification(user_id, "{} by {}.".format(message, self._current_user_name), flow, more_info, add_current_user)

    def remove(self, message_id_list, clear_all: bool = False):
        self._remove_notification(message_id_list, clear_all)

    def update(self, message_id_list):
        status = self._update_notification(message_id_list)
        return status

    def upload(self, pack_id, action_date_time, action_taken_by):
        """
        This function is used to insert history when pack is uploaded.
        @param pack_id: int
        @param action_date_time:datetime
        @return: function
        """
        return self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_UPLOAD,
                                    action_date_time=action_date_time, new_value=action_date_time,
                                    action_taken_by=action_taken_by)

    def drug_alter(self, old_drug_list, new_drug_list, drug_ndc_map, pack_ids, drug_name_map):
        """
        Insert history when drug in a pack is altered.
        @param drug_name_map:
        @param old_drug_list: list
        @param new_drug_list: list
        @param drug_ndc_map:
        @param pack_ids: list
        @return: function call
        """
        for i, old_ndc in enumerate(old_drug_list):
            old_drug_id = int(old_ndc)
            new_drug_id = int(new_drug_list[i])
            for pack_id in pack_ids:
                self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_NDC_CHANGE,
                                     action_date_time=get_current_date_time(),
                                     old_value=old_drug_id, new_value=new_drug_id)
            self._send_notification(0, settings.NOTIFICATION_MESSAGE_CODE_DICT["DRUG_ALTERED"].format(
                drug_name_map[old_drug_id],
                drug_ndc_map[old_drug_id],
                drug_ndc_map[new_drug_id],
                self._current_user_name), flow='dp,pfw')

    def print_label(self, pack_id):
        """
        Insert in PackHistory table when pack label is being printed.
        @param pack_id: int
        @return: function call
        """
        self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_PRINT_LABEL,
                             action_date_time=get_current_date_time(),
                             new_value=pack_id)

    def print_labels(self, pack_ids):
        """
        Insert in PackHistory table when multiple pack labels are being printed.
        @param pack_ids: list
        @return: function call
        """
        for pack_id in pack_ids:
            self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_PRINT_LABEL,
                                 action_date_time=get_current_date_time(),
                                 new_value=pack_id)

    def fill_partially(self, userpacks):
        """
        Insert in PackHistory table when pack is being filled partially.
        @param userpacks: list
        @return: function call
        """
        for userpack in userpacks:
            self._insert_history(pack_id=userpack["pack_id"], action_id=settings.PACK_HISTORY_HOLD_PACK,
                                 action_date_time=get_current_date_time(), new_value=userpack["pack_id"])

    def add_pack_status_change_history(self, pack_status_list, pack_status_change_from_ips=False):
        """
        Testing Remaining
        Insert in PackHistory table when packs are filled.
        @param pack_status_change_from_ips:
        @param pack_status_list: list
        @return: function call
        """
        if pack_status_change_from_ips:
            action_id = settings.PACK_HISTORY_STATUS_CHANGE_FROM_IPS
            from_ips = True
        else:
            action_id = settings.PACK_HISTORY_STATUS_CHANGE
            from_ips = False

        for packs in pack_status_list:
            self._insert_history(pack_id=packs["pack_id"], action_id=action_id,
                                 action_date_time=get_current_date_time(), old_value=packs["old_status"],
                                 new_value=packs["new_status"], from_ips=from_ips)

    def progress(self, pack_status_list):
        """
        Insert in PackHistory table when packs are in Progress.
        @param pack_status_list: list
        @return: function call
        """
        for packs in pack_status_list:
            self._insert_history(pack_id=packs["pack_id"], action_id=settings.PACK_HISTORY_STATUS_CHANGE,
                                 action_date_time=get_current_date_time(), old_value=packs["old_status"],
                                 new_value=packs["new_status"])

    def generate_and_upload(self, file_upload_date, pack_ids):
        # assigned_count = 0
        assign_details = list()
        for index, pack in enumerate(pack_ids):
            self.upload(pack_id=pack["pack_id"], action_date_time="{} {}".format(file_upload_date.created_date,
                                                                                 file_upload_date.created_time),
                        action_taken_by=file_upload_date.created_by)
            self.generate(pack["pack_id"])
            if "assigned_to" in pack and pack["assigned_to"] is not None:
                assign_details.append({"assigned_to": pack["assigned_to"], "assigned_from": pack["assigned_from"]})
        if len(assign_details) > 0:
            self.assign(pack["pack_id"], pack["assigned_to"], pack["assigned_from"])
            # self.send_assign_messages(assign_details)

    def check_and_send_assign_message(self, pack_assign_details):
        for pd in pack_assign_details:
            self.assign(pd["pack_id"], pd["assigned_to"], pd["assigned_from"])
        # self.send_assign_messages(pack_assign_details)

    def send_assign_messages(self, reassign_details):
        user_ids = list()
        user_ids.append('0')
        if reassign_details is not None:
            assigned_counts = {}
            unassigned_counts = {}
            for row in reassign_details:
                if str(row["assigned_to"]) not in user_ids:
                    user_ids.append(str(row["assigned_to"]))
                if row["assigned_from"] is not None and str(row["assigned_from"]) not in user_ids:
                    user_ids.append(str(row["assigned_from"]))
                if row["assigned_to"] not in assigned_counts:
                    assigned_counts[row["assigned_to"]] = 0
                if row["assigned_from"] is not None and row["assigned_from"] not in unassigned_counts \
                        and row["assigned_from"] != row["assigned_to"]:
                    unassigned_counts[row["assigned_from"]] = 0
                assigned_counts[row["assigned_to"]] = assigned_counts[row["assigned_to"]] + 1
                if row["assigned_from"] is not None and row["assigned_from"] != row["assigned_to"]:
                    unassigned_counts[row["assigned_from"]] = unassigned_counts[row["assigned_from"]] + 1
            user_details = get_users_by_ids(",".join(user_ids))
            if user_details is not None:
                for k, v in unassigned_counts.items():
                    if k is not None:
                        if k != self._created_by:
                            self.send(k, "{} has self assigned {} packs that were assigned to you.".format(
                                self._current_user_name, v),
                                      flow='pfw')
                for k, v in assigned_counts.items():
                    if k is not None:
                        if k != self._created_by:
                            self.send(k, "{} new packs are assigned to you by {}.".format(v, self._current_user_name),
                                      flow='pfw')

    def generate(self, pack_id):
        """
        To insert in PackHistory when a pack is generated.
        @param pack_id:int
        @return: function call
        """
        return self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_GENERATE)

    def template_change(self, pack_id):
        """
        To insert in PackHistory when a template is changed
        @param pack_id:int
        @return: function call
        """
        return self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_TEMPLATE_CHANGE)

    def pre_process(self, patient_id, file_id):
        """
        Insert Details in PackHistory during Pack-Preprocessing
        @param patient_id: int
        @param file_id: int
        @return: bool
        """
        query = PackDetails.select(PackDetails.id).dicts() \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .where(PackHeader.file_id == file_id, PackHeader.patient_id == patient_id) \
            .group_by(PackDetails.id)
        for pack in query:
            self._insert_history(pack_id=pack["id"], action_id=settings.PACK_HISTORY_PRE_PROCESS)
        return True

    def assign(self, pack_id, value, value2):
        """
        celery task
        Insert in PackHistory table when pack is assigned_to or reassigned_to.
        @param pack_id: int
        @param value: int
        @param value2: int
        @return: function call
        """
        if value2 is not None:
            return self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_REASSIGNED, old_value=value2,
                                        new_value=value)
        else:
            return self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_ASSIGNED, new_value=value)

    def status(self, pack_id, status, previous_status):
        """
        To insert in PackHistory Table when the status of a pack is being changed.
        @param pack_id: int
        @param status: int
        @param previous_status:int
        @return: function call
        """
        if previous_status is not None:
            return self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_STATUS_CHANGE,
                                        old_value=previous_status, new_value=status)
        return self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_STATUS_CHANGE, new_value=status)

    def scan(self, pack_id):
        """
        To insert in PackHistory table when label of a pack is being scanned.
        @param pack_id: int
        @return: function call
        """
        return self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_SCAN_LABEL)

    def ndc_change(self, pack_id):
        """
        To insert in PackHistory table when NDC of a pack is being changed.
        @param pack_id: int
        @return: function call
        """
        return self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_NDC_CHANGE)

    def ndc_change(self, pack_id):
        return self._insert_history(pack_id=pack_id, action_id=settings.PACK_HISTORY_PRINT_LABEL)

    def stock_change(self, drug_id):
        return self._insert_history(drug_id, action_id=settings.PACK_HISTORY_STOCK_CHANGE)

    def send_transfer_notification(self, user_id: int or None, system_id: int, batch_id: int, device_message: dict, unique_id: int or None, flow='mfd') -> bool:
        try:

            logger.debug("In send_transfer_notification")
            response = list()
            database_name = get_couch_db_database_name(system_id=system_id)
            if user_id is None:
                user_id = self._current_user['id']
            created_by = self._created_by
            if created_by is None:
                created_by=0
            cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
            cdb.connect()
            logger.info(
                'notifications: message: {}, user_id:{}, flow:{}, created_by:{} '.format(device_message,
                                                                                            str(user_id), flow,
                                                                                            str(created_by)))

            for device_id_key, message in device_message.items():
                notification = Notification(message=message, created_by=created_by, user_id=user_id)
                notification.save()
                response.append(notification)
                notification_data = []
                notification_data_dict = {
                    "userId": user_id,
                    "message": message,
                    "createdDate": get_current_date_time(),
                    "users": [created_by],
                    "action_taken_by": None,
                    "view_list": [],
                    "unique_id": unique_id,
                    '_id': notification.id
                }
                id = "mfd_notifications_{}".format(device_id_key)
                type = "mfd_notifications"
                table = cdb.get(_id=id)
                logger.info("notifications {}: doc_id: {}".format(str(created_by), str(id)))
                if table is None:
                    notification_data.append(notification_data_dict)
                    data = {"device_id":device_id_key, "batch_id":batch_id, "notification_data":notification_data}
                    table = {"_id": id, "type": type, "data":data}

                else:
                    if table["data"].get("batch_id") == batch_id:
                        table["data"]["notification_data"].append(notification_data_dict)
                    else:
                        notification_data.append(notification_data_dict)
                        for notification_info in notification_data:
                            notification_info.update({"action_taken_by": None})
                        data = {"device_id": device_id_key, "batch_id": batch_id,
                                "notification_data": notification_data}
                        table["data"] = data
                cdb.save(table)
            logger.info('notification updated: message: {}, user_id:{}, flow:{}, created_by:{} '
                        .format(message, str(user_id), flow, str(created_by)))

            logger.info("Notification response {}".format(response))

        except couchdb.http.ResourceConflict as e:
            logger.error(e)
            raise Exception("EXCEPTION: Document update conflict while transferring canisters.")
        except Exception as e:
            logger.error(e)
            raise Exception("Couch db update failed while transferring canisters")

    def update_transfer_notification_view_list(self, message_id_list, system_id, device_id):
        """
        adds user into view list of notification.
        :param message_id_list:
        :param system_id:
        :param device_id:
        :return:
        """
        try:
            database_name = get_couch_db_database_name(system_id=system_id)
            cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
            cdb.connect()
            id = "mfd_notifications_{}".format(device_id)
            logger.info("notification_document_name: " + str(id))
            table = cdb.get(_id=id)
            if table is not None:
                for message_id in message_id_list:
                    logger.info("message_id:" + str(message_id))
                    for i, item in enumerate(table["data"]["notification_data"]):
                        if item["_id"] == message_id:
                            table["data"]["notification_data"][i]["view_list"].append(self._created_by)
                cdb.save(table)
            return True
        except couchdb.http.ResourceConflict as e:
            logger.error(e)
            raise Exception("EXCEPTION: Document update conflict while transferring canisters.")
        except Exception as e:
            logger.error(e)
            raise Exception("Couch db update failed while transferring canisters")

    def check_if_notification_is_present(self, unique_id, device_id, system_id, batch_id):
        """
        check if notification is already there for trolley and trolley seq
        @param unique_id:
        @param device_id:
        @param system_id:
        @param batch_id:
        @return:
        """
        try:
            database_name = get_couch_db_database_name(system_id=system_id)
            cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
            cdb.connect()
            id = "mfd_notifications_{}".format(device_id)
            type = "mfd_notifications"
            table = cdb.get(_id=id)
            if table is None:
                return False
            else:
                if table["data"].get("batch_id") == batch_id:
                    notification_data = table["data"]["notification_data"]
                    for data in notification_data:
                        if unique_id == data['unique_id']:
                            return True
                else:
                    return False
            return False

        except Exception as e:
            logger.error(e)
            raise Exception("Error in check_if_notification_is_present")