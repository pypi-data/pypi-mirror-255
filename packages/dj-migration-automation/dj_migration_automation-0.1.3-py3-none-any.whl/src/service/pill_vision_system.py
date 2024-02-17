from peewee import InternalError, IntegrityError, DoesNotExist, DataError
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response, get_current_modified_datetime, get_current_date_time
from src import constants
from src.dao.pill_registration_system_dao import db_create_prs_data
from src.dao.pill_vision_system_dao import get_pvs_slot_recent_record, update_pvs_slot, db_create_pvs_slot, \
    get_unique_drug_based_on_fndc_txr, db_create_pvs_slot_details, get_pack_grid, pvs_drug_count_update_or_create, \
    drug_list_from_drug_training_for_given_filters, get_unique_drug_from_fndc_txr, update_drug_training_status, \
    get_associated_device_id

logger = settings.logger

#
# @validate(required_fields=['system_id', 'pack_id', 'device_id'])
# @log_args_and_response
# def create_pvs_pack(pack_data):
#     """
#     Creates entry in `PVSPack` and returns id of `PVSPack`.
#     :param pack_data:
#     :return: json
#
#         >>> create_pvs_pack({"pack_id": 1, "device_id": 3, "system_id":2, "mfd_status":0})
#     """
#     pack_id = pack_data['pack_id']
#     device_id = pack_data['device_id']
#     system_id = pack_data['system_id']
#     mfd_status = pack_data.get('mfd_status', None)
#     if mfd_status is None:
#         mfd_status = 0
#     try:
#         # if pack_id and device_id update PVSPack
#         if pack_id and device_id:
#             valid_pack = PackDetails.db_verify_pack_id_by_system_id(pack_id, system_id)
#             if not valid_pack:
#                 logger.error("pvspack: pack_id {} or system_id {} is not valid".format(pack_id, system_id))
#                 return error(1014)
#             logger.debug("pvspack: found valid pack_id ")
#             created_date, modified_date = get_current_modified_datetime()
#             update_dict = {'modified_date': modified_date,
#                            'deleted': True}
#             pvs_pack_data_dict = {"pack_id": pack_id,
#                                   "device_id": device_id,
#                                   "mfd_status": mfd_status,
#                                   "created_date": created_date,
#                                   "modified_date": modified_date}
#
#             logger.debug(
#                 "updating existing pvs_pack as deleted = 1 and create new record for pack_id {} and device_id {}"
#                     .format(pack_id, device_id))
#             with db.transaction():
#                 # different robot can process same pack so device_id needed
#                 pvs_pack_update_status = update_pvs_pack(update_dict=update_dict, pack_id=pack_id, device_id=device_id)
#                 logger.debug("updated pvs_pack deleted=1 for pack_id {} and device_id {}".format(pack_id, device_id))
#                 pvs_pack_id = create_pvs_pack_record(pvs_pack_data_dict=pvs_pack_data_dict).id
#
#             logger.debug("pvspack: record inserted in pvs_pack with id: {}, record: {}".format(pvs_pack_id, pvs_pack_data_dict))
#         return create_response(pvs_pack_id)
#     except (IntegrityError, InternalError, DataError) as e:
#         logger.error(e, exc_info=True)
#         return error(2001)


