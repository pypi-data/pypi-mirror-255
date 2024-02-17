from model.model_init import init_db
from dosepack.base_model.base_model import db
from src.model.model_batch_change_tracker import BatchChangeTracker
from src.model.model_batch_hash import BatchHash
from src.model.model_batch_master import BatchMaster
from src.model.model_canister_transfers import CanisterTransfers
from src.model.model_configuration_master import ConfigurationMaster
from src.model.model_doctor_master import DoctorMaster
from src.model.model_facility_distribution_master import FacilityDistributionMaster
from src.model.model_new_fill_drug import NewFillDrug
from src.model.model_note_master import NoteMaster
from src.model.model_pack_canister_usage import PackCanisterUsage
from src.model.model_pack_header import PackHeader
from src.model.model_pack_rx_link import PackRxLink
from src.model.model_pack_status_tracker import PackStatusTracker
from src.model.model_pack_verification import PackVerification
from src.model.model_patient_master import PatientMaster
from src.model.model_facility_master import FacilityMaster
from src.model.model_pharmacy_master import PharmacyMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_generate_canister import GenerateCanister
from src.model.model_canister_zone_mapping import CanisterZoneMapping
from src.model.model_canister_tracker import CanisterTracker
from src.model.model_canister_history import CanisterHistory
from src.model.model_group_master import GroupMaster
from src.model.model_action_master import ActionMaster
from src.model.model_reason_master import ReasonMaster
from src.model.model_code_master import CodeMaster
from model.model_device_manager import RobotMaster
from model.model_drug import ImportedDrug
from src.model.model_drug_stock_history import DrugStockHistory
from src.model.model_drug_details import DrugDetails
from src.model.model_dosage_type import DosageType
from src.model.model_drug_sync_log import DrugSyncLog
from src.model.model_drug_sync_history import DrugSyncHistory
from src.model.model_imported_drug_image import ImportedDrugImage
from src.model.model_skipped_canister import SkippedCanister
from src.model.model_slot_header import SlotHeader
from src.model.model_slot_transaction import SlotTransaction
from src.model.model_temp_slot_info import TempSlotInfo
from src.model.model_unique_drug import UniqueDrug
from src.model.model_drug_master import DrugMaster
from src.model.model_patient_schedule import PatientSchedule
from src.model.model_facility_schedule import FacilitySchedule
from src.model.model_file_validation_error import FileValidationError
from src.model.model_file_header import FileHeader
from model.model_inventory import DrugLotMaster, DrugBottleMaster, DrugBottleQuantityTracker, DrugBottleTracker
from model.model_misc import CompanySetting, FileDownloadTracker, SystemSetting, \
    OverLoadedPackTiming
from src.model.model_print_queue import PrintQueue
from src.model.model_printers import Printers
from model.model_pack import FillProductivity, FilledPack, PackDetails, PackFillError, \
    PackProcessingOrder, PackFillErrorDetails, ReplenishAnalysis, SlotDetails, \
    SlotFillError, SlotFillErrorDetails
from src.model.model_pack_error import PackError
from src.model.model_pack_user_map import PackUserMap
from src.model.model_partially_filled_pack import PartiallyFilledPack
from src.model.model_alternate_drug_option import AlternateDrugOption
from src.model.model_notification import Notification
from src.model.model_pack_history import PackHistory
from src.model.model_batch_manual_packs import BatchManualPacks
from src.model.model_pack_analysis_details import PackAnalysisDetails
from src.model.model_pack_analysis import PackAnalysis
from model.model_pack import BatchMaster, FillProductivity, FilledPack, NewFillDrug, Notification, \
    PatientRx, PackHeader, PackAnalysis, PackAnalysisDetails, PackError, PackFillError, \
    PackHistory, PackProcessingOrder, PackRxLink, PackStatusTracker, PackFillErrorDetails, PackUserMap, \
    PackVerification, PartiallyFilledPack, CanisterTransfers, AlternateDrugOption, BatchChangeTracker, \
    BatchHash, BatchManualPacks, ReplenishAnalysis, SkipUSPack, SkippedCanister, SlotDetails, \
    SlotHeader, SlotHeaderTransaction, SlotFillError, SlotFillErrorDetails, SlotTransaction, TempSlotInfo
from src.model.model_pack_details import PackDetails

