from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)


    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'group_master'


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


class LocationMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"

class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


class CanisterTxMeta(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    cycle_id = IntegerField()
    device_id = ForeignKeyField(DeviceMaster)
    status_id = ForeignKeyField(CodeMaster)
    to_cart_transfer_count = IntegerField()
    from_cart_transfer_count = IntegerField()
    normal_cart_count = IntegerField()
    elevator_cart_count = IntegerField()
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tx_meta"


class CanisterTransfers(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    dest_device_id = ForeignKeyField(DeviceMaster, null=True)
    dest_location_number = SmallIntegerField(null=True)
    dest_quadrant = SmallIntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    trolley_loc_id = ForeignKeyField(LocationMaster, null=True)
    to_ct_meta_id = ForeignKeyField(CanisterTxMeta, null=True, related_name="to_cart_meta_id")
    from_ct_meta_id = ForeignKeyField(CanisterTxMeta, null=True, related_name="from_cart_meta_id")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfers"


def migration_canister_transfer():
    """
    To create new CanisterTransferMeta table and modify CanisterTransfers Table
    @return: Success Message
    """
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    with db.transaction():

        if GroupMaster.table_exists():
            GroupMaster.insert(id=constants.CANISTER_TRANSFER_GROUP_ID, name="CanisterTransfer").execute()

        if CodeMaster.table_exists():
            # codes for guided meta
            CodeMaster.insert(id=constants.CANISTER_TRANSFER_RECOMMENDATION_DONE,
                              group_id=constants.CANISTER_TRANSFER_GROUP_ID,
                              value="Canister Transfer Recommendation Done").execute()
            CodeMaster.insert(id=constants.CANISTER_TRANSFER_TO_TROLLEY_DONE,
                              group_id=constants.CANISTER_TRANSFER_GROUP_ID,
                              value="Canister Transfer To Trolley Done").execute()
            CodeMaster.insert(id=constants.CANISTER_TRANSFER_FROM_TROLLEY_DONE,
                              group_id=constants.CANISTER_TRANSFER_GROUP_ID,
                              value="Canister Transfer From Trolley Done").execute()

        print('Data Added in GroupMaster, CodeMaster')

        db.create_tables([CanisterTxMeta], safe=True)
        print("Table created: CanisterTransferMeta")

        if CanisterTransfers.table_exists():
            migrate(
                migrator.add_column(CanisterTransfers._meta.db_table,
                                    CanisterTransfers.to_ct_meta_id.db_column,
                                    CanisterTransfers.to_ct_meta_id)
            ),
            migrate(
                migrator.add_column(CanisterTransfers._meta.db_table,
                                    CanisterTransfers.from_ct_meta_id.db_column,
                                    CanisterTransfers.from_ct_meta_id)
            )

            print("Table CanisterTransfers Modified")


if __name__ == '__main__':
    migration_canister_transfer()
