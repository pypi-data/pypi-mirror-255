from peewee import PrimaryKeyField, CharField

import settings
from dosepack.base_model.base_model import BaseModel
logger = settings.logger


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"

    @staticmethod
    def get_initial_data():
        return [
            dict(id=1, name="PackStatus"),
            dict(id=2, name="FileStatus"),
            dict(id=3, name="TemplateStatus"),
            dict(id=4, name="OrderStatus"),
            dict(id=5, name="DocumentType"),
            dict(id=6, name="PackFillReason"),
            dict(id=7, name="BatchStatus"),
            dict(id=8, name="PVS"),
            dict(id=9, name="DrugBottle"),
            dict(id=10, name="FacilitySchedule"),
            dict(id=11, name="BatchChange"),
            dict(id=12, name="DrugVerification"),
            dict(id=13, name="FacilityDistributionStatus"),
            dict(id=14, name="extPackDetailsFromIPS"),
            dict(id=15, name="DrugDispensingTemplatesModule"),
            dict(id=16, name="BatchSchedulingModule"),
            dict(id=17, name="PackPreProcessingModule"),
            dict(id=18, name="CanisterSize"),
            dict(id=19, name="DrugUsage"),
        ]


