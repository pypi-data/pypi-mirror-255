from dosepack.base_model.base_model import db
from model.model_canister import CanisterMaster
from src.model.model_drug_master import DrugMaster


def populate_canister_data(old_database, new_database):
    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    cursor = db.execute_sql('select * from canister_master;')
    canister_data = []

    for row in cursor.fetchall():
        robot_id = row[1]
        drug_id = row[5]
        rfid = row[7]
        available_quantity = row[8]
        canister_number = row[9]
        active = row[10]
        reorder_quantity = row[11]
        barcode = row[12]
        created_date = row[15]
        modified_date = row[16]

        canister_data.append({"robot_id": robot_id, "drug_id": drug_id, "rfid": rfid,
                              "available_quantity": available_quantity, "canister_number": canister_number,
                              "active": active, "reorder_quantity": reorder_quantity,
                              "barcode": barcode, "created_date": created_date, "modified_date": modified_date,
                              "created_by": 1, "modified_by": 1})

    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    counter = 0
    for record in canister_data:
        try:
            record["drug_id"] = DrugMaster.get(ndc=record["drug_id"]).id
            CanisterMaster.get_or_create(**record)
            counter += 1
            if counter == 10:
                print('.', end="", flush=True)
                counter = 0
        except Exception as e:
            print('-', end="", flush=True)
            pass







