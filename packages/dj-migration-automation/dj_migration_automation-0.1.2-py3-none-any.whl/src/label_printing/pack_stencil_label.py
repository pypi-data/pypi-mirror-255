import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import settings
from src.label_printing.utils import get_barcode

logger = settings.logger

pst_dir = os.path.join('pst_labels')  # pack stencils labels directory


def generate_stencil_label(file_name, stencil_id, seq_no, width=2.25, height=1.25,
                           barcode_position=(0, 50), seq_no_position=40, id_position=25):
    """
    Generates label for stencil
    :param file_name:
    :param stencil_id:
    :param seq_no:
    :param width: width of pdf in inch
    :param height: height of pdf in inch
    :param barcode_position: (tuple) (x, y)
    :param seq_no_position: (int) position for y axis, x will adjusted to center
    :param id_position: (int) position for y axis, x will adjusted to center
    :return:
    """
    font_name = 'tahoma'
    font_size = 8
    pdfmetrics.registerFont(TTFont(font_name, 'tahomabd.ttf'))
    page_size = (width * 72, height * 72)  # 2.25 inch * 1.25 inch (w*h)
    can = canvas.Canvas(file_name, pagesize=page_size)
    can.setFont(font_name, font_size)

    barcode = get_barcode(value=seq_no, width=150)

    label_width = page_size[0]
    # x = 10  # start of x axis cursor
    # y = 18  # start of y axis cursor
    barcode.hAlign = 'CENTER'
    barcode.drawOn(can, barcode_position[0], barcode_position[1], _sW=(label_width - barcode.width))

    text_width = pdfmetrics.stringWidth(seq_no, fontName=font_name, fontSize=font_size)
    can.drawString(((label_width - text_width) / 2.0), seq_no_position, seq_no)

    stencil_id = 'ID: {}'.format(stencil_id)
    font_size = 10
    can.setFont(font_name, font_size)
    text_width = pdfmetrics.stringWidth(stencil_id, fontName=font_name, fontSize=font_size)
    can.drawString(((label_width - text_width) / 2.0), id_position, stencil_id)

    # can.drawString(0, 0, '.')  # Left Bottom
    # can.drawString(0, 88, '.')  # Left Top
    # can.drawString(160, 88, '.')  # Right Top
    # can.drawString(160, 0, '.')  # Right Bottom

    can.save()  # save file
