from peewee import *
from playhouse.shortcuts import cast
from typing import List, Dict

import settings
from dosepack.base_model.base_model import BaseModel
from src.exceptions import NoLocationExists
from src.model.model_container_master import ContainerMaster
from src.model.model_device_master import DeviceMaster

logger = settings.logger


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster, related_name="lm_device_id_id")
    location_number = IntegerField()
    container_id = ForeignKeyField(ContainerMaster, related_name='location_container_id')
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)
    is_disabled = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

    @classmethod
    def get_formatted_location(cls):
        """
        formatted location is the location used for the communication with csr hardware
        :return:
        """
        logger.debug("In get_formatted_location")

        return cast(fn.Substr(cls.display_location, fn.instr(cls.display_location, '-') + 1) - 1, 'SIGNED')

    @classmethod
    def get_device_location(cls):
        """
        csr location to be displayed on front end
        :return:
        """
        logger.debug("In get_device_location")
        return cast(fn.Substr(cls.display_location, fn.instr(cls.display_location, '-') + 1), 'SIGNED')

    @classmethod
    def get_location_id(cls, device_id, location_number):
        """
        formatted location is the location used for the communication with csr hardware
        :return:
        """
        logger.debug("In get_location_id")
        try:
            query = cls.select(cls.id).where(cls.device_id == device_id, cls.location_number == location_number).get()
            return query.id
        except DoesNotExist as e:
            raise NoLocationExists

    @classmethod
    def get_location_id_by_display_location(cls, device_id, display_location):
        logger.debug("In get_location_id_by_display_location")
        """
        formatted location is the location used for the communication with csr hardware
        :return:
        """
        logger.debug("In get_location_id_by_display_location")
        try:
            query = cls.select(cls.id).where(cls.device_id == device_id, cls.display_location == display_location).get()
            return query.id
        except DoesNotExist as e:
            logger.error("Data Not Found for given given arguments")
            return None

    @classmethod
    def get_location_number_from_display_location(cls, device_id, display_location):
        """
                formatted location is the location used for the communication with csr hardware
                :return:
                """
        try:
            query = cls.select(cls.location_number).where(cls.device_id == device_id, cls.display_location == display_location).get()
            return query.location_number
        except DoesNotExist as e:
            raise NoLocationExists

    @classmethod
    def get_location_ids_from_device_id(cls, device_id):
        logger.debug("In get_location_ids_from_device_id")
        try:
            total_locations = []
            query = cls.select(cls.id).where(cls.device_id == device_id)
            for record in query:
                total_locations.append(record.id)
            return total_locations
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
        except DoesNotExist as e:
            raise NoLocationExists

    @classmethod
    def get_quadrant_from_device_location(cls, device_id, location):
        logger.debug("In get_quadrant_from_device_location")
        try:
            query = LocationMaster.select(LocationMaster.quadrant) \
                .where(LocationMaster.device_id == device_id, LocationMaster.display_location == location).get()
            return query.quadrant
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
        except DoesNotExist as e:
            raise NoLocationExists

    @classmethod
    def get_display_locations_from_device_ids(cls, devide_ids):
        logger.debug("In get_display_locations_from_device_ids")
        locations = {}
        try:
            for device in devide_ids:
                locations[device] = set()
                query = cls.select(cls.display_location, cls.location_number).where(cls.device_id == device)
                for record in query.dicts():
                    locations[device].add((record["display_location"], record["location_number"]))
            return locations
        except DoesNotExist as e:
            raise NoLocationExists

    @classmethod
    def get_display_locations_from_device_idsV3(cls, devide_ids):
        logger.debug("In get_display_locations_from_device_idsV3")
        locations = {}
        try:
            for device in devide_ids:
                locations[device] = {}
                query = cls.select(cls.display_location, cls.location_number, cls.quadrant).where(
                    cls.device_id == device)
                for record in query.dicts():
                    if record['quadrant'] not in locations[device]:
                        locations[device][record['quadrant']] = set()
                    locations[device][record['quadrant']].add(record["location_number"])
            return locations
        except DoesNotExist as e:
            raise NoLocationExists

    @classmethod
    def get_location_ids(cls, device_id, location_number_list):
        """
        formatted location is the location used for the communication with csr hardware
        :return:
        """
        logger.debug("In get_location_ids")
        try:
            query = cls.select(cls.id).dicts().where(cls.device_id == device_id,
                                                     cls.location_number << location_number_list)
            location_id_list = [item['id'] for item in query]
            return location_id_list
        except DoesNotExist as e:
            raise NoLocationExists

    @classmethod
    def add_multiple_locations_data(cls, locations_data):
        logger.debug("In add_multiple_locations_data")
        try:
            query = LocationMaster.insert_many(locations_data).execute()
            return True
        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError
        except DataError as e:
            raise DataError

    @classmethod
    def enable_location(cls, device_id, display_location):
        logger.debug("In enable_location")
        try:
            query = cls.update(is_disabled=False).where(cls.device_id == device_id,
                                                        cls.display_location == display_location).execute()
            return query
        except (IntegrityError, InternalError) as e:
            logger.error(e)
            raise

    @classmethod
    def disable_location(cls, location_id_list):
        logger.debug("In disable_location")
        try:
            query = cls.update(is_disabled=True).where(cls.id << location_id_list).execute()
            return query
        except (IntegrityError, InternalError) as e:
            logger.error(e)
            raise

    @classmethod
    def db_get_disabled_locations_of_devices(cls, device_ids):
        logger.debug("In db_get_disabled_locations_of_devices")
        try:
            disabled_locations = cls.select().dicts().where(cls.is_disabled == True, cls.device_id << device_ids)
            return list(disabled_locations)
        except IntegrityError as e:
            logger.error(e)
            raise IntegrityError
        except InternalError as e:
            logger.error(e)
            raise InternalError
        except DataError as e:
            logger.error(e)
            raise DataError
        except DoesNotExist as e:
            logger.error(e)
            return list()

    @classmethod
    def disabled_locations(cls, location_id_list: List[int]) -> Dict[int, str]:
        """
        Returns True if location is disabled for given location_id, False otherwise

        :param location_id_list:
        :return: bool
        """
        logger.debug("In disabled_locations")
        disabled_locations: Dict[int, str] = dict()
        try:
            query = cls.select(cls.id, cls.display_location).dicts().where(cls.id << location_id_list, cls.is_disabled == True)

            for record in query:
                disabled_locations[record["id"]] = record["display_location"]

            return disabled_locations

        except (InternalError, IntegrityError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_location_id_by_display_location_list(cls, device_id: int, display_location_list: list) -> list:
        """
        this is used to get the location ids from the display_locations
        :return:
        """
        logger.debug("In get_location_id_by_display_location_list")
        location_ids: list = []
        try:
            query = cls.select(cls.id).dicts().where(
                cls.device_id == device_id, cls.display_location << display_location_list)

            for record in query:
                location_ids.append(record["id"])

            return location_ids

        except DoesNotExist as e:
            raise NoLocationExists

    @classmethod
    def get_locations_by_container_id(cls, device_id: int, container_id: list) -> list:
        """
        This method fetches all the locations for the given container of a device.
        @param device_id:
        @param container_id:
        @return:
        """
        logger.debug("Inside get_locations_by_container_id")
        location_data: list = []
        try:
            query = cls.select().dicts().where(cls.device_id == device_id, cls.container_id << container_id)

            for record in query:
                location_data.append(record)

            return location_data

        except DoesNotExist as e:
            raise NoLocationExists

    @classmethod
    def db_get_empty_locationsV3(cls, device_ids, packdistribution=False):
        """
        Returns empty locations for given robot ids

        :param device_ids: (dict) keys as robot id and value as max canisters for that robot id
        :return: dict
        @param packdistribution:
        """
        try:
            if packdistribution:
                empty_locations = {x: set([i for i in range(1, device_ids[x] + 1)]) for x in device_ids}
            else:
                empty_locations = LocationMaster.get_display_locations_from_device_idsV3(device_ids)
            # filling with all locations first
            locations = {x: {} for x in device_ids}
            device_id_list = list(device_ids.keys())
            disabled_locations = {x: {} for x in device_ids}
            if device_ids:
                for record in LocationMaster.select(LocationMaster.device_id, LocationMaster.display_location,
                                                    LocationMaster.location_number, LocationMaster.quadrant) \
                        .dicts() \
                        .where(LocationMaster.is_disabled == True, LocationMaster.device_id << device_id_list):
                    if packdistribution:
                        if record['quadrant'] not in disabled_locations[record['device_id']]:
                            disabled_locations[record['device_id']][record['quadrant']] = set()
                        disabled_locations[record['device_id']][record['quadrant']].add(record['location_number'])
                    else:
                        if record['quadrant'] not in disabled_locations[record['device_id']]:
                            disabled_locations[record['device_id']][record['quadrant']] = set()
                        disabled_locations[record['device_id']][record['quadrant']].add(record['location_number'])
                for k, v in disabled_locations.items():
                    if len(v) > 0:
                        for quadrant, locations in v.items():
                            empty_locations[k][quadrant] -= disabled_locations[k][quadrant]
                # for k, v in locations.items():
                #     for quadrant, location in v.items():
                #         empty_locations[k][quadrant] -= locations[k][quadrant]
                logger.info("db_get_empty_locationsV3 > empty_locations: " + str(empty_locations))
                return empty_locations
            else:
                return empty_locations

        except (InternalError, IntegrityError, ValueError) as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(e)
            raise

    @classmethod
    def db_get_quadrant_and_device_from_location_number(cls, location_number):
        try:
            query = cls.select(cls.quadrant, cls.device_id).dicts().where(cls.location_number == location_number).get()
            return query['quadrant'], query['device_id']
        except DoesNotExist as e:
            print("data not exist for location_number {}".format(location_number))
            return None, None
        except (InternalError, IntegrityError, ValueError) as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise e

