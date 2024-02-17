import os

from dosepack.utilities.utils import log_args_and_response
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import settings
from src.label_printing.utils import get_datamatrix

logger = settings.logger

bottle_dir = os.path.join('canister_bottle')

bottle_datamatrix = os.path.join(bottle_dir, "datamatrix")
bottle_label = os.path.join(bottle_dir, "label")


@log_args_and_response
def generate_drug_bottle_label(bottle_data_list):
    """
    :return:
    @param bottle_data_list:
    """
    if not os.path.exists(bottle_datamatrix):
        os.makedirs(bottle_datamatrix)

    resp = False
    bottle_id_list = []
    file_to_delete_list = []

    for bottle in bottle_data_list:
        matrix_file_name = str(bottle["id"]) + ".jpg"
        matrix_path = os.path.join(bottle_datamatrix, matrix_file_name)
        bottle_id_list.append(str(bottle["id"]))
        bottle["data_matrix_path"] = matrix_path

        file_to_delete_list.append(matrix_path)

        print ("Bottle data: ", bottle)
        resp = get_datamatrix(bottle["ndc"][:10], bottle["lot_number"], bottle["expiry_date"],
                              bottle["serial_number"], matrix_path)

        if not resp:
            raise Exception

    if resp:
        if not os.path.exists(bottle_label):
            os.makedirs(bottle_label)

        bottle_id_label_name = ",".join(bottle_id_list)

        label_path = bottle_id_label_name + ".pdf"
        label_path = os.path.join(bottle_label, label_path)

        font_name = 'tahoma'
        font_size = 6
        pdfmetrics.registerFont(TTFont(font_name, 'tahomabd.ttf'))
        page_size = (0.75 * 72, 0.75 * 72) # Label will be 0.75 inch by 0.75 inch
        can = canvas.Canvas(label_path, pagesize=page_size)

        file_to_delete_list.append(label_path)

        for bottle_data in bottle_data_list:
            can.setFont(font_name, font_size)
            # can.drawImage('drug_images/test1.jpeg', y, y, preserveAspectRatio=True, anchor='c')
            can.drawImage(bottle_data["data_matrix_path"], 5, 10, preserveAspectRatio=False, anchor='c')

            if bottle_data["serial_number"][0] == "#":
                bottle_data["serial_number"] = "#"+ bottle_data["serial_number"][-9:]

            serial_number = 'SR.NO: ' + str(bottle_data["serial_number"])

            can.drawString(15, 7, serial_number[0:7])
            can.drawString(10, 1, serial_number[7:])
            can.showPage()
        can.save()  # save file
        return label_path, file_to_delete_list
