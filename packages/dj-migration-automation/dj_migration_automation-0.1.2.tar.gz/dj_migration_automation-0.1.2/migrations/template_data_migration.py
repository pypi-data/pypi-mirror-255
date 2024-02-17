from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from src.model.model_patient_rx import PatientRx
from src.model.model_patient_master import PatientMaster
from model.model_template import TemplateDetails


def template_data_migration(old_database, new_database):
    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    cursor = db.execute_sql('select * from template_master;')
    template_data = []
    for row in cursor.fetchall():
        patient_no = row[2]
        pharmacy_rx_no = row[1]
        hoa_time = row[4]
        column_number = row[5]
        quantity = row[6]
        template_data.append({"patient_id": patient_no, "patient_rx_id": pharmacy_rx_no, "column_number": column_number,
                              "hoa_time": hoa_time, "quantity": quantity, "created_by": 1, "modified_by": 1})

    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    count = 0
    template_data_list = []
    patient_id_dict = {}
    patient_rx_dict = {}

    for item1 in PatientMaster.select(PatientMaster.id, PatientMaster.patient_no).dicts():
        patient_id_dict[item1["patient_no"]] = item1["id"]

    for item2 in PatientRx.select(PatientRx.id, PatientRx.pharmacy_rx_no).dicts():
        patient_rx_dict[item2["pharmacy_rx_no"]] = item2["id"]
    with db.transaction():
        for record in template_data:
            try:
                record["patient_id"] = patient_id_dict[record["patient_id"]]
                record["patient_rx_id"] = patient_rx_dict[str(record["patient_rx_id"])]
                template_data_list.append(record)
                count += 1
                if count == 100:
                    print('.', end="", flush=True)
                    count = 0
                    BaseModel.db_create_multi_record(template_data_list, TemplateDetails)
                    template_data_list = []
            except Exception as e:
                pass

        if template_data_list:
            BaseModel.db_create_multi_record(template_data_list, TemplateDetails)





