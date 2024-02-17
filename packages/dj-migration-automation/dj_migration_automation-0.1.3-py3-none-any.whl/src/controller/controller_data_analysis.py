import json
import os
import sys

import cherrypy

import settings
from dosepack.base_model.base_model import db, logger
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.manage_db_connection import use_database
from src.service.data_analysis import get_robot_daily_update, get_efficiency_stats, get_manual_drugs_for_imported_batch, \
    get_batch_wise_drop_count_percentage, get_ndc_percentile_usage, \
    get_sensor_drug_error_data, get_pill_analysis_falling_on_3D_printed_part, get_success_sensor_drug_drop, \
    pvs_detection_problem_classification, get_csv_data_for_sensor_error, get_drug_data_for_graph_regeneration,\
    get_manual_pack_filling_details, get_manual_pack_filling_details_for_analyzer, get_sensor_error_count_robot_wise, \
    get_sensor_data_with_different_condition, get_filled_slot_count_of_pack, get_user_reported_error_data,\
    user_reported_error_mail



class RobotDailyUpdate(object):
    """
    Controller to get robot daily update.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, system_id=None, company_id=None, time_zone=None, **kwargs):
        try:
            if system_id is None or company_id is None:
                return error(1001, "Missing Parameter(s): system_id or company_id")
            data_dict = {
                'system_id': system_id,
                'company_id': company_id,
                'time_zone': time_zone,
            }
            cherrypy.response.timeout = 450
            response = get_robot_daily_update(data_dict)
            return create_response(response)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_robot_daily_update {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_robot_daily_update: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_robot_daily_update: " + str(ex))


class NdcPercentileUsage(object):
    """
    Controller to get robot daily update.
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, system_id=None, company_id=None, time_zone=None, ndc=None, **kwargs):
        try:
            if system_id is None or company_id is None or ndc is None:
                return error(1001, "Missing Parameter(s): system_id or company_id or ndc")
            data_dict = {
                'system_id': system_id,
                'company_id': company_id,
                'time_zone': time_zone,
                'ndc': ndc
            }
            response = get_ndc_percentile_usage(data_dict)
            return create_response(response)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_ndc_percentile_usage {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_ndc_percentile_usage: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_ndc_percentile_usage: " + str(ex))


class GetEfficiencyStats(object):
    """
    Controller for get efficiency statistics
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, from_date=None, to_date=None, time_zone=None, robot_daily_update_flag=False,  **kwargs):
        try:
            data_dict = {
                'from_date': from_date,
                'to_date': to_date,
                'time_zone': time_zone,
                'robot_daily_update_flag': robot_daily_update_flag
            }

            response = get_efficiency_stats(data_dict)

            return create_response(response)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_efficiency_stats {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in get_efficiency_stats: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_efficiency_stats: " + str(ex))


class GetImportedBatchManualDrugs(object):
    """
    Controller for get imported batch manual drugs
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, batch_id=None, company_id=None, system_id=None, **kwargs):
        try:
            data_dict = {
                'batch_id': batch_id,
                'company_id': company_id,
                'system_id': system_id
            }

            response = get_manual_drugs_for_imported_batch(data_dict)

            return create_response(response)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_manual_drugs_for_imported_batch {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in get_manual_drugs_for_imported_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_manual_drugs_for_imported_batch: " + str(ex))


class GetBatchWiseDropCountPercentage(object):
    """
    Controller for get batch wise drop count percentage
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, batch_ids, company_id=None, system_id=None, **kwargs):
        try:
            data_dict = {
                'batch_ids': batch_ids,
                'company_id': company_id,
                'system_id': system_id
            }

            response = get_batch_wise_drop_count_percentage(data_dict)

            return create_response(response)
        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_manual_drugs_for_imported_batch {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error in get_manual_drugs_for_imported_batch: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_manual_drugs_for_imported_batch: " + str(ex))

class GetSensorDroppingError(object):
    exposed = True
    """
        Controller for get sensor drop errors for specific date.
    """

    @use_database(db, settings.logger)
    def GET(self, system_id=None, company_id=None, time_zone=None, date=None, **kwargs):
        try:
            if system_id is None or company_id is None:
                return error(1001, "Missing Parameter(s): system_id or company_id")
            if time_zone is None:
                time_zone = "PST"
            data_dict = {
                'system_id': system_id,
                'company_id': company_id,
                'time_zone': time_zone,
                'date': date
            }
            cherrypy.response.timeout = 400
            response = get_sensor_drug_error_data(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_sensor_drug_error_data {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_sensor_drug_error_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_sensor_drug_error_data: " + str(ex))


class PillAnalysisFallingOn3DPrintedPart(object):
    exposed = True
    """
        Controller for get sensor drop errors for specific date.
    """

    @use_database(db, settings.logger)
    def GET(self, system_id=None, company_id=None, time_zone=None, date=None, min_value=None, max_value=None, **kwargs):
        try:
            if system_id is None or company_id is None:
                return error(1001, "Missing Parameter(s): system_id or company_id")
            if time_zone is None:
                time_zone = "PST"
            if min_value is None:
                min_value = 28
            if max_value is None:
                max_value = 30
            data_dict = {
                'system_id': system_id,
                'company_id': company_id,
                'time_zone': time_zone,
                'date': date,
                'min_value': min_value,
                'max_value': max_value
            }
            cherrypy.response.timeout = 400
            response = get_pill_analysis_falling_on_3D_printed_part(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_sensor_drug_error_data {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_sensor_drug_error_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_sensor_drug_error_data: " + str(ex))

class GetSuccessDropAnalysis(object):
    exposed = True
    """
        Controller for get success drop data for specific fndc,txr.
    """

    @use_database(db, settings.logger)
    def GET(self, track_date=None, fndc=None, txr=None, number_of_graphs=None, time_zone=None, **kwargs):
        try:
            if track_date is None and fndc is None and txr is None:
                return error(1001, "Missing Parameter(s): start_date or end_date or fndc or txr")
            if time_zone is None:
                time_zone = "PST"
            data_dict = {
                'time_zone': time_zone,
                'track_date': track_date,
                'number_of_graphs': int(number_of_graphs),
                'fndc': fndc,
                'txr': txr,
            }
            cherrypy.response.timeout = 400
            response = get_success_sensor_drug_drop(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_success_sensor_drug_drop {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_success_sensor_drug_drop: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_success_sensor_drug_drop: " + str(ex))


class PvsDetectionProblemClassification(object):
    exposed = True
    """
        Controller for Pvs Detection Problem Classification
    """

    @use_database(db, settings.logger)
    def GET(self, system_id=None, company_id=None, time_zone=None, date=None, **kwargs):
        try:
            if system_id is None or company_id is None:
                return error(1001, "Missing Parameter(s): system_id or company_id")
            if time_zone is None:
                time_zone = "PST"
            data_dict = {
                'system_id': system_id,
                'company_id': company_id,
                'time_zone': time_zone,
                'date': date
            }
            cherrypy.response.timeout = 400
            response = pvs_detection_problem_classification(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in pvs_detection_problem_classification {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in pvs_detection_problem_classification: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in pvs_detection_problem_classification: " + str(ex))


class GetCSVdataForSensorError(object):
    exposed = True
    """
        Controller for Pvs Detection Problem Classification
    """

    @use_database(db, settings.logger)
    def GET(self, system_id=None, company_id=None, time_zone=None, date=None, **kwargs):
        try:
            if system_id is None or company_id is None:
                return error(1001, "Missing Parameter(s): system_id or company_id")
            if time_zone is None:
                time_zone = "PST"
            data_dict = {
                'system_id': system_id,
                'company_id': company_id,
                'time_zone': time_zone,
                'date': date
            }
            cherrypy.response.timeout = 400
            response = get_csv_data_for_sensor_error(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_csv_data_for_sensor_error {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_csv_data_for_sensor_error: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in pvs_detection_problem_classification: " + str(ex))

class GetDrugDataForGraphRegenration(object):
    exposed = True
    """
        Controller for Pvs Detection Problem Classification
    """

    @use_database(db, settings.logger)
    def GET(self, system_id=None, company_id=None, time_zone=None, date=None, fndc=None, txr=None, **kwargs):
        try:
            if system_id is None or company_id is None:
                return error(1001, "Missing Parameter(s): system_id or company_id")
            if time_zone is None:
                time_zone = "PST"
            data_dict = {
                'system_id': system_id,
                'company_id': company_id,
                'time_zone': time_zone,
                'date': date,
                'fndc': fndc,
                'txr': txr
            }
            cherrypy.response.timeout = 400
            response = get_drug_data_for_graph_regeneration(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_csv_data_for_sensor_error {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_csv_data_for_sensor_error: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in pvs_detection_problem_classification: " + str(ex))


class GetManualPackFillingDetails(object):
    exposed = True
    """
        Controller for Pvs Detection Problem Classification
    """

    @use_database(db, settings.logger)
    def GET(self, time_zone=None, from_date=None, to_date=None, **kwargs):
        try:
            if time_zone is None:
                time_zone = "PST"
            data_dict = {
                'time_zone': time_zone,
                'to_date': to_date,
                'from_date': from_date,
            }
            response = get_manual_pack_filling_details(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_manual_pack_filling_details {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_manual_pack_filling_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_manual_pack_filling_details: " + str(ex))

class GetManualPackFillingDetailsForAnalyzer(object):
    exposed = True
    """
        Controller for Pvs Detection Problem Classification
    """

    @use_database(db, settings.logger)
    def GET(self, time_zone=None, date=None, **kwargs):
        try:
            if time_zone is None:
                time_zone = "PST"
            data_dict = {
                'time_zone': time_zone,
                'date': date,
            }
            response = get_manual_pack_filling_details_for_analyzer(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_manual_pack_filling_details {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_manual_pack_filling_details: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_manual_pack_filling_details: " + str(ex))

class GetSensorErrorCountRobotWise(object):
    exposed = True
    """
        Controller for get sensor drop errors for specific date.
    """

    @use_database(db, settings.logger)
    def GET(self, time_zone=None, date=None, **kwargs):
        try:
            data_dict = {
                'time_zone': time_zone,
                'date': date
            }
            cherrypy.response.timeout = 400
            response = get_sensor_error_count_robot_wise(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_sensor_drug_error_data {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_sensor_drug_error_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_sensor_drug_error_data: " + str(ex))

class GetSensorDataWithDifferentCondition(object):
    exposed = True
    """
        Controller for get sensor drop errors for specific date.
    """

    @use_database(db, settings.logger)
    def GET(self, time_zone=None,  date=None, **kwargs):
        try:
            if time_zone is None:
                time_zone = "PST"
            data_dict = {
                'time_zone': time_zone,
                'date': date,
            }
            cherrypy.response.timeout = 400
            response = get_sensor_data_with_different_condition(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_sensor_drug_error_data {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_sensor_drug_error_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_sensor_drug_error_data: " + str(ex))

class GetFilledSlotCountForPack(object):
    exposed = True
    """
        Controller for get slot count of pack with pack_id and batch_id
    """

    @use_database(db, settings.logger)
    def GET(self, pack_ids=None, time_zone=None, **kwargs):
        try:
            data_dict = {
                'pack_ids': pack_ids,
                'time_zone': time_zone,
            }
            cherrypy.response.timeout = 400
            response = get_filled_slot_count_of_pack(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_filled_slot_count_of_pack {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_filled_slot_count_of_pack: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_filled_slot_count_of_pack: " + str(ex))


class GetUserReportedPackDetail(object):
    exposed = True
    """
        Controller for get user reported error detail for specific date.
    """

    @use_database(db, settings.logger)
    def GET(self, time_zone=None,  from_date=None, to_date=None, **kwargs):
        try:
            data_dict = {
                'time_zone': time_zone,
                'from_date': from_date,
                "to_date": to_date
            }
            cherrypy.response.timeout = 400
            response = get_user_reported_error_data(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in get_sensor_drug_error_data {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in get_user_reported_error_data: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in get_user_reported_error_data: " + str(ex))


class UserReportedErrorMail(object):
    exposed = True
    """
        Controller for get user reported error detail for specific date.
    """

    @use_database(db, settings.logger)
    def GET(self, time_zone=None,  date=None, to_date=None, **kwargs):
        try:
            data_dict = {
                'time_zone': time_zone,
                "date": date
            }
            cherrypy.response.timeout = 400
            response = user_reported_error_mail(data_dict)

            return create_response(response)

        except json.JSONDecodeError as e:
            return error(1020, str(e))
        except Exception as ex:
            logger.error("Error in user_reported_error_mail {}".format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                f"Error in user_reported_error_mail: exc_type - {exc_type}, filename - {filename}, line - {exc_tb.tb_lineno}")
            return error(1000, "Error in user_reported_error_mail: " + str(ex))