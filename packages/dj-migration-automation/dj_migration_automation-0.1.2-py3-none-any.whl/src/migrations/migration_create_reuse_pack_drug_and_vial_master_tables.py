import settings
from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_vail_master import VailMaster
from src.model.model_reuse_pack_drug import ReusePackDrug

migrator = MySQLMigrator(db)
init_db(db, 'database_migration')


def create_reuse_pack_drug_and_vial_master():

    init_db(db, 'database_migration')

    try:
        with db.transaction():
            db.create_tables([ReusePackDrug])
            print("reuse_pack_drug and vail_master table is created")
    except Exception as e:
        settings.logger.error("Error while create the table reuse_pack_drug and vail_master: ", str(e))


if __name__ == "__main__":
    create_reuse_pack_drug_and_vial_master()
