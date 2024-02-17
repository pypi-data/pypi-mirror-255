from dosepack.base_model.base_model import db
from src.model.model_file_header import FileHeader


def populate_file_data(old_database, new_database):
    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    cursor = db.execute_sql('select * from file_header;')
    template_data = []
    for row in cursor.fetchall():
        id = row[0]
        robot_id = row[1]
        system_id = 1   # system_id required in new database
        filename = row[2]
        filepath = row[3]
        _status = int(row[4])
        message = row[5]
        created_date = row[8]
        modified_date = row[9]
        if _status == 1:
            status = 11
        elif _status == 2:
            status = 12
        elif _status == 3:
            status = 14
        template_data.append({"id": id, "system_id": 1, "filename": filename, "filepath": filepath,
                              "message": message, "status": status, "created_by": 1, "modified_by": 1,
                              "pharmacy_software_id": 1, "created_date": created_date, "modified_date": modified_date})

    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    # counter = 0

    with db.transaction():
        with db.atomic():
            for idx in range(0, len(template_data), 1000):
                try:
                    FileHeader.insert_many(template_data[idx:idx+1000]).execute()
                    # counter += 1
                    # if counter == 1000:
                    #     print('.', end="", flush=True)
                    #     counter = 0
                except Exception as e:
                    print('-', end="", flush=True)
                    pass
