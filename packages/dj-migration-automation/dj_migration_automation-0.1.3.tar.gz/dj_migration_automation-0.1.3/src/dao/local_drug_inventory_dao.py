from typing import Dict, List, Any, Optional
import settings
from peewee import InternalError, IntegrityError, DataError, DoesNotExist

from dosepack.utilities.utils import log_args, log_args_and_response
from src.model.model_local_di_data import LocalDIData
from src.model.model_local_di_po_data import LocalDIPOData
from src.model.model_local_di_transaction import LocalDITransaction

logger = settings.logger


@log_args_and_response
def local_di_get_inventory_data(fndc_txr_list: Optional[List[str]] = None, ndc_list: Optional[List[str]] = None,
                                txr_list: Optional[List[str]] = None,
                                qty_greater_than_zero: Optional[bool] = False) -> List[Any]:
    """
    Returns the data of the local inventory based on the given list of fndc_txr or ndc or both or none.
    """
    try:
        return LocalDIData.get_data(fndc_txr_list=fndc_txr_list, ndc_list=ndc_list, txr_list=txr_list,
                                    qty_greater_than_zero=qty_greater_than_zero)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in local_di_get_inventory_data {}".format(e))
        raise e


@log_args_and_response
def local_di_insert_inventory_data(data_list: List[Dict[str, Any]]) -> bool:
    """
    Inserts multiple records in the LocalDIData.
    """
    try:
        return LocalDIData.insert_data(data_list=data_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in local_di_insert_inventory_data {}".format(e))
        raise e


@log_args
def local_di_update_inventory_by_ndc(update_dict: Dict[str, Any], ndc: str) -> bool:
    """
    Updates the data in the LocalDIData by ndc.
    """
    try:
        return LocalDIData.update_by_ndc(update_dict=update_dict, ndc=ndc)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in local_di_update_inventory_by_ndc {}".format(e))
        raise e


@log_args_and_response
def local_di_insert_txn_data(data_list: List[Dict[str, Any]]) -> bool:
    """
    Inserts multiple records in the LocalDITransaction.
    """
    try:
        return LocalDITransaction.insert_data(data_list=data_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in local_di_insert_txn_data {}".format(e))
        raise e


@log_args_and_response
def local_di_insert_po_data(data_list: List[Dict[str, Any]]) -> bool:
    """
   Inserts multiple records in the LocalDIPOData.
   """
    try:
        return LocalDIPOData.insert_data(data_list=data_list)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in local_di_insert_po_data {}".format(e))
        raise e


@log_args_and_response
def local_di_get_po_data(created_after_date: Optional[str] = None) -> List[Any]:
    """
    Returns the po data for that are created after the mentioned date.
    """
    try:
        return LocalDIPOData.get_data(created_after_date=created_after_date)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in local_di_get_po_data {}".format(e))
        raise e
