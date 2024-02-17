from typing import Dict

from peewee import InternalError, IntegrityError, DoesNotExist, DataError

import settings
from settings import logger
from src.model.model_drug_master import DrugMaster
from src.model.model_drug_status import DrugStatus
from src.model.model_unique_drug import UniqueDrug


def update_unique_drug_based_on_drug_status() -> bool:
    """
    Updates the active drug_id in the unique drug table if available.
    """
    fndc_txr_dict: Dict[str, int] = dict()
    try:
        # get the Unique drug data for which the drug_id is inactive.
        query1 = UniqueDrug.select(UniqueDrug.concated_fndc_txr_field("##").alias("fndc_txr"),
                                   UniqueDrug.id.alias("unique_drug_id")).dicts() \
            .join(DrugStatus, on=UniqueDrug.drug_id == DrugStatus.drug_id) \
            .where(DrugStatus.ext_status == settings.INVALID_EXT_STATUS)

        if len(query1) > 0:
            for data1 in query1:
                fndc_txr_dict[data1["fndc_txr"]] = data1["unique_drug_id"]

            # get the active drug id for the set of fndc_txr.
            query2 = DrugMaster.select(DrugMaster.concated_fndc_txr_field(sep="##").alias("fndc_txr"),
                                       DrugMaster.id.alias("drug_id")).dicts() \
                .join(DrugStatus, on=DrugStatus.drug_id == DrugMaster.id) \
                .where(DrugStatus.ext_status == settings.VALID_EXT_STATUS,
                       DrugMaster.concated_fndc_txr_field(sep="##").in_(list(fndc_txr_dict.keys())))

            if len(query2) > 0:
                # update the active drug id in the unique_drug_table
                for data2 in query2:
                    UniqueDrug.db_update_drug_id_by_id(unique_drug_id=fndc_txr_dict[data2["fndc_txr"]],
                                                       drug_id=data2["drug_id"])
        return True

    except (InternalError, IntegrityError, DoesNotExist, DataError) as e:
        logger.error("Error in update_unique_drug_based_on_drug_status".format(e))
        raise
