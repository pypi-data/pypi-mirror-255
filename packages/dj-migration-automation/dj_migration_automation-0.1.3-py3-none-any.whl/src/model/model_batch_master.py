import os
import sys

from peewee import CharField, IntegerField, ForeignKeyField, DateTimeField, FloatField, \
    PrimaryKeyField, InternalError, IntegrityError, DoesNotExist, DataError, fn
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster

logger = settings.logger


class BatchMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField(null=True)
    status = ForeignKeyField(CodeMaster, null=True, related_name="batch_status")
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    split_function_id = IntegerField(null=True)
    scheduled_start_time = DateTimeField(default=get_current_date_time(), null=True)
    estimated_processing_time = FloatField(null=True)
    imported_date = DateTimeField(null=True)
    mfd_status = ForeignKeyField(CodeMaster, null=True, related_name='batch_mfd_status_id')
    sequence_no = IntegerField(default=0)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"

    @classmethod
    def db_get(cls, batch_id):
        """Returns batch record"""
        try:
            return BatchMaster.get(id=batch_id)
        except (InternalError, IntegrityError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_batch_status(cls, batch_id):
        """Returns batch status"""
        try:
            query = BatchMaster.select(BatchMaster.status).dicts().where(BatchMaster.id == batch_id).get()
            return query['status']
        except (InternalError, IntegrityError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_batch_id(cls, system_id):
        """Returns batch record"""
        try:
            batch_ids = []
            query = BatchMaster.select(BatchMaster.id).dicts() \
                .where((BatchMaster.status.not_in([settings.BATCH_PROCESSING_COMPLETE, settings.BATCH_IMPORTED,
                                                   settings.BATCH_DELETED])) & (BatchMaster.system_id == system_id))
            for record in query:
                batch_ids.append(record['id'])
            return batch_ids
        except (InternalError, IntegrityError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_is_imported(cls, batch_id):
        """
        Returns True if batch is imported, False otherwise
        if batch does not exist returns None
        :param batch_id: int
        :return: bool | None
        """
        try:
            batch_status = BatchMaster.select(CodeMaster.id).dicts() \
                .join(CodeMaster, on=CodeMaster.id == BatchMaster.status) \
                .where(BatchMaster.id == batch_id).get()
            return batch_status['id'] == settings.BATCH_IMPORTED
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return None
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_system_id_from_batch_id(cls, batch_id):
        """
        Function to get system id of given batch_id
        todo: Move to batch master dao
        @param batch_id: int
        @return:
        """
        try:
            query = BatchMaster.select(BatchMaster.system_id).dicts() \
                .where(BatchMaster.id == batch_id)

            for record in query:
                return record['system_id']

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return None

    @classmethod
    def db_set_status(cls, batch_id, status, user_id):
        """ Sets status of batch id """
        try:
            logger.info('Setting Status {} for batch_id {}'.format(status, batch_id))
            status = BatchMaster.update(status=status,
                                        modified_by=user_id,
                                        modified_date=get_current_date_time()) \
                .where(BatchMaster.id == batch_id).execute()
            return status
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_split_function_id(cls, batch_id, split_function_id):
        """ Sets status of batch id """
        try:
            logger.info('getting split if {} for batch_id {}'.format(split_function_id, batch_id))

            record = BatchMaster.select(BatchMaster.id, BatchMaster.split_function_id).dicts() \
                .where(BatchMaster.id == batch_id).get()

            if split_function_id is None:
                response = record['split_function_id']
            elif record['split_function_id'] is None or (record['split_function_id'] != split_function_id):
                BatchMaster.update(split_function_id=split_function_id) \
                    .where(BatchMaster.id == batch_id) \
                    .execute()
                response = split_function_id
            else:
                response = record['split_function_id']
            return response

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_set_sequence(cls, sequence_no, batch_id):
        """ Sets sequence """
        try:
            logger.info('db_set_sequence sequence for batch_id {}'.format(batch_id))
            status = BatchMaster.update(sequence_no=sequence_no).where(BatchMaster.id == batch_id).execute()
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def get_max_batch_date(cls):
        batch_status_list = [settings.BATCH_PENDING, settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
                             settings.BATCH_CANISTER_TRANSFER_DONE,
                             settings.BATCH_IMPORTED, settings.BATCH_PROCESSING_COMPLETE,
                             settings.BATCH_ALTERNATE_DRUG_SAVED,
                             settings.BATCH_MFD_USER_ASSIGNED]
        try:
            query = BatchMaster.select().where(BatchMaster.status.in_(batch_status_list)) \
                .order_by(BatchMaster.id.desc()).limit(1)

            for record in query.dicts():
                return str(record["created_date"])

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return None

    @classmethod
    def db_get_latest_progress_batch_id(cls, system_id: int):
        """ get the latest progress batch_id which is in progress  'i.e' imported"""
        try:
            batch_id = BatchMaster.select(BatchMaster.id).dicts().order_by(BatchMaster.id.desc()).where(
                BatchMaster.status == settings.BATCH_IMPORTED, BatchMaster.system_id == system_id).get()
            logger.info("batch_id {}".format(batch_id['id']))
            return batch_id['id']

        except DoesNotExist as e:
            logger.info("db_get_latest_progress_batch_id: No batch is imported")
            return None

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_top_batch_id(cls, system_id: int):
        """ returns batch id of batch which is going to be imported next"""
        try:
            batch_id = BatchMaster.select(BatchMaster.id).dicts().order_by(BatchMaster.id.desc()).where(
                BatchMaster.status << [settings.BATCH_ALTERNATE_DRUG_SAVED,
                                       settings.BATCH_CANISTER_TRANSFER_RECOMMENDED,
                                       settings.BATCH_MFD_USER_ASSIGNED,
                                       settings.BATCH_CANISTER_TRANSFER_DONE],
                BatchMaster.system_id == system_id).get()
            return batch_id["id"]

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_top_batch_id_with_any_status(cls, track_date, offset, system_id):
        """ returns the latest batch id"""
        try:
            batch_id = BatchMaster.select(BatchMaster.id).dicts().order_by(BatchMaster.id.desc()).where(
                                BatchMaster.system_id == system_id).where(fn.DATE(fn.CONVERT_TZ(
                BatchMaster.created_date, settings.TZ_UTC,
                                         offset)) <= track_date, BatchMaster.status.not_in(
                                                                              [settings.BATCH_DELETED]
                                                                              )).get()
            return batch_id

        except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
            logger.error("error in get_batch_in_progress_today {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_batch_in_progress_today: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            raise e

    @classmethod
    def db_get_all_batch_list_from_system(cls, system_id: int):
        """ Function to return batch list that are pending to process or imported"""
        try:
            batch_query = BatchMaster.select(BatchMaster.id, BatchMaster.status).dicts() \
                .where(BatchMaster.status.not_in([settings.BATCH_PROCESSING_COMPLETE,
                                                  settings.BATCH_IMPORTED,
                                                  settings.BATCH_DELETED]),
                       BatchMaster.system_id == system_id) \
                .order_by(BatchMaster.id)

            return batch_query

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_last_imported_batch_by_system(cls, status: int, system_id: int):
        try:
            return BatchMaster.select(BatchMaster.id, BatchMaster.name).dicts()\
                .order_by(BatchMaster.id.desc())\
                .where(BatchMaster.status == status,
                       BatchMaster.system_id == system_id).get()

        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_validate_batch_id_dao(cls, batch_id):
        try:
            batch_data = BatchMaster.get(id=batch_id)
            if batch_data:
                return True
            return False
        except (IntegrityError, InternalError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            return False
        except Exception as e:
            logger.error(e, exc_info=True)
            return False
