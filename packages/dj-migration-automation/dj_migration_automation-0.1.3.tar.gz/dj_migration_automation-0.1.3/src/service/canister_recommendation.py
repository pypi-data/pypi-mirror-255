import json
import math
import os
import sys
from collections import defaultdict, OrderedDict
from copy import deepcopy
from itertools import chain

import pandas as pd
from peewee import IntegrityError, InternalError, DataError, DoesNotExist

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response, get_current_date_time
from dosepack.validation.validate import validate
from src import constants
from src.dao.alternate_drug_dao import insert_data_in_replenish_skipped_canister
from src.dao.analysis_dao import set_initial_pack_sequence
from src.dao.crm_dao import get_manual_packs_having_status_skipp_due_to_manual, get_manual_packs_by_batch_id, \
    db_add_batch_manual_packs_dao, db_get_create_manual_packs_dao
from src.dao.pack_analysis_dao import db_update_analysis_data, db_get_analysis_data, db_get_canister_data, \
    update_canister_location_v2, db_pack_analysis_update_manual_packs, \
    db_pack_analysis_update_manual_canister_location_v2, get_pack_wise_skipped_drug
from src.dao.patient_dao import get_next_schedules
from src.dao.reserve_canister_dao import reserve_canister
from src.dao.rph_verification_dao import db_verify_packlist_by_system
from src.optimised_drops_v3 import RecommendDrops
# from src.service.analysis import update_analysis_data
from src.dao.batch_dao import get_progress_batch_id, db_batch_import_status, db_update_batch_status, \
    update_scheduled_start_date_for_next_batches
from src.dao.canister_dao import db_delete_by_batch_dao, db_skipped_canisters_insert_many_dao, \
    get_canister_status_history_data, get_skip_canister_dao, get_canister_drug_quadrant, \
    get_empty_locations_count_quadwise, \
    delete_reserved_canister_for_skipped_canister, db_get_canister_by_company_id, get_canister_data_by_canister_ids
from src.dao.canister_transfers_dao import db_get_pending_transfers, db_get_remove_canister_list, \
    canister_transfer_get_or_create_data, get_canister_destination
from src.dao.pack_distribution_dao import db_get_empty_locations, get_pack_drug_slot_details, \
    get_packs_to_be_filled_by_canister, get_multi_canister_drug_data_by_canister, db_get_canister_reverted_packs, \
    db_get_affected_pack_list, get_affected_pack_list_for_canisters
from src.dao.device_manager_dao import get_mfd_locations_for_devices, get_max_locations_of_a_container, \
    get_csr_data_company_id_dao, get_max_locations_of_a_device, get_disabled_locations_of_devices, \
    get_robots_by_system_id_dao, get_canister_drug_with_location_for_given_drugs, db_get_robots_by_systems_dao, \
    get_nx_canister_drug_with_location_for_given_drugs
from src.dao.guided_replenish_dao import check_pending_guided_canister_transfer
from src.dao.mfd_dao import db_get_mfd_drop_number, update_drop_number_in_mfd_analysis_details, db_get_batch_mfd_packs, \
    get_pending_mfd_pack_list_dao
from src.dao.misc_dao import update_sequence_no_for_pre_processing_wizard
from src.dao.pack_analysis_dao import get_device_id_from_pack_list, db_save_analysis, \
    get_reserved_location_no_by_batch_and_device
from src.dao.pack_dao import db_get_pack_ids_dao, get_pack_slotwise_canister_drugs_, get_empty_location_by_quadrant, \
    get_pack_ids_by_batch_id, get_each_pack_delivery_date, get_quadrant_and_device_from_location_number_dao
from src.dao.pack_distribution_dao import db_get_empty_locations, get_pack_drug_slot_details
from src.dao.reserve_canister_dao import reserve_canister
from src.optimised_drops_v3 import RecommendDrops
# from src.service.canister_transfers import get_pending_cycle_data_based_on_status
from src.service.misc import update_timestamp_couch_db_pre_processing_wizard
logger = settings.logger


@log_args_and_response
@validate(required_fields=["canister_ids", "user_id", "batch_id"])
def add_skipped_canister(skipped_canister):
    """
    Creates entry for skipped canisters.
    @param skipped_canister:
    @return:
    """
    try:
        skipped_canister_list = list()
        batch_id = skipped_canister["batch_id"]
        user_id = skipped_canister["user_id"]
        for item in skipped_canister['canister_ids']:
            skipped_canister_list.append({
                'batch_id': batch_id,
                'created_by': user_id,
                'canister_id': item,
                'skipped_from': constants.SKIPPED_FROM_PACK_PRE_PROCESSING
            })
        with db.transaction():
            db_delete_by_batch_dao(batch_id=batch_id)

            if skipped_canister_list:
                db_skipped_canisters_insert_many_dao(skipped_canister_list)
                delete_reserved_canister_for_skipped_canister(canister_list=skipped_canister['canister_ids'], batch_id=[batch_id])
        return create_response(True)
    except (IntegrityError, InternalError) as e:
        logger.error("error in add_skipped_canister {}".format(e))
        return error(2001)
    except (DataError, Exception) as e:
        logger.error("error in add_skipped_canister {}".format(e))
        return error(1020)


