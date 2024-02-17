from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src.model.model_ext_pack_details import ExtPackDetails
from dosepack.utilities.utils import get_current_date_time
import settings

def migrate_60(drop_tables=False):
    init_db(db, "database_migration")

    if drop_tables:
        db.drop_tables([ExtPackDetails])
    db.create_tables([ExtPackDetails], safe=True)
    print('Table(s) Created: ExtPackDetails')


if __name__ == '__main__':
    migrate_60(True)
