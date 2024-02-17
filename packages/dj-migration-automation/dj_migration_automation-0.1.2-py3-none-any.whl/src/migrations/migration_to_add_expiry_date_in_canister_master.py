from playhouse.shortcuts import case

import settings
from playhouse.migrate import *

from dosepack.utilities.utils import last_day_of_month
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src import constants
import datetime

from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_tracker import CanisterTracker


def add_expiry_date_column_in_canister_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            if CanisterMaster.table_exists():

                # _____________________1:insert expiry_date column________________________

                migrate(
                    migrator.add_column(CanisterMaster._meta.db_table,
                                        CanisterMaster.expiry_date.db_column,
                                        CanisterMaster.expiry_date)
                )
                print("Added expiry_date column in CanisterMaster")

                # _____________________2:insert data in expiry_date column________________________

                print("inserting expiry date in canister_master")

                status = [constants.USAGE_CONSIDERATION_IN_PROGRESS,
                          constants.USAGE_CONSIDERATION_PENDING]

                canister_expiry_date_dict = dict()

                query = CanisterMaster.select(CanisterMaster.id,
                                              CanisterTracker.expiration_date).dicts() \
                        .join(CanisterTracker, on=CanisterMaster.id == CanisterTracker.canister_id) \
                        .where(CanisterMaster.available_quantity != 0,
                               CanisterTracker.usage_consideration.in_(status)) \
                        .order_by(CanisterMaster.id, CanisterTracker.id)
                for data in query:
                    if not canister_expiry_date_dict.get(data["id"]):
                        if not data["expiration_date"]:
                            continue
                        expiry = data["expiration_date"].split("-")
                        expiry_month = int(expiry[0])
                        expiry_year = int(expiry[1])
                        expiry_date = last_day_of_month(datetime.date(expiry_year, expiry_month, 1))

                        canister_expiry_date_dict[data["id"]] = (data["id"], expiry_date)

                print(f"canister_expiry_date_dict: {canister_expiry_date_dict}")
                canister_expiry_date_case = case(CanisterMaster.id, list(canister_expiry_date_dict.values()))
                status = CanisterMaster.update(expiry_date=canister_expiry_date_case).where(CanisterMaster.id.in_(list(canister_expiry_date_dict.keys()))).execute()
                print(f"inserted expiry date in canister_master. status: {status}")

    except Exception as e:
        settings.logger.error("Error while adding column: expiry_date in CanisterMaster. e:  ", str(e))


if __name__ == "__main__":
    add_expiry_date_column_in_canister_master()