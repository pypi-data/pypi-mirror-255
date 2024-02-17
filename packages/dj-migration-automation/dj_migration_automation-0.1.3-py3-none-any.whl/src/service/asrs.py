import json

from peewee import InternalError, IntegrityError, DataError

import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate
from settings import FAILURE_RESPONSE
from src.dao.asrs_dao import get_packs_of_container, remove_packs_from_container, \
    add_pack_details_in_pack_history, validate_devices, get_container_data, validate_asrs_device, \
    update_container_for_pack, \
    get_asrs_storage_device, db_dissociate_container_from_device, db_verify_packlist_by_system, db_associate_container_with_device, \
    get_container_data_by_id, get_container_at_location
from src.dao.pack_dao import db_verify_packlist_by_company
from src.dao.device_manager_dao import validate_container_with_company
from src.exceptions import RemoveASRSPacksException

logger = settings.logger


@validate(required_fields=["system_id", "company_id", "device_id", "user_id"])
def update_asrs_container_data(asrs_container_data: dict) -> dict:
    """
    This is used to allocate an ASRS device to mentioned container_id
    @param: asrs_container_data_dict: dict
    @return: success
    """

    logger.debug("In update_asrs_container_data")

    system_id = int(asrs_container_data["system_id"])
    company_id = int(asrs_container_data["company_id"])
    device_id = int(asrs_container_data["device_id"])
    user_id = int(asrs_container_data["user_id"])
    associate_container_id = asrs_container_data.get("associate_container_id", None)
    dissociate_container_id = asrs_container_data.get("dissociate_container_id", None)
    associate_container_empty_status = asrs_container_data.get("associate_container_empty_status", None)  # if empty True  else false
    associate_container_position = asrs_container_data.get("associate_container_position", None)

    response = {"associate_status": None, "dissociate_status": None}
    if not system_id or not device_id or not company_id:
        return error(1001, "Missing Parameter(s): system_id or device_id or company_id.")

    if not associate_container_id and not dissociate_container_id:
        return error(1001, "Missing Parameter(s): associate_container_id and dissociate_container_id.")

    if associate_container_id and (associate_container_empty_status is None or associate_container_position is None):
        return error(1001, "Missing parameter associate_container_empty_status or associate_container_position.")
    try:
        with db.transaction():
            # validate device_id with company_id and system_id
            device_validation_status = validate_asrs_device(device_id=device_id, company_id=company_id,
                                                            system_id=system_id)
            logger.info("In update_asrs_container_data, ASRS device:" + str(device_id) + str(device_validation_status))
            if not device_validation_status:
                return error(1039)

            container_ids = list()
            if associate_container_id:
                container_ids.append(associate_container_id)
            if dissociate_container_id:
                container_ids.append(dissociate_container_id)
            container_validation_status = validate_container_with_company(container_ids=container_ids,
                                                                          company_id=company_id)
            logger.info("In update_asrs_container_data, ASRSContainer validated" + str(container_validation_status))
            if not container_validation_status:
                return error(1000, "Invalid company_id or container_id.")

            if dissociate_container_id:
                asrs_storage_device = get_asrs_storage_device(company_id)
                if not asrs_storage_device:
                    return error(1000, "Unable to find ASRS Storage device for given company_id.")

                dissociate_status = db_dissociate_container_from_device(container_id=dissociate_container_id,
                                                                        asrs_storage_device=asrs_storage_device,
                                                                        user_id=user_id)
                logger.info(f"In update_asrs_container_data, dissociate_status: {dissociate_status}")
                response["dissociate_status"] = dissociate_status

            if associate_container_id:
                # commenting below code as there are some cases in which detach container call can be missed,
                # and so we have to handle this call from our end. Physically iit s not possible to attach more containers
                # than available locations.
                # container_linked_with_device = get_containers_linked_with_device(device_id=device_id)
                # if container_linked_with_device and container_linked_with_device >= constants.ASRS_DEVICE_LINKED_CAPACITY:
                #     return error(1000, "More than 3 containers cannot be linked with device.")
                # else:

                # detach existing container if available at the particular location
                # checking container at position associate_container_position
                container_linked_with_device = get_container_at_location(device_id=device_id,
                                                                         position=associate_container_position)
                logger.debug("In update_asrs_container_data, fetched container_linked_with_device")
                if container_linked_with_device and "id" in container_linked_with_device:
                    logger.debug(
                        "In update_asrs_container_data, found container_linked_with_device so detaching container: {}".format(
                            container_linked_with_device["id"]))
                    # dissociate this associated container first
                    asrs_storage_device = get_asrs_storage_device(company_id)
                    if not asrs_storage_device:
                        return error(1000, "Unable to find ASRS Storage device for given company_id.")
                    dissociate_status = db_dissociate_container_from_device(container_id=container_linked_with_device["id"],
                                                                            asrs_storage_device=asrs_storage_device,
                                                                            user_id=user_id)
                    logger.debug("In update_asrs_container_data, detached container- {} with status".format(
                        container_linked_with_device["id"], dissociate_status))

                # fetch empty status of container
                container_data = get_container_data_by_id(container_id=associate_container_id)
                if not container_data:
                    return error(1020, "Invalid associate_container_id")

                container_empty_status = container_data[0].get("is_empty")  # true if container is empty else false

                with db.transaction():
                    logger.debug("In update_asrs_container_data: associate_container_empty_status is {} "
                                 "and container_empty_status is {}".format(associate_container_empty_status,
                                         container_empty_status))
                    if associate_container_empty_status and not container_empty_status:
                        # remove packs from container if there are packs in container in db but physically not there
                        logger.debug("update_asrs_container_data: removing packs from container - {}"
                                     " as associate_container_empty_status is {} and container_empty_status is {}"
                                     .format(associate_container_id, associate_container_empty_status,
                                             container_empty_status))
                        args = {"company_id": company_id, "user_id": user_id, "container_id": associate_container_id}
                        remove_packs_status = json.loads(remove_asrs_packs(args))
                        if remove_packs_status["status"] == FAILURE_RESPONSE:
                            raise RemoveASRSPacksException(remove_packs_status["description"])
                        logger.debug("update_asrs_container_data: ")
                    associate_status = db_associate_container_with_device(container_id=associate_container_id,
                                                                          device_id=device_id,
                                                                          user_id=user_id,
                                                                          container_position=associate_container_position
                                                                          )
                    logger.info(f"In update_asrs_container_data, associate_status: {associate_status}")
                response["associate_status"] = associate_status

            return create_response(response)
    except RemoveASRSPacksException as e:
        logger.error(e, exc_info=True)
        return error(1000,
                     "In update_asrs_container_data, Error while removing packs from associated container: " + str(e))
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["company_id", "user_id"])
def remove_asrs_packs(args):
    try:
        company_id = args["company_id"]
        user_id = args["user_id"]
        container_id = args.get("container_id")
        pack_ids = args.get("pack_ids")

        if not container_id and not pack_ids:
            return error(1001, "Missing Parameter(s): container_id or pack_ids.")

        if container_id:
            # validate container - is container_id valid or not
            logger.debug("validating container_id {} with company_id {}".format(container_id, company_id))
            valid_container = validate_container_with_company(container_ids=[container_id], company_id=company_id)
            if not valid_container:
                return error(9059)

            # fetch packs associated with container
            logger.debug("Fetching packs of given asrs container {}".format(container_id))
            pack_list = get_packs_of_container(container_id=container_id)
            if not pack_list:
                return create_response("No packs available in the container - {}".format(container_id))
        else:
            logger.debug("got pack_ids: "+str(pack_ids))
            pack_list = pack_ids

        logger.info("packs available in container {} : {}".format(container_id, pack_list))

        # update null container id in pack details of that packs
        logger.debug("removing packs from container " + str(container_id))
        update_pack_status = remove_packs_from_container(pack_list=pack_list)

        # add those packs in pack_history
        logger.debug("adding removed packs data in pack_history")
        update_pack_history_status = add_pack_details_in_pack_history(pack_ids=pack_list, user_id=user_id,
                                                                      container_id=container_id)
        logger.info("In remove_asrs_packs: data inserted in pack history table: {}".format(update_pack_history_status))
        return create_response(update_pack_status)

    except (InternalError, IntegrityError, DataError) as e:
        return error(2001, e)


