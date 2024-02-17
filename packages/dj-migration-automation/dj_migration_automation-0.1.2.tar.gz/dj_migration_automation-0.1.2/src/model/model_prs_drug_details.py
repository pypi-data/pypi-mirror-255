from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_code_master import CodeMaster
from src.model.model_unique_drug import UniqueDrug
from src import constants

logger = settings.logger


class PRSDrugDetails(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    status = ForeignKeyField(CodeMaster)
    done_by = IntegerField(null=True)
    verified_by = IntegerField(null=True)
    registered_by = IntegerField(null=True)
    comments = CharField(null=True)
    face1 = TextField(null=True)
    face2 = TextField(null=True)
    side_face = TextField(null=True)
    predicted_qty = IntegerField(default=0)
    expected_qty = IntegerField(default=0)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'prs_drug_details'

    @classmethod
    def insert_data_in_prs(cls, data_dict):
        logger.debug("In insert_data_in_prs")
        try:
            prs_record = BaseModel.db_create_record(data_dict, cls, get_or_create=True)
            return prs_record
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e)
            raise

    @classmethod
    def get_pending_drug_ids(cls):
        logger.debug("In get_pending_drug_ids")
        try:
            unique_drug_ids = []
            query = cls.select(cls.unique_drug_id).dicts().where(cls.status == constants.PRS_DRUG_STATUS_PENDING)
            for record in query:
                unique_drug_ids.append(int(record['unique_drug_id']))
            logger.debug(unique_drug_ids)
            return unique_drug_ids
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e)
            raise

    @classmethod
    def db_get_prs_images_from_drug_id(cls, unique_drug_id):
        try:
            query = cls.select(cls.face1, cls.face2, cls.side_face).dicts().where(cls.unique_drug_id==unique_drug_id).get()
            return query
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e)
            raise

    @classmethod
    def db_update_prs_images_for_unique_drug(cls, face_1_list, face_2_list, side_face_list, unique_drug_id):
        try:
            status = cls.update(face1=face_1_list, face2=face_2_list, side_face=side_face_list) \
                        .where(cls.unique_drug_id == unique_drug_id).execute()
            return status
        except DoesNotExist as e:
            logger.error("error in db_update_prs_images_for_unique_drug {}".format(e))
            return None
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e)
            raise

