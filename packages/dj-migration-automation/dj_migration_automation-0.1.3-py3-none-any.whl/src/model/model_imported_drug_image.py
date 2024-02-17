from peewee import PrimaryKeyField, ForeignKeyField, CharField, DateTimeField, IntegerField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_drug_master import DrugMaster
from src.model.model_file_header import FileHeader


class ImportedDrugImage(BaseModel):
    id = PrimaryKeyField()
    drug_id = ForeignKeyField(DrugMaster)
    file_id = ForeignKeyField(FileHeader, null=True)
    source = CharField(max_length=500)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "imported_drug_image"


