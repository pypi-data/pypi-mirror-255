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


class OldFacilityDistributionMaster(BaseModel):
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

class FacilityDistributionMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = SmallIntegerField()
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    status_id = ForeignKeyField(CodeMaster, null= True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_distribution_master"


def migrate_facility_distribution_status():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if FacilityDistributionMaster.table_exists():
        migrate(
            migrator.drop_column(OldFacilityDistributionMaster._meta.db_table,
                                 OldFacilityDistributionMaster.status_id.db_column))

        migrate(
            migrator.add_column(FacilityDistributionMaster._meta.db_table,
                                FacilityDistributionMaster.status_id.db_column,
                                FacilityDistributionMaster.status_id)
        )
        print("status column updated")

    with db.transaction():
        facility_distribution_group = GroupMaster.create(**{'id': 13, 'name': 'FacilityDistributionStatus'})
        CodeMaster.create(**{'id': 56, 'key': 56, 'value': 'Pending', 'group_id': facility_distribution_group.id})
        CodeMaster.create(**{'id': 57, 'key': 57, 'value': 'Batch Distribution Done', 'group_id': facility_distribution_group.id})

        print('Tables Modified: GroupMaster, CodeMaster')

if __name__ == "__main__":
    migrate_facility_distribution_status()
