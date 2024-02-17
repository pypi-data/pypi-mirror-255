import functools
import operator
from peewee import InternalError, DoesNotExist, IntegrityError, JOIN_LEFT_OUTER, DataError
from peewee import fn

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.error_handling.error_handler import error
from dosepack.utilities.utils import log_args_and_response
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_training import DrugTraining
from src.model.model_slot_details import SlotDetails
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src.model.model_slot_header import SlotHeader
from src.model.model_patient_rx import PatientRx
from src.model.model_pvs_drug_count import PVSDrugCount
from src.model.model_pvs_slot import PVSSlot
from src.model.model_pvs_slot_details import PVSSlotDetails
from src.model.model_pack_grid import PackGrid
from src.model.model_pack_rx_link import PackRxLink

logger = settings.logger


# def update_pvs_pack(update_dict, **kwargs):
#     """
#     To update update_dict in pvs_pack.
#     At least one key, value should be there in kwargs
#     @param update_dict: dict to be updated
#     @param kwargs: multiple key and value condition to update pvs_pack like pack_id = 1, device_id=3
#     @return: update_status
#         >>> update_pvs_pack(update_dict={'modified_date': modified_date,'deleted': True}, pack_id=pack_id,
#                                                                                                 device_id=device_id)
#     """
#     try:
#         return PVSPack.db_update(update_dict=update_dict, **kwargs)
#     except (InternalError, IntegrityError, DataError) as e:
#         raise
#     except ValueError as e:
#         raise


# def create_pvs_pack_record(pvs_pack_data_dict):
#     """
#     To create record in pvs_pack
#     @param pvs_pack_data_dict: dict of record to be created
#     @return: record_id
#         >>> create_pvs_pack_record(pvs_pack_data_dict={"pack_id": 1,
#                                   "device_id": 3,
#                                   "mfd_status": 0,
#                                   "created_date": 2020-10-19 10:13:34,
#                                   "modified_date": 2020-10-19 10:13:34})
#     """
#     try:
#         record = PVSPack.db_create_record(pvs_pack_data_dict, PVSPack, get_or_create=False)
#         return record
#     except (InternalError, IntegrityError, DataError) as e:
#         logger.error(e)
#         raise
#

def db_get_pvs_predicted_qty_group_by_drug(pack_id):
    """
    Returns dictionary containing pvs predicted drugs according to the quantity in each slot drug wise
    :param pack_id: int
    :return: dict {unique_drug_id: {slot_number: predicted_qty}}
    """

    try:
        query = PVSDrugCount.select(
            PVSDrugCount.unique_drug_id,
            PVSDrugCount.predicted_qty,
            PVSDrugCount.pvs_slot_id,
            PackGrid.slot_number,
        ).dicts() \
            .join(PVSSlot, on=PVSSlot.id == PVSDrugCount.pvs_slot_id) \
            .join(SlotHeader, on=SlotHeader.id == PVSSlot.slot_header_id) \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .where(SlotHeader.pack_id == pack_id)

        return query

    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


def get_slot_drug_data_based_slot_details_ids(slot_details_ids):
    try:
        query = SlotDetails.select(DrugMaster.formatted_ndc,
                                   DrugMaster.txr,
                                   DrugMaster.id.alias('drug_id'),
                                   SlotDetails.id.alias('sd_id'),
                                   UniqueDrug.id.alias('unique_drug_id')).dicts() \
            .join(PackRxLink, on=PackRxLink.id == SlotDetails.pack_rx_id) \
            .join(PatientRx, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER, on=(
                (UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) &
                (UniqueDrug.txr == DrugMaster.txr))) \
            .where(SlotDetails.id << slot_details_ids)
        return list(query)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise
    except DoesNotExist as e:
        return []


# def get_pvs_pack_data(**kwargs):
#     try:
#         return PVSPack.db_get_data(**kwargs)
#     except (InternalError, IntegrityError, DataError) as e:
#         logger.error(e)
#         raise
#     except DoesNotExist as e:
#         logger.error(e)
#         return []


