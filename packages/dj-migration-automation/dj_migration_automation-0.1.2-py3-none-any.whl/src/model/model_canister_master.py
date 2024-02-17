import functools
import operator

from peewee import ForeignKeyField, PrimaryKeyField, CharField, \
    DateTimeField, IntegerField, BooleanField, SmallIntegerField, FixedCharField, \
    DoesNotExist, InternalError, IntegrityError, DataError, fn, DateField, JOIN_LEFT_OUTER

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_canister_status_history import CanisterStatusHistory
from src.model.model_canister_status_history_comment import CanisterStatusHistoryComment
from src import constants
from src.model.model_drug_master import DrugMaster
from src.exceptions import CanisterNotExist, CanisterNotPresent
from src.model.model_canister_stick import CanisterStick
from src.model.model_code_master import CodeMaster
from src.model.model_location_master import LocationMaster
from src.model.model_small_canister_stick import SmallCanisterStick

# get the logger for the canister

logger = settings.logger


class CanisterMaster(BaseModel):
    """
        @class: canister_master.py
        @type: file
        @desc: logical class for table canister_master
    """
    id = PrimaryKeyField()
    company_id = IntegerField()
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=32)
    available_quantity = SmallIntegerField()
    # canister_number = SmallIntegerField(default=0, null=True)F
    active = BooleanField()
    reorder_quantity = SmallIntegerField()
    barcode = CharField(max_length=15)
    canister_code = CharField(max_length=25, unique=True, null=True)
    label_print_time = DateTimeField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    location_id = ForeignKeyField(LocationMaster, null=True, unique=True)
    product_id = IntegerField(null=True)
    canister_type = ForeignKeyField(CodeMaster, default=71, related_name='canister_type')  # 70-big, 71-small
    canister_stick_id = ForeignKeyField(CanisterStick, related_name="canister_stick_id", null=True)
    # canister_usage = ForeignKeyField(CodeMaster, default=settings.CANISTER_DRUG_USAGE["Medium Fast Moving"])
    requested_id = IntegerField(null=True)
    expiry_date = DateField(null=True, default=None)
    threshold = IntegerField(default=75)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"

    @classmethod
    def db_get_canister_info(cls, canister_id):
        """
        Deletes canisters data from table
        :return:
        """
        try:
            query = cls.select().dicts().where(cls.id == canister_id).get()
            return query
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_verify_canister_id(cls, canister_id: int, company_id: int) -> bool:
        try:
            canister = CanisterMaster.get(id=canister_id)
            if company_id == canister.company_id:
                return True
            return False
        except (InternalError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            return False

    @classmethod
    def db_verify_active_canister_id(cls, canister_id: int) -> bool:
        try:
            canister = CanisterMaster.get(id=canister_id)
            if canister.active:
                return True
            return False
        except (InternalError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            return False

    @classmethod
    def delete_canister(cls, canister_id, user_id, update_location):
        try:
            if update_location:
                canister_update = CanisterMaster.update(active=0, modified_by=user_id, location_id=None).where(
                    CanisterMaster.id == canister_id).execute()
            else:
                canister_update = CanisterMaster.update(active=0, modified_by=user_id).where(
                    CanisterMaster.id == canister_id).execute()

            return canister_update
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError
        except IntegrityError as e:
            logger.error(e, exc_info=True)
            raise IntegrityError

    @classmethod
    def activate_canister(cls, user_id, location_id, rfid, update_location):
        try:
            if update_location:
                canister_update = CanisterMaster.update(location_id=location_id, active=1, modified_by=user_id).where(
                    CanisterMaster.rfid == rfid).execute()
            else:
                canister_update = CanisterMaster.update(active=1, modified_by=user_id).where(
                    CanisterMaster.rfid == rfid).execute()
            return canister_update
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError
        except IntegrityError as e:
            logger.error(e, exc_info=True)
            raise IntegrityError

    @classmethod
    def update_canister(cls, dict_canister_info, _id):
        try:
            status = CanisterMaster.update(**dict_canister_info).where(CanisterMaster.id == _id)
            status = status.execute()
            return status
        except (IntegrityError, InternalError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_canister_by_rfid(cls, dict_canister_info, rfid):
        try:
            status = CanisterMaster.update(**dict_canister_info).where(CanisterMaster.rfid == rfid)
            status = status.execute()
            return status
        except (IntegrityError, InternalError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_canister_status_by_location(cls, status, location_id):
        try:
            status = CanisterMaster.update(active=status).\
                where(CanisterMaster.location_id == location_id)
            status = status.execute()
            return status
        except (IntegrityError, InternalError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_available_quantity(cls, canister_id):
        try:
            # get the current quantity from the canister based on canister id
            quantity = CanisterMaster.get(id=canister_id).available_quantity
            return quantity
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            raise DoesNotExist(ex)
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError(e)

    @classmethod
    def get_canister_ids(cls, rfid_list):
        try:
            canister_id_list = []
            for record in CanisterMaster.select(CanisterMaster.id, CanisterMaster.rfid).where(
                    CanisterMaster.rfid << rfid_list):
                canister_id_list.append(record["id"])
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            raise DoesNotExist(ex)
        except InternalError as e:
            raise InternalError(e)
        return canister_id_list

    @classmethod
    def get_canister_id_by_rfid(cls, rfid):
        try:
            for record in CanisterMaster.select(CanisterMaster.id) \
                    .dicts() \
                    .where(CanisterMaster.rfid == rfid):
                return record['id']

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

        except DoesNotExist as e:
            logger.error(e)
            return None, None

    @classmethod
    def db_get_drug_ids(cls, company_id):
        """
        Returns drug ids present in canisters of given company id
        :param company_id: Company ID
        :return: set
        """
        drug_ids_set = set()
        try:
            # get the current quantity from the canister based on canister id
            for record in CanisterMaster.select(CanisterMaster.drug_id).dicts() \
                    .where(CanisterMaster.company_id == company_id):
                drug_ids_set.add(record["drug_id"])
            return drug_ids_set
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            raise DoesNotExist(ex)
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e
        except Exception as e:
            logger.info(e, exc_info=True)
            raise e

    @classmethod
    def db_get_canister_data_by_rfid(cls, rfid: str) -> dict:
        """
        Returns canister data(dict) by RFID, raise exception if no canister found
        :param rfid: RFID of canister
        :return: dict
        """
        try:
            return CanisterMaster.select().dicts().where(CanisterMaster.rfid == rfid).get()
        except(IntegrityError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
        except DoesNotExist as e:
            logger.debug('No Canister found for RFID {}, exc: {}'.format(rfid, e))
            raise CanisterNotExist

    @classmethod
    def db_get_canister_data_by_location_id(cls, location_id: int) -> dict:
        """
        Returns canister data(dict) by location_id, raise exception if no canister found
        :param location_id: location_id
        :return: dict
        """
        try:
            return CanisterMaster.select().dicts().where(CanisterMaster.location_id == location_id).get()
        except(IntegrityError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
        except DoesNotExist as e:
            logger.debug('No Canister found at location {}, exc: {}'.format(location_id, e))
            raise CanisterNotPresent

    @classmethod
    def db_get_last_canister_id(cls):
        try:
            return cls.select(CanisterMaster.id).order_by(CanisterMaster.id.desc()).get().id
        except(IntegrityError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_create_canister_record(cls, dict_canister_info, company_id, canister_code, user_id, location_id):
        try:
            record_data = {
                "company_id": company_id,
                "drug_id": dict_canister_info["drug_id"],
                "rfid": dict_canister_info["rfid"],
                "available_quantity": dict_canister_info.get("available_quantity", 0),
                "reorder_quantity": dict_canister_info.get("reorder_quantity", 0),
                "canister_type": dict_canister_info.get("canister_type", settings.SIZE_OR_TYPE['SMALL']),
                "barcode": dict_canister_info["barcode"],
                "canister_code": canister_code,
                "created_by": user_id,
                "modified_by": user_id,
                "location_id": location_id,
                "product_id": dict_canister_info.get('product_id', None),
                "canister_stick_id": dict_canister_info.get('canister_stick_id', None),
            }

            if dict_canister_info.get("reason_type") == constants.CANISTER_FAIL_DUE_TO_NON_COMPATIBLE_DRUG:
                record_data["active"] = False
            else:
                record_data["active"] = True
            if dict_canister_info.get("available_quantity", None):
                record_data["available_quantity"] = dict_canister_info.get("available_quantity",
                                                                           0) + dict_canister_info.get("quantity", 0)
            else:
                record_data["available_quantity"] = dict_canister_info.get("quantity", 0)
            if dict_canister_info.get("expiry_date", None):
                record_data["expiry_date"] = dict_canister_info.get("expiry_date", None)
            record = BaseModel.db_create_record(record_data, CanisterMaster, get_or_create=False)
            return record.id
        except(IntegrityError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_canister_count_by_drug_and_company_id(cls, company_id, drug_id_list):
        """

        :param company_id:
        :param drug_id_list:
        :return:
        """
        # TODO: Replace with company id when merged

        response_dict = dict()
        query = CanisterMaster.select(CanisterMaster.drug_id,
                                      fn.COUNT(CanisterMaster.id).alias("canister_count")).where(
            (CanisterMaster.drug_id.in_(drug_id_list)) & (CanisterMaster.company_id == company_id) &
            (CanisterMaster.active == settings.is_canister_active))

        for record in query.dicts():
            response_dict[record["drug_id"]] = record["canister_count"]

        return response_dict

    @classmethod
    def get_canister_data_by_drug_and_company_id(cls, drug_id_list, company_id):
        """

        :param drug_id_list:
        :param company_id:
        :return:
        """
        db_response = list()
        for record in CanisterMaster.select().dicts().where((CanisterMaster.company_id == company_id) &
                                                            (CanisterMaster.drug_id.in_(drug_id_list)) &
                                                            (CanisterMaster.active == settings.is_canister_active)):
            db_response.append(record)

        return db_response

    @classmethod
    def update_canister_location_id(cls, canister_id, location_id):
        try:
            status = CanisterMaster.update(location_id=location_id).where(CanisterMaster.id == canister_id) \
                .execute()
            return status

        except IntegrityError as e:
            raise e
        except InternalError as e:
            raise e
        except DataError as e:
            raise e

    @classmethod
    def update_canister_location(cls, canister_id, location_id, company_id):
        try:
            status = CanisterMaster.update(location_id=location_id).where(CanisterMaster.id == canister_id,
                                                                         CanisterMaster.company_id == company_id) \
                .execute()
            return status

        except IntegrityError as e:
            raise e
        except InternalError as e:
            raise e
        except DataError as e:
            raise e

    @classmethod
    def update_canister_location_based_on_rfid(cls, location_id: int, rfid: str) -> bool:

        try:
            new_location_update_query = CanisterMaster.update(location_id=location_id) \
                .where(CanisterMaster.rfid == rfid).execute()
            return new_location_update_query
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_canister_stick_of_canister(cls, canister_id: int, canister_stick_id: int) -> bool:

        try:
            status = CanisterMaster.update(canister_stick_id=canister_stick_id).where(
                CanisterMaster.id == canister_id).execute()

            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_canister_location_shelf(cls, user_id, location_id_list):
        try:
            status = CanisterMaster.update(
                location_id=None,
                modified_date=get_current_date_time(),
                modified_by=user_id
            ).where(CanisterMaster.location_id << location_id_list).execute()
            return status
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_canister_data_by_rfid_company(cls, rfid, company_id):
        try:
            return CanisterMaster.select(CanisterMaster.id,
                                         CanisterMaster.rfid,
                                         CanisterMaster.drug_id,
                                         CanisterMaster.location_id,
                                         CanisterMaster.company_id,
                                         CanisterMaster.canister_type,
                                         CanisterMaster.product_id,
                                         CanisterMaster.barcode,
                                         CanisterMaster.canister_stick_id).dicts()\
                .where(CanisterMaster.rfid == rfid, CanisterMaster.company_id == company_id).get()
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_create_canister_master(cls, insert_canister_data):
        try:
            return CanisterMaster.insert(**insert_canister_data).execute()
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_get_on_shelf_canister_ids(cls):
        """

        :param drug_id_list:
        :param company_id:
        :return:
        """
        db_response = list()
        for record in CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
                                            CanisterMaster.location_id.alias("location_id")).dicts().where(
                                                            (CanisterMaster.location_id.is_null(True))):
            db_response.append(record)

        return db_response

    @classmethod
    def db_get_deactive_canisters_comment(cls, canister_id):
        canister_list = []

        try:
            for id in canister_id:
                query = CanisterMaster.select(
                    CanisterMaster.id,
                    CanisterStatusHistoryComment.comment
                ).dicts() \
                    .join(CanisterStatusHistory, on=CanisterStatusHistory.canister_id == CanisterMaster.id) \
                    .join(CanisterStatusHistoryComment,
                          on=CanisterStatusHistoryComment.canister_status_history_id == CanisterStatusHistory.id) \
                    .where(CanisterMaster.id == id)

                for record in query:
                    canister_list.append(record)

            return canister_list
        except Exception as e:
            logger.info(e)
            return e

        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError

    @classmethod
    def db_get_deactive_canisters_new(cls, width, depth, length, all_flag=False):
        # todo decide based on deleted canister
        canister_list = []
        clauses = list()
        clauses.append((CanisterMaster.active == 0))
        clauses.append(CanisterMaster.rfid.is_null(False))
        clauses.append(BigCanisterStick.width == float(width))
        clauses.append(BigCanisterStick.depth == float(depth))
        clauses.append(SmallCanisterStick.length == float(length))

        try:
            query = BigCanisterStick.select(
                CanisterMaster.id.alias('canister_id'),
                BigCanisterStick.width.alias('Recommended_Big_Stick_Width'),
                BigCanisterStick.depth.alias('Recommended_Big_Stick_Depth'),
                BigCanisterStick.serial_number.alias('Recommended_Big_Stick_Serial_Number'),
                SmallCanisterStick.length.alias('Recommended_Small_Stick_Serial_Number_Length'),
            ).dicts() \
                .join(CanisterStick, JOIN_LEFT_OUTER, on=CanisterStick.big_canister_stick_id == BigCanisterStick.id) \
                .join(SmallCanisterStick, JOIN_LEFT_OUTER,
                      on=CanisterStick.small_canister_stick_id == SmallCanisterStick.id) \
                .join(CanisterMaster, JOIN_LEFT_OUTER, on=CanisterMaster.canister_stick_id == CanisterStick.id) \
                .where(functools.reduce(operator.and_, clauses))
            for record in query:
                canister_list.append(record)
            return canister_list
        except Exception as e:
            logger.info(e)
            return e

        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError