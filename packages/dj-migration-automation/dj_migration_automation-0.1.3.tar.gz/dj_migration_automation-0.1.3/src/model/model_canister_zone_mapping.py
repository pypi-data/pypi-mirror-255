from peewee import PrimaryKeyField, ForeignKeyField, DateTimeField, IntegerField, IntegrityError, InternalError, \
    DataError, fn, Clause

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_canister_master import CanisterMaster
from src.model.model_zone_master import ZoneMaster


logger = settings.logger


class CanisterZoneMapping(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    zone_id = ForeignKeyField(ZoneMaster)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_zone_mapping"

    @classmethod
    def update_canister_zone_mapping_by_rfid(cls, zone_ids, user_id, rfid):
        try:
            canister_id = CanisterMaster.select(CanisterMaster.id).where(CanisterMaster.rfid == rfid).get().id
            cls.update_canister_zone_mapping_by_canister_id(zone_ids, user_id, canister_id)
        except IntegrityError as e:
            raise InternalError(e)
        except InternalError as e:
            raise InternalError(e)
        except DataError as e:
            raise DataError(e)

    @classmethod
    def db_create_canister_zone_mapping(cls, canister_master_id, zone_id, user_id):
        try:
            BaseModel.db_create_record({
                "canister_id": canister_master_id,
                "zone_id": zone_id,
                "created_time": get_current_date_time(),
                "created_by": user_id,
                }, CanisterZoneMapping, get_or_create=False)
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_canister_zone_mapping_by_canister_id(cls, zone_ids, user_id, canister_id):
        try:
            zone_data = CanisterZoneMapping.select(fn.GROUP_CONCAT(Clause(fn.DISTINCT(
                fn.IF(CanisterZoneMapping.id.is_null(True), 'null', CanisterZoneMapping.id)))).alias(
                'canister_zone_id'),
                fn.GROUP_CONCAT(Clause(fn.DISTINCT(
                    fn.IF(CanisterZoneMapping.zone_id.is_null(True), 'null',
                          CanisterZoneMapping.zone_id)))).alias('zone_id')) \
                .where(CanisterZoneMapping.canister_id == canister_id).dicts().get()

            if zone_data["zone_id"] is not None:
                existing_zone_ids = list(map(lambda x: int(x), zone_data["zone_id"].split(',')))
                canister_zone_ids = list(map(lambda x: int(x), zone_data["canister_zone_id"].split(',')))

                # when existing_zone_ids in table is same as new zone_ids
                if zone_ids == existing_zone_ids:
                    zone_update_status = 0
                # when number of existing records and to updates records are same
                elif len(zone_ids) == len(existing_zone_ids):
                    update_dict = {canister_zone_ids[i]: zone_ids[i] for i in range(len(zone_ids))}
                    for canister_zone_id, zone_id in update_dict.items():
                        update_info = {"canister_id": canister_id, "zone_id": zone_id,
                                       "created_date": get_current_date_time(), "created_by": user_id}
                        zone_update_status = CanisterZoneMapping.update(**update_info).where(
                            CanisterZoneMapping.id == canister_zone_id).execute()

                #   if existing zone id is 1 and records in zone_ids are 2 then update existing record and
                #   add one more records
                elif len(zone_ids) > len(existing_zone_ids):
                    zone_update_status = CanisterZoneMapping.update(zone_id=zone_ids[0],
                                                                    created_date=get_current_date_time(),
                                                                    created_by=user_id) \
                        .where(CanisterZoneMapping.canister_id == canister_id).execute()
                    zone_update_status = CanisterZoneMapping.insert(canister_id=canister_id, zone_id=zone_ids[1],
                                                                    created_date=get_current_date_time(),
                                                                    created_by=user_id).execute()

                # when two records exist and if we want to update with one zone id then delete one record and
                # update another one
                else:
                    CanisterZoneMapping.delete().where(CanisterZoneMapping.id == canister_zone_ids[0]).execute()
                    update_info = {"canister_id": canister_id, "zone_id": zone_ids[0],
                                   "created_date": get_current_date_time(), "created_by": user_id}
                    zone_update_status = CanisterZoneMapping.update(**update_info).where(
                        CanisterZoneMapping.id == canister_zone_ids[1]).execute()
            else:
                zone_records = []
                for zone_id in zone_ids:
                    zone_records.append(
                        {"canister_id": canister_id, "zone_id": zone_id, "created_date": get_current_date_time(),
                         "created_by": user_id})
                zone_update_status = CanisterZoneMapping.insert_many(zone_records).execute()

            return zone_update_status

        except (IntegrityError, InternalError, DataError, Exception) as e:
            raise e

    @classmethod
    def db_canister_zone_mapping_insert_bulk_data(cls, insert_zone_data):
        try:
            return CanisterZoneMapping.insert_many(insert_zone_data).execute()
        except (IntegrityError, InternalError, DataError, Exception) as e:
            raise e
