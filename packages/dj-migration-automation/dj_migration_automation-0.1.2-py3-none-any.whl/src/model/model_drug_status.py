from peewee import PrimaryKeyField, ForeignKeyField, BooleanField, DateTimeField, DateField, InternalError, \
    IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_drug_master import DrugMaster


logger = settings.logger


class DrugStatus(BaseModel):
    id = PrimaryKeyField()
    drug_id = ForeignKeyField(DrugMaster, unique=True)
    ext_status = BooleanField(default=False)
    ext_status_updated_date = DateTimeField(default=None, null=True)
    last_billed_date = DateField(default=None, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_status"

    @classmethod
    def db_update_status(cls, drug_id, status, update_date):
        """ Updates drug status of ips """
        try:
            result = cls.db_update_or_create({'drug_id': drug_id},
                                             {'ext_status': status, 'ext_status_updated_date': update_date})
            logger.info("drug_status_updated_by_IPS_for_drug_id " + str(drug_id) + " with status " + str(status))
            return result
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise