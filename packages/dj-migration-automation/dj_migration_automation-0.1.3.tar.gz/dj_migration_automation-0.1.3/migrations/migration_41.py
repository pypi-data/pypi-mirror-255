from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        indexes = (
            (('formatted_ndc', 'txr'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class CustomDrugShape(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50, unique=True)
    image_name = CharField(max_length=55, null=True)
    help_video_name = CharField(max_length=55, null=True)
    is_deleted = BooleanField(default=False)

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


class DrugShapeFields(BaseModel):
    id = PrimaryKeyField()
    custom_shape_id = ForeignKeyField(CustomDrugShape)
    field_name = CharField()
    label_name = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_shape_fields'


class MissingStickRecommendation(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    width = DecimalField(decimal_places=3, max_digits=6)  # in mm
    length = DecimalField(decimal_places=3, max_digits=6)  # in mm
    depth = DecimalField(decimal_places=3, max_digits=6)  # in mm
    fillet = DecimalField(decimal_places=3, max_digits=6, null=True)
    shape_id = ForeignKeyField(CustomDrugShape)
    company_id = IntegerField()
    is_manual = BooleanField(default=False)
    image_url = CharField(null=True)
    user_id = IntegerField()
    created_at = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'missing_stick_recommendation'


def insert_drug_shape_fields():
    """
    Function to include the starting values in the db
    :return:
    """
    DrugShapeFields.create(custom_shape_id=1, field_name="depth", label_name="Diameter")
    DrugShapeFields.create(custom_shape_id=1, field_name="length", label_name="Length")
    DrugShapeFields.create(custom_shape_id=2, field_name="depth", label_name="Depth")
    DrugShapeFields.create(custom_shape_id=2, field_name="width", label_name="Width")
    DrugShapeFields.create(custom_shape_id=2, field_name="length", label_name="Length")
    DrugShapeFields.create(custom_shape_id=2, field_name="fillet", label_name="Depth at Edge")
    DrugShapeFields.create(custom_shape_id=4, field_name="depth", label_name="Depth")
    DrugShapeFields.create(custom_shape_id=4, field_name="width", label_name="Width")
    DrugShapeFields.create(custom_shape_id=4, field_name="length", label_name="Length")
    DrugShapeFields.create(custom_shape_id=4, field_name="fillet", label_name="Depth at Edge")
    DrugShapeFields.create(custom_shape_id=5, field_name="length", label_name="Diameter")
    DrugShapeFields.create(custom_shape_id=5, field_name="depth", label_name="Depth")
    DrugShapeFields.create(custom_shape_id=5, field_name="fillet", label_name="Depth at Edge")
    DrugShapeFields.create(custom_shape_id=6, field_name="length", label_name="Diameter")
    DrugShapeFields.create(custom_shape_id=6, field_name="depth", label_name="Depth")


def migrate_41():

    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            CustomDrugShape._meta.db_table,
            CustomDrugShape.image_name.db_column,
            CustomDrugShape.image_name
        ),
        migrator.add_column(
            CustomDrugShape._meta.db_table,
            CustomDrugShape.help_video_name.db_column,
            CustomDrugShape.help_video_name
        ),
        migrator.add_column(
            DrugDimension._meta.db_table,
            DrugDimension.verified.db_column,
            DrugDimension.verified
        ),
        migrator.add_column(
            DrugDimension._meta.db_table,
            DrugDimension.verified_by.db_column,
            DrugDimension.verified_by
        ),
        migrator.add_column(
            DrugDimension._meta.db_table,
            DrugDimension.verified_date.db_column,
            DrugDimension.verified_date
        ),
        migrator.add_column(
            CustomDrugShape._meta.db_table,
            CustomDrugShape.is_deleted.db_column,
            CustomDrugShape.is_deleted
        )
    )
    print('Table(s) Modified: CustomDrugShape, DrugDimension')
    # mark current drug verified by admin
    with db.transaction():
        q = DrugDimension.update(verified_date=DrugDimension.created_date,
                                 verified_by=DrugDimension.created_by,
                                 verified=True)
        q.execute()
        shapes = {item.name: item for item in CustomDrugShape.select()}
        for name, shape in shapes.items():
            shape.image_name = '{}.png'.format(name.replace(' ', '_').lower())
            shape.help_video_name = '{}.mp4'.format(name.replace(' ', '_').lower())
            shape.save()

        db.create_tables([SkipStickRecommendation, DrugShapeFields, MissingStickRecommendation], safe=True)

        insert_drug_shape_fields()


if __name__ == '__main__':
    migrate_41()

