# from future.backports import OrderedDict
from collections import OrderedDict
from datetime import datetime

import dateutil

import settings
from peewee import InternalError, IntegrityError, DoesNotExist, fn, DataError, SQL, JOIN_LEFT_OUTER

from dosepack.base_model.base_model import db, BaseModel
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import log_args_and_response, get_current_date_time
from src import constants
from src.constants import MFD_CANISTER_SKIPPED_STATUS, MFD_DRUG_SKIPPED_STATUS
from src.dao.misc_dao import get_system_setting_by_system_id
from src.dao.reserve_canister_dao import db_delete_reserved_canister
from src.model.model_batch_change_tracker import BatchChangeTracker
from src.dao.reserve_canister_dao import db_update_available_canister, db_update_available_canister_pack_queue
from src.model.model_code_master import CodeMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_batch_master import BatchMaster
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_user_map import PackUserMap
from src.model.model_reserved_canister import ReservedCanister
from src.service.misc import get_weekdays

logger = settings.logger


@log_args_and_response
def get_batch_status(batch_id: int) -> int:
    try:
        return BatchMaster.db_get_batch_status(batch_id=batch_id)
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_batch_status {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_batch_status {}".format(e))
        raise


@log_args_and_response
def db_batch_import_status(batch_id):
    try:
        return BatchMaster.db_is_imported(batch_id)
    except (IntegrityError, InternalError, Exception) as e:
        logger.error("error in db_batch_import_status {}".format(e))
        raise


@log_args_and_response
def get_system_id_from_batch_id(batch_id):
    """
        This function returns system_id for given batch
       """
    # todo: this function is currently being used at many place from pack.py and in other direct class-method
    #  remove this
    # function from this files once dao file is defined and use it in mfd.py
    try:
        system_id = BatchMaster.db_get_system_id_from_batch_id(batch_id)
        return system_id

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_system_id_from_batch_id {}".format(e))
        return e
    except Exception as e:
        logger.error("error in get_system_id_from_batch_id {}".format(e))
        raise


@log_args_and_response
def get_last_done_batch(company_id):
    try:
        logger.info("In get_last_done_batch")

        batch_id = None

        query = BatchMaster.select(BatchMaster.id).dicts() \
                .where(BatchMaster.status == settings.BATCH_PROCESSING_COMPLETE) \
                .order_by(BatchMaster.id.desc()) \
                .limit(1)

        for data in query:
            batch_id = data["id"]

        return batch_id

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_last_done_batch {}".format(e))
        return e
    except Exception as e:
        logger.error("error in get_last_done_batch {}".format(e))
        raise


@log_args_and_response
def get_current_batch(company_id):
    try:
        logger.info("In get_current_batch")

        batch_id = None
        order_list = []
        order_list.append(SQL('FIELD(status,{},{},{}, {}, {}, {})'.format(settings.BATCH_IMPORTED,
                                                                          settings.BATCH_CANISTER_TRANSFER_DONE,
                                                                       settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
                                                                       settings.BATCH_MFD_USER_ASSIGNED,
                                                                       settings.BATCH_ALTERNATE_DRUG_SAVED,
                                                                       settings.BATCH_PENDING)))
        query = BatchMaster.select(BatchMaster.id,
                                   BatchMaster.status.alias("status")).dicts() \
                .where(BatchMaster.status.not_in([settings.BATCH_DELETED, settings.BATCH_PROCESSING_COMPLETE])) \
                .group_by(BatchMaster.status) \
                .order_by(*order_list) \
                .limit(1)

        for data in query:
            batch_id = data["id"]

        return batch_id

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_current_batch {}".format(e))
        return e
    except Exception as e:
        logger.error("error in get_current_batch {}".format(e))
        raise

@log_args_and_response
def db_get_last_imported_batch_by_system_dao(status: int, system_id: int):
    try:
        return BatchMaster.db_get_last_imported_batch_by_system(status=status, system_id=system_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_get_last_imported_batch_by_system_dao {}".format(e))
        raise


@log_args_and_response
def db_update_mfd_status(batch, mfd_status, user_id):
    """ set or update mfd status of batch id """
    try:
        status = BatchMaster.update(mfd_status=mfd_status,
                                    modified_by=user_id,
                                    modified_date=get_current_date_time()) \
            .where(BatchMaster.id == batch).execute()
        return status
    except (InternalError, IntegrityError) as e:
        logger.error("error in db_update_mfd_status {}".format(e))
        raise
    except Exception as e:
        logger.error("error in db_update_mfd_status {}".format(e))
        raise

@log_args_and_response
def db_update_mfd_skip(mfd_analysis_ids, mfd_analysis_detail_ids, user_id):
    """ set status for mfd """
    try:
        status1 = MfdAnalysis.update(status_id=MFD_CANISTER_SKIPPED_STATUS,
                                     modified_by=user_id,
                                     modified_date=get_current_date_time()) \
            .where(MfdAnalysis.id << mfd_analysis_ids).execute()

        status2 = MfdAnalysisDetails.update(status_id=MFD_DRUG_SKIPPED_STATUS,
                                            modified_by=user_id,
                                            modified_date=get_current_date_time()) \
            .where(MfdAnalysisDetails.id << mfd_analysis_detail_ids).execute()
        return status1, status2

    except (InternalError, IntegrityError) as e:
        logger.error("error in db_update_mfd_status {}".format(e))
        raise
    except Exception as e:
        logger.error("error in db_update_mfd_status {}".format(e))
        raise


@log_args_and_response
def get_progress_batch_id(system_id: int):
    """
    @return: batch id of batch which is in progress  'i.e' imported
    """
    try:
        batch_id = BatchMaster.db_get_latest_progress_batch_id(system_id=system_id)
        return batch_id

    except DoesNotExist as e:
        logger.error("error in get_progress_batch_id {}".format(e))
        logger.info("get_progress_batch_id: No batch is imported")
        return None

    except (InternalError, IntegrityError, Exception) as e:
        logger.error("Error in get_progress_batch_id: {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("error in get_progress_batch_id {}".format(e))
        raise


@log_args_and_response
def get_top_batch_id(system_id: int):
    """
    returns batch id of batch which is going to be imported next
    :param system_id:
    :return:
    """
    try:
        batch_id = BatchMaster.db_get_top_batch_id(system_id=system_id)

        logger.info("In get_top_batch_id: batch_id {}".format(batch_id))
        return batch_id

    except DoesNotExist as e:
        logger.error("error in get_top_batch_id {}".format(e))
        return None

    except (InternalError, IntegrityError) as e:
        logger.error("error in get_top_batch_id {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("error in get_top_batch_id {}".format(e))
        raise


@log_args_and_response
def db_update_batch_status(batch_id, user_id, status):
    try:
        return BatchMaster.db_set_status(batch_id=batch_id, status=status, user_id=user_id)
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in db_update_batch_status {}".format(e))
        raise


def db_reset_batch(batch_id, user_id, status=settings.BATCH_PENDING):
    """
    Deletes relevant data to batch ID

    @param user_id:
    @param status:
    @param batch_id: batch ID of packs
    :return:
    """
    try:
        batch_record = BatchMaster.get(id=batch_id)
        if batch_record.status != settings.BATCH_PENDING:
            # if batch is pending than there will be no pack analysis data
            PackAnalysis.db_delete_pack_analysis(batch_id)
        # remove batch id for pack list
        # removing system_id too so data stay consistent
        PackDetails.update(batch_id=None,
                           system_id=None) \
            .where(PackDetails.batch_id == batch_id).execute()
        BatchMaster.db_set_status(batch_id, status, user_id)
        db_delete_reserved_canister(batch_id=batch_id)
    except (InternalError, IntegrityError) as e:
        logger.error("error in db_reset_batch {}".format(e))
        raise


def get_batch_record(batch_id):
    try:
        batch_record = BatchMaster.get(id=batch_id)
        return batch_record
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_batch_record {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_batch_record {}".format(e))
        raise


@log_args_and_response
def db_update_batch_status_from_create_batch(status, batch_id_list, progress_batch_id=None, batch_packs=None):
    """

    @param status:
    @param batch_id_list:
    @param progress_batch_id:
    @param batch_packs:
    @return:
    """
    try:
        with db.transaction():
            if int(status) == settings.BATCH_IMPORTED:
                # If batch is imported, update reserved canister
                db_update_available_canister(batch_id_list[0])
                BatchMaster.update(imported_date=get_current_date_time()) \
                    .where(BatchMaster.id << batch_id_list).execute()
            #
            # if int(status) == settings.BATCH_MERGED:
            #     db_update_batch_id_after_merged(batch_id_list[0], progress_batch_id, batch_packs)

            if int(status) == settings.BATCH_PROCESSING_COMPLETE:
                # truncating GuidedTracker Table in batch completion
                # todo-uncomment below when we change structure of guided_transfer_cycle_history
                # guided_tracker_changes = delete_from_guided_tracker(batch_id=batch_id)
                # if guided_tracker_changes:
                #     print("Guided Tracker table cleared for batch :{}".format(batch_id))

                #todo - commented because we need to remove it while removing packs from pack queue

                # db_delete_reserved_canister(batch_id=batch_id)
                pending_packs = PackDetails.select(PackDetails.id).dicts() \
                    .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id) \
                    .where(PackDetails.batch_id << batch_id_list,
                           PackDetails.pack_status << [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS],
                           PackUserMap.id.is_null(True))
                pending_pack_ids = [pack['id'] for pack in pending_packs]
                if pending_pack_ids:
                    logger.info("Marking packs as done at batch end for packs having "
                                "pending_progress_status: {}".format(pending_pack_ids))
                    # update_status = PackDetails.update(pack_status=settings.DONE_PACK_STATUS,
                    #                                    modified_date=get_current_date_time()) \
                    #     .where(PackDetails.id << pending_pack_ids).execute()

            BatchMaster.update(status=status) \
                .where(BatchMaster.id << batch_id_list).execute()

    except (InternalError, IntegrityError) as e:
        logger.error("error in db_update_batch_status_from_create_batch {}".format(e))
        raise
    except Exception as e:
        logger.error("error in db_update_batch_status_from_create_batch {}".format(e))
        raise


def update_batch_pack_status_create_batch(batch_id, system_id, user_id, batch_name, batch_record, pack_list, pack_orders):
    try:
        with db.transaction():
            if not batch_id:
                status = settings.BATCH_PENDING
                record = BaseModel.db_create_record({
                    'name': batch_name,
                    'system_id': system_id,
                    'status': status,
                    'created_by': user_id,
                    'modified_by': user_id,
                }, BatchMaster, get_or_create=False)
                batch_id = record.id
            else:  # update batch data
                status = batch_record.status.id
                update_dict = {
                    'name': batch_name,
                    'system_id': system_id,
                    'modified_date': get_current_date_time(),
                    'modified_by': user_id
                }
                BatchMaster.update(**update_dict) \
                    .where(BatchMaster.id == batch_id).execute()
            # if pack list provided, update pack order
            PackDetails.db_update_pack_order_no({
                'pack_ids': ','.join(list(map(str, pack_list))),
                'order_nos': ','.join(list(map(str, pack_orders))),
                'system_id': system_id
            })
            update_pack_dict = {
                'batch_id': batch_id,
                'modified_date': get_current_date_time(),
                'modified_by': user_id,
                'system_id': system_id
            }
            PackDetails.update(**update_pack_dict) \
                .where(PackDetails.id << pack_list).execute()

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_batch_pack_status_create_batch {}".format(e))
        raise
    except Exception as e:
        logger.error("error in update_batch_pack_status_create_batch {}".format(e))
        raise


def db_update_batch_status_from_create_multi_batch(status, batch_id):
    try:
        with db.transaction():
            if int(status) == settings.BATCH_IMPORTED:
                # If batch is imported, update reserved canister
                db_update_available_canister(batch_id)
            if int(status) == settings.BATCH_PROCESSING_COMPLETE:
                db_delete_reserved_canister(batch_id=batch_id)
            BatchMaster.update(status=status) \
                .where(BatchMaster.id == batch_id).execute()
    except (InternalError, IntegrityError) as e:
        logger.error("error in db_update_batch_status_from_create_multi_batch {}".format(e))
        raise


@log_args_and_response
def update_batch_pack_status_create_multi_batch(batch_id, system_id, user_id, batch_name, status, pack_list, pack_orders, scheduled_start_time, estimated_processing_time):
    try:
        with db.transaction():
            if not batch_id:
                record = BaseModel.db_create_record({
                    'name': batch_name,
                    'system_id': system_id,
                    'status': status,
                    'created_by': user_id,
                    'modified_by': user_id,
                    'estimated_processing_time': estimated_processing_time,
                    'scheduled_start_time': scheduled_start_time
                }, BatchMaster, get_or_create=False)
                batch_id = record.id
            else:  # update batch data
                update_dict = {
                    'name': batch_name,
                    'system_id': system_id,
                    'modified_date': get_current_date_time(),
                    'modified_by': user_id
                }
                BatchMaster.update(**update_dict) \
                    .where(BatchMaster.id == batch_id).execute()
                # if pack list provided, update pack order
            update_pack_dict = {
                'batch_id': batch_id,
                'modified_date': get_current_date_time(),
                'modified_by': user_id,
                'system_id': system_id
            }
            logger.info("pack details update info : " + str(update_pack_dict))

            PackDetails.update(**update_pack_dict) \
                .where(PackDetails.id << pack_list).execute()

            PackDetails.db_update_pack_order_no({'pack_ids': ','.join(list(map(str, pack_list))),
                                                 'order_nos': ','.join(list(map(str, pack_orders))),
                                                 'system_id': system_id
                                                 })

        return status, batch_id

    except (InternalError, IntegrityError) as e:
        logger.error("error in update_batch_pack_status_create_multi_batch {}".format(e))
        raise
    except Exception as e:
        logger.error("error in update_batch_pack_status_create_multi_batch {}".format(e))
        raise


def db_get_batch_id_from_system(system_id):
    try:
        batch_ids = BatchMaster.db_get_batch_id(system_id)
        return batch_ids

    except (InternalError, IntegrityError) as e:
        logger.error("error in db_get_batch_id_from_system {}".format(e))
        raise
    except Exception as e:
        logger.error("error in db_get_batch_id_from_system {}".format(e))
        raise


@log_args_and_response
def save_batch_change_tracker_data(user_id: int, action_id: int, params: dict, packs_affected: list, batch_id: int or None = None) -> bool:
    """
    Function to save data in batch change tracker
    @param batch_id:
    @param user_id:
    @param action_id:
    @param params:
    @param packs_affected:
    @return:
    """
    try:
        status = BatchChangeTracker.db_save(batch_id=batch_id,
                                            user_id=user_id,
                                            action_id=action_id,
                                            params=params,
                                            packs_affected=packs_affected)
        return status

    except (InternalError, IntegrityError) as e:
        logger.error("error in save_batch_change_tracker_data {}".format(e))
        print("Error in save_batch_change_tracker_data: ", str(e))
        raise e

    except Exception as e:
        print("Exception in save_batch_change_tracker_data: ", str(e))
        raise e


@log_args_and_response
def set_batch_status_dao(batch_id: int, status: int, user_id: int) -> bool:
    """
    Function to set batch status
    @param status:
    @param batch_id:
    @param user_id:
    @return:
    """
    try:
        batch_status = BatchMaster.db_set_status(batch_id=batch_id, status=status, user_id=user_id)
        return batch_status

    except (InternalError, IntegrityError) as e:
        logger.error("error in set_batch_status_dao {}".format(e))
        print("Error in set_batch_status_dao: ", str(e))
        raise

    except Exception as e:
        print("Exception in set_batch_status_dao: ", str(e))


@log_args_and_response
def get_batch_id_from_pack_list(pack_ids):
    try:
        query = PackDetails.select(PackDetails.batch_id, PackDetails.system_id).where(
            PackDetails.id << pack_ids).dicts().get()
        return query['batch_id'], query['system_id']
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return 0, 0
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_batch_id_from_pack_list {}".format(e))
        return error(2001)


@log_args_and_response
def update_scheduled_start_date_for_next_batches(pack_ids):
    try:
        with db.transaction():
            batch_id, system_id = get_batch_id_from_pack_list(pack_ids)
            pack_count = get_pack_count_by_batch(batch_id)
            batch_schedule_date_dict = {}
            previous_start_date = 0
            if pack_count == 0:
                batch_start_date_dict = get_next_pending_batches(system_id, batch_id)
                if len(batch_start_date_dict) > 1:
                    count = 1
                    for batch, start_date in batch_start_date_dict.items():
                        if batch == batch_id:
                            # batch_schedule_date_dict[batch] = start_date
                            previous_start_date = start_date
                            count += 1
                            continue
                        if count == 2:
                            batch_schedule_date_dict[batch] = previous_start_date
                            total_packs = get_pack_count_by_batch(batch)
                            count += 1
                            continue
                        # total_packs = get_pack_count_by_batch(batch)
                        system_timings = get_system_setting_by_system_id(system_id=system_id)
                        previous_start_date = get_batch_scheduled_start_date(system_timings, total_packs,
                                                                             previous_start_date,
                                                                             batch)
                        batch_schedule_date_dict[batch] = previous_start_date
                        date_status = BatchMaster.update(scheduled_start_time=previous_start_date).where(
                            BatchMaster.id == batch).execute()
                        if count == len(batch_start_date_dict):
                            break
                        count += 1
                        total_packs = get_pack_count_by_batch(batch)

                update_status = BatchMaster.update(status=settings.BATCH_DELETED).where(
                    BatchMaster.id == batch_id).execute()

                # this function call deletes the data from guided tracker when the batch is marked as deleted
                # todo- uncomment this when we change join of guided_transfer_cycle_history table
                # delete_from_guided_tracker(batch_id=batch_id)
                return update_status
            return 1
    except (InternalError, InternalError, Exception) as e:
        logger.error("error in update_scheduled_start_date_for_next_batches {}".format(e))


@log_args_and_response
def get_system_wise_batch_id(system_list=None):
    system_max_batch_id_dict = {}
    try:
        if system_list:
            query = BatchMaster.select(BatchMaster.system_id, fn.MAX(BatchMaster.id).alias('last_batch'))\
                .where(BatchMaster.status.not_in([settings.BATCH_PROCESSING_COMPLETE, settings.BATCH_DELETED, settings.BATCH_MERGED]),
                                                 BatchMaster.system_id << system_list)\
                .group_by(BatchMaster.system_id)
        else:
            query = BatchMaster.select(BatchMaster.system_id, fn.MAX(BatchMaster.id).alias('last_batch')) \
                .where(BatchMaster.status.not_in([settings.BATCH_PROCESSING_COMPLETE, settings.BATCH_DELETED])) \
                .group_by(BatchMaster.system_id)

        for record in query.dicts():
            system_max_batch_id_dict[record['system_id']] = record['last_batch']
        return system_max_batch_id_dict
    except (InternalError, IntegrityError, Exception) as e:
        logger.error("error in get_system_wise_batch_id {}".format(e))
        raise


@log_args_and_response
def get_next_pending_batches(system_id, batch_id):
    try:
        batch_start_date_dict = OrderedDict()
        query = BatchMaster.select(BatchMaster.id, BatchMaster.scheduled_start_time).where(BatchMaster.id >= batch_id,
                                                                                           BatchMaster.status == settings.BATCH_PENDING,
                                                                                           BatchMaster.system_id == system_id)
        for record in query.dicts():
            batch_start_date_dict[record["id"]] = record["scheduled_start_time"]
        return batch_start_date_dict
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_next_pending_batches {}".format(e))
        return error(2001)


@log_args_and_response
def get_batch_scheduled_start_date(system_timings, total_packs, start_date, batch_id):
    AUTOMATIC_PER_DAY_HOURS = int(system_timings['AUTOMATIC_PER_DAY_HOURS'])
    AUTOMATIC_PER_HOUR = int(system_timings['AUTOMATIC_PER_HOUR'])
    AUTOMATIC_SATURDAY_HOURS = int(system_timings['AUTOMATIC_SATURDAY_HOURS'])
    AUTOMATIC_SUNDAY_HOURS = int(system_timings['AUTOMATIC_SUNDAY_HOURS'])
    batch_date_day_dict = {}
    batch_start_date_dict = {}
    rem_cap = 0
    processing_hours = 0
    # b = "2015-10-28 16:09:59"

    last_batch_start_date = dateutil.parser.parse(str(start_date)).date()
    last_batch_start_date_str = str(last_batch_start_date)  # this is in date format
    last_batch_packs_count = total_packs  # will take from db

    batch_date_day_dict[last_batch_start_date] = get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                              int(last_batch_start_date_str.split('-')[1]),
                                                              int(last_batch_start_date_str.split('-')[2]))
    while last_batch_packs_count > 0:
        last_batch_start_date_str = str(last_batch_start_date)
        batch_date_day_dict[last_batch_start_date] = get_weekdays(int(last_batch_start_date_str.split('-')[0]),
                                                                  int(last_batch_start_date_str.split('-')[1]),
                                                                  int(last_batch_start_date_str.split('-')[2]))
        if batch_date_day_dict[last_batch_start_date] == settings.SATURDAY:
            if AUTOMATIC_SATURDAY_HOURS == 0:
                last_batch_start_date += datetime.timedelta(days=1)
            elif last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS
                last_batch_start_date += datetime.timedelta(days=1)
                processing_hours += AUTOMATIC_SATURDAY_HOURS
                if last_batch_packs_count == 0:
                    # scheduled_end_date = last_batch_start_date - datetime.timedelta(days=1)
                    # self.batch_processing_time_dict[self.batch_count] = processing_hours
                    batch_start_date_dict[batch_id] = last_batch_start_date
            elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SATURDAY_HOURS:
                # rem_cap = AUTOMATIC_PER_HOUR*AUTOMATIC_SATURDAY_HOURS - batch_packs_count
                # if rem_cap <= AUTOMATIC_PER_HOUR:
                #     last_batch_start_date += datetime.timedelta(days=1)
                processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                last_batch_packs_count = 0
                scheduled_end_date = last_batch_start_date
                batch_start_date_dict[batch_id] = last_batch_start_date
                # self.batch_processing_time_dict[self.batch_count] = processing_hours
        elif batch_date_day_dict[last_batch_start_date] == settings.SUNDAY:
            if AUTOMATIC_SUNDAY_HOURS == 0:
                last_batch_start_date += datetime.timedelta(days=1)
            elif last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS and AUTOMATIC_SUNDAY_HOURS > 0:
                last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS
                last_batch_start_date += datetime.timedelta(days=1)
                processing_hours += AUTOMATIC_SUNDAY_HOURS
                if last_batch_packs_count == 0:
                    # scheduled_end_date = last_batch_start_date - datetime.timedelta(days=1)
                    # self.batch_processing_time_dict[self.batch_count] = processing_hours
                    batch_start_date_dict[batch_id] = last_batch_start_date
            elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_SUNDAY_HOURS:
                last_batch_packs_count = 0
                processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                last_batch_packs_count = 0
                scheduled_end_date = last_batch_start_date
                batch_start_date_dict[batch_id] = last_batch_start_date
                # self.batch_processing_time_dict[self.batch_count] = processing_hours
        else:
            if last_batch_packs_count >= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                last_batch_packs_count -= AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS
                last_batch_start_date += datetime.timedelta(days=1)
                processing_hours += AUTOMATIC_PER_DAY_HOURS
                if last_batch_packs_count == 0:
                    # scheduled_end_date = last_batch_start_date - datetime.timedelta(days=1)
                    # self.batch_processing_time_dict[self.batch_count] = processing_hours
                    batch_start_date_dict[batch_id] = last_batch_start_date
            elif last_batch_packs_count < AUTOMATIC_PER_HOUR * AUTOMATIC_PER_DAY_HOURS:
                processing_hours += last_batch_packs_count / AUTOMATIC_PER_HOUR
                last_batch_packs_count = 0
                scheduled_end_date = last_batch_start_date
                batch_start_date_dict[batch_id] = last_batch_start_date
    return batch_start_date_dict[batch_id]


@log_args_and_response
def get_pack_count_by_batch(batch_id):
    try:
        query = PackDetails.select(fn.COUNT(PackDetails.id).alias('pack_count')).where(PackDetails.batch_id == batch_id,
                                                                                       PackDetails.pack_status == settings.PENDING_PACK_STATUS).dicts().get()
        return query['pack_count']
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_pack_count_by_batch {}".format(e))
        return error(2001)


def db_is_imported(batch_id):
    """
    Returns True if batch is imported, False otherwise
    if batch does not exist returns None
    :param batch_id: int
    :return: bool | None
    """
    try:
        batch_status = BatchMaster.select(CodeMaster.id).dicts() \
            .join(CodeMaster, on=CodeMaster.id == BatchMaster.status) \
            .where(BatchMaster.id == batch_id).get()
        return batch_status['id'] == settings.BATCH_IMPORTED
    except DoesNotExist as e:
        logger.error("error in db_is_imported {}".format(e))
        return None
    except (IntegrityError, InternalError) as e:
        logger.error("error in db_is_imported {}".format(e))
        raise


def get_system_status_dao(system_id_list, non_idle_status_list):
    try:
        query = BatchMaster.select(BatchMaster.system_id) \
            .where(
            BatchMaster.system_id << system_id_list,
            BatchMaster.status.not_in(non_idle_status_list)
        )
        return query.dicts()
    except DoesNotExist as e:
        logger.error("error in get_system_status_dao {}".format(e))
        return None
    except (IntegrityError, InternalError) as e:
        logger.error("error in get_system_status_dao {}".format(e))
        raise


def db_delete_reserved_canister(batch_id, device_ids=None):
    """
    Deletes canisters for given batch id and given robot ids
    This makes canister available for other systems and canister recommendation will consider this canister.

    @param batch_id:
    @param device_ids:
    :return:
    """
    try:
        if device_ids:
            query = PackAnalysis.select(PackAnalysisDetails.canister_id).distinct() \
                .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id)
            canisters = query.where(PackAnalysis.batch_id == batch_id,
                                    PackAnalysisDetails.device_id << device_ids)
            return ReservedCanister.delete() \
                .where(ReservedCanister.canister_id << canisters) \
                .execute()
        else:
            return ReservedCanister.delete() \
                .where(ReservedCanister.batch_id == batch_id).execute()

    except (InternalError, IntegrityError) as e:
        logger.error("error in db_delete_reserved_canister {}".format(e))
        raise e


def validate_batch_id_dao(batch_id: int) -> int:
    try:
        return BatchMaster.db_validate_batch_id_dao(batch_id=batch_id)
    except(IntegrityError, InternalError, DoesNotExist) as e:
        logger.error(e)
        return False
    except Exception as e:
        logger.error(e)
        return False


@log_args_and_response
def check_batch_id_assign_for_packs(pack_list: list) -> int:
    """
    check batch id is already assign for packs or not
    """
    try:
        count = PackDetails.db_check_batch_id_assign_for_packs(pack_list=pack_list)
        return count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_batch_id_assign_for_packs {}".format(e))
        raise e


@log_args_and_response
def get_pack_ids_for_batch(batch_id):
    pack_ids = []
    try:
        query = PackDetails.select(PackDetails.id).dicts().where(PackDetails.batch_id == batch_id,
                                                                 PackDetails.pack_status == settings.PENDING_PACK_STATUS)
        for record in query:
            pack_ids.append(record["id"])
        return pack_ids

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in check_batch_id_assign_for_packs {}".format(e))
        raise e


@log_args_and_response
def db_update_batch_id_after_merged(batch_id, progress_batch_id, batch_packs):
    """

    @param batch_id: Batch which has came for merging
    @param progress_batch_id: Batch which is imported in pack queue
    @return:
    """
    try:
        if batch_packs:
            pack_details_update = PackDetails.update(previous_batch_id=batch_id, batch_id = progress_batch_id) \
                .where(PackDetails.id << batch_packs).execute()

            pack_analysis_update = PackAnalysis.update(batch_id=progress_batch_id) \
                .where(PackAnalysis.pack_id << batch_packs).execute()

            mfd_analysis_update = MfdAnalysis.update(batch_id=progress_batch_id) \
                .where(MfdAnalysis.batch_id == batch_id).execute()
        return True

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in db_update_batch_id_after_merged {}".format(e))
        raise e


@log_args_and_response
def update_batch_status_for_empty_pack_queue(pack_queue_count):

    '''
    @param pack_queue_count:
    @return:
    If pack queue is empty then update batch status from imported to batch_processing_complete and remove entry from
    ResevedCanisters if no batch is imported and canister recommendation is not done for any batch.
    '''

    try:
        batch_id_list = list()
        if not pack_queue_count:
            query = BatchMaster.select(BatchMaster.id).dicts()\
                .where(BatchMaster.status == settings.BATCH_IMPORTED)
            for batch in query:
                batch_id_list.append(batch['id'])
            if batch_id_list:
                logger.info("Inside update_batch_status_for_empty_pack_queue, updating batch_status to "
                            "batch_processing_complete for batch {}".format(batch_id_list))
                db_update_batch_status_from_create_batch(status=settings.BATCH_PROCESSING_COMPLETE, batch_id_list=batch_id_list)
            status = remove_from_reserved_canisters_for_empty_pack_queue()
            return True
        return False
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in update_batch_status_for_empty_pack_queue {}".format(e))
        raise e

    except Exception as e:
        logger.error("error in update_batch_status_for_empty_pack_queue {}".format(e))
        raise e


@log_args_and_response
def remove_from_reserved_canisters_for_empty_pack_queue():

    '''
        empty ReservedCanisters if pack queue is empty and no batch is imported and canister recommendation
        of any batch is not done.
    '''
    status = None
    try:

        logger.info("Inside remove_from_reserved_canisters_for_empty_pack_queue")
        batch_id_list = list()

        query = BatchMaster.select(BatchMaster.id).dicts() \
            .where(BatchMaster.status.in_([settings.BATCH_IMPORTED,
                                           settings.BATCH_CANISTER_TRANSFER_DONE,
                                           settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
                                           settings.BATCH_MFD_USER_ASSIGNED]))

        for record in query:
            batch_id_list.append(record['id'])

        if not batch_id_list:
            status = ReservedCanister.delete().execute()

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in remove_from_reserved_canisters_for_empty_pack_queue {}".format(e))
        raise e
