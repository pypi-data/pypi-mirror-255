import os
import shutil
import time
from peewee import DoesNotExist, InternalError, DataError, IntegrityError
import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import get_current_date_time, convert_date_to_sql_date
from dosepack.validation.validate import validate
from src import constants
from src.label_printing.print_label import bulk_print_pack_label
from src.dao.pack_dao import update_dict_pack_details, db_get_unassociated_packs
from src.dao.verification_dao import get_processed_packs_dao


logger = settings.logger


@validate(required_fields=["company_id", "time_zone"])
def get_packs_master(request_params):
    """
    Returns packs which are processed.

    @param request_params: dict Dictionary containing system_id key
    and other param to filter, sort and paginate the results
    :return: str
    """
    logger.info("Parameters for get_packs_master: {}"
                .format(request_params))
    company_id = request_params["company_id"]
    system_id = request_params.get("system_id", None)
    time_zone = request_params["time_zone"]
    print_labels = request_params.get('print_labels', False)
    user_id = request_params.get('user_id', None)
    filter_fields = request_params.get('filter_fields', None)
    sort_fields = request_params.get('sort_fields', None)
    paginate = request_params.get('paginate', None)
    module = request_params.get('module', None)
    if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
        return error(1020, 'Missing key(s) in paginate.')
    try:
        count, results, patient_count, facility_count = get_processed_packs_dao(company_id=company_id,
                                                                                filter_fields=filter_fields,
                                                                                paginate=paginate,
                                                                                sort_fields=sort_fields,
                                                                                time_zone=time_zone, module_id=module)

        # schedule_data = PatientSchedule.get_next_schedules(company_id)
        # for item in results:
        #     if item['schedule_id']:
        #         item['delivery_date'] = schedule_data['{}:{}'.format(item['schedule_id'], item['facility_id'])]['delivery_date']
        #     else:
        #         item['delivery_date'] = None
        # print(results)
        # if sort_on_delivery_date:
        #
        #     sorting_list = list()
        #     null_list = list()
        #     for item in results:
        #         if item['delivery_date']:
        #             sorting_list.append(item)
        #     if reverse:
        #         sorted(sorting_list, key=lambda i: i['delivery_date'], reverse=True)
        #     else:
        #         sorted(sorting_list, key=lambda i: i['delivery_date'], reverse=True)
        #     pack_list = list()
        #     if reverse:
        #         if null_list:
        #             pack_list.extend(null_list)
        #         if sorting_list:
        #             pack_list.extend(sorting_list)
        #     else:
        #         if sorting_list:
        #             pack_list.extend(sorting_list)
        #         if null_list:
        #             pack_list.extend(null_list)
        # else:
        #     pack_list = results
        if print_labels:  # if user wants to print labels for given filtered packs
            if not user_id:
                return error(1020, "The parameter user_id is required with print_labels.")
            if not system_id:
                return error(1020, "The parameter system_id is required with print_labels.")
            packs = list()
            for item in results:
                packs.append(item['pack_id'])
                # schedule_data[schedule_facility_id] = cls.get_next_schedule_from_last_import(record)
            # packs will be printed through default printer
            # returning print labels response
            return bulk_print_pack_label({'pack_ids': packs,
                                          'user_id': user_id,
                                          'system_id': system_id
                                          })
        for record in results:
            record["cyclic_pack"] = 1 if record["store_type"] == constants.STORE_TYPE_CYCLIC else 0
        response = {"pack_list": list(results), "number_of_records": count, "patient_count": patient_count,
                    "facility_count": facility_count}
        return create_response(response)
    except DoesNotExist as e:
        logger.error("error in get_packs_master {}".format(e))
        return error(1004)
    except InternalError as e:
        logger.error("error in get_packs_master {}".format(e))
        return error(2001)
    except Exception as e:
        logger.error("error in get_packs_master {}".format(e))
        return error(2001)


@validate(required_fields=["pack_id", "rfid", "system_id"])
def associate_rfid_with_pack_id(dict_pack_info):
    """
        Takes the pack id and associates rfid with it for a given system id.

        Args:
            dict_pack_info (pack_id): The pack id with which rfid is to be associated.

        Returns:
           json response in success or failure

        Examples:
            >>> associate_rfid_with_pack_id({})
                []
    """
    # get the user_id from username
    try:
        user_id = dict_pack_info["user_id"]
    except KeyError:
        user_id = 1  # todo remove when user id will be assigned to robot, crm

    rfid = dict_pack_info["rfid"]
    pack_id = int(dict_pack_info["pack_id"])
    system_id = int(dict_pack_info["system_id"])
    current_date_time = get_current_date_time()

    try:
        with db.transaction():
            update_dict = {"rfid": rfid,
                           "modified_by": user_id,
                           "modified_date": current_date_time}
            status = update_dict_pack_details(update_dict=update_dict, pack_id=pack_id, system_id=system_id)
        return create_response(status)

    except (InternalError, DataError, IntegrityError) as ex:
        logger.error("error in associate_rfid_with_pack_id {}".format(ex))
        error(2001, ex)
    except Exception as e:
        logger.error("Error in associate_rfid_with_pack_id {}".format(e))
        return error(1000, "Error in associate_rfid_with_pack_id: " + str(e))


@validate(required_fields=["date_from", "date_to", "system_id"])
def get_all_unassociated_packs(dict_date_info):
    """
        Takes all the packs which do not have rfid associated with them.

        Args:
            dict_date_info (dict): from_date, to_date, system_id

        Returns:
           json response in success or failure

        Examples:
            >>> get_all_unassociated_packs({})
                []
    """
    from_date, to_date = convert_date_to_sql_date(dict_date_info["date_from"], dict_date_info["date_to"])
    try:
        response = db_get_unassociated_packs(from_date, to_date, dict_date_info["system_id"])
        return create_response(response)

    except (InternalError, DataError, IntegrityError) as ex:
        logger.error("error in get_all_unassociated_packs {}".format(ex))
        error(2001, ex)
    except Exception as e:
        logger.error("Error in get_all_unassociated_packs {}".format(e))
        return error(1000, "Error in get_all_unassociated_packs: " + str(e))


def store_photo_in_server(dict_photo_info):
    """
        Stores the photo into the server.

        Args:
            dict_photo_info (dict): data, filename

        Returns:
            json response in success or failure

        Examples:
            >>> store_photo_in_server({})
                {}
    """
    # get the file name and data
    filename = dict_photo_info["file_name"]
    img_data = dict_photo_info["img_data"]
    # create directory to store the image
    val, file_path = create_directory("image_storage")
    if val:
        # create the path for storage
        file_path = os.path.join(file_path, filename)
        try:
            # creating the file and storing its content
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(img_data, f)
            return create_response({"data": filename + ' stored successfully into server.', "status": "Success"})
        except TypeError as ex:
            error(10008, ex)
        except AttributeError as ex:
            error(2001, ex)
    else:
        return create_response({"data": 'Storing ' + filename + ' into server failed.', "status": "Failure"})


def create_directory(filename):
    """Creates required directories in the order of year, month and day in the 'filename' directory.

    Args:
        filename (str): the parent directory in which directory to be created

    Returns:
        True if successfully able to create a directory, False otherwise
    """
    today_path = time.strftime('%Y/%m/%d')

    try:
        # adding today_path to the parent path
        file_path = os.path.join(filename, today_path)

        # creating directory if data does not exist
        if not os.path.exists(file_path):
            os.makedirs(file_path)
    except OSError as ex:
        return False, str(ex)

    return True, file_path