from src.model.model_drug_training import DrugTraining
from src.model.model_pack_grid import PackGrid
from src.model.model_reserved_canister import ReservedCanister
from model.model_template import PatientNote, TakeawayTemplate, TemplateDetails, TemplateMaster, StoreSeparateDrug
from src.model.model_unit_conversion import UnitConversion
from src.model.model_unit_master import UnitMaster
from src.model.model_slot_fill_error_v2 import SlotFillErrorV2
from src.model.model_vision_drug_count import VisionCountPrediction
from src.model.model_vision_drug_prediction import VisionDrugPrediction
from src.model.model_patient_rx import PatientRx
from model.model_volumetric_analysis import BigCanisterStick, CanisterParameters, SmallCanisterStick, CanisterStick, \
    CustomShapeCanisterParameters, SkipStickRecommendation, SmallStickCanisterParameters, DrugCanisterParameters, DrugCanisterStickMapping
from src.model.model_missing_stick_recommendation import MissingStickRecommendation
from src.model.model_drug_shape_fields import DrugShapeFields
from src.model.model_drug_dimension import DrugDimension
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_pack_fill_error_v2 import PackFillErrorV2
from src.model.model_zone_master import ZoneMaster
from src.model.model_container_master import ContainerMaster
from src.model.model_device_layout_details import DeviceLayoutDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_device_type_master import DeviceTypeMaster
from src.model.model_disabled_location_history import DisabledLocationHistory
from src.model.model_location_master import LocationMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_mfd_analysis_details import MfdAnalysisDetails
from src.model.model_mfd_canister_master import MfdCanisterMaster
from src.model.model_mfd_canister_status_history import MfdCanisterStatusHistory
from src.model.model_mfd_canister_transfer_history import MfdCanisterTransferHistory
from src.model.model_prs_drug_details import PRSDrugDetails
from src.model.model_pvs_dimension import PVSDimension
from src.model.model_pvs_drug_count import PVSDrugCount
from src.model.model_pvs_slot import PVSSlot
from src.model.model_pvs_slot_details import PVSSlotDetails
from src.model.model_remote_tech_slot import RemoteTechSlot
from src.model.model_remote_tech_slot_details import RemoteTechSlotDetails
from src.model.model_guided_meta import GuidedMeta
from src.model.model_guided_tracker import GuidedTracker
from dosepack.base_model.base_model import db
from src.model.model_consumable_tracker import ConsumableTracker
from src.model.model_consumable_type_master import ConsumableTypeMaster
from src.model.model_consumable_used import ConsumableUsed
from src.model.model_courier_master import CourierMaster
from src.model.model_group_master import GroupMaster
from src.model.model_code_master import CodeMaster
from src.model.model_error_details import ErrorDetails
from playhouse.migrate import *

from src.model.model_order_details import OrderDetails
from src.model.model_order_document import OrderDocument
from src.model.model_order_status_tracker import OrderStatusTracker
from src.model.model_orders import Orders
from src.model.model_shipment_tracker import ShipmentTracker


