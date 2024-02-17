from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings
import logging

logger = logging.getLogger("root")


class PatientMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    # facility_id = ForeignKeyField(FacilityMaster)
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
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_master"


class FileHeader(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    # status = ForeignKeyField(CodeMaster)
    filename = CharField(max_length=150)
    filepath = CharField(null=True, max_length=200)
    manual_upload = BooleanField(null=True) # added - Amisha
    message = CharField(null=True, max_length=500)
    created_by = IntegerField()
    modified_by = IntegerField()
    # created_date = DateField(default=get_current_date)
    # created_time = TimeField(default=get_current_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_header"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class TemplateMasterIntermediate(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)
    patient_id = ForeignKeyField(PatientMaster)
    file_id = ForeignKeyField(FileHeader)
    status = ForeignKeyField(CodeMaster)
    is_modified = BooleanField()
    delivery_datetime = DateTimeField(null=True, default=None)
    fill_manual = BooleanField(default=False)  # for marking packs manual generated from template
    is_template_modified = SmallIntegerField(default=0)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"


class TemplateMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)
    patient_id = ForeignKeyField(PatientMaster)
    file_id = ForeignKeyField(FileHeader)
    status = ForeignKeyField(CodeMaster)
    delivery_datetime = DateTimeField(null=True, default=None)
    fill_manual = BooleanField(default=False)  # for marking packs manual generated from template
    is_modified = SmallIntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"


def migrate_62():
    init_db(db, "database_migration")

    migrator = MySQLMigrator(db)

    with db.transaction():
        migrate(
            migrator.add_column(
                TemplateMasterIntermediate._meta.db_table,
                TemplateMasterIntermediate.is_template_modified.db_column,
                TemplateMasterIntermediate.is_template_modified
            )
        )
        true_flag = TemplateMaster.select(TemplateMaster.id).dicts().where(TemplateMaster.is_modified == True)
        true_ids = [template['id'] for template in true_flag]
        print(true_ids)
        TemplateMasterIntermediate.update(is_template_modified=1)\
            .where(TemplateMasterIntermediate.id << true_ids).execute()
        migrate(
            migrator.drop_column(
                TemplateMasterIntermediate._meta.db_table,
                TemplateMasterIntermediate.is_modified.db_column
            )
        )

        migrate(
            migrator.rename_column(
                TemplateMasterIntermediate._meta.db_table,
                'is_template_modified',
                'is_modified'
            )
        )

    print('Table(s) Updated: TemplateMaster')


if __name__ == '__main__':
    migrate_62()


