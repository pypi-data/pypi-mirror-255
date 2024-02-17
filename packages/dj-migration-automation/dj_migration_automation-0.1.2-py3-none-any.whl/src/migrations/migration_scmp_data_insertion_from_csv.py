import csv

from peewee import IntegrityError, InternalError

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_action_master import ActionMaster
from src.model.model_code_master import CodeMaster
from src.model.model_company_setting import CompanySetting
from src.model.model_configuration_master import ConfigurationMaster
from src.model.model_consumable_type_master import ConsumableTypeMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_dosage_type import DosageType
from src.model.model_drug_shape_fields import DrugShapeFields
from src.model.model_group_master import GroupMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_grid import PackGrid
from src.model.model_reason_master import ReasonMaster
from src.model.model_system_setting import SystemSetting
from src.model.model_unit_master import UnitMaster
from src.model.model_zone_master import ZoneMaster

path_to_csv = "src/migrations/path_to_csv/"
tables_path = {
    GroupMaster: 'group_master',
    ActionMaster: 'action_master',
    CodeMaster: 'code_master',
    DeviceTypeMaster: 'device_type_master',
    DeviceMaster: 'device_master',
    ContainerMaster: 'container_master',
    LocationMaster: 'location_master',
    ConfigurationMaster: 'configuration_master',
    PackGrid: 'pack_grid',
    CompanySetting: 'company_setting',
    SystemSetting: 'system_setting',
    ConsumableTypeMaster: 'consumable_type_master',

    CustomDrugShape: 'custom_drug_shape',
    DosageType: 'dosage_type',
    DrugShapeFields: 'drug_shape_fields',
    ReasonMaster: 'reason_master',

    UnitMaster: 'unit_master',
    ZoneMaster: 'zone_master',
    DeviceLayoutDetails: 'device_layout_details',
}


def add_data_in_scmp_tables():
    init_db(db, 'database_migration')

    try:
        with db.transaction():
            for table in tables_path.keys():
                table_data = list(csv.DictReader(open(path_to_csv + tables_path[table] + ".csv", "r")))
                for data in table_data:
                    for k, v in data.items():
                        if v == 'NULL':
                            data[k] = None
                table.insert_many(table_data).execute()
                print("Data added in " + str(table))

    except (IntegrityError, InternalError) as e:
        raise e


if __name__ == "__main__":
    add_data_in_scmp_tables()
