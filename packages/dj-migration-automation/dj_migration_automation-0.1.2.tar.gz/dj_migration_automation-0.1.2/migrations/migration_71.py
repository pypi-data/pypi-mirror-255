from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class CustomDrugShape(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50, unique=True)
    image_name = CharField(max_length=55, null=True)
    help_video_name = CharField(max_length=55, null=True)
    is_deleted = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'custom_drug_shape'


class DrugShapeFields(BaseModel):
    id = PrimaryKeyField()
    custom_shape_id = ForeignKeyField(CustomDrugShape)
    field_name = CharField()
    label_name = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_shape_fields'


def insert_custom_drug_shape_fileds():
    """

    @return:
    """
    CustomDrugShape.create(name="Other Shape", image_name="other.png", help_video_name="other.mp4", is_deleted=0)
    print('column added')


def insert_drug_shape_fields(custom_shape_id):
    """
    Function to include the starting values in the db
    :return:
    """
    DrugShapeFields.create(custom_shape_id=custom_shape_id, field_name="depth", label_name="Diameter")
    DrugShapeFields.create(custom_shape_id=custom_shape_id, field_name="width", label_name="Width")
    DrugShapeFields.create(custom_shape_id=custom_shape_id, field_name="length", label_name="Length")
    DrugShapeFields.create(custom_shape_id=custom_shape_id, field_name="fillet", label_name="Depth at Edge")

    print('drug shape added')


def migrate_71():
    init_db(db, 'database_migration')

    with db.transaction():
        insert_custom_drug_shape_fileds()
        custom_other_id = CustomDrugShape.select(CustomDrugShape.id).where(CustomDrugShape.name == "Other Shape").get()
        insert_drug_shape_fields(custom_other_id.id)


if __name__ == '__main__':
    migrate_71()
