import logging

from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_canister import LocationMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from src.model.model_drug_master import DrugMaster
from model.model_init import init_db
from src import constants

logger = logging.getLogger("root")

# constants
ADD_CANISTER_ACTION = 'ADD'
DELETE_CANISTER_ACTION = 'DELETE'
ACTIVATE_CANISTER_ACTION = 'ACTIVATE'
TRANSFER_CANISTER_ACTION = 'TRANSFER'
NDC_CHANGE_CANISTER_ACTION = 'NDC Change'


class CanisterHistory(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster, related_name='canister_id')
    # current_robot_id = ForeignKeyField(RobotMaster, null=True, related_name='current_robot_id')
    # previous_robot_id = ForeignKeyField(RobotMaster, null=True, related_name='previous_robot_id')
    current_location_id = ForeignKeyField(LocationMaster, null=True, related_name='current_location')
    drug_id = ForeignKeyField(DrugMaster)
    # current_canister_number = SmallIntegerField(default=0, null=True)
    # previous_canister_number = SmallIntegerField(default=0, null=True)
    previous_location_id = ForeignKeyField(LocationMaster, null=True, related_name='previous_location')
    action = CharField(max_length=50)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_history"


class CanisterStatusHistory(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster, related_name="canister_id_id")
    action = ForeignKeyField(CodeMaster, related_name="action_id")
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_status_history"


def get_data_from_canister_master(company_id: int) -> list:
    canister_status_action_list = list()
    try:
        query = CanisterMaster.select(CanisterMaster.id.alias('canister_id'), CanisterMaster.created_by,
                                      CanisterMaster.created_date).dicts() \
            .where(CanisterMaster.company_id == company_id)

        for record in query:
            record['action'] = constants.CODE_MASTER_CANISTER_ACTIVATE
            canister_status_action_list.append(record)

        return canister_status_action_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


def get_data_from_canister_history(company_id: int) -> list:
    canister_action_list = list()

    try:
        query = CanisterHistory.select(CanisterHistory.canister_id, CanisterHistory.action,
                                       CanisterHistory.created_by, CanisterHistory.created_date).dicts() \
            .join(CanisterMaster, on=CanisterMaster.id == CanisterHistory.canister_id) \
            .where(CanisterMaster.company_id == company_id)

        for record in query:
            if record['action'] == ADD_CANISTER_ACTION:
                continue
            elif record['action'] == DELETE_CANISTER_ACTION:
                record['action'] = constants.CODE_MASTER_CANISTER_DEACTIVATE
            elif record['action'] == NDC_CHANGE_CANISTER_ACTION:
                record['action'] = constants.CODE_MASTER_CANISTER_NDC_CHANGE
            elif record['action'] == ACTIVATE_CANISTER_ACTION:
                record['action'] = constants.CODE_MASTER_CANISTER_REACTIVATE
            else:
                continue
            canister_action_list.append(record)

        return canister_action_list

    except Exception as e:
        logger.error(e)
        raise


def add_data_in_canister_status_history(data_dict: list) -> bool:
    try:
        record = CanisterStatusHistory.db_create_multi_record(data_dict, CanisterStatusHistory)
        return True

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


def delete_data_from_canister_history(company_id: int) -> bool:
    try:
        canister_id = CanisterMaster.select(CanisterMaster.id).dicts().where(CanisterMaster.company_id == company_id)
        canister_list = [record['id'] for record in canister_id]
        record = CanisterHistory.delete().where(CanisterHistory.action != TRANSFER_CANISTER_ACTION,
                                                CanisterHistory.canister_id << canister_list).execute()
        logger.info("Data deleted from canister history")
        return True

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        raise


def migrate_canister_status_history(company_id: int):
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        GROUP_MASTER_DATA = [
            dict(id=constants.GROUP_MASTER_CANISTER_STATUS, name='CanisterStatus')
        ]

        CODE_MASTER_DATA = [
            dict(id=constants.CODE_MASTER_CANISTER_ACTIVATE, group_id=constants.GROUP_MASTER_CANISTER_STATUS,
                 value="Activate"),
            dict(id=constants.CODE_MASTER_CANISTER_DEACTIVATE, group_id=constants.GROUP_MASTER_CANISTER_STATUS,
                 value="Deactivate"),
            dict(id=constants.CODE_MASTER_CANISTER_REACTIVATE, group_id=constants.GROUP_MASTER_CANISTER_STATUS,
                 value="Reactivate"),
            dict(id=constants.CODE_MASTER_CANISTER_NDC_CHANGE, group_id=constants.GROUP_MASTER_CANISTER_STATUS,
                 value="NDC Change"),
            dict(id=constants.CODE_MASTER_CANISTER_NEW_FROM_OLD, group_id=constants.GROUP_MASTER_CANISTER_STATUS,
                 value="New from Old")
        ]

        GroupMaster.insert_many(GROUP_MASTER_DATA).execute()

        CodeMaster.insert_many(CODE_MASTER_DATA).execute()

        print("Table modified: GroupMaster, CodeMaster")

        db.create_tables([CanisterStatusHistory], safe=True)
        print("Table(s) Created: CanisterStatusHistory")

        canister_master_data = get_data_from_canister_master(company_id=company_id)
        logger.info("Data collected from canister master")
        canister_master_status_history_data = add_data_in_canister_status_history(canister_master_data)
        logger.info("Data added in canister status history cm {}".format(canister_master_status_history_data))

        canister_history_data = get_data_from_canister_history(company_id=company_id)
        logger.info("Data collected from canister history")
        canister_status_history_data = add_data_in_canister_status_history(canister_history_data)
        logger.info("Data added in canister status history ch {}".format(canister_status_history_data))
        delete_from_canister_history = delete_data_from_canister_history(company_id=company_id)
        logger.info("delete_from_canister_history {}".format(delete_from_canister_history))

        if CanisterHistory.table_exists():
            migrate(
                migrator.drop_column(CanisterHistory._meta.db_table,
                                     CanisterHistory.action.db_column))

            migrate(
                migrator.drop_column(CanisterHistory._meta.db_table,
                                     CanisterHistory.drug_id.db_column))
            print("action and drug_id column dropped")

    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    migrate_canister_status_history(company_id=3)
