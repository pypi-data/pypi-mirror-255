from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class DrugDimension(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension'


class BigCanisterStick(BaseModel):
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


class CanisterStickDimension(BaseModel):
    id = PrimaryKeyField()
    width = DecimalField(decimal_places=3, max_digits=6)
    depth = DecimalField(decimal_places=3, max_digits=6)
    ral_code = CharField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_stick_dimension'


class SmallCanisterStick(BaseModel):
    id = PrimaryKeyField()
    length = DecimalField(decimal_places=3, max_digits=6)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'small_canister_stick'


class CanisterStick(BaseModel):
    big_canister_stick_id = ForeignKeyField(BigCanisterStick)
    small_canister_stick_id = ForeignKeyField(SmallCanisterStick)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_stick'


class CanisterParameters(BaseModel):
    id = PrimaryKeyField()
    speed = DecimalField(decimal_places=3, max_digits=6, null=True)  # drum rotate speed
    wait_timeout = DecimalField(decimal_places=3, max_digits=6, null=True)  # sensor wait timeout
    cw_timeout = DecimalField(decimal_places=3, max_digits=6, null=True)  # clockwise
    ccw_timeout = DecimalField(decimal_places=3, max_digits=6, null=True)  # counter clockwise
    drop_timeout = DecimalField(decimal_places=3, max_digits=6, null=True)  # total pill drop timeout
    canister_stick_id = ForeignKeyField(CanisterStick)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_parameters'


class DrugCanisterStickMapping(BaseModel):
    id = PrimaryKeyField()
    drug_dimension_id = ForeignKeyField(DrugDimension)
    canister_stick_id = ForeignKeyField(CanisterStick)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_canister_stick_mapping'


def migrate_21():
    init_db(db, 'database_migration')

    db.create_tables([SmallCanisterStick, BigCanisterStick, CanisterStick,
                      CanisterParameters, DrugCanisterStickMapping], safe=True)
    print("Tables created: SmallCanisterStick, BigCanisterStick"
          ", CanisterStick, CanisterParameters, DrugCanisterStickMapping")

    if CanisterStickDimension.table_exists():
        db.drop_table(CanisterStickDimension)
        print("Tables dropped: CanisterStickDimension")
