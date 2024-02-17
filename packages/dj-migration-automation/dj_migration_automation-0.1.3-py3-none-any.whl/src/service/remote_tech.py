from peewee import InternalError, IntegrityError, DoesNotExist, DataError
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate
from src import constants
from src.dao.remote_tech_dao import (get_pvs_and_rts_slot_data, get_pvs_and_rts_slot_details_data, get_unique_drug_id,
                                     add_remote_tech_slot_details_data, validate_pvs_slot_id, add_remote_tech_slot_data,
                                     get_pvs_slot_details, get_drug_data, remote_screen_data,
                                     get_rts_status_for_skipped, update_remote_tech_slot, assign_rts_to_given_user,
                                     rts_user_progress_data, assign_remote_tech_slots,
                                     assign_rts_slots_of_inactive_users,
                                     change_drug_queue_status_in_rts_slot_assign_info)

logger = settings.logger


@log_args_and_response
@validate(required_fields=["pack_id", "pack_grid_id", "pvs_slot_id", "remote_tech_id", "remote_tech_mapping",
                           "remote_tech_verification_status", "start_time", "end_time"])
def add_remote_tech_data(remote_tech_data: dict) -> dict:
    """
    This populates the RemoteTechSlot and RemoteTechSlotDetails
    @param remote_tech_data:
    @return:success
    """
    logger.debug('Test commit')
    logger.debug("Inside the add_remote_tech_data function: {}".format(remote_tech_data))

    pack_id = remote_tech_data["pack_id"]
    pack_grid_id = remote_tech_data["pack_grid_id"]
    pvs_slot_id = remote_tech_data["pvs_slot_id"]
    remote_tech_id = remote_tech_data["remote_tech_id"]
    remote_tech_verification_status = remote_tech_data["remote_tech_verification_status"]
    start_time = remote_tech_data["start_time"]
    end_time = remote_tech_data["end_time"]
    remote_tech_mapping = remote_tech_data["remote_tech_mapping"]
    try:
        with db.transaction():
            # # Validate the pvs_slot_id based on the pack_id and pack_grid_id
            validation_status = validate_pvs_slot_id(pvs_slot_id=pvs_slot_id)
            if validation_status:
                logger.info("pvs_slot_id: " + str(pvs_slot_id) + " validated")
            else:
                logger.info("No entry present for the pvs_slot_id: " + str(pvs_slot_id))
                return error(2008, "pvs_slot_id : " + str(pvs_slot_id))
            # Verify if the RTS_USER_SKIPPED or RTS_SYSTEM_SKIPPED entry is present in RemoteTechSlot for the
            # RTS_SKIPPED_MAPPED status
            if remote_tech_verification_status == constants.RTS_SKIPPED_MAPPED:
                valid_entry = get_rts_status_for_skipped(pvs_slot_id=pvs_slot_id, remote_tech_id=remote_tech_id)
                if valid_entry:
                    update_remote_tech_slot_status = update_remote_tech_slot(pvs_slot_id=pvs_slot_id)

                else:
                    return error(8006)

            # Preparing the dictionary for inserting data in the RemoteTechSlot table
            remote_tech_slot_data = {"pvs_slot_id": pvs_slot_id,
                                     "remote_tech_id": remote_tech_id,
                                     "verification_status": remote_tech_verification_status,
                                     "start_time": start_time,
                                     "end_time": end_time}

            # Populating the data in the RemoteTechSlot table
            remote_tech_slot_id = add_remote_tech_slot_data(remote_tech_slot_data)
            logger.info("inserted remote_tech_slot_id:" + str(remote_tech_slot_id))
            if remote_tech_mapping:
                if remote_tech_verification_status in [constants.RTS_VERIFIED, constants.RTS_REJECTED,
                                                       constants.RTS_NOT_SURE, constants.RTS_SKIPPED_MAPPED]:
                    # Get pvs_slot_details_id based on the pvs_slot_id
                    pvs_slot_details_data = get_pvs_slot_details(pvs_slot_id=pvs_slot_id)

                    # Binding the image_name with the pvs_slot_details_id
                    image_pvs_slot_details_id_dict = {data["crop_image_name"]: data["id"]
                                                      for data in pvs_slot_details_data}

                    # Getting the unique_drug_id for predicted_ndc of remote_tech_mapping
                    formatted_ndc_txr_list = list(set(record["predicted_ndc"] for record in remote_tech_mapping))

                    unique_drug_ids_dict = get_unique_drug_id(formatted_ndc_txr_list=formatted_ndc_txr_list)
                    # In case of Foreign Object Detection, ndc --> null
                    logger.info(f"unique_drug_ids_dict: {unique_drug_ids_dict}")
                    unique_drug_ids_dict["null"] = None
                    logger.info(f"unique_drug_ids_dict: {unique_drug_ids_dict}")
                    # Binding image_name with the unique_drug_id and status

                    image_unique_drug_dict = {record["image_name"]: {"label_drug_id": None if not record["predicted_ndc"] else unique_drug_ids_dict[record["predicted_ndc"]],
                                                                     "mapped_status": record["mapped_status"],
                                                                     "linked_qty": float(record["linked_qty"])}
                                              for record in remote_tech_mapping}
                    logger.info(f"image_unique_drug_dict :{image_unique_drug_dict}")
                    # for record in remote_tech_mapping:
                    #     image_name = record["image_name"]
                    #     predicted_fndc_txr = record["predicted_ndc"]
                    #     image_unique_drug_dict[image_name] = unique_drug_ids_dict[predicted_fndc_txr]

                    image_list = image_unique_drug_dict.keys()
                    logger.debug("image_unique_drug_dict: {}".format(image_list))
                    # Preparing the data for populating RemoteTechSlotDetails table
                    remote_tech_slot_details_data = []
                    for image in image_list:
                        remote_tech_slot_details_data.append(
                            {"pvs_slot_details_id": image_pvs_slot_details_id_dict[image],
                             "remote_tech_slot_id": str(remote_tech_slot_id),
                             "label_drug_id": image_unique_drug_dict[image]["label_drug_id"],
                             "mapped_status": image_unique_drug_dict[image]["mapped_status"],
                             "linked_qty": image_unique_drug_dict[image]["linked_qty"]})

                    # Populating the data in the RemoteTechSlotDetails table
                    logger.info('remote_tech_slot_details_data: {}'.format(remote_tech_slot_details_data))
                    add_remote_tech_slot_details_data(remote_tech_slot_details_data)

            return create_response(constants.SUCCESS_RESPONSE)

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)


