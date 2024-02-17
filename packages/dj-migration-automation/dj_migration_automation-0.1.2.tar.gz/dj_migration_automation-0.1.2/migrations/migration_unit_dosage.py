from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


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

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class PackHeader(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_header"


class FacilityDistributionMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_distribution_master"


class OldPackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)  # system_id from dpauth project System table
    pack_header_id = ForeignKeyField(PackHeader)
    batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    is_takeaway = BooleanField(default=False)
    pack_status = ForeignKeyField(CodeMaster)
    filled_by = FixedCharField(max_length=64)
    consumption_start_date = DateField()
    consumption_end_date = DateField()
    filled_days = SmallIntegerField()
    fill_start_date = DateField()
    delivery_schedule = FixedCharField(max_length=50)
    association_status = BooleanField(null=True)
    rfid = FixedCharField(null=True, max_length=20, unique=True)
    pack_plate_location = FixedCharField(max_length=2, null=True)
    order_no = IntegerField(null=True)
    filled_date = DateTimeField(null=True)
    filled_at = SmallIntegerField(null=True)
    # marked filled at which step
    # Any manual goes in 0-10, If filled by system should be > 10
    #  0 - Template(Auto marked manual for manual system),
    #  1 - Pack Pre-Processing/Facility Distribution, 2 - PackQueue, 3 - MVS
    #  11 - DosePacker
    fill_time = IntegerField(null=True, default=None)  # in seconds
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class PackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)  # system_id from dpauth project System table
    pack_header_id = ForeignKeyField(PackHeader)
    batch_id = ForeignKeyField(BatchMaster, null=True)
    pack_display_id = IntegerField()
    pack_no = SmallIntegerField()
    is_takeaway = BooleanField(default=False)
    pack_status = ForeignKeyField(CodeMaster, related_name="pack_details_pack_status")
    filled_by = FixedCharField(max_length=64)
    consumption_start_date = DateField()
    consumption_end_date = DateField()
    filled_days = SmallIntegerField()
    fill_start_date = DateField()
    delivery_schedule = FixedCharField(max_length=50)
    association_status = BooleanField(null=True)
    rfid = FixedCharField(null=True, max_length=20, unique=True)
    pack_plate_location = FixedCharField(max_length=2, null=True)
    order_no = IntegerField(null=True)
    filled_date = DateTimeField(null=True)
    filled_at = SmallIntegerField(null=True)
    # marked filled at which step
    # Any manual goes in 0-10, If filled by system should be > 10
    #  0 - Template(Auto marked manual for manual system),
    #  1 - Pack Pre-Processing/Facility Distribution, 2 - PackQueue, 3 - MVS
    #  11 - DosePacker
    fill_time = IntegerField(null=True, default=None)  # in seconds
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    modified_date = DateTimeField(default=get_current_date_time)
    facility_dis_id = ForeignKeyField(FacilityDistributionMaster, null=True)
    # facility_dis_id_id = IntegerField()
    car_id = IntegerField(null=True)
    unloading_time = DateTimeField(null=True)
    pack_sequence = IntegerField(null=True)
    dosage_type = ForeignKeyField(CodeMaster, default=settings.DOSAGE_TYPE_MULTI)
    filling_status = ForeignKeyField(CodeMaster, null=True, related_name="packdetails_filling_status")

    # facility_distribution_id_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


def migrate_unit_dosage():
    init_db(db, "database_migration")

    if GroupMaster.table_exists():
        GroupMaster.insert(id=settings.DOSAGE_TYPE_GROUP_ID, name='DoseType').execute()
        GroupMaster.insert(id=settings.FILLING_STATUS_GROUP_ID, name='FillingStatus').execute()
    if CodeMaster.table_exists():
        CodeMaster.insert(id=settings.DOSAGE_TYPE_UNIT, group_id=settings.DOSAGE_TYPE_GROUP_ID,
                          key=settings.DOSAGE_TYPE_UNIT, value="Unit Dose").execute()
        CodeMaster.insert(id=settings.DOSAGE_TYPE_MULTI, group_id=settings.DOSAGE_TYPE_GROUP_ID,
                          key=settings.DOSAGE_TYPE_MULTI, value="Multi Dose").execute()
        CodeMaster.insert(id=settings.FILLING_STATUS_MFD, group_id=settings.FILLING_STATUS_GROUP_ID,
                          key=settings.FILLING_STATUS_MFD, value="Mfd").execute()
        CodeMaster.insert(id=settings.FILLING_STATUS_MANUAL, group_id=settings.FILLING_STATUS_GROUP_ID,
                          key=settings.FILLING_STATUS_MANUAL, value="Manual").execute()
        CodeMaster.insert(id=settings.FILLING_STATUS_MFD_AND_MANUAL, group_id=settings.FILLING_STATUS_GROUP_ID,
                          key=settings.FILLING_STATUS_MFD_AND_MANUAL, value="Mfd and Manual").execute()
    print('Data Added in GroupMaster, CodeMaster')

    migrator = MySQLMigrator(db)
    if OldPackDetails.table_exists():
        migrate(
            migrator.add_column(
                PackDetails._meta.db_table,
                PackDetails.dosage_type.db_column,
                PackDetails.dosage_type
            ),
            migrator.add_column(
                PackDetails._meta.db_table,
                PackDetails.filling_status.db_column,
                PackDetails.filling_status
            )
        )
        print("Table Modified: PACK DETAILS")


if __name__ == "__main__":
    migrate_unit_dosage()
