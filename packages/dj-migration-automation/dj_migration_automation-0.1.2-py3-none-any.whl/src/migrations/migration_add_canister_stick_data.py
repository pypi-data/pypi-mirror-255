import logging
from typing import Dict

from playhouse.migrate import *

from dosepack.base_model.base_model import db
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_canister_master import CanisterMaster
from model.model_init import init_db
from src.model.model_canister_stick import CanisterStick
from src.model.model_small_canister_stick import SmallCanisterStick
from src.service.volumetric_analysis import get_canister_stick_id_by_serial_number
from src.service.canister import get_canister_data_from_oddo_product_id
from src.model.model_canister_drum import CanisterDrum

logger = logging.getLogger("root")


def migration_add_canister_stick_data(company_id: int):
    logger.info("Started migration_add_canister_stick_data.")
    init_db(db, 'database_migration')
    migrator: MySQLMigrator = MySQLMigrator(db)
    # drop_column_canister_stick_id(migrator=migrator)
    # truncate_tables_related_to_canister_stick_canister_drum()
    # add_column_canister_stick_id(migrator=migrator)
    insert_mapping_data_in_canister_master(company_id)
    logger.info("migration_add_canister_stick_data ended successfully.")


def drop_column_canister_stick_id(migrator: MySQLMigrator):
    """
    Drop column canister_stick_id CanisterMaster Table
    @param migrator:
    @return:
    """
    try:
        if any(column_data.name == 'canister_stick_id_id' for column_data in db.get_columns('canister_master')):
            migrate(
                migrator.drop_column(
                    CanisterMaster._meta.db_table,
                    CanisterMaster.canister_stick_id.db_column,
                    CanisterMaster.canister_stick_id
                )
            )
            logger.info("Table Modified: CanisterMaster, column canister_stick_id dropped successfully.")
    except Exception as e:
        logger.error("Error while dropping column canister_stick_id from canister_master", str(e))


def add_column_canister_stick_id(migrator: MySQLMigrator):
    """
    Add column canister_stick_id CanisterMaster Table
    @param migrator:
    @return:
    """
    try:
        if not(any(column_data.name == 'canister_stick_id_id' for column_data in db.get_columns('canister_master'))):
            if CanisterMaster.table_exists():
                migrate(
                    migrator.add_column(
                        CanisterMaster._meta.db_table,
                        CanisterMaster.canister_stick_id.db_column,
                        CanisterMaster.canister_stick_id
                    )
                )
                print("Table Modified: CanisterMaster, column canister_stick_id added successfully.")
    except Exception as e:
        logger.error("Error while dropping column canister_stick_id from canister_master", str(e))


def insert_mapping_data_in_canister_master(company_id: int):
    """
    Insert latest data from odoo in Canister stick column in canister master table
    @param company_id:
    @return:
    """
    try:
        logger.info("in insert_mapping_data_in_canister_master")
        canister_id_by_product_id_dict: Dict[int, int] = dict()
        canister_stick_by_product_id: Dict[int, int] = dict()
        query = CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                      CanisterMaster.product_id.alias('product_id')).where(
            (CanisterMaster.company_id == 3) & (CanisterMaster.product_id.is_null(False)) &
            (CanisterMaster.canister_stick_id.is_null(True)) & (CanisterMaster.rfid.is_null(False)))

        for data in query.dicts():
            canister_id_by_product_id_dict[data["product_id"]] = data["canister_id"]
            product_id = data["product_id"]

            bs_serial_number, ss_serial_number, drum_serial_number, canister_detail = get_canister_data_from_oddo_product_id(
                product_id, company_id, flag=True)
            logger.info("bs_Serial_number {}, ss_serial_number {}, drum_serial_number is {}.".format(
                bs_serial_number, ss_serial_number, drum_serial_number))

            if (bs_serial_number and ss_serial_number) or drum_serial_number:
                canister_stick_by_product_id[product_id] = get_canister_stick_id_by_serial_number(bs_serial_number,
                                                                                                  ss_serial_number,
                                                                                                  drum_serial_number,
                                                                                                  canister_detail)
            logger.info("For Canister ID {}, Product ID {}, canister_stick_id is {}.".format(
                canister_id_by_product_id_dict[product_id],
                product_id, canister_stick_by_product_id[product_id]))

            CanisterMaster.update(canister_stick_id=canister_stick_by_product_id[product_id]).where(
                CanisterMaster.id == canister_id_by_product_id_dict[product_id]).execute()

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return e
    except Exception as e:
        logger.info(e, exc_info=True)
        return e


def truncate_tables_related_to_canister_stick_canister_drum():
    """
        #  truncate tables related to canister stick and canister drum
    """
    try:
        db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        if BigCanisterStick.table_exists():
            db.truncate_table(BigCanisterStick)
        if SmallCanisterStick.table_exists():
            db.truncate_table(SmallCanisterStick)
        if CanisterDrum.table_exists():
            db.truncate_table(CanisterDrum)
        if CanisterStick.table_exists():
            db.truncate_table(CanisterStick)
        db.execute_sql("SET FOREIGN_KEY_CHECKS=1")

        print("Truncated tables")
    except Exception as e:
        logger.error("Error while truncating tables", str(e))


if __name__ == '__main__':
    migration_add_canister_stick_data(company_id=3)
