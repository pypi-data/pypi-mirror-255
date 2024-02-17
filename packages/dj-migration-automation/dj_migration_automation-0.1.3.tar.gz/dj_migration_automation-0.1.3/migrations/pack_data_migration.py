from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from model.model_pack import PackHeader
from src.model.model_pack_details import PackDetails
from src.model.model_patient_master import PatientMaster


def pack_data_migration(old_database, new_database):
    PACK_STATUS = {'pending': 2, 'progress': 3, 'done': 5, 'verified': 6, 'deleted': 7, 'manual': 8, 'C': 21,
                   "dispense pending": 23, "dropped": 24, 'invalid': 9}

    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    cursor = db.execute_sql('select pack_id, pack_display_id, rfid, pack_no, pack_status, pack_plate_location,\
                            filecheck_id, patient_checked_id, association_status, pack_header.created_date,\
                            pack_header.modified_date,file_id_id from pack_header \
                            join patient_master on pack_header.patient_id_id=patient_master.patient_id \
                            order by pack_id;')
    pack_data = []

    for row in cursor.fetchall():
        pack_id = row[0]
        pack_display_id = row[1]
        rfid = row[2]
        pack_no = row[3]
        pack_status = PACK_STATUS[row[4]]
        pack_plate_location = row[5]
        fill_id = row[6]
        patient_id = row[7]
        association_status = row[8]
        created_date = row[9]
        modified_date = row[10]
        file_id = row[11]

        pack_data.append({"pack_id": pack_id, "pack_display_id": pack_display_id, "rfid": rfid,
                          "pack_no": pack_no, "pack_status": pack_status, "pack_plate_location": pack_plate_location,
                          "fill_id": fill_id,
                          "patient_id": patient_id, "created_date": created_date, "modified_date": modified_date,
                          "association_status": association_status, "file_id": file_id})
    print('Pack Data from old db fetched')
    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    # counter = 0

    with db.transaction():
        print('Pack Data insertion for new db started')
        pack_list = []
        patient_id_dict = {}
        for item1 in PatientMaster.select(PatientMaster.id, PatientMaster.patient_name,
                                          PatientMaster.patient_no).dicts():
            patient_id_dict[item1["patient_no"]] = item1["id"]

        pack_set = set()
        new_pack_data = []  # for storing records from pack_data
        db.execute_sql("set foreign_key_checks=0;")
        db.execute_sql("delete from packheader;")
        db.execute_sql("delete from packdetails;")
        for record in pack_data:
            try:
                try:
                    record["patient_id"] = patient_id_dict[record["patient_id"]]
                except KeyError:
                    record["patient_id"] = 1

                pack_header_record = {"patient_id": record["patient_id"], "total_packs": 4, "start_day": 0,
                                      "pharmacy_fill_id": record["fill_id"], "created_date": record["created_date"],
                                      "modified_date": record["modified_date"], "created_by": 1, "modified_by": 1,
                                      "file_id": record["file_id"]}

                pack_header_id = PackHeader.get_or_create(**pack_header_record)[0].id

                if not record["pack_plate_location"]:
                    record["pack_plate_location"] = None
                else:
                    record["pack_plate_location"] = record["pack_plate_location"].strip()[0]

                if record["pack_id"] not in pack_set:
                    pack_details_record = {"id": record["pack_id"], "pack_header_id": pack_header_id, "batch_id": 1,
                                           "pack_display_id": record["pack_display_id"],
                                           "pack_no": record["pack_no"], "filled_by": "berguiza", "filled_days": 7,
                                           "fill_start_date": "2016-01-01", "system_id": 1,
                                           "pack_plate_location": record["pack_plate_location"],
                                           "rfid": record["rfid"], "association_status": record["association_status"],
                                           "created_date": record["created_date"], "pack_status": record["pack_status"],
                                           "modified_date": record["modified_date"], "created_by": 1, "modified_by": 1,
                                           "delivery_schedule": "Cycle", "consumption_start_date": record["created_date"]
                                           }
                    pack_set.add(record["pack_id"])
                    new_pack_data.append(pack_details_record)
                    # PackDetails.create(**pack_details_record)
                    # counter += 1
                    # if counter == 1000:
                    # counter = 0
            except Exception as e:
                print(e)
        print('No of records to be inserted in packdetails', len(new_pack_data))
        with db.atomic():
            for idx in range(0, len(new_pack_data), 1000):
                try:
                    PackDetails.insert_many(new_pack_data[idx:idx + 1000]).execute()
                    print('.', end="", flush=True)
                except Exception as ex:
                    print('Exception in migrating pack data', str(ex))


def update_changed_pack(old_database, new_database):
    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    cursor = db.execute_sql(
        'select pack_id, pack_display_id, rfid, pack_no, pack_status, pack_plate_location, filecheck_id, patient_checked_id, association_status, pack_header.created_date, pack_header.modified_date,file_id_id from pack_header join patient_master on pack_header.patient_id_id=patient_master.patient_id order by pack_id;')
    pack_patient_dict = {}

    for row in cursor.fetchall():
        pack_display_id = row[1]
        patient_id = row[7]
        pack_patient_dict[pack_display_id] = patient_id

    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    patient_id_dict = {}
    for item1 in PatientMaster.select(PatientMaster.id, PatientMaster.patient_name, PatientMaster.patient_no).dicts():
        patient_id_dict[item1["patient_no"]] = item1["id"]

    for record in PackHeader.select(PackHeader.id, PackHeader.patient_id, PackHeader.pharmacy_fill_id).dicts().where(
                    PackHeader.patient_id == 1):
        pack_header_id = record["id"]
        try:
            patient_id = patient_id_dict[pack_patient_dict[record["pharmacy_fill_id"]]]
            status = PackHeader.update(patient_id=patient_id).where(PackHeader.id == pack_header_id).execute()
            print(status)
        except KeyError:
            print(record["pharmacy_fill_id"])
