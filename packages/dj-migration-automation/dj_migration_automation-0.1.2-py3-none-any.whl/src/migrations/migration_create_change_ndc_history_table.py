from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_change_ndc_history import ChangeNdcHistory


def migration_create_table_change_ndc_history():
    init_db(db, 'database_migration')
    if not ChangeNdcHistory.table_exists():
        db.create_tables([ChangeNdcHistory], safe=True)
        print('Table(s) created: ChangeNdcHistory')


if __name__ == "__main__":
    migration_create_table_change_ndc_history()
