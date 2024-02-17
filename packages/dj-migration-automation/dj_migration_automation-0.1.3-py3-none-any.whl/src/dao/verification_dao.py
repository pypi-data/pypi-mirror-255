import functools
import operator
from functools import reduce

from peewee import fn, JOIN_LEFT_OUTER, InternalError, IntegrityError, DataError
from playhouse.shortcuts import cast, case

import settings
from src import constants
from src.api_utility import get_results, get_pack_module, get_multi_search
from src.model.model_batch_master import BatchMaster
from src.model.model_code_master import CodeMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_ext_pack_details import ExtPackDetails
from src.model.model_facility_master import FacilityMaster
from src.model.model_fill_error_details import FillErrorDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_status_tracker import PackStatusTracker
from src.model.model_pack_user_map import PackUserMap
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_print_queue import PrintQueue

logger = settings.logger


def get_processed_packs_dao(company_id, filter_fields, paginate, sort_fields, time_zone, module_id=None):
    """

    @param company_id:
    @param filter_fields:
    @param paginate:
    @param sort_fields:
    @param time_zone:
    @param module_id:
    @return:
    """
    debug_mode_flag = False
    clauses = []

    try:
        if "pack_type" in filter_fields and module_id != constants.MODULE_TYPE_RPH_SCREEN:
            pack_type_clauses = []
            pack_type_data = filter_fields.pop("pack_type")
            for pack_type_dict in pack_type_data:
                if list(pack_type_dict.values())[0] == 1:
                    store_type = constants.STORE_TYPE_CYCLIC
                    sub_clause = (
                        PackDetails.packaging_type == list(pack_type_dict.keys())[0],
                        PackDetails.store_type == store_type)
                else:
                    store_type = [constants.STORE_TYPE_NON_CYCLIC, constants.STORE_TYPE_RETAIL]
                    sub_clause = (
                        PackDetails.packaging_type == list(pack_type_dict.keys())[0],
                        PackDetails.store_type.in_(store_type))
                pack_type_clauses.append(functools.reduce(operator.and_, sub_clause))
            clauses.append(functools.reduce(operator.or_, pack_type_clauses))
        if "fill_error" in filter_fields:
            fill_error_flag = filter_fields.pop("fill_error")
        else:
            fill_error_flag = False
        module = str()
        # status_tuples = [(settings.MANUAL_PACK_STATUS, "Filled Manually"),
        #                  (settings.DONE_PACK_STATUS, "Filled Automatically"),
        #                  (settings.PROCESSED_MANUALLY_PACK_STATUS, "Processed Manually"),
        #                  (settings.DELETED_PACK_STATUS, "Deleted"),
        #                  (settings.PENDING_PACK_STATUS, "Pending"),
        #                  (settings.PROGRESS_PACK_STATUS, "Progress")
        #                  ]

        filled_flow_tuple = [(0, 'Auto'),
                             (1, 'Pre-Batch Allocation'),
                             (2, 'Post-Import'),
                             (3, 'Manual Verification Station'),
                             (4, 'Pre-Import'),
                             (11, 'DosePacker')
                             ]

        if filter_fields and 'module' in filter_fields.keys():
            module = filter_fields['module']
            filter_fields.pop('module')
        filled_at_tuples = PackDetails.FILLED_AT_MAP.items()
        if filter_fields and filter_fields.get('pack_display_id') and filter_fields.get('pack_id'):
            debug_mode_flag = True
        elif filter_fields and filter_fields.get('pack_display_id') and not filter_fields.get('pack_id'):
            debug_mode_flag = False

        # do not give alias here, instead give it in select_fields,
        # as this can be reused in where clause
        fields_dict = {"pack_display_id": PackDetails.pack_display_id,
                       "facility_name": FacilityMaster.facility_name,
                       "filled_date": fn.DATE(fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC, time_zone)),
                       "created_date": fn.DATE(fn.CONVERT_TZ(PackDetails.created_date, settings.TZ_UTC, time_zone)),
                       "filled_datetime": fn.CONVERT_TZ(PackDetails.filled_date, settings.TZ_UTC, time_zone),
                       "patient_name": fn.CONCAT(PatientMaster.last_name, ', ', PatientMaster.first_name),
                       # "pack_status": fn.IF(
                       #     PackUserMap.id.is_null(True),
                       #     case(PackDetails.pack_status, status_tuples, default='Filled Automatically'),
                       #     "Filled Manually"
                       # ),
                       "pack_status": CodeMaster.id,
                       "filled_at_value": fn.IF(
                           PackDetails.filled_at.is_null(False),
                           cast(case(PackDetails.filled_at, filled_at_tuples), 'CHAR'), 'N.A.'
                       ),
                       "pack_id": PackDetails.id,
                       "system_id": PackDetails.system_id,
                       "print_requested": fn.IF(PrintQueue.id.is_null(True), 'No', 'Yes'),
                       "delivery_date": fn.DATE(PackHeader.scheduled_delivery_date),
                       "filled_by": PackDetails.filled_by,
                       "filled_flow": fn.IF(
                           PackUserMap.id.is_null(True),
                           case(PackDetails.filled_at, filled_flow_tuple, default='DosePacker'),
                           "Pack_Fill_Flow"
                       ),
                       "assigned_to": PackUserMap.assigned_to,
                       "assigned_to_fill_error": FillErrorDetails.assigned_to,
                       "reported_by": FillErrorDetails.reported_by,
                       "storage_container_name": ContainerMaster.drawer_name,
                       "modified_date": fn.DATE(fn.CONVERT_TZ(PackDetails.modified_date, settings.TZ_UTC, time_zone)),
                       "modified_by": PackDetails.modified_by,
                       "admin_start_date": fn.DATE(PackDetails.consumption_start_date),
                       "admin_end_date": fn.DATE(PackDetails.consumption_end_date),
                       "pack_type": PackDetails.packaging_type,
                       "ext_pack_usage_status_id": ExtPackDetails.pack_usage_status_id,
                       "verification_status": PackDetails.verification_status,
                       "pack_checked_by": PackDetails.pack_checked_by,
                       "pack_checked_time": PackDetails.pack_checked_time,
                       "store_type": PackDetails.store_type,
                       "pharmacy_rx_no": PatientRx.pharmacy_rx_no
                       }
        global_search = [
            fn.CONCAT(PatientMaster.last_name, ", ", PatientMaster.first_name),
            FacilityMaster.facility_name,
            PackDetails.pack_display_id,
            PackDetails.pack_status,
            PatientRx.pharmacy_rx_no
        ]
        if filter_fields and filter_fields.get('global_search', None) is not None:
            multi_search_string = filter_fields['global_search'].split(',')
            multi_search_string.remove('') if '' in multi_search_string else multi_search_string
            clauses = get_multi_search(clauses, multi_search_string, global_search)
        CHAR = 'CHAR'  # to cast it char instead of int or datetime
        select_fields = [fields_dict['pack_id'].alias('pack_id'),
                         fields_dict['pack_display_id'].alias('pack_display_id'),
                         fields_dict['system_id'].alias('system_id'),
                         # cast(PackDetails.pack_display_id, CHAR).alias('pack_display_id'),
                         PackDetails.pack_no,
                         fields_dict["filled_date"].alias("filled_date"),
                         cast(fields_dict["filled_datetime"], CHAR).alias("filled_datetime"),
                         PackHeader.created_date,
                         cast(PackHeader.delivery_datetime, CHAR).alias('delivery_datetime'),
                         fields_dict['delivery_date'].alias('delivery_date'),
                         fn.DATE(PackHeader.delivery_datetime).alias('ips_delivery_date'),
                         fields_dict["modified_date"].alias("modified_date"),
                         PackDetails.modified_by,
                         PackHeader.patient_id,
                         PatientMaster.last_name,
                         PatientMaster.first_name,
                         fields_dict["patient_name"].alias('patient_name'),
                         PatientMaster.id.alias('patient_id'),
                         PatientMaster.patient_no,
                         FacilityMaster.facility_name,
                         PatientMaster.facility_id,
                         PatientMaster.dob,
                         PackDetails.order_no,
                         PackDetails.pack_plate_location,
                         PackDetails.facility_dis_id,
                         PackDetails.batch_id,
                         fields_dict['admin_start_date'].alias('admin_start_date'),
                         fields_dict['admin_end_date'].alias('admin_end_date'),
                         BatchMaster.status.alias('batch_status'),
                         # PackVerification.pack_fill_status, PackVerification.image_path,
                         # NoteMaster.note1, NoteMaster.note2, NoteMaster.note3, NoteMaster.note4, NoteMaster.note5,
                         CodeMaster.value,
                         CodeMaster.id.alias('pack_status'),
                         # fields_dict['pack_status'].alias('pack_status'),
                         fields_dict['filled_at_value'].alias('filled_at_value'),
                         fields_dict['print_requested'].alias('print_requested'),
                         fields_dict['filled_by'].alias('filled_by'),
                         fields_dict['assigned_to'].alias('assigned_to'),
                         PackUserMap.id.alias("pack_user_id"),
                         fields_dict['filled_flow'].alias('filled_flow'),
                         ContainerMaster.id.alias("storage_container_id"),
                         ContainerMaster.drawer_name.alias("storage_container_name"),
                         DeviceMaster.id.alias("storage_device_id"),
                         DeviceMaster.name.alias("storage_device_name"),
                         ExtPackDetails.ext_status_id.alias('ext_pack_status_id'),
                         fields_dict['ext_pack_usage_status_id'].alias("ext_pack_usage_status_id"),
                         PackStatusTracker.reason.alias('reason'),
                         PackDetails.packaging_type,
                         PatientRx.to_fill_qty,
                         FillErrorDetails.assigned_to.alias("assigned_to_fill_error"),
                         FillErrorDetails.reported_by,
                         PackDetails.created_date.alias("pack_created_date"),
                         PackDetails.id.alias("pack_id_count"),
                         PackDetails.store_type,
                         FacilityMaster.id.alias("facility_id_count"),
                         PackDetails.verification_status,
                         PackDetails.pack_checked_by,
                         PackDetails.pack_checked_time,
                         PatientRx.pharmacy_rx_no
                         ]

        clauses += [(PackDetails.company_id == company_id)]
        if fill_error_flag:
            clauses.append(PackDetails.verification_status == constants.RPH_VERIFICATION_STATUS_FILL_ERROR)
            clauses.append(PackDetails.pack_status.in_(
                [constants.PRN_DONE_STATUS, settings.DONE_PACK_STATUS, settings.PROCESSED_MANUALLY_PACK_STATUS]))
        elif module_id != constants.MODULE_TYPE_RPH_SCREEN:
            clauses.append(PackDetails.store_type == constants.STORE_TYPE_CYCLIC)

        if module_id == constants.MODULE_TYPE_RPH_SCREEN:
            clauses.append(
                (PackDetails.pack_status << [settings.DONE_PACK_STATUS, settings.PROCESSED_MANUALLY_PACK_STATUS,
                                             constants.PRN_DONE_STATUS]))
            clauses.append(PackDetails.delivery_status == None)

        if debug_mode_flag:
            like_search_list = ['facility_name', 'patient_name']
            string_search_field = [fields_dict['pack_display_id'], fields_dict['pack_id']]
            multi_search_fields = [filter_fields['pack_display_id']]
            # sub_clauses = [(PackDetails.company_id == company_id)]
            clauses = get_multi_search(clauses=clauses, multi_search_values=multi_search_fields,
                                       model_search_fields=string_search_field)
            filter_fields.pop('pack_display_id')
            filter_fields.pop('pack_id')
            # packs = PackDetails.select(PackDetails.id).dicts().where(reduce(operator.and_, sub_clauses))
            # clauses.append((fields_dict['pack_id'] << [record['id'] for record in packs]))

        else:
            like_search_list = ['pack_display_id', 'facility_name', 'patient_name']

        between_search_list = ['filled_date', 'delivery_date', 'modified_date', 'admin_start_date', 'created_date']
        exact_search_list = ['print_requested', 'pack_status', 'ext_pack_usage_status_id', 'cyclic_pack', 'pharmacy_rx_no']
        membership_search_list = ['pack_id', 'filled_at_value', 'system_id', 'filled_by', 'assigned_to',
                                  'storage_container_name', 'modified_by', 'assigned_to_fill_error', 'reported_by',
                                  'pack_type', 'verification_status', 'pack_checked_by', 'store_type']
        if module == settings.PACK_MODULE_BATCH_DISTRIBUTION:
            clauses.extend((PackDetails.pack_status == settings.PENDING_PACK_STATUS,
                           PackDetails.batch_id.is_null(True), PackUserMap.id.is_null(True)))
        if module == settings.PACK_MODULE_MANUAL_FILLING:
            clauses.extend((PackDetails.pack_status << settings.MANUAL_FILLING_STATUS,
                           PackUserMap.id.is_null(False)))
        if module == settings.PACK_MODULE_PACK_PRE:
            clauses.extend((BatchMaster.status << settings.PACK_PRE_BATCH_STATUS, PackDetails.batch_id.is_null(False),
                           PackUserMap.id.is_null(True)))
        if module == settings.PACK_MODULE_PACK_QUEUE:
            clauses.extend((BatchMaster.status == settings.BATCH_IMPORTED, PackUserMap.id.is_null(True),
                            PackDetails.pack_status << [
                                settings.PENDING_PACK_STATUS, settings.PROGRESS_PACK_STATUS]))
        if module == settings.PACK_MODULE_PACK_MASTER:
            clauses.append((PackDetails.pack_status << [settings.DONE_PACK_STATUS, settings.DELETED_PACK_STATUS,
                                                        settings.PROCESSED_MANUALLY_PACK_STATUS]))

        # if 'delivery_date' in filter_fields:
        #     delivery_date = datetime.datetime.strptime(filter_fields['delivery_date'], '%m-%d-%y')
        #     filter_fields['delivery_date'] = delivery_date.strftime('%Y-%m-%d')
        # reverse = False
        # sort_on_delivery_date = False
        order_list = list()
        # for item in sort_fields:
        #     if item[0] == 'delivery_date':
        #         sort_on_delivery_date = True
        #         if item[1] == -1:
        #             reverse = True
        #         sort_fields.remove(item)
        if sort_fields:
            order_list.extend(sort_fields)
        # print(reverse)
        sub_query = ExtPackDetails.select(fn.MAX(ExtPackDetails.id).alias('max_ext_pack_details_id'),
                                          ExtPackDetails.pack_id.alias('pack_id'),
                                          ExtPackDetails.packs_delivery_status.alias('packs_delivery_status')) \
            .group_by(ExtPackDetails.pack_id).alias('sub_query')
        sub_query_reason = PackStatusTracker.select(fn.MAX(PackStatusTracker.id).alias('max_pack_status_id'),
                                                    PackStatusTracker.pack_id.alias('pack_id')) \
            .group_by(PackStatusTracker.pack_id).alias('sub_query_reason')

        ext_join_condition = sub_query.c.pack_id == PackDetails.id
        if module_id == constants.MODULE_TYPE_RPH_SCREEN:
            ext_join_condition = (sub_query.c.pack_id == PackDetails.id) & (
                        sub_query.c.packs_delivery_status != constants.PACK_DELIVERY_STATUS_RETURN_FROM_THE_DELIVERY_ID)

        query = PackDetails.select(*select_fields) \
            .join(PackHeader, on=PackHeader.id == PackDetails.pack_header_id) \
            .join(BatchMaster, JOIN_LEFT_OUTER, on=BatchMaster.id == PackDetails.batch_id)\
            .join(PatientMaster, on=PackHeader.patient_id == PatientMaster.id) \
            .join(CodeMaster, on=PackDetails.pack_status == CodeMaster.id) \
            .join(FacilityMaster, on=FacilityMaster.id == PatientMaster.facility_id) \
            .join(PrintQueue, JOIN_LEFT_OUTER, on=PrintQueue.pack_id == PackDetails.id) \
            .join(PackUserMap, JOIN_LEFT_OUTER, on=PackUserMap.pack_id == PackDetails.id) \
            .join(ContainerMaster, JOIN_LEFT_OUTER, on=ContainerMaster.id == PackDetails.container_id) \
            .join(DeviceMaster, JOIN_LEFT_OUTER, on=DeviceMaster.id == ContainerMaster.device_id) \
            .join(sub_query, JOIN_LEFT_OUTER, on=ext_join_condition) \
            .join(ExtPackDetails, JOIN_LEFT_OUTER, on=ExtPackDetails.id == sub_query.c.max_ext_pack_details_id) \
            .join(sub_query_reason, JOIN_LEFT_OUTER, on=(sub_query_reason.c.pack_id == PackDetails.id)) \
            .join(PackStatusTracker, JOIN_LEFT_OUTER, on=PackStatusTracker.id == sub_query_reason.c.max_pack_status_id) \
            .join(PackRxLink, JOIN_LEFT_OUTER, on=PackRxLink.pack_id == PackDetails.id) \
            .join(PatientRx, JOIN_LEFT_OUTER, on=PatientRx.id == PackRxLink.patient_rx_id) \
            .join(FillErrorDetails, JOIN_LEFT_OUTER, on=FillErrorDetails.pack_id == PackDetails.id) \
            # multiple print request will result in multiple rows in this query so group data by pack_id
        query = query.group_by(PackDetails.id)
        results, count, non_paginate_result = get_results(query.dicts(), fields_dict, clauses=clauses,
                                                          filter_fields=filter_fields,
                                                          sort_fields=order_list,
                                                          paginate=paginate,
                                                          exact_search_list=exact_search_list,
                                                          like_search_list=like_search_list,
                                                          between_search_list=between_search_list,
                                                          membership_search_list=membership_search_list,
                                                          last_order_field=[fields_dict['pack_id']],
                                                          non_paginate_result_field_list=['pack_id_count',
                                                                                          'facility_id_count'])

        logger.info("In get_processed_packs_dao : processed query : {}".format(query))
        patient_count = len(set(non_paginate_result['pack_id_count'])) if non_paginate_result else 0
        facility_count = len(set(non_paginate_result['facility_id_count'])) if non_paginate_result else 0
        for data in results:
            data['module'] = get_pack_module(pack_status=data['pack_status'], batch_id=data['batch_id'],
                                             batch_status=data['batch_status'],
                                             facility_dist_id=data['facility_dis_id'], user_id=data['pack_user_id'])
        return count, results, patient_count, facility_count

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("error in get_processed_packs_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_processed_packs_dao {}".format(e))
        raise e


