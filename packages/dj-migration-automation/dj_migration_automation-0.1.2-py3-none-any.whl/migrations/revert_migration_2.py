from playhouse.migrate import *
from collections import defaultdict
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import get_current_date_time


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    name = CharField()
    serial_number = CharField(unique=True)
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


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    drawer_number = IntegerField()
    display_location = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

        indexes = (
            (('device_id', 'location_number'), True),
        )


class RobotMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    company_id = IntegerField()
    name = CharField(max_length=150)
    serial_number = FixedCharField(unique=True, max_length=10)
    version = FixedCharField(max_length=11)
    active = BooleanField(default=True)
    max_canisters = SmallIntegerField()  # number of canisters that robot can hold
    big_drawers = IntegerField(default=4)  # number of big drawers that robot holds
    small_drawers = IntegerField(default=12)  # number of small drawers that robot holds
    # controller used 'AR' for ardiuno and 'BB' for beagle bone 'BBB' for beagle bone black
    controller = CharField(max_length=10, default="AR")
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "robot_master"


class IntermediateDisabledCanisterLocation(BaseModel):
    id = PrimaryKeyField()
    robot_id = ForeignKeyField(RobotMaster,null=True)
    location = SmallIntegerField(null=True)
    comment = CharField()
    loc_id = ForeignKeyField(LocationMaster, null=True, related_name='loc_id')
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "disabled_canister_location"
        indexes = (  # unique location per robot
            (('location', 'robot_id'), True),
        )


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    robot_id = ForeignKeyField(RobotMaster, null=True)
    # drug_id = ForeignKeyField(DrugMaster)
    rfid = FixedCharField(null=True, unique=True, max_length=20)
    available_quantity = SmallIntegerField()
    canister_number = SmallIntegerField(default=0, null=True)
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
    location_id = ForeignKeyField(LocationMaster, null=True, unique=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class CanisterHistory(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    current_robot_id = ForeignKeyField(RobotMaster, null=True, related_name='current_robot_id')
    previous_robot_id = ForeignKeyField(RobotMaster, null=True, related_name='previous_robot_id')
    # drug_id = ForeignKeyField(DrugMaster)
    current_canister_number = SmallIntegerField(default=0, null=True)
    previous_canister_number = SmallIntegerField(default=0, null=True)
    current_location_id = ForeignKeyField(LocationMaster, null=True, default=None, related_name='current_location_id')
    previous_location_id = ForeignKeyField(LocationMaster, null=True, default=None, related_name='previous_location_id')
    action = CharField(max_length=50)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_history"


class IntermediateCanisterTransfers(BaseModel):
    id = PrimaryKeyField()
    # batch_id = ForeignKeyField(BatchMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    dest_robot_id = ForeignKeyField(RobotMaster, null=True)
    dest_device_id = ForeignKeyField(DeviceMaster, null=True)
    dest_location_number = SmallIntegerField(null=True)
    dest_location_id = ForeignKeyField(LocationMaster, null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfers"

class IntermediatePvsSlotImageDimension(BaseModel):
    id = PrimaryKeyField()
    company_id = SmallIntegerField()
    robot_id = ForeignKeyField(RobotMaster, null=True)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    quadrant = SmallIntegerField(default=0)
    left_value = IntegerField(default=0)
    right_value = IntegerField(default=1280)
    top_value = IntegerField(default=0)
    bottom_value = IntegerField(default=720)

    class Meta:
        indexes = (
            (('company_id', 'robot_id', 'quadrant'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pvs_slot_image_dimension"


class CanisterDrawers(BaseModel):
    id = PrimaryKeyField()
    robot_id = ForeignKeyField(RobotMaster)
    drawer_id = IntegerField()  # To store the drawer id for electronics api calls.
    drawer_number = IntegerField()  # To store the physical drawer number.
    ip_address = CharField()
    drawer_size = CharField(default="REGULAR", max_length=20)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drawers"

        indexes = (
            (('robot_id', 'drawer_number', 'ip_address'), True),
        )


def migrate_data():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    with db.transaction():
        # starting changes in disabled location
        migrate(
            # migrator.add_column(
            #     IntermediateDisabledCanisterLocation._meta.db_table,
            #     IntermediateDisabledCanisterLocation.location.db_column,
            #     IntermediateDisabledCanisterLocation.location
            # ),
            migrator.add_column(
                IntermediateDisabledCanisterLocation._meta.db_table,
                IntermediateDisabledCanisterLocation.robot_id.db_column,
                IntermediateDisabledCanisterLocation.robot_id
            )
        )
        print("column added: " + str(IntermediateDisabledCanisterLocation))

        query = IntermediateDisabledCanisterLocation.select(LocationMaster.device_id,
                                                            LocationMaster.location_number,
                                                            IntermediateDisabledCanisterLocation.id.alias(
                                                                'table_id')).dicts() \
            .join(LocationMaster,
                  on=(IntermediateDisabledCanisterLocation.loc_id == LocationMaster.id))
        update_dict = defaultdict(list)
        for record in query:
            update_dict[(int(record['device_id']),int(record['location_number']))].append(record['table_id'])

        for key, value in update_dict.items():
            IntermediateDisabledCanisterLocation.update(robot_id=key[0], location=key[1]) \
                .where(IntermediateDisabledCanisterLocation.id << value).execute()

        print("Column values updated " + str(IntermediateDisabledCanisterLocation))

        try:
            migrate(migrator.add_not_null(IntermediateDisabledCanisterLocation._meta.db_table,
                                          IntermediateDisabledCanisterLocation.robot_id.db_column))
            migrate(migrator.add_not_null(IntermediateDisabledCanisterLocation._meta.db_table,
                                          IntermediateDisabledCanisterLocation.location.db_column))
        except Exception as e:
            print(e)
            print('Could not add not_null constraint to {}'.format(IntermediateDisabledCanisterLocation))

        migrate(

            migrator.drop_column(
                IntermediateDisabledCanisterLocation._meta.db_table,
                IntermediateDisabledCanisterLocation.loc_id.db_column
            )
        )
        print("Column dropped " + str(IntermediateDisabledCanisterLocation))

        # starting changes in CanisterMaster

        migrate(
            migrator.add_column(
                CanisterMaster._meta.db_table,
                CanisterMaster.robot_id.db_column,
                CanisterMaster.robot_id
            ),
            migrator.add_column(
                CanisterMaster._meta.db_table,
                CanisterMaster.canister_number.db_column,
                CanisterMaster.canister_number
            )
        )

        deleted_canisters = CanisterMaster.select(CanisterMaster.id).dicts() \
            .where(CanisterMaster.active != settings.is_canister_active)
        deleted_canister_list = [deleted_canister['id'] for deleted_canister in deleted_canisters]

        if deleted_canister_list:
            query = CanisterMaster.update(robot_id=None, canister_number=-1) \
                .where(CanisterMaster.id << deleted_canister_list).execute()

        on_shelf_canisters = CanisterMaster.select(CanisterMaster.id).dicts() \
            .where(CanisterMaster.location_id.is_null(True))
        on_shelf_canister_list = [on_shelf_canister['id'] for on_shelf_canister in on_shelf_canisters]

        if on_shelf_canister_list:
            query = CanisterMaster.update(robot_id=None, canister_number=0) \
                .where(CanisterMaster.id << on_shelf_canister_list).execute()

        update_canister_info = CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                                     LocationMaster.location_number, LocationMaster.device_id).dicts() \
            .join(LocationMaster, on=(LocationMaster.id == CanisterMaster.location_id) &
                                     (LocationMaster.location_number == CanisterMaster.canister_number))

        update_canister_count = 0
        for canister in update_canister_info:
            CanisterMaster.update(robot_id=canister['device_id'], canister_number=canister['location_number']) \
                .where(CanisterMaster.id == canister['canister_id']).execute()
            update_canister_count += 1
            print('Updating CanisterMaster, update count', update_canister_count)

        print('Table(s) Modified: CanisterMaster')

        migrate(
            migrator.drop_column(
                CanisterMaster._meta.db_table,
                CanisterMaster.location_id.db_column,
            )
        )
        print("Column dropped " + str(CanisterMaster))
        # ===============================================================================================
        # # starting changes in canisterTransfer table
        if IntermediateCanisterTransfers.table_exists():
            migrate(
                migrator.add_column(
                    IntermediateCanisterTransfers._meta.db_table,
                    IntermediateCanisterTransfers.dest_robot_id.db_column,
                    IntermediateCanisterTransfers.dest_robot_id
                )
            )
            print("column added: " + str(IntermediateCanisterTransfers))

            query = IntermediateCanisterTransfers.select(IntermediateCanisterTransfers.dest_device_id.alias('device_id'),
                                                         IntermediateCanisterTransfers.id.alias('table_id')).dicts()
            update_dict = defaultdict(list)
            for record in query:
                if record['device_id']:
                    update_dict[int(record['device_id'])].append(record['table_id'])

            for key, value in update_dict.items():
                IntermediateCanisterTransfers.update(dest_robot_id=key).where(
                    IntermediateCanisterTransfers.id << value).execute()

            print("Column values updated " + str(IntermediateCanisterTransfers))

            migrate(
                migrator.drop_column(
                    IntermediateCanisterTransfers._meta.db_table,
                    IntermediateCanisterTransfers.dest_device_id.db_column,
                )
            )
            print("Column dropped " + str(IntermediateCanisterTransfers))

            migrate(
                migrator.rename_column(
                    IntermediateCanisterTransfers._meta.db_table,
                    IntermediateCanisterTransfers.dest_location_number.db_column,
                    'dest_canister_number'
                )
            )
        # =====================================================================================================
        if IntermediatePvsSlotImageDimension.table_exists():
            migrate(
                migrator.add_column(
                    IntermediatePvsSlotImageDimension._meta.db_table,
                    IntermediatePvsSlotImageDimension.robot_id.db_column,
                    IntermediatePvsSlotImageDimension.robot_id
                )
            )
            print("column added: " + str(IntermediatePvsSlotImageDimension))

            query = IntermediatePvsSlotImageDimension.select(IntermediatePvsSlotImageDimension.device_id.alias('device_id'),
                                       IntermediatePvsSlotImageDimension.id.alias('table_id')).dicts()
            update_dict = defaultdict(list)
            for record in query:
                if record['device_id']:
                    update_dict[int(record['device_id'])].append(record['table_id'])

            for key, value in update_dict.items():
                IntermediatePvsSlotImageDimension.update(robot_id=key).where(IntermediatePvsSlotImageDimension.id << value).execute()

            print("Column values updated " + str(IntermediatePvsSlotImageDimension))

            try:
                migrate(migrator.add_not_null(IntermediatePvsSlotImageDimension._meta.db_table, IntermediatePvsSlotImageDimension.robot_id.db_column))
            except Exception as e:
                print(e)
                print('Could not add not_null constraint to {}'.format(IntermediatePvsSlotImageDimension))

            migrate(
                migrator.drop_column(
                    IntermediatePvsSlotImageDimension._meta.db_table,
                    IntermediatePvsSlotImageDimension.device_id.db_column,
                )
            )
            print("Column dropped " + str(IntermediatePvsSlotImageDimension))

        if CanisterDrawers.table_exists():
            db.drop_tables([CanisterDrawers])
            print("Table dropped: CanisterDrawers")

        db.create_tables([CanisterDrawers], safe=True)

        #  starting changes in CanisterHistory table
        migrate(
            migrator.add_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.current_robot_id.db_column,
                CanisterHistory.current_robot_id
            ),
            migrator.add_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.previous_robot_id.db_column,
                CanisterHistory.previous_robot_id
            ),
            migrator.add_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.current_canister_number.db_column,
                CanisterHistory.current_canister_number
            ),
            migrator.add_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.previous_canister_number.db_column,
                CanisterHistory.previous_canister_number
            )
        )
        print('CanisterHistory columns added')

        current_location_query = CanisterHistory.select(
            CanisterHistory.id.alias('can_history_id'),
            LocationMaster.location_number,
            LocationMaster.device_id
        ).dicts() \
            .join(LocationMaster, on=((CanisterHistory.current_location_id == LocationMaster.id)))
        update_dict = defaultdict(list)

        print('current_location_id being updated')
        for record in current_location_query:
            update_dict[(int(record['device_id']), int(record['location_number']))].append(record['can_history_id'])

        for key, value in update_dict.items():
            CanisterHistory.update(current_robot_id=key[0],
                                   current_canister_number=key[1]).where(CanisterHistory.id << value).execute()

        print('previous_location_id being updated')
        previous_location_query = CanisterHistory.select(
            CanisterHistory.id.alias('can_history_id'),
            LocationMaster.location_number,
            LocationMaster.device_id
        ).dicts() \
            .join(LocationMaster, on=((CanisterHistory.previous_location_id == LocationMaster.id)))
        update_dict = defaultdict(list)
        for record in previous_location_query:
            update_dict[(int(record['device_id']), int(record['location_number']))].append(record['can_history_id'])

        for key, value in update_dict.items():
            CanisterHistory.update(previous_robot_id=key[0],
                                   previous_canister_number=key[1]).where(CanisterHistory.id << value).execute()

        print('Table values updated')
        migrate(
            migrator.drop_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.previous_location_id.db_column,
            ),
            migrator.drop_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.current_location_id.db_column,
            )
        )
        print('columns dropped')
        print('Table updated CanisterHistory')


if __name__ == "__main__":
    migrate_data()
