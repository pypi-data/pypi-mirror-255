import os
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
import settings
from dosepack.utilities.utils import fn_shorten_drugname

logger = settings.logger

pack_error_dir = os.path.join('pack_error_labels')


def generate_pack_error_label(file_name, drug_name, ndc, strength, strength_value, imprint, source):
    """
    Generates pdf for error label with drug_name, strength, NDC, Imprint and Source

    :param file_name:
    :param drug_name:
    :param ndc:
    :param strength:
    :param strength_value:
    :param imprint:
    :param source:
    :return: None
    """
    font_name = 'tahoma'
    font_size = 8
    pdfmetrics.registerFont(TTFont(font_name, 'tahomabd.ttf'))
    page_size = (2.25 * 72, 1.25 * 72)  # 2.25 inch * 1.25 inch (w*h)
    can = canvas.Canvas(file_name, pagesize=page_size)
    can.setFont(font_name, font_size)

    if len(drug_name) > 25:  # shorten drug name if length is longer than 25
        drug_name = fn_shorten_drugname(drug_name)
    drug_strength = strength_value + ' ' + strength

    label_width = page_size[0]
    # x = 10  # start of x axis cursor
    y = 22  # start of y axis cursor

    text_width = pdfmetrics.stringWidth(drug_name, fontName=font_name, fontSize=font_size)
    centered_x = ((label_width - text_width) / 2.0)
    can.drawString(centered_x, y + 40, drug_name)

    text_width = pdfmetrics.stringWidth(drug_strength, fontName=font_name, fontSize=font_size)
    centered_x = ((label_width - text_width) / 2.0)
    can.drawString(centered_x, y + 30, drug_strength)

    ndc = 'NDC: ' + ndc
    text_width = pdfmetrics.stringWidth(ndc, fontName=font_name, fontSize=font_size)
    centered_x = ((label_width - text_width) / 2.0)
    can.drawString(centered_x, y + 20, ndc)

    imprint = 'Imprint: ' + imprint
    text_width = pdfmetrics.stringWidth(imprint, fontName=font_name, fontSize=font_size)
    centered_x = ((label_width - text_width) / 2.0)
    can.drawString(centered_x, y + 10, imprint)

    source = 'Source: ' + source
    text_width = pdfmetrics.stringWidth(source, fontName=font_name, fontSize=font_size)
    centered_x = ((label_width - text_width) / 2.0)
    can.drawString(centered_x, y, source)
    # can.drawString(0, 0, '.')  # Left Bottom
    # can.drawString(0, 88, '.')  # Left Top
    # can.drawString(160, 88, '.')  # Right Top
    # can.drawString(160, 0, '.')  # Right Bottom

    can.save()  # save file