# def validate_pvs_pack_id_and_slot_header_id(pvs_pack_id, slot_header_id):
#     try:
#         PVSPack.select(PVSPack.id).dicts() \
#             .join(SlotHeader, on=PVSPack.pack_id == SlotHeader.pack_id) \
#             .where(SlotHeader.id == slot_header_id,
#                    PVSPack.id == pvs_pack_id).get()
#     except (InternalError, IntegrityError, DataError) as e:
#         logger.error(e)
#         raise
#     except DoesNotExist as e:
#         logger.error(e)
#         raise


def get_pvs_slot_recent_record(slot_header_id: int, drop_number: int, device_id: int,
                               quadrant: int):
    """
    @param device_id:
    @param drop_number:
    @param slot_header_id:
    @param quadrant:
    """
    try:
        return PVSSlot.select().dicts() \
            .where(PVSSlot.slot_header_id == slot_header_id,
                   PVSSlot.drop_number == drop_number,
                   PVSSlot.quadrant == quadrant,
                   PVSSlot.device_id == device_id) \
            .order_by(PVSSlot.created_date.desc()).get()

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise
    except DoesNotExist as e:
        logger.error(e)
        raise


@log_args_and_response
def update_pvs_slot(update_dict, **kwargs):
    try:
        update_status = PVSSlot.db_update(update_dict=update_dict, **kwargs)
        return update_status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


def pvs_drug_count_slots(slot_header_id, unique_drug_id):

    data = list()
    try:
        query = PVSSlot.select(PVSDrugCount.predicted_qty).dicts()\
            .join(PVSDrugCount, on=PVSSlot.id == PVSDrugCount.pvs_slot_id)\
            .where(PVSSlot.slot_header_id == slot_header_id,
                   PVSDrugCount.unique_drug_id == unique_drug_id)
        data = [record for record in query]

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
    finally:
        return data


@log_args_and_response
def db_create_pvs_slot(create_dict):
    """
    Method to create record in pvs_slot
    @param create_dict: dict to create record
    @return: id
    """
    try:
        query = BaseModel.db_create_record(create_dict, PVSSlot, get_or_create=False)
        return query.id
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


def db_create_pvs_slot_details(create_dict):
    """
    Method to create record in pvs_slot_details
    @param create_dict: dict to create record
    @return: id
    """
    try:
        query = BaseModel.db_create_record(create_dict, PVSSlotDetails, get_or_create=False)
        return query.id
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def get_unique_drug_based_on_fndc_txr(fndctxr):
    try:
        query = UniqueDrug.select(UniqueDrug.id,
                                  UniqueDrug.formatted_ndc,
                                  UniqueDrug.drug_id,
                                  UniqueDrug.lower_level,
                                  UniqueDrug.drug_usage,
                                  fn.IFNULL(UniqueDrug.txr, '').alias('txr')).dicts() \
            .where(fn.CONCAT(UniqueDrug.formatted_ndc, '_', fn.IFNULL(UniqueDrug.txr, '')) << fndctxr)
        return list(query)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise
    except DoesNotExist as e:
        logger.error(e)
        return []


def get_pack_grid(**kwargs):
    try:
        return PackGrid.db_get_data(**kwargs)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise
    except DoesNotExist as e:
        logger.error(e)
        return []


@log_args_and_response
def pvs_drug_count_update_or_create(create_dict, update_dict):
    try:
        updated_record = PVSDrugCount.db_update_or_create(create_dict, update_dict)
        return updated_record
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


