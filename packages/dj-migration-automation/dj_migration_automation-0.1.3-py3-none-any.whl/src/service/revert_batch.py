import itertools
import os
import sys

from peewee import InternalError, IntegrityError, DoesNotExist, DataError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args, log_args_and_response
from dosepack.validation.validate import validate
from src import constants
from src.constants import MFD_CANISTER_MVS_FILLING_REQUIRED, MFD_CANISTER_RTS_REQUIRED_STATUS
from src.dao.batch_dao import save_batch_change_tracker_data
from src.dao.canister_dao import update_replenish_based_on_system, delete_reserved_canister_for_pack_queue
from src.dao.canister_transfers_dao import check_pending_canister_transfers
from src.dao.couch_db_dao import reset_couch_db_document
from src.dao.device_manager_dao import get_mfs_system_device_from_company_id
from src.dao.guided_replenish_dao import get_system_device_for_batch, check_pending_guided_canister_transfer
from src.dao.mfd_dao import update_mfs_data_in_couch_db
from src.dao.pack_dao import get_manual_packs_patient_data, create_pack_status_tracker_dao, \
    get_patient_pack_data_by_batch_id, get_mfd_analysis_status
from src.dao.pack_queue_dao import get_packs_from_pack_queue
from src.dao.revert_batch_dao import get_pack_ids_from_batch_id, get_pack_analysis_details_ids_by_batch, \
    delete_data_from_pack_analysis_tables, delete_reserved_canister_for_batch, get_mfd_analysis_ids_by_batch, \
    delete_mfd_analysis_data, delete_canister_transfers_for_batch, update_pack_details_data_for_batch, \
    update_batch_master_revert_batch, get_mfd_filled_pack_ids_by_batch, \
    delete_pack_user_map_by_pack_id, get_analysis_data_dao, delete_frequent_mfd_drugs_for_revert_batch, \
    delete_drug_tracker_data_for_batch, delete_replenish_skipped_canister_data_for_batch
from src.service.misc import update_timestamp_couch_db_pre_processing_wizard, update_mfd_module_couch_db

logger = settings.logger


@log_args
@validate(required_fields=["company_id", "system_id", "call_from_screen", "revert_to_screen", "user_id", "revert_pack_flag"])
def revert_batch_v3(data_dict: dict) -> str:
    """
    This function deletes data from required tables to revert batch.
    Batch can be reverted to PPP schedule batch screen or Batch Distribution select facilities screen.
    @param data_dict:
    @return:
    """

    batch_id = data_dict.get('batch_id', None)
    company_id = data_dict.get('company_id')
    system_id = data_dict.get('system_id')
    current_module_id = data_dict.get('current_module_id', None)  # Module of PPP
    input_pack_ids = data_dict.get('pack_ids', [])  # selected packs to revert from ack queue and manual fill flow
    call_from_screen = data_dict.get('call_from_screen')
    revert_to_screen = data_dict.get('revert_to_screen')  # either BD/select facilities of PPP/Schedule batch
    user_id = data_dict.get('user_id')
    revert_pack_flag = data_dict.get('revert_pack_flag')
    pack_status_tracker_list: list = list()
    other_packs_of_filled_patient: list = list()
    # 0: by default
    # 1: some packs are filled mfd and some are not filled mfd packs then revert unfilled packs of other patient(whose mfd is not filled and packs are in pending states) pack to BD/select facilities
    #    Or same patient’s pending packs are available then revert packs to BD/select facilities

    try:
        # module of pack_pre_processing screen
        module_id_0 = constants.PRE_PROCESSING_MODULE_MAPPING[constants.PPP_SEQUENCE_IN_PENDING]
        module_id_1 = constants.PRE_PROCESSING_MODULE_MAPPING[constants.PPP_SEQUENCE_PACK_DISTRIBUTION_BY_BATCH_DONE]
        module_id_2 = constants.PRE_PROCESSING_MODULE_MAPPING[constants.PPP_SEQUENCE_MFD_RECOMMENDATION_DONE]
        module_id_3 = constants.PRE_PROCESSING_MODULE_MAPPING[constants.PPP_SEQUENCE_UPDATE_MFD_ANALYSIS_DONE]
        module_id_4 = constants.PRE_PROCESSING_MODULE_MAPPING[constants.PPP_SEQUENCE_CANISTER_RECOMMENDATION_DONE]

        with db.transaction():
            db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
            db.execute_sql("SET SQL_SAFE_UPDATES=0")

            # get system wise device list for given batch that includes ROBOT and CSR
            system_device_dict = get_system_device_for_batch()

            # get mfs stations to update couch db
            mfs_system_device = dict()
            if batch_id:
                mfs_system_device = get_mfs_system_device_from_company_id(company_id=company_id,
                                                                          batch_id=batch_id)
                logger.info("In revert_batch_v3: mfs_system_device {}".format(mfs_system_device))

            if call_from_screen == constants.CALL_FROM_PACK_PRE_PROCESSING:
                # get pack list from batch id
                batch_pack_ids, pending_pack_id_list = get_pack_ids_from_batch_id(batch_id=batch_id)
                logger.info("In revert_batch_v3: call from : {}, total number of packs in batch: {}, pending packs: {}"
                            .format(call_from_screen, len(batch_pack_ids), len(pending_pack_id_list)))

                # if all packs in batch are pending (all packs in batch and pending packs in batch are same)
                if batch_pack_ids == pending_pack_id_list:
                    revert_pack_id_list = batch_pack_ids
                else:
                    # if all packs in batch are not pending(some are deleted or some are move to manual fill flow from PPP)
                    # so only pending packs of batch are allow to_revert
                    revert_pack_id_list = pending_pack_id_list

                # get analysis ids from pack_analysis table
                analysis_ids = get_pack_analysis_details_ids_by_batch(batch_id=batch_id,
                                                                      pack_list=revert_pack_id_list)
                # get mfd analysis ids from mfd_analysis table
                mfd_analysis_ids = get_mfd_analysis_ids_by_batch(batch_id=batch_id,
                                                                 pack_list=revert_pack_id_list)

                #  if call from PACK_PRE_PROCESSING then allow to revert batch to batch distribution screen or 1st module of pack pre-processing screen
                # but if some packs have filled mfd then not allow user to revert mfd filled packs(other packs of same patient). only revert unfilled mfd packs to BD/select facilities module

                # check if module == 0 -> only revert batch to batch distribution screen
                # check if module == 1 -> (1)revert batch to batch distribution(select facilities) screen or
                #                         (2)pack_pre_processing(schedule batch)
                if current_module_id == module_id_0:

                    # revert batch to batch distribution(select facilities) screen
                    if revert_to_screen == constants.REVERT_TO_BATCH_DISTRIBUTION:
                        update_dict = {"system_id": None,
                                       "facility_dis_id": None,
                                       "batch_id": None,
                                       "filled_at": None,
                                       "car_id": None}
                        # if all packs in btch are reverted then delete batch
                        if revert_pack_id_list == batch_pack_ids:
                            batch_update_dict = {"status": settings.BATCH_DELETED}

                        elif revert_pack_id_list == pending_pack_id_list:
                            batch_update_dict = {"status": settings.BATCH_PROCESSING_COMPLETE}

                        # update pack details and batch master table
                        pack_status, batch_status = update_pack_details_and_batch_master_to_revert_batch_to_batch_dis(
                            batch_id=batch_id,
                            pack_list=revert_pack_id_list,
                            update_dict=update_dict,
                            batch_update_dict=batch_update_dict)
                        logger.info(
                            "In revert_batch_v3: call_from: {}, revert_to: {},current_module_id: {}, pack details updated: {} "
                            "for batch_id: {} and batch details updated: {}"
                            .format(call_from_screen, revert_to_screen, current_module_id, pack_status, batch_id,
                                    batch_status))

                    # revert batch to pack_pre_processing(schedule batch) screen
                    elif revert_to_screen == constants.REVERT_TO_PACK_PRE_PROCESSING:

                        batch_update_dict = {"status": settings.BATCH_PENDING,
                                             "sequence_no": constants.PPP_SEQUENCE_IN_PENDING}
                        # update sequence_no to PPP_SEQUENCE_IN_PENDING and batch status to pending
                        batch_status_update = update_batch_master_revert_batch(batch_id=batch_id,
                                                                               batch_update_dict=batch_update_dict)
                        logger.debug("In revert_batch_v3: call_from: {}, module: {}, revert_to_screen: {},"
                                     "sequence updated: {} , changed sequence to {}, batch status to: {} for batch_Id: {}"
                                     .format(call_from_screen, current_module_id, revert_to_screen, batch_status_update,
                                             constants.PPP_SEQUENCE_IN_PENDING, settings.BATCH_PENDING, batch_id))

                    # todo commented for now as we don't allow user to revert batch when MFD filling is started
                    # reset MFS couch db documents when revert batch completely
                    # if len(mfs_system_device):
                    #     mfs_doc_status = reset_mfs_couch_db_documents_batch_revert(mfs_system_device)
                    #     logger.info(
                    #         "In revert_batch_v3: call_from: {}, revert to screen: {}, current_module_id: {}, mfs_doc_status: {}"
                    #         .format(call_from_screen, revert_to_screen, current_module_id, mfs_doc_status))
                    #
                    # # update company level , system level couch db
                    reset_company_level_cd_doc, reset_system_level_cd_doc = revert_batch_couch_db_update(
                        company_id=company_id,
                        system_device_dict=system_device_dict,
                        call_from_screen=call_from_screen)
                    logger.info("In revert_batch_v3: call_from: {}, revert to screen: {}, current_module_id: {}, "
                                "company_level couch db update: {}, system level couch db update: {}"
                                .format(call_from_screen, revert_to_screen, current_module_id,
                                        reset_company_level_cd_doc,
                                        reset_system_level_cd_doc))

                    # update couch db timestamp for pack_pre_processing_wizard change
                    couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args={"system_id": system_id})
                    logger.info("In revert_batch_v3: call_from: {}, module: {}, revert_to_screen: {}, "
                                "time stamp update for pre processing wizard: {} for batch_id: {}"
                                .format(call_from_screen, current_module_id, revert_to_screen, couch_db_status,
                                        batch_id))

                    batch_change_tracker_status = save_batch_change_tracker_data(batch_id=batch_id,
                                                        user_id=user_id,
                                                        action_id=constants.ACTION_ID_MAP[
                                                            constants.REVERT_BATCH_OR_PACKS],
                                                        params={"revert_from": call_from_screen,
                                                                "revert_to": revert_to_screen,
                                                                "module_id": current_module_id,
                                                                "batch_id": batch_id,
                                                                "user_id": user_id,
                                                                "pack_count": len(set(revert_pack_id_list))},
                                                        packs_affected=list(set(revert_pack_id_list)))
                    logger.info("In revert_batch_v3: data saved in batch change tracker: {}, "
                                "revert_to_screen: {} for call from: {}, current module id: {}"
                                .format(batch_change_tracker_status, revert_to_screen, call_from_screen, current_module_id))

                    return create_response(settings.SUCCESS_RESPONSE)

                # check if module == 2, 3, 4 -> (1)revert batch to batch distribution(select facilities) screen or
                #                               (2)pack_pre_processing(schedule batch)
                # if mfd is filled for some packs then not allow user to revert mfd filled pack and only allow to revert other packs to BD/select facilities screen
                elif current_module_id == module_id_1 or current_module_id == module_id_2 or current_module_id == module_id_3 or current_module_id == module_id_4:

                    # check if any canister transfer is pending for any batch
                    pending_can_transfers = check_pending_canister_transfers(system_id=system_id)
                    if pending_can_transfers:
                        logger.info("In revert_batch_v3: Incomplete canister transfer flow")
                        pending_batch_id = None
                        for record in pending_can_transfers:
                            if not pending_batch_id:
                                pending_batch_id = record["batch_id"]
                        return error(14004, "{},{}".format(pending_batch_id, system_id),
                                     additional_info={"additional_info":  constants.REVERT_BATCH_INFO_MESSAGE['CANISTER_TRANSFER']})

                    # if user want to revert batch from module_id_2, module_id_3, module_id_4 check if mfd is filled or not for the packs
                    # if mfd is filled for some packs then not allow user to revert mfd filled pack and revert other packs
                    filled_patient_id_list, filled_mfd_pack_ids = get_mfd_filled_pack_ids_by_batch(batch_id=batch_id)
                    logger.info("In revert_batch_v3: call from: {}, revert to : {}, current module: {},"
                                "filled_patient_id_list: {}, filled_mfd_pack_ids: {}"
                                .format(call_from_screen, revert_to_screen, current_module_id, filled_patient_id_list,
                                        filled_mfd_pack_ids))

                    # if all packs of batch or all the pending packs of batch are filled mfd packs then return error
                    if set(revert_pack_id_list) == set(filled_mfd_pack_ids):
                        return error(14012, additional_info={"additional_info":  constants.REVERT_BATCH_INFO_MESSAGE['MFD_FILLING_PENDING']})

                    if filled_patient_id_list:
                        # get patient pack by patient id and batch id
                        other_packs_of_filled_patient_query = get_patient_pack_data_by_batch_id(batch_id=batch_id,
                                                                                                patient_id_list=filled_patient_id_list)

                        for data in other_packs_of_filled_patient_query:
                            other_packs_of_filled_patient.append(data['pack_id'])
                            if data['pack_id'] in revert_pack_id_list:
                                revert_pack_id_list.remove(data['pack_id'])

                    logger.info(
                        "In revert_batch_v3: call from: {}, revert_to_screen: {}, module: {}, revert_pack_id_list: {}"
                        "".format(call_from_screen, revert_to_screen, current_module_id, len(revert_pack_id_list)))

                    if revert_pack_flag == constants.REVERT_PACK_FLAG_0 and not revert_pack_id_list:
                        return error(14013, additional_info={"additional_info":  constants.REVERT_BATCH_INFO_MESSAGE['UNFILLED_MFD_CANISTER']})
                    if filled_mfd_pack_ids and revert_pack_id_list and revert_pack_flag == constants.REVERT_PACK_FLAG_0:
                        return error(14009)

                    if revert_to_screen == constants.REVERT_TO_BATCH_DISTRIBUTION:
                        update_dict = {"system_id": None,
                                       "facility_dis_id": None,
                                       "batch_id": None,
                                       "filled_at": None,
                                       "car_id": None}
                        # only revert mfd filling pending packs to BD/select facilities module
                        if revert_pack_flag == constants.REVERT_PACK_FLAG_1 and revert_pack_id_list:
                            logger.info(
                                "In revert_batch_v3: call from: {}, revert_to_screen: {}, module: {}, revert pack ids: {}"
                                .format(call_from_screen, revert_to_screen, current_module_id, revert_pack_id_list))

                            # get canister used in other_packs_of_filled_patient
                            canister_ids = get_analysis_data_dao(
                                other_packs_of_filled_patient=other_packs_of_filled_patient,
                                batch_id=batch_id)
                            # revert pending packs and delete
                            status = revert_filling_pending_packs(batch_id=batch_id,
                                                                  revert_packs_ids_for_batch=revert_pack_id_list,
                                                                  update_dict=update_dict)
                            logger.info(
                                "In revert_batch_v3: call from: {}, current_module: {},revert_pack_flag:{}, revert_to_screen: {}, "
                                "revert_filling_pending_packs: {}"
                                .format(call_from_screen, current_module_id, revert_pack_flag, revert_to_screen,
                                        status))

                            # delete canister from canister transfers and reserved canister
                            # delete data from reserved_canisters table
                            delete_reserved_canisters = delete_reserved_canister_for_batch(batch_id=batch_id,
                                                                                           canister_ids=canister_ids)
                            logger.info("In revert_batch_v3: delete_reserved_canisters {}".format(
                                delete_reserved_canisters))

                            # delete data from canister_transfers table
                            delete_canister_transfer_data = delete_canister_transfers_for_batch(batch_id=batch_id,
                                                                                                canister_ids=canister_ids,
                                                                                                revert_pack_id_list=revert_pack_id_list)
                            logger.info("In revert_batch_v3: delete_canister_transfer_data {}"
                                        .format(delete_canister_transfer_data))

                            batch_change_tracker_status = save_batch_change_tracker_data(batch_id=batch_id,
                                                                user_id=user_id,
                                                                action_id=constants.ACTION_ID_MAP[
                                                                    constants.REVERT_BATCH_OR_PACKS],
                                                                params={"revert_from": call_from_screen,
                                                                        "revert_to": revert_to_screen,
                                                                        "module_id": current_module_id,
                                                                        "batch_id": batch_id,
                                                                        "user_id": user_id,
                                                                        "pack_count": len(set(revert_pack_id_list))},
                                                                packs_affected=list(set(revert_pack_id_list)))
                            logger.info(
                                "In revert_batch_v3: data saved in batch change tracker: {}, for call from: {}, current module id: {}"
                                .format(batch_change_tracker_status, call_from_screen, current_module_id))
                            return create_response(settings.SUCCESS_RESPONSE)

                        # in normal case if all packs are pending and mfd is not filled for any packs then revert batch to BD/select facilities' module
                        status = revert_all_packs_of_batch_to_batch_distribution(analysis_ids=analysis_ids,
                                                                                 batch_id=batch_id,
                                                                                 company_id=company_id,
                                                                                 mfd_analysis_ids=mfd_analysis_ids,
                                                                                 revert_pack_id_list=revert_pack_id_list,
                                                                                 system_device_dict=system_device_dict,
                                                                                 system_id=system_id,
                                                                                 mfs_system_device=mfs_system_device,
                                                                                 update_dict=update_dict,
                                                                                 call_from_screen=call_from_screen)
                        if set(batch_pack_ids) == set(revert_pack_id_list):
                            batch_update_dict = {"status": settings.BATCH_DELETED}
                        elif set(pending_pack_id_list) == set(revert_pack_id_list):
                            batch_update_dict = {"status": settings.BATCH_PROCESSING_COMPLETE}

                        if batch_update_dict:
                            # set batch status to batch deleted if all packs of batch is reverted to batch distribution screen
                            batch_status_update = update_batch_master_revert_batch(batch_id=batch_id,
                                                                                   batch_update_dict=batch_update_dict)

                            logger.info("In revert_batch_v3: call from: {}, current_module: {},revert_pack_flag:{}, "
                                        "revert_to_screen: {}, revert_all_packs_of_batch_to_batch_distribution: {}, batch_status_update: {}"
                                        .format(call_from_screen, current_module_id, revert_pack_flag, revert_to_screen,
                                                status, batch_status_update))

                    elif revert_to_screen == constants.REVERT_TO_PACK_PRE_PROCESSING and revert_pack_flag == constants.REVERT_PACK_FLAG_0:
                        status = revert_all_packs_of_batch_to_pack_pre_processing(analysis_ids=analysis_ids,
                                                                                  batch_id=batch_id,
                                                                                  company_id=company_id,
                                                                                  mfd_analysis_ids=mfd_analysis_ids,
                                                                                  system_device_dict=system_device_dict,
                                                                                  system_id=system_id,
                                                                                  mfs_system_device=mfs_system_device,
                                                                                  call_from_screen=call_from_screen)
                        logger.info(
                            "In revert_batch_v3: call from: {}, current_module: {},revert_pack_flag: {}, revert_to_screen: {}, "
                            "revert_all_packs_of_batch_to_pack_pre_processing: {}"
                            .format(call_from_screen, current_module_id, revert_pack_flag, revert_to_screen, status))

                    # save drug change tracker data in table
                    batch_change_tracker_status = save_batch_change_tracker_data(batch_id=batch_id,
                                                        user_id=user_id,
                                                        action_id=constants.ACTION_ID_MAP[
                                                            constants.REVERT_BATCH_OR_PACKS],
                                                        params={"revert_from": call_from_screen,
                                                                "revert_to": revert_to_screen,
                                                                "module_id": current_module_id,
                                                                "batch_id": batch_id,
                                                                "user_id": user_id,
                                                                "pack_count": len(set(revert_pack_id_list))},
                                                        packs_affected=list(set(revert_pack_id_list)))

                    logger.info(
                        "In revert_batch_v3: data saved in batch change tracker: {}, for call from: {}, current module id: {}, revert_to_screen: {}"
                        .format(batch_change_tracker_status, call_from_screen, current_module_id, revert_to_screen))
                    return create_response(settings.SUCCESS_RESPONSE)

            # if user want to revert batch from pack queue screen
            elif call_from_screen == constants.CALL_FROM_PACK_QUEUE:
                # check if guided is running or not - if guided is running not allow user to revert-batch
                pending_guided_cycles = check_pending_guided_canister_transfer(system_id=system_id)
                logger.info("In revert_batch_v3: call from : {},Pending guided canister cycles - {}"
                            .format(call_from_screen, pending_guided_cycles))

                if pending_guided_cycles:
                    logger.info("In revert_batch_v3: call from: {}| Incomplete canister transfer flow".format(call_from_screen))
                    pending_batch_id = None
                    for record in pending_guided_cycles:
                        if not pending_batch_id:
                            pending_batch_id = record["batch_id"]
                    return error(14005,
                                 additional_info={"additional_info": constants.REVERT_BATCH_INFO_MESSAGE['GUIDED_TRANSFER']})


                # get pack list from batch id
                # batch_pack_ids, pending_pack_id_list = get_pack_ids_from_batch_id(batch_id=batch_id)
                pending_pack_id_list = []
                batch_pack_ids = []
                pack_queue_packs = get_packs_from_pack_queue(company_id=company_id)
                for data in pack_queue_packs:
                    batch_pack_ids.append(data["id"])
                    if data['pack_status'] == settings.PENDING_PACK_STATUS:
                        pending_pack_id_list.append(data["id"])

                logger.info("In revert_batch_v3: call from : {}, total number of packs in batch: {}, pending packs: {}"
                            .format(call_from_screen, len(batch_pack_ids), len(pending_pack_id_list)))

                # get packs status and packs patient to revert
                query = get_patient_pack_data_by_batch_id(pack_list=input_pack_ids)

                # get dict-remove progress packs and same patient packs from input pack ids
                input_pack_ids_to_revert_dict, pending_same_patient_dict, progress_same_patient_dict, pack_status_set \
                    = get_progress_pending_patient_packs(pack_ids=input_pack_ids, query=query, call_from_screen=call_from_screen)

                pack_status_list = list(pack_status_set)
                # if selected input packs to revert is not in pending(status = 2) state then return error
                if not all(status == settings.PENDING_PACK_STATUS for status in pack_status_list):
                    return error(14010, additional_info={"additional_info": constants.REVERT_BATCH_INFO_MESSAGE['PENDING_PACKS']})

                # if user want to revert batch from pack queue check if mfd is filled or not for the packs to revert
                # if mfd is filled for some packs then not allow user to revert mfd filled pack and revert other pending packs
                filled_patient_id_list, filled_mfd_pack_ids = get_mfd_filled_pack_ids_by_batch()
                logger.info("In revert_batch_v3: call_from: {}, filled_analysis_ids_list: {}, filled_mfd_pack_ids: {}"
                    .format(call_from_screen, filled_patient_id_list, len(filled_mfd_pack_ids)))

                for filled_patient_id in filled_patient_id_list:
                    # filled_patient_id in input_pack_ids_to_revert_dict then remove it from input_pack_ids_to_revert_dict(don't allow user to revert mfd filled patient packs)
                    if filled_patient_id in input_pack_ids_to_revert_dict.keys():
                        input_pack_ids_to_revert_dict.pop(filled_patient_id)
                    #     if some packs are mfd filled and some are in pending then remove filled_patient_id from batch_pending_same_patient_dict
                    if filled_patient_id in pending_same_patient_dict.keys():
                        pending_same_patient_dict.pop(filled_patient_id)

                logger.info("In revert_batch_v3: call_from: {}, input_pack_ids_to_revert_dict: {}, batch_pending_same_patient_dict: {}"
                    .format(call_from_screen, input_pack_ids_to_revert_dict, pending_same_patient_dict))

                # all packs are mfd filled
                if not input_pack_ids_to_revert_dict:
                    return error(14013, additional_info={"additional_info": constants.REVERT_BATCH_INFO_MESSAGE['UNFILLED_MFD_CANISTER']})

                # if manual_progress_same_patient_dict -> then check if
                for patient_id, patient_packs in progress_same_patient_dict.items():
                    # if progress pack's patient id in input_pack_ids_to_revert_dict(it means some patient packs in input pack ids but other packs of same patient is in progress)
                    # then remove patient id from input_pack_ids_to_revert_dict
                    if patient_id in input_pack_ids_to_revert_dict.keys():
                        input_pack_ids_to_revert_dict.pop(patient_id)

                    # if progress pack's patient id in pending_same_patient_dict(it means some patient packs in input pack ids but other packs of same patient is in progress and pending)
                    # then remove patient id from pending_same_patient_dict
                    if patient_id in pending_same_patient_dict.keys():
                        pending_same_patient_dict.pop(patient_id)

                logger.info("In revert_batch_v3: call_from: {}, input_pack_ids_to_revert_dict: {},manual_pending_same_patient_dict: {} "
                    .format(call_from_screen, input_pack_ids_to_revert_dict, pending_same_patient_dict, progress_same_patient_dict))

                if revert_pack_flag == constants.REVERT_PACK_FLAG_0:
                    # if not input_pack_ids_to_revert_dict(means other packs of same patient is in progress)
                    if not input_pack_ids_to_revert_dict:
                        return error(14014, additional_info={"additional_info": constants.REVERT_BATCH_INFO_MESSAGE['OTHER_PATIENT_PACK']})
                    # if input_pack_ids_to_revert_dict and some packs are pending or progress then only allow you to revert pending packs - 'revert_pack_flag'=1 from front end
                    if input_pack_ids_to_revert_dict and pending_same_patient_dict:
                        return error(14011)
                    # some packs are mfd filled but still some other patient packs are pending then allow to revert pending packs of other patients.(whose mfd is not filled)
                    if filled_patient_id_list and input_pack_ids_to_revert_dict:
                        return error(14009)



                # make list for packs to revert (all packs from input_pack_ids_to_revert_dict + other pending packs of same patient)
                # use chain to combine list of list in python ({1667: [78781]}, {1667: [78776, 78777]} )
                # final_pack_ids_to_revert = [78781] + [78776, 78777]
                final_pack_ids_to_revert = list(itertools.chain.from_iterable(list(input_pack_ids_to_revert_dict.values()))) + \
                                           list(itertools.chain.from_iterable(list(pending_same_patient_dict.values())))

                if (revert_pack_flag == constants.REVERT_PACK_FLAG_0 and input_pack_ids_to_revert_dict) or \
                        (revert_pack_flag == constants.REVERT_PACK_FLAG_1 and final_pack_ids_to_revert):

                    update_dict = {"system_id": None,
                                   "facility_dis_id": None,
                                   "batch_id": None,
                                   "filled_at": None,
                                   "car_id": None}
                    # delete batch(when all packs of batch are reverted to BD screen)
                    if set(batch_pack_ids) == set(pending_pack_id_list) == set(final_pack_ids_to_revert):
                        # get analysis ids from pack_analysis table
                        analysis_ids = get_pack_analysis_details_ids_by_batch(pack_list=final_pack_ids_to_revert)
                        # get mfd analysis ids from mfd_analysis table
                        mfd_analysis_ids = get_mfd_analysis_ids_by_batch(pack_list=final_pack_ids_to_revert)

                        # in normal case if all packs are pending and mfd is not filled for any packs then revert batch to BD/select facilities' module
                        status = revert_all_packs_of_batch_to_batch_distribution(analysis_ids=analysis_ids,
                                                                                 company_id=company_id,
                                                                                 mfd_analysis_ids=mfd_analysis_ids,
                                                                                 revert_pack_id_list=final_pack_ids_to_revert,
                                                                                 system_device_dict=system_device_dict,
                                                                                 system_id=system_id,
                                                                                 update_dict=update_dict,
                                                                                 call_from_screen=call_from_screen)

                        batch_update_dict = {"status": settings.BATCH_DELETED}
                        # set batch status to batch deleted if all packs of batch is reverted to batch distribution screen
                        batch_status_update = update_batch_master_revert_batch(batch_update_dict=batch_update_dict)

                        logger.info("In revert_batch_v3: call from: {}, current_module: {},revert_pack_flag:{}, "
                                    "revert_to_screen: {}, revert_all_packs_of_batch_to_batch_distribution: {}, batch_status_update: {}"
                                    .format(call_from_screen, current_module_id, revert_pack_flag, revert_to_screen,
                                            status, batch_status_update))

                    delete_reserved_canister_for_pack_queue(final_pack_ids_to_revert)
                    status = revert_filling_pending_packs(revert_packs_ids_for_batch=final_pack_ids_to_revert,
                                                              update_dict=update_dict)
                    logger.info("In revert_batch_v3: call_from: {}, final_pack_ids_to_revert: {}, revert_mfd_filling_pending_packs - {}"
                                    .format(call_from_screen, final_pack_ids_to_revert, status))
                    update_replenish_based_on_system(system_id=system_id)
                    # save drug change tracker data in table
                    batch_change_tracker_status = save_batch_change_tracker_data(batch_id=None,
                                                        user_id=user_id,
                                                        action_id=constants.ACTION_ID_MAP[
                                                            constants.REVERT_BATCH_OR_PACKS],
                                                        params={"revert_from": call_from_screen,
                                                                "revert_to": revert_to_screen,
                                                                "module_id": current_module_id,
                                                                "batch_id": None,
                                                                "user_id": user_id,
                                                                "pack_count": len(set(final_pack_ids_to_revert))},
                                                        packs_affected=list(set(final_pack_ids_to_revert)))

                    logger.info("In revert_batch_v3: data saved in batch change tracker: {}, for call from: {}, current module id: {}"
                        .format(batch_change_tracker_status, call_from_screen, current_module_id))
                    return create_response(settings.SUCCESS_RESPONSE)

            # when user want to revert packs from manual fill flow
            # (Only pending(pack status = 8) packs are allowed to revert from manual fill flow)
            elif call_from_screen == constants.CALL_FROM_MANUAL_FILL_FLOW:

                mfd_status = get_mfd_analysis_status(pack_list=input_pack_ids)
                keys = list(mfd_status.keys())
                keys = ','.join(str(elem) for elem in keys)
                if mfd_status:
                    return error(21006, additional_info={"additional_info": "Pack_ids : " + keys})

                logger.info("In revert_batch_v3: call_from: {}, pack_ids with manual dropping or rts required: {}"
                            .format(call_from_screen, mfd_status.keys()))

                # get patient ids and pack status of selected pack ids
                query = get_manual_packs_patient_data(pack_list=input_pack_ids)
                # get dict-remove progress packs and same patient packs from input pack ids
                input_pack_ids_to_revert_dict, pending_same_patient_dict, progress_same_patient_dict, pack_status_set\
                    = get_progress_pending_patient_packs(pack_ids=input_pack_ids, query=query, call_from_screen=call_from_screen)

                pack_status_list = list(pack_status_set)
                # if selected input packs to revert is not in pending(status = 8) state then return error
                if not all(status == settings.MANUAL_PACK_STATUS for status in pack_status_list):
                    return error(14010, additional_info={"additional_info": constants.REVERT_BATCH_INFO_MESSAGE['PENDING_PACKS']})

                logger.info("In revert_batch_v3: call_from: {}, input_pack_ids_to_revert_dict: {},manual_pending_same_patient_dict: {} "
                            .format(call_from_screen, input_pack_ids_to_revert_dict, pending_same_patient_dict, progress_same_patient_dict))

                # if manual_progress_same_patient_dict -> then check if
                for patient_id, patient_packs in progress_same_patient_dict.items():
                    # if progress pack's patient id in input_pack_ids_to_revert_dict(it means some patient packs in input pack ids but other packs of same patient is in progress)
                    # then remove patient id from input_pack_ids_to_revert_dict
                    if patient_id in input_pack_ids_to_revert_dict.keys():
                        input_pack_ids_to_revert_dict.pop(patient_id)

                    # if progress pack's patient id in pending_same_patient_dict(it means some patient packs in input pack ids but other packs of same patient is in progress and pending)
                    # then remove patient id from pending_same_patient_dict
                    if patient_id in pending_same_patient_dict.keys():
                        pending_same_patient_dict.pop(patient_id)

                logger.info("In revert_batch_v3: call_from: {}, input_pack_ids_to_revert_dict: {},manual_pending_same_patient_dict: {} "
                    .format(call_from_screen, input_pack_ids_to_revert_dict, pending_same_patient_dict,
                            progress_same_patient_dict))

                # other packs of same patient is in progress
                if progress_same_patient_dict and not input_pack_ids_to_revert_dict:
                    return error(14014, additional_info={"additional_info": constants.REVERT_BATCH_INFO_MESSAGE['OTHER_PATIENT_PACK']})
                if revert_pack_flag == constants.REVERT_PACK_FLAG_0 and input_pack_ids_to_revert_dict and pending_same_patient_dict:
                    # only other packs of same patient is in pending then allowed to revert 'revert_pack_flag' = 1 from front end
                    return error(14011)

                # make list for packs to revert (all packs from input_pack_ids_to_revert_dict + other pending packs of same patient)
                # use chain to combine list of list in python ({1667: [78781]}, {1667: [78776, 78777]} )
                # final_pack_ids_to_revert = [78781] + [78776, 78777]
                final_pack_ids_to_revert = list(itertools.chain.from_iterable(list(input_pack_ids_to_revert_dict.values()))) + \
                                           list(itertools.chain.from_iterable(list(pending_same_patient_dict.values())))

                logger.info("In revert_batch_v3: call from: {}, final_pack_ids_to_revert: {}"
                            .format(call_from_screen, final_pack_ids_to_revert))

                if (revert_pack_flag == constants.REVERT_PACK_FLAG_0 and input_pack_ids_to_revert_dict) or \
                        (revert_pack_flag == constants.REVERT_PACK_FLAG_1 and final_pack_ids_to_revert):
                    # delete entry from pack user map table
                    delete_status = delete_pack_user_map_by_pack_id(pack_ids=final_pack_ids_to_revert)
                    logger.info("In revert_batch_v3: call_from: {}, pack user map data deleted - {},final_pack_ids_to_revert: {}"
                                .format(call_from_screen, delete_status, final_pack_ids_to_revert))

                    update_dict = {"system_id": None,
                                   "facility_dis_id": None,
                                   "batch_id": None,
                                   "filled_at": None,
                                   "car_id": None,
                                   'pack_status': settings.PENDING_PACK_STATUS}
                    status = revert_filling_pending_packs(revert_packs_ids_for_batch=final_pack_ids_to_revert,
                                                          update_dict=update_dict)
                    logger.info("In revert_batch_v3: call_from: {}, final_pack_ids_to_revert: {}, revert_mfd_filling_pending_packs status- {}"
                                .format(call_from_screen, final_pack_ids_to_revert, status))

                    # create record for reverted packs from manual fill flow(change status = 8 to pending =2)
                    for item in final_pack_ids_to_revert:
                        pack_status_tracker_list.append({"pack_id": item, "status": settings.PENDING_PACK_STATUS,
                                                 'created_by': user_id,
                                                 'reason':  "pack reverted"})

                    # create record for pack status tracker
                    status = create_pack_status_tracker_dao(pack_status_tracker_list=pack_status_tracker_list)
                    logger.info("In revert_batch_v3: entry created in pack status tracker: {}".format(status))

                    # TODO: batch id = null for manual fill flow not able to add entry in batch change tracker
                    # # save drug change tracker data in table
                    # status = BatchChangeTracker.db_save(batch_id=batch_id,
                    #                                     user_id=user_id,
                    #                                     action_id=ActionMaster.ACTION_ID_MAP[
                    #                                         ActionMaster.REVERT_BATCH_OR_PACKS],
                    #                                     params={"revert_from": call_from,
                    #                                             "module_id": current_module_id,
                    #                                             "batch_id": batch_id,
                    #                                             "user_id": user_id,
                    #                                             "pack_count": len(pack_ids)},
                    #                                     packs_affected=final_pack_ids_to_revert)
                    #
                    # logger.info("In revert_batch_v3: data saved in batch change tracker: {}, for call from: {}, current module id: {}"
                    #     .format(status, call_from, current_module_id))
                    return create_response(settings.SUCCESS_RESPONSE)

            # return create_response(settings.SUCCESS_RESPONSE)

    except (InternalError, IntegrityError) as e:
        logger.error("error in revert_batch_v3 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in revert_batch_v3: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in revert_batch_v3 {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in revert_batch_v3: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in revert_batch_v3: " + str(e))


