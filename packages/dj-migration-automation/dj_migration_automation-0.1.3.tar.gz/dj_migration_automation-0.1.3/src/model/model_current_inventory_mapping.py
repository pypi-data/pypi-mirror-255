from typing import List, Dict, Any, Optional

from peewee import (ForeignKeyField, PrimaryKeyField, IntegrityError, InternalError, CharField, DataError, DoesNotExist,
                    DecimalField, BooleanField)
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_batch_drug_data import BatchDrugData
from src.model.model_facility_distribution_master import FacilityDistributionMaster

logger = settings.logger


class CurrentInventoryMapping(BaseModel):
    id = PrimaryKeyField()
    facility_dist_id = ForeignKeyField(FacilityDistributionMaster)
    batch_drug_id = ForeignKeyField(BatchDrugData)
    reserve_ndc = CharField(max_length=14)
    reserve_txr = CharField(max_length=8, null=False)
    reserve_qty = DecimalField(decimal_places=2)
    is_local = BooleanField(default=False)
    is_active = BooleanField(default=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "current_inventory_mapping"

    @classmethod
    def get_data_by_facility_dist_id(cls, facility_dist_id: int, local_di: bool,
                                     only_active: Optional[bool] = True) -> List[Any]:
        """
        Fetches data from CurrentInventoryMapping for the given facility_dist_id and the active flag
        """
        logger.debug("Inside CurrentInventoryMapping.get_data_by_facility_dist_id")
        clauses: List[Any] = [cls.facility_dist_id == facility_dist_id, cls.is_local == 1 if local_di else 0]
        if only_active:
            clauses.append(cls.is_active == 1)
        try:
            return cls.select().dicts().where(*clauses)
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Gets the list of records from the CurrentInventoryMapping for the given facility_dist_id.
        """
        logger.debug("Inside CurrentInventoryMapping.insert_data")
        try:
            cls.insert_many(data_list).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def delete_data(cls, facility_dist_id: int) -> bool:
        """
        Updates the is_active flag false in the CurrentInventoryMapping table.
        """
        logger.debug("Inside CurrentInventoryMapping.delete_data")
        try:
            cls.update(is_active=False).where(cls.facility_dist_id == facility_dist_id).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_data_by_id(cls, data: Dict[str, Any], update_id: int) -> bool:
        """
        Updates the record for the given drug_id and the facility_dist_id.
        """
        try:
            query = cls.update(**data).where(cls.id == update_id).execute()
            if query >= 0:
                return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
