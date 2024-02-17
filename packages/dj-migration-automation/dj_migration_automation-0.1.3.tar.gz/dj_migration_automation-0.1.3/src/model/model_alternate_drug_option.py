from peewee import PrimaryKeyField, ForeignKeyField, BooleanField, IntegerField, DateTimeField, InternalError, \
    IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger


class AlternateDrugOption(BaseModel):
    """
    This table data serves as the input for the drug consideration in the Batch-Distribution Algorithm.
    """
    id = PrimaryKeyField()
    facility_dis_id = ForeignKeyField(FacilityDistributionMaster)
    unique_drug_id = ForeignKeyField(UniqueDrug, related_name='unique_drug_id')
    alternate_unique_drug_id = ForeignKeyField(UniqueDrug, related_name='alternate_unique_drug_id')
    active = BooleanField()
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "alternate_drug_option"

    @classmethod
    def add_alternate_drug(cls, info_list):
        try:
            status = cls.insert_many(info_list).execute()
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def remove_alternate_drug_distribution_id(cls, info_dict: dict) -> bool:
        try:
            if info_dict.get('unique_drug_ids', None):
                query = cls.select(cls.alternate_unique_drug_id).dicts() \
                    .where(cls.facility_dis_id == info_dict['facility_distribution_id'],
                           cls.unique_drug_id << info_dict['unique_drug_ids'])
                alternate_unique_drug_id = [record['alternate_unique_drug_id'] for record in query]
                status = cls.update(active=False,
                                    modified_date=get_current_date_time(),
                                    modified_by=info_dict['user_id']) \
                    .where(cls.alternate_unique_drug_id << alternate_unique_drug_id,
                           cls.facility_dis_id == info_dict['facility_distribution_id']).execute()
            elif info_dict.get('alternate_unique_drug_ids', None):
                status = cls.update(active=False,
                                    modified_date=get_current_date_time(),
                                    modified_by=info_dict['user_id']) \
                    .where(cls.alternate_unique_drug_id << info_dict['alternate_unique_drug_ids'],
                           cls.facility_dis_id == info_dict['facility_distribution_id']).execute()
            else:
                status = cls.update(active=False,
                                    modified_date=get_current_date_time(),
                                    modified_by=info_dict['user_id']) \
                    .where(cls.facility_dis_id == info_dict['facility_distribution_id']).execute()
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_alternate_drug_option(cls, update_dict: dict, alt_drug_list: list) -> bool:
        """
        update alternate drug option by alt_drug_list
        :return:
        """
        try:
            status = AlternateDrugOption.update(**update_dict) \
                .where(AlternateDrugOption.alternate_unique_drug_id << alt_drug_list).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_remove_alternate_drug_by_id(cls, update_dict: dict, alt_drug_option_id: list) -> bool:
        """
        update alternate drug option by alt_drug_option_id_list
        :return:
        """
        try:
            status = AlternateDrugOption.update(**update_dict) \
                .where(AlternateDrugOption.id << alt_drug_option_id).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e
