from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


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


def migrate_38():
    init_db(db, 'database_migration')
    CodeMaster.get_or_create(
        id=45, group_id=1,
        key=settings.PROCESSED_MANUALLY_PACK_STATUS,
        value='Processed Manually'
    )
    print('Table(s) updated: CodeMaster')


if __name__ == '__main__':
    migrate_38()