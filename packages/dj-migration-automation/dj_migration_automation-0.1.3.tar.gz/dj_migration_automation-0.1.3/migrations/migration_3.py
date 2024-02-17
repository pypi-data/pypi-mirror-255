import json
import base64
from dosepack.base_model.base_model import db, BaseModel
from playhouse.migrate import *


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    rfid = FixedCharField(null=True, max_length=20)

    class Meta():
        db_table = "canister_master"


def migrate_3():

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

    status1 = CanisterMaster.update(rfid=None).where(CanisterMaster.rfid == "rfid").execute()
    print("{} rows rfid update with NULL".format(status1))

    migrator = MySQLMigrator(db)
    if CanisterMaster.table_exists():
        migrate(migrator.add_index(CanisterMaster._meta.db_table, (CanisterMaster.rfid.db_column,), True),)
        print("Tables(s) Modified: CanisterMaster")
