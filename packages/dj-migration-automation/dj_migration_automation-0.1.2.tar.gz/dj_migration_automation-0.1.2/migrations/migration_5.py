import json
import base64
from dosepack.base_model.base_model import db
from src.model.model_group_master import GroupMaster
from src.model.model_reason_master import ReasonMaster
from model.model_pack import PackFillError, PackFillErrorDetails
from playhouse.migrate import *

from src.model.model_slot_transaction import SlotTransaction


def migrate_5():

    json_file = open('config.json', "r")
    data = json.load(json_file)
    json_file.close()

    # Here database_migration is the key for the db engine present in
    # config.json file

    try:
        database = data["database_migration"]["db"]
        username = base64.b64decode(data["database_migration"]["user"])
        password = base64.b64decode(data["database_migration"]["passwd"])
        host = data["database_migration"]["host"]
        port = 3306
    except Exception as ex:
        raise Exception("Incorrect Value for db engine")

    db.init(database, user=username, password=password, host=host, port=port)

    migrator = MySQLMigrator(db)
    with db.transaction():
        fill_reason_group = GroupMaster.create(**{'id': 6, 'name': 'PackFillReason'})
        if not ReasonMaster.table_exists():
            db.create_tables([ReasonMaster])
            print("Tables(s) Created: ReasonMaster")
            ReasonMaster.create(**{'id': 1, 'reason_group': fill_reason_group, 'reason': 'Broken Pill'})
            ReasonMaster.create(**{'id': 2, 'reason_group': fill_reason_group, 'reason': 'Extra Pill Count'})
            ReasonMaster.create(**{'id': 3, 'reason_group': fill_reason_group, 'reason': 'Missing Pill'})
            ReasonMaster.create(**{'id': 4, 'reason_group': fill_reason_group, 'reason': 'Pill Misplaced'})
            print("Tables(s) Modified: ReasonMaster")
        if not PackFillError.table_exists() and not PackFillErrorDetails.table_exists():
            db.create_tables([PackFillError, PackFillErrorDetails])
            print("Tables(s) Created: PackFillError, PackFillErrorDetails")
        if SlotTransaction.table_exists():
            migrate(migrator.add_column(SlotTransaction._meta.db_table, SlotTransaction.canister_number.db_column, SlotTransaction.canister_number))
            print("Tables(s) Modified: SlotTransaction")
