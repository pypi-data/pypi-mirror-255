from typing import List, Dict, Any
from peewee import (IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, DecimalField, IntegrityError,
                    InternalError, BooleanField, CharField, DataError, DoesNotExist, fn)
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src import constants

logger = settings.logger


class AdhocDrugRequest(BaseModel):
    id = PrimaryKeyField()
    unique_id = CharField(max_length=15)
    formatted_ndc = CharField(max_length=12, null=True)
    txr = CharField(max_length=8, null=True)
    daw = IntegerField()
    ndc = CharField(max_length=14)
    req_qty = DecimalField(decimal_places=2)
    order_qty = IntegerField()
    department = CharField(max_length=20, null=False)
    status_id = ForeignKeyField(CodeMaster)
    ext_is_success = BooleanField(null=True)
    ext_note = CharField(default=None, null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "adhoc_drug_request"

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Inserts multiple records in the BatchDrugData.
        """
        logger.debug("Inside AdhocDrugRequest.insert_data")
        try:
            cls.insert_many(data_list).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_adhoc_drug_request_by_fndc_txr_daw(cls, data: Dict[str, Any], unique_id: str, fndc_txr_daw: str) -> bool:
        """
        Updates the record for the given drug and the unique_id.
        """
        try:
            if len(fndc_txr_daw.strip().split("##")) == 3:
                cls.update(**data).where(cls.unique_id == unique_id,
                                         fn.CONCAT(cls.formatted_ndc, "##", cls.txr, "##",
                                                   cls.daw) == fndc_txr_daw).execute()
            else:
                cls.update(**data).where(cls.unique_id == unique_id,
                                         fn.CONCAT(cls.txr, "##", cls.daw) == fndc_txr_daw).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_adhoc_drug_request_by_fndc_txr_daw_case(cls, ext_note_case ,ext_success_case, unique_id, fndc_txr_daws):
        """
        Updates the record for the given drug and the unique_id.
        """
        try:
            cls.update(ext_is_success=ext_success_case, ext_note=ext_note_case, modified_date=get_current_date_time()).where(cls.unique_id == unique_id,
                                         fn.CONCAT(cls.formatted_ndc, "##", cls.txr, "##",
                                                   cls.daw) << fndc_txr_daws).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
    @classmethod
    def delete_data(cls, delete_list: List[str], unique_id: str) -> bool:
        """
        Updates the status as deleted of the given list of drug_ids and the given unique_id.
        """
        logger.debug("Inside AdhocDrugRequest.delete_data")
        fndc_txr_daw_list: List[str] = list()
        txr_daw_list: List[str] = list()
        try:
            for value in delete_list:
                if len(value.strip().split("##")) == 3:
                    fndc_txr_daw_list.append(value)
                else:
                    txr_daw_list.append(value)
            if len(fndc_txr_daw_list) > 0:
                cls.update(status_id=constants.DRUG_INVENTORY_MANAGEMENT_DELETED_ID,
                           modified_date=get_current_date_time(), ext_is_success=None, ext_note=None) \
                    .where(cls.unique_id == unique_id,
                           fn.CONCAT(cls.formatted_ndc, "##", cls.txr, "##", cls.daw).in_(fndc_txr_daw_list)).execute()
            if len(txr_daw_list) > 0:
                cls.update(status_id=constants.DRUG_INVENTORY_MANAGEMENT_DELETED_ID,
                           modified_date=get_current_date_time(), ext_is_success=None, ext_note=None) \
                    .where(cls.unique_id == unique_id, fn.CONCAT(cls.txr, "##", cls.daw).in_(txr_daw_list)).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_adhoc_drug_request_by_ndc(cls, data: Dict[str, Any], unique_id: str, ndc: str) -> bool:
        """
        Updates the record for the given ndc and the facility_dist_id.
        """
        try:
            query = cls.update(**data).where(cls.unique_id == unique_id, cls.ndc == ndc).execute()
            if query > 0:
                return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
