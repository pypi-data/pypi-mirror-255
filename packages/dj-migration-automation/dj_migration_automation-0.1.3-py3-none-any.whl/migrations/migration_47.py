from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


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
    SLOT_COUNT_THRESHOLD = 'SLOT_COUNT_THRESHOLD'
    template_setting_converter_and_default = {
        # dict to maintain type and default of template settings
        SLOT_COUNT_THRESHOLD: (int, 10)
    }

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "company_setting"
        indexes = (
            (('company_id', 'name'), True),
            # keep trailing comma as suggested by peewee doc # unique setting per company
        )

def migrate_47():
    init_db(db, "database_migration")
    company_id = 3
    user_id = 1
    for name, value in CompanySetting.template_setting_converter_and_default.items():
        # insert if not present, do not override it
        CompanySetting.get_or_create(
            company_id=company_id,
            name=name,
            defaults={
                'value': str(value[1]),
                'created_by': user_id,
                'modified_by': user_id,
            })
    print('Settings changed.')

if __name__ == '__main__':
    migrate_47()
