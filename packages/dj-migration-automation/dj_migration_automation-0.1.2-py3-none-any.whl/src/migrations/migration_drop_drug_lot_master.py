import settings
from playhouse.migrate import *
from model.model_init import init_db
from src.model.model_drug_master import DrugMaster
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time

class DrugLotMaster(BaseModel):
    """
    Database table to manager the data about each lot of drugs
    """
    id = PrimaryKeyField()
    drug_id = ForeignKeyField(DrugMaster)
    lot_number = CharField(unique=True)
    expiry_date = CharField()
    total_packages = IntegerField()
    company_id = IntegerField()
    is_recall = BooleanField(default=False)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_lot_master"

def drop_drug_lot_master_table():

    init_db(db, 'database_migration')

    try:
        with db.transaction():
            if DrugLotMaster.table_exists():
                db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
                db.execute_sql("SET SQL_SAFE_UPDATES=0")
                db.drop_tables([DrugLotMaster])
                print("drug_lot_master table is dropped")
    except Exception as e:
        settings.logger.error("Error while drop the table drug_lot_master: ", str(e))


if __name__ == "__main__":
    drop_drug_lot_master_table()
