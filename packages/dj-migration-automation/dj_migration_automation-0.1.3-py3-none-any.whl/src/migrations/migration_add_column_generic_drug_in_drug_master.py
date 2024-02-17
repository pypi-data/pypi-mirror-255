from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings
import logging

logger = logging.getLogger("root")


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
    upc = CharField(max_length=20, unique=True, null=True)
    generic_drug = CharField(null=True, max_length=120)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


def migration_add_column_generic_drug_in_drug_master():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)

    migrate(
        migrator.add_column(
            DrugMaster._meta.db_table,
            DrugMaster.generic_drug.db_column,
            DrugMaster.generic_drug
        )
    )

    print("DrugMaster table updated. Column 'generic_drug' added.")


if __name__ == '__main__':
    migration_add_column_generic_drug_in_drug_master()
