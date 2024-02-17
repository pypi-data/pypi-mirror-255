"""
    This module contains util functions required to generate different labels.
"""
import json

import settings
from dosepack.error_handling.error_handler import create_response, error
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from pystrich.datamatrix import DataMatrixEncoder
from PIL import Image

from dosepack.utilities.utils import get_gtin_from_ndc
from src.service.misc import update_rfid_in_couchdb
logger = settings.logger



def get_barcode(value, width, barWidth=0.2*inch, fontSize=30, humanReadable=False):
    """
    Returns drawing of barcode

    :param value:
    :param width:
    :param barWidth:
    :param fontSize:
    :param humanReadable:
    :return: Drawing
    """
    barcode = createBarcodeDrawing('Code128', value=value, barWidth=barWidth, fontSize=fontSize,
                                   humanReadable=humanReadable)

    drawing_width = width
    barcode_scale = drawing_width / barcode.width
    drawing_height = barcode.height * barcode_scale

    drawing = Drawing(drawing_width, drawing_height)
    drawing.scale(barcode_scale, barcode_scale)
    drawing.add(barcode, name='barcode')

    return drawing

def get_datamatrix(ndc, lot_number, expiry_number, sr_no, file_name, height=45, width=45):
    """
    This function will be used to get a pdf of data matrix based on the given information
    ndc will be converted to GTIN and then data matrix format will be used to get the data matrix
    :param ndc:
    :param lot_number:
    :param expiry_number:
    :param sr_no:
    :param file_name:
    :param height:
    :param width:
    :return:
    """
    try:
        gtin_value = get_gtin_from_ndc(ndc_value=ndc)
        FNC1 = chr(29)

        if len(sr_no) != 20:
            sr_no = sr_no + FNC1

        # Formation of string: GS (01)[Prefix of GTIN]{GTIN/NDC} (21)[Prefix of Serial Number]{ Serial Number} \
        #                      GS (17)[Prefix of Expiry Date]{Expiry Date} (10)[Prefix of lot no] {Lot No}
        value_for_matrix = str(FNC1) + "01" + gtin_value + "21" + sr_no + "17" + expiry_number + "10" + lot_number

        encoder = DataMatrixEncoder(value_for_matrix)
        encoder.save(file_name)

        f1 = Image.open(file_name)
        f2 = f1.resize((height, width), Image.ANTIALIAS)
        f2.save(file_name)

        return True
    except Exception as e:
        print ("Exception in data matrix: ", e)
        return False


def api_callback(args):
    try:
        # args = '{\"status\":\"success\",\"station_type\":\"56000\",\"station_id\":\"56001\",\"msg_id\":\"0\",\"resp_code\":\"11101\",\"data\":{\"5\":\"123654\"}}'
        callback_data = json.loads(args)
    except:
        try:
            callback_data = eval(args)
        except:
            logger.error(1001, "api_callback - Exception: ")
            return create_response(False)

    response = update_rfid_in_couchdb(callback_data)
    if response:
        return create_response(response)
    else:
        return error(1000, "Unable to update data in couch db.")