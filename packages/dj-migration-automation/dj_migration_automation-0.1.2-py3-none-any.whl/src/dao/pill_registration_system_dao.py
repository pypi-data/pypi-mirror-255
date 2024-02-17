import datetime
import functools
import operator
from copy import deepcopy

from peewee import *

import settings
from dosepack.utilities.utils import image_convert, log_args_and_response
from src.dao.volumetric_analysis_dao import get_drug_details
from src.model.model_code_master import CodeMaster
from src.model.model_drug_details import DrugDetails
from src.model.model_pack_details import PackDetails
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_remote_tech_slot import RemoteTechSlot
from src.model.model_slot_details import SlotDetails
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src.model.model_company_setting import CompanySetting
from src.model.model_drug_dimension import DrugDimension
from src.model.model_custom_drug_shape import CustomDrugShape
from src import constants
from src.api_utility import get_results, apply_paginate
from src.model.model_pvs_slot import PVSSlot
from src.model.model_prs_drug_details import PRSDrugDetails
from src.model.model_pvs_slot_details import PVSSlotDetails
from src.model.model_pvs_drug_count import PVSDrugCount
from src.model.model_remote_tech_slot_details import RemoteTechSlotDetails

logger = settings.logger


def add_data_in_prs_drug_data(data_dict):
    try:
        logger.debug("In add_data_in_pvs_drug_data")
        if type(data_dict["unique_drug_id"]) == list:
            unique_drug_list = data_dict.pop("unique_drug_id")
            for unique_drug in unique_drug_list:
                create_dict = {"unique_drug_id": unique_drug}
                update_dict = data_dict
                PRSDrugDetails.db_update_or_create(create_dict=create_dict, update_dict=update_dict)
        else:
            create_dict = {"unique_drug_id": data_dict.pop("unique_drug_id")}
            update_dict = data_dict
            PRSDrugDetails.db_update_or_create(create_dict=create_dict, update_dict=update_dict)

        return True

    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error in add_data_in_prs_drug_data: " + str(e))
        raise
    except ValueError as e:
        logger.error("Error in add_data_in_prs_drug_data: " + str(e))
        raise


