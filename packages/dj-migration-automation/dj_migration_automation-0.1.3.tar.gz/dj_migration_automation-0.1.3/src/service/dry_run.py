from peewee import IntegrityError, InternalError

import settings
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import log_args_and_response
from src.dao.pack_distribution_dao import PackDistributor, transfer_canister_recommendation, \
    recommend_canister_to_register, recommend_canister_to_register_optimised
from src.service.pack_distribution import get_current_split

logger = settings.logger


@log_args_and_response
def pack_distribution(company_id, batch_ids):

    try:
        batch_ids = list(map(int, batch_ids.split(',')))

        pack_distributor = PackDistributor(company_id, dry_run=True)
        pack_distributor.create_batch_packs_from_batches(batch_ids)

        recommendations = pack_distributor.get_recommendation()
        response = dict()
        for system, data in recommendations.items():
            response[system] = {}
            transfer_recommendations, remove_locations, \
            pending_transfers, reserved_canister = transfer_canister_recommendation(
                data['canister_transfer_info_dict'],
                pack_distributor.canister_data,
                pack_distributor.robot_dict
            )
            response[system]['pending_transfers'] = pending_transfers
            response[system]['remove_locations'] = dict(remove_locations)
            response[system]['transfer_recommendations'] = transfer_recommendations
            response[system]['pending_transfer_count'] = len(pending_transfers)
            response[system]['transfer_recommendations_count'] = len(transfer_recommendations)
            response[system]['split'] = {}
            data, split = get_current_split(
                data['analysis'], data['canister_transfer_info_dict'],
                pack_distributor.fully_manual_pack_drug
            )
            response[system]['split']['summary'] = split
            response[system]['split']['data'] = data

        return response
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Unknown error- " + str(e))


@log_args_and_response
def register_canisters(company_id, batch_id):
    try:
        response = recommend_canister_to_register({
            'company_id': company_id,
            'batch_id': batch_id
        })
        return response
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Unknown error- " + str(e))


@log_args_and_response
def register_canisters_optimised(company_id, batch_id, number_of_drugs_needed, drugs_to_register):
    try:
        response = recommend_canister_to_register_optimised({
            'company_id': company_id,
            'batch_id': batch_id,
            'number_of_drugs_needed': number_of_drugs_needed,
            'drugs_to_register':drugs_to_register
        })
        return response
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(1000, "Unknown error- " + str(e))