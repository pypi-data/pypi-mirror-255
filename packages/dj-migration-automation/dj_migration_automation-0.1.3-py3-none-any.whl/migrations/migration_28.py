from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
from src.model.model_patient_master import PatientMaster
from playhouse.migrate import *
import settings

class UniqueDrug(BaseModel):
    id = PrimaryKeyField()
    formatted_ndc = CharField()
    txr = CharField(null=True)
    # drug_id = ForeignKeyField(DrugMaster)
    # one of the drug id which has same formatted ndc and txr number
    #  TODO think only drug id or (formatted_ndc, txr)

    class Meta:
        indexes = (
            (('formatted_ndc', 'txr'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class PVSSlotDetails(BaseModel):  # entry for every pill dropped
    id = PrimaryKeyField()
    # pvs_slot_header_id = ForeignKeyField(PVSSlot)
    # label_drug_id = ForeignKeyField(UniqueDrug, null=True)  # sent by remote tech.
    crop_image = CharField(null=True)
    predicted_ndc = CharField(null=True)  # fndc, txr -> unique drug id
    pvs_match = BooleanField(default=False)  # original ndc == predicted ndc  # sent by pvs
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot_details'


class NewPVSSlotDetails(BaseModel):  # entry for every pill dropped
    id = PrimaryKeyField()
    # pvs_slot_header_id = ForeignKeyField(PVSSlot)
    # label_drug_id = ForeignKeyField(UniqueDrug, null=True,
    #                                 related_name='remote_tech_drug_label')  # sent by remote tech.
    crop_image = CharField(null=True)
    predicted_label_drug_id = ForeignKeyField(UniqueDrug, null=True, related_name='pvs_drug_label')  # sent by pvs
    pvs_classification_status = SmallIntegerField(null=True)  # 0 for not matched, 1 for matched and 2 for not sure
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'pvs_slot_details'


def migrate_28():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if PVSSlotDetails.table_exists():
        migrate(
            migrator.drop_column(
                PVSSlotDetails._meta.db_table,
                PVSSlotDetails.pvs_match.db_column
            ),
            migrator.drop_column(
                PVSSlotDetails._meta.db_table,
                PVSSlotDetails.predicted_ndc.db_column
            )
        )
        migrate(
            migrator.add_column(
                NewPVSSlotDetails._meta.db_table,
                NewPVSSlotDetails.predicted_label_drug_id.db_column,
                NewPVSSlotDetails.predicted_label_drug_id
            ),
            migrator.add_column(
                NewPVSSlotDetails._meta.db_table,
                NewPVSSlotDetails.pvs_classification_status.db_column,
                NewPVSSlotDetails.pvs_classification_status
            )
        )
        print("Table Modified: PVSSlotDetails")

if __name__ == "__main__":
    migrate_28()


