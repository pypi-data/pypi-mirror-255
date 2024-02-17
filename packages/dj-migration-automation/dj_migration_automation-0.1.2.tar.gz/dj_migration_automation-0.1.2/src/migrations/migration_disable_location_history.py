import logging

from peewee import *
from playhouse.migrate import migrate, MySQLMigrator

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
# get the logger for the pack from global configuration file logging.json
from model.model_init import init_db

logger = logging.getLogger("root")


class LocationMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


class DisabledCanisterLocation(BaseModel):
    id = PrimaryKeyField()
    loc_id = ForeignKeyField(LocationMaster, related_name='loc_id', unique=True)
    comment = CharField()
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "disabled_canister_location"


class NewDisabledLocationHistory(BaseModel):
    id = PrimaryKeyField()
    loc_id = ForeignKeyField(LocationMaster, related_name='loc_id_new', unique=True)
    start_time = DateTimeField(default=get_current_date_time())
    end_time = DateTimeField(null=True)
    comment = CharField()
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "disabled_location_history"


def rename_disabled_canister_location():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    try:
        migrate(
            migrator.rename_table(DisabledCanisterLocation._meta.db_table,
                                  NewDisabledLocationHistory._meta.db_table)
        )
        print("table disabled_canister_location renamed to disabled_location_history")
        migrate(
            migrator.add_column(NewDisabledLocationHistory._meta.db_table,
                                NewDisabledLocationHistory.start_time.db_column,
                                NewDisabledLocationHistory.start_time),
            migrator.add_column(NewDisabledLocationHistory._meta.db_table,
                                NewDisabledLocationHistory.end_time.db_column,
                                NewDisabledLocationHistory.end_time)
        )
        print("Columns added start_time and end_time in disabled_location_history table")

    except Exception as e:
        logger.error("Error while renaming table disabled_canister_location", str(e))


if __name__ == '__main__':
    rename_disabled_canister_location()
