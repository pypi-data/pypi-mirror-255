from playhouse.migrate import MySQLMigrator, migrate

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_action_master import ActionMaster
from src.model.model_code_master import CodeMaster
from src.model.model_group_master import GroupMaster
from src.model.model_pack_analysis_details import PackAnalysisDetails


def add_status_column_in_pack_analysis_details():
    try:

        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        with db.transaction():

            if GroupMaster.table_exists():

                GroupMaster.insert(id=constants.REPLENISH_CANISTER_STATUS_GROUP_ID,
                                   name="ReplenishCanisterTransferStatus").execute()
                print("REPLENISH_CANISTER_STATUS_GROUP_ID inserted in GroupMaster")

            if CodeMaster.table_exists():

                CodeMaster.insert(id=constants.REPLENISH_CANISTER_TRANSFER_SKIPPED,
                                  group_id=constants.REPLENISH_CANISTER_STATUS_GROUP_ID,
                                  value="Replenish Canister Transfer Skipped ").execute()
                print("SKIPPED_REPLENISH_CANISTER_TRANSFER inserted in CodeMaster")

                CodeMaster.insert(id=constants.REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED,
                                  group_id=constants.REPLENISH_CANISTER_STATUS_GROUP_ID,
                                  value="Replenish Canister Transfer Not Skipped").execute()
                print("REPLENISH_CANISTER_TRANSFER_NOT_SKIPPED inserted in CodeMaster")

                CodeMaster.insert(id=constants.SKIPPED_DUE_TO_MANUAL_PACK,
                                  group_id=constants.REPLENISH_CANISTER_STATUS_GROUP_ID,
                                  value="Skipped Due To Manual Pack").execute()
                print("SKIPPED_DUE_TO_MANUAL_PACK inserted in CodeMaster")

            if PackAnalysisDetails.table_exists():
                print("Running... .. .")
                migrate(migrator.add_column(PackAnalysisDetails._meta.db_table,
                                            PackAnalysisDetails.status.db_column,
                                            PackAnalysisDetails.status))
                print("Add 'status' column in PackAnalysisDetails")

                PackAnalysisDetails.update(status=constants.SKIPPED_DUE_TO_MANUAL_PACK) \
                    .where(PackAnalysisDetails.config_id.is_null(True),
                           PackAnalysisDetails.location_number.is_null(True),
                           PackAnalysisDetails.drop_number.is_null(True),
                           PackAnalysisDetails.canister_id.is_null(True),
                           PackAnalysisDetails.device_id.is_null(True),
                           PackAnalysisDetails.quadrant.is_null(True)).execute()
                print("SKIPPED_DUE_TO_MANUAL_PACK status updated in PackAnalysisDetails")

                PackAnalysisDetails.update(status=constants.REPLENISH_CANISTER_TRANSFER_SKIPPED) \
                    .where(PackAnalysisDetails.config_id.is_null(True),
                           PackAnalysisDetails.location_number.is_null(True),
                           PackAnalysisDetails.drop_number.is_null(True),
                           PackAnalysisDetails.quadrant.is_null(True),
                           PackAnalysisDetails.status != constants.SKIPPED_DUE_TO_MANUAL_PACK).execute()
                print("REPLENISH_CANISTER_TRANSFER_SKIPPED status updated in PackAnalysisDetails")

            if ActionMaster.table_exists():
                ActionMaster.insert(id=53,
                                    group_id=constants.BATCH_CHANGE,
                                    value=constants.REPLENISH_REVERTED_PACKS).execute()
                print("REPLENISH_AFTER_SKIP action inserted in ActionMaster")

    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    add_status_column_in_pack_analysis_details()