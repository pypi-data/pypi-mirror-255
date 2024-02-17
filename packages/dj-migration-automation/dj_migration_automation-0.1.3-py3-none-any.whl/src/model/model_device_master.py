from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.error_handling.error_handler import create_response, error
from src.model.model_device_type_master import DeviceTypeMaster

logger = settings.logger


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField(max_length=50)
    serial_number = CharField(max_length=20, unique=True)
    device_type_id = ForeignKeyField(DeviceTypeMaster)
    system_id = IntegerField(null=True)
    version = CharField(null=True)
    active = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()
    associated_device = ForeignKeyField('self', null=True)
    ip_address = CharField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )

    @classmethod
    def db_get_device_master_data(cls, device_id: int):
        """ get device master data by device id"""
        try:
            return DeviceMaster.select().dicts().where(DeviceMaster.id == device_id).get()
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def add_device_data(cls, device_data):
        logger.debug("In add_device_data")
        try:
            query = BaseModel.db_create_record(device_data, DeviceMaster, get_or_create=False)
            return query.id

        except IntegrityError as e:
            raise
        except InternalError as e:
            raise InternalError
        except DataError as e:
            raise DataError

    @classmethod
    def get_device_data_from_serial_number(cls, serial_number):
        logger.debug("In get_device_data_from_serial_number")
        try:
            query = DeviceMaster.select(DeviceMaster.id, DeviceMaster.company_id).dicts() \
                .where(DeviceMaster.serial_number == serial_number).get()

            return query
        except DoesNotExist as e:
            raise DoesNotExist

    @classmethod
    def get_device_type_from_device(cls, device_id_list):
        device_type_dict = dict()
        try:
            query = DeviceMaster.select(DeviceMaster.id, DeviceMaster.device_type_id).dicts()\
                    .where(DeviceMaster.id << device_id_list)

            for record in query:
                device_type_dict[record['id']] = record['device_type_id']

            return device_type_dict

        except (InternalError, IntegrityError) as e:
            logger.error(e)
            return e

        except DoesNotExist as e:
            logger.error(e)
            return device_type_dict

    @classmethod
    def db_get_device_name_from_device(cls, device_id_list):
        device_id_name_dict = dict()
        try:
            query = DeviceMaster.select(DeviceMaster.id, DeviceMaster.name) \
                .where(DeviceMaster.id << device_id_list)
            for record in query.dicts():
                device_id_name_dict[record['id']] = record['name']

            return device_id_name_dict

        except (InternalError, IntegrityError) as e:
            logger.error(e)
            return e

        except DoesNotExist as e:
            logger.error(e)
            return device_id_name_dict

    @classmethod
    def get_all_devices_of_a_type(cls, device_type_ids: list, company_id: int) -> list:
        logger.debug("In get_all_devices_of_a_type")
        try:
            db_result = list()
            query = DeviceMaster.select(DeviceMaster.id,
                                        DeviceMaster.name,
                                        DeviceMaster.serial_number).dicts() \
                .where(DeviceMaster.company_id == company_id,
                       DeviceMaster.device_type_id << device_type_ids)
            for device in query:
                db_result.append(device)
            return db_result

        except InternalError as e:
            raise InternalError
        except IntegrityError as e:
            raise IntegrityError

    @classmethod
    def get_company_id_of_a_device(cls, device_id):
        logger.debug("In get_company_id_of_a_device")
        try:
            query = DeviceMaster.select(DeviceMaster.company_id).dicts().where(DeviceMaster.id == device_id).get()

            return query

        except DoesNotExist as e:
            raise DoesNotExist
        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError

    @classmethod
    def get_drawers_quantity(cls, device_id):
        try:
            query = DeviceMaster.select(DeviceMaster.max_canisters,
                                        DeviceMaster.big_drawers,
                                        DeviceMaster.small_drawers).dicts()\
                .where(DeviceMaster.id == device_id).get()

            return query

        except DoesNotExist as e:
            raise DoesNotExist
        except InternalError as e:
            raise InternalError
        except IntegrityError as e:
            raise IntegrityError

    @classmethod
    def db_verify_device_id(cls, device_id, system_id):
        logger.debug("In db_verify_device_id")
        system_id = int(system_id)
        try:
            device = DeviceMaster.get(id=device_id)
            if system_id == device.system_id:
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError:
            return False

    @classmethod
    def db_verify_device_id_by_company(cls, device_id: int, company_id: int) -> bool:
        logger.debug("In db_verify_device_id_by_company")
        company_id = int(company_id)
        try:
            device = DeviceMaster.get(id=device_id)
            if company_id == device.company_id:
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError:
            return False

    @classmethod
    def db_get_by_id(cls, device_id: int):
        logger.debug("In db_get_by_id")
        try:
            device_data = cls.get(id=device_id)
            return device_data
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            raise DoesNotExist
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError

    @classmethod
    def db_get_robots_by_systems(cls, system_id_list):
        """
        Returns robots data for given system id list
        :param system_id_list: list
        :return: list
        """
        logger.debug("In db_get_robots_by_systems")
        robots_data = dict()
        try:
            if system_id_list:
                for record in cls.select().dicts() \
                        .where(cls.system_id << system_id_list,
                               cls.device_type_id == settings.DEVICE_TYPES["ROBOT"],
                               cls.active == settings.is_device_active):
                    robots_data.setdefault(record["system_id"], list()).append(record)
            return robots_data
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_robots_by_system_id(cls, system_id, version=None):
        logger.debug("In db_get_robots_by_system_id")
        robots = []
        if not version:
            version = [settings.ROBOT_SYSTEM_VERSIONS['v2'], settings.ROBOT_SYSTEM_VERSIONS['v3']]
        try:
            for record in DeviceMaster.select() \
                    .where(DeviceMaster.system_id == system_id,
                           cls.device_type_id == settings.DEVICE_TYPES["ROBOT"],
                           cls.version << version,
                           cls.active == settings.is_device_active) \
                    .dicts():
                robots.append(record)
            return robots
        except InternalError as ex:
            logger.error(ex, exc_info=True)
            raise InternalError

    @classmethod
    def db_get_csr_by_company_id(cls, company_id):
        logger.debug("In db_get_csr_by_company_id")
        csrs = []

        try:
            for record in DeviceMaster.select() \
                    .where(DeviceMaster.company_id == company_id,
                           DeviceMaster.active == settings.is_device_active,
                           cls.device_type_id == settings.DEVICE_TYPES["CSR"]) \
                    .dicts():
                csrs.append(record)
            return csrs
        except InternalError as ex:
            logger.error(ex, exc_info=True)
            raise InternalError

    @classmethod
    def get_associated_trolley_by_device_id(cls, device_id, device_type):
        logger.debug("In get_associated_trolley_by_device_id")
        device_data = []
        try:
            for record in DeviceMaster.select().dicts() \
                    .where(DeviceMaster.associated_device == device_id,
                           DeviceMaster.device_type_id << device_type):
                device_data.append(record)
            return device_data

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get(cls, system_id, device_id=None, serial_number=None, device_type=[settings.DEVICE_TYPES['ROBOT']]):
        logger.debug("In db_get")
        device_data = []
        try:
            if serial_number:
                for record in DeviceMaster.select().dicts() \
                        .where(DeviceMaster.system_id == system_id,
                               DeviceMaster.serial_number == serial_number,
                               DeviceMaster.device_type_id << device_type):
                    device_data.append(record)
                return device_data

            if device_id is None:
                for record in DeviceMaster.select().dicts() \
                        .where(DeviceMaster.system_id == system_id,
                               DeviceMaster.device_type_id << device_type):
                    device_data.append(record)
                return device_data
            else:
                for record in DeviceMaster.select().dicts() \
                        .where(DeviceMaster.system_id == system_id,
                               DeviceMaster.id == device_id,
                               DeviceMaster.device_type_id << device_type):
                    device_data.append(record)
                return device_data

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_by_company_id(cls, company_id, device_type=[settings.DEVICE_TYPES['ROBOT']]):
        logger.debug("In db_get_by_company_id")
        device_data = []
        try:
            for record in DeviceMaster.select().dicts() \
                    .where(DeviceMaster.company_id == company_id,
                           DeviceMaster.device_type_id << device_type):
                device_data.append(record)
            return device_data

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_robot_details(cls, device_id, system_id):
        logger.debug("In db_get_robot_details")
        # device_details = []
        robot_details = []

        try:
            if device_id != 0:
                for record in DeviceMaster.select(
                        DeviceMaster.name.alias('device_name')
                ).dicts().where(DeviceMaster.id == device_id,
                                DeviceMaster.system_id == system_id):
                    robot_details.append(record)

            else:
                for record in DeviceMaster.select(
                        DeviceMaster.id.alias('device_id'),
                        DeviceMaster.name.alias('device_name')
                ).dicts().where(DeviceMaster.system_id == system_id):
                    robot_details.append(record)

            return create_response({"robot_details": robot_details})
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            return error(2001)
        except InternalError as ex:
            logger.error(ex, exc_info=True)
            return error(2002)

    @classmethod
    def db_verify_devicelist(cls, devicelist, company_id):
        """
        Returns True if all devices belongs to the same company_id
        :param devicelist:
        :param company_id:
        :return:
        """
        logger.debug("In db_verify_devicelist")
        company_id = int(company_id)
        try:
            device_count = DeviceMaster.select().where(
                DeviceMaster.id << devicelist,
                DeviceMaster.company_id == company_id
            ).count()
            if device_count == len(set(devicelist)):
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError:
            return False

    @classmethod
    def db_get_active_robots_count_by_system_id(cls, system_id):
        logger.debug("In db_get_active_robots_count_by_system_id")
        try:
            active_robot_count = DeviceMaster.select(fn.COUNT(cls.id).alias("robot_count")) \
                .where(cls.system_id == system_id, cls.active == True,
                       cls.device_type_id == settings.DEVICE_TYPES["ROBOT"]) \
                .get().robot_count
            return active_robot_count
        except (InternalError, IntegrityError) as ex:
            logger.error(ex, exc_info=True)
            raise

    @classmethod
    def db_get_system_id_by_device_id(cls, device_id):
        logger.debug("In db_get_system_id_by_device_id")
        try:
            system_id = DeviceMaster.select(cls.system_id).where(cls.id == device_id).get().system_id
            return system_id
        except (InternalError, IntegrityError) as ex:
            logger.error(ex, exc_info=True)
            raise

    @classmethod
    def delink_trolley_from_device(cls, system_id):
        logger.debug("In delink_trolley_from_device")
        try:
            dict_robot_info = {'system_id': None, 'associated_device': None}
            return DeviceMaster.update(**dict_robot_info).where(DeviceMaster.system_id == system_id,
                                                                DeviceMaster.device_type_id <<
                                                                (settings.DEVICE_TYPES['CANISTER_ROBOT_TROLLEY'],
                                                                 settings.DEVICE_TYPES['CANISTER_CSR_TROLLEY'])
                                                                ).execute()

        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_device_data(cls, dict_robot_info, device_id):
        logger.debug("In update_device_data")
        try:
            return DeviceMaster.update(**dict_robot_info).where(DeviceMaster.id == device_id).execute()

        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_device_data(cls, device_id, type_validation=None, version=None):
        logger.debug("In get_device_data")
        if not version:
            version = [settings.ROBOT_SYSTEM_VERSIONS['v3']]
        try:
            query = DeviceMaster.select().dicts().where(cls.id == device_id,
                                                cls.active == 1,
                                                cls.version << version)
            if type_validation:
                query = query.where(cls.device_type_id == type_validation)
            for record in query:
                return record
        except DoesNotExist as e:
            logger.info(e, exc_info=True)
            return 0
        except (InternalError, IntegrityError) as ex:
            logger.error(ex, exc_info=True)
            raise

    @classmethod
    def get_mfs_id_by_system_id(cls, system_id, type_validation=None, version=None):
        manual_fill_stations = list()
        try:
            query = DeviceMaster.select().dicts() \
                .where(cls.system_id == system_id,
                       cls.active == settings.is_device_active,
                       cls.device_type_id == settings.DEVICE_TYPES['Manual Filling Device'])
            for record in query:
                manual_fill_stations.append(record['id'])
            return manual_fill_stations
        except DoesNotExist as e:
            logger.info(e, exc_info=True)
            return 0
        except (InternalError, IntegrityError) as ex:
            logger.error(ex, exc_info=True)
            raise

    @classmethod
    def get_mfs_system_by_device(cls, device_ids, type_validation=None, version=None):
        manual_fill_stations = dict()
        device_associated_device_dict = dict()
        try:
            query = DeviceMaster.select().dicts() \
                .where(cls.id << device_ids,
                       cls.active == settings.is_device_active,
                       cls.device_type_id == settings.DEVICE_TYPES['Manual Filling Device'])
            for record in query:
                if record['system_id'] not in manual_fill_stations:
                    manual_fill_stations[record['system_id']] = list()
                manual_fill_stations[record['system_id']].append(record['id'])
                device_associated_device_dict[record['id']] = record['associated_device']
            return manual_fill_stations, device_associated_device_dict
        except DoesNotExist as e:
            logger.info(e, exc_info=True)
            return 0
        except (InternalError, IntegrityError) as ex:
            logger.error(ex, exc_info=True)
            raise

    @classmethod
    def db_verify_device_id_list(cls, device_id, system_id):
        logger.debug("In db_verify_device_id")
        try:
            device_count = DeviceMaster.select().where(
                DeviceMaster.id << device_id,
                DeviceMaster.system_id == system_id
            ).count()
            if device_count == len(set(device_id)):
                return True
            return False
        except (IntegrityError, InternalError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            return False
        except Exception as e:
            logger.error(e, exc_info=True)
            return False