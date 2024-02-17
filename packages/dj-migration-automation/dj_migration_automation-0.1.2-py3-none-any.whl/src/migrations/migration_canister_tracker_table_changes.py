from playhouse.migrate import MySQLMigrator, migrate

import src.constants
from dosepack.base_model.base_model import BaseModel, db
from peewee import *
import settings
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()


class DrugMaster(BaseModel):
    id = PrimaryKeyField()


class OLDCanisterTracker(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)  # refill_device_id
    drug_id = ForeignKeyField(DrugMaster)
    refill_type = SmallIntegerField(null=True)  # 1 for refill-device
    quantity_adjusted = SmallIntegerField()
    original_quantity = SmallIntegerField()
    lot_number = CharField(max_length=30, null=True)
    expiration_date = CharField(max_length=8, null=True)
    # expiration_date = DateField(null=True)
    note = CharField(null=True, max_length=100)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    created_time = TimeField()
    voice_notification_uuid = CharField(null=True)
    drug_scan_type = ForeignKeyField(CodeMaster, default=src.constants.DATA_MATRIX)
    replenish_mode = ForeignKeyField(CodeMaster, default=src.constants.MANUAL_CODE, related_name="rep_mode")
    canister_scan_type = ForeignKeyField(CodeMaster, default=src.constants.DATA_MATRIX, related_name="can_scan_type")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tracker"


class CanisterTracker(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)  # device from where replenish done
    drug_id = ForeignKeyField(DrugMaster)
    qty_update_type_id = ForeignKeyField(CodeMaster, null=True)
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

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tracker"


def remove_columns(migrator):
    try:
        # drop column created_time as we already hav created_datetime field
        migrate(
            migrator.drop_column(OLDCanisterTracker._meta.db_table,
                                 OLDCanisterTracker.created_time.db_column),
            migrator.drop_column(OLDCanisterTracker._meta.db_table,
                                 OLDCanisterTracker.canister_scan_type.db_column)
        )
        print("CanisterTracker - Dropped column created_time")
    except Exception as e:
        settings.logger.error("Error while removing columns- " + str(e))


def rename_columns(migrator):
    try:
        migrate(
            migrator.rename_column(OLDCanisterTracker._meta.db_table,
                                   OLDCanisterTracker.refill_type.db_column,
                                   'qty_update_type_id_id'),
            migrator.rename_column(OLDCanisterTracker._meta.db_table,
                                   OLDCanisterTracker.drug_scan_type.db_column,
                                   'drug_scan_type_id_id'),
            migrator.rename_column(OLDCanisterTracker._meta.db_table,
                                   OLDCanisterTracker.replenish_mode.db_column,
                                   'replenish_mode_id_id'),
        )
        print("modified column names in canister_tracker table")
    except Exception as e:
        settings.logger.error("Error while renaming columns - "+str(e))


def update_null_in_field_refill_type():
    try:
        CanisterTracker.update(qty_update_type_id=None).execute()
        print("Values updated in field qty_update_type_id")
    except Exception as e:
        settings.logger.error("Error while updating values in column qty_update_type_id")


def add_foreign_key(migrator):
    try:
        db.execute_sql("ALTER TABLE canister_tracker MODIFY COLUMN qty_update_type_id_id INT;")
        migrate(
            migrator.add_foreign_key_constraint(CanisterTracker._meta.db_table, CanisterTracker.qty_update_type_id.db_column,
                                                CodeMaster._meta.db_table, CodeMaster.id.db_column)
        )
        print("Added foreign key constraint for column qty_update_type_id")
    except Exception as e:
        settings.logger.error("Error while adding foreign key constraint for column qty_update_type_id - "+str(e))


def set_nullable_columns(migrator):
    try:
        migrate(
            migrator.drop_not_null(CanisterTracker._meta.db_table,
                                   CanisterTracker.drug_scan_type_id.db_column,
                                   ),
            migrator.drop_not_null(CanisterTracker._meta.db_table,
                                   CanisterTracker.replenish_mode_id.db_column,
                                   ),
        )
        print("dropped not null constraint for some columns in canister tracker table")
    except Exception as e:
        settings.logger.error("Error while dropping not null constraint - "+str(e))


def code_addition():
    try:

        GroupMaster.insert(id=constants.CANISTER_QUANTITY_UPDATE_TYPE_GROUP_ID,
                           name="CanisterQuantityUpdateType").execute()

        CodeMaster.insert(id=constants.CANISTER_QUANTITY_UPDATE_TYPE_REPLENISHMENT,
                          group_id=constants.CANISTER_QUANTITY_UPDATE_TYPE_GROUP_ID,
                          value="Replenishment").execute()

        CodeMaster.insert(id=constants.CANISTER_QUANTITY_UPDATE_TYPE_ADJUSTMENT,
                          group_id=constants.CANISTER_QUANTITY_UPDATE_TYPE_GROUP_ID,
                          value="Adjustment").execute()

        CodeMaster.insert(id=src.constants.REPLENISHED_WITH_ENTIRE_DRUG_BOTTLE,
                          group_id=src.constants.REPLENISH_MODE_GROUP_ID,
                          value="Replenished with Entire Drug Bottle").execute()
        print("Code added in group_master and code_master")

    except Exception as e:
        settings.logger.error("Error while adding Code in code_master- "+str(e))


def update_records():
    try:
        update1 = CanisterTracker.update(qty_update_type_id=constants.CANISTER_QUANTITY_UPDATE_TYPE_REPLENISHMENT) \
                                .where(CanisterTracker.quantity_adjusted > 0).execute()
        update2 = CanisterTracker.update(qty_update_type_id=constants.CANISTER_QUANTITY_UPDATE_TYPE_ADJUSTMENT) \
            .where(CanisterTracker.quantity_adjusted <= 0).execute()
        print("Updated table canister tracker with status - {} and {}".format(update1, update2))

    except Exception as e:
        settings.logger.error("Error while updating canister tracker table- "+str(e))


def canister_tracker_table_changes():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    remove_columns(migrator)
    rename_columns(migrator)
    update_null_in_field_refill_type()
    add_foreign_key(migrator)
    set_nullable_columns(migrator)
    code_addition()
    update_records()


if __name__ == "__main__":
    canister_tracker_table_changes()
