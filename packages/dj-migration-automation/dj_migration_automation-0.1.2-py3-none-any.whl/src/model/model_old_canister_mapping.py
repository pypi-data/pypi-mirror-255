from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_canister_master import CanisterMaster
from src.model.model_product_details import ProductDetails

logger = settings.logger


class OldCanisterMapping(BaseModel):
    id = PrimaryKeyField()
    product_id = ForeignKeyField(ProductDetails, null=True, default=None, to_field='product_id')
    old_canister_id = ForeignKeyField(CanisterMaster, default=None, related_name='old_can_id', null=True)
    new_canister_id = ForeignKeyField(CanisterMaster, default=None, related_name='new_can_id', null=True)
    created_by = CharField(null=True, default=None)
    created_date = DateTimeField(default=get_current_date_time())
    modified_date = DateTimeField(default=get_current_date_time())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "old_canister_mapping"

    @classmethod
    def db_create_product_mapping(cls, insert_mapping_data):
        try:
            return OldCanisterMapping.insert_many(insert_mapping_data).execute()
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e
