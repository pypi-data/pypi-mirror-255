from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from playhouse.migrate import *
import settings
from src.model.model_file_header import FileHeader


class ExtHoldRx(BaseModel):
    # rx that are on hold in IPS due to some reasons will be stored here
    id = PrimaryKeyField()
    file_id = ForeignKeyField(FileHeader)
    ext_pharmacy_rx_no = FixedCharField(max_length=20)
    ext_note = CharField(null=True, max_length=100)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ext_hold_rx"


def migration_ext_hold_rx():
    init_db(db, 'database_migration')
    db.create_tables([ExtHoldRx], safe=True)
    print('Table(s) created: ExtHoldRx')
