from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


class OldTechnicianPack(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    technician_id = IntegerField()
    # pvs_pack_id = ForeignKeyField(PVSPack)
    verified_pills = DecimalField(decimal_places=2, max_digits=5, default=0)
    total_pills = DecimalField(decimal_places=2, max_digits=5, default=0)
    verification_status = BooleanField(default=False)
    start_time = DateTimeField(null=True)  # time for technician
    end_time = DateTimeField(null=True)
    verification_time = SmallIntegerField(null=True)  # total time for verification in seconds
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_pack'


class NewTechnicianPack(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    technician_id = IntegerField()
    # pvs_pack_id = ForeignKeyField(PVSPack)
    verified_pills = DecimalField(decimal_places=2, max_digits=5, default=0)
    total_pills = DecimalField(decimal_places=2, max_digits=5, default=0)
    verification_status = BooleanField(null=True, default=None)
    start_time = DateTimeField(null=True)  # time for technician
    end_time = DateTimeField(null=True)
    verification_time = SmallIntegerField(null=True)  # total time for verification in seconds
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'technician_pack'


def migrate_35():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    if OldTechnicianPack.table_exists():
        migrate(
            migrator.drop_column(
                OldTechnicianPack._meta.db_table,
                OldTechnicianPack.verification_status.db_column,
            ),
            migrator.add_column(
                NewTechnicianPack._meta.db_table,
                NewTechnicianPack.verification_status.db_column,
                NewTechnicianPack.verification_status
            )
        )
        print('table modified: TechnicianPack')