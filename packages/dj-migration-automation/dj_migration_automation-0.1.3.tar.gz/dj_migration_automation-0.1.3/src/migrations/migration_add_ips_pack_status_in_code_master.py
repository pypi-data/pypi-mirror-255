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

def migration_add_codes_for_ips_pack_status():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:


        if GroupMaster.table_exists():
            # codes for canister testing
            GroupMaster.insert(id=constants.PHARMACY_PACK_STATUS_GROUP_ID,
                              name="PharmacyPackStatus").execute()

            print("Data inserted in the GroupMaster table.")

        if CodeMaster.table_exists():
            # codes for canister testing
            CodeMaster.insert(id=constants.PHARMACY_PACK_STATUS_NOT_FILLED,
                              group_id=constants.PHARMACY_PACK_STATUS_GROUP_ID,
                              value="Not Filled (Fill Data Missing)").execute()

            print("Data inserted in the CodeMaster table.")
            CodeMaster.insert(id=constants.PHARMACY_PACK_STATUS_FILL_ERROR,
                              group_id=constants.PHARMACY_PACK_STATUS_GROUP_ID,
                              value="Fill Error").execute()

            print("Data inserted in the CodeMaster table.")
            CodeMaster.insert(id=constants.PHARMACY_PACK_STATUS_FIX_ERROR,
                              group_id=constants.PHARMACY_PACK_STATUS_GROUP_ID,
                              value="Fix Error").execute()

            print("Data inserted in the CodeMaster table.")
            CodeMaster.insert(id=constants.PHARMACY_PACK_STATUS_FILLED,
                              group_id=constants.PHARMACY_PACK_STATUS_GROUP_ID,
                              value="Filled (Not Checked)").execute()

            print("Data inserted in the CodeMaster table.")
            CodeMaster.insert(id=constants.PHARMACY_PACK_STATUS_CHECKED,
                              group_id=constants.PHARMACY_PACK_STATUS_GROUP_ID,
                              value="Checked").execute()

            print("Data inserted in the CodeMaster table.")
            CodeMaster.insert(id=constants.PHARMACY_PACK_STATUS_NOT_DELIVERED,
                              group_id=constants.PHARMACY_PACK_STATUS_GROUP_ID,
                              value="Not Delivered").execute()

            print("Data inserted in the CodeMaster table.")


    except Exception as e:
        settings.logger.error("Error while adding Code Master ", str(e))


if __name__ == "__main__":
    migration_add_codes_for_ips_pack_status()
