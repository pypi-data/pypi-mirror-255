from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings
from model.model_pill_vision import PvsSlotImageDimension


def migrate_65(drop_tables=False):
    init_db(db, "database_migration")
    if drop_tables:
        print("dropping tables")
        db.drop_tables([PvsSlotImageDimension])
    
    print("creating table PvsSlotImageDimension")
    db.create_tables([PvsSlotImageDimension], safe=True)
    print('Table(s) Created: PvsSlotImageDimension')
    insert_in_table()


def insert_in_table():
    try:
        row_data = [
            {
                "company_id": 3,
                "robot_id": 2,
                "quadrant": 0,
                "left_value": 280,
                "right_value": 280 + 720
            },
            {
                "company_id": 3,
                "robot_id": 3,
                "quadrant": 0,
                "left_value": 347,
                "right_value": 347 + 720,
            },
        ]

        PvsSlotImageDimension.insert_many(row_data).execute()
        print('PvsSlotImageDimension initial data inserted')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    migrate_65(drop_tables=False)
