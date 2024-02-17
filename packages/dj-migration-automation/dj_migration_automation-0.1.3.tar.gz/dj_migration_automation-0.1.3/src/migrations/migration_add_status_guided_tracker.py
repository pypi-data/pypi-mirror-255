from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'group_master'


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


class LocationMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


def add_codes_for_guided_tracker():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if CodeMaster.table_exists():
            # codes for guided tracker

            CodeMaster.insert(id=constants.GUIDED_TRACKER_TO_TROLLEY_SKIPPED,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Tracker To Trolley Skipped").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Tracker To Trolley Skipped and Alternate").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE_TRANSFER_LATER,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Tracker To Trolley Alternate Transfer Later").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_TO_ROBOT_SKIPPED,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Tracker To Robot Skipped").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_TO_ROBOT_SKIPPED_AND_ALTERNATE,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Tracker To Robot Skipped and Alternate").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE_TRANSFER_LATER,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Tracker To Robot Alternate Transfer Later").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_TO_CSR_SKIPPED,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Tracker To CSR Skipped").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_DRUG_SKIPPED,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Tracker Drug Skipped").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_TO_TROLLEY_ALTERNATE,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Tracker To Trolley Alternate").execute()
            CodeMaster.insert(id=constants.GUIDED_TRACKER_TO_ROBOT_ALTERNATE,
                              group_id=constants.GUIDED_TRACKER_GROUP_ID,
                              value="Guided Tracker To Robot Alternate").execute()

            print("Added codes in Code Master")

        if ActionMaster.table_exists():
            ActionMaster.create(id=constants.GUIDED_TRACKER_TRANSFER_ACTION, key=constants.GUIDED_TRACKER_TRANSFER_ACTION,
                                group_id=constants.GUIDED_TRACKER_GROUP_ID, value="Guided Canister Transfer")
            ActionMaster.create(id=constants.GUIDED_TRACKER_SKIPPED_ACTION, key=constants.GUIDED_TRACKER_SKIPPED_ACTION,
                                group_id=constants.GUIDED_TRACKER_GROUP_ID, value="Guided Canister Skipped")
            ActionMaster.create(id=constants.GUIDED_TRACKER_SKIPPED_AND_DEACTIVATE_ACTION,
                                key=constants.GUIDED_TRACKER_SKIPPED_AND_DEACTIVATE_ACTION,
                                group_id=constants.GUIDED_TRACKER_GROUP_ID, value="Guided Canister Skipped and Deactive")

            print("Data inserted in the Action Master table.")

    except Exception as e:
        settings.logger.error("Error while adding codes in code_master and group_master: ", str(e))


if __name__ == "__main__":
    add_codes_for_guided_tracker()
