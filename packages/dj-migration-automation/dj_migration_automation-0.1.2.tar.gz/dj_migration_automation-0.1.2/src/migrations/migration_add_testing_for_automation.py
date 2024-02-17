import settings
from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_code_master import CodeMaster


def testing_migration():
    try:
        init_db(db, 'database_migration')
        if CodeMaster.table_exists():
            CodeMaster.insert(id=settings.TESTING_CODE, group_id=settings.PRODUCT_STATUS,
                              value='Testing Code').execute()
        print("Testing Automation Completed")
    except Exception as e:
        raise e


testing_migration()
