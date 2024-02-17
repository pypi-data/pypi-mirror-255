from peewee import *

import settings
import src.constants
from couch_db_implementation import PrintJobStoreDocument
from dosepack.utilities.utils import log_args_and_response, log_args
from realtime_db.dp_realtimedb_interface import Database
from src.dao.couch_db_dao import get_couch_db_database_name
from src.exceptions import RealTimeDBException
from src.model.model_code_master import CodeMaster
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src.model.model_slot_header import SlotHeader
from src.model.model_pvs_slot import PVSSlot
from src.model.model_pack_grid import PackGrid
from src.model.model_pvs_slot_details import PVSSlotDetails
from src.model.model_remote_tech_slot import RemoteTechSlot
from src.model.model_remote_tech_slot_details import RemoteTechSlotDetails

logger = settings.logger

DISPLAY_ERROR_PRIORITY = {src.constants.US_STATION_REJECTED: 40, src.constants.US_STATION_SUCCESS: 10,
                          src.constants.US_STATION_NOT_SURE: 30, src.constants.US_STATION_MISSING_PILLS: 20, }


def get_pvs_data_dao(pack_id):
    """
    Returns Pill Vision Data for user station for given pack_id

    @param pack_id: Pack ID
    :return: dict
    """
    logger.info("In get_pvs_data_dao")
    us_station_list = [src.constants.US_STATION_REJECTED, src.constants.US_STATION_SUCCESS,
                       src.constants.US_STATION_NOT_SURE,
                       src.constants.US_STATION_MISSING_PILLS]
    try:
        DrugMasterAlias = DrugMaster.alias()
        UniqueDrugAlias = UniqueDrug.alias()
        query = SlotHeader.select(
            PackGrid.slot_row,
            PackGrid.slot_column,
            RemoteTechSlot.verification_status,
            PVSSlot.device_id,
            PVSSlot.slot_image_name,
            PVSSlot.us_status,
            PVSSlot.pvs_identified_count,
            PVSSlotDetails.radius,
            PVSSlotDetails.pill_centre_x,
            PVSSlotDetails.pill_centre_y,
            PVSSlotDetails.crop_image_name,
            RemoteTechSlotDetails.label_drug_id.alias('remote_tech_label_drug_id'),
            PVSSlotDetails.id.alias("pvs_sd_id"),
            fn.IF(  # flag to indicate who predicted/identified crop
                #  2 = Remote Tech., 1 = PVS, 0 = No one
                PVSSlotDetails.predicted_label_drug_id.is_null(True),
                fn.IF(
                    RemoteTechSlotDetails.label_drug_id.is_null(True), 0, 1
                ),
                2
            ).alias('predicted_by'),
            DrugMaster,
            PVSSlotDetails.predicted_label_drug_id.alias('pvs_drug_label'),
            PVSSlotDetails.pvs_classification_status,
            DrugMasterAlias.image_name.alias('predicted_image_name'),
            DrugMasterAlias.drug_name.alias('predicted_drug_name'),
            DrugMasterAlias.strength.alias('predicted_strength'),
            DrugMasterAlias.strength_value.alias('predicted_strength_value'),
            DrugMasterAlias.ndc.alias('predicted_ndc'),
            DrugMasterAlias.imprint.alias('predicted_imprint'),
            DrugMasterAlias.color.alias('predicted_color'),
            DrugMasterAlias.shape.alias('predicted_shape'),
            PVSSlot.drop_number,
            PVSSlot.quadrant
        ) \
            .dicts() \
            .join(PackGrid, on=PackGrid.id == SlotHeader.pack_grid_id) \
            .join(PVSSlot, on=SlotHeader.id == PVSSlot.slot_header_id) \
            .join(PVSSlotDetails, JOIN_LEFT_OUTER,
                  on=PVSSlotDetails.pvs_slot_id == PVSSlot.id) \
            .join(RemoteTechSlot, JOIN_LEFT_OUTER,
                  on=RemoteTechSlot.pvs_slot_id == PVSSlot.id) \
            .join(RemoteTechSlotDetails, JOIN_LEFT_OUTER,
                  on=RemoteTechSlot.remote_tech_id == RemoteTechSlotDetails.id) \
            .join(UniqueDrug, JOIN_LEFT_OUTER,
                  on=UniqueDrug.id == RemoteTechSlotDetails.label_drug_id) \
            .join(DrugMaster, JOIN_LEFT_OUTER,
                  on=DrugMaster.id == UniqueDrug.drug_id) \
            .join(UniqueDrugAlias, JOIN_LEFT_OUTER,
                  on=UniqueDrugAlias.id == PVSSlotDetails.predicted_label_drug_id) \
            .join(DrugMasterAlias, JOIN_LEFT_OUTER,
                  on=DrugMasterAlias.id == UniqueDrugAlias.drug_id) \
            .join(CodeMaster, on=CodeMaster.id == PVSSlot.us_status) \
            .where(SlotHeader.pack_id == pack_id, PVSSlot.us_status << us_station_list)
        logger.debug("Done get_pvs_data_dao")
        return query
    except (InternalError, IntegrityError) as e:
        logger.error(e, exc_info=True)
        raise


@log_args
def get_print_job_cdb_data(system_id):
    """
    get print job couchdb document data
    """

    database_name = get_couch_db_database_name(int(system_id))
    if database_name is None:
        raise RealTimeDBException

    cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
    try:
        logger.info("attempting to connect to db")
        cdb.connect()
        logger.info("connection successful")

        settings.PRINTJOB_DOCUMENT_OBJ = PrintJobStoreDocument(cdb, settings.CONST_PRINT_JOB_DOC_ID)
        settings.PRINTJOB_DOCUMENT_OBJ.initialize_doc()

        # store the document retrieved from the database
        settings.PRINTJOB_DOC = settings.PRINTJOB_DOCUMENT_OBJ.get_document()

        # get the existing printqueue
        settings.PRINT_JOB_QUEUE = settings.PRINTJOB_DOC["data"]["print_jobs"]
        return settings.PRINT_JOB_QUEUE
    except Exception as ex:
        logger.error("Error in get_print_job_cdb_data" + str(ex))
        return False, False


@log_args_and_response
def update_print_job_cdb_data_for_cron_job(system_id, updated_list):
    """
        update printjobs couch db document
    """

    database_name = get_couch_db_database_name(int(system_id))
    if database_name is None:
        raise RealTimeDBException

    cdb = Database(settings.CONST_COUCHDB_SERVER_URL, database_name)
    try:
        logger.info("attempting to connect to db")
        cdb.connect()
        logger.info("connection successful")

        settings.PRINTJOB_DOCUMENT_OBJ = PrintJobStoreDocument(cdb, settings.CONST_PRINT_JOB_DOC_ID)
        settings.PRINTJOB_DOCUMENT_OBJ.initialize_doc()

        # store the document retrieved from the database
        settings.PRINTJOB_DOC = settings.PRINTJOB_DOCUMENT_OBJ.get_document()

        settings.PRINTJOB_DOC["data"]["print_jobs"] = updated_list
        # now save the document
        settings.PRINTJOB_DOCUMENT_OBJ.update_document(settings.PRINTJOB_DOC)
        return True
    except Exception as ex:
        logger.error("Error in update_print_job_cdb_data_for_cron_job" + str(ex))
        return False, False
