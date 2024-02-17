from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants


class GroupMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'group_master'


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class PVSSlot(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot'


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


class PVSSlotDetails(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot_details'


class PVSPack(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_pack'


class TechnicianPack(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    technician_id = IntegerField()
    pvs_pack_id = ForeignKeyField(PVSPack)
    verified_pills = DecimalField(decimal_places=2, max_digits=5, default=0)
    total_pills = DecimalField(decimal_places=2, max_digits=5, default=0)
    verification_status = BooleanField(null=True, default=None)
    start_time = DateTimeField(null=True)  # time for technician
    end_time = DateTimeField(null=True)
    verification_time = SmallIntegerField(null=True)  # total time for verification in seconds
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_pack'


class TechnicianSlotDetails(BaseModel):
    id = PrimaryKeyField()
    pvs_sd_id = ForeignKeyField(PVSSlotDetails)
    technician_id = IntegerField()
    technician_ndc = CharField()
    original_ndc_match = BooleanField()  # original ndc == technician ndc
    pvs_ndc_match = BooleanField()  # PVSSlotDetails.predicted_ndc == technician ndc
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_slot_details'


class TechnicianSlot(BaseModel):
    id = PrimaryKeyField()
    pvs_sh_id = ForeignKeyField(PVSSlot)
    technician_id = IntegerField()
    verified = SmallIntegerField()  # 0 Reject, 1 Verified, 2 Not sure 3 reset
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_slot_header'


class RemoteTechSlot(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_id = ForeignKeyField(PVSSlot)
    remote_tech_id = IntegerField(null=True)
    verification_status = ForeignKeyField(CodeMaster)
    start_time = DateTimeField(default=get_current_date_time)
    end_time = DateTimeField(default=get_current_date_time)
    is_updated = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'remote_tech_slot'


class RemoteTechSlotDetails(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_details_id = ForeignKeyField(PVSSlotDetails)
    remote_tech_slot_id = ForeignKeyField(RemoteTechSlot)
    label_drug_id = ForeignKeyField(UniqueDrug, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'remote_tech_slot_details'


def migration_remote_tech():
    """
    To create new RemoteTechSlot and RemoteTechSlotDetails table
    @return: Success Message
    """
    init_db(db, "database_migration")
    if GroupMaster.table_exists():
        GroupMaster.insert(id=constants.RTS_GROUP_ID, name="RtsStatus").execute()

    if CodeMaster.table_exists():
        CodeMaster.insert(id=constants.RTS_VERIFIED, group_id=constants.RTS_GROUP_ID,
                          key=constants.RTS_VERIFIED, value="Verified").execute()
        CodeMaster.insert(id=constants.RTS_REJECTED, group_id=constants.RTS_GROUP_ID,
                          key=constants.RTS_REJECTED, value="Rejected").execute()
        CodeMaster.insert(id=constants.RTS_NOT_SURE, group_id=constants.RTS_GROUP_ID,
                          key=constants.RTS_NOT_SURE, value="Not Sure").execute()
        CodeMaster.insert(id=constants.RTS_SKIPPED, group_id=constants.RTS_GROUP_ID,
                          key=constants.RTS_SKIPPED, value="Skipped").execute()
    print('Data Added in GroupMaster, CodeMaster')

    if TechnicianSlot.table_exists():
        db.drop_tables([TechnicianSlot])
        print("Table Dropped: TechnicianSlot")
    if TechnicianSlotDetails.table_exists():
        db.drop_tables([TechnicianSlotDetails])
        print("Table Dropped: TechnicianSlotDetails")
    if TechnicianPack.table_exists():
        db.drop_tables([TechnicianPack])
        print("Table Dropped: TechnicianPack")

    db.create_tables([RemoteTechSlot, RemoteTechSlotDetails], safe=True)
    print("Table created:RemoteTechSlot,RemoteTechSlotDetails")


if __name__ == '__main__':
    migration_remote_tech()
