from peewee import PrimaryKeyField, ForeignKeyField, CharField, InternalError, IntegrityError
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_group_master import GroupMaster

logger = settings.logger


class ReasonMaster(BaseModel):
    id = PrimaryKeyField()
    reason_group = ForeignKeyField(GroupMaster)
    reason = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "reason_master"

    @staticmethod
    def get_initial_data():
        return [
            dict(id=1, reason_group=6, reason="Broken Pill"),
            dict(id=2, reason_group=6, reason="Extra Pill Count"),
            dict(id=3, reason_group=6, reason="Missing Pill"),
            dict(id=4, reason_group=6, reason="Pill Misplaced")
        ]

    @classmethod
    def db_get_reasons(cls, reason_group):
        """
        Returns all reasons for a group

        :return: list
        """
        reasons = list()
        try:
            for record in ReasonMaster.select(ReasonMaster.id.alias('reason_id'),
                                              ReasonMaster.reason_group,
                                              ReasonMaster.reason).dicts()\
                    .where(ReasonMaster.reason_group == reason_group):
                reasons.append(record)
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

        return reasons