@log_args_and_response
def get_progress_pending_patient_packs(pack_ids, query, call_from_screen):
    """
    @param pack_ids:
    @param query:
    @param call_from_screen:
    @return:

    function to get other packs of patient whose packs in  input packs to revert
    """
    try:
        input_pack_ids_to_revert_dict: dict = dict()
        pending_same_patient_dict: dict = dict()
        progress_same_patient_dict: dict = dict()
        pack_status_set: set = set()

        if call_from_screen == constants.CALL_FROM_PACK_QUEUE:
            status = settings.PENDING_PACK_STATUS
        else:
            status = settings.MANUAL_PACK_STATUS
        for patient_data in query:
            # create pack status set(input packs to revert)
            if patient_data['pack_id'] in pack_ids:
                pack_status_set.add(patient_data['pack_status'])

                # create input patient packs' dict(input_pack_ids_to_revert_dict = {1667: [78781], 1041: [79720]})
                if patient_data['patient_id'] not in input_pack_ids_to_revert_dict.keys():
                    input_pack_ids_to_revert_dict[patient_data['patient_id']] = list()
                input_pack_ids_to_revert_dict[patient_data['patient_id']].append(patient_data['pack_id'])
            else:
                # check other packs status of same patients(packs not in input pack list) is pending pack status then create
                # manual_pending_same_patient_dict = {1667: [78776, 78777], 1041: [79719, 79721]}
                if patient_data['pack_status'] == status:
                    if patient_data['patient_id'] not in pending_same_patient_dict.keys():
                        pending_same_patient_dict[patient_data['patient_id']] = list()
                    pending_same_patient_dict[patient_data['patient_id']].append(patient_data['pack_id'])

                # check other packs status of same patients(packs not in input pack list) = progress pack then create
                # manual_progress_same_patient_dict = {1041: [79722]}
                elif patient_data['pack_status'] == settings.PROGRESS_PACK_STATUS:
                    if patient_data['patient_id'] not in progress_same_patient_dict.keys():
                        progress_same_patient_dict[patient_data['patient_id']] = list()
                    progress_same_patient_dict[patient_data['patient_id']].append(patient_data['pack_id'])

        logger.info("In get_progress_pending_patient_packs: pending_same_patient_dict: {}, progress_same_patient_dict: {}, input_pack_ids_to_revert_dict: {}"
            .format(pending_same_patient_dict, progress_same_patient_dict,
                    input_pack_ids_to_revert_dict))

        return input_pack_ids_to_revert_dict, pending_same_patient_dict, progress_same_patient_dict, pack_status_set
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_progress_pending_patient_packs:".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_progress_pending_patient_packs:".format(e))
        raise e


