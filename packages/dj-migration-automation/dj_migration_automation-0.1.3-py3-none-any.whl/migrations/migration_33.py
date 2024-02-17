from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from dosepack.utilities.utils import get_current_date_time
from playhouse.migrate import *
import settings


class OldPVSSlot(BaseModel):  # SlotHeader Level Data
    id = PrimaryKeyField()
    # pvs_pack_id = ForeignKeyField(PVSPack)
    batch_id = SmallIntegerField()
    # slot_header_id = ForeignKeyField(SlotHeader)
    top_light_image = CharField()
    bottom_light_image = CharField()
    recognition_status = BooleanField(default=False)
    us_status = BooleanField(default=False)
    actual_count = DecimalField(decimal_places=2, max_digits=4)
    predicted_count = DecimalField(decimal_places=2, max_digits=4, null=True)
    drop_count = DecimalField(decimal_places=2, max_digits=4)
    mft_status = BooleanField(default=False)
    created_date = DateTimeField()
    modified_date = DateTimeField()
    created_by = IntegerField()
    modified_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot'


class PVSSlot(BaseModel):  # SlotHeader Level Data
    id = PrimaryKeyField()
    # pvs_pack_id = ForeignKeyField(PVSPack)
    batch_id = SmallIntegerField()
    # slot_header_id = ForeignKeyField(SlotHeader)
    top_light_image = CharField()  # image will be stored in cloud storage
    bottom_light_image = CharField()
    recognition_status = BooleanField(default=False)  # pvs recognition done or not
    us_status = ForeignKeyField(CodeMaster, default=39)  # slot should be highlight on user station
    actual_count = DecimalField(decimal_places=2, max_digits=4)
    predicted_count = DecimalField(decimal_places=2, max_digits=4, null=True)  # None If pvs not execute for pill count
    drop_count = DecimalField(decimal_places=2, max_digits=4)
    mft_status = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot'


def migrate_33():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    if GroupMaster.table_exists():
        group_id, status = GroupMaster.get_or_create(name='PVS')
        if CodeMaster.table_exists():
            code_id, created = CodeMaster.get_or_create(id=39, group_id=group_id, key=39, value='Rejected')
            code_id, created = CodeMaster.get_or_create(id=40, group_id=group_id, key=40, value='Success')
            code_id, created = CodeMaster.get_or_create(id=41, group_id=group_id, key=41, value='Not Confident')
            code_id, created = CodeMaster.get_or_create(id=42, group_id=group_id, key=42, value='Deleted')
            code_id, created = CodeMaster.get_or_create(id=43, group_id=group_id, key=43, value='Missing Pills')
            code_id, created = CodeMaster.get_or_create(id=44, group_id=group_id, key=44, value='Missing and deleted')
        print("Table(s) modified: GroupMaster, CodeMaster")
    if OldPVSSlot.table_exists():
        query = OldPVSSlot.select(OldPVSSlot.id, OldPVSSlot.us_status).dicts()\
            .where(OldPVSSlot.us_status == 1).execute()
        status_update_list = list()
        for record in query:
            status_update_list.append(record["id"])
        migrate(
            migrator.drop_column(
                OldPVSSlot._meta.db_table,
                OldPVSSlot.us_status.db_column,
            ),
            migrator.add_column(
                PVSSlot._meta.db_table,
                PVSSlot.us_status.db_column,
                PVSSlot.us_status
            )
        )
        print("Table(s) modified: PVSSlot")
        if status_update_list:
            count = PVSSlot.update({PVSSlot.us_status: 40}).where(PVSSlot.id << status_update_list).execute()
            print("Table(s) updated: PVSSlot, row(s) with us_status 40 updated: {} ".format(count))


if __name__ == "__main__":
    migrate_33()
