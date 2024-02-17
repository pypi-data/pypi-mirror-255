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
    """
    It contain the data related to drug dimensions.
    """
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True)
    width = DecimalField(decimal_places=3, max_digits=6)
    length = DecimalField(decimal_places=3, max_digits=6)
    depth = DecimalField(decimal_places=3, max_digits=6)
    fillet = DecimalField(decimal_places=3, max_digits=6, null=True)
    approx_volume = DecimalField(decimal_places=3, max_digits=6)
    accurate_volume = DecimalField(decimal_places=3, max_digits=6, null=True)
    shape = CharField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension'


class CanisterStickDimension(BaseModel):
    """
    It contain the data related to canister sticks.
    """
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


def migrate_18():
    init_db(db, 'database_migration')

    db.create_tables([DrugDimension, CanisterStickDimension], safe=True)
    print("Tables created: DrugDimension, CanisterStickDimension")
