from peewee import PrimaryKeyField, ForeignKeyField, BooleanField, IntegerField, DateTimeField, IntegrityError, \
    InternalError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger


# TODO Include training thing in mapping of slotdetails ID
# Also provide api for this to PVS  # based on count > somecount


class DrugTraining(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    status = BooleanField(default=False)
    image_crops_count = IntegerField(default=0)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_training'

    @classmethod
    def db_update_or_create(cls, drug_id, qty=1):
        """
        Updates count of drug if not creates a record
        :param drug_id:
        :param qty:
        :return:
        """
        try:
            record, created = DrugTraining.get_or_create(unique_drug_id=drug_id)
            if not created:
                DrugTraining.update(image_crops_count=record.image_crops_count + qty,
                                    modified_date=get_current_date_time()) \
                    .where(DrugTraining.unique_drug_id == drug_id).execute()
            return record
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_reduce_count(cls, drug_id, qty=1):
        """
        Updates count of drug if not creates a record
        :param drug_id:
        :param qty:
        :return:
        """
        try:
            DrugTraining.update({DrugTraining.image_crops_count: DrugTraining.image_crops_count - qty,
                                 DrugTraining.modified_date: get_current_date_time()}) \
                .where(DrugTraining.unique_drug_id == drug_id).execute()
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_drugs_by_count(cls, count, status):
        """
        Returns drug which have more count than given count and status False
        :param count: int
        :param status: bool
        :return: list
        """
        drugs = list()
        try:
            for record in DrugTraining.select(DrugTraining,
                                              UniqueDrug.formatted_ndc,
                                              UniqueDrug.txr,
                                              UniqueDrug.drug_id) \
                    .join(UniqueDrug, on=DrugTraining.unique_drug_id == UniqueDrug.id).dicts() \
                    .where(DrugTraining.image_crops_count > count,
                           DrugTraining.status == status):
                drugs.append(record)
            return drugs
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_drugs(cls, fndc_list, txr_list):
        """
        Returns drug which
        filter_drug will be used when available and will return drug for that list only
        :param fndc_list: list
        :return: list
        """
        drugs = list()
        try:
            for record in DrugTraining.select(DrugTraining,
                                              UniqueDrug.formatted_ndc,
                                              UniqueDrug.txr,
                                              UniqueDrug.drug_id) \
                    .join(UniqueDrug, on=DrugTraining.unique_drug_id == UniqueDrug.id).dicts() \
                    .where(UniqueDrug.formatted_ndc << fndc_list,
                           UniqueDrug.txr << txr_list):
                drugs.append(record)
            return drugs
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_drugs_by_status(cls, status):
        """
        Returns drug which has given status
        :param status: status
        :return: list
        """
        drugs = list()
        try:
            for record in DrugTraining.select(DrugTraining,
                                              UniqueDrug.formatted_ndc,
                                              UniqueDrug.txr,
                                              UniqueDrug.drug_id) \
                    .join(UniqueDrug, on=DrugTraining.unique_drug_id == UniqueDrug.id).dicts() \
                    .where(DrugTraining.status == status):
                drugs.append(record)
            return drugs
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_status(cls, status, unique_drug_id_list):

        try:
            status = cls.update(status=int(status)) \
                .where(cls.unique_drug_id << unique_drug_id_list).execute()

            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
