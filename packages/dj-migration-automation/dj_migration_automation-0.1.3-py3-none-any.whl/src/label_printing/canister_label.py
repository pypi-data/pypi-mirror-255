import os

import settings
from dosepack.utilities.utils import fn_shorten_drugname, log_args_and_response
from src import constants
from src.label_printing.utils import get_barcode
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

logger = settings.logger

canister_dir = os.path.join('canister_labels')
mfd_canister_dir = os.path.join("mfd_canister_labels")
expired_drug_label_dir = os.path.join('expired_drug_labels')


def draw_dosepack_logo(canvas):
    """
    Sets dosepack logo to the given canvas at top left for canister label
    :param canvas:
    :return: None
    """
    dosepack_icon = os.path.join('static', 'dosepacker-icon-black.png')
    canvas.drawImage(dosepack_icon, 6, 67, 0.25 * 72, 0.25 * 72, mask='auto')


@log_args_and_response
def generate_canister_label(file_name, drug_name, ndc, strength, strength_value, canister_id,
                            manufacturer, imprint, color, shape, form, canister_version=None,
                            drug_shape_name=None, big_canister_stick_id=None, small_canister_stick_id=None,
                            product_id=None, big_stick_serial_number=None, small_stick_serial_number=None,
                            lower_level=None, drum_serial_number=None, company_id=None):
    """
    Generates canister label pdf

    :param file_name:
    :param drug_name:
    :param ndc:
    :param strength:
    :param strength_value:
    :param canister_id:
    :param imprint:
    :param color:
    :param manufacturer:
    :param shape:
    :param form:
    :param canister_version:
    :param drug_shape_name:
    :param big_canister_stick_id:
    :param small_canister_stick_id:
    :param product_id:
    :param big_stick_serial_number:
    :param small_stick_serial_number:
    :param lower_level:
    :param drum_serial_number:
    :return:
    """
    canister = dict()
    canister['drug_name'] = drug_name
    canister['ndc'] = ndc
    canister['strength'] = strength
    canister['strength_value'] = strength_value
    canister['canister_id'] = canister_id
    canister['manufacturer'] = manufacturer
    canister['imprint'] = imprint
    canister['color'] = color
    canister['shape'] = shape
    canister['drug_form'] = form
    canister['drug_shape_name'] = drug_shape_name
    canister['big_canister_stick_id'] = big_canister_stick_id
    canister['small_canister_stick_id'] = small_canister_stick_id
    canister['product_id'] = product_id
    canister['big_stick_serial_number'] = big_stick_serial_number
    canister['small_stick_serial_number'] = small_stick_serial_number
    canister['lower_level'] = lower_level
    canister['drum_serial_number'] = drum_serial_number
    canister['company_id'] = company_id
    canister_data_list = [canister]

    if canister_version == "v2":
        generate_canister_label_v2(file_name=file_name, canister_data_list=canister_data_list)
    else:
        generate_canister_label_v3(file_name=file_name, canister_data_list=canister_data_list)


@log_args_and_response
def generate_expired_drug_label(file_name, expired_drug_dicts):
    try:
        page_size = (2.25 * 72, 1.25 * 72)

        can = canvas.Canvas(file_name, pagesize=page_size)
        for expired_drug_dict in expired_drug_dicts:
            drug_name = expired_drug_dict.get("drug_name")
            ndc = 'NDC: ' + str(expired_drug_dict.get("ndc"))
            lot_no = 'lot no.: ' + str(expired_drug_dict.get("lot_number"))
            manufacturer = 'manufacturer: ' + str(expired_drug_dict.get("manufacturer"))
            approx_disposed_quantity = "approx disposed quantity: " + str(expired_drug_dict.get("trashed_qty"))
            expiry_date = 'expiry date: ' + str(expired_drug_dict.get("expiration_date"))

            file_name = file_name

            font_name = 'tahoma'
            drug_font_size = 8
            ndc_font_size = 7
            last_layer_font_size = 6
            margin_between_two_words = 3
            pdfmetrics.registerFont(TTFont(font_name, 'tahomabd.ttf'))
            page_size = (2.25 * 72, 1.25 * 72)
            PAGE_WIDTH = (2.25 * 72)  # 2.25 inch * 1.25 inch (w*h)

            # can = canvas.Canvas(file_name, pagesize=page_size)

            draw_dosepack_logo(can)

            label_width = page_size[0]
            y = 17  # start of y axis cursor
            drug_name_width = pdfmetrics.stringWidth(drug_name, fontName=font_name, fontSize=drug_font_size)
            can.setFont(font_name, drug_font_size)
            can.drawString((PAGE_WIDTH - drug_name_width) / 2.0, y + 38, drug_name)

            can.setFont(font_name, ndc_font_size)
            ndc_size = pdfmetrics.stringWidth(ndc, fontName=font_name, fontSize=ndc_font_size)
            can.drawString((PAGE_WIDTH - ndc_size) / 2.0, y + 20, ndc)

            lot_no_size = pdfmetrics.stringWidth(lot_no, fontName=font_name, fontSize=ndc_font_size)
            can.drawString((PAGE_WIDTH - lot_no_size) / 2.0, y + 28, lot_no)

            date_size = pdfmetrics.stringWidth(expiry_date, fontName=font_name, fontSize=ndc_font_size)
            can.drawString((PAGE_WIDTH - date_size) / 2.0, y + 12, expiry_date)

            qty_size = pdfmetrics.stringWidth(approx_disposed_quantity, fontName=font_name, fontSize=ndc_font_size)
            can.drawString((PAGE_WIDTH - qty_size) / 2.0, y + 4, approx_disposed_quantity)

            manufacturer_size = pdfmetrics.stringWidth(manufacturer, fontName=font_name, fontSize=ndc_font_size)
            can.drawString((PAGE_WIDTH - manufacturer_size) / 2.0, y - 4, manufacturer)
            can.showPage()
        can.save()
        return True
    except Exception as e:
        print(f"error in generate_expired_drug_label:{e}")
        raise e


@log_args_and_response
def generate_canister_label_v2(file_name, canister_data_list):
    """
    Generates canister label pdf

    :param file_name:
    :param canister_data_list:
    :return:
    """
    canister_barcode_dict = dict()

    font_name = 'tahoma'
    drug_font_size = 8
    ndc_font_size = 7
    last_layer_font_size = 6
    margin_between_two_words = 3
    pdfmetrics.registerFont(TTFont(font_name, 'tahomabd.ttf'))
    page_size = (2.25 * 72, 1.25 * 72)  # 2.25 inch * 1.25 inch (w*h)
    can = canvas.Canvas(file_name, pagesize=page_size)

    for canister in canister_data_list:
        barcode = get_barcode(value=str(canister["canister_id"]), width=150)
        canister_barcode_dict[canister["canister_id"]] = barcode

    for canister in canister_data_list:
        draw_dosepack_logo(can)
        can.setFont(font_name, ndc_font_size)
        drug_imprint = ''
        drug_color = ''
        drug_shape = ''
        drug_form = ''
        manufacturer = ''
        if len(canister["drug_name"]) > 25:  # shorten drug name if length is longer than 25
            drug_name = fn_shorten_drugname(canister["drug_name"])
        else:
            drug_name = canister["drug_name"]

        drug_strength = canister["strength_value"] + ' ' + canister["strength"]

        label_width = page_size[0]
        y = 17  # start of y axis cursor
        barcode_to_use = canister_barcode_dict[canister["canister_id"]]
        barcode_to_use.hAlign = 'RIGHT'
        barcode_to_use.drawOn(can, (label_width - barcode_to_use.width), y + 54,
                              _sW=(label_width - barcode_to_use.width))

        can.setFont(font_name, drug_font_size)

        drug_name_width = pdfmetrics.stringWidth(drug_name, fontName=font_name, fontSize=drug_font_size)
        drug_strength_width = pdfmetrics.stringWidth(drug_strength, fontName=font_name, fontSize=drug_font_size)
        drug_name_is_short = False
        if (drug_name_width + margin_between_two_words + drug_strength_width) < 160:
            drug_name_is_short = True
        if drug_name_is_short:
            can.drawString(0, y + 42, drug_name)
            can.drawString((drug_name_width + margin_between_two_words), y + 42, drug_strength)
        else:
            can.drawString(0, y + 42, drug_name)
            can.drawString(0, y + 30, drug_strength)

        canister_id = 'ID: ' + str(canister["canister_id"])
        canister_id_width = pdfmetrics.stringWidth(canister_id, fontName=font_name, fontSize=drug_font_size)
        if canister['manufacturer']:
            manufacturer = canister['manufacturer']
        manufacturer_width = pdfmetrics.stringWidth(manufacturer, fontName=font_name, fontSize=drug_font_size)
        can.drawString(0, y + 18, canister_id)
        can.drawString((label_width - manufacturer_width), y + 18, manufacturer)

        can.setFont(font_name, ndc_font_size)

        ndc = 'NDC: ' + canister["ndc"]
        ndc_size = pdfmetrics.stringWidth(ndc, fontName=font_name, fontSize=ndc_font_size)
        can.drawString(0, y + 6, ndc)

        #  Color, shape, imprint starts.

        can.setFont(font_name, last_layer_font_size)

        if canister["imprint"]:
            drug_imprint = canister["imprint"]
        imprint_size = pdfmetrics.stringWidth(drug_imprint, fontName=font_name, fontSize=last_layer_font_size)

        if canister["color"]:
            drug_color = canister["color"]
        drug_color_size = pdfmetrics.stringWidth(drug_color, fontName=font_name, fontSize=last_layer_font_size)

        if canister["shape"]:
            drug_shape = canister["shape"]
        shape_size = pdfmetrics.stringWidth(drug_shape, fontName=font_name, fontSize=last_layer_font_size)

        if canister["drug_form"]:
            drug_form = canister["drug_form"]
        drug_form_size = pdfmetrics.stringWidth(drug_form, fontName=font_name, fontSize=last_layer_font_size)

        show_in_one_line = False
        if (imprint_size + drug_color_size + shape_size + drug_form_size + margin_between_two_words) < 160:
            show_in_one_line = True

        combined_list = [(drug_imprint, imprint_size), (drug_color, drug_color_size), (drug_shape, shape_size),
                         (drug_form, drug_form_size)]
        if show_in_one_line:
            non_empty_combined_list = []
            for (property_value, size) in combined_list:
                if len(property_value) > 0:
                    non_empty_combined_list.append(property_value)
            combined_string = ', '.join(non_empty_combined_list)
            can.drawString(0, y - 6, combined_string)
        else:
            first_row_list = []
            second_row_list = []
            width_occupied = 0
            first_row_full = False
            for (property_value, size) in combined_list:
                if len(property_value) > 0:
                    if width_occupied + size < 160 and first_row_full is False:
                        first_row_list.append(property_value)
                        width_occupied += size
                    else:
                        first_row_full = True
                        second_row_list.append(property_value)
            if second_row_list:
                first_row_list.append('')
            combined_first_string = ', '.join(first_row_list)
            can.drawString(0, y - 6, combined_first_string)

            combined_second_string = ', '.join(second_row_list)
            can.drawString(0, y - 15, combined_second_string)

        can.showPage()

    can.save()  # save file


