import json
import settings
from peewee import InternalError, IntegrityError, DataError, DoesNotExist
from src import constants
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate
from src.dao.canister_testing_dao import validate_canister_id_with_company_id

from src.dao.canister_dao import get_empty_locations_count_of_drawers_dao
from src.dao.csr_dao import get_csr_filters_data, get_csr_drawer_details, \
    get_container_id, get_canister_size_and_type, get_empty_location_for_given_canister, \
    get_top_drawer_empty_location_for_given_canister, get_serial_number_by_station_type_and_id
from src.dao.drug_dao import get_drawer_level_data_dao, get_csr_drawer_level_data_dao, \
    get_csr_location_level_data_dao
from src.dao.device_manager_dao import get_drawer_data_dao, validate_device_ids_with_company, \
    get_container_data_based_on_serial_numbers_dao, update_container_lock_status, \
    get_zone_wise_device_list, validate_device_id_dao

logger = settings.logger


@log_args_and_response
@validate(required_fields=["device_id", "company_id"])
def get_csr_filters(data_dict: dict) -> dict:
    """
    This function gets the filter data for the given CSR device.
    @return:
    """
    logger.debug("Inside the get_csr_filters.")

    device_id = int(data_dict["device_id"])
    company_id = int(data_dict["company_id"])

    try:
        # validate if the given device_id belongs to the given company_id
        valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
        if not valid_device:
            return error(1033)

        # get all the unique filter values for the given device_id and company_id.
        response = get_csr_filters_data(device_id=device_id, company_id=company_id)

        return create_response(response)

    except (DoesNotExist, DataError, IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["device_id", "company_id"])