@log_args_and_response
def create_slot_data(slot_data):
    """
    Creates entry into `PVSSLot` and `PVSSlotDetails` and update PvsDrugCount
    - Data format for slot data:
                        [{
            # "pvs_pack_id": 1, --> not needed anymore
            "device_id": 11,
            "slot_header_id": 11,
            "slot_image_name": "abc.png",
            "expected_count": 2,
            "pvs_identified_count": 2,
            "robot_drop_count": 2,
            "mfd_status": false,
            "us_status": 40,
            "slot_details": [{
                    "crop_image": "123 _1.png",
                    "predicted_ndc": "763850104_4590",
                    "classification_status": 87,
                    "dimension_status": false,
                    "pill_centre_x": 12.3,
                    "pill_centre_y": 11.2,
                    "radius": 0.5
                },
                {
                    "crop_image": "123 _2.png",
                    "predicted_ndc": "710930132_13318",
                    "classification_status": 87,
                    "dimension_status": false,
                    "pill_centre_x": 12.3,
                    "pill_centre_y": 11.2,
                    "radius": 0.5
                }
            ],
            "predicted_drugs": [{
                    "predicted_qty": 1,
                    "slot_row": 1,
                    "slot_column": 1,
                    "predicted_ndc": "763850104_4590",
                    "expected_qty": 1
                },
                {
                    "predicted_qty": 1,
                    "slot_row": 1,
                    "slot_column": 1,
                    "predicted_ndc": "710930132_13318",
                    "expected_qty": 1
                }
            ]
        }]
    :param slot_data:
    :return: json
    """
    try:
        logger.debug("In create_pvs_slot")
        unique_drug_data = dict()
        pvs_slot_ids = list()
        with db.transaction():
            logger.debug("In create_slot_data, create_pvs_slot: Transaction started for pvsslot")
            error_list = [constants.US_STATION_SUCCESS, constants.US_STATION_NOT_SURE]
            for slot_data_record in slot_data:
                # pvs_pack_id = slot_data_record['pvs_pack_id']
                # pvs_pack_data = get_pvs_pack_data(id=pvs_pack_id)
                # if pvs_pack_data:
                #     pack_id = pvs_pack_data[0]["pack_id"]
                # else:
                #     return error(1020, "Invalid pvs_pack_id: {}.".format(pvs_pack_id))
                slot_header_id = slot_data_record['slot_header_id']
                device_id = slot_data_record['device_id']
                drop_number = slot_data_record['drop_number']
                quadrant = slot_data_record['quadrant']

                # try:
                #     validate_pvs_pack_id_and_slot_header_id(pvs_pack_id=pvs_pack_id, slot_header_id=slot_header_id)
                # except DoesNotExist as e:
                #     logger.error(e)
                #     logger.debug(
                #         "pvs_pack_id: {} and slot_header_id: {} is invalid".format(pvs_pack_id, slot_header_id))
                #     return error(1020, "Invalid pvs_pack_id {} or slot_header_id {}.".format(pvs_pack_id,slot_header_id))
                if slot_header_id:

                    try:
                        logger.debug("In create_slot_data, fetching existing data for slot_header_id: {}".format(slot_header_id))
                        pvs_slot_data = get_pvs_slot_recent_record(slot_header_id=slot_header_id, drop_number=drop_number,
                                                                   device_id=device_id, quadrant=quadrant)
                        if pvs_slot_data["us_status"] in error_list:
                            return error(1027, "Last slot user_station status was Success or Not Confident.")
                        us_status = pvs_slot_data["us_status"]
                        if pvs_slot_data["us_status"] == constants.US_STATION_MISSING_PILLS:
                            us_status = constants.US_STATION_MISSING_PILLS_AND_DELETED
                        if pvs_slot_data["us_status"] == constants.US_STATION_REJECTED:
                            us_status = constants.US_STATION_DELETED

                        pvs_update_dict = {"us_status": us_status, "modified_date": get_current_date_time()}
                        update_status = update_pvs_slot(update_dict=pvs_update_dict, id=pvs_slot_data["id"])
                        logger.info("In create_slot_data: update_pvs_slot status: {}".format(update_status))

                    except DoesNotExist:
                        logger.debug("In create_slot_data, No previous data exists for given slot_header_id: {}".format(slot_header_id))

                created_date, modified_date = get_current_modified_datetime()

                associated_device_id = get_associated_device_id(device_id=device_id)

                slot_data_dict = {
                    'device_id': slot_data_record['device_id'],
                    'slot_header_id': slot_data_record['slot_header_id'],
                    'drop_number': slot_data_record['drop_number'],
                    'slot_image_name': slot_data_record['slot_image_name'],
                    'us_status': slot_data_record['us_status'],
                    'expected_count': slot_data_record.get('expected_count', 0),
                    'pvs_identified_count': slot_data_record['pvs_identified_count'],
                    'robot_drop_count': slot_data_record.get('robot_drop_count', 0),
                    'mfd_status': slot_data_record['mfd_status'],
                    'quadrant': slot_data_record['quadrant'],
                    'created_date': created_date,
                    'modified_date': modified_date,
                    'associated_device_id': associated_device_id,
                    'pack_id': slot_data_record.get('pack_id', None)
                }

                pvs_slot_id = db_create_pvs_slot(create_dict=slot_data_dict)
                logger.debug("create_pvs_slot: Data {} added in pvsslot with id: {}".format(slot_data_dict, pvs_slot_id))
                pvs_slot_ids.append(pvs_slot_id)
                slot_details = slot_data_record['slot_details']

                fndctxr = [slot_detail['predicted_ndc'] for item in slot_data for slot_detail in item['slot_details']
                           if 'predicted_ndc' in slot_detail]

                if fndctxr:
                    unique_drug_data_based_on_fndc_txr = get_unique_drug_based_on_fndc_txr(fndctxr)
                    for record in unique_drug_data_based_on_fndc_txr:
                        unique_drug_data[(record['formatted_ndc'], record['txr'])] = record['id']

                for slot_detail in slot_details:
                    predicted_label_drug = None
                    fndc_txr = slot_detail.get('predicted_ndc', None)
                    if fndc_txr:
                        fndc, txr = fndc_txr.split('_')
                        if not txr:
                            txr = None

                        predicted_label_drug = unique_drug_data[(fndc, txr)]
                    created_date, modified_date = get_current_modified_datetime()
                    slot_detail_data = {
                        'pvs_slot_id': pvs_slot_id,
                        'crop_image_name': slot_detail['crop_image'],
                        'predicted_label_drug_id': predicted_label_drug,
                        'pvs_classification_status': slot_detail.get('classification_status', None),
                        'pill_centre_x': slot_detail.get('pill_centre_x', None),
                        'pill_centre_y': slot_detail.get('pill_centre_y', None),
                        'radius': slot_detail.get('radius', None),
                        'created_date': created_date,
                        'modified_date': modified_date
                    }
                    pvs_slot_detail_id = db_create_pvs_slot_details(create_dict=slot_detail_data)

                    logger.debug("create_pvs_slot: Data {} added in pvs slot details with id: {}".format(slot_detail_data,
                                                                                                    pvs_slot_detail_id))

                # entry for pvs predicted drug count in any slot
                predicted_fndc_txr = [fndc_txr_data["predicted_ndc"] for fndc_txr_data in
                                      slot_data_record['predicted_drugs']
                                      if "_" in fndc_txr_data["predicted_ndc"]]
                logger.info("In create_slot_data, predicted_fndc_txr: " + str(predicted_fndc_txr))
                if predicted_fndc_txr:
                    unique_drug_data_based_on_predicted_fndc_txr = get_unique_drug_based_on_fndc_txr(predicted_fndc_txr)
                    for record in unique_drug_data_based_on_predicted_fndc_txr:
                        unique_drug_data[(record['formatted_ndc'], record['txr'])] = record['id']

                for predicted_drug in slot_data_record['predicted_drugs']:
                    # pack_grid_id = get_pack_grid(slot_row=predicted_drug['slot_row'],
                    #                              slot_column=predicted_drug['slot_column'])[0]['id']
                    # logger.info("In create_slot_data: pack_grid_id: {}".format(pack_grid_id))
                    if '_' not in predicted_drug['predicted_ndc']:
                        continue

                    fndc, txr = predicted_drug["predicted_ndc"].split("_")

                    unique_drug_id = unique_drug_data[(fndc, txr)]

                    create_dict = {
                        'pvs_slot_id': pvs_slot_id,
                        'unique_drug_id': unique_drug_id,
                    }
                    update_dict = {
                        'predicted_qty': predicted_drug['predicted_qty'],
                        'expected_qty': predicted_drug['expected_qty']
                    }
                    prs_drug_dict = {
                        'unique_drug_id': unique_drug_id,
                        'predicted_qty': predicted_drug['predicted_qty'],
                        'expected_qty': predicted_drug['expected_qty']
                    }
                    updated_pvs_drug_count = pvs_drug_count_update_or_create(create_dict=create_dict, update_dict=update_dict)
                    logger.debug("create_pvs_slot: Updated pvsdrugcount as {}".format(updated_pvs_drug_count))

                    prs_data_creation = db_create_prs_data(drug_dict=prs_drug_dict)
                    logger.debug("created_or_updated prs_drug_details: {}".format(prs_data_creation))

        response = {"pvs_slot_ids": pvs_slot_ids}
        return create_response(response)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
    except DoesNotExist as e:
        logger.error(e, exc_info=True)
        return error(1020)
    except Exception as e:
        logger.error(e, exc_info=True)
        return error(2001)


