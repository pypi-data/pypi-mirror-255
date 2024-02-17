"""
    @file: src/model/model_pvs_drug_count.py
    @type: file
    @desc: model class for db table pvs_drug_count
"""

from playhouse.migrate import *

import settings
from src.model.model_unique_drug import UniqueDrug
from settings import logger
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pvs_slot import PVSSlot


class PVSDrugCount(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_id = ForeignKeyField(PVSSlot, related_name='pvsdrugcount_pvs_slot_id')
    unique_drug_id = ForeignKeyField(UniqueDrug, related_name='pvsdrugcount_unique_drug_id')
    expected_qty = DecimalField(null=True)
    predicted_qty = DecimalField(null=True)
    robot_drop_qty = DecimalField(null=True)
    created_date = DateTimeField(default=get_current_date_time, null=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pvs_drug_count"

    @classmethod
    def db_fetchall_pvs_drug_count(cls):
        """
        Method to get all pvs_drug_counts
        @return: dict
        """
        try:
            query = PVSDrugCount.select().dicts()
            return query

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e)
            raise

    @classmethod
    def db_get_pvs_drug_count(cls, **kwargs):
        """
        Method to get pvs_drug_count with clauses
        @param kwargs: key, value pairs needed for where condition
        @return: dict
        """
        try:
            clauses = list()
            for field, value in kwargs.items():
                clauses.append((getattr(PVSDrugCount, field) == value))
            if clauses:
                query = PVSDrugCount.select(PVSDrugCount).dicts().where(clauses)
                return query
            else:
                logger.error("There must be atleast one value in clauses")
                return None
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e)
            raise