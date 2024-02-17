from functools import partial

from peewee import IntegrityError, InternalError, DataError

import settings
from dosepack.utilities.utils import log_args_and_response
from src.exceptions import FileParsingException
from src.model.model_doctor_master import DoctorMaster
from src.model.model_facility_master import FacilityMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_template_master import TemplateMaster

logger = settings.logger


PARSING_ERRORS = {
    "default": "File parsing failed.",
    "missing_drug": "Drug data does not exist for the given NDC: ",
    "duplicate_fill_id": 'Duplicate Pharmacy Fill ID found.',
    "multiple_fill_id": "Multiple Pharmacy Fill IDs found for some patient(s).",
    "drug_fetch": "Unable to fetch drug data from Pharmacy Software.",
    "duplicate_file": "File name already exists.",
    "add_task_failed": "File parsing task could not be queued. "
                       "(Probable Reasons: Network Failure, Improper Deployment Configuration)",
}


@log_args_and_response
def db_doctor_master_update_or_create(dict_doctor_master_data, pharmacy_doctor_id, company_id, default_data_dict,
                                      remove_fields):
    try:
        return DoctorMaster.db_update_or_create(data=dict_doctor_master_data, pharmacy_doctor_id=pharmacy_doctor_id,
                                                company_id=company_id, default_data_dict=default_data_dict,
                                                remove_fields=remove_fields)
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise FileParsingException(PARSING_ERRORS["default"])


@log_args_and_response
def db_update_modification_status_by_change_rx(patient_id, file_id):
    try:
        # Update the Modification Status as Yellow(as we are not using Red anymore) and then continue to get
        # template data
        is_modified = TemplateMaster.IS_MODIFIED_MAP["YELLOW"]
        TemplateMaster.db_update_modification_status(patient_id=patient_id, file_id=file_id,
                                                     is_modified_status=is_modified,
                                                     template_status=
                                                     settings.PENDING_CHANGE_RX_TEMPLATE_STATUS_TEMPLATE)
    except (IntegrityError, InternalError, DataError, Exception) as e:
        logger.error(e, exc_info=True)
        raise


@log_args_and_response
def db_partial_update_create_facility_master_dao(default_data_dict):
    try:
        return partial(FacilityMaster.db_update_or_create, default_data_dict=default_data_dict)
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise FileParsingException(PARSING_ERRORS["default"])


@log_args_and_response
def db_patient_rx_update_or_create_dao(dict_patient_rx_info, drug_id, doctor_id, remove_fields_list, default_data_dict, stop_data):
    try:
        return PatientRx.db_update_or_create_rx(
            dict_patient_rx_info["patient_id"],
            dict_patient_rx_info["pharmacy_rx_no"],
            dict_patient_rx_info,
            add_fields={
                'drug_id': drug_id,
                'doctor_id': doctor_id
            },
            remove_fields=remove_fields_list,
            default_data_dict=default_data_dict,
            stop_data=stop_data
        )
    except (IntegrityError, InternalError, DataError) as e:
        logger.error(e, exc_info=True)
        raise
