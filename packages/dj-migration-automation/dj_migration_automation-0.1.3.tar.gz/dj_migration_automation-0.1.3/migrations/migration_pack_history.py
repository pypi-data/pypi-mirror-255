from peewee import PrimaryKeyField, ForeignKeyField, SmallIntegerField, CharField, DateTimeField, IntegerField, \
    FixedCharField, BooleanField
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from model.model_init import init_db
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
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


class PackDetails(BaseModel):
    id = PrimaryKeyField()
    # company_id = IntegerField()
    # system_id = IntegerField(null=True)  # system_id from dpauth project System table
    # pack_header_id = ForeignKeyField(PackHeader)
    # batch_id = ForeignKeyField(BatchMaster, null=True)
    # pack_display_id = IntegerField()
    # pack_no = SmallIntegerField()
    # is_takeaway = BooleanField(default=False)
    # pack_status = ForeignKeyField(CodeMaster, related_name="pack_details_pack_status")
    # filled_by = FixedCharField(max_length=64)
    # consumption_start_date = DateField()
    # consumption_end_date = DateField()
    # filled_days = SmallIntegerField()
    # fill_start_date = DateField()
    # delivery_schedule = FixedCharField(max_length=50)
    # association_status = BooleanField(null=True)
    # rfid = FixedCharField(null=True, max_length=20, unique=True)
    # pack_plate_location = FixedCharField(max_length=2, null=True)
    # order_no = IntegerField(null=True)
    # filled_date = DateTimeField(null=True)
    # filled_at = SmallIntegerField(null=True)
    # # marked filled at which step
    # # Any manual goes in 0-10, If filled by system should be > 10
    # #  0 - Template(Auto marked manual for manual system),
    # #  1 - Pack Pre-Processing/Facility Distribution, 2 - PackQueue, 3 - MVS
    # #  11 - DosePacker
    # fill_time = IntegerField(null=True, default=None)  # in seconds
    # created_by = IntegerField()
    # modified_by = IntegerField()
    # created_date = DateField()
    # modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class PackHistory(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    action_id = ForeignKeyField(ActionMaster)
    action_taken_by = IntegerField()
    action_date_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_history"


class PackHistoryDetails(BaseModel):
    id = PrimaryKeyField()
    pack_history_id = ForeignKeyField(PackHistory)
    name = FixedCharField(max_length=50)
    value = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_history_details"


class DrugStockHistory(BaseModel):
    id = PrimaryKeyField()
    # drug_master_id = ForeignKeyField(DrugMaster, related_name='drug_id')
    unique_drug_id = ForeignKeyField(UniqueDrug)
    is_in_stock = BooleanField(default=True)
    is_active = BooleanField(default=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_stock_history"


class Notification(BaseModel):
    id = PrimaryKeyField()
    message = CharField(null=True, default=None,max_length=500)
    user_id = IntegerField()
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    read_date = DateTimeField(null=True, default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "notifications"


class DrugDetails(BaseModel):
    id = PrimaryKeyField()
    drug_master_id = ForeignKeyField(DrugMaster, related_name='drug_details_id')
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_details"


def migrate_pack_history():
    init_db(db, "database_migration")

    action_start_id = 7
    actions = [
        'Pack assigned',
        'Ndc change',
        'Print label',
        'Pack filled partially',
        'Scan label',
        'Verification',
        'Out for delivery',
        'Delivered',
        'Status Change',
        'Stock Change',
        'Template Change',
        'Pre Process',
        'Uploaded',
        'Generated',
    ]
    for action in actions:
        ActionMaster.get_or_create(
            id=action_start_id,
            group_id=1,
            key=action_start_id,
            value=action
        )
        action_start_id += 1
    print('Table(s) Updated: ActionMaster')

    db.create_tables([PackHistory, PackHistoryDetails,Notification, DrugStockHistory, DrugDetails], safe=True)
    print('table created: PackHistory, PackHistoryDetails, Notifications, DrugStockHistory, DrugDetails')


def migrate_notification():
    init_db(db, "database_migration")
    db.create_tables([Notification], safe=True)
    print('table created: notifications')


if __name__ == '__main__':
    migrate_pack_history()
