from peewee import (IntegerField, DateTimeField, PrimaryKeyField, CharField, BooleanField, SmallIntegerField,
                    InternalError, IntegrityError)
import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
logger = settings.logger


class NewFillDrug(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)
    formatted_ndc = CharField(max_length=12, null=True)
    txr = CharField(max_length=8, null=True)
    new = BooleanField(default=True)
    packs_filled = SmallIntegerField(default=0)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "new_fill_drug"

    @classmethod
    def db_create_new_fill_drug(cls, drug, company_id):
        try:
            BaseModel.db_create_record({
                'formatted_ndc': drug.formatted_ndc,
                'txr': drug.txr,
                'company_id': company_id
            }, NewFillDrug)  # insert drug, marks it new, if already present don't change status
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise
