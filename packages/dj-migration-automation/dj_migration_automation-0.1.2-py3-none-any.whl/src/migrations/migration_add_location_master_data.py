import logging
from peewee import *
from playhouse.migrate import MySQLMigrator

import settings
from model.model_init import init_db
from dosepack.base_model.base_model import BaseModel,db

logger = logging.getLogger("root")


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


class ContainerMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "container_master"


class LocationMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    location_number = IntegerField()
    container_id = ForeignKeyField(ContainerMaster, related_name='location_master_container_id')
    display_location = CharField()
    quadrant = SmallIntegerField(null=True)
    is_disabled = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


def add_data_in_location_master():
    # for robot
    robot_location_number = 0
    robot_dict = {}
    location_data_list = []
    device_id = 0
    container_id = 0
    s = 'MABCDEFG'
    for i in range(1, 3):
        device_id += 1
        for data in s:
            for j in range(1, 11):
                container_id += 1
                for k in range(1, 9):
                    if j == 1 or j == 2 or j == 3 or j == 4:
                        if k == 1 or k == 2 or k == 3 or k == 4:
                            quadrant = 4
                        else:
                            quadrant = 1
                    if j == 5 or j == 6:
                        if k == 1 or k == 2:
                            quadrant = 4
                        if k == 3 or k == 4:
                            quadrant = 3
                        if k == 5 or k == 6:
                            quadrant = 2
                        if k == 7 or k == 8:
                            quadrant = 1
                    if j == 7 or j == 8 or j == 9 or j == 10:
                        if k == 1 or k == 2 or k == 3 or k == 4:
                            quadrant = 3
                        else:
                            quadrant = 2

                    display_location = data + str(j) + '-' + str(k)
                    robot_location_number += 1
                    robot_dict['container_id'] = container_id
                    robot_dict['device_id'] = device_id
                    robot_dict['location_number'] = robot_location_number
                    robot_dict['display_location'] = display_location
                    robot_dict['quadrant'] = quadrant
                    location_data_list.append(robot_dict.copy())

    # csr dictionary
    csr_dict = {}
    csr_device_id = 3
    csr_location_number = 0
    bi = []
    f = 'ABCDEFGHIJ'
    for data in f:
        for i in range(1, 27):
            container_id += 1
            for j in range(1, 21):
                display_location = data + str(i) + '-' + str(j)
                csr_location_number += 1
                csr_dict['container_id'] = container_id
                csr_dict['location_number'] = csr_location_number
                csr_dict['device_id'] = csr_device_id
                csr_dict['display_location'] = display_location
                csr_dict['quadrant'] = None
                location_data_list.append(csr_dict.copy())

    # manual trolley dictionary
    mcc_dict = {}
    mcc_device_id = 3
    mcc = []
    mcc_location_number = 0
    f = 'ABCDEFGHIJ'
    for data in f:
        mcc_device_id += 1
        for i in range(1, 17):
            container_id += 1
            for j in range(1, 21):
                display_location = 'M' + data + str(i) + '-' + str(j)
                mcc_location_number += 1
                mcc_dict['container_id'] = container_id
                mcc_dict['location_number'] = mcc_location_number
                mcc_dict['display_location'] = display_location
                mcc_dict['device_id'] = mcc_device_id
                mcc_dict['quadrant'] = None
                location_data_list.append(mcc_dict.copy())

    # canister transfer trolley dictionary
    ctc_dict = {}
    ctc_device_id = 13
    ctc_location_number = 0
    ctc = []
    f = 'ABC'
    for data in f:
        ctc_device_id += 1
        for i in range(1, 17):
            container_id += 1
            for j in range(1, 21):
                display_location = 'C' + data + str(i) + '-' + str(j)
                ctc_location_number += 1
                ctc_dict['container_id'] = container_id
                ctc_dict['location_number'] = ctc_location_number
                ctc_dict['display_location'] = display_location
                ctc_dict['device_id'] = ctc_device_id
                ctc_dict['quadrant'] = None
                ctc.append(ctc_dict.copy())
                location_data_list.append(ctc_dict.copy())

    # Canister cart elevator dict
    cce_dict = {}
    cce_location_number = 0
    cce_device_id = 17
    f = 'EA'
    for i in range(1, 9):
        container_id += 1
        for j in range(1, 21):
            display_location = f + str(i) + '-' + str(j)
            cce_location_number += 1
            cce_dict['container_id'] = container_id
            cce_dict['location_number'] = cce_location_number
            cce_dict['display_location'] = display_location
            cce_dict['device_id'] = cce_device_id
            cce_dict['quadrant'] = None
            location_data_list.append(cce_dict.copy())

    # manual filled drawer
    f = 'MF'
    mfd_dict = {}
    mfd_location_number = 0
    mfd_device_id = 18
    container_id += 1
    for i in range(1, 5):
        mfd_device_id += 1
        container_id += 1
        for j in range(1, 17):
            display_location = f + str(i) + '-' + str(j)
            mfd_location_number += 1
            mfd_dict['container_id'] = container_id
            mfd_dict['location_number'] = mfd_location_number
            mfd_dict['display_location'] = display_location
            mfd_dict['device_id'] = mfd_device_id
            mfd_dict['quadrant'] = None
            location_data_list.append(mfd_dict.copy())
    print(location_data_list)
    print(container_id)

    try:
        LocationMaster.insert_many(location_data_list).execute()
        print("Data Added in LocationMaster")
    except (IntegrityError, InternalError) as e:
        raise e


def migration_location_data():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    add_data_in_location_master()


if __name__ == '__main__':
    migration_location_data()
