import src.constants
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField(null=True)
    status = ForeignKeyField(CodeMaster, null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    split_function_id = IntegerField(null=True)
    scheduled_start_time = DateTimeField(default=get_current_date_time(), null=True)
    estimated_processing_time = FloatField(null=True)
    imported_date = DateTimeField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class SlotDetails(BaseModel):
    id = PrimaryKeyField()
    # slot_id = ForeignKeyField(SlotHeader)
    # pack_rx_id = ForeignKeyField(PackRxLink)
    quantity = DecimalField(decimal_places=2, max_digits=4)
    is_manual = BooleanField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_details"


class MfdCanisterMaster(BaseModel):
    id = PrimaryKeyField()
    rfid = FixedCharField(null=True, unique=True, max_length=32)
    # location_id = ForeignKeyField(LocationMaster, null=True, unique=True)
    canister_type = CharField(max_length=36)
    active = BooleanField()
    state_status = SmallIntegerField(default=1)
    label_print_time = DateTimeField(null=True, default=None)
    erp_product_id = IntegerField(null=True, unique=True)
    company_id = IntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    # home_cart_id = ForeignKeyField(DeviceMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_master"


class MfdAnalysis(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster, related_name='batch_id')
    mfd_canister_id = ForeignKeyField(MfdCanisterMaster, null=True, related_name='mfd_can_id')
    order_no = IntegerField()
    assigned_to = IntegerField(null=True)
    status_id = ForeignKeyField(CodeMaster, related_name='can_status')
    # dest_device_id = ForeignKeyField(DeviceMaster, related_name='robot_id')
    # mfs_device_id = ForeignKeyField(DeviceMaster, null=True, related_name='manual_fill_station')
    mfs_location_number = IntegerField(null=True)
    dest_quadrant = IntegerField()
    # trolley_location_id = ForeignKeyField(LocationMaster, related_name='trolley_loc_id', null=True)
    # dropped_location_id = ForeignKeyField(LocationMaster, null=True, related_name='dropped_loc_id')
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_analysis"


class MfdAnalysisDetails(BaseModel):
    id = PrimaryKeyField()
    analysis_id = ForeignKeyField(MfdAnalysis)
    mfd_can_slot_no = IntegerField()
    drop_number = IntegerField()
    # config_id = ForeignKeyField(ConfigurationMaster)
    quantity = DecimalField(decimal_places=2, max_digits=4)
    status_id = ForeignKeyField(CodeMaster)
    slot_id = ForeignKeyField(SlotDetails)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_analysis_details"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField(max_length=50)
    serial_number = CharField(max_length=20, unique=True)
    # device_type_id = ForeignKeyField(DeviceTypeMaster)
    system_id = IntegerField(null=True)
    version = CharField(null=True)
    active = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()
    associated_device = ForeignKeyField('self', null=True)
    ip_address = CharField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


class MfdCanisterStatusHistory(BaseModel):
    id = PrimaryKeyField()
    mfd_canister_id = ForeignKeyField(MfdCanisterMaster)
    action = CharField(max_length=50)
    action_id = ForeignKeyField(ActionMaster, default=38)
    home_cart = ForeignKeyField(DeviceMaster, related_name='cart', default=1)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_status_history"


class MfdCycleHistory(BaseModel):
    id = PrimaryKeyField()
    analysis_id = ForeignKeyField(MfdAnalysis)
    action_id = ForeignKeyField(ActionMaster)
    current_status_id = ForeignKeyField(CodeMaster, related_name='current_mfd_status')
    previous_status_id = ForeignKeyField(CodeMaster, related_name='previous_mfd_status')
    action_taken_by = IntegerField()
    action_date_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_cycle_history"


class MfdCycleHistoryComment(BaseModel):
    id = PrimaryKeyField()
    cycle_history_id = ForeignKeyField(MfdCycleHistory)
    comment = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_cycle_history_comment"


class MfdStatusHistoryComment(BaseModel):
    id = PrimaryKeyField()
    status_history_id = ForeignKeyField(MfdCanisterStatusHistory)
    comment = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_status_history_comment"


def migrate_mfd_mvs():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    db.create_tables([MfdCycleHistory, MfdCycleHistoryComment, MfdStatusHistoryComment], safe=True)
    print('Table created: MfdCycleHistory, MfdCycleHistoryComment, MfdStatusHistoryComment')
    try:

        CODE_MASTER_DATA = [
                dict(id=src.constants.MFD_CANISTER_MVS_FILLING_REQUIRED, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                     value="Manual Dropping required"),
                dict(id=src.constants.MFD_CANISTER_MVS_FILLED_STATUS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                     value="Manually Dropped"),
                dict(id=src.constants.MFD_DRUG_MVS_FILLED, group_id=src.constants.GROUP_MASTER_MFD_CANISTER_DRUG,
                     value="Manually Dropped"),
                dict(id=settings.PARTIALLY_FILLED_BY_ROBOT, group_id=settings.GROUP_MASTER_PACK,
                     value="Robot Partially Filled"),
            ]

        ACTION_MASTER_DATA = [
            dict(id=src.constants.MFD_ACTION_SKIP, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Skip"),
            dict(id=src.constants.MFD_ACTION_FILLED, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Filled"),
            dict(id=src.constants.MFD_ACTION_DROPPED, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Dropped"),
            dict(id=src.constants.MFD_ACTION_PILLS_EXTRACTED, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Dropped"),
            dict(id=src.constants.MFD_ACTION_FILLING_IN_PROGRESS, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="In Progress"),
            dict(id=src.constants.MFD_ACTION_DEACTIVATE_AND_SKIP, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Deactivate and skip"),
            dict(id=src.constants.MFD_CANISTER_ACTIVATED, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Active"),
            dict(id=src.constants.MFD_CANISTER_DEACTIVATED, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Deactive"),
            dict(id=src.constants.MFD_CANISTER_ADDED, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Add"),
            dict(id=src.constants.MFD_CANISTER_DELETED, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Delete"),
            dict(id=src.constants.MFD_CANISTER_MARKED_MISPLACED, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Misplaced"),
            dict(id=src.constants.MFD_CANISTER_FOUND, group_id=src.constants.GROUP_MASTER_MFD_CANISTER,
                 value="Found"),
        ]

        CodeMaster.insert_many(CODE_MASTER_DATA).execute()
        ActionMaster.insert_many(ACTION_MASTER_DATA).execute()
        print("Table modified: CodeMaster, ActionMaster")

        if MfdCanisterStatusHistory.table_exists():
            migrate(migrator.drop_column(MfdCanisterStatusHistory._meta.db_table, MfdCanisterStatusHistory.action.db_column))
            migrate(
                migrator.add_column(MfdCanisterStatusHistory._meta.db_table, MfdCanisterStatusHistory.action_id.db_column,
                                    MfdCanisterStatusHistory.action_id),
                migrator.add_column(MfdCanisterStatusHistory._meta.db_table,
                                    MfdCanisterStatusHistory.home_cart.db_column,
                                    MfdCanisterStatusHistory.home_cart)
            )
        if MfdCanisterMaster.table_exists():
            migrate(
            migrator.add_column(MfdCanisterMaster._meta.db_table,
                                MfdCanisterMaster.state_status.db_column,
                                MfdCanisterMaster.state_status))
            deactive_canister_list = list()
            deactive_canister_query = MfdCanisterMaster.select(MfdCanisterMaster.id).dicts()\
                .where(MfdCanisterMaster.active == False)
            for deactive_canister in deactive_canister_query:
                deactive_canister_list.append(deactive_canister['id'])

            if deactive_canister_list:
                MfdCanisterMaster.update(state_status=0).where(MfdCanisterMaster.id << deactive_canister_list).execute()

            migrate(migrator.drop_column(MfdCanisterMaster._meta.db_table, MfdCanisterMaster.active.db_column))

        print("Table modified: MfdCanisterStatusHistory, MfdCanisterMaster")

    except Exception as e:
        print(e)
        print('failed')


if __name__ == "__main__":
    migrate_mfd_mvs()
