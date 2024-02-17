from playhouse.migrate import *
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.service.zone import get_robot_quadrant
from src.model.model_container_master import ContainerMaster
from src.model.model_location_master import LocationMaster


def get_device_locations(device_list):
    try:
        location_quadrant_mapping = dict()

        for device_id in device_list:
            query = LocationMaster.select(LocationMaster.id,
                                          LocationMaster.display_location,
                                          ContainerMaster.drawer_name).dicts()\
                .join(ContainerMaster, on= ContainerMaster.id == LocationMaster.container_id)\
                .where(LocationMaster.device_id == device_id)
            for record in query:
                location_id = record['id']
                display_location = list(str(record['display_location']).split("-"))
                location_number = int(display_location[1])
                drawer_name = list(str(record['drawer_name']).split("-"))
                drawer_number = int(drawer_name[1])
                quadrant = get_robot_quadrant(location_number, drawer_number)
                location_quadrant_mapping[location_id] = quadrant

        for location, quad in location_quadrant_mapping.items():
            update_status = LocationMaster.update(quadrant = quad).where(LocationMaster.id == location).execute()
            print(update_status)

    except Exception as e:
        print('Exception came in updating location data: ', e)
        raise e


def migrate_update_robot_quad():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    device_list = [2,3]
    get_device_locations(device_list)
    print("Quadrant updated")


if __name__ == "__main__":
    migrate_update_robot_quad()
