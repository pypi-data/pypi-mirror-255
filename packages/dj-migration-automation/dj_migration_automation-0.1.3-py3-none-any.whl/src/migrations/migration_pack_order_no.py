import logging
from copy import deepcopy

from peewee import *
from playhouse.shortcuts import case
from playhouse.migrate import MySQLMigrator, migrate

import settings
from dosepack.error_handling.error_handler import error
from model.model_pack import (BatchMaster, SlotDetails, PackRxLink, PackHeader)
from src.model.model_pack_details import PackDetails
from src import constants
from src.model.model_mfd_analysis import (MfdAnalysis)
from src.model.model_mfd_analysis_details import (MfdAnalysisDetails)

from dosepack.base_model.base_model import db
from dosepack.utilities.utils import get_current_date_time
from src.model.model_file_header import FileHeader
from model.model_init import init_db

# get the logger for the pack from global configuration file logging.json
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_slot_details import SlotDetails
from src.model.model_batch_master import BatchMaster

logger = logging.getLogger("root")


def db_get_batch_mfd_packs(batch_id):
    """
    Funtion to get list mfd packs for given batch
    @param batch_id:
    @return: list
        Sample Output = ['mfd_pack':1, 'mfd_pack':2]
    """
    try:
        mfd_canister_status = [constants.MFD_CANISTER_FILLED_STATUS,
                               constants.MFD_CANISTER_PENDING_STATUS,
                               constants.MFD_CANISTER_IN_PROGRESS_STATUS,
                               constants.MFD_CANISTER_VERIFIED_STATUS]

        query = MfdAnalysis.select(fn.GROUP_CONCAT(fn.DISTINCT(PackRxLink.pack_id)).alias('mfd_pack'),
                                   BatchMaster.system_id,
                                   fn.DATE(PackHeader.scheduled_delivery_date).alias('scheduled_delivery_date')).dicts() \
            .join(MfdAnalysisDetails, on=MfdAnalysis.id == MfdAnalysisDetails.analysis_id) \
            .join(SlotDetails, on=SlotDetails.id == MfdAnalysisDetails.slot_id) \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(BatchMaster, on=BatchMaster.id == MfdAnalysis.batch_id) \
            .where(MfdAnalysis.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                   MfdAnalysis.status_id << mfd_canister_status) \
            .group_by(PackRxLink.pack_id) \
            .order_by(fn.MIN(MfdAnalysis.order_no), fn.MIN(MfdAnalysisDetails.mfd_can_slot_no))

        return list(query)

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise

    except DoesNotExist as e:
        logger.error(e)
        return None


def change_pack_sequence_mfd(pack_list: list, order_number_list: list) -> int:
    """
    Function to updated pack sequence considering mfd_packs on top
    @param pack_list: list
    @param order_number_list: list
    @return: status
    """
    print("In change_pack_sequence_mfd with pack_list: {} and order_number_list: {}".format(pack_list, order_number_list))
    try:
        print("pack list and order list {}, {}".format(pack_list, order_number_list))
        new_seq_tuple = list(tuple(zip(map(str, pack_list), map(str, order_number_list))))
        print('new_seq_tuple: {}'.format(new_seq_tuple))
        case_sequence = case(PackDetails.id, new_seq_tuple)

        logger.info(case_sequence)
        response = PackDetails.update(order_no=case_sequence).where(
            PackDetails.id.in_(pack_list)).execute()
        logger.info(response)

        return response

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except ValueError as e:
        return error(2005, str(e))


