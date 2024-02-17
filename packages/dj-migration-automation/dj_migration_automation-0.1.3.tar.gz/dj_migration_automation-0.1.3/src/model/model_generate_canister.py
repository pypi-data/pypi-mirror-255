from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, IntegrityError, InternalError, \
    DataError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_canister import logger
from src.model.model_canister_stick import CanisterStick
from src.model.model_code_master import CodeMaster
from src.model.model_drug_master import DrugMaster


class GenerateCanister(BaseModel):
    """

    """
    id = PrimaryKeyField()
    drug_id = ForeignKeyField(DrugMaster)
    company_id = IntegerField()
    system_id = IntegerField()
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    requested_canister_count = IntegerField(default=0)
    odoo_request_id = IntegerField()
    status = ForeignKeyField(CodeMaster)
    canister_stick_id = ForeignKeyField(CanisterStick, null=True)
    fulfilled_requested_canister_count = IntegerField(default=0)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "generate_canister"

    @classmethod
    def db_add_generate_canister_data(cls, drug_data_details):
        try:
            query = BaseModel.db_create_record(drug_data_details, GenerateCanister, get_or_create=False)
            return True, query.id

        except IntegrityError as e:
            return False, e
        except InternalError as e:
            return False, e
        except DataError as e:
            return False, e

    @classmethod
    def db_update_requested_canister_status(cls, odoo_req_id, requested_canister_status):
        try:
            status = cls.update(status=requested_canister_status).where(cls.odoo_request_id == odoo_req_id).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_insert_canister_data(cls, canister_data):
        """
         insert canisters data to table
        :return:
        """
        try:
            status = cls.insert_many(canister_data).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise