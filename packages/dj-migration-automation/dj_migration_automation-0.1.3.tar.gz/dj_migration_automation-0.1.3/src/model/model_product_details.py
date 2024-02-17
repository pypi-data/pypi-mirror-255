from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_location_master import LocationMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_code_master import CodeMaster

logger = settings.logger


class ProductDetails(BaseModel):
    id = PrimaryKeyField()
    product_id = IntegerField(null=False, unique=True)
    rfid = FixedCharField(null=True, unique=True, max_length=32)
    lot_number = CharField(null=True)
    delivery_date = DateTimeField(default=None, null=True)
    ndc = ForeignKeyField(DrugMaster, to_field='ndc')
    status = ForeignKeyField(CodeMaster, default=settings.PRODUCT_TESTING_PENDING)
    canister_serial_number = CharField(null=True, unique=True, default=None)
    transfer_location = ForeignKeyField(LocationMaster, default=None, null=True)
    is_skipped = BooleanField(default=False)
    development_needed = BooleanField(default=False)
    created_date = DateTimeField(default=None)
    modified_date = DateTimeField(default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "product_details"

    @classmethod
    def db_create_product_details(cls, insert_product_data):
        try:
            return ProductDetails.get_or_create(**insert_product_data)
        except IntegrityError as e:
            logger.warning(f"Skipping duplicate record: {insert_product_data}")
        except Exception as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_product_delivery(cls, lot_number):
        try:
            return ProductDetails.update(delivery_date=get_current_date_time(),
                                         modified_date=get_current_date_time()).where(
                ProductDetails.lot_number == lot_number).execute()
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e
