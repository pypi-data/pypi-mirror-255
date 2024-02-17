from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class PatientMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_master"


class DoctorMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "doctor_master"


class DrugMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class PatientRx(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster)
    drug_id = ForeignKeyField(DrugMaster)
    doctor_id = ForeignKeyField(DoctorMaster)
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
        indexes = (
            (('patient_id', 'pharmacy_rx_no'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_rx"


def migrate_79():

    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)
    migrate(migrator.add_index(
        PatientRx._meta.db_table,
        (PatientRx.patient_id.db_column,
        PatientRx.pharmacy_rx_no.db_column,),
        True
    ))
    print('Table updated: PatientRx')


if __name__ == '__main__':
    migrate_79()
