import os
import csv
import sqlanydb

from dosepack.base_model.base_model import db, BaseModel
from model.model_pack import ReasonCodeMaster, BatchMaster, PackRxLink, PackHeader, PackVerification, \
    SlotDetails, SlotHeader, SlotTransaction, TempSlotInfo, PatientRx, PackStatusTracker
from src.model.model_pack_details import PackDetails
from src.model.model_doctor_master import DoctorMaster
from src.model.model_patient_master import PatientMaster
from src.model.model_facility_master import FacilityMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_batch_master import BatchMaster

import sys
from collections import defaultdict


def facility_data_migration(old_database, new_database):
    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    # facility master data insertion
    with db.transaction():
        with open(os.path.join('migrations', 'facility-data.csv'), 'r') as _file:
            data = csv.reader(_file, delimiter='\t')
            data = list(data)
            # header = data.pop(0)
            # print("Header", header)
            for item in data:
                FacilityMaster.get_or_create(
                    **{"client_id": 1, "pharmacy_id": 1, "pharmacy_facility_id": item[0], "facility_name": item[1],
                       "created_by": 1, "modified_by": 1})
    return True


def patient_data_migration(old_database, new_database):
    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    facility_master_dict = {}
    for record in FacilityMaster.select(FacilityMaster.id, FacilityMaster.pharmacy_facility_id).dicts():
        facility_master_dict[record["pharmacy_facility_id"]] = record["id"]

    # facility master data insertion
    with db.transaction():
        patient_data_list = []
        with open(os.path.join('migrations', 'patient-data.csv'), 'r') as _file:
            data = csv.reader(_file, delimiter='\t')
            data = list(data)
            header = data.pop(0)
            # print("Header", header)
            for item in data:
                try:
                    if not item[11]:
                        item[11] = None
                except IndexError:
                    item[11] = None

                try:
                    allergy = item[12]
                except IndexError:
                    allergy = None

                if not item[0]:
                    item[0] = 1
                try:
                    facility_id = facility_master_dict[int(item[0])]
                except KeyError:
                    pass

                dict_patient_object = {"client_id": 1, "pharmacy_id": 1, "pharmacy_patient_id": item[3],
                                       "patient_name": item[1] + "," + item[2], "patient_picture": item[4],
                                       "address1": item[5], "zip_code": item[6], "city": item[7], "state": item[8],
                                       "workphone": item[10], "dob": item[11], "patient_no": item[9],
                                       "allergy": allergy,
                                       "facility_id": facility_id, "created_by": 1, "modified_by": 1}
                patient_data_list.append(dict_patient_object)
            db.execute_sql('delete from patientmaster;')
            BaseModel.db_create_multi_record(patient_data_list, PatientMaster)
    return True


def doctor_data_migration(old_database, new_database):
    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    # doctor master data insertion
    with db.transaction():
        doctor_data_list = []
        with open(os.path.join('migrations', 'doctor-data.csv'), 'r') as _file:
            data = csv.reader(_file, delimiter='\t')
            data = list(data)
            ids = set()
            for item in data:
                if not item:
                    continue
                if not item[0]:
                    item[0] = None
                if item[1] not in ids:
                    dict_doctor_object = {"client_id": 1, "pharmacy_id": 1, "pharmacy_doctor_id": item[1],
                                          "doctor_name": item[3] + "," + item[2],
                                          "workphone": item[0], "created_by": 1, "modified_by": 1}
                    doctor_data_list.append(dict_doctor_object)
                    ids.add(item[1])
                else:
                    print("Duplicate:", item[1])
            db.execute_sql('delete from doctormaster;')
            BaseModel.db_create_multi_record(doctor_data_list, DoctorMaster)
    return True


def rx_data_migration(old_database, new_database, script, ips_db, use_ips):
    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    drug_master_dict = dict()
    drug_master_set = set()
    for record in DrugMaster.select(DrugMaster.ndc, DrugMaster.id).dicts():
        drug_master_dict[record["ndc"]] = record["id"]
        drug_master_set.add(record["ndc"])

    doctor_master_dict = dict()
    for record in DoctorMaster.select(DoctorMaster.id, DoctorMaster.pharmacy_doctor_id).dicts():
        doctor_master_dict[record["pharmacy_doctor_id"]] = record["id"]

    # rx table master data insertion
    with db.transaction():
        counter = 0
        records_added = 0
        patient_rx_data = []
        if use_ips:
            try:
                conn = sqlanydb.connect(uid='dba', pwd='1m2p3k4n', eng=ips_db, dbn=ips_db)
                curs = conn.cursor()
                curs.execute(script)
                data = curs.fetchall()
            except Exception:
                print("Unable to connect to IPS Database. System Exiting...")
                sys.exit(1)
        else:
            with open(os.path.join('migrations', 'ips-data.csv'), 'r', newline='') as _file:
                data = _file.read()
                data = data.replace('\'', '')
                data = csv.reader(data.splitlines(), delimiter='\t', skipinitialspace=True)

        drug_set = set()

        for item in data:
            # print('*** Data from CSV ***', item)
            # doctor_id_set.add(int(item[1]))
            try:
                try:
                    doctor_id = doctor_master_dict[int(item[1])]
                    drug_id = drug_master_dict[item[10]]
                except KeyError:
                    drug_set.add(item[10])
                    raise KeyError("Invalid Doctor PharmacyId " + str(item[10]))

                patient_rx_fields = {"client_id": 1, "created_by": 1, "modified_by": 1, "drug_id": drug_id,
                                     "pharmacy_rx_no": item[9], "sig": item[2], "morning": int(float(item[3])),
                                     "noon": int(float(item[4])), 'evening': int(float(item[5])),
                                     'bed': int(float(item[6])), 'caution1': item[7], 'caution2': item[8],
                                     'remaining_refill': round(float(item[11]), 2), "doctor_id": doctor_id}

                patient_rx_data.append(patient_rx_fields)
                counter += 1
                if counter == 1000:
                    print('.', end="", flush=True)
                    records_added += counter
                    counter = 0
                    BaseModel.db_create_multi_record(patient_rx_data, PatientRx)
                    patient_rx_data = []

            except Exception as e:
                # print(e)
                # print('-', end="", flush=True)
                pass

        print('** Records added ****', records_added)
        if patient_rx_data:
            BaseModel.db_create_multi_record(patient_rx_data, PatientRx)

    print('** set operation **', counter, len(drug_set), len(drug_master_set),(drug_set - drug_master_set))

    return True