@log_args_and_response
def generate_canister_label_v3(file_name, canister_data_list):
    """
    Generates canister label pdf

    :param file_name:
    :param canister_data_list:
    :return:
    """
    try:
        canister_barcode_dict = dict()

        font_name = 'Helvetica-Bold'  # 'Times-Bold'
        drug_font_size = 9  # 7
        canister_id_size = 10  # 7
        product_id_font_size = 6  # 3
        stick_font_size = 6  # 3
        ndc_font_size = 7  # 5
        manufracture_size = 6  # 5
        last_layer_font_size = 6  # 5
        margin_between_two_words = 3
        # pdfmetrics.registerFont(TTFont(font_name, 'TIMESROMAN.ttf'))
        page_size = (2.25 * 72, 1.25 * 72)  # 2.25 inch * 1.25 inch (w*h)
        PAGE_WIDTH = (2.25 * 72)
        logger.info(file_name)
        can = canvas.Canvas(file_name, pagesize=page_size)
        drug_shapes_list = ["capsule", "elliptical", "oval", "round_curved", "round_flat", "other", "oblong"]

        for canister in canister_data_list:
            qr_data = constants.CANISTER_LABEL_PREFIX + "-" + str(canister["canister_id"]) + "-" + str(canister["company_id"])
            qrw = QrCodeWidget(qr_data)
            b = qrw.getBounds()

            w = b[2] - b[0]
            h = b[3] - b[1]

            d = Drawing(35, 35, transform=[35. / w, 0, 0, 35. / h, 0, 0])
            d.add(qrw)
            canister_barcode_dict[canister["canister_id"]] = d

        for canister in canister_data_list:
            draw_dosepack_logo(can)
            can.setFont(font_name, ndc_font_size)
            drug_shape_name = canister['drug_shape_name']
            drug_imprint = ''
            drug_color = ''
            drug_shape = ''
            drug_form = ''
            manufacturer = ''

            drug_strength = canister["strength_value"] + ' ' + canister["strength"]

            label_width = page_size[0]
            y = 9  # start of y axis cursor
            if canister['product_id']:
                product_id = "PROD. ID: {}".format(canister['product_id'])
            else:
                product_id = "PROD. ID: N.A"
            can.setFont(font_name, product_id_font_size)
            product_id_width = pdfmetrics.stringWidth(product_id, fontName=font_name, fontSize=product_id_font_size)
            product_id_x_axis = PAGE_WIDTH - product_id_width - 4
            x_axis_space = PAGE_WIDTH - 4
            can.drawString(product_id_x_axis, 80, product_id)

            barcode_to_use = canister_barcode_dict[canister["canister_id"]]
            barcode_to_use.hAlign = 'CENTER'
            # renderPDF.draw(barcode_to_use, can, (PAGE_WIDTH - barcode_to_use.width) / 2.0, y=55)

            renderPDF.draw(barcode_to_use, can, (PAGE_WIDTH - 35) / 2.0, y=55)

            can.setFont(font_name, drug_font_size)
            # canister id
            can.setFont(font_name, canister_id_size)
            canister_id = 'ID: ' + str(canister["canister_id"])
            id_width = stringWidth(canister_id, fontName=font_name, fontSize=drug_font_size)
            can.drawString((PAGE_WIDTH - id_width) / 2.0, y + 42, canister_id)

            # drug name
            can.setFont(font_name, drug_font_size)
            drug_name = canister["drug_name"]
            drug_name_width = pdfmetrics.stringWidth(drug_name, fontName=font_name, fontSize=drug_font_size)
            drug_strength_width = pdfmetrics.stringWidth(drug_strength, fontName=font_name, fontSize=drug_font_size)
            center_drug_name = (PAGE_WIDTH - drug_name_width + margin_between_two_words + drug_strength_width) / 2.0
            # center_drug_name = 63
            space_left = (x_axis_space - center_drug_name)

            if (drug_name_width + drug_strength_width) > space_left or center_drug_name <= 0:  # shorten drug name if length is longer than 25
                drug_name = fn_shorten_drugname(canister["drug_name"])
                drug_name_width = pdfmetrics.stringWidth(drug_name, fontName=font_name, fontSize=drug_font_size)

            else:
                drug_name = canister["drug_name"]

            if (drug_name_width + margin_between_two_words + drug_strength_width) <= space_left:
                drug_name_strength = drug_name + " " + drug_strength
                can.drawString((PAGE_WIDTH - (drug_name_width + margin_between_two_words + drug_strength_width)) / 2.0,
                               y + 32, drug_name_strength)
                # can.drawString((drug_name_width + margin_between_two_words), y + 42, drug_strength)

            # elif drug_name_width < space_left:
            #     drug_name_strength = drug_name + "   " + drug_strength
            #     can.drawString((PAGE_WIDTH - (drug_name_width + margin_between_two_words + drug_strength_width)) / 2.0,
            #                    y + 32, drug_name_strength)
            #     can.drawString((PAGE_WIDTH - drug_name_width) / 2.0, y + 32, drug_name)
            #     can.drawString((PAGE_WIDTH - drug_strength_width) / 2.0, y + 24, str(drug_strength))

            else:
                can.drawString((PAGE_WIDTH - drug_name_width) / 2.0, y + 32, drug_name)
                can.drawString((PAGE_WIDTH - drug_strength_width) / 2.0, y + 23, str(drug_strength))

            # ndc
            can.setFont(font_name, ndc_font_size)

            ndc = 'NDC: ' + canister["ndc"]
            ndc_size = pdfmetrics.stringWidth(ndc, fontName=font_name, fontSize=ndc_font_size)
            can.drawString((PAGE_WIDTH - ndc_size) / 2.0, y + 14, ndc)

            # manufacturer
            can.setFont(font_name, manufracture_size)
            manufacturer_width = 0
            if canister['manufacturer']:
                manufacturer = canister['manufacturer']
                manufacturer_width = pdfmetrics.stringWidth(manufacturer, fontName=font_name,
                                                            fontSize=manufracture_size)
                can.drawString((PAGE_WIDTH - manufacturer_width) / 2.0, y + 8, manufacturer)

            # drug_shape image
            drug_shape_name = str(drug_shape_name).lower()
            if " " in drug_shape_name:
                drug_shape_data = drug_shape_name.split()
                drug_shape_name = str(drug_shape_data[0]) + "_" + str(drug_shape_data[1])
            if drug_shape_name in drug_shapes_list:
                drug_shape_image = os.path.join('static', drug_shape_name + '.png')
                x_axis = max(ndc_size, manufacturer_width) + 20
                can.drawImage(drug_shape_image, (PAGE_WIDTH - x_axis) / 2.0, y + 8, 7, 7, preserveAspectRatio=True)

            else:
                drug_shape_image = os.path.join('static', "other" + '.png')
                x_axis = max(ndc_size, manufacturer_width) + 20
                can.drawImage(drug_shape_image, (PAGE_WIDTH - x_axis) / 2.0, y + 8, 8, 7, preserveAspectRatio=True)

            #  Color, shape, imprint starts.

            can.setFont(font_name, last_layer_font_size)

            if canister["imprint"]:
                drug_imprint = str(canister["imprint"]).upper()
            imprint_size = pdfmetrics.stringWidth(drug_imprint, fontName=font_name, fontSize=last_layer_font_size)

            if canister["color"]:
                drug_color = str(canister["color"]).upper()
            drug_color_size = pdfmetrics.stringWidth(drug_color, fontName=font_name, fontSize=last_layer_font_size)

            if canister["drug_shape_name"]:
                drug_shape = str(canister["shape"]).upper()
            elif canister["drug_shape_name"] == "other":
                drug_shape = "Other Shape"
            else:
                drug_shape = "Other Shape"
            shape_size = pdfmetrics.stringWidth(drug_shape, fontName=font_name, fontSize=last_layer_font_size)

            if canister["drug_form"]:
                drug_form = str(canister["drug_form"]).upper()
            drug_form_size = pdfmetrics.stringWidth(drug_form, fontName=font_name, fontSize=last_layer_font_size)

            show_in_one_line = False
            if (imprint_size + drug_color_size + shape_size + drug_form_size + margin_between_two_words) < 95:
                show_in_one_line = True

            combined_list = [(drug_imprint, imprint_size), (drug_color, drug_color_size), (drug_shape, shape_size),
                             (drug_form, drug_form_size)]
            if show_in_one_line:
                non_empty_combined_list = []
                for (property_value, size) in combined_list:

                    if len(property_value) > 0:
                        non_empty_combined_list.append(property_value)
                combined_string = ', '.join(non_empty_combined_list)
                total_line_size = pdfmetrics.stringWidth(combined_string, fontName=font_name,
                                                         fontSize=last_layer_font_size)
                can.drawString((PAGE_WIDTH - total_line_size) / 2.0, y + 1, combined_string)
            else:
                first_row_list = []
                second_row_list = []
                width_occupied = 0
                second_line_width = 0
                first_row_empty = True
                first_row_full = False
                for (property_value, size) in combined_list:
                    if len(property_value) > 0:
                        if width_occupied + size < 95 and first_row_full is False:
                            first_row_empty = False
                            first_row_list.append(property_value)
                            width_occupied += size

                        elif first_row_empty and width_occupied + size < 100:
                            first_row_empty = False
                            first_row_list.append(property_value)
                            width_occupied += size
                        else:
                            first_row_full = True
                            second_row_list.append(property_value)
                            second_line_width += size
                if second_row_list:
                    first_row_list.append('')
                combined_first_string = ', '.join(first_row_list)
                can.drawString((PAGE_WIDTH - width_occupied) / 2.0, y + 1, combined_first_string)

                combined_second_string = ', '.join(second_row_list)
                can.drawString((PAGE_WIDTH - second_line_width) / 2.0, y - 6, combined_second_string)

            #  corners stick data and lower level
            can.setFont(font_name, stick_font_size)
            if canister['lower_level']:
                ll_image = os.path.join('static', 'LL.png')
                can.drawImage(ll_image, (PAGE_WIDTH - 9), y - 7, 10, 11, mask='auto')

            can.rotate(90)
            if canister['small_stick_serial_number']:
                can.drawString(33, - 13, " SS: {} ".format(canister['small_stick_serial_number']))
            if canister['big_stick_serial_number']:
                can.drawString(4, -13, "BS: {} ".format(canister['big_stick_serial_number']))
            if canister['drum_serial_number']:
                can.drawString(4, -13, "DRUM: {} ".format(canister['drum_serial_number']))

            can.showPage()
            can = generate_canister_top_label(canister_data_list, can, drug_name)
            can.showPage()
        can.save()
    except Exception as e:
        logger.info("Error in generating canister label {}".format(e))
        return e