@log_args_and_response
@validate(required_fields=["company_id", "device_ids"])
def get_asrs_container_data(args: dict) -> dict:
    """
    Fetches the containers of the ASRS and ASRS Storage devices.
    @param args:
    @return:
    """
    logger.debug("Inside get_asrs_container_data.")

    company_id = args["company_id"]
    device_ids = list(map(int, args["device_ids"].split(",")))
    try:
        # validate if the list of devices belong to the given company_id and are of the expected device_type.
        validation_status = validate_devices(device_ids=device_ids, company_id=company_id)

        if not validation_status:
            return error(9059)

        # get the container details for the given devices.
        container_data = get_container_data(device_ids=device_ids)

        return create_response(container_data)

    except (InternalError, IntegrityError, DataError) as e:
        return error(2001, e)


@validate(required_fields=["company_id", "system_id", "pack_id", "container_id"])
def update_pack_container(args):
    """
    Function to update ASRS container for given pack
    @param args: dict
    @return: json
    """
    logger.debug("In update_pack_container")
    logger.info("Input update_pack_container args {}".format(args))
    company_id = args["company_id"]
    system_id = args["system_id"]
    pack_id = args["pack_id"]
    container_id = args["container_id"]
    dry_run: bool = bool(args["dry_run"])

    if dry_run:
        create_response(1)

    valid_packlist_by_company = db_verify_packlist_by_company(company_id=company_id, pack_list=[pack_id])
    if not valid_packlist_by_company:
        return error(1026)

    valid_packlist_by_system = db_verify_packlist_by_system(system_id=system_id, pack_list=[pack_id])
    if not valid_packlist_by_system:
        return error(1014)

    response = update_container_for_pack(company_id=company_id,
                                         system_id=system_id,
                                         pack_id=pack_id,
                                         container_id=container_id)
    logger.info(response)

    return create_response(response)
