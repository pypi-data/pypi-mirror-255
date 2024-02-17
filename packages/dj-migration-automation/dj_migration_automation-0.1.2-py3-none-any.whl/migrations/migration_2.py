import json
import base64
from dosepack.base_model.base_model import db
from model.model_drug import ImportedDrug
from src.model.model_imported_drug_image import ImportedDrugImage


def migrate_2():

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
        db.create_tables([ImportedDrug, ImportedDrugImage], safe=True)
        print('Table(s) Created: ImportedDrug, ImportedDrugImage')