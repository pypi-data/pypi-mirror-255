import logging
import operator
import os
import sys
from collections import defaultdict
from datetime import datetime, date
from functools import reduce
from typing import List, Dict, Any
from uuid import uuid4

from peewee import IntegrityError, DataError, InternalError, DoesNotExist, fn, ProgrammingError, JOIN_LEFT_OUTER
from playhouse.shortcuts import case

import settings
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import log_args_and_response

from src import constants
from src.dao.mfd_dao import update_mfs_data_in_couch_db, check_and_update_mfd_module_for_all_batch_mfd_skipped_couch_db
from src.exceptions import FileParsingException, AutoProcessTemplateException
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_header import PackHeader
from src.model.model_pack_queue import PackQueue
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_temp_slot_info import TempSlotInfo
from src.model.model_template_master import TemplateMaster
from src.service.misc import get_userid_by_ext_username
from src.model.model_ext_change_rx import ExtChangeRx
from src.model.model_ext_change_rx_details import ExtChangeRxDetails
from src.model.model_ext_changerx_json import ExtChangeRxJson
from src.model.model_ext_pack_details import ExtPackDetails


logger = logging.getLogger("root")


@log_args_and_response
def process_change_rx_insert_data(template_master_data: List[Dict[str, Any]], company_id: int,
                                  data_dict: Dict[str, Any]) -> bool:

    ext_change_rx_dict: Dict[str, Any] = dict()
    ext_change_rx_id: int
    ext_change_rx_json_dict: Dict[str, Any] = dict()
    ext_change_rx_details_list: List[Dict[str, Any]] = list()
    data_rx_list: List[Dict[str, Any]] = list()
    insert_status: int = 0

    try:
        for template in template_master_data:
            logger.debug("Insert data into ext_change_rx table...")
            ext_change_rx_dict = {"current_template": template["id"],
                                  "ext_action": settings.PENDING_CHANGE_RX_TEMPLATE_STATUS_TEMPLATE,
                                  "new_template": template["id"],
                                  "company_id": company_id}
            ext_change_rx_id = insert_ext_change_rx_data_dao(ext_change_rx_dict=ext_change_rx_dict)

            # file_id = template["file_id"]
            # template_id = template["id"]
            # patient_id = template["patient_id"]
            # pharmacy_patient_id = data_dict["pharmacy_patient_id"]

            logger.info("Prepare the JSON related dictionary to store the JSON data for Change Rx")
            ext_change_rx_json_dict = {"ext_change_rx_id": ext_change_rx_id,
                                       "ext_data": str(data_dict)}
            insert_status = insert_ext_change_rx_json_dao([ext_change_rx_json_dict])

            logger.info("Start Processing ChangeRx based on actions taken in IPS.")
            data_rx_list = data_dict["rx_change_details"]

            for rx_detail in data_rx_list:
                start_date = datetime.strptime(rx_detail["fill_start_date"], "%Y%m%d").date()
                end_date = datetime.strptime(rx_detail["fill_end_date"], "%Y%m%d").date()
                change_rx_action = rx_detail["status"]
                pharmacy_rx_no = rx_detail["pharmacy_rx_no"]
                change_rx_comment = rx_detail["rx_change_comment"]

                change_rx_user_name = rx_detail["rx_change_user_name"]
                user_info = get_userid_by_ext_username(change_rx_user_name, company_id)
                if user_info and "id" in user_info:
                    user_id = user_info["id"]
                else:
                    logger.error("Error while fetching user_info for rx_change_user_name {}".
                                 format(change_rx_user_name))
                    return constants.ERROR_CODE_INVALID_USER_IPS_DOSEPACK
                logger.info("userinfo: {} for ips_username: {}".format(user_info, change_rx_user_name))

                # ----------- 2. Prepare the Insert Dictionary for ext_change_rx_details table -----------
                logger.info("Prepare ext_change_rx_details Dictionary.")
                ext_change_rx_details_list.append({
                    "ext_change_rx_id": ext_change_rx_id,
                    "ext_pharmacy_rx_no": pharmacy_rx_no,
                    "action_id": change_rx_action,
                    "ext_comment": change_rx_comment,
                    "start_date": start_date,
                    "end_date": end_date,
                    "created_by": user_id
                })

            insert_status = insert_ext_change_rx_details_dao(ext_change_rx_details_list)

            if insert_status > 0:
                return True
            else:
                return False

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def update_ext_change_rx_new_template_dao(ext_change_rx_new_template_dict: Dict[str, Any], ext_change_rx_id: list):
    try:
        ExtChangeRx.update_ext_change_rx_new_template(data_list=ext_change_rx_new_template_dict,
                                                      ext_change_rx_id=ext_change_rx_id)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except (DoesNotExist, Exception) as e:
        logger.error(e, exc_info=True)
        raise Exception


@log_args_and_response
def db_get_ext_change_rx_record(old_pharmacy_fill_id: List[int], template_id: int, company_id: int) -> Dict[str, Any]:
    ext_change_rx_data: Dict[str, Any] = {}
    clauses = list()
    try:
        clauses.append(ExtPackDetails.ext_company_id == company_id)
        clauses.append(ExtChangeRx.ext_action == settings.PENDING_CHANGE_RX_TEMPLATE_STATUS_PACK)
        if old_pharmacy_fill_id:
            clauses.append(ExtPackDetails.ext_pack_display_id << old_pharmacy_fill_id)

        if template_id:
            clauses.append(ExtChangeRx.new_template == template_id)

        query = ExtPackDetails.select(ExtChangeRx.id, ExtChangeRx.ext_action,
                                      ExtChangeRx.current_template, ExtChangeRx.new_template).dicts()\
            .join(ExtChangeRx, on=ExtPackDetails.ext_change_rx_id == ExtChangeRx.id) \
            .where(reduce(operator.and_, clauses))\
            .group_by(ExtChangeRx.id)\
            .order_by(ExtChangeRx.id)

        for ext_data in query:
            # Here it is assumed that Old templates in case of multiple templates, 1st's status will be considered
            # Also There will be only one "new template"
            if not "ext_change_rx_id" in ext_change_rx_data:
                ext_change_rx_data["ext_change_rx_id"] = [ext_data["id"]]
                ext_change_rx_data["current_template"] = [ext_data["current_template"]]
                ext_change_rx_data["new_template"] = ext_data["new_template"]
                ext_change_rx_data["ext_action"] = ext_data["ext_action"]
                continue

            ext_change_rx_data["ext_change_rx_id"].append(ext_data["id"])
            ext_change_rx_data["current_template"].append(ext_data["current_template"])

        return ext_change_rx_data

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise FileParsingException


@log_args_and_response
def db_get_pharmacy_fill_id_by_ext_id_dao(ext_change_rx_id):
    try:
        return ExtPackDetails.db_get_pharmacy_fill_id_by_ext_id(ext_change_rx_id=ext_change_rx_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException


@log_args_and_response
def db_get_old_template_by_new_template_dao(template_id: int):
    try:
        return ExtChangeRx.db_get_old_template_by_new_template(template_id=template_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def db_get_linked_packs(pharmacy_patient_id, company_id, fill_start_date, fill_end_date) -> List[int]:
    old_pharmacy_fill_id: List[int] = []
    try:
        query = TemplateMaster.select(fn.GROUP_CONCAT(fn.DISTINCT(ExtPackDetails.ext_pack_display_id))
                                      .coerce(False).alias("old_pharmacy_fill_id")).dicts() \
            .join(ExtChangeRx, on=TemplateMaster.id == ExtChangeRx.current_template) \
            .join(ExtPackDetails, on=ExtPackDetails.ext_change_rx_id == ExtChangeRx.id) \
            .join(PatientMaster, on=TemplateMaster.patient_id == PatientMaster.id) \
            .where(TemplateMaster.company_id == company_id,
                   PatientMaster.company_id == company_id, PatientMaster.pharmacy_patient_id == pharmacy_patient_id,
                   ExtChangeRx.ext_action == settings.PENDING_CHANGE_RX_TEMPLATE_STATUS_PACK,
                   ExtChangeRx.new_template.is_null(True),
                   TemplateMaster.fill_start_date <= fill_start_date, TemplateMaster.fill_end_date >= fill_end_date) \
            .group_by(TemplateMaster.id)

        for ext_pack_data in query.dicts():
            if ext_pack_data["old_pharmacy_fill_id"] is not None:
                old_pharmacy_fill_id += list(map(lambda x: int(x), ext_pack_data["old_pharmacy_fill_id"].split(',')))

        return old_pharmacy_fill_id

    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_check_linked_change_rx_details_by_patient_and_file(patient_id: int, file_id: int) -> bool:
    try:
        query = TemplateMaster.select(ExtChangeRx).dicts()\
            .join(ExtChangeRx, on=TemplateMaster.id == ExtChangeRx.new_template)\
            .where(TemplateMaster.patient_id == patient_id, TemplateMaster.file_id == file_id)

        if query.count() > 0:
            return True
        return False
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return False
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_templates_by_template_info(template_dict: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
    file_ids: List[int] = list()
    patient_ids: List[int] = list()

    try:
        logger.debug("Prepare the File and Patient list to fetch the Template status...")
        for display_id, template_data in template_dict.items():
            file_ids.append(template_data["file_id"])
            patient_ids.append(template_data["patient_id"])

        if file_ids and patient_ids:
            return TemplateMaster.db_get_templates_for_file_patient_ids(file_ids=file_ids, patient_ids=patient_ids)

        return []
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_templates_by_file_and_patient_info(file_ids: List[int], patient_ids: List[int]):
    try:
        return TemplateMaster.db_get_templates_for_file_patient_ids(file_ids=file_ids, patient_ids=patient_ids)
    except DoesNotExist as e:
        logger.error("Function: db_get_templates_by_file_and_patient_info -- exception: {}".format(e), exc_info=True)
        return []
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Function: db_get_templates_by_file_and_patient_info -- exception: {}".format(e), exc_info=True)
        raise


@log_args_and_response
def db_get_pack_patient_and_file_info(pack_id_list: List[int]):
    pack_file_patient_dict: Dict[int, List[int]] = {}
    patient_id: int = 0
    distinct_file_id = set()

    try:
        pack_query = PackDetails.select(PackHeader.patient_id, PackHeader.file_id).dicts()\
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id)\
            .where(PackDetails.id << pack_id_list, PackDetails.pack_status != settings.DELETED_PACK_STATUS)

        for pack in pack_query:
            patient_id = pack["patient_id"]
            distinct_file_id.add(pack["file_id"])

        if patient_id and distinct_file_id:
            pack_file_patient_dict[patient_id] = list(distinct_file_id)

        return pack_file_patient_dict
    except DoesNotExist as e:
        logger.error("Function: db_get_pack_patient_and_file_info -- exception: {}".format(e), exc_info=True)
        return {}
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Function: db_get_pack_patient_and_file_info -- exception: {}".format(e), exc_info=True)
        raise


@log_args_and_response
def db_get_pack_details_by_pack_ids(pack_ids: List[int], packs_delivered: List[int] = None, current_template: int = None):
    pack_display_list_for_change_rx: List[int] = []
    pack_header_ids: List[int] = []
    pack_details: Dict[int, Any] = {}

    try:
        pack_header_ids = db_get_template_pack_header_data(pack_ids=pack_ids, template_id=current_template)
        logger.info("In db_get_pack_details_by_pack_ids: pack_header_id = {}".format(pack_header_ids))
        if pack_header_ids:
            pack_display_list_for_change_rx = PackDetails.get_pack_display_ids_by_pack_header(pack_header_ids=
                                                                                              pack_header_ids)

            # query = PackDetails.select(PackDetails.pack_display_id).dicts()\
            #     .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id)\
            #     .where(PackHeader.pharmacy_fill_id << pack_display_ids)
            #
            # for pack in query:
            #     all_packs_list.append(pack["pack_display_id"])

            if packs_delivered:
                logger.debug("Change Rx Flow -- Ignore Deletion for Packs that are delivered: {}".format(packs_delivered))
                pack_display_list_for_change_rx = list(set(pack_display_list_for_change_rx) - set(packs_delivered))
            logger.info("In db_get_pack_details_by_pack_ids: pack_display_list_for_change_rx = {}".format(pack_display_list_for_change_rx))
            pack_details = PackDetails.db_get_pack_details_by_display_ids(pack_display_ids=pack_display_list_for_change_rx)

        return pack_display_list_for_change_rx, pack_details
    except (InternalError, IntegrityError, ProgrammingError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_template_pack_header_data(pack_ids, template_id=None):
    pack_header_ids = []
    try:
        query = PackDetails.select(PackDetails.pack_header_id).dicts()\
                .join(PackHeader, on=PackDetails.pack_header_id==PackHeader.id) \
                .join(TemplateMaster, on=((TemplateMaster.patient_id == PackHeader.patient_id) & (
                    TemplateMaster.file_id == PackHeader.file_id))) \
                .where(PackDetails.id << pack_ids, TemplateMaster.id == template_id)
        for pack_header in query:
            pack_header_ids.append(pack_header["pack_header_id"])
        return pack_header_ids
    except (InternalError, IntegrityError, ProgrammingError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pack_ids_by_pack_display_id_dao(pack_display_ids, company_id):
    try:
        return PackDetails.db_get_pack_ids_by_pack_display_id(pack_display_ids=pack_display_ids,
                                                              company_id=company_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_check_ext_pack_status_on_hold_dao(pack_display_ids):
    try:
        return ExtPackDetails.db_check_ext_pack_status_on_hold(pack_display_ids=pack_display_ids)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_check_ext_pack_status_on_hold_by_pack_id_dao(pack_ids: List[int]):
    try:
        return ExtPackDetails.db_check_ext_pack_status_on_hold_by_pack_ids(pack_ids=pack_ids)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pack_display_ids_on_hold_dao(pack_display_ids: List[int]):
    try:
        return ExtPackDetails.db_get_ext_pack_display_ids_on_hold(pack_display_ids=pack_display_ids)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_check_pack_marked_for_delete_dao(pack_id: int):
    try:
        return ExtPackDetails.db_check_pack_marked_for_delete(pack_id=pack_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def insert_ext_change_rx_data_dao(ext_change_rx_dict: Dict[str, Any]) -> int:
    """
    Returns the newly generated ID from ext_change_rx table during insertion.
    During update, we are not really concerned about the return value because we just need to update the processed date.
    """
    try:
        return ExtChangeRx.insert_ext_change_rx_data(data_list=ext_change_rx_dict)
    except (IntegrityError, DataError, InternalError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_patient_details_dao(patient_id: int) -> Dict[str, Any]:
    patient_details: Dict[str, Any] = {}
    patient_list: List[Dict[str, Any]] = []
    try:
        patient_list = PatientMaster.db_get_patient_name_patient_no_from_patient_id(patient_id=patient_id)
        for patient in patient_list:
            patient_details["patient_name"] = patient["patient_name"]
            patient_details["patient_no"] = patient["patient_no"]

        return patient_details
    except DoesNotExist as ex:
        logger.error(ex, exc_info=True)
        return {}
    except (InternalError, DoesNotExist) as ex:
        logger.error(ex, exc_info=True)
        raise


@log_args_and_response
def db_delete_template_rx_info(patient_id: int, file_ids: List[int], patient_rx_id: int, start_date: date,
                               end_date: date) -> None:
    """
    Performs delete operation for the Rx from TempSlotInfo, that needs to be removed from the packs
    """
    try:
        TempSlotInfo.db_delete_rx_info(patient_id=patient_id, file_ids=list(file_ids),
                                       patient_rx_id=patient_rx_id,
                                       start_date=start_date, end_date=end_date)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def insert_ext_change_rx_details_dao(rx_list: List[Dict[str, Any]]) -> int:
    """
    Inserts records into ext_change_rx_details table.
    """
    try:
        return ExtChangeRxDetails.insert_ext_change_rx_details(rx_list=rx_list)
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def insert_ext_change_rx_json_dao(rx_json_list: List[Dict[str, Any]]) -> int:
    try:
        return ExtChangeRxJson.insert_ext_change_rx_json(rx_json_list=rx_json_list)
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_template_admin_duration_by_template(template_id: int):
    template_dict: Dict[str, Any] = {}
    try:
        template_query = TemplateMaster.select(TemplateMaster.fill_start_date, TemplateMaster.fill_end_date,
                                               TemplateMaster.patient_id, TemplateMaster.file_id,
                                               TemplateMaster.company_id).dicts() \
            .where(TemplateMaster.id == template_id) \
            .group_by(TemplateMaster.patient_id, TemplateMaster.file_id)

        for record in template_query:
            template_dict["fill_start_date"] = record["fill_start_date"]
            template_dict["fill_end_date"] = record["fill_end_date"]
            template_dict["patient_id"] = record["patient_id"]
            template_dict["file_id"] = record["file_id"]
            template_dict["company_id"] = record["company_id"]

        return template_dict
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_packs_count_by_template(template_id: int) -> int:
    """
    --> Mainly used to identify the split at Pack level

    Returns the count of packs for any Template
    """
    try:
        return TemplateMaster.select().dicts() \
            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id))) \
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id) \
            .where(TemplateMaster.id == template_id).count()

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pack_slot_count_by_template(template_id: int):
    """
    --> Mainly used to identify the split at a detail level

    Return the Pack, Slot and HOA data for any template in sorted manner
    * This will help to check the count of records among Old and New Templates
    * This will help to check the data mapping in detailed manner
    """
    try:
        return TemplateMaster.select(PackDetails.id.alias("pack_id"), PackRxLink.patient_rx_id.alias("rx_id"),
                                     SlotHeader.hoa_date.alias("hoa_date"), SlotHeader.hoa_time.alias("hoa_time"),
                                     SlotHeader.pack_grid_id.alias("pack_grid_id"),
                                     SlotDetails.quantity.alias("quantity"), SlotDetails.drug_id.alias("drug_id"))\
            .dicts() \
            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id))) \
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(SlotHeader, on=SlotDetails.slot_id == SlotHeader.id) \
            .where(TemplateMaster.id == template_id)\
            .order_by(PackDetails.id, SlotHeader.hoa_date, SlotHeader.hoa_time, PackRxLink.patient_rx_id)

    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_pack_slot_hoa_split(old_pack_slot_data, new_pack_slot_data) -> bool:
    """
    Compare the data among Old and New Template Packs

    Returns Boolean value
    True = Split identified
    False = No Split
    """
    old_pack_set = set()
    new_pack_set = set()
    try:
        for old_record in old_pack_slot_data:
            old_pack_set.add(old_record["pack_id"] + settings.SEPARATOR + old_record["rx_id"] + settings.SEPARATOR +
                             old_record["hoa_date"] + settings.SEPARATOR + old_record["hoa_time"] + settings.SEPARATOR +
                             old_record["pack_grid_id"] + settings.SEPARATOR +
                             old_record["quantity"] + settings.SEPARATOR + old_record["drug_id"] + settings.SEPARATOR)

        for new_record in new_pack_slot_data:
            new_pack_set.add(new_record["pack_id"] + settings.SEPARATOR + new_record["rx_id"] + settings.SEPARATOR +
                             new_record["hoa_date"] + settings.SEPARATOR + new_record["hoa_time"] + settings.SEPARATOR +
                             new_record["pack_grid_id"] + settings.SEPARATOR +
                             new_record["quantity"] + settings.SEPARATOR + new_record["drug_id"] + settings.SEPARATOR)

        if old_pack_set == new_pack_set:
            return False

        return True
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_mfd_drugs_present_in_pack(template_id):
    mfd_drug_list: List[int] = []
    try:
        query = MfdAnalysisDetails.select(PackDetails.id.alias("pack_id"),
                                          SlotDetails.drug_id.alias("mfd_drug_id")).dicts()\
            .join(SlotDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id)\
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id)\
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id)\
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id)\
            .join(TemplateMaster, on=((PackHeader.patient_id == TemplateMaster.patient_id) &
                                      (PackHeader.file_id == TemplateMaster.file_id)))\
            .where(TemplateMaster.id == template_id)\
            .group_by(SlotDetails.drug_id)

        for record in query:
            mfd_drug_list.append(record["mfd_drug_id"])

        return mfd_drug_list

    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_mfd_slot_by_drug(template_id, common_mfd_drugs):
    try:
        return MfdAnalysisDetails.select(SlotDetails.id.alias("slot_id"), SlotDetails.drug_id.alias("mfd_drug_id"),
                                         PackDetails.id.alias("pack_id"),
                                         PackGrid.slot_number,
                                         SlotDetails.quantity,
                                         DrugMaster.concated_fndc_txr_field().alias("fndc_txr"),
                                         fn.CONCAT(PackDetails.consumption_start_date, ' to ',
                                                   PackDetails.consumption_end_date).alias(
                                             'admin_period'),)\
            .dicts() \
            .join(SlotDetails, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(TemplateMaster, on=((PackHeader.patient_id == TemplateMaster.patient_id) &
                                      (PackHeader.file_id == TemplateMaster.file_id))) \
            .where(TemplateMaster.id == template_id, SlotDetails.drug_id << common_mfd_drugs) \
            .group_by(SlotDetails.id) \
            .order_by(SlotDetails.id)
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_mfd_slot_new_template_by_drug(template_id, common_mfd_drugs):
    try:
        return SlotDetails.select(SlotDetails.id.alias("slot_id"), SlotDetails.drug_id.alias("mfd_drug_id"),
                                  PackDetails.id.alias("pack_id"),
                                  PackGrid.slot_number,
                                  DrugMaster.concated_fndc_txr_field().alias("fndc_txr"),
                                  SlotDetails.quantity,
                                  fn.CONCAT(PackDetails.consumption_start_date, ' to ',
                                            PackDetails.consumption_end_date).alias(
                                      'admin_period'),
                                  )\
            .dicts() \
            .join(PackRxLink, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(PackDetails, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
            .join(TemplateMaster, on=((PackHeader.patient_id == TemplateMaster.patient_id) &
                                      (PackHeader.file_id == TemplateMaster.file_id))) \
            .where(TemplateMaster.id == template_id, SlotDetails.drug_id << common_mfd_drugs) \
            .group_by(SlotDetails.id) \
            .order_by(SlotDetails.id)
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_mfd_drugs_mapping_for_common_drugs(old_template_id: int, new_template_id: int, common_mfd_drugs: List[int]):
    old_mfd_slot_dict= dict()
    new_mfd_slot_dict= dict()
    final_mfd_mapping = {}
    try:
        # TODO -- What should happen if we do not find a matching new slot for the old slot???
        old_mfd_query = db_get_mfd_slot_by_drug(old_template_id, common_mfd_drugs)
        for record in old_mfd_query:
            if record['admin_period'] not in old_mfd_slot_dict.keys():
                old_mfd_slot_dict[record['admin_period']] = dict()
            if record['mfd_drug_id'] not in old_mfd_slot_dict[record['admin_period']].keys():
                old_mfd_slot_dict[record['admin_period']][record['mfd_drug_id']] = list()
            old_mfd_slot_dict[record['admin_period']][record["mfd_drug_id"]].append(record["slot_id"])
        logger.info("db_get_mfd_drugs_mapping_for_common_drugs old_mfd_slot_dict {}".format(old_mfd_slot_dict))

        new_mfd_query = db_get_mfd_slot_new_template_by_drug(new_template_id, common_mfd_drugs)
        for record in new_mfd_query:
            if record['admin_period'] not in new_mfd_slot_dict.keys():
                new_mfd_slot_dict[record['admin_period']] = dict()
            if record['mfd_drug_id'] not in new_mfd_slot_dict[record['admin_period']].keys():
                new_mfd_slot_dict[record['admin_period']][record['mfd_drug_id']] = list()
            new_mfd_slot_dict[record['admin_period']][record["mfd_drug_id"]].append(record["slot_id"])
        logger.info("db_get_mfd_drugs_mapping_for_common_drugs new_mfd_slot_dict {}".format(new_mfd_slot_dict))

        logger.debug("Old MFD Slot Dictionary: {}".format(old_mfd_slot_dict))
        logger.debug("New MFD Slot Dictionary: {}".format(new_mfd_slot_dict))

        for admin_period,drug in old_mfd_slot_dict.items():
            for record in drug.keys():
                old_slot_value = old_mfd_slot_dict[admin_period][record]
                if admin_period in new_mfd_slot_dict and record in new_mfd_slot_dict[admin_period]:
                    new_slot_value = new_mfd_slot_dict[admin_period][record]
                else:
                    new_slot_value = None
                for old_slot in old_slot_value:
                    if new_slot_value:
                        new_slot = new_slot_value.pop(0)
                    else:
                        break
                    final_mfd_mapping[old_slot] = new_slot

        logger.debug("MFD slot level mapping with Old Slot to New Slot: {}".format(final_mfd_mapping))
        return final_mfd_mapping

    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_mfd_drugs_present_in_template(template_id: int, mfd_drug_list: List[int]) -> List[int]:
    mfd_drugs_list_new_template: List[int] = []
    try:
        # drug_query = TemplateMaster.select(PatientRx.drug_id).dicts()\
        #     .join(TempSlotInfo, on=((TemplateMaster.patient_id == TempSlotInfo.patient_id) &
        #                             (TemplateMaster.file_id == TempSlotInfo.file_id)))\
        #     .join(PatientRx, on=TempSlotInfo.patient_rx_id == PatientRx.id)\
        #     .where(TemplateMaster.id == template_id, PatientRx.drug_id << mfd_drug_list)\
        #     .group_by(TempSlotInfo.patient_id, TempSlotInfo.file_id)
        drug_query = TemplateMaster.select(SlotDetails.drug_id).dicts()\
            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id))) \
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id) \
            .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .where(TemplateMaster.id == template_id, SlotDetails.drug_id << mfd_drug_list) \
            .group_by(SlotDetails.drug_id)

        for drug in drug_query:
            mfd_drugs_list_new_template.append(drug["drug_id"])

        return list(set(mfd_drugs_list_new_template))
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return []
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_check_and_map_mfd_drug_for_new_pack(old_template_id: int, new_template_id: int, batch_id: int = None) -> int:
    mfd_mapping_update: int = 0
    old_mfd_slot_ids: List[int] = []
    new_mfd_slot_ids: List[int] = []
    system_id_list: List[int] = []
    linked_mfd_slots: List[int] = []
    remaining_mfd_slots: List[int] = []
    reset_mfd_couch_db = False

    try:
        old_pack_mfd_drug_list = db_get_mfd_drugs_present_in_pack(old_template_id)

        if old_pack_mfd_drug_list:
            logger.debug("MFD drugs found in Old Templates...")
            # new_pack_mfd_drug_list = db_get_mfd_drugs_present_in_template(template_id=new_template_id,
            #                                                               mfd_drug_list=old_pack_mfd_drug_list)
            new_pack_mfd_drug_list = True
            if new_pack_mfd_drug_list:
                logger.debug("MFD drugs found in New Templates. MFD recommendation mapping needs to be done after "
                             "packs are generated...")
                # common_mfd_drugs = list(set(old_pack_mfd_drug_list).intersection(set(new_pack_mfd_drug_list)))
                # if common_mfd_drugs:
                #     logger.debug("Following MFD drugs are common between Old and New Packs: {}"
                #                  .format(common_mfd_drugs))

                # TODO: Need to use the following code while mapping MFD recommendation
                # mfd_mapping_dict = db_get_mfd_drugs_mapping_for_common_drugs(old_template_id, new_template_id,
                #                                                              new_pack_mfd_drug_list)
                #
                # logger.debug("MFD Mapping Dictionary: {}".format(mfd_mapping_dict))
                mfd_mapping_dict = True
                if mfd_mapping_dict:
                    # for old_slot_id, new_slot_id in mfd_mapping_dict.items():
                    #     old_mfd_slot_ids.append(old_slot_id)
                    #     new_mfd_slot_ids.append(new_slot_id)

                    logger.debug("db_check_and_map_mfd_drug_for_new_pack old new list {}, {}".format(old_mfd_slot_ids,
                                                                                                     new_mfd_slot_ids))

                    total_mfd_slots = TemplateMaster.select(fn.DISTINCT(SlotDetails.id)
                                                            .alias("linked_mfd_slots")).dicts()\
                        .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                              (TemplateMaster.file_id == PackHeader.file_id)))\
                        .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id)\
                        .join(PackRxLink, on=PackDetails.id == PackRxLink.pack_id)\
                        .join(SlotDetails, on=PackRxLink.id == SlotDetails.pack_rx_id)\
                        .join(MfdAnalysisDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id)\
                        .where(TemplateMaster.id == old_template_id)

                    linked_mfd_slots = []
                    for slots in total_mfd_slots:
                        linked_mfd_slots.append(slots["linked_mfd_slots"])

                    if linked_mfd_slots:
                        logger.debug("Find the distinct system_id value for the mapping Slot ID for Old Packs..")
                        mfd_query = MfdAnalysisDetails.select(DeviceMaster.system_id).dicts() \
                            .join(MfdAnalysis, on=MfdAnalysisDetails.analysis_id == MfdAnalysis.id) \
                            .join(DeviceMaster, on=MfdAnalysis.mfs_device_id == DeviceMaster.id) \
                            .where(MfdAnalysisDetails.slot_id << linked_mfd_slots) \
                            .group_by(DeviceMaster.system_id)

                        for record in mfd_query:
                            system_id_list.append(record["system_id"])
                        logger.debug("db_check_and_map_mfd_drug_for_new_pack system_id_list {}".format(system_id_list))

                    # if linked_mfd_slots:
                    #     remaining_mfd_slots = list(set(linked_mfd_slots) - set(old_mfd_slot_ids))
                    # logger.info("db_check_and_map_mfd_drug_for_new_pack linked and remaining slots {}, {}".format(
                    #     linked_mfd_slots, remaining_mfd_slots))
                    #
                    # new_seq_tuple = list(tuple(zip(map(str, old_mfd_slot_ids), new_mfd_slot_ids)))
                    # logger.debug("db_check_and_map_mfd_drug_for_new_pack new_seq_tuple {}".format(new_seq_tuple))
                    #
                    # mfd_case_sequence = case(MfdAnalysisDetails.slot_id, new_seq_tuple)
                    # mfd_mapping_update = MfdAnalysisDetails.update(slot_id=mfd_case_sequence)\
                    #     .where(MfdAnalysisDetails.slot_id << old_mfd_slot_ids).execute()
                    # logger.debug("MFD Mapping Update Status: {}".format(mfd_mapping_update))

                    logger.debug("Remaining MFD slots to update skip status for Drug: {}".format(linked_mfd_slots))
                    if linked_mfd_slots:
                        mfd_mapping_update = MfdAnalysisDetails.update(status_id=constants.MFD_DRUG_SKIPPED_STATUS) \
                            .where(MfdAnalysisDetails.slot_id << linked_mfd_slots).execute()
                        logger.debug("MFD Skipped Update Status: {}".format(mfd_mapping_update))

                    if system_id_list:
                        logger.debug("Update MFS_V1 Couch DB document based on appropriate system for Auto-refresh")
                        for system_id in system_id_list:
                            if batch_id:
                                reset_mfd_couch_db = check_and_update_mfd_module_for_all_batch_mfd_skipped_couch_db(batch_id, system_id)

                            trolley_data = {constants.AUTO_REFRESH_BATCH_UUID_KEY: uuid4().hex}
                            status, doc = update_mfs_data_in_couch_db(constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                                      system_id, trolley_data, reset_mfd_couch_db)
                            logger.debug("Update MFS Couch Document. System ID: {}, status: {}, doc: {}"
                                         .format(system_id, status, doc))


        return mfd_mapping_update
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return 0
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_ext_and_pack_details_for_template(template_ids: list):
    try:
        logger.debug("Check the Pack status for Old Packs...")
        ext_packs = TemplateMaster.select(PackDetails, ExtPackDetails.status_id.alias("ext_status_id"),
                                          ExtPackDetails.packs_delivered,
                                          PackQueue.id.alias("pack_queue")).dicts()\
            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id)))\
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id)\
            .join(ExtPackDetails, on=PackDetails.id == ExtPackDetails.pack_id) \
            .join(PackQueue, JOIN_LEFT_OUTER, on= PackQueue.pack_id == PackDetails.id)\
            .where(TemplateMaster.id << template_ids).order_by(TemplateMaster.fill_start_date)
        return ext_packs
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return []
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_get_new_pack_details_for_template(template_id: int):
    try:
        new_packs = TemplateMaster.select(PackDetails).dicts() \
            .join(PackHeader, on=((TemplateMaster.patient_id == PackHeader.patient_id) &
                                  (TemplateMaster.file_id == PackHeader.file_id))) \
            .join(PackDetails, on=PackHeader.id == PackDetails.pack_header_id) \
            .where(TemplateMaster.id == template_id)

        return new_packs
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return []
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_check_and_update_mfd_recommendation_mapping(batch_id: int, old_template_id: int, new_template_id: int) -> bool:
    mfd_analysis_fill_status: bool = False
    delete_old_packs_after_mfd_map: bool = False
    try:
        # Todo: No need to check MFD Analysis Status as it was already checked Template is processed.
        # logger.debug("Check MFD Analysis status to determine if MFD action is already taken...")
        # mfd_analysis_fill_status = db_check_mfd_analysis_status(batch_id, old_template_id)
        # if not mfd_analysis_fill_status:

        mfd_drug_for_new_pack = db_check_and_map_mfd_drug_for_new_pack(old_template_id, new_template_id, batch_id)
        if mfd_drug_for_new_pack:
            delete_old_packs_after_mfd_map = True
        # else:
        #     logger.debug("MFD Filling has already been initiated. Do not delete Old Packs...")

        return delete_old_packs_after_mfd_map
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException


