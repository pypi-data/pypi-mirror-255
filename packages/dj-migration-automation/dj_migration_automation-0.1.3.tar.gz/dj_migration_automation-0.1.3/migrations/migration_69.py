from playhouse.migrate import *
from collections import defaultdict
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
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
    robot_id = ForeignKeyField(RobotMaster)
    location = SmallIntegerField()
    comment = CharField()
    loc_id = ForeignKeyField(LocationMaster, null=True, related_name='loc_id', unique=True)
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
    dest_canister_number = SmallIntegerField(null=True)
    dest_location_id = ForeignKeyField(LocationMaster, null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfers"

class IntermediatePvsSlotImageDimension(BaseModel):
    id = PrimaryKeyField()
    company_id = SmallIntegerField()
    robot_id = ForeignKeyField(RobotMaster)
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


class IntermediateCanisterDrawerMaster(BaseModel):
    id = PrimaryKeyField()
    robot_id = ForeignKeyField(RobotMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    canister_drawer_number = SmallIntegerField()
    security_code = CharField(default='0000', max_length=8)
    created_by = IntegerField() # todo check if user creates this data
    modified_by = IntegerField() # todo check if user creates this data
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_drawer_master"
        indexes = (
            (('robot_id', 'canister_drawer_number'), True), # keep trailing comma as suggested by peewee doc
        )


def migrate_69():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)
    with db.transaction():
        # starting changes in disabled location
        migrate(
            migrator.add_column(
                IntermediateDisabledCanisterLocation._meta.db_table,
                IntermediateDisabledCanisterLocation.loc_id.db_column,
                IntermediateDisabledCanisterLocation.loc_id
            )
        )
        print("column added: " + str(IntermediateDisabledCanisterLocation))

        query = IntermediateDisabledCanisterLocation.select(LocationMaster.id.alias('location_id'),
                                                            IntermediateDisabledCanisterLocation.id.alias(
                                                                'table_id')).dicts() \
            .join(LocationMaster,
                  on=((IntermediateDisabledCanisterLocation.robot_id == LocationMaster.device_id) &
                      (IntermediateDisabledCanisterLocation.location == LocationMaster.location_number)))

        update_dict = defaultdict(list)
        for record in query:
            update_dict[int(record['location_id'])].append(record['table_id'])

        for key, value in update_dict.items():
            IntermediateDisabledCanisterLocation.update(loc_id=key) \
                .where(IntermediateDisabledCanisterLocation.id << value).execute()

        print("Column values updated " + str(IntermediateDisabledCanisterLocation))

        migrate(
            migrator.drop_index(
                IntermediateDisabledCanisterLocation._meta.db_table,
                'disabled_canister_location_robot_id_id_location'
            ),
            migrator.drop_column(
                IntermediateDisabledCanisterLocation._meta.db_table,
                IntermediateDisabledCanisterLocation.robot_id.db_column
            )
        )
        migrate(
            migrator.drop_column(
                IntermediateDisabledCanisterLocation._meta.db_table,
                IntermediateDisabledCanisterLocation.location.db_column
            )
        )
        print("Column dropped " + str(IntermediateDisabledCanisterLocation))

        # starting changes in CanisterMaster

        deleted_canisters = CanisterMaster.select(CanisterMaster.id).dicts() \
            .where(CanisterMaster.robot_id.is_null(True), CanisterMaster.canister_number == -1)
        deleted_canister_list = [deleted_canister['id'] for deleted_canister in deleted_canisters]

        if deleted_canister_list:
            query = CanisterMaster.update(location_id=None, active=False) \
                .where(CanisterMaster.id << deleted_canister_list).execute()

        on_shelf_canisters = CanisterMaster.select(CanisterMaster.id).dicts() \
            .where(CanisterMaster.robot_id.is_null(True), CanisterMaster.canister_number == 0)
        on_shelf_canister_list = [on_shelf_canister['id'] for on_shelf_canister in on_shelf_canisters]

        if on_shelf_canister_list:
            query = CanisterMaster.update(location_id=None) \
                .where(CanisterMaster.id << on_shelf_canister_list).execute()

        update_canister_info = CanisterMaster.select(CanisterMaster.id.alias('canister_id'),
                                                     LocationMaster.id.alias('location_id')).dicts() \
            .join(LocationMaster, on=(LocationMaster.device_id == CanisterMaster.robot_id) &
                                     (LocationMaster.location_number == CanisterMaster.canister_number))

        update_canister_count = 0
        for canister in update_canister_info:
            CanisterMaster.update(location_id=canister['location_id']) \
                .where(CanisterMaster.id == canister['canister_id']).execute()
            update_canister_count += 1
        print('Updating CanisterMaster, update count', update_canister_count)

        print('Table(s) Modified: CanisterMaster')

        migrate(
            migrator.drop_column(
                CanisterMaster._meta.db_table,
                CanisterMaster.robot_id.db_column,
            ),
            migrator.drop_column(
                CanisterMaster._meta.db_table,
                CanisterMaster.canister_number.db_column,
            )
        )
        print("Column dropped " + str(CanisterMaster))

        # starting changes in canisterTransfer table
        if IntermediateCanisterTransfers.table_exists():
            migrate(
                migrator.add_column(
                    IntermediateCanisterTransfers._meta.db_table,
                    IntermediateCanisterTransfers.dest_device_id.db_column,
                    IntermediateCanisterTransfers.dest_device_id
                )
            )
            print("column added: " + str(IntermediateCanisterTransfers))

            query = IntermediateCanisterTransfers.select(IntermediateCanisterTransfers.dest_robot_id.alias('robot_id'),
                                                         IntermediateCanisterTransfers.id.alias('table_id')).dicts()
            update_dict = defaultdict(list)
            for record in query:
                if record['robot_id']:
                    update_dict[int(record['robot_id'])].append(record['table_id'])

            for key, value in update_dict.items():
                IntermediateCanisterTransfers.update(dest_device_id=key).where(
                    IntermediateCanisterTransfers.id << value).execute()

            print("Column values updated " + str(IntermediateCanisterTransfers))

            migrate(
                migrator.drop_column(
                    IntermediateCanisterTransfers._meta.db_table,
                    IntermediateCanisterTransfers.dest_robot_id.db_column,
                )
            )
            print("Column dropped " + str(IntermediateCanisterTransfers))

            migrate(
                migrator.rename_column(
                    IntermediateCanisterTransfers._meta.db_table,
                    IntermediateCanisterTransfers.dest_canister_number.db_column,
                    'dest_location_number'
                )
            )

        if IntermediatePvsSlotImageDimension.table_exists():
            migrate(
                migrator.add_column(
                    IntermediatePvsSlotImageDimension._meta.db_table,
                    IntermediatePvsSlotImageDimension.device_id.db_column,
                    IntermediatePvsSlotImageDimension.device_id
                )
            )
            print("column added: " + str(IntermediatePvsSlotImageDimension))

            query = IntermediatePvsSlotImageDimension.select(IntermediatePvsSlotImageDimension.robot_id.alias('robot_id'),
                                       IntermediatePvsSlotImageDimension.id.alias('table_id')).dicts()
            update_dict = defaultdict(list)
            for record in query:
                if record['robot_id']:
                    update_dict[int(record['robot_id'])].append(record['table_id'])

            for key, value in update_dict.items():
                IntermediatePvsSlotImageDimension.update(device_id=key).where(IntermediatePvsSlotImageDimension.id << value).execute()

            print("Column values updated " + str(IntermediatePvsSlotImageDimension))

            try:
                migrate(
                    migrator.drop_index(
                        IntermediatePvsSlotImageDimension._meta.db_table,
                        'pvs_slot_image_dimension_company_id_device_id_id_quadrant'
                    ),
                    migrator.drop_foreign_key_constraint(IntermediatePvsSlotImageDimension._meta.db_table,
                                                         IntermediatePvsSlotImageDimension.device_id.db_column),

                    migrator.add_not_null(IntermediatePvsSlotImageDimension._meta.db_table,
                                          IntermediatePvsSlotImageDimension.device_id.db_column),
                    migrator.add_foreign_key_constraint(IntermediatePvsSlotImageDimension._meta.db_table,
                                                        IntermediatePvsSlotImageDimension.device_id.db_column,
                                                        DeviceMaster._meta.db_table, DeviceMaster.id.db_column),
                    migrator.add_index(
                        IntermediatePvsSlotImageDimension._meta.db_table,
                        (IntermediatePvsSlotImageDimension.company_id.db_column,
                         IntermediatePvsSlotImageDimension.device_id.db_column,
                         IntermediatePvsSlotImageDimension.quadrant.db_column),
                        True
                    )
                )
            except Exception as e:
                print(e)
                print('Could not add not_null constraint to IntermediatePvsSlotImageDimension')

            migrate(
                migrator.drop_index(
                    IntermediatePvsSlotImageDimension._meta.db_table,
                    'pvs_slot_image_dimension_company_id_robot_id_id_quadrant'
                ),
                migrator.drop_column(
                    IntermediatePvsSlotImageDimension._meta.db_table,
                    IntermediatePvsSlotImageDimension.robot_id.db_column,
                ),
                migrator.add_index(
                    IntermediatePvsSlotImageDimension._meta.db_table,
                    (IntermediatePvsSlotImageDimension.company_id.db_column,
                     IntermediatePvsSlotImageDimension.device_id.db_column,
                     IntermediatePvsSlotImageDimension.quadrant.db_column),
                    True
                )
            )
            print("Column dropped " + str(IntermediatePvsSlotImageDimension))

        if IntermediateCanisterDrawerMaster.table_exists():
            migrate(
                migrator.add_column(
                    IntermediateCanisterDrawerMaster._meta.db_table,
                    IntermediateCanisterDrawerMaster.device_id.db_column,
                    IntermediateCanisterDrawerMaster.device_id
                )
            )
            print("column added: " + str(IntermediateCanisterDrawerMaster))

            query = IntermediateCanisterDrawerMaster.select(
                IntermediateCanisterDrawerMaster.robot_id.alias('robot_id'),
                IntermediateCanisterDrawerMaster.id.alias('table_id')).dicts()
            update_dict = defaultdict(list)
            for record in query:
                if record['robot_id']:
                    update_dict[int(record['robot_id'])].append(record['table_id'])

            for key, value in update_dict.items():
                IntermediateCanisterDrawerMaster.update(device_id=key).where(
                    IntermediateCanisterDrawerMaster.id << value).execute()

            print("Column values updated " + str(IntermediateCanisterDrawerMaster))

            try:
                migrate(
                    migrator.drop_index(
                        IntermediateCanisterDrawerMaster._meta.db_table,
                        'canister_drawer_master_canister_drawer_number_device_id_id'
                    ),
                    migrator.drop_foreign_key_constraint(IntermediateCanisterDrawerMaster._meta.db_table,
                                                         IntermediateCanisterDrawerMaster.device_id.db_column),
                    migrator.add_not_null(IntermediateCanisterDrawerMaster._meta.db_table,
                                          IntermediateCanisterDrawerMaster.device_id.db_column),
                    migrator.add_foreign_key_constraint(IntermediateCanisterDrawerMaster._meta.db_table,
                                                        IntermediateCanisterDrawerMaster.device_id.db_column,
                                                        DeviceMaster._meta.db_table, DeviceMaster.id.db_column),
                    migrator.add_index(
                        IntermediateCanisterDrawerMaster._meta.db_table,
                        (IntermediateCanisterDrawerMaster.canister_drawer_number.db_column,
                         IntermediateCanisterDrawerMaster.device_id.db_column),
                        True
                    )
                )
            except Exception as e:
                print(e)
                print('Could not add not_null constraint to IntermediateCanisterDrawerMaster')

            migrate(
                migrator.drop_index(
                    IntermediateCanisterDrawerMaster._meta.db_table,
                    'canister_drawer_master_robot_id_id_canister_drawer_number'
                ),
                migrator.drop_column(
                    IntermediateCanisterDrawerMaster._meta.db_table,
                    IntermediateCanisterDrawerMaster.robot_id.db_column,
                ),
                migrator.add_index(
                    IntermediateCanisterDrawerMaster._meta.db_table,
                    (IntermediateCanisterDrawerMaster.canister_drawer_number.db_column,
                     IntermediateCanisterDrawerMaster.device_id.db_column),
                    True
                )
            )
            print("Column dropped " + str(IntermediateCanisterDrawerMaster))

        # starting changes in CanisterHistory table
        if CanisterHistory.table_exists():
            migrate(
                migrator.add_column(
                    CanisterHistory._meta.db_table,
                    CanisterHistory.current_location_id.db_column,
                    CanisterHistory.current_location_id
                ),
                migrator.add_column(
                    CanisterHistory._meta.db_table,
                    CanisterHistory.previous_location_id.db_column,
                    CanisterHistory.previous_location_id
                )
            )
            print('CanisterHistory columns added')

            # current_location_query = CanisterHistory.select(
            #     CanisterHistory.id.alias('can_history_id'),
            #     LocationMaster.id.alias('location_id')
            # ).dicts() \
            #     .join(LocationMaster, on=((CanisterHistory.current_robot_id == LocationMaster.device_id) &
            #                               (CanisterHistory.current_canister_number == LocationMaster.location_number)))
            # update_dict = defaultdict(list)
            # print('current_location_id being updated')
            # for record in current_location_query:
            #     update_dict[int(record['location_id'])].append(record['can_history_id'])
            #
            # for key, value in update_dict.items():
            #     CanisterHistory.update(current_location_id=key).where(CanisterHistory.id << value).execute()
            #
            # print('previous_location_id being updated')
            # previous_location_query = CanisterHistory.select(
            #     CanisterHistory.id.alias('can_history_id'),
            #     LocationMaster.id.alias('location_id')
            # ).dicts() \
            #     .join(LocationMaster, on=((CanisterHistory.previous_robot_id == LocationMaster.device_id) &
            #                               (CanisterHistory.previous_canister_number == LocationMaster.location_number)))
            # update_dict = defaultdict(list)
            # for record in previous_location_query:
            #     update_dict[int(record['location_id'])].append(record['can_history_id'])
            #
            # for key, value in update_dict.items():
            #     CanisterHistory.update(previous_location_id=key).where(CanisterHistory.id << value).execute()

        current_location_query = 'update canister_history ch JOIN location_master lm ON ' \
                                 'lm.device_id_id = ch.current_robot_id_id AND ' \
                                 'lm.location_number = ch.current_canister_number' \
                                 ' SET ch.current_location_id_id = lm.id;'
        result = db.execute_sql(current_location_query)
        print('Updated rows count for current location {}'.format(result))

        previous_location_query = 'update canister_history ch JOIN location_master lm ON ' \
                                  'lm.device_id_id = ch.previous_robot_id_id AND ' \
                                  'lm.location_number = ch.previous_canister_number ' \
                                  'SET ch.previous_location_id_id = lm.id;'

        result = db.execute_sql(previous_location_query)
        print('Updated rows count for previous location {}'.format(result))

        print('Table values updated')
        migrate(
            migrator.drop_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.previous_canister_number.db_column,
            ),
            migrator.drop_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.previous_robot_id.db_column,
            ),
            migrator.drop_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.current_canister_number.db_column,
            ),
            migrator.drop_column(
                CanisterHistory._meta.db_table,
                CanisterHistory.current_robot_id.db_column,
            )
        )
        print('columns dropped')
        print('Table updated CanisterHistory')


if __name__ == "__main__":
    migrate_69()
