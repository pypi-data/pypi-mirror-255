from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings
from datetime import timedelta

class FacilitySchedule(BaseModel):
    id = PrimaryKeyField()
    # fill_cycle = ForeignKeyField(CodeMaster)  # 46=Weekly, 47=Bi-weekly, 48=monthly(28 days) and 49=other
    week_day = IntegerField(null=True)  # 0=Monday, 1=Tuesday, .. 5=Saturday, 6=Sunday
    days = IntegerField(null=True)  # scheduled after every n days
    start_date = DateTimeField(null=True)  # start date for schedule
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'facility_schedule'


class PatientSchedule(BaseModel):
    id = PrimaryKeyField()
    # facility_id = ForeignKeyField(FacilityMaster)
    # patient_id = ForeignKeyField(PatientMaster)
    schedule_id = ForeignKeyField(FacilitySchedule, null=True)
    total_packs = IntegerField()
    delivery_date_offset = SmallIntegerField(null=True, default=None)
    active = BooleanField(default=True)
    last_import_date = DateTimeField(default=get_current_date_time)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('facility_id', 'patient_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'patient_schedule'

def migrate_45():

    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)
    query = FacilitySchedule.select(FacilitySchedule.id).where(FacilitySchedule.week_day.is_null(False))
    facility_schedule_ids = list()
    for record in query:
        facility_schedule_ids.append(record.id)
    print(facility_schedule_ids)
    PatientSchedule.update({PatientSchedule.schedule_id: None}).where(
        PatientSchedule.schedule_id << facility_schedule_ids).execute()
    FacilitySchedule.delete().where(FacilitySchedule.id << facility_schedule_ids).execute()
    migrate(
        migrator.add_column(
            PatientSchedule._meta.db_table,
            PatientSchedule.delivery_date_offset.db_column,
            PatientSchedule.delivery_date_offset
        ),
        migrator.add_column(
            PatientSchedule._meta.db_table,
            PatientSchedule.active.db_column,
            PatientSchedule.active
        ),
        migrator.add_column(
            PatientSchedule._meta.db_table,
            PatientSchedule.last_import_date.db_column,
            PatientSchedule.last_import_date
        ),
        migrator.drop_column(
            FacilitySchedule._meta.db_table,
            FacilitySchedule.week_day.db_column
        )
    )
    PatientSchedule.update({PatientSchedule.last_import_date: fn.CONVERT_TZ(PatientSchedule.modified_date, '+00:00', '-08:00')}).execute()
    print('Table(s) modified: PatientSchedule, FacilitySchedule')


if __name__ == '__main__':
    migrate_45()