import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *


class SystemSetting(BaseModel):

    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField()
    value = CharField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "system_setting"
        indexes = (
            (('system_id', 'name'), True),  # keep trailing comma as suggested by peewee doc # unique setting per system
        )

    @classmethod
    def db_update_or_create_record(cls, create_dict, update_dict):
        """
        checks if for the system id and name the data is created in system settings
        if created than updated or else create new row
        @param update_dict:
        @param create_dict:
        """
        try:
            record, created = SystemSetting.get_or_create(defaults=update_dict, **create_dict)
            response = "row created"
            if not created:
                created_by = update_dict.pop("created_by", None)
                created_date = update_dict.pop("created_date", None)
                update_dict['modified_date'] = get_current_date_time()
                SystemSetting.update(**update_dict).where(SystemSetting.id == record.id).execute()
                response = "row updated"
            return response

        except DataError as e:
            raise DataError(e)
        except IntegrityError as e:
            raise InternalError(e)
        except InternalError as e:
            raise InternalError(e)


def migrate_system_setting_for_data_insertion(system_id):
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        system_setting_data = [{"system_id": system_id, "name": "MFD_CANISTER_THRESHOLD_PER_HOUR", "value": 15},
                               {"system_id": system_id, "name": "BATCH_DURATION_IN_DAYS", "value": 7}]

        for data in system_setting_data:
            data_dict = {'system_id': data["system_id"], 'name': data["name"]}
            update_dict = {"created_by": 11, "created_date": get_current_date_time(), "modified_by": 11,
                           "value": data["value"]}

            print("data dict", data_dict)
            response = SystemSetting.db_update_or_create_record(data_dict, update_dict)
            print(response)

    except Exception as e:
        print(e)
        print('failed')


if __name__ == "__main__":
    migrate_system_setting_for_data_insertion(system_id=14)
