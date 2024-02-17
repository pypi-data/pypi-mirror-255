from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_rts_slot_assign_info import RtsSlotAssignInfo


def migration_create_table_rts_slot_assign_info():
    init_db(db, 'database_migration')
    if not RtsSlotAssignInfo.table_exists():
        db.create_tables([RtsSlotAssignInfo], safe=True)
        print('Table(s) created: RtsSlotAssignInfo')


if __name__ == "__main__":
    migration_create_table_rts_slot_assign_info()