def generate_canister_top_label(canister_data_list, can, drug_name_label):
    font_name = 'Helvetica-Bold'  # 'Times-Bold'
    drug_font_size = 10  # 7
    canister_id_size = 10  # 7
    product_id_font_size = 6  # 3
    stick_font_size = 6  # 3
    ndc_font_size = 7  # 5
    manufracture_size = 6  # 5
    last_layer_font_size = 6  # 5
    margin_between_two_words = 3
    # pdfmetrics.registerFont(TTFont(font_name, 'TIMESROMAN.ttf'))
    page_size = (2.25 * 72, 1.25 * 72)  # 2.25 inch * 1.25 inch (w*h)
    PAGE_WIDTH = (2.25 * 72)
    # can = canvas.Canvas(file_name, pagesize=page_size)
    drug_shapes_list = ["capsule", "elliptical", "oval", "round_curved", "round_flat", "other", "oblong"]

    for canister in canister_data_list:
        draw_dosepack_logo(can)
        can.setFont(font_name, ndc_font_size)
        drug_shape_name = canister['drug_shape_name']
        drug_imprint = ''
        drug_color = ''
        drug_shape = ''
        drug_form = ''
        manufacturer = ''

        drug_strength = canister["strength_value"] + ' ' + canister["strength"]

        label_width = page_size[0]
        y = 9  # start of y axis cursor
        if canister['product_id']:
            product_id = "PROD. ID: {}".format(canister['product_id'])
        else:
            product_id = "PROD. ID: N.A"
        can.setFont(font_name, product_id_font_size)
        x_axis_space = PAGE_WIDTH - 6
        product_id_width = pdfmetrics.stringWidth(product_id, fontName=font_name, fontSize=product_id_font_size)
        product_id_x_axis = PAGE_WIDTH - product_id_width - 4
        can.drawString(product_id_x_axis, 81, product_id)

        can.setFont(font_name, drug_font_size)
        # canister id
        can.setFont(font_name, canister_id_size)
        canister_id = 'ID: ' + str(canister["canister_id"])
        id_width = stringWidth(canister_id, fontName=font_name, fontSize=drug_font_size)
        can.drawString((PAGE_WIDTH - id_width) / 2.0, y + 52, canister_id)

        # drug name
        can.setFont(font_name, drug_font_size)
        drug_name = drug_name_label
        drug_name_width = pdfmetrics.stringWidth(drug_name, fontName=font_name, fontSize=drug_font_size)
        drug_strength_width = pdfmetrics.stringWidth(drug_strength, fontName=font_name, fontSize=drug_font_size)
        center_drug_name = (PAGE_WIDTH - (drug_name_width + margin_between_two_words + drug_strength_width)) / 2.0

        space_left = (x_axis_space - abs(center_drug_name))

        if (drug_name_width + drug_strength_width) > space_left or center_drug_name <= 0:  # shorten drug name if length is longer than 25
            drug_name = fn_shorten_drugname(drug_name)
            drug_name_width = pdfmetrics.stringWidth(drug_name, fontName=font_name, fontSize=drug_font_size)

        else:
            drug_name = drug_name

        if (drug_name_width + margin_between_two_words + drug_strength_width) <= space_left:
            drug_name_strength = drug_name + " " + drug_strength
            can.drawString((PAGE_WIDTH - (drug_name_width + margin_between_two_words + drug_strength_width)) / 2.0,
                           y + 42, drug_name_strength)
            # can.drawString((drug_name_width + margin_between_two_words), y + 42, drug_strength)

        # elif drug_name_width < space_left:
        #     drug_name_strength = drug_name + "   " + drug_strength
        #     can.drawString((PAGE_WIDTH - (drug_name_width + margin_between_two_words + drug_strength_width)) / 2.0,
        #                    y + 32, drug_name_strength)
        #     can.drawString((PAGE_WIDTH - drug_name_width) / 2.0, y + 32, drug_name)
        #     can.drawString((PAGE_WIDTH - drug_strength_width) / 2.0, y + 24, str(drug_strength))

        else:
            can.drawString((PAGE_WIDTH - drug_name_width) / 2.0, y + 42, drug_name)
            can.drawString((PAGE_WIDTH - drug_strength_width) / 2.0, y + 33, str(drug_strength))

        # ndc
        can.setFont(font_name, ndc_font_size)

        ndc = 'NDC: ' + canister["ndc"]
        ndc_size = pdfmetrics.stringWidth(ndc, fontName=font_name, fontSize=ndc_font_size)
        can.drawString((PAGE_WIDTH - ndc_size) / 2.0, y + 24, ndc)

        # manufacturer
        can.setFont(font_name, manufracture_size)
        manufacturer_width = 0
        if canister['manufacturer']:
            manufacturer = canister['manufacturer']
            manufacturer_width = pdfmetrics.stringWidth(manufacturer, fontName=font_name,
                                                        fontSize=manufracture_size)
            can.drawString((PAGE_WIDTH - manufacturer_width) / 2.0, y + 18, manufacturer)

        # drug_shape image
        drug_shape_name = str(drug_shape_name).lower()
        if " " in drug_shape_name:
            drug_shape_data = drug_shape_name.split()
            drug_shape_name = str(drug_shape_data[0]) + "_" + str(drug_shape_data[1])
        if drug_shape_name in drug_shapes_list:
            drug_shape_image = os.path.join('static', drug_shape_name + '.png')
            x_axis = max(ndc_size, manufacturer_width) + 20
            can.drawImage(drug_shape_image, (PAGE_WIDTH - x_axis) / 2.0, y + 18, 7, 7, preserveAspectRatio=True)

        else:
            drug_shape_image = os.path.join('static', "other" + '.png')
            x_axis = max(ndc_size, manufacturer_width) + 20
            can.drawImage(drug_shape_image, (PAGE_WIDTH - x_axis) / 2.0, y + 18, 8, 7, preserveAspectRatio=True)

        #  Color, shape, imprint starts.

        can.setFont(font_name, last_layer_font_size)

        if canister["imprint"]:
            drug_imprint = str(canister["imprint"]).upper()
        imprint_size = pdfmetrics.stringWidth(drug_imprint, fontName=font_name, fontSize=last_layer_font_size)

        if canister["color"]:
            drug_color = str(canister["color"]).upper()
        drug_color_size = pdfmetrics.stringWidth(drug_color, fontName=font_name, fontSize=last_layer_font_size)

        if canister["drug_shape_name"]:
            drug_shape = str(canister["shape"]).upper()
        elif canister["drug_shape_name"] == "other":
            drug_shape = "Other Shape"
        else:
            drug_shape = "Other Shape"
        shape_size = pdfmetrics.stringWidth(drug_shape, fontName=font_name, fontSize=last_layer_font_size)

        if canister["drug_form"]:
            drug_form = str(canister["drug_form"]).upper()
        drug_form_size = pdfmetrics.stringWidth(drug_form, fontName=font_name, fontSize=last_layer_font_size)

        show_in_one_line = False
        if (imprint_size + drug_color_size + shape_size + drug_form_size + margin_between_two_words) < 95:
            show_in_one_line = True

        combined_list = [(drug_imprint, imprint_size), (drug_color, drug_color_size), (drug_shape, shape_size),
                         (drug_form, drug_form_size)]
        if show_in_one_line:
            non_empty_combined_list = []
            for (property_value, size) in combined_list:

                if len(property_value) > 0:
                    non_empty_combined_list.append(property_value)
            combined_string = ', '.join(non_empty_combined_list)
            total_line_size = pdfmetrics.stringWidth(combined_string, fontName=font_name,
                                                     fontSize=last_layer_font_size)
            can.drawString((PAGE_WIDTH - total_line_size) / 2.0, y + 11, combined_string)
        else:
            first_row_list = []
            second_row_list = []
            width_occupied = 0
            second_line_width = 0
            first_row_empty = True
            first_row_full = False
            for (property_value, size) in combined_list:
                if len(property_value) > 0:
                    if width_occupied + size < 95 and first_row_full is False:
                        first_row_empty = False
                        first_row_list.append(property_value)
                        width_occupied += size

                    elif first_row_empty and width_occupied + size < 100:
                        first_row_empty = False
                        first_row_list.append(property_value)
                        width_occupied += size
                    else:
                        first_row_full = True
                        second_row_list.append(property_value)
                        second_line_width += size
            if second_row_list:
                first_row_list.append('')
            combined_first_string = ', '.join(first_row_list)
            can.drawString((PAGE_WIDTH - width_occupied) / 2.0, y + 8, combined_first_string)

            combined_second_string = ', '.join(second_row_list)
            can.drawString((PAGE_WIDTH - second_line_width) / 2.0, y, combined_second_string)

        #  corners stick data and lower level
        can.setFont(font_name, stick_font_size)
        if canister['lower_level']:
            ll_image = os.path.join('static', 'LL.png')
            can.drawImage(ll_image, (PAGE_WIDTH - 9), y - 7, 10, 11, mask='auto')

        return can


