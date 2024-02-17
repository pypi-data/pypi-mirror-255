import settings
import src.constants
from dosepack.utilities.utils import log_args_and_response
from src.dao.mfd_dao import map_pack_location_dao
from src.dao.print_label_dao import get_pvs_data_dao

logger = settings.logger


@log_args_and_response
def get_pvs_data(pack_id):
    logger.debug("In get_pvs_data")
    DISPLAY_ERROR_PRIORITY = {src.constants.US_STATION_REJECTED: 40, src.constants.US_STATION_SUCCESS: 10,
                              src.constants.US_STATION_NOT_SURE: 30, src.constants.US_STATION_MISSING_PILLS: 20, }

    pvs_data = dict()
    unique_crops = set()
    data = get_pvs_data_dao(pack_id)
    for record in data:
        slot_row, slot_column = record["slot_row"], record["slot_column"]
        location = map_pack_location_dao(slot_row=slot_row, slot_column=slot_column)
        pvs_data.setdefault(location, {})
        pvs_data[location].setdefault("data_list", {})
        # uncomment below code
        # if record['device_id'] not in pvs_data[location]["data_list"]:
        #     pvs_data[location]["data_list"][record['device_id']] = {}
        pvs_data[location].setdefault("pvs_slot_error", src.constants.US_STATION_SUCCESS)
        if (DISPLAY_ERROR_PRIORITY[record["us_status"]] >
                DISPLAY_ERROR_PRIORITY[pvs_data[location]["pvs_slot_error"]]):
            pvs_data[location]["pvs_slot_error"] = record["us_status"]
            # change pvs_slot_error if us_status has higher priority'
        # comment uncomment below code
        # pvs_data[location]["data_list"][record['device_id']].setdefault(record['drop_number'], {
        #     "crop_images": list(),
        #     "drop_number": record["drop_number"],
        #     "slot_image": record["slot_image_name"],
        #     "predicted_count": 0,
        #     "device_id": record["device_id"]
        # })
        pvs_data[location]["data_list"].setdefault((record['drop_number'], record['quadrant']), {
            "crop_images": list(),
            "drop_number": record["drop_number"],
            "quadrant": record["quadrant"],
            "slot_image": record["slot_image_name"],
            "predicted_count": 0,
            "device_id": record["device_id"]
        })
        # pvs_data[location]["data_list"].setdefault(pack_id, {
        #     "crop_images": list(),
        #     "drop_number": record["drop_number"],
        #     "slot_image": record["slot_image_name"],
        #     "predicted_count": 0,
        #     "device_id": record["device_id"]
        # })
        # batch_data = pvs_data[location]["data_list"][pack_id]
        # uncomment below code
        batch_data = pvs_data[location]["data_list"][(record['drop_number'], record['quadrant'])]
        if record["pvs_sd_id"]:
            if record["pvs_sd_id"] not in unique_crops:
                unique_crops.add(record["pvs_sd_id"])
                batch_data["crop_images"].append({
                    # unable to pass remote technician's data
                    # "crop_image": record["crop_image"],
                    # "drug_name": record["drug_name"],
                    # "strength": record["strength"],
                    # "strength_value": record["strength_value"],
                    # "ndc": record["ndc"],
                    # "color": record["color"],
                    # "shape": record["shape"],
                    # "imprint": record["imprint"],
                    # "drug_image": record["image_name"],
                    # 'crop_id': record['crop_id'],
                    # 'ref_drug_id': record['pvs_drug_label'],  #
                    "predicted_by": record["predicted_by"],
                    'crop_image': record['crop_image_name'],
                    'predicted_drug_name': record['predicted_drug_name'],
                    'predicted_strength': record['predicted_strength'],
                    'predicted_strength_value': record['predicted_strength_value'],
                    'predicted_ndc': record['predicted_ndc'],
                    'predicted_color': record['predicted_color'],
                    'predicted_shape': record['predicted_shape'],
                    'predicted_imprint': record['predicted_imprint'],
                    'predicted_image_name': record['predicted_image_name'],  # drug image
                    'pvs_classification_status': record['pvs_classification_status'],
                    'pvs_drug_label': record['pvs_drug_label'],
                    'radius': record['radius'],
                    'pill_centre_x': record['pill_centre_x'],
                    'pill_centre_y': record['pill_centre_y']
                })
                batch_data["predicted_count"] = len(batch_data["crop_images"])
                batch_data["device_id"] = record["device_id"]
    for k, v in pvs_data.items():  # flatten objects in data_list
        data_list = list(v["data_list"].values())
        v["data_list"] = sorted(data_list, key=lambda x: x['drop_number'])
        # uncomment below code for multiple images
        # data_list = list()
        # device_ids = list(v["data_list"].keys())
        # for device in sorted(device_ids):
        #     data_list.append(sorted(list(v['data_list'][device].values()), key=lambda x: x["drop_number"]))
        # v["data_list"]= data_list
    logger.debug(pvs_data)
    return pvs_data
