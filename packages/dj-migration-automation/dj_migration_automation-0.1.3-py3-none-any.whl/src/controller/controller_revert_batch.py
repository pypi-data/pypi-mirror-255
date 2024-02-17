import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.validation.validate import validate_request_args
from src.service.revert_batch import revert_batch_v3


class RevertBatchV3(object):
    """
    Class contains methods to delete and update data from batch related tables to revert batch
    """
    # todo: This API not to be used in production for reverting batch because for below cases MFD canisters are to
    #  be marked as RTS done and after that user can proceed to revert batch:
    #  1) When MFD canisters are filled and at MVS
    #  2) MFD canisters at MFS and filling is pending
    #  3) MFD canisters are in trolley for transfer to robot

    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(kwargs["args"], revert_batch_v3)
            return response

        else:
            return error(1001)
