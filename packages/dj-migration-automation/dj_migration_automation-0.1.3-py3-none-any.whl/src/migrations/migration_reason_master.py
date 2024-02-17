from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel, db
from model.model_init import init_db


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class ReasonMaster(BaseModel):
    id = PrimaryKeyField()
    reason_group = ForeignKeyField(GroupMaster)
    reason = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "reason_master"

    @staticmethod
    def get_initial_data():
        return [
            dict(id=1, reason_group=6, reason="Broken Pill"),
            dict(id=2, reason_group=6, reason="Extra Pill Count"),
            dict(id=3, reason_group=6, reason="Missing Pill"),
            dict(id=4, reason_group=6, reason="Pill Misplaced")
        ]


def add_codes():
    try:
        ReasonMaster.insert_many(ReasonMaster.get_initial_data()).execute()
        print("migrate_reason_master: code added in reason master")
    except Exception as e:
        print("migrate_reason_master: Error while adding codes in reason master: " + str(e))


def migrate_reason_master():
    init_db(db, 'database_migration')
    add_codes()


if __name__ == "__main__":
    migrate_reason_master()
