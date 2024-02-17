# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

import base64
import datetime
import json
import logging
import os
import threading
import time
import urllib
from datetime import timedelta

from com.pharmacy_software import is_response_valid
from dosepack.error_handling.error_handler import create_response
from dosepack.utilities.utils import fn_shorten_drugname, retry, fn_shorten_drugname_v2
from src.label_printing import label_config, pack_label
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import *
from reportlab.graphics.barcode import code93
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
# import winreg
# import subprocess
from reportlab.lib import colors
from reportlab.lib import units
from reportlab.lib.colors import lightblue, black, green, blue, orange, maroon
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Image, Paragraph, Spacer
from reportlab.platypus.flowables import Flowable
from src.cloud_storage import create_blob, download_blob, label_blob_dir
from src.dao.drug_dao import get_label_drugs
from src.dao.pack_dao import db_get_label_info, get_pharmacy_data_for_system_id, get_patient_details_for_patient_id
from src.dao.misc_dao import get_system_setting_by_system_id

color_array = [blue, orange, green, lightblue, blue, orange, green, lightblue]

pdfmetrics.registerFont(TTFont('tahoma', 'tahomabd.ttf'))
pdfmetrics.registerFont(TTFont('tahoma_normal', 'tahoma.ttf'))
pdfmetrics.registerFont(TTFont('arial', 'arial.ttf'))

# get the logger for the label_printing
logger = logging.getLogger('root')
styleSheet = getSampleStyleSheet()
styleSheet["Normal"].leading = 9


class RotededText(Flowable):
    """
        @function: RotededText
        @createdBy: Manish Agarwal
        @createdDate: 09/22/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/22/2015
        @type: function
        @param: object Flowable
        @purpose - Takes a paragraph and rotaties it by 90 degree
        @input -
            Object(Paragraph)
        @output -

    """

    def __init__(self, text):
        Flowable.__init__(self)
        self.text = text

    def draw(self):
        canvas = self.canv
        canvas.rotate(90)
        fs = canvas._fontsize
        canvas.translate(1, -fs/1.2) # canvas._leading?
        canvas.drawString(0, 0, self.text)

    def wrap(self, aW, aH):
        canv = self.canv
        fn, fs = canv._fontname, canv._fontsize
        return canv._leading, 1 + canv.stringWidth(self.text, fn, fs)


class RotatedParagraph(Flowable):
    """
        @function: RotatedParagraph
        @createdBy: Manish Agarwal
        @createdDate: 09/22/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/22/2015
        @type: function
        @param: object Flowable
        @purpose - Takes a paragraph and rotates it by 90 degree
        @input -
            object(Paragraph)
        @output -

    """

    def __init__(self, text ):
        Flowable.__init__(self)
        self.text=text

    def draw(self):
        canvas = self.canv
        canvas.rotate(90)
        fs = canvas._fontsize
        canvas.translate(1, -self.height)
        self.text.canv = canvas
        try:
            self.text.draw()
        finally:
            del self.text.canv

    def wrap(self, aW, aH):
        w, h = self.text.wrap(aH,aW)
        self.width,self.height = h, w
        return h, w


class RotatedPara(Paragraph):
    def draw(self):
        self.canv.saveState()
        self.canv.translate(0,0)
        self.canv.rotate(90)
        Paragraph.draw(self)
        self.canv.restoreState()


class BoxyLine(Flowable):
    """
        @function: BoxyLine
        @createdBy: Manish Agarwal
        @createdDate: 09/22/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/22/2015
        @type: function
        @param: Object(Flowable)
        @purpose - Draws a rectangle around the text
        @input -
            text = Hello World
        @output -
            ---------------
            - Hello World -
            ---------------
    """
    def __init__(self, x=14, y=0, width=528, height=25, text=""):
        Flowable.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.styles = getSampleStyleSheet()

    def coord(self, x, y, unit=1):
        """
        http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab
        Helper class to help position flowables in Canvas objects
        """
        x, y = x * unit, self.height - y * unit
        return x, y

    def draw(self):
        """
        Draw the shape, text, etc
        """
        self.canv.rect(self.x, self.y, self.width, self.height)
        self.canv.line(self.x, 0, 500, 0)
        val = '<para align=center><font name = tahoma size=8 color = blue><b>%s</b></font><br />' \
              '<font name = tahoma_normal size=10 color=blue>' \
              'Federal or state law prohibits transfer of this prescription to any person other than ' \
              'patient for whom it is prescribed.</font></para>' % "THE PHARMACIST IS AVAILABLE FOR COUNSELING."
        p = Paragraph(val, style=self.styles["Normal"])
        p.wrapOn(self.canv, self.width, self.height)
        p.drawOn(self.canv, *self.coord(self.x-9, 9, mm))


class PatientInfo(Flowable):
    """
        @function: BoxyLine
        @createdBy: Manish Agarwal
        @createdDate: 09/22/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/22/2015
        @type: function
        @param: Object(Flowable)
        @purpose - Draws a rectangle around the text
        @input -
            text = Hello World
        @output -
            ---------------
            - Hello World -
            ---------------
    """
    def __init__(self, patient_info, time_details, packid, system_id, pack_info):
        Flowable.__init__(self)
        self.patient_info = patient_info
        self.time_details = time_details
        self.packid = packid
        self.pack_info = pack_info
        self.system_id = system_id
        # todo add system_id as method variable

    def draw(self):
        """
        Draw the shape, text, etc
        """
        patient_info = self.patient_info
        time_details = self.time_details
        packid = self.packid
        system_id = self.system_id
        try:
            birth_date = patient_info["dob"]
            birth_date = datetime.datetime.strptime(birth_date, '%Y-%m-%d')
            birth_date = birth_date.strftime('%m/%d/%y')
        except Exception:
            birth_date = "-"

        start_date = self.pack_info["filled_start_date"]
        end_date = self.pack_info["filled_end_date"]

        start_filling_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        start_filling_date = start_filling_date.strftime('%m/%d/%y')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_date = end_date.strftime('%m/%d/%y')
        admin_period = str(start_filling_date) + " - " + str(end_date)

        facility_name = patient_info["facility_name"]
        patient_name = patient_info["patient_name"]

        if len(patient_name) > 20:
            patient_size = 12
        elif len(patient_name) > 15:
            patient_size = 16
        else:
            patient_size = 22

        patient_no = patient_info["patient_no"]

        if not patient_no:
            patient_no = 'AST80'

        patient_picture = patient_info["patient_picture"]

        pic_status = False

        if not patient_picture:
            qr_text = "GETPHOTO" + ":" + str(label_config.MEDITAB_ID) + ":" + str(packid)
            I = generate_qr_code_patient(qr_text)

        else:
            # todo code for patient image download
            patient_image = os.path.join('patient_images', str(system_id), patient_picture)
            if os.path.isfile(patient_image):
                pic_status = True
            else:
                # download the patient image
                resp = get_patient_image(system_id, patient_picture, packid)
                if not resp:
                    qr_text = "GETPHOTO" + ":" + str(label_config.MEDITAB_ID) + ":" + str(packid)
                    I = generate_qr_code_patient(qr_text)
                else:
                    pic_status = True

        self.canv.setFont("arial", 22)
        self.canv.drawString(17, -6, patient_no)
        self.canv.setFont("arial", 8)
        self.canv.drawString(18, -16, "Admin Period: " + str(admin_period))
        self.canv.rect(144, -16, .6*inch, .4*inch, fill=0)

        self.canv.setFont("arial", patient_size)
        self.canv.drawString(191, -6, patient_name)
        self.canv.setFont("arial", 8)
        self.canv.drawString(191, -16, "DOB: " + str(birth_date) + " " + patient_name + " (" + patient_no + ") " + facility_name[0:30])
        self.canv.setFont("arial", 22)
        self.canv.drawString(410, -6, str(packid))

        self.canv.setFont("arial", 8)
        self.canv.setFillColor(blue)
        self.canv.saveState()
        self.canv.rotate(90)
        base_y = -502
        for index, item in enumerate(time_details):
            self.canv.setFillColor(color_array[index])
            self.canv.drawString(-20, base_y, str(item))
            base_y -= 8
        self.canv.restoreState()
        self.canv.setFillColor(black)
        try:
            if pic_status:
                self.canv.drawImage(patient_image, 148, -16, .5 * inch, .4 * inch)
            else:
                renderPDF.draw(I, self.canv, 151, -16)
        except Exception as ex:
            logger.error(ex, exc_info=True)


