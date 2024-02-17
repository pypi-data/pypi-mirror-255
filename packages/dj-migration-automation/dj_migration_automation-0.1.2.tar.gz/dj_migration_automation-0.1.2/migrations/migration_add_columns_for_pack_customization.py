import logging
from playhouse.migrate import *
from src.model.model_template_master import TemplateMaster
from src.model.model_code_master import CodeMaster
from src.model.model_group_master import GroupMaster
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants
from src.model.model_company_setting import CompanySetting

logger = logging.getLogger("root")


def migration_add_template_split_count_threshold_in_company_settings():
    try:

        init_db(db, 'database_migration')
        row_data = [
            {
                "company_id": 3,
                "name": "TEMPLATE_SPLIT_COUNT_THRESHOLD_UNIT",
                "value": 3,
                "created_by": 2,
                "modified_by": 2
            }
        ]
        if CompanySetting.table_exists():
            CompanySetting.insert_many(row_data).execute()
            print("Added template split count threshold for unit packs in company settings")
    except Exception as e:
        print(e)
        raise e


def add_codes_in_code_master_for_pack_fill_type():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    try:
        if GroupMaster.table_exists():
            GroupMaster.insert(id=constants.PACK_FILL_TYPE,
                               name='PackFillType').execute()

        if CodeMaster.table_exists():
            CodeMaster.insert(id=constants.MULTI_DOSE_PER_PACK,
                              group_id=constants.PACK_FILL_TYPE,
                              value="Multi").execute()
            CodeMaster.insert(id=constants.UNIT_DOSE_PER_PACK,
                              group_id=constants.PACK_FILL_TYPE,
                              value="Unit").execute()
        print("Codes added in code master and group master")
    except Exception as e:
        logger.error("Error while adding codes in CodeMaster: ", str(e))


def add_columns_in_template_master_for_updated_file():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(TemplateMaster._meta.db_table,
                                TemplateMaster.pack_type.db_column,
                                TemplateMaster.pack_type)
        )
        print("pack_type columns added in TemplateMaster")
        migrate(
            migrator.add_column(TemplateMaster._meta.db_table,
                                TemplateMaster.customized.db_column,
                                TemplateMaster.customized)
        )
        print("customized columns added in TemplateMaster")
        migrate(
            migrator.add_column(TemplateMaster._meta.db_table,
                                TemplateMaster.seperate_pack_per_dose.db_column,
                                TemplateMaster.seperate_pack_per_dose)
        )
        print("seperate_pack_per_dose columns added in TemplateMaster")
        migrate(
            migrator.add_column(TemplateMaster._meta.db_table,
                                TemplateMaster.true_unit.db_column,
                                TemplateMaster.true_unit)
        )
        print("true_unit columns added in TemplateMaster")

        migrate(
            migrator.add_column(TemplateMaster._meta.db_table,
                                TemplateMaster.is_bubble.db_column,
                                TemplateMaster.is_bubble)
        )
        print("is_bubble columns added in TemplateMaster")
    except Exception as e:
        logger.error("Error while adding columns in TemplateMaster: ", str(e))


def pack_customization_columns_and_codes():
    migration_add_template_split_count_threshold_in_company_settings()
    add_codes_in_code_master_for_pack_fill_type()
    add_columns_in_template_master_for_updated_file()


if __name__ == "__main__":
    pack_customization_columns_and_codes()
