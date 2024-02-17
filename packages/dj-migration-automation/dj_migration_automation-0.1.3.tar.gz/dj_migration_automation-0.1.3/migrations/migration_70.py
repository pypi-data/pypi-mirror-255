from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from playhouse.migrate import *
import settings


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()
    formatted_ndc = CharField()
    txr = CharField(null=True)
    # drug_id = ForeignKeyField(DrugMaster)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class CustomDrugShape(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'custom_drug_shape'


class OldDrugDimension(BaseModel):
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
    verified = BooleanField(default=False)
    verified_by = IntegerField(default=None, null=True)  # verification needs to be done by second pharmacy tech.
    verified_date = DateTimeField(default=None, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension'


class DrugDimension(BaseModel):
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
    verified = BooleanField(default=False)
    verification_status_id = ForeignKeyField(CodeMaster, default=52)
    verified_by = IntegerField(default=None, null=True)  # verification needs to be done by second pharmacy tech.
    verified_date = DateTimeField(default=None, null=True)
    rejection_note = CharField(default= None, max_length=1000, null = True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension'


def migrate_70():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)

    with db.transaction():
        batch_group = GroupMaster.create(**{'id': 12, 'name': 'DrugVerification'})
        CodeMaster.create(**{'id': 52, 'key': 52, 'value': 'Pending', 'group_id': batch_group.id})
        CodeMaster.create(**{'id': 53, 'key': 53, 'value': 'Verified', 'group_id': batch_group.id})
        CodeMaster.create(**{'id': 54, 'key': 54, 'value': 'Rejected', 'group_id': batch_group.id})
        print('Tables Modified: GroupMaster, CodeMaster')


    migrate(
        migrator.add_column(DrugDimension._meta.db_table,
                            DrugDimension.verification_status_id.db_column,
                            DrugDimension.verification_status_id)
    )

    migrate(
        migrator.add_column(DrugDimension._meta.db_table,
                            DrugDimension.rejection_note.db_column,
                            DrugDimension.rejection_note)
    )

    with db.transaction():
        DrugDimension.update(verification_status_id=53).where(DrugDimension.verified == 1).execute()

    migrate(
        migrator.drop_column(
            DrugDimension._meta.db_table,
            DrugDimension.verified.db_column
        )
    )

    print('Table Modified: DrugDimension')


if __name__ == "__main__":
    migrate_70()
