from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
from src.model.model_patient_master import PatientMaster
from playhouse.migrate import *
import settings


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class OldPackDetails(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField() #  system_id from dpauth project System table
    # pack_header_id = ForeignKeyField(PackHeader)
    # batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    is_takeaway = BooleanField(default=False)
    # pack_status = ForeignKeyField(CodeMaster, related_name="pack_details_pack_status")
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
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class PackDetails(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField() #  system_id from dpauth project System table
    # pack_header_id = ForeignKeyField(PackHeader)
    # batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    is_takeaway = BooleanField(default=False)
    pack_status = ForeignKeyField(CodeMaster, related_name="pack_details_pack_status")
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
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


def migrate_30():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if OldPackDetails.table_exists():
        migrate(
            migrator.add_column(
                PackDetails._meta.db_table,
                PackDetails.filled_date.db_column,
                PackDetails.filled_date
            )
        )
        PackDetails.update(filled_date=PackDetails.modified_date)\
            .where(PackDetails.pack_status << settings.PACK_FILLING_DONE_STATUS_LIST)\
            .execute()
        print("Table Modified: PackDetails")

if __name__ == "__main__":
    migrate_30()


