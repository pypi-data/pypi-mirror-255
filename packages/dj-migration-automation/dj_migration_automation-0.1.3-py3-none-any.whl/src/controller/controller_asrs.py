import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from dosepack.utilities.validate_auth_token import authenticate
from dosepack.validation.validate import validate_request_args
from src.service.asrs import update_asrs_container_data, get_asrs_container_data, remove_asrs_packs
from src.service.asrs import update_pack_container


class ASRSContainerData(object):
    """
    This class contains methods to add, get and update the data in/from ContainerMaster table for ASRS.
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_asrs_container_data
            )
        else:
            return error(1001)

        return response

    @use_database(db, settings.logger)
    def GET(self, company_id: int = None, device_ids: list = None, **kwargs) -> dict:
        if company_id is None or device_ids is None:
            return error(1001, "Missing Parameter(s): company_id or device_ids.")

        args = {
            "company_id": company_id,
            "device_ids": device_ids
        }

        return get_asrs_container_data(args)


class RemoveASRSPacks(object):
    """
        Controller to remove packs from asrs container
    """
    exposed = True

    @authenticate(settings.logger)
    @use_database(db, settings.logger)
    def POST(self, **kwargs):
        # check if input argument kwargs is present
        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], remove_asrs_packs
            )
        else:
            return error(1001)
        return response


class UpdatePackContainer(object):
    """
    Controller to update ASRS container_id for pack.
    """
    exposed = True

    @use_database(db, settings.logger)
    def POST(self, **kwargs):

        if "args" in kwargs:
            response = validate_request_args(
                kwargs["args"], update_pack_container
            )
        else:
            return error(1001)

        return response