@log_args_and_response
def revert_all_packs_of_batch_to_pack_pre_processing(analysis_ids: list, batch_id: int, company_id: int, mfd_analysis_ids: list,
                                                     system_device_dict: dict, system_id: int,
                                                     call_from_screen: str,
                                                     mfs_system_device: dict or None = None):
    """
             Function to revert all packs of batch to batch distribution screen
             @param mfs_system_device:
             @param batch_id:
             @param analysis_ids:
             @param company_id:
             @param mfd_analysis_ids:
             @param system_device_dict:
             @param system_id:
             @return:
       """
    try:
        # delete data from all the analysis table
        delete_pack_analysis_data, delete_mfd_analysis = \
            delete_analysis_data_for_revert_batch(batch_id=batch_id, analysis_ids=analysis_ids,
                                                  mfd_analysis_ids=mfd_analysis_ids)
        logger.info("In revert_all_packs_of_batch_to_pack_pre_processing: update table pack_analysis:{},"
                    "pack_analysis_details:{}".format(delete_pack_analysis_data, delete_mfd_analysis))

        # delete data from reserved_canisters table
        delete_reserved_canisters = delete_reserved_canister_for_batch(batch_id=batch_id)
        logger.info("In revert_all_packs_of_batch_to_pack_pre_processing: delete_reserved_canisters {}".format(
            delete_reserved_canisters))

        # delete data from canister_transfers and canister_tx_meta table
        delete_canister_transfer_data = delete_canister_transfers_for_batch(batch_id=batch_id)
        logger.info("In revert_all_packs_of_batch_to_pack_pre_processing: delete_canister_transfer_data {}".format(
            delete_canister_transfer_data))

        # delete data from frequent_mfd_drugs table
        delete_frequent_mfd_drugs = delete_frequent_mfd_drugs_for_revert_batch(batch_id=batch_id)
        logger.info(
            f"In revert_all_packs_of_batch_to_pack_pre_processing, delete_frequent_mfd_drugs: {delete_frequent_mfd_drugs}")


        batch_update_dict = {"status": settings.BATCH_PENDING, "sequence_no": constants.PPP_SEQUENCE_IN_PENDING}
        # update sequence_no to PPP_SEQUENCE_IN_PENDING and batch status to pending
        batch_status_update = update_batch_master_revert_batch(batch_id=batch_id,
                                                               batch_update_dict=batch_update_dict)
        logger.debug("In revert_all_packs_of_batch_to_pack_pre_processing:revert to: {}, sequence updated: {}, "
                     "changed sequence to {}, batch status to: {} for batch_Id: {}"
                     .format(constants.REVERT_TO_PACK_PRE_PROCESSING, batch_status_update,
                             constants.PPP_SEQUENCE_IN_PENDING, settings.BATCH_PENDING, batch_id))

        # update company level , system level couch db
        reset_company_level_cd_doc, reset_system_level_cd_doc = \
            revert_batch_couch_db_update(company_id=company_id, system_device_dict=system_device_dict,
                                         call_from_screen=call_from_screen)
        logger.info("In revert_all_packs_of_batch_to_pack_pre_processing: revert to : {}, "
                    "company_level couch db update: {}, system level couch db update: {}"
                    .format(constants.REVERT_TO_PACK_PRE_PROCESSING, reset_company_level_cd_doc,
                            reset_system_level_cd_doc))
        #
        # # reset MFS couch db documents when revert batch completely
        # if len(mfs_system_device):
        #     mfs_doc_status = reset_mfs_couch_db_documents_batch_revert(mfs_system_device)
        #     logger.info("In revert_all_packs_of_batch_to_pack_pre_processing: mfs_doc_status: {}"
        #                 .format(mfs_doc_status))

        # update couch db timestamp for pack_pre_processing_wizard change
        couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args={"system_id": system_id})
        logger.info("In revert_all_packs_of_batch_to_pack_pre_processing:revert to: {}, time stamp update for "
                    "pre processing wizard: {} for batch_id: {}"
                    .format(constants.REVERT_TO_PACK_PRE_PROCESSING, couch_db_status, batch_id))

        return True
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in revert_all_packs_of_batch_to_pack_pre_processing:".format(e))
        raise e


@log_args_and_response
def revert_all_packs_of_batch_to_batch_distribution(analysis_ids: list, company_id: int,
                                                    mfd_analysis_ids: list, revert_pack_id_list: list,
                                                    system_device_dict: dict, system_id: int,
                                                    update_dict: dict, call_from_screen:str, batch_id: int or None = None,
                                                    mfs_system_device: dict or None = None):
    """
          Function to revert all packs of batch to batch distribution screen
          @param update_dict:
          @param revert_pack_id_list:
          @param mfs_system_device:
          @param batch_id:
          @param analysis_ids:
          @param company_id:
          @param mfd_analysis_ids:
          @param system_device_dict:
          @param system_id:
          @return:
    """
    try:
        # delete data from all the analysis table
        delete_pack_analysis_data, delete_mfd_analysis = delete_analysis_data_for_revert_batch(batch_id=batch_id,
                                                                                               analysis_ids=analysis_ids,
                                                                                               mfd_analysis_ids=mfd_analysis_ids)
        logger.info(
            "In revert_all_packs_of_batch_to_batch_distribution: update table pack_analysis:{},pack_analysis_details:{}".format(
                delete_pack_analysis_data, delete_mfd_analysis))

        # delete data from frequent_mfd_drugs table
        delete_frequent_mfd_drugs = delete_frequent_mfd_drugs_for_revert_batch(batch_id=batch_id)
        logger.info(
            f"In revert_all_packs_of_batch_to_batch_distribution, delete_frequent_mfd_drugs: {delete_frequent_mfd_drugs}")

        # delete data from reserved_canisters table
        delete_reserved_canisters = delete_reserved_canister_for_batch(batch_id=batch_id)
        logger.info("In revert_all_packs_of_batch_to_batch_distribution: delete_reserved_canisters {}".format(
            delete_reserved_canisters))

        if batch_id:
            # delete data from canister_transfers and canister_tx_meta table
            delete_canister_transfer_data = delete_canister_transfers_for_batch(batch_id=batch_id)
            logger.info("In revert_all_packs_of_batch_to_batch_distribution: delete_canister_transfer_data {}".format(
                delete_canister_transfer_data))

        # update pack details set (system_id=None, facility_dis_id=None, batch_id=None, filled_at=None, car_id=None)
        pack_details_update = update_pack_details_data_for_batch(pack_list=revert_pack_id_list, update_dict=update_dict)
        logger.info(
            "IN revert_all_packs_of_batch_to_batch_distribution: pack_details updated:{}".format(pack_details_update))

        # update company level , system level couch db
        reset_company_level_cd_doc, reset_system_level_cd_doc = revert_batch_couch_db_update(company_id=company_id,
                                                                                             system_device_dict=system_device_dict,
                                                                                             call_from_screen=call_from_screen)
        logger.info("In revert_all_packs_of_batch_to_batch_distribution: company_level couch db update: {}, system level couch db update: {}"
            .format(reset_company_level_cd_doc, reset_system_level_cd_doc))

        # reset MFS couch db documents when revert batch completely
        # TODO: for now commented, because we don't have any case where filling is ongoing on MFS and we revert that packs
        # if len(mfs_system_device):
        #     mfs_doc_status = reset_mfs_couch_db_documents_batch_revert(mfs_system_device)
        #     logger.info("In revert_all_packs_of_batch_to_batch_distribution: mfs_doc_status: {}"
        #                 .format(mfs_doc_status))

        # update couch db timestamp for pack_pre_processing_wizard change
        couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args={"system_id": system_id})
        logger.info(
            "In revert_all_packs_of_batch_to_batch_distribution: time stamp update for pre processing wizard: {} for batch_id: {}".format(
                couch_db_status, batch_id))

        return True
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in revert_all_packs_of_batch_to_batch_distribution:".format(e))
        raise e


@log_args_and_response
def revert_filling_pending_packs(revert_packs_ids_for_batch: list, update_dict: dict, batch_id: int or None = None) -> bool:
    """
       Function to revert mfd filling pending packs
       @param update_dict:
       @param batch_id:
       @param revert_packs_ids_for_batch:
       @return:
       """
    try:
        # get analysis ids from pack_analysis table
        revert_analysis_ids = get_pack_analysis_details_ids_by_batch(batch_id=batch_id,
                                                                     pack_list=revert_packs_ids_for_batch)
        # get mfd analysis ids from mfd_analysis table
        revert_mfd_analysis_ids = get_mfd_analysis_ids_by_batch(batch_id=batch_id,
                                                                pack_list=revert_packs_ids_for_batch)

        pack_details_update = update_pack_details_data_for_batch(pack_list=revert_packs_ids_for_batch,
                                                                 update_dict=update_dict,
                                                                 batch_id=batch_id)
        logger.info("In revert_mfd_filling_pending_packs: pack_details updated:{}".format(pack_details_update))

        # delete the data from drug_tracker
        drug_tracker_delete_status = delete_drug_tracker_data_for_batch(analysis_ids=revert_analysis_ids,
                                                                        mfd_analysis_ids=revert_mfd_analysis_ids
                                                                        )

        logger.info("In revert_mfd_filling_pending_packs: drug_tracker_delete_status: {}"
                    .format(drug_tracker_delete_status))

        # delete the data from replenish_skipped_canister
        replenish_skipped_canister_delete_status = delete_replenish_skipped_canister_data_for_batch(pack_list=revert_packs_ids_for_batch)
        logger.info("In revert_mfd_filling_pending_packs: replenish_skipped_canister_delete_status: {}"
                    .format(replenish_skipped_canister_delete_status))

        # delete data from all the analysis table
        delete_pack_analysis_data, delete_mfd_analysis = delete_analysis_data_for_revert_batch(batch_id=batch_id,
                                                                                               analysis_ids=revert_analysis_ids,
                                                                                               mfd_analysis_ids=revert_mfd_analysis_ids)

        logger.info("In revert_mfd_filling_pending_packs: pack_analysis:{},pack_analysis_details:{}"
                    .format(delete_pack_analysis_data, delete_mfd_analysis))
        return True
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in revert_mfd_filling_pending_packs:".format(e))
        raise e