@log_args_and_response
def get_remote_tech_data(remote_tech_data: dict) -> dict:
    """
    This fetches the data from PVSSlot, PVSSlotDetails, RemoteTechSlot & RemoteTechSlotDetails.
    @param remote_tech_data:
    @return:
    """
    logger.debug("Inside the get_remote_tech_data.")
    pvs_slot_id = remote_tech_data["pvs_slot_id"]
    try:
        # Getting data from PVSSlot & RemoteTechSlot table based on the pvs_slot_id.
        pvs_rts_slot_data = get_pvs_and_rts_slot_data(pvs_slot_id=pvs_slot_id)

        response_dict = {"pack_id": pvs_rts_slot_data["pack_id"],
                         "pack_grid_id": pvs_rts_slot_data["pack_grid_id"],
                         "pvs_slot_id": pvs_rts_slot_data["pvs_slot_id"],
                         "pvs_slot_image_name": None,  #pvs_rts_slot_data["slot_image_name"],
                         "remote_tech_slot_id": pvs_rts_slot_data["remote_tech_slot_id"],
                         "remote_tech_id": pvs_rts_slot_data["remote_tech_id"],
                         "remote_tech_verification_status": pvs_rts_slot_data["verification_status"],
                         "slot_number": pvs_rts_slot_data["slot_number"],
                         "start_time": pvs_rts_slot_data["start_time"],
                         "end_time": pvs_rts_slot_data["end_time"]}

        logger.info("In get_remote_tech_data, response_dict: {}".format(response_dict))
        # Getting data from PVSSlotDetails & RemoteTechSlotDetails table based on the pvs_slot_id.
        pvs_rts_slot_details_data = get_pvs_and_rts_slot_details_data(pvs_slot_id=pvs_slot_id,
                                                                      remote_tech_slot_id =
                                                                      pvs_rts_slot_data["remote_tech_slot_id"])

        pvs_rts_mapping = []
        rts_linked_drug_list = []
        for pvs_rts_slot_detail in pvs_rts_slot_details_data:
            # remove rts slot details from response if it is unlinked by user at prs screen,
            # so that user can link it again.
            if pvs_rts_slot_detail["mapped_status"] == constants.SKIPPED_AND_DELETED:
                pvs_rts_slot_detail["remote_tech_slot_details_id"] = None
                pvs_rts_slot_detail["label_drug_id"] = None
            pvs_rts_slot_details_dict = {"pvs_slot_details_id": pvs_rts_slot_detail["pvs_slot_details_id"],
                                         "crop_image_name": pvs_rts_slot_detail["crop_image_name"],
                                         "pvs_unique_drug": pvs_rts_slot_detail["predicted_label_drug_id"],
                                         "pvs_classification_status": pvs_rts_slot_detail["pvs_classification_status"],
                                         "rts_slot_details_id": pvs_rts_slot_detail["remote_tech_slot_details_id"],
                                         "rts_unique_drug": pvs_rts_slot_detail["label_drug_id"]}
            pvs_rts_mapping.append(pvs_rts_slot_details_dict)
            if pvs_rts_slot_detail["label_drug_id"]:
                rts_linked_drug_list.append(pvs_rts_slot_detail["label_drug_id"])

        response_dict["pvs_rts_mapping"] = pvs_rts_mapping
        logger.info("In get_remote_tech_data: {}".format(rts_linked_drug_list))
        # Fetching unique_drugs for the slot and the corresponding images and ndc based on the pvs_slot_id.
        drug_data = get_drug_data(pvs_slot_id=pvs_slot_id)

        drug_data_list = []
        for data in drug_data:
            # Getting the linked drug count.
            linked_count = rts_linked_drug_list.count(data["unique_drug_id"])
            drug_dict = {"drug_name": data["drug_name"],
                         "ndc": data["ndc"],
                         "formatted_ndc": data["formatted_ndc"],
                         "txr": data["txr"],
                         "drug_image": data["image_name"],
                         "drug_imprint": data["imprint"],
                         "drug_shape": data["shape"],
                         "drug_color": data["color"],
                         "expected_quantity": data["quantity"],
                         "linked_count": linked_count,
                         "unique_drug_id": data["unique_drug_id"]}
            drug_data_list.append(drug_dict)

        response_dict["drug_data_list"] = drug_data_list

        return response_dict
    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(2001)


