from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class UnitMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "unit_master"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField(max_length=20)
    serial_number = CharField(max_length=20, unique=True)
    # device_type_id = ForeignKeyField(DeviceTypeMaster)
    system_id = IntegerField(null=True)
    version = CharField(null=True)
    active = IntegerField(null=True)
    max_canisters = IntegerField(null=True)
    big_drawers = IntegerField(null=True)
    small_drawers = IntegerField(null=True)
    controller = CharField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )



class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    # drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=20)
    available_quantity = SmallIntegerField()
    # canister_number = SmallIntegerField(default=0, null=True)
    canister_type = CharField(max_length=20)
    active = BooleanField()
    reorder_quantity = SmallIntegerField()
    barcode = CharField(max_length=15)
    canister_code = CharField(max_length=25, unique=True, null=True)
    label_print_time = DateTimeField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    # location_id = ForeignKeyField(LocationMaster, null=True, unique=True)
    product_id = IntegerField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class ZoneMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=25)
    floor = IntegerField(null=True)
    length = DecimalField(decimal_places=2, null=True)
    height = DecimalField(decimal_places=2, null=True)
    width = DecimalField(decimal_places=2, null=True)
    company_id = IntegerField()  # Foreign key field of company table of dp auth
    x_coordinate = DecimalField(decimal_places=2, null=True)
    y_coordinate = DecimalField(decimal_places=2, null=True)
    dimensions_unit_id = ForeignKeyField(UnitMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "zone_master"
        indexes = (
            (('company_id', 'name'), True),
        )


class DeviceLayoutDetails(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster, null=True, unique=True)
    zone_id = ForeignKeyField(ZoneMaster, null=True)
    x_coordinate = DecimalField(decimal_places=2, null=True)
    y_coordinate = DecimalField(decimal_places=2, null=True)
    marked_for_transfer = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_layout_details"


class CanisterZoneMapping(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    zone_id = ForeignKeyField(ZoneMaster)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_zone_mapping"


def migrate_zone_impmentation_changes_in_canister():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    with db.transaction():
        if DeviceLayoutDetails.table_exists():
            migrate(
                migrator.drop_not_null(
                    DeviceLayoutDetails._meta.db_table, DeviceLayoutDetails.x_coordinate.db_column
                ),
                migrator.drop_not_null(
                    DeviceLayoutDetails._meta.db_table, DeviceLayoutDetails.y_coordinate.db_column
                )
            )
            print("Table modified: DeviceLayoutDetails")

        if ZoneMaster.table_exists():
            migrate(
                migrator.drop_not_null(
                    ZoneMaster._meta.db_table, ZoneMaster.floor.db_column
                ),
                migrator.drop_not_null(
                    ZoneMaster._meta.db_table, ZoneMaster.length.db_column
                ),
                migrator.drop_not_null(
                    ZoneMaster._meta.db_table, ZoneMaster.height.db_column
                ),
                migrator.drop_not_null(
                    ZoneMaster._meta.db_table, ZoneMaster.width.db_column
                ),
                migrator.drop_not_null(
                    ZoneMaster._meta.db_table, ZoneMaster.x_coordinate.db_column
                ),
                migrator.drop_not_null(
                    ZoneMaster._meta.db_table, ZoneMaster.y_coordinate.db_column
                ),
                migrator.drop_not_null(
                    ZoneMaster._meta.db_table, ZoneMaster.dimensions_unit_id.db_column
                )
            )
            print("Table modified: ZoneMaster")

            system_company_data = DeviceMaster.select(fn.DISTINCT(DeviceMaster.company_id).alias('company_id'))\
                .dicts().order_by(DeviceMaster.company_id)

            zones_data = list()
            for data in system_company_data:
                zones_data.append({"name": "Zone-{}".format(data["company_id"]),
                                   "company_id": data['company_id']})

            if zones_data:
                ZoneMaster.insert_many(zones_data).execute()
                print("Records inserted in table: ZoneMaster")

        db.create_tables([CanisterZoneMapping], safe=True)
        print('Table Created: CanisterZoneMapping')
        company_zone_id = ZoneMaster.select(ZoneMaster.id.alias('zone_id'), ZoneMaster.company_id).dicts()
        company_zone_data = dict()
        for data in company_zone_id:
            company_zone_data[data["company_id"]] = data["zone_id"]

        if CanisterZoneMapping.table_exists():
            with db.atomic():
                query = CanisterMaster.select(CanisterMaster.id.alias('canister_id'), CanisterMaster.company_id)\
                    .where(CanisterMaster.active == 1)\
                    .dicts()
                canisters_data = []
                for record in query:
                    canisters_data.append({"canister_id": record['canister_id'],
                                           "zone_id": company_zone_data[record['company_id']], "created_by": 1})
                CanisterZoneMapping.insert_many(canisters_data).execute()
            print("Records inserted in table canister_zone_mapping ")

        if DeviceLayoutDetails.table_exists():
            device_data = DeviceMaster.select(DeviceMaster.id, DeviceMaster.company_id).dicts()
            data_list = list()
            for device in device_data:
                data_list.append({"device_id": device['id'], "zone_id": company_zone_data[device['company_id']]})
            if data_list:
                DeviceLayoutDetails.insert_many(data_list).execute()
                print("Records inserted in table: DeviceLayoutDetails")


if __name__ == "__main__":
    migrate_zone_impmentation_changes_in_canister()
