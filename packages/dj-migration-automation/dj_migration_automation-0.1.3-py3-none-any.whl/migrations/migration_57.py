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


    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "company_setting"
        indexes = (
            (('company_id', 'name'), True),
            # keep trailing comma as suggested by peewee doc # unique setting per company
        )


def migrate_57():
    init_db(db, "database_migration")
    company_id = 3
    user_id = 1
    name = 'PACK_FILL_SYSTEM_AUTO_PRINT'
    value = 0
    CompanySetting.get_or_create(
        company_id=company_id,
        name=name,
        defaults={
            'value': str(value),
            'created_by': user_id,
            'modified_by': user_id,
        })
    print('Table(s) Updated: CompanySetting')


if __name__ == '__main__':
    migrate_57()
