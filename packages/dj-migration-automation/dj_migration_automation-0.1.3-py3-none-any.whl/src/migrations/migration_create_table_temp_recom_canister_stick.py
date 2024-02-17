from dosepack.base_model.base_model import db, BaseModel
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from model.model_init import init_db
from src import constants
from src.model.model_temp_recommnded_stick_canister import TempRecommendedStickCanisterData


def migration_temp_recom_canister_stick():

    init_db(db, 'database_migration')
    if not TempRecommendedStickCanisterData.table_exists():
        db.create_tables([TempRecommendedStickCanisterData], safe=True)
        print('Table(s) created: TempRecommendedStickCanisterData')

    if GroupMaster.table_exists():
        GroupMaster.insert(id=constants.RECOMMENDED_STICK_CANISTER_STATUS_GROUP_ID,
                           name='RecommendedStickCanisterStatus').execute()

    if CodeMaster.table_exists():
        # for Canister testing pending use code same as canister testing status
        #     CANISTER_TESTING_GROUP_ID = 36
        #     CANISTER_TESTING_PASS = 145
        #     CANISTER_TESTING_FAIL = 146
        #     CANISTER_TESTING_PENDING = 198
        # Recommended stick canister status
        CodeMaster.insert(id=constants.CANISTER_DEFECTIVE_ID,
                          group_id=constants.RECOMMENDED_STICK_CANISTER_STATUS_GROUP_ID,
                          value="Defective").execute()
        CodeMaster.insert(id=constants.CANISTER_NOT_AVAILABLE_ID,
                          group_id=constants.RECOMMENDED_STICK_CANISTER_STATUS_GROUP_ID,
                          value="Not Available").execute()


if __name__ == "__main__":
    migration_temp_recom_canister_stick()
