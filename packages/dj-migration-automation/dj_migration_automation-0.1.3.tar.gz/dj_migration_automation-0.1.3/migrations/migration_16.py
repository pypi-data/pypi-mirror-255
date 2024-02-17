import json
import base64
from dosepack.base_model.base_model import db, BaseModel
from playhouse.migrate import *
import settings
import datetime


class DrugMaster(BaseModel):
    id = PrimaryKeyField()
    drug_name = CharField(max_length=255)
    ndc = CharField(max_length=14, unique=True)
    formatted_ndc = CharField(max_length=12, null=True)
    strength = CharField(max_length=50)
    strength_value = CharField(max_length=16)
    manufacturer = CharField(null=True, max_length=100)
    txr = CharField(max_length=8, null=True)
    imprint = CharField(null=True, max_length=82)
    color = CharField(null=True, max_length=30)
    shape = CharField(null=True, max_length=30)
    image_name = CharField(null=True, max_length=255)
    brand_flag = CharField(null=True, max_length=1)
    brand_drug = CharField(null=True, max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()
    formatted_ndc = CharField()
    txr = CharField(null=True)
    drug_id = ForeignKeyField(DrugMaster)

    class Meta:
        indexes = (
            (('formatted_ndc', 'txr'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class PackDetails(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        db_table = 'pack_details'


class RobotMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        db_table = 'robot_master'


class PVSPack(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    robot_id = ForeignKeyField(RobotMaster)
    mft_status = BooleanField()
    user_station_status = BooleanField()
    deleted = BooleanField()
    created_date = DateTimeField()
    modified_date = DateTimeField()
    created_by = IntegerField()
    modified_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_pack'


class SlotHeader(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        db_table = 'slot_header'


class PVSSlot(BaseModel):
    id = PrimaryKeyField()
    pvs_pack_id = ForeignKeyField(PVSPack)
    batch_id = SmallIntegerField()
    slot_header_id = ForeignKeyField(SlotHeader)
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


class PVSBatchDrugs(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_id = ForeignKeyField(PVSSlot)
    drug_id = ForeignKeyField(UniqueDrug)
    quantity = DecimalField(decimal_places=2, max_digits=4)
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_batch_drugs'


class PVSSlotDetails(BaseModel):
    id = PrimaryKeyField()
    pvs_slot_header_id = ForeignKeyField(PVSSlot)
    label_drug_id = ForeignKeyField(UniqueDrug, null=True)
    crop_image = CharField(null=True)
    predicted_ndc = CharField(null=True)
    pvs_match = BooleanField(default=False)
    created_date = DateTimeField()
    modified_date = DateTimeField()
    created_by = IntegerField()
    modified_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot_details'


class DrugTraining(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    status = BooleanField()
    image_crops_count = IntegerField()
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_training'


class TechnicianPack(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    technician_id = IntegerField()
    pvs_pack_id = ForeignKeyField(PVSPack)
    verified_pills = DecimalField(decimal_places=2, max_digits=5)
    total_pills = DecimalField(decimal_places=2, max_digits=5, default=0)
    verification_status = BooleanField(default=False)
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    verification_time = SmallIntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()
    created_by = IntegerField()
    modified_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_pack'


class TechnicianSlot(BaseModel):
    id = PrimaryKeyField()
    pvs_sh_id = ForeignKeyField(PVSSlot)
    technician_id = IntegerField()
    verified = SmallIntegerField()
    created_date = DateTimeField()
    modified_date = DateTimeField()
    created_by = IntegerField()
    modified_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_slot_header'


class TechnicianSlotDetails(BaseModel):
    id = PrimaryKeyField()
    pvs_sd_id = ForeignKeyField(PVSSlotDetails)
    technician_id = IntegerField()
    technician_ndc = CharField()
    original_ndc_match = BooleanField()
    pvs_ndc_match = BooleanField()
    created_date = DateTimeField()
    modified_date = DateTimeField()
    created_by = IntegerField()
    modified_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_slot_details'


def migrate_16():
    json_file = open('config.json', "r")
    data = json.load(json_file)
    json_file.close()

    # Here database_migration is the key for the db engine present in
    # config.json file

    try:
        database = data["database_migration"]["db"]
        username = base64.b64decode(data["database_migration"]["user"])
        password = base64.b64decode(data["database_migration"]["passwd"])
        host = data["database_migration"]["host"]
        port = 3306
    except Exception as ex:
        raise Exception("Incorrect Value for db engine")

    db.init(database, user=username, password=password, host=host, port=port)

    db.create_tables([UniqueDrug, PVSPack, PVSSlot, PVSBatchDrugs,
                      PVSSlotDetails, DrugTraining, TechnicianPack,
                      TechnicianSlot, TechnicianSlotDetails], safe=True)
    print("Table(s) Created: UniqueDrug, PVSPack, PVSSlot, "
          "PVSBatchDrugs, PVSSlotDetails, DrugTraining, TechnicianPack, "
          "TechnicianSlot, TechnicianSlotDetails")

    print('Updating Table(s): UniqueDrug')
    unique_drug_list = list()
    for record in DrugMaster.select(DrugMaster.id.alias('drug_id'),
                                    DrugMaster.formatted_ndc,
                                    DrugMaster.txr).dicts()\
            .group_by(DrugMaster.formatted_ndc, DrugMaster.txr):
        unique_drug_list.append(record)
        if len(unique_drug_list) == 1000:
            BaseModel.db_create_multi_record(unique_drug_list, UniqueDrug)
            print(".")
            unique_drug_list = list()
    if unique_drug_list:
        BaseModel.db_create_multi_record(unique_drug_list, UniqueDrug)
    print('Table(s) Modified: UniqueDrug')