@log_args_and_response
def update_pack_details_and_batch_master_to_revert_batch_to_batch_dis(batch_id: int, pack_list: list, update_dict: dict, batch_update_dict: dict) -> tuple:
    """
    Function to update pack details and batch master to revert batch (all packs of batch)to batch distribution
    @param batch_update_dict:
    @param update_dict:
    @param batch_id:
    @param pack_list:
    @return:
    """
    try:
        batch_status_update = False
        pack_details_update = update_pack_details_data_for_batch(pack_list=pack_list, update_dict=update_dict, batch_id=batch_id)

        if batch_update_dict:
            # set batch status to batch deleted if all packs of batch is reverted to batch distribution screen
            batch_status_update = update_batch_master_revert_batch(batch_id=batch_id,
                                                                   batch_update_dict=batch_update_dict)
        return pack_details_update, batch_status_update
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in update_pack_details_and_batch_master_to_revert_batch_to_batch_dis:".format(e))
        raise e


@log_args_and_response
def revert_batch_couch_db_update(company_id: int, system_device_dict: dict, call_from_screen:str) -> tuple:
    """
    Function to update company level and system level couch db for revert batch
    @param company_id:
    @param system_device_dict:
    @return:
    """
    try:
        # reset company level couch db docs of canister transfer and guided tx
        reset_company_level_cd_doc = reset_company_level_couch_db_document_batch_revert(company_id=company_id,
                                                                                        call_from_screen=call_from_screen)

        # reset system level doc of canister transfer, guided tx and company level device doc of MFD
        reset_system_level_cd_doc = reset_system_level_couch_db_document_batch_revert(company_id=company_id,
                                                                                      system_device_dict=
                                                                                      system_device_dict,
                                                                                      call_from_screen=call_from_screen)
        return reset_company_level_cd_doc, reset_system_level_cd_doc
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in revert_batch_couch_db_update: {}".format(e))
        raise e


