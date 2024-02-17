from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
from playhouse.migrate import *
import settings


class GenerateCanister(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField()
    ndc = CharField(max_length=14)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)


    class Meta:
            if settings.TABLE_NAMING_CONVENTION == "_":
                db_table = "generate_canister"


def test_migration():
    init_db(db, 'database_t1')

    migrator = MySQLMigrator(db)
    db.create_tables([GenerateCanister], safe=True)
    print("Tables created: GenerateCanister")

if __name__ == "__main__":
    test_migration()
