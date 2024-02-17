from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


class FacilityMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "facility_master"


class PatientMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_master"


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


class FacilitySchedule(BaseModel):
    id = PrimaryKeyField()
    fill_cycle = ForeignKeyField(CodeMaster)  # 46=Weekly, 47=Bi-weekly, 48=monthly(28 days) and 49=other
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
    facility_id = ForeignKeyField(FacilityMaster)
    patient_id = ForeignKeyField(PatientMaster)
    schedule_id = ForeignKeyField(FacilitySchedule, null=True)
    total_packs = IntegerField()
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        indexes = (
            (('facility_id', 'patient_id'), True),
        )

        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'patient_schedule'


def migrate_40():
    init_db(db, 'database_migration')

    if GroupMaster.table_exists():
        GroupMaster.insert(id=10,name='FacilitySchedule').execute()
    if CodeMaster.table_exists():
        CodeMaster.insert(id=46,group_id=10,key=46,value='Weekly').execute()
        CodeMaster.insert(id=47,group_id=10,key=47,value='Bi-weekly').execute()
        CodeMaster.insert(id=48,group_id=10,key=48,value='Monthly').execute()
        CodeMaster.insert(id=49,group_id=10,key=49,value='Other').execute()

    db.create_tables([PatientSchedule, FacilitySchedule], safe=True)
    print('Table created: PatientSchedule, FacilitySchedule')
