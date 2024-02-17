import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_drug_lot_master import DrugLotMaster

init_db(db, 'database_migration')
migrator = MySQLMigrator(db)

def create_drug_lot_master_table():

    init_db(db, 'database_migration')

    try:
        with db.transaction():
            db.create_tables([DrugLotMaster])
            print("drug_lot_master table is created")
    except Exception as e:
        settings.logger.error("Error while create the table drug_lot_master: ", str(e))


if __name__ == "__main__":
    create_drug_lot_master_table()