def get_csr_data(csr_args: dict) -> dict:
    logger.debug("csr_args: " + str(csr_args))
    device_id = int(csr_args["device_id"])
    company_id = int(csr_args["company_id"])
    list_view = bool(int(csr_args.get("list_view", 0)))
    empty_locations = bool(int(csr_args.get("empty_locations", 0)))
    filter_fields = csr_args.get("filter_fields")
    sort_fields = csr_args.get("sort_fields")
    paginate = csr_args.get("paginate")
    response = dict()
    try:
        #   validate device_id and company_id
        logger.debug("validating device_id {} and company_id {}".format(device_id, company_id))
        if device_id and company_id:
            valid_devices = validate_device_ids_with_company(device_ids=[device_id], company_id=company_id)
            if not valid_devices:
                logger.error("Invalid device ID {} or company_id {}".format(device_id, company_id))
                return error(9059)

        if list_view:
            # if list view then send csr location level data
            logger.debug("list_view so fetching location level data")
            response = get_csr_location_level_data_dao(device_id=device_id, filter_fields=filter_fields,
                                                       sort_fields=sort_fields, paginate=paginate)
            logger.debug("drawers data fetched")

        else:
            # grid view so return drawer level data
            logger.debug("grid view so fetching csr drawer level data")
            drawer_ids = list()
            if filter_fields:
                # when filter or search applied then we have highlighted only filtered drawers
                logger.debug("fetching drawer level data based on filters")
                filtered_drawer_data = get_csr_drawer_level_data_dao(device_id=device_id, filter_fields=filter_fields,
                                                                     sort_fields=sort_fields, paginate=paginate)
                drawers_to_highlight = [drawer["id"] for drawer in filtered_drawer_data]
                logger.debug("drawers_to_highlight: " + str(drawers_to_highlight))
                filtered_shelf_list = [str(drawer["drawer_name"]).split('-')[1] for drawer in filtered_drawer_data]
                logger.debug("filtered_shelf_list: " + str(filtered_shelf_list))
                drawers_data = get_drawer_data_dao(device_id=device_id, shelf_list=filtered_shelf_list)
                for drawer in drawers_data:
                    drawer_ids.append(drawer["id"])
                    if drawer["id"] in drawers_to_highlight:
                        drawer["to_be_highlight"] = True
                    else:
                        drawer["to_be_highlight"] = False
            else:
                # when no filter or search applied in csr screen then highlight all drawers
                logger.debug("fetching drawer level data without filters")
                drawers_data = get_drawer_data_dao(device_id=device_id, shelf_list=None)
                for drawer in drawers_data:
                    drawer_ids.append(drawer["id"])
                    drawer["to_be_highlight"] = True

            if empty_locations:
                logger.debug("fetching empty locations count drawer wise")
                drawer_empty_locations_data = get_empty_locations_count_of_drawers_dao(drawer_ids=drawer_ids)

                # modified the retrieval by making use of get method for dictionary because we had a mismatch in the
                # length of "drawers_data" and "drawer_empty_locations_data" because we have applied the filter to
                # obtain only those empty locations that are enabled
                drawers_data = [dict(drawer, empty_locations_count=drawer_empty_locations_data.get(drawer["id"], 0))
                                for drawer in drawers_data]
            response["drawers_data"] = drawers_data
        return create_response(response)
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["drawer_name", "device_id", "company_id"])
def get_csr_drawer_data(data_dict: dict) -> dict:
    """
    This function gets the canister and location based data for the given CSR drawer.
    @param data_dict: dict
    @return:
    """
    logger.debug("Inside the get_csr_drawer_data.")

    filter_fields = data_dict.get('filter_fields', None)
    device_id = int(data_dict["device_id"])
    company_id = int(data_dict["company_id"])
    # display_locations = None
    # list for drawer_name(s)
    drawer_name_list = data_dict["drawer_name"].split(",")

    try:
        # validate if the given device_id belongs to the given company_id
        valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
        if not valid_device:
            return error(1033)

        # get the container id for the given set of drawer and device
        container_id_list = get_container_id(drawer_name_list=drawer_name_list, device_id=device_id)
        if len(container_id_list) == 0:
            return error(1000, "Invalid drawer_name or device_id.")
        # get the details of the canisters placed in all the locations of a given drawer
        drawer_details = get_csr_drawer_details(container_id_list=container_id_list,
                                                filter_fields=filter_fields)

        if filter_fields:
            filtered_canister_data = get_drawer_level_data_dao(container_id_list=container_id_list,
                                                               filter_fields=filter_fields)
            filtered_canister_locations = [record['location_id'] for record in filtered_canister_data]
        else:
            filtered_canister_locations = []
        response_list = []
        for record in drawer_details:
            is_searched: bool = False
            # if the canister is searched it should be highlighted so the below check
            if record['location_id'] in filtered_canister_locations:
                is_searched = True
            record["is_searched"] = is_searched
            response_list.append(record)

        return create_response(response_list)
    except (DoesNotExist, DataError, IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
@validate(required_fields=["canister_id", "device_id", "company_id"])
def recommend_csr_location(data_dict: dict) -> str:
    """
    This function recommends the csr drawer for the given canister.
    @param data_dict:
    @return:
    """
    logger.debug("Inside recommend_csr_location.")
    canister_id = int(data_dict["canister_id"])
    device_id = int(data_dict["device_id"])
    company_id = int(data_dict["company_id"])
    reserved_location_list = data_dict.get('reserved_location_list', [])
    recommend_top_drawer = data_dict.get('recommend_top_drawer', False)
    call_from_robot = data_dict.get('call_from_robot', False)
    system_id = data_dict.get('system_id', None)

    try:
        # validate if the given device_id belongs to the given company_id
        valid_device = validate_device_id_dao(device_id=device_id, company_id=company_id)
        if not valid_device:
            return error(1033)

        # validate if the given canister belongs to the given company_id
        valid_canister = validate_canister_id_with_company_id(canister_id=canister_id, company_id=company_id)
        if not valid_canister:
            return error(1038)

        # get csr device id if call is from robot
        if call_from_robot:
            if not system_id:
                return error(1001, "system_id missing")
            csr_device_ids = get_zone_wise_device_list(company_id, [settings.DEVICE_TYPES['CSR']], system_id)
            device_id = csr_device_ids[0]

        # get the canister size and canister type of the given canister
        canister_data = get_canister_size_and_type(canister_id=canister_id)
        usage_key = canister_data["canister_type"]
        size_key = canister_data["canister_size"]

        if recommend_top_drawer:
            # get top drawer empty location for given canister
            if size_key == constants.SIZE_OR_TYPE_BIG:
                drawer_size = [constants.SIZE_OR_TYPE_BIG]
            else:
                drawer_size = [constants.SIZE_OR_TYPE_BIG, constants.SIZE_OR_TYPE_SMALL]
            response_dict = get_top_drawer_empty_location_for_given_canister(size_key=drawer_size,
                                                                             device_id=device_id,
                                                                             reserved_location_list=reserved_location_list)

        else:
            # get an empty location for the given canister size and usage.
            response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                  device_id=device_id,
                                                                  reserved_location_list=reserved_location_list)

        # recommend big csr drawer with appropriate usage for big canister
        if not response_dict and size_key == constants.SIZE_OR_TYPE_BIG:
            response_dict = get_appropriate_csr_drawer_for_big_canister(device_id=device_id,
                                                                        size_key=size_key, usage_key=usage_key,
                                                                        reserved_location_list=reserved_location_list)

        # recommend big or small csr appropriate drawer for small canister
        if not response_dict and size_key == constants.SIZE_OR_TYPE_SMALL:
            response_dict = get_appropriate_csr_drawer_for_small_canister(device_id=device_id,
                                                                          usage_key=usage_key,
                                                                          reserved_location_list=reserved_location_list)

        # if not getting an empty location for the given usage type and size
        if not response_dict:
            return error(9060)

        response_dict["canister_id"] = canister_id
        return create_response(response_dict)

    except (DoesNotExist, DataError, IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        return error(2001)


def get_appropriate_csr_drawer_for_small_canister(device_id, usage_key, reserved_location_list,company_id=None,response_dict=None):
    try:
        if usage_key == constants.USAGE_FAST_MOVING:
            # Big-F > Small-MF > Big-MF > Small-MS > Big-MS > small-S > Big-S
            size_key = constants.SIZE_OR_TYPE_BIG
            # Big - fast moving
            response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                  device_id=device_id,
                                                                  reserved_location_list=reserved_location_list)
            if not response_dict:
                # small - med. fast moving
                size_key = constants.SIZE_OR_TYPE_SMALL
                usage_key = constants.USAGE_MEDIUM_FAST_MOVING
                response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                      device_id=device_id,
                                                                      reserved_location_list=reserved_location_list)
                if not response_dict:
                    # big - med. fast
                    size_key = constants.SIZE_OR_TYPE_BIG
                    usage_key = constants.USAGE_MEDIUM_FAST_MOVING
                    response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                          device_id=device_id,
                                                                          reserved_location_list=reserved_location_list)
                    if not response_dict:
                        # small - med. slow
                        size_key = constants.SIZE_OR_TYPE_SMALL
                        usage_key = constants.USAGE_MEDIUM_SLOW_MOVING
                        response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                              usage_key=usage_key,
                                                                              device_id=device_id,
                                                                              reserved_location_list=
                                                                              reserved_location_list)
                        if not response_dict:
                            # big- med. slow
                            size_key = constants.SIZE_OR_TYPE_BIG
                            usage_key = constants.USAGE_MEDIUM_SLOW_MOVING
                            response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                  usage_key=usage_key,
                                                                                  device_id=device_id,
                                                                                  reserved_location_list=
                                                                                  reserved_location_list)
                            if not response_dict:
                                # small - slow
                                size_key = constants.SIZE_OR_TYPE_SMALL
                                usage_key = constants.USAGE_SLOW_MOVING
                                response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                      usage_key=usage_key,
                                                                                      device_id=device_id,
                                                                                      reserved_location_list=
                                                                                      reserved_location_list)
                                if not response_dict:
                                    # big - slow
                                    size_key = constants.SIZE_OR_TYPE_BIG
                                    usage_key = constants.USAGE_SLOW_MOVING
                                    response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                          usage_key=usage_key,
                                                                                          device_id=device_id,
                                                                                          reserved_location_list=
                                                                                          reserved_location_list)

        elif usage_key == constants.USAGE_MEDIUM_FAST_MOVING:
            # Big-MF > Small-MS > Big-MS > small-S > Big-S > Small- F > Big-F
            size_key = constants.SIZE_OR_TYPE_BIG
            # Big - med. fast moving
            response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                  device_id=device_id,
                                                                  reserved_location_list=reserved_location_list)
            if not response_dict:
                # small - med. slow moving
                size_key = constants.SIZE_OR_TYPE_SMALL
                usage_key = constants.USAGE_MEDIUM_SLOW_MOVING
                response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                      device_id=device_id,
                                                                      reserved_location_list=reserved_location_list)
                if not response_dict:
                    # big - med. slow
                    size_key = constants.SIZE_OR_TYPE_BIG
                    usage_key = constants.USAGE_MEDIUM_SLOW_MOVING
                    response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                          device_id=device_id,
                                                                          reserved_location_list=reserved_location_list)
                    if not response_dict:
                        # small - slow
                        size_key = constants.SIZE_OR_TYPE_SMALL
                        usage_key = constants.USAGE_SLOW_MOVING
                        response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                              usage_key=usage_key,
                                                                              device_id=device_id,
                                                                              reserved_location_list=
                                                                              reserved_location_list)
                        if not response_dict:
                            # big- slow
                            size_key = constants.SIZE_OR_TYPE_BIG
                            usage_key = constants.USAGE_SLOW_MOVING
                            response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                  usage_key=usage_key,
                                                                                  device_id=device_id,
                                                                                  reserved_location_list=
                                                                                  reserved_location_list)
                            if not response_dict:
                                # small - fast
                                size_key = constants.SIZE_OR_TYPE_SMALL
                                usage_key = constants.USAGE_FAST_MOVING
                                response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                      usage_key=usage_key,
                                                                                      device_id=device_id,
                                                                                      reserved_location_list=
                                                                                      reserved_location_list)
                                if not response_dict:
                                    # big - fast
                                    size_key = constants.SIZE_OR_TYPE_BIG
                                    usage_key = constants.USAGE_FAST_MOVING
                                    response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                          usage_key=usage_key,
                                                                                          device_id=device_id,
                                                                                          reserved_location_list=
                                                                                          reserved_location_list)
        elif usage_key == constants.USAGE_MEDIUM_SLOW_MOVING:
            # Big-MS > small-Slow > Big-Slow  > Small- med.F > Big- med. F > small- fast > big-fast
            size_key = constants.SIZE_OR_TYPE_BIG
            # Big - med. slow moving
            response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                  device_id=device_id,
                                                                  reserved_location_list=reserved_location_list)
            if not response_dict:
                # small - slow moving
                size_key = constants.SIZE_OR_TYPE_SMALL
                usage_key = constants.USAGE_SLOW_MOVING
                response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                      device_id=device_id,
                                                                      reserved_location_list=reserved_location_list)
                if not response_dict:
                    # big - slow
                    size_key = constants.SIZE_OR_TYPE_BIG
                    usage_key = constants.USAGE_SLOW_MOVING
                    response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                          device_id=device_id,
                                                                          reserved_location_list=reserved_location_list)
                    if not response_dict:
                        # small - med. fast
                        size_key = constants.SIZE_OR_TYPE_SMALL
                        usage_key = constants.USAGE_MEDIUM_FAST_MOVING
                        response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                              usage_key=usage_key,
                                                                              device_id=device_id,
                                                                              reserved_location_list=
                                                                              reserved_location_list)
                        if not response_dict:
                            # big- med. fast
                            size_key = constants.SIZE_OR_TYPE_BIG
                            usage_key = constants.USAGE_MEDIUM_FAST_MOVING
                            response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                  usage_key=usage_key,
                                                                                  device_id=device_id,
                                                                                  reserved_location_list=
                                                                                  reserved_location_list)
                            if not response_dict:
                                # small - fast
                                size_key = constants.SIZE_OR_TYPE_SMALL
                                usage_key = constants.USAGE_FAST_MOVING
                                response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                      usage_key=usage_key,
                                                                                      device_id=device_id,
                                                                                      reserved_location_list=
                                                                                      reserved_location_list)
                                if not response_dict:
                                    # big - fast
                                    size_key = constants.SIZE_OR_TYPE_BIG
                                    usage_key = constants.USAGE_FAST_MOVING
                                    response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                          usage_key=usage_key,
                                                                                          device_id=device_id,
                                                                                          reserved_location_list=
                                                                                          reserved_location_list)
        else:
            # For small-slow: Big-slow > Small-MS > Big-MS > small- med fast > Big- med. fast > Small- F > Big-F
            size_key = constants.SIZE_OR_TYPE_BIG
            # Big - slow moving
            response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                  device_id=device_id,
                                                                  reserved_location_list=reserved_location_list)
            if not response_dict:
                # small - med. slow moving
                size_key = constants.SIZE_OR_TYPE_SMALL
                usage_key = constants.USAGE_MEDIUM_SLOW_MOVING
                response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                      device_id=device_id,
                                                                      reserved_location_list=reserved_location_list)
                if not response_dict:
                    # big - med. slow
                    size_key = constants.SIZE_OR_TYPE_BIG
                    usage_key = constants.USAGE_MEDIUM_SLOW_MOVING
                    response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                          device_id=device_id,
                                                                          reserved_location_list=reserved_location_list)
                    if not response_dict:
                        # small - med. fast
                        size_key = constants.SIZE_OR_TYPE_SMALL
                        usage_key = constants.USAGE_MEDIUM_FAST_MOVING
                        response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                              usage_key=usage_key,
                                                                              device_id=device_id,
                                                                              reserved_location_list=
                                                                              reserved_location_list)
                        if not response_dict:
                            # big- med fast
                            size_key = constants.SIZE_OR_TYPE_BIG
                            usage_key = constants.USAGE_MEDIUM_FAST_MOVING
                            response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                  usage_key=usage_key,
                                                                                  device_id=device_id,
                                                                                  reserved_location_list=
                                                                                  reserved_location_list)
                            if not response_dict:
                                # small - fast
                                size_key = constants.SIZE_OR_TYPE_SMALL
                                usage_key = constants.USAGE_FAST_MOVING
                                response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                      usage_key=usage_key,
                                                                                      device_id=device_id,
                                                                                      reserved_location_list=
                                                                                      reserved_location_list)
                                if not response_dict:
                                    # big - fast
                                    size_key = constants.SIZE_OR_TYPE_BIG
                                    usage_key = constants.USAGE_FAST_MOVING
                                    response_dict = get_empty_location_for_given_canister(size_key=size_key,
                                                                                          usage_key=usage_key,
                                                                                          device_id=device_id,
                                                                                          reserved_location_list=
                                                                                          reserved_location_list)
        return response_dict
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e


