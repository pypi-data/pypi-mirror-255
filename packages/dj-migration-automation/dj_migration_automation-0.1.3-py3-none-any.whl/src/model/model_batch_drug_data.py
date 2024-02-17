from typing import List, Dict, Any

from peewee import (IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, DecimalField, IntegrityError,
                    InternalError, BooleanField, CharField, DataError, DoesNotExist, fn)
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster

from src import constants
from src.model.model_facility_distribution_master import FacilityDistributionMaster

logger = settings.logger


class BatchDrugData(BaseModel):
    id = PrimaryKeyField()
    facility_dist_id = ForeignKeyField(FacilityDistributionMaster)
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
    created_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField(null=True)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_drug_data"

    @classmethod
    def get_drug_data_by_facility_dist_id_and_dept(cls, facility_dist_id: int, department: str) -> List[Any]:
        """
        Gets the list of records from the BatchDrugData for the given facility_dist_id.
        """
        logger.debug("Inside model.get_drug_data_by_facility_dist_id_and_dept")
        try:
            query = cls.select().dicts().where(cls.facility_dist_id == facility_dist_id, cls.department == department)
            return query
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Inserts multiple records in the BatchDrugData.
        """
        logger.debug("Inside BatchDrugData.insert_data")
        try:
            cls.insert_many(data_list).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def delete_data(cls, delete_list: List[str], facility_dist_id: int, user_id: int) -> bool:
        """
        Updates the status as deleted of the given list of drug_ids and the given facility_dist_id.
        """
        logger.debug("Inside BatchDrugData.delete_data")
        fndc_txr_daw_list: List[str] = list()
        txr_daw_list: List[str] = list()
        try:
            for value in delete_list:
                if len(value.strip().split("##")) == 3:
                    fndc_txr_daw_list.append(value)
                else:
                    txr_daw_list.append(value)
            if len(fndc_txr_daw_list) > 0:
                cls.update(status_id=constants.DRUG_INVENTORY_MANAGEMENT_DELETED_ID, modified_by=user_id,
                           modified_date=get_current_date_time(), ext_is_success=None, ext_note=None) \
                    .where(cls.facility_dist_id == facility_dist_id,
                           fn.CONCAT(cls.formatted_ndc, "##", cls.txr, "##", cls.daw).in_(fndc_txr_daw_list)).execute()
            if len(txr_daw_list) > 0:
                cls.update(status_id=constants.DRUG_INVENTORY_MANAGEMENT_DELETED_ID, modified_by=user_id,
                           modified_date=get_current_date_time(), ext_is_success=None, ext_note=None) \
                    .where(cls.facility_dist_id == facility_dist_id,
                           fn.CONCAT(cls.txr, "##", cls.daw).in_(txr_daw_list)).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_batch_drug_data_by_fndc_txr_daw_and_dept(cls, data: Dict[str, Any], facility_dist_id: int,
                                                        fndc_txr_daw: str, department: str) -> bool:
        """
        Updates the record for the given identifier and the facility_dist_id.
        """
        try:
            if len(fndc_txr_daw.strip().split("##")) == 3:
                cls.update(**data).where(cls.facility_dist_id == facility_dist_id, cls.department == department,
                                         fn.CONCAT(cls.formatted_ndc, "##", cls.txr, "##",
                                                   cls.daw) == fndc_txr_daw).execute()
            else:
                cls.update(**data).where(cls.facility_dist_id == facility_dist_id, cls.department == department,
                                         fn.CONCAT(cls.txr, "##", cls.daw) == fndc_txr_daw).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_batch_drug_data_by_ndc(cls, data: Dict[str, Any], facility_dist_id: int, ndc: str) -> bool:
        """
        Updates the record for the given ndc and the facility_dist_id.
        """
        try:
            query = cls.update(**data).where(cls.facility_dist_id == facility_dist_id, cls.ndc == ndc).execute()
            if query > 0:
                return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