# @validate(required_fields=["pvs_slot_id", "remote_tech_slot_id", "remote_tech_id", "remote_tech_verification_status",
#                            "start_time", "end_time", "pvs_rts_mapping"])
# def update_remote_tech_data(remote_tech_data):
#     """
#     This updates the data in RemoteTechSlot and RemoteTechSlotDetails table.
#     @param remote_tech_data:
#     @return:
#     """
#     logger.debug("Inside the update_remote_tech_data function.")
#
#     pvs_slot_id = remote_tech_data["pvs_slot_id"]
#     remote_tech_slot_id = remote_tech_data["remote_tech_slot_id"]
#     remote_tech_id = remote_tech_data["remote_tech_id"]
#     verification_status = remote_tech_data["remote_tech_verification_status"]
#     start_time = remote_tech_data["start_time"]
#     end_time = remote_tech_data["end_time"]
#     pvs_rts_mapping = remote_tech_data["pvs_rts_mapping"]
#
#     try:
#         with db.transaction():
#             # Preparing update data for the RemoteTechSlot table.
#             rts_slot_update_dict = {"remote_tech_id": remote_tech_id,
#                                     "verification_status": verification_status,
#                                     "start_time": start_time,
#                                     "end_time": end_time}
#
#             # Updating the data in the RemoteTechSlot table.
#             status = update_rts_slot(update_dict=rts_slot_update_dict, id=remote_tech_slot_id,
#                                      pvs_slot_id=pvs_slot_id)
#             logger.info("update_rts_slot_status: " + status)
#
#             # Preparing the data and updating the RemoteTechSlotDetails data.
#             for record in pvs_rts_mapping:
#                 rts_slot_details_id = record["rts_slot_details_id"]
#                 pvs_slot_details_id = record["pvs_slot_details_id"]
#                 rts_slot_details_update_dict = {"label_drug_id": record["rts_unique_drug"]}
#                 update_status = update_rts_slot_details(update_dict=rts_slot_details_update_dict,
#                                                         id=rts_slot_details_id,
#                                                         pvs_slot_details_id=pvs_slot_details_id,
#                                                         remote_tech_slot_id=remote_tech_slot_id)
#                 logger.info("update_rts_slot_details_status: " + update_status)
#
#             return create_response(constants.SUCCESS_RESPONSE)
#
#     except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
#         logger.error(e)
#         return error(2001)
#     except Exception as e:
#         logger.error(e)
#         return error(2001)

