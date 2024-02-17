from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'group_master'


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


def data_insertion_in_group_master_and_code_master_for_product_status():
    init_db(db, 'database_migration')

    if GroupMaster.table_exists():
        GroupMaster.insert(id=settings.PRODUCT_STATUS, name='ProductStatus').execute()
    if CodeMaster.table_exists():
        CodeMaster.insert(id=settings.PRODUCT_STATUS_BROKEN, group_id=settings.PRODUCT_STATUS,
                          value='Product Status Broken').execute()
        CodeMaster.insert(id=settings.PRODUCT_TESTING_PENDING, group_id=settings.PRODUCT_STATUS,
                          value='Product Testing Pending').execute()
        CodeMaster.insert(id=settings.PRODUCT_STATUS_TRANSFER_PENDING, group_id=settings.PRODUCT_STATUS,
                          value='Product Transfer Pending').execute()
        CodeMaster.insert(id=settings.PRODUCT_STATUS_DONE, group_id=settings.PRODUCT_STATUS, value='Done').execute()
    print("Insertion in Group Master and Code Master completed.")


if __name__ == "__main__":
    data_insertion_in_group_master_and_code_master_for_product_status()
