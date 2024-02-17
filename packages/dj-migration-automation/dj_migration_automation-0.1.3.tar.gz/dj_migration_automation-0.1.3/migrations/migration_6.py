import json
import base64
from dosepack.base_model.base_model import db, BaseModel
from src.model.model_drug_master import DrugMaster
from playhouse.migrate import *
import settings


class PackDetails(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class PackError(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    drug_id = ForeignKeyField(DrugMaster, null=True)  # null to handle errors not related to drug
    quantity = DecimalField(decimal_places=2, max_digits=4, null=True)  # qty of extra drug found
    note = CharField(max_length=1000, null=True)  # Note provided by user
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_error"


def migrate_6():

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
        db.create_tables([PackError])
        print("Tables(s) Created: PackError")