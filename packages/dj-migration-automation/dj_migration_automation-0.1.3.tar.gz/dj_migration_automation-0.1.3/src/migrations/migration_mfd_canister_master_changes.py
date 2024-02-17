from peewee import *
from playhouse.migrate import MySQLMigrator, migrate

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from model.model_init import init_db
from src.model.model_device_master import DeviceMaster
from src.model.model_location_master import LocationMaster


class OldMfdCanisterMaster(BaseModel):
    id = PrimaryKeyField()
    rfid = FixedCharField(null=True, unique=True, max_length=32)
    location_id = ForeignKeyField(LocationMaster, null=True, unique=True, related_name='mfd_loc_id')
    canister_type = CharField()
    active = BooleanField()
    label_print_time = DateTimeField(null=True, default=None)
    erp_product_id = IntegerField(null=True, unique=True)
    company_id = IntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    home_cart_id = ForeignKeyField(DeviceMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_master"


class NewMfdCanisterMaster(BaseModel):
    id = PrimaryKeyField()
    rfid = FixedCharField(null=True, unique=True, max_length=32)
    location_id = ForeignKeyField(LocationMaster, null=True, unique=True, related_name='mfd_canister_master_mfd_loc_id')
    canister_type = ForeignKeyField(CodeMaster, default=settings.SIZE_OR_TYPE["MFD"])
    active = BooleanField()
    label_print_time = DateTimeField(null=True, default=None)
    erp_product_id = IntegerField(null=True, unique=True)
    company_id = IntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    home_cart_id = ForeignKeyField(DeviceMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_canister_master"


def migrate_mfd_canister_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    if OldMfdCanisterMaster.table_exists():
        migrate(
            migrator.drop_column(
                OldMfdCanisterMaster._meta.db_table,
                OldMfdCanisterMaster.canister_type.db_column,
            ),
            migrator.add_column(
                NewMfdCanisterMaster._meta.db_table,
                NewMfdCanisterMaster.canister_type.db_column,
                NewMfdCanisterMaster.canister_type
            )
        )
        print('table modified: MfdCanisterMaster')