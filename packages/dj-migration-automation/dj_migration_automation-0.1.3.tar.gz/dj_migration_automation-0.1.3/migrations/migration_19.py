from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class DrugMaster(BaseModel):
    id = PrimaryKeyField()
    drug_name = CharField(max_length=255)
    ndc = CharField(max_length=14, unique=True)
    formatted_ndc = CharField(max_length=12, null=True)
    strength = CharField(max_length=50)
    strength_value = CharField(max_length=16)
    manufacturer = CharField(null=True, max_length=100)
    txr = CharField(max_length=8, null=True)
    imprint = CharField(null=True, max_length=82)
    color = CharField(null=True, max_length=30)
    shape = CharField(null=True, max_length=30)
    image_name = CharField(null=True, max_length=255)
    brand_flag = CharField(null=True, max_length=1)
    brand_drug = CharField(null=True, max_length=50)
    drug_form = CharField(null=True, max_length=15)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class FileHeader(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_header"


class ImportedDrug(BaseModel):
    id = PrimaryKeyField()
    drug_name = CharField(max_length=255)
    ndc = CharField(max_length=14)
    formatted_ndc = CharField(max_length=12, null=True)
    strength = CharField(max_length=50, null=True)
    strength_value = CharField(max_length=16, null=True)
    manufacturer = CharField(null=True, max_length=100)
    txr = CharField(max_length=8, null=True)
    imprint = CharField(null=True, max_length=82)
    color = CharField(null=True, max_length=30)
    shape = CharField(null=True, max_length=30)
    image_name = CharField(null=True, max_length=255)
    brand_flag = CharField(null=True, max_length=1)
    brand_drug = CharField(null=True, max_length=50)
    drug_form = CharField(null=True, max_length=15)
    file_id = ForeignKeyField(FileHeader, null=True)
    source = CharField(max_length=500, null=True)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "imported_drug"


def migrate_19():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)

    if DrugMaster.table_exists():
        migrate(migrator.add_column(DrugMaster._meta.db_table,
                                    DrugMaster.drug_form.db_column,
                                    DrugMaster.drug_form))
    if ImportedDrug.table_exists():
        migrate(migrator.add_column(ImportedDrug._meta.db_table,
                                    ImportedDrug.drug_form.db_column,
                                    ImportedDrug.drug_form))
    print("Tables modified: DrugMaster, ImportedDrug")


def rollback_19():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)

    if DrugMaster.table_exists():
        migrate(migrator.drop_column(DrugMaster._meta.db_table,
                                    DrugMaster.drug_form.db_column))
    if ImportedDrug.table_exists():
        migrate(migrator.drop_column(ImportedDrug._meta.db_table,
                                    ImportedDrug.drug_form.db_column))
    print("Tables modified: DrugMaster, ImportedDrug")