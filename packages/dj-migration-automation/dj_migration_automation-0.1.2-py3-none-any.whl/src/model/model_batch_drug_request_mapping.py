import logging
from typing import List, Dict, Any, Set

from peewee import (IntegerField, ForeignKeyField, PrimaryKeyField, IntegrityError, InternalError, CharField, DataError,
                    DoesNotExist, fn, DateTimeField)

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger


class BatchDrugRequestMapping(BaseModel):
    id = PrimaryKeyField()
    facility_dist_id = ForeignKeyField(FacilityDistributionMaster)
    txr = CharField(max_length=8, null=True)
    daw = IntegerField()
    source_unique_drug_id = ForeignKeyField(UniqueDrug, related_name="source_unique_drug_id")
    requested_unique_drug_id = ForeignKeyField(UniqueDrug, related_name="requested_unique_drug_id")
    created_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_drug_request_mapping"

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Inserts multiple records in the BatchDrugData.
        """
        logger.debug("Inside BatchDrugRequestMapping.insert_data")
        try:
            cls.insert_many(data_list).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def get_mapping_data_by_facility_dist_id(cls, facility_dist_id: int) -> Dict[str, Dict[str, Any]]:
        """
        Fetches the data grouped by requested_unique_drug_id and daw for the given facility_dist_id.
        """
        logger.debug("Inside model.get_mapping_data_by_facility_dist_id")
        result_dict: Dict[str, Dict[str, Any]] = dict()
        try:
            query = cls.select(cls.requested_unique_drug_id,
                               cls.daw,
                               fn.GROUP_CONCAT(cls.source_unique_drug_id).coerce(False).alias(
                                   'source_unique_drug_ids')).dicts() \
                .where(cls.facility_dist_id == facility_dist_id) \
                .group_by(cls.requested_unique_drug_id, cls.daw)
            if query.count() > 0:
                for record in query:
                    source_unique_drug_ids: Set[int] = set()
                    for unique_drug_id in list(record['source_unique_drug_ids'].split(",")):
                        source_unique_drug_ids.add(int(unique_drug_id))

                    result_dict[str(record["daw"]) + "##" + str(record["requested_unique_drug_id"])] = {
                        "requested_unique_drug_id": int(record["requested_unique_drug_id"]),
                        "daw": int(record["daw"]),
                        "source_unique_drug_ids": list(source_unique_drug_ids)
                    }
            else:
                raise DoesNotExist("There are no values for the given unique_id")
            return result_dict

        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
