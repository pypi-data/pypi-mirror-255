from playhouse.migrate import *

from dosepack.base_model.base_model import db
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from model.model_init import init_db
from src import constants
from src.model.model_drug_tracker import DrugTracker


# ------------ STATUS OF GroupMaster DURING MIGRATION EXECUTION ------------
# class GroupMaster(BaseModel):
#     id = PrimaryKeyField()
#     name = CharField(max_length=50)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "group_master"

# ------------ STATUS OF CodeMaster DURING MIGRATION EXECUTION ------------
# class CodeMaster(BaseModel):
#     id = PrimaryKeyField()
#     group_id = ForeignKeyField(GroupMaster)
#     # key = SmallIntegerField(unique=True)
#     value = CharField(max_length=50)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "code_master"

# ------------ STATUS OF CanisterTracker DURING MIGRATION EXECUTION ------------
# class CanisterTracker(BaseModel):
#     """
#         @class: canister_tracker.py
#         @createdBy: Manish Agarwal
#         @createdDate: 04/19/2016
#         @lastModifiedBy: Payal Wadhwani
#         @lastModifiedDate: 11/25/2020
#         @type: file
#         @desc: logical class for table canister_tracker.
#                 Stores a record whenever a quantity is updated in canister
#     """
#     id = PrimaryKeyField()
#     canister_id = ForeignKeyField(CanisterMaster, related_name="ct_canister_id")
#     device_id = ForeignKeyField(DeviceMaster, null=True)  # device from where replenish done
#     drug_id = ForeignKeyField(DrugMaster)
#     qty_update_type_id = ForeignKeyField(CodeMaster, null=True)  # Whether canister is replenished or adjusted
#     quantity_adjusted = SmallIntegerField()
#     original_quantity = SmallIntegerField()
#     lot_number = CharField(max_length=30, null=True)
#     expiration_date = CharField(max_length=8, null=True)
#     note = CharField(null=True, max_length=100)
#     created_by = IntegerField()
#     created_date = DateTimeField(default=get_current_date_time)
#     voice_notification_uuid = CharField(null=True)
#     drug_scan_type_id = ForeignKeyField(CodeMaster, null=True, related_name="drug_bottle_scan_id")
#     replenish_mode_id = ForeignKeyField(CodeMaster, null=True, related_name="replenish_mode_id")
#     usage_consideration = ForeignKeyField(CodeMaster, related_name="uc_code_id_id",
#               default=constants.USAGE_CONSIDERATION_PENDING)
#
#     class Meta:
#         if settings.TABLE_NAMING_CONVENTION == "_":
#             db_table = "canister_tracker"


def migration_drug_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if GroupMaster.table_exists():
        GroupMaster.insert(id=constants.CANISTER_TRACKER_USAGE_CONSIDERATION_GROUP_ID,
                           name="CanisterTrackerUsageConsideration").execute()

    if CodeMaster.table_exists():
        CodeMaster.insert(id=constants.USAGE_CONSIDERATION_PENDING,
                          group_id=constants.CANISTER_TRACKER_USAGE_CONSIDERATION_GROUP_ID,
                          value='Pending').execute()
        CodeMaster.insert(id=constants.USAGE_CONSIDERATION_IN_PROGRESS,
                          group_id=constants.CANISTER_TRACKER_USAGE_CONSIDERATION_GROUP_ID,
                          value='In Progress').execute()
        CodeMaster.insert(id=constants.USAGE_CONSIDERATION_DONE,
                          group_id=constants.CANISTER_TRACKER_USAGE_CONSIDERATION_GROUP_ID,
                          value='Done').execute()

    if CanisterTracker.table_exists():
        migrate(
            migrator.add_column(CanisterTracker._meta.db_table,
                                CanisterTracker.usage_consideration.db_column,
                                CanisterTracker.usage_consideration),
        )
        print("Added column: usage_consideration in CanisterTracker")

    if not DrugTracker.table_exists():
        db.create_tables([DrugTracker], safe=True)
        print('Table created: DrugTracker')


if __name__ == '__main__':
    migration_drug_tracker()
