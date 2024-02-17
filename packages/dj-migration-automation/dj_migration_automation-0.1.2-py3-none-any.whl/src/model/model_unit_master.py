from peewee import PrimaryKeyField, CharField, IntegrityError, InternalError, DataError, DoesNotExist

import settings
from dosepack.base_model.base_model import BaseModel


class UnitMaster(BaseModel):
    """
    Class to store the unit details.
    """
    id = PrimaryKeyField()
    name = CharField()
    type = CharField()
    symbol = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "unit_master"


    @classmethod
    def insert_unit(cls, unit_data):
        """
        To insert a unit data.
        :param unit_data:
        :return:
        """
        try:
            query = BaseModel.db_create_record(unit_data, UnitMaster, get_or_create=False)
            return query.id

        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError
        except DataError as e:
            raise DataError

    @classmethod
    def get_units_by_type(cls, unit_type):
        """
        To get the details of all of the units by the unit type ( i.e unit type can be volume, currency, etc.)
        :param unit_type:
        :return:
        """
        db_result = list()
        try:
            query = UnitMaster.select().dicts().where(UnitMaster.type == unit_type)
            for unit in query:
                db_result.append(unit)
            return db_result

        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError
        except DataError as e:
            raise DataError

    @classmethod
    def get_unit_by_unit_id(cls, unit_id):
        """
        To get the details of a unit by the unit id.
        @param unit_id:
        @return:
        """
        try:
            data = UnitMaster.select().dicts().where(UnitMaster.id == unit_id).get()
            return data

        except (InternalError, IntegrityError, DataError,DoesNotExist) as e:
            raise e

    @classmethod
    def get_unit_data_by_name(cls, unit_name):
        """
        To get the unit data by the unit name.
        @param unit_name:
        @return:
        """
        try:
            data = UnitMaster.select().dicts().where(UnitMaster.name == unit_name).get()

            return data

        except (InternalError, IntegrityError, DataError,DoesNotExist) as e:
            raise e