@log_args_and_response
def delete_analysis_data_for_revert_batch(analysis_ids: list, mfd_analysis_ids: list, batch_id: int or None) -> tuple:
    """
    Function to update pack details and batch master to revert batch (all packs of batch)to batch distribution
    @param analysis_ids:
    @param mfd_analysis_ids:
    @param batch_id:
    @return:
    """
    try:
        delete_pack_analysis_data: bool = False
        delete_mfd_analysis: bool = False
        if analysis_ids:
            # delete data from pack_analysis and pack_analysis_details table
            delete_pack_analysis_data = delete_data_from_pack_analysis_tables(batch_id=batch_id,
                                                                              analysis_ids=analysis_ids)
            logger.info("In delete_analysis_data_for_revert_batch: delete_pack_analysis_data {}"
                        .format(delete_pack_analysis_data))

        if mfd_analysis_ids:
            # delete data from mfd_analysis and mfd_analysis_details table
            delete_mfd_analysis = delete_mfd_analysis_data(batch_id=batch_id,
                                                           mfd_analysis_ids=mfd_analysis_ids)
            logger.info("In delete_analysis_data_for_revert_batch: delete_mfd_analysis {}".format(delete_mfd_analysis))

        return delete_pack_analysis_data, delete_mfd_analysis
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error(e)
        raise e


@log_args_and_response
def reset_company_level_couch_db_document_batch_revert(company_id: int,call_from_screen: str) -> bool:
    """
    Function to reset company level couch db documents of canister transfer and guided in case of batch revert
    @param company_id:
    @return:
    """
    try:
        # reset canister transfer wizard document
        if call_from_screen == constants.CALL_FROM_PACK_PRE_PROCESSING:
            document_name = constants.CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME
            reset_couch_db_dict_for_reset = {"company_id": company_id,
                                             "document_name": document_name,
                                             "couchdb_level": constants.STRING_COMPANY,
                                             "key_name": "data"}
            reset_couch_db_document(reset_couch_db_dict_for_reset)

        # todo commented because we don't want to revert when guided is in progress
        # reset guided transfer document
        # document_name = constants.GUIDED_TRANSFER_WIZARD
        # reset_couch_db_dict_for_reset = {"company_id": company_id,
        #                                  "document_name": document_name,
        #                                  "couchdb_level": constants.STRING_COMPANY,
        #                                  "key_name": "data"}
        # reset_couch_db_document(reset_couch_db_dict_for_reset)

        return True

    except Exception as e:
        logger.error("Error in reset_company_level_couch_db_document_batch_revert: {}".format(e))
        raise e


@log_args_and_response
def reset_system_level_couch_db_document_batch_revert(company_id: int, system_device_dict: dict, call_from_screen: str) -> bool:
    """
    Function to reset couch db document of canister transfers, mfd and guided transfer
    @param company_id:
    @param system_device_dict:
    @return:
    """
    try:
        if call_from_screen == constants.CALL_FROM_PACK_PRE_PROCESSING:
            for system_id, device_list in system_device_dict.items():
                for device_id in device_list:
                    # canister transfer document reset
                    reset_couch_db_dict_for_reset = {"system_id": system_id,
                                                     "document_name": str(
                                                         constants.CANISTER_TRANSFER_DEVICE_DOCUMENT_NAME) + '_{}'.format(
                                                         device_id),
                                                     "couchdb_level": constants.STRING_SYSTEM,
                                                     "key_name": "data"}
                    reset_couch_db_document(reset_couch_db_dict_for_reset)

                # todo: commented because we don't want to revert when guided is in progress
                # guided transfer document reset
                # document_name = str(constants.GUIDED_TRANSFER_DOCUMENT_NAME) + '_{}'.format(device_id)
                # reset_couch_db_dict_for_reset = {"system_id": system_id,
                #                                  "document_name": document_name,
                #                                  "couchdb_level": constants.STRING_SYSTEM,
                #                                  "key_name": "data"}
                # reset_couch_db_document(reset_couch_db_dict_for_reset)

                # todo: commented because we don't want to reset couch db as MFD can be in progress
                # reset MFD couch-db document for wizard
                # doc_name = str(constants.MFD_CANISTER_TRANSFER_WIZARD_DOCUMENT_NAME) + "-" + str(device_id)
                # reset_couch_db_dict_for_reset = {"company_id": company_id,
                #                                  "document_name": doc_name,
                #                                  "couchdb_level": constants.STRING_COMPANY,
                #                                  "key_name": "data"}
                # reset_couch_db_document(reset_couch_db_dict_for_reset)

        return True
    except Exception as e:
        logger.error("Error in reset_system_level_couch_db_document_batch_revert: {}".format(e))
        raise e


@log_args_and_response
def reset_mfs_couch_db_documents_batch_revert(mfs_system_device_dict: dict) -> bool:
    """
    Function to reset MFS related couch db document
    @param mfs_system_device_dict:
    @return:
    """
    try:
        mfs_systems = list(mfs_system_device_dict.keys())

        for system_id in mfs_systems:
            # clear MFS_v1 document
            mfs_status, mfs_doc = update_mfs_data_in_couch_db(document_name=constants.CONST_MANUAL_FILL_STATION_DOC_ID,
                                                              system_id=system_id,
                                                              mfs_data=dict(),
                                                              reset_data=True)
            logger.info("reset_mfs_couch_db_documents_batch_revert mfs_status, doc {}, {}".format(mfs_status, mfs_doc))

            # clear Mfd pre fill documents
            module_data = {
                'batch_id': 0,
                'trolley_scanned': False,
                'current_module': constants.MFD_MODULES["SCHEDULED_BATCH"]
            }
            logger.info('In reset_mfs_couch_db_documents_batch_revert: {}'.format(module_data))
            prefill_status, pre_filldoc = update_mfd_module_couch_db(constants.CONST_MFD_PRE_FILL_DOC_ID, system_id,
                                                                     module_data)
            logger.info("In reset_mfs_couch_db_documents_batch_revert: reset_mfs_couch_db_documents_batch_revert prefill, doc {}, {}".format(prefill_status, pre_filldoc))
        return True
    except Exception as e:
        logger.error("Error in reset_mfs_couch_db_documents_batch_revert: {}".format(e))
        raise e