@log_args_and_response
def get_drug_training(filters):
    """
    Returns drug list from `DrugTraining` using given filters.
    :param filters: dict
    :return: json
    """
    try:

        drug_list = drug_list_from_drug_training_for_given_filters(filters)
        return create_response(drug_list)

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_drug_training {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in get_drug_training {}".format(e))
        return error(1000, "Error in get_drug_training: " + str(e))


@log_args_and_response
def update_drug_training(training_data):
    """
    updates status for drug
    format:  {"0":[{"formatted_ndc":681800981, "txr":391}] ,
              "1":[{"formatted_ndc":710450010, "txr":78569},
                   {"formatted_ndc":678770223, "txr":21414}]}
    :param training_data: dict
    :return:
    """

    try:
        for status, drug_details in training_data.items():
            fndc_txr_list = list(
                '{}_{}'.format(drug_detail['formatted_ndc'], drug_detail['txr'] or '') for drug_detail in drug_details)
            unique_drug_data = get_unique_drug_from_fndc_txr(fndc_txr_list)
            if unique_drug_data:
                unique_drug_id_list = list(unique_drug_data.values())
                status = update_drug_training_status(status, unique_drug_id_list)
                logger.info("In update_drug_training: update_drug_training_status: {}".format(status))

        return create_response(True)

    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)
