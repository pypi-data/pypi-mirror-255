import json
import base64
from dosepack.base_model.base_model import db, BaseModel

from playhouse.migrate import *
import settings


class PackDetails(BaseModel):
    id = PrimaryKeyField()
    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"

class FillProductivity(BaseModel):
    id = PrimaryKeyField()
    session_id = IntegerField()
    system_id = IntegerField()
    total_time = IntegerField(null=True)  # in seconds
    user_station_time = IntegerField(null=True)  # in seconds
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        db_table = "fill_productivity"


class FilledPack(BaseModel):
    id = PrimaryKeyField()
    productivity_id = ForeignKeyField(FillProductivity)
    pack_id = ForeignKeyField(PackDetails)
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        db_table = "filled_pack"


def migrate_11():
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

    with db.transaction():
        db.create_tables([FillProductivity, FilledPack], safe=True)
        # db.create_tables([FilledPack])
        print('Table(s) Created: FillProductivity, FilledPack')