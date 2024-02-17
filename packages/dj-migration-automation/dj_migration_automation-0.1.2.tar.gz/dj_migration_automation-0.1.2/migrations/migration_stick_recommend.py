from collections import defaultdict
from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class DrugMaster(BaseModel):
    """
        @class: drug_master.py
        @createdBy: Manish Agarwal
        @createdDate: 04/19/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/19/2016
        @type: file
        @desc: logical class for table drug_master
    """
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
    drug_form = CharField(null=True, max_length=15)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()
    formatted_ndc = CharField()
    txr = CharField(null=True)
    drug_id = ForeignKeyField(DrugMaster)
    # one of the drug id which has same formatted ndc and txr number
    #  TODO think only drug id or (formatted_ndc, txr)

    class Meta:
        indexes = (
            (('formatted_ndc', 'txr'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class SmallCanisterStick(BaseModel):
    """
    It contain the data related to small canister sticks.
    """
    id = PrimaryKeyField()
    length = DecimalField(decimal_places=3, max_digits=6)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'small_canister_stick'


class BigCanisterStick(BaseModel):
    """
    It contain the data related to big canister sticks.
    """
    id = PrimaryKeyField()
    width = DecimalField(decimal_places=3, max_digits=6)
    depth = DecimalField(decimal_places=3, max_digits=6)
    serial_number = CharField(unique=True, max_length=10)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'big_canister_stick'


class CustomDrugShape(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50, unique=True)
    image_name = CharField(max_length=55, null=True)
    help_video_name = CharField(max_length=55, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'custom_drug_shape'


class DrugDimension(BaseModel):
    """
    It contain the data related to drug dimensions.
    """
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True)
    width = DecimalField(decimal_places=3, max_digits=6)  # in mm
    length = DecimalField(decimal_places=3, max_digits=6)  # in mm
    depth = DecimalField(decimal_places=3, max_digits=6)  # in mm
    fillet = DecimalField(decimal_places=3, max_digits=6, null=True)
    approx_volume = DecimalField(decimal_places=6, max_digits=10)  # in mm^3
    # approx_volume must be calculated using length*width*depth on every insert and update
    accurate_volume = DecimalField(decimal_places=6, max_digits=10, null=True)  # in mm^3  # provided by user
    shape = ForeignKeyField(CustomDrugShape, null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)
    verified = BooleanField(default=True)
    verified_by = IntegerField(default=None, null=True)  # verification needs to be done by second pharmacy tech.
    verified_date = DateTimeField(default=None, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension'


class SkipStickRecommendation(BaseModel):
    """
    Stores the recommendation if it was over written by the dosepack admin
    """
    id = PrimaryKeyField()
    drug_dimension_id = ForeignKeyField(DrugDimension)
    recommended_small_stick_id = ForeignKeyField(SmallCanisterStick)
    used_small_stick_id = ForeignKeyField(SmallCanisterStick, related_name="used_small_stick")
    recommended_big_stick_id = ForeignKeyField(BigCanisterStick)
    used_big_stick_id = ForeignKeyField(BigCanisterStick, related_name="used_big_stick")
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'skip_stick_recommendation'


def migrate_stick_recommendation():
    init_db(db, "database_migration")

    if SkipStickRecommendation.table_exists():
        db.drop_tables([SkipStickRecommendation])

    db.create_tables([SkipStickRecommendation])
    print('Table Created: SkipStickRecommendation')

if __name__ == '__main__':
    migrate_stick_recommendation()