class DrawImage(Flowable):
    """
        @function: BoxyLine
        @createdBy: Manish Agarwal
        @createdDate: 09/22/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/22/2015
        @type: function
        @param: Object(Flowable)
        @purpose - Draws a rectangle around the text
        @input -
            text = Hello World
        @output -
            ---------------
            - Hello World -
            ---------------
    """
    def __init__(self):
        Flowable.__init__(self)

    def draw(self):
        """
        Draw the shape, text, etc
        """

        image2 = os.path.join('drug_images', 'image2.png' )
        image1 = os.path.join('drug_images', 'imag1.png' )

        self.canv.drawInlineImage(image2, -13, -481, .30 * inch, .30 * inch)
        self.canv.drawInlineImage(image1, -13, -649, .30 * inch, .30 * inch)

        self.canv.drawInlineImage(image2, 537, -481, .30 * inch, .30 * inch)
        self.canv.drawInlineImage(image1, 537, -649, .30 * inch, .30 * inch)

        self.canv.drawInlineImage(image2, -13, 102, .30 * inch, .30 * inch)
        self.canv.drawInlineImage(image1, -13, 272, .30 * inch, .30 * inch)

        self.canv.drawInlineImage(image2, 537, 102, .30 * inch, .30 * inch)
        self.canv.drawInlineImage(image1, 537, 272, .30 * inch, .30 * inch)

        self.canv.setFont("arial", 8)
        self.canv.saveState()
        self.canv.rotate(90)

        self.canv.drawString(150, -6, "Keep away from children.")
        self.canv.drawString(120, 2, "Green packaging designed to reduce waste")

        self.canv.drawString(150, -542, "Keep away from children.")
        self.canv.drawString(120, -550, "Green packaging designed to reduce waste")

        self.canv.drawString(-145, 3, "Scan QR code before taking dosage.")
        self.canv.drawString(-295, 3, "Keep away from children.")
        self.canv.drawString(-445, 3, "Store in cool dry place.")
        self.canv.drawString(-632, 3, "Green packaging designed to reduce waste")

        self.canv.drawString(-145, -552, "Scan QR code before taking dosage.")
        self.canv.drawString(-295, -552, "Keep away from children.")
        self.canv.drawString(-445, -552, "Store in cool dry place.")
        self.canv.drawString(-632, -552, "Green packaging designed to reduce waste")

        self.canv.restoreState()


def get_barcode(value, width, barWidth=0.2 * units.inch, fontSize=30, humanReadable=False):

    barcode = createBarcodeDrawing('Code128', value=value, barWidth=barWidth, fontSize=fontSize, humanReadable=humanReadable)

    drawing_width = width
    barcode_scale = drawing_width / barcode.width
    drawing_height = barcode.height * barcode_scale

    drawing = Drawing(drawing_width, drawing_height)
    drawing.scale(barcode_scale, barcode_scale)
    drawing.add(barcode, name='barcode')

    return drawing


def get_drug_details(patient_id, pack_id, system_id):
    try:
        pharmacy_data = next(get_pharmacy_data_for_system_id(system_id=system_id))
        patient_details = next(get_patient_details_for_patient_id(patient_id=patient_id))
        pack_info = next(db_get_label_info(pack_id))
    except StopIteration as e:
        logger.error(e, exc_info=True)
    pharmacy_rx_info = get_label_drugs(pack_id)

    if not (pharmacy_rx_info or pharmacy_data or pack_info or patient_details):
        return

    data = {"pharmacy_data": pharmacy_data, "patient_details": patient_details, "pack_info": pack_info,
            "pharmacy_rx_info": pharmacy_rx_info}
    # handling string conversion of date using json
    data = json.loads(create_response(data))
    return data["data"]


def parse_drug_details(drug_data):
    patient_data = drug_data["patient_details"]
    pharmacy_rx_data = drug_data["pharmacy_rx_info"]
    pack_info = drug_data["pack_info"]
    pharmacy_data = drug_data["pharmacy_data"]

    drug_label_data = []
    drug_images = []
    for item in pharmacy_rx_data:
        drug_label_data.append({item["ndc"]: item})
        if "image_name" in item and item["image_name"]:
            drug_images.append(item["image_name"])

    return patient_data, drug_label_data, pack_info, pharmacy_data, drug_images


# def get_slot_details(pack_id, system_id, canister_based_manual=False):
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
#     slot_data = PackDetails.db_slot_details_for_label_printing(pack_id, system_id,
#                                                                canister_based_manual=canister_based_manual)
#
#     for item in slot_data:
#         slot_row, slot_column = item["slot_row"], item["slot_column"]
#         item["quantity"] = float(item["quantity"])
#         location = map_pack_location(slot_row, slot_column)
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

def construct_label_slots(slot_details, patient_name, batchid, packid):
    """
        @function: construct_label_slots
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: String
        @purpose - Construct label slots for printing from slot details
        @input -
            type: (String)
             {
                    "1": [
                            {
                                "admin_date": 1032015,
                                "admin_time": 800,
                                "drug_name": "ACYCLOVIR OINTMENT",
                                "ndc": "00000000001",
                                "quantity": "1",
                                "slot_column": 0,
                                "slot_row": 0
                            },
                            {
                                "admin_date": 1032015,
                                "admin_time": 800,
                                "drug_name": "ACYCLOVIR OINTMENT",
                                "ndc": "00000000001",
                                "quantity": "1",
                                "slot_column": 0,
                                "slot_row": 0
                            }
                        ],
                    "2": [
                            {
                                "admin_date": 1042015,
                                "admin_time": 800,
                                "drug_name": "ACYCLOVIR OINTMENT",
                                "ndc": "00000000001",
                                "quantity": "1",
                                "slot_column": 0,
                                "slot_row": 1
                            }
                        ],
        @output -
            []
    """
    if not slot_details:
        return None

    slots_for_printing = [[None for i in range(0, 4)] for j in range(0, 7)]
    slot_info_for_printing = [[{} for i in range(0, 4)] for j in range(0, 7)]

    drug_details = set()
    time_details = set()

    for key, value in list(slot_details.items()):
        total_quantity = 0.0

        for item in value["drug_details"]:
            # commenting to remove hardcoded checking
            # if item["quantity"]:
            #     if float(item["quantity"]) > 0.5 and float(item["quantity"]) != 1.5 and float(item["quantity"]) != 2.5:
            #         item["quantity"] = str(int(float(item["quantity"])))

            try:
                qty = float(item["quantity"])
            except Exception as ex:
                qty = 0.0

            total_quantity += qty
            admin_date = value["hoa_date"]

            slot_row = int(value["slot_row"])
            slot_col = int(value["slot_column"])

            slot_location = map_pack_location(slot_row, slot_col)

            admin_time = str(value["hoa_time"])
            admin_time = datetime.datetime.strptime(admin_time, "%H:%M:%S").strftime("%I:%M %p")

            ndc = item["ndc"]
            drug_details.add(ndc)
            time_details.add(str(value["hoa_time"]))
            date = datetime.datetime.strptime(value["hoa_date"], '%Y-%m-%d').strftime('%a')
            slot_admin_period = admin_time + ' ' + str(date).upper()

            drug_name = item["drug_name"]
            drug_name = fn_shorten_drugname(drug_name)

            if item["quantity"].is_integer():  # converting to int to save space if perfect integer
                item["quantity"] = int(item["quantity"])
            slot_value = drug_name + "#" + str(item["quantity"])
            is_manual = item["is_manual"]
            if slot_value is None:
                slot_value = ''
            else:
                if is_manual:
                    slot_value = ':' + slot_value
                else:
                    slot_value = slot_value

            if slots_for_printing[slot_row][slot_col] is None:
                slots_for_printing[slot_row][slot_col] = []
                slots_for_printing[slot_row][slot_col].append(slot_admin_period)
                slots_for_printing[slot_row][slot_col].append(slot_value)
            else:
                slots_for_printing[slot_row][slot_col].append(slot_value)

            slot_info_for_printing[slot_row][slot_col]["total_quantity"] = total_quantity
            slot_info_for_printing[slot_row][slot_col]["slot_number"] = slot_location
            slot_info_for_printing[slot_row][slot_col]["admin_date"] = admin_date
            slot_info_for_printing[slot_row][slot_col]["batchid"] = batchid
            slot_info_for_printing[slot_row][slot_col]["patient_name"] = patient_name

    row_len = len(slots_for_printing)
    col_len = len(slots_for_printing[0])
    slots_for_priniting = set_order_for_slots(slots_for_printing, packid)
    slot_info_for_printing = set_order_for_slots(slot_info_for_printing, packid)

    # logger.info(slot_info_for_printing)

    for i in range(row_len):
        for j in range(col_len):
            slots_for_priniting[i][j] = CreateFlowable(slots_for_priniting[i][j], slot_info_for_printing[i][j], i,
                                                       time_details)

    return slots_for_priniting, drug_details, time_details


def set_order_for_slots(slots_for_printing, packid):
    """

    :param slots_for_printing:
    :param packid:
    :return:
    """
    start_day = 0

    slot_details_list = []
    if start_day == 0:
        logger.info("default start day called")
        for item in slots_for_printing:
            slot_details_list.insert(0, item)

    for item in slot_details_list:
        for index, _item in enumerate(item):
            if _item is None:
                item[index] = []

    return slot_details_list


