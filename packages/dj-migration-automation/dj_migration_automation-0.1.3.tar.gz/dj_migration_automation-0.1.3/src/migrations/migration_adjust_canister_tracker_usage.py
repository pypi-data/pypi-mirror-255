
from typing import List

from peewee import fn, PrimaryKeyField, ForeignKeyField, SmallIntegerField, CharField, IntegerField, DateTimeField

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants
from src.constants import USAGE_CONSIDERATION_DONE
from src.model.model_canister_master import CanisterMaster
from src.model.model_code_master import CodeMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_drug_master import DrugMaster

QUANTITY_ADJUSTED_LABEL = "quantity_adjusted"
ORIGINAL_QUANTITY_LABEL = "original_quantity"
NOTE_LABEL = "note"
NOTE_DESCRIPTION = "Stock Adjustment"
CANISTER_TRACKER_ID_LABEL = "id"


class CanisterTracker(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster, related_name="canister_id_1")
    device_id = ForeignKeyField(DeviceMaster, null=True, related_name="device_id_1")  # device from where replenish done
    drug_id = ForeignKeyField(DrugMaster, related_name="drug_id_1")
    qty_update_type_id = ForeignKeyField(CodeMaster, null=True, related_name="qty_update_type_id_1")  # Whether canister is replenished or adjusted
    quantity_adjusted = SmallIntegerField()
    original_quantity = SmallIntegerField()
    lot_number = CharField(max_length=30, null=True)
    expiration_date = CharField(max_length=8, null=True)
    note = CharField(null=True, max_length=100)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    voice_notification_uuid = CharField(null=True)
    drug_scan_type_id = ForeignKeyField(CodeMaster, null=True, related_name="drug_bottle_scan_id_1")
    replenish_mode_id = ForeignKeyField(CodeMaster, null=True, related_name="replenish_mode_id_1")
    usage_consideration = ForeignKeyField(CodeMaster, related_name="uc_code_id_id_1", default=constants.USAGE_CONSIDERATION_PENDING)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tracker"


