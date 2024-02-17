import functools
import operator

from peewee import PrimaryKeyField, CharField, ForeignKeyField, BooleanField, fn, DoesNotExist, InternalError, \
    IntegrityError, DataError, IntegerField, DecimalField, DateTimeField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_dosage_type import DosageType
from src.model.model_drug_master import DrugMaster


logger = settings.logger


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()
    formatted_ndc = CharField()
    txr = CharField(null=True)
    drug_id = ForeignKeyField(DrugMaster)
    lower_level = BooleanField(default=False)  # drug to be kept at lower level so pill doesn't break while filling
    drug_usage = ForeignKeyField(CodeMaster, default=settings.CANISTER_DRUG_USAGE["Slow Moving"])
    is_powder_pill = IntegerField(null=True)
    min_canister = CharField(default=2, null=True)
    max_canister = CharField(default=2, null=True)
    dosage_type = ForeignKeyField(DosageType, null=True, default=None, related_name='dosage_type')
    packaging_type = ForeignKeyField(CodeMaster, null=True, default=None, related_name='packaging_type')
    coating_type = CharField(null=True)
    is_zip_lock_drug = IntegerField(null=True)
    is_delicate = BooleanField(default=False)
    unit_weight = DecimalField(null=True)
    modified_date = DateTimeField(null=True, default=get_current_date_time)

    # one of the drug id which has same formatted ndc and txr number
    #  TODO think only drug id or (formatted_ndc, txr)

    class Meta:
        indexes = (
            (('formatted_ndc', 'txr'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'

    @classmethod
    def concated_fndc_txr_field(cls, sep='#'):
        """ Returns CONCAT on formatted_ndc, `sep`, txr """
        return fn.CONCAT(
            cls.formatted_ndc, sep, fn.IFNULL(cls.txr, '')
        )

    @classmethod
    def db_create_unique_drug(cls, drug_master_data):
        try:
            return UniqueDrug.insert(formatted_ndc=drug_master_data['formatted_ndc'],
                                     txr=drug_master_data['txr'],
                                     drug_id=drug_master_data['id']).execute()
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_or_create(cls, formatted_ndc, txr, drug_id=None):
        """
        Returns `UniqueDrug` for given formatted ndc, txr combination
        :param formatted_ndc:
        :param txr:
        :param drug_id:
        :return:
        """
        try:
            clauses = list()
            clauses.append((UniqueDrug.formatted_ndc == formatted_ndc))
            if txr is None:
                clauses.append((UniqueDrug.txr.is_null(True)))
            else:
                clauses.append((UniqueDrug.txr == txr))
            return UniqueDrug.select().where(functools.reduce(operator.and_, clauses)).get()
        except DoesNotExist:
            if not drug_id:
                clauses = list()
                clauses.append((DrugMaster.formatted_ndc == formatted_ndc))
                if txr is None:
                    clauses.append((DrugMaster.txr.is_null(True)))
                else:
                    clauses.append((DrugMaster.txr == txr))
                drug = DrugMaster.select().where(functools.reduce(operator.and_, clauses)).get()
                drug_id = drug.id
            unique_drug = UniqueDrug.create(**{
                'formatted_ndc': formatted_ndc,
                'txr': txr,
                'drug_id': drug_id
            })
            return unique_drug

    @classmethod
    def db_get_fndc_txr_by_unique_id(cls, unique_ids: list) -> list or None:
        """
        Returns `UniqueDrug` for given formatted ndc, txr combination
        :param unique_ids:
        :return:
        """
        try:
            unique_drug_data = []
            clauses = list()
            clauses.append((UniqueDrug.id << unique_ids))
            query = UniqueDrug.select().where(functools.reduce(operator.and_, clauses))
            for record in query.dicts():
                unique_drug_data.append(record)

            return unique_drug_data

        except DoesNotExist:
            return None

        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError(e)

    @classmethod
    def db_get_unique_drug_id(cls, formatted_ndc_txr_list):
        """

        @param formatted_ndc_txr_list: list of formatted_ndc, txr combined by "_"
        @return: dict
        """
        try:
            logger.info("Inside db_get_unique_drug_id with input {}".format(formatted_ndc_txr_list))
            unique_drug_data = dict()
            query = cls.select(cls.id, cls.formatted_ndc, cls.txr) \
                .where(fn.CONCAT(cls.formatted_ndc, '_', fn.IFNULL(UniqueDrug.txr, '')) << formatted_ndc_txr_list)
            for record in query.dicts():
                unique_drug_data[record['formatted_ndc'] + "_" + record['txr']] = record['id']
            logger.info("Inside db_get_unique_drug_id with Output {}".format(unique_drug_data))
            return unique_drug_data
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError(e)


    @classmethod
    def db_update_drug_id_by_id(cls, drug_id: int, unique_drug_id: int) -> int:
        try:
            response = cls.update(drug_id=drug_id).where(cls.id == unique_drug_id).execute()
            logger.info("Drug id: " + str(drug_id) + " updated in the UniqueDrug table for id: " + str(unique_drug_id))
            return response
        except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
            logger.error(e)
            raise

    @classmethod
    def db_get_drug_from_unique_drug(cls, canister_data):
        try:
            return UniqueDrug.select(DrugMaster).dicts() \
                .join(DrugMaster, on=DrugMaster.id == UniqueDrug.drug_id) \
                .where(fn.CONCAT(UniqueDrug.formatted_ndc, '##', fn.IFNULL(UniqueDrug.txr, '')) ==
                       canister_data['ndc##txr']).get()
        except (InternalError, IntegrityError, DoesNotExist, DataError, Exception) as e:
            logger.error(e)
            raise

    @classmethod
    def db_update_powder_pill_data(cls, fndc, txr, is_powder_pill):
        try:
            is_delicate = 0
            if is_powder_pill == constants.POWDER_PILL:
                is_delicate = 1

            response = cls.update(is_powder_pill=is_powder_pill, is_delicate=is_delicate).where(
                cls.formatted_ndc == fndc,
                cls.txr == txr)
            response.execute()
            logger.debug(" Response for db_update_powder_pill_data = {}".format(response))
            return response
        except (InternalError, IntegrityError, DoesNotExist, DataError, Exception) as e:
            logger.error(e)
            raise