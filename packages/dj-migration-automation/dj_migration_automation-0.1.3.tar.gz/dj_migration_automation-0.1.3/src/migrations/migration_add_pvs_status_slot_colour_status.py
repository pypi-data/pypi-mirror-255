from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster


def migration_add_pvs_status_slot_colour():

    try:

        init_db(db, 'database_migration')

        if CodeMaster.table_exists():

            CodeMaster.insert(id=constants.SLOT_COLOUR_STATUS_WHITE,
                              group_id=constants.SLOT_COLOUR_STATUS_GROUP_ID,
                              value="White").execute()
            print("SLOT_COLOUR_STATUS_WHITE inserted in CodeMaster")

            CodeMaster.insert(id=constants.PVS_CLASSIFICATION_STATUS_BROKEN_PILL,
                              group_id=constants.PVS_CLASSIFICATION_STATUS_GROUP_ID,
                              value="Broken Pill").execute()
            print("PVS_CLASSIFICATION_STATUS_BROKEN_PILL inserted in CodeMaster")

            CodeMaster.insert(id=constants.PVS_CLASSIFICATION_STATUS_MAY_BE_BROKEN_PILL,
                              group_id=constants.PVS_CLASSIFICATION_STATUS_GROUP_ID,
                              value="May Be Broken Pill").execute()
            print("PVS_CLASSIFICATION_STATUS_MAY_BE_BROKEN_PILL inserted in CodeMaster")

    except Exception as e:
        print(e)
        raise


if __name__ == "__main__":
    migration_add_pvs_status_slot_colour()

