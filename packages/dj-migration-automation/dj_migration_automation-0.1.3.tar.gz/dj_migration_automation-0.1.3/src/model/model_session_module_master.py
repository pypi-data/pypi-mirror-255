from peewee import BooleanField, PrimaryKeyField, IntegerField, CharField, ForeignKeyField, \
    InternalError, IntegrityError, DataError
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_group_master import GroupMaster

logger = settings.logger


class SessionModuleMaster(BaseModel):
    id = PrimaryKeyField()
    session_module_type_id = ForeignKeyField(GroupMaster)
    screen_sequence = IntegerField()
    screen_name = CharField(max_length=100)
    screen_interaction = BooleanField()
    max_idle_time = IntegerField()
    company_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "session_module_master"

    @classmethod
    def get_module_param(cls, module_type_id: int, screen_sequence: int, company_id: int) -> dict:
        """
        @desc: Returns SessionModuleMaster table fields for provided parameters
        @param module_type_id:int
        @param screen_sequence:int
        @param company_id:int
        @return:dict
        """
        try:
            query = cls.select().dicts().where(cls.session_module_type_id == module_type_id,
                                               cls.screen_sequence == screen_sequence, cls.company_id == company_id)
            for record in query:
                return record
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise