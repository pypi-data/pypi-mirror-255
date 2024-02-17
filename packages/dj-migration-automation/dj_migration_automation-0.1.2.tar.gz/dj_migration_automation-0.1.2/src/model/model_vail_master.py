import settings
from peewee import *
from src.model.model_drug_master import DrugMaster
from dosepack.base_model.base_model import BaseModel
from src.model.model_pack_details import PackDetails
from src.model.model_reuse_pack_drug import ReusePackDrug
from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class VailMaster(BaseModel):
    """
    database table to manage the deleted pack data for RTS and Resuse
    """
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    drug_id = ForeignKeyField(DrugMaster)
    total_quantity = DecimalField(decimal_places=2, max_digits=7)
    available_quantity = DecimalField(decimal_places=2, max_digits=7)
    expiry_date = CharField()
    vail_type = IntegerField()
    vail_status = IntegerField()
    current_status = IntegerField()
    reason = CharField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    item_id = ForeignKeyField(ReusePackDrug)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "vail_master"

