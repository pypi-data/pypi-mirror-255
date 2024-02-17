import json
import os
import threading
import time

import settings
from dosepack.error_handling.error_handler import create_response
# from label_generator import PackLabelGeneratorABC
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from src.cloud_storage import download_blob
from src.dao.drug_dao import get_label_drugs
from src.dao.pack_dao import db_get_label_info, get_pharmacy_data_for_system_id, get_patient_details_for_patient_id
from src.dao.misc_dao import get_system_setting_by_system_id

logger = settings.logger

BUCKET_DRUG_IMAGE_PATH = 'drug_images'
DRUG_IMAGE_MODIFICATION_ALLOWED = 168  # in hours


class PackLabelGenerator():

    def __init__(self, pack_id, patient_id, system_id, pack_display_id, label_dir, drug_images_dir, patient_image_dir):
        super().__init__(pack_id, patient_id, system_id, pack_display_id, label_dir, drug_images_dir, patient_image_dir)

    @staticmethod
    def download_drug_image(image_name, image_path):
        """
        Downloads drug image (suppresses any exception)

        :param image_name:
        :param image_path:
        :return:
        """
        try:
            with open(image_path, 'wb')as drug_image:
                logger.info('Downloading Drug Image: ' + str(image_name))
                download_blob(image_name, drug_image, BUCKET_DRUG_IMAGE_PATH, drug_image=True)
                logger.info('Downloaded Drug Image: ' + str(image_name))
        except Exception as e:
            logger.warning(str(image_name) + ': Downloading Failed ' + str(e))
            try:
                os.remove(image_path)  # could not download file, so remove
            except Exception:
                pass
            logger.error(e)

    def get_drug_images(self, drug_images):
        """

        :param drug_images:
        :param drug_image_dir:
        :return:
        """
        try:
            threads_list = []
            # try to download drug images required if any exception skip
            for drug_image in drug_images:
                drug_image_path = os.path.join(self.drug_images_dir, drug_image)
                if not os.path.exists(drug_image_path):
                    t = threading.Thread(target=self.download_drug_image, args=[drug_image, drug_image_path])
                    threads_list.append(t)
                    t.start()
                else:  # download if only drug image is older than some constant time
                    modification_in_hours = int((os.path.getmtime(drug_image_path) - time.time()) / 3600)
                    if modification_in_hours > DRUG_IMAGE_MODIFICATION_ALLOWED:
                        t = threading.Thread(target=self.download_drug_image, args=[drug_image, drug_image_path])
                        threads_list.append(t)
                        t.start()
            [th.join() for th in threads_list]  # wait for all images to download
        except Exception as e:
            logger.error(e)

    def get_system_setting(self, system_id):
        return get_system_setting_by_system_id(system_id=system_id)

    def get_drug_details(self):
        try:
            pharmacy_data = next(get_pharmacy_data_for_system_id(system_id=self.system_id))
            patient_details = next(get_patient_details_for_patient_id(patient_id=self.patient_id))
            pack_info = next(db_get_label_info(self.pack_id))
        except StopIteration as e:
            logger.error(e, exc_info=True)
        pharmacy_rx_info = get_label_drugs(self.pack_id)

        if not (pharmacy_rx_info or pharmacy_data or pack_info or patient_details):
            return

        data = {"pharmacy_data": pharmacy_data, "patient_details": patient_details, "pack_info": pack_info,
                "pharmacy_rx_info": pharmacy_rx_info}
        # handling string conversion of date using json
        data = json.loads(create_response(data))
        return data["data"]

    # def get_slot_details(self, canister_based_manual=False):
    #     """
    #         @function: get_slot_details
    #         @createdBy: Manish Agarwal
    #         @createdDate: 09/23/2015
    #         @lastModifiedBy: Manish Agarwal
    #         @lastModifiedDate: 09/23/2015
    #         @type: function
    #         @param: int
    #         @purpose - Get the slot details for the given packid.
    #         @input -
    #             type - (int) 12
    #         @output -
    #              {
    #                     "1": [
    #                             {
    #                                 "admin_date": 1032015,
    #                                 "admin_time": 800,
    #                                 "drug_name": "ACYCLOVIR OINTMENT",
    #                                 "ndc": "00000000001",
    #                                 "quantity": "1",
    #                                 "slot_column": 0,
    #                                 "slot_row": 0
    #                             },
    #                             {
    #                                 "admin_date": 1032015,
    #                                 "admin_time": 800,
    #                                 "drug_name": "ACYCLOVIR OINTMENT",
    #                                 "ndc": "00000000001",
    #                                 "quantity": "1",
    #                                 "slot_column": 0,
    #                                 "slot_row": 0
    #                             }
    #                         ],
    #                     "2": [
    #                             {
    #                                 "admin_date": 1042015,
    #                                 "admin_time": 800,
    #                                 "drug_name": "ACYCLOVIR OINTMENT",
    #                                 "ndc": "00000000001",
    #                                 "quantity": "1",
    #                                 "slot_column": 0,
    #                                 "slot_row": 1
    #                             }
    #                         ],
    #     """
    #     data = drug_data = {}
    #     dict_slot_info = defaultdict(dict)
    #
    #     slot_data = PackDetails.db_slot_details_for_label_printing(self.pack_id, self.system_id,
    #                                                                canister_based_manual=canister_based_manual)
    #
    #     for item in slot_data:
    #         slot_row, slot_column = item["slot_row"], item["slot_column"]
    #         item["quantity"] = float(item["quantity"])
    #         location = self.map_pack_location(slot_row, slot_column)
    #         dict_slot_info[location]['hoa_date'] = item["hoa_date"]
    #         dict_slot_info[location]['hoa_time'] = item["hoa_time"]
    #         dict_slot_info[location]['slot_row'] = item["slot_row"]
    #         dict_slot_info[location]['slot_column'] = item["slot_column"]
    #         dict_slot_info[location].setdefault("drug_details", []).append(create_slot(item))
    #
    #     # handling string conversion of date using json
    #     dict_slot_info = json.loads(create_response(dict_slot_info))
    #
    #     return dict_slot_info["data"]
    #

def generate_packid_sticker(file_name, packid):
    """
    Generates pack sticker pdf

    :param file_name:
    :param packid_list:
    """

    font_name = 'tahoma'
    pdfmetrics.registerFont(TTFont(font_name, 'tahomabd.ttf'))
    page_size = (2.25 * 72, 1.25 * 72)  # 2.25 inch * 1.25 inch (w*h)
    can = canvas.Canvas(file_name, pagesize=page_size)

    pack_id = 'Pack ID: ' + str(packid)
    can.drawString(30, 40, pack_id)
    can.showPage()

    can.save()  # save file