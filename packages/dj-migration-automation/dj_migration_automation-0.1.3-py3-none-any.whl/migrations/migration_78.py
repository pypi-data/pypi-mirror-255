from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class FileHeader(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    status = ForeignKeyField(CodeMaster)
    filename = CharField(max_length=150)
    filepath = CharField(null=True, max_length=200)
    manual_upload = BooleanField(null=True) # added - Amisha
    message = CharField(null=True, max_length=500)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    created_time = TimeField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_header"


class TemplateMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)
    # patient_id = ForeignKeyField(PatientMaster)
    file_id = ForeignKeyField(FileHeader)
    status = ForeignKeyField(CodeMaster)
    is_modified = BooleanField()
    delivery_datetime = DateTimeField(null=True, default=None)
    fill_manual = BooleanField(default=False)  # for marking packs manual generated from template
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    reason = CharField(max_length=255, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"


def migrate_78():

    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)
    migrate(migrator.add_column(
        TemplateMaster._meta.db_table,
        TemplateMaster.reason.db_column,
        TemplateMaster.reason
    ))
    print('Table Modified: TemplateMaster')
    with db.transaction():
        sub_q = FileHeader.select(FileHeader.message)\
            .where(FileHeader.status == settings.UNGENERATE_FILE_STATUS,
                   FileHeader.id == TemplateMaster.file_id)
        query = TemplateMaster.update(status=settings.UNGENERATED_TEMPLATE_STATUS,
                                      reason=sub_q)\
            .where(TemplateMaster.status == settings.UNGENERATE_FILE_STATUS)
        status = query.execute()
        print('Rows updated with reason ', status)


if __name__ == '__main__':
    migrate_78()