@log_args_and_response
def get_prs_data_dao(filter_fields, sort_fields, paginate, mode, required_count=16):
    """
        returns PRS drug data
        @param required_count:
        @param filter_fields: shape, color,
        @param sort_fields: mentioned fields
        @param paginate: page number and number of rows
        @return: dict
    """

    response = dict()
    pack_id_list = list()
    drug_qty_dict = dict()
    clauses = list()
    like_search_list = ["drug_name", "ndc"]
    membership_search_list = ["shape", "status", "color", "updated_by", "faces"]
    distinct_non_paginate_results = True
    order_list = list()
    having_clauses = list()
    linked_drugs = list()
    drug_list = list()
    last_order_field = list()
    unique_id_for_drug_details = list()
    logger.debug("In get_prs_data_dao")

    fields_dict = {
        "drug_name": DrugMaster.concated_drug_name_field(),
        "ndc": DrugMaster.ndc,
        "color": DrugMaster.color,
        "shape": CustomDrugShape.name,
        "status": PRSDrugDetails.status,
        "updated_by": fn.IF(PRSDrugDetails.status == constants.PRS_DRUG_STATUS_REGISTERED, PRSDrugDetails.registered_by,
                            fn.IF(PRSDrugDetails.status == constants.PRS_DRUG_STATUS_VERIFIED,
                                  PRSDrugDetails.verified_by,
                                  fn.IF(PRSDrugDetails.status == constants.PRS_DRUG_STATUS_DONE, PRSDrugDetails.done_by,
                                        'null'))),
        "faces": fn.IF(PRSDrugDetails.face1.is_null(False),
                       fn.IF(PRSDrugDetails.face2.is_null(False),
                             fn.IF(PRSDrugDetails.side_face.is_null(False), "All Faces", "Face1,Face2"), "Face1,Face2"), "None")
    }
    select_fields = [
        PRSDrugDetails.unique_drug_id.alias('unique_drug_id'),
        fields_dict["drug_name"].alias('drug_name'),
        DrugMaster.image_name,
        DrugMaster.imprint,
        fields_dict["ndc"].alias('ndc'),
        UniqueDrug.formatted_ndc,
        UniqueDrug.txr,
        PRSDrugDetails.expected_qty,
        fields_dict["shape"].alias('shape'),
        fields_dict["color"].alias('color'),
        fields_dict["status"].alias('status'),
        fields_dict["updated_by"].alias('update_by'),
        fields_dict["faces"].alias('faces'),
        CodeMaster.value.alias('code_status')
    ]
    try:
        month_back_date = (datetime.datetime.now() - datetime.timedelta(days=30)).date()

        packs_query = PackDetails.select(PackDetails.id).where(PackDetails.created_date > month_back_date)

        for pack in packs_query.dicts():
            pack_id_list.append(pack['id'])
        logger.info("In get_prs_data_dao, pack_id_list: {}".format(pack_id_list))

        if pack_id_list:
            drug_qty_query = PackRxLink.select(UniqueDrug.id, fn.SUM(SlotDetails.quantity).alias('quantity')) \
                                        .join(SlotDetails, on=SlotDetails.pack_rx_id == PackRxLink.id) \
                                        .join(DrugMaster, on=DrugMaster.id == SlotDetails.drug_id) \
                                        .join(UniqueDrug,
                                              on=((UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr))) \
                                        .join(PRSDrugDetails, on=PRSDrugDetails.unique_drug_id == UniqueDrug.id) \
                                        .where(PRSDrugDetails.status == constants.PRS_DRUG_STATUS_PENDING) \
                                        .group_by(UniqueDrug.id)

            drug_qty_query = drug_qty_query.where(PackRxLink.pack_id << pack_id_list)

            for drug in drug_qty_query.dicts():
                drug_qty_dict[drug['id']] = drug['quantity']

            sorted_drugs = sorted(drug_qty_dict.items(), key=operator.itemgetter(1))
            drug_list = [drug[0] for drug in sorted_drugs]

        linked_drug_query = PRSDrugDetails.select(UniqueDrug.id).dicts() \
                                .join(UniqueDrug, on=UniqueDrug.id == PRSDrugDetails.unique_drug_id) \
                                .join(RemoteTechSlotDetails,
                                      on=UniqueDrug.id == RemoteTechSlotDetails.label_drug_id) \
                                .where(PRSDrugDetails.status == constants.PRS_DRUG_STATUS_PENDING,
                                       RemoteTechSlotDetails.mapped_status == constants.SKIPPED_AND_SURE_MAPPED) \
                                .group_by(UniqueDrug.id) \
                                .having(fn.COUNT(fn.DISTINCT(RemoteTechSlotDetails.id)) >= required_count)

        # final drug list will be sorted drugs of last one month (based on quantity) and all the linked drugs.
        for drug in linked_drug_query:
            linked_drugs.append(drug['id'])
        final_drug_list = deepcopy(drug_list)
        for drug in drug_list:
            if drug not in linked_drugs:
                final_drug_list.remove(drug)
            else:
                linked_drugs.remove(drug)
        final_drug_list.extend(linked_drugs)
        logger.info("In get_prs_data_dao, final_drug_list length: {}".format(len(final_drug_list)))

        query = PRSDrugDetails.select(*select_fields).dicts() \
                                .join(UniqueDrug, on=UniqueDrug.id == PRSDrugDetails.unique_drug_id) \
                                .join(DrugMaster, on=(UniqueDrug.formatted_ndc == DrugMaster.formatted_ndc) & (UniqueDrug.txr == DrugMaster.txr)) \
                                .join(DrugDimension, JOIN_LEFT_OUTER, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
                                .join(CustomDrugShape, JOIN_LEFT_OUTER, on=DrugDimension.shape == CustomDrugShape.id) \
                                .join(CodeMaster, on=CodeMaster.id == PRSDrugDetails.status) \
                                .where((PRSDrugDetails.status != constants.PRS_DRUG_STATUS_PENDING) |
                                       (UniqueDrug.id << final_drug_list)) \
                                .group_by(UniqueDrug.id)

        logger.info(query)
        if drug_list:
            order_list.append(SQL('FIELD(unique_drug_id,{})'.format(str(drug_list)[1:-1])).desc())

        order_list.append(SQL('FIELD(status, {}, {}, {}, {}, {})'.
                            format(constants.PRS_DRUG_STATUS_PENDING,
                                   constants.PRS_DRUG_STATUS_DONE,
                                   constants.PRS_DRUG_STATUS_REJECTED,
                                   constants.PRS_DRUG_STATUS_VERIFIED,
                                   constants.PRS_DRUG_STATUS_REGISTERED)))
        results, count = get_results(query,
                                     fields_dict,
                                     filter_fields=filter_fields,
                                     paginate=paginate,
                                     clauses=clauses,
                                     clauses_having=having_clauses,
                                     like_search_list=like_search_list,
                                     membership_search_list=membership_search_list,
                                     identified_order=order_list,
                                     distinct_non_paginate_results=distinct_non_paginate_results,
                                     sort_fields=sort_fields,
                                     last_order_field=last_order_field)
        for drug in results:
            unique_id_for_drug_details.append(drug['unique_drug_id'])
        drug_details_list = get_drug_details(unique_id_for_drug_details)
        for drug in results:
            for unique_drug in drug_details_list:
                if unique_drug['unique_drug_id'] == drug['unique_drug_id']:
                    drug['last_seen_with'] = unique_drug['last_seen_with']
                    break

        response["prs_data"] = results
        response["total_drugs"] = count
        response["mode"] = mode

        return response

    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("Error while fetching PRSDrugData: " + str(e))
        raise


@log_args_and_response
def db_get_next_unique_drug_id_based_on_status(drug_status: int) -> int:
    """
        Get next unique_drug_id based on status
        @return: unique_drug_id
    """
    try:
        query = PRSDrugDetails.select(PRSDrugDetails.unique_drug_id).dicts() \
            .where(PRSDrugDetails.status == drug_status).get()
        return query["unique_drug_id"]
    except DoesNotExist:
        logger.error("No pending unique_drug_id available in prs_details")
        raise
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error while fetching next pending unique_drug_id: " + str(e))
        raise


@log_args_and_response
def db_get_prs_drug_data(unique_drug_ids):
    """
    This method returns prs drug data
    @param unique_drug_ids:
    @return: drug data
    """
    try:
        query = PRSDrugDetails.select(PRSDrugDetails.unique_drug_id,
                                      PRSDrugDetails.status.alias("drug_status"),
                                      DrugMaster.concated_drug_name_field().alias("drug_name"),
                                      DrugMaster.image_name,
                                      DrugMaster.ndc,
                                      DrugMaster.formatted_ndc,
                                      DrugMaster.txr,
                                      DrugMaster.color,
                                      DrugMaster.imprint,
                                      DrugMaster.shape,
                                      PRSDrugDetails.face1.alias("face_1_selected_images"),
                                      PRSDrugDetails.face2.alias("face_2_selected_images"),
                                      PRSDrugDetails.side_face.alias("side_face_selected_images"),
                                      ).dicts() \
            .join(CodeMaster, on=CodeMaster.id == PRSDrugDetails.status) \
            .join(UniqueDrug, on=UniqueDrug.id == PRSDrugDetails.unique_drug_id) \
            .join(DrugMaster, on=DrugMaster.id == UniqueDrug.drug_id) \
            .where(PRSDrugDetails.unique_drug_id << unique_drug_ids)
        return list(query)

    except DoesNotExist:
        logger.error("No data available in prs_details for unique_drug_id - " + str(unique_drug_ids))
        raise
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error while fetching next pending unique_drug_id: " + str(e))
        raise


@log_args_and_response
def db_get_pvs_drug_crop_images(prs_mode, unique_drug_id, paginate=None):
    """
    This is used to get the crop images available in pvs_slot_details for unique_drug_id.
    @param unique_drug_id:
    @param prs_mode: rts or non_rts
    @param total_images: int
    @param created_from: date
    @param created_to: date
    @return:
    """
    try:
        clauses = [UniqueDrug.id == unique_drug_id,
                   RemoteTechSlot.is_updated == False,
                   RemoteTechSlot.verification_status << [constants.RTS_VERIFIED, constants.RTS_SKIPPED_MAPPED],
                   RemoteTechSlotDetails.mapped_status == constants.SKIPPED_AND_SURE_MAPPED]
        # PVSSlot.created_date.year >= 2022,
        # (PVSSlot.created_date.year >= 2022 | PVSSlot.created_date.month >= 5),
        # (PVSSlot.created_date.year >= 2022 | PVSSlot.created_date.month >= 5 | PVSSlot.created_date.day > 26)]
        # PVSSlot.device_id == 2]  # note: take only images from R1 in prs portal

        # if prs_mode == constants.RTS_MODE:
        #     query = PVSSlotDetails.select(PVSSlotDetails.crop_image_name).dicts() \
        #         .join(RemoteTechSlotDetails, on=PVSSlotDetails.id == RemoteTechSlotDetails.pvs_slot_details_id)
        #     clauses.append(RemoteTechSlotDetails.label_drug_id == unique_drug_id)
        #
        # else:
        # query = PVSSlotDetails.select(PVSSlotDetails.crop_image_name).dicts() \
        #     .join(PVSSlot, on=PVSSlot.id == PVSSlotDetails.pvs_slot_id) \
        #     .join(PVSDrugCount, on=PVSDrugCount.pvs_slot_id == PVSSlot.id)
        # clauses.append(PVSDrugCount.unique_drug_id == unique_drug_id)
        query = PVSSlotDetails.select(fn.DISTINCT(PVSSlotDetails.crop_image_name).alias('crop_image_name'), RemoteTechSlotDetails.id).dicts() \
            .join(RemoteTechSlotDetails, on=RemoteTechSlotDetails.pvs_slot_details_id == PVSSlotDetails.id) \
            .join(UniqueDrug, on=UniqueDrug.id == RemoteTechSlotDetails.label_drug_id) \
            .join(RemoteTechSlot, on=RemoteTechSlot.id == RemoteTechSlotDetails.remote_tech_slot_id) \
            .join(PVSSlot, on=PVSSlot.id == PVSSlotDetails.pvs_slot_id)

        query = query.where(functools.reduce(operator.and_, clauses))
        query = query.order_by(fn.IF(PVSSlotDetails.modified_date.is_null(False), PVSSlotDetails.modified_date,
                                     PVSSlotDetails.created_date).desc())

        total_available_images = query.count()
        result = dict()
        if paginate:
            query = apply_paginate(query, paginate)

        for record in query:
            converted_image = image_convert(str(record["crop_image_name"]))
            result[converted_image] = record['id']
        return total_available_images, result

    except DoesNotExist:
        logger.error("No crop images available in pvs_slot_details for unique_drug_id - " + str(unique_drug_id))
        return 0, []
    except (InternalError, IntegrityError, DataError) as e:
        logger.error("Error : {} : while fetching crop images available in pvs_slot_details for unique_drug_id - {}"
                     .format(str(e), str(unique_drug_id)))
        raise


@log_args_and_response
def db_create_prs_data(drug_dict):
    logger.info("In db_create_prs_data")
    """
    To insert or update PrsDrugDetails table based on pvs_slot_details
    @param pvs_slot_detail_id:int
    @return: int
    """
    try:
        unique_drug_id = drug_dict['unique_drug_id']
        predicted_qty = drug_dict['predicted_qty']
        expected_qty = drug_dict['expected_qty']

        # select records from prsdrugdetails for comparing already existing drug image count with pvsdrugcount quantity
        for record in PRSDrugDetails.select(PRSDrugDetails.unique_drug_id, PRSDrugDetails.predicted_qty,
                                            PRSDrugDetails.expected_qty).dicts():
            if record['unique_drug_id'] == unique_drug_id:
                previous_predicted_qty = record['predicted_qty']
                previous_expected_qty = record['expected_qty']
                # updates if drug already present
                logger.info(f"In db_create_prs_data, update prs data for unique drug: {record['unique_drug_id']}")
                update_prs_data = PRSDrugDetails.update(predicted_qty=previous_predicted_qty + predicted_qty,
                                                        expected_qty=previous_expected_qty + expected_qty) \
                    .where(PRSDrugDetails.unique_drug_id == record['unique_drug_id']).execute()
                logger.info(f"In db_create_prs_data, updated prs data for unique drug: {record['unique_drug_id']}, update_prs_data: {update_prs_data}")
                return update_prs_data
        data_dict = {'unique_drug_id': unique_drug_id, 'status': constants.PRS_DRUG_STATUS_PENDING,
                     'predicted_qty': predicted_qty, 'expected_qty': expected_qty}
        # creates new record if not present
        logger.info(f"In db_create_prs_data, insert_data_in_prs: {data_dict}")
        insert_prs_data = PRSDrugDetails.insert_data_in_prs(data_dict)
        return insert_prs_data

    except(InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in db_create_prs_data {}".format(e))
        raise


def get_count_from_company_setting(company_id: int) -> int:
    """
    To obtain MINIMUM_IMAGE_COUNT_FOR_PRS from company_setting table
    @param company_id: int
    @return: int
    """
    try:
        logger.info("In get_count_from_company_setting")
        query = CompanySetting.db_get_by_company_id(company_id=company_id)
        image_count: int = 0
        for record, value in query.items():
            if record == constants.MINIMUM_IMAGE_COUNT_PRS_COMPANY_SETTING:
                image_count = int(value)
                logger.debug(image_count)
        return image_count
    except(InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("error in get_count_from_company_setting {}".format(e))
        raise


def get_pending_drug_ids_from_prs():
    """
    To obtain pending unique_drug_ids from prs_drug_details table
    @return: list
    """
    try:
        logger.info("In get_pending_drug_ids_from_prs")
        unique_drug_ids_list = PRSDrugDetails.get_pending_drug_ids()
        return unique_drug_ids_list

    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def get_filters_for_prs():
    try:
        shape = set()
        color = set()
        status = set()
        faces = set()

        query = PRSDrugDetails.select((DrugMaster.shape).alias('shape'),
                                     (DrugMaster.color).alias('color'),
                                     (CodeMaster.value).alias('status'),
                                     (fn.IF(PRSDrugDetails.face1.is_null(False),
                                                                        fn.IF(PRSDrugDetails.face2.is_null(False),
                                                                              fn.IF(PRSDrugDetails.side_face.is_null(
                                                                                  False), "All Faces", "Face1,Face2"),
                                                                              "Face1,Face2"), "None")).alias("faces")).dicts() \
            .join(UniqueDrug, on=UniqueDrug.id == PRSDrugDetails.unique_drug_id) \
            .join(DrugMaster,
                  on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) & (DrugMaster.txr == UniqueDrug.txr))) \
            .join(CodeMaster, on=CodeMaster.id == PRSDrugDetails.status)

        for drug in query:
            shape.add(drug['shape'])
            color.add(drug['color'])
            status.add(drug['status'])
            faces.add(drug['faces'])

        return list(shape), list(color), list(status), list(faces)
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def get_prs_images_from_unique_drug_id(unique_drug_id):
    try:
        query = PRSDrugDetails.db_get_prs_images_from_drug_id(unique_drug_id=unique_drug_id)
        return query
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def update_prs_images_for_unique_drug(face_1_list, face_2_list, side_face_list, unique_drug_id):
    try:
        status = PRSDrugDetails.db_update_prs_images_for_unique_drug(face_1_list, face_2_list, side_face_list, unique_drug_id)
        return status
    except (InternalError, IntegrityError, DataError) as e:
        logger.error(e)
        raise


@log_args_and_response
def get_remote_tech_slot_id_from_prs_unique_drug_and_images(unique_drug_id, images):
    try:
        remote_tech_ids = set()
        remote_tech_slot_details_ids = set()
        query = RemoteTechSlotDetails.select(RemoteTechSlot.id.alias('remote_tech_slot_id'),
                                             RemoteTechSlotDetails.id.alias('remote_tech_slot_details_id')).dicts() \
            .join(PVSSlotDetails, on=RemoteTechSlotDetails.pvs_slot_details_id == PVSSlotDetails.id) \
            .join(PRSDrugDetails, on=PRSDrugDetails.unique_drug_id == RemoteTechSlotDetails.label_drug_id) \
            .join(RemoteTechSlot, on=RemoteTechSlotDetails.remote_tech_slot_id == RemoteTechSlot.id) \
            .where(PVSSlotDetails.crop_image_name << images, RemoteTechSlotDetails.label_drug_id == unique_drug_id)

        for record in query:
            remote_tech_ids.add(record['remote_tech_slot_id'])
            remote_tech_slot_details_ids.add(record['remote_tech_slot_details_id'])

        return list(remote_tech_ids), list(remote_tech_slot_details_ids)
    except (InternalError, IntegrityError, DataError, Exception) as e:
        logger.error("Error get_remote_tech_slot_id_from_prs_unique_drug_and_images: " + str(e))
        raise