def generate_qr_code(qr_text, patient_image=False):
    """

    :param qr_text:
    :return:
    """
    # draw a QR code
    qr_code = qr.QrCodeWidget(qr_text)
    try:
        bounds = qr_code.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        if patient_image:
            qr_drawing = Drawing(30, 30, transform=[40./width, 0, 0, 40./height, 0, 0])
        else:
            qr_drawing = Drawing(30, 30, transform=[40./width, 0, 0, 40./height, 0, 0])
        qr_drawing.add(qr_code)
        return qr_drawing
    except Exception as ex:
        logger.error(ex, exc_info=True)


def generate_qr_code_patient(qr_text):
    """

        @function: generate_qr_code_patient
        @createdBy: Manish Agarwal
        @createdDate: 02/16/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 02/16/2016
        @type: function
        @param: str
        @purpose - This is the new function created when qr code displayed for patient
                   does not fit in the box for patient details.This function takes qr
                   text as a argument and returns Drawing of dimension 30 * 30 for qr code.
        @input - qrtext
        @output - Drawing
    """
    # draw a QR code
    qr_code = qr.QrCodeWidget(qr_text)
    try:
        bounds = qr_code.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        qr_drawing = Drawing(30, 30, transform=[30./width, 0, 0, 30./height, 0, 0])
        qr_drawing.add(qr_code)
        return qr_drawing
    except Exception as ex:
        logger.error(ex, exc_info=True)


def map_pack_location(row, col):
    """
    @function: map_pack_location
    @createdBy: Manish Agarwal
    @createdDate: 7/22/2015
    @lastModifiedBy: Manish Agarwal
    @lastModifiedDate: 08/12/2015
    @type: function
    @param: int,int
    @purpose - Map the slot row and slot col from
              matrix index i,j to a pack location
    @input - 1,0
    @output - 14
    """
    TOTAL_ROWS_IN_PACKS = label_config.PACK_ROW

    if col % 2 == 0:
        location = (row + 1) + (col * TOTAL_ROWS_IN_PACKS)
    else:
        location = ((col + 1) * TOTAL_ROWS_IN_PACKS) - row
    return location


class CreateFlowable(Flowable):

    def __init__(self, slot_record, additional_slot_info, row_no, time_details):
        """

        :param slot_record:
        :param additional_slot_info:
        :return:
        """
        Flowable.__init__(self)
        self.slot_record = slot_record
        self.additional_slot_info = additional_slot_info
        self.row_no = row_no
        time_details = sorted(time_details)
        self.time_details = [datetime.datetime.strptime(item, "%H:%M:%S").strftime("%I:%M %p") for item in time_details]

    def draw(self):
        """
                @function: print_slot_label
                @createdBy: Manish Agarwal
                @createdDate: 12/23/2015
                @lastModifiedBy: Manish Agarwal
                @lastModifiedDate: 12/23/2015
                @type: function
                @param: String
                @purpose - Construct label slots for printing from slot details
                @input -

                @output -
                    []
        """
        slot_record = self.slot_record
        additional_slot_info = self.additional_slot_info

        if slot_record is None or not slot_record or len(slot_record) == 0:
            return ""

        batchid = ' ' + str(additional_slot_info["batchid"])
        patient_name = additional_slot_info["patient_name"]
        slot_location = additional_slot_info["slot_number"]
        admin_date = additional_slot_info["admin_date"]
        total_quantity = str(additional_slot_info["total_quantity"])

        printed_date = datetime.datetime.strptime(admin_date, '%Y-%m-%d').strftime('%m/%d')

        _quantity = total_quantity.split('.')
        if _quantity[1] == '0':
            total_quantity = _quantity[0]

        try:
            if slot_record is None or not slot_record or len(slot_record) == 0:
                logger.error("No slot record found")

            patient_name = patient_name.split(',')
            patient_name = ' ' + patient_name[0].strip()[0:5] + ',' + patient_name[1].strip()[0]

            _time = slot_record[0].split(" ")
            meditab_id = label_config.MEDITAB_ID
            qr_text = meditab_id + ", " + admin_date + "\n" + _time[0] + " " + _time[1] + ", " + str(batchid) + ", " + str(slot_location)
            qr = generate_qr_code(qr_text)

            hoa = slot_record[0].split(" ")
            self.canv.rotate(90)
            self.canv.setFont("tahoma", 10)

            _time = hoa[0] + " " + hoa[1]
            try:
                _color = self.time_details.index(_time)
            except Exception as ex:
                _color = 0

            self.canv.setFillColor(color_array[_color])
            self.canv.drawString(4, 98, hoa[0] + hoa[1][0])
            self.canv.setFillColor(black)
            # changing x coordinates for hoa day to align slots in label
            self.canv.drawString(75, 98, hoa[2])

            slot_record.pop(0)
            self.canv.setFont("tahoma", 8)
            self.canv.setFillColor(maroon)
            self.canv.drawString(2, 89, patient_name)
            self.canv.setFillColor(black)

            # changing x coordinates for printed date to align slots in label
            self.canv.drawString(75, 89, printed_date)

            self.canv.setFont("arial", 7)
            self.canv.drawString(4, 82, str(batchid))
            self.canv.drawString(76, 82, "#" + str(total_quantity))

            x = 74
            slot_record = sorted(slot_record)
            for item in slot_record:
                self.canv.drawString(4, x, str(item))
                x -= 8

            renderPDF.draw(qr, self.canv, 38, 78)

        except Exception as ex:
            logger.error(ex, exc_info=True)


class CreatePatientFlowable(Flowable):

    def __init__(self, qr_text):
        """

        :param slot_record:
        :param additional_slot_info:
        :return:
        """
        Flowable.__init__(self)
        self.qr_text = qr_text

    def draw(self):
        """
                @function: print_slot_label
                @createdBy: Manish Agarwal
                @createdDate: 12/23/2015
                @lastModifiedBy: Manish Agarwal
                @lastModifiedDate: 12/23/2015
                @type: function
                @param: String
                @purpose - Construct label slots for printing from slot details
                @input -

                @output -
                    []
        """
        try:
            self.canv.setFillColor(lightblue)

            self.canv.rect(0*inch, 0*inch, .6*inch, .7*inch, fill=1)

            qr = generate_qr_code(self.qr_text, True)
            self.canv.setFont("arial", 8)
            renderPDF.draw(qr, self.canv, 2, -3)

            self.canv.setFillColor(black)
            self.canv.drawString(6, 40, "UPLOAD")
            self.canv.drawString(8, 33, "PHOTO")

            # make text go straight up
            self.canv.rotate(90)
        except Exception as ex:
            logger.error(ex, exc_info=True)


def transform_input(input, patient_name, batchid):
    """
        @function: transform_input
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: str
        @purpose - Transform text input into reportlab Paragraph
        @input -
            type: (list)
                ["Phenlotypeleb 200mg #1","Oxydrocin 10mg #5",....]
        @output -
            Paragraph()
    """
    if input is None or not input or len(input) == 0:
        return ""

    pateint_name = patient_name.split(',')
    pateint_name = pateint_name[0].strip() + ',' + pateint_name[1].strip()[0]
    tranformed_input_start = '<para align=left><font name = tahoma size = 10><b>%s</b></font><font name = arial size = 7><br /><b>%s</b><br /><b>---%s----</b><br /></font><font name = arial size = 7>' %(input[0],pateint_name,batchid)
    input.pop(0)

    transform_input_body = ''
    for item in input:
        transform_input_body += '%s<br />' % item

    len_input = len(input) + 3

    for i in range(len_input, 9):
        transform_input_body += '%s<br />' % ''

    transform_input_end = '</font></para>'

    transformed_input = tranformed_input_start + transform_input_body + transform_input_end
    return RotatedParagraph(Paragraph(transformed_input, styleSheet["Normal"]))


def construct_pharmacy_details(pharmacy_data):
    """
        @function: construct_pharmacy_details
        @createdBy: Manish Agarwal
        @createdDate: 09/21/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/21/2015
        @type: function
        @param: int
        @purpose - Get the pharmacy details form the given pharmacy id and convert it into reportlab Paragraph.
        @input -
            type: (int)
                pharmacy_id = 5
        @output -
            Paragraph()
    """
    header_message = ""
    try:
        address_body = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + pharmacy_data["store_address"] + "&nbsp;&nbsp; * &nbsp;&nbsp;  PH: " + pharmacy_data["store_phone"]
        if pharmacy_data["store_fax"]:
            address_body += "&nbsp;&nbsp; FAX: " + pharmacy_data["store_fax"]
        if pharmacy_data["store_website"]:
            store_website = pharmacy_data["store_website"]
            address_body += "&nbsp;&nbsp;*&nbsp;&nbsp"
        else:
            store_website = ""
        pharmacy_details_body = '<para align = left><font name = arial size=8>%s' \
                                '<i>%s</i></font></para>' % (address_body, store_website)
        pharmacy_details_header = '<para align = left><font name = tahoma size=12><b>&nbsp;&nbsp;' \
                                  '&nbsp;&nbsp;%s' \
                                  '</b></font><font name = tahoma size=8><b>%s &nbsp;' \
                                  '</b></font></para>' % (pharmacy_data["store_name"], header_message)
        return pharmacy_details_header, pharmacy_details_body

    except Exception as ex:
        logger.error(ex, exc_info=True)
        return None, None