@log_args_and_response
def get_appropriate_csr_drawer_for_big_canister(device_id, size_key, usage_key,
                                                reserved_location_list, company_id=None, response_dict=None):
    try:
        if usage_key == constants.USAGE_FAST_MOVING:
            # big - MF > big - MS > big - S
            usage_key = constants.USAGE_MEDIUM_FAST_MOVING
            response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                  device_id=device_id,
                                                                  reserved_location_list=reserved_location_list)
            if not response_dict:
                usage_key = constants.USAGE_MEDIUM_SLOW_MOVING
                response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                      device_id=device_id,
                                                                      reserved_location_list=reserved_location_list)
                if not response_dict:
                    usage_key = constants.USAGE_SLOW_MOVING
                    response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                          device_id=device_id,
                                                                          reserved_location_list=reserved_location_list)
        elif usage_key == constants.USAGE_MEDIUM_FAST_MOVING:
            # big - MS > big - S > big - F
            usage_key = constants.USAGE_MEDIUM_SLOW_MOVING
            response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                  device_id=device_id,
                                                                  reserved_location_list=reserved_location_list)
            if not response_dict:
                usage_key = constants.USAGE_SLOW_MOVING
                response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                      device_id=device_id,
                                                                      reserved_location_list=reserved_location_list)
                if not response_dict:
                    usage_key = constants.USAGE_FAST_MOVING
                    response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                          device_id=device_id,
                                                                          reserved_location_list=reserved_location_list)

        elif usage_key == constants.USAGE_MEDIUM_SLOW_MOVING:
            # big - S > big - MF > big - F
            usage_key = constants.USAGE_SLOW_MOVING
            response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                  device_id=device_id,
                                                                  reserved_location_list=reserved_location_list)
            if not response_dict:
                usage_key = constants.USAGE_MEDIUM_FAST_MOVING
                response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                      device_id=device_id,
                                                                      reserved_location_list=reserved_location_list)
                if not response_dict:
                    usage_key = constants.USAGE_FAST_MOVING
                    response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                          device_id=device_id,
                                                                          reserved_location_list=reserved_location_list)
        else:
            # big - MS > big - MF > big - F
            usage_key = constants.USAGE_MEDIUM_SLOW_MOVING
            response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                  device_id=device_id,
                                                                  reserved_location_list=reserved_location_list)
            if not response_dict:
                usage_key = constants.USAGE_MEDIUM_FAST_MOVING
                response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                      device_id=device_id,
                                                                      reserved_location_list=reserved_location_list)
                if not response_dict:
                    usage_key = constants.USAGE_FAST_MOVING
                    response_dict = get_empty_location_for_given_canister(size_key=size_key, usage_key=usage_key,
                                                                          device_id=device_id,
                                                                          reserved_location_list=reserved_location_list)
        return response_dict
    except (DataError, IntegrityError, InternalError, Exception) as e:
        logger.error(e, exc_info=True)
        raise e