def generate_mfd_canister_label(file_name: str, canister_data_list: list):
    """
    Generates mfd canister label pdf

    :param file_name: pdf file name
    :param canister_data_list: canister data to be printed
    :return:
    """
    try:
        canister_qrcode_dict = dict()

        font_name = 'Helvetica-Bold'  # 'Times-Bold'
        canister_id_size = 10  # 7
        product_id_font_size = 7  # 3
        page_size = (2.25 * 72, 1.25 * 72)  # 2.25 inch * 1.25 inch (w*h)
        PAGE_WIDTH = (2.25 * 72)
        logger.debug(file_name)
        can = canvas.Canvas(file_name, pagesize=page_size)

        for canister in canister_data_list:
            # Add dosepack logo
            draw_dosepack_logo(can)

            y = 7  # start of y axis cursor
            # add product id
            if canister['product_id']:
                product_id = "PROD. ID: {}".format(canister['product_id'])
            else:
                product_id = "PROD. ID: N.A"
            can.setFont(font_name, product_id_font_size)
            product_id_width = pdfmetrics.stringWidth(product_id, fontName=font_name, fontSize=product_id_font_size)
            product_id_x_axis = PAGE_WIDTH - product_id_width - 2
            can.drawString(product_id_x_axis, 82, product_id)

            # Add QR code
            qrw = QrCodeWidget(str(canister["canister_id_with_mfd_prefix"]))
            b = qrw.getBounds()
            w = b[2] - b[0]
            h = b[3] - b[1]
            d = Drawing(50, 50, transform=[60. / w, 0, 0, 60. / h, 0, 0])
            d.add(qrw)

            qrcode_to_use = d
            qrcode_to_use.hAlign = 'CENTER'
            renderPDF.draw(qrcode_to_use, can, (PAGE_WIDTH - 62) / 2.0, y=25)

            # Add canister id
            can.setFont(font_name, canister_id_size)
            canister_id = 'ID: ' + str(canister["canister_id"])
            id_width = stringWidth(canister_id, fontName=font_name, fontSize=canister_id_size)
            can.drawString((PAGE_WIDTH - id_width) / 2.0, y+12, canister_id)
            # device_name = "Manual Canister Cart 1"
            device_name = canister['home_cart']
            device_name_width = stringWidth(device_name, fontName=font_name, fontSize=canister_id_size)
            can.drawString((PAGE_WIDTH - device_name_width) / 2.0, y, device_name)
            can.showPage()
            # can = generate_mfd_canister_top_label(canister, can)
            # can.showPage()
        can.save()
    except Exception as e:
        logger.info(e)
        return e