def construct_patient_details(patient_info, packid):
    """
        @function: construct_patient_details
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: int
        @purpose - Construct pateint header from the given pateint details
        @input -
            type: (dict)

        @output -

    """
    patient_no = patient_info["patient_no"]
    patient_name = patient_info["patient_name"] + "&nbsp;"
    patient_id = '(' + patient_no + ')'
    patient_address = patient_info["address1"]
    workphone = patient_info["workphone"]
    allergy = patient_info["allergy"]
    if allergy is None:
        allergy = "No Known Allergy"
    allergy = allergy[0:32]

    pack_id = str(packid)
    font_sz = '8'
    if len(patient_address) > 32:
        font_sz = '7'

    # if the length of allergy is greater than 30
    if len(allergy) > 30:
        allergy = allergy[0:30]
    if len(patient_address) > 32:
        all_font_sz = 7
    else:
        all_font_sz = 8

    pateint_details = "<para align=left><font name = tahoma size=12><b>%s</b></font></para>" %(patient_name+patient_id)
    pateint_address = "<para align=left><font name = tahoma_normal size=%s>%s &nbsp;&nbsp;*&nbsp;&nbsp;Ph:%s</font></para>" %(font_sz, patient_address, workphone)
    pateint_allergy = "<para align=left color=red><font name = tahoma_normal size=%s>%s</font></para>" %(all_font_sz, allergy)
    pack_id = "<para align=left><font name = tahoma size=%s><b>Pack ID:&nbsp;%s</b></font></para>" %(font_sz, pack_id)

    return Paragraph(pateint_details, styleSheet["Normal"]), Paragraph(pateint_address, styleSheet["Normal"]), Paragraph(pateint_allergy, styleSheet["Normal"]), Paragraph(pack_id, styleSheet["Normal"])


def construct_facility_details(patient_info, pack_info):
    """
        @function: construct_facility_details
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: int
        @purpose - Construct patient header from the given patient details
        @input -
            type: (dict)

        @output -

    """
    facility_name = patient_info["facility_name"]
    if facility_name is None:
        facility_name = patient_info["facility_name"]
    start_date = pack_info["filled_start_date"]
    end_date = pack_info["filled_end_date"]
    fill = pack_info["filled_date"]

    fill = datetime.datetime.strptime(fill, '%Y-%m-%d')
    filled_date_exp = fill + timedelta(days=180)
    filled_date_exp = filled_date_exp.strftime('%m/%y')

    fill = str(fill.strftime('%m/%d/%y'))

    filled_by = pack_info["filled_by"]
    expiration = filled_date_exp
    date_time = pack_info["delivery_schedule"]

    start_filling_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    start_filling_date = start_filling_date.strftime('%m/%d/%y')
    end_date = end_date.strftime('%m/%d/%y')
    admin_period = str(start_filling_date) + " - " + str(end_date)

    facility_details = "<para align=right><font name = tahoma size = 12><b>%s</b></font></para>" %(facility_name)
    admin_period = "<para align=right color = blue><font name = tahoma_normal size = 8><b>Admin Period: %s &nbsp;&nbsp;&nbsp; %s</b></font></para>" %(admin_period, date_time)
    details = "<para align=right><font name = tahoma_normal size = 7>Fill:&nbsp;%s&nbsp;&nbsp;Filled by:&nbsp;%s &nbsp; Exp:&nbsp;%s &nbsp; Tech: &nbsp;&nbsp;&nbsp; Rph:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</font></para>" %(fill,filled_by,expiration)
    return Paragraph(facility_details, styleSheet["Normal"]), Paragraph(admin_period, styleSheet["Normal"]),Paragraph(details,styleSheet["Normal"])


def construct_table_for_drug_information_top(drug_info, header = False):
    """
        @function: construct_table_for_drug_information_top
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: int
        @purpose - Construct pateint header from the given pateint details
        @input -
            type: (dict)

        @output -

    """
    drug_info1 = drug_info[0]
    drug_info2 = {}
    try:
        drug_info2 = drug_info[1]
    except IndexError:
        pass

    for k1, v1 in list(drug_info1.items()):
        rx_no1, mfg1, qty1, refill1, morn1, noon1, eve1, bed1 = v1["pharmacy_rx_no"], v1["manufacturer"], v1["print_qty"], \
        v1["remaining_refill"], v1["morning"], v1["noon"], v1["evening"], v1["bed"]

    if morn1 == 0:
        morn1 = ''
    if noon1 == 0:
        noon1 = ''
    if eve1 == 0:
        eve1 = ''
    if bed1 == 0:
        bed1 = ''

    rx_no2, mfg2, qty2, refill2, morn2, noon2, eve2, bed2 = "", "", "", "", "", "", "", ""

    right_column = 17
    new_column1 = 9
    new_column2 = 16
    if drug_info2:
        right_column = 8
        new_column1 = 30
        new_column2 = 30
        for k1, v1 in list(drug_info2.items()):
            rx_no2, mfg2, qty2, refill2, morn2, noon2, eve2, bed2 = v1["pharmacy_rx_no"], v1["manufacturer"], v1["print_qty"], \
            v1["remaining_refill"], v1["morning"], v1["noon"], v1["evening"], v1["bed"]

    if morn2 == 0:
        morn2 = ''
    if noon2 == 0:
        noon2 = ''
    if eve2 == 0:
        eve2 = ''
    if bed2 == 0:
        bed2 = ''

    colwidths = [.645*inch, .645*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, .1*inch, .645*inch, .645*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch]

    rx_no1 = '<para align = left color = brown><font name = tahoma size = 8><b>%s</b></font></para>' % rx_no1
    mfg1 = '<para align = left color = brown><font name = tahoma size = 8><b>%s</b></font></para>' % mfg1[0:6]
    qty1 = '<para align = left color = brown><font name = tahoma size = 8><b>%s</b></font></para>' % qty1
    refill1 = '<para align = left color = brown><font name = tahoma size = 8><b>%s</b></font></para>' % refill1
    morn1 = '<para align = left color = blue><font name = tahoma size = 8><b>%s</b></font></para>' % morn1
    noon1 = '<para align = left color = blue><font name = tahoma size = 8><b>%s</b></font></para>' % noon1
    eve1 = '<para align = left color = blue><font name = tahoma size = 8><b>%s</b></font></para>' % eve1
    bed1 = '<para align = left color = blue><font name = tahoma size = 8><b>%s</b></font></para>' % bed1
    empty = '<para align = left color = blue><font name = tahoma size = 8><b></b></font></para>'
    rx_no2 = '<para align = left color = brown><font name  = tahoma size = 8><b>%s</b></font></para>' % rx_no2
    mfg2 = '<para align = left color = brown><font name = tahoma size = 8><b>%s</b></font></para>' % mfg2[0:6]
    qty2 = '<para align = left color = brown><font name = tahoma size = 8><b>%s</b></font></para>' % qty2
    refill2 = '<para align = left color = brown><font name = tahoma size = 8><b>%s</b></font></para>' % refill2
    morn2 = '<para align = left color = blue><font name = tahoma size = 8><b>%s</b></font></para>' % morn2
    noon2 = '<para align = left color = blue><font name = tahoma size = 8><b>%s</b></font></para>' % noon2
    eve2 = '<para align = left color = blue><font name = tahoma size = 8><b>%s</b></font></para>' % eve2
    bed2 = '<para align = left color = blue><font name = tahoma size = 8><b>%s</b></font></para>' % bed2

    rowwidth  = 1 * [0.15 * inch]

    data = [[Paragraph(rx_no1, styleSheet["Normal"]), Paragraph(mfg1, styleSheet["Normal"]), Paragraph(qty1,styleSheet["Normal"]),Paragraph(refill1,styleSheet["Normal"]),Paragraph(morn1,styleSheet["Normal"]),Paragraph(noon1,styleSheet["Normal"]),Paragraph(eve1,styleSheet["Normal"]),Paragraph(bed1,styleSheet["Normal"]),"",Paragraph(rx_no2,styleSheet["Normal"]),Paragraph(mfg2,styleSheet["Normal"]),Paragraph(qty2,styleSheet["Normal"]),Paragraph(refill2,styleSheet["Normal"]),Paragraph(morn2,styleSheet["Normal"]),Paragraph(noon2,styleSheet["Normal"]),Paragraph(eve2,styleSheet["Normal"]),Paragraph(bed2,styleSheet["Normal"])]]

    table = Table(data, colwidths, rowwidth)
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 20), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('INNERGRID', (7, 0), (9, 0), 0.25, colors.black),
        ('LINEABOVE', (8, 0), (right_column, 0), 2, colors.white),
        ('LINEBELOW', (8, 0), (right_column, 0), 2, colors.white),
        ('LINEBEFORE', (new_column1, 0), (new_column1, 0), 2, colors.white),
        ('LINEAFTER', (new_column2, 0), (new_column2, 0), 2, colors.white)
    ]))
    return table