@log_args_and_response
def get_remote_tech_screen_data(remote_tech_data: dict) -> dict:
    """
    This fetches the data for the Remote Technician Screen.
    @param remote_tech_data:
    @return:
    """
    logger.debug("Inside the get_remote_tech_screen_data.")
    company_id = remote_tech_data.get("company_id")
    user_id = remote_tech_data.get("user_id")
    filter_fields = remote_tech_data.get("filter_fields", None)
    sort_fields = remote_tech_data.get("sort_fields", None)
    paginate = remote_tech_data.get("paginate", None)
    advanced_search_fields = remote_tech_data.get('advanced_search_fields', None)
    is_remote_technician = remote_tech_data.get("is_remote_technician", None)
    try:
        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        # getting data for the remote tech screen based on the given filters and sorting.
        response = remote_screen_data(advanced_search_fields=advanced_search_fields,
                                      filter_fields=filter_fields,
                                      sort_fields=sort_fields,
                                      paginate=paginate,
                                      user_id=int(user_id),
                                      is_remote_technician=is_remote_technician)

        return create_response(response)
    except (IntegrityError, InternalError) as e:
        logger.info(e)
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in get_remote_tech_screen_data: " + str(e))


@log_args_and_response
def assign_rts_to_user(args: dict):
    try:
        logger.info("In assign_rts_to_user")

        status = assign_rts_to_given_user(args)

        return create_response(status)

    except (IntegrityError, InternalError) as e:
        logger.info(f"Error in assign_rts_to_user: {e}")
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in assign_rts_to_user: " + str(e))


@log_args_and_response
def get_remote_tech_user_progress(args: dict) -> dict:
    logger.info('start: remote tech user progress')

    user_id = args.get('user_id')
    start_date = args.get('start_date', None)
    end_date = args.get('end_date', None)

    try:
        response = rts_user_progress_data(user_id=user_id,
                                          start_date=start_date,
                                          end_date=end_date)
        return create_response(response)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in get_remote_tech_user_progress: " + str(e))


@log_args_and_response
def assign_remote_tech_slot_data(args: dict):
    try:
        logger.info("In assign_remote_tech_slot_data")

        status = assign_remote_tech_slots(args)

        return create_response(status)

    except (IntegrityError, InternalError) as e:
        logger.info(f"Error in assign_remote_tech_slot_data: {e}")
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in assign_remote_tech_slot_data: " + str(e))


@log_args_and_response
def assign_inactive_users_rts_slots(args=None):
    try:
        logger.info("In assign_inactive_users_rts_slots")
        token = None
        if args:
            token = args.get('token')
        status = assign_rts_slots_of_inactive_users(token)

        return create_response(status)

    except (IntegrityError, InternalError) as e:
        logger.info(f"Error in assign_remote_tech_slot_data: {e}")
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in assign_inactive_users_rts_slots: " + str(e))


@log_args_and_response
def assign_more_crops_for_unique_drug(args: dict):
    try:
        logger.info("In assign_inactive_users_rts_slots")
        unique_drug_id = args['unique_drug_id']
        status = change_drug_queue_status_in_rts_slot_assign_info(unique_drug_id)
        logger.info("In assign_more_crops_for_unique_drug, {}".format(status))
        return create_response(True)

    except (IntegrityError, InternalError) as e:
        logger.info(f"Error in assign_remote_tech_slot_data: {e}")
        return error(2001)
    except Exception as e:
        logger.error(e)
        return error(1000, "Error in assign_inactive_users_rts_slots: " + str(e))