@log_args_and_response
def flow_handler(system_id, rc_flag, user_id, company_id, batch_id=None, re_run=False, idle_robot_ids=None,
                 include_skipped=False, version_type='c'):
    """
    Handles which algorithm needs to be called for given recommendation flag
    @param system_id:
    @param rc_flag:
    @param user_id:
    @param company_id:
    @param batch_id:
    @param re_run: whether to re-run recommend canister
    @param idle_robot_ids: transfer data will be filtered for that robot ids
                    (Useful in parallel replenish scenario)
    @param include_skipped:  flag to indicate if skipped canister list is required or not
    @param version_type:
    @return:
    """
    try:
        # check for any batch in progress, if any batch is in progress in current system then return error
        progress_batch_id = get_progress_batch_id(system_id=system_id)
        # if progress_batch_id:
        #     return error(14006)

        # check if guided flow is pending or not
        logger.info("IN flow_handler: checking for pending guided canister cycle")
        pending_guided_cycles = check_pending_guided_canister_transfer(system_id=system_id)
        logger.info(
            "IN flow_handler: Pending guided canister cycles - " + str(pending_guided_cycles))

        if pending_guided_cycles:
            return error(14005)
            # if there are pending guided cycles get batch_id and system_id for the same
            # status, response, pending_batch_id, pending_system_id = get_pending_cycle_data_based_on_status(
            #     pending_guided_cycles=pending_guided_cycles, company_id=company_id, system_id=system_id)
            #
            # if status:
            #     logger.info("IN flow_handler: Successfully updated pending guided cycle data")
            #     if pending_batch_id and pending_system_id:
            #         logger.info("In flow_handler: Need to complete pending guided flow")
            #         return error(14005, "{},{}".format(pending_batch_id, pending_system_id))
            # else:
            #     logger.info("IN flow_handler: Error in updating guided cycle status")
            #     return response

        recommendation_flags = ('transfer',)  # allowed flags
        # is_imported = db_is_imported(batch_id)
        is_imported = db_batch_import_status(batch_id=batch_id)
        if is_imported is None or is_imported:
            return error(1020)

        if idle_robot_ids:
            idle_robot_ids = list(map(int, idle_robot_ids.split(',')))
        if rc_flag not in recommendation_flags:  # Invalid Flag
            return error(1020)

        # pack_list = PackDetails.db_get_pack_ids(batch_id, system_id)
        pack_list = db_get_pack_ids_dao(batch_id=batch_id, system_id=system_id)
        logger.info('Pack list for recommend canister {} - {}'.format(len(pack_list), pack_list))
        logger.info('Re Run Algo : {}'.format(re_run))

        robots_data, robot_capacity = robot_location_data(system_id)
        csr_data, csr_capacity = csr_location_data(company_id)

        if rc_flag == 'transfer':
            robot_ids = {item['id']: item['max_canisters'] for item in robots_data}
            csr_ids = {item['id']: item['max_canisters'] for item in csr_data}
            device_ids = dict()
            device_ids.update(robot_ids)
            device_ids.update(csr_ids)
            print(device_ids)
            empty_locations = db_get_empty_locations(device_ids=device_ids)

            # removing mfd_locations from empty_locations
            mfd_locations = get_mfd_locations_for_devices(device_ids=robot_ids)
            for k, v in mfd_locations.items():
                empty_locations[k] -= mfd_locations[k]
            replenish_data = update_analysis_data({
                'batch_id': batch_id,
                'system_id': system_id,
                'company_id': company_id,
                'user_id': user_id,
                'get_replenish': True,
                'update_batch_status': False,
                'idle_robot_ids': idle_robot_ids,
                'transfer_info_required': False
            })
            json_replenish_data = json.loads(replenish_data)
            if json_replenish_data['status'] == 'success':
                # replenish_canister_ids = set(json_replenish_data['data']['replenish_canister_ids'])
                # replenish_canister_data = json_replenish_data['data']['replenish_data']
                required_replenish_quantity = json_replenish_data['data']['required_replenish_quantity']
            else:
                # TODO Return???
                return error(1000, 'Could not get replenish data', json_replenish_data['description'])

            response, remove_locations, deleted_canister, csr_remove_locations = get_pending_transfers(
                batch_id, system_id, required_replenish_quantity, version_type
            )
            pending_transfer_count = len(response)
            response = transfer_for_idle_robots(response, idle_robot_ids)
            response = sorted(response, key=lambda each_drug: each_drug['drug_name'])
            empty_locations_data = list()
            for item in robots_data:
                empty_locations_data.append({
                    'device_id': item['id'],
                    'device_name': item['name'],
                    'empty_locations': list(empty_locations[item['id']]),
                    'remove_locations': remove_locations[item['id']]
                })
            # for item in csr_data:
            #     empty_locations_data.append({
            #         'device_id': item['id'],
            #         'device_name': item['name'],
            #         'empty_locations': list(empty_locations[item['id']]),
            #         'remove_locations': remove_locations[item['id']]
            #     })
            res = {
                'transfers': response,
                'batch_id': batch_id,
                'empty_locations': empty_locations_data,
                'deleted_canister': deleted_canister,
                'pending_transfer_count': pending_transfer_count,
                'csr_remove_locations': csr_remove_locations,
                'csr_data': csr_data
            }
        if include_skipped:
            res["skipped_canister"] = get_skip_canister_dao(batch_id=batch_id)
        logger.info("Response for canister recommendation {}".format(res))

        if not res["transfers"]:
            # update sequence_no to PPP_SEQUENCE_CANISTER_RECOMMENDATION_DONE
            # (it means PPP_SEQUENCE_CANISTER_RECOMMENDATION_DONE  api run successfully)
            seq_status = update_sequence_no_for_pre_processing_wizard(sequence_no=constants.
                                                                      PPP_SEQUENCE_CANISTER_RECOMMENDATION_DONE,
                                                                      batch_id=batch_id)
            logger.info("In flow_handler: flow_handler run successfully with no transfers: {}, "
                        "change sequence to {} for batch_id: {}".format(seq_status, constants.
                                                                        PPP_SEQUENCE_CANISTER_RECOMMENDATION_DONE,
                                                                        batch_id))

            batch_info = {"system_id": system_id}
            if seq_status:
                # update couch db timestamp for pack_pre processing wizard change
                couch_db_status = update_timestamp_couch_db_pre_processing_wizard(args=batch_info)
                logger.info("In flow_handler: time stamp update for pre processing wizard: {} for "
                            "batch_id: {}".format(couch_db_status, batch_id))
        return create_response(res)

    except (IntegrityError, InternalError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in flow_handler {}".format(e))
        return error(2001)


@log_args_and_response
def transfer_for_idle_robots(transfers, robot_id_list):
    """
    Returns transfers list for idle robot
    @param transfers: list of all canister transfers
    @param robot_id_list: Idle robot ids list
    @return:
    """
    try:
        if not robot_id_list:  # If no robot id is specified return all data
            return transfers

        # list of robot ids from which canister can be moved
        # None represents On Shelf canister
        transferable_robot_ids = [None] + robot_id_list
        filtered_list = list()
        for item in transfers:

            # if canister need to move out of given robot OR
            # canister is on shelf and need to put in given robot id OR
            # canister transfer between given robot ids OR
            # canister to be put in trolley
            if item["source_device_id"] in transferable_robot_ids:
                if item["dest_device_id"] not in transferable_robot_ids:
                    item["is_in_trolly"] = True
                else:
                    item["is_in_trolly"] = False
                filtered_list.append(item)
        return filtered_list
    except Exception as e:
        logger.error("error in transfer_for_idle_robots {}".format(e))
        raise


@log_args_and_response
def get_pending_transfers(batch_id, system_id, required_replenish_quantity, version_type):
    """
    Returns
    - list of canisters which are not placed in recommended robots
    - Free locations
    - Canister Deleted

    @param batch_id:
    @param system_id:
    @param required_replenish_quantity:
    @param version_type:
    @return:
    """
    pending_transfers = list()
    remove_locations = defaultdict(list)
    csr_remove_locations = defaultdict(lambda: defaultdict(list))
    deleted = False

    try:
        for record in chain(db_get_pending_transfers(batch_id),
                            db_get_remove_canister_list(batch_id, system_id)):
            if "container_id" in record and record["container_id"] is not None:
                record['drawer_max_canisters'] = get_max_locations_of_a_container(container_id=record['container_id'])
            canister_id = str(record['id'])
            replenish_data_available = required_replenish_quantity.get(canister_id, False)
            if replenish_data_available:
                record['required_qty'] = required_replenish_quantity[canister_id]['required_qty']
                record['replenish_qty'] = required_replenish_quantity[canister_id]['required_qty'] -\
                                          required_replenish_quantity[canister_id]['available_qty']
                record['replenish_qty'] = record['replenish_qty'] if record['replenish_qty'] > 0 else 0
            else:
                record['required_qty'] = 0
                record['replenish_qty'] = 0

            if record['transfer_status'] in [constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_AT_PPP,
                                             constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                                             constants.CANISTER_TX_TO_ROBOT_SKIPPED_AND_ALTERNATE]\
                    or not record['canister_transfer_id']:
                continue

            if record['transfer_status'] in [constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                                             constants.CANISTER_TX_TO_ROBOT_SKIPPED,
                                             constants.CANISTER_TX_TO_TROLLEY_ALTERNATE_TRANSFER_LATER,
                                             constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_LATER]\
                    and record['dest_device_type_id'] == settings.DEVICE_TYPES['ROBOT']:
                record['enable_actions'] = True
            else:
                record['enable_actions'] = False

            replenish_required = True if record['replenish_qty'] > 0 else False
            record['replenish_required'] = replenish_required
            # if replenish_required:
            #     print(replenish_canister_data)
            #     for rep_can_record in replenish_canister_data:
            #         if rep_can_record['canister_id'] == record['id']:
            #             record['replenish_qty'] = rep_can_record['replenish_qty']
            #             record['required_qty'] = rep_can_record['required_qty']
            # else:
            #     record['replenish_qty'] = None
            if version_type in settings.V3 and (record['source_device_id'] == record['dest_device_id']) \
                    and (record['source_quadrant'] == record['dest_quadrant']):
                continue  # canister at required location and replenish not required, so skip it.
            if version_type not in settings.V3 and (record['source_device_id'] == record['dest_device_id']) and \
                    not replenish_required and (record['source_quadrant'] == record['dest_quadrant']):
                continue  # canister at required location and replenish not required, so skip it.
            if record['dest_device_id'] is None:
                remove_locations[record['source_device_id']].append(record['display_location'])

            if record['active'] != settings.is_canister_active:
                deleted = True
                canister_status_dict = get_canister_status_history_data(canister_list=[canister_id],
                                                                        status=constants.CODE_MASTER_CANISTER_DEACTIVATE)
                try:
                    record['deactive_comment'] = canister_status_dict[canister_id]["comment"]
                except KeyError:
                    record['deactive_comment'] = None
            else:
                record['deactive_comment'] = None

            if record['source_device_type_id'] == settings.DEVICE_TYPES['CSR']:
                csr_remove_locations[record['source_device_name']][record['source_drawer_name']].append(
                    record['display_location'])
            if record["expiry_date"]:
                record["expiry_date"] = record["expiry_date"].strftime("%Y-%m")
            pending_transfers.append(record)

        print(csr_remove_locations)
        logger.info('Data for Pending Transfer: {}'.format(pending_transfers))
        logger.info('Data for Remove Location: {}'.format(remove_locations))

        return pending_transfers, remove_locations, deleted, csr_remove_locations
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error("error in get_pending_transfers {}".format(e))
        raise


@log_args_and_response
def transfer_canister_recommendation(cr_res, canister_data, robot_dict):
    """
    Returns list of recommendations for canister transfers
    @param cr_res: {canister id: (source_robot_id, dest_robot_id) }
    @param canister_data: {canister_id: {...}}
    @param robot_dict:
    @return:
    """
    robot_dict.setdefault(None, {})
    robot_dict[None]["name"] = None
    recommendations = list()  # stores recommended canister destination
    pending_transfers = list()
    remove_locations = defaultdict(list)
    for canister_id, robots in cr_res.items():
        canister = canister_data[canister_id]
        canister["dest_device_id"] = robots[1]
        canister["source_device_id"] = robots[0]
        canister["dest_device_name"] = robot_dict[robots[1]]["name"]
        canister["source_device_name"] = robot_dict[robots[0]]["name"]
        if robots[1] != robots[0]:
            # dest robot is not same as source robot, transfer action pending
            pending_transfers.append(canister)
        recommendations.append(canister)
        if robots[1] is None:
            remove_locations[robots[0]].append(canister['location_number'])
    logger.info("recommendations: {}".format(recommendations))
    logger.info("remove_locations: {}".format(remove_locations))
    logger.info("pending_transfers: {}".format(pending_transfers))
    return recommendations, remove_locations, pending_transfers


@log_args_and_response
def create_dataset(pack_set, drug_ids_set, pack_mapping):
    """ Takes the drug id and the pack id list and creates a dataframe for drug and pack mapping.

    Args:
        pack_set (set): The distinct set of the pack ids
        drug_ids_set (set): The distinct set of the drug ids
        pack_mapping (dict): The dict containing the mapping of pack ids and the drug ids

    Returns:
        pandas.dataframe

    Examples:
        >>> create_dataset([])
        pandas.DataFrame, []
    """
    df = pd.DataFrame(index=pack_set, columns=drug_ids_set)

    for key, value in pack_mapping.items():
        for item in value:
            df.ix[key][item] = value[item]
    df = df.fillna(0)

    return df, df.columns.tolist()


@log_args_and_response
def csr_location_data(company_id):
    csr_ids = list()
    try:
        csr_data = get_csr_data_company_id_dao(company_id=company_id)
        for csr in csr_data:
            csr["max_canisters"] = get_max_locations_of_a_device(csr["id"])
            csr_ids.append(csr["id"])

        disabled_locations = defaultdict(set)
        for record in get_disabled_locations_of_devices(device_ids=csr_ids):
            disabled_locations[record["device_id"]].add(record["location_number"])
        csr_capacity = {x["id"]: x["max_canisters"] - len(disabled_locations[x["id"]]) for x in csr_data}

        return csr_data, csr_capacity
    except (DoesNotExist, IntegrityError, InternalError, DataError, Exception) as e:
        logger.error("error in csr_location_data {}".format(e))
        raise e


@log_args_and_response
def robot_location_data(system_id):
    robot_ids = list()
    try:
        robots_data = get_robots_by_system_id_dao(system_id)
        for robot in robots_data:
            robot["max_canisters"] = get_max_locations_of_a_device(robot["id"])
            robot_ids.append(robot["id"])
        disabled_locations = defaultdict(set)
        for record in get_disabled_locations_of_devices(device_ids=robot_ids):
            disabled_locations[record["device_id"]].add(record["location_number"])
        robot_capacity = {x["id"]: x["max_canisters"] - len(disabled_locations[x["id"]]) for x in robots_data}

        return robots_data, robot_capacity
    except (IntegrityError, InternalError, DataError, DoesNotExist, Exception) as e:
        logger.error("error in robot_location_data {}".format(e))
        raise e


@log_args_and_response
def get_canister_sorted_on_source_location(canister_list, source_location_dict):
    """

    @param canister_list:
    @param source_location_dict:
    @return:
    """
    sorted_can_dict = OrderedDict()

    for can in canister_list:
        if source_location_dict[can] not in sorted_can_dict.keys():
            sorted_can_dict[source_location_dict[can]] = list()
        sorted_can_dict[source_location_dict[can]].append(can)
    ordered_can_dict = sorted(sorted_can_dict, key=lambda key: len(sorted_can_dict[key]), reverse=True)
    sorted_can_list = [item for sublist in ordered_can_dict for item in sorted_can_dict[sublist]]
    return sorted_can_list


@log_args_and_response
def get_canister_transfer_data_to_update(trolley_data_dict):
    """
    Function will assign device(trolley) location to each canister.

    @param trolley_data_dict: {"trolley_list": list of trolley required for transfers,
                            "unavailable_trolley_dict": dict having device type id as key and count of unavailable trolley,
                            "device_quad_drawer_dict": device_quad_drawer_dict
                            }
    @return response: {"canister_transfer_data_dict": {canister_id: (trolley_loc_id, device, quad, drawer_level)},
                    "remaining_trolley_locations": empty device(trolley) locations,
                    "pending_transfers": count of canister to which device(trolley) location is not allocated,
                    "transfer_count": count of transfers}
    """

    logger.info("Input args for get_canister_transfer_data_to_update {}".format(trolley_data_dict))
    cycle_id = trolley_data_dict.get('cycle_id', 1)
    cycle_device_dict = trolley_data_dict.get('cycle_device_dict', dict())
    canister_cycle_id_dict = trolley_data_dict.get('canister_cycle_id_dict', dict())
    trolley_locations = deepcopy(trolley_data_dict['trolley_locations'])
    canister_transfer_dest_loc_dict = trolley_data_dict['canister_transfer_dest_loc_dict']
    canister_transfer_source_loc_dict = trolley_data_dict['canister_transfer_source_loc_dict']
    canister_transfer_data_dict = trolley_data_dict.get('canister_transfer_data_dict', dict())

    pending_canister_transfer_dest_loc_dict = dict()
    on_shelf_canisters = list()
    lift_trolley_drawers = list()
    regular_trolley_drawers = list()

    if settings.DEVICE_TYPES['Canister Cart w/ Elevator'] in trolley_locations.keys():
        lift_trolley_drawers = [drawer_id for drawer_id in
                                trolley_locations[settings.DEVICE_TYPES['Canister Cart w/ Elevator']].keys()]

    if settings.DEVICE_TYPES['Canister Transfer Cart'] in trolley_locations.keys():
        regular_trolley_drawers = [drawer_id for drawer_id in
                                   trolley_locations[settings.DEVICE_TYPES['Canister Transfer Cart']].keys()]

    try:
        if cycle_id not in cycle_device_dict.keys():
            cycle_device_dict[cycle_id] = list()
        for device, drawer_quad in canister_transfer_dest_loc_dict.items():
            for drawer_level, quad_canister in drawer_quad.items():
                if drawer_level == 2 or len(regular_trolley_drawers) == 0:
                    device_type_id = settings.DEVICE_TYPES['Canister Cart w/ Elevator']
                    can_per_drawer = settings.ELEVATOR_TROLLEY_CANISTER_PER_DRAWER
                    for quad, can_list in quad_canister.items():
                        can_list = get_canister_sorted_on_source_location(can_list, canister_transfer_source_loc_dict)
                        drawer_required = math.ceil(len(can_list)/can_per_drawer)
                        trolley_loc_list = list()
                        if len(lift_trolley_drawers) > 0:
                            for i in range(0, drawer_required):
                                if len(lift_trolley_drawers):
                                    drawer = lift_trolley_drawers.pop(0)
                                    trolley_loc_list.extend(trolley_locations[device_type_id][drawer])

                            for canister in can_list:
                                if device and quad is None:
                                    on_shelf_canisters.append(canister)

                                if len(trolley_loc_list):
                                    source_device, level, quadrant = canister_transfer_source_loc_dict[canister]
                                    if source_device and source_device not in cycle_device_dict[cycle_id]:
                                        cycle_device_dict[cycle_id].append(source_device)
                                    trolley_loc_id = trolley_loc_list.pop(0)
                                    canister_cycle_id_dict[canister] = cycle_id
                                    canister_transfer_data_dict[canister] = (trolley_loc_id, device, quad, drawer_level, source_device)
                                    if device not in cycle_device_dict[cycle_id]:
                                        cycle_device_dict[cycle_id].append(device)

                                else:
                                    if device not in pending_canister_transfer_dest_loc_dict.keys():
                                        pending_canister_transfer_dest_loc_dict[device] = dict()
                                    if drawer_level not in pending_canister_transfer_dest_loc_dict[device].keys():
                                        pending_canister_transfer_dest_loc_dict[device][drawer_level] = dict()
                                    if quad not in pending_canister_transfer_dest_loc_dict[device][drawer_level].keys():
                                        pending_canister_transfer_dest_loc_dict[device][drawer_level][quad] = list()
                                    pending_canister_transfer_dest_loc_dict[device][drawer_level][quad].append(canister)

                        else:
                            if device not in pending_canister_transfer_dest_loc_dict.keys():
                                pending_canister_transfer_dest_loc_dict[device] = dict()
                            if drawer_level not in pending_canister_transfer_dest_loc_dict[device].keys():
                                pending_canister_transfer_dest_loc_dict[device][drawer_level] = dict()
                            if quad not in pending_canister_transfer_dest_loc_dict[device][drawer_level].keys():
                                pending_canister_transfer_dest_loc_dict[device][drawer_level][quad] = list()
                            pending_canister_transfer_dest_loc_dict[device][drawer_level][quad].extend(can_list)

                else:
                    device_type_id = settings.DEVICE_TYPES['Canister Transfer Cart']
                    can_per_drawer = settings.TROLLEY_CANISTER_PER_DRAWER
                    for quad, can_list in quad_canister.items():
                        can_list = get_canister_sorted_on_source_location(can_list, canister_transfer_source_loc_dict)
                        drawer_required = math.ceil(len(can_list) / can_per_drawer)
                        trolley_loc_list = list()
                        if len(regular_trolley_drawers) > 0:
                            for i in range(0, drawer_required):
                                if len(regular_trolley_drawers):
                                    drawer = regular_trolley_drawers.pop(0)
                                    trolley_loc_list.extend(trolley_locations[device_type_id][drawer])

                            for canister in can_list:
                                if device and quad is None:
                                    on_shelf_canisters.append(canister)

                                if len(trolley_loc_list):
                                    source_device, level, quadrant = canister_transfer_source_loc_dict[canister]
                                    if source_device and source_device not in cycle_device_dict[cycle_id]:
                                        cycle_device_dict[cycle_id].append(source_device)
                                    trolley_loc_id = trolley_loc_list.pop(0)
                                    canister_cycle_id_dict[canister] = cycle_id
                                    canister_transfer_data_dict[canister] = (trolley_loc_id, device, quad, drawer_level, source_device)
                                    if device not in cycle_device_dict[cycle_id]:
                                        cycle_device_dict[cycle_id].append(device)

                                else:
                                    if device not in pending_canister_transfer_dest_loc_dict.keys():
                                        pending_canister_transfer_dest_loc_dict[device] = dict()
                                    if drawer_level not in pending_canister_transfer_dest_loc_dict[device].keys():
                                        pending_canister_transfer_dest_loc_dict[device][drawer_level] = dict()
                                    if quad not in pending_canister_transfer_dest_loc_dict[device][drawer_level].keys():
                                        pending_canister_transfer_dest_loc_dict[device][drawer_level][quad] = list()
                                    pending_canister_transfer_dest_loc_dict[device][drawer_level][quad].append(canister)

                        else:
                            if device not in pending_canister_transfer_dest_loc_dict.keys():
                                pending_canister_transfer_dest_loc_dict[device] = dict()
                            if drawer_level not in pending_canister_transfer_dest_loc_dict[device].keys():
                                pending_canister_transfer_dest_loc_dict[device][drawer_level] = dict()
                            if quad not in pending_canister_transfer_dest_loc_dict[device][drawer_level].keys():
                                pending_canister_transfer_dest_loc_dict[device][drawer_level][quad] = list()
                            pending_canister_transfer_dest_loc_dict[device][drawer_level][quad].extend(can_list)

        if len(pending_canister_transfer_dest_loc_dict):
            # recursive call of same function
            cycle_id += 1
            trolley_data_dict['cycle_id'] = cycle_id
            trolley_data_dict['cycle_device_dict'] = cycle_device_dict
            trolley_data_dict['canister_transfer_dest_loc_dict'] = pending_canister_transfer_dest_loc_dict
            trolley_data_dict['canister_transfer_data_dict'] = canister_transfer_data_dict
            trolley_data_dict['canister_cycle_id_dict'] = canister_cycle_id_dict
            get_canister_transfer_data_to_update(trolley_data_dict)

        response = {"canister_transfer_data_dict": canister_transfer_data_dict,
                    "remaining_trolley_locations": trolley_locations,
                    "transfer_count": len(canister_transfer_data_dict),
                    "canister_cycle_id_dict": canister_cycle_id_dict,
                    "cycle_device_dict": cycle_device_dict
                    }

        return True, response

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_canister_transfer_data_to_update {}".format(e))
        return False, e

    except Exception as e:
        logger.error("error in get_canister_transfer_data_to_update {}".format(e))
        return False, e


@log_args_and_response
def execute_recommendation_for_new_pack_after_change_rx(new_pack_list: list, old_pack_list: list, company_id: int,
                                                        batch_id: int):
    """

    @return:
    """
    try:
        unique_matrix_list = list()
        unique_matrix_data_list = list()
        pack_canister_slot_drug_dict_updated = dict()
        pack_max_auto_drop = {}
        temp_reserved_loc = list()

        old_packs_devices = get_device_id_from_pack_list(pack_list=old_pack_list)
        device_id = int(old_packs_devices.pop())

        pack_all_slot_drug_dict,pack_canister_slot_drug_dict, drugs_set,pack_manual_drugs_set = get_pack_slotwise_canister_drugs_(
            pack_list=new_pack_list, company_id=company_id)

        if drugs_set:
            pack_drug_slot_number_slot_id_dict = get_pack_drug_slot_details(new_pack_list)

            robot_quadrant_drug_data, remaining_drug_canister_location_dict, robot_quadrant_drug_canister_info_dict, \
            canister_location_number, canister_drugs_set = get_canister_drug_with_location_for_given_drugs(
                drug_list=list(drugs_set), device_id=device_id, batch_id=batch_id, pack_list=old_pack_list)

            if len(remaining_drug_canister_location_dict):
                empty_loc_device = get_empty_locations_count_quadwise(device_ids=[device_id])
                quad_empty_locations = empty_loc_device.get(device_id, dict())

                for drug in remaining_drug_canister_location_dict:
                    new_quad = None
                    canister = remaining_drug_canister_location_dict[drug][0]["canister_id"]
                    canister_type = remaining_drug_canister_location_dict[drug][0]["canister_type"]

                    for quad in quad_empty_locations.keys():
                        new_quad = quad
                        robot_quadrant_drug_data[device_id][new_quad]["drugs"].add(drug)
                        robot_quadrant_drug_canister_info_dict[device_id][new_quad][drug]= [canister]
                        canister_drugs_set.add(drug)
                        break
                    if new_quad is None:
                        new_quad = 1
                        robot_quadrant_drug_data[device_id][new_quad]["drugs"].add(drug)
                        robot_quadrant_drug_canister_info_dict[device_id][new_quad][drug] =[canister]
                        canister_drugs_set.add(drug)

                    if canister not in canister_location_number:
                        exclude_location = get_reserved_location_no_by_batch_and_device(batch_id=batch_id,
                                                                                        device_id=device_id)
                        empty_location_data = get_empty_location_by_quadrant(
                            device_id, new_quad, company_id,
                            drawer_type= [canister_type], exclude_location=exclude_location + temp_reserved_loc)
                        logger.debug('empty_location_data for canister_id {}: {}: {}'.format(canister,device_id,
                                                                                          empty_location_data))

                        if not empty_location_data and canister_type == settings.CANISTER_TYPE["SMALL"]:
                            empty_location_data = get_empty_location_by_quadrant(
                                device_id, new_quad, company_id,
                                drawer_type=[settings.CANISTER_TYPE["BIG"]], exclude_location=exclude_location + temp_reserved_loc)
                            logger.debug('empty_location_data for canister_id {}: {}: {}'.format(canister,device_id,
                                                                                              empty_location_data))

                        canister_location_number[canister] = empty_location_data.get('location_number', None)
                        if empty_location_data.get('location_id', None):
                            temp_reserved_loc.append(empty_location_data['location_id'])

            for pack, slot_drug_dict in pack_canister_slot_drug_dict.items():
                pack_canister_slot_drug_dict_updated[pack] = dict()
                for slot, drug_set in slot_drug_dict.items():
                    pack_canister_slot_drug_dict_updated[pack][slot] = set()
                    for drug in drug_set:
                        if drug in canister_drugs_set:
                            pack_canister_slot_drug_dict_updated[pack][slot].add(drug)

            distribution_response = {"quadrant_drugs": robot_quadrant_drug_data[device_id],
                                     "pack_slot_drug_dict": pack_canister_slot_drug_dict_updated}
            logger.info("RecommendDrops input {}".format(distribution_response))
            rd = RecommendDrops(distribution_response=distribution_response, unique_matrix_list=unique_matrix_list,
                                unique_matrix_data_list=unique_matrix_data_list)
            pack_wise_detailed_time, total_time, pack_slot_drop_info_dict, pack_slot_drug_config_id_dict, \
            pack_slot_drug_quad_id_dict, unique_matrix_list, unique_matrix_data_list = rd.get_pack_fill_analysis()

            pack_drug_canister_robot_dict = fill_pack_drug_canister_robot_dictV3(
                pack_slot_drop_info_dict=deepcopy(
                    pack_slot_drop_info_dict),
                robot_quadrant_drug_distribution_dict=deepcopy(
                    robot_quadrant_drug_data),
                robot_quadrant_drug_canister_info_dict=deepcopy(
                    robot_quadrant_drug_canister_info_dict),
                pack_drug_slot_number_slot_id_dict=deepcopy(
                    pack_drug_slot_number_slot_id_dict),
                pack_slot_drug_quad_id_dict=deepcopy(
                    pack_slot_drug_quad_id_dict),
                pack_slot_drug_config_id_dict=deepcopy(
                    pack_slot_drug_config_id_dict),
                robot=device_id,
                pack_slot_drug_dict_global=pack_all_slot_drug_dict,
                pack_canister_slot_drug_dict=pack_canister_slot_drug_dict_updated)

            analysis_data, pack_max_auto_drop = create_canister_pack_analysis_data(pack_drug_canister_robot_dict,
                                                                                   canister_location_number,
                                                                                   batch_id,company_id=company_id)

            db_save_analysis(analysis_data, batch_id)

        return pack_max_auto_drop

    except Exception as e:
        logger.error("Exception in execute_recommendation_for_new_pack_after_change_rx {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Exception in execute_recommendation_for_new_pack_after_change_rx: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def fill_pack_drug_canister_robot_dictV3(pack_slot_drop_info_dict, robot_quadrant_drug_distribution_dict,
                                         pack_drug_slot_number_slot_id_dict, robot_quadrant_drug_canister_info_dict,
                                         pack_slot_drug_config_id_dict, pack_slot_drug_quad_id_dict,
                                         robot, pack_slot_drug_dict_global, pack_canister_slot_drug_dict):
    """

    @param pack_slot_drug_dict_global:
    @param pack_slot_drop_info_dict:
    @param robot_quadrant_drug_distribution_dict:
    @param pack_drug_slot_number_slot_id_dict:
    @param robot_quadrant_drug_canister_info_dict:
    @param pack_slot_drug_config_id_dict:
    @param pack_slot_drug_quad_id_dict:
    @param robot:
    @return:
    """
    try:

        pack_drug_canister_robot_dict = dict()

        for pack, slot_details in pack_slot_drug_dict_global.items():

            if pack not in pack_canister_slot_drug_dict:
                # when after change rx the pack got split and it does not have any canister drug
                continue

            pack_drug_canister_robot_dict[pack] = []
            for slot, drugs in slot_details.items():

                for drug in drugs:

                    slot_id = pack_drug_slot_number_slot_id_dict[pack][drug][slot]

                    if slot not in pack_canister_slot_drug_dict[pack]:
                        pack_drug_canister_robot_dict[pack].append(
                            [drug, None, None, None, slot_id, None, None])
                        continue

                    if drug not in pack_canister_slot_drug_dict[pack][slot]:
                        pack_drug_canister_robot_dict[pack].append(
                            [drug, None, None, None, slot_id, None, None])
                        continue

                    quadrant_details = pack_slot_drop_info_dict[pack][slot]
                    drug_used = False

                    if 'drop_number' in quadrant_details and quadrant_details['drop_number'] is None:
                        pack_drug_canister_robot_dict[pack].append(
                            [drug, None, None, None, slot_id, None, None])
                        continue

                    if type(quadrant_details['quadrant']) == tuple or type(quadrant_details['quadrant']) == set:
                        quadrants = list(quadrant_details['quadrant'])
                    else:
                        quadrants = list(map(int, list(str(quadrant_details['quadrant']))))

                    if len(quadrant_details['configuration_id']) > 1:
                        quad = pack_slot_drug_quad_id_dict[pack][slot][drug]
                        conf_id = pack_slot_drug_config_id_dict[pack][slot][drug]
                        drop_id = pack_slot_drop_info_dict[pack][slot]['drop_number']
                        if drug in robot_quadrant_drug_distribution_dict[robot][quad]['drugs']:
                            if drug_used is True:
                                break
                            if drug in robot_quadrant_drug_canister_info_dict[robot][quad]:
                                canister_id = robot_quadrant_drug_canister_info_dict[robot][quad][drug]
                                pack_drug_canister_robot_dict[pack].append(
                                    [drug, canister_id[0], robot, quad, slot_id, drop_id,
                                     {conf_id}])
                            else:
                                pack_drug_canister_robot_dict[pack].append(
                                    [drug, None, None, None, slot_id, None, None])
                            drug_used = True
                        continue

                    for quad in quadrants:
                        if drug in robot_quadrant_drug_distribution_dict[robot][quad]['drugs']:
                            if drug_used is True:
                                break
                            if drug in robot_quadrant_drug_canister_info_dict[robot][quad]:
                                canister_id = robot_quadrant_drug_canister_info_dict[robot][quad][drug]

                                pack_drug_canister_robot_dict[pack].append(
                                    [drug, canister_id[0], robot, quad, slot_id, quadrant_details['drop_number'],
                                     quadrant_details['configuration_id']])

                            else:
                                pack_drug_canister_robot_dict[pack].append(
                                    [drug, None, None, None, slot_id, None, None])
                            drug_used = True

        return pack_drug_canister_robot_dict

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Exception in fill_pack_drug_canister_robot_dictV3: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def create_canister_pack_analysis_data(analysis, canister_location_number, batch_id, company_id , reserved_canister=True,
                                       mfd_data=False, canister_ids = None, device_id=None):
    """
    Create data to save in pack analysis and analysis details tables
    @param batch_id:
    @param canister_location_number:
    @param analysis:
    @return:
    :param reserved_canister:
    """
    try:
        logger.info("Input args with loc {}".format(canister_location_number))
        # todo give here dummy location of that device only
        pack_list = list()
        analysis_data = list()
        pack_max_auto_drop_number = dict()
        canister_dict = dict()
        canister_ids = [] if not canister_ids else canister_ids
        for pack, drugs in analysis.items():
            # create analysis data to store in db
            pack_data = dict()
            pack_max_auto_drop_number[pack] = 1
            pack_list.append(pack)
            pack_data["pack_id"] = pack
            pack_data["manual_fill_required"] = 1
            pack_data.setdefault('ndc_list', [])
            for item in drugs:
                if item[5] and item[5] > pack_max_auto_drop_number[pack]:
                    pack_max_auto_drop_number[pack] = item[5]
                drug = {}
                canister_id = item[1]
                if canister_id and canister_id not in canister_dict.keys():
                    canister_dict[canister_id] = {"device_id": item[2], "quadrant": item[3]}
                location_number = canister_location_number.get(canister_id, None)
                # quadrant, device_id = get_quadrant_and_device_from_location_number_dao(location_number)
                # assign empty location in robot only for change ndc flow and if current quadrant and current device of
                # canister are not in robot.
                if mfd_data and canister_id in canister_ids:
                    canister_data = get_canister_data_by_canister_ids(canister_ids, None, None, None)
                    if canister_data[0][0]["canister_type"] == constants.SMALL_CANISTER_CODE:
                        drawer_type = [constants.SMALL_CANISTER_CODE, constants.BIG_CANISTER_CODE]
                    else:
                        drawer_type = [constants.BIG_CANISTER_CODE]
                    empty_locations = get_empty_location_by_quadrant(device_id=item[2], quadrant=item[3],
                                                                     company_id=company_id,
                                                                     drawer_type=drawer_type,
                                                                     exclude_location=[])
                    location_number = empty_locations.get('location_number', None)
                    if not location_number:
                        return error(1000, f"Oops! There are no empty locations in Robot {constants.ROBOT_MAPPING[device_id]} where canister ID {canister_ids[0]} can be used."), None


                drug["canister_id"] = canister_id
                drug["device_id"] = item[2]
                drug["location_number"] = location_number
                drug["quadrant"] = item[3]
                drug["slot_id"] = item[4]
                drug["drop_number"] = item[5]
                drug["config_id"] = item[6]

                pack_data['ndc_list'].append(drug)
            analysis_data.append(pack_data)

        for each_can in canister_dict.keys():
            if reserved_canister:
                record, created = reserve_canister(batch_id=batch_id, canister_id=each_can)

            update_dict = {'dest_device_id': canister_dict[each_can]["device_id"],
                           'dest_quadrant': canister_dict[each_can]["quadrant"], 'trolley_loc_id': None,
                           'to_ct_meta_id': None, 'from_ct_meta_id': None, 'transfer_status': None,
                           'modified_date': get_current_date_time(), 'dest_location_number': None}

            record1, created1 = canister_transfer_get_or_create_data(canister_id=each_can, batch_id=batch_id,
                                                                     update_dict=update_dict)

        return analysis_data, pack_max_auto_drop_number

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Exception in create_canister_pack_analysis_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_drop_number_for_new_packs(new_pack_list: list, pack_max_drop_number: dict):
    """
    Function to update drop number in mfd analysis details for packs in which canister recom
    is updated.
    @param new_pack_list:
    @param pack_max_drop_number:
    @return:
    """
    try:
        analysis_id_drop_dict = dict()
        pack_drop_analysis_id, pack_drop_no_dict = db_get_mfd_drop_number(pack_list= new_pack_list)
        new_pack_drop_analysis_id = dict()
        for pack in pack_max_drop_number.keys():
            max_drop = pack_max_drop_number[pack] + 1
            if pack in pack_drop_analysis_id.keys():
                new_pack_drop_analysis_id[pack] = dict()
                for drop, analysis_id_list in pack_drop_analysis_id[pack].items():
                    new_pack_drop_analysis_id[pack][max_drop] = analysis_id_list
                    max_drop += 1

        logger.info("update_drop_number_for_new_packs new_pack_drop_analysis_id {}".format(new_pack_drop_analysis_id))

        if len(new_pack_drop_analysis_id):
            for pack, drop_analysis_id in new_pack_drop_analysis_id.items():
                for drop, analysis_id_list in drop_analysis_id.items():
                    for analysis_id in analysis_id_list:
                        analysis_id_drop_dict[analysis_id] = drop

            update_mfd_analysis_details = update_drop_number_in_mfd_analysis_details(analysis_id_drop_dict)

        return analysis_id_drop_dict

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Exception in update_drop_number_for_new_packs: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def revert_canister_usage_by_recom(device_id, canister_id, company_id,  batch_id=None, affected_pack_list=None):
    """

    :param device_id:
    :param canister_id:
    :param company_id:
    :param preferred_quad:
    :param batch_id:
    :param affected_pack_list:
    :return:
    """
    packs_to_reconfigure = list()
    if affected_pack_list is None:
        affected_pack_list = list()
    try:
        with db.transaction():
            pack_canister_slot_drug_dict_updated = dict()
            unique_matrix_list = list()
            unique_matrix_data_list = list()

            # packs_to_reconfigure, preferred_quad = db_get_canister_reverted_packs(device_id, [canister_id])

            # pack_list = list(set(packs_to_reconfigure).intersection(set(affected_pack_list)))
            pack_list = list(affected_pack_list)
            # this is to create failsafe as in case if no
            # canister quadrant is determined from the table, no re-run of recommendation
            # if not pack_list or not preferred_quad:
            #     return affected_pack_list
            if not pack_list:
                return affected_pack_list
            pack_all_slot_drug_dict, pack_canister_slot_drug_dict, drugs_set, pack_manual_drugs_set = \
                get_pack_slotwise_canister_drugs_(pack_list=pack_list, company_id=company_id)

            canister_quad_drug = get_canister_drug_quadrant([canister_id])
            if drugs_set:
                pack_drug_slot_number_slot_id_dict = get_pack_drug_slot_details(pack_list)

                robot_quadrant_drug_data, remaining_drug_canister_location_dict, robot_quadrant_drug_canister_info_dict, \
                canister_location_number, canister_drugs_set = get_nx_canister_drug_with_location_for_given_drugs(
                    drug_list=list(drugs_set), device_id=device_id, batch_id=batch_id, pack_list=pack_list,
                    canister_ids=[canister_id])
                # for canister, quad_drug in canister_quad_drug.items():
                #     for quad, drug in quad_drug.items():
                #         # todo: Add check if no space in preferred quad, find spack for it
                #         try:
                #             robot_quadrant_drug_data[device_id][preferred_quad]["drugs"].add(drug)
                #         except (KeyError, Exception) as e:
                #             logger.info("Error in rever_canister_usage while adding canister from quadrant")
                #             raise e
                #         try:
                #             robot_quadrant_drug_canister_info_dict[device_id][preferred_quad][drug]=(canister)
                #         except (KeyError, ValueError, Exception) as e:
                #             logger.info("Error in use_other_drug while removing adding from quadrant")
                #             raise e

                for pack, slot_drug_dict in pack_canister_slot_drug_dict.items():
                    pack_canister_slot_drug_dict_updated[pack] = dict()
                    for slot, drug_set in slot_drug_dict.items():
                        pack_canister_slot_drug_dict_updated[pack][slot] = set()
                        for drug in drug_set:
                            if drug in canister_drugs_set:
                                pack_canister_slot_drug_dict_updated[pack][slot].add(drug)

                distribution_response = {"quadrant_drugs": robot_quadrant_drug_data[device_id],
                                         "pack_slot_drug_dict": pack_canister_slot_drug_dict_updated}
                logger.info("In rever_canister_usage RecommendDrops input {}".format(distribution_response))
                rd = RecommendDrops(distribution_response=distribution_response, unique_matrix_list=unique_matrix_list,
                                    unique_matrix_data_list=unique_matrix_data_list)
                pack_wise_detailed_time, total_time, pack_slot_drop_info_dict, pack_slot_drug_config_id_dict, \
                pack_slot_drug_quad_id_dict, unique_matrix_list, unique_matrix_data_list = rd.get_pack_fill_analysis()

                pack_drug_canister_robot_dict = fill_pack_drug_canister_robot_dictV3(
                    pack_slot_drop_info_dict=deepcopy(
                        pack_slot_drop_info_dict),
                    robot_quadrant_drug_distribution_dict=deepcopy(
                        robot_quadrant_drug_data),
                    robot_quadrant_drug_canister_info_dict=deepcopy(
                        robot_quadrant_drug_canister_info_dict),
                    pack_drug_slot_number_slot_id_dict=deepcopy(
                        pack_drug_slot_number_slot_id_dict),
                    pack_slot_drug_quad_id_dict=deepcopy(
                        pack_slot_drug_quad_id_dict),
                    pack_slot_drug_config_id_dict=deepcopy(
                        pack_slot_drug_config_id_dict),
                    robot=device_id,
                    pack_slot_drug_dict_global=pack_all_slot_drug_dict,
                    pack_canister_slot_drug_dict=pack_canister_slot_drug_dict)

                analysis_data, pack_max_auto_drop = create_canister_pack_analysis_data(pack_drug_canister_robot_dict,
                                                                                       canister_location_number,
                                                                                       batch_id, company_id, False,
                                                                                       device_id)

                pack_wise_skipped_drug = get_pack_wise_skipped_drug(pack_list, device_id)

                db_update_analysis_data(analysis_data, batch_id, pack_wise_skipped_drug)

                # return list(set(pack_list+affected_pack_list))
                return pack_list

    except Exception as e:
        logger.error("Exception in rever_canister_usage {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Exception in rever_canister_usage: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def use_other_canisters(device_id, canister_ids, company_id, batch_id=None, affected_pack_list=None, mfd_data=None):
    if affected_pack_list is None:
        affected_pack_list = list()
    mfd_analysis_dict = {}
    analysis_ids = []
    drug_id = None
    if mfd_data:
        # when change ndc done for any mfd drug and canister will be used for current batch then this case will be used
        affected_pack_list, mfd_analysis_dict, analysis_ids, batch_id, drug_id, device_id = get_pending_mfd_pack_list_dao(canister_ids)
        # if not affected_pack_list:
        #     affected_pack_list, device_id = get_affected_pack_list_for_canisters(canister_ids)
        #     mfd_data = None
    try:
        with db.transaction():
            pack_canister_slot_drug_dict_updated = dict()
            unique_matrix_list = list()
            unique_matrix_data_list = list()

            packs_to_reconfigure, current_batch_id = get_packs_to_be_filled_by_canister(device_id, canister_ids)
            if not packs_to_reconfigure and not affected_pack_list:
                return create_response(1)

            # skip_for_packs
            if affected_pack_list and packs_to_reconfigure and (current_batch_id == batch_id):
                pack_list = list(set(packs_to_reconfigure).intersection(set(affected_pack_list)))

            # skip_for_batch
            elif packs_to_reconfigure and not affected_pack_list:
                pack_list = packs_to_reconfigure

            # to handle the case of merge_batch at PPP screen while importing the batch
            elif affected_pack_list:
                pack_list = affected_pack_list

            pack_all_slot_drug_dict, pack_canister_slot_drug_dict, drugs_set, pack_manual_drugs_set = get_pack_slotwise_canister_drugs_(
                pack_list=pack_list, company_id=company_id, mfd_drug_id=drug_id)

            """
            commented below code to handle the current changes regarding replenish_skipped_canister fox nx
            """
            # canister_quad_drug = get_canister_drug_quadrant(canister_ids)
            if drugs_set:
                pack_drug_slot_number_slot_id_dict = get_pack_drug_slot_details(pack_list)

                robot_quadrant_drug_data, remaining_drug_canister_location_dict, robot_quadrant_drug_canister_info_dict, \
                canister_location_number, canister_drugs_set = get_nx_canister_drug_with_location_for_given_drugs(
                    drug_list=list(drugs_set), device_id=device_id, batch_id=batch_id, pack_list=pack_list,
                    canister_ids=canister_ids, mfd_data=mfd_data, drug_id=drug_id)
                """
                commented below code to handle the current changes regarding replenish_skipped_canister fox nx
                """
                # for canister, quad_drug in canister_quad_drug.items():
                #     if canister in skipped_canister:
                #         for quad, drug in quad_drug.items():
                #             try:
                #                 robot_quadrant_drug_data[device_id][quad]["drugs"].remove(drug)
                #             except (KeyError, Exception) as e:
                #                 logger.info("Error in use_other_drug while removing canister from quadrant {}".format(e))
                #                 return error(0, 'Error in use_other_drug while removing canister from robot_quadrant_drug_data')
                #             try:
                #                 robot_quadrant_drug_canister_info_dict[device_id][quad][drug].remove(canister)
                #             except (KeyError, ValueError, Exception) as e:
                #                 logger.info("Error in use_other_drug while removing canister from quadrant {}".format(e))
                #                 return error(0,
                #                              'Error in use_other_drug while removing canister from robot_quadrant_drug_canister_info_dict')

                for pack, slot_drug_dict in pack_canister_slot_drug_dict.items():
                    pack_canister_slot_drug_dict_updated[pack] = dict()
                    for slot, drug_set in slot_drug_dict.items():
                        pack_canister_slot_drug_dict_updated[pack][slot] = set()
                        for drug in drug_set:
                            if drug in canister_drugs_set:
                                pack_canister_slot_drug_dict_updated[pack][slot].add(drug)

                distribution_response = {"quadrant_drugs": robot_quadrant_drug_data[device_id],
                                         "pack_slot_drug_dict": pack_canister_slot_drug_dict_updated}
                logger.info("RecommendDrops input {}".format(distribution_response))
                rd = RecommendDrops(distribution_response=distribution_response, unique_matrix_list=unique_matrix_list,
                                    unique_matrix_data_list=unique_matrix_data_list)
                pack_wise_detailed_time, total_time, pack_slot_drop_info_dict, pack_slot_drug_config_id_dict, \
                pack_slot_drug_quad_id_dict, unique_matrix_list, unique_matrix_data_list = rd.get_pack_fill_analysis()

                pack_drug_canister_robot_dict = fill_pack_drug_canister_robot_dictV3(
                    pack_slot_drop_info_dict=deepcopy(
                        pack_slot_drop_info_dict),
                    robot_quadrant_drug_distribution_dict=deepcopy(
                        robot_quadrant_drug_data),
                    robot_quadrant_drug_canister_info_dict=deepcopy(
                        robot_quadrant_drug_canister_info_dict),
                    pack_drug_slot_number_slot_id_dict=deepcopy(
                        pack_drug_slot_number_slot_id_dict),
                    pack_slot_drug_quad_id_dict=deepcopy(
                        pack_slot_drug_quad_id_dict),
                    pack_slot_drug_config_id_dict=deepcopy(
                        pack_slot_drug_config_id_dict),
                    robot=device_id,
                    pack_slot_drug_dict_global=pack_all_slot_drug_dict,
                    pack_canister_slot_drug_dict=pack_canister_slot_drug_dict)

                analysis_data, pack_max_auto_drop = create_canister_pack_analysis_data(
                    analysis=pack_drug_canister_robot_dict,
                    canister_location_number=canister_location_number,
                    batch_id=batch_id, company_id=company_id, mfd_data=True, canister_ids=canister_ids,device_id=device_id)

                if pack_max_auto_drop is None:
                    return error(1000, f"Oops! There are no empty locations in Robot {constants.ROBOT_MAPPING[device_id]} where canister ID {canister_ids[0]} can be used.")

                pack_wise_skipped_drug = get_pack_wise_skipped_drug(pack_list, device_id)

                db_update_analysis_data(analysis_data, batch_id, pack_wise_skipped_drug, mfd_analysis_dict, analysis_ids)

                return True

    except Exception as e:
        logger.error("Exception in execute_recommendation_for_new_pack_after_change_rx {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Exception in execute_recommendation_for_new_pack_after_change_rx: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
@validate(required_fields=["packlist", "batch_id", "system_id"])
def get_analysis_data(pack_info):
    """
    Returns canister list and manual drugs for analysis done for batch id and pack ids

    @param pack_info:
    :return: json
    """
    pack_ids = pack_info["packlist"]
    batch_id = pack_info["batch_id"]
    system_id = pack_info["system_id"]
    analysis_data = defaultdict(dict)
    facility_ids = set()
    facility_seq_no = dict()

    # valid_packs = PackDetails.db_verify_packlist_by_system_id(pack_ids, system_id)
    valid_packs = db_verify_packlist_by_system(pack_ids, system_id)

    if not valid_packs:
        return error(1014)

    try:
        for record in db_get_analysis_data(batch_id, pack_ids=pack_ids):
            if record['facility_id'] not in facility_ids:
                facility_seq_no[record['facility_id']] = len(facility_ids) + 1
                facility_ids.add(record['facility_id'])
            record['facility_seq_no'] = facility_seq_no[record['facility_id']]

            canister_flag, manual_flag = False, False
            analysis_data[record["pack_id"]].setdefault("canister_list", [])
            analysis_data[record["pack_id"]].setdefault("manual_drugs", [])
            quantities = list(map(float, record["quantities"].split(',')))
            robot_quantities = [math.floor(i) != 0 for i in quantities]  # list of bool
            fractional_quantities = [i % 1 != 0 for i in quantities]  # list of bool
            if any(robot_quantities) and record["canister_id"] and record["device_id"]:
                # if all drugs are fractional, won't be dispensed by canister
                #  was present in analysis, add in canister list
                record['canister_qty'] = record['drug_qty']
                record['manual_qty'] = record['total_qty'] - record["drug_qty"]
                # analysis_data[record["pack_id"]]["canister_list"].append(record.copy())
                canister_flag = True

            half_pill = any(fractional_quantities)
            # TODO Remove drug_qty key,
            # TODO ... right now it is same as manual_qty in manual list and same as canister_qty in canister list
            # TODO ... as this can be confusing
            if not record["canister_id"] or record["device_id"] is None or half_pill:
                if half_pill and record["canister_id"] and record["device_id"] is not None:
                    # manual due to half pills, so consider only half pills
                    record['canister_qty'] = record["drug_qty"]
                    record['manual_qty'] = record['total_qty'] - record["drug_qty"]
                else:
                    # manual because canister not present, all qty will be manual
                    record['canister_qty'] = float(0)
                    record['manual_qty'] = record["total_qty"]
                # manual drug if no canister found during analysis or fractional pill
                # analysis_data[record["pack_id"]]["manual_drugs"].append(record)
                manual_flag = True
            record['canister_and_manual'] = manual_flag and canister_flag  # flag to set drug present in both list
            if canister_flag:
                analysis_data[record["pack_id"]]["canister_list"].append(record.copy())
            if manual_flag:
                record['drug_qty'] = record['manual_qty']
                analysis_data[record["pack_id"]]["manual_drugs"].append(record)
        return create_response(analysis_data)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def replenish_for_idle_robots(response, idle_robots):
    """
    Filters replenish response for idle robots if specified
    :param response: list of canisters which needs replenish
    :param idle_robots: list of idle robots
    :return: list
    """
    try:
        if not idle_robots:
            return list(response)
        filtered_response = list()
        replenishable_robots = [None] + idle_robots  # None = On Shelf
        for item in response:
            if item["device_id"] in replenishable_robots:
                filtered_response.append(item)
        return filtered_response

    except Exception as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
@validate(required_fields=["batch_id", "system_id", "user_id", "company_id"])
def update_analysis_data(analysis_info):
    """
    Updates canisters location data in analysis, and returns batch details and replenish data

    @param analysis_info:
    :return: json
    """
    batch_id = analysis_info["batch_id"]
    system_id = analysis_info["system_id"]
    company_id = analysis_info["company_id"]
    user_id = analysis_info["user_id"]
    get_replenish = analysis_info.get("get_replenish", False)
    idle_robot_ids = analysis_info.get("idle_robot_ids", None)
    update_batch_status = analysis_info.get("update_batch_status", True)
    transfer_info_required = analysis_info.get('transfer_info_required', True)
    import_state = analysis_info.get('import_state', False)
    batch_manual = False
    # Whether api is used for replenish screen
    update_dict = dict()
    canister_location = dict()
    canister_ids = set()
    manual_list = list()
    analysis_details_ids = list()
    batch_data = dict()
    pack_orders = defaultdict(list)
    canister_qty = dict()
    canister_records = dict()
    replenish_canister_ids = set()
    replenish_data = dict()
    deleted_canister = False
    canister_destination = dict()
    pack_id_list = list()
    manual_pack_list = list()
    delivery_date_manual = list()
    null_delivery_date_manual = list()
    # canister_location_null = set()
    canister_location_not_null = set()
    manual_drug_list = list()
    required_replenish_quantity = dict()
    mfd_packs = list()
    batch_mfd_packs = list()
    canister_location_dict = dict()
    pack_canister_dict = dict()

    try:
        # is_imported = db_is_imported(batch_id)
        is_imported = db_batch_import_status(batch_id)
        if is_imported is None or is_imported:
            return error(1020)

        """
        Below code block added to check if this function is already executed and we have manual packs
        for this batch stored then directly return them.
        """
        # pending_manual_packs = BatchManualPacks.verify_manual_packs_by_batch_id(batch_id)
        # if import_state and len(pending_manual_packs) > 0:
        #     batch_packs = PackDetails.db_get_pack_ids_by_batch_id(batch_id, company_id)
        #     if len(batch_packs) == 0:
        #         batch_manual = True
        #     logger.info("response of pack_analysis {}, {}".format(pending_manual_packs, batch_id))
        #     return create_response({"manual_packs": pending_manual_packs, "batch_id": batch_id,
        #                               "batch_manual": batch_manual})
        """
        Verification ENDS
        """

        # here device_ids are robot_ids of system
        device_ids = [item["id"] for items in db_get_robots_by_systems_dao([system_id]).values() for item in
                      items]
        for record in db_get_canister_by_company_id(company_id):
            if record["device_id"] not in device_ids:
                # if not present in given system's robot, mark it unavailable
                canister_location[record["canister_id"]] = (None, None, None)
            else:
                canister_location[record["canister_id"]] = (
                    record["device_id"], record["location_number"], record['quadrant'])
            canister_records[record["canister_id"]] = record
            canister_qty[record["canister_id"]] = record["available_quantity"]

        logger.info(
            'In update_analysis_data, Canister locations before updating locations: {}'.format(canister_location))

        if import_state:
            batch_mfd_data = db_get_batch_mfd_packs(batch_id)
            logger.info(batch_mfd_data)
            batch_mfd_packs = [int(item['mfd_pack']) for item in batch_mfd_data]

            logger.info("In update_analysis_data, batch mfd packs {}".format(batch_mfd_packs))

        for record in db_get_canister_data(batch_id):
            if record["canister_id"] and record["canister_id"] not in canister_ids:
                canister_ids.add(record["canister_id"])

                try:
                    update_dict[record["canister_id"]] = {
                        'device_id': canister_location[record["canister_id"]][0],
                        'location_number': canister_location[record["canister_id"]][1]
                    }
                except KeyError as e:
                    deleted_canister = True
                    update_dict[record["canister_id"]] = {'device_id': None, 'location_number': None, 'active': False}

                    logger.info('In update_analysis_data, Deleted Canister Found: Canister ID - {}, exc: {}'.format(
                        record["canister_id"], e))
            try:
                canister_manual = record["canister_id"] is None or canister_location[record["canister_id"]][0] is None
                if canister_manual:
                    # if no canister allocated or canister present outside robot, mark it manual
                    manual_list.append(record["analysis_id"])

            except KeyError:
                # deleted canister found
                pass

            # TODO: check this for v2 and verify
            if record["canister_id"] and record['canister_id'] in canister_location.keys() \
                    and (record['dest_quadrant'] != canister_location[record["canister_id"]][2] or
                         canister_location[record["canister_id"]][0] != record['dest_device_id']):
                manual_drug_list.append(record["id"])
                canister_location_dict[record["canister_id"]] = {"device_id": record["device_id"],
                                                                 "quadrant": record["quadrant"],
                                                                 "location_number": record["location_number"]}
                if record["pack_id"] not in pack_canister_dict.keys():
                    pack_canister_dict[record['pack_id']] = set()
                pack_canister_dict[record['pack_id']].add(record['canister_id'])

            else:
                analysis_details_ids.append(record["id"])

        if not get_replenish:  # If importing packs
            with db.transaction():  # update canisters location and mark manual acc. to canisters
                # for k, v in update_dict.items():
                #     PackAnalysisDetails.update_canister_location(k, v, analysis_details_ids)
                # commenting to use optimized functions
                update_canister_location_v2(analysis_details_ids, system_id)
                logger.info('Manual analysis IDs for batch ID: {} - {}'.format(batch_id, manual_list))

                # PackAnalysis.db_update_manual_packs(manual_list, True)
                db_pack_analysis_update_manual_packs(manual_list=manual_list, manual=True)

                # PackAnalysisDetails.update_manual_canister_location_v2(manual_drug_list)

                insert_status = insert_data_in_replenish_skipped_canister(canister_location_dict, pack_canister_dict)
                logger.info(f'In update_analysis_data, insert_status: {insert_status}')

                status, canister_list = db_pack_analysis_update_manual_canister_location_v2(manual_drug_list=manual_drug_list)
                if canister_list:
                    for device_id in device_ids:
                        txr_dict, can_list = get_multi_canister_drug_data_by_canister(canister_list, device_id, batch_id)
                        if can_list:
                            affected_pack_list = db_get_affected_pack_list(can_list, device_id, batch_id)
                            if affected_pack_list:
                                rerun_drop_optimisation = use_other_canisters(device_id, can_list, company_id,
                                                                              batch_id=batch_id,
                                                                              affected_pack_list=affected_pack_list)
        else:
            if not idle_robot_ids:  # only change status when user is in replenish canister screen
                if update_batch_status:
                    # BatchMaster.update(status=settings.BATCH_CANISTER_TRANSFER_DONE,
                    #                    modified_by=user_id,
                    #                    modified_date=get_current_date_time()) \
                    #     .where(BatchMaster.id == batch_id).execute()
                    db_update_batch_status(batch_id=batch_id, user_id=user_id,
                                           status=settings.BATCH_CANISTER_TRANSFER_DONE)

        if transfer_info_required:
            canister_destination = get_canister_destination(batch_id)

        facility_patient_id_set = set()
        # prepare analysis data, replenish data, pack orders
        for record in db_get_analysis_data(batch_id):
            facility_patient_id_set.add(record['schedule_facility_id'])
            canister_id = record["canister_id"]
            if record['pack_id'] not in batch_data:
                pack_id_list.append((record['pack_id']))
                batch_data[record["pack_id"]] = {
                    "pack_id": record["pack_id"],
                    "manual_fill_required": record["manual_fill_required"],
                    "uploaded_date": record["uploaded_date"],
                    "facility_name": record["facility_name"],
                    "patient_name": record["patient_name"],
                    "patient_id": record["patient_id"],
                    "patient_no": record["patient_no"],
                    "pack_display_id": record["pack_display_id"],
                    "device_ids": [],
                    "canister_id_list": [],
                    "ndc_list": [],
                    "schedule_facility_id": record["schedule_facility_id"],
                    "pack_priority": record["order_no"],
                    "consumption_start_date": record["consumption_start_date"],
                    "consumption_end_date": record["consumption_end_date"],
                    "delivery_datetime": record["delivery_datetime"],
                }
            if record["device_id"]:
                batch_data[record["pack_id"]]['device_ids'].append(record["device_id"])
            if record["canister_id"]:
                batch_data[record["pack_id"]]['canister_id_list'].append(record['canister_id'])
            batch_data[record["pack_id"]]['ndc_list'].append({
                "device_id": record["device_id"],
                "canister_id": record["canister_id"],
                "location_number": record["location_number"],
                "ndc": record["ndc"],
                "txr": record["txr"],
                "total_quantity": float(record["drug_qty"]),
                "formatted_ndc": record["formatted_ndc"],
                "drug_id": record["drug_id"],
                "available_quantity": record["available_quantity"]
            })
            # if record["canister_id"]:

            if record["canister_id"] and record["device_id"]:
                try:
                    if not required_replenish_quantity.get(canister_id, None):

                        required_replenish_quantity[canister_id] = {
                            "required_qty": record["drug_qty"],
                            "available_qty": canister_qty[canister_id],
                        }
                    else:
                        current_data = required_replenish_quantity[canister_id]
                        required_replenish_quantity[canister_id] = {
                            "required_qty": record["drug_qty"] + current_data['required_qty'],
                            "available_qty": canister_qty[canister_id],

                        }
                    canister_qty[canister_id] -= record["drug_qty"]
                    if canister_qty[canister_id] < 0:
                        replenish_data[canister_id] = canister_records[canister_id]
                        replenish_data[canister_id]["replenish_qty"] = float(abs(canister_qty[canister_id]))
                        if replenish_data[canister_id].get("order_no", record["order_no"] + 1) > record["order_no"]:
                            # replacing facility with the least priority  # on key error put facility anyway
                            replenish_data[canister_id]["order_no"] = record["order_no"]
                            replenish_data[canister_id]["facility_name"] = record["facility_name"]
                            replenish_canister_ids.add(canister_id)
                            if transfer_info_required:
                                replenish_data[canister_id].update(canister_destination[canister_id])
                except KeyError:
                    deleted_canister = True
            if record["device_id"] and record["canister_id"]:
                pack_orders[record["device_id"]].append(record["pack_id"])

        logger.info('Pack_id list for pack_analysis {} - {}'.format(len(pack_id_list), pack_id_list))
        patient_schedule_ids = get_next_schedules(company_id=company_id,
                                                  active=True,
                                                  schedule_facility_ids=facility_patient_id_set)
        for pack, record in batch_data.items():
            schedule_detail = patient_schedule_ids.get(record['schedule_facility_id'], None)
            if schedule_detail:
                record['delivery_datetime'] = schedule_detail['delivery_date']
            else:
                record['delivery_datetime'] = None
            logger.info("batch data in analysis {}".format(record))

            logger.info("Batch data log {}".format(record))
            if import_state and len(record['device_ids']) == 0 and len(record["canister_id_list"]) == 0:
                # if packs to be filled by mfd then do not consider them manual
                if (batch_mfd_packs and pack not in batch_mfd_packs) or not batch_mfd_packs:
                    manual_pack_list.append(record['pack_id'])
                else:
                    # packs which are to be filled only by mfd
                    mfd_packs.append(pack)

            for each_data in record['ndc_list']:
                canister_location_not_null.add(each_data['canister_id'])

        # get manual packs from pack analysis which were skipp due to manual from update_mfd_analysis API
        manual_packs = get_manual_packs_having_status_skipp_due_to_manual(batch_id=batch_id)
        logger.info(f"In update_analysis_data, manual_packs having status skipped due to manual: {manual_packs}")

        manual_pack_list.extend(manual_packs)
        manual_pack_list.sort()

        if import_state and len(manual_pack_list) > 0:
            # batch_packs = PackDetails.db_get_pack_ids_by_batch_id(batch_id, company_id)
            batch_packs = get_pack_ids_by_batch_id(batch_id=batch_id, company_id=company_id)

            if len(batch_packs) == len(manual_pack_list):
                resp = update_scheduled_start_date_for_next_batches(batch_packs)
                batch_manual = True

            packs_dd_dict = get_each_pack_delivery_date(manual_pack_list)
            for pack, delivery_date in packs_dd_dict.items():
                if delivery_date is None:
                    null_delivery_date_manual.append(pack)
                else:
                    delivery_date_manual.append(pack)

            # pending_manual_packs = BatchManualPacks.db_verify_manual_packs_by_batch_id(batch_id)
            pending_manual_packs = get_manual_packs_by_batch_id(batch_id=batch_id)

            pending_manual_packs.sort()
            logger.info("manual packs {}, {}".format(pending_manual_packs, manual_pack_list))
            if len(pending_manual_packs) == 0:
                # add_data = BatchManualPacks.db_add_batch_manual_packs(manual_pack_list, batch_id, user_id)
                add_data = db_add_batch_manual_packs_dao(manual_pack_list=manual_pack_list, batch_id=batch_id,
                                                         user_id=user_id)
                logger.info(add_data)

            elif len(pending_manual_packs) > 0 and pending_manual_packs == manual_pack_list:
                logger.info("data already added in batch manual packs table for packs {}".format(manual_pack_list))

            elif len(pending_manual_packs) > 0:
                # add_data = BatchManualPacks.db_get_create_manual_packs(manual_pack_list, pending_manual_packs,
                #                                                       batch_id, user_id)
                add_data = db_get_create_manual_packs_dao(manual_pack_list=manual_pack_list,
                                                          pending_manual_packs=pending_manual_packs, batch_id=batch_id,
                                                          user_id=user_id)
                logger.info(add_data)

        logger.info('replenish_data batch_id: {}, length: {}, data: {}'
                    .format(batch_id, len(replenish_data), replenish_data))

        total_replenish_count = len(replenish_data)
        replenish_response = replenish_for_idle_robots(replenish_data.values(), idle_robot_ids)
        set_initial_pack_sequence(batch_id)
        response = {'batch_details': list(batch_data.values()),
                    'batch_id': batch_id,
                    'pack_orders': pack_orders,
                    'replenish_data': replenish_response,
                    'deleted_canister': deleted_canister,
                    'total_replenish_count': total_replenish_count,
                    'replenish_canister_ids': replenish_canister_ids,
                    'manual_packs': manual_pack_list,
                    'delivery_date_manual': delivery_date_manual,
                    'null_delivery_date_manual': null_delivery_date_manual,
                    'required_replenish_quantity': required_replenish_quantity,
                    'batch_manual': batch_manual,
                    'manual_mfd_packs': mfd_packs
                    }
        logger.info("response of pack_analysis {}".format(response))
        return create_response(response)
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(f"in update_analysis_data error occured {e}")

