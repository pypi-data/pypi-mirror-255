from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
from src.model.model_patient_master import PatientMaster
from playhouse.migrate import *
import settings


class CanisterStick(BaseModel):
    """
    It contains the data related to small and big stick combination
    """
    id = PrimaryKeyField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_stick'


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        indexes = (
            (('formatted_ndc', 'txr'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class OldCanisterParameters(BaseModel):
    """
    It contain the data related to canister parameters and timers to run the canister motors..
    """
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


class CanisterParameters(BaseModel):
    """
    It contain the data related to canister parameters and timers to run the canister motors..
    """
    id = PrimaryKeyField()
    speed = SmallIntegerField(null=True)  # drum rotate speed
    wait_timeout = SmallIntegerField(null=True)  # sensor wait timeout
    cw_timeout = SmallIntegerField(null=True)  # clockwise
    ccw_timeout = SmallIntegerField(null=True)  # counter clockwise
    drop_timeout = SmallIntegerField(null=True)  # total pill drop timeout
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'canister_parameters'


class DrugCanisterParameters(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True)
    canister_parameter_id = ForeignKeyField(CanisterParameters)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)
    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_canister_parameters'


def migrate_31():
    init_db(db, 'database_migration')

    if OldCanisterParameters.table_exists():
        db.drop_tables([OldCanisterParameters])
        print("Table dropped: CanisterParameters")


    db.create_tables([DrugCanisterParameters, CanisterParameters], safe=True)
    print("Table created: DrugCanisterParameters, CanisterParameters")


if __name__ == "__main__":
    migrate_31()


