from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings

class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"

class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"

class PackHeader(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_header"


class OldPackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)  # system_id from dpauth project System table
    pack_header_id = ForeignKeyField(PackHeader)
    batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    is_takeaway = BooleanField(default=False)
    pack_status = ForeignKeyField(CodeMaster)
    filled_by = FixedCharField(max_length=64)
    consumption_start_date = DateField()
    consumption_end_date = DateField()
    filled_days = SmallIntegerField()
    fill_start_date = DateField()
    delivery_schedule = FixedCharField(max_length=50)
    association_status = BooleanField(null=True)
    rfid = FixedCharField(null=True, max_length=20, unique=True)
    pack_plate_location = FixedCharField(max_length=2, null=True)
    order_no = IntegerField(null=True)
    filled_date = DateTimeField(null=True)
    filled_at = SmallIntegerField(null=True)
    fill_time = IntegerField(null=True, default=None)  # in seconds
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"




class PackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)  # system_id from dpauth project System table
    pack_header_id = ForeignKeyField(PackHeader)
    # batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    is_takeaway = BooleanField(default=False)
    pack_status = ForeignKeyField(CodeMaster)
    filled_by = FixedCharField(max_length=64)
    consumption_start_date = DateField()
    consumption_end_date = DateField()
    filled_days = SmallIntegerField()
    fill_start_date = DateField()
    delivery_schedule = FixedCharField(max_length=50)
    association_status = BooleanField(null=True)
    rfid = FixedCharField(null=True, max_length=20, unique=True)
    pack_plate_location = FixedCharField(max_length=2, null=True)
    order_no = IntegerField(null=True)
    filled_date = DateTimeField(null=True)
    filled_at = SmallIntegerField(null=True)
    # marked filled at which step
    # Any manual goes in 0-10, If filled by system should be > 10
    #  0 - Template(Auto marked manual for manual system),
    #  1 - Pack Pre-Processing/Facility Distribution, 2 - PackQueue, 3 - MVS
    #  11 - DosePacker
    fill_time = IntegerField(null=True, default=None)  # in seconds
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)
    unloading_time = DateTimeField(null= True)
    car_id = IntegerField(null= True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


def migrate_73():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if OldPackDetails.table_exists():
        migrate(
            migrator.add_column(
                PackDetails._meta.db_table,
                PackDetails.unloading_time.db_column,
                PackDetails.unloading_time
            ),
            migrator.add_column(
                PackDetails._meta.db_table,
                PackDetails.car_id.db_column,
                PackDetails.car_id
                )
        )
        print("Table Modified: PACK DETAILS, column unloading_time and car_id added")


if __name__ == "__main__":
    migrate_73()
