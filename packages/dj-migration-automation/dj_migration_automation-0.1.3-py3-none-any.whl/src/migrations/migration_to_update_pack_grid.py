import csv

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_pack_grid import PackGrid


path_to_csv = "pack_grid_new_7_4.csv"


def update_data_in_pack_grid_from_csv():
    init_db(db, 'database_migration')

    try:
        with db.transaction():
            db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
            if PackGrid.table_exists():
                db.truncate_table(PackGrid)

            if not PackGrid.table_exists():
                db.create_tables([PackGrid], safe=True)
                print('Table(s) created: PackGrid')

            table_data = list(csv.DictReader(open(path_to_csv, "r")))
            for data in table_data:
                for k, v in data.items():
                    if v == 'NULL':
                        data[k] = None
            PackGrid.insert_many(table_data).execute()

            db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
            print(f"data inserted in PackGrid")

    except Exception as e:
        print(e)
        raise e


if __name__ == '__main__':

    update_data_in_pack_grid_from_csv()