def create_table_migration():
    init_db(db, "database_migration")
    db.create_tables([GroupMaster])
    db.create_tables([CodeMaster])
    db.create_tables([ActionMaster])
    db.create_tables([BatchMaster])
    db.create_tables([BigCanisterStick])
    db.create_tables([SmallCanisterStick])
    db.create_tables([CanisterParameters])
    db.create_tables([CanisterStick])
    db.create_tables([DeviceTypeMaster])
    db.create_tables([DeviceMaster])
    db.create_tables([ContainerMaster])
    db.create_tables([LocationMaster])
    db.create_tables([CompanySetting])
    db.create_tables([ConfigurationMaster])
    db.create_tables([ConsumableTypeMaster])
    db.create_tables([ConsumableTracker])
    db.create_tables([ConsumableUsed])
    db.create_tables([CourierMaster])
    db.create_tables([CustomDrugShape])
    db.create_tables([CustomShapeCanisterParameters])
    db.create_tables([DisabledLocationHistory])
    db.create_tables([DoctorMaster])
    db.create_tables([DosageType])
    db.create_tables([DrugMaster])
    db.create_tables([DrugLotMaster])
    db.create_tables([DrugBottleMaster])
    db.create_tables([DrugBottleQuantityTracker])
    db.create_tables([DrugBottleTracker])
    db.create_tables([DrugDetails])
    db.create_tables([DrugShapeFields])
    db.create_tables([DrugStockHistory])
    db.create_tables([DrugSyncHistory])
    db.create_tables([DrugSyncLog])
    db.create_tables([FacilityDistributionMaster])
    db.create_tables([FacilityMaster])
    db.create_tables([FacilitySchedule])
    db.create_tables([FileDownloadTracker])
    db.create_tables([FileHeader])
    db.create_tables([FileValidationError])
    db.create_tables([FillProductivity])
    db.create_tables([GenerateCanister])
    db.create_tables([ImportedDrug])
    db.create_tables([ImportedDrugImage])
    db.create_tables([MfdCanisterMaster])
    db.create_tables([MfdAnalysis])
    db.create_tables([MfdCanisterStatusHistory])
    db.create_tables([MfdCanisterTransferHistory])
    db.create_tables([NewFillDrug])
    db.create_tables([NoteMaster])
    db.create_tables([Notification])
    db.create_tables([Orders])
    db.create_tables([OrderStatusTracker])
    db.create_tables([OrderDetails])
    db.create_tables([OrderDocument])
    db.create_tables([PackGrid])
    db.create_tables([PatientMaster])
    db.create_tables([PatientRx])
    db.create_tables([PackHeader])
    db.create_tables([PackDetails])
    db.create_tables([FilledPack])
    db.create_tables([PackAnalysis])
    db.create_tables([PackError])
    db.create_tables([PackHistory])
    db.create_tables([PackProcessingOrder])
    db.create_tables([PackRxLink])
    db.create_tables([PackStatusTracker])
    db.create_tables([PackFillError])
    db.create_tables([PackUserMap])
    db.create_tables([PackVerification])
    db.create_tables([PartiallyFilledPack])
    db.create_tables([PatientNote])
    db.create_tables([PatientSchedule])
    db.create_tables([PharmacyMaster])
    db.create_tables([PrintQueue])
    db.create_tables([Printers])
    db.create_tables([PVSDimension])
    db.create_tables([ReasonMaster])
    db.create_tables([PackFillErrorDetails])
    db.create_tables([CanisterMaster])
    db.create_tables([CanisterHistory])
    db.create_tables([CanisterTracker])
    db.create_tables([CanisterTransfers])
    db.create_tables([BatchChangeTracker])
    db.create_tables([BatchHash])
    db.create_tables([BatchManualPacks])
    db.create_tables([ReplenishAnalysis])
    db.create_tables([ReservedCanister])
    db.create_tables([RobotMaster])
    db.create_tables([ShipmentTracker])
    db.create_tables([SkippedCanister])
    db.create_tables([SlotHeader])
    db.create_tables([SlotDetails])
    db.create_tables([PackAnalysisDetails])
    db.create_tables([SlotFillError])
    db.create_tables([SlotFillErrorDetails])
    db.create_tables([SlotTransaction])
    db.create_tables([SmallStickCanisterParameters])
    db.create_tables([SystemSetting])
    db.create_tables([TakeawayTemplate])
    db.create_tables([TempSlotInfo])
    db.create_tables([TemplateDetails])
    db.create_tables([TemplateMaster])
    db.create_tables([UniqueDrug])
    db.create_tables([AlternateDrugOption])
    db.create_tables([PackCanisterUsage])
    db.create_tables([DrugCanisterParameters])
    db.create_tables([DrugDimension])
    db.create_tables([SkipStickRecommendation])
    db.create_tables([DrugCanisterStickMapping])
    db.create_tables([ErrorDetails])
    db.create_tables([MfdAnalysisDetails])
    db.create_tables([MissingStickRecommendation])
    db.create_tables([PackFillErrorV2])
    db.create_tables([PRSDrugDetails])
    db.create_tables([PVSSlot])
    db.create_tables([PVSSlotDetails])
    db.create_tables([PVSDrugCount])
    db.create_tables([RemoteTechSlot])
    db.create_tables([RemoteTechSlotDetails])
    db.create_tables([SlotFillErrorV2])
    db.create_tables([StoreSeparateDrug])
    db.create_tables([UnitMaster])
    db.create_tables([UnitConversion])
    db.create_tables([ZoneMaster])
    db.create_tables([DeviceLayoutDetails])
    db.create_tables([VisionDrugPrediction])
    db.create_tables([VisionCountPrediction])
    db.create_tables([CanisterZoneMapping])
    db.create_tables([DrugTraining])
    db.create_tables([OverLoadedPackTiming])
    db.create_tables([GuidedMeta])
    db.create_tables([GuidedTracker])
    print("Tables Created Successfully")


if __name__ == '__main__':
    create_table_migration()
