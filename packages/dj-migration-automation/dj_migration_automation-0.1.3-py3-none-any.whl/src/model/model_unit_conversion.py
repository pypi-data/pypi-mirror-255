from peewee import PrimaryKeyField, ForeignKeyField, DecimalField, IntegrityError, InternalError, DataError

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_unit_master import UnitMaster


class UnitConversion(BaseModel):
    """
    Class to store the unit conversion ratios between the units of the same type.
    """
    id = PrimaryKeyField()
    convert_from = ForeignKeyField(UnitMaster, related_name='converted_from')
    convert_to = ForeignKeyField(UnitMaster, related_name='converted_into')
    conversion_ratio = DecimalField(decimal_places=6)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "unit_conversion"

    @classmethod
    def insert_conversion_ratio(cls, ratio_data):
        """
        To insert the conversion ratio between two units.
        :param ratio_data:
        :return:
        """
        try:
            query = BaseModel.db_create_record(ratio_data, UnitConversion, get_or_create=False)
            return query.id

        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError
        except DataError as e:
            raise DataError

    @classmethod
    def get_conversion_ratio_for_a_unit(cls, convert_from, convert_into):
        """
        To get the conversion ratio of two units.
        :param convert_from:
        :param convert_into:
        :return:
        """
        try:
            query = UnitConversion.select(UnitConversion.conversion_ratio).dicts().where(UnitConversion.convert_from ==
                                                                                         convert_from,
                                                                                         UnitConversion.convert_to ==
                                                                                         convert_into).get()
            return query['conversion_ratio']

        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError
        except DataError as e:
            raise DataError