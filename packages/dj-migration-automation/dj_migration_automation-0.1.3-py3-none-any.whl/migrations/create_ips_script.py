from dosepack.base_model.base_model import db
import shutil
import os


def create_ips_script(old_db):
    try:
        db.init(old_db, user="root".encode('utf-8'), password="root".encode('utf-8'))
        db.connect()

        cursor = db.execute_sql('select pack_display_id from pack_header;')
        pack_ids = []
        for row in cursor.fetchall():
            pack_ids.append(str(row[0]))

        pack_ids = ','.join(pack_ids)

        script_data = "pfh.tran_id in (" + pack_ids + ")"

        with open(os.path.join('migrations', 'ips-data-migration-script'), 'r') as _file:
            data = _file.read()

        data += script_data
        with open(os.path.join('migrations', 'ips-data-script'), 'w') as _file:
            _file.write(data)

        return True, data

    except Exception as e:
        print(e)
        return False

