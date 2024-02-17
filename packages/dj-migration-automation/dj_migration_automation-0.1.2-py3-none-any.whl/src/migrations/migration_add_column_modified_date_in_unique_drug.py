import settings
from playhouse.migrate import *

from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from src.model.model_code_master import CodeMaster
from src.model.model_dosage_type import DosageType
from src.model.model_drug_master import DrugMaster


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()
    formatted_ndc = CharField()
    txr = CharField(null=True)
    drug_id = ForeignKeyField(DrugMaster, related_name='drug_id')
    lower_level = BooleanField(default=False)  # drug to be kept at lower level so pill doesn't break while filling
    drug_usage = ForeignKeyField(CodeMaster, default=settings.CANISTER_DRUG_USAGE["Slow Moving"], related_name='drug_usage')
    is_powder_pill = IntegerField(null=True)
    dosage_type = ForeignKeyField(DosageType, null=True, default=None, related_name='drug_dosage_type')
    packaging_type = ForeignKeyField(CodeMaster, null=True, default=None, related_name='drug_packaging_type')
    coating_type = CharField(null=True)
    is_zip_lock_drug = IntegerField(null=True)
    is_delicate = BooleanField(default=False)
    unit_weight = DecimalField(null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)

    class Meta:
        indexes = (
            (('formatted_ndc', 'txr'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


def add_modified_date_in_unique_drug():

    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        with db.transaction():
            if UniqueDrug.table_exists():
                migrate(migrator.add_column(UniqueDrug._meta.db_table,
                                            UniqueDrug.modified_date.db_column,
                                            UniqueDrug.modified_date
                                            )
                        )

                print("Added modified_date column in unique_drug")

    except Exception as e:
        settings.logger.error("Error while add or updated modified_date column in unique_drug: ", str(e))


if __name__ == "__main__":
    add_modified_date_in_unique_drug()
