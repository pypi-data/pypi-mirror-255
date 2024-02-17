from peewee import PrimaryKeyField, CharField, IntegerField, DecimalField, ForeignKeyField, IntegrityError, \
    InternalError, DataError, DoesNotExist

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_unit_conversion import UnitConversion
from src.model.model_unit_master import UnitMaster


class ZoneMaster(BaseModel):
    """
        @desc: Class to store the zone details of company.
    """
    id = PrimaryKeyField()
    name = CharField(max_length=25)
    floor = IntegerField(null=True)
    length = DecimalField(decimal_places=2,null=True)
    height = DecimalField(decimal_places=2,null=True)
    width = DecimalField(decimal_places=2,null=True)
    company_id = IntegerField()  # Foreign key field of company table of dp auth
    x_coordinate = DecimalField(decimal_places=2,null=True)
    y_coordinate = DecimalField(decimal_places=2,null=True)
    dimensions_unit_id = ForeignKeyField(UnitMaster,null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "zone_master"
        indexes = (
            (('company_id', 'name'), True),
        )

    @classmethod
    def create_zone(cls, zone_data):
        """
        Create record for the new zone entry.
        @param zone_data: data of the new zone.
        @return: id of the zone entry created.
        """
        try:
            query = BaseModel.db_create_record(zone_data, ZoneMaster, get_or_create=False)
            return query.id

        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            raise e

    @classmethod
    def update_zone_dimensions(cls, company_id, zone_list):
        """
        Updates zones x_coordinate and y_coordinate
        :param company_id: company_id
        :param zone_list: list of dictionaries containing zone_id and respective updated coordinates values.
        :return: True
        """
        try:
            for zone in zone_list:
                query = ZoneMaster.update(x_coordinate=zone['x_coordinate'],
                                          y_coordinate=zone['y_coordinate']) \
                    .where(ZoneMaster.id == zone['id'], ZoneMaster.company_id == company_id).execute()

            return True

        except (IntegrityError, InternalError, DataError) as e:
            raise e

    @classmethod
    def verify_zone_id_for_company(cls, zone_id, company_id):
        """
        To verify whether the given zone_id exists for the given company_id.
        :param zone_id:
        :param company_id:
        :return: True if it exists otherwise False
        """
        try:
            company_id_in_db = ZoneMaster.select(ZoneMaster.company_id).dicts() \
                .where(ZoneMaster.id == zone_id).get()
            if len(company_id_in_db.keys()) > 0 and company_id_in_db['company_id'] == int(company_id):
                return True
            else:
                return False

        except (IntegrityError, InternalError, DataError) as e:
            raise e
        except DoesNotExist as e:
            return False

    @classmethod
    def get_zone_id_list_for_a_company(cls, company_id):
        """
        To get the list of all the zone ids for a company.
        @param company_id:
        :return:
        """
        db_result = list()
        try:
            query = ZoneMaster.select(ZoneMaster.id).dicts().where(
                ZoneMaster.company_id == company_id)

            for device in query:
                db_result.append(device['id'])
            return db_result

        except (IntegrityError, InternalError, DataError) as e:
            raise e


    @classmethod
    def get_zone_data_by_zone_id(cls, zone_id, company_id):
        """
        To get the zone details by zone_id and company_id.
        :param zone_id:
        :param company_id:
        :return:
        """
        try:
            zone_data = ZoneMaster.select().dicts().where(ZoneMaster.id == zone_id,
                                                          ZoneMaster.company_id == company_id).get()

            return zone_data

        except (IntegrityError, InternalError, DataError) as e:
            raise e
