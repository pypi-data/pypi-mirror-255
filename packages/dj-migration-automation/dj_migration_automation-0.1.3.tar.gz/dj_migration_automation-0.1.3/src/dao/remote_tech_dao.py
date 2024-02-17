import functools
import operator
import threading
from datetime import datetime, timedelta
from functools import reduce

import cherrypy
from peewee import InternalError, IntegrityError, DoesNotExist, DataError, fn, JOIN_LEFT_OUTER

import settings
from com.pharmacy_software import set_authorization_headers
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import log_args_and_response, call_webservice
from src.dao.drug_dao import dpws_paginate
from src.exc_thread import ExcThread
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_rx import PatientRx
from src.model.model_prs_drug_details import PRSDrugDetails
from src.model.model_rts_slot_assign_info import RtsSlotAssignInfo
from src.model.model_slot_details import SlotDetails
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src.model.model_slot_header import SlotHeader
from src.model.model_pack_details import PackDetails
from src.model.model_pack_grid import PackGrid
from src import constants
from src.api_utility import get_results_prs, get_results
from src.model.model_pvs_slot import PVSSlot
from src.model.model_pvs_slot_details import PVSSlotDetails
from src.model.model_remote_tech_slot import RemoteTechSlot
from src.model.model_remote_tech_slot_details import RemoteTechSlotDetails
logger = settings.logger


@log_args_and_response
def validate_pvs_slot_id(pvs_slot_id: int) -> bool:
    """
    This function validates the pvs_slot_id from PVSSlot table.
    @param pvs_slot_id:
    @return:
    """
    logger.debug("Inside validate_pvs_slot_id.")
    try:
        query = PVSSlot.select().dicts() \
            .where(PVSSlot.id == pvs_slot_id)
        logger.debug(query)
        if query.count() == 1:
            return True
        else:
            return False

    except (DoesNotExist, IntegrityError, InternalError) as e:
        logger.error(e)
        raise


@log_args_and_response
def add_remote_tech_slot_data(remote_tech_slot_data: dict) -> int:
    """
    This calls the class method of RemoteTechSlot to add data.
    @param remote_tech_slot_data: dict
    @return: int
    """
    logger.debug("Inside add_remote_tech_slot_data: {}".format(remote_tech_slot_data))
    try:
        record = BaseModel.db_create_record(remote_tech_slot_data, RemoteTechSlot, get_or_create=False)
        return record.id
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def get_unique_drug_id(formatted_ndc_txr_list: list) -> dict:
    """
    This fetches the unique_drug_id corresponding to the fndc_txr list
    @param formatted_ndc_txr_list:list
    @return:
    """
    logger.debug("Inside get_unique_drug_id.")
    try:
        return UniqueDrug.db_get_unique_drug_id(formatted_ndc_txr_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.info(e)
        raise


@log_args_and_response
def get_pvs_slot_details(pvs_slot_id: int) -> dict:
    """
    This fetches the pvs_slot_details data for the pvs_slot_id by calling the class method of PVSSlotDetails.
    @param pvs_slot_id:int
    @return:dict
    """
    logger.debug("Inside get_pvs_slot_details_id.")
    try:
        query = PVSSlotDetails.select(PVSSlotDetails.id, PVSSlotDetails.crop_image_name).dicts() \
            .where(PVSSlotDetails.pvs_slot_id == pvs_slot_id)
        logger.debug(query)
        return query
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        raise


def add_remote_tech_slot_details_data(remote_tech_slot_details_data: list) -> bool:
    """
    Inserts multiple records in the RemoteTechSlotDetails table.
    @param remote_tech_slot_details_data:
    @return:
    """
    logger.debug("Inside add_remote_tech_slot_details_data {}".format(remote_tech_slot_details_data))
    try:
        RemoteTechSlotDetails.insert_many(remote_tech_slot_details_data).execute()
        return True
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def get_pvs_and_rts_slot_data(pvs_slot_id: int) -> dict:
    """
    Fetches data from PVSSlot & RemoteTechSlot table based on the pvs_slot_id.
    @param pvs_slot_id:
    @return:
    """
    logger.debug("Inside get_pvs_and_rts_slot_data.")
    try:
        query = PVSSlot.select(PVSSlot.id.alias("pvs_slot_id"),
                               PVSSlot.slot_image_name.alias("slot_image_name"),
                               SlotHeader.pack_id,
                               SlotHeader.pack_grid_id,
                               PackGrid.slot_number,
                               RemoteTechSlot.id.alias("remote_tech_slot_id"),
                               RemoteTechSlot.remote_tech_id,
                               RemoteTechSlot.verification_status,
                               RemoteTechSlot.start_time,
                               RemoteTechSlot.end_time) \
            .dicts() \
            .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
            .join(PackGrid, on=SlotHeader.pack_grid_id == PackGrid.id) \
            .join(RemoteTechSlot, on=RemoteTechSlot.pvs_slot_id == PVSSlot.id) \
            .where(PVSSlot.id == pvs_slot_id).order_by(RemoteTechSlot.id.desc()).limit(1)
        logger.debug(query)

        for record in query:
            return record

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        raise


@log_args_and_response
def get_pvs_and_rts_slot_details_data(pvs_slot_id: int, remote_tech_slot_id) -> dict:
    """
    Fetches data from PVSSlotDetails & RemoteTechSlotDetails table based on the pvs_slot_id.
    @param pvs_slot_id:
    @return:
    """
    logger.debug("Inside get_pvs_and_rts_slot_details_data.")
    try:
        query = PVSSlotDetails.select(PVSSlotDetails.id.alias("pvs_slot_details_id"),
                                      PVSSlotDetails.crop_image_name,
                                      PVSSlotDetails.predicted_label_drug_id,
                                      PVSSlotDetails.pvs_classification_status,
                                      RemoteTechSlotDetails.id.alias("remote_tech_slot_details_id"),
                                      RemoteTechSlotDetails.label_drug_id,
                                      RemoteTechSlotDetails.mapped_status) \
            .dicts() \
            .join(PVSSlot, on=PVSSlotDetails.pvs_slot_id == PVSSlot.id) \
            .join(RemoteTechSlot, on=RemoteTechSlot.pvs_slot_id == PVSSlot.id) \
            .join(RemoteTechSlotDetails, JOIN_LEFT_OUTER,
                  on=((RemoteTechSlotDetails.remote_tech_slot_id == RemoteTechSlot.id) &
                      (PVSSlotDetails.id == RemoteTechSlotDetails.pvs_slot_details_id))) \
            .where(PVSSlotDetails.pvs_slot_id == pvs_slot_id, RemoteTechSlot.id == remote_tech_slot_id) \
            .group_by(PVSSlotDetails.id)
        logger.debug(query)
        return query

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        raise


@log_args_and_response
def get_drug_data(pvs_slot_id: int) -> dict:
    """
    Fetches unique_drugs for the slot and the corresponding images and ndc based on the pvs_slot_id.
    @param pvs_slot_id:int
    @return:dict
    """
    logger.debug("Inside get_drug_data.")
    try:
        query = PVSSlot.select(DrugMaster.concated_drug_name_field().alias("drug_name"),
                               DrugMaster.ndc,
                               DrugMaster.formatted_ndc,
                               DrugMaster.txr,
                               DrugMaster.image_name,
                               DrugMaster.imprint,
                               DrugMaster.shape,
                               DrugMaster.color,
                               SlotDetails.quantity,
                               UniqueDrug.id.alias("unique_drug_id")) \
            .dicts() \
            .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug,
                  on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
            .where(PVSSlot.id == pvs_slot_id)
        logger.info(query)
        return query

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        raise


# def update_rts_slot(update_dict, **kwargs):
#     """
#     Updates the RemoteTechSlot table.
#     @param update_dict:
#     @param kwargs:
#     @return:
#     """
#     logger.debug("Inside update_rts_slot.")
#     try:
#         update_status = RemoteTechSlot.db_update(update_dict=update_dict, **kwargs)
#         return str(update_status)
#     except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
#         logger.error(e)
#         raise


# def update_rts_slot_details(update_dict, **kwargs):
#     """
#     Updates the RemoteTechSlotDetails table.
#     @param update_dict:
#     @param kwargs:
#     @return:
#     """
#     logger.debug("Inside update_rts_slot_details.")
#     try:
#         update_status = RemoteTechSlotDetails.db_update(update_dict=update_dict, **kwargs)
#         return str(update_status)
#     except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
#         logger.error(e)
#         raise

@log_args_and_response
def remote_screen_data(filter_fields: dict,
                       paginate: dict,
                       sort_fields: list,
                       advanced_search_fields: dict,
                       user_id: int = None,
                       is_remote_technician=None) -> dict:
    """
    Gets the data for teh Remote Technician Screen.
    @param time_zone: time
    @param sort_fields: list
    @param company_id:int
    @param filter_fields: dict
    @param paginate: dict
    @return: dict
    """
    # todo code changed temporarily for optimizing response time
    logger.debug("Inside remote_screen_data.")
    try:
        response = dict()
        rts_records = list()
        order_list = list()

        if sort_fields:
            order_list.extend(sort_fields)

        rts_records, count, assigned_to_other_user = get_record_from_remote_tech_slot(user_id, paginate, filter_fields, advanced_search_fields,
                                                                                      is_remote_technician)

        response['remote_tech_screen_data'] = rts_records
        response['assigned_to_other_user'] = assigned_to_other_user
        response['total_slots'] = count

        return response

    except (IntegrityError, InternalError) as e:
        logger.info("Error in remote_screen_data {}".format(e))
        raise
    except Exception as e:
        logger.info("Error in remote_screen_data {}".format(e))
        raise


@log_args_and_response
def get_rts_status_for_skipped(pvs_slot_id: int, remote_tech_id: int) -> bool:
    logger.debug("Inside get_rts_status_for_skipped")
    try:
        query = RemoteTechSlot.select(RemoteTechSlot.verification_status).dicts() \
            .where(RemoteTechSlot.pvs_slot_id == pvs_slot_id, RemoteTechSlot.remote_tech_id == remote_tech_id)

        for record in query:
            if record['verification_status'] == constants.RTS_USER_SKIPPED or \
                    record['verification_status'] == constants.RTS_SYSTEM_SKIPPED:
                return True
            else:
                return False

    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.info(e)
        raise


def update_remote_tech_slot(pvs_slot_id: int) -> bool:
    """
    updates the existing entry of pvs_slot in remote tech table
    """
    logger.debug("Inside update_remote_tech_slot")
    try:
        query = RemoteTechSlot.update(is_updated=True).where(RemoteTechSlot.pvs_slot_id == pvs_slot_id).execute()
        logger.info("In update_remote_tech_slot: remote tech slot updated: {}".format(query))
        return True
    except (DoesNotExist, InternalError, IndexError) as e:
        logger.error(e)
        raise


@log_args_and_response
def assign_rts_to_given_user(args):
    try:
        assign_to = args.get('assign_to')
        pack_id = args.get('pack_id', None)
        slot_number = args.get('slot_number', None)
        formatted_ndc = args.get('formatted_ndc', None)
        txr = args.get('txr', None)
        clauses = list()
        rts_id_to_update = set()
        result = list()

        if pack_id:
            clauses.append(SlotHeader.pack_id == pack_id)
        if slot_number:
            clauses.append(PackGrid.slot_number << slot_number)
        if formatted_ndc:
            if '#' in str(formatted_ndc):
                formatted_ndc, txr = str(formatted_ndc).split('#')
        if txr:
            if '#' in str(txr):
                formatted_ndc, txr = str(txr).split('#')
        if formatted_ndc:
            clauses.append(DrugMaster.formatted_ndc == formatted_ndc)
        if txr:
            clauses.append(DrugMaster.txr == txr)
        if (formatted_ndc or txr) and (not pack_id):
            if formatted_ndc and txr:
                result, count, user_ids = get_data_for_remote_tech_screen_for_formatted_ndc_or_txr(formatted_ndc=formatted_ndc, txr=txr)
            elif formatted_ndc:
                result, count, user_ids = get_data_for_remote_tech_screen_for_formatted_ndc_or_txr(
                    formatted_ndc=formatted_ndc)
            else:
                result, count, user_ids = get_data_for_remote_tech_screen_for_formatted_ndc_or_txr(txr=txr)

        else:
            result = RemoteTechSlot.select(RemoteTechSlot.id, RemoteTechSlot.remote_tech_id).dicts() \
                .join(PVSSlot, on=PVSSlot.id == RemoteTechSlot.pvs_slot_id) \
                .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
                .join(PackGrid, on=SlotHeader.pack_grid_id == PackGrid.id) \
                .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .where(
                    RemoteTechSlot.verification_status << ([constants.RTS_USER_SKIPPED, constants.RTS_SYSTEM_SKIPPED]),
                    RemoteTechSlot.is_updated == False, DrugMaster.image_name.is_null(False))
            result = result.where(reduce(operator.and_, clauses))

            result = result.group_by(SlotHeader.pack_id, SlotHeader.id, PVSSlot.id) \
                        .order_by(RemoteTechSlot.id.desc())
            logger.info("In assign_rts_to_given_user, result: {}".format(result))

        for record in result:
            if record['remote_tech_id'] != assign_to:
                rts_id_to_update.add(record['id'])

        logger.info("In assign_rts_to_given_user rts_id_to_update:{}".format(rts_id_to_update))

        if rts_id_to_update:
            RemoteTechSlot.update_remote_tech_id(assign_to, list(rts_id_to_update))

        return True

    except (DoesNotExist, IntegrityError) as e:
        logger.error(f"Error in assign_rts_to_given_user: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in assign_rts_to_given_user: {e}")


@log_args_and_response
def get_data_for_remote_tech_screen_for_formatted_ndc_or_txr(formatted_ndc=None, txr=None, paginate=None):
    try:
        past_one_month_date = (datetime.now() - timedelta(days=30)).date()
        slot_pvs_map = dict()
        clauses = list()
        slot_header_info = dict()
        pvs_slot_dict = dict()
        req_pvs = list()
        rts = dict()
        final_pvs_slot = list()
        result = list()
        user_ids = set()

        pvs_slot_query = PVSSlot.select(SlotHeader.id, fn.GROUP_CONCAT(fn.DISTINCT(PVSSlot.id)).alias("pvs_ids")).dicts() \
            .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
            .where(fn.DATE(PVSSlot.created_date) >= past_one_month_date) \
            .group_by(SlotHeader.id)

        logger.info("In get_data_for_remote_tech_screen_for_formatted_ndc_or_txr, pvs_slot_query: {}".format(pvs_slot_query))

        for data in pvs_slot_query:
            pvs_id_list = list(map(int, data["pvs_ids"].split(",")))
            slot_pvs_map[data["id"]] = pvs_id_list
            for pvs_id in pvs_id_list:
                pvs_slot_dict[pvs_id] = data['id']

        if not slot_pvs_map:
            return [], 0, []

        slot_header_info_query = SlotHeader.select(SlotHeader.id, PackGrid.slot_number, SlotHeader.pack_id, SlotHeader.pack_grid_id).dicts() \
            .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .where(SlotHeader.id.in_(list(slot_pvs_map.keys())), DrugMaster.image_name.is_null(False)) \
            .group_by(SlotHeader.id)
        if formatted_ndc:
            clauses.append(DrugMaster.formatted_ndc==formatted_ndc)
        if txr:
            clauses.append(DrugMaster.txr==txr)
        if clauses:
            slot_header_info_query = slot_header_info_query.where(reduce(operator.and_, clauses))
        logger.info("In get_data_for_remote_tech_screen_for_formatted_ndc_or_txr, slot_header_info_query: {}".format(slot_header_info_query))

        for data in slot_header_info_query:
            pvs_id = slot_pvs_map.get(data["id"], [])
            if pvs_id:
                slot_data = data
                slot_id = slot_data.pop('id')
                slot_header_info[slot_id] = slot_data
                req_pvs.extend(pvs_id)
        req_pvs = list(set(req_pvs))

        if not req_pvs:
            return [], 0, []

        remote_tech_info_query = RemoteTechSlot.select(RemoteTechSlot.id, RemoteTechSlot.remote_tech_id, RemoteTechSlot.verification_status,
                                                       RemoteTechSlot.pvs_slot_id).dicts() \
            .where(RemoteTechSlot.pvs_slot_id.in_(req_pvs),
                   RemoteTechSlot.is_updated == False,
                   RemoteTechSlot.verification_status.in_([108, 109])) \
            .group_by(RemoteTechSlot.id)
        logger.info("In get_data_for_remote_tech_screen_for_formatted_ndc_or_txr, "
                    "remote_tech_info_query: {}".format(remote_tech_info_query))

        for data in remote_tech_info_query:
            rts[data['pvs_slot_id']] = data
            final_pvs_slot.append(data['pvs_slot_id'])

        logger.info("In get_data_for_remote_tech_screen_for_formatted_ndc_or_txr, final_pvs_slot: {}".format(final_pvs_slot))
        final_pvs_slot = list(set(final_pvs_slot))

        for pvs_id in final_pvs_slot:
            if pvs_slot_dict.get(pvs_id, None):
                slot_rts_map = dict()
                slot_info = slot_header_info.get(pvs_slot_dict[pvs_id])
                remote_tech_info = rts[pvs_id]
                for key, value in slot_info.items():
                    slot_rts_map[key] = value
                for key, value in remote_tech_info.items():
                    slot_rts_map[key] = value
                user_ids.add(remote_tech_info['remote_tech_id'])
                result.append(slot_rts_map)

        count = len(result)
        if paginate:
            result = dpws_paginate(result, paginate)

        return result, count, list(user_ids)

    except (DoesNotExist, IntegrityError) as e:
        logger.error(f"Error in get_data_for_remote_tech_screen_for_formatted_ndc_or_txr: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in get_data_for_remote_tech_screen_for_formatted_ndc_or_txr: {e}")


@log_args_and_response
def get_remote_tech_slot_id_dao(remote_tech_slot_details_ids):
    try:
        remote_tech_ids = list()
        query = RemoteTechSlotDetails.select(fn.DISTINCT(RemoteTechSlotDetails.remote_tech_slot_id).alias('remote_tech_slot_id')) \
                                     .where(RemoteTechSlotDetails.id << remote_tech_slot_details_ids)

        for record in query.dicts():
            remote_tech_ids.append(record['remote_tech_slot_id'])

        return remote_tech_ids

    except (DoesNotExist, IntegrityError) as e:
        logger.error(f"Error in get_remote_tech_slot_id_dao: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in get_remote_tech_slot_id_dao: {e}")


@log_args_and_response
def update_status_in_remote_tech_slot_dao(remote_tech_ids):
    try:
        status = RemoteTechSlot.update_status_in_remote_tech_slot(remote_tech_ids=remote_tech_ids)
        return status
    except (DoesNotExist, IntegrityError) as e:
        logger.error(f"Error in update_status_in_remote_tech_slot_dao: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in update_status_in_remote_tech_slot_dao: {e}")


@log_args_and_response
def update_status_in_remote_tech_slot_details_dao(remote_tech_slot_details_ids):
    try:
        status = RemoteTechSlotDetails.update_status_in_remote_tech_slot_details(remote_tech_slot_details_ids=
                                                                                 remote_tech_slot_details_ids)
        return status
    except (DoesNotExist, IntegrityError) as e:
        logger.error(f"Error in update_status_in_remote_tech_slot_dao: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in update_status_in_remote_tech_slot_dao: {e}")


@log_args_and_response
def get_record_from_remote_tech_slot(user_id, paginate, filter_fields, advanced_search_fields, is_remote_technician):
    """

    @return:
    """
    rts_data_list = list()
    rts_record = list()
    sort_fields = None
    exact_search_fields = list()
    like_search_fields = list()
    membership_search_fields = list()
    between_search_fields = list()
    order_list = list()
    count = 0
    clauses = list()
    formatted_ndc = None
    txr = None
    assigned_to_other_user = False
    non_paginate_result_field_list = list()
    distinct_non_paginate_results = True
    user_ids = set()
    result = list()
    assigning_in_progress = False
    user = None
    verification_status = None
    rts_query = None

    try:
        exact_search_fields = ["remote_tech_id", "pack_id"]
        membership_search_fields = ["verification_status", "slot_number"]
        between_search_fields = ["start_time"]
        non_paginate_result_field_list = ["remote_tech_id"]

        fields_dict = {"pack_id": SlotHeader.pack_id,
                       "remote_tech_id": RemoteTechSlot.remote_tech_id,
                       "verification_status": RemoteTechSlot.verification_status,
                       "slot_number": PackGrid.slot_number,
                       "start_time": PVSSlot.created_date
                       }

        if not advanced_search_fields:
            if "verification_status" in filter_fields:
                verification_status = filter_fields.pop("verification_status")
                rts_query = RemoteTechSlot.get_remote_tech_slot(user_id=[user_id],
                                                            status=verification_status)

                for record in rts_query:
                    rts_data_list.append(record['id'])
            if len(rts_data_list):
                clauses = [RemoteTechSlot.id << rts_data_list]
            if len(rts_data_list) < 250 and is_remote_technician:
                thread_name = "assigning_new_rts_slots_to_user"
                for thread in threading.enumerate():
                    if thread.name == thread_name:
                        assigning_in_progress = True

                if not assigning_in_progress:
                    t = ExcThread([], name=thread_name,
                                  target=assigning_new_rts_slots_to_user,
                                  args=[user_id])
                    t.start()
            logger.info("Rts data list get_record_from_remote_tech_slot {}".format(rts_data_list))
            if not len(rts_data_list):
                return [], 0, None

        select_fields = [
            fields_dict["pack_id"],
            SlotHeader.pack_grid_id,
            RemoteTechSlot.pvs_slot_id,
            fields_dict["verification_status"],
            fields_dict["remote_tech_id"],
            RemoteTechSlot.id,
            fields_dict["slot_number"]
        ]

        query = RemoteTechSlot.select(*select_fields) \
            .join(PVSSlot, on=PVSSlot.id == RemoteTechSlot.pvs_slot_id) \
            .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
            .join(PackGrid, on=SlotHeader.pack_grid_id == PackGrid.id)

        if advanced_search_fields:
            query = query.join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
                         .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id)

            clauses.append(RemoteTechSlot.is_updated == False)
            for field in advanced_search_fields:
                if field == "formatted_ndc":
                    if '#' in str(advanced_search_fields[field]):
                        formatted_ndc, txr = str(advanced_search_fields[field]).split('#')
                    else:
                        formatted_ndc = advanced_search_fields[field]
                elif field == "txr":
                    if '#' in str(advanced_search_fields[field]):
                        formatted_ndc, txr = str(advanced_search_fields[field]).split('#')
                    else:
                        txr = advanced_search_fields[field]
                else:
                    filter_fields[field] = advanced_search_fields[field]
            if formatted_ndc:
                clauses.append(DrugMaster.formatted_ndc == formatted_ndc)
            if txr:
                clauses.append(DrugMaster.txr == txr)
            if ('formatted_ndc' in advanced_search_fields or 'txr' in advanced_search_fields) and (
                    'pack_id' not in advanced_search_fields):
                if formatted_ndc and txr:
                    result, count, user_ids = get_data_for_remote_tech_screen_for_formatted_ndc_or_txr(
                        formatted_ndc=formatted_ndc, txr=txr, paginate=paginate)
                elif formatted_ndc:
                    result, count, user_ids = get_data_for_remote_tech_screen_for_formatted_ndc_or_txr(
                        formatted_ndc=formatted_ndc, paginate=paginate)
                else:
                    result, count, user_ids = get_data_for_remote_tech_screen_for_formatted_ndc_or_txr(txr=txr,
                                                                                                       paginate=paginate)
                if (len(user_ids) > 1) or (len(user_ids) == 1 and user_ids[0] != user_id):
                    return result, count, True
                else:
                    return result, count, False

        clauses.append(PVSSlot.pvs_identified_count != 0)

        query = query.group_by(SlotHeader.pack_id, SlotHeader.id, PVSSlot.id) \
            .order_by(RemoteTechSlot.id.desc())
        logger.info("In get_record_from_remote_tech_slot, query: {}".format(query))

        results, count, non_paginate_result = get_results(query.dicts(), fields_dict,
                                                          filter_fields=filter_fields,
                                                          sort_fields=sort_fields,
                                                          paginate=paginate,
                                                          clauses=clauses,
                                                          exact_search_list=exact_search_fields,
                                                          like_search_list=like_search_fields,
                                                          membership_search_list=membership_search_fields,
                                                          between_search_list=between_search_fields,
                                                          identified_order=order_list,
                                                          non_paginate_result_field_list=non_paginate_result_field_list,
                                                          distinct_non_paginate_results=distinct_non_paginate_results)

        for record in results:
            rts_record.append(record)

        if 'remote_tech_id' in non_paginate_result:
            non_paginate_result['remote_tech_id'] = list(non_paginate_result['remote_tech_id'])
            if (len(non_paginate_result['remote_tech_id']) > 1) or \
                    (len(non_paginate_result['remote_tech_id']) == 1 and non_paginate_result['remote_tech_id'][0] != user_id):
                assigned_to_other_user = True
            else:
                assigned_to_other_user = False
        else:
            assigned_to_other_user = None

        return rts_record, count, assigned_to_other_user

    except (IntegrityError, InternalError) as e:
            logger.info("Error in get_record_from_remote_tech_slot {}".format(e))
            raise
    except Exception as e:
            logger.info("Error in get_record_from_remote_tech_slot {}".format(e))
            raise


@log_args_and_response
def assigning_new_rts_slots_to_user(user_id):
    try:
        pending_drug_dict = dict()
        non_pending_drug_dict = dict()
        past_date = (datetime.now() - timedelta(days=settings.DAYS_FOR_ASSIGNING_NEW_RTS_SLOTS)).date()
        drugs_in_queue = list()
        rts_slot_count = 0
        pending_rts_not_in_queue_count = 0
        rts_id_to_update = list()
        drug_without_images = set()
        status = None
        slot_pvs_map = dict()
        slot_pack_analysis_map = dict()
        prs_status = {
            'pending': list(),
            'non_pending': list()
        }
        pending_drug_pvs_slot = dict()
        non_pending_drug_pvs_slot = dict()
        pvs_rts_map = dict()
        unique_drug_qty_dict = dict()
        pvs_id_list = list()

        # if the same user comes again then change current_queue of that user to 0 in rts_slot_assign_info table
        count = RtsSlotAssignInfo.get_user_wise_drug_assigned_count(user_id)

        if count:
            update_status = RtsSlotAssignInfo.remove_user_from_current_queue(user_id=user_id)
            logger.info("In assigning_new_rts_slots_to_user, update_query: {}".format(update_status))

        # fetch status of all the unique_drugs from PRSDrugDetails table
        prs_query = PRSDrugDetails.select(PRSDrugDetails.unique_drug_id, PRSDrugDetails.status).dicts().group_by(
            PRSDrugDetails.unique_drug_id)

        # separate pending and non-pending drugs.
        for drug in prs_query:
            if drug['status'] == constants.PRS_DRUG_STATUS_PENDING:
                prs_status['pending'].append(drug['unique_drug_id'])
            else:
                prs_status['non_pending'].append(drug['unique_drug_id'])

        # get one month back data from PVSSlot
        pvs_query = PVSSlot.select(PVSSlot.id, PVSSlot.slot_header_id, PVSSlot.quadrant).dicts() \
            .where(fn.DATE(PVSSlot.created_date) >= past_date, PVSSlot.pvs_identified_count != 0) \
            .order_by(PVSSlot.id.desc())

        for pvs_data in pvs_query:
            pvs_id_list.append(pvs_data['id'])

        # fetch remote tech slot id for pvs ids.
        remote_tech_slot_query = RemoteTechSlot.select(RemoteTechSlot.id, RemoteTechSlot.pvs_slot_id).dicts() \
            .where(RemoteTechSlot.is_updated == False, RemoteTechSlot.verification_status << [108, 109],
                   RemoteTechSlot.remote_tech_id.is_null(True), RemoteTechSlot.pvs_slot_id << list(pvs_id_list))

        for record in remote_tech_slot_query:
            pvs_rts_map[record['pvs_slot_id']] = record['id']

        # make a dictionary with pvsslot id for every quadrant for each slot header id
        for pvs_slot in pvs_query:
            # only if remote tech slot exists for that pvs id then only add it to new dict
            if pvs_slot['id'] in pvs_rts_map:
                if pvs_slot['slot_header_id'] not in slot_pvs_map:
                    slot_pvs_map[pvs_slot['slot_header_id']] = dict()
                slot_pvs_map[pvs_slot['slot_header_id']][pvs_slot['quadrant']] = pvs_slot['id']

        slot_quadrant_query = SlotHeader.select(SlotHeader.id, PackAnalysisDetails.quadrant, UniqueDrug.id.alias('drug_id'),
                                                MfdAnalysis.dest_quadrant, SlotDetails.quantity, DrugMaster.image_name,
                                                PackAnalysisDetails.status.alias('pack_analysis_status'),
                                                MfdAnalysisDetails.status_id.alias('mfd_analysis_status')).dicts() \
            .join(SlotDetails, on=SlotHeader.id == SlotDetails.slot_id) \
            .join(PackAnalysisDetails, JOIN_LEFT_OUTER, on=PackAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysisDetails, JOIN_LEFT_OUTER, on=MfdAnalysisDetails.slot_id == SlotDetails.id) \
            .join(MfdAnalysis, JOIN_LEFT_OUTER, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
            .join(UniqueDrug,
                  on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
            .where(SlotHeader.id.in_(list(slot_pvs_map.keys())))

        # calculate quantity for each unique_drug.
        # dictionary with either quadrant from PackAnalysisDetails or MfdAnalysis for each slot header and
        # list of drugs dropped from each quadrant.
        for slot in slot_quadrant_query:
            if slot['drug_id'] not in unique_drug_qty_dict:
                unique_drug_qty_dict[slot['drug_id']] = dict()
                unique_drug_qty_dict[slot['drug_id']]['quantity'] = slot['quantity']
                unique_drug_qty_dict[slot['drug_id']]['image_name'] = slot['image_name']
            else:
                unique_drug_qty_dict[slot['drug_id']]['quantity'] += slot['quantity']
            if slot['id'] not in slot_pack_analysis_map and (slot['pack_analysis_status'] == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED or
                slot['mfd_analysis_status'] == constants.MFD_DRUG_DROPPED_STATUS):
                slot_pack_analysis_map[slot['id']] = dict()
                if slot['quadrant']:
                    slot_pack_analysis_map[slot['id']][slot['quadrant']] = list()
                    if slot['drug_id']:
                        slot_pack_analysis_map[slot['id']][slot['quadrant']].append(slot['drug_id'])
                if slot['dest_quadrant']:
                    slot_pack_analysis_map[slot['id']][slot['dest_quadrant']] = list()
                    if slot['drug_id']:
                        slot_pack_analysis_map[slot['id']][slot['dest_quadrant']].append(slot['drug_id'])

            elif slot['id'] in slot_pack_analysis_map and (slot['pack_analysis_status'] == constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED or
                slot['mfd_analysis_status'] == constants.MFD_DRUG_DROPPED_STATUS):
                if slot['quadrant'] and slot['quadrant'] not in slot_pack_analysis_map[slot['id']]:
                    slot_pack_analysis_map[slot['id']][slot['quadrant']] = list()
                if slot['dest_quadrant'] and slot['dest_quadrant'] not in slot_pack_analysis_map[slot['id']]:
                    slot_pack_analysis_map[slot['id']][slot['dest_quadrant']] = list()
                if slot['drug_id'] and slot['quadrant']:
                    slot_pack_analysis_map[slot['id']][slot['quadrant']].append(slot['drug_id'])
                if slot['drug_id'] and slot['dest_quadrant']:
                    slot_pack_analysis_map[slot['id']][slot['dest_quadrant']].append(slot['drug_id'])

        # check where the quadrant from pvs slot is in quandrant from PackAnalysisDetails or MfdAnalysis details and separate each
        # drug and pvs_slot id in pending and non pending pvs slot ids.

        for slot, quadrant_data in slot_pvs_map.items():
            for quadrant, pvs_slot_id in quadrant_data.items():
                if slot_pack_analysis_map.get(slot):
                    slot_data = slot_pack_analysis_map.get(slot)
                    if slot_data.get(quadrant):
                        drug_list = slot_data.get(quadrant)
                        for drug in drug_list:
                            if drug in prs_status['pending']:
                                if drug not in pending_drug_pvs_slot:
                                    pending_drug_pvs_slot[drug] = list()
                                if pvs_slot_id not in pending_drug_pvs_slot[drug]:
                                    pending_drug_pvs_slot[drug].append(pvs_slot_id)
                            elif drug in prs_status['non_pending']:
                                if drug not in non_pending_drug_pvs_slot:
                                    non_pending_drug_pvs_slot[drug] = list()
                                if pvs_slot_id not in non_pending_drug_pvs_slot[drug]:
                                    non_pending_drug_pvs_slot[drug].append(pvs_slot_id)

        # update pending and non pending drug dict with qty, and remote tech slot ids
        for unique_drug, pvs_slot_ids in pending_drug_pvs_slot.items():
            for pvs_slot in pvs_slot_ids:
                if pvs_slot in pvs_rts_map:
                    if unique_drug not in pending_drug_dict:
                        pending_drug_dict[unique_drug] = {
                            'qty': unique_drug_qty_dict[unique_drug]['quantity'],
                            'rts_ids': list(),
                            'in_table': False,
                            'current_queue': None,
                            'drug_image': unique_drug_qty_dict[unique_drug]['image_name']
                        }
                    pending_drug_dict[unique_drug]['rts_ids'].append(pvs_rts_map[pvs_slot])

        for unique_drug, pvs_slot_ids in non_pending_drug_pvs_slot.items():
            for pvs_slot in pvs_slot_ids:
                if pvs_slot in pvs_rts_map:
                    if unique_drug not in non_pending_drug_dict:
                        non_pending_drug_dict[unique_drug] = {
                            'qty': unique_drug_qty_dict[unique_drug]['quantity'],
                            'rts_ids': list(),
                            'in_table': False,
                            'current_queue': None,
                            'drug_image': unique_drug_qty_dict[unique_drug]['image_name']
                        }
                    non_pending_drug_dict[unique_drug]['rts_ids'].append(pvs_rts_map[pvs_slot])

        rts_slot_assign_query = RtsSlotAssignInfo.select(RtsSlotAssignInfo.unique_drug_id, RtsSlotAssignInfo.current_queue).dicts()
        rts_assigned_dict = dict()
        for unique_drug in rts_slot_assign_query:
            rts_assigned_dict[unique_drug['unique_drug_id']] = unique_drug['current_queue']

        # udpate whether the unique drug is in table RtsSlotAssignInfo and current_queue status
        for unique_drug in pending_drug_dict:
            if unique_drug in rts_assigned_dict:
                pending_drug_dict[unique_drug]['in_table'] = True
                pending_drug_dict[unique_drug]['current_queue'] = rts_assigned_dict[unique_drug]

        for unique_drug in non_pending_drug_dict:
            if unique_drug in rts_assigned_dict:
                non_pending_drug_dict[unique_drug]['in_table'] = True
                non_pending_drug_dict[unique_drug]['current_queue'] = rts_assigned_dict[unique_drug]

        logger.info("In assigning_new_rts_slots_to_user, drug without images are: {}".format(drug_without_images))

        # sort pending_drug_dict and non_pending_drug_dict on quantity.
        pending_drug_dict = dict(sorted(pending_drug_dict.items(), key=lambda x: x[1]["qty"], reverse=True))
        non_pending_drug_dict = dict(sorted(non_pending_drug_dict.items(), key=lambda x: x[1]["qty"], reverse=True))

        # when more crops are required for a drug then its status is 2 in current_queue.
        # Need to assign those drugs when they are in top 10 drugs(usage wise)

        #first assign pending drugs not in queue and not in rtsslotassigninfo, then pending drugs
        # which are in table but not in current_queue then at last non-pending drugs

        for drug in pending_drug_dict:
            if rts_slot_count < 2500:
                # No check on length of rts_ids for current_queue = 2 because need
                # to assign 250 slots for those drugs even if they are older than one month.
                if ((not pending_drug_dict[drug]['in_table'] and len(pending_drug_dict[drug]['rts_ids'])) or
                    (pending_drug_dict[drug]['in_table'] and pending_drug_dict[drug]['current_queue'] == 2)) \
                         and pending_drug_dict[drug]['drug_image']:
                    rts_id_to_update, rts_slot_count = get_rts_ids_for_particular_drug(rts_slot_count,
                                                                                       pending_drug_dict[drug]['rts_ids'],
                                                                                       rts_id_to_update, drug,
                                                                                       pending_drug_dict[drug]['current_queue'])
                    drugs_in_queue.append(drug)
                elif not pending_drug_dict[drug]['drug_image']:
                    drug_without_images.add(drug)

                if pending_drug_dict[drug]['in_table'] and not pending_drug_dict[drug]['current_queue'] and pending_drug_dict[drug]['drug_image']:
                    pending_rts_not_in_queue_count += len(pending_drug_dict[drug]['rts_ids'])

            else:
                break

        logger.info("pending_rts_not_in_queue_count: {}".format(pending_rts_not_in_queue_count))

        if rts_slot_count < 2500:
            if pending_rts_not_in_queue_count:
                # remove drugs from rtsslotassigninfo with current_queue status = 0
                # and do same thing as pending_drug_list
                delete_query = RtsSlotAssignInfo.delete().where(RtsSlotAssignInfo.current_queue==0).execute()
                logger.info("In assigning_new_rts_slots_to_user delete_query {}".format(delete_query))
                if delete_query:
                    logger.info("In assigning_new_rts_slots_to_user, "
                                "Assigning slots from pending drugs already assigned but not in current queue ...")
                    for drug in pending_drug_dict:
                        if rts_slot_count < 2500:
                            if ((pending_drug_dict[drug]['in_table'] and not pending_drug_dict[drug]['current_queue']
                                and len(pending_drug_dict[drug]['rts_ids']))
                                or (pending_drug_dict[drug]['in_table'] and pending_drug_dict[drug]['current_queue'] == 2)) \
                                    and pending_drug_dict[drug]['drug_image']:
                                rts_id_to_update, rts_slot_count = get_rts_ids_for_particular_drug(rts_slot_count,
                                                                                                   pending_drug_dict[
                                                                                                       drug]['rts_ids'],
                                                                                                   rts_id_to_update,
                                                                                                   drug, pending_drug_dict[drug]['current_queue'])
                                drugs_in_queue.append(drug)
                            elif not pending_drug_dict[drug]['drug_image']:
                                drug_without_images.add(drug)
                        else:
                            break

            if rts_slot_count < 2500:
                logger.info("In assigning_new_rts_slots_to_user, {} Slots left for assigning, so assigning non pending drugs"
                            .format(2500 - rts_slot_count))
                for drug in non_pending_drug_dict:
                    if rts_slot_count < 2500:
                        delete_query = RtsSlotAssignInfo.delete().where(RtsSlotAssignInfo.current_queue == 0).execute()
                        logger.info(
                            "In assigning_new_rts_slots_to_user delete_query while assigning non_pending_drugs{}".format(
                                delete_query))
                        if delete_query:
                            if ((not non_pending_drug_dict[drug]['in_table'] and len(non_pending_drug_dict[drug]['rts_ids'])) or
                                    (non_pending_drug_dict[drug]['in_table'] and non_pending_drug_dict[drug]['current_queue'] == 2)) \
                                    and non_pending_drug_dict[drug]['drug_image']:
                                rts_id_to_update, rts_slot_count = get_rts_ids_for_particular_drug(rts_slot_count,
                                                                                                   non_pending_drug_dict[drug]['rts_ids'],
                                                                                                   rts_id_to_update, drug,
                                                                                                   non_pending_drug_dict[drug]['current_queue'])
                                drugs_in_queue.append(drug)
                            elif not non_pending_drug_dict[drug]['drug_image']:
                                drug_without_images.add(drug)
                    else:
                        break
        logger.info("In assigning_new_rts_slots_to_user, drug without images: {}".format(drug_without_images))
        logger.info("In assigning_new_rts_slots_to_user, drugs_in_queue: {}".format(drugs_in_queue))

        with db.transaction():
            if drugs_in_queue:
                insert_status = RtsSlotAssignInfo.insert_into_rts_slot_assign_info(drugs_in_queue=drugs_in_queue,
                                                                                   user_id=user_id)
                logger.info("In assigning_new_rts_slots_to_user insert_status: {}".format(insert_status))

            logger.info("In assigning_new_rts_slots_to_user length of rts_id_to_update: {}".format(len(rts_id_to_update)))

            if len(rts_id_to_update):
                status = RemoteTechSlot.update_remote_tech_id(user_id, rts_id_to_update)

            logger.info("In assigning_new_rts_slots_to_user, Status: {}".format(status))
            return status

    except (IntegrityError, InternalError) as e:
        logger.info("Error in assigning_new_rts_slots_to_user {}".format(e))
        raise
    except Exception as e:
        logger.info("Error in assigning_new_rts_slots_to_user {}".format(e))
        raise


@log_args_and_response
def rts_user_progress_data(user_id: int,
                           start_date=None,
                           end_date=None):
    try:
        clauses = [RemoteTechSlot.remote_tech_id == user_id,
                   RemoteTechSlot.is_updated == False,
                   RemoteTechSlot.verification_status in (constants.RTS_SKIPPED_MAPPED,
                                                          constants.RTS_VERIFIED,
                                                          constants.RTS_NOT_SURE)]
        date_format = '%Y-%m-%d'
        if start_date is not None:
            start_date = datetime.strptime(start_date, date_format)
            clauses.append(fn.DATE(RemoteTechSlot.end_time) >= start_date)
        if end_date is not None:
            end_date = datetime.strptime(end_date, date_format)
            clauses.append(fn.DATE(RemoteTechSlot.end_time) <= end_date)

        fields_dict = {
            "date": fn.DATE(RemoteTechSlot.end_time),
            "slots": fn.COUNT(fn.DISTINCT(SlotHeader.id)),
            "subdrops": fn.COUNT(fn.DISTINCT(PVSSlot.id)),
            "crops": fn.COUNT(fn.DISTINCT(RemoteTechSlotDetails.id))
        }

        query = RemoteTechSlot.select(*[value.alias(key) for key, value in fields_dict.items()]).dicts() \
            .join(RemoteTechSlotDetails, on=RemoteTechSlot.id == RemoteTechSlotDetails.remote_tech_slot_id) \
            .join(PVSSlot, on=PVSSlot.id == RemoteTechSlot.pvs_slot_id) \
            .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
            .where(reduce(operator.and_, clauses)) \
            .group_by(fn.DATE(RemoteTechSlot.end_time)) \
            .order_by(fn.DATE(RemoteTechSlot.end_time).desc())
        logger.info('rts user progress query: ' + str(query))

        # results = list()
        # for record in query:
        #     pass
        results, count = get_results(query, fields_dict)
        return {str(user_id): results}

    except (DoesNotExist, IntegrityError) as e:
        logger.error(e)
        raise


@log_args_and_response
def assign_remote_tech_slots(args: dict):
    try:
        logger.info("In assign_remote_tech_slots")

        company_id = args["company_id"]
        system_id = args["system_id"]
        user_id = args["user_id"]
        device_id_list = args.get("device_id")
        quadrant_list = args.get("quadrant")
        swap_user_from = args.get("swap_user_from")
        assigned_to_list = args.get("assigned_to")
        date_from = args.get("date_from")
        date_to = args.get("date_to")
        limit = args.get("limit")
        fndc = args.get("fndc")
        txr = args.get("txr")
        associate_device_id_list = args.get("associate_device_id")

        clauses = []
        status = None

        if not assigned_to_list:
            logger.info("In assign_remote_tech_slots, get all remote technician id")
            status, data = call_webservice(settings.BASE_URL_AUTH,
                                           settings.GET_USERS_ROLE_WISE,
                                           parameters={"role": "Remote Technician", "system_id": system_id}
                                           )
            # assigned_to_list = [203, 204, 210, 211, 225, 231, 232, 233, 234, 235, 236, 237] # need to add all by default users
            assigned_to_list = [x["user_id"] for x in data if x["is active"] == 1]
            logger.info(f"In assign_remote_tech_slots, assign_to_list: {assigned_to_list}")

        logger.info(f"In assign_remote_tech_slots, user_id {user_id} is assigning slots to {assigned_to_list}")

        remote_tech_slot_ids_list: list = list()
        clauses.append(RemoteTechSlot.is_updated == False)
        clauses.append(RemoteTechSlot)

        unassigned_slot_query = RemoteTechSlot.select(RemoteTechSlot.id,
                                                      RemoteTechSlot,
                                                      RemoteTechSlot.remote_tech_id,
                                                      PVSSlot.device_id,
                                                      PVSSlot.quadrant,
                                                      PVSSlot.created_date,
                                                      DrugMaster.formatted_ndc,
                                                      DrugMaster.txr).dicts() \
                                .join(PVSSlot, on=PVSSlot.id == RemoteTechSlot.pvs_slot_id) \
                                .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
                                .join(SlotDetails, on=SlotDetails.slot_id == SlotHeader.id) \
                                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                                .where(RemoteTechSlot.is_updated==False,
                                       RemoteTechSlot.verification_status << [constants.RTS_USER_SKIPPED, constants.RTS_SYSTEM_SKIPPED],
                                       RemoteTechSlot.remote_tech_id.is_null(True))

        if device_id_list:
            unassigned_slot_query = unassigned_slot_query.where(PVSSlot.device_id << device_id_list)
        if associate_device_id_list:
            unassigned_slot_query = unassigned_slot_query.where(PVSSlot.associated_device_id << associate_device_id_list)
        if quadrant_list:
            unassigned_slot_query = unassigned_slot_query.where(PVSSlot.quadrant << quadrant_list)
        if date_from and date_to:
            unassigned_slot_query = unassigned_slot_query.where(fn.DATE(PVSSlot.created_date).between(date_from, date_to))
        if swap_user_from:
            unassigned_slot_query = unassigned_slot_query.where(RemoteTechSlot.remote_tech_id == swap_user_from)
        if fndc and txr:
            unassigned_slot_query = unassigned_slot_query.where(DrugMaster.formatted_ndc == fndc,
                                        DrugMaster.txr == txr)

        unassigned_slot_query = unassigned_slot_query.order_by(SlotHeader.pack_id.desc()).group_by(RemoteTechSlot.id)
        # unassigned_slot_query = unassigned_slot_query.group_by(RemoteTechSlot.id)
        if limit:
            unassigned_slot_query = unassigned_slot_query.limit(limit)

        for data in unassigned_slot_query:
            remote_tech_slot_ids_list.append(data["id"])

        total_remote_tech_slot_ids = len(remote_tech_slot_ids_list)
        if remote_tech_slot_ids_list:

            with db.transaction():

                for user_id in assigned_to_list:

                    per_user_slot = int(len(remote_tech_slot_ids_list)/len(assigned_to_list[assigned_to_list.index(user_id):]))

                    remote_tech_ids = remote_tech_slot_ids_list[:per_user_slot]

                    del remote_tech_slot_ids_list[:per_user_slot]

                    status = RemoteTechSlot.update(remote_tech_id=user_id).where(
                                RemoteTechSlot.id << remote_tech_ids).execute()

                    logger.info(f"In assign_remote_tech_slots, assigned remote_tech_slots to user {user_id}: {status}")
        if status:
            return True
        return False

    except (DoesNotExist, IntegrityError) as e:
        logger.error(f"Error in assign_remote_tech_slots: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in assign_remote_tech_slots: {e}")


@log_args_and_response
def get_rts_ids_for_particular_drug(rts_slot_count, rts_ids, rts_id_to_update, unique_drug_id, current_queue):
    try:
        required = 2500 - rts_slot_count
        remote_tech_slots = list()
        if required > 0:
            count = 0
            for i in rts_ids:
                if count < 250 and rts_slot_count < 2500:
                    if (i not in rts_id_to_update) and (i not in remote_tech_slots):
                        remote_tech_slots.append(i)
                        rts_slot_count += 1
                        count += 1
                else:
                    break
        # if more crops are required for a drug, then fetch 250 crops.
        if (len(remote_tech_slots) < 250) and (rts_slot_count < 2500) and (current_queue == 2):
            logger.info("In get_rts_ids_for_particular_drug, assigning more crops for drug: {}".format(unique_drug_id))
            query = UniqueDrug.select(RemoteTechSlot.id).dicts() \
                                       .join(DrugMaster, on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                                                             (UniqueDrug.txr == DrugMaster.txr))) \
                                       .join(SlotDetails, on=DrugMaster.id == SlotDetails.drug_id) \
                                       .join(SlotHeader, on=SlotHeader.id == SlotDetails.slot_id) \
                                       .join(PVSSlot, on=PVSSlot.slot_header_id == SlotHeader.id) \
                                       .join(RemoteTechSlot, on=RemoteTechSlot.pvs_slot_id == PVSSlot.id) \
                                       .where(RemoteTechSlot.is_updated == False, RemoteTechSlot.verification_status << [108,109],
                                              PVSSlot.pvs_identified_count != 0,
                                              UniqueDrug.id == unique_drug_id) \
                                       .group_by(RemoteTechSlot.id) \
                                       .order_by(RemoteTechSlot.id.desc()) \
                                       .limit(250)
            if remote_tech_slots:
                query = query.where(RemoteTechSlot.id.not_in(remote_tech_slots))
            for record in query:
                if len(remote_tech_slots) < 250 and rts_slot_count < 2500:
                    remote_tech_slots.append(record['id'])
                    rts_slot_count += 1
                else:
                    break
        rts_id_to_update.extend(remote_tech_slots)
        return rts_id_to_update, rts_slot_count
    except (DoesNotExist, IntegrityError) as e:
        logger.error(f"Error in get_rts_ids_for_particular_drug: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in get_rts_ids_for_particular_drug: {e}")


@log_args_and_response
def assign_rts_slots_of_inactive_users(token):
    try:
        logger.info("Inside assign_rts_slots_inactive_users..")
        inactive_users_list = list()
        rts_slots_to_assign = list()
        assigned_to_list = list()
        verification_status = [constants.RTS_USER_SKIPPED, constants.RTS_SYSTEM_SKIPPED]
        last_five_days = (datetime.now() - timedelta(days=5))
        authorization = None
        status = None
        if not token:
            authorization = cherrypy.request.headers.get("Authorization")
        if not authorization:
            authorization = 'Bearer Gz6CluN6TJdHVm4MXWDLM9Sgukz0xv'

        headers = set_authorization_headers(token) if token else set_authorization_headers(authorization)

        status, data = call_webservice(settings.BASE_URL_AUTH,
                                       settings.GET_USERS_ROLE_WISE,
                                       headers=headers,
                                       parameters={"role": "Remote Technician"}
                                       )
        for user in data['data']['technician']:
            if user["last_login"]:
                last_login = datetime.strptime(user['last_login'], '%Y-%m-%d %H:%M:%S %Z%z')
                last_login = last_login.replace(tzinfo=None)
            else:
                continue
            if user["is_active"]:
                # if user is inactive for last five days append it to inactive users list
                inactive_users_list.append(user['user_id']) if last_login < last_five_days else assigned_to_list.append(user["user_id"])

        logger.info("inactive_users_list".format(inactive_users_list))
        # get all the remote tech slots assigned to inactive users
        if not inactive_users_list:
            logger.info("In assign_rts_slots_of_inactive_users, there are no inactive users..")
            return True

        rts_query = RemoteTechSlot.get_remote_tech_slot(user_id=inactive_users_list,
                                                        status=verification_status)

        for record in rts_query:
            rts_slots_to_assign.append(record['id'])

        logger.info("rts_slots_to_assign {}".format(len(rts_slots_to_assign)))
        logger.info(f"In assign_remote_tech_slots, assign_to_list: {assigned_to_list}")

        if rts_slots_to_assign:

            with db.transaction():
                for user_id in assigned_to_list:

                    per_user_slot = int(len(rts_slots_to_assign)/len(assigned_to_list[assigned_to_list.index(user_id):]))

                    remote_tech_ids = rts_slots_to_assign[:per_user_slot]

                    del rts_slots_to_assign[:per_user_slot]

                    status = RemoteTechSlot.update(remote_tech_id=user_id).where(
                                RemoteTechSlot.id << remote_tech_ids).execute()

                    logger.info(f"In assign_remote_tech_slots, assigned remote_tech_slots to user {user_id}: {status}")

        if status:
            return True
        return False

    except (IntegrityError, InternalError) as e:
        logger.info("Error in assign_rts_slots_inactive_users {}".format(e))
        raise
    except Exception as e:
        logger.info("Error in assign_rts_slots_inactive_users {}".format(e))
        raise


@log_args_and_response
def change_drug_queue_status_in_rts_slot_assign_info(unique_drug_id):
    try:
        status = RtsSlotAssignInfo.db_change_drug_queue_status_in_rts_slot_assign_info(unique_drug_id)
        return status
    except (IntegrityError, InternalError) as e:
        logger.info("Error in remove_record_from_rts_slot_assign_info {}".format(e))
        raise
    except Exception as e:
        logger.info("Error in remove_record_from_rts_slot_assign_info {}".format(e))
        raise