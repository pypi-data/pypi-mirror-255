from playhouse.migrate import *
from collections import defaultdict
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time


class FacilityDistributionMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = SmallIntegerField()
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    status_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_distribution_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


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
    drug_form = CharField(null=True, max_length=15)

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


class PackRxLink(BaseModel):
    id = PrimaryKeyField()
    # patient_rx_id = ForeignKeyField(PatientRx)
    # pack_id = ForeignKeyField(PackDetails)

    # If original_drug_id is null while alternatendcupdate function
    # then store current drug id as original drug id in pack rx link
    # this is required so we can send the flag of ndc change while printing label
    original_drug_id = ForeignKeyField(DrugMaster, null=True)
    bs_drug_id = ForeignKeyField(DrugMaster, null=True, related_name='bs_drug_id') # drug_id selected from batch scheduling logic.
    fill_manually = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_rx_link"


class AlternateDrugOption(BaseModel):
    id = PrimaryKeyField()
    facility_dis_id = ForeignKeyField(FacilityDistributionMaster)
    unique_drug_id = ForeignKeyField(UniqueDrug, related_name='unique_drug_id')
    alternate_unique_drug_id = ForeignKeyField(UniqueDrug, related_name='alternate_unique_drug_id')
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)

    class Meta:
        indexes = (
            (('facility_dis_id', 'unique_drug_id', 'alternate_unique_drug_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "alternate_drug_option"


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


def migrate_batch_distribution_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    db.create_tables([AlternateDrugOption], safe=True)
    print('Table(s) Created: AlternateDrugOption')

    if PackRxLink.table_exists():
        migrate(
            migrator.add_column(
                PackRxLink._meta.db_table,
                PackRxLink.bs_drug_id.db_column,
                PackRxLink.bs_drug_id
            ),
            migrator.add_column(
                PackRxLink._meta.db_table,
                PackRxLink.fill_manually.db_column,
                PackRxLink.fill_manually
            )
        )
        print('Table Modified: PackRxLink')

    if CodeMaster.table_exists():
        CodeMaster.create(**{'id': settings.BATCH_ALTERNATE_DRUG_SAVED,
                             'key': settings.BATCH_ALTERNATE_DRUG_SAVED,
                             'value': 'Alternate Saved',
                             'group_id': settings.GROUP_MASTER_BATCH})

    print("Table modified: CodeMaster")


if __name__ == "__main__":
    migrate_batch_distribution_master()

