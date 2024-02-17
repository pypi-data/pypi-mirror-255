from typing import List, Dict, Any, Optional

from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, CharField, DateTimeField, InternalError, \
    IntegrityError, DoesNotExist, JOIN_LEFT_OUTER, fn, TextField
from playhouse.shortcuts import case

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_template_master import TemplateMaster
from src.model.model_ext_change_rx import ExtChangeRx

logger = settings.logger


class ExtPackDetails(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails, null=True)
    template_id = ForeignKeyField(TemplateMaster, null=True)
    status_id = ForeignKeyField(CodeMaster, null=True)
    ext_pack_display_id = IntegerField()
    ext_status_id = ForeignKeyField(CodeMaster, related_name='ext_status')
    ext_comment = CharField(null=True)
    ext_company_id = IntegerField()
    ext_user_id = IntegerField()
    ext_created_date = DateTimeField(default=get_current_date_time())
    ext_change_rx_id = ForeignKeyField(ExtChangeRx, null=True)
    packs_delivered = TextField(null=True)
    pharmacy_pack_status_id = ForeignKeyField(CodeMaster, null=True, related_name='pharmacy_pack_status')
    pack_usage_status_id = ForeignKeyField(CodeMaster, related_name='pack_usage_status_id',
                                           default=constants.EXT_PACK_USAGE_STATUS_NA_ID)
    packs_delivery_status = ForeignKeyField(CodeMaster, related_name="pack_delivery_status", null=True)
    ext_modified_date = DateTimeField(default=get_current_date_time)

    # commenting below fields to change table structure according to modified flow
    # This can have values like Checked, Error, Fixed Error, Not Checked
    # rph_verification_status = ForeignKeyField(CodeMaster, related_name="ext_pack_details_rph_verification_status",
    #                                           null=True)
    # rph_reason_code = CharField(null=True)
    # rph_comment = CharField(null=True)
    # rph_ext_user_name = FixedCharField(max_length=64, null=True)
    # rph_user_id = IntegerField(null=True)
    # rph_status_datetime = DateTimeField(null=True)
    #
    # # This can have values like Filled, Deleted, Reuse
    # technician_fill_status = ForeignKeyField(CodeMaster, related_name="ext_pack_details_technician_fill_status",
    #                                          null=True)
    # technician_status_datetime = DateTimeField(null=True)
    # technician_ext_user_name = FixedCharField(max_length=64, null=True)
    # technician_user_id = IntegerField(null=True)
    #
    # # This fields will store delivery information
    # delivery_status = ForeignKeyField(CodeMaster, related_name="ext_pack_details_delivery_status", null=True)
    # delivery_status_datetime = DateTimeField(null=True)
    # delivery_change_ext_user_name = FixedCharField(max_length=64, null=True)
    # delivery_change_user_id = IntegerField(null=True)
    #
    # api_call_created_datetime = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ext_pack_details"

    @classmethod
    def db_check_ext_pack_status_on_hold(cls, pack_display_ids):
        try:
            query = ExtPackDetails.select(ExtPackDetails).dicts() \
                .where(ExtPackDetails.ext_pack_display_id << pack_display_ids,
                       ExtPackDetails.ext_status_id == constants.EXT_PACK_STATUS_CODE_CHANGE_RX_HOLD)

            if query.count() > 0:
                return True
            return False
        except DoesNotExist as e:
            logger.debug("db_check_ext_pack_status_on_hold: No records found on Hold for Pack Display IDs: {}"
                         .format(pack_display_ids))
            return False
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_check_ext_pack_status_on_hold_by_pack_ids(cls, pack_ids):
        try:
            query = ExtPackDetails.select(ExtPackDetails).dicts() \
                .where(ExtPackDetails.pack_id << pack_ids,
                       ExtPackDetails.ext_status_id == constants.EXT_PACK_STATUS_CODE_CHANGE_RX_HOLD)

            if query.count() > 0:
                return True
            return False
        except DoesNotExist as e:
            logger.debug("db_check_ext_pack_status_on_hold: No records found on Hold for Pack IDs: {}"
                         .format(pack_ids))
            return False
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_ext_packs_on_hold(cls, pack_ids):
        ext_pack_ids: List[int] = []
        ext_pack_display_ids: List[int] = []
        ext_data: Dict[str, Any] = {}
        try:
            logger.debug("Inside db_get_ext_packs_on_hold method..")
            query = ExtPackDetails.select(ExtPackDetails, ExtChangeRx.current_template.alias("old_template_id"),
                                          ExtChangeRx.new_template.alias("new_template_id"),
                                          fn.IF(TemplateMaster.with_autoprocess.is_null(True),
                                                False, TemplateMaster.with_autoprocess).alias("with_autoprocess")
                                          ).dicts() \
                .join(ExtChangeRx, on=ExtPackDetails.ext_change_rx_id == ExtChangeRx.id)\
                .join(TemplateMaster, JOIN_LEFT_OUTER, on=ExtChangeRx.new_template == TemplateMaster.id)\
                .where(ExtPackDetails.pack_id << pack_ids,
                       ExtPackDetails.ext_status_id == constants.EXT_PACK_STATUS_CODE_CHANGE_RX_HOLD)

            for ext_pack in query:
                ext_pack_ids.append(ext_pack["pack_id"])
                ext_pack_display_ids.append((ext_pack["ext_pack_display_id"]))
                if not ext_data:
                    ext_data = {"ext_change_rx_id": ext_pack["ext_change_rx_id"],
                                "old_template_id": ext_pack["old_template_id"],
                                "new_template_id": ext_pack["new_template_id"],
                                "company_id": ext_pack["ext_company_id"],
                                "autoprocess_template": ext_pack["with_autoprocess"]
                                }
            return ext_pack_ids, ext_pack_display_ids, ext_data
        except DoesNotExist as e:
            logger.debug("db_get_ext_packs_on_hold: No records found on Hold for Pack IDs: {}".format(pack_ids))
            return ext_pack_ids, ext_pack_display_ids, ext_data
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_ext_pack_display_ids_on_hold(cls, pack_display_ids):
        ext_pack_display_ids: List[int] = []
        try:
            query = ExtPackDetails.select(ExtPackDetails).dicts() \
                .where(ExtPackDetails.ext_pack_display_id << pack_display_ids,
                       ExtPackDetails.ext_status_id == constants.EXT_PACK_STATUS_CODE_CHANGE_RX_HOLD)

            for ext_pack in query:
                ext_pack_display_ids.append(ext_pack["ext_pack_display_id"])
            return ext_pack_display_ids
        except DoesNotExist as e:
            logger.debug("db_get_ext_pack_display_ids_on_hold: No records found on Hold for Pack Display IDs: {}"
                         .format(pack_display_ids))
            return ext_pack_display_ids
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_ext_packs_with_pack_usage_pending(cls, pack):
        ext_pack_ids: List[int] = []
        PackHeaderAlias = PackHeader.alias()
        PackDetailsAlias = PackDetails.alias()
        try:
            logger.debug("Inside db_get_ext_packs_with_pack_usage_pending function..")
            query = PackDetails.select(ExtPackDetails.pack_id.alias("pack_id")).dicts()\
                .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id)\
                .join(PackHeaderAlias, on=PackHeader.patient_id == PackHeaderAlias.patient_id)\
                .join(PackDetailsAlias, on=PackHeaderAlias.id == PackDetailsAlias.pack_header_id)\
                .join(ExtPackDetails, on=PackDetailsAlias.id == ExtPackDetails.pack_id)\
                .where(PackDetails.id == pack,
                       ExtPackDetails.pack_usage_status_id << [constants.EXT_PACK_USAGE_STATUS_PENDING_ID, constants.EXT_PACK_USAGE_STATUS_NA_ID],
                       PackDetailsAlias.pack_status == settings.DELETED_PACK_STATUS,
                       PackDetailsAlias.consumption_start_date >= PackDetails.consumption_start_date,
                       PackDetailsAlias.consumption_end_date <= PackDetails.consumption_end_date)

            logger.debug("Inside db_get_ext_packs_with_pack_usage_pending -- Query: {}".format(query))
            for ext_pack in query:
                ext_pack_ids.append(ext_pack["pack_id"])
            return ext_pack_ids
        except DoesNotExist as e:
            logger.debug("db_get_ext_packs_with_pack_usage_pending: No records found with Pack Usage Status Pending "
                         "for Pack IDs: {}".format(pack))
            return ext_pack_ids
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_ext_pack_usage_status(cls, pack_ids):
        try:
            return ExtPackDetails.update(pack_usage_status_id=constants.EXT_PACK_USAGE_STATUS_DONE_ID)\
                .where(ExtPackDetails.pack_id << pack_ids).execute()
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_ext_status(cls, hold_to_delete_pack_ids: List[int],
                             pack_display_id_status_dict: Optional[Dict[int, Dict[str, Any]]] = None,
                             force_delete: Optional[bool] = False):
        pack_ids: List[int] = []
        pack_status_ids: List[int] = []
        pack_usage_status_ids: List[int] = []
        ext_change_rx_ids: List[int] = []
        try:
            if pack_display_id_status_dict:
                logger.info("When Delete happens after new template is processed, fetch the pack status before it "
                             "gets deleted. {}".format(pack_display_id_status_dict))
                for pack_display_id, ext_pack in pack_display_id_status_dict.items():
                    pack_ids.append(ext_pack["pack_id"])
                    pack_status_ids.append(ext_pack["pack_status"])
                    if ext_pack["pack_status"] in settings.PACK_PROGRESS_DONE_STATUS_LIST:
                        pack_usage_status_ids.append(constants.EXT_PACK_USAGE_STATUS_PENDING_ID)
                    else:
                        pack_usage_status_ids.append(constants.EXT_PACK_USAGE_STATUS_NA_ID)

            else:
                logger.info("When Delete happens during Intimation call or Delete, fetch the pack status directly "
                            "from Pack Details. {}".format(hold_to_delete_pack_ids))
                ext_query = ExtPackDetails.select(PackDetails.id.alias("pack_id"),
                                                  PackDetails.pack_status.alias("pack_status"),
                                                  ExtPackDetails.ext_change_rx_id).dicts()\
                    .join(PackDetails, on=ExtPackDetails.pack_id == PackDetails.id)\
                    .where(PackDetails.id << hold_to_delete_pack_ids)

                for ext_pack in ext_query:
                    pack_ids.append(ext_pack["pack_id"])
                    pack_status_ids.append(ext_pack["pack_status"])
                    if ext_pack["pack_status"] in settings.PACK_PROGRESS_DONE_STATUS_LIST:
                        pack_usage_status_ids.append(constants.EXT_PACK_USAGE_STATUS_PENDING_ID)
                    else:
                        pack_usage_status_ids.append(constants.EXT_PACK_USAGE_STATUS_NA_ID)

                    if ext_pack["ext_change_rx_id"]:
                        ext_change_rx_ids.append(ext_pack["ext_change_rx_id"])

            new_status_seq_tuple = list(tuple(zip(map(str, pack_ids), pack_status_ids)))
            update_status_case_sequence = case(ExtPackDetails.pack_id, new_status_seq_tuple)

            new_pack_usage_status_seq_tuple = list(tuple(zip(map(str, pack_ids), pack_usage_status_ids)))
            update_pack_usage_status_case_sequence = case(ExtPackDetails.pack_id,
                                                          new_pack_usage_status_seq_tuple)

            logger.debug("Update Status Case: {}, Update Pack Usage Status Case: {}"
                         .format(update_status_case_sequence, update_pack_usage_status_case_sequence))
            ext_pack_update = ExtPackDetails.update(status_id=update_status_case_sequence,
                                                    ext_status_id=constants.EXT_PACK_STATUS_CODE_DELETED,
                                                    ext_comment=constants.DELETE_REASON_EXT_CHANGE_RX,
                                                    pack_usage_status_id=update_pack_usage_status_case_sequence) \
                .where(ExtPackDetails.pack_id << pack_ids)
            logger.info("In db_update_ext_status: ext_pack_update query {}".format(ext_pack_update.sql()))
            ext_pack_update.execute()

            logger.debug("ExtChangeRx IDs: {}".format(ext_change_rx_ids))
            if force_delete and ext_change_rx_ids:
                logger.info(
                    "In db_update_ext_status: Trying to set new_template=0 while force delete for extchangerx ids = {}".format(
                        ext_change_rx_ids))
                ext_change_rx_ids = list(set(ext_change_rx_ids))
                ext_change_rx_update = ExtChangeRx.update(new_template=None, modified_date=get_current_date_time())\
                    .where(ExtChangeRx.id << ext_change_rx_ids).execute()
                logger.debug("Update ExtChangeRx Status: {}".format(ext_change_rx_update))
            #
            # ExtPackDetails.update(ext_status_id=constants.EXT_PACK_STATUS_CODE_DELETED)\
            #     .where(ExtPackDetails.pack_id << hold_to_delete_pack_ids)
            return ext_pack_update
        except (InternalError, IntegrityError, Exception) as e:
            logger.info("Error in db_update_ext_status: {}".format(e))
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_pharmacy_fill_id_by_ext_id(cls, ext_change_rx_id: int) -> List[int]:
        ext_pharmacy_fill_id: List[int] = []
        try:
            query = ExtPackDetails.select(ExtPackDetails).dicts()\
                .where(ExtPackDetails.ext_change_rx_id == ext_change_rx_id)

            for ext_pack in query:
                ext_pharmacy_fill_id.append(ext_pack["ext_pack_display_id"])

            return ext_pharmacy_fill_id
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return []
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_check_pack_marked_for_delete(cls, pack_id: int) -> bool:
        try:
            query = ExtPackDetails.select().dicts().where(ExtPackDetails.pack_id == pack_id)
            if query.count() > 0:
                return True

            return False
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return False
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_ext_pack_details_by_pack_id(cls, pack_ids, update_dict):
        try:
            logger.info("In db_update_ext_pack_status_by_pack_id with pack_ids: {}, update_dict: {}"
                        .format(pack_ids, update_dict))
            return ExtPackDetails.update(**update_dict) \
                .where(ExtPackDetails.pack_id << pack_ids).execute()
        except Exception as e:
            logger.error("Error in db_update_ext_pack_status_by_pack_id: {}".format(e))
            raise e

    @classmethod
    def db_insert_many_records_in_ext_pack_details(cls, data_list):
        try:
            logger.info("In db_insert_many_records_in_ext_pack_details: with data_list: {}".format(data_list))
            return ExtPackDetails.insert_many(data_list).execute()

        except Exception as e:
            logger.error("Error in db_insert_many_records_in_ext_pack_details: {}".format(e))
            raise e

    @classmethod
    def db_get_ext_pack_data_by_pack_ids(cls, pack_ids):
        try:
            logger.info("In db_get_ext_pack_data_by_pack_id: with pack_ids: {}".format(pack_ids))
            query = (ExtPackDetails.select(ExtPackDetails)
                     .dicts()
                     .where(ExtPackDetails.pack_id << pack_ids)
                     )

            return query

        except Exception as e:
            logger.error("Error in db_get_ext_pack_data_by_pack_id: {}".format(e))
            raise e
