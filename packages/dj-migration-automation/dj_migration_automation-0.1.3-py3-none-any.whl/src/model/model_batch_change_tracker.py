import ast
import json

from peewee import (DateTimeField, PrimaryKeyField, ForeignKeyField, TextField, IntegerField, InternalError,
                    IntegrityError)
import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
from src.model.model_action_master import ActionMaster
from src.model.model_batch_master import BatchMaster

logger = settings.logger


class BatchChangeTracker(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster, null=True)
    action_id = ForeignKeyField(ActionMaster)
    input_params = TextField(null=True)  # parameters that are applied on batch
    # e.g. {"canister_id": 1, "alt_canister_id": 10}
    packs_affected = TextField(null=True)  # if partial packs are affected, then store it
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_change_tracker"

    @classmethod
    def db_save(cls, batch_id, user_id, action_id, params=None, packs_affected=None):
        """
        Stores action taken on batch and parameters that affected batch
        - `params` and `packs_affected` must be json serializable
        :param batch_id:
        :param user_id:
        :param action_id: id or instance of `ActionMaster`
        :param params: parameters as input that were applied on batch
        :param packs_affected: None if whole batch is modified (to remove unnecessary data), and list of packs if partially updated
        :return: `model_pack.BatchChangeTracker`
        """
        try:
            if params:
                params = json.dumps(params)
            if packs_affected:
                packs_affected = list(set(packs_affected))
                packs_affected = json.dumps(packs_affected)
            return cls.create(
                batch_id=batch_id,
                action_id=action_id,
                input_params=params,
                packs_affected=packs_affected,
                created_by=user_id,
            )
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise


def get_batch_id_by_action_id(batch_list):
    skip_pack_details = []

    query = BatchChangeTracker.select(BatchChangeTracker.packs_affected.alias("packs_affected")) \
        .where(BatchChangeTracker.action_id << [6, 50],
               BatchChangeTracker.batch_id << batch_list,
               BatchChangeTracker.packs_affected.is_null(False)).dicts()

    for record in query:
        packs = ast.literal_eval(record["packs_affected"])
        for pack in packs:
            skip_pack_details.append(pack)


    return skip_pack_details