from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from model.model_user_interaction import UserSession, UserSessionMeta, \
    UserSessionInteractionTracker, ModuleTypeMaster
from dosepack.utilities.utils import get_current_date_time
import settings

def migrate_63(drop_tables=False):
    init_db(db, "database_migration")

    if drop_tables:
        print ("dropping tables")
        db.drop_tables([ModuleTypeMaster, UserSession, UserSessionMeta,
                        UserSessionInteractionTracker])
    db.create_tables([ModuleTypeMaster, UserSession, UserSessionMeta, UserSessionInteractionTracker], safe=True)
    print('Table(s) Created: ModuleTypeMaster, UserSession, UserSessionMeta, UserSessionInteractionTracker')

    default_idle_time = 30
    default_expected_seconds = None

    try:
        module_type_init_data = [
            {
                "id": 1,
                "name": "Drug Dispensing Template",
                "record_screen_interaction": True,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 1
            },
            {
                "id": 2,
                "name": "Create Batch",
                "record_screen_interaction": True,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 1
            },
            {
                "id": 3,
                "name": "Alternate Drugs",
                "record_screen_interaction": True,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 1
            },
            {
                "id": 4,
                "name": "Advance Pre-processing",
                "record_screen_interaction": True,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 1
            },
            {
                "id": 5,
                "name": "Canister Recommendation",
                "record_screen_interaction": False,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 1
            },
            {
                "id": 6,
                "name": "Replenish Canister",
                "record_screen_interaction": False,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 1
            },
            {
                "id": 7,
                "name": "Import Packs",
                "record_screen_interaction": True,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 1
            },
            {
                "id": 8,
                "name": "Manual Verification Screen",
                "record_screen_interaction": True,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 2
            },
            {
                "id": 10,
                "name": "Robot Replenish Canisters",
                "record_screen_interaction": False,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 2
            },
            {
                "id": 11,
                "name": "Pack Separator Refill",
                "record_screen_interaction": False,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 2
            },
            {
                "id": 12,
                "name": "Machine Error Management",
                "record_screen_interaction": False,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 2
            },
            {
                "id": 13,
                "name": "Label Refills",
                "record_screen_interaction": False,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 2
            },
            {
                "id": 14,
                "name": "Unloading Station (unloading and stacking)",
                "record_screen_interaction": False,
                "idle_time_seconds": default_idle_time,
                "expected_seconds_per_unit": default_expected_seconds,
                "module_category_id": 2
            },
        ]

        ModuleTypeMaster.insert_many(module_type_init_data).execute()
        print('ModuleTypeMaster initial data inserted')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    migrate_63(False)
