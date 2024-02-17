from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, DecimalField

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_group_master import GroupMaster
from src.model.model_pack_details import PackDetails
from src.model.model_slot_header import SlotHeader

# from src.model.model_pack_verification import PackVerification
# from src.model.model_pack_verification_details import PackVerificationDetails


class PackVerification(BaseModel):

    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    pack_verified_status = ForeignKeyField(CodeMaster)
    created_by = IntegerField(default=1)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_verification"


class PackVerificationDetails(BaseModel):
    id = PrimaryKeyField()
    pack_verification_id = ForeignKeyField(PackVerification)
    slot_header_id = ForeignKeyField(SlotHeader)
    colour_status = ForeignKeyField(CodeMaster)
    compare_quantity = DecimalField(decimal_places=2, max_digits=4)
    dropped_quantity = DecimalField(decimal_places=2, max_digits=4)
    predicted_quantity = DecimalField(decimal_places=2, max_digits=4, null=True)
    created_by = IntegerField(default=1)
    created_date = DateTimeField(null=False, default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_verification_details"




def migration_create_pack_verification_and_pack_verification_details_table():

    try:

        init_db(db, 'database_migration')

        if PackVerification.table_exists():
            db.drop_table(PackVerification)
            print('Table(s) dropped: PackVerification')

        if not PackVerification.table_exists():
            db.create_tables([PackVerification], safe=True)
            print('Table(s) created: PackVerification')

        if not PackVerificationDetails.table_exists():
            db.create_tables([PackVerificationDetails], safe=True)
            print('Table(s) created: PackVerificationDetails')

        if GroupMaster.table_exists():

            GroupMaster.insert(id=constants.PACK_VERIFICATION_STATUS_GROUP_ID,
                               name='PackVerificationStatus').execute()
            print("PACK_VERIFICATION_STATUS_GROUP_ID inserted in GroupMaster")

            GroupMaster.insert(id=constants.SLOT_COLOUR_STATUS_GROUP_ID,
                               name='SlotColourStatus').execute()
            print("SLOT_COLOUR_STATUS_GROUP_ID inserted in GroupMaster")

        if CodeMaster.table_exists():

            CodeMaster.insert(id=constants.PACK_NOT_MONITORED_STATUS,
                              group_id=constants.PACK_VERIFICATION_STATUS_GROUP_ID,
                              value="Pack Not Monitored").execute()
            print("PACK_NOT_MONITORED_STATUS inserted in CodeMaster")

            CodeMaster.insert(id=constants.PACK_MONITORED_STATUS,
                              group_id=constants.PACK_VERIFICATION_STATUS_GROUP_ID,
                              value="Pack Monitored").execute()
            print("PACK_MONITORED_STATUS inserted in CodeMaster")

            CodeMaster.insert(id=constants.PACK_VERIFIED_STATUS,
                              group_id=constants.PACK_VERIFICATION_STATUS_GROUP_ID,
                              value="Pack Verified").execute()
            print("PACK_VERIFIED_STATUS inserted in CodeMaster")

            CodeMaster.insert(id=constants.SLOT_COLOUR_STATUS_RED,
                              group_id=constants.SLOT_COLOUR_STATUS_GROUP_ID,
                              value="Red").execute()
            print("SLOT_COLOUR_STATUS_RED inserted in CodeMaster")

            CodeMaster.insert(id=constants.SLOT_COLOUR_STATUS_GREEN,
                              group_id=constants.SLOT_COLOUR_STATUS_GROUP_ID,
                              value="Green").execute()
            print("SLOT_COLOUR_STATUS_GREEN inserted in CodeMaster")

    except Exception as e:
        print(e)
        raise



if __name__ == "__main__":
    migration_create_pack_verification_and_pack_verification_details_table()

