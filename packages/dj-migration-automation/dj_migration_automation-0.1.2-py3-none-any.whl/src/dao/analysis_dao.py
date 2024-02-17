import functools
import operator
from collections import defaultdict

from peewee import DoesNotExist, fn, JOIN_LEFT_OUTER, InternalError, IntegrityError, DataError
from playhouse.shortcuts import case

import settings
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import log_args_and_response
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_slot_details import SlotDetails
from src.model.model_zone_master import ZoneMaster
from src.service.misc import update_replenish_canisters_couch_db

logger = settings.logger


@log_args_and_response
def get_batch_drugs_dao(company_id, batch_id, system_id, number_of_packs, type_of_drug,
                replenish_required, extra_canister_data):
    try:
        pack_ids = None
        CanisterMasterAlias = CanisterMaster.alias()
        if not batch_id:
            try:
                batch_id = BatchMaster.select(BatchMaster.id).dicts() \
                    .where(BatchMaster.system_id == system_id,
                           BatchMaster.status == settings.BATCH_IMPORTED).order_by(BatchMaster.id.desc()).get()
            except DoesNotExist as e:
                logger.info(e, exc_info=True)
                return error(1020, 'Currently imported batch not found.')
            batch_id = batch_id['id']
        if number_of_packs:
            query = PackDetails.select(PackDetails.id).dicts() \
                .where(PackDetails.company_id == company_id,
                       PackDetails.batch_id == batch_id,
                       PackDetails.pack_status == settings.PENDING_PACK_STATUS) \
                .order_by(PackDetails.order_no).limit(number_of_packs)
            pack_ids = [item['id'] for item in query]

        filter_dict = {
            'canister_qty': fn.IF(CanisterMaster.id, fn.SUM(fn.FLOOR(SlotDetails.quantity)), 0),
            'manual_qty': fn.IF(CanisterMaster.id, fn.SUM(fn.MOD(SlotDetails.quantity, 1)),
                                fn.SUM(SlotDetails.quantity)),
            'total_req_qty': fn.SUM(SlotDetails.quantity)
        }
        clauses = list()
        clauses.append((PackDetails.batch_id == batch_id))
        clauses.append((PackDetails.company_id == company_id))
        clauses.append((PackDetails.pack_status == settings.PENDING_PACK_STATUS))
        if pack_ids:
            clauses.append((PackAnalysis.pack_id << pack_ids))
        # drug_list = dict()

        query = PackDetails.select(PackAnalysisDetails,
                                   DrugMaster,
                                   SlotDetails,
                                   fn.IF(type_of_drug == settings.DRUG_TYPE['canister'],
                                         filter_dict['canister_qty'],
                                         fn.IF(type_of_drug == settings.DRUG_TYPE['manual'],
                                               filter_dict['manual_qty'],
                                               filter_dict['total_req_qty'])).alias('required_quantity'),
                                   CanisterMaster,
                                   filter_dict['canister_qty'].alias('canister_qty'),
                                   filter_dict['total_req_qty'].alias('total_req_qty'),
                                   filter_dict['manual_qty'].alias('manual_qty'),
                                   fn.IF((filter_dict['canister_qty'] > CanisterMaster.available_quantity),
                                         True, False).alias('replenish_required'),
                                   fn.IF(((filter_dict['canister_qty'] - CanisterMaster.available_quantity) > 0),
                                         filter_dict['canister_qty'] - CanisterMaster.available_quantity, 0.0)
                                   .alias('replenish_qty')).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackAnalysis,
                  on=((PackAnalysis.pack_id == PackDetails.id) &
                      (PackDetails.batch_id == PackAnalysis.batch_id))) \
            .join(PackAnalysisDetails,
                  on=((PackAnalysisDetails.analysis_id == PackAnalysis.id)
                      & (PackAnalysisDetails.slot_id == SlotDetails.id))) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr, PackAnalysisDetails.canister_id) \
            .where(functools.reduce(operator.and_, clauses))
        if replenish_required == 1:
            query = query.having(filter_dict['canister_qty'] > CanisterMaster.available_quantity)
        elif replenish_required == 0:
            query = query.having(
                (filter_dict['canister_qty'] <= CanisterMaster.available_quantity) | (CanisterMaster.id.is_null(True)))
        if type_of_drug == settings.DRUG_TYPE['canister']:
            query = query.having(filter_dict['canister_qty'] > 0)
        elif type_of_drug == settings.DRUG_TYPE['manual']:
            query = query.having(filter_dict['manual_qty'] > 0)

        clauses.append((CanisterMasterAlias.active == settings.is_canister_active))
        clauses.append((CanisterMasterAlias.rfid.is_null(False)))

        query2 = PackDetails.select(PackAnalysisDetails,
                                    DrugMaster,
                                    SlotDetails,
                                    fn.IF(type_of_drug == settings.DRUG_TYPE['canister'],
                                          filter_dict['canister_qty'],
                                          fn.IF(type_of_drug == settings.DRUG_TYPE['manual'],
                                                filter_dict['manual_qty'],
                                                filter_dict['total_req_qty'])).alias('required_quantity'),
                                    CanisterMaster.id.alias('original_can_id'),
                                    CanisterMasterAlias,
                                    fn.IF(CanisterMasterAlias.id.is_null(False), True, False).alias('extra_can'),
                                    CanisterMasterAlias.id.alias('canister_id'),
                                    CanisterMasterAlias.id.alias('extra_can'),
                                    filter_dict['canister_qty'].alias('canister_qty'),
                                    filter_dict['total_req_qty'].alias('total_req_qty'),
                                    filter_dict['manual_qty'].alias('manual_qty'),
                                    fn.IF((filter_dict['canister_qty'] > CanisterMasterAlias.available_quantity),
                                          True, False).alias('replenish_required'),
                                    fn.IF(((filter_dict['canister_qty'] - CanisterMasterAlias.available_quantity) > 0),
                                          filter_dict['canister_qty'] - CanisterMasterAlias.available_quantity, 0.0)
                                    .alias('replenish_qty')).dicts() \
            .join(PackRxLink, on=PackRxLink.pack_id == PackDetails.id) \
            .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
            .join(PackAnalysis,
                  on=((PackAnalysis.pack_id == PackDetails.id) &
                      (PackDetails.batch_id == PackAnalysis.batch_id))) \
            .join(PackAnalysisDetails,
                  on=((PackAnalysisDetails.analysis_id == PackAnalysis.id)
                      & (PackAnalysisDetails.slot_id == SlotDetails.id))) \
            .join(DrugMaster, on=SlotDetails.drug_id == DrugMaster.id) \
            .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
            .join(CanisterMasterAlias, on=((CanisterMasterAlias.drug_id == SlotDetails.drug_id) &
                                           (CanisterMasterAlias.id != CanisterMaster.id))) \
            .join(ReservedCanister, on=ReservedCanister.canister_id != CanisterMasterAlias.id) \
            .where(functools.reduce(operator.and_, clauses)) \
            .group_by(CanisterMasterAlias.id)
        if replenish_required == 1:
            query2 = query2.having(filter_dict['canister_qty'] > CanisterMasterAlias.available_quantity)
        elif replenish_required == 0:
            query2 = query2.having((filter_dict['canister_qty'] <= CanisterMasterAlias.available_quantity) |
                                   (CanisterMaster.id.is_null(True)))
        if type_of_drug == settings.DRUG_TYPE['canister']:
            query2 = query2.having(filter_dict['canister_qty'] > 0)
        elif type_of_drug == settings.DRUG_TYPE['manual']:
            query2 = query2.having(filter_dict['manual_qty'] > 0)

        logger.info("inside get_batch_drugs_dao: {}".format(query2))

        canister_list = list()
        for rec in query2:
            canister_list.append(rec['canister_id'])

        logger.info("inside get_batch_drugs_dao: {}".format(canister_list))
        if not extra_canister_data:
            list_final = list(query)
        else:
            list_final = list(query) + list(query2)

        return pack_ids, list_final

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_batch_drugs_dao {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_batch_drugs_dao {}".format(e))
        raise


@log_args_and_response
def get_replenish_drugs_dao(batch_id, system_id, pack_orders, device_id):
    try:
        pack_status_list = [settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS]
        canister_data = dict()
        response_list = []

        clauses = list()
        clauses.append((PackDetails.system_id == system_id))
        clauses.append((PackDetails.pack_status << pack_status_list))
        clauses.append((PackAnalysis.batch_id == batch_id))
        clauses.append((PackAnalysisDetails.device_id.is_null(False)))
        if device_id:
            clauses.append((LocationMaster.device_id == device_id))

        try:
            _pack_orders = defaultdict(list)
            # min. processing order of pack in all robots  # 1 based index
            # convert robot wise pack orders to min order dict for packs
            for k, v in pack_orders.items():
                for pack_index, pack in enumerate(v):
                    _pack_orders[str(pack)].append(pack_index + 1)
            for pack, indexes in _pack_orders.items():
                _pack_orders[str(pack)] = min(indexes)

            _pack_orders = dict(_pack_orders)
            # sub_q = PackRxLink.select(PackRxLink.id.alias('pack_rx_id'),
            #                           PatientRx.drug_id.alias('drug_id'),
            #                           PackRxLink.pack_id.alias('pack_id'),
            #                           DrugMaster.formatted_ndc,
            #                           DrugMaster.txr) \
            #     .join(PatientRx,
            #           on=(PatientRx.id == PackRxLink.patient_rx_id)) \
            #     .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            #     .join(PackDetails, on=PackDetails.id == PackRxLink.pack_id) \
            #     .where(PackDetails.system_id == system_id,
            #            PackDetails.pack_status << pack_status_list,
            #            PackDetails.batch_id == batch_id) \
            #     .alias('pack_drugs')  # sub query to get pack drugs
            query = PackAnalysis.select(fn.SUM(SlotDetails.quantity).alias('total_qty'),
                                        CanisterMaster,
                                        DrugMaster,
                                        CanisterMaster.available_quantity,
                                        fn.IF(CanisterMaster.available_quantity < 0, 0,
                                              CanisterMaster.available_quantity).alias(
                                            'display_quantity'),
                                        PackAnalysis.pack_id,
                                        LocationMaster.device_id,
                                        SlotDetails.drug_id,
                                        PackAnalysisDetails.canister_id,
                                        LocationMaster.location_number,
                                        ContainerMaster.drawer_name.alias('drawer_number'),
                                        LocationMaster.display_location,
                                        ZoneMaster.id.alias('zone_id'),
                                        ZoneMaster.name.alias('zone_name'),
                                        DeviceLayoutDetails.id.alias('device_layout_id'),
                                        DeviceMaster.name.alias('device_name'),
                                        DeviceMaster.id.alias('device_id'),
                                        DeviceTypeMaster.device_type_name,
                                        DeviceTypeMaster.id.alias('device_type_id'),
                                        ContainerMaster.ip_address,
                                        ContainerMaster.secondary_ip_address
                                        ).dicts() \
                .join(PackAnalysisDetails, on=PackAnalysis.id == PackAnalysisDetails.analysis_id) \
                .join(SlotDetails, on=SlotDetails.pack_rx_id == PackAnalysisDetails.slot_id) \
                .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                .join(PackDetails, on=PackDetails.id == PackAnalysis.pack_id) \
                .join(CanisterMaster, on=CanisterMaster.id == PackAnalysisDetails.canister_id) \
                .join(LocationMaster, on=CanisterMaster.location_id == LocationMaster.id) \
                .join(ContainerMaster, on=ContainerMaster.id == LocationMaster.container_id) \
                .join(DeviceMaster, on=DeviceMaster.id == LocationMaster.device_id) \
                .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
                .join(DeviceLayoutDetails, JOIN_LEFT_OUTER, DeviceLayoutDetails.device_id == DeviceMaster.id) \
                .join(ZoneMaster, JOIN_LEFT_OUTER, DeviceLayoutDetails.zone_id == ZoneMaster.id) \
                .where(functools.reduce(operator.and_, clauses)) \
                .group_by(PackAnalysis.pack_id, SlotDetails.drug_id) \
                .order_by(PackDetails.order_no)
            for record in query:
                if record['canister_id'] not in canister_data:
                    canister_data[record['canister_id']] = {'canister_id': record['canister_id'],
                                                            'device_id': record['device_id'],
                                                            'device_name': record['device_name'],
                                                            'available_qty': record['available_quantity'],
                                                            'replenish_qty': record['available_quantity'],
                                                            'location_number': record['location_number'],
                                                            'display_location': record['display_location'],
                                                            'drug_name': record['drug_name'],
                                                            'strength': record['strength'],
                                                            'strength_value': record['strength_value'],
                                                            'ndc': record['ndc'],
                                                            'image_name': record['image_name'],
                                                            'color': record['color'],
                                                            'shape': record['shape'],
                                                            'imprint': record['imprint'],
                                                            'rfid': record['rfid'],
                                                            'drawer_number': record['drawer_number'],
                                                            }
                try:
                    check_replenish(
                        canister_data,
                        record['canister_id'],
                        record['total_qty'],
                        _pack_orders[str(record['pack_id'])]
                    )
                except KeyError as e:
                    pass  # skipping as pack is processed
                    # logger.info("Skip Replenish data check for pack {}"
                    #             .format(record["pack_id"]))
            for item in canister_data.values():
                if 'replenish' in item:
                    item['replenish_qty'] = float(abs(item['replenish_qty']))
                    response_list.append(item)
            response_list.sort(key=lambda _v: _v['replenish_order'])
            # update cdb
            logger.info(f"Inside get_replenish_drugs_dao : {response_list}")
            update_replenish_canisters_couch_db(response_list, system_id)
        except (InternalError, IntegrityError) as e:
            logger.error("error in get_replenish_drugs_dao {}".format(e))
            return error(2001)

        return response_list
    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("error in get_replenish_drugs_dao {}".format(e))
        raise
    except Exception as e:
        logger.error("error in get_replenish_drugs_dao {}".format(e))
        raise


def check_replenish(canister_data, canister_id, total_qty, pack_order):
    """
    takes dictionary of canister data and marks it for replenish using canister_id
    :param canister_data: dict {"some_canister_id": {'replenish_qty': 10}, ...}
    :param canister_id: int
    :param total_qty: float
    :param pack_order: int
    :return:
    """
    canister_data[canister_id]['replenish_qty'] -= total_qty
    if 'replenish' not in canister_data[canister_id] and canister_data[canister_id]['replenish_qty'] < 0:
        canister_data[canister_id]['replenish'] = True
        canister_data[canister_id]['replenish_qty'] = canister_data[canister_id]['replenish_qty']
        canister_data[canister_id]['replenish_order'] = pack_order


@log_args_and_response
def set_initial_pack_sequence(batch_id):
    try:
        query = PackDetails.select(PackDetails.id, PackDetails.order_no).where(
            PackDetails.pack_status.in_([settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS]),
            PackDetails.batch_id == batch_id,
            PackDetails.order_no.is_null(
                False)).order_by(
            PackDetails.order_no)

        pack_list = []
        for record in query.dicts():
            pack_list.append(record['id'])

        sequence = list(tuple(zip(map(str, pack_list), map(str, range(1, len(pack_list) + 1)))))
        case_sequence = case(PackDetails.id, sequence)
        if pack_list:
            resp = PackDetails.update(pack_sequence=case_sequence).where(
                PackDetails.id.in_(pack_list)).execute()
    except (InternalError, IntegrityError) as e:
        logger.error("error in set_initial_pack_sequence {}".format(e))
        return error(2001)


def update_config_pack_analysis(data, batch_id):


    for pack in data:
        analysis_id = (PackAnalysis.select(PackAnalysis.id).where(PackAnalysis.pack_id == pack['pack_id'])).scalar()


    pass