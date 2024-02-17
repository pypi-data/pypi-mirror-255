import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_details import PackDetails
from src.model.model_canister_status_history import CanisterMaster
from src.model.model_location_master import LocationMaster
from src.model.model_pack_grid import PackGrid
from src.model.model_unique_drug import UniqueDrug
from peewee import ForeignKeyField, DateTimeField, PrimaryKeyField, InternalError, IntegrityError

logger = settings.logger


class PackCanisterUsage(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    unique_drug_id = ForeignKeyField(UniqueDrug)
    # robot_id = ForeignKeyField(RobotMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    # canister_number = SmallIntegerField()
    location_id = ForeignKeyField(LocationMaster)
    pack_grid_id = ForeignKeyField(PackGrid)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_id', 'unique_drug_id', 'pack_grid_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = 'pack_canister_usage'

    @classmethod
    def add_pack_canister_usage_details(cls, pack_details):
        """
        adds used canister data
        :param pack_details: dict
        :return:
        """
        try:

            for pack_detail in pack_details:
                create_dict = {
                    'pack_id': pack_detail['pack_id'],
                    'pack_grid_id': pack_detail['pack_grid_id'],
                    'unique_drug_id': pack_detail['unique_drug_id']
                }
                update_dict = {
                    'canister_id': pack_detail['canister_id'],
                    'location_id': pack_detail['location_id']
                }
                PackCanisterUsage.db_update_or_create(create_dict, update_dict)
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise

