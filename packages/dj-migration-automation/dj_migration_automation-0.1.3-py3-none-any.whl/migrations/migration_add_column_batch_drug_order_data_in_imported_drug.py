from peewee import PrimaryKeyField, CharField, ForeignKeyField, DateTimeField, IntegerField
from playhouse.migrate import MySQLMigrator, migrate

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import get_current_date_time
from src.model.model_file_header import FileHeader
from model.model_init import init_db
from src.model.model_batch_drug_data import BatchDrugData
from src.model.model_batch_drug_order_data import BatchDrugOrderData


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
    order_data_id = ForeignKeyField(BatchDrugOrderData, null=True)


# add column order_data_id(ForeignKey of BatchDrugOrderData) in Imported_drug
def migration_add_column_batch_drug_order_data_id_in_imported_drug():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if ImportedDrug.table_exists():
            migrate(migrator.add_column(ImportedDrug._meta.db_table,
                                        ImportedDrug.order_data_id.db_column,
                                        ImportedDrug.order_data_id),
                    )
        print("Added column order_data_id in ImportedDrug")
    except Exception as e:
        settings.logger.error("Error while adding columns in ImportedDrug: ", str(e))


if __name__ == '__main__':
    migration_add_column_batch_drug_order_data_id_in_imported_drug()
