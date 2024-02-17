import logging

from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_dosage_type import DosageType
from src.model.model_drug_master import DrugMaster
from src.model.model_group_master import GroupMaster
from src.model.model_unique_drug import UniqueDrug

logger = logging.getLogger("root")

#
# class UniqueDrug(BaseModel):
#     id = PrimaryKeyField()
#     formatted_ndc = CharField()
#     txr = CharField(null=True)
#     drug_id = ForeignKeyField(DrugMaster)
#     lower_level = BooleanField(default=False)  # drug to be kept at lower level so pill doesn't break while filling
#     drug_usage = ForeignKeyField(CodeMaster, default=settings.CANISTER_DRUG_USAGE["Slow Moving"])
#     is_powder_pill = IntegerField(null=True)
#     dosage_type = ForeignKeyField(CodeMaster, null=True, default=None)
#     packaging_type = ForeignKeyField(CodeMaster, null=True, default=None)
#
#     # one of the drug id which has same formatted ndc and txr number
#     #  TODO think only drug id or (formatted_ndc, txr)
#
#     class Meta:
#         indexes = (
#             (('formatted_ndc', 'txr'), True),
#         )
#         if settings.TABLE_NAMING_CONVENTION == '_':
#             db_table = 'unique_drug'


init_db(db, 'database_migration')
migrator = MySQLMigrator(db)


def add_dosage_type_column_in_unique_drug():


    try:
        if UniqueDrug.table_exists():
            migrate(
                migrator.add_column(UniqueDrug._meta.db_table,
                                    UniqueDrug.dosage_type.db_column,
                                    UniqueDrug.dosage_type)
            )
            print("Added dosage_type column in UniqueDrug")
    except Exception as e:
        settings.logger.error("Error while adding dosage_type columns in UniqueDrug: ", str(e))


def add_packaging_type_column_in_unique_drug():

    try:
        if UniqueDrug.table_exists():
            migrate(
                migrator.add_column(UniqueDrug._meta.db_table,
                                    UniqueDrug.packaging_type.db_column,
                                    UniqueDrug.packaging_type)
            )
            print("Added packaging_type column in UniqueDrug")
    except Exception as e:
        settings.logger.error("Error while adding packaging_type columns in UniqueDrug: ", str(e))


def add_status_in_code_master_group_master():

    try:

        with db.transaction():

            if GroupMaster.table_exists():

                GroupMaster.insert(id=constants.PACKAGING_TYPE_GROUP_ID,
                                   name='PackagingType').execute()
                print("PackagingType inserted in GroupMaster")

            if CodeMaster.table_exists():

                CodeMaster.insert(id=constants.PACKAGING_TYPE_BLISTER_PACK_MULTI_7X4,
                                  group_id=constants.PACKAGING_TYPE_GROUP_ID,
                                  value="Blister Pack").execute()
                print("PACKAGING_TYPE_BLISTER_PACK inserted in CodeMaster")

                CodeMaster.insert(id=constants.PACKAGING_TYPE_DRUG_BOTTLE,
                                  group_id=constants.PACKAGING_TYPE_GROUP_ID,
                                  value="Drug Bottle").execute()
                print("PACKAGING_TYPE_DRUG_BOTTLE inserted in CodeMaster")

    except Exception as e:
        print(e)
        raise e


def add_normal_dosage_in_dosage_type():
    try:
        with db.transaction():
            DosageType.insert(id=4, code="NML", name="Normal").execute()

            print("data inserted in dosage type")
    except Exception as e:
        print(e)
        raise e


def migration_add_columns_dosage_type_packaging_type_in_unique_drug():
    add_status_in_code_master_group_master()
    add_normal_dosage_in_dosage_type()
    add_dosage_type_column_in_unique_drug()
    add_packaging_type_column_in_unique_drug()


if __name__ == '__main__':
    migration_add_columns_dosage_type_packaging_type_in_unique_drug()

