from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings
from src.model.model_pack_details import PackDetails
from src.model.model_drug_master import DrugMaster
from src.model.model_doctor_master import DoctorMaster
from src.model.model_patient_master import PatientMaster


class PatientRx(BaseModel):
    id = PrimaryKeyField()
    # patient_id = ForeignKeyField(PatientMaster)
    # drug_id = ForeignKeyField(DrugMaster)
    # doctor_id = ForeignKeyField(DoctorMaster)
    pharmacy_rx_no = FixedCharField(max_length=20)
    sig = CharField(max_length=1000)
    morning = FloatField(null=True)
    noon = FloatField(null=True)
    evening = FloatField(null=True)
    bed = FloatField(null=True)
    caution1 = CharField(null=True, max_length=300)
    caution2 = CharField(null=True, max_length=300)
    remaining_refill = DecimalField(decimal_places=2, max_digits=5)
    is_tapered = BooleanField(null=True)
    daw_code = SmallIntegerField(default=0)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_rx"

class PackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)  # system_id from dpauth project System table
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

    FILLED_AT_MAP = {
        0: 'Auto',
        1: 'Pre-Import',
        2: 'Post-Import',
        3: 'Manual Verification Station',
        11: 'DosePacker'
    }

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"

class PackRxLink(BaseModel):
    id = PrimaryKeyField()
    patient_rx_id = ForeignKeyField(PatientRx)
    pack_id = ForeignKeyField(PackDetails)
    original_drug_id = ForeignKeyField(DrugMaster, null=True, related_name="original_pack_rx")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_rx_link"


def migrate_58():
    init_db(db, "database_migration")

    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            PackRxLink._meta.db_table,
            PackRxLink.original_drug_id.db_column,
            PackRxLink.original_drug_id
        )
    )
    print('Table(s) Modified: PackRxLink')

if __name__ == '__main__':
    migrate_58()
