from dosepack.utilities.utils import log_args_and_response
from src.api_utility import getrecords
from src.dao.manual_pack_dao import getuserpacks, fields, get_patient_list, get_patient, get_facility, get_facility_list
from src.service.notifications import Notifications
import settings

logger = settings.logger


@log_args_and_response
def getPatientsList(request, json):
    try:
        postBody = getrequestparams(request, json)
        query = get_patient_list()
        return ok(getrecords({"sorts": [["patient_name", 1]], "filters": postBody["filters"]}, fields, query, True), 0)
    except Exception as e:
        return error(e, [])


@log_args_and_response
def getPatients(company_id, available_only=True):
    try:
        record = get_patient(company_id, available_only)
        return ok(record, 0)
    except Exception as e:
        return error(e, [])


# def getTotalPacks(filters, fields):
#     query = PackDetails.select(
#         FacilityMaster.facility_name,
#         PatientMaster.facility_id,
#         fn.MIN(FileHeader.created_date).alias('uploaded_date'),
#         PackDetails.created_date,
#         fn.DATE(fn.MAX(PackHeader.scheduled_delivery_date)).alias('delivery_date'),
#     ).dicts() \
#         .join(PackHeader, on=PackDetails.pack_header_id == PackHeader.id) \
#         .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
#         .join(FileHeader, on=PackHeader.file_id == FileHeader.id) \
#         .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
#         .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
#         .join(PackUserMap, on=PackUserMap.pack_id == PackDetails.id)
#     totalPacks = getrecords(filters, fields, query)
#     return totalPacks["totalRecords"]
#

@log_args_and_response
def getFacilitiesList(request, json):
    try:
        postBody = getrequestparams(request, json)
        query = get_facility_list()
        return ok(getrecords({"sorts": [["facility_name", 1]], "filters": postBody["filters"]}, fields, query, True), 0)
    except Exception as e:
        return error(e, [])


@log_args_and_response
def getFacilities(company_id, available_only=True):
    try:
        record = get_facility(company_id, available_only)
        return ok(record, 0)
    except Exception as e:
        return error(e, [])


@log_args_and_response
def getpacks(request, json):
    try:
        params = getrequestparams(request, json)
        data = getuserpacks(params)
        if "filters" in params and "from_scan" in params["filters"] and params["filters"]["from_scan"] and len(
                data["data"]) == 1:
            Notifications().scan(data["data"][0]["id"])
        return ok(data["data"], data["totalRecords"],
                  {'totalPatients': data['totalPatients'], 'totalFacilities': data['totalFacilities'],
                   'PacksCount': data['totalPacksCount']})
    except Exception as e:
        return error(e, [])

#
# def remove_notification(company_id, user_id, message_id):
#     Notifications().remove_notification(company_id, user_id, message_id)


def getRecords_from_request(request, json, fields, query, onlydata=False):
    body = getrequestparams(request, json)
    return getrecords(body, json, fields, query, onlydata)


def getrequestparams(request, json):
    bytesdata = request.body.read()
    bytesdata = bytesdata.decode("utf-8")
    return json.loads(bytesdata)


def ok(data, totalrows=0, addl=None):
    result = {"data": data, "totalRecords": totalrows, "error": False, "errorMessage": ""}
    if addl is not None:
        result.update(addl)
    return result


def error(e, default=None):
    msgs = list()
    for var in e.args:
        msgs.append(str(var))
    return {"data": default, "totalRecords": 0, "error": True, "errorMessage": "\n".join(msgs)}
