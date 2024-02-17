import datetime
from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, SmallIntegerField, CharField, DateField, TimeField, \
    InternalError, IntegrityError, DoesNotExist, DataError
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date, get_current_time
from src.model.model_pack_details import PackDetails
from src.model.model_patient_master import PatientMaster
logger = settings.logger


class PrintQueue(BaseModel):
    """
        @class: print_queue.py
        @createdBy: Manish Agarwal
        @createdDate: 04/19/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/19/2016
        @type: file
        @desc: logical class for table task_queue
    """
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    pack_display_id = IntegerField()
    patient_id = ForeignKeyField(PatientMaster)
    printing_status = SmallIntegerField()
    filename = CharField(null=True, max_length=30)
    printer_code = CharField(max_length=55)
    file_generated = SmallIntegerField(default=0)
    created_by = IntegerField()
    created_date = DateField(default=get_current_date)
    created_time = TimeField(default=get_current_time)
    page_count = SmallIntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "print_queue"

    @classmethod
    def db_get_by_id(cls, print_queue_id):
        """
        Returns print queue record given id

        :param print_queue_id:
        :return: dict
        """
        print_queue_data = dict()
        try:
            for record in PrintQueue.select().dicts().where(PrintQueue.id == print_queue_id):
                record["created_date"] = datetime.datetime.combine(
                    record["created_date"],
                    record["created_time"]
                )
                print_queue_data = record
            return print_queue_data
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_task_status(cls, record_ids, status):
        """
        Updates print status of print job and returns update status
        :param record_ids: list
        :param status: int
        :return: None | int
        """
        try:
            if record_ids:
                status = PrintQueue.update(printing_status=int(status)) \
                    .where(PrintQueue.id << record_ids).execute()
                return status
            return None
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_printer_code(cls, pack_ids, printer_code, status=0):
        """
        update printer code for given pack_ids and printing_status
        @param pack_ids:
        @param printer_code:
        @param status:
        @return:
        """
        try:
            if pack_ids:
                status = PrintQueue.update(printer_code=printer_code) \
                    .where(PrintQueue.pack_id << pack_ids, PrintQueue.printing_status == status).execute()
                return status
            return None
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_create(cls, pack_id, patient_id, pack_display_id, user_id, file_name, printer_code, page_count,
                  file_generated=False):
        """
        Creates entry in PrintQueue as print task

        :param pack_id: pack id
        :param patient_id: patient id
        :param pack_display_id: pharmacy pack id
        :param user_id: user id who requested print
        :param file_name: label file name
        :param printer_code: code of printer to be used
        :param page_count: number of pages required in label
        :return: peewee.Model (PrintQueue)
        """
        try:
            record = BaseModel.db_create_record({
                "pack_id": pack_id,
                "printing_status": 0,
                "patient_id": patient_id,
                "pack_display_id": pack_display_id,
                "created_by": user_id,
                "created_date": get_current_date(),
                "filename": file_name,
                "printer_code": printer_code,
                "file_generated": file_generated,
                "page_count": page_count,
            }, PrintQueue, get_or_create=False)
            return record
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise
