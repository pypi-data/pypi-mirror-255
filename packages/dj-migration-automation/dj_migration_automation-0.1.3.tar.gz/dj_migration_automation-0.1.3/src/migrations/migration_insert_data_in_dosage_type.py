import logging

from dosepack.base_model.base_model import db
from src.model.model_dosage_type import DosageType
from model.model_init import init_db

logger = logging.getLogger("root")


def insert_data_in_dosage_type():
    try:
        with db.transaction():
            init_db(db, 'database_migration')
            db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
            if DosageType.table_exists():
                db.truncate_table(DosageType)
                print("truncated table dosage type")

                DosageType.insert(id=1, code="NML", name="Normal").execute()
                DosageType.insert(id=2, code="CTB", name="Chewable Tablet").execute()
                DosageType.insert(id=3, code="ODT", name="Orally Disintegrating Tablet").execute()
                DosageType.insert(id=4, code="SGL", name="Softgel").execute()
                db.execute_sql("SET FOREIGN_KEY_CHECKS=1")
                print("data inserted in dosage type")
    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    insert_data_in_dosage_type()