def unique_drug_get_or_create(formatted_ndc, txr, drug_id=None):
    """
           Returns `UniqueDrug` for given formatted ndc, txr combination
           :param formatted_ndc:
           :param txr:
           :param drug_id:
           :return:
           """
    try:
        clauses = list()
        clauses.append((UniqueDrug.formatted_ndc == formatted_ndc))
        if txr is None:
            clauses.append((UniqueDrug.txr.is_null(True)))
        else:
            clauses.append((UniqueDrug.txr == txr))
        return UniqueDrug.select().where(functools.reduce(operator.and_, clauses)).get()
    except DoesNotExist:
        if not drug_id:
            clauses = list()
            clauses.append((DrugMaster.formatted_ndc == formatted_ndc))
            if txr is None:
                clauses.append((DrugMaster.txr.is_null(True)))
            else:
                clauses.append((DrugMaster.txr == txr))
            drug = DrugMaster.select().where(functools.reduce(operator.and_, clauses)).get()
            drug_id = drug.id
        unique_drug = UniqueDrug.create(**{
            'formatted_ndc': formatted_ndc,
            'txr': txr,
            'drug_id': drug_id
        })
        return unique_drug
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


# todo remove below code if not in used for vision-system front-end

# def db_get_results(cls, pack_id, slot_number, pack_details):
#     db_result = {}
#     data = dict()
#     db_result["pack_id"] = pack_id
#     db_result["patient_name"] = pack_details["patient_name"]
#     db_result["rfid"] = pack_details["rfid"]
#     db_result["pack_display_id"] = pack_details["pack_display_id"]
#     db_result["facility_name"] = pack_details["facility_name"]
#
#     if slot_number:
#         for record in VisionCountPrediction.select().dicts()\
#                 .join(VisionDrugMapping)\
#                 .join(VisionDrugPrediction)\
#                 .join(DrugMaster).where(VisionCountPrediction.pack_id == pack_id, VisionCountPrediction.slot_number == slot_number):
#
#             _key = record["slot_number"] - 1
#             data[_key] = {"slot_no": _key,
#                                            "image_url": record["predicted_image_path"],
#                                            "predicted_pills_count": record["predicted_pill_count"],
#                                            "actual_pills_count": record["actual_pill_count"]}
#
#             try:
#                 data[_key]["predicted_drug_list"].append(
#                     {"drug_name": record["drug_name"], "ndc": record["ndc"],
#                      "shape": record["shape"], "color": record["color"], "coords": record["coordinates"]})
#             except KeyError:
#                 data[_key]["predicted_drug_list"] = []
#                 data[_key]["predicted_drug_list"].append(
#                     {{"drug_name": record["drug_name"], "ndc": record["ndc"],
#                       "shape": record["shape"], "color": record["color"], "coords": record["coordinates"]}})
#
#             try:
#                 data[_key]["actual_drug_list"].append(
#                     {{"drug_name": record["drug_name"], "ndc": record["ndc"],
#                       "shape": record["shape"], "color": record["color"], "coords": record["coordinates"]}})
#             except KeyError:
#                 data[_key]["actual_drug_list"] = []
#                 data[_key]["actual_drug_list"].append(
#                     {{"drug_name": record["drug_name"], "ndc": record["ndc"],
#                       "shape": record["shape"], "color": record["color"], "coords": record["coordinates"]}})
#
#     else:
#         for record in VisionCountPrediction.select(VisionCountPrediction.predicted_image_path, VisionCountPrediction.predicted_pill_count,
#                                                    VisionCountPrediction.actual_pill_count, VisionCountPrediction.slot_number,
#                                                    DrugMaster.drug_name, DrugMaster.ndc, DrugMaster.shape, DrugMaster.color,
#                                                    VisionCountPrediction.precision, VisionCountPrediction.recall).dicts()\
#                 .join(VisionDrugMapping)\
#                 .join(VisionDrugPrediction)\
#                 .join(DrugMaster).where(VisionCountPrediction.pack_id == pack_id):
#
#             _key = record["slot_number"] - 1
#
#             if _key not in data:
#                 data[_key] = {"slot_no": _key, "image_url": record["predicted_image_path"],
#                                "predicted_pills_count": record["predicted_pill_count"], "actual_pills_count": record["actual_pill_count"],
#                               "predicted_drug_list": [], "actual_drug_list": []}
#
#             try:
#                 data[_key]["predicted_drug_list"].append({"drug_name": record["drug_name"], "ndc": record["ndc"],
#                                                                            "shape": record["shape"], "color": record["color"], "coords": record["coordinates"]})
#             except KeyError:
#                 data[_key]["predicted_drug_list"] = []
#                 data[_key]["predicted_drug_list"].append({"drug_name": record["drug_name"], "ndc": record["ndc"],
#                                                                            "shape": record["shape"], "color": record["color"], "coords": record["coordinates"]})
#
#             try:
#                 data[_key]["actual_drug_list"].append({"drug_name": record["drug_name"], "ndc": record["ndc"],
#                                                                            "shape": record["shape"], "color": record["color"], "coords": record["coordinates"]})
#             except KeyError:
#                 data[_key]["actual_drug_list"] = []
#                 data[_key]["actual_drug_list"].append({"drug_name": record["drug_name"], "ndc": record["ndc"],
#                                                                            "shape": record["shape"], "color": record["color"], "coords": record["coordinates"]})
#
#             data[_key]["overall_accuracy"] = 100 - (math.fabs(record["actual_pill_count"] - record["predicted_pill_count"]) / record["actual_pill_count"])
#             data[_key]["precision"] = record["precision"]
#             data[_key]["recall"] = record["recall"]
#
#     slot_data = data.values()
#     db_result["slot_data"] = data.values()
#     slot_mapping = {}
#     for index, item in enumerate(slot_data):
#         slot_mapping[item["slot_no"]] = index
#     db_result["slot_mapping"] = slot_mapping
#     return db_result


