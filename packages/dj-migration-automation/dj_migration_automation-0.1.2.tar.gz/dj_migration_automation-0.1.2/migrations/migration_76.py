from playhouse.migrate import *
from collections import defaultdict
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time


class CompanySetting(BaseModel):
    """ stores setting for a company """
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField()
    value = CharField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    # Constant for template_settings
    SLOT_VOLUME_THRESHOLD_MARK = 'SLOT_VOLUME_THRESHOLD_MARK'
    SPLIT_STORE_SEPARATE = 'SPLIT_STORE_SEPARATE'
    VOLUME_BASED_TEMPLATE_SPLIT = 'VOLUME_BASED_TEMPLATE_SPLIT'
    COUNT_BASED_TEMPLATE_SPLIT = 'COUNT_BASED_TEMPLATE_SPLIT'
    TEMPLATE_SPLIT_COUNT_THRESHOLD = 'TEMPLATE_SPLIT_COUNT_THRESHOLD'
    SLOT_COUNT_THRESHOLD = 'SLOT_COUNT_THRESHOLD'
    TEMPLATE_AUTO_SAVE = 'TEMPLATE_AUTO_SAVE'

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "company_setting"
        indexes = (
            (('company_id', 'name'), True),
            # keep trailing comma as suggested by peewee doc # unique setting per company
        )


def migrate_76():
    init_db(db, 'database_migration')

    CompanySetting.update(value='0.58').where(CompanySetting.name == "SLOT_VOLUME_THRESHOLD_MARK").execute()

    print("value for SLOT_VOLUME_THRESHOLD_MARK updated")


if __name__ == "__main__":
    migrate_76()
