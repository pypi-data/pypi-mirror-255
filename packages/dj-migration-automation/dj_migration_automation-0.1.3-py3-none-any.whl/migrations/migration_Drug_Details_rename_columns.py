from playhouse.migrate import *
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time


class DrugMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class OldDrugDetails(BaseModel):
    id = PrimaryKeyField()
    drug_master_id = ForeignKeyField(DrugMaster, unique=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_details"


class DrugDetails(BaseModel):
    id = PrimaryKeyField()
    drug_master_id = ForeignKeyField(DrugMaster, unique=True)
    last_seen_by = IntegerField()
    last_seen_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_details"


def migrate_drug_details():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)

    if DrugDetails.table_exists():
        migrate(
            migrator.rename_column(DrugDetails._meta.db_table, OldDrugDetails.created_by.db_column, 'last_seen_by'),
            migrator.rename_column(DrugDetails._meta.db_table, OldDrugDetails.created_date.db_column, 'last_seen_date')
        )

        print("columns name modified in table drug_details")


if __name__ == '__main__':
    migrate_drug_details()