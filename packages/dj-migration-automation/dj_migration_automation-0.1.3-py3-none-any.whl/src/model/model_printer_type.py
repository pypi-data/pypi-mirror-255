from peewee import PrimaryKeyField, CharField, InternalError, IntegrityError
import settings
from dosepack.base_model.base_model import BaseModel

logger = settings.logger


class PrinterType(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)
    description = CharField(max_length=255, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "printer_type"

    @classmethod
    def db_get(cls):
        """
        Returns all printer types

        :return: list
        """
        printer_types = list()
        try:
            for record in PrinterType.select(PrinterType.name,
                                             PrinterType.id,
                                             PrinterType.description).dicts():
                printer_types.append(record)
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

        return printer_types