def generate_mfd_canister_top_label(canister, can):
    """
       Generates mfd canister top label
       :param can: existing canvas
       :param canister: canister data to be printed
       :return: can
       """
    try:
        font_name = 'Helvetica-Bold'  # 'Times-Bold'
        canister_id_size = 25  # 7
        product_id_font_size = 10  # 3
        PAGE_WIDTH = (2.25 * 72)

        # Add dosepack logo
        draw_dosepack_logo(can)

        y = 32  # start of y axis cursor
        # add product id
        if canister['product_id']:
            product_id = "PROD. ID: {}".format(canister['product_id'])
        else:
            product_id = "PROD. ID: N.A"
        can.setFont(font_name, product_id_font_size)
        product_id_width = pdfmetrics.stringWidth(product_id, fontName=font_name, fontSize=product_id_font_size)
        product_id_x_axis = PAGE_WIDTH - product_id_width - 2
        can.drawString(product_id_x_axis, 78, product_id)

        # Add canister id
        can.setFont(font_name, canister_id_size)
        canister_id = 'ID: ' + str(canister["canister_id"])
        id_width = stringWidth(canister_id, fontName=font_name, fontSize=canister_id_size)
        can.drawString((PAGE_WIDTH - id_width) / 2.0, y + 4, canister_id)
        return can
    except Exception as e:
        logger.info(e)
        return e