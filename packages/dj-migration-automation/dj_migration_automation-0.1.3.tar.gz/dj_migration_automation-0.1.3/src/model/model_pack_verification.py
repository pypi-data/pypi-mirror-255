from peewee import IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, fn

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src.model.model_pack_details import PackDetails

logger = settings.logger


class PackVerification(BaseModel):

    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    pack_verified_status = ForeignKeyField(CodeMaster)
    created_by = IntegerField(default=1)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_verification"



def get_pack_verification_status_count(system_id, company_id, track_date, offset):
    """
        pvs_detection_problem_classification
    """
    try:
        pack_verification_data = []
        pack_id = []
        query = PackVerification.select(fn.Count(PackVerification.id).alias("count"),
                                        PackVerification.pack_verified_status.alias("pack_verified_status"),
                                        CodeMaster.value.alias("value"))\
            .join(CodeMaster, on=PackVerification.pack_verified_status == CodeMaster.id)\
            .where(fn.DATE(fn.CONVERT_TZ(PackVerification.created_date, settings.TZ_UTC,
            offset)) == track_date).group_by(PackVerification.pack_verified_status).dicts()

        query2 = PackVerification.select(PackVerification.pack_id.alias("pack_id"))\
            .where(fn.DATE(fn.CONVERT_TZ(PackVerification.created_date, settings.TZ_UTC,
            offset)) == track_date).dicts()

        for record in query:
            pack_verification_data.append(record)
        for record in query2:
            pack_id.append(record)

        return pack_verification_data, pack_id

    except (Exception) as e:
        logger.error("error in get_pack_verification_status_count {}".format(e))
        print(
            f"Error in get_pack_verification_status_count ")

        raise e