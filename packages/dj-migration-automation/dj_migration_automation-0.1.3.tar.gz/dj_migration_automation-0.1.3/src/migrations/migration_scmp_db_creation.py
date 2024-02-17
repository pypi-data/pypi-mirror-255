from dosepack.base_model.base_model import db
from model.model_init import init_db

from src.model.model_group_master import GroupMaster
from src.model.model_action_master import ActionMaster
from src.model.model_code_master import CodeMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_device_master import DeviceMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_location_master import LocationMaster
from src.model.model_configuration_master import ConfigurationMaster
from src.model.model_mfd_history_comment import MfdCycleHistoryComment
from src.model.model_pack_grid import PackGrid
from src.model.model_company_setting import CompanySetting
from src.model.model_pack_verification_details import PackVerificationDetails
from src.model.model_session_meta import SessionMeta
from src.model.model_shipment_tracker import ShipmentTracker
from src.model.model_skipped_canister import SkippedCanister
from src.model.model_slot_fill_error_v2 import SlotFillErrorV2
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_small_stick_canister_parameters import SmallStickCanisterParameters
from src.model.model_store_separate_drug import StoreSeparateDrug
from src.model.model_system_setting import SystemSetting
from src.model.model_consumable_type_master import ConsumableTypeMaster
from src.model.model_courier_master import CourierMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_dosage_type import DosageType
from src.model.model_drug_shape_fields import DrugShapeFields
from src.model.model_pharmacy_master import PharmacyMaster
from src.model.model_printers import Printers
from src.model.model_reason_master import ReasonMaster
from src.model.model_takeaway_template import TakeawayTemplate
from src.model.model_temp_mfd_filling import TempMfdFilling
from src.model.model_temp_recommnded_stick_canister import TempRecommendedStickCanisterData
from src.model.model_unit_conversion import UnitConversion
from src.model.model_unit_master import UnitMaster
from src.model.model_vision_drug_count import VisionCountPrediction
from src.model.model_vision_drug_prediction import VisionDrugPrediction
from src.model.model_zone_master import ZoneMaster
from src.model.model_facility_master import FacilityMaster
from src.model.model_doctor_master import DoctorMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_batch_pack_data import BatchPackData
from src.model.model_big_canister_stick import BigCanisterStick
from src.model.model_canister_drum import CanisterDrum
from src.model.model_small_canister_stick import SmallCanisterStick
from src.model.model_canister_stick import CanisterStick
from src.model.model_canister_parameters import CanisterParameters
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_celery_task_meta import CeleryTaskmeta
from src.model.model_local_di_data import LocalDIData
from src.model.model_local_di_po_data import LocalDIPOData
from src.model.model_local_di_transaction import LocalDITransaction
from src.model.model_new_fill_drug import NewFillDrug
from src.model.model_note_master import NoteMaster
from src.model.model_notification import Notification
from src.model.model_overloaded_pack_timings import OverLoadedPackTiming
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_batch_master import BatchMaster
from src.model.model_file_header import FileHeader
from src.model.model_patient_master import PatientMaster
from src.model.model_patient_rx import PatientRx
from src.model.model_temp_slot_info import TempSlotInfo
from src.model.model_template_details import TemplateDetails
from src.model.model_template_master import TemplateMaster
from src.model.model_pack_header import PackHeader
from src.model.model_pack_details import PackDetails
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_slot_header import SlotHeader
from src.model.model_slot_details import SlotDetails
from src.model.model_pack_history import PackHistory
from src.model.model_facility_schedule import FacilitySchedule
from src.model.model_file_validation_error import FileValidationError
from src.model.model_mfd_canister_master import MfdCanisterMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_mfd_canister_status_history import MfdCanisterStatusHistory
from src.model.model_mfd_canister_transfer_history import MfdCanisterTransferHistory
from src.model.model_mfd_cycle_history import MfdCycleHistory
from src.model.model_mfd_status_history_comment import MfdStatusHistoryComment
from src.model.model_adhoc_drug_request import AdhocDrugRequest
from src.model.model_unique_drug import UniqueDrug
from src.model.model_alternate_drug_option import AlternateDrugOption
from src.model.model_batch_change_tracker import BatchChangeTracker
from src.model.model_batch_drug_data import BatchDrugData
from src.model.model_batch_drug_order_data import BatchDrugOrderData
from src.model.model_batch_drug_request_mapping import BatchDrugRequestMapping
from src.model.model_batch_hash import BatchHash
from src.model.model_batch_manual_packs import BatchManualPacks
from src.model.model_canister_master import CanisterMaster
from src.model.model_canister_history import CanisterHistory
from src.model.model_canister_status_history import CanisterStatusHistory
from src.model.model_canister_status_history_comment import CanisterStatusHistoryComment
from src.model.model_canister_testing_status import CanisterTestingStatus
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_canister_tx_meta import CanisterTxMeta
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_canister_transfer_cycle_history import CanisterTransferCycleHistory
from src.model.model_canister_transfer_history_comment import CanisterTransferHistoryComment
from src.model.model_consumable_tracker import ConsumableTracker
from src.model.model_consumable_used import ConsumableUsed
from src.model.model_current_inventory_mapping import CurrentInventoryMapping
from src.model.model_custom_shape_canister_parameters import CustomShapeCanisterParameters
from src.model.model_disabled_location_history import DisabledLocationHistory
from src.model.model_drug_lot_master import DrugLotMaster
from src.model.model_drug_bottle_master import DrugBottleMaster
from src.model.model_drug_bottle_quantity_tracker import DrugBottleQuantityTracker
from src.model.model_drug_bottle_tracker import DrugBottleTracker
from src.model.model_drug_canister_parameters import DrugCanisterParameters
from src.model.model_drug_dimension import DrugDimension
from src.model.model_drug_canister_stick_mapping import DrugCanisterStickMapping
from src.model.model_drug_details import DrugDetails
from src.model.model_drug_status import DrugStatus
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_drug_sync_history import DrugSyncHistory
from src.model.model_drug_sync_log import DrugSyncLog
from src.model.model_drug_tracker import DrugTracker
from src.model.model_drug_training import DrugTraining
from src.model.model_error_details import ErrorDetails
from src.model.model_ext_pack_details import ExtPackDetails
from src.model.model_generate_canister import GenerateCanister
from src.model.model_guided_meta import GuidedMeta
from src.model.model_guided_misplaced_canister import GuidedMisplacedCanister
from src.model.model_guided_tracker import GuidedTracker
from src.model.model_guided_transfer_cycle_history import GuidedTransferCycleHistory
from src.model.model_guided_transfer_history_comment import GuidedTransferHistoryComment
from src.model.model_imported_drug import ImportedDrug
from src.model.model_imported_drug_image import ImportedDrugImage
from src.model.model_missing_drug_pack import MissingDrugPack
from src.model.model_missing_stick_recommendation import MissingStickRecommendation
from src.model.model_orders import Orders
from src.model.model_order_details import OrderDetails
from src.model.model_order_document import OrderDocument
from src.model.model_order_status_tracker import OrderStatusTracker
from src.model.model_pack_analysis import PackAnalysis
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_canister_usage import PackCanisterUsage
from src.model.model_pack_drug_tracker import PackDrugTracker
from src.model.model_pack_error import PackError
from src.model.model_pack_fill_error_v2 import PackFillErrorV2
from src.model.model_pack_status_tracker import PackStatusTracker
from src.model.model_pack_user_map import PackUserMap
from src.model.model_pack_verification import PackVerification
from src.model.model_partially_filled_pack import PartiallyFilledPack
from src.model.model_patient_note import PatientNote
from src.model.model_patient_schedule import PatientSchedule
from src.model.model_pre_order_missing_ndc import PreOrderMissingNdc
from src.model.model_print_queue import PrintQueue
from src.model.model_prs_drug_details import PRSDrugDetails
from src.model.model_pvs_dimension import PVSDimension
from src.model.model_pvs_slot import PVSSlot
from src.model.model_pvs_drug_count import PVSDrugCount
from src.model.model_pvs_slot_details import PVSSlotDetails
from src.model.model_remote_tech_slot import RemoteTechSlot
from src.model.model_remote_tech_slot_details import RemoteTechSlotDetails
from src.model.model_reserved_canister import ReservedCanister
from src.model.model_session_module_master import SessionModuleMaster
from src.model.model_session import Session
from src.model.model_session_module_meta import SessionModuleMeta

tables = [GroupMaster, ActionMaster, CodeMaster, DeviceTypeMaster, DeviceMaster, ContainerMaster, LocationMaster,
          ConfigurationMaster,
          PackGrid, CompanySetting, SystemSetting, ConsumableTypeMaster, CourierMaster, CustomDrugShape, UnitMaster,
          ZoneMaster, DeviceLayoutDetails, DosageType,
          DrugShapeFields, PharmacyMaster, Printers, ReasonMaster, UnitConversion, FacilityMaster, DoctorMaster,
          DrugMaster, BatchPackData, BigCanisterStick, CanisterDrum, SmallCanisterStick, CanisterStick, CanisterMaster,
          CanisterParameters, CanisterZoneMapping,
          CeleryTaskmeta, LocalDIData, LocalDIPOData, LocalDITransaction, NewFillDrug, NoteMaster, Notification,
          OverLoadedPackTiming,
          FacilityDistributionMaster, BatchMaster, FileHeader, PatientMaster, PatientRx, TempSlotInfo, TemplateDetails,
          TemplateMaster,
          PackHeader, PackDetails, PackRxLink, SlotHeader, SlotDetails, PackHistory, FacilitySchedule,
          FileValidationError, MfdCanisterMaster,
          MfdAnalysis, MfdAnalysisDetails, MfdCanisterStatusHistory, MfdCanisterTransferHistory, MfdCycleHistory,
          MfdCycleHistoryComment,
          MfdStatusHistoryComment, AdhocDrugRequest, UniqueDrug, AlternateDrugOption, BatchChangeTracker, BatchDrugData,
          BatchDrugOrderData,
          BatchDrugRequestMapping, BatchHash, BatchManualPacks, CanisterHistory, CanisterStatusHistory,
          CanisterStatusHistoryComment,
          CanisterTestingStatus, CanisterTracker, CanisterTxMeta, CanisterTransfers, CanisterTransferCycleHistory,
          CanisterTransferHistoryComment,
          ConsumableTracker, ConsumableUsed, CurrentInventoryMapping, CustomShapeCanisterParameters,
          DisabledLocationHistory, DrugLotMaster,
          DrugBottleMaster, DrugBottleQuantityTracker, DrugBottleTracker, DrugCanisterParameters, DrugDimension,
          DrugCanisterStickMapping,
          DrugDetails, DrugStatus, DrugStockHistory, DrugSyncHistory, DrugSyncLog, DrugTracker, DrugTraining,
          ErrorDetails, ExtPackDetails,
          GenerateCanister, GuidedMeta, GuidedMisplacedCanister, GuidedTracker, GuidedTransferCycleHistory,
          GuidedTransferHistoryComment,
          ImportedDrug, ImportedDrugImage, MissingDrugPack, MissingStickRecommendation, Orders, OrderDetails,
          OrderDocument, OrderStatusTracker,
          PackAnalysis, PackAnalysisDetails, PackCanisterUsage, PackDrugTracker, PackError, PackFillErrorV2,
          PackStatusTracker, PackUserMap,
          PackVerification, PackVerificationDetails, PartiallyFilledPack, PatientNote, PatientSchedule,
          PreOrderMissingNdc, PrintQueue, PRSDrugDetails, PVSDimension,
          PVSSlot, PVSDrugCount, PVSSlotDetails, RemoteTechSlot, RemoteTechSlotDetails, ReservedCanister,
          SessionModuleMaster, Session,
          SessionModuleMeta, SessionMeta, ShipmentTracker, SkippedCanister, SlotFillErrorV2, SlotTransaction,
          SmallStickCanisterParameters,
          StoreSeparateDrug, TakeawayTemplate, TempMfdFilling, TempRecommendedStickCanisterData, VisionDrugPrediction,
          VisionCountPrediction]


def create_scmp_table():
    init_db(db, 'database_migration')
    with db.transaction():
        for table in tables:
            if not table.table_exists():
                db.create_tables([table])
                print(str(table) + "Created")


def drop_all_scmp_tables():
    init_db(db, 'database_migration')
    for table in tables[::-1]:
        if table.table_exists():
            db.drop_tables([table])
            print(str(table) + "Dropped")


if __name__ == "__main__":
    create_scmp_table()
