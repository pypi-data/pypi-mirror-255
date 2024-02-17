from peewee import PrimaryKeyField, IntegerField, ForeignKeyField, DateTimeField, SmallIntegerField, BooleanField, \
    CharField, DateField
from playhouse.migrate import MySQLMigrator, migrate

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_code_master import CodeMaster
from src.model.model_file_header import FileHeader
from src.model.model_patient_master import PatientMaster
from src.model.model_temp_slot_info import TempSlotInfo


class TemplateMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)
    patient_id = ForeignKeyField(PatientMaster, related_name="patient_id")
    file_id = ForeignKeyField(FileHeader, related_name="file_id")
    status = ForeignKeyField(CodeMaster, related_name="status")
    is_modified = SmallIntegerField()
    delivery_datetime = DateTimeField(null=True, default=None)
    fill_manual = BooleanField(default=False)  # for marking packs manual generated from template
    task_id = CharField(max_length=155, null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    reason = CharField(max_length=255, null=True)
    with_autoprocess = BooleanField(default=False)
    fill_start_date = DateField(null=True)
    fill_end_date = DateField(null=True)
    pharmacy_fill_id = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"


def add_column(migrator):
    if TemplateMaster.table_exists():
        migrate(
            migrator.add_column(TemplateMaster._meta.db_table,
                                TemplateMaster.fill_start_date.db_column,
                                TemplateMaster.fill_start_date)
        )
        migrate(
            migrator.add_column(TemplateMaster._meta.db_table,
                                TemplateMaster.fill_end_date.db_column,
                                TemplateMaster.fill_end_date)
        )
        migrate(
            migrator.add_column(TemplateMaster._meta.db_table,
                                TemplateMaster.pharmacy_fill_id.db_column,
                                TemplateMaster.pharmacy_fill_id)
        )
        print("Added columns in TemplateMaster")


def update_data():
    query = TempSlotInfo.select(TemplateMaster.id, TempSlotInfo.fill_start_date, TempSlotInfo.fill_end_date,
                                TempSlotInfo.pharmacy_fill_id).dicts()\
        .join(TemplateMaster, on=((TempSlotInfo.patient_id == TemplateMaster.patient_id) &
                                  (TempSlotInfo.file_id == TemplateMaster.file_id)))\
        .group_by(TempSlotInfo.patient_id, TempSlotInfo.file_id)

    for template in query:
        update_flag = TemplateMaster.update(pharmacy_fill_id=template["pharmacy_fill_id"],
                                            fill_start_date=template["fill_start_date"],
                                            fill_end_date=template["fill_end_date"])\
            .where(TemplateMaster.id == template["id"]).execute()
        print("TemplateID: {} updated from TempSlotInfo. Update Status: {}".format(template["id"], update_flag))


def migration_template_master_redesign_add_columns():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    # Add New column in ext_pack_details table
    add_column(migrator)

    # Update data from TempSlotInfo to TemplateMaster
    update_data()


if __name__ == "__main__":
    migration_template_master_redesign_add_columns()
