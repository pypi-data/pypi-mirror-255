import functools
import operator
import datetime
import settings
from datetime import datetime as dt

from peewee import fn, JOIN_LEFT_OUTER, IntegrityError, InternalError, DoesNotExist, JOIN_INNER
from playhouse.shortcuts import case, cast

from dosepack.utilities.utils import log_args_and_response
from src.model.model_code_master import CodeMaster
from src.model.model_pack_details import PackDetails
from src.model.model_pack_user_map import PackUserMap
from src.model.model_session import Session
from src.model.model_batch_master import BatchMaster
from src.model.model_session_meta import SessionMeta
from src.model.model_session_module_master import SessionModuleMaster
from src.model.model_session_module_meta import SessionModuleMeta
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader

logger = settings.logger


@log_args_and_response
def get_batch_preprocess_data_dao() -> list:
    """
    Get batch details, process details, and time spent on that screen of the preprocessing module for each batch
    @return: list
    """

    try:
        # time details for preprocessing module
        session_details = (Session.select(Session.identifier_value,
                                          Session.start_time,
                                          Session.end_time,
                                          Session.active_time,
                                          Session.system_id,
                                          Session.company_id,
                                          SessionModuleMaster.screen_name.alias('process'),
                                          (SessionMeta.value * SessionModuleMeta.time_per_unit).alias(
                                              'ideal_time'))
                           .join(CodeMaster, on=(CodeMaster.id == Session.identifier_key))
                           .join(SessionModuleMaster, on=(SessionModuleMaster.id == Session.session_module_id))
                           .join(SessionMeta, on=(SessionMeta.session_id == Session.id))
                           .join(SessionModuleMeta,
                                 on=((SessionModuleMeta.id == SessionMeta.session_module_meta_id) & (
                                         SessionModuleMeta.session_module_id == SessionModuleMaster.id)))
                           .where(SessionModuleMaster.session_module_type_id == 28)).dicts()

        session_details = session_details.alias('t_sess')

        # get packs done only by system
        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        done_system_packs = (PackDetails.select(PackDetails.batch_id.alias('batch_id'),
                                                fn.COUNT(PackDetails.id).alias('number_of_packs'))
                             .join(PackUserMap, JOIN_LEFT_OUTER, on=(PackDetails.id == PackUserMap.pack_id))
                             .where((PackDetails.pack_status == 5) & (PackUserMap.pack_id.is_null()) &
                                    (fn.DATE(PackDetails.filled_date) == yesterday))
                             .group_by(PackDetails.batch_id)).dicts()

        done_system_packs = done_system_packs.alias('t_packs')

        # get batch name for these packs
        data = list()
        preprocessing_details = (BatchMaster.select(
                                                    fn.MIN(session_details.c.start_time).alias('start_time'),
                                                    fn.MAX(session_details.c.end_time).alias('end_time'),
                                                    fn.SUM(session_details.c.active_time).alias('actual_time_taken'),
                                                    session_details.c.system_id,
                                                    fn.MIN(session_details.c.company_id).alias('company_id'),
                                                    session_details.c.process,
                                                    session_details.c.ideal_time,
                                                    BatchMaster.name.alias('batch'),
                                                    done_system_packs.c.batch_id.alias('batch_id'),
                                                    fn.MAX(done_system_packs.c.number_of_packs).alias('number_of_packs'))
                                 .from_(session_details)
                                 .join(done_system_packs,
                                       on=(session_details.c.identifier_value == done_system_packs.c.batch_id))
                                 .join(BatchMaster, on=(BatchMaster.id == session_details.c.identifier_value))
                                 .group_by(session_details.c.system_id, session_details.c.process, BatchMaster.id))

        for row in preprocessing_details.dicts():
            data.append(row)
        return data
    except (IntegrityError, InternalError, DoesNotExist) as e:
        logger.error("error in get_batch_preprocess_data_dao:  {}".format(e))
        raise