@log_args_and_response
def csr_emlock_status_callback_v3(emlock_status: bool, station_type: int, station_id: str) -> dict:
    try:
        # fetch container_id based on station_type and station_id
        logger.debug("fetching container_id based on station_type and station_id")
        actual_station_id = station_id[:-1]
        container_id = None
        try:
            # get container serial number based on station_type and station_id
            container_serial_number = get_serial_number_by_station_type_and_id(station_type=int(station_type),
                                                                                     station_id=actual_station_id,
                                                                                     container_serial_number=True,
                                                                                     device_serial_number=False)
        except ValueError as e:
            logger.error(e)
            return error(9062)
        # fetch container_data based on container serial number
        container_data = get_container_data_based_on_serial_numbers_dao(serial_numbers=[container_serial_number])
        if not container_data:
            return error(9063)
        for container in container_data:
            if container["serial_number"] == container_serial_number:
                container_id = container["id"]
                break
        logger.debug("fetched container_id and now updating em lock status of container- " + str(container_id))
        # update lock status based on container_id
        response = update_container_lock_status(container_id=container_id, emlock_status=emlock_status)
        logger.debug("updated em lock status for container: " + str(container_id))
        return create_response(response)

    except (IntegrityError, InternalError) as e:
        logger.info("Error in csr_emlock_status_callback_v3: {}".format(e))
        return error(2001)
    except DoesNotExist as e:
        logger.info("Error in csr_emlock_status_callback_v3: {}".format(e))
        return error(9063)
    except DataError as e:
        logger.info("Error in csr_emlock_status_callback_v3: {}".format(e))
        return error(1020)


