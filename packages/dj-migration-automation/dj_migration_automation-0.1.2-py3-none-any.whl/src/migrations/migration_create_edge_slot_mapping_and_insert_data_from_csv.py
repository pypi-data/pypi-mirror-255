import csv

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_edge_slot_mapping import EdgeSlotMapping


def create_edge_slot_mapping_table():

    try:

        init_db(db, 'database_migration')
        if EdgeSlotMapping.table_exists():
            db.drop_table(EdgeSlotMapping)
            print('Table(s) dropped: EdgeSlotMapping')

        if not EdgeSlotMapping.table_exists():
            db.create_tables([EdgeSlotMapping], safe=True)
            print('Table(s) created: EdgeSlotMapping')

    except Exception as e:
        print(f"Error in create_edge_slot_mapping_table: {e}")
        raise e


path_to_csv = "edgeslotmapping_new_7_4.csv"


def insert_data_in_edge_slot_mapping_from_csv():
    init_db(db, 'database_migration')

    try:
        with db.transaction():
            table_data = list(csv.DictReader(open(path_to_csv, "r")))
            for data in table_data:
                for k, v in data.items():
                    if v == 'NULL':
                        data[k] = None
            EdgeSlotMapping.insert_many(table_data).execute()
            print(f"data inserted in EdgeSlotMapping")

    except Exception as e:
        print(e)
        raise e

if __name__ == '__main__':

    create_edge_slot_mapping_table()
    insert_data_in_edge_slot_mapping_from_csv()