@log_args_and_response
def get_pack_details_by_date_resource(last_fetch_id=0):
    """
    Function to get dictionary of new last_fetch_id and records containing date, resource, resource_type level
    data about number of packs, pills, and total time taken by that resource to fill those many packs

    @param last_fetch_id: pack id of the last record fetched from PackDetails
    @return: list
    """
    try:
        # getting pill counts for each pack
        pills_cnt = SlotHeader.select(
                                        SlotHeader.pack_id.alias('pack_id'),
                                        fn.SUM(SlotDetails.quantity).alias('qty')) \
                                .join(SlotDetails, JOIN_INNER, on=(SlotHeader.id == SlotDetails.slot_id)) \
                                .group_by(SlotHeader.pack_id).alias('pills_cnt')

        # filters
        system_deploy_date = '2019-08-01'
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        clauses = []
        c1 = PackDetails.filled_date.is_null(False)
        c2 = (PackDetails.pack_status == 5) | ((PackDetails.pack_status == 8) & (PackUserMap.pack_id.is_null()))
        c3 = cast(PackDetails.filled_date, 'DATE') >= cast(dt.strptime(system_deploy_date, '%Y-%m-%d'), 'DATE')

        c4 = (PackDetails.id > last_fetch_id)
        c5 = (fn.DATE(PackDetails.filled_date) == yesterday)
        clauses.append(c1)
        clauses.append(c2)
        clauses.append(c3)

        clauses.append(c4)
        clauses.append(c5)

        # case when for resource
        res_tuple = [(((PackDetails.pack_status == 5) & (PackUserMap.pack_id.is_null())),
                      fn.CONCAT('system', ' ', PackDetails.system_id))]
        resource_case = case(None, res_tuple, PackDetails.filled_by)

        # case when for resource_type
        res_type_tuple = [(((PackDetails.pack_status == 5) & (PackUserMap.pack_id.is_null())), 'system')]
        res_type_case = case(None, res_type_tuple, 'user')

        # required data for pharma manual view

        pharma_manual_data = PackDetails.select(fn.COUNT(PackDetails.id).alias('packs'),
                                                cast(PackDetails.filled_date, 'DATE').alias('date'),
                                                resource_case.alias('resource'),
                                                res_type_case.alias('resource_type'),
                                                PackDetails.company_id.alias('company'),
                                                case(None,
                                                     [(res_type_case == 'user', fn.SUM(PackDetails.fill_time)),
                                                      (res_type_case == 'system', None)], None).alias('time'),
                                                fn.SUM(pills_cnt.c.qty).alias('pills')) \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=(PackDetails.id == PackUserMap.pack_id)) \
            .join(pills_cnt, JOIN_INNER, on=(PackDetails.id == pills_cnt.c.pack_id)) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(cast(PackDetails.filled_date, 'DATE'), resource_case, res_type_case, PackDetails.company_id)

        records = []
        for row in pharma_manual_data.dicts():
            records.append(row)

        updated_last_fetch_id = PackDetails.select(fn.MAX(PackDetails.id).alias('max_pack_id')).get()

        response = {'records': records, 'last_fetch_id': updated_last_fetch_id.max_pack_id}

        return response
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_pack_details_by_date_resource:  {}".format(e))
        raise


@log_args_and_response
def get_all_system_packs_data():
    """
    Function to get info of all packs that are done and processed by the system
    @return: list
    """

    try:
        # get pack ids, batch id, system id, company id, and batch name of packs that have status 5 (Done) and
        # that are filled by system

        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        query = (PackDetails.select(PackDetails.id.alias('pack_id'),
                                    PackDetails.batch_id,
                                    PackDetails.system_id,
                                    PackDetails.company_id,
                                    BatchMaster.name.alias('batch'))
                 .join(PackUserMap, JOIN_LEFT_OUTER, on=(PackDetails.id == PackUserMap.pack_id))
                 .join(BatchMaster, on=(BatchMaster.id == PackDetails.batch_id))
                 .where((PackDetails.pack_status == 5) & (PackUserMap.pack_id.is_null())
                 & (fn.DATE(PackDetails.filled_date) == yesterday)))

        data = list(query.dicts())

        return data
    except (InternalError, IntegrityError) as e:
        logger.error("error in get_all_system_packs_data:  {}".format(e))
        raise
