import os
import sys
from collections import defaultdict

from peewee import InternalError, IntegrityError, JOIN_LEFT_OUTER, fn, DataError, SQL
from sqlalchemy import case

import settings
from dosepack.utilities.utils import log_args_and_response
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src import constants
from src.api_utility import get_multi_search, get_results
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_canister_drum import CanisterDrum
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_stick import CanisterStick
from src.model.model_code_master import CodeMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_drug_dimension import DrugDimension
from src.model.model_generate_canister import GenerateCanister
from src.model.model_location_master import LocationMaster
from src.model.model_small_canister_stick import SmallCanisterStick
from src.model.model_temp_recommnded_stick_canister import TempRecommendedStickCanisterData

logger = settings.logger


@log_args_and_response
def get_drug_info_for_requested_canister(company_id: int, filter_fields: [dict, None],
                                         sort_fields: [list, None],
                                         paginate: [dict, None]) -> tuple:
    """
    function to get list of drug info for requested canister
    @param sort_fields:
    @param paginate:
    @param filter_fields:
    @param company_id:
    @return:
    """
    clauses: list = list()
    like_search_list = ["drug_name", "ndc", "shape"]
    global_search = [DrugMaster.concated_drug_name_field(), DrugMaster.ndc]

    # apply global_search clause when global_search in filter_field (search by drug_name, ndc or shape)
    if filter_fields and filter_fields.get('global_search', None) is not None:
        multi_search_string = filter_fields['global_search'].split(',')
        multi_search_string.remove('') if '' in multi_search_string else multi_search_string
        clauses = get_multi_search(clauses, multi_search_string, global_search)

    fields_dict = {'drug_name': DrugMaster.concated_drug_name_field(include_ndc=True),
                   'ndc': DrugMaster.ndc,
                   'drug_id': GenerateCanister.drug_id,
                   'shape': CustomDrugShape.name
                   }

    try:
        clauses.append(GenerateCanister.company_id == company_id)

        # query to get drug info for which canister is requested
        query = GenerateCanister.select(DrugMaster.id,
                                        DrugMaster.formatted_ndc,
                                        DrugMaster.txr,
                                        fields_dict["drug_name"].alias("drug_name"),
                                        fields_dict["ndc"],
                                        fields_dict["shape"].alias("shape"),
                                        GenerateCanister.created_date,
                                        GenerateCanister.created_by,
                                        fn.sum(
                                            fn.IF(GenerateCanister.status.in_(constants.REQUESTED_CANISTER_STATUS_LIST),
                                                  (
                                                              GenerateCanister.requested_canister_count - GenerateCanister.fulfilled_requested_canister_count),
                                                  0)).alias("requested_canister_count"),
                                        ).dicts() \
            .join(DrugMaster, on=DrugMaster.id == GenerateCanister.drug_id) \
            .join(UniqueDrug, on=(fn.IF(DrugMaster.txr.is_null(True), '', DrugMaster.txr) ==
                                  fn.IF(UniqueDrug.txr.is_null(True), '', UniqueDrug.txr)) &
                                 (DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc)) \
            .join(DrugDimension, on=DrugDimension.unique_drug_id == UniqueDrug.id) \
            .join(CustomDrugShape, on=CustomDrugShape.id == DrugDimension.shape) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
        logger.info(query)
        results, count = get_results(query.dicts(), fields_dict,
                                     filter_fields=filter_fields,
                                     sort_fields=sort_fields,
                                     paginate=paginate,
                                     clauses=clauses,
                                     like_search_list=like_search_list,
                                     last_order_field=[fields_dict['drug_name']])

        return results, count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_info_for_requested_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_drug_info_for_requested_canister {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_info_for_requested_canister: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_available_drug_canister(company_id: int, fndc: str, txr: str) -> list:
    """
    function to get available canister for drug
    @param company_id:
    @param fndc:
    @param txr:
    @return:
    """
    try:
        available_canister_list: list = list()
        # get number of available canister count for given drug
        query = CanisterMaster.select(CanisterMaster.id).dicts().join(DrugMaster,
                                                                      on=CanisterMaster.drug_id == DrugMaster.id) \
            .where(DrugMaster.formatted_ndc == fndc,
                   DrugMaster.txr == txr,
                   CanisterMaster.company_id == company_id, CanisterMaster.rfid.is_null(False))

        for record in query:
            available_canister_list.append(record['id'])
        logger.info("In get_available_drug_canister: Available canister for fndc:{} and txr: {} is = {}".format(fndc, txr,
                                                                                                        available_canister_list))
        return available_canister_list
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_available_drug_canister_counts: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_available_drug_canister_counts {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_available_drug_canister_counts: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_request_canister_status_info(canister_request_data: dict, fndc: str, txr: str) -> list:
    """
    function to get requested canister status info for canister request status screen
    @param txr:
    @param canister_request_data:
    @param fndc:
    @return:
    """
    company_id = canister_request_data.get('company_id')
    filter_fields = canister_request_data.get('filter_fields', None)
    canister_status_list: list = list()

    clauses = [DrugMaster.formatted_ndc == fndc, DrugMaster.txr == txr,
               GenerateCanister.company_id == company_id, GenerateCanister.status != constants.DONE_ID]
    if filter_fields and filter_fields.get('status', None) is not None:
        status = filter_fields.get('status')
        clauses.append(CodeMaster.value == status)

    try:
        # query to get requested canister status info
        query = GenerateCanister.select(GenerateCanister.odoo_request_id,
                                        CodeMaster.value.alias("canister_request_status")).dicts() \
            .join(DrugMaster, on=DrugMaster.id == GenerateCanister.drug_id) \
            .join(CodeMaster, on=CodeMaster.id == GenerateCanister.status) \
            .where(*clauses)
        # //TODO get big stick small stick parameter from odoo
        for status_data in query:
            status_data["big_stick"] = None
            status_data["small_stick"] = None
            canister_status_list.append(status_data)
        logger.info(
            "In get_request_canister_status_info: requested canister status info: {} for fndc:{} and txr: {}".format(
                canister_status_list, fndc, txr))
        return canister_status_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_request_canister_status_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_request_canister_status_info {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_request_canister_status_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_same_stick_canister_list(drug_canister_data: dict) -> dict:
    """
    function to get other canister ids with same stick combination
    @param drug_canister_data:
    @return:
    """
    company_id = drug_canister_data.get("company_id")
    stick_id_list = drug_canister_data.get("stick_id_list")
    same_stick_canister_list = defaultdict(list)
    order_list: list = list()
    try:

        order_list.append(SQL('device_type_id is null'))
        order_list.append(SQL('FIELD(device_type_id, {},{},{},{})'
                              .format(settings.DEVICE_TYPES['CSR'], settings.DEVICE_TYPES['ROBOT'],
                                      settings.DEVICE_TYPES['Canister Transfer Cart'],
                                      settings.DEVICE_TYPES['Canister Cart w/ Elevator'])))
        # get canister with same stick for ndc
        query = CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
                                      CanisterMaster.canister_stick_id,
                                      CanisterMaster.location_id, DeviceTypeMaster.id.alias('device_type_id')).dicts() \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, on=DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .where(CanisterMaster.canister_stick_id.in_(stick_id_list),
                   CanisterMaster.company_id == company_id,
                   CanisterMaster.active != settings.is_canister_active,
                   CanisterMaster.available_quantity == 0,
                   CanisterMaster.rfid.is_null(False)) \

        query = query.order_by(*order_list)
        for record in query:
            same_stick_canister_list.setdefault((record['canister_stick_id']), []).append(record)

        return same_stick_canister_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_same_stick_canister_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_same_stick_canister_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_same_stick_canister_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_recommended_stick_canister_data(company_id: int, user_id: int) -> list:
    """
    function to get canister data by canister id for generate canister screen
    @param company_id:
    @param user_id:
    @return:
    """
    try:

        query = TempRecommendedStickCanisterData.select(CanisterMaster.id.alias("canister_id"),
                                                        DeviceMaster.system_id,
                                                        DeviceMaster.name.alias('device_name'),
                                                        ContainerMaster.drawer_name.alias('drawer_number'),
                                                        LocationMaster.display_location,
                                                        CanisterStick.id.alias("canister_stick_id"),
                                                        CanisterStick.big_canister_stick_id.alias(
                                                            "big_canister_stick_number"),
                                                        BigCanisterStick.width,
                                                        BigCanisterStick.depth,
                                                        CanisterStick.small_canister_stick_id.alias(
                                                            "small_canister_stick_number"),
                                                        DeviceTypeMaster.id.alias('device_type_id'),
                                                        ContainerMaster.ip_address,
                                                        ContainerMaster.secondary_ip_address,
                                                        ContainerMaster.shelf,
                                                        ContainerMaster.serial_number
                                                        ).dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == TempRecommendedStickCanisterData.canister_id) \
            .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(DeviceTypeMaster, JOIN_LEFT_OUTER, DeviceTypeMaster.id == DeviceMaster.device_type_id) \
            .join(CanisterStick, JOIN_LEFT_OUTER, on=CanisterStick.id == CanisterMaster.canister_stick_id) \
            .join(BigCanisterStick, JOIN_LEFT_OUTER, on=BigCanisterStick.id == CanisterStick.big_canister_stick_id) \
            .where(CanisterMaster.company_id == company_id,
                   TempRecommendedStickCanisterData.recommended_stick == 1,
                   TempRecommendedStickCanisterData.status == constants.CANISTER_TESTING_PENDING,
                   TempRecommendedStickCanisterData.user_id == user_id) \
            .order_by(TempRecommendedStickCanisterData.order_no).limit(1)
        logger.info(query)
        return list(query)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_recommended_stick_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_recommended_stick_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_recommended_stick_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_requested_canister_stick_data_from_stick_id(stick_id_list: list):
    """
    returns big canister stick serial number, small canister stick serial number and drum serial number stick_id_list
    @param stick_id_list:
    :return:
    """
    canister_stick_info_list: list = list()
    try:
        query = CanisterStick.select(CanisterStick.id,
                                     BigCanisterStick.serial_number.alias("big_stick_serial_number"),
                                     SmallCanisterStick.length.alias("small_stick_serial_number"),
                                     CanisterDrum.serial_number.alias("drum_serial_number")
                                     ).dicts() \
            .join(BigCanisterStick, JOIN_LEFT_OUTER, on=BigCanisterStick.id == CanisterStick.big_canister_stick_id) \
            .join(SmallCanisterStick, JOIN_LEFT_OUTER,
                  on=SmallCanisterStick.id == CanisterStick.small_canister_stick_id) \
            .join(CanisterDrum, JOIN_LEFT_OUTER, on=CanisterDrum.id == CanisterStick.canister_drum_id) \
            .where(CanisterStick.id.in_(stick_id_list))
        for record in query:
            canister_stick_info_list.append(record)
        return canister_stick_info_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_requested_canister_data_from_stick_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_requested_canister_data_from_stick_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_requested_canister_data_from_stick_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_same_stick_canister_info(canister_id: int):
    """
    returns canister list for which stick is same as given canister stick's
    @param canister_id:
    :return:
    """
    canister_list: list = list()
    try:
        TempRecommendedStickCanisterDataAlias = TempRecommendedStickCanisterData.alias()
        query = TempRecommendedStickCanisterData.select(TempRecommendedStickCanisterData.canister_id,
                                                        TempRecommendedStickCanisterData.canister_stick_id).dicts() \
            .join(TempRecommendedStickCanisterDataAlias,
                  on=((
                                  TempRecommendedStickCanisterData.canister_stick_id == TempRecommendedStickCanisterDataAlias.canister_stick_id) &
                      (TempRecommendedStickCanisterDataAlias.canister_id == canister_id))) \
            .where(TempRecommendedStickCanisterData.status == constants.CANISTER_TESTING_PASS)
        for record in query:
            # remove tested canister id from link_canister pop up
            if record['canister_id'] == int(canister_id):
                continue
            canister_list.append(record)
        return canister_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_same_stick_canister_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_same_stick_canister_info {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_same_stick_canister_info: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_stick_canister_status(canister_data: dict) -> bool:
    """
    function to update canister status for generate canister in TempRecommendedStickCanisterData table
    @param canister_data:
    :return:
    """

    try:
        canister_id = int(canister_data.get('canister_id'))
        tested_canister_status = canister_data.get('status_id')
        user_id = canister_data.get('user_id')
        canister_stick_id = canister_data.get('stick_id_list')
        status = TempRecommendedStickCanisterData.db_update_tested_stick_canister_status(canister_id=canister_id,
                                                                                         canister_stick_id=canister_stick_id,
                                                                                         tested_canister_status=tested_canister_status,
                                                                                         user_id=user_id)
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_stick_canister_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in update_stick_canister_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_stick_canister_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_odoo_requested_canister_status(canister_data: dict) -> int:
    """
    returns update requested canister status in Generate canister table
    :return:
    """

    try:
        odoo_req_id = int(canister_data['odoo_req_id'])
        requested_canister_status = int(canister_data['status'])
        status = GenerateCanister.db_update_requested_canister_status(odoo_req_id=odoo_req_id,
                                                                      requested_canister_status=requested_canister_status)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_odoo_requested_canister_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in update_odoo_requested_canister_status {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_odoo_requested_canister_status: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def delete_recom_temp_stick_canister_data(user_id: int) -> int:
    """
    returns delete recommended stick canister data from TempRecommendedStickCanisterData
    :return:
    """
    try:
        status = TempRecommendedStickCanisterData.db_delete_canister(user_id=user_id)
        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_recom_temp_stick_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in delete_recom_temp_stick_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in delete_recom_temp_stick_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_recom_stick_canister_data():
    """
    returns recommended stick canister data from TempRecommendedStickCanisterData
    :return:
    """
    try:
        query = TempRecommendedStickCanisterData.db_get_recom_stick_canister_data()
        return query
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_recom_stick_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_recom_stick_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_recom_stick_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def check_existence_record(user_id):
    """
    check existence of record in table for given use id
    :return: bool
    """
    try:
        is_record_exist = TempRecommendedStickCanisterData.check_if_canister_data_exit_for_user(user_id=user_id)
        return is_record_exist

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in check_existence_record: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in check_existence_record {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in check_existence_record: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_canister_info_by_canister_id(canister_id: int):
    """
    get canister info by canister id
    :return: bool
    """
    try:
        canister_data = CanisterMaster.db_get_canister_info(canister_id=canister_id)
        return canister_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_canister_info_by_canister_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_canister_info_by_canister_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_canister_info_by_canister_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_drug_dimension_info_by_unique_drug_id(unique_drug_id: int):
    """
    get drug dimension info by unique drug id
    :return: bool
    """
    try:
        drug_dimension_data = DrugDimension.db_get_drug_dimension_info(unique_drug_id=unique_drug_id).get()

        return drug_dimension_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension_info_by_unique_drug_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in get_drug_dimension_info_by_unique_drug_id {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_dimension_info_by_unique_drug_id: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def insert_stick_canister_data(canister_list: list):
    """
    insert canister whose stick is same as tested canister stick in case of test with other canister
    :return: bool
    """
    try:
        status = TempRecommendedStickCanisterData.db_insert_canister_data(canister_list=canister_list)

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in insert_stick_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in insert_stick_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in insert_stick_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def update_order_no_canister_list(seq_tuples: list, canister_list: list):
    """
    update order number in TempRecommendedStickCanisterData when tested canister status is defective
    :return: bool
    """
    try:
        case_sequence = case(TempRecommendedStickCanisterData.canister_id, seq_tuples)
        status = TempRecommendedStickCanisterData.db_update_order_no(order_no=case_sequence, canister_list=canister_list)

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_order_no_canister_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in update_order_no_canister_list {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in update_order_no_canister_list: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def get_drug_requested_canister_count(company_id: int, fndc: str, txr: str) -> int:
    """
    function to get already requested canister count for drug
    @param company_id:
    @param fndc:
    @param txr:
    @return:
    """
    try:
        query = DrugMaster.select(fn.SUM(GenerateCanister.requested_canister_count -
                                         GenerateCanister.fulfilled_requested_canister_count)
            .alias('requested_canister_count')).dicts() \
            .join(GenerateCanister, on=DrugMaster.id == GenerateCanister.drug_id) \
            .where(DrugMaster.formatted_ndc == fndc,
                   DrugMaster.txr == txr,
                   GenerateCanister.status.in_(constants.REQUESTED_CANISTER_STATUS_LIST),
                   GenerateCanister.company_id == company_id) \
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
        logger.info("In get_drug_requested_canister_count:requested canister count for fndc:{} and txr: {} is = {}"
                    .format(fndc, txr, query))
        for record in query:
            return record['requested_canister_count']
        return 0
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_requested_canister_count: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e

    except Exception as e:
        logger.error("error in get_drug_requested_canister_count {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in get_drug_requested_canister_count: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e


@log_args_and_response
def insert_requested_canister_data(canister_data: list):
    """
    insert requested canister data in generate canister table
    :return: bool
    """
    try:
        status = GenerateCanister.db_insert_canister_data(canister_data=canister_data)

        return status

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in insert_requested_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
    except Exception as e:
        logger.error("error in insert_requested_canister_data {}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error in insert_requested_canister_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
        raise e
