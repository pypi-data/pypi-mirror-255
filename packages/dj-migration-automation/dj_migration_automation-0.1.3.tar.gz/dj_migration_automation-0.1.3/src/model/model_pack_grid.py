from peewee import PrimaryKeyField, InternalError, IntegrityError, SmallIntegerField
import settings
from dosepack.base_model.base_model import BaseModel
from src import constants

logger = settings.logger


class PackGrid(BaseModel):
    id = PrimaryKeyField()
    slot_row = SmallIntegerField()
    slot_column = SmallIntegerField()
    slot_number = SmallIntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_grid"

    @classmethod
    def db_get_pack_grid_data(cls, grid_type):
        try:
            data = PackGrid.select().dicts().where(PackGrid.slot_row.in_(constants.PACK_GRID_ROW_MAP[grid_type]))
            return data
        except (InternalError, IntegrityError) as e:
            logger.error("Error in db_get_pack_grid_data: {}".format(e))
            raise e

    @classmethod
    def db_get_pack_grid_id(cls, row, col):
        try:
            data = cls.select(cls.id).dicts().where((cls.slot_row == row), (cls.slot_column == col)).get()
            return data['id']
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_pack_grid_id_by_slot_number(cls, slot_number):
        try:
            query = PackGrid.select(PackGrid.id).where(PackGrid.slot_number == slot_number).get()
            return query.id
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def map_pack_location(cls, row, col):
        """
        @function: map_pack_location
        @createdBy: Manish Agarwal
        @createdDate: 7/22/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 08/12/2015
        @type: function
        @param: int,int
        @purpose - Map the slot row and slot col from
                  matrix index i,j to a pack location
        @input - 1,0
        @output - 14
        """
        query = PackGrid.select(PackGrid.slot_number).where(
            (PackGrid.slot_row == row) & (PackGrid.slot_column == col)).get()
        return query.slot_number
