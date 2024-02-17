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

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"

        indexes = (
            (('name', 'company_id'), True),
        )


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    active = BooleanField()

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
            print("Table DeviceLayoutDetails modified: altered null=True in columns x_coordinate, y_coordinate")

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
            print(
                "Table ZoneMaster modified: altered null=True in columns floor, length, height, width, x_coordinate, "
                "y_coordinate,dimensions_unit_id")

        zones_data = [{"name": 'Alpha', "floor": 1, "length": 1500.0, "height": 1300.0, "width": 1500.0,
                            "company_id": 3, "x_coordinate": 12.30, "y_coordinate": 12.30, "dimensions_unit_id": 5},
                           {"name": 'Beta', "floor": 1, "length": 1300.0, "height": 1200.0, "width": 1300.0,
                            "company_id": 3, "x_coordinate": 20.30, "y_coordinate": 20.30, "dimensions_unit_id": 5}]
        ZoneMaster.insert_many(zones_data).execute()
        print("Dummy records inserted in table zone_master")

        db.create_tables([CanisterZoneMapping], safe=True)
        print('Table Created: CanisterZoneMapping')

        if CanisterZoneMapping.table_exists():
            with db.atomic():
                query = CanisterMaster.select(CanisterMaster.id.alias('canister_id')).where(CanisterMaster.active == 1)\
                    .dicts()
                canisters_data = []
                for record in query:
                    canisters_data.append({"canister_id": record['canister_id'], "zone_id": 1, "created_by": 5})
                CanisterZoneMapping.insert_many(canisters_data).execute()
            print("Records inserted in table canister_zone_mapping ")


if __name__ == "__main__":
    migrate_zone_impmentation_changes_in_canister()
