# pharmacy_doctor_id, company_id
#
# pharmacy_patient_id, company_id
from peewee import *
from playhouse.migrate import MySQLMigrator, migrate

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


class FacilityMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    pharmacy_facility_id = IntegerField()
    facility_name = CharField(max_length=40)
    address1 = CharField(null=True)
    address2 = CharField(null=True)
    cellphone = FixedCharField(max_length=14, null=True)
    workphone = FixedCharField(max_length=14, null=True)
    fax = FixedCharField(max_length=14, null=True)
    email = CharField(max_length=320, null=True)
    website = CharField(null=True, max_length=50)
    active = BooleanField(null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pharmacy_facility_id', 'company_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_master"


class DoctorMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    pharmacy_doctor_id = IntegerField()
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    address1 = CharField(null=True)
    address2 = CharField(null=True)
    cellphone = FixedCharField(max_length=14, null=True)
    workphone = FixedCharField(max_length=14, null=True)
    fax = FixedCharField(max_length=14, null=True)
    email = CharField(max_length=320, null=True)
    website = CharField(null=True, max_length=50)
    active = BooleanField(null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pharmacy_doctor_id', 'company_id'), True),
        )

        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "doctor_master"


class PatientMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    facility_id = ForeignKeyField(FacilityMaster)
    pharmacy_patient_id = IntegerField()
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    patient_picture = CharField(null=True)
    address1 = CharField()
    zip_code = CharField(max_length=9)
    city = CharField(max_length=50, null=True)
    state = CharField(max_length=50, null=True)
    address2 = CharField(null=True)
    cellphone = FixedCharField(max_length=14, null=True)
    workphone = FixedCharField(max_length=14, null=True)
    fax = FixedCharField(max_length=14, null=True)
    email = CharField(max_length=320, null=True)
    website = CharField(null=True, max_length=50)
    active = BooleanField(null=True)
    dob = DateField(null=True)
    allergy = CharField(null=True, max_length=500)
    patient_no = FixedCharField(null=True, max_length=35)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pharmacy_patient_id', 'company_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_master"


def add_unique_constraint_in_facility_patient_doctor_master():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)

    migrate(
        migrator.add_index(FacilityMaster._meta.db_table,
                            (FacilityMaster.pharmacy_facility_id.db_column,
                            FacilityMaster.company_id.db_column,), True),
        migrator.add_index(DoctorMaster._meta.db_table,
                           (DoctorMaster.pharmacy_doctor_id.db_column,
                            DoctorMaster.company_id.db_column,), True),
        migrator.add_index(PatientMaster._meta.db_table,
                           (PatientMaster.pharmacy_patient_id.db_column,
                            PatientMaster.company_id.db_column,), True)
    )
    print("Added unique data constraint in table(s) facility_master, doctor_master and patient_master")


if __name__ == "__main__":
    add_unique_constraint_in_facility_patient_doctor_master()