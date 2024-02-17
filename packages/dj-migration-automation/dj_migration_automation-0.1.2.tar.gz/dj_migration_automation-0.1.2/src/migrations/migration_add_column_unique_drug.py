import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from peewee import *

class DrugMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        indexes = (
            (('formatted_ndc', 'txr'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_master'

class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()
    formatted_ndc = CharField()
    txr = CharField(null=True)
    drug_id = ForeignKeyField(DrugMaster)
    lower_level = BooleanField(default=False)  # drug to be kept at lower level so pill doesn't break while filling
    drug_usage = ForeignKeyField(CodeMaster, default=settings.CANISTER_DRUG_USAGE["Slow Moving"])

    class Meta:
        indexes = (
            (('formatted_ndc', 'txr'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'

def add_column_unique_drug():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if UniqueDrug.table_exists():
            migrate(
                migrator.add_column(UniqueDrug._meta.db_table,
                                    UniqueDrug.drug_usage.db_column,
                                    UniqueDrug.drug_usage)
            )
            print("Added column in UniqueDrug")
    except Exception as e:
        settings.logger.error("Error while adding columns in UniqueDrug: ", str(e))


