from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src.model.model_session_module_master import SessionModuleMaster

logger = settings.logger


class Session(BaseModel):
    id = PrimaryKeyField()
    session_module_id = ForeignKeyField(SessionModuleMaster)
    identifier_key = ForeignKeyField(CodeMaster)
    identifier_value = IntegerField(null=True)
    start_time = DateTimeField()
    end_time = DateTimeField(null=True)
    active_time = IntegerField(default=0)
    created_datetime = DateTimeField()
    modified_datetime = DateTimeField()
    user_id = IntegerField()
    system_id = IntegerField(null=True)
    company_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "session"

    @classmethod
    def get_session_data(cls, session_module_id: int = None, identifier_key: int = None, identifier_value: int = None,
                         user_id: int = None, system_id: int = None, company_id: int = None) -> dict:
        """
        Creates record if not already present returns record otherwise.
        @param session_module_id: int
        @param identifier_key: int
        @param identifier_value: int
        @param user_id: int
        @param system_id: int
        @param company_id: int
        @return: json and bool
        """
        try:
            logger.debug("In get_session_data")
            query = Session.select().dicts().where(cls.session_module_id == session_module_id,
                                                   cls.identifier_key == identifier_key,
                                                   cls.identifier_value == identifier_value, cls.user_id == user_id,
                                                   cls.system_id == system_id, cls.company_id == company_id,
                                                   cls.end_time.is_null(True))
            for record in query:
                return record
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def insert_session_data(cls, session_module_id: int = None, identifier_key: int = None,
                            identifier_value: int = None,
                            start_time: str = None, end_time: str = None, active_time: str = None, user_id: int = None,
                            system_id: int = None, company_id: int = None) -> int:
        """
        Creates record if not already present returns record otherwise.
        @param active_time:
        @param session_module_id: int
        @param identifier_key: int
        @param identifier_value: int
        @param start_time: datetime
        @param end_time: datetime
        @param active_time: int
        @param user_id: int
        @param system_id: int
        @param company_id: int
        @return: int
        """

        try:
            logger.debug("Inside insert_session_data")
            created_datetime = get_current_date_time()
            modified_datetime = created_datetime
            if active_time is None:
                active_time = 0
            if end_time is None:
                end_time

            query = Session.insert(session_module_id=session_module_id, identifier_key=identifier_key,
                                   identifier_value=identifier_value, active_time=active_time, start_time=start_time,
                                   end_time=end_time, user_id=user_id, system_id=system_id, company_id=company_id,
                                   created_datetime=created_datetime, modified_datetime=modified_datetime).execute()
            return query
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_session_data(cls, id: int = None, active_time: str = None, end_time: str = None) -> int:
        """
        @desc: To update Session table data with provided parameters
        @param id: int
        @param active_time: int
        @param end_time: datetime
        @return: int
        """
        try:
            logger.debug("In update_session_data")
            modified_datetime = get_current_date_time()
            if end_time is None:
                query = cls.update(active_time=active_time, modified_datetime=modified_datetime).where(
                    cls.id == id).execute()
                return query
            else:
                query = cls.update(active_time=active_time, end_time=end_time,
                                   modified_datetime=modified_datetime).where(
                    cls.id == id).execute()
                return query
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_session_id(cls, session_module_id: int = None) -> int:
        """
        Returns session_meta_id for corresponding session_module_master_id
        @param session_module_id: int
        @return: int
        """
        try:
            logger.debug("In get_session_id")
            query = cls.select().dicts().where(cls.session_module_id == session_module_id)
            for record in query:
                return record["id"]
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_start_id(cls, session_module_id: int) -> int:
        """
        To get the last id for the given module
        @param session_module_id: int
        """
        try:
            logger.debug("In get_start_id")
            start_id = None
            query = cls.select(cls.id).dicts() \
                .where(cls.identifier_value.is_null(False), cls.session_module_id == session_module_id) \
                .order_by(cls.id.desc()) \
                .limit(1)
            for record in query:
                start_id = record["id"]
            return start_id
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_identifier_value_for_select_facility(cls, start_id: int, identifier_value: int, end_id: int) -> int:
        """
        To update rows where identifier value is none for select facility screen.
        @param start_id: int
        @param identifier_value: int
        @param end_id: int
        @return:int
        """
        try:
            logger.debug("In update_identifier_value_for_select_facility")
            update_response = cls.update(identifier_value=identifier_value) \
                .where(cls.id.between(start_id, end_id)).execute()
            return update_response

        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise
