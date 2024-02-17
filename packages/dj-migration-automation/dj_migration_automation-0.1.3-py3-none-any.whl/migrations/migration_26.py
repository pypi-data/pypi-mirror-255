from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
from src.model.model_patient_master import PatientMaster
from playhouse.migrate import *
import settings


class TemplateNote(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster)
    note = TextField(500)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_note"


class PatientNote(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster, unique=True)
    note = CharField(max_length=500)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_note"


def migrate_26():
    init_db(db, 'database_migration')
    query = TemplateNote.select().dicts()
    template_notes = list()
    for record in query:
        template_notes.append(record)
    db.drop_table(TemplateNote, fail_silently=True)
    print("Table Created: TemplateNote")

    db.create_tables([PatientNote], safe=True)
    print("Table Created: PatientNote")
    if template_notes:
        PatientNote.insert_many(template_notes).execute()
        print("Table updated: PatientNote")

if __name__ == "__main__":
    migrate_26()