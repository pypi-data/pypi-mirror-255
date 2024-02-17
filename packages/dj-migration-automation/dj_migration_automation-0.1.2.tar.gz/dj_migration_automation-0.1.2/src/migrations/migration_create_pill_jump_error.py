from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_pill_fill_error import PillJumpError


def migration_create_pill_jump_error():
    init_db(db, 'database_migration')
    if not PillJumpError.table_exists():
        db.create_tables([PillJumpError], safe=True)
        print('Table(s) created: PackFillJumpError')


if __name__ == "__main__":
    migration_create_pill_jump_error()
