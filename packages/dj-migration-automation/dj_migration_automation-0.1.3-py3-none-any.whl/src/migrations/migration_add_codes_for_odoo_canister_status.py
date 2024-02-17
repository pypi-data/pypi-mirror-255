from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'group_master'


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


def migration_add_codes_for_odoo_canister_status():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if GroupMaster.table_exists():
            GroupMaster.insert(id=constants.REQUESTED_CANISTER_STATUS_GROUP_ID,
                               name='RequestedCanisterStatus').execute()

        if CodeMaster.table_exists():
            # codes for odoo requested canister status
            CodeMaster.insert(id=constants.APPROVED_ID,
                              group_id=constants.REQUESTED_CANISTER_STATUS_GROUP_ID,
                              value="Approved").execute()
            CodeMaster.insert(id=constants.IN_PROGRESS_ID,
                              group_id=constants.REQUESTED_CANISTER_STATUS_GROUP_ID,
                              value="In Progress").execute()
            CodeMaster.insert(id=constants.DONE_ID,
                              group_id=constants.REQUESTED_CANISTER_STATUS_GROUP_ID,
                              value="Done").execute()
            CodeMaster.insert(id=constants.CANCELLED_ID,
                              group_id=constants.REQUESTED_CANISTER_STATUS_GROUP_ID,
                              value="Cancelled").execute()
            CodeMaster.insert(id=constants.REJECTED_ID,
                              group_id=constants.REQUESTED_CANISTER_STATUS_GROUP_ID,
                              value="Rejected").execute()
            CodeMaster.insert(id=constants.PENDING_ID,
                              group_id=constants.REQUESTED_CANISTER_STATUS_GROUP_ID,
                              value="Pending").execute()

    except Exception as e:
        settings.logger.error("Error while adding Code Master and Group Master: ", str(e))


if __name__ == "__main__":
    migration_add_codes_for_odoo_canister_status()
