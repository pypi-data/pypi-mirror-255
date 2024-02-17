from collections import defaultdict
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


class OldDrugDimension(BaseModel):
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
    shape = CharField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension'


class CustomDrugShape(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50, unique=True)

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

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension'


class CanisterParameters(BaseModel):
    """
    It contain the data related to canister parameters and timers to run the canister motors..
    """
    id = PrimaryKeyField()
    speed = IntegerField(null=True)  # drum rotate speed
    wait_timeout = IntegerField(null=True)  # sensor wait timeout  # in ms
    cw_timeout = IntegerField(null=True)  # clockwise # in ms
    ccw_timeout = IntegerField(null=True)  # counter clockwise # in ms
    drop_timeout = IntegerField(null=True)  # total pill drop timeout # in ms
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_parameters'


class CustomShapeCanisterParameters(BaseModel):
    """
    Mapping for drug custom shape and canister parameter
    """
    id = PrimaryKeyField()
    custom_shape_id = ForeignKeyField(CustomDrugShape, unique=True)
    canister_parameter_id = ForeignKeyField(CanisterParameters)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'custom_shape_canister_parameters'


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


class SmallStickCanisterParameters(BaseModel):
    id = PrimaryKeyField()
    small_stick_id = ForeignKeyField(SmallCanisterStick, unique=True)
    canister_parameter_id = ForeignKeyField(CanisterParameters)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'small_stick_canister_parameters'



def migrate_39():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    q = CanisterParameters.select()
    canister_parameters = list(q.dicts())
    print(canister_parameters)  # just in case script fails
    drop_and_add_columns = [
        CanisterParameters.speed,
        CanisterParameters.cw_timeout,
        CanisterParameters.ccw_timeout,
        CanisterParameters.wait_timeout,
        CanisterParameters.drop_timeout,
        CanisterParameters.created_date,
        CanisterParameters.modified_date,
        CanisterParameters.created_by,
        CanisterParameters.modified_by,
    ]
    # dropping as need Integer instead of SmallInteger
    # dropping other fields too to maintain order as table is in initial stage
    for item in drop_and_add_columns:
        migrate(
            migrator.drop_column(
                CanisterParameters._meta.db_table,
                item.db_column
            )
        )
        migrate(
            migrator.add_column(
                CanisterParameters._meta.db_table,
                item.db_column,
                item
            )
        )

    print("Table(s) modified: CanisterParameters")
    for item in canister_parameters:
        item_id = item.pop("id")
        CanisterParameters.update(**item)\
            .where(CanisterParameters.id == item_id)\
            .execute()
    print("Table(s) updated: CanisterParameters")
    db.create_tables([
        CustomDrugShape,
        CustomShapeCanisterParameters,
        SmallStickCanisterParameters
    ], safe=True)
    print("Table(s) created: CustomDrugShape, CustomShapeCanisterParameters, SmallStickCanisterParameters")
    shape_list = ['Round Flat', 'Round Curved', 'Oval', 'Capsule', 'Oblong', 'Elliptical']
    shape_list.sort()
    for item in shape_list:
        CustomDrugShape.get_or_create(name=item)
    shape_dict = dict()
    for record in CustomDrugShape.select():
        shape_dict[record.name] = record.id
    print("Table(s) updated: CustomDrugShape")

    temp_shape_col = 'temp_shape'
    query = OldDrugDimension.select(OldDrugDimension.id, OldDrugDimension.shape)\
        .where(OldDrugDimension.shape.is_null(False))
    temp_shape_data = list(query)
    migrate(migrator.rename_column(
        DrugDimension._meta.db_table,
        'shape',
        temp_shape_col
    ))
    migrate(
        migrator.add_column(
            DrugDimension._meta.db_table,
            DrugDimension.shape.db_column,
            DrugDimension.shape
        )
    )
    update_dict = defaultdict(list)
    for item in temp_shape_data:
        try:
            update_dict[shape_dict[item.shape]].append(item.id)
        except KeyError as e:
            print('Shape missing from custom_drug_shape {}'.format(item.shape))
    with db.transaction():
        for k, v in update_dict.items():
            DrugDimension.update(shape=k).where(DrugDimension.id << v).execute()
        print("Table(s) updated: DrugDimension")
    migrate(
        migrator.drop_column(
            DrugDimension._meta.db_table,
            temp_shape_col
        )
    )


if __name__ == '__main__':
    migrate_39()
