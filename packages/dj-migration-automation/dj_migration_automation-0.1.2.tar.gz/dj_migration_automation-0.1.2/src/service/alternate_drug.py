import json
import os
import sys
from collections import defaultdict
from copy import deepcopy
from typing import Dict
from peewee import DoesNotExist, InternalError, IntegrityError, DataError
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args, log_args_and_response, get_current_date_time
from dosepack.validation.validate import validate
from src.dao.batch_dao import save_batch_change_tracker_data, set_batch_status_dao
from src.dao.canister_dao import get_alternate_canister_for_batch_data, update_replenish_based_on_device, \
    get_alternate_canister_from_canister_id, db_skipped_canisters_insert_many_dao, \
    get_import_batch_id_from_system_id_or_device_id, get_ndc_list_for_deactivated_canisters
from src.dao.drug_dao import fetch_canister_drug_data_from_canister_ids, db_get_by_id, get_pack_drugs_by_pack_id_dao, \
    get_drug_and_bottle_information_by_drug_id_dao, get_drugs_for_batch_pre_processing, get_ordered_list, dpws_paginate, \
    db_get_drug_info_by_canister, get_fndc_txr_wise_inventory_qty
from src.dao.drug_inventory_dao import validate_facility_dist_id_by_company_id
from src.dao.pack_distribution_dao import get_multi_canister_drug_data_by_canister, db_get_pending_pack_list
from src.dao.pack_drug_dao import create_records_in_pack_drug_tracker, update_pack_rx_link_dao
from src.dao.patient_dao import get_patient_rx_data
from src.dao.reserve_canister_dao import get_reserved_canister_query
from src.exceptions import PharmacySoftwareCommunicationException, PharmacySoftwareResponseException, \
    AlternateDrugUpdateException
from src import constants
from src.dao.alternate_drug_dao import get_canister_data_from_txr, get_alternate_drug_verification_list, \
    alternate_drug_update, \
    db_get_alternate_drug_canisters, db_get_alternate_drugs, update_alternate_drug_canister_for_batch_data, \
    update_alternate_drug_for_batch_data, db_skip_for_batch, db_skip_canister_for_packs, get_drug_info_dao, \
    get_alternate_drug_data_dao, save_alternate_drug_option, get_old_drug_new_drug_data, \
    create_update_alternate_option_dao, update_alternate_drug_option_dao, get_alternate_drug_option_dao, \
    remove_alternate_drug_option_dao, get_altered_drugs_dao, remove_alternate_drug_by_id, get_packs_to_update_dao, \
    get_manual_drug_manual_pack_dao, get_save_alternate_drug, update_pack_analysis, \
    send_alternate_drug_change_data_to_ips, update_alternate_drug_for_batch_data_pack_queue, \
    db_skip_for_batch_pack_queue, db_skip_canister_for_packs_pack_queue, get_same_drug_canister
from src.dao.device_manager_dao import db_get_system_zone_mapping, get_device_master_data_dao
from src.dao.mfd_dao import get_drug_status_by_drug_id, get_batch_data
from src.dao.misc_dao import update_sequence_no_for_pre_processing_wizard, get_company_setting_by_company_id
from src.dao.pack_dao import get_pack_ids_by_batch_id, get_batch_id_from_packs, get_manual_pack_ids, \
    verify_pack_list_by_company_id, get_slot_data_by_pack_ids_drug_ids, update_slot_details_by_slot_id_dao
from src.service.canister import revert_replenish_skipped_canister
from src.service.canister_recommendation import use_other_canisters
from src.service.pack import update_drug_status
from src.dao.pack_analysis_dao import update_pack_analysis_canisters_data, \
    update_pack_analysis_details_by_analysis_slot_id
from src.model.model_patient_rx import PatientRx
from src.service.mfd import update_mfd_alternate_drug
from src.service.misc import update_timestamp_couch_db_pre_processing_wizard
from src.service.volumetric_analysis import get_available_drugs_for_recommended_canisters
from utils.auth_webservices import send_email_for_defective_skip_canister
from utils.drug_inventory_webservices import get_current_inventory_data

logger = settings.logger


@log_args_and_response
def get_selected_alternate_drug_list(data_dict):
    """
    Fetches all the drugs fow which alternate are chosen after batch_distribution
    :param data_dict:
    :return:
    """
    try:
        system_id = int(data_dict['system_id'])
        system_list = data_dict['system_id'].split(',')
        system_zone_mapping, zone_list = db_get_system_zone_mapping(system_list)
        zone_id = system_zone_mapping[system_id]
        company_id = data_dict['company_id']
        filter_fields = data_dict.get('filter_fields', None)
        sort_fields = data_dict.get('sort_fields', None)
        paginate = data_dict.get('paginate', None)
        batch_id = data_dict['batch_id']
        args = {"system_id": system_id}
        alt_verification_data = list()
        alternate_drug_data = list()
        list_length = 0
        order_list = list()
        temp_dict = defaultdict(dict)
        paginated_txr = list()
        # paginated_result = list()
        paginated_ndc_list = []

        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, ' Missing key(s) in paginate.')
        if sort_fields:
            order_list = sort_fields
        order_list.insert(0, ['required_qty', -1])

        logger.info("Inside get_selected_alternate_drug_list, fetching drug data")
        # getting all the drugs whose alternate drugs are present, in batch
        drug_data_dict, total_count, txr_list, changed_bs_count, ndc_list = get_drugs_for_batch_pre_processing(
            company_id=company_id, batch_id=batch_id, filter_fields=filter_fields)
        # ndc_list = [str(x).zfill(11) for x in ndc_list]
        # ndc_list_for_change_ndc = get_ndc_list_for_deactivated_canisters(ndc_list)
        # change_ndc_drug_list = get_available_drugs_for_recommended_canisters(ndc_list)
        # change_ndc_drug_list = [x.zfill(11) for x in change_ndc_drug_list]

        logger.info("Inside get_selected_alternate_drug_list, fetched drug data")
        if drug_data_dict:
            # Fetch EPBM inventory data
            inventory_qty = get_fndc_txr_wise_inventory_qty(txr_list)
            inventory_quantity = get_current_inventory_data(ndc_list=ndc_list, qty_greater_than_zero=False)
            inventory_qty_ndc_dict = {}
            for item in inventory_quantity:
                inventory_qty_ndc_dict[item['ndc']] = item['quantity']

            logger.info("Inside get_selected_alternate_drug_list, fetching Canister data")
            # Fetching canister data for the given drugs
            alt_txr_set_can_data = get_canister_data_from_txr(company_id,
                                                              list(txr_list),
                                                              zone_id,
                                                              )

            for fndc_txr, drug_data in drug_data_dict.items():
                # formatted_ndc, txr = fndc_txr
                drug_data['canister_avl_qty'] = 0
                drug_data['inventory_qty'] = inventory_qty_ndc_dict.get(drug_data['ndc'], 0)
                drug_data['is_in_stock'] = 0 if drug_data['inventory_qty'] <= 0 else 1
                drug_data['can_data'] = alt_txr_set_can_data.get(fndc_txr, [])
                drug_data['canister_qty'] = len(drug_data['can_data'])
                drug_data['alternate_drug_list'] = list()
                for item in drug_data['can_data']:
                    drug_data['canister_avl_qty'] += item['available_quantity']
                # packing data dict for sorting
                alt_verification_data.append(drug_data)
                list_length += 1
            # Getting sorted drugs for the whole batch
            drug_canister_data = get_ordered_list(alt_verification_data, order_list)
            # paginating drug list
            if paginate:
                paginated_result = dpws_paginate(drug_canister_data, paginate)
            # Unpacking drug list to add alternate drug data
            for record in paginated_result:
                temp_dict[(record['formatted_ndc'], record['txr'])] = record
                paginated_txr.append(record['txr'])
                paginated_ndc_list.append(record['ndc'])
            change_ndc_drug_list = get_available_drugs_for_recommended_canisters(paginated_ndc_list)
            change_ndc_drug_list = [x.zfill(11) for x in change_ndc_drug_list]

            logger.info("Inside get_selected_alternate_drug_list, fetching alternate drug data")
            alt_canister_data, alternate_drug_list = get_alternate_drug_verification_list(list(paginated_txr),
                                                                                          zone_id,
                                                                                          )

            for fndc_txr, drug_data in temp_dict.items():
                drug_data['change_ndc_available'] = True if drug_data['ndc'] in change_ndc_drug_list else False
                formatted_ndc, txr = fndc_txr
                alt_data = alternate_drug_list[txr]
                for alt_fndc, alt_fndc_data in alt_data.items():
                    alt_fndc_data['canister_avl_qty'] = 0
                    alt_fndc_data['inventory_qty'] = inventory_qty.get((alt_fndc, txr), 0)
                    alt_fndc_data['is_in_stock'] = 0 if alt_fndc_data['inventory_qty'] == 0 else 1
                    if alt_fndc != formatted_ndc:
                        canister_data = alt_canister_data.get((alt_fndc, txr), {})
                        if canister_data:
                            alt_fndc_data['can_data'] = canister_data
                            for item in alt_fndc_data['can_data']:
                                alt_fndc_data['canister_avl_qty'] += item['available_quantity']
                        alt_fndc_data['canister_count'] = len(canister_data)
                        drug_data['alternate_drug_list'].append(alt_fndc_data)

                if drug_data['alternate_drug_list']:
                    drug_data['alternate_drug_list'] = sorted(drug_data['alternate_drug_list'],
                                                              key=lambda i: (i['ext_status'],
                                                                             i['alt_selection'],
                                                                             i['canister_count'], i['inventory_qty'],
                                                                             i['sort_last_billed_date']),
                                                              reverse=True)
                # Packing data dict to list of dict for response
                alternate_drug_data.append(drug_data)

            logger.info('Inside get_selected_alternate_drug_list:  adding_alt_data: end')

        if not alt_verification_data and not filter_fields:
            # update sequence_no to PPP_SEQUENCE_SAVE_ALTERNATES
            # seq_status = update_sequence_no_for_pre_processing_wizard(
            #     sequence_no=constants.PPP_SEQUENCE_SAVE_ALTERNATES,
            #     batch_id=int(batch_id))
            # logger.info(
            #     "In get_selected_alternate_drug_list: alternate drug verification list is empty, changed sequence to {} for batch_id: {}"
            #     .format(constants.PPP_SEQUENCE_SAVE_ALTERNATES, int(batch_id)))
            # update couch db timestamp for pack_pre_processing_wizard change
            couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=args)
            logger.info(
                "In get_selected_alternate_drug_list : time stamp update for pre processing wizard: {} for batch_id: {}".format(
                    couch_db_status, int(batch_id)))
        result = {
            "drug_data": alternate_drug_data,
            "list_length": list_length,
            "changed_bs_count": changed_bs_count,
            "total_batch_generic_drugs": total_count
        }
        # logger.info("Inside get_selected_alternate_drug_list,RESPONSE: {}".format(result))
        return create_response(result)
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error in get_selected_alternate_drug_list: exc_type - {exc_type}, f_name - {f_name}, line - {exc_tb.tb_lineno}")
        logger.info(e)
        raise e


