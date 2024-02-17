import functools
import operator
import os
import sys
from datetime import date
from typing import List, Dict, Optional, Any

from peewee import PrimaryKeyField, IntegerField, ForeignKeyField, SmallIntegerField, BooleanField, FixedCharField, \
    DateField, DateTimeField, fn, DoesNotExist, IntegrityError, InternalError, DataError, ProgrammingError, CharField

from src import constants
import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_header import PackHeader
from src.model.model_batch_master import BatchMaster
from src.model.model_code_master import CodeMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_facility_distribution_master import FacilityDistributionMaster

logger = settings.logger


class PackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)  # system_id from dpauth project System table
    pack_header_id = ForeignKeyField(PackHeader)
    batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    is_takeaway = BooleanField(default=False)
    pack_status = ForeignKeyField(CodeMaster, related_name="pack_details_pack_status")
    filled_by = FixedCharField(max_length=64)
    consumption_start_date = DateField()
    consumption_end_date = DateField()
    filled_days = SmallIntegerField()
    fill_start_date = DateField()
    delivery_schedule = FixedCharField(max_length=50)
    association_status = BooleanField(null=True)
    rfid = FixedCharField(null=True, max_length=20, unique=True)
    pack_plate_location = FixedCharField(max_length=2, null=True)
    order_no = IntegerField(null=True)
    filled_date = DateTimeField(null=True)
    filled_at = SmallIntegerField(null=True)
    # marked filled at which step
    # Any manual goes in 0-10, If filled by system should be > 10
    #  0 - Template(Auto marked manual for manual system),
    #  1 - Pack Pre-Processing/Facility Distribution, 2 - PackQueue, 3 - MVS
    #  11 - DosePacker
    fill_time = IntegerField(null=True, default=None)  # in seconds
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)
    facility_dis_id = ForeignKeyField(FacilityDistributionMaster, null=True)
    # facility_dis_id_id = IntegerField()
    car_id = IntegerField(null=True)
    unloading_time = DateTimeField(null=True)
    # facility_distribution_id_id = IntegerField()
    pack_sequence = IntegerField(null=True)
    dosage_type = ForeignKeyField(CodeMaster, default=settings.DOSAGE_TYPE_MULTI)
    pack_type = ForeignKeyField(CodeMaster, null=True, default=None, related_name="pack_type")
    filling_status = ForeignKeyField(CodeMaster, null=True, related_name="pack_details_filling_status")
    container_id = ForeignKeyField(ContainerMaster, null=True)
    previous_batch_id = ForeignKeyField(BatchMaster, null=True, related_name="pack_details_prev_batch")
    grid_type = ForeignKeyField(CodeMaster, null=True, default=constants.PACK_GRID_ROW_7x4, related_name="grid_type ")
    store_type = ForeignKeyField(CodeMaster, default=constants.STORE_TYPE_CYCLIC, related_name="pack_details_store_type")
    verification_status = ForeignKeyField(CodeMaster, default=constants.RPH_VERIFICATION_STATUS_NOT_CHECKED, related_name="pack_details_rph_verification_status")
    pack_checked_by = IntegerField(null=True, default=None)
    pack_checked_time = DateTimeField(null=True, default=None)
    queue_no = IntegerField(null=True)
    queue_type = CharField(null=True)
    delivered_date = DateTimeField(null=True)
    delivery_status = ForeignKeyField(CodeMaster, default=None, null=True, related_name="pack_details_delivery_status")
    bill_id = IntegerField(null=True, default=None)
    packaging_type = ForeignKeyField(CodeMaster, default=constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4, related_name="pack_details_packaging_type")

    FILLED_AT_MAP = {
        0: 'Auto',
        1: 'Pre-Batch Allocation',
        2: 'Post-Import',
        3: 'Manual Verification Station',
        4: 'Pre-Import',
        11: 'DosePacker'
    }

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"

    @classmethod
    def update_pack_filling_status(cls, pack_status_dict):
        """
        Function to update pack_filling_status in pack details
        @param pack_status_dict:
        @return:
        """
        try:
            for pack, status in pack_status_dict.items():
                response = PackDetails.update(filling_status=status) \
                    .where(PackDetails.id == pack).execute()
                logger.info(response)

            return True

        except (InternalError, IntegrityError) as e:
            logger.error(e)
            raise

    @classmethod
    def get_pack_count_by_clauses(cls, clauses, append_clause=None):
        """

        @param clauses:
        @param append_clause:
        @return:
        """
        try:
            if append_clause:
                clauses.append(append_clause)
            query = PackDetails.select(fn.COUNT(PackDetails.id).alias('pack_count')) \
                .where(functools.reduce(operator.and_, clauses))
            logger.info("In get_pack_count_by_clauses query:{}".format(query))
            if append_clause:
                clauses.pop()
            for record in query.dicts():
                logger.info("In get_pack_count_by_clauses: one hour pack count: {}".format(record['pack_count']))
                return record['pack_count']
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_pack_header_by_pack_detail_ids(cls, pack_ids):
        pack_header_ids: List[int] = []
        try:
            query = PackDetails.select(PackDetails.pack_header_id).dicts().where(PackDetails.id << pack_ids)
            for pack_header in query:
                pack_header_ids.append(pack_header["pack_header_id"])

            return pack_header_ids
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_pack_display_ids_by_pack_header(cls, pack_header_ids):
        pack_display_ids: List[int] = []
        try:
            query = PackDetails.select(PackDetails.pack_display_id).dicts()\
                .where(PackDetails.pack_header_id << pack_header_ids,
                       PackDetails.pack_status != settings.DELETED_PACK_STATUS)
            for pack in query:
                pack_display_ids.append(pack["pack_display_id"])

            return pack_display_ids
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_pack_details_by_display_ids(cls, pack_display_ids):
        pack_details: Dict[int, Any] = {}
        try:
            query = PackDetails.select(PackDetails.id.alias("pack_id"), PackDetails.pack_status,
                                       PackDetails.batch_id, PackDetails.facility_dis_id).dicts() \
                .where(PackDetails.pack_display_id << pack_display_ids)
            for pack in query:
                pack_details[pack["pack_id"]] = pack

            return pack_details
        except (InternalError, IntegrityError, ProgrammingError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_pack_list(cls, clauses):
        try:
            pack_ids: list = list()
            query = PackDetails.select(PackDetails.id).where(functools.reduce(operator.and_, clauses))
            for record in query.dicts():
                pack_ids.append(record["id"])
            return pack_ids
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_pack_ids(cls, batch_id, system_id):
        """
        Returns list of pack ids
        :param batch_id:
        :param system_id:
        :return: list
        """
        try:
            pack_ids = list()
            query = PackDetails.select(PackDetails.id) \
                .where(PackDetails.system_id == system_id,
                       PackDetails.batch_id == batch_id)
            for record in query:
                pack_ids.append(record.id)
            return pack_ids
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_pack_ids_by_batch_id(cls, batch_id: int, company_id: int) -> list:
        try:
            query = PackDetails.select(PackDetails.id) \
                .where(PackDetails.batch_id == batch_id,
                       PackDetails.company_id == company_id,
                       PackDetails.pack_status == settings.PENDING_PACK_STATUS)
            pack_ids = [record.id for record in query]
            return pack_ids
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_packs_by_facility_distribution_id(cls, facility_distribution_id: int, company_id: int) -> list:
        try:
            query = PackDetails.select(PackDetails.id) \
                .where(PackDetails.facility_dis_id == facility_distribution_id,
                       PackDetails.company_id == company_id,
                       PackDetails.pack_status << [settings.PENDING_PACK_STATUS])
            pack_ids = [record.id for record in query]
            return pack_ids
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_total_packs_count_for_batch(cls, batch_id):
        logger.info("Inside db_get_total_packs_count_for_batch {}".format(batch_id))
        try:
            if type(batch_id) != list:
                batch_list = [batch_id]
            else:
                batch_list = batch_id
            query = PackDetails.select(fn.COUNT(PackDetails.id)).where(PackDetails.batch_id << batch_list,
                                                                       PackDetails.pack_status.not_in(
                                                                           [settings.MANUAL_PACK_STATUS,
                                                                            settings.DELETED_PACK_STATUS,
                                                                            settings.PARTIALLY_FILLED_BY_ROBOT]),
                                                                       PackDetails.filled_at.is_null(
                                                                           True) | PackDetails.filled_at.not_in(
                                                                           [settings.FILLED_AT_POST_PROCESSING]))

            return query.scalar()
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_total_packs_count_for_imported_batch_or_merged_batch(cls, batch_id):
        logger.info("Inside db_get_total_packs_count_for_batch {}".format(batch_id))
        try:
            query = PackDetails.select(fn.COUNT(PackDetails.id)).where((PackDetails.batch_id == int(batch_id)) | (PackDetails.previous_batch_id == int(batch_id)),
                PackDetails.pack_status.not_in(
                                                                           [settings.MANUAL_PACK_STATUS,
                                                                            settings.DELETED_PACK_STATUS,
                                                                            settings.PARTIALLY_FILLED_BY_ROBOT]),
                                                                       PackDetails.filled_at.is_null(
                                                                           True) | PackDetails.filled_at.not_in(
                                                                           [settings.FILLED_AT_POST_PROCESSING]))

            return query.scalar()
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_filled_pack_count(cls, batch_id):
        try:
            query = PackDetails.select(fn.COUNT(PackDetails.id)).where(PackDetails.batch_id == batch_id,
                                                                       PackDetails.pack_status << (
                                                                           [settings.DONE_PACK_STATUS,
                                                                            settings.PROCESSED_MANUALLY_PACK_STATUS]),
                                                                       PackDetails.filled_at.not_in(
                                                                           [settings.FILLED_AT_POST_PROCESSING]))
            return query.scalar()
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_pack_ids_by_pack_display_id(cls, pack_display_ids, company_id):
        try:
            query = PackDetails.select(PackDetails.id, PackDetails.pack_display_id).dicts() \
                .where(PackDetails.pack_display_id << pack_display_ids,
                       PackDetails.company_id == company_id)
            pack_ids = {}
            # [{record.pack_display_id: record.id} for record in query]

            for record in query:
                pack_ids[record['pack_display_id']] = record['id']

            return pack_ids
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return {}
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_schedule_id(cls, pack_list, facility_distribution_id):
        """
        updates batch id for all packs in pack list when we move facility from left to right
        :param: pack_list : list of packs for a facility
                batch_id : schedule_id to b added for packs
        :return:
        """
        try:
            PackDetails.update(facility_dis_id=facility_distribution_id).where(PackDetails.id << pack_list).execute()
            return "rows updated"

        except IntegrityError as e:
            logger.error(e, exc_info=True)
            raise IntegrityError
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError

    @classmethod
    def update_schedule_id_null(cls, pack_list, facility_dis_id, update=False):
        """
        updates schedule id as null
         1. for given list in case when we move facility from right to left
         2. for packs which is not included in batch while save batch, so that packs move to left in facility screen
        :param: batch_id : for packs having schedule_id as batch_id
        :return:
        """
        try:
            clauses = list()
            if update:
                if facility_dis_id:
                    clauses.append((PackDetails.facility_dis_id == facility_dis_id))
                clauses.append((PackDetails.pack_status == settings.PENDING_PACK_STATUS))
                clauses.append((PackDetails.id.not_in(pack_list)))

            if update:
                PackDetails.update(facility_dis_id=None).where(functools.reduce(operator.and_, clauses)).execute()
            else:
                PackDetails.update(facility_dis_id=None).where(PackDetails.id << pack_list).execute()
            # record = PackDetails.select(PackDetails.id) \
            #         .where(PackDetails.facility_dis_id_id == facility_distribution_id)
            # print("record", record.count())
            # if record.count() == 0:
            #     print("facility id", facility_distribution_id)
            #     status = FacilityDistributionMaster.delete().where(
            # FacilityDistributionMaster.facility_distribution_id == facility_distribution_id).execute()
            #     FacilityDistributionMaster.al
            #     print("status", status)
            return "schedule id done null"

        except IntegrityError as e:
            logger.error(e, exc_info=True)

            raise IntegrityError
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError

    @staticmethod
    def update_pack_plate_location(**kwargs):
        logger.debug("Updating pack plate location for pack ids :" + str(kwargs))
        if not kwargs:
            return
        for key, value in kwargs.items():
            PackDetails.update(pack_plate_location=value).where(PackDetails.id == int(key)).execute()

    @classmethod
    def db_get_pack_display_ids(cls, pack_ids):
        pack_display_ids = []
        try:
            for record in PackDetails.select(
                    PackDetails.pack_display_id).dicts().where(PackDetails.id << pack_ids):
                pack_display_ids.append(str(record["pack_display_id"]))
            return pack_display_ids
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            raise DoesNotExist(ex)
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError(e)

    @classmethod
    def db_get_pack_id(cls, rfid):
        try:
            status = PackDetails.get(rfid=rfid).id
            return status
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            return 0
        except InternalError as ex:
            logger.error(ex, exc_info=True)
            return 0

    @classmethod
    def db_update_pack_order_no(cls, dict_order_list):
        update_info = False
        order_no_list = dict_order_list["order_nos"].split(',')
        pack_ids_list = dict_order_list["pack_ids"].split(',')
        system_id = int(dict_order_list["system_id"])

        try:
            with db.transaction():
                for index, item in enumerate(pack_ids_list):
                    update_info = PackDetails.update(order_no=order_no_list[index]) \
                        .where(PackDetails.system_id == system_id, PackDetails.id == item)
                    update_info = update_info.execute()
            return create_response(update_info)
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            return error(1004)

    @classmethod
    def db_update_batch_id_null(cls, pack_list, system_id):
        """
        Updates batch id null for manual pack
        @param pack_list:
        @param system_id:
        @return: int
        """
        try:
            with db.transaction():
                if len(pack_list) > 0:
                    update_info = PackDetails.update(batch_id=None).where(PackDetails.id << pack_list,
                                                                          PackDetails.system_id == system_id).execute()
                    return update_info

                return 0
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            raise DoesNotExist
        except InternalError as e:
            logger.error(e, exc_info=True)
            return InternalError

    @classmethod
    def db_get_deleted_packs_by_batch(cls, batch_id, company_id):
        """
        Return deleted packs out of batch id
        @param company_id:
        @param batch_id:
        @return:
        """
        try:
            logger.info("Inside get_deleted_packs_by_batch {}".format(batch_id))
            deleted_packs = list()
            query = PackDetails.select(PackDetails.id, PackDetails.pack_display_id).dicts() \
                .where(PackDetails.batch_id == batch_id,
                       PackDetails.pack_status == settings.DELETED_PACK_STATUS,
                       PackDetails.company_id == company_id)

            for record in query:
                deleted_packs.append(record['id'])

            logger.info("get_deleted_packs_by_batch response {}".format(deleted_packs))
            return deleted_packs
        except InternalError as e:
            raise e

    @classmethod
    def db_verify_pack_id_by_system_id(cls, pack_id, system_id=None):
        """ Returns True if pack id is generated for given system_id, False otherwise

        :param pack_id:
        :param system_id:
        :return: Boolean
        """
        pack_id = int(pack_id)
        if system_id:
            system_id = int(system_id)
        try:
            pack = PackDetails.get(id=pack_id)
            if system_id == pack.system_id:
                return True
            if pack_id and not system_id:
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError:
            return False

    @classmethod
    def db_verify_packlist(cls, packlist, company_id):
        """ Returns True if pack list is generated for given company_id , False otherwise

        :param packlist:
        :param company_id:
        :return: Boolean
        """
        company_id = int(company_id)
        try:
            pack_count = PackDetails.select().where(
                PackDetails.id << packlist,
                PackDetails.company_id == company_id
            ).count()
            if pack_count == len(set(packlist)):
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError:
            return False

    @classmethod
    def db_verify_packlist_by_system_id(cls, packlist, system_id):
        """ Returns True if pack list is generated for given system_id , False otherwise

        :param packlist:
        :param system_id:
        :return: Boolean
        """
        system_id = int(system_id)
        try:
            pack_count = PackDetails.select().where(
                PackDetails.id << packlist,
                PackDetails.system_id == system_id
            ).count()
            if pack_count == len(set(packlist)):
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError:
            return False

    @classmethod
    def db_update_pack_details(cls, update_dict: dict, pack_id: int) -> bool:
        """
        update pack_details for given pack id
        @param pack_id:
        @param update_dict:
        """
        try:
            status = PackDetails.update(**update_dict).where(PackDetails.id == pack_id).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_pack_id_list_by_status(cls, status: list, batch_id: int, pack_id_list: Optional[list] = None) -> list:
        """
        get pack id list for given status
        @param pack_id_list:
        @param status:
        @param batch_id:
        """
        pack_ids_list: list = list()
        try:
            if pack_id_list is None:
                query = PackDetails.select(PackDetails.id).where(
                    PackDetails.pack_status << status, PackDetails.batch_id == batch_id)
            else:
                query = PackDetails.select(PackDetails.id).where(
                    (PackDetails.id << pack_id_list) & (PackDetails.pack_status << status))
            for record in query.dicts():
                pack_ids_list.append(record['id'])

            return pack_ids_list
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_dict_pack_details(cls, update_dict, pack_id, system_id) -> bool:
        """
        update pack_details for given pack id
        @param update_dict:
        @param system_id:
        @param pack_id:
        """
        try:
            status = PackDetails.update(**update_dict).where(PackDetails.id == pack_id,
                                                             PackDetails.system_id == system_id).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_order_pack_id_list(cls, pack_id_list: list, system_id: int) -> list:
        """
        get order pack ids from pack id list
        @param system_id:
        @param pack_id_list:
        """
        pack_ids_list: list = list()
        try:
            query = PackDetails.select(PackDetails.id) \
                .where(PackDetails.id.in_(pack_id_list), PackDetails.system_id == system_id) \
                .order_by(PackDetails.order_no)

            for record in query.dicts():
                pack_ids_list.append(record["id"])
            return pack_ids_list
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_change_pack_sequence(cls, case_sequence, pack_list):
        """
        update order no
        :return:
        """
        try:
            status = cls.update(order_no=case_sequence).where(
                cls.id.in_(pack_list)).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_pack_order_no(cls, batch_id: int):
        """
        get query to get pack order
        @param batch_id:
        """
        try:
            query = PackDetails.select(PackDetails.id, PackDetails.order_no).dicts() \
                .where(PackDetails.batch_id == batch_id) \
                .order_by(PackDetails.order_no)
            return query
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_pending_order_pack_by_batch(cls, batch_id: int, priority: Optional[int] = None):
        """
        get query to get pack order
        @param priority:
        @param batch_id:
        """
        try:
            if priority == 1:
                query = PackDetails.select(PackDetails.id, PackDetails.order_no).dicts() \
                    .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                           PackDetails.batch_id == batch_id,
                           PackDetails.order_no.is_null(False)) \
                    .order_by(PackDetails.order_no)
                return query
            else:
                query = PackDetails.select(PackDetails.id, PackDetails.order_no).dicts() \
                    .where(PackDetails.pack_status << [settings.PENDING_PACK_STATUS],
                           PackDetails.batch_id == batch_id,
                           PackDetails.order_no.is_null(False)) \
                    .order_by(PackDetails.order_no.desc())
                return query

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_batch_status_wise_pack_count(cls, batch_id: int, status_list: list):
        """
        return status wise pack count
        @param status_list:
        @param batch_id:
        """
        try:
            query = PackDetails.select(fn.COUNT(PackDetails.id).alias("id"), PackDetails.pack_status).where(
                PackDetails.pack_status << status_list, PackDetails.batch_id == batch_id) \
                .group_by(PackDetails.pack_status)
            return query
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_batch_of_pack(cls, pack_list):
        packs = []
        query = PackDetails.select(PackDetails.batch_id, PackDetails.id).where(PackDetails.id << pack_list,
                                                                               PackDetails.batch_id.is_null(False))
        for record in query.dicts():
            packs.append(record['id'])

        return packs

    @classmethod
    def db_get_batch_id_from_packs(cls, pack_list):
        query = PackDetails.select(PackDetails.batch_id).where(PackDetails.id << pack_list,
                                                               PackDetails.batch_id.is_null(False))
        for record in query.dicts():
            return record['batch_id']

    @classmethod
    def db_get_pack_status(cls, pack_list):
        packs = []
        query = PackDetails.select(PackDetails.pack_status, PackDetails.id).where(PackDetails.id << pack_list,
                                                                                  PackDetails.pack_status ==
                                                                                  settings.MANUAL_PACK_STATUS)
        for record in query.dicts():
            packs.append(record['id'])
        return packs

    @classmethod
    def db_get_facility_distribution_ids(cls, pack_list: list):
        try:
            facility_distribution_id = set()
            query = PackDetails.select(PackDetails.facility_dis_id, PackDetails.id).where(PackDetails.id << pack_list)
            for record in query.dicts():
                facility_distribution_id.add(record['facility_dis_id'])
            return facility_distribution_id
        except (InternalError, IntegrityError) as e:
            logger.info(e)
            raise

    @classmethod
    def db_get_facility_distribution_id(cls, pack_list):
        try:
            query = PackDetails.select(fn.COUNT(fn.DISTINCT(PackDetails.facility_dis_id)).alias('count_facility_dis'),
                                       PackDetails.facility_dis_id).dicts() \
                .where(PackDetails.id << pack_list).get()
            if query['count_facility_dis'] == 1:
                return query['facility_dis_id']
            else:
                return None
        except DoesNotExist as e:
            logger.info(e)
            raise
        except (InternalError, IntegrityError) as e:
            logger.info(e)
            raise

    @classmethod
    def get_company_id_for_pack(cls, pack_ids):
        try:
            query = PackDetails.select(PackDetails.company_id).dicts().where(PackDetails.id << pack_ids).get()
            logger.debug("Query Data: {}".format(query))
            if query:
                return query["company_id"]
            else:
                return 0
        except DoesNotExist as e:
            logger.info(e)
            return 0
        except (InternalError, IntegrityError) as e:
            logger.info(e)
            raise

    @classmethod
    def db_get_pack_data(cls, pack_ids):
        try:
            query = PackDetails.select().dicts() \
                .where(PackDetails.id << pack_ids)
            return query
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            return 0
        except InternalError as ex:
            logger.error(ex, exc_info=True)
            return 0

    @classmethod
    def db_get_filled_pack_count_by_date(cls, company_id, from_date, to_date, offset):
        pack_count_list = list()
        try:
            filled_date = fn.DATE(fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC, offset))

            pack_count_query = PackDetails.select(fn.COUNT(PackDetails.id).alias('pack_count'),
                                                  PackDetails.filled_at, PackDetails.pack_type,
                                                  PackDetails.dosage_type, filled_date.alias('filled_date')).dicts() \
                .where(filled_date.between(from_date, to_date),
                       PackDetails.company_id == company_id) \
                .group_by(filled_date, PackDetails.filled_at, PackDetails.dosage_type, PackDetails.pack_type)

            print("In db_get_filled_pack_count_by_date: pack_count_query", str(pack_count_query))

            for count in pack_count_query:
                pack_count_list.append(count)
            return pack_count_list

        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error("error in db_get_filled_pack_count_by_date {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in db_get_filled_pack_count_by_date: exc_type - {exc_type}, filename - {filename}, line - "
                f"{exc_tb.tb_lineno}")
            raise e
        except DoesNotExist:
            logger.info('No packs filled on ' + str(from_date))
            return pack_count_list

    @classmethod
    def db_get_facility_dic_id_by_batch_id(cls, batch_id) -> int:
        try:
            facility_dist_id = PackDetails.select(PackDetails.facility_dis_id).dicts() \
                .where(PackDetails.batch_id == batch_id).get()
            return facility_dist_id['facility_dis_id']

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_max_order_no(cls, system_id):
        order_no = 0
        try:
            order_no = PackDetails.select(PackDetails.order_no) \
                .where(PackDetails.system_id == system_id) \
                .order_by(PackDetails.order_no.desc()) \
                .get().order_no
            return order_no
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            return order_no
        except InternalError as e:
            logger.error(e)
            return order_no

    @classmethod
    def db_check_batch_id_assign_for_packs(cls, pack_list) -> int:
        """
        function to get count of pack ids for which batch id is already assigned
        @param pack_list:
        """
        try:
            query = PackDetails.select().where(PackDetails.id.in_(pack_list), PackDetails.batch_id.is_null(False))
            return query.count()
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_pack_details_by_pack_list(cls, update_pack_dict: Dict[str, Any], pack_ids: List[int]):
        try:
            return PackDetails.update(**update_pack_dict).where(PackDetails.id << pack_ids).execute()
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_packs_partially_filled_by_robot(cls, today: date, offset, system_id: int, company_id: int) -> int:
        """
        function to get count of pack ids for which are marked as partially filled by robot for today
        @param today: date for which we need data
        @param offset: for timezone conversion
        @param system_id:
        @param company_id:
        """
        try:
            query = PackDetails.select(fn.COUNT(fn.distinct(PackDetails.id)).alias("pack_count")).where(
                fn.DATE(fn.CONVERT_TZ(
                    PackDetails.modified_date, settings.TZ_UTC,
                    offset)) == today, PackDetails.company_id == company_id, PackDetails.system_id ==
                system_id, PackDetails.pack_status == settings.PARTIALLY_FILLED_BY_ROBOT)
            logger.info("In db_get_packs_partially_filled_by_robot query:{}".format(query))

            return query.scalar()

        except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
            logger.error("error in get_packs_partially_filled_by_robot {}".format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_packs_partially_filled_by_robot: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            raise e


    @classmethod
    def db_get_last_order_no_of_given_batch(cls, batch_id: int):
        """
        get query to get last order no. of given batch
        @param batch_id:
        """
        try:
            query = PackDetails.select(fn.MAX(PackDetails.order_no).alias("last_order_no")).dicts() \
                .where(PackDetails.batch_id == batch_id, PackDetails.previous_batch_id.is_null(True))
            return query.scalar()
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_first_order_no_of_merged_batches(cls, batch_ids: list):
        """
        get query to get first order no. of given batches
        @param batch_ids:
        """
        try:
            merged_batch_first_order_no_details = list()
            query = PackDetails.select(fn.MIN(PackDetails.order_no).alias("first_order_no"),
                                       PackDetails.previous_batch_id.alias("merged_batch_id")).dicts() \
                .where(PackDetails.previous_batch_id << batch_ids).group_by(PackDetails.previous_batch_id)

            for record in query:
                merged_batch_first_order_no_details.append(record)
            return merged_batch_first_order_no_details
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_last_order_no_of_merged_batches(cls, batch_ids: list):
        """
        get query to get first order no. of given batches
        @param batch_ids:
        """
        try:
            merged_batch_first_order_no_details = list()
            query = PackDetails.select(fn.MAX(PackDetails.order_no).alias("last_order_no"),
                                       PackDetails.previous_batch_id.alias("merged_batch_id")).dicts() \
                .where(PackDetails.previous_batch_id << batch_ids).group_by(PackDetails.previous_batch_id)

            for record in query:
                merged_batch_first_order_no_details.append(record)
            return merged_batch_first_order_no_details
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_last_processed_pack_order_no_id_pack_status(cls):
        """
        get query to get last processed pack order no., pack id, pack status
        """
        try:
            last_processed_pack_list = list()
            query = PackDetails.select(fn.MAX(PackDetails.order_no).alias("last_processed_pack_order_no"),
                                       PackDetails.id.alias("pack_id"), PackDetails.pack_status).dicts() \
                .where(PackDetails.pack_status != 2, PackDetails.order_no != 0)
            for record in query:
                last_processed_pack_list.append(record)
            return last_processed_pack_list
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_first_merged_pending_pack_order_no_id_pack_status(cls, merged_pack_ids):
        """
        get query to get first merged pending pack order no., pack id, pack status
        @param merged_pack_ids:
        """
        try:
            first_merged_pending_pack_details = list()
            query = PackDetails.select(fn.MIN(PackDetails.order_no).alias("first_merged_pending_pack_order_no"),
                                       PackDetails.id.alias("pack_id"), PackDetails.pack_status).dicts() \
                .where(PackDetails.pack_status == 2, PackDetails.order_no != 0, PackDetails.id << merged_pack_ids)
            for record in query:
                first_merged_pending_pack_details.append(record)
            return first_merged_pending_pack_details
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_last_merged_pending_pack_order_no_id_pack_status(cls, merged_pack_ids):
        """
        get query to get last merged pending pack order no., pack id and pack status
        @param merged_pack_ids:
        """
        try:
            last_merged_pending_pack_details = list()
            query = PackDetails.select(fn.MAX(PackDetails.order_no).alias("last_merged_pending_pack_order_no"),
                                       PackDetails.id.alias("pack_id"), PackDetails.pack_status).dicts() \
                .where(PackDetails.pack_status == 2, PackDetails.order_no != 0, PackDetails.id << merged_pack_ids)
            for record in query:
                last_merged_pending_pack_details.append(record)
            return last_merged_pending_pack_details
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_verify_pack_display_id(cls, pack_display_id):
        """ Returns True if pack id is valid, False otherwise

        :param pack_id:
        :param system_id:
        :return: Boolean
        """
        pack_id = int(pack_display_id)
        try:
            pack = PackDetails.get(pack_display_id=pack_display_id)
            if pack:
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError:
            return False


