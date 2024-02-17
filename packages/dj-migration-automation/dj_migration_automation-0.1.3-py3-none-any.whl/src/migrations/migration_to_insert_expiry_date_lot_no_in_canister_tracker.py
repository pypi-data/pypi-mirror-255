from playhouse.shortcuts import case

import settings

from model.model_init import init_db
from dosepack.base_model.base_model import db
from src import constants

from src.model.model_canister_tracker import CanisterTracker


def insert_expiry_date_and_lot_no_for_discard_canister():
    init_db(db, 'database_migration')

    try:
        with db.transaction():

            canister_tracker_list = list()
            canister_dict = dict()
            canister_set = set()
            update_dict = dict()
            expiration_date_update_dict = dict()
            lot_number_update_dict = dict()
            query = CanisterTracker.select(CanisterTracker.id,
                                           CanisterTracker.canister_id).dicts() \
                    .where(CanisterTracker.usage_consideration == constants.USAGE_CONSIDERATION_DISCARD,
                           CanisterTracker.qty_update_type_id == constants.CANISTER_QUANTITY_UPDATE_TYPE_DISCARD) \
                    .order_by(CanisterTracker.id)
            for data in query:
                # canister_set.add(data["canister_id"])
                # canister_tracker_list.append({"id": data["id"], "canister_id": data["canister_id"]})
                if not canister_dict.get(data["canister_id"]):
                    canister_dict[data['canister_id']] = []
                canister_dict[data["canister_id"]].append({"id": data["id"], "canister_id": data["canister_id"]})

            for k, v in canister_dict.items():

                query = CanisterTracker.select(CanisterTracker.canister_id,
                                               CanisterTracker.expiration_date,
                                               CanisterTracker.lot_number,
                                               CanisterTracker.id).dicts() \
                        .where(CanisterTracker.canister_id == k,
                               CanisterTracker.usage_consideration == constants.USAGE_CONSIDERATION_DISCARD,
                               CanisterTracker.qty_update_type_id != constants.CANISTER_QUANTITY_UPDATE_TYPE_DISCARD) \
                        .order_by(CanisterTracker.id)
                previous_id = 0
                for data in query:
                    if v:
                        canister_tracker_id = v[0]["id"]
                        canister_tracker_canister = v[0]["canister_id"]

                        if data["id"] < canister_tracker_id and data[
                            "id"] > previous_id and canister_tracker_canister == data["canister_id"]:

                            update_dict[canister_tracker_id] = {"expiration_date": data["expiration_date"],
                                                                "lot_number": data["lot_number"]}
                            expiration_date_update_dict[canister_tracker_id] = (canister_tracker_id, data['expiration_date'])
                            lot_number_update_dict[canister_tracker_id] = (canister_tracker_id, data["lot_number"])
                            v.pop(0)
                            previous_id = canister_tracker_id

                print(update_dict)
            print(f"update_dict: {update_dict}")
            print(f"expiration_date_update_dict: {expiration_date_update_dict}")
            print(f"lot_number_update_dict: {lot_number_update_dict}")

            if expiration_date_update_dict and lot_number_update_dict:
                expiration_date_case = case(CanisterTracker.id, list(expiration_date_update_dict.values()))
                lot_number_case = case(CanisterTracker.id, list(lot_number_update_dict.values()))
                status = CanisterTracker.update(expiration_date=expiration_date_case,
                                                lot_number=lot_number_case)\
                                        .where(CanisterTracker.id.in_(list(update_dict.keys())))\
                                        .execute()
                print(f"status: {status}")

    except Exception as e:
        settings.logger.error("Error in insert_expiry_date_and_lot_no_in_tracker ", str(e))
        raise e


if __name__ == "__main__":
    insert_expiry_date_and_lot_no_for_discard_canister()