@log_args_and_response
def drug_list_from_drug_training_for_given_filters(filters):
    """
    @param filters:
    @return:
    """
    drug_list = list()
    clauses = list()
    fndc_txr_list = list()
    count = filters.get('count', None)
    drugs = filters.get('drugs', None)
    status = filters.get('status', None)
    try:
        if count is not None:
            clauses.append((DrugTraining.image_crops_count > count))
        if drugs:
            for item in drugs:
                fndc_txr_list.append("{}#{}".format(item['formatted_ndc'], item['txr'] or ''))
            clauses.append((fn.CONCAT(UniqueDrug.formatted_ndc, '#', fn.IFNULL(UniqueDrug.txr, '')) << fndc_txr_list))
        if status is not None:
            clauses.append((DrugTraining.status == status))
        query = DrugTraining.select(DrugTraining,
                                    UniqueDrug.formatted_ndc,
                                    UniqueDrug.txr,
                                    UniqueDrug.drug_id) \
            .join(UniqueDrug, on=DrugTraining.unique_drug_id == UniqueDrug.id).dicts() \
            .where(*clauses)

        for record in query:
            drug_list.append(record)

        return drug_list

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_unique_drug_from_fndc_txr(fndc_txr_list):
    try:
        unique_drug_data = UniqueDrug.db_get_unique_drug_id(fndc_txr_list)
        return unique_drug_data

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def update_drug_training_status(status, unique_drug_id_list):
    try:
        status = DrugTraining.db_update_status(status, unique_drug_id_list)
        return status

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except Exception as e:
        raise e


@log_args_and_response
def get_associated_device_id(device_id):
    try:
        logger.info("get_associated_device_id")
        associated_device_id = 1 # bydefault 1

        query = DeviceMaster.select(DeviceMaster.associated_device).dicts() \
                        .where(DeviceMaster.id == device_id)
        for data in query:
            associated_device_id = data["associated_device"]
            return associated_device_id
        return associated_device_id

    except (IntegrityError, InternalError) as e:
        logger.error(f"Error in get_associated_device_id: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error in get_associated_device_id: {e}")
        raise e