def update_pack_sequence_of_mfd_packs(batch_id: int, mfd_packs: list) -> bool:
    """
    Function to get updated pack sequence of packs considering MFD packs to be moved
    on top
    @param batch_id: int
    @param mfd_packs: list
    @return: status
    """
    print("In update_pack_sequence_of_mfd_packs with batch_id {} and mfd_packs {}".format(batch_id, mfd_packs))
    automatic_delivery_date_pack_dict = dict()
    mfd_pack_delivery_date_dict = dict()
    delivery_dates = list()
    updated_mfd_pack_sequence = deepcopy(mfd_packs)
    updated_pack_list = list()
    order_number_list = list()
    try:
        query = PackDetails.select(PackDetails.id,
                                   PackDetails.order_no,
                                   fn.DATE(PackHeader.scheduled_delivery_date).alias('scheduled_delivery_date')).dicts() \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .where(PackDetails.batch_id == batch_id,
                   PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                   ) \
            .order_by(PackDetails.order_no)

        for record in query:
            if not record['order_no']:
                continue
            order_number_list.append(record['order_no'])
            record['scheduled_delivery_date'] = record['scheduled_delivery_date'].strftime("%Y-%m-%d")
            if record['scheduled_delivery_date'] not in delivery_dates:
                delivery_dates.append(record['scheduled_delivery_date'])

            if record['id'] in mfd_packs:
                mfd_pack_delivery_date_dict[record['id']] = record['scheduled_delivery_date']

            else:
                if record['scheduled_delivery_date'] not in automatic_delivery_date_pack_dict.keys():
                    automatic_delivery_date_pack_dict[record['scheduled_delivery_date']] = list()

                automatic_delivery_date_pack_dict[record['scheduled_delivery_date']].append(record['id'])

        print("automatic_delivery_date_pack_dict {}".format(automatic_delivery_date_pack_dict))
        print("mfd_pack_delivery_date_dict {}".format(mfd_pack_delivery_date_dict))
        print("mfd_packs: {}".format(mfd_packs))

        sorted_mfd_packs_delivery_date = dict()
        for pack in mfd_packs:
            sorted_mfd_packs_delivery_date[pack] = mfd_pack_delivery_date_dict[pack]

        for each_delivery_date in delivery_dates:
            if len(updated_mfd_pack_sequence):
                for pack, date in sorted_mfd_packs_delivery_date.items():
                    if pack in updated_mfd_pack_sequence:
                        if date <= each_delivery_date:
                            updated_pack_list.append(pack)
                            updated_mfd_pack_sequence.remove(pack)
                        else:
                            break

            if each_delivery_date in automatic_delivery_date_pack_dict.keys():
                for each_pack in automatic_delivery_date_pack_dict[each_delivery_date]:
                    updated_pack_list.append(each_pack)

        if len(updated_mfd_pack_sequence):
            for pack_ in updated_mfd_pack_sequence:
                updated_pack_list.append(pack_)

        if len(updated_pack_list) != len(order_number_list):
            print("Pack list and order list does not match")
            return False

        print('before check')
        update_status = change_pack_sequence_mfd(updated_pack_list, order_number_list)
        logger.info(update_status)

        return True

    except (InternalError, IntegrityError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except ValueError as e:
        return error(2005, str(e))
    except Exception as e:
        logger.error(e)
        return e


def update_sequence_for_mfd_packs(batch_id: int) -> bool:
    """
    Function to update sequence for mfd packs
    @param batch_id:
    @return:
    """
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    try:
        mfd_pack_dict = db_get_batch_mfd_packs(batch_id)
        mfd_packs = [int(item['mfd_pack']) for item in mfd_pack_dict]
        print('mfd_pack_ids: {}'.format(mfd_packs))

        if len(mfd_packs):
            print("MFD packs while import {}".format(mfd_packs))
            order_no = 1
            updated_pack_list = list()
            order_number_list = list()
            query = PackDetails.select(PackDetails.id,
                                       PackDetails.order_no,
                                       fn.DATE(PackHeader.scheduled_delivery_date).alias(
                                           'scheduled_delivery_date')).dicts() \
                .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
                .where(PackDetails.batch_id == batch_id,
                       PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                       ) \
                .order_by(PackDetails.order_no)
            for record in query:
                updated_pack_list.append(record['id'])
                order_number_list.append(order_no)
                order_no += 1
            print('before packs {} & order_number_list {}'.format(updated_pack_list, order_number_list))
            update_status = change_pack_sequence_mfd(updated_pack_list, order_number_list)
            print('update_pack_count {}'.format(update_status))
            pack_order_update_status = update_pack_sequence_of_mfd_packs(batch_id, mfd_packs)
            print("pack_order_update_status {}".format(pack_order_update_status))
            if not pack_order_update_status:
                return False

        else:
            return True

    except ValueError as e:
        return error(2005, str(e))
    except Exception as e:
        logger.exception("Exception in updating pack sequence: ")
        return error(1001, e)


if __name__ == '__main__':
    output = update_sequence_for_mfd_packs(batch_id=27)
    print('output: {}'.format(output))
