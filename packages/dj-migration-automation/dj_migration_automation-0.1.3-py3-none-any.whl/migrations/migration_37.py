from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db

class PVSSlotDetails(BaseModel):  # entry for every pill dropped
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot_details'


class PVSCropDimension(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_details_id = ForeignKeyField(PVSSlotDetails)
    length = DecimalField(decimal_places=3, max_digits=6)  # in mm
    width = DecimalField(decimal_places=3, max_digits=6)  # in mm
    depth = DecimalField(decimal_places=3, max_digits=6, null=True)  # in mm
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_crop_dimension'


def migrate_37():
    init_db(db, 'database_migration')

    db.create_tables([PVSCropDimension], safe=True)
    print('table created: PVSCropDimension')