@log_args_and_response
def guided_recommend_csr_drawers_to_unlock(company_id: int, device_id: int, canister_id_list: list,
                                           transfer_data) -> tuple:
    """
    Function to get empty locations of CSR to place canisters
    @param transfer_data:
    @param company_id:
    @param device_id:
    @param canister_id_list:
    @return:
    """
    try:
        drawer_to_unlock = dict()
        reserve_location_list = list()
        input_args = {'device_id': device_id,
                      'company_id': company_id}

        for index, canister_id in enumerate(canister_id_list):
            input_args['canister_id'] = canister_id
            input_args['reserved_location_list'] = reserve_location_list
            response = recommend_csr_location(input_args)
            loaded_response = json.loads(response)
            logger.info("recommend_csr_drawers_to_unlock loaded response {}".format(loaded_response))
            location_id = loaded_response['data']['location_id']
            reserve_location_list.append(location_id)
            if loaded_response['data']["drawer_name"] not in drawer_to_unlock.keys():
                drawer_to_unlock[loaded_response['data']["drawer_name"]] = {
                                        'id': loaded_response['data']["container_id"],
                                          'drawer_name': loaded_response['data']["drawer_name"],
                                    'serial_number': loaded_response['data']["serial_number"],
                                    'ip_address': loaded_response['data']["ip_address"],
                                    'secondary_ip_address': loaded_response['data']["secondary_ip_address"],
                                    'device_type_id': settings.DEVICE_TYPES['CSR'],
                                    'shelf': loaded_response['data']['shelf'],
                                    'to_device': list(),
                                    'from_device': list()
                    }

            if loaded_response['data']["drawer_name"]:
                transfer_data[index]['drawer_name'] = str(loaded_response['data']["drawer_name"])
                transfer_data[index]['dest_display_location'] = str(loaded_response['data']["display_location"])
            drawer_to_unlock[loaded_response['data']["drawer_name"]]["to_device"].append(
                loaded_response['data']["display_location"])

        return drawer_to_unlock, transfer_data

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in recommend_csr_drawers_to_unlock {}".format(e))
        raise error(2001)

    except Exception as e:
        logger.error("Error in recommend_csr_drawers_to_unlock {}".format(e))
        raise error(1000, "Error in recommend_csr_drawers_to_unlock")
