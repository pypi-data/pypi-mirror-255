from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_consumable_sent_data import ConsumableSentData


def migration_create_table_consumable_sent_data():
    init_db(db, 'database_migration')
    if not ConsumableSentData.table_exists():
        db.create_tables([ConsumableSentData], safe=True)
        print('Table(s) created: ConsumableSentData')


if __name__ == "__main__":
    migration_create_table_consumable_sent_data()
