from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster


def add_blue_red_blue_colour_in_code_master():
    try:

        init_db(db, 'database_migration')

        with db.transaction():

            if CodeMaster.table_exists():

                CodeMaster.insert(id=constants.SLOT_COLOUR_STATUS_BLUE,
                                  group_id=constants.SLOT_COLOUR_STATUS_GROUP_ID,
                                  value="Blue").execute()
                print("SLOT_COLOUR_STATUS_BLUE inserted in CodeMaster")

                CodeMaster.insert(id=constants.SLOT_COLOUR_STATUS_RED_BLUE,
                                  group_id=constants.SLOT_COLOUR_STATUS_GROUP_ID,
                                  value="Red-Blue").execute()
                print("SLOT_COLOUR_STATUS_RED_BLUE inserted in CodeMaster")

    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    add_blue_red_blue_colour_in_code_master()