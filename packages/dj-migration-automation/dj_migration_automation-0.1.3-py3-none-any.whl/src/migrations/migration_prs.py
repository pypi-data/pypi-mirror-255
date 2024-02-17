from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants


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


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'unique_drug'


class PRSDrugDetails(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    status = ForeignKeyField(CodeMaster)
    done_by = IntegerField(null=True)
    verified_by = IntegerField(null=True)
    registered_by = IntegerField(null=True)
    comments = CharField(null=True)
    face1 = TextField(null=True)
    face2 = TextField(null=True)
    side_face = TextField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'prs_drug_details'


def migration_pill_registration():
    """
    To insert data in GroupMaster and CodeMaster Table
    To create new PRSDrugData and PRSDetails table
    @return: Success Message
    """
    init_db(db, "database_migration")
    db.create_tables([PRSDrugDetails], safe=True)
    print("Table created:PRSDrugDetails")

    if GroupMaster.table_exists():
        # Identification of ids remaining(Session and table differences amongst different dbs)
        GroupMaster.insert(id=constants.PRS_DRUG_STATUS_GROUP_ID, name='PRSStatus').execute()
    if CodeMaster.table_exists():
        CodeMaster.insert(id=constants.PRS_DRUG_STATUS_PENDING, group_id=constants.PRS_DRUG_STATUS_GROUP_ID,
                          key=constants.PRS_DRUG_STATUS_PENDING, value='Pending').execute()
        CodeMaster.insert(id=constants.PRS_DRUG_STATUS_DONE, group_id=constants.PRS_DRUG_STATUS_GROUP_ID,
                          key=constants.PRS_DRUG_STATUS_DONE, value='Done').execute()
        CodeMaster.insert(id=constants.PRS_DRUG_STATUS_REJECTED, group_id=constants.PRS_DRUG_STATUS_GROUP_ID,
                          key=constants.PRS_DRUG_STATUS_REJECTED, value='Rejected').execute()
        CodeMaster.insert(id=constants.PRS_DRUG_STATUS_VERIFIED, group_id=constants.PRS_DRUG_STATUS_GROUP_ID,
                          key=constants.PRS_DRUG_STATUS_VERIFIED, value='Verified').execute()
        CodeMaster.insert(id=constants.PRS_DRUG_STATUS_REGISTERED, group_id=constants.PRS_DRUG_STATUS_GROUP_ID,
                          key=constants.PRS_DRUG_STATUS_REGISTERED, value='Registered').execute()

    print("Insertion in Group Master and Code Master completed.")


if __name__ == '__main__':
    migration_pill_registration()