def construct_table_for_drug_details(drug_info, first=False):
    """
        @function: construct_table_for_drug_details
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: int
        @purpose - Construct patient header from the given patient details
        @input -
            type: (dict)

        @output -

    """
    drug_info1 = drug_info[0]
    drug_info2 = []
    sig1_font_size = 10
    sig2_font_size = 10
    max_len_for_font_size_10 = 46
    max_len_for_font_size_7 = 30
    try:
        drug_info2 = drug_info[1]
    except Exception as ex:
        pass

    for key, value in list(drug_info1.items()):
        drug_name1, sig1, imagename1, strength_value1, strength1 = value["drug_name"], value["sig"], value["image_name"], value["strength_value"],value["strength"]

    drug_name1_with_strength = drug_name1 + " " + strength_value1 + " " + strength1
    if len(drug_name1_with_strength) > max_len_for_font_size_10:
        drug_name1_with_strength = fn_shorten_drugname_v2(drug_name1, strength=strength1, strength_value=strength_value1, ai_width=46, include_strength=True)
    drug_name_font_size1 = 10
    if len(drug_name1_with_strength) > max_len_for_font_size_7:
        drug_name_font_size1 = 7

    drug_name1 = Paragraph('''<para align = left><font  name = tahoma_normal size = %s><b>%s</b></font></para>''' %(drug_name_font_size1, drug_name1_with_strength),styleSheet["Normal"])

    if len(sig1) > 85:
        sig1_font_size = 6

    drug_name2, sig2, imagename2, strength_value2, strength2 = "", "", "", "", ""

    if drug_info2:
        for key, value in list(drug_info2.items()):
            drug_name2, sig2, imagename2, strength_value2, strength2= value["drug_name"], value["sig"], value["image_name"], value["strength_value"], value["strength"]

    if len(sig2) > 85:
        sig2_font_size = 6

    drug_name2_with_strength = drug_name2 + " " + strength_value2 + " " + strength2
    if len(drug_name2_with_strength) > max_len_for_font_size_10:
        drug_name2_with_strength = fn_shorten_drugname_v2(drug_name2, strength=strength2, strength_value=strength_value2, ai_width=46, include_strength=True)

    drug_name_font_size2 = 10
    if len(drug_name2_with_strength) > max_len_for_font_size_7:
        drug_name_font_size2 = 7
    drug_name2 = Paragraph('''<para align = left><font name = tahoma_normal size = %s><b>%s</b></font></para>''' %(drug_name_font_size2, drug_name2_with_strength), styleSheet["Normal"])

    styleSheet["Normal"].leading = 10
    styleSheet["Normal"].firstLineIndent = 0
    styleSheet["Normal"].alignment=TA_LEFT
    styleSheet["Normal"].borderPadding= 0

    P1 = Paragraph('''<para align = left><font name = tahoma_normal size = %s><b>%s</b></font></para>''' %(sig1_font_size,sig1),styleSheet["Normal"])
    P2 = Paragraph('''<para align = left><font name = tahoma_normal size = %s><b>%s</b></font></para>''' %(sig2_font_size,sig2),styleSheet["Normal"])
    styleSheet["Normal"].leading = 9

    try:
        if imagename1:
            image1 = os.path.join('drug_images', imagename1)
            I1 = Image(image1)
            I1.drawHeight = 0.42 * inch
            I1.drawWidth  = 0.42 * inch
            I1.hAlign = "LEFT"
        else:
            I1 = ''
    except Exception as ex:
        I1 = ''

    I2 = ''

    if imagename2:
        image2 = os.path.join('drug_images', imagename2)
        try:
            I2 = Image(image2)
            I2.drawHeight = 0.42 * inch
            I2.drawWidth = 0.42 * inch
            I2.hAlign = "LEFT"
        except Exception as ex:
            I2 = ''

    if first:
        colwidths = [2.84*inch, 0.71*inch, .1 * inch, 2.84*inch, 0.71*inch, 0.2]
        rowwidth  = [0.15 * inch, 0.34 * inch]
        data = [[drug_name1, I1, '', drug_name2, I2, ''], [P1, '', '', P2, '']]
    else:
        colwidths = [2.84*inch, 0.71*inch, .1 * inch, 2.84*inch, 0.71*inch]
        rowwidth  = [0.15 * inch, 0.34 * inch]
        data = [[drug_name1, I1, '', drug_name2, I2], [P1, '', '', P2, '']]

    table = Table(data, colwidths, rowwidth)
    table.setStyle(TableStyle([
        # ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 1), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (0, 0), 0),
        ('BOTTOMPADDING', (3, 0), (3, 0), 0),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('SPAN', (-1, -1), (-1, -2)),
        ('SPAN', (1, 1), (1, 0)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    return table


def construct_table_for_drug_information_bottom(drug_info):
    """
        @function: construct_table_for_drug_information_bottom
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: int
        @purpose - Construct pateint header from the given pateint details
        @input -
            type: (dict)

        @output -

    """
    drug_info1 = drug_info[0]
    drug_info2 = {}

    try:
        drug_info2 = drug_info[1]
    except IndexError:
        pass

    doctor_name1, doctor_phone1, drug_type1, shape1, color1, caution11, caution21, imprint1 = '', '', '', '', '', '', '', ''
    for key, value in list(drug_info1.items()):
        doctor_name1, doctor_phone1, drug_type1, shape1, color1, caution11, caution21 = 'Dr: ' + value["doctor_name"].title(), value["cellphone"], \
                value["drug_type"], value["shape"], value["color"], value["caution1"], value["caution2"]
        if len(value["imprint"]) > 0:
            imprint1 = '(' + value["imprint"] + ')'

    if not drug_type1:
        drug_type1 = ''
    else:
        drug_type1 = drug_type1.split(' ')
        drug_type1 = drug_type1[0] + ": " + drug_type1[2]

    if not caution11:
        caution11 = ''
    if not caution21:
        caution21 = ''

    doctor_name2, doctor_phone2, drug_type2, shape2, color2, imprint2 = '', '', '', '', '', ''

    P2 = ''

    if drug_info2:
        for key, value in list(drug_info2.items()):
            doctor_name2, doctor_phone2, drug_type2, shape2, color2, caution12, caution22 = 'Dr: ' + value["doctor_name"].title(), value["cellphone"], \
                    value["drug_type"], value["shape"], value["color"], value["caution1"], value["caution2"]
            if len(value["imprint"]) > 0 and value["imprint"]:
                imprint2 = '(' + value["imprint"] + ')'

        if not caution12:
            caution12 = ''
        if not caution22:
            caution22 = ''
        if not drug_type2:
            drug_type2 = ''
        else:
            drug_type2 = drug_type2.split(' ')
            drug_type2 = drug_type2[0] + ": " + drug_type2[2][0:5]

        if caution12 or caution22:
            P2 = Paragraph('''<para align = left><font name = tahoma_normal size = 6 color = blue>Caution:&nbsp;%s</font></para>''' %(caution12+caution22), styleSheet["Normal"])

    colwidths = [1.775*inch, 1.775*inch, .1 * inch, 1.775*inch, 1.775*inch]
    rowwidth  = [0.15 * inch, 0.25 * inch]

    try:
        P1 = Paragraph('''<para align = left><font name = tahoma_normal size = 6 color = blue>Caution:&nbsp;%s</font></para>''' %(caution11+caution21), styleSheet["Normal"])
    except Exception as ex:
        logger.error(ex, exc_info=True)
        P1 = ''
    if drug_type1:
        imprint1 = ''
        drug_type1 = drug_type1[0:25].upper()
    else:
        imprint1 = imprint1[0:13].upper()

    if drug_type2:
        imprint2 = ''
        drug_type2 = drug_type2[0:25].upper()
    else:
        imprint2 = imprint2[0:13].upper()

    if not shape1:
        shape1 = ''
    if not shape2:
        shape2 = ''
    if not color1:
        color1 = ''
    if not color2:
        color2 = ''
    if not imprint1:
        imprint1 = ''
    if not imprint2:
        imprint2 = ''
    if not doctor_phone1:
        doctor_phone1 = ''
    if not doctor_phone2:
        doctor_phone2 = ''

    data = [[color1 + "  " + shape1 + '  ' + drug_type1 + '  ' + imprint1, doctor_name1[0:16] + "    " + doctor_phone1, '', color2 + "  " + shape2 + '  ' + drug_type2 + '  ' + imprint2, doctor_name2[0:16] + "," + doctor_phone2],
        [P1, '', '', P2]]

    table = Table(data, colwidths, rowwidth)
    table.setStyle(TableStyle([
        # ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.blue),
        ('SPAN', (-1, -1), (3, -1)),
        ('SPAN', (1, 1), (0, 1)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    return table


def construct_table_for_patient_information_bottom(patient_info, time_details, packid):
    """
        @function: construct_table_for_patient_information_bottom
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: int
        @purpose - Construct pateint header from the given pateint details
        @input -
            type: (dict)

        @output -

    """
    birth_date = patient_info["dob"]
    birth_date = datetime.datetime.strptime(birth_date, '%Y-%m-%d')
    birth_date = birth_date.strftime('%m/%d/%y')

    start_date = patient_info["filled_start_date"]
    start_filling_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = patient_info["filled_end_date"]
    start_filling_date = start_filling_date.strftime('%m/%d/%y')
    end_date = end_date.strftime('%m/%d/%y')
    admin_period = str(start_filling_date) + " - " + str(end_date)

    font_size = 14
    font_size_sm = 7
    bottom_padding = 10
    if len(patient_info["facility_name"]) > 20:
        font_size = 12
        font_size_sm = 5

    patient_name = Paragraph('''<para align = left><font name = tahoma size = %s><b>&nbsp;&nbsp;&nbsp;&nbsp;%s
    </b></font></para>''' % (font_size, patient_info["patient_name"]), styleSheet["Normal"])

    patient_id = Paragraph('''<para align = left><font name = tahoma size = %s><b>%s</b></font></para>'''
                           %(font_size, patient_info["patient_group_no"]), styleSheet["Normal"])

    pack_id = Paragraph('''<para align = left><font name = tahoma size = %s><b>%s</b></font></para>'''
                        %(font_size, patient_info["pack_display_id"].split('.')[0]), styleSheet["Normal"])

    admin_period = Paragraph('''<para align = left color=red><font name = tahoma_normal size = %s>
    Admin Period:&nbsp;%s</font></para>''' % (font_size_sm, admin_period), styleSheet["Normal"])

    dob = Paragraph('''<para align = left><font name = tahoma_normal size = %s>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Bdate:&nbsp;%s&nbsp;&nbsp;%s&nbsp;&nbsp;%s</font></para>'''
                    %(font_size_sm, birth_date, patient_info["patient_group_no"], patient_info["facility_name"]),
                    styleSheet["Normal"])

    time_info = '<para align = left><font name = tahoma size = 8><b>'

    len_time_details = len(time_details)

    if len_time_details == 1:
        time_info += '%s' %time_details[0]
    if len_time_details == 2:
        time_info += '%s<br />%s' %(time_details[0], time_details[1])
    if len_time_details == 3:
        time_info += '%s<br />%s<br />%s' %(time_details[0], time_details[1], time_details[2])
    if len_time_details == 4:
        time_info += '%s<br />%s<br />%s<br />%s' %(time_details[0], time_details[1], time_details[2], time_details[3])

    time_info = RotatedPara(time_info, styleSheet["Normal"])

    colwidths = [1.75*inch, .35 * inch, 2.8 * inch, 1.32*inch, 1 * inch]
    rowwidth  = [.3 * inch, 0.15 * inch]

    patient_picture = patient_info["patient_picture"]

    if not patient_picture:
        qr_text = "GETPHOTO" + ":" + str(label_config.MEDITAB_ID) + ":" + str(packid)
        I = generate_qr_code(qr_text)
    else:
        # todo code for patient image download - no need
        patient_image = os.path.join('patient_images', patient_picture)
        if os.path.isfile(patient_image):
            I = Image(patient_image)
            I.drawHeight = 0.60 * inch
            I.drawWidth = 0.50 * inch
            I.hAlign = "LEFT"
        else:
            qr_text = "GETPHOTO" + ":" + str(label_config.MEDITAB_ID) + ":" + str(packid)
            I = generate_qr_code(qr_text)

    data = [[patient_id, I, patient_name, pack_id, ''], [admin_period, '', dob, '', time_info]]

    table = Table(data, colwidths, rowwidth)
    table.setStyle(TableStyle([
                               # ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ('LEFTPADDING',  (0, 0), (-1, -1),0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                               ('TOPPADDING', (0, 0), (-1, 0), 10), ('BOTTOMPADDING', (0, 0), (-1, 0), bottom_padding),
                               ('BOTTOMPADDING', (1, 0), (1, 1), 0),
                               ('TOPPADDING', (0, 1), (0, -1), 0),
                               ('SPAN', (1, 1), (1, 0)),
                               ('TOPPADDING', (1, 1), (1, 0), 0),
                               # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ]))
    return table


def construct_drug_label(drug_info, first):
    """
        @function: construct_drug_label
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: int
        @purpose - Construct pateint header from the given pateint details
        @input -
            type: (dict)

        @output -

    """
    if first:
        drug_table1 = construct_table_for_drug_information_top(drug_info, True)
        rowwidth = 1 * [0.15 * inch]

        try:
            _drug_info = drug_info[1]
            col1 = -1
            col2 = 8
            col3 = -200
            colwidths = [.645*inch, .645*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, .1*inch,.645*inch,.645*inch,0.38*inch,0.38*inch,0.38*inch,0.38*inch,0.38*inch,0.38*inch]
            data = [[Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Rx No</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Mfg</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Qty</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Refill</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Morn</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Noon</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Even</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Bed</b></font></para>''',styleSheet["Normal"]),"",Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Rx No</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Mfg</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font  name = tahoma size = 7><b>Qty</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Refill</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Morn</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Noon</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Even</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Bed</b></font></para>''',styleSheet["Normal"])]]
        except Exception as ex:
            col1 = 7
            col2 = 16
            col3 = 9
            colwidths = [.645*inch, .645*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch,
                         .1*inch, .645*inch, .645*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch, 0.38*inch]
            data = [[Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Rx No</b></font></para>''',
                               styleSheet["Normal"]), Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Mfg</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Qty</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Refill</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Morn</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Noon</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Even</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = brown><font name = tahoma size = 7><b>Bed</b></font></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = white></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = white></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = white></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = white></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = white></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = white></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = white></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = white></para>''',styleSheet["Normal"]),Paragraph('''<para align = left color = white></para>''',styleSheet["Normal"])]]

        table = Table(data, colwidths, rowwidth)
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (col1,col1), 0.25, colors.black),
                               ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                               ('TOPPADDING', (0, 0), (-1, -1), 20), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                               ('FONTSIZE', (0, 0), (-1, -1), 8),
                               ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
                               ('INNERGRID', (7, 0), (9, 0), 0.25, colors.black),
                               ('BACKGROUND', (8, 0), (col2, 0), colors.white),
                               ('LINEABOVE', (8, 0), (col2, 0), 1, colors.white),
                               ('LINEBELOW', (8, 0), (col2, 0), 1, colors.white),
                               ('LINEBEFORE', (col3, 0), (col3, 0), 2, colors.white)
                       ]))
    else:
        drug_table1 = construct_table_for_drug_information_top(drug_info)
        table = None

    drug_table2 = construct_table_for_drug_details(drug_info, first)
    drug_table3 = construct_table_for_drug_information_bottom(drug_info)

    return drug_table1, drug_table2, drug_table3, table


def prepare_print_label(current_pack_drug_info, pack_info, slot_data, patient_info, pharmacy_header, pharmacy_details, doc, time_details, packid, contd, system_id, second_pack = False):
    """
        @function: prepare_print_label
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: int
        @purpose - Construct patient header from the given patient details
        @input -
            type: (dict)

        @output -

    """
    elements = []
    spacer = Spacer(0, 0.06*inch)
    elements.append(Paragraph(pharmacy_header, styleSheet["Normal"]))
    elements.append(spacer)
    spacer = Spacer(0, 0.04*inch)
    elements.append(Paragraph(pharmacy_details, styleSheet["Normal"]))

    P1, P2, P3, P4= construct_patient_details(patient_info, packid)
    F1, F2, F3 = construct_facility_details(patient_info, pack_info)

    barcode_value = pack_info["pack_display_id"]
    barcode_value = '+' + str(barcode_value)

    barcode39Std = code93.Standard93(barcode_value)
    barcode = get_barcode(value=barcode_value, width = 130)

    patient_picture = patient_info["patient_picture"]

    if not patient_picture:
        patient_image = ''
    else:
        patient_image = os.path.join('patient_images', str(system_id), patient_picture)

    if os.path.isfile(patient_image):
        I = Image(patient_image)
        I.drawHeight = 0.6 * inch
        I.drawWidth  = 0.6 * inch
        I.hAlign = "LEFT"
    else:
        # try to download patient_image
        res = get_patient_image(system_id, patient_picture, packid)
        if res:
            I = Image(patient_image)
            I.drawHeight = 0.6 * inch
            I.drawWidth  = 0.6 * inch
            I.hAlign = "LEFT"
        else:
            qr_text = "GETPHOTO" + ":" + str(label_config.MEDITAB_ID) + ":" + str(packid)
            I = CreatePatientFlowable(qr_text)

    green_image2 = Image(os.path.join('drug_images', 'new_left_green.png'))
    green_image2.drawHeight = 4.2 * inch
    green_image2.drawWidth = 0.20 * inch
    green_image2.hAlign = "RIGHT"

    dataFront = [[I, P1, '', F1], ['', '', '', ''], ['', P2, '', F2], ['', P3, barcode], ['', P4, '', F3]]

    # Creates a table with 2 columns, variable width
    colwidths = [.7*inch, 1.7*inch, 1.55*inch, 3.30*inch]

    # Two rows with variable height
    rowheights = [.26 * inch, .06*inch, .14*inch, .14*inch, .14*inch]

    table = Table(dataFront, colwidths, rowheights)
    table.setStyle(TableStyle([
        # ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1),0),
        ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('SPAN', (0, 4), (0, 0)),
        ('SPAN', (2, 4), (2, 3)),
        ('SPAN', (1, 0), (2, 0)),
        ('SPAN', (1, 2), (2, 2)),
        # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    elements.append(table)
    spacer = Spacer(0, 0.05*inch)
    elements.append(spacer)

    drug_info_len = len(current_pack_drug_info)
    spacer = Spacer(0, 0.03*inch)

    for i in range(0, drug_info_len, 2):
        if i == 0:
            drug_table1, drug_table2, drug_table3, table = construct_drug_label(current_pack_drug_info[i:i+2], first = True)
        else:
            drug_table1, drug_table2, drug_table3, table = construct_drug_label(current_pack_drug_info[i:i+2], first = False)
        if table:
            elements.append(table)
            spacer = Spacer(0, 0.02*inch)
            elements.append(spacer)
            elements.append(drug_table1)
            elements.append(drug_table2)
            spacer = Spacer(0, 0.01*inch)
            elements.append(spacer)
            elements.append(drug_table3)
            # spacer = Spacer(0, 0.03*inch)
            elements.append(spacer)
        else:
            elements.append(drug_table1)
            elements.append(drug_table2)
            spacer = Spacer(0, 0.01*inch)
            elements.append(spacer)
            elements.append(drug_table3)
            # elements.append(spacer)

    if drug_info_len < 14:
        remaining_slots = int((14 - drug_info_len) / 2)
        if remaining_slots == 1:
            spacer = Spacer(0, 1.05*inch)
            elements.append(spacer)
        elif remaining_slots == 2:
            spacer = Spacer(0, 1.05*2*inch)
            elements.append(spacer)
        elif remaining_slots == 3:
            spacer = Spacer(0, 3.15*inch)
            elements.append(spacer)
        elif remaining_slots == 4:
            spacer = Spacer(0, 4.20*inch)
            elements.append(spacer)
        elif remaining_slots == 5:
            spacer = Spacer(0, 5.25*inch)
            elements.append(spacer)
        elif remaining_slots == 6:
            spacer = Spacer(0, 6.30*inch)
            elements.append(spacer)
        elif remaining_slots == 7:
            spacer = Spacer(0, 6.25*inch)
            elements.append(spacer)

    if contd:
        spacer = Spacer(0, 0.55*inch)
        elements.append(spacer)
        spacer = Spacer(0, 0.30*inch)
        box = BoxyLine()
        elements.append(box)
        elements.append(spacer)
        elements.append(PatientInfo(patient_info, time_details, packid, system_id, pack_info))
        # elements.append(construct_table_for_patient_information_bottom(patient_info,time_details,packid))

        spacer = Spacer(0, 0.45*inch)
        elements.append(spacer)

        elements.append(DrawImage())

        if not second_pack:
            table = Table(slot_data, 4*[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch],[1.41*inch,1.41*inch,1.41*inch,1.41*inch,1.41*inch,1.41*inch,1.41*inch])

            table.setStyle(TableStyle([
                # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                # ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                # ('ALIGN', (0,0), (-1, -1), 'RIGHT'),
                # ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 22),
                ('LEFTPADDING', (1, 0), (1, 6), 0),
                ('LEFTPADDING', (0, 0), (0, 6), 100),
                ('LEFTPADDING', (1, 0), (1, 6), 102),
                ('LEFTPADDING', (2, 0), (2, 6), 121),
                ('LEFTPADDING', (3, 0), (3, 6), 130),
                ('BOTTOMPADDING', (0, 0), (3, 1), 0),
                ('BOTTOMPADDING', (0, 2), (3, 3), 2),
                ('BOTTOMPADDING', (0, 4), (3, 5), 2),
                ('BOTTOMPADDING', (0, 6), (3, 6), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(table)
    else:
        spacer = Spacer(0, 0.95*inch)
        elements.append(spacer)
        spacer = Spacer(0, 0.30*inch)
        box = BoxyLine()
        elements.append(box)
        elements.append(spacer)
        elements.append(PatientInfo(patient_info, time_details, packid, system_id, pack_info))
        # elements.append(construct_table_for_patient_information_bottom(patient_info,time_details,packid))

        spacer = Spacer(0, 0.55*inch)
        elements.append(spacer)

        elements.append(DrawImage())
        spacer = Spacer(0, 0.1*inch)
        elements.append(spacer)

        if not second_pack:
             table=Table(slot_data, 4*[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch],[1.41*inch,1.41*inch,1.41*inch,1.41*inch,1.41*inch,1.41*inch,1.41*inch])

             table.setStyle(TableStyle([
                           # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                           # ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                           # ('ALIGN', (0,0), (-1, -1), 'RIGHT'),
                           # ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                           ('TOPPADDING', (0, 0), (-1, -1), 22),
                           ('LEFTPADDING', (1, 0), (1, 6), 0),
                           ('LEFTPADDING', (0, 0), (0, 6), 100),
                           ('LEFTPADDING', (1, 0), (1, 6), 102),
                           ('LEFTPADDING', (2, 0), (2, 6), 121),
                           ('LEFTPADDING', (3, 0), (3, 6), 130),
                           # ('BOTTOMPADDING', (0, 0), (3, 1), 11),
                           # ('BOTTOMPADDING', (0, 2), (3, 3), 6),
                           # ('BOTTOMPADDING', (0, 4), (3, 4), 3),
                           # ('BOTTOMPADDING', (0, 6), (3, 6), 0),
                           # ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                           ('BOTTOMPADDING', (0, 0), (3, 1), 18),
                           ('BOTTOMPADDING', (0, 2), (3, 2), 14),
                           ('BOTTOMPADDING', (0, 3), (3, 3), 11),
                           ('BOTTOMPADDING', (0, 4), (3, 4), 11),
                           ('BOTTOMPADDING', (0, 5), (3, 5), 6),
                           ('BOTTOMPADDING', (0, 6), (3, 6), 0),
                           ('RIGHTPADDING', (0, 0), (-1, -1), 0)
                           ]))
             elements.append(table)

    # write the document to disk
    try:
        doc.build(elements)
    except Exception as ex:
        logger.error(ex, exc_info=True)


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
            download_blob(image_name, drug_image, label_config.BUCKET_DRUG_IMAGE_PATH, drug_image=True)
            logger.info('Downloaded Drug Image: ' + str(image_name))
    except Exception as e:
        logger.warning(str(image_name) + ': Downloading Failed '+ str(e))
        try:
            os.remove(image_path)  # could not download file, so remove
        except Exception:
            pass
        logger.error(e)


def get_drug_images(drug_images, drug_image_dir):
    """

    :param drug_images:
    :param drug_image_dir:
    :return:
    """
    try:
        threads_list = []
        # try to download drug images required if any exception skip
        for drug_image in drug_images:
            drug_image_path = os.path.join(drug_image_dir, drug_image)
            if not os.path.exists(drug_image_path):
                t = threading.Thread(target=download_drug_image, args=[drug_image, drug_image_path])
                threads_list.append(t)
                t.start()
            else:  # download if only drug image is older than some constant time
                modification_in_hours = int((os.path.getmtime(drug_image_path) - time.time()) / 3600)
                if modification_in_hours > label_config.DRUG_IMAGE_MODIFICATION_ALLOWED:
                    t = threading.Thread(target=download_drug_image, args=[drug_image, drug_image_path])
                    threads_list.append(t)
                    t.start()
        [th.join() for th in threads_list]  # wait for all images to download
    except Exception as e:
        logger.error(e)

#
# def print_label(dict_label_info, canister_based_manual=False):
#     """
#         @function: prepare_print_data
#         @createdBy: Manish Agarwal
#         @createdDate: 09/23/2015
#         @lastModifiedBy: Manish Agarwal
#         @lastModifiedDate: 09/23/2015
#         @type: function
#         @param: int
#         @purpose - Construct patient header from the given pateint details
#         @input -
#             type: (dict)
#
#         @output -
#
#     """
#
#     pack_id = dict_label_info["pack_id"]
#     pack_display_id = dict_label_info["pack_display_id"]
#     # pharmacy_id = dict_label_info["pharmacy_id"]
#     patient_id = dict_label_info["patient_id"]
#     user_id = dict_label_info["user_id"]
#     system_id = dict_label_info["system_id"]
#     patient_data, pharmacy_rx_data, pack_info, pharmacy_data, drug_images = parse_drug_details(
#         get_drug_details(patient_id, pack_id, system_id))
#     slot_data, ndc_list, time_details = construct_label_slots(get_slot_details(pack_id, system_id, canister_based_manual),
#                                                               patient_data["patient_name"], pack_display_id, pack_id)
#
#     time_details = sorted(time_details)
#     time_details = [datetime.datetime.strptime(item, "%H:%M:%S").strftime("%I:%M %p") for item in time_details]
#
#     pharmacy_header, pharmacy_details = construct_pharmacy_details(pharmacy_data)
#
#     get_drug_images(drug_images, label_config.DRUG_PATH)
#
#     length = len(pharmacy_rx_data)
#     file_1 = str(pack_id) + '.pdf'
#     file_2 = str(pack_id) + '_cont.pdf'
#     generated_path1 = os.path.join('pack_labels', 'generated', file_1)
#     generated_path2 = os.path.join('pack_labels', 'generated', file_2)
#     path = []
#     label_files = []
#     file_names = []
#
#     try:
#         if length <= 14:
#             label_files.append(generated_path1)
#             file_names.append(file_1)
#             doc = SimpleDocTemplate(generated_path1, pagesize=(568.0, 1513.27), rightMargin=0, leftMargin=5,
#                                     topMargin=0, bottomMargin=0)
#             prepare_print_label(pharmacy_rx_data, pack_info, slot_data, patient_data, pharmacy_header, pharmacy_details, doc, time_details, pack_display_id, False, system_id)
#             # send_to_printer(generated_path1)
#             path.append(os.path.abspath(generated_path1))
#
#         else:
#             label_files.append(generated_path1)
#             label_files.append(generated_path2)
#             file_names.append(file_1)
#             file_names.append(file_2)
#             doc = SimpleDocTemplate(generated_path1, pagesize = (568.0, 1463.27), rightMargin=0, leftMargin=5,
#                                     topMargin=0, bottomMargin=0)
#             prepare_print_label(pharmacy_rx_data[0:14], pack_info, slot_data, patient_data, pharmacy_header,
#                                 pharmacy_details, doc, time_details, pack_display_id, True, system_id)
#
#             # send_to_printer(generated_path1)
#             path.append(os.path.abspath(generated_path1))
#             doc = SimpleDocTemplate(generated_path2, pagesize=(568.0, 1463.27), rightMargin=5, leftMargin=5,
#                                     topMargin=0, bottomMargin=0)
#
#             prepare_print_label(pharmacy_rx_data[14:], pack_info, slot_data, patient_data, pharmacy_header, pharmacy_details,
#                                 doc, time_details, pack_display_id, True, system_id, True)
#             # send_to_printer(generated_path2)
#             path.append(os.path.abspath(generated_path2))
#
#         logger.info("Pack label generated successfully for PackID: " + str(pack_id))
#         file_upload_status_list = list()
#         for file in label_files:
#             status, _ = upload_pack_label(file, file_names[label_files.index(file)])
#             logger.info('Status {} for file {}'.format(status, file))
#             file_upload_status_list.append(status)
#         if not all(file_upload_status_list):
#             raise Exception('Pack label(s) not uploaded to central storage')
#         msg = {"error": "none", "status": label_config.SUCCESS, "data": path, 'file_list': file_names}
#         return msg
#     except Exception as ex:
#         logger.error('Error while generating label for PackID: ' + str(pack_id) + str(ex), exc_info=True)
#         msg = {"error": str(ex), "status": label_config.FAILURE, "data": path, 'file_list': []}
#         return msg
#     finally:
#         remove_files(label_files)


def print_label(dict_label_info, canister_based_manual=False):
    """
        @function: prepare_print_data
        @createdBy: Manish Agarwal
        @createdDate: 09/23/2015
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 09/23/2015
        @type: function
        @param: int
        @purpose - Construct patient header from the given pateint details
        @input -
            type: (dict)

        @output -

    """
    label_files = []
    try:
        pack_id = dict_label_info["pack_id"]
        pack_display_id = dict_label_info["pack_display_id"]
        patient_id = dict_label_info["patient_id"]
        system_id = dict_label_info["system_id"]
        label_dir = os.path.join('pack_labels', 'generated', str(system_id))
        patient_image_dir = os.path.join('patient_images', str(system_id))
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)
        if not os.path.exists(patient_image_dir):
            os.makedirs(patient_image_dir)
        label_generator = pack_label.PackLabelGenerator(pack_id, patient_id, system_id, pack_display_id,
                                                        label_dir, 'drug_images', patient_image_dir)
        res = label_generator.print_label(canister_based_manual=canister_based_manual)
        file_upload_status_list = []
        if res["file_list"]:
            for file in res["file_list"]:
                file_path = os.path.join(label_dir, file)
                label_files.append(file_path)
                status, _ = upload_pack_label(file_path, file)
                logger.info('Status {} for file {}'.format(status, file))
                file_upload_status_list.append(status)
            if not all(file_upload_status_list):
                raise Exception('Pack label(s) not uploaded to central storage')
        return res
    except Exception as ex:
        logger.error(ex, exc_info=True)
        return {"error": str(ex), "status": label_config.FAILURE, "data": label_files, 'file_list': []}
    finally:
        remove_files(label_files)


@retry(3)
def upload_pack_label(file, file_name):
    """
    Uploads pack label to global storage
    - returns True, True if uploaded
    - returns False, False if not uploaded

    :param file:
    :param file_name:
    :return: bool, bool
    """
    try:
        create_blob(file, file_name, label_blob_dir)
        return True, True  # file uploaded successfully, first True as status for retry decorator
    except Exception as e:
        logger.error(e, exc_info=True)
        return False, False


def remove_files(files):
    """
    Removes files if present

    :param files:
    :return:
    """
    for f in files:
        try:
            os.remove(f)
        except (OSError, IOError) as e:
            logger.error(e, exc_info=True)


def get_patient_image(system_id, patient_name, batchid):
    """
    Downloads the patient image from IPS.
    """
    system_setting = get_system_setting_by_system_id(system_id=system_id)
    # 2. construct download url and download the file
    try:
        download_url = label_config.IPS_CONN_SCHEME + system_setting["BASE_URL_IPS"] + label_config.PATIENT_PIC_WEBSERVICE + '?batchid=' + str(
            batchid) \
                       + '&token=' + system_setting["IPS_COMM_TOKEN"]

        save_to_path = os.path.join('patient_images', str(system_id), patient_name)
        root_dir = os.path.join('patient_images', str(system_id))
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)

        print("** Downloading file ::", patient_name, "from url ::", download_url)
        headers = {'Authorization': system_setting["IPS_COMM_TOKEN"]}
        req = urllib.request.Request(download_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            # logger.debug("Response for getpatientimage: " + str(response.read()))
            file_data = json.loads(response.read().decode('utf-8').encode('unicode_escape'))
            if not is_response_valid(file_data):
                return False  # If response if NOT OK return false as file won't be saved properly
            file_data = base64.b64decode(file_data['response']['data'])
            if not file_data:
                logger.info("No Patient Image Found", exc_info=True)
                return False
            # save the file to the specified path
            try:
                with open(save_to_path, 'wb') as fp:
                    fp.write(file_data)
                    print("File saved at ::", save_to_path)
                    return True
            except IsADirectoryError:
                logger.info("No Patient Image Found", exc_info=True)
                return False

    except urllib.error.HTTPError as ex:
        logger.error(ex, exc_info=True)
        print("Failed to download file .....", str(ex))
        return False
    except Exception as ex:
        logger.error(ex, exc_info=True)
        print('Exception while saving file for batchid: ', str(batchid))
        return False


# this function is not required on linux.
# def send_to_printer(path):
#     printer = label_config.ROBOT6PRINTER
#     # This is where you would specify the path to your pdf
#     pdf = path
#
#     # Dynamically get path to AcroRD32.exe
#     AcroRD32Path = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, 'Software\\Adobe\\Acrobat\Exe')
#
#     acroread = AcroRD32Path
#
#     # The last set of double quotes leaves the printer blank, basically defaulting
#     # to the default printer for the system.
#     cmd = '{0} /N /T "{1}" "{2}"'.format(acroread, pdf, printer)
#
#     # See what the command line will look like before execution
#     logger.info(cmd)
#
#     # Open command line in a different process other than ArcMap
#     proc = subprocess.Popen(cmd)
#
#     import time
#     time.sleep(15)
#
#     # Kill AcroRD32.exe from Task Manager
#     os.system("TASKKILL /F /IM AcroRD32.exe")