@log_args_and_response
def get_new_template_from_old_packs(pack_ids):
    old_to_new_template = {}
    try:
        new_template = ExtChangeRx.select(ExtChangeRx.current_template, ExtChangeRx.new_template).dicts()\
            .join(ExtPackDetails, on=ExtChangeRx.id == ExtPackDetails.ext_change_rx_id)\
            .where(ExtPackDetails.pack_id << pack_ids).group_by(ExtChangeRx.current_template)
        for record in new_template:
            old_to_new_template[record["current_template"]] = record["new_template"]

        return old_to_new_template
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise AutoProcessTemplateException


@log_args_and_response
def insert_new_rx_based_on_old_one(old_new_rx_dict, template_id, user_id, remaining_refill_dict):
    try:
        logger.info('In insert_new_rx_based_on_old_one')

        insert_list = list()
        new_patient_rx_ids = dict()
        old_patient_rx_ids = dict()
        # template_id = None
        patient_rx_ids_dict = dict()

        query = TemplateMaster.select(PatientRx).dicts() \
                .join(TempSlotInfo, on=((TempSlotInfo.patient_id == TemplateMaster.patient_id) & (TempSlotInfo.file_id == TemplateMaster.file_id))) \
                .join(PatientRx, on=PatientRx.id == TempSlotInfo.patient_rx_id) \
                .where(TemplateMaster.id == template_id,
                       PatientRx.pharmacy_rx_no.in_((list(old_new_rx_dict.keys()) + list(old_new_rx_dict.values())))) \
                .group_by(PatientRx.id)

        for data in query:
            # if not template_id:
            #     template_id = data["template_id"]

            if not patient_rx_ids_dict.get(data['pharmacy_rx_no']):
                patient_rx_ids_dict[data["pharmacy_rx_no"]] = data

        logger.info(f"In insert_new_rx_based_on_old_one, patient_rx_ids_dict: {patient_rx_ids_dict}")

        for old_rx, new_rx in old_new_rx_dict.items():
            if patient_rx_ids_dict.get(new_rx):
                #new rx for already in the db.
                old_patient_rx_ids[old_rx] = patient_rx_ids_dict[old_rx]["id"]
                new_patient_rx_ids[new_rx] = patient_rx_ids_dict[new_rx]['id']
            else:
                #new rx not in the db > need to insert.
                old_patient_rx_ids[old_rx] = patient_rx_ids_dict[old_rx]["id"]
                data = patient_rx_ids_dict[old_rx]
                data.pop("id", None)
                data.pop("template_id", None)
                data.pop("modified_date", None)
                data.pop("created_date", None)
                data["remaining_refill"] = remaining_refill_dict.get(new_rx, 0)
                data["created_by"] = user_id
                data["modified_by"] = user_id
                data["pharmacy_rx_no"] = new_rx
                patient_id = data["patient_id"]
                logger.info(f'In insert_new_rx_based_on_old_one, insert data:{data}')
                try:
                    id = PatientRx.insert(**data).execute()
                except IntegrityError:
                    # this case happens when nfo calls for same patients but diff packs in small time gap.
                    logger.info(f"In insert_new_rx_based_on_old_one, rx: {new_rx} already exists for patien_id: {patient_id}")
                    id = PatientRx.select(PatientRx.id).where(PatientRx.patient_id == patient_id, PatientRx.pharmacy_rx_no == new_rx).get().id
                logger.info(f"In insert_new_rx_based_on_old_one, PatientRx_id: {id}")
                new_patient_rx_ids[str(new_rx)] = id

        # for data in query:
        #     old_patient_rx_ids[data["pharmacy_rx_no"]] = data['id']
        #     data.pop("id", None)
        #     data.pop("modified_date", None)
        #     data.pop("created_date", None)
        #     data["created_by"] = user_id
        #     data["modified_by"] = user_id
        #     data["pharmacy_rx_no"] = old_new_rx_dict[data["pharmacy_rx_no"]]
        #     logger.info(f'In insert_new_rx_based_on_old_one, insert data:{data}')
        #     id = PatientRx.insert(**data).execute()
        #     print(id)
        #     new_patient_rx_ids[data["pharmacy_rx_no"]] = id
        #     # insert_list.append(data)
        #
        # # logger.info(f'In insert_new_rx_based_on_old_one, insert_list:{insert_list}')
        # # if insert_list:
        # #     status = PatientRx.insert_many(insert_list).execute()
        # #     logger.info(f'In insert_new_rx_based_on_old_one, status:{status}')
        # # query = TemplateMaster.select(PatientRx.id,
        # #                               PatientRx.pharmacy_rx_no).dicts() \
        # #     .join(TempSlotInfo, on=(
        # #     (TempSlotInfo.patient_id == TemplateMaster.patient_id) & (TempSlotInfo.file_id == TemplateMaster.file_id))) \
        # #     .join(PatientRx, on=PatientRx.id == TempSlotInfo.patient_rx_id) \
        # #     .where(TemplateMaster.id == template_id,
        # #            PatientRx.pharmacy_rx_no.in_(list(old_new_rx_dict.values()) + list(old_new_rx_dict.keys()))) \
        # #     .group_by(PatientRx.id)
        # #
        # # for data in query:
        # #     if data["pharmacy_rx_no"] in old_patient_rx_ids:
        # #         old_patient_rx_ids[data["pharmacy_rx_no"]] = data['id']
        # #     else:
        # #         new_patient_rx_ids[data["pharmacy_rx_no"]] = data["id"]
        #
        # logger.info(f'In insert_new_rx_based_on_old_one, new_patient_rx_ids:{new_patient_rx_ids}')
        #
        # return new_patient_rx_ids, old_patient_rx_ids

        # q = TemplateMaster.select(TemplateMaster.id.alias("template_id"),
        #                           PatientRx).dicts() \
        #     .join(TempSlotInfo, on=((TempSlotInfo.patient_id == TemplateMaster.patient_id) & (TempSlotInfo.file_id == TemplateMaster.file_id))) \
        #     .join(PatientRx, on=PatientRx.id == TempSlotInfo.patient_rx_id) \
        #     .join(PackHeader, JOIN_LEFT_OUTER, on=((PackHeader.patient_id == TemplateMaster.patient_id) & (PackHeader.file_id == TemplateMaster.file_id))) \
        #     .join(PackDetails, JOIN_LEFT_OUTER, on=PackDetails.pack_header_id == PackHeader.id) \
        #     .where((PackDetails.pack_display_id.in_(pack_display_ids) | TemplateMaster.pharmacy_fill_id.in_(pack_display_ids)),
        #            PatientRx.pharmacy_rx_no.in_(list(old_new_rx_dict.keys()) + list(old_new_rx_dict.values()))) \
        #     .group_by(PatientRx.pharmacy_rx_no)

        # for data in q:
        #     if not template_id:
        #         template_id = data["template_id"]
        #
        #     if not patient_rx_ids_dict.get(data['pharmacy_rx_no']):
        #         patient_rx_ids_dict[data["pharmacy_rx_no"]] = data
        # for old_rx, new_rx in old_new_rx_dict.items():
        #     if patient_rx_ids_dict.get(new_rx):
        #         old_patient_rx_ids[old_rx] = patient_rx_ids_dict[old_rx]["id"]
        #         new_patient_rx_ids[new_rx] = patient_rx_ids_dict[new_rx]['id']
        #     else:
        #         old_patient_rx_ids[old_rx] = patient_rx_ids_dict[old_rx]["id"]
        #         data = patient_rx_ids_dict[old_rx]
        #         data.pop("id", None)
        #         data.pop("template_id", None)
        #         data.pop("modified_date", None)
        #         data.pop("created_date", None)
        #         data["created_by"] = user_id
        #         data["modified_by"] = user_id
        #         data["pharmacy_rx_no"] = new_rx
        #         logger.info(f'In insert_new_rx_based_on_old_one, insert data:{data}')
        #         id = PatientRx.insert(**data).execute()
        #         print(id)
        #         new_patient_rx_ids[new_rx] = id

        logger.info(f'In insert_new_rx_based_on_old_one, new_patient_rx_ids:{new_patient_rx_ids}')

        return new_patient_rx_ids, old_patient_rx_ids

    except Exception as e:
        logger.error("error in insert_new_rx_based_on_old_one {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in insert_new_rx_based_on_old_one: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_temp_slot_info_data(template_id, old_new_rx_dict):
    """
    args: template_id

    returns: temp_slot_info_data = {
                                rx1: {
                                    hoa_time_1: {
                                        date_1: temp_slot_info_id,
                                        date_2: temp_slot_info_id
                                        },
                                    hoa_time_2: {}
                                },
                                rx2: {}
                                }
    """
    try:
        logger.info("In get_temp_slot_info_data")

        temp_slot_info_data: dict = dict()

        query = TemplateMaster.select(PatientRx.pharmacy_rx_no,
                                      TempSlotInfo.hoa_date,
                                      TempSlotInfo.hoa_time,
                                      TempSlotInfo.id).dicts() \
                .join(TempSlotInfo, on=((TempSlotInfo.patient_id == TemplateMaster.patient_id) & (TempSlotInfo.file_id == TemplateMaster.file_id))) \
                .join(PatientRx, on=PatientRx.id == TempSlotInfo.patient_rx_id) \
                .where(TemplateMaster.id == template_id,
                       PatientRx.pharmacy_rx_no.in_(list(old_new_rx_dict.keys())))

        for data in query:

            if not temp_slot_info_data.get(data["pharmacy_rx_no"]):
                temp_slot_info_data[data['pharmacy_rx_no']] = dict()

            if not temp_slot_info_data[data["pharmacy_rx_no"]].get(data["hoa_time"]):
                temp_slot_info_data[data["pharmacy_rx_no"]][data["hoa_time"]] = dict()

            temp_slot_info_data[data["pharmacy_rx_no"]][data["hoa_time"]][data["hoa_date"]] = data["id"]

        return temp_slot_info_data

    except Exception as e:
        logger.error("error in get_temp_slot_info_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_temp_slot_info_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_temp_slot_info(update_dict):
    logger.info("In update_temp_slot_info")
    try:
        status = None
        update_list = []
        info_ids = []
        for patient_rx_id, temp_slot_info_list in update_dict.items():
            info_ids.extend(temp_slot_info_list)
            l = [(temp_slot_info_id, patient_rx_id) for temp_slot_info_id in temp_slot_info_list]
            update_list.extend(l)

        logger.info(f'In update_temp_slot_info, update_list: {update_list}')

        if update_list:
            temp_slot_info_case = case(TempSlotInfo.id, update_list)
            status = TempSlotInfo.update(patient_rx_id=temp_slot_info_case).where(TempSlotInfo.id.in_(info_ids)).execute()

            logger.info(f'In update_temp_slot_info, status: {status}')

        return status

    except Exception as e:
        logger.error("error in update_temp_slot_info {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_temp_slot_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_slot_details_ids(old_new_rx_dict, pack_display_id):
    """
    returns:
        1. slot_details: {hoa_time: {rx_no: {hoa_date: [slot_details_id], ...}, ...}, ...}
        2. slot_pack_dict: {slot_details_id: pack_id, ...}
        3. current_pack_rx_link: {(pack_id, pharmacy_rx_no): {pack_rx_link table}, (): {}, ...}
    """
    try:
        slot_details = dict()
        slot_pack_dict = dict()
        current_pack_rx_link = dict()
        #
        # query = TemplateMaster.select(SlotDetails.id.alias("slot_details_id"),
        #                               PackRxLink.pack_id,
        #                               SlotHeader.hoa_time,
        #                               SlotHeader.hoa_date,
        #                               PatientRx.pharmacy_rx_no,
        #                               PatientRx.id.alias("patient_rx_id"),
        #                               PackRxLink.original_drug_id,
        #                               PackRxLink.bs_drug_id,
        #                               PackRxLink.fill_manually
        #                               ).dicts() \
        #         .join(TempSlotInfo, on=((TempSlotInfo.patient_id == TemplateMaster.patient_id) & (TempSlotInfo.file_id == TemplateMaster.file_id))) \
        #         .join(PatientRx, on=PatientRx.id == TempSlotInfo.patient_rx_id) \
        #         .join(PackRxLink, on=PackRxLink.patient_rx_id == PatientRx.id) \
        #         .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
        #         .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
        #         .where(TemplateMaster.id == template_id,
        #                PatientRx.pharmacy_rx_no.in_(list(old_new_rx_dict.keys()))) \
        #         .group_by(SlotDetails.id) \
        #         .order_by(SlotHeader.hoa_date)

        query = PackDetails.select(SlotDetails.id.alias("slot_details_id"),
                                      PackRxLink.pack_id,
                                      SlotHeader.hoa_time,
                                      SlotHeader.hoa_date,
                                      PatientRx.pharmacy_rx_no,
                                      PatientRx.id.alias("patient_rx_id"),
                                      PackRxLink.original_drug_id,
                                      PackRxLink.bs_drug_id,
                                      PackRxLink.fill_manually).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .where(PackDetails.pack_display_id.in_(pack_display_id),
                   PatientRx.pharmacy_rx_no.in_(list(old_new_rx_dict.keys()))) \
            .group_by(SlotDetails.id) \
            .order_by(SlotHeader.hoa_date)

        logger.info(f"In get_slot_details_ids, query:{query}")

        for data in query:

            slot_pack_dict[data["slot_details_id"]] = data["pack_id"]

            if not current_pack_rx_link.get((data["pack_id"], data["pharmacy_rx_no"])):

                link_data = {"patient_rx_id": data["patient_rx_id"],
                             "pack_id": data["pack_id"],
                             "original_drug_id": data["original_drug_id"],
                             "bs_drug_id": data["bs_drug_id"],
                             "fill_manually": data["fill_manually"]}

                current_pack_rx_link[(data["pack_id"], data["pharmacy_rx_no"])] = link_data
            # current_pack_rx_link.add((data["pack_id"], data["pharmacy_rx_no"]))

            if not slot_details.get(data["hoa_time"]):
                slot_details[data["hoa_time"]] = dict()

            if not slot_details[data["hoa_time"]].get(data["pharmacy_rx_no"]):
                slot_details[data["hoa_time"]][data["pharmacy_rx_no"]] = dict()
            if not slot_details[data["hoa_time"]][data["pharmacy_rx_no"]].get(data['hoa_date']):
                slot_details[data["hoa_time"]][data["pharmacy_rx_no"]][data["hoa_date"]] = list()
            slot_details[data["hoa_time"]][data["pharmacy_rx_no"]][data["hoa_date"]].append(data["slot_details_id"])

        return slot_details, slot_pack_dict, current_pack_rx_link

    except Exception as e:
        logger.error("error in get_slot_details_ids {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_slot_details_ids: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_pack_rx_data(template_id, old_new_rx_dict):
    try:
        query = TemplateMaster.select().dicts() \
                .join(PatientMaster, on=PatientMaster.id == TemplateMaster.patient_id) \
                .join(PatientRx, on=PatientRx.patient_id == PatientMaster.id) \
                .join(PackHeader, on=(PackHeader.patient_id == TemplateMaster.patient_id & PackHeader.file_id == PackHeader.file_id)) \
                .join(PackDetails, on=PackDetails.pack_header_id == PackHeader.id) \
                .where(TemplateMaster.id == template_id,
                       PatientRx.pharmacy_rx_no.in_(list(old_new_rx_dict.keys())))

        start_date = set()

        pass

    except Exception as e:
        logger.error("error in get_pack_rx_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_pack_rx_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def changes_in_pack_rx_link_and_slot_details(final_slot_details, template_id, old_new_rx_dict, new_patient_rx_ids, old_patient_rx_ids, slot_pack_dict, new_old_rx_dict, current_pack_rx_link):
    try:

        can_not_change = set()
        update_pack_rx_link = set()
        final_t_slot_list = dict()
        insert_pack_rx_link_dict_2 = dict()
        status = None
        # query = PackRxLink.select().dicts() \
        #         .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
        #         .join(PatientMaster, on=PatientMaster.id == PatientRx.patient_id) \
        #         .join(TemplateMaster, on=TemplateMaster.patient_id == PatientMaster.id) \
        #         .where(TemplateMaster.id == template_id)\
        #         .group_by(PackRxLink.id)
        #
        # for data in query:
        #     current_pack_rx_link.append((data["pack_id"], data["pharmacy_rx_no"]))
        logger.info(f"In changes_in_pack_rx_link_and_slot_details, current_pack_rx_link: {current_pack_rx_link}")

        for hoa_time, rx_data in final_slot_details.items():
            for rx, slot_id in rx_data.items():
                for slot in slot_id:
                    if (slot_pack_dict.get(slot), rx) in current_pack_rx_link:
                        can_not_change.add((slot_pack_dict.get(slot), rx))
                    else:
                        if (slot_pack_dict.get(slot), new_old_rx_dict[rx]) in current_pack_rx_link and (slot_pack_dict.get(slot), new_old_rx_dict[rx]) not in can_not_change:
                            t = (slot_pack_dict.get(slot),old_patient_rx_ids[new_old_rx_dict[rx]],new_patient_rx_ids[rx])
                            # pack, old_patient_rx_ids, patient_rx_id of new rx
                            update_pack_rx_link.add(t)

                        else:
                            t = (slot_pack_dict.get(slot),new_patient_rx_ids[rx]) # pack , patient_rx_ids
                            # insert_pack_rx_link.add(t)
                            # if not insert_pack_rx_link_dict.get(new_patient_rx_ids[rx]):
                            #     insert_pack_rx_link_dict[new_patient_rx_ids[rx]] = set()
                            # insert_pack_rx_link_dict[new_patient_rx_ids[rx]].add(slot_pack_dict.get(slot))
                            # pack_ids.add(slot_pack_dict.get(slot))
                            # rx_ids.add(old_patient_rx_ids[new_old_rx_dict[rx]])
                            # final_slot_dict[slot] = t
                            if not final_t_slot_list.get(t):
                                final_t_slot_list[t]= []
                            final_t_slot_list[t].append(slot)
                            dd = current_pack_rx_link[(slot_pack_dict.get(slot), new_old_rx_dict[rx])]
                            dd['patient_rx_id'] = t[1]
                            insert_pack_rx_link_dict_2[t] = dd

        logger.info(f'In changes_in_pack_rx_link_and_slot_details, update_pack_rx_link: {update_pack_rx_link}')
        for data in update_pack_rx_link:
            status = PackRxLink.update(patient_rx_id = data[2]).where(PackRxLink.pack_id==data[0], PackRxLink.patient_rx_id == data[1]).execute()
            logger.info(f"In changes_in_pack_rx_link_and_slot_details, update pack_rx_link status: {status}")

        for t, insert_data in insert_pack_rx_link_dict_2.items():
            pack_rx_link_id = PackRxLink.insert(**insert_data).execute()
            if final_t_slot_list.get(t):
                status = SlotDetails.update(pack_rx_id=pack_rx_link_id).where(SlotDetails.id.in_(final_t_slot_list[t])).execute()

        return status
    except Exception as e:
        logger.error("error in changes_in_pack_rx_link_and_slot_details {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in changes_in_pack_rx_link_and_slot_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

