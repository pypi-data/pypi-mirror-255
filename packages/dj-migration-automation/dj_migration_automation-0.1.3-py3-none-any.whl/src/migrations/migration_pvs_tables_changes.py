import logging

from peewee import *

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants

logger = logging.getLogger("root")


class PackDetails(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pack_details'


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'device_master'


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class PackGrid(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pack_grid'


class SlotHeader(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'slot_header'


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


class OldPVSPack(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    device_id = ForeignKeyField(DeviceMaster)
    mft_status = BooleanField()
    user_station_status = BooleanField(default=False)
    deleted = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_pack'


class OldPVSSlot(BaseModel):
    id = PrimaryKeyField()
    pvs_pack_id = ForeignKeyField(OldPVSPack)
    batch_id = SmallIntegerField()
    slot_header_id = ForeignKeyField(SlotHeader)
    top_light_image = CharField()
    bottom_light_image = CharField()
    recognition_status = BooleanField(default=False)
    us_status = ForeignKeyField(CodeMaster)
    actual_count = DecimalField(decimal_places=2, max_digits=4)
    predicted_count = DecimalField(decimal_places=2, max_digits=4, null=True)
    drop_count = DecimalField(decimal_places=2, max_digits=4)
    mft_status = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot'


class PVSSlot(BaseModel):
    id = PrimaryKeyField()
    slot_header_id = ForeignKeyField(SlotHeader)
    slot_image_name = CharField(null=False)
    expected_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    pvs_identified_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    robot_drop_count = DecimalField(default=0, decimal_places=2, max_digits=4)
    mfd_status = BooleanField(default=False)
    created_date = DateTimeField(null=False, default=get_current_date_time)
    modified_date = DateTimeField(null=False)
    us_status = ForeignKeyField(CodeMaster)
    device_id = ForeignKeyField(DeviceMaster)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot'


class PVSBatchDrugs(BaseModel):  # stores drug split in batch created by pvs
    id = PrimaryKeyField()
    pvs_slot_id = ForeignKeyField(PVSSlot)
    drug_id = ForeignKeyField(UniqueDrug)
    quantity = DecimalField(decimal_places=2, max_digits=4)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_batch_drugs'


class OldPVSDrugCount(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    unique_drug_id = ForeignKeyField(UniqueDrug, null=True)
    pack_grid_id = ForeignKeyField(PackGrid)
    expected_qty = DecimalField(default=None, null=True)
    predicted_qty = DecimalField(default=None, null=True)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pvs_drug_count"


class PVSDrugCount(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_id = ForeignKeyField(PVSSlot)
    unique_drug_id = ForeignKeyField(UniqueDrug)
    expected_qty = DecimalField(null=True)
    predicted_qty = DecimalField(null=True)
    robot_drop_qty = DecimalField(null=True)
    created_date = DateTimeField(default=get_current_date_time, null=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pvs_drug_count"


class OldPVSSlotDetails(BaseModel):  # entry for every pill dropped
    id = PrimaryKeyField()
    pvs_slot_header_id = ForeignKeyField(PVSSlot)
    label_drug_id = ForeignKeyField(UniqueDrug, null=True,
                                    related_name='remote_tech_drug_label')  # sent by remote tech.
    crop_image = CharField(null=True)
    # predicted_ndc = CharField(null=True)  # fndc, txr -> unique drug id
    predicted_label_drug_id = ForeignKeyField(UniqueDrug, null=True, related_name='pvs_drug_label')  # sent by pvs
    pvs_classification_status = SmallIntegerField(null=True)
    pill_centre_x = FloatField(null=True)
    pill_centre_y = FloatField(null=True)
    radius = FloatField(null=True)
    # 0 = not matched, 1 = matched, 2 = not sure and 3 = extra pill
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot_details'


class PVSSlotDetails(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_id = ForeignKeyField(PVSSlot)
    crop_image_name = CharField(null=False)
    predicted_label_drug_id = ForeignKeyField(UniqueDrug, null=False)
    pvs_classification_status = ForeignKeyField(CodeMaster, null=True)
    pill_centre_x = FloatField(null=True)
    pill_centre_y = FloatField(null=True)
    radius = FloatField(null=True)
    created_date = DateTimeField(null=False, default=get_current_date_time)
    modified_date = DateTimeField(null=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot_details'


class PvsSlotImageDimension(BaseModel):
    id = PrimaryKeyField()
    company_id = SmallIntegerField(null=False)
    device_id = ForeignKeyField(DeviceMaster)
    quadrant = SmallIntegerField(default=0)
    left_value = IntegerField(default=0)
    right_value = IntegerField(default=1280)
    top_value = IntegerField(default=0)
    bottom_value = IntegerField(default=720)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pvs_slot_image_dimension"


class PvsDimension(BaseModel):
    id = PrimaryKeyField()
    company_id = SmallIntegerField()
    device_id = ForeignKeyField(DeviceMaster)
    quadrant = SmallIntegerField(default=0)
    left_value = IntegerField(default=0)
    right_value = IntegerField(default=1280)
    top_value = IntegerField(default=0)
    bottom_value = IntegerField(default=720)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pvs_dimension"


class PVSCropDimension(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_details_id = ForeignKeyField(PVSSlotDetails)
    length = DecimalField(decimal_places=3, max_digits=6)
    width = DecimalField(decimal_places=3, max_digits=6)
    depth = DecimalField(decimal_places=3, max_digits=6, null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_crop_dimension'


def add_constants_in_group_master_code_master(db):
    with db.transaction():
        if GroupMaster.table_exists():
            GroupMaster.insert(id=constants.PVS_CLASSIFICATION_STATUS_GROUP_ID, name="PvsClassificationStatus").execute()

        if CodeMaster.table_exists():
            CodeMaster.insert(id=constants.PVS_CLASSIFICATION_STATUS_NOT_MATCHED,
                              group_id=constants.PVS_CLASSIFICATION_STATUS_GROUP_ID,
                              key=constants.PVS_CLASSIFICATION_STATUS_NOT_MATCHED, value="Not Matched").execute()
            CodeMaster.insert(id=constants.PVS_CLASSIFICATION_STATUS_MATCHED,
                              group_id=constants.PVS_CLASSIFICATION_STATUS_GROUP_ID,
                              key=constants.PVS_CLASSIFICATION_STATUS_MATCHED, value="Matched").execute()
            CodeMaster.insert(id=constants.PVS_CLASSIFICATION_STATUS_NOT_SURE,
                              group_id=constants.PVS_CLASSIFICATION_STATUS_GROUP_ID,
                              key=constants.PVS_CLASSIFICATION_STATUS_NOT_SURE, value="Not Sure").execute()
            CodeMaster.insert(id=constants.PVS_CLASSIFICATION_STATUS_EXTRA_PILL,
                              group_id=constants.PVS_CLASSIFICATION_STATUS_GROUP_ID,
                              key=constants.PVS_CLASSIFICATION_STATUS_EXTRA_PILL, value="Extra Pill").execute()
            CodeMaster.insert(id=constants.PVS_CLASSIFICATION_STATUS_PILL_DIMENSION_NOT_REGISTERED,
                              group_id=constants.PVS_CLASSIFICATION_STATUS_GROUP_ID,
                              key=constants.PVS_CLASSIFICATION_STATUS_PILL_DIMENSION_NOT_REGISTERED,
                              value="Pill Dimension not registered").execute()
            CodeMaster.insert(id=constants.PVS_CLASSIFICATION_STATUS_PILL_DIMENSION_CONFUSING,
                              group_id=constants.PVS_CLASSIFICATION_STATUS_GROUP_ID,
                              key=constants.PVS_CLASSIFICATION_STATUS_PILL_DIMENSION_CONFUSING,
                              value="Pill Dimension confusing").execute()
            CodeMaster.insert(id=constants.PVS_CLASSIFICATION_STATUS_PILL_CONFUSION_EXCLAMATION,
                              group_id=constants.PVS_CLASSIFICATION_STATUS_GROUP_ID,
                              key=constants.PVS_CLASSIFICATION_STATUS_PILL_CONFUSION_EXCLAMATION,
                              value="Pill confusion exclamation").execute()
        print('Data Added in GroupMaster, CodeMaster')


def migration_pvs_changes():
    init_db(db, 'database_migration')
    if OldPVSPack.table_exists():
        db.drop_tables([OldPVSPack])
        print("Table dropped: PVSPack")
    if OldPVSSlot.table_exists():
        db.drop_tables([OldPVSSlot])
        print("Table dropped: PVSSlot")
    if PVSBatchDrugs.table_exists():
        db.drop_tables([PVSBatchDrugs])
        print("Table dropped: PVSBatchDrugs")
    if OldPVSDrugCount.table_exists():
        db.drop_tables([OldPVSDrugCount])
        print("Table dropped: PVSDrugCount")

    if OldPVSSlotDetails.table_exists():
        db.drop_tables([OldPVSSlotDetails])
        print("Table dropped: PVSSlotDetails")

    if PvsSlotImageDimension.table_exists():
        db.drop_tables([PvsSlotImageDimension])
        print("Table dropped: PvsSlotImageDimension")

    db.create_tables([PVSSlot, PVSDrugCount, PVSSlotDetails, PvsDimension], safe=True)
    print("Tables Created: PVSDrugCount,PVSSlot,PVSSlotDetails,PVSDimension")

    add_constants_in_group_master_code_master(db)


if __name__ == '__main__':
    migration_pvs_changes()