def migration_adjust_canister_tracker_usage():
    init_db(db, 'database_migration')

    # Get the list of canisters that exists among CanisterTracker and CanisterMaster
    #     canister_list = [123, 456, 789...]

    #     Get the records from canister tracker in descending order of replenish (sum of original qty and qty adjusted)
    #     Eg:  Canister ID = 123 --> Available qty = 250
    #       13  Replenish-2 --> 5       200
    #       12  Replenish-1 --> 5       120
    #       11  Replenish-0 --> 10      100

    #       Output:
    #       13  Replenish-2 --> 5       200 == 200                  --> Usage consideration = Pending
    #       NEW Replenish-1 --> 200     50  == 250 (200 + 50)       --> Usage consideration = Pending --> New entry
    #       12  Replenish-1 --> 5       70                          --> Modify --> Update usage consideration = Done
    #       11  Replenish-0 --> 10      100                         --> Unused --> Update usage consideration = Done

    # Value of 200 is set as Available Qty in the above case by
    # calculating Canister Available Qty - Qty Adjusted for New Entry

    canister_tracker_ids_list: List[int] = []
    canister_tracker_update_dict = dict()
    canister_tracker_insert_dict = dict()
    canister_tracker_adjustment_update_list = []
    canister_tracker_adjustment_insert_list = []
    insert_response: int = 0
    update_response: int = 0

    try:

        # Get the List of Canisters along with their Available Qty and Canister Tracker details
        for record in CanisterMaster.select(CanisterMaster.id.alias("canister_id"),
                                            CanisterMaster.available_quantity,
                                            fn.GROUP_CONCAT(CanisterTracker.id).coerce(False).alias("tracker_ids")
                                            ).dicts() \
                .join(CanisterTracker, on=CanisterMaster.id == CanisterTracker.canister_id) \
                .group_by(CanisterMaster.id):

            canister_original_qty = record["available_quantity"]
            canister_tracker_ids_list = list(map(lambda x: int(x), record["tracker_ids"].split(',')))

            canister_tracker_adjustment_update_list = []
            canister_tracker_adjustment_insert_list = []
            print("\n\nCanister ID: {}".format(record["canister_id"]))

            if canister_original_qty > 0:
                # Get the Canister Tracker Details per Canister to evaluate the adjustment of Canister Available Qty
                for canister_tracker in CanisterTracker.select(CanisterTracker.id, CanisterTracker.canister_id,
                                                               CanisterTracker.device_id, CanisterTracker.drug_id,
                                                               CanisterTracker.qty_update_type_id,
                                                               CanisterTracker.quantity_adjusted,
                                                               CanisterTracker.original_quantity,
                                                               CanisterTracker.lot_number, CanisterTracker.expiration_date,
                                                               CanisterTracker.note, CanisterTracker.created_by,
                                                               CanisterTracker.drug_scan_type_id,
                                                               CanisterTracker.replenish_mode_id)\
                        .dicts() \
                        .where(CanisterTracker.canister_id == record["canister_id"]) \
                        .order_by(CanisterTracker.id.desc()):

                    canister_tracker_update_dict = {}
                    canister_tracker_insert_dict = {}
                    canister_tracker_id = canister_tracker[CANISTER_TRACKER_ID_LABEL]

                    if canister_original_qty >= canister_tracker[QUANTITY_ADJUSTED_LABEL]:
                        canister_tracker_ids_list.remove(canister_tracker[CANISTER_TRACKER_ID_LABEL])
                        canister_original_qty -= canister_tracker[QUANTITY_ADJUSTED_LABEL]

                        # If the Canister Tracker entry matches with the Canister Available Qty then no need for
                        # Stock Adjustment
                        if canister_original_qty == 0:
                            break
                    else:

                        # ----- Update existing Canister Tracker details with Quantity Adjusted and Usage Status as Done
                        canister_qty_adjustment = canister_tracker[QUANTITY_ADJUSTED_LABEL] - canister_original_qty
                        canister_tracker_update_dict.update({QUANTITY_ADJUSTED_LABEL: canister_qty_adjustment,
                                                             NOTE_LABEL: NOTE_DESCRIPTION})
                        update_response = CanisterTracker.update(**canister_tracker_update_dict)\
                            .where(CanisterTracker.id == canister_tracker[CANISTER_TRACKER_ID_LABEL]).execute()

                        # ------ Insert the adjustment entry in Canister Tracker that will have Usage Status as Pending
                        canister_tracker[QUANTITY_ADJUSTED_LABEL] = canister_original_qty
                        canister_tracker[ORIGINAL_QUANTITY_LABEL] = record["available_quantity"] - canister_original_qty
                        canister_tracker.pop(CANISTER_TRACKER_ID_LABEL)

                        if canister_tracker[NOTE_LABEL]:
                            canister_tracker[NOTE_LABEL] = canister_tracker[NOTE_LABEL] + " -- " + NOTE_DESCRIPTION
                        else:
                            canister_tracker[NOTE_LABEL] = NOTE_DESCRIPTION

                        canister_tracker_insert_dict.update(canister_tracker)

                        # CODE IS COMMENTED BECAUSE WE NEED TO PERFORM INSERT ONLY ONCE AT THE BOTTOM
                        # insert_response = CanisterTracker.insert(**canister_tracker_insert_dict).execute()
                        # insert_response = CanisterTracker.insert_many([canister_tracker_insert_dict]).execute()
                        # insert_response = BaseModel.db_create_multi_record([canister_tracker_insert_dict],
                        #                                                    CanisterTracker)
                        # insert_response = CanisterTracker.create(**canister_tracker_insert_dict).execute()

                        # ------- Only for documentation purpose
                        canister_tracker_update_dict.update({CANISTER_TRACKER_ID_LABEL: canister_tracker_id})
                        canister_tracker_adjustment_update_list.append(canister_tracker_update_dict)
                        canister_tracker_adjustment_insert_list.append(canister_tracker_insert_dict)

                        # Move out of the loop once adjustment is done. No need to check for any further entries in
                        # Canister Tracker table.
                        break

            print("Update List: {}".format(canister_tracker_adjustment_update_list))
            print("Insert List: {}".format(canister_tracker_adjustment_insert_list))
            print("Canister Tracker List that is used: {}".format(canister_tracker_ids_list))

            if canister_tracker_adjustment_insert_list:
                insert_response = CanisterTracker.insert_many(canister_tracker_adjustment_insert_list).execute()

            # Update Canister Tracker -- Usage consideration
            if canister_tracker_ids_list:
                update_response = CanisterTracker.update(usage_consideration=USAGE_CONSIDERATION_DONE) \
                    .where(CanisterTracker.id << canister_tracker_ids_list).execute()

        print("Execution successful..")
    except Exception as e:
        print("Exception encountered: {}".format(e))
        print("Insert Response: {}".format(insert_response))
        print("Update Response: {}".format(update_response))
        print("Execution Failed for Canister Tracker Usage Consideration Update...")


if __name__ == "__main__":
    migration_adjust_canister_tracker_usage()
