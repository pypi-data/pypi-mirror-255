from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
import settings
import logging

logger = logging.getLogger("root")


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


def migrate_84():
    init_db(db, "database_migration")
    with db.transaction():
        try:
            CodeMaster.update(value='Queued').where(CodeMaster.id == settings.PENDING_FILE_STATUS).execute()
            print('Table(s) Updated: CodeMaster')
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)


if __name__ == '__main__':
    migrate_84()
