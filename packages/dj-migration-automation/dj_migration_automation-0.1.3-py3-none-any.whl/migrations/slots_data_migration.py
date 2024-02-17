from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from src.model.model_drug_master import DrugMaster
from src.model.model_slot_details import SlotDetails
from src.model.model_slot_header import SlotHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_patient_rx import PatientRx
from collections import defaultdict


def populate_slot_data(old_database, new_database):
    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    cursor = db.execute_sql('select rx_no, pack_id_id, admin_date, admin_time, slot_row, slot_column, quantity, \
                                canister_number,ndc from slot_details;')
    pack_data = []
    drug_dict = {}
    for row in cursor.fetchall():
        pharmacy_rx_no = row[0]
        pack_id = row[1]
        hoa_date = row[2]
        hoa_time = row[3]
        slot_row = row[4]
        slot_column = row[5]
        quantity = row[6]
        canister_number = row[7]
        ndc = row[8]
        pack_data.append(
            {"pack_id": pack_id, "pharmacy_rx_no": pharmacy_rx_no, "hoa_date": hoa_date, "hoa_time": hoa_time,
             "slot_row": slot_row, "slot_column": slot_column, "quantity": quantity,
             "canister_number": canister_number, "ndc": ndc})

    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    slot_details_data = []
    counter = 0
    patient_rx_dict = defaultdict(dict)
    for item2 in PatientRx.select(PatientRx.id, PatientRx.pharmacy_rx_no, PatientRx.drug_id).dicts():
        patient_rx_dict[item2["pharmacy_rx_no"]][item2["drug_id"]] = item2["id"]

    for item in DrugMaster.select(DrugMaster.id, DrugMaster.ndc).dicts():
        drug_dict[item["ndc"]] = item["id"]

    saved_records = set()
    saved_rx_set = {}
    saved_drug_ids = set()
    with db.atomic():
        for record in pack_data:
            try:
                # print("record is ", record)
                drug_id = drug_dict[record["ndc"]]
                # print("drug_id is ", drug_id)
                try:
                    patient_rx_id = patient_rx_dict[str(record["pharmacy_rx_no"])][drug_id]
                    # print("patient_rx_id is ", patient_rx_id)
                except KeyError:
                    patient_rx_id = 1
                    saved_records.add(record["pack_id"])
                    saved_drug_ids.add(drug_id)
                    saved_rx_set[record["pharmacy_rx_no"]] = record["ndc"]

                pack_rx_link = {"patient_rx_id": patient_rx_id, "pack_id": record["pack_id"]}
                pack_rx_id = PackRxLink.get_or_create(**pack_rx_link)[0].id
                slot_header_data = {"pack_id": record["pack_id"], "hoa_date": record["hoa_date"],
                                    "hoa_time": record["hoa_time"],
                                    "slot_row": record["slot_row"], "slot_column": record["slot_column"]}
                slot_header_link = SlotHeader.get_or_create(**slot_header_data)[0].id
                is_manual = True
                if record["canister_number"] > 0:
                    is_manual = False
                slot_data = {"slot_id": slot_header_link, "pack_rx_id": pack_rx_id, "quantity": record["quantity"],
                             "is_manual": is_manual}
                slot_details_data.append(slot_data)
                counter += 1
                # print("Counter is", counter)
                if counter == 10000:
                    print('.', counter, end="", flush=True)
                    counter = 0
                    BaseModel.db_create_multi_record(slot_details_data, SlotDetails)
                    db.commit()
                    slot_details_data = []
            except Exception as e:
                # print("drug ids", saved_drug_ids)
                # print("pack ids", saved_records)
                # print("rx set", saved_rx_set)
                saved_records = set()
                saved_rx_set = {}
                saved_drug_ids = set()

        if slot_details_data:
            print(BaseModel.db_create_multi_record(slot_details_data, SlotDetails))
    print("Total slot details in old db", len(pack_data))
