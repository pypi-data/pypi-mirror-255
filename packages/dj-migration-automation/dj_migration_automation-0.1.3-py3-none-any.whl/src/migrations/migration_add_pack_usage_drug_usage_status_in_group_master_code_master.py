import settings
from src import constants
from playhouse.migrate import *
from model.model_init import init_db
from src.model.model_code_master import CodeMaster
from src.model.model_group_master import GroupMaster
from dosepack.base_model.base_model import db, BaseModel


def add_pack_usage_drug_usage_status_in_group_master_and_code_master():
    try:
        init_db(db, 'database_migration')
        migrator = MySQLMigrator(db)

        with (db.transaction()):
            if CodeMaster.table_exists():
                # codes for pack_usage status
                CodeMaster.insert(id=constants.EXT_PACK_USAGE_STATUS_PROGRESS_ID,
                                  group_id=constants.EXT_PACK_USAGE_STATUS_GROUP_ID,
                                  value=constants.EXT_PACK_USAGE_STATUS_PROGRESS_DESC
                                  ).execute()

                print("Pack In Progress status added in code_master")

                CodeMaster.insert(id=constants.EXT_PACK_USAGE_STATUS_RTS_DONE_ID,
                                  group_id=constants.EXT_PACK_USAGE_STATUS_GROUP_ID,
                                  value=constants.EXT_PACK_USAGE_STATUS_RTS_DONE_DESC
                                  ).execute()

                print("Pack RTS Done status added in code_master")

                CodeMaster.insert(id=constants.EXT_PACK_USAGE_STATUS_PACK_RESEALED_ID,
                                  group_id=constants.EXT_PACK_USAGE_STATUS_GROUP_ID,
                                  value=constants.EXT_PACK_USAGE_STATUS_PACK_RESEALED_DESC
                                  ).execute()

                print("Pack Resealed status added in code_master")

                CodeMaster.insert(id=constants.EXT_PACK_USAGE_STATUS_PACK_DISCARDED_ID,
                                  group_id=constants.EXT_PACK_USAGE_STATUS_GROUP_ID,
                                  value=constants.EXT_PACK_USAGE_STATUS_PACK_DISCARDED_DESC
                                  ).execute()

                print("Pack Discarded status added in code_master")

            if GroupMaster.table_exists():
                # group_code for drug usage status
                GroupMaster.insert(id=constants.REUSE_DRUG_STATUS_GROUP_ID,
                                   name=constants.REUSE_DRUG_STATUS_GROUP_DESC
                                   ).execute()

                print("Drug Usage group code added in group_master")

            if CodeMaster.table_exists():
                # codes for drug usage status in code_master
                CodeMaster.insert(id=constants.REUSE_DRUG_STATUS_DRUG_REUSE_PENDING_ID,
                                  group_id=constants.REUSE_DRUG_STATUS_GROUP_ID,
                                  value=constants.REUSE_DRUG_STATUS_DRUG_REUSE_PENDING_DESC
                                  ).execute()

                print("Drug Reuse Pending status added in code_master")

                CodeMaster.insert(id=constants.REUSE_DRUG_STATUS_DRUG_REUSE_IN_PROGRESS_ID,
                                  group_id=constants.REUSE_DRUG_STATUS_GROUP_ID,
                                  value=constants.REUSE_DRUG_STATUS_DRUG_REUSE_IN_PROGRESS_DESC
                                  ).execute()

                print("Drug Reuse In Progress status added in code_master")

                CodeMaster.insert(id=constants.REUSE_DRUG_STATUS_DRUG_REUSE_DONE_ID,
                                  group_id=constants.REUSE_DRUG_STATUS_GROUP_ID,
                                  value=constants.REUSE_DRUG_STATUS_DRUG_REUSE_DONE_DESC
                                  ).execute()

                print("Drug Reuse Done status added in code_master")

                CodeMaster.insert(id=constants.REUSE_DRUG_STATUS_DRUG_RTS_DONE_ID,
                                  group_id=constants.REUSE_DRUG_STATUS_GROUP_ID,
                                  value=constants.REUSE_DRUG_STATUS_DRUG_RTS_DONE_DESC
                                  ).execute()

                print("Reuse Drug RTS Done status added in code_master")

                CodeMaster.insert(id=constants.REUSE_DRUG_STATUS_DRUG_RESEALED_ID,
                                  group_id=constants.REUSE_DRUG_STATUS_GROUP_ID,
                                  value=constants.REUSE_DRUG_STATUS_DRUG_RESEALED_DESC
                                  ).execute()

                print("Reuse Drug Resealed status added in code_master")

                CodeMaster.insert(id=constants.REUSE_DRUG_STATUS_DRUG_DISCARDED_ID,
                                  group_id=constants.REUSE_DRUG_STATUS_GROUP_ID,
                                  value=constants.REUSE_DRUG_STATUS_DRUG_DISCARDED_DESC
                                  ).execute()

                print("Reuse Drug Discarded status added in code_master")

            if GroupMaster.table_exists():
                GroupMaster.insert(id=constants.PACK_DELIVERY_STATUS_GROUP_ID,
                                   name=constants.PACK_DELIVERY_STATUS_GROUP_DESC
                                   ).execute()

                print("PackDeliveryStatus group code added in group_master")

            if CodeMaster.table_exists():
                CodeMaster.insert(id=constants.PACK_DELIVERY_STATUS_INSIDE_PHARMACY_ID,
                                  group_id=constants.PACK_DELIVERY_STATUS_GROUP_ID,
                                  value=constants.PACK_DELIVERY_STATUS_INSIDE_PHARMACY_DESC
                                  ).execute()

                print("Ext Pack Inside the Pharmacy status added in code_master")

                CodeMaster.insert(id=constants.PACK_DELIVERY_STATUS_RETURN_FROM_THE_DELIVERY_ID,
                                  group_id=constants.PACK_DELIVERY_STATUS_GROUP_ID,
                                  value=constants.PACK_DELIVERY_STATUS_RETURN_FROM_THE_DELIVERY_DESC
                                  ).execute()

                print("Ext Pack Return From The Delivery status added in code_master")

                CodeMaster.insert(id=constants.EXT_PACK_STATUS_CODE_DELETED_RETURN_IN_PHARMACY_ID,
                                  group_id=constants.EXT_PACK_STATUS_GROUP_ID,
                                  value=constants.EXT_PACK_STATUS_CODE_DELETED_RETURN_IN_PHARMACY_DESC
                                  ).execute()

                print("Returned in Pharmacy status added in code_master")

                CodeMaster.insert(id=constants.PHARMACY_PACK_STATUS_RETURNED_IN_PHARMACY,
                                  group_id=constants.PHARMACY_PACK_STATUS_GROUP_ID,
                                  value="Returned in Pharmacy"
                                  ).execute()

                print("Returned in Pharmacy status for PharmacyPackStatus added in code_master")

    except Exception as e:
        settings.logger.error("Error in add_pack_usage_drug_usage_status_in_group_master_and_code_master: {}".format(e))
        raise e


if __name__ == "__main__":
    add_pack_usage_drug_usage_status_in_group_master_and_code_master()
