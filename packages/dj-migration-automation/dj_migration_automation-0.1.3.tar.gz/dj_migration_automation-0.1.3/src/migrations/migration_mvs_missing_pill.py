import settings
from src.model.model_group_master import GroupMaster
from src.model.model_missing_drug_pack import MissingDrugPack
from src.model.model_reason_master import ReasonMaster
from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.constants import MVS_REASON_GROUP, MVS_PRINTER_SLOW, MVS_HEAT_SEAL_NOT_WORKING, \
    MVS_UNLOADING_STATION_NOT_WORKING, MVS_DRUGS_OUT_OF_STOCK, MVS_MULTIPLE_LABEL, MVS_MISSING_PILLS, MVS_OTHER

mvs_feature: str = "MVS: Missing Pill Option -- "


def migrate_mvs_missing_pill():
    print(mvs_feature + "Migration Started...")

    try:
        init_db(db, 'database_migration')
        print(mvs_feature + "Database Connection: Done")

        add_table_missing_drug_pack()
        add_data()

        print(mvs_feature + "Migration Executed...")
    except Exception as e:
        settings.logger.error("Error while executing migration for {}".format(mvs_feature), str(e))


def add_table_missing_drug_pack():
    try:
        print(mvs_feature + "New Table creation missing_drug_pack: Started")
        db.create_tables([MissingDrugPack], safe=True)
        print(mvs_feature + "New Table Creation: Done")
    except Exception as e:
        settings.logger.error("Error while executing table creation for missing_drug_pack.", str(e))
        raise


def add_data():
    try:
        print(mvs_feature + "Insertion in Group Master and Reason Master: Started")

        if GroupMaster.table_exists():
            GroupMaster.insert(id=MVS_REASON_GROUP, name='MVSReason').execute()
        print(mvs_feature + "Insertion in Group Master: Done")

        if ReasonMaster.table_exists():
            ReasonMaster.insert(id=MVS_PRINTER_SLOW, reason_group=MVS_REASON_GROUP,
                                reason="Printer Slow").execute()
            ReasonMaster.insert(id=MVS_HEAT_SEAL_NOT_WORKING, reason_group=MVS_REASON_GROUP,
                                reason="Heat Seal Not Working").execute()
            ReasonMaster.insert(id=MVS_UNLOADING_STATION_NOT_WORKING, reason_group=MVS_REASON_GROUP,
                                reason="Unloading Station Not Working").execute()
            ReasonMaster.insert(id=MVS_DRUGS_OUT_OF_STOCK, reason_group=MVS_REASON_GROUP,
                                reason="Drugs Out of Stock").execute()
            ReasonMaster.insert(id=MVS_MULTIPLE_LABEL, reason_group=MVS_REASON_GROUP,
                                reason="Multiple label").execute()
            ReasonMaster.insert(id=MVS_MISSING_PILLS, reason_group=MVS_REASON_GROUP,
                                reason="Missing Pills").execute()
            ReasonMaster.insert(id=MVS_OTHER, reason_group=MVS_REASON_GROUP,
                                reason="Other").execute()

        print(mvs_feature + "Insertion in Reason Master: Done")
    except Exception as e:
        settings.logger.error("Error while executing insertion of Group Master or Reason Master constants.", str(e))
        raise


if __name__ == "__main__":
    migrate_mvs_missing_pill()