@log_args
@validate(required_fields=["batch_id", "old_drug_list", "new_drug_list", "user_id", "company_id"])
def update_saved_alternate_drug(dict_alternate_drug_info):
    # validating drugs and alternate drugs
    alt_drugs = dict_alternate_drug_info['new_drug_list'].split(',')
    original_drugs = dict_alternate_drug_info['old_drug_list'].split(',')
    # fill_manually = list(map(lambda x: int(x), dict_alternate_drug_info['fill_manually'].split(',')))
    alt_fndc_txr_dict = dict()
    if len(alt_drugs) != len(original_drugs):
        return error(1020, 'Length of old_drug_list and new_drug_list should be same.')
    try:
        for index in range(0, len(alt_drugs)):
            alternate_drug = get_drug_status_by_drug_id(drug_id=alt_drugs[index], dicts=True)
            current_drug = get_drug_status_by_drug_id(original_drugs[index], dicts=True)
            alt_fndc_txr_dict['{}#{}'.format(current_drug['formatted_ndc'], current_drug['txr'])] = \
                '{}#{}'.format(alternate_drug['formatted_ndc'], alternate_drug['txr'])
            valid_alternate_drug = current_drug and alternate_drug \
                                   and current_drug['formatted_ndc'] != alternate_drug['formatted_ndc'] \
                                   and current_drug['txr'] == alternate_drug['txr'] \
                                   and str(current_drug['brand_flag']) == \
                                   str(alternate_drug['brand_flag']) == settings.GENERIC_FLAG
            if not valid_alternate_drug:
                return error(1020, 'The parameter drug_id and alt_drug_id are not alternate drugs.')

        company_id = dict_alternate_drug_info["company_id"]

        pack_ids = get_pack_ids_by_batch_id(
            dict_alternate_drug_info['batch_id'],
            company_id
        )
        if not pack_ids:
            return error(1020)

        response = alternate_drug_update({
            'pack_list': ','.join(map(str, pack_ids)),
            'olddruglist': dict_alternate_drug_info['old_drug_list'],
            'newdruglist': dict_alternate_drug_info['new_drug_list'],
            'alt_fndc_txr_dict': alt_fndc_txr_dict,
            'user_id': dict_alternate_drug_info['user_id'],
            'company_id': company_id,
            'batch_id': dict_alternate_drug_info['batch_id'],
            'changed_after_batch': True,
            'module_id': constants.PDT_PRE_PROCESSING_ALTERNATE_DRUG_UPDATE
        })
        response = json.loads(response)
        if response['status'] != 'success':
            # throwing exception to rollback changes as we could not update IPS
            return error(response['code'])
        else:
            return create_response(1)
    except (InternalError, DataError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error in update_saved_alternate_drug: exc_type - {exc_type}, f_name - {f_name}, line - {exc_tb.tb_lineno}")
        logger.info(e)
        raise e


@log_args
def replenish_alternate_options(company_id, canister_id, device_id, guided_transfer=False, batch_id=None,
                                robot_utility_call=False) -> Dict:
    try:
        # get alternate canisters

        alternate_canisters = get_alternate_canister_for_batch_data(company_id=company_id,
                                                                        alt_in_robot=False,
                                                                        canister_ids=[int(canister_id)],
                                                                        current_not_in_robot=False,
                                                                        device_id=device_id,
                                                                        guided_transfer=guided_transfer,
                                                                    batch_id=batch_id)

        reserved_canisters_query = get_reserved_canister_query(device_id=device_id, company_id=company_id)
        logger.info("In replenish_alternate_options: reserved_canisters_query: {}".format(reserved_canisters_query))

        same_drug_canisters = get_same_drug_canister(canister_ids=[int(canister_id)], device_id=device_id,
                                                     alt_canisters_count=len(alternate_canisters))

        alternate_drug_canisters = db_get_alternate_drug_canisters(canister_id=canister_id,
                                                                   company_id=company_id,
                                                                   reserved_canister_query=reserved_canisters_query,
                                                                   same_drug_canisters=same_drug_canisters)

        alternate_drugs = db_get_alternate_drugs(canister_id=canister_id, company_id=company_id,
                                                 same_drug_canisters=same_drug_canisters)
        # get drug bottles for canister
        # TODO FUTURE
        # alternate drug bottles, drugs
        # TODO FUTURE

        response = {
            'alt_canisters': alternate_canisters,
            'alt_drug_canisters': alternate_drug_canisters,
            'alt_drugs': alternate_drugs,
        }
        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in replenish_alternate_options: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)
    except Exception as e:
        logger.error("Error in replenish_alternate_options {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in replenish_alternate_options: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)


@validate(required_fields=['action', 'company_id', 'user_id', 'device_id'])
@log_args_and_response
def save_replenish_alternate(request_args):
    alt_canister = 'alt_canister'
    alt_drug_canister = 'alt_drug_canister'  # alternate drug with canister
    alt_drug = 'alt_drug'
    skip_for_batch = 'skip_for_batch'
    skip_for_packs = 'skip_for_packs'
    valid_actions = frozenset([alt_canister, alt_drug, alt_drug_canister, skip_for_batch, skip_for_packs])
    action = request_args['action']
    company_id = request_args['company_id']
    current_pack_id = request_args.get('current_pack_id', None)
    device_id = request_args['device_id']
    user_id = request_args['user_id']
    robot_utility_call = request_args.get('robot_utility_call', False)
    batch_id = request_args.get('batch_id', None)
    system_id = request_args.get('system_id', None)
    skip_reason = request_args.get('skip_reason', None)
    module_id = request_args.get('module_id', constants.MODULE_PACK_PRE_PROCESSING)
    skipped_canister_list: list = list()
    canister_list = [request_args.get('canister_id')]
    skip_defective_canister_list = list()
    # todo: Remove batch_id once all internal dependency get sorted

    if action not in valid_actions:
        return error(1020, 'Action is not valid. Valid Actions: {}.'.format(valid_actions))
    try:

        # check for alternate canister action
        if action == alt_canister:
            # update canister id in pack analysis
            canister_id = request_args.get('canister_id')
            alt_canister_id = request_args.get('alt_canister_id')
            with db.transaction():

                try:
                    if module_id == constants.MODULE_REPLENISH_SKIPPED_CANISTER:
                        args_dict = dict()
                        args_dict["user_id"] = user_id
                        args_dict["device_id"] = device_id
                        args_dict["system_id"] = system_id
                        args_dict["company_id"] = company_id
                        args_dict["canister_id"] = canister_id
                        response = revert_replenish_skipped_canister(args_dict)
                        logger.info("In save_replenish_alternate: revert_replenish_skipped_canister: response: {}"
                                    .format(response))

                    status = update_pack_analysis_canisters_data(replace_canisters={canister_id: alt_canister_id},
                                                                 batch_id=batch_id,
                                                                 user_id=user_id,
                                                                 robot_utility_call=robot_utility_call,
                                                                 device_id=device_id,
                                                                 company_id=company_id)

                    if module_id == constants.MODULE_REPLENISH_SKIPPED_CANISTER:
                        update_replenish_based_on_device(device_id)
                        return create_response(status)

                except ValueError as e:
                    return error(1020, str(e))

        # check for alternate drug canister action
        elif action == alt_drug_canister:
            canister_id = request_args.get('canister_id')
            alt_canister_id = request_args.get('alt_canister_id')
            if robot_utility_call:
                batch_id = None
            with db.transaction():

                try:
                    if module_id == constants.MODULE_REPLENISH_SKIPPED_CANISTER:
                        args_dict = dict()
                        args_dict["user_id"] = user_id
                        args_dict["device_id"] = device_id
                        args_dict["system_id"] = system_id
                        args_dict["company_id"] = company_id
                        args_dict["canister_id"] = canister_id
                        response = revert_replenish_skipped_canister(args_dict)
                        logger.info("In save_replenish_alternate: revert_replenish_skipped_canister: response: {}"
                                    .format(response))

                    status, response = update_alternate_drug_canister_for_batch_data(batch_id=batch_id,
                                                                                     canister_id=canister_id,
                                                                                     alt_canister_id=alt_canister_id,
                                                                                     device_id=device_id,
                                                                                     user_id=user_id,
                                                                                     company_id=company_id)
                    logger.info("In save_replenish_alternate: status: {}, response: {}".format(status, response))

                    if module_id == constants.MODULE_REPLENISH_SKIPPED_CANISTER:
                        update_replenish_based_on_device(device_id)
                        return create_response(status)

                    if not status and response:
                        manual_packs = {"manual_packs": response}
                        return create_response(manual_packs)
                except ValueError as e:
                    return error(1020, str(e))

        # check for alternate drug action
        elif action == alt_drug:
            # update patient_rx and IPS
            canister_id = request_args.get('canister_id')
            alt_drug_id = request_args.get('alt_drug_id')
            with db.transaction():

                if not robot_utility_call:
                    status, response = update_alternate_drug_for_batch_data(canister_id=canister_id,
                                                                            alt_drug_id=alt_drug_id,
                                                                            batch_id=batch_id,
                                                                            current_pack_id=current_pack_id,
                                                                            device_id=device_id,
                                                                            user_id=user_id,
                                                                            company_id=company_id)
                else:
                    status, response = update_alternate_drug_for_batch_data_pack_queue(canister_id=canister_id,
                                                                                       alt_drug_id=alt_drug_id,
                                                                                       batch_id=None,
                                                                                       current_pack_id=current_pack_id,
                                                                                       device_id=device_id,
                                                                                       user_id=user_id,
                                                                                       company_id=company_id)

                if not status and response:
                    manual_packs = {"manual_packs": response}
                    return create_response(manual_packs)

        # check for action skip for batch
        elif action == skip_for_batch:
            canister_list = request_args['canister_list']
            with db.transaction():
                if not robot_utility_call:
                    status, response = db_skip_for_batch(batch_id=batch_id,
                                                         canister_list=canister_list,
                                                         user_id=user_id,
                                                         current_pack=current_pack_id)
                else:
                    status, response = db_skip_for_batch_pack_queue(batch_id=None,
                                                                    canister_list=canister_list,
                                                                    user_id=user_id,
                                                                    current_pack=current_pack_id,
                                                                    device_id=device_id)

            if batch_id is None:
                batch_id = get_import_batch_id_from_system_id_or_device_id(device_id=device_id)
            txr_dict, can_list = get_multi_canister_drug_data_by_canister(canister_list, device_id, batch_id)
            if can_list:
                rerun_drop_optimisation = use_other_canisters(device_id, can_list, company_id, batch_id=batch_id)
            logger.info(
                "In save_replenish_alternate skip for batch response status for skip_for_batch: {}".format(status))

            if not status and response:
                manual_packs = {"manual_packs": response}
                return create_response(manual_packs)

        # check for action skip for packs
        elif action == skip_for_packs:
            canister_list = request_args['canister_list']
            pack_count_to_skip = request_args['packs_to_skip']
            manual_pack_count = request_args.get('manual_pack_count', None)
            with db.transaction():
                if not robot_utility_call:
                    status, response = db_skip_canister_for_packs(batch_id=batch_id,
                                                                  canister_list=canister_list,
                                                                  user_id=user_id,
                                                                  current_pack=current_pack_id,
                                                                  device_id=device_id,
                                                                  pack_count=pack_count_to_skip,
                                                                  manual_pack_count=manual_pack_count)
                else:
                    status, response = db_skip_canister_for_packs_pack_queue(batch_id=None,
                                                                             canister_list=canister_list,
                                                                             user_id=user_id,
                                                                             current_pack=current_pack_id,
                                                                             device_id=device_id,
                                                                             pack_count=pack_count_to_skip,
                                                                             manual_pack_count=manual_pack_count)
            logger.info(
                "In save_replenish_alternate skip for batch response status for skip_for_packs:{}".format(status))
            if batch_id is None:
                batch_id = get_import_batch_id_from_system_id_or_device_id(device_id=device_id)
            txr_dict, can_list = get_multi_canister_drug_data_by_canister(canister_list, device_id, batch_id)
            if can_list:
                if response:
                    affected_pack_list = db_get_pending_pack_list(pack_list=response)
                    if affected_pack_list:
                        rerun_drop_optimisation = use_other_canisters(device_id, can_list, company_id, batch_id=batch_id,
                                                                      affected_pack_list=affected_pack_list)
            if not status and response:
                manual_packs = {"manual_packs": response}
                return create_response(manual_packs)

        for canister in canister_list:
            if canister:
                skipped_from = constants.SKIPPED_MODULE_ID_DICT[module_id]
                skip_canister_data = {
                    'batch_id': batch_id,
                    'created_by': user_id,
                    'canister_id': canister,
                    'skip_reason': skip_reason,
                    'skipped_from': skipped_from
                }
                skipped_canister_list.append(skip_canister_data)
                if skip_reason != 'Drug out of stock':
                    skip_canister_data.pop('batch_id')
                    skip_defective_canister_list.append(skip_canister_data)
                    if skip_reason in [constants.SKIP_REASON_DRUG_NOT_ENOUGH_DRUG_QUANTITY] and settings.USE_EPBM:
                        drug_info = db_get_drug_info_by_canister(canister)

                        args = {
                            "drug_id": drug_info['drug_id'],
                            "is_in_stock": 0,
                            "user_id": user_id,
                            "user_confirmation": True,
                            "reason": skip_reason
                        }
                        status = update_drug_status(args)

                else:
                    if settings.USE_EPBM:
                        drug_info = db_get_drug_info_by_canister(canister)

                        args = {
                            "drug_id": drug_info['drug_id'],
                            "is_in_stock": 0
                        }
                        status = update_drug_status(args)
        logger.info(
            "In save_replenish_alternate defective skip canister are: {}".format(skip_defective_canister_list))

        if skipped_canister_list:
            db_skipped_canisters_insert_many_dao(skipped_canister_list)

        if skip_defective_canister_list:
            send_email_for_defective_skip_canister(company_id=company_id,
                                                   skip_defective_canister_data=skip_defective_canister_list)

        update_replenish_based_on_device(device_id)
        return create_response(status)

    except AlternateDrugUpdateException as e:
        return error(int(str(e)))
    except PharmacySoftwareCommunicationException as e:
        logger.error(e, exc_info=True)
        return error(7001)
    except PharmacySoftwareResponseException as e:
        logger.error(e, exc_info=True)
        return error(7001)
    except (InternalError, IntegrityError, ValueError, DataError) as e:
        logger.error("error in save_replenish_alternate {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in save_replenish_alternate: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in save_replenish_alternate {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            f"Error in save_replenish_alternate: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in save_replenish_alternate: " + str(e))


@validate(required_fields=["drug_id", "company_id"])
def get_alternate_drugs(drug_info):
    """
         Fetches alternate drugs
        @param drug_info:
        @return:
    """

    drug_id = drug_info["drug_id"]
    company_id = drug_info["company_id"]
    device_id = drug_info["device_id"]
    paginate = drug_info.pop("paginate", None)
    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, 'Missing key(s) in paginate.')
    sort_fields = drug_info.pop("sort_fields", None)

    try:
        # get drug information by company id and drug id
        drug = get_drug_info_dao(company_id=company_id, drug_id=drug_id)

        device_type_id = None
        if device_id:
            # find device_type_id for device_id
            device_type_id_query = get_device_master_data_dao(device_id=device_id)
            for data in device_type_id_query:
                device_type_id = data['device_type_id']
        # get all canister data for drug from list of canister
        drug['canister_list_with_qty'] = fetch_canister_drug_data_from_canister_ids(canister_ids=drug['canister_ids'],
                                                                                    device_id=device_id,
                                                                                    device_type_id=device_type_id)
        drug['available_quantity'] = float(drug['available_quantity'] if drug['available_quantity'] else 0)
        alternate_drugs, count = get_alternate_drug_data_dao(company_id=company_id,
                                                             device_id=device_id,
                                                             device_type_id=device_type_id,
                                                             drug_id=drug_id,
                                                             paginate=paginate,
                                                             sort_fields=sort_fields)
        drug["alternate_drugs"] = alternate_drugs

        response = {"total_records": count,
                    "drugs": drug}
        return create_response(response)

    except (DoesNotExist, StopIteration) as e:
        logger.error(e, exc_info=True)
        return error(1020)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_alternate_drugs {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_alternate_drugs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_alternate_drugs {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_alternate_drugs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_alternate_drugs: " + str(e))


@validate(required_fields=["facility_distribution_id", "user_id", "company_id"])
def add_all_alternate_drug(info_dict):
    """
    Function to add all alternate drugs
    @param info_dict:
    @return:
    @rtype: object
    """
    # temporary check
    create_response(True)
    try:
        if not info_dict["facility_distribution_id"] or not info_dict["company_id"] or not info_dict["user_id"]:
            return error(1001, "Missing Parameter(s): facility_distribution_id or company_id or user_id.")

        response = save_alternate_drug_option(pack_data={'facility_distribution_id': info_dict['facility_distribution_id'],
                                               'company_id': info_dict['company_id'],
                                               'user_id': info_dict['user_id'],
                                               'save_alternate_drug_option': True})
        return response

    except (InternalError, IntegrityError) as e:
        logger.error("error in add_all_alternate_drug {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_all_alternate_drug: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in add_all_alternate_drug {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_all_alternate_drug: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in add_all_alternate_drug: " + str(e))


@validate(required_fields=['old_drug_ids', 'new_drug_ids', 'facility_distribution_id', 'user_id',
                           'company_id'])
def add_alternate_drug_data(drug_data):
    """
    adds alternate drug and alternate canister for batch_distribution
    :param drug_data:
    :return:
    """
    record = None
    incorrect_alternate_drug_list: list = list()
    alt_drug: set = set()
    company_id = drug_data['company_id']
    facility_distribution_id = drug_data['facility_distribution_id']
    user_id = drug_data['user_id']

    valid_batch_distribute = validate_facility_dist_id_by_company_id(company_id=company_id, facility_dist_id=facility_distribution_id)
    if not valid_batch_distribute:
        return error(1034)

    old_drug_ids = list(map(int, drug_data['old_drug_ids'].split(',')))
    new_drug_ids = list(map(int, drug_data['new_drug_ids'].split(',')))

    logger.info("In add_alternate_drug_data: len(old_drug_ids): {},len(new_drug_ids): {}".format(old_drug_ids, new_drug_ids))
    if not (len(old_drug_ids) == len(new_drug_ids)):
        return error(1020, 'Length of old_drug_ids, new_drug_ids and new_canister_ids should be same.')

    try:
        for i in range(0, len(old_drug_ids)):
            try:
                new_drug_record, old_drug_record = get_old_drug_new_drug_data(i=i, new_drug_ids=new_drug_ids, old_drug_ids=old_drug_ids)

            except DoesNotExist as e:
                logger.info("In add_alternate_drug_data : data not exit: {}".format(e))
                incorrect_alternate_drug_dict = {'old_drug_id': old_drug_ids[i],
                                                 'alternate_drug_id': new_drug_ids[i],
                                                 'reason': 'Drug not available'
                                                 }
                incorrect_alternate_drug_list.append(incorrect_alternate_drug_dict)
                continue

            # is_alternate = old_drug_record['txr'] == new_drug_record['txr'] \
            #                and old_drug_record['formatted_ndc'] != new_drug_record['formatted_ndc'] \
            #                and str(old_drug_record['brand_flag']) == settings.GENERIC_FLAG == str(
            #     new_drug_record['brand_flag'])

            # commented above code to allow saving same drug for alternate
            is_alternate = old_drug_record['txr'] == new_drug_record['txr'] \
                           and str(old_drug_record['brand_flag']) == settings.GENERIC_FLAG == str(
                new_drug_record['brand_flag']) and new_drug_record['ext_status'] == settings.VALID_EXT_STATUS

            logger.info("In add_alternate_drug_data: is_alternate: {}".format(is_alternate))

            if not is_alternate:
                incorrect_alternate_drug_dict = {'old_drug_id': old_drug_ids[i],
                                                 'alternate_drug_id': new_drug_ids[i],
                                                 'reason': 'Drug_id and Alternate_drug_id are not alternate of eachother'}
                incorrect_alternate_drug_list.append(incorrect_alternate_drug_dict)
            else:
                create_dict = {'unique_drug_id': old_drug_record['unique_drug_id'],
                               'alternate_unique_drug_id': new_drug_record['unique_drug_id'],
                               'facility_dis_id': facility_distribution_id
                               }
                default_dict = {'created_by': user_id,
                                'modified_by': user_id,
                                'active': True,
                                'modified_date': get_current_date_time()
                                }

                logger.info("In add_alternate_drug_data: create_dict: {}, default_dict: {}".format(create_dict, default_dict))
                record = create_update_alternate_option_dao(create_dict=create_dict, update_dict=default_dict)
                alt_drug.add(new_drug_record['unique_drug_id'])

        logger.info("In add_alternate_drug_data: alt_drug: {}".format(alt_drug))
        if alt_drug:
            update_dict = {"active": 1}
            status = update_alternate_drug_option_dao(update_dict=update_dict, alt_drug_list=list(alt_drug))
            print(status)

        logger.info("In add_alternate_drug_data: incorrect_alternate_drug_list: {}".format(incorrect_alternate_drug_list))

        response = {'incorrect_alternate_drug_list': incorrect_alternate_drug_list,
                    'correct_drug_status': True if record else False}

        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in add_alternate_drug_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_alternate_drug_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in add_alternate_drug_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in add_alternate_drug_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in add_alternate_drug_data: " + str(e))


@log_args_and_response
def get_alternate_drug_option(company_id: int, facility_distribution_id: int) -> dict:
    """
    returns alternate option for particular batch_distribution
    :param company_id:
    :param facility_distribution_id:
    :return:
    """
    try:


        valid_batch_distribute = validate_facility_dist_id_by_company_id(company_id=company_id,
                                                                         facility_dist_id=facility_distribution_id)
        if not valid_batch_distribute:
            return error(1034)

        alternate_drug_options = get_alternate_drug_option_dao(facility_dist_id=facility_distribution_id)
        response = {'alternate_drug_options': alternate_drug_options}
        return create_response(response)

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_alternate_drug_option {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_alternate_drug_option: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_alternate_drug_option {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_alternate_drug_option: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_alternate_drug_option: " + str(e))


@log_args
@validate(required_fields=["facility_distribution_id", "company_id", "user_id"])
def remove_alternate_drug_option(drug_dict):
    """
    removes alternate drug option for particular batch_distribution
    :param drug_dict:
    :return:
    """
    try:
        facility_distribution_id = drug_dict['facility_distribution_id']
        company_id = drug_dict['company_id']
        user_id = drug_dict['user_id']
        valid_facility_dis_id = validate_facility_dist_id_by_company_id(company_id=company_id,
                                                                        facility_dist_id=facility_distribution_id)
        if not valid_facility_dis_id:
            return error(1034)

        alternate_drug_option_ids = drug_dict.get('alternate_drug_option_ids', None)
        drug_ids = drug_dict.get('drug_ids', None)
        alternate_drug_ids = drug_dict.get('alternate_drug_ids', None)
        logger.info("In remove_alternate_drug_option: alternate_drug_option_ids: {}, drug_ids: {}, alternate_drug_ids: {}"
            .format(alternate_drug_option_ids, drug_ids, alternate_drug_ids))

        if alternate_drug_option_ids is None and drug_ids is None and alternate_drug_ids is None:
            return error(1001, "Missing Parameter(s): alternate_drug_option_ids and drug_ids and alternate_drug_ids.")

        if alternate_drug_option_ids:
            alternate_drug_option_ids_list = list(map(int, alternate_drug_option_ids.split(',')))
            update_dict = {"active": False,
                           "modified_date": get_current_date_time(),
                           "modified_by": user_id}
            status = remove_alternate_drug_by_id(update_dict=update_dict, alt_drug_option_ids=alternate_drug_option_ids_list)
            return create_response({'status': status})

        if drug_ids:
            status = remove_alternate_drug_option_dao(drug_ids_list=drug_ids,
                                                      facility_distribution_id=facility_distribution_id,
                                                      user_id=user_id)

            return create_response({'status': status})
        if alternate_drug_ids:
            status = remove_alternate_drug_option_dao(drug_ids_list=alternate_drug_ids,
                                                      facility_distribution_id=facility_distribution_id,
                                                      user_id=user_id)
            return create_response({'status': status})

    except ValueError as e:
        logger.error("error in remove_alternate_drug_option {}".format(e))
        return error(1020)

    except (InternalError, IntegrityError) as e:
        logger.error("error in remove_alternate_drug_option {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in remove_alternate_drug_option: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in remove_alternate_drug_option {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in remove_alternate_drug_option: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in remove_alternate_drug_option: " + str(e))


@log_args
@validate(required_fields=["pack_id"])
def get_altered_drugs_of_pack(args):
    """
    Returns all altered drugs of a pack
    @param args: {"pack_id": int}
    @return: dict
    """
    pack_id = args.get("pack_id")
    try:
        response = get_altered_drugs_dao(pack_id=pack_id)

        return create_response(response)

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_altered_drugs_of_pack {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_altered_drugs_of_pack: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_altered_drugs_of_pack {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_altered_drugs_of_pack: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_altered_drugs_of_pack: " + str(e))


@log_args_and_response
def update_alternate_drug_for_batch_manual_canister(update_drug_dict: dict):
    """
        update alternate drug for batch manual canister , update patient_rx, IPS
        @param update_drug_dict:
        @return:
    """
    analysis_ids: list = list()
    pack_ids: list = list()
    drug_list: list = list()
    alt_drug_list: list = list()
    slot_ids: list = list()
    pack_list: list = list()

    try:
        old_drug_ids = [update_drug_dict['drug_id']]
        alt_drug_id = update_drug_dict['alt_drug_id']
        batch_id = update_drug_dict.get('batch_id', None)
        current_pack_id = update_drug_dict['current_pack_id']
        user_id = update_drug_dict['user_id']
        company_id = update_drug_dict['company_id']
        alternate_drug = db_get_by_id(alt_drug_id, dicts=True)

        if batch_id is None:
            batch_id = get_batch_id_from_packs(all_pack_list=[int(current_pack_id)])

        analysis_to_update = get_packs_to_update_dao(old_drug_ids=old_drug_ids,
                                                                current_pack_id=current_pack_id)

        alt_drug_id = alternate_drug['id']
        logger.info("In update_alternate_drug_for_batch_manual_canister: alternate drug id: {}".format(alt_drug_id))

        if analysis_to_update:
            for record in analysis_to_update.dicts():
                pack_ids.append(record['pack_id'])
                analysis_ids.append(record['analysis_id'])
                slot_ids.append(record['slot_id'])

        logger.info("In update_alternate_drug_for_batch_manual_canister: pack_ids: {}, analysis_ids: {}, slot_ids: {}"
                    .format(pack_ids, analysis_ids, slot_ids))

        query = get_pack_drugs_by_pack_id_dao(current_pack_id=current_pack_id, old_drug_ids=old_drug_ids)
        for record in query.dicts():
            pack_list.append(record['pack_id'])
            if record['drug_id'] not in drug_list:
                drug_list.append(record['drug_id'])
                alt_drug_list.append(alt_drug_id)

        logger.info("In update_alternate_drug_for_batch_manual_canister: pack_list: {} drug_list: {}, alt_drug_list: {}"
                    .format(pack_list, drug_list, alt_drug_list))

        with db.transaction():
            update_dict = {'canister_id': None}

            if old_drug_ids:
                response = alternate_drug_update({'pack_list': ','.join(map(str, pack_list)),
                    'olddruglist': ','.join(map(str, old_drug_ids)),
                    'newdruglist': ','.join(map(str, [alt_drug_id])),
                    'user_id': user_id,
                    'company_id': company_id,
                    'module_id': constants.PDT_REPLENISH_ALTERNATES})

                response = json.loads(response)
                if response['status'] != 'success':
                    # throwing exception to rollback changes as we could not update IPS
                    # raise AlternateDrugUpdateException(response['code'])
                    return error(response['code'])
                    # todo handle the error
                if analysis_to_update:
                    status = update_pack_analysis_details_by_analysis_slot_id(update_dict=update_dict, analysis_ids=analysis_ids, slot_ids=slot_ids)
                    logger.info("Inside update_alternate_drug_for_batch_manual_canister, pack analysis updated {}".format(status))

                batch_change_tracker_status = save_batch_change_tracker_data(batch_id=batch_id,
                                                                             user_id=user_id,
                                                                             action_id=constants.ACTION_ID_MAP[constants.UPDATE_ALT_DRUG],
                                                                             params={"alt_drug_id": alt_drug_id,
                                                                                 "batch_id": batch_id,
                                                                                 "current_pack_id": current_pack_id,
                                                                                 "user_id": user_id,
                                                                                 "changed_from_mvs": True,
                                                                                "pack_count": len(pack_list)},
                                                                             packs_affected=pack_list)
                logger.info("Inside update_alternate_drug_for_batch_manual_canister,batch_change_tracker_status: {}".format(batch_change_tracker_status))

                return create_response(True)
            else:
                return create_response(False)


    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in update_alternate_drug_for_batch_manual_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_alternate_drug_for_batch_manual_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except PharmacySoftwareCommunicationException as e:
        logger.error("Error in update_alternate_drug_for_batch_manual_canister {}".format(e))
        return error(7001)
    except PharmacySoftwareResponseException as e:
        logger.error("Error in update_alternate_drug_for_batch_manual_canister {}".format(e))
        return error(7001)

    except Exception as e:
        logger.error("Error in update_alternate_drug_for_batch_manual_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_alternate_drug_for_batch_manual_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in update_alternate_drug_for_batch_manual_canister: " + str(e))


def get_manual_drug_manual_pack(drug_id: int):
    """
        function to get manual alternate drug of pack drug by drug id
        @param drug_id:
        @return:
    """
    results: list = list()
    try:
        query = get_manual_drug_manual_pack_dao(drug_id=drug_id)

        for record in query.dicts():
            results.append(record)
        return create_response(results)

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error("error in get_manual_drug_manual_pack {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_manual_drug_manual_pack: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        logger.error("Error in get_manual_drug_manual_pack {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_manual_drug_manual_pack: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in get_manual_drug_manual_pack: " + str(e))


def save_alternate_drug(data):
    """
       This function save alternates drugs
       :param data:
       :return:
    """
    batch_id = data['batch_id']
    alt_fndc_txr: dict = dict()
    try:
        with db.transaction():
            batch_data = get_batch_data(batch_id=batch_id)
            if batch_data.sequence_no == constants.PPP_SEQUENCE_IN_PROGRESS:
                return error(2000)
            else:
                previous_sequence = batch_data.sequence_no
                logger.info("In save_alternate_drug: previous sequence: {} for batch_id:{}".format(previous_sequence, batch_id))

                if previous_sequence != constants.PPP_SEQUENCE_PACK_DISTRIBUTION_BY_BATCH_DONE:
                    return error(1020, 'Already saved data.')

                # update sequence_no to PPP_SEQUENCE_IN_PROGRESS(1) in batch master
                seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=constants.PPP_SEQUENCE_IN_PROGRESS,
                                                                          batch_id=batch_id)
                logger.info("In save_alternate_drug: save_alternate_drug execution started: {} , changed sequence to {} for batch_id: {}"
                             .format(seq_status, constants.PPP_SEQUENCE_IN_PROGRESS, batch_id))
                if seq_status:
                    # update couch db timestamp for pack_pre_processing_wizard change
                    couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=data)
                    logger.info("In save_alternate_drug : time stamp update for pre processing wizard for in_progress API: {} and batch_id: {}".format(
                        couch_db_status, batch_id))

        with db.transaction():
            system_id = int(data['system_id'])
            system_list = data['system_id'].split(',')
            system_zone_mapping, zone_list = db_get_system_zone_mapping(system_list=system_list)
            zone_id = system_zone_mapping[system_id]
            company_id = data['company_id']
            user_id = data['user_id']

            if batch_data.status_id not in [settings.BATCH_PENDING,
                                            settings.BATCH_CANISTER_TRANSFER_RECOMMENDED]:
                seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                          batch_id=batch_id)
                if seq_status:
                    # update couch db timestamp for pack_pre_processing_wizard change
                    couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=data)
                    logger.info("In save_alternate_drug : Already saved data ,time stamp update for pre processing wizard: {} for batch_id: {}".format(
                        couch_db_status, batch_id))
                return error(1020, 'Already saved data.')


            query = get_save_alternate_drug(batch_id=batch_id, company_id=company_id)
            for record in query:
                alt_fndc_txr['{}#{}'.format(record['formatted_ndc'], record['txr'])] = \
                    '{}#{}'.format(record['alt_formatted_ndc'], record['txr'])

            logger.info('In save_alternate_drug: alt_fndc_txr: {} '.format(alt_fndc_txr))

            if alt_fndc_txr:
                update_status = update_pack_analysis(alt_fndc_txr=alt_fndc_txr,
                                                     batch_id=batch_id,
                                                     zone_id=zone_id,
                                                     company_id=company_id)
                logger.info('In save_alternate_drug: update_status: {} '.format(update_status))

            batch_status = set_batch_status_dao(batch_id=batch_id,
                                                status=settings.BATCH_ALTERNATE_DRUG_SAVED,
                                                user_id=user_id)
            logger.info('In save_alternate_drug: batch_status: {} '.format(batch_status))

            if batch_status:
                # update sequence_no to PPP_SEQUENCE_SAVE_ALTERNATES(it means save alternates api run successfully)
                seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=constants.PPP_SEQUENCE_SAVE_ALTERNATES,
                                                                          batch_id=batch_id)
                logger.info("In save_alternate_drug:save_alternate_drug run successfully: {} , changed sequence to {} for batch_id: {}"
                             .format(seq_status, constants.PPP_SEQUENCE_SAVE_ALTERNATES, batch_id))
                if seq_status:
                    # update couch db timestamp for pack_pre_processing_wizard change
                    couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=data)
                    logger.info("In save_alternate_drug : time stamp update for pre processing wizard: {} when save_alternates done for batch_id: {}".format(
                        couch_db_status, batch_id))
            else:
                seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                          batch_id=batch_id)
                logger.info("In save_alternate_drug: save_alternate_drug response fail for batch_id: {} , changed sequence to {}"
                             .format(batch_id, previous_sequence))
                if seq_status:
                    # update couch db timestamp for pack_pre_processing_wizard change
                    couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=data)
                    logger.info("In save_alternate_drug : time stamp update for pre processing wizard: {} when response is fail for batch_id: {}".format(
                        couch_db_status, batch_id))

            return create_response(batch_status)

    except (InternalError, IntegrityError) as e:
        seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                  batch_id=batch_id)
        if seq_status:
            # update couch db timestamp for pack_pre_processing_wizard change
            couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=data)
            logger.info("In save_alternate_drug : time stamp update for pre processing wizard: {} when exception occurs, changed sequence to: {} for batch_id: {}"
                .format(couch_db_status, previous_sequence, batch_id))
        logger.error("error in get_manual_drug_manual_pack {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in save_alternate_drug: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(2001)

    except Exception as e:
        seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=previous_sequence,
                                                                  batch_id=batch_id)
        if seq_status:
            # update couch db timestamp for pack_pre_processing_wizard change
            couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=data)
            logger.info("In save_alternate_drug : time stamp update for pre processing wizard: {} when exception occurs changed sequence to: {} for batch_id: {}"
                .format(couch_db_status, previous_sequence, batch_id))
        logger.error("Error in save_alternate_drug {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in save_alternate_drug: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        return error(1000, "Error in save_alternate_drug: " + str(e))


@log_args_and_response
def update_alternate_drug_by_module(company_id: int, user_id: int, batch_id: int, new_drug: str, old_drug: int, module: int, pack_ids: list = None):
    """
    Update Drug id in slot details for alternate drugs
    @param company_id:
    @param user_id:
    @param batch_id:
    @param new_drug:
    @param old_drug:
    @param module:
    @param pack_ids:
    @return: True or Packs Affected
    """
    try:
        if module == constants.PDT_MVS_MANUAL_FILL:

            data_dict = {
                'company_id': company_id,
                'alt_drug_id': new_drug,
                'drug_id': old_drug,
                'batch_id': batch_id,
                'current_pack_id': pack_ids,
                'user_id': user_id,
                'module': module
            }

            response = update_alternate_drug_for_batch_manual_canister(update_drug_dict=data_dict)
            response = json.loads(response)
            print(response)
            if response['status'] == "success":

                if not response['data']:
                    return False
                logger.info("Alternate Drug updated Successfully")
                return response

            if response['status'] == "failure":
                raise PharmacySoftwareResponseException

        elif module == constants.PDT_PACK_FILL_WORKFLOW:
            data_dict = {
                "olddruglist": str(old_drug),
                "newdruglist": str(new_drug),
                "company_id": company_id,
                "assigned_user_id": user_id,
                "user_id": user_id,
                "module": module

            }
            response = alternate_drug_update_manual_packs(data_dict)
            response = json.loads(response)
            if response['status'] == "success":
                logger.info("Alternate Drug updated Successfully")
                return response

            if response['status'] == "failure":
                raise PharmacySoftwareResponseException

        elif module == constants.PDT_MFD_ALTERNATE:
            old_ndc = get_drug_and_bottle_information_by_drug_id_dao(drug_id=old_drug)["ndc"]
            new_ndc = get_drug_and_bottle_information_by_drug_id_dao(drug_id=new_drug)["ndc"]
            data_dict = {
                "batch_id": str(batch_id),
                "old_ndc": str(old_ndc),
                "new_ndc": new_ndc,
                "user_id": user_id,
                "company_id": company_id

            }
            response = update_mfd_alternate_drug(data_dict)
            response = json.loads(response)
            if response['status'] == "success":
                logger.info("Alternate Drug updated Successfully")
                return response

            if response['status'] == "failure":
                raise PharmacySoftwareResponseException

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        raise e
    except PharmacySoftwareCommunicationException as e:
        logger.error(e, exc_info=True)
        raise e
    except PharmacySoftwareResponseException as e:
        logger.error(e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(e)
        raise e


@validate(required_fields=["olddruglist", "newdruglist", "company_id", "user_id"])
@log_args_and_response
def alternate_drug_update_manual_packs(dict_alternate_drug_info):
    """ Updates the alternate drug information for the packs assigned to user in
     manual packging flow and also sends the alternate drug information
    to the pharmacy software.

    Args:
        dict_alternate_drug_info (dict): The json dict containing
                                        company_id, olddruglist, newdruglist, user_id

    Returns:
        json response of success or failure

    Examples:
        >>> alternate_drug_update()
        None

    """

    company_id = dict_alternate_drug_info["company_id"]
    # user_id = dict_alternate_drug_info["user_id"]
    assigned_user_id = dict_alternate_drug_info.get("assigned_user_id", None)
    pack_ids = dict_alternate_drug_info.get("pack_ids", None)

    slot_details_updation: dict = dict()
    pack_drug_tracker_details: list = list()

    # ips_change_response: bool = False
    # partially_filled_rxs = PackRxLink.select(PartiallyFilledPack.pack_rx_id).dicts() \
    #     .join(PartiallyFilledPack, on=PartiallyFilledPack.pack_rx_id == PackRxLink.id) \
    #     .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
    #     .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id) \
    #     .where(PackUserMap.pack_id << pack_ids)

    pack_ids = get_manual_pack_ids(assigned_user_id, company_id, pack_ids)
    if not pack_ids:
        return error(1020, 'No packs found.')

    # make list which will be sent to IPS, this will be updated later by NDC.
    ips_drug_ids = deepcopy(dict_alternate_drug_info["olddruglist"].split(','))
    ips_alt_drug_ids = deepcopy(dict_alternate_drug_info["newdruglist"].split(','))

    original_drug_ids = deepcopy(dict_alternate_drug_info["olddruglist"].split(','))

    requestedOldDrugIds = dict_alternate_drug_info['olddruglist'].split(',')
    requestedNewDrugIds = dict_alternate_drug_info['newdruglist'].split(',')
    # pack_rx_ids = list(item['pack_rx_id'] for item in list(partially_filled_rxs))

    dict_alternate_drug_info['olddruglist'] = [item for item in dict_alternate_drug_info['olddruglist'].split(',') for i in range(len(pack_ids))]
    dict_alternate_drug_info['newdruglist'] = [item for item in dict_alternate_drug_info['newdruglist'].split(',') for i in range(len(pack_ids))]

    user_id = dict_alternate_drug_info["user_id"]
    drug_ids = dict_alternate_drug_info["olddruglist"]
    alt_drug_ids = dict_alternate_drug_info["newdruglist"]

    try:
        # convert to int, throw error if you can not convert to int
        ips_drug_ids = list(map(int, ips_drug_ids))
        ips_alt_drug_ids = list(map(int, ips_alt_drug_ids))
    except ValueError as e:
        logger.error(e, exc_info=True)
        return error(1020, "Element of old_drug_list and newdruglist must be integer.")

    valid_packlist = verify_pack_list_by_company_id(pack_list=pack_ids, company_id=company_id)
    if not valid_packlist:
        return error(1014)

    company_settings = get_company_setting_by_company_id(company_id=company_id)
    required_settings = settings.ALTERNATE_DRUG_SETTINGS
    settings_present = all([key in company_settings for key in required_settings])

    if not settings_present:
        return error(6001)

    packlist_len = len(pack_ids)
    drugs_ids_len = len(drug_ids)
    alt_drug_dict: dict = dict()

    # get the number of distinct alternate drugs
    _size = int(drugs_ids_len / packlist_len)
    new_pack_ids: list = list()  # only those pack ids which really have old drugs
    new_pack_display_ids: list = list()  # to return pack_display_ids for which drug updated
    try:
        with db.transaction():
            for i in range(0, _size):
                alt_drug_dict[int(drug_ids[i * packlist_len])] = int(alt_drug_ids[i * packlist_len])

            patient_rx_ids: dict = dict()
            pack_rx_link_original_drug_ids: dict = dict()
            pack_ids = list(set(pack_ids))
            # for handling daw drug update -- allowed for only daw 0
            # fetch only those patient_rx_ids where daw value is zero
            patient_rx_query = get_patient_rx_data(pack_ids)
            for record in patient_rx_query:
                try:
                    patient_rx_ids[record["patient_rx_id"]] = alt_drug_dict[record["drug_id"]]
                    if record["original_drug_id"] is None:  # If original_drug_id is null then store current drug id as original drug id in pack rx link
                        pack_rx_link_original_drug_ids[record["id"]] = record["drug_id"]
                    new_pack_ids.append(record["pack_id"])
                    new_pack_display_ids.append(record["pack_display_id"])
                except KeyError:
                    pass  # not really drug id for that given pack id so will throw key error

            if not new_pack_ids:  # if no pack has given old drug id return 0
                return error(14003)

            logger.info("Inside alternate_drug_update_manual_packs packs {}".format(pack_ids))

            slot_query = get_slot_data_by_pack_ids_drug_ids(original_drug_ids=original_drug_ids, pack_ids=pack_ids)

            for record in slot_query:
                slot_details_updation[record["id"]] = {"prev_drug_id": record["drug_id"],
                                                       "drug_id": alt_drug_dict[record["drug_id"]]}

                pack_drug_tracker_info = {"slot_details_id": record["id"],
                                          "previous_drug_id": record["drug_id"],
                                          "updated_drug_id": alt_drug_dict[record["drug_id"]],
                                          "module": constants.PDT_PACK_FILL_WORKFLOW,
                                          "created_by": user_id,
                                          "created_date": get_current_date_time()}

                pack_drug_tracker_details.append(pack_drug_tracker_info)

            ips_change_response = send_alternate_drug_change_data_to_ips(new_pack_ids=new_pack_ids,
                                                                         alt_drug_ids=alt_drug_ids,
                                                                         drug_ids=drug_ids,
                                                                         ips_drug_ids=ips_drug_ids,
                                                                         ips_alt_drug_ids=ips_alt_drug_ids,
                                                                         company_settings=company_settings,
                                                                         requestedOldDrugIds=requestedOldDrugIds,
                                                                         requestedNewDrugIds=requestedNewDrugIds,
                                                                         pack_ids=pack_ids,
                                                                         send_notification=True)
            if ips_change_response:

                for key, value in patient_rx_ids.items():
                    update_dict = {"drug_id": value,
                                   "modified_by": user_id,
                                   "modified_date": get_current_date_time()}
                    status1 = PatientRx.db_update_patient_rx_data(update_dict=update_dict, patient_rx_id=key)
                    logger.info("In alternate_drug_update_manual_packs: Updating alternate drugs with values for patient_rx_ids"
                                 ": " + str(key) + "," + str(value) + ":" + str(status1))

                for key, value in pack_rx_link_original_drug_ids.items():
                    update_dict = {"original_drug_id": value}
                    status2 = update_pack_rx_link_dao(update_dict=update_dict, pack_rx_link_id=[key])
                    logger.debug("In alternate_drug_update_manual_packs: Updating PackRxLink alternate drugs with values for pack_rx_link_original_drug_ids"
                                 ": " + str(key) + "," + str(value) + ":" + str(status2))

                for slot_details_id, slot_drugs in slot_details_updation.items():
                    drug_id = slot_drugs["drug_id"]
                    prev_drug_id = slot_drugs["prev_drug_id"]

                    update_dict = {"drug_id": drug_id}
                    slot_details_update_status = update_slot_details_by_slot_id_dao(update_dict=update_dict,
                                                                                    slot_details_id=slot_details_id)


                    logger.debug(f"In alternate_drug_update_manual_packs: Updating SlotDetails drugs with values, id: {slot_details_id}, prev_drug_id: {prev_drug_id}, "
                        f"updated_drug_id: {drug_id} with status: {slot_details_update_status}")

                create_records_in_pack_drug_tracker(pack_drug_tracker_details=pack_drug_tracker_details)

            else:
                return error(7001)

        return create_response({"updated_pack_display_ids": new_pack_display_ids})

    except (InternalError, DataError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001, e)
    except PharmacySoftwareCommunicationException as e:
        logger.error(e, exc_info=True)
        return error(7001)
    except PharmacySoftwareResponseException as e:
        logger.error(e, exc_info=True)
        return error(7001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Error in alternate_drug_update_manual_packs: " + str(e))
