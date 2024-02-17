from datetime import date

from peewee import PrimaryKeyField, ForeignKeyField, SmallIntegerField, CharField, IntegerField, DateTimeField, fn, \
    InternalError, IntegrityError, DataError, DoesNotExist

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_canister import logger
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_device_master import DeviceMaster


class CanisterTracker(BaseModel):
    """
        @class: canister_tracker.py
        @createdBy: Manish Agarwal
        @createdDate: 04/19/2016
        @lastModifiedBy: Payal Wadhwani
        @lastModifiedDate: 11/25/2020
        @type: file
        @desc: logical class for table canister_tracker.
                Stores a record whenever a quantity is updated in canister
    """
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)  # device from where replenish done
    drug_id = ForeignKeyField(DrugMaster)
    qty_update_type_id = ForeignKeyField(CodeMaster, null=True)  # Whether canister is replenished or adjusted
    quantity_adjusted = SmallIntegerField()
    original_quantity = SmallIntegerField()
    lot_number = CharField(max_length=30, null=True)
    expiration_date = CharField(max_length=8, null=True)
    note = CharField(null=True, max_length=100)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    voice_notification_uuid = CharField(null=True)
    drug_scan_type_id = ForeignKeyField(CodeMaster, null=True, related_name="drug_bottle_scan_id")
    replenish_mode_id = ForeignKeyField(CodeMaster, null=True, related_name="replenish_mode_id")
    usage_consideration = ForeignKeyField(CodeMaster, related_name="uc_code_id_id", default=constants.USAGE_CONSIDERATION_PENDING)
    modified_date = DateTimeField(default=get_current_date_time)
    case_id = CharField(null=True, default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tracker"

    @classmethod
    def update_usage_consideration_status(cls, replenish_ids, status):
        """
        Function to update sage_consideration_status in canister tracker
        @param replenish_ids: ids for which status gets updated
        @param status: status to update
        @return:
        """
        try:
            response = CanisterTracker.update(usage_consideration=status,
                                              modified_date=get_current_date_time()) \
                .where(CanisterTracker.id << replenish_ids).execute()
            logger.info("response for update_usage_consideration_status: " + str(response))
            return True

        except (InternalError, IntegrityError) as e:
            logger.error(e)
            raise

    @classmethod
    def db_create_canister_tracker(cls, canister_tracker_info):
        try:
            BaseModel.db_create_record({
                "canister_id": canister_tracker_info["canister_id"],
                "device_id": canister_tracker_info["device_id"],
                "drug_id": canister_tracker_info["drug_id"],
                "qty_update_type_id": canister_tracker_info["qty_update_type_id"],
                "original_quantity": canister_tracker_info["original_quantity"],
                "quantity_adjusted": canister_tracker_info["quantity_adjusted"],
                "lot_number": canister_tracker_info["lot_number"],
                "expiration_date": canister_tracker_info["expiration_date"],
                "note": canister_tracker_info["note"],
                "created_by": canister_tracker_info["created_by"],
                "drug_scan_type_id": canister_tracker_info.get("drug_scan_type_id", None),
                "replenish_mode_id": canister_tracker_info.get("replenish_mode_id", None),
                "voice_notification_uuid": canister_tracker_info.get("voice_notification_uuid", None)
            }, CanisterTracker, get_or_create=False)
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_add_canister_drawer(cls, canister_drawer_data, default_dict):
        try:
            record, created = CanisterTracker.get_or_create(
                device_id=canister_drawer_data["device_id"],
                drawer_number=canister_drawer_data["drawer_number"],
                drawer_id=canister_drawer_data["drawer_id"],
                defaults=default_dict
            )
            return record.id
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_drug_replenish_details_from_canister_tracker(cls, from_date: date, to_date: date, offset) -> list:
        """
        Return canister transfer details from canister history table
        @param from_date:
        @param to_date:
        @return:
        """
        try:
            logger.info('In get_drug_replenish_details_from_canister_tracker')
            drug_replenish_details = list()
            query = CanisterTracker.select(CanisterTracker.canister_id,
                                           fn.CONVERT_TZ(CanisterTracker.created_date, settings.TZ_UTC,
                                                         offset).alias('canister_tracker_created_date'),
                                           CanisterTracker.replenish_mode_id.alias("replenish_mode")
                                           ).distinct().dicts() \
                .where((fn.CONVERT_TZ(CanisterTracker.created_date, settings.TZ_UTC,
                                      offset)).between(from_date, to_date)
                       ).order_by(CanisterTracker.canister_id)

            logger.info("In get_drug_replenish_details_from_canister_tracker:{}".format(query))

            for record in query:
                drug_replenish_details.append(record)

            return drug_replenish_details
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error("error in get_drug_replenish_guided_details {}".format(e))
            raise e
        except Exception as e:
            logger.error("error in get_drug_replenish_guided_details {}".format(e))
            raise e

    @classmethod
    def db_get_canister_last_replenished_drug_dao(cls, canister_id):
        """
        Returns the last canister's replenished drug.
        @param canister_id:
        @return:
        """
        try:
            drug_id = None
            query = CanisterTracker.select(CanisterTracker.drug_id).dicts() \
                .where(CanisterTracker.canister_id == canister_id) \
                .order_by(CanisterTracker.id.desc()).limit(1)
            for record in query:
                drug_id = record['drug_id']
            return drug_id
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error("error in db_get_canister_last_replenished_drug_dao {}".format(e))
            raise e
        except Exception as e:
            logger.error("error in db_get_canister_last_replenished_drug_dao {}".format(e))
            raise e

    @classmethod
    def db_get_last_canister_replenish_id(cls, canister_id):
        """
        Returns the last canister replenish id
        """
        logger.info("In db_get_last_canister_replenish_id: canister_id: {}".format(canister_id))
        try:
            canister_tracker_data = dict()
            query = (CanisterTracker.select(CanisterTracker.id, CanisterTracker.lot_number,
                                            CanisterTracker.expiration_date, CanisterTracker.case_id)
                     .dicts()
                     .where(CanisterTracker.canister_id == canister_id)
                     .order_by(CanisterTracker.id.desc()).limit(1))

            for record in query:
                canister_tracker_data["canister_tracker_id"] = record["id"]
                canister_tracker_data["lot_number"] = record["lot_number"]
                canister_tracker_data["expiration_date"] = record["expiration_date"]
                canister_tracker_data["case_id"] = record["case_id"]

            return canister_tracker_data

        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error("Error in db_get_last_canister_replenish_id {}".format(e))
            raise e
        except Exception as e:
            logger.error("Error in db_get_last_canister_replenish_id {}".format(e))
            raise e
