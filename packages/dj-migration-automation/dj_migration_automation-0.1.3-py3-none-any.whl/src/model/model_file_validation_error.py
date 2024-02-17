import functools
import operator
from typing import Dict, Any

from peewee import PrimaryKeyField, ForeignKeyField, CharField, DateTimeField, DoesNotExist, InternalError, \
    IntegrityError
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_file_header import FileHeader


logger = settings.logger


class FileValidationError(BaseModel):
    id = PrimaryKeyField()
    file_id = ForeignKeyField(FileHeader)
    patient_name = CharField(max_length=50)
    patient_no = CharField(max_length=50)
    column = CharField(max_length=50)
    value = CharField(max_length=255)
    message = CharField(max_length=100)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_validation_error"

            indexes = (
                (('file_id', 'patient_no', 'column', 'value', 'message'), True),
            )

    @classmethod
    def db_get_file_validation(cls, clauses) -> Dict[int, Any]:
        file_validation_data: Dict[int, Any] = dict()

        try:
            query = cls.select(cls).dicts() \
                .where(functools.reduce(operator.and_, clauses))

            for record in query:
                file_validation_data[record["id"]] = record
            return file_validation_data
        except DoesNotExist:
            return {}
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise
