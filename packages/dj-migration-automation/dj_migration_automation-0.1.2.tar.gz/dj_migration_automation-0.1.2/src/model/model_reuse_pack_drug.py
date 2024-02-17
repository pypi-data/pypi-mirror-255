import settings
from peewee import *
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_drug_master import DrugMaster
from dosepack.base_model.base_model import BaseModel
from src.model.model_pack_details import PackDetails
from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class ReusePackDrug(BaseModel):
    """
    database table to manage the deleted pack data for RTS and Resuse
    """
    id = PrimaryKeyField()
    item_id = CharField()
    pack_id = ForeignKeyField(PackDetails)
    drug_id = ForeignKeyField(DrugMaster)
    lot_number = CharField()
    total_quantity = DecimalField(decimal_places=2, max_digits=7)
    available_quantity = DecimalField(decimal_places=2, max_digits=7)
    status_id = ForeignKeyField(CodeMaster)
    expiry_date = CharField()
    company_id = IntegerField()
    # reason = CharField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "reuse_pack_drug"

    @classmethod
    def insert_multiple_record_in_reuse_pack_drug(cls, records_list):
        try:
            logger.info("In insert_multiple_record_in_reuse_pack_drug with input: {}".format(records_list))
            status = BaseModel.db_create_multi_record(records_list, ReusePackDrug)

            return status
        except Exception as e:
            logger.error("Error in insert_multiple_record_in_reuse_pack_drug: {}".format(e))
            raise e

    @classmethod
    def db_update_status_by_pack_id_drug_ids(cls, pack_id, drug_ids, status_id):
        try:
            logger.info("In db_update_drug_status_by_pack_id_drug_id with pack_id: {}, drug_id: {}, status_id: {}"
                        .format(pack_id, drug_ids, status_id))
            status = (ReusePackDrug.update(status_id=status_id,
                                           modified_date=get_current_date_time()
                                           )
                      .where(ReusePackDrug.pack_id == pack_id,
                             ReusePackDrug.drug_id << drug_ids).execute()
                      )

            return status
        except Exception as e:
            logger.error("Error in db_discard_drug_by_pack_id_drug_id: {}".format(e))
            raise e

    @classmethod
    def db_get_reuse_pack_drug_data_by_pack_id(cls, pack_ids: list):
        try:
            logger.info("In db_get_reuse_pack_drug_data_by_pack_id with pack_id: {}".format(pack_ids))
            reuse_pack_drug_data = (ReusePackDrug.select(ReusePackDrug)
                                    .dicts()
                                    .where(ReusePackDrug.pack_id << pack_ids))

            return reuse_pack_drug_data
        except Exception as e:
            logger.error("Error in db_get_reuse_pack_drug_data_by_pack_id: {}".format(e))
            raise e

    @classmethod
    def db_update_drugs_status_by_pack_id(cls, pack_ids, status_id):
        try:
            logger.info("In db_update_drugs_status_by_pack_id: pack_ids: {}, status_id: {}"
                        .format(pack_ids, status_id))

            update_status = (ReusePackDrug.update(status_id=status_id,
                                                  modified_date=get_current_date_time()
                                                  )
                             .where(ReusePackDrug.pack_id << pack_ids).execute()
                             )

            return update_status
        except Exception as e:
            logger.error("Error in db_update_drugs_status_by_pack_id: {}".format(e))
            raise e

    @classmethod
    def db_update_reuse_pack_drug_by_pack_id_drug_id(cls, pack_id, drug_id, update_dict):
        try:
            logger.info("In db_update_reuse_pack_drug_by_pack_id_drug_id with pack_id: {}, drug_id: {}, update_dict: {}"
                        .format(pack_id, drug_id, update_dict))
            update_status = (ReusePackDrug.update(**update_dict)
                             .where(ReusePackDrug.pack_id == pack_id,
                                    ReusePackDrug.drug_id == drug_id
                                    ).execute()
                             )

            return update_status
        except Exception as e:
            logger.error("Error in db_update_reuse_pack_drug_by_pack_id_drug_id: {}".format(e))
            raise e