def populate_orphan_rx_nos(old_database, new_database):
    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    rx_list = []
    cursor = db.execute_sql('select distinct rx_no, ndc from slot_details;')
    for row in cursor.fetchall():
        pharmacy_rx_no = row[0]
        ndc = row[1]
        rx_list.append((str(pharmacy_rx_no), ndc))

    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    drug_master_dict = {}
    for record in DrugMaster.select(DrugMaster.ndc, DrugMaster.id).dicts():
        drug_master_dict[record["ndc"]] = record["id"]

    rx_drug_dict = defaultdict(dict)
    rx_dict = {}
    for record in PatientRx.select().dicts():
        rx_drug_dict[record["pharmacy_rx_no"]][record["drug_id"]] = 1
        rx_dict[record["pharmacy_rx_no"]] = record

    counter = 0
    patient_rx_data = []
    _doctor_id = DoctorMaster.get(pharmacy_doctor_id=16).id
    for item in rx_list:
        try:
            drug_id = drug_master_dict[item[1]]
        except KeyError:
            continue

        try:
            data = rx_drug_dict[item[0]][item[1]]
            if not data:
                raise KeyError
        except KeyError:
            try:
                rx_data = rx_dict[item[0]]
            except KeyError:
                rx_data = {"sig": "invalid", "morning": 1.0, "noon": 0, "evening": 0, "bed": 0, "caution1": "invalid",
                           "caution2": "invalid", "doctor_id": _doctor_id, "remaining_refill": 0.0}

            patient_rx_fields = {"client_id": 1, "created_by": 1, "modified_by": 1, "drug_id": drug_id,
                                 "pharmacy_rx_no": item[0], "sig": rx_data["sig"], "morning": rx_data["morning"],
                                 "noon": rx_data["noon"], 'evening': rx_data["evening"],
                                 'bed': rx_data["bed"], 'caution1': rx_data["caution1"],
                                 'caution2': rx_data["caution2"],
                                 'remaining_refill': rx_data["remaining_refill"], "doctor_id": rx_data["doctor_id"]}

            patient_rx_data.append(patient_rx_fields)
            counter += 1
            if counter == 500:
                print('.', end="", flush=True)
                counter = 0
                try:
                    BaseModel.db_create_multi_record(patient_rx_data, PatientRx)
                except Exception as e:
                    print(e)
                patient_rx_data = []

    if patient_rx_data:
        BaseModel.db_create_multi_record(patient_rx_data, PatientRx)


def pack_meta_info_migration(old_database, new_database, script, ips_db, use_ips):
    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    # pack details data insertion
    with db.transaction():
        if use_ips:
            try:
                conn = sqlanydb.connect(uid='dba', pwd='1m2p3k4n', eng=ips_db, dbn=ips_db)
                curs = conn.cursor()
                curs.execute(script)
                data = curs.fetchall()
            except Exception:
                print("Unable to connect to IPS Database. System Exiting...")
                sys.exit(1)
        else:
            with open(os.path.join('migrations', 'ips-data.csv'), 'r', newline='') as _file:
                data = _file.read()
                data = data.replace('\'', '')
                data = csv.reader(data.splitlines(), delimiter='\t', skipinitialspace=True)

        pack_ids_set = set()
        for item in data:
            try:
                pack_id = item[12]
                fill_start_date = item[13]
                delivery_schedule = item[14]
                filled_by = item[15]
                if pack_id not in pack_ids_set:
                    status = PackDetails.update(fill_start_date=fill_start_date, delivery_schedule=delivery_schedule,
                                                filled_by=filled_by).where(
                        PackDetails.pack_display_id == int(pack_id)).execute()
                    pack_ids_set.add(pack_id)
                print('.',end="", flush=True)
            except Exception as e:
                print(e)
                print('-', end="", flush=True)
                pass
    return True
