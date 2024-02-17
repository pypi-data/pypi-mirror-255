# -*- coding: utf-8 -*-
"""
    src.test_pack
    ~~~~~~~~~~~~~~~~

   This module generates  sample drug name to be used in the generation of sample test packs.

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""

import logging

from peewee import InternalError, IntegrityError, JOIN_LEFT_OUTER, DataError

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import get_current_date, log_args_and_response
from dosepack.validation.validate import validate
from src.dao.canister_dao import get_canisters_by_device_system_company
from src.dao.pack_dao import get_pack_grid_id_dao
from src.model.model_canister_master import CanisterMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_details import PackDetails
# get the logger for the pack from global configuration file logging.json
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_rx import PatientRx
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader

logger = logging.getLogger("root")


@log_args_and_response
def get_canisters(system_id=None, device_ids=None, company_id=None):
    """  Gives the canister information for the given robot ids or system or company id
    """
    data = []
    # distinct_drug_name = []
    # try:
    #     DrugMasterAlias = DrugMaster.alias()
    #     # using drug master alias to return all unique drugs
    #     select_fields = [
    #             CanisterMaster.id,
    #             LocationMaster.device_id,
    #             PatientRx.id.alias('rx_id'),
    #             LocationMaster.location_number,
    #             ContainerMaster.drawer_name.alias('drawer_number'),
    #             LocationMaster.display_location,
    #             DrugMasterAlias.drug_name,
    #             DrugMasterAlias.ndc,
    #             DrugMasterAlias.strength,
    #             DrugMasterAlias.strength_value
    #     ]
    #
    #     query = PatientRx.select(*select_fields) \
    #         .join(DrugMaster, on=DrugMaster.id == PatientRx.drug_id) \
    #         .join(DrugMasterAlias, on=(DrugMasterAlias.formatted_ndc == DrugMaster.formatted_ndc)
    #                                   & (DrugMasterAlias.txr == DrugMaster.txr)) \
    #         .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.drug_id == DrugMasterAlias.id) \
    #         .join(LocationMaster, JOIN_LEFT_OUTER, on=LocationMaster.id == CanisterMaster.location_id)\
    #         .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == LocationMaster.container_id) \
    #         .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == LocationMaster.device_id)
    #
    #     query = query.where(CanisterMaster.active == settings.is_canister_active)
    #     if device_ids:
    #         query = query.where(LocationMaster.device_id << device_ids)
    #
    #         query = query.group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
    #         for record in query.distinct().dicts():
    #             drug_name = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"] + " [" + str(record["canister_number"]) + "]"
    #             if record["ndc"] not in distinct_drug_name:
    #                 data.append({
    #                     "value": record["rx_id"],
    #                     "text": drug_name,
    #                     "robot": str(record["device_id"]),
    #                     "location_number": record["location_number"],
    #                     "drawer_number": record["drawer_number"]
    #                 })
    #                 distinct_drug_name.append(record["ndc"])
    #     else:
    #         query = query.where(CanisterMaster.location_id.is_null(False))  # only canister which are in robot
    #         if company_id:
    #             query = query.where(CanisterMaster.company_id == company_id)
    #         if system_id:
    #             query = query.where(DeviceMaster.system_id == system_id)
    #         query = query.group_by(DrugMaster.formatted_ndc, DrugMaster.txr)
    #         for record in query.distinct().dicts():
    #             drug_name = record["drug_name"] + " " + record["strength_value"] + " " + record["strength"] + " [" + str(record["display_location"]) + "]"
    #             if record["ndc"] not in distinct_drug_name:
    #                 data.append({"value": record["rx_id"], "text": drug_name, "robot": str(record["device_id"]), "location_number": record["location_number"], "drawer_number": record["drawer_number"]})
    #                 distinct_drug_name.append(record["ndc"])
    try:
        data = get_canisters_by_device_system_company(system_id=system_id, device_ids=device_ids, company_id=company_id)
        return create_response(data)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def populate_pack_generator(data):
    """
    Creates a dummy pack for the given rx_ids and system_id

    Returns: pack_id of the generated dummy pack

    """
    if settings.SERVER_TYPE == 0:
        msg = '0'
        return create_response(msg)
    system_id = int(data["system_id"])
    rx_ids = data["rx_ids"].split(',')
    pack_header_id = PackHeader.get().id 
    pack_data = {"pack_header_id": pack_header_id, "batch_id": 1, "pack_display_id": 1000, "pack_no": 1, "pack_status_id": 2,
                 "filled_by": "test", "filled_days": 7, "fill_start_date": "2016-01-01", "delivery_schedule": "test",
                 "order_no": 100, "created_by": 1, "modified_by": 1, "created_date": get_current_date(), "system_id": system_id,
                 "consumption_start_date": "2016-01-01", "consumption_end_date": "2016-01-07"}

    with db.atomic():
        status = BaseModel.db_create_record(pack_data, PackDetails, get_or_create=False)
        pack_id = status.id
        dates = ["2016-01-01", "2016-01-02", "2016-01-03", "2016-01-04", "2016-01-05", "2016-01-06", "2016-01-07"]
        times = ["08:00", "13:00", "18:00", "22:00"]
        for rx_id in rx_ids:
            rx_record_id = BaseModel.db_create_record({"patient_rx_id": rx_id, "pack_id": pack_id}, PackRxLink, get_or_create=False).id
            for i in range(0, 7):
                for j in range(0, 4):
                    pack_grid_id = get_pack_grid_id_dao(slot_row=i, slot_column=j)
                    slot_record = BaseModel.db_create_record({"pack_id": pack_id, "hoa_date": dates[i], "hoa_time": times[j],
                                                          "pack_grid_id": pack_grid_id}, SlotHeader, get_or_create=False)

                    slot_id = slot_record.id
                    slot_details_record = BaseModel.db_create_record({"slot_id": slot_id, "pack_rx_id": rx_record_id, "quantity": 1, "is_manual": 0}, SlotDetails, get_or_create=False)

    return create_response(pack_id)


